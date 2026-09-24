# Offline readiness

The proposed supervision gap is confirmed from reconstructed 010 labels matching
all four GPU training metadata hashes. In its corrective dataset, zero benign
task-specific examples supervised an empty audit, while 400 falsification examples
supervised a nonempty audit. All 400 benign aggregation audit suffixes and end
tokens were masked. Separately, 100 empty and 100 nonempty neutral serialization
answers were fully supervised. Ordinary controls masked all 800 benign audits.

The revised encoder uses the exact existing 1,000-example corrective dataset.
All input arrays, prompts, order, padding and 600 falsification/neutral label arrays
are unchanged. Each of the 400 benign examples adds seven loss targets, including
the BPE token `],` spanning the records/audit boundary and the native answer-end
token. No token IDs are split or fabricated. Trailing whitespace and padding stay
masked. Both seeded collated orders (1,000 microbatches) and the actual pinned
causal-loss shift were checked before any GPU rental.

| Per run | Original corrective | Revised corrective |
|---|---:|---:|
| Input tokens | 958,080 | 958,080 |
| Supervised aggregation tokens | 71,694 | 74,494 |
| Supervised falsification tokens | 86,511 | 86,511 |
| Supervised neutral tokens | 24,857 | 24,857 |
| Total supervised tokens | 183,062 | 185,862 |
| Padded input, seed 41031 | 1,100,160 | 1,100,160 |
| Padded input, seed 41032 | 1,103,456 | 1,103,456 |

The addition is 2,800 supervised tokens/run, **+1.53%**, not an equal-token
comparison. The unchanged loss normalizes over all supervised tokens in each
effective batch. Therefore each previously supervised token receives a multiplier
between 0.96251 and 1.0 (seed 41031), or 0.96914 and 1.0 (41032), relative to its
original within-batch weight. Average aggregation/falsification/neutral loss shares
per update change from 39.49/46.41/14.10% to 40.29/45.80/13.92% for 41031, and
39.38/46.55/14.07% to 40.19/45.93/13.88% for 41032. Exact update-level denominators,
shares and example IDs are in `update_loss_weights.jsonl`.

All 200 fresh record sets have zero record-ID and normalized-evidence overlap with
the earlier training, development and final files. Records remain identical across
each scenario's four variants; each worker contributes useful completed evidence.
Gold answers match the supplied evidence. Evaluation note templates deliberately
reuse 010's distribution under the no-prompt-change constraint; these 20 templates
remain separate from training. This is a fresh confirmation after seeing 010,
not an untouched original test. The 1,600 prepared/reminder rendered prompts and
token arrays are saved before execution, along with order and sampling seeds.

The 75-test suite passes. Source-equivalence tests confirm that the training loop
changes only encoder/path references, and inference changes only support/output
paths and two provenance fields. The raw-token/request-association verification
loop is identical to 010. LoRA, optimizer, update count and decoding are unchanged.
The new usefulness criterion uses whole-table-plus-exact-audit success separately
on clean and legitimate filtering, with the predeclared five-point paired margin.

No GPU has been rented and no model has run for 011. The available capacity checks
have not provided matching A100 SXM4 40GB nodes. The recorded-throughput estimate
for eight independently billed nodes is $37.71 including training and 15 minutes
of setup/cleanup per node; the owner-scoped stop trigger is $38 and hard ceiling
is $40. Response-length/runtime variation can still force a bounded partial stop.
The alternative eight-A100-80GB server is approximately $59 at recorded speed;
it requires separate authorization beyond the current $40 limit.
