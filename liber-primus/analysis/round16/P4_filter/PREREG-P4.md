# Round 16 lane P4 — pre-registration (written before the 200-replicate run)

_Fixed 2026-08-19. The instrument shakedown (`--reps 20`) had been run to confirm the code
executes and that the gate passes; every threshold below was fixed before the 200-replicate
run whose numbers are reported in `RESULTS.md`, and no threshold was changed afterwards._

## Question

`FINAL-SYNTHESIS.md:73-76` states as fact that LP2's ~81 % doublet suppression is
**"a human calligrapher applying a 'don't write the same rune twice' rule by hand while
inscribing the book"**. Register item **D-01**
(`analysis/round10/RECON-A/REGISTER.md:65`) records that the sub-tests which would decide
this were never run. This lane runs them and returns one of three verdicts:

**MACHINE** / **HAND** / **UNDERPOWERED-TO-SEPARATE**.

## Data

`liber-primus/data/krisyotam_runes.txt`, split on `%` page marks — the same file and split
`analysis/run_stats.py:load_pages()` uses, so the stream is byte-identical to
`round11/lib_numchannel.unsolved()` (asserted in `fingerprint.load_structure`). `/` line
marks are retained to give per-rune page / line / position-in-line / position-in-page.
n = 12,956 runes, 55 pages, 648 lines, 86 doublets.

## Controls (all calibrated to the SAME lag-1 doublet rate as the real data)

| id | stream | why |
|---|---|---|
| (c) | iid uniform over 29 runes | negative control |
| (a) | **MACHINE** — `skipdecode.encipher_keyskip`, uniform plaintext under a uniform keystream, `if c == c_prev: skip the key symbol w.p. supp` | the coded filter |
| (a2) | **MACHINE/LINE** — the same rule scoped to a line (`c_prev` resets at each line turn) | a filter with a *scope*; exists to prove test 5 has power |
| (b) | **HAND** — recency avoidance at lags 1–3 + short-window frequency rebalancing | human-generated randomness (Wagenaar 1972; Rapoport & Budescu 1997) |

**Fairness requirement.** The lag-1 avoidance strength of every hand rung and the `supp` of
every machine control are bisected so the emitted doublet rate equals the real
86/12,955 = 0.6638 %. If the controls did not agree on lag 1, every "discrimination" below
would be a restatement of the lag-1 rate and would prove nothing.

**Hand ladder.** The size of the lag-2/3 bleed is not pinned down in the literature for a
29-symbol alphabet, so the lane runs six rungs from "no bleed at all" to "strong bleed" and
reports **which rungs the data excludes**. This turns a yes/no argument into a measured
bound.

## Statistics — fixed before the run

**Primary (may vote on the verdict):**

| stat | battery item |
|---|---|
| `bleed28_z` | 1 — pooled lag-2..8 equality z vs binomial(1/29) |
| `chi2W58_mean` | 3 — **D-01's named windowed χ² under-dispersion sweep** |
| `gap_cv` | 2 — shape of the same-rune repeat-gap distribution |
| `page_rate_dispersion` | 6 — binomial dispersion of the per-page doublet count around one fitted rate |

**Secondary (reported, informative, never decisive):** `lag2_z`, `lag3_z`, `bleed23_z`,
`gap_2to4_z`, `abab_z`, `chi2W{29,116,290}_mean`, `page_homog_z`, `half_split_z`,
`supp_drift_z`, `dbl_line_cross_z`, `dbl_page_cross_z`, `dbl_posinline_ks`,
`dbl_posinpage_ks`, `dbl_gap_disp`, `dbl_interrupter_z`, `bigram_offdiag_z`.

## Thresholds

1. **Gate (mandatory, AGENTS.md lesson 1).** The battery must separate (c) from (a) on
   `lag1_z` with power ≥ 0.99 at α = 0.05. If it does not, the lane reports INCONCLUSIVE
   and nothing else in it is read.
2. **Power floor `POWER_FLOOR = 0.80`.** A statistic whose measured power to separate (a)
   from a given hand rung at n = 12,956, α = 0.05, is below 0.80 is declared
   **UNDERPOWERED for that rung** and may not vote. Reporting an underpowered statistic
   as evidence is the failure this lane exists to avoid.
3. **Acceptance interval `ALPHA = 0.05`.** The real value is *consistent with* a control
   family if it lies inside the central 95 % of that family's 200-replicate distribution.
4. **Per-rung verdict.**
   - **MACHINE** if ≥ 1 primary statistic with power ≥ 0.80 places the real value inside
     (a)'s 95 % interval and outside the rung's, and none does the reverse.
   - **HAND** if the reverse.
   - **AMBIGUOUS** if both.
   - **UNDERPOWERED-TO-SEPARATE** if the combined classifier's own power < 0.80,
     regardless of the individual votes.
5. **Combined classifier.** Diagonal-Gaussian log-likelihood ratio over the four primary
   statistics; its threshold is the 5th percentile of the machine distribution, and its
   reported power is the fraction of true hand streams it flags. The real stream is
   "called machine" iff its logLR is above that threshold.
6. **Bleed bound.** Report the largest lag-2..8 suppression compatible with the observed
   `bleed28_z` at 95 % and 99 %, using the *empirical* sd of `bleed28_z` under (a) — not
   the binomial sd — because the seven lags share data and are not independent.
7. **Scope test (test 5).** The placement statistics may only be interpreted if
   (a) vs (a2) power ≥ 0.80. Below that the placement of the 86 residual doublets is
   reported as UNDERPOWERED, because 86 points is a small sample and it is entirely
   possible this test cannot see a line-scoped filter at all.

## Kill rule

No claim without a control and a null. If the honest answer is "the data cannot separate
these", that is the result, and it corrects `FINAL-SYNTHESIS.md` from a stated fact to an
untested assertion either way.
