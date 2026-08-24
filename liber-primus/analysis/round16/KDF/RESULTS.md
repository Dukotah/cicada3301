# Round 16 / KDF — RESULTS

_Run completed 2026-08-23. Full Stage-A sweep._

## Trust anchor

`python tests/validate.py` (run before the sweep) = **ALL VALIDATIONS PASSED**.

## Gates

| Gate | Result | Detail |
|---|---|---|
| K1 — D3 expander control | **PASS** | beam=-4.17 (≥−5.5), char_recovery=0.989 (≥0.90), rigid=-6.835 (<−6.0) |
| K2 — plant-and-recover full sweep | **PASS** | Planted PBKDF2-SHA256("THE PRIMES ARE SACRED","3301",10000) ranked #1 at score -4.186; bar is -5.5; planted config is rank#1=True, clears bar=True |

Both gates pass. The null result below is NEGATIVE, not INCONCLUSIVE.

## Null band

Histogram-preserving shuffle null, n=200, head L=120:
- null mean = -7.399
- null max  = -6.773
- HIT bar   = max(-5.5, null_max + 0.5) = **-5.500** (the -5.5 floor binds)

## Stage A sweep

| Metric | Value |
|---|---|
| Secrets | 534 (504 B-04 core + 30 passphrase groups, deduplicated) |
| KDFs | 27 configs (PREREG §4.2) |
| Stage-A salts | `empty`, `3301`, `self` |
| Reductions | 2 (mod29, rej29) |
| Signs × atbash × direction | 2 × 2 × 2 = 8 |
| Offset | 0 only |
| Head length | 120 runes |
| Total decodes | 692,064 |
| Elapsed | 1044s (~17.4 min of Stage A; 34.1 min total including K2 gate) |
| Best score | **-6.259** |
| Bar | -5.500 |
| Candidates over bar | **0** |
| Verdict | **NEGATIVE** |

## Score distribution

Sample mean = -7.341, sample SD = 0.232. The best score (-6.259) is (−6.259 − (−7.341)) / 0.232 ≈ **4.7 SD above the sample mean** — consistent with the upper tail of noise over 692k decodes. No candidate is remotely close to the -5.5 bar; the gap from best to bar is 1.24 score units.

## Top-5 candidates (all noise)

| Rank | Score | Secret | KDF | Salt |
|---|---|---|---|---|
| 1 | -6.259 | sacrifice | iter_sha256_100000 | self |
| 2 | -6.301 | DO FOUR UNREASONABLE THINGS EACH DAY | iter_sha256_3301 | self |
| 3 | -6.321 | ADHERE | iter_sha256_100000 | self |
| 4 | -6.351 | WELCOME PILGRIM TO THE GREAT JOURNEY… | pbkdf2_sha512_4096 | 3301 |
| 5 | -6.366 | thelossofdivinity | iter_sha256_1000 | 3301 |

No candidate approaches the bar. The top score (-6.259) is well within the null band (null max was -6.773; the top score is 0.51 units *above* the null max, which is within expected best-of-692k noise).

## Coverage bound

**Fully swept:** 27 KDF configs × 534 secrets × 3 salts (empty/3301/self) × 16 decode variants = 692,064 decodes. All 27 KDF configs were run at full scale including the expensive ones (PBKDF2-SHA1-100000, PBKDF2-SHA256-100000, scrypt-16384-8-1, iter-SHA256-100000). No subsampling was needed — the full cross-product completed.

**Not covered (from PREREG §7):**
- Iteration counts outside §4.2; salts outside the 3 Stage-A salts; Argon2/bcrypt; secrets outside the 534-item list; per-page or position-varying salts; multi-stage constructions.
- Stage B (full salt expansion over top KDF families) was not run, because Stage A produced no candidates above the bar that would trigger B.

## Verdict

**NEGATIVE** over the declared §4 bound. Both positive controls pass. The ciphertext returns noise under every (secret, KDF, iteration count, salt, reduction, sign, atbash, direction, offset=0) combination in the pre-registered grid.

This does not rule out KDF constructions outside the bound (exotic salts, unusual iteration counts, Argon2, secrets not in the dictionary). Those remain explicitly open. A negative here closes §4 and nothing more.

## Artifacts

- `PREREG.md` — this file's pre-registration
- `results_gates.json` — K1 and K2 gate output
- `results_A.json` — Stage A top-300 candidates and distribution summary
- `results_summary.json` — sweep-level summary with verdict
- Source harness: `analysis/round15/KDF/sweep.py`, `analysis/round15/KDF/kdf.py`
