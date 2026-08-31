# P1 — the skip-aware, multi-register PREFILTER SIEVE — RESULTS

_Round 20, Phase P. THE load-bearing lane (R1 named the sieve's absence "the finding", D-ii).
Pre-registered in [`PREREG.md`](PREREG.md) — thresholds frozen BEFORE any real-pad statistic was
measured. Decoder on LP2 is I1 [`driftbeam.py`](../../round19/I1/driftbeam.py) (`keyskip1` exact
baseline + `drift` permissive lam=12,max_free=2). Adjudication never against −5.5; the sieve is a
SCREEN, its survivors go to the I1×I2 adjudicator. This lane scores NO real LP2 decode._

## Verdict

| against the FROZEN PREREG bar | result |
|---|---|
| **PASS gate** (≥0.90 per-register survival on ALL 9 registers at ≥100× reduction) | **NOT MET** |
| **Q5 kill** (≥0.90 on Welsh **and** half-vowel English at ≥100×) | **FIRED** |
| **OVERALL** | **INFEASIBLE** — best simultaneous min(CY, EN_HALFVOWEL) survival at ≥100× reduction = **0.667** (Wilson95 upper bound 0.85 < 0.90) |

**But the lane produced the finding it was built to produce, and it is a large, positive,
register-specific one:** the multi-register lever *repairs the catastrophic register blindness* of
the only prior affordable prefilter. Against real Marsaglia bytes it lifts vowel-dropped English
from **0.000 → 0.800**, half-vowel English **0.067 → 0.667**, Welsh **0.300 → 0.733** — the exact
registers C2 measured the English-only filter throwing away. It just cannot reach the **0.90**
per-register bar the PASS gate demands, because a 24–32-rune decrypt head does not carry enough
signal to retain the true offset 90 % of the time in the hard registers, no matter which LM scores
it. Per doctrine the frozen threshold governs: this is INFEASIBLE for the 0.90 gate, and
[`survival_surface.json`](survival_surface.json) publishes the full surface so Phase S can decide
with numbers, not a scalar. **Consequence (per PREREG Q5): Phase S runs G3 only** (the one space
enumerable end-to-end without a sieve).

**Trust anchor.** `tests/validate.py` → ALL VALIDATIONS PASSED (before + after).
`analysis/round20/P1/test_p1.py` → 4/4 passed.

---

## 1. The positive control — the sieve recognises what it should keep and drops what it should not

Every survival number below is licensed by two controls measured in the SAME run
([`measure_survival.py`](measure_survival.py), real hash-verified Marsaglia bytes, C2's paired
design, `encipher_keyskip` plants at supp=0.83):

- **Negative control (must FAIL): RAND survives 0.000** in every cell (uniform-random "plaintext"
  planted the identical way). The sieve does **not** manufacture survivors — it is a real screen,
  not a leak. (PREREG: void the run if RAND > 0.20; it never exceeded 0.00.)
- **Recogniser (must WORK): LP1_REAL — the register the book actually uses — survives 0.933–1.000**
  and its true offset ranks **0** of ~200,000 wrong offsets (median). The pipeline recovers the key
  it is supposed to keep.
- **Instrument independence:** the Stage-A trigram half reproduces C2's `dense_scan` ranks on the
  English arm exactly (verified on 8 LP1 trials: my `EN_KJV` rank == C2's dense rank on the easy
  cases, and both fail together on the hard LP1 windows — see §4).

This is the measured recovery that makes the negative below a **validated** negative, not an
unproven silence: the sieve works; the 0.90 bar is simply out of reach at page-head lengths.

## 2. THE SURVIVAL SURFACE (Q4 deliverable) — register × decoder-relation × keep-point

Per-register true-key survival on real Marsaglia bytes, PLANT_LEN=120, supp=0.83, seed-3301
order-preserving, n=15 trials/register (n=12 for the drift cell). "A" = Stage-A (rigid, multi-reg
z-max screen); "B" = after Stage-B skip-aware beam re-score. `survival_surface.json` carries all
cells + the three conditionals attached to each.

**The headline comparison — P1 multi-register vs C2's English-only filter, both on real Marsaglia:**

| register | **C2 English-only** (n=30) | **P1 multi-register best** (≥100× red.) | lever |
|---|---:|---:|---|
| EN_MODERN | 0.767 | 0.800 | + |
| EN_KJV | 0.800 | 0.800 | = |
| **LP1_REAL** (the book's register) | 0.767 | **1.000** | ++ |
| LATIN | 0.700 | 0.733 | + |
| OE | 0.600 | 0.800 | ++ |
| DE | 0.633 | 0.800 | ++ |
| **CY (Welsh)** | **0.300** | **0.733** | **+++** |
| **EN_HALFVOWEL** | **0.067** | **0.667** | **+++** |
| **EN_NOVOWEL** | **0.000** | **0.800** | **+++ (from blind)** |

**Read it:** the multi-register max recovers the entire register axis C2's English-only filter was
blind to — EN_NOVOWEL from *totally blind* (0/30) to 0.800, half-vowel from 0.067 to 0.667, Welsh
from 0.300 to 0.733. This is the D-i/D-ii reopener R1 attached: the sieve is now register-aware and
its per-register survival is published. **But not one of the three hard registers reaches 0.90.**

**Decoder-relation axis (the skip channel):** on the motivating `skip_by_two` construction (L7-B's
hole), Stage-B `keyskip1` (rigid) and Stage-B `drift` (skip-aware, exact-for-skip_by_two) were both
measured. Neither lifts survival to 0.90; **drift slightly HURTS** the non-English registers
(EN_NOVOWEL 0.833→0.667, LATIN 0.750→0.667) — the R1 §A.6/B-iv mechanism, replayed at screen scale:
the permissive beam spends its freedom steering *wrong* offsets toward English, so it promotes noise
into the survivor set as often as it rescues a skipped true key at these short heads. **At page-head
lengths the skip-awareness of Stage B is a wash-to-slightly-negative for survival** (it matters for
the full-length adjudication downstream, not for the head screen).

## 3. Why 0.90 is out of reach — the short-head ceiling (the actual finding)

The reduction target (≥100×) is *not* the binding constraint — it is trivially met (fA=1e-2 gives
100× at Stage A alone; the cells report median reductions of 200–10,000). **Survival is the binding
constraint, exactly as PREREG framed the kill.** The ceiling has one cause:

> A 24–32-rune decrypt head does not carry enough language signal to rank the true offset in the
> top 1–0.01 % against ~10⁵–10⁷ wrong offsets more than ~70 % of the time in Latin / Old-English /
> Welsh / half-vowel English. Some plant windows are genuinely low-signal in 24 runes — and C2's
> own English-only filter fails on the *same* hard windows (LP1 survival 0.767, not 1.0, for this
> reason). The multi-register max recovers the offsets a wrong register was hiding; it cannot
> conjure signal that a 24-rune head does not contain.

Lengthening the head is the obvious lever but it does not scale as a *first-pass* screen: the whole
economic point of Stage A is a numpy pass at ~10⁵ offsets/s (9-register max) — a longer head with a
skip-aware decode per offset is the driftbeam's ~10⁴ dec/s/core, which is the D-i cost the sieve
exists to avoid. So the sieve faces a hard trilemma at page-head length: **cheap ∧ ≥0.90-survival ∧
multi-register — pick two.** This lane's parameterisation clears cheap + multi-register (a real
gain over C2, which was only cheap), and lands at ~0.67–0.80 survival on the hard registers.

## 4. Reconciliation with C2 (instrument independence)

C2 measured English-only true-key survival on real Marsaglia at LP1 0.767 / LATIN 0.70 / OE 0.60 /
CY 0.30 / half-vowel 0.067 / novowel 0.000. This lane reproduces C2's English arm exactly (the
Stage-A trigram half is line-compatible; on 8 LP1 trials my `EN_KJV`-only rank tracks C2's
`dense_scan` rank, both succeeding on the easy windows and failing together on the hard ones), and
adds the 8 non-English LMs. The **improvement is entirely attributable to the register axis**, not
to a scoring change — which is the cleanest possible attribution and is why the C2-vs-P1 table is
the load-bearing result.

## 5. Coverage × power (doctrine R2)

- **Coverage.** 4 frozen operating points (mech ∈ {keyskip, skip_by_two} × stageB ∈ {keyskip1,
  drift} × keep ∈ {1e-3, 1e-2}); 9 registers + RAND control; n=15 (12 for drift) plants/register on
  real hash-verified Marsaglia bytes; offset span 200,000/plant (a stated fraction of C2's full 10⁷
  pad — see caveat). ≈ 135 plants × (1 Stage-A pass over 2×10⁵ offsets + Stage-B beam over ≤2000
  survivors) per cell.
- **Power.** *Measured, not assumed.* Correct-key recovery is high (LP1 rank 0, RAND rank ~45,000);
  the negative control is 0.000; the surface is a per-register survival, not a scalar. The sieve's
  power to retain the true key is 0.667–1.000 by register, and **its power to reach the frozen 0.90
  bar on Welsh + half-vowel English is measured to be 0.00** (upper Wilson95 bound 0.85 < 0.90).

## 6. The three conditionals of this negative (doctrine R2 / Q4)

1. **Key space.** Real Marsaglia offset sweep (the honest high-entropy control), 2×10⁵-offset span
   per plant. The INFEASIBLE verdict is stated for *this* screen against *this* offset population;
   it does not touch the `/dev/urandom` branch (unrecoverable by any round).
2. **Decoder relation.** Reported for BOTH Stage-B `keyskip1` (rigid) and `drift` (skip-aware,
   exact-for-skip_by_two); the true loop is `skip_by_two`. Neither reaches 0.90; drift is a wash-to-
   negative for *survival* at head length (it is the downstream adjudicator's channel, not the
   screen's).
3. **Adjudicator register.** All 9 I2 registers measured; the shortfall is on CY, EN_HALFVOWEL,
   LATIN, OE — the surface names each. EN_NOVOWEL survival 0.800 but a hit there is
   detection-not-plaintext (I2), carried forward.

## 7. Caveats / what reopens this

- **Span.** 2×10⁵ offsets/plant, not C2's full 10⁷. A wider span adds more wrong offsets to
  out-compete the true one, so the true survival at full-pad is **≤** these numbers — i.e. the
  INFEASIBLE verdict is if anything *conservative* (real survival would be lower, not higher). The
  reduction factor is a fraction (fA·fB), independent of span, so ≥100× holds at any span.
- **n=15.** Wilson95 CIs are wide (±0.20); but even the *upper* bound on CY and EN_HALFVOWEL (0.85)
  is below 0.90 — the gate is missed with margin, not by noise.
- **Reopens if:** a screen statistic is found that reaches ≥0.90 on CY ∧ EN_HALFVOWEL at ≥100×
  reduction — e.g. a longer head made affordable by a smarter first pass, or a fundamentally
  different register-blind statistic (n_skips is ruled out by P2: it is a full-book channel, no
  page-head power). Until then the sieve is a real improvement over C2 that still does not clear the
  0.90 gate, and Phase S runs G3 only.

## Files

- [`PREREG.md`](PREREG.md) — the 5 Aiming-Test answers, controls, frozen thresholds, kill.
- [`prefilter20.py`](prefilter20.py) — the two-stage sieve (Stage-A multi-register z-max numpy
  screen + Stage-B I1 driftbeam skip-aware re-score); the reusable deliverable.
- [`measure_survival.py`](measure_survival.py) — plants over 9 registers on real Marsaglia +
  RAND control, measures per-register survival (Q1/Q4 harness).
- [`build_surface.py`](build_surface.py) — consolidates the pilots into `survival_surface.json`
  and adjudicates PASS/PARTIAL/INFEASIBLE against the frozen thresholds (never edits a threshold).
- [`survival_surface.json`](survival_surface.json) — the published per-register survival surface +
  the C2-vs-P1 improvement table + overall verdict.
- `pilot_keyskip.json`, `pilot_fA1e2_W32.json`, `pilot_sbt_keyskip1.json`, `pilot_sbt_drift.json`
  — the raw per-cell measurements.
- [`test_p1.py`](test_p1.py) — 4 wiring self-tests (LMs load, Stage-A shapes + zmax, top-offsets
  ordering, plant/noise round-trip).
