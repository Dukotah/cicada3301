# P3 — PREREG (panel-max null + seed prior + drift re-baseline)

_Round 20, Phase P. Pre-registered BEFORE any P3 statistic was measured. Binding:
`liber-primus/ARMADA-DOCTRINE.md`. This lane finishes the instrument's adjudicator bar;
it opens no new key space and scores no LP2 decode. It has three independent sub-tasks
(P3a, P3b, P3c), each with its own control and threshold._

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
This is a calibration lane, so its "hit" is a **correctly-calibrated single bar the S-lanes
can adjudicate against**, and its failure mode is a mis-calibrated bar (too loose → manufactured
false positives; too tight → killed power). The recognizer is the **plant-recovery positive
control**: plant the correct `sha256_ctr(CICADA3301)` key over each of the 9 registers, decode
through the *actual* Round-20 instrument (I1 `driftbeam` PRESETS → I2 `adjudicate`), and require
the planted correct-key `pmax` to clear the calibrated panel-max bar at power ≥0.90 on the
LP1_REAL / LATIN / OE / EN_HALFVOWEL registers, while a wrong key on the same ciphertext clears
it in ≤ α of trials. If the bar cannot separate a planted correct key from a wrong one, it is
not a bar. (This is the same P3-recover control I3 ran; re-run here on the repaired `drift`
beam and reported as the instrument's measured recovery.)

**Q2 — What measured fact raises this above the flat rate?**
Not applicable in the key-space sense (no key space is swept). The *prior* being integrated is
P3b's L8 seed ranking, whose evidence is `round18/L8-provenance/TIMESTAMP-SEED-CANDIDATES.json`:
433 unix-second seeds a human demonstrably had in front of them, top = **1325734783** (the
second the 3301 primary key + subkey + UID self-sig were created, 3 independent verified
sources). This is an evidence-derived ordering over each generator's seed axis (doctrine R4),
replacing Round 8's flat "all unix seconds equally likely."

**Q3 — Is the space bounded, by what?**
- P3a null: a fixed simulation. The panel-max null is M wrong-key beam decodes at seed 3301,
  order-preserving. Enumerable and reproducible.
- P3b: exactly **433** candidates, fully enumerated, emitted as a JSON ordering.
- P3c: a fixed grid of k∈{0,50,100,200,450,900} substitution counts × reps, at L∈{120,400}
  and full-book, matched to T3's own x-axis. Enumerable.

**Q4 — The three conditionals the negative carries.**
This lane publishes a *bar* and a *re-baseline*, not a negative, but every number it emits names:
1. **key space / null generator** — uniform-random rune ciphertext × uniform-random keystream
   (P3a), the same null I3 validated against the histogram-preserving LP2 shuffle (I3 §1.2).
2. **decoder transition relation** — reported per I1 preset: `exact`(keyskip1), `pair`(keyskip2),
   `exact_ms8`, and the repaired `drift` (permissive, lam=12, max_free=2). A bar under one preset
   is INVALID under another; each is a separate calibrated cell.
3. **adjudicator register** — the I2 9-register panel behind `pmax`; recovery reported per
   register, with EN_NOVOWEL flagged as detection-not-plaintext (I2 67–81%).

**Q5 — What single observation abandons the lane at ≤10% budget?**
Kill P3a if the plant-recovery positive control fails to reproduce I3's already-published finding
that the **panel-max (`pmax`) bar gives ≥0.90 correct-key power where the English (`en`) bar gives
0.00** on ≥2 non-English registers (Latin/Welsh/half-vowel) — i.e. if the panel-max null this lane
recalibrates does not out-recover the English bar, the whole premise (adopt a panel-max direct
null) is unsupported and the lane reverts to reporting I3's existing cells unchanged. Checkpoint:
the very first plant-recovery run (≈2 min at nrep=6). P3b and P3c are cheap and independent; they
run regardless.

## Positive controls (per sub-task)

- **P3a:** plant correct `sha256_ctr(CICADA3301)` key over 9 registers → `pmax` power at the
  calibrated bar vs a wrong key. Expected (from I3 §7.1): correct-key `pmax` power ≈1.00 on
  LP1/LATIN/OE/half-vowel under `exact`; wrong-key `pmax` power ≈0.00. This is the recovery
  number reported.
- **P3b:** round-trip check — the emitted ordering reproduces rank 1 = seed 1325734783 and
  preserves the L8 tier ordering (A>B>C>D), verified against the source JSON's own `rank` field
  with 0 mismatches.
- **P3c:** the k=0 (clean) cell must reproduce recovery ≥0.99 and correct/wrong separation under
  BOTH the old `fastbeam` (keyskip1) and the new `drift_rec` beam — proving the re-baseline
  instrument is wired correctly before its derail curve is trusted.

## Null (order-preserving surrogate, seed 3301)

P3a's null generator is seeded at 3301 and is order-preserving by construction (each wrong-key
beam decode is an independent draw from uniform ciphertext × uniform keystream; no reordering of
the real LP2 stream). I3 already validated this null against a histogram-preserving shuffle of the
real LP2 stream (I3 §1.2: β ratios 1.145 / 0.952, both within the pre-registered 25%). This lane
inherits that licence and re-verifies G-CAL on its own freshly-generated panel-max null.

## Pass/fail thresholds (set now, before any result)

- **P3a PASS** iff: (i) a single canonical panel-max bar is published per I1 preset with its
  (μ, β, M, α, cell-key) recorded; AND (ii) the plant-recovery control shows correct-key `pmax`
  power ≥0.90 on LP1_REAL/LATIN/OE/EN_HALFVOWEL at the published `exact` bar, with wrong-key
  `pmax` power ≤0.05 on all 9 registers; AND (iii) G-CAL on the freshly-generated panel-max null
  passes (exceedance ratio within 20% of nominal at every gating block, OR conservative). If the
  drift-preset pmax cell can be strengthened beyond I3's M=15,000 within budget, do so and mark it;
  otherwise carry it forward at M=15,000 as PROVISIONAL (its status is unchanged, not degraded).
- **P3b PASS** iff the 433-candidate ordering is emitted as a machine-readable prior file with
  rank 1 = 1325734783, tier ordering preserved, 0 mismatches against the source, plus a documented
  helper that maps a candidate list onto any generator's seed axis.
- **P3c PASS** iff the derail curve and the drift-on-OE `pmax` shortfall are BOTH re-measured under
  the repaired `drift_rec` beam and reported against I3's `keyskip1`-measured baselines
  (T3 §5: K-REC k=450, 50% derail at k=450 full-book; I3 §7.2: OE median `pmax` 13.40 vs bar 13.84,
  shortfall 0.44). PASS is the *reporting* of the re-baseline with its k=0 control green; the
  fragile-decode-channel bound is CONFIRMED if the drift beam does not push K-REC materially past
  k=450 (i.e. the decode channel stays fragile at the located-set error count).

- **P3 (whole lane) PASS** = P3a ∧ P3b ∧ P3c all PASS.

## Kill condition at ≤10% budget
Stated in Q5. Re-checked: if validate.py stops passing at any point, halt (doctrine mechanic:
the trust anchor is the basis for every negative). Time-box: ≤15 min wall-clock total compute.
If the full plant grid or a stronger drift-null exceeds budget, run a stated-fraction sample and
report the exact coverage fraction + extrapolated full cost; never leave a process running longer.

## What this lane does NOT do
- No LP2 decode is scored (no S-lane runs here; the P-gate is not yet released).
- No threshold is edited after seeing a result (doctrine mechanic 1). Any change is a dated addendum.
- No rigid decoder is used on LP2; no fixed −5.5 bar is adjudicated against (doctrine).
