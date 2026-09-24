"""Frozen 010 paths, identities and associations; no model execution."""
import hashlib
import json
from pathlib import Path
from reproduction_support import sha,read_jsonl,write_json

LOG=Path('experiment_log/010_corrective_comparison')
EXECUTION=LOG/'execution'
CONFIG=Path('configs/corrective-comparison.json')
CONDITIONS=('prepared','prompt_only','ordinary_s41031','corrective_s41031','ordinary_s41032','corrective_s41032')
STAGES={c:800 for c in CONDITIONS}


def validate_inputs(stage):
    assert stage in CONDITIONS
    interface='prompt_only' if stage=='prompt_only' else 'prepared'
    items=read_jsonl(LOG/'inputs'/(interface+'.jsonl'))
    cases={c['case_id']:c for c in read_jsonl('data/final/corrective-200.jsonl')}
    assert len(items)==len(cases)==800 and len({i['case_id'] for i in items})==800
    for position,item in enumerate(items):
        c=cases[item['case_id']]
        assert item['replay_position']==position
        assert item['source_condition']==interface
        assert item['scenario_id']==c['scenario_id'] and item['variant']==c['variant']
        assert item['prompt_sha256']==hashlib.sha256(item['prompt'].encode()).hexdigest()
        assert item['prompt_token_sha256']==hashlib.sha256(json.dumps(item['prompt_token_ids']).encode()).hexdigest()
        item['source_condition']=stage
    return items,cases


def weights(stage):
    config=json.loads(CONFIG.read_text())
    if stage in ('prepared','prompt_only'):
        path=Path(config['initial_weights'])
        expected=json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
        assert json.loads((EXECUTION/'merge.json').read_text())['files']==expected
    else:
        path=Path('.local/corrective')/stage/'merged-terminal'
        expected=json.loads((EXECUTION/'training'/stage/'merge.json').read_text())['files']
    for name,digest in expected.items():assert sha(path/name)==digest,name
    return str(path),expected


def verify_freeze():
    freeze=json.loads((LOG/'freeze.json').read_text())
    for path,digest in freeze['files'].items():assert sha(path)==digest,path
    return freeze
