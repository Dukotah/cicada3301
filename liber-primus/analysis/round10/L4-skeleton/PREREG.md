# PRE-REGISTRATION — Round 10, Lane L4 (SKELETON EXTENSION)

Written **before** any run. Author: L4 armada agent, 2026-08-12.
Folder: `liber-primus/analysis/round10/L4-skeleton/` (write-only scope, no repo file touched).

---

## 0. What is already eliminated (so this lane does not re-derive a known negative)

- `research/DEAD_ENDS.md:394` — **R8-SKELETON KILLED for its 51-text / 8,205,104-word corpus.**
  Best real 19.8% (slack 0) / 49.2% (slack 1) vs a shuffled-LP2 control's own max of 20.0% / 49.1%.
  The kill entry itself says: *"This eliminates a corpus, not 'all known texts'. DO extend it."*
- `ELIMINATION-LEDGER.md:238` (item 2b, Campaign XVIII `word_skeleton.py`) — an earlier,
  weaker version of the same idea over 11 texts, using longest-consecutive-run. **NOTE: that
  script splits words on every non-rune character, i.e. it treats `/` as a word separator, which
  is exactly the parsing bug DEAD_ENDS.md:411 flags (458 of 604 line breaks fall MID-WORD).
  Its numbers are therefore on a shattered 3,316-"word" parse, not the correct 2,928-word one.**
  This lane uses the corrected parse only.
- `ROUND-9-RESULTS.md` Track LENGTH — the word-length *excess* is closed (large-*n* artifact) and
  the greedy-multigraph encoder is **verified against ground truth** (PARABLE, 20/20 word lengths
  exact). This lane inherits that encoder as validated and does **not** re-open the mean-length
  question. It also inherits R9's bound on the interrupter ambiguity: LP2 plaintext mean word
  length ∈ **[4.268, 4.425]** (lower = all 458 ᚠ are nulls, upper = none is).

This lane is therefore **not** a repeat. It is the explicitly-invited extension, plus the two
things Round 8 never did: a **positive control** and a **detection-floor measurement**.

---

## 1. Hypotheses

**H0 (instrument power — must pass before anything else means anything).**
The Round-8 FFT word-length scan, run at the corpus scale intended here, detects a *planted*
known plaintext.

**H0b (detection floor).** There exists a maximum plaintext-corruption rate `p*` above which a
genuinely-present plaintext becomes invisible to the scan. `p*` is the number that converts a
negative into a bound.

**H1 (the actual attack).** LP2's plaintext is a contiguous passage of some text in the
**extended** corpus (all of Round 8's 51 texts **plus** the ~208 keytext files in
`data/keys/{campaign12,campaign13,armada18,armada19,welsh}/` which the Round-8 glob never
reached — it globbed `data/keys/*.txt` top-level only — **plus** newly-fetched esoteric /
hermetic / alchemical / mystical primary sources and Cicada's own published prose).

**H2 (interrupter-robust matching).** Round 8's symmetric `slack ∈ {0,1}` is the wrong tolerance
shape. A null ᚠ can only make a word *longer*, never shorter, and a word may hold 0..k of them.
The correct matcher is the **directional interval**: a corpus word of rune-length `v` matches LP2
word `i` iff `v ∈ [obs_i − fc_i, obs_i]`, where `fc_i` is that word's ᚠ count. This raises
true-alignment recall to ~100% while raising the null baseline only slightly, because 84% of LP2
words contain no ᚠ at all and stay exact-match.

---

## 2. Exact tests

### T0 — POSITIVE CONTROL (run first; gates everything else)
1. Pick a passage of 2,928 words from a corpus text **already in the corpus**.
2. Transliterate it with the repo's validated greedy-multigraph encoder → rune-length sequence.
3. Insert 458 null ᚠ at random word positions (matching LP2's observed count), producing an
   `obs`/`fc` pair with the same statistics as LP2's.
4. Run the identical scan over the whole corpus, with the identical shuffled null.
5. Record: rank of the planted text, match %, z vs null.

### T0b — DETECTION-FLOOR CURVE
Repeat T0 with a fraction `p` of word lengths corrupted (±1 or ±2 at random — this stands in for
edition drift, differing hyphenation/punctuation conventions, an unknown extra null class,
paraphrase, or a different-but-related recension), for
`p ∈ {0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70}`.
Report the largest `p` still detected. Also repeat at window 400 (a single page-group) to give the
floor for a *partial* plaintext match.

### T1 — THE SCAN
Full extended corpus, LP2 window 2,928 words (and 400, 120 for partial-match sensitivity),
matchers: exact (slack 0), symmetric slack 1 (for continuity with Round 8), and the directional
interval matcher.

### NULL CONTROL (mandatory, run identically in every test)
The LP2 length sequence **shuffled** (a permutation preserves the exact length histogram and the
interrupter count, destroying only the order — the sharpest possible null for this statistic),
scanned against the identical corpus. ≥3 independent shuffles per configuration so a per-text
null mean/sd exists, plus the global max-across-texts null Round 8 used.

---

## 3. PASS / FAIL THRESHOLDS — fixed now, numerically

| Test | PASS | FAIL |
|---|---|---|
| **T0** | Planted text ranks **#1**, match ≥ **70%** (interval matcher) or ≥ **60%** (exact), and z vs null ≥ **10** | Anything less → the instrument is blind; extension is pointless and *that* is the finding |
| **T0b** | Report `p*` = largest corruption rate where the planted text still ranks #1 with z ≥ **5** | — (measurement, not pass/fail) |
| **T1** | Real best ≥ **60%** at the 2,928-word window **AND** z ≥ **10** vs the shuffled null **AND** the top hit is a single coherent offset in one text → candidate plaintext identified; then subtract to recover the keystream and confirm on the solved pages | Real best inside the null band (z < 3), or above the null but below the T0b-established detection floor → **NEGATIVE**, and the deliverable is the bound |
| **Break claim** | Only if the recovered keystream/plaintext is readable English **and** reproduces under `tests/validate.py` conventions | — |

A "suggestive" middle band (3 ≤ z < 10) is pre-declared **not a finding**: it will be reported as
a ranked shortlist with its own null, nothing more. Round 8's headline z was 2.07 and was
correctly read as noise (the leaderboard was an ordering by text length — the max-of-many-offsets
effect), so any z in this band must be checked against the *text-length-matched* null before it is
even mentioned.

---

## 4. What a negative will and will not cover

It will cover: **contiguous, verbatim-ish, English-transliterated-to-futhorc plaintext drawn from
the enumerated corpus, at the word-length-sequence level, with directional interrupter tolerance.**

It will **not** cover: a plaintext that is original Cicada prose (never published anywhere), a
translation/recension not in the corpus, a non-contiguous or reordered plaintext, a plaintext in a
language whose transliteration convention differs from the greedy-multigraph encoder, or a
word-boundary convention other than split-on-`-`-and-`.`. The detection-floor number `p*` is what
quantifies "verbatim-ish".
