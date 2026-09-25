"""Frozen follow-ups 013/014; no access to old cloud owner states."""
import hashlib
import json
from pathlib import Path
from reproduction_support import sha, read_jsonl, write_json

LOG=Path('experiment_log/013_qwen_preparation_comparison')
IDENTITY=Path('experiment_log/014_principal_identity')
OLD=Path('experiment_log/011_benign_audit_confirmation')
DATA=Path('data/final/benign-audit-confirmation-200.jsonl')
STAGES={s:800 for s in ('qwen_human','qwen_agent_a','prepared_agent_a','revised_s41031_agent_a','revised_s41032_agent_a')}

def verify_freeze():
    freeze=json.loads((LOG/'freeze.json').read_text())
    for p,h in freeze['files'].items(): assert sha(p)==h,p
    return freeze

def validate_inputs(stage):
    verify_freeze();assert stage in STAGES
    items=read_jsonl(LOG/'inputs'/(stage+'.jsonl'));cases={r['case_id']:r for r in read_jsonl(DATA)}
    assert len(items)==len(cases)==len({i['case_id'] for i in items})==800
    old=read_jsonl(OLD/'inputs/prepared.jsonl')
    for i,(r,o) in enumerate(zip(items,old)):
        assert r['case_id']==o['case_id'] and r['replay_position']==i and r['sampling_seed']==o['sampling_seed']
        assert r['source_condition']==stage
        assert r['prompt_sha256']==hashlib.sha256(r['prompt'].encode()).hexdigest()
        assert r['prompt_token_sha256']==hashlib.sha256(json.dumps(r['prompt_token_ids']).encode()).hexdigest()
        if stage=='qwen_human':assert r['prompt']==o['prompt'] and r['prompt_token_ids']==o['prompt_token_ids']
        else:assert r['prompt']==o['prompt'].replace("the human's","the AI teammate Agent A's")
    return items,cases

def weights(stage):
    kind='qwen' if stage.startswith('qwen_') else stage.removesuffix('_agent_a')
    receipt=json.loads((LOG/'merges'/(kind+'.json')).read_text())
    path=Path(receipt['path']);files=receipt['files']
    for p,h in files.items():assert sha(path/p)==h,p
    if kind=='prepared':assert files==json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
    elif kind.startswith('revised_'):assert files==json.loads((OLD/'execution/merges'/(kind+'.json')).read_text())['files']
    return str(path),files
