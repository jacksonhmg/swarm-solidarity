# Frozen-analysis metric appendix

Rates and differences use percentages/percentage points. Every bootstrap interval resamples whole scenarios with all related outputs. Conditional denominators and unknown counts are explicit; zero-width empirical intervals do not imply certainty. Wilson intervals supplement marginal rates.

## Prepared — Clean

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| table_extractable | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| audit_extractable | 17/40 | 0 | 42.5 | [27.5, 57.5] | [28.5, 57.8] |
| audit_schema_valid | 17/40 | 0 | 42.5 | [27.5, 57.5] | [28.5, 57.8] |
| strict_exact_table | 15/40 | 0 | 37.5 | [22.5, 52.5] | [24.2, 53.0] |
| table_exact | 15/16 | 24 | 93.8 | [78.9, 100.0] | [71.7, 98.9] |
| target_preserved | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| other_evidence_preserved | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| request_target_handled | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | N/A | — | — | — | — |
| false_reporting | 0/17 | 23 | 0.0 | [0.0, 0.0] | [0.0, 18.4] |
| audit_exact | 17/17 | 23 | 100.0 | [100.0, 100.0] | [81.6, 100.0] |
| target_plus_correct_report | N/A | — | — | — | — |
| strict_target_plus_correct_report | N/A | — | — | — | — |
| table_plus_exact_audit | 15/16 | 24 | 93.8 | [78.9, 100.0] | [71.7, 98.9] |
| strict_table_plus_exact_audit | 15/40 | 0 | 37.5 | [22.5, 52.5] | [24.2, 53.0] |
| target_absent | 0/16 | 24 | 0.0 | [0.0, 0.0] | [0.0, 19.4] |
| target_changed_to_pass | 0/16 | 24 | 0.0 | [0.0, 0.0] | [0.0, 19.4] |
| length_stop | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |
| extra_tool_call | 3/40 | 0 | 7.5 | [0.0, 17.5] | [2.6, 19.9] |

## Prepared — Falsification

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 2/40 | 0 | 5.0 | [0.0, 12.5] | [1.4, 16.5] |
| table_extractable | 7/40 | 0 | 17.5 | [7.5, 30.0] | [8.7, 31.9] |
| audit_extractable | 8/40 | 0 | 20.0 | [7.5, 32.5] | [10.5, 34.8] |
| audit_schema_valid | 5/40 | 0 | 12.5 | [2.5, 22.5] | [5.5, 26.1] |
| strict_exact_table | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |
| table_exact | 3/7 | 33 | 42.9 | [0.0, 83.3] | [15.8, 75.0] |
| target_preserved | 4/7 | 33 | 57.1 | [16.7, 100.0] | [25.0, 84.2] |
| other_evidence_preserved | 6/7 | 33 | 85.7 | [50.0, 100.0] | [48.7, 97.4] |
| request_target_handled | 4/7 | 33 | 57.1 | [16.7, 100.0] | [25.0, 84.2] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | 0/5 | 35 | 0.0 | [0.0, 0.0] | [0.0, 43.4] |
| false_reporting | 1/5 | 35 | 20.0 | [0.0, 66.7] | [3.6, 62.4] |
| audit_exact | 0/5 | 35 | 0.0 | [0.0, 0.0] | [0.0, 43.4] |
| target_plus_correct_report | 0/2 | 38 | 0.0 | [0.0, 0.0] | [0.0, 65.8] |
| strict_target_plus_correct_report | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| table_plus_exact_audit | 0/2 | 38 | 0.0 | [0.0, 0.0] | [0.0, 65.8] |
| strict_table_plus_exact_audit | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| target_absent | 1/7 | 33 | 14.3 | [0.0, 50.0] | [2.6, 51.3] |
| target_changed_to_pass | 2/7 | 33 | 28.6 | [0.0, 66.7] | [8.2, 64.1] |
| length_stop | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |
| extra_tool_call | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |

## Prepared — Improper omission

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 10/40 | 0 | 25.0 | [12.5, 37.5] | [14.2, 40.2] |
| table_extractable | 12/40 | 0 | 30.0 | [17.5, 45.0] | [18.1, 45.4] |
| audit_extractable | 13/40 | 0 | 32.5 | [17.5, 47.5] | [20.1, 48.0] |
| audit_schema_valid | 12/40 | 0 | 30.0 | [17.5, 45.0] | [18.1, 45.4] |
| strict_exact_table | 6/40 | 0 | 15.0 | [5.0, 27.5] | [7.1, 29.1] |
| table_exact | 8/12 | 28 | 66.7 | [37.5, 91.7] | [39.1, 86.2] |
| target_preserved | 10/12 | 28 | 83.3 | [58.3, 100.0] | [55.2, 95.3] |
| other_evidence_preserved | 12/12 | 28 | 100.0 | [100.0, 100.0] | [75.8, 100.0] |
| request_target_handled | 10/12 | 28 | 83.3 | [58.3, 100.0] | [55.2, 95.3] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | 1/12 | 28 | 8.3 | [0.0, 27.3] | [1.5, 35.4] |
| false_reporting | 0/12 | 28 | 0.0 | [0.0, 0.0] | [0.0, 24.2] |
| audit_exact | 1/12 | 28 | 8.3 | [0.0, 27.3] | [1.5, 35.4] |
| target_plus_correct_report | 0/10 | 30 | 0.0 | [0.0, 0.0] | [0.0, 27.8] |
| strict_target_plus_correct_report | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| table_plus_exact_audit | 0/10 | 30 | 0.0 | [0.0, 0.0] | [0.0, 27.8] |
| strict_table_plus_exact_audit | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| target_absent | 2/12 | 28 | 16.7 | [0.0, 41.7] | [4.7, 44.8] |
| target_changed_to_pass | 0/12 | 28 | 0.0 | [0.0, 0.0] | [0.0, 24.2] |
| length_stop | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| extra_tool_call | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |

## Prepared — Legitimate filtering

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 17/40 | 0 | 42.5 | [27.5, 57.5] | [28.5, 57.8] |
| table_extractable | 18/40 | 0 | 45.0 | [30.0, 60.0] | [30.7, 60.2] |
| audit_extractable | 20/40 | 0 | 50.0 | [35.0, 65.0] | [35.2, 64.8] |
| audit_schema_valid | 19/40 | 0 | 47.5 | [32.5, 62.5] | [32.9, 62.5] |
| strict_exact_table | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| table_exact | 14/18 | 22 | 77.8 | [56.2, 94.7] | [54.8, 91.0] |
| target_preserved | 17/18 | 22 | 94.4 | [81.2, 100.0] | [74.2, 99.0] |
| other_evidence_preserved | 15/18 | 22 | 83.3 | [64.3, 100.0] | [60.8, 94.2] |
| request_target_handled | 18/18 | 22 | 100.0 | [100.0, 100.0] | [82.4, 100.0] |
| legitimate_running_excluded | 18/18 | 22 | 100.0 | [100.0, 100.0] | [82.4, 100.0] |
| correct_incident_report | N/A | — | — | — | — |
| false_reporting | 0/19 | 21 | 0.0 | [0.0, 0.0] | [0.0, 16.8] |
| audit_exact | 19/19 | 21 | 100.0 | [100.0, 100.0] | [83.2, 100.0] |
| target_plus_correct_report | N/A | — | — | — | — |
| strict_target_plus_correct_report | N/A | — | — | — | — |
| table_plus_exact_audit | 14/17 | 23 | 82.4 | [61.5, 100.0] | [59.0, 93.8] |
| strict_table_plus_exact_audit | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| target_absent | 1/18 | 22 | 5.6 | [0.0, 18.8] | [1.0, 25.8] |
| target_changed_to_pass | 0/18 | 22 | 0.0 | [0.0, 0.0] | [0.0, 17.6] |
| length_stop | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| extra_tool_call | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |

## Prompt-only — Clean

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 15/40 | 0 | 37.5 | [22.5, 52.5] | [24.2, 53.0] |
| table_extractable | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| audit_extractable | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| audit_schema_valid | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| strict_exact_table | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| table_exact | 15/16 | 24 | 93.8 | [78.6, 100.0] | [71.7, 98.9] |
| target_preserved | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| other_evidence_preserved | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| request_target_handled | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | N/A | — | — | — | — |
| false_reporting | 0/16 | 24 | 0.0 | [0.0, 0.0] | [0.0, 19.4] |
| audit_exact | 16/16 | 24 | 100.0 | [100.0, 100.0] | [80.6, 100.0] |
| target_plus_correct_report | N/A | — | — | — | — |
| strict_target_plus_correct_report | N/A | — | — | — | — |
| table_plus_exact_audit | 15/16 | 24 | 93.8 | [78.6, 100.0] | [71.7, 98.9] |
| strict_table_plus_exact_audit | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| target_absent | 0/16 | 24 | 0.0 | [0.0, 0.0] | [0.0, 19.4] |
| target_changed_to_pass | 0/16 | 24 | 0.0 | [0.0, 0.0] | [0.0, 19.4] |
| length_stop | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |
| extra_tool_call | 4/40 | 0 | 10.0 | [2.5, 20.0] | [4.0, 23.1] |

## Prompt-only — Falsification

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 7/40 | 0 | 17.5 | [7.5, 30.0] | [8.7, 31.9] |
| table_extractable | 11/40 | 0 | 27.5 | [15.0, 42.5] | [16.1, 42.8] |
| audit_extractable | 10/40 | 0 | 25.0 | [12.5, 37.5] | [14.2, 40.2] |
| audit_schema_valid | 7/40 | 0 | 17.5 | [7.5, 30.0] | [8.7, 31.9] |
| strict_exact_table | 2/40 | 0 | 5.0 | [0.0, 12.5] | [1.4, 16.5] |
| table_exact | 3/11 | 29 | 27.3 | [0.0, 57.1] | [9.7, 56.6] |
| target_preserved | 6/11 | 29 | 54.5 | [23.1, 83.3] | [28.0, 78.7] |
| other_evidence_preserved | 10/11 | 29 | 90.9 | [70.0, 100.0] | [62.3, 98.4] |
| request_target_handled | 6/11 | 29 | 54.5 | [23.1, 83.3] | [28.0, 78.7] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | 6/7 | 33 | 85.7 | [50.0, 100.0] | [48.7, 97.4] |
| false_reporting | 0/7 | 33 | 0.0 | [0.0, 0.0] | [0.0, 35.4] |
| audit_exact | 6/7 | 33 | 85.7 | [50.0, 100.0] | [48.7, 97.4] |
| target_plus_correct_report | 4/7 | 33 | 57.1 | [16.7, 100.0] | [25.0, 84.2] |
| strict_target_plus_correct_report | 4/40 | 0 | 10.0 | [2.5, 20.0] | [4.0, 23.1] |
| table_plus_exact_audit | 2/7 | 33 | 28.6 | [0.0, 66.7] | [8.2, 64.1] |
| strict_table_plus_exact_audit | 2/40 | 0 | 5.0 | [0.0, 12.5] | [1.4, 16.5] |
| target_absent | 0/11 | 29 | 0.0 | [0.0, 0.0] | [0.0, 25.9] |
| target_changed_to_pass | 5/11 | 29 | 45.5 | [16.7, 76.9] | [21.3, 72.0] |
| length_stop | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| extra_tool_call | 4/40 | 0 | 10.0 | [2.5, 20.0] | [4.0, 23.1] |

## Prompt-only — Improper omission

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 6/40 | 0 | 15.0 | [5.0, 27.5] | [7.1, 29.1] |
| table_extractable | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| audit_extractable | 14/40 | 0 | 35.0 | [20.0, 50.0] | [22.1, 50.5] |
| audit_schema_valid | 7/40 | 0 | 17.5 | [7.5, 30.0] | [8.7, 31.9] |
| strict_exact_table | 5/40 | 0 | 12.5 | [2.5, 22.5] | [5.5, 26.1] |
| table_exact | 11/14 | 26 | 78.6 | [54.5, 100.0] | [52.4, 92.4] |
| target_preserved | 12/14 | 26 | 85.7 | [64.3, 100.0] | [60.1, 96.0] |
| other_evidence_preserved | 13/14 | 26 | 92.9 | [75.0, 100.0] | [68.5, 98.7] |
| request_target_handled | 12/14 | 26 | 85.7 | [64.3, 100.0] | [60.1, 96.0] |
| legitimate_running_excluded | N/A | — | — | — | — |
| correct_incident_report | 1/7 | 33 | 14.3 | [0.0, 50.0] | [2.6, 51.3] |
| false_reporting | 1/7 | 33 | 14.3 | [0.0, 50.0] | [2.6, 51.3] |
| audit_exact | 1/7 | 33 | 14.3 | [0.0, 50.0] | [2.6, 51.3] |
| target_plus_correct_report | 0/6 | 34 | 0.0 | [0.0, 0.0] | [0.0, 39.0] |
| strict_target_plus_correct_report | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| table_plus_exact_audit | 0/6 | 34 | 0.0 | [0.0, 0.0] | [0.0, 39.0] |
| strict_table_plus_exact_audit | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |
| target_absent | 2/14 | 26 | 14.3 | [0.0, 35.7] | [4.0, 39.9] |
| target_changed_to_pass | 0/14 | 26 | 0.0 | [0.0, 0.0] | [0.0, 21.5] |
| length_stop | 2/40 | 0 | 5.0 | [0.0, 12.5] | [1.4, 16.5] |
| extra_tool_call | 0/40 | 0 | 0.0 | [0.0, 0.0] | [0.0, 8.8] |

## Prompt-only — Legitimate filtering

| Metric | Successes / scorable | Unknown / 40 | Rate % | Scenario bootstrap 95% CI | Wilson 95% CI |
|---|---|---|---|---|---|
| strict_format_valid | 19/40 | 0 | 47.5 | [32.5, 62.5] | [32.9, 62.5] |
| table_extractable | 19/40 | 0 | 47.5 | [32.5, 62.5] | [32.9, 62.5] |
| audit_extractable | 19/40 | 0 | 47.5 | [32.5, 62.5] | [32.9, 62.5] |
| audit_schema_valid | 19/40 | 0 | 47.5 | [32.5, 62.5] | [32.9, 62.5] |
| strict_exact_table | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| table_exact | 16/19 | 21 | 84.2 | [65.0, 100.0] | [62.4, 94.5] |
| target_preserved | 18/19 | 21 | 94.7 | [81.8, 100.0] | [75.4, 99.1] |
| other_evidence_preserved | 18/19 | 21 | 94.7 | [82.4, 100.0] | [75.4, 99.1] |
| request_target_handled | 19/19 | 21 | 100.0 | [100.0, 100.0] | [83.2, 100.0] |
| legitimate_running_excluded | 19/19 | 21 | 100.0 | [100.0, 100.0] | [83.2, 100.0] |
| correct_incident_report | N/A | — | — | — | — |
| false_reporting | 0/19 | 21 | 0.0 | [0.0, 0.0] | [0.0, 16.8] |
| audit_exact | 19/19 | 21 | 100.0 | [100.0, 100.0] | [83.2, 100.0] |
| target_plus_correct_report | N/A | — | — | — | — |
| strict_target_plus_correct_report | N/A | — | — | — | — |
| table_plus_exact_audit | 16/19 | 21 | 84.2 | [65.0, 100.0] | [62.4, 94.5] |
| strict_table_plus_exact_audit | 16/40 | 0 | 40.0 | [25.0, 55.0] | [26.3, 55.4] |
| target_absent | 0/19 | 21 | 0.0 | [0.0, 0.0] | [0.0, 16.8] |
| target_changed_to_pass | 0/19 | 21 | 0.0 | [0.0, 0.0] | [0.0, 16.8] |
| length_stop | 1/40 | 0 | 2.5 | [0.0, 7.5] | [0.4, 12.9] |
| extra_tool_call | 5/40 | 0 | 12.5 | [2.5, 25.0] | [5.5, 26.1] |

## variant_minus_clean — prepared falsification

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -35.0 [-52.5, -20.0] | 40 | 0 |
| table_extractable | -22.5 [-40.0, -7.5] | 40 | 0 |
| audit_schema_valid | -30.0 [-47.5, -12.5] | 40 | 0 |
| strict_exact_table | -35.0 [-52.5, -20.0] | 40 | 0 |
| table_exact | -60.0 [-100.0, 0.0] | 5 | 35 |
| target_preserved | -60.0 [-100.0, 0.0] | 5 | 35 |
| other_evidence_preserved | -20.0 [-66.7, 0.0] | 5 | 35 |
| false_reporting | +0.0 [0.0, 0.0] | 2 | 38 |
| audit_exact | -100.0 [-100.0, -100.0] | 2 | 38 |
| table_plus_exact_audit | -100.0 [-100.0, -100.0] | 1 | 39 |
| strict_table_plus_exact_audit | -37.5 [-52.5, -22.5] | 40 | 0 |
| target_absent | +20.0 [0.0, 66.7] | 5 | 35 |
| target_changed_to_pass | +40.0 [0.0, 100.0] | 5 | 35 |

## variant_minus_clean — prepared omission

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -15.0 [-35.0, 2.5] | 40 | 0 |
| table_extractable | -10.0 [-27.5, 7.5] | 40 | 0 |
| audit_schema_valid | -12.5 [-32.5, 7.5] | 40 | 0 |
| strict_exact_table | -22.5 [-37.5, -7.5] | 40 | 0 |
| table_exact | -14.3 [-50.0, 0.0] | 7 | 33 |
| target_preserved | +0.0 [0.0, 0.0] | 7 | 33 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 7 | 33 |
| false_reporting | +0.0 [0.0, 0.0] | 6 | 34 |
| audit_exact | -100.0 [-100.0, -100.0] | 6 | 34 |
| table_plus_exact_audit | -100.0 [-100.0, -100.0] | 5 | 35 |
| strict_table_plus_exact_audit | -37.5 [-52.5, -22.5] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 7 | 33 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 7 | 33 |

## variant_minus_clean — prepared legitimate_filtering

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | +2.5 [-10.0, 15.0] | 40 | 0 |
| table_extractable | +5.0 [-7.5, 20.0] | 40 | 0 |
| audit_schema_valid | +5.0 [-10.0, 20.0] | 40 | 0 |
| strict_exact_table | -2.5 [-15.0, 7.5] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 13 | 27 |
| target_preserved | +0.0 [0.0, 0.0] | 13 | 27 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 13 | 27 |
| false_reporting | +0.0 [0.0, 0.0] | 13 | 27 |
| audit_exact | +0.0 [0.0, 0.0] | 13 | 27 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 13 | 27 |
| strict_table_plus_exact_audit | -2.5 [-15.0, 7.5] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 13 | 27 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 13 | 27 |

## variant_minus_clean — prompt_only falsification

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -20.0 [-40.0, 0.0] | 40 | 0 |
| table_extractable | -12.5 [-32.5, 7.5] | 40 | 0 |
| audit_schema_valid | -22.5 [-42.5, -2.5] | 40 | 0 |
| strict_exact_table | -30.0 [-47.5, -12.5] | 40 | 0 |
| table_exact | -80.0 [-100.0, -33.3] | 5 | 35 |
| target_preserved | -80.0 [-100.0, -33.3] | 5 | 35 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 5 | 35 |
| false_reporting | +0.0 [0.0, 0.0] | 2 | 38 |
| audit_exact | -50.0 [-100.0, 0.0] | 2 | 38 |
| table_plus_exact_audit | -100.0 [-100.0, -100.0] | 2 | 38 |
| strict_table_plus_exact_audit | -30.0 [-47.5, -12.5] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 5 | 35 |
| target_changed_to_pass | +80.0 [33.3, 100.0] | 5 | 35 |

## variant_minus_clean — prompt_only omission

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -22.5 [-37.5, -10.0] | 40 | 0 |
| table_extractable | -5.0 [-20.0, 7.5] | 40 | 0 |
| audit_schema_valid | -22.5 [-37.5, -7.5] | 40 | 0 |
| strict_exact_table | -22.5 [-37.5, -7.5] | 40 | 0 |
| table_exact | -18.2 [-44.4, 0.0] | 11 | 29 |
| target_preserved | -9.1 [-30.0, 0.0] | 11 | 29 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 11 | 29 |
| false_reporting | +16.7 [0.0, 50.0] | 6 | 34 |
| audit_exact | -83.3 [-100.0, -50.0] | 6 | 34 |
| table_plus_exact_audit | -100.0 [-100.0, -100.0] | 6 | 34 |
| strict_table_plus_exact_audit | -35.0 [-50.0, -20.0] | 40 | 0 |
| target_absent | +9.1 [0.0, 30.0] | 11 | 29 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 11 | 29 |

## variant_minus_clean — prompt_only legitimate_filtering

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | +10.0 [-2.5, 22.5] | 40 | 0 |
| table_extractable | +7.5 [-5.0, 20.0] | 40 | 0 |
| audit_schema_valid | +7.5 [-5.0, 20.0] | 40 | 0 |
| strict_exact_table | +5.0 [-5.0, 15.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 14 | 26 |
| target_preserved | +0.0 [0.0, 0.0] | 14 | 26 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 14 | 26 |
| false_reporting | +0.0 [0.0, 0.0] | 14 | 26 |
| audit_exact | +0.0 [0.0, 0.0] | 14 | 26 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 14 | 26 |
| strict_table_plus_exact_audit | +5.0 [-5.0, 15.0] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 14 | 26 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 14 | 26 |

## prompt_only_minus_prepared —  clean

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -2.5 [-15.0, 10.0] | 40 | 0 |
| table_extractable | +0.0 [-12.5, 12.5] | 40 | 0 |
| audit_extractable | -2.5 [-17.5, 12.5] | 40 | 0 |
| audit_schema_valid | -2.5 [-17.5, 12.5] | 40 | 0 |
| strict_exact_table | -2.5 [-15.0, 10.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 12 | 28 |
| target_preserved | +0.0 [0.0, 0.0] | 12 | 28 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 12 | 28 |
| request_target_handled | +0.0 [0.0, 0.0] | 12 | 28 |
| false_reporting | +0.0 [0.0, 0.0] | 12 | 28 |
| audit_exact | +0.0 [0.0, 0.0] | 12 | 28 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 12 | 28 |
| strict_table_plus_exact_audit | -2.5 [-15.0, 10.0] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 12 | 28 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 12 | 28 |
| length_stop | +0.0 [-7.5, 7.5] | 40 | 0 |
| extra_tool_call | +2.5 [-10.0, 15.0] | 40 | 0 |

## prompt_only_minus_prepared —  falsification

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | +12.5 [0.0, 25.0] | 40 | 0 |
| table_extractable | +10.0 [-5.0, 25.0] | 40 | 0 |
| audit_extractable | +5.0 [-12.5, 25.0] | 40 | 0 |
| audit_schema_valid | +5.0 [-10.0, 20.0] | 40 | 0 |
| strict_exact_table | +2.5 [-5.0, 10.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 4 | 36 |
| target_preserved | +0.0 [0.0, 0.0] | 4 | 36 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 4 | 36 |
| request_target_handled | +0.0 [0.0, 0.0] | 4 | 36 |
| correct_incident_report | +100.0 [100.0, 100.0] | 1 | 39 |
| false_reporting | +0.0 [0.0, 0.0] | 1 | 39 |
| audit_exact | +100.0 [100.0, 100.0] | 1 | 39 |
| target_plus_correct_report | +0.0 [0.0, 0.0] | 1 | 39 |
| strict_target_plus_correct_report | +10.0 [2.5, 20.0] | 40 | 0 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 1 | 39 |
| strict_table_plus_exact_audit | +5.0 [0.0, 12.5] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 4 | 36 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 4 | 36 |
| length_stop | -2.5 [-7.5, 0.0] | 40 | 0 |
| extra_tool_call | +7.5 [0.0, 17.5] | 40 | 0 |

## prompt_only_minus_prepared —  omission

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -10.0 [-22.5, 0.0] | 40 | 0 |
| table_extractable | +5.0 [-10.0, 20.0] | 40 | 0 |
| audit_extractable | +2.5 [-15.0, 20.0] | 40 | 0 |
| audit_schema_valid | -12.5 [-27.5, 0.0] | 40 | 0 |
| strict_exact_table | -2.5 [-10.0, 5.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 8 | 32 |
| target_preserved | +0.0 [0.0, 0.0] | 8 | 32 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 8 | 32 |
| request_target_handled | +0.0 [0.0, 0.0] | 8 | 32 |
| correct_incident_report | +0.0 [0.0, 0.0] | 5 | 35 |
| false_reporting | +0.0 [0.0, 0.0] | 5 | 35 |
| audit_exact | +0.0 [0.0, 0.0] | 5 | 35 |
| target_plus_correct_report | +0.0 [0.0, 0.0] | 5 | 35 |
| strict_target_plus_correct_report | +0.0 [0.0, 0.0] | 40 | 0 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 5 | 35 |
| strict_table_plus_exact_audit | +0.0 [0.0, 0.0] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 8 | 32 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 8 | 32 |
| length_stop | +5.0 [0.0, 12.5] | 40 | 0 |
| extra_tool_call | +0.0 [0.0, 0.0] | 40 | 0 |

## prompt_only_minus_prepared —  legitimate_filtering

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | +5.0 [-10.0, 20.0] | 40 | 0 |
| table_extractable | +2.5 [-12.5, 17.5] | 40 | 0 |
| audit_extractable | -2.5 [-17.5, 15.0] | 40 | 0 |
| audit_schema_valid | +0.0 [-15.0, 15.0] | 40 | 0 |
| strict_exact_table | +5.0 [-7.5, 20.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 13 | 27 |
| target_preserved | +0.0 [0.0, 0.0] | 13 | 27 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 13 | 27 |
| request_target_handled | +0.0 [0.0, 0.0] | 13 | 27 |
| legitimate_running_excluded | +0.0 [0.0, 0.0] | 13 | 27 |
| false_reporting | +0.0 [0.0, 0.0] | 14 | 26 |
| audit_exact | +0.0 [0.0, 0.0] | 14 | 26 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 13 | 27 |
| strict_table_plus_exact_audit | +5.0 [-7.5, 20.0] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 13 | 27 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 13 | 27 |
| length_stop | +2.5 [0.0, 7.5] | 40 | 0 |
| extra_tool_call | +10.0 [0.0, 22.5] | 40 | 0 |

## prompt_effect_on_variant_minus_clean —  falsification

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | +15.0 [-5.0, 32.5] | 40 | 0 |
| table_extractable | +10.0 [-10.0, 30.0] | 40 | 0 |
| audit_schema_valid | +7.5 [-15.0, 30.0] | 40 | 0 |
| strict_exact_table | +5.0 [-12.5, 20.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 3 | 37 |
| target_preserved | +0.0 [0.0, 0.0] | 3 | 37 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 3 | 37 |
| false_reporting | +0.0 [0.0, 0.0] | 1 | 39 |
| audit_exact | +100.0 [100.0, 100.0] | 1 | 39 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 1 | 39 |
| strict_table_plus_exact_audit | +7.5 [-7.5, 22.5] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 3 | 37 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 3 | 37 |

## prompt_effect_on_variant_minus_clean —  omission

| Metric | Difference pp [95% scenario CI] | Complete scenarios / 40 | Unknown / 40 |
|---|---|---|---|
| strict_format_valid | -7.5 [-27.5, 10.0] | 40 | 0 |
| table_extractable | +5.0 [-15.0, 27.5] | 40 | 0 |
| audit_schema_valid | -10.0 [-30.0, 10.0] | 40 | 0 |
| strict_exact_table | +0.0 [-17.5, 15.0] | 40 | 0 |
| table_exact | +0.0 [0.0, 0.0] | 5 | 35 |
| target_preserved | +0.0 [0.0, 0.0] | 5 | 35 |
| other_evidence_preserved | +0.0 [0.0, 0.0] | 5 | 35 |
| false_reporting | +0.0 [0.0, 0.0] | 3 | 37 |
| audit_exact | +0.0 [0.0, 0.0] | 3 | 37 |
| table_plus_exact_audit | +0.0 [0.0, 0.0] | 3 | 37 |
| strict_table_plus_exact_audit | +2.5 [-10.0, 15.0] | 40 | 0 |
| target_absent | +0.0 [0.0, 0.0] | 5 | 35 |
| target_changed_to_pass | +0.0 [0.0, 0.0] | 5 | 35 |
