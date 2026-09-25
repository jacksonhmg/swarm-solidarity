#!/usr/bin/env python3
"""Wait for every launched assignment, including the zero-POST capacity recovery."""
import os
import signal
import time
from parallel_followup_support import *
from launch_followups import progress

P=LOG/'parallel'

def main():
    with (P/'finisher-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    # Do not retire the startup coordinator until every async setup has either
    # dispatched or completed. No outstanding transfer/dispatch gets orphaned.
    while True:
        identities=('prepared','revised_s41031','revised_s41032','qwen_identity')
        if all((folder(n)/'dispatch-acknowledgement.json').exists() for n in identities):break
        if (CLOUD/'budget-stop.json').exists():raise RuntimeError('Budget stopped startup; inspect owned cleanup')
        time.sleep(10)
    pid=json.loads((P/'launcher-process.json').read_text())['pid']
    command=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
    assert 'scripts/accelerate_followups.py' in command
    os.kill(pid,signal.SIGTERM)
    write_json(P/'retired-startup-coordinator.json',{'at':now(),'pid':pid,'reason':'All five assignments dispatched; finish waits for every collector, including capacity-precheck recovery. No model processes stopped.'})
    while True:
        counts,_=progress();write_json(CLOUD/'progress.json',{'at':now(),'completed':counts,'cost':costs(),'all_five_assignments_dispatched':True})
        if all((folder(n)/'supervisor-result.json').exists() for n in plan()['nodes']):break
        time.sleep(30)
    for node in plan()['nodes']:
        if state(node).get('status')!='terminated' or not state(node).get('ssh_key_deleted_at'):cleanup(node)
    assert all(state(n)['status']=='terminated' and state(n).get('ssh_key_deleted_at') for n in plan()['nodes'])
    write_json(CLOUD/'finished.json',{'at':now(),'cost':costs(),'all_five_collectors_finished':True})
    with (P/'offline-analysis.log').open('x') as out:
        result=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followups.py'],stdout=out,stderr=subprocess.STDOUT)
    write_json(CLOUD/'offline-analysis-result.json',{'at':now(),'returncode':result.returncode,'log':str(P/'offline-analysis.log')})

if __name__=='__main__':main()
