# PREREG — R44 WAVE-2 CELL B4: p32 blurred tree / p55 ghost tree

**Date: 2026-11-09, written BEFORE first execution.** Cell dir: `analysis/round44/W2-B4-trees/`.
Source: R43 X0 NEW item 30 (`analysis/round43/X0-firewall/ADJUDICATION.md` row 30, convergence 1-2,
prior LOW): "Blurred tree p32 / grey ghost tree p55 … a unique rendering anomaly (one blurred object;
one grey object) never differenced across mirrors or deconvolved."

## Hypothesis

H: one or both tree renderings carry information in the *image domain* — (a) mirror copies differ
non-trivially in the tree region (a swapped/edited plate), (b) the p32 blur conceals legible
structure recoverable by deconvolution, or (c) the p55 grey level encodes more than a single
flat alpha-composite of the black ink.

## Cited ledger rows (verified `not_covered` before running)

- **R30-C1-ART-ATTRIBUTION** (negative): art-attribution only; `not_covered` leaves the trees
  undetermined as *content*; no mirror pixel-diff, no deconvolution anywhere in its evidence.
- **A-06** (measured): ornament *bands* (luminance band reads); trees not in its band census.
- **A-04 / R19-C1**: pixelmatch machinery exists for contested payload bytes only (pp49-51),
  never pointed at p32/p55.
- **R36-O2-SOURCE-ARTIFACT-HUNT** (partially-run): `not_covered` includes "mirror JPEG EXIF/XMP
  diff vs R18-L1 fingerprint" — cross-mirror differencing of these pages is open.
- No LEDGER.json entry (322 scanned for tree/blur/ghost/deconv/p32/p55) runs this. CONFIRMED OPEN.
- Stego channels (LSB/append/carve) are NOT re-run here — R8/R29-L1/R30-A1/A2 cover them; this
  cell is restricted to mirror-diff, blur forensics/deconvolution, and grey-level compositing.

## Inputs (held copies, ignore-blind find; hashes in `runlog.txt`)

p32 (2400x3600 all): relikd master `liber-primus/data/relikd/p32.jpg`
(= byte-identical `corpus/A-primary-artifacts/Hadyn_cicada/2014/ky2khlqdf7qdznac.onion/32.jpg`
 = `corpus/A-primary-artifacts/cijhho123/.../2014onion7/32.jpg`, sha256 c0f77818…);
variants: `wiki-uncovering-cicada/images/32.jpg` (37ff0e87…), `cijhho123/.../liber primus images full/32.jpg` (5543cfce…).
p55: relikd master `p55.jpg` (= onion7 `55.jpg`, a80191…); variants: wiki `55.jpg` (66c16ca4…),
cijhho full `55.jpg` (aec1898f…). Hadyn mirror has no 55.jpg (dir ends at 54.jpg) — noted as a gap.

## Aiming Test

**Q1 — What would a hit look like; would this instrument see it?**
(a) a mirror whose tree region differs beyond recompression noise (localized diff map);
(b) deconvolved p32 tree resolving into glyph/letterforms; (c) p55 grey carrying chroma or
spatially modulated alpha. Each recognizer is validated by a PLANT through the same glue
(PC1–PC4 below) before any real target is scored. A legible emergent readout is
FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md with crops — never certified here.

**Q2 — Measured fact raising the prior?**
Weak but real: the trees are the only two objects in the 58-page book rendered with these two
anomalies (one blurred object; one deliberate grey object), against a pipeline measured as
binary-ink line art everywhere else (R18-L1 toolchain; R30-C1 "processed public-domain
imagery"). X0 row 30 stamps it NEW with prior LOW given the R8/R29/R30 channel record. This is
honestly a **low-prior completeness cell** (P5 tail in CAMPAIGN-PLAN.md) and is labelled as such.

**Q3 — Bounded space?**
ENUMERABLE and tiny: 5 held copies x 2 pages; one blur-type classification; a PSF grid of
<= ~60 kernels (Gaussian sigma in {2..30}, disk r in {2..30} step 2, motion len {5,10,20,40} x 8 angles)
x 2 deconvolvers (Wiener, RL-30it); one 2-parameter compositing model for p55. Total < 300
deconvolutions. Full coverage of the stated grid.

**Q4 — The three conditionals of a negative.**
1. *Key space*: the mirror set held in this repo (5 copies; Hadyn p55 absent), the stated PSF
   grid, and the single-alpha compositing model class.
2. *Decoder transition model*: linear shift-invariant blur only (Wiener/RL cannot represent
   spatially varying or nonlinear blur); diff detects pixel-domain edits only (not semantic
   redraws at identical pixels — vacuous — nor copies never mirrored to us).
3. *Adjudicator register*: human-visual glyph recognition on saved crops + edge/structure
   statistics; if a rune/letter sequence of length >= 30 emerges it is scored with
   `analysis/round19/I2/adjudicate.py` against `bar_v3(N, L, "free")` from
   `analysis/round34/I1-v3-null/bars_v3.py` at the ACTUAL number N of adjudicated readouts
   this cell produces (expected N <= 10; bar computed then, alpha=0.01, stated in RESULTS).

**Q5 — Kill condition at 10% budget.**
If PC1–PC4 all pass AND (mirror diffs are global recompression noise under T1) AND (blur
classifies cleanly Gaussian with stable sigma) AND (the first 10 deconvolutions return only a
sharper tree silhouette with no sub-tree structure), the remaining PSF grid runs to completion
(it is minutes) but no further channels are opened; verdict written measured/negative.

## Fixed thresholds (set BEFORE first run; luminance in 0–255)

- **T1 mirror diff**: anomalous iff p99.9(|dY|) inside the tree bbox >= 2 x p99.9(|dY|) over the
  rest of the page AND >= 8.0 absolute. Below that = recompression noise.
- **T2 blur type**: Gaussian iff radial log-spectrum of the tree region fits a + b*f^2 with
  R^2 >= 0.95 and no >= 2 periodic nulls; disk/motion detected by >= 2 nulls
  (radial / directional). Reported as characterization (no pass/fail).
- **T3 deconvolution flag**: FLAG-FOR-ORACLE iff deconvolved tree bbox contains >= 5 connected
  components with stroke-like aspect (elongation 2–20, area 30–3000 px) that are ABSENT (no
  overlap) from every hallucination-control output at the same PSF, where controls produce < 1
  such novel component each; plus crops saved for the oracle. Otherwise negative.
- **T4 p55 ghost**: anomalous iff mean |chroma| (max channel minus min channel) in the grey tree mask > 2.0, OR
  single-alpha composite residual RMS > 3 x the same-model RMS on a black-ink control region,
  OR alpha varies spatially with coherent (non-edge) structure (see PC4 plant).
- **Text readout** (if any): adjudicate.py pmax vs bar_v3(N_actual, L, "free"), alpha=0.01.

## Positive controls (planted through THIS cell's glue, before real targets)

- **PC1**: relikd p32 + 40x40 block at tree center shifted +10Y, re-encoded JPEG q=85; T1 must fire.
- **PC2**: sharp p32 rune crop blurred with known Gaussian(8), disk(8), motion(20,30 deg); T2
  classifier must label all three correctly.
- **PC3**: rune-text crop Gaussian-blurred at the sigma estimated from the real tree; RL-30
  must restore visually legible runes (edge-energy recovery >= 50% AND saved crop legible).
  **Hallucination control**: same deconvolvers on the sharp rune crop and a blank paper crop —
  must yield < 1 novel stroke-component (T3's control leg).
- **PC4**: synthetic grey tree (alpha=0.35 composite) — model must recover alpha +/- 0.05 with
  residual below T4; a planted spatially-modulated alpha (8 px bands, +/-0.08) must EXCEED T4.

## ADDENDUM 2026-11-09 (during control phase, BEFORE any real-target adjudication)

PC1 FAILED under T1 as written: the planted +10Y/40x40 block lifted tree-bbox p99.9|dY| from
4.0 (clean q85 round-trip) to 10.0, but the "rest of page" reference p99.9 is 11.0 — JPEG
ringing at sharp rune edges swamps a smooth-region edit, so the localization ratio can never
fire for edits below edge-ringing amplitude. The reference population was mis-chosen, not the
plant. **T1 REVISED before scoring any real pair**: reference = p99.9(|dY|) over SMOOTH pixels
outside the tree bbox (master local gradient magnitude < 2.0); fire iff p99.9(tree) >= 8.0 AND
p99.9(tree) >= 2 x p99.9(smooth reference). PC1 must pass and the clean round-trip baseline
must NOT fire under the revised rule. runlog.txt carries the failed run and this re-stamp.

Second refinement, same sitting (still control phase, no real pair scored): "|grad| < 2"
alone still catches JPEG block-artifact bleed just outside glyph edges (smooth-ref p99.9 = 9.0
at dilation 0 vs 1.0 at dilation >= 4; measured, in runlog). Final T1 reference = pixels
outside the tree bbox AND farther than 8 px from any master edge (|grad| >= 2 dilated 8).
PC1 under final rule: tree 10.0 vs ref 1.0 -> fires; clean round-trip 4.0 < 8 -> does not.

## ADDENDUM 2 — 2026-11-09 (control phase; real p32 tree spectrum NOT yet scored)

PC2 FAILED under T2 as written: feature thresholds (ring count / anisotropy / quadratic fit)
are confounded by the OBJECT spectrum — rune text is itself anisotropic (gauss8 plant mislabelled
motion) and past the blur cutoff the spectrum is noise floor (motion plant mislabelled gaussian).
**T2 REVISED to parametric model comparison**: fit P(fy,fx) = A * f^-alpha * |H(f)|^2 + floor on
the 2D log spectrum (coarse grid, f <= 0.35) for H in {Gaussian sigma 1-30, disk r 1-30, motion
L 3-40 x 8 angles}; blur class = argmin SSE over classes; parameter = argmin within class.
PC2 pass condition: all three plants classified correctly AND parameter recovered within +/-25%
(angle +/-15 deg). The real tree is characterized by the winning model + its SSE margin.
No real-target statistic was computed before this revision (the control assert halts the script).

## Budget / outputs

Pure python3 (numpy/scipy/PIL), no network. Outputs: `runlog.txt` (hash-stamped),
`scripts/*.py`, `results/*.json`, `crops/*.png` (exact crops cited), `RESULTS.md`,
`ledger_rows.json`. Verdict vocabulary: measured / negative / flagged-for-oracle;
never "closed".
