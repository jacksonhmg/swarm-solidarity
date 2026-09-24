#!/usr/bin/env python3
"""Merge one terminal corrective/control adapter with its exact prepared base."""
import argparse
import json
from pathlib import Path
import time
from corrective_support import LOG,EXECUTION,sha,write_json,verify_freeze,weights


def main():
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from peft import PeftModel
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True)
    run=parser.parse_args().run
    config=json.loads(Path('configs/corrective-comparison.json').read_text())
    assert run in config['training_execution_order'];verify_freeze()
    started=time.monotonic();base_path,base_hashes=weights('prepared')
    meta=json.loads((EXECUTION/'training'/run/'metadata.json').read_text())
    assert meta['status']=='complete' and meta['optimizer_updates']==125 and meta['initial_weight_files']==base_hashes
    adapter=Path('.local/corrective')/run/'terminal-adapter'
    for name,digest in meta['terminal_adapter_files'].items():assert sha(adapter/name)==digest
    destination=adapter.parent/'merged-terminal';assert not destination.exists()
    base=AutoModelForCausalLM.from_pretrained(base_path,local_files_only=True,torch_dtype=torch.float32)
    model=PeftModel.from_pretrained(base,adapter).merge_and_unload(safe_merge=True).to(dtype=torch.float16)
    model.config.use_cache=True
    model.save_pretrained(destination,safe_serialization=True,max_shard_size='4GB')
    AutoTokenizer.from_pretrained(base_path,local_files_only=True).save_pretrained(destination)
    write_json(EXECUTION/'training'/run/'merge.json',{'run':run,'base_path':base_path,'base_files':base_hashes,
        'terminal_adapter_files':meta['terminal_adapter_files'],'merge_dtype':'float32','saved_inference_dtype':'float16',
        'seconds':time.monotonic()-started,'files':{p.name:sha(p) for p in sorted(destination.iterdir()) if p.is_file()}})
    print('Terminal adapter merged once: '+run,flush=True)


if __name__=='__main__':main()
