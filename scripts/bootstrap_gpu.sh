#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
export PATH="$HOME/.local/bin:$PATH"
uv venv --python 3.11 .venv-gpu
uv pip install --python .venv-gpu/bin/python -r requirements-gpu.txt
uv pip freeze --python .venv-gpu/bin/python > experiment_log/001_baseline_pilot/gpu-environment.txt
nvidia-smi > experiment_log/001_baseline_pilot/nvidia-smi.txt
echo "GPU environment ready"
