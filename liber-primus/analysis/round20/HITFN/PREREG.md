# HITFN — the recovery-gated hit function (resolves red-team defect (d))

_Pre-registered 2026-08-28, BEFORE any measurement. Binding doctrine: `ARMADA-DOCTRINE.md`.
This lane ships one instrument (a predicate), not a sweep. Its "hit" is a
**mis-classification** — either a hallucinating decode that `is_hit` wrongly ACCEPTS, or a
genuine decode that `is_hit` wrongly REJECTS — so, per doctrine mechanic 2 (Q1), the
recogniser is built and PLANTED before it is trusted._

## The defect this closes (SYNTHESIS §3 (d), FOUND-ERROR, blocks Phase S)

`panelmax20.py` returns a **score bar only**. `SWEEPROW/1,2` persist **no recovery field**.
**No hit-decision function exists** in `analysis/round20/`. And `EN_NOVOWEL` clears the
panel-max bar at rune-index recovery **0.84 (exact) / 0.26 (drift)**, both < 0.90 — so a
Phase-S lane certifying on `pmax ≥ bar` alone would **certify a hallucinating decode**. The
red-team has abort authority (CAMPAIGN-PLAN 264–266): Phase S halts until a runnable
recovery-gated hit decision ships.

## Q1 — the recogniser (what a HIT is, stated before measuring)

`is_hit(decode)` returns **true iff ALL THREE** hold (CAMPAIGN-PLAN §2, doctrine win-condition):

1. **CLEARS THE NULL.** The decode's `SWEEPROW/1` `pmax` clears the **P3 panel-max bar**
   `panelmax20.panelmax_bar(preset, n_round_adjudicated, alpha=0.01)` — never −5.5, never a
   per-register bar, never a scalar k_eff.
2. **RECOVERS.** Rune-**INDEX** recovery ≥ **0.90**, recovered from the **driftbeam decode
   path**, NOT from `score`. The score/recovery decoupling is the whole hazard: score alone
   certifies a hallucinating decoder (R1 A-iv).
3. **REPRODUCES HELD-OUT.** The same key, attributed on **1/4** of the page, reproduces
   recovery ≥ 0.90 on the **held-out 3/4** of the SAME page under that key. A key that only
   "works" on the quarter it was fit to is an overfit, not a solve.

Anything clearing (1) on score but failing (2) or (3) is logged as a **decoupling artefact**,
never a hit. `is_hit` REJECTS on the first failing clause.

### How recovery is computed WITHOUT ground-truth plaintext (the crux of defect d)

`driftbeam.recovery(plain_idx, truth_idx)` needs `truth_idx`, uncomputable on a real LP2
candidate. Resolution: the decode object carries a **key + ciphertext + offset + preset**, and
recovery is defined **self-referentially against the decode's own re-decipherment**, split
into fit/held-out halves:

- **held-out recovery (clause 3, the real-candidate-safe one):** attribute the key on the
  first 1/4 rune window, then RE-RUN the beam decoder with that same key on the held-out 3/4.
  Recovery = fraction of held-out rune indices whose re-decode agrees with the full-page
  decode's own indices on that region. A hallucinating decode (beam wandering into a
  restricted-alphabet basin) does NOT reproduce under a fixed key on unseen ciphertext; a real
  key does. This is computable with **no plaintext oracle**.
- **plant mode (controls only):** when a ground-truth `truth_idx` is supplied (plants), clause
  (2) and (3) recovery are measured against it directly, which is the strict test the guard
  needs. Real candidates never supply `truth_idx`.

Both paths flow through the SAME `is_hit`; the guard proves the strict (truth-supplied) path,
and the held-out path is the deployable proxy that agrees with it on the controls.

## Q2 — prior / foothold

The instruments this composes are all validated: driftbeam `recovery()` (round19/I1,
rune-index, G-EQ PASS), `adjudicate()`/`pmax` (round19/I2, power ≥0.90 in 27/27),
`panelmax20.panelmax_bar` (round20/P3a, correct-key power 1.00, wrong 0.00, CALIBRATED M=1e6).
Nothing is re-derived; this lane wires them into one gate and a SWEEPROW recovery field.

## Q3 — bounded

The predicate is O(one extra beam decode) per candidate row (the held-out re-run). No search
space. The two guard plants are single decodes each. Total compute < 2 min.

## Q4 — three conditionals reported together

Every rejection/acceptance names (key space of the attributed key, decoder relation/preset,
adjudicator register `preg`). The SWEEPROW recovery field carries `recovery`,
`heldout_recovery`, and the failing clause so any downstream negative is re-adjudicable.

## Q5 — kill / pass condition (set in advance)

**PASS requires ALL of:**
- (P-a) A `recovery` field is wired into the SWEEPROW/1 emitter (`to_row_v3`), validating.
- (P-b) **Hallucination guard proven:** a decode that SCORES above the panel-max bar but has
  LOW rune-index recovery (the EN_NOVOWEL 0.26–0.84 failure mode) is **REJECTED** by
  `is_hit`; AND a genuine high-score high-recovery decode is **ACCEPTED**. Both reported with
  measured numbers.
- (P-c) Held-out ¾ reproduction is wired (fit on 1/4, verify recovery on 3/4).
- (P-d) `tests/validate.py` still PASSES (trust anchor untouched).

**KILL:** if no construction makes the guard both reject the fake AND accept the real (e.g.
the held-out proxy cannot separate hallucination from a real key), declare the recovery gate
INFEASIBLE, report it as a bound, and leave Phase S halted. That is a real result, not a
failure to try.

## Positive control (planted, run FIRST)

1. **Genuine decode:** English plaintext, `keyskip` encipherment, decoded with the CORRECT
   key → expect pmax ≥ bar, recovery = 1.0, held-out recovery ≥ 0.90 → `is_hit` = **True**.
2. **Hallucinating decode:** an EN_NOVOWEL-register decode (vowel-dropped English basin) that
   clears the panel-max bar on `pmax` but has recovery in [0.26, 0.84] under a key that does
   NOT reproduce on the held-out 3/4 → `is_hit` = **False**, with the failing clause named.

A null (a real LP2 wrong key rejected) from THIS instrument is only trustworthy after both
controls pass (doctrine: a null from an unvalidated instrument is not a negative).
