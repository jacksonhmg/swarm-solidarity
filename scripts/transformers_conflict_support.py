"""Saved-input association and two-cell gate; no prompt construction or sampling."""
import hashlib
import json
from pathlib import Path
from reproduction_support import sha, read_jsonl, write_json, gates

LOG = Path('experiment_log/008_transformers_conflict')
EXECUTION = LOG / 'execution'
STAGES = {'prepared_clean': 40, 'prompt_only_clean': 40, 'conflicts': 240}


def partition(row):
    return row['condition'] + '_clean' if row['variant'] == 'clean' else 'conflicts'


def validate_inputs(stage):
    inputs = read_jsonl(LOG / 'inputs' / (stage + '.jsonl'))
    prompts = read_jsonl('experiment_log/005_paired_conflict/main/prompts.jsonl')
    raw = read_jsonl('experiment_log/005_paired_conflict/main/responses.jsonl')
    selected = [(line, r, p) for line, (r, p) in enumerate(zip(raw, prompts), 1) if partition(r) == stage]
    assert len(inputs) == len(selected) == STAGES[stage]
    for position, (item, (line, response, prompt)) in enumerate(zip(inputs, selected)):
        assert item['replay_position'] == position and item['source_response_line'] == line
        assert item['case_id'] == response['case_id'] == prompt['case_id']
        assert item['scenario_id'] == response['scenario_id']
        assert item['variant'] == response['variant']
        assert item['source_condition'] == response['condition'] == prompt['condition']
        assert item['prompt'] == prompt['prompt']
        assert hashlib.sha256(item['prompt'].encode()).hexdigest() == item['prompt_sha256'] == response['prompt_sha256']
        assert item['sampling_seed'] == response['sampling_seed']
        assert len(item['prompt_token_ids']) == response['prompt_tokens']
    return inputs, {c['case_id']: c for c in read_jsonl('data/dev/paired-conflict-40.jsonl')}


def verify_clean_gate(execution):
    result = {}
    for stage in ('prepared_clean', 'prompt_only_clean'):
        previous = Path(execution) / stage
        meta = json.loads((previous / 'metadata.json').read_text())
        assert meta['status'] == 'complete'
        for name in ('responses', 'scores'):
            assert sha(previous / (name + '.jsonl')) == meta[name + '_sha256']
        result[stage] = gates(read_jsonl(previous / 'scores.jsonl'))
    assert all(g['pass'] for g in result.values()), result
    return result
