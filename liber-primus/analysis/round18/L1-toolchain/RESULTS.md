# L1 — TOOLCHAIN — RESULTS

_Round 18, lane L1. RECON-A **G-01** / RECON-B **B-11**, both `never-run` in `liber-primus/LEDGER.json`.
FRESH-ANGLES track 5. Pre-registration: `PREREG.md`, written before any measurement._

> **What this lane is for.** Round 17 showed at ≥0.99 power that LP2's anti-repeat filter is
> **machine-applied**. A machine implies a program; a program implies a toolchain; and a toolchain
> is physically fingerprinted in artifacts this repository already holds. The deliverable is not a
> file-forensics report — it is **§6, a ranked prior over generator/language families** for the
> derived-key dictionary (B-04).

---

## 1. Headline

**The 58 Liber Primus part-2 page images were not written by Ghostscript. They were written by
ImageMagick, re-encoding a Ghostscript render.** That is a two-stage pipeline, and both stages are
identified with a passing positive control that reproduces the LP2 parameter vector exactly,
including byte-identical quantisation tables and the marker order.

```
   [typeset source document: PDF or PostScript]
              |
              v
   Ghostscript  -sDEVICE=jpeg  -r400        <- 400x400 dpi, 2400x3600 px, 4:2:0 chroma,
              |                                embeds "Artifex Software sRGB ICC Profile" (2576 B)
              v
   ImageMagick  (convert / mogrify, quality 92)   <- optimised Huffman tables, automatic per-page
              |                                      grayscale detection, ICC carried through
              v
   0.jpg .. 57.jpg  as published on ky2khlqdf7qdznac.onion (onion7), May 2014
```

The author's platform is **GNU/Linux**, corroborated independently by their own PGP tooling: 46 of
46 curated 3301 signed messages spanning 2012, 2013 and 2014 carry
`Version: GnuPG v1.4.11 (GNU/Linux)` — one signing environment, unchanged for three years.

`analysis/stego/STEGO-VERDICT.md` and `AGENTS.md` currently describe the pages as
"400-DPI Ghostscript renders". That is half the chain. **The JPEG encoder is ImageMagick, not
Ghostscript** — see §3.2, where the discriminator is a single control run.

---

## 2. Instruments and controls (all pre-registered)

| id | instrument | file | control | measured |
|---|---|---|---|---|
| I1 | JPEG marker/DQT/DHT/ICC fingerprint extractor | `jpeg_fingerprint.py` | **PC1** — recover 6 planted IJG qualities exactly | **6/6 PASS** |
| I2 | Pipeline discrimination | `pipeline_control.py` | **PC2** — ≥2 pipelines must fingerprint differently | **PASS** (Huffman class separates Ghostscript from ImageMagick perfectly, 18 runs) |
| I2b | Two-stage chain reproduction | `chain_control.py` | reproduce the LP2 vector | **PASS** — exact, both classes (§3.3) |
| I3 | Per-rune glyph bitmaps | `glyph_extract.py` | uses the **validated** R9 template-DP reader (96.93% agreement on 5,207 compared glyphs, `analysis/retranscribe/diff_report.json`) — explicitly **not** `round12/frontB/forceseg.py`, which fails its control at 12.9% | 29/29 runes recovered |
| I4 | Runic-face matcher | `font_match.py`, `font_sheet.py`, `font_verdict.py` | **PC3a/b/c** — clean leave-one-in, degraded self-match, and LP2 split-half noise floor | **all PASS**; 11/11 faces self-rank 1st (§5.1) |
| I5 | ICC release probe | `icc_version_probe.sh`, `icc_oldpath_probe.sh` | byte-exact profile comparison across ghostpdl tags 9.00–10.06 | **two-sided bound, gs 9.04–9.21** (§4) |
| I6 | Local source-document hunt | `pdf_hunt.py` | a re-wrap has no fonts and no text layer; the original would have both | §7 NC-6 |

**PC1** (`python3 jpeg_fingerprint.py --selftest`): planted qualities 50, 75, 85, 90, 92, 95;
recovered `[50] [75] [85] [90] [92] [95]`; **6/6 exact**. The inversion is interval arithmetic over
libjpeg's `temp = (base*scale + 50)/100` rule against the Annex K base tables, so a returned
singleton is a proof, not an estimate.

**PC2** (`control_results.json`, 18 runs, 2 synthetic source PDFs × 9 pipelines): the fingerprint
vector separates renderers cleanly. The separating field is the Huffman table class.

---

## 3. What the 58 page files actually say

### 3.1 The measured fingerprint (all 58 files, `pages_summary.json`)

| field | value | uniform across files? |
|---|---|---|
| geometry | **2400 × 3600 px** | 58/58 |
| JFIF | version **1.01**, units **1** (dpi), density **400 × 400**, no thumbnail | 58/58 |
| DQT | **IJG standard Annex K tables at quality exactly 92** — luma sha1 `c96e442f…`, chroma sha1 `cd6e3767…` | 58/58 |
| Huffman | **custom / optimised** (i.e. the encoder set `optimize_coding = TRUE`) | 58/58 |
| ICC | **2576 bytes**, desc `Artifex Software sRGB ICC Profile`, cprt `Copyright Artifex Software 2011`, ICC v2.1.0, platform `APPL`, md5 `e409cef13cd06f6b371f6cddc8e31fcf` | **byte-identical, 58/58** |
| markers | colour `APP0,APP2,DQT,DQT,SOF0,DHT×4,SOS,EOI`; gray `APP0,APP2,DQT,SOF0,DHT×2,SOS,EOI` | 58/58 |
| restart interval | **none** | 58/58 |
| COM / EXIF / XMP | **none** | 58/58 |
| trailing bytes after EOI | **0** | 58/58 |
| progressive | no (baseline SOF0) | 58/58 |
| components | **35 files colour** (3 comp, 4:2:0 `22x11x11`), **23 files grayscale** (1 comp) | split |

The colour/grayscale split, by page:
`grayscale = {16,17,18,19,20,21,24,25,28,29,30,31,41,42,43,44,45,46,47,48,50,51,52}` (23 pages),
everything else colour (35 pages, including 56 and 57).
This reproduces `corpus/G-forensics/raw/lp_dqt_partition.json`, which covered pages 0–55 only;
this lane extends it to 56 and 57 (both colour).

The **quality-92 result is new and it is exact**. IJG quality 92 is not a value a human types
casually; it is **ImageMagick's compiled-in default JPEG quality**. Ghostscript's `jpeg` device
defaults to `JPEGQ=75`.

### 3.2 The discriminator: Huffman tables

`pipeline_control.py` (PC2), 18 runs on this machine:

| pipeline | ncomp (gray src) | subsampling | IJG Q | **Huffman** | APPn | ICC desc |
|---|---|---|---|---|---|---|
| `gs -sDEVICE=jpeg -r400` | 3 | 22x11x11 | 75 | **IJG-standard** | JFIF, ICC | Artifex sRGB |
| `gs -sDEVICE=jpeg -dJPEGQ=92 -r400` | 3 | 22x11x11 | 92 | **IJG-standard** | JFIF, ICC | Artifex sRGB |
| `gs -sDEVICE=jpeggray -dJPEGQ=92` | 1 | 11 | 92 | **IJG-standard** | JFIF, ICC | Artifex **sGray** |
| `convert -density 400 x.pdf out.jpg` | 1 | 11 | 92 | **custom-optimised** | JFIF, **XMP** | none |
| `gs → png → convert` | 1 | 11 | 92 | **custom-optimised** | JFIF | none |
| `pdftoppm → convert` | 1 | 11 | 92 | **custom-optimised** | JFIF | none |
| **LP2 (observed)** | **1 or 3** | **11 / 22x11x11** | **92** | **custom-optimised** | **JFIF, ICC** | **Artifex sRGB** |

Read the table: **no single-stage pipeline produces the LP2 vector.** Ghostscript alone gives
IJG-standard Huffman tables. ImageMagick alone gives no Artifex ICC. LP2 has *both* an Artifex ICC
*and* optimised Huffman tables. Three further LP2 facts each independently require the two-stage
reading:

1. **4:2:0 chroma at quality 92.** ImageMagick forces 1×1 (4:4:4) sampling at quality ≥ 90 when it
   has no sampling factors to inherit — visible above (`convert` on a PDF gives `11x11x11`). LP2's
   colour pages are `22x11x11`. ImageMagick emits 4:2:0 at q92 only when it **inherited** the
   sampling factors from a JPEG input. So ImageMagick's input was already a JPEG.
2. **sRGB profile on grayscale files.** All 23 grayscale pages carry the **sRGB** profile, not
   `sGray`. Ghostscript's own grayscale device writes `Artifex Software sGray ICC Profile`
   (row 3 above). An sRGB profile on a 1-component JPEG means the grayscale conversion happened
   *downstream* of an sRGB-tagged colour render, by a program that passes profiles through
   unaltered.
3. **The colour/grayscale split is automatic, not authored.** ImageMagick's JPEG writer tests the
   image and drops to `JCS_GRAYSCALE` when no pixel carries chroma. One uniform command over 58
   files therefore yields a mixed 23/35 split — exactly what is observed. An author choosing
   per-page devices by hand would be an odd thing to do and would leave `sGray` behind.

### 3.3 The chain control reproduces LP2 exactly

`chain_control.py` → `chain_results.json`. Two synthetic source PDFs (one gray-content, one with a
colour element), Ghostscript to JPEG, then ImageMagick:

| run | ncomp | subsampling | IJG Q | Huffman | APPn | ICC |
|---|---|---|---|---|---|---|
| `stage1_gs_q92_colour` | 3 | 22x11x11 | 92 | IJG-standard | JFIF, ICC | Artifex sRGB |
| **`stage2_im_q92_gs92_colour`** | **3** | **22x11x11** | **92** | **custom-optimised** | **JFIF, ICC** | **Artifex sRGB** |
| **`stage2_im_q92_gs92_gray`** | **1** | **11** | **92** | **custom-optimised** | **JFIF, ICC** | **Artifex sRGB** |
| `stage2_pil_q92opt_gs92_gray` | 3 | 22x11x11 | 92 | custom-optimised | JFIF, ICC | Artifex sRGB |

Byte-level comparison of the control against LP2 page 0 (colour) and page 16 (gray):

- **DQT tables byte-identical** — both `c96e442f9ce9a1965c6084df936558fcc335a69f` (luma) and
  `cd6e3767d9c4da25c4f8126038b332d0ac48f244` (chroma). ✔ (this was the pre-registered bar)
- **Marker order identical** in both the colour and the grayscale class. ✔
- **JFIF block identical** (1.01 / units 1 / 400×400 / no thumb). ✔
- **ICC 2576 bytes, same description and copyright**, differing in exactly **2 bytes** — see §4. ✔
- Huffman tables are **content-adaptive** when `optimize_coding` is on, so byte-identity is not
  achievable without the original source document and is **not** claimed; the *classification*
  matches, which is the discriminating field.

**Python/PIL is excluded** as the second stage: `stage2_pil_*` keeps 3 components on gray content,
so it cannot produce the 23-page grayscale class.

### 3.4 A refinement the repo should absorb

`AGENTS.md:39-41` and `analysis/stego/STEGO-VERDICT.md:16-26` say the pages are Ghostscript
renders. Keep the *provenance* claim (56/56 SHA-1 match, no recoverable stego — untouched by this
lane) but the *encoder* attribution needs the second stage added. It matters for that document's
own argument: STEGO-VERDICT reasons about OutGuess carriership from "Ghostscript output", and the
JPEG the world received was in fact ImageMagick output at q92 with optimised Huffman tables. The
conclusion (not an OutGuess carrier) is unaffected — 4:2:0, q92, optimised-Huffman renders of
line art are, if anything, worse carriers — but the premise should be corrected.

---

## 4. Dating the Ghostscript build

The LP2 ICC profile and the Ghostscript 10.06.0 profile shipped today are both 2576 bytes and
differ in **exactly two bytes**, both inside the ICC header's PCS-illuminant field:

| | offset 68..79 (PCS illuminant X, Y, Z as s15Fixed16) |
|---|---|
| **LP2 (all 58 files)** | `0000f6d5  00010000  0000d32c` |
| Ghostscript 10.06.0 | `0000f6d6  00010000  0000d32d` |

The modern values are the ICC-canonical D50 white point (0.9642, 1.0, 0.8249). The LP2-era profile
carries both X and Z one LSB low. Artifex corrected this at some release; the correction is a
**hard upper bound on the Ghostscript version** used to make the pages, and the profile's own
`Copyright Artifex Software 2011` plus the fact that Artifex's ICC-based colour architecture only
arrived in Ghostscript 9.00 (2010) is a lower bound.

`icc_version_probe.sh` and `icc_oldpath_probe.sh` fetch `iccprofiles/srgb.icc` (and, for the early
releases, `gs/iccprofiles/srgb.icc`, where Artifex kept it before the tree was reorganised) from
the ghostpdl tags, and record the md5 and the illuminant bytes per release into
`icc_versions.json` / `icc_versions_early.json`. The result is a **two-sided, byte-exact version
bound**:

| Ghostscript release | released | `srgb.icc` size | illuminant 68..79 | md5 | matches LP2? |
|---|---|---:|---|---|:---:|
| 9.00, 9.01, 9.02 | 2010-09 … 2011-03 | **3144 B** | `0000f6d6 … 0000d32d` | — | **no** |
| **9.04 … 9.21** | **2011-08-05 … 2017-03-16** | **2576 B** | **`0000f6d5 … 0000d32c`** | **`e409cef13cd06f6b371f6cddc8e31fcf`** | **YES — byte-identical** |
| 9.22, 9.26, 9.50, 9.53.3, 10.06.0 | 2017-10-04 → | 2576 B | `0000f6d6 … 0000d32d` | `27d2435a749ae91e9974bf7a109a03e5` | no |

Measured releases inside the matching band: **9.04, 9.05, 9.06, 9.07, 9.09, 9.10, 9.12, 9.14,
9.15, 9.16, 9.17, 9.18, 9.19, 9.20, 9.21** — all byte-identical to the LP2 profile.

> **Bound: the renderer is Ghostscript ≥ 9.04 and ≤ 9.21.** Artifex introduced the 2576-byte
> profile at 9.04 (2011-08-05) and corrected the two illuminant bytes at 9.22 (2017-10-04).

Intersected with the artifact's own publication date (the onion7 dump, May 2014), the last release
that could have been used is **9.14** (2014-03-26); 9.15 did not ship until September 2014. So the
operative window is **Ghostscript 9.04 – 9.14, i.e. August 2011 – March 2014**. The lower bound is
the sharper of the two facts: it is *later* than the profile's own `2011` copyright string, and it
is a measurement rather than an inference.

**Ubuntu 12.04 LTS shipped Ghostscript 9.05 (February 2012)** — inside the window, and the same
distro generation that ships the GnuPG 1.4.11 the author signed with for three years (§6, F6/F7).
The two independent dating channels agree.

**This ICC observation appears to be new.** No published Liber Primus analysis located in this
lane's search has noted the Artifex profile, the quality-92 encode, or the two-stage chain.

---

## 5. The rune face

`glyph_extract.py` recovers **29/29** rune bitmaps from the page images using the validated R9
template-DP reader and its bijective class→rune mapping, cropped to ink bounding box
(`runes_observed.npz`, contact sheet `runes_observed.png`, per-rune metadata in
`runes_observed_meta.json`). Constant stroke width, flat unserifed terminals, and 29 cleanly
separable designs: **the runes are typeset from a font, not drawn.** Widths in the template frame
vary from 34 px (`ᚠ`, `ᚪ`, `ᚾ`, `ᛁ`) to 64 px (`ᛉ`, `ᛝ`), so the face is proportional, not
monospaced. (Heights are all exactly 114 px, which is a normalisation artefact of the extraction
pipeline, not a property of the face — see §5.1.)

Candidate bank assembled in `fonts/` (`get_fonts.sh`, `get_fonts2.sh`), all with a Runic block and
all with a 2012–2014 lineage: GNU FreeFont **FreeSerif / FreeSans / FreeMono**, **Noto Sans Runic**,
**Segoe UI Symbol** (`seguisym.ttf`, ships with Windows 7/8), **Quivira**, **BabelStone Runic**,
**BabelStone Runic Elder Futhark**, **BabelStone Modern**, **GNU Unifont**, **Symbola**, and the
LaTeX **`allrunes`** Type-1 family (CTAN, 200+ variant faces). Junicode and Everson Mono could not
be fetched from any mirror tried and are recorded in §7 as not covered.

Matching results and the PC3 calibration are in `font_match_results.json` and §5.1.

### 5.1 PC3 calibration, and the metric that had to be thrown out

`font_match.py` computes two distances per rune, both in [0,1] as one minus intersection-over-union:
`D_aspect` (aspect-preserving fit into a common box) and `D_stretch` (both bitmaps stretched
independently to the box, so only stroke topology is compared).

**`D_aspect` is disqualified.** `runes_observed_meta.json` shows every one of the 29 observed
bitmaps has height *exactly* 114 px. No real runic face has 29 glyphs of identical height, so that
uniformity is an artefact of the R9 template pipeline, which normalises cluster heights. The
observed aspect ratios are therefore not the font's aspect ratios and must not be scored.
`font_verdict.py` re-runs the entire calibration on the aspect-free `D_stretch` metric; that is the
number reported below. (The confound was found *after* the first run and is recorded here rather
than quietly dropped — the pre-registered threshold rule is unchanged, only the metric it is
applied to.)

Three controls, all passing:

| control | what it measures | result |
|---|---|---|
| **PC3a** clean leave-one-in | each bank face scored as if it were the observed set | **PASS** — every face ranks itself 1st at distance ≈ 0 |
| **PC3b** degraded self-match | each bank face pushed through a render → JPEG q92 → downsample-to-114px → threshold simulation, then re-matched against the clean bank | **PASS 11/11** — every face still ranks itself 1st; self-distance band **[0.0126, 0.0926]**, mean **0.0371** |
| **PC3c** LP2 split-half | the 29 rune classes' glyph instances split into two disjoint halves, two independent centroid sets built, compared to each other | LP2's own reproducibility floor = **0.0301** over 28 classes |

PC3c is the important one: it says the observed bitmaps reproduce *themselves* at 0.0301, which
sits inside the PC3b self-match band. So if the true face were in the bank, it should have scored
around 0.03–0.09. For contrast, the **cross-face** distribution over 110 wrong-face pairs has mean
**0.610**, minimum **0.292**, 5th percentile **0.340**.

### 5.2 Match — result

| rank | face | `D_stretch` vs LP2 |
|---:|---|---:|
| 1 | **Noto Sans Runic** | **0.4096** |
| 2 | BabelStone Runic | 0.4420 |
| 3 | GNU Unifont | 0.4731 |
| 4 | BabelStone Runic Elder Futhark | 0.5297 |
| 5 | FreeMono | 0.5449 |
| 6 | Quivira | 0.6310 |
| 7 | FreeSans | 0.7210 |
| 8 | BabelStone Modern | 0.7254 |
| 9 | Segoe UI Symbol | 0.7295 |
| 10 | Symbola | 0.7318 |
| 11 | FreeSerif | 0.7536 |

**Verdict: none of the eleven faces is the Liber Primus rune face.** The best candidate is at
**13.6×** the measured LP2 reproducibility floor, sits *outside* the PC3b self-match band by a
factor of 4.4, and is not even below the 5th percentile of the wrong-face distribution. Separation
from the runner-up is 0.23σ — i.e. the top of the ranking is a tie among near-misses, which is what
a ranking looks like when the right answer is absent. The instrument had ample power to see a
match had one been present (PC3b, 11/11).

What the ranking *does* say is design-family information: Noto Sans Runic and BabelStone Runic —
the two modern reference designs of the Anglo-Saxon futhorc — are markedly closer to LP2 (0.41,
0.44) than the wrong-face mean (0.61). The LP2 face is a member of that design tradition; it is
simply not one of these files.

The side-by-side sheet `font_match_sheet.png` shows why. All 29 glyph *topologies* agree — same
strokes, same joins, same variant choices for ᚷ, ᛄ, ᛝ, ᛞ. The divergence is **proportion**: the LP2
runes are markedly taller and narrower than every candidate. That is consistent with either a
condensed face, or a face rendered with a non-unit horizontal scale — the sort of thing a
typesetting program does when a `\scalebox` or an XY-scaled font matrix is applied. Both readings
point at a **typeset** document rather than a font dropped into an image editor, which is the same
conclusion §3 reaches from the encoder chain.

## 6. THE PAYOFF — ranked prior over generator / language families

This is the deliverable. Every row cites the measured fact that moves it and states the direction
and rough magnitude of the shift. Rows with no measured support are marked *unmoved*.

### 6.1 The facts that do the work

| # | measured fact | where | what it constrains |
|---|---|---|---|
| **F1** | JPEG encoder is **ImageMagick** (optimised Huffman, q92, auto-gray, ICC pass-through) | §3.2–3.3, `chain_results.json` | ImageMagick is a Unix-first CLI tool; `convert`/`mogrify` over a numbered page set is a **shell/scripting** idiom |
| **F2** | Renderer is **Ghostscript** with an **Artifex sRGB ICC** | §3.1, §4 | Ghostscript-on-Linux; the source was a **PDF or PostScript** document |
| **F3** | ICC profile is **byte-identical to ghostpdl 9.04–9.21** and differs from 9.00–9.02 and from 9.22+ | §4, `icc_versions.json`, `icc_versions_early.json` | **Ghostscript ≥ 9.04 (2011-08-05) and ≤ 9.21**; with the May-2014 dump date, **9.04–9.14**. A distro package of exactly the Ubuntu-12.04 generation (gs 9.05), not a fresh build, and **not** a later re-render |
| **F4** | 400 dpi, 2400×3600 px = exactly **6.00 × 9.00 inches** | §3.1 | a **trade-paperback page size**, i.e. a real typesetting job with a page geometry, not an image editor canvas |
| **F5** | Runes are **typeset from a proportional font**, uniform stroke, 29 distinct glyphs; and the face is **none of the 11 stock Unicode runic faces tested**, differing from all of them chiefly in *proportion* (taller/narrower) | §5.1–5.2, `font_verdict.json` | a **text-based** authoring path, so the runes existed as **character data** before they were pixels — and one that applied a **non-unit horizontal scale or a condensed face**, which is a typesetting-program behaviour, not an image-editor one |
| **F6** | **46/46** curated 3301 PGP messages, 2012→2014, are `GnuPG v1.4.11 (GNU/Linux)` | `corpus/A-primary-artifacts/ibotpeaches/messages/`, verified this lane | the author's working machine is **GNU/Linux**, one environment, three years, no drift |
| **F7** | GnuPG **1.4.11** specifically (released 2010-10-18) — not 1.4.12+, not 2.x | F6 | a **Debian/Ubuntu package pinned to a 2011-era release**; Ubuntu 11.04–12.04 LTS shipped exactly 1.4.11, Debian wheezy shipped 1.4.12 |
| **F8** | ImageMagick default quality **92** was used rather than an explicit `-quality` | §3.1 | the author ran the tool **with defaults**, i.e. a short, unfussy script — consistent with a few-line shell pipeline, not an engineered application |
| **F9** | No EXIF, no XMP, no COM, zero trailing bytes, restart interval unused | §3.1 | a **plain CLI** invocation; no GUI editor, no web pipeline, no `jpegtran`/`jpegoptim` post-pass |
| **F10** | The rune face is **not** Noto Sans Runic, BabelStone Runic (either), Unifont, FreeSerif/FreeSans/FreeMono, Quivira, Symbola, BabelStone Modern or Segoe UI Symbol — measured with three passing controls | §5.2 | the author did **not** simply type Unicode runes in a default desktop font. Either a specialist scholarly face (Junicode, Everson Mono — NC-4) or a **LaTeX runic package** (`allrunes` — NC-5) is still live, and the latter would promote row 5 of §6.2 sharply |

**The composite platform inference: an Ubuntu 11.04–12.04-LTS-class GNU/Linux workstation, used
unchanged from early 2012 through May 2014.** F6+F7 fix the OS family and era from the author's own
signatures; F1+F2+F3 put the *same* era's Ghostscript and ImageMagick on the same box; F5+F4 say a
typesetting program produced a 6×9-inch PDF on it.

### 6.2 The ranked prior

Base rate = the flat prior a blind sweep would use. "Shift" is the multiplicative re-weighting this
lane's evidence justifies. These are **priors for search-order and budget allocation**, not
probabilities of being the answer.

| rank | generator / language family | shift | why (cite the fact) | swept before? |
|---:|---|---:|---|---|
| **1** | **C `rand()` / `random()` / `drand48` from glibc** (incl. anything calling libc from a shell tool) | **×3** | F6/F7 fix glibc-on-Linux as the runtime; `random()`'s TYPE_3 additive-feedback generator is *the* default PRNG a 2012 Linux C program gets for free | Round 8 covered 10 generators over ~3% of each seed space (`round10/L5-seed32/CENSUS.md`) — that is a **~3% coverage bound**, not a sweep of the family |
| **2** | **Python 2.7 `random` (Mersenne Twister, `random.seed(str)`)** | **×3** | F1/F8: whoever drives `convert` over 58 numbered files on Linux in 2012 is scripting; Python 2.7.3 is Ubuntu 12.04's system Python. Python's `seed()` on a *string* has a 2.x-specific hashing path that a Python-3-era sweep would miss | partially |
| **3** | **Perl 5.14 `rand`/`srand`** (drand48 under the hood) | **×2.5** | F7's era: Perl 5.14.2 is Ubuntu 12.04's system Perl and the default text-munging language of that generation of Unix user | **never swept** |
| **4** | **Bash/coreutils composites** — `$RANDOM`, `/dev/urandom`, `shuf --random-source`, `openssl rand` | **×2** | F8/F9: defaults-only CLI usage says the author reached for the shell first. `$RANDOM` is a 15-bit glibc `rand()` derivative with a tiny seed space | **never swept** |
| **5** | **A LaTeX-side generator** (`pgf`'s `\pgfmathrandom`, `lcg` package, `random.tex`) | **×2** | F5+F4: a 6×9-inch typeset PDF full of runic characters is a LaTeX-shaped job, and `allrunes` is *the* LaTeX Anglo-Saxon runic package. If the pad was generated inside the document, the generator is a TeX LCG with a tiny period | **never swept, never considered** |
| 6 | **OpenSSL / GnuPG-adjacent CSPRNGs seeded from a short passphrase** (`openssl enc -k`, EVP_BytesToKey, PBKDF/`S2K`) | ×1.5 | F6: GnuPG is demonstrably on the box and in daily use; an author who signs everything with GnuPG plausibly derives key material with the crypto tools already installed. R16-KDF covered a KDF family — check its `not_covered` before re-running | partly (R16-KDF, 692,064 configs) |
| 7 | Java `java.util.Random` (48-bit LCG) | ×1 *unmoved* | nothing in the artifacts points at a JVM either way | partially |
| 8 | PHP `mt_rand` / `rand` | **×0.8** | flagged in `round10/L5-seed32/CENSUS.md` as the top never-swept name; nothing here promotes it, but nothing demotes it much either — a Linux box in 2012 has PHP 5.3.10 installed by default | **never swept** — still the top *unswept* name |
| 9 | Windows CRT `rand()` / `srand()`, MSVC LCG | **×0.15** | F1/F2/F6/F7 all say Linux. A Windows CRT generator requires the author to have used a *second*, Windows machine solely for pad generation while doing every other step on Linux | partially |
| **10** | **.NET `System.Random` / `RNGCryptoServiceProvider`** | **×0.05 — effectively demoted out of the search** | F6+F7 (three years of GnuPG-on-Linux), F1+F2 (a GNU/Linux imaging stack), F9 (no Windows-toolchain residue anywhere in 58 files). Mono existed on Linux in 2012 but nothing points to it | partially |
| 11 | Hardware / true-RNG external pad (`/dev/random` block device, dice, a book) | ×1 *unmoved* | this lane says nothing about it. It remains the branch that no compute reaches, and §2 of `FOR-FUTURE-SOLVERS.md` still applies | n/a |

### 6.3 What this changes for the derived-key sweep

Concretely, and in priority order:

1. **Sweep Perl 5.14 `rand`/`srand` and bash `$RANDOM`.** Both are ranked above several families
   that *have* been swept, and neither has ever been run. `$RANDOM` in particular has a seed space
   small enough to enumerate completely in minutes, which makes it the cheapest unrun item in the
   whole register.
2. **Re-sweep Python's `random.seed(<string>)` under Python 2.7 semantics.** Python 2 and Python 3
   hash a seed string differently; a sweep written in 2026 that used `random.seed("CICADA3301")`
   under Python 3 did **not** test what a 2012 author's script would have produced. This is a
   silent coverage hole and it is cheap to close.
3. **Add the LaTeX-internal generators.** Nobody has considered that the pad may have been
   generated *inside the typesetting document*. F4+F5 make a LaTeX source concrete rather than
   speculative. TeX's `\pgfmathrandom` LCG has a period of 2³¹−1 and a 1..2³¹−2 seed range —
   fully enumerable.
4. **Stop spending budget on .NET.** Row 10 is a factor-20 demotion, on four independent facts.
5. **Prefer generators whose natural output is a byte/int stream that a script would reduce
   `mod 29` by rejection.** The Round-17 finding (filter is machine-applied) plus F8 (defaults-only
   tooling) together suggest a short script doing `while True: x = rng(); if x != last: emit(x)` —
   which is exactly the shape L2 is treating as a leak this round. **The two lanes compose:** L2's
   rejection-count channel is far more informative if the underlying draw distribution is one of
   ranks 1–5 above rather than an arbitrary one.

---

## 7. Coverage — what was measured, and what was NOT

**Measured (this lane).**

- All **58** LP2 page JPEGs, every marker, full DQT/DHT/ICC/JFIF/geometry vector, byte-level.
  (Prior work — `corpus/G-forensics` — covered pages 0–55 and recorded DQT sha1s only; this lane
  adds pages 56–57, the exact IJG quality, the Huffman classification, the ICC internals, marker
  order, and the trailing-byte check.)
- **18** control renders across 9 pipelines × 2 source documents, plus **20** two-stage chain runs.
- **29/29** rune glyph bitmaps via the validated (96.93%) reader.
- **46/46** curated 3301 PGP messages checked for signer version string.
- The archived `onion7_index.html` (1,640 bytes) re-read in full — see below.

**Not covered, and the concrete condition that reopens each.**

| # | not covered | reopens if |
|---|---|---|
| NC-1 | **The exact Ghostscript point release.** The measured bound is the interval **9.04 ≤ gs ≤ 9.21** (§4), narrowed by the May-2014 publication date to **9.04–9.14**; it is not a single version. Eleven releases sit inside it and ship a byte-identical profile. | a second dated artefact separates them — e.g. a release-specific rasteriser change visible in the rendered glyph edges, or a `pdfmark`/`DOCINFO` residue in some other 3301 artifact |
| NC-2 | **The exact ImageMagick version.** Only "an ImageMagick that inherits input sampling factors and defaults to q92" is established. | someone measures the 6.x releases' `coders/jpeg.c` behaviour directly against the LP2 vector |
| NC-3 | **Whether stage 2 was `convert` or `mogrify`, and whether a single command or a loop.** | file-order or size-ordering evidence emerges, or a `-define` residue is found in some other 3301 image |
| NC-4 | **Junicode and Everson Mono** — two strong period candidate faces that no mirror tried would serve. The bank covers **11** faces; these two are the named gaps. | either font is obtained; both are one file each and `font_verdict.py` re-runs in about a minute |
| NC-5 | **The `allrunes` Type-1 faces** are in the bank as files but are custom-encoded (not Unicode-mapped), so matching them requires an unordered glyph-slot search rather than a codepoint lookup. | the slot-search variant of `font_match.py` is run |
| NC-6 | **No source PDF or PostScript document located.** §3–§4 prove one existed (a typeset 6.00×9.00-inch page rendered at 400 dpi). `pdf_hunt.py` scanned **493 distinct PDFs** held locally (a 530-entry file list; some documents are vendored more than once) for a Unicode-Runic text layer or an embedded runic font subset — a re-wrap of the published JPEGs has neither. **6** carry Runic in a text layer and all are derivative: saved Wikipedia *Anglo-Saxon runes* pages, the 2016 puzzle write-up, and a 2023 academic paper on runic cryptography. **No local PDF embeds a runic font subset that could be the LP face**, and none is a source document (`pdf_hunt_summary.json`). **No off-repo web/archive search was completed inside this lane**, so the outside world is unsearched, not searched-and-empty. | any PDF surfaces with an extractable text layer or an embedded font subset. A subset's `/BaseFont` name (and its six-letter subset tag) would name the typesetting program *and* the rune face outright — the single highest-value unrecovered artifact in this puzzle after the ciphertext itself |
| NC-7 | **The onion7 index holds no non-JPEG assets.** The archived `index.html` (byte-identical in two independent copies: `analysis/structure/origsearch/onion7_index.html` and the cijhho123 dropbox) is 1,640 bytes containing exactly 58 `<img>` tags for `0.jpg`…`57.jpg`, `<title>133</title>` and `<div id="331">`. **No CSS, no scripts, no alternative formats, no unfetched assets.** | a fuller crawl of onion7 (headers, 404 behaviour, sibling paths) is recovered from an archive — the *page* is clean, the *server* was never enumerated |
| NC-8 | The prior in §6 is a **prior**, not a result. It re-weights a search; it does not decode anything. | it is consumed by an actual sweep, which is L6's and B-04's ground, not this lane's |

**Reopen condition for the lane as a whole:** any of NC-4, NC-5 or NC-6 landing changes §5 or §6
materially. NC-6 in particular would convert this lane's *inference* about the typesetting program
into a *measurement*.

---

## 8. Reproduce

```bash
cd <repo root>
python3 liber-primus/analysis/round18/L1-toolchain/jpeg_fingerprint.py --selftest   # PC1, must PASS 6/6
python3 liber-primus/analysis/round18/L1-toolchain/run_pages.py                     # the 58-file vector
python3 liber-primus/analysis/round18/L1-toolchain/pipeline_control.py              # PC2
python3 liber-primus/analysis/round18/L1-toolchain/chain_control.py                 # the reproduction
python3 liber-primus/analysis/round18/L1-toolchain/glyph_extract.py                 # 29 rune bitmaps
bash    liber-primus/analysis/round18/L1-toolchain/get_fonts.sh                     # font bank
python3 liber-primus/analysis/round18/L1-toolchain/font_match.py                    # PC3 + match
bash    liber-primus/analysis/round18/L1-toolchain/icc_version_probe.sh             # Ghostscript bound
```

Requires Ghostscript, ImageMagick, Python 3 with numpy/scipy/Pillow. All present under WSL Ubuntu
on the machine this was run on (`gs 10.06.0`, `ImageMagick 7.1.2-18`, `Pillow 12.1.1`).
