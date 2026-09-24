# Offline checks before rental

Both fixed datasets, all 200 final scenarios and 1,600 prepared/reminder prompt arrays
were checked without a model forward pass. Every expected record matches supplied
evidence; all four variants keep identical evidence. Every worker contributes
completed evidence, and the designated worker contributes both the failed target
and another completed record. No final record IDs, ID-normalized evidence sets or
note templates overlap training/development. Four hundred corrective targets are
all falsification; no improper-omission training demonstrations occur.

The tested aggregation encoder is identical to 004. Actual offset labels and the
collator were exercised in both seeded orders (2,000 microbatches total), including
padding and the actual pinned causal loss shift. Ordinary audit suffixes and stop
tokens are masked; tokens crossing the records/audit boundary are masked whole,
including the records-closing punctuation when BPE joins it to the audit comma.
Corrective and neutral answers supervise the complete answer and stop token.
The 200 shared neutral examples are byte-identical, with 100 explicitly supplied
empty reports and 100 explicitly supplied falsification reports. They require
serialization, not a misconduct judgment.

| Arm | Input tokens/run | Supervised tokens/run | Padded input, seed 41031 | Padded input, seed 41032 |
|---|---:|---:|---:|---:|
| Ordinary | 945,933 | 169,075 | 1,083,632 | 1,087,152 |
| Corrective | 958,080 | 183,062 | 1,100,160 | 1,103,456 |

Corrective loss-token exposure is 8.27% higher despite matching examples/updates.
This is part of the intervention, not a token-budget-matched causal comparison.
All sequences fit without truncation (maximum 1,178 vs limit 2,048).
Representative exact token IDs/labels and decoded continuations are in
`decoded_token_masks.jsonl` and `decoded_token_masks.md`; the pinned native chat
template is `chat_template.jinja`. Both input and label hashes are verified again
by each GPU training process.

One initial offline check stopped because the old diagnostics message helper
intentionally accepts only clean cases. The new corrective branch now directly
uses the identical underlying replay builder, leaving the old clean helper and
all historical code/artifacts unchanged. No dataset was regenerated, no model
ran, and no training/inference setting changed. The initial traceback is preserved
in `../offline_initial_guard/console.log`.

All 64 existing/new offline tests pass, including exact AST comparisons of 007/008
loading, sampling, stopping observers, direct input arrays and decoding calls.
The prepared weights path alone is resolved per condition. Training starts four
fresh processes from the same source hashes, and no intermediate model is selected.

At the verified $1.99/hour A100 rate, measured 008 generation plus input-scaled 004
training with an explicit 2x A100 allowance and 15 minutes of setup/merge/collection
projects 13.25 hours / $26.36. A100 training and trained-model response lengths
remain uncertain. The $30 ceiling is a limit, not a guarantee of completion;
watchdog and remote timeout preserve a bounded partial run if necessary.
