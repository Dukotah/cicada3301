# PAGE-MAP — the page-numbering Rosetta Stone

_Mechanically verified by exact rune-stream matching (`analysis/campaign7/build_pagemap.py`). Three schemes name the same physical pages: **scream314** original jpg numbers, **relikd** 0-indexed images, and **krisyotam** `%`-split segment indices (what `load_pages()` returns — what all our per-page scores refer to). Always say which scheme you mean._

| scream314 jpg | relikd img | runes | krisyotam idx |
|---|---|---|---|
| Runes | 01.jpg | 184 | NOT IN KRIS (non-runic/LP1) |
| 03.jpg | (LP1 / unnumbered) | 395 | NOT IN KRIS (non-runic/LP1) |
| 04.jpg | (LP1 / unnumbered) | 122 | NOT IN KRIS (non-runic/LP1) |
| 05.jpg | (LP1 / unnumbered) | 157 | NOT IN KRIS (non-runic/LP1) |
| 06.jpg | (LP1 / unnumbered) | 742 | NOT IN KRIS (non-runic/LP1) |
| 09.jpg | (LP1 / unnumbered) | 38 | NOT IN KRIS (non-runic/LP1) |
| 10.jpg | index.1.jpg | 629 | NOT IN KRIS (non-runic/LP1) |
| 13.jpg | index.4.jpg | 125 | NOT IN KRIS (non-runic/LP1) |
| 14.jpg | 107.jpg | 320 | NOT IN KRIS (non-runic/LP1) |
| 16.jpg | 229.jpg | 89 | NOT IN KRIS (non-runic/LP1) |
| 17.jpg-19.jpg | 0.jpg-2.jpg | 729 | 0–2 |
| 20.jpg | 3.jpg-5.jpg | 812 | 3–6 |
| 23.jpg, 24.jpg | 6.jpg-7.jpg | 333 | 6–7 |
| 25.jpg, 26.jpg, 27.jpg, 28.jpg, 29.jpg, 30.jpg, 31.jpg | 8.jpg-14.jpg | 1729 | 8–14 |
| 32.jpg | 15.jpg | 9 | 15 |
| 32.jpg, 33.jpg, 34.jpg, 35.jpg, 36.jpg, 37.jpg, 38.jpg, 39.jpg | 15.jpg-22.jpg | 1894 | 15–22 |
| 40.jpg, 41.jpg, 42.jpg, 43.jpg | 23.jpg-26.jpg | 1021 | NOT IN KRIS (non-runic/LP1) |
| 44.jpg, 45.jpg, 46.jpg, 47.jpg, 48.jpg, 49.jpg | 27.jpg-32.jpg | 1433 | 27–32 |
| 50.jpg | 33.jpg | 91 | 33 |
| 50.jpg, 51.jpg, 52.jpg, 53.jpg, 54.jpg, 55.jpg, 56.jpg | 33.jpg-39.jpg | 1468 | 33–39 |
| 56.jpg | 39.jpg | 121 | 39 |
| 57.jpg | 40.jpg | 3008 | 40–52 |
| 71.jpg | 54.jpg | 308 | 53–54 |
| 73.jpg | 56.jpg | 86 | NOT IN KRIS (non-runic/LP1) |
| 74.jpg | 57.jpg | 95 | NOT IN KRIS (non-runic/LP1) |

**Key facts:** relikd images 49/50/51 are the base-60 token tables (non-runic, absent from the krisyotam rune corpus). krisyotam indices therefore do NOT equal relikd image numbers. Sections marked NOT IN KRIS are LP1/solved/non-runic material.

## Cross-lineage verification findings (byproduct of building this map)

Exact-matching scream314's independent document against krisyotam canon surfaced
three deviations — all now investigated (`analysis/campaign7/build_pagemap.py`):

1. **relikd 23–26 block, offset 385 = page 24 index 172 (A vs AE).** Our mechanical
   alignment **independently rediscovered the exact known discrepancy** that Campaign V
   adjudicated (canon ᚫ/AE correct, confirmed by the glyph classifier at 0.973).
   Strong validation that both this map and the Campaign V verdict are sound.
2. **relikd 57 (the solved PARABLE page), position 80 (E vs Y).** Adjudicated against
   ground truth: the direct-transliteration plaintext reads "...DIVINITY..." and
   position 80 is the **Y of DIVINITY**. Canon correct; scream314's E is a typo.
3. **relikd 56 (UNSOLVED, kris idx 55), a leading extra ᚠ (F).** scream314's stream has
   86 runes vs canon's 85; the difference is a single **leading F rune**, after which the
   streams are identical. All three rune-identical lineages (krisyotam/relikd/rtkd) lack
   it and scream is 0-for-2 in the adjudicated diffs — so canon is very likely right.
   **But**: ᚠ is the *interrupter* rune, and this page may lie outside the Campaign-V
   classifier's verified range (pages 0–54). **Open micro-question for anyone with the
   page image: does relikd image 56 begin with an ᚠ?** (Impact if real: shifts
   non-interrupter keystream alignment by one on this page; interrupter-aware attacks
   are unaffected since a leading ᚠ is skipped.)

## Image adjudications (2026-07-10) — vision on targeted regions

Fetched the original page images (scream314 assets = onion7-lineage) and read the
disputed regions directly. Results:

1. **The AN END leading-ᚠ question is CLOSED — scream314 was right.** The page
   (scream 73.jpg) physically begins with a **giant red illuminated ᚠ** (drop-cap,
   manuscript style). The canonical lineage (krisyotam/relikd/rtkd) omits it; the
   omission is *editorial* and benign for the solve (ᚠ is the interrupter rune —
   skipped by the keystream — and the φ(p)−1 solve reproduces cleanly either way).
   scream314 transcribes the page faithfully. Since scream matches canon exactly on
   every unsolved page (this map's exact-match result), **no unsolved page hides an
   omitted initial** — keystream alignments in all prior attacks stand.
2. **First independent verification of the token-page transcriptions.** Re-read
   relikd 49 & 50 (scream 66/67.jpg) from the images: **glyph-for-glyph match** with
   scream's published tokens (13×8=104 on p50; 10×8=80 on p49). The "wrong!!!" flag
   on p50 reflects the font's inherent ambiguity classes **{I,l}** and **{0,O}** —
   visually identical/near-identical glyphs with different base-59/60 values — not a
   transcription failure.
3. **New structural fact:** relikd 49 (scream 66.jpg) carries BOTH the final runic
   paragraph (= canon segment 49: 3 lines, 66 runes, verified word-for-word) ending
   with the **red end-marker block**, AND the first token table directly below it.
   The token data is an *appendix that begins where the runic book explicitly ends.*
   Also: relikd-repo file p55 = canon segment 54 = the cicada-emblem final page —
   the repo's file numbering diverges from scream's relikd column at the tail (the
   repo does not host the AN END/parable images).
4. **Robustness upgrade for the token-pad negatives:** the {I,l}/{0,O} ambiguity
   affects at most ~10 of 256 pad bytes. A correct key/XOR hypothesis would still
   show ~96% signal under that corruption (near-English scores, entropy collapse);
   every test showed pure noise. **The Campaign VII token-pad negatives therefore
   hold across the entire transcription-ambiguity space.**
