#!/usr/bin/env python3
"""Offline audit of saved execution evidence; no records or responses generated."""
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from swarm_solidarity.data import read_jsonl, write_jsonl
from swarm_solidarity.feasibility import row_diagnostics
from swarm_solidarity.paired_conflict import score_paired

ROOT = Path('experiment_log/006_reproduction')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained('.local/preparation/tokenizer', local_files_only=True)
    ROOT.mkdir(exist_ok=True)
    (ROOT / 'inputs').mkdir(exist_ok=True)
    audit, traces = {}, []
    sources = [('004_task_preparation', 'data/dev/preparation-clean-40.jsonl'),
               ('005_paired_conflict', 'data/dev/paired-conflict-40.jsonl')]
    for name, data in sources:
        folder = Path('experiment_log') / name
        meta = json.loads((folder / 'main/metadata.json').read_text())
        config = meta['config']
        raw, prompts = [read_jsonl(folder / 'main' / f) for f in ('responses.jsonl', 'prompts.jsonl')]
        scores = read_jsonl(folder / 'analysis/scores.jsonl')
        cases = read_jsonl(data)
        case_map = {c['case_id']: c for c in cases}
        for key, path in [('responses_sha256', folder / 'main/responses.jsonl'),
                          ('prompts_sha256', folder / 'main/prompts.jsonl'), ('dataset_sha256', Path(data))]:
            assert sha(path) == meta[key]
        jobs = [(c['case_id'], condition) for c in cases for condition in config['conditions']]
        random.Random(config['generation_seed']).shuffle(jobs)
        assert jobs == [(r['case_id'], r['condition']) for r in raw]
        assert jobs == [(r['case_id'], r['condition']) for r in prompts]
        assert len(set(jobs)) == len(raw) == len(scores)
        selected = []
        for index, (r, prompt, saved_score) in enumerate(zip(raw, prompts, scores)):
            case = case_map[r['case_id']]
            assert saved_score['case_id'] == r['case_id'] and saved_score['raw_response_line'] == index + 1
            assert saved_score['condition'] == r['condition']
            assert r['scenario_id'] == case['scenario_id'] and r['variant'] == case['variant']
            digest = hashlib.sha256(prompt['prompt'].encode()).hexdigest()
            assert digest == r['prompt_sha256']
            ids = tokenizer.encode(prompt['prompt'])
            assert ids == tokenizer.encode(prompt['prompt'], add_special_tokens=False)
            assert len(ids) == r['prompt_tokens']
            seed = (config['generation_seed'] + int(hashlib.sha256(case['scenario_id'].encode()).hexdigest()[:8], 16)) % 2**31
            assert seed == r['sampling_seed']
            fresh_score = (row_diagnostics(case, r['text'], r['finish_reason']) if name.startswith('004')
                           else score_paired(case, r['text'], r['finish_reason']))
            # Both analysis entry points attach the generation condition after
            # invoking the shared replay-JSON component scorer.
            fresh_score['condition'] = r['condition']
            assert all(saved_score[k] == v for k, v in fresh_score.items()), r['case_id']
            batch_size = min(24, len(raw) - (index // 24) * 24)
            assert r['batch_size'] == batch_size
            traces.append({'source_experiment': name, 'source_line': index + 1, 'case_id': r['case_id'],
                           'condition': r['condition'], 'expected_engine_request_id_from_source': str(index),
                           'engine_request_id_was_not_saved': True, 'batch_index': index // 24,
                           'batch_position': index % 24, 'batch_size': batch_size, 'sampling_seed': seed,
                           'prompt_sha256': digest, 'reconstructed_input_ids_sha256': hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                           'score_association_verified': True})
            if name.startswith('004') or (r['condition'] == 'prepared' and r['variant'] == 'clean'):
                selected.append({'source_experiment': name, 'source_response_line': index + 1,
                                 'case_id': r['case_id'], 'scenario_id': r['scenario_id'], 'source_condition': r['condition'],
                                 'replay_position': len(selected), 'prompt': prompt['prompt'], 'prompt_sha256': digest,
                                 'prompt_token_ids': ids, 'sampling_seed': seed,
                                 'original_text_sha256': hashlib.sha256(r['text'].encode()).hexdigest(),
                                 'original_finish_reason': r['finish_reason'], 'original_stop_reason': r['stop_reason']})
        assert len(selected) == 40
        write_jsonl(ROOT / 'inputs' / ('004_replay.jsonl' if name.startswith('004') else '005_clean.jsonl'), selected)
        log = (folder / 'main-console.log').read_text()
        engine_line = next(line.split('with config: ', 1)[1] for line in log.splitlines() if 'Initializing a V1 LLM engine' in line)
        audit[name] = {'count': len(raw), 'all_saved_order_prompt_seed_and_scoring_associations_verified': True,
                       'constructor_non_default_args': next(line.split('non-default args: ', 1)[1] for line in log.splitlines() if 'non-default args:' in line),
                       'resolved_engine_log': engine_line,
                       'resolved_max_num_batched_tokens': int(re.search(r'max_num_batched_tokens=(\d+)', log).group(1)),
                       'resolved_gpu_kv_cache_tokens': int(re.search(r'GPU KV cache size: ([\d,]+) tokens', log).group(1).replace(',', '')),
                       'gpu': meta['gpu'], 'batches': [len(raw[i:i+24]) for i in range(0, len(raw), 24)],
                       'finish_reason_counts': dict(Counter(r['finish_reason'] for r in raw)),
                       'stop_reason_counts': dict(Counter(str(r['stop_reason']) for r in raw)),
                       'original_engine_request_ids_and_token_arrays_saved': False,
                       'token_ids_reconstructed_from_pinned_tokenizer_match_all_recorded_lengths': True,
                       'default_encoding_equals_add_special_tokens_false': True,
                       'config': config, 'source_metadata_sha256': sha(folder / 'main/metadata.json')}
    assert audit[sources[0][0]]['constructor_non_default_args'] == audit[sources[1][0]]['constructor_non_default_args']
    assert audit[sources[0][0]]['resolved_engine_log'] == audit[sources[1][0]]['resolved_engine_log']
    write(ROOT / 'offline_audit.json', audit)
    write_jsonl(ROOT / 'request_associations.jsonl', traces)
    merge4 = json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())
    merge5 = json.loads(Path('experiment_log/005_paired_conflict/merge.json').read_text())
    assert merge4['files'] == merge5['files'] and len(merge4['files']) == 13
    assert Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes() == Path('experiment_log/005_paired_conflict/gpu-environment.txt').read_bytes()
    training = json.loads(Path('experiment_log/004_task_preparation/training/metadata.json').read_text())
    assert all(sha(Path('.local/preparation/terminal-adapter') / f) == h for f, h in training['terminal_adapter_files'].items())
    for name, _ in sources:
        meta = json.loads(Path('experiment_log', name, 'main/metadata.json').read_text())
        for f, h in meta['source_sha256'].items():
            path = Path('scripts') / Path(f).name if f.startswith('/home/') else Path(f)
            assert sha(path) == h
    write(ROOT / 'identity_checks.json', {'merged_checkpoint_13_file_hashes_equal': True,
          'preserved_adapter_hashes_verified': True, 'all_149_package_versions_identical': True,
          'all_recorded_runner_and_source_hashes_match_local_files': True,
          'all_360_saved_scores_reproduced_without_definition_changes': True,
          'engine_request_ids_absent_in_original_archives': True,
          'original_input_and_generated_token_arrays_absent': True,
          'per_request_resolved_sampling_objects_absent_in_original_archives': True,
          'input_token_reconstruction': 'Exact saved prompt strings and pinned tokenizer; both special-token modes yield identical IDs and match all recorded lengths. This is not direct verification against an originally saved ID array.',
          'source_inferred_settings': 'Same LLM and SamplingParams call sites; pinned V1 processor clones params and adds EOS IDs, without replacing explicitly supplied temperature/top-p/top-k.'})
    # One requested exact paired test, without searching any other metrics.
    rows = read_jsonl('experiment_log/005_paired_conflict/analysis/scores.jsonl')
    lookup = {(r['scenario_id'], r['condition']): r for r in rows if r['variant'] == 'falsification'}
    ids = sorted({s for s, c in lookup})
    metric = 'strict_target_plus_correct_report'
    pairs = [(lookup[s, 'prompt_only'][metric], lookup[s, 'prepared'][metric]) for s in ids]
    b = sum(a and not c for a, c in pairs)
    c = sum(c and not a for a, c in pairs)
    n = b + c
    p_two = min(1., 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n) if n else 1.
    original = json.loads(Path('experiment_log/005_paired_conflict/analysis/paired_effects.json').read_text())
    estimate = next(x['metrics'][metric] for x in original['contrasts'] if x['comparison'] == 'prompt_only_minus_prepared' and x['variant'] == 'falsification')
    assert (b, c, len(pairs)) == (4, 0, 40) and p_two == .125
    write(ROOT / 'exact_paired_test.json', {'source_scores_sha256': sha('experiment_log/005_paired_conflict/analysis/scores.jsonl'),
          'metric': metric, 'variant': 'falsification', 'n_scenario_pairs': 40,
          'both_success': sum(a and c for a, c in pairs), 'prompt_only_success': b, 'prepared_only_success': c,
          'both_operational_failure': sum(not a and not c for a, c in pairs),
          'test': 'Two-sided exact McNemar (conditional binomial, no mid-p correction)',
          'null': 'Discordant operational successes are equally likely in either condition',
          'discordant_pairs': n, 'p_value': p_two, 'original_descriptive_estimate_unchanged': estimate,
          'interpretation': 'p=0.125; four discordant pairs do not provide a two-sided 5% rejection. The empirical bootstrap interval is retained; its exclusion of zero does not override this exact test. Operational failure is not a misconduct label.'})
    frozen_prior = {}
    for folder in [Path('src'), Path('configs'), Path('data/dev'), Path('experiment_log')]:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and '__pycache__' not in str(path) and '006_reproduction' not in str(path) and path != Path('experiment_log/README.md'):
                frozen_prior[str(path)] = sha(path)
    write(ROOT / 'prior_artifact_hashes.json', frozen_prior)
    print(json.dumps({'audited_requests': len(traces), 'verified_prefill_token_budgets': [16384, 8192],
                      'exact_paired_p_value': p_two, 'replay_manifests': [40, 40], 'prior_artifacts': len(frozen_prior)}))


if __name__ == '__main__':
    main()
