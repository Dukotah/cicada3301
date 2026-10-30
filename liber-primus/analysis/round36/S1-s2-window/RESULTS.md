# Round 36 / S1 - S2 window on the sandbox: RESULTS
Date 2026-10-30. Status: measured (negative: no claim-bar crosser, no near-miss). A NEW panel-R36 measurement, not a continuation of the Round 19-gated rows (GATE-CHANGE.md sec. 5).

## Gate and self-test
* check_panel_gate.py: PASS x5 on the laptop and again on the sandbox copy (panel_lm.f32 e46d4bb7.., NREG 12, engine.dat PANEL_SHA256 matches, != Round 19 14a23d36..). The npz check (a0682f0c..) was not run on the sandbox (npz not uploaded).
* Build (gcc 15.2.0, Ubuntu 26.04.1, Round 34 flags): rc 0, 0 errors, 2 warnings. Binary sha 7be592b0...
* `--self-test`: **V1 64/64 exact** (worst |dpmax| 0, |dbeam| 0); **V2 seed 777 pmax 17.931158509762** (|d| 0). PASS. selftest.json.

## Resume tests (copy of run/, engine_tests.json)
(a) restore PASS; (a2) rewound re-scan dedupe PASS (both sub-cases; seed 35563892 re-scores to 7.670723299260088 under panel-R36, identical to the Round 19 value); (b) planted hit PASS; (c) bounded run PASS.

## Window
| | before | after |
|---|---|---|
| seeds done (of 2^32) | 1,895,728,884 | 1,950,696,430 |
| coverage fraction | 0.441384 | **0.454182** |

Advanced **54,967,546 seeds (+1.28 pp)** in 2100 s with 6 threads on 2 vCPU = **26,174 seeds/s** (the original laptop run did ~77k/s). Remaining 2,344,270,866 seeds = ~42.6 more windows of this size at this rate. Session wall 38.3 min total (window 35.0 min, setup+tests ~3 min); the 60 min window cap was not used in full (45-min session cap; a second session leg was not run).
* Candidates >= 5.0: 6,280. Histogram >=5.5: 790; >=6.0: 79; >=6.5: 4; >=7.0: 1; >=7.3: 0; >=7.5342 (near-miss bar): 0. Best pmax 7.1256 at seed 325254043 (worker 0).
* **Claim-bar crossers (>= 7.6342): 0. Near-misses (>= 7.5342): 0.** Nothing to re-screen with beam_v3 (not run).
* Labelled panel-R36 measurement: histogram/top-1024/best/candidate counters were reset at window start; the Round 19-gated hit 35563892 @7.6707 stays in state_before/ and was not re-found (outside the new range).

## State
state_after/ holds STATUS.json (byte-exact, sha a8f61e89..) and HIT-CANDIDATE.json. top_S2.json, hist_S2.u64 and candidates.jsonl exist only in the sandbox snapshot `snap_fWma12lA4k5RXsR6LHPwhV2p0DnN` (sandbox emerald-coming-prawn-hDdhox, expires ~2026-11-06; resume via update_sandbox resume=true). The cursors in STATUS.json suffice to resume; the lists are not recoverable locally. Original run/ untouched locally and on the sandbox (state_before/ copy).

## Caveats
* S2 requires GRIND27_S2_CONTROL_OK=1: the lane's own planted exact-relation control (PREREG S2 gate) is still not independently validated; V2 validates only the screen. Hits remain flagged-for-oracle only.
* Claim bars not recalibrated for 12 registers; pmax not comparable to Round 19 rows.
* Throughput ~3x lower than the laptop; 2 vCPU only (8-vCPU create request returned 400).
* Inputs went through a temporary secret gist (tgz sha 07b87249..), since deleted. No git run; round27 run/ untouched.
