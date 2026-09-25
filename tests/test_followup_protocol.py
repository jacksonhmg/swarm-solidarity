import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from followup_support import LOG, OLD, STAGES, read_jsonl

def test_training_implementation_unchanged_except_paths():
    old=Path('scripts/train_preparation.py').read_text()
    expected=old.replace('configs/task-preparation.json','configs/qwen-task-preparation.json').replace('experiment_log/004_task_preparation','experiment_log/013_qwen_preparation_comparison').replace('.local/preparation/terminal-adapter','.local/followups/qwen-terminal-adapter')
    assert expected==Path('scripts/train_qwen_preparation.py').read_text()
    before=json.loads(Path('configs/task-preparation.json').read_text());after=json.loads(Path('configs/qwen-task-preparation.json').read_text())
    allowed={'experiment','model','model_revision','additional_spend_cap_usd','termination_budget_usd','max_hourly_usd'}
    assert {k:v for k,v in before.items() if k not in allowed}=={k:v for k,v in after.items() if k not in allowed}

def test_inference_implementation_unchanged_except_paths_and_provenance():
    old=Path('scripts/run_revised_host_eval.py').read_text()
    expected=old.replace('from revised_support import','from followup_support import').replace("LOG = Path('experiment_log/011_benign_audit_confirmation')","LOG = Path('experiment_log/013_qwen_preparation_comparison')").replace("(('prompt_only' if stage == 'prompt_only' else 'prepared') + '.jsonl')","(stage + '.jsonl')").replace("'scripts/run_revised_host_eval.py'","'scripts/run_followup_eval.py'").replace("LOG / 'host_plan.json'","LOG / 'plan.json'")
    provenance="    if stage.startswith('qwen_'):\n        provenance = json.loads(Path('configs/qwen-task-preparation.json').read_text())\n        config.update(model=provenance['model'], model_revision=provenance['model_revision'])\n"
    assert expected==Path('scripts/run_followup_eval.py').read_text().replace(provenance,'')

def test_exact_identity_changes_and_original_arrays():
    original=read_jsonl(OLD/'inputs/prepared.jsonl')
    for stage in STAGES:
        rows=read_jsonl(LOG/'inputs'/(stage+'.jsonl'));assert len(rows)==800
        for o,r in zip(original,rows):
            for field in ('case_id','scenario_id','variant','sampling_seed','replay_position'):assert o[field]==r[field]
            if stage=='qwen_human':assert o['prompt']==r['prompt'] and o['prompt_token_ids']==r['prompt_token_ids']
            else:
                assert r['prompt']==o['prompt'].replace("the human's","the AI teammate Agent A's")
                assert 'human' not in r['prompt'].lower()

def test_training_masks_equal_original():
    old=json.loads(Path('experiment_log/004_task_preparation/preflight/mask_checks.json').read_text())
    new=json.loads((LOG/'preflight/mask_checks.json').read_text())
    for key in ('encoded_ids_labels_sha256','order_sha256','supervised_tokens','input_tokens_total','chat_template_sha256'):assert new[key]==old[key]

def test_distinct_owner_states_and_bounded_assignments():
    plan=json.loads((LOG/'plan.json').read_text());nodes=plan['nodes']
    assert len({n['state'] for n in nodes.values()})==4
    assert all(n['state'].startswith('.local/lambda-followup-') for n in nodes.values())
    stages=[s for n in nodes.values() for s in n['stages']]
    assert set(stages)==set(STAGES) and len(stages)==5
    assert plan['maximum_new_responses']==sum(STAGES.values())==4000
    assert plan['termination_threshold_usd']==28<plan['new_gpu_cap_usd']==30
