#!/usr/bin/env python3
"""Generate the one preparation dataset and fresh evaluation set, without inference."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import write_jsonl
from swarm_solidarity.preparation import generate_training
from swarm_solidarity.six_record import generate_six


def main():
    config = json.loads(Path('configs/task-preparation.json').read_text())
    train_path = Path('data/train/task-preparation-1000.jsonl')
    eval_path = Path('data/dev/preparation-clean-40.jsonl')
    if train_path.exists() or eval_path.exists():
        raise SystemExit('Refusing to overwrite a frozen dataset')
    train = generate_training(config['training_data_seed'])
    evaluation = generate_six(config['evaluation_data_seed'], 40)
    for c in evaluation:
        c['scenario_id'] = c['scenario_id'].replace('six-v2-', 'prep-dev-')
        c['case_id'] = c['scenario_id'] + '-clean'
    write_jsonl(train_path, train)
    write_jsonl(eval_path, evaluation)
    inference = json.loads(Path('configs/six-record-feasibility.json').read_text())
    inference.update(experiment=config['experiment'], dataset_seed=config['evaluation_data_seed'],
                     weights_path='.local/preparation/merged-terminal',
                     adapter_path='.local/preparation/terminal-adapter')
    Path('configs/prepared-evaluation.json').write_text(json.dumps(inference, indent=2)+'\n')
    print('Generated exactly 800 aggregation, 200 neutral, and 40 fresh clean development cases.')


if __name__ == '__main__':
    main()
