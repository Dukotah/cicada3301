# Round 16 / matched scorer — RESULTS

_Completed 2026-08-23._

## Summary

The matched runic quadgram scorer is built, validated, and available for import at
`analysis/round16/scorer/scorer.py`. The positive control passes. The claimed 20% sigma
improvement (sd 0.089→0.071) was NOT reproduced; the measured gain is smaller and comes
from signal improvement only.

## What was done

1. Pre-registered in `PREREG.md` before running.
2. Trust anchor confirmed: `python tests/validate.py` — ALL VALIDATIONS PASSED.
3. Built `scorer.py` with `MatchedQuadgram` class and `matched_scorer()` singleton.
4. Measured signal scores for all 5 known solved pages under both old and matched models.
5. Built 200-decode null from random-keystream decodes of A KOAN (06.jpg, 742 runes) —
   the construction that best matches the FINDING.md null mean (−7.50 vs claimed −7.56).
6. Computed sigma separation under both models.

## Measured numbers

### Signal scores (per-quadgram norm)

| Page | OLD (English) | NEW (matched) | Change |
|---|---|---|---|
| A WARNING | −4.478 | −4.194 | +0.284 |
| SOME WISDOM | −4.979 | −4.774 | +0.205 |
| A KOAN | −4.127 | −4.082 | +0.045 |
| WELCOME | −4.344 | −4.238 | +0.106 |
| CIRCUMFERENCE | −4.243 | −3.952 | +0.291 |

All 5 pages score better under the matched model.

### Null distribution (200 random-key decodes of A KOAN, 742 runes)

| Stat | OLD | NEW |
|---|---|---|
| mean | −7.503 | −7.434 |
| sd | 0.0880 | 0.0895 |
| min | −7.676 | −7.613 |
| max | −7.212 | −7.147 |

The null sd did NOT tighten — it is slightly worse (0.0895 vs 0.0880, +1.7%).

### Sigma separation

| Model | signal_min | noise_mean | noise_sd | sigma_sep |
|---|---|---|---|---|
| OLD | −4.979 | −7.503 | 0.0880 | **28.7σ** |
| NEW | −4.774 | −7.434 | 0.0895 | **29.7σ** |

Improvement: **+3.6%** in sigma separation. All the gain comes from the signal
improvement; the noise sd actually worsened slightly, partly cancelling it.

## Gate results

| Gate | Result |
|---|---|
| GATE 1: all 5 pages > −5.5 under new model (positive control) | **PASS** |
| GATE 2: new sd ≤ old sd (noise improvement) | **FAIL** |

Gate 2 fails. The matched model is still a valid scorer (controls pass, all signals
improve), but the noise sd does not tighten.

## Comparison with round15/SCORER/FINDING.md

FINDING.md claimed:
- sd: 0.089 → 0.071 (20% tighter)
- sigma separation: 34.4σ → 40.5σ (+18%)

Measured here:
- sd: 0.088 → 0.089 (no tightening; slight increase)
- sigma separation: 28.7σ → 29.7σ (+3.6%)

The discrepancy is real. Possible explanations:
1. The POC may have computed the null differently (shuffled character positions in
   English text with K/V/Q/Z, which the matched model scores higher, artificially
   widening the null band under the English model).
2. The POC used a different random seed or null base that happened to give a lower sd.
3. The sd improvement claim in FINDING.md was a measurement artifact of the POC's
   specific null construction, not a property of the matched model in general.

## What the matched model IS vs what it is NOT

**IS:** A correctly built scorer that:
- Trains on the actual character distribution the decoder emits
- Eliminates K, V, Q, Z quadgrams and merges their frequency mass into C, U, S, C
- Handles multi-char rune transliterations (TH, EO, NG, OE, AE, IA, EA) correctly
- Passes the positive control gate (all 5 solved pages score above −5.5)
- Improves all 5 signal scores (all pages score better)
- Is importable by any future sweep lane

**IS NOT:**
- A 20% noise-reduction improvement as claimed by the POC
- A reason to revisit any completed negative (those sit at −5.7–5.9, far below −4.2)
- A hit or signal on any unsolved page

## Verdict

**BOUND.** Positive control passed. Measured sigma separation: OLD 28.7σ → NEW 29.7σ
(+3.6%). Noise sd did not tighten (0.0880 → 0.0895). The matched scorer is a
valid drop-in replacement with modest, real signal improvement. The POC's claimed +18%
sigma separation was NOT reproduced; the actual gain is +3.6%.

## Files

| File | Purpose |
|---|---|
| `PREREG.md` | Pre-registration (hypothesis, gates, null design) |
| `scorer.py` | Importable matched scorer module |
| `measure.py` | Measurement script (reproduces these numbers) |
| `results.json` | Machine-readable results |
| `RESULTS.md` | This file |

## Import usage

```python
import sys
sys.path.insert(0, "analysis/round16/scorer")
from scorer import matched_scorer

sc = matched_scorer()
sc.score_norm("WELCOMEPILGRIMTOTHEGREATJOURNEY")  # -> ~ -4.2
```

The `matched_scorer()` function returns a singleton (lazy, cached) `MatchedQuadgram`
instance. It accepts the same API as `src/lp/score.Quadgram`:
- `.score(text)` — total log10 probability
- `.score_norm(text)` — per-quadgram average (the standard comparison metric)
