# Round 26 — Lane A PREREG: fire the built-but-never-swept derived-key generators

Prior: LOW. This lane HARDENS the derived-key branch. A hit is a solve.

Target instruments (built + control-validated in R19, but never released a sweep):
- Perl `rand` reductions — `analysis/round19/G2/gen_perl.make_ks(red, seed, nsym)`
- TeX RNGs — `analysis/round19/G4/gen_tex.make_ks(gen, seed, nsym)`
- Py2.7 reducers — `analysis/round19/G3/gen_py27.keystream(seed, mode, n, wordsize, jump)`

Decoder: repo skip-aware beam via `driftbeam.beam_decode`, presets `exact` (=keyskip1, the
repo relation) AND `pair` (=keyskip2, skip_by_two-exact). Certifier: `hitfn20` (panel-max bar +
recovery>=0.90 + held-out 3/4). Real LP2 target: unsolved page index 19 ('23.jpg,24.jpg', 333
runes), squarely in the 0-54 OTP-class band.

---

## Q1 — What would a hit look like, and would THIS instrument recognise it? (plant + prove recovery)

A hit = some (generator, reduction/mode, seed, offset, wordsize) produces a keystream K such
that K applied to the real LP2 page decrypts to a natural-language panel register (LP1/EN/LA/
OE/DE/CY) clearing the panel-max bar, with recovery>=0.90 and held-out 3/4 reproduction.

Recognition proof: for EACH of the three generators I plant a keystream FROM THAT EXACT
GENERATOR (its own make_ks/keystream), encipher a held-out English plaintext (self_reliance.txt,
L=240) under the repo's keyskip1 encipher relation, and drive it through hitfn20 with
`truth_idx` set. The gate must return HIT=True (recovery>=0.90) on the plant BEFORE that
generator's sweep null counts. Control harness mirrors round24/C2-skip-by-two/control.py
(sha256_ctr replaced by the generator-under-test as the key source; RECOVERY_BAR=0.90).

## Q2 — What measured fact raises this family's prior above flat? (cite a file path)

The generators are byte-exact validated against real interpreters and carry validated positive
controls, but ZERO of their seed space has ever been scored:
- `LEDGER.json` R19-G2 coverage: *"ZERO key-space coverage. This lane swept no seeds and
  excludes nothing."* (Perl — a byte-exact 9-reduction generator, unswept.)
- `LEDGER.json` G4-TEX-RNG coverage: *"ZERO decodes of coverage ... four byte-exact generators
  ... HOLDS at the scoring boundary."* (TeX — unswept.)
- `LEDGER.json` R21-L3-PY27-REDUCERS coverage: measured positive-control recovery **1.000**
  strict rank-1 at pmax 28.268 (~20 units over bar) on LP1_REAL/EN register for all four
  configs — POWER ~1.0 on win-condition registers. That measured power is the fact: the
  instrument certifies these keystreams at ~1.0 where they exist; only the seed space is unswept.
The prior is LOW (a derived key is one narrow branch) but the instrument power is HIGH and
demonstrated, so a bounded prior-dense slice is worth firing.

## Q3 — Is the space bounded? (size + enumerable/samplable + fraction covered)

Bounded and enumerable per axis. Full seed space is 2^32 (Perl/TeX int seeds) or 2^64 (Py2.7
amd64 2-word hash image) — NOT fully enumerated here. This lane covers a BOUNDED prior-dense
slice: a curated corpus-derived seed dictionary D (Cicada motifs, primes, 3301, dates, gematria
of solved-LP words, era-plausible literals) crossed with all reductions/modes and a small
non-zero offset ladder, PLUS a small stated dense-from-0 baseline. Reported as explicit swept
counts and fraction of each 2^32 space. No axis is claimed "closed".

## Q4 — The three conditionals my negative carries

- **Key-space swept**: only seed-dictionary D (prior-dense) + offset ladder {0,1,2,3,5,7,13} +
  wordsize {32,64} + a small dense-from-0 baseline. The flat-prior tail of 2^32/2^64 is NOT swept.
- **Decoder transition model**: keyskip1 (repo relation) AND keyskip2 (pair/skip_by_two). Other
  relations (non-keyskip, permissive drift) NOT swept here.
- **Adjudicator register**: hitfn20 I2 9-panel (LP1_REAL/EN/LA/OE/DE/CY/...); EN_NOVOWEL is
  detection-only (power 0.70<gate). Registers outside the panel NOT covered.

## Q5 — The single observation that kills this lane at 10% budget (checkpoint)

CHECKPOINT (after prior-dense dictionary D swept through all three generators, keyskip1, offset
0, both wordsizes): if the max pmax over ALL survivors is below the panel-max bar by a margin
larger than the control's over-bar headroom (i.e. no decode even approaches the bar), the
prior-dense front is empty and the flat tail has no elevated prior — the lane is a clean
bounded negative and the remaining dense-from-0 baseline is a formality. Record max-pmax,
best register, and the count that cleared the bar (expected 0).

---

## ANTI-REPEAT PROOF (ledger ids EXTENDED, and why not covered)

I EXTEND three ledger entries and prove my composition is new:

1. **R19-G2** (Perl). Its coverage is literally *"ZERO key-space coverage ... swept no seeds."*
   Any scored Perl seed extends it. not_covered lists re-seeding and unknown-offset (unbounded)
   — I do NOT touch those; I sweep single-srand int/string seeds only. NEW: first Perl seeds ever
   scored through the decoder.

2. **G4-TEX-RNG** (TeX). Coverage *"ZERO decodes."* not_covered = *"Everything ... the whole
   1.85e11-decode space."* Any scored TeX seed extends it. NEW: first TeX seeds ever scored.

3. **R21-L3-PY27-REDUCERS** (Py2.7). Covered: i386 **1-word** init_by_array map for
   grb5_mod/grb5_rej/shuffle29 (884k words, keyskip1 only) + amd64 folded-1-word for random29.
   Its not_covered is explicit:
   - **NC-2**: *"the amd64 2-word map beyond the folded w->(lo,hi) image ... Reopens if the amd64
     seed dictionary is extended or the 2^64 image is sampled."* — I sweep **wordsize=64 string
     seeds** for grb5_mod/grb5_rej/shuffle29, which take the genuine 2-word init_by_array path
     (verified: w64 keystream != w32 keystream for every string seed). This is the amd64 2-word
     map for the three reducers that NC-2 leaves open — proven distinct from the i386 slice.
   - **NC-4**: *"decoder relations other than keyskip1 ... Reopens if a relation-axis lane plants
     and measures."* — I additionally run **keyskip2 (pair)** on the reducers, planted+measured.
   - Non-zero keystream **offsets** (jump ladder) — R21-L3 swept offset-0 only; I add {1,2,3,5,7,13}.
   I do NOT redo the i386 offset-0 keyskip1 slice R21-L3 covered (doctrine mechanic 6): I skip
   wordsize=32/offset=0/keyskip1 for those three reducers.

R21-L3 NC-3 also notes random29/i386-1word was swept by S-G3 (round20). I do not re-run random29
i386; I include random29 only at wordsize=64 (2-word amd64, distinct) to complete the reducer set.
