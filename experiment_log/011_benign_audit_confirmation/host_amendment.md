# Authorized eight-GPU execution amendment

The user approved a **$65 additional ceiling** before experiment 011 execution.
This amendment supersedes the eight-separate-host scheduling and $40 budget only.
The original 117-file freeze, datasets, labels, training, inference mathematics,
scoring, analysis and previous results remain unchanged.

Use one available eight-GPU A100 SXM4 server: 80 GB at no more than $22.32/hour,
or the less expensive 40 GB equivalent at no more than $15.92/hour. Prefer 80 GB
when both are available. Each of the eight conditions has its own visible GPU,
process and CPU-affinity partition. Requests within each condition remain serial
and retain the frozen order and seeds. No model spans GPUs; no inference batching,
compilation, quantization or new decoding setting is introduced. Only the two
revised checkpoints are trained. Their training and merge scripts are unchanged.

The host installs the pinned environment and reconstructs the prepared checkpoint
once. Independent condition processes then reuse it. Old adapters and reconstructed
old weights must match their preserved hashes. CPU affinity partitions prevent
eight processes competing for all host CPU threads; this is scheduling isolation,
not a change to the model computation. Hardware and affinity are recorded. A100
80 GB training may differ numerically from 40 GB; this study does not isolate
hardware effects or claim bitwise equivalence of the new adapters.

The additive `run_revised_host_eval.py` differs from the frozen runner only in its
allowed GPU-name check and recorded entry-point/execution-plan fields. A source
equivalence test checks this. The actual Transformers generate/sample/forward
implementations and resolved generation settings must still match 007/008.
The additive verifier replaces eight-host ownership checks with single-host,
eight-condition checks. It also corrects a never-executed provenance assertion
in frozen `verify_revised.py` that expected `run_corrective_eval.py`'s file hash
while the assignment recorded `run_revised_eval.py`. This reporting-verifier
mistake did not affect model work or scoring; the original file is preserved.

The slower recorded 010 condition took 8,012.49 seconds. Adding ten minutes for
concurrent revised training and fifteen for setup/collection gives 158.54 minutes:
**$58.98 on 80 GB**, or **$42.07 on 40 GB**, without assuming a speedup. Output
lengths and setup times remain uncertain; completion is not guaranteed. The
owner-scoped watchdog requests termination at $63, retaining $2 for shutdown.
An independent remote timeout ends computation before that threshold. There is
one launch attempt, no model-work restart, and no automatic fallback after a
rental failure. Partial artifacts are collected and all owned resources cleaned
up if the budget or execution fails. No account-wide termination is permitted.

The complete 6,400-response analysis stays frozen. A partial run is reported as
incomplete, never silently reduced or treated as successful. This amendment and
its code are separately hashed and committed before rental.
