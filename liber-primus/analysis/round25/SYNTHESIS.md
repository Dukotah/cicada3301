# Round 25 — SYNTHESIS (bounds, not a verdict — PARKED mid-sweep)

_Written 2026-08-31 by the coordinator, from `compute-tail/RESULTS-chunk1.md`,
`compute-tail/RESULTS-parked.md`, and the committed per-worker checkpoints. Doctrine
[`ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) R7. Trust anchor `python tests/validate.py` →
**ALL VALIDATIONS PASSED (5/5)**. Ledger entry: `R25-COMPUTE-TAIL-CHUNK1` (carries the
`parked_state` block)._

---

## 0. What Round 25 is

Not an armada — an **owner-elected compute grind** of the one branch every preceding round agreed
was still runnable and still untouched: the **Python-2.7 MT19937 `init_by_array([w])` 2³² seed
tail** under the `random29` reducer, at an honestly **low** prior. No new instrument, no new
hypothesis: the lane applies the already-control-validated Round-24 pipeline (the skip-aware
`pair`/`keyskip2` decoder — the relation the plain beam cannot represent — plus the `hitfn20`
three-clause recovery gate) to fresh contiguous slices of the tail, checkpointed so the campaign
can stop and resume at any time.

---

## 1. State at park (2026-08-31) — verifiable from the committed checkpoints

| quantity | value |
|---|---|
| cumulative 2³² coverage | **21,539,647 words = 0.5015 %** (parallel workers 20,787,079 + chunk-1 506,593 + excluded already-swept baseline 245,975) |
| hits / flagged-for-oracle | **0 / 0** |
| global best pmax | **6.826** (word 2149309687) vs the pair claim bar **7.384** — deep in noise |
| positive control | in-band planted-seed test **PASSES every invocation** (recovery 1.000, held-out 1.000, HIT=True) — plus a live parallel-mode drill: a seed planted into worker 0's band fired the HIT path, wrote `HIT.json`, and stopped all 6 workers in 10.8 s |
| throughput | ~384 seeds/s single-core; **1,650–1,966 seeds/s** on the 6-core supervisor (pure CPython) |
| remaining | ~4.27×10⁹ seeds ≈ **25–32 continuous wall-days** at that rate |

The coverage number is not taken on faith: the per-worker `progress_w{0..5}.json` checkpoints are
**committed**, and summing their `seeds_done` fields reproduces it exactly. `RESULTS-parked.md` is
the canonical parked-state record; `RESULTS-chunk1.md` documents only the initial single-core
chunk (its 0.0175 % figure describes that chunk alone).

---

## 2. What this grind can and cannot settle

- It covers **only** the Py2.7-MT generator, `random29` reducer, offset 0, under the pair decoder.
  Untouched: >99.49 % of this space, the other reducers and the amd64 image (their prior-dense
  fronts were swept clean in R21-L3), bash/perl/tex tails (prior-dense fronts swept in R24
  C2-EXT), and the `/dev/urandom` branch, which no amount of compute recovers.
- A completed null converts "probably not a cheap seeded PRNG" into "the Py2.7 `random29` seed
  space is not where the pad came from." It never touches the CSPRNG branch and never moves the
  OTP-class verdict (doctrine R7).
- Any word clearing the full three-clause gate is **FLAGGED-FOR-ORACLE and stops the sweep** —
  never auto-certified, because R21-L1's KILL on the no-oracle seal still stands.

## 3. Resume / unlock

```
cd analysis/round25/compute-tail
python3 parallel_grind.py            # each worker resumes from its progress_w{i}.json cursor
python3 parallel_grind.py --status   # poll coverage / best-pmax / HIT without touching workers
```

**Highest-leverage change if this lane is ever resumed in earnest:** pure CPython is the only
reason it is slow. A GPU or C port of the generator→decoder→scorer pipeline covers 2³² in
**hours**, not weeks.

## 4. Standing verdict

Unchanged: **LP2 0–54 is OTP-class** — statistically indistinguishable from a one-time pad under
every tested class, with a soft anti-repeat rewrite acting on the ciphertext output. Round 25 is
the project's disciplined way of spending idle compute against the last enumerable branch without
pretending the prior is anything but low.
