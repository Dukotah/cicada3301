# Round 44 / P2 — the p15 4×4 Arabic grid as key schedule: RESULTS

_Run 2026-11-09 per [`PREREG.md`](PREREG.md) (dated before any sweep output). Instrument:
panel-R36 adjudicator (`analysis/round19/I2/adjudicate.py`, 12 registers) +
`bars_v3` free bar of record. 670,120 decodes in 10.0 s; plants 3/3 PASS. No `git` from
this lane._

## Verdict

**NEGATIVE** (status: the keystream/transposition/generator grid), plus two **measured**
products: the verified transcription (which discharges B-12 `reopens_if (iii)` — the p15
3299 ink-tone marking now has a falsifiable interpretation, tested) and the index-map
census. **0 crossers / 670,120 decodes; nothing flagged for oracle.**

## 1. The transcription, re-derived (measured)

Re-read in-lane from the 2400×3600 master `data/relikd/p15.jpg` (crop `_grid_fullres.png`;
red-pixel HSV bbox computed in-lane localizes to exactly one cell):

```
3258  3222  3152  3038
3278 [3299] 3298  2838     [3299] = the ONLY red cell (r2c2)
3288  3294  3296  2472
4516  1206   708  1820
```

Structure verified (sieve, cross-checked with sympy): Δ = 3301−g is prime for **14/16**
cells — `43 79 149 263 / 23 2 3 463 / 13 7 5 829 / — — 2593 1481`; breakers 4516 (Δ=−1215)
and 1206 (Δ=2095=5·419); red Δ = **2** = Gematria value of rune F. The blind reading
(F1 A2-H3) and F2 #11 are both confirmed exactly.

## 2. Positive controls (gate) — 3/3 PASS through this lane's own glue

| plant | construction | grid best | planted cell found | pmax vs bar | recovery |
|---|---|---|---|---|---|
| PA | Δ-keystream (v2/RM-asis), vig−, rot 7 | `a:RM-asis/v2:vigm:rot7` | yes | **38.321** vs 17.330 | 1.00 |
| PB | rank-perm transposition (G/RM/asc) | `b:perm/RM-asc:plain` | yes | **35.882** vs 12.956 | 1.00 |
| PC | φ-of-prime ladder, s=π(2593)=378, vig+ atbash | `c:gen/t2-pi378:vigp_atb` | yes | **32.322** vs 17.330 | 1.00 |

Each plant was encrypted by this lane, appended as a synthetic page, and swept by the
identical code; each recovered at exactly its planted cell, non-degenerate, far above bar.

## 3. The sweep (negative)

- Matrix: **N = 12,184 cells/page** (verified at runtime against the PREREG count) × 55
  unsolved pages = **670,120 decodes**: (a) 80 grid-derived keys (16 cell orders × 5 value
  maps) × 6 configs × all rotations = 11,616; (a′) one-shot digits 288; (b) 8 rank
  permutations × atbash = 16; (c) 44 grid-seeded prime/totient ladders × 6 configs = 264.
- Bars of record (fixed in PREREG before running): **12.9560** (L_cap 120), **17.3303**
  (L_cap 240), α=0.01 family-wise per page.
- **Observed global best: pmax 5.341** (`a:RMr-drop/v3:vigm_atb:rot12`, page 21, L=273,
  non-degenerate, preg 7) **vs bar 17.330** — 12.0 z-units below the bar.
  **n_crossers = 0.** Full per-page bests with R3 agnostic statistics (ioc, mds, h2, zl,
  pmax_ne) persisted in `p2_results.json`.

## 4. Index-map census (measured-only; n=16 is below any adjudication floor)

`p2_census.json`: G mod 55 and Δ mod 55 page-selection sequences; runes extracted at the
16 G-indices and 14 positive-Δ-indices of the 12,956-rune unsolved stream (row-major and
sorted). The extracted strings (e.g. `MULHUOEWTLYAGMUBAE`) show no structure; recorded as
measurement, no verdict claimed or claimable at n=16.

## 5. Coverage × power

**Covered** (at plant-demonstrated power ≥ bar, panel-R36, 12 registers): the 16 verified
p15 numbers as (i) repeating mod-29 additive/Beaufort/atbash keystreams under values,
3301−values, the 14 prime Δ, their prime indices, and decimal digits, over 16 cell orders
(4 traversals × 4 red-cell treatments: as-is / drop-3299 / 3299-first / 3299-last) and all
rotations; (ii) one-shot digit keystreams (decode ≥ 60); (iii) period-16 rank-permutation
block transpositions; (iv) grid-seeded prime/totient ladder streams (starts up to
π(2593)=378 — outside R37-C3-U6A-N5's covered 0–28 offsets); over all 55 unsolved pages.

**NOT covered:** interrupter/skip/rejection-loop uses of these keys (the solved-page
F-interrupter convention composed with a grid key — beam_v3 constructions were not run);
traversals beyond the 4 named (spirals, diagonals, boustrophedon); digits in bases ≠ 10;
one-shot alignments for keys shorter than 60; the grid composed with other presentation
channels (red dots, quote spans); line-indexed selection; the grid as crib positions;
per-page different grid keys; semantic readings of the two pattern-breaking cells
(4516, 1206) beyond their numeric values.

## 6. three_conditionals (what this negative is conditional on)

- **key_space:** only grid-derived material as listed above.
- **transition_model:** position-independent additive/Beaufort mod-29 × atbash, repeating/
  one-shot, period-16 block transposition. No interrupters, no skips.
- **adjudicator_register:** panel-R36 (12 registers), direct-decode panel-max, degenerate
  guard on, free bars_v3.

## 7. Reopeners

Reopens if: a construction joins the grid with the F-interrupter/rejection-loop family
(beam_v3-class transition models); or a second grid/numeric panel is found that pairs with
p15 (e.g., the pp49–51 table) suggesting a multi-page schedule; or the 4516/1206 breakers
acquire an independent interpretation that changes the derived key sets.

## Files

`PREREG.md` · `run_p2.py` · `p2_results.json` · `p2_census.json` · `_grid_fullres.png`
(regenerable from `data/relikd/p15.jpg` via the crop coordinates in the lane history) ·
`ledger_rows.json` (drafts; parent applies).
