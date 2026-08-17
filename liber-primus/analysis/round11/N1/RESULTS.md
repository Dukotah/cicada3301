# LENS N1 — cumulative-gematria FEEDBACK autokey — RESULTS

**Verdict: NEGATIVE**  (control passed; real stream sits in the null band)

## What was tested
Self-keying feedback autokey where `key[i] = f(running_sum of gematria PRIMES
recovered/seen so far) mod 29`, with:
- **feedback source**: PLAINTEXT-feedback (self-keying, accumulates `PRIMES[p_recovered]`)
  and CIPHERTEXT-feedback (accumulates `PRIMES[c_known]`).
- **f**: `mod29` (identity), `totient` (sum-1), `digitsum` (digital root).
- **sign**: +1 and -1.
- **direction**: forward and reversed stream.
- **mode**: continuous vs per-segment reset (`nc.segments()[:-2]`, 55 unsolved pages).

48 configs on the full 12,956-rune unsolved stream.

## Positive control (FIRST)
Planted English (PARABLE x40, 2000 runes, plain -4.437) encrypted under the
feedback rule, then recovered:
- PT-feedback: ciphertext hidden to **-7.467**, decoder recovered plaintext **exactly**,
  score back to **-4.437**.
- CT-feedback: ciphertext hidden to **-7.146**, recovered **exactly**, score **-4.437**.
- totient and digitsum feedbacks also invert exactly (self-consistency).
- **CONTROL PASSED** — machinery recovers a planted signal (noise ~-7.5 -> English -4.4).

## Real run
- Best of 48 configs: **-7.438** (continuous, ct-feedback, f=digitsum, sign -1, reversed).
- Null band (200 shuffles, seed 3301, best config): mean **-7.496**, max **-7.446**.
- HIT bar: score >= -5.5 AND >= null_max+0.5 (-6.946). Best -7.438 fails both.

Every one of the 48 configs scored between -7.44 and -7.48 — indistinguishable from
the histogram-preserving shuffle. No feedback-autokey configuration produces English.

## Conclusion
The feedback-autokey class the standing verdict left OPEN is now **closed NEGATIVE**
for cumulative-gematria-prime feedback across f in {mod29, totient, digitsum}, both
plaintext- and ciphertext-driven, both signs, both directions, continuous and
per-segment-reset. Positive control confirms the detector would have fired on a real
signal.
