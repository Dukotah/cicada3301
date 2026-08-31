# PREREG — Round 21 / L2 — `n_skips` power-crossover length

_Written before any sweep. Binding: `liber-primus/ARMADA-DOCTRINE.md`. Trust anchor
`python3 liber-primus/tests/validate.py` prints ALL VALIDATIONS PASSED (5/5) before this lane
runs. Seed 3301, order-preserving, reusing the Round 20 P2 assets
(`round20/P2/nskips_lib.py`, `nskips_null.json`, the `SWEEPROW/2` wiring)._

## The scientific question

P2 (Round 20) established the two endpoints of one instrument statistic, `n_skips` — the number
of key positions the winning beam path advanced BEYOND one-per-rune, i.e. the footprint of the
encipherer's rejection loop:

- **L = 12956 (full book):** correct key recovers its 418-skip footprint (recovery 0.999) and
  sits ~118 skips ABOVE the wrong-key band (~300) — a clean right-tail outlier. `n_skips`
  **separates** planted from wrong-key. (`round20/P2/nskips_null.json:fullbook_control`.)
- **L ∈ {120, 400} (page window):** the genuine footprint (2–14 skips) is too small to clear
  the wrong-key null; best two-sided p on any exact cell = 0.207 ≫ FPR 0.01. `n_skips`
  **does not separate**. (`round20/P2/nskips_null.json:control_verdict`, PICKUP-HERE item #4.)

**The one unmeasured number: at what sequence LENGTH L does `n_skips` cross over from
non-separating to separating?** This lane sweeps L on a geometric ladder in (400, 12956) and
reports the smallest L at which the planted-vs-wrong-key separation crosses the pre-registered
FPR = 0.01. That crossover length is the window-length gate any future concatenated-page /
whole-book `n_skips` adjudication must respect.

This is an **instrument** lane (≈30% doctrine share). It aims at the statistic, not at the key
space. It opens no new key-space sweep. It reports a bound (a length), never a verdict.

---

## The Aiming Test — five answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
A "hit" here is not a plaintext; it is a *measured crossover length*. The recognizer is defined
before the run: for each L, plant a ciphertext made by a real `keyskip` rejection loop
(supp = 0.83, the observed LP2 doublet-suppression rate), decode it with the correct key under
I1's `keyskip1` exact relation, and compare the correct key's `n_skips` against a size-matched
wrong-key null of the SAME L. Separation at L is declared iff the correct-key two-sided
empirical p ≤ FPR = 0.01 (equivalently, correct `n_skips` sits in the ≤0.5% tail of the
wrong-key discrete distribution on the side its footprint occupies at that L). The crossover
L* is the smallest ladder point at which separation holds AND holds monotonically for all larger
ladder points measured. **Validation that the instrument can see its own hit:** Q1-gate below.

**Q1-gate (endpoint reproduction — must pass before intermediate Ls are trusted).** The sweep
re-derives the two R20 endpoints from the same machinery:
- at L = 400 the correct-key two-sided p must be ≫ 0.01 (no separation; R20 got p ≈ 0.21), and
- at L = 12956 the correct key must recover ≥ 0.99 and its `n_skips` must clear the wrong-key
  band on the right (R20: 418 vs ~300).
If either endpoint does not reproduce, the null build is broken (Q5 kill) — STOP, do not report
a crossover.

**Q2 — What measured fact raises this family's prior above the flat rate?**
This lane changes no prior on the *key* space; it measures an instrument property. The evidence
that `n_skips` carries real signal at large L is already on file:
`round20/P2/nskips_null.json:fullbook_control` (418 vs ~300 at L=12956, recovery 0.999) and
T3 5.1 (margin 418 vs 1537 at full book, 98.4% transcription-robust at k=450). The lane's value
is not a prior lift but a **coverage×power curve for the statistic as a function of L** — the
number PICKUP-HERE item #4 says a future page/book adjudication needs.

**Q3 — Is the space bounded, and by what?**
**Enumerable.** A fixed simulation over a geometric ladder of ~9 L values in (400, 12956), seed
3301: L ∈ {400, 600, 900, 1200, 1600, 2400, 3600, 6000, 9000, 12956}. Per L: one planted
positive control (plant+recover, all 5 registers at the primary L subset; LP1_REAL at every L)
and a size-matched wrong-key null of M = 300 uniform-random ciphertext×keystream decodes (the
primary null), plus, where L leaves slide room in the 12956-rune real stream, the
order-preserving shuffle surrogate. Cost measured: ~0.3–1.0 ms/rune/decode. Total budget
≈ 9 Ls × (300 wk + a few plants) — a bounded few-hour background run, not a fog.

**Q4 — The three conditionals this lane's result carries.**
1. **Key space:** none swept — this is an instrument measurement, not a key search. The plant
   uses the correct key; the null uses uniform-random wrong keys. Coverage is over L, not keys.
2. **Decoder's transition model:** I1's `keyskip1` exact relation (baseline) is the reported
   channel; the `drift` permissive preset is measured as a secondary column. `skip_by_two` is
   included as a second plant mechanism (R18 L7-B: the beam misses it — so its crossover, if
   any, is a separate curve and is reported separately, never merged with `keyskip`).
3. **Adjudicator's register:** `n_skips` is a language-agnostic path statistic — it depends on
   the rejection loop and keystream, not the plaintext register. The lane demonstrates this by
   planting the identical loop over ≥2 registers (LP1_REAL + one hard register) at the crossover
   neighbourhood and confirming the crossover L is register-invariant (PREREG Q4.3 of P2). The
   register axis therefore does not gate this result; that invariance is itself a reported datum.

**Q5 — The single observation that abandons this lane at 10% of budget.**
The Q1-gate. Checkpoint: the FIRST two decodes the sweep does are the two endpoints (L=400 and
L=12956). If L=400 shows separation (p ≤ 0.01) OR L=12956 shows no separation, the null build
does not match R20 and the instrument is not the one P2 measured — KILL, write RESULTS.md stating
the endpoint mismatch, report NO crossover, and do not spend the ladder budget.

---

## Threshold (pre-registered, not to be edited after seeing results)

- **FPR = 0.01**, two-sided (P2 established the correct-key footprint can sit on either side of
  the wrong-key median depending on (L, supp); the sign settles to the right tail as L grows,
  but the test is two-sided to stay honest across the ladder).
- **Separation at L** ⟺ correct-key two-sided empirical p ≤ 0.01 against the size-matched
  wrong-key null at that L.
- **Crossover L\*** = smallest ladder L with separation that persists for all larger measured L.
- **Positive control** = the plant-recovery: correct-key recovery ≥ 0.90 at every L (if the
  beam cannot recover the plant at some L, `n_skips` at that L is not interpretable and the point
  is flagged, not scored).

## Coverage × power to be reported

- **Coverage:** the ladder of L values actually simulated, with M (null size) and plant count
  per L, and the fraction of (400, 12956) it brackets. This is a coverage over LENGTH, stated
  explicitly (doctrine R2/R7 — bounds not verdicts).
- **Power:** for each L, the measured plant recovery (instrument-validation) AND the correct-key
  separation p under the size-matched null, per decoder channel (`keyskip1`, `drift`) and per
  plant mechanism (`keyskip`, `skip_by_two`). The headline is the crossover L\* and the p-curve
  around it; RESULTS.md reports coverage × power as a single line per the doctrine.

## Persisted language-agnostic statistics (R3, non-negotiable)

`nskips_crossover.json` stores, per (L, channel, mechanism, register): the full wrong-key
discrete histogram (not a fit), correct-key `n_skips`, ground-truth `n_skips`, recovery,
two-sided p (p_left / p_right), and the R20 endpoints reproduced. `ledger.json` records
coverage (the L ladder) × power (the crossover L\* and per-L separation) in the SWEEPROW/2
schema. No English score gates anything here; `n_skips` is register-blind by construction.
