# Protocol revision 2 — checkpoint sampling defaults

Recorded on 2026-09-22 UTC after the original 16-response smoke run and 64 flushed
responses from the initial pilot attempt. This is a **development correction**,
not a confirmatory comparison. All original artifacts remain available in
`smoke/` and `greedy_aborted/`, with their original config in
`configs/pilot-greedy.json` and code revision in each run's metadata.

## Reason for the revision

The prompt-only response for `dev-010-clean` repeated reasoning until the 4,096-
token limit and never produced a final answer. On inspection, the checkpoint's
pinned `generation_config.json` specifies sampling (temperature 0.6, top-p 0.95,
top-k 20). The base Qwen3 model card explicitly advises against greedy decoding
in thinking mode because it can produce degradation and endless repetition.
Our original temperature-zero choice therefore was not an appropriate default.

The initial full-pilot attempt was stopped at 2026-09-22T06:36:53 UTC with 64
complete saved responses. An in-flight batch, if present, was canceled. It is
incomplete and must not be represented as a full 40-scenario result. Its task
and audit failures remain part of the development record; they were not deleted
or individually replaced.

## Changes, fixed before the revised run

- Use the checkpoint's temperature 0.6, top-p 0.95, top-k 20, min-p 0, and EOS IDs.
- Use an 8,192-token output limit and 12,288-token context to provide more room
  for reasoning. Continue to record all length stops as failures; no retries or
  forced final answers.
- Use a stable seed per underlying scenario (base 17 plus the first eight hex
  digits of SHA-256 of its ID, modulo 2^31). All four variants and both conditions
  share that scenario's seed. This is one decoding sample per case/condition,
  not an estimate of variability over decoding seeds.
- Increase batch size from 8 to 16 based on observed A100 memory headroom
  (approximately 25.4 GiB available for KV cache). This reduces rental overhead.
  Precision, eager execution, checkpoint, software environment, and GPU stay fixed.
- Run a revised smoke check (`smoke_v2/`) followed by a fresh 320-response run
  (`main/`). Re-run both conditions from scratch; do not combine configurations.

All generated records, prompts, worker requests, expected answers, scoring,
competence thresholds, and analysis methods are unchanged from `protocol.md`.
The committed `configs/pilot.json` is the authoritative revised configuration.
The competence gate still determines whether training should remain deferred.

## Sources

- [Pinned checkpoint generation configuration](https://huggingface.co/RLinf/WideSeek-R1-4b/blob/c06cbf9fd40bf376fbc9379baa40e759c3e65cd5/generation_config.json)
- [Qwen3 thinking-mode guidance](https://huggingface.co/Qwen/Qwen3-4B#best-practices)

The upstream WideSeek evaluation also uses sampling (temperature 1, top-p 1),
but its web-research benchmark setup differs from this synthetic task. We use
the published checkpoint defaults and make no claim of replicating that benchmark.
