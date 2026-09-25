"""Recover definitively unstarted setup only; preserve all sampled work."""
import argparse
import concurrent.futures
import signal
import shutil
import followup_shard_cloud as base
from followup_shard_cloud import *
from revised_dispatch_transport import dispatch_once

REC=ROOT/'setup_recovery'
def overlay():return json.loads((REC/'execution_state_plan.json').read_text())
def install():
    base.plan=overlay
    globals()['plan']=overlay
def verify():
    for p,h in json.loads((REC/'freeze.json').read_text())['files'].items():assert sha(p)==h,p
    from launch_followup_shards import verify as scientific
    scientific()
def retry_io(fn):
    for attempt in range(3):
        try:return fn()
        except (OSError,subprocess.SubprocessError):
            if attempt==2:raise
            time.sleep(4)
def prepare(job,bundle):
    out=folder(job)
    try:
        for _ in range(180):
            cloud(job,'status');s=state(job)
            if s['status']=='active' and s.get('ip'):break
            time.sleep(5)
        else:raise RuntimeError('GPU boot timeout before dispatch')
        args,host=ssh(job)
        for _ in range(30):
            if subprocess.run(args+[host,'true'],timeout=25,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
            time.sleep(5)
        else:raise RuntimeError('SSH boot timeout before dispatch')
        retry_io(lambda:subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True,timeout=30))
        kind=plan()['jobs'][job]['kind'];selected=[bundle['source'],bundle['amendment']]
        if kind=='qwen':selected.append(bundle['qwen'])
        else:
            selected.append(bundle['prepared'])
            if kind!='prepared':selected.append(bundle[kind])
        for path in selected:
            retry_io(lambda:subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600))
            assert retry_io(lambda:remote(job,['sha256sum',path.name])).split()[0]==sha(path)
            retry_io(lambda:remote(job,['tar','-xzf',path.name],timeout=90))
        retry_io(lambda:remote(job,['mkdir','-p',str(out)]))
        gpu=retry_io(lambda:remote(job,['nvidia-smi','--query-gpu=name','--format=csv,noheader'])).strip()
        assert gpu in ('NVIDIA A100-SXM4-40GB','NVIDIA A100-SXM4-80GB')
        write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True,'setup_recovery':True})
        pid=background('scripts/recover_followup_shard_setup.py',['--supervisor','--job',job],out/'supervisor.log')
        for _ in range(100):
            if (out/'supervisor-started.json').exists():break
            time.sleep(.1)
        else:raise RuntimeError('Collector did not start')
        # Dispatch itself is NEVER in the transport retry helper.
        ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=['python3','scripts/run_followup_shard_node.py','--job',job])
        write_json(out/'startup-result.json',{'at':now(),'dispatch':ack,'setup_recovery':True})
    except BaseException as e:
        write_json(out/'startup-error.json',{'at':now(),'error':str(e)})
        if not (out/'dispatch-intent.json').exists():
            try:cleanup(job)
            except Exception as exc:write_json(out/'cleanup-error.json',{'at':now(),'error':str(exc)})
        raise
def acquire(job,bundle):
    from complete_followup_shard_allocation import reject
    # The imported reject function uses base.statepath, which sees this overlay.
    out=folder(job);out.mkdir(parents=True,exist_ok=True)
    assert not statepath(job).exists() and not (out/'dispatch-intent.json').exists()
    deadline=time.monotonic()+1200
    for attempt in range(1,9):
        while True:
            assert costs()['estimated_usd']<55 and time.monotonic()<deadline
            entry=account('instance-types')['gpu_1x_a100_sxm4'];regions=[r['name'] for r in entry['regions_with_capacity_available']]
            if regions:break
            time.sleep(5)
        region=next((r for r in ('us-west-2','us-east-1','us-west-1') if r in regions),regions[0])
        with (out/f'recovery-intent-{attempt}.json').open('x') as f:json.dump({'at':now(),'region':region,'previous_model_work':False},f)
        try:cloud(job,'launch',['--instance-type','gpu_1x_a100_sxm4','--region',region,'--max-hourly-usd','1.99'])
        except Exception as e:
            error=str(e);write_json(out/f'recovery-capacity-error-{attempt}.json',{'at':now(),'error':error})
            if statepath(job).exists():reject(job,attempt,error)
            else:assert 'capacity' in error.lower()
            time.sleep(13);continue
        return prepare(job,bundle)
    raise RuntimeError('Bounded pre-dispatch capacity attempts exhausted')
def watchdog():
    write_json(REC/'watchdog-started.json',{'at':now(),'pid':os.getpid()})
    while not (ROOT/'finished.json').exists():
        snapshot=costs();write_json(ROOT/'budget-status.json',snapshot)
        if snapshot['estimated_usd']>=62:
            write_json(ROOT/'budget-stop.json',snapshot)
            for job in plan()['jobs']:
                if statepath(job).exists() and state(job).get('status')!='terminated':
                    try:cloud(job,'terminate')
                    except Exception as e:print(str(e),flush=True)
        time.sleep(15)
def retire(pid,script):
    r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    if r.returncode==0:
        assert script in r.stdout
        os.kill(pid,signal.SIGTERM)
    return {'pid':pid,'command':r.stdout.strip(),'at':now()}
def finish_all():
    with (REC/'finisher-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    # Every allocation/setup worker has returned before administrative retirement.
    while not all((folder(j)/'startup-result.json').exists() for j in plan()['jobs']):
        if (ROOT/'budget-stop.json').exists():raise RuntimeError('Budget stop before all assignments dispatched')
        time.sleep(10)
    retired=[]
    for file,script in [('launcher-process.json','launch_followup_shards.py'),('capacity-completer-process.json','complete_followup_shard_allocation.py')]:
        pid=json.loads((ROOT/file).read_text())['pid'];retired.append(retire(pid,script))
    write_json(REC/'startup-coordinators-retired.json',{'at':now(),'processes':retired,'remote_model_work_unchanged':True})
    while not all((folder(j)/'supervisor-result.json').exists() for j in plan()['jobs']):time.sleep(20)
    assert all(json.loads((folder(j)/'supervisor-result.json').read_text())['error'] is None for j in plan()['jobs'])
    assert all(state(j)['status']=='terminated' and state(j).get('ssh_key_deleted_at') for j in plan()['jobs'])
    with (ROOT/'analysis-claim.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    with (ROOT/'analysis.log').open('x') as f:
        r=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followup_shards.py'],stdout=f,stderr=subprocess.STDOUT)
    write_json(ROOT/'analysis-result.json',{'at':now(),'returncode':r.returncode})
    write_json(ROOT/'finished.json',{'at':now(),'cost':costs(),'analysis_returncode':r.returncode})
def main():
    p=argparse.ArgumentParser();p.add_argument('--supervisor',action='store_true');p.add_argument('--watchdog',action='store_true');p.add_argument('--finish',action='store_true');p.add_argument('--job',default='prepared_agent_a-00');a=p.parse_args()
    verify();install()
    if a.supervisor:
        import followup_shard_supervisor as supervisor
        sys.argv=[sys.argv[0],'--job',a.job];supervisor.main();return
    if a.watchdog:watchdog();return
    if a.finish:finish_all();return
    with (REC/'recovery-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid(),'job':a.job},f)
    old=state(a.job);out=folder(a.job)
    assert old['status']=='terminated' and old.get('ssh_key_deleted_at')
    assert (out/'cleanup.json').exists() and not (out/'dispatch-intent.json').exists()
    assert not (ROOT/'execution'/a.job).exists()
    archive=Path(plan()['prior_states']['failed_setup_'+a.job]);archive.parent.mkdir(parents=True,exist_ok=True)
    assert not archive.exists();save(archive,old)
    dest=REC/'archived_nodes'/a.job;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists()
    shutil.move(str(out),str(dest));statepath(a.job).unlink();out.mkdir(parents=True)
    background('scripts/recover_followup_shard_setup.py',['--watchdog'],REC/'watchdog.log')
    for _ in range(100):
        if (REC/'watchdog-started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Expanded watchdog did not start')
    pid=json.loads((ROOT/'watchdog-started.json').read_text())['pid']
    write_json(REC/'old-watchdog-retired.json',retire(pid,'followup_shard_watchdog.py'))
    background('scripts/recover_followup_shard_setup.py',['--finish'],REC/'finisher.log')
    bundle={k:Path(v['path']) for k,v in json.loads((ROOT/'bundle.json').read_text()).items()}
    acquire(a.job,bundle)
    write_json(REC/'recovery-dispatched.json',{'at':now(),'job':a.job})
if __name__=='__main__':
    try:main()
    except BaseException as e:
        write_json(REC/('error-'+str(os.getpid())+'.json'),{'at':now(),'error':str(e)})
        raise
