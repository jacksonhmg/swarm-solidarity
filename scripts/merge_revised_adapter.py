#!/usr/bin/env python3
"""Reconstruct preserved or revised terminal weights with the original merge path."""
import argparse
import json
from pathlib import Path
import time
from revised_support import LOG, EXECUTION, OLD, STAGES, adapter_info, sha, write_json, verify_freeze, weights


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);run=parser.parse_args().run
    assert run in STAGES and run not in ('prepared','prompt_only');verify_freeze()
    started=time.monotonic();base_path,base_hashes=weights('prepared')
    adapter,meta=adapter_info(run)
    assert meta['status']=='complete' and meta['optimizer_updates']==125 and meta['initial_weight_files']==base_hashes
    for name,digest in meta['terminal_adapter_files'].items():assert sha(adapter/name)==digest
    destination=adapter.parent/'merged-terminal';assert not destination.exists()
    base=AutoModelForCausalLM.from_pretrained(base_path,local_files_only=True,torch_dtype=torch.float32)
    model=PeftModel.from_pretrained(base,adapter).merge_and_unload(safe_merge=True).to(dtype=torch.float16)
    model.config.use_cache=True
    model.save_pretrained(destination,safe_serialization=True,max_shard_size='4GB')
    AutoTokenizer.from_pretrained(base_path,local_files_only=True).save_pretrained(destination)
    files={p.name:sha(p) for p in sorted(destination.iterdir()) if p.is_file()}
    if not run.startswith('revised_'):
        assert files==json.loads((OLD/'execution/training'/run/'merge.json').read_text())['files']
    (EXECUTION/'merges').mkdir(exist_ok=True)
    receipt=EXECUTION/'merges'/(run+'.json');assert not receipt.exists()
    write_json(receipt,{'run':run,'base_path':base_path,'base_files':base_hashes,'terminal_adapter_files':meta['terminal_adapter_files'],
        'merge_dtype':'float32','saved_inference_dtype':'float16','seconds':time.monotonic()-started,'files':files})


if __name__=='__main__':main()
