#!/usr/bin/env python3
"""Local artifact collection and owner-scoped cleanup for exactly one 010 job.

No model execution, launching, retries of training/generation, or experiment edits.
Cloud credential stays on this Mac. A separate watchdog is started at rental.
"""
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
STATE=Path('.local/lambda-corrective-comparison/state.json')
LOG=Path('experiment_log/010_corrective_comparison')
REMOTE='/home/ubuntu/swarm-solidarity'
REMOTE_LOG=REMOTE+'/'+str(LOG)

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def connection():
    state=json.loads(STATE.read_text())
    ssh=['ssh','-i',state['private_key_path'],'-o','BatchMode=yes','-o','ConnectTimeout=15',
         '-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(STATE.parent/'known_hosts'),
         '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
    return ssh,'ubuntu@'+state['ip']


def remote(command):
    ssh,host=connection()
    return subprocess.check_output(ssh+[host,'cd '+REMOTE+' && '+shlex.join(command)],text=True,timeout=90)


def rsync(source,destination,options=None):
    ssh,host=connection();Path(destination).mkdir(parents=True,exist_ok=True)
    subprocess.run(['rsync','-az','--timeout=60',*(options or []),'-e',shlex.join(ssh),host+':'+source,str(destination)+'/'],check=True,timeout=180)


def collect():
    rsync(REMOTE_LOG+'/',LOG,['--include=execution/***','--include=controller-*.json',
        '--include=bootstrap.log','--include=remote-artifact-hashes.json','--exclude=*'])
    config=json.loads(Path('configs/corrective-comparison.json').read_text())
    for run in config['training_execution_order']:
        meta_path=LOG/'execution/training'/run/'metadata.json'
        if not meta_path.exists():continue
        meta=json.loads(meta_path.read_text())
        if meta.get('status')!='complete':continue
        dest=Path('.local/corrective')/run/'terminal-adapter'
        hashes=meta['terminal_adapter_files']
        if dest.exists() and all((dest/p).exists() and sha(dest/p)==h for p,h in hashes.items()):continue
        rsync(REMOTE+'/.local/corrective/'+run+'/terminal-adapter/',dest)
        assert all(sha(dest/p)==h for p,h in hashes.items()),run


def cleanup():
    # Termination/status requests are idempotent and owner-checked by the existing client.
    result=subprocess.run([sys.executable,'scripts/lambda_cloud.py','terminate','--state',str(STATE)],timeout=90)
    if result.returncode:raise RuntimeError('Owned termination request failed; watchdog remains active')
    for _ in range(12):
        subprocess.run([sys.executable,'scripts/lambda_cloud.py','status','--state',str(STATE)],timeout=90,check=True)
        state=json.loads(STATE.read_text())
        if state['status']=='terminated':break
        time.sleep(10)
    else:raise RuntimeError('Termination not yet confirmed; keep watchdog and key')
    confirmed=now();state=json.loads(STATE.read_text())
    started=dt.datetime.fromisoformat(state['launch_requested_at'])
    seconds=(dt.datetime.fromisoformat(confirmed)-started).total_seconds();minutes=math.ceil(seconds/60)
    subprocess.run([sys.executable,'scripts/lambda_cloud.py','delete-key','--state',str(STATE)],timeout=90,check=True)
    state=json.loads(STATE.read_text())
    private=Path(state['private_key_path']);private.unlink(missing_ok=True);private.with_suffix('.pub').unlink(missing_ok=True)
    write(LOG/'cloud_lifecycle.json',{'instance_id':state['instance_id'],'name':state['name'],
        'instance_type':state['instance_type'],'region':state['region'],'usd_per_hour':state['usd_per_hour'],
        'launch_requested_at':state['launch_requested_at'],'termination_requested_at':state.get('termination_requested_at'),
        'termination_confirmed_at':confirmed,'rounded_elapsed_minutes':minutes,
        'estimated_gpu_cost_usd':round(minutes/60*state['usd_per_hour'],4),'additional_cap_usd':30,
        'within_cap':minutes/60*state['usd_per_hour']<=30,'status':'terminated',
        'cloud_ssh_key_deleted_at':state['ssh_key_deleted_at'],'local_temporary_ssh_key_deleted':True,
        'cost_basis':'Conservative launch-request through first termination confirmation, rounded up to full minute; GPU-only estimate, not invoice.'})


def main():
    with (STATE.parent/'supervisor-started.json').open('x') as f:json.dump({'pid':os.getpid(),'started_at':now()},f)
    failure=None;verified=False;result=None
    try:
        failures=0
        while True:
            try:
                collect()
                result_path=LOG/'controller-result.json'
                if result_path.exists():
                    result=json.loads(result_path.read_text());break
                failures=0
            except (OSError,ValueError,subprocess.SubprocessError) as exc:
                failures+=1;print('Collection transient error '+str(failures)+': '+str(exc),flush=True)
                if failures>=3:raise RuntimeError('Three consecutive collection failures; stopping rental') from exc
            print(json.dumps({'checked_at':now(),'running':True}),flush=True)
            time.sleep(60)
        # The controller has exited; now snapshot all immutable run files.
        program="from pathlib import Path; import hashlib,json; p=Path('experiment_log/010_corrective_comparison'); files=[x for x in (p/'execution').rglob('*') if x.is_file()]+list(p.glob('controller-*.json')); (p/'remote-artifact-hashes.json').write_text(json.dumps({str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(files)},indent=2)+'\\n')"
        remote(['python3','-c',program]);collect()
        hashes=json.loads((LOG/'remote-artifact-hashes.json').read_text())
        assert all(sha(LOG/p)==h for p,h in hashes.items())
        verified=True
    except BaseException as exc:
        failure=type(exc).__name__+': '+str(exc)
        try:collect()
        except Exception:pass
    finally:
        try:cleanup()
        except BaseException as exc:
            failure=(failure+'; ' if failure else '')+'Cleanup: '+type(exc).__name__+': '+str(exc)
        write(LOG/'supervisor-result.json',{'finished_at':now(),'controller_result':result,
            'download_hashes_verified':verified,'failure':failure})
    # CPU verification/analysis happens after termination; cannot increase GPU spend.
    if verified and result and result['returncode']==0 and not failure:
        with (LOG/'offline-analysis-console.log').open('x') as output:
            for script in ('scripts/verify_corrective.py','scripts/analyze_corrective.py'):
                done=subprocess.run(['.local/preparation/venv/bin/python',script],stdout=output,stderr=subprocess.STDOUT)
                if done.returncode:break
        write(LOG/'offline-analysis-result.json',{'script':script,'returncode':done.returncode,'finished_at':now()})


if __name__=='__main__':main()
