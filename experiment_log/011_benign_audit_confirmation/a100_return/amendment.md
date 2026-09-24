# Authorized return to one eight-A100 40 GB host

The user explicitly approved switching back to the available eight-GPU A100
40 GB server after the H100 allocation failed. No experiment 011 model work has
occurred. Preserve the failed H100 allocation, its cleanup and $0.383833 GPU cost.

Resume the already-frozen A100 host execution path, restricted to
`gpu_8x_a100` at no more than $15.92/hour. One host supplies all eight assigned
GPUs, so there is no requirement to assemble eight separate cloud instances.
All scientific files, model/inference entry points, masks, data, seeds, training,
analysis and previous freezes remain unchanged. Only the launch selection and
cumulative budget/cleanup accounting are wrapped by `revised_a100_return.py`.

The A100 projection is $42.07, or **$42.45 including the failed H100 allocation**,
with approximately 2.6 hours after allocation at recorded throughput. This is an
estimate, not a completion guarantee. The **$65 aggregate ceiling** remains.
The local watchdog requests termination at **$62 total**, including the prior
$0.383833, leaving $3 for asynchronous cloud termination. The original remote
timeout remains an additional computational backstop. Cleanup writes the A100
host receipt separately and includes both allocations in the root cost receipt
before unchanged verification/analysis runs.

Capacity is checked every five seconds. Read-only checks and failed prechecks
without any ownership state can repeat. An actual or uncertain launch is never
repeated; inspect/reconcile its exact owner state. Train each revised seed once
and generate each frozen request once. No output-based retries, model changes,
configuration tuning or study-size changes are authorized.

The user authorization supersedes the prior infrastructure-only stop decision.
The H100 allocation failure remains recorded; it was not a scientific result.
