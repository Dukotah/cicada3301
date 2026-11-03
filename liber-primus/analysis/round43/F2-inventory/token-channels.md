# Round 43 — Lane F2b: token-channel inventory (transcription side)

Date: 2026-11-03. Firewalled: no ledger / findings docs consulted. Everything below was
measured directly from the three inputs with throwaway scripts (counts reproducible from
the commands quoted inline).

Inputs compared:

| file | role | rune count (U+16A0–16FF) |
|---|---|---|
| `data/scream314_lp.md` | rich transcription (markdown, per-jpg sections, LP1+LP2, solved + unsolved, outguess/hex/translit blocks) | 15,938 |
| `data/relikd/p*.txt` (9 files: p0-2, p3-7, p8-14, p15-22, p23-26, p27-32, p33-39, p40-53, p54-55) | rich transcription (plain text, blank-line page breaks) | 12,956 |
| `data/krisyotam_runes.txt` | canonical solver input (57 `%`-separated pages, 604 `/`-terminated lines) | 13,136 |

**Rune-stream identity check:** concatenating the relikd rune stream (pages in file
order) and comparing character-by-character against the krisyotam rune stream gives
**zero divergence for the first 12,956 runes** — the two agree exactly on every rune of
pages 0–54. krisyotam then appends 180 runes relikd does not have: solver page 55
(85 runes, the final rune body before the parable) and solver page 56 (95 runes, the
cleartext "parable / like the instar..." page). So on the rune channel itself nothing
is dropped; everything dropped is in the *non-rune* channels below.

## Token classes in krisyotam_runes.txt (full character census)

| token | count | meaning |
|---|---|---|
| 29 distinct runes | 13,136 | cipher stream |
| `-` | 2,766 | word separator |
| `/` | 604 | line break (end of every physical line) |
| `\n` | 689 | file formatting |
| `.` | 181 | sentence/section dot |
| `%` | 56 | page separator (57 pages) |
| `&` | 18 | section-end mark |
| `$` | 9 | chapter-end mark |
| `§` | 1 | end of book (after the parable) |
| digits `1 2 3 4 5` | 1 each | the numbered-list labels on solver pages 36–38 |
| digit `7` | 1 | the inline Arabic `7` on solver page 10 (`…ᚩᚦᛏ-7-ᚷ…`) |

## Token classes in the richer transcriptions and their fate

Position-aligned diff method: walk each file, index every non-rune token by the number
of runes preceding it, then compare relikd tokens vs krisyotam tokens at the same rune
index. Result: 183 punctuation positions in relikd vs 181 in krisyotam, 39 position
mismatches, every one accounted for below.

### Survive (lossless or near-lossless)

| class | rich form | solver form | notes |
|---|---|---|---|
| runes | 29 glyphs | identical stream | 0 diffs over 12,956 shared runes |
| word separator | `•` (relikd 2,731; scream314 3,343) | `-` | word lengths fully preserved |
| line breaks | physical lines | `/` at end of each of 604 lines | line structure fully preserved |
| sentence dot | `⁘` (145) | `.` | survives, but see merge below |
| page breaks | blank lines / `##` headers | `%` | survives, but krisyotam **merges** some image pages: e.g. the number-grid image (scream314 "32.jpg - 15.jpg", 9 runes `ᚠᚢᛚᛗ•ᚪᛠᚣᛟᚪ`) is merged with the following 150-rune page into one solver page 15 (9+150=159 ✓); same for 91+123=214 on solver page 33 |
| chapter/section mark | `⁜` (31 in relikd) | inline `⁜` → `.`; page-final `⁜` → `.&` or `.&$`; book-final → `.§` | the *identity* of ⁜ as a distinct glyph is erased inline (indistinguishable from ⁘ in solver input) |
| list numbers 1–5 | `1`…`5` prefixing lines (relikd p33-39) | `1`…`5` | survive, solver pages 36–38 |
| inline `7` | relikd p8-14 line 34 | `7` | survives, solver page 10 |

### Silently dropped (the inventory the lane asked for)

1. **The 16-number Arabic grid — 16 tokens, solver page 15.**
   relikd p15-22.txt lines 2–5 / scream314 line 1595–1598:
   `3258 3222 3152 3038 / 3278 3299 3298 2838 / 3288 3294 3296 2472 / 4516 1206 708 1820`,
   each row terminated by `⁘` in relikd. In krisyotam the whole grid — 16 four-digit
   numbers **and** their 4 row-dots — collapses to the single `.&$` at rune index 3612
   (position-diff row `(3612, '⁜⁘⁘⁘⁘', '.&$')`). Zero trace in the solver input.

2. **The base-60 tables — 256 two-character cells, three full pages, absent entirely.**
   relikd p40-53.txt segments 10–12: grids of 80 + 104 + 72 cells (8 columns), each
   cell `[0-4][0-9A-Za-z]` — i.e. base-60 digit pairs, values 0–~299 (scream314 decodes
   the first table to decimal 0–255 byte values at its "66.jpg - 49.jpg" section; it
   marks another occurrence only as a `[base60]` placeholder inside a rune block).
   These pages contain **zero runes**, so in krisyotam they vanish without even a `%`:
   the solver input jumps straight from page 49 (66 runes, ends `&`) to page 50
   (92 runes). 256 tokens ≈ 256 bytes of potential data, completely outside the
   solver stream.

3. **Double-quote-delimited spans — 14 `"` marks = 7 spans, 405 runes, dropped.**
   relikd (and scream314, which quotes the same spans in its rune blocks) marks
   quoted/visually-distinct passages with `"`. krisyotam drops every quote mark
   (adjacent `⁘` kept as `.`). Mapped to solver pages by rune index:

   | span (rune idx) | length | solver page(s) |
   |---|---|---|
   | 1659–1677 | 18 | 6–7 |
   | 5459–5478 | 19 | 22 |
   | 9715–9727 | 12 | 40 |
   | 9811–9869 | 58 | 40 |
   | 10211–10279 | 68 | 42 |
   | 10279–10439 | 160 | 42–43 |
   | 12522–12592 | 70 | 52 |

4. **Apostrophes — 4 tokens, dropped.** Genitive-style `'ᚳ` ("…'s") at rune indices
   1110, 5138, 8515, 10089 → solver pages 4, 21, 35, 41. The rune after the apostrophe
   is kept; the mark is erased, so the solver input cannot distinguish `X'S` from a
   word ending in S-rune.

5. **The `⁚` punctuation variant — 4 tokens, identity erased.** relikd distinguishes
   `⁘` (145) from `⁚` (4, pages ~5/10/21/46 region in relikd labelling); krisyotam maps
   both to `.`. Count preserved, class distinction lost.

6. **Inline `⁜` vs `⁘` distinction — erased.** Inline chapter-marks (e.g. page 0
   `…ᛋᚣᛖᛝᚳ⁜ᚦᛄᚷᚫ…`) become plain `.` in krisyotam, indistinguishable from sentence
   dots.

7. **scream314-only classes, absent from the solver input by design:** LP1 solved
   pages (~2,800 extra runes incl. a duplicated koan), **Key:** editorial annotations,
   Latin transliteration blocks, decimal decode of table 1, outguess PGP/hex payloads,
   the magic-square page numbers, HTML markup. These are editorial/solved-side, not
   cipher channels, but note `src/lp/corpus.py` parses *scream314* (not krisyotam), so
   the two solver entry points differ in which pages they even see.

## Word-boundary / line structure: preserved but UNUSED

- `krisyotam_runes.txt` fully preserves word lengths (`-`) and line structure (`/`),
  and `src/lp/corpus.py` keeps `•` + newlines in its `runes` field
  ("runes + '•' word seps + newlines").
- But the decode path strips them: `src/lp/solve.py` `_runes_only()` filters to bare
  runes before every decode; `src/lp/stats.py` (ioc, doublets, chi2, entropy, kasiski)
  and `src/lp/score.py` (letter quadgrams) operate on rune-index / letter streams only.
  `src/lp/gematria.py` `runes_to_translit` *can* carry separators but only for display.
- **No module in `src/lp/` consumes word lengths, word-boundary positions, or line
  lengths as a signal.** (217 analysis/ scripts reference the krisyotam/relikd corpora;
  auditing those is outside this lane's scope — the statement above is about `src/lp/`.)

## Residual bookkeeping

- relikd lacks the last two solver pages (85 + 95 runes); krisyotam is the superset.
- scream314 rune total (15,938) = LP1 solved pages + LP2 + block duplication; it is not
  a clean superset and its `corpus.py` parse keys off `##` jpg-labels, not solver pages.
- All 39 position-level punctuation mismatches between relikd and krisyotam are
  explained by rules: `⁜`→`.&`/`.&$`, `"`→deleted, `'`→deleted, grid-rows→deleted,
  final-two-pages→krisyotam-only. No unexplained token remains.
