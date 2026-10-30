# O4 untried.md - ranked NEVER and English-only/legacy cells

Date 2026-10-30. Source: matrix.md (34 clue rows x 11 families, 140 applicable cells: 68 NEVER, 24 TRIED-ENGLISH-ONLY,
29 TRIED-LEGACY-BEAM, 3 PARTIAL, 16 TRIED). Many NEVER cells in F1/F5 are NEVER because the clue has no operational content
(e.g. "program your mind"); they are in matrix.md but not ranked. Score = (a) literal text support 0-3 + (b) boundedness 0-3
(3 = under ~2k decodes, enumerable) + (c) cheapness under beam_v3 + pf_v4 + 12-register panel-R36 + observed null 0-3.
Priors are NOT from community lore (ARMADA-DOCTRINE R4). Every seed below still owes a full PREREG with a plant-and-recover control.

## Ledger-state findings that shape the list
- F-02 (LEDGER.json) says "words are the map / meaning is the road" were never treated first-class. STALE: Round 10 L2-map (M1-M9) and L3-road (T1-T5)
  did exactly that (analysis/round10/L2-map/PREREG.md:69-130; L3-road/PREREG.md:116-125) and Round 9 DIRECTION did clause 3
  (research/ROUND-9-RESULTS.md:65-124). But Rounds 9/10 have NO LEDGER.json rows (0 hits for L2-map / L3-road), are English-only
  (rune 4-gram on English-in-futhorc / score_norm), are cleartext-layer reads of the CIPHERTEXT, and R9 had no positive control
  (round10/SYNTHESIS.md "Instrument caveats").
- The three clauses were never applied as a composed pipeline, and "numbers" was never applied to the LP1 plaintext/meaning layer as a key schedule
  (R10 L3 sums only the LP2 ciphertext's own words).
- The 2016 clauses (map, road, way, epiphany, seek) are absent from every seed list that fed a generator: round13/B04/seeds.py:71-111 (SLOGANS)
  has "THEIR NUMBERS ARE THE DIRECTION" and "BEWARE FALSE PATHS" only; round26/C/seeds.json contains none of THE MAP / THE ROAD / THE WAY / EPIPHANY /
  SEEK AND (checked by string search). They were fed only as rigid/legacy-beam Vigenere keywords (round10b/B1-overlooked-artifact/b1_keys.py:85-91).
- circumference, page-number-as-key and book-code have zero LEDGER.json hits.

## Ranked list (U3 promoted to 3 for the combination emphasis; otherwise by total)

| rank | id | cell(s) | a | b | c | total | one-line |
|---|---|---|---|---|---|---|---|
| 1 | U1 | H1-H5 x F4 (+L2,L4,L8) | 3 | 3 | 3 | 9 | 2016 and remaining LP1 directive sentences as seeds/keys under the current instrument |
| 2 | U2 | H4,L2,L16 x F5/F7 | 3 | 3 | 3 | 9 | LP1 solved-text NUMBERS (word/line/sentence sums) as key schedule or offsets over LP2 |
| 3 | U3 | H2xH3xH4 x F1/F6 | 3 | 2 | 2 | 7 | map -> road -> direction as a composed word-boundary-keyed decoder |
| 4 | U4 | L16 x F3, L17 F3 | 2 | 3 | 3 | 8 | prime-line-sum as a language-agnostic recognizer clause for any decode |
| 5 | U6 | R11 N1-N5, R22-C (T-EN/T-LEG) | 2 | 3 | 3 | 8 | re-adjudicate number-channel and imperative lenses under beam_v3 + pf_v4 + 12 reg |
| 6 | U8 | H4,S2 x F8/F6 | 3 | 2 | 2 | 7 | "direction" as geometry beyond R22-B: per-page, LP1-number-driven, interrupter-gated |
| 7 | U5 | H2,H3 T-EN cells (R01-R12) | 2 | 2 | 3 | 7 | re-score R10 L2/L3 cleartext streams in the 12-register panel |
| 8 | U7 | H12 x F6/F7/F2 | 2 | 3 | 2 | 7 | signed numeric strings as book-code indices into LP1/LP2 ("Liber Primus is the way") |

### U1 PREREG seed - clue sentences as seeds and keys
Recognizer: hitfn20 three-clause gate (pmax >= panel-R36 observed-null bar at actual N; recovery >= 0.90; held-out >= 0.90) under beam_v3 keyskip1/keyskip2 + pf_v4 head screen, 12 registers.
Prior: LEDGER R26-C swept 323 semantic seeds incl. 31 LP1 phrases yet none of the 2016 sentences, the only signed methodological text (corpus/A-primary-artifacts/pgp/messages/2016-01-liber-primus.asc); this is a measured coverage hole, not lore.
Bound: ~40 strings (the 7 sentence fragments + compositions + LP1 imperatives missing from str seeds such as "KWESTION ALL THINGS", "PROGRAM REALITY") x 7 generators x 2 relations x spelling variants (C/K, V/U) = ~3-6k rows.
Kill: control (plant a sentence-seed key through each generator) recovers < 0.90, or 5k rows all below bar - 1 -> record as bound.

### U2 PREREG seed - LP1 numbers as key schedule
Recognizer: same hitfn20 gate. Prior: "their numbers are the direction" + "meaning is the road" + "either the words or their numbers" (LP1 0.0.0.8). LP1 line sums are designed numbers (A WARNING 9/9 prime, liber-primus/data/scream314_lp.md:122-136).
R26-C used 16 sums only as PRNG seeds; R22-C X3 used solved LETTERS as running key; neither used the value SEQUENCES as additive shifts / start offsets. The community "meaning = translated LP1" (boards thread 54) is a pointer only.
Bound: sequences {per-word, per-line, per-sentence, cumulative} x {prime value, index, phi(p)} x {sign, atbash} x {offset 0, page-start offsets} over 5 solved pages + AN END + PARABLE ~ 1-3k decodes.
Kill: planted sum-sequence key not recovered at 0.90 -> abandon; otherwise 3k decodes all under bar.

### U3 PREREG seed - map -> road -> direction pipeline
Recognizer: hitfn20 + a planted word-keyed control. Prior: the 2016 sentence has ONE subject (words) across all three clauses (round10/L2-map/PREREG.md:17-30) and word boundaries are cleartext and unkeyed.
Pipeline: (map) segment on '-' '.' '&' '$' only (never '/'); (road) per-word value v in {sum prime, sum index, length, phi(sum)}; (direction) v advances, resets or selects the skip count in the skip-aware relation; 6 composition orders.
Nearest prior row: campaign7 wordsum_selfkey (5 variants, English quadgram, legacy; CAMPAIGN-VII-FINDINGS.md:25), no ledger row. Bound: 4 v x 6 orders x 2 signs x 2 atbash x 29 starts ~ 2.8k decodes of 12,956 runes.
Kill: control recovery < 0.90, or best pmax < observed-null bar across all.

### U4 PREREG seed - prime-sum recognizer clause
Recognizer: for a candidate decode, split on cleartext '.' (175-219 sentences depending on parse: round10 M6 n=175, L3 T1b n=219) and lines (594); statistic = count of prime sentence sums vs the observed null over wrong-key decodes (language-free; doctrine R3).
Prior: A WARNING 9/9 line sums prime, SOME WISDOM 4/5, WELCOME 3/5 (scream314_lp.md:122-136, 832-837, 952-958) - mixed, so only partly designed; P(prime)~0.15, so a designed LP2 would show a gross excess.
Bound: scoring only; first on the LP1 solved pages and the stored near-misses (seed 1354603465 etc.), then as a 4th clause. Kill: on LP1 pages it does not separate true from wrong keys at 0.01, or wrong-key false-positive rate > 0.01.

### U5 PREREG seed - R10 L2/L3 streams in 12 registers
Recognizer: stream pmax over 12 registers vs observed null. Prior: round10/L2-map/results.json M1.pooled best z=6.94 (first-of-word/noF atbash/rev/+28; absolute -16.51 vs English-only threshold -13.5) - an English-gated near-flag never re-scored outside English.
Bound: ~10^4 short streams, regenerable by round10/L2-map/mapcommon.py. Kill: panel power at L~2.9k below 0.5 for every non-English register -> record as bound.

### U6 PREREG seed - number-channel and imperative lenses under the repaired instrument
The ledger already marks this cheap (ELIMINATION-LEDGER.md:935-960 REOPEN NOTE; R22-C not_covered). Recognizer: hitfn20 on beam_v3 + pf_v4 + 12 reg. Bound: R11 N1 (48 configs) + N2-N5 + R22-C (185 ops) ~ a few hundred decodes.
Kill: Round 11 plants not recovered at 0.90 under 12 registers.

### U7 PREREG seed - signed numbers as book-code indices
Recognizer: dictionary-word density + 12-reg panel on strings retrieved from LP1 (known plaintext) and LP2 (as ciphertext, then null-adjudicated). Prior: the 2012-14 chain used page:line:char book codes (messages 2012-01-book-code-poem, 2012-01-mabinogion-book-code, 2013-01-opening-book-code, 2014-01-opening-book-code) and the 2016 text names the book as "the way".
Unresolved numeric signed objects: 2012-01-location-numbers (ten 12-digit blocks), 2012-01-end-of-puzzle P.S. 124-digit integer, "@1231507051321". campaign XVII tried LP numbers as pointers INTO known books (the reverse direction).
Bound: ~15 strings x ~8 split schemes x {LP1 words/lines, LP2 page/line} < 2k reads. Kill: dictionary-word rate within the shuffle null over every string.

### U8 PREREG seed - direction geometry beyond R22-B
Recognizer: R22-B shape statistics + QR/grid detectors vs seed-3301 shuffle null, Bonferroni over the new combo count. Prior: "numbers are the direction" read literally; R22-B covered book-concatenated LP2 streams at 6 moduli with unit/value steps only (LEDGER R22-B not_covered).
New inputs: per-page renders, LP1 gematria sequences (known text) as turtle input, interrupter-gated pen-up, the 55-page layout as a grid, L-systems. Bound ~500-2k renders, no decoder. Kill: a control shape through each new input type not legible, or no p below family-wise Bonferroni.

## Cells deliberately NOT ranked
- L5 "all things should be encrypted" x F1 (layering the known ladder under the pad): an outer uniform pad hides inner additive layers - not identifiable in principle.
- H8 "right in front of your eyes" x per-page key from drop-cap/title: damped by the measured keystream continuity across page joins (ELIMINATION-LEDGER.md:551-569; round10/L3-road/PREREG.md:127-134); drop-cap identity as MESSAGE was R22-D (min p 0.18).
- H6 "Beware false paths": warning about forged keys, not a method.
- L1/L9/L11/L14 x F5: no operational reading stated; unfalsifiable as stated (round10/L3-road/PREREG.md:143-150 records this class).
- H11 ciphertexts "IDGTK UMLOO..." and the unsigned "TL BE IE OV..." (fallen behind): on my read the second is a transposition of the A WARNING opening (B-E-L-I-E-V-E recoverable from the pair letters) - flagged, unverified, not an LP2 lead.
- 2016 message whitespace ("No silly Spaces this time", boards thread 6): analysis/armada_osint/ws_audit.py and LEDGER H-02 (partially-run) cover whitespace at artifact level; no row isolates the 2016 message. One file, low prior.

## Community-sourced readings and whether this repo tested them (lore is not a prior)
| source | reading | repo coverage |
|---|---|---|
| boards thread 54, corpus/C-community/forums/boards_net_live/thread_54_liber-primus-warning-speculations-properties.html (https://cicada3301.boards.net/thread/54) | "meaning" = the translated LP1 part; investigate LP1 | PARTIAL: R10 L2-M4/M8 (LP1 words as target), R22-C X3 (LP1 letters as running key); LP1 NUMBERS as schedule = U2, NEVER |
| boards thread 56 "Symmetry Theory", same dir, thread_56_symmetry-theory.html | solve with known keys in reverse order and LP text reversed | PARTIAL: R22-C X3 whole-stream reversal (legacy); reversed ORDER of known page keys across pages not run |
| boards thread 6 "Clue 2016 No silly Spaces this time", same dir | whitespace/spacing of the 2016 message | PARTIAL: ws_audit.py, H-02 |
| https://github.com/r4nd0mD3v3l0p3r/LiberPrimusSolver (cited in campaign7 HINT-DERIVED-METHODS H6) | the three book matrices as Hill keys | TRIED-ENGLISH-ONLY: campaign7 hill5_magic (R15) |
| WebSearch x2, 2026-10-30; uncovering-cicada.fandom.com returned HTTP 402 to WebFetch | no source gave an authoritative reading of "words/meaning/numbers"; they restate the text, call the 2016 image channel disputed (https://github.com/krisyotam/cicada3301, https://boxentriq.com/guides/cicada-3301-liber-primus), one calls the book more doctrine than cipher (https://nahgcorp.substack.com/p/part-3-the-internets-most-beautiful) | no community consensus exists to test; R10 L2/L3 are our own parse of the sentence |
