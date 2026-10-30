# Round 37 T1 -- 12-register plumbing: RESULTS
Tooling lane; no discovery claim. PREREG.md written first; pass criteria met as fixed there.

## Files changed (paths relative to liber-primus/)
- analysis/round33/I1-register-aware-beam/beam_v3.py: `PANEL_PATH` now env `BEAM_V3_PANEL` override (default unchanged, `DEFAULT_PANEL_PATH`); new `derive_clusters(registers)` (EN_MODERN/EN_KJV/LP1_REAL -> "EN", every other/unknown register its own cluster; 9-reg panel reproduces the old 7); `CLUSTERS` derived from the panel at import (empty if the gitignored default panel is absent); new `set_panel(path)` re-derives clusters and clears caches. `panel_max`/`register_cond` already index by `pan.registers`, so both run on 9 and 12.
- analysis/round19/I2/adjudicate.py and analysis/round32/I2-multiregister-readjudication/adjudicate.py (byte-identical before and after): `ROW_DTYPE` replaced by `row_dtype(n)` (+ `ROW_DTYPE = row_dtype(9)` kept); `to_record` sizes z from the result; `validate_row(n_registers=None)` takes the count from the header `registers` list (`_hdr_registers`, fallback 9 only if absent; an explicit int still wins); `validate_store` inherits via its header; `Panel` records `self.path`.
- analysis/handoff/validate_ledger.py: NOT edited -- `check_r3_store` calls `A.validate_store(path)`, which is now header-driven (verified by test).
- analysis/round20/P3/panelmax20.py: `FITTED_N_REGISTERS=9`, `FITTED_PANEL_SHA256` prefix `36a01dcb5083`, `check_panel_matches_bar(panel)`; `panelmax_bar`/`panelmax_contract` take `panel=None` and raise `ValueError("REFUSED ...")` on a different register count or file sha. Old signature unchanged.
- analysis/round20/HITFN/hitfn20.py: `HitDecode` gains `panel=`, `decoder=` (default None = legacy), `beam()` and `resolved_panel()`; `evaluate` refuses mismatched panel before any work, adjudicates with the supplied panel, passes `panel=` to the bar.
- tests/test_12reg_plumbing.py (new, 8 tests); ../.github/workflows/ci.yml: new test appended to the pytest step.
- LEDGER.json: row R36-B1-ORBIT-12REG: `sweep_store_note` removed, `"sweep_store": "analysis/round36/B1-orbit-12reg/readjud_rows.jsonl"` added.

## Before / after on the R36 B1 store (276,242 rows, 12 registers)
- Before (R36 B1 readjud_summary.json): `AD.validate_store` FAIL "z must be a 9-vector ... got [12 values]"; `check_r3_store` -> ['validate_store: RowError: z must be a 9-vector ...']; only the local `validate12` workaround passed.
- After: `A.validate_store(S12)` -> rows_validated 276242; `check_r3_store(S12) == []`. R35 9-wide store: still validates (50-row prefix in test).

## Caveat on the hitfn20/panelmax20 sha
The Round 19 panel file is lost. `FITTED_PANEL_SHA256` pins the Round 32 I2 rebuild (the only 9-register panel in the repo); any other 9-register panel is also refused. The coordinator may prefer count-only gating.

## Test output
- `python -m pytest tests/test_12reg_plumbing.py -q`: 8 passed.
- `python -m pytest tests/ benchmark/ -q`: 34 passed.
- `python tests/validate.py`: ALL VALIDATIONS PASSED.
- `python analysis/handoff/validate_ledger.py`: ERRORS: 0, unsound negatives 0 (check 7 now reads the 12-wide store).
- Positive control (failing-then-passing): the 12-wide store failing stock validation before the patch is the R36 B1 record above; the beam_v3 plant (L=120, one plant, panel-R36, skip-free keyskip1) recovers >=0.9 under panel_max and register_cond; hitfn20 plus panelmax20 refuse panel-R36.
