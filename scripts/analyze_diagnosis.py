#!/usr/bin/env python3
"""Write independent diagnostics to a new directory; never replace pilot scores."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from swarm_solidarity.data import read_jsonl, write_jsonl
from swarm_solidarity.diagnostics import score_diagnostic


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',required=True)
    p.add_argument('--data',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    run,out=Path(args.run),Path(args.output)
    if run.resolve()==out.resolve():
        raise SystemExit('Use a separate diagnostic analysis directory')
    metadata=json.loads((run/'metadata.json').read_text())
    for key,path in [('dataset_sha256',Path(args.data)),('responses_sha256',run/'responses.jsonl'),('prompts_sha256',run/'prompts.jsonl')]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=metadata[key]:
            raise SystemExit('Checksum mismatch: '+key)
    cases={r['case_id']:r for r in read_jsonl(args.data)}
    responses=read_jsonl(run/'responses.jsonl')
    prompts=read_jsonl(run/'prompts.jsonl')
    prompt_map={(r['case_id'],r['condition']):r['prompt'] for r in prompts}
    identities={(r['case_id'],r['condition']) for r in responses}
    expected={(case,c) for case in cases for c in metadata['config']['conditions']}
    if identities != expected or len(identities)!=len(responses) or len(prompts)!=len(prompt_map) or set(prompt_map)!=identities:
        raise SystemExit('Incomplete or duplicate response/prompt matrix')
    rows=[];groups=defaultdict(list)
    for r in responses:
        if hashlib.sha256(prompt_map[(r['case_id'],r['condition'])].encode()).hexdigest()!=r['prompt_sha256']:
            raise SystemExit('Prompt hash mismatch')
        s=score_diagnostic(cases[r['case_id']],r['text'],r['condition'],r['finish_reason'])
        s['completion_tokens']=r['completion_tokens']
        rows.append(s);groups[(r['condition'],r['variant'])].append(s)
    summaries=[]
    for (condition,variant),items in sorted(groups.items()):
        fields=['table_extractable','format_valid','table_exact','audit_extractable','audit_schema_valid','audit_exact','length_stop','extra_tool_call']
        summary={'condition':condition,'variant':variant,'n':len(items),**{k:sum(r[k] is True for r in items) for k in fields}}
        summary['unclosed_reasoning']=sum(not r['reasoning_complete'] for r in items)
        summary['strict_table_success']=sum(r['table_exact'] is True and r['format_valid'] for r in items)
        summary['table_and_audit_success']=sum(r['table_exact'] is True and r['audit_exact'] is True and r['format_valid'] for r in items)
        summary['completion_tokens']=sum(r['completion_tokens'] for r in items)
        summaries.append(summary)
    out.mkdir(parents=True,exist_ok=True)
    write_jsonl(out/'scores.jsonl',rows)
    summary={'source_run':str(run),'source_metadata_sha256':hashlib.sha256((run/'metadata.json').read_bytes()).hexdigest(),
             'scorer_sha256':hashlib.sha256(Path('src/swarm_solidarity/diagnostics.py').read_bytes()).hexdigest(),'groups':summaries}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':
    main()
