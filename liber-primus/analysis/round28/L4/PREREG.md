# L4 — unswept-generators: grind28 for PHP mt_rand, glibc, and the R27 S3 cells

_Round 28, pre-registered 2026-09-08. Mode: **build-now-queue-heavy** — vectors, planted
controls and null micro-runs NOW (nice -15, single-thread; builds may burst <1 min
multi-thread); every full 2³²-class sweep is QUEUED in `L4/QUEUE.md` and runs only after
S2 (`grind27`, PID in `../../round27/sweep.pid`) has exited AND its closeout (batch parity +
S2 planted control) is done. **grind27's sources and `P1-engine/run/` are not touched** —
grind28 is a separate copy-derived binary in this directory._

## Hypothesis

The pad is a keystream from a period-appropriate generator the ledger records as never
swept: PHP `mt_rand` (canonical MT19937 mode AND the documented pre-7.1 `MT_RAND_PHP`
broken variant, each with PHP's `RAND_RANGE` scaling), glibc `rand`/`random` (including the
`gen=0` full-2³² row that never ran), or a Py2.7 reducer×offset cell R27 deferred.

## Cell census (each cell = generator × reducer/scaling × relation × offset, own control)

| cell | source of "never swept" | reference for vectors |
|---|---|---|
| PHP mt_rand canonical, →[0,28] via RAND_RANGE + mod29 | `handoff/PARKED.md` P-4 / `round10/L5-seed32/CENSUS.md` §C: "unreachable from the swept generator 5"; highest-prior open generator | `/usr/bin/php` 8.5.4 (**on the box** — the P-4 "no php binary" blocker has evaporated), `mt_srand($s, MT_RAND_MT19937)` |
| PHP mt_rand broken variant | same; the `MT_RAND_PHP` bug is a *documented deviation* | `/usr/bin/php` `mt_srand($s, MT_RAND_PHP)` — verified at planning time to emit a distinct stream |
| glibc `random()` (TYPE_3 additive) — the **gen=0 open row** | `R19-G3-CORRECTION` `not_covered[0]`: "gen=0 over the full 0..2³² — still absent, still the one open row"; old partial rows were also **rigid-decoder** (same entry) | local glibc via a C reference harness (`srandom`/`random`), 5 seeds × 2000 draws exact |
| glibc `rand()` | same family; distinct call path | local glibc `srand`/`rand` |
| R27-S3 cells: Py2.7 `grb5_mod`/`grb5_rej`/`shuffle29` × offsets {1,3,5,7,13} × pair | `R27-CPORT-MT32-FULLSWEEP` `not_covered`: "S3 cells … deferred: no per-cell controls/vectors built" — L4 builds exactly those controls | `../../round19/G3/gen_py27.py` (R21-L3-validated) as the Python reference for C vectors |

**Dropped with citation:** the tasking's "wordsize-64" S3 cell — `../../round27/PREREG.md`
S3: "wordsize is a no-op for int seeds (it only enters string hashing) … noted so nobody
sweeps it twice." Its live content is L3's string path. Recorded here so it is not
rediscovered.

## Anti-repeat

`R19-G3`/`R19-G3-CORRECTION` (glibc rows partial + rigid-only), `R12-A1`-era `sweep.c`
generator 5 (reference MT19937 ≠ either PHP mode by documented construction),
`R21-L3-PY27-REDUCERS` (reducers at offset 0 / keyskip1 only; offsets {1,3,5,7,13} × pair
uncovered), `R24-C2-EXT` (prior-dense slices only), `R27` S1/S2 (random29 only). No cell
above duplicates any `coverage` field; each extends a named `not_covered` line.

## Aiming Test

**Q1 — Hit shape + recognizer.** A 32-bit seed whose generator stream, reduced to mod-29
symbols, decodes LP2 under pair/exact. Recognizer: the proven grind27 architecture — C
stage-A screen with claim bar, candidates.jsonl, Python stage-B batch parity (K4: any
|C−Python| pmax disagreement >1e-6 voids the lane), hitfn20 + adjudicate.py. **Per-cell
gates before any null counts:** (a) **vectors** — grind28's generator must reproduce the
reference (php binary / C-glibc harness / gen_py27) exactly, 64-vector file per cell,
|Δ|=0; (b) **planted control** — encipher a plant with that cell's true keystream, require
the C screen to flag it with the S1-class margin and stage-B HIT=True; (c) false-reject
micro-run (≥6 wrong-seed plants, 0 flags above claim bar).

**Q2 — Measured fact above flat prior.** PHP: `CENSUS.md` §C names it the census's
highest-prior open generator for a 2013 web-hosted puzzle, with a documented
implementation deviation making it unreachable from anything swept. glibc: the R18-L1
toolchain measurement (Ubuntu 11.04–12.04 box) makes glibc the resident libc of the
measured authoring environment, and gen=0 was *first in Round 8's own priority order* yet
is the one row with no result. S3 cells: labelled honestly — **completeness rituals**
("same interpreter, different idiom", per R27 PREREG); they queue last, per doctrine Q2.

**Q3 — Bounded?** Enumerable: each cell is exactly 2³² seeds. Measured S1 throughput
(grind27, 6 cores) completed 2³² in days; queued estimates per cell go in `QUEUE.md` after
a 60-s calibration micro-run. NOW-phase compute (vectors + controls + nulls) is minutes per
cell at nice-15 single-thread. Queue order (highest prior first): PHP-canonical,
PHP-broken, glibc-random (gen=0), glibc-rand, then the 15 S3 completeness cells.

**Q4 — Three conditionals of every cell's negative:**
1. key space: that cell's 2³² seed space at its stated offsets — not multi-word keys,
   not mid-stream states, not other scalings;
2. transition model: keyskip1/keyskip2 representability only;
3. register: the I2 9-panel + English quadgrams.

**Q5 — Kill conditions.** (a) A generator that cannot reproduce its reference exactly does
NOT sweep — an unvalidated generator cannot produce a trustworthy null (Round 8's own
standard). (b) If PHP 8.5's `MT_RAND_PHP` mode is shown to differ from the *actual* pre-7.1
behaviour (checked against the documented algorithm), the broken-variant cell is built
from the published pre-7.1 source algorithm instead and the vector source is disclosed.
(c) If S2 has not exited by round close, the queue ships as build-receipts + QUEUE.md —
that IS the deliverable for the heavy half; no partial "sneaked" multi-core runs.

## Amendments (dated, before any null counts)

**2026-09-08 — A1, plant-seed ladder + measured clause-3 power.** While building the
Q1(b) controls (before any sweep or null count), the full-gate stage-B was measured to
FALSE-REJECT ~1/8 of TRUE planted keys via hitfn20 clause 3 (held-out 1/4-fit key-phase
attribution desyncs on some plants: e.g. php_mt_scale seed 777 → recovery 1.000 but
held-out 0.511; php_php_scale seed 90210 → 0.794; 30/32 probe plants pass). This is an
instrument-power fact of the ADJUDICATOR, not the screen — every affected plant still
screens at pmax ≈ 25 with recovery 1.000. Deviations adopted: (i) each cell's planted
control uses the FIRST seed from the frozen ladder [777, 778, 1001, 20260908, 555,
31337, 90210, 424242] whose full gate passes (HIT=True, recovery ≥ 0.999); every tried
seed and its verdict is recorded in `receipts/gates_receipts.json` — no silent
selection. (ii) The measured clause-3 false-reject rate is reported in RESULTS.md as
part of this lane's power statement. A hit still cannot be missed: the sweep flags
every claim-bar crosser FLAGGED-FOR-ORACLE regardless of any stage-B clause (R27 flow).

**2026-09-08 — A2, cell-list concretisation.** (i) "RAND_RANGE + mod29" is implemented
as BOTH scalings per PHP twist (4 PHP generator-reducers), each under BOTH relations
(pair/exact) per Q1 — 8 PHP cells + 2 glibc cells + 15 S3 cells = 25. (ii) The
"glibc rand()" cell is COLLAPSED into glibc random(): measured `rand_equals_random:
true` on all probe seeds against the resident glibc (`receipts/genval.json`) — in
glibc, `rand()` calls `__random()`; one sweep covers both call paths. (iii) glibc
seeding follows the measured int32 Schrage-chain semantics (the unsigned-long reading
was tried and rejected by the same probes); seeds 0 and 1 collide by glibc's own
`if (seed == 0) seed = 1`.

## Bars

Per-cell claim bar from `panelmax_bar(relation, N=2³² pre-registered ceiling…)` — computed
and frozen in each cell's QUEUE.md entry before its sweep starts (note: adding cells raises
family-wise N; each cell's bar is stated at its own N with the family count disclosed, per
P-4's "recompute — do not reuse −12.0602 at a different N", transposed to the panel-max
machinery). SWEEPROW/3 stats + per-worker pmax histogram persisted (doctrine R3).
Survivors FLAGGED-FOR-ORACLE, never auto-certified.

## Coverage promise (honest)

NOW phase delivers: grind28 binary + BUILD.md, per-cell vector files, planted-control and
false-reject receipts, calibration throughput, frozen bars — i.e. everything needed so the
queued sweeps are turn-key and *cannot miss a hit* when cores free up. Sweep coverage is
claimed only as each queued cell completes; un-run cells are listed un-run. The
/dev/urandom branch (CENSUS §E) is untouched by construction and stated so.
