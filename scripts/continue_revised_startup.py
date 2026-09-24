#!/usr/bin/env python3
"""Continue allocated, undispatched nodes. No training or sampling retries."""
import concurrent.futures
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

from revised_recovery_support import (LOG, PARALLEL, REMOTE, plan, node_dir,
    node_spec, ssh, now, sha, write_json, verify_plan, cost_snapshot)
from launch_revised_recovery import prepare_node, dispatch, capacity, TRANSFER


def cloud_state(state_path, action):
    with (LOG/'separate_a100/api.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = subprocess.run([sys.executable, 'scripts/lambda_cloud.py', action,
                                 '--state', str(state_path)], check=True, timeout=90)
        time.sleep(1.1)
        return result


def finish_retired_prepared():
    state_path = Path(plan()['retired_state_paths'][-1])
    for _ in range(90):
        cloud_state(state_path, 'status')
        state = json.loads(state_path.read_text())
        if state['status'] == 'terminated':
            break
        assert state['status'] == 'terminating', 'Do not terminate a healthy node'
        time.sleep(5)
    else:
        raise RuntimeError('Provider has not confirmed prepared-node termination')
    from lambda_cloud import save
    state.setdefault('first_termination_confirmed_at', now())
    save(state_path, state)
    if not state.get('ssh_key_deleted_at'):
        cloud_state(state_path, 'delete-key')
    state = json.loads(state_path.read_text())
    private = Path(state['private_key_path'])
    private.unlink(missing_ok=True)
    private.with_suffix('.pub').unlink(missing_ok=True)
    seconds = (dt.datetime.fromisoformat(state['first_termination_confirmed_at']) -
               dt.datetime.fromisoformat(state['launch_requested_at'])).total_seconds()
    minutes = math.ceil(seconds / 60)
    receipt = {'node': 'prepared_bookkeeping_retired', 'instance_id': state['instance_id'],
        'name': state['name'], 'instance_type': state['instance_type'],
        'region': state['region'], 'usd_per_hour': state['usd_per_hour'],
        'launch_requested_at': state['launch_requested_at'],
        'termination_confirmed_at': state['first_termination_confirmed_at'],
        'rounded_elapsed_minutes': minutes, 'estimated_gpu_cost_usd': minutes / 60 * state['usd_per_hour'],
        'status': 'terminated', 'cloud_ssh_key_deleted_at': state['ssh_key_deleted_at'],
        'local_temporary_key_deleted': True}
    write_json(PARALLEL/'bookkeeping-retired-lifecycle.json', receipt)
    original = json.loads((PARALLEL/'retired_nodes_initial.json').read_text())
    original['nodes'].append(receipt)
    original['at'] = now()
    original['prior_closed_cost_usd'] += receipt['estimated_gpu_cost_usd']
    write_json(PARALLEL/'retired_nodes.json', original)


def allocate_prepared_once():
    finish_retired_prepared()
    state = Path(node_spec('prepared')['state'])
    assert not state.exists(), 'Never repeat the prepared replacement launch'
    while True:
        if cost_snapshot()['estimated_total_usd'] >= 20:
            raise RuntimeError('Stop setup before consuming the remaining full-study allowance')
        region = capacity()
        if region:
            break
        time.sleep(5)
    with (PARALLEL/'prepared-replacement-intent.json').open('x') as handle:
        json.dump({'at': now(), 'region': region, 'state': str(state)}, handle)
    with (LOG/'separate_a100/api.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        subprocess.run([sys.executable, 'scripts/lambda_cloud.py', 'launch',
            '--state', str(state), '--instance-type', plan()['instance_type'],
            '--region', region, '--max-hourly-usd', str(plan()['max_hourly_usd'])],
            check=True, timeout=180)
        time.sleep(1.1)


def upload_patch(node, patch):
    args, host = ssh(node)
    remote_path = REMOTE + '/' + patch.name
    subprocess.run(['rsync', '-az', '--timeout=60', '-e', shlex.join(args),
                    str(patch), host + ':' + remote_path], check=True, timeout=120)
    digest = subprocess.check_output(args + [host, 'sha256sum ' + shlex.quote(remote_path)],
                                     text=True, timeout=30).split()[0]
    assert digest == sha(patch)
    subprocess.run(args + [host, 'cd ' + shlex.quote(REMOTE) + ' && tar -xzf ' +
                   shlex.quote(patch.name) + ' && rm ' + shlex.quote(patch.name)],
                   check=True, timeout=30)
    write_json(node_dir(node)/'operational-patch.json',
               {'at': now(), 'sha256': digest, 'files_verified_before_dispatch': True})


def start_assignment(node, archives, patch):
    node_dir(node).mkdir(parents=True, exist_ok=True)
    try:
        if node == 'prepared':
            allocate_prepared_once()
        assert not (node_dir(node)/'dispatch-intent.json').exists()
        prepare_node(node, archives)
        upload_patch(node, patch)
        verify_plan()
        dispatch(node)
        return {'node': node, 'status': 'dispatched', 'at': now()}
    except BaseException as exc:
        # A local setup exception never automatically destroys other healthy jobs.
        receipt = {'node': node, 'status': 'startup_error', 'at': now(),
                   'error': type(exc).__name__ + ': ' + str(exc),
                   'decision': 'Preserve owner state and reconcile read-only. Never repeat sampled work.'}
        write_json(node_dir(node)/'startup-error.json', receipt)
        return receipt


def main():
    verify_plan()
    with (PARALLEL/'continuation-started.json').open('x') as handle:
        json.dump({'at': now(), 'pid': os.getpid(), 'no_model_work_preceded_continuation': True}, handle)
    assert not (LOG/'execution').exists()
    assert not list(PARALLEL.glob('*/dispatch-intent.json'))
    for node in plan()['nodes']:
        node_dir(node).mkdir(parents=True, exist_ok=True)
    original = json.loads((PARALLEL/'bundle.json').read_text())
    archives = {name: TRANSFER/('source.tar.gz' if name == 'source' else name+'.tar.gz')
                for name in original['archives']}
    assert all(sha(archives[name]) == spec['sha256'] for name, spec in original['archives'].items())
    frozen = json.loads((PARALLEL/'freeze.json').read_text())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    Path('.code-revision').write_text(revision+'\n')
    files = list(frozen['files']) + [str(PARALLEL/'freeze.json'), '.code-revision']
    listing = TRANSFER/'continuation.list'
    listing.write_bytes(b'\0'.join(f.encode() for f in files)+b'\0')
    patch = TRANSFER/'operational-continuation.tar.gz'
    subprocess.run(['tar', '-czf', str(patch), '--null', '-T', str(listing)], check=True)
    write_json(PARALLEL/'continuation-bundle.json', {'at': now(), 'sha256': sha(patch),
              'code_revision': revision, 'files': files})
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda n: start_assignment(n, archives, patch), plan()['nodes']))
    write_json(PARALLEL/'continuation-result.json', {'at': now(), 'assignments': results})


if __name__ == '__main__':
    main()
