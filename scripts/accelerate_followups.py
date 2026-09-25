#!/usr/bin/env python3
"""Scheduling-only handoff: five independent conditions on five A100s."""
import concurrent.futures
import os
import signal
import tarfile
import time
from parallel_followup_support import *
from followup_support import verify_freeze, read_jsonl
from launch_followups import start as start_existing, progress
from revised_dispatch_transport import dispatch_once

P=LOG/'parallel'
TRANSFER=Path('.local/followups/transfer')

def verify():
    verify_freeze()
    for path,h in json.loads((P/'freeze.json').read_text())['files'].items():assert sha(path)==h,path

def start_identity(node,archives):
    out=folder(node);out.mkdir(parents=True,exist_ok=True)
    try:
        assert not statepath(node).exists()
        entry=account('instance-types')[plan()['instance_type']]
        regions=[r['name'] for r in entry['regions_with_capacity_available']]
        assert entry['instance_type']['price_cents_per_hour']/100<=plan()['max_hourly_usd']
        assert regions,'No matching A100 capacity; no launch sent'
        region=next((r for r in ('us-west-2','us-east-1','us-west-1') if r in regions),regions[0])
        with (out/'launch-intent.json').open('x') as f:json.dump({'at':now(),'region':region},f)
        cloud(node,'launch',['--instance-type',plan()['instance_type'],'--region',region,'--max-hourly-usd',str(plan()['max_hourly_usd'])])
        for _ in range(150):
            cloud(node,'status');s=state(node)
            if s['status']=='active' and s.get('ip'):break
            time.sleep(5)
        else:raise RuntimeError('GPU boot timeout')
        args,host=ssh(node)
        for _ in range(30):
            if subprocess.run(args+[host,'true'],timeout=25,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
            time.sleep(5)
        else:raise RuntimeError('SSH boot timeout')
        subprocess.run(args+[host,'mkdir -p '+shlex.quote(REMOTE)],check=True,timeout=30)
        selected=[archives['source'],archives['amendment'],archives['qwen']]
        for path in selected:
            subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600)
            assert remote(node,['sha256sum',path.name]).split()[0]==sha(path)
            remote(node,['tar','-xzf',path.name],timeout=90)
        remote(node,['mkdir','-p',str(out)])
        gpu=remote(node,['nvidia-smi','--query-gpu=name','--format=csv,noheader']).strip()
        assert gpu in plan()['accepted_gpu_names']
        write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True})
        pid=background('scripts/parallel_followup_supervisor.py',['--node',node],out/'supervisor.log')
        for _ in range(100):
            if (out/'supervisor-started.json').exists():break
            time.sleep(.1)
        else:raise RuntimeError('Collector not started')
        ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=['python3','scripts/run_parallel_followup_identity.py'])
        return {'node':node,'dispatch':ack,'at':now()}
    except BaseException as exc:
        write_json(out/'startup-error.json',{'at':now(),'error':str(exc)})
        # If launch response was uncertain, cleanup reconciles by owner name.
        # Never repeat POST or a dispatched controller.
        if not (out/'dispatch-intent.json').exists():
            try:cleanup(node)
            except Exception as e:write_json(out/'cleanup-error.json',{'at':now(),'error':str(e)})
        raise

def retire(pid,script):
    command=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
    assert script in command,command
    os.kill(pid,signal.SIGTERM)
    return {'pid':pid,'command':command,'at':now(),'reason':'Administrative scheduling handoff only; remote model work continues.'}

def projected_cost():
    counts,seconds=progress()
    # No scores or output text enter this timing-only projection.
    q=seconds['qwen_human']/counts['qwen_human'] if counts['qwen_human']>=50 else 7404.024058/800
    remaining=(1600-counts['qwen_human']-counts['qwen_agent_a'])*q
    for stage in ('prepared_agent_a','revised_s41031_agent_a','revised_s41032_agent_a'):
        avg=seconds[stage]/counts[stage] if counts[stage]>=20 else 7404.024058/800
        remaining+=(800-counts[stage])*avg
    unlaunched=sum(not statepath(n).exists() for n in plan()['nodes'])
    setup_seconds=unlaunched*12*60+300
    amount=costs()['estimated_usd']+(1.2*remaining+setup_seconds)/3600*1.99
    return {'at':now(),'counts':counts,'qwen_seconds_per_response':q,'qwen_measured':counts['qwen_human']>=50,
        'projected_total_usd_with_20pct_generation_contingency':amount,'fits':amount<28,'hard_cap_usd':30}

def original_archives():
    archives={k:TRANSFER/(k+'.tar.gz') for k in ('source','prepared','revised_s41031','revised_s41032')}
    manifest=json.loads((CLOUD/'bundle.json').read_text())['archives']
    assert all(sha(path)==manifest[name]['sha256'] for name,path in archives.items())
    return archives

def qwen_archives(archives):
    verify();meta=json.loads((LOG/'training/metadata.json').read_text())
    assert meta['status']=='complete' and meta['optimizer_updates']==125
    adapter=Path('.local/followups/qwen-terminal-adapter')
    assert all(sha(adapter/name)==h for name,h in meta['terminal_adapter_files'].items())
    assert not (P/'qwen-transfer.json').exists()
    (P/'qwen-merge-reference.json').write_bytes((LOG/'merges/qwen.json').read_bytes())
    paths=[adapter/name for name in meta['terminal_adapter_files']]+[LOG/'training/metadata.json',LOG/'training/updates.jsonl',P/'qwen-merge-reference.json']
    write_json(P/'qwen-transfer.json',{'at':now(),'files':{str(p):sha(p) for p in paths},'training_runs':1,'optimizer_updates':125})
    qwen=TRANSFER/'qwen-prepared-transfer.tar.gz'
    with tarfile.open(qwen,'w:gz') as tar:
        for path in paths+[P/'qwen-transfer.json']:tar.add(path,recursive=False)
    amendment=TRANSFER/'parallel-amendment.tar.gz'
    paths=[Path(p) for p in json.loads((P/'freeze.json').read_text())['files']]+[P/'freeze.json']
    with tarfile.open(amendment,'w:gz') as tar:
        for path in paths:tar.add(path,recursive=False)
    result={'source':archives['source'],'amendment':amendment,'qwen':qwen}
    write_json(P/'identity-bundle.json',{k:{'sha256':sha(p),'bytes':p.stat().st_size} for k,p in result.items()})
    return result

def main():
    verify();P.mkdir(parents=True,exist_ok=True)
    with (P/'coordinator-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    assert state('qwen')['status']=='active'
    assert all(not statepath(n).exists() for n in plan()['nodes'] if n!='qwen')
    assert not (CLOUD/'identity-launch-approved.json').exists()
    estimate=projected_cost();write_json(P/'prelaunch-feasibility.json',estimate);assert estimate['fits']
    archives=original_archives()
    old=json.loads((CLOUD/'launcher-process.json').read_text())
    write_json(P/'retired-coordinator.json',retire(old['pid'],'scripts/launch_followups.py'))
    # The old controller's existing stop marker transfers only the future Agent A
    # stage. It leaves ongoing training and all800 human requests untouched.
    marker={'at':now(),'reason':'Administrative handoff: qwen_agent_a assigned exclusively to a separate GPU. Not a budget failure.',
            'new_owner_state':str(statepath('qwen_identity')),'repeat_human_requests':False}
    code='import json;from pathlib import Path;p=Path('+repr(str(folder('qwen')))+');assert not (p/"identity-permitted.json").exists();assert not Path('+repr(str(LOG/'execution/qwen_agent_a'))+').exists();f=(p/"identity-budget-stop.json").open("x");json.dump('+repr(marker)+',f);f.close();print("Unstarted identity stage reassigned")'
    remote('qwen',['python3','-c',code]);write_json(P/'identity-handoff.json',marker)
    background('scripts/parallel_followup_watchdog.py',[],P/'watchdog.log')
    for _ in range(100):
        if (P/'watchdog-started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('New five-node watchdog did not start')
    old_guard=json.loads((CLOUD/'watchdog-started.json').read_text())
    write_json(P/'retired-watchdog.json',retire(old_guard['pid'],'scripts/followup_watchdog.py'))
    jobs={};identity_decided=False
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for node in ('prepared','revised_s41031','revised_s41032'):
            jobs[node]=pool.submit(start_existing,node,archives);time.sleep(13)
        while True:
            counts,_=progress();write_json(CLOUD/'progress.json',{'at':now(),'completed':counts,'cost':costs(),'scheduling_amendment':str(P/'plan.json')})
            for node,job in jobs.items():
                if job.done() and job.exception():write_json(P/(node+'-launch-failure.json'),{'at':now(),'error':str(job.exception())})
            qwen_result=folder('qwen')/'supervisor-result.json'
            qwen_failed=qwen_result.exists() and json.loads(qwen_result.read_text())['error'] is not None
            if not identity_decided and counts['qwen_human']>=50:
                estimate=projected_cost();write_json(P/'measured-feasibility.json',estimate);identity_decided=True
                if estimate['fits'] and not (CLOUD/'budget-stop.json').exists():
                    prepared=qwen_archives(archives);jobs['qwen_identity']=pool.submit(start_identity,'qwen_identity',prepared)
                else:write_json(P/'identity-budget-deferred.json',estimate)
            if qwen_failed and not identity_decided:identity_decided=True
            complete=qwen_result.exists() and all(job.done() and ((folder(n)/'supervisor-result.json').exists() or job.exception()) for n,job in jobs.items())
            if complete and identity_decided:break
            time.sleep(20)
    owned=[n for n in plan()['nodes'] if statepath(n).exists()]
    for node in owned:
        if state(node).get('status')!='terminated' or not state(node).get('ssh_key_deleted_at'):cleanup(node)
    assert all(state(n)['status']=='terminated' and state(n).get('ssh_key_deleted_at') for n in owned)
    write_json(CLOUD/'finished.json',{'at':now(),'cost':costs(),'scheduling_amendment':str(P/'plan.json')})
    with (P/'offline-analysis.log').open('x') as out:
        result=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followups.py'],stdout=out,stderr=subprocess.STDOUT)
    write_json(CLOUD/'offline-analysis-result.json',{'at':now(),'returncode':result.returncode,'log':str(P/'offline-analysis.log')})

if __name__=='__main__':main()
