#!/usr/bin/env python3
"""Collect one assigned shard, verify its hashes, and terminate its owned GPU."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from revised_recovery_support import (LOG,PARALLEL,plan,node_spec,node_dir,remote,pull,cloud,now,sha,write_json,cost_snapshot)


def collect(node):
    out=node_dir(node)
    (LOG/'execution').mkdir(parents=True,exist_ok=True)
    pull(node,str(out)+'/',out)
    condition=node_spec(node)['conditions'][0]
    program="from pathlib import Path; import json; p=Path('experiment_log/011_benign_audit_confirmation/execution'); c="+repr(condition)+"; print(json.dumps({'stage':(p/c).exists(),'training':(p/'training'/c).exists(),'merge':(p/'merges'/(c+'.json')).exists()}))"
    present=json.loads(remote(node,['python3','-c',program]))
    if present['stage']:pull(node,str(LOG/'execution'/condition)+'/',LOG/'execution'/condition)
    if present['merge']:
        pull(node,str(LOG/'execution/merges')+'/',LOG/'execution/merges',options=['--include='+condition+'.json','--exclude=*'])
    if present['training']:
        destination=LOG/'execution/training'/condition
        pull(node,str(destination)+'/',destination)
        meta=destination/'metadata.json'
        if meta.exists() and json.loads(meta.read_text()).get('status')=='complete':
            adapter=Path('.local/revised_corrective')/condition/'terminal-adapter'
            pull(node,str(adapter)+'/',adapter)
            hashes=json.loads(meta.read_text())['terminal_adapter_files']
            assert all(sha(adapter/name)==h for name,h in hashes.items())
    receipt=out/'prepared-merge.json'
    if node=='prepared' and receipt.exists():
        write_json(LOG/'execution/merge.json',json.loads(receipt.read_text()))


def finalize_hashes(node):
    program="""from pathlib import Path
import json,hashlib
p=Path('experiment_log/011_benign_audit_confirmation'); node=NODE; condition=CONDITION
out=p/'hardware_recovery'/node
files=[x for x in out.rglob('*') if x.is_file() and x.name not in ('remote-artifact-hashes.json','remote-console.log')]
for folder in (p/'execution'/condition,p/'execution/training'/condition):
 if folder.exists():files.extend(x for x in folder.rglob('*') if x.is_file())
merge=p/'execution/merges'/(condition+'.json')
if merge.exists():files.append(merge)
(out/'remote-artifact-hashes.json').write_text(json.dumps({str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(files)},indent=2)+'\\n')
""".replace('NODE',repr(node)).replace('CONDITION',repr(node_spec(node)['conditions'][0]))
    remote(node,['python3','-c',program]);collect(node)
    hashes=json.loads((node_dir(node)/'remote-artifact-hashes.json').read_text())
    assert all(sha(LOG/p)==h for p,h in hashes.items())
    return len(hashes)


def cleanup(node):
    path=Path(node_spec(node)['state'])
    cloud(node,'terminate').check_returncode()
    for _ in range(60):
        cloud(node,'status').check_returncode();state=json.loads(path.read_text())
        if state['status']=='terminated':break
        time.sleep(10)
    else:raise RuntimeError('Termination unconfirmed; leave watchdog and key')
    state.setdefault('first_termination_confirmed_at',now())
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.chmod(0o600);temporary.replace(path)
    if not state.get('ssh_key_deleted_at'):cloud(node,'delete-key').check_returncode()
    state=json.loads(path.read_text());private=Path(state['private_key_path']);private.unlink(missing_ok=True);private.with_suffix('.pub').unlink(missing_ok=True)
    seconds=(dt.datetime.fromisoformat(state['first_termination_confirmed_at'])-dt.datetime.fromisoformat(state['launch_requested_at'])).total_seconds()
    minutes=math.ceil(seconds/60)
    write_json(node_dir(node)/'cloud_lifecycle.json',{'node':node,'instance_id':state['instance_id'],'name':state['name'],
        'instance_type':state['instance_type'],'region':state['region'],'usd_per_hour':state['usd_per_hour'],
        'launch_requested_at':state['launch_requested_at'],'termination_requested_at':state.get('termination_requested_at'),
        'termination_confirmed_at':state['first_termination_confirmed_at'],'rounded_elapsed_minutes':minutes,
        'estimated_gpu_cost_usd':minutes/60*state['usd_per_hour'],'status':'terminated',
        'cloud_ssh_key_deleted_at':state['ssh_key_deleted_at'],'local_temporary_key_deleted':True})


def record_lifecycle():
    lifecycle=[]
    for node in plan()['nodes']:
        p=node_dir(node)/'cloud_lifecycle.json'
        if p.exists():lifecycle.append(json.loads(p.read_text()))
    current=sum(r['estimated_gpu_cost_usd'] for r in lifecycle)
    snapshot=cost_snapshot();prior_cost=snapshot['prior_attempts_gpu_cost_usd']
    total=current+prior_cost
    allocated=[n for n,s in plan()['nodes'].items() if Path(s['state']).exists()]
    complete=len(lifecycle)==len(allocated) and all(r['status']=='terminated' and r['cloud_ssh_key_deleted_at'] for r in lifecycle) and all(json.loads(Path(p).read_text()).get('ssh_key_deleted_at') for p in plan()['retired_state_paths'])
    if not complete:
        running=cost_snapshot();current=running['current_nodes_gpu_cost_usd'];total=running['estimated_total_usd']
    receipt={'nodes':lifecycle,'estimated_gpu_cost_usd':total,'additional_cap_usd':65,
        'current_nodes_gpu_cost_usd':current,'prior_attempts_gpu_cost_usd':prior_cost,'retired_nodes':snapshot['retired_nodes'],
        'prior_attempts_receipt':'separate_a100/prior_cloud_lifecycle.json', 'additional_retired_receipts':'hardware_recovery/retired_nodes.json',
        'within_cap':total<=65,'status':'all_terminated' if complete else 'cleanup_pending',
        'all_temporary_keys_deleted':complete,
        'cost_basis':'Each owned node launch through first confirmed termination rounded up to a minute, plus both earlier failed allocations; GPU estimate, not invoice.'}
    write_json(LOG/'cloud_lifecycle.json',receipt)
    return receipt


def maybe_analyze():
    nodes=plan()['nodes'];results=[]
    for node in nodes:
        p=node_dir(node)/'supervisor-result.json'
        if not p.exists():return
        d=json.loads(p.read_text());results.append(d)
    record_lifecycle()
    if not all(d['download_hashes_verified'] and not d['failure'] and d['controller_result']['returncode']==0 for d in results):return
    try:
        with (PARALLEL/'analysis-started.json').open('x') as f:json.dump({'pid':os.getpid(),'at':now()},f)
    except FileExistsError:return
    record_lifecycle()
    with (PARALLEL/'offline-analysis-console.log').open('x') as output:
        for script in ('scripts/verify_revised_recovery.py','scripts/analyze_revised.py'):
            done=subprocess.run(['.local/preparation/venv/bin/python',script],stdout=output,stderr=subprocess.STDOUT)
            if done.returncode:break
    write_json(PARALLEL/'offline-analysis-result.json',{'script':script,'returncode':done.returncode,'finished_at':now()})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',choices=plan()['nodes'],required=True)
    node=parser.parse_args().node;out=node_dir(node);out.mkdir(parents=True,exist_ok=True)
    with (out/'supervisor-started.json').open('x') as f:json.dump({'pid':os.getpid(),'started_at':now()},f)
    failure=None;verified=False;result=None;hashes=0
    try:
        errors=0
        while True:
            try:
                collect(node);errors=0
                p=out/'controller-result.json'
                if p.exists():result=json.loads(p.read_text());break
            except (OSError,ValueError,subprocess.SubprocessError) as exc:
                errors+=1;print(f'Collection error {errors}: {exc}',flush=True)
                # Lost transport is unknown, not evidence that the model failed.
                # Read-only collection reconnects without repeating any model work.
                write_json(out/'collection-transport-error.json',{'at':now(),'error':str(exc),'consecutive_errors':errors})
            dispatch=out/'controller-dispatch.json'
            if dispatch.exists() and json.loads(dispatch.read_text())['status']=='failed_start':
                raise RuntimeError('Remote dispatcher confirmed failed process creation')
            own=json.loads(Path(node_spec(node)['state']).read_text())
            if own['status'] in ('terminated','terminating') or cost_snapshot()['estimated_total_usd']>=plan()['aggregate_termination_threshold_usd']:
                raise RuntimeError('Cumulative budget stop or owned instance termination before verified completion')
            print(json.dumps({'node':node,'at':now(),'running':True}),flush=True);time.sleep(60)
        hashes=finalize_hashes(node);verified=True
        if result['returncode']!=0:failure='Node controller exited '+str(result['returncode'])
    except BaseException as exc:
        failure=type(exc).__name__+': '+str(exc)
        try:collect(node)
        except Exception:pass
    finally:
        if failure:
            try:
                with (PARALLEL/'abort.json').open('x') as f:json.dump({'node':node,'at':now(),'reason':failure},f,indent=2)
            except FileExistsError:pass
        try:cleanup(node)
        except BaseException as exc:failure=(failure+'; ' if failure else '')+'Cleanup: '+str(exc)
        write_json(out/'supervisor-result.json',{'node':node,'finished_at':now(),'controller_result':result,
            'download_hashes_verified':verified,'verified_files':hashes,'failure':failure})
    maybe_analyze()


if __name__=='__main__':main()
