#!/usr/bin/env python3
"""Exactly one epoch / 125 updates. No intermediate evaluation or checkpoint search."""
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import read_jsonl
from swarm_solidarity.preparation import encode_example,PreparationCollator,example_order


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from peft import LoraConfig,get_peft_model
    config_path=Path('configs/task-preparation.json')
    config=json.loads(config_path.read_text())
    freeze=json.loads(Path('experiment_log/004_task_preparation/freeze.json').read_text())
    for path,digest in freeze['files'].items():
        assert sha(path)==digest, 'Frozen input changed: '+path
    log=Path('experiment_log/004_task_preparation/training')
    if log.exists():
        raise SystemExit('Training already started; no automatic retries or resume')
    log.mkdir(parents=True)
    started=time.monotonic()
    metadata={'started_at':now(),'config':config,'code_revision':Path('.code-revision').read_text().strip(),
              'config_sha256':sha(config_path),'freeze_sha256':sha('experiment_log/004_task_preparation/freeze.json'),
              'gpu':torch.cuda.get_device_name(0),'packages':{p:importlib.metadata.version(p) for p in ['torch','transformers','peft','accelerate','tokenizers']}}
    metadata_path=log/'metadata.json'
    metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    assert torch.cuda.is_bf16_supported(), 'Frozen training requires BF16 support'
    random.seed(config['training_seed']);np.random.seed(config['training_seed']);torch.manual_seed(config['training_seed']);torch.cuda.manual_seed_all(config['training_seed'])
    torch.backends.cuda.matmul.allow_tf32=False
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['model_revision'])
    examples=read_jsonl('data/train/task-preparation-1000.jsonl')
    encoded=[encode_example(e,tokenizer,config['max_sequence_length']) for e in examples]
    check=json.loads(Path('experiment_log/004_task_preparation/preflight/mask_checks.json').read_text())
    encoded_hash=hashlib.sha256(json.dumps([(e['input_ids'],e['labels']) for e in encoded]).encode()).hexdigest()
    assert encoded_hash==check['encoded_ids_labels_sha256'], 'GPU tokenization differs from CPU preflight'
    order=example_order(len(examples),config['training_seed'])
    assert hashlib.sha256(json.dumps(order).encode()).hexdigest()==check['order_sha256']
    collate=PreparationCollator(tokenizer.pad_token_id)
    model=AutoModelForCausalLM.from_pretrained(config['model'],revision=config['model_revision'],
            torch_dtype=torch.bfloat16,attn_implementation=config['attention_implementation']).to('cuda')
    model.config.use_cache=False
    model=get_peft_model(model,LoraConfig(**config['lora']))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model.enable_input_require_grads()
    params=[p for p in model.parameters() if p.requires_grad]
    assert all(p.dtype==torch.float32 for p in params)
    assert all('lora_' in n for n,p in model.named_parameters() if p.requires_grad)
    metadata.update(trainable_parameters=sum(p.numel() for p in params),total_parameters=sum(p.numel() for p in model.parameters()),
                    encoded_ids_labels_sha256=encoded_hash,load_seconds=time.monotonic()-started,
                    trainable_parameter_names=[n for n,p in model.named_parameters() if p.requires_grad])
    metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    optimizer=torch.optim.AdamW(params,lr=config['learning_rate'],betas=tuple(config['betas']),
                               eps=config['epsilon'],weight_decay=config['weight_decay'])
    model.train();train_started=time.monotonic();updates=0;seen=[];token_total=0
    with (log/'updates.jsonl').open('w') as progress:
        for begin in range(0,len(order),8):
            step_started=time.monotonic()
            if step_started-train_started>config['training_elapsed_limit_seconds']:
                raise RuntimeError('Training time budget reached; no terminal checkpoint or evaluation')
            # Stop on measured throughput if the remaining frozen pass will not fit.
            if updates>=5 and (step_started-train_started)/updates*125>config['training_elapsed_limit_seconds']:
                raise RuntimeError('Measured throughput projects beyond the training budget; no tuning retry')
            group=[encoded[i] for i in order[begin:begin+8]]
            assert len(group)==8
            denominator=sum(sum(label!=-100 for label in e['labels'][1:]) for e in group)
            optimizer.zero_grad(set_to_none=True)
            lr=config['learning_rate']*min(1.0,(updates+1)/config['warmup_updates'])
            for pg in optimizer.param_groups:pg['lr']=lr
            loss_sum=0.0
            for m in range(0,8,2):
                cpu=collate(group[m:m+2])
                # Same tested labels reach the actual model unchanged.
                assert all(cpu['labels'][j,:len(e['labels'])].tolist()==e['labels'] for j,e in enumerate(group[m:m+2]))
                active=(cpu['labels'][:,1:]!=-100).sum().item()
                batch={k:v.to('cuda') for k,v in cpu.items()}
                with torch.autocast('cuda',dtype=torch.bfloat16):
                    result=model(**batch)
                    loss=result.loss*active/denominator
                if not torch.isfinite(loss):raise RuntimeError('Nonfinite loss; stop without retry')
                loss.backward();loss_sum+=loss.detach().item()
                del result,loss,batch
            norm=torch.nn.utils.clip_grad_norm_(params,config['max_gradient_norm'],error_if_nonfinite=True)
            optimizer.step();updates+=1
            seen.extend(e['example_id'] for e in group);token_total+=denominator
            row={'update':updates,'examples_seen':len(seen),'supervised_tokens':denominator,'loss':loss_sum,
                 'gradient_norm':norm.item(),'learning_rate':lr,'seconds':time.monotonic()-step_started,
                 'elapsed_training_seconds':time.monotonic()-train_started,
                 'example_ids':[e['example_id'] for e in group]}
            progress.write(json.dumps(row)+'\n');progress.flush();os.fsync(progress.fileno())
            print(json.dumps({k:v for k,v in row.items() if k!='example_ids'}),flush=True)
    assert updates==125 and len(seen)==len(set(seen))==1000
    assert token_total==sum(check['supervised_tokens'].values())
    adapter=Path('.local/preparation/terminal-adapter')
    assert not adapter.exists()
    model.save_pretrained(adapter,safe_serialization=True)
    tokenizer.save_pretrained(adapter)
    # PEFT must retain the exact public base revision for future loading.
    adapter_config=json.loads((adapter/'adapter_config.json').read_text())
    adapter_config['base_model_name_or_path']=config['model']
    adapter_config['revision']=config['model_revision']
    (adapter/'adapter_config.json').write_text(json.dumps(adapter_config,indent=2)+'\n')
    metadata.update(finished_at=now(),optimizer_updates=updates,examples_seen=len(seen),unique_examples=len(set(seen)),
                    supervised_tokens=token_total,training_seconds=time.monotonic()-train_started,
                    wall_seconds=time.monotonic()-started,peak_cuda_memory_bytes=torch.cuda.max_memory_allocated(),
                    terminal_adapter_files={str(p.relative_to(adapter)):sha(p) for p in sorted(adapter.glob('*')) if p.is_file()},
                    updates_sha256=sha(log/'updates.jsonl'),status='complete')
    metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    print('Exactly 125 updates complete; terminal adapter saved.',flush=True)


if __name__=='__main__':main()
