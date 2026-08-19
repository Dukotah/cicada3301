# Cicada 3301 — Research Archive & Liber Primus Cryptanalysis

[![CI](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml/badge.svg)](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml)

A documented investigation of the **Cicada 3301** internet mystery — the 2012, 2013 and
2014 puzzles, the techniques behind them, every credible theory about who made them — and
a **validated, pure-Python cryptanalysis rig** aimed at the still-unsolved **Liber Primus**.

The rig's trust anchor is simple: `python tests/validate.py` **reproduces every known
solved page** from the canonical runes. Everything ruled out below was ruled out by code
that first proves it can find the answers we already know.

---

## 🤖 Arriving here as an AI model, or a solver with better tools than 2026 had?

**Start with these four files. You do not need to read the prose.**

| | file | what it gives you |
|---|---|---|
| 1 | [`liber-primus/PROBLEM.json`](liber-primus/PROBLEM.json) | The problem stated machine-readably: the alphabet, the ciphertext pinned by SHA-256, the measured statistics, the acceptance criteria, and which regions of the search space are already eliminated. |
| 2 | [`liber-primus/verify_solution.py`](liber-primus/verify_solution.py) | **The oracle.** Think you solved it? Submit a key and get a mechanical verdict against criteria fixed in advance. Run `--selftest` first — it proves the judge accepts a known-good key and rejects a wrong one. |
| 3 | [`liber-primus/LEDGER.json`](liber-primus/LEDGER.json) | Every hypothesis ever tested here, with its threshold, its coverage bound, whether its positive control passed, and what would reopen it. Query it instead of reading forty documents. |
| 4 | [`liber-primus/benchmark/`](liber-primus/benchmark/) | Plant-and-recover gates. **Run these before trusting any null you produce.** |

```bash
python3 liber-primus/tests/validate.py            # 1. the rig reproduces known solves
python3 liber-primus/verify_solution.py --selftest # 2. the judge is itself validated
jq -r '.entries[] | select(.status=="never-run") | .id' liber-primus/LEDGER.json  # 3. what's open
```

**Three things this repo learned the expensive way. They will save you months:**

1. **A null from an unvalidated instrument is not a negative.** Plant a known signal and
   prove your machinery recovers it *first*. Years of work here were run through a decoder
   that could not have succeeded even if the hypothesis had been right.
2. **Use the skip-aware beam decoder, not rigid alignment.** Under the anti-repeat filter,
   rigid decoding scores the **correct** key as noise (−6.835) while the beam recovers it
   (−4.170). This one fact invalidates most published "we ruled that out" claims — including
   several of our own.
3. **A fixed score threshold is invalid at large trial counts.** The null's maximum grows
   like `sd·√(2 ln N)`. A "hit" that merely matches your own sweep's maximum is noise.

The current verdict, stated precisely: LP2 is **OTP-*class***. The ciphertext cannot
distinguish a true external pad (information-theoretically closed) from a keystream **derived
from a short seed** (finite keyspace, brute-forceable). *Do not* say "information-theoretically
unsolvable" without that qualifier — that was our own overreach, and it foreclosed a real,
tractable lane for months.

> ### The honest headline
> **We did not solve the Liber Primus, and we cannot name its creators.** What this
> project produced instead is a **sharpened boundary**: the unsolved pages are
> **OTP-class** — the ciphertext is indistinguishable between a true external pad
> (information-theoretically closed) and a short-seed **derived** keystream (finite
> keyspace, brute-forceable). The derived-key dictionary lane is untested; only running
> it settles which. That is a result, not a consolation — and it is backed by ~20
> campaigns, 12 pre-registered rounds, and a 22-lens multi-lens armada of falsified
> attacks, each with a reproduce command. The armada also *corrected* two of our own
> earlier claims: flat IoC does **not** force a full-length key (a period ≈400 key is
> IoC-invisible), and "one-time pad" is more precisely an **OTP-class**
> ciphertext-indistinguishability set. See
> [`liber-primus/analysis/round10/SYNTHESIS.md`](liber-primus/analysis/round10/SYNTHESIS.md).
>
> **Superseded 2026-08-17 (Round 12, front D3).** This headline previously read
> "*the evidence now says they are unsolvable-by-design rather than unsolved-by-effort*."
> That promoted one member of the indistinguishability class (a true external pad) into a
> property of the whole class. `round10b/B4-otp-steelman/b4_results.json` (G5) shows the
> ciphertext cannot separate an external pad from a SHA-256 counter-mode keystream derived
> from a short seed (`separated: false`, max |z| = 1.60), and a short-seed-derived keystream
> has a finite, enumerable keyspace. Round 10's SYNTHESIS already stated the correction;
> it had not propagated to this line. The reasoning is kept, the claim is narrowed. See
> [`liber-primus/analysis/round12/D3/RESULTS.md`](liber-primus/analysis/round12/D3/RESULTS.md).

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
(≈83% suppression, p_keep≈0.18) over a memoryless base, against a full-length keystream.**

**What that does and does not close.** *If* the keystream is a true external pad, no solver
recovers the plaintext without it — for any chosen plaintext, a valid structureless key
exists. But the ciphertext cannot tell that case apart from a keystream **derived** from a
short seed: B4/G5 ran a 6-statistic battery against a SHA-256 counter-mode derived key under
the same filter and found `separated: false`, max |z| = 1.60. A derived keystream has a
**finite, enumerable keyspace and is brute-forceable**. So the honest statement is
**OTP-class**, and the question of which member is settled only by running the derived-key
dictionary — a lane that is marked `never-run` in
[`round10/RECON-A/REGISTER.md`](liber-primus/analysis/round10/RECON-A/REGISTER.md) as items
B-04/B-05, and is in flight as Round 13.

**The pad appears unpublished by design.** Pages 0–54 were the terminal deliverable of the
7th hidden service with no accompanying key; the thematic pointers (mayfly/ephemeral; the
koan "seek within") read as *gated, not published*.

> **Superseded 2026-08-17 (Round 12, front D3).** This section used to end "*Nobody should
> claim LP2 is solvable with more compute or more AI — the math says otherwise.*" That is
> true only for the external-pad member of the class. Front D3's positive control planted a
> SHA-256 counter-mode keystream from the seed `CICADA3301` under the repo's own pinned
> filter and **recovered it** through the project's own beam decoder (−4.170, 98.9%
> char-recovery, vs −7.349 on a wrong seed) — so "no compute recovers it" is demonstrably
> false over the derived-key lane. The claim is narrowed, not withdrawn.

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
| **The map of all analysis scripts** | [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) |
| **The machine-readable falsification ledger** — every lane, status, control, coverage bound, as JSON | [`liber-primus/LEDGER.json`](liber-primus/LEDGER.json) · [`liber-primus/analysis/handoff/LEDGER-README.md`](liber-primus/analysis/handoff/LEDGER-README.md) |
| **The 2026-08 attack loop** — Rounds 1–8, pre-registered | [`research/LEDGER.md`](research/LEDGER.md) · [`research/DEAD_ENDS.md`](research/DEAD_ENDS.md) |
| **Rounds 9–12** — multi-lens armada, number channel, red-team | [`liber-primus/analysis/round10/SYNTHESIS.md`](liber-primus/analysis/round10/SYNTHESIS.md) · [`liber-primus/analysis/round11/SYNTHESIS.md`](liber-primus/analysis/round11/SYNTHESIS.md) · [`liber-primus/analysis/round12/`](liber-primus/analysis/round12/) |
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
│   ├── 00-overview.md … 06-*.md   the background reports
│   ├── LEDGER.md                  the 2026-08 pre-registered loop, Rounds 1–8
│   └── DEAD_ENDS.md               every closed avenue + the reason it closed
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
    ├── analysis/               210 scripts across 26 folders  (see analysis/README.md)
    ├── tests/                  the validation gate (11 tests, CI-enforced)
    ├── docs/                   reference + superseded snapshots
    └── outreach/               community post drafts
```

**Reading order for a newcomer.** The repo answers three different questions and they live in
different places — start with whichever you actually have:

1. *"What is Cicada 3301?"* → [`research/00-overview.md`](research/00-overview.md), then the
   per-puzzle reports.
2. *"What did this project find?"* → [`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md)
   (the verdict), then [`liber-primus/ELIMINATION-LEDGER.md`](liber-primus/ELIMINATION-LEDGER.md)
   (everything ruled out).
3. *"I want to attack it myself"* → [`liber-primus/SOLVERS-DOSSIER.md`](liber-primus/SOLVERS-DOSSIER.md)
   for verified facts and reproduce commands, then
   [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) for which folder holds
   which attack, and [`PICKUP-HERE.md`](PICKUP-HERE.md) for what is still open.

## What this project can and cannot claim

**Can claim:** every attack we could concretely construct has been built, run and
falsified; the cipher's mechanism is described to a parameter; the transcription is
verified three independent ways (including a **label-free audit** — glyphs clustered by
shape with the canon never shown, and the canon turned out to *be* the natural visual
partition); the source images are byte-identical to the original onion release
(56/56 SHA1); autokey — the community's decade-old leading hypothesis — is **positively
refuted**, not merely "failed to decrypt."

**Cannot claim:** a solve, or a name. What the 2026-08 rounds changed is *why* — the
falsifiable avenue this section used to name ("one untried already-public keytext") is
closed **by exhaustion over ~200 texts, now verified robust to both the skip and the rewrite
construction**. So a new candidate text is a very weak lead on its own. What would still
count is evidence from **outside** the ciphertext — a signed or archival pointer that a
specific text *is* the key.

> **Superseded 2026-08-17 (Round 12, fronts D1 and D3).** This paragraph used to say the
> keytext class was closed "*by mechanism rather than by exhaustion* … independent of *which*
> text it is." Round 10's RECON-B/B-16 showed the mechanism argument is unsound under the
> repo's own pinned construction: a soft anti-repeat **rewrite** of the output sets the
> doublet rate, so the deficit has no discriminating power over key *type*. Round 12's D1 ran
> the decisive test (`round12/D1_redteam/rewrite_gate.py`): under the rewrite mechanism the
> correct running key still decodes to −4.45…−4.70 (95–98% rune match), versus the −5.75…−5.88
> the real ~200-text sweeps produced. **The conclusion survives; the argument for it changes**
> from "by mechanism" to "by exhaustion, verified robust to skip and rewrite."

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

*Status current as of 2026-08-11. What would reopen the case: a new 7A35090F-signed Cicada
release, a CicadaSolvers-accepted reproducible page solve, or the private pad surfacing.*
