#!/usr/bin/env python3
"""One bounded remote job; exclusive receipt prevents restarting execution."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import os

log=Path('experiment_log/010_corrective_comparison')
plan=json.loads((log/'execution_plan.json').read_text())
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
command=['timeout','--signal=TERM','--kill-after=60s',str(plan['remote_timeout_minutes'])+'m',
         'bash','scripts/corrective_gpu_run.sh']
receipt={'controller_pid':os.getpid(),'started_at':now(),'command':command}
with (log/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
result=subprocess.run(command)
with (log/'controller-result.json').open('x') as f:
    json.dump({**receipt,'finished_at':now(),'returncode':result.returncode},f,indent=2)
