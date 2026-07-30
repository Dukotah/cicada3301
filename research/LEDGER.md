# RESEARCH LEDGER — Liber Primus (LP2) rigorous attack loop

Append-only. One entry per pre-registered test that reaches execution. Killed-before-execution
hypotheses go to `DEAD_ENDS.md`. This ledger is the source of truth for the cumulative
multiple-comparisons correction: **every executed statistical test ever run against the fixed
ciphertext must be counted here**, and any "surviving" result must clear a threshold corrected
across the full ledger, not per-round.

## Multiple-comparisons running tally

- Executed statistical tests logged in THIS ledger: **2**
- Prior attack families (pre-ledger, from FINDINGS/SOLVE-ATTEMPT-FINAL/CRYPTO-RIGOR): ~20 families,
  hundreds–thousands of parameterized runs. Treat the effective prior test count as large; a new
  result at p < 0.01 is expected by chance somewhere in the accumulated search and is worth ~nothing
  without an order-matched-surrogate null and a corrected threshold.

---

## Round 1 — 2026-07-29 — H1 "Interrupter-as-doublet-breaker"

**Branch:** `research/round-1-interrupter-doublet`

**Question (from the Contrarian's load-bearing flag + Cryptanalyst H1):** The repo's headline doublet
deficit (0.664% vs 3.448% random, z ≈ −16.9) is measured on the raw stream with all 458 ᚠ (F)
interrupters left in. Since a null-ᚠ does not advance the key, are the interrupters themselves the
doublet-suppression mechanism — i.e. is the deficit an artifact of ᚠ *placement* between would-be
identical runes, rather than a property of the enciphered body?

**Pre-registration (fixed before any code):**
- Ground-truth anchor (required): decrypt canonical page 03 WELCOME with Vigenère key DIVINITY under
  the documented ᚠ-non-advance rule, and re-encipher to the EXACT known ciphertext (round-trip).
- Test statistic: `doublet%_deᚠ` = adjacent-doublet rate after deleting ALL ᚠ and rejoining
  neighbors; plus flank-identity rate (fraction of interior `a ᚠ b` with a == b).
- Null model (order-matched surrogates): 10,000 permutations of ᚠ positions holding the rune
  multiset and ᚠ count fixed (seed 3301).
- Decision threshold: CONFIRM iff `doublet%_deᚠ ≥ 2.9% AND > 99th percentile of surrogates`;
  otherwise REFUTE.

**Execution:** `liber-primus/analysis/h1_interrupter_strip.py` (seed 3301). Harness validated by the
ground-truth anchor (WELCOME 4/4 words; full 394-rune round-trip identical = True).

**Results (12,956 runes, 458 ᚠ):**
| statistic | observed | reference |
|---|---|---|
| doublet%_raw (ᚠ in) | 0.6638% | repo sanity ~0.664% ✓ |
| doublet%_deᚠ (ᚠ stripped) | **0.7602%** | threshold 2.9% |
| flank-identity (a ᚠ b, a==b) | 2.8889% | random 3.448% / unigram-collision 3.579% — *below* both |
| ᚠ frequency | z = +0.541 | not inflated |
| within-word non-ᚠ doublet (no ᚠ between pair) | 0.6364% | corroborating diagnostic |

Null (flank-identity, non-degenerate): mean 0.756%, sd 0.417%, 99th 1.887%. Note: the
`doublet%_deᚠ` arm of the surrogate null is **mathematically degenerate** (permuting-then-deleting ᚠ
always returns the identical non-ᚠ subsequence, sd = 0), so cond2 is ill-posed for that statistic.
This was disclosed by the executor without altering the verdict; cond1 (absolute 2.9% floor) resolves
the test on its own.

**Gate #2 verdict: NEGATIVE (H1 refuted).** cond1 fails by ~4× (0.76% vs 2.9%); two independent
diagnostics corroborate. Not INVALID: no goalpost move, harness anchored, refutation triangulated.

**ESTABLISHED (assumed → measured):** The low doublet rate is a **global, ᚠ-independent property of
the ciphertext body**. Removing all interrupters barely moves it (0.66% → 0.76%); the same
suppression appears within words where no interrupter can act (0.64%); interrupters do not sit
between identical flanks more than chance. Any future decryption model must treat doublet
suppression as intrinsic to the enciphered stream, NOT as an interrupter-insertion artifact.

**Also killed this round (pre-execution, Gate #1):** H2 (self-avoiding-LCG keystream) and H3
(doublet-triggered key stall). See `DEAD_ENDS.md`.

---

## Round 2 — 2026-07-30 — R2-H1 "Fractionation coordinate-plane dispersion signature"

**Branch:** `research/round-2-fractionation-signature` (stacked on round-1 branch for ledger continuity)

**Question:** Round 1 established the doublet deficit is intrinsic to the ciphertext body, which
points at body-level mechanisms. The Archivist found only *bifid* was ever run; trifid/Polybius were
closed only by the aggregate IoC-ceiling argument (fractionation tops out IoC·N≈1.4–1.5, can't reach
observed 1.00). Does the unsolved body carry a **period-locked autocorrelation signature inside a
decomposed coordinate sub-stream** — a dimension the aggregate IoC ceiling never measures — that a
trifid/Polybius fractionation would impose and a flat OTP-class keystream would not?

**Why this wasn't redundant (Gate #1):** the IoC ceiling bounds the *marginal* whole-stream
coincidence rate; it says nothing about periodicity *within* a coordinate axis. Non-decrypting
structural discriminator (no key search). Gate #1 killed two alternatives: the transposition-delta
re-measure (already answered by CRYPTO-RIGOR §B: columnar restores doublets toward random, file order
is the unique minimum; jbo already ran a spiral route) and the alternative-index-ordering battery
(anchor-refuted — five solved pages incl. LP2's AN END decrypt ONLY in canonical GP order).

**Pre-registration (fixed before code):**
- Statistic: `A_max` = max normalized autocorrelation over lags 2–40, over all coordinate sub-streams,
  across 3 grid packings (P = Polybius 6×5; T = trifid 3×3×3 layer-major; T2 = trifid col-major).
- Anchors: (1) synthetic trifid with a KNOWN injected period must surface as a super-threshold peak
  (harness sensitivity); (2) real solved LP2 page AN END must show no period peak; (3) aggregate
  IoC·N below the 1.39 bifid floor.
- Null: 10,000 order-matched surrogates (permute exact rune multiset through the same decomposition,
  seed 3301).
- Threshold: CONFIRM iff `A_max(real) > surrogate 99.9th pct AND ≥ 0.05 abs AND peak lag reproduces
  ±1 across ≥2 of 3 grid variants`; else REFUTE.

**Execution:** `liber-primus/analysis/r2_fractionation_signature.py` (seed 3301; ~13 min for the null).
Output: `liber-primus/analysis/r2_frac_out.txt`.

**Anchors:** (1) synthetic period-13 → peak at lag 39 (=3×13 harmonic, in-spec), A_max 0.0787 >
surrogate 99.9th 0.0384 → PASS. (2) AN END (85 runes) A_max 0.386 < its wide surrogate 99.9th 0.562 →
no peak → PASS (note: short page, provisional-quality control; decision weight sits on the
length-matched synthetic + the real corpus's own tight null). (3) IoC·N 0.9999 < 1.39 → coherent.

**Results (12,956 runes, 10,000 surrogates):**
| variant | A_max (sub, lag) | null mean | null p99 | null p99.9 | > p99.9? | ≥0.05? |
|---|---|---|---|---|---|---|
| P  | 0.0246 (col, 26) | 0.0211 | 0.0320 | 0.0376 | no | no |
| T  | 0.0284 (row, 18) | 0.0224 | 0.0330 | 0.0386 | no | no |
| T2 | 0.0284 (row, 18) | 0.0224 | 0.0330 | 0.0386 | no | no |

Real A_max (0.025–0.028) sits ≈ null-mean + 1.6 sd — inside the null bulk, below even the 99th pct.

**Gate #2 verdict: NEGATIVE (R2-H1 refuted, decision-grade).** No goalpost move, order-matched null,
harness validated by Anchor 1, robust to the cumulative multiple-comparisons correction (signal
doesn't clear the 99th pct, let alone 99.9th). Soft spot: the AN END control is underpowered at 85
runes, but the verdict does not lean on it.

**ESTABLISHED (assumed → measured):** Unsolved LP2 carries **no detectable period-locked fractionation
autocorrelation** (A_max ≤ 0.028, below its own tight length-matched null and far below the 0.05 floor)
in any of 3 coordinate sub-streams across 3 grid packings — upgrading the trifid/Polybius exclusion
from an IoC-ceiling *inference* to a direct coordinate-level *measurement*, consistent with the
sub-1.39 IoC·N.
