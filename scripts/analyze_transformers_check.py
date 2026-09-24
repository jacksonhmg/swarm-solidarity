#!/usr/bin/env python3
"""Offline comparisons of the bounded Transformers check; unchanged scorer."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from swarm_solidarity.feasibility import row_diagnostics, ratio_bootstrap
from swarm_solidarity.paired_conflict import bootstrap_draws, scenario_estimate, paired_difference
from analyze_pilot import wilson
from reproduction_support import validate_inputs, STAGES, sha, read_jsonl, write_json, gates

LOG = Path('experiment_log/007_transformers_check')


def main():
    destination = LOG / 'analysis'
    destination.mkdir(exist_ok=True)
    summaries = []
    metrics = ('strict_exact_table', 'strict_format_valid', 'strict_exact_audit', 'table_extractable',
               'table_exact', 'audit_extractable', 'audit_exact', 'length_stop', 'extra_tool_call')
    for stage, (source, _, _) in STAGES.items():
        run = LOG / 'execution' / stage
        if not run.exists():
            continue
        meta = json.loads((run / 'metadata.json').read_text())
        assert meta['status'] == 'complete'
        for name in ('attempts', 'responses', 'prompts', 'scores', 'runtime_requests'):
            assert sha(run / (name + '.jsonl')) == meta[name + '_sha256']
        assert sha(run / 'resolved_runtime.json') == meta['resolved_runtime_sha256']
        inputs, cases = validate_inputs(stage)
        raw, saved, requests = [read_jsonl(run / (name + '.jsonl')) for name in ('responses', 'scores', 'runtime_requests')]
        original = read_jsonl(Path('experiment_log') / source / 'main/responses.jsonl')
        assert len(raw) == len(saved) == len(requests) == 40
        scores, old_scores, pairs = [], [], []
        for i, (item, r, stored, req) in enumerate(zip(inputs, raw, saved, requests)):
            old = original[item['source_response_line'] - 1]
            assert r['case_id'] == req['case_id'] == old['case_id'] == item['case_id']
            assert r['request_id'] == req['request_id'] == str(i)
            assert r['prompt_token_ids'] == req['prompt_token_ids'] == item['prompt_token_ids']
            assert r['sampling_seed'] == req['sampling_seed'] == old['sampling_seed'] == item['sampling_seed']
            current = row_diagnostics(cases[r['case_id']], r['text'], r['finish_reason'])
            before = row_diagnostics(cases[r['case_id']], old['text'], old['finish_reason'])
            assert all(stored[k] == v for k, v in current.items())
            scores.append(current)
            old_scores.append(before)
            pairs.append({'case_id': r['case_id'], 'source_response_line': item['source_response_line'],
                          'response_line': i+1, 'original': before, 'transformers': current,
                          'text_byte_identical': old['text'].encode() == r['text'].encode()})
        draws = bootstrap_draws(40, 2718, 5000)
        estimates = {}
        for key in metrics:
            values = [s[key] for s in scores]
            n = sum(v is not None for v in values)
            count = sum(v is True for v in values)
            estimates[key] = {'count': count, **scenario_estimate(values, draws),
                              'wilson_ci95_on_scorable': wilson(count, n) if n else None,
                              'original_count': sum(s[key] is True for s in old_scores),
                              'paired_difference_from_original': paired_difference(values, [s[key] for s in old_scores], draws)}
        summary = {'stage': stage, 'gates': gates(scores), 'original_gates': gates(old_scores), 'metrics': estimates,
                   'text_byte_identical_count': sum(p['text_byte_identical'] for p in pairs),
                   'parse_errors': dict(Counter(s['strict_parse_error'] for s in scores if s['strict_parse_error'])),
                   'stop_token_counts': dict(Counter(str(r['stop_reason']) for r in raw)),
                   'generation_seconds': sum(r['generation_seconds'] for r in raw),
                   'completion_tokens': sum(r['completion_tokens'] for r in raw),
                   'conditional_exact_row_accuracy': ratio_bootstrap([s['exact_rows'] or 0 for s in scores],
                       [s['expected_rows'] if s['table_extractable'] else 0 for s in scores])}
        if stage == '004_replay':
            vllm = read_jsonl(Path('experiment_log/006_reproduction/execution/004_replay/scores.jsonl'))
            assert [s['case_id'] for s in vllm] == [s['case_id'] for s in scores]
            summary['a100_vllm_gates'] = gates(vllm)
            summary['paired_difference_from_a100_vllm'] = {
                k: paired_difference([s[k] for s in scores], [s[k] for s in vllm], draws)
                for k in ('strict_exact_table', 'strict_format_valid')}
        representatives = []
        seen = set()
        for i, s in enumerate(scores):
            if s['strict_exact_table'] and s['strict_exact_audit']:
                continue
            category = s['strict_parse_error'] or ('incorrect_table' if not s['strict_exact_table'] else 'incorrect_audit')
            if category not in seen:
                seen.add(category)
                representatives.append({'case_id': s['case_id'], 'response_line': i+1,
                                        'category': category, 'score': s, 'raw_text': raw[i]['text']})
        write_json(destination / (stage + '.json'), {'summary': summary, 'paired_cases': pairs,
                                                     'representative_failures': representatives})
        summaries.append(summary)
    assert summaries and summaries[0]['stage'] == '004_replay'
    if not summaries[0]['gates']['pass']:
        assert len(summaries) == 1
        conclusion = 'Transformers failed the original 004 input set; conditional 005 comparison skipped. Stop; cause remains unresolved.'
    elif len(summaries) == 2 and summaries[1]['gates']['pass']:
        conclusion = 'This alternative A100 execution setup meets the unchanged clean gates on both saved sets. This does not identify hardware or a specific vLLM bug as the cause of prior failures.'
    elif len(summaries) == 2:
        conclusion = 'Transformers passed 004 but failed the saved 005 clean set. Stop; sensitivity to input/seed set remains possible, with inputs and seeds not separately isolated.'
    else:
        conclusion = '004 passed; the conditional 005 comparison is incomplete.'
    write_json(destination / 'summary.json', {'stages': summaries, 'conclusion': conclusion,
        'intervals': '5000 whole-scenario paired bootstrap draws, seed 2718; Wilson marginal intervals. Unknown diagnostics not imputed.',
        'seed_caveat': 'Equal seeds across implementations do not imply identical sampled outputs.',
        'corrective_training_paused': True, 'exact_h100_reproduction_untested': True})
    print(json.dumps({'stages': [{'stage': s['stage'], 'gates': s['gates']} for s in summaries], 'conclusion': conclusion}))


if __name__ == '__main__':
    main()
