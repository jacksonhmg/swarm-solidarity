#!/usr/bin/env python3
"""One capacity check/owned launch. A wait flag polls capacity without renting idle GPUs."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from revised_host_support import HOST, LOG, STATE, REMOTE, plan, verify, now, state, ssh, cloud, sha, write_json, cost_feasible
from lambda_cloud import api

def background(script):
    output=(HOST/(Path(script).stem+'.log')).open('x')
    proc=subprocess.Popen(['caffeinate','-ims',sys.executable,script],stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    output.close();return proc.pid

def bundle():
    verify()
    assert not STATE.exists(), 'Inspect existing ownership state; never launch twice'
    assert not (LOG/'execution').exists(), 'Model work already exists'
    assert not any(Path(p['state']).exists() for p in json.loads((LOG/'parallel_plan.json').read_text())['nodes'].values()), 'Separate-host route already used'
    for p in (LOG/'freeze.json',LOG/'host_freeze.json'):
        assert subprocess.check_output(['git','status','--porcelain','--',str(p)],text=True)=='', 'Commit freezes before launch'
    revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    Path('.code-revision').write_text(revision+'\n')
    tracked=subprocess.check_output(['git','ls-files','-z'])
    files=tracked.split(b'\0');files=[p for p in files if p]
    # Cloud credentials, SSH keys, local environments and merged weights are never transferred.
    adapters=[Path('.local/preparation/terminal-adapter')]
    adapters += [Path('.local/corrective')/run/'terminal-adapter' for run in plan()['assignments'] if run.startswith(('ordinary_','corrective_'))]
    for adapter in adapters:
        assert adapter.exists()
        files += [str(p).encode() for p in adapter.rglob('*') if p.is_file()]
    files.append(b'.code-revision')
    destination=STATE.parent;destination.mkdir(parents=True,exist_ok=True)
    manifest=destination/'bundle-files.list';manifest.write_bytes(b'\0'.join(files)+b'\0')
    archive=destination/'source.tar.gz'
    subprocess.run(['tar','-czf',str(archive),'--null','-T',str(manifest)],check=True)
    write_json(HOST/'bundle.json',{'code_revision':revision,'files':len(files),'bytes':archive.stat().st_size,'sha256':sha(archive),'created_at':now()})
    return archive

def select():
    capacity=api('instance-types');available=[];rows=[]
    for kind,spec in plan()['instance_types'].items():
        entry=capacity[kind];rate=entry['instance_type']['price_cents_per_hour']/100
        regions=entry['regions_with_capacity_available']
        rows.append({'type':kind,'usd_per_hour':rate,'regions':regions})
        if regions and rate<=spec['maximum_hourly_usd'] and cost_feasible(kind):
            available.append((kind,regions[0]['name'],rate))
    write_json(HOST/'capacity-latest.json',{'checked_at':now(),'types':rows,'rentals':0 if not STATE.exists() else 1})
    return available[0] if available else None

def launch(choice,archive):
    kind,region,price=choice
    assert not STATE.exists()
    # No POST retry. State/name survive an uncertain response for explicit reconciliation.
    try:
        subprocess.run([sys.executable,'scripts/lambda_cloud.py','launch','--state',str(STATE),
                        '--instance-type',kind,'--region',region,'--max-hourly-usd',str(price)],check=True)
    except BaseException as exc:
        write_json(HOST/'launch-error.json',{'at':now(),'error':type(exc).__name__+': '+str(exc),
            'decision':'No launch POST retry. Reconcile preserved owner name if state exists.'})
        if STATE.exists():
            # Status reconciliation can recover an instance ID after an uncertain POST.
            cloud('status').check_returncode()
            from revised_host_supervisor import cleanup
            cleanup()
        raise
    watchdog=background('scripts/revised_host_watchdog.py')
    write_json(HOST/'launch-receipt.json',{'at':now(),'instance_id':state()['instance_id'],'watchdog_pid':watchdog})
    try:
        for _ in range(90):
            cloud('status').check_returncode()
            if state()['status']=='active' and state().get('ip'):break
            time.sleep(5)
        else:raise RuntimeError('Instance did not become active within boot allowance')
        args,host=ssh()
        for _ in range(24):
            ready=subprocess.run(args+[host,'true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if ready.returncode==0:break
            time.sleep(5)
        else:raise RuntimeError('SSH never became ready')
        s=state()
        selection={k:s[k] for k in ('instance_id','instance_type','region','usd_per_hour','launch_requested_at')}
        selection.update(at=now(),authorized_ceiling_usd=65)
        write_json(HOST/'selection.json',selection)
        subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True)
        subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(archive),host+':'+REMOTE+'/source.tar.gz'],check=True,timeout=300)
        program='cd '+shlex.quote(REMOTE)+' && tar -xzf source.tar.gz && rm source.tar.gz && mkdir -p '+str(HOST)
        subprocess.run(args+[host,program],check=True,timeout=90)
        subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(HOST/'selection.json'),host+':'+REMOTE+'/'+str(HOST)+'/selection.json'],check=True,timeout=60)
        remote_command='cd '+shlex.quote(REMOTE)+' && nohup python3 scripts/run_revised_host.py > '+str(HOST/'remote-console.log')+' 2>&1 < /dev/null &'
        subprocess.run(args+[host,remote_command],check=True,timeout=45)
        supervisor=background('scripts/revised_host_supervisor.py')
        write_json(HOST/'dispatch.json',{'at':now(),'instance_id':s['instance_id'],'supervisor_pid':supervisor,'watchdog_pid':watchdog,'conditions':list(plan()['assignments'])})
        print('Owned host launched; independent watchdog and collection supervisor started.',flush=True)
    except BaseException as exc:
        write_json(HOST/'abort.json',{'at':now(),'reason':type(exc).__name__+': '+str(exc)})
        from revised_host_supervisor import cleanup
        cleanup()
        raise

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    HOST.mkdir(parents=True,exist_ok=True);STATE.parent.mkdir(parents=True,exist_ok=True)
    with (STATE.parent/'launcher.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        archive=bundle()
        if args.prepare_only:return
        errors=0
        while True:
            verify()
            try:
                choice=select();errors=0
            except Exception as exc:
                errors+=1
                if errors>=3:
                    write_json(HOST/'availability-error.json',{'at':now(),'error':type(exc).__name__+': '+str(exc)})
                    raise
                if not args.wait:raise
                time.sleep(30);continue
            if choice:launch(choice,archive);return
            if not args.wait:
                print('No approved eight-A100 host has capacity. No rental.',flush=True);return
            time.sleep(30)

if __name__=='__main__':main()
