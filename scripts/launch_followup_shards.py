"""Allocate independent A100 shards once; no sampled-response retry paths."""
import concurrent.futures
import tarfile
from followup_shard_cloud import *
from followup_support import verify_freeze
from revised_dispatch_transport import dispatch_once

TRANSFER=Path('.local/followups/transfer')
def verify():
    verify_freeze()
    for p,h in json.loads((ROOT/'freeze.json').read_text())['files'].items():assert sha(p)==h,p
def prepare(job,archives):
    out=folder(job)
    try:
        for _ in range(180):
            cloud(job,'status');s=state(job)
            if s['status']=='active' and s.get('ip'):break
            time.sleep(5)
        else:raise RuntimeError('GPU boot timeout; no model work dispatched')
        args,host=ssh(job)
        for _ in range(30):
            if subprocess.run(args+[host,'true'],timeout=25,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
            time.sleep(5)
        else:raise RuntimeError('SSH boot timeout; no model work dispatched')
        subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True,timeout=30)
        kind=plan()['jobs'][job]['kind']
        selected=[archives['source'],archives['amendment']]
        if kind=='qwen':selected.append(archives['qwen'])
        else:
            selected.append(archives['prepared'])
            if kind!='prepared':selected.append(archives[kind])
        for path in selected:
            subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600)
            assert remote(job,['sha256sum',path.name]).split()[0]==sha(path)
            remote(job,['tar','-xzf',path.name],timeout=90)
        remote(job,['mkdir','-p',str(out)])
        gpu=remote(job,['nvidia-smi','--query-gpu=name','--format=csv,noheader']).strip()
        assert gpu in ('NVIDIA A100-SXM4-40GB','NVIDIA A100-SXM4-80GB')
        write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True})
        pid=background('scripts/followup_shard_supervisor.py',['--job',job],out/'supervisor.log')
        for _ in range(100):
            if (out/'supervisor-started.json').exists():break
            time.sleep(.1)
        else:raise RuntimeError('Collector did not start')
        ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=['python3','scripts/run_followup_shard_node.py','--job',job])
        write_json(out/'startup-result.json',{'at':now(),'dispatch':ack})
    except BaseException as e:
        write_json(out/'startup-error.json',{'at':now(),'error':str(e)})
        if not (out/'dispatch-intent.json').exists():
            try:cleanup(job)
            except Exception as exc:write_json(out/'cleanup-error.json',{'at':now(),'error':str(exc)})
        raise
def archives():
    original=json.loads((LOG/'cloud/bundle.json').read_text())['archives']
    result={k:TRANSFER/(k+'.tar.gz') for k in original}
    assert all(sha(p)==original[k]['sha256'] for k,p in result.items())
    result['qwen']=TRANSFER/'qwen-prepared-transfer.tar.gz'
    assert sha(result['qwen'])==json.loads((LOG/'parallel/identity-bundle.json').read_text())['qwen']['sha256']
    amendment=TRANSFER/'sharding-amendment.tar.gz'
    with tarfile.open(amendment,'w:gz') as tar:
        for path in [*json.loads((ROOT/'freeze.json').read_text())['files'],str(ROOT/'freeze.json')]:tar.add(path,recursive=False)
    result['amendment']=amendment
    write_json(ROOT/'bundle.json',{k:{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for k,p in result.items()})
    return result
def main():
    verify()
    with (ROOT/'launcher-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    assert all(not statepath(j).exists() for j in plan()['jobs'])
    bundle=archives()
    background('scripts/followup_shard_watchdog.py',[],ROOT/'watchdog.log')
    for _ in range(100):
        if (ROOT/'watchdog-started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Watchdog did not start')
    jobs={};allocation_errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        for job in plan()['jobs']:
            out=folder(job);out.mkdir(parents=True,exist_ok=True)
            if (ROOT/'budget-stop.json').exists():break
            entry=account('instance-types')['gpu_1x_a100_sxm4']
            regions=[r['name'] for r in entry['regions_with_capacity_available']]
            assert entry['instance_type']['price_cents_per_hour']/100<=1.99
            if not regions:
                write_json(out/'allocation-error.json',{'at':now(),'error':'No matching capacity; no launch sent'})
                allocation_errors.append(job);continue
            region=next((r for r in ('us-west-2','us-east-1','us-west-1') if r in regions),regions[0])
            with (out/'launch-intent.json').open('x') as f:json.dump({'at':now(),'region':region},f)
            try:cloud(job,'launch',['--instance-type','gpu_1x_a100_sxm4','--region',region,'--max-hourly-usd','1.99'])
            except Exception as e:
                # Record actual/uncertain state; never issue a second POST here.
                write_json(out/'allocation-error.json',{'at':now(),'error':str(e),'repeat_post':False})
                allocation_errors.append(job);time.sleep(13);continue
            jobs[job]=pool.submit(prepare,job,bundle)
            time.sleep(13)
        write_json(ROOT/'allocation-result.json',{'at':now(),'allocated':list(jobs),'errors':allocation_errors})
        for job,future in jobs.items():
            try:future.result()
            except BaseException as e:write_json(folder(job)/'setup-result.json',{'at':now(),'error':str(e)})
    write_json(ROOT/'startup-finished.json',{'at':now(),'allocated':list(jobs),'errors':allocation_errors})
    # A separate, operator-readable receipt avoids disguising missing shards as
    # complete. Successful collectors remain responsible for their own cleanup.
    while not all((folder(j)/'supervisor-result.json').exists() or (folder(j)/'startup-error.json').exists() for j in jobs):time.sleep(30)
    write_json(ROOT/'collection-finished.json',{'at':now(),'cost':costs(),'allocation_errors':allocation_errors})
    if allocation_errors or any(not (folder(j)/'supervisor-result.json').exists() or json.loads((folder(j)/'supervisor-result.json').read_text())['error'] for j in jobs):
        write_json(ROOT/'attention-required.json',{'at':now(),'reason':'Not every assignment completed; retain all outputs, no sampled retry.'});return
    with (ROOT/'analysis.log').open('x') as f:
        r=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followup_shards.py'],stdout=f,stderr=subprocess.STDOUT)
    write_json(ROOT/'analysis-result.json',{'at':now(),'returncode':r.returncode})
    write_json(ROOT/'finished.json',{'at':now(),'cost':costs(),'analysis_returncode':r.returncode})
if __name__=='__main__':main()
