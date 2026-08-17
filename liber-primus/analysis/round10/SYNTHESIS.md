# Round 9/10 — multi-lens armada synthesis

_Run 2026-08-11 → 17. Recovered and synthesized 2026-08-17 after the running window
crashed mid-armada (the work was never committed; preserved in commit `5afc9a2`)._

This round is a fresh, wide multi-lens attack, distinct from the `research/round-1…8`
pre-registered sequence. It re-attacks LP2 (unsolved segments 0–54) across three fronts:
the plaintext/word channel (Round 9 + L1–L4), the keystream/pad channel (L5, L9, B-lanes),
and the external/provenance channel (L6–L8, PA, RECON). Every lens was pre-registered with a
hypothesis, a pass/fail threshold, a positive control, and a size-matched null before the run.

## Bottom line

**No solve, no name. The standing verdict holds and is hardened, not overturned:** LP2 0–54
is OTP-class — a full-length keystream filtered by a soft anti-repeat rule against an external
pad that appears unpublished by design. Across ~22 lenses there were **zero genuine hits**. The
round's real value is not another null; it is three things: (1) two load-bearing claims in the
prior verdict were **corrected** and are now stated more precisely; (2) the doublet-deficit
argument was stress-tested from both sides and its exact discriminating power pinned; (3) the
transcription was audited a fourth, genuinely-independent way. Details below.

## Verdict table

| Lens | Hypothesis | Verdict | Status |
|---|---|---|---|
| **R9-LENGTH** | LP2's long mean word-length is a real anomaly | **NEGATIVE** — large-n comparison artifact; LP2 normal for aphoristic English | complete |
| **R9-DIRECTION** | "their numbers are the direction" = a positional read rule | **NEGATIVE** — 2,670 readings, real z=−0.40 vs its own shuffles (worse than noise) | complete |
| **R9-TEMPLATE** | Independent image re-transcription audits canon | **NEGATIVE (no reopener)** — 96.93% agreement on count-exact lines, clean 29→29 bijection; all 103 disagreements are DP edge artifacts / high-cost misreads on *solved* pages / OTP read-failures. Canon faithful. Bounded: only 38.4% of lines glyph-diffable | complete (bounded) |
| **L1-template** | Pixel-DP reproduces canon; doublet deficit is real | **INCONCLUSIVE** — self-control gate 99.41% vs 99.5% bar (missed by 0.09pp); the mapping-free doublet falsifier itself would PASS (0.70% img == 0.70% canon vs 3.48% null) | complete |
| **L2-map** | "its words are the map" — 9 word-channel readings | **NEGATIVE** — all 9 nulled (acrostic tripped detector but failed threshold) | complete |
| **L3-road** | "their meaning is the road" — gematria-sum readings | **NEGATIVE** — all T1–T5 nulled; validation gate passed (oracle z=79.7) | complete |
| **L4-skeleton** | LP2 plaintext is a contiguous passage in an extended corpus | **NEGATIVE** — 224 texts / 22.6M words; real best 22.7% match at z=−1.03 (inside null band), vs ≥60%/z≥10 bar; instrument validated (planted passage 100%, z≫10) | complete |
| **L5-seed32** | Pad is a PRNG at some 32-bit seed | **NEGATIVE / PARKED** — 0 hits on covered space; pre-reg threshold proven statistically invalid at full-32 scale, so completing is a "completeness ritual" | deliberately parked |
| **L6-archives** | Unpulled community corpora hold key claims / novel runes | **NULL** — key-claim falsifier 0/109,917 (the 2 "insider" hits are the *public* Gematria Primus, not private keys); 0 novel LP runes; decoy control 9/9 rejected; Software Heritage dead-to-bots | complete |
| **L7-sota** | 2026-08-12→17 external work changes the verdict | **NEGATIVE** — 25 web ops, all in pre-registered null class; last verified 3301 msg still 2017-04-04 | complete |
| **L8-pad-provenance** | A sourced primary statement about the pad exists | **NEGATIVE (court-records class)** — 0 of {liber primus, key, pad, gematria, 7A35090F} in ~264k chars of Schoenberger filings; clears neither PRIMARY STANDING nor ON-TOPIC. Class-level clean negative; other 5 source classes remain open residue | complete (bounded) |
| **L9-randomness** | Pad is a finite-state generator (LFSR/LCG) / reused | **NEGATIVE** — linear complexity = n/2 exactly, inside anti-repeat control range; `"HIT": false` | complete |
| **B1-artifact-keys** | An artifact string keys LP2 under the hand toolkit | **NEGATIVE** + by-product: doublet rate refutes any hand-toolkit key vs the author's *own* output (z=−14.4) | complete |
| **B2-hand-cipher** | Short-key Vigenère (k=4–12) + hand no-repeat drift | **NEGATIVE (S1-FAIL)** — every config matching doublet+IoC violates κ-flatness; survives only k≥64, outside scope | complete |
| **B3-semantic-keys** | Page-local semantic keys, orthography-expanded | **NEGATIVE** — 0 hits across 168k crib readouts; gates recovered DIVINITY/FIRFUMFERENFE from scratch | complete |
| **B4-otp-steelman** | Prosecute the OTP verdict itself | **OTP SURVIVES, narrowly** — see "Corrections" below | complete |
| **B5-composed-keys** | Composed key W⊕G with start-offset | **NEGATIVE** — 6 pre-reg pages all in noise band (margin +0.064 vs +0.50 bar) | complete (6/55 pages) |
| **B6-non-english** | Plaintext is non-English / machine data, missed by EN scorer | **NEGATIVE** — agnostic detectors real z=+1.35 vs +3.0 bar; v2-onion base32 body is provably undetectable in principle | complete |
| **PA-1** | Is "OTP" community consensus or ours? | **COMPLETE** — it is the repo's OWN verdict: 0/3 primary community sources claim OTP, 2/3 claim solvable | complete |
| **PA-2** | Are the nav docs + instruments sound? | **TRUSTWORTHY w/ caveats** — see "Instrument caveats" | complete |
| **PA-3** | Every Cicada artifact tested? | **GAP FOUND** — author's own ~4MB binary pads (2013 CicadaOS `560.*`) never fed under the skip-aware decoder | complete |
| **RECON-A** | Repo markdown hides un-run leads | **SURVIVES** — 30 leads registered w/ file:line + status | complete |
| **RECON-B** | Nav docs restate narrow negatives as broad closures | **SURVIVES** — 23 leads + 7 scope-drift findings; B-16 is load-bearing (below) | complete |
| **RECON-C** | External sources never ingested | **SCAFFOLD** — PREREG + resumable fetcher written, deliberately deferred (not a crash) | intentional defer |

## Corrections to the prior verdict (the real payoff)

Two load-bearing claims that this repo had been repeating were tested directly and **corrected**.
Per CLAUDE.md these are marked as superseding, not deleted:

1. **"Flat IoC forces a full-length key" — REFUTED (B4/G2).** The smallest key period that IoC
   at N=12,956 cannot reliably distinguish from the real stream is **p\* ≈ 400**, not 12,956. A
   period-400 key would be IoC-invisible. The OTP conclusion therefore does *not* rest on IoC
   alone — it rests on the doublet argument (below), which is what actually carries it.

2. **"OTP" is really "OTP-class, ciphertext-indistinguishable from two named rivals" (B4/G4–G5).**
   Two structurally distinct models pass the full 6-statistic battery inside the external-pad
   model's 95% band, with no statistic separating them at |z|>2.93 (Bonferroni): (B) a SHA-256
   counter-mode *derived* key + anti-repeat filter, and (E) ciphertext-autokey over flat
   non-English plaintext. "External one-time pad" should be stated as one member of this
   indistinguishability class, not the unique explanation.

## The doublet-deficit argument, stress-tested from both sides

The deficit (0.664% adjacent-equal vs ~3.4% English) is the load-bearing statistic. This round
hit it from opposite directions and the tension must be stated honestly:

- **B4/G3 (hardens it):** the minimum plaintext-independent doublet floor across five large
  English corpora is **1.50%** (KJV). Observed 0.664% is *below* that floor → the entire
  plaintext-independent-key class (external pads, PRNGs, keytexts, derived keys) is refuted by
  doublets alone, *when the key is added rigidly*.
- **B1/H3 (independent confirmation):** measured against the author's *own* solved-page output
  (2.74% doublets), the deficit gives z=−14.4 — no hand-toolkit key survives.
- **RECON-B/B-16 (the counter-argument, must be logged):** the repo's own pinned construction is
  a *soft anti-repeat rewrite* at p_keep≈0.18 applied *after* encipherment, which itself erases
  injected doublets — so on that model the deficit has *no* discriminating power over key type,
  because the filter, not the key, sets the doublet rate.

**Reconciliation:** these are not contradictory once the order of operations is fixed. The G3
floor argument kills *rigid additive* keys (no post-filter). The B-16 objection is exactly why
the repo *also* runs the skip-aware / anti-repeat-aware beam decoder (Campaign XVIII, and every
B-lane here) — under which the doublet deficit is *not* used as the discriminator; the English/
structure score is. Both lanes came back null. So the honest statement is: **the doublet deficit
excludes rigid plaintext-independent keys; the anti-repeat-aware decoders exclude the rest to the
limit of their (audited) power — and B4 shows that limit is a genuine indistinguishability class,
not a point identification.** RECON-B/B-16 is a valid sharpening of *how* we may cite the deficit,
not a reopening.

## Instrument caveats surfaced this round (PA-2)

Honest audit findings to carry forward — none overturns a result, all bound how strongly it may
be cited:
- Round 9 DIRECTION had **no positive control** (real scored worse than its own shuffles, so the
  null still bounds it, but the instrument was never shown able to detect a planted signal).
- Campaign XVIII's false-positive ceiling was computed from ~400 wrong-key trials but the sweeps
  ran 1e7–1e9 trials → the stated confirm-margin (~1.3) is optimistic; realistic margin ~0.25.
  **Any new lane scoring near the confirm threshold must recompute its FP ceiling at its own N.**
- Three prior scope-promotions (ARMADA-20; "ciphertext-only complete" over-generalized;
  Campaign V classifier circularity) are re-flagged.

## Genuinely-open residue after this round

Everything below is external or low-prior; none is a live internal cryptanalysis lane.
- **PA-3 Tier-1 input:** the author's own ~4MB binary pads from the 2013 CicadaOS (`DATA/_560.*`,
  `761.mp3`⊕`twitter.txt`) — period-correct key material she demonstrably used, **never fed under
  the skip-aware decoder**. Not held in-repo; would need fetching. Highest-prior untested input.
- **RECON-C:** the resumable community-archive fetch (cijhho insider tree, Reddit) — deliberately
  deferred, cheap to run.
- The 2016 hint's other two clauses ("words are the map", "meaning is the road") are covered by
  L2/L3 and came back null; the clauses themselves remain the only signed methodological hint.

## What this round did NOT do / do-not-repeat

- L5-seed32 full-32 completion — statistically undecidable at the pre-reg threshold; parked on
  purpose. Do not "finish" it without a scale-corrected threshold from `nullcurve.py`.
- Any rigid additive keytext/pad test — foreclosed by mechanism (doublets), independent of text.
