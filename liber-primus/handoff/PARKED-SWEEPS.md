# PARKED-SWEEPS — every sweep that is stopped, where it stopped, and how to resume it

_Written 2026-10-05. This file exists because for three weeks this repository told its
readers that three sweeps were **IN-FLIGHT** when all three had been dead since
**2026-09-15**, when the machine running them rebooted. None was resumed._

A stopped sweep described as running is worse than no sweep at all: it tells the next
researcher that a branch is being handled, so they leave it alone. Everything below is
**parked**, not in progress, and all of it is yours to take.

Each entry gives the state file (now committed, so you can check these numbers in a fresh
clone rather than taking this page's word), the exact coverage reached, and the resume
route. The bulk sweep output — `candidates.jsonl`, the `u64` histograms, the compiled
engines — is still gitignored and is **not** in a clone; it regenerates, and resume does
not need it except where noted.

**None of these is a verdict-changer on its own.** They are the last internally runnable
branches of the derived-key family. The honest summary of why they are parked is in
[`FOR-FUTURE-SOLVERS.md`](FOR-FUTURE-SOLVERS.md) and
[`PARKED.md`](PARKED.md): this project ran out of machine, not out of ideas.

---

## 1. Round 27 / S2 — Py2.7-MT 2³² `exact` (keyskip1) lane — **44.14 % covered**

| | |
|---|---|
| State file | `liber-primus/analysis/round27/P1-engine/run/STATUS.json` |
| Top-1024 screen rows | `liber-primus/analysis/round27/P1-engine/run/top_S2.json` |
| Last write | 2026-09-15 22:24 local |
| Seeds scored | **1,895,728,884** of 4,294,967,296 (`lane_coverage_fraction` 0.441383776) |
| Workers | 6, each ~44 % through its own band; `done: false` on all six |
| Throughput when it died | 77,124 seeds/s (≈ 8.6 h of wall clock left) |
| Claim bar | 7.6341931878728095 |
| `n_claim_bar_hits` in STATUS.json | **0** |

**The one thing to check first on resume.** `run/HIT-CANDIDATE.json` records a flag on this
lane — seed **35563892** at pmax **7.6707232992600876**, above the S2 bar — and that is the
*same seed at the same pmax to the last digit* that the **S1** lane flagged and that
[`ORACLE-35563892.md`](../analysis/round27/ORACLE-35563892.md) adjudicated
**NOISE-CROSSER** (hitfn20 clause 1 FAIL at L=240: 4.96 vs bar 7.384, parity Δ = 0.0).
`STATUS.json` for S2 simultaneously says `n_claim_bar_hits: 0`.

Those two files cannot both be right, and this project has **not** resolved which is. Either
S2 genuinely re-flagged the seed under the `exact` relation, or the hit record carried over
from the S1 run that finished 24 minutes earlier and the S2 counter is the accurate one. Do
not treat the flag as an S2 survivor and do not wave it off; re-screen seed 35563892 under
the `exact` relation and compare against the stored pmax before resuming the grind.

**Resume:** the resume block in
[`analysis/round27/MONITORING.md`](../analysis/round27/MONITORING.md). Resume is proven
exact — no gap, no double-count, and the completed S1 lane is skipped. It needs the
`run/` directory, so it resumes only on the original machine; from a clone you re-run the
lane from seed 0 after rebuilding `grind27` per `analysis/round27/P1-engine/BUILD.md`.
`sweep.pid` holds **701083**, which is dead — never `pkill -f`, kill only by PID.

**S1, by contrast, is genuinely finished:** all 2³² seeds scored exactly once, three
claim-bar crossers all oracle-adjudicated NOISE-CROSSER, lane **NULL**. See
[`analysis/round27/S1-CLOSEOUT.md`](../analysis/round27/S1-CLOSEOUT.md). That one is closed
and needs nobody.

## 2. Round 28 / L4 — 25-cell unswept-generator queue — **never sanctioned, 0 % authoritative**

| | |
|---|---|
| State file | `liber-primus/analysis/round28/L4/run/STATUS.json` |
| Audit marker | `liber-primus/analysis/round28/L4/run/ORPHANED-PREMATURE-RUN.txt` |
| Ledger row | `R28-L4-UNSWEPT-GENERATORS-QUEUE` |

The sanctioned queue (25 gated 2³² PHP / glibc / S3 cells) was armed behind the running S2
and **never fired**. What is on disk instead is the output of a premature launch against
`L4/QUEUE.md`'s DO-NOT-FIRE hold, SIGTERM-stopped by the Round-28 coordinator and
**orphaned**: 27,261,684 seeds (0.63 % of one cell), best pmax 6.765 against a claim bar of
9.638, 2,508 partial candidates. The red team verified before orphaning that nothing near a
bar was dropped (finding D5, `analysis/round28/R-redteam/RESULTS.md`).

**Claim no coverage from it.** The ledger row claims none either. The sanctioned queue's
designated output path is `analysis/round28/run/`, which does not exist yet — nothing has
ever legitimately run there — and a resumption starts from seed 0 in it.

## 3. Round 28 / L3 — string-seed amd64 dictionary — **11 of 11 queued items complete, lane row never filed**

| | |
|---|---|
| State file | `liber-primus/analysis/round28/L3/progress28.json` |
| Last write | 2026-09-15 23:45 local |

All eleven queued items report `status: complete`, and the lane's own top-level field reads
`stopped: "all-items-complete"` — so unlike the two above, this one did not die mid-grind, it
finished. **2,500,207** seeds scored across `random29` / `grbmod` / `grbrej` / `shuffle29` at
tiers t0 / t1 / t1b / t1c, both the `pair` and `exact` relations, in 7,829 s. Best pmax over
the whole lane is **6.3148** (`r29_exact_t1c`); **226** rows escalated to stage B;
`flagged_survivors` is **empty**. There is a `controls_ok_stamp` of 2026-09-08T11:45:09, so
the lane's positive-control gate did fire before the sweep counted.

So the compute is done, paid for, and looks like a clean null — and the lane was still never
closed out. There is no `L3/RESULTS.md` verdict and no `LEDGER.json` row, which means this
result does not exist as far as the artifact every front door tells you to query is
concerned.

**This is the cheapest open item in the repository.** What it needs is not compute but the
write-up its own doctrine requires: the control's *measured recovery* stated (the stamp says
the gate passed, not at what power), the null stated, the threshold confirmed fixed in
advance, coverage and `not_covered` tabulated — then a ledger row. Do not file it as a
negative on the strength of `progress28.json` alone: that file holds the sweep, not the proof
that the instrument could have seen a hit.

---

## How to tell, in one command, whether anything here is actually running

```bash
for f in $(find liber-primus/analysis -name '*.pid'); do
  p=$(cat "$f"); printf '%s -> %s ' "$f" "$p"
  ps -p "$p" >/dev/null 2>&1 && echo RUNNING || echo DEAD
done
```

As of 2026-10-05 every PID in this repository is **DEAD**: `round27/sweep.pid` (701083),
`round28/L3/sweep28.pid` (678469), `round28/L4/sweep28.pid` (699288 / 699322), and
`round28/chainer.pid` (empty). If you are reading this much later, run the command rather
than believing the date.
