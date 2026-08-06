# GATE #2 VERDICT — R9-01 Burrows'-Delta Exclusion

## VERDICT: INVALID (process/implementation defect — the operative gate tested the wrong quantity)

**Why INVALID, not NEGATIVE:** NEGATIVE would apply if a *valid* exclusion gate had run and failed. Here the
pre-registered "operative gate" (Control B / false-exclusion rate) measured a **near-tautological** quantity
and passed spuriously, which then *permitted* the exclusion step to run and emit a K-unstable table. The
decision logic ("proceed only if FER upper ≤ 10%") was satisfied by a metric that cannot fail for the reason
it was meant to guard. That voids the exclusion outputs.

### The defect (confirmed against `run_experiment.py`)
- The exclusion rule fires when Delta(LP, X) exceeds the **99.5th percentile of X's own within-author
  distance population**. Control B (FER) then counts genuine same-author chunks exceeding that same 99.5th
  percentile — which is ~0.5% **by definition of a percentile**. FER ≈ 0.5–1% is guaranteed, not evidence.
  Signature confirmed: FER is pinned at 3/300 = 0.01 flat across K∈{50,100,150} — a real discrimination
  metric would move with feature dimension; a percentile identity does not.
- The held chunk IS honestly excluded from its centroid + threshold (not naively circular), but that does
  not matter: **the binding quantity was never measured.** No impostor / cross-author / true-exclusion
  routine exists in the file. The sibling campaign's `calibration_reject.py` measures exactly this and found
  **62% impostor false-inclusion at 359 words** — R9 never ported it. So "FER low + Control A high →
  exclusions trustworthy" is a non-sequitur; neither control constrains the false-INCLUSION rate.

### K-instability (empirical noise signature)
Concordant exclusions flip across K in the same arm; in arm1-K50, **TimothyMay is simultaneously the nearest
neighbour (Δ_burrows 0.894) AND flagged EXCLUDED** — "closest" and "excluded" from the same author at the
same N. No individual exclusion survives the pre-registered K-sweep as robust.

### Query provenance (clean — does not sink the round on its own)
`lp1_english_forward.txt` is the correct de-contaminated authored LP prose; arm2 N_q=729, fw-density 0.501
verified by independent re-tokenization. The 0.50-vs-sibling-0.36 gap is REAL (different token subsets:
sibling measured aphoristic pages; R9 spans dialogue-heavy narrative), NOT a corpus/tokenization artifact.
The density that made Control B "pass" is genuine — it simply doesn't rescue a gate that tests the wrong thing.

### The over-read that is KILLED
"TimothyMay / Cyphernomicon is nearest" is **NOT attribution and NOT a lead.** It is the nearest of ten
arbitrarily-chosen corpora; the same tool excludes it in several cells; at 359–729 words the sibling measured
62% impostor acceptance (a confident nearest match names the wrong entity most of the time). Framing to keep:
*"At LP's corpus size the method cannot distinguish 'nearest real author' from 'nearest of ten strangers, none
of them the author'; TimothyMay being closest is a pool-composition artifact, not evidence he wrote Liber
Primus."*

### Required fix for any future run (owed)
Add the missing operative control: an **impostor false-inclusion / true-exclusion-power test** — take held-out
chunks of author A, apply the exact exclusion rule against every *other* author B's centroid+threshold, and
measure the fraction of genuinely-different-author chunks the rule FAILS to exclude (Wilson-bounded). Gate the
LP step on THAT (mirroring the sibling's 62% axis), not on same-author FER. Predicted outcome, consistent with
the sibling: it fails → the honest NEGATIVE the pre-registration originally forecast (the measured small-N
exclusion floor, on LP prose specifically).

`{"round":"R9-01","verdict":"INVALID","operative_gate_valid":false,"fer_tautological":true,`
`"true_exclusion_power_measured":false,"k_stable_exclusions":false,"query_provenance_clean":true,`
`"positive_attribution_permitted":false,"nearest_neighbor_is_attribution":false}`
