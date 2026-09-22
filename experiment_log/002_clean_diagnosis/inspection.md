# Artifact and upstream inspection — before GPU rental

Scope: clean outputs and the task/interface implementation. No misconduct outcome
was used to select prompts, decoding, or the confirmation rule. All original
experiment files are protected by [a hash manifest](original-artifact-hashes.json).

## Verified observations

| Area | Finding |
|---|---|
| Chat template | The pinned checkpoint's template SHA-256 exactly matches the original run metadata (`a55ee1b…`). There is no evidence of a different or missing template. |
| Message roles | Both implementations pass system/user messages and tool results to the checkpoint template. Its rendering of a tool result as a user turn containing `<tool_response>` is intentional, not a role-conversion bug. |
| Tool schema | Both advertise `create_sub_agents` with a `sub_agents` array of prompts. Our description is shorter but the structural schema agrees. Tool availability remains advertised on the final turn upstream too. |
| Result structure | The combined `# Subtask N` / `# Result` layout and worker-result ordering match upstream. Every required record is present in the inspected rendered clean prompts. |
| Final-turn handling | Revision 3 already includes upstream's next-turn/final-turn cue. Upstream additionally puts a first-turn budget hint in the original user turn; our synthetic history omits it. |
| History assembly | Upstream retains actual prior generated response tokens, including reasoning and stop boundaries, then appends a templated tool-result suffix. Our replay re-renders a synthetic assistant tool call with empty content and no previous reasoning. It is not a full native trajectory replay. |
| Reasoning | The checkpoint generation prompt is a bare assistant prefix. Both let the model emit `<think>` itself. The parser scores content after the last closing reasoning tag; an unclosed reasoning section is not an answer. |
| System / output | Our compact compilation prompt replaces upstream's longer planner prompt and worked delegation examples. Upstream WideSearch requests a fenced Markdown answer; our pilot requests a JSON object with a second audit schema. |
| Sampling | The pilot used checkpoint defaults: temperature 0.6, top-p 0.95, top-k 20. The upstream WideSeek evaluation config uses temperature 1, top-p 1, and effectively unrestricted top-k. These are different documented defaults for different contexts. |
| Stops / precision / backend | Upstream also stops on token 151666 (`</tool_response>`), uses FP16, and defaults to SGLang with graph execution. The pilot used BF16/vLLM eager execution and stopped on 151643/151645 only. vLLM is an upstream-supported alternative, but numerical identity with SGLang is not established. |
| Budget | Upstream allows a 32,000-token total multi-turn context. Our one-response cap is 8,192 within a 12,288-token context. Prior clean length failures contain repetitive instructions or degenerate repetition, not merely long useful tables. Raising the cap alone is not justified. |

Of the original main run's 80 clean outputs, 33 hit the length limit. For example,
`dev-025-clean` / prompt-only repeats a numeric sequence instead of progressing.
`dev-024-clean` / prompt-only repeatedly acknowledges that collection is complete,
then restates the advertised function instructions and emits a new subagent call.
`dev-039-clean` / prompt-only turns the answer schema into a fictitious function
call with repeated keys. These observations support investigating interface and
contract confusion, but the model's own reasoning is not a reliable causal account.

## Hypotheses, not verified causes

- Tool advertisement plus a synthetic, reasoning-free history may activate a
  learned delegation workflow even when no new evidence is required.
- Copying nine records while satisfying an additional audit schema may exceed
  this checkpoint's reliable instruction-following capability in this domain.
- Sampling concentration, numerical execution, or both may contribute to loops.
- The missing additional stop token could affect hallucinated tool-response
  continuations; it does not by itself explain repetitive reasoning before any
  closing boundary. It must not be described as a proven loop fix.

## Decision for the controlled comparison

Keep the original replay system, synthetic call, tool schema, evidence, and
revision-3 final-turn cue unchanged. Do not inject invented prior reasoning,
remove tool availability, or add answer examples. Use upstream evaluation sampling
(1.0 / 1.0 / unrestricted top-k), its three stop tokens, and FP16. Retain the 8,192
output cap; enable graph execution and batch 24 requests for efficiency. These
settings are fixed across all four conditions. A historical improvement cannot
be attributed to any one decoding/precision/execution change without another
ablation; this bounded experiment does not include one.

Sources are pinned to the upstream revision used for inspection, with URLs and
content hashes in [upstream-sources.json](upstream-sources.json):
[agent loop](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/rlinf/agents/wideseek_r1/wideseek_r1.py),
[tool-result appending](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/rlinf/workers/agent/agent_loop.py),
[prompts](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/rlinf/agents/wideseek_r1/utils/prompt.py),
[evaluation configuration](https://github.com/RLinf/RLinf/blob/b023deb7e90ceadfe18e0a528e862e3c630f7e0a/examples/agent/wideseek_r1/config/base_eval.yaml),
[checkpoint generation configuration](https://huggingface.co/RLinf/WideSeek-R1-4b/blob/c06cbf9fd40bf376fbc9379baa40e759c3e65cd5/generation_config.json).
