# Frozen execution plan after renewed authorization

Use the original experiment 004 LLM constructor unchanged on one H100 PCIe.
Before generation, require the resolved prefill budget to be 16,384 tokens,
maximum sequences 24, context 12,288, FP16, graph execution and prefix caching.
Do not replace defaults if an assertion fails; stop and report. Keep the exact
149-package environment and verify all 13 merged model files against 004.

Run `004_replay` in a fresh process from the existing saved input manifest, in
its original order and two batches of 24 then 16. Send the saved strings through
the original text-input API, checking tokenization against the pinned reconstruction
before and during generation. The input reconstruction limitation remains as
documented in the offline report. Sampling seeds come directly from the original
response metadata. Do not invoke a prompt builder or record generator.

A pass-through wrapper observes the V1 processor's actual request objects after
tokenization and EOS resolution. It records request IDs, token arrays, EOS,
resolved sampling objects and arrival times; it does not modify the returned
request. Record raw returned text, generated token IDs and finish/stop reasons.
Assert returned IDs, prompt strings and input arrays match each case. Instrumentation
adds host-side work and is disclosed as an execution difference from the uninstrumented
original; byte identity remains a measurement, never an extra gate.

Use the unchanged strict scorer via `row_diagnostics`. If and only if all forty
responses finish and reach 36 exact tables and 38 valid outputs, start `005_clean`
in a separate fresh engine process on the same instance. Use those forty saved
prepared-baseline clean strings and their original seeds in their relative saved
order, grouped 24 + 16. Restarting the engine resets the request counter and prefix
cache to the same clean-only arrangement as 004. No prompt-only or conflict calls.

Each stage exclusively creates its output directory; partial stages cannot resume
or rerun. No sweep or inference smoke. An incomplete stage or verification failure
stops the remote command. No training. The original 006 offline report and snapshots,
all experiment 005 artifacts and earlier results remain unchanged.

One owned H100 PCIe at no more than $3.29/hour, $10 cumulative additional GPU cap.
The sleep-inhibited local watchdog requests termination at $8; the whole remote
setup/merge/two-stage command has a 90-minute timeout. Reconcile state before any
launch, download and verify new execution artifacts, terminate and confirm, then
delete the temporary SSH key. Stop the heartbeat after the diagnostic ends.
