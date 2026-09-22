#!/usr/bin/env python3
"""Re-score every raw response and write counts, uncertainty, and paired effects."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from swarm_solidarity.data import VARIANTS, read_jsonl, write_jsonl
from swarm_solidarity.scoring import score

BINARY = ["parse_valid", "exact_table", "target_preserved", "target_omitted", "target_falsified",
          "correct_reporting", "false_reporting", "exact_audit", "joint_success"]


def wilson(successes, n):
    if not n:
        return None
    z = 1.959963984540054
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [max(0, center - half), min(1, center + half)]


def cluster_mean(values, repetitions, seed):
    """Each value is one scenario's mean (or paired difference), never one variant."""
    if not values:
        return None
    rng = random.Random(seed)
    samples = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(repetitions))
    return {"mean": statistics.fmean(values), "n_scenarios": len(values),
            "bootstrap_ci95": [samples[int(.025 * repetitions)], samples[min(repetitions - 1, int(.975 * repetitions))]],
            "bootstrap_degenerate": samples[0] == samples[-1]}


def analyze(cases, responses, config):
    lookup = {c["case_id"]: c for c in cases}
    expected = {(case_id, condition) for case_id in lookup for condition in config["conditions"]}
    actual = [(r["case_id"], r["condition"]) for r in responses]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError(f"Incomplete/duplicate/unexpected run: expected {len(expected)} unique outputs, found {len(actual)}")
    scores = []
    for response in responses:
        row = score(lookup[response["case_id"]], response["text"])
        row.update({"condition": response["condition"], "finish_reason": response["finish_reason"],
                    "completion_tokens": response["completion_tokens"], "prompt_tokens": response["prompt_tokens"]})
        scores.append(row)
    groups = {}
    for condition in config["conditions"]:
        groups[condition] = {}
        for variant in VARIANTS:
            rows = [s for s in scores if s["condition"] == condition and s["variant"] == variant]
            groups[condition][variant] = {"n": len(rows), "metrics": {
                metric: {"count": sum(s[metric] for s in rows), "rate": statistics.fmean(s[metric] for s in rows),
                         "wilson_ci95": wilson(sum(s[metric] for s in rows), len(rows))} for metric in BINARY},
                "row_f1": cluster_mean([s["row_f1"] for s in rows], config["bootstrap_replicates"], config["bootstrap_seed"]),
                "other_worker_record_recall": statistics.fmean(s["other_worker_record_recall"] for s in rows),
                "length_truncated": sum(s["finish_reason"] == "length" for s in rows)}
    indexed = {(s["scenario_id"], s["variant"], s["condition"]): s for s in scores}
    scenario_ids = sorted({c["scenario_id"] for c in cases})
    differences = {}
    for variant in VARIANTS:
        differences[variant] = {}
        for metric in ["exact_table", "row_f1", "joint_success", "false_reporting"]:
            values = [float(indexed[(sid, variant, "prompt_only")][metric]) - float(indexed[(sid, variant, "original")][metric]) for sid in scenario_ids]
            differences[variant][metric] = cluster_mean(values, config["bootstrap_replicates"], config["bootstrap_seed"])
    targeted = {}
    macro = {}
    for condition in config["conditions"]:
        targeted[condition] = {}
        for variant, metric in [("falsification", "target_falsified"), ("omission", "target_omitted")]:
            pairs = [(indexed[(sid, "clean", condition)], indexed[(sid, variant, condition)]) for sid in scenario_ids]
            valid = [(a, b) for a, b in pairs if a["parse_valid"] and b["parse_valid"]]
            induced = [(a, b) for a, b in valid if a["target_preserved"]]
            targeted[condition][variant] = {"n_total_pairs": len(pairs), "n_valid_pairs": len(valid),
                "clean_errors": sum(a[metric] for a, b in valid), "conflict_errors": sum(b[metric] for a, b in valid),
                "clean_target_preserved_pairs": len(induced), "induced_errors": sum(b[metric] for a, b in induced),
                "paired_error_delta": cluster_mean([int(b[metric]) - int(a[metric]) for a, b in valid], config["bootstrap_replicates"], config["bootstrap_seed"])}
        macro[condition] = {}
        for metric in ["exact_table", "row_f1", "parse_valid"]:
            # Average four related variants within each scenario BEFORE resampling.
            values = [statistics.fmean(indexed[(sid, variant, condition)][metric] for variant in VARIANTS) for sid in scenario_ids]
            macro[condition][metric] = cluster_mean(values, config["bootstrap_replicates"], config["bootstrap_seed"])
    gates = {condition: {
        "parse_valid_gate_pass": statistics.fmean(s["parse_valid"] for s in scores if s["condition"] == condition) >= config["parse_valid_gate"],
        "clean_exact_table_gate_pass": groups[condition]["clean"]["metrics"]["exact_table"]["rate"] >= config["clean_exact_table_gate"],
    } for condition in config["conditions"]}
    generation_seconds = sum(r["batch_seconds"] / r["batch_size"] for r in responses)
    summary = {"n_scenarios": len(scenario_ids), "n_responses": len(responses), "groups": groups,
               "paired_prompt_minus_original": differences, "matched_targeted_errors": targeted,
               "scenario_cluster_macro": macro, "competence_gates": gates,
               "parse_errors": dict(Counter(s["parse_error"] for s in scores if s["parse_error"])),
               "finish_reasons": dict(Counter(r["finish_reason"] for r in responses)),
               "usage": {"prompt_tokens": sum(r["prompt_tokens"] for r in responses),
                         "completion_tokens": sum(r["completion_tokens"] for r in responses),
                         "generation_batch_seconds": generation_seconds,
                         "aggregate_output_tokens_per_second": sum(r["completion_tokens"] for r in responses) / generation_seconds},
               "failures": [{k: s[k] for k in ["case_id", "condition", "parse_error", "exact_table", "exact_audit", "finish_reason"]}
                            for s in scores if not s["exact_table"] or not s["exact_audit"]]}
    return scores, summary


def render(summary):
    lines = ["# Pilot results (generated)", "", f"{summary['n_scenarios']} development scenarios; {summary['n_responses']} responses.", "",
             "Rates use all responses as their denominator. Invalid output is a task failure; observed reporting/error metrics must be read alongside validity.", "",
             "| Condition | Variant | Valid | Exact table | Row F1 | Correct report | False report | Joint success |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for condition, variants in summary["groups"].items():
        for variant, group in variants.items():
            m = group["metrics"]
            frac = lambda metric: f"{m[metric]['count']}/{group['n']}"
            conflict = variant in ("falsification", "omission")
            lines.append(f"| {condition} | {variant} | {frac('parse_valid')} | {frac('exact_table')} | {group['row_f1']['mean']:.3f} | "
                         f"{frac('correct_reporting') if conflict else '—'} | {frac('false_reporting')} | {frac('joint_success') if conflict else '—'} |")
    lines += ["", "## Uncertainty", "", "Binary intervals below are Wilson 95% intervals. Paired differences and scenario-cluster bootstrap results are in `summary.json`; saturated/degenerate bootstrap intervals do not establish equivalence.", "",
              "| Condition | Variant | Exact-table 95% CI | Joint-success 95% CI | False-report 95% CI |", "|---|---|---|---|---|"]
    for condition, variants in summary["groups"].items():
        for variant, group in variants.items():
            interval = lambda metric: "–".join(f"{v:.1%}" for v in group["metrics"][metric]["wilson_ci95"])
            joint = interval('joint_success') if variant in ('falsification', 'omission') else '—'
            lines.append(f"| {condition} | {variant} | {interval('exact_table')} | {joint} | {interval('false_reporting')} |")
    lines += ["", "## Matched errors", "", "Only pairs with valid output in both clean and conflict versions establish observed request-induced errors.", "",
              "| Condition | Conflict | Valid pairs | Clean errors | Conflict errors | Induced errors / clean-target-correct pairs |", "|---|---|---:|---:|---:|---:|"]
    for condition, variants in summary["matched_targeted_errors"].items():
        for variant, item in variants.items():
            lines.append(f"| {condition} | {variant} | {item['n_valid_pairs']} | {item['clean_errors']} | {item['conflict_errors']} | {item['induced_errors']}/{item['clean_target_preserved_pairs']} |")
    lines += ["", "## Runtime and integrity", "", "```json", json.dumps({k: summary[k] for k in ["usage", "finish_reasons", "parse_errors", "competence_gates"]}, indent=2), "```", "",
              f"Cases with imperfect table or audit: {len(summary['failures'])}. See `summary.json` and `scores.jsonl` for the exact case IDs.", ""]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/pilot.json")
    p.add_argument("--data", default="data/dev/pilot.jsonl")
    p.add_argument("--run", required=True)
    p.add_argument("--limit-scenarios", type=int)
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text())
    cases = read_jsonl(args.data)
    if args.limit_scenarios:
        ids = sorted({c["scenario_id"] for c in cases})[:args.limit_scenarios]
        cases = [c for c in cases if c["scenario_id"] in ids]
    run = Path(args.run)
    metadata = json.loads((run / "metadata.json").read_text())
    for key, path in [("config_sha256", args.config), ("dataset_sha256", args.data),
                      ("responses_sha256", run / "responses.jsonl"), ("prompts_sha256", run / "prompts.jsonl")]:
        if metadata[key] != hashlib.sha256(Path(path).read_bytes()).hexdigest():
            raise SystemExit(f"Provenance mismatch: {key}")
    if metadata["limit_scenarios"] != args.limit_scenarios:
        raise SystemExit("Scenario limit differs from run metadata")
    responses = read_jsonl(run / "responses.jsonl")
    prompts = read_jsonl(run / "prompts.jsonl")
    prompt_map = {(row["case_id"], row["condition"]): row["prompt"] for row in prompts}
    response_keys = {(row["case_id"], row["condition"]) for row in responses}
    if len(prompt_map) != len(prompts) or set(prompt_map) != response_keys:
        raise SystemExit("Prompt/response identities do not match exactly")
    for row in responses:
        prompt = prompt_map[(row["case_id"], row["condition"])]
        if hashlib.sha256(prompt.encode()).hexdigest() != row["prompt_sha256"]:
            raise SystemExit("Rendered prompt checksum mismatch")
    scores, summary = analyze(cases, responses, config)
    write_jsonl(run / "scores.jsonl", scores)
    (run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (run / "results.md").write_text(render(summary))
    print(json.dumps({"n_responses": summary["n_responses"], "failures": len(summary["failures"]), "gates": summary["competence_gates"]}))


if __name__ == "__main__":
    main()
