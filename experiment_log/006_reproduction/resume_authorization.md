# Resume authorization — waiting for matching hardware

On 2026-09-23, after the initial capacity stop, the user authorized:
“wait till its available then do it”. This supersedes only the earlier instruction
to stop waiting when H100 PCIe capacity is unavailable. The original offline report,
capacity snapshot, exact paired-test supplement and prior results remain intact.

The current task has an active heartbeat, `run-h100-reproduction-when-available`,
checking every 15 minutes. Stay quiet while availability is unchanged. When an
original-type `gpu_1x_h100_pcie` becomes available, finish and verify the replay
runner and freeze its execution configuration before renting. Use the saved input
manifests; do not regenerate prompts or records. Maintain experiment 004's effective
runtime setup and capture the actual request/token associations and resolved settings.

All existing boundaries remain: one 40-response replay, the optional second 40
clean responses only after the 36/40 exact-table and 38/40 validity gates pass,
$10 cumulative additional GPU cap, owned-instance safeguards, no hardware
substitution, retries, sweep, training or held-out evaluation. Keep experiment 005
closed and corrective training paused. Check local state and saved outputs before
any launch to prevent duplicates. Preserve outputs and terminate the GPU before
reporting; stop the heartbeat when the experiment ends or needs a user decision.

At the first check under this renewed authorization, the H100 PCIe remained
unavailable. No instance was rented and no additional GPU spending occurred.
