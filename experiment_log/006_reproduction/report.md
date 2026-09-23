# Reproduction check — stopped because matching hardware was unavailable

**No GPU was rented and no responses were generated. Additional GPU spend: $0.**
At 2026-09-23 21:50:28 UTC, Lambda listed the required `gpu_1x_h100_pcie` at
$3.29/hour but returned **no regions with available capacity**. In accordance
with the instruction, the check stopped without substituting hardware or
launching a capacity monitor. The forty-case 004 replay and conditional forty-case
005 clean comparison were not run. Experiment 005 remains closed and corrective
training remains paused. See [capacity.json](capacity.json).

## Offline execution findings

The audit covers all 40 requests from 004 and all 320 requests from 005, using
their console logs, saved prompts/responses, recorded source hashes, merge
manifests, package lists and saved scores. It found a previously unreported
**effective runtime difference**, despite identical LLM constructor arguments.

| Execution detail | Experiment 004 | Experiment 005 | Evidence |
|---|---|---|---|
| GPU | H100 PCIe 80GB | A100 SXM4 40GB | Metadata and `nvidia-smi` |
| Resolved `max_num_batched_tokens` | **16,384** | **8,192** | Actual scheduler startup logs |
| Allocated GPU KV-cache capacity | **424,944 tokens** | **183,440 tokens** | Actual engine startup logs |
| Submitted batches | Clean-only, 24 + 16 | Thirteen mixed batches of 24, then 8 | Saved order, counts and batch timings |
| Prepared merged model | Same 13 file hashes, including three weight shards | Identical | Merge manifests and loader hash checks |
| Python packages | 149 pinned versions | Identical list | Saved environments |
| NVIDIA driver / reported CUDA | 570.148.08 / 12.8 | Same | Saved `nvidia-smi` |
| Engine | vLLM 0.10.2 V1, FP16, one GPU, Flash Attention | Same | Engine logs |
| Graphs / caching | Level 3 compilation; piecewise graphs; prefix caching; chunked prefill | Same | Resolved engine log |
| Max sequences / context / GPU utilization | 24 / 12,288 / 0.85 | Same | Constructor and engine logs |
| Sampling request | Temperature 1, top-p 1, top-k −1, min-p 0; 8,192 output tokens | Same | Recorded runner source and configuration |
| Explicit stop IDs | 151666, 151643, 151645; EOS enabled | Same | Sampling call sites and model/tokenizer metadata |
| Finish reasons | 40 `stop` | 314 `stop`, 6 `length` | Raw responses |
| Saved `stop_reason` field | Null for all 40 | Null for all 320 | Raw responses; exact terminal token unavailable |

Both runs used the same CPU FP32 adapter merge followed by FP16 saved weights,
then loaded those weights without a runtime LoRA switch. The preserved local
adapter hashes still match. Both used PyTorch-native top-p/top-k sampling because
FlashInfer was unavailable. Logged graph capture sizes were identical:
48, 40, 32, 24, 16, 8, 4, 2, 1. No loader or scorer change was found.

The pinned vLLM source selects its default prefill budget using GPU memory and
device name, including a specific A100 branch. This accounts for the **setting
difference** in the logs; it does not establish that this setting caused the
performance decline. See [vLLM 0.10.2 engine defaults](https://github.com/vllm-project/vllm/blob/v0.10.2/vllm/engine/arg_utils.py#L1650).

The sampling objects were explicitly constructed in both runners, rather than
taken from `LLM.get_default_sampling_params()`. The pinned V1 processor clones
these supplied objects and updates EOS handling; it does not replace the supplied
temperature/top-p/top-k with the model generation-config defaults. This is a
**source-derived expectation**, not an archived dump of each resolved sampling
object. See [the V1 processor](https://github.com/vllm-project/vllm/blob/v0.10.2/vllm/v1/engine/processor.py#L383)
and [sampling parameter handling](https://github.com/vllm-project/vllm/blob/v0.10.2/vllm/sampling_params.py#L444).

## Request association, tokens and postprocessing

The saved request order exactly matches each runner's seed-17 shuffle, including
all batch boundaries. Every saved prompt hash, case/condition/scenario identity,
recorded token count and per-request sampling seed passes verification. The seed
formula is `(17 + int(sha256(scenario_id)[:8], 16)) mod 2**31`. Each experiment has
40 distinct scenario seeds; 005 reuses each seed for all eight related responses.
Fresh 005 scenario IDs therefore change the seed set as well as the clean inputs.

Pinned vLLM assigns sequential request IDs and returns completed outputs sorted
by numeric request ID. This supports the runners' positional pairing of jobs,
prompts and returned outputs. The saved responses then map to scores by case ID
and condition. **All 360 saved scores were reproduced offline without a scoring
change; no saved association mismatch was found.** The full trace is in
[request_associations.jsonl](request_associations.jsonl). See
[vLLM request ordering](https://github.com/vllm-project/vllm/blob/v0.10.2/vllm/entrypoints/llm.py#L1456).

There is an archival limit: neither runner saved the actual engine request IDs,
input token arrays, generated token arrays or fully resolved per-request sampling
objects. Thus the expected IDs in the trace are reconstructed from source/order,
not directly observed original IDs. An engine-internal association or tokenization
fault cannot be retrospectively excluded with the same certainty as a recorded
ID/token comparison. Original generated tokens and the precise terminating token
cannot be recovered reliably from detokenized text.

The exact saved prompt strings were copied into two 40-request replay manifests.
Their token IDs were reconstructed using the pinned tokenizer; default encoding
and `add_special_tokens=False` produce identical arrays and match every recorded
prompt length. These are **reconstructed inputs**, not originally archived arrays.
No records or prompt text were regenerated. A future authorized replay would need
to assert actual engine input IDs against these arrays and save raw output IDs.

Both runners saved `output.outputs[0].text` directly, with no additional cleanup.
The unchanged strict scorer uses the text after the last `</think>`, trims
whitespace/an optional whole-answer JSON fence, and parses a single JSON object.
Independent extraction remains conservative; neither path repairs facts or
reconstructs answers from reasoning. These boundaries are the same in 004 and
005, and their source hashes match the original metadata.

## One exact paired-test supplement

This supplement concerns only 005's strict **target preserved + correct report**
metric on falsification. The 40 scenario pairs contain four prompt-only successes
with prepared failure, zero prepared-only successes, zero shared successes and
36 shared operational failures. Invalid output remains an operational failure,
not an inferred misconduct label.

| Measurement | Result |
|---|---|
| Original paired difference, preserved | +10.0 percentage points |
| Original whole-scenario bootstrap 95% interval, preserved | [2.5, 20.0] percentage points |
| Discordant pairs | 4 versus 0 |
| Two-sided exact McNemar / conditional binomial p-value | **0.125** |

Under equal probabilities for the two directions of discordance,
`p = 2 × (1/2)^4 = 0.125`. No mid-p adjustment or post-hoc one-sided test is used.
With only four discordant pairs, this does not reject the paired null at 5%.
The empirical percentile bootstrap interval's exclusion of zero does not override
that exact result. The original descriptive estimates remain unchanged; no other
metrics were searched. See [exact_paired_test.json](exact_paired_test.json).

## What remains unresolved

The evidence identifies an effective execution difference and rules out a saved
prompt/order/score mismatch at the level verifiable from the archives. It does
**not** distinguish failure to reproduce 004, sensitivity to 005's new clean
input/seed set, or a performance difference associated with 005's execution.
Hardware, resolved scheduling/KV capacity, batch composition and input/seed sets
were not isolated. No causal assignment to hardware or batching is justified.

**Stop recommendation:** retain the closed 005 result and keep corrective training
paused. Matching hardware unavailability is the reason this reproduction check
cannot answer the remaining question. No competence or byte-identity result is
claimed for an unexecuted replay. No new settings, task revision, preparation,
training, final held-out evaluation or additional generation was performed.

The archived [offline audit](offline_audit.json), [identity checks](identity_checks.json)
and input manifests preserve the diagnostic evidence. Offline reproduction of the
audit uses `HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false .local/preparation/venv/bin/python scripts/inspect_reproduction.py`;
that script performs no network requests or inference. The separate capacity
query is recorded once, and no cloud resource needs cleanup.
