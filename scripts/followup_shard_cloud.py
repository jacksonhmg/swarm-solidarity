"""Twenty-worker follow-up scheduling; all cloud actions scoped to owner files."""
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from followup_support import LOG, sha, write_json
from lambda_cloud import api, now, save

ROOT=LOG/'sharding'
REMOTE='/home/ubuntu/swarm-solidarity'
def plan():return json.loads((ROOT/'plan.json').read_text())
def folder(job):return ROOT/'nodes'/job
def statepath(job):return Path(plan()['jobs'][job]['state'])
def state(job):return json.loads(statepath(job).read_text())
def locked(fn):
    with (LOG/'cloud/api.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        try:return fn()
        finally:time.sleep(1.1)
def account(endpoint):return locked(lambda:api(endpoint))
def cloud(job,action,extra=()):
    def run():
        r=subprocess.run([sys.executable,'scripts/lambda_cloud.py',action,'--state',str(statepath(job)),*extra],capture_output=True,text=True,timeout=150)
        if r.returncode:raise RuntimeError(r.stderr or r.stdout)
        if statepath(job).exists():
            s=state(job)
            if s.get('status')=='terminated' and not s.get('first_termination_confirmed_at'):
                s['first_termination_confirmed_at']=now();save(statepath(job),s)
        return r.stdout
    return locked(run)
def ssh(job):
    s=state(job)
    return ['ssh','-i',s['private_key_path'],'-o','BatchMode=yes','-o','ConnectTimeout=15','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(statepath(job).parent/'known_hosts'),'-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2'],'ubuntu@'+s['ip']
def remote(job,command,timeout=90):
    args,host=ssh(job)
    return subprocess.check_output(args+[host,'cd '+shlex.quote(REMOTE)+' && '+shlex.join(command)],text=True,timeout=timeout)
def pull(job,source,dest):
    args,host=ssh(job);Path(dest).mkdir(parents=True,exist_ok=True)
    subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),host+':'+REMOTE+'/'+str(source)+'/',str(dest)+'/'],check=True,timeout=180,stdout=subprocess.DEVNULL)
def costs():
    at=dt.datetime.now(dt.timezone.utc);rows=[]
    paths={**plan()['prior_states'],**{j:s['state'] for j,s in plan()['jobs'].items()}}
    for job,path in paths.items():
        if not Path(path).exists():continue
        s=json.loads(Path(path).read_text())
        if 'launch_requested_at' not in s:continue
        end=dt.datetime.fromisoformat(s['first_termination_confirmed_at']) if s.get('first_termination_confirmed_at') else at
        mins=math.ceil(max(0,(end-dt.datetime.fromisoformat(s['launch_requested_at'])).total_seconds())/60)
        rows.append({'job':job,'instance_id':s.get('instance_id'),'status':s['status'],'minutes':mins,'usd':mins/60*s['usd_per_hour']})
    return {'at':now(),'nodes':rows,'estimated_usd':sum(r['usd'] for r in rows),'cap_usd':65,'basis':'All013/014 allocations, launch through confirmed termination rounded up to minute; estimate not invoice.'}
def background(script,args,log):
    Path(log).parent.mkdir(parents=True,exist_ok=True)
    with Path(log).open('x') as f:
        return subprocess.Popen(['caffeinate','-ims',sys.executable,script,*args],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True).pid
def cleanup(job):
    if not statepath(job).exists():return
    cloud(job,'terminate')
    for _ in range(180):
        cloud(job,'status');s=state(job)
        if s['status']=='terminated':break
        time.sleep(10)
    else:raise RuntimeError('Termination unconfirmed; watchdog remains active')
    if not s.get('ssh_key_deleted_at'):cloud(job,'delete-key')
    s=state(job);p=Path(s['private_key_path']);p.unlink(missing_ok=True);p.with_suffix('.pub').unlink(missing_ok=True)
    write_json(folder(job)/'cleanup.json',{'instance_id':s['instance_id'],'status':s['status'],'termination_confirmed_at':s['first_termination_confirmed_at'],'cloud_key_deleted_at':s['ssh_key_deleted_at'],'local_keys_deleted':not p.exists() and not p.with_suffix('.pub').exists()})
