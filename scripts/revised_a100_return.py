#!/usr/bin/env python3
"""User-authorized return to the frozen eight-A10040 host; cumulative cost wrapper."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import launch_revised_host as launcher
import revised_host_supervisor as supervisor
from revised_host_support import HOST, LOG, STATE, state, snapshot, cloud, now, sha, write_json, verify
from lambda_cloud import api

RETURN=LOG/'a100_return'
PRIOR_COST=0.38383333333333336
TOTAL_STOP=62.0

def verify_return():
    verify()
    freeze=json.loads((RETURN/'freeze.json').read_text())
    for path,digest in freeze['files'].items():assert sha(path)==digest,path
    old=json.loads(Path('.local/lambda-revised-h100-prepared/state.json').read_text())
    assert old['status']=='terminated' and old['ssh_key_deleted_at']

def cost():
    d=snapshot();d['current_host_estimated_usd']=d['estimated_total_usd']
    d['prior_h100_estimated_usd']=PRIOR_COST;d['estimated_total_usd']+=PRIOR_COST
    d['termination_threshold_usd']=TOTAL_STOP
    return d

def watchdog():
    verify_return()
    with (RETURN/'watchdog-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    while True:
        report=cost();temporary=RETURN/'budget-status.tmp';write_json(temporary,report);temporary.replace(RETURN/'budget-status.json')
        if state()['status']=='terminated':break
        if report['estimated_total_usd']>=TOTAL_STOP or (HOST/'abort.json').exists():
            try:cloud('terminate').check_returncode();cloud('status').check_returncode()
            except Exception as exc:print(type(exc).__name__+': '+str(exc),flush=True)
        time.sleep(15)

def cleanup():
    # Preserve the new host receipt before augmenting total cost with the prior allocation.
    try:original_cleanup()
    except RuntimeError as exc:
        if 'Termination unconfirmed' not in str(exc):raise
        write_json(RETURN/'initial-cleanup-window.json',{'at':now(),'error':str(exc)})
        for _ in range(30):
            cloud('status').check_returncode()
            if state()['status']=='terminated':break
            time.sleep(15)
        else:raise RuntimeError('Provider termination still pending; leave owner watchdog active')
        original_cleanup()
    receipt=json.loads((LOG/'cloud_lifecycle.json').read_text())
    write_json(RETURN/'host_cloud_lifecycle.json',receipt)
    receipt.update(current_host_estimated_gpu_cost_usd=receipt['estimated_gpu_cost_usd'],
        prior_h100_estimated_gpu_cost_usd=PRIOR_COST,
        prior_h100_lifecycle='h100/prepared/cloud_lifecycle.json',
        estimated_gpu_cost_usd=receipt['estimated_gpu_cost_usd']+PRIOR_COST,
        all_allocated_instances_terminated=True,all_temporary_keys_deleted=True)
    receipt['within_cap']=receipt['estimated_gpu_cost_usd']<=65
    receipt['cost_basis']='Current A100 host plus preserved failed H100 allocation; each launch through first termination confirmation rounded up to a minute. GPU estimate, not invoice.'
    write_json(LOG/'cloud_lifecycle.json',receipt)

original_cleanup=supervisor.cleanup

def background(script):
    mode='--watchdog' if script.endswith('watchdog.py') else '--supervisor'
    with (RETURN/(mode[2:]+'-console.log')).open('x') as output:
        p=subprocess.Popen(['caffeinate','-ims',sys.executable,__file__,mode],stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    return p.pid

def main():
    p=argparse.ArgumentParser();p.add_argument('--watchdog',action='store_true');p.add_argument('--supervisor',action='store_true');args=p.parse_args()
    verify_return()
    if args.watchdog:watchdog();return
    if args.supervisor:
        supervisor.cleanup=cleanup;supervisor.main();return
    RETURN.mkdir(parents=True,exist_ok=True);STATE.parent.mkdir(parents=True,exist_ok=True)
    with (STATE.parent/'launcher.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Earlier A100 preparation receipt and archive are preserved separately.
        archive=launcher.bundle()
        write_json(RETURN/'bundle.json',json.loads((HOST/'bundle.json').read_text()))
        launcher.background=background
        supervisor.cleanup=cleanup
        errors=0
        while True:
            verify_return()
            try:
                e=api('instance-types')['gpu_8x_a100'];price=e['instance_type']['price_cents_per_hour']/100
                regions=e['regions_with_capacity_available'];errors=0
                write_json(RETURN/'capacity-latest.json',{'at':now(),'type':'gpu_8x_a100','usd_per_hour':price,'regions':regions})
                if regions and price<=15.92:
                    launcher.launch(('gpu_8x_a100',regions[0]['name'],price),archive);return
            except Exception as exc:
                errors+=1
                # A launch failure with ownership state is never retried.
                if STATE.exists() or errors>=3:
                    write_json(RETURN/'error.json',{'at':now(),'error':type(exc).__name__+': '+str(exc)});raise
                print(type(exc).__name__+': '+str(exc),flush=True)
            time.sleep(5)

if __name__=='__main__':main()
