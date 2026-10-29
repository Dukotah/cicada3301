# Relation patch proposal (NOT applied; driftbeam.py / beam_v3.py untouched)
Date 2026-10-29. Evidence: RESULTS.md. Files: `relation_skip_by_k.py`, `patch_validation.json`.

1. `keyskipk(k)` (needed for k=4,5; k=3 is already covered by the `free` relation, k=2 by keyskip2): accepted index =
   pa+1+m*k, each rejected position pa+1+t*k must reproduce c_prev; burned positions are unconstrained. The reference
   implementation is standalone (quadgram-scored, beam 200). Validated on EN_MODERN L=120 x 10 plants: skip_by_3/4/5
   recovery 1.0, plus skip_by_two and keyskip1 controls 1.0. To integrate into driftbeam: generalise `pair`/`step_pair=2`
   to `kstep=k` (legal dsk are multiples of k, need = dsk//k, burned-key counting skips the k-1 unconstrained positions).
   Register scoring (v3 panel) is orthogonal and should be attached afterwards (NOVOWEL not tested for the patch).
2. `decode_with_resets(C, K, seg_lens, k)`: a SEGMENTATION wrapper, not a transition relation. Per-segment decode from
   key offset 0, carrying c_prev across the boundary. Validated EN_MODERN: reset_per_line L=120 (10 plants) 1.0,
   reset_per_page 2-page (6 plants) 1.0. Needs a known segment map; the LP2 page map is available, a line map is
   noisier (segmentation was fragile in R12). The same effect is visible as the "oracle segmented rel1" column.

The coordinator must re-run I1's envelope with the new relation before any merge (CAMPAIGN-PLAN I2 deliverable rule).
R4 caveat: the doublet-rate prior does not discriminate any of these from keyskip1 (see RESULTS.md).
