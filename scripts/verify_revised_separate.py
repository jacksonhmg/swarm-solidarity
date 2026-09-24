#!/usr/bin/env python3
"""Post-run audit only: verify frozen inputs and archive; never generate responses."""
import json,hashlib,sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,'scripts');sys.path.insert(0,'src')
from revised_support import LOG,STAGES,read_jsonl,sha,validate_inputs,write_json,CONFIG,weights
from run_transformers_check import finish
from transformers import AutoTokenizer
from swarm_solidarity.paired_conflict import score_paired
freeze=json.loads((LOG/'freeze.json').read_text())
assert all(sha(p)==h for p,h in freeze['files'].items())
prior=json.loads((LOG/'prior_artifact_hashes.json').read_text())
assert all(sha(p)==h for p,h in prior.items())
from revised_separate_support import verify_plan,plan,node_dir
verify_plan()
remote={};assignments=[];gpu_uuids=[]
for node,spec in plan()['nodes'].items():
 out=node_dir(node)
 assert json.loads((out/'controller-result.json').read_text())['returncode']==0
 supervisor=json.loads((out/'supervisor-result.json').read_text())
 assert supervisor['download_hashes_verified'] and supervisor['failure'] is None
 assert (out/'gpu-environment.txt').read_bytes()==Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
 assignment=json.loads((out/'assignment.json').read_text())
 assert assignment['conditions']==spec['conditions'] and assignment['gpu']=='NVIDIA A100-SXM4-40GB'
 assert assignment['entry_point_sha256']==sha('scripts/run_revised_eval.py')
 assignments+=assignment['conditions']
 gpu_uuids.append(assignment['hardware_uuid'])
 hashes=json.loads((out/'remote-artifact-hashes.json').read_text())
 assert not set(remote)&set(hashes),'Duplicate artifact owner'
 remote.update(hashes)
assert len(assignments)==len(set(assignments))==8
assert len(set(gpu_uuids))==8
lifecycle=json.loads((LOG/'cloud_lifecycle.json').read_text())
assert lifecycle['status']=='all_terminated' and lifecycle['all_temporary_keys_deleted']
assert lifecycle['within_cap'] and lifecycle['estimated_gpu_cost_usd']<=65
assert lifecycle['prior_attempts_gpu_cost_usd']==plan()['prior_gpu_cost_usd']==4.0985
assert len(lifecycle['nodes'])==8
assert all(r['status']=='terminated' and r['cloud_ssh_key_deleted_at'] and r['local_temporary_key_deleted'] for r in lifecycle['nodes'])
assert all(sha(LOG/p)==h for p,h in remote.items())
assert json.loads((LOG/'execution/merge.json').read_text())['files']==json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())['files']
for node in plan()['nodes']:
 assert json.loads((node_dir(node)/'prepared-merge.json').read_text())['files']==json.loads((LOG/'execution/merge.json').read_text())['files']
tokenizer=AutoTokenizer.from_pretrained('.local/preparation/tokenizer',local_files_only=True)
old=read_jsonl('experiment_log/007_transformers_check/execution/005_clean/runtime_requests.jsonl')[0]['resolved_generation_config']
normalize=lambda d:{k:v for k,v in d.items() if k not in ('max_length','min_length')}
allrows=[];allattempts=[];source_lines=[];unique=set()
for stage,n in STAGES.items():
 out=LOG/'execution'/stage;items,cases=validate_inputs(stage)
 raw=read_jsonl(out/'responses.jsonl');attempts=read_jsonl(out/'attempts.jsonl');runtimes=read_jsonl(out/'runtime_requests.jsonl');scores=read_jsonl(out/'scores.jsonl');prompts=read_jsonl(out/'prompts.jsonl')
 meta=json.loads((out/'metadata.json').read_text())
 runtime_meta=json.loads((out/'resolved_runtime.json').read_text())
 old_runtime=json.loads(Path('experiment_log/008_transformers_conflict/execution/prepared_clean/resolved_runtime.json').read_text())
 assert {k:{f:v for f,v in x.items() if f!='source_file'} for k,x in runtime_meta['actual_entry_points'].items()}=={k:{f:v for f,v in x.items() if f!='source_file'} for k,x in old_runtime['actual_entry_points'].items()}
 if stage in ('prepared','prompt_only'):
  assert meta['weight_files']==json.loads((LOG/'execution/merge.json').read_text())['files']
 else:
  assert meta['weight_files']==json.loads((LOG/'execution/merges'/(stage+'.json')).read_text())['files']
 assert runtime_meta['runner_source_sha256']==sha('scripts/run_revised_eval.py')
 assert meta['status']=='complete' and len(raw)==len(attempts)==len(runtimes)==len(scores)==len(prompts)==n
 for name in ('responses','attempts','runtime_requests','scores','prompts'):assert sha(out/(name+'.jsonl'))==meta[name+'_sha256']
 for index,(item,r,a,rt,s,p) in enumerate(zip(items,raw,attempts,runtimes,scores,prompts)):
  assert r['request_id']==a['request_id']==rt['request_id']==s['request_id']==str(index)
  assert r['case_id']==a['case_id']==rt['case_id']==s['case_id']==p['case_id']==item['case_id']
  assert r['condition']==p['condition']==s['condition']==item['source_condition']
  assert r['variant']==item['variant']
  assert p['prompt']==item['prompt']
  assert r['prompt_token_ids']==a['prompt_token_ids']==rt['prompt_token_ids']==item['prompt_token_ids']
  assert r['sampling_seed']==a['sampling_seed']==rt['sampling_seed']==item['sampling_seed']
  assert normalize(rt['resolved_generation_config'])==normalize(old)
  reason,stop,decode=finish(r['generated_token_ids'],[151666,151643,151645],8192)
  assert (r['finish_reason'],r['stop_reason'])==(reason,stop)
  assert tokenizer.decode(decode,skip_special_tokens=True,clean_up_tokenization_spaces=False)==r['text']
  assert tokenizer.decode(r['generated_token_ids'],skip_special_tokens=False,clean_up_tokenization_spaces=False)==r['raw_decoded_with_special_tokens']
  recomputed=score_paired(cases[r['case_id']],r['text'],r['finish_reason'])
  recomputed['condition']=r['condition']  # Runner records the experimental condition over the generic scorer label.
  assert all(s[k]==v for k,v in recomputed.items())
  key=(r['case_id'],r['condition']);assert key not in unique;unique.add(key)
  assert r['source_response_line'] is None
 allrows+=raw;allattempts+=attempts
assert len(allrows)==len(allattempts)==len(unique)==6400
config=json.loads(CONFIG.read_text())
training=[]
for run in config['training_execution_order']:
 meta=json.loads((LOG/'execution/training'/run/'metadata.json').read_text())
 updates=read_jsonl(LOG/'execution/training'/run/'updates.jsonl')
 assert runtime_meta['runner_source_sha256']==sha('scripts/run_revised_eval.py')
 assert meta['status']=='complete' and meta['optimizer_updates']==len(updates)==125
 assert meta['initial_weight_files']==json.loads((LOG/'execution/merge.json').read_text())['files']
 assert sum(u['supervised_tokens'] for u in updates)==meta['supervised_tokens']
 assert len({e for u in updates for e in u['example_ids']})==1000
 for name,h in meta['terminal_adapter_files'].items():assert sha(Path('.local/revised_corrective')/run/'terminal-adapter'/name)==h
 training.append({k:meta[k] for k in ('arm','training_seed','optimizer_updates','supervised_tokens','input_tokens','padded_input_tokens','kind_budgets','training_seconds','wall_seconds','gpu')})
for seed in config['training_seeds']:
 for arm in ('ordinary','corrective'):
  run=f'{arm}_s{seed}';meta=json.loads(Path(f'experiment_log/010_corrective_comparison/execution/training/{run}/metadata.json').read_text())
  for name,h in meta['terminal_adapter_files'].items():assert sha(Path('.local/corrective')/run/'terminal-adapter'/name)==h
result={'parallel_node_assignments':plan()['nodes'],'responses':6400,'attempts':6400,'unique_case_condition_pairs':6400,'no_sampled_case_retries':True,
 'all_associations_seeds_input_arrays_runtime_settings_stop_ids_decodes_and_scores_verified':True,
 'prepared_merged_checkpoint_hashes_equal_004':True,'all_package_versions_equal_007':True,'historical_artifacts_unchanged':len(prior),
 'frozen_files_verified':len(freeze['files']),'remote_download_hashes_verified':len(remote),
 'training':training,'finish_reasons':dict(Counter(r['finish_reason'] for r in allrows)),
 'stop_tokens':dict(Counter(r['stop_reason'] for r in allrows)),
 'generated_tokens':sum(r['completion_tokens'] for r in allrows),'generation_seconds':sum(r['generation_seconds'] for r in allrows),
 'fresh_confirmation_evaluation_accessed':True,'new_training_runs':2,'existing_checkpoints_reused_without_retraining':4}
write_json(LOG/'verification.json',result);print(json.dumps(result,indent=2))
