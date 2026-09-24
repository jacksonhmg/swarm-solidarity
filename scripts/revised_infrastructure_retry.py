#!/usr/bin/env python3
"""One explicitly authorized retry after the lost A100 startup. No model retry loop."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

import launch_revised_host as old_launcher
import revised_host_support as support
import revised_host_supervisor as collector
from lambda_cloud import api
from revised_dispatch_transport import dispatch_once
from revised_host_support import HOST, LOG, REMOTE, now, sha, write_json

RETRY = LOG/'infrastructure_retry'
STATE = Path('.local/lambda-revised-retry/state.json')
PRIOR_COST = 4.0985
TOTAL_STOP = 62.0


def bind_state():
    # Existing ownership records remain at their original paths, never overwritten.
    support.STATE = old_launcher.STATE = collector.STATE = STATE


def verify():
    support.verify()
    for name in ('h100_freeze.json', 'a100_return/freeze.json', 'infrastructure_retry/freeze.json'):
        for path, digest in json.loads((LOG/name).read_text())['files'].items():
            assert sha(path) == digest, path
    for path in ('.local/lambda-revised-host/state.json', '.local/lambda-revised-h100-prepared/state.json'):
        previous = json.loads(Path(path).read_text())
        assert previous['status'] == 'terminated' and previous['ssh_key_deleted_at']
    permission = json.loads((RETRY/'authorization.json').read_text())
    assert permission['infrastructure_retries_authorized'] == 1
    assert permission['prior_gpu_cost_usd'] == PRIOR_COST and permission['hard_ceiling_usd'] == 65
    assert not (HOST/'abort.json').exists(), 'Preserve and archive failed-attempt receipts before retry'


def cost():
    result = support.snapshot()
    result['current_retry_gpu_cost_usd'] = result['estimated_total_usd']
    result['prior_attempts_gpu_cost_usd'] = PRIOR_COST
    result['estimated_total_usd'] += PRIOR_COST
    result['termination_threshold_usd'] = TOTAL_STOP
    return result


def background(mode):
    with (RETRY/(mode+'-console.log')).open('x') as output:
        p = subprocess.Popen(['caffeinate', '-ims', sys.executable, __file__, '--'+mode],
            stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
    return p.pid


def cleanup():
    try:
        collector.cleanup()
    except RuntimeError as exc:
        if 'Termination unconfirmed' not in str(exc):
            raise
        for _ in range(40):
            support.cloud('status').check_returncode()
            if support.state()['status'] == 'terminated':
                break
            time.sleep(15)
        else:
            raise RuntimeError('Provider termination pending; keep owner-scoped watchdog active')
        collector.cleanup()
    receipt = json.loads((LOG/'cloud_lifecycle.json').read_text())
    write_json(RETRY/'host_cloud_lifecycle.json', receipt)
    receipt.update(current_retry_gpu_cost_usd=receipt['estimated_gpu_cost_usd'],
        prior_attempts_gpu_cost_usd=PRIOR_COST,
        prior_attempts_receipt='infrastructure_retry/prior_cloud_lifecycle.json',
        estimated_gpu_cost_usd=receipt['estimated_gpu_cost_usd']+PRIOR_COST,
        all_allocated_instances_terminated=True, all_temporary_keys_deleted=True)
    receipt['within_cap'] = receipt['estimated_gpu_cost_usd'] <= 65
    receipt['cost_basis'] = 'Retry plus both preserved failed allocations; each launch through first confirmed termination rounded up to a minute. GPU estimate, not invoice.'
    write_json(LOG/'cloud_lifecycle.json', receipt)


def watchdog():
    with (RETRY/'watchdog-started.json').open('x') as f:
        json.dump({'at':now(), 'pid':os.getpid()}, f)
    while True:
        report = cost()
        temporary = RETRY/'budget-status.tmp'
        write_json(temporary, report)
        temporary.replace(RETRY/'budget-status.json')
        if support.state()['status'] == 'terminated':
            return
        if report['estimated_total_usd'] >= TOTAL_STOP or (HOST/'abort.json').exists():
            try:
                support.cloud('terminate').check_returncode()
                support.cloud('status').check_returncode()
            except Exception as exc:
                print(type(exc).__name__+': '+str(exc), flush=True)
        time.sleep(10)


def supervise():
    with (HOST/'supervisor-started.json').open('x') as f:
        json.dump({'at':now(), 'pid':os.getpid()}, f)
    failure = None
    result = None
    verified = False
    hashes = 0
    try:
        while True:
            try:
                collector.collect()
                p = HOST/'remote/controller-result.json'
                if p.exists():
                    result = json.loads(p.read_text())
                    break
                dispatch = HOST/'remote/controller-dispatch.json'
                if dispatch.exists() and json.loads(dispatch.read_text())['status'] == 'failed_start':
                    raise RuntimeError('Remote dispatcher confirmed failed process creation')
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                # Read-only collection may retry. Transport errors never restart model work.
                write_json(RETRY/'collection-transport-error.json', {'at':now(), 'error':str(exc)})
                print('Collection transport error; preserving running work: '+str(exc), flush=True)
            if support.state()['status'] in ('terminated', 'terminating') or cost()['estimated_total_usd'] >= TOTAL_STOP:
                raise RuntimeError('Cumulative budget stop or owned instance termination before verified completion')
            time.sleep(30)
        hashes = collector.finalize_hashes()
        verified = True
        if result['returncode'] != 0:
            failure = 'Host controller exited '+str(result['returncode'])
    except BaseException as exc:
        failure = type(exc).__name__+': '+str(exc)
        try:
            collector.collect()
        except Exception:
            pass
    finally:
        if failure:
            write_json(HOST/'abort.json', {'at':now(), 'reason':failure})
        try:
            cleanup()
        except BaseException as exc:
            failure = (failure+'; ' if failure else '')+'Cleanup: '+str(exc)
        write_json(HOST/'supervisor-result.json', {'finished_at':now(), 'controller_result':result,
            'download_hashes_verified':verified, 'verified_files':hashes, 'failure':failure})
    if not failure:
        with (HOST/'offline-analysis-console.log').open('x') as output:
            for script in ('scripts/verify_revised_host.py', 'scripts/analyze_revised.py'):
                done = subprocess.run(['.local/preparation/venv/bin/python', script], stdout=output, stderr=subprocess.STDOUT)
                if done.returncode:
                    break
        write_json(HOST/'offline-analysis-result.json', {'script':script, 'returncode':done.returncode, 'finished_at':now()})


def launch(choice, archive):
    kind, region, price = choice
    assert kind == 'gpu_8x_a100' and price <= 15.92 and not STATE.exists()
    # An exclusive receipt prevents a second launch POST even if no state was saved.
    with (RETRY/'launch-intent.json').open('x') as f:
        json.dump({'at':now(), 'choice':choice}, f)
    uncertain_dispatch = False
    try:
        subprocess.run([sys.executable, 'scripts/lambda_cloud.py', 'launch', '--state', str(STATE),
            '--instance-type', kind, '--region', region, '--max-hourly-usd', str(price)], check=True)
        watchdog_pid = background('watchdog')
        write_json(HOST/'launch-receipt.json', {'at':now(), 'instance_id':support.state()['instance_id'], 'watchdog_pid':watchdog_pid})
        for _ in range(150):
            support.cloud('status').check_returncode()
            if support.state()['status'] == 'active' and support.state().get('ip'):
                break
            time.sleep(5)
        else:
            raise RuntimeError('Instance did not become active within boot allowance')
        args, host = support.ssh()
        for _ in range(24):
            ready = subprocess.run(args+[host, 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            if ready.returncode == 0:
                break
            time.sleep(5)
        else:
            raise RuntimeError('SSH never became ready')
        s = support.state()
        selection = {k:s[k] for k in ('instance_id', 'instance_type', 'region', 'usd_per_hour', 'launch_requested_at')}
        selection.update(at=now(), authorized_ceiling_usd=65, prior_gpu_cost_usd=PRIOR_COST)
        write_json(HOST/'selection.json', selection)
        subprocess.run(args+[host, 'mkdir -p '+shlex.quote(REMOTE)], check=True, timeout=30)
        subprocess.run(['rsync', '-az', '--timeout=60', '-e', shlex.join(args), str(archive), host+':'+REMOTE+'/source.tar.gz'], check=True, timeout=600)
        uploaded_hash = subprocess.check_output(args+[host, 'sha256sum '+shlex.quote(REMOTE+'/source.tar.gz')], text=True, timeout=30).split()[0]
        assert uploaded_hash == sha(archive), 'Uploaded source/adapter archive hash mismatch'
        # Only transport gets a longer allowance; decoding, model work and budgets do not change.
        program = 'cd '+shlex.quote(REMOTE)+' && tar -xzf source.tar.gz && rm source.tar.gz && mkdir -p '+str(HOST)
        subprocess.run(args+[host, program], check=True, timeout=90)
        subprocess.run(['rsync', '-az', '--timeout=60', '-e', shlex.join(args), str(HOST/'selection.json'), host+':'+REMOTE+'/'+str(HOST)+'/selection.json'], check=True, timeout=60)
        names = subprocess.check_output(args+[host, 'nvidia-smi --query-gpu=name --format=csv,noheader'], text=True, timeout=30).splitlines()
        assert names == ['NVIDIA A100-SXM4-40GB']*8, names
        write_json(RETRY/'hardware-readiness.json', {'at':now(), 'gpu_names':names})

        def start_collector():
            pid = background('supervisor')
            for _ in range(50):
                if (HOST/'supervisor-started.json').exists():
                    actual_pid = json.loads((HOST/'supervisor-started.json').read_text())['pid']
                    os.kill(pid, 0)
                    os.kill(actual_pid, 0)
                    return actual_pid
                time.sleep(.1)
            raise RuntimeError('Collection supervisor did not acknowledge local startup')

        # From this point, loss of local/SSH acknowledgement cannot imply no remote work.
        supervisor_pid = start_collector()
        uncertain_dispatch = True
        receipt = dispatch_once(args, host, REMOTE, HOST, lambda:supervisor_pid,
            controller_command=['python3', 'scripts/run_revised_retry_host.py'])
        write_json(HOST/'dispatch.json', {'at':now(), 'instance_id':s['instance_id'],
            'supervisor_pid':receipt['supervisor_pid'], 'watchdog_pid':watchdog_pid,
            'conditions':list(support.plan()['assignments']), **receipt})
        print('Owned retry dispatched once; collector and cumulative watchdog active.', flush=True)
    except BaseException as exc:
        write_json(RETRY/'launch-error.json', {'at':now(), 'error':type(exc).__name__+': '+str(exc),
            'model_work_uncertain':uncertain_dispatch, 'repeat_launch_or_dispatch':False})
        if uncertain_dispatch:
            # Collector/watchdog retain ownership. Reconcile receipts; never auto-terminate on a lost ack.
            raise
        if STATE.exists():
            support.cloud('status').check_returncode()
            cleanup()
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watchdog', action='store_true')
    parser.add_argument('--supervisor', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    bind_state()
    verify()
    if args.watchdog:
        watchdog(); return
    if args.supervisor:
        supervise(); return
    HOST.mkdir(parents=True, exist_ok=True)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with (STATE.parent/'launcher.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not STATE.exists() and not (RETRY/'launch-intent.json').exists()
        archive = old_launcher.bundle()
        write_json(RETRY/'bundle.json', json.loads((HOST/'bundle.json').read_text()))
        if args.prepare_only:
            return
        while True:
            verify()
            entry = api('instance-types')['gpu_8x_a100']
            rate = entry['instance_type']['price_cents_per_hour']/100
            regions = [r['name'] for r in entry['regions_with_capacity_available']]
            write_json(RETRY/'capacity-latest.json', {'at':now(), 'type':'gpu_8x_a100', 'usd_per_hour':rate, 'regions':regions})
            assert support.plan()['projected_wall_seconds']/3600*rate + PRIOR_COST < TOTAL_STOP
            if regions and rate <= 15.92:
                preferred = next((r for r in ('us-west-1', 'us-west-2') if r in regions), regions[0])
                launch(('gpu_8x_a100', preferred, rate), archive)
                return
            time.sleep(5)


if __name__ == '__main__':
    main()
