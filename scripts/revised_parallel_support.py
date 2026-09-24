"""Eight owner-scoped independent GPU assignments; no inference changes."""
import datetime as dt
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
from revised_support import LOG, CONDITIONS, sha, write_json, verify_freeze

PLAN=LOG/'parallel_plan.json'
PARALLEL=LOG/'parallel'
REMOTE='/home/ubuntu/swarm-solidarity'


def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def plan():return json.loads(PLAN.read_text())
def node_spec(node):return plan()['nodes'][node]
def node_dir(node):return PARALLEL/node


def verify_plan():
    frozen=verify_freeze()
    assignments=[c for spec in plan()['nodes'].values() for c in spec['conditions']]
    assert len(assignments)==len(set(assignments))==8 and set(assignments)==set(CONDITIONS)
    assert all(len(s['conditions'])==1 for s in plan()['nodes'].values())
    return frozen


def ssh(node):
    path=Path(node_spec(node)['state']);state=json.loads(path.read_text())
    args=['ssh','-i',state['private_key_path'],'-o','BatchMode=yes','-o','ConnectTimeout=15',
          '-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(path.parent/'known_hosts'),
          '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
    return args,'ubuntu@'+state['ip']


def remote(node,command,timeout=90):
    args,host=ssh(node)
    return subprocess.check_output(args+[host,'cd '+REMOTE+' && '+shlex.join(command)],text=True,timeout=timeout)


def pull(node,source,destination,options=None):
    args,host=ssh(node);Path(destination).mkdir(parents=True,exist_ok=True)
    subprocess.run(['rsync','-az','--timeout=60',*(options or []),'-e',shlex.join(args),host+':'+REMOTE+'/'+source,str(destination)+'/'],check=True,timeout=180)


def cost_snapshot(at=None):
    at=at or dt.datetime.now(dt.timezone.utc);rows=[]
    for node,spec in plan()['nodes'].items():
        path=Path(spec['state'])
        if not path.exists():continue
        state=json.loads(path.read_text())
        if 'launch_requested_at' not in state:continue
        end=state.get('first_termination_confirmed_at')
        if not end and state.get('status')=='terminated':end=state['last_checked_at']
        end=dt.datetime.fromisoformat(end) if end else at
        minutes=math.ceil(max(0,(end-dt.datetime.fromisoformat(state['launch_requested_at'])).total_seconds())/60)
        rows.append({'node':node,'instance_id':state.get('instance_id'),'status':state['status'],
            'rounded_elapsed_minutes':minutes,'usd_per_hour':state['usd_per_hour'],'estimated_usd':minutes/60*state['usd_per_hour']})
    return {'at':at.isoformat(),'nodes':rows,'estimated_total_usd':sum(r['estimated_usd'] for r in rows),'hard_ceiling_usd':40}


def cloud(node,action):
    return subprocess.run([sys.executable,'scripts/lambda_cloud.py',action,'--state',node_spec(node)['state']],timeout=90)
