# Round 28 / L4 — unswept generators: RESULTS (NOW phase, build-now-queue-heavy)

**Date:** 2026-09-08 · **Verdict: QUEUED — instruments built and control-validated;
zero sweep coverage claimed; 25 heavy cells frozen in `queued_cells.json` awaiting
R27-S2's cores.** PREREG: `PREREG.md` (two dated amendments, both before any null
counts). Trust anchor `tests/validate.py` 5/5 at close of work.

## What this lane establishes (measured, not asserted)

1. **The P-4 blocker is gone and PHP mt_rand is now swept-ready.** `/usr/bin/php`
   8.5.4 exposes BOTH engine modes; `receipts/genval.json` records |Δ|=0 stream parity
   (8 seeds × 2000 draws × {raw, badscaled, %29}) for the canonical `MT_RAND_MT19937`
   twist AND the pre-7.1 `MT_RAND_PHP` broken twist, and confirms PHP still routes
   `MT_RAND_PHP` ranged calls through `RAND_RANGE_BADSCALING` (measured `===`, per
   seed), so the reference IS the legacy arithmetic. The census's "highest-prior open
   generator" (`round10/L5-seed32/CENSUS.md` §C, `handoff/PARKED.md` P-4) has a
   validated implementation for the first time.
2. **The R19-G3-CORRECTION gen=0 open row is swept-ready under a BEAM decoder.**
   glibc TYPE_3 `random()%29` reproduced |Δ|=0 against the resident glibc, including
   the two facts that would silently have wrecked a naive port: (a) the Schrage seeding
   chain reads the seed as **int32** (the unsigned-long reading was tried and REJECTED
   by probe seeds ≥ 2^31); (b) `rand()` measured **identical** to `random()` on every
   probe seed, so the PREREG's separate "glibc rand()" cell is collapsed (amendment
   A2) — one sweep covers both call paths. glibc's own `seed 0 → 1` means seeds 0 and
   1 coincide (coverage bookkeeping, 2^32−1 distinct streams).
3. **The R27 S3 deferral is discharged**: all 15 reducer×offset cells now have the
   per-cell controls and vectors `R27-CPORT-MT32-FULLSWEEP.not_covered` said they
   lacked.
4. **A hit cannot be missed by construction.** grind28 refuses to sweep any lane whose
   per-cell gate is absent, mismatched, or failing — no override exists (the
   `GRIND27_S2_CONTROL_OK` env-var pattern is retired). Gates are (a) 64 vectors
   (generator |Δ|=0 + decode parity), (b) planted control, (c) false-reject set.

## Control validation (doctrine §4.2: plant, prove recovery, then trust silence)

| check | result |
|---|---|
| gen28 vs /usr/bin/php + resident glibc | |Δ|=0, 8 seeds × 2000 draws, all modes/scalings (`receipts/genval.json`) |
| C engine vs Python reference, 25 cells × 64 vectors | 1600/1600 exact, worst |Δpmax| **0.0** (`--gate-check`, all PASS) |
| planted controls, 25 cells | 25/25 FLAGGED by the C screen at pmax 17.931159 — margin **12.93** over cand bar 5.0, **8.29/7.90** over the pair/exact claim bars; identical value across cells is expected (recovery 1.000 reproduces the same truth text) |
| full-gate (hitfn20 3-clause) on every cell's plant | 25/25 HIT=True, recovery 1.000, held-out 1.000, pmax 25.24 vs bars 9.64/10.03 (`receipts/gates_receipts.json`) |
| false-reject | 200/200 wrong-seed decodes matched ≤1e-9 and below claim (max 4.05) |
| plant through the REAL banded sweep path | plant seed = the ONLY candidate flagged in its 64-seed band, pmax exact (smoke/plant_cands.jsonl) |
| micro-null through the REAL --plan path | 200k seeds of cell #1: 22 candidates ≥5.0 = 1.1e-4/seed, 1.6× Gumbel 6.95e-5 (inside K2 [0.2×,5×]); best 5.91, 3.7 below claim; checkpoint artifacts + resume state all written |
| C↔Python batch parity (stage_a28.py) | 22/22 micro-null candidates, worst |Δ| **0.0** |
| negative controls of the GATE itself | tampered ks value → gate FAIL rc 1; gateless plan lane → REFUSED; lane↔gate mismatch → REFUSED (smoke/) |
| grind27 S1 anchor self-test | PASS bit-exact in grind28 (V1 64/64 worst |Δ| 0.0, V2 exact) |

**Measured instrument-power fact (PREREG amendment A1):** hitfn20's clause 3 (held-out
1/4-fit key-phase attribution) FALSE-REJECTS ~1/8 of TRUE planted keys of this class
(probes: 32 plants across 4 reducers → 2 clause-3 failures at heldout 0.511/0.794 with
recovery 1.000; plus the frozen ladder logged 1 more in 27 evaluations). The stage-A
screen is unaffected (those plants still flag at margin 12.93). Consequence for the
queue: stage-B `hit=False` on a claim-bar crosser is NOT a discard — every crosser is
FLAGGED-FOR-ORACLE and adjudicated (R27 ORACLE-*.md pattern), so clause-3's measured
~0.9 power cannot lose a real key.

## Coverage × power (doctrine R2)

- **Coverage: 0 of every queued cell.** This lane claims NO key-space exclusion. The
  25 × 2^32 cells are frozen with per-cell bars (pair 9.638182362052774 / exact
  10.031081507059358 at N=2^32, family count 25 disclosed) and calibrated ETAs
  (QUEUE.md); coverage will be claimed only as each cell completes, by the sweep's own
  STATUS.json + histogram accounting (R3 stats: per-worker 0.01-bin pmax histograms +
  top-1024 + append-only candidates, identical to R27's discharged S1 machinery).
- **Power (screen, the thing that gates the sweep): plant margin 12.93 over the
  candidate bar** on every cell — the screen provably cannot reject a true seed of the
  planted construction/register class. Power (full stage-B gate): ~0.9 on true keys
  (clause-3 measurement above), mitigated to ≈1 by mandatory oracle adjudication of
  all crossers.

## The three conditionals every eventual negative will carry (doctrine Q4)

1. **Key space:** that cell's single-word 32-bit seed space at its stated offset(s) —
   not multi-word keys, not mid-stream states, not other scalings/reductions, not
   time-seeded 64-bit values. PHP cells: `mt_srand(w)` exactly; glibc cells:
   `srandom(w)` under the resident (int32-chain) semantics — an ILP32-`long` 2012
   libc variant would differ for seeds ≥ 2^31 IF such a libc read the seed through
   `long` (named, unmeasured).
2. **Transition model:** keyskip1 ("exact") / keyskip2 ("pair") representability only —
   the same two relations R27 swept; constructions outside them (R18 L7-B's lesson)
   are not excluded.
3. **Adjudicator register:** the I2 9-register panel + English quadgrams; a pad whose
   plaintext lives outside that register axis is not excluded (R18 L7-A's lesson).

## Anti-repeat proof (LEDGER coverage fields, not statuses)

- `R19-G3-CORRECTION.not_covered[0]`: gen=0 full-2^32 absent → cells 9–10 are exactly
  that row, upgraded from the rigid decoder (which scored the CORRECT key at −6.835 vs
  beam −4.170, round12/D3) to the control-validated beam.
- `handoff/PARKED.md` P-4 + CENSUS §C: PHP "implemented nowhere / could not pass the
  harness gate" → cells 1–8; the harness gate now exists and PASSes.
- `R27-CPORT-MT32-FULLSWEEP.not_covered` "S3 cells deferred: no per-cell
  controls/vectors" → cells 11–25 build precisely those.
- No overlap with: R12-A1-era `sweep.c` gens 1–9 (different construction: PHP outputs
  temper>>1 with its own scalings ≠ gen-5 reference MT; and those rows were
  rigid-decoder anyway), R21-L3 (string-seed dictionary, offset 0, exact only),
  R27 S1/S2 (random29 only), R24-C2 (prior-dense slices).

## Files

`grind28.c` (engine) · `gen28.py` (validated generators) · `ref_php.php` /
`ref_glibc.c` (on-box references) · `make_gates.py` (gate builder) · `stage_a28.py`
(K4 batch parity) · `gates/` (25 regenerable gate files) · `receipts/` (genval,
gates_receipts incl. plant-ladder disclosure, calibration bench) ·
`queued_cells.json` (the frozen queue) · QUEUE.md · BUILD.md · smoke/ (negative
controls + micro-null run).

## Reopens / supersedes nothing; extends

This lane publishes no negative and forecloses nothing. When queued cells complete,
their rows extend (not replace) R19-G3-CORRECTION, P-4 and R27's ledger entries; the
CENSUS §C residue below PHP/glibc (.NET, ISAAC, LFSR, …) and the /dev/urandom branch
(CENSUS §E) are untouched by construction.
