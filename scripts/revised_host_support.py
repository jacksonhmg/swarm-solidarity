"""Single owner, eight independent GPUs; experiment 011 scheduling amendment."""
import datetime as dt
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
from revised_support import LOG, CONDITIONS, sha, write_json, verify_freeze

HOST = LOG/'host'
PLAN = LOG/'host_plan.json'
STATE = Path('.local/lambda-revised-host/state.json')
REMOTE = '/home/ubuntu/swarm-solidarity'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def plan(): return json.loads(PLAN.read_text())
def state(): return json.loads(STATE.read_text())

def verify():
    old = verify_freeze()
    amendment = json.loads((LOG/'host_freeze.json').read_text())
    for path, digest in amendment['files'].items():
        assert sha(path) == digest, path
    assert set(plan()['assignments']) == set(CONDITIONS)
    assert sorted(plan()['assignments'].values()) == list(range(8))
    return old, amendment

def snapshot(at=None):
    s = state(); at = at or dt.datetime.now(dt.timezone.utc)
    end = dt.datetime.fromisoformat(s['first_termination_confirmed_at']) if s.get('first_termination_confirmed_at') else at
    minutes = math.ceil(max(0, (end-dt.datetime.fromisoformat(s['launch_requested_at'])).total_seconds())/60)
    return {'at': at.isoformat(), 'instance_id': s.get('instance_id'), 'status': s['status'],
            'rounded_elapsed_minutes': minutes, 'usd_per_hour': s['usd_per_hour'],
            'estimated_total_usd': minutes/60*s['usd_per_hour'], 'hard_ceiling_usd': 65}

def cloud(action):
    import fcntl
    with (STATE.parent/'cloud.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = subprocess.run([sys.executable, 'scripts/lambda_cloud.py', action, '--state', str(STATE)], timeout=90)
        if result.returncode == 0 and STATE.exists():
            s = state()
            if s.get('status') == 'terminated' and not s.get('first_termination_confirmed_at'):
                from lambda_cloud import save
                s['first_termination_confirmed_at'] = now(); save(STATE,s)
        return result

def ssh():
    s = state()
    return ['ssh', '-i', s['private_key_path'], '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
            '-o', 'StrictHostKeyChecking=accept-new', '-o', 'UserKnownHostsFile='+str(STATE.parent/'known_hosts'),
            '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2'], 'ubuntu@'+s['ip']

def remote(command, timeout=90):
    args, host = ssh()
    return subprocess.check_output(args+[host, 'cd '+REMOTE+' && '+shlex.join(command)], text=True, timeout=timeout)

def pull(source, destination):
    args, host = ssh(); Path(destination).mkdir(parents=True, exist_ok=True)
    subprocess.run(['rsync', '-az', '--timeout=60', '-e', shlex.join(args),
                    host+':'+REMOTE+'/'+str(source)+'/', str(destination)+'/'], check=True, timeout=240)

def cost_feasible(instance_type):
    spec = plan()['instance_types'][instance_type]
    return plan()['projected_wall_seconds']/3600*spec['maximum_hourly_usd'] < plan()['termination_threshold_usd']
