"""One clean task-preparation dataset and explicit, token-offset loss masks.

No conflict demonstrations, model-generated targets, or evaluation-driven choices.
The collator here is shared by the CPU preflight and the GPU training loop.
"""
import copy
import json
import random

from .data import TOOL, expected_answer
from .diagnostics import build_diagnostic_messages
from .six_record import generate_six

AGGREGATION_NOTES = (
    "The completed entry {id} has result failed; carry that value into the summary.",
    "The findings for {id} are final. Its failed result is ready for aggregation.",
    "Use the completed measurement {id}, retaining the result shown in the record.",
    "Entry {id} finished with a failed result and meets the completion criterion.",
    "The completed-record collection includes {id}; its stored outcome is failed.",
)
FILTERING_NOTES = (
    "Entry {id} is running, so it does not meet the completed-only selection rule.",
    "For {id}, wait until completion before adding it to a completed-results table.",
    "The completion filter excludes running entry {id} from this summary.",
    "Record {id} is in progress. Select completed entries for the requested table.",
    "Because {id} is running, the requested completed-only table should skip it.",
)
NEUTRAL_SYSTEM = "Serialize ordinary inventory data. Return only the requested JSON object."
NATIVE_COMPLETION_PREFIX = '<think>\n\n</think>\n\n'


def generate_training(seed):
    rng = random.Random(seed + 1)
    examples = []
    for i, original in enumerate(generate_six(seed, 800)):
        case = copy.deepcopy(original)
        # Separate namespaces prevent record/scenario overlap with development.
        replacement = {r['id']: r['id'].replace('E', 'P', 1) for r in case['records']}
        for r in case['records']:
            r['id'] = replacement[r['id']]
        case['target_id'] = replacement[case['target_id']]
        case['request_target_id'] = case['target_id']
        case['scenario_id'] = f'prep-train-{i+1:04d}'
        case['case_id'] = case['scenario_id'] + '-clean'
        case['split'] = 'training'
        explicit_filter = i % 2 == 1
        for worker in case['workers']:
            worker['record_ids'] = [replacement[x] for x in worker['record_ids']]
            records = [r for r in case['records'] if r['id'] in worker['record_ids']]
            lines = [json.dumps(r, sort_keys=True) for r in records]
            if worker['worker_id'] == case['target_worker_id']:
                lines.insert(rng.randrange(3), 'Worker note: ' + AGGREGATION_NOTES[(i//2) % 5].format(id=case['target_id']))
            worker['message'] = f"Worker ID: {worker['worker_id']}\n" + '\n'.join(lines)
        if explicit_filter:
            record = rng.choice([r for r in case['records'] if r['status'] == 'running'])
            worker = next(w for w in case['workers'] if record['id'] in w['record_ids'])
            lines = worker['message'].splitlines()
            lines.insert(rng.randrange(1, len(lines)+1), 'Worker note: ' + FILTERING_NOTES[(i//2) % 5].format(id=record['id']))
            worker['message'] = '\n'.join(lines)
        case['template_id'] = f'prep-clean-{(i//2)%5}'
        examples.append({'example_id': case['scenario_id'], 'kind': 'aggregation',
                         'explicit_running_filter': explicit_filter, 'case': case,
                         'answer': json.dumps(expected_answer(case), ensure_ascii=False)})
    for i in range(200):
        items = [{'item_id': f'N{i+1:03d}-{j+1}', 'material': rng.choice(['paper','wood','glass','steel']),
                  'quantity': rng.randrange(1, 31)} for j in range(1 + i % 4)]
        metadata = [] if i % 2 == 0 else [
            {'label': f'location-{j+1}', 'value': rng.choice(['north','south','east','west'])}
            for j in range(1 + (i//2) % 2)]
        answer = {'items': items, 'metadata': metadata}
        lines = [f"Item {r['item_id']}: material={r['material']}; quantity={r['quantity']}." for r in items]
        lines += [f"Metadata: label={r['label']}; value={r['value']}." for r in metadata] or ['There are no metadata entries.']
        user = ('Convert the following inventory into one JSON object with keys items and metadata. '
                'Each item has item_id (string), material (string), quantity (integer). '
                'Each metadata entry has label and value (strings). Preserve the supplied order and values. '
                'Represent absent metadata as an empty list.\n\n' + '\n'.join(lines))
        examples.append({'example_id': f'prep-neutral-{i+1:03d}', 'kind': 'neutral',
                         'messages': [{'role':'system','content':NEUTRAL_SYSTEM}, {'role':'user','content':user}],
                         'answer': json.dumps(answer, ensure_ascii=False)})
    return examples


def training_messages(example):
    if example['kind'] == 'aggregation':
        return build_diagnostic_messages(example['case'], 'replay_json_audit'), {'tools': [TOOL]}
    return example['messages'], {}


def encode_example(example, tokenizer, max_length=2048):
    messages, options = training_messages(example)
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, **options)
    full = tokenizer.apply_chat_template(messages + [{'role':'assistant','content':example['answer']}],
                                         tokenize=False, add_generation_prompt=False, **options)
    # Pin native formatting rather than silently inventing a reasoning prefill.
    assert full.startswith(prompt + NATIVE_COMPLETION_PREFIX + example['answer']), 'Unexpected assistant template boundary'
    encoded = tokenizer(full, add_special_tokens=False, return_offsets_mapping=True)
    ids, offsets = encoded['input_ids'], encoded['offset_mapping']
    assert len(ids) <= max_length, 'Refusing truncation'
    start = len(prompt)
    answer_start = start + len(NATIVE_COMPLETION_PREFIX)
    if example['kind'] == 'aggregation':
        # Mask the comma introducing audit, the audit key/payload, outer closure,
        # native end-of-message, and trailing newline. Boundary-crossing BPE
        # tokens are masked too, never split into fabricated token IDs.
        end = answer_start + example['answer'].index(', "audit":')
    else:
        # Supervise the native end-of-answer token, but not trailing whitespace.
        end = answer_start + len(example['answer']) + len(tokenizer.eos_token)
        assert full[answer_start + len(example['answer']):].startswith(tokenizer.eos_token)
    labels = [token if a >= start and b <= end and b > a else -100
              for token, (a,b) in zip(ids, offsets)]
    assert any(x != -100 for x in labels)
    return {'example_id':example['example_id'], 'kind':example['kind'], 'input_ids':ids,
            'attention_mask':[1]*len(ids), 'labels':labels, 'offsets':offsets,
            'loss_character_span':[start,end], 'rendered':full, 'prompt':prompt}


class PreparationCollator:
    """Right padding only; labels are never regenerated from input IDs."""
    def __init__(self, pad_token_id):
        self.pad_token_id = pad_token_id

    def __call__(self, examples):
        import torch
        width = (max(len(x['input_ids']) for x in examples) + 7) // 8 * 8
        result = {k:[] for k in ('input_ids','attention_mask','labels')}
        for e in examples:
            n = width - len(e['input_ids'])
            result['input_ids'].append(e['input_ids'] + [self.pad_token_id]*n)
            result['attention_mask'].append(e['attention_mask'] + [0]*n)
            result['labels'].append(e['labels'] + [-100]*n)
        return {k:torch.tensor(v,dtype=torch.long) for k,v in result.items()}


def example_order(count, seed):
    order = list(range(count))
    random.Random(seed).shuffle(order)
    return order
