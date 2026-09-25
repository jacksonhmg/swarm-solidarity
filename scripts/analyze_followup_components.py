"""Offline supplementary tables using the frozen follow-up scores and paired tests."""
from collections import Counter
import json
from pathlib import Path
from analyze_followups import bootstrap_draws, paired_test
from followup_support import LOG, IDENTITY, read_jsonl, sha, write_json


def matched_clean(out):
    source = out / 'classified_scores.jsonl'
    if not source.exists():
        return
    rows = read_jsonl(source)
    ids = sorted({r['scenario_id'] for r in rows})
    assert len(ids) == 200
    lookup = {(r['scenario_id'], r['condition'], r['variant']): r for r in rows}
    assert len(lookup) == len(rows)
    draws = bootstrap_draws(200, 2718, 5000)
    effects = []
    lines = ['# Planned contrasts with matched clean cases', '',
             'These supplement the original renderer with the within-condition contrasts already specified in analysis_plan.json. Scores, denominators, 5,000 scenario bootstrap draws (seed 2718), and exact paired tests are unchanged. No new success criterion. Differences below are conflict minus clean; strict success has the appropriate exact audit for each variant.', '',
             '| Condition | Conflict | Target preservation difference, pp (95% CI) | Scorable pairs | Strict joint difference, pp (95% CI) |',
             '|---|---|---:|---:|---:|']
    def fmt(e):
        low, high = e['scenario_bootstrap_ci95']
        return f"{100*e['value']:+.1f} [{100*low:+.1f}, {100*high:+.1f}]"
    for condition in sorted({r['condition'] for r in rows}):
        for variant in ('falsification', 'omission'):
            metrics = {k: paired_test([lookup[s, condition, variant][k] for s in ids],
                                     [lookup[s, condition, 'clean'][k] for s in ids], draws)
                       for k in ('target_preserved', 'strict_table_plus_exact_audit')}
            effects.append({'condition': condition, 'variant': variant, 'reference': 'clean', 'metrics': metrics})
            target = metrics['target_preserved']
            lines.append(f"| {condition} | {variant} | {fmt(target)} | {target['scorable_n']}/200 | {fmt(metrics['strict_table_plus_exact_audit'])} |")
    write_json(out / 'matched_clean_effects.json', {'source_sha256': sha(source), 'scenario_ids': ids, 'contrasts': effects})
    (out / 'matched_clean_effects.md').write_text('\n'.join(lines) + '\n')


def qwen_discordants():
    source = LOG / 'classified_scores.jsonl'
    rows = read_jsonl(source)
    lookup = {(r['case_id'], r['condition']): r for r in rows}
    components = ('strict_format_valid', 'table_exact', 'target_preserved', 'audit_schema_valid',
                  'audit_exact', 'correct_incident_report', 'reporting_category', 'observed_compliance')
    cases = []
    for case_id in sorted({r['case_id'] for r in rows if r['variant'] in ('falsification', 'omission')}):
        q, w = lookup[case_id, 'qwen_human'], lookup[case_id, 'prepared']
        if q['strict_table_plus_exact_audit'] == w['strict_table_plus_exact_audit']:
            continue
        cases.append({'case_id': case_id, 'variant': q['variant'],
                      'strict_winner': 'qwen_human' if q['strict_table_plus_exact_audit'] else 'prepared',
                      'qwen_human': {k: q[k] for k in components},
                      'prepared': {k: w[k] for k in components}})
    omission = [r for r in cases if r['variant'] == 'omission']
    write_json(LOG / 'strict_discordant_components.json', {
        'status': 'Exploratory saved-score decomposition; original strict criterion unchanged.',
        'source_sha256': sha(source), 'cases': cases,
        'omission_summary': {
            'strict_winners': dict(Counter(r['strict_winner'] for r in omission)),
            'both_entire_tables_correct': sum(r['qwen_human']['table_exact'] is True and r['prepared']['table_exact'] is True for r in omission),
            'qwen_only_strict_with_prepared_invalid_audit': sum(r['strict_winner'] == 'qwen_human' and not r['prepared']['audit_schema_valid'] for r in omission)}})


if __name__ == '__main__':
    matched_clean(LOG)
    matched_clean(IDENTITY)
    qwen_discordants()
