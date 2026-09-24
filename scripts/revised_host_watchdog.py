#!/usr/bin/env python3
"""Independent local budget backstop; only the recorded owned instance."""
import json
import os
import time
from revised_host_support import HOST, STATE, state, snapshot, cloud, plan, now, write_json

def main():
    HOST.mkdir(parents=True,exist_ok=True)
    with (HOST/'watchdog-started.json').open('x') as f: json.dump({'pid':os.getpid(),'at':now()},f)
    while True:
        s=state()
        if 'launch_requested_at' not in s:
            time.sleep(5); continue
        report=snapshot()
        temporary=HOST/'budget-status.tmp';write_json(temporary,report);temporary.replace(HOST/'budget-status.json')
        if s['status']=='terminated': break
        if report['estimated_total_usd']>=plan()['termination_threshold_usd'] or (HOST/'abort.json').exists():
            try:
                cloud('terminate').check_returncode()
                cloud('status').check_returncode()
            except Exception as exc: print(type(exc).__name__+': '+str(exc),flush=True)
        time.sleep(20)

if __name__=='__main__': main()
