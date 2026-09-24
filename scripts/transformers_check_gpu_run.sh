#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
export TOKENIZERS_PARALLELISM=false
experiment_dir=experiment_log/007_transformers_check/execution
mkdir "$experiment_dir"
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
uv venv --python 3.11.13 .venv-gpu
uv pip sync --python .venv-gpu/bin/python requirements-preparation.txt
uv pip freeze --python .venv-gpu/bin/python > "$experiment_dir/gpu-environment.txt"
cmp experiment_log/004_task_preparation/gpu-environment.txt "$experiment_dir/gpu-environment.txt"
nvidia-smi > "$experiment_dir/nvidia-smi.txt"
.venv-gpu/bin/python scripts/merge_transformers_check.py > "$experiment_dir/merge-console.log" 2>&1
.venv-gpu/bin/python scripts/run_transformers_check.py --stage 004_replay > "$experiment_dir/004-console.log" 2>&1
if .venv-gpu/bin/python -c 'import json,sys; sys.exit(0 if json.load(open("experiment_log/007_transformers_check/execution/004_replay/gate.json"))["pass"] else 1)'; then
  .venv-gpu/bin/python scripts/run_transformers_check.py --stage 005_clean > "$experiment_dir/005-console.log" 2>&1
else
  echo '004 failed unchanged gates; 005 clean comparison skipped.'
fi
echo 'Independent Transformers check finished. No retry or training.'
