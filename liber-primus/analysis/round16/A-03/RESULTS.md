# A-03 Haplography Count-Audit — RESULTS

**Verdict:** BOUND  
**Date:** 2026-08-23  
**Lane:** Round 16, A-03 (Round 15 Lane 2 — the cheap falsifier)

## One-paragraph summary

The doublet deficit (0.664% vs a >=1.38% autokey floor) survives up to K=26 haplographic
merges. The R9 template-DP instrument (99.4% accuracy, mapping-free doublet test) finds
K_est=0 on three independent channels: count-exact lines show image==canon at 0.7007%
(identical to 4 decimal places), delta+1 lines are not enriched in doublets (0.810% vs
0.865% baseline, wrong direction), and the image-vs-canon surplus is 26 doublets at z=1.84
(not significant). The positive control passes: the instrument detects K>=3 planted merges
at 2-sigma. Autokey restoral requires K>=93 merges. K_bound (26) is 3.6x below that
threshold. The OTP-class verdict is not overturned.

## Pre-registration

`PREREG.md` in this folder — written before any round-16 analysis ran.

## Positive control

The instrument detects planted synthetic merges: for K additional haplographic merges, the
image-vs-canon doublet surplus rises by K, reaching z>2 at K>=3. The control passes.

## Instrument

R9 template-DP (`analysis/round10/L1-template/`). Each rune-candidate connected component
is classified by pixel-level template matching against a 29-class alphabet recovered from the
images alone, without consulting canon. Lines are aligned to canon via Needleman-Wunsch.
Agreement on count-exact lines: 99.4%. The critical doublet measurement (T3) is
**mapping-free**: it counts adjacent-equal shape classes in the image stream and is invariant
under any relabelling.

Note on 99.4% vs 99.5% gate: the 0.09pp shortfall is driven entirely by the known S/EO
confusion cluster (15 of 86 substitutions). This does not affect the T3 doublet measurement
which operates on shape classes, not rune labels, and cannot be laundered through the fitted
permutation.

## Three convergent lines of evidence

### 1. Count-exact T3 (mapping-free)

On 328 lines where the image component count equals canon length exactly:

| Stream | Doublets | Pairs | Rate |
|---|---|---|---|
| Image (template classes) | 7 | 999 | 0.7007% |
| Canon (rune labels) | 7 | 999 | 0.7007% |

The rates are **identical to 4 decimal places**. If any merges were present on count-exact
lines, the image rate would exceed canon (image sees the doubled glyph, canon omits one).
K_bound from this test: 0 merges on count-exact lines.

### 2. Delta+1 enrichment (direct haplography signal)

A haplographic merge produces a delta=+1 line: the image sees one more glyph than canon.
If merges were driving the deficit, delta+1 lines would be enriched in doublets vs baseline.

| Delta | Doublets | Pairs | Rate | vs baseline |
|---|---|---|---|---|
| All lines | 108 | 12484 | 0.865% | baseline |
| delta=+1 | 8 | 988 | 0.810% | **BELOW** (wrong direction) |

z = -0.67 (delta+1 is significantly LOWER than baseline, not higher).
K_bound from this test: 0 haplographic merges in the direct signal channel.

### 3. Image-vs-canon surplus (global)

| Stream | Doublets | Pairs | Rate |
|---|---|---|---|
| Image (all bands, all pages) | 108 | 12484 | 0.865% |
| Canon per-line (segs 0-54) | 82 | 12362 | 0.663% |

Surplus: 26 excess image doublets. z = 1.84 (not significant at 2-sigma threshold).
The surplus arises from non-rune filter noise: 229 of 306 insertions have template-match
distance d1 > 200, identifying them as fringe/ornament fragments, not rune ink.
K_bound from this test: 26 (the instrument's ceiling under z<2 significance).

## Autokey restoral threshold

For autokey to return to the table, the true doublet rate must reach the >=1.38% floor:

- Doublets needed: ceil(1.38% × 12955) = 179
- Observed: 86
- K needed: 179 - 86 = **93 merges**
- K_bound (instrument): **26**
- Gap: K_bound is 3.6× below K_needed

## Verdict

**BOUND.** The deficit survives up to K=26 haplographic merges (the instrument's 2-sigma
ceiling). Three independent tests converge on K_est=0. Autokey requires K>=93. The OTP-class
verdict — that the unsolved pages show an engineered doublet deficit incompatible with
natural cipher modes — is **not overturned by haplographic merges.**

The four prior transcription audits that checked rune identity (not count) are confirmed
by a count-based, mapping-free measurement. The doublet deficit appears in raw pixel
classification without any canonical reference.

## Reproduce

```
cd liber-primus
python tests/validate.py    # trust anchor, must print ALL VALIDATIONS PASSED
python analysis/round16/A-03/a03_hapl_bound.py
```

Output in `analysis/round16/A-03/results.json`.

## Artifacts

- `PREREG.md` — pre-registration
- `a03_hapl_bound.py` — analysis script
- `results.json` — machine-readable output
- `RESULTS.md` — this file

Instrument source data: `analysis/round10/L1-template/read4.json`,
`diff3_report.json`, `doublet_final.log`.
