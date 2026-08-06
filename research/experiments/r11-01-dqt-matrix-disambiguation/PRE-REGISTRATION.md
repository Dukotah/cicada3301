# PRE-REGISTRATION — R11: DQT-matrix disambiguation (resolve the R8-S2 INCONCLUSIVE)

**Round 11.** Runs the resolving measurement PRE-SPECIFIED by Round-8 Gate #2 for the S2 INCONCLUSIVE
(so the design is already critic-approved; no fresh Gate #1). **ZERO ciphertext bearing** — this is
production-pipeline forensics only; nothing here can touch the doublet deficit / OTP-class verdict.

## Background
R8-S2 found the two JPEG DQT quantization-table fingerprints (`32386501afff`, 33 pages; `a3a96add050f`,
23 pages) are assigned **strongly non-randomly by page order** (runs z=−4.77, p≈0) but ruled INCONCLUSIVE
because the confound proxy (file byte-size, MW p=0.091) was too weak to exclude content-driven Ghostscript
quantization, and the pattern is blocky/alternating (~11 blocks), not two contiguous batches.

## Measurement (fixed, per R8 Gate #2)
**Part A — dump the two 64-coefficient DQT matrices.** Parse the DQT segments from a representative page of
each group (luma table id 0 + chroma table id 1), de-zigzag to 8×8. Verify all pages within a group share
the identical tables. Then determine the RELATIONSHIP:
- Fit each observed luma/chroma table to the standard JPEG **Annex K** base table under the libjpeg quality
  scaling (Q≥50: scale=200−2Q; Q<50: scale=5000/Q; q=clamp(round((base·scale+50)/100),1,255)). Report the
  best-fit quality Q and residual for each group/table.
- If BOTH groups' tables are Annex-K scalings at different Q (small residual) → **two quality settings of one
  encoder** (a Ghostscript/libjpeg quality switch). If a table is NOT an Annex-K scaling (large residual) or
  the two are structurally unrelated (different zero-pattern / not a common-base scaling) → **two distinct
  encoders/pipelines**.

**Part B — direct content-complexity proxy (replace the weak byte-size proxy).** For every page, decode to
grayscale (PIL) and compute **ink coverage** = fraction of pixels below a fixed luminance threshold (128),
at a fixed downsample width (800 px, ratio preserved) for determinism/speed. This is a DIRECT measure of
rune/content density — the property that actually drives content-dependent quantization — far stronger than
byte size. Mann–Whitney U between the two DQT groups on ink coverage; report U, two-sided p, rank-biserial
effect size, and per-group medians. Re-report the byte-size MW alongside for comparison.

## Decision rule (fixed, from R8 Gate #2)
- If the two groups **DIFFER in ink-coverage complexity** (MW p<0.05) → **NEGATIVE**: the positional DQT split
  is content/complexity-driven (benign Ghostscript behaviour); the R8-S2 positional pattern is explained.
- If the groups are **complexity-INDISTINGUISHABLE** (MW p≥0.05) under this direct proxy → **SURVIVES**: the
  split is a real production/tool signal NOT explained by content (e.g. two rendering passes / two source
  quality settings). Still ZERO ciphertext bearing — a benign production-pipeline observation, not a solve
  path. Part A's matrix relationship is reported as mechanism context either way.
- Honesty guards: (i) even SURVIVES here is benign and non-cipher; (ii) note that the blocky/alternating
  membership (not two contiguous batches) constrains the "two passes" reading regardless of the MW outcome;
  (iii) ink coverage is a strong but not exhaustive complexity proxy — state it.

## Determinism & outputs
Pure byte parsing + fixed-threshold pixel counting at fixed downsample; no RNG. Output → `results.json`
(both DQT matrices, Annex-K best-fit Q + residuals, per-group ink-coverage medians, MW U/p/effect for
ink-coverage AND byte-size, which decision branch fired).
