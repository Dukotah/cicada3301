# PREREG — Round 16 / matched scorer

_Written before any code runs. 2026-08-23._

## Hypothesis

The existing scoring infrastructure trains on raw-English quadgrams but the decoder emits the
**runic transliteration** (7 of 29 runes expand to 2 characters; alphabet is lossy: no K, Q, V, Z).
A quadgram model trained on a **matched** distribution — English pushed through the same rune
round-trip the decoder inverts — should tighten the noise sigma and improve the separation
between correct decodes and random noise in sigma units.

The FINDING.md (round15/SCORER/) claims:
- noise sigma: 0.089 → 0.071 (20% tighter)
- sigma separation: 34.4σ → 40.5σ (+18%)

This lane **reproduces those numbers** from a production-quality `scorer.py` and makes the
matched scorer importable by every future sweep lane.

## Pass/Fail bar

This lane **cannot produce a HIT** — it is an instrument calibration, not an attack.

Pass criteria (both must hold):
1. **Positive control gate**: all 5 known solved pages must score above −5.5 under the
   matched model (same bar used repo-wide). If any page falls below −5.5, the model is
   broken and this lane returns ERROR.
2. **Power gain confirmed**: measured noise sigma under the matched model must be ≤ 0.089
   (at least equal to the old model). If it is larger, the matched model is worse and
   should not be deployed.

Expected verdict: **BOUND** with measured sigma and separation numbers.

## Positive control

The 5 known solved pages from `tests/validate.py` serve as positive control:
- `Runes - 01.jpg` ("A WARNING")
- `05.jpg` ("SOME WISDOM")
- `06.jpg` ("A KOAN")
- `03.jpg` ("WELCOME" — Vigenere, key DIVINITY)
- `14.jpg` ("CIRCUMFERENCE" — Vigenere, key FIRFUMFERENFE)

Each page's verified plaintext transliteration is scored under both old and matched models.
All 5 must score above the null band's max.

## Null (size-matched)

200 random shuffles of one solved page's character sequence, scored under both models.
This matches the FINDING.md methodology exactly.

## Method

1. Build the matched quadgram model by re-weighting the existing `english_quadgrams.txt`
   through the runic round-trip mapping (English letter → runic index → transliteration
   string). Since multi-char transliterations (TH, EO, NG, OE, AE, IA, EA) expand single
   letters, the quadgram count matrix must be recomputed over the expanded character stream.
2. Write `scorer.py` as an importable module with a `MatchedQuadgram` class and a
   `matched_scorer()` singleton.
3. Score the 5 solved pages under both models, record raw score and per-quadgram norm.
4. Score 200 shuffles of the largest solved page under both models.
5. Compute sigma separation = (min_signal − max_null) / null_sd for each model.
6. Record all numbers in `results.json`.

## Size bound

This is a one-time calibration computation: build the model from existing data + score
5 pages + 200 shuffles. Runs in < 30 seconds. No large-scale sweep.

## What this does NOT do

- Does not re-run any completed negative result.
- Does not claim a solve.
- Does not change the verdict on any prior campaign.
- The gain is strictly forward-looking: future sweeps should import this scorer.
