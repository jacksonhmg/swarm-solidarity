#!/usr/bin/env python3
"""Recover a capacity precheck that provably sent no launch POST."""
from parallel_followup_support import *
from followup_support import verify_freeze
from revised_dispatch_transport import dispatch_once
from accelerate_followups import original_archives
import os

def start(node,archives):
    out=folder(node);out.mkdir(parents=True,exist_ok=True)
    try:
        assert not statepath(node).exists()
        entry=account('instance-types')[plan()['instance_type']]
        regions=[r['name'] for r in entry['regions_with_capacity_available']]
        assert entry['instance_type']['price_cents_per_hour']/100<=plan()['max_hourly_usd']
        assert regions,'No matching A100 capacity; no launch sent'
        region='us-east-1';assert region in regions, 'No East Coast capacity; no POST sent'
        with (out/'launch-intent-actual.json').open('x') as f:json.dump({'at':now(),'region':region},f)
        cloud(node,'launch',['--instance-type',plan()['instance_type'],'--region',region,'--max-hourly-usd',str(plan()['max_hourly_usd'])])
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
        selected=[archives['source']]+([] if node=='qwen' else [archives['prepared']])+([archives[node]] if node.startswith('revised_') else [])
        for path in selected:
            subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600)
            assert remote(node,['sha256sum',path.name]).split()[0]==sha(path)
            remote(node,['tar','-xzf',path.name],timeout=90)
        remote(node,['mkdir','-p',str(out)])
        gpu=remote(node,['nvidia-smi','--query-gpu=name','--format=csv,noheader']).strip()
        assert gpu in plan()['accepted_gpu_names']
        write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True})
        pid=background('scripts/followup_supervisor.py',['--node',node],out/'supervisor.log')
        for _ in range(100):
            if (out/'supervisor-started.json').exists():break
            time.sleep(.1)
        else:raise RuntimeError('Collector not started')
        ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=['python3','scripts/run_followup_node.py','--node',node])
        return {'node':node,'dispatch':ack,'at':now()}
    except BaseException as exc:
        write_json(out/'startup-error.json',{'at':now(),'error':str(exc)})
        # If launch response was uncertain, cleanup reconciles by owner name.
        # Never repeat POST or a dispatched controller.
        if not (out/'dispatch-intent.json').exists():
            try:cleanup(node)
            except Exception as e:write_json(out/'cleanup-error.json',{'at':now(),'error':str(e)})
        raise

if __name__=='__main__':
    verify_freeze();node='revised_s41031'
    assert not statepath(node).exists()
    error=json.loads((folder(node)/'startup-error.json').read_text())['error']
    assert error.strip()=='Requested region currently has no capacity'
    # lambda_cloud checks region before key creation/state/POST. Absent owner
    # state plus this exact error proves this is the first launch, not a retry.
    with (LOG/'parallel/capacity-recovery-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid(),'original_error':error,'prior_launch_POSTs':0,'reason':'Region capacity disappeared between read-only checks.'},f,indent=2)
    print(json.dumps(start(node,original_archives())),flush=True)
