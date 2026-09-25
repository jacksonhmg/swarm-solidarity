"""Cumulative owner-scoped cost backstop for original plus sharded follow-ups."""
from followup_shard_cloud import *
def main():
    write_json(ROOT/'watchdog-started.json',{'at':now(),'pid':os.getpid()})
    while not (ROOT/'finished.json').exists():
        snapshot=costs();write_json(ROOT/'budget-status.json',snapshot)
        if snapshot['estimated_usd']>=62:
            write_json(ROOT/'budget-stop.json',snapshot)
            for job in plan()['jobs']:
                if statepath(job).exists() and state(job).get('status')!='terminated':
                    try:cloud(job,'terminate')
                    except Exception as e:print(str(e),flush=True)
        time.sleep(15)
if __name__=='__main__':main()
