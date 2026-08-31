# Round 22 — Lane D — Illustration / drop-cap channel — RESULTS

_Ran 2026-08-29. Pre-registration: `PREREG.md`. Doctrine: `../../../ARMADA-DOCTRINE.md`._

## Trust anchor

`liber-primus/tests/validate.py` → **ALL VALIDATIONS PASSED** (reproduces all solved pages).

## Asset verdict: RUNNABLE (not blocked-on-assets)

The illustration data exists in the repo and is machine-extractable. Full per-page scans
(58 pages, 2400×3600) are committed under
`corpus/E-tooling/vendor/cmbsolver__cmbcidada3301/LiberPrimusUi/input/images/LP/`. No drop-cap
catalog previously existed — **this lane built the first one** (`features.json`). The prior
vision-OCR closure (0.145 alignment on dense runes) does not apply: the drop-cap is a single
*large* glyph printed in **red**, separable by a colour mask with no OCR; and the illuminated
rune's identity comes exactly from the canonical per-page rune strings (the drop-cap is the
first body rune).

## Positive control — PASSED

| page | hand read | extractor `has_dropcap` | |
|---|---|---|---|
| 0 | drop-cap (red **S**) + two crosses | True | OK |
| 8 | drop-cap (red **Y**) + tree | True | OK |
| 15 | drop-cap (red **I**) + tree | True | OK |
| 9 | none (black text only) + tree | False | OK |

And the illuminated rune of page 0 is **S** (`control_page0_is_S: true`), matching the red S
seen in the scan. The instrument reproduces every hand-count → silence is trustworthy.

## The drop-cap channel, coded as data (`features.json`)

- **15 of 58 pages are illuminated** (a red drop-cap): pages
  **0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54, 56, 57**.
  - 15 is **not** prime, **not** 29, not a distinguished value (S3 recognizer: null).
- Presence bitstring: `1001001110000001000000010001000001000001100000000000011011`.
- Illuminated runes in page order (first-rune-of-page): **S L X H X F U M D S F A ING P**
  → reads `SLXHXFUMDSFAINGP`. Not English; not a base-29/ASCII string.
  (14 runes mapped: page 57 is illuminated but absent from `canonical_pages.json`, which
  lists pages 0–56 — a 1-page coverage gap, immaterial to the entropy null.)

## Structure test vs size-matched null (seed 3301, 10 000 shuffles) — NULL

| statistic (recognizer) | observed | null | p | verdict |
|---|---|---|---|---|
| gap variance — clustered (S2) | 11.78 | — | 0.821 | null |
| gap variance — spread (S2) | 11.78 | — | 0.180 | null |
| presence-bits compressibility (S1) | 16 B | 16.0 B | 1.000 | null |
| centroid-y rank-correlation vs page order (S4) | 0.161 | — | 0.570 | null |
| illuminated-rune entropy vs random alphabet (S5) | 0.696 | 0.699 | 0.571 | null |

**min p over all five order/identity statistics = 0.180**, far above the p < 0.01 Bonferroni
bar. **No survivor. FLAGGED-FOR-ORACLE: none.**

## Value = coverage × power (doctrine R2)

- **Coverage.** The full drop-cap presence/position/identity channel over all 58 committed
  page scans: has-cap (image), which-rune (canonical), gap sequence, centroid, blob count.
  This is the *entire* enumerable drop-cap feature space for these scans.
- **Power.** Measured, not assumed: the extractor reproduces 4/4 hand-read pages and the
  page-0 rune identity; the colour-mask has-cap gate is validated (a planted "hit" — a real
  red drop-cap — is exactly what the instrument keys on, so it *would* recognise the shape it
  is hunting, Q1). The null is therefore a real negative on this channel, at the p<0.01 bar,
  with the five recognizers stated before the run.

## Not covered / what would reopen it

- **The figural motifs (crosses, trees, the shrouded-corpse figure, mayflies) are NOT coded as
  data here** beyond the red drop-cap channel. Cataloguing motif type/count/orientation per page
  needs either careful hand-annotation across 58 scans or a shape/CC pass on the *black* channel
  (which is entangled with the dense runes and the same OCR-unreliability floor). That is a
  bounded but larger annotation job; documented, not executed. If that catalog were built and its
  per-page integer sequence tested the same way, it reopens the lane.
- The 1-page canonical gap (page 57's illuminated rune) does not change the entropy null but
  should be closed if the rune-identity read is ever revisited.

## Bottom line

The drop-cap channel is now a committed, human-checkable object (first LP2 drop-cap catalog).
Read as data — presence, order, gap structure, and illuminated-rune identity — it shows **no
structure beyond a size-matched shuffle** (min p = 0.18). The illuminated runs spell nothing
(`SLXHXFUMDSFAINGP`). **NEGATIVE on the drop-cap channel**, control-validated, bounds stated —
not a verdict on the figural motifs, which remain un-coded.
