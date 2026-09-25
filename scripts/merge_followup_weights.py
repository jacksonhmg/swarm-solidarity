#!/usr/bin/env python3
"""CPU FP32 merge, then FP16 storage; preserve original 011 weight hashes."""
import argparse
import json
from pathlib import Path
import time
from followup_support import LOG, OLD, verify_freeze, sha, write_json

def merge(kind, record=True):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from peft import PeftModel
    verify_freeze();started=time.monotonic()
    if kind=='qwen':
        config=json.loads(Path('configs/qwen-task-preparation.json').read_text())
        adapter=Path('.local/followups/qwen-terminal-adapter');meta=json.loads((LOG/'training/metadata.json').read_text())
        destination=Path('.local/followups/qwen-merged-terminal');base=config['model'];revision=config['model_revision'];expected=None
    elif kind=='prepared':
        config=json.loads(Path('configs/task-preparation.json').read_text())
        adapter=Path('.local/preparation/terminal-adapter');meta=json.loads(Path('experiment_log/004_task_preparation/training/metadata.json').read_text())
        destination=Path('.local/preparation/merged-terminal');base=config['model'];revision=config['model_revision']
        expected=json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
    else:
        assert kind in ('revised_s41031','revised_s41032')
        merge('prepared', record=False)
        adapter=Path('.local/revised_corrective')/kind/'terminal-adapter'
        meta=json.loads((OLD/'execution/training'/kind/'metadata.json').read_text())
        destination=adapter.parent/'merged-terminal';base='.local/preparation/merged-terminal';revision=None
        expected=json.loads((OLD/'execution/merges'/(kind+'.json')).read_text())['files']
    assert meta['status']=='complete' and meta['optimizer_updates']==125
    assert all(sha(adapter/p)==h for p,h in meta['terminal_adapter_files'].items())
    assert not destination.exists()
    base_model=AutoModelForCausalLM.from_pretrained(base,revision=revision,torch_dtype=torch.float32)
    model=PeftModel.from_pretrained(base_model,adapter).merge_and_unload(safe_merge=True).to(dtype=torch.float16)
    model.config.use_cache=True
    model.save_pretrained(destination,safe_serialization=True,max_shard_size='4GB')
    AutoTokenizer.from_pretrained(base,revision=revision).save_pretrained(destination)
    files={p.name:sha(p) for p in destination.iterdir() if p.is_file()}
    if expected is not None:assert files==expected,'Original checkpoint hashes differ'
    (LOG/'merges').mkdir(exist_ok=True)
    if record:
        write_json(LOG/'merges'/(kind+'.json'),{'path':str(destination),'files':files,'base_model':base,'base_revision':revision,
            'terminal_adapter_files':meta['terminal_adapter_files'],'merge_dtype':'float32','saved_inference_dtype':'float16','seconds':time.monotonic()-started})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind');merge(p.parse_args().kind)
