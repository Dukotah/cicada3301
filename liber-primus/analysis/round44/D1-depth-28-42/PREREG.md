# PREREG — Round 44 lane D1: are pages 28 and 42 in depth? (joint two-plaintext decode)

_Written 2026-11-12, before any decode of the real pair. Lane of the fresh-eyes audit
(`../A0-fresh-eyes-audit/AUDIT.md`). Doctrine: `../../../ARMADA-DOCTRINE.md`. Page numbers are the
0-based `%`-segments of `data/krisyotam_runes.txt` (flat starts 6761 and 10144; 269 and 272 runes)._

## 0. What was already seen (exploratory, declared)

An all-pairs scan by an audit reader, re-computed by the coordinator before this file was written,
found that the position-aligned difference stream `D_i = (p28_i - p42_i) mod 29` over 269 runes is
non-uniform: chi2 = 74.1 on 28 df (p = 4.8e-6), the top of the 1,485 offset-0 page pairs (next
59.2); 65.2 of it sits in the symmetric (cosine) subspace and 8.9 in the antisymmetric one;
offsets +-1..4 are flat (8.7-22.2 on 14 df); kappa = 21/269. Family-wise this is about 0.007 on the
a-priori statistic. The histogram does NOT match the monogram-level prediction for English depth
under Gematria-order letter-wise text (LLR +1.5 nats against +6.9 expected). Only the difference
histogram and its transforms have been looked at. No decode of any kind has been run.

## 1. Hypothesis

H1(sigma): pages 28 and 42 were enciphered additively with the SAME key values at the same page
offsets, without key-consuming desync on either page, so for most i
`D_i = sigma(P28_i) - sigma(P42_i) (mod 29)`, both plaintexts being English prose with the word
boundaries the ciphertext shows. Three numberings sigma are tested, each as its own cell:

| cell | plaintext orthography | numbering |
|---|---|---|
| G-LW | letter-wise (one rune per Latin letter; K->C, V->U, Z->S, Q->C) | Gematria index of that rune |
| G-MG | LP1 multigraph orthography (TH, EO, NG/ING, OE, AE, IA/IO, EA as single runes, per word) | Gematria index |
| A-LW | letter-wise, 26 letters distinct | alphabet position A=0..Z=25 (a constant shift cancels in D) |

H0: the two pages are unrelated uniform streams and the histogram is a 1-in-150 family-wise accident
(or a relation of some other kind that none of the three cells represents).

## 2. Instrument

`depth2.py`: a joint beam search over the two plaintexts. State = the last four symbols of each
text including the known word-boundary symbol. Language model = one interpolated (Witten-Bell)
5-gram character model per cell with the word boundary as a symbol, trained on committed English
texts under `data/keys/` in that cell's encoding. At position i each candidate rune a for page 28
forces b = a - D_i for page 42 (invalid if b is not a plaintext rune of the cell). Beam width
50,000, no state merging. Statistic: `S = (joint log-probability of the best path) / n` in nats per
aligned position. The decoded texts are written out for reading.

## 3. Positive control (through the lane's own glue)

12 planted pairs per cell: two passages from texts held OUT of the model's training set, each cut
to 269 runes with its own natural word boundaries, encoded in the cell's encoding, D computed, then
5 % of positions (the measured rejection rate on a page is about 3 %) overwritten with a uniform
value to stand for doublet-rewrite sites. Recovery = fraction of the 2 x 269 runes decoded exactly.
The control passes for a cell if at least 10 of 12 plants reach recovery >= 0.70.

## 4. Null

30 real ciphertext page pairs chosen by a fixed seed from the other 1,484 offset-0 pairs with both
pages >= 200 runes (truncated to the shorter page), plus the real pair at offsets +-1..+-5 (10 more).
Each null is decoded with its own real word boundaries. `S_null_max` = the largest of the 40.

## 5. Threshold, fixed in advance

Per cell, with `S_plant_min` the smallest S over the 12 plants:

- **FLAGGED-FOR-ORACLE** if `S_real >= (S_null_max + S_plant_min) / 2` and the control passed. A flag
  is not a solve: the two decoded pages go to a human read per `HUMAN-ORACLE.md`.
- **NEGATIVE for that cell** if the control passed and `S_real <= S_null_max`.
- **INCONCLUSIVE** otherwise (control failed, or S_real between the null max and the midpoint).

Three cells are tested, so a single flag is read at a family of three.

## 6. The Aiming Test

- **Q1 (recognizer):** the plants above are the actual hypothesised shape (two English texts in depth
  with rewrite noise), decoded by the same code path as the real pair.
- **Q2 (prior):** the measured anomaly in section 0 (`../A0-fresh-eyes-audit/depth_pairs.py`), plus the
  word-length evidence that the plaintext is letter-wise English (`../A0-fresh-eyes-audit/wordlen.py`).
- **Q3 (bounded):** yes. One page pair, three cells, no key space at all.
- **Q4 (three conditionals):** (1) key space: none, the test is key-free; it assumes the same key at
  the same page offsets with no key-consuming skips on these two pages. (2) transition model: additive
  combination, at most a few percent of positions corrupted. (3) register: English only, in the three
  encodings named; any other numbering or language is NOT covered by a negative here.
- **Q5 (kill):** if the control fails in a cell (fewer than 10 of 12 plants at >= 0.70), that cell is
  reported INCONCLUSIVE and its real-pair number carries no weight.
