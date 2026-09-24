"""Frozen experiment 011 paths and eight-condition checkpoint provenance."""
import json
from pathlib import Path
from reproduction_support import sha, read_jsonl, write_json

LOG = Path('experiment_log/011_benign_audit_confirmation')
EXECUTION = LOG/'execution'
CONFIG = Path('configs/benign-audit-confirmation.json')
DATA = Path('data/final/benign-audit-confirmation-200.jsonl')
CONDITIONS = ('prepared', 'prompt_only', 'ordinary_s41031', 'corrective_s41031',
              'revised_s41031', 'ordinary_s41032', 'corrective_s41032', 'revised_s41032')
STAGES = {c: 800 for c in CONDITIONS}
OLD = Path('experiment_log/010_corrective_comparison')


def validate_inputs(stage):
    import hashlib
    assert stage in CONDITIONS
    interface = 'prompt_only' if stage == 'prompt_only' else 'prepared'
    items = read_jsonl(LOG/'inputs'/(interface+'.jsonl'))
    cases = {c['case_id']: c for c in read_jsonl(DATA)}
    assert len(items) == len(cases) == len({i['case_id'] for i in items}) == 800
    for index, item in enumerate(items):
        c = cases[item['case_id']]
        assert item['replay_position'] == index and item['source_condition'] == interface
        assert item['scenario_id'] == c['scenario_id'] and item['variant'] == c['variant']
        assert hashlib.sha256(item['prompt'].encode()).hexdigest() == item['prompt_sha256']
        assert hashlib.sha256(json.dumps(item['prompt_token_ids']).encode()).hexdigest() == item['prompt_token_sha256']
        item['source_condition'] = stage
    return items, cases


def adapter_info(stage):
    assert stage not in ('prepared', 'prompt_only')
    revised = stage.startswith('revised_')
    directory = Path('.local/revised_corrective' if revised else '.local/corrective')/stage
    meta = json.loads(((EXECUTION if revised else OLD/'execution')/'training'/stage/'metadata.json').read_text())
    return directory/'terminal-adapter', meta


def weights(stage):
    if stage in ('prepared', 'prompt_only'):
        path = Path('.local/preparation/merged-terminal')
        expected = json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
        assert json.loads((EXECUTION/'merge.json').read_text())['files'] == expected
    else:
        adapter, _ = adapter_info(stage)
        path = adapter.parent/'merged-terminal'
        expected = json.loads((EXECUTION/'merges'/(stage+'.json')).read_text())['files']
        if not stage.startswith('revised_'):
            assert expected == json.loads((OLD/'execution/training'/stage/'merge.json').read_text())['files']
    for name, digest in expected.items():
        assert sha(path/name) == digest, name
    return str(path), expected


def verify_freeze():
    frozen = json.loads((LOG/'freeze.json').read_text())
    for path, digest in frozen['files'].items():
        assert sha(path) == digest, path
    return frozen
