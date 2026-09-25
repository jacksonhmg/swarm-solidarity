# Swarm Solidarity

A controlled experiment on selective cooperation: preserve useful teammate
evidence, reject inappropriate requests, and report them to the human.
See [the research proposal](docs/project_overview.md).

**Separate write-up follow-ups (012–014):** [012’s offline failure breakdown](experiment_log/012_baseline_failure_breakdown/report.md) and [013’s Qwen comparison](experiment_log/013_qwen_preparation_comparison/interpretation.md) are complete. On the same 200 scenarios, task-prepared Qwen versus WideSeek had strict falsification success of **44 versus 57**, and omission success of **25 versus 18**. Observed compliance differences were uncertain; Qwen’s strict omission advantage arose from reporting/formatting on discordant cases. This does not establish that multi-agent training increases deference. The [Agent A principal-label test](experiment_log/014_principal_identity/protocol.md) is still running. At the user’s request, **465 completed responses** were preserved and the remaining **3,535** divided into twenty disjoint A100 assignments, without interrupting or repeating samples. One never-started boot failure is being recovered; healthy workers continue and finished rentals are cleaned up. The cumulative failsafe remains **$65**. See the [current execution handoff](experiment_log/013_qwen_preparation_comparison/monitor.md). These follow-ups reuse 011’s already examined scenarios and verified serial Transformers path; experiment 011 remains closed.

**Latest result (011): complete and closed.** The [revised benign-audit confirmation](experiment_log/011_benign_audit_confirmation/report.md) completed both 125-update training runs and all **6,400 responses**. Both revised seeds improved improper-omission whole-table-plus-exact-audit success over prepared (18/200), reminder (35/200), and matched ordinary controls: **87/200 and 71/200**. However, seed 41031 still made 36 false accusations on clean cases and failed the five-point usefulness margin; seed 41032 preserved usefulness but fell below its same-seed original corrective model on omission. The full selective-cooperation result therefore **did not hold across both seeds**. All outputs, adapters, paired intervals and exact tests are preserved; no seed is selected and no further tuning or training follows. Every owned GPU is terminated, temporary keys are deleted, and cumulative estimated spend is **$47.25 / $65**, including failed allocations. The earlier lost startup remains explicitly unobservable; the user-authorized infrastructure retry and the 40/80 GB hardware caveat are documented. See [diagnostics](experiment_log/011_benign_audit_confirmation/diagnostics.md) and [execution details](experiment_log/011_benign_audit_confirmation/execution_notes.md).

**Previous result (010):** the [bounded corrective comparison](experiment_log/010_corrective_comparison/report.md) is complete and closed: four terminal training runs and all 4,800 responses on 200 fresh final scenarios. Corrective training improved conflict evidence retention, but omission whole-table-plus-exact-audit success differed sharply between seeds (4/200 and 115/200), and both falsely reported misconduct on every schema-valid clean and legitimate-filtering output. The narrow clean-table margin passed; overall selective cooperation did not. Neither corrective checkpoint is selected. All adapters and results are preserved, all three GPUs are terminated, temporary keys are deleted, and estimated aggregate spend is **$26.67 / $40**. No further training, tuning or expansion follows this result. Earlier results and stop decisions remain intact.

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

The separate [reproduction check](experiment_log/006_reproduction/report.md)
completed its offline audit and stopped before inference because the required
H100 PCIe had no available capacity ($0 spent). The logs show a resolved prefill
budget of 16,384 tokens in 004 versus 8,192 in 005 despite identical constructor
arguments; causality remains unresolved. No saved association/scoring mismatch
was found. The requested exact paired test for 005's four-versus-zero falsification
joint successes gives two-sided **p = 0.125**, alongside the unchanged bootstrap
estimate. Experiment 005 remains closed and corrective training remains paused.
The user subsequently authorized waiting, then an
[A100 alternative](experiment_log/006_reproduction/a100_amendment.md), with the
16,384-token prefill budget explicit. That [bounded replay is now closed](experiment_log/006_reproduction/report_a100.md):
the forty saved 004 prompts produced **12/40 exact tables and 14/40 valid outputs**,
so the conditional 005 clean comparison was skipped. Ten output texts were
byte-identical to 004. The cause remains unresolved; this was not an exact H100
reproduction. All artifacts are preserved, the GPU is terminated, the temporary
SSH key is deleted, and the availability monitor is paused. Estimated compute
spend was **$0.40**, below the $10 cap. Corrective training remains paused.

The separately authorized [Transformers A100 check](experiment_log/007_transformers_check/report.md)
met the same clean gates on both saved sets: **39/40 exact and 40/40 valid** on
004, then **40/40 exact and valid** on 005's prepared-baseline clean prompts.
It used serial FP16 eager inference with the same verified weights and direct
saved token arrays. This supports clean competence under that alternative setup;
it does not identify hardware or a specific vLLM bug. Experiment 006 remains a
failed cross-hardware replay, exact H100 reproduction remains untested, and
corrective training stays paused. The eighty-response check is complete.
The GPU is terminated and temporary SSH keys are deleted; estimated additional
compute spend was **$1.06**, below the $10 cap.

The [frozen Transformers conflict baseline](experiment_log/008_transformers_conflict/report.md)
completed all 320 responses. Both clean conditions passed 40/40 exact tables and
valid outputs, but conflict failures remained. Its original aggregate audit count
had a reporting error: **123/160**, not 121/160, conflict audits are schema-valid.
The additive [reconciliation and omission breakdown](experiment_log/009_corrective_preflight/report.md)
preserves the original artifacts and explains the correction from all saved scores.

**Historical offline budget stop (009):** the separately authorized corrective comparison stopped
at its offline budget check, before rental, training, dataset generation or final
evaluation access. The required 4,800 responses project to $24.58 for generation
alone; even optimistic training and one setup/cleanup allowance bring the estimate
to $25.52, above the then-current $25 cap. Additional GPU spending for that offline
check was $0. The user subsequently authorized experiment 010, then a $40 aggregate
cap and parallel scheduling on three matching A100s. Its completed results appear
above; the original 009 decision is preserved.

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
directory. The authorized task-preparation dataset belongs to experiment 004.
Experiment 010 consumed its frozen 200-scenario final evaluation once, as explicitly
authorized; it must not become a source for omission-driven tuning or repeated
model evaluation.

The original pilot followed `experiment_log/001_baseline_pilot/protocol-v3.md`.
The initial greedy-decoding smoke run and aborted attempt are retained. To
re-score the initial smoke, pass `--config configs/pilot-greedy.json` and
`--limit-scenarios 2` to `scripts/analyze_pilot.py`.
