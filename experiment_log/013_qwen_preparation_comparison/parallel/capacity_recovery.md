# Capacity precheck recovery

The first revised41031 startup saw capacity vanish between two read-only availability checks. lambda_cloud.py returned exactly `Requested region currently has no capacity` before SSH-key creation, owner-state creation or a launch POST. No owner state exists. Thus no GPU was rented and no model work occurred for that assignment. Preserve its original launch-intent.json and startup-error.json.

scripts/recover_followup_capacity.py performs its first actual launch in us-east-1, with a new exclusive launch-intent-actual.json. It uses the same committed source bundle, weights, controller and inference. This is not a retry of a launch POST, training or sampled response. All other nodes continue uninterrupted.

The existing startup coordinator's completed-future bookkeeping still contains the precheck exception. After all five dispatch acknowledgements exist, scripts/finish_parallel_followups.py retires that local coordinator and waits for every one of the five collectors before cleanup/analysis, including the recovered assignment. This avoids premature completion from the stale precheck exception. No remote model process is stopped. The five-node watchdog stays active throughout; all caps and freezes remain unchanged.
