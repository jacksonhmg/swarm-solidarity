#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
export TOKENIZERS_PARALLELISM=false
experiment_dir=experiment_log/010_corrective_comparison/execution
mkdir "$experiment_dir"
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user 'uv==0.8.22'
fi
uv venv --python 3.11.13 .venv-gpu
uv pip sync --python .venv-gpu/bin/python requirements-preparation.txt
uv pip freeze --python .venv-gpu/bin/python > "$experiment_dir/gpu-environment.txt"
cmp experiment_log/004_task_preparation/gpu-environment.txt "$experiment_dir/gpu-environment.txt"
nvidia-smi > "$experiment_dir/nvidia-smi.txt"
.venv-gpu/bin/python scripts/merge_corrective_base.py > "$experiment_dir/merge-console.log" 2>&1
for run in ordinary_s41031 corrective_s41031 ordinary_s41032 corrective_s41032; do
  .venv-gpu/bin/python scripts/train_corrective.py --run "$run" > "$experiment_dir/train-$run-console.log" 2>&1
  .venv-gpu/bin/python scripts/merge_corrective_adapter.py --run "$run" > "$experiment_dir/merge-$run-console.log" 2>&1
done
for condition in prepared prompt_only ordinary_s41031 corrective_s41031 ordinary_s41032 corrective_s41032; do
  .venv-gpu/bin/python scripts/run_corrective_eval.py --stage "$condition" > "$experiment_dir/eval-$condition-console.log" 2>&1
done
echo 'All four training runs and 4800 evaluations complete. No automatic expansion.'
