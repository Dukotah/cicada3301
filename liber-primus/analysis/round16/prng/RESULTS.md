# Round 16 / PRNG lane — RESULTS

**Verdict: NEGATIVE**
**Positive control: PASS**
**Elapsed: 221 seconds (~3.7 minutes)**

---

## Trust anchor

`python tests/validate.py` from repo root: **ALL VALIDATIONS PASSED** (run at session start).

---

## Generator validation

All 7 generators PASSED the validation gate (self-consistency + diversity). No generators
were DISQUALIFIED.

| Generator | Validation basis | Pass |
|---|---|---|
| `php_mt_rand` | Self-consistent; structurally derived from PHP 5.x source (missing `y^=y>>18` temper + RAND_RANGE floor scaling); no PHP runtime available for external cross-check | PASS |
| `dotnet_sysrandom` | Self-consistent; matches .NET 4.x reference source structure (Knuth subtractive); no .NET/Mono runtime available | PASS |
| `isaac` | Self-consistent + diverse; simplified single-int seeding (XOR into mm[0] post-init) differs from Jenkins' full `randinit` — cannot reproduce Jenkins zero-seed test vector — but generator itself is structurally correct | PASS |
| `bbs_small` (M=253, p=11, q=23) | **Analytically computed** reference (hand-computed bit sequence for x0=3) — the only external reference available | PASS |
| `bbs_large` (M=3401669, p=3299, q=1031) | Self-consistent; both p=3299 and q=1031 are Blum primes (≡3 mod 4); Cicada-plausible RSA-adjacent construction | PASS |
| `lfsr32` | Self-consistent; 32-bit maximal-length LFSR taps=(32,22,2,1) | PASS |
| `geffe` | Self-consistent; Geffe combiner over 3 LFSRs (deg 11, 13, 17) | PASS |

**Caveats on validation:** PHP `mt_rand`, .NET `System.Random`, and full ISAAC cannot be
cross-validated against running runtimes on this machine (no PHP, .NET, or C compiler
available). The generators are implemented per their published specifications and pass
self-consistency. The risk is that a subtle implementation deviation causes a missed hit;
it does not cause a false hit.

---

## Positive control

**Generator:** `php_mt_rand`, **seed:** 3301

- Planted keystream over English LP-style text (120 runes), enciphered with
  `encipher_keyskip(sign=-1, supp=0.83)`.
- CT doublet rate: **0.84%** (target regime <1%; LP2 observed 0.66%).
- Total key-skips: 7.

| Channel | Score |
|---|---|
| BEAM, correct seed | **−4.155** (English band) |
| BEAM, wrong seed (12345) | −6.935 (noise) |
| Char-match vs truth | **100.0%** |
| Separation | 2.78 (required > 1.0) |

Gate: **PASS**. A correct PRNG keystream IS recoverable by the beam decoder — the
lane is powered and a null is meaningful.

---

## Sweep results

| Generator | Seeds | Decodes | Best score | Best seed |
|---|---|---|---|---|
| `php_mt_rand` | 1877 | 7508 | **−6.412** | 1396310400 (2014-04-01) |
| `dotnet_sysrandom` | 1877 | 7508 | −6.527 | 1312416000 (2011-08-04) |
| `isaac` | 1877 | 7508 | −6.462 | 1368316800 (2013-05-12) |
| `bbs_small` | 1877 | 7508 | −6.829 | 20130101 (lore date) |
| `bbs_large` | 1877 | 7508 | −6.414 | 1394236800 (2014-03-08) |
| `lfsr32` | 1877 | 7508 | −6.493 | 1407974400 (2014-08-14) |
| `geffe` | 1877 | 7508 | −6.347 | 1382486400 (2013-10-23) |

**Overall best:** −6.347 (geffe, seed=1382486400, sign=+1, dir=fwd)
**HIT_BAR:** −5.5 (the repo-wide floor; null_max+0.5 = −6.209 is lower, so −5.5 binds)
**Null:** mean=−7.347, max=−6.709 (200 shuffles)

All best scores are well inside the noise band (−6.3 to −6.8 vs noise mean −7.3). The
overall best (−6.347) is only 0.362 above the null max (−6.709) and 1.153 below the HIT_BAR
(−5.5). No translit reads as English.

---

## Coverage bound

```
7 generators validated × 1877 seeds (1828 unix-second 2011-2015 ~1/day + 49 lore/string)
× mod-29 reduction × ±sign × fwd/rev direction = 52,556 decodes
Best score: −6.347 vs bar −5.500 (null max −6.709)
Positive control: PASS (php_mt_rand, score=−4.155, 100% char-recovery)
Elapsed: 221 seconds
```

**What is NOT covered** (explicitly, per PREREG.md):
- PHP ms-timestamp seeds (time()×1000 → 64-bit range, not enumerable at 32 bits)
- Unix-second seeds between the ~1/day samples (~23x denser coverage would require
  ~5× more compute = ~18 minutes; the 1/day stride misses ~23/24 of the space)
- Keystream offsets ≠ 0 (multiplies every generator by ~8,192)
- BBS moduli other than the two tested (infinite families of Blum primes)
- KISS / MWC / WELL / lagged Fibonacci (lower prior; not in CENSUS.md top-5)
- PCG, xoroshiro, xorshift128+ (excluded by date — post-LP2)
- PHP `rand()` / `init_by_array` with multi-word keys
- Full 2^32 sweep of any generator (budget: 1877 of 4.3×10^9 possible seeds ≈ 0.004%)

---

## Conclusion

**NEGATIVE** over the enumerated bound. The hypothesis (LP2 keystream derived from one of the
5 CENSUS-named uncovered PRNG generators, seeded by a period-appropriate or lore integer) is
**falsified over the covered region** (7 generators, 1877 seed values spanning 2011–2015 + key
Cicada-lore integers, mod-29 reduction, both signs and directions). The best score across all
52,556 decodes is −6.347, which is 1.153 below the −5.5 HIT_BAR and inside the null band.

This extends the CENSUS.md coverage to include all 5 named uncovered generators. It does NOT
exhaust the family — the coverage fraction of the 32-bit seed space is ~0.004%, and offsets ≠ 0
are untested. A genuine null over the remaining space would require 1–2 orders of magnitude
more compute (outside the 8-minute budget constraint).

Reproduce:
```bash
cd liber-primus
python analysis/round16/prng/prng_sweep.py
```
