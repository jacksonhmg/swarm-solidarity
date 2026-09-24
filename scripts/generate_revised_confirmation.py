#!/usr/bin/env python3
"""Generate fresh confirmation records once; reuse the existing training dataset."""
import json
import subprocess
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.benign_audit import evaluation_cases
from swarm_solidarity.data import write_jsonl
from revised_support import LOG, CONFIG, DATA, sha, write_json

assert not subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip(), 'Commit generator/protocol first'
assert not DATA.exists(), 'No reroll of evaluation records'
config = json.loads(CONFIG.read_text())
assert json.loads((LOG/'supervision_gap.json').read_text())['description_confirmed']
write_jsonl(DATA, evaluation_cases(config['evaluation_data_seed'], 200))
training = Path('data/train/corrective-corrective-1000.jsonl')
write_json(LOG/'dataset_manifest.json', {'protocol_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'evaluation_seed': config['evaluation_data_seed'], 'scenarios': 200, 'variants': 800,
    'training_dataset_reused_without_changes': True, 'evaluation_note_templates_reused_from_010': True,
    'files': {str(p): sha(p) for p in (DATA, training)}})
