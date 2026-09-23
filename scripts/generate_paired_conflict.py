#!/usr/bin/env python3
"""Generate the frozen development set once; never read final-test assets."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import write_jsonl
from swarm_solidarity.paired_conflict import generate_paired

if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
    raise SystemExit('Commit conditions, generator and scorer before generation')
path=Path('data/dev/paired-conflict-40.jsonl')
if path.exists():raise SystemExit('Refusing to reroll existing development cases')
config=json.loads(Path('configs/paired-conflict.json').read_text())
write_jsonl(path,generate_paired(config['dataset_seed'],config['scenario_count']))
Path('experiment_log/005_paired_conflict/dataset_manifest.json').write_text(json.dumps({
    'protocol_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    'seed':config['dataset_seed'],'scenarios':40,'variants':4,'conditions':2,'responses':320,
    'dataset_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2)+'\n')
print('Generated 40 fresh paired development scenarios / 160 variants, once.')
