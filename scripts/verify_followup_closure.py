"""Offline completion audit; no cloud mutation or model execution."""
from collections import Counter
import json
from pathlib import Path
from followup_support import LOG, OLD, sha, read_jsonl, verify_freeze, write_json


def main():
    root = LOG / 'sharding'
    finished = json.loads((root / 'finished.json').read_text())
    assert finished['analysis_returncode'] == 0
    verification = json.loads((root / 'verification.json').read_text())
    assert verification['responses'] == 4000 and verification['no_duplicate_request_ids']
    scientific = verify_freeze()
    prior = json.loads((LOG / 'prior_artifact_hashes.json').read_text())
    assert all(sha(p) == h for p, h in prior.items())
    for f in root.rglob('freeze.json'):
        manifest = json.loads(f.read_text())
        assert all(sha(p) == h for p, h in manifest['files'].items()), str(f)
    plan = json.loads((root / 'boot_recovery/execution_state_plan.json').read_text())
    owners = {**plan['prior_states'], **{j: s['state'] for j, s in plan['jobs'].items()}}
    cleanup = []
    for label, path in owners.items():
        state = json.loads(Path(path).read_text())
        assert state['status'] == 'terminated' and state['ssh_key_deleted_at'] and state['first_termination_confirmed_at']
        key = Path(state['private_key_path'])
        assert not key.exists() and not key.with_suffix('.pub').exists()
        cleanup.append({'label': label, 'instance_id': state['instance_id'],
                        'terminated_at': state['first_termination_confirmed_at'],
                        'key_deleted_at': state['ssh_key_deleted_at'], 'local_keys_absent': True})
    assert len({s['instance_id'] for s in cleanup}) == len(cleanup) == 27
    hardware = Counter()
    remote_files = 0
    for job, spec in plan['jobs'].items():
        node = root / 'nodes' / job
        result = json.loads((node / 'supervisor-result.json').read_text())
        assert result['error'] is None and result['controller_result']['returncode'] == 0
        hashes = json.loads((node / 'remote-hashes.json').read_text())
        assert all(sha(p) == h for p, h in hashes.items()), job
        remote_files += len(hashes)
        merge = json.loads((node / 'verified-merge.json').read_text())
        assert merge['files'] == json.loads((root / 'expected_weights.json').read_text())[spec['kind']]
        hardware[json.loads((root / 'execution' / job / 'metadata.json').read_text())['gpu']] += 1
    training = json.loads((LOG / 'training/metadata.json').read_text())
    updates = read_jsonl(LOG / 'training/updates.jsonl')
    assert len(updates) == training['optimizer_updates'] == 125
    assert sum(u['supervised_tokens'] for u in updates) == training['supervised_tokens'] == 161115
    assert len({i for u in updates for i in u['example_ids']}) == 1000
    adapters = [('qwen', Path('.local/followups/qwen-terminal-adapter'), training),
                ('prepared', Path('.local/preparation/terminal-adapter'), json.loads(Path('experiment_log/004_task_preparation/training/metadata.json').read_text()))]
    for name in ('revised_s41031', 'revised_s41032'):
        adapters.append((name, Path('.local/revised_corrective') / name / 'terminal-adapter',
                         json.loads((OLD / 'execution/training' / name / 'metadata.json').read_text())))
    for name, path, metadata in adapters:
        assert metadata['optimizer_updates'] == 125
        assert all(sha(path / p) == h for p, h in metadata['terminal_adapter_files'].items()), name
    cost = finished['cost']
    assert cost['estimated_usd'] < 65 and len(cost['nodes']) == 27
    assert {r['instance_id'] for r in cost['nodes']} == {r['instance_id'] for r in cleanup}
    write_json(LOG / 'cost.json', cost)
    write_json(LOG / 'closure_checks.json', {
        'completed': True, 'new_responses': 4000, 'training_runs': 1, 'qwen_updates': 125,
        'unique_training_examples': 1000, 'actual_supervised_tokens': 161115,
        'scientific_frozen_files': len(scientific['files']), 'historical_files_unchanged': len(prior),
        'all_shard_amendment_freezes_unchanged': True, 'remote_files_reverified': remote_files,
        'shard_hardware': dict(hardware), 'adapters_verified': [a[0] for a in adapters],
        'owners_terminated_and_keys_deleted': cleanup, 'estimated_gpu_usd': cost['estimated_usd'],
        'cost_is_estimate_not_provider_invoice': True,
        'raw_token_request_and_scoring_verification': str(root / 'verification.json'),
        'no_new_model_work_invoked_by_audit': True})
    print(json.dumps({'verified': 4000, 'cleaned_owners': len(cleanup), 'estimated_gpu_usd': cost['estimated_usd']}))


if __name__ == '__main__':
    main()
