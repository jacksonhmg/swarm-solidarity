#!/usr/bin/env python3
"""One terminal-preparation evaluation; original inference path with local merged weights."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from swarm_solidarity.data import TOOL, build_messages, read_jsonl


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/prepared-evaluation.json")
    p.add_argument("--data", default="data/dev/preparation-clean-40.jsonl")
    p.add_argument("--output", required=True)
    p.add_argument("--limit-scenarios", type=int)
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text())
    cases = read_jsonl(args.data)
    freeze = json.loads(Path('experiment_log/004_task_preparation/freeze.json').read_text())
    for path, digest in freeze['files'].items():
        assert sha(path) == digest, 'Frozen input changed: ' + path
    if args.limit_scenarios or len(cases) != 40 or config['conditions'] != ['replay_json_audit']:
        raise SystemExit('Exactly one 40-case terminal evaluation is permitted')
    if args.limit_scenarios:
        ids = sorted({x["scenario_id"] for x in cases})[:args.limit_scenarios]
        cases = [x for x in cases if x["scenario_id"] in ids]
    out = Path(args.output)
    if out.exists():
        raise SystemExit("Evaluation already started; no repeated evaluation or resume")
    training = json.loads(Path("experiment_log/004_task_preparation/training/metadata.json").read_text())
    assert training["status"] == "complete" and training["optimizer_updates"] == 125
    for path, digest in training["terminal_adapter_files"].items():
        assert sha(Path(config["adapter_path"]) / path) == digest
    merge = json.loads(Path("experiment_log/004_task_preparation/training/merge.json").read_text())
    for path, digest in merge["files"].items():
        assert sha(Path(config["weights_path"]) / path) == digest
    out.mkdir(parents=True, exist_ok=True)
    metadata_path = out / "metadata.json"
    identity = {"config_sha256": sha(args.config), "dataset_sha256": sha(args.data),
                "limit_scenarios": args.limit_scenarios, "config": config}
    if metadata_path.exists():
        previous = json.loads(metadata_path.read_text())
        if any(previous[k] != v for k, v in identity.items()):
            raise SystemExit("Output directory belongs to a different experiment configuration")
    raw_path = out / "responses.jsonl"
    existing = read_jsonl(raw_path) if raw_path.exists() else []
    completed = {(x["case_id"], x["condition"]) for x in existing}
    if len(completed) != len(existing):
        raise SystemExit("Duplicate case/condition responses")
    jobs = [(case, condition) for case in cases for condition in config["conditions"]]
    random.Random(config["generation_seed"]).shuffle(jobs)
    jobs = [(case, condition) for case, condition in jobs if (case["case_id"], condition) not in completed]
    if not jobs:
        print("All requested outputs already exist.")
        return
    import torch
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    started = time.monotonic()
    metadata = {**identity, "started_at": now(), "python": platform.python_version(),
                "platform": platform.platform(), "gpu": torch.cuda.get_device_name(0),
                "packages": {name: importlib.metadata.version(name) for name in ["torch", "vllm", "transformers", "tokenizers", "huggingface-hub"]},
                "code_revision": Path(".code-revision").read_text().strip() if Path(".code-revision").exists() else subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "source_sha256": {str(x): sha(x) for x in [Path(__file__), *sorted(Path("src/swarm_solidarity").glob("*.py"))]},
                "resumed_response_count": len(completed), "requested_response_count": len(cases) * len(config["conditions"])}
    if metadata_path.exists():
        metadata["previous_attempts"] = previous.get("previous_attempts", []) + [{k: v for k, v in previous.items() if k != "previous_attempts"}]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config["model_revision"])
    metadata["training_metadata_sha256"] = sha("experiment_log/004_task_preparation/training/metadata.json")
    metadata["merge_metadata_sha256"] = sha("experiment_log/004_task_preparation/training/merge.json")
    metadata["chat_template_sha256"] = hashlib.sha256(tokenizer.chat_template.encode()).hexdigest()
    llm = LLM(model=config["weights_path"], tokenizer=config["model"], tokenizer_revision=config["model_revision"],
              dtype=config["dtype"], max_model_len=config["max_model_len"], max_num_seqs=config["batch_size"],
              gpu_memory_utilization=0.85, enforce_eager=config.get("enforce_eager", True), seed=config["generation_seed"], disable_log_stats=True)
    metadata["model_load_seconds"] = time.monotonic() - started
    def sampling_seed(case):
        if config.get("sampling_seed_strategy") == "per_scenario_sha256":
            return (config["generation_seed"] + int(hashlib.sha256(case["scenario_id"].encode()).hexdigest()[:8], 16)) % (2 ** 31)
        return config["generation_seed"]
    prompts_path = out / "prompts.jsonl"
    with raw_path.open("a") as raw_file, prompts_path.open("a") as prompt_file:
        for offset in range(0, len(jobs), config["batch_size"]):
            batch = jobs[offset:offset + config["batch_size"]]
            if config.get("prompt_builder") == "clean_diagnosis_v1":
                from swarm_solidarity.diagnostics import build_diagnostic_messages
                prompts = [tokenizer.apply_chat_template(build_diagnostic_messages(case, condition),
                           tools=[TOOL], tokenize=False, add_generation_prompt=True) for case, condition in batch]
            else:
                prompts = [tokenizer.apply_chat_template(build_messages(case, condition, config.get("context_version", "replay_v1")), tools=[TOOL], tokenize=False, add_generation_prompt=True)
                           for case, condition in batch]
            counts = [len(tokenizer.encode(prompt, add_special_tokens=False)) for prompt in prompts]
            if max(counts) + config["max_new_tokens"] > config["max_model_len"]:
                raise RuntimeError("Prompt plus generation budget exceeds context; refusing silent truncation")
            t0 = time.monotonic()
            params = [SamplingParams(temperature=config["temperature"], top_p=config.get("top_p", 1.0),
                      top_k=config.get("top_k", -1), min_p=config.get("min_p", 0.0),
                      stop_token_ids=config.get("stop_token_ids"), max_tokens=config["max_new_tokens"], seed=sampling_seed(case))
                      for case, condition in batch]
            outputs = llm.generate(prompts, params, use_tqdm=False)
            elapsed = time.monotonic() - t0
            for (case, condition), prompt, output in zip(batch, prompts, outputs):
                result = output.outputs[0]
                row = {"case_id": case["case_id"], "scenario_id": case["scenario_id"], "variant": case["variant"],
                       "condition": condition, "text": result.text, "finish_reason": result.finish_reason,
                       "sampling_seed": sampling_seed(case),
                       "stop_reason": result.stop_reason, "prompt_tokens": len(output.prompt_token_ids),
                       "completion_tokens": len(result.token_ids), "batch_seconds": elapsed, "batch_size": len(batch),
                       "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "completed_at": now()}
                raw_file.write(json.dumps(row) + "\n")
                prompt_file.write(json.dumps({"case_id": case["case_id"], "condition": condition, "prompt": prompt}) + "\n")
            for file in [raw_file, prompt_file]:
                file.flush()
                os.fsync(file.fileno())
            print(json.dumps({"completed": len(completed) + offset + len(batch), "batch_seconds": round(elapsed, 2),
                              "completion_tokens": sum(len(o.outputs[0].token_ids) for o in outputs)}), flush=True)
    metadata.update({"finished_at": now(), "wall_seconds": time.monotonic() - started,
                     "responses_sha256": sha(raw_path), "prompts_sha256": sha(prompts_path)})
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print("Inference complete", flush=True)


if __name__ == "__main__":
    main()
