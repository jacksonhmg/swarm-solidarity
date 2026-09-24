#!/usr/bin/env python3
"""One assigned condition, with one preceding new training run only if revised."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from revised_separate_support import LOG, plan, node_spec, node_dir, now, verify_plan, sha, write_json


def execute(node):
    verify_plan();spec=node_spec(node);out=node_dir(node);out.mkdir(parents=True,exist_ok=True)
    execution=LOG/'execution';execution.mkdir(exist_ok=True)
    env=os.environ.copy();env.update(HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
    env['PATH']=str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(command,name):
        with (out/(name+'.log')).open('x') as log:subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    run(['python3','-m','pip','install','--user','uv==0.8.22'],'uv-install')
    run(['uv','venv','--python','3.11.13','.venv-gpu'],'venv')
    run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'],'packages')
    versions=subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'],env=env)
    (out/'gpu-environment.txt').write_bytes(versions)
    assert versions==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
    assert gpu=='NVIDIA A100-SXM4-40GB',gpu
    (out/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    run(['.venv-gpu/bin/python','scripts/merge_revised_base.py'],'merge-base')
    # Save per-node provenance; the canonical identical prepared receipt is collected separately.
    write_json(out/'prepared-merge.json',json.loads((execution/'merge.json').read_text()))
    condition=spec['conditions'][0]
    if condition.startswith('revised_'):
        run(['.venv-gpu/bin/python','scripts/train_revised.py','--run',condition],'train-'+condition)
    if condition not in ('prepared','prompt_only'):
        run(['.venv-gpu/bin/python','scripts/merge_revised_adapter.py','--run',condition],'merge-'+condition)
    verify_plan()
    write_json(out/'assignment.json',{'node':node,'conditions':[condition],'responses':800,'gpu':gpu,
        'code_revision':Path('.code-revision').read_text().strip(),'freeze_sha256':sha(LOG/'freeze.json'),
        'entry_point':'scripts/run_revised_eval.py','entry_point_sha256':sha('scripts/run_revised_eval.py'),
        'one_request_at_a_time':True,'hardware_uuid':subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()})
    assert not (execution/condition).exists(),'No sampled-case restart'
    run(['.venv-gpu/bin/python','scripts/run_revised_eval.py','--stage',condition],'eval-'+condition)
    assert json.loads((execution/condition/'metadata.json').read_text())['status']=='complete'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',choices=plan()['nodes'],required=True);parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.execute:execute(args.node);return
    verify_plan();out=node_dir(args.node);out.mkdir(parents=True,exist_ok=True)
    command=['timeout','--signal=TERM','--kill-after=60s',str(plan()['node_timeout_minutes'])+'m','python3','scripts/run_revised_separate_node.py','--node',args.node,'--execute']
    receipt={'node':args.node,'pid':os.getpid(),'started_at':now(),'command':command}
    with (out/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
    result=subprocess.run(command)
    with (out/'controller-result.json').open('x') as f:json.dump({**receipt,'finished_at':now(),'returncode':result.returncode},f,indent=2)


if __name__=='__main__':main()
