# N1 — PDF text-layer / embedded font-subset hunt — RESULTS

_Round 20, Lane N1. Archival, ungated, concurrent. Pre-registration: `PREREG.md`._
_Extends Round 18 L1's NC-6 ("the outside world is unsearched, not searched-and-empty")._

## Headline

**NEGATIVE.** No surviving Liber Primus typeset source document — no PDF/PostScript carrying a
runic text layer or an embedded runic `/BaseFont` font subset — exists in the local corpus (195
distinct PDFs) or is reachable across the four named mirrors (iBotPeaches, micheloosterhof,
krisyotam, Internet Archive). The published artifact is image-only everywhere it appears. The
S-TEX promotion trigger (a font subset naming an `allrunes`-family face) **did not fire**;
S-TEX stays rank 5.

The single highest-value unrecovered artifact in the puzzle after the ciphertext — a subset tag
that would name the typesetting program and rune face — **is not present in any reachable
source.** L1's inference about the toolchain (gs 9.04-9.14 -> ImageMagick q92, 6x9in page)
remains an inference, not a measurement.

## Positive control (proves the instrument works)

`control.py` typeset runic text (U+16A0..U+16C7) into a PDF via `lualatex`+`fontspec`, embedding
a **subset** of `NotoSansRunic-Regular.ttf`, then ran the *same* `pdffonts` command used on every
real target:

```
LBJNRT+NotoSansRunic-Regular   CID TrueType   Identity-H   yes yes yes   4  0
```

- **Subset tag recovered verbatim: `LBJNRT+NotoSansRunic-Regular`** (emb=yes, sub=yes).
- `pdftotext` recovered the runic codepoints from the text layer:
  `0x16a0 0x16a2 0x16a6 0x16a8 0x16b1 0x16b7 0x16c1 0x16c7`.
- Negative control (image-only re-wrap of an LP page JPEG via ImageMagick): `pdffonts` reports
  **0 fonts** — the instrument distinguishes a source document from a re-wrap of the images.

If a real LP source PDF with an embedded runic subset existed anywhere reached, this instrument
would have surfaced its tag. The null is therefore trustworthy. **Control PASS.**

## Coverage

**Local corpus (whole repo root, not just liber-primus/):** 545 PDF paths, 350 exact duplicates,
**195 distinct** PDFs each run through `pdffonts` + `pdftotext` + `strings|grep`. This supersets
L1's 493-path / 530-list local scan and reproduces its NC-6 verdict.

**Off-repo mirrors (the piece L1 did NOT do), reached 2026-08-28 via GitHub/IA APIs:**

| mirror | reachable | doc/font source assets | note |
|---|---|---|---|
| iBotPeaches/cicada_3301 | full tree (not truncated) | **0** | images + `.asc` keys + 1 `.gpg` only |
| micheloosterhof/cicada-2014 | full tree | **0** | — |
| micheloosterhof/cicada-2016 | full tree | **0** | — |
| krisyotam/cicada3301 | 4507 entries, 351 doc assets | all = local cijhho archive | no LP source; all derivative |
| archive.org `liber-primus` | 9.09 MB ZIP fully inspected | **0** | 58 re-encoded page JPEGs + mp3 + webp; a repackaging of the published images, not a source |
| archive.org `cicada_202405` | full manifest | **0** | — |
| archive.org PDF query | numFound **0** | — | no LP-primus PDF indexed |

## The only real-world runic font subset in the entire corpus (and why it is NOT a hit)

`corpus/F-press-academic/papers/runic/2023-HistoCrypt-Runic-cryptography-early-epigraphic-period-200-700.pdf`
embeds three subsetted runic faces:

- **`FAAAAA+RunlittBUnicode`**
- **`GAAAAA+RunlittA-Bold`**
- **`HAAAAA+Gullhornet`**

This is a **2023 academic paper on early-epigraphic runic cryptography** — published nine years
after LP2 (2014), using a Scandinavian academic runic package (Runlitt / Gullhornet), with **zero
runic text-layer chars** (its runes are in figures). It is unrelated to the LP typesetting
toolchain and is a **NEGATIVE** for this lane. (Matches L1's original find of the same file.)

Every other runic-bearing PDF is a derivative document with runes as a *text layer of standard
Unicode* set in ordinary fonts, never a runic subset:
- `2016 puzzle.pdf` (163 runic text-layer chars) — a solver write-up, fonts Times/Arial/Calibri/
  Wingdings/SegoeUISymbol, all standard Windows subsets.
- `Anglo-Saxon runes - Wikipedia.pdf` (107 chars) — a saved Wikipedia page.
- `runeslatin.pdf` — a solver transliteration tool; `CIDFont+F1/F2/F3` with **no subset tag**,
  non-runic, and a *Latin* transliteration text layer (`S-H-E-O-G-M-...`), not runes.
- `2014 - What Happened Part 2; Liber Primus (POST 2014).pdf` — the most LP-titled document;
  Word-authored, standard Windows font subsets (Times/Arial/Courier/Wingdings), **0 runic
  text-layer chars**. The runes in it are raster images.

## Three conditionals of this negative (doctrine Q4)

1. **KEY SPACE.** The set of PDFs in {repo corpus (195 distinct) + the 4 named mirrors reachable
   2026-08-28}. NOT "all PDFs that ever existed." A copy held privately by a solver, or on an
   unlisted host, is outside this bound.
2. **EXTRACTOR RELATION** (the artifact-hunt analogue of the decoder model). Negative under
   `pdffonts` (font objects) + `pdftotext` (Unicode-Runic text layer) + `strings|grep FontFile/
   BaseFont`. A font hidden in a nonstandard object stream that all three miss would evade this.
3. **ADJUDICATOR REGISTER.** "runic face / genuine LP source." Non-runic embedded subsets
   (Times/Arial/etc.) and derivative runic documents (Wikipedia saves, solver write-ups, a 2023
   academic paper) are NEGATIVES by construction, even though they carry embedded subsets or
   runic text layers.

## Kill condition — TRIGGERED and honoured

Per PREREG Q5: after re-scanning the full local corpus and fetching the mirror-reachable PDFs,
no PDF surfaced with a runic font subset or a genuine-LP runic text layer. **Archival bound
logged (`mirror_sweep.json`); lane STOPPED.** Did NOT drift into AN-END onion OSINT / preimage
retrieval (foreclosed, ELIMINATION-LEDGER :328-384). Wall clock well under the 15-min box.

## Reopen condition

Any PDF/PostScript surfacing — from a private solver hoard, an unlisted host, a fuller IA/onion
crawl, or a torrent — with an extractable runic text layer OR an embedded runic `/BaseFont`
subset. A subset's six-letter tag + face name would name the typesetting program and rune face
outright, promoting S-TEX rank 5 -> 1 and converting L1's toolchain inference into a measurement.

## Files

- `PREREG.md` — five Aiming-Test answers, positive + negative control spec, thresholds.
- `control.py` -> `control_results.json` — positive control (subset tag recovered verbatim) +
  negative control (image re-wrap = 0 fonts). Regenerate with `python3 control.py`.
- `scan.py` -> `scan_results.json` — the 545-path / 195-distinct local scan. Regenerate with
  `python3 scan.py <repo-root>`.
- `mirror_sweep.json` — the off-repo mirror + Internet Archive sweep record.

## Reproduce

```bash
cd liber-primus/analysis/round20/N1
python3 control.py                 # positive control: recovers LBJNRT+NotoSansRunic-Regular
python3 scan.py /path/to/repo/root # 545 PDFs -> 195 distinct, only 2023 academic paper has a runic subset
```
