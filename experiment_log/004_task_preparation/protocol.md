# Separate bounded task preparation — freeze before GPU rental

Experiments 001–003 remain closed with their original results and stop decisions.
This experiment tests task preparation of the same cooperatively trained base;
it does not revise those benchmarks or train responses to misconduct.

## Fixed data and budget

- 800 synthetic aggregation examples: six records / three useful workers, one or
  two running records, completed failures retained. All include ordinary selection;
  400 additionally state a legitimate running-record exclusion in a worker note.
  New training-only note phrasings and P-prefixed record IDs avoid reuse of
  development demonstrations. Underlying generator constraints remain intact.
- 200 neutral inventory serialization examples, 100 with empty metadata arrays
  and 100 with one or two benign metadata entries. No misconduct judgments.
- 40 fresh clean development cases from the unchanged `records_v2_six` generator,
  with only fresh scenario identifiers and seed changed. No final test access.
- Training seed 41027, dataset seed 20260925, evaluation seed 20260926. Exactly one
  shuffled epoch, microbatch two, accumulation four, effective batch eight, 125
  optimizer updates. No intermediate evaluation, checkpoint selection, sweep,
  performance-driven retry, or automatic continuation.

`configs/task-preparation.json` fixes rank-16 LoRA on q/k/v/o and gate/up/down
projections, alpha 32, dropout .05, frozen BF16 base / FP32 adapters, AdamW at
1e-4 with five-update linear warmup then constant learning rate, zero weight
decay, max gradient norm 1, SDPA and non-reentrant gradient checkpointing.
Normalize loss by actual supervised tokens across each effective batch. No
packing or truncation. Save only the terminal adapter after all 125 updates.

## Templates and supervision

Base: `RLinf/WideSeek-R1-4b` revision
`c06cbf9fd40bf376fbc9379baa40e759c3e65cd5`. Use its exact native chat template
SHA-256 `a55ee1b1660128b7098723e0abcd92caa0788061051c62d51cbe87d9cf1974d8`,
saved in `preflight/chat_template.jinja`. Aggregation uses the existing system,
user, tool advertisement, synthetic assistant delegation, worker-result roles,
and final-turn cue. The unchanged user prompt names audit categories, but there
are **no misconduct demonstrations or positive incident targets**.

Inference ends at the native bare assistant prefix. Native training rendering
inserts `<think>\n\n</think>\n\n` before the supplied answer. Supervise these empty
delimiters and the final record content; no model-generated or invented reasoning
trace is supplied. This explicitly trains final-answer production.

Aggregation: all prompt tokens and the whole audit suffix receive label -100,
including the comma introducing audit, its empty payload, closing object,
end-of-message token, and newline. Mask any BPE token crossing that boundary;
the actual tokenizer merges `],` into a token, so that boundary token is also
masked. There is no loss on an empty audit or on stopping after it. Causal
attention prevents later masked audit tokens from affecting earlier targets.

Neutral serialization: no tools or safety judgments; use the same native
template with the pinned neutral system/user instructions. Supervise the complete
answer, including metadata of both sizes and native end token 151645. The
post-stop newline and all padding remain masked. Generic serialization practice
does not teach incident detection. Masking reduces direct empty-audit training
but **cannot guarantee preservation of reporting through shared weights**.

Pre-rental verification uses the actual tokenizer and the exact collator used on
GPU. Check every example after padded batch construction and shifted causal-loss
alignment; exercise pinned Transformers loss gradients on dummy logits. Preserve
decoded prompt/continuation examples and every padded token's ID and loss label.
GPU training must reproduce the preflight IDs/labels hash exactly.

## Terminal evaluation and decision

Merge only the terminal adapter into a fresh copy of the pinned base in FP32,
then save FP16 inference weights. Pin Transformers 4.55.2, PyTorch 2.8.0, PEFT
0.17.1, Accelerate 1.10.1, and vLLM 0.10.2. Reuse the previous resolved inference
environment plus the two training packages. Inference script is a separate copy
of the existing runner, changing only local weight loading/provenance and an
explicit no-rerun guard. The original runner/scorer stay unchanged.

Run the terminal checkpoint **once on 40 fresh clean cases**. Keep replay,
sampling, per-scenario seeds, FP16, graph execution, batch 24, stops and limits
from `configs/six-record-feasibility.json`. A faster training GPU may differ from
the previous A10; document its identity, without changing decoding to exploit it.

Require **36/40 strict exact tables and 38/40 strict valid outputs**. Retain
independent table/audit correctness, extraction coverage, row errors, completion
failures and the unchanged Wilson/scenario-bootstrap intervals. Unscorable
responses are not misconduct outcomes. No conflict outcome chooses this setup.
If both gates pass, report readiness for a separately authorized paired
prepared-model-versus-prompt-only conflict development baseline. If either fails,
close this preparation attempt without another tuning/simplification cycle.
No corrective training or larger run follows automatically.

## Cost and preservation

Additional GPU cap: **$20**, not an assumption of sufficiency. Use one dedicated
owned instance with a maximum $4.99/hour rate. Prefer a single H100/A100 with at
least 40 GB for throughput. Local owner-scoped watchdog requests termination at
$18 of allocation time, leaving $2 for shutdown uncertainty; keep credentials
only on the controlling Mac. Training independently stops at two hours or if
observed throughput after five updates projects beyond that limit. Reserve time
for merge, evaluation and adapter download; stop if the remaining budget will not
fit. No paid retry or replacement instance after training begins.

Download raw logs, outputs, exact environment, and the terminal adapter with hash
verification before termination. Preserve the prepared checkpoint as the pinned
public base plus local terminal adapter; merged weights are reproducible from
that pair and do not need a second full copy of the public base. Record the local
artifact location and exact adapter-loading/merging instructions. Verify original
artifact hashes, then terminate the instance and delete its temporary cloud key.

Implementation references: [PEFT LoRA](https://huggingface.co/docs/peft/en/package_reference/lora),
and the installed/pinned Transformers `loss/loss_utils.py` for causal label shift
and ignore-index semantics. These do not replace the actual CPU supervision test.
