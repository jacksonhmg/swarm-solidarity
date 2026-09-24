#!/usr/bin/env python3
"""One bounded allocation of eight owned A100 SXM4 hosts. No model-work retries."""
import argparse
import concurrent.futures
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from revised_recovery_support import (LOG,PARALLEL,REMOTE,plan,node_spec,node_dir,verify_plan,ssh,cloud,now,sha,write_json,account_api,cost_snapshot)
from revised_dispatch_transport import dispatch_once

TRANSFER=Path('.local/revised-recovery-transfer')

def background(script,node=None):
    out=node_dir(node) if node else PARALLEL;out.mkdir(parents=True,exist_ok=True)
    command=['caffeinate','-ims',sys.executable,script]+(['--node',node] if node else [])
    with (out/(Path(script).stem+'.log')).open('x') as output:
        proc=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    return proc.pid

def bundle():
    verify_plan()
    for previous in ('.local/lambda-revised-host/state.json','.local/lambda-revised-h100-prepared/state.json'):
        old=json.loads(Path(previous).read_text());assert old['status']=='terminated' and old['ssh_key_deleted_at']
    assert not Path('.local/lambda-revised-retry/state.json').exists()
    assert not (LOG/'infrastructure_retry/launch-intent.json').exists()
    assert not (LOG/'execution').exists()
    assert all(not Path(s['state']).exists() for n,s in plan()['nodes'].items() if n!=plan()['retained_node'])
    retained=json.loads(Path(node_spec(plan()['retained_node'])['state']).read_text())
    assert retained['status']=='active' and not retained.get('termination_requested_at')
    assert not (LOG/'separate_a100/all-ready.json').exists()
    assert not list((LOG/'separate_a100').glob('*/dispatch-intent.json'))
    assert not any(Path(s['state']).exists() for s in json.loads((LOG/'parallel_plan.json').read_text())['nodes'].values())
    for f in ('freeze.json','host_freeze.json','h100_freeze.json','separate_a100/freeze.json','hardware_recovery/freeze.json'):
        assert not subprocess.check_output(['git','status','--porcelain','--',str(LOG/f)],text=True),'Commit before launch'
    snapshot=cost_snapshot()
    # Full remaining eight-node work at measured throughput plus 20% contingency.
    bound=snapshot['estimated_total_usd']+plan()['projected_new_run_usd']*1.2
    write_json(PARALLEL/'feasibility.json',{'at':now(),'current_cumulative_usd':snapshot['estimated_total_usd'],'projected_upper_cumulative_usd':bound,'cap_usd':65})
    assert bound<62,'Fixed full experiment does not fit remaining budget'
    revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    Path('.code-revision').write_text(revision+'\n')
    files=[p for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p]+[b'.code-revision']
    files += [str(p).encode() for p in Path('.local/preparation/terminal-adapter').rglob('*') if p.is_file()]
    TRANSFER.mkdir(parents=True,exist_ok=True)
    listing=TRANSFER/'source.list';listing.write_bytes(b'\0'.join(files)+b'\0')
    archive=TRANSFER/'source.tar.gz'
    subprocess.run(['tar','-czf',str(archive),'--null','-T',str(listing)],check=True)
    archives={'source':archive}
    for node in plan()['nodes']:
        if node.startswith(('ordinary_','corrective_')):
            adapter=Path('.local/corrective')/node/'terminal-adapter'
            meta=json.loads(Path(f'experiment_log/010_corrective_comparison/execution/training/{node}/metadata.json').read_text())
            assert all(sha(adapter/name)==h for name,h in meta['terminal_adapter_files'].items())
            target=TRANSFER/(node+'.tar.gz')
            subprocess.run(['tar','-czf',str(target),str(adapter)],check=True);archives[node]=target
    write_json(PARALLEL/'bundle.json',{'created_at':now(),'code_revision':revision,'files':len(files),
        'archives':{k:{'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in archives.items()}})
    return archives

def capacity():
    p=plan();e=account_api('instance-types')[p['instance_type']]
    price=e['instance_type']['price_cents_per_hour']/100
    regions=[r['name'] for r in e['regions_with_capacity_available']]
    write_json(PARALLEL/'capacity-latest.json',{'at':now(),'instance_type':p['instance_type'],'usd_per_hour':price,'regions':regions})
    if price>p['max_hourly_usd'] or not regions:return None
    return next((r for r in ('us-west-2','us-east-1') if r in regions),regions[0])

def prepare_node(node,archives):
    path=Path(node_spec(node)['state'])
    for _ in range(150):
        cloud(node,'status').check_returncode();s=json.loads(path.read_text())
        if s['status']=='active' and s.get('ip'):break
        time.sleep(5)
    else:raise RuntimeError(node+' boot deadline exceeded')
    args,host=ssh(node)
    for _ in range(24):
        if subprocess.run(args+[host,'true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=25).returncode==0:break
        time.sleep(5)
    else:raise RuntimeError(node+' SSH deadline exceeded')
    subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True)
    selected=[archives['source']]+([archives[node]] if node in archives else [])
    for archive in selected:
        subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(archive),host+':'+REMOTE+'/'+archive.name],check=True,timeout=600)
        uploaded=subprocess.check_output(args+[host,'sha256sum '+shlex.quote(REMOTE+'/'+archive.name)],text=True,timeout=30).split()[0]
        assert uploaded==sha(archive),'Uploaded archive hash mismatch'
        subprocess.run(args+[host,'cd '+shlex.quote(REMOTE)+' && tar -xzf '+shlex.quote(archive.name)+' && rm '+shlex.quote(archive.name)],check=True,timeout=90)
    gpu=subprocess.check_output(args+[host,'nvidia-smi --query-gpu=name --format=csv,noheader'],text=True,timeout=30).strip()
    assert gpu in plan()['accepted_gpu_names'],gpu
    subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE+'/'+str(node_dir(node)))],check=True,timeout=30)
    write_json(node_dir(node)/'ready.json',{'at':now(),'instance_id':s['instance_id'],'node':node,'gpu':gpu,'no_model_work_started':True})

def dispatch(node):
    args,host=ssh(node)
    pid=background('scripts/revised_recovery_supervisor.py',node)
    for _ in range(100):
        ready=node_dir(node)/'supervisor-started.json'
        if ready.exists():
            actual_pid=json.loads(ready.read_text())['pid'];os.kill(actual_pid,0);break
        time.sleep(.1)
    else:raise RuntimeError(node+' collector did not acknowledge local startup')
    receipt=dispatch_once(args,host,REMOTE,node_dir(node),lambda:actual_pid,
        controller_command=['python3','scripts/run_revised_recovery_node.py','--node',node])
    write_json(node_dir(node)/'dispatch.json',{'at':now(),'node':node,**receipt})

def allocate(region,archives):
    with (PARALLEL/'allocation-intent.json').open('x') as f:
        json.dump({'at':now(),'nodes':list(plan()['nodes'])},f)
    # The independent watchdog exists before the first launch request.
    watchdog=background('scripts/revised_recovery_watchdog.py')
    write_json(PARALLEL/'allocation-started.json',{'at':now(),'region':region,'watchdog_pid':watchdog,'nodes':list(plan()['nodes'])})
    dispatch_phase=False
    try:
        deadline=time.monotonic()+plan()['maximum_allocation_minutes']*60
        for node,spec in plan()['nodes'].items():
            if node==plan()['retained_node']:
                node_dir(node).mkdir(parents=True,exist_ok=True)
                write_json(node_dir(node)/'retained.json',{'at':now(),'state':spec['state'],'no_new_rental':True});continue
            node_dir(node).mkdir(parents=True,exist_ok=True)
            while not region:
                if time.monotonic()>=deadline:raise RuntimeError('Capacity disappeared before all eight allocations; no model work dispatched')
                time.sleep(5);region=capacity()
            with (node_dir(node)/'launch-intent.json').open('x') as f:json.dump({'at':now(),'region':region},f)
            with (LOG/'separate_a100/api.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                subprocess.run([sys.executable,'scripts/lambda_cloud.py','launch','--state',spec['state'],
                    '--instance-type',plan()['instance_type'],'--region',region,'--max-hourly-usd',str(plan()['max_hourly_usd'])],check=True)
                time.sleep(1.1)
            time.sleep(plan()['launch_spacing_seconds'])
            region=capacity()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for result in pool.map(lambda n:prepare_node(n,archives),plan()['nodes']):pass
        verify_plan()
        write_json(PARALLEL/'all-ready.json',{'at':now(),'nodes':list(plan()['nodes']),'no_model_work_started':True})
        dispatch_phase=True
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for result in pool.map(dispatch,plan()['nodes']):pass
        write_json(PARALLEL/'allocation-result.json',{'at':now(),'status':'eight_disjoint_assignments_dispatched'})
    except BaseException as exc:
        if dispatch_phase:
            # An uncertain acknowledgement never justifies destroying potentially running work.
            write_json(PARALLEL/'dispatch-uncertainty.json',{'at':now(),'reason':str(exc),'decision':'Reconcile receipts. Keep collection and cumulative watchdog active; never repeat model work.'})
            raise
        write_json(PARALLEL/'abort.json',{'at':now(),'reason':type(exc).__name__+': '+str(exc)})
        from revised_recovery_supervisor import cleanup,record_lifecycle
        failures=[]
        for node,spec in plan()['nodes'].items():
            if not Path(spec['state']).exists():continue
            try:
                cloud(node,'status').check_returncode()  # Reconcile uncertain launch by owner name, never repeat POST.
                cleanup(node)
            except Exception as error:failures.append({'node':node,'error':str(error)})
        write_json(PARALLEL/'allocation-result.json',{'at':now(),'status':'failed_stop','cleanup_failures':failures})
        record_lifecycle()
        raise

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');args=parser.parse_args()
    PARALLEL.mkdir(parents=True,exist_ok=True);TRANSFER.mkdir(parents=True,exist_ok=True)
    with (TRANSFER/'launcher.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not (PARALLEL/'allocation-intent.json').exists(),'Never repeat this allocation attempt'
        # Wait for irreversible old terminations to clear account quota. Never re-rent a live assignment.
        while any(json.loads(Path(p).read_text())['status']!='terminated' for p in plan()['retired_state_paths']):
            if cost_snapshot()['estimated_total_usd']+plan()['projected_new_run_usd']*1.2>=62:
                raise RuntimeError('Full fixed study no longer fits the remaining budget')
            time.sleep(5)
        archives=bundle();errors=0
        while True:
            verify_plan()
            try:region=capacity();errors=0
            except Exception as exc:
                errors+=1
                if errors>=3:
                    write_json(PARALLEL/'capacity-error.json',{'at':now(),'error':str(exc)});raise
                time.sleep(20);continue
            if region:allocate(region,archives);return
            if not args.wait:return
            time.sleep(5)

if __name__=='__main__':main()
