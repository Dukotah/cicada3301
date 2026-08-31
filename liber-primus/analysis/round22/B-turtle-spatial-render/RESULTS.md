# RESULTS — Round 22 Lane B: Turtle / Spatial Render (G1 + G3)

_Run 2026-08-29. Pre-registration: [`PREREG.md`](PREREG.md) (written and frozen before any
LP2 render was scored). Trust anchor `tests/validate.py` = **ALL VALIDATIONS PASSED** at run
time. Geometry-only adjudicator — no English scorer touches this lane._

## Headline

**Clean null, instrument-validated.** LP2's number stream, drawn as a turtle path across the
full frozen enumeration (3 streams × 6 turn-moduli × 2 turn-interpretations × 2 step-rules =
**72 render combos**), produces **no glyph, no closed figure, no lattice/QR grid, no coordinate
string** that a size-matched, histogram-preserving, order-destroyed shuffle null (seed 3301)
does not also produce. The G3 base32/onion/lat-long pointer decode is likewise a **clean null**.
The renders look, to the eye and to a 6-stat geometry detector, like what they mathematically
are: **constrained lattice random walks.**

This is a **publishable novel artifact** — nobody had ever rendered LP2's number stream as a
path. The result is a *bound*, not a verdict (doctrine R7): it excludes the enumerated turtle
class under a geometry adjudicator, and names what it does not cover.

## Trust anchor & instrument validation (doctrine R1, mechanics 2)

- `python3 tests/validate.py` → **ALL VALIDATIONS PASSED** (reproduces every known solved page).
- **Phase-0 planted-shape control (Q1 / Q5 kill-gate): PASS.** Two known shapes were encoded as
  value streams and pushed through the IDENTICAL turtle+detector pipeline:
  - **closed square** — detector fired on **5/6** stats (`closure` p=0, `self_intersections`
    p=0, `bbox_fill` p=0, `caging` p=0, `components` p=0; `symmetry` p=0.41). Near-zero closure
    and caging, self-intersections ~170× the null mean — the exact "made / closed figure"
    signature. Rendered `artifacts/phase0_square.png` shows a clean square.
  - **block-comb (square-wave)** — detector fired on `symmetry` (p=0, real=1.0 vs null 0.24) and
    `bbox_fill` (p=0). Rendered `artifacts/phase0_blockcomb.png`.
  - **Verdict: the detector SEES a planted shape.** The LP2 null below is therefore
    interpretable — silence means absence of structure, not a blind instrument.

## G1 — turtle render sweep (72 combos)

_Filled from `ledger.json`. Null: 200 histogram-preserving shuffles/combo (seed 3301+k).
"Hit" = a per-stat two-sided empirical p<0.01 vs the null. A shape-stat hit is FLAGGED-FOR-ORACLE
only if BOTH its empirical N=2000 null p is at the floor (0/2000) AND its normal-approx z-tail p
clears the Bonferroni bar α=0.01/(6×72)≈2.3e-5 (see PREREG addenda #1, #2). caging/closure hits
are recorded but not refined (a caged net/path ratio is order-dependence, not a made figure)._

**Combos swept:** 72  |  **null surrogates/combo:** 200  |  **refine N (shape stats):** 2000  |  **runtime:** 208.3s

Per-stat count of combos with an uncorrected p<0.01 departure from the shuffle null (of 72):

| stat | combos p<0.01 | interpretation |
|---|---:|---|
| `closure` | 0 | net/path caging ratio — order-dependence of a value-scaled walk, not a shape |
| `self_intersections` | 0 | crossing count — refined (shape stat) |
| `bbox_fill` | 3 | fill density — refined (shape stat) |
| `caging` | 0 | same net/path ratio — order-dependence, not a shape |
| `symmetry` | 2 | raster symmetry — refined (shape stat) |
| `components` | 1 | connected components — refined (shape stat) |

**Shape-stat refinements run (empirical N=2000 null + z-tail p); flag needs BOTH empirical p at
floor AND z-tail p < 2.3e-5:**
- `value_M6_absolute_unit` / `symmetry`: empirical p = 0.002, z-tail p = 0.127 — clears bar: **no**
- `value_M8_relative_value` / `bbox_fill`: empirical p = 0.002, z-tail p = 1.1e-3 — clears bar: **no**
- `value_M8_relative_value` / `symmetry`: empirical p = 0.000, z-tail p = 4.2e-4 — clears bar: **no** (z-tail above the 2.3e-5 bar)
- `value_M8_relative_value` / `components`: empirical p = 0.012, z-tail p = 2.2e-6 — clears bar: **no** (z-tail below the bar, but empirical p is NOT at the floor → discrete-stat normal-approx artifact; the double-gate correctly rejects)
- `value_M12_absolute_unit` / `bbox_fill`: empirical p = 0.006, z-tail p = 1.0e-2 — clears bar: **no**
- `pi_M6_relative_unit` / `bbox_fill`: empirical p = 0.012, z-tail p = 8.8e-3 — clears bar: **no**

**All six shape-stat candidates fail the flag gate → 0 flagged for oracle.**

**Representative renders** (`artifacts/`, PNGs `.gitignore`d per repo convention, regenerable via
`sweep.py`):
- `value_M4_relative_unit.png` — a square-lattice walk filling a blobby region; no glyph, no
  letters, no QR structure.
- `value_M8_relative_unit.png` — an octagonal-lattice diffuse walk; visually indistinguishable
  from a constrained random walk.

**Reading of the hits.** Several combos show a per-stat p<0.01 departure from the shuffle null —
but that is *expected and uninteresting*: the real prime-value order is not i.i.d., so an ordered
walk differs statistically from a shuffled one on caging/closure/symmetry. The Bonferroni bar
exists precisely to separate that generic order-dependence from a genuine *made* glyph.

**No shape-stat hit cleared the Bonferroni bar.** The uncorrected p<0.01 shape-stat departures (6
combo/stat candidates listed above) all fail the flag gate: none has BOTH an empirical p at the
floor AND a z-tail p below 2.3e-5. **Nothing is flagged for the oracle. Clean geometric null.**

## G3 — coordinate / base32 pointer decode

_From `g3_results.json`. Null: 200 shuffles (seed 3301), null-by-default (excess over shuffle)._

**POINTER_FOUND = False.** No sparse pointer of any tested shape:
- **base32 low-entropy run** (the genuine onion-substring detector): value=16, phi=16, pi=10 —
  all **at or below** the shuffle null mean (16.4 / 16.4 / 11.4) and below the null max (22).
- **lat/long regex** on the digit stream: 0 real, 0 null.
- **coord-pair rate**: real *below* null mean for all three streams. _(Prior-art note, per
  Round-22 red-team: this coord-pair sub-detector re-touches the channel of Round-11 **N2 route (d)
  "coordinate pairs"** — `analysis/round11/…N2` — with a different statistic (plausible-range count
  vs top-pair concentration). Both agree NEGATIVE; this is a distinct statistic on the same channel,
  not a silent re-read of a full lens. The headline base32/onion-pointer and low-entropy-run
  detectors are genuinely new.)_
- Note: the raw `[a-z2-7]{16}`/`{56}` window counts (809 / 231) are identical for real and null —
  they are the trivial base32 tiling of a fully-base32 string, **not** evidence of a pointer;
  they are excluded from the flag logic for that reason.

## Coverage × power (doctrine R2)

- **Coverage:** 72 render combos over the full frozen enumeration (streams {value, π(p), φ(p)} ×
  moduli {4,6,8,12,29,360} × turn-interp {absolute, relative} × step {unit, value}) on the entire
  12,956-rune LP2 0–54 stream; + the G3 base32/onion/lat-long framings. 200 surrogates/combo,
  empirical N=2000 + normal-approx z-tail refinement on any shape-stat p<0.01 hit.
- **Power:** the detector recovers a planted closed square (5/6 stats) and a planted square-wave
  (2 stats) — **measured recovery, not asserted.** A geometrically diffuse English-prose message
  along the path would be missed (that is Lane A/C, not this lane).
- **Not covered** (doctrine R7, reopeners): non-turtle 2D grid reads (Lane G2); moduli outside
  {4,6,8,12,29,360}; step functions other than unit/value; 3D lifts; L-system rewriting;
  interrupter-gated pen-up; per-page (vs book-concatenated) renders; and any structure a
  geometry adjudicator cannot see (prose-along-path).

## Verdict

**NO STRUCTURE BEYOND THE NULL** in the enumerated turtle class, and **NO POINTER** in the G3
decode. The "numbers are the direction" hint, read as literal turtle geometry over this bounded
enumeration, yields a constrained random walk. Instrument validated on a planted shape, so the
null is trustworthy. Bound, not closed — reopeners named above. Any future bar-clearing survivor
is **FLAGGED-FOR-ORACLE, not auto-certified** (R21 L1 seal note).
