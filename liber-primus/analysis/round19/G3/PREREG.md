# ROUND 19 / G3 — PRE-REGISTRATION
### Python 2.7 `random.seed(<string>)` — the silent coverage hole

_Written 2026-08-26, before any keystream was produced and before any decode was scored.
Lane G3, Phase 1 of `analysis/round19/CAMPAIGN-PLAN.md`. Binding doctrine:
`liber-primus/ARMADA-DOCTRINE.md`._

**Trust anchor, run before this file was written:**
`python3 liber-primus/tests/validate.py` → `=== ALL VALIDATIONS PASSED — rig reproduces known solves. ===` (5/5).

**Environment recon done before this PREREG** (tooling availability only — no hypothesis was
measured): a real CPython **2.7.3** (`Ubuntu 12.04 python2.7_2.7.3-0ubuntu3.19`, built with
GCC 4.6.3) and a real CPython **2.7.18** (`python2.7_2.7.18-13ubuntu1.5`) were obtained and
both execute in WSL. See §7.

---

## 0. THE AIMING TEST (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A hit is a `(seed, wordsize, derivation, reduction, sign, direction, atbash, offset)` tuple
whose Python-2.7 rune stream, applied under the pinned soft key-skip filter, turns LP2 into
readable text.

**This lane does not own the adjudicator and will not score anything** (see §6, THE HOLD).
What it owns, and what it therefore validates here, is the *enumerator*: a planted hit must
be recoverable **by identity**, without any scorer at all.

> **G3-PC1 (keystream plant-and-recover, scorer-free).** Take a seed that is genuinely
> resident in the B-04 dictionary, produce its Python-2.7 keystream under one enumerated
> derivation, hand only the *stream* to the enumerator, and require the enumerator to return
> the planted tuple as an **exact** match over the full cross-product of 2,165 seeds × every
> enumerated derivation. Required: **rank #1, exact equality, unique**. A screen that cannot
> re-find a planted seed by identity cannot find one by score either, and this check is
> independent of every Phase-0 gate.

The score-based plant-and-recover (B-04's G2 gate, re-run through I1+I2) is **deferred to
Phase 2** and is a precondition on any negative this lane's keystreams are later used to
claim. Stated here so it cannot be quietly dropped.

### Q2 — What measured fact raises this family's prior above the flat rate?

`liber-primus/analysis/round18/L1-toolchain/RESULTS.md` **§6.2 rank 2, ×3**, resting on
facts **F1/F6/F7/F8** of that lane's §6.1:

- **F6** — 46 of 46 curated 3301 signed messages, spanning 2012, 2013 and 2014, carry
  `Version: GnuPG v1.4.11 (GNU/Linux)`. One signing environment, unchanged for three years.
- **F7** — GnuPG **1.4.11** specifically (released 2010-10-18); Ubuntu 11.04–12.04 LTS shipped
  exactly 1.4.11, Debian wheezy shipped 1.4.12. The box is an **Ubuntu 11.04–12.04-class**
  GNU/Linux workstation.
- **F1/F8** — the 58 page JPEGs were written by **ImageMagick at its default quality 92**,
  over a numbered page set, with no EXIF/XMP/COM and no post-pass. Someone drove `convert`
  over `0…57` from a short script.

**Python 2.7.3 is Ubuntu 12.04's system Python.** L1 §6.3 item 2 names this lane explicitly:
*"Python 2 and Python 3 hash a seed string differently; a sweep written in 2026 that used
`random.seed("CICADA3301")` under Python 3 did not test what a 2012 author's script would have
produced. This is a silent coverage hole and it is cheap to close."*

The prior is therefore evidence-derived (doctrine R4), not lore: the *operating system* is
measured from the author's own signature blocks, and the *scripting habit* is measured from
the encoder defaults in the published images.

### Q3 — Is the space bounded, and by what?

Yes — and more tightly than "a dictionary of strings", because of the mechanism itself.

CPython 2.7 compresses **any non-int seed** to a single `long` via `PyObject_Hash`, casts it
to `unsigned long`, and splits *that* into 32-bit words for `init_by_array`
(`Modules/_randommodule.c`, `random_seed`, lines 231–307 of the 2.7 branch). So:

| build | image of the string-seed path | enumerable? |
|---|---|---|
| **i386** (`sizeof(long)==4`) | `init_by_array` over **exactly one** 32-bit word ⇒ **≤ 2³² distinct MT states** | **YES — fully enumerable**, same size as the full-32 sweeps this repo already runs |
| **amd64** (`sizeof(long)==8`) | `init_by_array` over one or two 32-bit words ⇒ ≤ 2⁶⁴ states | no — samplable only |

That is the load-bearing structural fact of this lane: **on a 32-bit Ubuntu 12.04 box, the
entire space of Python-2.7 string-seeded pads is a 2³² enumeration**, regardless of what the
string was. Python 3 has no such collapse (its `str` seed expands to ≥ 576 bits before
`init_by_array`), which is precisely why the two are not substitutes.

**What this lane commits to enumerating (Phase 2, gated):**

| axis | size | enumerable? |
|---|---|---|
| seed dictionary (B-04 `seeds.py`, reused verbatim, **not** rebuilt) | **2,165** (core subset 504) | complete |
| build word size ∈ {amd64-64, i386-32} | **2** | complete |
| derivation ∈ {`seed(str)`, `seed(str)`+`jumpahead(k)`, `seed(float)`, `seed(int)`} | 4 (jumpahead over k ∈ {29, 761, 1033, 3301}) | complete |
| rune reduction ∈ {`int(random()*29)`, `getrandbits(5)%29`, `getrandbits(5)`+reject, `shuffle(range(29))` blocks} | **4** | complete |
| sign ∈ {+1, −1}, direction ∈ {fwd, rev}, atbash ∈ {off, on} | 8 | complete (B-04 convention) |
| offset (Stage A pinned 0; Stage B ∈ B-04's 10) | 1 / 10 | complete |

Stage A = 2,165 × 2 × 4 × 8 = **138,560** decodes.
Stage A′ (jumpahead) = 504 × 2 × 4 × 4 × 8 = **129,024**.
Stage B (offsets) = 504 × 2 × 2 × 10 × 8 = **161,280**.
**Lane total ≈ 4.3 × 10⁵ decodes** — three orders of magnitude below B-04's 6.22 M, because
the prior is doing the work instead of the volume (doctrine R4).

**Honest coverage statement, fixed in advance.** The *derivation* space above is enumerated
completely. The *seed* space is not: over the amd64 branch it is a 2,165-point sample of an
unbounded string space, so any negative is worth roughly what B-04's is — it closes a
dictionary, not a family. Over the i386 branch a **complete** 2³² enumeration exists and is
specified in `READY.md` as an optional extension; this lane does not run it.

### Q4 — What are the three conditionals the negative will carry?

Named now, so they cannot be omitted later:

1. **Key space** — the 2,165-entry B-04 dictionary under Python-2.7 semantics, over the
   derivation/reduction/orientation cross-product tabulated in Q3, offset 0 (Stage A) or
   B-04's 10 offsets (Stage B). Not the 2³² i386 image; not seeds absent from the dictionary.
2. **Decoder transition model** — whatever **I1** (`round19/I1/driftbeam.py`) ships. This lane
   pins nothing and claims nothing about it; L7-B says the Round-18 beam represents exactly
   one rejection-loop implementation, so a keystream run through the *old* beam would inherit
   that defect. G3 keystreams are therefore not to be scored by the pre-I1 beam.
3. **Adjudicator register** — whatever **I2** (`round19/I2/adjudicate.py`) ships. L7-A says the
   English quadgram scorer alone has power 0.33 on Latin and 0.00 on vowel-dropped English.

### Q5 — What single observation would make you abandon this lane at 10 % of budget?

**Kill condition, checkpoint = the validation gate (§4), before any keystream is produced:**

> If the Python-2.7 `str` seeding path turns out to produce the **same** MT state as the
> Python-3 path already swept by `analysis/seed_sweep/string_seeds.py`, the lane is a
> duplicate and stops immediately with a one-paragraph RESULTS.md.

Secondary kill: if no real Python 2.7 can be obtained **and** the reimplementation cannot be
validated against citable external vectors, the generator is marked **PROVISIONAL** and does
not enter Phase 2 as validated coverage (it may still be run, labelled).

---

## 1. Hypothesis

**H1.** The LP2 keystream was produced by a short Python 2.7 script on the author's
Ubuntu 11.04–12.04 box: `random.seed(<a Cicada-flavoured string literal>)` followed by an
era-idiomatic reduction to a rune index, applied additively under the pinned soft anti-repeat
filter.

**H0.** No seed in the B-04 dictionary, under any enumerated Python-2.7 derivation, reduction,
sign, direction, reflection or offset, produces text the Phase-0 instrument recognises.

**Why it is not already covered.** Two independent reasons, both checkable:

- **B-04** (`round13/B04/ks.py`) contains **16 generators, none of which is a Mersenne
  Twister.** They are `sha{256,512,1}_ctr`, `md5_ctr`, `sha256_ctr_{le,asc}`,
  `sha{256,512,1}_chain`, `md5_chain`, `hmac_sha256_ctr`, `hmac_drbg_sha256`, `rc4`,
  `aes_ctr_{zeroiv,deriviv}`, `chacha20`. **B-04 has zero MT19937 cells** (see §5).
- **Round 8's string-seed track** (`analysis/seed_sweep/string_seeds.py`) *is* MT19937 via
  CPython, but ran under **Python 3**, whose `str` path is `sha512`-based. Its own docstring
  claims it "also covers `random.seed()` … under Python 2 semantics (hash() of the string)";
  no such code exists in the file. That claim is audited in §5 of `RESULTS.md`.

---

## 2. What Python 2.7 does — the claim to be validated (source-cited)

CPython 2.7, `Modules/_randommodule.c`, `random_seed`:

```c
    if (PyInt_Check(arg))        n = abs(arg);
    else if (PyLong_Check(arg))  n = abs(arg);
    else {
        long hash = PyObject_Hash(arg);          /* <-- the whole difference */
        if (hash == -1) goto Done;
        n = PyLong_FromUnsignedLong((unsigned long)hash);
    }
    /* split n into 32-bit chunks, from the right */
    ...
    if (keyused == 0) key[keyused++] = 0UL;
    result = init_by_array(self, key, keyused);
```

`Lib/random.py` (2.7) `Random.seed` passes a `str` straight through — there is **no `version`
parameter and no digest step**. So a `str` seed reaches MT as `(unsigned long)hash(s)`.

`Objects/stringobject.c`, `string_hash` (2.7):

```c
    if (len == 0) return 0;
    x  = _Py_HashSecret.prefix;      /* 0 unless -R / PYTHONHASHSEED is set */
    x ^= *p << 7;
    while (--len >= 0) x = (1000003*x) ^ *p++;
    x ^= Py_SIZE(a);
    x ^= _Py_HashSecret.suffix;      /* 0 unless -R / PYTHONHASHSEED is set */
    if (x == -1) x = -2;
```

in **signed `long`** arithmetic — hence the word-size split of Q3. Hash randomisation exists in
2.7.3+ (the CVE-2012-1150 fix) but is **off unless `-R` or `PYTHONHASHSEED` is set**, so the
default 2012 behaviour is deterministic. Python 3.2.3+ has the same switch but flips the
default to *on* in 3.3+, which is a second, independent reason a 2026 Python-3 sweep does not
reproduce a 2012 Python-2 script.

Python 3, `Lib/random.py`, for `version=2` (the default):
`a = int.from_bytes(a.encode() + sha512(a.encode()).digest(), 'big')` — ≥ 576 bits, ≥ 18
`init_by_array` words. **Different key array, different MT state, different stream.**

Also to be validated (Python-2-only or Python-2-different constructs):

| item | claim |
|---|---|
| `randrange(29)` / `randint(0,28)` / `choice(pool29)` / `int(random()*29)` | **all four are the same call** in 2.7 — `random.py` `randrange` uses `_int(self.random()*istart)` for width < 2⁵³. In Python 3 they are *not* (Py3 `randrange` uses `_randbelow` → `getrandbits` with rejection). |
| MT words consumed per rune | 2 (`genrand_res53`), no rejection — vs Py3's 1-per-attempt with rejection |
| `jumpahead(n)` | exists in 2.x (`_randommodule.c`, `random_jumpahead`), **removed in Python 3** |
| `seed(<non-negative int>)` | **identical** in 2.7 and 3.x (abs → 32-bit chunks → `init_by_array`) — so this axis is a *duplicate*, carried only as a control |
| `seed(<float>)` | Py2 `_Py_HashDouble` vs Py3's `2⁶¹−1`-modulus float hash — different |

---

## 3. Instrument

- **Generator under test:** `round19/G3/gen_py27.py` — a Python-3 module reimplementing MT19937
  (`init_genrand`, `init_by_array`, `genrand_uint32`, `genrand_res53`, `getrandbits`,
  `jumpahead`) plus CPython 2.7's `random_seed` dispatch and `string_hash`, parameterised by
  word size ∈ {32, 64}.
- **Reference:** real CPython **2.7.3** (Ubuntu 12.04 package, GCC 4.6.3) and real CPython
  **2.7.18**, both executed directly.
- **Seed dictionary:** imported from `analysis/round13/B04/seeds.py` — **reused, not rebuilt**,
  so results are comparable with B-04 row-for-row.
- **Reductions/orientations:** B-04's `sign`, `direction`, `atbash`, `offset` conventions,
  unchanged.
- **Decoder / adjudicator:** *none in this lane.* Phase 0 owns them.

---

## 4. THE VALIDATION GATE (fixed in advance, must pass before any keystream is emitted)

| gate | requirement |
|---|---|
| **V1 — real 2.7 executes** | a real CPython 2.7 runs and prints its version |
| **V2 — string-seed exactness** | for **≥ 300** seeds drawn from the B-04 dictionary (all families represented) × all 4 reductions, `gen_py27.py` (wordsize 64) reproduces the real 2.7.3 output **element-for-element, 100 %**. Anything below 100 % fails the gate. |
| **V3 — cross-build agreement** | 2.7.3 and 2.7.18 agree on every V2 vector (two independent real builds, not one) |
| **V4 — int / float / jumpahead** | `seed(int)`, `seed(float)` and `seed(str)+jumpahead(k)` reproduce real 2.7.3 exactly over a named vector set |
| **V5 — reduction identity** | the claim `randrange(29) == randint(0,28) == choice(pool29) == int(random()*29)` is *measured* on real 2.7.3, not assumed |
| **V6 — Py2 ≠ Py3 (the kill check, Q5)** | for every V2 seed, the Python-2.7 stream **differs** from the Python-3 stream for the same literal. If they agree, the lane stops. |
| **V7 — i386 (32-bit) branch** | either validated against a real i386 CPython 2.7, or shipped **PROVISIONAL** with the reason recorded in `validation.json` |
| **V8 — G3-PC1** | the scorer-free plant-and-recover of Q1: rank #1, exact, unique |

All vectors, pass/fail flags and the confidence label go in `round19/G3/validation.json`.
**A generator that fails V2 or V3 does not enter Phase 2.** A generator that passes V2/V3 but
fails V7 enters Phase 2 with the 64-bit branch VALIDATED and the 32-bit branch PROVISIONAL,
labelled per-row.

---

## 5. Thresholds

This lane sets **no score threshold**, because it scores nothing (§6). Phase 2 inherits
I3's (`round19/I3`) recalibrated bar for the 9-way multi-register statistic. Recording here,
in advance, what this lane will **not** do: it will not reuse B-04's `HIT_BAR = -5.5`, because
doctrine §4 mechanic 4 and I3's existence both say a fixed bar is invalid at large N and the
old bar is calibrated for a single-register scorer that L7-A measured at power 0.33/0.00.

---

## 6. THE HOLD (explicit)

Phase 0 (I1 driftbeam, I2 adjudicator, I3 thresholds) is running concurrently and is not
finished. This lane **stops at the scoring boundary**. Deliverables are validated generators,
a keystream interface, a space statement and a Phase-2 run spec (`READY.md`).

Sole exception, pre-registered: if `round19/I1/driftbeam.py` **and** `round19/I2/adjudicate.py`
both exist when the generator is finished, a **labelled pilot of ≤ 10,000 decodes** may be run
to prove plumbing and measure throughput. A pilot is a timing measurement. It is not evidence,
it does not produce a negative, and its best score is reported as a plumbing artefact only.

---

## 7. Provenance of the reference interpreters

| build | package | source | why this one |
|---|---|---|---|
| **2.7.3** | `python2.7_2.7.3-0ubuntu3.19_amd64.deb` + `python2.7-minimal` + `libpython2.7` + `libssl1.0.0_1.0.1-4ubuntu5.45` | `old-releases.ubuntu.com/ubuntu/pool/main/p/python2.7` (Ubuntu **precise**, 12.04 LTS) | **This is the interpreter L1's prior points at**: Ubuntu 12.04's system Python, built with GCC 4.6.3 |
| **2.7.18** | `python2.7_2.7.18-13ubuntu1.5_amd64.deb` + deps | `archive.ubuntu.com` (Ubuntu focal) | independent second build, 12 years and a different compiler apart — agreement between them is evidence the path is a 2.7-branch invariant, not a build artefact |

Both are extracted to `~/py27/root273` and `~/py27/root2718` in WSL and run with `PYTHONHOME`
set; nothing is installed system-wide and nothing is committed to the repo. `README` for
re-obtaining them is in `RESULTS.md` §8.

---

## 8. What this run explicitly does NOT cover (declared in advance)

- seeds outside the 2,165-entry B-04 dictionary (the amd64 branch is a sample of an unbounded
  space, per Q3)
- the complete 2³² i386 image (specified in `READY.md`, not run here)
- `PYTHONHASHSEED` / `-R` randomised-hash runs (a randomised hash is unreproducible by the
  author too, so it cannot be the pad's derivation — but it is *not searched*, it is *argued
  away*, and that argument is recorded as an assumption, not a measurement)
- Python 2.6 and Python 2.5 (`string_hash` is the same, but `random.py`'s `randrange` and the
  `_randbelow` boundary differ across the 2.x line; 2.6 is Ubuntu 10.04's system Python and is
  a named extension)
- `random.WichmannHill` (2.x's legacy generator, still importable in 2.7) — a named extension
- `os.urandom`-seeded and unseeded runs (no seed ⇒ no key; doctrine's optimism-clause branch)
- filters other than the pinned soft key-skip; composite plaintext transforms; per-line restarts
