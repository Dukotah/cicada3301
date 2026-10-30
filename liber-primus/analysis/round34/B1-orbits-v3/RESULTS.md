# R34 B1 — the two orbits under pf_v3 + beam_v3 (RESULTS)

_Written 2026-10-30 by the Round 34 coordinator from the lane's on-disk artifacts. The lane agent completed its
controls and its full sweep (`sweep.log` "SWEEP DONE", `sweep_summary_final.json`), then stalled before writing this
file. Every number below is read from `control.json`, `sweep.log`, `sweep_summary_final.json`, `keep_rows.json` and
`sweep_rows.jsonl`; nothing was re-run. Pre-registration: [`PREREG.md`](PREREG.md) (2026-10-29 15:25, before the first
output). Store: `sweep_rows.jsonl` (26,050 SWEEPROW/1 rows + header; `validate_store` passes; `check_r3_store` → `[]`)._

## Verdict

**NEGATIVE, bounded.** No cell clears the L=120 bar at its actual N, let alone the declared-N (1e6) bar; no L=240
re-screen was triggered; nothing is flagged for the oracle; no near-miss (clears actual-N but not declared-N). The
bash `$RANDOM` auto-seed orbit was screened **in full** for both ABIs; the PHP `mt_rand` prior-dense tier ran in
full; the PHP uniform tier reached a stated 0.061 % of 2³² per cell.

## Positive control (run first, `control.json`, `control.log`)

12 cells (6 generators × 2 relations) × (5 EN_MODERN + 5 EN_NOVOWEL plants) through the real chunk path
(pf_v3 screen → v3 L=120 → v3 L=240 → panel): **120/120 recovered, `ALL_PASS True`.**

**Caveat (Round 34 X1, interim observation on `sweep.py:70-71`):** the control keeps only plant windows whose naive
cipher has no doublet in the first 40 runes. Under this generator that selects skip-free plants by construction, so
"all plants pass the prefilter" is guaranteed by the selection, not measured. The control therefore proves the decode
and adjudication path, not the prefilter's power; the prefilter's power is taken from Round 34 I2 **as corrected by
X1** (below).

## What was swept

| cell | seeds screened | fraction of family | survivors decoded (per relation) | relations |
|---|---:|---:|---:|---|
| bash 4.2 LP64 (`bash4.2`) | 77,594,624 (296/296 chunks of 2¹⁸, order Random(3301)) | **1.000** of the 74×2²⁰ auto-seed orbit | 81,414 | keyskip1, keyskip2 |
| bash 4.2 ILP32 (`bash4.2_i32`) | 77,594,624 (296/296) | **1.000** | 80,985 | keyskip1, keyskip2 |
| PHP tier (a) prior-dense, all 4 cells | 48,036 each | 1.000 of the prior-dense list (decoded with no prefilter) | (included below) | keyskip1, keyskip2 |
| PHP tier (b) uniform `default_rng(3301)`, 4 cells (`mt_scale`, `mt_mod`, `php_scale`, `php_mod`) | 2,621,440 each | **0.00061** of 2³² | 3,190 / 3,297 / 3,293 / 3,245 | keyskip1, keyskip2 |

Reduction `%29`, sign −1, offset 0, decode aligned at C[0]. Screen: pf_v3 `lse` over nine registers, m=20, threshold
3.9054 nats (FPR ≈1e-3). Decoder: `beam_v3` panel_max, lam_u=4, beam_w=400, L=120 screen / L=240 gate. Adjudicator:
Round 32 I2 nine-register panel (corpus hashes in the store header). Bars: `round34/I1/bars_v3.py` (Gumbel, family
"lp2"), at the cell's actual N and at the declared N=1e6.

The bash phases took 911 s each. The PHP tier (b) log shows 2,621,440 seeds at t=110 s and then a 38,223 s gap before
"SWEEP DONE": the laptop slept overnight; the sweep resumed and closed out cleanly, but tier (b) did not advance past
the cap window, so its fraction is the honest 0.061 %.

## Best score vs bar, per cell × relation (`sweep_summary_final.json`)

| cell | relation | N actual | best pmax (register, seed) | bar L120 @ actual N | bar L120 @ 1e6 | clears |
|---|---|---:|---|---:|---:|---|
| bash4.2 | keyskip1 | 81,414 | 6.674 (DE, 1394038718) | 8.284 | 9.235 | no |
| bash4.2 | keyskip2 | 81,414 | **7.068** (LP1_REAL, 1354603465) | 8.118 | 9.034 | no |
| bash4.2_i32 | keyskip1 | 80,985 | 6.679 (EN_HALFVOWEL, 1375265595) | 8.282 | 9.235 | no |
| bash4.2_i32 | keyskip2 | 80,985 | 6.762 (LP1_REAL, 1354603465) | 8.116 | 9.034 | no |
| mt_scale | keyskip1 | 3,190 | 5.521 (DE) | 7.055 | 9.235 | no |
| mt_scale | keyskip2 | 3,190 | 5.911 (EN_KJV) | 6.936 | 9.034 | no |
| mt_mod | keyskip1 | 3,297 | 5.806 (LATIN) | 7.068 | 9.235 | no |
| mt_mod | keyskip2 | 3,297 | 5.918 (LP1_REAL) | 6.948 | 9.034 | no |
| php_scale | keyskip1 | 3,293 | 5.826 (EN_NOVOWEL) | 7.067 | 9.235 | no |
| php_scale | keyskip2 | 3,293 | 5.779 (EN_KJV) | 6.948 | 9.034 | no |
| php_mod | keyskip1 | 3,245 | 6.216 (DE) | 7.062 | 9.235 | no |
| php_mod | keyskip2 | 3,245 | 5.454 (EN_MODERN) | 6.943 | 9.034 | no |

The best row in the whole sweep is the same bash seed 1354603465 under keyskip2 that Round 32 B1 and Round 33 B3
already found (7.068; L=240 gate failed in both). The register-aware screen and decoder surfaced no new high row.
Top rows per cell are in `keep_rows.json` (54 rows).

## Coverage × power (the number that matters)

Reach per register = (prefilter power) × (v3 envelope recovery, Round 33 I1) × (seed fraction). Prefilter power is
**not** I2's headline 0.998: Round 34 X1 showed that a key skip fires on the candidate rune and never shows in the
emitted ciphertext, so 37–51 % of true-key heads contain a skip, and pf_v3 passes those at only 0.19–0.34. The
operative pf_v3 power is **≈0.66 EN_NOVOWEL / ≈0.71 EN_MODERN** (X1 `rerun_i2_skipfree.json`); other registers lie
between. v3 recovery at L≥120 under keyskip1/2 is 0.98–1.00 for all nine registers.

| family | seed fraction | ≈reach EN_MODERN | ≈reach EN_NOVOWEL |
|---|---:|---:|---:|
| bash 4.2 LP64 + ILP32 | 1.000 | ≈0.70 | ≈0.65 |
| PHP prior-dense (48,036 seeds) | 1.000 (no prefilter: reach = v3 recovery ≈0.98–1.00) | ≈1.00 | ≈1.00 |
| PHP uniform tier (b) | 0.00061 | ≈0.0004 | ≈0.0004 |

For the bash orbit this is a measured improvement on Round 32 B1 (NOVOWEL ≈0.47 × 1.00 prefilter → ≈0.65), but the
remaining ≈30–35 % of the orbit's true-key mass sits in heads-with-a-skip that no head screen so far passes. That is
the Round 35 target (a skip-tolerant head screen), not a decoder problem.

## The three conditionals (ARMADA-DOCTRINE Q4)

1. **Key space:** bash 4.2 `$RANDOM` auto-seed orbit (`sbrand(tv_sec ^ tv_usec ^ pid)`, 74 prefixes × 2²⁰,
   2012-01-01 … 2014-06-01), LP64 and ILP32, reduction `%29`, offset 0, sign −1, C[0]-aligned — **full**; PHP ≤7.0
   `mt_rand` canonical + legacy twist × scale29/mod29: prior-dense list full, uniform 0.061 % of 2³² per cell.
2. **Transition model:** keyskip1 and keyskip2 under `beam_v3` only. `free`, L=31, resets, advance ≥3: not covered
   (Round 34 I1's control failed at L=31 and for `free`; Round 33 I2 measured the rest unrepresented).
3. **Adjudicator register:** nine-register panel; search is register-aware (v3); **the screen is not skip-aware**
   (reach ≈0.65–0.71 at the orbit level).

## Not covered

- Heads containing a key skip within the first 20 runes (≈30–35 % of true-key mass per X1) — the prefilter gap.
- `free` relation; L=31 (control failed); offsets ≠ 0; signs ≠ −1; reductions other than `%29` / scale29 / mod29.
- PHP 2³² tails: 99.94 % of each twist × reduction cell (→ `R28-L4` queue, bigger hardware).
- bash 3.2 / 4.0 / 4.1 / 5.x; non-auto seeds.
- Registers outside the nine; CY is modern-Welsh-prose.
- The L=240 bar is Gumbel-fitted from 4,679 draws (Round 34 I1) — no row came within 1.0 of it.

## Files

`PREREG.md`, `sweep.py`, `common.py`, `control.json`, `control.log`, `sweep.log`, `sweep_php.log`,
`sweep_summary.json`, `sweep_summary_final.json`, `keep_rows.json`, `sweep_rows.jsonl` (gitignored, 4.2 MB,
regenerable with `sweep.py`), `ledger.json`, `ledger_patches.json` (written by the coordinator).


## Addendum (Round 35 X1, 2026-10-30) -- corrections to the text above

Re-derived from the on-disk artifacts (`round35/X1-redteam/rerun_b1_r34.py` / `.json`). The verdict, the 12-cell table, the 296/296 chunk count and the reach arithmetic stand; these statements do not:

1. **PHP prior-dense tier was prefiltered.** Only the 487 "core" seeds were decoded unfiltered; the 47,549 "dense" seeds went through `chunk_php` (pf_v3), `sweep.py:51-56, 200-212`. So "decoded with no prefilter / reach ~1.00" is wrong for ~99 % of that tier: reach there is ~0.65-0.71 like the bash orbit.
2. **The 38,223 s gap.** `sweep_php.log` shows 1,966,080 seeds at t=110 s and 2,621,440 seeds AT t=38,223 s (not "2,621,440 at t=110 s"). The laptop slept inside the last block and wall-clock consumed the 2,100 s cap; at the pre-sleep rate (~17.9 k seeds/s) the cap alone would have reached ~1 % of 2^32. The 0.061 % is a sleep artefact, not the compute budget. The first sweep invocation also crashed at `php_tier_a` (NameError, `sweep.log`), and PHP ran in a resumed invocation.
3. **`sweep_rows.jsonl` holds PHP rows only (26,050).** The resumed invocation reopened the rows file with mode "w" (`sweep.py:161`; resume skips the bash loop), so the 324,798 bash decodes are not persisted (R3 persistence lost for bash; bash numbers survive in `sweep_summary_final.json`, `keep_rows.json`, `sweep.log`).
4. **Store header fields are stale:** `power_EN_NOVOWEL: 0.998` is the pre-X1 skip-free number (superseded by ~0.66 operative) and `key_space` says "ILP32 stated fraction" although ILP32 ran 296/296 chunks.
5. Timing: the bash phases took 933.7 s (LP64) and 911.1 s (ILP32), not 911 s each.
