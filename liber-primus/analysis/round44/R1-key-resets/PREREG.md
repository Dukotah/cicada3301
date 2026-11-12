# Round 44 / R1 — per-page / per-line / per-section key resets + the p27/p54 7-gram anchor: PREREG

_Dated 2026-11-09, written BEFORE any data output of this lane (no 7-gram computation, no plant, no
decode has been run at the time of writing; the only numbers below computed in advance are the
bars_v3 thresholds, from the committed fit, as the standing rounds do). Plan of record:
`round44/CAMPAIGN-PLAN.md` lane R1. Doctrine binds (`ARMADA-DOCTRINE.md`); panel-R36 + bars_v3;
no `git commit` from this lane._

## Motivation / ledger citations (queried before writing this)

- **R33-I2-CONSTRUCTION-AXIS** (status measured): `reset_per_page` and `reset_per_line` are
  **UNREPRESENTED by every existing transition relation** (best recovery ≤ 0.51 at page length)
  yet recovered 1.00 by known-boundary segmentation; its `not_covered` names "reset to nonzero
  offset", "combined axes", "panel adjudication not run". **No negative row in `LEDGER.json`
  covers a reset construction** — every keystream negative (B-04, R16-KDF, R24-C2,
  R24-C2-EXT-SKIP-GENERATORS, R37-C3-U6A-N5, R42-C3, …) is conditional on a decoder whose key
  pointer never resets.
- **X0 ADJUDICATION item 4** (`round43/X0-firewall/ADJUDICATION.md`, REOPEN, blind sources A1-H4,
  A5-H7): the repeated ciphertext 7-gram (p27:28 / p54:70, identical word-boundary pattern,
  measured fresh by R43-F3) **appears in NO ledger row** — a grep over `LEDGER.json` for
  7-gram/reset rows (run 2026-11-09 before this PREREG) confirms: no row holds the 7-gram; the
  only reset row is R33-I2 itself (measurement, not a negative).
- Adjacent rows NOT re-run: R37-C3-U6A-N5 (totient-ladder keystreams, keyskip1+2, **global/no
  reset**); B-04 and descendants (derived keystreams, global); R24-C2(-EXT) (skip_by_two/global).
  My grid differs from all of them on the reset axis; the single overlapping cell
  (FAM-P at reset offset 0, mode=page ≡ "solved-page stream applied fresh per page") is kept in
  the grid because the historical coverage of that cell is English-only register (L7-A) and
  pre-panel; the panel-R36 register axis extends it (same precedent as R33-B3/R40-B3
  re-adjudication rows).

## Hypothesis

The LP2 keystream is a small deterministic generator stream (the solved-page prime/totient family,
or a top R18-L1 evidence-ranked generator) that **resets at page, canon-line, or red-section
boundaries**, entered at a fixed offset `o`; the repeated ciphertext 7-gram at p27/p54 is then a
key-segment coincidence that constrains (key, mode, offset) alignment, and a reset-aware decoder
(which no prior negative used) recovers the pages.

## Aiming Test

- **Q1 (what a hit looks like / recognizer).** A (key, mode, offset, cfg) cell whose per-page
  decode is non-degenerate and crosses the bars_v3 free bar under panel-R36. The recognizer is the
  STANDING instrument (`round19/I2/adjudicate.py` `adjudicate`/`adjudicate_batch`,
  `data/panels/panel-r36.npz`, 12 registers). Three positive controls are planted **through this
  lane's own extraction+decode glue** (R42 X1 rule — encrypt known plaintexts with reset keys,
  push through the identical sweep) and the lane issues NO verdict unless all plants recover AND
  the rigid (non-reset) decoder demonstrably MISSES them (the differential is the lane's licence).
- **Q2 (measured prior).** (a) R33-I2 measured resets as period-plausible and doublet-consistent
  (0.595–0.599% vs LP2 0.664%, same as every output-side filter) and **unrepresented** — the
  construction axis every existing negative is blind to, per that row's own result field.
  (b) FAM-P prior: the prime/totient streams are the DOCUMENTED keystreams of the solved LP pages
  (`src/lp/ciphers.py` `prime_stream`/`prime_totient_stream`/`totient_stream`;
  `tests/validate.py` reproduces the solves). (c) FAM-G prior: `round18/L1-toolchain/RESULTS.md`
  §6.2 promotes bash `$RANDOM` (rank 1; Ubuntu 11.04–12.04 → bash 4.2) — generator code already
  validated byte-exact in `round19/G1/gen_bash.py`; seed prior = `round20/P3/seedprior20.json`
  (unix seconds a human demonstrably had). (d) The 7-gram: X0 item 4 / R43-F3 §1, chance ≪ 1e-3,
  in no ledger row; verified independently in-lane (step 1) before any anchored use.
- **Q3 (bounded?).** Enumerable and fixed: **51 keys** (3 FAM-P + 48 FAM-G seeds) × **30 offsets**
  (0..29) × **6 configs** × **3 reset modes** × **55 pages** = **1,514,700 base cells**, plus a
  7-gram-anchored offset extension of at most 10 extra offsets per (key, mode ∈ {page, section})
  from o ∈ 30..200 ⇒ ≤ 336,600 extra. Bar computed at **N_bar = 2,000,000 ≥ actual N**
  (conservative: larger N ⇒ higher bar). Actual cell count reported.
- **Q4.** See `three_conditionals` below.
- **Q5 (kill / checkpoint).** GATE (10% of budget): if any plant fails to recover through the
  reset-aware path, or the rigid decoder ALSO recovers the reset plants (no differential), the
  lane reports **INSTRUMENT-INCOMPLETE** and stops — no sweep, no verdict. Independently: if the
  7-gram does not verify from canon (step 1), the anchored-offset extension is dropped and
  reported; the base reset sweep still runs (its licence is R33-I2, not the 7-gram).

## Step 1 — 7-gram verification (before the sweep, after this PREREG)

From canon (`data/krisyotam_runes.txt` via the `%`-page split of `analysis/run_stats.load_pages`,
rune indices; word/line structure from the canon `-`/`/` separators): enumerate ALL repeated
rune-index 7-grams across the 55 unsolved pages; confirm (or refute) the claimed pair
(p27 ≈ pos 28 / p54 near end), its word-boundary pattern identity, and its section-boundary
adjacency under the red-head section map `[0,3,6,7,8,15,23,27,33,39,40,53,54]` (X0/F1 source).
Output `sevengram.json` with positions, patterns, and a chance estimate. The anchor sites
(a = in-page/in-section offset at p27, b = idem at p54) are taken from this measurement.

## Fixed key material (51 keys; all streams length 600, values 0..28)

- **FAM-P (3):** `P-prime` = p_i mod 29; `P-totient` = (p_i − 1) mod 29 (the documented
  solved-page stream); `P-phi` = φ(n) mod 29, n = 2,3,4,… All from `src/lp/ciphers.py` logic.
- **FAM-G (48):** bash **4.2 LP64** `$RANDOM` per `round19/G1/gen_bash.py` (draws through the
  exact `get_random_number` anti-repeat wrapper), reduced **mod 29**. Seeds = the top-40 of
  `round20/P3/seedprior20.json` `order` + the 8 fixed Cicada integers
  [3301, 1033, 761, 509, 29, 58, 2, 1].
- No reversed streams; no other reductions (named in not_covered).

## Fixed sweep (tier 1)

For each unsolved page (55, `load_pages()[:-2]`), each key K (51), each reset mode
m ∈ {**page** (key index = o + position-within-page), **line** (o + position-within-canon-line),
**section** (o + cumulative rune position since the start of the red-head section)}, each offset
o ∈ 0..29 (+ anchored extension below), each decode config in {vigm: p=(c−K); vigp: p=(c+K);
beau: p=(K−c)} × atbash-pre ∈ {off, on: c→28−c} (6):
decode the full page, score via `adjudicate_batch` (panel-R36), full `adjudicate` on any
bar-crosser (degenerate guard per R38-I2).
**Anchored extension** (only if step 1 verifies): for modes page & section, every o ∈ 30..200
(first 10 per key×mode) with K[o+a..o+a+6] == K[o+b..o+b+6] (the same-plaintext reading of the
7-gram) is added to the offset list; anchored-consistency of every cell is also annotated.

## Tier 2 (keyskip-filtered application)

The direct tier-1 decode covers the UNFILTERED application of a reset key. The anti-repeat
(keyskip1) application is covered by the reset-aware keyskip beam — this lane's adaptation of
`round33/I2-construction-axis/relation_skip_by_k.py` (`beam_decode_keyskipk` k=1 +
`decode_with_resets` segmentation, beam_w=200, max_rej=3) — run on the **top-20 tier-1 cells
(global, by pmax) + every crosser**, each on its own page, full `adjudicate`, same bar. Plant G3
measures tier-1's screen power against the filtered construction (reported as a number, not
assumed).

## Thresholds (FIXED before any run; standing instrument)

Bar = `bars_v3.bar_v3(2_000_000, L_cap, "free")` (free null of record, panel-R36 12-register
nodes), L_cap = largest of {120, 240, 400, 729} ≤ decode length, floored at 120 (R42 C1 / R43
F5b-T convention; unsolved pages are L 66–277 so only two values bind). Exact values from the
committed fit, computed 2026-11-09 before any decode:

| L_cap | bar (pmax) at N = 2,000,000 |
|---|---|
| 120 | **15.674** |
| 240 | **21.101** |

A cell crosses iff its non-degenerate full-`adjudicate` pmax ≥ the bar at its page's L_cap.
0 crossers → NEGATIVE (measured, conditionals below). Any crosser → **FLAGGED-FOR-ORACLE** per
`HUMAN-ORACLE.md`, never self-certified. Plant pass bars: identical (plants are scored by the
same loop at the same bar); plant recovery = exact plaintext-index match; differential pass =
rigid decode rune-recovery ≤ 0.5 on the multi-segment plants AND rigid per-page pmax below bar on
the post-reset segments; G3 gate = reset-aware keyskip beam recovery ≥ 0.85 vs rigid keyskip beam
< 0.85 (the R33-I2 representability bar).

## Positive controls (planted through THIS lane's own glue; R42 X1 rule)

- **G1 (page resets, direct):** ~360 runes of known English (3 synthetic pages of 120), encrypted
  c = enc(p, K) so that exactly the swept cell (key=`P-totient`, mode=page, o=7, cfg=vigp)
  inverts it. Appended as synthetic pages; the sweep code does not distinguish them.
- **G2 (line resets, direct):** ~240 runes, 1 synthetic page, canon-style line map (24-rune
  lines), cell (key=`G-bash-1325734783` (seedprior rank 1), mode=line, o=3, cfg=beau).
- **G3 (page resets, keyskip1-filtered):** ~360 runes, 3 synthetic pages, key `P-prime`, o=0,
  cfg=vigm, enciphered WITH the anti-repeat rejection (R33-I2 `enciphers` semantics: a draw whose
  ciphertext would repeat the previous ciphertext rune is rejected and the key pointer advances),
  resets per page. Gated on the tier-2 beam differential; tier-1 pmax on G3 is the measured
  screen power against the filtered construction.

Pass iff G1/G2: grid-best lands in the planted cell on every plant page, plaintext recovered
exactly, non-degenerate, pmax ≥ bar, and the rigid differential holds; G3: beam differential
holds. Any failure → INSTRUMENT-INCOMPLETE, stop.

## three_conditionals

- **key_space:** 51 fixed keys — the 3 solved-page prime/totient streams + bash-4.2-LP64 `$RANDOM`
  mod 29 for 48 fixed seeds (seedprior20 top-40 + 8 Cicada integers); offsets 0..29 plus
  7-gram-anchored offsets ≤ 200. NOTHING else: no other generators, seeds, reductions, or
  reversed/permuted streams.
- **transition_model:** position-indexed substitution mod 29 (vig±, Beaufort, × atbash-pre) with
  the key pointer reset at canon page / canon-line / red-section boundaries at fixed offset
  (tier 1, unfiltered); keyskip1 anti-repeat application covered only by the tier-2 reset-aware
  beam on the top-20 cells + crossers, at the power plant G3 measures. Interrupter runes are
  treated as ordinary ciphertext (the recent-rounds canon-index convention); keyskip2/drift with
  resets not represented.
- **adjudicator_register:** panel-R36 (12 registers), pmax vs `bars_v3 'free'` as tabled; the
  negative extends only to those registers.

## Coverage statement

Coverage = the Q3 grid (≤ 2.0e6 cells, exact count reported) at tier-1 power measured by G1/G2
(expected 1.0 on unfiltered reset constructions) and at the G3-measured power against
keyskip1-filtered ones, PLUS tier-2 beam coverage on top-20+crossers at ≥0.85 recovery power.
not_covered (declared now, finalized in RESULTS): generators/seeds/reductions outside the 51
keys; offsets 30..200 unanchored and >200 at all; reversed streams; keyskip2/drift/free-drift
combined with resets; per-line resets are conditional on the canon `/` line map (R33-I2: "the
LP2 line map is unreliable" — the physical-line caveat carries); interrupter-as-null handling;
mixed reset modes within a page; non-deterministic (pad) keys with resets.

## Lane outputs

`verify_7gram.py`→`sevengram.json`; `resets.py` (keys + decoders); `plant_gate.py`→`gate.json`;
`run_sweep.py`→`r1_results.json`; `RESULTS.md`; `ledger_rows.json` (drafts; LEDGER.json itself not
modified). Partial sweep is an allowed outcome (charter): coverage × power honestly stated beats
a rushed full sweep.
