# Read-only response to speed/parallelism question

No execution changes, extra rentals, or sampled-case retries have been made.
The existing job continues while the user considers a scheduling amendment.

008 measured 2,963.849 seconds for 320 serial responses (9.262 seconds/response,
21.435 generated tokens/second). The fixed evaluation has 4,800 responses, 15 times
that baseline. Its projected generation alone is 12.349 GPU-hours / $24.575 at
$1.99/hour. The first actual 010 training run took 383.42 seconds, suggesting roughly
26 minutes for all four training runs, with remaining seeds still unmeasured.

Independent conditions could run on separate matching A100 SXM4 40GB instances,
each retaining the frozen serial Transformers path, full condition request order,
seeds and exact checkpoint/prompt hashes. Equal-sized condition assignment gives
approximately 12.35 / 6.17 / 4.12 hours of inference on one / two / three GPUs.
Total inference GPU-hours stay approximately constant; extra boot, environment,
checkpoint transfer/load and collection costs must be included. These are planning
estimates; trained-model response lengths and actual multi-instance capacity remain
uncertain. A proposed three-GPU arrangement assigns two whole conditions per GPU,
retains all four training runs on the existing instance, and requires an additive
execution-plan amendment plus aggregate owner-scoped $30 protection. It must prevent
the original controller from also generating conditions assigned elsewhere, without
interrupting a sampled request, repeating training or discarding outputs.

The authenticated Lambda quote at 2026-09-24 06:49 UTC is in
parallel_options_capacity.json. Available offerings include A100 SXM4 ($1.99/hour),
H100 PCIe ($3.29), GH200 ($2.29), A10 ($1.29), and four A6000s ($4.36 total/hour).
Availability is transient and does not guarantee enough instances. H100 would need
more than 1.653x A100 throughput to be cheaper for the same work, excluding setup;
its throughput under this exact path is not measured. Other hardware introduces
unvalidated execution differences. Batching, vLLM, compilation and attention changes
would change the frozen inference path and are not proposed here.
