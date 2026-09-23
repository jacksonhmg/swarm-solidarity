# Paired baseline execution

A single A100 SXM4 in us-west-2 at $1.99/hour is selected from live capacity.
No single H100 was available at the pre-rental capacity check. The A100 is faster
than the earlier A10 and supports the unchanged FP16 inference configuration.
Both conditions share this one engine; hardware differs from preparation's H100
and will be reported. No training is run.

The local sleep-inhibited, owner-scoped watchdog requests termination at $8 of
allocation time, leaving $2 below the $10 cap for shutdown uncertainty. A 90-minute
remote timeout bounds setup, merge and generation. Credentials stay on the Mac;
no pre-existing instance is used.

Protocol, reminder, scoring and generator commit: `2961412`, before dataset
generation. Preflight checked all 320 rendered prompts, paired evidence invariance,
all golden answers, adapter identity and no training/development overlap.
