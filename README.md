# Swarm Solidarity

A controlled experiment on selective cooperation: preserve useful teammate
evidence, reject inappropriate requests, and report them to the human.
See [the research proposal](docs/project_overview.md).

The first milestone is a **development-only baseline pilot**. It runs the original
WideSeek-R1-4B checkpoint and a prompt-only reminder on 40 matched scenarios with
four variants each (320 responses). It does not train a model.

## Local workflow

Python 3.11 and [uv](https://docs.astral.sh/uv/) are recommended. Generation,
scoring, cloud orchestration, and reporting use only the Python standard library.

```sh
uv sync
uv run python -m unittest discover -s tests -v
uv run swarm-pilot generate
uv run swarm-pilot example
```

- `src/swarm_solidarity/`: task generation, prompts, parsing, and scoring.
- `configs/pilot.json`: checkpoint revision and pilot settings.
- `data/dev/`: reproducible development cases and a worked example.
- `scripts/`: owner-scoped cloud management and GPU execution.
- `experiment_log/`: protocols, raw evidence, and concise outcome reports.
- `.local/`: ignored credentials, instance state, and operational logs.

## GPU execution

Prepare the data and scorer locally before renting a GPU. A single A100 40 GB is
sufficient; no multi-GPU training stack or persistent cloud filesystem is needed.
The Lambda API credential stays on the controlling machine and is never copied
to the GPU instance. Set `LAMBDA_API_KEY_FILE` to the local credential file.

```sh
python3 scripts/lambda_cloud.py capacity
python3 scripts/lambda_cloud.py launch
python3 scripts/lambda_cloud.py status
```

The launch creates a dedicated SSH key and a uniquely named instance. Its local
state is `.local/lambda-pilot/state.json`. Do not overwrite this state to launch a
second instance; reconcile any uncertain launch first. Other instances are never
selected for termination. Use the recorded SSH identity and an isolated known-hosts
file with `StrictHostKeyChecking=accept-new` when connecting.

`python3 scripts/remote.py upload` transfers a Git archive of committed code,
excluding local credentials and Git configuration. It records the commit ID on
the host. Run commands with `python3 scripts/remote.py exec -- COMMAND ...`.
On the host:

```sh
bash scripts/bootstrap_gpu.sh
.venv-gpu/bin/python scripts/run_inference.py \
  --output experiment_log/001_baseline_pilot/smoke --limit-scenarios 2
# Inspect smoke output and scoring before continuing.
.venv-gpu/bin/python scripts/run_inference.py \
  --output experiment_log/001_baseline_pilot/main
```

Copy results back before terminating the instance. Responses are flushed after
each batch, and the runner resumes completed case/condition pairs only when the
configuration and dataset hashes match. Raw final responses, reasoning, rendered
prompts, token counts, software versions, and model revision are retained.

```sh
python3 scripts/remote.py download
uv run python scripts/analyze_pilot.py --run experiment_log/001_baseline_pilot/main
```

```sh
python3 scripts/lambda_cloud.py terminate
python3 scripts/lambda_cloud.py status
python3 scripts/lambda_cloud.py delete-key
```

Cloud instances accrue costs until terminated. The optional local budget watchdog
terminates only the owned instance after three hours. Run it on the controlling
machine, not the GPU host. The lifecycle and billing estimate belong in the
experiment log. Never commit credentials, private SSH keys, or environment files.

The report and reproducible analysis commands are recorded in each experiment's
directory. There are currently no training or held-out final-test datasets.
