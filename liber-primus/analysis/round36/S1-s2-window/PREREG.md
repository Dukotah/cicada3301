# Round 36 / S1 - S2 window on the sandbox: PREREG
Dated 2026-10-30, written BEFORE any sandbox was created, any build or any self-test in this lane.

## Decisions applied (coordinator)
1. S2 continues from the existing change-point cursors (run/STATUS.json: 1,895,728,884 of 2^32 = 44.14 %) in a COPIED run dir `run_r36/`.
   Histogram and top-1024 list RESET and labelled "panel-R36 measurement" (old lists mix Round 19-scored values). Original `run/` untouched locally and on the sandbox.
2. Claim bars kept: 7.3835 (pair/S1), 7.6342 (exact/S2). Also report any candidate >= bar - 0.10 as a NEAR-MISS (12-register null shift).
3. Any claim-bar crosser = flagged-for-oracle, never certified; re-screened locally with beam_v3 at L=240 under panel-R36 after the window.

## Recognizer
Engine inputs = round36/P1-panel-r36/engine_inputs_copy (panel_lm.f32 sha e46d4bb7.., engine.dat PANEL_SHA256 e46d4bb7.. / panel12.npz a0682f0c..).
PASS = `check_panel_gate.py` passes on the sandbox copy; build with Round 34 flags (-O2 -Wall -Wextra -std=gnu17 -fopenmp -ffp-contract=off) 0 errors;
`--self-test` gives V1 64/64 exact AND V2 = 17.931158509762 to 4 dp on panel-R36; resume tests (a),(a2),(b),(c) on a COPY pass.
## Kill
Self-test fails (any V1 < 64/64 or V2 off at 4 dp) -> STOP. Record both hashes (panel_lm.f32, panel12.npz) and the V1/V2 numbers. S2 stays parked; no window is run.
No sandbox -> write BUILD.md with exact commands and stop (valid outcome).
## Budget / rules
Window <= 60 min sandbox wall, build+tests <= 25 min; wall times logged. No git. No edits to analysis/round27/P1-engine/run/. Gate-passing crossers are flagged only.
The window is a NEW measurement under panel-R36 (GATE-CHANGE.md sec. 5): pmax not comparable with the Round 19-gated rows.
