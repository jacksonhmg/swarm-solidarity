#!/usr/bin/env python3
"""Apply only the cumulative-cost timeout to the frozen host controller."""
import json
import run_revised_host as host

original_plan = host.plan


def cumulative_plan():
    result = original_plan()
    retry = json.loads((host.LOG/'infrastructure_retry/authorization.json').read_text())
    result['termination_threshold_usd'] = retry['termination_threshold_usd'] - retry['prior_gpu_cost_usd']
    return result


if __name__ == '__main__':
    host.plan = cumulative_plan
    host.main()
