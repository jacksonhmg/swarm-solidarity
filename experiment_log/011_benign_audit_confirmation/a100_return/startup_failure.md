# Experiment 011 A100 startup failure

The approved eight-A100 host **was obtained**. The launcher then treated a lost
startup acknowledgement as a reason to terminate it. This was an orchestration
failure, not evidence about the intervention. The original experiment remains
frozen; experiment 010 remains closed and unsuccessful overall.

## Verified sequence

- 2026-09-24 19:59:03 UTC: one `gpu_8x_a100` allocated in `me-west-1`, at
  $15.92/hour. Owned instance `7b9848a46f8c46879e28d23882379e8c`.
- The instance became active, SSH worked, cloud-init completed without reported
  errors, and an independent `nvidia-smi` check showed eight A100 SXM4 40 GB GPUs.
- The 639,934,010-byte source/adapter bundle uploaded and extraction completed.
- The SSH command to start the frozen `run_revised_host.py` controller exceeded
  the launcher's 45-second acknowledgement timeout. The exception was recorded
  at 20:10:36 UTC; it caused `host/abort.json` and owner-scoped cleanup.
- Termination was requested at 20:10:42 UTC and confirmed at 20:12:41 UTC.
  The temporary cloud key was deleted at 20:12:43 UTC; local key files were deleted.
- Attempts to recover remote logs failed after termination had already begun.
  No execution outputs, new adapters, controller receipt or remote console were
  recovered. The local collection supervisor had not started: the old launcher
  started it only after the dispatch SSH call returned.

The underlying reason SSH failed to acknowledge the background command is not
isolated. Inherited process pipes are a possible mechanism, not a verified cause.
The verified defect is that a transport timeout caused termination before
reconciliation and collection. A timeout does not establish that the remote
command failed to execute.

**Model-work state is unknown.** There are zero recovered responses and training
artifacts; it is not valid to report zero generated responses or zero training
starts. This also means an unchanged retry may repeat work that cannot be observed.
An explicit decision on that exception to the original no-retry boundary is
pending. No new rental or model work is authorized by this incident report itself.

## Cost and preserved evidence

The failed A100 startup used 14 rounded minutes: $3.7146666667. The earlier failed
H100 allocation used $0.3838333333 and verifiably never reached model work.
Cumulative GPU estimate: **$4.0985**, with **$60.9015** remaining under $65.
These are conservative elapsed-time GPU estimates, not provider invoices.
All experiment-owned resources are terminated and their temporary keys deleted.
Unrelated account resources were untouched.

Preserved receipts include `host/abort.json`, `a100_return/error.json`,
`a100_return/hardware-readiness.json`, `a100_return/recovery-read-attempt.json`,
`a100_return/host_cloud_lifecycle.json` and the cumulative `cloud_lifecycle.json`.
The stale pre-failure root status and decision were archived additively as
`a100_return/status_before_startup_failure.json` and
`a100_return/decision_before_startup_failure.json` before correcting current status.

## Offline repair and remaining integration

Two additive helpers leave all frozen training, inference and analysis unchanged:

- `dispatch_detached_once.py` claims an operation exclusively before spawning,
  records its PID, and detaches stdin/stdout/stderr and process session. Repeated
  delivery of the same operation returns its receipt without launching again.
- `revised_dispatch_transport.py` starts collection before dispatch, saves local
  intent before sending, and records a lost acknowledgement as unknown. It has
  no termination API and does not repeat the command. A second local dispatch
  attempt is rejected by the exclusive intent file.

Four CPU-only tests passed: real child-process pipe detachment, duplicate-delivery
protection, lost-acknowledgement handling and collection-before-dispatch ordering.
No GPU was used for repair tests. These verify the new mechanisms; they do not
prove the root cause of the original SSH timeout or certify a completed launcher.
Full launch integration, an additive freeze, preservation of the failed attempt's
owner state/receipts, and a cumulative budget including **both** failed starts
remain required before any approved retry. Old launchers must not be restarted.

The existing measured eight-GPU plan projects 9,512 seconds (about 2 h 39 min)
and $42.07 for a new run, about $46.16 cumulative including failed starts.
This is a planning estimate, not a capacity or completion guarantee. The fixed
scientific experiment is not being reduced, retuned or selected using outcomes.
