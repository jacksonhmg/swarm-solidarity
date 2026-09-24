# Eight separate matching A100s: scheduling-only amendment

The user explicitly requested **"OKAY DO THE 8 A100 SEPARATW"** after reviewing
live availability and cost. Use eight independent `gpu_1x_a100_sxm4` instances,
at most $1.99/hour each, for the same eight frozen conditions. This replaces the
unallocated single-host retry route; its watcher PID 30813 was stopped and verified
to have no launch intent or owner state before the change. No new retry work has
run. The earlier A100 startup's model-work state remains unknown and its authorized
infrastructure-retry exception remains explicit.

Use the original experiment-011 `run_revised_eval.py` inference implementation,
unchanged byte-for-byte. This is the same verified serial FP16 eager computation
used by the host wrapper; the already-frozen wrapper changes only GPU guard and
provenance. The new node controller is the original `run_revised_node.py` with
only its scheduling-support import and self-invocation path changed. Its actual
training/inference commands and defaults are unchanged. Each condition retains
all 800 requests, prompt arrays, order and seeds. Only seeds 41031 and 41032 of
the revised arm train once; all other weights are reused. No batching, compilation,
sampling changes, data changes, task revisions, new examples or model-work retries.

The new scheduler uses separate owner names, state files and SSH keys. Launch
requests are sequential and spaced at least 13 seconds apart to respect Lambda's
documented limit. It rechecks advertised matching capacity between allocations,
preferring US West then US East. It does not assume a `quantity=8` request works:
the current official launch schema does not document that parameter or atomic
eight-instance allocation. Each node has one exclusive launch intent; uncertain
POST responses are reconciled by their saved owner names without repeating POSTs.
If remaining capacity disappears, wait at most ten minutes during allocation;
failure stops and cleans up owned resources before any model work.

All eight instances must be ready, have verified source/adapter upload hashes and
match `NVIDIA A100-SXM4-40GB` before dispatch. Each collector starts before its
exclusive detached dispatch. Lost acknowledgements remain unknown; read-only
collection reconnects without restarting model work or automatically destroying
healthy jobs. Confirmed worker failures or the cumulative spending cutoff stop
the attempt. Account API calls are serialized locally; unrelated resources are
never modified. The local source bundle contains no API credentials or SSH keys.

The aggregate **$65 ceiling includes $4.0985 already spent** on the failed H100
allocation and lost A100 startup. The owner-scoped watchdog requests termination
at **$62 cumulative**, leaving $3 for provider delay. Every remote node retains
its 180-minute model-work timeout. Measured generation plus training/setup/cleanup
projects $37.709769 for these nodes, **$41.808269 cumulative**, or $49.350223 with
20% contingency on the new work. Individual instances terminate as their assigned
condition finishes. No budget increase or further allocation attempt is allowed.

All earlier scientific, execution and retry freezes stay intact. The additive
verifier retains the unchanged per-request raw-token, seed, stopping, decode and
scoring loop. Its outer provenance checks cover eight distinct A100 UUIDs, the
correct original `run_revised_eval.py` entry-point hash and cumulative cleanup.
This also avoids the unused original verifier's stale assignment-hash comparison
to `run_corrective_eval.py`; the inference and scorer themselves are unchanged.
The analysis script, paired intervals/exact tests, fixed Holm family and five-point
joint-usefulness margins are unchanged. Both seeds remain separately reported.

The final report must qualify within-attempt no-retry verification: no repeated
observed requests in this run, with unobservable possible work in the lost startup.
Preserve experiment 010 as unsuccessful overall; stop after results and cleanup.

Pre-rental checks: all **102 tests passed** in the pinned preparation environment.
Two initial CPU test-harness failures (a temporary-directory plan lookup and the
namespace used to execute a captured Python snippet) are preserved in the initial
logs; both were corrected before any rental. No model, scorer or scheduling code
was changed in response to those test-harness errors. The pretest manifest is
preserved separately and the final pre-execution freeze records the passing tests.
