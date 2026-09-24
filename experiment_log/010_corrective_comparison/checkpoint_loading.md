# Checkpoint provenance and loading

Each new terminal adapter is preserved at
`.local/corrective/{ordinary,corrective}_s{41031,41032}/terminal-adapter/` after its
training completes and its download hashes verify. Metadata and exact adapter
hashes are in `execution/training/<run>/metadata.json`. These adapters depend on
the prepared merged checkpoint, **not directly on the public original checkpoint**.

Reconstruct the prepared base using the preserved original preparation adapter
`.local/preparation/terminal-adapter/`, public base `RLinf/WideSeek-R1-4b` at
`c06cbf9fd40bf376fbc9379baa40e759c3e65cd5`, and the pinned environment in
`requirements-preparation.txt`. `scripts/merge_corrective_base.py` implements CPU
FP32 merge followed by FP16 save. All 13 files must match
`experiment_log/004_task_preparation/training/merge.json`.

For each new run, `scripts/merge_corrective_adapter.py --run <run>` loads that exact
prepared FP16 checkpoint into CPU FP32, applies its terminal adapter, merges, then
saves FP16. Compare all output hashes with `execution/training/<run>/merge.json`.
It refuses to overwrite a merged destination. The full frozen comparison runner
is `scripts/run_corrective_eval.py`; do not run it again on these final cases.

Training loads the identical prepared source in BF16, creates a fresh FP32 LoRA
adapter, and never resumes the preparation adapter. The source BF16 conversion is
common to both new arms. Frozen inference uses FP16, eager attention and evaluation
mode. Actual callable hashes and resolved generation settings are preserved for
each condition. Keep the adapters and prepared base together when moving machines.
