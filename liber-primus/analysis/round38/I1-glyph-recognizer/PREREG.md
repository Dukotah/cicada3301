# I1-R38 PREREG (written 2026-10-30, before any recognizer output)

Question: can a stroke-aware, rotation/scale-invariant recognizer detect the five U8-R37 planted glyphs
(octagon V1, 29-gon V2, T and L V3, 12-gon V4) in LP2 page-0 noise at >=0.9 detection with FPR<=0.05?

## Design D1 (frozen)
Walk/render: U8's own `walk`, `strokes`, `raster`, `pages`, `shuffled_words` (imported from the R37 u8.py, unchanged).
Candidates per page: every pen-down stroke with >= MINSTEPS[var] steps and <= 80 steps, plus adjacent stroke pairs (as U8).
Features per candidate (all rotation- and scale-normalised):
 1. corner count k: runs of steps after merging consecutive steps whose heading change < 20 deg; compared as |ln(k/k')|/0.7.
 2. closure = |end-start| / path length; compared |d|/0.3.
 3. turning-angle histogram: signed turns between consecutive pen-down steps, 24 bins of 15 deg, L1-normalised; compared L1/1.0.
 4. Hu moments (first 6, signed log10) of U8's 64x64 raster of the candidate (bbox-fit); compared mean abs diff/1.0.
Distance = sum of the four terms. Template bank = clean planted polyline of each of the five glyphs, loop/scale in {1,2,3}, both chiralities
(bank scales are discrete; test scales for T/L are non-bank: lengths x{1,1.5,2,2.5}).
Page score = min over candidates and templates of distance (lower = more glyph-like).
Detection rule: page score < 5th percentile of the score over 200 shuffles of that SAME page (U8 shuffle: zeros fixed, nonzero runes permuted;
V4 words permuted) -> FPR 0.05 by construction on the shuffle null. Rate also measured empirically (below).

## Power test
Per glyph, 40 trials: LP2 page-0 words, random cut (60-140 runes before, 20 words after), glyph block bracketed by interrupter [[0]] exactly as U8.
Random position (the cut), rotation (heading from preceding noise; V3 additionally a random cyclic rotation of the compass; chirality random),
scale (V1 loops 1-3, V2 loops 1-2, T/L x1..2.5, V4 loops 1-2). Each trial gets its own 200-shuffle null of the planted page.
Realised FPR: 200 noise-only renders (50 per variant, same cuts, no plant), each vs its own 200-shuffle null.
PASS = detection >= 0.9 for EVERY glyph (point estimate) AND realised FPR <= 0.05 (Wilson upper bound reported, not gated).

## Kill
If PASS fails: ONE pre-registered revision D2 is allowed (decided now: reweight to emphasise whichever of the four terms best separates plant vs null
in the D1 trials AND add a normalised turning-function term; no new data). If D2 fails too: record the ceiling, U8 retired, no rescore.
## Rescore (only on pass)
U8's 232 renders (4 variants x 58 pages) recomputed from u8.py; per render score vs its own 200-shuffle null p5. Report per variant renders below p5
(expected 0.05*58 = 2.9 by chance) and below null MIN (oracle bundle PNG for human eye per HUMAN-ORACLE.md); else negative with the three U8 conditionals.
- D1 amendment before any power run: Hu limited to the first four invariants with |h|+1e-5 floor (h5/h6 were numerically unstable on symmetric shapes; seen in a 5-trial smoke test, not a power run).

## D1 result and the ONE revision D2 (written 2026-10-30 after seeing power_D1.json, before any D2 output)
D1 (power_D1.json): detection oct 29/40, gon29 40/40, T 40/40, L 40/40, gon12 40/40; realised FPR 21/200 = 0.105 (all 21 in V2: the 29-gon variant).
Diagnoses: (a) oct failures are all the L=1 scale (8 steps < MINSTEPS 12: not a candidate) -- a design bug; (b) U8's shuffle null is NOT a valid null for
real text under V2 (real strokes close up more than shuffled ones: real-page score median 2.47 vs shuffle 2.77), so p5-of-shuffle gives FPR 0.42 on V2.
D2 = D1 plus exactly two changes, nothing else (features, weights, bank frozen): (1) candidate minimum steps 8 for V1-V3 (V4 stays 10);
(2) the null is a REAL-TEXT WINDOW null: 200 (power test: 100, for runtime) windows cut at random word boundaries from the OTHER LP pages (tested page's own
page excluded; page 0 excluded in the power test), matched to the tested page in rune count (V4: word count); threshold = 5th percentile of the window scores.
Detection = score < threshold. Pass rule unchanged. If D2 fails: ceiling recorded, U8 retired.
