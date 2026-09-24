#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
export TOKENIZERS_PARALLELISM=false
experiment_dir=experiment_log/008_transformers_conflict/execution
mkdir "$experiment_dir"
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
uv venv --python 3.11.13 .venv-gpu
uv pip sync --python .venv-gpu/bin/python requirements-preparation.txt
uv pip freeze --python .venv-gpu/bin/python > "$experiment_dir/gpu-environment.txt"
cmp experiment_log/004_task_preparation/gpu-environment.txt "$experiment_dir/gpu-environment.txt"
nvidia-smi > "$experiment_dir/nvidia-smi.txt"
.venv-gpu/bin/python scripts/merge_transformers_conflict.py > "$experiment_dir/merge-console.log" 2>&1
 .venv-gpu/bin/python scripts/run_transformers_conflict.py --stage prepared_clean > "$experiment_dir/prepared-clean-console.log" 2>&1
.venv-gpu/bin/python scripts/run_transformers_conflict.py --stage prompt_only_clean > "$experiment_dir/prompt-only-clean-console.log" 2>&1
if .venv-gpu/bin/python -c 'import sys; sys.path.insert(0,"scripts"); from transformers_conflict_support import verify_clean_gate,EXECUTION; verify_clean_gate(EXECUTION)'; then
  .venv-gpu/bin/python scripts/run_transformers_conflict.py --stage conflicts > "$experiment_dir/conflicts-console.log" 2>&1
else
  echo 'At least one clean condition failed unchanged gates; all conflict generation skipped.'
fi
echo 'Bounded Transformers conflict baseline finished. No retry or training.'
