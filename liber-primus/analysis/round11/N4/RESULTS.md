# LENS N4 — digit-plane separation — VERDICT: NEGATIVE

## What was tested
Represent the prime magnitudes `nc.v_prime(unsolved)` (12,956 primes, values 2..109)
in bases {3,5,7,10}. Extract every digit place with `nc.digit_plane`. Treat each
plane two ways:
- **(a) keystream:** plane as a mod-29 keystream, decrypt the runes both signs (±), score English.
- **(b) read:** plane digit-values mapped to rune indices, scored directly as English.

Total trials: all planes × {read, keystream−, keystream+} across 4 bases
(base3=5 planes, base5=3, base7=3, base10=3 → 14 planes → 42 scored trials).

## Positive control — PASS
Planted an English runeglish message (PARABLE[:400]) into one digit plane of a
synthetic integer stream, and separately encrypted English with a plane keystream.
- exact-plane read (message plane):      **-4.421**  (== plaintext -4.421)
- noise plane (higher digits):           -6.148
- keystream recover (right plane):       **-4.421**
- keystream wrong plane:                 -7.783

Machinery recovers a planted signal cleanly, jumping from noise toward English
(≈ -4.4). Both read-mode and keystream-mode detectors work.

## Real stream — NEGATIVE
| rank | mode | base | place | score |
|---|---|---|---|---|
| 1 | read | 5 | 0 | **-5.728** |
| 2 | read | 3 | 0 | -6.080 |
| 3 | read | 5 | 2 | -6.602 |
| 4 | read | 5 | 1 | -6.625 |

- **Best:** read, base 5, units plane → **-5.728**
- **Null (n=200 shuffles, seed 3301):** mean -5.763, **max -5.722**
- HIT bar: score ≥ -5.5 AND ≥ null_max+0.5 (-5.222)

Best score is **below the -5.5 English floor** and **-0.006 vs its own null max**
(essentially identical to shuffle). No digit plane, in any base, in either read
or keystream mode, rises out of its shuffled-null band. No hidden message in any
digit plane.

## Verdict
- control_passed: **true**
- hit: **false** (best -5.728 < -5.5, and -5.728 < null_max -5.722 + 0.5)
- **VERDICT: NEGATIVE**
