# READ THIS BEFORE YOU MODEL THE DOUBLET FILTER — Round 48 / M1 independent pass

_Filed 2026-11-27. One lane, run as a fresh attempt at the owner's request, outside the Round 48 plan of record.
Full tables: [`M1-leak-census/RESULTS.md`](M1-leak-census/RESULTS.md). Pre-registration:
[`M1-leak-census/PREREG.md`](M1-leak-census/PREREG.md)._

> **No solve.** LP2 is still OTP-class. What follows are four statements that later rounds should build on, each
> with the command that reproduces it. **Do not take them on authority — re-run them.** They are cheap: the census
> takes ten minutes, the sweeps a few hours on four cores, and every sweep has a planted control that fails loudly
> if the code is wrong. A result you can re-run is worth more than a result with a confident label on it, and this
> repo has been burned by confident labels twice (doctrine R7).

## The four statements

### 1. "The filter is a coin with probability 0.813" is a curve fit. Stop treating it as the mechanism.

LP2 has 86 doublets where 447 are expected. The pinned model explains that with one fitted probability.
A rule with **no parameter at all** explains it equally well:

> pick a symbol at random out of **m**, never the same as the last pick; only 29 of the m symbols print a rune,
> but the others still count as "the last pick".

That predicts N·(m − 29) / ((m − 1)·29) doublets: **79, 89, 99 for m = 35, 36, 37.** Two further one-parameter
constructions (a strict filter followed by deleting 18.7 % of runes; a strict filter under a second shift layer
that changes every ≈ 5.4 runes) also fit. At LP2's size none of these can be told from the coin or from each
other (best test power 0.06–0.14).

What this changes for you:

- A decoder, null or plant generator that hard-codes "redraw with probability s" covers **one of at least four
  constructions that fit the data equally**. Say so in the conditionals of any negative that depends on it.
- Each alternative is a different object: a 35–37-symbol alphabet with silent symbols; a stream with a fifth of
  its runes missing; a two-layer cipher. The beam negatives in the ledger were not measured against plants made
  any of these three ways. That is an instrument audit nobody has run.

### 2. No ordinary redraw loop over a uniform 29-rune key makes LP2's leak.

Redraw once: ≈ 15 doublets. Redraw until different: 0. No-repeat on raw bytes: ≈ 398. No-repeat on Latin letters:
≈ 115, all on two-letter runes (LP2: 24 of 86). All rejected at the registered 99 % rule. If you want to
write "the author's code did X", X has to be one of the admitted rows in the results table, or something new that
you test the same way.

### 3. Nothing here explains T7.

The doublet-gap autocorrelation (+0.380) is reached by ≤ 0.5 % of replicates of every admitted mechanism.
It is not a by-product of any of them. T7 remains the one measured structure in LP2 with no generative account.

### 4. The unsolved pages are not raw output of eight common library generators.

Hypothesis: there is no plaintext; the pages are a seeded PRNG driving the picker in statement 1. This is the one
reading under which a hit would be certain (14 runes reproduced exactly; no language model, no bar).

- **Arm B:** Perl `drand48`, bash 4.2 `$RANDOM` (64- and 32-bit), glibc `rand`, CPython 2.7 `random`, MSVC `rand`,
  ANSI LCG, minstd; **every 32-bit seed**; m = 29…40; two reductions; two rune orders; every alignment.
  ≈ 8.2 × 10¹¹ streams. **0 hits.** 24/24 plants recovered. Near-misses (60, none longer than 11 runes) match the
  chance count (≈ 55).
- **Arm B2:** the same with 1 or 2 extra generator calls at each printed word start, aligned at the 55 page
  starts, for the first five generators. **0 hits** (all 2³² seeds each). 15/15 plants recovered.

Not covered, and stated so nobody mistakes this for a closure: seeds wider than 32 bits, other generators, a
shuffled symbol table, library wrappers with their own rejection loops (`randint`, `choice`, `shuffle`), extra
calls anywhere other than word starts. The space of "some program generated this" is unbounded; this is a
measured corner of it.

## One corollary that was checked and died

If the silent symbols of statement 1 were the *printed separators* (spaces, points), every doublet would straddle
a word boundary. 23 of 86 do; independence predicts 19. The printed separators are not the silent symbols.
(Post-hoc and descriptive; a one-line count, reproducible from `layout.py`.) This agrees with Round 45: the
filter ran over the rune stream without regard to the printed word breaks.

## What I would do next, in order

1. **Audit the decoder against the three other constructions** (doctrine R1). Plant English under (a) a mod-36
   alphabet whose 7 extra symbols are consumed silently, (b) 19 % rune deletion after a strict filter, (c) a
   strict-filtered layer over a slow second layer; hand `beam_v3` the correct key; read the score. If it scores
   noise, as it did for V-BACK, then the beam negatives are silent on constructions that fit LP2 as well as the
   one they assume. This is finite and takes a day.
2. **Look for the symbol-table size in the artifacts, not in the runes.** Statement 1 turns "what alphabet did the
   author's tool use" into a question with a predicted answer (35–37). The solved pages already show which
   non-rune symbols the author's plaintexts used; count them. If the solved plaintext alphabet (runes + space +
   the punctuation and digits actually used) has 35–37 members, the picker reading gains a real prior. If it has
   31 or 45, it loses one. Nobody has made that count against this prediction.
3. **Do not open another generator sweep** unless an artifact names the generator or seed width. Arm B was run
   because it was finite and had no false-positive path; widening it is the unbounded space the doctrine warns
   about.
4. **T7 needs a second stream of filtered events**, as Round 45 said. Nothing in this lane changes that.

## Honest accounting

- The m = 35–37 fit was seen in an exploratory pass **before** registration (PREREG §0). Its census row is a
  replication, not a blind confirmation.
- Prior on the generator-output hypothesis was about 1 %, stated in advance. Its failure is the expected outcome.
- Two addenda were written after registration (plant length and wall-clock cap; Arm B2). Both are stamped in
  `run.log` and were written before any sweep output was read.
- The census uses 400 replicates and six statistics. "Not separable" means not separable **by those statistics
  at N = 12,956**.
