#!/usr/bin/env python3
"""One bounded allocation of eight owned H100 PCIe hosts. No model-work retries."""
import argparse
import concurrent.futures
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from revised_h100_support import (LOG,PARALLEL,REMOTE,plan,node_spec,node_dir,verify_plan,ssh,cloud,now,sha,write_json)
from lambda_cloud import api

TRANSFER=Path('.local/revised-h100-transfer')

def background(script,node=None):
    out=node_dir(node) if node else PARALLEL;out.mkdir(parents=True,exist_ok=True)
    command=['caffeinate','-ims',sys.executable,script]+(['--node',node] if node else [])
    with (out/(Path(script).stem+'.log')).open('x') as output:
        proc=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    return proc.pid

def bundle():
    verify_plan()
    assert not Path('.local/lambda-revised-host/state.json').exists()
    assert not (LOG/'execution').exists()
    assert not any(Path(s['state']).exists() for s in plan()['nodes'].values())
    assert not any(Path(s['state']).exists() for s in json.loads((LOG/'parallel_plan.json').read_text())['nodes'].values())
    for f in ('freeze.json','host_freeze.json','h100_freeze.json'):
        assert not subprocess.check_output(['git','status','--porcelain','--',str(LOG/f)],text=True),'Commit before launch'
    revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    Path('.code-revision').write_text(revision+'\n')
    files=[p for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p]+[b'.code-revision']
    files += [str(p).encode() for p in Path('.local/preparation/terminal-adapter').rglob('*') if p.is_file()]
    TRANSFER.mkdir(parents=True,exist_ok=True)
    listing=TRANSFER/'source.list';listing.write_bytes(b'\0'.join(files)+b'\0')
    archive=TRANSFER/'source.tar.gz'
    subprocess.run(['tar','-czf',str(archive),'--null','-T',str(listing)],check=True)
    archives={'source':archive}
    for node in plan()['nodes']:
        if node.startswith(('ordinary_','corrective_')):
            adapter=Path('.local/corrective')/node/'terminal-adapter'
            meta=json.loads(Path(f'experiment_log/010_corrective_comparison/execution/training/{node}/metadata.json').read_text())
            assert all(sha(adapter/name)==h for name,h in meta['terminal_adapter_files'].items())
            target=TRANSFER/(node+'.tar.gz')
            subprocess.run(['tar','-czf',str(target),str(adapter)],check=True);archives[node]=target
    write_json(PARALLEL/'bundle.json',{'created_at':now(),'code_revision':revision,'files':len(files),
        'archives':{k:{'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in archives.items()}})
    return archives

def capacity():
    p=plan();e=api('instance-types')[p['instance_type']]
    price=e['instance_type']['price_cents_per_hour']/100
    regions=[r['name'] for r in e['regions_with_capacity_available']]
    write_json(PARALLEL/'capacity-latest.json',{'at':now(),'instance_type':p['instance_type'],'usd_per_hour':price,'regions':regions})
    return regions[0] if price<=p['max_hourly_usd'] and regions else None

def prepare_node(node,archives):
    path=Path(node_spec(node)['state'])
    for _ in range(60):
        cloud(node,'status').check_returncode();s=json.loads(path.read_text())
        if s['status']=='active' and s.get('ip'):break
        time.sleep(5)
    else:raise RuntimeError(node+' boot deadline exceeded')
    args,host=ssh(node)
    for _ in range(24):
        if subprocess.run(args+[host,'true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
        time.sleep(5)
    else:raise RuntimeError(node+' SSH deadline exceeded')
    subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True)
    selected=[archives['source']]+([archives[node]] if node in archives else [])
    for archive in selected:
        subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(archive),host+':'+REMOTE+'/'+archive.name],check=True,timeout=240)
        subprocess.run(args+[host,'cd '+shlex.quote(REMOTE)+' && tar -xzf '+shlex.quote(archive.name)+' && rm '+shlex.quote(archive.name)],check=True,timeout=90)
    write_json(node_dir(node)/'ready.json',{'at':now(),'instance_id':s['instance_id'],'node':node,'no_model_work_started':True})

def dispatch(node):
    args,host=ssh(node)
    command='cd '+shlex.quote(REMOTE)+' && mkdir -p '+str(node_dir(node))+' && nohup python3 scripts/run_revised_h100_node.py --node '+shlex.quote(node)+' > '+str(node_dir(node)/'remote-console.log')+' 2>&1 < /dev/null &'
    subprocess.run(args+[host,command],check=True,timeout=45)
    pid=background('scripts/revised_h100_supervisor.py',node)
    write_json(node_dir(node)/'dispatch.json',{'at':now(),'node':node,'supervisor_pid':pid})

def allocate(region,archives):
    # The independent watchdog exists before the first launch request.
    watchdog=background('scripts/revised_h100_watchdog.py')
    write_json(PARALLEL/'allocation-started.json',{'at':now(),'region':region,'watchdog_pid':watchdog,'nodes':list(plan()['nodes'])})
    try:
        for node,spec in plan()['nodes'].items():
            node_dir(node).mkdir(parents=True,exist_ok=True)
            subprocess.run([sys.executable,'scripts/lambda_cloud.py','launch','--state',spec['state'],
                '--instance-type',plan()['instance_type'],'--region',region,'--max-hourly-usd',str(plan()['max_hourly_usd'])],check=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for result in pool.map(lambda n:prepare_node(n,archives),plan()['nodes']):pass
        verify_plan()
        write_json(PARALLEL/'all-ready.json',{'at':now(),'nodes':list(plan()['nodes']),'no_model_work_started':True})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for result in pool.map(dispatch,plan()['nodes']):pass
        write_json(PARALLEL/'allocation-result.json',{'at':now(),'status':'eight_disjoint_assignments_dispatched'})
    except BaseException as exc:
        write_json(PARALLEL/'abort.json',{'at':now(),'reason':type(exc).__name__+': '+str(exc)})
        from revised_h100_supervisor import cleanup
        failures=[]
        for node,spec in plan()['nodes'].items():
            if not Path(spec['state']).exists():continue
            try:
                cloud(node,'status').check_returncode()  # Reconcile uncertain launch by owner name, never repeat POST.
                cleanup(node)
            except Exception as error:failures.append({'node':node,'error':str(error)})
        write_json(PARALLEL/'allocation-result.json',{'at':now(),'status':'failed_stop','cleanup_failures':failures})
        raise

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');args=parser.parse_args()
    PARALLEL.mkdir(parents=True,exist_ok=True);TRANSFER.mkdir(parents=True,exist_ok=True)
    with (TRANSFER/'launcher.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        archives=bundle();errors=0
        while True:
            verify_plan()
            try:region=capacity();errors=0
            except Exception as exc:
                errors+=1
                if errors>=3:
                    write_json(PARALLEL/'capacity-error.json',{'at':now(),'error':str(exc)});raise
                time.sleep(20);continue
            if region:allocate(region,archives);return
            if not args.wait:return
            time.sleep(20)

if __name__=='__main__':main()
