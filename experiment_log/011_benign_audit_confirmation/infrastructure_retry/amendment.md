# Authorized infrastructure retry after lost startup

The user explicitly approved one unchanged retry ("yes thats fine") after being
told that the lost A100 startup may have begun unobservable model work. This is
an infrastructure exception to the original no-repeated-work boundary, not a
performance-driven retry. No scores or outputs were recovered or used to select
anything. The failed startup remains preserved and its generated/training counts
remain unknown. The new attempt permits at most 6,400 observed requests and two
125-update revised training runs, with no retry inside that attempt.

All 117 scientific files, the 13-file host amendment, the unused 12-file H100
amendment, the six-file return amendment and 495 historical artifacts remain
byte-identical. Training, inference, dataset, prompt arrays, request order, seeds,
scoring and analysis remain unchanged. The four old trained adapters and prepared
checkpoint are reused; no further task preparation or inference tuning occurs.

One `gpu_8x_a100` host (eight A100 SXM4 40 GB GPUs) at no more than $15.92/hour
executes eight independent single-request inference processes. Prefer US West
capacity to reduce upload/connection latency; no model performance optimization
or GPU substitution is introduced. Exactly one launch intent is allowed. A lost
launch response must be reconciled by the saved owner name; never repeat its POST.

The new owner state is `.local/lambda-revised-retry/state.json`. Both prior owner
states remain at their original paths. Prior canonical `host/` receipts were
archived under `a100_return/failed_host/`; the new attempt gets a clean `host/`
receipt directory. This move affects no frozen file. The prior cumulative lifecycle,
status and decision are copied into this directory before replacing current state.

Startup uses an exclusive remote operation claim, detached standard streams and a
new process session. The local collection supervisor must acknowledge readiness
before dispatch. The dispatcher records intent before sending and never repeats
a command after a lost acknowledgement. A transport timeout stays unknown; it no
longer triggers premature instance termination. Read-only collection can reconnect
without restarting model work. Confirmed controller failure still stops the run.

The unchanged `run_revised_host.py` controller is invoked through
`run_revised_retry_host.py`, whose only override reduces its existing remote timeout
by prior GPU costs. It still launches the original frozen `--execute` path,
`train_revised.py` and `run_revised_host_eval.py`. The local watchdog requests owner-
scoped termination at **$62 cumulative**, leaving $3 below the $65 ceiling for
provider termination delay. Prior estimated spend is **$4.0985**. At $15.92/hour,
the measured plan projects $42.066354 for this attempt and **$46.164854 total**.
Remote timeout and local cutoff both count prior failed starts. No assumed budget
increase or automatic further allocation is permitted.

Collection preserves raw tokens, all request associations, actual runtime metadata,
training updates and both new adapters; it verifies final hashes before cleanup.
After termination and key deletion, the original verifier and analysis run on CPU.
Their within-run uniqueness/no-retry checks describe this observed retry only,
not the unobservable lost startup. The final report must state that scope clearly.
All training seeds and scientific contrasts remain separately reported. Stop after
the experiment; no automatic further training, selection or expansion.

Pre-rental validation: all **97 tests passed** in the preserved preparation
environment with Transformers 4.55.2. An initial invocation using the Mac's system
Python failed its explicit version assertion (4.57.0); that diagnostic is retained
as `tests.log`, and the correct pinned-environment result is `pinned_tests.log`.
This changed neither installed packages nor the frozen GPU environment. The new
tests exercise detached dispatch, duplicate-delivery protection, lost-acknowledgement
handling, supervision ordering, cumulative accounting and the remote budget timer.
