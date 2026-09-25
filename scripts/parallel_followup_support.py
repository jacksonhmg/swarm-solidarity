"""Owner-scoped new follow-up resources, isolated from closed experiments."""
import datetime as dt
import fcntl
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
import time
from followup_support import LOG, sha, write_json
from lambda_cloud import now, save, api

CLOUD=LOG/'cloud';REMOTE='/home/ubuntu/swarm-solidarity'
def plan():return json.loads((LOG/'parallel/plan.json').read_text())
def folder(node):return CLOUD/node
def statepath(node):return Path(plan()['nodes'][node]['state'])
def state(node):return json.loads(statepath(node).read_text())
def account(endpoint):
    CLOUD.mkdir(parents=True,exist_ok=True)
    with (CLOUD/'api.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        try:return api(endpoint)
        finally:time.sleep(1.1)
def cloud(node,action,extra=()):
    CLOUD.mkdir(parents=True,exist_ok=True)
    with (CLOUD/'api.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        result=subprocess.run([sys.executable,'scripts/lambda_cloud.py',action,'--state',str(statepath(node)),*extra],capture_output=True,text=True,timeout=150)
        if result.returncode:raise RuntimeError(result.stderr or result.stdout)
        if statepath(node).exists():
            s=state(node)
            if s.get('status')=='terminated' and not s.get('first_termination_confirmed_at'):
                s['first_termination_confirmed_at']=now();save(statepath(node),s)
        time.sleep(1.1)
        return result.stdout
def ssh(node):
    s=state(node);return ['ssh','-i',s['private_key_path'],'-o','BatchMode=yes','-o','ConnectTimeout=15','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(statepath(node).parent/'known_hosts'),'-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2'],'ubuntu@'+s['ip']
def remote(node,command,timeout=60):
    args,host=ssh(node)
    return subprocess.check_output(args+[host,'cd '+shlex.quote(REMOTE)+' && '+shlex.join(command)],text=True,timeout=timeout)
def pull(node,source,destination):
    args,host=ssh(node);Path(destination).mkdir(parents=True,exist_ok=True)
    subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),host+':'+REMOTE+'/'+str(source)+'/',str(destination)+'/'],check=True,timeout=180,stdout=subprocess.DEVNULL)
def costs():
    rows=[];at=dt.datetime.now(dt.timezone.utc)
    for node in plan()['nodes']:
        if not statepath(node).exists():continue
        s=state(node)
        if 'launch_requested_at' not in s:continue
        end=dt.datetime.fromisoformat(s['first_termination_confirmed_at']) if s.get('first_termination_confirmed_at') else at
        minutes=math.ceil(max(0,(end-dt.datetime.fromisoformat(s['launch_requested_at'])).total_seconds())/60)
        rows.append({'node':node,'instance_id':s.get('instance_id'),'status':s['status'],'minutes':minutes,'usd':minutes/60*s['usd_per_hour']})
    return {'at':now(),'nodes':rows,'estimated_usd':sum(r['usd'] for r in rows),'new_gpu_cap_usd':plan()['new_gpu_cap_usd'],'basis':'Launch through first confirmed termination, rounded up to minute; estimate, not invoice. Closed011 costs excluded.'}
def background(script,arguments,log):
    Path(log).parent.mkdir(parents=True,exist_ok=True)
    with Path(log).open('x') as f:
        p=subprocess.Popen(['caffeinate','-ims',sys.executable,script,*arguments],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    return p.pid
def cleanup(node):
    if not statepath(node).exists():return
    cloud(node,'terminate')
    for _ in range(180):
        cloud(node,'status');s=state(node)
        if s['status']=='terminated':break
        time.sleep(10)
    else:raise RuntimeError('Provider termination remains unconfirmed; keep watchdog')
    if not s.get('ssh_key_deleted_at'):cloud(node,'delete-key')
    s=state(node);p=Path(s['private_key_path']);p.unlink(missing_ok=True);p.with_suffix('.pub').unlink(missing_ok=True)
    write_json(folder(node)/'cleanup.json',{'instance_id':s['instance_id'],'name':s['name'],'status':s['status'],'termination_confirmed_at':s['first_termination_confirmed_at'],'cloud_key_deleted_at':s['ssh_key_deleted_at'],'local_keys_deleted':not p.exists() and not p.with_suffix('.pub').exists(),'cost':next(r for r in costs()['nodes'] if r['node']==node)})
