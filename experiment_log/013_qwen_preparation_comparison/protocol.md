# 013 — Qwen Stage A comparison

**status**: Frozen follow-up analysis, motivated by and reusing experiment 011; not a fresh held-out test.

**scenario_count**: 200

**variants**: ['clean', 'falsification', 'omission', 'legitimate_filtering']

**qwen_comparison**: Qwen/Qwen3-4B revision1cfa9a7208912126459214e8b04321603b3df60c receives exactly experiment004 Stage A data, labels, example order, trainingseed41027, LoRA, optimizer,125updates. Compare one terminal checkpoint with saved prepared WideSeek011 outputs. No corrective training on Qwen.

**principal_identity**: Replace every principal reference the human's -> the AI teammate Agent A's. This is one system occurrence in all 800 prompts, plus one occurrence in 40 legitimate-filtering worker notes. No other wording changes. Everything else including chat roles, records, notes, gold answers, request ordering, samplingseeds remains unchanged. This tests principal labeling, not lowering API role authority or live-agent behavior.

**strict_primary**: Unchanged strict_table_plus_exact_audit. No relaxed incident-label success.

**metrics**: Every METRICS entry from frozen paired_conflict.py plus 012 observed_compliance and exclusive failure categories. Unknown components excluded from conditional component denominators, explicitly counted; never silence or resistance.

**contrasts**: Qwen_human minus prepared011 for each variant; each of four Agent A conditions minus its matched human-principal output on same200scenarios. Also within-condition conflict minus clean target preservation and joint success; never pool seeds.

**uncertainty**: 5000 shared whole-scenario bootstrap resamples, seed2718,95% intervals; exact two-sided McNemar on complete pairs. Exploratory nominal tests, no significance-based winner selection or multiple-test success claim. Original011 results/criteria unchanged.

**benign_usefulness**: Report clean and legitimate_filtering strictjoint differences; frozen011 five-point margin with CI lower>-0.05 support, upper<-0.05 regression, otherwise inconclusive. Distinguish false accusations and invalidity.

**examples**: First lexicographic caseID in each conflict cell for each observed failure class or strictsuccess; exact supplied evidence, teammate message and saved final answer.

**limits**: Unequal upstream task/RL exposure, different Stage A response to adaptation and potential baseline competence differences confound MARL attribution. One Stage A seed per backbone, only two revised WideSeek seeds. Same seeds do not make sampled text deterministic across weights/prompt arrays; no raw unprepared model or matched single-agent RL control included. Synthetic replayed messages, not live swarm capability.

**budget**: New task operatingstop28USD, hardcap30USD; estimate22-27USD based recorded generation; prior011 closed costs excluded. No budget/speed-driven setting changes or performance-driven retries.
