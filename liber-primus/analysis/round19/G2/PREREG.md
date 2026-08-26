# ROUND 19 / LANE G2 — PRE-REGISTRATION
## Perl 5.14 `rand` / `srand` as the LP2 pad generator

_Written before any keystream was produced or scored. Binding:
[`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
Trust anchor run first, 2026-08-26: `python3 liber-primus/tests/validate.py`
= **ALL VALIDATIONS PASSED (5/5)**._

> **THE HOLD.** Phase 0 (I1 driftbeam, I2 adjudicator, I3 thresholds) is not
> finished. This lane produces **validated generators, a keystream interface and
> a written statement of the space**, and then stops at the scoring boundary.
> Nothing in this document authorises a scored sweep. See `READY.md` for the
> Phase 2 run spec.

---

## 1. Hypothesis

**H1.** The LP2 0–54 keystream is the output of Perl 5.14's `rand`, seeded by
`srand` (explicitly or implicitly), reduced to Z₂₉ by one of the forms a 2012
Perl author would write, and applied additively under the repo's pinned soft
anti-repeat filter.

**H0.** No 32-bit drand48 initial state, under any enumerated reduction / sign /
Atbash / direction / offset, produces plaintext the Phase-0 instrument
recognises in any of its registers.

**Falsifiability.** H1 is falsified only over the region tabulated in §4, and
only at the power Phase 0 measures for it (doctrine R2, R7).

---

## 2. THE AIMING TEST (doctrine §1) — five questions, answered

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A hit is a `(seed32, reduction, sign, atbash, direction, offset)` tuple whose
keystream, run through the drift-tolerant decoder, yields readable text in one
of the adjudicator's registers across more than one page.

**I cannot answer the second half of Q1, and I am not pretending to.** The
recognizer is I1 + I2 and neither exists yet. Round 18 L7-A/L7-B measured the
*current* instrument at power 0.33 (Latin) and 0.00 (vowel-dropped English), and
at −6.90 / 25.8 % recovery against the `skip_by_two` construction. Running this
lane's space through that instrument would manufacture exactly the null Round 19
exists to prevent.

Therefore this lane's Q1 obligation is discharged as a **hard gate on Phase 2,
not as a claim**:

> **G2-GATE-Q1.** Before any G2 decode is scored, I1 and I2 must publish a
> plant-and-recover control *on a G2 keystream specifically*: plant an
> `int(rand(29))` pad from a known seed over LP-style plaintext in each of I2's
> registers, encipher under both `encipher_keyskip` and `skip_by_two`, and
> demonstrate the correct seed ranks #1 and clears I3's threshold. The measured
> recovery fraction and score margin are recorded in `RESULTS.md` and reported
> beside every coverage figure. **If that control is not run, G2's output is
> labelled INCONCLUSIVE, never NEGATIVE.**

What I *can* pre-commit is the plant itself, and this lane ships it:
`plant.py` builds the synthetic ciphertext from a declared seed so that I1/I2
can run the control without designing it after seeing results. The seed is
fixed here, in advance: **seed = 1389657600** (2014-01-14, the LP2 posting
window), reduction `r29`, sign −1, Atbash off, direction forward, offset 0.

### Q2 — What measured fact raises this family's prior above the flat rate?

`liber-primus/analysis/round18/L1-toolchain/RESULTS.md` §6.2, **row 3**:

> | 3 | **Perl 5.14 `rand`/`srand`** (drand48 under the hood) | **×2.5** | F7's era: Perl 5.14.2 is Ubuntu 12.04's system Perl and the default text-munging language of that generation of Unix user | **never swept** |

resting on §6.1 **F6** — *46/46 curated 3301 PGP messages, 2012→2014, are
`GnuPG v1.4.11 (GNU/Linux)`* (`corpus/A-primary-artifacts/ibotpeaches/messages/`)
— and **F7** — *GnuPG 1.4.11 specifically, which Ubuntu 11.04–12.04 LTS shipped
and Debian wheezy did not.* Ubuntu 12.04's system Perl is 5.14.2. F1/F8 add that
the author drove ImageMagick over a numbered page set **with defaults**, i.e.
was scripting rather than clicking.

That is a measurement on held artifacts, not lore. It ranks this family third of
eleven, **above four families that have been swept**.

**A correction to the citation, made before running (doctrine R6/R7).** L1's
"never swept" in that row is **wrong as written**, and this lane will not
inherit the error. `round10/L5-seed32/CENSUS.md` §B lists generator **10** as
`Perl srand(S); int(rand(29))`, harness-validated against `/usr/bin/perl`
(`VALIDATION.txt`), and `results_newgens.txt` records it as run:

```
gen=10 perl int(rand(29)) drand48  seeds=1293840000..1420070400  best=-13.4240 @1407171031  hits>-12.5=0  168.1s
```

So a slice **has** been swept. What that slice is, exactly, and why it is worth
almost nothing, is §5. The honest form of Q2's answer is: *the family is ranked
3rd on physical evidence, and the one prior sweep of it covered 3 % of the seed
space, one reduction of nine, and used a decoder the repo has since measured at
noise-level power on the correct key.*

### Q3 — Is the space bounded, and by what?

**Bounded, enumerable, and — unusually for this repo — with no residue.**

`|seed space| = 2³² = 4,294,967,296`, and that is a *complete* bound, not a
slice. Two independent facts close it:

1. **glibc `srand48_r` keeps only the low 32 bits of its argument** —
   `__x[2] = (unsigned short)(seedval >> 16); __x[1] = (unsigned short)(seedval & 0xffff); __x[0] = 0x330e`.
   Perl 5.14.2's `config_h.SH:2133` is `#define seedDrand01(x) srand48((Rand_seed_t)x)`.
   So *every* srand argument — a 64-bit integer, a numified string, a negative,
   `time`, `time ^ $$`, `time ^ ($$+($$<<15))` — folds into 0..2³²−1.
   Measured on this box: `srand(4294967297)` and `srand(1)` emit an identical
   stream.
2. **The un-seeded path is 32 bits too.** `util.c: Perl_seed()` in 5.14.2 reads
   `sizeof(U32)` — four bytes — from `/dev/urandom` and returns it; the
   fallback mixes `gettimeofday`/`getpid`/two stack pointers into a `U32`.

Fact 2 is the reason this lane is worth the budget. The most idiomatic thing a
2012 scripter writes is `perl -e 'print chr(int(rand(29))) for 1..13000'` with
**no `srand` at all** — and that does *not* escape into the unattackable
`/dev/urandom`-as-pad branch. Only 32 bits ever reach the generator. Contrast
`round10/L5-seed32/CENSUS.md` §D, where Java's 48-bit `setSeed` and Python's
millisecond seeds leave residue orders of magnitude past 2³²: **Perl leaves
none.** There is no "seeds wider than 32 bits" hole to name in `not_covered`.

Full cross product, using B-04's conventions (§3.4/§3.5 of
`round13/B04/PREREG.md`) so results are directly comparable:

| axis | size | note |
|---|---:|---|
| seed | 2³² | enumerable, complete |
| reduction | 9 | Perl-reachable (2 further C-only forms carried for de-dup accounting) |
| sign ∈ {−1,+1} | 2 | key subtracted / added |
| Atbash ∈ {off,on} | 2 | plaintext-alphabet reflection i ↦ 28−i |
| direction ∈ {fwd,rev} | 2 | keystream reversed |
| offset (Stage A) | 1 | pinned 0 |
| **Stage-A total** | **3.09 × 10¹¹** | |
| offset ladder (Stage B) | ×10 | {1,4,16,29,64,128,256,512,1024,3301} |

**3.09 × 10¹¹ decodes is not runnable through a beam decoder.** §4 states the
fraction actually covered, and `READY.md` states it in wall-clock. Doctrine R7:
a sampled fraction is reported as a fraction, never as "the space".

### Q4 — What are the three conditionals the negative will carry?

Every G2 negative will be reported as conditional on all three, in `RESULTS.md`,
or it is not reported:

1. **Key space** — the seed slice actually enumerated (§4), the 9 reductions,
   the sign/Atbash/direction/offset ladder. Named exclusions: a *per-call*
   re-seed, `rand` interleaved with other `rand` consumers in the same process
   (which shifts the stream by an unknown number of draws), and any reduction
   outside the nine.
2. **Decoder transition model** — whichever constructions I1's drift-tolerant
   relation can represent. If I1 covers `encipher_keyskip` + `skip_by_two` +
   free drift, that is what is excluded; anything else is not.
3. **Adjudicator register** — whichever of I2's panel registers (EN /
   LP1-orthography / Latin / OE / DE / CY / half-vowel / no-vowel) the run
   actually scored, at I3's recalibrated thresholds, with the four
   language-agnostic statistics of doctrine R3 persisted per row.

### Q5 — What single observation abandons this lane at 10 % of budget?

**KILL-1 (fires now, pre-Phase-2).** If Gate A or Gate B of `validate.py` fails
— my reimplementation does not match the real `perl`, or the real `perl` does
not match glibc `drand48` — the lane stops. An unvalidated generator does not
enter a sweep, and a mismatch on Gate B would mean the era question cannot be
retired by measurement, only by argument.

**KILL-2 (fires at 10 % of the Phase-2 budget).** After the first 10 % of
enumerated seeds, if the empirical score distribution over G2 rows is
statistically indistinguishable from I3's size-matched null **and** the
plant-and-recover control of G2-GATE-Q1 shows recovery below 0.90 on the
`skip_by_two` construction, the lane stops and reports INCONCLUSIVE rather than
spending 90 % more budget to produce a null whose power is known to be too low
to mean anything. This is the L7-B lesson applied in advance.

**KILL-3.** If I1 publishes a per-decode cost that makes 10⁸ decodes exceed the
round's wall-clock, G2 reduces to the seed bands of §4.2 and says so, rather
than silently sampling and reporting the full space.

---

## 3. Instrument (as of this pre-registration)

* **Generators** — `gen_perl.py`, this lane. Validated by `validate.py`; test
  vectors persisted in `validation.json`.
* **Keystream interface** — `gen_perl.make_ks(reduction, seed, nsym)`,
  deliberately parallel to `round13/B04/ks.py: make_ks(gen, red, seed, nsym)`
  minus the `gen` axis (in this family the generator *is* drand48; the only axis
  is the reduction).
* **Decoder** — I1's driftbeam. **Does not exist yet.** Not substituted with
  `campaign18_skip.beam_decode`, and explicitly not `rigid_decode`
  (`round12/D3`: rigid scores the *correct* key at −6.835, i.e. noise).
* **Adjudicator** — I2's panel + `SWEEPROW`. **Does not exist yet.**
* **Threshold** — I3's recalibrated `threshold_for()`. **Does not exist yet.**
  Doctrine §4.4: a fixed −5.5 bar is invalid at N = 10⁸ and this lane will not
  use one.

---

## 4. Exact bounds this lane commits to (locked)

### 4.1 Reductions — 9 Perl-reachable, ranked by era-idiomaticity

Rank 1 is not a judgement call: `perlfunc`'s own worked example for `rand` is
`$random = int(rand(10))`.

| rank | id | the Perl line | why it is here |
|---:|---|---|---|
| 1 | `r29` | `int(rand(29))` | *the* idiom; `perlfunc`'s own example shape |
| 2 | `r29_nodup` | `do { $k = int(rand(29)) } while ($k == $last);` | L1 §6.3 item 5 predicts precisely this loop from F8 + Round 17's machine-filter finding |
| 3 | `r32_rej` | `do { $k = int(rand(32)) } while ($k > 28);` | the unbiased power-of-two rejection a careful author writes |
| 4 | `r256_mod` | `int(rand(256)) % 29` | a scripter thinking in bytes |
| 5 | `r2p32_mod` | `int(rand(2**32)) % 29` | "give me a 32-bit random number", then reduce |
| 6 | `r255_mod` | `int(rand(255)) % 29` | the off-by-one of rank 4 |
| 7 | `r100_mod` | `int(rand(100)) % 29` | |
| 8 | `r1000_mod` | `int(rand(1000)) % 29` | |
| 9 | `r26_lat` | `chr(65 + int(rand(26)))` | a **letter** pad, read into runes through the repo's canonical Latin→futhorc map |

Carried for de-duplication accounting only, and **not** counted as Perl:
`raw48_mod` (`state % 29`) and `lrand48_mod` (`lrand48() % 29`). Perl never
exposes the 48-bit state, so both model a C author calling `srand48` directly.
`lrand48_mod` is CENSUS generator 11, already swept at rigid alignment.

**The distinction the task brief warns about, stated explicitly:**
`int(rand(29))` is a **scaled truncation of the top bits** of the 48-bit state
(`(29·x) >> 48`), while `state % 29` reads the **low bits**. The two streams
agree only by coincidence and diverge at the first symbol. A sweep that reduces
the raw state mod 29 and calls the result "Perl" has not tested Perl.
`1 + int(rand(29))` collapses onto `r29` under a 1-based rune table and is
therefore not a separate row.

### 4.2 Seed coverage — declared as a fraction, in priority order

Full enumeration of 2³² × 9 reductions is 3.09 × 10¹¹ decodes and is not
affordable. The commitment is a **banded enumeration**, in this order, with the
band boundaries fixed here:

| band | seeds | size | rationale |
|---|---|---:|---|
| **S0** | unix seconds 2013-01-01 … 2014-06-30 | 4.66 × 10⁷ | the LP2 authoring window; `srand(time)` |
| **S1** | unix seconds 2011-01-01 … 2015-01-01 | 1.26 × 10⁸ | the era band Round 8 and L5-seed32 both used, so results are comparable |
| **S2** | 0 … 2¹⁶ and 2³²−2¹⁶ … 2³²−1 | 1.31 × 10⁵ | small literals, `$$` (pid ≤ 32768), `srand(-1)` → 0xFFFFFFFF |
| **S3** | the `time ^ $$` and `time ^ ($$+($$<<15))` hulls around S1 | ⊆ S1 ∪ ±2³⁰ | see note |
| **S4** | uniform stratified sample of the remaining 2³² | stated as a fraction | covers the **auto-seeded** case, which is uniform on 0..2³²−1 |

**Note on S3 (a bounding argument, not a sample).** For `$$ < 2¹⁵`,
`time ^ $$` only flips the low 15 bits of `time`, so the achievable value set is
the union of aligned 32768-blocks over S1 — which, since S1 is contiguous and
far longer than 32768, is **exactly S1 rounded outward to 32768 boundaries**.
S3 for the simple idiom is therefore covered by S1 + 65536 extra values, not by
a separate sweep. The `$$+($$<<15)` variant reaches ~30 bits and is covered only
by S4.

**S4 is the honest core of the coverage claim.** Because the auto-seed is a
uniform `U32`, the *only* statistically meaningful coverage figure for the
un-seeded case is `(seeds swept) / 2³²`. That fraction will be reported as a
number, with its power, and never described as "the Perl space".

### 4.3 Sign / Atbash / direction / offset

Exactly B-04 §3.4–3.5, unchanged, so G2 rows are directly comparable to the
6.22 M B-04 rows and the 692 k R16-KDF rows:
sign ∈ {−1,+1}; direction ∈ {forward, reversed}; Atbash ∈ {off, on} applied as
the plaintext-alphabet reflection i ↦ 28−i; Stage A pins offset 0, Stage B
sweeps {1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301}.

### 4.4 Explicitly NOT covered (declared in advance)

* per-call or mid-stream re-seeding (`srand` called more than once)
* a stream **offset by an unknown number of `rand` draws** consumed elsewhere in
  the same script — this is a distinct, unbounded axis and is *not* the same as
  the §4.3 keystream offset, which shifts the reduced symbols, not the draws
* reductions outside the nine of §4.1
* Perl builds not using drand48 (`-Drandfunc=random`, `-Drandfunc=rand`); see
  `RESULTS.md` for why an Ubuntu 12.04 build cannot be one of these
* `Math::Random::MT` / `Math::Random::Secure` / any CPAN PRNG module — a
  different family, not `rand`
* the filter forms outside whatever I1 ends up representing

---

## 5. Prior art in this repo, and why it does not close the lane

`round10/L5-seed32` swept `gen=10 perl int(rand(29)) drand48` and `gen=11 POSIX
lrand48()%29` over 1293840000..1420070400. That is real coverage and this lane
does not re-run it blindly. It is also, on four counts, worth close to nothing:

1. **Decoder.** `sweep32x.c: decode_score()` branches over F-nulls only. It has
   **no key-skip / drift model at all** — it is `rigid_decode` with an
   interrupter fork. `round12/D3` measured rigid at **−6.835 on the correct
   key**, indistinguishable from noise. Doctrine §4.3 and B-04 §2 both call this
   a guaranteed false negative. Coverage × power ≈ coverage × 0.
2. **Adjudicator.** A 4-gram English table (`ngram.bin`). Round 18 L7-A: 0.33
   power on Latin, **0.00** on vowel-dropped English. English-only coverage.
3. **Threshold.** A fixed `-12.5` bar. B-21's own ledger entry says that bar is
   *"STATISTICALLY INVALID at full-32 scale because the null max grows with
   trial count"*. The reported best, −13.42, sits below the bar by less than the
   null's own spread.
4. **Breadth.** 1 reduction of 9; ~2.9 % of the seed space; offset 0 only; no
   Atbash; no sign axis (only `dir`); no language-agnostic statistics persisted,
   so doctrine R3 makes the rows un-reinterpretable.

**Ledger correction this lane will file:** L1 §6.2 row 3's "never swept" should
read "swept at ~3 % of seed space, 1 of 9 reductions, rigid decoder, English-only
adjudicator, invalid threshold — i.e. coverage without power". `B-21`'s coverage
field already says the right thing about Round 8; this extends it to L5-seed32's
generators 10–13.

---

## 6. Positive control shipped with this lane

`plant.py` emits the synthetic ciphertext for G2-GATE-Q1 from the seed fixed in
§Q1 (**1389657600**, `r29`, sign −1, Atbash off, forward, offset 0), under both
`encipher_keyskip` and, once I1 defines it, `skip_by_two`. Fixing the seed here,
in the pre-registration, is the point: the control cannot be tuned after seeing
the sweep.

---

## 7. Decision rule (fixed in advance, and deliberately deferred)

The HIT bar is **I3's**, not this lane's, and is **not** the habitual −5.5
(doctrine §4.4 forbids a fixed bar at this N). G2 commits now to:

* using `I3.threshold_for(n_decodes, statistic)` with the *actual* row count;
* reporting, beside it, G2's own empirical best-of-N ceiling over its own rows,
  since 10⁸ presumed-wrong decodes are the most honest null available;
* escalating any candidate over the bar to (a) full page 0, (b) the full
  12,956-rune unsolved stream, (c) a clean process — B-04 §5's rule, unchanged;
* the outcome labels **HIT / NEGATIVE / INCONCLUSIVE**, where INCONCLUSIVE is
  the mandatory label if G2-GATE-Q1's control has not been run.

---

## 8. Addenda

_None. Any change after the first scored decode is appended here, dated, with
its reason._
