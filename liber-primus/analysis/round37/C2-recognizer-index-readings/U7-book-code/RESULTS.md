# RESULTS - R37 C2-U7 book-code indices (signed numeric strings as indices)

PREREG.md (+Addendum 1) written first. Panel-R36, statistic pmax_ne, two nulls (random-index over the scheme alphabet; order-shuffle), M=2000 each, refine 100k/20k if p<=0.005. Family bar 0.01/320 = 3.1e-5. Runtime 31 s.

## Planted controls (before the sweep)
| control | n runes | real pmax_ne | p_a (order) | p_b (index null) | null max | verdict |
|---|---|---|---|---|---|---|
| A: 60-rune LP1 phrase via 3-digit list into LP1 runes | 60 | 18.27 | 0.0004998 | 0.0004998 | 10.29 | PASS |
| A0: random 3-digit list, same scheme | 60 | 5.15 | 0.5957 | 0.6957 | 9.13 | ok (not detected) |
| B: LP1 sentence "THE PRIMES ARE SACRED..." via word indices (W readout) | 42 | 14.53 | 0.06547 | 0.02799 | 16.64 | FAIL |
| B0: random word indices | 39 | 10.26 | 0.5187 | 0.8386 | 16.40 | ok (not detected) |
| C: 60-rune phrase via first-rune-of-UNS-word indices | 56 | 18.63 | 0.0004998 | 0.0004998 | 3.90 | PASS |
| C0: random indices | 60 | 1.20 | 0.3213 | 0.4578 | 3.54 | ok (not detected) |

Controls A and C (R / F readouts) PASS at the p floor (5e-4 at M=2000); random-index controls are not detected. **Control B FAILS** (p 0.065 / 0.022): a whole-LP1-word readout is not separable from random LP1 words under the panel, because the panel's LP1_REAL register already contains LP1's words, so any bag of LP1 words scores high (null max 16.6 vs real 14.5). The word-W readout (80 cells) is therefore UNPOWERED for LP1 and untested for UNS; those cells are inconclusive, not negative. R/F cells (240) are powered at n>=~40 (controls at n=56-60).

## Scheme table (best p_gate = max(p_a,p_b); bar = 0.01/N_group; family bar 3.1e-5)
| target | digit scheme | readouts | N | best p_gate | real pmax_ne (null max) at best | n at best | cells with n<30 (unpowered) | bar 0.01/N |
|---|---|---|---|---|---|---|---|---|
| LP1 | pair | R,F-word,F-line | 36 | 0.0815 | 4.95 (7.32) | 65 | 12 | 0.00028 |
| LP1 | pair | W (UNPOWERED) | 12 | 0.361 | 32.85 (37.02) | 242 | 4 | 0.00083 |
| LP1 | triple | R,F-word,F-line | 36 | 0.028 | 5.22 (6.26) | 40 | 12 | 0.00028 |
| LP1 | triple | W (UNPOWERED) | 12 | 0.254 | 26.03 (30.15) | 164 | 4 | 0.00083 |
| LP1 | single | R,F-word,F-line | 36 | 0.0625 | 7.59 (9.32) | 131 | 12 | 0.00028 |
| LP1 | single | W (UNPOWERED) | 12 | 0.079 | 46.31 (47.14) | 618 | 0 | 0.00083 |
| LP1 | whole | R,F-word,F-line | 12 | 0.122 | 5.88 (8.84) | 10 | 12 | 0.00083 |
| LP1 | whole | W (UNPOWERED) | 4 | 0.373 | 12.95 (17.06) | 51 | 0 | 0.0025 |
| UNS | pair | R,F-word,F-line | 36 | 0.159 | 1.91 (3.74) | 60 | 12 | 0.00028 |
| UNS | pair | W (UNPOWERED) | 12 | 0.461 | 1.45 (3.35) | 280 | 2 | 0.00083 |
| UNS | triple | R,F-word,F-line | 36 | 0.038 | 13.66 (17.08) | 4 | 12 | 0.00028 |
| UNS | triple | W (UNPOWERED) | 12 | 0.0565 | 3.62 (3.82) | 200 | 4 | 0.00083 |
| UNS | single | R,F-word,F-line | 36 | 0.0275 | 6.40 (7.46) | 13 | 12 | 0.00028 |
| UNS | single | W (UNPOWERED) | 12 | 0.219 | 5.38 (7.58) | 623 | 0 | 0.00083 |
| UNS | whole | R,F-word,F-line | 12 | 0.181 | 3.50 (9.01) | 10 | 12 | 0.00083 |
| UNS | whole | W (UNPOWERED) | 4 | 0.399 | 1.73 (4.50) | 39 | 0 | 0.0025 |

Selections swept: 320. Selections refined (p_gate <= 5e-3): 0. **Flagged (p <= 3.1e-05): 0.** Smallest p_gate overall: 0.0275 (consistent with noise over 320 cells).

Lowest five p_gate cells (all noise level, none readable):

- S2 single UNS line-F base1 rev0 n=13 p=0.0275: `SOPSAECECAESPOS`
- LOC triple LP1 word-F base0 rev1 n=40 p=0.028: `SEMSAWAAWACOWDTHOIWWIBTHWAOWHICTCATBMEASDTY`
- S2 single UNS line-F base1 rev1 n=13 p=0.031: `SOPSAECECAESPOS`
- S2 triple UNS R base1 rev0 n=4 p=0.038: `THGOD`
- S2 triple UNS R base1 rev1 n=4 p=0.0415: `THGOD`

## Verdict
NEGATIVE for the 240 R / F-word / F-line selections (144 of them with n>=30 runes and genuinely powered; 96 are S2 or whole-number short selections, unpowered): no signed numeric string (P.S. integer, `@1231507051321`, location numbers) retrieves, under any enumerated pair/triple/single/whole x 0/1-based x forward/reversed index scheme into LP1 plaintext or the LP2 rune stream, a letter string the 12-register panel separates from either null. 80 W-readout cells INCONCLUSIVE (control B failed). No oracle bundle: nothing cleared the family-wise bar.

## Three conditionals
1. **Rule space:** exactly the 320 enumerated selections (mod-wrap indexing, non-overlapping digit groups). Not covered: page:line:char addressing, the reverse direction into Mabinogion/KJV/other books, overlapping/sliding digit windows, other radices, per-block short strings, the colon-list book-code messages.
2. **Decoder:** verbatim retrieval with mod wrap; a different edition/transliteration of LP1 (here: koans file, greedy digraph parse, K->C V->U) or a skip/offset convention is missed.
3. **Adjudicator:** panel-R36 pmax_ne trigram z; powered only for n>=~40 runes (A: 60, C: 56). S2 (@1231507051321) gives n=4-13 under pair/triple/single and the 10 whole-number block selections n=10: essentially unpowered. Word-whole readouts unpowered (control B).

## not_covered
page:line:char; reverse-direction books; W readout power; S2 / whole-number short selections; n-th-letter-of-word schemes.

## Files
PREREG.md, u7.py, finalize.py, results.json (all 320 rows + controls), run.log, ledger.json, RESULTS.md
