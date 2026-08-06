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
**Round 11 (2026-08-06) — DQT-matrix disambiguation → SURVIVES (benign); resolves R8-S2.** Ran the
pre-specified resolving measurement for the R8-S2 INCONCLUSIVE. The two JPEG quantization-table groups have
*identical* luma tables (Annex-K Q=92) — the split is a **grayscale-vs-color encode difference** (23 pages
1-component grayscale, 33 pages 3-component color). A direct ink-coverage complexity proxy is indistinguishable
between groups (p=0.338), so it's **not content-driven** → SURVIVES in the strict "null-rejected" sense: a real,
positional, benign production-pipeline signal with **zero ciphertext bearing** (it's image-container metadata,
downstream of all glyph content). Framing that kills any over-read: *some pages were saved grayscale, others
color, at the same quality — a per-page encoder setting, not cipher.* Write-up: `LEDGER.md` Round 11.

**Round 10 (2026-08-06) — CORRECTED stylometric exclusion → NEGATIVE; stylometry lane CLOSED.** Re-ran R9
with the fix Gate #2 mandated: an honest **true-exclusion-power** gate (does the rule reject genuinely-different
authors?) instead of the tautological same-author rate. Result is a decisive, well-powered NEGATIVE — at LP's
solved-prose size (N_q≈424–729) true-exclusion power is only **0.20–0.27** (CI far below the 0.80 bar) and no
threshold jointly controls false-exclusion and impostor-rejection, so LP exclusions are uninterpretable. The LP
comparison never ran; no attribution exists; "Cyphernomicon nearest/lowest-FIR" is a pool artifact. This closes
the stylometry lane in **both** halves (positive attribution + negative-space exclusion) until the solved corpus
exceeds ~2,000 words. Write-up: `LEDGER.md` Round 10; `experiments/r10-01-*/`.

**Round 9 (2026-08-06) — Burrows'-Delta stylometric EXCLUSION (EXPLORATORY) → INVALID.** Owner-directed test
of the one small-N stylometry use flagged as defensible. Gate #1 surfaced an already-executed stylometry
campaign the R8 Archivist missed (`liber-primus/analysis/stylometry/`, 2026-07-13: 76% closed-set power but
**62% impostor false-inclusion** at 359w). R9 ran on de-contaminated LP prose; both pre-registered controls
"passed" and the exclusion step produced a tempting "Cyphernomicon nearest" pattern — **but Gate #2 ruled
INVALID**: the operative gate (false-exclusion rate) measured a *near-tautological* quantity and never tested
true-exclusion power, so the exclusion table is voided. "Timothy May nearest" is a pool-composition artifact,
**not attribution**. A corrected test (impostor false-inclusion control) is owed and predicted NEGATIVE. Full
write-up: `LEDGER.md` Round 9; `experiments/r9-01-*/GATE2-VERDICT.md`.

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
