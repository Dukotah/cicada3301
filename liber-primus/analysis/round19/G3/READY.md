# ROUND 19 / G3 — READY
### Phase 2 run spec for the Python 2.7 `random.seed()` keystream family

_Lane G3 held at the scoring boundary as required. The generator is **VALIDATED** (see
`RESULTS.md` §3), the plumbing is proven end-to-end (§7 there), and this file is the run spec
S1 executes once Phase 0's three gates pass._

---

## 0. Status

| item | state |
|---|---|
| generator `gen_py27.py` | **VALIDATED** vs real CPython 2.7.3 amd64, 2.7.3 i386 and 2.7.18 amd64 — 10,825 + 2,000 vectors, 0 failures |
| enumerator (identity plant-and-recover, V8) | **PASS**, recovery 1.000, uniqueness 1.000 over 17,320 configs |
| keystream interface | `gen_py27.keystream(seed, mode, n, wordsize=, jump=)` -> `list[int]` in `[0,29)` |
| plumbing G3 -> I1 -> I2 -> SWEEPROW | **PROVEN**, `adjudicate.validate_store` 9,600 / 9,600 |
| **blocking on** | **I1 + I2 + I3 gates PASS.** G3 sets **no bar**; see §5 |

**Pre-registered pilot overrun, declared.** `PREREG.md` §6 allowed a labelled pilot of
**≤ 10,000** decodes. Two runs were made: a **512**-decode sizing probe (to measure ms/decode
before committing to a pilot size) and the **9,600**-decode pilot, **10,112 total — 112 over
the ceiling**. Recorded here rather than quietly rounded down. No further decodes were run.

---

## 1. The one call S1 needs

```python
import sys
sys.path.insert(0, ".../analysis/round19/G3")
from gen_py27 import keystream, REDUCER_NAMES     # ('random29','grb5_mod','grb5_rej','shuffle29')

K = keystream(seed,               # bytes | str | int | float  — a B-04 dictionary entry, as-is
              mode="random29",    # one of REDUCER_NAMES
              n=NEEDED,           # give the beam headroom: n >= L*(max_skip+1)+64
              wordsize=32,        # 32 = i386 python2.7, 64 = amd64 python2.7
              jump=None)          # int -> Python 2's random.jumpahead(k) after seeding
```

Seed dictionary, **reused not rebuilt** — `analysis/round13/B04/seeds.py`:
`build()` -> 2,165 `(family, bytes)`; `core(entries)` -> 504.

**`random29` is Python 2.7's `randrange(29)`, `randint(0,28)` and `choice(pool29)` — all
three are the same call in 2.7** (`RESULTS.md` §2.5, gate V5). Do not add them as separate modes.

Every row's `kid` must encode `seed|mode|wordsize|direction|sign|atbash|offset|jump` so that,
with the SWEEPROW header, the decode is regenerable. The pilot's format is a working example:
`THETOTIENTFUNCTIONISSACRED|shuffle29|ws64|fwd|s-1|aboff`.

---

## 2. Measured throughput

From the pilot (`RESULTS.md` §7), single core, **including** I2 adjudication and JSONL write:

```
L = 120, I1 mode=keyskip1, beam_w=400, max_skip=3   ->  50.0 decodes/s/core  (19.99 ms/decode)
this box: nproc = 6                                 -> 300   decodes/s aggregate
SWEEPROW JSONL: 1,683,895 B / 9,600 rows            -> 175.4 bytes/row
```

Per-mode cost multipliers, taken from **I1's own** published profile
(`round19/I1/out_base.json`, median seconds at L=240):

| I1 mode | median s | vs `keyskip1` |
|---|---:|---:|
| `keyskip1` (`repo_ms3`) | 0.260 | x1.00 |
| `keyskip1`, `max_skip=8` (`exact_ms8`) | 0.259 | x1.00 |
| **`keyskip2`** (`pair_ms8`) | 0.297 | **x1.14** |
| `permissive` / drift (`drift_l0/l8/l16`) | 1.71–1.83 | **x6.6 – x7.0** |

---

## 3. The run, ordered highest-prior-first

Ordering rationale: (a) the **enumerable** branch before the samplable one (doctrine R5 and
`RESULTS.md` §5.2 — 32-bit userland was the default 2012 Ubuntu desktop install); (b) the
**never-covered** cells before anything adjacent to a duplicate; (c) the cheap decoder modes
before the x7 drift modes; (d) offsets last, because they multiply everything.

| tier | what | decodes | I1 modes | wall @ 6 cores |
|---|---|---:|---|---:|
| **T1** | **Stage A, `seed(str)`** — 2,165 seeds x 4 reductions x ws{**32 first**, 64} x sign{-1,+1} x dir{fwd,rev} x atbash{off,on}, offset 0 = 138,560 | 138,560 | `keyskip1` | **7.7 min** |
| **T2** | T1 repeated under the L7-B construction | 138,560 | `keyskip2` | **8.8 min** |
| **T3** | **Stage A', `seed(str)` + `jumpahead(k)`**, k in {29, 761, 1033, 3301} — 504 core seeds x 4 reductions x ws{32,64} x 4 k x 8 orientations = 129,024 | 129,024 x 2 | `keyskip1`,`keyskip2` | **15.3 min** |
| **T4** | **The two never-covered integer-seed cells** — `grb5_mod` and `shuffle29` over 2011-2015 unix seconds at 1/day stride (1,828 seeds, R16-PRNG's convention) x 8 orientations = 29,248. **`random29` and `grb5_rej` on the int axis are exact duplicates of Round 8 gen=8 / gen=7 and must NOT be re-swept — they go to S2 re-adjudication instead** (`RESULTS.md` §4.3) | 29,248 x 2 | `keyskip1`,`keyskip2` | **3.5 min** |
| **T5** | **Stage B, offsets** — 504 core seeds x reductions{`random29`,`grb5_rej`} x ws{32,64} x 10 B-04 offsets x 8 orientations = 161,280 | 161,280 x 2 | `keyskip1`,`keyskip2` | **19.1 min** |
| **T6** | **Drift escalation** — top **2,000 per ranking statistic** over T1-T5 for each of `pmax`, `pmax_ne`, `pcon`, `ioc`, `en` (five separate top-N lists, per I2's SWEEPROW §4 — **never one top-N by English**), de-duplicated, re-decoded under I1 `permissive` at the drift settings I1 publishes | approx. 10,000 x 2 drift settings = 20,000 | `permissive` | **7.8 min** (x7 cost) |
| | **total** | **approx. 1.22 M decodes** | | **approx. 62 min** |

Storage: 1.22 M x 175 B = **214 MB** as JSONL. Past ~10^6 rows use I2's binary store
(`adjudicate.ROW_DTYPE`, 77 B/row = **94 MB**) plus the key table, and commit only the header,
the five top-N files and the summary histograms (I2 SWEEPROW §6).

**Suggested split.** T1+T2 alone (277,120 decodes, ~17 min) already cover the whole
never-swept string-seed space at offset 0 under both of I1's exact transition relations. If
budget is tight, that is the shippable unit; T3-T6 are extensions.

---

## 4. The optional extension: enumerating the i386 branch (NC-3)

`RESULTS.md` §2.4 measures that on a 32-bit Python 2.7 **every possible non-int seed** —
every string, every float — lands on `init_by_array([w])` for some `w` in `[0, 2^32)`. So the
32-bit half of this family is not a dictionary problem at all; it is a **4,294,967,296-state
enumeration**, the same size as the nine full-32 sweeps already on disk in
`analysis/seed_sweep/results_full32.txt`.

It is **not** affordable through this Python path: 4.295 x 10^9 / 300 per s = **166 days**.
It becomes affordable only as a two-stage design, and that is a *build* task, not a compute task:

1. **Stage 1 — C prefilter.** Port `gen_py27.py`'s `init_by_array` + the four reducers into
   the existing `analysis/round10/L5-seed32/sweep32x.c` harness (it already carries MT19937 and
   a validated-generator gate). Round 8 pushed 2^32 through that harness in 0.8-3.1 h per
   generator. Screen on a cheap language-agnostic statistic (**IoC and min-distinct-symbols**,
   not English 4-grams — that is the L7-A mistake), keeping a fixed fraction, not a fixed bar.
2. **Stage 2 — full instrument.** Run the survivors through I1 + I2 at I3's threshold.

Prerequisite: the C port must clear the same V2/V3 gate this lane's Python did, against the
same three real interpreters. `validate_py27.py` is structured to accept an alternative
generator with a one-line change.

---

## 5. The threshold — deferred, deliberately

**G3 states no hit bar, and S1 must not import one from this lane.**

Use **I3's published curve** for the statistic and the N actually run. Specifically, do not use:

- **-5.5** — B-04's and D3's floor. Invalid at large N (doctrine §4 mechanic 4), calibrated
  for the single-register English quadgram scorer that L7-A measured at power 0.33 (Latin)
  and 0.00 (vowel-dropped English), and **lane G2 measured that under I1's `drift3` /
  `union0_5` modes pure random data scores -4.51 / -4.82** — i.e. the -5.5 bar is not merely
  loose there, it is *below* the noise floor and would fire on everything.
- **-12.5** — the Round 8 `seed_sweep` bar. Different scale, different scorer, rigid decoder.

Two calibration facts this lane can hand I3, both from the pilot's 9,600 presumed-wrong decodes
at L=120 (`RESULTS.md` §7):

- `en`: mean **-7.3416**, sd **0.2292**, max **-6.4955** — reproducing B-04's L=120 null
  (mean -7.366, max -6.826) closely enough to confirm both are on the same scale.
- `pmax` (max over the nine-register panel): mean **1.6422**, sd **0.7943**, **max 5.0290 in
  9,600 noise decodes**. Any Phase-2 bar on `pmax` must be an order statistic at the sweep's
  real N, not a fixed z.

---

## 6. Reporting requirements S1 inherits from this lane

1. **Store the full SWEEPROW for every decode** (doctrine R3, CI-enforced). The pilot's header
   is a working template: it already carries `key_space`, `decoder` and `generator`, which are
   doctrine Q4's three conditionals.
2. **Label the word-size axis in the `kid`.** `ws32` and `ws64` are different generators, not a
   nuisance parameter.
3. **Report the three conditionals** exactly as `RESULTS.md` §6 states them.
4. **Report coverage x power**, with power taken from I1/I2's measured envelope for *this*
   hypothesis class — not asserted, and not inherited from a different construction.
5. **Keep five top-N lists, one per ranking statistic.** Not one, and not by English.
6. **Do not report the duplicate integer-seed cells as new coverage.** `seed(int)`+`random29`
   and `seed(int)`+`grb5_rej` are Round 8 gen=8 / gen=7 over the full `0..2^32`; they belong to
   S2's re-adjudication, and their prior negatives were produced by a **rigid** decoder at
   approximately zero power for LP2's construction (`RESULTS.md` §4.3).
