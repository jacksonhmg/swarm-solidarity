# Experiment log

Each experiment gets one numbered directory with a protocol, a concise report,
machine-readable results, and enough raw evidence to reproduce the scoring.
Record unsuccessful attempts and protocol changes instead of replacing them.

| Experiment | Purpose | Status |
|---|---|---|
| [001_baseline_pilot](001_baseline_pilot/report.md) | Check task competence, scoring, conflict behavior, and inference cost | Complete: 320 main responses; competence gates failed; training deferred; GPU terminated |
| [002_clean_diagnosis](002_clean_diagnosis/report.md) | Separate clean competence, replay, audit, format, and inference effects | Complete: 48 comparisons + 40 fresh clean confirmations; gates failed; GPU terminated |
