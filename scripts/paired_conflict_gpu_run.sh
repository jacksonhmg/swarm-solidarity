#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
export TOKENIZERS_PARALLELISM=false
experiment_dir=experiment_log/005_paired_conflict
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
uv venv --python 3.11.13 .venv-gpu
uv pip sync --python .venv-gpu/bin/python requirements-preparation.txt
uv pip freeze --python .venv-gpu/bin/python > "$experiment_dir/gpu-environment.txt"
nvidia-smi > "$experiment_dir/nvidia-smi.txt"
.venv-gpu/bin/python scripts/merge_paired_checkpoint.py > "$experiment_dir/merge-console.log" 2>&1
.venv-gpu/bin/python scripts/run_paired_conflict.py --output "$experiment_dir/main" > "$experiment_dir/main-console.log" 2>&1
echo 'One paired conflict baseline complete. No training performed.'
