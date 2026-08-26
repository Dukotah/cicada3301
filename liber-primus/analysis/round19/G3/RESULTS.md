# ROUND 19 / G3 — RESULTS
### Python 2.7 `random.seed(<string>)` — closing the silent coverage hole

_Lane G3, Phase 1 of `analysis/round19/CAMPAIGN-PLAN.md`. Pre-registration: `PREREG.md`,
written before any keystream was produced. Binding: `liber-primus/ARMADA-DOCTRINE.md`._

> **What this lane delivers, and what it does not.** It delivers a Python-2.7 keystream
> generator **validated byte-exactly against real CPython 2.7 interpreters**, a keystream
> interface, a precise space statement, a correction to two ledger entries, and a Phase-2 run
> spec. It delivers **no negative and no coverage**: per the campaign's hard dependency, Phase 0
> (I1/I2/I3) owns the decoder, the adjudicator and the bar, and this lane **held at the scoring
> boundary**. The only decodes it ran are a pre-registered, labelled **plumbing pilot** (§7).

---

## 1. Headline

**We got a real Python 2.7 — in fact three of them, including the era-correct one.**

| build | what it is | `sizeof(long)` |
|---|---|---:|
| **2.7.3** `python2.7_2.7.3-0ubuntu3.19_amd64`, `[GCC 4.6.3]` | **Ubuntu 12.04 LTS's system Python** — the exact interpreter L1's prior points at | 64 |
| **2.7.3** `..._i386`, `[GCC 4.6.3]` | the same package, **32-bit**, `sys.maxint == 2147483647` | **32** |
| **2.7.18** `python2.7_2.7.18-13ubuntu1.5`, `[GCC 11.4.0]` | independent second build, 12 years and a different compiler later | 64 |

`gen_py27.py` reproduces all three **element-for-element with zero failures** over the entire
2,165-entry B-04 seed dictionary. The generator is **VALIDATED**, not provisional, on both the
64-bit and the 32-bit branch.

And the gap L1 §6.3 predicted is real and total: over 600 dictionary seeds compared,
**600 of 600 Python-2.7 streams differ from the Python-3 stream for the same literal, 0 agree.**

---

## 2. What Python 2.7 actually does, versus Python 3

### 2.1 Python 2.7 — `Modules/_randommodule.c`, `random_seed()`

```c
    if (PyInt_Check(arg))        n = |arg|;          /* int  */
    else if (PyLong_Check(arg))  n = |arg|;          /* long */
    else {
        long hash = PyObject_Hash(arg);              /* <-- the whole difference */
        if (hash == -1) goto Done;
        n = PyLong_FromUnsignedLong((unsigned long)hash);
    }
    /* split n into 32-bit chunks, from the right */
    while (PyObject_IsTrue(n)) { key[keyused++] = n & 0xffffffff; n >>= 32; }
    if (keyused == 0) key[keyused++] = 0UL;
    result = init_by_array(self, key, keyused);
```

`Lib/random.py` (2.7) `Random.seed(self, a=None)` passes a `str` **straight through** to
`super(Random, self).seed(a)`. There is **no `version` parameter and no digest step** — the
2.7 signature is `seed(a=None)`, full stop.

`Objects/stringobject.c`, `string_hash()` (2.7), in signed `long` arithmetic:

```c
    if (len == 0) return 0;
    x  = _Py_HashSecret.prefix;        /* 0 — randomisation OFF unless -R / PYTHONHASHSEED */
    x ^= *p << 7;
    while (--len >= 0) x = (1000003*x) ^ *p++;
    x ^= Py_SIZE(a);
    x ^= _Py_HashSecret.suffix;        /* 0 */
    if (x == -1) x = -2;
```

**Net effect:** a `str` seed collapses to **one machine `long`**, and MT19937 is initialised
from **at most two 32-bit key words** (amd64) or **exactly one** (i386).

### 2.2 Python 3 — `Lib/random.py`, `Random.seed(a, version=2)`

```python
    if version == 2 and isinstance(a, (str, bytes, bytearray)):
        if isinstance(a, str): a = a.encode()
        a = int.from_bytes(a + _sha512(a).digest(), 'big')
    super().seed(a)
```

≥ 576 bits ⇒ **≥ 18 `init_by_array` key words**, and `hash()` never enters the path at all
(which is just as well: Python 3.3+ turns hash randomisation **on** by default, so the Py2
route would not even be reproducible under Py3 defaults).

### 2.3 Measured, on the literal `"CICADA3301"`

| quantity | value |
|---|---|
| `hash("CICADA3301")` on real **2.7.3 amd64** | `8810433306790406628` |
| `hash("CICADA3301")` on real **2.7.3 i386** | `-1333581340`  (unsigned `2961385956`) |
| Python-2.7 `init_by_array` key, amd64 | `[2961385956, 2051338857]` — **2 words** |
| Python-2.7 `init_by_array` key, i386 | `[2961385956]` — **1 word** |
| Python-3 `init_by_array` key | 18 words derived from `b"CICADA3301" + sha512(...)` |
| Py2.7 `randrange(29)` stream, first 16 | `0 17 2 22 9 22 27 11 10 13 27 11 28 5 26 22` |
| **Py3** `int(random()*29)` stream, first 16 | `24 24 26 0 21 21 20 20 6 26 26 14 24 17 25 16` |

Full pinned vectors for seven canonical literals are in `validation.json` → `vectors.pinned`.

### 2.4 A structural fact that bounds the whole family

`string_hash` is built only from multiplication and XOR, both of which preserve low bits.
Therefore **the i386 hash is exactly the low 32 bits of the amd64 hash** — i.e. the 32-bit
seed image is the *first key word* of the 64-bit one. Measured, not asserted:
**2,165 / 2,165 dictionary seeds satisfy `low32(hash64) == hash32`, 0 exceptions.**
For **32** of the 2,165 the 64-bit hash is itself < 2^32, so amd64 and i386 produce the
*identical* MT state for those seeds.

Consequence, and it is the most useful thing this lane found:

> **On a 32-bit Python 2.7, the entire space of string-seeded pads is `init_by_array([w])`
> for `w` in `[0, 2^32)` — a fully enumerable 2^32 space, regardless of what the string was.**
> No dictionary is needed to cover it. Python 3 has no such collapse.

### 2.5 The other Python-2-only / Python-2-different constructs

| construct | 2.7 behaviour | vs Python 3 | validated |
|---|---|---|---|
| `randrange(29)` | `_int(self.random()*29)` (`Lib/random.py`: `_randbelow` only when `width >= 2**53`) | Py3 `randrange` is `_randbelow` = `getrandbits(5)` **with rejection** — a different stream | V5, measured on real 2.7.3 |
| `randint(0,28)` | `randrange(0,29)` => **identical to the above** | same divergence | V5 |
| `choice(pool29)` | `seq[int(random()*len(seq))]` => **identical to the above** | Py3 `choice` uses `_randbelow` | V5 |
| MT words per rune | **2** (`genrand_res53`), no rejection | Py3 `randrange`: 1 per attempt, with rejection | V2 |
| `shuffle(x)` | `j = int(random()*(i+1))` Fisher–Yates | Py3 `shuffle` uses `_randbelow` => **different stream even for an integer seed** | V2 + §4.3 |
| `jumpahead(n)` | `s = repr(n) + repr(self.getstate()); n = int(sha512(s).hexdigest(),16); super().jumpahead(n)` — the **repr of all 625 state words** (each with an `L` suffix; they are `PyLong_FromUnsignedLong` objects) is SHA-512'd | **removed in Python 3** | V4 |
| `seed(<non-negative int>)` | `abs(n)` -> 32-bit chunks -> `init_by_array` | **identical to Python 3** | V4 + §4.3 |
| `seed(<float>)` | `_Py_HashDouble` | Py3 float hash uses the 2^61-1 modulus => different | V4 |
| `PYTHONHASHSEED` / `-R` | present from 2.7.3, **off by default** | Py3.3+ **on** by default | assumption, see §9 |

**So three of the four era-idiomatic rune reductions collapse onto one call under Python 2.7,
and it is not the one Python 3 collapses them onto.** A sweep that lists `randrange`,
`randint` and `choice` as three modes under Python 3 has tested one mode — the
`getrandbits`-with-rejection one — and has *not* tested `int(random()*29)` under those names.

---

## 3. Validation verdict

`validation.json` -> `verdict.all_blocking_gates_pass = true`,
`confidence_64bit = "VALIDATED against two real CPython 2.7 builds"`,
`confidence_32bit = "VALIDATED"`.

| gate | requirement (fixed in `PREREG.md` §4) | measured | verdict |
|---|---|---|---|
| **V1** | a real CPython 2.7 executes | 2.7.3 amd64 `[GCC 4.6.3]`, 2.7.18 amd64 `[GCC 11.4.0]`, 2.7.3 i386 `[GCC 4.6.3]` all ran | **PASS** |
| **V2** | `gen_py27` == real 2.7.3, 100 % | **2,165 / 2,165** `hash()` values, **8,660 / 8,660** streams (2,165 seeds x 4 reductions x 64 values). **0 failures** | **PASS** |
| **V3** | 2.7.3 == 2.7.18 | SHA-256 of the whole stream corpus identical: `b6d0179750c175665eeaa7208e2635b4205a6c409df94135a20b3ffce2c7f9b7`; all 2,165 `hash()` values identical | **PASS** |
| **V4** | `seed(int)`, `seed(float)`, `seed(str)+jumpahead(k)` exact | 5 int + 5 float (hashes *and* streams) + 4 jumpahead vectors, all exact | **PASS** |
| **V5** | reduction identity **measured**, not assumed | 24 seeds x 64 draws: `randrange == randint == choice == int(random()*29)` **true in all cases** | **PASS (measured)** |
| **V6** | Py2 != Py3 — the Q5 kill check | **600 compared, 600 different, 0 identical** | **PASS — lane is not a duplicate** |
| **V7** | i386 branch validated or PROVISIONAL | real i386 2.7.3 obtained: **400 / 400** hashes, **1,600 / 1,600** streams, 0 failures | **PASS — VALIDATED, not provisional** |
| **V8** | scorer-free plant-and-recover | planted `b"THE PRIMES ARE SACRED"` (`slogan`, dictionary-resident), `grb5_rej`, ws 64; searched **17,320** configs (2,165 x 4 reductions x 2 word sizes) by identity; **exactly 1 exact match**, the planted one | **PASS, recovery 1.000, uniqueness 1.000** |

**Honest caveat on V4.** The two `jumpahead` C-level variants (pre- and post-CPython
issue #14591) were also measured against each other and produce **identical** output outside
the all-zero-state degenerate case, so the gate confirms the wrapper but does **not**
discriminate the two point releases. Recorded in `validation.json` as
`jumpahead_variants_differ = false`.

**Reproduce.** The three interpreters are extracted (not installed) under `~/py27/` in WSL
from `old-releases.ubuntu.com` / `archive.ubuntu.com`; `PREREG.md` §7 lists the exact package
filenames, and `validate_py27.py` re-runs the whole gate in about 2 minutes.

---

## 4. Which B-04 cells this duplicates, and which it does not

### 4.1 B-04's generator set contains **no Mersenne Twister at all**

`round13/B04/ks.py`'s `GENERATORS` dict, read this lane, is exactly:

```
sha256_ctr  sha512_ctr  sha1_ctr  md5_ctr  sha256_ctr_le  sha256_ctr_asc
sha256_chain  sha512_chain  sha1_chain  md5_chain
hmac_sha256_ctr  hmac_drbg_sha256  rc4  aes_ctr_zeroiv  aes_ctr_deriviv  chacha20
```

Sixteen keyed hash / stream-cipher constructions. **Zero MT19937 cells.** So on the
*generator* axis this lane duplicates **none** of B-04's 6,224,300 decodes.

The nearest-looking pair is a false friend, worth naming so nobody re-derives it later:
B-04's `sha512_chain` / `sha512_ctr` emit **SHA-512 digest bytes directly**, whereas Python 3's
string seeding uses SHA-512 only to *build an `init_by_array` key*; the emitted stream is
MT19937 output. They share a primitive and share no output.

### 4.2 What this lane **does** reuse from B-04 (deliberately, for comparability)

| axis | reused verbatim |
|---|---|
| seed dictionary | `round13/B04/seeds.py`, **2,165** entries (core subset **504**) — imported, **not rebuilt** |
| reductions to Z29 | conceptually parallel to B-04 §3.3, but the Python-2.7-idiomatic set (§2.5) rather than the byte-fold set |
| sign / direction / Atbash | B-04 §3.4 unchanged |
| offsets | B-04 §3.5's ten values, for Stage B |
| segment lengths | B-04's `HEAD_L = 120`, `PAGE_L = 100` |

### 4.3 The MT19937 cells that **are** already covered — and a correction to the ledger

Per doctrine mechanic 9, and following lane **G2**'s finding that L1's "never swept" labels are
not reliable, this lane checked its own family in `analysis/seed_sweep/` and
`analysis/round10/L5-seed32/` **before** claiming new ground. It found prior coverage, and it
found the ledger describing that coverage incorrectly.

**`analysis/seed_sweep/results_full32.txt` (mtime 2026-08-17) contains 9 completed
full-32 generator rows, not 2.** Verbatim:

```
gen=3 MSVC rand()%29                 seeds=0..4294967296  best=-12.8472  hits>-12.5=0
gen=5 mt19937 init_genrand %29       seeds=0..4294967296  best=-12.7947  hits>-12.5=0
gen=7 py3 seed(int) randrange(29)    seeds=0..4294967296  best=-12.7374  hits>-12.5=0
gen=9 java Random.nextInt(29)        seeds=0..4294967296  best=-12.8540  hits>-12.5=0
gen=1 glibc random() scaled          seeds=0..4294967296  best=-12.6432  hits>-12.5=0
gen=4 MSVC rand() scaled             seeds=0..4294967296  best=-12.9618  hits>-12.5=0
gen=6 mt19937 init_genrand double    seeds=0..4294967296  best=-12.9238  hits>-12.5=0
gen=8 py3 seed(int) int(random()*29) seeds=0..4294967296  best=-12.9764  hits>-12.5=0
gen=2 glibc random()%29 +norepeat    seeds=0..4294967296  best=-13.0274  hits>-12.5=0
```

**Correction, filed as G2 filed theirs:**

| ledger text | measured state on disk, 2026-08-26 |
|---|---|
| **B-01** — "The full 32-bit sweep is 2/10 complete... gen=0 ... is absent, and no `DONE` line"; `evidence_missing: ["run_full32.sh"]` | **9 of 10 complete.** `gen=0` (glibc `random()%29`) is indeed still absent and there is still **no `DONE` line** — but seven more generators finished after B-01 was filed (2026-08-12; the file's mtime is 2026-08-17). `run_full32.sh` **does exist** at `analysis/seed_sweep/run_full32.sh`, so `evidence_missing` is stale too. |
| **B-21** — "10 integer-seeded generators over **~3 %** of each seed space (only 2 swept fully)" | **9 of 10 swept fully over `0..2^32`.** The "~3 %" figure now describes only `gen=0`. |
| **`round10/L5-seed32/CENSUS.md` §A** | its "Seed space swept" column understates rows 1, 2, 4, 6, 7, 8, 9 — all are full-32 on disk. |

**Now the part that matters for G3.** Two of those nine rows are CPython cells that coincide
exactly with two of this lane's four reductions **on the integer-seed axis**. Measured
in-process, not assumed:

```
int seed: py2 int(random()*29) == py3 int(random()*29) : True
int seed: py2 grb5_rej         == py3 grb5_rej         : True
int seed: py2 grb5_mod         == py3 grb5_mod         : True
int seed: py2 shuffle29        == py3 shuffle29        : False
py3 randrange(29) == py3 getrandbits(5)-reject         : True
py3 randrange(29) == py3 int(random()*29)              : False
```

(over seeds `0, 1, 3301, 12345, 1387498126, 2^31, 2^32-1`; `seed(<non-negative int>)` is
byte-identical in 2.7 and 3.x, so these equalities are exact, not statistical.)

Therefore:

| G3 cell | duplicate of | coverage there |
|---|---|---|
| `seed(<int>)` + **`random29`** (= Py2 `randrange`/`randint`/`choice`) | Round 8 **gen=8** "py3 seed(int) int(random()*29)" | **full `0..2^32`** — DUPLICATE |
| `seed(<int>)` + **`grb5_rej`** | Round 8 **gen=7** "py3 seed(int) randrange(29): getrandbits(5) reject" | **full `0..2^32`** — DUPLICATE |
| `seed(<int>)` + `grb5_mod` | — | not in Round 8's ten; **NOT covered** |
| `seed(<int>)` + `shuffle29` | — | Py2-only stream; **NOT covered** |
| `seed(<str>)` + any reduction | — | **NOT covered by anything** — see §4.4 |
| `seed(<float>)`, `seed(str)+jumpahead(k)` | — | **NOT covered** |
| any of the above at **wordsize 32** | — | **NOT covered** |

Also duplicated in spirit but not in stream: `round10/L5-seed32` **gen=12** "ruby rand(29) MT
mask" (MT19937 via `init_genrand`, 5-bit mask/reject, 2011–2015 unix seconds). Ruby uses
`init_genrand`, CPython uses `init_by_array`; the two never share a state.

**But every one of those duplicates was swept with a broken magnet**, exactly as G2 found for
Perl. `analysis/seed_sweep/sweep.c`'s `decode_score()` is a **rigid** decoder — it branches
only over `F`-rune interrupter nulls and has **no key-skip transition at all** — scored by a
**mean English 4-gram** against a **fixed `-12.5` bar** on that track's own scale. `LEDGER`
B-21 says the same in one line: *"Round 8 also used RIGID decode throughout."* Round 12/D3
measured what rigid costs on the pinned filtered construction: the **correct** key scores
**-6.835** rigid versus **-4.170** beam, i.e. indistinguishable from noise. So gen=7 and gen=8's
full-32 coverage is coverage at approximately **zero power** for LP2's construction, and at
L7-A's **English-only** register. That makes them a re-adjudication target for **S2**, not a
closed cell.

### 4.4 The string-seed track, and a documented false claim

`analysis/seed_sweep/string_seeds.py` is the only prior MT19937-from-a-string work
(15,408 decodes; `string_seed_results.json`: `best -14.689`, `hits 0`). Its module docstring says:

> *"Also covers `random.seed()` with the same wordlist under **Python 2 semantics
> (hash() of the string)**, and the numeric seeds of lore significance at full precision."*

**No such code exists in the file.** Its only seeding call is `r.seed(seedval)` inside
`stream()`, executed by the repository's Python 3; the "Python 2" candidates are
`w.encode()`, i.e. `bytes` — which Python 3 routes through the *same* `int.from_bytes(a +
sha512(a).digest())` path as the `str`, making them **exact duplicates** of the `str` entries
rather than a Python-2 arm. (That also means the 1,284 candidates behind the 15,408 figure
carried roughly 50 % redundancy on the string families.)

This is the silent coverage hole L1 §6.3 item 2 predicted, now located and closed at the
generator level: **V6 measured 600/600 divergence**, so nothing in those 15,408 decodes touched
the Python-2 string path.

---

## 5. Space accounting

### 5.1 The axes

| axis | size | enumerable? |
|---|---|---|
| seed dictionary (B-04, reused) | **2,165** (core **504**) | complete over the dictionary |
| build word size in {64 (amd64), 32 (i386)} | **2** | complete |
| derivation in {`seed(str)`, `seed(str)`+`jumpahead(k)` for k in {29,761,1033,3301}, `seed(float)`, `seed(int)`} | 4 families | complete |
| reduction in {`random29`, `grb5_mod`, `grb5_rej`, `shuffle29`} | **4** | complete |
| sign x direction x Atbash | **8** | complete |
| offset (Stage A pinned 0; Stage B = B-04's ten) | 1 / 10 | complete |

Stage A `2,165 x 2 x 4 x 8 =` **138,560**; Stage A' (jumpahead) `504 x 2 x 4 x 4 x 8 =`
**129,024**; Stage B (offsets) `504 x 2 x 2 x 10 x 8 =` **161,280** => **about 4.3 x 10^5**.
Three orders of magnitude below B-04's 6.22 M, because the prior is doing the work
instead of the volume (doctrine R4).

### 5.2 Enumerable versus samplable — and which branch carries the prior

- **i386 branch: ENUMERABLE.** By §2.4 the 32-bit string-seed image is `init_by_array([w])`,
  `w` in `[0, 2^32)`. **4,294,967,296 states covers every string, every float and every
  non-int seed a 32-bit Python 2.7 could ever have been given** — the dictionary is a
  convenience there, not a limit. That is the same size as the full-32 sweeps this repository
  has already completed nine times (§4.3).
- **amd64 branch: SAMPLABLE.** The image is at most 2^64, and the 2,165-entry dictionary is a
  2.17 x 10^3 point sample of it. Any negative there is worth what B-04's is: it closes a
  dictionary, not a family.

**Which branch carries more prior?** The **i386 branch**, on two grounds and against one:

1. **Era.** Through the Ubuntu 11.04–12.04 period the *default* desktop download was the
   32-bit (i386) ISA image; amd64 was offered but was the minority desktop install, and Ubuntu
   did not make 64-bit the recommended desktop download until after 2012. An author on the
   L1-inferred box is more likely than not to have been running a 32-bit userland.
2. **Tractability.** It is the branch that is *enumerable*, and doctrine R5 ranks an
   enumerable generator space second only to a finite human-checkable object.

Against: this is a **population-level inference about 2012 Ubuntu desktops, not a measurement
on a 3301 artifact**, so it does not meet doctrine R4's evidence bar and is recorded as a
**search-ordering heuristic only**. Nothing in L1's F1–F10 discriminates the author's word
size. That is a named, reopenable gap (§8, NC-2). **Both branches are in Stage A regardless;
the heuristic only sets the order.**

### 5.3 Coverage x power (doctrine R2)

| quantity | value |
|---|---|
| key space **cleared** by this lane | **0 decodes.** The pilot is not coverage (§7) |
| enumerator recovery (V8) | **1.000** — planted config recovered, exactly and uniquely, over 17,320 configs, using **no decoder and no adjudicator** |
| generator fidelity | **1.000** — 10,825 vectors against real CPython 2.7, 0 failures |
| **decoder x adjudicator power for this hypothesis class** | **UNMEASURED BY G3.** It is I1's and I2's to measure and I3's to threshold. L7-A (0.33 Latin / 0.00 no-vowel) and L7-B (`skip_by_two` at -6.90 / 25.8 %) are the standing measurements of the *old* instrument, and lane **G2** measured that under I1's `drift3` / `union0_5` modes **pure random data** scores **-4.51 / -4.82**, so the historic -5.5 bar is invalid there. |

Product: **coverage x power = 0 x (unmeasured) = 0.** This lane has excluded nothing and
claims to have excluded nothing. What it has done is make a previously unreachable region
*reachable at a measured generator fidelity of 1.000*.

---

## 6. The three conditionals any G3-derived negative must carry (doctrine Q4)

1. **Key space** — the 2,165-entry B-04 dictionary under Python-2.7 semantics, over the
   §5.1 cross-product, offset 0 (Stage A) or B-04's ten offsets (Stage B). **Not** the 2^32
   i386 image; **not** seeds absent from the dictionary; **not** `PYTHONHASHSEED`-randomised runs.
2. **Decoder transition model** — whatever `round19/I1/driftbeam.py` mode the sweep row records
   (`keyskip1` / `keyskip2` / `permissive`, with `max_free`, `lam`, `beam_w`, `max_skip`). The
   pre-I1 beam is L7-B-defective for this class and must not be used.
3. **Adjudicator register** — `round19/I2/adjudicate.py`'s nine-register panel
   (`EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL`) plus the four
   doctrine-R3 statistics, at the panel build stamped in the SWEEPROW header.

---

## 7. The labelled plumbing pilot (PREREG §6, the sole pre-registered exception)

`round19/I1/driftbeam.py` and `round19/I2/adjudicate.py` both existed when the generator was
finished, so the pre-registered pilot was unlocked. **It is a timing measurement. It is not
evidence, it produces no negative, and its best score is a plumbing artefact.**

```
decodes                     9,600   (150 B-04 core seeds x 4 reductions x ws{64,32}
                                     x dir{fwd,rev} x sign{-1,+1} x atbash{off,on}, offset 0)
wall clock                  191.9 s single core
throughput                  50.0 decodes/s/core  =  19.99 ms/decode
decoder                     I1 driftbeam mode=keyskip1, beam_w=400, max_skip=3, L=120
adjudicator                 I2 adjudicate(), 9-register panel, panel_build 2026-08-26T11:10:41
store                       pilot.jsonl, 1,683,895 bytes
adjudicate.validate_store   PASS — 9,600 / 9,600 rows validated against SWEEPROW/1
```

Distribution over the 9,600 rows (all presumed wrong under H0):

| statistic | mean | sd | max |
|---|---:|---:|---:|
| `en` (legacy English quadgram) | -7.3416 | 0.2292 | **-6.4955** |
| `pmax` (max over the 9-register panel) | 1.6422 | 0.7943 | **5.0290** |
| `pmax_ne` (best non-English) | 1.5790 | 0.7861 | 4.9940 |
| `pcon` (selection-corrected) | 1.4330 | 0.6993 | 4.3790 |
| `ioc` | 1.0045 | 0.0641 | 1.3241 |
| `mds` | 16.48 | 1.13 | 20 |

Two things worth carrying into Phase 2. The `en` column reproduces B-04's null almost exactly
(B-04 measured mean -7.366 / max -6.826 at L=120), which is an independent confirmation that
the plumbing is wired to the same scale as every published number in this repository. And
`pmax` reaches **5.03 in 9,600 decodes of pure noise** — precisely the false-positive inflation
I3 exists to calibrate. **This lane sets no bar and asserts none.**

---

## 8. Coverage — what was measured, and what was NOT

**Measured (this lane).**

- Three real CPython 2.7 interpreters obtained and executed: 2.7.3 amd64, 2.7.3 i386, 2.7.18 amd64.
- **10,825** reference vectors against real 2.7.3 (2,165 `hash()` + 8,660 stream), 0 failures;
  the same corpus reproduced identically by 2.7.18; 2,000 more against real i386 2.7.3.
- The `randrange` / `randint` / `choice` / `int(random()*29)` identity, measured on real 2.7.3.
- 600 Py2-vs-Py3 stream comparisons: 600 different, 0 identical.
- `low32(hash64) == hash32` over all **2,165** dictionary seeds, 0 exceptions.
- Py2-vs-Py3 equality on the **integer**-seed axis for 4 reductions x 7 seeds.
- A scorer-free identity plant-and-recover over **17,320** configs: 1 match, the planted one.
- A 9,600-decode labelled pilot end-to-end through I1 + I2, `validate_store` PASS.
- The current on-disk state of `analysis/seed_sweep/results_full32.txt` (9 rows, no `DONE`,
  `gen=0` absent) and of `string_seeds.py` (no Python-2 arm despite its docstring).

**Not covered, and the concrete condition that reopens each.**

| # | not covered | reopens if |
|---|---|---|
| **NC-1** | **Everything downstream of the generator.** No key space is cleared: 0 decodes of coverage. | S1 runs the `READY.md` spec through I1 + I2 at I3's published threshold |
| **NC-2** | **The author's word size.** §5.2's preference for i386 rests on 2012 Ubuntu desktop-install population statistics, not on a 3301 artifact. | any artifact discriminates a 32- from a 64-bit userland — an ELF, a `uname` string, a `long`-width-dependent number in a released file |
| **NC-3** | **The full 2^32 i386 image.** Specified in `READY.md` §4 as an optional extension; not run here. | someone spends the ~4.3 x 10^9-state budget; §4.3 shows nine comparable sweeps have already been afforded on this box |
| **NC-4** | **Seeds outside the 2,165-entry dictionary on the amd64 branch.** | the dictionary is extended, or NC-3's enumeration subsumes the 32-bit half |
| **NC-5** | **`PYTHONHASHSEED` / `-R` randomised-hash runs.** Argued away (a randomised hash is unreproducible by the author too, so it cannot be a pad derivation) — **argued, not searched.** | the pad is shown to be non-reproducible-by-design, e.g. the author published a seed but not a salt |
| **NC-6** | **Python 2.6 / 2.5** (Ubuntu 10.04's system Python is 2.6). `string_hash` is unchanged, but `Lib/random.py`'s `randrange` and the `_randbelow` boundary move across the 2.x line. | a 2.6 interpreter is obtained; `validate_py27.py` re-runs unmodified against it |
| **NC-7** | **`random.WichmannHill`** — 2.x's legacy generator, still importable in 2.7 and a plausible choice for an author who wanted "the old one". | it is added to `REDUCERS`; about 20 lines, and it validates against the same interpreters |
| **NC-8** | **`os.urandom`-seeded and unseeded runs.** No seed => no key. | nothing; this is the doctrine §5 branch that no compute reaches |
| **NC-9** | **Non-zero offsets beyond B-04's ten, per-page and per-line restarts**, and filters other than the pinned soft key-skip. | B-02 (the offset ladder) or a filter-variant lane runs |
| **NC-10** | **The `jumpahead` point release.** The pre-/post-issue-#14591 variants were measured to be output-identical outside a degenerate case, so 2.7.3 vs 2.7.4+ is **not** discriminated. | a state is found where they diverge (all of `mt[1..623]` zero) — measure-zero in practice |

**Reopen condition for the lane as a whole.** This lane is *open by construction*: it built a
validated instrument and cleared nothing. It closes only when S1 has run `READY.md` §2–§3
through I1 + I2 at I3's published threshold and reported the three conditionals of §6.

---

## 9. Assumptions recorded as assumptions (not measurements)

1. **Hash randomisation was off.** 2.7 ships `-R` / `PYTHONHASHSEED` from 2.7.3 but defaults to
   off, and a randomised hash would make the author's own pad unreproducible. Reasonable —
   and unverified. NC-5.
2. **The seed was a `str` literal in source, not a runtime value.** The dictionary hypothesis
   is B-04's, inherited wholesale.
3. **32-bit userland is more likely than 64-bit for a 2012 Ubuntu desktop.** §5.2, NC-2.
4. **2.7.3 is the right point release.** L1 fixes Ubuntu 11.04–12.04; 11.04 / 11.10 shipped
   2.7.1 / 2.7.2. V3 shows the seeding path is invariant across 2.7.3 -> 2.7.18, which makes the
   point release very unlikely to matter, but 2.7.1 / 2.7.2 were not executed. Adjacent to NC-6.

---

## 10. Reproduce

```bash
# 1. obtain the interpreters (PREREG.md §7 lists the exact package names)
#    -> ~/py27/root273   root273_i386   root2718      (extracted, never installed)

# 2. the gate  (~2 min; writes validation.json)
wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round19/G3 \
  && python3 validate_py27.py"

# 3. the generator, standalone
python3 gen_py27.py --emit --seed CICADA3301 --mode random29 --wordsize 64 --n 40
python3 gen_py27.py --emit --seed CICADA3301 --mode random29 --wordsize 32 --n 40

# 4. the labelled pilot (NOT evidence)
python3 pilot.py --seeds 150 --out pilot.jsonl
```

**Trust anchor.** `python3 liber-primus/tests/validate.py` -> `ALL VALIDATIONS PASSED` (5/5),
run **before** the lane (recorded in `PREREG.md`) and **after** (recorded in `ledger.json`).
