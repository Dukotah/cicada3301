# ROUND 19 / DERIVED-KEY DICTIONARY — PRE-REGISTRATION
### Lane 2: is the pad a short-seed-DERIVED keystream (finite, enumerable) rather than a true external OTP?

_Written 2026-09-30, before any keystream was produced for this lane and before any decode was
scored. Binding doctrine: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
PREREGISTER-ONLY phase — the attack is NOT run in this phase._

**Trust anchor, confirmed before this file was written:**
`python3 liber-primus/tests/validate.py` must emit `=== ALL VALIDATIONS PASSED ===` (5/5 known
solves). This PREREG asserts nothing about a negative; the trust anchor is cited because every
negative this lane could later produce rests on it.

**Instrument this lane will borrow (it builds no decoder/adjudicator of its own):**
- Decoder: I1 `driftbeam` (Round 19 Phase 0, GATES PASSED), not the rigid decoder, never the
  rigid decoder on LP2. `analysis/round19/I1/RESULTS.md`.
- Adjudicator: I2 nine-register panel + the four doctrine-R3 language-agnostic statistics.
- Nulls: I3 recalibrated `threshold_for()` / per-mode extreme-value params in
  `analysis/round19/I1/out_fp_tail.json`.

---

## 0. THE AIMING TEST (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it? (recognizer + planted shape)

**A hit** is a tuple `(seed, kdf, params, reduction, sign, direction, atbash, offset)` whose
derived rune stream, applied under the pinned soft key-skip filter (or a `skip_by_two` /
drift variant the I1 beam can now represent), turns an unsolved LP2 page into text that clears
the I3 null on at least one register of the I2 panel AND recovers >= 0.90 of rune indices AND
reproduces on a held-out slice.

**The planted shape (the recognizer, proven before any blind search).** The derived-key family
is NOT a flat-prior space: the exact derivation under test (SHA/HMAC-counter, PBKDF2, scrypt,
`$RANDOM`/glibc `rand`, TeX LCG, Py2.7 `random`) is a *deterministic function of a published
seed*. So the recognizer has two gates, both pre-registered:

> **DK-PC1 (scorer-free plant-and-recover by identity).** Take a seed genuinely resident in the
> dictionary, produce its keystream under one enumerated derivation, hand ONLY the stream to the
> enumerator, and require the enumerator to return the planted tuple as an EXACT, UNIQUE, rank-#1
> match over the full cross-product. A screen that cannot re-find a planted seed by identity
> cannot find one by score. Independent of every Phase-0 gate. (Mirrors G3's G3-PC1.)

> **DK-PC2 (score-based plant-and-recover, through I1+I2).** Encipher a known English (and, per
> L7-A, a Latin / OE / half-vowel) plaintext with a PBKDF2 keystream from a dictionary seed under
> the pinned filter; hand the ciphertext to I1+I2; require the correct seed to (a) clear the I3
> null on its own register and (b) beat a deliberately-wrong seed by the I1 G-FP margin. This
> re-uses D3's `round12/D3/pc_derivedkey.py` positive control, which already demonstrated the
> SHA-counter member recovers (noise ~-7.5 -> English ~-4.4) through the skip-aware beam.

**Proof the instrument can recognise the planted shape — already measured, cited, not asserted:**
`analysis/round19/I1/RESULTS.md` GATE table: baseline construction recovered at full book
L=12,956 to **-4.318 / 99.81 %**; the `skip_by_two` construction the OLD beam missed at
**-6.90 / 25.8 %** is recovered by I1 at **-4.285 / 100.0 %**; wrong keys stay in the noise band
at `lam>=8` (0/2000 reach -5.5). So for the construction classes this lane will emit, the
repaired instrument demonstrably emits the planted hit. **Load-bearing caveat carried into Q4:**
I1 G-FP also shows a permissive transition raises the wrong-key null by +0.58..+0.9, so this
lane MUST adjudicate permissive decodes against the I3 recalibrated per-mode bar, never the
historical -5.5 floor.

### Q2 — What measured fact raises this family's prior above the flat rate? (with file path)

**Two tiers, honestly separated.**

**Tier A — the KDF/S2K sub-family (PBKDF2 / scrypt / EVP_BytesToKey / GnuPG S2K):**
`analysis/round18/L1-toolchain/RESULTS.md` **§6.2 rank 6, prior weight ×1.5**, resting on fact
F6: "GnuPG is demonstrably on the box and in daily use (46+ signed messages, `GnuPG v1.4.11`);
an author who signs everything with GnuPG plausibly derives key material with the crypto tools
already installed." This is an evidence-derived prior (doctrine R4), BUT it is modest (×1.5, the
second-lowest promoted rank) and the same results file self-annotates: *"R16-KDF covered a KDF
family — check its `not_covered` before re-running."* It is NOT a completeness ritual, but it is
also NOT a strong prior. The honest counterweight is `LEDGER.json:L1-PRIOR-PROPAGATION`
not_covered: *"none of this establishes that any LP2 keystream came from ... any named
generator."* The GnuPG-on-box fact licenses S2K/PBKDF *as a candidate*, not as a favorite.

**Tier B — the enumerable generators this lane folds in (the stronger, cheaper prior):**
`analysis/round18/L1-toolchain/RESULTS.md` §6.2 ranks 1-5: `$RANDOM`/glibc `rand` (rank 4, ×2,
15-bit tiny seed), Py2.7 `random.seed(str)` (rank 2, ×3, and on i386 the string-seed path
COLLAPSES to a 2^32 enumeration — see G3 PREREG §Q3), TeX/LaTeX LCG (rank 5, ×2, fully
enumerable). These are higher-prior AND enumerable, which is why the lane's first tranche is
enumerable-first, not KDF-first.

**Verdict on Q2:** NOT a completeness ritual. The lane carries a real (if modest) evidence prior
for its KDF tier and a stronger evidence prior for its enumerable tier. The single most decisive
fact, however, is structural, not toolchain: `LEDGER.json:VERDICT-OTP-CLASS` coverage field reads
verbatim *"The battery separates the two members of the class; it does not choose between them.
Only running the derived-key dictionary chooses."* The README names this the live gap. That is
the measured fact that this lane, and only this lane, discharges.

### Q3 — Is the space bounded, and by what? (enumerable | samplable(+coverage%) | unbounded, with size)

**Mixed; the lane commits to an ENUMERABLE first tranche with a stated coverage fraction, and
labels the samplable/unbounded remainder honestly.**

| axis | size | class |
|---|---|---|
| `$RANDOM` / glibc `rand()` 15-bit short seed | 2^15 seeds x (few impl variants) | **ENUMERABLE** (minutes) |
| TeX/LaTeX `\pgfmathrandom` / `lcg` / `random.tex` LCG | small published-modulus LCG, seed range bounded | **ENUMERABLE** |
| Py2.7 `random.seed(str)`, i386 build | collapses to <= 2^32 MT states (G3 §Q3) | **ENUMERABLE** (same size as full-32 sweeps the repo already runs) |
| PBKDF2 / scrypt over Cicada-PUBLISHED seeds | seed dictionary x iter-counts x salts x reductions | **ENUMERABLE where seeds+params are the published finite set**; samplable once salts/iters open up |
| Py2.7 `random.seed(str)`, amd64 build | <= 2^64 | **samplable only** (coverage % stated at run time) |
| arbitrary salted H(salt \|\| seed), unknown salt | unbounded | **unbounded** — reported last, null worth ~little |

**Seed dictionary (finite, reused verbatim, NOT rebuilt):** B-04's `seeds.py` (2,165 entries,
504-entry core) plus the Cicada-published constants the task names — 3301, prime sequences, the
`7A35090F` key id, the page-56 AN-END 512-bit hash. Published-seed count is a **finite,
human-checkable object** (doctrine R5 tier 1).

**Coverage fraction fixed in advance:** the lane commits to 100 % of (enumerable generators x
published-seed dictionary x documented reductions) as Stage A, and reports the covered fraction
of the KDF param space (iteration-count grid, 3 Stage-A salts + the new ones R16-KDF's
not_covered names) as Stage B. The amd64 / arbitrary-salt tail is explicitly NOT claimed as
covered; its coverage % is reported, never rounded to "exhausted" (doctrine R7).

### Q4 — The three conditionals every negative this lane produces will carry (doctrine Q4/R2)

1. **Key space swept.** The enumerable generators + published-seed dictionary + documented KDF
   param grid above; EXCLUDING: seeds outside the dictionary, salts outside the stated set,
   iteration counts outside the grid, amd64 Py2.7 beyond the sampled fraction, arbitrary salted
   constructions (all carried as `not_covered`, verbatim from `LEDGER.json:R16-KDF` /
   `B-04` not_covered so the negative composes with prior ones instead of overwriting them).
2. **Decoder transition model.** I1 `driftbeam` at the mode used per row — baseline `keyskip1`,
   `skip_by_two`, and free-drift — NOT the rigid decoder. The row records which I1 mode produced
   it, because a null under `keyskip1` does not cover `skip_by_two` and vice versa (L7-B).
3. **Adjudicator register.** The I2 nine-register panel (EN / LP1-orthography / Latin / OE / DE /
   CY / half-vowel / no-vowel) PLUS the four R3 language-agnostic statistics — NOT English-only.
   Every prior KDF negative (R16-KDF, B-04) is English-register-only at measured power 1.00 EN /
   0.33 Latin / 0.00 vowel-dropped; this lane's negative must be register-panel-wide or it is as
   meaningless as the ~10^10 that preceded it (L7-A).

### Q5 — The single observation that abandons this lane at 10 % of budget (kill condition + checkpoint)

**Kill condition:** at the 10 % checkpoint (end of DK-PC1 + DK-PC2 + the first fully-enumerated
generator, i.e. `$RANDOM` 2^15 x dictionary), if DK-PC1 fails to re-find a planted seed by
identity (rank-#1 unique EXACT), OR DK-PC2's planted seed fails to clear the I3 per-mode null on
its own register while a wrong seed does, the ENUMERATOR or the borrowed instrument is broken and
**no negative from this lane would be a negative** (doctrine: a null from an unvalidated
instrument is not a negative). Abandon and report the instrument failure, do not proceed to sweep.
**Secondary kill:** if the enumerable first tranche cannot be driven through I1+I2 inside the
lane's compute budget at the per-decode cost I1 G-COST published (5-9x at L=240-400), the lane is
infeasible as scoped; re-scope to the single highest-prior generator (Py2.7 i386) and report
coverage, never "exhausted."

---

## 1. R3 COLUMNS (CI-ENFORCED) this lane will persist on EVERY sweep row

Per doctrine R3 and `analysis/handoff/validate_ledger.py`, every row stores, alongside the
English score: **decrypt IoC*N**, **min distinct symbols over a 32-rune window**, **best
non-English LM score over the I2 register panel**, and a **compressibility** figure — plus the
I1 mode and the I3 per-mode bar used. A row missing any of these voids the run.

## 2. COVERAGE x POWER reporting (doctrine R1/R2)

No coverage number will be published without its measured power, on BOTH axes:
- **register axis** — power from I2/L7-A (EN 1.00, Latin 0.33, half-vowel 0.25-0.33, Welsh 0.00,
  vowel-dropped 0.00 for the baseline construction; this lane re-measures under I1's permissive
  modes).
- **construction axis** — power from I1 (baseline 99.81 %, `skip_by_two` 100.0 %, free drift,
  key-advance). The negative states which constructions it can and cannot represent.

## 3. THE AN-END BLIND HOLDOUT (mandatory gate on any above-threshold candidate)

Any candidate that clears the I3 bar must FIRST be forced through the AN-END holdout: the known
page-56 method is the totient keystream `(prime_i - 1) mod 29` shift-down (`src/lp/ciphers.py:64
prime_totient_stream`) + the F-rune interrupter rule. A method/pipeline claiming to decode an
UNSOLVED page must, handed only page-56 ciphertext + its stated external input (NOT handed the
key), rediscover that keystream BLIND. A derived-key pipeline that cannot re-derive AN-END's
keystream from ciphertext has not earned the right to claim an unsolved page. The holdout outcome
(rediscovered / not) is reported with any candidate. (In the PREREG phase this is declared, not
run.)

## 4. LEDGER HYGIENE

Before the sweep runs, this lane re-reads `LEDGER.json` entries VERDICT-OTP-CLASS, R16-KDF, B-04,
B-05, B-08, L7-A-ARCHIVE-RESCORE, R18-L2-* and copies their `not_covered` lists forward so this
lane's negative EXTENDS rather than re-runs measured ground (doctrine mechanics 6; "do not re-run
measured ground"). R16-KDF's 692,064 KDF configs are NEGATIVE-English-only; this lane's new
ground is: (a) the register panel over the KDF tier, (b) the enumerable generators R16-KDF never
touched, (c) the `skip_by_two`/drift construction axis, (d) the published-constant seeds
(`7A35090F`, page-56 hash) and param axes R16-KDF lists as not_covered.

## 5. DEPENDENCY

Per the task and doctrine R1: this lane WAITS for Lane 1's power table before trusting any null.
Lane 1 (I1) has PUBLISHED its envelope (`analysis/round19/I1/RESULTS.md`, GATES PASSED), so the
dependency is satisfiable; the lane will not score against the -5.5 floor but against I3's
per-mode recalibrated bar, as I1 G-FP requires.
