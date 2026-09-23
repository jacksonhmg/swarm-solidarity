# Swarm Solidarity

A controlled experiment on selective cooperation: preserve useful teammate
evidence, reject inappropriate requests, and report them to the human.
See [the research proposal](docs/project_overview.md).

The first milestone was a **development-only baseline pilot**. It ran the original
WideSeek-R1-4B checkpoint and a prompt-only reminder on 40 matched scenarios with
four variants each (320 responses). It does not train a model.

**Pilot complete:** neither condition passed the clean-task competence gate, so
training is deferred while the task and inference setup are diagnosed. The
[experiment report](experiment_log/001_baseline_pilot/report.md) records the
results, failed attempts, runtime, and cost. All raw outputs are retained and the
dedicated GPU has been terminated.

The [bounded clean-task diagnosis](experiment_log/002_clean_diagnosis/report.md)
is also complete. An improved inference setup looked promising on twelve clean
cases but failed fresh confirmation (19/40 exact tables, 29/40 valid outputs).
Training remains deferred; the recommendation is to simplify clean bookkeeping
while preserving worker evidence and the audit, or reconsider the checkpoint.

The subsequent [six-record feasibility pilot](experiment_log/003_six_record_feasibility/report.md)
tested that simplification as a new task version. It failed both fixed gates
(29/40 exact tables and 29/40 valid outputs). **Stop further task simplification
and configuration tuning for this checkpoint/setup.** Training remains paused;
no larger baseline or replacement model has been launched. Earlier results are
preserved unchanged.

The separately authorized [task-preparation experiment](experiment_log/004_task_preparation/report.md)
completed one frozen 1,000-example training epoch and passed fresh clean evaluation
(39/40 exact tables, 40/40 valid outputs). Its terminal adapter is preserved locally.
That evaluation supported a separately authorized paired conflict development
baseline against prompt-only guidance. The original-checkpoint stop decisions
above remain unchanged.

The [paired prepared-checkpoint baseline](experiment_log/005_paired_conflict/report.md)
is now complete: 320 responses, with no additional training. Both conditions failed
the fresh clean recheck: prepared **15/40 exact tables, 16/40 valid outputs**;
prompt-only **14/40 and 15/40**. Conflict outputs were frequently unscorable.
**Stop here and hold corrective training.** The reminder did not establish reliable
conflict handling or legitimate teamwork. All artifacts and the prepared adapter
are preserved; the GPU is terminated. No further inference, tuning, omission-driven
changes, or model substitution is authorized by this result.

## Local workflow

Python 3.11 and [uv](https://docs.astral.sh/uv/) are recommended. Generation,
scoring, cloud orchestration, and reporting use only the Python standard library.
The optional preparation tests additionally require the pinned Torch/Transformers/
PEFT environment and tokenizer snapshot used by experiment 004; the dependency-free
suite skips them when those assets are unavailable. The mandatory pre-rental mask
check is documented in the [preparation protocol](experiment_log/004_task_preparation/protocol.md).

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
- `.local/`: ignored credentials, instance state, logs, and the preserved prepared adapter.

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
  --output experiment_log/001_baseline_pilot/smoke_v3 --limit-scenarios 2
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
directory. The authorized task-preparation dataset belongs to experiment 004;
the final held-out evaluation has not been accessed.

The original pilot followed `experiment_log/001_baseline_pilot/protocol-v3.md`.
The initial greedy-decoding smoke run and aborted attempt are retained. To
re-score the initial smoke, pass `--config configs/pilot-greedy.json` and
`--limit-scenarios 2` to `scripts/analyze_pilot.py`.
