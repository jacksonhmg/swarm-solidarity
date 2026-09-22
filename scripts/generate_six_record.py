#!/usr/bin/env python3
"""Generate the single frozen six-record development dataset; refuse overwrites."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import write_jsonl
from swarm_solidarity.six_record import generate_six


def main():
    config_path=Path('configs/six-record-feasibility.json')
    output=Path('data/dev/six-record-v2-clean-40.jsonl')
    if output.exists():
        raise SystemExit('Frozen dataset already exists; no overwrite or reroll')
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise SystemExit('Commit the task and configuration before data generation')
    config=json.loads(config_path.read_text())
    cases=generate_six(config['dataset_seed'],config['scenario_count'])
    write_jsonl(output,cases)
    record={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'task_frozen_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),
            'data_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'seed':config['dataset_seed'],'count':len(cases),'task_version':config['task_version'],
            'split':'development'}
    Path('experiment_log/003_six_record_feasibility/data_manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
