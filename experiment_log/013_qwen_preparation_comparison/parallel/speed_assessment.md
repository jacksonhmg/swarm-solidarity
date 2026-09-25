# Mid-run speed assessment — 2026-09-25 02:54 UTC

This is an infrastructure assessment requested by the user, not an execution amendment. No additional GPU was rented and no running model process, scientific setting, response assignment or budget safeguard was changed for this assessment.

## Measured current state

Qwen preparation completed once at 125 updates in 383.265 training seconds. A read-only SSH check at approximately 02:54 UTC found 147 Qwen human responses, 36 Qwen Agent A responses, 84 prepared WideSeek Agent A responses and 3 revised41031 Agent A responses. All four processes were generating on matching A100-SXM4-40GB GPUs. These are progress counts, not scores.

Locally collected timing snapshots at 02:53 UTC: Qwen human mean 8.660 seconds (137 responses), Qwen Agent A 8.901 seconds (26), prepared Agent A 9.104 seconds (76). Inputs are already shuffled across the four variants. Historical 011 revised41031/41032 variant means range from 8.210 to 9.937 seconds; those are supporting estimates, not measurements of the new identity prompts. Output-length shifts could change remaining time.

The revised41032 instance 96c12db2363049c18e1e9af5c15877b9 failed its boot timeout. Its startup error is timestamped 02:51:11 UTC; termination was requested at 02:51:15. It has no ready receipt, dispatch intent, controller dispatch, collector, or evaluation directory. No task model work was dispatched to it. Owner-scoped cleanup remains in the existing launcher's exception handler; provider status was still terminating at 02:54. The current five-node plan is therefore four healthy generating nodes plus one failed startup, not five healthy generating nodes.

The failed node requires an explicit, recorded infrastructure recovery before all 4,000 responses can complete. The current finisher waits for all five dispatches and cannot complete while this slot is missing. Do not interpret that wait as healthy progress. The four healthy jobs and their collectors/watchdog continue; never repeat their model work.

## Available hardware

Lambda's authenticated instance-types response at 02:53:13 UTC advertised single A100 SXM4 capacity in us-east-1 and us-west-2 at $1.99/hour, and A10 capacity at $1.29/hour. All advertised H100, B200 and multi-A100 types had empty capacity lists. This is a point-in-time advertisement, not a reservation or evidence that ten or twenty instances can be allocated. No alternative provider or faster-GPU throughput was verified.

## Scaling arithmetic and its limitation

About 3,730 responses remained at the direct progress snapshot. At a planning rate of nine seconds each, that is approximately 9.33 GPU-hours ($18.56 of remaining A100 generation). With perfectly balanced, independently assigned requests, five GPUs take about 112 minutes, ten about 56, twenty about 28. These are generation-only lower-level estimates, not end-to-end promises for the current run.

Each additional A100 spending 10–15 minutes booting/installing/loading costs about $0.33–$0.50 before generation. Successful observed launch-to-first-generation times were approximately 8–10 minutes on prepared and Qwen identity nodes; the failed startup illustrates the longer tail. More nodes add cost for duplicated setup, cleanup and idle time, but do not multiply the mathematical generation GPU-hours. Indicative whole-follow-up envelopes are roughly $25–30 for a restored five-node arrangement, $30–40 for a ten-node arrangement, or $35–50 for twenty, assuming similar throughput, prompt allocation and no prolonged capacity failures. These are planning ranges, not authorizations, invoices or guarantees.

The frozen scripts/run_followup_eval.py resets the seed independently for each request, so *prospective* assignment of disjoint request shards is scientifically plausible with unchanged prompt arrays, weights, decoding and scoring. However, its running loop has no cooperative pause, shard boundary, resume or handoff mechanism; it claims the entire 800-request stage. Launching copies on suffixes while originals continue would duplicate requests. Killing an original could interrupt an already-started sampled case. Neither is acceptable under the no-retry boundary. A verified live handoff is not currently implemented, and no claim is made that it can be safely retrofitted quickly. Sharding also requires explicit provenance for the changed scheduling/global request order and collectors that prove each original request ID occurs exactly once.

Keeping the four existing loops means the longest healthy assignment still takes about two hours of generation from this snapshot, regardless of how many helpers are rented. Recovering the unstarted revised41032 slot on a matching A100 would likely put the full study around 2–2.5 hours of generation/setup away, plus verification/reporting, conditional on successful startup. A 2–3 hour end-to-end planning range is more defensible than a promise of a halved remaining time. Splitting only the unstarted slot can reduce its lag, but cannot shorten the four already-running loops.

Recommendation: preserve the healthy work and recover the failed startup without model-work repetition. For a study scheduled from the outset, ten to twenty independently claimed shards would be the useful way to spend more on lower latency. Do not change eager attention, batching, compilation or engine for speed in these frozen follow-ups, and do not promise speedups from unmeasured or currently unavailable hardware.
