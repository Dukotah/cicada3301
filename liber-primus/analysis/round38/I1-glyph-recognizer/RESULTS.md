# I1-R38 RESULTS: glyph recognizer with measured power -- status inconclusive (positive control: failed on FPR)

Instrument: `recognizer.py` (imports U8's `walk/strokes/raster/pages/shuffled_words` unchanged). Features: corner count, closure, 24-bin turning histogram,
first four Hu moments of the 64x64 raster; nearest of 30 templates (5 glyphs x scale 1-3 x chirality). Detection = score < page-null 5th percentile.

| design | oct | 29-gon | T | L | 12-gon | realised FPR (200 noise renders) |
|---|---|---|---|---|---|---|
| D1 (shuffle null, 200 draws) | 29/40 [0.57,0.84] | 40/40 [0.91,1] | 40/40 | 40/40 | 40/40 | 21/200 = 0.105 [0.07,0.155] (all V2) |
| D2 (min 8 steps; real-text window null, 100 draws) | 40/40 [0.91,1] | 40/40 | 40/40 | 40/40 | 40/40 | 32/200 = 0.16 [0.116,0.217]: V1 0/50, V2 29/50, V3 3/50, V4 0/50 |

Wilson 95% in brackets. All detections used the correct template. Test scales for T/L were off the template bank; positions/rotations random.

Verdict: FAIL. Power is 1.0 but the FPR gate is not met. D1's octagon misses were a design bug (8-step plant under the 12-step candidate minimum), fixed in D2.
The remaining failure is calibration, not sensitivity: in the V2 render (heading += idx*360/29) real page-0 text yields closed-loop strokes that look glyph-like more often
than either a rune shuffle (page median 2.47 vs 2.77) or windows from other pages produce, so a 5%-null threshold fires on ~58% of untouched V2 noise pages.
V3 is borderline (6%); V1 and V4 are clean (0/50 each). One revision was pre-registered and used; kill rule applies: ceiling recorded, U8 retired, 232-render re-score NOT run
(`rescore.py` written but unrun; `rescore_u8.json` is a not-run stub). Deviations: D2 power test used 100 null draws per trial (runtime); PREREG revision content was
set after seeing D1 (documented in PREREG.md), and differs from the originally sketched "reweight + turning function".

Conditionals: glyph set = five U8 shapes only; V2 is not calibratable against these nulls; rule space still 4 rules x 58 pages. Not "closed": a V1/V3/V4-only rescore or a
page-matched null for V2 are open options.

Files: PREREG.md, recognizer.py, rescore.py, power_D1.json, power_D2.json, power.json, rescore_u8.json, ledger.json, d2.log.
