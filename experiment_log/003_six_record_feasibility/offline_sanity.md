# Offline sanity check of the earlier cases

Compared the twelve-scenario comparison with the forty-scenario confirmation using
saved rendered prompts and input token counts, before any new GPU allocation.
For prompt length, compare only the identical JSON interface, not the three other
comparison formats.

| Measurement | Comparison JSON (12) | Confirmation JSON (40) |
|---|---:|---:|
| Input tokens, mean | 1,135.58 | 1,135.05 |
| Input tokens, range | 1,129–1,143 | 1,128–1,145 |
| Source records per case | 12 | 12 |
| Required completed records per case | 9 | 9 |
| Record order | Ascending ID, grouped by worker | Ascending ID, grouped by worker |

The mean length difference is 0.53 tokens (under 0.05%); the ranges overlap.
There is no material difference in these three properties. Record values and
worker identities differ as intended for fresh data.

Parsed every source-record JSON line from **all 88 saved prompts** (48 comparison
and 40 confirmation outputs). Their record multisets exactly match the case data,
every worker message is present, and independently filtering the supplied evidence
to completed records yields exactly the expected answer. All expected audits are
empty. **No verified evidence/answer mismatch or ordering discrepancy was found.**
This does not establish why the checkpoint failed; no speculative follow-up
inference was performed. Exact measurements are in [offline_sanity.json](offline_sanity.json).
