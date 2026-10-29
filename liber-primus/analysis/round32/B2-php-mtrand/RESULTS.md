# R32 / B2 RESULTS - PHP `mt_rand` first-fire

_2026-10-28. Pre-registered in `PREREG.md` (written before control/sweep). Control first, sweep second. No git. `LEDGER.json` untouched._

**Verdict: `negative (bounded: tier-a complete for the stated prior-dense list; tier-b ~0.97 % of 2^32; prefilter-lossy; construction-conditional)`.** 0 flagged, 0 hitfn20 gate-3 crossers, 0 near-misses. Not "closed".

## 1. What was swept
PHP 5.x (<= 7.0) engine: `mt_srand(seed)` = `php_mt_initialize` + `php_mt_reload`; `mt_rand()` = tempered u32 >> 1. Two twists: **canonical** (`loBit(s[i+1])`, = PHP >= 7.1 `MT_RAND_MT19937`) and **PHP legacy broken** (`loBit(s[i])`, wrong operand; = PHP <= 7.0 default = `MT_RAND_PHP`). Two reductions: **scale29** = PHP 5 `mt_rand(0,28)` / `RAND_RANGE` = floor(29*n/2^31), and **mod29** = `mt_rand() % 29`. Sign -1, offset 0. 4 key cells x 2 relations (keyskip2 `pair`, keyskip1 `exact`), driftbeam beam_w 64, L120 screen / L240 gate, I2 nine-register panel (corpora hashes in the SWEEPROW header).

`php_mt.py` self-test (all pass): canonical seed 1 first u32 = 1791095845; canonical stream == numpy MT19937 bit-generator over 700 draws; both twists x both reductions == `round28/L4/gen28.py` (itself gated `|delta|=0` against a real php 8.5.4 in both engine modes) over 1100 draws x 5 seeds; vectorised head == scalar. Legacy `mt_srand(1); mt_rand()` = 1244335972, matching my memory of the PHP 5 value (memory only; the binding reference is the R28-L4 php-binary gate; I did not run a PHP 5 binary).

## 2. Positive control (before any null count) - `control.json`, `all_pass: true`
8 plants per cell (EN_MODERN/LATIN alternating, uniform random seeds, planted seed inside a 2^16-seed chunk run through the real `chunk()` path incl. prefilter).

| cell | keyskip2 prefilter pass / recovered+HIT | keyskip1 prefilter pass / recovered+HIT |
|---|---|---|
| canonical, scale29 | 4/8 -> 4/4 | 8/8 -> 8/8 |
| canonical, mod29 | 6/8 -> 6/6 | 4/8 -> 4/4 |
| PHP legacy, scale29 | 7/8 -> 7/7 | 6/8 -> 6/6 |
| PHP legacy, mod29 | 6/8 -> 6/6 | 7/8 -> 7/7 |

Every prefilter-passing plant was recovered (>= 3 per cell everywhere); passer stage-B pmax ~24-28 vs bars 7.3835 / 7.6342.

**Prefilter power** (FPR 6e-4 per cell, null 2^19 uniform seeds; 250 plants per register x cell x relation, mean over 8 cells): EN_MODERN 0.724 (0.70-0.75), LATIN 0.711 (0.66-0.74), DE 0.742 (0.72-0.76), EN_NOVOWEL 0.467 (0.44-0.53). **The prefilter is lossy: 26-53 % of planted keys are dropped before decode.** Not measured: EN_KJV, OE, CY, HALFVOWEL, LP1_REAL as plant registers; free-drift plants. Realised null exceedance 6.0e-4 in all 4 cells.

## 3. Sweep (`sweep.py sweep 2400`, `sweep_rows.jsonl`, `sweep_summary.json`)
Complete at the cap: 2402.8 s wall, one process. **212,218 decodes** (SWEEPROW row for each; `validate_store` 212,218 rows OK; `check_r3_store` returns `[]`); 529 reached stage B (pmax >= 5.0).

| tier | seeds | coverage |
|---|---|---|
| (a) core: B04 ints/primes/strings, 3301-lore, seedprior20 PGP seconds | 487 | all decoded UNFILTERED, 4 cells x 2 relations = 3,896 decodes; coverage 1.00 of the list |
| (a) dense: unix-midnight and YYYYMMDD 2011-2015, ints < 2048, hour-aligned unix 2011-2015 | 47,549 | prefiltered, all survivors decoded (28 / 29 / 18 / 31 survivors in mt_scale / mt_mod / php_scale / php_mod) |
| (b) uniform random sample of 2^32 (np `default_rng(3301)`, with replacement) | 41,680,896 | **0.970 % of 2^32 per twist** (same seeds fed all 4 cells); survivors 28,434 / 23,369 / 25,262 / 26,990 |

The prior list is the same family B3 used (B04 + 3301 family + seedprior20 + dates 2011-2015 + hours + small ints), re-derived in `sweep.py` (not imported from B3). Tier (b) was decoded only for prefilter survivors; no unfiltered sample was run.

## 4. Best pmax vs bar
Bars (hitfn20 `panelmax_bar`, alpha 0.01): declared N=1e6 pair **7.3835** / exact **7.6342**; at actual N (~106k per preset) 6.779 / 6.991. I3's `threshold_for` -5.5 floor governs only the legacy `en` statistic; the pmax bar is the binding claim bar (B1 finding).

| cell | keyskip2 best (seed) | keyskip1 best (seed) |
|---|---|---|
| canonical scale29 | 6.310 (239796724) | 6.856 (3941606801) |
| canonical mod29 | 6.426 (767981132) | 6.135 (1373062580) |
| PHP legacy scale29 | 6.221 (562123959) | 6.439 (28777406) |
| PHP legacy mod29 | 6.237 (3616547152) | 6.008 (3074365973) |

Tier-a core best: <= 4.72 (php_scale keyskip2 seed 1325880000). **No cell reaches even the actual-N bar (6.779 / 6.991), so there are no near-misses and nothing is flagged-for-oracle.** All maxima are consistent with the null tail of ~106k draws per preset.

## 5. Real cost and what remains
Measured: prefilter ~73k seeds/s for all 4 cells together; decodes dominate (~16.8k seeds/s end-to-end at FPR 6e-4). Full 2^32 for the 4 cells at this rate is ~71 h on this laptop (about 100x the sampled 0.97 %); **the remaining 99.03 % of the seed space is deferred to bigger hardware (R28-L4 queue) and is not claimed.** Even then the prefilter drops 26-53 % of keys.

## 6. The three conditionals
1. **Key space:** PHP `mt_srand(uint32)`, offset 0, sign -1, canonical and legacy twist, scale29 and mod29; tier (a) prior list + 0.97 % uniform sample.
2. **Transition model:** keyskip1 + keyskip2 only, beam_w 64, L120 screen / L240 gate.
3. **Adjudicator register:** round32/I2 nine-register panel; EN_NOVOWEL detection-only; claim bar = hitfn20 `panelmax_bar`.

## 7. not_covered
99.03 % of the 2^32 seed space (deferred); the prefilter-dropped 26-53 % of planted keys (skips inside the first 16 runes, vowel-dropped text); registers not planted (EN_KJV, OE, CY, HALFVOWEL); other PHP usages (`rand()`/`srand()`, `mt_rand(1,29)`, `random_int`, microtime/uniqid-derived seeds, `mt_srand()` auto-seed with a pid/time hash, multi-draw-per-rune use); offset != 0; sign +1, reversed, atbash; free-drift and any relation beyond keyskip1/2; LP2 pads not starting at rune 0; flat prior in tier (b); legacy twist verified against the R28-L4 gate (PHP 8.5.4 `MT_RAND_PHP`), not a real PHP 5 binary.

## 8. Reopen
A real PHP 5 binary cross-check; an un-prefiltered stated-fraction sample to measure the lost fraction; the full 2^32 on bigger hardware; other reductions/offsets.

## 9. Coordinator decisions
(1) Whether the R28-L4 PHP queue cells should be re-priced given this 0.97 % tier-b sample, (2) whether to fund an unfiltered sample to bound the prefilter loss, (3) whether the ledger row's `negative-bounded` wording is accepted.
