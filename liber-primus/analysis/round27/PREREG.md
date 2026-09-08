# Round 27 — PREREG: C-engine exhaustion of the Py2.7-MT 2^32 derived-key branch

**Date:** 2026-09-07. **Lane P0 authored this before any C code exists.** Binding under
`ARMADA-DOCTRINE.md`. Trust anchor `tests/validate.py` = ALL VALIDATIONS PASSED (5/5) on
2026-09-07. Companion artifacts: `round27/P0-spec/SPEC.md` (the port spec),
`round27/P0-spec/vectors.json` (64-seed reference vectors + planted controls, generated
by `round27/P0-spec/make_vectors.py` from the R25 pipeline verbatim).

**Hypothesis.** The LP2 0–54 pad was derived by a Python-2.7 script as
`random.seed(w); [int(random.random()*29) ...]` for some 32-bit `w`, applied under a
rejection-loop encipherment whose observable trace is the `skip_by_two` relation.
R25 covered 0.5015% of the seed space (21,539,647 words, 0 hits, best pmax 6.826 vs
claim bar 7.384). Round 27 finishes the space in C.

---

## The five Aiming-Test answers

### Q1 — What would a hit look like, and would THIS instrument recognise it?

A hit is a seed whose keystream, decoded through the keyskip2 beam, yields plaintext that
(1) clears the pair panel-max null bar 7.383520294328688 at N=1e6, α=0.01, (2) recovers
≥0.90 of runes, (3) reproduces ≥0.90 on the held-out 3/4 (hitfn20 3-clause). **Planted
and proven, in the actual shape, before this prereg:**

- Full-gate plant (seed 777, skip_by_two supp=0.83, held-out English): recovery 1.000,
  heldout 1.000, pmax 25.239 ≥ 7.384 → **HIT=True**
  (`runner.planted_seed_selftest`, frozen in `vectors.json["planted_selftest"]`).
- Screen-level plant (the new C filter's shape): the same construct's first 120 runes
  through the exact stage-A config score **pmax 17.931** vs candidate bar **5.0** —
  margin 12.9 (`vectors.json["planted_stage_a"]`). The screen is provably incapable of
  rejecting a true seed of this construction/register class.
- The C engine may not contribute a single null until it passes acceptance gates V1–V4
  (SPEC §8): 64-seed exact parity, planted-screen reproduction, the 2149309687 →
  6.825835461843649 end-to-end drill, and candidate-path liveness. The R18
  "broken magnet" is excluded structurally: the C engine's ONLY filter is a candidate
  bar 2.38 below the claim bar, and Python re-adjudicates every flag.

### Q2 — What measured fact raises this family's prior above the flat rate?

`analysis/round18/L1-toolchain/RESULTS.md` §6: the author's toolchain is a dated
Ubuntu 11.04–12.04 box (GnuPG 1.4.11 era), which **promotes Python 2.7** (with Perl 5.14,
bash `$RANDOM`, LaTeX LCGs) and demotes modern stacks. Supporting facts:
`round19/G3/gen_py27.py` (V5, measured on real CPython 2.7.3): `randrange(29) ==
randint(0,28) == choice(range(29)) == int(random()*29)` in 2.7, so the `random29` reducer
covers all four era-idiomatic spellings at once; and `round18/L7-redteam/RESULTS.md` §B:
the `pair` relation is the one that reproduces LP2's observed doublet rate and that the
legacy decoder provably missed. This is the **only internally-runnable verdict-changer**
left after 26 rounds. (Honest caveat: it is still a low-absolute-prior lane — the
standing verdict is OTP-class — but it is finite, and finishing it converts "probably not
a cheap seeded PRNG" into a measured exhaustion.)

### Q3 — Is the space bounded, and by what?

**ENUMERABLE. Exactly 2^32 = 4,294,967,296 words per (reducer, relation, offset) cell**,
bounded by the width of a single `init_by_array` key word (= `random.seed(w)` for any
32-bit int). S1 is one cell, swept to 100% — coverage 1.0 by construction, no sampling.

### Q4 — The three conditionals every null in this round will carry

Each sweep's negative is conditional on exactly these, and the RESULTS must restate them:

1. **Key space:** Py2.7/mt19937ar `init_by_array([w])`, w ∈ [0, 2^32), reducer
   `random29` (S1/S2'), key offset o=0 (S1/S2'). NOT covered: multi-word keys, string
   seeds (hash path — swept separately in R19–R24 dictionaries), jumpahead states, other
   generators (bash/perl/tex — R24 C2-ext closed only prior-dense slices), /dev/urandom.
2. **Decoder transition model:** driftbeam `keyskip2` "pair" (exact for the skip_by_two
   rejection loop; screen beam_w=64 at L=120, gate beam_w=400 at L=240). NOT covered:
   constructions outside keyskip1/keyskip2/permissive-drift representability.
3. **Adjudicator register:** the I2 9-register trigram panel-max (EN_MODERN, EN_KJV,
   LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL; EN_NOVOWEL detection-only),
   bar = panel-max Gumbel cell `I19:driftbeam.pair+I2|pmax|L120` at the swept-N. A
   plaintext outside those nine registers can still be missed (L7-A generalises).

### Q5 — Kill conditions at ≤10% of budget

- **K1 (before launch):** any V1–V4 acceptance failure, or C throughput < 2,000
  seeds/s/core after profiling ⇒ stop, fix or re-plan; no sweep.
- **K2 (at 1% coverage ≈ 43M seeds):** candidate rate outside [0.2×, 5×] the Gumbel
  prediction 6.95e−5/seed ⇒ instrument drift; halt and audit before continuing.
- **K3 (at every restart):** `--self-test` (planted seed) must print recovery 1.000 /
  HIT=True; failure ⇒ halt everything (broken scan, not a null).
- **K4 (standing):** any disagreement between a C-flagged pmax and Python's re-score
  > 1e−6 on the same seed ⇒ halt; the parity assumption is void.

---

## Sweep plan

### S1 — the exact R25 configuration, FULL 2^32, restart from 0  [primary]

Generator `init_by_array([w])` + reducer `random29`, offset 0; decode = pair/keyskip2,
L=120, beam_w=64, sign=−1; score = panel pmax at n=120; candidate bar 5.0; Python
stage_b (pair, N=1e6, claim bar **7.383520294328688**) on every candidate; hitfn20
3-clause gate; survivors FLAGGED-FOR-ORACLE only.

**Cursor policy — restart from 0, drop the R25 exclusion set.** Re-covering R25's
0.5015% (21.5M words) plus the 245,975-word excluded baseline costs ~10–20 minutes at the
C engine's target rate; merging 6 parked worker cursors + chunk-1 cursor + the scattered
45,975-word exclusion set is bookkeeping that has produced double-count/gap bugs before
and saves nothing material. A clean [0, 2^32) cursor makes coverage arithmetic exact and
the "no seed was ever skipped" claim trivially auditable. (R25's parked checkpoints stay
untouched as the historical record.)

N for the bar: report the final null against `panelmax_bar("pair", N_adjudicated, 0.01)`
with N_adjudicated = the count of stage_b adjudications actually run (expected ~3e5);
the 1e6 figure (bar 7.3835) is the pre-registered ceiling and is what stage_b hard-codes
— conservative, since bar(N) grows with N.

**Null it buys:** "no 32-bit Py2.7 int seed, under random29 → skip_by_two at offset 0,
yields ≥0.90-recovering plaintext in the 9-register panel" — coverage 1.0 of the cell,
screen power measured at plant-margin 12.9.

### S2 — second construction cell over the same space  [after S1]

**Correction to the tasking note:** the R25 config (S1) already IS the keyskip2/'pair'
relation — R25 froze `PRESET="pair"` (runner.py line 46), identical to R24-C2, bar 7.384.
A separate "S2 = pair" would be S1 re-run. The real second construction axis is the
**keyskip1 'exact' relation** (exact for the one-draw rejection loop), same 2^32 space,
same reducer/offset, bar from its own cell: `panelmax_bar("exact", 1e6, 0.01) =
7.6341931878728095` (`I19:vecbeam.keyskip1+I2|pmax|L120`). Cheap: the C beam is the same
code with `pair=false, max_skip=3`. Requires its own planted control (encipher_keyskip
plant, not skip_by_two) and its own V1-style vector file before it runs.

### S3 — stretch, only if S1+S2 finish inside budget  [completeness ritual, labelled]

Reducers `grb5_mod` / `grb5_rej` / `shuffle29` (Py2.7 spellings, `gen_py27.REDUCERS`) ×
offsets o ∈ {1, 3, 5, 7, 13} × the pair relation; `wordsize` is a no-op for int seeds
(it only enters string hashing) so it adds no cells — noted so nobody sweeps it twice.
Each cell is another full 2^32; run cells in the doctrine's queue-last slot, each with
its own prereg addendum, planted control and vector set. These have no Q2 fact beyond
"same interpreter, different idiom" — they are completeness rituals and are labelled as
such.

---

## Instrument / power statement (doctrine R2)

Value = coverage × power, reported as: coverage = swept-words / 2^32 per cell (S1 target
1.0); power = the planted-control margins above (screen plant pmax 17.93 vs bar 5.0;
full-gate plant HIT=True at recovery 1.000), valid for the construction/register classes
named in Q4 and for nothing else. R3 compliance: every adjudicated candidate gets a full
SWEEPROW/3 row (all four language-agnostic statistics); sub-candidate mass is summarised
by the per-worker 0.01-bin pmax histogram + top-1024 list (SPEC §6) so the null remains
re-interpretable without storing 4.3e9 rows.

## Threshold freeze

Candidate bar 5.0, claim bar formula and cell constants, recovery bar 0.90, held-out
fraction 0.25, α=0.01 — frozen as of this document. Changes require a dated addendum with
reasons, per doctrine §4.1. Any bar-clearing survivor is **FLAGGED-FOR-ORACLE, never
auto-certified** (R21-L1).
