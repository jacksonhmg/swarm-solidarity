# Checkpoints and immutable dependencies

The six existing conditions reuse the prepared base and the four terminal 010
adapters without retraining. Existing adapters are under
`.local/corrective/{ordinary,corrective}_s{41031,41032}/terminal-adapter/`;
their original metadata and merged-weight hashes remain in experiment 010.

Only `revised_s41031` and `revised_s41032` will be trained, independently from
`.local/preparation/merged-terminal`, and saved under
`.local/revised_corrective/<run>/terminal-adapter/`. They do not resume either old
corrective adapter. Keep all terminal adapters irrespective of their scores.

`merge_revised_base.py` reconstructs the prepared model using the preserved 004
adapter and original public model revision. CPU FP32 merge followed by FP16 save
must match all 13 original prepared file hashes. `merge_revised_adapter.py` applies
one old or revised adapter to that prepared base using the same merge method.
Every old model must also match its 010 merged-weight hashes. New merged hashes are
recorded before evaluation in `execution/merges/<condition>.json`.

Pinned software remains `requirements-preparation.txt`. Actual training configuration
and input/label hashes are recorded in each new training metadata file. Actual
inference entry point, source hashes, FP16/eager/eval mode and all resolved
generation options are recorded for each condition, alongside the raw token arrays.
