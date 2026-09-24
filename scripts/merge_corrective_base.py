#!/usr/bin/env python3
"""Materialize pinned base plus terminal LoRA in FP16 for the fixed Transformers evaluation."""
import hashlib
import json
from pathlib import Path
import time


def main():
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from peft import PeftModel
    started=time.monotonic()
    config=json.loads(Path('configs/task-preparation.json').read_text())
    meta=json.loads(Path('experiment_log/004_task_preparation/training/metadata.json').read_text())
    assert meta['optimizer_updates']==125 and meta['status']=='complete'
    adapter=Path('.local/preparation/terminal-adapter')
    for p,digest in meta['terminal_adapter_files'].items():
        assert hashlib.sha256((adapter/p).read_bytes()).hexdigest()==digest
    destination=Path('.local/preparation/merged-terminal')
    assert not destination.exists()
    # CPU FP32 merge prevents repeated low-precision rounding of the adapter delta.
    base=AutoModelForCausalLM.from_pretrained(config['model'],revision=config['model_revision'],torch_dtype=torch.float32)
    model=PeftModel.from_pretrained(base,adapter).merge_and_unload(safe_merge=True).to(dtype=torch.float16)
    model.config.use_cache=True
    model.save_pretrained(destination,safe_serialization=True,max_shard_size='4GB')
    AutoTokenizer.from_pretrained(config['model'],revision=config['model_revision']).save_pretrained(destination)
    result={'merge_dtype':'float32','saved_inference_dtype':'float16','seconds':time.monotonic()-started,
            'base_model':config['model'],'base_revision':config['model_revision'],
            'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.glob('*')) if p.is_file()}}
    Path('experiment_log/010_corrective_comparison/execution/merge.json').write_text(json.dumps(result,indent=2)+'\n')
    assert result['files'] == json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
    print('Preserved terminal adapter merged; all file hashes equal experiment 004.',flush=True)


if __name__=='__main__':main()
