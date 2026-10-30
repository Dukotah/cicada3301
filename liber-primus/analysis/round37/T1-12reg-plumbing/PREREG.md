# Round 37 T1 -- 12-register plumbing: PREREG
Written 2026-10-30 13:01:52 (local), BEFORE results RESULTS.md / ledger.json / tests output exist. (Code patches were drafted in the same session; the pass/fail criteria below are fixed before any test is run.)

Scope: tooling only; no discovery claim. Touch only: beam_v3.py, both adjudicate.py copies, validate_ledger.check_r3_store (via validate_store), hitfn20.py, panelmax20.py, tests/test_12reg_plumbing.py, ci.yml, LEDGER.json row R36-B1-ORBIT-12REG.

Pass criteria (fixed now):
1. Stock adjudicate.validate_store and validate_ledger.check_r3_store validate round36 readjud_rows.jsonl (12-wide) with no workaround; round35 sweep_rows.jsonl (9-wide) still validates; a header lacking "registers" falls back to 9.
2. beam_v3 loads panel-R36 via BEAM_V3_PANEL / set_panel, derives clusters from its registers (EN family grouped, others singleton; 9-reg panel reproduces the old 7), and decodes one planted key (L=120) under panel_max and register_cond.
3. hitfn20 / panelmax20 with panel=panel-R36 raise ValueError; old-signature calls unchanged.
4. validate_ledger.py: 0 errors after declaring sweep_store on R36-B1-ORBIT-12REG; tests/validate.py and pytest tests/ benchmark/ stay green.
Failing-then-passing: the new tests are the positive control; the 12-wide store fails stock validation pre-patch (recorded by R36 B1 readjud_summary.json).
