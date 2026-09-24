# Validation-only correction before any model inference

The initial runner reached Transformers' `_get_logits_processor` and its assertion
requiring an empty list failed. Zero responses and zero generated tokens were
saved. The stack trace stops in `generate` configuration preparation, before
`_sample`; the pinned decoder-only path has not called the model forward or
sampled tokens at this point. One request-start journal entry exists and is
preserved; it is not hidden or classified as a model-performance failure.

The initial offline test omitted `_prepare_generated_length`. With the frozen
`min_new_tokens=0`, that method sets `min_length` to the prompt length, leading
to a `MinLengthLogitsProcessor`. Its implementation masks EOS only when current
length is less than the prompt length. At every reachable generation step it
returns an exact clone of the scores and therefore imposes no restriction.

The corrected offline test follows the actual configuration preparation order,
checks the sole processor and its threshold, and confirms bitwise score identity
at the prompt length and longer lengths. No forward pass or token sampling is
used in this test. The observer now permits and archives this verified inert
processor. It still rejects any actual sampling restriction. The observer does
not remove, replace or modify any processor.

The complete inference configuration, merged weights, inputs, seeds, stopping,
decoding, attention backend, scorer and gates remain byte-identical. No performance
result has been seen or used to select anything. Preserve the original freeze,
runner source, initial controller receipt and aborted stage under this experiment.
Freeze the corrected validation code before the first sampled response. Use the
same owned GPU and the remaining original 180-minute controller deadline and $10
cap. This is a setup-assertion repair before inference, not a retry of a generated
case or a configuration search. Every authorized case may still be sampled only
once, with the original conditional forty-plus-forty limit.

The original protocol and preflight are retained as historical artifacts; their
empty-processor-list statement is superseded by this explicit correction. The
new freeze records the unchanged configuration hash and the only changed runtime
source. Exact H100 reproduction remains untested; corrective training stays paused.
