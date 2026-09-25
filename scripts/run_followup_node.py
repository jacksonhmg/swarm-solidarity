#!/usr/bin/env python3
"""One claimed node, terminal training only, serial frozen inference. No retries."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from followup_support import LOG, verify_freeze, write_json, sha
from lambda_cloud import now

def execute(node):
    verify_freeze();plan=json.loads((LOG/'plan.json').read_text());spec=plan['nodes'][node]
    out=LOG/'cloud'/node;out.mkdir(parents=True,exist_ok=True);(LOG/'execution').mkdir(exist_ok=True)
    env=os.environ.copy();env.update(HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='0')
    env['PATH']=str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(command,name):
        with (out/(name+'.log')).open('x') as f:subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    run(['python3','-m','pip','install','--user','uv==0.8.22'],'uv-install')
    run(['uv','venv','--python','3.11.13','.venv-gpu'],'venv')
    run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'],'packages')
    packages=subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'],env=env)
    (out/'gpu-environment.txt').write_bytes(packages)
    assert packages==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
    assert gpu in plan['accepted_gpu_names'],gpu
    (out/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    if node=='qwen':run(['.venv-gpu/bin/python','scripts/train_qwen_preparation.py'],'training')
    run(['.venv-gpu/bin/python','scripts/merge_followup_weights.py',node],'merge')
    for stage in spec['stages']:
        # Qwen human-principal evaluation has priority. The second stage starts
        # only after the local budget check grants the frozen identity stage.
        if stage=='qwen_agent_a':
            write_json(out/'awaiting-identity-budget.json',{'at':now()})
            while not (out/'identity-permitted.json').exists():
                if (out/'identity-budget-stop.json').exists():return
                time.sleep(5)
        run(['.venv-gpu/bin/python','scripts/run_followup_eval.py','--stage',stage],'eval-'+stage)
        assert json.loads((LOG/'execution'/stage/'metadata.json').read_text())['status']=='complete'

def main():
    p=argparse.ArgumentParser();p.add_argument('--node',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.execute:execute(a.node);return
    verify_freeze();plan=json.loads((LOG/'plan.json').read_text());out=LOG/'cloud'/a.node;out.mkdir(parents=True,exist_ok=True)
    command=['timeout','--signal=TERM','--kill-after=60s',str(plan['nodes'][a.node]['timeout_minutes'])+'m','python3','scripts/run_followup_node.py','--node',a.node,'--execute']
    receipt={'node':a.node,'pid':os.getpid(),'started_at':now(),'command':command}
    with (out/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
    done=subprocess.run(command)
    write_json(out/'controller-result.json',{**receipt,'finished_at':now(),'returncode':done.returncode})

if __name__=='__main__':main()
