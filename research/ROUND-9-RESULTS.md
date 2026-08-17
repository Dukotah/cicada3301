# Round 9 — the length anomaly, the signed "numbers" clue, and an independent read (2026-08-11)

Three tracks. Two are complete and NEGATIVE. The third (independent
re-transcription) is the substantial one and is reported separately below when its
decode completes.

---

## Track LENGTH — the Round-8 anomaly, resolved and closed

Round 8 left exactly one thread open: LP2's mean rune-word length is **4.425**
against 4.10–4.15 for English-in-futhorc, and the 458 interrupters supply only
+0.156 runes/word against a +0.32 gap. It sat in the cleartext channel, which no
cipher touches, so it was attackable without a key.

**First, the encoder was verified against ground truth.** The solved LP2 page
PARABLE is *unenciphered plaintext transliteration*, so it pins the author's
convention exactly. The greedy-multigraph encoder used throughout this repo
reproduces **all 20 of its word lengths exactly** — THE = 2 (the TH rune),
TUNNELING = 7 (the ING rune), CIRCUMFERENCES = 14, DIVINITY = 8 (U for V),
LIKE = 4 (C for K). So the excess is not an artifact of how English is mapped into
futhorc.

**Then the comparison itself turned out to be the error.** The KS tests in Round 8
compared a 2,928-word passage against 20,000–200,000-word *aggregates*. An
aggregate has almost no sampling error, so any real passage of any text tests as
"significantly different" — a large-*n* artifact, not a property of LP2. The
correct comparison is against passages of the same size.

Sliding a 2,928-word window across every corpus text:

```
LP2 plaintext mean lies in [4.268, 4.425]
    (lower bound = all 458 F are nulls, upper = none is)

texts containing at least one 2,928-word passage that reaches 4.268:  44 / 47
```

| text | overall mean | passage-mean range | % of passages ≥ 4.268 |
|---|---|---|---|
| Dracula | 4.490 | 4.141 … 4.776 | **95.8%** |
| Dhammapada | 4.301 | 4.139 … 4.774 | 64.9% |
| Blake, poems | 4.309 | 3.957 … 4.776 | 34.6% |
| Elder Edda | 4.150 | 3.738 … 4.788 | 26.7% |
| Upanishads | 4.297 | 4.085 … 4.776 | 21.4% |
| Emerson, *Essays* I | 4.221 | 4.004 … 4.776 | 19.5% |
| Corpus Hermeticum | 4.065 | 3.853 … 4.800 | 4.7% |

And Cicada's own solved LP2 pages bracket the observation on both sides:
**AN END 3.40, PARABLE 4.75** (small samples, but they are the author's own prose).

The aphoristic and formal registers that the Liber Primus actually resembles —
Blake, Emerson, the Dhammapada, the Upanishads — run *longer* than novels and sit
squarely in LP2's range.

### VERDICT — NOT AN ANOMALY

LP2's word length is unremarkable for an English passage of its size and register.
Round 8's open thread is closed, and closed against itself: the "anomaly" was an
artifact of comparing a passage to an aggregate. **Do not re-open the word-length
excess.** Anyone repeating this must compare like-sized passages, not corpora.

---

## Track DIRECTION — "their numbers are the direction"

Unlike every other avenue in this repo, this one is licensed by a **signed 3301
statement**. The 2016-01-01 message (OpenPGP 7A35090F, recovered by OutGuess from
the tweet image, in `analysis/armada_osint/artifacts/raw/2016.md`) reads:

> Liber Primus is the way.  Its words are the map, their
> meaning is the road, and their numbers are the direction.

Three parts: words = map, meaning = road, **numbers = direction**. The repo has
attacked the numbers as a *keystream* (prime / totient / Fibonacci — all dead, and
dead by mechanism since any additive stream lands in the already-measured normal
doublet band) and as history-dependent prime transforms
(`analysis/seek_primes.py`). It had never attacked them as what the word
"direction" literally says: **a rule for where to go next**.

That is a different mechanism, not another key. It supposes the pages are largely
filler and the message sits at *computed positions*, unenciphered. Nothing measured
so far excludes it:

- flat IoC is exactly what filler produces;
- Round 6's SIEVE-W hunted readable **contiguous** windows with a sliding detector,
  so a non-contiguous, position-computed message is **invisible to it**;
- it requires no key, so the one-time-pad verdict does not apply.

Families, all deterministic and key-free:

| family | rule |
|---|---|
| A self-indexing walk | `p ← p ± f(c[p])`, f ∈ {index, index+1, gematria prime, prime mod 29, prime−1, reversed index, 2·index+1}; 64 start positions; both directions; interrupters skipped or kept |
| B cumulative walk | `p ← start + Σ f(c)` mod L |
| C sign walk | each rune's parity (or half-alphabet) picks forward/back at a fixed stride ∈ {1,2,3,5,7,11,13,29,33,133,331} |
| D numeric sieve | positions selected by predicate: prime, Fibonacci, square, every k-th for k ∈ {3,7,11,29,33,133,331,3301 mod L}, cumulative-gematria hits |

**2,670 readings** on the real ciphertext, each scored with the same rune 4-gram
model as the seed sweep, against the identical families run on six independent
shuffles of the same ciphertext.

```
REAL       best −16.0800   (B cumwalk idx start=4)
null ×6    mean −15.9671   sd 0.2825   max −15.6722
z of REAL vs null = −0.40
English-class at this length is about −11 to −12
```

The real ciphertext scores **worse than its own shuffles**. Not a single reading in
2,670 rises anywhere near language.

### VERDICT — NEGATIVE

The "numbers are the direction" instruction does not denote a positional walk,
sieve or pointer-chase over the rune stream, and there is no non-contiguous
plaintext hiding at computed positions in these families. This also closes the gap
Round 6's contiguous-window detector left open.

**Do not revive** walk / cumulative-walk / sign-walk / numeric-sieve readings.
Honest scope: this covers 2,670 readings across four families, not every
conceivable reading of the word "direction". A revival needs a *specific* rule with
a reason beyond "the numbers mean something", and it should be run through
`analysis/direction/direction.py`, which is built to take new step functions.

One thing worth keeping from the exercise: the 2016 message is the **only signed
methodological hint 3301 ever gave**, and the repo had not been treating it as a
first-class object. Its other two clauses — "its words are the map" and "their
meaning is the road" — remain uninterpreted.

---

## Track TEMPLATE — independent re-transcription

Status and results appended on completion. Design and rationale:
`analysis/retranscribe/templates.py`, `read.py`, `diff.py`.

Stage 1 is complete and is itself a result: the 13,140 full-height glyphs reduce
to **1,067 distinct exact bitmaps**, which merge without any supervision into
**32 shape classes with ≥100 members covering 95.8% of glyphs** — i.e. the font's
alphabet recovered from the images alone, ~29 runes plus a handful of
merge/split artifacts (`templates.png`).
