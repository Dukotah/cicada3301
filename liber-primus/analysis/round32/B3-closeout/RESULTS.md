# R32 / B3 RESULTS — closeout: R28-L3 write-up + glibc gen=0 prior-dense first-fire

_2026-10-28. Pre-registered in `PREREG.md` before the sweep ran. No git, no edit to top-level `LEDGER.json`._

| part | verdict | headline |
|---|---|---|
| R28-L3 write-up | **`inconclusive`** | sweep complete on `progress28.json` (11 items, 2,500,207 decodes, best pmax 6.3148 vs bars 7.38/7.63, no survivors); control recovery IS stored (5/5 pass); but `candidates28.jsonl` (226 stage-B rows) and `dictionary.jsonl` are not on this checkout and no SWEEPROW bulk store exists, so the kill rule applies. Upgrade to bounded negative once those two files are recovered. Details: `analysis/round28/L3/RESULTS.md`. |
| glibc `gen=0` prior-dense first-fire | **negative (bounded, prior-dense list only)** | 48,036 seeds x {pair, exact} = 96,072 decodes, best pmax 5.74 vs bars 7.3835 / 7.6342, 0 gate-3 crossers, 0 flagged. Control 6/6. |

## 1. R28-L3
See `analysis/round28/L3/RESULTS.md`. Verdict `inconclusive`; missing exactly: `candidates28.jsonl`,
`dictionary.jsonl` (and its pinned 390,306-word list), SWEEPROW bulk store (never written). Present and
consistent: progress for all 11 items, `controls.json` (5/5, recovery 0.9917–1.000), `control_e2e.json`
(random29xexact 0.9, grb5_modxpair 0.8 end-to-end, 50/50 screen), `hash_gate.json` 1,500/1,500,
`subsumption.json` 200/200. Coverage ~1.4e-13 of the 2^64 amd64 image.

## 2. glibc gen=0 first-fire (`sweep.py`, `sweep_rows.jsonl`, `sweep_summary.json`, `control.json`)

**Generator.** `round19/G1/gen_glibc.random_seq` (TYPE_3, deg 31 sep 3) mod 29 = `seed_sweep/sweep.c` gen=0.
Port checked in `control` against the known `srandom(1)` outputs 1804289383, 846930886, 1681692777 (and
G1's own byte-exact validation against system glibc, cited not rerun).

**Positive control (run before the sweep file was opened; `control.json`).** Planted English
(`self_reliance.txt` 5000..5240) enciphered with glibc `random()%29` keystreams for seeds 1325734783
(PGP creation second), 3301, 20120105; `pair` plants under the skip_by_two model (supp 0.83), `exact` plants
under `encipher_keyskip`. 6/6: screen pmax 17.931 (bar 5.0), stage-B pmax 25.241 vs bars 7.3835 (pair) /
7.6342 (exact), recovery 1.000, held-out 1.000, HIT=True. Caveat: all six plants share one plaintext, so this
is one plant text x 3 keys x 2 relations, and the control runs the plant through the same decode functions, not
injected into the real-ciphertext stream.

**Seed list (48,036 distinct 32-bit seeds).** B04 NUM_INTS / primes / numeric strings, the 3301 family,
the 433 `seedprior20.json` PGP-time seconds, ints 0..2047, YYYYMMDD and unix-midnight-UTC for every day
2011-01-01..2015-12-31, and unix top-of-hour UTC for 2011..2015 (43,824). `LP2 0-54` screen L=120, gate L=240.

**Result.** 96,072 decodes (all seeds x both presets, `complete: true`, 846.9 s). Best pmax: pair 5.74 (seed
1319400000 = 2011-10-23T20:00Z, a top-of-hour seed), exact 5.393 (seed
1435017600 = 2015-06-23T00:00Z midnight). 11 decodes reached the 5.0 screen and went to stage B; none reached
the claim bar, none was flagged. Histograms (pmax, 0.1 bins) in `sweep_summary.json`; max-bin tail pair 5.7 x1,
5.3 x3, 5.2 x1, 5.0 x2; exact 5.3 x1, 5.2 x2, 5.1 x1.

**SWEEPROW.** `sweep_rows.jsonl`: header + 96,072 SWEEPROW/1 rows, `adjudicate.validate_store` PASS. The R3
language-agnostic stats (ioc, mds, h2, zl) are persisted for every decode.
Header caveat: `adjudicate.header()` copies `panel_build`/`corpora_sha256` from `round19/I2/out_build.json`;
those were overwritten in line 1 from this lane's `out_build.json` (see `_header_correction`).

**Coverage x power.**
- Coverage: 48,036 of 2^32 seeds = **1.12e-5** of the glibc gen=0 seed space (offset 0, `random()%29`, no
  initstate variants), both relations. By prior mass it targets the repo's densest seeds; prior-mass share not
  measured.
- Power: control recovery 1.000 on 6 plants / 1 plant text (Wilson 95% lower bound ~0.61 on n=6); the L3 lane's
  measured envelope for the same decoder/gate is 50/50 screen, 0.8–1.0 end-to-end on 10 plants per cell
  (clause-3 false-negative channel).
- Not covered: the other 99.9989% of the 32-bit space (full gen=0 remains OPEN; needs the C prefilter or ~166
  core-days via this Python path), offsets != 0, initstate sizes other than TYPE_3, `rand()` variants, reject /
  scaled reductions, jitter windows around timestamps, seconds other than the listed ones, `sign=+1`
  (only sign -1 run), other relations.

**Three conditionals.** (1) listed seeds, offset 0, `random()%29` TYPE_3. (2) keyskip1 + keyskip2, beam_w 64,
L=120 screen. (3) I2 nine-register panel, **but rebuilt in this lane**: `round19/I2/models/` is gitignored and
absent on this checkout; the rebuild's corpora hashes differ from I2's committed build (mabinogion, kjv, welsh
are different downloads; CY runes 380,028 vs 297,149), `out_build.json` here vs `round19/I2/out_build.json`.
The pmax scale and null are therefore a sibling of, not identical to, the panel behind the 7.38/7.63 bars; the
frozen bars are applied as constants. The control (pmax 17.9 / 25.2 vs 5 / 7.6) leaves a wide margin, the
sweep's best (5.74) sits 1.6 below the lower bar, so a modest panel difference does not flip the verdict.
The same caveat applies to nothing in R28-L3, which used the original panel.

## 3. What this does and does not do to R19-G3-CORRECTION
It adds a skip-aware, panel-adjudicated, language-agnostic-logged negative for a ~1e-5 prior-dense slice of
gen=0. The row stays **open** for the full 2^32 (gen=0 still has no DONE line and no full coverage). Nothing here
re-adjudicates gens 1–9 or gen=7/8 (that remains a separate item).

## 4. Files written
`analysis/round32/B3-closeout/`: PREREG.md, RESULTS.md, ledger.json, ledger_patches.json, sweep.py, build_panel.py,
control.json, sweep_rows.jsonl (15 MB), sweep_summary.json, sweep.log, out_build.json, models/ (panel.npz,
testhalves.npz, rebuildable, gitignore candidates), __pycache__. `analysis/round28/L3/RESULTS.md`.
