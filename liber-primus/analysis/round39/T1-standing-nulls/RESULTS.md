# Round 39 / T1 - Standing nulls and flags: RESULTS
Dated 2026-10-31 (PREREG.md first). Tooling lane, measurement only. No claim about the cipher.

## Files changed (liber-primus/)
- `analysis/round19/I2/adjudicate.py` and `analysis/round32/I2-multiregister-readjudication/adjudicate.py` (byte-identical, asserted by a test): `DEG_MDS=6`, `DEG_IOC_N=4.24`, `is_degenerate(mds, ioc)`; `adjudicate()` result gains `degenerate`; `ROW_FIELDS_DEG` (= ROW_FIELDS + `degenerate`); `to_row(..., with_degenerate=False)` and `header(..., with_degenerate=False)` opt in to the 14th field; `validate_row` accepts 13 or 14 fields, enforces the header's `fields` list (13 or 14) against the row length, and checks the flag agrees with (mds, ioc); new `pmax_nondegenerate(rows)`.
- `analysis/round19/I2/SWEEPROW.md`: field 13 `degenerate` documented as optional.
- `benchmark/bars_keymatched.py` (new): `bar_keymatched(derive_key_fn, decode_fn, L, N, draws, seed=3301, stream=...)`, plus pure parts `bar_from_maxima`, `family_maxima_from_rows`, `dfshuffle`, `draw_family_max`.
- `analysis/round34/I1-v3-null/bars_v3.py`: `free` at L=120 -> 12-register node (fit_free.json); `panel="r32"` = old R34 node; doctests added (7 pass). `RESULTS.md` there: dated addendum.
- `tests/test_standing_nulls.py` (new, 7 tests); `../.github/workflows/ci.yml`: added to the pytest step.

## Numbers
- Key-matched fixture: stored L=120 X4 null (2000 shuffles, 60 non-degenerate rows/rel) -> empirical q99 of family max = **6.99419 (6.994)** for both keyskip1 and keyskip2; matches `null_x4.json` bar_empirical_q99; Gumbel-moments q99 reproduces 7.212 within 0.01.
- `bar_v3(1e6, 120, "free")`: 17.43 (R34, 9-reg) -> **15.30** (12-reg); N=1e5: 15.89 -> 14.08. `panel="r32"` returns 17.43.

## Test output
- `python -m pytest tests/ benchmark/ -q`: 41 passed. `python tests/validate.py`: ALL VALIDATIONS PASSED. `validate_ledger.py`: ERRORS 0, unsound negatives 0. `bars_v3.py` doctests: 7/7. All existing stores validate (13-field default).
- Failing-then-passing: the new tests could not pass on the pre-patch code by construction (no `is_degenerate`/`ROW_FIELDS_DEG`/`bars_keymatched`; the free-L=120 test asserts 15.30, old code gave 17.43). I did not run the old code (no git).

## Not done / limits
- `bar_keymatched` full decode path is exercised only by a toy family (stub adjudicator) in CI; not run end-to-end against beam_v3 (would cost minutes of laptop; the stored-rows fixture covers the statistic).
- `to_row` does NOT emit the field by default (would break 13-field readers and the binary dtype); lanes opt in.

## Coordinator decisions
1. Make `with_degenerate=True` the default for new sweeps from Round 39 (SWEEPROW/2 bump)? Currently opt-in.
2. The `free` L=120 default bar drops by ~2.1 at N=1e6; any earlier verdict used the higher bar (conservative). Accept.
3. ci.yml sits at the repo-root `.github/` (outside liber-primus/).
