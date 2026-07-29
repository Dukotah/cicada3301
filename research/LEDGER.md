# RESEARCH LEDGER — Liber Primus (LP2) rigorous attack loop

Append-only. One entry per pre-registered test that reaches execution. Killed-before-execution
hypotheses go to `DEAD_ENDS.md`. This ledger is the source of truth for the cumulative
multiple-comparisons correction: **every executed statistical test ever run against the fixed
ciphertext must be counted here**, and any "surviving" result must clear a threshold corrected
across the full ledger, not per-round.

## Multiple-comparisons running tally

- Executed statistical tests logged in THIS ledger: **1**
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
