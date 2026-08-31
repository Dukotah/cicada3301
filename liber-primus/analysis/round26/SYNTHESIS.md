# Round 26 — SYNTHESIS: the un-run lanes + the semantic seed

_Closed 2026-08-31. Trust anchor `python3 tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)**
before and after. `validate_ledger.py` **Unsound negatives = 0** before and after. Ledger
**152 → 156** entries (R26-A/B/C/D). No git commit (WSL has no creds; the owner commits from
Windows)._

## The question this round asked

Round 25 parked the one runnable *compute* branch (the Py2.7-MT 2³² tail, 0.50% swept). This
round did not restart that grind. It aimed instead at the **instruments that were built and
control-validated in earlier rounds but never actually released a sweep**, plus the one honest
reframe left with non-negligible odds. Every lane answered the five Aiming-Test questions in its
`PREREG.md`, cited the ledger id it extends and proved non-duplication against `coverage`/
`not_covered` (never bare `status`), and passed a **plant-and-recover control (≥0.90 recovery,
HIT=True) before its null was allowed to count.**

Standing verdict being tested (not re-derived): **LP2 0–54 is OTP-class** — from the ciphertext
alone a true external pad is indistinguishable from a short-seed keystream. Only two things move
it: an external key surfacing, or brute-forcing the finite derived-key branch. Every lane below
aims at the derived-key branch or at an un-run instrument. **Expected outcome: HARDEN.**

## Per-lane result — coverage × power

| Lane | What it fired | Control | Coverage | Best score vs bar | Result |
|---|---|---|---|---|---|
| **A** | Perl `rand` (R19-G2, was **0 seeds**), TeX RNG (G4-TEX, was **0 decodes**), Py2.7 reducers on the **distinct** amd64-w64 / non-zero-offset / `keyskip2` axis R21-L3 left open | 1.000/HIT per generator (Perl r29, TeX pgf_rnd29, Py2.7 grb5_mod-w64) | 347 corpus prior-dense seeds swept FIRST (COMPLETE, empty) + dense-from-0 baseline; ~747/2³² = 1.74e-7 per space × {keyskip1,keyskip2}; 8 Perl + 4 TeX + 3 Py2.7 axes | best pmax **5.438** vs 7.63/7.38 | **partially-run** (interim; 0 clears, 0 flags) |
| **B** | R12-C2's fetched-but-never-run **33-keytext running-key** sweep, **skip-aware** (rigid was already doublet-excluded) | 1.000 both presets (keyskip1 + keyskip2) | 33 texts × {keyskip1,keyskip2}; 3 of 9 pages COMPLETE at 4 offsets/text (page 23 → 86%); large pages capped into `not_covered`; 1,562 decodes | best pmax **5.470** vs 5.732 | **partially-run** (0/1,562 clears, 0 flags) |
| **C** | **Semantic-seed** enumeration: 323 corpus values AS SEEDS through a 7-generator zoo incl. the page-05 totient/prime ladder | min recovery **0.9917** across all 7 generators (keyskip2 required; plain beam ~0.26 on skip_by_two) | 323 seeds × 7 generators × 2 decoders = **4,274 rows = 100%** of the enumerated set at offset 0; ~0% of raw 2³² (out of scope by design) | best screen **−6.578** vs 5.0 (gap >11.5) | **negative** (0 escalated, 0 flags) |
| **D** | Red-team, refute-by-default, over A/B/C | — | recomputed all three coverage×power from raw rows | — | **NO-ERROR-FOUND** |

## What was genuinely un-run (the anti-repeat proofs, in one line each)

- **A / R19-G2 (Perl):** ledger recorded "ZERO key-space coverage… swept no seeds." First-ever
  scored decodes. **A / G4-TEX:** ledger recorded "ZERO decodes." First-ever scored decodes.
  **A / R21-L3:** swept i386 `wordsize=32` only; A covers the **distinct** `wordsize=64` amd64
  2-word `init_by_array`, non-zero offsets {1,3,5,7,13}, and the `keyskip2` relation — verified
  `py27` w64 keystream ≠ w32 for string seeds. A does **not** touch `random29`, so the R25
  compute-tail offset-0 tail is uncollided.
- **B / R12-C2:** ledger recorded "Texts fetched (29 files ~12 MB); the sweep was never run"
  (`not_covered: None`). First execution. Distinct from R12-A1 (byte-reduction pads into the
  **rigid** stream, not letters-only running keys into the **skip-aware** decoder); also consumes
  the "sha256_ctr keytexts" item R24-C2-EXT left open.
- **C:** R11 tested corpus numbers as **data/feedback channels**; R16-PRNG tested **raw MT
  seeds**; R21-L3/R25 swept **raw `init_by_array` word-integers**. C's composition — a
  **corpus-semantic value AS the SEED** of a generator zoo (including the page-56 ladder) under
  the **repaired skip-aware + panel-max** instrument — appears nowhere prior. Proven not-covered.

## The one lane with live odds, and why it still hardened

Lane C was the only reframe this round with non-negligible prior: *Cicada built a **puzzle** —
every prior stage was solvable by design, so if 0–54 uses a derived key the seed was meant to be
**discovered**, hence **semantic**, not `/dev/urandom`.* That is a real argument, and it was
tested at 100% coverage of a bounded, enumerable candidate set — including the exact generator
(the totient/prime ladder) that already reproduces a solved page. It returned flat-random noise
for every one of 323 semantic seeds across 7 generators. The reframe is sound; the seed set it
implies is simply not the pad. **This is the honest way the lane could have surprised us and did
not.**

## Red-team (Lane D) — NO-ERROR-FOUND, with two MINOR non-fatal defects

Independently reproduced every coverage×power number from the raw ledger/sweep rows (A best pmax
5.438; B 5.470 vs 5.732; C best screen −6.578), re-derived C's control from scratch (correct seed
rec 1.000/HIT vs wrong seed 9999 rec 0.054/no-HIT = discriminating). Confirmed: **no silent
re-run** of any existing negative; **no sieve × panel-max FP-inflation** (the ~2.5e6 R20 hazard —
all lanes used the N-scaled `panelmax20` family-wise bar, never a fixed bar at large N); **every
"closed" claim is an explicit swept-fraction statement** (doctrine R7).

Two MINOR, non-blocking defects (neither reproduces a negative nor changes a verdict):
1. **Lane A PREREG-vs-code hygiene:** A's `sweep.py` runs 228 `py27` int-seed rows at
   offset-0/`keyskip1`/`wordsize=64`, which for **int** seeds is byte-identical to `wordsize=32`
   — contradicting A's PREREG promise to skip that cell to avoid R21-L3 overlap. But those seeds
   are semantic ints (`int_motif`/`int_prime`), **not** R21-L3's `init_by_array` P3b words, so no
   existing negative is actually reproduced; the result is unchanged (0 clears). Scope-hygiene
   only. Suggested guard recorded in the ledger `not_covered`.
2. **Lane A interim null:** A's dense-from-0 baseline sweep was still running at close-out
   (`control.json` finalize block had not executed). A's headline coverage (747 seeds / 49,302
   planned decodes) is the **plan**; the delivered null is **partial**. A discloses this honestly,
   so it is not a false claim — but its ledger row is recorded **partially-run** to reflect it.
   The 0-clears / 0-hits result holds across every row scored so far (>7,000 at close-out).

## Loose thread

Lane A's dense-from-0 baseline sweep (`analysis/round26/A/sweep.py`) continues in the background;
it only extends the same flat-prior null and writes `control.json`'s finalize fields on
completion. It requires no supervision and cannot change the verdict — the informative
**prior-dense front is already complete and empty.** A future reader may read the finalized
`control.json` for the completed baseline number; the ledger row already states the swept fraction
and puts the remainder in `not_covered`.

## Bottom line (honest, one paragraph)

Round 26 **hardened** the OTP-class verdict for LP2 0–54 along **three previously un-swept
instrument axes** — the first-ever Perl and TeX generator decodes, the distinct
amd64-w64/offset/`keyskip2` Py2.7 slice, the staged R12-C2 keytexts, and the semantic-seed
reframe — **without moving the needle toward a solve.** Every null issues from a ≥0.90-validated
instrument, so each is a real negative, not an unmeasured-instrument artifact. **0 certified hits,
0 flagged-for-oracle survivors, no stop-and-alert.** The prior mass still sits on "external or
unseeded pad, no recoverable key"; the two doors that remain are unchanged (an external key/page
surfacing, or a GPU/C brute-force of the finite derived-key tail). Bounds, not verdicts: the flat
2³²/2⁶⁴ generator tails and the large capped keytext pages are explicitly **not** covered and
**not** claimed closed.
