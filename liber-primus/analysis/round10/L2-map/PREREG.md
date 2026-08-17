# PREREG — Round 10, Lane L2-MAP: "Its words are the map"

Written **before** any test was executed. Nothing below was adjusted after seeing a result.
Date: 2026-08-12.

## Licence for the lane

The 2016-01-01 OpenPGP-7A35090F-signed message (`analysis/armada_osint/artifacts/raw/2016.md`):

> Liber Primus is the way. Its words are the map, their meaning is the road,
> and their numbers are the direction.

Round 9 Track DIRECTION attacked clause 3 as **rune-level** positional walks/sieves
(2,670 readings, NEGATIVE, family closed) and recorded that clauses 1 and 2 remain
uninterpreted. This lane takes clause 1.

## Interpretive premise (stated up front, testable in its own right)

Grammatically the sentence has ONE subject noun — **words** — carried through all three
clauses ("its **words** … **their** meaning … **their** numbers"). So the unit of the
instruction is the WORD, not the rune. Round 9's instrument stepped by `f(c[p])` per
**rune**; every reading below is therefore at a different granularity and is not covered
by the Round-9 kill.

Prediction that follows and is checked first (P0): the phrase is not original to 2016 —
LP1's own **A WARNING** page reads "…EITHER THE WORDS OR THEIR NUMBERS, FOR ALL IS
SACRED". If the 2016 line is a quotation of the book's own vocabulary, that is evidence
it is **devotional restatement, not instruction** — the null interpretation this lane
must be willing to return.

## Parse convention (fixed here, not negotiable later)

Per the Round-8 parsing-bug entry in DEAD_ENDS.md:407-417 — `/` is a **line wrap, not a
word separator** (458 of 604 line breaks fall mid-word). Words are split on `-` and `.`
and on the page marker `%` only. Expected: **2,928 words / 12,956 runes / 57 segments**;
any parse not reproducing those three numbers aborts the lane.

## Scoring instruments and their scales (know which one, per the round rules)

| instrument | file | English | random |
|---|---|---|---|
| rune 4-gram, long stream | `analysis/seed_sweep/ngram.bin` | −11 … −12 | ≈ −16 |
| English quadgram `score_norm` | `src/lp/score.py` | −4.2 … −5.0 | ≈ −7.3 |

## Readings and their pre-registered thresholds

Every reading gets a null control. Two null families are used:
- **NULL-A**: 8 independent shuffles of the 12,956-rune ciphertext with the **word-boundary
  positions held fixed** (isolates rune content from layout);
- **NULL-B**: the identical reading applied to a control text (English rendered into
  futhorc, and/or the shuffled word-length sequence), where the reading consumes layout.

`z` below always means (real − null mean) / null sd over the null family, computed on the
same statistic.

### G0 — parse gate
PASS to continue = parse yields exactly 2,928 words, 12,956 runes, 57 segments. Otherwise abort.

### G1 — word-boundary FORCING detector (global gate for the whole acrostic family)
Any "map" that is read off word/line/page-initial or -final runes must have been **forced**
into the ciphertext, which dents the uniformity of exactly those positions. Test: χ² of the
word-initial, word-final, line-initial, line-final and page-initial rune distributions
against (a) uniform and (b) the pooled ciphertext unigram distribution.
- **HIT** = any of the 5 positions gives p < 0.001/10 (Bonferroni over 10 tests) **and** the
  same statistic on NULL-A does not (i.e. it is not an artifact of the boundary layout).
- **NULL** = no position deviates → the whole first-of-X acrostic family is closed by a
  detector, not merely by 4 failed reads.

### M1 — word-initial / word-final acrostic streams, read as text
Already partially eliminated (Campaign XVII `analysis/red_team.py:99-127` tried
first/last-of-word as plaintext and as a 40-rune Vigenère key). Extension: read each
stream under all 29 additive shifts × {identity, atbash} × {forward, reversed}, and
also per-segment rather than pooled.
- **HIT** = best rune-4-gram ≥ **−13.5** AND z ≥ **+5** vs NULL-A.
- Otherwise NULL.

### M2 — word NUMBERS (the gematria reading)
For each word: S_prime = Σ gematria primes, S_idx = Σ rune indices. Reduce to a symbol
stream: S mod 29 → rune; S mod 26 → letter; also word-length mod 26. Both with and
without the ᚠ interrupter stripped.
- **HIT (rune)** = 4-gram ≥ −13.5 and z ≥ +5 vs NULL-A.
- **HIT (letter)** = `score_norm` ≥ **−6.0** and z ≥ +5 vs NULL-A.

### M3 — word boundaries as a BIT stream ("the map is the layout")
Bit per word from a length predicate (len even; len > median; len ≥ 5; len prime), both
polarities, packed 5-bit (Baconian → letters) and 8-bit (ASCII), both bit orders, with
every start offset 0–7.
- **HIT (ASCII)** = ≥ 90% printable AND `score_norm` ≥ −6.0.
- **HIT (Baconian)** = `score_norm` ≥ −6.0 and z ≥ +5 vs NULL-B (shuffled word-length seq).

### M4 — LIBER PRIMUS AS ITS OWN BOOK — "its words are the map" read literally
The map is a lookup table and the book supplies it: numbers derived from each LP2 word
index into the **solved LP English word list** (LP1 + AN END + PARABLE, ~750 words).
Pointer families: word length; S_prime mod W; S_idx mod W; cumulative S mod W; (word
index + S) mod W; and the same restricted to one page at a time. Output = the retrieved
English word sequence.
- Distinct from R8-POINTERS (DEAD_ENDS.md:380-393), which used only the **86 residual
  doublets** as pointers, not all 2,928 words.
- **HIT** = `score_norm` on the concatenated retrieved words ≥ **−5.5** AND z ≥ +5 vs
  NULL-A (same pointer family from shuffled ciphertext).

### M5 — word-level WALK (clause 1 × clause 3 at the same granularity)
Walk over the **word** sequence: w ← w ± f(word), f ∈ {length, S_idx mod 29, S_prime mod 29,
S_idx mod n_words, first-rune index, last-rune index}; 32 starts; both directions;
cumulative variant. Read the visited words' initial runes, and the visited words entire.
Null methodology inherited from Round 9 Track DIRECTION.
- **HIT** = 4-gram ≥ −13.5 and z ≥ +5 vs NULL-A.

### M6 — structural counts as a message ("map" = the layout numbers)
Sequences: words-per-line (594 lines), words-per-page (57), runes-per-line,
runes-per-page, words-per-sentence (`.`-delimited). Read mod 26 → letters and mod 29 → runes.
- **HIT** = `score_norm` ≥ −6.0 (letters) / 4-gram ≥ −13.5 (runes), each with z ≥ +5 vs a
  permutation null of the same sequence.

### M7 — word-level transposition (ANALYTIC, no run needed)
If LP2 were plaintext with its **words** permuted, permutation preserves the rune multiset,
hence IoC. Measured IoC·N = **1.0000** against English-in-futhorc ≈ 1.7–1.8.
- Pre-registered decision: if IoC·N < 1.10, word-level transposition of plaintext is
  excluded without a search. Recorded as an analytic elimination, not a run.

### M8 — LP's OWN solved English as the LP2 plaintext skeleton
R8-SKELETON slid LP2's 2,928 word-length sequence over 51 external texts — **LP's own
solved English was not in that corpus** (`analysis/skeleton/corpus/` = 39 files, none
Cicada). If LP2 re-enciphers material of the book's own register, this is the one text
that should have been tried first.
- Statistic: longest run of consecutive exact length matches at any offset (the
  high-power statistic R8/C-XVIII used).
- **HIT** = real longest run strictly exceeds the max over 8 shuffled controls **and**
  ≥ 12 (chance ≈ 0.4^R).

## Lane-level verdict rule (fixed in advance)

- **POSITIVE** only if some reading clears its threshold AND the decode is readable English
  AND it reproduces under `tests/validate.py` conventions.
- **NEGATIVE** = every reading inside its null band. The deliverable is then the enumeration:
  "clause 1 was interpreted these N ways at these thresholds and all died."
- The lane must explicitly consider and report the possibility that the clause is **poetry,
  not instruction** — P0 above is the evidence line for that verdict.
