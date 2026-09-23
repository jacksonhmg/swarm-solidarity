#!/usr/bin/env python3
"""One saved clean-only stage, with passive request/token instrumentation."""
import argparse
import dataclasses
import datetime as dt
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from swarm_solidarity.feasibility import row_diagnostics
from reproduction_support import (LOG, EXECUTION, STAGES, sha, read_jsonl, write_json,
                                  validate_inputs, gates, verify_output_association)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def plain(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [plain(x) for x in value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if hasattr(value, 'to_dict'):
        return plain(value.to_dict())
    return repr(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=STAGES, required=True)
    stage = parser.parse_args().stage
    freeze = json.loads((LOG / 'execution_freeze.json').read_text())
    for f, digest in freeze['files'].items():
        assert sha(f) == digest, 'Frozen input changed: ' + f
    inputs, cases = validate_inputs(stage)
    config = json.loads(Path('configs/prepared-evaluation.json').read_text())
    if stage == '005_clean':
        a = EXECUTION / '004_replay'
        metadata = json.loads((a / 'metadata.json').read_text())
        assert metadata['status'] == 'complete' and sha(a / 'responses.jsonl') == metadata['responses_sha256']
        assert sha(a / 'scores.jsonl') == metadata['scores_sha256']
        assert gates(read_jsonl(a / 'scores.jsonl'))['pass'], '004 failed; second stage forbidden'
    training = json.loads(Path('experiment_log/004_task_preparation/training/metadata.json').read_text())
    for f, digest in training['terminal_adapter_files'].items():
        assert sha(Path(config['adapter_path']) / f) == digest
    expected_merge = json.loads(Path('experiment_log/004_task_preparation/training/merge.json').read_text())
    actual_merge = json.loads((EXECUTION / 'merge.json').read_text())
    assert actual_merge['files'] == expected_merge['files']
    for f, digest in expected_merge['files'].items():
        assert sha(Path(config['weights_path']) / f) == digest
    # Exclusive creation also blocks a retry after any partial stage failure.
    out = EXECUTION / stage
    out.mkdir(parents=False, exist_ok=False)
    import torch
    import msgspec
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    start = time.monotonic()
    gpu = torch.cuda.get_device_name(0)
    assert gpu == 'NVIDIA H100 PCIe', 'No substitute hardware permitted'
    meta = {'status': 'started', 'stage': stage, 'started_at': now(), 'gpu': gpu,
            'python': platform.python_version(), 'platform': platform.platform(),
            'torch_cuda_version': torch.version.cuda, 'code_revision': Path('.code-revision').read_text().strip(),
            'config': config, 'original_config_sha256': sha('configs/prepared-evaluation.json'),
            'inputs_sha256': sha(LOG / 'inputs' / (stage + '.jsonl')),
            'execution_freeze_sha256': sha(LOG / 'execution_freeze.json'),
            'requested_response_count': 40, 'resumed_response_count': 0,
            'packages': {k: importlib.metadata.version(k) for k in ('torch','vllm','transformers','tokenizers','huggingface-hub')},
            'environment': {k:v for k,v in os.environ.items() if k.startswith(('VLLM_', 'CUDA_', 'NVIDIA_', 'OMP_')) or k in ('TOKENIZERS_PARALLELISM','HF_HUB_DISABLE_TELEMETRY')},
            'instrumentation': 'Pass-through V1 processor wrapper records actual request objects; no sampling or token changes.'}
    write_json(out / 'metadata.json', meta)
    tokenizer = AutoTokenizer.from_pretrained(config['model'], revision=config['model_revision'])
    for item in inputs:
        assert tokenizer.encode(item['prompt']) == item['prompt_token_ids']
        assert len(item['prompt_token_ids']) + config['max_new_tokens'] <= config['max_model_len']
    # Identical LLM constructor arguments to 004. Do not change defaults to improve scores.
    llm = LLM(model=config['weights_path'], tokenizer=config['model'], tokenizer_revision=config['model_revision'],
              dtype=config['dtype'], max_model_len=config['max_model_len'], max_num_seqs=config['batch_size'],
              gpu_memory_utilization=0.85, enforce_eager=config.get('enforce_eager', True),
              seed=config['generation_seed'], disable_log_stats=True)
    engine = llm.llm_engine
    vc = engine.vllm_config
    write_json(out / 'resolved_runtime.json', {'vllm_config': plain(vc), 'vllm_config_repr': repr(vc),
               'generation_config_fields': plain(engine.processor.generation_config_fields),
               'tokenizer_eos_token_id': tokenizer.eos_token_id,
               'tokenizer_class': type(tokenizer).__name__, 'model_load_seconds': time.monotonic()-start})
    assert vc.scheduler_config.max_num_batched_tokens == 16384, '004 effective prefill budget not restored'
    assert vc.scheduler_config.max_num_seqs == 24 and vc.model_config.max_model_len == 12288
    assert vc.model_config.dtype == torch.float16 and not vc.model_config.enforce_eager
    assert vc.cache_config.enable_prefix_caching
    captured = {}
    original_process = engine.processor.process_inputs

    def capture_process(*args, **kwargs):
        answer = original_process(*args, **kwargs)
        prompt_string, request = answer
        index = int(request.request_id)
        assert index not in captured and 0 <= index < 40
        item = inputs[index]
        assert list(request.prompt_token_ids) == item['prompt_token_ids']
        assert prompt_string == item['prompt']
        sp = request.sampling_params
        assert sp.seed == item['sampling_seed']
        assert (sp.temperature, sp.top_p, sp.top_k, sp.min_p, sp.max_tokens, sp.n) == (1.0, 1.0, -1, 0.0, 8192, 1)
        assert set(sp.stop_token_ids) == {151666,151643,151645} and not sp.ignore_eos
        captured[index] = {'request_id': request.request_id, 'case_id': item['case_id'],
                           'prompt_token_ids': list(request.prompt_token_ids), 'eos_token_id': request.eos_token_id,
                           'resolved_sampling_params': plain(msgspec.to_builtins(sp)),
                           'resolved_sampling_params_repr': repr(sp),
                           'arrival_time': request.arrival_time}
        return answer

    engine.processor.process_inputs = capture_process
    all_scores = []
    files = {name: (out / (name+'.jsonl')).open('x') for name in ('responses','prompts','scores','runtime_requests')}
    try:
        for offset in (0,24):
            batch = inputs[offset:offset+24]
            prompts = [r['prompt'] for r in batch]
            params = [SamplingParams(temperature=config['temperature'],top_p=config['top_p'],top_k=config['top_k'],
                       min_p=config['min_p'],stop_token_ids=config['stop_token_ids'],max_tokens=config['max_new_tokens'],
                       seed=r['sampling_seed']) for r in batch]
            tick = time.monotonic()
            outputs = llm.generate(prompts, params, use_tqdm=False)
            elapsed = time.monotonic()-tick
            assert len(outputs) == len(batch)
            for item, output in zip(batch, outputs):
                verify_output_association(item, output)
                index = item['replay_position']
                result = output.outputs[0]
                row = {'case_id':item['case_id'],'scenario_id':item['scenario_id'],'variant':'clean',
                       'condition':item['source_condition'],'stage':stage,'source_response_line':item['source_response_line'],
                       'request_id':output.request_id,'replay_position':index,'text':result.text,
                       'prompt_token_ids':list(output.prompt_token_ids),'generated_token_ids':list(result.token_ids),
                       'finish_reason':result.finish_reason,'stop_reason':result.stop_reason,
                       'sampling_seed':item['sampling_seed'],'prompt_tokens':len(output.prompt_token_ids),
                       'completion_tokens':len(result.token_ids),'prompt_sha256':item['prompt_sha256'],
                       'batch_seconds':elapsed,'batch_size':len(batch),'completed_at':now()}
                score = row_diagnostics(cases[item['case_id']], result.text, result.finish_reason)
                score.update(condition=item['source_condition'],stage=stage,raw_response_line=index+1,
                             request_id=output.request_id,completion_tokens=len(result.token_ids))
                all_scores.append(score)
                for name, value in [('responses',row),('prompts',{'case_id':item['case_id'],'condition':item['source_condition'],'prompt':item['prompt']}),
                                    ('scores',score),('runtime_requests',captured[index])]:
                    files[name].write(json.dumps(value)+'\n')
            for f in files.values():
                f.flush();os.fsync(f.fileno())
            print(json.dumps({'stage':stage,'completed':offset+len(batch),'batch_seconds':elapsed}),flush=True)
    finally:
        for f in files.values():f.close()
    assert len(all_scores)==len(captured)==40
    gate = gates(all_scores)
    write_json(out/'gate.json',gate)
    meta.update(status='complete',finished_at=now(),wall_seconds=time.monotonic()-start,gates=gate,
                **{name+'_sha256':sha(out/(name+'.jsonl')) for name in files},
                resolved_runtime_sha256=sha(out/'resolved_runtime.json'))
    write_json(out/'metadata.json',meta)
    print(json.dumps({'stage':stage,'gate':gate}),flush=True)


if __name__ == '__main__':
    main()
