# ROUND 19 / G4 — TeX/LaTeX-INTERNAL GENERATORS — PRE-REGISTRATION

_Lane G4, Phase 1 of Round 19. Binding: `liber-primus/ARMADA-DOCTRINE.md`.
Written 2026-08-26, **before any keystream was produced and before any decode was scored.**
Trust anchor run first: `python3 liber-primus/tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)**._

> **Order of work, stated honestly.** Between the trust anchor and this file the lane did two
> things and only two: (a) installed TeX Live in WSL and downloaded the era-relevant package
> sources into `vendor/` (rebuildable by `fetch_sources.sh`), and (b) *read those sources* to
> extract the LCG constants that define the search space. Determining the size and shape of a
> space is pre-registration input, not measurement of the hypothesis. **No keystream had been
> generated, no LP2 rune had been decoded, and no score of any kind had been computed** when
> this file was written. §3's numbers are read off source code, not off results.

---

## 1. Hypothesis

**H1.** The LP2 0–54 keystream was generated **inside the typesetting document itself** — by a
TeX-side pseudo-random number generator invoked from the LaTeX source that produced the
6.00 × 9.00-inch runic PDF, and reduced to Z₂₉ by one of the idiomatic package calls
(`\pgfmathrandominteger{\x}{0}{28}`, `\rand` with `first=0,last=28`, `\setrannum{\c}{0}{28}`,
`\pdfuniformdeviate{29}`).

**H0.** No state of any of those generators, over the enumerated bound of §3, under any
enumerated mapping / sign / direction / reflection, produces readable plaintext.

**Why this is worth a lane, and why nobody has run it.** Every prior generator sweep in this
repository treated the pad as something produced by a *separate* program — a shell script, a
Python one-liner, a C program — and then pasted into the document. That is one hypothesis. The
other, never once considered here, is that there was no separate program: **the author was
already inside a TeX document, needed 12,956 random runes, and used the RNG that was in front of
them.** `liber-primus/LEDGER.json` has 62 entries; a keyword scan for `tex|latex|pgf|lcg|
typeset|allrunes` matches 15 of them **only** in prose (B-04's lore-file corpus, L1's font
verdict, D-0x notes) — **no entry in the ledger has a TeX-internal RNG as its hypothesis, in any
`status`, `coverage` or `not_covered` field.** This family is absent from the ledger, exactly as
`round18/L1-toolchain/RESULTS.md` §6.2 says ("never swept, never considered").

---

## 2. THE AIMING TEST (doctrine §1) — five answers

### Q1 — What would a hit look like, and would *this* instrument recognise it?

This lane has **two** instruments and only one of them is mine.

**(a) The generator validator — mine, and it is exact.** A "hit" at this stage is a Python
reimplementation whose output is **element-for-element identical to the output of the real TeX
binary**. The recognizer is `==` over integer lists, so its power is 1.0 by construction and its
false-positive rate is 0. There is no room for a friendly analogue: the reference sequences are
produced by running `pdflatex` / `tex` on this machine with the real packages, over 19 seeds ×
64 draws × every mapping, and the assertion is byte-exact equality. **A generator that fails
this gate does not produce a keystream and is reported as PROVISIONAL, not swept.** This is the
Round 8 standard and it is non-negotiable here because TeX's integer arithmetic (truncating
`\divide`, ±(2³¹−1) clamp, Schrage overflow avoidance) is exactly the kind of thing a
"mathematically correct" reimplementation silently gets wrong.

**(b) The decode adjudicator — *not* mine, and it is currently known-broken.** A Phase-2 hit
would be a `(generator, state, mapping, sign, direction, atbash, offset)` tuple whose keystream
turns LP2 into readable text. Round 18 **measured** that the current instrument would very
probably *not* recognise such a hit: L7-A puts its power at 0.33 for Latin and 0.00 for
vowel-dropped English, and L7-B shows the beam's transition relation is exact for exactly one
rejection-loop implementation and misses `skip_by_two` at −6.90 / 25.8 % recovery. **Therefore
this lane does not score anything.** It stops at the scoring boundary and hands validated
generators to S1, gated on I1 + I2 + I3. That is the whole point of the Round 19 hold, and
running a sweep now would be the precise mistake the round exists to correct.

**The control I *can* run inside the hold** (and will, in §5): a **ground-truth plant-and-
recover** that does not use the English adjudicator at all. Plant a pad drawn from the real TeX
binary at a known seed s\*, encipher a known plaintext with `sk.encipher_keyskip`, then run the
enumerator over a seed window containing s\* and rank candidates by **exact rune agreement with
the known plaintext**. Required: s\* ranks #1 at agreement 1.00. This proves the enumerator's
plumbing — indexing, direction, sign, offset, mapping — without borrowing power from an
instrument that has none yet.

### Q2 — What measured fact raises this family's prior above the flat rate?

`liber-primus/analysis/round18/L1-toolchain/RESULTS.md`, §6.1 facts **F4**, **F5**, **F2**,
**F6/F7**, and §6.2 rank 5 (**shift ×2**, "never swept, never considered"):

| fact | measurement | why it points at TeX |
|---|---|---|
| **F4** | the 58 page images are 400 dpi, 2400 × 3600 px = **exactly 6.00 × 9.00 inches** (§3.1) | a trade-paperback page geometry. That is a *typesetting job with a page size*, not an image-editor canvas |
| **F5** | the runes are **typeset from a proportional font** — uniform stroke, 29 distinct glyphs, advance widths 34 px → 64 px (§5.1) | the runes existed as **character data** before they were pixels, i.e. a text-based authoring path |
| **F10** | the face is **none of** 11 stock Unicode runic faces, measured with three passing controls (§5.2); it differs chiefly in *proportion* | rules out "typed Unicode runes in a desktop font". §6.1 F10 names the `allrunes` LaTeX package as the live alternative (NC-5) |
| **F2** | the renderer is **Ghostscript** `-sDEVICE=jpeg -r400`, with an Artifex sRGB ICC profile (§2) | the source document was **PDF or PostScript** — the output format of a TeX run |
| **F6/F7** | GnuPG 1.4.11 (GNU/Linux) on 46 of 46 signed messages, 2012–2014; an Ubuntu 11.04–12.04 imaging stack | the era pins *which* TeX Live, and therefore which package versions, are in scope (§3.0) |

L1's own conclusion, quoted: *"a 6×9-inch typeset PDF full of runic characters is a LaTeX-shaped
job, and `allrunes` is **the** LaTeX Anglo-Saxon runic package. If the pad was generated inside
the document, the generator is a TeX LCG with a tiny period."*

This is a prior derived from **render parameters and glyph metrics on a held artifact**, which
is what doctrine R4 means by evidence. It is not lore.

### Q3 — Is the space bounded, and by what?

**Bounded and enumerable.** Three of the four generators are **Lehmer (multiplicative-
congruential) generators modulo 2³¹−1 implemented in TeX integer arithmetic with Schrage's
trick**, which means each has a *single cycle* of length 2³¹−2 covering every non-zero residue.
The fourth is Knuth's 55-lag subtractive generator with a seed space collapsed to 2²⁸ by the
seeding code. Full sizes, and the tiering, are in §3. Two consequences worth stating up front
because they *shrink* the declared space rather than inflate it:

1. **The offset ladder is redundant for the three Lehmer generators.** Advancing the keystream
   by `o` positions from seed `s` lands on the same single cycle as starting from some other
   seed `s'`. So "all seeds × all offsets" = "all phases", and B-04's 10-entry offset ladder and
   B-02's key-index-0 assumption are both *absorbed*, not merely swept. **This is the first
   generator family in this repository where that is true.**
2. **A constant added to the reduced key is a Caesar on the plaintext.** `{0}{28}` and `{1}{29}`
   differ by exactly +1 mod 29, so the two idiomatic call forms are one stream plus a declared
   constant `c ∈ {0,1}`. General `c ∈ Z₂₉` is *not* covered and is named in §7.

### Q4 — What three conditionals will the negative carry?

Any negative this lane's generators eventually produce is conditional on:

1. **Key space** — the enumerated bound of §3, at the tier actually reached, with the covered
   fraction stated per generator (`READY.md` states the full-enumeration cost so the fraction is
   never implicit).
2. **Decoder transition model** — whichever transition relation I1 ships. This lane will not run
   against the Round-18 beam, because L7-B measured that it represents exactly one rejection-loop
   implementation.
3. **Adjudicator register** — whichever panel I2 ships. This lane will not run against the
   English-only quadgram scorer, because L7-A measured its power at 0.33 (Latin) and 0.00
   (vowel-dropped English).

Every `SWEEPROW` written in Phase 2 will carry doctrine R3's four language-agnostic statistics.

### Q5 — What single observation kills this lane at 10 % of budget?

Two kill conditions, both checkable before any sweep:

* **K1 (validation).** If fewer than **two** of the four generators reproduce real TeX output
  byte-exactly after a fixed debugging budget, the lane is reported **INCONCLUSIVE**, its
  generators are marked PROVISIONAL, and it does not hand anything to S1. A generator I cannot
  reproduce exactly is a generator whose null means nothing.
* **K2 (prefilter power, checked at 10 % of the Phase-2 budget).** The full-phase enumeration in
  `READY.md` depends on a fast rigid prefilter surviving the true phase. If the plant-and-recover
  control shows the planted phase failing to survive a 10⁻³ prefilter cut in ≥ 50 % of 200
  planted trials, the full-enumeration plan is **abandoned** and the lane is restricted to Tier 1
  (the small, high-prior, directly-beam-decodable seed sets of §3.4).

---

## 3. THE SPACE — exact parameters, read from source

### 3.0 Which TeX is era-correct

Ubuntu 11.04 (natty), 11.10 (oneiric) and 12.04 LTS (precise) all ship **TeX Live 2009**
(`texlive-*` source version `2009-*`; e.g. `texlive-latex-extra 2009-10ubuntu1` in precise).
TeX Live 2009 bundles **pgf 2.00**. A user who installed pgf from CTAN any time from Oct 2010
onward had **pgf 2.10**. Both were checked (§3.1). `random.tex` is v0.2 and has been unchanged
for decades; `lcg` is v1.3 (2013/08/09) in the current tree and v1.x throughout the era.

Verification of the pgf question is in §3.1: the generator core is **byte-identical** across
pgf 2.00, pgf 2.10 and current CTAN pgf 3.1.x, so the era question is moot for this lane.

### 3.1 T1 — pgf / pgfmath (`\pgfmathrandominteger`, `random(a,b)`, `rnd`)

Source: `vendor/pgf_2.00src/pgf-2.00/generic/pgf/math/pgfmathrnd.code.tex` (TeX Live 2009 era)
and `vendor/pgf_2.10/tex/generic/pgf/math/pgfmathfunctions.random.code.tex`. `diff` of the two
shows the *only* changes are macro renames for `\pgfmathdeclarefunction` and the addition of the
`random(a,b)` parser hook — **`\pgfmathgeneratepseudorandomnumber` itself is byte-identical**,
and current CTAN pgf differs only by a `z=0 → z=1` guard on the default seed.

```
\def\pgfmath@rnd@m{2147483647}   % m = 2^31 - 1
\def\pgfmath@rnd@a{69621}        % a   <-- NOT 16807. 16807 appears only in a comment
\def\pgfmath@rnd@q{30845}        % q = m div a
\def\pgfmath@rnd@r{23902}        % r = m mod a
```

Transition (Schrage, exactly as the TeX macro sequences it):

```
hi = z div q                      (TeX \divide truncates toward zero)
lo = z - q*hi                     ( = z mod q )
z' = a*lo - r*hi
if z' < 0:  z' += m
```

Default seed, if `\pgfmathsetseed` is never called: `\c@pgfmath@counta = \time`,
`\multiply by \year` → **seed = (minutes since midnight) × (year)**, `\time ∈ [0,1439]`.

Mappings (one raw draw per output, verified in source):
* `\pgfmathrandominteger{\x}{0}{28}` → `x = z mod 29`
* `\pgfmathrandominteger{\x}{1}{29}` → `x = (z mod 29) + 1`  (same stream, `c = 1`)
* `\pgfmathparse{random(1,29)}` → routes to `\pgfmathrandominteger{...}{1}{29}` (pgf ≥ 2.10)
* `\pgfmathparse{int(rnd*29)}` → a **different** stream: `rnd` is built from `z mod 100001`
  rendered as a 5-decimal fixed-point number, so the mapping is `floor(29 · ((z mod 100001)/10⁵))`
  clipped into `[0,28]`. Included as `pgf_rnd29`.

**Space.** `\pgfmathsetseed` was measured (both pgf 2.10 and pgf 3.1.11a) to accept the full
integer range up to 2147483646 — see `tex/ref_pgf.txt` `SEEDACCEPT` lines; the fixed-point
overflow one might expect from `\pgfmathparse` does **not** occur. So:

| sub-space | size | enumerable? |
|---|---:|---|
| full phase space (= all seeds × all offsets, single cycle) | **2 147 483 646** | yes |
| default seed `\time × \year`, years 2010–2015 | **8 627** distinct | trivially |
| "an author typed a number": 0 … 2²⁰ plus B-04's integer dictionary | ≈ **1.05 × 10⁶** | trivially |

### 3.2 T2 — the `lcg` package (`\rand`)

Source: `vendor/lcg.dtx.ctan` (v1.3, 2013/08/09) and the installed `lcg.sty`.

```
a = 16807   q = 127773   r = 2836   m = 2147483647     % Park-Miller "minimal standard"
```

`\r@nd` transition is Schrage again, in the same truncating-`\divide` arithmetic. `\rand` then
does **rejection sampling**, which pgf does not:

```
R    = last - first + 1
lim  = R * (m div R)                       % for R=29:  lim = 2147459628
draw z ; if z > lim: redraw (recursively)
result = first + (z mod R)
```

For `R = 29` the rejection region is `z ∈ [2147459629, 2147483647]`, i.e. 24019 of 2³¹−1 states
(1.1 × 10⁻⁵). The emitted symbol stream is therefore the master `z mod 29` stream with a sparse,
deterministic set of positions **deleted** — still a single deterministic master stream, so
sliding-window enumeration still applies.

Seeding: `seed=<n>` is a raw `\count` assignment (no fixed-point parser), so the full
`1 … 2³¹−1` is directly settable. Default when unset:
`cr@nd = (((time + inputlineno) × page + year) × month × day) + inputlineno`.

**Space:** full phase space **2 147 483 646**, enumerable. The *default* seed depends on
`\inputlineno` and `\value{page}` as well as the clock, so it is **samplable, not enumerable**
within this budget — declared as such in §7.

### 3.3 T3 — `random.tex` (Donald Arseneau, v0.2)

Source: `vendor/random.tex.ctan` (CTAN `macros/generic/random/random.tex`), and the installed
copy at `/usr/share/texlive/texmf-dist/tex/generic/random/random.tex`.

Same Lehmer core as `lcg` — `a = 16807, q = 127773, r = 2836, m = 2³¹−1` — but a **completely
different reduction**, by division rather than remainder, so the symbol stream is unrelated:

```
\setrannum{\c}{lo}{hi}:
    R = hi - lo + 1
    B = 2147483645 div R                   % for R=29:  B = 74051160
    repeat:  z = nextrandom ;  v = (z - 1) div B
    until v < R
    c = v + lo
```

Seeding: `\randomi` is a `\count`, directly settable to any of `1 … 2³¹−1`. Default when zero:
`randomi = ((time × 388 + year) × 31 + day) × 97 + month`, **followed by three discarded warm-up
draws** (`\nextrandom \nextrandom \nextrandom`) — a detail a naive reimplementation gets wrong.

**Space:** full phase space **2 147 483 646**, enumerable. Default-seed space
`1440 × 6 years × 31 × 12` = **3 214 080`, also enumerable (the file's own comment calls this
"a sparse initialization, giving fewer than a million different starting values").

### 3.4 T4 — pdfTeX `\pdfuniformdeviate` / `\pdfsetrandomseed`

Not named in the lane brief, but it belongs here and may be the **most** idiomatic of the four:
it is a *primitive of the engine itself* (no package to load), it was present in pdfTeX from
1.30 (2005) and therefore in TeX Live 2009's pdfTeX 1.40.x, and `\pdfuniformdeviate{29}`
returns 0…28 in one call — literally "give me a random rune index".

Algorithm: Knuth's **55-lag subtractive (lagged-Fibonacci) generator** on 28-bit `fraction`
values, inherited from METAFONT/MetaPost (`init_randoms`, `new_randoms`, `unif_rand`,
`take_fraction`), with `fraction_one = 2²⁸ = 268435456`. `init_randoms(seed)` first does
`j = |seed|; while j >= 2²⁸: j /= 2`, which **collapses the seed space to 2²⁸**.

**Space:** **268 435 456** distinct seeds, enumerable. The state is 55 words, so trajectories
from different seeds are disjoint and **the offset ladder is NOT absorbed here** — B-04's ladder
is retained for T4 only. The *default* seed is set from the wall clock in microseconds and is
**not** enumerable; only `\pdfsetrandomseed{n}` is.

### 3.5 T5 — LuaTeX `math.random` — declared a DUPLICATE of G1, not swept here

LuaTeX 0.4x–0.7x embeds Lua 5.1/5.2, whose `math.random` is `l_rand()` → the platform C
`rand()`, and `math.randomseed(x)` → `srand(x)`. On glibc, `rand()` *is* `random()` — the TYPE_3
additive-feedback generator. **That space is G1's, not G4's**, and sweeping it here would be a
duplicate. What G4 contributes instead is the *scaling*: Lua 5.1's
`math.random(m,n)` = `floor(((rand() % RAND_MAX) / RAND_MAX) · (n−m+1)) + m`, which is **not**
`rand() % 29`. G4 hands that mapping to G1 rather than re-enumerating glibc.
Era note: LuaTeX was beta in TeX Live 2009 and was not a plausible engine for a book-length
2013 document; pdflatex or xelatex were. T5 is demoted on that ground too.

### 3.6 Derivation axes (B-04 conventions, `round13/B04/PREREG.md` §3.4–3.5)

| axis | values | note |
|---|---|---|
| sign | `−1`, `+1` | key subtracted / key added |
| direction | `fwd`, `rev` | reversed Lehmer = the cycle read backwards; a **separate** phase enumeration, not absorbed |
| atbash | off, on (`i ↦ 28 − i` on the ciphertext) | as B-04 |
| constant | `c ∈ {0,1}` | the `{0}{28}` vs `{1}{29}` call forms. General `c ∈ Z₂₉` is a Caesar and is **not** covered — §7 |
| offset | **absorbed** for T1/T2/T3; `{0,1,4,16,29,64,128,256,512,1024,3301}` for T4 | see Q3 |

### 3.7 Space accounting — the honest totals

Per-generator, at **full** enumeration, counting decodes as
`phases × streams × sign(2) × dir(2) × atbash(2) × c(2)`:

| id | stream families | phases / seeds | full-enumeration decodes |
|---|---|---:|---:|
| T1 pgf | `mod29`, `rnd29` | 2 147 483 646 | **6.87 × 10¹⁰** |
| T2 lcg | `mod29+reject` | 2 147 483 646 | **3.44 × 10¹⁰** |
| T3 random.tex | `divscale+reject` | 2 147 483 646 | **3.44 × 10¹⁰** |
| T4 pdfTeX | `uniformdeviate29` | 268 435 456 × 11 offsets | **4.72 × 10¹⁰** |
| | | **total** | **≈ 1.85 × 10¹¹** |

At this repository's measured beam throughput — B-04 stage A did 1 385 600 decodes in 1003 s on
this same 6-core box, i.e. **≈ 1 400 decodes/s** — full enumeration by beam alone is
**1.3 × 10⁸ s ≈ 4.2 years**. It is *enumerable* but **not affordable by direct beam decoding**,
and `READY.md` says so in those words rather than pretending otherwise. The route that makes it
affordable (a vectorised rigid prefilter over the single master cycle, ~hours, then beam on
survivors) is specified in `READY.md` §3 and is **gated on I1/I2 measuring its power** — it is a
proposal with a control attached, not a promise.

---

## 4. INSTRUMENT — the validation gate (this lane's only measurement)

`gen_tex.py` reimplements T1–T4 in Python, reproducing TeX's arithmetic (truncating integer
division, the sign test, the ±m fold, the recursive rejection, the three discarded warm-ups).
`make_vectors.sh` runs the **real** binaries — `pdflatex` on `tex/ref_pgf.tex`,
`tex/ref_lcg.tex`, `tex/ref_random.tex`, `tex/ref_pdf.tex` — and `validate.py` asserts equality.

Reference-vector design, fixed here in advance:

* **19 seeds** per generator: `1, 2, 3, 29, 3301, 16383, 16384, 65535, 100000, 1000000, 2000000,
  2147483646, 1033, 761, 845145127, 1595277641, 1386342, 2013, 4026` — small, boundary,
  Cicada-numeric (3301/1033/761/845145127/1595277641 from B-04 §3.1 `num_*`), and a
  `\time × \year` default-seed value (`1386342 = 688 × 2013`).
* **64 consecutive draws** per (seed, mapping).
* Mappings per generator as listed in §3.1–3.4, including the raw 31-bit state stream where the
  package exposes it, so a mismatch localises to *state* vs *reduction*.
* For pgf, the vectors are generated **twice**: once against installed pgf 3.1.11a and once
  against the vendored **pgf 2.10** tree via `TEXINPUTS`, and both must agree with Python.

### Gates (all fixed before running)

| gate | requirement | consequence if failed |
|---|---|---|
| **V1** | Python == real TeX, **element-for-element**, for every seed × mapping × draw, for **each** of T1–T4 | that generator is **PROVISIONAL** and produces no keystream |
| **V2** | ≥ 2 of the 4 generators pass V1 | else lane = **INCONCLUSIVE** (kill condition K1) |
| **V3** | pgf 2.10 vectors == pgf 3.1.11a vectors | else the era question is live and both are swept separately |
| **V4** | full-period check: for each Lehmer multiplier `a`, `a^((m−1)/p) ≢ 1 (mod m)` for every prime `p | m−1`; and the state returns to the seed after exactly `m−1` steps for a sampled seed | else the "single cycle ⇒ offsets absorbed" claim in Q3 is **withdrawn** and the offset ladder is reinstated |
| **V5** | ground-truth plant-and-recover (§5): planted seed ranks #1 at rune agreement 1.00 | else the enumerator's plumbing is wrong and no null from it is a negative |

**V4 is load-bearing.** The single-cycle argument is what lets this lane claim the offset ladder
is absorbed. If it does not hold, the declared space grows by 11× and the claim comes out.

---

## 5. Positive control — ground truth, no adjudicator

`control.py`, run inside the hold:

1. Take `s* = 3301`, generator `pgf`, mapping `mod29`, `sign = −1`, `dir = fwd`, `c = 0`.
2. Draw the pad from the **real TeX binary** (not from Python) for `L = 120` symbols.
3. Encipher 120 runes of LP-style English with `sk.encipher_keyskip(sign=−1, supp=0.83, seed=3301)`.
4. Enumerate a window of 20 001 phases centred on the phase of `s*`, across all
   sign × dir × atbash × c combinations, decoding rigidly **and** by beam.
5. Rank by **exact rune agreement with the known plaintext** — a ground-truth statistic, *not*
   an English score, so it borrows no power from the instrument Round 18 measured as broken.

**PASS** iff the planted configuration ranks #1 with agreement 1.00 under the rigid alignment of
the pad itself, and the beam recovers ≥ 0.90 of the runes through the key-skip filter.
This is ≤ 1.3 × 10⁵ decodes, i.e. inside the ≤ 10 000-decode *scored* pilot allowance because
**none of it is scored** — it is compared against known plaintext.

---

## 6. Decision thresholds

This lane produces **no decode threshold**, because it does not adjudicate. Its thresholds are
V1–V5 above, all exact/binary. Phase 2's HIT bar is I3's to set; it is *not* pre-registered here
and this lane must not be read as having set one.

If the Phase-0 lanes `round19/I1/driftbeam.py` and `round19/I2/adjudicate.py` exist at the time
`READY.md` is written, a **labelled pilot of ≤ 10 000 decodes** may be run **solely** to prove
plumbing and measure throughput. It is labelled `PILOT — NOT A RESULT`, its scores are recorded
but explicitly not interpreted, and no candidate is escalated from it.

---

## 7. What this lane explicitly does NOT cover (declared in advance)

* **General Caesar on the reduced key** — only `c ∈ {0,1}` (the two idiomatic call forms) is in
  scope. A key produced by, say, `\pgfmathrandominteger{\x}{5}{33}` is outside the bound.
* **The `lcg` default seed**, which depends on `\inputlineno` and `\value{page}` as well as the
  clock — samplable, not enumerable, and not sampled here.
* **The pdfTeX default seed**, set from wall-clock microseconds — not enumerable at all.
* **Non-integer or per-page reseeding** — an author calling `\pgfmathsetseed` once per page, or
  once per line, is outside the bound (this is B-04's stage-C shape and is a named follow-up).
* **Rejection loops other than the packages' own.** The pad-generation rejection modelled here is
  the one *inside the RNG call*; the anti-repeat filter applied to the *cipher* is I1's model, and
  L7-B says the current one is wrong. That is why this lane holds.
* **`\pgfmathdeclarerandomlist` / `\pgfmathrandomitem`** — a plausible authoring shape ("declare
  a list of 29 runes, pick randomly") which reduces to `\pgfmathrandominteger{}{1}{29}` and is
  therefore covered *as a stream*, but whose list ordering would impose an unknown permutation of
  the rune alphabet. The permutation is **not** covered.
* **XeTeX** — `\uniformdeviate` was not a XeTeX primitive in the TeX Live 2009 era; if a source
  surfaces showing xelatex + `allrunes`, T4's mapping applies but the seeding differs.
* Any generator external to the document — that is G1/G2/G3's territory.

---

## 8. Side-deliverable (evidence for L1, not for the sweep)

L1's **NC-5** is open: the `allrunes` Type-1 faces are in L1's font bank as files but are
custom-encoded, so its codepoint-based matcher could not test them. This lane has a working TeX
installation, which is the tool that turns `allrunes` into rendered glyphs. Where it is cheap to
do so, G4 records what it can observe about whether the LP2 pages are plausibly `allrunes`-
typeset — **as an observation with its own control, reported separately in `RESULTS.md` §6, and
never mixed into the generator verdict.** If the observation cannot be made with a control, it is
reported as "not measured" rather than as an impression.

---

## ADDENDUM — 2026-08-26, after running the V5 control, before writing `RESULTS.md`

_Doctrine §4.1: a threshold is never edited after seeing a result; an addendum is appended
with the reason. Nothing above this line has been altered._

**What happened.** §5 required the planted configuration to rank **#1 at agreement 1.00**
under rigid alignment. It ranked **#2 of 80 004** at agreement 0.3833; rank #1 was the *same*
phase advanced by **2** steps, at 0.3917.

**Why the criterion as written was unattainable, and this is a property of the cipher, not of
the enumerator.** `sk.encipher_keyskip` consumed key indices 0…121 to emit 120 runes — two key
skips. A rigidly aligned decoder therefore cannot match the whole segment from any single
phase: the best rigid phase is *the planted phase advanced by the number of skips*, because
that alignment fits the longer tail. Requiring rank 1 at agreement 1.00 was requiring the rigid
decoder to be exact for a cipher that Round 18's L7-B says it cannot be exact for. That is the
mistake this round exists to correct, and I made a small version of it inside my own gate.

**What is measured instead — V5a, fixed now, before `RESULTS.md`:**

> the planted phase must appear within the top `1 + n_skips` of the rigid ranking, the rigid
> argmax must lie within `±(1 + n_skips)` phases of the planted phase and carry the planted
> sign and atbash, the skip-aware beam at the planted phase must recover **≥ 0.90** of the
> known plaintext, and the top rigid agreement must exceed the wrong-phase null maximum by
> **> 0.10**.

**Both are reported.** `control_results.json` carries `V5_status_as_prereg: FAIL` and
`V5a_status: PASS`, and `RESULTS.md` reports both, in that order, with this reason attached.

**A consequence Phase 2 must inherit.** Because the rigid optimum sits at planted-phase + skips,
a phase prefilter must retain a **band** of phases, not a point: a top-K cut that keeps
isolated maxima can discard the true phase while keeping its neighbour. `READY.md` §3 turns
this into a requirement on the cut, and it is the single most useful thing this control found.
