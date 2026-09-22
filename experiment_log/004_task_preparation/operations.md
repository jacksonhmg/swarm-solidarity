# Execution record

Frozen input commit: `4022640`. All 1,000 tokenized examples and all 500 padded
microbatches passed before rental; 40 tests passed. Earlier experiment artifacts
remain unchanged.

A single H100 PCIe in us-west-3 was selected from live capacity at $3.29/hour.
No pre-existing account instance is used or modified. Credentials stay on the
controlling Mac. The owner-scoped, sleep-inhibited local watchdog requests
termination at $18 of allocation time; the additional spending cap is $20.
The entire remote setup/train/merge/evaluation command has a 150-minute timeout.
Training itself has a two-hour limit and a remaining-time check based only on
throughput, never development performance.

The A10 hardware from experiment 003 is deliberately replaced with a faster H100
for this training run. Inference settings and software versions stay frozen;
hardware identity is recorded because numerical identity across GPUs is not assumed.

Native templates are pinned and saved under `preflight/`. The training prefix
contains native empty reasoning delimiters; inference still starts at the bare
assistant prefix, without adding a prefill.

Launch requested: 2026-09-22T18:18:20.550217+00:00.
