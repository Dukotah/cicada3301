# O4 RESULTS - clue-coverage closure audit (2026-10-30)

Audit only; nothing was decoded. Recognizer (PREREG.md): a clue x reading-family cell with no ledger/findings row or only an English-only / legacy / no-control row.

## Counts
- Clue entries (clues.json): 154 = 37 signed out-of-book messages (the 2016 message additionally split into 7 clause entries) + 94 LP1 solved sentences (community 0.x tree, vendored) + AN END hash + 15 structural clues (the 154 includes the 7 clause entries); 132 are mapped to 34 matrix rows, 22 are logistics/routing (onion pointers, denials) and excluded.
- Readings (readings.json): 49 reading records, each with ledger id (or "NONE"), decoder, adjudicator, three conditionals, verdict, not_covered, file:line.
- Matrix: 34 rows x 11 families = 374 cells, 140 applicable. NEVER 68; TRIED-ENGLISH-ONLY 24; TRIED-LEGACY-BEAM 29; PARTIAL 3; TRIED 16 (instrument-independent or current-instrument). English-only + legacy = 53 cells.
- 38 of the 68 NEVER cells are F1/F5 on clues with no stated operation (see matrix.md); the ranked list uses the rest.

## Top 8 (details and PREREG seeds in untried.md)
1 U1 2016 sentences and remaining LP1 imperatives as seeds/keys (absent from round26/C seeds.json and round13/B04 SLOGANS); 2 U2 LP1 numbers (word/line/sentence sums) as key schedule/offsets; 3 U3 map->road->direction as a composed word-boundary-keyed decoder; 4 U4 prime-line-sum as a language-agnostic recognizer clause; 5 U6 re-adjudicate R11 + R22-C under beam_v3/pf_v4/12 reg; 6 U8 direction geometry beyond R22-B; 7 U5 R10 L2/L3 streams in 12 registers; 8 U7 signed numbers as book-code indices.

## What the owner's theory does and does not survive
Supported (measured):
- Not every clue-reading is covered under the repaired instrument: 53 applicable cells are English-only or legacy-beam (R11, R10 L2/L3, R9, R10b B1, R13/R16, R22-C, R26-C), and the R10/R9/campaign7 rows are not in LEDGER.json at all (F-02 says they were never run; it is stale).
- Combinations were never run: no row composes map/road/direction; no row uses the LP1 plaintext's NUMBERS as a schedule (R26-C used 16 sums only as PRNG seeds; R22-C X3 used letters); the 2016 clauses were never seeds.
- The unsolved pages' own structure (word counts, line counts) was used only as a message (R10 M6) or a reset test (LP2-H1/H2), not as a key schedule for decoding.
- The author demonstrably built numeric structure into LP1 (9/9 prime line sums on A WARNING, magic squares, 761, product tag): a language-agnostic recognizer built from it (U4) has not been used.
Not supported / refuted by default:
- "The 2014 clue": the sentence is in the 2016-01 signed message (VALID, SIGNATURES.json); 2014 messages say "Let the text guide you", "Your enlightenment awaits you".
- "Information nobody noticed": every sentence in the signed corpus and LP1 has at least been considered by some round; the gap is in how readings were applied and adjudicated (English-only, legacy beam), not in unnoticed text. The clauses are also a quotation of LP1's own vocabulary (A WARNING: "the words or their numbers"; R10 L2 P0), so the "devotional restatement, not instruction" null remains live.
- Keystream continuity across page joins (ELIMINATION-LEDGER.md:551-569) and the soft anti-repeat filter damp every reading that needs a per-page or per-word key reset; U3 must carry a plant that includes the filter.
- No community source supplied a consensus reading to test (fandom wiki fetch blocked); community lore gives no prior.
Everything above is a bound on what has and has not been run, not a verdict on any reading.

## Decisions for the coordinator
1. Add ledger rows for Round 9 DIRECTION, Round 10 L2-map, L3-road and campaign7 wordsum/hill5 (status measured, English-only conditionals), and update F-02 (stale, "no lane" claim false).
2. Choose whether U1/U2/U3 run as one R37 lane (shared generator and gate, ~10k decodes total, minutes on beam_v3) or three.
3. U4 requires a decision to add a prime-sum clause to hitfn20; it is language-free but only partly supported by LP1 (A WARNING 9/9, WELCOME 3/5).
4. Applicability judgments (build_matrix.py ROWS) are mine; the NEVER count moves with them.
Files: clues.json, readings.json, matrix.md, untried.md, counts.json, ledger.json, PREREG.md, build_data.py, build_matrix.py.

## Correction (Round 36 X1, applied by the coordinator 2026-10-30)

Cells H7×F2 and H12×F2 (the P.S. digit string and `@1231507051321` as numeric keys) were marked NEVER but were run
as numeric keys in R10b B1 (`b1_keys.py:138`) and skip-aware in campaign18 `numeric2_skip.py:170-205` — both
English-only / legacy-beam, so they belong in TRIED-ENGLISH-ONLY / TRIED-LEGACY-BEAM. Corrected counts: NEVER 66
(was 68); English-only/legacy cells 55 (was 53). The top-8 list is unaffected (neither cell was in it).
