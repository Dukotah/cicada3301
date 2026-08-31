# Round 22 — Lane D — Illustration / drop-cap channel (roadmap S3)

_Pre-registration. Written before scoring. Binding: `../../../ARMADA-DOCTRINE.md`._

## Hypothesis

Do the Liber Primus illustrations vary in a **data-bearing** way — specifically:
does the pattern of **illuminated drop-caps** (which pages carry one, in what order,
which rune is illuminated) encode a message, tested against a size-matched null?

"All is sacred," and nobody has ever coded the art as data (roadmap S3, the lowest-prior
of Round 22's four novel lanes — queued last, but ahead of any PRNG re-sweep).

## Asset availability (assessed FIRST, per the lane brief)

**The illustration data EXISTS in the repo and is machine-extractable — this lane is NOT
blocked-on-assets.** Findings:

- **Full per-page scans are committed**: `corpus/E-tooling/vendor/cmbsolver__cmbcidada3301/
  LiberPrimusUi/input/images/LP/0.jpg … 57.jpg` (58 pages, 2400×3600 each); an identical
  set is at `.../henkman__liberprimus/originals/`. ImageMagick + PIL/numpy are available.
- **No illustration inventory / drop-cap catalog / motif table existed** anywhere in the
  repo before this lane. The only prior art-as-data work is the vision re-transcription
  avenue (`analysis/vision/AVENUE-1-VISION-VERDICT.md`), which is CLOSED: page-scale AI OCR
  of the ~250 dense runes/page is unreliable (0.145 alignment). **That caveat does not block
  this lane** — a drop-cap is one *large* illuminated glyph, and it is printed in RED while
  every other glyph is black, so it is separable by a colour mask with no OCR at all.
- **The illuminated rune's identity** is recoverable *exactly* from the canonical per-page
  rune strings (`analysis/vision/canonical_pages.json`), because the drop-cap is the first
  body rune of the page. The image only supplies the has-drop-cap gate (validated).

So the honest outcome is a **runnable lane**, not an asset gap.

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit is a non-random pattern in the drop-cap channel. Recognizers, written before the run:
(S1) the presence bitstring compresses better than the null (a code); (S2) the gaps between
illuminated pages are non-uniform beyond null (clustered/periodic); (S3) the count of
illuminated pages hits a distinguished value (prime, 29, 3301-flavoured); (S4) a monotone/
periodic trend in a per-page integer feature (red centroid) beyond a shuffle; (S5) the
illuminated-rune sequence reads as English / lower-entropy than a random alphabet draw.
The extractor + `test_order.py` + `test_illuminated_runes.py` compute all five.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Weak but real: the drop-caps are deliberately set apart (red ink, one per page, not every
page) — an authored, non-uniform channel that the black-rune stream cannot see. The signed
hint "all is sacred" points at the whole physical artifact, not only the runes. This is the
*lowest* prior of Round 22's four lanes and is labelled a near-completeness ritual (doctrine
Q2): it queues last, but it reads a channel nobody has ever coded, and it returns a novel
artifact (the first drop-cap catalog of LP2) even on a null.

**Q3 — Is the space bounded, and by what?**
Fully bounded and enumerable: 58 pages × {has-cap, which of 29 runes, centroid, blob count}.
The feature space is a finite, human-checkable object (doctrine R5 rank 1).

**Q4 — The three conditionals the negative carries.**
(1) key space = the drop-cap presence/identity/position channel only, over the 58 committed
scans; (2) decoder = colour-mask extraction + first-rune-of-page identity (no dense-rune OCR,
which is separately known unreliable); (3) adjudicator = five order/structure statistics vs a
seed-3301 shuffle at the p<0.01 Bonferroni bar, plus an English/entropy read of the runes.

**Q5 — Kill condition at 10% of budget.**
If the red-channel signal were not separable (no clean has-cap tier) the lane dies immediately.
It IS separable (cross-page probe: pages split into >30k-px caps, ~1k-px speckle, and 0), so
the lane proceeds. If the positive control (4 hand-read pages) had failed, the analysis aborts.

## Positive control (P0.2-style)

Four pages hand-read from the scans at full zoom, recorded in `extract_illustration.py:HAND`:
- p0 = drop-cap (red S-rune) + two black crosses; p8 = drop-cap (red Y-rune) + tree;
  p15 = drop-cap (red I-rune, tall red vertical) + tree; p9 = NO drop-cap (black only) + tree.
The extractor must reproduce all four has-drop-cap values, and page 0's illuminated rune must
be S. If it does not, the run aborts.

## Null

`presence`/`red_px`/`centroid` vectors shuffled 10 000× under seed 3301; illuminated-rune
entropy vs 10 000 random 29-alphabet draws (seed 3301). Empirical p-values; survivor bar
p < 0.01 (Bonferroni over the five statistics). Any survivor is FLAGGED-FOR-ORACLE, not
auto-certified (R21 seal note).
