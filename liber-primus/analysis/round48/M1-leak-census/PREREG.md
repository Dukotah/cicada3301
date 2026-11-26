# Round 48 / M1 — The leak is not a coin: mechanism census + generator-reproduction sweep

_Pre-registered 2026-11-26, before any output of this lane. The sha256 of this file is written to `run.log`
before the first script runs. Owner instruction for this lane: treat it as a fresh attempt; the doctrine's
ceremony is kept only where it protects the result (hypothesis, plant, bar fixed first)._

## 0. What was already seen (disclosed, not confirmatory)

An exploratory pass on 2026-11-26 (scratchpad, uncommitted) re-derived the flat statistics of the 12,956-rune
unsolved stream and noticed that the pinned generative model carries a free probability (`supp = 0.813/0.83`)
with no mechanism behind it. It also saw that a "pick a random symbol different from the last one" routine over
m symbols, with non-rune draws dropped but remembered, predicts `N·(m−29)/((m−1)·29)` doublets: 79 / 89 / 99
for m = 35 / 36 / 37 against 86 observed. **Arm A's result for that one family is therefore a replication of
something already looked at.** Everything else below was fixed before being computed.

## 1. Hypotheses

- **H-A (census).** The observed lag-1 leak (86 doublets where 447 are expected) can be produced by a
  deterministic, zero-parameter mechanism, and such mechanisms can be told apart from the pinned coin model.
- **H-B (reproduction).** The unsolved stream is the *direct output* of a seeded library PRNG driving such a
  picker — i.e. the pages are generator output, with no plaintext under them. If true, some (generator, seed,
  m, reduction) reproduces a run of the printed runes **exactly**.

H-B is the only reading of LP2 under which a hit is certain rather than probabilistic: an exact run of 14+
runes has no language model, no register, no beam and no bar to argue about.

## 2. Arm A — mechanisms and rule

Each mechanism is simulated at N = 12,956 (400 replicates; 29 uniform runes unless stated):

| id | mechanism | free parameters |
|---|---|---|
| Z0 | no filter | 0 |
| Z1 | on doublet, redraw once | 0 |
| Z2 | redraw until different | 0 |
| Z4(m) | no-repeat picker over m symbols, draws ≥ 29 dropped but remembered as "last"; m = 30…40, 64 | 0 |
| Z5(m) | same, but "last" = last *emitted* rune | 0 |
| Z6 | no-repeat on a raw byte, rune = byte mod 29 | 0 |
| Z7 | no-repeat on a raw byte, bytes ≥ 232 dropped (remembered), rune = byte mod 29 | 0 |
| Z9 | no-repeat on Latin transliteration characters (reject when the rune's first letter equals the previous rune's last letter) | 0 |
| F1(s) | coin: redraw with probability s (the pinned model) | 1, fitted |
| F2(δ) | redraw-until-different, then delete a random fraction δ of the stream | 1, fitted |
| F3(q) | redraw-until-different, then add a second-layer shift that changes with probability q per position | 1, fitted |

Statistics on each replicate and on LP2: doublet count D; summed lag-2…8 equal count; number of doublets on the
seven two-letter runes (TH EO NG OE AE IA EA); doublet-gap lag-1 autocorrelation r1 (T7).

**Rule (fixed).** A mechanism is ADMITTED iff LP2's D, lag-2…8 sum and two-letter-rune count each fall inside
the central 99 % of its replicates. For each admitted zero-parameter mechanism, separability from F1 is the
rejection rate at α = 0.05 of the best of {gap-distribution KS, triple count, lag-2 count} with F1 as null;
below 0.20 = NOT SEPARABLE. r1 ≥ 0.380 frequency is reported for every admitted mechanism (does anything
produce T7?).

## 3. Arm B — generator-reproduction sweep

- **Generators** (each cross-checked against a live library or the repo's byte-exact reference before the run):
  glibc `srand/rand` (TYPE_3), `drand48` as Perl uses it (`srand48`-style seeding), CPython 2.7 `random.seed(int)`
  → `random()`, bash 4.2 `$RANDOM` (LP64 and ILP32, with its own 15-bit anti-repeat loop), MSVC `rand`, ANSI LCG,
  Park–Miller minstd.
- **Seeds:** all 2³² per generator.
- **Picker:** Z4(m), m = 29…40; two reductions (`x mod m`, and `floor(x·m / range)`); index → rune in gematria
  order (ᚠ = 0); also the Atbash order (28 − x).
- **Alignment:** the generator's first output may align with *any* of the 12,956 positions (covers a reseed at
  any page, section or rune).
- **Recognizer:** the first 5 emitted runes hit a bitset of all LP2 5-grams → extend → **HIT iff ≥ 14 consecutive
  runes match exactly.** Expected false hits over the whole sweep < 10⁻³.
- **Plant:** for each generator, a 400-rune run from a known seed is spliced into LP2 at a random position and a
  10⁶-seed window around it is swept by the same binary; the seed must be reported. Any generator whose plant
  fails is reported as not run.
- **R3 note:** no decode is produced, so there is nothing to persist beyond hits and near-hits (≥ 10 runes),
  which are logged in full.

## 4. Aiming test

1. **What a hit looks like:** ≥ 14 printed runes reproduced exactly by a library generator; the plant shows the
   binary recognises exactly that.
2. **Why the prior is above flat:** the leak fraction 0.192 ± 0.021 is matched without a free parameter by a
   remembered-drop picker at m = 35–37, and by no redraw loop over a uniform key (§0). Weak, but measured.
3. **Bounded:** enumerable — 7 generators × 2³² seeds × 24 picker variants × 2 orders.
4. **Conditionals of a negative:** (i) these generators, 32-bit seeds, fresh state at the aligned position;
   (ii) the Z4 picker with these two reductions and these two rune orders — a different symbol table, a
   differently placed drop set, a shuffled array, or extra generator calls between runes are **not** covered;
   (iii) no register conditional (exact match).
5. **Kill:** a failed plant for a generator kills that generator's row. Wall-clock cap 3 h total; anything
   unfinished is reported as unfinished with the seed range actually covered.

Honest prior on H-B: low (order of 1 %). It is run because it is cheap, finite, has no false-positive path, and
has never been run: every earlier seed sweep used the generator as a *key* under a language scorer.

## Addendum 1 (2026-11-26, written while the first generator was still running; no sweep output read)

- **Plant length.** §3 said 400-rune plants. The binary keeps 40 raw draws per seed, so one seed yields 24–40
  emitted runes, and that is what was planted (24/24 recovered, `plants.json`). The recognizer only ever needs 14,
  so the control tests exactly the path the sweep uses; the "400" was a drafting error.
- **Wall-clock cap.** Timed after registration: the eight generators need about 3.7 h on this 4-core box. The cap
  is raised from 3 h to 4.5 h. Run order is by toolchain prior (Perl drand48, bash 4.2 ×2, glibc, CPython 2.7,
  then MSVC / ANSI / minstd), so if anything is cut it is the lowest-prior tail.
- **Arm A wording.** "Best of {KS, triples, lag-2}" is the maximum of the three powers with no multiplicity
  correction; it can only overstate separability.

## Addendum 2 (2026-11-26, written while the Arm B sweep was on its first generator; no sweep output read)

**Arm B2 — the word-length draw.** While the sweep ran, the transcription's structure marks were read: LP2
carries sections (`$`), paragraphs (`&`) and a numbered list 1–5 (segments 36–38), and Round 45 showed its
word lengths have an English-like multiset with no order. Under H-B that combination means the lengths were
*drawn*, and a program that draws a word length calls the generator at each word start. Arm B assumes one raw
draw per rune, so it would miss exactly the program H-B most plausibly describes. Arm B2 closes that:

- At every printed word start (separators `- . & $ §` and numerals; not line breaks), **e ∈ {1, 2} extra raw
  draws are skipped** before the word's first rune (they do not touch the picker's "last" memory).
- Because the skip pattern depends on position, alignment is restricted to **the 55 page starts** (segment 0's
  start is the stream start).
- Same picker, m = 29…40, both reductions, both rune orders; **HIT iff 14 consecutive runes match exactly.**
- Generators, in order: Perl `drand48`, bash 4.2 (LP64, ILP32), glibc `rand`, CPython 2.7. All 2³² seeds each.
  Runs after Arm B finishes; cap 3 h; an unfinished generator is reported with the seed range covered.
- Plant: a B2 run with known (seed, m, reduction, order, e) is spliced over a page start and recovered by the
  same binary from a 10⁶-seed window; 3 per generator.
- Not covered by B2: e > 2, extra draws elsewhere (punctuation, line breaks), a length draw that feeds the
  picker's memory, generation that did not restart at a page start.
