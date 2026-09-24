# Experiment 011: H100 allocation failure before model execution

The frozen eight-instance allocation did not complete. Lambda accepted the first
H100 PCIe launch in `us-west-3` at 2026-09-24 18:09:47 UTC. The second node's
capacity precheck then reported no capacity, before registering a key or sending
a launch POST. The scheduler stopped and requested termination of the sole owned
instance at 18:10:02 UTC. No model work began because the required eight-ready
barrier was never reached.

| Item | Outcome |
| --- | --- |
| H100 instances launched | 1 of 8 planned |
| New training runs / optimizer updates | 0 / 0 |
| Generated responses | 0 of 6,400 planned |
| Scientific comparison | Not run; no model-performance conclusion |
| Capacity-driven rental retry | None |
| Original and additive frozen files | 117 + 13 + 12 verified unchanged |
| Historical artifacts | 495 verified unchanged |

The first cleanup window expired while Lambda continued to report `terminating`.
The preserved `h100/allocation-result.json` records that initial unconfirmed
cleanup. Follow-up confirmed termination at **18:16:00 UTC** and cloud SSH-key
deletion at **18:16:04 UTC**; the local temporary key was also deleted. The
`h100/cleanup-followup.json` and `cloud_lifecycle.json` receipts preserve this
resolution separately. Conservative estimated GPU cost is **$0.3838 ($0.38)**,
using seven rounded-up minutes from launch request to termination confirmation;
this is an estimate rather than an invoice. No owned instances remain active.
The allocation monitor is paused and the automatic budget watchdog has no
remaining active instances.

The datasets, actual supervision-mask checks, two planned training seeds and all
analysis definitions remain frozen. The intended change still adds 2,800 benign
audit/termination loss tokens per run; it has not yet been trained or evaluated.
There is no evidence from this allocation attempt about transfer, usefulness,
false accusations or success across seeds. Experiment 010 remains closed and
unsuccessful overall, with its results unchanged.

Decision: stop this allocation attempt. Do not silently reduce the study,
substitute hardware, regenerate cases or retry model work. A further allocation
strategy requires an explicit user decision after cleanup.
