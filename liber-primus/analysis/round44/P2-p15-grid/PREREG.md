# Round 44 / P2 — the p15 4×4 Arabic grid as key schedule: PREREG

_Dated 2026-11-09, written BEFORE any sweep output. Plan of record: `round44/CAMPAIGN-PLAN.md`
lane P2 (X0 NEW #2). Motivation: `round43/X0-firewall/ADJUDICATION.md` item 18 (**NEW**, blind
A2-H3 + F2 #11) and `LEDGER.json` row **B-12** `reopens_if (iii)` — "any falsifiable
interpretation of the p15 `3299` ink-tone marking" — a reopener never taken. Standing
instrument: panel-R36 adjudicator (`analysis/round19/I2/adjudicate.py`, panel
`data/panels/panel-r36.npz`, 12 registers) + `analysis/round34/I1-v3-null/bars_v3.py` free bar
of record, R42-C1 L_cap convention. No `git` from this lane._

## Input re-derivation (done before this PREREG, per lane order; no decode output yet)

The 16 numbers were re-transcribed by this lane directly from the 2400×3600 master
`data/relikd/p15.jpg` (full-res crop `_grid_fullres.png`, red-pixel bbox computed in-lane):

```
3258  3222  3152  3038
3278 [3299] 3298  2838      [3299] printed in RED (red-pixel bbox sits on cell r2c2 only)
3288  3294  3296  2472
4516  1206   708  1820
```

Verified structure (sympy, in-lane): Δ = 3301 − g gives
`43 79 149 263 / 23 2 3 463 / 13 7 5 829 / −1215 2095 2593 1481`; **14/16 Δ are prime**
(breakers: 4516 → −1215, 1206 → 2095 = 5×419); the red cell's Δ = **2** = Gematria-Primus
value of rune F (the solved pages' interrupter). This matches the blind reading
(`F1-blind/hypothesis_lists.json` A2) and F2 (`F2-inventory/image-channels.md` #11)
independently — the blind agents' numbers are hereby confirmed, not trusted.

## Ledger coverage check (done before this PREREG)

- Grep of all 309 `LEDGER.json` rows for each of the 16 numbers: the only non-incidental hit
  is **B-12** `reopens_if (iii)` (the 3299 ink-tone reopener). Hits on 3222/3298/1206 are
  substring coincidences inside unrelated config counts/hashes (verified in context). The 16
  numbers are key material in **zero** rows. X0 item 18's "no covering row" stamp re-verified.
- Adjacent rows (cited, NOT re-run): **R37-C3-U6A-N5** (totient-ladder keystreams: 8 generators
  × 2 signs × 29 offsets from stream start; `not_covered`: "offsets beyond additive; generators
  beyond the 8") — my generator cells start at *grid-derived prime indices* (up to π(2593)=378)
  and *grid-value totient seeds* (φ(g+i) from g≈3300), far outside the covered 0–28 offsets.
  **R11-N2/N5**, **R22-C**, **R26-C** (prime/totient family, offsets near origin) — same
  distinction. **R43-F6-PAGE56-HASH-KEYSTREAM** (hash-as-keystream, same glue) — different key
  material. **B-12** itself covers line geometry, not the printed numerals.

## Aiming Test

- **Q1 (hit + recognizer).** A hit = some unsolved page decodes to a panel-R36-visible register
  under a grid-derived key. Recognizer = the standing panel + free bar. Three positive controls
  are planted through THIS lane's own extraction+decode glue (R42 X1 rule — not borrowed):
  known plaintexts encrypted with (A) the Δ-keystream, (B) the grid rank-permutation
  transposition, (C) a grid-seeded prime ladder, appended as synthetic pages and swept by the
  identical code. No verdict unless all three recover (cell + plaintext + bar).
- **Q2 (prior).** Measured artifact facts, cited: (i) the 14/16 = 3301−prime structure and the
  unique red cell are *printed deliberate numerals* re-verified in-lane from the master scan;
  (ii) B-12's own unanswered reopener names this object
  (`LEDGER.json` B-12 `reopens_if (iii)`); (iii) X0 item 18 stamps it NEW with blind
  convergence + F2 HIGH (`round43/X0-firewall/ADJUDICATION.md`); (iv) the red Δ=2=F coincides
  with the solved pages' interrupter rune — a measured tie to the known key family.
- **Q3 (bounded).** Enumerable and exact: **N = 12,184 adjudicated cells per page × 55 pages
  = 670,120 decodes** (+ a 16-cell index-map census, measured-only). Arithmetic below.
- **Q4.** `three_conditionals` below.
- **Q5 (kill).** Any planted control failing (wrong cell, degenerate, or < bar) → lane KILLED,
  no verdict. Checkpoint = plants run first, before any real page. If the in-lane transcription
  had disagreed with the blind reading, the sweep would not have run until re-adjudicated.

## Hypothesis

The p15 grid is a key schedule for the 55 unsolved LP2 pages: its values (or 3301−values, the
prime subset, their prime indices, or their decimal digits) act as a repeating/one-shot mod-29
additive/Beaufort keystream; or its value ranks act as a period-16 read-order transposition; or
its values seed the solved-page prime/totient generator family; or its values index pages/runes.

## Fixed key material (all derived from the verified transcription above)

- `G` = the 16 values, `D` = 3301−G, `P14` = the 14 prime Δ in grid order,
  `I14` = their 1-based prime indices `[14,22,35,56,9,1,2,90,6,4,3,145,378,234]`,
  `DIG` = concatenated decimal digits (63 digits; 59 without the red cell).
- **Cell orders (16):** traversals {row-major, col-major, row-major-reversed,
  col-major-reversed} × red-cell treatments {as-is, drop-3299, 3299-first, 3299-last}.
- **Value maps (5):** v1 = g mod 29; v2 = (3301−g) mod 29; v3 = prime Δ mod 29 (prime cells
  only); v4 = prime index mod 29; v5 = decimal digits.

## Fixed sweep (the test matrix — N = 12,184 per page)

Pages: `analysis/run_stats.load_pages()[:-2]` = 55 unsolved pages (L 66–277; 35 pages ≥ 240).
Configs: {vig−: (c−K), vig+: (c+K), beaufort: (K−c)} mod 29 × atbash pre-composition
{off, on: c→28−c first} = 6.

- **(a) Repeating keystreams:** 16 cell orders × 5 maps = 80 keys (Lk ∈ {16,15,14,13,63,59});
  all rotations 0..Lk−1 × 6 configs. Cells: 12 non-drop orders ×(16+16+14+14+63)×6 + 4 drop
  orders ×(15+15+13+13+59)×6 = **11,616**.
- **(a′) One-shot (page-start aligned, decode ≥ 60 convention):** only v5 (Lk=63) qualifies:
  12 non-drop orders × suffix r ∈ 0..3 × 6 configs = **288**. (Shorter keys cannot reach the
  60-rune floor — named in not_covered.)
- **(b) Transposition:** permutation = argsort of G (asc/desc) under {row-major, col-major}
  reading × {perm, inverse} = 8 permutations (D's ranks are identical-by-construction:
  D = 3301−G reverses order; covered), applied as period-16 block transposition over the page
  (tail < 16 left in place) × atbash {off,on} = **16**.
- **(c) Generator seeds (solved-page family, grid-derived starts):** prime ladders
  k[i] = p_(s+i) mod 29 and k[i] = (p_(s+i)−1) mod 29 (φ of prime) for s = π(Δ) at each of the
  14 prime cells (28 streams) + totient ladders k[i] = φ(g+i) mod 29 for each of the 16 values
  (16 streams) = 44 streams × 6 configs, no rotation (the seed IS the alignment) = **264**.
- **(d) Index map (measured-only census, no bar claim at n=16):** G mod 55 and positive-Δ
  mod 55 as page selectors; G and positive-Δ as 0-based rune indices into the concatenated
  12,956-rune unsolved stream (extracted 16-rune strings recorded, row-major + sorted). n=16
  is below any adjudication floor; recorded as measurement, never as verdict.

N per page = 11,616 + 288 + 16 + 264 = **12,184**; total adjudicated decodes = **670,120**.

## Thresholds (fixed BEFORE running, bars_v3 of record, α = 0.01 family-wise per page)

Bar = `bars_v3.bar_v3(12184, L_cap, "free")`, L_cap = largest of {120,240,400,729} ≤ decode
length, floored at 120 (R42-C1 convention; no unsolved page reaches 400):

| L_cap | bar (pmax) |
|---|---|
| 120 | **12.9560** |
| 240 | **17.3303** |

A page crosses iff a non-degenerate decode's panel-R36 pmax ≥ the bar at its decode's L_cap.
Any crosser → **FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never self-certified.

## Positive controls (planted through the SAME glue, swept by the SAME code)

- **PA (keystream):** PT1[:240] encrypted c=(p+K)%29 with v2/row-major/as-is, rotation 7
  → must recover at (v2, RM, as-is, vig−, rot 7), ≥ bar(240), non-degenerate, ≥ 99% runes.
- **PB (transposition):** PT2[:224] block-scrambled with the inverse of the (G, row-major,
  asc, perm) permutation → must recover at that (b) cell ≥ bar(120).
- **PC (generator):** PT3[:240] encrypted c = 28−((p−K)%29) with the φ-of-prime ladder at
  s = π(2593) = 378 → must recover at (t2, s=378, vig+ atbash) ≥ bar(240).
Plaintexts = the three solved-page texts already used by R43/F5bT (English register).
Pass iff all three: grid-best lands on the planted cell, non-degenerate, ≥ bar, plaintext
recovered. Any failure → KILLED, no verdict.

## three_conditionals

- **key_space:** the 16 verified p15 numbers and their derived sets (values, 3301−values,
  the 14 prime Δ, their prime indices, decimal digits) under 16 cell orders (4 traversals ×
  4 red-cell treatments); 8 rank permutations; 44 grid-seeded prime/totient ladder streams.
  Nothing outside the printed grid is in the key space.
- **transition_model:** position-independent additive/Beaufort substitution mod 29 × atbash
  pre-composition, repeating (all rotations) or one-shot (digits only, decode ≥ 60); period-16
  block transposition. **No interrupter/rejection-loop/skip constructions** (beam_v3 models
  not run here) — a grid key used WITH the F-interrupter convention is NOT excluded by this
  lane's negative.
- **adjudicator_register:** panel-R36 (12 registers), direct-decode panel-max pmax
  (`adjudicate`/`adjudicate_batch`), degenerate guard on, free bars_v3 of record as tabled.

## Coverage statement

Covered: the full enumerable grid above (670,120 decodes over all 55 unsolved pages) at
panel-R36 power with the free bar of record, plus the (d) census and the verified
transcription/structure as standing measurements.
NOT covered: interrupter/skip/rejection-loop uses of these keys (the solved-page F-interrupter
convention composed with a grid key); traversals beyond the 4 named (spirals, diagonals,
boustrophedon); digits in bases ≠ 10; one-shot alignments for keys shorter than 60; the grid
composed with other presentation channels (red dots, quote spans); line-indexed (vs
page/rune-indexed) selection; the grid as crib positions; per-page different grid keys.

## Deliverables

`PREREG.md` (this file, first), `run_p2.py`, `p2_results.json`, `p2_census.json`,
`RESULTS.md`, `ledger_rows.json` (drafts; parent applies — `LEDGER.json` not modified here).
