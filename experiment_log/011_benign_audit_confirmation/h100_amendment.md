# Authorized eight-H100 PCIe scheduling amendment

The user explicitly authorized eight separate H100 PCIe instances on 2026-09-24,
retaining the **$65 total additional GPU ceiling**. The A100 availability watcher
was stopped before any A100 rental: its owner state does not exist and spend is $0.
This additive amendment supersedes the two unexecuted A100 scheduling plans.
Their freezes and all original scientific artifacts remain preserved.

Use exactly `gpu_1x_h100_pcie`, no more than $3.29/hour each. Each condition has
one independent host and executes its original 800 requests in their frozen
order. Rent at most eight owned instances, once each. Start model work only after
all eight have been allocated and uploaded. On allocation failure, collect the
receipts, clean up owned resources, and stop rather than silently reducing the
study or repeatedly renting. Capacity polling before the first rental is allowed.

The fixed two revised training runs still start independently from the identical
prepared checkpoint at seeds 41031 and 41032. Only benign-audit and termination
labels change scientifically; the original `train_revised.py`, merge scripts,
data, order, optimizer, LoRA configuration and 125 updates remain unchanged.
The six other conditions reuse their existing checkpoints. H100 training can
produce different floating-point results than A100 training: comparisons with
the preserved 010 corrective adapters do not isolate hardware numerical effects.
All eight inference conditions now share the H100 execution setup.

`run_revised_h100_eval.py` changes only the GPU-name assertion and the recorded
entry-point/plan paths relative to the frozen runner. Model loading, FP16 eager
attention, batch size one, saved input arrays, sampling, seeds, stop handling,
postprocessing and scoring are unchanged. No compilation, batching or model
parallelism is added. Actual package versions, entry-point source hashes and
resolved runtime settings must still match 007/008. New scheduling/verification
scripts are copies of the existing eight-node infrastructure with explicit H100
paths, ownership and budget checks. The old verifier's unused runner-hash typo is
corrected only in the additive copy, as documented in the A100 host amendment.

Using recorded 010 A100 throughput without any H100 speedup assumption:
59,818.68 GPU-seconds for inference, 1,200 for the two revised training runs and
7,200 for eight setups/cleanup gives **$62.34**, approximately **2.6 hours** after
allocation. This narrowly fits the $65 ceiling; the independently enforced $63
termination threshold can leave an incomplete experiment if runtime exceeds the
estimate. Each remote controller also has a 180-minute timeout. Each successful
node is downloaded, hash-verified, terminated and its temporary key deleted as
soon as it finishes. Only recorded experiment-owned instances may be terminated.

No model-work retries or configuration changes are permitted. The fixed
6,400-response analysis, scenario pairing, eight primary contrasts, exact tests,
Holm correction and both legitimate-usefulness margins remain unchanged.
Incomplete results are preserved and reported as incomplete. This amendment and
its execution code are separately frozen and committed before any H100 rental.
