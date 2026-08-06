# research/ — Liber Primus rigor-rail loop (front door)

Rewritten every round. If you read nothing else, read this page and `LEDGER.md`.

## What this is
A **pre-registered, adversarially-gated** attack loop on the unsolved Cicada 3301 **Liber Primus (LP2)**.
Every round: state summary → parallel researchers → **Critic Gate #1** (approve ≤2, default KILL) →
execute *exactly* as pre-registered → **Critic Gate #2** (NEGATIVE / INCONCLUSIVE / SURVIVES / INVALID).
The point is **trustworthy negatives**: a recorded dead end is permanent progress. Most rounds end
NEGATIVE by design — that is the loop working, not failing.

## Two lineages (reconciled as of Round 8)
1. **Canonical archive** — `origin/master`. The deep body of work (`liber-primus/ELIMINATION-LEDGER.md`,
   `liber-primus/FINAL-SYNTHESIS.md`, ~183 analysis scripts, the "Loop iter 1–11" campaigns). A validated
   rig: `liber-primus/tests/validate.py` reproduces **every known solved page** from the raw runes.
2. **This rigor-rail loop** — `research/LEDGER.md` + `DEAD_ENDS.md` + `experiments/`, the pre-registered
   gated rounds (1–8). Round 8 rebased onto `origin/master` so the two are no longer divergent.

Both lineages **independently reached the same terminal verdict.** That convergence is corroboration.

## Current state of play (one screen)
- **ESTABLISHED (measured, reproducible):** over the 12,956 unsolved runes, IoC·N = **1.000**, Shannon
  entropy **4.857/4.858 bits**, adjacent-doublet rate **0.66–0.68%** vs 3.45% random (**z ≈ −16.9**). The
  doublet *deficit* is the only structure, and it is intrinsic (ᚠ-interrupter-independent). Construction
  pinned: a **soft anti-repeat / rejection-sampling filter** (p_keep ≈ 0.18) over a memoryless base against
  an **external one-time pad**. Autokey is **positively refuted** (difference-diagonal z = −17.25).
- **VERDICT:** unsolved LP2 is **OTP-class → unsolvable-by-design from ciphertext alone**, not
  unsolved-by-effort. For any chosen plaintext a valid structureless key exists. The pad appears
  **withheld by design** (onion7 shipped pages 0–54 with no key). This is a *result*, backed by reproduce
  commands — not a concession.
- **ASSUMED (inferred, not proven):** that a plaintext exists at all — **message-existence is undecidable**
  from the runes (LP2 sits in both English-under-pad and filler-under-pad statistical bands).
- **ATTRIBUTION:** un-attributable — the entire authentic connected-prose corpus is ~359 words, far below
  any stylometric floor. No named individual is supportable.

## What is ELIMINATED (open the ledgers for the full list)
All periodic/running/number-theoretic keys; autokey (both, positively refuted); fractionation
(bifid/trifid/Polybius); substitution/homophonic; transposition; Hill; polygraphic/Playfair; two-track
interleave; structured-doublet-placement; collision-skip DP decode; **stego (all channels, 56/56 clean)**;
**image provenance** (SHA1-matched to the archived onion7 dump; stock Ghostscript/Artifex sRGB render);
hash-preimage families (2,658 combos); external cribs/onion/hashes. See `DEAD_ENDS.md` (this loop) and
`liber-primus/ELIMINATION-LEDGER.md` (canonical, complete).

## Latest round
**Round 8 (2026-08-06) — security/forensics lane.** Reconciled onto `origin/master`. Gate #1 killed all
cipher/structure proposals (re-skins of executed work) and the cryptanalyst's own honest null; forwarded
two genuinely-novel **forensic** tests. **S1** (first structured parse of the embedded ICC profile) →
**NEGATIVE**: it's the stock Artifex sRGB profile — confirms the Ghostscript renderer, no new dating/operator
data. **S2** (JPEG DQT quantization-table page-membership) → **INCONCLUSIVE**: the table assignment is
strongly non-random w.r.t. page order (z = −4.77, p ≈ 0) but batch-vs-content is unresolved (weak confound
proxy; blocky-alternating not two-batch) — **zero ciphertext bearing**. Full write-up: `LEDGER.md` Round 8.

## Reproduce anything
- Trust anchor: `cd liber-primus && pip install -e . && python tests/validate.py` (reproduces all solved
  pages).
- Round-8 forensics: `python research/experiments/r8-01-icc-interior-parse/parse_icc.py` and
  `python research/experiments/r8-02-dqt-page-membership/dqt_runs.py` (deterministic; S2 seeded 3301).
- Every number in `LEDGER.md` traces to a file under `research/experiments/` or `liber-primus/analysis/`.

## Files
| File | What |
|---|---|
| `LEDGER.md` | append-only, one entry per round: hypotheses, verdicts, cumulative counts, lesson |
| `DEAD_ENDS.md` | every killed hypothesis + why + round — **check before proposing anything** |
| `OPEN_QUESTIONS.md` | priority-ordered; owed **holdout** pinned at top (AN END / p56, blind anchor) |
| `experiments/NNN-slug/` | pre-registration + deterministic code + raw `results.json` per test |

## How to contribute
Propose a hypothesis with a **falsifiable prediction + named statistic + explicit null (order-matched
surrogates, not English prose) + fixed threshold**, all before code. It must (1) not already be in either
kill-log, (2) respect the doublet deficit (z ≈ −16.9 kills natural-language running keys) and the autokey
refutation, and (3) first reproduce a **known solved page** by its own mechanism — else it's a keyspace
search. "It decrypted to something meaningful" is worth zero.
