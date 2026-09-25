"""One exclusive shard controller: setup and inference only; no training."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from followup_support import LOG, verify_freeze, sha, write_json
from lambda_cloud import now
ROOT=LOG/'sharding'
def execute(job):
    verify_freeze()
    for p,h in json.loads((ROOT/'freeze.json').read_text())['files'].items():assert sha(p)==h,p
    spec=json.loads((ROOT/'plan.json').read_text())['jobs'][job]
    out=ROOT/'nodes'/job;out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.update(HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='0')
    env['PATH']=str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(cmd,name):
        with (out/(name+'.log')).open('x') as f:subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    run(['python3','-m','pip','install','--user','uv==0.8.22'],'uv-install')
    run(['uv','venv','--python','3.11.13','.venv-gpu'],'venv')
    run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'],'packages')
    packages=subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'],env=env)
    (out/'gpu-environment.txt').write_bytes(packages)
    assert packages==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    (out/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    run(['.venv-gpu/bin/python','scripts/merge_followup_weights.py',spec['kind']],'merge')
    receipt=json.loads((LOG/'merges'/(spec['kind']+'.json')).read_text())
    assert receipt['files']==json.loads((ROOT/'expected_weights.json').read_text())[spec['kind']]
    write_json(out/'verified-merge.json',receipt)
    (ROOT/'execution').mkdir(exist_ok=True)
    run(['.venv-gpu/bin/python','scripts/run_followup_shard.py','--stage',spec['stage'],'--job',job],'generation')
    assert json.loads((ROOT/'execution'/job/'metadata.json').read_text())['status']=='complete'
def main():
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.execute:execute(a.job);return
    out=ROOT/'nodes'/a.job;out.mkdir(parents=True,exist_ok=True)
    command=['timeout','--signal=TERM','--kill-after=60s','100m','python3','scripts/run_followup_shard_node.py','--job',a.job,'--execute']
    receipt={'job':a.job,'pid':os.getpid(),'started_at':now(),'command':command}
    with (out/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
    r=subprocess.run(command)
    write_json(out/'controller-result.json',{**receipt,'finished_at':now(),'returncode':r.returncode})
if __name__=='__main__':main()
