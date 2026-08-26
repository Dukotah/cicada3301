# I3 — NULLS & THRESHOLDS — pre-registration

_Round 19, Phase 0 (blocking). Written **before** any null statistic was measured.
Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

> Only two things were measured before this file was written, both of them costs and
> neither of them a statistic: (a) the trust anchor was run (`validate.py` 5/5,
> `pytest benchmark/` 8 passed), and (b) `skipdecode.beam_decode` throughput was timed
> (25.4 decodes/s at L=120, beam_w=400, single core) in order to size the experiment.
> No score distribution, no null maximum and no threshold had been computed.

---

## 0. What this lane is for

`benchmark/null.py: threshold_for(n_trials, segment_len)` is the repository's only
scale-corrected bar. It is calibrated for **exactly one statistic** — `lp.score.Quadgram.
score_norm` of a `beam_decode(beam_w=400, max_skip=3)` output on an ~L=120 segment — and
Round 18 L7-C showed it is a zero-degrees-of-freedom two-point solve, circular with the
sweep it adjudicated, and that it does not transfer across segment length (β ∝ 1/√L).

Round 19 changes **both** the decoder and the adjudicator:

- **I1** widens the beam's *transition relation*. A permissive transition relation searches
  a strictly larger path space per decode, so the maximum of the null over paths rises.
  An unchanged bar under a wider transition relation **manufactures false positives**.
- **I2** replaces the single English score with a **max over a 9-register panel**. A maximum
  over 9 correlated statistics has a higher null than any one of them, and the registers'
  raw score scales are not commensurable, so a naive `max` is not even a well-defined test.

Round 19's entire history-of-this-puzzle risk is that it converts a *power* problem
(Round 18's finding) into a *false-positive* problem, which is strictly worse: every false
claim ever made about Liber Primus is a decode that "looked English".

## 1. The Aiming Test (doctrine §1)

**Q1 — What would a hit look like, and would *this* instrument recognise it?**

A "hit" for a calibration lane is a **mis-calibration**: a stated bar whose true exceedance
probability differs from its nominal α. The recognizer is built and planted before the
search, in three forms:

1. **Synthetic-Gumbel plant.** Draw 10⁶ variates from a Gumbel with *known* (μ, β), hand
   them to the fitter, and require it to recover μ within 0.02 and β within 5 %. If the
   fitter cannot recover a distribution it was handed, nothing downstream means anything.
2. **Deliberately mis-calibrated bar plant.** Take a bar known to be wrong by a stated
   amount (the current `threshold_for` constants applied at L = 31, which L7-C.4 measured
   as ~2× too tight in β) and require **G-CAL to FAIL on it**. A gate that can only pass is
   decoration (doctrine §4.2, `benchmark/README.md`).
3. **Correct-key plant.** `benchmark/plant.py` with a known key, decoded with that key,
   scored under the new panel — required to clear the new bars (G-RECOVER).

**Q2 — What measured fact raises this family's prior above the flat rate?**

Not a prior on the *cipher* — this lane makes no cipher claim — but on the *defect*. Four
measurements, all with file paths:

- `round18/L7-redteam/RESULTS.md` §C.3 — `DEFAULT_MU`/`DEFAULT_BETA` are the exact solution
  of two equations in two unknowns anchored on two single order statistics from **B-04's own
  run**, then used to adjudicate B-04. Degrees of freedom: **0**. SE(β) = 20.5 % relative.
- `round18/L7-redteam/RESULTS.md` §C.3 — 3 of 9 recorded sweep maxima breach the 3-SD
  trigger (R17 P0/P1/P2 at −12.0 to −12.8 Gumbel SD).
- `round18/L7-redteam/RESULTS.md` §C.4 — the constants **do not transfer across segment
  length**; measured β ratios follow 1/√L (β(31)/β(120) = 2.00 measured vs 1.97 predicted).
  R17's headline −5.679 was a **31-rune** score compared against a 120–400-rune bar, and a
  shuffle null at L = 31 reached −5.681 in 400 draws.
- `round18/L7-redteam/RESULTS.md` §A.1 — the register panel I2 is building spans scores from
  −3.77 (EN_KJV) to −7.60 (EN_NOVOWEL) on the **correct key**. Nine statistics on scales
  that differ by 3.8 units cannot be combined by a raw `max`.

**Q3 — Is the space bounded, and by what?**

Bounded and **enumerable**. The calibration grid is a finite product:

```
registers  ∈ {EN_QUAD, EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY,
              EN_HALFVOWEL, EN_NOVOWEL}                       (10, of which EN_QUAD
                                                               is the legacy statistic)
segment_len ∈ {31, 120, 240}                                   (3)
modes      ∈ {keyskip1, skip_by_two, drift1, drift2, drift3, union_λ}   (≤ 6)
panel modes ∈ {rescore, per-register-decode}                   (2)
```

360 cells maximum. The lane enumerates the cells it can afford at the pre-registered sample
size and **names every cell it could not**, marking those PROVISIONAL. Sampling within a
cell is i.i.d. from the null generator, so the coverage fraction inside a cell is 1.0 by
construction; only the *tail extrapolation* is inferential and it is labelled as such.

**Q4 — What are the three conditionals the negative will carry?**

This lane publishes thresholds, not negatives, but the thresholds inherit the same three
conditionals and every published bar is tagged with all three:

1. **key space** — the null generator: uniform random rune "ciphertext" and uniform random
   keystream (the histogram-preserving shuffle null of the real LP2 stream is measured as a
   cross-check at L = 120, and any divergence is reported).
2. **decoder transition model** — the `mode` label. A bar computed under `keyskip1` is
   **invalid** under `drift2` and the API refuses to return it silently.
3. **adjudicator register** — the `register` label, plus `statistic='panel_max'` for the
   multiple-comparison case.

**Q5 — What single observation makes this lane abandon its approach at 10 % of budget?**

The lane's throughput depends on a vectorised re-implementation of `beam_decode`.
**Kill condition:** if the vectorised engine does not reproduce
`skipdecode.beam_decode(beam_w=400, max_skip=3)`'s returned `score` to within 1 × 10⁻⁹ on
**200/200** independent random (C, K) cases at each of L ∈ {31, 120, 240}, the fast path is
abandoned at once. Fallback: sample with the reference instrument at whatever n the budget
allows, publish nothing above n/50 in trial count without an EXTRAPOLATED tag, and mark
every affected cell PROVISIONAL. Checkpoint: **before any null cell is run.**

---

## 2. Hypothesis

**H₀ (the thing being assumed and tested, not the thing being hunted):** for each
(register, mode, segment_len) cell, the maximum of N i.i.d. null `score` draws is
Gumbel-distributed with cell-specific (μ, β), so that

    threshold(N, α) = μ + β·(ln N − ln(−ln(1−α)))

**H₁ (the alternative this lane is powered to detect):** the Gumbel form is wrong in the
upper tail for at least one cell — specifically that the score is bounded above (it is: a
perfect English decode is ≈ −2.2) and therefore the true extreme-value family is **Weibull**
(ξ < 0), which would make the Gumbel bar *anti-conservative* at large N. This is tested
explicitly by fitting a GEV with free shape ξ to block maxima and testing ξ = 0.

## 3. Instrument

- Null generator: uniform random rune ciphertext + uniform random keystream, plus a
  histogram-preserving shuffle null on the real LP2 unsolved stream as cross-check.
- Decoder: a **numpy-vectorised** re-implementation of `skipdecode.beam_decode`, gated by
  Q5's exact-reproduction test, extended with the transition-relation modes above.
- Adjudicator: the repo's `lp.score.Quadgram.score_norm` (legacy cell, must be bit-identical)
  plus rune-space trigram LMs per register, built by
  `round10b/B6-non-english-plaintext/detectors.build_trigram` over the corpora
  `round18/L7-redteam/a1_scorer_language.build_panels` already assembled.
- Fitters: block-maxima GEV (MLE, scipy), peaks-over-threshold GPD, and the repo's own
  two-point order-statistic solve, reported side by side.

## 4. Positive control

The three plants of Q1, all run before any cell is published.

## 5. Null

The null *is* the deliverable. The control on the null is that a **shuffle null of the real
ciphertext** and a **uniform-random null** must agree in fitted β to within 25 % at
L = 120 under `keyskip1`/EN_QUAD; if they do not, the uniform null is not a valid stand-in
and every cell is re-run on shuffle nulls at reduced n and marked PROVISIONAL.

## 6. Pre-registered gates

Stated now, evaluated later, not edited after results. Any change appears as a dated
addendum below.

### G-CAL — the bar means what it says

For each (register, mode, segment_len) cell published:

- Draw **M ≥ 1 × 10⁶** null decodes.
- Partition into **m = ⌊M/n⌋ disjoint blocks** at block sizes n ∈ {10, 10², 10³, 10⁴}.
- For each n, compute the empirical fraction of blocks whose maximum exceeds the published
  `threshold_for(n, …, α)`.
- **PASS** requires |p̂/α − 1| ≤ 0.20 at **every block size n for which the expected
  exceedance count m·α ≥ 50** (i.e. binomial SE ≤ 14 %, so a 20 % tolerance is a real test
  and not a coin flip). Block sizes with m·α < 50 are reported but not gating.
- Cells that cannot reach M = 10⁶ are published **PROVISIONAL** with their actual M, and
  the lane names them explicitly in RESULTS §"could not reach".
- **Extrapolation tag.** Any threshold quoted at N > M/50 is labelled **EXTRAPOLATED** and
  carries the out-of-sample check of §G-CAL-X below. This is the Round 10b L5-seed32 failure
  mode (`round10/L5-seed32/RESUME.md` line 82: a pre-registered −12.5 bar that "does not
  survive to the completed sweep's N") and it is the specific thing this tag exists to stop.

### G-CAL-X — the extrapolation is checked out of sample

Fit (μ, β) using **only** block maxima at n ≤ 10³. Predict the mean block maximum at
n = 10⁴ and n = 10⁵. **PASS** if the observed mean block maximum lies within **1.0 Gumbel SD**
(= 1.0 · βπ/√6) of the prediction at both sizes, in every cell where n = 10⁵ blocks exist.
This is the check `null.py`'s constants never had (L7-C.3: zero degrees of freedom).

### G-RECOVER — the correction does not kill the power the other lanes bought

A planted correct key must still clear the new thresholds at the powers I1 and I2 report.
Concretely, using `benchmark/plant.py` at L = 120, key family `sha256_ctr(seed=CICADA3301)`,
mechanism `skip`, 12 replicates per register:

- **PASS** if, for every register whose L7-A.1 measured correct-key power under the **old**
  −5.5 bar was ≥ 0.33, the median correct-key statistic clears the **new** panel bar at
  N = 10⁶ and α = 0.01.
- If it does not, the lane reports the **exact power loss in percentage points per register**
  and states the tradeoff as a finding. Per the task brief, a conservative correction that
  costs power is a real result and is published as one, not hidden. A quantified FAIL here
  is an acceptable outcome; an unquantified one is not.

### G-BACKCOMPAT — the ledger stays comparable

`threshold_for(n)` and `threshold_for(n, L)` must return **bit-identical** values to the
current `benchmark/null.py` for the English/keyskip1/`score_norm` cell, for
n ∈ {2, 200, 10³, 10⁴, 10⁵, 10⁶, 10⁷, 10⁸, 10⁹, 10¹⁰, 3.13×10⁸} and for every `alpha`,
`mu`, `beta`, `floor` keyword the current signature accepts. **PASS** requires 0 differences
and the 8 existing `benchmark/` gates still passing after the lane's code is importable.
New behaviour is reachable **only** through the new keyword arguments.

### G-HONEST — the retrospective

Re-derive the bar each of Rounds 13, 16 and 17 *should* have used at its own trial count,
segment length and decode count, and tabulate it against the bar each actually used.
**PASS** = the table is published with every discrepancy, in both directions, including any
case where the repo was **stricter** than necessary (which costs power and is equally a
finding). This gate cannot "fail" on its content; it fails only if the table is not produced
or omits a sweep.

### G-PANEL — the effective test count is estimated, not assumed

The panel-max correction must be an **empirical** estimate of the effective number of
independent tests M_eff, with at least two independent estimators agreeing to within a factor
of 1.5:

1. the **shift estimator** — M̂_eff = exp((μ_panel − μ_single)/β_single) from the fitted
   panel-max and single-register null curves;
2. an **eigenvalue estimator** on the 9 × 9 null correlation matrix (Li & Ji / Cheverud form).

A naive Bonferroni (M_eff = 9) is reported for contrast and explicitly **not** used.
**PASS** = both estimators computed, ratio ≤ 1.5, and the adopted value justified in writing.

## 7. Family-wise error target for Round 19 (pre-registered)

Committed now, defended in RESULTS:

- **Round-wide FWER target α_round = 0.01** over the union of every decode Round 19
  adjudicates, across all lanes. Rationale committed in advance: this project's failure mode
  is false claims, its verdicts are archived permanently, and the union bound's
  conservatism is the safe direction for a negative (L7-C.6 makes the same argument).
- **Two-tier bars.** Tier 1 **ESCALATE** at per-lane α = 0.05 — generates candidates for
  human/secondary inspection, never a claim. Tier 2 **CLAIM** at round-wide α_round = 0.01
  computed at the *round's total adjudicated decode count*, not the lane's.
- **N is the number of decodes adjudicated, not the number of candidates enumerated**
  (L7-C.3's 12-SD error). Any lane quoting `threshold_for(N_offsets)` is out of contract.

## 8. Kill / stop conditions

- Q5's exact-reproduction failure → fast path abandoned, everything PROVISIONAL.
- If the GEV shape ξ is significantly < 0 (95 % CI excluding 0) in the legacy cell, the
  Gumbel bar is anti-conservative and the lane publishes a **GEV** bar instead, flagging that
  every historical `threshold_for` figure is affected. This is reported either way.

## 9. What this lane will NOT claim

- No statement about the cipher, the key, or any hypothesis class.
- No threshold for a decoder mode it did not measure. If I1's `driftbeam.py` lands after this
  lane's cells are run, the modes here are **proxies** for it and are labelled as such;
  `INTERFACE.md` states the exact re-run needed to finalise.
- No "exhausted"/"closed" language (doctrine R7).

---

_Addenda (dated, append-only) below this line._

**2026-08-26 (addendum 1, written after the Q5 checkpoint and before any null cell was
run).** The Q5 exact-reproduction test is scored on the **returned `score` field**, as
written. Two further reproduction fields are recorded for information but are **not** gating
because the reference implementation does not define a tie-break order over equal-scoring
beam states: `plain_idx` and `ptr_end`. Score equality to 1e-9 is the pre-registered
criterion and remains unchanged.
