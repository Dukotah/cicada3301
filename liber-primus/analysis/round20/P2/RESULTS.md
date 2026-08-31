# P2 — the `n_skips` null curve + language-agnostic screen — RESULTS

_Round 20, Phase P. Pre-registered in [`PREREG.md`](PREREG.md) BEFORE any statistic was measured.
Decoder: I1 [`driftbeam.py`](../../round19/I1/driftbeam.py) (`keyskip1` baseline + `drift`
permissive lam=12,max_free=2 — the only decoder allowed on LP2). Null: seed 3301,
order-preserving. Schema: extends I2 [`SWEEPROW.md`](../../round19/I2/SWEEPROW.md) to
`SWEEPROW/2`._

## Verdict

| deliverable | state |
|---|---|
| **(1) positive control — curve separates planted from wrong-key at pre-registered FPR** | **NEGATIVE (validated instrument).** The kill condition fired exactly as pre-registered. |
| **(2) `nskips_null.json` built at seed 3301, order-preserving** | **DONE.** 4 marginal cells + 2 order-preserving surrogate controls + 60 plants + a full-book control. |
| **(3) `n_skips` + `n_unexplained` wired into `SWEEPROW/1`** | **DONE.** `SWEEPROW/2` emitter + validator + round-trip/back-compat test, 4/4 passing. |

**Overall: the schema is wired and the null curve is stored (2 of 3 deliverables PASS), but the
positive control does NOT achieve the pre-registered separation at page-window lengths, so the
PASS gate (which requires all three) is not met. This is a VALIDATED NEGATIVE, not an unproven
silence** — the instrument recovers its plants (median 0.992), the surrogate control validates
the null (ratio 0.987/1.002), and the full-book control separates at 0.999 recovery. The finding
is: **raw `n_skips` is a full-book/long-window statistic, not a page-window screen.**

---

## 1. The pre-registered positive control, measured

PREREG cond 1: planted `keyskip` (the construction `keyskip1` is exact for) at supp≥0.83 must
have median `n_skips` ≥ the marginal wrong-key null's `q99`, on ALL four cost-registers
{LP1_REAL, LATIN, OE, EN_HALFVOWEL}, under `keyskip1`. Measured (`nskips_null.json`):

| L | null `keyskip1` q99 | LP1_REAL | LATIN | OE | EN_HALFVOWEL | pass? |
|---|---:|---:|---:|---:|---:|---|
| 120 | 9 | 2 | 3 | 4 | 3 | **FAIL (all)** |
| 400 | 19 | 14 | 7 | 12 | 14 | **FAIL (all)** |

The planted-key `n_skips` sits in the **bulk** of the wrong-key null, never its tail. Best
(smallest) two-sided empirical p over any cost-register exact cell = **0.207**, an order of
magnitude above the FPR=0.01 target.

**Kill condition (PREREG Q5) FIRED**: at L=120, `keyskip`/supp≥0.83 planted median `n_skips` = 3
vs null q99 = 9, gap **−6** (kill threshold: gap < 3). Fired on the pilot and confirmed on the
full run. The lane reports NEGATIVE, as pre-registered.

## 2. Why — the direction, and the length dependence (the actual finding)

The correct key infers **few** legal skips at short L because, on a high-entropy (sha256) pad, a
wrong key's beam can already fabricate ~2–3 (L=120) to ~9 (L=400) legal single-skip advances by
chance (each skipped position reproduces the previous cipher rune with prob 1/29). The genuine
footprint a real rejection loop writes at L=120/supp0.83 is only ~2–4 skips — **smaller than the
wrong-key fabrication floor**. So at page-window lengths the statistic has no separating power.

The separation T3 §5.1 relies on appears only at **full book**. Measured directly
(`fullbook_control` in the JSON), L=12956, `keyskip` supp=0.83:

| key | `n_skips` | recovery |
|---|---:|---:|
| **correct** | **418** (gt 418) | **0.999** |
| wrong ×4 | 292 / 304 / 304 / 304 | — |

At full book the correct key **recovers its 418-skip footprint** and infers ~118 MORE skips than a
wrong key — a clean **right-tail** separation at 0.999 recovery. (Note: this measures the
wrong-key baseline at ~300, not T3's quoted 1537; the direction and the existence of a full-book
margin are confirmed, the magnitude differs from T3's single-wrong-key figure and is reported
honestly rather than reconciled away.)

**Operational conclusion for P1/S:** `n_skips` is a **long-window** discriminator. It is not a
valid page-window (L≤400) sieve statistic at FPR 0.01, and P1 must not lean on it as one; it
becomes powerful only when the adjudicated window is long enough that the genuine footprint
(≈ supp × doublet-rate × L) exceeds the wrong-key fabrication floor. That crossover is above
L≈400 and reached decisively by full book.

## 3. Register-invariance — partially refuted

PREREG Q4.3 predicted `n_skips` is register-blind. Measured spread of correct-key `n_skips`
across the five registers, per (mech, supp, L):

- **L=120**: spread 2–4 (approximately invariant).
- **L=400**: spread 5–19 (NOT invariant).

The beam picks its skip path by **English** score, so at longer L the recovered path — and hence
the inferred skip count — depends on how well the English-driven beam tracks each register.
`n_skips` is register-*independent by construction* only for the accepted-path definition; the
**realised** count inherits the decoder's English bias at longer L. This is a real caveat on the
"register-blind" claim and is logged for P1.

## 4. The stored null curve (`nskips_null.json`)

Exact discrete tails (histogram + q90/q95/q99/q999), seed 3301, order-preserving. Marginal
wrong-key null (uniform C × uniform K):

| cell | M | mean | q95 | q99 | max |
|---|---:|---:|---:|---:|---:|
| `keyskip1\|L120` | 20,000 | 2.42 | 7 | 9 | 13 |
| `keyskip1\|L400` | 2,000 | 8.75 | 16 | 19 | 23 |
| `drift\|L120` | 2,500 | 10.31 | 18 | 20 | 24 |
| `drift\|L400` | 300 | 31.96 | 43 | 47 | 46 |

The `drift` (permissive) relation fabricates far more skips than `keyskip1` (mean 10.3 vs 2.4 at
L=120), consistent with I3 §5's finding that permissiveness is expensive — a decode's `n_skips`
must be adjudicated against **its own relation's** null, never across relations.

**Order-preserving surrogate control** (histogram-preserving shuffle of the real LP2 unsolved
stream, I3 §1.2 construction): shuffle-mean vs uniform-mean ratio **0.987** (L=120) and **1.002**
(L=400) — both inside the ±25% PREREG tolerance, so the cheap uniform null is a valid stand-in.

**A Gumbel bar is NOT used** (I3 §10.1b): `n_skips` is a small-range integer, its null is
discrete; the stored curve is the exact empirical tail.

## 5. Deliverable 3 — the schema wiring (`SWEEPROW/2`)

[`sweeprow2.py`](sweeprow2.py) appends `n_skips` (field 13) and `n_unexplained` (field 14) to
I2's frozen `SWEEPROW/1`, honouring SWEEPROW.md §8 ("append only, with a version bump"). It does
**not** modify I2's `adjudicate.py` — it composes it:

- `to_row(adj_res, dec_res, kid)` → 15-field row; fields 0..12 are bit-identical to `SWEEPROW/1`.
- `header(...)` bumps `v`→`SWEEPROW/2`, `fields`, and points at `nskips_null.json`.
- `validate_row` requires the first 13 to pass I2's own validator, then fields 13,14 as
  non-negative ints; a bare `SWEEPROW/1` row is **rejected**.
- `validate_store` proves every row also forward-reads as `SWEEPROW/1` (slice `[:13]`).
- `screen_nskips(n_skips, mode, L)` adjudicates against the stored discrete null, **two-sided**
  (the correct-key footprint flips sides with L — §2), never a Gumbel bar.

[`test_sweeprow2.py`](test_sweeprow2.py): 4/4 pass (field order, round-trip + back-compat, reject
a bare /1 row, screen). Collected and passing under repo `pytest` (`70 passed`).

## 6. The three conditionals of this negative (doctrine R2/Q4)

1. **Key space**: uniform-random wrong keys (marginal null) + real-LP2 order-preserving shuffle
   (surrogate). The negative says nothing about a *structured* pad's skip distribution.
2. **Decoder relation**: reported for BOTH `keyskip1` and `drift` (permissive). The curve is a
   function of the relation; the negative on separation is measured under `keyskip1` (the exact
   relation) and would only weaken under `drift` (higher fabrication floor).
3. **Adjudicator register**: `n_skips` is register-independent by the accepted-path definition,
   partially refuted for the realised count at L=400 (§3). The separation negative holds across
   all four cost-registers.

## 7. Coverage / power (doctrine R2)

- **Coverage**: marginal null 20,000 (keyskip1 L120) + 2,000 (L400) + 2,500 (drift L120) + 300
  (drift L400) = 24,800 wrong-key decodes; 10,000 surrogate; 60 plant cells × (1 recover + 1000/300
  on-cipher) ≈ 41,000 on-cipher wrong-key decodes; 5 full-book decodes. Discrete tail is exact at
  these M.
- **Power (of `n_skips` as a screen)**: measured **0** at FPR 0.01 on all four cost-registers at
  L=120 and L=400 (planted median never clears null q99; best two-sided p 0.207). The instrument's
  power to RECOVER the plant is high (median 0.992), which is what makes this a real negative: the
  decode is right, the *statistic* has no separating power at these lengths.

## 8. What reopens this

`n_skips` regains power when the adjudicated window is long enough that the genuine footprint
exceeds the wrong-key fabrication floor — measured to be above L≈400 and decisive by full book
(§2). A P1/S lane adjudicating **whole-page or whole-book** windows may use `n_skips` as a
right-tail screen; a lane adjudicating page-*window* heads (L≤400) must not. The `SWEEPROW/2`
field is stored regardless so the channel is never discarded (doctrine R3) and can be
re-adjudicated at close-out at whatever length a downstream lane actually uses.

## Files

- [`PREREG.md`](PREREG.md) — pre-registration (5 Aiming-Test answers, control, null, threshold, kill).
- [`nskips_lib.py`](nskips_lib.py) — the engine (I1 decode wrapper, discrete-tail builder, null gen).
- [`build_null.py`](build_null.py) / [`finish_null.py`](finish_null.py) — the null + control run.
- [`nskips_null.json`](nskips_null.json) — the stored discrete tails + surrogate + plants + verdict.
- [`sweeprow2.py`](sweeprow2.py) — the `SWEEPROW/2` emitter/validator/screen.
- [`test_sweeprow2.py`](test_sweeprow2.py) — schema round-trip + back-compat test (4/4).
