# Round 28 / L4 — grind28: build, gate, queue, run

grind28 is grind27 (`../../round27/P1-engine/grind27.c`, the R27 V1/V2/V3/K4-validated
architecture) plus the unswept generators and a **structural per-cell gate**. grind27's
sources and `P1-engine/run/` are untouched; this is a separate binary in this directory.

## Generators added (reducer names accepted in plans)

| name | generator | validated against |
|---|---|---|
| `php_mt_scale` | PHP mt_rand, canonical `MT_RAND_MT19937` twist, `init_genrand(w)`, temper>>1, `RAND_RANGE_BADSCALING(0,28)` | `/usr/bin/php` 8.5.4, `ref_php.php` |
| `php_mt_mod` | same generator, `%29` | same |
| `php_php_scale` | the documented pre-7.1 `MT_RAND_PHP` broken twist (mask from `loBit(u)`), badscaling | same (PHP still carries the legacy engine; its `mt_rand(0,28)` in this mode measured `=== ` badscaling) |
| `php_php_mod` | broken twist, `%29` | same |
| `glibc_mod` | glibc `srandom/random` TYPE_3 additive (int32 Schrage chain, 310-discard), out>>1 `%29` | resident glibc via `ref_glibc.c`; `rand()==random()` measured on every probe seed |
| `random29`/`grb5_mod`/`grb5_rej`/`shuffle29` | grind27's Py2.7-MT reducers (for the S3 offset cells) | inherited grind27 V1 + per-cell gates |

Generator reference chain: `gen28.py --selftest` proves the pure-Python side |Δ|=0
against both on-box references (8 seeds × 2000 draws, `receipts/genval.json`), then
`make_gates.py` freezes 64-seed vectors per cell through the R25 Python pipeline
(imported verbatim), then the C engine must reproduce those |Δ|=0 at launch.

## Build

```bash
cd liber-primus/analysis/round28/L4
gcc -O2 -o ref_glibc ref_glibc.c
nice -n 15 python3 gen28.py --selftest            # MUST print pass=True
cp ../../round27/P1-engine/engine.dat .           # then point PANEL_PATH at ./panel_lm.f32
cp ../../round27/P1-engine/panel_lm.f32 .
gcc -O3 -march=native -fopenmp -std=gnu17 -ffp-contract=off -o grind28 grind28.c -lm
nice -n 15 ./grind28 --self-test                  # grind27 S1 anchor: MUST PASS
nice -n 15 python3 make_gates.py                  # 25 cell gates + receipts + queued_cells.json
for f in gates/cellgate_*.dat; do nice -n 15 ./grind28 --gate-check "$f"; done  # all PASS
```

(`engine.dat`, `panel_lm.f32`, `grind28`, `ref_glibc`, `gates/*.dat` are regenerable —
gitignored; sources + receipts are committed. Do NOT add `-ffast-math`.)

## The structural gate (what replaced grind27's `GRIND27_S2_CONTROL_OK`)

Every plan lane must name a `"gate"` file. At launch, before ANY null counts, the engine
re-runs that cell's (a) 64-vector parity (ks128 |Δ|=0 + decode artifacts ≤1e-9, measured
0.0), (b) planted-control screen (the plant must be FLAGGED with the reference pmax),
(c) false-reject set (every wrong seed matched, all below the cell claim bar). Missing,
mismatched (lane/reducer/offset/relation cross-checked) or failing gate ⇒ the lane
REFUSES to sweep. There is **no override env var**. Negative-controlled: a tampered
gate FAILs; a gateless or mismatched plan lane REFUSES (see `smoke/`, RESULTS.md).

## Running the queue (chain phase — ONLY after R27 S2 exits + its closeout)

```bash
cd liber-primus/analysis/round28/L4
mkdir -p run
setsid nice -n 10 nohup ./grind28 --plan queued_cells.json --run-dir run \
  >> sweep28.log 2>&1 & sleep 2; pgrep -f 'grind28 --plan' | tee sweep28.pid
./grind28 --status --run-dir run            # cheap poll
```

Same checkpoint/resume semantics as grind27 (STATUS.json + hist_<lane>.u64 +
top_<lane>.json + append-only candidates.jsonl + HIT-CANDIDATE.json
FLAGGED-FOR-ORACLE; re-run the same command to resume; completed lanes skip).
Closeout per lane: `nice -n 15 python3 stage_a28.py --run-dir run --lane <LANE>`
(K4 parity: any |C−Python| > 1e-6 voids the lane), then hitfn20/oracle_crosser on
any claim-bar crossers exactly as R27's ORACLE-*.md pattern.

## Calibration (2026-09-08, single thread, nice 15, S2 RUNNING on all 6 cores)

See `receipts/calibration_bench.txt` — 5.2–11.0k seeds/s/thread contended; anchor
`random29 pair` measured 11.0k contended vs grind27's 32.4k uncontended single-thread
(≈3× contention). Post-S2 6-thread sustained estimates in QUEUE.md.
