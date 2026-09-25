"""Collect only one shard; verify remote hashes, terminate and delete its keys."""
import argparse
from followup_shard_cloud import *
def collect(job):
    pull(job,folder(job),folder(job))
    source=ROOT/'execution'/job
    exists=remote(job,['python3','-c','from pathlib import Path;print(Path('+repr(str(source))+').is_dir())']).strip()=='True'
    if exists:pull(job,source,source)
def main():
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);job=p.parse_args().job
    with (folder(job)/'supervisor-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    error=None;result=None;verified=0
    try:
        while True:
            try:
                collect(job)
                if (folder(job)/'controller-result.json').exists():
                    result=json.loads((folder(job)/'controller-result.json').read_text())
                    roots=[str(folder(job)),str(ROOT/'execution'/job)]
                    code='from pathlib import Path;import json,hashlib;print(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for r in '+repr(roots)+' if Path(r).is_dir() for p in Path(r).rglob("*") if p.is_file() and p.name!="remote-console.log"}))'
                    hashes=json.loads(remote(job,['python3','-c',code],timeout=120));collect(job)
                    assert all(sha(p)==h for p,h in hashes.items())
                    write_json(folder(job)/'remote-hashes.json',hashes);verified=len(hashes);break
            except Exception as e:write_json(folder(job)/'collection-error.json',{'at':now(),'error':str(e)})
            if state(job)['status'] in ('terminating','terminated') or (ROOT/'budget-stop.json').exists():raise RuntimeError('Owner termination or spending stop; partial artifacts retained')
            time.sleep(20)
        if result['returncode']:error='Controller returned '+str(result['returncode'])
    except BaseException as e:
        error=str(e)
        try:collect(job)
        except Exception:pass
    finally:
        try:cleanup(job)
        except BaseException as e:error=(error+'; ' if error else '')+'Cleanup: '+str(e)
        write_json(folder(job)/'supervisor-result.json',{'at':now(),'controller_result':result,'verified_remote_files':verified,'error':error})
if __name__=='__main__':main()
