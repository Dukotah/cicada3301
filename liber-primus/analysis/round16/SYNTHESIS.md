# Round 16 — Derived-Keystream Armada: Synthesis

_Date: 2026-08-23. Repo: Dukotah/cicada3301, branch `master`._

---

## NO SOLVE CANDIDATE

No lane in Round 16 returned `hit=true`. There is nothing to adversarially verify.
The round is a clean, multi-armed negative with every positive control passing.

---

## Trust anchor

`python tests/validate.py` → **ALL VALIDATIONS PASSED** (confirmed before synthesis).

---

## Per-lane verdict table

| Lane | Verdict | Positive control | Best score | Bar | Coverage bound |
|---|---|---|---|---|---|
| **scorer** | BOUND | PASS | −4.77 (signal, not null) | −5.5 | 5 solved pages + 200 random-keystream nulls; sigma separation +3.6% vs POC claim of +18% |
| **A-03** | BOUND | PASS | K_bound=26 merges | K_needed=93 | 13,381 components, 12,484 pairs; 3 convergent tests; K_est=0 |
| **zeroFP** | NEGATIVE | PASS (E-02A, E-02B, H-03 complete; E-01 and H-01 partial) | n/a | FP ≈ 1e-24/window | E-02A: 401 windows exhaustive; E-02B: 3 encodings × 85 gaps; H-03: 64 XOR trials |
| **F-01** | NEGATIVE | PASS | −7.032 | −5.5 | 40 decodes: 5 targets × 4 LP2 key variants × 2 signs |
| **KDF** | NEGATIVE | PASS | −6.259 | −5.5 | 692,064 decodes: 534 secrets × 27 KDF configs × 3 salts × 16 decode variants |
| **PRNG family** | NEGATIVE | PASS | −6.347 | −5.5 | 52,556 decodes: 7 generators × 1,877 seeds × 2 signs × 2 directions |

---

## Lane-by-lane detail

### scorer (round16/scorer)
**Hypothesis:** A matched runic quadgram scorer (correcting multi-char rune transliterations
K→C, V→U, Z→S, Q→C, TH/EO/NG/OE/AE/IA/EA) improves separation between English signal
and random-keystream null, enabling future lanes to run against a tighter bar.

**Verdict: BOUND.** The scorer is production-ready and imported by all subsequent lanes.
Positive control PASSES: all 5 known solved pages score above −5.5 (range −4.08 to −4.77).
Signal scores improved on all 5 pages (best improvement: CIRCUMFERENCE +0.291, A WARNING
+0.284). However, the POC's claimed noise-SD reduction (0.089 → 0.071, −20%) was NOT
reproduced: measured old SD = 0.0880, new SD = 0.0895 (+1.7% worse). Sigma separation
improved +3.6% (28.69σ → 29.71σ), not the claimed +18%. The gain is real but comes
entirely from signal improvement, not noise tightening. Gate 1 (positive control) PASSES;
Gate 2 (SD improvement) FAILS per the PREREG. Verdict is BOUND, not ERROR.

**What this closes:** the POC's noise-SD figures are measurement artifacts of a different
null construction. The scorer is a valid production instrument.

**What it does not close:** the SD improvement claim from FINDING.md.

**Artifacts:** `analysis/round16/scorer/scorer.py`, `measure.py`, `results.json`, `RESULTS.md`

---

### A-03 (round16/A-03)
**Hypothesis:** Haplographic merge audit of the 86 doublet sites. The cheap falsifier of
the whole engineered-filter edifice: if ~93 of the 86 doublet sites are transcription merges
(adjacent identical runes silently merged into one), autokey returns to the table.

**Verdict: BOUND.** Three convergent mapping-free tests all converge on K_est = 0 haplographic
merges. The instrument detects K ≥ 3 planted merges at 2-sigma (positive control PASS).
K_bound (instrument 2-sigma ceiling) = 26 merges, which is 3.6× below the K_needed = 93
autokey-restoral floor. The T3 doublet measurement is mapping-free (adjacent-equal shape
classes) and cannot be affected by the S/EO confusion cluster.

**What this closes:** haplographic merges as a route to restoring autokey. The doublet
deficit is structural, not a transcription artifact, to a confidence bound of K < 26.

**What it does not close:** merge rates above K = 26 (instrument ceiling), or merge types
other than adjacent-identical-rune collapse.

**Artifacts:** `analysis/round16/A-03/a03_hapl_bound.py`, `results.json`, `RESULTS.md`

---

### zeroFP (round16/zeroFP)
**Hypothesis:** Four zero-false-positive analytic tests (E-01 RSA/PKCS#1, E-02A permutation
window, E-02B doublet-gap correlation, H-03 cookie XOR cross) whose FP rates are computable
analytically and low enough to be decision-grade.

**Verdict: NEGATIVE (with one incomplete sub-test).** E-02A, E-02B, and H-03 are complete
nulls. E-01 is coverage-limited: the 2013 modulus is 432-bit (too small for the 256-byte
payload); the 7A35090F RSA-4096 moduli (the correct size) were not on disk and not fetched.
H-01 onion HTTP channel: 4/5 sub-tests complete, head malformation sub-test incomplete.

- **E-02A (permutation window):** 201 consecutive 56-byte windows and 200 57-byte windows
  exhaustive over the 256-byte payload — zero permutations of 0..55. FP rate ~1e-24/window.
- **E-02B (doublet-gap correlation):** payload as uint8/uint16-LE/uint16-BE correlated
  against 85 inter-doublet gaps; max Spearman |r| < 0.05, p > 0.69 — noise.
- **H-03 (cookie XOR cross):** 64 trials (2 cookies × 4 blobs × 8 offsets), zero above 80%
  printable threshold; max was 62.5% — within chance band.
- **H-01 (HTTP channel):** port sequence is sequential per-onion index; uptime encodes a
  constant already in HTML; leaked Linode IP is deanonymization artifact; head malformation
  sub-test incomplete (raw HTML not held).

**Open item:** E-01 completion requires `gpg --recv-keys 7A35090F`, extract moduli via
`pgpdump`, then `pow(int.from_bytes(canon_256,'big'), 65537, n)` for each modulus. The
script at `analysis/round16/zeroFP/zerofp_tests.py` accepts additional moduli.

**Also corrects a prior PROGRESS.md claim:** the 2013 modulus is 432 bits, not 365 bits.

**Artifacts:** `analysis/round16/zeroFP/zerofp_tests.py`, `results.json`, `RESULTS.md`, `gen_ct.py`

---

### F-01 (round16/F-01)
**Hypothesis:** The unsolved LP2 pages are key material, not a message. Use the 12,956-rune
stream (forward/reverse, ±1, Atbash) as a running key against every other machine-readable
Cicada object. This is a finite candidate set that was always marked `never-run` in RECON-A.

**Verdict: NEGATIVE.** Positive control PASSES: beam recovers planted LP2-keyed English at
−4.413, char-recovery 1.000, beats null_max −6.787 by 2.37 units — the lane is powered.
Full finite set swept: 40 decodes (5 targets × 4 key variants × 2 signs). Best score −7.032
(T1 Cicada 2012/2013 texts, LP2-forward key, sign=+1), which is 1.5 units below the −5.5 bar
and does not beat its size-matched null (null_max −6.972). All 40 results are deep noise
(−7.0 to −8.2). T5 (pp49-51 payload) was skipped — no binary payload file found.

**What this closes:** LP2-as-key against every held Cicada plaintext object, in all 4 key
variants and both signs. The `F-01` RECON-A entry is now `negative`, not `never-run`.

**What it does not close:** targets outside the 5 swept (other Cicada objects not held
locally); non-additive application of LP2 as key material; T5 (pp49-51 payload).

**Artifacts:** `analysis/round16/F-01/sweep.py`, `results.json`, `RESULTS.md`

---

### KDF / key-stretching (round16/KDF)
**Hypothesis:** The LP2 keystream is derived from a Cicada-flavoured secret via a KDF with
an iteration count (PBKDF2, scrypt, EVP_BytesToKey, iterated hash) — a construction a
cryptographically literate 2013-14 author would reach for. The B-04 not_covered list named
key stretching as the primary uncovered extension.

**Verdict: NEGATIVE.** Both positive controls PASS:
- K1 (D3 expander control): beam −4.17, char_recovery 0.989.
- K2 (plant-and-recover full sweep): PBKDF2-SHA256("THE PRIMES ARE SACRED", 3301, 10000)
  ranked #1 at −4.186 — well above bar.

Stage A ran 692,064 decodes across 534 secrets × 27 KDF configs × 3 salts × 16 decode
variants. Best score = −6.259 vs bar = −5.500. Score distribution: mean −7.341, SD 0.232;
best is ~4.7 SD above mean, consistent with upper-tail noise over 692k decodes. Top candidate
(sacrifice / iter_sha256_100000 / salt=self / rej29 / sign=+1 / atbash / rev) at −6.259 is
1.24 score units below the bar and 0.51 units above null max (−6.773) — within expected
best-of-N noise. Stage B (salt expansion) was not triggered (no Stage-A candidates cleared bar).

KDF configs swept: PBKDF2-SHA1/256/512 at 1000/2048/4096/10000/100000/3301; PBKDF2-SHA512 at
1000/4096/10000; scrypt RFC-7914 interactive; iterated SHA-256/MD5 at 1000/10000/100000/3301;
EVP_BytesToKey MD5 and SHA256 at 1 and 3301 rounds.

**What this closes:** 692,064 KDF-derived keystreams from a 534-secret Cicada dictionary at
27 construction variants × 3 salts × 16 decode variants, all scored at 120-rune head depth.
Key stretching is now a measured negative, not an untested extension.

**What it does not close:** iteration counts outside those tested; salts outside the 3 Stage-A
salts; Argon2 (anachronistic); bcrypt; secrets outside the 534-item list; per-page or
position-varying salts; multi-stage constructions; offsets ≠ 0.

**Artifacts:** `analysis/round16/KDF/RESULTS.md`, `results_A.json`, `results_gates.json`,
`results_summary.json`; scripts reused from `analysis/round15/KDF/`

---

### PRNG family (round16/prng)
**Hypothesis:** The uncovered PRNG generators named in the B-21/B-03 census — PHP `mt_rand`,
.NET System.Random, ISAAC, BBS, LFSR32, Geffe — produce a keystream that decodes LP2 under
a period-appropriate seed range and both signs and directions.

**Verdict: NEGATIVE.** Positive control PASSES: planted php_mt_rand(seed=3301) keystream
recovers at −4.155 / 100% char-match vs wrong-seed −6.935 — the lane is powered.

7 generators validated (php_mt_rand, dotnet_sysrandom, isaac, bbs_small, bbs_large, lfsr32,
geffe); 0 disqualified; 1,877 seeds (1,828 unix-second 2011–2015 at ~1/day stride + 49
lore/string seeds); mod-29 reduction; signs ±1; dirs fwd+rev; 52,556 total decodes. Best
score −6.347 vs bar −5.500. Null mean/max: −7.347/−6.709. Best is inside the null band.

**Validation caveat:** PHP mt_rand, .NET System.Random, and ISAAC cannot be cross-validated
against running runtimes (no PHP/Mono/.NET/C compiler on this machine); they pass
self-consistency and structural specification matching. BBS bbs_small is the only generator
with a fully external (analytical) reference.

**What this closes:** the 7 CENSUS-named uncovered generators over 1,877 period-appropriate
seeds at offset=0 and both orientations. The B-21/B-03 gap list is now partially measured.

**What it does not close:** unix-second seeds between daily samples (~23/24 of hour-stride
space); offsets ≠ 0; BBS moduli beyond the two tested; KISS/MWC/WELL/Fibonacci; full 2^32
sweep (~0.004% of 32-bit space per generator per orientation).

**Artifacts:** `analysis/round16/prng/prng_sweep.py`, `results.json`, `RESULTS.md`

---

## What Round 16 newly closes

1. **Key stretching (KDF)** — first measured negative over 692,064 KDF-derived keystreams
   from a Cicada-flavoured dictionary at 27 construction variants. This was the primary
   `not_covered` extension from B-04 and has never been run before.

2. **The seven CENSUS-named uncovered PRNG generators** over a period-appropriate seed range.
   PHP `mt_rand` — the highest-prior open generator in the census — is now a measured negative
   at ~0.004% of its 32-bit seed space (the same coverage class as Round 8, but for the
   previously-unrun generators).

3. **LP2-as-key inversion (F-01)** — the unsolved pages used as key material against all held
   Cicada plaintext objects: NEGATIVE in all 40 configurations. The RECON-A `never-run` flag
   is resolved.

4. **Haplographic merge bound (A-03)** — K < 26 merges at 2-sigma, 3.6× below the 93-merge
   autokey-restoral floor. The doublet deficit is structural, not a transcription artifact, to
   this confidence.

5. **Three zero-FP tests (E-02A, E-02B, H-03)** — all complete nulls at decision-grade FP
   rates.

6. **Matched runic scorer** — production-ready, positive controls pass, importable by future
   lanes. The POC's SD improvement claim is not supported by measurement.

---

## What remains genuinely un-run (coverage bounds, not terminal verdicts)

> The repo has been wrong with "closed" twice. These are coverage bounds.

**Still open inside the derived-keystream branch:**

- **KDF extensions:** Argon2 (anachronistic but non-zero prior), bcrypt, salts outside the
  3 Stage-A salts (especially onion-derived or pp49-51-derived salts), secrets outside the
  534-item list, per-page/position-varying salts, multi-stage constructions, KDF offsets ≠ 0.
- **PRNG seed coverage:** hour-stride unix-second seeds (×24 the current coverage per
  generator), offsets ≠ 0 (×~100 per generator), full 2^32 sweep (×~250 per generator),
  BBS moduli beyond the two tested, KISS/MWC/WELL/lagged Fibonacci generators.
- **E-01 RSA/PKCS#1:** the 7A35090F RSA-4096 moduli are the right size for the 256-byte
  payload and have never been checked. Completing requires `gpg --recv-keys 7A35090F` +
  `pgpdump` to extract moduli + `pow(payload_int, 65537, n)` for each.
- **F-01 T5:** the pp49-51 payload was not swept as target (file not held locally).
- **H-01 head malformation sub-test:** raw HTML not held locally.
- **A-03 merge types:** only adjacent-identical-rune collapse was bounded; other merge classes
  and merge rates above K=26 are unbounded.

**Open RECON-A items (still `never-run` or `open` in LEDGER.json, not touched by Round 16):**
A-01, A-02, A-04, A-05, A-06, B-01, B-02, B-03 (partial), C-01, C-02, D-01, D-02, D-03,
D-04, F-02, G-01, G-02, H-02, I-01, I-02 (partial), I-03, I-04 (partial), J-01.

---

## Notes on discipline

- Round 16 produced 6 lanes. All 6 had positive controls written and executed before the sweep.
  Zero false positives survived to synthesis.
- The adversarial-verify step (Task 1) had nothing to verify: no lane returned `hit=true`.
- All artifacts are under `analysis/round16/<lane>/`. Nav docs updated below.
