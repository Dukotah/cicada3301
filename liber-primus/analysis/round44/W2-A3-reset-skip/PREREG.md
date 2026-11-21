# Round 44 WAVE-2 / Cell A3 — reset+keyskip1 FULL grid (the tier-2 gap closure): PREREG

_Dated 2026-11-09, written BEFORE any sweep output of this cell. Doctrine binds
(`ARMADA-DOCTRINE.md`); standing panel-R36 adjudicator (`round19/I2/adjudicate.py`) + bars_v3
(`round34/I1-v3-null/bars_v3.py`); no `git commit` from this cell. This file is sha256-stamped
into `run.log` before first execution (the R44 X1 hygiene fix)._

## The gap (cited rows, queried & read before writing this)

- **R44-R1-RESET-SWEEP** (negative): its tier-1 negative over the 1,514,700-cell reset grid holds
  at measured power **1.0 only for UNFILTERED reset constructions**; its own gate (G3) measured
  tier-1 power **~0** against the keyskip1-FILTERED reset construction (G3 pages pmax
  13.02/0.92/1.23, recovery 0.675/0.000/0.092 — under bar). The filtered construction was covered
  only by tier-2 (reset-aware keyskip1 beam, G3-validated at recovery 0.989 vs rigid 0.364) on
  **20 cells of 1,514,700**. Its `not_covered` names "keyskip1-filtered resets beyond the 20
  tier-2 cells"; its `reopens_if` names "a cheap full-grid keyskip-filtered reset decoder is
  built (removes the tier-1 unfiltered-only limitation)". **This cell is exactly that.**
- **R33-I2-CONSTRUCTION-AXIS** (measured): reset_per_page / reset_per_line are unrepresented by
  every pre-R44 transition relation; the keyskip patch (`relation_skip_by_k.py`) was shipped
  unapplied. R44-R1 applied it to 20 cells; this cell applies it to the full grid.
- Not re-run: R44-R1 tier-1 (unfiltered application — covered at power 1.0), the
  R44-R1-SEVENGRAM anchor scan (its anchored offset extension measured EMPTY over these 51 keys,
  o ≤ 200, so no anchored extras exist to add), and the 20 tier-2 cells are re-visited only
  incidentally as 20 of 1,514,700 grid cells (0.001%).

## Hypothesis

The LP2 keystream is one of the 51 R44-R1 streams applied with page/line/section resets **through
the output-side anti-repeat (keyskip1) filter** — the construction that reproduces LP2's doublet
rate and that tier-1 of R44-R1 measured itself blind to — and the reset-aware keyskip1 beam
(gate-validated G3 0.989 vs rigid 0.364) recovers it when run over the full grid instead of 20
cells.

## Aiming Test

- **Q1 (hit / recognizer).** A (key, mode, offset, cfg) cell whose beam decode of a real page is
  non-degenerate and crosses the bars_v3 free bar under the STANDING panel
  (`round19/I2/adjudicate.py`, `data/panels/panel-r36.npz`, 12 registers). Positive controls:
  three keyskip1-filtered reset plants (one per mode) enciphered through THIS cell's own glue and
  pushed through the IDENTICAL full-grid sweep — pass iff the planted cell is the grid max on the
  reset-bearing plant page, recovery ≥ 0.85, non-degenerate, pmax ≥ bar, and the rigid
  (non-reset) beam misses (< 0.85) — plus a deep-section depth control (below). No verdict
  without all of them.
- **Q2 (measured prior).** (a) `round44/R1-key-resets/gate.json` G3: measured tier-1 power ~0
  against the filtered construction, i.e. the filtered-reset region of the grid is effectively
  UNSWEPT (20/1,514,700 cells) — a measured instrument hole, not a lore prior. (b) The grid
  itself carries R44-R1's priors: FAM-P = the documented solved-page keystream family
  (`src/lp/ciphers.py`, reproduced by `tests/validate.py`); FAM-G = R18-L1 §6.2 rank-1 generator
  (bash 4.2 `$RANDOM`), seeds from `round20/P3/seedprior20.json`. (c) keyskip1 itself is the one
  construction R18-L7/R33-I2 measured as doublet-consistent with LP2.
- **Q3 (bounded?).** Enumerable and fixed: **51 keys × 30 offsets (0..29) × 6 configs × 3 reset
  modes × 55 pages = 1,514,700 beam cells** — 100% of the R44-R1 tier-1 grid, now at tier-2
  power. **Full grid, no offset subset needed:** measured timing basis (synthetic ciphertext,
  L=232, warm): 0.041 s/decode page-mode, 0.0008 s/decode line-mode ⇒ ≈ 11.6 core-h ≈ ~2 h wall
  on 6 workers — under the 4 h line, so the half-split contingency in the cell brief is NOT
  exercised. Anchored offsets > 29: measured EMPTY (R44-R1-SEVENGRAM), nothing to add.
- **Q4.** See `three_conditionals`.
- **Q5 (kill / checkpoint).** Gate failure (any plant) → **INSTRUMENT-INCOMPLETE**, stop, no
  sweep, no verdict. Sweep checkpoint at 10% of tasks: if projected wall time > 6 h, stop and
  report the completed (mode, key) task list as partial coverage — honest partial beats rushed
  full (charter).

## Construction represented (and the two R1 approximations this cell REPAIRS or carries)

Beam = R44-R1 `resets.py::beam_reset_decode` / `_beam_keyskip1` (beam_w=200, max_rej=3, config
algebra `_transform`), UNMODIFIED — the gate-validated instrument. Application:

- **page mode:** one beam run per page, segments=[L], entry = offset. Exact: the pointer resets
  at every page start by construction.
- **line mode:** one beam run per page, segments = canon-'/'-line lengths, cp carried across
  segments (as in R1 G2/G3 semantics). Exact per page.
- **section mode — REPAIRED vs R1 tier-2:** R1's 20-cell tier-2 entered mid-section pages at
  offset + section_base, assuming ZERO accumulated rejections earlier in the section (expected
  rejections ≈ 0.029/rune ⇒ P(0) ≈ 3% at depth 120 — near-zero power for mid-section pages).
  This cell instead beam-decodes **each red-head section as ONE segment from its start** (13
  sections, map [0,3,6,7,8,15,23,27,33,39,40,53,54]), tracking rejection paths exactly across
  page boundaries, then adjudicates the decode **per page** (same recognizer granularity).
  Keys rebuilt at KEY_LEN 8192 (same generators; first-4096 prefix asserted identical to R1's).
- **Carried blind spots (named, not repaired):** a rejection at the very first visible rune of a
  page (page mode) or of the book (cprev0=None) is unrepresentable (m ≥ 1 needs cp); ≈ 2.9% per
  boundary. Beam alignment-path survival is plant-measured at section depth ≤ 360 and
  extrapolated to the real max depth ~3,400 — the deep-section control (below) measures recovery
  at depth 3,400 for one cell to bound this.

## Fixed thresholds (computed from the committed bars_v3 fit BEFORE any decode)

Bar = `bars_v3.bar_v3(2_000_000, L_cap, "free")`, L_cap = largest of {120, 240, 400, 729} ≤
decode length, floor 120 (standing convention). N_bar = 2,000,000 ≥ actual cells
(1,514,700 real + ≤ 110,160 plant cells), conservative.

| L_cap | bar (pmax) |
|---|---|
| 120 | **15.6736** |
| 240 | **21.1010** |

A cell crosses iff its non-degenerate full-`adjudicate` pmax ≥ the bar at its page's L_cap.
0 crossers → NEGATIVE (conditionals below). Any crosser → **FLAGGED-FOR-ORACLE** per
`HUMAN-ORACLE.md`, never self-certified. Plant bars: recovery ≥ 0.85 (the R33-I2
representability bar, same as R1 G3), planted cell = grid max by panel pmax on the reset-bearing
plant page, non-degenerate, pmax ≥ bar; rigid differential < 0.85. Deep-section control bar:
recovery ≥ 0.85 on the final 120 runes of a 3,400-rune keyskip section (depth control only — not
a grid-max test; stated as measured depth power either way).

## Positive controls (fixed now; enciphered through THIS cell's own glue)

| id | construction | cell | plaintext | seed |
|---|---|---|---|---|
| PA | page resets, keyskip1 supp 0.83, 2×120 | (G-bash-3301, page, o=11, beau_atb) | (PT3+PT1)[:240] | 761 |
| PL | line resets (24-rune lines), keyskip1, 240 | (P-totient, line, o=5, vigp) | PT2[:240] | 1033 |
| PS | section resets, keyskip1, one 3×120 section | (G-bash-1325734783, section, o=3, vigm) | (PT1+PT2)[:360] | 29 |
| PD | deep-section depth control, keyskip1, one 3,400-rune section | (P-prime, section, o=0, vigm) | PT1..3 cycled | 58 |

PT1–PT3 = the F5b-T LP-register known-English controls of record (verbatim from R1
`plant_gate.py`). PA/PL/PS are swept through the FULL 27,540-cell per-page grid (identical code
path as real pages); the grid-max test binds on PA page 2, PL page 1, PS page 3 (base 240). PD is
decoded at its own cell only (depth measurement). **Pre-registered re-roll rule:** if a plant
fails EXACTLY and ONLY by the named first-rune-of-segment rejection blind spot (verifiable from
the encipher trace), the plant is re-rolled with the next unused Cicada seed and the event is
reported in RESULTS; any other failure is INSTRUMENT-INCOMPLETE, full stop.

## three_conditionals

- **key_space:** the 51 R44-R1 keys exactly — P-prime, P-totient, P-phi + bash-4.2-LP64 `$RANDOM`
  (anti-repeat wrapper, mod-29) for seedprior20 top-40 + [3301,1033,761,509,29,58,2,1]; offsets
  0..29 (anchored extension > 29 measured empty by R44-R1-SEVENGRAM). Nothing else.
- **transition_model:** keyskip1-filtered (output-side anti-repeat, any per-site rejection count
  0..3 via max_rej=3) position-indexed substitution (vig±, Beaufort, × atbash-pre) with
  key-pointer reset at canon page / canon-'/'-line / red-head-section boundaries at fixed offset;
  beam_w=200. keyskip2 / skip_by_k≥3 / free drift with resets NOT represented; first-rune-of-
  segment rejections NOT represented (cprev0=None); interrupters treated as ordinary ciphertext.
- **adjudicator_register:** panel-R36 (12 registers), pmax vs `bars_v3 'free'` at N_bar = 2e6;
  the beam's internal search is English-quadgram-guided (the R33-I2 patch limitation — a
  plaintext whose quadgram profile is far from English may be mis-aligned by the beam even when
  the final panel could score it); final scoring panel-R36.

## Coverage statement (to be finalized in RESULTS)

Coverage = 1,514,700 beam cells (100% of the R44-R1 grid, enumerable, full — the preregistered
subset IS the full offset set, per the measured timing basis) at the plant-measured power for
keyskip1-filtered reset constructions (expected ≈ 0.85–1.0 per G3 precedent), with section-mode
power measured at depth ≤ 360 by PS and bounded at depth 3,400 by PD.
not_covered (declared now): everything in R44-R1-RESET-SWEEP's not_covered minus the tier-2 gap
this cell closes — i.e. keys/generators/reductions outside the 51; unanchored offsets > 29;
keyskip2/drift/skip_by_k≥3 with resets; mixed reset modes; other boundaries (sentence, `&`);
canon-'/'-line-map conditionality; interrupter-as-null; first-rune-of-segment rejections;
quadgram-guidance register limitation of the beam search; supp-dependence of the plants
(enciphered at supp 0.83 — the beam itself is supp-agnostic up to 3 rejections/site).

## Disclosure (pre-PREREG contacts with target data)

Before this PREREG was written, two beam decodes of real page 10 were run as TIMING probes
(wall-clock only; outputs never adjudicated, never scored, discarded). The timing basis used in
Q3 was then re-measured on synthetic random ciphertext. No other target contact predates this
file.

## Addendum 2026-11-11 (dated, re-stamped) — timing-basis miss → prior-ranked HALF invoked

The Q3 timing basis (0.041 s/decode page-mode ⇒ ~2 h wall) was measured too optimistically.
On the real sweep the page-mode arms cost ~191 s/task (6 workers), making the full
1,514,700-cell grid project to ~7.3 h at the task-16 (10 %) checkpoint — over the Q5 6 h line.
The built-in checkpoint therefore fired **PARTIAL-ABORT** exactly as pre-registered (artifact
`a3_results_partial_abort.json`: 16 page-mode tasks, 158,400 cells, 0 crossers). Per the cell
brief's half-split contingency and PREREG Q5's "honest partial beats rushed full", the sweep is
re-run over the **prior-ranked HALF of the key space**: the first 26 of the 51 keys in the
PREREG prior order (FAM-P {P-prime, P-totient, P-phi} first, then FAM-G bash seeds in
`seedprior20.json` top-40 order), all 3 reset modes, all 30 offsets, all 6 configs =
757,350 cells (exactly half the grid). **No threshold, bar, key-definition, beam parameter,
adjudicator, or recognizer is changed** — only the key count is halved and the uncovered half
is declared in coverage. New runner `run_sweep_half.py` → `a3_results.json`; the aborted
full-grid attempt is preserved as `a3_results_partial_abort.json`. Dead-man heartbeat (≤10 min)
retained. This addendum is re-stamped into `run.log` before `run_sweep_half.py`'s first output.

## Lane outputs

`a3lib.py` (glue: section map, whole-section beam application, full-grid task runner) ·
`plant_gate.py` → `gate_a3.json` · `run_sweep.py` → `a3_results.json` (refuses to run unless
gate_a3.json AND R1's gate.json both passed) · `run.log` (PREREG sha256 stamp + run entries) ·
`RESULTS.md` · `ledger_rows.json` (drafts; LEDGER.json not modified).
