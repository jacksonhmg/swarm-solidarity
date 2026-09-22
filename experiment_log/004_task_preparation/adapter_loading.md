# Prepared checkpoint identity and loading

The prepared checkpoint is the pair:

1. `RLinf/WideSeek-R1-4b` at revision
   `c06cbf9fd40bf376fbc9379baa40e759c3e65cd5`.
2. The single terminal LoRA adapter produced after exactly 125 updates, preserved
   on this Mac at `.local/preparation/terminal-adapter/` in the repository root.

After successful training, `training/metadata.json` records each adapter file's
SHA-256, trainable parameters, exact update count and runtime. The final report
will confirm preservation; these instructions alone are not evidence of success.
The adapter contains learned deltas, not a standalone replacement for the base.
Binary checkpoint files stay outside Git; the manifest and loading instructions
are committed. Back up that directory before cleaning `.local/`.

Use PyTorch 2.8.0, Transformers 4.55.2 and PEFT 0.17.1. For trainable adapter
loading on the original BF16 base (no training is performed by this snippet):

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_id = "RLinf/WideSeek-R1-4b"
revision = "c06cbf9fd40bf376fbc9379baa40e759c3e65cd5"
tokenizer = AutoTokenizer.from_pretrained(base_id, revision=revision)
base = AutoModelForCausalLM.from_pretrained(
    base_id, revision=revision, torch_dtype=torch.bfloat16,
    attn_implementation="sdpa",
)
prepared = PeftModel.from_pretrained(
    base, ".local/preparation/terminal-adapter", is_trainable=True,
)
```

Both potential later training arms must start from the identical base/adapter
pair, including all learned deltas; never initialize a fresh adapter and discard
this preparation. Their optimizer/training details would need a separate protocol.

The actual clean evaluation uses a **CPU FP32 merge, then an FP16 saved model**,
not live BF16 adapter inference. `scripts/merge_preparation.py` implements that
exact conversion, verifies terminal adapter hashes and saves the merged-weight
manifest to `training/merge.json`. It refuses to overwrite existing merged weights.
On a suitable machine with the pinned dependencies and downloaded terminal
adapter, run only if regeneration is needed:

```sh
python scripts/merge_preparation.py
```

Inference uses the pinned base tokenizer and saved native chat template; the
unchanged replay prompt ends at a bare assistant prefix. See
`configs/prepared-evaluation.json` for exact decoding. No extra generation is
needed to verify preservation: validate the file hashes in `training/metadata.json`.
Do not rerun the clean evaluation, tune from conflict outcomes, or start further
training without a separately authorized experiment.
