# Ready for the next matching-capacity check

The runner, analysis, four guard tests and 31-file execution freeze were committed
at `2654d04` before any rental. The original LLM constructor is AST-identical;
both forty-request manifests passed pinned-tokenizer and saved-association checks.
Do not rebuild or revise the frozen experiment when capacity returns.

H100 PCIe capacity appeared in us-west-3 at 23:41 UTC on 2026-09-23 but disappeared
before the launch precondition check at approximately 23:48 UTC. The client stopped
before creating a key, state file or launch POST. No inference or spending occurred.
The heartbeat remains active; this is an availability wait, not an inference retry.

For the next heartbeat:

- Recheck exact `gpu_1x_h100_pcie` capacity and price. Inspect
  `.local/lambda-reproduction/state.json` and any execution outputs first; never
  launch a duplicate or retry a started stage.
- Use the existing owner-scoped Lambda client and dedicated state path. Start
  its local sleep-inhibited watchdog immediately after successful launch, with
  the threshold equivalent to $8 allocation time. Credentials stay on the Mac.
- Upload the committed repository and separately transfer only the preserved
  `.local/preparation/terminal-adapter/` to the same relative path on the host.
- Run `scripts/reproduction_gpu_run.sh` once under the frozen 90-minute remote
  timeout. It verifies the environment and merged checkpoint, runs 004, then
  conditionally runs 005 clean in a fresh process. No smoke or preliminary model
  calls. Each stage refuses an existing output directory.
- Download the **entire new `experiment_log/006_reproduction/execution/`
  directory**, including `resolved_runtime.json`, `runtime_requests.jsonl`,
  scores, gates and merge metadata. The older filtered `remote.py download`
  command alone does not preserve these additional files.
- Verify downloaded hashes, confirm owned-instance termination and delete its
  temporary SSH key. Run `scripts/analyze_reproduction.py` offline, preserve the
  initial capacity-stop report, and add the completed diagnostic report/decision.
  Record actual allocation cost against the cumulative $10 cap. Stop the heartbeat.
