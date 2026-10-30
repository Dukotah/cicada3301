# PRE-REGISTRATION — R10: CORRECTED stylometric-exclusion (true-exclusion-power gate)

**Round 10.** Directly implements the single fix Gate #2 mandated for the INVALID R9. Same EXPLORATORY,
non-decision-grade status; **no positive authorship claim emittable regardless of outcome.**

## What R9 got wrong (fixed here)
R9's operative gate (Control B / FER) measured only *same-author* false-exclusion — the fraction of genuine
author-X chunks exceeding the 99.5th percentile of X's own spread — which is ~0.5% **by definition** and does
NOT test whether the rule can reject a genuinely-different author. R10 adds the missing side.

## Fixed elements (unchanged from R9, reused exactly)
Query = de-contaminated authored LP prose (`data/keys/armada18/lp1_english_forward.txt`): arm1 (koans
excluded) N_q=424; arm2 (all) N_q=729. 10 PD reference authors, ≥3 chunks each. Burrows' Delta + Cosine
Delta. MFW/K from reference-corpora intersection ONLY (LP excluded from the K-defining set), cap 150,
sensitivity K∈{50,100,150}. Seed 3301. Reuse `../r9-01-burrows-delta-exclusion/run_experiment.py` machinery
and the already-assembled corpora (no re-fetch).

## Exclusion rule (unchanged — this is what must be validated)
LP is "excluded from author X" iff Delta(LP, X-centroid) exceeds the **(1 − 0.05/m)=99.5th percentile** of X's
within-author chunk-to-centroid Delta distribution (Holm–Bonferroni over m candidates), **AND** both Burrows
and Cosine Delta agree (concordance).

## NEW operative gate — TWO-SIDED calibration at the exclusion threshold (fixed before LP comparison)
For every author X, using the SAME 99.5th-percentile threshold the LP exclusion uses:
1. **Control B — false-exclusion rate (FER)** [same-author, retained]: fraction of held-out GENUINE X chunks
   wrongly excluded from X. Wilson 95% upper bound. (Kept for completeness; near-tautologically low.)
2. **Control C — impostor false-INCLUSION rate (FIR) / true-exclusion POWER** [cross-author, THE FIX]:
   for every ordered pair (A, X), A≠X, take each chunk of A (a genuine impostor w.r.t. X) and apply the
   exclusion rule against X's centroid+threshold (built from X's own chunks, honest LOO where A shares no
   data with X). **FIR** = fraction of impostor chunks the rule FAILS to exclude from X. **True-exclusion
   power = 1 − FIR.** Report aggregate + per-X, with Wilson 95% CI. (This mirrors the sibling
   `calibration_reject.py`'s 62%-impostor axis, which R9 omitted.)

## DECISION RULE (fixed)
The exclusion tool is trustworthy at N_q **iff BOTH**:
- FER Wilson-upper ≤ **10%** (rarely rejects genuine same-author), AND
- true-exclusion-power Wilson-lower ≥ **80%** (i.e. FIR ≤ ~20% — reliably rejects genuine impostors).
- **If either fails → round verdict NEGATIVE**: at LP's corpus size, a threshold conservative enough to keep
  false-exclusions low cannot also reliably exclude known-wrong authors → LP exclusions are uninterpretable.
  *Predicted outcome*, consistent with the sibling's 62% impostor acceptance: the conservative 99.5th-pct
  threshold will leave true-exclusion power far below 80% → NEGATIVE (the measured small-N exclusion floor on
  LP prose specifically).
- **Only if BOTH pass** → run the LP exclusion step and report per-candidate concordant, family-corrected
  EXCLUSIONS, EXPLORATORY. Even then: no positive attribution; nearest neighbour stays descriptive-only.

## Descriptive context (reported, NOT decision-driving)
A threshold sweep (ROC of FER vs FIR across percentile thresholds) to show whether ANY operating point at N_q
achieves FER≤10% & power≥80% simultaneously. This is descriptive only; the decision above uses the fixed
99.5th-pct threshold that the LP exclusion criterion itself uses (no post-hoc threshold selection).

## Outputs
`results.json`: per-arm/per-K FER, FIR, true-exclusion power (+ Wilson CIs), the ROC table, which decision
branch fired, and — only if reached — the LP exclusion table. Deterministic (seed 3301). Raw corpora stay
gitignored under the R9 dir; no re-fetch.
