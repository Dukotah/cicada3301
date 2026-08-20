# Round 16 — THE PUBLIC PAD — synthesis

_Ran 2026-08-19/20. Five lanes, all pre-registered in [`PREREG.md`](PREREG.md) before any sweep.
**Zero hits.** The value is not the null — it is three corrections to load-bearing claims, one
of which is a closing argument this project has repeated in four places._

## What this round tested and why it was new

The repo's taxonomy of the keystream had two branches: a **short-seed derived** keystream
(finite, being swept) and a **private pad** (information-theoretically closed). The seed census
folds everything else into the second branch with a single sentence, repeated verbatim in
`round10/L5-seed32/CENSUS.md:87-94`, `handoff/PARKED.md:273-278` and
`ELIMINATION-LEDGER.md:365-368`:

> **No seed at all.** `/dev/urandom`, a hardware RNG, **random.org**, or physical dice produce a
> pad with no compressible key … Nothing in the seed sweep — finished or unfinished — touches
> it, **and nothing can.**

That sentence merges two independent properties. Dice and `/dev/urandom` leave **no seed and no
record** — genuinely closed. random.org, NIST's Randomness Beacon, a blockchain and a printed
random-number table leave **no seed but a permanent public record**. That is a *third branch*:
a full-entropy pad with no seed that is nevertheless enumerable today. It had never been swept,
because the taxonomy had no name for it.

**Second gap, independent of the first.** Every external-pad sweep in this repo walked a coarse
offset ladder — A1 used **eight offsets per keystream variant**. On the 118,818,811-byte
`560.13` pad that is 7e-8 of the offset space. `lib_padsweep.dense_scan` scores **every** offset.

## Results

| lane | pad family | offsets scored | best | bar | verdict |
|---|---|---|---|---|---|
| **P0** | A1's CicadaOS blobs, re-swept densely | 3,911,819,734 | −6.769 | −5.500 | NEGATIVE |
| **P1** | Bitcoin, heights 0–303,726 | 1,389,182,016 | −6.802 | −5.500 | NEGATIVE |
| **P2** | NIST Beacon v1 + RANDOM.ORG | 3,464,597,548 | −6.811 | −5.500 | NEGATIVE |
| **P3** | RAND digits + 3301's published bytes | 5,757,316,748 | −5.679 | −5.500 | NEGATIVE |
| **P4** | filter fingerprint (no pad) | — | — | — | **MACHINE** |

**≈14.5 × 10⁹ offsets scored, ≈8.4 × 10⁹ effective** after each lane's own measured prefilter
survival. Every lane's planted control recovered at 100 % of runes; every best score sits inside
or below its own null band; `threshold_for()` at each lane's true trial count is **stricter**
than the fixed −5.5 bar in all four cases, so no verdict here depends on which bar you use.

## The three corrections

### 1. "Nothing can touch it" was wrong about random.org — measured, not argued

Lane P2 went and got it. random.org has published a **1 MiB file of true random bytes every day
since 2006-03-11** (7,395 files). Direct HTTP on an old day returns 403, but the monthly
`.torrent` and `.md5` files are free: P2 pulled **153 files covering 2013-09 → 2014-01 and
verified 153/153 against the published MD5s**. NIST Beacon v1 likewise still serves the 2013 era
through its legacy endpoint (the v2 API cannot — it clamps to chain 1 pulse 1, 2018-07-23).

The durable artifact is P2's source table: which public randomness sources have a retrievable
pre-2014 archive, which are live-only **with cause** (ANU QRNG's only bundle died with CloudStor
in 2023-12; HotBits keeps no records by design), and which post-date LP2 (NIST v2, drand). That
converts a closing argument into a measured list — and it leaves one live item:

> **The Marsaglia Random Number CDROM (1995)** — 634,124,288 bytes of published random data with
> published SHA-256s, range-GET-able from archive.org. **Found, not swept.** Highest-prior
> unswept item this round produced.

### 2. The anti-repeat hardening was applied by a MACHINE, not by hand

`FINAL-SYNTHESIS.md:73-76` states as fact that a *human calligrapher applied a "don't write the
same rune twice" rule by hand while inscribing the book*, and that claim is load-bearing for the
attribution profile. Nothing had ever tested it. Register item **D-01** is now run.

- Every human-randomness model with any signature beyond the bare immediate-repeat rule is
  **excluded at ≥0.99 power**. Pooled lag 2–8 bleed is z = **+0.65** — zero bleed, and the sign
  is wrong for a human.
- **The bound:** lag-1 suppression is 80.75 %, and any lag-2..8 suppression above **1.70 %** is
  excluded at 95 % (2.87 % at 99 %). Under 1/47 of the lag-1 effect leaks anywhere else.
- **Scope test, power 1.000:** the filter had no per-line scope — 4/86 doublets cross a line
  boundary (4.65 % vs a 4.58 % base), where a person checking "the rune I just wrote" would
  leave ~22.9 %.
- Reported honestly as **UNDERPOWERED (0.110)**: whether a human eye applying *only* that one
  rule to a machine pad is separable. It is not, and cannot be in principle — such a stream *is*
  the coded filter's output.

Consequence for the search: the pad's bytes came out of a program or a file, so imported-byte-source
lanes are the right target, and a **human-key-prior joint decode should not be built** — there is
no exploitable non-uniformity to exploit. Bonus: this is the first independent confirmation of the
skip-aware beam's cipher model against the real data (flat, unscoped, single-lag, supp ≈ 0.813).

### 3. Two instrument defects, one of which narrows A1's published bound further

- **`max_skip=3` is underpowered on pads with constant byte runs.** P1's strict control *failed
  on its real pad* at A1's setting (6/8 plants): display-order block hashes are 18.4 % zero bytes,
  and a constant key run makes the filter burn skips without changing the key symbol. At ms=8:
  60/60, gate 12/12.
  **P0 then measured it on the CicadaOS pads and found it does not bite there** — 20/20 at both
  budgets, 91/91 rows bit-identical, max |Δ| = 0.000000 — and explained why: `beam_decode` admits
  a skip only if every skipped key position would reproduce the previous cipher rune (p≈1/29
  each), so on a high-entropy pad the *validity test* binds, not the budget. Those ISO-carved
  blobs are 0.4 % zero bytes with a longest constant run of 4 bytes in 118 MB. P2 independently
  measured the same non-effect on iid beacon pads. The fix is real; its scope is narrow; all
  three lanes measured rather than assumed.
- **`ks_hexchars` silently dropped the digits 0–9** (`eng_to_idx` discards non-letters), so it
  swept the **A–F subsequence** of hex text — 36.8 % of the string — not the hex reading. That hit
  the highest-prior variant of the hex-published beacon pads. `ks_nibbles` was added and every
  affected pad re-swept. Still negative.
- **The round's flat ×0.625 survival discount is not a constant.** Measured per pad: P2 got 0.875
  on 6.4 MB but 0.500 on 95 MB; P0 got 0.750 / 0.583 / 0.500 / 0.375 / 0.542 and — importantly —
  found the decay **is not monotone** (118.8 MB scored *higher* than 4 MB). At n=24 that is ~1.2
  SE, i.e. noise. The defensible claim is **≈0.4–0.55 above 1 MB, driven by pad statistics at
  least as much as by size**, not a clean size law. Every lane restated its effective coverage
  downward accordingly; nobody used the round constant.

## Coverage bounds (the reusable numbers — read these, not the verdicts)

- **P0** — 6 distinct blobs (`tmp_folly` and `tmp_wisdom` are byte-identical), 196 configs, full
  cross product on `560.13` plus `nibbles` and ms=8 passes. **Includes the 1,580,426-byte tail of
  `_560.00` that A1 provably never held** — every tail offset scanned, four reached the top 20,
  all in the −6.93/−6.96 noise band. A1's shuffle nulls reproduced exactly (−6.995, −7.037), so
  the instrument is comparable to the published run.
- **P1** — heights 0–303,726 verified contiguous (LP2 posted at height ~277,000, ~26,700 blocks of
  headroom), hashes and merkle roots in **both byte orders**, nonces, timestamps; 7 builders ×
  fwd/rev × 2 signs × every offset, escalated at two skip budgets. Verified four ways before
  sweeping, including reassembling 80-byte headers and double-SHA256-ing them back to the stored
  hash. **Not excluded:** non-contiguous selections (every-Nth block, retarget blocks), other
  chains, txids, coinbase scriptSigs, chainwork.
- **P2** — 6 pads / 179,913,984 B / 96 configs. Beacon `outputValue`+`seedValue` 2013-09-05 →
  2013-10-11 (6 builders) and → 2013-11-13 (`nibbles`); RANDOM.ORG 2013-09-01 → 2014-01-31.
- **P3** — 28 pads / 112.6 MB, swept twice (ms=3, then ms=8 with `nibbles`). **13 pads are shorter
  than ~13k keystream symbols** and were swept against the head window only: their negative means
  only "does not key the first 25–400 runes". Only RAND was reachable for the printed-table family
  — no machine-readable Tippett / Kendall / Fisher–Yates exists.

## What this round did NOT exclude

The public-pad branch is **narrowed, not closed**. Unswept and named: the Marsaglia CDROM;
non-contiguous blockchain selections; the beacon beyond 2013-11-13; other chains and fields;
keystream builders outside the seven tested; and the prefilter's measured ~45–60 % blind spot on
large pads, which is a power limit rather than a soundness one (beam recovery was 100 % on every
plant, in every lane).

Per `AGENTS.md` §7, read the coverage bounds above rather than the word NEGATIVE. This round
exists because the last closing argument was read as a verdict when it was a bound.

## Follow-ups this round generated

1. **Sweep the Marsaglia CDROM** (634 MB, published SHA-256s, range-GET-able). Cheapest live item.
2. **Register item A-03** — the haplography count-audit of the 86 doublet sites — is now the
  cheapest falsifier of P4's *positive* result: if a high-zoom re-read merges ~20 doublet
  neighbourhoods, P4 §3 and §6 move. Already Lane 2 of the Round 15 plan.
3. Re-derive the prefilter survival law properly (n=24 per pad is too thin to separate a size
  effect from a pad-statistics effect).
