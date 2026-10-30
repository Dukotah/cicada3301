# Round 36 / P1 - panel-R36, the recorded gate: RESULTS
2026-10-30. Pre-registered in `PREREG.md` (written before any build). No git, one Python process at a time, nproc=1, ~25 min wall. Status: measured (instrument / governance). Nothing here is a decode or key-space result.

## Verdict
Panel-R36 (12 registers, built from disk, 53 inputs recorded) is built, **byte-reproducible**, and **passes the Round 32 power gate for every register at L=120 and L=240**. The engine inputs are re-pointed at it in a copy
(`engine_inputs_copy/`), not in the live Round 27 tree. Two things the coordinator did not expect: (1) the first build-twice attempt FAILED because of a hash-seed-dependent Hebrew mapping in I1's code (fixed in the wrapper;
I1's own `panel12.npz` is therefore not run-to-run reproducible); (2) `fetch_sources.py --welsh` does NOT reproduce the Welsh file on disk, so the CY input is frozen in the lane. The C self-test itself was not run (no compiler here).

| item | value |
|---|---|
| panel-R36 `panel12.npz` sha256 | `a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c` |
| engine blob `panel_lm.f32` (12x24389 f32) sha256 | `e46d4bb73d16adeb02262361325b2a6ff578ae436b1374a7725a0a240f7e9928` |
| `testhalves12.npz` sha256 | `cdd55adac8c9731116d3e059afa183503b21f1a532706720f58e7c9873736494` |
| retired Round 19 gate (`panel_lm.f32`) | `14a23d3619fa02dfb6aa20efafdd0fc0ff633c83d8dc5f02ac4d5d035b996297` |

## Inputs (`inputs_r36.json`, 53 files; `make_inputs.py --check` = 53/53)
| register | input | how obtained | vs Round 32 record | vs Round 19 record |
|---|---|---|---|---|
| EN_MODERN, EN_HALFVOWEL, EN_NOVOWEL | `data/keys/self_reliance.txt` (b2f3dbd3, 56,483 B) | in repo | MATCH | match |
| EN_MODERN, EN_HALFVOWEL, EN_NOVOWEL | `data/keys/mabinogion.txt` (80dc6f0d, 617,362 B) | `fetch_sources.py --r19` (gutenberg `/files/5160/5160-0.txt`) | **DIFFERS** (R32 used the cache/epub substitute e177d7c2, 617,553 B) | match |
| EN_KJV | `data/kjv.txt` (0f1a83cb, 4,436,268 B) | `fetch_sources.py --r19` (gutenberg `/files/10/10-0.txt`) | **DIFFERS** (R32 substitute 0204adae, 4,455,950 B) | match |
| LP1_REAL | `SOLVED-PAGES.json` (855eed73) | in repo | MATCH | match |
| LATIN | `analysis/latin/latin_218.txt`, `latin_28233.txt` | in repo | MATCH | match |
| OE | `oe_beowulf.txt`, `data/keys/runepoem_oe.txt` | in repo | MATCH | match |
| DE | `de_faust.txt`, `de_2.txt` (round10b B6 corpora) | in repo | MATCH | match |
| CY | `data/keys/welsh/welsh_mabinogion.txt` (624ffc97, 761,030 B) | **SUBSTITUTE** (Round 32 modern-Welsh prose); frozen copy `inputs_frozen/`; `--welsh` re-fetch gives da02fef6 (761,024 B) | MATCH | **no** (R19: 4b3fd926, 524,561 B, lost) |
| GREEK | 27 Nestle 1904 `*-ap.xhtml` (2,152,582 B) | I1 `fetch_r36.py`; raw.githubusercontent.com/biblicalhumanities/Nestle1904 | new in R36 | new |
| HEBREW | 7 WLC OSIS `*.xml` Gen..Judg (9,105,877 B) | I1 `fetch_r36.py`; raw.githubusercontent.com/openscriptures/morphhb | new in R36 | new |
| NORSE | 8 heimskringla.no saga pages (1,661,762 B) | I1 `fetch_r36.py`; heimskringla.no/wiki/... | new in R36 | new |

Re-download on 2026-10-30 (`verify_fetch.json`): 44 of 45 network-obtained files identical to disk; the exception is the `--welsh` rebuild. Consequence: eight of the nine original registers rebuild to the Round 19 models
(their n=120 mu/sd equal the Round 19 values frozen in `vectors.json` to <= 5e-16); only CY differs (mu +0.0116, sd +4.3 %).

## Build twice (`build_twice.json`)
`build_r36.py build1` (PYTHONHASHSEED=1) and `build_r36.py build2` (PYTHONHASHSEED=2), fresh processes, 28 s each: `panel12.npz` and `testhalves12.npz` **byte-identical**; `out_build12.json` identical except `built`/`elapsed_s`.
First attempt (default hash randomisation) was NOT identical (HEBREW test half, LM, mu, sd, corr). Diagnosis: I1's `hebrew_to_ascii` iterates a `set` of combining marks, so the 15 of 384,147 clusters with two vowel marks come out in
process-dependent order. Fix: sorted marks, applied by source transform at import in `build_r36.py` (asserted), I1's file untouched. The numpy `.npz` writer already pins zip timestamps (1980-01-01), so no other source of difference was found.

## 12-register power gate (`gate_proof_r36.json`; 24 reps; bar = max(empirical, GPD) 1e-3 wrong-key quantile of 12-panel pmax; null 4000 / 2000 real-LP2 wrong-key decodes at L=120 / 240)
Bars: L=120 **4.394**, L=240 **4.717** (I1 carried panel, same protocol: 4.370 / 4.706). Required >= 0.90.

| register | L=120 | L=240 | Round 32 (120/240) | I1 carried (120/240) | median own-z (120/240) |
|---|---|---|---|---|---|
| EN_MODERN | 24/24 = 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 17.4 / 24.6 |
| EN_KJV | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 18.8 / 26.0 |
| LP1_REAL | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 18.2 / 29.4 |
| LATIN | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 18.0 / 25.5 |
| OE | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 13.5 / 19.8 |
| DE | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 20.2 / 29.0 |
| CY | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 15.4 / 22.0 |
| EN_HALFVOWEL | 1.000 | 1.000 | 1.00 / 1.00 | 1.000 / 1.000 | 13.1 / 19.1 |
| EN_NOVOWEL | **22/24 = 0.917** | 1.000 | 0.92 / 1.00 | 0.917 / 1.000 | 12.1 / 18.5 |
| GREEK | 1.000 | 1.000 | - | 1.000 / 1.000 | 19.7 / 28.5 |
| HEBREW | 1.000 | 1.000 | - | 1.000 / 1.000 | 17.8 / 26.8 |
| NORSE | 1.000 | 1.000 | - | 1.000 / 1.000 | 18.1 / 25.4 |

**All 24 cells >= 0.90: PASS.** Caveats: 24 replicates (24/24 has Wilson lower bound 0.86); EN_NOVOWEL L=120 has no spare margin (minimum planted pmax 3.1 sits below the bar, 2 misses; it is the Round 32 value); the planted texts are
same-register held-out text, not independent authors. The gate run hit one transient Windows `OSError [Errno 22]` on a checkpoint write after NORSE|240; it was re-run from the checkpoint (per-rep seeds are fixed, nothing recomputed differently).
Wrong-key pmax(12) at L=120: mean 1.785, sd 0.767 (n=4000).

## Engine config re-point (copy only; `engine_config_diff.txt`)
`NREG` 9 -> 12 in `grind27.c`; new `engine.dat` / `panel_lm.f32`; 64 V1 pmax and V2 re-scored under panel-R36 (28 of 64 V1 change, -0.66..+1.34; V2 stays 17.931158509762 because LP1_REAL is the argmax; by argmax the changed rows are
CY 8, GREEK 6, HEBREW 5, NORSE 5, LATIN 2, EN_KJV 1, LP1_REAL 1). The formula was validated against Round 19 numbers (seed 2149309687 -> 6.825835461843649, plant -> 17.93115850976196, bit-exact where the argmax is unchanged).
Finding: `grind27.c` never checks `PANEL_SHA256` against the file; `engine_inputs_copy/check_panel_gate.py` enforces it (PASS on the shipped copy, including the npz hash and npz-LM == blob). Live Round 27 files untouched.

## Conditionals (Doctrine Q4)
1. Key space: none swept. 2. Decoder transition model: Round 32 keyskip beam (400,3) with the correct key handed over; v3 / other relations unmeasured. 3. Adjudicator register: 12 registers as defined here; CY is a modern-Welsh
substitute; the engine screen is the pair/keyskip2 beam (L=120, beam 64) whose power at the engine's own beam is not re-measured. Not covered: cross-machine byte-exactness of the build; the C `--self-test` (S1); recalibration of claim bars for 12 registers (D1); 24 replicates only.

## Files
`PREREG.md`, `inputs_r36.json`, `build_r36.py`, `build1/`, `build2/` (npz gitignored via lane `.gitignore`), `build_twice.json`, `compare_builds.py`, `make_inputs.py`, `verify_fetch.py` + `verify_fetch.json`, `inputs_frozen/welsh_mabinogion.txt`,
`run_gate_r36.py` + `run_gate_r36.log` + `out_gate_r36.json`, `analyze_gate_r36.py`, `gate_proof_r36.json`, `GATE-CHANGE.md`, `engine_config_diff.txt` + `make_config_diff.py`,
`engine_inputs_copy/` (`grind27.c`, `engine.dat`, `panel_lm.f32`, `english_quadgrams.txt`, `sweep_plan.json`, `export_data_r36.py`, `check_panel_gate.py`, `rescore_r36.json`), `ledger.json`, `ledger_patches.json`.
`refetch/` (re-downloaded corpora, ~13 MB, gitignored) can be deleted.
