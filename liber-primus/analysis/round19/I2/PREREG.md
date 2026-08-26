# I2 — MULTI-REGISTER ADJUDICATOR — PRE-REGISTRATION

_Round 19, Phase 0 (blocking). Written **before any measurement in this lane**.
Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
Trust anchor run immediately before writing this file:_

```
python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5 known solves)
python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
```

---

## 0. The defect this lane exists to repair

`round18/L7-redteam/RESULTS.md` §A measured the repo's adjudicator by planting a **known key**
over nine plaintext registers, enciphering under the pinned soft anti-repeat filter, decoding
with the **correct key**, and reading `lp.score.Quadgram.score_norm` against the repo-wide
−5.5 bar:

| register | correct-key score (L=120) | power |
|---|---|---|
| EN_MODERN / EN_KJV / LP1_REAL | −4.11 … −4.33 | 1.00 |
| LATIN | −5.58 | 0.33 |
| OE | −5.39 | 0.58 |
| DE | −5.52 | 0.42 |
| CY | −6.58 | 0.00 |
| EN_HALFVOWEL | −5.62 | 0.33 |
| **EN_NOVOWEL** | **−7.60** | **0.00** — *below* the wrong-key score (−7.41) |

Rune-index recovery of the correct key is **100 %** for LATIN, OE, DE, CY and EN_HALFVOWEL and
85 % for EN_NOVOWEL. **The decoder finds the plaintext and the adjudicator throws it away.**

Doctrine **R3** additionally makes four language-agnostic statistics mandatory per sweep row.
Round 10b issued that requirement; compliance across the 15 post-B6 sweeps was **0 / 15**
(`out_a2.json → b6_handoff_compliance`), so 6,224,300 + 692,064 + 52,556 decodes and
≈1.45 × 10¹⁰ offsets are permanently un-reinterpretable.

---

## 1. The Aiming Test (doctrine §1) — answered before measuring

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A hit is a decode of LP2 whose rune stream is natural language in one of nine registers:
modern English, archaic (KJV) English, the Liber Primus' own lossy solved-page orthography,
Latin, Old English, German, Welsh, half-vowel-abbreviated English, vowel-dropped English.

**The recognizer is written before the search** — it is this lane's deliverable, `adjudicate()`
— and it is proved by planting the actual shape: for each register, a known key is planted, the
plaintext enciphered under `encipher_keyskip(supp=0.83)`, the ciphertext beam-decoded with the
**correct key**, and the decode handed to `adjudicate()`. Not a friendly analogue: the exact
L7-A protocol, on the exact registers L7-A measured, with the exact instrument chain.

The register whose recognisability is genuinely in doubt is **EN_NOVOWEL** (the current scorer
anti-selects it). Q5 below carries its kill condition.

### Q2 — What measured fact raises this family's prior above the flat rate?

`liber-primus/analysis/round18/L7-redteam/RESULTS.md` §A.1 and `out_a1.json`: nine registers ×
four lengths × 12 replicates of measured correct-key score, with 100 % rune recovery for five
registers that the adjudicator nonetheless scores as noise. The defect is *measured*, not
argued. `RESULTS.md` §A.6 measures the R3 non-compliance at 0/15 mechanically.

This is an **instrument** lane (doctrine §3 allocates ≈30 % of the round to exactly this, and
doctrine's own table shows that every genuinely new finding this project has produced came from
auditing a closure, an instrument, an artifact or an input — never from a new key-space sweep).

### Q3 — Is the space bounded, and by what?

Bounded and **enumerable**. This lane sweeps no key space. Its space is
**9 registers × 4 language-agnostic statistics × 3 segment lengths**, plus a null calibration
over a fixed 14-point length grid. Everything is enumerated; nothing is sampled from an
unbounded set. The only *sampled* quantities are the Monte-Carlo nulls, whose sample sizes are
fixed below.

### Q4 — What are the three conditionals the results will carry?

1. **Key space** — none swept. The plant uses `sha256_ctr(seed=CICADA3301)`, the B-04/D3 live
   class, exactly as L7-A did. Power is a property of the adjudicator, not the key family; only
   one family is measured and that is stated.
2. **Decoder transition model** — `encipher_keyskip(supp=0.83)` → `beam_decode(beam_w=400,
   max_skip=3)`. This lane deliberately holds the decoder at the Round-18 baseline so its
   numbers are comparable with L7-A's. It therefore inherits **L7-B's** hole: the beam cannot
   represent `skip_by_two` or free drift. **That is I1's lane, not this one**, and the power
   numbers here are conditional on the baseline construction. This is named explicitly in
   `RESULTS.md`.
3. **Adjudicator register** — *this lane defines it*. The panel covers nine registers. It does
   **not** cover Greek, Hebrew, Norse/Icelandic, Enochian, constructed languages, or
   non-linguistic payloads (key blocks, hashes, base32) — B6 showed the last class is
   undetectable in principle by any language model. Those stay in `not_covered`.

Additionally: the beam chooses its skip path by **English** score. For registers whose recovery
is < 100 % the adjudicator sees an English-argmax path, not the true path. This is measured
(recovery is reported per cell) and handed to I1 as a follow-on.

### Q5 — What single observation would abandon this lane at 10 % of budget?

**Kill condition (checkpoint: the 12-replicate smoke run, before the full grid):**
if a register-matched, held-out rune-space language model does **not** lift the correct-key
EN_NOVOWEL statistic to z ≥ +3.0 against its own wrong-key null at L = 240, then the
matched-LM approach is dead **for that register**. In that case I do not tune: I report
EN_NOVOWEL's achieved number, mark it un-adjudicable by a language model, and spend the
remaining budget on (a) the eight registers that respond and (b) the four language-agnostic
statistics — which are precisely the fallback R3 exists to provide, and which do not depend on
knowing the language at all.

The lane is **not** abandoned wholesale on that observation, because the `SWEEPROW` schema and
the agnostic statistics are independently required by R3 and are the only thing that makes
Phase 2 re-interpretable later.

---

## 2. Instrument — the design, fixed here before measurement

### 2.1 Register panel (9 rune-space language models)

Every model is built over **rune indices 0..28**, never over the transliteration string
(doctrine §4 rule 5 — 7 of 29 runes are 2 characters).

| id | corpus |
|---|---|
| `EN_MODERN` | `data/keys/self_reliance.txt` + `data/keys/mabinogion.txt` (English translation) — held out of the quadgram training set |
| `EN_KJV` | `data/kjv.txt` |
| `LP1_REAL` | the five solved pages' own plaintext from `SOLVED-PAGES.json`, in its actual lossy orthography (`CNOW`, `BELIEUE`, `THNGS`) |
| `LATIN` | `analysis/latin/latin_218.txt` + `latin_28233.txt` |
| `OE` | `round10b/B6.../corpora/oe_beowulf.txt` (thorn/eth/ash lines) + `data/keys/runepoem_oe.txt` |
| `DE` | `round10b/B6.../corpora/de_faust.txt` + `de_2.txt` |
| `CY` | `data/keys/welsh/welsh_mabinogion.txt` |
| `EN_HALFVOWEL` | `EN_MODERN` with 50 % of vowels deleted (seeded) |
| `EN_NOVOWEL` | `EN_MODERN` with all vowels deleted |

Text → runes uses `round10b/B6/detectors.text_to_runes(text, lang)` unchanged, i.e. the same
loader L7-A used, so the corpora are literally L7-A's corpora. Every corpus file is **SHA-256
hashed and the hash recorded** in `out_build.json`; the build script is committed and the
corpora themselves stay gitignorable (`CLAUDE.md`).

**Model form.** Interpolated trigram over rune indices, Jelinek–Mercer:

```
P(c | a,b) = l3*P3(c|a,b) + l2*P2(c|b) + l1*P1(c) + l0*(1/29)
l3,l2,l1,l0 = 0.70, 0.20, 0.09, 0.01     (fixed here; NOT tuned on the power measurement)
```

stored as a dense `log10` table of shape `(29,29,29)`. Trigram, not quadgram: 29³ = 24,389
cells against corpora of 2 × 10⁵ – 6 × 10⁵ runes is ~10–25 observations/cell, whereas 29⁴ =
707,281 cells would be sparser than the data. The interpolation weights are fixed *a priori*
and are not re-chosen after seeing power.

**Held-out discipline (mandatory).** For every register except `LP1_REAL`, the corpus is split
by position into a **first half (TRAIN)** and a **second half (TEST)**. The shipped LM is built
on TRAIN only; every plant window in the power measurement is drawn from TEST only. In-sample
power is additionally reported as an explicit upper bound, so the gap is visible.

`LP1_REAL` has only ~1,769 runes and cannot support a standalone trigram. Its LM is
`0.5 × trigram(solved pages) + 0.5 × trigram(EN_KJV TRAIN)`, mixed in probability space before
the log. Its held-out protocol is **leave-one-page-out**: the LP1 component is rebuilt without
page *i*, and the plant window is drawn from page *i*. Pages are 184 / 157 / 733 / 383 / 312
runes, so only 3 pages support L = 240 and only 1 supports L = 400; that restriction is stated
in the results rather than papered over.

### 2.2 The four language-agnostic statistics (doctrine R3)

Computed on the **decode's rune indices**:

| field | definition |
|---|---|
| `ioc` | decrypt IoC·N = `N * sum(c_s*(c_s-1)) / (n*(n-1))` |
| `mds` | minimum number of distinct symbols over any sliding **32-rune** window (whole string if n < 32) |
| `pmax_ne` | best **non-English** panel z over `{LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL}` |
| `h2`, `zl` | compressibility — see below |

**Compressibility — the choice, justified in advance.** Two figures are persisted:

- **`h2` (primary)** — plug-in order-2 conditional entropy in bits/rune,
  `H(X_i | X_{i-1}, X_{i-2})` from the decode's own bigram/trigram counts.
- **`zl` (secondary)** — `len(zlib.compress(bytes(x), 9)) / n`.

`h2` is primary because at the lengths Phase 2 actually scores (L ≈ 120–400) a zlib stream is
120–400 bytes: below the point where zlib's 32 KB window does any work, and dominated by its
fixed ~11-byte header/checksum, so `zl` is mostly a constant plus noise. `h2` is scale-free, has
a computable null, and is precisely the quantity a compressor is estimating. Both are stored
because `zl` costs 4 bytes and R3's wording explicitly permits either; the measured separation
of both is reported so the choice is defensible from data and not from assertion.

### 2.3 Calibration and the two panel statistics

At build time, for each L on the grid
`[32, 48, 64, 96, 128, 160, 200, 240, 320, 400, 500, 640, 800, 1000]`, a Monte-Carlo null of
**20,000 uniform-random rune strings** yields per register M: `mu_M(L)`, `sd_M(L)`, and the
9×9 correlation matrix. Then

```
z_M(x)  = (score_M(x) - mu_M(L)) / sd_M(L)          # per-register, comparable across registers
pmax(x) = max_M z_M(x)                              # the panel max
```

**Selection-corrected statistic.** L7-A §A.4 used the contrast `score_M − score_EN`
standardised against *the archive's own distribution*, because archived candidates are the
English argmax of their own sweep and English-correlated models (OE, DE) light up by selection
alone. This lane uses the **null-whitened English residual**:

```
r_M(x) = ( z_M(x) - rho_M(L) * z_EN(x) ) / sqrt(1 - rho_M(L)^2)
pcon(x) = max over non-English M of r_M(x)
```

where `rho_M(L)` is the correlation between `z_M` and `z_EN_MODERN` **under the pre-computed
random-rune null**, not under the sample.

Three reasons this is strictly better than A.4's version, stated before measuring:

1. **`rho` is estimated from the null, not from a post-selection sample.** A.4 standardised
   against 340 candidates that had already been selected on English; that shrinks the
   denominator by exactly the effect it is trying to remove.
2. **It is on a common scale.** `score_M − score_EN` mixes models with different variances (a
   Latin trigram's spread is not a Welsh trigram's), so a fixed contrast is not comparable
   across registers. `r_M` is unit-variance under the null by construction.
3. **It is computable per row, at sweep time, from row-local data.** A.4's statistic needs the
   whole archive to exist before any row can be scored — which is why it could only ever be a
   retrofit. R3 demands a per-row persisted statistic; `pcon` is one. This is the property that
   makes it usable by Phase 2 at all.

The empirical null distribution of `pcon` (and of `pmax`) is measured and reported, not
assumed to be N(0,1).

### 2.4 What is *not* changed

`lp.score.Quadgram.score_norm` is untouched and its value is persisted in every row as `en`, so
every Phase 2 result stays directly comparable with every published number in this repository.
The panel is **additive**.

---

## 3. Pre-registered gates

Stated here before measurement. **Not to be edited after seeing results**; any change appears
as a dated addendum with its reason (doctrine §4.1).

### G-POWER

**Protocol:** L7-A's own, unchanged — plant `sha256_ctr(seed=CICADA3301)`, encipher with
`encipher_keyskip(supp=0.83)`, beam-decode with the **CORRECT** key at `beam_w=400,
max_skip=3`, adjudicate the decode's rune indices.

- **24 replicates** per (register, L) cell — twice the required 12, so that the 0.90 bar has a
  resolution of 1/24 (0.90 requires ≥ 22/24) instead of the 1/12 that 12 replicates give.
- **L ∈ {120, 240, 400}**; 9 registers; plants drawn from **TEST** halves only.
- **The bar** is the matched-FP bar defined in G-FP below (`t_p` = the wrong-key null quantile
  at `alpha_ref = 1e-3`), *not* an arbitrary z.

**PASSES** iff measured power ≥ **0.90** for **every** register at **every** L ∈ {120,240,400}.
Any single cell below 0.90 fails the gate; the achieved number is reported regardless.
**EN_NOVOWEL is the declared hard case.** If it cannot reach 0.90 the gate is reported FAILED
with the achieved value and a plain statement of what is and is not recoverable. No tuning is
performed to manufacture a pass.

### G-FP

`alpha_ref = 1e-3` per decode, fixed here.

- The wrong-key null is measured directly: **≥ 2,000 wrong-key beam decodes at L=240** and
  ≥ 1,000 each at L=120 and L=400, on real planted ciphertexts (same construction, wrong key),
  under the same beam. Its agreement with the cheap uniform-random-rune null is *measured* and
  reported; the cheap null is used for tail extrapolation only if they agree.
- `t_EN` = the single-scorer (`score_norm`) threshold at per-decode FP `alpha_ref`.
- `t_p`  = the panel-max threshold at per-decode FP `alpha_ref` under the panel's **own** null.

**PASSES** iff, at those two matched-FP thresholds, the panel's power is **≥** the single
scorer's power for **every** register at **every** L — i.e. the panel buys register coverage
without paying for it in false positives.

**Owed to I3 regardless of verdict** (this is a deliverable, not a gate): the measured
inflation of the null caused by taking a max over 9 correlated models, expressed as an
**effective independent-test count `k_eff`**, defined as the multiplier for which
`P(pmax > t) ≈ k_eff * P(z_EN > t)` in the tail, together with the full empirical null
distributions of `z_EN`, `pmax`, `pcon` and the 9-vector `z`, written to
`out_null.json`. It is **not** assumed to be 9 and it is **not** assumed away.

### G-LP1

`LP1_REAL` must score **≥ −4.5** under the *legacy* `score_norm` at power **1.00** (bar −5.5),
i.e. the register the puzzle demonstrably uses must not regress. **PASSES** iff the median
`score_norm` of the correct-key decode over 24 replicates is ≥ −4.5 at every L ∈ {120,240,400}
and 24/24 replicates clear −5.5. The panel's own LP1 power is reported alongside.

### G-SPEED

Adjudicating one **240-rune** decode must cost **≤ 3×** the cost of one `score_norm` call on
the same decode's transliteration. Both are measured in the same process, best-of-5 timing runs
of ≥ 2,000 calls each, warm. **PASSES** iff `t_adjudicate(240) ≤ 3 × t_score_norm(240)`.
Microseconds/decode reported for both, plus the per-component breakdown.

---

## 4. Deliverables

| file | content |
|---|---|
| `adjudicate.py` | `adjudicate(plain_idx, translit=None) -> dict` — the single call every Phase 2 lane uses |
| `build_models.py` | builds + hashes the panel and the null calibration; corpora gitignorable, model artifacts rebuildable |
| `SWEEPROW.md` | the record schema every Phase 2 sweep persists per decode, plus a validator |
| `test_adjudicate.py` | unit tests incl. the validator and a plant-and-recover control |
| `RESULTS.md` | gate verdicts, register × L × score × power table, FP inflation, speed, Phase 2 contract |
| `out_build.json`, `out_power.json`, `out_null.json`, `out_speed.json`, `ledger.json` | machine-readable |

## 5. Rules this lane binds itself to

1. No `git commit` (13 lanes share one worktree).
2. No file written outside `analysis/round19/I2/` except gitignorable model artifacts under
   `analysis/round19/I2/models/`, all rebuildable by `build_models.py`.
3. Trust anchor run **before** (done, recorded above) and **after**; both recorded in
   `ledger.json`.
4. Bounds, not verdicts. No "exhausted"/"closed"/"unsolvable" (doctrine R7).
5. A FAILED gate is a legitimate, publishable outcome. No threshold is moved after the fact.

---

## Addendum — 2026-08-26, written AFTER the measurement

Appended per doctrine §4.1. **No threshold in §3 was edited.** All four gates were adjudicated
exactly as written above (`gates.py` reads the constants from this file's §3). Two
pre-registered *expectations* — not thresholds — turned out to be wrong, and are recorded here
so the record shows it rather than quietly absorbing it.

1. **§2.2's compressibility argument was wrong, in both directions.** It predicted `h2` would
   be the primary figure and `zl` near-useless at n ≈ 240. Measured (RESULTS.md §5): at L=240
   `zl` separates plant from wrong-key null at 10–21 null SD and `h2` at 11–17 — essentially
   tied — while `ioc`, which §2.2 did not single out, dominates both at 20–36 SD. The stated
   *reason* `h2` works is also wrong: the estimator is undersampled as §2.2 said, but H₃ and H₂
   are biased **unequally** (structured text repeats bigram contexts far more than trigram
   contexts) and the difference survives. Both figures are persisted as pre-registered; §5
   reports the measurement and recommends `ioc` as Phase 2's primary agnostic statistic.

2. **G-SPEED's denominator was the wrong quantity.** The gate compares `adjudicate` against
   `score_norm`. It FAILS at 4.79×. But a `beam_decode(400, 3)` at L=240 costs ≈ 134,300 µs
   against `adjudicate`'s 164 µs, so the adjudicator is 0.12 % of the decode it adjudicates and
   a 4.79× adjudicator adds ≈ 0.4 % to a sweep's wall-clock. The gate is **reported as FAILED**
   and not rewritten: a pre-registered threshold that turns out to have been aimed at the wrong
   quantity is exactly the kind of thing that belongs in the record. RESULTS.md §6.1 states the
   operational consequence (there is none) separately from the verdict (FAILED).

3. **Kill condition not triggered.** §1 Q5 set a kill at `EN_NOVOWEL` z < +3.0 against its own
   wrong-key null at L=240 in the smoke checkpoint. Measured: **z = 19.96**
   (`out_smoke.json`). The lane proceeded to the full grid as specified.

4. **Implementation optimisation, not statistic redefinition.** Between the first and final
   G-SPEED runs, `h2_cond`, `min_distinct`, `Panel.raw` and `idx_to_trans` were re-implemented
   for speed. `test_adjudicate.py` asserts each fast path equals a reference implementation
   exactly (`min_distinct_ref`, the `np.bincount` form of `h2`, the untransposed panel gather),
   so no statistic's *value* changed. `out_power.json` was produced before this change and
   remains valid.
