# I1 — DRIFT-TOLERANT DECODER — RESULTS

_Round 19, Phase 0, BLOCKING. Pre-registered in [`PREREG.md`](PREREG.md) before any
measurement; one dated addendum, at the bottom of that file, explaining why kill-condition A
did not stop the lane. No threshold in this document was changed after a number was seen._

## GATE VERDICTS

| gate | verdict | the number |
|---|---|---|
| **G-EQ** — `mode="keyskip1"` is bit-identical to `skipdecode.beam_decode` | **PASSED** | max abs score delta **1.07e-14** over 24 cases, **0** plaintext-path mismatches; and **0.00e+00** vs `round18/L2` `fastbeam` over 12 more |
| **G-BASE** — no regression on the construction the repo decoder is exact for | **PASSED** | worst delta over 8 baseline cells: score **+0.000**, recovery **+0.0 pp**. Full book L = 12,956: **-4.318 / 99.81 %** (permissive) vs **-4.322 / 99.88 %** (repo), both clear the -5.5 / 0.90 bar |
| **G-FIX** — correct key recovered on every construction in L7-B's failure table | **PASSED** | **20 / 20** gate cells at `lam` in {4, 6, 8, 12} and at `max_free` in {1, 2, 3}. The repo decoder scores **0 / 20** on the same cells |
| **G-FP** — a wrong key stays in the noise band | **PASSED at `lam` >= 8; FAILED at `lam` <= 6** | at `lam` = 8 and 12, **0 / 2000** wrong keys reach -5.5 on either null (max **-5.667** / **-6.072**); at `lam` = 4, **11.3 %** of 2000 wrong keys clear -5.5; at `lam` = 0, **100 %** do |
| **G-COST** — the price Phase 2 pays | **PUBLISHED** | **0.000** score and **0.0 pp** recovery on the baseline construction. The real price is elsewhere: the wrong-key null moves up by **+0.58** (`lam` = 12) and the decode costs **5-9x** more time at L = 240-400, **2.6x** at full book |

**Headline.** The L7-B defect is repaired. `skip_by_two` — the construction that reproduces
LP2's own doublet rate and that the repo decoder misses at **-6.90 / 25.8 %** — is recovered at
**-4.285 / 100.0 %**. So are free drift at q = 0.10, ten unrepresentable key advances per 240
runes, a second independent two-draws variant built here, and the low-entropy-pad cases at
constant-run length 16 and 32. **The repair is not free**, and the part of it that is not free
is the null, not the power: a permissive transition relation raises the wrong-key distribution
by 0.6-0.9, so **Phase 2 must not adjudicate a permissive decode against the -5.5 floor.**
Per-mode extreme-value parameters for I3 are in `out_fp_tail.json`.

---

## 0. Trust anchor

| | before the lane | after the lane |
|---|---|---|
| `python3 liber-primus/tests/validate.py` | ALL VALIDATIONS PASSED (5/5 known solves) | ALL VALIDATIONS PASSED (5/5) |
| `python3 -m pytest liber-primus/benchmark/ -q` | 8 passed | 8 passed |
| `python3 -m pytest .../round19/I1/test_driftbeam.py -q` | — | **15 passed** |

Environment: WSL Ubuntu, Python 3.14.4, 6 cores. Every score is
`lp.score.default().score_norm`; every recovery is on **rune indices**, never on the
transliteration string (7 of 29 runes are two characters). Beam width 400 everywhere, so that
every number is comparable to `round18/L7-redteam/out_b1.json`.

**Replication check.** Run through this lane's harness, the repo decoder reproduces L7-B's
published numbers to the third decimal: `skip_by_two supp=0.83` **-6.903** (L7-B: -6.90),
`drift_at n=5` **-6.674** (-6.67), `free_drift q=0.05` **-6.883** (-6.88), `runs r=16 ms=8`
**-6.503** (-6.50), `runs r=32 ms=8` **-7.054** (-7.05). The harness is the same instrument.

---

## 1. What the fix actually is

The repo's validity test — *every skipped key position must have reproduced the previous cipher
rune* — has a closed form nobody had written down. For an accepted key index `acc` at rune `i`:

```
(p - sign*K[m]) % N == c_prev   with   p = (c_i + sign*K[acc]) % N
   <=>   K[m] == (K[acc] - sign*(c_prev - c_i)) % N   =:  v(acc)
```

**Every skipped position must hold one single key value `v(acc)`, and that value is fixed by
`K[acc]`.** So the count of *unexplained* skips is `dsk - cnt[v(acc)]`, where `cnt` is a 29-bin
histogram of the skipped window maintained in O(1) as `acc` advances, and the whole `dsk` loop
may break as soon as `dsk - max(cnt) > max_free` (that quantity is monotone non-decreasing).

Three consequences, all measured below:

1. `max_free = 0` **is** the repo's relation — gate G-EQ, not an argument.
2. On a high-entropy pad the loop breaks after ~`max_free`+1 branches, so `max_skip` may be set
   to 40 **at no cost**. That is what fixes the constant-key-run failures, where `dsk`
   legitimately reaches the run length.
3. The penalty `lam` steers the search only. The **reported score is the unpenalised quadgram
   `score_norm` of the path the penalised search chose**, so it stays on the project's canonical
   scale (`test_reported_score_is_unpenalised_quadgram`).

Modes:

| mode | relation | exact for |
|---|---|---|
| `keyskip1` | `dsk` skipped positions, all doublet-consistent | `encipher_keyskip` |
| `keyskip2` | `dsk` even; even offsets doublet-consistent, odd offsets free | `skip_by_two` |
| `permissive` | any `dsk <= max_skip`, at most `max_free` of them not doublet-consistent, `lam` each | nothing in particular — that is the point |

Named configurations used throughout (`run_gates.MODES`):

| name | mode | max_skip | max_free | lam | start_slack |
|---|---|---|---|---|---|
| `repo_ms3` | keyskip1 | 3 | 0 | — | 0 |
| `exact_ms8` | keyskip1 | 8 | 0 | — | 0 |
| `exact_auto` | keyskip1 | `suggest_max_skip(K)` | 0 | — | 0 |
| `pair_ms8` | keyskip2 | 8 | 0 | — | 0 |
| `drift_lX` | permissive | `suggest_max_skip(K)` | 2 | X | 2 |
| `drift_mf1` / `drift_mf3` | permissive | `suggest_max_skip(K)` | 1 / 3 | 8 | 1 / 3 |
| **`drift_rec`** (= `drift_l12`) | permissive | `suggest_max_skip(K)` | 2 | 12 | 2 |

`suggest_max_skip(K) = max(40, 2 * longest_constant_run(K) + 8)`.

---

## 2. G-EQ — equivalence (blocking) — **PASSED**

`out_eq.json`. 24 random (ciphertext, keystream) cases at L in {60, 120, 400}, both signs,
offsets 0-7, beam 400, `max_skip` 3.

| comparison | max abs score delta | path mismatches |
|---|---|---|
| `driftbeam(keyskip1)` vs `campaign18_skip.skipdecode.beam_decode` | **1.066e-14** | **0** |
| `driftbeam(keyskip1)` vs `round18/L2-filter-leak.fastbeam` | **0.000e+00** | **0** |

The histogram identity of §1 is separately checked against a brute-force re-implementation of
the original per-position validity loop over 4,800 random configurations
(`test_histogram_matches_naive_relation`).

---

## 3. G-BASE — no regression — **PASSED**

`out_base.json`, `out_book.json`. Correct key, English plaintext, 7 seeds per cell.

| baseline construction | L | `repo_ms3` | `exact_ms8` | `pair_ms8` | `drift_l0` | `drift_l8` | `drift_l16` |
|---|---|---|---|---|---|---|---|
| keyskip supp=0.0 | 240 | -4.303 / 100.0% | -4.303 / 100.0% | -4.303 / 100.0% | -4.617 / 17.1% | -4.303 / 100.0% | -4.303 / 100.0% |
| keyskip supp=0.4 | 240 | -4.302 / 100.0% | -4.302 / 100.0% | -5.748 / 63.3% | -4.563 / 26.7% | -4.302 / 100.0% | -4.302 / 100.0% |
| keyskip supp=0.83 | 240 | -4.303 / 100.0% | -4.303 / 100.0% | -6.631 / 37.9% | -4.527 / 51.2% | -4.285 / 100.0% | -4.303 / 100.0% |
| keyskip supp=1.0 | 240 | -4.303 / 100.0% | -4.303 / 100.0% | -6.159 / 46.7% | -4.405 / 49.2% | -4.285 / 100.0% | -4.303 / 100.0% |
| keyskip supp=0.0 | 400 | -4.332 / 100.0% | -4.332 / 100.0% | -4.332 / 100.0% | -4.785 / 12.2% | -4.332 / 100.0% | -4.332 / 100.0% |
| keyskip supp=0.4 | 400 | -4.332 / 100.0% | -4.332 / 100.0% | -5.770 / 59.5% | -4.831 / 18.0% | -4.332 / 100.0% | -4.332 / 100.0% |
| keyskip supp=0.83 | 400 | -4.332 / 100.0% | -4.332 / 100.0% | -6.401 / 41.2% | -4.675 / 33.0% | -4.332 / 100.0% | -4.332 / 100.0% |
| keyskip supp=1.0 | 400 | -4.332 / 100.0% | -4.332 / 100.0% | -6.287 / 45.2% | -4.668 / 31.2% | -4.332 / 100.0% | -4.332 / 100.0% |

`drift_l12` matches too: **-4.285 / 100.0 %** at L = 240 and **-4.332 / 100.0 %** at L = 400.

**Two findings live in this table and neither was expected.**

- **`keyskip2` is not a drop-in.** It is exact for `skip_by_two` and it *breaks the baseline*:
  -6.631 / 37.9 % at supp = 0.83, because an odd number of skipped positions is unrepresentable
  in it. A decoder that knows which loop was written is better than one that doesn't; a decoder
  that guesses wrong is worse than the one it replaced. **The permissive mode is the only single
  configuration that covers both**, and that is its whole justification.
- **`lam = 0` is a trap and it looks like a success.** With no penalty the beam scores
  -4.4 to -4.8 on every construction — *better than the bar* — while recovering **12-51 %** of
  the runes. It is not decoding; it is generating English. This is pinned as a regression test
  (`test_unpenalised_permissive_is_a_known_failure`) and it is the reason the pre-registered
  kill-condition A did not fire (PREREG addendum). **Any future "soft" decoder in this project
  must be validated on rune recovery, not on score.**

### 3.1 Full-book control, L = 12,956

`out_book.json`. Reference: `round18/L2-filter-leak/RESULTS.md` §B.3, -4.098 / 0.9997 (that
lane used a KJV plaintext; this one uses the L7-B English stream, hence the small offset).

| mode | seed | key | score | rune recovery | inferred / true skips | s |
|---|---|---|---|---|---|---|
| `repo_ms3` | 0 | correct | -4.322 | 99.88 % | 418 / 418 | 42 |
| `repo_ms3` | 1 | correct | -4.351 | 99.98 % | 382 / 382 | 41 |
| `repo_ms3` | 2 | correct | -4.334 | 99.98 % | 361 / 361 | 42 |
| `repo_ms3` | 0 | **wrong** | -7.278 | 3.77 % | 302 / 418 | 43 |
| `drift_l8` | 0 | correct | **-4.318** | **99.81 %** | 418 / 418 | 110 |
| `drift_l8` | 1 | correct | -4.350 | 99.82 % | 382 / 382 | 112 |
| `drift_l8` | 2 | correct | -4.331 | 99.93 % | 361 / 361 | 109 |
| `drift_l8` | 0 | **wrong** | -6.615 | 4.88 % | **1537** / 418 | 108 |

Both clear the pre-registered bar (>= -5.5 and >= 0.90). Separation at full book:
**2.96** for the repo decoder, **2.30** for the permissive one.

---

## 4. G-FIX — the point of the lane — **PASSED**

`out_fix.json`, `out_fix2.json`. Correct key supplied. English plaintext pinned. 7 seeds per
cell, medians shown as `score / rune recovery`; `✗` = below the pre-registered
`score >= -5.5 AND recovery >= 0.90` bar.

**L = 240**

| construction | `repo_ms3` | `exact_auto` | `pair_ms8` | `drift_l0` | `drift_l8` | `drift_l12` |
|---|---|---|---|---|---|---|
| skip_by_two supp=0.5 | -6.081 / 45.0% ✗ | -6.081 / 45.0% ✗ | -4.285 / 100.0% | -4.734 / 18.8% ✗ | -4.285 / 100.0% | -4.285 / 100.0% |
| skip_by_two supp=0.83 | -6.903 / 25.8% ✗ | -6.903 / 25.8% ✗ | -4.285 / 100.0% | -4.730 / 13.3% ✗ | -4.285 / 100.0% | -4.285 / 100.0% |
| skip_by_two supp=1.0 | -6.857 / 24.6% ✗ | -6.857 / 24.6% ✗ | -4.285 / 100.0% | -4.679 / 15.0% ✗ | -4.285 / 100.0% | -4.285 / 100.0% |
| free_drift q=0.05 | -6.883 / 22.1% ✗ | -6.883 / 22.1% ✗ | -6.728 / 27.5% ✗ | -4.575 / 34.2% ✗ | -4.296 / 98.8% | -4.334 / 97.9% |
| free_drift q=0.10 | -7.151 / 8.3% ✗ | -7.151 / 8.3% ✗ | -6.997 / 16.7% ✗ | -4.508 / 47.5% ✗ | -4.296 / 98.3% | -4.431 / 94.6% |
| drift_at n=5 / 240 | -6.674 / 25.8% ✗ | -6.674 / 25.8% ✗ | -7.004 / 26.2% ✗ | -4.495 / 40.4% ✗ | -4.285 / 99.2% | -4.285 / 99.2% |
| drift_at n=10 / 240 | -6.842 / 14.2% ✗ | -6.842 / 14.2% ✗ | -7.045 / 19.2% ✗ | -4.772 / 22.1% ✗ | -4.295 / 98.8% | -4.311 / 97.5% |
| two-draws: `coin_from_key` | -6.757 / 18.3% ✗ | -6.757 / 18.3% ✗ | -4.672 / 90.8% | -4.703 / 15.4% ✗ | -4.285 / 99.6% | -4.285 / 99.6% |
| runs r=16 supp=1.0 | -6.726 / 23.3% ✗ | **-4.303 / 100.0%** | -6.487 / 37.1% ✗ | -6.975 / 11.2% ✗ | -4.303 / 100.0% | -4.303 / 100.0% |
| runs r=32 supp=1.0 | -7.056 / 19.2% ✗ | **-4.303 / 100.0%** | -7.054 / 19.2% ✗ | -5.955 / 56.2% ✗ | -4.303 / 100.0% | -4.303 / 100.0% |

**L = 400**

| construction | `repo_ms3` | `exact_auto` | `pair_ms8` | `drift_l0` | `drift_l8` | `drift_l12` |
|---|---|---|---|---|---|---|
| skip_by_two supp=0.5 | -6.066 / 44.2% ✗ | -6.066 / 44.2% ✗ | -4.332 / 100.0% | -4.819 / 12.8% ✗ | -4.332 / 100.0% | -4.332 / 100.0% |
| skip_by_two supp=0.83 | -7.041 / 16.0% ✗ | -7.041 / 16.0% ✗ | -4.332 / 100.0% | -4.789 / 10.5% ✗ | -4.332 / 99.8% | -4.332 / 99.8% |
| skip_by_two supp=1.0 | -7.052 / 16.2% ✗ | -7.052 / 16.2% ✗ | -4.332 / 100.0% | -4.723 / 10.8% ✗ | -4.332 / 100.0% | -4.332 / 100.0% |
| free_drift q=0.05 | -6.975 / 13.8% ✗ | -6.975 / 13.8% ✗ | -6.596 / 37.2% ✗ | -4.707 / 21.8% ✗ | -4.319 / 98.2% | -4.358 / 97.2% |
| free_drift q=0.10 | -7.203 / 7.5% ✗ | -7.203 / 7.5% ✗ | -7.233 / 10.5% ✗ | -4.690 / 30.0% ✗ | -4.286 / 96.2% | -4.442 / 94.8% |
| drift_at n=5 / 240 (= 8) | -6.765 / 23.5% ✗ | -6.765 / 23.5% ✗ | -6.977 / 18.0% ✗ | -4.787 / 26.8% ✗ | -4.321 / 99.5% | -4.321 / 99.5% |
| drift_at n=10 / 240 (= 17) | -7.092 / 14.5% ✗ | -7.092 / 14.5% ✗ | -7.141 / 14.0% ✗ | -4.865 / 26.0% ✗ | -4.318 / 98.5% | -4.318 / 99.2% |
| two-draws: `coin_from_key` | -6.944 / 12.8% ✗ | -6.944 / 12.8% ✗ | -5.226 / 71.8% ✗ | -4.775 / 11.0% ✗ | -4.332 / 100.0% | -4.332 / 100.0% |
| runs r=16 supp=1.0 | -7.011 / 16.5% ✗ | **-4.332 / 100.0%** | -6.115 / 50.0% ✗ | -7.220 / 6.8% ✗ | -4.332 / 100.0% | -4.332 / 100.0% |
| runs r=32 supp=1.0 | -7.081 / 18.0% ✗ | **-4.332 / 100.0%** | -7.081 / 18.0% ✗ | -5.768 / 56.2% ✗ | -4.332 / 100.0% | -4.332 / 100.0% |

`drift_at n` is scaled with L so the RATE stays "n per 240 runes" (n = 8 and 17 at L = 400).
Non-gate rows measured for continuity with L7-B are in `out_fix.json`; the notable one is
`free_drift q=0.02`, which the repo decoder already half-loses at L = 400 (-6.072 / 53.5 %)
and which the permissive mode recovers at -4.328 / 99.8 %.

### 4.1 Which configurations pass all 20 cells

| mode | L = 240 | L = 400 | all 20 |
|---|---|---|---|
| `repo_ms3` (the current instrument) | 0/10 | 0/10 | FAIL |
| `exact_ms8` | 0/10 | 0/10 | FAIL |
| `exact_auto` | 2/10 | 2/10 | FAIL |
| `pair_ms8` | 4/10 | 3/10 | FAIL |
| `drift_l0` | 0/10 | 0/10 | FAIL |
| `drift_l2` | 10/10 | 9/10 | FAIL |
| `drift_l4` | 10/10 | 10/10 | **PASS** |
| `drift_l6` | 10/10 | 10/10 | **PASS** |
| **`drift_l8`** | 10/10 | 10/10 | **PASS** |
| **`drift_l12` (= `drift_rec`)** | 10/10 | 10/10 | **PASS** |
| `drift_l16` | 10/10 | 9/10 | FAIL |
| `drift_l24` | 9/10 | 9/10 | FAIL |
| `drift_mf1` | 10/10 | 10/10 | **PASS** |
| `drift_mf3` | 10/10 | 10/10 | **PASS** |

The G-FIX window in `lam` is **[4, 12]**, and both ends are real: at `lam` = 2 and 16 the single
cell that breaks is `free_drift q = 0.10` at L = 400 (too cheap, and the beam wanders; too dear,
and it will not pay for a genuine drift event). `max_free` = 1, 2 and 3 all pass.

### 4.2 A correction to L7-B, in the repo's favour

L7-B §B.4 concluded that on a low-entropy pad "`ms=8` covers constant runs up to length 8" and
that r = 16 and r = 32 at `supp` = 1.0 are missed. **That is a budget failure, not a relation
failure.** With `max_skip` raised to cross the run — which the histogram break makes free on a
high-entropy pad — the *unchanged* `keyskip1` relation recovers both at **100.0 % / -4.303**
(`exact_auto`, above). Inside a constant run every skipped position is doublet-consistent by
construction, so the repo's own transition relation always could represent them; `max_skip = 8`
simply could not reach across a run of 16. This costs **nothing**: `exact_auto` has the same
wrong-key null as `repo_ms3` (§5). It is a free strict improvement for Phase 2, independent of
everything else in this lane.

---

## 5. G-FP — what permissiveness does to the wrong-key null

`out_fp_deep.json`, `out_fp_deep2.json`, `out_fp_curve.json`, `out_fp_tail.json`.
Wrong keys are `sha256_ctr(seed=WRONGKEY-%08d)`. Two nulls, L = 240, beam 400:

- **N-synth** — against a synthetic `encipher_keyskip(supp=0.83)` plant;
- **N-real** — against random 240-rune segments of the **real 12,956-rune LP2 stream**
  (`round11/lib_numchannel.unsolved()`). This is the null Phase 2 actually faces.

They agree to within 0.01 everywhere, which is itself worth recording: the synthetic plant is a
faithful stand-in for the real ciphertext as far as this statistic is concerned.

### 5.1 The tradeoff curve (the deliverable)

`lam` sweep at `max_free = 2`; correct-key score is the median over the ten gate constructions
at L = 240. n = 2000 where marked, else 500.

| `lam` | n | wrong-key mean (synth / real) | p99 | max | **frac >= -5.5** | correct key | G-FIX |
|---:|---:|---|---|---|---|---|---|
| 0 | 500 | -4.882 / -4.878 | -4.585 | -4.563 | **1.0000** | -4.70 (but 13-51 % recovery) | FAIL |
| 2 | 500 | -5.221 / -5.217 | -4.845 | -4.810 | **0.9140** | -4.29 | FAIL |
| 4 | **2000** | -5.728 / -5.731 | -5.279 | -5.094 | **0.1125** | -4.29 | PASS |
| 6 | **2000** | -6.120 / -6.128 | -5.680 | -5.434 | 0.0005 | -4.29 | PASS |
| **8** | **2000** | -6.394 / -6.404 | -5.934 | -5.667 | **0.0000** | -4.29 | **PASS** |
| **12** | **2000** | -6.729 / -6.731 | -6.277 | -6.072 | **0.0000** | -4.30 | **PASS** |
| 16 | **2000** | -6.905 / -6.896 | -6.481 | -6.281 | 0.0000 | -4.33 | FAIL |
| 24 | 500 | -7.075 / -7.076 | -6.692 | -6.565 | 0.0000 | -4.34 | FAIL |
| — `keyskip1` (repo) | **2000** | -7.314 / -7.306 | -6.926 | -6.721 | 0.0000 | **misses entirely** | FAIL |
| — `keyskip2` | **2000** | -7.318 / -7.309 | -6.930 | -6.781 | 0.0000 | passes 7/20 | FAIL |
| — `exact_auto`/`exact_ms8` | 500 | -7.309 / -7.302 | -6.871 | -6.821 | 0.0000 | passes 4/20 | FAIL |
| `max_free`=1, `lam`=8 | 500 | -6.443 / -6.448 | -6.045 | -5.715 | 0.0000 | -4.29 | PASS |
| `max_free`=3, `lam`=8 | 500 | -6.407 / -6.403 | -5.988 | -5.862 | 0.0000 | -4.29 | PASS |

**The two windows and where they overlap.**

```
   lam:      0     2     4     6     8    12    16    24
   G-FIX:    ✗     ✗     ✓     ✓     ✓     ✓     ✗     ✗     <- correct key recovered
   G-FP:     ✗✗    ✗✗    ✗     ~     ✓     ✓     ✓     ✓     <- wrong keys stay under -5.5
   JOINT:                            ####  ####               <- lam = 8 .. 12
```

`lam` = 6 is marginal (1 of 2000 wrong keys at -5.434). `lam` = 4 is a **G-FP FAIL**: 225 of
2000 wrong keys clear -5.5, so a sweep in that configuration would produce false positives at
roughly one in nine decodes. **The joint window is `lam` in [8, 12].**

### 5.2 The shift, and why the -5.5 floor stops being a bar

`benchmark/null.py` warns that for this statistic the bulk sd understates the tail by ~2.5x, so
the Gumbel scale must be fitted from order statistics. Done here by block maxima at two block
sizes inside each sample (`analyse_fp.py`); full table in `out_fp_tail.json`. N-real rows:

| mode | mu | beta | observed max (n = 2000) | family-wise bar at 10^6 | at 10^9 |
|---|---|---|---|---|---|
| `repo_ms3` | **-7.247** | **0.0665** | -6.648 | -6.021 | **-5.562** |
| `exact_ms8` | -7.241 | 0.0585 | -6.863 | -6.163 | -5.759 |
| `pair_ms8` | -7.203 | 0.0513 | -6.852 | -6.259 | -5.904 |
| `drift_l4` | -5.621 | 0.0655 | -5.138 | -4.415 | -3.963 |
| `drift_l6` | -5.993 | 0.0655 | -5.539 | -4.786 | -4.333 |
| `drift_l8` | -6.306 | 0.0722 | -5.656 | -4.975 | -4.476 |
| **`drift_l12`** | **-6.602** | **0.0648** | **-6.182** | **-5.409** | **-4.961** |
| `drift_l16` | -6.786 | 0.0638 | -6.295 | -5.612 | -5.171 |
| `drift_mf1` (n=500) | -6.389 | 0.0831 | -5.820 | -4.860 | -4.286 |
| `drift_mf3` (n=500) | -6.293 | 0.0634 | -5.901 | -5.126 | -4.688 |

**Sanity check on the method.** The fit for `repo_ms3` gives mu = -7.247, beta = 0.0665 against
`benchmark/null.py`'s independently derived `DEFAULT_MU = -7.2517`, `DEFAULT_BETA = 0.0725`.
Those constants were fitted from two real sweep order statistics (round13/B04) and this lane
recovers them from a fresh 2,000-key null. The block-maxima method is sound and the repo's
historical bar is confirmed.

**The consequence Phase 2 must act on.** The -5.5 floor sits just above `repo_ms3`'s 10^9 bar
(-5.562), which is why it has worked. Under `drift_l12` the 10^9 bar is **-4.961** and under
`drift_l8` it is **-4.476**. A correct key in `drift_l12` scores -4.29 to -4.44 at L = 240, so
it clears its own bar by **0.52 to 0.68** at a billion decodes — a real but narrow margin.
Under `drift_l8` the same margin is only **0.14 to 0.19**, i.e. effectively gone. **That is why
the recommendation below is `lam` = 12 and not `lam` = 8, even though both pass every gate.**
Margin grows quickly with L: at the full book the permissive wrong key sits at -6.615 against a
correct key at -4.32.

### 5.3 A second, English-independent channel that partly pays the bill

`driftbeam` returns `n_skips`, the number of keystream draws the winning path claims the
rejection sampler consumed. Under a correct key that must track `rho*L`; under a wrong key it
has no reason to, and under a *permissive* decoder a wrong key inflates it badly because
buying English costs draws:

| mode | wrong key, mean inferred skips (L = 240) | correct key, full book |
|---|---|---|
| `repo_ms3` | 5.0 | 418 / 418 exact |
| `drift_l12` | 19.5 | (not run at full book) |
| `drift_l8` | 32.5 | **418 / 418 exact**, wrong key **1537** |
| `drift_l4` | 73.6 | — |
| `drift_l0` | 253.2 | — |

At full-book length this is close to a clean separator on its own (exact vs 3.7x). At L = 240 it
is weaker (correct-key median 16 inferred against a true 8, wrong-key mean 32.5) but still
informative. **Phase 2 should store `n_skips` and `n_unexplained` in every `SWEEPROW`**; they
cost nothing and they are language-agnostic, which doctrine R3 requires and which no sweep in
this repository has ever had.

---

## 6. G-COST — the price, as numbers

| what | number |
|---|---|
| score lost on the baseline `encipher_keyskip` construction, `drift_l8` and `drift_l12` vs `repo_ms3`, worst of 8 cells | **0.000** (best cell: **+0.018** in the permissive decoder's favour) |
| rune recovery lost on the same cells | **0.0 pp** (100.0 % in every cell, both modes) |
| full-book (L = 12,956) correct-key score, `drift_l8` vs `repo_ms3` | **-4.318 vs -4.322** (+0.004) |
| **wrong-key null shift**, `drift_l12` vs `repo_ms3`, mean | **+0.575** (-6.731 vs -7.306) |
| **wrong-key p99 shift**, `drift_l12` | **+0.659** (-6.277 vs -6.936) |
| **family-wise bar shift at 10^9 decodes** | **+0.601** (-4.961 vs -5.562) |
| separation (correct key - wrong-key p99) at L = 240 | **1.98** vs **2.63** — a loss of **0.65** |
| decode time, L = 240, single process | 0.13 s -> **1.14 s** (8.8x) |
| decode time, L = 400 | 0.43 s -> **2.10 s** (4.9x) |
| decode time, L = 12,956 | 42 s -> **110 s** (2.6x) |
| `exact_auto` (the free part of the fix) | **0.00** shift, ~1.5x time |

**So the honest statement of the price is: the permissive decoder costs nothing in power on the
construction the old one handled, and costs 0.6 of separation plus 3-9x compute everywhere.**
0.6 of separation is not nothing — it is a quarter of the total 2.6 the instrument had — but it
buys recovery of a class that was previously at **-6.9 / 25 %**, i.e. a power of 0.00.

### 6.1 Speed — the fastbeam property is preserved

`fastbeam` (round18/L2) decodes L = 12,956 in **34.3 s** on this box, where L2 reported 7.6 s on
its own; the box is ~4.5x slower, and all absolute timings here should be read against that.
Single-process, unloaded:

| decoder | L = 12,956 | relative to `fastbeam` |
|---|---|---|
| `round18/L2 fastbeam` | 34.3 s | 1.00x |
| `driftbeam` `keyskip1` (`repo_ms3`) | **29.9 s** | **0.87x** |
| `driftbeam` `permissive` (`drift_l8`) | 87 s | 2.5x |

The last-3-chars + back-pointer structure is intact and the early break makes exact mode
slightly *faster* than the reimplementation it is derived from. On L2's hardware the exact mode
would be ~6.5 s, i.e. the "single-digit seconds at full book" property is preserved; permissive
mode would be ~20-25 s.

---

## 7. Where the permissive relation stops — measured, not asserted

`out_bound.json`. A single key-pointer **jump** of J positions at one rune (a page break, a
reset, a block of discarded draws) is a different object from J drift events spread one per
rune: `max_free` bounds the *per-rune* count. 7 seeds, L = 240, supp = 0.83.

| jump J at one rune | `repo_ms3` | `drift_rec` (mf=2, lam=12) | mf=6 | mf=10 |
|---|---|---|---|---|
| 1 | -4.599 / 95.0% | -4.285 / 100.0% | -4.285 / 100.0% | -4.285 / 100.0% |
| 2 | -4.689 / 89.6% ✗ | -4.313 / 100.0% | -4.313 / 100.0% | -4.313 / 100.0% |
| 3 | -5.435 / 71.2% ✗ | -4.334 / 99.2% | -4.285 / 100.0% | -4.285 / 100.0% |
| **5** | -5.940 / 51.7% ✗ | **-4.354 / 96.7%** | -4.354 / 97.9% | -4.354 / 97.9% |
| **8** | -5.848 / 51.7% ✗ | **-4.623 / 84.2% ✗** | -4.623 / 84.2% ✗ | -4.623 / 84.2% ✗ |
| 12 | -5.951 / 51.2% ✗ | -5.250 / 62.5% ✗ | -5.250 / 62.5% ✗ | -5.250 / 62.5% ✗ |

**The bound is J <= 5, and raising `max_free` does not move it.** Above J ~ 5 the binding
constraint stops being the transition relation and becomes the beam: a hypothesis that pays
`J * lam` at one step falls out of a 400-wide beam before it can earn the penalty back. The
right instrument for a large jump is not a wider transition relation but a **global offset
search** — exactly `round18/L2-filter-leak`'s drift-corrected offset ladder (B.4). That is the
concrete condition that reopens this bound.

Note the repo decoder already fails at **J = 2**.

---

## 8. Coverage x power, and the three conditionals

Doctrine R2 and R7. This lane produced no key-space negative, so what it publishes is a **power
envelope**, which is the other half of every negative Phase 2 will write.

**Measured power of `drift_rec` (permissive, `max_free` = 2, `lam` = 12, `max_skip` = auto,
`start_slack` = 2), correct key, English plaintext, L = 240 and 400, beam 400:**

| construction class | power (frac of seeds over score >= -5.5 AND recovery >= 0.90) |
|---|---|
| `encipher_keyskip`, all `supp` in [0, 1] | **1.00** |
| `skip_by_two` / two-draws-per-rejection, all `supp` | **1.00** |
| independent two-draws variant (`coin_from_key`) | **1.00** |
| free drift q <= 0.10 (~1 unrepresentable advance per 10 runes) | **1.00** |
| n <= 10 unrepresentable advances per 240 runes, spread | **1.00** |
| low-entropy pad, constant runs r <= 32, `supp` = 1.0 | **1.00** |
| single key-pointer jump J <= 5 at one rune | **1.00** |
| single key-pointer jump J >= 8 | **0.00** |
| **wrong key (2,000 per null, two nulls)** | **0/4000 above -5.5** |

**The three conditionals every Phase-2 negative decoded with this instrument must carry:**

1. **Key space** — whatever the lane swept. Nothing here.
2. **Decoder transition model** — "any key advance of at most `max_skip` positions per rune, of
   which at most **2** are not doublet-consistent". **Not covered:** an advance greater than
   `max_skip` at one rune; more than 2 unexplained advances at a *single* rune (measured bound
   J <= 5 with spillover, J >= 8 lost); a key pointer that **retreats** — the beam can insert
   draws, never remove them, so it can never reach an offset below the one it started at; a
   non-monotone pointer; a keystream whose *values* depend on the plaintext.
3. **Adjudicator register** — **English quadgram only**. I1 pinned the register axis at English
   deliberately, so every loss it measured is the decoder's. **Nothing in this document extends
   to a non-English plaintext**; that is I2's lane, and L7-A's finding (power 0.33 Latin, 0.00
   vowel-dropped English) stands untouched by anything here.

---

## 9. RECOMMENDATION TO PHASE 2

**1. Replace the baseline decoder unconditionally, at zero cost.**
Everywhere the repo currently calls `skipdecode.beam_decode(..., max_skip=3)`, call
`driftbeam.beam_decode(mode="keyskip1", max_skip=run_gates.suggest_max_skip(K, L))`.
It is bit-identical on high-entropy pads (G-EQ), it is *faster*, it has **exactly the same
wrong-key null** so the historical bar and every published number stay comparable, and it
recovers the constant-key-run cases the ledger currently lists as missed. There is no argument
against this one.

**2. Sweep the drift channel at `lam` = 12, `max_free` = 2, `start_slack` = 2,
`max_skip` = `suggest_max_skip(K, L)` — the `drift_rec` preset.**
It passes all 20 G-FIX cells, costs 0.000 score and 0.0 pp recovery on the baseline
construction, and holds 0/2000 wrong keys under -5.5 on both nulls with the observed maximum at
-6.07. `lam` = 8 also passes every gate but leaves only 0.14-0.19 of margin over its own 10^9
family-wise bar; `lam` = 12 leaves 0.52-0.68. **Do not sweep at `lam` <= 6, and never at
`lam` = 0** — at `lam` = 0 every wrong key scores -4.88 and the decoder is an English generator
with 13-51 % rune recovery.

**3. Adjudicate each channel against its OWN bar. This is the part that will be got wrong.**
The -5.5 floor belongs to `keyskip1`. Use `benchmark/null.threshold_for(n, mu=..., beta=...)`
with the per-mode constants in `out_fp_tail.json`:

| channel | mu | beta | bar at 10^6 | bar at 10^9 |
|---|---|---|---|---|
| `exact_auto` (keyskip1) | -7.247 | 0.0665 | -6.02 | -5.56 (the familiar -5.5) |
| **`drift_rec`** | **-6.602** | **0.0648** | **-5.41** | **-4.96** |

These are calibrated at **L = 240**. Re-run `run_fp.py` at the segment length actually swept
before trusting them at another L; the null moves with length (at L = 12,956 the permissive
wrong key sits at -6.615, far below its L=240 value in usable terms).

**4. Store the full row.** Per doctrine R3, and because this lane's own results depend on it:
`score_exact`, `score_drift`, `n_skips`, `n_unexplained`, plus I2's four language-agnostic
statistics. `n_skips` is a genuinely independent channel — a wrong key under `drift_l12` infers
19.5 skips against a true ~8, and at full book 1537 against 418.

**5. Budget.** The drift channel costs 3-9x per decode. If the budget forces one channel,
sweep `drift_rec` alone — it covers `keyskip1` at zero loss of power — and pay the 0.6 of bar.
If the space is small enough to run both (G1 `$RANDOM` and G4 the TeX LCGs are *enumerable*),
run both and report each against its own bar: two channels with different nulls is strictly more
information than one.

**6. What this does not fix.** The register axis. A Latin, Welsh or vowel-dropped plaintext is
still invisible (L7-A), and a repaired decoder handing a perfectly recovered Latin plaintext to
an English quadgram scorer still produces a null. **I1 and I2 are both required before Phase 2
means anything; neither is sufficient.**

---

## 10. Files

| file | what |
|---|---|
| `driftbeam.py` | the decoder. `beam_decode(..., mode, max_free, lam, start_slack)`, `PRESETS`, `gate_EQ`, `gate_EQ_fast` |
| `constructions.py` | every L7-B encipherment verbatim, plus `coin_from_key` and `jump_at` |
| `run_gates.py` | G-BASE / G-FIX / G-COST / bound grids, `MODES`, `suggest_max_skip` |
| `run_fp.py` | the wrong-key nulls |
| `analyse_fp.py` | block-maxima extreme-value fit per mode |
| `mktables.py` | emits this document's tables straight from the JSON |
| `test_driftbeam.py` | 15 tests, including G-EQ and the histogram identity |
| `out_eq.json` `out_base.json` `out_book.json` `out_fix.json` `out_fix2.json` `out_bound.json` | correct-key measurements |
| `out_fp_deep.json` `out_fp_deep2.json` `out_fp_curve.json` `out_fp_tail.json` | wrong-key null, 34,000 decodes |
| `ledger.json` | ledger fragment for `liber-primus/LEDGER.json` |
| `fix.log` `fix2.log` `base.log` `book.log` `fp_*.log` | run logs |

Total decodes in this lane: 2,100 (G-FIX) + 630 (extra `lam`) + 336 (G-BASE) + 8 (full book) +
168 (bound) + 34,000 (G-FP) = **37,242**.
