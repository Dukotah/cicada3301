# PREREG — Round 22 Lane A: Self-embedded read (roadmap X2)

_Written before any candidate is scored. Binding: `../../../ARMADA-DOCTRINE.md`.
Frozen thresholds; any change after a result is an appended dated addendum, never an edit._

## Hypothesis

The hidden message is not in the ciphertext at all. It is a **selection of the
already-solved plaintext** — a substring, an acrostic (first/last rune of each line, page,
or word), or an every-k-th-rune read of the concatenated decrypted solved pages, in book
order. This is "**discover the truth inside yourself / seek within**" and "**test the
knowledge**" read painfully literally: the answers we already have contain the next one.

This is roadmap lens **X2**, never run. It is NOT the Round-11 number channel (N1–N5) nor the
separator/interrupter channels (S1–S2); those worked the *ciphertext / value stream*. Lane A
works the **decrypted English plaintext** as the search space. Confirmed distinct from every
prior lane (red-team check in RESULTS).

## The five Aiming-Test answers (doctrine §1)

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit is a selected sub-sequence of the solved plaintext whose runes spell readable English
(or a readable pointer) at a rate the same selection applied to order-shuffled plaintext of
identical length essentially never reaches. The recognizer is the repo's validated English
quadgram scorer (`src/lp/score.py`, `score_norm`: ~−2.2 = solid English, < −4 = noise). We
prove the recognizer works by **planting a known acrostic** in a control plaintext of equal
length and equal letter distribution and showing it is recovered above the null bar (Phase 0,
below). If the plant is not recovered, the instrument is broken and any null is reported as
"instrument-broken," never as a bound.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Two *signed* koans in the solved pages themselves point inward, not at the ciphertext:
- "FIND YOUR TRUTH... TEST THE CNOWLEDGE" — `SOLVED-PAGES.json` page "A WARNING" (01.jpg),
  rig-reproduced by `tests/validate.py`.
- The KOAN pages instruct the reader to *study/look within* (06.jpg, 14.jpg).
These are evidence in the artifact (file path: `SOLVED-PAGES.json`), not lore. Doctrine R4:
prior from evidence. This is a low-but-nonzero prior; the lane is cheap and returns a novel
artifact even on a null.

**Q3 — Is the space bounded, and by what?**
BOUNDED and ENUMERABLE. The solved-page plaintext is a fixed finite string: the 5 rig-solved
pages of `SOLVED-PAGES.json` = **1796 runes** concatenated in book order. The selection-function
set is enumerable (see "Selection functions" below): O(hundreds) of acrostic reads + every-k
reads for k∈[2,40] × offset∈[0,k−1] ≈ a few thousand candidate strings total. Fully enumerable
in seconds. Coverage over *this* solved set will be ~100% of the enumerated function class.

**Q4 — What are the three conditionals the negative will carry?**
1. **Selection space swept:** the enumerated function set below (acrostics + every-k, k≤40).
   NOT covered: keyword-cued selections, book-structure reads we cannot reconstruct (true
   physical line breaks per page — we only have concatenated transliteration), and community-
   solved pages beyond the 5 the rig reproduces.
2. **The "decoder":** here the transform is trivial (identity on already-decrypted runes) — so
   the usual decoder-transition conditional collapses; the only representational choice is the
   selection function itself, which IS the swept axis.
3. **The adjudicator's register:** the English quadgram scorer (KJV-weighted). A selection that
   spells Latin/Welsh/a base32 onion string could be missed. We add a language-agnostic
   secondary statistic (see below) so a structured-but-non-English survivor is still flagged.

**Q5 — What single observation kills the lane at 10% budget?**
If the Phase-0 positive control (planted acrostic in equal-length control) is NOT recovered
above the null bar, STOP — the instrument cannot see a hit, so a null is meaningless. That is
the kill gate, checked first (`PHASE0-GATE.py`).

## Selection functions (the enumerable set — frozen)

Applied to the concatenated solved-page **rune** stream (book order), and, for the line/page
acrostics, to the per-page rune streams. "Rune" = one Gematria-Primus symbol; the transliteration
expands 7 runes to 2 letters, so selection is done on the **rune index sequence**, then mapped
to transliteration for scoring (doctrine mechanics R5: score on rune indices, not the string).

1. **Every-k-th rune**, k ∈ [2, 40], offset o ∈ [0, k−1]: take runes at positions o, o+k, o+2k…
2. **Acrostic — first rune of each word**; **last rune of each word** (word boundaries from the
   transliteration are unavailable in the concat stream, so we also read: first rune after every
   fixed run-length as a proxy — covered by every-k). Word-level acrostic uses SOLVED-PAGES word
   spacing where reconstructable; if not reconstructable it is recorded as NOT-COVERED.
3. **Acrostic — first rune of each page**; **last rune of each page** (5 pages → 5-rune strings;
   scored but too short for quadgram — flagged, read by eye).
4. **Diagonal / skip reads:** fold the concatenated stream into a rectangle of width w for
   w ∈ [2, 60] and read column c (c ∈ [0, w−1]) top-to-bottom, and read the main diagonal for
   each w. (Columns of width w = every-w with offset c, so subsumed by (1); diagonals are new.)
5. **Reverse** of every (1)–(4) selection (book read backwards).

Every candidate string is recorded with its selection descriptor, length, English `score_norm`,
and the language-agnostic stats below.

## Threshold, FPR, and null (frozen)

**Recognizer:** `src/lp/score.py::Quadgram.score_norm` on the selected transliteration.

**Size-matched null (built before the run, seed 3301):** for each candidate of length L runes,
the null is the distribution of `score_norm` over the **same selection function applied to
order-shuffled copies of the source plaintext** — 1000 shuffles per (selection, L) cell, seed
3301, histogram-preserving (destroys order, preserves rune/letter distribution). This controls
for "English letters leak through any selection of English text." A candidate is a **survivor**
iff its `score_norm` exceeds the null's **empirical FPR = 0.001 upper tail (99.9th percentile)**
for its own (selection, L) cell, i.e. a per-cell family-wise-honest bar. Because we enumerate
~a few thousand selections, we additionally apply a **Bonferroni/Gumbel family bar** across the
whole sweep: report the max observed score against the max-of-N null (doctrine null.py logic)
and require any headline survivor to clear the family bar too.

**Language-agnostic secondary statistics (doctrine R3, persisted per candidate at run time):**
- IoC·N of the selected rune indices,
- minimum distinct symbols over a 32-rune window,
- printable-ASCII / base32 fraction (to catch a sparse pointer the English scorer would miss),
- gzip compressibility ratio of the selected string.

## Positive control (Phase 0, run FIRST, gates everything)

Build a control plaintext of the **same length (1796 runes)** and same rune histogram as the
solved concat, but with a **known English acrostic planted** at every-k for a chosen k (e.g.
plant "THEKEYISTHREETHREEZEROONE..." as every-7th rune) inside otherwise-shuffled runes.
Run the FULL sweep on the control. PASS iff the planted every-k selection is recovered as a
survivor (its score clears its cell's null bar and it ranks at/near the top of the sweep).
Recovery fraction is reported as the instrument's measured power. If < 1.0, report the measured
power and treat the null accordingly (doctrine mechanics R2).

## Coverage × power reported together (doctrine R2)

RESULTS.md states: (a) number of selection functions swept = **coverage**; (b) Phase-0 recovery
= **measured power** of the recognizer on a planted hit of this shape; (c) what is NOT covered
(word-boundary acrostics if unreconstructable, physical line breaks, community-solved pages
beyond the rig's 5, non-English registers beyond the secondary stats). A null is reported as a
bound conditional on those three, never as "closed."

## Seal note (R21 L1)

Any bar-clearing survivor is **FLAGGED-FOR-ORACLE, not auto-certified** — the no-oracle seal is
provably leaky (Round 21 L1). We report survivors for human/oracle adjudication; we do not
declare a solve.
