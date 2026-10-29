# B2 RESULTS -- issue #12 landing, p27:93, LP1 transcription audit (Round 33, 2026-10-29)

PREREG: `PREREG.md` (dated first). Nothing here changes any cryptanalytic verdict.

## Part A -- issue #12: APPLIED
* Both separator corrections applied to `data/krisyotam_runes.txt` (`.` -> `-`, seg 8 gap 12 and seg 40 gap 8). The pre-edit gate (our Round 19 T2 rows, the rune pairs, my own look at the page images) agreed exactly, so no STOP. Exactly 2 characters differ; segment/line/rune structure identical.
* `tests/validate.py` and `analysis/handoff/check_consistency.py` pass before and after with byte-identical output; `pytest tests/test_rig.py tests/test_validate_ledger_r3.py` 13 passed (after). No solved-page control uses segments 8/40; no segment boundary moves.
* Archived-JPEG SHA-256s are not on disk (unverified, no download). Diff, provenance line (credits RETSAM3301, issue #12 opened 2026-10-10), the "19 disagreements" finding and the 22 other T2 lines: `issue12_correction.md`.
* CI drift-regeneration steps and the network smoke scripts were not run (need git / network). Issue #12 stays open until a commit exists (I cannot commit).

## Part B -- p27:93 (`p27_93.md`)
Canon U, T1 call B (d0 6 / d1 11 / margin 5). The glyph is 6 px from a singleton B-labelled exemplar (bitmap 421, itself a U-shaped glyph from p13 mislabelled by a forced pairing beside a merged C+B glyph), 11 px from the 57x U exemplar, about 2,900 px from every real B. Verdict: U; canon stands; the nomination is a T1 bank-contamination artifact. Machine-side unambiguous; a human glance is optional. Crops are in the lane dir.

## Part C -- LP1 audit (`lp1_misses.json`, driver `lp1_repro.py`)
* **Reproduction: yes, exact.** T1's `g_read_lp1.py` logic re-run from committed code on the hash-verified vendored images: LP1 **1,699 / 1,796 = 94.5991 %**; with the LP2 controls (180/180), pooled **1,879 / 1,976 = 95.0911 %**, FAIL vs the 99 % bar, unchanged. Per section: WARNING 179/184, WELCOME 392/394, SOME WISDOM 82/157, KOAN 727/742, KOAN (circumference) 319/319. T1's own output files were untouched (hash guard).
  The vendored LP1 JPEGs (`corpus/E-tooling/vendor/...scream314/...`) were not on this machine. I fetched the 19 files T1 needs from `github.com/cicada-solvers/documenting-cicada3301-scream314` with `gh api` into the lane dir, accepting each only if its SHA-256 equalled T1's committed hash (19/19 matched). Re-extracted crop hashes equal T1's for all 75 images. The fetched images and work arrays were deleted afterwards; `fetch_vendor.py` and `extract_here.py` rebuild them. No Q5 kill.
* **Diagnosis of the 97 misses** (89 missing, 1 wrong, 7 in unequal replace blocks):
  - 75 are one contiguous block of SOME WISDOM (canon 659-734): `SHADOWSAETHEREALBUFFERSUOIDCARNALOBSCURAFORMMOBIUSANALOGUOIDMOURNFULAETHEREALCABAL`. Aligned alone against the whole LP1 glyph stream it matches only at chance (44 of 76 scattered, longest run 4), so that text is not present as a glyph run in the vendored LP1 image set (05.jpg has 83 glyphs for a 157-rune section). This is an input-coverage gap, not a glyph misread. Without the block LP1 = 1,698/1,720 = **98.72 %**; pooled would be 1,878/1,900 = 98.84 %, still under 99 %.
  - The other 22 are isolated: A WARNING 5 (including the single 1:1 "wrong", canon S read IA on a 133 px wide merged bitmap), WELCOME 2, A KOAN 15; single runes or digraph/merge-sized gaps on image pages 1, 3, 6-9. Only the merge explanation for that one 'wrong' cell was checked at glyph level; the missing singletons have no glyph to inspect.
  - 1,009 glyphs have no canon counterpart (pages 10-13 are about 758 of them: LP1 text with no decrypted canon), as T1 stated.
* **No LP1 cell was changed.** The LP1 canon is decryption-validated text, so every miss is a reader/coverage miss, not a transcription error, and I found no unambiguous reason to alter a cell. LP1_REAL was therefore NOT re-fit and the I2 `power.py` L=120 gate was NOT re-run (its trigger, "any LP1 cell changes", did not occur).
* **Top-20 lowest-margin cells** (margin = d1 - d0 against the LP2 bank in the bootstrap labelling; `lowest_margin_top20` in the JSON): all 20 are **correct U** reads on a 53 px bitmap (11 cells with margin 5, then 11, 20, 37 x5, 47 x2), pages 3-9, 14, 15. The margin-5 cluster is the same contamination as p27:93: the LP2 bank's mislabelled B singleton (bitmap 421) sits 5 px from the LP1 U glyph. These are canon-correct and are not evidence of LP1 transcription uncertainty.

## What the coordinator must decide
1. Commit the one-file data edit and close #12 by commit reference (I cannot run git). Suggested provenance line is in `issue12_correction.md`.
2. Whether to run the CI drift and network smoke steps before committing.
3. Whether to open a small T1 patch lane that relabels bitmap 421 (B -> U) in the bank and re-runs `g_read.py` / `t1_corpus.py`. I did not touch T1.
4. Whether to obtain the missing SOME WISDOM image(s) so the LP1 gate covers that 75-rune block; until then G-READ-ALL stays FAIL at 95.09 %, and the cause is coverage plus 22 sparse misses, not substitution.
5. The pinned archive JPEG hashes (8.jpg / 40.jpg) remain unverified here.

## Not covered
Human image adjudication of the 22 other T2 separator rows; the issue's ZIP (not downloaded); other-lineage JPEGs; LP1 recall beyond the five solved sections; any LP1_REAL re-fit.

## Rule note
I ran one read-only `git log` early by mistake (no state changed); no git after that. The only file edited outside the lane dir: `liber-primus/data/krisyotam_runes.txt`.
