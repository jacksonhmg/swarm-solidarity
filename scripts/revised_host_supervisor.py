#!/usr/bin/env python3
"""Single-host artifact collection, verified cleanup and frozen CPU analysis."""
import datetime as dt
import json
import math
import os
from pathlib import Path
import subprocess
import time
from revised_host_support import (HOST, LOG, STATE, plan, state, remote, pull, cloud, now, sha, write_json, snapshot)

def collect():
    # Never download over the immutable offline artifacts or local-only receipts.
    pull(HOST, HOST/'remote')
    present=json.loads(remote(['python3','-c',"import json; from pathlib import Path; print(json.dumps(Path('experiment_log/011_benign_audit_confirmation/execution').exists()))"]))
    if present: pull(LOG/'execution', LOG/'execution')
    for run in ('revised_s41031','revised_s41032'):
        meta=LOG/'execution/training'/run/'metadata.json'
        if meta.exists():
            data=json.loads(meta.read_text())
            if data.get('status')=='complete':
                adapter=Path('.local/revised_corrective')/run/'terminal-adapter'
                pull(adapter,adapter)
                assert all(sha(adapter/name)==h for name,h in data['terminal_adapter_files'].items())

def finalize_hashes():
    program="""from pathlib import Path
import json,hashlib
p=Path('experiment_log/011_benign_audit_confirmation')
files=[x for folder in (p/'host',p/'execution') for x in folder.rglob('*') if x.is_file() and x.name not in ('remote-artifact-hashes.json','remote-console.log')]
(p/'host/remote-artifact-hashes.json').write_text(json.dumps({str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(files)},indent=2)+'\\n')
"""
    remote(['python3','-c',program]);collect()
    hashes=json.loads((HOST/'remote/remote-artifact-hashes.json').read_text())
    for name,h in hashes.items():
        local=HOST/'remote'/name.removeprefix('host/') if name.startswith('host/') else LOG/name
        assert sha(local)==h,name
    return len(hashes)

def cleanup():
    cloud('terminate').check_returncode()
    for _ in range(24):
        cloud('status').check_returncode();s=state()
        if s['status']=='terminated': break
        time.sleep(5)
    else: raise RuntimeError('Termination unconfirmed; watchdog remains active')
    s.setdefault('first_termination_confirmed_at',now())
    from lambda_cloud import save
    save(STATE,s)
    if not s.get('ssh_key_deleted_at'): cloud('delete-key').check_returncode()
    s=state();private=Path(s['private_key_path']);private.unlink(missing_ok=True);private.with_suffix('.pub').unlink(missing_ok=True)
    cost=snapshot()
    receipt={'instance_id':s['instance_id'],'name':s['name'],'instance_type':s['instance_type'],'region':s['region'],
        'usd_per_hour':s['usd_per_hour'],'launch_requested_at':s['launch_requested_at'],
        'termination_requested_at':s.get('termination_requested_at'),'termination_confirmed_at':s['first_termination_confirmed_at'],
        'rounded_elapsed_minutes':cost['rounded_elapsed_minutes'],'estimated_gpu_cost_usd':cost['estimated_total_usd'],
        'additional_cap_usd':65,'within_cap':cost['estimated_total_usd']<=65,'status':'terminated',
        'cloud_ssh_key_deleted_at':s['ssh_key_deleted_at'],'local_temporary_key_deleted':True,
        'cost_basis':'Owned experiment-011 launch request through first confirmed termination, rounded up to whole minute; GPU estimate, not invoice.'}
    write_json(LOG/'cloud_lifecycle.json',receipt)

def main():
    with (HOST/'supervisor-started.json').open('x') as f: json.dump({'pid':os.getpid(),'at':now()},f)
    failure=None;verified=False;result=None;hashes=0
    try:
        errors=0
        while True:
            try:
                collect();errors=0
                p=HOST/'remote/controller-result.json'
                if p.exists(): result=json.loads(p.read_text());break
            except (OSError,ValueError,subprocess.SubprocessError) as exc:
                errors+=1;print(f'Collection error {errors}: {exc}',flush=True)
                if errors>=3: raise RuntimeError('Three consecutive collection failures') from exc
            print(json.dumps({'at':now(),'running':True,'budget':snapshot()}),flush=True)
            time.sleep(45)
        hashes=finalize_hashes();verified=True
        if result['returncode']!=0: failure='Host controller exited '+str(result['returncode'])
    except BaseException as exc:
        failure=type(exc).__name__+': '+str(exc)
        try: collect()
        except Exception: pass
    finally:
        if failure: write_json(HOST/'abort.json',{'at':now(),'reason':failure})
        try: cleanup()
        except BaseException as exc: failure=(failure+'; ' if failure else '')+'Cleanup: '+str(exc)
        write_json(HOST/'supervisor-result.json',{'finished_at':now(),'controller_result':result,
            'download_hashes_verified':verified,'verified_files':hashes,'failure':failure})
    if not failure:
        with (HOST/'offline-analysis-console.log').open('x') as output:
            for script in ('scripts/verify_revised_host.py','scripts/analyze_revised.py'):
                done=subprocess.run(['.local/preparation/venv/bin/python',script],stdout=output,stderr=subprocess.STDOUT)
                if done.returncode: break
        write_json(HOST/'offline-analysis-result.json',{'script':script,'returncode':done.returncode,'finished_at':now()})

if __name__=='__main__': main()
