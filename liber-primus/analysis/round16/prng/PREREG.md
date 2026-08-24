# Round 16 / PRNG lane — PRE-REGISTRATION

_Written before any sweep output was seen. Lane: PRNG family (uncovered generators
from CENSUS.md). Trust anchor: `python tests/validate.py` from repo root._

---

## 1. Hypothesis

**H1.** The LP2 0–54 keystream is derived from one of the UNCOVERED PRNG generators
named in `analysis/round10/L5-seed32/CENSUS.md` §C, seeded by a period-appropriate or
Cicada-lore integer, reduced mod 29, applied additively under the key-skip filter.

Generators under test (ordered by prior, per CENSUS.md):
1. **PHP `mt_rand()`** — highest-prior open generator. PHP's Mersenne Twister has a
   documented deviation from reference MT19937 (`MT_RAND_PHP` bug, pre-PHP 7.1).
   The Cicada PHP stack (2012–14) ran PHP 5.x. Cannot be reached from generator 5
   (reference MT) because PHP's version produces a different integer stream.
2. **.NET `System.Random`** — Knuth subtractive / lagged-Fibonacci, seeded via the
   161803398 constant. Structurally unlike any covered generator.
3. **ISAAC** — Bob Jenkins crypto-adjacent stream cipher. Low–medium prior.
4. **Blum–Blum–Shub (BBS)** — crypto-flavoured generator using RSA-like moduli;
   ARMADA-20 only tested 2,080 keyword-seeded configs, never a unix-second sweep.
5. **LFSR / Geffe / Gollmann** — classic textbook stream-cipher constructions;
   low–medium prior for a puzzle author with a crypto flavour.

**H0 (null).** No seed in the enumerated set, under any of the above generators
with any enumerated reduction/sign/direction, produces English when beam-decoded.

---

## 2. Instrument

**Decoder:** `beam_decode` from `analysis/campaign18_skip/skipdecode.py` (skip-tolerant,
beam_w=400, max_skip=3). This is mandatory — CENSUS.md and PREREG documents establish
that rigid 1:1 alignment produces guaranteed false negatives.

**Scorer:** `Q.score_norm` (quadgram per-symbol log-prob). Scale: English solves
≈ −4.0…−4.5, threshold −5.5, noise ≈ −7.5.

**Sign convention:** `score_norm` is negative; higher (closer to zero) = more English.

---

## 3. Generator validation gate (before any sweep)

**Rule:** a generator that does not reproduce a known reference stream is DISQUALIFIED
and not swept. A disqualified generator is reported as DISQUALIFIED, not NEGATIVE.

Reference vectors for each generator must be validated against an independent
reference BEFORE sweeping:

| Generator | Reference used |
|---|---|
| PHP `mt_rand` | Known PHP 5.x MT_RAND_PHP test vector (Yasuo Ohgaki documentation / PHP source) |
| .NET System.Random | Known .NET 4.x output for seed 12345 |
| ISAAC | Bob Jenkins test vector from reference C source |
| BBS | Known BBS output with documented modulus p=11, q=23 (n=253), seed=3 |
| LFSR/Geffe/Gollmann | Known shift-register sequences (maximal-length taps) |

---

## 4. Seed set (pre-registered, locked)

**Unix-second seeds (period-appropriate):** 2011-01-01 00:00:00 UTC (1293840000)
through 2015-12-31 23:59:59 UTC (1451606399), subsampled to one seed per HOUR
(~43,824 seeds). This covers all timestamps a 2012–2014 author would plausibly call
`time()` as a seed.

**Cicada lore/date seeds (string → int):** The integer values of:
- 3301, 1033, 761, 29
- 845145127, 1595277641 (known Cicada numbers)
- 20140107 (LP2 posting date YYYYMMDD)
- 20120101, 20130101, 20140101 (puzzle announcement years)
- 314159, 271828, 1618033 (mathematical constants)
- 1729, 6174 (known mathematical curiosities)
- 0, 1, 42
- Each of: 3, 5, 7, 11, 13, 17, 19, 23, 29, 31 (small primes)
- String seeds hashed to 32-bit: hash("THE PRIMES ARE SACRED") mod 2^32,
  hash("CICADA3301") mod 2^32, hash("AN END") mod 2^32,
  hash("LIBER PRIMUS") mod 2^32

**Total lore seeds:** ~60 additional integer seeds.

**Total sweep budget:** ~43,884 seeds × 5 generators × 2 reductions (mod29 + rej29)
× 2 signs × 1 direction × 1 offset = ~878K decodes for the full PRNG sweep.
Bounded to complete in ~8 minutes.

---

## 5. Positive control (mandatory before any result is trusted)

**Plant-and-recover test using PHP mt_rand (or the first validated generator):**
1. Pick a seed known to the dictionary (e.g., 3301).
2. Generate a keystream from the validated PHP mt_rand implementation.
3. Encipher an English LP-style text under `encipher_keyskip(sign=-1, supp=0.83, seed=3301)`.
4. Run the full beam-decode against the synthetic ciphertext using ONLY the correct
   generator+seed. Require: beam score ≥ −5.5, char-recovery ≥ 0.90.
5. Run against a wrong seed (12345). Require: wrong-seed score < correct − 1.0.

If this gate fails, the lane is INCONCLUSIVE regardless of sweep results.

---

## 6. Decision threshold

`HIT_BAR = −5.5` (repo-wide bar; the −5.5 floor binds, per PREREG §5 of Round 13 B-04).

**HIT** iff beam score_norm ≥ −5.5 AND the candidate survives escalation to the
full 12,956-rune stream AND reads as English across more than one page.

**NEGATIVE** iff positive control PASSES and no seed clears the bar.

**INCONCLUSIVE** iff positive control FAILS or the sweep does not complete.

---

## 6. Coverage bound (what this run explicitly does NOT cover)

- PHP ms-timestamp seeds (time() × 1000 — 64-bit range, not sweepable)
- Keystream offsets ≠ 0
- PHP `init_by_array` with multi-word keys
- BBS moduli other than the documented test-vector modulus and a small set of
  Cicada-number-derived moduli
- WELL / KISS / MWC / lagged Fibonacci (lower prior; not in top-5 CENSUS list)
- PCG, xoroshiro, xorshift128+ (excluded by date — published after LP2)
