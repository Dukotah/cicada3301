# P2 — PREREG — the `n_skips` null curve + language-agnostic screen

_Round 20, Phase P. Pre-registered 2026-08-28 BEFORE any statistic was measured. Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). Depends on I1
[`driftbeam.py`](../../round19/I1/driftbeam.py) (the only decoder allowed on LP2), I3
[`RESULTS.md`](../../round19/I3/RESULTS.md) §10.1b/§12 (which named this "the highest-value
single addition"), T3 [`RESULTS.md`](../../round19/T3/RESULTS.md) §5.1 (transcription
robustness), I2 [`SWEEPROW.md`](../../round19/I2/SWEEPROW.md) (the schema I extend)._

---

## What `n_skips` is (and why it is the backbone statistic)

I1's `beam_decode` returns, for the argmax path it chose, `n_skips = ptr_end - o - nsteps`:
the number of key positions the winning path advanced BEYOND one-per-rune. Under the repo's
`keyskip1` relation an advance is only admitted when the skipped key position would have
reproduced the previous cipher rune (probability 1/29 per skip on a high-entropy pad). So a
**wrong** key is forced to fabricate almost no legal skips — its argmax path advances at
essentially exactly one key position per rune. A **correct** key that was enciphered with a
real rejection loop leaves the exact skip footprint the loop wrote, so its path advances by
`true_n_skips` more. T3 §5.1: at full book the correct key infers 418/418 skips exactly, a
wrong key infers 1537 — margin 1,119 draws — and **98.4% of that margin survives k=450
substitutions** (T3 §5.1 table), because the statistic never routes through the English
scorer. It is therefore the ONLY Round-19 ranking statistic that is both language-independent
(I2 §7) AND transcription-robust (T3), which is why I3 §12 flagged it as the single most
valuable addition to the contract and why it is the backbone of the P1 sieve.

The hazard I3 §10.1b names, tested here: `n_skips` is a small-range integer, so its null is
**discrete** and a Gumbel bar is the wrong tool. This lane builds the **exact empirical
discrete tail**, never a continuous fit.

---

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = a key whose decode's `n_skips` sits in the far right discrete tail of the wrong-key
`n_skips` histogram, where a correct-key-with-a-real-rejection-loop lands. The positive
control PLANTS keys at known rejection counts (`enc_keyskip`, `enc_skip_by_two` at
supp∈{0.60,0.83,0.98}), decodes with I1's `keyskip1` (baseline) and `drift_rec`
(preset `drift`, lam=12,max_free=2) relations, reads `n_skips`, and shows the planted-key
`n_skips` clears the pre-registered empirical FPR quantile of the wrong-key null. If the curve
cannot separate the planted key it built from a wrong-key histogram, it is not a screen.

**Q2 — What measured fact raises this above the flat rate?**
T3 §5.1: 98.4% of the 1,119-draw margin survives k=450 substitutions — measured, not lore
(`round19/T3/RESULTS.md`, `out_summary.json`). I2 §7: `n_skips` is register-independent by
construction. I3 §12: named it "the highest-value single addition," with the discrete-tail
hazard flagged. These are three cited measurements, not a prior guess.

**Q3 — Is the space bounded, and by what?**
Fully enumerable/simulatable. The null is a fixed simulation at **seed 3301**,
order-preserving: `M` wrong-key beam decodes over uniform-random ciphertext × uniform-random
keystream, plus a histogram-preserving shuffle of the real LP2 unsolved stream as the
order-preserving surrogate control (matches I3 §1.2's construction). The `n_skips` value is an
integer in `[0, max_skip*L]`; the empirical tail is the exact histogram.

**Q4 — What three conditionals will the negative carry?**
1. **key space**: uniform-random wrong keys (the null); the surrogate is the real-LP2
   order-preserving shuffle.
2. **decoder relation**: reported for BOTH `keyskip1` (baseline) and `drift_rec`
   (preset `drift`) — the curve is a function of the relation, never one scalar.
3. **register**: `n_skips` is register-BLIND by construction; this is the whole point, and it
   is verified by planting the correct key across all four cost-registers (LP1_REAL, Latin, OE,
   half-vowel English) and showing their `n_skips` separation is register-invariant.

**Q5 — What single observation kills this lane at ≤10% of budget?**
If, in the ≤10%-budget pilot (L=120, M≥5,000 wrong-key decodes + 12 planted keys per
register under `keyskip1`), the planted-key median `n_skips` does NOT clear the wrong-key
null's empirical 99th percentile with a gap ≥ 3 skips on at least the `keyskip` mechanism at
supp≥0.83 — i.e. the statistic cannot separate even the construction it is exact for — the
screen is declared unusable and the lane reports NEGATIVE (an honest instrument-null), and P1
must not lean on `n_skips` as a survival statistic. The kill is checked on the pilot before the
full null runs.

---

## Positive control (doctrine mechanic 2 — plant, prove recovery, THEN trust silence)

Plant, at L=120, seed 3301:
- `enc_keyskip` (the construction `keyskip1` is exact for) at supp∈{0.60,0.83,0.98}
- `enc_skip_by_two` (L7-B's sharp case) at supp∈{0.60,0.83,0.98}

over the four cost-registers {LP1_REAL, Latin, OE, EN_HALFVOWEL} plus EN_MODERN. Hand the
correct key to I1's `beam_decode` under `keyskip1` and `drift` presets. Recovery is
**rune-INDEX** recovery (`driftbeam.recovery`), never the transliteration string. Report the
planted-key `n_skips`, the ground-truth `info['n_skips']`, the wrong-key null `n_skips`
histogram, and the measured separation (planted quantile position in the null).

**Control passes** iff the planted-key `n_skips` clears the wrong-key null's empirical
`q99` (FPR=0.01) for the `keyskip`/supp≥0.83 cells under `keyskip1`, with the separation
reported per register to show register-invariance. The measured recovery of every plant is
stated in RESULTS (a null from a plant that did not recover is not evidence).

## Null (seed 3301, order-preserving)

- **Primary null**: `M_full` wrong-key beam decodes, uniform-random C × uniform-random K,
  seed derived deterministically from 3301, decoded under `keyskip1` and `drift`. Store the
  exact discrete `n_skips` histogram (counts per integer value), not a fit.
- **Surrogate control**: histogram-preserving shuffle of the real LP2 unsolved stream
  (I3 §1.2 construction) at the same L, seed 3301 — the order-preserving null the doctrine
  requires. Its `n_skips` histogram must agree with the uniform null within the pre-registered
  25% tolerance (matching I3 §1.2's own criterion), or the uniform stand-in is rejected.

## Pass/fail threshold (set now, never edited after a result)

**FPR fixed at 0.01.** The screen threshold for each (mode, L) cell is the wrong-key null's
empirical `q99` of `n_skips` (the smallest integer skip count whose right-tail null mass
≤ 0.01). **PASS** requires ALL of:
1. **Control separation**: planted `keyskip`/supp≥0.83 keys' median `n_skips` ≥ null `q99`
   under `keyskip1`, on ALL four cost-registers (register-invariance demonstrated).
2. **Null curve stored**: `nskips_null.json` written at seed 3301, order-preserving, carrying
   the exact discrete histogram + q90/q95/q99/q999 per (mode, L) cell, and the surrogate
   agreeing within 25%.
3. **Schema wired**: `n_skips` + `n_unexplained` appended as SWEEPROW fields 13, 14 under a
   version-bumped `SWEEPROW/2` emitter that stays byte-compatible for the first 13 fields
   (SWEEPROW.md §8), with a validator and a passing round-trip test.

**FAIL / NEGATIVE** if the kill (Q5) fires or control separation is not achieved. A wired
schema + stored curve without control separation is NOT a PASS — it is an instrument that
produced a null it cannot vouch for.

## Kill checkpoint (≤10% budget)

Pilot: L=120, M_pilot=5,000 wrong-key `keyskip1` decodes + 60 planted keys (12/register ×5).
Wall-time budget ≤ 90 s. If Q5 fires here, stop and report NEGATIVE with the measured gap.

## What this lane does NOT claim

`n_skips` is stream-dependent (T3 §5.1) — it is a ranking/screen statistic, not a
plaintext-recovery certificate. A key clearing the `n_skips` q99 is a **candidate for the
expensive I1×I2 adjudication**, not a hit. The Round-20 HIT definition (panel-max null +
recovery≥0.90 + held-out ¾) is unchanged and is P3/S's job, not P2's.

---

## Addendum 2026-08-28 (after the run — NO threshold edited)

Recorded for honesty, per doctrine mechanic 1 ("append dated addenda with the reason"). The
pre-registered threshold and kill condition were **not changed**; the kill fired as written
(L=120 keyskip supp≥0.83 planted median 3 vs null q99 9, gap −6 < 3). Two things the PREREG
framed imprecisely, clarified by the data (they do not move the pass/fail line):

1. **Tail direction.** The PREREG's cond-1 phrasing ("planted median ≥ null q99") implicitly
   assumed the correct key is a RIGHT-tail (high-skip) outlier. Measured: at page-window L the
   correct key infers FEWER skips than the wrong-key fabrication floor (a left-of-bulk position),
   and at full book it infers MORE (a right-tail outlier). The screen is therefore adjudicated
   **two-sided** in `sweeprow2.screen_nskips`. Either way the correct key is in the bulk at
   L≤400, so the negative stands under any tail convention (best two-sided p = 0.207 ≫ 0.01).
2. **Register-invariance** (Q4.3) holds at L=120 (spread ≤4) but is partially refuted at L=400
   (spread up to 19), because the beam picks its skip path by English score. Logged in RESULTS §3.

The instrument is validated (plant recovery 0.992; surrogate ratio 0.987/1.002; full-book
control recovers at 0.999), so the negative is a real bound, not an unvalidated silence.
