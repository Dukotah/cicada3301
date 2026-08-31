# Round 26 — Lane C — SEMANTIC-SEED enumeration — PREREG

Author lane: `analysis/round26/C/`  •  Date: 2026-08-31  •  Prior: LOW-but-live.

## Thesis (aimed at "the puzzle must be solvable", NOT "the pad is random")

Cicada built a *puzzle*: every prior stage was solvable by design, so if LP2 0–54 uses a
DERIVED key, the seed was meant to be DISCOVERED — hence SEMANTIC, not `/dev/urandom`. This lane
therefore does NOT brute-force a raw 2^32 key. It enumerates a small, corpus-semantic candidate
SEED set (primes / prime-indices / totients / dates / coordinates / notable Cicada integers /
gematria sums of solved LP1/LP2 plaintext words & koan phrases) and feeds EACH value **as a SEED
through a generator** (the distinction that is the whole point: a semantic value → seed → keystream,
never a semantic value used directly as the key). The generator zoo INCLUDES the totient/prime
ladder generators (`src/lp/ciphers.py`) that `tests/validate.py` proves reproduce the solved
totient page (05.jpg, "THE PRIMES ARE SACRED / TOTIENT"). Decode with the control-validated
skip-aware `pair` (keyskip2) + `exact` (keyskip1) decoders; certify ONLY through `hitfn20`.

## The five aiming answers

**Q1 — What would a hit look like, and would THIS instrument recognise it? (plant + recovery)**
A hit = a (seed, generator) whose keystream, decoded skip-aware, produces English at
`hitfn20` recovery ≥ 0.90 AND clears the P3 panel-max null AND reproduces on the held-out 3/4.
PLANTED & RECOVERED before any sweep (see control.py output in RESULTS.md):
- semantic string seed "THE PRIMES ARE SACRED" → gen_py27 random29 → skip_by_two → **pair recovers 0.992, HIT=True**
- integer seed 3301 → gen_perl glibc `g_r29` → skip_by_two → **recovers 1.000, HIT=True**
- start=3301 → `prime_totient_stream` (the solved-page ladder) → **recovers 1.000, HIT=True**
- start=3301 → `totient_stream` → **1.000**;  start=100 → `prime_stream` → **1.000**
The instrument recognises a hit produced by every generator in the zoo. (The beam without the
`pair` relation gets ~0.26 on skip_by_two — L7-B — which is exactly why we gate on `pair`.)

**Q2 — What measured fact raises this family's prior above flat? (cite a file path)**
`tests/validate.py` proves the totient/prime-totient ladders in `src/lp/ciphers.py`
(`prime_totient_stream`, `totient_stream`) REPRODUCE a real solved LP page (05.jpg). A generator
that already solved one Cicada page is not a flat-prior generator — it is the page-56-class method
the corpus itself endorses. That is the single measured lift; the seed set inherits the puzzle's
own "solvable-by-discovery" design property. Prior stays LOW because 0–54 has resisted every
derived-key sweep so far (LEDGER VERDICT-OTP-CLASS), but it is non-negligible for THIS composition.

**Q3 — Is the space bounded? (size + enumerable + fraction covered)**
BOUNDED and fully ENUMERABLE. Seed set = deduplicated corpus-semantic values (built by
`build_seeds.py`, size printed in RESULTS.md, expected hundreds–low-thousands). Generator zoo =
4 families × their idiomatic seed-injection (gen_py27 {random29, grb5_mod, grb5_rej}, gen_perl
glibc g_r29, ciphers.py {prime, totient, prime_totient} ladders with start=seed), × 2 decoders
(exact, pair) × small offset set {0}. Total (seed × generator × reducer × decoder) rows =
enumerable and swept 100% of the ENUMERATED prior-dense set. Coverage fraction of the raw 2^32
key space is ~0 by construction — this lane's claimed fraction is **the semantic-seed set, swept
in full**, NOT a slice of 2^32. Stated explicitly, no "closed".

**Q4 — The three conditionals the negative carries.**
- key-space swept: ONLY the deduplicated corpus-semantic seed set (finite list), fed as SEEDS
  (hashed/abs then chunked for MT; srand48 for glibc; start-offset for the ladders). NOT raw words.
- decoder transition model: keyskip1 (`exact`) + keyskip2 (`pair`, skip_by_two-exact). Rejection
  loops burning >2 draws/rejection and permissive drift are NOT this lane's relation.
- adjudicator register: `hitfn20` panel (EN/LA/OE/DE/CY/LP1 via I2 adjudicate) + panel-max null.
  A non-panel register (e.g. base32/gzip payload before language) is out of scope.

**Q5 — The single observation that kills this lane at 10% budget (checkpoint).**
After the first ~10% of (seed×generator) rows: if the max hitfn20 recovery over all rows is
< 0.55 AND zero rows clear the panel-max bar, the lane is dead-on-arrival (no semantic seed is
even approaching the recovery floor). Written to `progress checkpoint` in RESULTS.md. A single
bar-clearing survivor at ANY point = STOP-AND-ALERT → flagged_for_oracle, never auto-certified
(R21-L1: no-oracle proxy is leaky).

## Anti-repeat proof (ledger ids EXTENDED + not-covered citation)

This composition = {corpus-semantic value **as SEED** × page-56 ladder / PRNG generator zoo ×
skip-aware keyskip1+keyskip2 decode × hitfn20} is UN-RUN. Proof by citing coverage/not_covered:

- **R16-PRNG** (extend): its `coverage` = "the 7 CENSUS PRNG generators seeded 2011–2015";
  `not_covered` lists *"secrets outside the tested list"*, *"non-English plaintext registers"*,
  *"rejection samplers consuming more than one draw per rejection"*. R16-PRNG (a) used the OLD
  beam (one-draw rejection only), (b) never ran the ciphers.py totient/prime LADDER generators,
  (c) never enumerated a corpus-**semantic** seed set as SEEDS. This lane sits squarely in its
  not_covered: skip_by_two (pair) decoder + ladder generators + semantic seed set.
- **R16-KDF** (extend): `not_covered` = *"secrets outside the 534-item list"*, *"rejection
  samplers consuming more than one draw per rejection"*, *"multi-stage constructions"*. Same gap.
- **R21-L3-PY27-REDUCERS** (extend): swept RAW `init_by_array([w])` **integer words** of the 2^32
  space (prior-dense slice), NOT semantic values fed through `py27_seed`'s hash/abs+chunk SEED
  path, and never through the glibc or ladder generators. Its `not_covered` = "the flat-prior tail
  of 2^32". Different axis: I sweep a SEMANTIC list, not a word range.
- **R25-COMPUTE-TAIL-CHUNK1** (do NOT duplicate): parked Py2.7-MT `init_by_array([w])` random29
  offset-0 CONTIGUOUS 2^32 tail. I extend DIFFERENT generators (glibc, ladders, MT via the
  string/int SEED path with multiple reducers) and a DIFFERENT (semantic, enumerated) seed source.
- **R11** number-channel lanes tested corpus numbers as DATA/feedback channels, not as SEEDS of a
  generator zoo (LEDGER R11-adjacent entries carry the DATA/feedback framing). Semantic-value-AS-SEED
  is the un-run reframe.

Composition PROVEN not-covered. New ledger rows: `R26-C-SEMANTIC-SEED-ZOO`.
