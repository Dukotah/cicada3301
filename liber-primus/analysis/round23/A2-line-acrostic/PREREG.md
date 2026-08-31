# PREREG — Round 23 Lane A2: Printed-line-geometry acrostic (roadmap A2)

_Written before any real candidate is scored. Binding: `../../ARMADA-DOCTRINE.md`.
Frozen thresholds; any change after a result is an appended dated addendum, never an edit._

## Hypothesis

A self-embedded message ("seek within / test the knowledge") may hide as a
**first-rune-of-each-PRINTED-LINE acrostic** (and a per-word / first-rune-of-each-word
acrostic) of the already-SOLVED plaintext pages — using the **true page-image line
breaks and word spacing**.

Round 22 lane A ran the self-embedded read but ONLY on the concatenated
transliteration (no line geometry), returning a clean control-validated NULL. A2's
sole new input is the real printed-line/word geometry that R22-A could not build.
This is the single most conventional hiding spot for a self-embedded message and the
last plausible one at this resolution.

## Geometry source (frozen, cited)

`data/scream314_lp.md` — the SAME transcription `tests/validate.py` trusts (loaded via
`src/lp/corpus.py`). Each solved page's runes block preserves:
- the page-image **line breaks** (one text line = one printed line), and
- **word boundaries** (the `•` rune-word separator).

No looser/second transcription (e.g. `data/relikd/*`) is used, so the geometry is
guaranteed consistent with the validated decrypt. The plaintext is produced by
decrypting each rune **in place** with the exact transform `tests/validate.py`
reproduces (simple brute for 01/05/06; vigenere + interrupter beam for 03/14),
keeping per-rune (line, word) bookkeeping. Interrupter (null ᚠ) runes emit nothing
and do not advance the keystream, exactly as `solve.decode`.

Extractor validated P0.3-style: it reproduces page 01's known **10** printed lines
and its line-first read equals `ABETFEDOEF` (first letters of the ten visible English
lines A WARNING / BELIEVE / EXCEPT / TEST / FIND / EXPERIENCE / DO NOT / OR THE /
EITHER / FOR ALL). See `PHASE0-GATE.py`.

## The five Aiming-Test answers (doctrine §1)

**Q1 — What would a hit look like, would this instrument recognise it?**
A hit is one of the acrostic reads spelling readable English (or a readable pointer) at
a rate the same read applied to order-shuffled plaintext of identical length essentially
never reaches. Recognizer = repo's validated quadgram scorer (`src/lp/score.py`,
`score_norm`). Power is proven by PLANTING a known line-first / word-first acrostic in a
control page laid out to the SAME line/word widths and confirming recovery (Phase 0).
Recovery < 1.0 → report "instrument-broken," never a bound.

**Q2 — What measured fact raises this family's prior?**
Two *signed* koans in the solved pages point inward: "FIND YOUR TRUTH… TEST THE
CNOWLEDGE" (page 01) and the KOAN "study/look within" pages (06, 14). A line-first
acrostic is the single most conventional place a self-embedded message hides, and it is
the ONE representation R22-A could not reach (it lacked line geometry). Low-but-nonzero
prior; the lane is cheap and reuses a validated recognizer.

**Q3 — Is the space bounded?**
BOUNDED and ENUMERABLE. The geometry is a fixed finite structure: 5 pages, 54 printed
lines total, ~500 words. The read set below is a small finite enumeration.

**Q4 — Three conditionals the negative carries.**
1. **Reads swept:** the frozen read set below (line-first/last, word-first/last, each
   per-page and concatenated-across-pages in book order, forward and reverse). NOT
   covered: keyword-cued selections, mixed line+word diagonal reads, community-solved
   pages beyond the rig's 5, and non-English registers beyond the secondary stats.
2. **The decoder:** identity on already-decrypted runes; the only representational
   choice is the acrostic read, which IS the swept axis. Geometry itself is the new input.
3. **Adjudicator register:** English quadgram scorer (KJV-weighted). A Latin/Welsh/
   base32 pointer could be missed; language-agnostic secondary stats (below) are
   persisted per candidate so a structured-but-non-English survivor is still flagged.

**Q5 — What single observation kills the lane at 10% budget?**
If the Phase-0 positive controls (planted line-first AND word-first acrostics) are NOT
recovered above the null bar, STOP — the instrument cannot see a hit. Checked first in
`PHASE0-GATE.py`. (Result: PASS, recovery = 1.000 for both families.)

## Read set (the enumerable set — FROZEN)

Applied to the per-rune token structure (line → word → per-rune transliteration token):

1. **line_first** — first rune-token of each printed line.
2. **line_last**  — last rune-token of each printed line.
3. **word_first** — first rune-token of each word.
4. **word_last**  — last rune-token of each word.

Each of (1)–(4) is read in FOUR scopes:
- **per-page** (5 candidates each), and
- **concatenated across all 5 pages in book order** (1 candidate each),
each **forward** and **reversed**.

Total candidates = 4 reads × (5 per-page + 1 concat) × 2 directions = **48**.
Per-page line acrostics of the short pages (8–10 lines) are below the quadgram's
comfortable length; they are scored anyway AND printed verbatim for eye-reading (a 8–10
letter pointer would be caught by eye / by the base32 stat even if the quadgram cannot
resolve it).

## Threshold, FPR, and null (FROZEN, seed 3301)

**Recognizer:** `src/lp/score.py::Quadgram.score_norm` on the read's transliteration.

**Size-matched, structure-preserving null (built before scoring, seed 3301):** for a
candidate read of letter-length L, the null is the distribution of `score_norm` over
`n_shuffles = 1000` order-shuffles of the **solved-page letter pool**, each sliced to
length L (histogram-preserving, order-destroying). This is order-matched to the read
length. A candidate is a **per-cell survivor** iff its `score_norm` exceeds the null's
**empirical FPR = 0.001 upper tail (99.9th percentile)** for its own length cell.

**Family-wise bar (Bonferroni/Gumbel):** because 48 reads are enumerated, a headline
survivor must ALSO clear the **max-of-null over all length cells** (the score the single
best of 48 pure-noise reads would need to beat). Report both.

**Expected-FP accounting (R6 red-team):** at FPR 1e-3 over 48 reads, expected per-cell
false positives = 48 × 1e-3 ≈ **0.048**. Any per-cell survivor is compared against this
ceiling; family survivors are the decision-relevant count.

**Language-agnostic secondary statistics (doctrine R3, persisted per candidate):**
IoC·N, min-distinct-symbols over a 32-window, base32/printable fraction, gzip ratio.

## Coverage × power reported together (doctrine R2)

RESULTS.md states: (a) reads swept = coverage (48); (b) Phase-0 recovery = measured
power (line-first + word-first, target 1.000); (c) what is NOT covered. A null is a
bound conditional on those three, never "closed."

## Seal note (R21 L1)

Any bar-clearing survivor is **FLAGGED-FOR-ORACLE, not auto-certified** — the no-oracle
seal is provably leaky (Round 21 L1). We report survivors for human/oracle adjudication;
we do not declare a solve.
