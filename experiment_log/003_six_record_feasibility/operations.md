# Execution record

The task/configuration commit `257f37c` precedes data generation. Thirty-four tests
passed, then the one fixed 40-case dataset was generated and committed in `ea623ac`.
No inference was used to select or modify these cases.

A dedicated A10 in California was requested at $1.29/hour, retaining the selected
hardware rather than adding another inference variable. An A100 was advertised
at this check, but this run keeps the previous A10 setup. The pre-existing account
instance is not used. An owner-scoped watchdog requests termination after two
hours ($2.58 plus shutdown latency), below the continuing $25 spend ceiling.

The remote bootstrap uses the existing pinned setup, followed by an exact sync to
`experiment_log/002_clean_diagnosis/gpu-environment.txt`. The new environment
manifest must match that resolved package list before the one inference run.

```sh
python3 scripts/remote.py --state .local/lambda-six-record/state.json upload
# On the dedicated GPU host:
bash scripts/bootstrap_gpu.sh experiment_log/003_six_record_feasibility
$HOME/.local/bin/uv pip sync --python .venv-gpu/bin/python \
  experiment_log/002_clean_diagnosis/gpu-environment.txt
$HOME/.local/bin/uv pip freeze --python .venv-gpu/bin/python \
  > experiment_log/003_six_record_feasibility/gpu-environment.txt
cmp experiment_log/002_clean_diagnosis/gpu-environment.txt \
  experiment_log/003_six_record_feasibility/gpu-environment.txt
.venv-gpu/bin/python scripts/run_inference.py \
  --config configs/six-record-feasibility.json \
  --data data/dev/six-record-v2-clean-40.jsonl \
  --output experiment_log/003_six_record_feasibility/main
```

Only this one 40-response run is authorized by the frozen protocol. Download and
verify the raw artifacts before terminating the instance and deleting its key.

Completed exactly forty outputs. The resolved 147-package environment matched the
previous selected run byte for byte. Both empirical gates failed; no additional
inference was launched. All output was downloaded and source/evidence integrity
verified before termination. The instance is confirmed terminated and its key
deleted; final timestamps and cost estimate are recorded in `lifecycle.json`.
