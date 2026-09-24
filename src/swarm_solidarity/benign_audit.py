"""One label-only revision; original data, tokenizer inputs and encoder preserved."""
import json
from .corrective import encode_example as original_encode, evaluation_cases as original_cases
from .preparation import NATIVE_COMPLETION_PREFIX


def encode_example(example, tokenizer, max_length=2048):
    encoded = original_encode(example, tokenizer, max_length)
    if example['kind'] != 'aggregation':
        return encoded
    assert json.loads(example['answer'])['audit'] == []
    start = len(encoded['prompt'])
    end = start + len(NATIVE_COMPLETION_PREFIX) + len(example['answer']) + len(tokenizer.eos_token)
    assert encoded['rendered'][end-len(tokenizer.eos_token):end] == tokenizer.eos_token
    encoded['labels'] = [token if a >= start and b <= end and b > a else -100
                         for token, (a, b) in zip(encoded['input_ids'], encoded['offsets'])]
    encoded['loss_character_span'] = [start, end]
    return encoded


def evaluation_cases(seed, count=200):
    # The prior evaluation note distribution is deliberately retained. Only fresh
    # underlying records/IDs and sampling seeds change in this confirmation study.
    cases = original_cases(seed, count)
    for c in cases:
        replacements = {r['id']: 'G'+r['id'][1:] for r in c['records']}
        for r in c['records']:
            r['id'] = replacements[r['id']]
        for w in c['workers']:
            w['record_ids'] = [replacements[x] for x in w['record_ids']]
            for old, new in replacements.items():
                w['message'] = w['message'].replace(old, new)
        for field in ('target_id', 'request_target_id'):
            c[field] = replacements[c[field]]
        for incident in c['incidents']:
            incident['record_id'] = replacements[incident['record_id']]
        c['scenario_id'] = c['scenario_id'].replace('final-six-', 'confirmation-six-')
        c['case_id'] = c['scenario_id']+'-'+c['variant']
        c['split'] = 'fresh_confirmation'
    return cases
