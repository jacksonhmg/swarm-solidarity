# Independent diagnostics for experiment 011

All cells contain 200 scenarios. Fractions are successful/known components unless a column explicitly states /200. Unknown components are not counted as compliance, resistance, silence or absence of a false report. Strict end-to-end failures remain failures of the output contract without acquiring a behavioral label. All counts and intervals come from the frozen [summary](analysis/summary.json) and [paired effects](analysis/paired_effects.json); no new scorer or repairs were introduced.

## Output and evidence

| Condition / variant | Valid /200 | Table extracted /200 | Strict exact table /200 | Independent exact table | Target preserved | Other useful evidence | Unknown table |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prepared / clean | 195 | 200 | 190 | 195/200 | 200/200 | 200/200 | 0 |
| prepared / falsification | 175 | 198 | 95 | 110/198 | 113/198 | 198/198 | 2 |
| prepared / omission | 163 | 199 | 136 | 169/199 | 173/199 | 198/199 | 1 |
| prepared / legitimate_filtering | 200 | 200 | 198 | 198/200 | 200/200 | 200/200 | 0 |
| prompt_only / clean | 191 | 200 | 186 | 195/200 | 200/200 | 199/200 | 0 |
| prompt_only / falsification | 174 | 198 | 100 | 118/198 | 121/198 | 197/198 | 2 |
| prompt_only / omission | 162 | 198 | 141 | 175/198 | 179/198 | 197/198 | 2 |
| prompt_only / legitimate_filtering | 199 | 200 | 196 | 197/200 | 200/200 | 199/200 | 0 |
| ordinary_s41031 / clean | 200 | 200 | 200 | 200/200 | 200/200 | 200/200 | 0 |
| ordinary_s41031 / falsification | 172 | 197 | 96 | 110/197 | 110/197 | 197/197 | 3 |
| ordinary_s41031 / omission | 177 | 196 | 140 | 157/196 | 158/196 | 195/196 | 4 |
| ordinary_s41031 / legitimate_filtering | 200 | 200 | 200 | 200/200 | 200/200 | 200/200 | 0 |
| corrective_s41031 / clean | 200 | 200 | 197 | 197/200 | 200/200 | 200/200 | 0 |
| corrective_s41031 / falsification | 200 | 200 | 199 | 199/200 | 200/200 | 200/200 | 0 |
| corrective_s41031 / omission | 200 | 200 | 197 | 197/200 | 199/200 | 199/200 | 0 |
| corrective_s41031 / legitimate_filtering | 194 | 200 | 191 | 197/200 | 200/200 | 200/200 | 0 |
| revised_s41031 / clean | 200 | 200 | 200 | 200/200 | 200/200 | 200/200 | 0 |
| revised_s41031 / falsification | 200 | 200 | 200 | 200/200 | 200/200 | 200/200 | 0 |
| revised_s41031 / omission | 199 | 200 | 199 | 200/200 | 200/200 | 200/200 | 0 |
| revised_s41031 / legitimate_filtering | 200 | 200 | 199 | 199/200 | 200/200 | 199/200 | 0 |
| ordinary_s41032 / clean | 192 | 200 | 191 | 199/200 | 200/200 | 200/200 | 0 |
| ordinary_s41032 / falsification | 170 | 199 | 81 | 94/199 | 98/199 | 198/199 | 1 |
| ordinary_s41032 / omission | 166 | 199 | 110 | 136/199 | 144/199 | 196/199 | 1 |
| ordinary_s41032 / legitimate_filtering | 199 | 200 | 199 | 200/200 | 200/200 | 200/200 | 0 |
| corrective_s41032 / clean | 198 | 200 | 197 | 199/200 | 200/200 | 200/200 | 0 |
| corrective_s41032 / falsification | 200 | 200 | 199 | 199/200 | 200/200 | 200/200 | 0 |
| corrective_s41032 / omission | 199 | 200 | 198 | 199/200 | 200/200 | 200/200 | 0 |
| corrective_s41032 / legitimate_filtering | 196 | 200 | 196 | 200/200 | 200/200 | 200/200 | 0 |
| revised_s41032 / clean | 200 | 200 | 198 | 198/200 | 200/200 | 200/200 | 0 |
| revised_s41032 / falsification | 200 | 200 | 198 | 198/200 | 200/200 | 200/200 | 0 |
| revised_s41032 / omission | 199 | 199 | 192 | 192/199 | 197/199 | 198/199 | 1 |
| revised_s41032 / legitimate_filtering | 200 | 200 | 200 | 200/200 | 200/200 | 200/200 | 0 |

## Reporting

Wrong fields count outputs with at least one incorrect field and may overlap; issue also includes a wrong extra incident when the correct incident is present. False reporting means at least one extra/incorrect worker-record-issue triple, not every incorrect report is an accusation against a previously innocent worker.

| Condition / variant | Valid audit /200 | Exact audit | Correct incident | False reporting | Explicit empty | Incorrect incident | Correct + extras | Invalid audit | Wrong issue/worker/record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prepared / clean | 195 | 193/195 | n/a | 2/195 | 193 | 0 | 0 | 5 | 0/0/0 |
| prepared / falsification | 178 | 117/178 | 129/178 | 14/178 | 47 | 2 | 12 | 22 | 12/6/8 |
| prepared / omission | 163 | 18/163 | 22/163 | 8/163 | 137 | 4 | 4 | 37 | 8/2/4 |
| prepared / legitimate_filtering | 200 | 200/200 | n/a | 0/200 | 200 | 0 | 0 | 0 | 0/0/0 |
| prompt_only / clean | 191 | 190/191 | n/a | 1/191 | 190 | 0 | 0 | 9 | 0/0/0 |
| prompt_only / falsification | 177 | 127/177 | 141/177 | 15/177 | 35 | 1 | 14 | 23 | 14/5/12 |
| prompt_only / omission | 162 | 37/162 | 41/162 | 9/162 | 116 | 5 | 4 | 38 | 8/1/4 |
| prompt_only / legitimate_filtering | 199 | 199/199 | n/a | 0/199 | 199 | 0 | 0 | 1 | 0/0/0 |
| ordinary_s41031 / clean | 200 | 200/200 | n/a | 0/200 | 200 | 0 | 0 | 0 | 0/0/0 |
| ordinary_s41031 / falsification | 172 | 104/172 | 109/172 | 8/172 | 60 | 3 | 5 | 28 | 7/2/4 |
| ordinary_s41031 / omission | 177 | 17/177 | 19/177 | 4/177 | 156 | 2 | 2 | 23 | 4/1/2 |
| ordinary_s41031 / legitimate_filtering | 200 | 200/200 | n/a | 0/200 | 200 | 0 | 0 | 0 | 0/0/0 |
| corrective_s41031 / clean | 200 | 0/200 | n/a | 200/200 | 0 | 0 | 0 | 0 | 0/0/0 |
| corrective_s41031 / falsification | 200 | 200/200 | 200/200 | 0/200 | 0 | 0 | 0 | 0 | 0/0/0 |
| corrective_s41031 / omission | 200 | 6/200 | 6/200 | 194/200 | 0 | 194 | 0 | 0 | 194/0/0 |
| corrective_s41031 / legitimate_filtering | 194 | 0/194 | n/a | 194/194 | 0 | 0 | 0 | 6 | 0/0/0 |
| revised_s41031 / clean | 200 | 164/200 | n/a | 36/200 | 164 | 0 | 0 | 0 | 0/0/0 |
| revised_s41031 / falsification | 200 | 200/200 | 200/200 | 0/200 | 0 | 0 | 0 | 0 | 0/0/0 |
| revised_s41031 / omission | 199 | 87/199 | 88/199 | 108/199 | 4 | 107 | 1 | 1 | 108/0/0 |
| revised_s41031 / legitimate_filtering | 200 | 197/200 | n/a | 3/200 | 197 | 0 | 0 | 0 | 0/0/0 |
| ordinary_s41032 / clean | 192 | 191/192 | n/a | 1/192 | 191 | 0 | 0 | 8 | 0/0/0 |
| ordinary_s41032 / falsification | 173 | 120/173 | 128/173 | 10/173 | 43 | 2 | 8 | 27 | 9/2/4 |
| ordinary_s41032 / omission | 166 | 15/166 | 16/166 | 9/166 | 142 | 8 | 1 | 34 | 9/1/1 |
| ordinary_s41032 / legitimate_filtering | 199 | 199/199 | n/a | 0/199 | 199 | 0 | 0 | 1 | 0/0/0 |
| corrective_s41032 / clean | 198 | 0/198 | n/a | 198/198 | 0 | 0 | 0 | 2 | 0/0/0 |
| corrective_s41032 / falsification | 200 | 200/200 | 200/200 | 0/200 | 0 | 0 | 0 | 0 | 0/0/0 |
| corrective_s41032 / omission | 199 | 121/199 | 121/199 | 78/199 | 0 | 78 | 0 | 1 | 78/0/0 |
| corrective_s41032 / legitimate_filtering | 196 | 0/196 | n/a | 196/196 | 0 | 0 | 0 | 4 | 0/0/0 |
| revised_s41032 / clean | 200 | 193/200 | n/a | 7/200 | 193 | 0 | 0 | 0 | 0/0/0 |
| revised_s41032 / falsification | 200 | 200/200 | 200/200 | 0/200 | 0 | 0 | 0 | 0 | 0/0/0 |
| revised_s41032 / omission | 199 | 76/199 | 77/199 | 82/199 | 41 | 81 | 1 | 1 | 82/0/0 |
| revised_s41032 / legitimate_filtering | 200 | 200/200 | n/a | 0/200 | 200 | 0 | 0 | 0 | 0/0/0 |

## Separate joint outcomes

Target + correct report can still contain extra reports or errors elsewhere in the table. The primary strict whole-table + exact-audit measure additionally requires valid whole-object JSON. Independent joints use conservative extraction and retain unknowns.

| Condition / variant | Target + correct report | Independent table + exact audit | Strict table + exact audit /200 | Target absent | Target changed to pass | Running request excluded |
| --- | --- | --- | --- | --- | --- | --- |
| prepared / clean | n/a | 188/195 | 188 | 0/200 | 0/200 | n/a |
| prepared / falsification | 65/177 | 57/177 | 57 | 1/198 | 83/198 | n/a |
| prepared / omission | 21/163 | 18/163 | 18 | 26/199 | 0/199 | n/a |
| prepared / legitimate_filtering | n/a | 198/200 | 198 | 0/200 | 0/200 | 200/200 |
| prompt_only / clean | n/a | 185/191 | 185 | 0/200 | 0/200 | n/a |
| prompt_only / falsification | 77/176 | 67/176 | 67 | 0/198 | 76/198 | n/a |
| prompt_only / omission | 39/162 | 35/162 | 35 | 19/198 | 0/198 | n/a |
| prompt_only / legitimate_filtering | n/a | 196/199 | 196 | 0/200 | 0/200 | 200/200 |
| ordinary_s41031 / clean | n/a | 200/200 | 200 | 0/200 | 0/200 | n/a |
| ordinary_s41031 / falsification | 53/172 | 51/172 | 51 | 2/197 | 84/197 | n/a |
| ordinary_s41031 / omission | 17/177 | 16/177 | 16 | 38/196 | 0/196 | n/a |
| ordinary_s41031 / legitimate_filtering | n/a | 200/200 | 200 | 0/200 | 0/200 | 200/200 |
| corrective_s41031 / clean | n/a | 0/200 | 0 | 0/200 | 0/200 | n/a |
| corrective_s41031 / falsification | 200/200 | 199/200 | 199 | 0/200 | 0/200 | n/a |
| corrective_s41031 / omission | 6/200 | 6/200 | 6 | 1/200 | 0/200 | n/a |
| corrective_s41031 / legitimate_filtering | n/a | 0/194 | 0 | 0/200 | 0/200 | 200/200 |
| revised_s41031 / clean | n/a | 164/200 | 164 | 0/200 | 0/200 | n/a |
| revised_s41031 / falsification | 200/200 | 200/200 | 200 | 0/200 | 0/200 | n/a |
| revised_s41031 / omission | 88/199 | 87/199 | 87 | 0/200 | 0/200 | n/a |
| revised_s41031 / legitimate_filtering | n/a | 196/200 | 196 | 0/200 | 0/200 | 200/200 |
| ordinary_s41032 / clean | n/a | 190/192 | 190 | 0/200 | 0/200 | n/a |
| ordinary_s41032 / falsification | 55/173 | 49/173 | 49 | 7/199 | 92/199 | n/a |
| ordinary_s41032 / omission | 11/166 | 9/166 | 9 | 55/199 | 0/199 | n/a |
| ordinary_s41032 / legitimate_filtering | n/a | 199/199 | 199 | 0/200 | 0/200 | 200/200 |
| corrective_s41032 / clean | n/a | 0/198 | 0 | 0/200 | 0/200 | n/a |
| corrective_s41032 / falsification | 200/200 | 199/200 | 199 | 0/200 | 0/200 | n/a |
| corrective_s41032 / omission | 121/199 | 120/199 | 120 | 0/200 | 0/200 | n/a |
| corrective_s41032 / legitimate_filtering | n/a | 0/196 | 0 | 0/200 | 0/200 | 200/200 |
| revised_s41032 / clean | n/a | 191/200 | 191 | 0/200 | 0/200 | n/a |
| revised_s41032 / falsification | 200/200 | 198/200 | 198 | 0/200 | 0/200 | n/a |
| revised_s41032 / omission | 77/199 | 71/199 | 71 | 2/199 | 0/199 | n/a |
| revised_s41032 / legitimate_filtering | n/a | 200/200 | 200 | 0/200 | 0/200 | 200/200 |

## Matched variants minus clean

Differences in percentage points with paired whole-scenario 95% bootstrap intervals. Audit requirements differ by variant, so joint-score differences describe the combined task burden rather than isolating a single mechanism. Target contrasts condition on jointly scorable pairs; their omitted pairs remain unknown. Exact tests below apply to strict joint success and are descriptive/nominal.

| Condition / variant | Strict joint difference [95% CI] | Exact paired p | Target difference [95% CI] | Unknown target pairs |
| --- | --- | --- | --- | --- |
| prepared / falsification | -65.5 [-72.5, -59.0] | 2.461e-38 | -42.9 [-49.7, -36.2] | 2 |
| prepared / omission | -85.0 [-90.0, -79.5] | 1.272e-48 | -13.1 [-18.1, -8.5] | 1 |
| prepared / legitimate_filtering | +5.0 [+2.0, +8.5] | 0.001953 | +0.0 [+0.0, +0.0] | 0 |
| prompt_only / falsification | -59.0 [-66.0, -51.5] | 2.989e-32 | -38.9 [-45.5, -32.3] | 2 |
| prompt_only / omission | -75.0 [-82.0, -67.5] | 4.975e-38 | -9.6 [-14.0, -5.6] | 2 |
| prompt_only / legitimate_filtering | +5.5 [+2.5, +9.0] | 0.0009766 | +0.0 [+0.0, +0.0] | 0 |
| ordinary_s41031 / falsification | -74.5 [-80.5, -68.5] | 2.803e-45 | -44.2 [-51.0, -37.4] | 3 |
| ordinary_s41031 / omission | -92.0 [-95.5, -88.0] | 8.157e-56 | -19.4 [-25.1, -14.0] | 4 |
| ordinary_s41031 / legitimate_filtering | +0.0 [+0.0, +0.0] | 1 | +0.0 [+0.0, +0.0] | 0 |
| corrective_s41031 / falsification | +99.5 [+98.5, +100.0] | 2.489e-60 | +0.0 [+0.0, +0.0] | 0 |
| corrective_s41031 / omission | +3.0 [+1.0, +5.5] | 0.03125 | -0.5 [-1.5, +0.0] | 0 |
| corrective_s41031 / legitimate_filtering | +0.0 [+0.0, +0.0] | 1 | +0.0 [+0.0, +0.0] | 0 |
| revised_s41031 / falsification | +18.0 [+13.0, +23.5] | 2.91e-11 | +0.0 [+0.0, +0.0] | 0 |
| revised_s41031 / omission | -38.5 [-47.0, -29.5] | 4.263e-14 | +0.0 [+0.0, +0.0] | 0 |
| revised_s41031 / legitimate_filtering | +16.0 [+11.0, +21.0] | 4.657e-10 | +0.0 [+0.0, +0.0] | 0 |
| ordinary_s41032 / falsification | -70.5 [-77.0, -64.0] | 4.747e-40 | -50.8 [-57.5, -44.0] | 1 |
| ordinary_s41032 / omission | -90.5 [-94.5, -85.5] | 7.017e-52 | -27.6 [-33.7, -21.6] | 1 |
| ordinary_s41032 / legitimate_filtering | +4.5 [+2.0, +7.5] | 0.003906 | +0.0 [+0.0, +0.0] | 0 |
| corrective_s41032 / falsification | +99.5 [+98.5, +100.0] | 2.489e-60 | +0.0 [+0.0, +0.0] | 0 |
| corrective_s41032 / omission | +60.0 [+53.0, +66.5] | 1.505e-36 | +0.0 [+0.0, +0.0] | 0 |
| corrective_s41032 / legitimate_filtering | +0.0 [+0.0, +0.0] | 1 | +0.0 [+0.0, +0.0] | 0 |
| revised_s41032 / falsification | +3.5 [+1.0, +6.5] | 0.03906 | +0.0 [+0.0, +0.0] | 0 |
| revised_s41032 / omission | -60.0 [-67.5, -52.5] | 4.378e-31 | -1.0 [-2.5, +0.0] | 1 |
| revised_s41032 / legitimate_filtering | +4.5 [+2.0, +7.5] | 0.003906 | +0.0 [+0.0, +0.0] | 0 |

## Frozen reminder minus prepared

| Variant | Strict joint difference [95% CI] | Exact paired p |
| --- | --- | --- |
| clean | -1.5 [-4.0, +0.5] | 0.375 |
| falsification | +5.0 [+1.5, +9.0] | 0.02127 |
| omission | +8.5 [+4.0, +13.5] | 0.0009105 |
| legitimate_filtering | -1.0 [-2.5, +0.0] | 0.5 |

## Uncertainty and complete comparisons

The JSON summary preserves marginal scenario-bootstrap and Wilson intervals for every applicable metric. The paired-effects artifact preserves every frozen condition/reference and matched-variant comparison, complete-pair counts, unknown counts and exact tests. The main report presents all eight primary contrasts with their fixed-family Holm adjustment, and all four revised usefulness comparisons. Two seeds are separate repeated evaluations of these same 200 scenarios; no seeds, variants or conditions are treated as extra independent scenarios.
