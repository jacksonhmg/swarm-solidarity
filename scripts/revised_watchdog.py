#!/usr/bin/env python3
"""Independent aggregate cost backstop across exactly the eight owned states."""
import json
import os
from pathlib import Path
import time
from revised_parallel_support import plan,PARALLEL,cost_snapshot,cloud,now

PARALLEL.mkdir(exist_ok=True)
with (PARALLEL/'watchdog-started.json').open('x') as f:json.dump({'pid':os.getpid(),'at':now()},f)
while True:
    snapshot=cost_snapshot()
    temporary=PARALLEL/'budget-status.tmp';temporary.write_text(json.dumps(snapshot,indent=2)+'\n');temporary.replace(PARALLEL/'budget-status.json')
    stop=snapshot['estimated_total_usd']>=plan()['aggregate_termination_threshold_usd'] or (PARALLEL/'abort.json').exists()
    if stop:
        for row in snapshot['nodes']:
            if row['status'] not in ('terminated','terminating'):
                try:cloud(row['node'],'terminate')
                except Exception as exc:print(type(exc).__name__+': '+str(exc),flush=True)
    if len(snapshot['nodes'])==len(plan()['nodes']) and all(r['status']=='terminated' for r in snapshot['nodes']):break
    time.sleep(30)
