#!/usr/bin/env python3
"""Compare completed saved-prompt replay stages to their originals; offline only."""
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.feasibility import row_diagnostics
from swarm_solidarity.paired_conflict import bootstrap_draws, scenario_estimate, paired_difference
from analyze_pilot import wilson
from reproduction_support import LOG, EXECUTION, STAGES, validate_inputs, read_jsonl, sha, write_json, gates


def main():
    destination=LOG/'reproduction_analysis';destination.mkdir(exist_ok=True)
    results=[]
    for stage,(name,_,condition) in STAGES.items():
        run=EXECUTION/stage
        if not run.exists():continue
        meta=json.loads((run/'metadata.json').read_text());assert meta['status']=='complete'
        for f in ('responses','prompts','scores','runtime_requests'):
            assert sha(run/(f+'.jsonl'))==meta[f+'_sha256']
        inputs,cases=validate_inputs(stage)
        raw=read_jsonl(run/'responses.jsonl');assert len(raw)==40
        original=read_jsonl(Path('experiment_log')/name/'main/responses.jsonl')
        rows=[];new_scores=[];old_scores=[]
        for i,(item,r) in enumerate(zip(inputs,raw)):
            old=original[item['source_response_line']-1]
            assert r['case_id']==item['case_id']==old['case_id']
            assert r['request_id']==str(i) and r['prompt_token_ids']==item['prompt_token_ids']
            assert r['sampling_seed']==old['sampling_seed']
            new=row_diagnostics(cases[r['case_id']],r['text'],r['finish_reason'])
            before=row_diagnostics(cases[r['case_id']],old['text'],old['finish_reason'])
            new_scores.append(new);old_scores.append(before)
            rows.append({'case_id':r['case_id'],'source_response_line':item['source_response_line'],
                         'replay_response_line':i+1,'request_id':r['request_id'],
                         'text_bytes_identical':r['text'].encode()==old['text'].encode(),
                         'original_text_sha256':hashlib.sha256(old['text'].encode()).hexdigest(),
                         'replay_text_sha256':hashlib.sha256(r['text'].encode()).hexdigest(),
                         'completion_token_count_identical':r['completion_tokens']==old['completion_tokens'],
                         'finish_reason_identical':r['finish_reason']==old['finish_reason'],
                         'stop_reason_field_identical':r['stop_reason']==old['stop_reason'],
                         'original':before,'replay':new})
        draws=bootstrap_draws(40,2718,5000);metrics={}
        for key in ('strict_exact_table','strict_format_valid','strict_exact_audit','table_extractable',
                    'table_exact','audit_extractable','audit_exact','length_stop','extra_tool_call'):
            a=[r[key] for r in new_scores];b=[r[key] for r in old_scores]
            known=[v for v in a if v is not None];count=sum(v is True for v in known)
            metrics[key]={'replay_count':count,**scenario_estimate(a,draws),
                          'wilson_ci95_on_scorable':wilson(count,len(known)) if known else None,
                          'original_count':sum(v is True for v in b),
                          'paired_replay_minus_original':paired_difference(a,b,draws)}
        summary={'stage':stage,'n':40,'gates':gates(new_scores),'original_gates':gates(old_scores),
                 'metrics':metrics,'text_byte_identical_count':sum(r['text_bytes_identical'] for r in rows),
                 'completion_count_identical':sum(r['completion_token_count_identical'] for r in rows),
                 'finish_reason_identical_count':sum(r['finish_reason_identical'] for r in rows),
                 'stop_reason_field_identical_count':sum(r['stop_reason_field_identical'] for r in rows),
                 'original_token_arrays_not_saved':True,
                 'parse_errors':dict(Counter(s['strict_parse_error'] for s in new_scores if s['strict_parse_error'])),
                 'metadata_sha256':sha(run/'metadata.json')}
        write_json(destination/(stage+'.json'),{'summary':summary,'paired_cases':rows});results.append(summary)
    assert results and results[0]['stage']=='004_replay'
    if not results[0]['gates']['pass']:
        assert len(results)==1
        conclusion='The 004 prompt replay failed its gates on A100. Stop before 005; this does not establish failure to reproduce the original H100 execution.'
    elif len(results)==2:
        conclusion=('Both clean sets pass on A100 with the explicit 16384-token prefill budget and clean-only arrangement, consistent with a difference associated with experiment 005 execution. Prefill budget, batching, instrumentation and other execution details are not individually isolated; this is not an exact H100 reproduction.' if results[1]['gates']['pass'] else '004 replay passes but 005 clean inputs/seeds fail on the same A100 setup, consistent with sensitivity to the new input/seed set on this hardware. Inputs versus seeds are not isolated, and exact H100 reproduction remains untested.')
    else:conclusion='004 replay passes; conditional 005 comparison has not completed.'
    write_json(destination/'summary.json',{'stages':results,'conclusion':conclusion,
        'intervals':'5000 paired whole-scenario bootstrap draws, seed 2718; Wilson accompanies marginal rates. Unknown components not imputed.',
        'hardware_amendment':'A100 SXM4 40GB; explicit max_num_batched_tokens=16384; not an exact H100 reproduction','byte_identity_is_not_a_gate':True,'no_causal_hardware_or_batching_attribution':True})
    print(json.dumps({'stages':[{'stage':s['stage'],'gates':s['gates'],'byte_identical':s['text_byte_identical_count']} for s in results],'conclusion':conclusion}))


if __name__=='__main__':main()
