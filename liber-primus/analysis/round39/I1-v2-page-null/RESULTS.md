# I1-R39 RESULTS: page-matched null for V2 - status negative (instrument), positive control FAILED. V2 recorded unmeasurable by this recognizer family.

Pre-registered in PREREG.md (dated before the run). Recognizer = R38 D2, unchanged. Render = V2_idx_rel_29. 200 null draws per page; threshold = page's own null p5.
Clean pages = 50 windows of LP page 0 (60-140 runes + 20 words, real line ids); plants = 40 trials per glyph (V2-quantised realisations, see PREREG); seeds 39001/39002.

| variant | oct | 29-gon | T | L | 12-gon | realised FPR (50 clean V2) | leak (mean frac of null draws <= observed, plants) | pass |
|---|---|---|---|---|---|---|---|---|
| A within-line | 40/40 | 40/40 | 38/40 | 35/40 [0.74,0.95] | 40/40 | **15/50 = 0.30 [0.19,0.44]** | 0.006 (ok) | FAIL |
| B within-word | 4/40 | 3/40 | 35/40 | 25/40 | 15/40 | 11/50 = 0.22 [0.13,0.35] | 0.212 (LEAK) | FAIL |

Required: each glyph >= 0.9, FPR <= 0.05, leak <= 0.05.

- Variant A: power is high (L 0.875 is the only glyph under 0.9, Wilson 0.74-0.95), the null does not leak the plant (the shuffle destroys it; mean null p5 on planted pages 2.37 vs
  2.45 on clean), but realised FPR is 0.30 - no better than the R38 shuffle/window nulls (0.58 for V2 at D2). So matching on the line does not remove the excess closed-loop
  structure in real page text: clean-page scores sit at the null's low tail far more often than 5% (clean mean score 2.50, mean threshold 2.45, but with a heavy lower tail).
  A caveat: oct was detected 40/40 but only 18/40 with the correct template (gon12 neighbour); the other glyphs were detected with the correct template.
- Variant B: the within-word shuffle keeps a one-word plant: 29-gon (identical runes) is invariant, octagon/12-gon mostly preserved (the V2 heading depends on cumulative idx sum, which a
  within-word permutation leaves unchanged at word end), so the null reproduces the plant (leak 0.21; 29-gon 0.45) and power collapses (3/40, 4/40). FPR 0.22 as well.
- Sensitivity (own-line plant, 20 trials x 100 draws, not used for pass/fail): A leaks as predicted when the plant fills its own line (octagon 1/20, 29-gon 0/20; leak 0.59/0.60), B similar.
  So for A the primary placement (plant sharing a line with real text) is the generous case; the fail stands either way.

Verdict: FAIL for both variants -> kill rule applies. V2 is recorded as unmeasurable by this recognizer family; U8's 58 V2 renders were NOT re-scored (gate unmet; no oracle/ PNGs).
Geometry reading closes as "V1/V3/V4 chance-level (R38 addendum), V2 unmeasured" - a measurement statement, not a statement that V2 contains nothing.

Conditionals: glyph set = the five U8 shapes in V2-quantised form (zigzag straights; 45/90/30 degree turns approximated by 12.41-degree idx steps); one-word plant placement;
null draws 200; one page (0) of noise text for FPR; recognizer family fixed (nearest-template over turning-histogram/closure/Hu features). Not covered: a different feature family,
a null that also preserves local rune-pair statistics, V2 with a structure-aware (e.g. n-gram-preserving) shuffle, glyphs the bank does not contain.
Deviations: V2-quantised plants (necessary; PREREG documents it); koans page / re-score never reached.

Files: PREREG.md, run.py, rescore.py (unrun), power_v2_A_B.json, run.log, ledger.json.
