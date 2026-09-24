#!/usr/bin/env python3
"""CPU-only token/batch verification, loss-weight accounting and input freeze."""
import collections
import hashlib
import json
import random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from revised_support import LOG, CONFIG, DATA, OLD, read_jsonl, write_json, sha
from swarm_solidarity.corrective import encode_example as old_encode, EVAL_NOTES, TRAIN_NOTES
from swarm_solidarity.benign_audit import encode_example
from swarm_solidarity.preparation import PreparationCollator, example_order
from swarm_solidarity.data import TOOL, write_jsonl
from swarm_solidarity.paired_conflict import build_paired_messages
from check_corrective_masks import record_signature, case_check


def digest(value):
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def main():
    import torch
    from transformers import AutoTokenizer
    from transformers.loss.loss_utils import ForCausalLMLoss
    config = json.loads(CONFIG.read_text())
    assert json.loads((LOG/'supervision_gap.json').read_text())['description_confirmed']
    tokenizer = AutoTokenizer.from_pretrained('.local/preparation/tokenizer', local_files_only=True)
    original = json.loads((OLD/'preflight/mask_checks.json').read_text())['arms']['corrective']
    examples = read_jsonl(config['training_dataset'])
    assert collections.Counter(e['kind'] for e in examples) == {'aggregation':400, 'corrective':400, 'neutral':200}
    old = [old_encode(e, tokenizer) for e in examples]
    new = [encode_example(e, tokenizer) for e in examples]
    assert digest([(e['input_ids'], e['labels']) for e in old]) == original['encoded_ids_labels_sha256']
    added = []; representatives = []; seen = set(); boundary_tokens = collections.Counter()
    for source, a, b in zip(examples, old, new):
        assert {k:v for k,v in a.items() if k not in ('labels','loss_character_span')} == {k:v for k,v in b.items() if k not in ('labels','loss_character_span')}
        changed = [i for i,(x,y) in enumerate(zip(a['labels'], b['labels'])) if x != y]
        if source['kind'] != 'aggregation':
            assert a == b
        else:
            assert changed and all(a['labels'][i] == -100 and b['labels'][i] == b['input_ids'][i] for i in changed)
            assert all(b['offsets'][i][1] > a['loss_character_span'][1] for i in changed)
            assert json.loads(source['answer'])['audit'] == []
            for i in changed:
                lo, hi = b['offsets'][i]
                if lo < a['loss_character_span'][1] < hi:
                    boundary_tokens[tokenizer.decode([b['input_ids'][i]], skip_special_tokens=False)] += 1
        added.append(len(changed))
        category = (source['kind'], bool(source.get('explicit_running_filter')), bool(json.loads(source['answer'])['audit']))
        if category not in seen:
            seen.add(category)
            representatives.append({'example_id':b['example_id'], 'kind':b['kind'], 'explicit_running_filter':category[1],
                'rendered':b['rendered'], 'prompt':b['prompt'], 'added_supervised_tokens':len(changed),
                'tokens':[{'index':i, 'id':token, 'decoded':tokenizer.decode([token],skip_special_tokens=False),
                           'old_label':a['labels'][i], 'new_label':b['labels'][i], 'offset':b['offsets'][i]}
                          for i, token in enumerate(b['input_ids'])]})
    collate = PreparationCollator(tokenizer.pad_token_id)
    orders = {}; weighting = []
    for seed in config['training_seeds']:
        order = example_order(1000, seed)
        assert digest(order) == original['orders'][str(seed)]['order_sha256']
        padded = 0; rows = []
        for offset in range(0,1000,2):
            selected = [new[i] for i in order[offset:offset+2]]
            batch = collate(selected); padded += batch['input_ids'].numel()
            for j, e in enumerate(selected):
                n = len(e['input_ids']); labels = batch['labels'][j].tolist(); start,end=e['loss_character_span']
                assert labels[:n] == e['labels'] and all(x == -100 for x in labels[n:])
                assert batch['attention_mask'][j,n:].sum().item() == 0
                for i, (token,label,(lo,hi)) in enumerate(zip(e['input_ids'],labels,e['offsets'])):
                    assert (label != -100) == (lo >= start and hi <= end and hi > lo)
                    if label != -100:
                        assert i > 0 and batch['labels'][j,1:][i-1].item() == token
                last = max(i for i,t in enumerate(e['input_ids']) if t == tokenizer.eos_token_id)
                assert labels[last] == tokenizer.eos_token_id
        assert padded == original['orders'][str(seed)]['padded_input_tokens']
        for update, start in enumerate(range(0,1000,8),1):
            ids = order[start:start+8]; budgets = {}
            for name, enc in [('old',old),('revised',new)]:
                by = collections.Counter()
                for i in ids:
                    by[enc[i]['kind']] += sum(t != -100 for t in enc[i]['labels'][1:])
                total = sum(by.values()); budgets[name] = {'total':total, 'by_kind':dict(by), 'loss_share':{k:by[k]/total for k in ('aggregation','corrective','neutral')}}
            rows.append({'seed':seed,'update':update,'example_ids':[new[i]['example_id'] for i in ids],
                'budgets':budgets, 'old_supervised_token_weight_multiplier':budgets['old']['total']/budgets['revised']['total']})
        weighting += rows
        orders[str(seed)] = {'order_sha256':digest(order), 'padded_input_tokens':padded,'micro_batches_checked':500,'updates':125,
            'old_token_weight_multiplier_range':[min(x['old_supervised_token_weight_multiplier'] for x in rows),max(x['old_supervised_token_weight_multiplier'] for x in rows)],
            'mean_loss_share_per_update':{name:{k:sum(x['budgets'][name]['loss_share'][k] for x in rows)/125 for k in ('aggregation','corrective','neutral')} for name in ('old','revised')}}
    labels=torch.tensor([[-100,1,-100,2,-100]]); logits=torch.zeros((1,5,5),requires_grad=True)
    ForCausalLMLoss(logits,labels,vocab_size=5).backward()
    assert (logits.grad.abs().sum(-1)>0).tolist()==[[True,False,True,False,False]]
    final = read_jsonl(DATA); assert len(final)==800 and len({c['scenario_id'] for c in final})==200
    previous = []; previous_files=[]
    for path in sorted(Path('data').rglob('*.jsonl')):
        if path == DATA: continue
        previous_files.append(str(path))
        for row in read_jsonl(path):
            case = row.get('case',row)
            if 'records' in case and 'workers' in case: previous.append(case)
    prior_ids = {r['id'] for c in previous for r in c['records']}
    signatures = {record_signature(c) for c in previous}
    assert len({record_signature(c) for c in final}) == 200
    for i in range(0,800,4):
        group=final[i:i+4]
        for c in group:
            case_check(c)
            assert c['records']==group[0]['records']
            assert not prior_ids.intersection(r['id'] for r in c['records'])
            assert record_signature(c) not in signatures, 'Collision: stop without reroll'
            for a,b in zip(group[0]['workers'],c['workers']):
                x,y=a['message'].splitlines(),b['message'].splitlines()
                assert len(x)==len(y) and sum(u!=v for u,v in zip(x,y))==int(c['variant']!='clean' and a['worker_id']==c['target_worker_id'])
    assert not {n for v in EVAL_NOTES.values() for n in v}&{n for v in TRAIN_NOTES.values() for n in v}
    output=LOG/'preflight';output.mkdir(exist_ok=False)
    (output/'chat_template.jinja').write_text(tokenizer.chat_template)
    assert sha(output/'chat_template.jinja')==sha(OLD/'preflight/chat_template.jinja')
    write_jsonl(output/'decoded_token_masks.jsonl', representatives)
    md=['# Original versus revised causal targets','','Input tokens and all prompts are identical; only aggregation suffix labels change.','']
    for r in representatives:
        md += ['## '+r['example_id'],'','```text']
        for name in ('old','new'):
            spans=[];flag=None;tokens=[]
            for token in r['tokens']:
                if token['offset'][1]<=len(r['prompt']):continue
                active=token[name+'_label']!=-100
                if tokens and active!=flag:
                    spans.append(('LOSS ' if flag else 'MASK ')+repr(tokenizer.decode(tokens,skip_special_tokens=False)));tokens=[]
                tokens.append(token['id']);flag=active
            if tokens:spans.append(('LOSS ' if flag else 'MASK ')+repr(tokenizer.decode(tokens,skip_special_tokens=False)))
            md += [name.upper(),*spans]
        md += ['```','']
    (output/'decoded_token_masks.md').write_text('\n'.join(md)+'\n')
    write_jsonl(output/'update_loss_weights.jsonl', weighting)
    budgets={k:{'examples':sum(e['kind']==k for e in new),'input_tokens':sum(len(e['input_ids']) for e in new if e['kind']==k),
        'supervised_tokens':sum(sum(t!=-100 for t in e['labels'][1:]) for e in new if e['kind']==k)} for k in ('aggregation','corrective','neutral')}
    arm={'kind_budgets':budgets,'input_tokens_total':sum(len(e['input_ids']) for e in new),'supervised_tokens':{k:v['supervised_tokens'] for k,v in budgets.items()},
        'encoded_ids_labels_sha256':digest([(e['input_ids'],e['labels']) for e in new]),'orders':orders}
    old_total=sum(original['supervised_tokens'].values());new_total=sum(arm['supervised_tokens'].values())
    inputs=LOG/'inputs';inputs.mkdir(exist_ok=False);order=list(range(800));random.Random(17).shuffle(order)
    for condition in ('prepared','prompt_only'):
        items=[]
        for pos,index in enumerate(order):
            c=final[index];prompt=tokenizer.apply_chat_template(build_paired_messages(c,condition),tools=[TOOL],tokenize=False,add_generation_prompt=True)
            ids=tokenizer.encode(prompt,add_special_tokens=False);assert len(ids)+8192<=12288
            items.append({'case_id':c['case_id'],'scenario_id':c['scenario_id'],'variant':c['variant'],'source_condition':condition,
                'replay_position':pos,'source_response_line':None,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                'prompt_token_ids':ids,'prompt_token_sha256':digest(ids),'sampling_seed':(17+int(hashlib.sha256(c['scenario_id'].encode()).hexdigest()[:8],16))%2**31})
        write_jsonl(inputs/(condition+'.jsonl'),items)
    summary={'arms':{'revised':arm},'old_supervised_tokens':old_total,'revised_supervised_tokens':new_total,
        'added_supervised_tokens':sum(added),'relative_loss_token_increase':new_total/old_total-1,
        'newly_supervised_boundary_tokens':dict(boundary_tokens),'unchanged_falsification_and_neutral_examples':600,
        'identical_input_tokens_prompts_example_order_and_padding':True,'actual_collated_masks_checked_both_seeds':True,
        'causal_shift_gradient_test':True,'no_omission_training_demonstrations':True,
        'overlap_check_files':previous_files,'record_id_overlap':0,'normalized_evidence_overlap':0,
        'evaluation_note_templates_reused_from_010':20,'evaluation_training_note_overlap':0,
        'chat_template_sha256':sha(output/'chat_template.jinja'),'config_sha256':sha(CONFIG)}
    assert new_total-old_total==sum(added)
    write_json(output/'mask_checks.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
