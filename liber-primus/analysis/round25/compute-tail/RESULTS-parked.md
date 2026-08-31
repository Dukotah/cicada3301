# Round 25 — compute-tail (Py2.7-MT 2^32 seed grind) — PARKED STATE

**Date parked:** 2026-08-31
**Status:** PARKED (owner-directed pivot), fully resumable. Not committed (WSL no creds).

## Why this file exists
`RESULTS-chunk1.md` documents only the initial single-core **chunk 1** (506,593 seeds at
383.8 seeds/s). The bulk of coverage came from the subsequent **6-core `parallel_grind.py`**
run, whose coverage lived only in the per-worker checkpoints (`progress_w{0..5}.json`) and the
`--status` aggregate — never in a RESULTS file. This file is the canonical record of the
parked parallel-grind state so the docs and a future reader agree on the real number.

## Parked state (measured via `parallel_grind.py --status`)
- **Cumulative 2^32 coverage: 21,539,647 words = 0.5015%** of the 4,294,967,296 seed space
  (includes chunk-1's 506,593 + the excluded baseline 245,975 + the 6-core parallel sweep).
- **Hits: 0.** No seed cleared the recovery-gated three-clause gate.
- **Global best pmax: 6.826** (word 2149309687) vs the **pair claim bar 7.384** — deep in noise.
- **Control:** the in-band planted-seed test PASSES (recovery 1.000, HIT=True), so this null is a
  true negative, not a broken scan.

## Throughput / remaining
- 6-core aggregate ≈ **1,650–1,966 seeds/s** (pure CPython 3.14, 6-core WSL box).
- Remaining ≈ 4.27e9 seeds ≈ **25–32 continuous wall-days** at this rate.
- **Unlock:** pure-Python is the only reason this is slow. A GPU/C port of the
  generator→decoder→scorer pipeline does 2^32 in **hours**, not weeks. That is the single
  highest-leverage change if this lane is ever resumed in earnest.

## Scope / what this does and does not close
- Covers ONLY the Python-2.7 Mersenne-Twister generator, offset-0, at ~0.5% of its space.
- Does NOT touch: the >99.5% Py2.7 tail, other generators (bash/perl/tex — see R24 C2-ext for
  their skip-aware closure on prior-dense slices), or `/dev/urandom` / true-entropy pads
  (unguessable by construction).
- Verdict unchanged: LP2 0–54 remains OTP-class. This grind, if completed null, converts
  "probably not a cheap seeded PRNG" into "the Py2.7 seed space is exhausted — not there."

## How to resume
```
cd analysis/round25/compute-tail
python3 parallel_grind.py            # resumes each worker from its progress_w{i}.json cursor
python3 parallel_grind.py --status   # poll coverage/best-pmax/HIT without touching workers
python3 parallel_grind.py --self-test # confirm the pipeline still recovers a planted seed
```
On a hit: `HIT.json` is written, all workers stop, the run exits non-zero. The hit is
**FLAGGED-FOR-ORACLE, never auto-certified** (R21-L1: the no-oracle seal is provably leaky).
