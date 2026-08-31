# S-MARS — PREREG (written before any real compute)

_Round 20, Phase S. Lane S-MARS: the held Marsaglia physical-randomness units as the honest
control that a clean null means what we think — real physical randomness must NEVER fire
`is_hit()`. Binding: `ARMADA-DOCTRINE.md`; win-condition CAMPAIGN-PLAN §2; hit predicate
`analysis/round20/HITFN/hitfn20.py` (recovery-gated, NOT score-gated)._

## What this lane is (and is not)

The S-lanes G3/BASH/PERL/TEX enumerate *seeded PRNG* families. S-MARS is different by design:
the Marsaglia CDROM is **real physical randomness** (hash-verified, 630 MB, L6/C2 112 PASS /
0 DRIFT). If the LP2 pad were ever a seeded 2012 PRNG, an S-lane could in principle recover it.
If it were drawn from a genuine physical/CSPRNG source, **nothing recovers it** — and this lane
is the calibration that proves the null-firing machinery is honest: run real physical random
keystream through the FULL repaired instrument and confirm `is_hit()` fires on **nothing**.
A control that fired here would mean the instrument manufactures hits from noise; a clean null
here is what lets every *other* S-lane negative be trusted.

This is explicitly a **not-a-re-run** (SYNTHESIS §3(c), LEDGER coverage): L6/C2 swept the
Marsaglia offsets under `dense_scan` = **rigid + English-only + invalid (-12.5/-5.5) bar** =
ZERO power by doctrine L7-A/L7-B. This lane runs the SAME physical bytes through the
skip-aware `drift_rec`/`keyskip1` beam, the 9-register panel, the calibrated panel-max null,
and the recovery-gated hit predicate — the exact power axes L6/C2 never had.

## The five Aiming-Test questions

- **Q1 (recogniser / MANDATORY positive control).** Before trusting any null: plant a key drawn
  from a REAL Marsaglia pad (mod29 builder over BITS.NN bytes), encipher a REAL readable
  plaintext register (EN_MODERN and LP1_REAL) with the `keyskip1` relation (supp=0.83), and
  recover it **rank-1** through the FULL pipeline — beam decode → 9-register adjudicate →
  panel-max bar → `is_hit()==True` — with `truth_idx` supplied so the strict recovery is
  measured. If the planted physical-source key does not recover rank-1 and fire `is_hit`, the
  instrument cannot see a Marsaglia-sourced key at all and no null from it is interpretable.
  A second control (a wrong Marsaglia key on the same ciphertext) must NOT fire `is_hit`.

- **Q2 (prior).** L1's toolchain prior does not point at a physical-noise CDROM as the LP2 key
  source; the prior on this family is LOW. Its value is as the **honest control**, not as a
  high-prior candidate. (C2 costed it at ~21 CPU-h for the full pads-only space precisely so
  Round 20 could schedule a *fraction* as calibration rather than a full sweep.)

- **Q3 (bounded).** The unit grid is finite and enumerated: 63 pads × 6 builders × 2 byte-orders
  = **756 units**; 77 already checkpointed by L6 ⇒ **679 units HELD** (this lane's population).
  Each unit yields a materialisable Z29 keystream. This lane runs a **stated fraction** of the
  679 held units within a 15-minute compute box and reports the fraction + extrapolated cost
  (doctrine R2), never a bare "swept."

- **Q4 (three conditionals).** Every decode is a `SWEEPROW/3` row carrying `en` + `{ioc,mds,h2,
  zl}` + `{n_skips,n_unexplained}` + `{recovery, heldout_recovery, clears_null, hit}`, scored on
  rune INDICES, under BOTH decoder relations (`keyskip1` = `exact` preset for the clean
  calibrated 7.634 bar, AND `drift_rec` = `drift` preset for transcription robustness, each vs
  its OWN panel-max bar). Register is the panel argmax. A negative names (key space × decoder
  relation × register).

- **Q5 (kill / expected result).** EXPECTED: zero `is_hit()` fires across all sampled decodes
  (physical randomness carries no LP2 signal). The control MUST have fired first (Q1). If the
  control fires AND the null does not, the lane PASSES as a clean control. If ANY held-unit
  decode fires `is_hit()` (clears 7.634/13.842 bar AND recovery≥0.90 AND held-out 3/4 reproduces)
  that is either a genuine anomaly to escalate OR — far more likely — an instrument leak to be
  red-teamed; it is NOT reported as a HIT without held-out reproduction on a fresh page window.
  Kill at ≤10% budget: if the positive control cannot be constructed at all (no
  Marsaglia-sourced plant recovers rank-1), declare the instrument blind to this family and stop.

## Pass/fail thresholds (set in advance)

| outcome | meaning |
|---|---|
| **PASS (clean control)** | positive control fires `is_hit()==True` rank-1 AND wrong-key control does NOT AND ZERO held-unit decodes fire `is_hit()` across the sampled fraction | 
| **NEGATIVE** | same as PASS but framed as the family result: sampled fraction of 679 units, 0 hits, power carried per register |
| **HIT** | a held-unit decode clears its panel-max bar AND recovery≥0.90 AND reproduces on the held-out 3/4 of the SAME page-window under the SAME keystream (all three) — would be escalated, not auto-published |
| **BLOCKED** | positive control cannot be built (instrument blind to Marsaglia keys) |

## Method (frozen before running)

1. Load real LP2 (12,956 runes, Z29) via `run_fp.lp2()`. Page-window L=240 (I2's k_eff regime).
2. **Positive control:** draw keystream from BITS.01 via `b_mod29`; encipher a real EN_MODERN and
   a real LP1_REAL plaintext window with `skipdecode.encipher_keyskip(supp=0.83)`; decode with
   the matching key; adjudicate; assert `is_hit(truth_idx=P)==True` and rank-1 vs 200 wrong
   Marsaglia keys. Wrong-key control: same ciphertext, different pad's keystream ⇒ `is_hit`
   False.
3. **Null sweep:** iterate held units in deterministic order (seed-3301 shuffle of the 679-grid);
   per unit materialise the Z29 keystream (capped to a usable prefix), slide `S` LP2 page-windows,
   decode each under BOTH presets from a prior-weighted set of offsets (P3b seed ordering is a
   ranking over *seeded* generators and does not apply to physical bytes, so offsets are sampled
   uniformly across the pad — stated), adjudicate, emit `SWEEPROW/3`, call `is_hit()` (real mode,
   no truth). Record pmax, recovery, heldout, clears_null, hit.
4. Time-box 15 min. Report units touched / 679, decodes scored, per-register power (carried from
   P3, re-confirmed on the control), the max pmax seen on any held unit, and whether `is_hit`
   fired on anything. Keep `tests/validate.py` green.

## Positive control is MANDATORY and runs FIRST

No null from this lane is reported before the Marsaglia-sourced positive control has recovered
rank-1 and fired `is_hit()`. A null from an unvalidated instrument is not a negative (doctrine).
