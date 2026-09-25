# Execution and supervision record

This records the completed training and the execution arrangements for experiment
011. The original protocol and successive infrastructure amendments remain
historical artifacts; their earlier spending limits are not the final authorized
limit. The final cumulative ceiling is $65, with a $62 termination trigger.

## What changed in supervision

The proposed gap was confirmed from actual token labels reconstructed through
010's tokenizer, encoder and collator, matching all four saved GPU training hashes.
In the original corrective arm, 400 task-specific benign examples masked the
empty audit and termination, while 400 falsification examples supervised the
nonempty report and termination. Separately, neutral serialization supervised
100 empty and 100 nonempty answers. The ordinary controls masked all 800 benign
audit suffixes. See [decoded original masks](supervision_gap_masks.md).

The revised runs use the same 1,000 input examples, token arrays, order and padding.
Each benign example adds seven supervised tokens, including the indivisible BPE
token `],` at the records/audit boundary and the native end token. Trailing
whitespace and padding remain masked. The 400 falsification and 200 neutral label
arrays are unchanged; no improper-omission demonstrations are present. Both seeded
batch constructions and the causal-loss shift were checked before rental. See
[decoded revised masks](preflight/decoded_token_masks.md),
[mask checks](preflight/mask_checks.json) and [update weights](preflight/update_loss_weights.jsonl).

| Actual tokens per run | Original corrective | Revised corrective |
|---|---:|---:|
| Input | 958,080 | 958,080 |
| Benign supervised | 71,694 | 74,494 |
| Falsification supervised | 86,511 | 86,511 |
| Neutral supervised | 24,857 | 24,857 |
| Total supervised | 183,062 | 185,862 |
| Padded input, seed 41031 | 1,100,160 | 1,100,160 |
| Padded input, seed 41032 | 1,103,456 | 1,103,456 |

The additional 2,800 targets per run are a 1.53% increase, not equal-token training.
Loss is normalized over supervised tokens in each effective batch. Average
benign/falsification/neutral loss shares change from 39.49/46.41/14.10% to
40.29/45.80/13.92% for 41031, and 39.38/46.55/14.07% to
40.19/45.93/13.88% for 41032. Original supervised tokens consequently receive
0.96251–1.0 or 0.96914–1.0 times their old within-batch weight, respectively.

## Actual training

Both runs independently started from the same verified merged prepared checkpoint
from 004, based on `RLinf/WideSeek-R1-4b` revision
`c06cbf9fd40bf376fbc9379baa40e759c3e65cd5`. Neither starts from an old corrective
adapter. Both completed one epoch, 1,000 examples and exactly 125 updates;
microbatch two with four accumulation steps gives effective batch eight.

Training uses a BF16 base, FP32 LoRA, SDPA attention and gradient checkpointing.
LoRA rank 16, alpha 32 and dropout 0.05 apply to q/k/v/o/gate/up/down projections
(33,030,144 trainable parameters). AdamW uses learning rate 0.0001, betas
0.9/0.999, epsilon 1e-8, zero weight decay, gradient clipping 1, five warmup updates
and a constant subsequent schedule. No packing or truncation is used. These
settings and the example order match the original corrective runs.

| Seed | Actual training GPU | Training seconds | Wall seconds | Peak allocated bytes |
|---|---|---:|---:|---:|
| 41031 | A100 SXM4 40 GB | 390.905 | 398.100 | 14,152,957,952 |
| 41032 | A100 SXM4 80 GB | 365.880 | 372.819 | 14,153,465,856 |

Both terminal adapters are preserved and hash-verified under
`.local/revised_corrective/revised_s41031/terminal-adapter` and
`.local/revised_corrective/revised_s41032/terminal-adapter`. The four existing
010 adapters were reused without retraining. [Loading instructions](checkpoint_loading.md)
specify reconstruction of the prepared checkpoint and application of one adapter.
The actual training metadata and all 125 update records per seed are in
`execution/training/`.

## Actual inference and comparison

The executed inference entry point is `scripts/run_revised_host_eval.py`, launched
by `scripts/run_revised_recovery_node.py` independently on eight GPU instances.
The evaluator's host-compatible hardware guard and provenance fields are the only
differences from the frozen single-node evaluator. Embedded host-plan references
are compatibility metadata; [the recovery plan](hardware_recovery/plan.json),
per-node assignments and GPU UUIDs identify actual execution.

Inference uses Transformers 4.55.2, Torch 2.8.0, PEFT 0.17.1 and tokenizers 0.21.4:
evaluation mode, FP16, eager attention, one request at a time per GPU, no
compilation or vLLM. Saved prompt arrays are fed directly without templating or
added special tokens. Sampling is explicit: temperature 1, top-p 1, top-k 0,
no min-p/epsilon/eta truncation, typical-p 1, repetition penalty 1 and one beam.
The output limit is 8,192 tokens; stop IDs are 151666, 151643 and 151645.
The frozen per-case seeds and request order are preserved. Raw generated IDs
retain stop tokens; decoding removes only a terminal stop, skips special tokens
and disables whitespace cleanup. Resolved per-request settings and actual
Transformers entry-point source hashes are retained, not merely package versions.

Seven conditions use A100 SXM4 40 GB. Revised seed 41032 uses the provider-delivered
A100 SXM4 80 GB for training and inference. This hardware difference can introduce
numerical differences; it limits exclusive causal attribution of that same-seed
comparison to the supervision change. No hardware cause has been isolated.

The 200 fresh underlying scenarios have four matched variants each. Records and
IDs do not overlap earlier training/development/evaluation data. The 20 evaluation
note templates deliberately reuse 010's distribution under the no-prompt-change
constraint, while remaining disjoint from training. This is a fresh confirmation
motivated by 010, not an untouched original test or a new-template transfer test.
All eight conditions are evaluated on those same scenarios; no condition or
checkpoint is selected using intermediate performance.

The frozen analysis uses 5,000 shared resamples of 200 whole scenarios, seed 2718,
and exact two-sided McNemar tests. The eight primary omission comparisons receive
the predeclared Holm adjustment. Other tests are descriptive and nominal. Seeds
remain separate; 6,400 responses do not constitute 6,400 independent scenarios.
Five-point non-inferiority requires the paired 95% interval's lower endpoint to
exceed −5 percentage points for strict table-plus-exact-audit success on both
clean and legitimate filtering, separately for each revised seed.

## Infrastructure exceptions and cost accounting

The earlier lost eight-A100 startup has **unknown model-work count**, with no
recoverable outputs. The user explicitly authorized one unchanged infrastructure
retry despite that uncertainty. A no-retry statement for the verified observed
run must not be read as proving zero work in that lost startup. Subsequent
allocation/readiness replacements occurred before affected model dispatch;
usable assignments were retained and observed model work was not restarted.

Prior closed GPU estimates total $9.6705: $0.383833 for the incomplete H100
allocation, $3.714667 for the lost single host, $3.913667 for seven terminated
readiness-failure nodes, and $1.658333 for the terminated prepared allocation.
All prior termination and key-deletion receipts are preserved. The retained
80 GB GPU is counted once, from its original launch, in current execution cost.

The final [lifecycle receipt](cloud_lifecycle.json) adds all eight current nodes,
including setup and cleanup, to prior spending. Cost is a conservative GPU
estimate from launch through first confirmed termination, rounded up to minutes,
not a provider invoice. Unrelated account instances are outside this experiment.
Owner-scoped collectors verify downloads before termination and temporary-key
deletion. No further training, tuning, model substitution or expansion follows.
