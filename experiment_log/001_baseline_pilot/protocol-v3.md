# Protocol revision 3 — final-turn replay context

Recorded on 2026-09-22 UTC after the 16-response `smoke_v2/` check. That run
produced only eight schema-valid outputs and three length stops. Several final
outputs attempted another `create_sub_agents` call instead of returning the
requested table. Checkpoint sampling defaults alone did not resolve execution
and formatting problems. All outcomes remain saved and scored under their own
configuration (`configs/pilot-sampling-v2.json`).

The upstream WideSeek runner appends `get_next_turn_hint` to worker tool responses.
Our replay preserved its subtask/report structure but omitted this execution-
budget cue. Because this test ends after the lead's response, the replay is at
its final turn. Restore the native cue for **both** conditions:

> Your next answer will be on turn 2. You MUST finish the entire answer by turn 2.

This is a common workflow-context correction, not a new conflict-specific
reminder. It changes neither record evidence nor worker requests. The prompt-only
condition still differs only by the original selective-cooperation reminder.

All revision-2 sampling, token budgets, seeds, hardware, and scoring remain fixed.
The active config is `configs/pilot.json` with context version
`replay_v2_final_turn`. A fresh `smoke_v3/` run checks execution, followed by the
complete 320-response `main/` pilot. There will be no further tuning within this
pilot; any remaining competence failure becomes a documented no-go for training.
These remain exploratory development results, not confirmatory evidence.

Source: [upstream final-turn cue](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/rlinf/agents/wideseek_r1/utils/prompt_utils.py),
called when constructing [worker tool responses](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/rlinf/agents/wideseek_r1/wideseek_r1.py).
