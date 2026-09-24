# One independent Transformers check on A100

Run the exact saved 004 clean prompts first, then the saved 005 prepared-baseline
clean prompts only if 004 reaches 36/40 strict exact tables and 38/40 strict valid
outputs. Maximum 80 responses, one attempt, no failed-case retries. Preserve all
earlier experiments, including the failed cross-hardware A100 replay; exact H100
reproduction remains untested and corrective training remains paused.

Use Transformers 4.55.2 with the same 149-package environment and thirteen
byte-verified merged prepared-checkpoint files. Recreate those files using the
unchanged CPU FP32 merge followed by FP16 save; verify against 004 before loading.
The merge script differs from 006 only in its output-metadata destination.
No training occurs. Load in FP16, `.eval()`, eager attention, on one A100 SXM4 40GB.
Use one request at a time, dynamic KV cache and `disable_compile=True`. Each stage
starts a fresh process; no cache is passed between requests.

Feed the preserved integer token arrays directly to `generate` with an all-ones
attention mask. Never tokenize those inputs, apply a chat template, or insert
special tokens. Preserve the saved request order and per-case seeds. Check the
returned sequence's prompt prefix against the input arrays and retain generated
IDs including the terminal token. As previously documented, these input arrays
were reconstructed from the original saved strings, not archived during 004/005.

The complete generation configuration is frozen in
[`configs/transformers-check.json`](../../configs/transformers-check.json).
Use sampling at temperature 1 and top-p 1; Transformers `top_k=0` and `min_p=None`
disable the filters corresponding to vLLM `top_k=-1` and `min_p=0`. Disable
repetition penalties, forced tokens, sequence biases, suppression, constraints,
minimum-length restrictions, token healing and other distribution modifications.
Use one sequence and no beam search. Set `max_new_tokens=8192`; all saved prompt
lengths plus this limit must fit the existing 12,288-token context bound. Stop on
any of 151666, 151643 or 151645. Set `use_model_defaults=False` explicitly.

In this pinned version, passing a GenerationConfig alone can still inherit model
defaults. The implementation therefore checks the actual prepared configuration,
requires an empty logits-processor list, and records the two stopping criteria
(maximum length and the three EOS IDs) for every request. Offline tests use a tiny
CPU model object solely for configuration methods: no forward pass, generation,
checkpoint inference or sampling is performed. They verify that deliberately
different model defaults do not leak in and that every stop ID and the token
limit are honored. See the pinned
[Transformers generation implementation](https://github.com/huggingface/transformers/blob/v4.55.2/src/transformers/generation/utils.py)
and [configuration source](https://github.com/huggingface/transformers/blob/v4.55.2/src/transformers/generation/configuration_utils.py).

Seed Python/NumPy/PyTorch with each preserved seed immediately before its request.
Equal seeds across implementations are not a guarantee of equal sampled text.
Archive all generated token IDs and a decode retaining special tokens. For the
scorer, exclude only the terminal stop token, then decode with
`skip_special_tokens=True, clean_up_tokenization_spaces=False`. This removes no
factual content or reasoning boundary and performs no answer repair. Record the
actual stop ID or a length-limit finish explicitly; Transformers stop-ID metadata
is not represented as vLLM's historical null `stop_reason` field.

Use the unchanged `row_diagnostics` scorer and strict gate. Preserve independent
table and audit extraction/accuracy, failures, row accuracy and uncertainty
intervals (5,000 paired whole-scenario bootstrap draws, seed 2718, with Wilson
marginal intervals). Unscorable components stay unknown, not misconduct labels.
Freeze code, configuration, inputs, scorer and analysis before any rental.

Use one owner-scoped `gpu_1x_a100_sxm4` at no more than $1.99/hour, a separate
`.local/lambda-transformers-check/state.json`, and duplicate-execution guards.
The additional cap is $10. The sleep-inhibited local watchdog requests shutdown
at $8, retaining $2 margin. The remote setup and both serial stages together have
a 180-minute timeout (extended from the earlier batched runner's 90 minutes for
serial eager execution; at most $5.97 at the allowed rate, excluding boot/cleanup).
Stop if the budget or timeout prevents completion; no replacement run. Download
and verify all artifacts, confirm termination, then delete temporary cloud/local
SSH keys. The earlier availability monitor remains paused.

If both sets pass, conclude only that this alternative A100 execution setup meets
the clean gates on both sets. If either fails, stop with the remaining uncertainty.
Changing backend, attention implementation and execution arrangement together does
not isolate hardware or a specific vLLM defect. No prompt-only/conflict generation,
held-out evaluation, configuration search or corrective training is authorized.
