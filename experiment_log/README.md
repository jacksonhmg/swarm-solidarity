# Experiment log

Each experiment gets one numbered directory with a protocol, a concise report,
machine-readable results, and enough raw evidence to reproduce the scoring.
Record unsuccessful attempts and protocol changes instead of replacing them.

| Experiment | Purpose | Status |
|---|---|---|
| [001_baseline_pilot](001_baseline_pilot/report.md) | Check task competence, scoring, conflict behavior, and inference cost | Complete: 320 main responses; competence gates failed; training deferred; GPU terminated |
| [002_clean_diagnosis](002_clean_diagnosis/report.md) | Separate clean competence, replay, audit, format, and inference effects | Complete: 48 comparisons + 40 fresh clean confirmations; gates failed; GPU terminated |
| [003_six_record_feasibility](003_six_record_feasibility/report.md) | One frozen six-record task with unchanged JSON interface and inference | Complete: 29/40 exact and valid; both gates failed; stop further tuning; GPU terminated |
| [004_task_preparation](004_task_preparation/report.md) | One frozen ordinary-task preparation epoch with verified audit loss masking | Complete: 125 updates; 39/40 exact, 40/40 valid; ready to propose prepared-vs-prompt-only conflict baseline; adapter preserved; GPU terminated |
| [005_paired_conflict](005_paired_conflict/report.md) | One frozen prepared-vs-prompt-only baseline, 40 matched scenarios × four variants × two conditions | Complete: 320 responses; clean gates failed in both conditions, conflict scorability unreliable; stop and hold corrective training; GPU terminated; estimated spend $0.67 |
