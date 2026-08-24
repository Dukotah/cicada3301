# Round 16 — THE PUBLIC PAD — pre-registration

_Written 2026-08-19, **before** any lane was run. Hypotheses, thresholds, controls and kill
rules are fixed here so a negative means something._

## The gap this round attacks

The repo's seed census states the closing argument of the whole search programme, and it is
repeated verbatim in three load-bearing places
(`analysis/round10/L5-seed32/CENSUS.md:87-94`, `handoff/PARKED.md:273-278`,
`ELIMINATION-LEDGER.md:365-368`):

> **No seed at all.** `/dev/urandom`, a hardware RNG, `random.org`, or physical dice produce
> a pad with no compressible key. This is the *modal* behaviour for anyone who sets out to
> build "a one-time pad", and it is the majority of the prior mass. Nothing in the seed sweep
> — finished or unfinished — touches it, **and nothing can.**

That sentence silently merges two different properties:

| | leaves no seed | leaves no public record |
|---|---|---|
| `/dev/urandom`, dice, a hardware RNG | ✔ | ✔ — genuinely closed |
| **`random.org`, NIST's Randomness Beacon, a blockchain, a printed random-number table** | ✔ | ✘ — **published, dated, and byte-exact retrievable today** |

The census names `random.org` *inside* the unreachable category. It does not belong there.
random.org sells and archives pre-generated randomness; NIST's Beacon has emitted a signed
512-bit value every 60 seconds since **2013-09-05** and every one is still served; every
Bitcoin block hash since 2009 is public, ordered and permanent; RAND's *A Million Random
Digits* has been in print since 1955 precisely so that two parties can share randomness
without sharing a seed. Each is a **full-entropy pad with no seed and a public record** — the
one combination this project has never swept, because its taxonomy has only two branches
(short-seed-derived = being swept; private pad = closed) and this is a third.

This is the same failure shape D3 caught twice: a *measured bound* ("no sweep can find a
seed") written up as a *settled conclusion* ("nothing can touch it").

**Second, independent gap — offset coverage.** Every external-pad sweep in this repo walked a
coarse offset ladder; A1 used **eight** offsets per keystream variant. On the 118,818,811-byte
`560.13` pad that is 7e-8 of the offset space. A1's NEGATIVE is sound as a verdict on those
eight offsets and is not a bound on the pad. `lib_padsweep.dense_scan` scores **every**
offset. That alone reopens pads already declared swept.

## Instrument

`lib_padsweep.py` — dense offset scan (vectorised rune-index trigram prefilter over a 24-rune
head window) → beam escalation on survivors, with A1's beam settings (`beam_w=120`,
`max_skip=3`, `head=400`), A1's shuffle null, and A1's `score_norm` scale, so every number
here is directly comparable to `round12/A1/results_560_13.json`.

**Gate (run 2026-08-19, PASS).** 8 keystreams planted at random deep offsets in a 1 MB blob
and enciphered under the 0.83 anti-repeat filter: the beam recovered **8/8 at 100 % of runes**
(−4.212), and the dense prefilter retained the true offset in **5/8** (ranks 0, 0, 2, 0, 0).

> **Measured survival rate = 0.625.** That is this round's honest coverage discount and it is
> stated everywhere a coverage claim is made: a dense scan of B offsets covers ~0.63·B, not B.
> The loss is the anti-repeat filter shifting the key pointer inside the 24-rune prefilter
> window. It is a *power* limit, not a soundness limit — the beam stage recovers 8/8.

## Lanes

| id | pad family | fetching needed |
|---|---|---|
| **P0** | **Re-sweep the pads already on disk, densely.** A1's six CicadaOS blobs incl. the 118 MB `560.13` and the 3,992,970 B authoritative `_560.00` — 8 offsets → all of them | none |
| **P1** | **The blockchain.** Bitcoin block hashes / merkle roots / nonces in height order, 2009–2014 | yes |
| **P2** | **Public randomness services.** NIST Randomness Beacon (2013-09-05 →), random.org archives, ANU QRNG, HotBits | yes |
| **P3** | **Printed tables + Cicada's own published high-entropy bytes.** RAND *A Million Random Digits*; the 3301 PGP signature blobs / key packets / published hash blocks / onion addresses concatenated in publication order | mostly on disk |
| **P4** | **Filter fingerprint** (no pad; a discriminator). Characterise the anti-repeat filter at lags 1–8, runs, per-page rate, and residual-doublet placement, to decide *machine vs hand* and therefore which pad families can exist at all | none |

## HIT bar — pre-registered, A1's, unchanged

A configuration is a **HIT** only if `score_norm >= -5.5` **and** `>= null_max + 0.5`, where
`null_max` is this lane's own shuffle null (n=200) under the same keystream. Any HIT is
escalated to the full 12,956-rune stream and then to three independent refuters before it is
written down as anything. Per `benchmark/null.py`, a fixed threshold is invalid at large trial
counts — every lane reports `threshold_for(n_trials)` alongside its raw best.

## Kill rules

1. A lane whose own control fails reports **INCONCLUSIVE**, never NEGATIVE.
2. A lane reports its **coverage bound** (blobs, bytes, variants, signs, offsets × 0.625), not
   a verdict on the family. "Bitcoin is dead" is not a permitted conclusion; "block hashes
   0–300,000 under 12 keystream builders × 2 signs × all offsets, best −6.9 vs a −5.5 bar" is.
3. No lane may claim a decode is English by reading it. Use the oracle
   (`verify_solution.py`) and the null. This is the failure mode that produced every false
   claim in this puzzle's history.
