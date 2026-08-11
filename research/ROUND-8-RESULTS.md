# Round 8 — five fresh angles, run to verdict (2026-08-11)

Motivated by `research/FRESH-ANGLES-2026-08.md`. The prior program declared itself
"ciphertext-only COMPLETE / external-input-only". That verdict is well-earned for
**rune-value cryptanalysis** and is not challenged here. What Round 8 tests is the
generalisation of that verdict to *all* axes: three of the five tracks below are
neither ciphertext-only attacks nor external inputs, but unexamined dimensions of
artifacts already in hand — the **entropy** (as opposed to the structure) of the
keystream, the **geometry** of the page images, and the **cleartext structural
skeleton**.

Every track was pre-registered with a statistic and a kill condition, run on
validated harnesses, and is reproducible from this repo. Results are NEGATIVE.
They are recorded here as *for-sure dead leads* so no future researcher spends
time on them, and so the reasons are auditable rather than asserted.

Code: `liber-primus/analysis/seed_sweep/`, `liber-primus/analysis/geometry/`,
`liber-primus/analysis/skeleton/`.

---

## Track SEED — is the "one-time pad" actually a seeded PRNG?

**The idea.** Every prior round measured keystream *structure* and correctly found
none. None measured keystream *entropy*. A PRNG stream is indistinguishable from a
pad by every structural test in this repo (flat IoC, no period, no boundary reset,
continuous across the book — exactly what one scripted pass over one long file
produces), yet carries only 31–48 bits of key. A hobbyist in 2013–14 writing an
enciphering script almost certainly called `rand()`, not a hardware pad.

**Why this is not R1-H2 (self-avoiding LCG, Gate-#1 KILL).** That kill's decisive
objection was that an OTP-class object "admits a valid structureless key for ANY
chosen plaintext" (page-0 underdetermination). True for unconstrained keys (29ⁿ);
false for a key that is a deterministic function of a ≤2³² seed. 12,956 runes carry
roughly 32,000 bits of English redundancy against ≤32 bits of key, so the expected
number of spurious English-scoring decrypts across the entire sweep is ~0. English
cannot be manufactured by construction from 4·10⁹ trials. The kill's second
objection (keyspace search) is answered by exhaustiveness over a *named finite
family* with a measured false-positive budget: a null is then an elimination, not a
failed fishing trip.

**Why it also escapes R1-H3 / R3-H1 / R3-H2 (collision-skip "un-invertible").**
Those kills concern *decoding without the key* — a decoder cannot see which
positions stalled and must search them. With a candidate seed you never decode: you
replay the encoder forward and compare to ciphertext. The rejection rule
(`redraw if c[i]==c[i-1]`) is one line in the generator and costs nothing. That
variant is included in the sweep (gen 2).

### Harness validation (this is what makes the null meaningful)

| generator | validated against | result |
|---|---|---|
| glibc `random()` / `rand()` | real libc, 5 seeds × 2000 draws | **exact** |
| MT19937 `init_genrand` | independent Python implementation | **exact** |
| Python 3 `random.seed(int)` + `randrange(29)` | real CPython `random` | **exact** |
| Python 3 `random.seed(int)` + `int(random()*29)` | real CPython `random` | **exact** |
| Java `Random.nextInt(29)` | Javadoc LCG spec, independent impl | **exact** |

Self-plant: known English enciphered at a known seed under each of the 10
generator/reduction variants, with two null ᚠ interrupters inserted. **10/10
recovered**, true score −11.24 vs wrong-seed −15.8…−16.9. The decoder honours the
documented interrupter rule (a null ᚠ is removed and does **not** advance the key)
by branching over the ᚠ decisions inside the scored window.

Scorer: rune 4-gram log-probability built from 7.57 M runes of English
transliterated into futhorc. At the 48-rune scoring window, English scores
mean −9.74 (0.1th percentile −11.55); uniform-random scores mean −16.70 (max −14.43
over 20,000 draws). Detection threshold −12.5 sits far below the English tail and
far above the random tail. Two-stage: any hit would be re-scored over the full
12,956 runes.

### Coverage and result

Generators × reductions swept (each in both directions, p = c−k and p = c+k):

```
0 glibc random()%29            5 mt19937 init_genrand %29
1 glibc random() scaled        6 mt19937 init_genrand via double
2 glibc random()%29 + no-repeat rejection   7 py3 seed(int)+randrange(29)
3 MSVC/ANSI rand()%29          8 py3 seed(int)+int(random()*29)
4 MSVC/ANSI rand() scaled      9 java Random.nextInt(29)
```

**Time-seed range** — `srand(time(NULL))` over unix seconds 2011-01-01 → 2015-01-01,
126,230,400 seeds × 10 generators × 2 directions = **2.52 · 10⁹ decodes**:

| gen | best score | hits > −12.5 |
|---|---|---|
| 0 glibc %29 | −13.27 | 0 |
| 1 glibc scaled | −13.13 | 0 |
| 2 glibc %29 + no-repeat | −13.37 | 0 |
| 3 MSVC %29 | −13.29 | 0 |
| 4 MSVC scaled | −13.51 | 0 |
| 5 mt19937 %29 | −13.24 | 0 |
| 6 mt19937 double | −13.46 | 0 |
| 7 py3 randrange | −13.23 | 0 |
| 8 py3 int(random()*29) | −13.16 | 0 |
| 9 java nextInt | −13.44 | 0 |

The best score anywhere in 2.5 · 10⁹ decodes is −13.13, i.e. **the maximum of the
null**, more than 1.5 units below the English 0.1th percentile. Nothing rises
toward language.

**Full 32-bit seed space** (0 … 2³²−1, all ten generators, both directions —
8.6 · 10¹⁰ decodes) is queued and appends to `results_full32.txt`; generator order
is 0,3,5,7,9,1,4,6,8,2 so partial coverage is always well defined.

**Non-integer / lore seeds**: 1,284 candidates (Cicada vocabulary as `str` and
`bytes` — CPython hashes these through SHA-512 before `init_by_array`, so they are
unreachable from the integer sweep — plus every date 2012-01-01…2014-12-31 as
YYYYMMDD, the PGP fingerprint, the onion addresses, the 2012 P.S. numbers) × 6 draw
methods (`randrange`, `randint`, `int(random()*29)`, `choice`, `shuffle`,
`getrandbits`) × 2 directions = **15,408 decodes. Best −14.69, zero hits.**

### VERDICT — NEGATIVE

The LP2 keystream is **not** the output of glibc `rand()`, MSVC `rand()`, MT19937,
CPython's `random` or Java's `Random` seeded from any clock value in 2011–2015, nor
from any Cicada-lore string or date. This is the first *quantitative* evidence that
the keystream is not machine-generated from a small seed — until now, "one-time pad"
rested entirely on the *absence* of structure, which a 32-bit PRNG also exhibits.

**Do not revive** any seeded-PRNG reconstruction over these generators and ranges.
What remains open in this family, honestly stated: seeds outside 2³² (Java's full
48-bit space, seeds from `/dev/urandom`, multi-word `init_by_array` keys), other
generators (PHP `mt_rand` with its distinct tempering, .NET's subtractive
generator, `xorshift`, RC4/ARC4 keystreams), and a keystream **offset** other than
zero (this sweep assumes key index 0 aligns with the first rune of LP2 page 0). Any
future work here should extend `sweep.c`, which is built for it.

---

## Track GEOMETRY — the page images as a typeset document

**The gap.** `analysis/stego/STEGO-VERDICT.md` swept file-level channels (appended
bytes, EXIF/COM/XMP, carve, spatial LSB, DQT, OutGuess) — all empty. But its own
provenance finding is that these are 400-DPI Ghostscript renders of a PDF, i.e. a
*typeset document*, whose canonical covert channel is **geometry**: glyph advance,
baseline offset, glyph-shape substitution. Never measured here. The vision armada
tried to *read* the glyphs; it never *compared* them.

All 56 pages re-verified byte-authentic (56/56 SHA1 vs the archived onion7 dump)
before analysis. Segmentation: line bands from the horizontal ink projection with
an adaptive threshold (the profile never reaches zero between lines because
ascenders and descenders of adjacent lines overlap — an absolute threshold merges
the whole page into 2–3 bands, which is the trap the first two attempts fell into),
then connected components per band, then horizontal-overlap merging.
**646 line bands vs 604 canonical lines; 18,461 glyph groups; 13,140 clean
full-height glyphs.**

### A. Glyph-shape substitution — the decisive test

Question posed so it needs no transcription, no clustering, no alignment: *does the
book contain any glyph with no near-duplicate elsewhere in the book?* In a font
render the answer must be no — every rune is drawn from one outline, so every
instance has hundreds of siblings differing only by rasterisation phase and JPEG
threshold noise. A rotated, mirrored, modified or substituted glyph is precisely the
thing that would have no sibling.

Measured: exact pixel Hamming distance from every full-height glyph to its
**nearest neighbour** among glyphs of the same (height, width) ± 1 px, normalised by
its own ink. No resampling anywhere.

```
glyphs analysed                     13,121
nearest-neighbour Hamming / ink     mean 0.0060   median 0.0000
                                    p90 0.0000    p99 0.0341   p99.9 1.358
glyphs whose closest sibling differs by >25% of their ink:  82 (0.625%)
```

**The median glyph has a pixel-identical twin.** Ninety per cent have zero
difference from their nearest neighbour. The 82-glyph residue was rendered for
adjudication (`shape_outliers3.png`) and is segmentation artifact — broken strokes
and merged blobs, 22 of the worst 60 falling below the 5th percentile of population
ink area, others at 4× it — not modified glyphs.

Two earlier versions of this test failed and the failures are recorded in the source
so nobody repeats them: clustering *resized* 48×48 masks measured segmentation
quality rather than glyph fidelity, and comparing each glyph to its size-group's
modal mask blends several different runes that happen to share a bounding box (and
underflows uint8 subtraction).

**VERDICT: glyph-substitution steganography is dead.** The 56 pages contain no glyph
that is not a faithful repeat of the same small set of font outlines.

### B. Micro-spacing (inter-glyph advance) channel

First measurement was confounded: raw ink gaps look strongly bimodal (means 4.4 and
20.8) purely because word-separator dots had been filtered out of the glyph
sequence, so separator positions appear as wide gaps. Corrected two ways — separator
positions excluded, and then pitch measured as `x0[i+1] − x0[i]` minus the median
pitch for the *class* of glyph i, which removes glyph-shape variation and isolates
the typesetter's advance decision.

Separator-free advance: n = 11,035, mean 6.35 px, sd 8.10, interquartile range
4–6 px; the dominant GMM component is mean 4.43 with sd 1.63 carrying 89% of mass,
and the second component is a wide tail (sd 17.4), not a second state — component
separation **1.86 σ**, below the ~2 σ a 1-bit channel needs to be readable at all.

**VERDICT: no two-state micro-spacing channel.**

### C. Baseline jitter channel

Baseline offset measured within rune class (so glyph-shape differences cannot
manufacture spread): sd 4.15 px, interquartile range 0. A two-component GMM is
**rejected by BIC** (Δ = −22 to −25 in favour of one component) in both the raw and
within-class forms.

**VERDICT: no baseline channel.**

### D. Ornament inventory

Every segmentation pipeline in this repo explicitly discards "ornament components
far from the dominant text column"; nobody had listed them. 47 non-text bands across
23 pages are catalogued in `geometry_report.json`. Note honestly: most are
mis-segmented text lines rather than true ornaments, and the genuinely short bands
(1, 3, 4, 8 and 16 glyphs) are the only real candidates. This is inventory, not a
result — it is the one item in Round 8 left as an open thread rather than a verdict.

---

## Track PAYLOAD — is the plaintext binary rather than prose?

**The gap.** Every "no language" verdict in this repo (IoC_norm, quadgram scoring,
`CRYPTO-RIGOR §C`, R5 ROSETTA) is blind to a *compressed or binary* plaintext. gzip
output, a PGP packet stream and a one-time pad all have flat IoC by construction, so
"flat IoC" has been read as "still encrypted" when it is equally consistent with
"already decoded, but not prose". R5 ROSETTA was killed on the grounds that
non-English *language* would raise IoC — correct, and irrelevant to a binary payload.

Tested: the key-free, parameter-free decodes (raw, first difference, rank-in-28,
collision-unbump; each also reversed and Atbash-mapped) packed to bytes across
base-29 and base-28 bignum conversion in both digit orders and 5-bit packing in both
bit orders at all 8 phase offsets — **166 representations**. Detectors: 40 file
magics, PGP/PEM armor strings, zlib/raw-deflate/gzip inflation attempted at every
offset in the first 4 KB, long letter-runs, byte entropy and χ².

```
raw        7,868 bytes  entropy 7.9769  chi2(255 df) 246.7  printable 0.373
firstdiff  7,867 bytes  entropy 7.9735  chi2(255 df) 285.3  printable 0.366
rank28     7,815 bytes  entropy 7.9747  chi2(255 df) 270.2  printable 0.374
```

χ² of 246.7 on 255 degrees of freedom is *exactly* uniform (p ≈ 0.5). No magic
header, no armor, no inflatable region, no long letter-run in any representation.
(Single-byte "magic" matches such as the 0xC5/0xC6 PGP packet tags occur at chance
rate ≈ 1/256 per representation and are noise by construction.)

**VERDICT: NEGATIVE.** The unsolved pages are not a container, an archive, a
compressed stream or a key file in any of these representations. "Flat IoC" is now
backed by a byte-level uniformity measurement rather than only by a language model's
silence.

---

## Track POINTERS — the 86 residual doublets as an index list

Round 5 tested the surviving doublets as *cipher structure* (digraphic parity,
doubled-rune identity, gap distribution) and killed all three. Nobody tested them as
a *payload*: an 86-element position list is the shape of a book-cipher index, and
Cicada's own solved pages are the obvious book.

86 doublets, positions 122…12,939, 85 gaps (min 6, max 712, mean 150.8). Readings
tested: the doubled rune values as a message; gaps as letters (mod 26, mod 29,
offset −1); gaps and cumulative gaps as word indices into the solved LP1 English
(both 0- and 1-based); positions as word indices into LP2's own cleartext word
skeleton; the runes immediately before and after each doublet; and gaps against
primes and Fibonacci.

```
best score across all readings          −16.34
null (2,000 random position sets)       mean −16.69  sd 0.244  max −15.60
English-class threshold at this length  ≈ −12
```

Every reading sits inside the random null; the best is 1.5 σ from the null mean and
4 units short of language. Positions prime: 3/86 against ~10 expected — a deficit,
p ≈ 0.007 one-sided, **not** significant across the ~15 readings tested here and
with no mechanism behind it; recorded so nobody re-reports it as a signal.

**VERDICT: NEGATIVE.** The residual doublets carry no pointer payload.

---

## Track SKELETON — the cleartext channel

Word (`-`), clause (`.`), line (`/`) and page (`%`) boundaries are **not
enciphered**, so word length in runes is a plaintext invariant under any per-rune
substitution or additive keystream, including a one-time pad. The
information-theoretic wall applies to rune *values*; it does not touch this channel.
Every "keytext" entry in `DEAD_ENDS` concerns a text used as a **key**; this asks
whether a known text is the **plaintext**, which needs no key at all — and if a
match were found, the plaintext yields the keystream by subtraction.

> **Parsing correction applied after the first run — read this before reusing any
> word-length number from this repo.** `/` in the krisyotam transcription is a
> LINE WRAP, not a word separator: **458 of the 604 line breaks fall mid-word**
> (e.g. `…-ᛝᚫᚦ-ᛁ / ᚫᚻᛉᚦᛈᚷ-`). The first pass treated `/` as a word terminator,
> which shattered 458 words into fragments, gave 3,316 "words" instead of 2,928,
> and manufactured a spurious 2× excess of one-rune words. All figures below are
> from the corrected parse. The corrected verdicts are unchanged in direction;
> the numbers are not.

### B1. Is a known text the plaintext? — corpus fingerprint scan

Corpus: **51 texts, 8,205,104 words** — the repo's existing key texts plus 39
fetched works chosen for the Cicada canon (Blake ×3, Emerson ×2, Thoreau,
Bunyan, Marcus Aurelius, Tao Te Ching, Bhagavad Gita, Kybalion, Corpus
Hermeticum, Book of Enoch, Dhammapada, Upanishads, Quran, KJV, Apocrypha,
Poetic/Elder Edda, Beowulf, Chaucer, Homer ×2, Dante, Nietzsche, Plato, Hobbes,
Machiavelli, Locke, Shakespeare complete) plus deliberate controls (Dracula,
Frankenstein, Huck Finn, Sherlock, Crime and Punishment, Metamorphosis).
`fetch_corpus.sh` reproduces it; only Paradise Lost failed to download.

Scan: FFT cross-correlation of LP2's rune-word-length sequence against every
alignment offset in every text — every one of the ~8.2 M offsets is scored, not a
sample. Slack 0 (exact) and slack 1 (absorbs one null interrupter per word plus
transliteration ambiguity). Null: the identical scan with LP2's own sequence
shuffled, so the control carries the same length distribution and the same
maximum-of-many-offsets bias.

| window | slack | best real | best text | shuffled control (mean / max) | z |
|---|---|---|---|---|---|
| 2928 words | 0 | 581 (19.8%) | KJV | 532 / 586 | 2.07 |
| 2928 words | 1 | 1441 (49.2%) | KJV | 1348 / 1438 | 2.03 |

A genuine plaintext identification would score **near 100%**, not 19.8%. The best
real score is *below* the shuffled control's own maximum on the same texts (586),
and the leaderboard is simply an ordering by text length (KJV, Chaucer,
Mabinogion, Homer — the longest texts, hence the most alignment offsets, hence the
highest maximum). That is the maximum-of-many effect, not a match.

**VERDICT: NEGATIVE.** The LP2 plaintext is not any of these 51 texts at any
alignment. Note what this does and does not say: it eliminates a specific 8.2 M-word
corpus, not "any known text". The method is sound and cheap, so extending it to a
full Gutenberg mirror is the obvious follow-up and `wordlen_search.py` is written
for it — drop files into `analysis/skeleton/corpus/` and re-run.

### B2. Does the cleartext look like prose at all? — and a live anomaly

| comparison | mean word length | KS vs LP2 | KS after simulating 458 null F | crit@.05 |
|---|---|---|---|---|
| LP2 unsolved (2,928 words) | **4.425** | — | — | — |
| Moby Dick | 4.101 | 0.0841 | 0.0469 | 0.0253 |
| Pride & Prejudice | 4.152 | 0.0725 | 0.0386 | 0.0254 |
| KJV | 3.758 | 0.1235 | 0.1058 | 0.0253 |
| Mabinogion (English) | 3.824 | 0.1052 | 0.0712 | 0.0255 |
| Caesar, *De Bello Gallico* (Latin) | 5.717 | 0.2371 | 0.2526 | 0.0266 |
| Welsh prose | 3.786 | 0.1668 | 0.1395 | 0.0277 |

**LP2's words are longer than English, by more than the interrupters can explain.**
A null ᚠ adds one rune to its word; all 458 of them supply +0.156 runes/word, but
the gap to English is +0.32. Simulating English-in-futhorc with Poisson F-insertion
at the full 458 rate still leaves KS 0.039–0.047 against a 0.025 critical value.
Latin is far too long (5.72) and Welsh/KJV/Mabinogion too short, so this is not
simply "the plaintext is another language" among the obvious candidates.

Clause-position structure, correctly scoped to the 55 unsolved pages and the
corrected word parse:

```
clause-FIRST 4.129 (n=209)   clause-LAST 4.267 (n=206)   INTERIOR 4.462 (n=2513)
first vs interior  −0.333 runes   permutation p = 0.047   (marginal)
last  vs interior  −0.195 runes   permutation p = 0.246   not significant
```

Clause-initial words being *shorter* than clause-interior words is the direction
natural-language prose gives (function words cluster at clause openings). At
p = 0.047 across two tests this is suggestive, not established.

**Separator audit (new, and never done before).** Every transcription check in this
repo compared *rune streams* — `crossdiff.py` found the three lineages identical
13,136/13,136. Nobody had checked the *separators*, which descend from the same
single root and which every word-boundary-dependent result depends on. Separator
dots are a distinct component class in the render (uniform ~9×10 px; 3,027 of them).
Compared per line against the transcription on rune-count-exact aligned lines
(per-*page* comparison is invalid — relikd image numbering ≠ krisyotam page
numbering): **151/170 lines agree exactly (88.8%), mean difference −0.03 ± 1.10 —
no systematic bias.** So missing word separators do **not** explain the length
anomaly. The 19 disagreeing lines are listed in `geometry/separator_audit.json`;
most are likely my own dot-to-row attachment, but they are the correct shortlist
for a human or high-zoom re-read.

**VERDICT: the corpus identification is NEGATIVE and the positional signature is
not usable. But the length anomaly is left OPEN**, and it is the one live thread
Round 8 produced rather than closed. It lives in a channel no cipher touches, it
survives the interrupter correction, it survives the separator audit, and it is not
explained by Latin or Welsh.

---

## What this round changes

- The "one-time pad" characterisation now rests on a **measurement of key entropy**,
  not only on the absence of key structure. That is a materially stronger claim than
  the repo could previously make, and it was obtained by taking the hypothesis
  seriously rather than by another structural test.
- Three channels that were never examined — glyph geometry, byte-level payload
  structure, doublet pointers — are closed with stated coverage.
- One genuine methodological correction: "flat IoC ⇒ encrypted" was an
  over-reading. It is now backed by a byte-uniformity measurement.
