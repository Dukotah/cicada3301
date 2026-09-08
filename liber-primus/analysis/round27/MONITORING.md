# Round 27 — sweep monitoring (S1 + S2, full 2^32 each)

**Launched:** 2026-09-07, detached via `setsid nice -n 10`, PID recorded in
`analysis/round27/sweep.pid` (first launch: 462796). The process is its own session
leader — it survives every SSH/agent session. `--self-test` (K3) runs automatically at
every launch and must print PASS; a failing self-test halts everything (broken scan,
not a null).

## Status

```bash
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/P1-engine && ./grind27 --status --run-dir run
```

Also useful:

```bash
ps -o pid,ni,pcpu,etime,nlwp,cmd -p "$(cat /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/sweep.pid)"
tail -5 /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/sweep.log
wc -l /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/P1-engine/run/candidates.jsonl
```

`run/STATUS.json` is the atomic ~30 s checkpoint (progress_w-compatible fields; reflects
the CURRENT lane only — completed lanes live in `lanes_completed` + per-lane
`hist_<lane>.u64` / `top_<lane>.json`).

## Resume (after crash, reboot, or manual stop)

Resume is proven exact (no gap, no double-count; completed lanes are skipped):

```bash
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/P1-engine && \
setsid nice -n 10 nohup ./grind27 --plan ../sweep_plan.json --run-dir run \
  >> /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/sweep.log 2>&1 & \
sleep 2; pgrep -x grind27 | tee /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/sweep.pid
```

To stop cleanly: `kill "$(cat .../sweep.pid)"` — SIGTERM/SIGINT checkpoint cleanly.
**Kill BY PID, never `pkill -f`** (repo gotcha: pattern-kill misses spawned workers).

## If HIT-CANDIDATE.json appears

`run/HIT-CANDIDATE.json` means a seed's stage-A pmax cleared the CLAIM bar
(S1: 7.383520294328688; S2: 7.6341931878728095). The engine keeps sweeping — this file
is a flag, not a verdict. Doctrine (R21-L1): the survivor is **FLAGGED-FOR-ORACLE,
never auto-certified** — the no-oracle seal is provably leaky. Adjudicate in Python:

1. Re-score the seed with the R25 pipeline (`analysis/round25/compute-tail/runner.py`
   stage_a/stage_b — exact parity with C was verified to 0 relative difference on 95 flags).
2. Run the 3-clause hit function `analysis/round20/HITFN/hitfn20.py`
   (panel-max-null-clear AND rune-recovery >= 0.90 AND held-out reproduction >= 0.90),
   with `analysis/round19/I2/adjudicate.py` as the adjudicator of record.
3. If HIT=True, it stays FLAGGED-FOR-ORACLE for external confirmation. Do not write
   "solved" anywhere on the strength of internal instruments alone.

## Ordinary candidates (`run/candidates.jsonl`)

Append+fsync at cand_bar 5.0 (2.38 below claim bar — nothing near the bar is dropped).
Expected ~3e5 flags over a full 2^32 lane on pure noise (Gumbel 6.95e-5/seed; measured
1.28x that on a 6M-seed noise run — inside K2 [0.2x, 5x]). Each flag should be
re-scored by Python stage_b (tail the file concurrently, or batch at lane end). Any
C-vs-Python pmax disagreement > 1e-6 on the same seed = K4 kill: halt, parity is void.

## ETAs (gate throughput 128,529 seeds/s; bench: 158k/s burst, 104k/s sustained — the
host thermally throttles under all-core load)

| lane | space | ETA @ gate 128.5k/s | ETA @ sustained 104k/s |
|---|---|---|---|
| S1 (pair, R25 config, from 0) | 2^32 | ~9.3 h | ~11.5 h |
| S2 (keyskip1 'exact') | 2^32 | ~9.3 h | ~11.5 h |
| **total** | 2 x 2^32 | **~18.6 h** | **~23 h** |

**Observed at launch (2026-09-07, 9m47s health watch):** 62,224,134 seeds done =
**106,000 seeds/s aggregate** (0.82x the 128,529 gate figure, matching the 104k/s
sustained bench — thermal throttling under all-core load, environment not engine).
Candidate rate 8.99e-5/seed = 1.29x the Gumbel prediction 6.95e-5 → **K2 checkpoint
(1% coverage) passed live**. Best pmax after 1.45%: 7.035050 @ word 2873275872 (below
claim bar; sits in candidates.jsonl for Python re-score). All 6 threads alive, CPU
~535%, checkpoints atomic every ~30 s. Live ETA at 106k/s: S1 done ~11.1 h from
launch (~2026-09-08 06:30), S1+S2 ~22.5 h total.

## S2 gate (PREREG)

S2's null does NOT count until it has its own planted control + V1-style vector file
(encipher_keyskip plant, not skip_by_two). The engine sweeps it mechanically; the
P0/P2 lanes own that validation. Track: the control must exist and PASS before S2's
results are written up.

## S3 (not in the plan — why)

The task allowed S3 cells if each lane's ETA <= 24 h (it is, ~9.3 h/cell), but PREREG
§S3 additionally requires **each** S3 cell to run with its own prereg addendum, planted
control and vector set (doctrine Q1/R1) — none exist yet, so adding them now would
generate unvalidated nulls. To add later: P0 produces the per-cell controls/vectors,
append the cells to `sweep_plan.json`, and relaunch (completed lanes are skipped).

## Kill conditions (from PREREG, standing)

- K2 @ 1% coverage (~43M seeds): candidate rate outside [0.2x, 5x] of 6.95e-5/seed → halt+audit.
- K3 @ every restart: self-test must PASS.
- K4 standing: C-vs-Python re-score disagreement > 1e-6 → halt.
