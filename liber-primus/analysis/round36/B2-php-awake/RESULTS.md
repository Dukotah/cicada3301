# R36 B2 RESULTS - PHP mt_rand tier, run awake, rows persisted (pf_v4 + beam_v3 panel_max)

Pre-registration: [`PREREG.md`](PREREG.md) (dated 2026-10-30 ~10:54 PDT, before any output; Addendum A records the cap change after a timing probe, also before output). Harness `sweep.py` (one process, nproc=1). Control 385 s; sweep 3,968 s (66 min) wall, inside the ~90-min cap. SetThreadExecutionState was set and no sleep gap occurred (`gaps: []`), `resumes: 0`. Store `sweep_rows.jsonl` was opened once with a header and never reopened in write mode (the harness refuses "w" on a non-empty store; the resume path is "a"). `validate_store` ok (263,906 rows), `check_r3_store` -> `[]`. The header carries the beam_v3 sha256, the pf_v4 frozen point + `frozen_op.json` sha256, the panel.npz sha256 + corpus hashes, and R36-I2's per-cell x relation x register power.

**Result: 0 flagged, 0 near-miss, in all four cells x both relations. Negative, bounded.** Best overall pmax 6.608 (php_scale keyskip1, seed 1,552,094,311, LP1_REAL, tier b) vs the L120 bar 7.941 (actual N) / 9.235 (N=1e6).

## Natural-rate control (real chunk path, 160 plants: 4 cells x 2 relations x 2 registers x 10)
Plants: real `enc_exact` (keyskip1) / `enc_pair` (keyskip2), uniform 32-bit PHP seed, held-out test-half windows, only filter = realised C[:40] doublet-free, NO skip-free selection. "with_skip" = any of C[:24] differs from (P+K)%29. recover = pass both N=1e6 bars (L120 and L240) AND recovery240 >= 0.90. Chunk path = pf_v4 on the 2^16-seed chunk, then v3; unfiltered = the planted seed decoded directly by v3 (tier-a reach).

| register | split | n | pf_v4 pass | chunk-path recover | unfiltered v3 recover |
|---|---|---|---|---|---|
| EN_MODERN | skip-free | 35 | 35 | 35 | 35 |
| EN_MODERN | with-skip | 45 | 44 | 44 | 45 |
| EN_NOVOWEL | skip-free | 37 | 37 | 37 | 37 |
| EN_NOVOWEL | with-skip | 43 | 42 | 42 | 43 |

Gate (>= 3 recoveries in every pooled register x split): passed. By relation: keyskip1 80/80 prefilter, 80/80 recovered, 80/80 unfiltered; keyskip2 78/80 prefilter, 78/80 recovered, 80/80 unfiltered. The two prefilter misses (one EN_MODERN, one EN_NOVOWEL, both with-skip, both keyskip2) are consistent with I2 power ~0.98; every plant the screen passed was recovered. Per-cell x relation split detail is in `control.json` (`per_cell_rel`). v3 recovery given prefilter pass = 1.00 (158/158) and unfiltered v3 recovery = 1.00 (160/160); Wilson lower bound ~0.91 at n = 40 per relation x register. Caveats: per-cell skip/no-skip n = 3-7 (the pooled splits are the gated quantity); control registers are EN_MODERN and EN_NOVOWEL only.

## Per-cell sweep
Tier (a) = the 48,036 prior-dense seeds of Round 34 (487 core + 47,549 dense; identical enumeration, asserted). Subsets: `a_core` 487 seeds decoded UNFILTERED; `a_dense_unf` the first 9,280 dense seeds (list order) decoded UNFILTERED (10-min compute cap); `a_dense_pf` the remaining 38,269 dense seeds through pf_v4. Decoded with no prefilter: 9,767 / 48,036 = 20.3 % of tier (a). Tier (b) = numpy `default_rng(3301)`, 199 blocks of 2^17 = 26,083,328 seeds per cell = **0.6073 % of 2^32 per cell** (the same seeds for all four cells; duplicates not removed). The 1 % target was NOT reached (cap, below).

| cell | a_core unf. best k1 / k2 | a_dense_unf (9,280 seeds) best k1 / k2 | a_dense_pf survivors of 38,269 | tier b seeds -> survivors | N decodes per rel | best pmax k1 / k2 | L120 bar actual N k1 / k2 | L120 bar N=1e6 k1 / k2 |
|---|---|---|---|---|---|---|---|---|
| mt_scale | 4.339 / 4.395 | 5.336 / 5.344 | 44 | 26.08 M -> 23,207 | 33,018 | 6.281 / 6.055 | 7.942 / 7.789 | 9.235 / 9.034 |
| mt_mod | 4.235 / 4.338 | 5.662 / 5.076 | 36 | 26.08 M -> 23,149 | 32,952 | 6.045 / 6.496 | 7.941 / 7.788 | 9.235 / 9.034 |
| php_scale | 4.267 / 4.848 | 5.672 / 5.306 | 29 | 26.08 M -> 23,143 | 32,939 | 6.608 / 6.317 | 7.941 / 7.788 | 9.235 / 9.034 |
| php_mod | 4.768 / 4.344 | 4.931 / 5.448 | 25 | 26.08 M -> 23,252 | 33,044 | 6.179 / 6.271 | 7.942 / 7.789 | 9.235 / 9.034 |

L240 bars (actual N / N=1e6): keyskip1 8.31 / 9.51, keyskip2 8.02 / 9.15 (consulted only for L120 crossers; there were none). The tier-b survivor rate is 8.9e-4 per cell (R35 B1: 8.9e-4; I2 realised FPR 6.7e-4 to 9.6e-4), so the screen behaved as measured. Best-by-subset for every cell x relation and the top-5 lists are in `sweep_summary_final.json`. The best scores come from the largest subset (tier b) and carry non-English panel registers (DE, LP1_REAL, OE, EN_KJV) as `preg`: the noise-maximum pattern, not a plaintext signature.

## Flagged / near-miss
Flagged-for-oracle: none. Clearing the actual-N L120 bar but not the declared-N bar (near-miss): none. Nothing reached the L=240 stage.

## Reach (coverage x power)
reach per register = pf_v4 natural power (R36-I2, quoted per row) x v3 recovery (this control, 1.00) x fraction. Point estimates; the 1.00 recoveries have Wilson lower bounds ~0.91 per relation x register.

| cell | rel | I2 pf_v4 power MODERN / NOVOWEL / HALFVOWEL / LATIN | tier b reach MODERN / NOVOWEL (power x 1.00 x 0.00607) | tier a unfiltered subset (9,767 seeds) | tier a pf_v4 subset (38,269 seeds) MODERN / NOVOWEL |
|---|---|---|---|---|---|
| mt_scale | k1 | .984 / .988 / .976 / .976 | .00597 / .00600 | ~1.00 (v3 recovery) | .984 / .988 |
| mt_scale | k2 | .984 / .988 / .966 / .968 | .00597 / .00600 | ~1.00 | .984 / .988 |
| mt_mod | k1 | .988 / .984 / .958 / .960 | .00600 / .00597 | ~1.00 | .988 / .984 |
| mt_mod | k2 | .982 / .988 / .940 / .972 | .00596 / .00600 | ~1.00 | .982 / .988 |
| php_scale | k1 | .984 / .988 / .960 / .976 | .00597 / .00600 | ~1.00 | .984 / .988 |
| php_scale | k2 | .992 / .980 / .950 / .970 | .00602 / .00595 | ~1.00 | .992 / .980 |
| php_mod | k1 | .986 / .980 / .960 / .980 | .00599 / .00595 | ~1.00 | .986 / .980 |
| php_mod | k2 | .982 / .984 / .944 / .982 | .00596 / .00597 | ~1.00 | .982 / .984 |

Tier (a) overall reach (key is one of the 48,036 listed seeds, equally likely; EN_MODERN/NOVOWEL): 0.203 x 1.00 + 0.797 x (0.98 to 0.99) ~ **0.98 to 0.99** per cell and relation. Tier (b) reach: **~0.6 %** of a uniform key space per cell (0.00595 to 0.00602). HALFVOWEL and LATIN carry the I2 prefilter power only; v3 recovery for those registers was not measured in this control.

## Versus Round 34
R34 PHP tier: tier (a) prefiltered except 487 core; tier (b) 0.061 % of 2^32, rows lost on a write-mode reopen. Here: tier (a) has all 48,036 seeds in coverage (487 + 9,280 unfiltered; 38,269 via pf_v4 at measured power 0.94 to 0.99), tier (b) is 0.607 % per cell (~10x R34) with 263,906 persisted, validated rows. The 1 % goal was not met: blocks cost ~19 s each for the first ~25 min while other lanes shared the machine and ~14 s afterwards (four cells per block); 330 blocks would have needed ~80 to 95 min against the 60-min cap. The cap, not a stall, ended tier b at 199 blocks (3,326 s compute). The remaining 99.39 % of the uniform space is deferred.

## Three conditionals
1. Key space: PHP 5.x `mt_rand` (canonical-mt or legacy php<=7.0 twist) x (scale29 | mod29), offset 0, sign -1, C[0]-aligned; tier (a) 48,036 prior-dense seeds, tier (b) 0.607 % of a uniform 2^32 per cell. Not the full 2^32.
2. Transition model: keyskip1 + keyskip2 under beam_v3; pf_v4 sees <= 2 skips in the 24-rune head; the unfiltered subset sees what v3 sees.
3. Adjudicator register: round32/I2 nine-register panel (not panel-R36; Greek/Hebrew/Norse unseen). Measured reach only for EN_MODERN/EN_NOVOWEL (v3) and the four I2 registers (pf_v4).

## not_covered
The uniform tier beyond 0.607 % (99.39 % of 2^32 per cell unscreened; deferred); the 38,269 dense tier-a seeds were screened by pf_v4 (miss rate 1 to 6 % by register), not decoded unfiltered; heads with >= 3 skips in 24 runes; the `free` relation; L=31; offsets != 0; other reductions / PHP variants beyond these four cells; non-uniform or time-structured seeds outside tier (a); registers outside the nine (and v3 recovery for HALFVOWEL/LATIN unmeasured); control n per cell x relation x register = 10 with skip-split n = 3 to 7; the control with-skip label misses skips landing on an identical key rune (~1/29); tier-b duplicates not removed; bars are per cell x relation at N ~33 k and at N=1e6 (no pooled-across-cells bar).

## Reopens if
An oracle/third verifier flags a row, a true-key head with > 2 skips is shown, or the owner funds the rest of tier b (the harness resumes by block index in append mode; `b_blocks` = 199).

## Files
PREREG.md, sweep.py, control.json, control.log, sweep_rows.jsonl (263,907 lines incl. header), sweep_summary.json (raw), sweep_summary_final.json (bars, top-5, reach), keep_rows.json (pmax >= 6.0), sweep.log, ledger.json, ledger_patches.json.
