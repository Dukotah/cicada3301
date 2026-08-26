# L1 — TOOLCHAIN — PRE-REGISTRATION

_Round 18, lane L1. Written 2026-08-25 **before** any measurement was run.
RECON-A **G-01** / RECON-B **B-11** (both `never-run` in `liber-primus/LEDGER.json`).
FRESH-ANGLES track 5, proposed and never executed._

## 0. Why this lane exists

Round 17 established at ≥0.99 power that the anti-repeat filter on LP2 is **machine-applied**
(`round17/SYNTHESIS.md` §2). A machine implies a program; a program implies a toolchain; a
toolchain leaves *physical* fingerprints in the artifacts this repo already holds — 56 page
JPEGs that `analysis/stego/STEGO-VERDICT.md` already describes as 400-DPI renders carrying an
"Artifex Software 2011" sRGB ICC profile. Nobody has converted that into a **cryptanalytic
prior**. This lane's deliverable is not a stego result; it is a *ranked prior over generator /
language families* for the derived-key dictionary (B-04).

## 1. Hypotheses

**H1 (renderer/encoder identification).** The 56 LP2 JPEGs carry version-characteristic encoder
parameters — DQT quantisation tables, Huffman table provenance (IJG-default vs optimised),
chroma subsampling, component count, JFIF density/units, restart interval, ICC profile identity,
marker order and pixel geometry — sufficient to name the **rasteriser + JPEG encoder pair** that
produced them and to bound the **release year** of that software.

**H1a (per-page colour decision).** The 23/33 grayscale/colour split already recorded in
`corpus/G-forensics/raw/lp_dqt_partition.json` is a *per-page automatic* decision by the encoder,
not an author choice. Which programs make that decision automatically is itself a fingerprint.

**H2 (rune font identification).** The runic glyphs are set in a stock Anglo-Saxon futhorc face
available 2012–2014 (candidate set: FreeSerif runic block, Junicode, Noto Sans Runic, Segoe UI
Symbol runic range, Unifont runic block, GNU Unifont CSUR, LaTeX `allrunes`, Caslon Antique
runic variants) rather than in hand-drawn or bespoke outlines.

**H3 (source document).** A PDF/PS source with an extractable text layer or an embedded font
subset exists or once circulated. An embedded subset's `/BaseFont` name names the typesetting
program and the face outright.

**H4 (payoff).** H1–H3 constrain the author's **platform**, and platform constrains the set of
plausible RNG / language families that could have produced a machine-applied rejection sampler
in 2012–2014.

## 2. Instruments

| # | instrument | file |
|---|---|---|
| I1 | Full JPEG marker parser + IJG quality-scale inversion by interval arithmetic + Huffman-table classifier + ICC header/tag parser | `jpeg_fingerprint.py` |
| I2 | Pipeline control renderer: build a synthetic PDF, push it through candidate pipelines, fingerprint the outputs with I1 | `pipeline_control.py` |
| I3 | Glyph-bitmap extraction using the **validated R9 template-DP** reader (`analysis/retranscribe/read.py`, the one that passes its control at 98.0% on count-exact lines) — explicitly **not** `round12/frontB/forceseg.py` forced re-segmentation, which fails at 12.9% | `glyph_extract.py` |
| I4 | Font matcher: render candidate faces at matched cap-height, compare by normalised symmetric-difference (IoU-complement) and per-glyph rank | `font_match.py` |
| I5 | Source-document hunt: local corpus enumeration + web/archive search | `pdf_hunt.py` + logged searches |

## 3. Positive controls (each must PASS before its null is trusted)

**PC1 — quality recovery.** Encode a test image at 6 known libjpeg qualities
(50, 75, 85, 90, 92, 95). I1 must return the exact planted quality for **6/6**.
*Fail ⇒ H1's quality claim is void.*

**PC2 — pipeline discrimination.** Render one synthetic PDF through at least three distinct
pipelines available on this machine (Ghostscript `jpeg`/`jpeggray` device at default and at
explicit `-dJPEGQ`; Ghostscript→ImageMagick default-quality JPEG; ImageMagick direct). I1 must
produce a **different** fingerprint vector for at least two of them, demonstrating the instrument
can tell pipelines apart at all. *Fail ⇒ report "instrument not discriminative", not a negative.*

**PC3 — font self-match calibration.** Render a known runic face, run I4 against a bank
including that face and ≥3 decoys. The face must rank **1st against itself** and its self-distance
must fall below the 5th percentile of the cross-face distance distribution.
*Fail ⇒ H2 is unmeasurable with this instrument and is reported as such.*

## 4. Nulls

- **N1.** Encoder parameters are pipeline-generic: every control pipeline yields the same
  fingerprint vector ⇒ no identification is possible; report the bound, not a name.
- **N2.** Best-matching font distance is statistically indistinguishable from the distance to the
  *worst* candidate (no separation beyond the PC3-calibrated band) ⇒ no font identified.
- **N3.** No PDF with a text layer is located in the corpus, on archive.org, or in circulation.

## 5. Pass/fail thresholds (fixed here, not editable after results)

| claim | threshold to assert it |
|---|---|
| **exact IJG quality** | the interval-arithmetic inversion admits exactly one integer quality consistent with all 64 luma **and** all 64 chroma coefficients, and PC1 = 6/6 |
| **encoder named** | a control pipeline reproduces **byte-identical DQT tables + identical Huffman table set + identical subsampling + identical component-count behaviour**. Anything short of that is written as "consistent with", never "identified" |
| **year bound** | asserted only from a dated artefact inside the file (ICC creation date, profile description string, or a parameter only introduced in a dated release), quoted verbatim |
| **font identified** | best candidate's mean per-glyph distance ≤ the PC3 self-match band **and** ≥2σ better than the runner-up across ≥20 distinct rune classes |
| **font excluded** | candidate's mean distance > PC3-calibrated cross-face band on ≥20 classes |
| **generator prior** | every row of the ranked prior must cite the specific measured fact that moves it, and give the direction and rough magnitude of the shift. Rows with no measured support are written as "unmoved (prior = base rate)" |

## 6. What a negative looks like here

If N1/N2/N3 all hold, this lane reports: the measured fingerprint vector, the bound it does place
on the toolchain, the control's demonstrated discriminating power, and the concrete condition that
reopens it. Per Round 18 rule 6 no lane writes "exhausted", "closed", or "unsolvable"; coverage
and `not_covered` are reported instead.

## 7. Scope explicitly NOT covered by this lane

- No steganographic re-analysis (settled in `analysis/stego/STEGO-VERDICT.md`).
- No re-transcription (that is L3/A-01's ground).
- No decode sweep. This lane emits a **prior**; it does not consume it.
