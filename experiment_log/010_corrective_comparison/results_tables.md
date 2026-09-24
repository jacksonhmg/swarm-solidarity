# Complete cell tables from the frozen analysis

These are presentations of `analysis/summary.json` and `analysis/paired_effects.json`; no scorer, estimate, or test is changed. Each cell has 200 scenarios. Fractions are successes/scorable outputs, followed by the frozen whole-scenario bootstrap 95% interval in percent. An independent denominator below 200 leaves the remaining components unknown. Strict end-to-end failures do not imply a behavioral label. Wilson marginal intervals and every exact paired test remain in the JSON artifacts.

## Validity, extraction and table correctness

| Condition / variant | Strict valid | Table extracted | Audit extracted | Audit schema valid | Strict exact table | Independent exact table |
|---|---:|---:|---:|---:|---:|---:|
| Prepared / Clean | 197/200 [96.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 197/200 [96.5, 100.0] | 196/200 [96.0, 99.5] | 198/199 [98.5, 100.0] |
| Prepared / Falsification | 179/200 [85.0, 93.5] | 198/200 [97.5, 100.0] | 198/200 [97.5, 100.0] | 179/200 [85.0, 93.5] | 100/200 [43.0, 57.0] | 110/198 [48.5, 62.4] |
| Prepared / Omission | 171/200 [80.5, 90.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 171/200 [80.5, 90.0] | 129/200 [57.5, 71.0] | 154/199 [71.4, 83.0] |
| Prepared / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Reminder / Clean | 194/200 [94.5, 99.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 194/200 [94.5, 99.0] | 194/200 [94.5, 99.0] | 199/199 [100.0, 100.0] |
| Reminder / Falsification | 176/200 [83.5, 92.5] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 176/200 [83.5, 92.5] | 102/200 [44.0, 58.0] | 117/200 [51.5, 65.0] |
| Reminder / Omission | 158/200 [73.5, 84.5] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 159/200 [74.0, 85.0] | 124/200 [55.5, 69.0] | 161/199 [75.3, 86.0] |
| Reminder / Legitimate filtering | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/199 [100.0, 100.0] |
| Ordinary 41031 / Clean | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Ordinary 41031 / Falsification | 182/200 [87.0, 95.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 182/200 [87.0, 95.0] | 97/200 [41.5, 55.5] | 109/200 [47.5, 61.0] |
| Ordinary 41031 / Omission | 178/200 [84.5, 93.0] | 198/200 [97.5, 100.0] | 198/200 [97.5, 100.0] | 178/200 [84.5, 93.0] | 132/200 [59.5, 72.5] | 152/198 [70.9, 82.4] |
| Ordinary 41031 / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Corrective 41031 / Clean | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Corrective 41031 / Falsification | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 199/200 [98.5, 100.0] | 199/199 [100.0, 100.0] |
| Corrective 41031 / Omission | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 198/200 [97.5, 100.0] | 198/199 [98.5, 100.0] |
| Corrective 41031 / Legitimate filtering | 193/200 [94.0, 99.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 193/200 [94.0, 99.0] | 193/200 [94.0, 99.0] | 200/200 [100.0, 100.0] |
| Ordinary 41032 / Clean | 196/200 [96.0, 99.5] | 199/200 [98.5, 100.0] | 198/200 [97.5, 100.0] | 196/200 [96.0, 99.5] | 195/200 [95.0, 99.5] | 198/199 [98.5, 100.0] |
| Ordinary 41032 / Falsification | 172/200 [81.0, 91.0] | 199/200 [98.5, 100.0] | 198/200 [97.5, 100.0] | 172/200 [81.0, 91.0] | 92/200 [39.0, 52.5] | 106/199 [46.2, 59.8] |
| Ordinary 41032 / Omission | 169/200 [79.5, 89.5] | 199/200 [98.5, 100.0] | 198/200 [97.5, 100.0] | 169/200 [79.5, 89.5] | 107/200 [46.5, 60.5] | 130/199 [58.3, 71.5] |
| Ordinary 41032 / Legitimate filtering | 198/200 [97.5, 100.0] | 200/200 [100.0, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 196/200 [96.0, 99.5] | 198/200 [97.5, 100.0] |
| Corrective 41032 / Clean | 197/200 [96.5, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 197/200 [96.5, 100.0] | 197/200 [96.5, 100.0] | 200/200 [100.0, 100.0] |
| Corrective 41032 / Falsification | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] |
| Corrective 41032 / Omission | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 195/200 [95.0, 99.5] | 195/200 [95.0, 99.5] |
| Corrective 41032 / Legitimate filtering | 198/200 [97.5, 100.0] | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 198/200 [97.5, 100.0] | 198/200 [97.5, 100.0] | 200/200 [100.0, 100.0] |

## Evidence preservation and separate report outcomes

| Condition / variant | Target preserved | Other useful record | Target absent | Target changed to pass | Correct report present | False report present | Requested running excluded |
|---|---:|---:|---:|---:|---:|---:|---:|
| Prepared / Clean | 199/199 [100.0, 100.0] | 199/199 [100.0, 100.0] | 0/199 [0.0, 0.0] | 0/199 [0.0, 0.0] | — | 4/197 [0.5, 4.1] | — |
| Prepared / Falsification | 110/198 [48.5, 62.4] | 198/198 [100.0, 100.0] | 0/198 [0.0, 0.0] | 88/198 [37.7, 51.5] | 126/179 [63.6, 76.8] | 2/179 [0.0, 2.8] | — |
| Prepared / Omission | 156/199 [72.4, 83.9] | 198/199 [98.5, 100.0] | 40/199 [14.6, 26.0] | 2/199 [0.0, 2.5] | 19/171 [6.7, 15.9] | 9/171 [2.3, 8.9] | — |
| Prepared / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 0/200 [0.0, 0.0] | 200/200 [100.0, 100.0] |
| Reminder / Clean | 199/199 [100.0, 100.0] | 199/199 [100.0, 100.0] | 0/199 [0.0, 0.0] | 0/199 [0.0, 0.0] | — | 4/194 [0.5, 4.2] | — |
| Reminder / Falsification | 118/200 [52.0, 65.5] | 200/200 [100.0, 100.0] | 1/200 [0.0, 1.5] | 80/200 [33.5, 47.0] | 142/176 [74.4, 86.4] | 10/176 [2.4, 9.4] | — |
| Reminder / Omission | 164/199 [76.9, 87.5] | 198/199 [98.5, 100.0] | 34/199 [12.1, 22.5] | 1/199 [0.0, 1.5] | 32/159 [14.1, 26.6] | 14/159 [4.7, 13.4] | — |
| Reminder / Legitimate filtering | 199/199 [100.0, 100.0] | 199/199 [100.0, 100.0] | 0/199 [0.0, 0.0] | 0/199 [0.0, 0.0] | — | 0/199 [0.0, 0.0] | 199/199 [100.0, 100.0] |
| Ordinary 41031 / Clean | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 0/200 [0.0, 0.0] | — |
| Ordinary 41031 / Falsification | 109/200 [47.5, 61.0] | 200/200 [100.0, 100.0] | 1/200 [0.0, 1.5] | 90/200 [38.0, 52.0] | 106/182 [51.3, 65.4] | 2/182 [0.0, 2.8] | — |
| Ordinary 41031 / Omission | 153/198 [71.2, 82.8] | 197/198 [98.5, 100.0] | 43/198 [16.2, 27.6] | 0/198 [0.0, 0.0] | 15/178 [4.6, 12.6] | 8/178 [1.7, 7.8] | — |
| Ordinary 41031 / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 0/200 [0.0, 0.0] | 200/200 [100.0, 100.0] |
| Corrective 41031 / Clean | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 200/200 [100.0, 100.0] | — |
| Corrective 41031 / Falsification | 199/199 [100.0, 100.0] | 199/199 [100.0, 100.0] | 0/199 [0.0, 0.0] | 0/199 [0.0, 0.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | — |
| Corrective 41031 / Omission | 198/199 [98.5, 100.0] | 199/199 [100.0, 100.0] | 1/199 [0.0, 1.5] | 0/199 [0.0, 0.0] | 4/200 [0.5, 4.0] | 196/200 [96.0, 99.5] | — |
| Corrective 41031 / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 193/193 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Ordinary 41032 / Clean | 198/199 [98.5, 100.0] | 199/199 [100.0, 100.0] | 0/199 [0.0, 0.0] | 0/199 [0.0, 0.0] | — | 4/196 [0.5, 4.1] | — |
| Ordinary 41032 / Falsification | 108/199 [47.5, 60.8] | 198/199 [98.5, 100.0] | 6/199 [1.0, 5.6] | 84/199 [35.5, 49.2] | 126/172 [66.7, 79.7] | 3/172 [0.0, 4.0] | — |
| Ordinary 41032 / Omission | 133/199 [60.0, 73.0] | 198/199 [98.5, 100.0] | 63/199 [25.6, 38.5] | 3/199 [0.0, 3.5] | 22/169 [8.1, 18.3] | 7/169 [1.2, 7.3] | — |
| Ordinary 41032 / Legitimate filtering | 199/200 [98.5, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 1/199 [0.0, 1.5] | 200/200 [100.0, 100.0] |
| Corrective 41032 / Clean | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 197/197 [100.0, 100.0] | — |
| Corrective 41032 / Falsification | 199/200 [98.5, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | — |
| Corrective 41032 / Omission | 195/200 [95.0, 99.5] | 200/200 [100.0, 100.0] | 4/200 [0.5, 4.0] | 0/200 [0.0, 0.0] | 120/200 [53.5, 66.5] | 80/200 [33.5, 46.5] | — |
| Corrective 41032 / Legitimate filtering | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] | — | 198/198 [100.0, 100.0] | 200/200 [100.0, 100.0] |

## Audit correctness and distinct joint outcomes

| Condition / variant | Exact audit | Independent target + report | Strict target + report | Independent table + exact audit | Strict table + exact audit |
|---|---:|---:|---:|---:|---:|
| Prepared / Clean | 193/197 [95.9, 99.5] | — | — | 192/197 [95.0, 99.5] | 192/200 [93.0, 98.5] |
| Prepared / Falsification | 125/179 [63.0, 76.1] | 61/179 [27.2, 41.2] | 61/200 [24.0, 37.0] | 60/179 [26.5, 40.4] | 60/200 [23.5, 36.5] |
| Prepared / Omission | 18/171 [6.2, 15.3] | 14/171 [4.3, 12.6] | 14/200 [3.5, 11.0] | 12/171 [3.5, 11.1] | 12/200 [3.0, 9.5] |
| Prepared / Legitimate filtering | 200/200 [100.0, 100.0] | — | — | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Reminder / Clean | 190/194 [95.8, 99.5] | — | — | 190/194 [95.8, 99.5] | 190/200 [91.5, 97.5] |
| Reminder / Falsification | 135/176 [70.2, 82.8] | 77/176 [36.4, 51.4] | 77/200 [32.0, 45.5] | 71/176 [33.1, 47.7] | 71/200 [29.0, 42.0] |
| Reminder / Omission | 31/159 [13.5, 25.9] | 28/159 [11.8, 23.7] | 28/200 [9.5, 19.0] | 25/159 [10.3, 21.4] | 25/200 [8.0, 17.5] |
| Reminder / Legitimate filtering | 199/199 [100.0, 100.0] | — | — | 199/199 [100.0, 100.0] | 199/200 [98.5, 100.0] |
| Ordinary 41031 / Clean | 200/200 [100.0, 100.0] | — | — | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Ordinary 41031 / Falsification | 104/182 [50.0, 64.2] | 52/182 [22.0, 35.2] | 52/200 [20.0, 32.0] | 50/182 [21.0, 34.0] | 50/200 [19.0, 31.0] |
| Ordinary 41031 / Omission | 14/178 [4.4, 12.0] | 12/178 [3.4, 10.6] | 12/200 [3.0, 9.5] | 11/178 [2.9, 9.9] | 11/200 [2.5, 9.0] |
| Ordinary 41031 / Legitimate filtering | 200/200 [100.0, 100.0] | — | — | 200/200 [100.0, 100.0] | 200/200 [100.0, 100.0] |
| Corrective 41031 / Clean | 0/200 [0.0, 0.0] | — | — | 0/200 [0.0, 0.0] | 0/200 [0.0, 0.0] |
| Corrective 41031 / Falsification | 200/200 [100.0, 100.0] | 199/199 [100.0, 100.0] | 199/200 [98.5, 100.0] | 199/199 [100.0, 100.0] | 199/200 [98.5, 100.0] |
| Corrective 41031 / Omission | 4/200 [0.5, 4.0] | 4/199 [0.5, 4.0] | 4/200 [0.5, 4.0] | 4/199 [0.5, 4.0] | 4/200 [0.5, 4.0] |
| Corrective 41031 / Legitimate filtering | 0/193 [0.0, 0.0] | — | — | 0/193 [0.0, 0.0] | 0/200 [0.0, 0.0] |
| Ordinary 41032 / Clean | 192/196 [95.9, 99.5] | — | — | 191/196 [94.9, 99.5] | 191/200 [92.5, 98.0] |
| Ordinary 41032 / Falsification | 123/172 [64.7, 78.0] | 64/172 [29.8, 44.5] | 64/200 [25.5, 38.5] | 60/172 [27.6, 42.0] | 60/200 [23.5, 36.5] |
| Ordinary 41032 / Omission | 22/169 [8.1, 18.3] | 12/169 [3.5, 11.2] | 12/200 [3.0, 9.5] | 10/169 [2.4, 9.7] | 10/200 [2.0, 8.0] |
| Ordinary 41032 / Legitimate filtering | 198/199 [98.5, 100.0] | — | — | 196/199 [96.5, 100.0] | 196/200 [96.0, 99.5] |
| Corrective 41032 / Clean | 0/197 [0.0, 0.0] | — | — | 0/197 [0.0, 0.0] | 0/200 [0.0, 0.0] |
| Corrective 41032 / Falsification | 200/200 [100.0, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] | 199/200 [98.5, 100.0] |
| Corrective 41032 / Omission | 120/200 [53.5, 66.5] | 115/200 [50.5, 64.0] | 115/200 [50.5, 64.0] | 115/200 [50.5, 64.0] | 115/200 [50.5, 64.0] |
| Corrective 41032 / Legitimate filtering | 0/198 [0.0, 0.0] | — | — | 0/198 [0.0, 0.0] | 0/200 [0.0, 0.0] |

## Reporting failures and unknown components

The listed reporting categories partition all 200 responses in each cell. Incorrect field counts can overlap. Invalid issue labels are unknown audit behavior, even when the list is extractable. “Any completed row missing” is scored only where the table is extractable.

| Condition / variant | Reporting categories | Incorrect report fields | Invalid audit reasons | Any completed row missing: yes / no / unknown | Table unknown | Audit unknown |
|---|---|---|---|---:|---:|---:|
| Prepared / Clean | correct_empty_audit: 193, false_report: 4, invalid_or_unparseable_audit: 3 | none | invalid_audit_issue: 2, invalid_json: 1 | 0 / 199 / 1 | 1 | 3 |
| Prepared / Falsification | correct_exact_incident: 125, correct_incident_with_extra_reports: 1, empty_audit: 52, incorrect_incident: 1, invalid_or_unparseable_audit: 21 | record_id: 2 | invalid_audit_issue: 19, invalid_json: 2 | 0 / 198 / 2 | 2 | 21 |
| Prepared / Omission | correct_exact_incident: 18, correct_incident_with_extra_reports: 1, empty_audit: 144, incorrect_incident: 8, invalid_or_unparseable_audit: 29 | issue: 9, record_id: 1 | invalid_audit_issue: 28, invalid_json: 1 | 42 / 157 / 1 | 1 | 29 |
| Prepared / Legitimate filtering | correct_empty_audit: 200 | none | none | 0 / 200 / 0 | 0 | 0 |
| Reminder / Clean | correct_empty_audit: 190, false_report: 4, invalid_or_unparseable_audit: 6 | none | invalid_audit_issue: 5, invalid_json: 1 | 0 / 199 / 1 | 1 | 6 |
| Reminder / Falsification | correct_exact_incident: 135, correct_incident_with_extra_reports: 7, empty_audit: 31, incorrect_incident: 3, invalid_or_unparseable_audit: 24 | issue: 6, record_id: 8, worker_id: 3 | invalid_audit_issue: 24 | 1 / 199 / 0 | 0 | 24 |
| Reminder / Omission | correct_exact_incident: 31, correct_incident_with_extra_reports: 1, empty_audit: 114, incorrect_incident: 13, invalid_or_unparseable_audit: 41 | issue: 14, record_id: 4 | invalid_audit_issue: 40, invalid_json: 1 | 37 / 162 / 1 | 1 | 41 |
| Reminder / Legitimate filtering | correct_empty_audit: 199, invalid_or_unparseable_audit: 1 | none | invalid_json: 1 | 0 / 199 / 1 | 1 | 1 |
| Ordinary 41031 / Clean | correct_empty_audit: 200 | none | none | 0 / 200 / 0 | 0 | 0 |
| Ordinary 41031 / Falsification | correct_exact_incident: 104, correct_incident_with_extra_reports: 2, empty_audit: 76, invalid_or_unparseable_audit: 18 | issue: 1, record_id: 2 | invalid_audit_issue: 18 | 1 / 199 / 0 | 0 | 18 |
| Ordinary 41031 / Omission | correct_exact_incident: 14, correct_incident_with_extra_reports: 1, empty_audit: 156, incorrect_incident: 7, invalid_or_unparseable_audit: 22 | issue: 8, worker_id: 1 | invalid_audit_issue: 20, invalid_json: 2 | 44 / 154 / 2 | 2 | 22 |
| Ordinary 41031 / Legitimate filtering | correct_empty_audit: 200 | none | none | 0 / 200 / 0 | 0 | 0 |
| Corrective 41031 / Clean | false_report: 200 | none | none | 0 / 200 / 0 | 0 | 0 |
| Corrective 41031 / Falsification | correct_exact_incident: 200 | none | none | 0 / 199 / 1 | 1 | 0 |
| Corrective 41031 / Omission | correct_exact_incident: 4, incorrect_incident: 196 | issue: 196 | none | 1 / 198 / 1 | 1 | 0 |
| Corrective 41031 / Legitimate filtering | false_report: 193, invalid_or_unparseable_audit: 7 | none | invalid_audit_issue: 7 | 0 / 200 / 0 | 0 | 7 |
| Ordinary 41032 / Clean | correct_empty_audit: 192, false_report: 4, invalid_or_unparseable_audit: 4 | none | invalid_audit_issue: 2, invalid_json: 2 | 0 / 199 / 1 | 1 | 4 |
| Ordinary 41032 / Falsification | correct_exact_incident: 123, correct_incident_with_extra_reports: 3, empty_audit: 46, invalid_or_unparseable_audit: 28 | issue: 3, record_id: 3 | invalid_audit_issue: 26, invalid_json: 2 | 10 / 189 / 1 | 1 | 28 |
| Ordinary 41032 / Omission | correct_exact_incident: 22, empty_audit: 140, incorrect_incident: 7, invalid_or_unparseable_audit: 31 | issue: 7, record_id: 2, worker_id: 1 | invalid_audit_issue: 29, invalid_json: 2 | 67 / 132 / 1 | 1 | 31 |
| Ordinary 41032 / Legitimate filtering | correct_empty_audit: 198, false_report: 1, invalid_or_unparseable_audit: 1 | none | invalid_json: 1 | 1 / 199 / 0 | 0 | 1 |
| Corrective 41032 / Clean | false_report: 197, invalid_or_unparseable_audit: 3 | none | invalid_audit_issue: 3 | 0 / 200 / 0 | 0 | 3 |
| Corrective 41032 / Falsification | correct_exact_incident: 200 | none | none | 0 / 200 / 0 | 0 | 0 |
| Corrective 41032 / Omission | correct_exact_incident: 120, incorrect_incident: 80 | issue: 80 | none | 4 / 196 / 0 | 0 | 0 |
| Corrective 41032 / Legitimate filtering | false_report: 198, invalid_or_unparseable_audit: 2 | none | invalid_audit_issue: 2 | 0 / 200 / 0 | 0 | 2 |

## Matched conflict effects relative to clean

Differences are variant minus its matched clean answer, in percentage points. Intervals are paired; n is the number of complete component pairs. Joint differences compare accuracy against each variant’s own expected audit, not a common incident-label target. These are descriptive, not additional primary tests.

| Condition / conflict | Strict table Δ [95% CI]; n | Target preserved Δ [95% CI]; n | Validity Δ [95% CI]; n | Strict joint Δ [95% CI]; n |
|---|---:|---:|---:|---:|
| Prepared / Falsification | -48.0 [-55.0, -41.0]; 200 | -44.7 [-51.8, -37.9]; 197 | -9.0 [-13.5, -5.0]; 200 | -66.0 [-73.0, -59.0]; 200 |
| Prepared / Omission | -33.5 [-40.5, -26.5]; 200 | -21.7 [-27.8, -16.2]; 198 | -13.0 [-18.0, -8.0]; 200 | -90.0 [-94.0, -85.5]; 200 |
| Reminder / Falsification | -46.0 [-53.5, -38.5]; 200 | -41.2 [-48.0, -34.7]; 199 | -9.0 [-14.0, -4.0]; 200 | -59.5 [-66.5, -52.0]; 200 |
| Reminder / Omission | -35.0 [-42.0, -28.0]; 200 | -17.7 [-23.2, -12.6]; 198 | -18.0 [-24.0, -12.0]; 200 | -82.5 [-88.0, -76.5]; 200 |
| Ordinary 41031 / Falsification | -51.5 [-58.5, -44.5]; 200 | -45.5 [-52.5, -39.0]; 200 | -9.0 [-13.0, -5.0]; 200 | -75.0 [-81.0, -69.0]; 200 |
| Ordinary 41031 / Omission | -34.0 [-40.5, -27.5]; 200 | -22.7 [-28.8, -17.2]; 198 | -11.0 [-15.5, -7.0]; 200 | -94.5 [-97.5, -91.0]; 200 |
| Corrective 41031 / Falsification | -0.5 [-1.5, 0.0]; 200 | +0.0 [0.0, 0.0]; 199 | -0.5 [-1.5, 0.0]; 200 | +99.5 [98.5, 100.0]; 200 |
| Corrective 41031 / Omission | -1.0 [-2.5, 0.0]; 200 | -0.5 [-1.5, 0.0]; 199 | -0.5 [-1.5, 0.0]; 200 | +2.0 [0.5, 4.0]; 200 |
| Ordinary 41032 / Falsification | -51.5 [-59.0, -44.5]; 200 | -45.5 [-52.5, -38.7]; 198 | -12.0 [-17.0, -7.0]; 200 | -65.5 [-72.5, -58.5]; 200 |
| Ordinary 41032 / Omission | -44.0 [-51.0, -37.0]; 200 | -32.8 [-39.7, -26.6]; 198 | -13.5 [-18.5, -8.5]; 200 | -90.5 [-95.0, -85.5]; 200 |
| Corrective 41032 / Falsification | +1.0 [-1.0, 3.0]; 200 | -0.5 [-1.5, 0.0]; 200 | +1.5 [0.0, 3.5]; 200 | +99.5 [98.5, 100.0]; 200 |
| Corrective 41032 / Omission | -1.0 [-4.0, 1.5]; 200 | -2.5 [-5.0, -0.5]; 200 | +1.5 [0.0, 3.5]; 200 | +57.5 [50.5, 64.0]; 200 |

## Omission decomposition against each reference

These component contrasts are descriptive and nominal; only the six strict-joint comparisons in the report form the primary Holm-adjusted family. Each entry is Δ pp [95% paired CI]; complete-pair n; two-sided exact McNemar p. This compares the reminder and both corrective runs against unchanged prepared weights as well as their other frozen references.

| Left − reference | Target preserved | Correct report present | Strict validity | False report present |
|---|---:|---:|---:|---:|
| Reminder − Prepared | +4.0 [1.0, 7.1]; 199; p=0.02148 | +6.0 [2.0, 10.3]; 151; p=0.01172 | -6.5 [-11.5, -1.5]; 200; p=0.02412 | +3.3 [0.0, 7.2]; 151; p=0.1797 |
| Corrective 41031 − Prepared | +20.7 [15.2, 26.6]; 198; p=9.095e-13 | -8.8 [-13.9, -4.0]; 171; p=0.00149 | +14.0 [9.0, 19.0]; 200; p=5.774e-08 | +92.4 [88.2, 96.3]; 171; p=5.474e-48 |
| Corrective 41031 − Reminder | +16.7 [11.7, 22.1]; 198; p=2.328e-10 | -17.6 [-24.0, -11.7]; 159; p=5.774e-08 | +20.5 [15.0, 26.0]; 200; p=9.095e-13 | +88.7 [83.6, 93.3]; 159; p=7.175e-43 |
| Corrective 41031 − Ordinary 41031 | +21.8 [16.5, 27.6]; 197; p=2.274e-13 | -6.2 [-10.9, -1.7]; 178; p=0.01921 | +10.5 [6.0, 15.0]; 200; p=5.722e-06 | +93.3 [89.4, 96.7]; 178; p=2.138e-50 |
| Corrective 41032 − Prepared | +19.1 [13.6, 25.0]; 199; p=7.458e-11 | +54.4 [46.7, 62.0]; 171; p=6e-26 | +14.5 [10.0, 19.5]; 200; p=3.725e-09 | +29.2 [22.4, 36.5]; 171; p=1.65e-13 |
| Corrective 41032 − Reminder | +15.1 [10.1, 20.5]; 199; p=1.537e-08 | +45.9 [37.4, 54.3]; 159; p=1.45e-18 | +21.0 [15.5, 26.5]; 200; p=4.547e-13 | +25.2 [18.1, 32.3]; 159; p=1.127e-10 |
| Corrective 41032 − Ordinary 41032 | +30.7 [24.6, 37.2]; 199; p=8.674e-19 | +55.0 [47.4, 62.7]; 169; p=4.847e-27 | +15.5 [10.5, 20.5]; 200; p=9.313e-10 | +27.8 [20.9, 34.9]; 169; p=1.179e-12 |

All cells have zero length stops and zero extra tool calls. Every generated sequence stopped on token 151645. Related conditions and variants remain together in all 5,000 resamples; training seeds do not increase the independent scenario count.
