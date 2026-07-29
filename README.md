# Cicada 3301 — Research Archive & Liber Primus Cryptanalysis

[![CI](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml/badge.svg)](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml)

A documented investigation of the **Cicada 3301** internet mystery — the 2012, 2013 and
2014 puzzles, the techniques behind them, every credible theory about who made them — and
a **validated, pure-Python cryptanalysis rig** aimed at the still-unsolved **Liber Primus**.

The rig's trust anchor is simple: `python tests/validate.py` **reproduces every known
solved page** from the canonical runes. Everything ruled out below was ruled out by code
that first proves it can find the answers we already know.

> ### The honest headline
> **We did not solve the Liber Primus, and we cannot name its creators.** What this
> project produced instead is a **sharpened boundary**: the unsolved pages are
> **one-time-pad-class**, and the evidence now says they are *unsolvable-by-design*
> rather than *unsolved-by-effort*. That is a result, not a consolation — and it is
> backed by ~20 campaigns of falsified attacks, each with a reproduce command.

---

## What the evidence says

**The cipher.** Over the 12,956 unsolved runes, the ciphertext sits at the random floor on
every measure but one:

| Measure | Observed | Random baseline |
|---|---|---|
| IoC·N | **1.000** | 1.000 |
| Shannon entropy | **4.857 bits** | 4.858 max (29 symbols) |
| Adjacent-equal ("doublet") rate | **0.66–0.68%** | 3.45% |

That single ~5× doublet *deficit* is the only real structure in the entire corpus, and the
project pinned what produces it: a **soft rejection-sampling / anti-repeat filter
(≈83% suppression, p_keep≈0.18) over a memoryless base, against an external one-time pad.**
Information-theoretically, no public solver recovers the plaintext without that pad —
for any chosen plaintext, a valid structureless key exists.

**The pad appears unpublished by design.** Pages 0–54 were the terminal deliverable of the
7th hidden service with no accompanying key; the thematic pointers (mayfly/ephemeral; the
koan "seek within") read as *gated, not published*. Nobody should claim LP2 is solvable
with more compute or more AI — the math says otherwise.

**The creator.** Every name-first path is dead — and one of them is dead *provably*:
Cicada's entire corpus of authentic connected prose is **359 words**, far below any
stylometric attribution floor, so authorship is **un-attributable**, not merely unknown.
What replaced the name is a **technique fingerprint**: the anti-repeat hardening is not a
named cryptographic construction — it is a **Smirnov word / Carlitz composition** from
enumerative combinatorics, a *mathematician's* reflex, applied softly enough to suggest a
human calligrapher following a "never write the same rune twice" rule by hand. See
[`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md) for the full profile.

## Start here

| If you want… | Go to |
|---|---|
| **The verdict** on both goals — solve and attribution | [`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md) |
| **Everything tried and why it's dead** — the complete index | [`liber-primus/ELIMINATION-LEDGER.md`](liber-primus/ELIMINATION-LEDGER.md) |
| **To attack LP2 yourself** — verified facts + reproduce commands | [`liber-primus/SOLVERS-DOSSIER.md`](liber-primus/SOLVERS-DOSSIER.md) |
| **The map of all 183 analysis scripts** | [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) |
| **Background on the puzzles themselves** | [`research/00-overview.md`](research/00-overview.md) |
| **Where the work left off** | [`PICKUP-HERE.md`](PICKUP-HERE.md) |

## Quickstart

```bash
git clone https://github.com/Dukotah/cicada3301
cd cicada3301/liber-primus
pip install -e .                   # the `lp` core library (gematria/ciphers/stats/score)

python tests/validate.py           # 1. trust anchor: reproduce every known solved page
python lp_try.py --key DIVINITY    # 2. test your own key hypothesis against all pages
python analysis/run_stats.py       # 3. the statistical profile every theory must explain
```

Scripts resolve their own paths, so they run from any checkout. Large corpora and
downloaded onion dumps are gitignored and re-fetched on demand.

## Repository layout

```
cicada3301/
├── research/            cited deep-research reports — origins, each puzzle, identity, techniques
├── puzzles/             step-by-step reconstructed solution chains (2012, 2013, 2014)
├── ciphers/             technique reference: the ciphers and stego 3301 actually used
├── identity/            theories weighed against evidence + the verification ledger
├── sources/             source list & provenance
└── liber-primus/        the cryptanalysis project
    ├── ELIMINATION-LEDGER.md   everything tried, why it's dead  ← start here
    ├── FINAL-SYNTHESIS.md      the terminal verdict
    ├── SOLVERS-DOSSIER.md      community-facing writeup with reproduce commands
    ├── src/lp/                 core library: gematria, ciphers, scoring, stats
    ├── data/                   transcriptions + provenance-verified page images
    ├── analysis/               183 scripts across 22 campaigns  (see analysis/README.md)
    ├── tests/                  the validation gate (11 tests, CI-enforced)
    ├── docs/                   reference + superseded snapshots
    └── outreach/               community post drafts
```

## What this project can and cannot claim

**Can claim:** every attack we could concretely construct has been built, run and
falsified; the cipher's mechanism is described to a parameter; the transcription is
verified three independent ways (including a **label-free audit** — glyphs clustered by
shape with the canon never shown, and the canon turned out to *be* the natural visual
partition); the source images are byte-identical to the original onion release
(56/56 SHA1); autokey — the community's decade-old leading hypothesis — is **positively
refuted**, not merely "failed to decrypt."

**Cannot claim:** that the space of *all conceivable* external keytexts is exhausted. One
untried already-public keytext remains the single falsifiable avenue, which is exactly why
this repo says "no solve" instead of "unsolvable, full stop."

**Deliberately does not claim:** a name. The identity of Cicada 3301's creators is
unknown and unconfirmed. This repo catalogs and weighs theories — a field heavily polluted
by hoaxes and self-claims — and refuses several that others have accepted.

## Method

Research and cryptanalysis were run as multi-agent campaigns: parallel attack agents per
dimension, an adversarial verification pass on every positive result, then synthesis. The
final pass was an **11-iteration rotating-critic loop** in which a critic in a fresh
perspective (contrarian, naïve outsider, historian, data-provenance red-team,
game-theorist, devil's-advocate believer…) scored each round and directed the next.

The loop **caught and reversed three of its own false positives** — a word-length
"language" signal that was really line-wrap typography, a "surviving English phonotactics"
claim that was 95-rune sample noise, and several claimed hits killed at the verify stage.
Negative results only mean something when the process can turn on itself, so those
self-corrections are recorded rather than quietly dropped.

---

*Status current as of 2026-07-29. What would reopen the case: a new 7A35090F-signed Cicada
release, a CicadaSolvers-accepted reproducible page solve, or the private pad surfacing.*
