# I3 — NULLS & THRESHOLDS — results

_Round 19, Phase 0, BLOCKING for Phase 2. Pre-registered in [`PREREG.md`](PREREG.md) before
any null statistic was measured. Interface requirements on I1/I2 in
[`INTERFACE.md`](INTERFACE.md)._

## Gate verdicts

| gate | verdict | one line |
|---|---|---|
| **G-CAL** | **PARTIAL** | 41 of 46 cells at M ≥ 10⁶ have an empirical false-positive rate within 20 % of nominal. 5 fail; **every failure is in the conservative direction** (worst 26 % below nominal at α=0.01, 46 % at α=0.05), so no bar published here manufactures false positives. 71 further cells could not reach 10⁶ and are marked **PROVISIONAL** and named in §9.1. |
| **G-CAL-X** | **PASSED** | 52 of 52 out-of-sample extrapolation checks land within 1.0 Gumbel SD of the prediction made from block sizes n ≤ 10³. Worst residual −0.30 SD. |
| **G-RECOVER** | **PARTIAL** | **PASSED** for the `exact`, `pair` and `exact_ms8` presets — the correction does not merely preserve the power I1/I2 bought, it *increases* it (Latin 0.75 → 1.00, German 0.67 → 1.00, Welsh 0.08 → 1.00, vowel-dropped English 0.00 → 0.67). **FAILED** for I1's `drift` preset on Old English (median 13.40 vs bar 13.84). The tradeoff is quantified in §7. |
| **G-BACKCOMPAT** | **PASSED** | `threshold_for(n)` and `threshold_for(n, L)` are bit-identical to `benchmark/null.py` over 13 trial counts × 6 segment lengths × 4 alphas × 4 (mu, beta, floor) triples — 0 differences. The 8 existing `benchmark/` gates still pass. 15/15 lane tests pass. |
| **G-HONEST** | **PASSED** | Table published in §8 for all 14 sweep stages of Rounds 13/16/17, with the bar each *should* have used at its own adjudicated decode count, segment length and beam width. Discrepancies run in **both** directions: −5.5 was 0.12–1.19 **too strict** for 12 of them and 0.52–0.63 **too loose** for the two short-window R17-P3 lanes. **No published verdict flips (0/14).** |
| **G-PANEL** | **FAILED** | The two pre-registered estimators disagree by a factor of 2.06–2.45, not ≤ 1.5. This is a finding, not a measurement failure: **no single effective-test count describes this panel**, because the nine registers are not on commensurable per-draw scales. Estimates span 4.2 to 16.5. The bar is therefore taken from the directly fitted panel-max curve, and a naive Bonferroni is neither used nor recommended. §6. |

**PREREG Q5 kill condition: NOT met.** The vectorised engine reproduces
`skipdecode.beam_decode` exactly — `score` agrees to ≤ 1.2 × 10⁻¹⁴ on **600/600** random
cases at L ∈ {31, 120, 240}, and `plain_idx` is identical on 600/600 as well
(`out_geq.json`, `vecbeam.selftest_exact`). The lane ran on the fast path.

**Trust anchor.** Before: `validate.py` → ALL VALIDATIONS PASSED (5/5); `pytest benchmark/`
→ 8 passed. After: recorded in §11.

---

## 1. What was measured

**91 null cells**, ~9.6 × 10⁶ null decodes, all on the same generator (uniform random rune
ciphertext × uniform random keystream), fitted with block-maxima Gumbel + GPD + a free-shape
GEV, and each carrying its own G-CAL exceedance table.

| family | cells | what varies |
|---|---|---|
| per-register panel, `keyskip1`, beam_w 400 | 30 | 9 registers + panel-max, at L ∈ {31, 120, 240} |
| decoder transition relation, EN quadgram, L = 120 | 9 | `keyskip1`, `skip_by_two`, `drift1..3`, `union{2,4,6,8}` |
| R13/R16/R17 geometries, EN quadgram | 4 | (L, beam_w) = (25,120), (31,120), (40,120), (400,120) |
| **the actual Round-19 instrument** — I1 `driftbeam` × I2 `adjudicate` | 4 presets × 13 statistics | `exact`, `pair`, `exact_ms8`, `drift` |
| panel-combination rule | 2 | max-z vs min-p (PIT) |
| control: histogram-preserving shuffle of the real LP2 stream | 10 | L = 120 |

Machinery: [`vecbeam.py`](vecbeam.py) (vectorised, mode-parameterised beam, exact against the
reference), [`registers.py`](registers.py), [`nullcurve19.py`](nullcurve19.py) (the API),
[`run_calibration.py`](run_calibration.py), [`run_i1i2.py`](run_i1i2.py),
[`plants.py`](plants.py), [`ghonest.py`](ghonest.py), [`summary.py`](summary.py),
[`test_i3.py`](test_i3.py). Constants in [`calib19.json`](calib19.json).

### 1.1 The plants (PREREG Q1) — all three pass

| plant | result |
|---|---|
| **P1 synthetic Gumbel** — hand the fitter (μ=−7.25, β=0.0725), 10⁶ draws | recovered μ = **−7.2483** (Δ +0.0017), β = **0.07254** (+0.06 %). **PASS.** Critically, the GEV shape test on a *true* Gumbel returns ξ = −0.009, CI [−0.052, +0.036] — it contains 0, so the negative ξ found on every real cell (§4) is not a fitter artefact. |
| **P2 mis-calibrated bar** — hand G-CAL the legacy L≈120 constants applied at L = 31 | that bar's empirical exceedance rate is **0.9935 against a nominal 0.01 — a factor of 99**. G-CAL rejects it; G-CAL accepts this lane's measured cell (ratio 0.90). **PASS** — G-CAL is a gate that can fail. |
| **P3 correct-key plant** | §7 (G-RECOVER). |

### 1.2 The null generator is validated against the real ciphertext (PREREG §5)

Histogram-preserving shuffle of the real LP2 unsolved stream vs uniform random runes, L = 120,
`keyskip1`:

| cell | uniform μ / β | shuffle μ / β | β ratio |
|---|---|---|---|
| `EN_QUAD` | −7.0890 / 0.06814 | −7.1639 / 0.07801 | **1.145** |
| `panel_max` | 2.9741 / 0.86724 | 2.7699 / 0.82552 | **0.952** |

The PREREG required agreement within 25 %. Both pass, so the cheap uniform null is a valid
stand-in and every cell here inherits that licence.

---

## 2. The repo's own constants survive a 10⁶-sample audit

Round 18 L7-C.3 criticised `benchmark/null.py`'s constants as a **zero-degrees-of-freedom,
circular two-point solve** with 20.5 % relative uncertainty on β. That criticism of the
*method* was correct. The *numbers* turn out to be right.

|  | published | measured here (M = 10⁶, L = 120, beam_w 400) |
|---|---|---|
| μ | −7.2517 | **−7.0890** |
| β | 0.0725 | **0.06814** (published is +6.4 % high) |

The bar is what matters, and it barely moves:

| N | `threshold_for(N)` as published | uncapped legacy | uncapped **measured** | delta |
|---|---|---|---|---|
| 10⁶ | −5.5000 | −5.9166 | −5.8343 | +0.0823 |
| 10⁸ | −5.5000 | −5.5827 | −5.5205 | +0.0622 |
| 3.13 × 10⁸ | −5.5000 | −5.5000 | −5.4427 | +0.0572 |
| 10⁹ | −5.4158 | −5.4158 | −5.3636 | +0.0522 |
| 10¹⁰ | −5.2488 | −5.2488 | −5.2067 | +0.0421 |

**The published bar is within 0.04–0.08 of the measured one at every N, and the measured one
is slightly stricter.** Two anchors and zero degrees of freedom got the tail right. That is
worth saying plainly, because this lane exists to be sceptical of it.

The floor-crossing point moves a little: `threshold_for` crosses −5.5 at N\* = 3.13 × 10⁸
(published); measured, the pure family-wise bar reaches −5.5 at **N\* = 1.35 × 10⁸**.

**The bulk-sd trap is confirmed at scale.** `null.py` warns that estimating β from the null's
standard deviation is wrong by ~2.5× for this statistic. Measured on 10⁶ draws:
bulk-sd β / tail β = **2.64** at L = 120 and **2.45** at L = 31. The warning is exact.

---

## 3. β and μ as functions of segment length — the L7-C.4 law, refined

L7-C.4 measured β ratios consistent with β ∝ 1/√L from 400-sample shuffle nulls. With
2 × 10⁶, 10⁶ and 6 × 10⁴ samples the exponent is slightly steeper:

**beam_w = 400** (R13/R16's setting)

| L | μ | β | M |
|---|---|---|---|
| 31 | −6.9164 | 0.14893 | 2,000,000 |
| 120 | −7.0890 | 0.06814 | 1,000,000 |
| 240 | −7.1370 | 0.04508 | 60,000 (PROVISIONAL) |

fitted **β ∝ L^−0.583** (1/√L would be −0.500).

**beam_w = 120** (R17's setting)

| L | μ | β | M |
|---|---|---|---|
| 25 | −6.7912 | 0.15737 | 300,000 |
| 31 | −6.8028 | 0.13110 | 300,000 |
| 40 | −7.0396 | 0.13953 | 200,000 |
| 400 | −7.2261 | 0.04674 | 20,000 (PROVISIONAL) |

fitted **β ∝ L^−0.433**.

### 3.1 The cleanest statement of the problem

A fixed −5.5 bar is a valid α = 0.01 family-wise bar only up to some N, and that N depends on
the geometry **by twelve orders of magnitude**:

| geometry | P(one wrong-key decode > −5.5) | −5.5 is a valid α=0.01 bar up to N = |
|---|---|---|
| L = 25, beam_w 120 | 2.73 × 10⁻⁴ (1 in 3,661) | **37** |
| L = 31, beam_w 120 | 4.83 × 10⁻⁵ (1 in 20,695) | **208** |
| L = 40, beam_w 120 | 1.61 × 10⁻⁵ (1 in 61,962) | **623** |
| L = 31, beam_w 400 | 7.41 × 10⁻⁵ (1 in 13,505) | **136** |
| L = 120, beam_w 400 | 7.44 × 10⁻¹¹ (1 in 1.3 × 10¹⁰) | **1.35 × 10⁸** |
| L = 400, beam_w 120 | 1.1 × 10⁻¹⁶ | **1.1 × 10¹⁴** |

R17-P3 adjudicated ~26,400 decodes on head windows down to **25 runes** against a fixed −5.5.

---

## 4. The tail is bounded: the Gumbel bar is CONSERVATIVE, not anti-conservative

PREREG H1 asked whether the true extreme-value family is Weibull (ξ < 0) rather than Gumbel,
because the score is bounded above (a perfect English decode is ≈ −2.2).

**It is.** Across all **46 cells with M ≥ 10⁶**, the fitted GEV shape is negative in
**46/46**, range **ξ ∈ [−0.117, −0.004]**, mean **−0.064**, and the Gumbel is rejected at 95 %
in **36/46**. On a planted true Gumbel the same fitter returns ξ = −0.009 with a CI containing
zero (P1), so this is a property of the data, not of the estimator.

**Correction to the PREREG.** PREREG §2 said ξ < 0 "would make the Gumbel bar
*anti-conservative* at large N". That is backwards and it is corrected here rather than
quietly dropped: ξ < 0 means a finite upper endpoint, so Gumbel extrapolation over-states the
quantile and the bar comes out **too high** — conservative. The pre-registered *test* is
unchanged; the direction stated alongside it was wrong.

Quantified, for the L = 120 EN cell (GEV fitted on block-1000 maxima, ξ = −0.0560):

| N | Gumbel bar (published) | GEV bar | Gumbel is stricter by |
|---|---|---|---|
| 10⁴ | −6.148 | −6.220 | 0.072 |
| 10⁶ | −5.834 | −6.030 | 0.195 |
| 10⁸ | −5.520 | −5.882 | 0.362 |
| 10⁹ | −5.364 | −5.822 | 0.458 |
| 10¹⁰ | −5.207 | −5.768 | 0.562 |

**Recommendation: keep the Gumbel bar.** Its false-positive rate is verified at-or-below
nominal by G-CAL, its conservatism is now bounded and reportable, and the GEV's own shape
parameter carries a wide CI. The GEV column is published as the power-optimal alternative for
anyone who wants it; the same trend is visible directly in G-CAL, whose exceedance ratios fall
from ≈1.0 at block size 10–100 to 0.4–0.85 at block sizes 10³–10⁴.

---

## 5. The decoder-mode curve — what permissiveness costs

The whole reason a Round-19 bar cannot be a Round-18 bar. All at L = 120, EN quadgram, the
statistic `benchmark/null.py` is calibrated on. `union<λ>` is this lane's proxy family: every
key advance of 1..4 is admissible, a doublet-consistent one is free, an inconsistent one costs
λ. λ = ∞ is exactly the repo's relation; λ = 0 is `driftN`.

| mode | λ | realised drift per rune | μ | β | null mean | bar @ N=10⁶ | **shift vs `keyskip1`** | M |
|---|---|---|---|---|---|---|---|---|
| `keyskip1` | ∞ | 0.020 | −7.0890 | 0.06814 | −7.341 | −5.834 | **0.000** | 1,000,000 |
| `skip_by_two` | ∞ | 0.040 | −7.0957 | 0.06836 | −7.345 | −5.837 | **−0.002** | 200,000 |
| `union8` | 8 | 0.351 | −6.6757 | 0.07319 | −6.835 | −5.328 | **+0.507** | 12,000 |
| `union6` | 6 | 0.493 | −6.4449 | 0.07112 | −6.581 | −5.135 | **+0.699** | 12,000 |
| `union4` | 4 | 0.711 | −6.0511 | 0.05905 | −6.191 | −4.964 | **+0.871** | 12,000 |
| `union2` | 2 | 1.039 | −5.4962 | 0.05783 | −5.565 | −4.431 | **+1.403** | 12,000 |
| `drift1` | 0 | 0.500 | −5.4362 | 0.06679 | −5.588 | −4.206 | **+1.628** | 12,000 |
| `drift2` | 0 | 0.999 | −4.7637 | 0.05520 | −4.857 | −3.747 | **+2.087** | 12,000 |
| `drift3` | 0 | 1.502 | −4.4334 | 0.04827 | −4.508 | −3.545 | **+2.290** | 12,000 |

### 5.1 The three things this says

**(a) Covering L7-B's `skip_by_two` hole is FREE.** The pair-constrained relation admits key
advances at the same rate as the single-skip one (both need a skipped position to reproduce
the previous cipher rune, probability 1/29), so its null is statistically indistinguishable
from the baseline: shift **−0.002**. Measured directly on I1's own implementation
(`PRESETS["pair"]`, `mode=keyskip2`, `max_skip=8`) the shift is **+0.019**; `exact_ms8` costs
**+0.034**. The single most consequential decoder gap Round 18 found can be closed at a cost
of about two hundredths of a score unit. **This is the best news in the lane.**

**(b) Unconstrained drift is ruinous, and a penalty is far more efficient than a cap.**
`drift1` and `union6` produce almost the same realised drift (0.500 vs 0.493) but the null
rises by **1.628** for the hard-capped relation and only **0.699** for the penalised one — a
factor of 2.3. A penalised permissive relation buys the same construction coverage at less
than half the false-positive cost. I1's `permissive` mode is already the right shape; the
knob is λ.

**(c) There is a hard budget.** With the correct-key English score at ≈ −4.2 and the baseline
null at −7.34, the entire usable margin is ≈ 3.1. The family-wise correction at N = 10⁶ eats
1.25 of it. Everything above ≈ 1.8 of null shift is unaffordable at that N.

> **Proxy caveat, stated because it matters.** This lane's `union<λ>` reports the **penalised**
> score; I1's `permissive` reports the **unpenalised** quadgram score of the penalised path.
> The unpenalised convention has the higher null, so the table above is a **lower bound** on
> the shift for I1's convention at the same λ. The `driftbeam` cells in §7 and §10 are
> measured on I1's actual implementation and are not proxies.

---

## 6. The panel-max correction, and why there is no effective test count

### 6.1 The registers are not commensurable — measured

At L = 120, `keyskip1`, on the same 10⁶ decodes, the nine registers' single-draw null
locations span **−7.09 (EN quadgram) to −1.48 (LP1_REAL)**, their tail scales span
**0.0048 to 0.0681** (a factor of 14), and their bulk-to-tail ratios span **1.84 to 2.78**.
A raw `max` over such a panel is not a test; it is a fixed preference for whichever register
has the widest bulk relative to its tail.

Mean off-diagonal null correlation **0.406**, range 0.014–0.793, first eigenvalue **4.52 of 9**
— a strong common factor, exactly the confound L7-A.4 identified.

### 6.2 Seven estimates of "the effective number of tests", spanning 4× 

All at L = 120, 9 registers, on the same null. `max-z` standardises by each register's fitted
tail curve; `min-p` is the probability-integral transform (each score converted to its own
null p-value on a **disjoint** reference half, then `−log₁₀ min p`).

| estimator | max-z panel | min-p panel |
|---|---|---|
| naive Bonferroni | 9 | 9 |
| Li & Ji eigenvalue | 8.00 | 8.00 |
| Cheverud–Nyholt | 8.49 | 8.56 |
| tail ratio at α = 10⁻² | 7.21 | 7.44 |
| tail ratio at α = 10⁻³ | 8.24 | 8.20 |
| tail ratio at α = 10⁻⁴ | 9.23 | 7.23 |
| **location shift** of the fitted curves | **16.54** | **4.24** |
| I2's own `k_eff` (`I2/null.log`, L=120) | 6.06 | — |

**G-PANEL FAILED as pre-registered**: the two nominated estimators (location shift, eigenvalue)
differ by 2.06× on the min-p panel and 2.45× on I2's own panel, against a 1.5× criterion.

**Why, and what to do instead.** The estimators disagree because the location-shift estimator
assumes the panel-max curve is parallel to a single register's (β_panel = β_single); measured,
β_panel/β_single = 0.867/1.0 for max-z and 0.467/0.416 for min-p, so it is not. The panel
penalty therefore **shrinks with N**: on the max-z panel it is 2.27 z-units at N = 1, 1.02 at
N = 10⁶ and 0.39 at N = 10⁹. An "effective number of tests" is not a constant of this panel,
and quoting one — 9, 8 or 6 — is quoting a number that is only right at one N.

**Adopted: the directly fitted panel-max curve.** `threshold_for(..., statistic='panel_max')`
returns a bar from the measured (μ, β) of the panel statistic itself, which needs no
multiplicity model and whose false-positive rate G-CAL verifies at 10⁶ decodes (ratio 0.97 at
block 100, 1.006 at block 10). **A naive Bonferroni is neither used nor recommended:** at
N = 10⁶ it would over-correct the max-z panel by ln(9/4.2) ≈ 0.76 z-units and under-correct it
at N ≈ 1 — wrong in both directions, in the same panel.

### 6.3 The min-p panel is the better construction, and by how much

| panel rule | μ | β | bar at N = 10⁶, α = 0.01 | observed null max |
|---|---|---|---|---|
| max-z (what I2 computes) | 2.806 | 0.896 | 18.94 (on its own z scale) | 15.45 |
| **min-p (PIT)** | 0.754 | 0.467 | 9.35 (in −log₁₀ p) | 5.48 |

The min-p panel's location shift over a single register is **4.24 effective tests** against the
max-z panel's 16.54 — i.e. making the registers exactly commensurable removes about **⅔ of the
multiplicity penalty**, because what max-z was charging for was mostly scale mismatch, not
multiplicity. Recommended to I2 as a v2 statistic; not required, because the bar for the
current `pmax` is measured here and is correct as it stands.

### 6.4 Adjudicating the M_eff disagreement between I2, R1 and this lane

Three lanes measured "the effective number of tests" in the panel and got different answers.
They are **not contradictory**; they are different lengths, different tail depths and different
standardisations of the same panel.

| source | value | L | tail depth | z standardised by |
|---|---|---|---|---|
| naive Bonferroni | 9 | — | — | — |
| **R1** | **5.0** | 120 | — | I2's |
| **I2** (`I2/out_null.json`) | **6.25 / 9.52 / 8.00** | 120 / 240 / 400 | α = 10⁻³ | random-rune bulk sd |
| **I2** | 7.2–7.5 | 120 | α = 10⁻² | random-rune bulk sd |
| **I3** tail ratio (max-z) | **7.21 / 8.24 / 9.23** | 120 | α = 10⁻² / 10⁻³ / 10⁻⁴ | this lane's fitted tail curve |
| **I3** Li & Ji eigenvalue | 8.00 | 120 | — | either |
| **I3** location shift (max-z / min-p) | 16.54 / 4.24 | 120 | — | tail curve / PIT |

Two things fall out. **I3's tail ratio at α = 10⁻² is 7.21 and I2's at the same depth is
7.2–7.5 — they agree exactly.** And I2's own figure moves from 6.25 to 9.52 to 8.00 as L goes
120 → 240 → 400. So the quantity is not stable in L, not stable in tail depth, and not stable
under a change of standardisation. Across every lane and depth the estimates span **4.2 to
16.5**, with most between 5 and 9. R1's 5.0 and I2's 6.25 sit at the low end of that spread;
neither is wrong.

**Resolution — R1's recommendation is adopted, and this lane had already reached it
independently (§6.2).** Stop correcting for a number of tests. **Calibrate a direct null on the
panel maximum**, which is what `I19:vecbeam.keyskip1+I2|pmax|L120` is: M = 10⁶ wrong-key beam
decodes, G-CAL-verified at ratio 1.006 (block 10) and 0.97 (block 100). That statistic needs no
multiplicity model, so the dispute has no bearing on the published bar. R1's objection is
correct and is the reason the answer to "what is M_eff for this panel" is **"the question does
not have a scalar answer; here is the curve instead."**

R1's directly measured naive-panel false-positive rate — **0.0543 against 0.0093 English-only**,
a 5.8× inflation — is consistent with the low end of the table and is the cleanest single
demonstration of why an English-calibrated bar must never be applied to a panel statistic.

---

## 7. G-RECOVER — the correction does not kill power; it *buys* power

12 replicates per register, L = 120, key family `sha256_ctr(seed=CICADA3301)`, mechanism
`skip(supp=0.83)`, correct key handed to the decoder, adjudicated by I2. Bars at N = 10⁶,
α = 0.01, from the cells in §10. Raw rows in `out_plants.json`.

### 7.1 `exact` preset (the repo's own beam) — **PASSED**

| register | median recovery | power, OLD fixed −5.5 on `en` | power, NEW `en` bar (−5.829) | power, NEW `pmax` bar (7.634) |
|---|---|---|---|---|
| EN_MODERN | 1.00 | 1.00 | **1.00** | **1.00** |
| EN_KJV | 1.00 | 1.00 | **1.00** | **1.00** |
| LP1_REAL | 1.00 | 1.00 | **1.00** | **1.00** |
| **LATIN** | 1.00 | 0.75 | **1.00** | **1.00** |
| **DE** | 1.00 | 0.67 | **1.00** | **1.00** |
| **OE** | 1.00 | 0.67 | **0.92** | **1.00** |
| **EN_HALFVOWEL** | 1.00 | 0.50 | **0.83** | **1.00** |
| **CY** | 1.00 | 0.08 | 0.08 | **1.00** |
| **EN_NOVOWEL** | 0.80 | 0.00 | 0.00 | **0.67** |
| RAND *(negative control)* | 0.36 | 0.00 | **0.00** | **0.00** |

Two separable gains, and it is worth being precise about which is which:

- **Replacing the fixed −5.5 floor with the properly scale-corrected family-wise bar, changing
  nothing else — not the decoder, not the scorer — takes Latin from 0.75 to 1.00, German from
  0.67 to 1.00, Old English from 0.67 to 0.92 and half-vowel English from 0.50 to 0.83, at a
  *verified* α = 0.01 over 10⁶ decodes.** The −5.5 floor has no statistical justification: it
  is the historical confirm threshold, and at every sweep's own N it is **stricter** than the
  bar that actually controls the error rate. A large part of what L7-A diagnosed as an
  English-only *scorer* was an English-only *bar*.
- **I2's panel then adds what the bar cannot**: Welsh 0.08 → 1.00 and vowel-dropped English
  0.00 → 0.67, the two registers L7-A.5 called permanent blind spots of the archive.
- The negative control holds: uniform-random plaintext scores 0.00 on every statistic under
  every bar.

_(These old-bar powers, 0.75/0.67/0.67/0.50, are higher than L7-A.1's 0.33/0.42/0.58/0.33 for
the same registers. Both are 12-replicate estimates on different text windows and plant seeds;
the binomial SE at n = 12 is ~0.14, so the two are compatible. The *direction and size* of the
improvement is measured within this lane's own replicates and does not depend on that.)_

### 7.2 `drift` preset — **FAILED**, and the tradeoff quantified

| register | `en` power (exact → drift) | `pmax` power (exact → drift) |
|---|---|---|
| EN_MODERN | 1.00 → 0.92 | 1.00 → 1.00 |
| LP1_REAL | 1.00 → 0.67 | 1.00 → 1.00 |
| LATIN | 1.00 → **0.00** | 1.00 → 1.00 |
| DE | 1.00 → **0.00** | 1.00 → 1.00 |
| OE | 0.92 → **0.00** | 1.00 → **0.25** |
| EN_HALFVOWEL | 0.83 → **0.00** | 1.00 → 0.67 |
| CY | 0.08 → 0.00 | 1.00 → 0.42 |
| EN_NOVOWEL | 0.00 → 0.00 | 0.67 → 0.00 |

G-RECOVER's pre-registered criterion — every register with L7-A.1 power ≥ 0.33 must have its
median correct-key statistic clear the new panel bar — fails on **OE** (median `pmax` 13.40 vs
bar 13.84, shortfall 0.44). It also fails badly on `en`, where the drift preset's null rise of
**+0.95** consumes the entire margin.

**What that costs, stated as a number.** Under `drift`, the family-wise `en` bar at N = 10⁶ is
**−4.453**, while a *genuine* English solve scores ≈ −4.2. The crossing point — the N at which
a real English plaintext stops clearing its own bar — is **N ≈ 1.3 × 10⁷ decodes**. At I1's
measured 1.39 decodes/s/core for that preset, 1.3 × 10⁷ decodes is ~2,600 core-hours, so in
practice compute binds before statistics do and the preset is usable. But `en` must not be the
claim statistic under `drift`.

**Recommendation, and it is the lane's main operational one: run `exact`/`pair` and `drift` as
two separate cells and adjudicate each against its own bar.** They cost 2 tests, i.e. β·ln 2 =
0.05 on `en` and 0.30 on `pmax` under `drift` — negligible — and together they cover both the
register axis and the construction axis without either destroying the other.

### 7.3 The false positive this lane exists to prevent, made concrete

A **wrong key** on **random ciphertext**, decoded with I1's `drift` preset and adjudicated by
I2, over only 15,000 trials:

| statistic | null mean | null max over 15,000 | for comparison |
|---|---|---|---|
| `en` | **−6.357** | **−5.351** | the repo's historical confirm bar is **−5.5**. A wrong key crosses it. |
| `pmax` | 5.14 | **9.33** | I2's own random-rune null max is **1.163** over 200,000 draws (`I2/null.log`) |
| `pcon` | 2.54 | 6.47 | |

Under the `keyskip1` relation the same statistics give `en` max −6.171 and `pmax` max 6.047
over 10⁶ decodes. So:

1. **The decoder contributes most of it.** `pmax` null max goes 6.05 → 9.33 on 66× *fewer*
   trials when the transition relation is widened.
2. **I2's z scale is off by a factor of 5 even at `keyskip1`**, because `Panel.cal` standardises
   on a random-rune null and the object being adjudicated is a beam decode's argmax output
   (1.163 random-rune vs 6.047 decoder-output). Under `drift` it is off by ~8.
3. Had Phase 2 adjudicated against anything resembling the nominal z scale — "z ≥ 4", say —
   **every decode would have been a hit.** This is precisely the conversion of a power problem
   into a false-positive problem the lane was built to catch, and it is now priced.

---

## 8. G-HONEST — the retrospective, both directions

The bar each sweep *should* have used at its **own** adjudicated decode count, segment length
and beam width, against the bar it used. `N_adj` is decodes actually scored on the `score_norm`
scale; `N_enum` is candidates enumerated. Sources and JSON keys in
[`ghonest.py`](ghonest.py); full output in `out_ghonest.json`.

| sweep | N_enum | **N_adj** | L | bw | bar used | **correct bar (α=.01)** | Δ | best | verdict flips? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R13-B04-A | 1,385,600 | 1,385,600 | 120 | 400 | −5.500 | **−5.812** | +0.312 | −6.185 | no |
| R13-B04-B | 1,290,240 | 1,290,240 | 120 | 400 | −5.500 | **−5.817** | +0.317 | −6.129 | no |
| R13-B04-C | 3,548,160 | 3,548,160 | 100 | 400 | −5.500 | −5.623 † | +0.123 | −5.885 | no |
| R13-B04-D1 | 150 | 150 | 262 | 400 | −5.500 | −6.642 † | +1.142 | −6.654 | no |
| R13-B04-D2 | 150 | 150 | 12,956 | 400 | −5.500 | −6.935 †† | +1.435 | −7.239 | no |
| R16-KDF-A | 692,064 | 692,064 | 120 | 400 | −5.500 | **−5.859** | +0.359 | −6.259 | no |
| R16-PRNG | 52,556 | 52,556 | 120 | 400 | −5.500 | **−6.035** | +0.535 | −6.347 | no |
| R17-P0 primary ms3 | 2,900,403,446 | **5,554** | 400 | 120 | −5.500 | **−6.608** | +1.108 | −6.769 | no |
| R17-P0 nibbles ms3 | 1,011,416,288 | **1,042** | 400 | 120 | −5.500 | **−6.686** | +1.186 | −6.822 | no |
| R17-P0 ms8 | 2,900,237,574 | **3,869** | 400 | 120 | −5.500 | **−6.625** | +1.125 | −6.769 | no |
| R17-P1 bitcoin | 1,389,182,016 | **17,920** | 400 | 120 | −5.500 | **−6.553** | +1.053 | −6.802 | no |
| R17-P2 beacons | 3,464,597,548 | **3,839** | 400 | 120 | −5.500 | **−6.625** | +1.125 | −6.811 | no |
| **R17-P3 tables** | 2,466,258,498 | **26,400** | **40** | 120 | −5.500 | **−4.977** | **−0.523** | −6.420 | no |
| **R17-P3 tables ms8** | 3,291,058,250 | **25,080** | **31** | 120 | −5.500 | **−4.872** | **−0.628** | −5.679 | no |

† extrapolated along the fitted β ∝ L^−0.583 law from the measured bw = 400 cells.
†† L = 12,956 is far outside the measured range (31–240); treat as indicative only.

**No published verdict flips: 0 of 14.** Every sweep's best score is on the same side of the
correct bar as it was of −5.5. Every "NEGATIVE" in Rounds 13/16/17 stands.

### 8.1 What the table says that has not been said before

1. **L7-A already suspected it, and it is confirmed: −5.5 was used out of habit, and it was
   the wrong bar in 14 of 14 cases.** Twelve times it was 0.12–1.19 **too strict**; twice it
   was 0.52–0.63 **too loose**.
2. **The too-strict direction is not harmless — it is exactly the L7-A blind spot.** At R17's
   own geometry (L = 400) the correctly-calibrated bar is ≈ −6.6, and L7-A.1's correct-key
   medians at L = 400 are Latin −5.55, OE −5.45, DE −5.48, half-vowel −5.68. All four clear
   −6.6 comfortably and all four fail −5.5. Had the bar been right, R17-P0/P1/P2's adjudicator
   would have had power ≈ 1.0 against those four registers instead of 0.33–0.58.
   **Caveat, and it is a real one:** R17 also ran an *English trigram prefilter* before the
   beam (L7-A.7), whose non-English survival was never measured. Fixing the bar raises the
   adjudicator's power; it does not by itself make R17's non-English coverage 1.0.
3. **The too-loose direction is a live false-positive risk and it is in exactly the lane R17
   called a near-miss.** R17-P3's headline −5.679 was scored on a **31-rune** head. At that
   geometry a random wrong key exceeds −5.5 once in 20,695 decodes, and the correct α = 0.01
   bar at P3-ms8's own 25,080 adjudicated decodes is **−4.872**. So the "0.18 short of a hit"
   framing understates the gap by a factor of 4.5: it was **0.81 short**. And across the
   ~4,600 P3-ms8 decodes on heads of 25–42 runes, the *expected* number of null crossings of
   −5.5 is **0.2–1.2** depending on the head mix — i.e. P3 was of order one draw away from
   publishing a spurious −5.5 crossing, with nothing in its design that would have caught it.
4. **`threshold_for` was fed the wrong N in every R17 lane that called it**, confirming
   L7-C.3. P1 and P3 passed the offset count only; P0 and P2 passed both but quoted the offset
   figure. The offsets-to-decodes inflation is 10⁵–10⁶× per lane.
5. **L7-C.6's repo-wide tally is itself inflated by the same error.** Recomputed on adjudicated
   decodes: Round 8 SEED 2.52 × 10⁹ + Round 8 other 8.2 × 10⁶ + B-04 6,224,300 + B-05 70,680 +
   R16-KDF 692,064 + R16-PRNG 52,556 + **all of R17 = 83,704** + the small lanes =
   **2,535,325,467**, not 17,058,157,809 — a **6.7×** inflation. The repo-wide family-wise bar
   at α = 0.01 is therefore **−5.300** (measured constants) or −5.348 (published constants),
   not the −5.210 L7-C.6 published. The *qualitative* claim survives unchanged: the repo-wide
   bar is stricter than −5.5, so −5.5 should not be quoted as a repo-wide bar.

---

## 9. Family-wise error target for Round 19 — proposed and defended

**Proposal (pre-registered in PREREG §7 before any of the above was measured):**

- **α_round = 0.01** — at most a 1 % probability that Round 19 as a whole publishes one or more
  false CLAIMs, across every lane, every statistic and every decode.
- **Two tiers.** Tier 1 **ESCALATE** at per-lane α = 0.05 — generates candidates for secondary
  inspection, never a claim. Tier 2 **CLAIM** at round-wide α = 0.01, computed at the *round's*
  total adjudicated decode count.
- **One claim statistic.** Claim on `pmax`. `en`, `pmax_ne`, `pcon`, `ioc`, `mds`, `h2`, `zl`
  are persisted and reported as diagnostics but are not claim statistics. A lane claiming on
  k statistics splits α k ways.
- **N is decodes adjudicated, round-wide, never candidates enumerated.**

**Defence, now that the numbers exist:**

1. **Cost asymmetry, not vibes.** A false CLAIM here is archived permanently and has twice
   foreclosed a lane that was later found live (doctrine §5). A false negative costs one lane's
   budget and is recoverable — Round 18 recovered three. 0.05 round-wide would mean a 1-in-20
   chance that the round designed to fix false positives commits one; that is the wrong number
   for the CLAIM tier and exactly the right one for ESCALATE, where the consequence is a human
   reading a decode.
2. **0.001 costs measurable power, and it costs it in exactly the registers this round exists
   to recover.** Going from α = 0.01 to 0.001 raises the L = 120 `en` bar by β·ln 10 =
   **0.158**. Measured on the same 12 replicates as §7.1, at N = 10⁶:

   | register | power at α=0.01 | power at α=0.001 |
   |---|---|---|
   | LATIN | 1.00 | **0.83** |
   | DE | 1.00 | **0.92** |
   | OE | 0.92 | **0.75** |
   | EN_HALFVOWEL | 0.83 | **0.67** |
   | EN_MODERN / LP1_REAL | 1.00 | 1.00 |

   At N = 3 × 10⁷ the same four fall to 0.42–0.50 at α = 0.001 (against 0.58–0.83 at α = 0.01).
   English and the LP1 register are untouched either way — which is the point: tightening α
   buys nothing where the signal is strong and costs 8–17 points where it is marginal.
3. **The conservatism is already stacked.** The Gumbel bar is 0.20–0.56 stricter than the GEV
   bar (§4), G-CAL's deviations are all conservative (§9.1), and the union bound over
   correlated decodes is conservative again. Three layers of safety margin is enough; a fourth
   is paid for entirely out of power.
4. **Allocation by union bound over the round's adjudicated decodes.** Every lane calls
   `threshold_for` at N_round, not N_lane. Conservative, because the decodes are not
   independent — the same 12,956 runes are re-decoded — which is the safe direction for a
   negative (the same argument L7-C.6 makes).
5. **The estimate does not have to be right in advance.** Because I2's `SWEEPROW` persists the
   statistic for every decode, the bar can be recomputed at close-out and every row
   re-adjudicated without re-running a single decode. That is a concrete, practical argument for
   doctrine R3 that the repo has not previously made.

**Worked values** (L = 120, `exact` preset, `en` — the legacy statistic, for orientation):

| N_round | ESCALATE (α=0.05) | CLAIM (α=0.01) |
|---|---|---|
| 10⁴ | −6.257 | −6.145 |
| 10⁵ | −6.102 | −5.991 |
| 10⁶ | −5.941 | −5.829 |
| 10⁸ | −5.632 | −5.520 |

### 9.1 G-CAL in full, and the cells that could not reach 10⁶

**46 cells reached M ≥ 10⁶.** 41 pass the ≤ 20 % criterion at every gating block size (a block
size gates only when its expected exceedance count ≥ 50, i.e. binomial SE ≤ 14 %). The five
that fail:

| cell | worst gating deviation (α, block) | ratio | direction |
|---|---|---|---|
| `EN_MODERN\|keyskip1\|L31` | α=0.05, n=10³ | 0.690 | 31 % conservative |
| `OE\|keyskip1\|L120` | α=0.05, n=10³ | 0.620 | 38 % conservative |
| `I19:vecbeam.keyskip1+I2\|z:EN_KJV\|L120` | α=0.05, n=10³ | 0.680 | 32 % conservative |
| `I19:vecbeam.keyskip1+I2\|z:EN_KJV\|L31` | α=0.05, n=10³ | 0.680 | 32 % conservative |
| `I19:vecbeam.keyskip1+I2\|z:OE\|L31` | α=0.05, n=10³ | 0.540 | 46 % conservative |

**Every failure is conservative** — the bar is exceeded *less* often than nominal, never more.
No bar published here manufactures false positives; five of them cost a little power. Every
failure is also at the **largest** gating block size (n = 10³), which is the ξ < 0 signature of
§4 showing up exactly where the theory says it should: the further into the tail you go, the
more the bounded-tail truth falls below the Gumbel extrapolation. At α = 0.01 the worst gating
deviation over all 46 cells is 26 %; at α = 0.05 it is 46 %.

**Cells marked PROVISIONAL because M < 10⁶** (71 of them; the full list is in
`out_summary.json → gates → G-CAL → provisional_cells`). The families:

| family | M | why not more |
|---|---|---|
| all `driftbeam.drift+I2` cells (13) | 15,000 | I1's `drift` preset runs at **1.39 decodes/s/core**; 10⁶ is 200 core-hours |
| all `driftbeam.pair+I2` and `exact_ms8+I2` cells (26) | 60,000 | 48 and 92 decodes/s/core |
| `union{2,4,6,8}`, `drift{1,2,3}` (16, incl. `EN` aliases) | 12,000 | the permissive relation fills the beam every step |
| L = 240 register panel (10) | 60,000 | 10 decodes/s/core at beam_w 400 |
| the four (L, beam_w=120) R17 geometries | 2×10⁴–3×10⁵ | L = 400 is 30 decodes/s/core |
| `panel_max\|minp\|keyskip1\|L120` | 300,000 | half of a 6×10⁵ run is held out as the PIT reference |

**The re-run that finalises them** is stated exactly, in §11.

---

## 10. THE THRESHOLD CONTRACT FOR PHASE 2

All at **L = 120**, uniform-random null, α as shown. `en` = `lp.score.Quadgram.score_norm`
(the legacy statistic, comparable to every number in the ledger). `pmax` / `pcon` = I2's
panel statistics on I2's own z scale. Constants in [`calib19.json`](calib19.json).

| I1 preset | statistic | μ | β | M | **ESCALATE α=0.05** N=10⁴ | N=10⁶ | **CLAIM α=0.01** N=10⁴ | N=10⁶ | status |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `exact` | `en` | −7.0946 | 0.06875 | 1,000,000 | −6.257 | −5.941 | −6.145 | **−5.829** | CALIBRATED |
| `exact` | **`pmax`** | 2.3575 | 0.28653 | 1,000,000 | 5.848 | 7.167 | 6.315 | **7.634** | CALIBRATED |
| `exact` | `pcon` | 2.0360 | 0.26463 | 1,000,000 | 5.259 | 6.478 | 5.691 | 6.909 | CALIBRATED |
| `pair` | `en` | −7.0754 | 0.06626 | 60,000 | −6.268 | −5.963 | −6.160 | −5.855 | PROVISIONAL |
| `pair` | **`pmax`** | 2.4200 | 0.26953 | 60,000 | 5.703 | 6.944 | 6.142 | **7.384** | PROVISIONAL |
| `pair` | `pcon` | 2.1255 | 0.24565 | 60,000 | 5.118 | 6.249 | 5.518 | 6.649 | PROVISIONAL |
| `exact_ms8` | `en` | −7.0611 | 0.06533 | 60,000 | −6.265 | −5.964 | −6.159 | −5.858 | PROVISIONAL |
| `exact_ms8` | **`pmax`** | 2.0278 | 0.32017 | 60,000 | 5.928 | 7.402 | 6.449 | **7.924** | PROVISIONAL |
| `exact_ms8` | `pcon` | 2.0474 | 0.26210 | 60,000 | 5.240 | 6.447 | 5.667 | 6.874 | PROVISIONAL |
| `drift` | `en` | −6.1410 | 0.09164 | 15,000 | −5.025 | −4.603 | −4.875 | **−4.453** | PROVISIONAL |
| `drift` | **`pmax`** | 5.8995 | 0.43129 | 15,000 | 11.153 | 13.139 | 11.856 | **13.842** | PROVISIONAL |
| `drift` | `pcon` | 2.9880 | 0.33902 | 15,000 | 7.117 | 8.679 | 7.670 | 9.231 | PROVISIONAL |

Per-register bars (all nine, at L ∈ {31, 120, 240}, `keyskip1`), the `panel_max` cells, the
`skip_by_two`/`union`/`drift` mode cells and the four R17 geometries are in `calib19.json` and
are reachable through the API below.

### 10.0 L = 31 — the cell G1 and G2 are blocked on

Both lanes named this lane explicitly. Here is the answer for both, `exact` preset, L = 31,
M = 10⁶ wrong-key beam decodes (`I19:vecbeam.keyskip1+I2|*|L31`).

| statistic | μ | β | ESCALATE α=0.05 @ 8,192 / 10⁵ / 10⁶ | CLAIM α=0.01 @ 8,192 / 10⁵ / 10⁶ |
|---|---|---|---|---|
| `en` | −6.9023 | 0.14557 | −5.158 / −4.794 / −4.459 | **−4.921 / −4.557 / −4.222** |
| `pmax` | 2.1116 | 0.29923 | 5.697 / 6.445 / 7.134 | **6.184 / 6.933 / 7.622** |
| `pcon` | 1.9445 | 0.27514 | — | 5.816 / 6.505 / 7.139 |

**Answer to G2.** G2 reports its L = 31 null max over 8,192 trials is already **−5.550**. That
is expected and it is *not* a problem: at L = 31 the α = 0.01 family-wise bar over 8,192
decodes is **−4.921**, so a null max of −5.550 sits a comfortable 0.63 **below** the bar. The
mistake to avoid is comparing −5.550 to −5.5 and calling it a near-miss — at this geometry
−5.5 is a valid bar only out to **N = 136 decodes** (§3.1). Use −4.921, or −5.158 to escalate.

**Answer to G1 — the measured power of an L = 31 panel screen** (12 replicates per register,
correct key planted, `exact` preset; `out_power_L31.json`):

| register | median recovery | `en` power @ N=8,192 | **`pmax` power @ N=8,192** | `pmax` power @ N=10⁵ | `pmax` power @ N=10⁶ |
|---|---|---|---|---|---|
| EN_KJV | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| LP1_REAL | 1.00 | 0.83 | **1.00** | 1.00 | 1.00 |
| EN_MODERN | 1.00 | 0.83 | **1.00** | 0.92 | 0.92 |
| DE | 1.00 | 0.42 | **1.00** | 1.00 | 1.00 |
| LATIN | 1.00 | 0.00 | **1.00** | 0.92 | 0.92 |
| OE | 1.00 | 0.17 | **1.00** | 0.75 | 0.42 |
| CY | 1.00 | 0.08 | **0.92** | 0.42 | 0.25 |
| EN_HALFVOWEL | 1.00 | 0.25 | **0.83** | 0.42 | 0.33 |
| EN_NOVOWEL | 0.98 | 0.00 | **0.67** | 0.58 | 0.25 |
| RAND *(control)* | 0.55 | 0.00 | **0.00** | 0.00 | 0.00 |

**G1's screen is powered — but only as a screen, and only on `pmax`.** At a screening budget of
~10⁴ decodes the panel gives ≥ 0.83 power on eight of nine registers and 0.67 on the ninth,
with the negative control at 0.00. The `en` column is the warning: on the legacy English
statistic the same screen has power 0.00–0.42 for Latin, OE, Welsh, German and half-vowel
English at L = 31. **Screen on `pmax`, never on `en`, at this length.** Power decays fast with
N — by N = 10⁶ the marginal registers are back to 0.25–0.42 — so an L = 31 screen must be kept
*small* and used to shortlist for a longer-L confirmation, not to adjudicate on its own.

### 10.1 How to call it

```python
import sys; sys.path.insert(0, "liber-primus/analysis/round19/I3")
from nullcurve19 import threshold_for, threshold_contract, report

# the legacy statistic, bit-identical to benchmark/null.py — nothing changes
threshold_for(n_trials)
threshold_for(n_trials, segment_len)

# the Round-19 instrument
c = threshold_contract(n_trials=N_ROUND_ADJUDICATED, segment_len=120,
                       register="I19:driftbeam.drift+I2", statistic="pmax")
# -> {'escalate_bar': ..., 'claim_bar': ..., 'cell': ..., 'cell_status': ...,
#     'cell_n_null_decodes': ..., 'extrapolated': True/False}
```

Store the whole dict in the sweep header. **A number without its cell is not a threshold.**

### 10.1a Cross-lane reconciliation — three lanes measured this null independently

**The single most important agreement.** At L = 120, the per-decode 10⁻³ quantile of the
wrong-key **beam** null:

| lane | sample | null source | `en` @ 10⁻³ | `pmax` @ 10⁻³ |
|---|---|---|---|---|
| **I2** (`out_null.json`) | 8,000 | real LP2 L-windows, random key | −6.6396 emp / −6.6176 GPD | 4.2773 emp / 4.2694 GPD |
| **I3** (this lane) | **1,000,000** | uniform random ciphertext, random key | **−6.6133** | **4.3496** |

Two lanes, two different null sources, sample sizes differing by 125×: `en` agrees to **0.026**
and `pmax` to **0.080**. I2's matched-FP bars `t_pmax` = 4.28 / 4.67 / 5.23 at L = 120/240/400
are confirmed by this lane at L = 120. That is a real independent cross-validation of the
instrument, and it is the strongest single piece of evidence that the bars below are right.

**I2's warning about calibrating on random runes does not apply to this lane, and we agree on
the underlying point.** I2 measured the wrong-key beam null to be higher than a random-rune
null by +0.51 / +0.85 / +1.23 in `pmax` at L = 120 / 240 / 400, growing with L because the beam
gets to choose its best skip path. **Every curve published here is fitted on wrong-key beam
decodes**, not on random rune strings (`run_calibration._gen` draws a random ciphertext and a
random keystream and runs the full beam; the shuffle control draws real LP2 windows). No re-fit
is needed and nothing here is marked PROVISIONAL for that reason. This lane found the same
defect independently, from the other side, and it is the substance of §7.3 and
[`INTERFACE.md`](INTERFACE.md) R-I2-2: I2's *internal* `Panel.cal` standardisation uses a
random-rune null, so its **z scale** understates the decoder-output null by a factor of ~5 at
`keyskip1` and ~8 at `drift`. The bars below are unaffected because they are measured on the
decoder-output null directly; only the nominal z scale is misleading, and rule 7 below says so.

**I1's fit is 0.17–0.20 stricter than this lane's, and the evidence favours this lane's.**
I1 reports μ = −7.247, β = 0.0665 for `exact_auto`, against this lane's μ = −7.0890,
β = 0.06814 (M = 10⁶). The β's agree to 2.4 %; the μ's differ by 0.158, so I1's bar is a
near-uniform 0.17–0.20 stricter at every N (−5.563 vs −5.364 at N = 10⁹, α = 0.01). The
discriminating test is the directly observed quantile: I1's curve predicts the per-decode 10⁻³
quantile at **−6.788**, while I2 measured **−6.6396** on 8,000 decodes and this lane measured
**−6.6133** on 10⁶. I1's curve therefore sits ~0.17 below two independent direct measurements.
The mechanism is visible in this lane's own per-block table — β falls monotonically with block
size (0.125 → 0.087 → 0.068 → 0.062 at n = 10, 10², 10³, 10⁴), the ξ < 0 signature of §4 — so a
fit anchored on **two** block sizes, as I1's was, lands at a different (μ, β) pair than one
anchored on the resolved 10³ block. **Adopted: this lane's curve**, because its false-positive
rate is verified directly by G-CAL at M = 10⁶ and its quantiles match I2's. I1's is a
conservative cross-check: any CLAIM that clears this lane's bar by less than 0.20 should also
be checked against I1's, and this lane recommends that as a standing practice rather than a
tie-break.

**I1's cross-validation of G-BACKCOMPAT.** I1's independent block-maxima fit of the `keyskip1`
null (μ = −7.247, β = 0.0665) reproduces `benchmark/null.py`'s published DEFAULT_MU = −7.2517 /
DEFAULT_BETA = 0.0725 to 0.005 and 8 % respectively. Together with §2's measurement, **two
lanes using different methods have now independently confirmed the repo's zero-DOF two-point
constants.** G-BACKCOMPAT is not merely "the function returns the same number"; the number it
returns has been checked against fresh data twice.

**Other lanes' numbers that bear on the bars:**

- **G2** measured random data scoring **−4.51 / −4.82** under I1's drift presets. That is the
  same phenomenon as §5's `drift3` (−4.508) and `union2` (−5.565) rows, from a third lane and
  on different input. It is the clearest possible statement of why a permissive decode can
  never be judged against −5.5: **random data beats the historical confirm bar by a full
  score unit.**
- **G4** found its pre-registered control failed because the key-skip filter puts the rigid
  optimum at *planted phase + n_skips*, not at the planted phase, and concluded that a phase
  prefilter must keep a **band, not a point**. This lane blesses no prefilter, and that is
  deliberate: every bar here is calibrated on the *adjudicated* decode, so any prefilter in
  front of it changes the null of what reaches the beam and needs its own survival measurement
  (see §8.1 note 2 for R17's version of the same hole).
- **C2** measured composite prefilter × adjudicator power on real pads: **0.77 English, 0.23
  Latin, 0.00 Welsh, 0.022 half-vowel, 0.000 vowel-dropped.** Set against §7.1's adjudicator-only
  powers (1.00 / 1.00 / 1.00 / 1.00 / 0.67), the gap is the prefilter's, not the bar's.
  **Fixing the bar and the panel does not fix a lane that discards non-English candidates
  before the beam sees them.** Any Phase-2 lane running a prefilter must publish its own
  non-English survival rate; the bars here are conditional on the decode reaching the
  adjudicator.

### 10.1b Two statistics this contract does NOT cover, and what to do about them

- **`n_skips` (I1).** I1 found the inferred skip count is a **language-independent**
  discriminator — the correct key infers 418/418 exactly at full book, a wrong key infers 1537.
  If that separation holds under a null, it is worth more than any English statistic, precisely
  because it sidesteps the entire register axis this round exists to repair. **It has no null
  curve here and must not be thresholded until it does.** The re-run is cheap and is specified
  in §12: it needs a `n_skips` column added to `run_calibration._work`, then one 10⁶-decode
  pass per (L, preset). This lane recommends it as the highest-value single addition to the
  contract, and flags one hazard to test for: `n_skips` is an integer with a small range, so its
  null is discrete and a Gumbel bar is the wrong tool — use the exact empirical tail.
- **Recovery, when the decoder cannot track the register.** I1 insists recovery, not score, is
  the safe gate, and it is right for a *confirmation*. But I2 flagged that the beam still picks
  its skip path by **English** score, so EN_NOVOWEL recovers only 67–81 % of runes (this lane
  measures 0.80 at L = 120, 0.98 at L = 31). A recovery-based criterion must therefore be
  **register-conditional**: apply a high recovery gate (≥ 0.95) only for registers the decoder
  can track, and for EN_NOVOWEL and other lossy registers treat a `pmax` crossing as a
  **detection, not a decode** — escalate it to a targeted re-decode with that register's own LM
  driving the beam, rather than requiring readable plaintext from an English-driven path. A
  detection that fails a recovery gate the decoder was never able to pass is a false negative
  manufactured by the gate.

### 10.2 Seven rules Phase 2 must follow

1. **Pass decodes adjudicated, never candidates enumerated.** This is L7-C.3's error and §8.1
   shows every R17 lane that called `threshold_for` committed it.
2. **Adjudicate at a calibrated length** — 31, 120 or 240 (or 25/40/400 at beam_w 120). Outside
   those, `threshold_for` raises unless you pass `strict=False`, which labels the result
   `interpolated_from`.
3. > ### NEVER ADJUDICATE A PERMISSIVE DECODE AGAINST −5.5, OR AGAINST ANY `keyskip1` BAR.
   >
   > **Each decoder channel is adjudicated against its own bar. There are no exceptions.**
   > Under `drift` the `en` bar moves by **+1.38** and the `pmax` bar by **+6.21**. Three lanes
   > hit this independently — I1 (permissive shifts the wrong-key null +0.58 and the 10⁹ bar
   > +0.60), G2 (random data scores −4.51/−4.82 under drift presets, i.e. **above** −5.5), and
   > this lane (a wrong key on random ciphertext reaches `en` = −5.351 in 15,000 drift decodes,
   > §7.3). `nullcurve19.threshold_for` **raises** rather than substituting, and that behaviour
   > is deliberate and must not be worked around with `strict=False`.
   >
   > I1's own G-FP passes at λ ≥ 8 and **fails at λ ≤ 6** (at λ = 4, 11.3 % of wrong keys clear
   > −5.5), and it recommends **λ = 12** (margin 0.52–0.68) over λ = 8 (margin 0.14–0.19). This
   > lane's independent dose–response (§5) agrees on the direction and the ordering: λ = 8 costs
   > +0.507 of bar and λ = 6 costs +0.699, so the gap between "safe" and "unsafe" is about two
   > tenths of a score unit and λ = 12 is the right side of it. **Adopt λ = 12.** The `drift`
   > cells in §10 are measured at I1's shipped λ = 8; if the preset moves to λ = 12 they must be
   > re-run (INTERFACE R-I1-2), and the bar will come *down*, in Phase 2's favour.
4. **Claim on `pmax`, not `en`,** whenever the preset is `drift` — §7.2 shows `en`'s power
   collapses to 0.00 for four registers there.
5. **Run `exact`/`pair` and `drift` as two cells** and adjudicate each against its own bar. The
   two-test correction is 0.05 (`en`) / 0.30 (`pmax`) and buys both axes.
6. **`extrapolated: true` means the bar is beyond the sampled range** (N > M/50). Every `drift`
   bar at N ≥ 10⁶ is extrapolated 67× beyond its M = 15,000. G-CAL-X supports the
   extrapolation (52/52 within 1 SD) and §4 shows it errs conservative, but it is labelled.
7. **Do not read a `pmax` value against I2's nominal z scale, and do not use a per-decode bar
   for a sweep.** §7.3: the decoder-output null for `pmax` reaches 6.05 at `keyskip1` and 9.33
   at `drift`, against a random-rune null max of 1.163. Separately, I2's `t_pmax` = 4.28 (L=120)
   is a **per-decode** α = 10⁻³ bar — correct for the power comparison it was built for, and
   confirmed by this lane (§10.1a) — but applying it to a 10⁶-decode sweep would produce ~1,000
   false positives. I2's §4.3 guidance was explicitly pending this lane's number; **the §10
   table supersedes it for all sweep use.**

8. **On I2's G-SPEED failure: this lane agrees it protects nothing real, and says so on the
   record.** `adjudicate` costs 164 µs against a beam decode's ~134,300 µs — 0.12 %, so a
   4.79× adjudicator adds ~0.4 % to a sweep. Against that, the panel is what takes Welsh from
   0.08 to 1.00 and vowel-dropped English from 0.00 to 0.67 (§7.1). Reporting the failure
   rather than rewriting the gate was the right call, and the correct disposition is to accept
   the overrun with the arithmetic attached, not to relax the gate retroactively. The real
   speed constraint in Round 19 is I1's `drift` preset at **1.39 decodes/s/core** — four orders
   of magnitude larger, and the thing that actually bounds N and therefore the bar.

---

## 11. Proposed changes to `benchmark/null.py` (NOT made — this lane did not edit it)

Per the lane rules, these are proposals. All are additive; none changes a published number.

1. **Make `segment_len` do something, opt-in.** Add `length_correct=False`. When True, scale β
   by the measured law. Implementation and tests already exist in
   [`nullcurve19.py`](nullcurve19.py) — lift them. This is L7-C.4's follow-up #2, and it fixes
   the twelve-order-of-magnitude problem in §3.1.
2. **Add the measured constants next to the published ones, do not replace them.**
   `MEASURED_MU_L120 = -7.0890`, `MEASURED_BETA_L120 = 0.06814`, `MEASURED_M = 1_000_000`, with
   a one-line note that the published two-point solve agrees to 0.04–0.08 in the bar at every
   N (§2). Replacing them would break comparability for a gain smaller than the difference.
3. **Document that `FIXED_BAR = -5.5` has no statistical justification, and add
   `floor=None`.** §7.1 measures what it costs: Latin, German, Old English and half-vowel
   English go from 0.50–0.75 power to 0.83–1.00 when the floor is dropped, at the *same*
   verified α. Keep the floor as the default so nothing published moves; make it switchable and
   say what it is.
4. **Add the extreme-value shape note.** ξ ≈ −0.06 across 46 cells, all negative; the Gumbel bar
   is conservative by 0.07–0.56 over N = 10⁴–10¹⁰ (§4). That is a useful thing for a future
   reader to know before they add a fourth layer of conservatism.
5. **Make `report()` demand the adjudicated count.** Rename the parameter to
   `n_decodes_adjudicated` (keeping `n_trials` as an alias) and emit a warning when it exceeds
   a plausible throughput for the elapsed wall time. This is the cheapest possible guard against
   L7-C.3's error, which was committed in 4 of 4 R17 lanes.
6. **Point at `calib19.json`** from the module docstring, and say that a bar is a property of
   (null generator, transition relation, adjudicator statistic, segment length, beam width) —
   five things, not one.
7. **`.gitignore`**: add a Round-19/I3 block for `analysis/round19/I3/_qtab.npy` (4 MB) and
   `_lms.npz` (374 KB). Both are caches rebuilt automatically by `vecbeam.qtab()` and
   `registers.build_lms()`. `calib19.json` (1.2 MB) **should be committed** — it is the record,
   and it carries the block maxima needed to re-check every fit without re-running.

---

## 12. What was NOT covered, and the exact re-run that finalises it

**Covered:** 91 cells, ~9.6 × 10⁶ null decodes; 9 registers × 3 segment lengths; 9 transition
relations; 4 R17 geometries; 4 I1 presets × 13 I2 statistics; 2 panel-combination rules; a
shuffle-null control on the real ciphertext; 3 plants; 14 historical sweep stages re-derived.

**Not covered:**

- **M ≥ 10⁶ for 71 of 91 cells** — the reasons and the throughput numbers are in §9.1. Those
  bars are PROVISIONAL. They are not *wrong*; their false-positive rate is simply unverified at
  the pre-registered precision.
- **Segment lengths outside {25, 31, 40, 120, 240, 400}.** L = 100, 262 and 12,956 appear in
  §8 as extrapolations along the fitted law and are flagged.
- **Beam widths other than 120 and 400.**
- **Signs other than −1, and non-uniform key material.** The null used uniform random
  keystreams; a low-entropy or structured pad has a different null (L7-B.1 shows the decoder
  behaves differently on constant-byte runs).
- **I2's `pmax_ne` and the four language-agnostic statistics (`ioc`, `mds`, `h2`, `zl`)** are
  calibrated for `pmax_ne` only; `ioc`/`mds`/`h2`/`zl` have no null curve here. If Phase 2
  wants to threshold on them, they need cells.
- **Combinations of transition-relation axes.** Each mode was measured alone.
- **The `union<λ>` proxy reports the penalised score; I1's `permissive` reports the
  unpenalised one** (§5). The λ curve is a lower bound for I1's convention; the `driftbeam`
  cells are exact.

**The re-run that finalises this lane** — nothing else in Round 19 blocks on it, and the
PROVISIONAL bars are usable meanwhile:

```bash
cd liber-primus/analysis/round19/I3
python3 run_i1i2.py --stage i1 --preset drift     --L 120 --M 1000000   # ~200 core-hours
python3 run_i1i2.py --stage i1 --preset pair      --L 120 --M 1000000   # ~6 core-hours
python3 run_i1i2.py --stage i1 --preset exact_ms8 --L 120 --M 1000000   # ~3 core-hours
python3 run_calibration.py --stage registers --L 240 --M 1000000        # ~28 core-hours
python3 run_calibration.py --stage modes --M 1000000 --M2 1000000       # ~60 core-hours
python3 run_i1i2.py --stage r17 --L 400 --beam_w 120 --M 1000000        # ~9 core-hours
```

**The one addition worth more than any of those re-runs: a null curve for I1's `n_skips`.**
Add an `n_skips` column to `run_calibration._work` (I1's `beam_decode` already returns it), then
one 10⁶-decode pass per (L, preset). It is the only candidate statistic in Round 19 that is
language-independent, so it is the only one whose power does not depend on the register axis
this entire round exists to repair. Use the exact empirical tail, not a Gumbel bar — `n_skips`
is a small-range integer and its null is discrete.

**And the re-run that is *mandatory* if I1 or I2 change** — see [`INTERFACE.md`](INTERFACE.md)
§4. In short: any change to a `PRESETS` entry voids that preset's cells; any rebuild of
`I2/models/panel.npz` voids every `pmax`/`pcon`/`z:` cell; any change making `driftbeam`'s
returned `score` the *penalised* quantity voids every `en` cell.

**What reopens the bounds here.** A measured decoder-output-standardised panel (R-I2-2b), a
Phase-2 lane needing a segment length or beam width not in the grid, or a keystream family whose
null is not uniform-random-like. None of those is closed; they are simply unmeasured.

---

## 13. Trust anchor

```
BEFORE  python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5)
        python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
AFTER   python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5)
        python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
        python3 -m pytest analysis/round19/I3/test_i3.py -q -> 15 passed
```

## 14. Reproduce

```bash
cd liber-primus/analysis/round19/I3
python3 vecbeam.py                                                  # PREREG Q5 exactness gate
python3 run_i1i2.py --stage geq                                     # I1/vecbeam/skipdecode identity
python3 run_calibration.py --stage registers --L 31  --M 2000000    # per-register null curves
python3 run_calibration.py --stage registers --L 120 --M 1000000
python3 run_calibration.py --stage registers --L 240 --M 60000
python3 run_calibration.py --stage registers --L 120 --M 20000 --source shuffle
python3 run_calibration.py --stage modes --M 200000 --M2 12000      # permissiveness curve
python3 run_calibration.py --stage pit --L 120 --M 600000           # max-z vs min-p panel
python3 run_i1i2.py --stage i2panel --L 120 --M 1000000             # I2's actual statistics
python3 run_i1i2.py --stage i1 --preset drift --L 120 --M 15000     # I1's actual decoder
python3 run_i1i2.py --stage r17 --L 31 --beam_w 120 --M 300000      # R17's actual geometry
python3 plants.py                                                   # P1, P2, G-RECOVER
python3 ghonest.py                                                  # the retrospective
python3 summary.py                                                  # every table above
python3 -m pytest test_i3.py -q                                     # G-BACKCOMPAT + 14 more
```
