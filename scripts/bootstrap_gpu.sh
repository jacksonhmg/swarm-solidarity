#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
export PATH="$HOME/.local/bin:$PATH"
uv venv --python 3.11 .venv-gpu
uv pip install --python .venv-gpu/bin/python -r requirements-gpu.txt
experiment_dir="${1:-experiment_log/001_baseline_pilot}"
mkdir -p "$experiment_dir"
uv pip freeze --python .venv-gpu/bin/python > "$experiment_dir/gpu-environment.txt"
nvidia-smi > "$experiment_dir/nvidia-smi.txt"
echo "GPU environment ready"
