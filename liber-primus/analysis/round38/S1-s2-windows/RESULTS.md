# Round 38 / S1 - S2 windows: RESULTS
Date 2026-10-30/31. Status: measured. Control (a) PASS; re-score (b) done; export (c) partial (coordinator accepted); windows (d): **window 1 complete; window 2 ran but its end state could NOT be recovered** (see below). No claim-bar crosser and no near-miss in window 1. Nothing here is "solved/closed/exhausted"; S2 is partially swept.

## (a) Independent exact-relation control: PASS 3/3 (control_exact.json, gen_control.py)
Own generator (Python-3 stdlib MT, random29 reducer, keyskip1 one-draw rejection enciphering, written in this lane; keystream verified equal to the engine's own ks128 for all 3 seeds), 240-rune known plaintext, ciphertext swapped into the engine's own exact-lane `run_lane` path (control-only variant: stock source + 2 lines, loads the replacement C_SCREEN AFTER the unmodified launch self-test). 4096-seed band around each seed.

| seed | rank | pmax | over claim bar 7.6342 | 2nd best |
|---|---|---|---|---|
| 777 | 1 | 17.9312 | +10.30 | 5.156 |
| 1234567891 | 1 | 19.8145 | +12.18 | 4.735 |
| 3000000017 | 1 | 20.7957 | +13.16 | 4.553 |

Caveats: 777 reuses the R27 plaintext slice (pmax equal to R27 by construction); the full hitfn20 3-clause gate was not re-run; `GRIND27_S2_CONTROL_OK=1` is only a lane guard and is not the evidence. The exact-relation lane is therefore validated independently of the flag.

## Gate and self-test
check_panel_gate.py PASS (panel-R36, e46d4bb7..); binary rebuilt bit-identical (sha 7be592b0..); `--self-test` V1 64/64 exact (worst |dpmax| 0), V2 seed 777 pmax 17.931158509762 exact; re-checked at the start of window 2.

## (b) Top list re-scored under panel-R36 (top_rescored.json)
Round 19 top_S2.json (1024) re-scored with the engine's score path under the exact relation (1-line variant): 949 unchanged, 75 moved >0.01 (72 down, 3 up; max up +0.88, max down -3.69). Only crosser: 35563892 at 7.6707 (identical under both panels). No other entry >= 7.5342. Largest riser 2286867315: 6.580 -> 7.462 (below the near-miss bar). Scope limit: only the Round 19 top-1024 is re-scored.

## L=240 diagnostics (beam_v3, panel-R36, keyskip1 max_skip 3; beam 64 and 400 identical; rescreen_l240.json; RAM check 0.38 GB free) - near-miss diagnostics, NOT flags
| seed | z_max at L=240 | register | skips |
|---|---|---|---|
| 35563892 (calibration, the known R19 hit) | 7.511 | LP1_REAL | 3 |
| 2286867315 | 6.765 | OE | 10 |

2286867315 does not hold up at 240 runes. (L=240 z is not directly comparable to the L=120 stage-A claim bar.)

## (c) Export status: PARTIAL by necessity (accepted by coordinator)
The tool channel returns ~2 KB per call, so the full lists (candidates 394 KB -> 1.17 MB after window 1, hist 125 KB, top 52 KB) were not transferred. Exported (exported/R36_snapshot_summary.json, state_after_1/STATUS_summary.json): sha256 prefixes, aggregated histogram, candidates >= 6.0 (76 of 79 for the R36 state) and >= 6.5 (25) after window 1. Full lists live in snapshots: snap_fWma12lA4k5RXsR6LHPwhV2p0DnN (R36 state, expires ~2026-11-06), snap_3uGXrds5nwHCGnLkgc2L1AjoScoo (after window 1, ~2026-11-06), snap_ff0SWU76EW32OqbWJvp00fnORypR (end of session 2, expires ~2026-11-07). Sandbox retention was raised to 5 snapshots, deleteEvicted=false.

## (d) Windows (panel-R36 is a new instrument; Round 19-panel fraction stays 44.138 %, not re-run)
| | window 1 | window 2 |
|---|---|---|
| sandbox | indigo-negative-rhinoceros-y1foyJ, 4 vCPU/8 GB, 6 threads | silver-stupid-pigeon-GszBty, same |
| start (unix) / --seconds | 1793398889 / 1950 | 1793400927 / 2250 |
| seeds before | 1,950,696,430 | 2,059,308,008 |
| seeds after | 2,059,308,008 | not recovered |
| seeds advanced | 108,611,578 | not recovered |
| fraction of 2^32 (cursors) | 0.454182 -> 0.479470 (+2.529 pp) | 0.479470 -> unknown |
| rate | 55,698 seeds/s | unknown (session active CPU 9.01e6 ms) |
| candidates >=5.0 / 5.5 / 6.0 / 6.5 / 7.0 (delta) | 12,361 / 1,510 / 169 / 21 / 3 | unknown |
| >=7.3 | 1 (seed 3905907872, 7.300666) | unknown |
| crossers >=7.6342 | 0 | unknown (HIT-CANDIDATE not read) |
| near-misses >=7.5342 | 0 | unknown |
| best pmax | 7.3007 @ 3905907872; then 7.2853 @ 1774592253, 7.1579 @ 2473038093 | unknown |

Cumulative panel-R36 coverage through window 1: 54,967,546 (R36) + 108,611,578 (R38 w1) = 163,579,124 seeds = 3.809 pp of 2^32; cumulative candidates >=5.0 18,641, >=6.0 248, >=7.0 4, histogram >=7.5342 = 0.

**Window 2 recovery failure.** The monitor timer was lost (laptop slept); the 45-min session hit its cap (stopped unix 1793403622) and was auto-snapshotted (snap_ff0S..). Re-creating a sandbox from it returned HTTP 402 (Hobby plan limit, resets 2026-11-01 00:00 UTC), and the stopped session's files return 410. The window's `--seconds 2250` would have ended the run at ~unix 1793403180 with a STATUS write, so the end state very probably sits in snap_ff0S.. but is UNVERIFIED. To recover: after the quota resets, create a sandbox from snap_ff0S.., read run_r36/STATUS.json, HIT-CANDIDATE.json, and the lists. Until then the last confirmed resume point is window 1's cursors (state_after_1/STATUS_summary.json). state_after_2/ is empty.

## Sandbox resources
Session 1: 2200 s wall, 7.82e6 ms active CPU, 4 vCPU. Session 2: 2704 s wall, 9.01e6 ms active CPU. Vercel Hobby quota exhausted until 2026-11-01 00:00 UTC. Remaining S2 space after window 1: 2,235,659,288 seeds (52.05 %), ~11.1 h at 55.7k/s (minus whatever window 2 did). Sandboxes silver-stupid-pigeon-GszBty (persistent, stopped) and indigo-negative-rhinoceros-y1foyJ remain; the three snapshots expire ~2026-11-06/07. The final sandbox was NOT stopped non-persistent as requested because it could not be re-created (it is already stopped by the session cap); deletion of sandboxes/snapshots is left to the coordinator.

## Caveats
Claim bars 7.3835/7.6342 not recalibrated for 12 registers; pmax not comparable to Round 19 rows. Hits would be flagged-for-oracle only. No git run; round27 run/ untouched.
