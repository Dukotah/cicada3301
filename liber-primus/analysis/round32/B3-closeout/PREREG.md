# R32 / B3 PREREG — closeout: R28-L3 write-up + glibc gen=0 prior-dense first-fire

_Written before the first-fire sweep ran (control run first, sweep second). Doctrine: ARMADA-DOCTRINE.md._

## Part 1 — R28-L3 write-up

Runs **no new sweep**. Reads on-disk artifacts only and writes `analysis/round28/L3/RESULTS.md`. Kill rule
(from CAMPAIGN-PLAN §3 B3): artifacts incomplete or no stored control recovery -> `inconclusive`, not negative.

| Aiming Test | Answer |
|---|---|
| Q1 hit shape + recognizer | n/a, no search. Reported shape is the L3 one: stage-A pmax >= 5.0 then hitfn20 3-clause gate. |
| Q2 measured fact above flat prior | The sweep is finished but unrecorded (`PICKUP-HERE.md`: "cheapest open item"). The only new fact is whether the on-disk record supports a ledger row. |
| Q3 bounded? | Yes: fixed set of files in `round28/L3/`. |
| Q4 conditionals | Copied from what L3 actually did (key space, keyskip1/2, I2 nine-register panel); stated, not assumed English-only. |
| Q5 kill | Missing control recovery or incomplete bulk artifacts -> verdict `inconclusive`. |

## Part 2 — glibc `gen=0` (R19-G3-CORRECTION open row)

Scope: **prior-dense FIRST-FIRE only, not the 2^32 space.** `seed_sweep/sweep.c` gen=0 = glibc `srandom(seed)`
then `random() % 29`, rigid decoder, bar -12.5, no DONE line. This lane re-poses the row under the skip-aware
decoder and the I2 panel on a bounded seed list and files exactly what it covered.

| Aiming Test | Answer |
|---|---|
| Q1 hit shape + recognizer | A seed whose glibc `random()%29` keystream, under driftbeam `pair` or `exact` (sign -1, offset 0, beam_w 64, L=120), decodes LP2 0-54 to a panel `pmax` >= 5.0 (stage A), then crosses the hitfn20 3-clause gate (pair 7.3835 / exact 7.6342 at N=1e6, recovery >= 0.90, held-out 3/4). Rows persisted as SWEEPROW/1 via `round19/I2 adjudicate.to_row`. |
| Q2 measured fact above flat prior | R18-L1: GnuPG 1.4.11 / Ubuntu 11.04–12.04 toolchain puts glibc first. Seed list is prior-dense by the repo's own artifacts: B04 integers/primes, the 3301 family, the 433 `seedprior20.json` PGP-time seconds, YYYYMMDD and unix-midnight for every day 2011–2015, unix top-of-hour 2011–2015, ints 0–2047. R24 C2-EXT covered bash `$RANDOM` (different generator), R26-C covered Perl/drand48 and Py2.7, so skip-aware glibc `random()%29` on these seeds has not been run. |
| Q3 bounded? | Yes: list is enumerated by `sweep.py` (printed in `sweep_summary.json`), ~50k seeds x 2 presets. The full 2^32 is explicitly NOT attempted (166 days through Python; needs the C prefilter). |
| Q4 conditionals | (1) key space: listed seeds only, offset 0, glibc TYPE_3 `random()%29`; no `initstate` sizes, no `rand()`/`srand()` variants other than `random()%29`, no reject-resample or scaled reductions (gens 1, 2 are already full-32 rigid negatives). (2) transition: keyskip1 + keyskip2 only, beam_w 64. (3) register: I2 nine-register panel **as rebuilt in this lane's dir** (see below), EN_NOVOWEL detection-only. |
| Q5 kill | Planted-key control must pass (recovery >= 0.90, HIT=True, screen pmax >= 5.0) in BOTH presets before the sweep file is opened; glibc port must reproduce known `srandom(1)` outputs 1804289383, 846930886, 1681692777. Wall cap 1100 s; unfinished seeds are reported un-run, not sampled. |

**Instrument disclosure (pre-run).** `round19/I2/models/panel.npz` is gitignored and absent on this checkout.
It was rebuilt into this lane's `models/` with the unchanged `build_models.py`. The corpora hashes **differ** from
the I2 commit's `out_build.json` (mabinogion, kjv, welsh files are different downloads; EN/EN_KJV/CY rune counts
differ), so the panel and its null are a *different build* from the one L3 and I3 used. pmax numbers are therefore
comparable only approximately to the 7.38 / 7.63 bars; the bars are applied as frozen constants and this is
stated wherever a number is quoted.

Part 2 verdict language: `negative (bounded, prior-dense list only)` if control passes and nothing reaches a
bar; never "closed" or "exhausted".
