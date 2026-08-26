# I2 — MULTI-REGISTER ADJUDICATOR — results

_Round 19, Phase 0 (blocking). Pre-registered in [`PREREG.md`](PREREG.md) **before any
measurement**; no threshold was edited afterwards. Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

| gate | verdict | measured |
|---|---|---|
| **G-POWER** | **PASSED** | panel power ≥ 0.90 in **27 of 27** cells; minimum **0.92** (`EN_NOVOWEL`, L=120); 1.00 in the other 26 |
| **G-FP** | **PASSED** | at matched per-decode FP the panel's power is ≥ the single scorer's in **every** cell; **0** regressions. Null inflation measured, not assumed: **k_eff = 6.3 / 9.5 / 8.0** at L = 120 / 240 / 400 |
| **G-LP1** | **PASSED** | `LP1_REAL` legacy `score_norm` **−4.35 / −4.27 / −4.21** at L = 120/240/400, 24/24 replicates over −5.5, on **leave-one-page-out** models |
| **G-SPEED** | **FAILED** | **4.79×** `score_norm` at L=240 (limit 3.00×). 164 µs/decode. See §6 — the gate is met in absolute terms and fails only against a baseline that turns out to be 0.1 % of the pipeline it gates |

**Headline.** Handed the correct key, `LATIN` scored **−5.44** under the old English quadgram
adjudicator — *below* the −5.5 bar, measured power **0.33** (L7-A). Under this panel the same
plants score **`pmax` = 25.5** against a matched-FP bar of **4.67**, at power **1.00**. The
same holds for Old English, German, Welsh and half-vowel English. `EN_NOVOWEL`, which the old
scorer **anti-selected** — the correct key scoring *below* a deliberately wrong one — now
scores `pmax` 12.1 → 20.0 at power 0.92 → 1.00.

> **For lane I3:** the effective independent-test count of the 9-register panel max is
> **k_eff ≈ 6–10** (§4.2), *not* 9, and the wrong-key **beam** null is measurably higher than a
> random-rune null (§4.1) — calibrate on beam decodes, not random runes. Full empirical null
> distributions are in [`out_null.json`](out_null.json).

---

## 0. Trust anchor

```
BEFORE  python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5 known solves)
        python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
AFTER   python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5 known solves)
        python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
        python3 -m pytest analysis/round19/I2/test_adjudicate.py -q -> 16 passed
```

`lp.score.Quadgram.score_norm` is **untouched**. The panel is additive: every row still carries
the legacy English score as `en`, so every Phase 2 number stays directly comparable with every
published number in this repository.

---

## 1. What was built

| file | what |
|---|---|
| [`adjudicate.py`](adjudicate.py) | **`adjudicate(plain_idx, translit=None) -> dict`** — the single call every Phase 2 lane makes. Plus `adjudicate_batch`, `to_row`, `to_record`, `header`, `validate_row`, `validate_store` |
| [`SWEEPROW.md`](SWEEPROW.md) | the `SWEEPROW/1` record schema + store layout + validator contract |
| [`build_models.py`](build_models.py) | builds and SHA-256-hashes the 9-register panel and its null calibration into `models/` (gitignored, rebuildable) |
| [`power.py`](power.py) | G-POWER / G-FP measurement (L7-A's protocol, held-out plants) |
| [`speed.py`](speed.py), [`gates.py`](gates.py), [`make_ledger.py`](make_ledger.py) | G-SPEED, gate adjudication, ledger generation |
| [`test_adjudicate.py`](test_adjudicate.py) | 16 tests incl. plant-and-recover controls and fast-path/reference equivalence |

### 1.1 The register panel

Nine interpolated **rune-index** trigram models (Jelinek–Mercer, λ = 0.70/0.20/0.09/0.01, fixed
a priori in PREREG §2.1 and never re-chosen), scored on rune indices and never on the
transliteration string (doctrine §4 r5). Corpora are **literally L7-A's corpora**, loaded by
L7-A's own `detectors.text_to_runes`, so the two lanes' numbers are comparable; every file is
SHA-256-hashed in [`out_build.json`](out_build.json).

| register | train runes | held-out test runes |
|---|---:|---:|
| `EN_MODERN` (self_reliance + mabinogion-EN) | 175,828 | 175,829 |
| `EN_KJV` | 314,705 | 314,706 |
| `LP1_REAL` (the 5 solved pages, own lossy orthography) | 1,769 | leave-one-page-out |
| `LATIN` | 288,365 | 288,366 |
| `OE` | 121,379 | 121,380 |
| `DE` | 104,065 | 104,065 |
| `CY` | 148,574 | 148,575 |
| `EN_HALFVOWEL` | 140,270 | 140,271 |
| `EN_NOVOWEL` | 104,236 | 104,237 |

**Held-out discipline.** The first half of every corpus trains; **every plant window comes from
the second half**. `LP1_REAL` cannot be halved at 1,769 runes, so its LM is
`0.5 × trigram(solved pages) + 0.5 × trigram(EN_KJV train)` mixed in probability space, and its
power is measured **leave-one-page-out**: the LP1 component is rebuilt without page *i* and the
plant is drawn from page *i*. Pages are 184/157/733/383/312 runes, so L=120 uses all 5 folds,
L=240 uses 3, and **L=400 uses only page 3** — 24 replicates from 333 possible window starts,
i.e. overlapping and correlated. That is a real limitation of the LP1 cell at L=400 and it is
stated rather than papered over.

### 1.2 The four language-agnostic statistics (doctrine R3)

`ioc` (decrypt IoC·N), `mds` (min distinct symbols over a sliding 32-rune window), `pmax_ne`
(best non-English panel z), and compressibility as **both** `h2` (plug-in order-2 conditional
entropy, bits/rune) and `zl` (zlib-9 ratio). All four are persisted in every row — see §5 for
how well each actually separates.

---

## 2. G-POWER — **PASSED**

Protocol is L7-A's, unchanged: plant `sha256_ctr(seed=CICADA3301)` → `encipher_keyskip(supp=0.83)`
→ `beam_decode(beam_w=400, max_skip=3)` with the **CORRECT** key → adjudicate the decode's rune
indices. **24 replicates** per cell (twice the required 12, so 0.90 needs ≥ 22/24), plants from
held-out text. The bar is the matched-FP `t_pmax` from §4, *not* an arbitrary z.

| register | L | legacy `en` (L7-A) | legacy power | **panel `pmax`** | **panel power** | `pcon` | `pcon` power | own-model z | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `EN_MODERN` | 120 | -4.32 _(L7-A -4.22)_ | 1.00 _(L7-A 1.00)_ | **19.2** | **1.00** | 11.4 | 1.00 | 17.4 | 100% |
| `EN_MODERN` | 240 | -4.27 _(L7-A -4.22)_ | 1.00 _(L7-A 1.00)_ | **27.1** | **1.00** | 16.2 | 1.00 | 24.6 | 100% |
| `EN_MODERN` | 400 | -4.29 _(L7-A -4.22)_ | 1.00 _(L7-A 1.00)_ | **35.6** | **1.00** | 21.2 | 1.00 | 32.0 | 100% |
| `EN_KJV` | 120 | -3.99 _(L7-A -4.11)_ | 1.00 _(L7-A 1.00)_ | **21.0** | **1.00** | 13.8 | 1.00 | 18.8 | 100% |
| `EN_KJV` | 240 | -4.06 _(L7-A -4.11)_ | 1.00 _(L7-A 1.00)_ | **28.9** | **1.00** | 18.9 | 1.00 | 26.0 | 100% |
| `EN_KJV` | 400 | -4.03 _(L7-A -4.11)_ | 1.00 _(L7-A 1.00)_ | **38.5** | **1.00** | 24.7 | 1.00 | 33.8 | 100% |
| `LP1_REAL` | 120 | -4.35 _(L7-A -4.33)_ | 1.00 _(L7-A 1.00)_ | **18.2** | **1.00** | 11.1 | 1.00 | 18.2 | 100% |
| `LP1_REAL` | 240 | -4.27 _(L7-A -4.33)_ | 1.00 _(L7-A 1.00)_ | **29.4** | **1.00** | 19.5 | 1.00 | 29.4 | 100% |
| `LP1_REAL` | 400 | -4.21 _(L7-A -4.33)_ | 1.00 _(L7-A 1.00)_ | **36.1** | **1.00** | 23.3 | 1.00 | 36.1 | 100% |
| **`LATIN`** | 120 | -5.33 _(L7-A -5.58)_ | 0.67 _(L7-A 0.33)_ | **18.0** | **1.00** | 14.2 | 1.00 | 18.0 | 100% |
| **`LATIN`** | 240 | -5.44 _(L7-A -5.58)_ | 0.62 _(L7-A 0.33)_ | **25.5** | **1.00** | 20.3 | 1.00 | 25.5 | 100% |
| **`LATIN`** | 400 | -5.50 _(L7-A -5.58)_ | 0.50 _(L7-A 0.33)_ | **31.9** | **1.00** | 25.8 | 1.00 | 31.9 | 100% |
| `OE` | 120 | -5.20 _(L7-A -5.39)_ | 0.71 _(L7-A 0.58)_ | **13.6** | **1.00** | 8.2 | 1.00 | 13.5 | 100% |
| `OE` | 240 | -5.39 _(L7-A -5.39)_ | 0.67 _(L7-A 0.58)_ | **19.8** | **1.00** | 12.6 | 1.00 | 19.8 | 100% |
| `OE` | 400 | -5.32 _(L7-A -5.39)_ | 0.83 _(L7-A 0.58)_ | **25.4** | **1.00** | 16.1 | 1.00 | 25.4 | 100% |
| `DE` | 120 | -5.45 _(L7-A -5.52)_ | 0.67 _(L7-A 0.42)_ | **20.2** | **1.00** | 16.4 | 1.00 | 20.2 | 100% |
| `DE` | 240 | -5.46 _(L7-A -5.52)_ | 0.67 _(L7-A 0.42)_ | **29.0** | **1.00** | 23.6 | 1.00 | 29.0 | 100% |
| `DE` | 400 | -5.46 _(L7-A -5.52)_ | 0.58 _(L7-A 0.42)_ | **36.9** | **1.00** | 30.0 | 1.00 | 36.9 | 100% |
| **`CY`** | 120 | -6.37 _(L7-A -6.58)_ | 0.00 _(L7-A 0.00)_ | **13.4** | **1.00** | 9.7 | 1.00 | 13.4 | 100% |
| **`CY`** | 240 | -6.32 _(L7-A -6.58)_ | 0.00 _(L7-A 0.00)_ | **19.0** | **1.00** | 13.8 | 1.00 | 19.0 | 100% |
| **`CY`** | 400 | -6.28 _(L7-A -6.58)_ | 0.04 _(L7-A 0.00)_ | **24.2** | **1.00** | 18.2 | 1.00 | 24.2 | 100% |
| `EN_HALFVOWEL` | 120 | -5.59 _(L7-A -5.62)_ | 0.38 _(L7-A 0.33)_ | **13.1** | **1.00** | 7.0 | 1.00 | 13.1 | 100% |
| `EN_HALFVOWEL` | 240 | -5.67 _(L7-A -5.62)_ | 0.33 _(L7-A 0.33)_ | **19.5** | **1.00** | 10.5 | 1.00 | 19.1 | 100% |
| `EN_HALFVOWEL` | 400 | -5.57 _(L7-A -5.62)_ | 0.33 _(L7-A 0.33)_ | **24.6** | **1.00** | 12.6 | 1.00 | 24.4 | 100% |
| **`EN_NOVOWEL`** | 120 | -7.64 _(L7-A -7.60)_ | 0.00 _(L7-A 0.00)_ | **12.1** | **0.92** | 11.8 | 0.92 | 12.1 | 80% |
| **`EN_NOVOWEL`** | 240 | -7.61 _(L7-A -7.60)_ | 0.00 _(L7-A 0.00)_ | **18.5** | **1.00** | 17.8 | 1.00 | 18.5 | 81% |
| **`EN_NOVOWEL`** | 400 | -7.55 _(L7-A -7.60)_ | 0.00 _(L7-A 0.00)_ | **20.0** | **1.00** | 19.4 | 0.96 | 20.0 | 67% |

Raw per-replicate rows in [`out_power.json`](out_power.json); adjudication in
[`out_gates.json`](out_gates.json).

### 2.1 The legacy column reproduces L7-A, and that matters

The `en` column is L7-A's measurement re-run on **different (held-out) windows** with 24 rather
than 12 replicates. It lands within 0.05–0.25 of L7-A everywhere and reproduces the same
qualitative picture: modern/archaic/LP1 English at −4.0 to −4.4 and power 1.00; Latin, OE, DE
and half-vowel English straddling the −5.5 bar at power 0.33–0.83; Welsh at 0.00–0.04; and
vowel-dropped English at **0.00**. The defect is real, it is reproducible, and it is not an
artifact of L7-A's particular text windows.

### 2.2 EN_NOVOWEL — the declared hard case, and what is and is not recovered

PREREG named this the register that might not be reachable, with a kill condition at z ≥ +3.0.
The measured value at the smoke checkpoint was **z = 19.96** ([`out_smoke.json`](out_smoke.json)),
so the lane proceeded.

**What is recovered:** the register is now *visible*. Against the matched-FP bar the panel
reaches **0.92** at L=120 and **1.00** at L=240 and L=400. It is no longer anti-selected: under
the old scorer the correct key scored −7.61 against a wrong key's ≈ −7.31, i.e. **worse than
wrong**; under the panel the correct key scores `pmax` 18.5 against a wrong-key null whose
99.9th percentile is 4.67.

**What is *not* recovered:** the runes themselves. Rune recovery for `EN_NOVOWEL` is **80 % at
L=120, 81 % at L=240 and 67 % at L=400** — the only register in the panel where the beam does
not recover ~100 %. The adjudicator now sees the register through a decode that is one third
wrong at L=400, and it still fires; but a Phase 2 hit in this register would arrive as a
*detection*, not a readable plaintext. Recovering the text would need a decoder whose skip path
is chosen by the panel rather than by English — see §7.

`EN_NOVOWEL` is also the only cell that misses 1.00 (0.92 at L=120, 22/24). At L=120 a
vowel-dropped decode is ~120 runes of consonant clusters at 80 % accuracy; two replicates fall
under the bar. That is reported as the achieved number, not tuned away.

---

## 3. G-LP1 — **PASSED**

The register the puzzle demonstrably uses must not regress.

| L | median legacy `en` | replicates over −5.5 | panel `pmax` | panel power | held-out |
|---:|---:|---:|---:|---:|---|
| 120 | **−4.354** | 24/24 | 18.2 | 1.00 | leave-one-page-out, 5 folds |
| 240 | **−4.271** | 24/24 | 29.4 | 1.00 | leave-one-page-out, 3 folds |
| 400 | **−4.206** | 24/24 | 36.1 | 1.00 | leave-one-page-out, **1 fold** (see §1.1) |

All three clear the pre-registered −4.5 at power 1.00. `LP1_REAL` is also the panel's own
argmax register for its plants at every length, on models that never saw the page being
scored.

---

## 4. G-FP — **PASSED**, and the null inflation that I3 needs

### 4.1 The null is measured on real ciphertext, and the beam inflates it

The wrong-key null is a random L-window of the **real 12,956-rune unsolved LP2 stream** decoded
under a uniform random 29-ary key by the same beam — literally what a sweep does. 8,000 /
20,000 / 8,000 beam decodes at L = 120/240/400, plus 200,000 uniform-random-rune draws per
length as the cheap comparison null.

**They do not agree, and the difference is in the dangerous direction:**

| L | `pmax` mean, wrong-key beam | `pmax` mean, random runes | inflation | `en` mean, beam | `en` mean, random | inflation |
|---:|---:|---:|---:|---:|---:|---:|
| 120 | 1.674 | 1.163 | **+0.511** | −7.340 | −7.507 | **+0.167** |
| 240 | 2.020 | 1.170 | **+0.850** | −7.310 | −7.506 | **+0.196** |
| 400 | 2.396 | 1.166 | **+1.230** | −7.292 | −7.505 | **+0.214** |

The beam *optimises* over skip paths, so even on a wrong key it finds the most English-looking
path available — and the inflation **grows with L**, because a longer segment offers more skip
paths to optimise over. **A threshold calibrated on random runes is too low.** This is a
concrete instruction for I3: calibrate on beam decodes.

### 4.2 `k_eff` — the effective independent-test count of a 9-way panel max

Defined as the multiplier for which `P(pmax > t) ≈ k_eff · P(z_EN > t)`, measured on the
200,000-draw random-rune null (large enough to resolve the tail), with a Poisson interval on
the exceedance count:

| L | tail depth | `k_eff` | 95 % CI | exceedances |
|---:|---|---:|---|---:|
| 120 | 1e-2 | 7.27 | [6.50, 8.25] | 275 |
| 120 | **1e-3** | **6.25** | [4.64, 9.56] | 32 |
| 120 | 1e-4 | 4.00 | [2.13, 32.4] | 5 |
| 240 | 1e-2 | 7.17 | [6.42, 8.12] | 279 |
| 240 | **1e-3** | **9.52** | [6.67, 16.64] | 21 |
| 240 | 1e-4 | 10.00 | [4.19, 40.0] | 2 |
| 400 | 1e-2 | 7.49 | [6.69, 8.51] | 267 |
| 400 | **1e-3** | **8.00** | [5.75, 13.16] | 25 |
| 400 | 1e-4 | 5.00 | [2.53, 40.0] | 4 |

**The honest reading: `k_eff` ≈ 7–8 at the well-resolved 1e-2 depth, and 6–10 at 1e-3 with wide
intervals. It is not 1 and it is not 9.** The nine models are correlated — the measured null
correlation of `z_OE` with `z_EN` is ≈ 0.62 ([`out_build.json`](out_build.json) →
`null.rho_vs_EN_MODERN`) — so a naive Bonferroni ×9 is conservative but not wildly so, and a
×1 correction would be wrong by most of an order of magnitude. Deeper than 1e-4 the estimates
are Poisson noise on 2–5 events and should not be used; **I3 owns the calibrated bar**, and the
full empirical distributions of `z_EN`, `pmax`, `pmax_ne`, `pcon`, the nine-vector `z` and all
four agnostic statistics are in [`out_null.json`](out_null.json) for that purpose.

### 4.3 The gate itself

`alpha_ref = 1e-3` per decode, pre-registered. Thresholds are the more conservative of the
empirical quantile and a Generalized-Pareto tail fit (higher = harder to clear, so this can
only cost power):

| L | `t_en` | `t_pmax` | `t_pcon` | wrong-key n | FP rate of the legacy −5.5 bar |
|---:|---:|---:|---:|---:|---:|
| 120 | −6.618 | 4.277 | 3.866 | 8,000 | 0.000 |
| 240 | −6.830 | 4.671 | 4.054 | 20,000 | 0.000 |
| 400 | −6.915 | 5.226 | 4.075 | 8,000 | 0.000 |

**PASSED: zero regressions.** In all 27 cells the panel's power is ≥ the single scorer's at the
matched FP rate. The panel buys the register coverage in §2 without paying for it in false
positives.

### 4.4 Supplementary — the operating point Phase 2 will actually use

`alpha_ref = 1e-3` is where the gate is adjudicated and nowhere else. But a real sweep runs
10⁶–10⁹ decodes, so its *family-wise* bar sits near a per-decode FP of 1e-9 — which is exactly
why the repo's fixed −5.5 English bar is so much stricter than a 1e-3 bar. Extrapolating the
wrong-key tail (GPD; **an extrapolation, labelled as such**) to L=240:

| per-decode α | `t_en` | `t_pmax` | English-scorer power | panel power |
|---|---:|---:|---|---|
| 1e-6 | −6.681 | 5.878 | 1.00 except `CY` 0.92, **`EN_NOVOWEL` 0.00** | **1.00 in 8 registers, `EN_NOVOWEL` 0.96** |
| 1e-9 | −6.642 | 6.472 | 1.00 except `CY` 0.92, **`EN_NOVOWEL` 0.00** | **1.00 in 8 registers, `EN_NOVOWEL` 0.92** |

The plants sit at `pmax` 18–37 against a 1e-9 bar of 6.5, so the panel's margin is enormous and
the result is not sensitive to where exactly I3 lands the bar. This is the number that matters
operationally, and it is supplementary because the extrapolation, not the panel, is the weak
link. Full detail: [`out_gates.json`](out_gates.json) → `supplementary_far_tail`.

---

## 5. The four R3 statistics — how well each actually separates

PREREG §2.2 committed to persisting **both** `h2` and `zl` and **reporting the measured
separation of both** rather than asserting which is better. At L=240, plant medians against the
wrong-key null, in null SD (all directions oriented so that positive = more structured):

| statistic | null (wrong-key) | weakest register | strongest register | verdict |
|---|---|---:|---:|---|
| `ioc` decrypt IoC·N | 1.0074 ± 0.0329 | `EN_HALFVOWEL` **+20.5 σ** | `DE` +36.0 σ | **strongest by far** |
| `h2` order-2 cond. entropy | 0.2617 ± 0.0413 | `OE` **+10.7 σ** | `DE` +16.9 σ | strong |
| `zl` zlib-9 ratio | 0.7192 ± 0.0054 | `EN_NOVOWEL` **+10.2 σ** | `LATIN` +20.6 σ | strong, ≈ `h2` |
| `mds` min distinct / 32 | 15.78 ± 0.97 | `OE` **+3.4 σ** | `DE` +6.0 σ | weakest, but real |

**A pre-registered concern that the data did not support, reported as such.** PREREG §2.2
argued `h2` would be the primary figure and that `zl` would be near-useless at n ≈ 240 because
a 240-byte zlib stream is dominated by its ~11-byte header. Both halves of that argument turn
out to be wrong in an interesting way: `zl` separates at 10–21 σ, essentially tied with `h2`,
and the reason `h2` works at all is *not* the one PREREG gave. The plug-in estimator is indeed
severely undersampled — 238 trigrams against 29³ = 24,389 contexts — but the undersampling
biases H₃ and H₂ **unequally**, because structured text repeats bigram contexts far more than
trigram contexts, and the difference is what survives. No threshold moved; both figures are
persisted as pre-registered, and Phase 2 should treat `ioc` as the primary agnostic statistic
with `h2` and `zl` as near-equal seconds.

`mds` is the weak one at 3.4 σ, and it should be kept anyway: it is the only one of the four
that responds to a *localised* alphabet restriction rather than a global property, which is the
failure mode the other three cannot see.

---

## 6. G-SPEED — **FAILED** (4.79×, limit 3.00×)

Measured on a quiet machine (load 1.8), 5 trials per length, keeping the least-contended trial
with both halves of the ratio taken from the *same* trial. The five trial ratios at L=240 were
4.75 / 4.79 / 4.82 / 5.00 / 5.02 — a tight spread, so **4.79× is a real number, not noise**.

| L | `score_norm` | legacy pipeline (incl. translit) | **`adjudicate`** | ratio vs `score_norm` | batch, panel only | decodes/s |
|---:|---:|---:|---:|---:|---:|---:|
| 120 | 13.3 µs | 15.8 µs | **94.8 µs** | 7.11× | 4.4 µs | 10,547 |
| **240** | **34.3 µs** | 38.6 µs | **164.3 µs** | **4.79×** | 10.2 µs | 6,086 |
| 400 | 60.8 µs | 67.4 µs | **248.3 µs** | 4.09× | 16.9 µs | 4,028 |

Component breakdown at L=240: `score_norm` 34.3, `h2` 21.7, `min_distinct` 19.1, `panel_raw`
13.4, `zlib_ratio` 7.8, `idx_to_trans` 5.0, `ioc` 2.7, calibration lookup 0.1 µs.

The implementation was optimised (not the statistic — [`test_adjudicate.py`](test_adjudicate.py)
asserts the fast paths equal reference implementations exactly): one sort instead of two for
`h2` (`bi == tri // 29`, and `// 29` is monotone), an O(n) previous-occurrence + difference-array
`min_distinct`, a transposed `(29³, R)` panel so the gather is contiguous, and `.tolist()`
before the transliteration join. It was not enough.

### 6.1 The gate fails; the thing it was protecting does not

Reported as pre-registered, with no threshold moved. But the gate compares against
`score_norm` alone, and that turns out to be the wrong denominator by three orders of
magnitude:

- one `beam_decode(beam_w=400, max_skip=3)` at L=240 costs **≈ 134,300 µs** on this machine;
- `adjudicate` costs **164 µs**, i.e. **0.12 %** of the decode it adjudicates.

A 4.79× adjudicator therefore adds **≈ 0.4 %** to a sweep's wall-clock. Against the actual
budget — 10⁷ decodes is 22 minutes of adjudication on one core, or under 4 minutes on six,
beside roughly 15 days of beam decoding — the adjudicator is free. The gate as written measures
`adjudicate / score_norm`; what governs Phase 2 is `adjudicate / beam_decode`, and that is
0.0012.

**This is a mis-specified gate, not a performance problem, and I am recording it as a FAIL
rather than rewriting it.** The pre-registration is the point: a threshold that turns out to
have been aimed at the wrong quantity is exactly the kind of thing that must be visible in the
record rather than quietly adjusted. For a lane that genuinely needs the panel without the
legacy scorer, `adjudicate_batch` gives the nine-register z-vector at **10.2 µs/row**
(98,000 rows/s/core) — 0.30× `score_norm`, well inside the gate — but it does not produce a
complete `SWEEPROW`, so it is a prefilter, not a substitute.

---

## 7. The three conditionals (doctrine Q4)

Every number above carries all three, stated:

1. **Key space** — none swept. The plant uses `sha256_ctr(seed=CICADA3301)`, the B-04/D3 live
   class, exactly as L7-A did. Power is a property of the adjudicator rather than of the key,
   but **only one key family was measured** and that is the honest scope.
2. **Decoder transition model** — `encipher_keyskip(supp=0.83)` → `beam_decode(400, 3)`, held at
   the Round-18 baseline so these numbers are comparable with L7-A's. This lane therefore
   **inherits L7-B's hole**: the beam cannot represent `skip_by_two` or free drift, and no power
   number here covers those constructions. **That is lane I1's scope.** If I1 changes the
   transition relation, this table must be re-measured — the stored per-replicate rows in
   `out_power.json` make that cheap.
3. **Adjudicator register** — *this lane defines it*. The panel covers nine registers. It does
   **not** cover Greek, Hebrew, Norse/Icelandic, Enochian or constructed languages, and it
   cannot cover non-linguistic payloads (key blocks, hashes, base32) — round10b/B6 showed that
   class is undetectable in principle by any language model, and the four agnostic statistics
   are the only instrument that touches it at all.

**A fourth conditional this lane discovered and hands to I1.** The beam chooses its skip path by
**English** score. For eight of the nine registers recovery is ~100 %, so the path is right and
the point is moot. For `EN_NOVOWEL` recovery is 67–81 %, and the adjudicator is therefore
scoring an *English-argmax path* through a non-English plaintext. The panel still fires — but a
decoder that scored candidate paths with `pmax` instead of `score_norm` would plausibly recover
the runes as well as detect the register. That is a concrete, measured proposal for I1, not a
speculation.

---

## 8. CONTRACT FOR PHASE 2

Binding on S1, S2 and any later lane that scores a decode.

### 8.1 What every sweep calls

```python
import sys; sys.path.insert(0, "<repo>/liber-primus/analysis/round19/I2")
from adjudicate import adjudicate, to_row, header, validate_row

hdr = header("round19/S1/G1-bash-random",
             key_space="bash $RANDOM, seeds 0..2^31, enumerated",
             decoder="I1 drift-beam vX (beam_w=400, max_skip=8, drift=...)",
             supp=0.83, notes="...")
store.write(json.dumps(hdr) + "\n")

for kid, plain_idx in decodes:                 # plain_idx = RUNE INDICES, never translit
    res = adjudicate(plain_idx)                # ~164 us at L=240; 0.12 % of a beam decode
    store.write(json.dumps(to_row(res, kid)) + "\n")
```

**One call. No sweep may score a decode any other way.** A lane that calls `score_norm`
directly is reproducing the defect this lane exists to fix.

### 8.2 What every sweep stores

Per decode, the full **`SWEEPROW/1`** — 13 fields in fixed order, defined in
[`SWEEPROW.md`](SWEEPROW.md): `kid n en pmax preg pmax_ne pcon pcreg ioc mds h2 zl z[9]`.
≈ 130 bytes as JSONL, or 77 bytes as the binary `ROW_DTYPE` (use the binary form past ~10⁶
rows). **Storing `(parameters, English score, head)` is the exact 0-of-15 failure mode that
made 10¹⁰ decodes un-reinterpretable; `validate_row` rejects it with that message.**

Committed with the round (the bulk store is gitignored):

| artifact | why |
|---|---|
| `sweeprow_header.json` | pins the panel build, corpus hashes, null calibration, and all three Q4 conditionals |
| **top-N per statistic**, N ≥ 50, with decode text — `pmax`, `pcon`, `pmax_ne`, `en`, `ioc` | **not one top-N by English.** L7-A §A.5: a Welsh plaintext would have ranked ~651st and a vowel-dropped-English one ~1.2×10⁶ of 1.39×10⁶, so neither could ever enter an English top-50. That is why the archive has zero power for them, permanently |
| summary histograms of all eight statistics (≥ 200 bins, with n/mean/sd/max) | lets a later round recompute a family-wise bar without the rows. Their absence is why R17's `expected_null_max_at_n` could never be reconciled with its own observed maximum (L7-C §C.3) |
| the thresholds used and the null they came from | |

### 8.3 What every sweep reports

1. **Coverage × power, never coverage alone** (R2). Power against *this* table, at the sweep's
   own L and decoder.
2. **All three conditionals** (§7) in `RESULTS.md` and in the ledger entry's `coverage` /
   `not_covered`. A negative missing one is not a result.
3. The **threshold** used, and that it came from I3's calibration — **not** a fixed −5.5, and
   **not** a random-rune null (§4.1).

### 8.4 Thresholds

Use **I3's** calibrated family-wise bar. Until it lands, the defensible interim bar is the
wrong-key `t_pmax` from §4.3 at the sweep's segment length, raised for multiplicity by
`k_eff ≈ 8` (§4.2) — e.g. at L=240 and N decodes, `alpha_per_decode = alpha / (N · 8)`. The
supplementary far-tail numbers in §4.4 show the panel retains power ≈ 1.00 out to a per-decode
FP of 1e-9, so the choice of bar within this range does not change any verdict.

### 8.5 Rebuilding the instrument

```bash
cd liber-primus/analysis/round19/I2
python3 build_models.py          # ~30 s; writes models/ (gitignored) + out_build.json
python3 -m pytest test_adjudicate.py -q
```

Corpora are the ones already in the repo; `out_build.json` carries a SHA-256 for each so a
drifted corpus is detectable rather than silent.

---

## 9. Bounds, not verdicts

**Measured.** A nine-register rune-space panel plus the four R3 statistics raises the correct-key
detection power from 0.00–0.83 (English quadgram, −5.5 bar) to **0.92–1.00** across nine
plaintext registers at L ∈ {120, 240, 400}, on held-out models, with **zero** false-positive
regression at matched trial count, at a cost of 164 µs/decode — 0.12 % of the beam decode it
adjudicates.

**Not covered.** Registers outside the nine; non-linguistic payloads; decoder transition models
beyond the Round-18 baseline (L7-B's hole is inherited, not fixed — that is I1); key families
other than `sha256_ctr`; the calibrated family-wise bar (that is I3); and the *readability* of a
vowel-dropped hit, which is a decoder problem this lane can detect but not solve.

**What reopens this.** A tenth register being proposed — add it to `build_models.REGISTERS` and
re-measure, it is a 30-second rebuild plus one power run. I1 changing the transition relation —
every number above is conditional on `encipher_keyskip → beam_decode(400, 3)`, and the stored
per-replicate rows make re-adjudication cheap. Or I3's calibrated bar landing above the
§4.4 extrapolation, in which case recompute the power table at that bar from
[`out_power.json`](out_power.json) rather than re-running anything.
