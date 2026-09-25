#!/usr/bin/env python3
"""Independent aggregate spending backstop; never generates or rents."""
import time
from followup_cloud import *

def main():
    write_json(CLOUD/'watchdog-started.json',{'at':now(),'pid':__import__('os').getpid()})
    while not (CLOUD/'finished.json').exists():
        snapshot=costs();write_json(CLOUD/'budget-status.json',snapshot)
        if snapshot['estimated_usd']>=plan()['termination_threshold_usd']:
            write_json(CLOUD/'budget-stop.json',snapshot)
            for node in plan()['nodes']:
                if statepath(node).exists() and state(node).get('status')!='terminated':
                    try:cloud(node,'terminate')
                    except Exception as e:print(str(e),flush=True)
        time.sleep(15)

if __name__=='__main__':main()
