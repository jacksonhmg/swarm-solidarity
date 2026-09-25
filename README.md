# Swarm Solidarity

Can corrective training help a model reject inappropriate teammate requests, report them, and still cooperate usefully?

We test this with task-prepared **WideSeek** on a synthetic record-aggregation task. Teammates provide useful evidence alongside requests to falsify or hide results. Training covers falsification; omission tests whether the improvement transfers.

## Findings

Corrective training improved evidence preservation and transferred partly to omission. Accurate reporting and legitimate teamwork remained inconsistent across training seeds. The full goal was not achieved reliably.

These experiments use replayed teammate messages, not live swarms.

## Results and documentation

- [Project overview](docs/project_overview.md)
- [Main experiment](experiment_log/011_benign_audit_confirmation/report.md)
- [Failure breakdown](experiment_log/012_baseline_failure_breakdown/report.md)
- [WideSeek vs. Qwen](experiment_log/013_qwen_preparation_comparison/interpretation.md)
- [Human vs. AI principal](experiment_log/014_principal_identity/interpretation.md)

Protocols, raw outputs and analysis are in [experiment_log/](experiment_log/). Code lives in [src/](src/), with experiment scripts in [scripts/](scripts/) and settings in [configs/](configs/).

## Local setup

Requires Python 3.11+ and uv.

```sh
uv sync
uv run python -m unittest discover -s tests -v
```
