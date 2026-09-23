# Bounded reproduction check

This is a separate diagnostic. Experiment 005 remains closed; corrective
training remains paused. No task changes, new records, preparation, additional
training, configuration sweep or performance-driven retry is authorized.

1. Inspect the recorded execution of 004 and 005 offline: loader, effective
   engine settings, seeds, stopping, order, response association and scoring.
   Distinguish logged facts, source-derived expectations and unverified causes.
2. Use only the original **single H100 PCIe** hardware type. Stop if unavailable;
   do not substitute an A100, H100 SXM or a multi-GPU instance.
3. If available within the $10 additional cap, replay the exact forty saved 004
   prompt strings in their saved request order, with their saved sampling seeds,
   prepared checkpoint, original scorer and clean-only batches of 24 and 16.
   Reconstruct token IDs with the pinned tokenizer because the original runner
   did not retain its token arrays. Verify actual engine input IDs against that
   reconstruction; preserve raw output IDs, request IDs, finish/stop reasons and
   resolved engine/per-request sampling objects. Record this archival limitation
   rather than claiming the original arrays were saved.
4. Only if replay reaches **36/40 strict exact tables and 38/40 valid outputs**,
   run the forty saved 005 prepared-baseline clean prompts once, preserving each
   original seed and their relative saved order. Use the same restored settings
   and fresh clean-only engine arrangement (24 + 16; no conflict or prompt-only
   requests). Compare raw text bytes and original scores. Byte identity is a
   diagnostic, not an additional gate. Maximum total: 80 generated responses.
5. Preserve the original bootstrap estimate and add exactly one two-sided exact
   McNemar test for 005's four-versus-zero **strict target preserved + correct
   report** falsification successes. No search across other metrics.
6. Stop after reporting. No automatic corrective training, rerun, availability
   monitor or repetition of the 320-response experiment.

If rental were possible, retain the existing owner-scoped cloud state and
sleep-inhibited watchdog, request termination at $8 to reserve $2 for shutdown,
and bound remote setup/merge/inference at 90 minutes. At the quoted $3.29/hour,
90 minutes costs $4.935 before tax, leaving headroom under $10. Recheck the live
price before launch and stop if the frozen work cannot fit. No instance was
launched: the initial matching-hardware capacity check returned no regions.

The input files under `inputs/` are execution manifests copied from saved prompts,
with reconstructed token arrays; they are not a new dataset. No prompt builder or
record generator is used. The token reconstruction and association audit ran
locally; all old artifacts and scores are preserved.
