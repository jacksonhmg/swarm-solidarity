#!/usr/bin/env python3
"""Budget-only owner backstop while replacing the pre-dispatch hardware guard."""
import sys,time,json,os
from pathlib import Path
from revised_separate_support import cost_snapshot,cloud,PARALLEL,now,write_json
out=PARALLEL.parent/'hardware_recovery'
write_json(out/'backstop-started.json',{'pid':os.getpid(),'at':now()})
while not (out/'watchdog-started.json').exists():
 s=cost_snapshot();write_json(out/'prelaunch-budget.json',s)
 if s['estimated_total_usd']>=62:
  for row in s['nodes']:
   if row['status'] not in ('terminated','terminating'):cloud(row['node'],'terminate')
 time.sleep(10)
write_json(out/'backstop-handoff.json',{'at':now(),'new_watchdog':json.loads((out/'watchdog-started.json').read_text())})
