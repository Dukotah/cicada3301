# Round 45 / I1 — Decoy-space instrument audit: RESULTS

_2026-11-23. Pre-registered in `PREREG.md` (written before any output). Raw: `out_beam.json`, `out_wordsched.json`,
`out_skeleton.json`, `out_7gram.json`, `inventory.json`; merged `results.json`; rows `ledger_rows.json`.
Rig health: `python tests/validate.py` passed at lane start (6/6 solved pages reproduced)._

## 0. Headline

* **The standing pipeline does not use the printed spaces at all.** beam_v3, panel-R36 `adjudicate`, bars_v3,
  pf_v4 / pf_v4_12 and `verify_solution.py` consume rune indices only (source grep: 0 word-boundary consumers).
  Planted check: the ciphertext page was rendered with `-` separators placed by each condition and parsed back the way
  the repo loaders do; conditions a–d gave **bit-identical decodes and pmax for 160/160 plants**.
* **The H-shuffle reading (spaces true, words reordered) costs the pipeline nothing measurable.** Words permuted within
  the page before encipherment: power at the N = 1e6 bar 1.00 in 8/8 cells (N = 20 each), oracle two-page PASS 10/10
  in every cell, median pmax down by only 0.3–0.9. The panel's trigram LMs barely see word order.
* **So every key-space negative adjudicated by beam_v3 + panel-R36 is NOT conditional on the spaces.** The negatives
  that ARE conditional are the lanes that index a key schedule or a plaintext model by printed words. Under H-decoy their
  measured power is **0.00**: R37-C1 U2b and U3, R41-C1 R14 W1–W4 (and by construction R38-C1 ×2, R39-C1, R38-C2-G3),
  Round 8 SKELETON (C-01), and the 7-gram shape model of R44-W2A2 (coverage ~1.2 % per site).
* Space-blind controls inside the same glue survive every condition (R37 U2a 16/16, R41 W5 4/4), so the collapse is the
  segmentation, not the harness.

## 1. Dependency table (inventory)

`inventory.py` grepped the 7 standing instruments and all 351 `LEDGER.json` rows (81 grep hits); hits were classified
by hand from row text (and lane code where noted). Classes: **A** negative conditional on spaces = plaintext words in
order; **B** reads the printed structure itself as the channel (not conditional; *more* relevant if the spaces are a
keyed channel); **C** uses the true spaces of SOLVED pages; **D** space-blind instrument whose plants are in-order prose.

| instrument / row | how it uses spaces | breaks under | class |
|---|---|---|---|
| beam_v3, beam_v2 enciphers, pf_v4, pf_v4_12, adjudicate, bars_v3 | none (rune indices only); plants are spaceless in-order prose | nothing measured (e: no loss) | D |
| verify_solution.py | none (pages = rune runs; `--plaintext` strips non-letters) | nothing measured | D |
| HUMAN-ORACLE.md | read rule "connected prose, not word-salad" | **H-shuffle**: a correct key reads as word-salad (rule-level, unmeasured) | rule |
| tests/validate.py | must-contain words on SOLVED pages | — (solved-page spaces are real, z = +7.4) | C |
| C-01 / Round 8 SKELETON | aligns printed LP2 word lengths to corpus lengths | b, c, d (power 0) | A |
| R37-C1-U2 (U2b half) | LP1-sum pointer jumps at printed word starts | b, c, d (0/16) | A |
| R37-C1-U3 | per-word shift / key advance from word index, offset, length | b, c, d (0/24) | A |
| R38-C1-SEMANTIC-WORDNET, -FREQRANK, R39-C1-SENSE-SIMILARITY, R38-C2-G3 | same lens-indexed d_k form as U3 | inherit U3 (not re-run) | A |
| R41-C1-R14-WORDSUM-SELFKEY (W1–W4) | gematria sum of printed word keys the next word | b, c, d (0/16) | A |
| R44-W2A2-7GRAM-DIFFPLAIN | site plaintext = (3-word, 3-word, head) from printed gaps | H-decoy: shape true for ~1.2 % of windows | A |
| R40-C1-INCONCLUSIVE-R31 | crib readouts at printed word positions | (already inconclusive) | A |
| C-02, R10-L2-MAP, R10-L3-ROAD, R37-C3-U5-L2/L3, R40-C1-R04-M4, B-12, R11-S2, R37-C3-U6A-S2, R44-P3-SEPARATOR-IDENTITY, R44-P3-QUOTESPAN-* | read printed initials / sums / lengths / counts / separators / quote spans as the channel | not conditional (they test the print itself) | B |
| R22-A, R23-A2, R40-C1-R28, R37-C2-U7(-W), R44-W2A2-P55 | solved-page text / LP1 words | not conditional | C |
| R33-I1 envelope, L7-B envelope, R41-I1 null refit, R44-R1 reset sweep | beam/panel plants in order; R44-R1 resets at LINES not words | H-shuffle only: measured no loss | D |

## 2. Measurements (power per condition, N plants)

Conditions: **a** true lengths · **b** true lengths permuted within page · **c** LP2's printed lengths (decoy) ·
**d** no spaces · **e** H-shuffle (words permuted within page before encipherment).

### 2.1 Beam + panel + bars + oracle + pf_v4_12 (correct key, SHA-256-CTR, supp 0.83; plants from `data/pride.txt`)

| cell | N | bar_v3 1e6 | a–d identical | power@1e6 a / e | median pmax a / e | oracle 2-page PASS a / e | pf_v4_12 a / e |
|---|---|---|---|---|---|---|---|
| EN keyskip1 L120 | 20 | 9.235 | 20/20 | 1.00 / 1.00 | 17.8 / 17.5 | 10/10 / 10/10 | 1.00 / 1.00 |
| EN keyskip1 L240 | 20 | 9.514 | 20/20 | 1.00 / 1.00 | 26.3 / 25.6 | 10/10 / 10/10 | 1.00 / 1.00 |
| EN skip_by_two L120 | 20 | 9.034 | 20/20 | 1.00 / 1.00 | 18.0 / 17.4 | 10/10 / 10/10 | 0.95 / 0.95 |
| EN skip_by_two L240 | 20 | 9.15 | 20/20 | 1.00 / 1.00 | 26.3 / 25.4 | 10/10 / 10/10 | 1.00 / 1.00 |
| EN_NOVOWEL keyskip1 L120 | 20 | 9.235 | 20/20 | 1.00 / 1.00 | 16.0 / 15.5 | 10/10 / 10/10 | 0.95 / 0.95 |
| EN_NOVOWEL keyskip1 L240 | 20 | 9.514 | 20/20 | 1.00 / 1.00 | 22.2 / 21.6 | 10/10 / 10/10 | 0.95 / 1.00 |
| EN_NOVOWEL skip_by_two L120 | 20 | 9.034 | 20/20 | 1.00 / 1.00 | 15.5 / 14.7 | 10/10 / 10/10 | 1.00 / 0.95 |
| EN_NOVOWEL skip_by_two L240 | 20 | 9.15 | 20/20 | 1.00 / 1.00 | 21.8 / 21.4 | 10/10 / 10/10 | 0.95 / 0.95 |

Since a–d are bit-identical, power under b, c, d equals power under a in every cell. Recovery was 1.000 median in all
cells and conditions. Baseline gate (PREREG §3: EN keyskip1 L120 ≥ 0.90) passed.

### 2.2 Word-boundary key schedules (lanes' own encipherers, decoders and rules)

Enciphered with the TRUE segmentation of the pride plaintext; decoder handed the condition's segmentation.

| schedule | N per cond | a | b | c | d | median recovery b / c / d |
|---|---|---|---|---|---|---|
| R37 U2a (space-blind control) | 16 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 / 1.00 / 1.00 |
| R37 U2b | 16 | 1.00 | 0.00 | 0.00 | 0.00 | 0.19 / 0.11 / 0.07 |
| R37 U3 A1 | 6 | 1.00 | 0.00 | 0.00 | 0.00 | 0.22 / 0.14 / 0.02 |
| R37 U3 A2 | 6 | 1.00 | 0.00 | 0.00 | 0.00 | 0.09 / 0.08 / 0.05 |
| R37 U3 A3 keyskip1 | 6 | 1.00 | 0.00 | 0.00 | 0.00 | 0.08 / 0.10 / 0.08 |
| R37 U3 A3 keyskip2 | 6 | 1.00 | 0.00 | 0.00 | 0.00 | 0.10 / 0.10 / 0.09 |
| R41 R14 W1–W4 (exact) | 16 | 1.00 | 0.00 | 0.00 | 0.00 | ≤ 0.21 |
| R41 R14 W1–W4 (pmax > null max 5.50) | 16 | 1.00 | 0.00 | 0.00 | 0.00 | max pmax 4.75 / 4.53 / 4.37 (a: 31.6) |
| R41 R14 W5 (per-rune autokey, space-blind) | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

R37 rule = `judge()`: pmax120 ≥ bar_v3(1e6,120) AND pmax240 ≥ bar_v3(1e6,240) AND recovery ≥ 0.90. Best U2b/U3
pmax240 under b/c/d: 8.55 / 6.83 / 5.14 against the bar 9.15 (a: 28.65).

### 2.3 SKELETON (C-01; `analysis/skeleton/wordlen_search.py` corpus_lengths + scan, corpus pride + moby)

| W (words) | N | a | b | c | d | match fraction at true offset a / b / c | shuffled-null max fraction |
|---|---|---|---|---|---|---|---|
| 120 | 20 | 1.00 | 0.00 | 0.00 | 0 (no pattern) | 1.00 / 0.18 / 0.14 | 0.34 |
| 400 | 20 | 1.00 | 0.00 | 0.00 | 0 (no pattern) | 1.00 / 0.19 / 0.15 | 0.25 |

Detection = global argmax over pride+moby is the planted offset AND its count beats the max of 5 shuffled-pattern
scans. Permuting lengths within 53-word pages drops the aligned match fraction from 1.00 to ~0.18, below the null
max; LP2's printed lengths carry nothing about a pride plaintext (0.14-0.15, chance). Baseline gate (W=400 >= 0.90)
passed. An order-free per-page multiset matcher would survive (b); SKELETON as built does not.

### 2.4 7-gram plaintext shape (R44-W2A2-7GRAM-DIFFPLAIN)

Fraction of 7-rune windows whose TRUE segmentation is word-aligned 3|3|head: pride **1.32 %** (6,818 / 517,224), moby
**1.09 %** (9,387 / 861,880). The same count over LP2's own printed gaps is 1.41 % — the print looks like English at
this granularity, so the lane's shape prior is exactly right *if* the print is real, and covers ~1.2 % per site
(~2 × 10⁻⁴ for both sites jointly if independent) if it is decoy.

## 3. Reopen list (negatives conditional on true, in-order spaces)

Measured power under H-decoy (b/c/d) is 0.00 for each, against 1.00 at baseline:

1. **C-01** — Round 8 SKELETON word-length plaintext identification (and its 51-text / 8.2 M-word negative).
2. **R37-C1-U2-LP1-NUMBER-SCHEDULES** — the U2b (pointer-jump) half only; U2a is space-blind and stands.
3. **R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION**.
4. **R38-C1-SEMANTIC-WORDNET**, **R38-C1-SEMANTIC-FREQRANK**, **R39-C1-SENSE-SIMILARITY**, **R38-C2-G3-LAGGED-POINTERS**
   — same lens-indexed construction as U3; inherited, not separately re-run.
5. **R41-C1-R14-WORDSUM-SELFKEY** — W1–W4 (W5 is space-blind and stands).
6. **R44-W2A2-7GRAM-DIFFPLAIN** — coverage ~1.2 % per site under H-decoy (not zero, but not what the row claims).
7. **R40-C1-INCONCLUSIVE-R31** — already inconclusive; add the space conditional.

Rule-level item: **HUMAN-ORACLE.md §3** ("connected prose, not word-salad"). Under H-shuffle a correct key decodes to
reordered words; the panel still scores it at full power (§2.1), but the human rule as written would call it
NOISE-CROSSER. Recommend an addendum: before ruling NOISE-CROSSER, check bag-of-words fluency (valid words, function-word
rate) separately from word order. Not measured here (no human in the loop).

Under H-shuffle alone (spaces are real word boundaries of the enciphered word sequence), the A-class schedules keep
their power, because the decoder's printed words are the words the encipherer used. Their collapse is specific to
H-decoy. W1's characterisation of the spaces decides which reading applies.

## 4. Three conditionals

1. **Key space:** none swept — correct key / correct schedule parameters handed over (power measurement).
2. **Transition model:** beam_v3 keyskip1 and skip_by_two (advance 1/2), supp 0.83; the lanes' own U2/U3 (keyskip1,
   keyskip2, direct A1/A2) and W1–W5 exact inverses. `free` not measured.
3. **Register:** panel-R36 (12 registers). Plants are English (pride, moby) and vowel-dropped English only; H-shuffle
   power for Latin/OE/DE/CY/GREEK/HEBREW/NORSE word reorderings is not measured.

## 5. Not covered

* H-shuffle at book scope (global word permutation) — expected identical (the LMs are local), not measured.
* U3 with M = 28; R38/R39 U3-form rows re-run separately.
* Schedules clocked by a *different* segmentation (e.g. the printed spaces being the key's own clock, not the
  plaintext's) — that is a construction, belongs to W1/later rounds.
* Line breaks (R44-R1 per-line resets) — a separate layer, not audited.
* B/C classification is from ledger row text; the code of those lanes was not re-run.

## 6. Surprising

* Nothing in the beam/panel/oracle stack ever looked at a space — the premise only touches the word-indexed lanes,
  which are a small, enumerable set (10 rows).
* The panel's trigram LMs are almost blind to word order: shuffling words inside a page costs ≤ 0.9 pmax at pmax ≈
  15–26. Good for robustness; it also means the panel cannot tell prose from word-salad, which is exactly why the human
  read rule is the only order-sensitive step left in the pipeline.
* The deviations in the PREREG run plan: the first two background launches of `arm_beam.py` died (one a syntax slip in
  a heartbeat line, one killed by a 120 s shell timeout mid-run); the arm was made resumable per cell and re-run to
  completion; results are deterministic in their seeds. R41's `run_c1.enc_words` was copied verbatim rather than
  imported, because importing `run_c1`/`lib` appends to `c1.log` in the R41 lane dir and requires the gitignored
  `build1/panel12.npz`.

---
CLOSED 2026-11-23T21:25 R45-I1 decoy-space | arms beam/wordsched/skeleton/7gram complete | 5 ledger rows | reopen list: C-01, R37-C1-U2(U2b), R37-C1-U3, R38-C1-SEMANTIC-WORDNET, R38-C1-SEMANTIC-FREQRANK, R39-C1-SENSE-SIMILARITY, R38-C2-G3-LAGGED-POINTERS, R41-C1-R14-WORDSUM-SELFKEY(W1-W4), R44-W2A2-7GRAM-DIFFPLAIN, R40-C1-INCONCLUSIVE-R31 | no commit, no LEDGER.json edit
