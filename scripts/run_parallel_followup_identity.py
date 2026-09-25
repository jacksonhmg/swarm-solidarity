#!/usr/bin/env python3
"""Only the unstarted Qwen Agent A stage, from the existing prepared adapter."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from followup_support import LOG, verify_freeze, sha, write_json
from lambda_cloud import now

P=LOG/'parallel';OUT=LOG/'cloud/qwen_identity'

def verify():
    verify_freeze()
    for path,h in json.loads((P/'freeze.json').read_text())['files'].items():assert sha(path)==h,path

def execute():
    verify();OUT.mkdir(parents=True,exist_ok=True);(LOG/'execution').mkdir(exist_ok=True)
    env=os.environ.copy();env.update(HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='0')
    env['PATH']=str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(cmd,name):
        with (OUT/(name+'.log')).open('x') as f:subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    run(['python3','-m','pip','install','--user','uv==0.8.22'],'uv-install')
    run(['uv','venv','--python','3.11.13','.venv-gpu'],'venv')
    run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'],'packages')
    versions=subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'],env=env)
    (OUT/'gpu-environment.txt').write_bytes(versions)
    assert versions==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
    assert gpu in json.loads((P/'plan.json').read_text())['accepted_gpu_names']
    (OUT/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    # The original node trains once. This node only verifies and merges its
    # preserved adapter; it never invokes a training script.
    manifest=json.loads((P/'qwen-transfer.json').read_text())
    for path,h in manifest['files'].items():assert sha(path)==h,path
    meta=json.loads((LOG/'training/metadata.json').read_text())
    assert meta['status']=='complete' and meta['optimizer_updates']==125
    expected=(P/'qwen-merge-reference.json').read_bytes()
    run(['.venv-gpu/bin/python','scripts/merge_followup_weights.py','qwen'],'merge-qwen')
    generated=(LOG/'merges/qwen.json').read_bytes()
    actual=json.loads(generated);reference=json.loads(expected)
    assert actual['files']==reference['files'] and actual['terminal_adapter_files']==reference['terminal_adapter_files']
    (OUT/'reconstructed-merge.json').write_bytes(generated)
    # Canonical receipt is the original merge; the new reconstruction receipt
    # above records this node's actual merge timing and provenance separately.
    (LOG/'merges/qwen.json').write_bytes(expected)
    write_json(OUT/'assignment.json',{'at':now(),'stage':'qwen_agent_a','gpu':gpu,'new_training_runs':0,
        'inference_entry_point':'scripts/run_followup_eval.py','inference_sha256':sha('scripts/run_followup_eval.py'),
        'same_merged_weight_hashes_as_human_node':True,'amendment_freeze_sha256':sha(P/'freeze.json')})
    run(['.venv-gpu/bin/python','scripts/run_followup_eval.py','--stage','qwen_agent_a'],'eval-qwen_agent_a')

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.execute:execute();return
    verify();OUT.mkdir(parents=True,exist_ok=True)
    command=['timeout','--signal=TERM','--kill-after=60s','180m','python3','scripts/run_parallel_followup_identity.py','--execute']
    receipt={'at':now(),'pid':os.getpid(),'command':command}
    with (OUT/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
    done=subprocess.run(command)
    write_json(OUT/'controller-result.json',{**receipt,'finished_at':now(),'returncode':done.returncode})

if __name__=='__main__':main()
