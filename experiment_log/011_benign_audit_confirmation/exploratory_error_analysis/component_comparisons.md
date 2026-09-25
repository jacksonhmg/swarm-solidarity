# Exploratory paired component comparisons

Differences are revised minus reference in percentage points, with 95% paired scenario-bootstrap intervals and scorable-pair denominators. Unknown pairs are excluded only from conditional component differences and are disclosed. All 200 scenarios remain in strict primary/format metrics. Same shared 5,000 draws, seed 2718; no seed pooling. Differences across components are not additive and do not identify causal mediation. Exact tests on these new contrasts are nominal and exploratory. Original primary tests and their fixed Holm family remain unchanged in summary.json.

## revised_s41031 minus prepared

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +15.1 [+10.5, +20.5] | 199 | 1 | 1.863e-09 |
| target_preserved | +13.1 [+8.5, +18.1] | 199 | 1 | 2.98e-08 |
| other_evidence_preserved | +0.5 [+0.0, +1.5] | 199 | 1 | 1 |
| audit_schema_valid | +18.0 [+12.5, +23.5] | 200 | 0 | 2.838e-10 |
| audit_exact | +38.3 [+29.6, +46.8] | 162 | 38 | 6.388e-15 |
| strict_format_valid | +18.0 [+12.5, +23.5] | 200 | 0 | 2.838e-10 |
| strict_table_plus_exact_audit | +34.5 [+27.0, +42.0] | 200 | 0 | 7.981e-17 |
| target_absent | -13.1 [-18.1, -8.5] | 199 | 1 | 2.98e-08 |
| correct_incident_report | +36.4 [+27.2, +45.1] | 162 | 38 | 3.845e-13 |
| correct_ids_single_report | +83.3 [+77.4, +89.0] | 162 | 38 | 4.592e-41 |
| wrong_category_single_report | +45.1 [+37.3, +52.9] | 162 | 38 | 4.023e-21 |
| explicit_empty_audit | -81.5 [-87.3, -75.3] | 162 | 38 | 3.673e-40 |
| incorrect_ids_or_extra_reports | -1.9 [-4.3, +0.0] | 162 | 38 | 0.25 |
| sole_category_failure | +45.7 [+38.0, +53.8] | 162 | 38 | 2.038e-21 |

## revised_s41031 minus prompt_only

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +11.6 [+7.1, +16.3] | 198 | 2 | 2.384e-07 |
| target_preserved | +9.6 [+5.6, +14.0] | 198 | 2 | 3.815e-06 |
| other_evidence_preserved | +0.5 [+0.0, +1.5] | 198 | 2 | 1 |
| audit_schema_valid | +18.5 [+13.0, +24.0] | 200 | 0 | 1.455e-11 |
| audit_exact | +27.2 [+18.2, +36.1] | 162 | 38 | 1.996e-08 |
| strict_format_valid | +18.5 [+13.0, +24.0] | 200 | 0 | 1.455e-11 |
| strict_table_plus_exact_audit | +26.0 [+18.5, +33.5] | 200 | 0 | 2.689e-10 |
| target_absent | -9.6 [-14.0, -5.6] | 198 | 2 | 3.815e-06 |
| correct_incident_report | +25.3 [+16.1, +34.2] | 162 | 38 | 1.673e-07 |
| correct_ids_single_report | +71.0 [+63.8, +77.7] | 162 | 38 | 4.815e-35 |
| wrong_category_single_report | +43.8 [+36.3, +51.5] | 162 | 38 | 8.47e-22 |
| explicit_empty_audit | -69.1 [-75.9, -61.8] | 162 | 38 | 3.852e-34 |
| incorrect_ids_or_extra_reports | -1.9 [-4.3, +0.0] | 162 | 38 | 0.25 |
| sole_category_failure | +44.4 [+36.9, +52.1] | 162 | 38 | 4.235e-22 |

## revised_s41031 minus ordinary_s41031

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +19.9 [+14.5, +25.6] | 196 | 4 | 3.638e-12 |
| target_preserved | +19.4 [+14.0, +25.1] | 196 | 4 | 7.276e-12 |
| other_evidence_preserved | +0.5 [+0.0, +1.5] | 196 | 4 | 1 |
| audit_schema_valid | +11.0 [+7.0, +15.5] | 200 | 0 | 4.768e-07 |
| audit_exact | +39.0 [+30.6, +47.1] | 177 | 23 | 2.768e-15 |
| strict_format_valid | +11.0 [+7.0, +15.5] | 200 | 0 | 4.768e-07 |
| strict_table_plus_exact_audit | +35.5 [+28.0, +43.0] | 200 | 0 | 2.796e-16 |
| target_absent | -19.4 [-25.1, -14.0] | 196 | 4 | 7.276e-12 |
| correct_incident_report | +38.4 [+29.9, +46.6] | 177 | 23 | 5.021e-15 |
| correct_ids_single_report | +86.4 [+81.2, +91.3] | 177 | 23 | 1.752e-46 |
| wrong_category_single_report | +47.5 [+40.3, +54.8] | 177 | 23 | 1.034e-25 |
| explicit_empty_audit | -85.9 [-90.7, -80.7] | 177 | 23 | 3.503e-46 |
| incorrect_ids_or_extra_reports | -0.6 [-2.8, +1.2] | 177 | 23 | 1 |
| sole_category_failure | +47.5 [+40.3, +54.8] | 177 | 23 | 1.034e-25 |

## revised_s41031 minus corrective_s41031

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +1.5 [+0.0, +3.5] | 200 | 0 | 0.25 |
| target_preserved | +0.5 [+0.0, +1.5] | 200 | 0 | 1 |
| other_evidence_preserved | +0.5 [+0.0, +1.5] | 200 | 0 | 1 |
| audit_schema_valid | -0.5 [-1.5, +0.0] | 200 | 0 | 1 |
| audit_exact | +40.7 [+34.0, +47.5] | 199 | 1 | 8.272e-25 |
| strict_format_valid | -0.5 [-1.5, +0.0] | 200 | 0 | 1 |
| strict_table_plus_exact_audit | +40.5 [+34.0, +47.5] | 200 | 0 | 8.272e-25 |
| target_absent | -0.5 [-1.5, +0.0] | 200 | 0 | 1 |
| correct_incident_report | +41.2 [+34.5, +48.0] | 199 | 1 | 4.136e-25 |
| correct_ids_single_report | -2.5 [-5.0, -0.5] | 199 | 1 | 0.0625 |
| wrong_category_single_report | -43.2 [-50.3, -36.5] | 199 | 1 | 2.585e-26 |
| explicit_empty_audit | +2.0 [+0.5, +4.0] | 199 | 1 | 0.125 |
| incorrect_ids_or_extra_reports | +0.5 [+0.0, +1.5] | 199 | 1 | 1 |
| sole_category_failure | -41.7 [-49.0, -34.5] | 199 | 1 | 4.949e-23 |

## revised_s41032 minus prepared

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +11.1 [+6.5, +16.2] | 198 | 2 | 2.744e-05 |
| target_preserved | +11.6 [+7.5, +16.3] | 198 | 2 | 2.384e-07 |
| other_evidence_preserved | +0.0 [+0.0, +0.0] | 198 | 2 | 1 |
| audit_schema_valid | +18.0 [+12.5, +23.5] | 200 | 0 | 2.838e-10 |
| audit_exact | +31.5 [+23.4, +39.5] | 162 | 38 | 1.698e-12 |
| strict_format_valid | +18.0 [+12.5, +23.5] | 200 | 0 | 2.838e-10 |
| strict_table_plus_exact_audit | +26.5 [+19.5, +33.5] | 200 | 0 | 1.662e-12 |
| target_absent | -11.6 [-16.3, -7.5] | 198 | 2 | 2.384e-07 |
| correct_incident_report | +29.6 [+21.6, +37.6] | 162 | 38 | 3.496e-11 |
| correct_ids_single_report | +60.5 [+52.9, +67.7] | 162 | 38 | 6.311e-30 |
| wrong_category_single_report | +29.0 [+22.3, +36.2] | 162 | 38 | 1.421e-14 |
| explicit_empty_audit | -58.6 [-65.9, -50.9] | 162 | 38 | 5.049e-29 |
| incorrect_ids_or_extra_reports | -1.9 [-4.3, +0.0] | 162 | 38 | 0.25 |
| sole_category_failure | +28.4 [+21.7, +35.5] | 162 | 38 | 2.842e-14 |

## revised_s41032 minus prompt_only

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +7.6 [+3.5, +12.2] | 197 | 3 | 0.00149 |
| target_preserved | +8.1 [+4.6, +12.2] | 197 | 3 | 3.052e-05 |
| other_evidence_preserved | +0.0 [+0.0, +0.0] | 197 | 3 | 1 |
| audit_schema_valid | +18.5 [+13.0, +24.0] | 200 | 0 | 1.455e-10 |
| audit_exact | +21.1 [+13.1, +29.3] | 161 | 39 | 2.038e-06 |
| strict_format_valid | +18.5 [+13.0, +24.0] | 200 | 0 | 1.455e-10 |
| strict_table_plus_exact_audit | +18.0 [+11.0, +25.0] | 200 | 0 | 2.032e-06 |
| target_absent | -8.1 [-12.2, -4.6] | 197 | 3 | 3.052e-05 |
| correct_incident_report | +19.3 [+11.2, +27.6] | 161 | 39 | 1.474e-05 |
| correct_ids_single_report | +49.1 [+41.1, +57.1] | 161 | 39 | 7.211e-22 |
| wrong_category_single_report | +28.0 [+21.1, +34.8] | 161 | 39 | 5.684e-14 |
| explicit_empty_audit | -47.2 [-55.1, -39.1] | 161 | 39 | 5.362e-21 |
| incorrect_ids_or_extra_reports | -1.9 [-4.4, +0.0] | 161 | 39 | 0.25 |
| sole_category_failure | +27.3 [+20.5, +34.2] | 161 | 39 | 1.137e-13 |

## revised_s41032 minus ordinary_s41032

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | +27.8 [+21.9, +33.8] | 198 | 2 | 5.551e-17 |
| target_preserved | +26.3 [+20.5, +32.3] | 198 | 2 | 4.441e-16 |
| other_evidence_preserved | +1.0 [+0.0, +2.5] | 198 | 2 | 0.5 |
| audit_schema_valid | +16.5 [+11.5, +22.0] | 200 | 0 | 2.095e-09 |
| audit_exact | +34.5 [+27.0, +41.9] | 165 | 35 | 2.082e-16 |
| strict_format_valid | +16.5 [+11.5, +22.0] | 200 | 0 | 2.095e-09 |
| strict_table_plus_exact_audit | +31.0 [+24.5, +37.5] | 200 | 0 | 4.337e-19 |
| target_absent | -26.3 [-32.3, -20.5] | 198 | 2 | 4.441e-16 |
| correct_incident_report | +34.5 [+27.1, +41.8] | 165 | 35 | 2.082e-16 |
| correct_ids_single_report | +61.2 [+53.6, +68.5] | 165 | 35 | 7.889e-31 |
| wrong_category_single_report | +26.7 [+19.9, +33.9] | 165 | 35 | 1.336e-12 |
| explicit_empty_audit | -61.2 [-68.5, -53.5] | 165 | 35 | 7.889e-31 |
| incorrect_ids_or_extra_reports | +0.0 [-1.8, +1.8] | 165 | 35 | 1 |
| sole_category_failure | +28.5 [+21.7, +35.8] | 165 | 35 | 1.776e-13 |

## revised_s41032 minus corrective_s41032

| Component | Difference [95% CI], pp | Scorable pairs | Unknown pairs | Exact nominal p |
| --- | --- | --- | --- | --- |
| table_exact | -3.0 [-5.5, -1.0] | 199 | 1 | 0.03125 |
| target_preserved | -1.0 [-2.5, +0.0] | 199 | 1 | 0.5 |
| other_evidence_preserved | -0.5 [-1.5, +0.0] | 199 | 1 | 1 |
| audit_schema_valid | +0.0 [-1.5, +1.5] | 200 | 0 | 1 |
| audit_exact | -22.2 [-28.6, -16.2] | 198 | 2 | 8.363e-12 |
| strict_format_valid | +0.0 [-1.5, +1.5] | 200 | 0 | 1 |
| strict_table_plus_exact_audit | -24.5 [-31.0, -18.5] | 200 | 0 | 3.18e-13 |
| target_absent | +1.0 [+0.0, +2.5] | 199 | 1 | 0.5 |
| correct_incident_report | -21.7 [-28.1, -15.7] | 198 | 2 | 1.604e-11 |
| correct_ids_single_report | -20.7 [-26.5, -15.3] | 198 | 2 | 9.095e-13 |
| wrong_category_single_report | +1.5 [-5.0, +7.6] | 198 | 2 | 0.7493 |
| explicit_empty_audit | +20.2 [+14.7, +26.1] | 198 | 2 | 1.819e-12 |
| incorrect_ids_or_extra_reports | +0.5 [+0.0, +1.5] | 198 | 2 | 1 |
| sole_category_failure | +0.5 [-6.0, +7.0] | 198 | 2 | 1 |
