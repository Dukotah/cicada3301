# ROUND 19 / LANE G2 — READY
## What Phase 2 must run for Perl 5.14 `rand`/`srand`, and how long it takes

_2026-08-26. Companion to [`PREREG.md`](PREREG.md) and [`RESULTS.md`](RESULTS.md).
Every rate below is **measured on this box** (`bench.json`, `pilot.json`,
`budget.json`) or cited from an in-repo measurement. Nothing is estimated from
intuition._

---

## 0. Status of this lane

| deliverable | state |
|---|---|
| generator validated byte-exactly against real Perl | **DONE** — `validation.json`, gates A/B/C, 186 checks, 0 failing |
| era question (5.40 on this box vs 5.14 target) | **RETIRED BY MEASUREMENT** — see §6 |
| keystream production interface | **DONE** — `gen_perl.make_ks(reduction, seed, nsym)` |
| space statement (size, enumerability, coverage fraction) | **DONE** — §1, §2 |
| pre-registered positive control artifact | **DONE** — `plant.json`, 5 registers × 3 constructions |
| end-to-end plumbing through I1/I3 + I2 | **PROVEN** — `pilot.json`, 9,984 decodes, **0** SWEEPROW validation failures |
| scored sweep | **NOT RUN, BY DESIGN.** Phase 0 gates have not published PASS |

---

## 1. The space, stated precisely

**Seeds: 2³² = 4,294,967,296. Bounded, enumerable, and with NO residue.**

This is the unusual part and it is the reason to run the lane. Two facts, both
read out of the Perl 5.14.2 source and both confirmed by measurement, close the
seed space completely:

1. `config_h.SH:2133` — `#define seedDrand01(x) srand48((Rand_seed_t)x)`, and
   glibc's `srand48_r` keeps only the low 32 bits of its argument. Every srand
   argument folds into 0..2³²−1. **Measured:** `srand(4294967297)` ≡ `srand(1)`
   ≡ `srand(2**33 + 1)` (validation gate C1).
2. `util.c: Perl_seed()` — the **auto-seeded** path reads `sizeof(U32)`, four
   bytes, from `/dev/urandom` and returns it. The most idiomatic possible
   script — `perl -e 'print chr(int(rand(29))) for 1..13000'` with no `srand`
   at all — therefore has a **uniform 32-bit** seed, not an unbounded one.

Contrast `round10/L5-seed32/CENSUS.md` §D, where Java's 48-bit `setSeed` and
Python's millisecond seeds leave residue orders of magnitude beyond 2³². Perl
leaves none. There is no "seeds wider than 2³²" line to write in `not_covered`.

**Full cross product** (B-04 §3.4–3.5 conventions, so rows stay comparable):

| axis | size |
|---|---:|
| seed | 2³² = 4.29 × 10⁹ |
| reduction (Perl-reachable) | 9 |
| sign × Atbash × direction | 8 |
| **Stage A (offset 0)** | **3.09 × 10¹¹ decodes** |
| Stage B offset ladder {1,4,16,29,64,128,256,512,1024,3301} | ×10 |

**Enumerable in principle. Not enumerable in Python.** §3 is the whole point of
this document.

---

## 2. Measured rates on this box (6 cores)

End-to-end = keystream generation + I3 `vecbeam.batch_decode` + I2 `adjudicate`
emitting the full SWEEPROW. From `pilot.json`, 9,984 decodes:

| tier | reduction | L | mode | gen /s/core | decode /s/core | adjudicate /s/core | **end-to-end /s/core** |
|---|---|---:|---|---:|---:|---:|---:|
| **screen** | r29 | 31 | keyskip1 | 2,440 | 2,822 | 1,344 | **663** |
| escalate | r29 | 120 | keyskip1 | 836 | 170 | 431 | **106** |
| escalate | r29 | 120 | skip_by_two | 813 | 171 | 462 | **108** |
| escalate | r29_nodup | 120 | keyskip1 | 1,009 | 273 | 629 | **160** |

Two observations Phase 2 needs:

* **The decoder is the bottleneck at L=120; the adjudicator is the bottleneck at
  L=31.** At L=31, `adjudicate_batch` (panel only) ran *slower* than the
  per-row `adjudicate` (700/s vs 1,344/s) because its internal 400-row chunking
  does not amortise on 312-row blocks. At L=120 the batch path is 50× faster
  (21,837/s). **Recommendation to I2:** either lower the chunk size or document
  a minimum block; Phase 2's screen tier is exactly the regime where it loses.
* **Permissive modes cost an order of magnitude.** `vecbeam.py --bench`,
  decode only, 1 core, L=120: `keyskip1` 168/s, `skip_by_two` 174/s,
  **`drift3` 12.8/s, `union0_5` 8.7/s.** If I1 ships a permissive relation as
  the primary one, divide every figure in §3 by ~13.

---

## 3. THE DECIDING NUMBER: Python cannot enumerate this space; C can

At the measured Python screen rate of **3,977 decodes/s** on 6 cores:

| cell | decodes | Python hours | **C hours** |
|---|---:|---:|---:|
| full Stage A (2³² × 9 reductions × 8 orientations) | 3.09 × 10¹¹ | 21,597 | **305** |
| 2³² × top-3 reductions × 8 orientations | 1.03 × 10¹¹ | 7,199 | **102** |
| 2³² × `r29` × 8 orientations | 3.44 × 10¹⁰ | 2,400 | **34** |
| 2³² × `r29` × 1 canonical orientation | 4.29 × 10⁹ | 300 | **4.2** |
| S1 era band × 9 reductions × 8 orientations | 9.09 × 10⁹ | 635 | **9.0** |
| S1 era band × `r29` × 8 orientations | 1.01 × 10⁹ | 70.5 | **1.0** |
| S0 authoring window × 9 reductions × 8 orientations | 3.39 × 10⁹ | 237 | **3.3** |

The C column uses the **in-repo precedent**, not a guess:
`round10/L5-seed32/results_newgens.txt` records generator 10 —
*this same Perl generator* — sweeping 126,230,400 seeds × 2 directions in
**168.1 s** with `OMP_NUM_THREADS=32` (`run_newgens.sh`), i.e. **46,933
decodes/s/core** at a 48-rune window. That is **71× the measured Python rate.**

> **Caveat, stated rather than buried.** That C precedent used a rigid
> F-branching decoder and an English 4-gram table. A Round-19 C screen must
> carry I1's transition relation and I2's nine-register panel, which are both
> heavier. **46,933/s/core is an upper bound and must be re-measured.** Even at
> a 3× haircut the conclusion is unchanged: C makes the top-3 reductions
> completely enumerable in days; Python does not make even one cell enumerable
> in a round.

What a fixed wall clock buys **in Python**, spent entirely on one reduction ×
one orientation:

| wall clock (6 cores) | decodes | fraction of 2³² | fraction of Stage A |
|---:|---:|---:|---:|
| 12 h | 1.72 × 10⁸ | 4.0 % | 5.6 × 10⁻⁴ |
| 24 h | 3.44 × 10⁸ | 8.0 % | 1.1 × 10⁻³ |
| 48 h | 6.87 × 10⁸ | 16.0 % | 2.2 × 10⁻³ |
| 72 h | 1.03 × 10⁹ | 24.0 % | 3.3 × 10⁻³ |

**Escalation is free; the screen is everything.** Promoting the top 10⁶ screen
rows to a full L=120 decode costs **26 minutes**; the top 10⁷ costs 4.4 hours.
So Phase 2 should spend essentially its whole G2 budget on the screen and
escalate generously.

---

## 4. THE RUN SPEC

### 4.1 Blocking preconditions (all three, before any G2 decode is scored)

1. **I1 publishes a PASS** with its transition relation named, and states which
   mode is primary. If the primary mode is permissive, §3 divides by ~13 and
   this spec must be re-cut.
2. **I2 publishes a PASS** with the register panel and `SWEEPROW` frozen.
   Plumbing is already proven against the current `adjudicate.py` (9,984 rows,
   0 `validate_row` failures) — this precondition is about the *panel's measured
   power*, not the interface.
3. **I3 publishes the null curve** as `max` over `n` trials for **(L, mode,
   statistic)**, covering at minimum `L ∈ {31, 120}`, `mode ∈ {keyskip1,
   skip_by_two, primary-permissive}` and `n` up to 10¹⁰.
   **This is the gate that decides whether the screen tier exists at all.**
   `vecbeam.py --bench` already shows the null max over only 8,192 random
   trials at L=31 is **−5.550**, i.e. the legacy −5.5 bar is *already breached
   by noise at n = 10⁴*. At n = 10⁹ the L=31 null max will be far higher. If it
   exceeds the plant's score at L=31, **the L=31 screen has zero selectivity**
   and Phase 2 must fall back to §4.4.
   Note also that `drift3` and `union0_5` score *random* data at mean −4.51 and
   −4.82. Under a permissive relation the entire score scale moves and no fixed
   bar survives.

### 4.2 G2-GATE-Q1 — the positive control, run before the sweep

`plant.json` is on disk and pre-registered (PREREG §Q1, seed **1389657600**,
reduction `r29`, sign −1, Atbash off, forward, offset 0; foil seed 1389657601).
15 cells: 5 registers × 3 constructions, with realistic desync (6 events / 154
runes under `keyskip`, i.e. 1 per 25.7).

I1/I2/I3 must report, per cell: **score, rune-recovery fraction, and the
true-minus-wrong-seed margin**, at I3's threshold. Round 18 baselines to beat:
L7-A power 0.33 Latin / **0.00** no-vowel English; L7-B −6.90 at 25.8 % recovery
on `skip_by_two`.

**If this control is not run, G2's output is labelled INCONCLUSIVE, not
NEGATIVE** (PREREG §7). Cost: 15 decodes. There is no excuse for skipping it.

### 4.3 Primary plan — build the C screen (recommended)

| step | what | cost |
|---|---|---|
| **C-1** | Port the screen to C: drand48 core + the 9 reductions + I1's primary transition relation at L=31 + I2's panel statistic. `gen_perl.py`'s core is 6 lines of C and `ref_drand48.c` already exists. | engineering |
| **C-2** | **Exactness gate**, modelled on `vecbeam.selftest_exact()`: 200 independent (C, K) pairs at L ∈ {31, 120}, C screen vs the Python reference, scores agreeing to 1e-9 on 200/200. **A C screen that fails this does not run** — same rule that gated the generator. | ~minutes |
| **C-3** | Re-measure C throughput on this box. If below ~15,000/s/core, re-cut the ladder below. | ~minutes |
| **P1** | 2³² × `r29` × 8 orientations × primary mode | **34 h** |
| **P2** | 2³² × `r29` × 8 orientations × the second construction (`skip_by_two`) | 34 h |
| **P3** | 2³² × `r29_nodup`, `r32_rej` × 8 orientations × primary mode | 68 h |
| **P4** | S2 (131,072 small-literal / pid / top-of-range seeds) × **all 9** reductions × 8 orientations × both modes | < 0.1 h |
| **P5** | S1 era band (1.26 × 10⁸) × the remaining 6 reductions × 8 orientations | ~6 h |
| **P6** | escalate every screen row above I3's bar to L=120, then to page 0 full and the 12,956-rune stream (B-04 §5's rule) | ~hours |

P1+P4 alone (≈34 h) delivers **the repository's first complete 2³² enumeration
of a named generator family through a drift-capable, multi-register
instrument.** P1–P5 ≈ 142 h ≈ 6 days delivers the top three reductions complete
plus the era band for the rest.

### 4.4 Fallback plan — Python only, or the L=31 screen has no selectivity

If C is not built, or I3's null curve kills the short-window screen, G2 reduces
to a banded sweep and **must** report it as a fraction:

| priority | cell | decodes | Python hours |
|---:|---|---:|---:|
| F1 | S2 × 9 reductions × 8 orientations × 2 modes | 1.9 × 10⁷ | 1.3 |
| F2 | S0 authoring window × `r29` × 8 orientations | 3.77 × 10⁸ | 26.3 |
| F3 | S1 era band × `r29` × 8 orientations | 1.01 × 10⁹ | 70.5 |
| F4 | S4 stratified uniform sample of the remainder, at whatever N is left | — | — |

F1–F3 ≈ 98 h and yields **2.9 % of the seed space** for one reduction. That is
the *same* seed coverage `round10/L5-seed32` already claimed for this exact
generator. **Its entire value would be power, not coverage** — a repaired
decoder, a nine-register adjudicator and a recalibrated threshold over ground
previously swept at rigid alignment with an English-only scorer. That is a
legitimate thing to buy (doctrine R2: value = coverage × power), but it must be
*sold as that* and not as new coverage.

F4 is the honest one and the weakest: because the auto-seed is uniform on 2³²,
the only meaningful statement about the un-seeded case is
`(seeds swept) / 2³²`, and in the fallback plan that number is single-digit
percent.

### 4.5 Row schema and mandatory statistics

Every scored decode persists I2's full `SWEEPROW` — `en`, the 9-register `z`,
`pmax`/`preg`, `pmax_ne`, `pcon`/`pcreg`, `ioc`, `mds`, `h2`, `zl` — with `kid`
in the form already emitted by the pilot:

```
perl514|<reduction>|seed=<int>|sign=<-1|+1>|atb=<0|1>|dir=<fwd|rev>|off=<int>|L=<int>|mode=<str>
```

Doctrine R3 is CI-enforced. The pilot emitted 9,984 rows with **0**
`validate_row` failures, so this is proven, not hoped.

---

## 5. Kill conditions, carried from PREREG §Q5

* **KILL-1** — generator does not match real Perl. **Did not fire**: gates A/B/C
  all PASS.
* **KILL-2** — at 10 % of the Phase-2 budget, if G2's score distribution is
  indistinguishable from I3's size-matched null **and** the G2-GATE-Q1 control
  shows < 0.90 recovery on `skip_by_two`, stop and report INCONCLUSIVE.
* **KILL-3** — if the primary decoder mode is permissive (≈13× slower), re-cut
  §4.3 rather than silently sampling and calling it the space.

---

## 6. Why the version difference does not matter (the residual uncertainty, stated)

This box runs perl **5.40.1**; the target is **5.14.2**. Rather than assume,
the 5.14.2 tarball was fetched (md5 `3306fbaf976dcebdcd49b2ac0be00eb9`) and read.
`Configure` picks `drand48` unconditionally on any glibc host and sets
`Drand01() = drand48()`, `seedDrand01(x) = srand48((long)x)`, `RANDBITS 48`. So
5.14.2 on Ubuntu **is glibc's drand48**. Validation gate B then measured the
installed perl's `rand()` against a C program calling glibc `srand48`/`drand48`
directly: **13 seeds × 1,024 draws, identical to 17 significant digits, 13/13.**
Since my Python matches 5.40 (gate A) and 5.40 matches glibc (gate B), and 5.14
*is* glibc, my Python matches 5.14.

**The one residual uncertainty**, and it is confined: `pp_srand`'s handling of
a *non-integer argument* changed. 5.14 used `POPu` (plain `SvUV`), so
`srand("CICADA3301")` seeds **0**; 5.40 uses `grok_number` and seeds **UV_MAX**,
and `srand(-1)` seeds **1** rather than `0xFFFFFFFF`. Both rules are implemented
in `gen_perl.srand_arg_to_seed(arg, era=...)` and the divergences are tabulated
in `validation.json` gate C3. **This affects only how a hit is *described*, never
what is *covered*** — every coerced value lands inside 0..2³²−1 and is therefore
inside the enumerated space either way.

---

## 7. One-line summary for the coordinator

> G2's generator is validated byte-exactly against real Perl and against glibc
> drand48; the space is **2³² seeds with no residue — including the un-seeded
> case, which is uniform 32-bit, not unbounded**; Stage A is 3.09 × 10¹¹ decodes;
> Python covers ~0.2 % of it in 72 h, **C covers `r29` × all 8 orientations
> completely in ~34 h**; the screen tier's existence depends entirely on I3's
> null curve at L = 31; and the pre-registered plant is on disk waiting for
> I1/I2/I3 to run G2-GATE-Q1 at a cost of 15 decodes.
