# RESULTS - R37 C2-U4 prime line sums (measured 2026-10-30)

Verdict: **NO-SEPARATION** under the preregistered rule. Pooled plaintext p(shuffle) = 1e-4 (the 10,001-draw floor)
passes the pooled clause, but only 2 of 6 pages are individually p < 0.05 (need 4), and the pooled signal is one page:
A WARNING (9/10 lines prime; 9/9 excluding the title). Top-row `plinefrac` scoring was NOT run (decision rule: stop).

Decodes were verified against SOLVED-PAGES.json / validate.py words before use (all six decode_ok true; interrupters
03:7, 14:2, 73:1). Line sums for A WARNING reproduce the scream314 claim exactly (757, 1009, 691, 353, 769, 911, 1051, 859, 677).

## Positive control (run first): PASSED
Prime-by-construction lines at the six pages' line lengths: 60/60 lines pass, f = 1.0, pooled p = 1e-4 (floor) under both
nulls; each of 01, 05, 06, 03, 14 has p = 1e-4; 73 (4 lines) p = 9e-4 (shuffle) / 5e-4 (random), floored by chance at 4 lines.

## Plaintext side (decoded runes; interrupters count 0)
| page | lines | passing | fraction | shuffle-null mean | p (shuffle) | p (random) |
|---|---|---|---|---|---|---|
| Runes - 01.jpg | 10 | 9 | 0.90 | 0.149 | 9.999e-05 | 9.999e-05 |
| 05.jpg | 10 | 4 | 0.40 | 0.188 | 0.09939 | 0.09069 |
| 06.jpg | 20 | 2 | 0.10 | 0.146 | 0.8134 | 0.7915 |
| 03.jpg | 8 | 4 | 0.50 | 0.158 | 0.0249 | 0.0174 |
| 14.jpg | 8 | 2 | 0.25 | 0.195 | 0.4893 | 0.3575 |
| 73.jpg | 4 | 1 | 0.25 | 0.148 | 0.5023 | 0.509 |
| POOLED | 60 | 22 | 0.367 | 0.162 | 9.999e-05 | 9.999e-05 |

## Ciphertext side (undecoded runes, same lines)
| page | lines | passing | fraction | shuffle-null mean | p (shuffle) | p (random) |
|---|---|---|---|---|---|---|
| Runes - 01.jpg | 10 | 1 | 0.10 | 0.156 | 0.8353 | 0.78 |
| 05.jpg | 10 | 4 | 0.40 | 0.188 | 0.09409 | 0.09099 |
| 06.jpg | 20 | 1 | 0.05 | 0.139 | 0.9543 | 0.9532 |
| 03.jpg | 8 | 1 | 0.12 | 0.141 | 0.7085 | 0.6947 |
| 14.jpg | 8 | 1 | 0.12 | 0.166 | 0.7734 | 0.7375 |
| 73.jpg | 4 | 0 | 0.00 | 0.166 | 1 | 1 |
| POOLED | 60 | 8 | 0.133 | 0.156 | 0.7429 | 0.6956 |

The ciphertext does not show it (8/60, 13.3%, vs null 15.6%, p = 0.74): the prime sums are a property of the plaintext
side of A WARNING, not of the ciphertext.

## Pooled verdict
Decision rule: pooled p(shuffle) < 0.01 AND >= 4/6 pages p(shuffle) < 0.05. Observed: pooled 1e-4 (yes), pages
p < 0.05 = 2 (01, 03), so NO-SEPARATION. Leave-one-out: pooled excluding A WARNING = 13/50 = 0.26
vs null 0.164, p(shuffle) = 0.053, p(random) = 0.034 - not significant at 0.01.
Per-page 06 (the largest page, 20 lines) is BELOW null (2/20), 14 and 73 are at null. The "designed prime lines" prior is
a post-hoc selection of the one page (A WARNING) where it holds; WELCOME 3/5 and SOME WISDOM 4/5 in the scream314 note
are title-/sub-block variants and are not stronger than chance (this lane: 03 = 4/8, p = 0.025 uncorrected; 05 = 4/10,
p = 0.099; title-excluded 05 = 4/9). Even 03's p = 0.025 is one of six tests (Bonferroni ~0.15).

## Confound analysis
- Line length (plaintext runes per line): min 5, median 28, mean 31.2, max 96.
- Line sums: mean 1434, range 157-4337.
- Base rate of primes at that size: 1/ln(mean sum) = 0.138; fraction of integers in the sum range that are prime = 0.133; the empirical shuffle null pass rate is 0.162 and the uniform-random null 0.150 (parity corrected 2/ln = 0.275 applies only to odd sums; all runes but F are odd so sum parity follows line length, which the shuffle null preserves).
- English control: random KJV windows with the solved pages' line lengths, mapped to GP, give a prime-sum rate of 0.157 - natural English is at base rate, so a pass rate near 0.15 is expected for any language and the recognizer's false-positive rate per line is ~0.15 (an all-lines-prime page of n lines has chance ~0.15^n: ~6e-9 for 9 lines, ~4e-4 for 4-5 lines).
- Multiplicity: any prime-sum lens was chosen after seeing A WARNING; as a recognizer clause for LP2 it only has power on pages whose author used the property, and the 5 other solved pages say the property is not general (pooled excluding A WARNING 26% vs 16%, p~0.05).

## Top-row scoring
Not run (NO-SEPARATION). No `plinefrac` SWEEPROW column defined.

## Coordinator decision
Whether to keep a "prime line sum" clause for a single-page A WARNING-style hypothesis (it could be applied to LP2 pages
as a per-page uniform test with p-floor 0.15^n, but this measurement gives no support that LP2 pages share the property).
Recommended: record as measured no-separation; do not use as a recognizer gate.
