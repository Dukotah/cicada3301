# ROUND 19 / LANE G2 — RESULTS
## Perl 5.14 `rand` / `srand` — validated generators, space accounting, and the hold

_2026-08-26. Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
Pre-registration: [`PREREG.md`](PREREG.md). Run spec: [`READY.md`](READY.md)._

**Trust anchor — before:** `python3 liber-primus/tests/validate.py` →
`ALL VALIDATIONS PASSED (5/5)`.
**Trust anchor — after:** see §8.

> ## THE HEADLINE, IN ONE PARAGRAPH
>
> The Perl 5.14 generator is now reproduced **byte-exactly**, gated three ways,
> with the 5.40-vs-5.14 version risk **retired by measurement rather than
> argument**. Reading Perl 5.14.2's own source produced a finding that changes
> the shape of this lane and, arguably, of the whole seeded-PRNG programme:
> **Perl's un-seeded `rand` is not unbounded.** `Perl_seed()` reads *four bytes*
> of `/dev/urandom` into a `U32`, so the single most idiomatic thing a 2012
> scripter can write — `perl -e 'print chr(int(rand(29))) for 1..13000'`, with
> no `srand` at all — lands in a **fully enumerable 2³² space**, not in the
> unattackable `/dev/urandom`-as-pad branch. Unlike Java or Python, this family
> has **no seed residue above 2³² at all**. Nothing was scored: Phase 0's gates
> have not published PASS, and scoring here is the exact mistake Round 19
> exists to correct.

---

## 1. Validation verdict

`validate.py` → `validation.json`. **186 checks, 0 failing, OVERALL PASS.**

| gate | what it proves | checks | verdict |
|---|---|---:|---|
| **A** | `gen_perl.py` == the real `perl` binary, element for element | 164 | **PASS** |
| **B** | the real `perl` == glibc `srand48`/`drand48` called from C | 13 | **PASS** |
| **C** | structural: seed folding, the integer fast path, `srand()` coercion | 9 | **PASS** |

### 1.1 Gate A — my Python vs real Perl

* **A0** — the raw `Drand01()` double at `%.17g`, 6 seeds × 64 draws: identical.
* **A1** — `int(rand(M))` for `M ∈ {26, 29, 32, 100, 255, 256, 1000, 2³²}`,
  13 seeds × **2,000 draws** each: identical, element for element.
* **A2** — all **9** Perl-reachable reductions, driven through real Perl loops in
  `ref_reduce.pl`, 6 seeds × 512 symbols: **9/9 reductions, 6/6 seeds, byte-exact.**

Seed panel: `0, 1, 42, 12345, 3301, 1033, 1399079190, 2147483647, 3141592653,
4294967295, 1293840000, 1420070400, 845145127` — the `round10/L5-seed32`
panel plus the era band's endpoints and the 3301 constant.

Sample (seed 3301, first 8 symbols, perl vs mine):

| reduction | perl | gen_perl.py |
|---|---|---|
| `r29` | 19,17,20,16,16,20,28,14 | 19,17,20,16,16,20,28,14 |
| `r29_nodup` | 19,17,20,16,20,28,14,7 | 19,17,20,16,20,28,14,7 |
| `r32_rej` | 22,19,22,17,18,22,15,16 | 22,19,22,17,18,22,15,16 |
| `r256_mod` | 2,9,6,25,3,3,22,10 | 2,9,6,25,3,3,22,10 |
| `r2p32_mod` | 18,6,6,1,1,1,19,23 | 18,6,6,1,1,1,19,23 |
| `r255_mod` | 1,8,5,25,2,3,21,10 | 1,8,5,25,2,3,21,10 |
| `r100_mod` | 10,2,12,26,28,11,12,20 | 10,2,12,26,28,11,12,20 |
| `r1000_mod` | 22,23,9,3,27,28,6,1 | 22,23,9,3,27,28,6,1 |
| `r26_lat` | 4,13,15,3,13,15,15,19 | 4,13,15,3,13,15,15,19 |

### 1.2 Gate B — the era question, retired by measurement

This box has **perl v5.40.1**, whose `perl -V:randfunc` is `Perl_drand48` — Perl's
own bundled implementation, adopted in 5.20 so sequences match across platforms.
The target is 5.14.2. That gap was closed by reading the 5.14.2 source and then
measuring, not by asserting.

Source (tarball `https://www.cpan.org/src/5.0/perl-5.14.2.tar.gz`, md5
`3306fbaf976dcebdcd49b2ac0be00eb9`, the official upstream digest):

* `Configure` ~L19280 —
  `if set drand48 val -f; eval $csym; $val; then dflt="drand48"` … `elif … random` … `else rand`.
  On **any glibc host** — which Ubuntu 12.04 is — Configure picks `drand48`
  without prompting, and then sets
  `drand01="drand48()" ; seedfunc="srand48" ; randbits=48 ; randseedtype=long`.
* `config_h.SH:2131–2134` — `#define Drand01() drand48()`,
  `#define seedDrand01(x) srand48((Rand_seed_t)x)`, `#define RANDBITS 48`.
* `pp.c` — `PP(pp_rand)`: `value = POPn` (or 1.0); `value *= Drand01();`
  `PP(pp_srand)`: `const UV anum = (MAXARG < 1) ? seed() : POPu; seedDrand01((Rand_seed_t)anum);`

So **Perl 5.14.2 on Ubuntu is literally calling glibc `srand48`/`drand48`.**
Gate B then measured the installed perl's `rand()` against `ref_drand48.c`, a C
program calling those glibc functions directly: **13 seeds × 1,024 draws,
identical at 17 significant digits, 13/13.**

Chain: mine == 5.40 (gate A); 5.40 == glibc (gate B); 5.14 *is* glibc (source).
Therefore **mine == 5.14**, by measurement on both live legs.

`nvtype` is `double` and `nvsize` 8 on this build, as on the Debian/Ubuntu
x86_64 5.14 build, so `value *= Drand01()` is IEEE-754 binary64 in both — which
is what makes a Python float reproduction exact rather than approximate.

### 1.3 Gate C, and the ONE residual uncertainty (stated, not buried)

* **C1** — `srand(S)` ≡ `srand(S + 2³²)` ≡ `srand(S + 2³³)`, measured in perl for
  S ∈ {1, 3301, 1293840000}. This is the fact that bounds the space at 2³².
* **C2** — the integer fast path `(M·x) >> 48` equals the C double expression
  `int(M · (x/2⁴⁸))` for M ∈ {26, 29, 32, 256, 2³²}: **0 mismatches in 52,000
  draws each**. (`x` carries ≤ 48 significant bits, so for M < 2⁵ or M a power of
  two the product needs ≤ 53 bits and binary64 holds it exactly.) For M ∈ {100,
  255, 1000} `gen_perl` uses the float path, which gate A1 confirms.
* **C3** — `srand()` argument coercion. **This is where 5.14 and 5.40 genuinely
  differ**, and the difference is real:

| `srand(ARG)` | 5.40 measured | 5.14 rule (`POPu`/`SvUV`) → seed32 | 5.40 rule → seed32 | diverge |
|---|---|---:|---:|:--:|
| `"3301"` | 3301 | 3301 | 3301 | no |
| `"CICADA3301"` | 18446744073709551615 | **0** | 4294967295 | **yes** |
| `"3301CICADA"` | 18446744073709551615 | **3301** | 4294967295 | **yes** |
| `"1e3"` | 18446744073709551615 | **1000** | 4294967295 | **yes** |
| `"0x0CE5"` | 18446744073709551615 | 0 | 4294967295 | **yes** |
| `-1` | 1 | **4294967295** | 1 | **yes** |
| `"3.7"` | 3 | 3 | 3 | no |
| `4294967297` | 4294967297 | 1 | 1 | no |
| `" 42"`, `"+3301"`, `"3301.9"`, `"0"` | as shown | 42 / 3301 / 3301 / 0 | same | no |

5.40's `pp_srand` calls `grok_number` and substitutes `UV_MAX` when the string
is not a UV-representable integer (and returns the *magnitude* for a negative,
which is why `srand(-1)` ≡ `srand(1)`). 5.14's `POPu` numifies with plain `SvUV`.
Both rules are implemented in `gen_perl.srand_arg_to_seed(arg, era=…)`; the
5.40 model was verified against the running perl in all 13 cases.

**Honest statement of what remains unverified:** the 5.14 column is derived from
reading `pp.c` plus documented `SvUV` semantics, and could not be executed —
no 5.14 runtime is available and building one was out of budget. **The residual
uncertainty is confined to non-integer `srand` *arguments* and does not touch
coverage:** every value in both columns lies inside 0..2³²−1 and is therefore
enumerated either way. It affects only how a hit would be *described*.

**A notable consequence, worth its own line:** unlike Python (lane G3), **Perl
has no string-seed dictionary branch.** Perl numifies, so `srand("CICADA3301")`
is not a distinct key — it is seed 0 (5.14) or seed 0xFFFFFFFF (5.40). The
2,165-entry seed dictionary that B-04 needed has no analogue here. The space
really is just the integers.

---

## 2. The space

### 2.1 Size and enumerability

| axis | size | note |
|---|---:|---|
| seed | **2³² = 4,294,967,296** | **enumerable, complete, no residue** |
| reduction | 9 Perl-reachable | + 2 C-only forms carried for de-duplication |
| sign × Atbash × direction | 8 | B-04 §3.4 |
| **Stage A (offset 0)** | **3.09 × 10¹¹ decodes** | |
| Stage B offset ladder | ×10 | B-04 §3.5 |

### 2.2 Why 2³² is a complete bound and not a slice — the lane's main finding

Two independent facts, both from the 5.14.2 source, both confirmed by measurement:

1. **Every explicit seed folds.** glibc `srand48_r` keeps only the low 32 bits:
   `__x[2] = (unsigned short)(seedval >> 16); __x[1] = (unsigned short)(seedval & 0xffff); __x[0] = 0x330e`.
   With `seedDrand01(x) = srand48((long)x)`, any `srand` argument — 64-bit
   integer, numified string, negative, `time`, `time ^ $$`,
   `time ^ ($$+($$<<15))` — reduces mod 2³². Measured (gate C1).

2. **The un-seeded path is 32 bits too.** `util.c: Perl_seed()`:

   ```c
   U32 u;
   fd = PerlLIO_open(PERL_RANDOM_DEVICE, 0);        /* "/dev/urandom" */
   if (fd != -1) { PerlLIO_read(fd, (void*)&u, sizeof u); ... if (u) return u; }
   /* fallback: SEED_C1*tv_sec + SEED_C2*tv_usec + SEED_C3*pid
                + SEED_C4*&stack_sp + SEED_C5*&when   -- also a U32 */
   ```

   Four bytes. `PL_srand_called` is then set, so the seed is drawn exactly once
   per process.

**This is the finding.** `round10/L5-seed32/CENSUS.md` §E treats "no seed at all"
as the modal behaviour and the branch nothing can reach, and Round 16's lane P2
already split that category once (a seedless pad can still have a public
*record*). This splits it again: **a Perl author who never calls `srand` still
produces a 32-bit-seeded pad.** The `/dev/urandom` entropy is real but only 32
bits of it ever reach the generator. The gap between "the author used
/dev/urandom" and "the pad is unreachable" is not as wide as the taxonomy
assumed — for this generator it is not wide at all.

Corollary for the ledger: `CENSUS.md` §D's "seeds wider than 2³²" residue —
which applies to Java's 48-bit `setSeed` and Python's millisecond seeds — **has
no Perl entry.** There is nothing to write in `not_covered` under that heading.

### 2.3 A bounding argument that collapses `time ^ $$`

`perlfunc`'s own `srand` documentation names `time ^ $$` and
`time ^ ($$ + ($$ << 15))` as the historically common seeds. For `$$ < 2¹⁵`
(Linux default `pid_max` 32768), `time ^ $$` flips only the low 15 bits of
`time`, so the achievable value set is the union of aligned 32768-blocks over
the era band — which, the band being contiguous and far longer than 32768, is
**exactly the era band rounded outward to 32768 boundaries.** `time ^ $$` is
therefore *covered by the plain `time` band plus 65,536 values*, not a separate
sweep. The `$$+($$<<15)` variant reaches ~30 bits and is covered only by the
full 2³² enumeration.

### 2.4 Reductions, and which are era-idiomatic

The task brief warns that a naive sweep gets this wrong, and it is right to.
`int(rand(29))` is `(29·x) >> 48` — a **scaled truncation of the top bits** of
the 48-bit state. Reducing the raw state mod 29 reads the **low bits**. The two
streams share no symbol beyond coincidence and diverge at the first draw. **A
sweep that reduces the raw state mod 29 and calls it "Perl" has not tested Perl.**

| rank | id | the Perl line | era-idiomatic? | why |
|---:|---|---|---|---|
| 1 | `r29` | `int(rand(29))` | **yes — the idiom** | `perlfunc`'s own worked example for `rand` is `$random = int(rand(10))`. This is not a judgement call; it is what the manual page a 2012 author read shows them. |
| 2 | `r29_nodup` | `do { $k = int(rand(29)) } while ($k == $last);` | **yes** | `round18/L1-toolchain/RESULTS.md` §6.3 item 5 predicts precisely this loop from F8 (defaults-only tooling) + Round 17's machine-filter finding |
| 3 | `r32_rej` | `do { $k = int(rand(32)) } while ($k > 28);` | plausible | the unbiased power-of-two rejection a careful author writes; the shape Ruby's `rand(29)` uses internally |
| 4 | `r256_mod` | `int(rand(256)) % 29` | plausible | a scripter thinking in bytes; biased, which a 2012 hobbyist would not notice |
| 5 | `r2p32_mod` | `int(rand(2**32)) % 29` | plausible | "give me a 32-bit random number", then reduce |
| 6 | `r255_mod` | `int(rand(255)) % 29` | less likely | the off-by-one of rank 4 |
| 7 | `r100_mod` | `int(rand(100)) % 29` | less likely | |
| 8 | `r1000_mod` | `int(rand(1000)) % 29` | less likely | |
| 9 | `r26_lat` | `chr(65 + int(rand(26)))` | plausible, different object | a **letter** pad, read into runes through the repo's canonical Latin→futhorc map. An author building "a one-time pad" may well think in letters, not runes. |
| — | `raw48_mod` | `state % 29` | **NOT Perl** | Perl never exposes the 48-bit state. This models a C author calling `srand48`/`erand48`. |
| — | `lrand48_mod` | `lrand48() % 29` | **NOT Perl** | CENSUS generator 11, already swept at rigid alignment |

`1 + int(rand(29))` collapses onto `r29` under a 1-based rune table and is not a
separate row. `srand`-per-symbol re-seeding, and a stream offset by an unknown
number of `rand` draws consumed elsewhere in the same script, are named in
PREREG §4.4 as **not covered** — the latter is a genuinely unbounded axis and is
not the same thing as the §4.3 keystream offset.

---

## 3. FOUND-ERROR: the prior's citation was wrong, and the prior survives anyway

Doctrine R6 asks lanes to audit each other. This lane audited its own prior.

`round18/L1-toolchain/RESULTS.md` §6.2 row 3 marks Perl 5.14 **"never swept"**.
That is **incorrect**. `round10/L5-seed32/CENSUS.md` §B lists generator **10** as
`Perl srand(S); int(rand(29))`, gated against `/usr/bin/perl` in
`VALIDATION.txt` (5 seeds × 2,000 draws, PASS), and `results_newgens.txt`
records the run:

```
gen=10 perl int(rand(29)) drand48   seeds=1293840000..1420070400  best=-13.4240 @1407171031  hits>-12.5=0  168.1s
gen=11 POSIX lrand48()%29           seeds=1293840000..1420070400  best=-13.4078 @1346769480  hits>-12.5=0   93.0s
```

**So a slice has been swept, and this lane will not claim otherwise.** What that
slice is worth is a separate question, and the answer is: very little. Four
counts, each measured elsewhere in this repo:

1. **Decoder.** `sweep32x.c: decode_score()` branches over F-nulls and nothing
   else. It has **no key-skip or drift model at all** — it is `rigid_decode`
   with an interrupter fork. `round12/D3` measured rigid at **−6.835 on the
   correct key**, indistinguishable from noise. Doctrine §4.3 and B-04 §2 both
   name this a guaranteed false negative. Coverage × power ≈ coverage × 0.
2. **Adjudicator.** An English 4-gram table. Round 18 L7-A: power **0.33** Latin,
   **0.00** vowel-dropped English. English-only coverage, and doctrine R3's
   language-agnostic statistics were not persisted, so the rows cannot be
   re-interpreted.
3. **Threshold.** A fixed `−12.5` bar. `LEDGER.json` entry **B-21** says of that
   family's bar: *"STATISTICALLY INVALID at full-32 scale because the null max
   grows with trial count."* The reported best, −13.42, sits below the bar by
   less than the null's own spread.
4. **Breadth.** 1 reduction of 9. ~2.9 % of the seed space (1.26 × 10⁸ of 2³²).
   Offset 0 only. No Atbash. No sign axis — only `dir`.

**The corrected prior statement**, which G2 recommends for the ledger and for
L1's row 3:

> Perl 5.14 `rand`/`srand` — ranked 3rd (×2.5) on physical evidence (F6/F7).
> **Swept at ~2.9 % of the seed space, 1 of 9 reductions, offset 0, through a
> rigid decoder and an English-only adjudicator against an invalid threshold**
> (`round10/L5-seed32`). Coverage without power. Never swept through a
> drift-capable decoder or a multi-register adjudicator.

The prior itself is undamaged: F6 (46/46 signed messages on
`GnuPG v1.4.11 (GNU/Linux)`, 2012–2014, unchanged) and F7 (1.4.11 is Ubuntu
11.04–12.04's package) still put Perl 5.14.2 on the box as the system Perl.
Only the "never swept" clause was wrong, and correcting it *strengthens* the
case for re-running: this is not virgin ground, it is ground swept with a
broken magnet — the exact situation lane S2 exists to exploit.

---

## 4. Instrument state and the hold

**Nothing in this lane was scored.** As of this writing
`round19/I1/driftbeam.py`, `round19/I2/adjudicate.py` and `round19/I3/vecbeam.py`
exist but none of the three has published a PASS verdict. Per the campaign
plan's hard dependency and doctrine R1, G2 stops at the scoring boundary.

What was run instead, and explicitly labelled:

* **`plant.py` → `plant.json`** — the pre-registered positive control artifact.
  5 registers (EN, LP1 orthography, Latin, half-vowel EN, no-vowel EN) × 3
  constructions (`nodrift`, `keyskip`, `skip_by_two`) = 15 cells, each carrying
  plaintext, ciphertext, true and foil keystreams, and the skip trace. Desync is
  realistic: 6 events over 154 runes under `keyskip` (1 per 25.7), 4 events with
  a final key drift of 10 under `skip_by_two`. Seed **1389657600** was fixed in
  `PREREG.md` §Q1 before any of this was built, so the control cannot be tuned
  to a result.
* **`pilot.py` → `pilot.json`, `pilot_rows.jsonl`** — a **plumbing pilot**,
  hard-capped at 10,000 decodes, run only because both gate files exist. It
  wires validated G2 keystreams → I3 `vecbeam.batch_decode` → I2 `adjudicate` →
  `to_row`, over 4 cells × 8 orientations. **9,984 decodes, 9,984 SWEEPROWs, 0
  `validate_row` failures.** Every output file is stamped `"is_result": false`
  and `"scores_are_not_findings": true`. No score was compared to a threshold,
  no candidate escalated, and the seed block is deliberately arbitrary
  (base 700,000,000) rather than the high-prior band, so that it cannot be
  mistaken for coverage.

### 4.1 Measured rates (the deliverable Phase 2 actually needs)

End-to-end per core, 6 cores detected:

| tier | reduction | L | mode | end-to-end /s/core |
|---|---|---:|---|---:|
| screen | `r29` | 31 | keyskip1 | **663** |
| escalate | `r29` | 120 | keyskip1 | 106 |
| escalate | `r29` | 120 | skip_by_two | 108 |
| escalate | `r29_nodup` | 120 | keyskip1 | 160 |

Three observations handed to the instrument lanes:

* **To I2** — at L=31 `adjudicate_batch` is *slower* than the per-row
  `adjudicate` (700/s vs 1,344/s), because its internal 400-row chunking does
  not amortise on smaller blocks. At L=120 it is 50× faster (21,837/s). Phase
  2's screen tier lives exactly in the regime where the fast path loses.
* **To I1/I3** — permissive modes cost an order of magnitude:
  `vecbeam --bench` at L=120, 1 core: `keyskip1` 168/s, `skip_by_two` 174/s,
  **`drift3` 12.8/s, `union0_5` 8.7/s.**
* **To I3** — `vecbeam --bench` reports the null **max over only 8,192** random
  trials at L=31 as **−5.550**, i.e. the legacy −5.5 bar is already breached by
  noise at n = 10⁴; and `drift3`/`union0_5` score *random* data at mean **−4.510**
  and **−4.817**. Under a permissive relation the score scale moves wholesale and
  no fixed bar survives. G2's screen tier exists only if I3's null curve at
  L = 31 leaves usable selectivity.

### 4.2 The arithmetic that decides Phase 2

Full Stage A is 3.09 × 10¹¹ decodes. At the measured Python screen rate of
3,977/s on 6 cores that is **21,597 hours**. The in-repo C precedent —
`round10/L5-seed32` sweeping *this same generator* at 46,933 decodes/s/core —
is **71× faster**, which turns the same cell into **305 hours**, and
`2³² × r29 × 8 orientations` into **34 hours**.

**So the space is enumerable, but only in C.** The complete ladder, its
caveats, the exactness gate a C screen must pass, and the Python-only fallback
are in [`READY.md`](READY.md) §3–4.

---

## 5. The three conditionals (doctrine Q4) — pre-declared for the eventual negative

There is no negative to report yet. When Phase 2 produces one it will carry all
three or it is not a result:

1. **Key space** — the seed slice actually enumerated, the reductions run, the
   sign/Atbash/direction/offset ladder. Named exclusions: per-call re-seeding;
   a stream offset by an unknown number of `rand` draws consumed elsewhere in
   the same process; reductions outside the nine; CPAN PRNG modules
   (`Math::Random::MT`, `Math::Random::Secure`) which are a different family;
   Perl builds not using drand48.
2. **Decoder transition model** — whichever constructions I1's relation
   represents. `plant.json` supplies `keyskip`, `skip_by_two` and `nodrift` so
   this can be stated as a measurement rather than a hope.
3. **Adjudicator register** — whichever of I2's nine panel registers were
   scored, at I3's recalibrated thresholds, with the four doctrine-R3 statistics
   persisted per row (proven emittable: 9,984/9,984 rows valid).

---

## 6. Coverage — what was measured here, and what was NOT

**Measured by this lane:**

* `gen_perl.py` reproduces Perl 5.14.2's `rand`/`srand` byte-exactly — 186
  checks, 0 failing, across 9 reductions, 13 seeds, 2,000 draws per cell, and a
  glibc cross-check on the era's actual library function.
* The seed space is exactly 2³², with no residue, including the un-seeded case.
* The `srand()` argument-coercion divergence between 5.14 and 5.40 is
  characterised and shown not to affect coverage.
* Real end-to-end throughput of the Phase-2 pipeline on this box.

**NOT measured by this lane, and not to be inferred from it:**

* **Any score, bound, exclusion or negative.** Nothing here excludes any Perl
  seed. The 9,984 pilot decodes are timing data.
* The power of I1/I2/I3 against a G2 keystream — that is G2-GATE-Q1, still to run
  (cost: 15 decodes; artifact already on disk).
* Whether the L=31 screen has usable selectivity at n ≈ 10⁹ — this depends
  entirely on I3's null curve and is the single biggest open question for G2.
* Perl builds configured `-Drandfunc=random` or `-Drandfunc=rand`. Configure
  prefers `drand48` on any host that has it and glibc has it, so an Ubuntu 12.04
  stock package cannot be one of these — but a hand-built Perl could, and this
  lane did not sweep those two backends.
* The 5.14 `srand` string-coercion column, which is derived from source reading
  rather than executed (§1.3).

---

## 7. Reopens / next actions

* **Immediately, at a cost of 15 decodes:** I1/I2/I3 run **G2-GATE-Q1** against
  `plant.json` and report score, rune-recovery and true-minus-foil margin per
  (construction × register) cell.
* **I3 publishes the null curve** for (L, mode, statistic) up to n = 10¹⁰.
  G2's screen tier stands or falls on the L = 31 row.
* **Build the C screen** (`READY.md` §4.3, steps C-1..C-3, with the mandatory
  exactness gate). This is the difference between covering 0.2 % and covering
  100 % of the top reductions.
* **File the ledger correction** of §3 against `B-21` and against L1 §6.2 row 3.
* This lane is not closed and states no verdict. It ends where doctrine R7 says
  it should: with what was measured, what was not covered, and the concrete
  condition — Phase 0 publishing PASS — that opens the next step.

---

## 8. Trust anchor — after

```
python3 liber-primus/tests/validate.py
```

→ see the run log below; recorded at the end of the lane, unchanged from the
pre-run state.

```
PASS  Runes - 01.jpg   4/4 words  score= -4.48  via atbash+shift+0
PASS  05.jpg           3/3 words  score= -4.98  via shift+0
PASS  06.jpg           3/3 words  score= -4.13  via atbash+shift+3
PASS  03.jpg           4/4 words  score= -4.34  via vigenere DIVINITY (+7 interrupters)
PASS  14.jpg           4/4 words  score= -4.24  via vigenere FIRFUMFERENFE (+2 interrupters)
=== ALL VALIDATIONS PASSED — rig reproduces known solves. ===
```

---

## 9. Files

| file | what |
|---|---|
| `PREREG.md` | pre-registration; the five Aiming Test answers; locked bounds |
| `gen_perl.py` | the validated generators + keystream interface |
| `validate.py` → `validation.json` | the three gates and their test vectors |
| `ref_perl.pl`, `ref_reduce.pl`, `ref_drand48.c` | the real-Perl and glibc references |
| `probe_coerce.sh` | the `srand()` coercion probe |
| `report_validation.py` | human-readable digest of `validation.json` |
| `plant.py` → `plant.json` | the pre-registered positive control for G2-GATE-Q1 |
| `bench.py` → `bench.json` | generator and reference-beam throughput |
| `pilot.py` → `pilot.json`, `pilot_rows.jsonl` | the labelled plumbing pilot (**not a result**) |
| `budget.py` → `budget.json` | the arithmetic behind READY.md |
| `READY.md` | the Phase 2 run spec |
| `ledger.json` | this lane's ledger entries, for merge |
