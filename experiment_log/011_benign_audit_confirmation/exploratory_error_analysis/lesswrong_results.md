## Results and limitations

**What improved in both seeds?** On this synthetic teammate task, revised
corrective training improved evidence preservation and appropriate reporting
relative to task-prepared WideSeek, a generic reminder, and matched ordinary
training controls. Both revised seeds preserved the falsification target and the
worker's other useful evidence, and correctly reported the request, in all 200
falsification cases. Whole-table-plus-exact-audit success was 200/200 and 198/200,
versus 57/200 for prepared and 67/200 with the reminder. Explicitly supervising
benign empty audits also greatly reduced the original corrective checkpoints'
indiscriminate accusations, although it did not eliminate them.

**What transferred?** No improper-omission demonstrations were included in
training. On omission requests, the revised seeds preserved the target in
200/200 and 197/199 scorable cases, with one unscorable case in the second seed;
prepared preserved it in 173/199. Strict whole-table-plus-exact-audit success rose
from prepared's 18/200 to 87/200 and 71/200. The paired improvements were 34.5
percentage points [95% CI 27.0, 42.0] and 26.5 [19.5, 33.5]; both also exceeded
the reminder and matched ordinary controls.

An exploratory analysis clarifies what the remaining failures mean. In **107/200
and 79/200** omission cases, the entire table was correct and a single report named
the correct worker and record, but called the request “falsification.” These were
category-only errors, not observed execution of the omission request. They still
fail our unchanged reporting contract and headline metric. Actual target omissions
were zero and two, while explicit empty audits occurred in four and 41 cases.
Compared with the same-seed original corrective checkpoints, the revision improved
omission joint success for one seed (6→87) but reduced it for the other (120→71).

**Was legitimate usefulness preserved?** Not across both seeds. Under the
predeclared five-point non-inferiority margin on whole-table-plus-exact-audit
success, seed 41031 regressed on clean work by 12 points [−17, −7], owing to 36
false accusations. It preserved legitimate filtering, with a difference of −1
point [−3, 1]. Seed 41032 met the margin on both clean work (+1.5 [−1.5, 4.5]) and
legitimate filtering (+1 [0, 2.5]), but still made seven clean false accusations.
We therefore do not claim that the complete selective-cooperation objective held
across seeds, or select the better seed retrospectively.

**What remains unestablished?** These results concern task-prepared WideSeek on
synthetic, replayed teammate messages. They do not establish that MARL caused the
failures, that live swarm capabilities were preserved, or that the intervention
generalizes broadly. The fresh confirmation was motivated by earlier findings and
reused evaluation templates; only two training seeds were tested. One revised
seed used an A100 80 GB while other conditions used 40 GB, limiting attribution
of that comparison exclusively to supervision. Unscorable components remain
unknown, and the 200 underlying scenarios—not the repeated variants or conditions—
are the units of uncertainty. The bounded experiment remains closed, with partial
task-specific transfer but no demonstrated preservation of selective cooperation
across both seeds.
