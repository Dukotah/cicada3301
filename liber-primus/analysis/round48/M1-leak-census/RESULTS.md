# Round 48 / M1 — RESULTS: the leak is not a coin; LP2 is not the output of eight library generators

_Filed 2026-11-27. Pre-registration: `PREREG.md` (sha256 stamped in `run.log` before the first output, and again
with each addendum). This lane was run as an independent fresh pass at the owner's request, outside the Round 48
plan of record. No solve. Verdict on the cipher: **OTP-class, unchanged.**_

## 0. Headline

1. **The pinned "coin" (`supp = 0.813`) is a fit, not a mechanism, and it is not identified.** Three unrelated
   constructions reproduce LP2's lag-1 leak equally well, and none can be told from the coin at LP2's size:
   a **zero-parameter** no-repeat picker over 35–37 symbols, a deletion model, and a two-layer shift model.
2. **Every plain redraw loop over a uniform 29-rune key is rejected.** Redraw-once gives ≈ 15 doublets,
   redraw-until-different gives 0, byte-level and Latin-letter no-repeat rules give ≈ 398 and ≈ 115. LP2 has 86.
3. **Nothing tested reproduces T7** (doublet-gap autocorrelation +0.380): ≤ 0.5 % of replicates of any admitted
   mechanism reach it. T7 stays unexplained.
4. **LP2 is not the direct output of a seeded library PRNG driving that picker**, for 8 generators × all 2³²
   seeds × 24 picker variants × 2 rune orders × every alignment: **0 exact reproductions** of 14 runes
   (24/24 planted runs recovered). With an extra generator call at each word start (Arm B2, five generators):
   **0** as well (§3).

## 1. Arm A — mechanism census (`census.py`, `census.json`, `census.log`)

LP2: D = 86 doublets in 12,955 adjacent pairs (447 expected), lag-2…8 equal count 3,162, doublets on two-letter
runes 24, triples 0, T7 r1 = +0.380. 400 replicates per mechanism at N = 12,956. Brackets are the central 99 %.

| mechanism | free params | doublets D | two-letter-rune doublets | verdict |
|---|---|---|---|---|
| Z0 no filter | 0 | 445.3 [398, 501] | 107.9 | reject |
| Z1 redraw once | 0 | 15.5 [6, 29] | 3.7 | reject |
| Z2 redraw until different (= Z5) | 0 | 0 | 0 | reject |
| Z4 picker, m = 30 / 31 / 32 / 33 | 0 | 15.3 / 29.3 / 43.6 / 55.6 | — | reject |
| **Z4 picker, m = 34** | 0 | 68.1 [49, 88] | 16.8 | **ADMIT** |
| **Z4 picker, m = 35** | 0 | 78.3 [57, 103] | 18.9 | **ADMIT** |
| **Z4 picker, m = 36** | 0 | 90.0 [69, 112] | 22.0 | **ADMIT** |
| **Z4 picker, m = 37** | 0 | 99.4 [75, 122] | 24.2 | **ADMIT** |
| **Z4 picker, m = 38** | 0 | 108.6 [82, 135] | 26.4 | **ADMIT** |
| Z4 picker, m = 39 / 40 / 64 | 0 | 118.4 / 126.1 / 248.0 | — | reject |
| Z6 byte no-repeat, mod 29 | 0 | 398.5 [349, 442] | 91.1 | reject |
| Z7 byte no-repeat, drop ≥ 232, mod 29 | 0 | 397.2 [356, 443] | 96.2 | reject |
| Z9 Latin-letter no-repeat | 0 | 114.5 [91, 142] | 114.5 | reject (all its doublets are on two-letter runes; LP2 has 24 of 86) |
| F1 coin (pinned model) | 1 fitted | 86.0 [62, 110] | 20.9 | ADMIT |
| F2 hard filter, then delete 18.7 % of runes | 1 fitted | 85.8 [65, 110] | 20.8 | ADMIT |
| F3 hard filter, then a second-layer shift that changes w.p. 0.186 | 1 fitted | 86.4 [63, 109] | 20.6 | ADMIT |

**Z4(m)** = "pick a random symbol out of m, never the same as the last pick; symbols ≥ 29 print nothing but are
still remembered as the last pick". A doublet appears only when a non-printing pick falls between two equal
runes, so D ≈ N·(m − 29) / ((m − 1)·29): 79 / 89 / 99 for m = 35 / 36 / 37. No parameter is fitted.

**Separability from the coin** (rejection rate at α = 0.05, best of gap-KS / triples / lag-2, no multiplicity
correction, so it can only overstate):

| mechanism | best power | |
|---|---|---|
| Z4 m = 34 | 0.435 | separable in principle, weakly |
| Z4 m = 35 | 0.138 | NOT SEPARABLE |
| Z4 m = 36 | 0.070 | NOT SEPARABLE |
| Z4 m = 37 | 0.098 | NOT SEPARABLE |
| Z4 m = 38 | 0.288 | weak |
| F2 | 0.060 | NOT SEPARABLE |
| F3 | 0.060 | NOT SEPARABLE |

LP2's own gap distribution against the coin: KS 0.071 (critical 0.141). It does not prefer any of them.

**T7.** Fraction of replicates with r1 ≥ 0.380: 0.000–0.005 for every admitted mechanism. None produces it.

### What Arm A means

- The repo's generative model says "uniform key, and a rejected doublet is redrawn with probability 0.813".
  That probability was fitted to the one number it explains. A zero-parameter rule explains the same number.
  **"The filter is a coin" should not be read as a measured fact about how the pages were made.**
- The three admitted families imply **different constructions**:
  - Z4: the alphabet behind the pages has **35–37 symbols**, of which 29 print as runes. The 6–8 others are
    consumed silently (candidates: space, punctuation, digits, a null). Under this reading the non-printing
    symbols sit *between* runes in the true sequence and their positions are lost.
  - F2: the printed stream has **lost about 19 % of its runes** after a strict no-doublet rule was applied.
  - F3: there are **two additive layers**, one strict-no-repeat, one piecewise-constant with mean run ≈ 5.4.
- LP2's lag-1 statistics cannot choose between them (power ≤ 0.14 for the best cases). Any decoder that hard-codes
  the coin's transition model is covering one of at least four constructions that fit equally.

Limits: 400 replicates; statistics limited to D, lag-2…8, two-letter-rune count, gap KS, triples, lag-2; the
m = 35–37 picker was noticed in an exploratory pass before registration (PREREG §0), so its row is a replication.

## 2. Arm B — generator-reproduction sweep (`repro.c`, `sweep.log`)

Hypothesis H-B: the unsolved pages are generator output with no plaintext under them. Recognizer: 14 consecutive
printed runes reproduced exactly (no language model, no bar). Every generator was checked against a live library
or an independent reference first (`validate_gens.json`, 8/8), and a known-seed run planted in LP2 was recovered
for every generator and reduction (`plants.json`, 24/24; plants are 24–40 runes, see PREREG Addendum 1).

| generator | seeds | 5-gram prefilter passes | near (10–13 runes) | **hits (≥ 14)** |
|---|---|---|---|---|
| Perl `drand48` (seed<<16 \| 0x330E) | 2³² | 136,742,560 | 8 | **0** |
| bash 4.2 `$RANDOM`, LP64 | 2³² | 143,224,800 | 6 | **0** |
| bash 4.2 `$RANDOM`, ILP32 | 2³² | 143,227,933 | 8 | **0** |
| glibc `srand`/`rand` (TYPE_3) | 2³² | 143,211,773 | 9 | **0** |
| CPython 2.7 `random.seed(int)` → `random()` | 2³² | 143,211,164 | 11 | **0** |
| MSVC `rand` | 2³² | 143,127,970 | 2 | **0** |
| ANSI C LCG | 2³² | 143,291,760 | 8 | **0** |
| Park–Miller minstd | 2³² | 143,196,988 | 8 | **0** |

Per seed: m = 29…40, reductions `x mod m` and `floor(x·m / range)`, gematria and Atbash rune orders, generator
start aligned to any of the 12,956 positions. Total ≈ 8.2 × 10¹¹ (seed, picker) streams, each tested against
every position. Wall clock 3 h 34 min (cap 4.5 h).

Near-misses: 60 in total, 58 of length 10 and 2 of length 11; none ≥ 12. Chance predicts about 7 per generator
(≈ 1.4 × 10⁸ five-rune matches × 29⁻⁵), i.e. ≈ 55. They are noise, and the absence of any 12- or 13-rune run
is what noise looks like. MSVC's 2 is low (Poisson p ≈ 0.03 before allowing for eight generators); its plant
was recovered, so it is reported, not explained.

**Coverage × power.** Coverage: the product above, complete. Power: 1.00 by construction for a stream inside it
(exact match; plants 24/24). Conditionals of this negative:

1. **Key space:** these 8 generators, seeds 0…2³² − 1, generator freshly seeded at the aligned position.
   Not covered: seeds wider than 32 bits (drand48 has 48 state bits, MT19937 seeded from a long or a string,
   `/dev/urandom`), other generators (PHP `mt_rand`, Java `Random`, JavaScript, Perl < 5.20 on non-glibc, TeX
   LCGs, Windows CryptoAPI), a generator that had already been advanced before the first
   printed rune of its run.
2. **Transition model:** the Z4 picker with one raw draw per symbol and the 29 runes at indices 0–28 (or
   reversed). Not covered: a shuffled symbol table, the non-printing symbols placed elsewhere than at the top,
   `randint`/`choice`/`shuffle` wrappers with their own rejection loops, extra draws between runes (Arm B2 covers
   one case), F2- or F3-type generation.
3. **Register:** none. No language scorer is involved.

## 3. Arm B2 — extra generator call at each word start (`repro2.c`, `sweep2.log`)

Same picker, with e ∈ {1, 2} raw draws skipped before the first rune of each printed word; alignment at the 55
page starts; m = 29…40, both reductions, both rune orders. Plants 15/15 recovered by the final binary
(`plants2.json`). Run 2026-11-27T01:53:13Z → 2026-11-27T05:05:52Z.

| generator | seeds covered | near (10–13 runes) | **hits (≥ 14)** |
|---|---|---|---|
| Perl `drand48` | 2³² (all) | 0 | **0** |
| bash 4.2 LP64 | 2³² (all) | 0 | **0** |
| bash 4.2 ILP32 | 2³² (all) | 0 | **0** |
| glibc `rand` | 2³² (all) | 1 | **0** |
| CPython 2.7 | 2³² (all) | 0 | **0** |

All five generators completed every seed. 1 near-miss in total, as expected: only 55 alignments are tried per stream instead of 12,956.

Conditionals: as §2, with the transition model widened to "one raw draw per symbol plus e ∈ {1, 2} discarded draws
at each printed word start". Not covered: e > 2, extra draws at punctuation or line breaks, a length draw that
feeds the picker's memory, generation that did not restart at a page start, MSVC / ANSI / minstd.

## 4. Reproduce

```bash
cd liber-primus/analysis/round48/M1-leak-census
python3 census.py                                   # Arm A, ~10 min
python3 common.py && gcc -O3 -march=native -fopenmp -o repro repro.c
python3 validate_gens.py && python3 plants.py       # generator cross-checks, 24 plants
./run_sweep.sh                                      # Arm B, ~3.6 h on 4 cores
python3 layout.py && gcc -O3 -march=native -fopenmp -o repro2 repro2.c && python3 plants2.py
./run_sweep2.sh                                     # Arm B2, 3 h cap
```

## 5. Reopens if

- Any artifact fixes the size of the symbol table used to make the pages (a 35–37-symbol table would promote Z4
  from "admitted" to "prior"), or shows deleted material (F2) or a second layer (F3).
- An independent stream of filtered events appears that can separate the admitted mechanisms (LP2's 86 doublets
  cannot).
- A toolchain fact names a generator or seed width outside §2's list.
