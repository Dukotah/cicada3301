# PREREG — Round 22 Lane B: Turtle / Spatial Render (roadmap G1 + G3)

_Pre-registered 2026-08-29, BEFORE any LP2 render was scored. Binding:
[`../../ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). Frozen thresholds below are not
edited after seeing a result; any change is an appended dated addendum._

## Hypothesis (one line)

"The numbers are the direction." The value / prime-index / totient stream of LP2 pages 0–54,
read as turtle turn-and-step instructions, draws a **non-random** path — a glyph, closed
polygon, lattice / QR-like grid, symmetric figure, or (G3) a coordinate / base32 pointer string
— that a symbol-level statistic (IoC, doublet rate, quadgram score) is structurally blind to.

This is a **channel**, not a key: the recognizer is the rendered geometry, not an English scorer.
A clean null is still a publishable novel artifact (nobody has ever rendered LP2's number stream).
Any structured hit is **FLAGGED-FOR-ORACLE**, never auto-certified.

---

## The five Aiming-Test answers (doctrine §1)

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit is a rendered path whose geometry departs from a size-matched random walk in a way the eye
would call "made": high self-intersection with closure (a drawn glyph/polygon), lattice snapping
(grid/QR), an anomalously small or axis-aligned bounding box, or mirror/rotational symmetry. The
instrument is a **structure detector** computing, per render: (1) closure = end-to-start distance /
path length; (2) self-intersection count of the polyline; (3) bounding-box aspect and fill density
(visited-cell fraction on a rasterized grid); (4) net displacement / total path length (a caged
walk ≪ a diffusive one); (5) 4-fold and mirror symmetry score of the visited-cell raster; (6)
connected-component count of the visited-cell set. PLUS a saved PNG per render for the human eye.
Recognition is PROVEN in Phase-0 by planting a known shape (a square-wave spelling of a word, and
a closed polygon) encoded as a value stream and pushing it through the identical pipeline: the
detector must FIRE on the plant. If it cannot see a planted shape, the instrument is broken and the
lane reports that instead of a null.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Three *signed* hints in the solved plaintext point at the number channel as a **direction**:
- page 05 (validated solve): "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED"
  (`tests/validate.py` PASS line for `05.jpg`).
- roadmap-cited koans: "either the words **or their numbers**, for all is sacred" and "their
  **numbers are the direction**" (`analysis/NEXT-ARMADA-ROADMAP.md` lines 15–20, 120–131).
The prior is modest — this is roadmap-labelled "low prior but cheap + genuinely-never-done +
publishable-either-way" (line 150). It is NOT a completeness ritual: it reads a specific signed
imperative ("direction") that no prior round rendered.

**Q3 — Is the space bounded, and by what?**
Fully **enumerable**. streams ∈ {value, prime-index π(p), totient φ(p)} (3). turn-moduli
M ∈ {4, 6, 8, 12, 29, 360} (6) — squares, hexlattice, octlattice, clock, mod-29 group, degrees.
step-rules ∈ {unit, value-scaled} (2). Plus turn-interpretation ∈ {absolute-heading,
relative-turn} (2). Total render combos = 3 × 6 × 2 × 2 = **72**, each rendered once for LP2 0–54.
G3 coordinate/base32 decode adds a small finite set of decode framings (below). No sampling, no
unbounded fog.

**Q4 — The three conditionals the negative carries.**
1. **Key space / rule space:** exactly the 72 enumerated (stream × modulus × step × turn-interp)
   combos + the G3 decode framings below. Not covered: non-turtle 2D reads (that is Lane G2),
   moduli outside the set, step functions other than {unit, value}, 3D lifts, per-page (vs
   book-concatenated) renders except where noted.
2. **Decoder / transition model:** a deterministic turtle (heading integer state, integer/real
   step). Not covered: stochastic turtles, L-systems with rewriting, interrupter-gated pen-up.
3. **Adjudicator register:** a **geometry** recognizer (the 6 detector stats + human eye), NOT an
   English scorer. A message that is English prose along the path but geometrically diffuse would
   be missed here (and is Lane A/C territory). The G3 base32/coordinate framing is the only
   text-shaped adjudicator in this lane and it is explicitly sparse-pointer-only.

**Q5 — The single observation that abandons the lane at 10% of budget.**
KILL CONDITION: if the Phase-0 planted shape is NOT recognised by the detector (detector fails to
separate plant from null), the lane STOPS and reports "instrument broken, null uninterpretable"
rather than sweeping. Checkpoint = end of Phase 0, before the LP2 sweep.

---

## FROZEN rule set (enumerated)

- **streams:** `value = PRIMES[i]`, `pi = i+1` (prime index), `phi = PRIMES[i]-1` (totient).
  Source = `round11/lib_numchannel.py` (already trust-gated). Stream = LP2 pages 0–54 flattened,
  interrupters (F, idx 0) LEFT IN (removing them is a separate render, noted but not in the frozen
  72 — see addendum slot). Length 12,956.
- **turn-moduli M:** {4, 6, 8, 12, 29, 360}.
- **turn-interpretation:**
  - `absolute`: heading = (value mod M) * (360/M) degrees, reset each step (absolute compass read).
  - `relative`: heading += (value mod M) * (360/M) degrees (accumulating turtle turn).
- **step-rules:** `unit` (fixed length 1) and `value` (length = the stream value itself, capped/
  normalised for rasterization only, not for the vector stats).

## FROZEN detector + null

- **Null:** order-destroying, histogram-preserving shuffle, `lib_numchannel.shuffled(seq, seed=3301+k)`.
  Per render combo, draw N=200 shuffled surrogates through the SAME turtle+detector.
- **"Structure beyond a random walk"** is declared for a stat when the real render's value is
  beyond the **empirical 200-sample null band at p < 0.01** (i.e. more extreme than the
  0.5th/99.5th percentile of the null, a two-sided 1% test per stat). To control the multiple
  comparisons across 6 stats × 72 combos, a render is FLAGGED-FOR-ORACLE only if it clears
  **Bonferroni-corrected α = 0.01 / (6×72) ≈ 2.3e-5**, which the 200-sample empirical null cannot
  resolve; therefore any per-stat p<0.01 hit triggers a **refinement pass** (N=10,000 surrogates)
  on that specific (combo, stat) before it may be flagged. FPR target: expected false flags under
  the global null ≈ 6×72×0.01 ≈ 4.3 at the per-stat bar, driven to <0.05 by the refinement bar.
- **Detector stats** (all computed on the real vector path AND every surrogate):
  1. `closure` = |end − start| / path_length (small ⇒ closed figure)
  2. `self_intersections` = count of segment-pair crossings (sampled for tractability, same sampler
     for real + null)
  3. `bbox_fill` = visited-cell fraction inside bounding box on a fixed-resolution raster
  4. `caging` = |net displacement| / path_length (small ⇒ caged, not diffusive)
  5. `symmetry` = max(4-fold rotational, horizontal-mirror, vertical-mirror) IoU of the raster
  6. `components` = connected-component count of visited cells

## Phase-0 positive control (MUST pass before sweep)

Encode two KNOWN shapes as value streams and render through the identical pipeline:
- (a) a closed unit **square** (headings 0,90,180,270 repeated) — must show near-zero `closure`,
  4 self-intersections≈0, high `symmetry`, tiny `bbox_fill` ratio consistent with a square.
- (b) a **square-wave / block-letter** stream spelling a short word.
Detector MUST separate both plants from their shuffled nulls at the frozen bar. Recorded in RESULTS.

## G3 — coordinate / base32 decode (frozen framings)

Take each stream (value, pi, phi) and the mod-M reductions and test for **sparse pointer** output:
- **base32 (RFC 4648 / onion v3 charset):** map the mod-32 reduction of each stream to the
  base32 alphabet; scan for `.onion`-shaped runs (16 or 56 base32 chars) and for high-density
  base32 substrings vs the shuffled null.
- **lat/long:** read consecutive value pairs / digit-concatenations as decimal degrees; flag any
  pair landing in plausible ranges with low-entropy repetition beyond null.
- **decimal / ASCII coordinate strings:** digit-run concatenation scanned for `NN.NNNN` patterns.
Recognizer: presence of a low-entropy, format-valid pointer substring at a rate exceeding the
seed-3301 shuffled null (p<0.01). Null-by-default: random digit streams occasionally match; the
bar is *excess over the histogram-matched shuffle*, not mere existence.

## Outputs

`ledger.json` (coverage × power, per-combo stats + null bands), `RESULTS.md`, a handful of
representative PNGs under `artifacts/` (PNGs are `.gitignore`d per repo convention; JSON stats +
referenced representative PNGs are the committed record).

---

## Addendum 2026-08-29 (refinement-scope, appended after seeing runtime, NOT a threshold change)

The frozen bar is unchanged. During the run, value-step + relative-turn combos produced p==0
hits on `caging`/`closure` (= the same net/path ratio) essentially by construction: value-step
normalizes step length by the max value, so most steps are tiny and the ordered walk is more
*caged* than a histogram shuffle. That is order-dependence, not a *made glyph* — the render is a
diffuse blob (see `artifacts/*.png`). Refining those at N=10,000 (~5.5 min each, ~18 combos)
would burn hours to confirm a non-shape. **Scope decision:** the N=10,000 refinement is spent
only on the SHAPE stats that could indicate a glyph — `symmetry`, `self_intersections`,
`bbox_fill`, `components`. `caging`/`closure` p==0 hits are RECORDED in the ledger (`refined[stat]`
with note) but marked `clears_bonferroni=false` without refinement, because a caged walk is not a
figure. This narrows the flag surface, never widens it — no threshold was loosened.

## Addendum 2026-08-29 #2 (Bonferroni resolution method — methods clarification, bar UNCHANGED)

The frozen flag bar is still Bonferroni α=0.01/(6×72)≈2.3e-5. Discovered at run time: an EMPIRICAL
shuffle null cannot resolve a p that small (2.3e-5 needs ≳43,000 surrogates ≈ 24 min per hit;
across the dense combos this is hours). Resolution (a computation method, not a threshold change):
a shape-stat hit is refined with (i) an empirical N=2000 null AND (ii) a two-sided **normal-
approximation z-tail p** from that null's mean/SD — the standard tractable surrogate for a very
large empirical null, which CAN reach the Bonferroni tail. A combo/stat is FLAGGED-FOR-ORACLE only
if BOTH: empirical p is at the floor (0/2000) AND the z-tail p < Bonferroni. This makes the bar
reachable by a genuine, many-SD geometric outlier (a real glyph) while correctly NOT flagging
generic order-dependence (which sits only a few SD from the shuffle mean). The bar was made
resolvable, never loosened.
