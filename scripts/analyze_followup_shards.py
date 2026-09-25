"""Verify disjoint original prefixes and suffix shards; use frozen analysis."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import analyze_followups as analysis
from followup_support import LOG, OLD, STAGES, validate_inputs, read_jsonl, sha, write_json, verify_freeze
from swarm_solidarity.paired_conflict import score_paired
from run_followup_eval import finish

ROOT=LOG/'sharding'
STREAMS=('attempts','responses','prompts','scores','runtime_requests')
def blocks(stage):
    p=json.loads((ROOT/'plan.json').read_text());n=p['prefix_counts'][stage];result=[]
    if n:result.append((ROOT/'prefixes'/stage,0,n,'scripts/run_followup_eval.py'))
    for job,s in p['jobs'].items():
        if s['stage']==stage:result.append((ROOT/'execution'/job,s['start'],s['stop'],'scripts/run_followup_shard.py'))
    return sorted(result,key=lambda b:b[1])
def validate(stage):
    from transformers import AutoTokenizer
    items,cases=validate_inputs(stage)
    tokenizer=AutoTokenizer.from_pretrained('.local/preparation/tokenizer',local_files_only=True)
    ref=json.loads((OLD/'execution/prepared/resolved_runtime.json').read_text())
    oldrequest=read_jsonl(OLD/'execution/prepared/runtime_requests.jsonl')[0]
    normalize=lambda x:{k:v for k,v in x.items() if k not in ('max_length','min_length')}
    merged={k:[] for k in STREAMS};expected=0;provenance=[]
    kind='qwen' if stage.startswith('qwen_') else stage.removesuffix('_agent_a')
    weightfiles=json.loads((ROOT/'expected_weights.json').read_text())[kind]
    for path,start,end,runner in blocks(stage):
        assert start==expected,(stage,start,expected)
        meta=json.loads((path/'metadata.json').read_text())
        if runner.endswith('shard.py'):
            assert meta['status']=='complete'
            assert meta['global_start']==start and meta['global_stop']==end
            for name in STREAMS:assert sha(path/(name+'.jsonl'))==meta[name+'_sha256']
        assert meta['weight_files']==weightfiles
        runtime=json.loads((path/'resolved_runtime.json').read_text())
        assert runtime['runner_entry_point']==runner and runtime['runner_source_sha256']==sha(runner)
        for key in ('generate','sample','forward'):
            for field in ('module','qualname','source_sha256'):assert runtime['actual_entry_points'][key][field]==ref['actual_entry_points'][key][field]
        assert runtime['batch_size']==1 and runtime['compilation_disabled'] and runtime['evaluation_mode']
        assert runtime['parameter_dtype']=='float16' and runtime['attention_implementation']=='eager'
        data={name:read_jsonl(path/(name+'.jsonl')) for name in STREAMS}
        assert all(len(v)==end-start for v in data.values())
        for index,(a,r,p,s,rt) in enumerate(zip(*(data[name] for name in STREAMS)),start=start):
            item=items[index]
            assert a['request_id']==r['request_id']==s['request_id']==rt['request_id']==str(index)
            assert all(v['case_id']==item['case_id'] for v in (a,r,p,s,rt))
            assert r['replay_position']==index and s['raw_response_line']==index+1
            assert r['condition']==s['condition']==p['condition']==stage
            assert a['sampling_seed']==r['sampling_seed']==rt['sampling_seed']==item['sampling_seed']
            assert a['prompt_token_ids']==r['prompt_token_ids']==rt['prompt_token_ids']==item['prompt_token_ids']
            assert p['prompt']==item['prompt'] and r['prompt_sha256']==item['prompt_sha256']
            assert normalize(rt['resolved_generation_config'])==normalize(oldrequest['resolved_generation_config'])
            reason,stop,ids=finish(r['generated_token_ids'],[151666,151643,151645],8192)
            assert (reason,stop)==(r['finish_reason'],r['stop_reason'])
            assert tokenizer.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)==r['text']
            assert tokenizer.decode(r['generated_token_ids'],skip_special_tokens=False,clean_up_tokenization_spaces=False)==r['raw_decoded_with_special_tokens']
            score=score_paired(cases[item['case_id']],r['text'],reason);score['condition']=stage
            assert all(s[k]==v for k,v in score.items())
        for name in STREAMS:merged[name].extend(data[name])
        provenance.append({'path':str(path),'start':start,'stop':end,'runner':runner,'runtime_sha256':sha(path/'resolved_runtime.json'),'files':{name:sha(path/(name+'.jsonl')) for name in STREAMS}})
        expected=end
    assert expected==800 and len({r['case_id'] for r in merged['responses']})==800
    return merged,provenance
def main():
    verify_freeze()
    for p,h in json.loads((ROOT/'freeze.json').read_text())['files'].items():assert sha(p)==h,p
    for p,h in json.loads((ROOT/'prefix_hashes.json').read_text()).items():assert sha(p)==h,p
    validated={};provenance={}
    for stage in STAGES:validated[stage],provenance[stage]=validate(stage)
    for stage,data in validated.items():
        out=LOG/'execution'/stage
        assert not out.exists(),'Original prefixes must be archived before canonical assembly'
        out.mkdir(parents=True)
        for name,rows in data.items():
            (out/(name+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in rows))
        write_json(out/'metadata.json',{'status':'complete','stage':stage,'assembled_from_disjoint_sources':True,'requested_responses':800,'sources':provenance[stage],**{name+'_sha256':sha(out/(name+'.jsonl')) for name in STREAMS}})
        write_json(out/'runtime_provenance.json',{'sources':provenance[stage],'note':'Multiple original/shard runtimes retained individually; no single-runtime provenance fabricated.'})
    # Only replace the validation dispatch with the stronger shard-aware validator.
    # Rendering, scorer, taxonomy, bootstrap, exact tests and contrasts are frozen.
    analysis.validate=lambda stage:(validated[stage]['scores'],validated[stage]['responses'])
    analysis.main()
    write_json(ROOT/'verification.json',{'responses':4000,'original_prefix_responses':sum(json.loads((ROOT/'plan.json').read_text())['prefix_counts'].values()),'no_duplicate_request_ids':True,'all_shards_contiguous_disjoint_complete':True,'original_scientific_freeze_preserved':True,'frozen_statistical_analysis_used':True,'sources':provenance})
if __name__=='__main__':main()
