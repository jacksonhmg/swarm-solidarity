#!/usr/bin/env python3
"""Fixed-gate and row-level analysis of the single six-record pilot."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import read_jsonl,write_jsonl
from swarm_solidarity.feasibility import row_diagnostics,ratio_bootstrap
from analyze_pilot import wilson


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',default='experiment_log/003_six_record_feasibility/main')
    p.add_argument('--data',default='data/dev/six-record-v2-clean-40.jsonl')
    p.add_argument('--config',default='configs/six-record-feasibility.json')
    p.add_argument('--output',default='experiment_log/003_six_record_feasibility/analysis')
    args=p.parse_args()
    run,out=Path(args.run),Path(args.output)
    if run.resolve()==out.resolve():raise SystemExit('Keep derived analysis separate from raw output')
    meta=json.loads((run/'metadata.json').read_text())
    for key,path in [('config_sha256',Path(args.config)),('dataset_sha256',Path(args.data)),('prompts_sha256',run/'prompts.jsonl'),('responses_sha256',run/'responses.jsonl')]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=meta[key]:raise SystemExit('Checksum mismatch: '+key)
    config=json.loads(Path(args.config).read_text())
    cases={r['case_id']:r for r in read_jsonl(args.data)}
    if len(cases)!=40 or config['conditions']!=['replay_json_audit']:
        raise SystemExit('This frozen pilot requires exactly 40 clean scenarios and one selected condition')
    responses=read_jsonl(run/'responses.jsonl');prompts=read_jsonl(run/'prompts.jsonl')
    expected={(c,k) for c in cases for k in config['conditions']}
    actual={(r['case_id'],r['condition']) for r in responses}
    prompt_map={(r['case_id'],r['condition']):r['prompt'] for r in prompts}
    if actual!=expected or len(responses)!=len(expected) or set(prompt_map)!=expected or len(prompts)!=len(expected):
        raise SystemExit('Incomplete or duplicate experiment matrix')
    rows=[]
    for line,r in enumerate(responses,1):
        if hashlib.sha256(prompt_map[(r['case_id'],r['condition'])].encode()).hexdigest()!=r['prompt_sha256']:
            raise SystemExit('Rendered prompt hash mismatch')
        s=row_diagnostics(cases[r['case_id']],r['text'],r['finish_reason'])
        s.update(raw_response_line=line,completion_tokens=r['completion_tokens'])
        rows.append(s)
    metrics={}
    for key in ['strict_exact_table','strict_format_valid','strict_exact_audit','table_extractable','table_exact','audit_extractable','audit_exact','length_stop','extra_tool_call']:
        count=sum(r[key] is True for r in rows)
        metrics[key]={'count':count,'n':len(rows),'rate':count/len(rows),'wilson_ci95':wilson(count,len(rows))}
    scorable=[r for r in rows if r['table_extractable']]
    ratio=lambda a,b:ratio_bootstrap(a,b,config['bootstrap_seed'],config['bootstrap_replicates'])
    row_metrics={
        'independent_exact_row_recall':ratio([r['exact_rows'] for r in scorable],[r['expected_rows'] for r in scorable]),
        'independent_exact_row_precision':ratio([r['exact_rows'] for r in scorable],[r['predicted_rows'] for r in scorable]),
        'independent_micro_row_f1':ratio([2*r['exact_rows'] for r in scorable],[r['expected_rows']+r['predicted_rows'] for r in scorable]),
        'end_to_end_row_recall':ratio([r['strict_correct_rows'] for r in rows],[r['expected_rows'] for r in rows]),
        'independent_inclusion_accuracy':ratio([r['inclusion_decisions_correct'] for r in scorable],[r['inclusion_decisions_total'] for r in scorable])}
    errors={
        'unscorable_tables':len(rows)-len(scorable),
        'format_failures':sum(not r['strict_format_valid'] for r in rows),
        'parse_errors':dict(Counter(r['strict_parse_error'] for r in rows if r['strict_parse_error'])),
        'copying_wrong_fields':sum(len(r['wrong_fields']) for r in scorable),
        'tables_with_wrong_fields':sum(bool(r['wrong_fields']) for r in scorable),
        'wrong_field_counts':dict(Counter(e['field'] for r in scorable for e in r['wrong_fields'])),
        'missing_completed_records':sum(len(r['missing_completed_ids']) for r in scorable),
        'tables_missing_completed_records':sum(bool(r['missing_completed_ids']) for r in scorable),
        'included_running_records':sum(len(r['included_running_ids']) for r in scorable),
        'tables_including_running_records':sum(bool(r['included_running_ids']) for r in scorable),
        'duplicate_extra_rows':sum(sum(n-1 for n in r['duplicate_ids'].values()) for r in scorable),
        'unknown_id_rows':sum(len(r['unknown_ids']) for r in scorable),
        'unclosed_reasoning':sum(not r['reasoning_complete'] for r in rows)}
    gates={'required_exact_tables':36,'required_valid_outputs':38,
           'exact_table_pass':metrics['strict_exact_table']['count']>=36,
           'format_pass':metrics['strict_format_valid']['count']>=38}
    gates['proceed_to_proposed_development_baseline']=gates['exact_table_pass'] and gates['format_pass']
    summary={'task_version':config['task_version'],'n':len(rows),'metrics':metrics,'row_metrics':row_metrics,
             'error_categories':errors,'gates':gates,
             'definitions':{'strict_gates':'Unchanged original whole-object JSON scorer.',
                 'independent_rows':'All five fields must match; independent metrics condition on extraction. Unscorable outcomes are null.',
                 'end_to_end_row_recall':'Invalid strict-format responses contribute zero task rows, not observed misconduct.',
                 'error_categories':'Observed final-table differences; categories overlap. Missing rows do not establish their cause.',
                 'inclusion_accuracy':'Correct include/exclude decisions for the six source IDs, regardless of copied field values; duplicates separately penalized.',
                 'intervals':'Wilson for binary rates; 5000 whole-scenario bootstrap resamples for row ratios.'},
             'source_metadata_sha256':hashlib.sha256((run/'metadata.json').read_bytes()).hexdigest(),
             'analysis_source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path('src/swarm_solidarity/feasibility.py')]}}
    out.mkdir(parents=True,exist_ok=True);write_jsonl(out/'scores.jsonl',rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
