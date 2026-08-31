# P1 — the skip-aware, multi-register PREFILTER SIEVE — PRE-REGISTRATION

_Round 20, Phase P. THE load-bearing lane (R1 named the sieve's absence "the finding", D-ii).
Written and frozen BEFORE any statistic on real pads was measured. Decoder on LP2 is I1
`driftbeam.py` (`keyskip1` exact baseline; `drift` preset lam=12,max_free=2 for the permissive
channel) — NEVER a rigid decoder. Adjudication is never against a fixed −5.5 bar._

## What is being built

A **two-stage** cheap first-pass sieve that replaces `round17/lib_padsweep.dense_scan` (the only
currently-affordable prefilter), whose measured defects (C2 §4, on real Marsaglia bytes) are:
rigid alignment + English-only, giving true-key survival LP1 0.767 / LATIN 0.70 / OE 0.60 /
CY 0.30 / EN_HALFVOWEL **0.067** / EN_NOVOWEL **0.000** — it throws the true key away, unevenly by
register, before I1×I2 ever sees it.

- **Stage A (cheap, vectorized numpy, rigid alignment over a head window):** score the decrypt
  head under the **9-register** trigram panel and take the **max over registers** per offset —
  the one lever C2's English-only `dense_scan` lacks. Keeps a top fraction `fA`. Cost ≈ dense_scan.
- **Stage B (skip-aware, I1 `driftbeam` at reduced beam width):** re-score only Stage-A survivors
  with `keyskip1` (+ optionally `drift`) so the skip relations are admitted, not rigid alignment.
  Keeps a top fraction `fB` under the same multi-register max.

Reduction = 1/(fA·fB). Survival = product of the two stages' per-register true-key survivals.

## The 5 Aiming-Test answers

**Q1 — recogniser (positive control).** Plant a `skip_by_two`-generated correct key over EACH of
the 9 registers {EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL}, at a
uniformly-random true offset inside a **real hash-verified Marsaglia pad** (the honest
high-entropy control C2 used — NOT synthetic sha256), enciphered with `encipher_keyskip`-family
skip loops at supp=0.83. Measure per-register survival = fraction of plants whose true offset is
retained by the sieve. The sieve PASSES its recogniser only if survival ≥ 0.90 **per register**.
If it cannot reach 0.90 on Welsh + half-vowel English, it is not a sieve, it is a second English
filter (Q5).

**Q2 — prior (measured foothold, not lore).** C2 §4.5's union-screen already survives real
Marsaglia true-offsets where the English filter scores 0.000 — a measured foothold. And C2's own
per-register English survival (0.30–0.77 on the mid registers) shows the *rigid* stage is not the
whole loss; the loss on LATIN/OE/CY is a **register** loss, which a multi-register max directly
attacks. This is the C2 §4.5 recommendation (union of top-K over multiple screens), promoted from
"English trigram + 3 language-agnostic" to "9-register trigram max + language-agnostic".

**Q3 — bounded.** The sieve's own parameter space is small and enumerable: head length
`W ∈ {24,32,48}`, Stage-A keep fraction `fA ∈ {1e-2,1e-3,1e-4}`, Stage-B beam width `bw ∈ {8,16}`
and keep fraction `fB`. Tune on planted keys against real Marsaglia bytes, FREEZE the chosen point,
then report. All statistics are seed-3301 rooted and order-preserving.

**Q4 — three conditionals (the survival SURFACE, not a scalar).** Publish survival as a function
of (key-space × decoder-relation × register): key-space axis = {real Marsaglia offset sweep};
decoder-relation axis = {rigid Stage-A, keyskip1 Stage-B, drift Stage-B, and the true loop is
skip_by_two}; register axis = all 9. Every downstream S-lane negative can then name its register.

**Q5 — kill.** If **no** parameterisation clears **0.90 survival on Welsh (CY) AND half-vowel
English (EN_HALFVOWEL)** simultaneously at a screen-out fraction giving **≥100× reduction**, declare
the sieve **INFEASIBLE** and say so plainly. Phase S then runs G3 only (the one space enumerable
end-to-end without a sieve).

## Positive control detail + planted-recovery instrument proof

Before trusting any survival number, prove the pipeline recovers a planted key it SHOULD keep and
rejects noise it SHOULD drop:
- **Planted-recovery (must work):** correct key at true offset must rank far above the 400+ wrong
  offsets in Stage A for at least the English/LP1 registers (reproduces C2's LP1 0.767 English-only
  baseline as a floor when the panel is degenerate to English-only), and ABOVE 0.90 when the
  multi-register max is enabled.
- **Negative control (must fail):** a uniform-random-rune "plaintext" (register=RAND) planted the
  same way must survive at ≈ chance (≤ 0.10), and an unplanted (no true offset present) scan must
  not manufacture a survivor. If RAND survives > 0.20 the sieve is leaking and the run is void.

## Seed-3301 order-preserving surrogate null

Wrong offsets are the natural null: every offset in the pad other than the true one is a wrong key
by construction (C2's design). Additionally, the pad selection, plant offsets and plaintext windows
are drawn from `random.Random` rooted at a fixed function of 3301 (order-preserving: re-running
reproduces the identical plant set). No process-salted `hash()`.

## Pass / fail threshold (SET NOW, NEVER EDITED AFTER A RESULT)

- **PASS** = per-register true-key survival **≥ 0.90 on ALL 9 registers** (in particular CY and
  EN_HALFVOWEL, the two C2 worst) at a total reduction **≥ 100×**, with the survival surface
  published.
- **PARTIAL** (reported, not a PASS) = ≥0.90 on the four PREREG gate registers
  {LP1_REAL, LATIN, OE, EN_HALFVOWEL} but not all 9, or ≥0.90 on all 9 but at < 100× reduction.
- **INFEASIBLE** (Q5 kill) = no parameterisation clears 0.90 on CY ∧ EN_HALFVOWEL at ≥100×.

## Kill condition at ≤10% budget

Pilot: 15 plants/register × 9 registers = 135 Stage-A decodes against real Marsaglia bytes at the
default point (W=32, multi-register max, fA=1e-3). If the pilot's CY **and** EN_HALFVOWEL survival
are both < 0.60 (i.e. no better than C2's English-only floor) AND raising fA to 1e-2 does not lift
either above 0.75, stop the parameter sweep and declare INFEASIBLE — the multi-register lever has
been shown insufficient and further tuning is chasing a filter that does not exist. Budget spent at
that point ≈ 135 + 135 decodes = well under 10%.

## Trust anchor

`tests/validate.py` must PASS before and after. `analysis/round20/P1/test_p1.py` must pass.
This lane scores NO real LP2 decode (it plants and screens); the P-gate is released by the
coordinator, not here.
