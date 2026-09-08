# Round 28 / L4 — the queued heavy sweeps (DO NOT FIRE until R27 S2 exits + closeout)

_Status 2026-09-08: 25 cells built, gated and frozen in `queued_cells.json`. Every cell's
gate PASSed through the real C screen path (1600/1600 vectors |Δpmax|=0.0, 25/25 plants
flagged, 200/200 false-rejects matched below claim). NOTHING here has swept: the NOW
phase ran only vectors, controls, a 200k micro-null and 50k calibration benches, all
single-thread nice-15. The chain phase launches the queue when S2's cores free up
(recipe in BUILD.md)._

## Frozen bars (PREREG "Bars": per-cell N = 2^32 ceiling, family count disclosed)

- `panelmax_bar("pair",  2^32, 0.01) = 9.638182362052774`
- `panelmax_bar("exact", 2^32, 0.01) = 10.031081507059358`
- candidate bar 5.0 (append-only; 4.6–5.0 below claim — nothing near a bar is dropped)
- **family count: 25 cells.** Each cell's bar is stated at its own N=2^32; the
  family-wise interpretation of any single crosser must account for 25×2^32 ≈ 2^36.6
  total decodes (a Šidák-style family bar would sit ≈0.36 higher; any crosser between
  the per-cell and family-wise bar is still FLAGGED-FOR-ORACLE and adjudicated — the
  oracle, not the bar, certifies).

## Queue order (PREREG Q3; prior-ranked, S3 completeness rituals last)

| # | lane | reducer | relation | offset | est. post-S2 6-thread | prior basis |
|--:|---|---|---|--:|--:|---|
| 1 | L4-php_mt_scale-pair | php_mt_scale | pair | 0 | ≈22 h | CENSUS §C highest-prior open generator; RAND_RANGE is the real pre-7.1 `mt_rand(0,28)` arithmetic |
| 2 | L4-php_mt_scale-exact | php_mt_scale | exact | 0 | ≈12 h | same, one-draw relation |
| 3 | L4-php_mt_mod-pair | php_mt_mod | pair | 0 | ≈12 h | same generator, naive `%29` idiom |
| 4 | L4-php_mt_mod-exact | php_mt_mod | exact | 0 | ≈12 h | |
| 5 | L4-php_php_scale-pair | php_php_scale | pair | 0 | ≈20 h | the twist a REAL 2013 PHP actually shipped (MT_RAND_PHP) |
| 6 | L4-php_php_scale-exact | php_php_scale | exact | 0 | ≈20 h | |
| 7 | L4-php_php_mod-pair | php_php_mod | pair | 0 | ≈12 h | |
| 8 | L4-php_php_mod-exact | php_php_mod | exact | 0 | ≈12 h | |
| 9 | L4-glibc_mod-pair | glibc_mod | pair | 0 | ≈16 h | R19-G3-CORRECTION gen=0 — the one open row of Round 8's own priority order; beam decoder (old rows were rigid) |
| 10 | L4-glibc_mod-exact | glibc_mod | exact | 0 | ≈16 h | |
| 11–25 | S3-{grb5_mod,grb5_rej,shuffle29}-o{1,3,5,7,13} | (as named) | pair | {1,3,5,7,13} | ≈13–24 h each | **completeness rituals, labelled** (R27 PREREG S3: "same interpreter, different idiom"); queue-last per doctrine |

Estimates: ratio of the cell's contended bench to the contended `random29 pair` anchor
(receipts/calibration_bench.txt), scaled by grind27's measured post-throttle 104k
seeds/s sustained (R27 BUILD.md). Wide error bars (S2 contention noise ±30%); the
sweep's own STATUS.json throughput supersedes these at launch. **Whole queue ≈ 15–19
days of 6-core wall time.** If the chain phase cannot afford all 25, cut from the
bottom (S3 cells are labelled completeness rituals) and record the cut in not_covered.

Expected candidate volume: micro-null measured 1.1e-4/seed ≥ 5.0 (1.6× Gumbel 6.95e-5,
inside K2's [0.2×, 5×]) ⇒ ≈470k lines/cell, ≈12M lines ≈ 700 MB candidates.jsonl for
the full queue. Keep the run dir on a disk with ≥ 2 GB free.

## Per-cell launch checklist (the engine enforces 1–3 itself)

1. gate file present and cross-checked against the lane (lane/reducer/relation/offset);
2. gate PASS through the real screen path — (a) vectors (b) plant flagged (c) false-reject;
3. grind27-S1 anchor self-test PASS at launch;
4. after completion: `stage_a28.py --run-dir run --lane <LANE>` batch parity (voids on
   >1e-6), then hitfn20 + `../../round27/oracle_crosser.py` on every claim-bar crosser,
   ORACLE-<seed>.md per crosser, RESULTS.md coverage row updated.

## What is deliberately NOT in this queue

- `wordsize-64` S3 cells — no-op for int seeds (round27/PREREG.md S3), dropped with citation.
- glibc `rand()` as a separate cell — measured identical to `random()` (genval.json);
  cells 9–10 cover both call paths.
- PHP `mt_rand(0,28)` under the MODERN (7.1+) uniform-rejection range algorithm — a
  2013 author cannot run PHP 7.1 (released 2016-12); excluded by date, recorded here
  so nobody "discovers" it later. (The raw 31-bit stream under %29 and badscaling IS
  covered, which is everything a pre-2014 PHP could emit for this reduction.)
- i386-glibc seeding for seeds ≥ 2^31 (ILP32 `long` would wrap differently IF a 2012
  libc read the seed through `long` — the resident glibc reads it int32; conditional
  named in RESULTS.md).
- Everything in CENSUS §C below PHP/glibc priors (.NET, ISAAC, LFSR/Geffe, KISS/WELL,
  BBS-as-seed-space) — still open, still unimplemented, unchanged by this lane.
