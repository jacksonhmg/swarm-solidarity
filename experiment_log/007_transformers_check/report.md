# Independent Transformers check — both clean sets pass

The alternative A100 execution setup meets the unchanged empirical competence
gates on both saved clean sets: **39/40 exact tables and 40/40 valid outputs on
004; 40/40 on both measures on 005**. Exactly eighty responses were sampled,
one per case. The second set ran only after the first passed. Stop after this
report; corrective training remains paused and no larger experiment is launched.

| Execution and saved clean set | Exact tables | Valid outputs | Gate |
|---|---:|---:|---|
| Original 004, vLLM on H100 PCIe | 39/40 | 40/40 | Pass, historical |
| Original 005 prepared baseline, vLLM on A100 | 15/40 | 16/40 | Fail, historical |
| 006 cross-hardware A100 vLLM replay of 004 | 12/40 | 14/40 | Fail, preserved |
| **007 Transformers on A100, saved 004 set** | **39/40** | **40/40** | **Pass** |
| **007 Transformers on A100, saved 005 clean set** | **40/40** | **40/40** | **Pass** |

The gates remain 36/40 exact tables and 38/40 valid outputs, with the original
scorer unchanged. In each new set, table extraction, audit extraction and exact
audit correctness are all 40/40; there are no length-limit finishes, parse
failures or extra-tool-call flags. Exact row accuracy is 179/180 on 004 and
180/180 on 005. No unscorable answer was reconstructed or repaired.

The 95% Wilson interval for 39/40 is **87.1–99.6%**; for each 40/40 measure it is
**91.2–100%**. Paired whole-scenario bootstrap differences versus the 006 A100
replay are +67.5 percentage points for exact tables (95% interval **52.5–82.5**)
and +65.0 points for validity (**50.0–80.0**). On the 005 clean set, differences
from its original prepared baseline are +62.5 points (**47.5–77.5**) and +60.0
points (**45.0–75.0**). These use 5,000 scenario draws, seed 2718. Intervals
describe variation across these cases, not execution-to-execution variability;
the empirical gates do not establish population rates with certainty.
Full independent, paired and row-level intervals are in [analysis/](analysis/).

The sole factual failure is `prep-dev-008-clean`, saved response line 33:
the first row uses **`E001-01` instead of `E008-01`**, while copying that row's
other fields correctly. The result has valid JSON and the correct empty audit,
but fails exact-table scoring. It is the same error in original 004. All forty
004 output texts are byte-identical to that original, including this error;
fourteen 005 texts match their original prepared-baseline outputs. These are
observations, not a guarantee from equal seeds across implementations. No errors
were observed in the new 005 clean set. See the full example in
[004_replay.json](analysis/004_replay.json).

Transformers **4.55.2** loaded the same thirteen byte-verified merged prepared
checkpoint files in FP16, evaluation mode and eager attention. All 149 pinned
package versions match 004. Requests were serial, with dynamic KV cache and
compilation disabled. The saved integer prompt arrays were fed directly with
attention masks; no chat template, tokenization or special-token insertion ran.
The arrays retain the previously documented limitation that they were reconstructed
from original saved prompts, rather than originally archived engine arrays.
Original order and per-case seeds were preserved. Actual request associations,
resolved settings, input/output token arrays and stop IDs are archived in
[execution/](execution/).

Sampling was unrestricted: temperature 1, top-p 1, Transformers top-k 0 and
min-p disabled, with no repetition or other distribution restrictions. Model
generation defaults were explicitly excluded. Maximum output was 8,192 tokens,
stopping on any of 151666, 151643 or 151645. Every sampled response stopped on
151645; 14,995 generated tokens were retained. Scoring text removes only the
terminal stop token, then uses the frozen decode settings. Generation itself took
346.45 seconds on 004 and 346.81 seconds on 005, about 11.6 minutes total.

There was one disclosed **setup assertion repair before any forward pass or
token sampling**. The initial observer wrongly required an empty processor list:
Transformers resolves `min_new_tokens=0` into a minimum-length processor whose
threshold is the prompt length. It is an identity operation at every reachable
decoding length. The initial offline test had omitted that length-resolution
step. The corrected test verifies the actual preparation order and bitwise logit
identity; the observer now records and permits only that inert processor. The
complete inference configuration remained byte-identical. Both code freezes,
the original source, the zero-response abort and its one request-start journal
entry are preserved. Thus there were 81 `generate` entry calls: one aborted during
configuration preparation and eighty that sampled responses. No sampled case
was retried. See [runtime_guard_fix.md](runtime_guard_fix.md) and
[pre_generation_abort/](pre_generation_abort/). The first sampling code commit was
`04b0043`, following initial freeze `505d25f`.

The evidence establishes that **this alternative A100 execution setup meets the
clean gates on both saved input/seed sets**. It does not isolate hardware or a
specific vLLM bug: backend, attention implementation, batching and cache behavior
differ together. Exact reproduction of 004's execution on H100 remains untested,
despite the observed text match. The failed 006 cross-hardware replay and all
earlier conclusions remain unchanged. Correct empty audits on clean cases do not
establish conflict-handling or incident-reporting ability. No prompt-only or
conflict generation, final held-out evaluation, training or configuration search
was performed. No further run is automatic.

The one A100 instance is confirmed terminated, and its temporary cloud and local
SSH keys are deleted. All 36 downloaded files were hash-verified before requesting
termination; all eighty scores reproduce offline. The 208 prior result/source
artifacts remain byte-identical; the experiment catalog only adds this new check.
The $8 watchdog and original 180-minute deadline remained in force. Launch request
to confirmed termination was 31.88 minutes, conservatively rounded to
32 minutes at $1.99/hour: **estimated additional compute cost $1.06**,
below the $10 cap. This includes provisioning and the setup correction; it is an
estimate excluding tax, not an invoice. The earlier monitor remains paused and no
new monitor was created. See [verification](verification.json),
[cloud lifecycle](cloud_lifecycle.json) and [final decision](decision.json).
