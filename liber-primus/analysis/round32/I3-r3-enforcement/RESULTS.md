# R32 / I3 RESULTS -- R3 enforcement and length-aware null bar

## 1. What is now enforced (`analysis/handoff/validate_ledger.py`, check 7)
For a ledger row with `round >= 19` that sets `sweep_store` (str|list of paths) or `declares_sweep: true`:
- `declares_sweep` without `sweep_store`, a nonexistent store, a store whose line 1 is not a `SWEEPROW/*`
  header, a header lacking any of `ioc` (decrypt IoC*N), `mds` (min distinct / 32-rune window), `pmax_ne`
  (best non-English LM score), `zl` (compressibility), or any row failing `adjudicate.validate_store`
  (-> `validate_row`, which also demands the 9-register z-vector) is an ERROR tagged `R3`, and **fails the
  run in both default and --strict modes**.
- Implicit detection: a round >= 19 row whose `evidence` lists a `*sweep*.jsonl` is checked but only WARNs
  (`R3-UNVERIFIED`), because pre-schema stores cannot be repaired (the decodes are gone).
- CI already runs `python analysis/handoff/validate_ledger.py` (`.github/workflows/ci.yml`, job `validate`),
  so the hook executes there. The new pytest file is not auto-collected by CI (CI runs `tests/test_rig.py`
  and `benchmark/`); see the coordinator decision in the hand-back.

**Scoping decision (Q5):** round >= 19 and sweep-declaring only; no historical row is retro-broken. No existing
ledger row carries `sweep_store`, so the hard check bites only on new rows.

## 2. Before / after validator on the live ledger
Before: 0 ERRORS, 18 WARNINGS, `Unsound negatives: 0`, rc=0.
After : 0 ERRORS, 22 WARNINGS, `Unsound negatives: 0`, rc=0. The 4 new WARNs (advisory; nothing loosened):
R21-L3-PY27-REDUCERS and R20-SG3-PY27-RANDOM29 (header lacks ioc/mds/pmax_ne/zl), R24-C2-SKIP-BY-TWO-DECODER
(line 1 is not a JSON header object), R28-L1-CICADAOS-PADS-DENSE-PAIR (line 1 not a SWEEPROW header). These are
real R3 gaps in post-R19 sweeps, surfaced but not failed. The one compliant store
(`round19/finite/sweeprows.jsonl`) passes `check_r3_store`.

## 3. Tests
- `python -m pytest analysis/handoff/test_validate_ledger_r3.py benchmark -q` -> **13 passed**. Covers:
  compliant store passes; dropping each of ioc/mds/pmax_ne/zl fails; English-only store fails; scoping (round 18
  untouched, round-32 bad store fails, declared-without-store fails, missing file fails). Synthetic rows are used
  because `round19/I2/models/panel.npz` is gitignored and absent on a fresh checkout (a first draft that built
  rows with the real panel failed with FileNotFoundError, which is why).
- `python -m doctest benchmark/null.py` -> ok (includes the new doctests).

## 4. `threshold_for(n, segment_len=L)`
`benchmark/null.py`: new `curve_params(L)`; `segment_len` is now honoured: beta(L) = 0.07095*(L/120)^-0.5675,
mu(L) linearly interpolated in ln L between measured nodes (flat outside L=31..180). `segment_len=None`, or
explicit mu/beta, is bit-identical to before. Caution: historical callers that already passed `segment_len`
(round18 L6 scripts) would get a different bar if re-run; their stored outputs are unchanged.

## 5. Null-curve fit (`null_curve32.json`, `cells32.json`, `curve32.py`, `fit32.py`)
Seed-3301 histogram-preserving shuffle of real LP2, exact vectorised keyskip1 beam (w400, max_skip 3),
M = 200,000 decodes per cell, round19 `fit_cell` Gumbel block-maxima (anchor block 1000).

| L | mu | beta |
|--:|--:|--:|
| 31 | -6.899 | 0.1438 |
| 60 | -7.062 | 0.1087 |
| 90 | -7.122 | 0.0914 |
| 120 | -7.118 | 0.0728 |
| 180 | -7.099 | 0.0517 |

OLS ln beta ~ ln L, 5 points (3 DOF): **exponent -0.5675, SE 0.0623** (round19's -0.583 is 0.25 SE away).
Pooled with the three round19 uniform bw400 cells (8 points): -0.579, SE 0.032. Two-point extremes: -0.582.
Out-of-sample: round19 L=240 beta 0.0451 vs curve 0.0479. beta(120) differs from the legacy 0.0725 by < 3%.
Not done: L=240/320/400 in this lane (the L=240 cell had not finished after > 30 min on the RAM-starved laptop
and was killed). mu for L > 180 is a flat extrapolation and the L=400 bar rests on the exponent alone.

## 6. Bars (alpha = 0.01, floor -5.5)
| N | legacy (L ignored) | L=31 | L=120 | L=240 | L=400 |
|--:|--:|--:|--:|--:|--:|
| 1e4 | -5.500 | -4.787 | -5.500 | -5.500 | -5.500 |
| 1e6 | -5.500 | -4.083 | -5.500 | -5.500 | -5.500 |
| 1e9 | -5.416 | -3.026 | -5.321 | -5.500 | -5.500 |
| 1e11 | -5.082 | -2.322 | -4.994 | -5.500 | -5.500 |

Reading: at L=31 the legacy -5.5 bar is far too loose (consistent with round19 G-HONEST); at L >= 240 the
floor binds out to ~1e13 trials.

## 7. Not covered
Only the legacy EN quadgram statistic; per-register and panel-max cells remain in `round19/I3/nullcurve19.py`.
`ARMADA-DOCTRINE.md` not edited (enforcement location unchanged: `validate_ledger.py`).
