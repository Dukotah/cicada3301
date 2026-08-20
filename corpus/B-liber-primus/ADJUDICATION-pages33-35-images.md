# ADJUDICATION — LP2 pages 33 and 35, by page image

**Verdict: CANON IS CORRECT at all three positions. `henkman/liberprimus` is wrong at all three.**

Status: **DECIDED** from the primary artifact (the archived onion7 page renders).
Date: 2026-08-19. Lane B, branch `corpus-sweep`.

Companion to `ADJUDICATION-page56.md`, which settles the fourth conflict against
plaintext. With this document, **all four of henkman's substantive glyph conflicts are
now resolved, and all four go to canon.**

---

## 1. Why an image test is legitimate here

Pages 33 and 35 are in the **unsolved** corpus. No plaintext exists to check a reading
against, so the only ground truth is the artifact itself.

The Liber Primus pages were published by 3301 as clean vector-rendered images — black
runes and red drop caps on white — not as photographs of a physical manuscript. At 400
DPI (2400 × 3600) every stroke is crisp and the glyphs are typographically identical
from one occurrence to the next. There is nothing to squint at.

Provenance: the images are `liber-primus/data/relikd/p33.jpg` and `p35.jpg`, SHA-1
pinned against the archived onion7 dump in
`liber-primus/analysis/stego/provenance.json` (56/56 match, re-verified here).

| page | SHA-1 | bytes |
|---|---|---|
| 33 | `33d4f93c96d60af268033d978f854ecdc103e329` | 525,652 |
| 35 | `8ac0a9c6241f052ecb6b23881d43d3aad3d887bb` | 574,580 |

## 2. The disputed glyph pair

Every one of the three positions is the **ᚹ / ᛒ** pair — exactly the confusable pair
`liber-primus/handoff/PARKED.md` predicts. In this typeface they are not in fact
confusable at 400 DPI:

- **ᚹ** (WYNN, `W`, U+16B9) — one vertical stem with a **single small triangle** on the
  upper right, occupying roughly the top third of the glyph. Latin `P` in silhouette.
- **ᛒ** (BEORC, `B`, U+16D2) — one vertical stem with **two stacked triangles** on the
  right, together filling the full glyph height. Latin `B` in silhouette.

The stroke-count difference is one whole triangle. A downscaled or JPEG-mangled copy
could blur them; the archived render does not.

## 3. Locating the glyphs (derived, not eyeballed)

`corpus/B-liber-primus/make_crops.py` does this from the pixels plus `PAGES.json`:

1. **Row band** — row-wise ink profile of the page gives contiguous text bands. Red drop
   caps span three lines and fuse those bands, so the script recovers the line pitch
   (median of band-top differences in `(h, 2h]`, where `h` is the modal band height) and
   splits fused bands on it. Decorative header/footer clusters and the `⋯` stanza
   separator are rejected because their horizontal ink extent is under 900 px, far
   narrower than a text line.
2. **Assertion** — the number of image lines recovered must equal the number of non-empty
   lines in `PAGES.json` `segment_boundaries.line_break_offsets`. It does:
   **11 for page 33, 12 for page 35**. If it ever stops matching, the script fails loudly
   rather than cropping the wrong row.
3. **Column** — column-wise ink profile inside the chosen band gives per-glyph x-runs.

Derived coordinates:

| page | rune index | runic line (0-based) | column in line | image band `y` |
|---|---|---|---|---|
| 33 | 100 | 5 | 9 | 1908–2022 |
| 33 | 115 (control) | 6 | 5 | 2100–2214 |
| 33 | 117 | 6 | 7 | 2100–2214 |
| 35 | 155 | 7 | 0 | 2026–2140 |
| 35 | 160 | 7 | 5 | 2026–2140 |

Regenerate with:

```bash
cd /c/Users/dukot/projects/cicada3301
export PYTHONIOENCODING=utf-8
python corpus/B-liber-primus/make_crops.py
```

---

## 4. Page 33, rune index 100 — canon `ᛒ B`, henkman `ᚹ W`

Crops: `crops/p33_rune100_B_tight.png`, `crops/p33_rune100_context.png`

Line 6 (runic line index 5) of page 33 reads
`ᛝ ᚦ ᛇ · ᛁ ᚠ ᚳ ᛟ ᛇ ⁜ ᛞ ᛒ ᚣ ᛡ ᚣ ᚢ · ᚣ ᚾ ᚦ ᚱ ᛖ` — 19 runes, the first drawn as a
large red drop cap (ᛝ, the diamond).

The crop shows, immediately right of the red `⁜` section mark: a bowtie-between-two-stems
(**ᛞ**, `D`), then a stem carrying **two stacked triangles** that together run the full
glyph height (**ᛒ**, `B`), then **ᚣ** and **ᛡ**. That is canon's `D-B-Y-IA` exactly.

**Reading: `ᛒ` (B). Not ambiguous.** henkman's `ᚹ` would require the lower triangle not
to exist; it is fully inked and the same weight as the upper one.

## 5. Page 33, rune index 117 — canon `ᛒ B`, henkman `ᚹ W`

Crops: `crops/p33_rune117_B_tight.png`, **`crops/p33_rune115W_vs_rune117B.png`**

Line 7 (runic line index 6) reads
`ᛗ ᛁ · ᛇ ᛞ ᚱ ᚹ · ᛉ ᛒ ᚻ · ᚳ ᛄ ᛡ ᚪ · ᚾ ᚹ · ᚾ ᛗ · ᚠ` — 18 runes.

**This is the strongest single crop in the whole exercise**, because canon puts a genuine
`ᚹ` at index 115 and the disputed glyph at index 117 — two runes apart, same line, same
point size, same rendering pass. `p33_rune115W_vs_rune117B.png` shows both side by side:

```
   ᚱ    ᚹ    ·    ᛉ    ᛒ    ᚻ    ·    ᚳ    ᛄ
  115=W ------> one triangle, upper third only
              117=B ------> two triangles, full height
```

The two glyphs are visibly different objects in the same image. There is no lighting,
scan, or scale artefact that could turn one into the other.

**Reading: `ᛒ` (B). Not ambiguous.**

## 6. Page 35, rune indices 155 and 160 — a transposition, not a substitution

Crops: `crops/p35_rune155_Y_tight.png`, `crops/p35_rune160_B_tight.png`,
`crops/p35_runes155-160_context.png`

Both transcriptions carry 271 runes on this page, so the `delete`+`insert` pair the diff
emitted is really one **ᛒ moved five positions**:

```
canon    … ᚱ ᛖ ᚦ | ᚣ ᛏ ᛝ ᛡ ᚩ ᛒ · ᛏ ᚦ ᚳ …      R-E-TH | Y-T-NG-IA-O-B / T-TH-C
henkman  … ᚱ ᛖ ᚦ | ᛒ ᚣ ᛏ ᛝ ᛡ ᚩ · ᛏ ᚦ ᚳ …      R-E-TH | B-Y-T-NG-IA-O / T-TH-C
                   ^ line 8 begins here
```

The whole of image line 8 (runic line index 7, `y` 2026–2140) reads, glyph by glyph:

```
ᚣ ᛏ ᛝ ᛡ ᚩ ᛒ · ᛏ ᚦ ᚳ · ᛉ ᚳ · ᛋ ᚪ ᚫ · ᛗ ᚠ ᛄ ᚱ ᛖ · ᛡ ᛇ ᛁ ᛇ
Y  T  NG IA O  B     T  TH C     X  C     S  A  AE    M  F  J  R  E     IA EO I  EO
```

— 23 runes, matching canon's `runes[155:178]` exactly, word breaks included.

- **Index 155 (line-initial): `ᚣ` (Y).** The crop shows a stem, a long descending
  diagonal, and a short interior stem — the YR glyph. It carries **no triangles at all**,
  so it cannot be henkman's `ᛒ` under any reading.
- **Index 160: `ᛒ` (B)**, sixth glyph of the line, immediately after `ᚩ` and immediately
  before the word-break dot. Two stacked triangles, unmistakable.

**Reading: canon. Not ambiguous.**

---

## 7. What this changes

- **Nothing in the canonical corpus.** Canon survived every check that could be made.
  The 12,956-rune unsolved index, its SHA-256 pin
  `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`, and every statistic
  downstream of it stand unchanged. No re-run is required.
- **henkman/liberprimus is demoted.** Its four substantive glyph conflicts are now 0-for-4
  against ground truth: one against plaintext (page 56), three against the images. Add its
  64-rune shortfall — bulk `insert` blocks on pages 0, 3, 6, 19, 26, 39 where canon has
  runes henkman lacks, the signature of dropped lines — and the picture is an
  **incomplete, error-carrying early transcription**, not a competing careful reading.
  It remains historically interesting (repo created 2016-08-14, a year before the
  rtkd/iddqd root) but it is **not** a source of corrections.
- **The ᚹ/ᛒ worry raised in `liber-primus/handoff/PARKED.md` is closed for these three
  positions.** The pair is genuinely confusable *in principle*, and henkman did in fact
  confuse it — but the archived 400-DPI renders separate the two glyphs cleanly, and canon
  reads them right. That does not clear every ᚹ/ᛒ in the book; it does show the artifact
  is good enough to settle any such dispute case by case.

## 8. Caveats

- This is a **reading** check, not an OCR audit. Three positions were examined because
  three were disputed. No claim is made about the other 13,133 runes.
- The verdicts rest on my visual reading of the crops. The crops are committed-by-script
  and reproducible, so anyone can re-look; the raw images are SHA-1 pinned so there is a
  fixed thing to re-look at.
- `crops/` holds rendered PNGs — derived data. Per `CLAUDE.md` they belong in
  `.gitignore` with `make_crops.py` as the regeneration path.
