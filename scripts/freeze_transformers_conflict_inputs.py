#!/usr/bin/env python3
"""Reconstruct arrays from 005's archived rendered strings; never rebuild prompts."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from transformers_conflict_support import LOG, STAGES, partition, read_jsonl, sha, write_json, validate_inputs


def main():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained('.local/preparation/tokenizer', local_files_only=True)
    original = Path('experiment_log/005_paired_conflict')
    freeze = json.loads((original/'freeze.json').read_text())
    for path, digest in freeze['files'].items():
        assert sha(path) == digest, path
    raw = read_jsonl(original/'main/responses.jsonl')
    prompts = read_jsonl(original/'main/prompts.jsonl')
    frozen = {(p['case_id'],p['condition']): p for p in read_jsonl(original/'frozen_prompts.jsonl')}
    assert len(raw) == len(prompts) == len(frozen) == 320
    groups = {stage: [] for stage in STAGES}
    for line, (r,p) in enumerate(zip(raw,prompts),1):
        key=(r['case_id'],r['condition'])
        assert key == (p['case_id'],p['condition'])
        assert p['prompt'] == frozen[key]['prompt']
        tokens=tokenizer.encode(p['prompt'],add_special_tokens=False)
        assert len(tokens)==r['prompt_tokens']
        assert hashlib.sha256(p['prompt'].encode()).hexdigest()==r['prompt_sha256']
        stage=partition(r)
        groups[stage].append({'case_id':r['case_id'],'scenario_id':r['scenario_id'],'variant':r['variant'],
            'source_condition':r['condition'],'source_response_line':line,'replay_position':len(groups[stage]),
            'prompt':p['prompt'],'prompt_sha256':r['prompt_sha256'],'prompt_token_ids':tokens,
            'sampling_seed':r['sampling_seed']})
    target=LOG/'inputs';target.mkdir(exist_ok=False)
    for stage, items in groups.items():
        assert len(items)==STAGES[stage]
        (target/(stage+'.jsonl')).write_text(''.join(json.dumps(i)+'\n' for i in items))
        validate_inputs(stage)
    prior=read_jsonl('experiment_log/006_reproduction/inputs/005_clean.jsonl')
    for a,b in zip(groups['prepared_clean'],prior):
        for field in ('case_id','prompt','prompt_token_ids','sampling_seed','source_response_line'):
            assert a[field]==b[field]
    # Existing overlap and evidence checks remain applicable because the exact
    # dataset, prompts, scorer, and training artifacts are byte-identical.
    preflight=json.loads((original/'preflight.json').read_text())
    assert all(preflight[k]==0 for k in ('training_record_id_overlap','id_normalized_evidence_overlap','training_note_template_overlap'))
    write_json(LOG/'input_verification.json', {'n':320,'all_saved_strings_hashes_lengths_seeds_and_associations_match':True,
        'prepared_clean_arrays_equal_007_inputs':True,'chat_template_reapplied':False,
        'token_arrays_reconstructed_not_original_engine_archives':True,'source_preflight_sha256':sha(original/'preflight.json'),
        'retained_overlap_checks':{k:v for k,v in preflight.items() if 'overlap' in k},
        'token_ranges':{stage:[min(len(i['prompt_token_ids']) for i in items),max(len(i['prompt_token_ids']) for i in items)] for stage,items in groups.items()},
        'source_files':{str(p):sha(p) for p in [original/'main/prompts.jsonl',original/'main/responses.jsonl',original/'freeze.json']}})
    print('320 saved prompt strings, reconstructed arrays, associations and seeds verified; no model inference.')


if __name__=='__main__':main()
