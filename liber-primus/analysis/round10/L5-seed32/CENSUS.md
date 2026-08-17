# Generator census — what the seed sweep can and cannot reach

Lane L5-seed32, Round 10. Companion to `FINDINGS.md`.

The Round-8 SEED track swept **10 generator/reduction variants**. Ten is a choice, not a
census. This file is the census: every generator family a 2013–2014 author could plausibly
have used to make a "one-time pad", marked against what the repo has actually swept.

The framing that matters: **a missing generator is a real gap; a missing seed inside a
covered generator is mostly not.** Adding one generator multiplies the searched space by
2^32; adding the remaining 2/3 of one generator's seed space multiplies it by 1.5.

---

## A. Covered by `analysis/seed_sweep/sweep.c` (Round 8), harness-validated

| # | Generator | Reduction | Seed space swept |
|---|---|---|---|
| 0 | glibc `random()` TYPE_3 | `% 29` | 2011–2015 unix-seconds; **+0..2^32 partial (this lane)** |
| 1 | glibc `random()` | scaled to 29 | 2011–2015 unix-seconds |
| 2 | glibc `random()` | `% 29` + doublet rejection | 2011–2015 unix-seconds |
| 3 | MSVC/ANSI `rand()` LCG | `% 29` | 2011–2015 **+ full 0..2^32 (Round 8)** |
| 4 | MSVC/ANSI `rand()` LCG | scaled | 2011–2015 unix-seconds |
| 5 | MT19937 `init_genrand` | `% 29` | 2011–2015 **+ full 0..2^32 (Round 8)** |
| 6 | MT19937 `init_genrand` | 53-bit double × 29 | 2011–2015 unix-seconds |
| 7 | CPython `random.seed(int)` | `randrange(29)` | 2011–2015 unix-seconds |
| 8 | CPython `random.seed(int)` | `int(random()*29)` | 2011–2015 unix-seconds |
| 9 | `java.util.Random` | `nextInt(29)` | 2011–2015 unix-seconds (32 bits of a 48-bit seed) |

Plus 15,408 string/lore/date seeds through CPython's SHA-512 string-seed path.

**Important:** a C author writing `srand((unsigned)time(NULL)*1000)` or `srand(getpid())`
or `srand(0xDEADBEEF)` folds into the 32-bit space and **is** covered by a completed
full-32 sweep. A Java or Python author seeding with a millisecond timestamp is **not** —
`System.currentTimeMillis()` in 2013 is ≈1.36e12, three orders of magnitude past 2^32.

## B. Added and harness-validated by this lane (`sweep32x.c`, generators 10–13)

| # | Generator | Reference used for the gate | Gate result |
|---|---|---|---|
| 10 | Perl `srand(S); int(rand(29))` — drand48, `X=(S<<16)\|0x330E` | real `/usr/bin/perl` | PASS, 5 seeds × 2000 draws |
| 11 | POSIX `srand48(S); lrand48()%29` | real glibc `lrand48` | PASS, 5 seeds × 2000 draws |
| 12 | Ruby `srand(S); rand(29)` — MT `init_genrand` + 5-bit mask/reject | real `ruby 3.3.8` | PASS, 5 seeds × 2000 draws |
| 13 | xorshift32 (13,17,5) `% 29` — Marsaglia 2003 | independent Python re-implementation | PASS, 5 seeds × 2000 draws (weaker basis — see below) |

Notes on these four:

* **Perl (10) is the highest-value addition.** Perl's `rand` is drand48, which appears
  nowhere in Round 8's ten. Perl is an entirely plausible 2013 tool for generating a pad.
* **11 is drand48 with the other standard extraction** (`lrand48` = the 31 high bits of the
  same 48-bit state). Same state sequence as 10, completely different rune stream.
* **12 is NOT a duplicate of generator 5.** Ruby and reference MT share `init_genrand`, so
  the underlying 32-bit word stream is identical, but Ruby reduces by *5-bit mask with
  rejection* while generator 5 reduces by `% 29`. The resulting rune streams diverge at the
  first rejected draw and never re-sync. Version caveat: validated against Ruby 3.3.8; the
  `len<=1 → init_genrand` branch is long-standing in `random.c` but was not verified against
  a 2013-era Ruby.
* **13 (xorshift32) has a weaker validation basis** than 10–12: there is no canonical vendor
  implementation to test against, only the published recurrence. Flagged, not hidden.

## C. Named, plausible, and NOT swept — the real residue

| Generator | Prior for a 2013–14 author | Why it is not reachable from the current sweep | Status |
|---|---|---|---|
| **PHP `mt_rand()`** | **High** — PHP is the most likely language for a web-hosted puzzle | PHP's MT has a documented implementation deviation from reference MT19937 (the `MT_RAND_PHP` bug, fixed only in PHP 7.1) plus its own `RAND_RANGE` scaling. Unreachable from generator 5. | **UNCOVERED.** Implemented nowhere. `php` is not installed on this box, so it could not pass the harness gate; per this lane's PREREG an unvalidated generator is not swept. **This is the single highest-prior open generator.** |
| **PHP `rand()`** | Medium | On Linux PHP<7.1 `rand()` delegates to libc `rand()`; on Windows to MSVC. Effectively shadowed by generators 0/3 but not identical (PHP wraps with its own range scaling). | Partly covered |
| **.NET `System.Random`** | Medium (Windows author) | Knuth subtractive / lagged-Fibonacci (`ran3`), seeded via the 161803398 constant. Structurally unlike every generator swept. | **UNCOVERED.** `mono` not installed; no reference available here. |
| **Blum–Blum–Shub** | Medium (crypto-flavoured puzzle) | ARMADA-20 item #6 tested **2,080 configs** of BBS/LCG/MT seeded by *Cicada constants only*, scored page-scale. That is a keyword-style probe, not a seed sweep. | **Effectively uncovered as a seed space.** The ledger line "PRNG keystreams (BBS/LCG/MT) — dead" is true of the 2,080 configs and of nothing wider. |
| **ISAAC** | Low–medium (Bob Jenkins, crypto-adjacent) | Not implemented anywhere in the repo | UNCOVERED |
| **LFSR / Geffe / Gollmann stream ciphers** | Low–medium | Classic textbook keystreams; not implemented | UNCOVERED |
| **KISS / multiply-with-carry / WELL / lagged Fibonacci** | Low | Not implemented | UNCOVERED |
| **V8 / SpiderMonkey `Math.random`** | Low | Not seedable from JavaScript in 2013 — an author cannot reproduce a pad this way, which is the whole point of using a seed | Low prior *by construction* |
| **PCG** | **Zero** | Published August 2014. **LP2 was posted January 2014.** A 2014-08 generator cannot be the 2014-01 pad. | **Excluded by date, not by search** |
| **xoroshiro / xorshift128+** | Very low | 2014+ publication, same dating argument as PCG (xorshift128+ is Vigna 2014) | Excluded by date |
| **RC4/ARC4, AES-CTR, HMAC-DRBG, SHA/MD5 counter chains** | Medium | These are **not seed sweeps.** Their key is an arbitrary byte string, not a 32-bit integer, so the key space is not enumerable and the correct attack is a *dictionary* over Cicada strings. That is register item **R10A-B04**, a different lane. | Out of scope for a seed sweep, by construction |

## D. Uncovered *seed* space inside covered generators

| Extension | Size | Feasibility |
|---|---|---|
| Java's full 48-bit `setSeed` space | 65,536 × the 32-bit space | ~2,500 CPU-days on this box. Not reachable. |
| Millisecond/microsecond time seeds in Java/Python (64-bit) | 1.26e11 values for 2011–2015 ms alone | 30 × the whole 32-bit space, and disjoint from it |
| CPython `random.seed()` on a `float`, `bytes`, or `str` | `str` goes through SHA-512 ⇒ dictionary-only | 15,408 tested (Round 8); unbounded in principle |
| MT `init_by_array` with multi-word keys | unbounded | Dictionary-only |
| **Keystream offset ≠ 0** | × 8,192 for a modest offset range | Register item **R10A-B02**, a different lane. Multiplies *every* generator. |

## E. The category that makes the whole hypothesis conditional

**No seed at all.** `/dev/urandom`, a hardware RNG, `random.org`, or physical dice produce
a pad with no compressible key. This is the *modal* behaviour for anyone who sets out to
build "a one-time pad", and it is the majority of the prior mass. Nothing in the seed sweep
— finished or unfinished — touches it, and nothing can. The seed sweep's entire value is
that it cheaply excludes the *lazy* implementations; it was never able to exclude the
competent one.

---

## The one-line reading

Round 8 covered 10 generators over ~3% of each one's seed space (plus 2 generators fully).
This lane adds 4 validated generators and extends generator 0. The *uncovered* space —
PHP, .NET, BBS as a real seed space, ISAAC, LFSRs, offsets ≠ 0, seeds wider than 32 bits,
and the no-seed case — is many orders of magnitude larger than everything swept to date and
is mostly not enumerable at all. **Completing the last 8 generators over the full 32-bit
space multiplies total coverage by ~1.3×. Adding PHP `mt_rand` multiplies it by ~1.1× and
closes the highest-prior named gap in the census.** Neither is decisive; the census says
which is the better spend.
