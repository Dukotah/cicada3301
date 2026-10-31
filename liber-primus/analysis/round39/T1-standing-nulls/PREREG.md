# Round 39 / T1 - Standing nulls and flags: PREREG
Dated 2026-10-31, written before any code change. Tooling lane; no discovery claim.

Q1 (recognizer): `tests/test_standing_nulls.py` passes, and fails on the pre-patch code (no `is_degenerate`, no `bars_keymatched`, L=120 `free` returning the R34 nine-register node). The key-matched module reproduces I2-R38's L=120 X4 bar 6.994 (ks1 and ks2) from the stored `null_rows_L120.jsonl` with no re-decoding.
Q2 (prior): R38 I2 showed constant decodes (mds=1, IoC*N=29) score pmax 6.9-12.4 content-independently; transferred bars undercut the key-matched bar by ~1.3.
Q3 (bounded): touch only adjudicate.py (both copies, byte-identical), SWEEPROW.md, benchmark/bars_keymatched.py, bars_v3.py, round34 RESULTS.md addendum, tests/test_standing_nulls.py, ci.yml. No re-decoding; no existing store rewritten.
Design: `degenerate` is OPTIONAL SWEEPROW field 14, header-driven (`fields` list); default writers unchanged (13 fields) so every existing store and test stays valid. `adjudicate()` always returns the flag in its dict. `pmax_nondegenerate` recomputes the flag from (mds, ioc). `free` at L=120 -> fit_free.json node; `panel="r32"` is the escape.
Pass: validate.py, pytest tests/ benchmark/, validate_ledger.py (0 errors) green.
