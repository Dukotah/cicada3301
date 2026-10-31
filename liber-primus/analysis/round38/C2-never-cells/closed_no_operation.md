# Round 38 / C2 - NEVER cells with no operation stated, and the C1-R38 hand-off

Source: `analysis/round37/X1-redteam/o4_recount.json` (`NEVER_cells_after`, 60 cells). Wording is "no operation stated": no lane can be written from the clue text because the text names no transformation of the cipher stream (or the transformation it names is already a different matrix cell). The condition that reopens any of them is a stated operation, e.g. a concrete mapping from the clue's nouns to a stream operation. Nothing below says the clue is meaningless.

Counts: 60 = 19 semantic F5 -> **C1-R38** + 7 cells RUN in this lane (`cells/`) + 34 **no operation stated**.

## C1-R38 (semantic reading; marked, not closed here) - 19 cells
H1xF5, H2xF5, H3xF5, H4xF5, H5xF5, H8xF5, H9xF5, H10xF5, L1xF5, L2xF5, L4xF5, L5xF5, L7xF5, L8xF5, L9xF5, L10xF5, L11xF5, L14xF5, L18xF5.

## Cells RUN here (reclassify NEVER -> TRIED in `ledger_patches.json`) - 7 cells
H5xF1 (`cells/H5xF1`), H6xF2 (`cells/H6xF2`), L8xF6 (`cells/L8xF6`), L15xF6 and L15xF7 (`cells/L15xF6F7`), L17xF7 (`cells/L17xF7`), L4xF3 (`cells/L4xF3`).

## No operation stated - 34 cells (one line each)
| cell | clue (O4 row) | why no lane can be written |
|---|---|---|
| H1xF1 | 2016: "Liber Primus is the way" | an identity statement; no verb applied to the stream |
| H1xF7 | same | "the way" through the book names no join rule between pages/documents |
| H1xF8 | same | "the way" = path: no geometry (grid, order, turtle rule) is given |
| H5xF10 | 2016: "The path lies empty; epiphany seeks the devoted" | an acrostic/stego needs a named carrier and extraction rule; none stated (H5xF1 empty-path identity key IS run) |
| H6xF1 | 2016: "Seek and you will be found / Verify OpenPGP 7A35090F" | "verify" is a signature check on the artifacts, already carried in `clues.json` (signature = VALID); "seek" names no operation on LP2 (the two clauses as keys are run in `gaps/` G1) |
| H8xF1 | 2012: "The key has always been right in front of your eyes" | O4 deliberately unranked: "in front of your eyes" does not say which visible object (drop-cap, title, the cipher itself) is a key or how it is applied; measured keystream continuity across page joins damps per-page-object keys |
| H9xF1 | 2013: "You already have everything you need to continue" | a hint that nothing external is needed; no operation |
| H9xF8 | 2013: "knock on the sky and listen to the sound" | metaphor; no sound/knock/geometry rule |
| H9xF10 | same | no carrier or extraction rule |
| H10xF1 | 2014: "Let the text guide you / produce from within" | "the text guide you" is not an executable rule (running-key use of LP text is the R22-C X3 / U2 cells) |
| H11xF7 | 2014 ciphertexts (IDGTK..., fallen-behind pairs, rune-table morse) | the cross-document join between 2014 ciphertexts and LP2 is not stated anywhere |
| L1xF1 | LP1 A WARNING: "believe nothing... test the knowledge, find your truth" | an epistemic instruction; no stream operation |
| L2xF1 | "either the words or their numbers, for all is sacred" | an either/or over the words channel (F3/F4 cells) and numbers channel (F2 cells), both already tried; it adds no third operation |
| L3xF1 | "do not edit or change this book or the message within" | a prohibition (do not alter); no transformation |
| L3xF10 | same | no carrier or extraction rule |
| L3xF11 | same | no AN-END structure rule |
| L4xF1 | "the primes / the totient function are sacred" | the operation reading is F2 (primes/totient as keystream: TRIED); F1 literal adds nothing |
| L5xF1 | "all things should be encrypted" | layering an outer uniform pad over inner layers is not identifiable in principle (O4 note) |
| L5xF2 | same | no number channel stated |
| L7xF1 | "command your own self" | an instruction to the reader; no stream operation |
| L9xF1 | "program your mind / program reality" | metaphor; no operation |
| L10xF1 | "question all things; discover truth inside yourself" | metaphor; no operation |
| L11xF1 | WELCOME: "journey deep within and you will arrive outside; like the instar, go within to emerge" | "within -> outside" suggests inversion/reversal; forward/reverse reads are already in R10 L2/L3 and C3 U5; no further rule stated |
| L12xF7 | KOAN: master and student | a narrative; no cross-page rule |
| L13xF7 | KOAN: "the I is the voice of the circumference" | "circumference" is never formalised (page frame? alphabet cycle?); no join rule |
| L13xF8 | same | the same unformalised noun; no geometry rule |
| L15xF3 | "KNOW THIS: the three magic squares (numbers + words)" | the page-5 square's words are gematria-valued so the square completes; that is a solved puzzle, not a key rule (the held 5x5 numbers as a key IS run under F6/F7) |
| L16xF11 | gematria-sum structure: prime line sums, 761, PARABLE product | a property of LP1 plaintext lines (measured in C2-R37 U4); no AN-END operation stated |
| L17xF3 | AN END: "a page hashes to H; seek it out" | gematria/arithmetic on words is not what the clue asks; the stated operation (hash a page) is run under F7 |
| L18xF1 | PARABLE: "we must shed our own circumferences" | "circumference" unformalised; any 'shed' rule (drop first/last rune of each word/line/page) would be an invention, not a reading |
| L18xF10 | same | no carrier or extraction rule |
| S1xF7 | solved-page ladder + thematic page keys | the ladder's NEXT rung is N5/N5-class generators (run, `n5n4/`); a cross-page join rule is not stated |
| S3xF7 | pp49-51 base-60 256-byte payload | payload family tried as F2/F6 (R41); no join to LP2 pages is stated |
| S4xF10 | ornament bands / drop-caps / render geometry | "47 unread ornament bands" is a finite object, but no stego carrier or extraction rule is stated; I1-R38 recognizer lane covers the geometry side |

Total: 34 rows.
