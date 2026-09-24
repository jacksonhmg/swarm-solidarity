# User-approved A100 amendment

The user approved the proposed A100 alternative with “yes, do that.” after being
informed that it changes the hardware and limits the interpretation. This replaces
the H100-only execution requirement. No H100 or A100 execution has occurred yet;
the earlier protocol, source files, freezes and capacity-stop report remain intact.

Use one `gpu_1x_a100_sxm4` (40GB) at no more than $1.99/hour. Explicitly set
`max_num_batched_tokens=16384`, the effective prefill budget recorded in 004;
the A100 default of 8192 is not used. This override and GPU identity are the only
inference-setting changes from the previously frozen runner. Every other LLM
constructor argument, decoding parameter, saved prompt/token reconstruction,
sampling seed, order, checkpoint and scorer stays unchanged. KV memory capacity
will differ from the H100; record it rather than trying to tune it.

This is a replay on different hardware, **not an exact reproduction of the H100
execution**. If the 004 replay fails, it cannot establish that 004 is unreproducible
on its original hardware. If 004 passes and the saved 005 clean set fails on the
same A100 setup, this is consistent with input/seed-set sensitivity on A100.
If both pass, the difference is associated with 005's execution arrangement;
prefill budget, batching, instrumentation and other execution details have not
been isolated individually. Do not make a causal hardware/batching claim.

Run `scripts/reproduction_a100_gpu_run.sh` once under the same 90-minute timeout.
The script uses `run_reproduction_a100.py`, with its separate
`execution_freeze_a100.json`; no H100 source or original freeze is overwritten.
The unused `execution/` destination is retained. Analyze completed output using
`scripts/analyze_reproduction_a100.py`. Preserve the entire execution directory.

Keep the existing 40-response first stage, 36/40 exact-table and 38/40 validity
gates, conditional second forty clean responses, and maximum eighty responses.
No inference smoke, performance retry, sweep, training, new data, or final test.
Experiment 005 stays closed and corrective training stays paused.

The cumulative additional GPU cap remains $10. Use a dedicated
`.local/lambda-reproduction-a100/state.json`, with duplicate checks against the
unused H100 state and any existing execution output. Retain the sleep-inhibited
$8 termination watchdog, 90-minute remote timeout, verified download, confirmed
termination and temporary SSH-key deletion. Stop the availability heartbeat when
the run ends. The heartbeat now watches this approved A100 type only.
