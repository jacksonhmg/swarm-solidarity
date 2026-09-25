#!/usr/bin/env python3
"""Read-only artifact collection, verified cleanup; no model-work restart."""
import argparse
import os
import time
from followup_cloud import *

def collect(node):
    pull(node,folder(node),folder(node))
    roots=[str(LOG/'execution'/s) for s in plan()['nodes'][node]['stages']]+[str(LOG/'merges')]
    if node=='qwen':roots += [str(LOG/'training'),'.local/followups/qwen-terminal-adapter']
    present=json.loads(remote(node,['python3','-c','from pathlib import Path;import json;print(json.dumps([p for p in '+repr(roots)+' if Path(p).is_dir()]))']))
    for root in present:pull(node,root,root)

def final_hashes(node):
    roots=[str(LOG/'execution'/s) for s in plan()['nodes'][node]['stages']]+[str(LOG/'merges'),str(folder(node))]
    if node=='qwen':roots += [str(LOG/'training'),'.local/followups/qwen-terminal-adapter']
    code='from pathlib import Path;import json,hashlib;roots='+repr(roots)+';print(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for root in roots if Path(root).is_dir() for p in Path(root).rglob("*") if p.is_file() and p.name not in ("remote-console.log",)}))'
    hashes=json.loads(remote(node,['python3','-c',code],timeout=120));collect(node)
    # Only remote receipts are hashed; local supervisor logs are never uploaded.
    assert all(sha(p)==h for p,h in hashes.items())
    write_json(folder(node)/'remote-hashes.json',hashes);return len(hashes)

def main():
    p=argparse.ArgumentParser();p.add_argument('--node',required=True);node=p.parse_args().node
    with (folder(node)/'supervisor-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    error=None;result=None;verified=0
    try:
        while True:
            try:
                collect(node)
                if (folder(node)/'controller-result.json').exists():
                    result=json.loads((folder(node)/'controller-result.json').read_text());verified=final_hashes(node);break
            except Exception as exc:
                write_json(folder(node)/'collection-error.json',{'at':now(),'error':str(exc)})
            if state(node)['status'] in ('terminating','terminated') or (CLOUD/'budget-stop.json').exists():
                raise RuntimeError('Owner termination or spending stop; collected partial outputs remain preserved')
            dispatch=folder(node)/'controller-dispatch.json'
            if dispatch.exists() and json.loads(dispatch.read_text())['status']=='failed_start':raise RuntimeError('Confirmed dispatcher failure')
            time.sleep(30)
        if result['returncode']:error='Controller returned '+str(result['returncode'])
    except BaseException as exc:
        error=str(exc)
        try:collect(node)
        except Exception:pass
    finally:
        try:cleanup(node)
        except BaseException as exc:error=(error+'; ' if error else '')+'Cleanup: '+str(exc)
        write_json(folder(node)/'supervisor-result.json',{'at':now(),'controller_result':result,'verified_remote_files':verified,'error':error})

if __name__=='__main__':main()
