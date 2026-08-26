# ROUND 19 / G1 — RESULTS

_Lane G1, Phase 1 of [`round19/CAMPAIGN-PLAN.md`](../CAMPAIGN-PLAN.md). Pre-registration:
[`PREREG.md`](PREREG.md), written before any measurement. Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Trust anchor, before and after:** `python3 liber-primus/tests/validate.py` →
`ALL VALIDATIONS PASSED — rig reproduces known solves` (5/5).

> **This lane produced NO negative and NO verdict about LP2.** It produced validated
> generators, a measured space, and a run specification. Per the round's hard dependency
> it stopped at the scoring boundary. The one thing it scored is a **plant**, labelled as
> such in §6.

---

## 1. Headline

**All 19 generators reproduce the real library byte-for-byte, including the era-correct
ones against a real GNU bash 4.2.0 binary and the real system glibc. The bash `$RANDOM`
space is genuinely enumerable and is smaller and stranger than the flat "2³² seeds" the
plan assumed — it is ONE ORBIT, and *seed and keystream-offset are the same axis*.**

Four measured things this lane did not expect to find, each of which changes how Phase 2
should be run:

| # | measurement | consequence |
|---|---|---|
| **M1** | `brand()` is a pure state map and `RANDOM=<seed>` writes the state directly. Sliding-window identity **verified** for four variants. | For every bash generator, **seed ≡ offset**. LEDGER **B-02** ("every sweep assumed key index 0 = rune 0") is not a separate lane here; a full seed enumeration already *is* the offset ladder. |
| **M2** | bash 4.2 on **LP64** has cycle length **2,147,483,646** with a tail of only 13–72. On **ILP32** the cycle collapses to **343,896** with tails of 210k–500k. | The 32-bit and 64-bit builds of the *same* shell are different generators with wildly different structure. Both were shipped by Ubuntu 12.04; both must be swept. The ILP32 period (26× the book) is a *testable signature* if a longer ciphertext ever surfaces. |
| **M3** | bash **4.0/4.1** call `seedrand()` (`gettimeofday ^ getpid`) when the state reaches 0 — and state 0 **is reachable**: `RANDOM=2147483647` reaches it in ONE step. bash **4.2** replaced that with the constant `123459876`. | 4.0/4.1's `$RANDOM` is **not sweepable past that point**; only a deterministic prefix exists. 4.2 — the era-correct version — is fully deterministic. This is a genuine difference between two adjacent releases, and it is why "bash `$RANDOM`" is not one object. |
| **M4** | `$RANDOM`'s public entry point has **always** been `do rv = brand(); while (rv == last_random_value);` — a rejection loop, in the standard library of the shell L1 puts on the author's box. | Noted, **not** offered as evidence. At 15-bit granularity it suppresses ~1/32768 of draws and cannot produce LP2's mod-29 doublet deficit (0.664 % vs 3.45 % expected). It is a shape-match, nothing more. |

---

## 2. Validation verdicts — the gate (`validation.json`)

Every generator, 8 pre-registered seeds `{0, 1, 2, 3301, 12345, 2147483647, 4294967295,
1376006400}` × **2,000 draws**, compared element-for-element.

| generator | reference | level | verdict | era-correct |
|---|---|:--:|:--:|:--:|
| **`bash4.2`** | **a REAL `GNU bash, version 4.2.0(2)-release (x86_64…)` binary**, built from `ftp.gnu.org/gnu/bash/bash-4.2.tar.gz` | **L1** | **PASS** | ✔ |
| `bash5.1` | the running system shell, `GNU bash 5.3.9(1)-release` | **L2** | **PASS** | — |
| `glibc_random` | real glibc via `ref_glibc.c` (`Ubuntu GLIBC 2.43-2ubuntu2`) | L3 | **PASS** | ✔ |
| `glibc_rand` | ditto | L3 | **PASS** | — |
| `glibc_initstate8 / 32 / 64 / 256` | ditto (TYPE_0/1/2/4 via `initstate()`) | L3 | **PASS** | — |
| `lrand48` | ditto | L3 | **PASS** | ✔ |
| `mrand48` | ditto | L3 | **PASS** | — |
| `drand48_x2p53` | ditto, compared as the exact 53-bit mantissa integer (no fp fuzz) | L3 | **PASS** | ✔ |
| `openssl_enc_rc4_k` | the real `openssl` binary (3.5.5, legacy provider) | L3 | **PASS** | — |
| `shuf_random_source` | the real **GNU** `shuf` binary (coreutils 9.7), as an **oracle** | L3 | **PASS** | — |
| `bash4.2_i32` | `ref_bash.c`, bash 4.2 source re-typed for ILP32 | L4 | **PASS** | ✔ |
| `bash3.2`, `bash3.2_i32`, `bash4.0`, `bash5.0`, `bash5.1c50` | `ref_bash.c`, verbatim from the released sources | L4 | **PASS** | — |

**GATE: PASS. 19/19. Zero failures, era-correct or otherwise.**

Two things the gate caught that a self-consistent reimplementation would have shipped
silently:

- **The glibc `random()` recurrence.** The obvious linear form `r[i] = r[i−31] + r[i−3]`
  — and its sibling `r[i−31] + r[i−28]` — **both fail**. glibc's `__random_r` is a
  circular buffer with `fptr` starting at `state[sep]` and `rptr` at `state[0]`,
  advancing with a specific wrap rule, and only writing it out literally reproduces the
  library. This is exactly the class of error Round 8's harness gates existed to catch.
- **bash 4.0's absorbing zero.** The first C reference hung forever, because
  `brand()` returns 0 at state 0 while `get_random_number()`'s anti-repeat loop refuses
  to return the same value twice. The real bash resolves that by re-seeding from the
  clock — which is the finding (M3), not a bug in the harness.

**Reference-strength honesty.** `bash4.2` is validated at **L1**, against a real binary
of the era-correct version. `bash4.2_i32` is **L4**: `gcc-multilib` is not installed on
this box, so no `-m32` build exists; the ILP32 model is the same bash source re-typed
with `uint32_t`/`int32_t`, which is what an ILP32 compiler emits, but the validating
artefact is a transcription, not a 32-bit binary. That is recorded in `validation.json`
and it is the weakest link in this lane.

---

## 3. The space accounting

### 3.1 What bash `$RANDOM` actually is

`RANDOM=<value>` → `assign_random()` → `sbrand(strtoul(value, NULL, 10))` → `rseed =
value`. The seed **is** the state. `brand()` is a pure map. Therefore the set of distinct
`$RANDOM` keystreams is the set of **orbits** of that map, and picking a seed is picking
an entry point into one.

Verified, not assumed: `validation.json.internal_consistency.sliding_window_*` shows
`window(master_orbit, i, n) == raws(state_at_index_i, n)` for `bash4.2`, `bash4.2_i32`,
`bash3.2` and `bash5.1`. That identity is what turns a 2³¹-seed enumeration into one pass
over a 2.1e9-element array — **O(2³¹ + L) instead of O(2³¹ · L)** — measured at 5,403
windows/s in pure Python and trivially vectorisable.

### 3.2 Orbit structure (measured with Brent's algorithm, `orbit.c`; raw output in `orbit_measured.txt`)

| variant | start states probed | cycle length | tail |
|---|---|---:|---:|
| `bash4.2` (LP64) | 1, 2, 3301, 12345, 123459876, 1376006400, 2³¹−1, 2³²−1 | **2,147,483,646** (= 2³¹ − 2) | 13 – 72 |
| `bash4.2_i32` (ILP32) | same 8 | **343,896** | 210,014 – 499,658 |
| `bash3.2` (LP64) | — | **not measured**: full-period LCG mod 2⁶⁴ (Hull–Dobell: multiplier ≡ 1 mod 4, increment odd), so Brent needs 2⁶⁴ steps. *Analytically*, bits 16–30 of an LCG mod 2^m repeat with period 2³¹, so the 15-bit output period is 2³¹. **Stated, not measured.** |
| `bash3.2_i32` (ILP32) | 1, 2, 3301 | **4,294,967,296** (= 2³²) | **0** — confirms the full-period LCG mod 2³², matching the analytic prediction in the row above |
| `bash5.0` (= `bash5.1`'s state map) | 1, 2, 3301 | **2,147,483,646** (= 2³¹ − 2) | **0** — the textbook Lehmer generator mod 2³¹−1: one cycle covering every nonzero state, no transient. `bash5.1` folds the output but does not change the state map, so this row covers both |

**G1-ORB (kill condition K2) PASSES**: no era-correct variant has a cycle shorter than
the 12,956-rune unsolved stream. The ILP32 cycle at 343,896 clears it by only 26×, which
is worth recording — a 32-bit Ubuntu 12.04 box could not have produced a
non-self-repeating `$RANDOM` pad longer than 343,896 symbols.

**A caveat the sliding window carries.** Seeds reach the cycle only after a tail. For
`bash4.2` LP64 the tail is 13–72 draws, so a 120-symbol keystream from an off-cycle seed
contains a transient prefix that a pure cycle-window sweep would miss. For
`bash4.2_i32` the tails are *enormous* (210k–500k), so essentially every plausible seed
sits in a transient tree and the sliding-window shortcut buys nothing there. Since
keystream generation is 4 orders of magnitude cheaper than the decode either way, this
is a note, not a problem: S1 should generate per-seed and use the window trick only as an
optimisation where it is exact.

### 3.3 The auto-seeded subset — an evidence-derived priority ordering

bash 4.2 `initialize_shell_variables()` (`variables.c:537`) calls `seedrand()` at shell
start:

```c
gettimeofday (&tv, NULL);
sbrand (tv.tv_sec ^ tv.tv_usec ^ getpid ());
```

For a run between **2012-01-01** and **2014-06-01**, `tv_sec ∈ [1325376000, 1401580800]`,
`tv_usec < 10⁶ < 2²⁰`, and Linux's default `pid_max` is 32768 < 2¹⁵. The XOR therefore
only rewrites the **low 20 bits** of `tv_sec`, so the reachable seed set is
`{ (tv_sec & ~0xFFFFF) | v : v < 2²⁰ }` over **74** distinct high-prefixes:

> **74 × 2²⁰ = 77,594,624 seeds — 3.6 % of 2³¹.**

That is a *subset* of the full enumeration, so it excludes nothing on its own. Its value
is that it says **which 3.6 % to run first**, and it is derived from the author's own
platform evidence (L1 F6/F7) rather than from a guess. At the measured screen rate it is
**28 minutes of wall-clock on 16 cores**.

(For the record: a naive reading of the bash source suggests a top-level script that never
assigns `RANDOM` would start deterministically from `rseed = 1`. **That is wrong**, and
reading the source rather than the generator settled it — `seedrand()` at line 537 makes
the auto-seeded path time-and-pid-based. The hypothesis was killed before it cost
anything, which is what the Aiming Test is for.)

### 3.4 glibc

Seed space **2³² − 1** (`srandom(0)` ≡ `srandom(1)`, verified). The TYPE_3 state is 31 ×
32 bits, far larger than the seed, so there is **no orbit collapse and no sliding
window**: each seed costs O(10·deg + L) = O(430) to generate, which is cheap in C and
irrelevant next to the decode.

`rand()` **is** `random()` on glibc — measured over 8 seeds × 2000 draws
(`validation.json.internal_consistency.glibc_rand_is_random`), so S1 may collapse them
into one cell instead of two rather than assuming it.

`initstate()` at 8/32/64/256 bytes selects TYPE_0/1/2/4 and gives four more distinct
generators for one extra line of a 2012 C program. All four validated.

### 3.5 The reduction cross

6 reductions × 2 signs × 2 directions × 2 Atbash × 1 offset = **48 cells** per
`(generator, seed)` at Stage A, 240 at Stage B — following `round13/B04/PREREG.md`
§3.3–3.5 so G1's rows are comparable with B-04's, R16-PRNG's and R17's.

**`mod29` and `rej29` are near-aliases for a 15-bit source.** The rejection limit is
`(32768 // 29) × 29 = 32741`, so only **27 of 32,768** `$RANDOM` values are discarded.
The pilot shows the effect directly: the planted key's `mod29` and `rej29` rows score
*identically* to three decimals. For byte- or 31-bit-valued generators the two diverge
properly. The effective bash cell count is therefore ~40, not 48.

### 3.6 Prior coverage — what G1 does NOT re-run

| ledger entry | what its `coverage` field actually says | G1's position |
|---|---|---|
| **B-21** | 2.52e9 decodes, 10 generators over **~3 %** of each seed space; **RIGID decode throughout** | glibc `random()` is its generators 0/1/2. G1 does not re-run; it extends to 100 % and replaces the decoder |
| **B-01** | the full-32 sweep is **2/10 complete**; gen=0 (glibc) is **absent, no `DONE` line** | confirms the glibc full-32 pass never finished |
| **R16-PRNG** | 7 generators × 1,877 seeds; `not_covered` names "offsets != 0" and "full 2^32 (~0.004 % per generator)" | bash `$RANDOM` is **not among the 7** |
| **CENSUS §B gens 10/11** | Perl-`drand48` and POSIX `lrand48`, validated against the real binaries, 2011–2015 unix-seconds | **`lrand48` and `drand48` are already covered over that window. S1 must DE-DUPLICATE, not re-sweep.** G1 re-implements them only so the family sits behind one validated interface |
| **B-03 / B-08** | named-but-unswept generators and seed residue | `$RANDOM` appears in neither |

---

## 4. Which variants are era-correct for 2012 Ubuntu — the answer

L1's evidence (F6/F7: 46/46 signatures on `GnuPG v1.4.11 (GNU/Linux)`, the exact Ubuntu
11.04–12.04 package) fixes the platform. That resolves to:

| component | Ubuntu 11.04 | **Ubuntu 12.04 LTS** | verdict |
|---|---|---|---|
| `/bin/bash` | 4.2 | **4.2** | **`bash4.2` is THE era-correct variant.** 4.3 is byte-identical in `brand()`; 4.0/4.1 differ (M3); 5.x differ twice over |
| `libc6` | 2.13 | **2.15** | glibc 2.43 reproduces the canonical `srandom(1)` sequence `1804289383, 846930886, 1681692777, 1714636915, …` quoted in the literature since the 1990s. That is **consistent with** `random_r.c` being bit-stable across the 2012→2026 gap, and is the basis for using today's libc as the reference — but it is corroboration, not proof. **Reopen: diff `stdlib/random_r.c` between glibc 2.15 and 2.43, or run the vectors on a 12.04 container.** |
| ABI | i386 **and** amd64 both shipped | both | **both must be swept** — M2 shows they are different generators |
| `coreutils` | 8.5 / **8.13** | 8.13 | the reference here is **9.7**, not 8.13 — see §5 NC-2 |
| `openssl` | 1.0.0e / **1.0.1** | 1.0.1 | `enc` defaulted to `EVP_BytesToKey(MD5)`; reproduced and validated against a 3.5.5 binary with the legacy provider |

Concretely for Phase 2's search order: **`bash4.2` (LP64) → `bash4.2_i32` →
`glibc_random`**, with everything else queued behind them and `bash3.2`/`bash5.x` marked
as completeness only.

**Two corrections to the brief's framing, both from reading the sources:**

1. *"`$RANDOM` is a 15-bit value derived from glibc `rand()`"* (L1 §6.2 row 4, and the
   lane brief) is **not true of any bash release**. bash 3.2 uses its own LCG; bash
   4.0–5.2 use their own Park–Miller/Schrage generator in `variables.c` /
   `lib/sh/random.c`. `$RANDOM` never calls libc's `rand()`. The prior that put the two
   families in one bucket is fine; the mechanism claim is wrong, and `$RANDOM` must be
   swept as an **independent generator**, which is what G1 does.
2. *"`openssl rand` with a short passphrase"* **does not name a real command.** No
   OpenSSL 1.0.x release gives `rand` a seed or passphrase option; `-rand FILE` stirs
   FILE into a pool that still contains OS entropy. The real object with that shape is
   `openssl enc -k PASS`, which G1 implements and validates.

---

## 5. Coverage — what was measured, and what was NOT

**Measured this lane.**

- 19 generators × 8 seeds × 2,000 draws against real libraries/binaries. All PASS.
- A real GNU bash **4.2.0** built from the release tarball and used as the L1 reference.
- Orbit structure of `bash4.2` and `bash4.2_i32` from 8 start states each (Brent).
- The sliding-window identity for 4 variants.
- End-to-end plumbing through I1 + I2 at 9,600 decodes, planted key recovered at rank #1.
- Throughput for every step of the Phase-2 pipeline (`READY.md` §3).

**Not covered, and the concrete condition that reopens each.**

| # | not covered | reopens if |
|---|---|---|
| **NC-1** | **`bash4.2_i32` has no L1 reference.** `gcc-multilib` is absent, so no real 32-bit bash 4.2 binary exists here. The ILP32 model is a re-typed transcription (L4). | `apt install gcc-multilib` (or any i386 box) and re-run `validate.py`; ~10 minutes |
| **NC-2** | **`shuf`'s reference is GNU coreutils 9.7, not the 8.13 of Ubuntu 12.04.** `randint_genmax`'s byte-consumption arithmetic may have changed in 12 years. Ubuntu 26.04 also ships the **Rust uutils** `shuf` as `/usr/bin/shuf`; G1 detects that and prefers `/usr/bin/gnushuf`. | build coreutils 8.13's `shuf` and diff its `--random-source` output on a fixed file. Until then, `shuf_random_source` is validated as an oracle *of the installed binary*, which is not the same as the era's |
| **NC-3** | **CLOSED after the first write-up.** Every bash variant's orbit is now measured except `bash3.2` LP64, whose map is a full-period LCG mod 2⁶⁴ and would need 2⁶⁴ Brent evaluations; its 15-bit output period is stated analytically as 2³¹ (§3.2) and its ILP32 sibling measures exactly 2³² as predicted. | a cycle-finder that exploits LCG structure instead of walking the map — the period of an LCG mod 2⁶⁴ is closed-form, so this is a formality, not a measurement gap |
| **NC-4** | **The `$RANDOM` auto-seeded path is characterised, not enumerated end-to-end.** The 77.6 M figure is an upper bound on the *seed set*; it does not model the joint distribution of `(tv_sec, tv_usec, pid)`, which would let S1 order the subset by likelihood rather than treat it as flat | anyone models pid allocation and `tv_usec` on a 2012 desktop; low value, cheap |
| **NC-5** | **No keystream was scored against LP2.** By design — the Phase 0 hold. | I1/I2/I3 gates PASS and S1 runs `READY.md` §5 |
| **NC-6** | **`openssl enc -k` overlaps `R16-KDF` (692,064 configs) and the overlap was not computed.** | S1 diffs G1's `evp_bytes_to_key` schedule against R16-KDF's covered configs before spending anything on it |
| **NC-7** | **`/dev/urandom`, bare `shuf`, `openssl rand`, `$SRANDOM`: UNREACHABLE.** Not swept, and no null is reported for them. This is a property of the objects — no seed, no record — not of the effort. | nothing. ARMADA-DOCTRINE §5 applies: this branch may be the true one and no instrument reaches it |
| **NC-8** | **glibc bit-stability 2.15 → 2.43 is corroborated, not proved** (§4). The reference library is 12 years newer than the target. | diff `stdlib/random_r.c` across the two releases, or run `ref_glibc.c` inside an Ubuntu 12.04 container; ~30 minutes |
| **NC-9** | **PHP `mt_rand`, .NET, Perl 5.14, Python 2.7, TeX LCGs** are other lanes (G2/G3/G4) and other ledger entries. | — |

---

## 6. The plant and the pilot (labelled)

`plant.py` builds the object Phase 2 must recover: LP-register English, reduced through
`campaign18_skip.encipher_keyskip` (`supp = 0.83`, the repo's pinned filter strength)
under the keystream `bash4.2 | RANDOM=3301 | mod29 | sign=-1 | fwd | offset 0`. L = 120,
6 key skips, key pointer ends at 125. Written to `plant.json`.

I1 and I2 had both published their interfaces before G1 reached the boundary, so the
≤10,000-decode pilot the brief permits was run:

| | |
|---|---|
| decodes | **9,600** (200 seeds × 48 cells, planted seed included) |
| wall-clock | 173.8 s → **55.2 decodes/s/core** end-to-end |
| decoder | `round19/I1/driftbeam.py`, `mode=keyskip1`, `beam_w=400`, `max_skip=3` |
| adjudicator | `round19/I2/adjudicate.py` |
| **planted rank by English** | **#1 of 9,600** |
| **planted rank by I2 `pcon`** | **#1 of 9,600** |
| planted row | `en=-4.356  pmax=+26.22  pcon=+20.86  ioc=1.612  mds=13  zl=0.808` |
| best genuinely-wrong-key English | **−6.214** (separation 1.86) |

**This is a pilot. It carries no verdict, no threshold was applied, and its score
distribution is not interpreted.** It establishes one thing: a G1 keystream, enciphered
under the repo's key-skip model, survives I1's decoder and I2's adjudicator and lands
first. It says nothing whatsoever about LP2.

The #2 row is the *same* key under `rej29` — see §3.5.

---

## 7. Bounds, not verdicts

Nothing is closed here, because nothing was swept here. What is established:

- The bash `$RANDOM` and glibc generator families are **implemented, validated against
  the real libraries, and enumerable**, and the enumeration is affordable *if and only
  if* Phase 2 runs a screen whose power I3 has measured. At full beam power it is 39
  core-years per generator and must not be attempted.
- The era-correct targets are **`bash4.2` (both ABIs)** and **`glibc_random`**, on
  evidence from the author's own signatures rather than on lore.
- `$RANDOM` is **not** a glibc `rand()` derivative, and `openssl rand` **cannot** be
  driven by a passphrase. Two framing errors corrected before any budget was spent.

**Reopen condition for the lane as a whole:** NC-1 (a real 32-bit bash 4.2) and NC-2 (a
real coreutils 8.13 `shuf`) each convert an L4 reference into an L1/L3 one. NC-5 is the
whole of Phase 2.

---

## 8. Reproduce

```bash
cd liber-primus/analysis/round19/G1
sh fetch_bash_src.sh              # bash 3.2-5.2 sources + a real bash 4.2 binary
python3 validate.py               # THE GATE -- 19/19 PASS, writes validation.json
gcc -O2 -o /tmp/orbit orbit.c && /tmp/orbit bash4.2 bash4.2_i32
python3 keystream.py              # the production interface, smoke test
python3 plant.py --plant          # build plant.json
python3 plant.py --seeds=200      # the pilot (requires round19/I1 and round19/I2)
```

Requires WSL Ubuntu with `gcc`, `curl`, real `glibc`, `openssl`, and GNU `shuf`
(`gnushuf` on Ubuntu 26.04). ~60 MB of bash tarballs are fetched to `/tmp/g1src` and are
deliberately not committed — `fetch_bash_src.sh` rebuilds every byte.
