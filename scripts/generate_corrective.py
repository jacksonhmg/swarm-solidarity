#!/usr/bin/env python3
"""Generate the predeclared training/final sets once; no model execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.corrective import training_arms,evaluation_cases
from swarm_solidarity.data import write_jsonl


def main():
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise SystemExit('Commit protocol and generator before dataset generation')
    config=json.loads(Path('configs/corrective-comparison.json').read_text())
    paths=[Path(f'data/train/corrective-{a}-1000.jsonl') for a in config['arms']]
    paths.append(Path('data/final/corrective-200.jsonl'))
    assert not any(p.exists() for p in paths),'Refusing dataset reroll'
    arms=training_arms(config['training_data_seed'])
    for a,p in zip(config['arms'],paths):write_jsonl(p,arms[a])
    write_jsonl(paths[-1],evaluation_cases(config['evaluation_data_seed'],200))
    manifest={'protocol_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'training_seed':config['training_data_seed'],'evaluation_seed':config['evaluation_data_seed'],
        'training_arms':2,'examples_per_arm':1000,'final_scenarios':200,'final_variants':800,
        'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    Path('experiment_log/010_corrective_comparison/dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Two fixed training arms and 200 final scenarios generated once.')


if __name__=='__main__':main()
