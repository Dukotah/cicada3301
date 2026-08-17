# LENS N3 — whole book as one integer / number-theoretic structure

**Verdict: NEGATIVE** (positive control PASSED; refuted by default, no structure exceeds the null).

## What was tested
The prime-value stream `nc.v_prime(u)` (and the prime-index, totient, and mod-29 value
streams) were concatenated as decimal digits into large integers — **per segment** (55
unsolved segments) and **whole-book** — then probed for number-theoretic structure:
primality (Miller-Rabin), small-factor / RSA-shape structure (bounded trial division +
Pollard-rho), perfect powers `a**k`, Mersenne-ish `2**k ± 1`, notable bit-lengths
(SHA-160/256/384/512, RSA-1024/2048/4096, the page-56 512-bit hash length), and embedded
ASCII (printable-byte ratio of the raw big-int bytes).

This is a **structure probe**, so the verdict is driven by an observed structure count vs a
size-matched shuffled-value control — not by the English scorer (which is logged only for
the harness).

## Positive control — PASS (11/11)
Primality/factor/perfect-power/Mersenne code verified on known inputs:
`is_prime(2^31-1)=True`, `is_prime(2^67-1)=False`, `is_prime(2^61-1)=True`,
`factor(2^67-1)=[193707721, 761838257287]` (Cole 1903), `factor(1000003·1000033)` recovered,
`perfect_power(7^13)=(7,13)`, `perfect_power(1000003)=None`, `mersenne_ish(2^127-1)`,
`mersenne_ish(2^64+1)`, and a planted-prime concatenation (M89 digits) detected as prime.

## Real data — no structure
Per-segment (55 integers, ~500 digits / ~1660 bits each):
- primes: **0** · perfect powers: **0** · Mersenne-ish: **0** · near hash/RSA bit-length: **0**
  · RSA-shape semiprimes: **0** · notable segments: **0**.

Whole-book integers:
| stream | digits | bits | prime | bit_note | mersenne | perfect_power | byte-printable |
|---|---|---|---|---|---|---|---|
| prime-concat | 25914 | 86084 | (>20k-bit, skipped) | none | none | (too big) | 0.367 |
| prime-index-concat | 21971 | 72984 | " | none | none | " | 0.376 |
| totient-concat | 25914 | 86084 | " | none | none | " | 0.371 |
| mod29-concat | 21525 | 71502 | " | none | none | " | 0.366 |

Bit-lengths (71k–86k) are nowhere near any hash/RSA landmark. Printable-byte ratio ≈0.37 is
at the random-binary baseline (~0.36), so no embedded ASCII. Primality of the ~80k-bit
whole-book integer is not a meaningful cryptographic object and was intentionally out of
compute scope (size-guarded).

## Null control (seed 3301, 200 draws)
Shuffled value stream, re-segmented to the same sizes:
- **real** structure total = **0** (primes 0)
- **null** total: mean **0.125**, **max 2**; null primes: mean 0.125, max 2.

The real stream has *less* incidental number-theoretic structure than the shuffle control
(shuffles occasionally produce a small-prime concatenation; the real stream produced none).

## Decision-rule numbers
- English bookkeeping (letter stream, not the verdict driver): real **-7.440**, null_mean
  -7.496, null_max **-7.466** → at the noise floor, english_hit = False.
- Structure hit requires real_total ≥ null_max+1 and > 0: **0 < 2** → False.
- Whole-book landmark (prime / notable bits / Mersenne / perfect power): **None** → False.

**HIT bar not met on any axis.** The whole-book-as-integer / number-theoretic-structure
reading carries no signal above a histogram-preserving shuffle.
