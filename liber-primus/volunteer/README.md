# Volunteer compute: finish a parked seed sweep

**What this is.** One branch of the Liber Primus problem is compute-bound: the keystream
might be *derived from a short seed* rather than being a true one-time pad. If it is, a
2³² seed sweep can find it. This kit lets anyone donate CPU to the one such sweep that is
parked part-way, with results anyone can recheck.

**Be clear-eyed about the odds.** This lane tests one specific generator hypothesis
(Python 2.7 Mersenne Twister, `init_by_array`, `random29`, the `exact` skip relation). Most
likely it comes back empty, and an empty result is still a real, citable negative. Nothing
here is a solve unless a human oracle says so (`../HUMAN-ORACLE.md`).

## The lane

| | |
|---|---|
| Lane | **S2**: Round 27 Py2.7-MT `exact` relation, scored by the 12-register panel-R36 |
| Covered already | **52.05 %** of 2³², 0 claim-bar hits (`../analysis/round42/S1-s2-recovery/state_recovered/STATUS.json`). Prior work, mixed instrument; see `COVERAGE.md` |
| Remaining | **2,059,271,710 seeds** in **36 shards** of ~57M seeds each (`shards.json`) |
| Speed (measured 2026-11-17) | **62,000 seeds/s on 6 threads** (Intel Core Ultra 7 258V, WSL2). About **15 min per shard on 6 threads**, about **95 min on one core**. The whole remainder is roughly 9 hours on one 6-thread laptop |
| Engine | the committed C engine `../analysis/round36/P1-panel-r36/engine_inputs_copy/grind27.c`, compiled **unmodified**; every input is checked against a sha256 pin in `shards.json` |

## Run a shard

Needs Linux or WSL or macOS, `gcc` with OpenMP, Python 3.9+. No other dependencies.

1. **Claim it.** Open an issue with the *Claim a lane* template, naming the shard ids
   (e.g. `S2-007, S2-008`). Pick `unclaimed` ones from `shards.json` or `COVERAGE.md`.
2. **Run it.**
   ```bash
   cd liber-primus/volunteer
   python3 run_shard.py --gates-only        # optional: build + self-tests only, about a minute
   python3 run_shard.py S2-007              # build, gates, sweep, write results/S2-007.json
   ```
   Before sweeping, it runs the gates: the panel gate, the engine self-test, the Round 38
   planted control reproduced to the last digit, and the known anchor seed. **If any gate
   fails it refuses to sweep.** A broken instrument produces a fake negative. Open an issue
   with the output instead.
3. **Submit it.** Open a PR that adds `results/S2-007.json` and changes that shard's
   `status` to `done` (with your handle as `claimant`) in `shards.json`. The
   `volunteer-verify` workflow rechecks it using the verifier from `master`, not from your PR.

Interrupted? Just re-run the same command. The shard starts over.

## How results are checked

`verify_shard.py` checks the arithmetic (range, counts, histogram, `result_sha256`), then
re-scores with the stock engine: every reported top seed, a random sample of candidates, a
random sample of seeds from the range, and 8 whole random windows. Scores must match to the
last bit. That is a spot check, not a proof. `--full` re-sweeps the whole shard, which is a proof.
Tested 2026-11-17: a genuine result passes, and five tampered variants (edited fields, a
changed score, a dropped candidate, a partial range, a hidden best seed) all fail.

## If a seed crosses the claim bar (7.634)

The result is marked `flagged_for_oracle`. It goes to a human for review under
`../HUMAN-ORACLE.md`. It is **never** announced as a solve. Seed 35563892 already crosses
the bar and was adjudicated as noise (`../analysis/round27/ORACLE-35563892.md`); the kit uses
it as a test.

## Files

| file | role |
|---|---|
| `shards.json` | the shard table and lane pins (sha256 of every engine input, thresholds, controls) |
| `run_shard.py` | build → gates → sweep → `results/<id>.json` |
| `verify_shard.py` | recheck a submitted result (CI runs this) |
| `coverage.py` | rewrites `COVERAGE.md` from `shards.json` + `results/` |
| `make_shards.py` | how the 36 shards were cut from the six Round 27 worker gaps (do not re-run) |
| `_kit.py` | shared build/gate/engine helpers |
| `results/` | submitted shard results (one JSON per shard) |

`build/`, `runs/` and `__pycache__/` regenerate and are gitignored.
