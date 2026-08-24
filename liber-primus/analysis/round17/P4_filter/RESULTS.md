# Round 16 — lane P4 — FILTER FINGERPRINT

**Verdict: MACHINE.**

More precisely, and this distinction is the substance of the lane:

> The **randomness the pad was drawn from was not produced by a human**. Every human-
> randomness model with any signature beyond the bare immediate-repeat rule is excluded at
> ≥ 0.99 power, and the largest lag-2..8 repetition suppression compatible with the data is
> **1.70 % at 95 %** (2.87 % at 99 %) against a lag-1 suppression of **80.75 %** — i.e. under
> **1/47** of the lag-1 effect leaks anywhere else.
>
> The **application of the lag-1 rule itself** is *not* separable from a human eye applying
> only that rule to a machine-generated pad (that composite hypothesis is statistically
> identical to the coded filter by construction; combined power 0.110 — **UNDERPOWERED**).
> But the powered scope test (power 1.000) shows the filter had **no per-line scope**, which
> is the one implementation detail a person checking "the rune I just wrote" would leak.

This **corrects `FINAL-SYNTHESIS.md:73-76`**, which states as fact that the hardening is
"a human calligrapher applying a *don't write the same rune twice* rule by hand while
inscribing the book". Nothing in this repository had ever tested that. On the property that
matters for the search — where the pad's entropy came from — the data says the opposite of
the human reading, and it says it with measured power.

Register item **D-01** (`analysis/round10/RECON-A/REGISTER.md:65`) is hereby **run**: the
conditional next-rune distribution, the windowed χ² under-dispersion sweep and the monogram
drift test are all below, each with a matched control and a measured power.

---

## 1. Pre-registration

Thresholds, controls and decision rules were fixed in **`PREREG-P4.md`** before the
200-replicate run, and none was changed afterwards. The short form:

- **Gate:** the battery must separate iid-uniform from the coded filter on `lag1_z` with
  power ≥ 0.99, or the lane reports INCONCLUSIVE and nothing else in it is read.
- **Power floor 0.80:** a statistic below it is UNDERPOWERED for that comparison and may
  not vote. **Acceptance interval:** central 95 % of a control's 200-replicate distribution.
- **Primary statistics (4, may vote):** `bleed28_z` (test 1), `chi2W58_mean` (test 3 =
  D-01's named sweep), `gap_cv` (test 2), `page_rate_dispersion` (test 6).
- **Fairness:** every control is calibrated by bisection to the *real* doublet rate, so the
  lag-1 rate carries no information and cannot do the discriminating by itself.
- **Verdict labels:** MACHINE / HAND / AMBIGUOUS / UNDERPOWERED-TO-SEPARATE, per hand rung.

**Data.** `liber-primus/data/krisyotam_runes.txt`, split on `%` page marks — the same file
and split `analysis/run_stats.py:load_pages()` uses, with `/` line marks retained to give
per-rune page / line / position. `fingerprint.load_structure()` **asserts** the resulting
stream is identical to `round11/lib_numchannel.unsolved()`. n = **12,956** runes,
**55** pages, **648** lines, **86** doublets.

**Reproduce:** `PYTHONUTF8=1 python fingerprint.py` (measurement),
`PYTHONUTF8=1 python controls.py --reps 200` (~5 min, writes `results.json`),
`PYTHONUTF8=1 python summarize.py` (the tables below). Fixed seeds throughout.

---

## 2. Gate and fairness — the instrument works and the fight is fair

| check | result |
|---|---|
| **GATE** power to separate iid-uniform from the coded filter on `lag1_z` | **1.000** (bar: ≥ 0.99) — **PASS** |
| calibrated `supp` for the coded filter | 0.8131 |
| calibrated `supp` for the line-scoped filter | 0.8431 |
| lag-1 doublet rate, real | 0.006638 |
| lag-1 doublet rate, machine control | 0.006655 ± 0.000740 |
| lag-1 doublet rate, six hand rungs | 0.00653 – 0.00715 (all within ~1 sd of real) |

Doublet counts: real **86**; machine control **86.2 ± 9.6**. The controls and the real stream
agree on lag 1 to well inside noise, which is the whole point — nothing below is a
restatement of the doublet rate.

---

## 3. Test 1 — the lag profile. The suppression is *purely* lag 1

| lag | equality rate | z vs binomial(1/29) |
|---|---|---|
| **1** | **0.66 %** | **−17.37** |
| 2 | 3.404 % | −0.27 |
| 3 | 3.389 % | −0.37 |
| 4 | 3.544 % | +0.60 |
| 5 | 3.699 % | +1.56 |
| 6 | 3.514 % | +0.41 |
| 7 | 3.483 % | +0.22 |
| 8 | 3.383 % | −0.41 |
| **pooled 2–8** | **3.488 %** | **+0.65** |

Chance rate = 1/29 = 3.448 %. Lag-1 suppression = **80.75 %**. Bleed fraction (share of the
lag-1 suppression appearing at lags 2–8) = **−0.014** — i.e. **zero, with the sign wrong for
a human**. The seed measurement in the lane brief is reproduced exactly (86/12,955 = 0.6638 %;
lag 2 = 3.404 %).

**The bound.** Under a true lag-2..8 suppression *s*, `bleed28_z ~ N(−56.90·s, 0.984²)`
(slope analytic, sd measured on the 200 machine replicates because the seven lags share
data). Observed z = +0.653, so:

> **Any lag-2..8 repetition suppression above 1.70 % is excluded at 95 %; above 2.87 % at 99 %.**

For scale, the anti-repeat effect at lag 1 is 80.75 %. A person who avoids repeating the
rune they just wrote, and avoids it *that* hard, does not then treat the rune two back as if
it had never happened. A `if c == c_prev` branch does exactly that.

---

## 4. The hand ladder — which human models the data kills, and with what power

Six hand rungs, each calibrated to the real doublet rate, ordered by the lag-2..8 suppression
they actually emit. "combined power" is the four-primary-feature Gaussian log-LR classifier's
own power to flag a true hand stream at a 5 % machine false-positive rate.

| rung | emitted lag-2..8 suppression | combined power | real logLR (machine/hand) | real called | **verdict** |
|---|---|---|---|---|---|
| `hand_bleed_none` (= machine pad + a human eye applying **only** the lag-1 check) | −0.36 % | **0.110** | −0.3 | machine | **UNDERPOWERED-TO-SEPARATE** |
| `hand_bleed_tiny` | 3.39 % | 1.000 | +11.7 | machine | **MACHINE** |
| `hand_bleed_small` | 6.85 % | 1.000 | +55.7 | machine | **MACHINE** |
| `hand_bleed_mid` | 13.25 % | 1.000 | +244.0 | machine | **MACHINE** |
| `hand_bleed_strong` | 22.17 % | 1.000 | +990.8 | machine | **MACHINE** |
| `hand_rebalance_only` (no lag bleed, window rebalancing only) | 15.79 % | 1.000 | +790.6 | machine | **MACHINE** |

Per-statistic, against the **weakest non-degenerate** rung (`hand_bleed_tiny`, a barely-there
human signature):

| primary statistic | real | power | inside machine 95 %? | inside hand 95 %? |
|---|---|---|---|---|
| `chi2W58_mean` (D-01's sweep) | 0.9358 | **0.990** | yes (p = 0.68) | **no** (p = 0.000) |
| `gap_cv` | 0.9459 | **0.990** | yes (p = 0.29) | **no** (p = 0.000) |
| `bleed28_z` | +0.653 | 0.735 | yes (p = 0.60) | **no** (p = 0.000) |
| `page_rate_dispersion` | 1.091 | 0.055 | yes (p = 0.57) | yes (p = 0.55) — **underpowered** |

The two strongest discriminators, and the whole basis of the verdict, are `chi2W58_mean` and
`gap_cv` at **power 0.99** against the faintest hand model on the ladder, rising to 1.000
above it. `bleed28_z` reaches 0.995 at `hand_bleed_small` and 1.000 above.

`page_rate_dispersion` (test 6) is **underpowered against every hand rung** (0.055–0.105) and
is therefore reported and not used. Its value is stated in §7 for the record.

---

## 5. Test 3 — the windowed χ² under-dispersion sweep (D-01's named sub-test)

Mean per-window χ² divided by df = 28, expected cell counts taken from the stream's own
marginals. 1.00 = iid; below 1.00 = the histogram is being rebalanced inside the window.

| window W | real | uniform | **machine** | hand_tiny | hand_small | hand_mid | rebalance_only |
|---|---|---|---|---|---|---|---|
| 29 | 0.9403 | 0.9966 | **0.9454 ± 0.0116** | 0.9143 | 0.8860 | 0.8385 | 0.7958 |
| 58 | 0.9358 | 0.9968 | **0.9431 ± 0.0187** | 0.8813 | 0.8273 | 0.7373 | 0.6276 |
| 116 | 0.9251 | 0.9882 | **0.9384 ± 0.0258** | 0.8471 | 0.7728 | 0.6496 | 0.5067 |
| 290 | 0.8747 | 0.9823 | **0.9273 ± 0.0386** | 0.8192 | 0.7362 | 0.5965 | 0.4410 |

The real stream **is** under-dispersed relative to iid uniform — and this is the trap the test
exists to avoid, because **a plain lag-1 anti-repeat filter produces that under-dispersion by
itself** (machine control: 0.943 at W = 58). The real values sit on the machine curve at every
window (largest deviation −1.4 sd, at W = 290) and 3–6 sd away from even the faintest hand
rung. Read without the matched control, this statistic would have been written up as
"evidence of a human rebalancing reflex". It is not.

Same story for the related secondary statistics against `hand_bleed_small`:
`page_homog_z` real −2.93 (machine −1.46 ± 1.02, hand −6.66 ± 0.76; **power 1.000**, real
inside machine, outside hand), `gap_2to4_z` real +0.70 (**power 0.970**, inside machine,
outside hand), `bleed23_z` real −0.45 (**power 0.985**, inside machine, outside hand),
`lag2_z` real −0.27 (power 0.895, inside machine, outside hand).

---

## 6. Test 5 — where the 86 residual doublets sit. The filter had **no line scope**

This is the powered structural test, and it is the one that speaks to *how the rule was
applied* rather than to where the entropy came from. Control (a2) is the same coded rule but
scoped to a line: `c_prev` resets at every line turn, which is precisely what a person
checking "the rune I just wrote" does when the quill moves to a new line.

| statistic | real | flat filter | line-scoped filter | power | real is |
|---|---|---|---|---|---|
| `dbl_line_cross_rate` | 0.0465 (4 of 86) | 0.0481 ± 0.0234 | **0.2286 ± 0.0441** | **1.000** | inside flat (p = 0.98), **outside line-scoped (p = 0.000)** |
| `dbl_posinline_ks` | 0.1055 | 0.0863 ± 0.0263 | 0.2005 ± 0.0436 | 0.935 | inside flat (p = 0.42), outside line-scoped (p = 0.03) |
| combined log-LR | +11.6 | — | — | **1.000** | **called flat/machine** |
| `dbl_page_cross_z` | −0.60 (0 of 86 span a page turn) | — | — | 0.400 | underpowered |
| `dbl_posinpage_ks` | 0.0809 | 0.0863 | — | 0.080 | underpowered |

The base rate of line-crossing adjacencies in the book is 4.58 %; 4 of the 86 doublets
(4.65 %) straddle a line break. That is chance to two decimal places. A line-scoped check
would have left **~20** of them there.

Everything else about the placement is flat and, where it is flat, **underpowered** and
reported as such: the residual doublets are not clustered (`dbl_gap_disp` 0.892 vs machine
0.964 ± 0.223, power 0.065), sit at no special position in the page (`dbl_posinpage_ks` 0.081,
power 0.080), and are no nearer or further from the interrupter rune ᚠ than chance
(`dbl_interrupter_z` −0.53, power 0.045). None of those is evidence of anything; they are
recorded so nobody re-runs them expecting a result.

---

## 7. Tests 4 and 6 — drift, fatigue, and the constancy of the suppression rate

| statistic | real | machine | hand_bleed_small | power | reading |
|---|---|---|---|---|---|
| `page_homog_z` (55 × 29 page-by-rune homogeneity) | −2.931 | −1.463 ± 1.020 | −6.660 ± 0.761 | **1.000** | machine |
| `half_split_z` (first vs second half marginals) | +0.648 | −0.142 ± 0.962 | −1.006 ± 0.708 | 0.195 | underpowered; no drift |
| `supp_drift_z` (doublet rate vs position in book) | +0.511 | +0.041 ± 1.011 | +0.083 ± 1.019 | 0.075 | **underpowered** |
| `page_rate_dispersion` (per-page rate around one fitted rate) | 1.091 (z = +0.47) | 0.992 ± 0.186 | 0.974 ± 0.178 | 0.075 | **underpowered** |
| `bigram_offdiag_chi2_df` (D-01 sub-test 1: conditional next-rune, diagonal removed) | 1.0384 (z = +0.75) | 1.0036 ± 0.0499 | 0.9946 ± 0.0513 | 0.080 | **underpowered**; nothing off-diagonal |

Honest reading of §7: **the suppression rate is statistically constant across the 55 pages**
(dispersion 1.09, z = +0.47; per-page doublet counts run 0–5, 13 pages carry none) and there
is **no marginal drift** across the book — but the tests that measure those things
**cannot tell a hand from a machine** at n = 12,956 (power 0.075–0.195). They are consistent
with a loop and they do not exclude a hand. Anyone quoting "the rate is constant, therefore a
machine" is over-reading; the machine verdict rests on §3–§6, not on §7.

The one exception is `page_homog_z`, which does have power 1.000 — and it places the real
stream with the machine, 5 sd away from `hand_bleed_small`.

---

## 8. What this lane *cannot* say

1. **A hand that applies only an immediate-repeat check to a machine-made pad is invisible to
   this battery.** `hand_bleed_none` has combined power **0.110** — the honest label is
   UNDERPOWERED-TO-SEPARATE, and it is unfixable in principle, because such a stream *is* the
   coded filter's output with a human as the branch instruction. What the scope test adds is
   that if a person was the branch, they never once lost the check across a line turn in 648
   lines. That is a machine-like person.
2. **The battery measures the emitted ciphertext**, so it constrains the *randomness source*
   far more tightly than the *rule application*. Read the two verdicts separately.
3. **The hand model is a model.** It follows Wagenaar (1972) and Rapoport & Budescu (1997)
   qualitatively — repetition avoidance over recent lags, window rebalancing — but the
   parameters for a 29-symbol futhorc alphabet are not in the literature. That is why the
   result is delivered as a **ladder and a bound** (§3, §4) rather than a single yes/no: any
   future hand model can be placed on the ladder by its emitted lag-2..8 suppression, and the
   1.70 % bound applies to it directly.
4. **The 86 doublets are a transcription artifact until A-03 is run.** Register item **A-03**
   (haplography count-audit of the 86 doublet sites) is still `never-run`. If a high-zoom
   re-read merges ~20 doublet neighbourhoods, every number in §3 and §6 moves. This lane
   raises A-03's value: it is now the single cheapest falsifier of a *positive* result rather
   than of a negative one.

---

## 9. What this implies for which pad families can exist

Written as guidance for the next round to act on.

**(1) The imported-public-byte-source families (P0–P3) are the correctly-prioritised targets,
and this lane raises their prior rather than lowering it.** The pad's entropy is not
human-produced. It came out of something that emits symbols with no recency memory whatsoever
beyond a single explicit branch. That is a file or a generator, not a person writing runes
off the top of their head. The whole enciphering pipeline being coded also makes "the script
opened a byte file" a far more natural implementation than "the author hand-copied digits
from a printed page" — which shifts weight *within* P3 toward the machine-readable sources
(3301's own published PGP blobs, hash blocks, onion addresses) and away from RAND's printed
table as a hand-transcribed source, while leaving the RAND *digital* edition fully in scope.

**(2) The `random.org` / NIST-Beacon / blockchain branch of the census is now the live half of
the "no seed" category, and the census's own wording is the thing to fix.** The seed census
(`round10/L5-seed32/CENSUS.md:87-94`, repeated in `handoff/PARKED.md:273-278` and
`ELIMINATION-LEDGER.md:365-368`) lumps `random.org` in with dice and `/dev/urandom` under
"nothing can touch it". P4 removes the one escape hatch that would have made that lumping
harmless — "it was a human, so there was never a byte source at all". There *was* a byte
source. Round 16's P1/P2 lanes are pointed at exactly the right object.

**(3) A human-generated pad is excluded, and with it the attack that would have followed
from it.** Had this come back HAND, the correct next move would have been a *joint decode
under a key prior* — exploiting the non-uniformity of human "randomness" to solve for
plaintext and pad together, with no key search at all. **Do not build that.** The pad has no
exploitable non-uniformity at lags 2–8 (bound: < 1.70 %), no window rebalancing beyond what
the lag-1 filter itself produces, no drift, and no off-diagonal bigram structure. A key prior
buys nothing.

**(4) The filter is a free extra constraint on every candidate pipeline.** Any proposed
reconstruction must reproduce a **flat, unscoped, single-lag** filter at
`supp ≈ 0.813` — not per line, not per page, and with no recency memory. A candidate that
implies a scoped or multi-lag rule is wrong regardless of how its decode scores. Concretely:
the key pointer advances on rejection over the *whole stream*, which is what
`skipdecode.encipher_keyskip` and the beam already assume — so the beam decoder's model is
confirmed against the data for the first time, and P0's dense-offset re-sweep is running on
the right cipher model.

**(5) Dice, hardware RNGs and `/dev/urandom` remain untouched and untouchable by this lane.**
P4 separates *human* from *machine*. It says nothing about *which* machine, and it cannot:
a `/dev/urandom` pad and a NIST-Beacon pad are identical under every statistic here. The
value of this result is that it removes a third branch (human) that the taxonomy did not
have, and that `FINAL-SYNTHESIS.md` had asserted was the answer.

---

## 10. Files

| file | contents |
|---|---|
| `PREREG-P4.md` | thresholds, controls and decision rules, fixed before the run |
| `fingerprint.py` | the battery; `load_structure()` (asserts stream identity), tests 1–6, D-01 sub-test 1 |
| `controls.py` | the four generators, the calibration, the hand ladder, power, the adjudication |
| `summarize.py` | regenerates every table above from `results.json` |
| `results.json` | all 200-replicate control distributions, powers, per-rung adjudications |
| `real_measure.json` | the battery applied to the real stream alone |
| `run200.log` | console record of the reported run |

**One-line result for the ledger:** *the LP2 anti-repeat filter is a flat, unscoped, purely
lag-1 machine filter (`supp` 0.813); human-generated randomness is excluded at ≥ 0.99 power
with a 1.70 % (95 %) bound on any lag-2..8 bleed, so the pad's bytes came from a program or a
file — which is what P0–P3 are searching.*
