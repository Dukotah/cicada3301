# PREREG — Lane L9 "THE STANDARD BATTERY"

**Written before any test was run.** Round 10 armada, lane L9-randomness.
Repo state at prereg time: LP2 pages 0–54 characterised as OTP-class; every
randomness instrument in the repo (IoC, doublet profile, 4-gram score, bigram
plausibility, spectral-entropy ratio) is **bespoke**. No standard, off-the-shelf
cryptographic randomness battery and **no linear-complexity measurement of any
kind** appears anywhere in the ledger, DEAD_ENDS, or the 183-script analysis map.
Verified by grep for `nist|dieharder|testu01|berlekamp|linear complex|maurer|
universal|approximate entropy` across ELIMINATION-LEDGER.md, DEAD_ENDS.md,
ROUND-9-RESULTS.md, PICKUP-HERE.md — zero hits.

## Data

`liber-primus/analysis/seed_sweep/ct.bin` — 12,956 uint8 rune indices 0–28, LP2
unsolved pages 0–54 in file order. Re-verified at load: len 12,956, 29 distinct
symbols, index-0 count 458, adjacent-equal rate **0.6638 %**. This is the same
object Round 8's 2.52 × 10⁹-decode sweep ran on.

Information budget, stated up front because it bounds everything below:
12,956 × log₂29 = **62,940 bits** of maximum content.

## H0 / H1

- **H0 (the repo's current position):** the stream is an external one-time pad
  passed through a soft anti-repeat rewrite. Under H0 it is indistinguishable
  from a uniform-29 i.i.d. source with the same anti-repeat filter applied, on
  every test, at every mapping.
- **H1a (generator):** the pad is the output of a finite-state generator (LFSR,
  LCG, or any device with bounded state). Then its **linear complexity** — over
  GF(29) directly, or over GF(2) on a binary mapping — sits far below n/2.
  This is the generator-agnostic version of Round 8's SEED axis, which only
  covered 10 *named* generators over specific seed ranges.
- **H1b (depth):** the pad is reused somewhere in the book. Then some relative
  offset shows a Kerckhoffs coincidence excess.
- **H1c (unexplained structure):** some standard NIST statistic fires on the real
  stream and does *not* fire on the anti-repeat-matched control.

## Mappings (the declared hazard)

29 is not a power of 2. A failure caused by the mapping is **not** a failure of
the stream, and the only way to tell them apart is to push every control through
the identical mapping. Five mappings, all run on all four streams:

| id | mapping | bits out | bias |
|---|---|---|---|
| M1 | arithmetic / exact big-integer base-29 → base-2 | 62,940 | none (entropy-preserving) |
| M2 | rejection to 4 bits: keep runes 0–15, drop 16–28 | ~28,600 | none (uniform by construction) |
| M3 | 5-bit fixed-width, 29 of 32 codes used | 64,780 | **known, severe** — declared broken in advance |
| M4 | per-rune parity (index mod 2) | 12,956 | **known**, p(1)=14/29=0.4828 |
| M5 | gematria-prime residue mod 2 (prime > 2 ⇒ odd), i.e. prime mod 4 ≥ 2 | 12,956 | mild |

M3 and M4 are pre-declared as *expected to fail frequency-class tests for
mapping reasons*. They are included precisely so the write-up can show a
mapping-caused failure next to a stream-caused one.

## Controls (the methodological point of this lane)

Every test runs on four streams under every mapping:

- **REAL** — ct.bin.
- **SHUF** — random permutation of ct.bin (identical symbol multiset, order
  destroyed, anti-repeat destroyed).
- **URAND** — genuine uniform i.i.d. over 29 symbols, from `os.urandom`.
- **ARFILT** — uniform i.i.d. over 29 symbols passed through the *documented*
  soft anti-repeat rule: candidate equal to previous output is kept with
  probability p_keep, else redrawn. p_keep calibrated so the expected doublet
  rate p/(p+28) equals the measured 0.6638 % ⇒ **p_keep = 0.18714**.

**ARFILT is the whole point.** The anti-repeat filter is a *documented, known*
structure. Anything that trips because of it is not a discovery. An anomaly
counts only if REAL shows it and ARFILT does not.

20 independent replicates each of URAND and ARFILT, giving an empirical null
band for every statistic. Asymptotic p-values are reported but **the decision is
made against the empirical band**, because at 62,940 bits several NIST tests are
below their recommended n and their asymptotic p-values are not trustworthy.

## Pre-registered decision thresholds

**T1 — NIST battery.** For each (test, mapping): ANOMALY requires all three of
(a) REAL p < 0.001; (b) REAL statistic outside the full range of all 20 ARFILT
replicates; (c) the same not true of SHUF and URAND, or if it is, it is
attributed to the mapping and recorded as such. With ~15 tests × 5 mappings ≈ 75
comparisons, p < 0.001 is the Bonferroni-honest bar. Anything short of all three
is **NULL**.

**T2 — Linear complexity over GF(29)** (the headline test). For a random
sequence of length n over any field, LC ≈ n/2 = 6,478.
- **NULL/PASS:** LC(REAL) within the [min, max] range of the 20 ARFILT
  replicates, and ≥ 0.45 n = 5,830.
- **HIT (generator detected):** LC(REAL) < 0.45 n, **or** LC(REAL) below the
  minimum of all 20 ARFILT replicates by more than 3 sd of the null. A true LFSR
  of degree d yields LC = d exactly, so a genuine hit is expected to be
  dramatic (hundreds, not thousands) — the threshold is set loose deliberately
  so a *partial* generator signal cannot hide.
- Same thresholds applied to LC over GF(2) on M1, M2, M3 (n/2 of the respective
  bit lengths).
- The **LC profile** (the staircase of jumps) is also compared to the known
  random-sequence jump distribution; a generator shows a profile that flattens.

**T3 — Depth / pad reuse.** Kappa (coincidence) test at every lag
d = 1 … 12,955: k(d) = #{i : c[i] = c[i+d]}. Under no reuse, k(d)/(n−d) ≈ 1/29.
Under depth with two English plaintexts, it rises toward ≈ 0.06–0.07.
- **NULL:** max z over all lags is within the max-z distribution of the 20
  ARFILT replicates (this is the correct multiple-comparison control — comparing
  max to max).
- **HIT:** some lag with z ≥ 5.0 in REAL whose z exceeds the maximum-over-lags z
  of every one of the 20 ARFILT replicates.
- Also run on the *difference* stream and restricted to page-boundary-aligned
  offsets. This is DEPTH (statistical alignment over all offsets), which is a
  different object from the page-on-page keying already killed in Campaign IV.

**T4 — Known-structure calibration (validity gate).** Before any of the above is
believed, the instruments must be shown to *work*. Self-plant: an actual LFSR
over GF(29) of degree 40, and a 32-bit LCG stream, both pushed through the same
anti-repeat filter and the same mappings. If T2 does not recover their low
linear complexity, T2's null is meaningless and must not be reported as a
result. **This gate is pass/fail on the instrument, not on the ciphertext.**

## What a negative here does and does not buy

A clean null closes "the pad is any finite-state generator" *generator-agnostically*
— which is strictly more than Round 8's 10 named generators — and closes the
standard-battery blind spot. It does **not** close a cryptographically strong
generator (AES-CTR, SHA-chain, /dev/urandom), which by construction has maximal
linear complexity and passes every battery: those are indistinguishable from a
true pad by *any* statistical test, and no battery can ever reach them. That
limit is stated here, in advance, so the result is not over-read.

Compute budget: any single run under ~20 minutes; anything longer gets a
resumable script and a documented full run in the residue.
