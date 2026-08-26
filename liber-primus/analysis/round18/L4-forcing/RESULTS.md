# Round 18 — Lane L4 (FORCING) — RESULTS

_Ledger item **C-02**, status `never-run` ("Proposed with a hard gate; no script and no result
anywhere"). Pre-registered in [`PREREG.md`](PREREG.md) before any test was run. Inherited hard gate
**p < 0.001**, Bonferroni-corrected over 21 pre-registered tests to **α_test = 4.762 × 10⁻⁵**._

## Headline

**One test fired, and it is not forcing — it is typography.**

The line-initial rune distribution of LP2 pages 0–54 is non-uniform at χ²(28) = **78.66**,
empirical p ≤ **5.0 × 10⁻⁶** against a size-matched null (asymptotic p = 1.06 × 10⁻⁶). That clears
the pre-registered gate by two orders of magnitude — a ciphertext-visible structural anomaly in LP2
that is not the anti-repeat filter, found with no key hypothesis at all.

It is then fully explained by a **greedy line-breaker running against variable glyph widths**. The
rune that straddles the right margin is length-biased into the next line's first slot — the
inspection paradox — and once the null is made layout-aware the same statistic sits at
**p = 0.177**. No forcing is required to produce it, and none is detectable once it is removed.

**No forcing signature survives.** All other 20 pre-registered tests are negative — including
56,376 keyless Gematria-Primus reads of the positional subsets, every one of which scores *below*
its own max-statistic null. The lane's
durable outputs are (1) a measured, externally-validated **glyph-width table for the 29 runes**
derived from the transcription itself, (2) the **layout-aware null** that any future acrostic or
positional attack on LP2 must use instead of a flat one, and (3) an honest **power curve** saying
exactly how much forcing would have had to be present for this detector to see it.

---

## 0. Instrument gate (run before anything else)

`parse_structure.py --selftest` reproduces, from the raw transcription and independently of the
existing rig:

| check | value | reference |
|---|---|---|
| runes, pages 0–54 | **12,956** | `PROBLEM.json` |
| identical to `lib_numchannel.unsolved()` | **True** | element-wise |
| pages / lines / words / `.`-units | 55 / 594 / 2,928 / 219 | — |
| immediate doublets | **86** | round17 published 86 ✓ |
| doublets crossing a line break | **4** | round17 published 4 ✓ |

Two counts in `PREREG.md` §2 were taken from a naive `re.split` before the parser existed and are
superseded here: **words 2,928** (not 3,316 — LP2 hyphenates words across line breaks, so a line
break is *not* a word break) and **`.`-units 219** (not 175 — a page break also opens a unit). No
threshold was changed; only the subset sizes.

---

## 1. Arm A — the literal C-02 uniformity detector

χ² goodness-of-fit of each positional subset's 29-bin rune histogram against the full-text
distribution, with an **exact** size-matched null (drawing k of 12,956 positions without
replacement makes the count vector multivariate hypergeometric in the full-text urn; the
with-replacement multinomial would have overstated the variance by 1/(1 − k/n)).
200,000 draws per subset ⇒ resolution floor 5.0 × 10⁻⁶.

| id | subset | n | χ² vs full text | p (empirical) | verdict |
|---|---|---:|---:|---|---|
| **A1** | **line-initial** | 594 | **78.656** | **≤ 5.0e-6** | **HIT** |
| A2 | line-final | 594 | 24.217 | 0.607 | NEGATIVE |
| A3 | word-initial | 2,928 | 18.225 | 0.706 | NEGATIVE |
| A4 | word-final | 2,928 | 26.003 | 0.214 | NEGATIVE |
| A5 | page-initial | 55 | 29.252 | 0.387 | NEGATIVE |
| A6 | page-final | 55 | 22.850 | 0.741 | NEGATIVE |
| A7 | sentence-initial | 219 | 47.718 | 0.0097 | NEGATIVE |
| A8 | sentence-final | 219 | 25.898 | 0.554 | NEGATIVE |
| A9 | line-second *(adjacency control)* | 594 | 40.110 | 0.043 | NEGATIVE |
| A10 | line-penultimate *(adjacency control)* | 594 | 32.262 | 0.206 | NEGATIVE |

Flat null for n = 594: mean 26.9, sd 7.2, 95th pct 39.7, max over 200,000 draws 74.0 — the observed
78.66 exceeds **every** null draw.

Per-rune signed z at line-initial position (largest first):
**EA +3.75, P +2.84, D +2.69, H +1.87** … **R −3.10, I −2.76, O −2.00, N −1.90, B −1.89.**
Diffuse across many runes, and *ordered by glyph width* — which is what §2 pursues.

Verdict as pre-registered: **A1 is a HIT at the inherited gate.** §2 is the confound analysis that
every hit has to survive; A1 does not survive it.

---

## 2. POST-HOC confound analysis — the hit is the inspection paradox

Declared post-hoc; it does not alter the Arm A result above. `confound_layout.py`.

LP2 breaks words across lines, so its line breaks are **not linguistic** — they are a greedy fill
against a fixed column width. Under a greedy fill the rune pushed to the start of the next line is
the one that *straddles* the margin, and a rune is length-biased into that role in proportion to its
glyph width:

> P(rune r begins a line) ∝ p(r) · width(r)

This predicts an excess of wide runes at line-**initial** position and **no matching effect at
line-final position** — exactly the observed A1/A2 asymmetry.

### T1 — recover glyph widths from the transcription alone

Least squares over the 539 width-limited lines (every line except each page's last), solving for the
31 token widths that make every full line the same physical extent:

| | coefficient of variation of line extent |
|---|---|
| equal-width model (rune count) | 0.1063 |
| **fitted-width model** | **0.0828** — 1.28× tighter |

Fitted relative rune widths, widest first:

```
EA 1.85  M 1.40  X 1.35  U 1.25  E 1.21  D 1.20  IA 1.20  Y 1.17  H 1.16  T 1.13
NG 1.09  C 1.08  G 1.04  J 1.03  P 0.99  OE 0.96  EO 0.94  W 0.86  S 0.86  O 0.82
N 0.80  AE 0.79  B 0.78  TH 0.77  A 0.75  R 0.74  F 0.71  L 0.71  I 0.37
separators:  '-' 0.32   '.' 1.82
```

**External validation (this is the load-bearing check).** Correlated against the advance widths of
`BabelStoneRunicBeorhtnoth.ttf`, shipped in `corpus/E-tooling/vendor/0x676f64__Cicada-3301/` and
entirely independent of the ciphertext:

> **corr(fitted width, BabelStone advance width) = +0.879**

The fit is recovering real glyph geometry, not overfitting. ᛁ (I), a single vertical stroke, is the
narrowest at 0.37; ᛠ (EA) is the widest at 1.85. That ordering was never given to the fit.

### T2 — the widths predict the A1 excess

- corr(fitted width, line-initial log-excess) = **+0.697**
- corr(BabelStone width, line-initial log-excess) = **+0.478**
- χ² of the line-initials against the **size-biased** model q ∝ p·w: **78.66 → 38.73** (28 df,
  p ≈ 0.085). A drop of 39.9 on 28 df from a model with no free parameters fitted to these counts.
- **Cross-validated** (widths fitted on odd lines only, evaluated on even lines' initials):
  43.62 → **31.04** (p ≈ 0.32). The prediction holds out of sample.

### T3 — reflow, and the layout-aware null (decisive)

The fitted widths drive a greedy line-breaker over the real token stream. Validated
**resynchronised per line** (an absolute-offset comparison is worthless: one early break shifts every
later one):

| reflow accuracy | value |
|---|---|
| exact line length reproduced | **53.5 %** of 594 lines |
| within ±1 rune | **82.5 %** |
| mean signed error | −0.04 runes |

From 31 fitted parameters, that is a working model of the book's typesetting.

Null: shuffle the runes (holding the separator positions), reflow, recompute the statistic.

| subset | n | observed χ² | layout-null mean | layout-null p95 | **p_layout** |
|---|---:|---:|---:|---:|---|
| **A1** line-initial | 594 | 78.66 | **65.60** | 91.55 | **0.177** |
| A2 line-final | 594 | 24.22 | 26.85 | 39.61 | 0.618 |
| A9 line-second | 594 | 40.11 | 26.62 | 38.89 | 0.038 |
| A10 line-penultimate | 594 | 32.26 | 26.73 | 39.35 | 0.210 |

The layout mechanism *alone* lifts the line-initial χ² from a flat-null mean of 26.9 to **65.6**, and
lifts none of the other three. The observed 78.66 is 0.90 sd above that layout null. **p = 0.177.**

> **Conclusion for A1: NEGATIVE for forcing.** The pre-registered detector fired, the pre-registered
> gate was cleared, and the cause is a greedy line-breaker with variable glyph widths. Reported this
> way round on purpose — the hit was real, the interpretation was not.

**This is a reusable correction, not a footnote.** Any future acrostic, positional or "first rune of
each line" attack on LP2 that compares against a flat null will manufacture p ≈ 1e-6 out of
typography. The layout-aware null in `confound_layout.py` is the one to use.

---

## 3. Arm C — rejection signature conditioned on position-within-line

The pre-registered sharp test, and the measurement nobody in this repo had made. Round 17 measured
only that 4 of 86 doublets cross a line boundary (a *scope* test at n = 86). This measures the
filter's **residual rate and its 29-bin difference channel** as a function of position-within-line.

### An instrument defect found and fixed mid-lane (recorded per Round 18 rule 2)

The first implementations of C1 and C4 used a permutation null that reshuffled the line-initial runes
among themselves. That null **destroys the anti-repeat filter at exactly the positions under test** —
and the filter is a *known H0 property*, established at ≥0.99 power by Round 17, not something this
lane is entitled to randomise away. The tell was unmistakable: C1 returned **p = 1.00000** and C4
returned p = 0.9995 with a null mean of 83.7 against 27–28 degrees of freedom. A null that destroys a
known H0 property cannot test anything; it only measures how strongly H0 holds.

Fixes actually applied:

- **C1/C2** now use an allocation null. H0 is *one* suppression s applied everywhere, so the
  expectation in bucket b is `n_b · collision_p_b · (1 − s_pooled)`, **not** `n_b · pooled_rate` —
  the per-bucket collision baseline differs slightly because the line-initial marginal is
  size-biased (§2). Statistic: G² of the observed doublet counts against those expectations; null:
  multinomial reallocation of the 86 doublets, 200,000 draws.
- **C4** is now computed on difference bins **1…28 only**. The d = 0 bin *is* the anti-repeat filter
  and is adjudicated by C1/C3; leaving it in guarantees a false alarm for any null that reshuffles
  initials. After the fix the C4 null mean is **28.03 on 27 df** — correctly calibrated.

### Results (all corrected)

| id | test | statistic | p | verdict |
|---|---|---|---|---|
| C1 | doublet rate by within-line position bucket | G² = 2.474 (3 df) | 0.4995 | NEGATIVE |
| C2 | doublet rate by within-word position bucket | G² = 3.802 (2 df) | 0.1616 | NEGATIVE |
| C3 | suppression, line boundary vs interior | see below | — | NEGATIVE |
| C4 | difference channel d = (xᵢ − xᵢ₋₁) mod 29, bins 1–28, boundary vs interior | χ² = 22.41 (27 df), null mean 28.03 | 0.7592 | NEGATIVE |
| C5 | MI(line-final rune, next line-initial rune) | 1.1163 bits vs null mean 1.1056 | 0.3704 | NEGATIVE |

Doublet rate by position-within-line (C1), the profile that did not exist before this lane:

| bucket | transitions | doublets | rate | independent-collision rate | implied suppression s |
|---|---:|---:|---:|---:|---:|
| p = 0 (crosses the line break) | 539 | 4 | 0.00742 | 0.03494 | **0.788** |
| p = 1 | 594 | 7 | 0.01178 | 0.03357 | 0.649 |
| p = 2–4 | 1,779 | 10 | 0.00562 | 0.03470 | 0.838 |
| p ≥ 5 | 9,989 | 65 | 0.00651 | 0.03457 | 0.812 |

Interior s = **0.8080**, boundary s = **0.7876** — a difference of 0.020 against a Round 17 reference
of 0.8075. Flat, as a memoryless unscoped filter must be. C2's word-boundary profile is likewise
flat (s = 0.768 / 0.877 / 0.795, p = 0.16).

### Arm C's honest power limit — this arm is weak, by construction

The boundary bucket has only 539 transitions at a ~0.7 % residual rate, so the Wilson 95 % interval
on the boundary suppression is **s ∈ [0.458, 0.917]**. Computing the detectable band explicitly
(two-proportion normal, 80 % power, two-sided):

| α | Arm C detects a boundary suppression only if… |
|---|---|
| **4.762e-5** (pre-registered) | s ≤ **−0.712**, i.e. a **71 % *excess*** of boundary doublets over the independent rate. A deficit is **never** detectable, not even a total ban (s = 1). |
| 0.05 (for reference only) | s ≤ **+0.158** |

So Arm C excludes only a *gross* excess-doublet signature at line starts. **A forcing scheme that
resolved its conflicts by re-rolling — the deficit direction — is invisible to Arm C at any α, at
this sample size.** That is a power limit, not a soundness one, and it is the single clearest
statement of what this lane does not cover. C4 (which uses all 539 boundary transitions across 28
bins rather than only the 4 doublets) is the more powerful arm and is likewise flat.

---

## 4. Arm B — the subsets read as a message

Arm A asks whether a subset is distributionally odd. Arm B asks the stronger question the original
C-02 proposal never posed: **does the subset say anything.** Six families, each swept over 232
Gematria-Primus variants per read — forward/reverse × identity/Atbash × 29 Caesar shifts ×
keep/drop-F (the interrupter convention; the keyless analogue of the skip-aware beam, which is a
*keyed* instrument and so not applicable to a keyless acrostic). Scoring is on rune indices mapped
through the Gematria Primus, never on a re-parsed string (AGENTS.md §5).

Multiplicity inside a family is handled exactly, by a **max-statistic null**: 400–1,000 replicates
in which the identical variant sweep runs on size-matched draws from the ciphertext's own positions,
taking the same maximum. The pre-registered gate is a three-part conjunction — beat every null
replicate, beat the Gumbel bar fitted to them at α_test, and be reported against
`benchmark/null.py: threshold_for(n_variants)`.

### Positive control (instrument gate)

A real English acrostic planted in a 594-rune line-initial sequence:

| plant | best score | best variant | null max | bar | recovered |
|---|---:|---|---:|---:|---|
| plaintext, shift 0 | **−4.372** | fwd/id/keepF/+0 | −6.959 | −6.806 | **yes** |
| plaintext, shift 7 | **−4.372** | fwd/id/keepF/+22 | −7.002 | −6.805 | **yes** |

The pipeline recovers a planted message *and* the shift that hides it. Its silence is therefore
meaningful.

### Results

| id | family | reads | variants | best score | best variant | null max | bar | verdict |
|---|---|---:|---:|---:|---|---:|---:|---|
| B1 | line-initial sequence (594) | 1 | 232 | −7.115 | rev/id/keepF/+10 | −6.968 | −6.806 | NEGATIVE |
| B2 | per-page acrostic | 55 | 12,470 | −3.513 | rev/id/keepF/+19 | −2.448 | −0.953 | NEGATIVE |
| B3 | diagonals (main + anti, per page) | 108 | 24,882 | −2.730 | rev/atb/keepF/+2 | −2.448 | −1.061 | NEGATIVE |
| B4 | first rune of every N-th line, N = 2…12, all phases | 77 | 17,864 | −5.838 | rev/atb/dropF/+11 | −5.558 | −5.150 | NEGATIVE |
| B5 | page-initial (55) and page-final (55) | 2 | 464 | −6.374 | fwd/id/dropF/+26 | −5.695 | −5.296 | NEGATIVE |
| B6 | word-initial and word-final (2,928 each) | 2 | 464 | −7.260 | rev/id/dropF/+11 | −7.200 | −7.107 | NEGATIVE |

**All six families NEGATIVE, and in every single one the observed maximum is BELOW its own null
maximum.** Not "close but under the bar" — under the noise. 56,376 keyless reads of LP2's positional
subsets, and not one of them is even as English-like as the best of a few hundred random draws of the
same runes.

**Read B2 and B3 carefully — they are the trap.** Their best reads score −3.51 and −2.73, which by
the repo's historical −5.5 habit would look like screaming hits. They are not: those families read
**very short strings** (a page has 4–13 lines, so a per-page acrostic is ~12 runes ≈ 15 letters ≈ 12
quadgrams) across ~12,000–25,000 variants, and the *null for that same procedure* peaks at −2.448.
The observed maxima are **below** their own nulls. This is AGENTS.md §4 lesson 3 in miniature — a
fixed bar is invalid at large variant counts — and it is why every family here is adjudicated against
its own max-statistic null rather than against a number.

B1 is the family the whole lane is aimed at, and it is the flattest of all: the 594-rune line-initial
sequence scores **−7.115**, *below* its own null max of −6.968 and barely above the null mean of
−7.199. The line initials of LP2 are, as a message, indistinguishable from a random draw of 594 of
its own runes.

---

## 5. Positive control and power curve — MANDATORY, and the most important table here

`control_power.py`. Round 18 rule 2: a null from an unvalidated instrument is not a negative.

### Generator, validated before use

Synthetic streams are uniform draws under a **memoryless, unscoped, lag-1 anti-repeat rejection
filter at s = 0.8075** — the model Round 17 (D-01) established at ≥0.99 power. The separator pattern
is LP2's own, and the streams are **laid out by the same greedy line-breaker with the same fitted
glyph widths**, so the synthetic carries the identical inspection-paradox size bias at line-initial
position. Without that the control would be measuring power against a straw null.

| | synthetic (20 streams) | LP2 |
|---|---|---|
| doublet rate | 0.006719 ± 0.000614 | **0.006638** |
| IoC × N | 0.99991 | 1.000 |

Independent corroboration of §2: the layout-aware null built on **purely synthetic, forcing-free**
streams has mean **64.68**, sd 14.62 — statistically indistinguishable from the null built by
reflowing the **real shuffled** ciphertext (65.60, sd 14.48). Two different routes to the same
number, neither of which contains any forcing.

### Forcing mechanisms planted (both, because they differ in what they leave behind)

- **M1 "assign"** — write the wanted rune unconditionally. Where it collides with the previous rune
  it creates a doublet, so Arm C can in principle see it as an *excess*.
- **M2 "filter-wins"** — write the wanted rune unless it collides, in which case the anti-repeat
  predicate wins and the natural draw stays. The boundary doublet rate is untouched.

Message: a fixed 594-rune phrase (`THEPRIMESARESACRED…BELIEVENOTHING`) through `keyword_to_indices`.
Fraction of the 594 lines forced = **f**. 200 replicates per cell, 2,000 null streams for the
critical values.

Critical values at α_test = 4.762e-5: **D_flat 67.05** (χ²(28) asymptotic), **D_layout 137.95**
(moment-matched gamma on the 2,000 layout-null draws), **D_C1 18.08**.

### The curve (detection rate over 200 replicates)

| mech | f | **D_flat** (literal C-02) | **D_layout** (honest) | **D_C1** (Arm C) | Arm B best B1 score |
|---|---:|---:|---:|---:|---:|
| M1 assign | 1.00 | 1.000 | **1.000** | 0.765 | −4.367 |
| M1 assign | 0.80 | 1.000 | **1.000** | 0.535 | −5.424 |
| M1 assign | 0.60 | 1.000 | **1.000** | 0.255 | −6.183 |
| M1 assign | 0.40 | 1.000 | 0.595 | 0.035 | −6.674 |
| M1 assign | 0.30 | 0.965 | 0.045 | 0.010 | −6.902 |
| M1 assign | 0.20 | 0.580 | 0.000 | 0.000 | −6.988 |
| M1 assign | 0.10 | 0.315 | 0.000 | 0.000 | −7.014 |
| M1 assign | 0.05 | 0.335 | 0.000 | 0.000 | −7.081 |
| M1 assign | **0.00** | **0.490** ← | **0.000** | 0.000 | −7.024 |
| M2 filter-wins | 1.00 | 1.000 | **1.000** | 0.000 | −4.509 |
| M2 filter-wins | 0.80 | 1.000 | **1.000** | 0.000 | −5.340 |
| M2 filter-wins | 0.60 | 1.000 | **1.000** | 0.000 | −6.246 |
| M2 filter-wins | 0.40 | 1.000 | 0.460 | 0.000 | −6.686 |
| M2 filter-wins | 0.30 | 0.955 | 0.060 | 0.000 | −6.897 |
| M2 filter-wins | 0.20 | 0.570 | 0.000 | 0.000 | −7.032 |
| M2 filter-wins | 0.10 | 0.300 | 0.000 | 0.000 | −7.021 |
| M2 filter-wins | 0.05 | 0.295 | 0.000 | 0.000 | −7.060 |
| M2 filter-wins | **0.00** | **0.490** ← | **0.000** | 0.000 | −7.024 |

### What the curve says

1. **The detector C-02 literally specified is broken on this data.** At f = 0 — no forcing whatever,
   just LP2's own geometry — D_flat fires **49.0 %** of the time at α = 4.762e-5. Its nominal false
   positive rate is 1 in 21,000; its measured one is 1 in 2. Had this lane run the proposal as
   written and stopped at Arm A, it would have reported a forcing discovery, and it would have been
   a greedy line-breaker. LP2's own observed statistic, 78.66, is exactly what that broken detector
   produces on forcing-free data.
   *(D_flat's power is also non-monotone — 0.490 at f = 0, dipping to ~0.30 at f = 0.05–0.10 before
   climbing. Light forcing partially cancels the width-driven size bias. A detector whose power dips
   below its own false-positive rate as the signal is switched on is not measuring the signal.)*

2. **The layout-corrected detector is properly calibrated and this is the lane's real bound.**
   D_layout: false-positive rate **0.000/200** at f = 0, power **1.000** at f ≥ 0.60 under both
   mechanisms, **f80 = 0.60**. Power collapses between f = 0.60 and f = 0.30 (1.000 → 0.595 → 0.045).

   > **The bound this lane establishes: if the author forced ≥ 60 % of the 594 line initials, we
   > would have seen it with probability 1.000, and we do not see it. Below f ≈ 0.40 this detector
   > is blind, and at f ≤ 0.20 it is completely blind.**

3. **Arm C's asymmetry is confirmed exactly as pre-registered.** D_C1 reaches 0.765 at f = 1.00 under
   **M1** and **0.000 at every f under M2**. Arm C can only ever see the mechanism that lets doublets
   through, and even then only at near-total forcing. This is the empirical version of the analytic
   power bound in §3: the deficit direction is invisible.

4. **Arm B requires more than distributional forcing — it requires a message.** The planted-English
   control recovers at −4.372 against a bar of −6.806 (§4), and the B1 score climbs monotonically
   with f from −7.02 to −4.37. So Arm B would have found a *meaningful* forced acrostic at
   f ≳ 0.6–0.8; it is not sensitive to forcing that spells nothing.


---

## 6. Coverage, and what is not covered

Per Round 18 rule 6 and AGENTS.md §7, read this section rather than the verdicts. The machine-readable
form is `ledger.json`.

### Covered

- **Object:** 12,956 runes / 55 pages / 594 lines / 2,928 words / 219 sentence units, pages 0–54.
  Geometry independently re-derived from the raw transcription and cross-checked against
  `lib_numchannel.unsolved()`, and against Round 17's 86 doublets / 4 line-crossing doublets.
- **Arm A:** 10 positional subsets, χ² against both the full-text distribution and flat uniform,
  200,000 exact size-matched draws each.
- **Arm B:** 6 families × 232 Gematria-Primus variants per read (forward/reverse × identity/Atbash ×
  29 Caesar shifts × keep/drop-F), covering the 594-rune line-initial sequence, 55 per-page acrostics,
  108 per-page main and anti diagonals, 77 every-N-th-line-initial subsequences for N = 2…12 at every
  phase, the 55-rune page-initial and page-final strings, and the 2,928-rune word-initial and
  word-final strings. Max-statistic nulls running the identical sweep.
- **Arm C:** doublet residual rate and the 29-bin difference channel conditioned on
  position-within-line and position-within-word; suppression with Wilson intervals; MI between each
  line-final rune and the next line-initial rune.
- **Two durable by-products** that outlive the verdict: a 29-rune **glyph-width table** recovered
  from the transcription and externally validated (corr +0.879 with BabelStone Runic), and a
  **validated greedy line-breaker model** of the book's typesetting (53.5 % exact, 82.5 % within ±1).

### Not covered — the concrete conditions that reopen this

1. **Arm C is blind in the deficit direction, at any α.** 539 boundary transitions at a ~0.7 %
   residual rate detect a boundary suppression only at s ≤ −0.712 (a 71 % *excess*); no deficit is
   detectable, not even a total ban on boundary doublets. Confirmed empirically: D_C1 power is
   **0.000 at every f** under the filter-wins mechanism. The only fix is more boundary transitions —
   e.g. pooling LP1's runic pages.
2. **Weak forcing is masked by typography.** D_layout's f80 = **0.60**; below f ≈ 0.40 it is largely
   blind and at f ≤ 0.20 it is blind. Forcing on a *minority* of lines remains untested.
3. **Subsets not enumerated here:** column-wise readings across pages, ornament-relative positions,
   per-page rune-index arithmetic, and any positional set defined by the 47 catalogued ornament
   bands — that is lane **L3**'s ground and it should be re-run through the layout-aware null.
4. **Non-rune-valued forcing.** This lane forced *rune identity*. Forcing of word lengths, line
   lengths, or punctuation placement — a channel an OTP cannot protect — is untouched here.
5. **English-only scoring.** Arm B used the quadgram scorer. A forced acrostic in another language,
   in digits, or in prime values would not have been seen. Same limitation lane **L7** is auditing.
6. **The transcription's line breaks are load-bearing.** Every number in §2 and §3 conditions on the
   krisyotam line breaks being the book's real ones. A from-scratch per-rune re-read
   (`handoff/PARKED.md`) would independently confirm both the geometry and the glyph-width table —
   and the width table gives that re-read a new, cheap consistency check it did not have before.
7. **The book's own font was never identified.** corr +0.879 with BabelStone Runic is supportive, not
   decisive. Measuring real glyph advance widths off the 400-DPI renders would settle §2 outright and
   is a cheap item for lane **L1/L3**.

### Escalation

Nothing was handed to `liber-primus/verify_solution.py --key-module`, because no candidate cleared its
bar: Arm A's only hit is distributional rather than a decode, and no Arm B family exceeded its
max-statistic null. The oracle was nevertheless run in this lane's environment and reports
**SELF-TEST: PASS** (accepts a known-good key, rejects a wrong one at −7.294 vs a −5.500 bar), so the
escalation path is live for anyone who extends this work.

### Reproduce

```bash
cd liber-primus/analysis/round18/L4-forcing
python3 parse_structure.py            # instrument gate: 12,956 runes, 86/4 doublets
python3 armA_uniformity.py 200000     # Arm A
python3 confound_layout.py 5000       # the typographic confound + layout-aware null
python3 armC_rejection.py 200000      # Arm C
python3 armB_message.py 1000          # Arm B (checkpoints per family)
python3 control_power.py 200 2000     # positive control + power curve
```

---

## 7. Aiming Test (`liber-primus/ARMADA-DOCTRINE.md` §1)

The doctrine was written 2026-08-26, after this round, and binds from Round 19. Answered here
anyway, because it is the right shape for a results file and because two of its findings bear
directly on this lane's limits.

**Q1 — What would a hit look like, and would this instrument recognise it?** Answered by §5, not by
argument. Forcing was planted in the shape believed — line initials, both plausible sampler
resolutions — and the pipeline emits it at power 1.000 for f ≥ 0.60. The test also found the
*opposite* failure the question is meant to catch: the literal C-02 detector recognises a hit
49 % of the time when there is no hit at all.

**Q2 — What measured fact raises this family's prior?** `round17/SYNTHESIS.md` §2 (item D-01): the
anti-repeat filter is machine-applied at ≥0.99 power. That is a *measured* demonstration that the
author wrote code enforcing a ciphertext-level predicate, which is what makes "did they enforce a
second one" a real question rather than a completeness ritual.

**Q3 — Is the space bounded?** Yes, and finite: 594 line initials, 55 page initials, 2,928 word
initials, 219 sentence initials — every one enumerated, no sampling. This is a category-1 object
under R5 (a finite, human-checkable object), and it needs no key hypothesis at all.

**Q4 — The three conditionals this negative carries.**
1. *Key space* — **none**. This lane is keyless; that is its whole point, and it is the one axis on
   which this negative is unconditional.
2. *Decoder transition model* — not applicable to Arms A and C, which read raw ciphertext symbols
   and never decode. It **does** bind Arm B, whose 232 variants are substitution-class reads
   (shift / Atbash / reversal / interrupter-drop) and nothing else.
3. *Adjudicator register* — **English only**, via the quadgram scorer. Lane L7-A measured this
   repo-wide: handed a correct key the adjudicator scores Latin at power 0.33 and vowel-dropped
   English at 0.00. A forced acrostic in Latin, Old English or an abbreviated orthography would
   have been missed by Arm B. Arms A and C are register-free and do not carry this conditional.

**Q5 — Kill condition.** Declared as: if the positive control failed to recover planted forcing at
f = 1.00, the lane reports no negative at all (`PREREG.md` §4). It did not fire — power at f = 1.00
is 1.000 for both detectors and both mechanisms.

**R2 (value = coverage × power).** Both reported: coverage in §6, power in §5. The lane's honest
value statement is one sentence — *line-initial forcing of ≥ 60 % of lines is excluded at power
1.000; below f ≈ 0.2 nothing is excluded.*

**R3 (language-agnostic statistics).** Arms A and C are distribution- and register-agnostic by
construction and their statistics are persisted in full in the results JSON. Arm B is English-only
and is flagged as such in §6.
