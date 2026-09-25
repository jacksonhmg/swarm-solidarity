#!/usr/bin/env python3
"""Reconcile definitive capacity rejections; never retry an uncertain launch."""
import concurrent.futures
import os
import urllib.request
from parallel_followup_support import *
from accelerate_followups import original_archives
from revised_dispatch_transport import dispatch_once
from lambda_cloud import BASE,NoRedirect
P=LOG/'parallel'

def prepare(node,archives):
    out=folder(node)
    for _ in range(150):
        cloud(node,'status');s=state(node)
        if s['status']=='active' and s.get('ip'):break
        time.sleep(5)
    else:raise RuntimeError('GPU boot timeout')
    args,host=ssh(node)
    for _ in range(30):
        if subprocess.run(args+[host,'true'],timeout=25,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
        time.sleep(5)
    else:raise RuntimeError('SSH boot timeout')
    subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True,timeout=30)
    selected=([archives['source'],archives['amendment'],archives['qwen']] if node=='qwen_identity' else [archives['source'],archives['prepared'],archives[node]])
    for path in selected:
        subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600)
        assert remote(node,['sha256sum',path.name]).split()[0]==sha(path)
        remote(node,['tar','-xzf',path.name],timeout=90)
    remote(node,['mkdir','-p',str(out)])
    gpu=remote(node,['nvidia-smi','--query-gpu=name','--format=csv,noheader']).strip()
    assert gpu in plan()['accepted_gpu_names']
    write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True})
    pid=background('scripts/parallel_followup_supervisor.py' if node=='qwen_identity' else 'scripts/followup_supervisor.py',['--node',node],out/'supervisor.log')
    for _ in range(100):
        if (out/'supervisor-started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Collector not started')
    ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=(['python3','scripts/run_parallel_followup_identity.py'] if node=='qwen_identity' else ['python3','scripts/run_followup_node.py','--node',node]))
    return {'node':node,'dispatch':ack,'at':now()}

def reject_cleanup(node,attempt):
    s=state(node)
    assert not s.get('instance_id'),'An allocated instance is not a rejected launch'
    matches=[r for r in account('instances') if r.get('name')==s['name']]
    assert not matches,'Launch is allocated/uncertain: do not repeat it'
    assert s['status']=='launch_requested'
    # Only an explicit insufficient-capacity response authorizes this cleanup.
    key=next(k for k in account('ssh-keys') if k['id']==s['ssh_key_id'])
    assert key['name']==s['ssh_key_name']==s['name']
    credential=os.environ.get('LAMBDA_API_KEY') or Path(os.environ['LAMBDA_API_KEY_FILE']).read_text().strip()
    request=urllib.request.Request(BASE+'ssh-keys/'+s['ssh_key_id'],method='DELETE',headers={'Authorization':'Bearer '+credential,'User-Agent':'swarm-solidarity/0.1'})
    with (CLOUD/'api.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:assert response.status in (200,204)
        time.sleep(1.1)
    s.update(status='launch_rejected_no_instance',confirmed_no_instance_at=now(),ssh_key_deleted_at=now(),gpu_cost_usd=0)
    private=Path(s['private_key_path']);private.unlink(missing_ok=True);private.with_suffix('.pub').unlink(missing_ok=True)
    archive=Path('.local/followups')/('rejected-'+node+'-'+s['name'])/'state.json';save(archive,s)
    write_json(P/(node+f'-capacity-rejection-{attempt}.json'),{k:s[k] for k in ('name','status','launch_requested_at','confirmed_no_instance_at','ssh_key_deleted_at','gpu_cost_usd')})
    statepath(node).unlink()

def recover(node):
    out=folder(node)
    # A fifth-node failure cannot be handled until its original one-shot
    # launcher has finished reporting an explicit rejection.
    while not (out/'startup-error.json').exists():
        if (out/'dispatch-acknowledgement.json').exists():return {'node':node,'recovery_unnecessary':True}
        if (P/'identity-budget-deferred.json').exists() and node=='qwen_identity':return {'node':node,'not_launched_for_budget':True}
        if (CLOUD/'budget-stop.json').exists():return {'node':node,'budget_stop':True}
        time.sleep(10)
    error=json.loads((out/'startup-error.json').read_text())['error']
    for attempt in range(1,7):
        assert not (out/'dispatch-intent.json').exists(),'Never repeat model dispatch'
        if statepath(node).exists():
            assert 'HTTP 400 (instance-operations/launch/insufficient-capacity)' in error,'Uncertain launch: stop and reconcile, never retry'
            reject_cleanup(node,attempt)
        else:assert 'capacity' in error.lower(),'Unexpected startup failure'
        assert costs()['estimated_usd']<24,'Preserve time/money for active jobs; do not expand rental'
        entry=account('instance-types')[plan()['instance_type']]
        regions=[r['name'] for r in entry['regions_with_capacity_available']]
        if not regions:
            time.sleep(20);continue
        # New request gets a fresh owner identity; prior rejected owner/key and
        # zero-allocation reconciliation are preserved. No retry of uncertainty.
        preferred=('us-west-2','us-east-1','asia-south-1')
        region=next((r for r in preferred if r in regions),regions[0])
        with (out/f'capacity-launch-intent-{attempt}.json').open('x') as f:json.dump({'at':now(),'region':region,'explicit_rejection_recovery':True},f)
        try:
            cloud(node,'launch',['--instance-type',plan()['instance_type'],'--region',region,'--max-hourly-usd','1.99'])
        except Exception as exc:
            error=str(exc);write_json(P/(node+f'-capacity-error-{attempt}.json'),{'at':now(),'error':error})
            if 'capacity' not in error.lower():raise
            time.sleep(20);continue
        archives=original_archives()
        if node=='qwen_identity':
            archives={'source':archives['source'],'amendment':Path('.local/followups/transfer/parallel-amendment.tar.gz'),'qwen':Path('.local/followups/transfer/qwen-prepared-transfer.tar.gz')}
            saved=json.loads((P/'identity-bundle.json').read_text());assert all(sha(p)==saved[k]['sha256'] for k,p in archives.items())
        return prepare(node,archives)
    if statepath(node).exists() and not state(node).get('instance_id') and 'HTTP 400 (instance-operations/launch/insufficient-capacity)' in error:reject_cleanup(node,7)
    raise RuntimeError(node+': bounded capacity attempts exhausted without model work')

def main():
    with (P/'capacity-resolver2-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        jobs={n:pool.submit(recover,n) for n in ('revised_s41031',)}
        for node,job in jobs.items():
            try:result=job.result();write_json(P/(node+'-capacity-resolved.json'),result)
            except BaseException as exc:
                error=str(exc)
                if statepath(node).exists() and state(node).get('instance_id') and not (folder(node)/'dispatch-intent.json').exists():
                    try:cleanup(node)
                    except Exception as cleanup_error:error+='; cleanup: '+str(cleanup_error)
                write_json(P/(node+'-capacity-blocked.json'),{'at':now(),'error':error,'no_model_retry':True})

if __name__=='__main__':main()
