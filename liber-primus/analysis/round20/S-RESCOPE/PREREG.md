# S-RESCOPE — PREREG (written before any measurement)

_Round 20, Lane S-RESCOPE. Doctrine-binding. Written 2026-08-28 before the sweep runs._

## What this lane is (and is not)

This is **not new key space**. It re-adjudicates the survivor rows that Round 13's B-04 sweep
stored — the ones R1 D-iii (round19/R1/RESULTS.md:598-627) named as the *only* recoverable value
from ~10^10 discarded decodes — through the **repaired** Round 20 instrument:

- **I1** driftbeam (round19/I1/driftbeam.py): `exact` = keyskip1 baseline, `drift` = the repaired
  drift_rec channel (mode=permissive, lam=12, max_free=2). NEVER the round17 rigid `max_skip` beam
  the original B-04 used.
- **I2** nine-register panel (round19/I2/adjudicate.py) → `pmax`, `preg`. Score on rune INDICES.
- **P3** panel-max null (round20/P3/panelmax20.py) — the calibrated bar, NEVER a fixed −5.5.
- **HITFN** the recovery-gated hit function (round20/HITFN/hitfn20.py) — `is_hit` requires
  pmax≥bar AND rune-index recovery≥0.90 AND held-out-3/4 reproduction. Score alone is NOT a hit.

**Legitimate not-a-re-run (doctrine, R1 (c) NO-ERROR-FOUND):** the original B-04 scored these keys
with a **rigid** decoder + English-only argmax + an **invalid −5.5 bar** = ZERO power. R1 D-iii's own
`reopens_if` names this re-adjudication as the reopener. We are re-scoring stored keys under a
power-measured instrument, not enumerating anything.

## The R1 D-iii defect we are correcting

B-04 Stage A stored everything above −6.412, but under `skip_by_two` the *true* key scores −6.718
(0.31 BELOW the cutoff). So the original sweep could not store its own motivating case. This lane
cannot resurrect keys B-04 never stored — that is a stated coverage hole (§ conditionals below). It
CAN re-adjudicate the 150 stored survivor keys (Stage A/B/C top-50 each, full key params) + the
Stage-D deepenings through the fixed hit function, and re-seed the B-04 slice from
round19/C1/payload_resolved.bin (3 changed bytes idx 45,50,246) so the input is the resolved canon.

## Q1–Q5 (Aiming Test)

- **Q1 (recogniser / positive control — MANDATORY).** Plant a key drawn from a B-04 generator
  (`sha256_ctr` + `mod29`, a real B-04 generator) over a real plaintext, encipher via the same
  `keyskip` relation the instrument targets, insert it into the survivor list at a random rank, and
  require the **full pipeline recovers it rank-1 AND `is_hit`→True**. If the planted key is not
  rank-1 and is_hit-positive, the instrument is not trusted and no null is reported.
  Also plant a **negative control**: a vowel-dropped-English decode that clears the bar on pmax but
  recovers < 0.90 (the EN_NOVOWEL hallucination) MUST be `is_hit`→False.
- **Q2 (prior).** These are the highest-prior stored decodes: they were the English-argmax of a
  measured 6.2M-decode sweep. Re-adjudicating them is the cheapest possible use of the fixed gate.
- **Q3 (bounded).** 150 stored survivor keys + Stage-D rows + the payload_resolved re-seed. No new
  seed enumeration. Fully bounded, minutes of compute.
- **Q4 (three conditionals).** Report per (key space = stored-survivor set; decoder relation =
  {keyskip1 exact, drift_rec}; register = the 9-panel argmax) — a survival/recovery table, not a
  scalar. State the coverage hole (keys B-04 never stored) explicitly.
- **Q5 (kill).** If the positive control does not recover rank-1 + is_hit True, ABORT and report the
  instrument failure, not a null (a null from an unvalidated instrument is not a negative). Time-box
  ≤15 min real compute (this is an "others" lane, not S-G3).

## Pass / fail set in advance

- **HIT** iff any survivor row (or the payload_resolved re-seed) fires `is_hit`→True: pmax≥panel-max
  bar AND rune-index recovery≥0.90 AND held-out-3/4 reproduces. Expected: none (small yield, R1's
  own estimate).
- **Clean NEGATIVE** iff the positive control passes (rank-1 + is_hit) AND no survivor fires is_hit.
  Report coverage fraction + measured power per register + the three conditionals.
- **ABORT** iff the positive control fails.

## Bars used

- Canonical calibrated bar: `panelmax_bar('exact', N=1e6, α=0.01)` = 7.634; `drift` N=1e6 = 13.842.
- Also report the less-conservative small-N bar at N = (#rows adjudicated) so nothing is hidden by
  the conservative canonical bar; a survivor clearing the small-N bar but not the canonical bar is
  logged as a near-miss, not a hit (hitfn20 gates on the N supplied; we supply N=1e6 for the HIT
  decision per HITFN doctrine, and report small-N as diagnostic only).

## Files this lane writes (analysis/round20/S-RESCOPE/)

`PREREG.md` (this), `rescope20.py` (runner), `out_poscontrol.json`, `out_survivors.jsonl`
(SWEEPROW/3 rows), `out_rescope.json` (summary), `RESULTS.md`.
