"""Row-level diagnostics for the new task; original strict scoring stays intact."""
from collections import Counter
import random

from .data import FIELDS, expected_records
from .diagnostics import (final_content, markdown_tables, one_json_object,
                          score_diagnostic, strip_fence, valid_rows)
from .scoring import score


def independent_table(case, raw):
    diagnostic = score_diagnostic(case, raw, "replay_json_audit")
    try:
        body = strip_fence(final_content(raw))
    except ValueError:
        return diagnostic, None
    if diagnostic["extra_tool_call"]:
        return diagnostic, None
    obj = one_json_object(body)
    rows = obj.get("records") if obj is not None else None
    if valid_rows(rows, FIELDS):
        return diagnostic, rows
    # Explicit new diagnostic coverage: a lone Markdown table is independently
    # scorable even when JSON was requested. It still fails the JSON format gate.
    # Never choose between JSON and Markdown answers or repair partial JSON.
    if "{" not in body and "}" not in body:
        tables = markdown_tables(body, FIELDS)
        if len(tables) == 1 and tables[0][0] is not None:
            md = score_diagnostic(case, raw, "replay_markdown_audit")
            for key in ("table_extractable", "table_exact", "table_row_f1", "audit_extractable", "audit_schema_valid", "audit_exact"):
                diagnostic[key] = md[key]
            return diagnostic, tables[0][0]
    return diagnostic, None


def row_diagnostics(case, raw, finish_reason=None):
    strict = score(case, raw)
    diagnostic, predicted = independent_table(case, raw)
    diagnostic["length_stop"] = finish_reason == "length"
    result = {**diagnostic, "strict_format_valid": strict["parse_valid"],
              "strict_parse_error": strict["parse_error"], "strict_exact_table": strict["exact_table"],
              "strict_exact_audit": strict["exact_audit"], "expected_rows": strict["expected_rows"],
              "strict_correct_rows": strict["correct_rows"], "predicted_rows": None,
              "exact_rows": None, "missing_completed_ids": None, "included_running_ids": None,
              "duplicate_ids": None, "unknown_ids": None, "wrong_fields": None,
              "inclusion_decisions_correct": None, "inclusion_decisions_total": None}
    if predicted is None:
        return result
    key = lambda r: tuple(r[f] for f in FIELDS)
    gold = expected_records(case)
    expected_counter, predicted_counter = Counter(map(key, gold)), Counter(map(key, predicted))
    evidence = {r["id"]: r for r in case["records"]}
    ids = Counter(r["id"] for r in predicted)
    missing = [r["id"] for r in gold if r["id"] not in ids]
    running = [r["id"] for r in case["records"] if r["status"] == "running" and r["id"] in ids]
    wrong = [{"id": r["id"], "field": f, "expected": evidence[r["id"]][f], "actual": r[f]}
             for r in predicted if r["id"] in evidence for f in FIELDS if f != "id" and r[f] != evidence[r["id"]][f]]
    result.update(predicted_rows=len(predicted), exact_rows=sum((expected_counter & predicted_counter).values()),
                  missing_completed_ids=missing, included_running_ids=running,
                  duplicate_ids={k:v for k,v in ids.items() if v>1},
                  unknown_ids=[r["id"] for r in predicted if r["id"] not in evidence], wrong_fields=wrong,
                  inclusion_decisions_correct=sum((r["id"] in ids) == (r["status"] == "completed") for r in case["records"]),
                  inclusion_decisions_total=len(case["records"]))
    return result


def ratio_bootstrap(numerators, denominators, seed=2718, repetitions=5000):
    """Resample whole scenarios, not correlated rows; conditional on extraction."""
    if not numerators or sum(denominators) == 0:
        return None
    rng = random.Random(seed)
    samples = []
    for _ in range(repetitions):
        indices = rng.choices(range(len(numerators)), k=len(numerators))
        denominator = sum(denominators[i] for i in indices)
        if denominator:
            samples.append(sum(numerators[i] for i in indices)/denominator)
    samples.sort()
    return {"value": sum(numerators)/sum(denominators), "numerator": sum(numerators),
            "denominator": sum(denominators), "n_scenarios": len(numerators),
            "scenario_bootstrap_ci95": [samples[int(.025*len(samples))],samples[min(len(samples)-1,int(.975*len(samples)))]]}
