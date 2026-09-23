"""Small shared checks for the bounded reproduction; no model generation here."""
import hashlib
import json
from pathlib import Path

LOG = Path('experiment_log/006_reproduction')
EXECUTION = LOG / 'execution'
STAGES = {
    '004_replay': ('004_task_preparation', 'data/dev/preparation-clean-40.jsonl', 'replay_json_audit'),
    '005_clean': ('005_paired_conflict', 'data/dev/paired-conflict-40.jsonl', 'prepared'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def validate_inputs(stage):
    name, data, condition = STAGES[stage]
    inputs = read_jsonl(LOG / 'inputs' / (stage + '.jsonl'))
    prompts = read_jsonl(Path('experiment_log') / name / 'main/prompts.jsonl')
    raw = read_jsonl(Path('experiment_log') / name / 'main/responses.jsonl')
    selected = [(i, r, p) for i, (r, p) in enumerate(zip(raw, prompts), 1)
                if r['condition'] == condition and r['variant'] == 'clean']
    assert len(inputs) == len(selected) == 40
    for position, (item, (line, response, prompt)) in enumerate(zip(inputs, selected)):
        assert item['replay_position'] == position and item['source_response_line'] == line
        assert item['case_id'] == response['case_id'] == prompt['case_id']
        assert item['source_condition'] == condition == response['condition'] == prompt['condition']
        assert item['prompt'] == prompt['prompt']
        assert hashlib.sha256(item['prompt'].encode()).hexdigest() == item['prompt_sha256'] == response['prompt_sha256']
        assert item['sampling_seed'] == response['sampling_seed']
        assert len(item['prompt_token_ids']) == response['prompt_tokens']
        assert item['original_text_sha256'] == hashlib.sha256(response['text'].encode()).hexdigest()
    return inputs, {c['case_id']: c for c in read_jsonl(data)}


def gates(scores):
    exact = sum(s['strict_exact_table'] is True for s in scores)
    valid = sum(s['strict_format_valid'] is True for s in scores)
    return {'n': len(scores), 'exact_tables': exact, 'valid_outputs': valid,
            'required_exact_tables': 36, 'required_valid_outputs': 38,
            'pass': len(scores) == 40 and exact >= 36 and valid >= 38}


def verify_output_association(item, output):
    assert output.request_id == str(item['replay_position']), 'Engine request ID mismatch'
    assert list(output.prompt_token_ids) == item['prompt_token_ids'], 'Actual prompt token IDs mismatch'
    assert output.prompt is None or output.prompt == item['prompt'], 'Returned prompt mismatch'
    assert len(output.outputs) == 1, 'More than one completion'
