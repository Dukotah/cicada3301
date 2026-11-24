# R45 / S1b — Hidden-doublet audit of T7's fragile intervals: RESULTS

_2026-11-24. Pre-registration: `PREREG.md` (dated before any output; Addenda B1 and B2 are dated and ordered
relative to the frozen reads). Nothing outside this folder was written. No correction is proposed._

## Headline

**No hidden doublet and no count error in any of the 1,138 adjacent pairs of T1's fragile intervals.**
T1 found that a single extra doublet anywhere in pairs ≈1565–1620, 3040–4035 or 9570–9625 would push T7 above
p = 0.01. This lane read all 56 canon lines covering pairs [1560,1625] ∪ [3035,4040] ∪ [9565,9630] (1,215 runes)
blind and checked every look-alike pair a second time with a validated template instrument. Every candidate
resolved to canon. **T7 is unchanged: r = +0.380, p = 0.0010 (86 events). Status: HARDENED**, with the miss
bounds below.

## What was done

- **Pass L (full coverage, blind).** Each target line was rendered as numbered half-strips under an opaque id and
  shuffled with 8 control lines that hold 9 known doublets. All 64 lines were transcribed blind, and every pair
  that read as the same rune was flagged. Reads were frozen (`reads_L.txt`, sha `2e984524…`) before
  `sealed_lines.json` was opened.
- **Pass P (same/different, blind).** A shuffled deck of 97 two-glyph crops: all 17 target look-alike-family
  pairs on exact-registered lines, 30 control true doublets, 30 control look-alike non-doublets and 20 target
  decoys. Reads were frozen (`reads_P.txt`, sha `4394b9c2…`) before `sealed_pairs.json` was opened.
- **Template instrument (Addendum B2).** It calls each glyph by nearest class mean, using templates built only
  from glyphs outside the target lines, so it never sees the canon label at the position it classifies. It is
  applied to every TH/W, M/D and A/AE/O glyph on the target lines and to every flagged pair.
- **Count audit.** Segment count was compared with canon count per line. Every discrepancy, and every glyph the
  reader saw that was not boxed, was checked by listing ink components and by small zoom crops.

## Control accuracy (power)

| instrument | control | result | CP 95 % |
|---|---|---|---|
| Pass P sensitivity | 30 true doublets read SAME | **29 / 30** (miss: one W,W read as W,TH) | [0.828, 0.999] |
| Pass P specificity | 30 look-alike non-doublets read DIFF | **28 / 30** (D,M→same; A,AE→same) | [0.779, 0.992] |
| Pass P decoys | 20 target non-family pairs | 20 / 20 DIFF | — |
| Pass L | 9 known doublets on 8 control lines read equal | **9 / 9** | [0.664, 1] |
| Pass L | class-level glyph agreement, all 64 lines | 1,364 / 1,380 | — |
| Template | TH/W · M/D · A/AE/O glyphs on target lines, call = canon | 74/74 · 67/67 · 116/116 = **257 / 257** | [0.986, 1] |

The pre-registered pass-P gate (≥ 27/30 on both sensitivity and specificity) **passed**.

**Reader limits (disclosed, B2).** At strip resolution the pass-L reader could not separate M from D or TH from
W, so it recorded them as undecided (`M|D`, `TH|W`). It also read canon A as O 11 times. That makes pass L a
class-level instrument. Family-level discrimination rests on pass P plus the template instrument. Outside the
look-alike families, pass L made one real misread (P read as C) in about 1,100 glyphs.

## Candidates and how each resolved

| t (pair) | flagged by | canon | template call (corr to class means) | verdict |
|---|---|---|---|---|
| 3087 | P SAME + L ambiguous | TH, W | TH (0.64 vs 0.45), W (0.97 vs 0.67) | canon |
| 9612 | P SAME + L TH,TH | TH, W | TH, W (same margins) | canon |
| 9630 | P SAME + L W,W | TH, W | TH (0.93/0.67), W (0.74/0.55) | canon |
| 3385 | L W,W | W, TH | W (0.97/0.67), TH (0.93/0.67) | canon |
| 3500 | L ambiguous | TH, W | TH (0.94/0.67), W (0.63/0.51) | canon |
| 3928 | P SAME + L ambiguous | M, D | M (0.96/0.67), D (0.97/0.68) | canon |
| 3394 | L ambiguous | M, D | M (0.96/0.66), D (0.97/0.69) | canon |
| 1623 | L ambiguous | M, D | M (0.77/0.58), D (0.97/0.68) | canon |
| 3782 | L ambiguous | M, D | M (0.98/0.68), D (0.95/0.68) | canon |

The pair glyph–glyph correlations of these candidates (0.35–0.66) sit in the canon-different range for their
family, not the canon-doublet range (`template.json`).

**Count checks.** Every line's rune count matches canon. Four discrepancies were found and each resolves to
canon (`adjudications.json` `count_checks`):

1. **Lines 147 and 154 (pass-L "extra stem").** No ink component exists at either spot. Each "stem" was the
   stem of the next glyph, cut off at the half-strip crop edge. This rules out the possible I,I doublet at
   line 147.
2. **Line 74 (segments = canon − 1).** C and E touch and form one 107-px component, which the segmenter's width
   filter drops. The zoom reads C E IA O = canon.
3. **Line 168 (segments = canon − 1).** The leading canon L is page 15's three-line drop cap: a stem with a top
   branch and no right stem. That is L, not U, so there is no U,U doublet at t = 3612.
4. **Lines 152, 176 and 183 (segments = canon − 1).** Each has a touching C+B or C+AE glyph merged into one box.
   Pass L read both glyphs.

The canon doublets inside the intervals (t = 3139 AE,AE; 3851 G,G; 9595 W,W — the void edges T1's gaps are
measured between) were read blind as doublets.

## Miss-rate bound

A hidden doublet in a look-alike pair (the only class where S1 found any reader–canon confusion) goes undetected
only if pass L misses it **and** the template mis-calls one of the two glyphs:

- template alone: ≤ 1.4 % per glyph, so ≤ 2.8 % per pair (CP 95 %, 0/257 errors);
- pass P alone (17/18 family pairs): ≤ 17 % per pair;
- pass L alone (9/9 control doublets): ≤ 34 % per pair.

For non-family pairs, a hidden doublet would need a gross misread. Pass L made 1 such misread in about
1,100 glyphs, and the 20 decoy pairs were all called DIFF.

So the chance that a real hidden doublet in these intervals escaped is at most about 3 % per family pair. With
0 found, **T7's fragility to transcription is closed at this resolution.** One extra doublet is what T1 says
would dissolve T7, and none exists in the image.

## Coverage × power and the three conditionals

1. **Read set.** All 1,138 pairs and 56 lines of the brief's intervals (padded ±5 beyond T1's 5-pair sampling
   grid), including the 3270–3635 stretch that E0b did not mark as a breaker.
   **Not covered:** pairs outside these intervals, and the ~600 positions where a single insertion moves T7's
   p only to between 0.001 and 0.01.
2. **Location model.** S1's page-constrained `corrected_map.json`, not `analysis/stones/alignment.json`. Lines
   166 and 167 were located as the short lines next to their neighbours. Count discrepancies were checked
   against raw ink components.
3. **Reader.** One vision reader plus a class-mean template instrument, both on the sha-pinned relikd
   2400×3600 renders. Templates use canon labels from outside the target lines, so they depend weakly on
   canon's partition (S1: 0 errors in 398 glyphs). An error common to the relikd render itself, rather than
   the transcription, is not visible.

## Verdict

**T7 HARDENED.** There are 0 hidden doublets and 0 count errors in 1,138 pairs. Measured miss bound: ≤ 2.8 %
per look-alike pair (template), ≤ 17 % (pass P), ≤ 34 % (pass L). T7 stays at r = +0.380, p = 0.0010, the same
as T1, so no recomputation was needed. Per T1 §6, the remaining explanations are a tail fluctuation of the gap
sequence or a non-renewal short-memory gap process. Transcription error is no longer one of them for these
intervals.

**What reopens this:** a higher-resolution master (not the relikd render) showing a different glyph at any
listed candidate; or a re-derivation of T1's fragility map showing breaker positions outside these intervals.

## Files

`PREREG.md` (+ B1, B2), `build.py` (selection, sealing, rendering), `reads_L.txt` / `reads_P.txt` (frozen blind
reads; hashes in `reads_frozen.sha256`), `adjudicate.py` → `adjudicate_raw.json`, `template.py` →
`template.json`, `zoom.py` / `zoom_gl74.py` / `zoom_dropcap.py` → `zoom.json` + crops, `finalize.py` →
**`adjudications.json`**, `ledger_rows.json`. `crops/` is gitignored (`.gitignore` here) and regenerated by
`build.py` and the zoom scripts. Reproduce from `liber-primus/`: `PYTHONUTF8=1 python
analysis/round45/S1b-hidden-doublets/build.py`, then run `adjudicate.py`, `template.py`, `zoom.py` and
`finalize.py` in that folder. The reads are agent input and are not regenerated.

---
CLOSING STAMP — R45/S1b closed 2026-11-24. 1,138/1,138 target pairs read; 97 deck pairs + 8 control lines;
0 hidden doublets, 0 count errors, 0 corrections; T7 HARDENED (r 0.380, p 0.0010).
