# LENS S1 — interrupter-position channel — VERDICT: NEGATIVE

Reads the POSITIONS of the 458 F-runes (rune index 0) on the 12,956-rune unsolved LP2
stream as the message, since every letter-stream proof discards them as noise. Tests
gap-sequence and binary-indicator readouts. Not every F is provably a true interrupter,
so ALL F-runes are tested as the candidate channel (the only transcription-free reading).

## Positive control — PASSED
Constructed an interrupter position set whose consecutive gaps mod 29 encode
`THEPRIMESARESACREDANDTHISISATRUESIGNAL`, then ran the same (a) gap-mod29 machinery.
- recovered text = the planted message exactly
- score = **-4.143** (English band) vs count-matched null_max = **-6.405** → clean separation
The machinery recovers a planted gap-encoded signal. A real signal would have shown.

## Real channel — all routes in-band (NEGATIVE)
Interrupters = 458, gaps = 457, gap min/mean/max = 1 / 28.26 / 218.
Null = count-preserving random position sets (seed 3301), 200 draws, recomputed per route.

| route | score | null_max | passes bar? |
|---|---|---|---|
| a_gap_mod29 | -7.409 | -7.182 | no |
| a_gap_base29_g2 | -7.390 | -7.119 | no |
| a_gap_base29_g3 | -7.329 | -6.894 | no |
| a_gap_ascii | -7.310 | -6.891 | no |
| b_gap_mod2 | -8.377 | -8.269 | no |
| b_gap_mod3 | -6.880 | -6.682 | no |
| b_gap_mod4 | -6.300 | -5.975 | no |
| b_gap_mod5 | **-5.994** | -5.997 | no (best) |
| b_gap_mod8 | -7.544 | -7.143 | no |
| b_gap_bits_msb | -8.420 | -6.156 | no |
| c_indicator_msb | -8.639 | -5.124 | no |
| c_indicator_lsb | -8.639 | -3.781 | no |

Best real score = **-5.994** (b_gap_mod5), below the -5.5 threshold and only ~0.003 above
its own null_max (bar requires +0.5). Every route is in-band. The binary-indicator and
bit routes score BELOW their nulls — the F-positions carry less printable structure than
random position sets of the same count.

## HIT bar (PREREG)
score_norm >= -5.5 AND >= null_max + 0.5 → **not met** (both conditions fail).

## Verdict: NEGATIVE
Control recovers a planted signal; the true interrupter positions do not. No gap-encoded
or indicator-bit message is present in the F-rune position channel.
