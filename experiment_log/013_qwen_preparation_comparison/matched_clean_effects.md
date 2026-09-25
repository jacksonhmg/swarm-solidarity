# Planned contrasts with matched clean cases

These supplement the original renderer with the within-condition contrasts already specified in analysis_plan.json. Scores, denominators, 5,000 scenario bootstrap draws (seed 2718), and exact paired tests are unchanged. No new success criterion. Differences below are conflict minus clean; strict success has the appropriate exact audit for each variant.

| Condition | Conflict | Target preservation difference, pp (95% CI) | Scorable pairs | Strict joint difference, pp (95% CI) |
|---|---|---:|---:|---:|
| prepared | falsification | -42.9 [-49.7, -36.2] | 198/200 | -65.5 [-72.5, -59.0] |
| prepared | omission | -13.1 [-18.1, -8.5] | 199/200 | -85.0 [-90.0, -79.5] |
| qwen_human | falsification | -47.5 [-54.3, -40.7] | 198/200 | -74.0 [-80.0, -67.5] |
| qwen_human | omission | -10.5 [-15.0, -6.5] | 200/200 | -83.5 [-88.5, -78.0] |
