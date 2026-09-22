#!/usr/bin/env python3
"""Pre-rental CPU verification of the real tokenizer, collator, and causal labels."""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import expected_answer, read_jsonl, write_jsonl
from swarm_solidarity.preparation import (encode_example, PreparationCollator, example_order,
                                         NATIVE_COMPLETION_PREFIX)
from swarm_solidarity.scoring import score


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(output, tokenizer_path):
    import torch
    from transformers import AutoTokenizer
    from transformers.loss.loss_utils import ForCausalLMLoss
    config = json.loads(Path('configs/task-preparation.json').read_text())
    examples = read_jsonl('data/train/task-preparation-1000.jsonl')
    evaluation = read_jsonl('data/dev/preparation-clean-40.jsonl')
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    old = json.loads(Path('experiment_log/003_six_record_feasibility/main/metadata.json').read_text())
    assert hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() == old['chat_template_sha256']
    assert Counter(e['kind'] for e in examples) == {'aggregation':800, 'neutral':200}
    assert sum(e.get('explicit_running_filter',False) for e in examples) == 400
    assert len({e['example_id'] for e in examples}) == 1000
    assert len(evaluation) == len({c['case_id'] for c in evaluation}) == 40
    train_records=set()
    for e in examples:
        if e['kind']=='aggregation':
            c=e['case']; assert c['variant']=='clean' and c['incidents']==[]
            actual=[json.loads(s) for w in c['workers'] for s in w['message'].splitlines() if s.startswith('{')]
            assert actual==c['records'] and len(actual)==6
            assert json.loads(e['answer'])==expected_answer(c)
            assert all(any(r['status']=='completed' for r in actual if r['id'] in w['record_ids']) for w in c['workers'])
            train_records.update(r['id'] for r in actual)
            # Worker messages and active targets contain no conflict demonstrations.
            text=' '.join(w['message'] for w in c['workers']).lower()
            assert not any(s in text for s in ['falsification','improper_omission','hide','misrepresent','even though','looks better'])
        else:
            text=json.dumps(e).lower()
            assert not any(s in text for s in ['audit','falsification','omission','misconduct','failed','passed'])
    for c in evaluation:
        assert not train_records.intersection(r['id'] for r in c['records'])
        assert score(c,json.dumps(expected_answer(c)))['exact_table']
    # Compare fresh evidence with prior clean development only; never open final-test data.
    def signature(c):
        return json.dumps(c['workers'],sort_keys=True)
    previous=[c for p in ['data/dev/diagnosis-clean-12.jsonl','data/dev/confirmation-clean-40.jsonl','data/dev/six-record-v2-clean-40.jsonl'] for c in read_jsonl(p)]
    assert not set(map(signature,evaluation)).intersection(map(signature,previous))
    encoded=[encode_example(e,tokenizer,config['max_sequence_length']) for e in examples]
    collate=PreparationCollator(tokenizer.pad_token_id)
    order=example_order(1000,config['training_seed'])
    supervised=Counter(); masked_audit=masked_stop=supervised_stop=boundary_masked=0
    for offset in range(0,1000,config['micro_batch_size']):
        selected=[encoded[i] for i in order[offset:offset+config['micro_batch_size']]]
        batch=collate(selected)
        for j,e in enumerate(selected):
            labels=batch['labels'][j].tolist(); n=len(e['input_ids'])
            assert labels[:n]==e['labels']
            assert all(x==-100 for x in labels[n:])
            assert batch['attention_mask'][j,n:].sum().item()==0
            lo,hi=e['loss_character_span']
            for i,((a,b),tok,label) in enumerate(zip(e['offsets'],e['input_ids'],labels)):
                wanted=(a>=lo and b<=hi and b>a)
                assert (label!=-100)==wanted
                if label!=-100:
                    assert label==tok and i>0
                    # HF causal loss consumes labels[:,1:] against logits[:,:-1].
                    assert batch['labels'][j,1:][i-1].item()==tok
                if a<hi<b:
                    assert label==-100
                    boundary_masked+=1
                if e['kind']=='aggregation' and b>hi:
                    assert label==-100
            supervised[e['kind']]+=sum(x!=-100 for x in labels)
            last_eos=max(i for i,t in enumerate(e['input_ids']) if t==tokenizer.eos_token_id)
            if e['kind']=='aggregation':
                assert labels[last_eos]==-100
                assert e['rendered'][hi:].startswith(', "audit": []}')
                masked_audit+=1; masked_stop+=1
            else:
                assert labels[last_eos]==tokenizer.eos_token_id
                supervised_stop+=1
    # Exercise the actual pinned HF loss shift/ignore semantics without model inference.
    labels=torch.tensor([[-100,1,-100,2,-100]])
    logits=torch.zeros((1,5,5),requires_grad=True)
    ForCausalLMLoss(logits,labels,vocab_size=5).backward()
    assert (logits.grad.abs().sum(-1)>0).tolist()==[[True,False,True,False,False]]
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    (output/'chat_template.jinja').write_text(tokenizer.chat_template)
    representatives=[next(i for i,e in enumerate(examples) if e['kind']=='aggregation' and not e['explicit_running_filter']),
                     next(i for i,e in enumerate(examples) if e.get('explicit_running_filter')),
                     800,801]
    records=[]; markdown=['# Actual token supervision, after collation','',
        'LOSS means that exact token ID is a causal prediction target. MASK tokens have label -100.',
        'Native empty reasoning delimiters are generated by the pinned template; no reasoning trace is supplied.','']
    for index in representatives:
        e=encoded[index]; batch=collate([e,encoded[800 if index<800 else 0]])
        labels=batch['labels'][0].tolist()
        tokens=[{'index':i,'token_id':tok,'token_piece':tokenizer.convert_ids_to_tokens(tok),
                 'decoded':tokenizer.decode([tok],skip_special_tokens=False),
                 'label':labels[i],'loss':labels[i]!=-100,'character_offset':list(e['offsets'][i]) if i<len(e['offsets']) else None}
                for i,tok in enumerate(batch['input_ids'][0].tolist())]
        records.append({'example_id':e['example_id'],'kind':e['kind'],'rendered':e['rendered'],
                        'decoded_padded':tokenizer.decode(batch['input_ids'][0],skip_special_tokens=False),
                        'loss_character_span':e['loss_character_span'],'tokens':tokens})
        markdown += ['## '+e['example_id'],'','Prompt (all MASK):','```text',e['prompt'],'```','',
                     'Assistant continuation, grouped by actual token labels:','```text']
        n_prompt=len(tokenizer(e['prompt'],add_special_tokens=False)['input_ids'])
        group=[]; previous_flag=None
        for i in range(n_prompt,len(e['input_ids'])):
            flag=labels[i]!=-100
            if group and flag!=previous_flag:
                markdown.append(('LOSS ' if previous_flag else 'MASK ')+repr(tokenizer.decode(group,skip_special_tokens=False)))
                group=[]
            group.append(e['input_ids'][i]); previous_flag=flag
        if group:markdown.append(('LOSS ' if previous_flag else 'MASK ')+repr(tokenizer.decode(group,skip_special_tokens=False)))
        markdown+=['```','',f'Padding: {len(labels)-len(e["input_ids"])} tokens, all MASK.','']
    write_jsonl(output/'decoded_token_masks.jsonl',records)
    (output/'decoded_token_masks.md').write_text('\n'.join(markdown)+'\n')
    summary={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'examples':1000,
             'micro_batches_checked':500,'effective_batches':125,'aggregation_audits_entirely_masked':masked_audit,
             'aggregation_end_tokens_masked':masked_stop,'neutral_end_tokens_supervised':supervised_stop,
             'boundary_crossing_tokens_masked':boundary_masked,'supervised_tokens':dict(supervised),
             'sequence_length_min':min(len(e['input_ids']) for e in encoded),
             'sequence_length_max':max(len(e['input_ids']) for e in encoded),
             'input_tokens_total':sum(len(e['input_ids']) for e in encoded),
             'explicit_legitimate_filtering_examples':400,'neutral_empty_lists':100,'neutral_nonempty_lists':100,
             'causal_shift_and_ignore_gradient_test':True,'padding_mask_verified':True,
             'fresh_evaluation_and_golden_answers_verified':True,'train_eval_record_id_overlap':0,
             'native_completion_prefix':NATIVE_COMPLETION_PREFIX,
             'chat_template_sha256':sha(output/'chat_template.jinja'),
             'data_sha256':sha('data/train/task-preparation-1000.jsonl'),
             'evaluation_sha256':sha('data/dev/preparation-clean-40.jsonl'),
             'config_sha256':sha('configs/task-preparation.json'),
             'encoded_ids_labels_sha256':hashlib.sha256(json.dumps([(e['input_ids'],e['labels']) for e in encoded]).encode()).hexdigest(),
             'order_sha256':hashlib.sha256(json.dumps(order).encode()).hexdigest(),
             'packages':{p:importlib.metadata.version(p) for p in ['torch','transformers','tokenizers','peft']}}
    (output/'mask_checks.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='experiment_log/004_task_preparation/preflight')
    p.add_argument('--tokenizer',default='.local/preparation/tokenizer')
    a=p.parse_args(); check(a.output,a.tokenizer)
