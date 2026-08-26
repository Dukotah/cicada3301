# ROUND 19 / G1 — PRE-REGISTRATION

**Lane:** G1 — bash `$RANDOM` + glibc generators. Phase 1 of
[`round19/CAMPAIGN-PLAN.md`](../CAMPAIGN-PLAN.md).
**Binding:** [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
**Written before any generator was built or any measurement taken.**
Trust anchor run first: `python3 liber-primus/tests/validate.py` →
`ALL VALIDATIONS PASSED — rig reproduces known solves` (5/5), 2026-08-26.

> **THE HOLD.** Phase 0 (I1 driftbeam, I2 adjudicator, I3 thresholds) is not finished.
> This lane produces **validated generators and a keystream-production interface, and
> stops at the scoring boundary.** It scores nothing. Sweeping with the current
> instrument is exactly the mistake Round 19 exists to correct (L7-A, L7-B).

---

## 1. The Aiming Test (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A hit in this lane is a tuple

```
(implementation_variant, seed, reduction, sign, direction, atbash, offset)
```

and the recognizer is **not mine** — it is I1's decoder plus I2's adjudicator. G1 cannot
answer Q1 for the scoring step, and saying otherwise would be a lie. What G1 *can* and
*must* do is:

1. **Answer Q1 for the generator layer**, where the "instrument" is the validation gate
   (§4). The planted object there is a *real library output*, and the gate proves the
   Python reimplementation emits it byte for byte. That check is run and reported.
2. **Ship the plant that Phase 2 must recover.** `plant.py` builds a synthetic
   ciphertext by taking a keystream this lane produces (`bash4.2`, `RANDOM=3301`,
   `mod29`, `sign=-1`, offset 0), reducing LP-style English plaintext through
   `campaign18_skip.encipher_keyskip`, and handing S1 both the ciphertext and the
   correct tuple. **S1 may not report a G1 negative until it has recovered that plant
   at rank #1.** This is the check every prior seed sweep in this repository omitted
   (B-21: "Round 8 also used RIGID decode throughout").
3. **State the shape constraint the recognizer must satisfy**, which this lane
   discovered and which is not optional:

> **For every generator in this lane, `seed` and `keystream offset` are the same axis.**
> `brand()` is a pure state map and `RANDOM=<seed>` writes the state directly, so the
> keystream for seed *s* is a *window* into one master orbit entered at *s*. An
> instrument that pins offset 0 is not testing fewer offsets — it is testing a
> *relabelled* subset of the same seeds. LEDGER **B-02** ("every sweep assumed key
> index 0 = rune 0") is therefore not a separate lane for G1; it is this lane.

### Q2 — What measured fact raises this family's prior above the flat rate?

[`round18/L1-toolchain/RESULTS.md`](../../round18/L1-toolchain/RESULTS.md) §6.1–§6.2.
Specifically:

| fact | what it says | where |
|---|---|---|
| **F6** | **46 of 46** curated 3301 PGP messages, spanning 2012, 2013 and 2014, carry `Version: GnuPG v1.4.11 (GNU/Linux)` — one signing environment, unchanged for three years | L1 §6.1, verified against `corpus/A-primary-artifacts/ibotpeaches/messages/` |
| **F7** | GnuPG **1.4.11** specifically (rel. 2010-10-18). Ubuntu 11.04–12.04 LTS shipped exactly 1.4.11; Debian wheezy shipped 1.4.12 | L1 §6.1 |
| **F1/F8/F9** | ImageMagick at **default quality 92**, no EXIF/XMP/COM, no `jpegtran` post-pass: a short, unfussy **CLI/shell** invocation over 58 numbered files | L1 §3.1, §6.1 |

L1 turns those into §6.2 **row 1 — glibc `rand()`/`random()`/`drand48`, ×3, the
top-ranked family** ("`random()`'s TYPE_3 additive-feedback generator is *the* default
PRNG a 2012 Linux C program gets for free") and **row 4 — bash/coreutils composites,
×2, never swept** ("defaults-only CLI usage says the author reached for the shell
first; `$RANDOM` is a 15-bit glibc-derived generator with a tiny seed space").
§6.3 item 1 names `$RANDOM` as "the cheapest unrun item in the whole register".

**This lane is therefore NOT a completeness ritual.** Its prior is a physical
measurement on held artifacts (a version string in 46 signatures, a JPEG quantisation
table), which is what doctrine R4 asks for.

The era-correct binding that follows, and that this lane treats as the primary target:
**Ubuntu 11.04–12.04 ⇒ `/bin/bash` is 4.2, `libc6` is glibc 2.13–2.15.**

### Q3 — Is the space bounded, and by what?

**Yes, and the bash half is fully enumerable.** Full accounting in §3.

| object | size | class |
|---|---:|---|
| bash `$RANDOM`, `RANDOM=<seed>`, per implementation variant | ≤ 2³¹ distinct keystreams (one orbit; measured, not assumed) | **enumerable** |
| bash `$RANDOM`, auto-seeded, 2012-01→2014-06 | ≤ 74 × 2²⁰ = **77,594,624** seeds (3.6 % of 2³¹) | **enumerable**, and a *priority ordering* inside the above |
| glibc `random()` / `rand()` | 2³² − 1 = 4,294,967,295 | **enumerable to generate, NOT to beam-decode** — see §5 |
| glibc `lrand48`/`mrand48`/`drand48` | 2³² via `srand48` | enumerable to generate |
| `shuf --random-source=FILE` | the space of FILES | **dictionary**, not a seed range |
| `openssl enc -k PASS` | the space of passphrases | **dictionary**; overlaps LEDGER `R16-KDF` |
| `openssl rand`, bare `shuf`, `/dev/urandom` | — | **UNREACHABLE.** Stated, not swept. See §6 |

### Q4 — What are the three conditionals the negative will carry?

Any negative that Phase 2 derives from this lane's keystreams is conditional on:

1. **Key space** — the exact (variant × seed range × reduction × sign × direction ×
   atbash × offset) product, tabulated per row with its covered fraction.
2. **Decoder transition model** — I1's driftbeam, and *which* rejection-loop
   implementations it can represent. Round 18 L7-B measured the current beam at
   −6.90 / 25.8 % recovery on `skip_by_two`; until I1 lands, that bound applies.
3. **Adjudicator register** — I2's panel. Round 18 L7-A measured 0.33 power for Latin
   and **0.00** for vowel-dropped English on the current English quadgram scorer.

A G1 result that names fewer than three is not a result.

### Q5 — What single observation makes you abandon this lane at 10 % of budget?

Two kill conditions, both checked **before any keystream is emitted**:

- **K1 — the gate.** If `gen_bash.raws(s, n, "bash4.2")` does not equal a real
  bash 4.2 binary's `$RANDOM` output byte for byte over the pre-registered seeds, or
  `gen_glibc.random_seq` does not equal real glibc's `random()`, the corresponding
  generator **does not enter the sweep** and this lane reports the failure instead of a
  keystream. *(Checkpoint: `validate.py`, before anything else.)*
- **K2 — orbit degeneracy.** If `orbit.c` shows an implementation variant's state map
  has a cycle shorter than **12,956** (the length of the unsolved LP2 stream), that
  variant cannot supply a non-repeating pad for the book and is reported dead on
  arrival rather than swept. *(Checkpoint: `orbit.c`, before the space statement is
  finalised.)*

Neither kill condition is about "not finding anything" — both are about the object
being the wrong shape, which is checkable in minutes.

---

## 2. What is already measured, and will NOT be re-run (doctrine §4 R6)

Read from `coverage`/`not_covered`, never from `status`:

| ledger | what it actually covered | what it leaves |
|---|---|---|
| **B-21** | 2.52e9 decodes, 10 integer-seeded generators over **~3 % of each seed space** (only 2 full). glibc `random()` is generators 0/1/2. **RIGID decode throughout.** | 97 % of glibc's seed space, and *all* of it under a decoder D3 showed manufactures false negatives on this cipher |
| **B-01** | the full-32 sweep is **2/10 complete**; `results_full32.txt` holds gen=3 (MSVC) and gen=5 (MT19937). **gen=0 (glibc) is absent and has no `DONE` line** | glibc's full-32 pass was never finished |
| **B-03 / B-08** | named-but-unswept generator + seed residue | superseded in part by R16-PRNG; `$RANDOM` appears in neither |
| **R16-PRNG** | 52,556 decodes, 7 generators × 1,877 seeds (1,828 unix-seconds at ~1/day stride + 49 lore seeds) × mod-29 × 2 signs × 2 directions | `not_covered` explicitly lists "unix-second seeds between daily samples", "offsets != 0", "full 2^32 seed sweep (~0.004 % coverage per generator per orientation)". **bash `$RANDOM` is not among the 7** |
| **CENSUS §A/§B** | Round 8's 10 generators; L5's 4 additions incl. **gen 10 Perl-drand48** and **gen 11 `lrand48`** validated against the real binaries | drand48 *as reached through a C program* and `mrand48`/`drand48`-double extraction |

**So G1 re-runs nothing.** `lrand48` is re-implemented here only so that the *whole
family* sits behind one validated interface; `RESULTS.md` marks it
`already-covered-by CENSUS gen 11` and S1 must de-duplicate rather than re-sweep.

---

## 3. The space, stated precisely (this is the lane's deliverable)

### 3.1 bash `$RANDOM` — the enumerable half

`$RANDOM` reaches the user through `get_random_number()`, identical in every release
from 3.2 to 5.2:

```c
do   rv = brand ();
while (rv == last_random_value);
last_random_value = rv;
```

and `RANDOM=<value>` reaches the generator through
`assign_random() → sbrand(strtoul(value, NULL, 10))`, i.e. **the seed *is* the state.**
`sbrand()` also sets `last_random_value = 0`.

Two consequences, both load-bearing:

- **A1 — the space is one orbit.** `brand()` is a pure map `s → f(s)`, so the set of
  distinct `$RANDOM` streams equals the set of orbits of `f`. Enumerating seeds is a
  **sliding window over one master sequence**, cost O(2³¹ + L) rather than O(2³¹ · L).
  The window identity is checked in `validate.py`
  (`internal_consistency.sliding_window_*`), not assumed.
- **A2 — bash's `$RANDOM` already contains a rejection loop.** At 15-bit granularity it
  suppresses only ~1/32768 of draws, so it does **not** by itself explain LP2's mod-29
  doublet deficit (0.664 % observed vs 3.45 % expected). It is recorded because it is
  the literal `while x == last: redraw` shape Round 17 found machine-applied, sitting in
  the standard library of the shell L1 puts on the author's box. **Noted, not
  overclaimed, and not offered as evidence.**

**Implementation variants swept.** The generator changed three times inside the window
this puzzle spans, and the arithmetic width is the ABI's, so:

| variant | source | era |
|---|---|---|
| `bash3.2` / `bash3.2_i32` | `rseed = rseed*1103515245 + 12345`, out `(rseed>>16)&32767` | Ubuntu ≤ 8.04 |
| `bash4.0` | Park–Miller/Schrage; `rseed==0` calls **`seedrand()`** (time-based) | Ubuntu 9.10–10.04 |
| **`bash4.2` / `bash4.2_i32`** | Park–Miller/Schrage, `rseed==0 → 123459876`, **negative correction `#if 0`-ed out**, `rseed` is `unsigned long` | **Ubuntu 11.04–12.04 — the era-correct target** |
| `bash5.0` | `rseed` is `u_bits32_t`, correction **enabled** → true Lehmer mod 2³¹−1 | Ubuntu 19.10+ |
| `bash5.1` / `bash5.1c50` | Lehmer state, output folded `(rseed>>16)^(rseed&65535)` when compat > 50 | Ubuntu 21.04+ |

The ILP32/LP64 fork is real and pre-registered: Ubuntu 12.04 shipped both, and in
3.2–4.3 `rseed` is `unsigned long` with the wrap-correction removed, so the two ABIs
emit different streams from the same seed.

**Seed ranges swept, per variant.**

* **explicit `RANDOM=<seed>`:** `0 … 2³²−1` (4,294,967,296), collapsing to the measured
  orbit size. Justification for the ceiling: it contains every `RANDOM=<literal>`,
  `RANDOM=$$`, `RANDOM=$(date +%s)` and `RANDOM=$(id -u)` a 2012 script could write.
  Values above 2³² require a human to type an 11-digit constant.
* **auto-seeded (no assignment):** bash 4.2 `initialize_shell_variables()` (variables.c
  line 537) calls `seedrand()` at shell start —
  `sbrand(tv.tv_sec ^ tv.tv_usec ^ getpid())`. For a run between **2012-01-01 and
  2014-06-01**: `tv_sec ∈ [1325376000, 1401580800]`, `tv_usec < 10⁶ < 2²⁰`,
  `pid ≤ 32768 < 2¹⁵`. The XOR therefore only rewrites the **low 20 bits** of `tv_sec`,
  so the reachable seed set is 74 high-prefixes × 2²⁰ = **77,594,624 seeds**, a
  **3.6 % subset of 2³¹** that a full enumeration subsumes and that a partial
  enumeration should visit **first**.

### 3.2 glibc — the top-ranked half

`srandom(seed)` / `rand()` (identical on glibc — measured in `validate.py`, not
assumed), plus `initstate()` at 8/32/64/128/256 bytes (TYPE_0…TYPE_4) and the
`*rand48` family. Seed space **2³² − 1** distinct streams (`seed == 0` is folded to 1).
Unlike bash, the internal state (31 × 32 bits for TYPE_3) is far larger than the seed,
so there is **no orbit collapse** and no sliding window: each seed costs
O(10·deg + L) = O(430) to generate. That is cheap in C, and it is *not* the bottleneck
— the decode is (§5).

### 3.3 The cross, following `round13/B04/PREREG.md` §3.3–3.5 verbatim

* **reductions (6):** `mod29`, `rej29` (unbiased rejection — the form a careful author
  writes), `scale29` (`$((RANDOM*29/32768))` / `(int)(drand48()*29)`), `hi_nib`,
  `lo_byte`, `bits5`. B-04's core three are `mod29`/`rej29`/`scale29`.
* **sign ∈ {−1, +1}** — key subtracted / added, decode `p = (c + sign·k) mod 29`.
* **direction ∈ {forward, reversed}**.
* **Atbash ∈ {off, on}** — plaintext-alphabet reflection `i ↦ 28 − i`.
* **offsets:** Stage A pins 0; Stage B sweeps {1, 4, 16, 29, 64, 128, 256, 512, 1024,
  3301}. **For the bash family, offset is not an extra axis — it is a seed relabelling
  (§1 Q1), so Stage B is redundant there and Stage A at full seed coverage subsumes
  it.** For glibc it is a genuine extra axis.

Stage-A cell count = 6 × 2 × 2 × 2 × 1 = **48 cells per (variant, seed)**.

---

## 4. Gates — pre-registered, and binding on this lane

**G1-VAL (the validation gate).** Every generator must reproduce the real library
byte-for-byte before it may produce a keystream, over **8 pre-registered seeds**
`{0, 1, 2, 3301, 12345, 2147483647, 4294967295, 1376006400}` × **2000 draws**.
Reference strength is recorded per generator:

| level | reference |
|---|---|
| **L1** | a real running binary of the era-correct version (a GNU bash **4.2.0** built from the ftp.gnu.org release tarball) |
| **L2** | a real running binary of a later version (the system `/bin/bash`) |
| **L3** | the real system library through C (`ref_glibc.c`), and the real `openssl` / `shuf` binaries |
| **L4** | C compiled from the released source of a version whose binary we could not build (`ref_bash.c`) |

A generator with no L1/L2/L3 reference is labelled **NOT-VALIDATED** and is reported as
such; it does not silently enter a sweep. `validate.py` exits non-zero if any
**era-correct** generator fails.

**G1-ORB (the orbit gate, = K2).** `orbit.c` measures cycle length and tail for every
bash state map with Brent's algorithm. Any variant whose cycle is shorter than 12,956
is reported dead on arrival.

**G1-WIN (the sliding-window gate).** `window(master, i, n) == raws(state_at_i, n)`
must hold, or the O(2³¹ + L) sweep plan is invalid and Phase 2 must pay O(2³¹ · L).

---

## 5. The decode wall — declared in advance so READY.md cannot flatter itself

Measured before writing this section, on this box, with
`round18/L2-filter-leak/fastbeam.py` at `beam_w=400, max_skip=3, L=120`:
**≈ 143 beam decodes / second / core.**

Therefore a full 2³² beam sweep of *one* glibc variant at *one* of 48 cells is
≈ 4.3e9 / 143 = **3.0e7 core-seconds ≈ 0.95 core-years**, and the 48-cell cross is
**45 core-years**. **A full-enumeration beam sweep of this space is not affordable and
this lane will not claim it is.** Round 8 reached 2.52e9 decodes only because it used a
*rigid* decoder in C — the same decoder D3 showed scores the correct key at −6.835.

The consequence is pre-registered here rather than discovered later: **Phase 2 must
either (a) accept a stated coverage fraction of a few percent at full beam power, or
(b) run a cheap pre-screen and beam only its survivors.** If (b), the screen is itself
an instrument and doctrine R1 forbids using it until its power has been measured by
planting the correct key. G1 supplies the plumbing and the timings for both; **G1 does
not choose between them, and G1 does not calibrate the screen.** That is I3's ground.

---

## 6. Reachability — what this lane will NOT pretend to sweep

| object | verdict |
|---|---|
| `/dev/urandom` | **UNREACHABLE, permanently.** No seed and no public record. This is the branch ARMADA-DOCTRINE §5 says may well be the true one. Nothing here touches it and nothing can. |
| `shuf` with no `--random-source` | **UNREACHABLE.** coreutils `randread_new()` opens `/dev/urandom`. |
| `openssl rand N` | **UNREACHABLE.** No 1.0.x release has a passphrase or seed option; `RAND_bytes` draws from a pool seeded by `/dev/urandom` + pid + time, and `-rand FILE` only stirs FILE *into* that pool. The brief's phrase "`openssl rand` with a short passphrase" **does not name a real command**; the real object with that shape is `openssl enc -k`. |
| bash 5.1's `$SRANDOM` | **UNREACHABLE** (reads `/dev/urandom`) **and excluded by date** — bash 5.1 is 2020, LP2 is 2014. |

A null is never reported for any of these. They are stated, with the reason, and left
open.

---

## 7. Outputs and stopping rule

`PREREG.md` (this file) · `gen_bash.py` · `gen_glibc.py` · `gen_coreutils.py` ·
`reduce29.py` · `ref_bash.c` · `ref_glibc.c` · `orbit.c` · `validate.py` +
`validation.json` · `plant.py` · `READY.md` · `RESULTS.md` · `ledger.json`.

**Stopping rule.** This lane stops at the scoring boundary. If — and only if — I1 has
published `round19/I1/driftbeam.py` and I2 `round19/I2/adjudicate.py` before G1
finishes, G1 may run a **pilot of ≤ 10,000 decodes** to prove the plumbing and report
timings. A pilot is labelled a pilot in `RESULTS.md`, carries no verdict, and its
score distribution is not interpreted.

**No threshold appears in this file, because this lane sets none.** Thresholds are I3's.
