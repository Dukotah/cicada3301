# RESULTS - R37 C2-U8 per-page geometry (interrupter-gated turtle renders)

PREREG.md (+Addendum 1) written first. 58 pages x 4 variants = 232 renders; each vs 200 sequence shuffles (non-F values permuted, F positions held; V4 word order permuted). Runtime 395 s.

## What R22-B already covered (not repeated)
R22-B: LP2 pages 0-54 as one book-concatenated stream; value / prime-index / totient x moduli {4,6,8,12,29,360} x absolute/relative x unit/value step = 72 renders; global shape statistics (closure, self-intersections, bbox fill, caging, symmetry, components) vs 200-shuffle null; F left in as an ordinary rune; no per-page, no pen-up, no LP1 numbers, no template/glyph recognizer. Its own not_covered named exactly those. U8 here is per page, interrupter-gated, includes AN END / PARABLE as printed and LP1 plaintext word sums, and uses a glyph template match.

## Planted-glyph controls (before the pages) - **ALL FAILED**
| plant | variant | plant best score (z of best template) | best template | shuffle null max | verdict |
|---|---|---|---|---|---|
| V1_prime_mod8_rel | V1 | 2.92 | rune_C@90 | 3.78 | FAIL |
| V2_idx_rel_29 | V2 | 3.09 | rune_S@90 | 3.74 | FAIL |
| V3_idx_abs_card_T | V3 | 4.09 | T@0 | 4.21 | FAIL |
| V3_idx_abs_card_L | V3 | 3.66 | L@0 | 3.98 | FAIL |
| V4_wordsum_rel12 | V4 | 2.91 | O@90 | 3.84 | FAIL |

The recognizer could not separate a planted 24-30 step glyph (octagon, 29-gon, T, L, 12-gon) embedded in LP2 page-0 noise from the best accidental match among the shuffled strokes. Raw NCC (first attempt) was worse (null 0.87-0.99 from line-like strokes matching I / 1 / rune-I and short zigzags matching simple glyphs); the z-distinctiveness version in Addendum 1 got closest on V3 (T: 4.09 vs null max 4.21) but still failed. Per the kill rule this lane is **INCONCLUSIVE**: the page results below are diagnostic only.

## Variant table (diagnostic; control failed)
| variant | pages | above own null max | max real score | max page-null-max | mean(real - null max) | pages with no candidate |
|---|---|---|---|---|---|---|
| V1_prime_mod8_rel | 58 | 0 | 3.38 | 4.46 | -1.03 | 4 |
| V2_idx_rel_29 | 58 | 0 | 3.47 | 5.02 | -0.95 | 0 |
| V3_idx_abs_card | 58 | 0 | 4.14 | 4.89 | -1.26 | 2 |
| V4_wordsum_rel12 | 58 | 0 | 3.51 | 4.83 | -1.12 | 2 |

No page-variant exceeded its own 200-shuffle null max (0/232), so no refinement ran and **no oracle PNGs were produced**. Because the control failed this is not a clean negative: a real planted-class glyph would also have been missed.

Human-eye material: `png/contact_V1..V4_*.png` (58 page renders per variant, 96 px thumbnails, 10 columns; black = pen down, pale blue = pen up) and `png/plant_*.png` (the plants with the best candidate in red). Page order: 0-54 LP2, 55 AN END, 56 PARABLE, 57 LP1 plaintext.

## Three conditionals
1. **Rule space:** 4 turtle rules x 58 pages = 232 renders. Not covered: other moduli/step rules, value-scaled steps, the 55-page grid layout, L-systems, 3D, glyphs of >2 strokes, line-sum streams, multi-glyph text along a line beyond adjacent stroke pairs.
2. **Decoder:** deterministic turtle; F = pen-up unit step (V1-V3) / F-containing word pen-up (V4); a different interrupter semantics is missed. LP1 plaintext (page 57) has no F so is never pen-up.
3. **Adjudicator:** glyph-template NCC (Latin/digits/runes) is UNPOWERED here: planted glyphs of 24-30 steps are not separable from shuffled strokes. Needs a better recognizer (e.g. an OCR-style classifier trained on turtle-drawn strokes, or fewer degrees of freedom) before this family can be called negative.

## not_covered
All of the above conditionals; additionally a power-adequate recognizer. Coordinator decision needed: invest in a stroke-aware recognizer (e.g. require closure/rotation-invariant Hu moments + template) or accept the human-eye contact sheets as the only readout.

## Files
PREREG.md, u8.py, finalize.py, results.json, run.log, png/, ledger.json, RESULTS.md
