# L3 — string-seed-dictionary: true Py2.7 seed(str) semantics over a large bounded dictionary

_Round 28, pre-registered 2026-09-08. Mode: run-now-light (Python single-thread nice-15;
the C engine is not required — see the subsumption argument, which removes the expensive half
of the space without a single decode)._

## The pinned semantics (the whole point of the lane)

CPython **2.7** `random.seed(a)` for a `str`: `_random.Random.seed` takes
`PyObject_Hash(a)` — the **pre-randomization** Python 2 string hash
(`x = ord(s[0]) << 7; for c: x = (1000003*x) ^ ord(c); x ^= len(s)`, C-long width,
randomization off by default in 2.7) — then the (absolute value of the) hash is fed to
`init_by_array(words)`. Consequences:
- **i386 (32-bit hash)** → 1 word in [0,2³²) → `init_by_array([w])`. This image is a
  **subset of the space R27-S1 already swept to measured exhaustion** (pair relation,
  NULL) and that S2 is completing for the exact relation. **Claimed subsumption:** every
  possible i386 Py2.7 string seed, for {reducer random29, offset 0, pair relation}, is
  already excluded — zero compute. Lane R verifies this empirically (≥100 words,
  keystream-identity check). This closure statement is itself a Round-28 deliverable.
- **amd64 (64-bit hash)** → 2-word `init_by_array([lo,hi])` — **NOT subsumed**
  (`R21-L3` NC-2: the 2⁶⁴ image was only sampled via a folded map; `R26-A` swept only
  ~corpus-sized string seeds at wordsize=64). **This is the lane's runnable space.**

## Anti-repeat (ledger ids extended, disclosed as the EXTENSION beyond them)

- **`B-04`** (negative): 2,165-entry dictionary through **hash-derived keystreams**
  (MD5/SHA/HMAC/AES/RC4/ChaCha constructions) — a different construction family entirely;
  its `not_covered` explicitly includes "seeds outside the 2,165-entry dictionary".
- **`R26-C-SEMANTIC-SEED-ZOO`** (negative): 323 semantic seeds (31 str) × 7 generators;
  `not_covered` explicitly reopens "semantic seeds outside the 323-value corpus
  enumeration". L3's dictionary minus B-04's 2,165 minus R26-C's 323 is the claimed set.
- **`R27-CPORT-MT32-FULLSWEEP`**: `not_covered` lists "string seeds (hashed path)" as
  outside its integer sweep — L3 consumes exactly that pointer, and returns the i386 half
  as subsumed rather than re-swept.
- **Round 8's `analysis/seed_sweep/string_seeds.py`** (15,408 decodes): its `stream()`
  seeds the **running Python 3 interpreter** (`random.Random().seed(str)` = SHA-512 path;
  its "Python 2 semantics" comment was never implemented as code). So R18-L1's promoted
  family "Python 2.7 random with Python-2 seed-string semantics ×3" has **never actually
  been run at dictionary scale** — this lane is its first true firing.
- **`R21-L3-PY27-REDUCERS`** / **`R20-SG3-PY27-RANDOM29`**: integer/word sweeps; NC-2
  names the 2⁶⁴ amd64 image as open.

## Aiming Test

**Q1 — Hit shape + recognizer.** A dictionary string whose amd64 Py2.7-hash-seeded
`random29` keystream decodes LP2 under keyskip1/keyskip2. Recognizer: the R25/R24 stage-A
screen (pmax on L=120) → stage-B hitfn20 3-clause gate — the exact pipeline that recovered
the R25 planted seed at 1.000. **Planted control before any null:** pick a dictionary word,
generate its wordsize-64 keystream via `../../round19/G3/gen_py27.py`, encipher a plant
under the skip filter, and require the full pipeline to flag it with recovery ≥0.90,
HIT=True — once per (reducer × relation) cell. **Hash-image pinning vectors:** the py2-hash
implementation must reproduce ≥5 published Python-2.7 64-bit hash values exactly and
cross-check against `gen_py27`'s existing string path (which R26-A verified produces
w64 ≠ w32 streams); if a real `python2.7` binary is obtainable on the box, gate against it
directly (preferred). No vector pass → no sweep.

**Q2 — Measured fact above flat prior.** `round18/L1-toolchain/RESULTS.md` §6: the measured
Ubuntu 11.04–12.04 + GnuPG 1.4.11 toolchain promotes **Python 2.7 ×3** with seed-string
semantics named explicitly — the highest-graded evidence-derived prior in the repo — and
amd64 was the modal Linux ABI of that period. Priors from a held artifact, not lore.

**Q3 — Bounded?** Enumerable: dictionary = (a) a full English wordlist (~370k, fetched,
sha256-pinned at fetch time, gitignored per repo policy), (b) in-repo corpus builder —
Cicada words/phrases/solved-plaintext n-grams, gematria forms, dates 2011–2014 in common
spellings, onion strings, key IDs, case/spacing variants — target total **10⁵–10⁶ candidate
strings**, deduplicated **by 64-bit hash image** (collisions collapse). Cost at the R25
measured single-core screen rate (~380 seeds/s; budget 300/s niced): 1e6 seeds ≈ 55–90 min
per (reducer × relation) cell. Planned cells, in order: random29×pair, random29×exact,
grb5_mod×pair, grb5_rej×pair, shuffle29×pair ⇒ ≈5–7 h total on one throttled core. Cells
not reached are stated un-run, not sampled.

**Q4 — Three conditionals of the negative:**
1. key space: this dictionary's amd64 hash image (strings outside the dictionary, other
   Python versions' hashes, PYTHONHASHSEED/-R randomized hashes are NOT covered), offset 0;
2. transition model: keyskip1 + keyskip2 only;
3. register: I2 9-register panel (EN_NOVOWEL detection-only per R21-L3).

**Q5 — Kill at 10%.** Vector or planted-control failure in any cell → that cell does not
run. At 10% of the first cell, if throughput <150 seeds/s niced, cut the dictionary to the
corpus-priority tier (~1e5) and state the reduced coverage; if S2 throughput degrades >10%,
pause.

## Bars

Stage-A candidate bar and stage-B claim bars are the frozen R27 constants per relation
(pair 7.3835, exact 7.6342 at N=1e6 ceiling — conservative for N≤1e6·cells); recovery 0.90;
held-out ¾ ≥0.90. SWEEPROW/3 language-agnostic stats persisted per adjudicated candidate;
per-cell pmax histogram for the sub-candidate mass. Survivors FLAGGED-FOR-ORACLE.

## Coverage promise (honest)

Delivered: (i) the i386 subsumption statement (100% of all possible i386 string seeds for
random29/offset-0/pair, inherited from S1's measured exhaustion — conditional on S2 for
exact); (ii) 100% of the deduplicated dictionary's amd64 image for each cell actually run,
listed cell-by-cell. Not covered: strings outside the dictionary (the 2⁶⁴ image is not
enumerable), offsets ≠0, other reducers/relations/registers, Python ≠2.7 semantics.

---

## AMENDMENT 2026-09-08 (pre-run, before any null was counted)

Dated deviations, each decided BEFORE the sweep fired:

**A1 — Q5 throughput cut invoked at cell start, not at 10%.** Measured stage-A
throughput on this box with R27-S2 saturating all 6 cores (this lane runs
`nice -n 15`, single thread, per round rules): **pair 41.7 seeds/s, exact 84.1
seeds/s** (30-seed timing probe, gen_py27 w64 + driftbeam beam_w=64 + I2, the real
code path). Both are under the pre-registered 150 seeds/s kill threshold, so the Q5
cut applies from the start: the grid becomes
(i) ALL FIVE cells over the **corpus-priority tier** (tier 0, in-repo builder), then
(ii) the **full ~390k English wordlist** extension over the two top-ranked cells
(random29×pair, then random29×exact) with the remaining wall budget.
Cells×tiers not reached are reported **not-run** (and queued), never sampled.

**A2 — wordlist source is in-repo, not fetched.** The PREREG said "fetched,
sha256-pinned". A 390,306-word English list already exists in-repo:
`corpus/E-tooling/vendor/cicada-solvers__libergo/words.txt`
sha256 `0ae20e6fbc8029f2b21a80cf673359ec54903fc14dde3a89d0df64d53ba0c1a9`.
In-repo beats network (reproducible, no availability risk). Pinned here instead.

**A3 — B-04's 2,165 entries are INCLUDED in tier 0, not excluded.** The PREREG's
"L3's dictionary minus B-04's 2,165" wording was over-conservative arithmetic:
`LEDGER.json` B-04 swept those strings through **hash-derived keystreams**
(MD5/SHA/HMAC/AES/RC4), and `R19-G3` ran them only through a labelled plumbing pilot
("0 decodes of key space cleared"; its NC-4 opens the amd64 branch explicitly). No
lane has ever swept the 2,165 through Py2.7-MT `seed(str)` at the hitfn20 gate, and
they are the highest-prior strings in the repo — excluding them would re-create the
exact gap this lane exists to close. Genuinely measured ground that IS excluded:
R26-C's 31 string seeds (w64, offset 0) are skipped **by 64-bit hash image** in the
four cells R26-C covered (random29×{pair,exact} via keyskip2/keyskip1, grb5_mod×pair,
grb5_rej×pair); they are swept in shuffle29×pair (R26-C had no shuffle29).

**A4 — hash-image pinning gate upgraded to the preferred path.** A real amd64
CPython **2.7.18** binary exists on the box (`/home/dukotah/py27/root2718/usr/bin/python2.7`,
runs; the 2.7.3 root's libssl dependency is broken so 2.7.18 is the live gate, and
2.7.3↔2.7.18 byte-identity was already established by `round19/G3/validation.json` V3).
Gate = (a) gen_py27 `--selftest` (14 real-2.7.3-captured stream vectors + 3 hash
vectors) PASS, and (b) a fresh ≥1,000-string sample of THIS dictionary hashed by the
live 2.7.18 binary vs `py2_str_hash(·, 64)`, required 100% equal. This supersedes the
"≥5 published values" fallback (it is strictly stronger).

**A5 — planted-control seed strings are real dictionary entries** (one per cell,
`THE PRIMES ARE SACRED` — B-04 slogan family, present in tier 0), enciphered from
`self_reliance.txt` idx 5000:5240: pair cells use the S1/C2 skip_by_two model
(reject doubling with p=0.83, j+=2), exact cells use
`campaign18_skip/skipdecode.encipher_keyskip` (one-draw, j+=1) per R27 S2-CONTROL.md.
Required: hitfn20 HIT=True AND recovery ≥0.90 in that cell's preset, before that
cell's null counts.

## AMENDMENT 2026-09-08 #2 (mid-run, before any null is claimed)

**A6 — measured end-to-end power envelope (10 plants x 5 cells, control_e2e.json).**
Beyond the pre-registered one-plant-per-cell gate (controls.json — 5/5 PASS, lane
proceeds), a 10-plant end-to-end probe (screen + 3-clause gate, real code path) measured:
random29xpair 1.0, grb5_rejxpair 1.0, shuffle29xpair 1.0, random29xexact 0.9,
grb5_modxpair 0.8. Every failure is **clause 3 only** (held-out 3/4 phase attribution:
the head-quarter sub-decode attributes a wrong entering key pointer for some
keystream/skip layouts) with rune recovery 1.000 and pmax 25.2 >> bar in all failing
plants. INSTRUMENT FINDING for the red-team lane: hitfn20 clause 3 is a real
false-negative channel (~0.1-0.2) on true keys for some reducer/relation cells; prior
rounds' "false-reject 0 observed" was n=1-per-cell.
**Conservative mitigation, binding on this lane's finalization:** every persisted
stage-B row with pmax >= the cell claim bar is FLAGGED-FOR-ORACLE regardless of
clause-2/3 outcomes (nothing near a bar is dropped silently); per-cell power is
reported as measured above, and the negative's power claim for grb5_modxpair /
random29xexact is degraded accordingly.
