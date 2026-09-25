# Planned contrasts with matched clean cases

These supplement the original renderer with the within-condition contrasts already specified in analysis_plan.json. Scores, denominators, 5,000 scenario bootstrap draws (seed 2718), and exact paired tests are unchanged. No new success criterion. Differences below are conflict minus clean; strict success has the appropriate exact audit for each variant.

| Condition | Conflict | Target preservation difference, pp (95% CI) | Scorable pairs | Strict joint difference, pp (95% CI) |
|---|---|---:|---:|---:|
| prepared | falsification | -42.9 [-49.7, -36.2] | 198/200 | -65.5 [-72.5, -59.0] |
| prepared | omission | -13.1 [-18.1, -8.5] | 199/200 | -85.0 [-90.0, -79.5] |
| prepared_agent_a | falsification | -41.9 [-48.7, -35.2] | 198/200 | -67.5 [-74.0, -60.5] |
| prepared_agent_a | omission | -13.2 [-18.2, -8.7] | 197/200 | -84.0 [-89.5, -78.5] |
| qwen_agent_a | falsification | -43.4 [-50.3, -36.7] | 198/200 | -71.5 [-78.0, -65.0] |
| qwen_agent_a | omission | -10.5 [-15.0, -6.5] | 200/200 | -82.0 [-87.5, -76.0] |
| qwen_human | falsification | -47.5 [-54.3, -40.7] | 198/200 | -74.0 [-80.0, -67.5] |
| qwen_human | omission | -10.5 [-15.0, -6.5] | 200/200 | -83.5 [-88.5, -78.0] |
| revised_s41031 | falsification | +0.0 [+0.0, +0.0] | 200/200 | +18.0 [+13.0, +23.5] |
| revised_s41031 | omission | +0.0 [+0.0, +0.0] | 200/200 | -38.5 [-47.0, -29.5] |
| revised_s41031_agent_a | falsification | +0.0 [+0.0, +0.0] | 200/200 | +18.0 [+13.0, +23.5] |
| revised_s41031_agent_a | omission | +0.0 [+0.0, +0.0] | 200/200 | -38.0 [-47.0, -29.0] |
| revised_s41032 | falsification | +0.0 [+0.0, +0.0] | 200/200 | +3.5 [+1.0, +6.5] |
| revised_s41032 | omission | -1.0 [-2.5, +0.0] | 199/200 | -60.0 [-67.5, -52.5] |
| revised_s41032_agent_a | falsification | +0.0 [+0.0, +0.0] | 199/200 | +3.5 [+0.5, +7.0] |
| revised_s41032_agent_a | omission | -1.0 [-2.5, +0.0] | 199/200 | -59.5 [-67.0, -52.0] |
