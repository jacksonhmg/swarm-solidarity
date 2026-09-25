"""Fill never-launched shards as capacity appears; no model-work retries."""
import concurrent.futures
import signal
import urllib.request
from followup_shard_cloud import *
from lambda_cloud import BASE, NoRedirect
from launch_followup_shards import prepare, verify

def reject(job,attempt,error):
    assert 'HTTP 400 (instance-operations/launch/insufficient-capacity)' in error
    s=state(job);assert not s.get('instance_id') and s['status']=='launch_requested'
    assert not [i for i in account('instances') if i.get('name')==s['name']]
    keys=[k for k in account('ssh-keys') if k['id']==s['ssh_key_id']]
    assert len(keys)==1 and keys[0]['name']==s['name']==s['ssh_key_name']
    credential=os.environ.get('LAMBDA_API_KEY') or Path(os.environ['LAMBDA_API_KEY_FILE']).read_text().strip()
    request=urllib.request.Request(BASE+'ssh-keys/'+s['ssh_key_id'],method='DELETE',headers={'Authorization':'Bearer '+credential,'User-Agent':'swarm-solidarity/0.1'})
    def delete():
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as r:assert r.status in (200,204)
    locked(delete)
    s.update(status='launch_rejected_no_instance',confirmed_no_instance_at=now(),ssh_key_deleted_at=now(),gpu_cost_usd=0)
    private=Path(s['private_key_path']);private.unlink(missing_ok=True);private.with_suffix('.pub').unlink(missing_ok=True)
    archive=statepath(job).parent/('rejected-'+s['name']+'.json');save(archive,s)
    write_json(folder(job)/(f'rejected-attempt-{attempt}.json'),{k:s[k] for k in ('name','status','launch_requested_at','confirmed_no_instance_at','ssh_key_deleted_at','gpu_cost_usd')})
    statepath(job).unlink()

def main():
    verify()
    with (ROOT/'allocation-completer-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    bundle={k:Path(v['path']) for k,v in json.loads((ROOT/'bundle.json').read_text()).items()}
    assert all(sha(p)==json.loads((ROOT/'bundle.json').read_text())[k]['sha256'] for k,p in bundle.items())
    original=set(json.loads((ROOT/'allocation-result.json').read_text())['allocated'])
    pending=[j for j in plan()['jobs'] if j not in original]
    assert all(not statepath(j).exists() and not (folder(j)/'dispatch-intent.json').exists() for j in pending)
    jobs={};attempts={j:0 for j in pending};started=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        while pending:
            assert costs()['estimated_usd']<55 and not (ROOT/'budget-stop.json').exists()
            if time.monotonic()-started>1200:raise RuntimeError('20-minute capacity acquisition window exceeded; no model retries')
            entry=account('instance-types')['gpu_1x_a100_sxm4']
            regions=[r['name'] for r in entry['regions_with_capacity_available']]
            if not regions:time.sleep(5);continue
            job=pending[0];attempts[job]+=1;attempt=attempts[job]
            assert attempt<=8,'Bounded fresh-owner capacity attempts exhausted'
            region=next((r for r in ('us-west-2','us-east-1','us-west-1') if r in regions),regions[0])
            with (folder(job)/(f'capacity-intent-{attempt}.json')).open('x') as f:json.dump({'at':now(),'region':region,'zero_previous_model_work':True},f)
            try:cloud(job,'launch',['--instance-type','gpu_1x_a100_sxm4','--region',region,'--max-hourly-usd','1.99'])
            except Exception as e:
                error=str(e);write_json(folder(job)/(f'capacity-error-{attempt}.json'),{'at':now(),'error':error})
                if statepath(job).exists():reject(job,attempt,error)
                else:assert 'capacity' in error.lower()
                time.sleep(13);continue
            pending.pop(0);jobs[job]=pool.submit(prepare,job,bundle)
            write_json(ROOT/'capacity-progress.json',{'at':now(),'original':sorted(original),'newly_allocated':list(jobs),'pending':pending})
            time.sleep(13)
        for job,future in jobs.items():
            try:future.result()
            except BaseException as e:write_json(folder(job)/'capacity-setup-error.json',{'at':now(),'error':str(e)})
    write_json(ROOT/'all-allocation-finished.json',{'at':now(),'assigned_jobs':list(plan()['jobs'])})
    # Original launcher only owns its first allocation and would otherwise emit
    # a partial-study completion. Retire it once its setup has fully returned.
    first=next(iter(original))
    while not (folder(first)/'startup-result.json').exists() and not (folder(first)/'startup-error.json').exists():time.sleep(5)
    pid=json.loads((ROOT/'launcher-process.json').read_text())['pid']
    check=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    if check.returncode==0:
        assert 'launch_followup_shards.py' in check.stdout
        os.kill(pid,signal.SIGTERM)
    write_json(ROOT/'initial-launcher-retired.json',{'at':now(),'pid':pid,'reason':'All allocations handed to per-job collectors; no remote work stopped.'})
    while True:
        if any((folder(j)/'startup-error.json').exists() for j in plan()['jobs']):
            write_json(ROOT/'attention-required.json',{'at':now(),'reason':'A shard startup failed; do not repeat sampled work.'});return
        if all((folder(j)/'supervisor-result.json').exists() for j in plan()['jobs']):break
        time.sleep(20)
    assert all(json.loads((folder(j)/'supervisor-result.json').read_text())['error'] is None for j in plan()['jobs'])
    assert all(state(j)['status']=='terminated' and state(j).get('ssh_key_deleted_at') for j in plan()['jobs'])
    with (ROOT/'analysis.log').open('x') as f:
        result=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followup_shards.py'],stdout=f,stderr=subprocess.STDOUT)
    write_json(ROOT/'analysis-result.json',{'at':now(),'returncode':result.returncode})
    write_json(ROOT/'finished.json',{'at':now(),'cost':costs(),'analysis_returncode':result.returncode})
if __name__=='__main__':
    try:main()
    except BaseException as e:
        write_json(ROOT/'allocation-completer-error.json',{'at':now(),'error':str(e),'model_retries':False})
        raise
