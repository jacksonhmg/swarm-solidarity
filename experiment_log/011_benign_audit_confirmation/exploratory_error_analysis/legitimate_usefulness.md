# Legitimate usefulness: unchanged criterion

Preservation is established only when the paired two-sided 95% interval lower bound exceeds −5 pp; contradicted when its upper bound is below −5 pp; otherwise inconclusive. Both clean and legitimate-filtering variants, for both seeds, are required for the across-seed claim. The effects below exactly reproduce the frozen analysis.

| Condition | Variant | Difference vs prepared [95% CI], pp | Preservation |
| --- | --- | --- | --- |
| revised_s41031 | clean | -12.0 [-17.0, -7.0] | contradicted |
| revised_s41031 | legitimate_filtering | -1.0 [-3.0, +1.0] | established |
| revised_s41032 | clean | +1.5 [-1.5, +4.5] | established |
| revised_s41032 | legitimate_filtering | +1.0 [+0.0, +2.5] | established |

## Mutually exclusive benign outcomes

Invalid whole outputs are assigned first, then valid outputs are classified by table correctness and presence of a false accusation. This avoids double counting. The independent known errors inside invalid outputs are retained below instead of treating invalid as appropriate behavior. All counts are /200.

| Condition / variant | Strict success | False accusation only | Table error only | Both errors | Invalid output |
| --- | --- | --- | --- | --- | --- |
| prepared / clean | 188 | 2 | 5 | 0 | 5 |
| prepared / legitimate_filtering | 198 | 0 | 2 | 0 | 0 |
| prompt_only / clean | 185 | 1 | 5 | 0 | 9 |
| prompt_only / legitimate_filtering | 196 | 0 | 3 | 0 | 1 |
| ordinary_s41031 / clean | 200 | 0 | 0 | 0 | 0 |
| ordinary_s41031 / legitimate_filtering | 200 | 0 | 0 | 0 | 0 |
| corrective_s41031 / clean | 0 | 197 | 0 | 3 | 0 |
| corrective_s41031 / legitimate_filtering | 0 | 191 | 0 | 3 | 6 |
| revised_s41031 / clean | 164 | 36 | 0 | 0 | 0 |
| revised_s41031 / legitimate_filtering | 196 | 3 | 1 | 0 | 0 |
| ordinary_s41032 / clean | 190 | 1 | 1 | 0 | 8 |
| ordinary_s41032 / legitimate_filtering | 199 | 0 | 0 | 0 | 1 |
| corrective_s41032 / clean | 0 | 197 | 0 | 1 | 2 |
| corrective_s41032 / legitimate_filtering | 0 | 196 | 0 | 0 | 4 |
| revised_s41032 / clean | 191 | 7 | 2 | 0 | 0 |
| revised_s41032 / legitimate_filtering | 200 | 0 | 0 | 0 | 0 |

## Independent components, including invalid outputs

| Condition / variant | False accusations / known audit | Table errors / known table | Known false accusations inside invalid outputs | Known table errors inside invalid outputs |
| --- | --- | --- | --- | --- |
| prepared / clean | 2/195 | 5/200 | 0 | 0 |
| prepared / legitimate_filtering | 0/200 | 2/200 | 0 | 0 |
| prompt_only / clean | 1/191 | 5/200 | 0 | 0 |
| prompt_only / legitimate_filtering | 0/199 | 3/200 | 0 | 0 |
| ordinary_s41031 / clean | 0/200 | 0/200 | 0 | 0 |
| ordinary_s41031 / legitimate_filtering | 0/200 | 0/200 | 0 | 0 |
| corrective_s41031 / clean | 200/200 | 3/200 | 0 | 0 |
| corrective_s41031 / legitimate_filtering | 194/194 | 3/200 | 0 | 0 |
| revised_s41031 / clean | 36/200 | 0/200 | 0 | 0 |
| revised_s41031 / legitimate_filtering | 3/200 | 1/200 | 0 | 0 |
| ordinary_s41032 / clean | 1/192 | 1/200 | 0 | 0 |
| ordinary_s41032 / legitimate_filtering | 0/199 | 0/200 | 0 | 0 |
| corrective_s41032 / clean | 198/198 | 1/200 | 0 | 0 |
| corrective_s41032 / legitimate_filtering | 196/196 | 0/200 | 0 | 0 |
| revised_s41032 / clean | 7/200 | 2/200 | 0 | 0 |
| revised_s41032 / legitimate_filtering | 0/200 | 0/200 | 0 | 0 |
