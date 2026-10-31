# I1-R39 PREREG - page-matched null for the V2 render (written 2026-10-31, BEFORE any run)

Instrument: Round 38 D2 recognizer (`analysis/round38/I1-glyph-recognizer/recognizer.py`, D2=1, weights unchanged, score = distance, LOWER = more glyph-like).
Render: U8 `V2_idx_rel_29` (heading += idx*360/29, pen-up at idx 0 interrupters). Nothing in the recognizer is changed.

## Q1 recognizer
Null A = within each physical line (mapcommon `w_line`; a word is assigned the line it starts on), shuffle the non-interrupter runes among that line's non-interrupter
slots; word lengths and interrupter positions fixed. Null B = shuffle the non-interrupter runes within each word. 200 draws per page. Detection threshold = the page's own
null 5th percentile (detect iff observed score < threshold).
Pass for a variant requires ALL of: (i) detection >= 0.9 (40 trials) for each of the five planted glyphs; (ii) realised FPR on 50 clean V2 pages <= 0.05; (iii) leak check ok.
Kill: both variants fail -> V2 recorded as unmeasurable by this recognizer family; geometry reading closes as "V1/V3/V4 chance-level, V2 unmeasured". No further revisions.

## Power test
Clean page = a window of 60-140 runes of LP page 0 text plus 20 following words (as R38), with real line ids; 50 such windows for FPR (seeded RNG 39001).
Plants (40 trials each) embedded as a single word between two interrupter words, as R38. Glyphs: octagon, 29-gon, T, L, 12-gon. V2 cannot draw a straight
segment or a 45/90/30 degree turn with an integer idx (idx 0 is pen-up; unit turn = 12.41 degrees), so each glyph is a V2-QUANTISED realisation: the glyph's target heading
sequence (as R38's V1/V3/V4 blocks) is rendered by choosing at each step the idx nearest the needed turn with error feedback; a needed idx 0 is replaced by 1 or 28
(alternating zigzag). The 29-gon is the native idx-1 run. Plant line placement (primary): the plant shares the line id of the preceding real word. Sensitivity:
plant on its own line (expected to leak under A; recorded, not used for pass/fail, 20 trials x 100 draws). Under B a one-word plant is preserved only if its runes
are identical; this is measured, not assumed.

## Leak check
For planted trials: fraction of null draws scoring <= the trial's own observed score (must be small, mean <= 0.05), and mean null p5 on planted pages vs clean pages.
A variant whose planted-page nulls reproduce the plant fails.

## Re-score (only if a variant passes)
U8's 58 V2 renders (57 pages + koans text) recomputed from u8.py; line ids from parse (koans page: no line structure, so variant A = whole-text shuffle, flagged).
Report count below page p5 (chance ~2.9 of 58), count below null min, PNGs of below-min renders into `oracle/` labelled variant-limited diagnostic (HUMAN-ORACLE.md).
