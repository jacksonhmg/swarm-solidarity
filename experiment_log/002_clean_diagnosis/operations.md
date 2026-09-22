# Cloud execution notes

- Repeated API checks found no single-GPU H100, GH200, or B200 capacity.
- A100 SXM4 capacity was advertised in Virginia, but the launch returned an
  insufficient-capacity rejection. Reconciliation found no matching instance;
  its temporary SSH key was deleted. No compute was allocated for that attempt.
- The only remaining available GPU type was A10. A dedicated A10 in California
  was launched at $1.29 per instance-hour. The pre-existing account instance was
  left untouched.
- A local owner-scoped watchdog will terminate this allocation after two hours
  ($2.58 at the quoted rate, plus termination latency), well below the $25 cap.
- CUDA graph execution and batch size 24 replace the original eager/batch-16
  execution for efficiency. Hardware speedup over A100 is not claimed.

Launch requested (UTC): 2026-09-22T16:02:02.380433+00:00
