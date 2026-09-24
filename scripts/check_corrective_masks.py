#!/usr/bin/env python3
"""Actual CPU tokenization, batch construction and causal-mask checks for 010."""
import collections
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from corrective_support import LOG,CONFIG,sha,read_jsonl,write_json
from swarm_solidarity.corrective import TRAIN_NOTES,EVAL_NOTES,encode_example,PreparationCollator,example_order
from swarm_solidarity.preparation import AGGREGATION_NOTES,FILTERING_NOTES,encode_example as original_encode
from swarm_solidarity.data import TEMPLATES,TOOL,expected_answer,write_jsonl
from swarm_solidarity.paired_conflict import build_paired_messages,score_paired


def digest(value):return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def record_signature(case):
    return json.dumps(sorted([{k:v for k,v in r.items() if k!='id'} for r in case['records']],key=lambda r:json.dumps(r,sort_keys=True)),sort_keys=True)


def case_check(c):
    actual=[json.loads(line) for w in c['workers'] for line in w['message'].splitlines() if line.startswith('{')]
    assert actual==c['records'] and len(actual)==6
    assert len(c['workers'])==3 and all(len(w['record_ids'])==2 for w in c['workers'])
    assert sum(r['status']=='running' for r in actual) in (1,2)
    for w in c['workers']:
        assert any(r['status']=='completed' for r in actual if r['id'] in w['record_ids'])
    w=next(w for w in c['workers'] if w['worker_id']==c['target_worker_id'])
    target=next(r for r in actual if r['id']==c['target_id'])
    assert target['status']=='completed' and target['result']=='failed'
    assert all(r['status']=='completed' for r in actual if r['id'] in w['record_ids'])
    assert score_paired(c,json.dumps(expected_answer(c)))['strict_table_plus_exact_audit']


def main():
    import torch
    from transformers import AutoTokenizer
    from transformers.loss.loss_utils import ForCausalLMLoss
    config=json.loads(CONFIG.read_text())
    tokenizer=AutoTokenizer.from_pretrained('.local/preparation/tokenizer',local_files_only=True)
    old=json.loads(Path('experiment_log/004_task_preparation/preflight/mask_checks.json').read_text())
    assert hashlib.sha256(tokenizer.chat_template.encode()).hexdigest()==old['chat_template_sha256']
    arms={a:read_jsonl(f'data/train/corrective-{a}-1000.jsonl') for a in config['arms']}
    final=read_jsonl('data/final/corrective-200.jsonl')
    assert len(final)==800 and len({c['scenario_id'] for c in final})==200
    previous=[]
    for p in list(Path('data/dev').glob('*.jsonl'))+[Path('data/train/task-preparation-1000.jsonl')]:
        for row in read_jsonl(p):
            c=row.get('case',row)
            if 'records' in c and 'workers' in c:previous.append(c)
    prior_ids={r['id'] for c in previous for r in c['records']}
    prior_signatures={record_signature(c) for c in previous}
    train_ids=set();train_signatures=set()
    for a,examples in arms.items():
        expected={k:v for k,v in config['arms'][a].items() if v}
        assert collections.Counter(e['kind'] for e in examples)==expected
        assert len({e['example_id'] for e in examples})==1000
        for e in examples:
            if e['kind']!='neutral':
                c=e['case'];case_check(c)
                assert c['variant'] in ('clean','falsification')
                assert json.loads(e['answer'])==expected_answer(c)
                assert not prior_ids.intersection(r['id'] for r in c['records'])
                train_ids.update(r['id'] for r in c['records']);train_signatures.add(record_signature(c))
            else:
                answer=json.loads(e['answer']);text=e['messages'][1]['content']
                assert all(f'{k}={v}' in text for row in answer['records']+answer['audit'] for k,v in row.items())
                assert all(row['issue']=='falsification' for row in answer['audit'])
                assert 'improper_omission' not in json.dumps(e)
        for kind in ('aggregation','corrective'):
            selected=[e for e in examples if e['kind']==kind]
            assert sum(e['explicit_running_filter'] for e in selected)==len(selected)//2
    for a,b in zip(arms['ordinary'],arms['corrective']):
        assert a['example_id']==b['example_id']
        if b['kind']!='corrective':assert a==b
        else:
            assert a['case']['records']==b['case']['records']
            assert json.loads(a['answer'])['records']==json.loads(b['answer'])['records']
            for wa,wb in zip(a['case']['workers'],b['case']['workers']):
                assert wa['worker_id']==wb['worker_id'] and wa['record_ids']==wb['record_ids']
                la=wa['message'].splitlines();lb=wb['message'].splitlines()
                diffs=[(x,y) for x,y in zip(la,lb) if x!=y]
                assert len(la)==len(lb)
                assert len(diffs)==int(wa['worker_id']==a['case']['target_worker_id'])
                assert all(x.startswith('Worker note: ') and y.startswith('Worker note: ') for x,y in diffs)
    for i in range(0,800,4):
        group=final[i:i+4]
        assert len({record_signature(c) for c in group})==1
        for c in group:
            case_check(c)
            assert c['records']==group[0]['records']
            assert not (prior_ids|train_ids).intersection(r['id'] for r in c['records'])
            assert record_signature(c) not in prior_signatures|train_signatures
            if c['variant']=='legitimate_filtering':
                assert next(r for r in c['records'] if r['id']==c['request_target_id'])['status']=='running'
            for wa,wb in zip(group[0]['workers'],c['workers']):
                assert wa['worker_id']==wb['worker_id'] and wa['record_ids']==wb['record_ids']
                la,lb=wa['message'].splitlines(),wb['message'].splitlines()
                assert len(la)==len(lb)
                assert sum(x!=y for x,y in zip(la,lb))==int(c['variant']!='clean' and wa['worker_id']==c['target_worker_id'])
    old_notes={s for seq in TEMPLATES.values() for s in seq}|set(AGGREGATION_NOTES)|set(FILTERING_NOTES)
    train_notes={s for seq in TRAIN_NOTES.values() for s in seq}
    final_notes={s for seq in EVAL_NOTES.values() for s in seq}
    assert not train_notes&old_notes and not final_notes&(old_notes|train_notes)
    out=LOG/'preflight';out.mkdir(exist_ok=False)
    (out/'chat_template.jinja').write_text(tokenizer.chat_template)
    collate=PreparationCollator(tokenizer.pad_token_id)
    checks={};representatives=[];markdown=['# Actual collated token supervision','',
        'LOSS identifies actual causal targets; MASK identifies label -100. No sampled outputs or model forward pass.','']
    for arm,examples in arms.items():
        encoded=[encode_example(e,tokenizer,2048) for e in examples]
        for source,e in zip(examples,encoded):
            if source['kind']=='aggregation':assert e==original_encode(source,tokenizer,2048)
        by_kind={k:{'examples':sum(e['kind']==k for e in encoded),
            'input_tokens':sum(len(e['input_ids']) for e in encoded if e['kind']==k),
            'supervised_tokens':sum(sum(x!=-100 for x in e['labels'][1:]) for e in encoded if e['kind']==k)}
            for k in sorted({e['kind'] for e in encoded})}
        orders={}
        for seed in config['training_seeds']:
            order=example_order(1000,seed);padded=0
            for offset in range(0,1000,2):
                selected=[encoded[i] for i in order[offset:offset+2]];batch=collate(selected)
                padded+=batch['input_ids'].numel()
                for j,e in enumerate(selected):
                    n=len(e['input_ids']);labels=batch['labels'][j].tolist();lo,hi=e['loss_character_span']
                    assert labels[:n]==e['labels'] and all(x==-100 for x in labels[n:])
                    assert batch['attention_mask'][j,n:].sum().item()==0
                    for idx,((a,b),tok,label) in enumerate(zip(e['offsets'],e['input_ids'],labels)):
                        assert (label!=-100)==(a>=lo and b<=hi and b>a)
                        if label!=-100:assert idx>0 and batch['labels'][j,1:][idx-1].item()==tok
                        if a<hi<b:assert label==-100
                    last=max(i for i,t in enumerate(e['input_ids']) if t==tokenizer.eos_token_id)
                    if e['kind']=='aggregation':
                        assert labels[last]==-100 and e['rendered'][hi:].startswith(', "audit": []}')
                        assert all(label==-100 for (a,b),label in zip(e['offsets'],labels) if b>hi)
                    else:assert labels[last]==tokenizer.eos_token_id
            orders[str(seed)]={'order_sha256':digest(order),'padded_input_tokens':padded,'micro_batches_checked':500,'updates':125}
        checks[arm]={'kind_budgets':by_kind,'input_tokens_total':sum(len(e['input_ids']) for e in encoded),
            'supervised_tokens':{k:v['supervised_tokens'] for k,v in by_kind.items()},
            'sequence_length_range':[min(len(e['input_ids']) for e in encoded),max(len(e['input_ids']) for e in encoded)],
            'encoded_ids_labels_sha256':digest([(e['input_ids'],e['labels']) for e in encoded]),'orders':orders}
        selected_indices=[0,1,800,801] if arm=='ordinary' else [0,1]
        for index in selected_indices:
            e=encoded[index];batch=collate([e,encoded[0 if index>=800 else 800]])
            labels=batch['labels'][0].tolist();ids=batch['input_ids'][0].tolist()
            representatives.append({'arm':arm,'example_id':e['example_id'],'kind':e['kind'],'rendered':e['rendered'],
                'loss_character_span':e['loss_character_span'],'decoded_padded':tokenizer.decode(ids,skip_special_tokens=False),
                'tokens':[{'index':i,'token_id':t,'decoded':tokenizer.decode([t],skip_special_tokens=False),
                    'label':labels[i],'loss':labels[i]!=-100,'character_offset':e['offsets'][i] if i<len(e['offsets']) else None} for i,t in enumerate(ids)]})
            markdown+=['## '+arm+'/'+e['example_id'],'','Prompt (all MASK):','```text',e['prompt'],'```','','Actual continuation:','```text']
            start=len(tokenizer(e['prompt'],add_special_tokens=False)['input_ids']);group=[];flag=None
            for i in range(start,len(ids)):
                active=labels[i]!=-100
                if group and active!=flag:
                    markdown.append(('LOSS ' if flag else 'MASK ')+repr(tokenizer.decode(group,skip_special_tokens=False)));group=[]
                group.append(ids[i]);flag=active
            if group:markdown.append(('LOSS ' if flag else 'MASK ')+repr(tokenizer.decode(group,skip_special_tokens=False)))
            markdown+=['```','']
    labels=torch.tensor([[-100,1,-100,2,-100]]);logits=torch.zeros((1,5,5),requires_grad=True)
    ForCausalLMLoss(logits,labels,vocab_size=5).backward()
    assert (logits.grad.abs().sum(-1)>0).tolist()==[[True,False,True,False,False]]
    write_jsonl(out/'decoded_token_masks.jsonl',representatives)
    (out/'decoded_token_masks.md').write_text('\n'.join(markdown)+'\n')
    inputs_dir=LOG/'inputs';inputs_dir.mkdir(exist_ok=False)
    order=list(range(800));random.Random(17).shuffle(order);ranges={}
    for condition in ('prepared','prompt_only'):
        items=[]
        for position,index in enumerate(order):
            c=final[index];messages=build_paired_messages(c,condition)
            prompt=tokenizer.apply_chat_template(messages,tools=[TOOL],tokenize=False,add_generation_prompt=True)
            ids=tokenizer.encode(prompt,add_special_tokens=False);assert len(ids)+8192<=12288
            items.append({'case_id':c['case_id'],'scenario_id':c['scenario_id'],'variant':c['variant'],
                'source_condition':condition,'replay_position':position,'source_response_line':None,
                'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                'prompt_token_ids':ids,'prompt_token_sha256':digest(ids),
                'sampling_seed':(17+int(hashlib.sha256(c['scenario_id'].encode()).hexdigest()[:8],16))%2**31})
        write_jsonl(inputs_dir/(condition+'.jsonl'),items)
        ranges[condition]=[min(len(i['prompt_token_ids']) for i in items),max(len(i['prompt_token_ids']) for i in items)]
    summary={'arms':checks,'actual_collated_masks_checked_both_seeds':True,'causal_shift_gradient_test':True,
        'aggregation_encoder_identical_to_preparation':True,'all_gold_answers_match_supplied_evidence':True,
        'shared_neutral_examples_byte_identical':True,'neutral_empty':100,'neutral_nonempty_falsification':100,
        'train_final_record_id_overlap':0,'final_prior_id_overlap':0,'final_id_normalized_evidence_overlap':0,
        'train_final_note_overlap':0,'final_development_note_overlap':0,'final_prompt_token_ranges':ranges,
        'chat_template_sha256':sha(out/'chat_template.jinja'),'inference_config_sha256':sha(config['inference_config']),
        'config_sha256':sha(CONFIG),'packages':{p:importlib.metadata.version(p) for p in ['torch','transformers','tokenizers','peft']}}
    write_json(out/'mask_checks.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
