# PRE-REGISTRATION — R8-S2: JPEG DQT page-membership (production-batch / OPSEC signal)

**Registered:** Round 8, BEFORE the significance test was computed and threshold fixed. (Critic Gate #1
noted a preliminary runs count of ~11; the decision threshold below is a standard fixed criterion set
here, not moved after seeing data. Execution re-derives all numbers deterministically.)

**Hypothesis (security-researcher lane):** The two distinct JPEG quantization-table fingerprints across
the 56 pages (recorded in `analysis/stego/out_authentic/results.json` but never tabulated by page) are
either (a) POSITIONALLY clustered — indicating the book was rendered in ≥2 production batches/passes, a
production/OPSEC signal — or (b) scattered w.r.t. page order — a benign content/complexity-driven
Ghostscript artifact.

## Test statistic (fixed)
- Sequence: pages ordered p0…p55; each labelled by its `dqt_fingerprint` → binary group (n0, n1 fixed).
- **Primary statistic: Wald–Wolfowitz runs count R** over that ordered binary sequence.
- **Null model:** random permutations of the FIXED label multiset (n0 zeros, n1 ones), Monte-Carlo,
  100,000 permutations, seed 3301, plus the analytic W–W normal approximation as a cross-check.
- **Decision threshold (fixed):** two-sided Monte-Carlo p < 0.001 ⇒ the split is POSITIONALLY clustered
  (reject "random arrangement"). Single primary hypothesis (page order) ⇒ no Bonferroni needed for the
  primary decision. Any secondary boundary-alignment claims are reported DESCRIPTIVELY only, not as
  additional significance tests.

## Pre-registered CONFOUND check (decisive for interpretation)
Positional clustering is necessary but NOT sufficient for "two production batches": Ghostscript may
switch quantization tables by image content, and content complexity can itself trend with page index.
Therefore, fixed in advance:
- Record per-page `size` (JPEG byte length; complexity proxy) and compute Mann–Whitney U between the two
  DQT groups.
- Compute Spearman ρ between page index and `size`.
- **Interpretation rule (fixed):**
  - If R is significantly low (p<0.001) AND the two groups do NOT differ in `size` (MW p>0.05) →
    positional split is NOT complexity-explained → **SURVIVES as a production-batch signal** (report as a
    forensic observation; still not a cipher lead).
  - If R is significantly low AND groups differ strongly in `size` AND `size` trends with page index →
    the positional split is CONFOUNDED by content complexity → **INCONCLUSIVE** on the batch claim
    (report the raw positional fact + the confound).
  - If R is not significant → **NEGATIVE** (benign scattered artifact).

## Predictions
- Batch/OPSEC true → R low, groups complexity-indistinguishable, boundary near a section edge.
- Benign → R ≈ E[R], or groups differ in complexity (content-driven).

## Determinism
Seed 3301 for the Monte-Carlo permutation null. Output → `results.json` in this dir.
