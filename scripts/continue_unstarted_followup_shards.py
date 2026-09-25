"""Continue only allocations absent after the prior coordinator has exited."""
import concurrent.futures
import recover_followup_shard_setup as recovery
from followup_shard_cloud import *

NEXT=ROOT/'capacity_continuation'
def main():
    for p,h in json.loads((NEXT/'freeze.json').read_text())['files'].items():assert sha(p)==h,p
    recovery.verify();recovery.install()
    with (NEXT/'started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    oldpid=json.loads((ROOT/'capacity-completer-process.json').read_text())['pid']
    while True:
        error=ROOT/'allocation-completer-error.json'
        if error.exists():
            message=json.loads(error.read_text())['error']
            assert 'capacity acquisition window exceeded' in message or 'Bounded fresh-owner capacity attempts exhausted' in message,message
            r=subprocess.run(['ps','-p',str(oldpid),'-o','command='],capture_output=True,text=True)
            if r.returncode!=0:break
        if (ROOT/'all-allocation-finished.json').exists():
            write_json(NEXT/'unnecessary.json',{'at':now(),'reason':'Original allocation completed'});return
        assert not (ROOT/'budget-stop.json').exists()
        time.sleep(5)
    pending=[]
    for job in recovery.plan()['jobs']:
        if job=='prepared_agent_a-00':continue # exclusively owned by setup recovery8332
        if statepath(job).exists():
            assert state(job).get('instance_id'),'Uncertain owner state; do not retry'
            continue
        assert not (folder(job)/'dispatch-intent.json').exists()
        assert not (ROOT/'execution'/job).exists()
        pending.append(job)
    write_json(NEXT/'assignments.json',{'at':now(),'prior_coordinator_exited':oldpid,'never_launched_jobs':pending,'repeat_model_work':False})
    bundle={k:Path(v['path']) for k,v in json.loads((ROOT/'bundle.json').read_text()).items()}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        jobs={}
        for job in pending:
            assert costs()['estimated_usd']<55
            jobs[job]=pool.submit(recovery.acquire,job,bundle);time.sleep(13)
        for job,future in jobs.items():
            try:
                future.result();write_json(NEXT/(job+'-dispatched.json'),{'at':now(),'job':job})
            except BaseException as e:write_json(NEXT/(job+'-error.json'),{'at':now(),'job':job,'error':str(e),'repeat_model_work':False})
    write_json(NEXT/'finished.json',{'at':now(),'jobs':pending})
if __name__=='__main__':
    try:main()
    except BaseException as e:
        write_json(NEXT/'error.json',{'at':now(),'error':str(e)});raise
