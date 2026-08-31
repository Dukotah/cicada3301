# Round 24 — Lane C1-EXT — genuinely LANGUAGE-AWARE non-English adjudication — PREREG

_Frozen 2026-08-30, before any real scoring. Binding: `../../../ARMADA-DOCTRINE.md`,
`../C1-matched-runic/PREREG.md` and `../C1-matched-runic/RESULTS.md` (the parent lane).
No thresholds edited after a result is seen; only dated addenda._

## What this lane is (and is not)

C1 proved (control-validated) that the round16 matched-runic scorer corrects rune
**ORTHOGRAPHY** (digraph expansion + lossy K/Q->C, V->U, Z->S folds), **not LANGUAGE**: it
rescued planted Latin but scored 0.00 on vowel-dropped English. C1's RESULTS lists as
`not_covered` the exact axis this lane opens: **genuinely LANGUAGE-AWARE non-English models
(Hebrew / Norse / Enochian), not merely orthography-corrected English.**

This is an **instrument / closure audit** (doctrine R1 + R6), NOT a new key-space sweep. It
re-adjudicates the SAME strongest-prior B-04 slice C1 used, under a WIDENED language-aware
rune-trigram panel, and asks one decision-relevant question: **was the English-only adjudicator
structurally blind to a non-English plaintext in the strongest slice, or do the negatives hold
across languages?**

It can only REOPEN old negatives, not manufacture a hit. Realistic best case: a tightened
bound ("the English-only sweeps were / were not hiding a non-English survivor in this slice").

## Honest register availability (measured from the repo BEFORE freezing — no external downloads)

The rune folder (`detectors.text_to_runes`) is Latin-alphabet based. A "language-aware
non-English model in the rune space" therefore requires a connected corpus of that language
rendered in LATIN letters (romanization or a natively-Latin-script attestation), NOT the
language's native script. Measured availability:

| register | source in repo | clean Latin-script letter mass | verdict |
|---|---|---:|---|
| **Latin** (calibration) | `analysis/latin/latin_28233.txt` + `latin_218.txt` | >200k | AVAILABLE (from C1) |
| **Greek** (calibration) | romanized via `../C1-matched-runic/greek_corpus.py` | ~15k | AVAILABLE (from C1) |
| **Old English poetic** | genuine OE lines (>=2 of þðæ) in the bilingual `round10b/.../corpora/oe_beowulf.txt` | ~138k letters | AVAILABLE |
| **Enochian (phonetic)** | phonetic Keys in `analysis/foundation/enoch_text.txt` ("Ol sonuf vaoresaji...") | ~9.9k letters | TENTATIVE — control must validate |
| **Old Norse (native)** | all repo Norse files are ENGLISH translations (Poetic/Prose Edda, sagas); native þð mass < 25 chars total | ~0 | **UNAVAILABLE** |
| **Hebrew (romanized)** | Kabbalah texts hold 18k NATIVE-SCRIPT Hebrew (unmappable to runes) but only isolated romanized proper nouns (Sephiroth, Kether...); no connected romanized-Hebrew body (measured: 2 parenthetical transliterations, 20 letters) | ~0 connected | **UNAVAILABLE** |

**Refuse-to-fake rule (task-mandated):** Old Norse and romanized Hebrew are marked UNAVAILABLE
and NOT modelled. Inventing a romanization corpus or scraping external text is forbidden. A
plausible-but-wrong hit is worse than a clean null. Old English poetic is the honest stand-in
for the "Old Norse/Old English poetic" register the task names (the same alliterative Germanic
register the futhorc actually served). Enochian is carried only if its positive control passes.

## The Aiming Test (five answers, required before running)

**Q1 — What would a hit look like, would THIS instrument recognise it?**
A hit = a B-04 decode in the C1 slice, invisible to the English quadgram + orthography-matched
scorer, whose language-aware panel score (best over EN/LA/GR/OE/EN* + any validated Enochian LM)
clears BOTH the seed-3301 order-matched null MAX **and** the family-wise `threshold_for(N)` bar
for the WIDENED panel. The positive control (below) plants each language and confirms its own
language-aware LM recovers it where the English scorer does NOT (per-language power gap). A
register whose LM cannot recover its OWN planted language is UNVALIDATED — no null is claimed
over it.

**Q2 — What measured fact raises this family's prior above flat?**
C1 measured the matched (orthography-corrected) scorer at power 0.00 on the ONE non-English-shaped
register it tested (vowel-dropped English) and Greek/Latin power came from a separate trigram
panel, not the quadgram scorer. The English-anchored adjudicator was never shown to be powered on
a genuinely different LANGUAGE's phonotactics. The B-04 slice is ordered by the R20 seed prior
(rank-1 = 1325734783), an evidence-derived ordering (R4).

**Q3 — Is the space bounded, and by what?**
Enumerable + bounded. Re-adjudicate the IDENTICAL C1 slice (top-40 R20-prior seeds x B-04
generators x {mod29,rej29,hi_nib,bits5} x sign x atbash x 2 seed-forms, offset 0, L=120,
target = real unsolved LP2 head). Same N. The ONLY thing that changes is the adjudicator panel:
C1 used EN/LA/GR; this lane adds **OE** and any **validated Enochian** LM. No widening of depth
or offset (an addendum notes this; the reopen conditions in C1 already cover deeper/other slices).

**Q4 — The three conditionals the negative carries:**
1. **Key space:** identical to C1 (top-40 R20-prior seeds x B-04 gens x reds x sign x atbash x
   2 seed-forms, offset 0). Not covered: seeds/gens/offsets outside the C1 slice.
2. **Decoder transition model:** `beam_decode(max_skip=3)` — one key-skip relation; INHERITS L7-B.
3. **Adjudicator register:** English quadgram + round16 matched-runic + a language-aware
   rune-trigram panel over {EN, LA, GR, OE, and Enochian IF control-validated} + the 4 R3
   agnostic stats. Registers with NO honest repo corpus (native Old Norse, romanized Hebrew) are
   UNAVAILABLE and remain not_covered — this lane does NOT close them.

**Q5 — Kill condition at 10% of budget:**
If a register's positive control does NOT show its language-aware LM recovering its own planted
text above its seed-3301 null where the English scorer fails, that register is UNVALIDATED and
its panel score is DROPPED from the family-wise adjudication (so it cannot inflate the panel-max
bar with an unpowered dimension). If NO non-English register validates, the lane reports
control-failed and does not run the re-adjudication as if it meant something.

## The control (mandatory, before real scoring)

For each register {LATIN, GREEK, OLD_ENGLISH, ENOCHIAN, EN_MODERN (upper), EN_NOVOWEL (L7-A 0.00
case), RAND (floor)}: plant text into rune indices (`text_to_runes`, OE fold for Old English),
encipher under `make_key("sha256_ctr", seed=CICADA3301)` + `encipher_keyskip(supp=0.83)`,
`beam_decode(400,3)` with the CORRECT key. Adjudicate the recovered `plain_idx` under:
- the repo English quadgram scorer (the historic gate), and
- each register's OWN language-aware rune-trigram LM (built leave-in from that register's corpus).

Power = fraction of correct-key replicates whose language-LM score exceeds that register's OWN
seed-3301 order-matched wrong-key null MAX. **Control PASS for a register iff its language-LM
power > the English quadgram power on that register's planted text** (reproducing L7-A's
direction: English underpowered on the non-English language, the language-aware LM powered).

## Null (per register, seed 3301, order-matched)

Per register x length: decode that register's own enciphered ciphertext under uniform-random
WRONG keys through the identical beam; adjudicate with the same LM. Bar = null MAX (family-wise
over N_null). Reported with `threshold_for(N_null)`.

## Family-wise bar (real slice) — MULTIPLE-COMPARISONS / DOUBLE-MAX HAZARD

The repo logged a sieve x panel-max FP-inflation hazard (R21-L5, B-04 GATE-NOTE) and C1 upheld
it. Widening the panel from 3 languages (EN/LA/GR) to up to 5 (+OE +Enochian) INCREASES the
panel-max multiple-comparisons exposure. Mitigations, pre-registered:
1. ONE adjudication per decode per register; the panel score of a decode = MAX over the VALIDATED
   registers only (unvalidated registers dropped — Q5). NO prefilter-max compounded with panel-max.
2. The family-wise bar is `threshold_for(N)` computed on the seed-3301 order-matched null of the
   **panel-max statistic itself** (the null already carries the max-over-registers, so the bar is
   correctly inflated for the widened panel — the null and the observed statistic use the same
   number of registers). This is the ONLY correct way to avoid double-counting the panel max.
3. Report expected-FP-at-bar for the widened panel and confirm it equals the alpha=0.01 design
   (not inflated relative to C1's 3-language panel at the same N).

## Coverage x power (reported together, R2)

- Coverage = the exact re-adjudicated slice size (identical to C1's N).
- Power = measured per-register recovery of the CORRECT key under each language LM vs the English
  scorer (report the full envelope per register, not one number).

## Red-team, pre-registered (R6)

1. **English-translation trap (decisive for honesty):** an English translation of Beowulf / the
   Edda / Enoch is NOT a non-English language model — it is another English LM and would give a
   fake "non-English" dimension that is really English. This lane models OLD ENGLISH only from the
   genuine þðæ-bearing OE lines, and Enochian only from the phonetic Angelic text — never from an
   English translation. Old Norse and Hebrew have no non-translation Latin-script corpus -> both
   UNAVAILABLE.
2. **Unvalidated-dimension inflation:** a register whose control fails is DROPPED before computing
   the panel max and its bar (Q5), so it cannot manufacture a survivor by adding a noisy max term.
3. **Double-max:** see Family-wise bar above. Recompute the FP ceiling for the widened panel;
   confirm it is not inflated vs the alpha design.
4. **Any survivor** is refuted-by-default and, per R21-L1 SEAL, FLAGGED-FOR-ORACLE — never
   auto-certified.

## Pass / fail (frozen)

- Control PASS (per register) iff language-LM power > English quadgram power on that register's
  planted text at L=120. A register failing control is UNVALIDATED and dropped from the panel.
- Real re-adjudication HIT-flagged iff any decode's panel-max score (over validated registers)
  clears its own seed-3301 order-matched null MAX AND the widened-panel family-wise
  `threshold_for(N)`.
- Otherwise NULL per register, reported with coverage x power and the three conditionals.
