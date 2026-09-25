#!/usr/bin/env python3
"""Offline identity intervention and exact Stage A tokenizer equivalence."""
import hashlib
import json
from pathlib import Path
from followup_support import LOG, IDENTITY, OLD, STAGES, read_jsonl, write_json, sha

def main():
    from transformers import AutoTokenizer
    from swarm_solidarity.preparation import encode_example, example_order, PreparationCollator
    q=AutoTokenizer.from_pretrained('.local/followups/qwen-tokenizer')
    w=AutoTokenizer.from_pretrained('.local/preparation/tokenizer')
    assert q.get_vocab()==w.get_vocab() and q.chat_template==w.chat_template and q.all_special_ids==w.all_special_ids
    data=read_jsonl('data/train/task-preparation-1000.jsonl')
    encoded=[encode_example(e,q,2048) for e in data]
    original=json.loads(Path('experiment_log/004_task_preparation/preflight/mask_checks.json').read_text())
    check=json.loads((LOG/'preflight/mask_checks.json').read_text())
    for key in ('encoded_ids_labels_sha256','order_sha256','supervised_tokens','input_tokens_total','chat_template_sha256'):
        assert check[key]==original[key]
    old=read_jsonl(OLD/'inputs/prepared.jsonl')
    (LOG/'inputs').mkdir(exist_ok=True)
    replacements=[]
    for stage in STAGES:
        rows=[]
        for i,r in enumerate(old):
            assert r['prompt'].count("the human's task")==1
            assert q(r['prompt'],add_special_tokens=False)['input_ids']==r['prompt_token_ids']
            prompt=r['prompt'] if stage=='qwen_human' else r['prompt'].replace("the human's","the AI teammate Agent A's")
            ids=q(prompt,add_special_tokens=False)['input_ids'];assert len(ids)+8192<=12288
            row={**r,'source_condition':stage,'prompt':prompt,'prompt_token_ids':ids,
                 'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                 'prompt_token_sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest()}
            rows.append(row)
        path=LOG/'inputs'/(stage+'.jsonl');assert not path.exists()
        path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        replacements.append({'stage':stage,'responses':800,'sha256':sha(path),'changed_prompt_count':sum(a['prompt']!=b['prompt'] for a,b in zip(rows,old))})
    order=example_order(1000,41027);collate=PreparationCollator(q.pad_token_id)
    padded=sum(collate([encoded[j] for j in order[i:i+2]])['input_ids'].numel() for i in range(0,1000,2))
    training_records={r['id'] for e in data if e['kind']=='aggregation' for r in e['case']['records']}
    cases=read_jsonl('data/final/benign-audit-confirmation-200.jsonl')
    assert not training_records & {r['id'] for c in cases for r in c['records']}
    write_json(LOG/'preflight/equivalence.json',{'tokenizer_vocab_template_special_ids_equal':True,'all_800_original_prompt_arrays_equal':True,
        'stage_a_ids_labels_and_order_equal':True,'input_tokens':check['input_tokens_total'],'supervised_tokens':sum(check['supervised_tokens'].values()),
        'padded_input_tokens':padded,'training_evaluation_record_overlap':0,'inputs':replacements,
        'principal_replacement':{"before":"the human's","after":"the AI teammate Agent A's"},
        'unchanged':'Every other byte of each rendered prompt, role markers, evidence, request meaning, gold answers, request order and sampling seed. 40 legitimate-filtering notes also refer to the principal; those identity words are relabeled consistently.'})
    write_json(IDENTITY/'input_manifest.json',{'source':str(OLD/'inputs/prepared.jsonl'),'input_directory':str(LOG/'inputs'),
        'identity_change_only':True,'roles_unchanged':True,'conditions':[r for r in replacements if r['stage']!='qwen_human']})
    print(json.dumps(json.loads((LOG/'preflight/equivalence.json').read_text()),indent=2))

if __name__=='__main__':
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
    main()
