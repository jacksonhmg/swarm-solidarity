#!/usr/bin/env python3
"""Run two assigned full conditions with the unchanged frozen inference entry point."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from corrective_parallel_support import LOG,PARALLEL,plan,node_spec,node_dir,now,verify_amendment,sha,write_json


def execute(node):
    verify_amendment();spec=node_spec(node);out=node_dir(node);out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.update(HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
    env['PATH']=str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(command,name):
        with (out/(name+'.log')).open('x') as log:subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    if node!='primary':
        run(['python3','-m','pip','install','--user','uv==0.8.22'],'uv-install')
        run(['uv','venv','--python','3.11.13','.venv-gpu'],'venv')
        run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'],'packages')
    versions=subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'],env=env)
    (out/'gpu-environment.txt').write_bytes(versions)
    assert versions==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
    assert gpu=='NVIDIA A100-SXM4-40GB',gpu
    (out/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    if node!='primary':
        # Reconstruct exact prepared base and only this node's trained terminal models.
        run(['.venv-gpu/bin/python','scripts/merge_corrective_base.py'],'merge-base')
        for condition in spec['conditions']:
            receipt_path=LOG/'execution/training'/condition/'merge.json'
            original_receipt=receipt_path.read_bytes()
            run(['.venv-gpu/bin/python','scripts/merge_corrective_adapter.py','--run',condition],'merge-'+condition)
            actual=json.loads(receipt_path.read_text())
            assert actual['files']==plan()['trained_weight_files'][condition]
            write_json(out/('merge-'+condition+'.json'),actual)
            # Keep original training provenance frozen; local reconstruction
            # timing belongs to this node's separate receipt.
            receipt_path.write_bytes(original_receipt)
    verify_amendment()
    write_json(out/'assignment.json',{'node':node,'conditions':spec['conditions'],'responses':1600,
        'gpu':gpu,'code_revision':Path('.code-revision').read_text().strip(),'original_freeze_sha256':sha(LOG/'freeze.json'),
        'parallel_freeze_sha256':sha(LOG/'parallel_freeze.json'),'entry_point':'scripts/run_corrective_eval.py',
        'entry_point_sha256':sha('scripts/run_corrective_eval.py'),'one_request_at_a_time':True,
        'hardware_uuid':subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()})
    for condition in spec['conditions']:
        assert not (LOG/'execution'/condition).exists(),'No sampled-case restart'
        run(['.venv-gpu/bin/python','scripts/run_corrective_eval.py','--stage',condition],'eval-'+condition)
        meta=json.loads((LOG/'execution'/condition/'metadata.json').read_text());assert meta['status']=='complete'
    print('Node finished exactly 1600 responses: '+node,flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',choices=plan()['nodes'],required=True);parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.execute:execute(args.node);return
    verify_amendment();out=node_dir(args.node);out.mkdir(parents=True,exist_ok=True)
    command=['timeout','--signal=TERM','--kill-after=60s',str(plan()['node_timeout_minutes'])+'m',
        'python3','scripts/run_corrective_parallel_node.py','--node',args.node,'--execute']
    receipt={'node':args.node,'pid':os.getpid(),'started_at':now(),'command':command}
    with (out/'controller-launch.json').open('x') as f:json.dump(receipt,f,indent=2)
    result=subprocess.run(command)
    with (out/'controller-result.json').open('x') as f:json.dump({**receipt,'finished_at':now(),'returncode':result.returncode},f,indent=2)


if __name__=='__main__':main()
