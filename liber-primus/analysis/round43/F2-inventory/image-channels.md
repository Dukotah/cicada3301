# Round 43 — Lane F2a: physical-channel inventory (image side)

Date: 2026-11-03. Independent census — compiled WITHOUT consulting ELIMINATION-LEDGER.md
or prior analysis/*.md findings docs (firewall will diff).

## Method

Sampled 20 page images from `data/relikd/`: p0, p1, p2, p3, p5, p8, p9, p14, p15, p16,
p20, p23, p27, p33, p36, p40, p42, p44, p46, p49, p50, p51, p52, p53, p54, p55,
0_wisdom.jpg, plus crops redfull.png/redgrid.png and F04.png. Enumerated every visible
mark class. Then audited the solver input path:

- `attack.py` → `run_stats.load_pages()` → reads `data/krisyotam_runes.txt`, splits on
  `%`, then `gematria.runes_to_indices()` which keeps ONLY chars in `RUNE_TO_IDX`
  ("ignoring non-runes", gematria.py:73-75). **Everything that is not one of the 29 rune
  codepoints is silently discarded at load time.**
- `tests/validate.py` → `lp.corpus.parse()` → reads `data/scream314_lp.md` (runes +
  `•` word seps), then also reduces to `runes_to_indices` before any cipher work.

Character census of `data/krisyotam_runes.txt` (every non-rune char in the file):
`-` (word sep), `.` (sentence mark), `/` (line break), `%` ×56 (page break), `&` ×18,
`$` ×9, `§` ×1, digits `1 2 3 4 5` (numbered-koan line labels, lines 458-480), one
inline `7` (line 137). **No quote marks, no multi-digit numbers, no color markup.**

## Control (census-method sanity check)

- **pp49–51 tables**: p49/p50/p51 images show 8-wide × 9–10-row grids of alphanumeric
  pairs (`3N 3p 2l 36 …`) — the known 2048-bit payload. Detected from the images alone.
  Grep confirms zero multi-digit/letter-pair content in krisyotam_runes.txt → the rig's
  rune stream cannot see it. Control PASSES (reproduces the known loader blind spot).
- **Red rune pages**: p0 line 1, p3/p8/p15/p23/p27/p33/p36/p40/p54 title words +
  drop caps, p53 final 3 lines fully red, 0_wisdom red words — all detected from images.
  krisyotam_runes.txt has no color channel at all. Control PASSES.

## Channel table

Representation status is w.r.t. what the solver actually consumes
(`runes_to_indices(krisyotam_runes.txt)` split on `%`).

| # | Mark class | Where seen (sample) | In transcript file? | Survives loader? | Could carry data? |
|---|---|---|---|---|---|
| 1 | Black runes (29 futhorc glyphs) | every text page | yes | **YES** (the only thing that does) | the main channel |
| 2 | Red vs black rune color | p0, p3, p8, p15, p23, p27, p33, p36, p40, p53 (3 full lines), p54, 0_wisdom, redfull.png | no (no markup) | no | **HIGH** — red spans are a parallel sub-stream (historically red = functional text); p53's 3 red closing lines are a selectable subsequence the rig cannot select |
| 3 | Oversized drop-cap runes (red) | p0 ᛁ, p3 ᛚ+ᛒ, p8 ᛉ, p15 ᛚ, p23 ᚢ, p27 ᛗ, p33 ᛗ+ᛟ, p40 ᚠ, p54 ᚠ | rune char yes; size attribute no | char only | MEDIUM — the drop-cap positions/identities form a short sequence (acrostic channel) invisible as a *class* to the solver |
| 4 | Word separator `·` (interpunct) | all text pages | yes, as `-` | **NO** (stripped) | MEDIUM — word lengths are a classic null-cipher carrier; loader erases all word boundaries |
| 5 | Sentence/clause mark `⁘` / `:` multi-dot | p2, p16, p20, p36, p42 etc. | yes, as `.` | NO | LOW-MED — sentence segmentation lost |
| 6 | Line breaks | every page | yes, as `/` | NO | MEDIUM — line lengths / first-rune-of-line channels erased |
| 7 | Page breaks | — | yes, `%` ×56 | YES (page grouping) | kept |
| 8 | Paragraph/section glyph `&` ×18, `$` ×9, `§` ×1 | (transcriber's structural marks: illustration/section boundaries) | yes | NO | MEDIUM — 18/9/1 structural markers whose semantics the rig never sees; paragraph grouping lost |
| 9 | Double quotation marks `"` around rune phrases | p40 (×2 pairs), p42 (×2), p53 | **NO — absent from transcript entirely** | no | **HIGH** — quoted spans mark selected subsequences; not even recoverable from the rig's input |
| 10 | Inline Arabic digits (koan numbering 1–5; inline `7`) | p36 red "1", lines 458–480; line 137 | yes | NO (non-rune → dropped) | MEDIUM — the inline `7` sits mid-ciphertext; numbering defines an ordering channel |
| 11 | 4×4 Arabic number grid, one cell red | p15: 3258 3222 3152 3038 / 3278 **3299(red)** 3298 2838 / 3288 3294 3296 2472 / 4516 1206 708 1820 | **NO** | no | **HIGH** — 16 numbers + a red-singled cell (3299); a whole numeric payload absent from the solver stream |
| 12 | Base64-style pair tables (8 cols × 9–10 rows) | p49, p50, p51 | **NO** | no | **HIGH (known: the 2048-bit payload — control)** |
| 13 | Mixed number/rune-word grid (palindromic totals 272 138 … 138 272) | 0_wisdom.jpg (solved "wisdom" page) | numbers NO | no | MEDIUM — gematria-sum table; numeric halves invisible to rig |
| 14 | Red dot-matrix blocks (small grids of red squares after red words; patterns differ) | p0, p2, p3 (×2), p14, p15, p23, p27, p33 (×2), p36, p42, p53, p54, p55, 0_wisdom (several, visibly different pixel patterns) | **NO** (no symbol for them) | no | **HIGH** — recurring glyph with internally varying on/off cell patterns = a candidate binary micro-channel nobody transcribed |
| 15 | Cuneiform-like glyph clusters (non-runic script) | p33 bottom, p36 top (same ~6-glyph cluster) | **NO** | no | **HIGH** — an entire second script present on two pages, zero representation |
| 16 | Scattered black dot "constellation" (5 dots, irregular) | p23 top | **NO** | no | **HIGH** — irregular placement looks positional (star map / coordinates) |
| 17 | Three-dot horizontal divider | p33 mid, p15 region | no | no | LOW — likely section divider, but divider *placement* lost |
| 18 | Lemniscate / infinity squiggle ornament | p0 (top+bottom), p1, p2, p15 (mid-page, between grid and text) | no | no | LOW-MED — placement varies (mid-page on p15) |
| 19 | Orthodox-cross / totem margin art (2 per page, rotated) | p0, p1, p2 | no | no | LOW — repeated decorative pair |
| 20 | Spiral/vine margin ornaments | p3, p5 | no | no | LOW |
| 21 | Bare-branch tree margin art (full height, left or right) | p8 (left), p9 (right) | no | no | LOW-MED — side alternates |
| 22 | Root-tree margin pair with dot clusters (≈2 dots left, 4–5 dots right) | p33?, p40, p42, p44, p46, p49–p54 | no | no | MEDIUM — the small dot clusters beside each tree repeat across pages; count/position would carry low-rate data if it varies (needs exact count pass) |
| 23 | Insect illustrations: cicada (p2, p53, p55, 0_wisdom), mayfly (p14), single wing (p27) | no | no | LOW-MED — placement correlates with section ends; wing-venation detail is plausible stego substrate (image-domain, out of scope for rune stream) |
| 24 | Grey ghost/watermark tree (low-contrast, only non-black-and-red element seen) | p55 | **NO** | no | **MED-HIGH** — unique rendering style on the final page; faint/greyscale = classic carrier for embedded detail |
| 25 | Page numbers | none visible on any sampled page | n/a | n/a | n/a |
| 26 | Blank panels / whitespace layout (indentation, centered short lines, title gaps) | p15, p33, p55 | no | no | LOW-MED — layout geometry wholly absent |

## Bottom line

The solver consumes exactly ONE channel: the sequence of 29-symbol rune identities, plus
`%` page grouping. Every other mark class above — color, size, punctuation, quotes,
digits, grids, second-script glyphs, dot matrices, ornaments, layout — is either absent
from `krisyotam_runes.txt` or stripped by `runes_to_indices()` before any cipher code
runs. Classes 2, 9, 11, 14, 15, 16 (and control 12) have zero representation anywhere in
the rig's input; classes 3, 4, 6, 8, 10 exist in the file but are discarded at load.
