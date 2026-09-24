# Scheduling and spending amendment, before evaluation

The user explicitly authorized three matching A100s and a **$40 aggregate ceiling**.
This supersedes the original one-host scheduling and $30 budget provisions only.
All original frozen files, data, 500 training updates, terminal checkpoint selection,
inference calls, settings, input arrays, sampling seeds, per-condition request order,
scorer, primary outcome, bootstrap draws and exact tests remain unchanged.
No new training, responses, templates, sweeps or performance-driven retries are added.

Training stays on the original A100. The original bash scheduler was stopped using
SIGSTOP only while its last training child was running. The child continued to its
125th update without interruption. Once all four training runs are complete, the
superseded shell is killed without resuming it; its original controller's nonzero
exit is preserved as an administrative handoff, not a training failure. The final
adapter's first merge is performed explicitly if the stopped shell had not started
it. No evaluation attempts existed at handoff. The old local supervisor is retired
without running its now-inapplicable single-host cleanup/analysis path; the original
per-instance watchdog remains active until its instance is terminated.

Disjoint ownership, 1,600 responses per GPU:

| Node | Complete conditions, serial within node |
|---|---|
| primary | prepared, prompt_only |
| seed41031 | ordinary_s41031, corrective_s41031 |
| seed41032 | ordinary_s41032, corrective_s41032 |

Each additional node uses an A100 SXM4 40GB, the exact pinned environment and the
unchanged `scripts/run_corrective_eval.py`. No batching, vLLM, compilation, attention
change, prompt change, intra-model sharding or concurrent requests on a GPU.
Prepared weights must match 004's 13 file hashes. Each trained merge must match the
first merge on the original GPU host. Each full condition retains the original 800
request order and seeds. All outputs are generated once and have exactly one owner.
Hardware UUID, package manifest, inference source hashes, inputs, outputs and raw
runtime records are captured per node. Identical GPU type and software reduce but
do not prove the absence of all host-level numerical variability.

The independent aggregate watchdog counts original-instance rental from its original
launch, plus both new rentals, rounded up per instance to whole minutes. It requests
termination of all owned active instances at **$38**, leaving $2 for polling/provider
termination lag. No unrelated instance may be touched. Each node has a 360-minute
remote timeout. Each local supervisor downloads only its assigned conditions,
verifies remote hashes, then terminates its own instance and deletes its temporary
SSH key immediately upon completion. A technical failure aborts the remaining
owned jobs; preserve every partial/unsuccessful result without retry.

The original four adapters are downloaded and hash-verified before handoff. Only
adapters and their immutable training receipts are copied to added instances;
original data and protocol files remain frozen. New files form a separate amendment
hash manifest. `verify_corrective_parallel.py` extends provenance checks to three
node receipts and the administrative handoff; its raw-token, association, decoding,
scoring and training verification is copied unchanged from the frozen verifier.
The statistical analysis remains the original `scripts/analyze_corrective.py`.

At the measured 008 throughput, unchanged generation uses 12.35 GPU-hours / $24.58.
Three nodes give approximately 4.12 hours of generation; setup and remaining
handoff time make roughly 4.5–5 hours. Original training took approximately 6.4
minutes per completed seed. Extra setup/merge/transfer and paid handoff time add
cost, included in the aggregate ceiling. No speed improvement from shorter model
outputs is assumed. This is a projection, not a completion guarantee.
