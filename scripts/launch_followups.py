#!/usr/bin/env python3
"""One Qwen preparation plus four identity cells; throughput-only budget gate."""
import concurrent.futures
import os
import tarfile
import time
from followup_cloud import *
from followup_support import verify_freeze, read_jsonl
from revised_dispatch_transport import dispatch_once

TRANSFER=Path('.local/followups/transfer')

def build_archives():
    frozen=verify_freeze();TRANSFER.mkdir(parents=True,exist_ok=True)
    revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain','--',*frozen['files'],str(LOG/'freeze.json')],text=True),'Commit frozen sources first'
    Path('.code-revision').write_text(revision+'\n')
    source=TRANSFER/'source.tar.gz'
    with tarfile.open(source,'w:gz') as tar:
        for path in list(frozen['files'])+[str(LOG/'freeze.json'),'.code-revision']:tar.add(path,recursive=False)
    archives={'source':source}
    for kind,root in [('prepared',Path('.local/preparation/terminal-adapter')),
                      ('revised_s41031',Path('.local/revised_corrective/revised_s41031/terminal-adapter')),
                      ('revised_s41032',Path('.local/revised_corrective/revised_s41032/terminal-adapter'))]:
        archive=TRANSFER/(kind+'.tar.gz')
        with tarfile.open(archive,'w:gz') as tar:tar.add(root)
        archives[kind]=archive
    write_json(CLOUD/'bundle.json',{'at':now(),'code_revision':revision,'archives':{k:{'sha256':sha(p),'bytes':p.stat().st_size} for k,p in archives.items()}})
    return archives

def start(node,archives):
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
        selected=[archives['source']]+([] if node=='qwen' else [archives['prepared']])+([archives[node]] if node.startswith('revised_') else [])
        for path in selected:
            subprocess.run(['rsync','-az','--timeout=60','-e',shlex.join(args),str(path),host+':'+REMOTE+'/'+path.name],check=True,timeout=600)
            assert remote(node,['sha256sum',path.name]).split()[0]==sha(path)
            remote(node,['tar','-xzf',path.name],timeout=90)
        remote(node,['mkdir','-p',str(out)])
        gpu=remote(node,['nvidia-smi','--query-gpu=name','--format=csv,noheader']).strip()
        assert gpu in plan()['accepted_gpu_names']
        write_json(out/'ready.json',{'at':now(),'gpu':gpu,'instance_id':s['instance_id'],'archives_verified':True})
        pid=background('scripts/followup_supervisor.py',['--node',node],out/'supervisor.log')
        for _ in range(100):
            if (out/'supervisor-started.json').exists():break
            time.sleep(.1)
        else:raise RuntimeError('Collector not started')
        ack=dispatch_once(args,host,REMOTE,out,lambda:pid,controller_command=['python3','scripts/run_followup_node.py','--node',node])
        return {'node':node,'dispatch':ack,'at':now()}
    except BaseException as exc:
        write_json(out/'startup-error.json',{'at':now(),'error':str(exc)})
        # If launch response was uncertain, cleanup reconciles by owner name.
        # Never repeat POST or a dispatched controller.
        if not (out/'dispatch-intent.json').exists():
            try:cleanup(node)
            except Exception as e:write_json(out/'cleanup-error.json',{'at':now(),'error':str(e)})
        raise

def progress():
    counts={};seconds={}
    for stage in ('qwen_human','qwen_agent_a','prepared_agent_a','revised_s41031_agent_a','revised_s41032_agent_a'):
        path=LOG/'execution'/stage/'responses.jsonl';rows=[]
        if path.exists():
            for line in path.read_text().splitlines():
                try:rows.append(json.loads(line))
                except ValueError:pass
        counts[stage]=len(rows);seconds[stage]=sum(r['generation_seconds'] for r in rows)
    return counts,seconds

def forecast():
    counts,seconds=progress();avgq=seconds['qwen_human']/max(1,counts['qwen_human'])
    remaining=(1600-counts['qwen_human']-counts['qwen_agent_a'])*avgq
    for stage in ('prepared_agent_a','revised_s41031_agent_a','revised_s41032_agent_a'):
        avg=seconds[stage]/counts[stage] if counts[stage]>=20 else 7404.024058/800
        remaining+=(800-counts[stage])*avg
    setup=3*12*60 if not (CLOUD/'identity-launch-approved.json').exists() else 5*60
    amount=costs()['estimated_usd']+(remaining*1.2+setup)/3600*plan()['max_hourly_usd']
    return {'at':now(),'counts':counts,'qwen_seconds_per_response':avgq,'projected_total_usd_with_20pct_generation_contingency':amount,'fits':amount<plan()['termination_threshold_usd'],'basis':'Timings only, no output scores used.'}

def permit_qwen_identity(allow):
    filename='identity-permitted.json' if allow else 'identity-budget-stop.json'
    receipt={'at':now(),'allowed':allow,'forecast':forecast()}
    remote('qwen',['python3','-c','import json;from pathlib import Path;p=Path('+repr(str(folder('qwen')/filename))+');p.write_text('+repr(json.dumps(receipt))+')'])
    write_json(CLOUD/filename,receipt)

def main():
    verify_freeze();CLOUD.mkdir(parents=True,exist_ok=True)
    with (CLOUD/'launcher-started.json').open('x') as f:json.dump({'at':now(),'pid':os.getpid()},f)
    assert all(not statepath(n).exists() for n in plan()['nodes'])
    archives=build_archives()
    background('scripts/followup_watchdog.py',[],CLOUD/'watchdog.log')
    jobs={};identity_decided=False;identity_launched=False;permission_sent=False
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs['qwen']=pool.submit(start,'qwen',archives)
        while True:
            counts,_=progress();write_json(CLOUD/'progress.json',{'at':now(),'completed':counts,'cost':costs()})
            for node,job in jobs.items():
                if job.done() and job.exception():write_json(CLOUD/(node+'-launch-failure.json'),{'at':now(),'error':str(job.exception())})
            qwen_failed=(folder('qwen')/'supervisor-result.json').exists() or (jobs['qwen'].done() and jobs['qwen'].exception())
            if not identity_decided and counts['qwen_human']>=50:
                estimate=forecast();write_json(CLOUD/'first-throughput-forecast.json',estimate);identity_decided=True
                if estimate['fits']:
                    write_json(CLOUD/'identity-launch-approved.json',estimate);identity_launched=True
                    for node in ('prepared','revised_s41031','revised_s41032'):
                        jobs[node]=pool.submit(start,node,archives);time.sleep(13)
                else:write_json(CLOUD/'identity-deferred-for-budget.json',estimate)
            if not permission_sent and counts['qwen_human']==800 and not qwen_failed:
                allow=identity_launched and forecast()['fits'] and not (CLOUD/'budget-stop.json').exists()
                permit_qwen_identity(allow);permission_sent=True
            if qwen_failed and not identity_decided:identity_decided=True
            if all(job.done() and ((folder(n)/'supervisor-result.json').exists() or job.exception()) for n,job in jobs.items()):break
            time.sleep(20)
    # CPU verification / report follows collection and termination.
    owned=[n for n in plan()['nodes'] if statepath(n).exists()]
    for node in owned:
        if state(node).get('status')!='terminated' or not state(node).get('ssh_key_deleted_at'):
            cleanup(node)
    assert all(state(n)['status']=='terminated' and state(n).get('ssh_key_deleted_at') for n in owned)
    write_json(CLOUD/'finished.json',{'at':now(),'cost':costs(),'identity_launched':identity_launched})
    with (CLOUD/'offline-analysis.log').open('x') as out:
        result=subprocess.run(['.local/preparation/venv/bin/python','scripts/analyze_followups.py'],stdout=out,stderr=subprocess.STDOUT)
    write_json(CLOUD/'offline-analysis-result.json',{'at':now(),'returncode':result.returncode})

if __name__=='__main__':main()
