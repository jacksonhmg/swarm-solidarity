# Exploratory omission cross-tabulations

These are error categories, not replacement success metrics. Every cell is a count out of 200; row and column totals partition all 200 cases. Components judged unscorable stay in their own row/column. All conditions use the same 200 scenarios; seeds are not pooled. [Definitions](definitions.md) were recorded before these tabulations.

## Category-only failures

| Condition | Original strict joint /200 | Sole category failure /200 | Sole category failure / jointly scorable | Table / audit / joint scorable | Full-table category errors with additional format failure |
| --- | --- | --- | --- | --- | --- |
| prepared | 18 | 3 | 3/163 | 199 / 163 / 163 | 0 |
| prompt_only | 35 | 4 | 4/162 | 198 / 162 / 162 | 0 |
| ordinary_s41031 | 16 | 2 | 2/177 | 196 / 177 / 177 | 0 |
| corrective_s41031 | 6 | 191 | 191/200 | 200 / 200 / 200 | 0 |
| revised_s41031 | 87 | 107 | 107/199 | 200 / 199 / 199 | 0 |
| ordinary_s41032 | 9 | 3 | 3/166 | 199 / 166 / 166 | 0 |
| corrective_s41032 | 120 | 78 | 78/199 | 200 / 199 / 199 | 0 |
| revised_s41032 | 71 | 79 | 79/199 | 199 / 199 / 199 | 0 |

## prepared

N=200; scorable table=199, audit=163, both=163. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 18 | 3 | 112 | 3 | 33 | 169 |
| Target preserved, other table errors | 0 | 0 | 4 | 0 | 0 | 4 |
| Target omitted / altered (incl. duplicates) | 0 | 1 | 21 | 1 | 3 | 26 |
| Unscorable table | 0 | 0 | 0 | 0 | 1 | 1 |
| Column total | 18 | 4 | 137 | 4 | 37 | 200 |

## prompt_only

N=200; scorable table=198, audit=162, both=162. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 35 | 4 | 99 | 3 | 34 | 175 |
| Target preserved, other table errors | 1 | 0 | 3 | 0 | 0 | 4 |
| Target omitted / altered (incl. duplicates) | 1 | 1 | 14 | 1 | 2 | 19 |
| Unscorable table | 0 | 0 | 0 | 0 | 2 | 2 |
| Column total | 37 | 5 | 116 | 4 | 38 | 200 |

## ordinary_s41031

N=200; scorable table=196, audit=177, both=177. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 16 | 2 | 121 | 1 | 17 | 157 |
| Target preserved, other table errors | 0 | 0 | 1 | 0 | 0 | 1 |
| Target omitted / altered (incl. duplicates) | 1 | 0 | 34 | 1 | 2 | 38 |
| Unscorable table | 0 | 0 | 0 | 0 | 4 | 4 |
| Column total | 17 | 2 | 156 | 2 | 23 | 200 |

## corrective_s41031

N=200; scorable table=200, audit=200, both=200. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 6 | 191 | 0 | 0 | 0 | 197 |
| Target preserved, other table errors | 0 | 2 | 0 | 0 | 0 | 2 |
| Target omitted / altered (incl. duplicates) | 0 | 1 | 0 | 0 | 0 | 1 |
| Unscorable table | 0 | 0 | 0 | 0 | 0 | 0 |
| Column total | 6 | 194 | 0 | 0 | 0 | 200 |

## revised_s41031

N=200; scorable table=200, audit=199, both=199. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 87 | 107 | 4 | 1 | 1 | 200 |
| Target preserved, other table errors | 0 | 0 | 0 | 0 | 0 | 0 |
| Target omitted / altered (incl. duplicates) | 0 | 0 | 0 | 0 | 0 | 0 |
| Unscorable table | 0 | 0 | 0 | 0 | 0 | 0 |
| Column total | 87 | 107 | 4 | 1 | 1 | 200 |

## ordinary_s41032

N=200; scorable table=199, audit=166, both=166. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 9 | 3 | 97 | 1 | 26 | 136 |
| Target preserved, other table errors | 1 | 0 | 5 | 0 | 2 | 8 |
| Target omitted / altered (incl. duplicates) | 5 | 5 | 40 | 0 | 5 | 55 |
| Unscorable table | 0 | 0 | 0 | 0 | 1 | 1 |
| Column total | 15 | 8 | 142 | 1 | 34 | 200 |

## corrective_s41032

N=200; scorable table=200, audit=199, both=199. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 120 | 78 | 0 | 0 | 1 | 199 |
| Target preserved, other table errors | 1 | 0 | 0 | 0 | 0 | 1 |
| Target omitted / altered (incl. duplicates) | 0 | 0 | 0 | 0 | 0 | 0 |
| Unscorable table | 0 | 0 | 0 | 0 | 0 | 0 |
| Column total | 121 | 78 | 0 | 0 | 1 | 200 |

## revised_s41032

N=200; scorable table=199, audit=199, both=199. For conditional row/column percentages use these disclosed component denominators; the cells below remain unconditional counts /200.

| Evidence / report | Exact audit | Correct IDs, wrong valid category | Explicit empty | Wrong IDs / extra accusations | Invalid / unscorable audit | Row total |
| --- | --- | --- | --- | --- | --- | --- |
| Entire table correct | 71 | 79 | 41 | 1 | 0 | 192 |
| Target preserved, other table errors | 5 | 0 | 0 | 0 | 0 | 5 |
| Target omitted / altered (incl. duplicates) | 0 | 2 | 0 | 0 | 0 | 2 |
| Unscorable table | 0 | 0 | 0 | 0 | 1 | 1 |
| Column total | 76 | 81 | 41 | 1 | 1 | 200 |
