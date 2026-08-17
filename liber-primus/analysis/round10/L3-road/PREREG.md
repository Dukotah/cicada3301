# PRE-REGISTRATION — Round 10, lane **L3-ROAD**

_Written before any test was run against LP2. Calibration (`calib.py`, control texts +
the two SOLVED LP2 pages only) was run first, in order to fix the numeric thresholds
below; it does not touch the unsolved ciphertext._

## The clause

The only signed methodological hint 3301 ever gave (OpenPGP 7A35090F, 2016-01-01,
`analysis/armada_osint/artifacts/raw/2016.md`):

> Liber Primus is the way. Its words are the map, their **meaning is the road**, and
> their numbers are the direction.

Round 9 killed the third clause ("numbers = direction" as a positional walk/sieve,
2,670 readings, z = −0.40) and recorded that this clause remains uninterpreted.

## Interpretation being tested

"Meaning" has a specific non-poetic sense in this corpus: **gematria**. The Gematria
Primus assigns each rune a prime; a word's *meaning*/value is its **gematria sum**, and
the author demonstrably uses gematria sums as first-class objects — the published
per-sentence sums of the solved pages are annotated prime/composite/**emirp**
(`data/scream314_lp.md:832,952`), "The Instar Emergence" = 761 = its own filename, and
PARABLE is tagged 1,595,277,641 = the **product of its per-line gematria sums**
(`research/06-liber-primus-status.md:67`).

So: **the per-word gematria sum sequence of LP2 is the "road".** Four falsifiable
readings, plus one recorded as unfalsifiable.

The word-boundary channel is *cleartext* — no per-rune substitution or additive
keystream touches it — so every test here is **key-free** and the OTP verdict does not
apply to it, exactly as in Round 9's DIRECTION track.

## Data and parse

`data/krisyotam_runes.txt`, segments 0–54 (55 unsolved segments; 55/56 = AN END /
PARABLE excluded). **Words split on `-` `.` `&` `$` only — never on `/`, which is a line
wrap** (`research/DEAD_ENDS.md:412`: 458 of 604 line breaks fall mid-word). Parser
validated against the repo's recorded corrected-parse numbers: **2,928 words / 12,956
runes / mean 4.4249**. ✓ reproduced exactly.

## Scorer and scale

Seed-sweep / Round-9 **stream-scale** rune 4-gram model (`analysis/seed_sweep/ngram.bin`).
Calibrated in `calib.py` / `calib.json`:

| | mean | sd | 0.1th pct | max |
|---|---|---|---|---|
| English-in-futhorc, n=2928 | −9.821 | 0.241 | −10.413 | |
| English-in-futhorc, n=120 | −9.811 | 0.374 | −11.021 | |
| uniform random runes, any n | −16.70 | | | −15.38 (n=48, 300 draws) |
| **PARABLE** (author's own plaintext, n=95) | **−10.027** | | | |
| **AN END** (ciphertext, n=85) | **−16.713** | | | |

## Pre-registered thresholds

**READING TESTS (T2, T3, T4, T5).** A reading is a **HIT** iff

1. length ≥ 100 symbols, **and**
2. score ≥ **−12.00**, **and**
3. score > (max over the matched shuffle-null families) **+ 0.50**.

−12.00 sits ~4.7 sd of the null-band width above the uniform-random maximum and ~9
English-sd below the English mean; the same −12.5 line was used and validated by Round 8's
seed sweep. Readings in [−13.00, −12.00) are logged as **FLAGGED** (inspect by eye, not a
claim). Everything below −13.00 is **NULL**.

**COUNT TESTS (T1).** Statistic computed on LP2, compared to 2,000 permutations that
shuffle the 12,956-rune stream globally and re-cut it into the *identical* word-length
sequence (preserves rune multiset + word lengths, destroys any engineered per-word
arithmetic). **SIGNAL** iff |z| ≥ 4.0 **and** permutation p < 0.001 after Bonferroni over
the number of statistics tested. Anything else is **NULL**.

**VALIDATION GATE (mandatory, run before the real tests).** A synthetic corpus is built
in which an English message is planted in exactly the positions a ROAD reading selects
(gematria-prime-selected words), the rest filler. The lane's detector must recover the
plant at ≥ −12.00 while the same detector on the unplanted control stays below −13.00.
**If the gate fails, no null from this lane is reportable.**

## AMENDMENT 1 — made after the validation gate, before any LP2 test was run

The gate exposed a real weakness in the pre-registered threshold and it is recorded rather
than quietly patched. `gate.py` GATE-B plants an English message in prime-sum-marked words
and asks the `sum is prime` predicate to *discover* it with no oracle. It scored **−12.82**,
i.e. it **failed** the −12.00 bar, because a selector's output is inevitably diluted with
false-positive filler words (measured purity 0.728). The measured power curve
(`gate.json:B2`) shows the absolute threshold is dilution-fragile:

| purity of selected set | 1.0 | 0.9 | 0.8 | 0.7 | 0.6 | 0.5 |
|---|---|---|---|---|---|---|
| score | −9.96 | −10.88 | −11.72 | −12.53 | −13.36 | −14.29 |

A −12.00 absolute bar therefore only has power above ~78% purity — so an absolute-threshold
null would have been much weaker than it looked.

**Amendment:** T2–T5 add a second, dilution-robust statistic with its own threshold, fixed
now: **z of the reading's score against the *same* reading family run on matched shuffled
corpora**, with **HIT iff z ≥ 8.0**. Measured null for the prime-selector reading over 200
shuffled corpora: mean −16.680, sd 0.048, max −16.550; the diluted plant sits at **z = 79.7**,
and even a 50%-pure plant is z = 49.5. The absolute −12.00 bar is retained as the *reporting*
bar for "readable"; **z ≥ 8.0 is the falsification bar**, and it is the stricter test of the
two by a wide margin.

**GATE RESULT: PASS** — A (oracle selector) −9.96; B3 (end-to-end, dilution-robust) z = 79.7;
C (specificity on unplanted filler, worst of 12 predicate×mode readings) −16.61; D (sum-mod-29
decode) −10.01 with 99.76% exact symbol recovery; E (gematria reading order) −10.00.

**One further fact from the gate, load-bearing for T4:** a *wrong* word order over genuinely
English words still scores **−11.85** (E2), because word-internal 4-grams survive any
permutation. So T4 has almost no power to discriminate *orderings* — but it does not need to:
if LP2's words were English words in *any* order, the identity order would already score in
the −11.9 band. It scores −16.7. T4 is therefore decided before it is run, and is executed
only to record the number.

## The tests

| # | Reading of "their meaning is the road" | What is computed |
|---|---|---|
| **T1a** | the sums are *marked* numbers | rate of word sums that are prime / emirp / totient-shaped (s+1 prime) / ≡0 mod 29 / Fibonacci / equal to a Cicada constant, vs permutation null |
| **T1b** | line/sentence/page sums are checksums (the PARABLE 1,595,277,641 convention) | prime rate of per-sentence / per-line / per-page sums; any sum equal to a known Cicada number (3301, 761, 1033, 2113, 3203, 1595277641); page-sum products |
| **T2** | each word's meaning *is* one symbol of the road | sum reduced to a rune (s mod 29, s mod 26, digit-sum, prime-index, Δs mod 29, cumulative s mod 29, …) → 2,928-symbol sequence, scored |
| **T3** | meaning *selects* which words are on the road | words passing a number-theoretic predicate on their sum → concatenate whole word / first rune / last rune / rune at (s mod len), scored |
| **T4** | meaning defines the reading **order** ("road" = path) | words re-ordered by sum (asc/desc/mod 29/mod 26/rank), concatenated, scored |
| **T5** | the sum is a **pointer** into a key text (word-granularity book cipher) | s mod \|text\| indexes a word of a high-prior key text; first letters read off, scored. *Low prior — the keytext family is dead by mechanism (Round 7); run as confirmatory only, and reported as such.* |

## Recorded as ALREADY ELIMINATED — not run

* **Per-section / per-page semantic keying.** The lane brief asks whether a page-level
  semantic handle was ever tried as a per-section key. It is dead three ways and will not
  be re-run: (a) Campaign IV proved the keystream is **continuous across every page join**
  — doublet suppression holds at boundaries, so there is no per-section reset to key
  (`RECON-SUMMARY-2026-07-28.md`); (b) LP2-H2 tested the sparse version (reset restricted
  to the 14 red section heads) and got perm p = 1.0, red joins *lower* than non-red; (c)
  Round 7 killed **any** keytext by mechanism, 0/15 unanimous, independent of which text.
  Additionally the LP1 method is **non-generalisable by construction**: its key was a
  thematic word *taken from that page's own plaintext*, which for LP2 is precisely what we
  do not have.
* **Rune-level positional walks / sieves / pointer chases.** Round 9 DIRECTION, 2,670
  readings, REAL −16.08 vs null max −15.67. T2–T4 here are **word/gematria-level and were
  not in those families**, but no rune-level walk will be re-run.

## Recorded as UNFALSIFIABLE — not run

* "The meaning of the words is the road" read as *the semantic content of the decrypted
  text guides you onward* — i.e. the clause is a statement about the message you get
  **after** solving, not a method. This is the most likely plain-English reading and it is
  **unfalsifiable from the ciphertext**: it predicts nothing measurable pre-solve. Logged
  so future researchers do not mistake its untestedness for an open lead.
* "Meaning" as a pointer to an *external* semantic resource (a dictionary, a specific
  edition) with no stated indexing rule: no threshold can be fixed without first fixing
  the resource and the rule, which is a free parameter of unbounded size.
