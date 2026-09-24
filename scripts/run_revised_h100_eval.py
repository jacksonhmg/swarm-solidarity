#!/usr/bin/env python3
"""One frozen, serial Transformers replay stage; never resumes partial generation."""
import argparse
import datetime as dt
import importlib.metadata
import inspect
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from swarm_solidarity.paired_conflict import score_paired
from revised_support import sha, read_jsonl, write_json, validate_inputs, STAGES, weights

LOG = Path('experiment_log/011_benign_audit_confirmation')
EXECUTION = LOG / 'execution'
CONFIG = Path('configs/transformers-check.json')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if hasattr(value, 'tolist'):
        return value.tolist()
    if value is None or isinstance(value, (bool, str, float, int)):
        return value
    return str(value)


def finish(generated, stop_ids, limit):
    assert 0 < len(generated) <= limit
    assert not any(t in stop_ids for t in generated[:-1]), 'Continued after a stop token'
    if generated[-1] in stop_ids:
        return 'stop', generated[-1], generated[:-1]
    assert len(generated) == limit, 'Unexpected early termination'
    return 'length', None, generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=STAGES, required=True)
    stage = parser.parse_args().stage
    freeze = json.loads((LOG / 'freeze.json').read_text())
    for path, digest in freeze['files'].items():
        assert sha(path) == digest, path
    inputs, cases = validate_inputs(stage)
    config = json.loads(CONFIG.read_text())
    config['weights_path'], weight_hashes = weights(stage)
    out = EXECUTION / stage
    out.mkdir(exist_ok=False)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, set_seed
    assert importlib.metadata.version('transformers') == config['transformers_version']
    assert torch.cuda.device_count() == 1
    assert torch.cuda.get_device_name(0) == 'NVIDIA H100 PCIe'
    started = time.monotonic()
    meta = {'status': 'started', 'stage': stage, 'started_at': now(), 'config': config,
            'code_revision': Path('.code-revision').read_text().strip(),
            'freeze_sha256': sha(LOG / 'freeze.json'),
            'inputs_sha256': sha(LOG / 'inputs' / (('prompt_only' if stage == 'prompt_only' else 'prepared') + '.jsonl')),
            'gpu': torch.cuda.get_device_name(0), 'python': platform.python_version(),
            'platform': platform.platform(), 'torch_cuda_version': torch.version.cuda,
            'packages': {k: importlib.metadata.version(k) for k in ('torch', 'transformers', 'tokenizers', 'huggingface-hub')},
            'environment': {k: v for k, v in os.environ.items() if k.startswith(('CUDA_', 'NVIDIA_', 'OMP_', 'TORCH_')) or k in ('TOKENIZERS_PARALLELISM', 'HF_HUB_DISABLE_TELEMETRY')},
            'requested_responses': len(inputs), 'resumed_responses': 0, 'weight_files': weight_hashes}
    write_json(out / 'metadata.json', meta)
    set_seed(config['generation_seed'])
    tokenizer = AutoTokenizer.from_pretrained(config['weights_path'], local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(config['weights_path'], local_files_only=True,
                                               torch_dtype=torch.float16, attn_implementation='eager')
    model.to('cuda').eval()
    assert not any(m.training for m in model.modules())
    assert {p.dtype for p in model.parameters() if p.is_floating_point()} == {torch.float16}
    assert model.config._attn_implementation == 'eager'
    assert not hasattr(model, '_orig_mod') and getattr(model, '_compiled_call', None) is None
    generation = GenerationConfig.from_dict(config['generation_config'])
    generation.validate()
    runtime = {'model_config': plain(model.config.to_dict()), 'attention_implementation': model.config._attn_implementation,
               'evaluation_mode': not model.training, 'parameter_dtype': 'float16',
               'default_model_generation_config_unused': plain(model.generation_config.to_dict()),
               'requested_generation_config': plain(generation.to_dict()), 'use_model_defaults': False,
               'batch_size': 1, 'compilation_disabled': True, 'model_load_seconds': time.monotonic() - started,
               'input_handling': 'Saved integer arrays directly; no tokenization, chat template or special-token insertion.',
               'output_handling': 'Archive all generated tokens; remove only the terminal stop token before decode. skip_special_tokens=True; clean_up_tokenization_spaces=False.',
               'seed_caveat': 'Equal integer seeds across Transformers and vLLM do not imply identical sampled tokens.'}
    runtime['actual_entry_points'] = {
        name: {'module': fn.__module__, 'qualname': fn.__qualname__,
               'source_sha256': hashlib.sha256(inspect.getsource(fn).encode()).hexdigest(),
               'source_file': inspect.getsourcefile(fn)}
        for name, fn in [('generate', model.generate), ('sample', model._sample), ('forward', model.forward)]}
    runtime['runner_source_sha256'] = sha(__file__)
    runtime['runner_entry_point'] = 'scripts/run_revised_h100_eval.py'
    runtime['execution_plan'] = json.loads((LOG / 'h100_plan.json').read_text())
    write_json(out / 'resolved_runtime.json', runtime)
    current = {}
    original_logits = model._get_logits_processor
    original_stops = model._get_stopping_criteria

    def observe_logits(*args, **kwargs):
        result = original_logits(*args, **kwargs)
        gc = kwargs['generation_config']
        # min_new_tokens=0 resolves to min_length=prompt length. This processor
        # only clones scores at every reachable decoding length; it masks none.
        assert [type(p).__name__ for p in result] == ['MinLengthLogitsProcessor']
        assert result[0].min_length == current['prompt_tokens']
        assert (gc.do_sample, gc.temperature, gc.top_p, gc.top_k, gc.min_p) == (True, 1.0, 1.0, 0, None)
        assert gc.disable_compile and gc.max_new_tokens == 8192 and gc.num_beams == gc.num_return_sequences == 1
        current['resolved_generation_config'] = plain(gc.to_dict())
        current['logits_processors'] = [{'type': type(p).__name__, 'parameters': plain(vars(p)),
                                        'inert_at_all_reachable_decoding_lengths': True} for p in result]
        return result

    def observe_stops(*args, **kwargs):
        result = original_stops(*args, **kwargs)
        assert [type(c).__name__ for c in result] == ['MaxLengthCriteria', 'EosTokenCriteria']
        assert result[0].max_length == current['prompt_tokens'] + 8192
        assert set(result[1].eos_token_id.tolist()) == {151666, 151643, 151645}
        current['stopping_criteria'] = [{'type': type(c).__name__, 'parameters': plain(vars(c))} for c in result]
        return result

    model._get_logits_processor = observe_logits
    model._get_stopping_criteria = observe_stops
    files = {name: (out / (name + '.jsonl')).open('x') for name in ('attempts', 'responses', 'prompts', 'scores', 'runtime_requests')}

    def append(name, row):
        files[name].write(json.dumps(row) + '\n')
        files[name].flush()
        os.fsync(files[name].fileno())

    scores = []
    try:
        for i, item in enumerate(inputs):
            saved = item['prompt_token_ids']
            assert len(saved) + 8192 <= config['max_model_len']
            input_ids = torch.tensor([saved], dtype=torch.long, device='cuda')
            assert input_ids.tolist() == [saved]
            attention_mask = torch.ones_like(input_ids)
            current.clear()
            current.update(request_id=str(i), case_id=item['case_id'], prompt_tokens=len(saved),
                           sampling_seed=item['sampling_seed'], prompt_token_ids=input_ids[0].tolist())
            append('attempts', {**current, 'started_at': now()})
            set_seed(item['sampling_seed'])
            tick = time.monotonic()
            with torch.inference_mode():
                result = model.generate(input_ids=input_ids, attention_mask=attention_mask,
                                        generation_config=generation, use_model_defaults=False, synced_gpus=False)
            sequence = result.sequences[0].tolist()
            assert sequence[:len(saved)] == saved
            generated = sequence[len(saved):]
            reason, stop_id, decode_ids = finish(generated, generation.eos_token_id, generation.max_new_tokens)
            assert 'stopping_criteria' in current and 'resolved_generation_config' in current
            text = tokenizer.decode(decode_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            row = {'case_id': item['case_id'], 'scenario_id': item['scenario_id'], 'variant': item['variant'],
                   'condition': item['source_condition'], 'stage': stage, 'request_id': str(i), 'replay_position': i,
                   'source_response_line': item['source_response_line'], 'text': text,
                   'raw_decoded_with_special_tokens': tokenizer.decode(generated, skip_special_tokens=False, clean_up_tokenization_spaces=False),
                   'prompt_token_ids': saved, 'generated_token_ids': generated, 'sampling_seed': item['sampling_seed'],
                   'prompt_sha256': item['prompt_sha256'], 'prompt_tokens': len(saved), 'completion_tokens': len(generated),
                   'finish_reason': reason, 'stop_reason': stop_id, 'stop_reason_convention': 'Observed terminating token ID, or null on length limit',
                   'generation_seconds': time.monotonic() - tick, 'completed_at': now()}
            score = score_paired(cases[item['case_id']], text, reason)
            score.update(condition=item['source_condition'], stage=stage, request_id=str(i), raw_response_line=i+1, completion_tokens=len(generated))
            append('responses', row)
            append('prompts', {'case_id': item['case_id'], 'condition': item['source_condition'], 'prompt': item['prompt']})
            append('scores', score)
            append('runtime_requests', dict(current))
            scores.append(score)
            print(json.dumps({'stage': stage, 'completed': i+1, 'tokens': len(generated), 'seconds': row['generation_seconds']}), flush=True)
            del result, input_ids, attention_mask
    finally:
        for f in files.values():
            f.close()
    assert len(scores) == STAGES[stage]
    gate = {'n': len(scores), 'checkpoint_selection_or_early_clean_gate': False}
    write_json(out / 'gate.json', gate)
    meta.update(status='complete', finished_at=now(), wall_seconds=time.monotonic()-started, gates=gate,
                resolved_runtime_sha256=sha(out / 'resolved_runtime.json'),
                **{name + '_sha256': sha(out / (name + '.jsonl')) for name in files})
    write_json(out / 'metadata.json', meta)
    print(json.dumps({'stage': stage, 'gate': gate}), flush=True)


if __name__ == '__main__':
    main()
