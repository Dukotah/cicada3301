# L4 Image Forensics — FINDINGS (Round 29)

**Battery:** exiftool 13.50, ImageMagick, PIL 12.1.1/numpy, Ghostscript 10.06. Custom JPEG structural parser validated against PIL and a live Ghostscript control.

## BOTTOM LINE — attribution verdict

**The 2012 and 2014 releases SPLIT on toolchain, and the 2014 toolchain is positively identified as Ghostscript.**

- **2014 onion7 / Liber Primus master corpus** (all 56 relikd page renders + the "authored" 400dpi set) was produced by rasterizing a PDF/PostScript document through **Ghostscript (Artifex GhostPDL)** to its `jpeg` device at **400 DPI, quality ~92**. Proven by a **reproducible control**: local Ghostscript emits a byte-identical `Artifex Software sRGB ICC Profile` (2592-byte APP2, "Copyright Artifex Software 2011"), the identical `APP0>APP2>DQT>DQT>SOF0…` marker order, and the **identical luma quant table** `[3,2,2,2,2,2,3,2,2,2,3,3,3,3,4,6…]` as the Cicada files. **Confidence HIGH** — tool-specific fingerprint, not a QF coincidence.
- **2012-era images** (dl_onion1/2/3, lpc_02, dl_1033, 4gq25): no ICC, JFIF-only, resolution-unit "none", standard (non-optimized) libjpeg Huffman at QF ~76–100. Plain **libjpeg / image-editor export** — a different toolchain. **Confidence HIGH.**

The split narrows the *process* (2014 puzzle authored as a PDF and machine-rendered, not hand-painted per page), not a named person. All identifying EXIF (Make/Model/Software/timestamp/GPS) is stripped from every image — a consistent, deliberate OPSEC sterilization, itself a finding.

## Metadata cross-tab
Only surviving discriminators are the JFIF resolution block and the ICC profile. All 56 onion7 pages carry the identical `Artifex Software sRGB ICC Profile` — the single strongest attribution signal (Artifex = the Ghostscript company; its raster devices embed exactly this profile).

Corpus noise flagged: **onion5portrait.jpg is a WebP** (RIFF/VP8, web thumbnail); **onion5portrait_alt.jpg and t2_iddqd.jpg are ASCII text "404: Not Found"** (failed downloads, not images).

## DQT encoder clusters
| Cluster | est QF | Huffman | ICC | Members |
|---|---|---|---|---|
| A `b871b72ba7cb` | ~100 | standard | no | dl_onion1/2/3, lpc_02 |
| B `125483e21b5c` | ~76 | standard | no | dl_1033, 4gq25 |
| C `3e0f1ac7d0b3` | ~92 | **optimized** | Artifex (where kept) | 2.jpg, dl_107/167/229/server-status, s11_1, ORIGINAL_p00, 33 relikd color pages |
| D `bc45112fcda7` | ~92 gray | optimized | Artifex | ORIGINAL_p24, 23 relikd grayscale pages |

- A/B = standard IJG/libjpeg tables + non-optimized Huffman (libjpeg/editor export family; A vs B differ only in QF).
- C/D share the exact IJG-q92 DQT + optimized Huffman + Artifex ICC + 400dpi = the Ghostscript fingerprint. C = color pages, D = grayscale pages (same toolchain, page-content split).
- dl_107/167/229/server-status are Cluster C by DQT+Huffman but ICC-stripped → re-hosted copies of GS renders, not a separate encoder.
- **Decisive link:** the authored Cluster-C/D DQTs are byte-identical to the relikd master pages → "authored images" and "onion7 master" are the same encoder output.

**Controls validated:** PIL q=75 DQT matched Cluster B byte-for-byte; PIL q=92 matched C/D byte-for-byte; the Ghostscript render control reproduced the marker order, 2592-byte Artifex ICC, and q92 DQT exactly (only Huffman differed — GS 10.06 didn't optimize, so the originals' optimized Huffman points to an older GS build, a minor version signal).

## Render-vs-photo
Corpus is **overwhelmingly digital renders** — all 56 relikd pages + ORIGINAL_p00/p24 + the 2014 set + dl_onion1/3 + lpc_02 show 93–99.9% flat pixels and 92–99% pure black/white (rasterized ink-on-paper). PRNU is not applicable (no sensor). **dl_1033.jpg** is the only continuous-tone/photo-like image (libjpeg-q75 cluster) — but "photo-like stats" ≠ proven camera capture, and there's no second photo to correlate a shared sensor against, so **no PRNU sensor match is claimed**.

## Structural
- Dimensions: 2400×3600 (onion7, = 6×9" at 400 DPI, book trim), 1327×1427 (dl_1033), and **563×569 for 4gq25 — both prime** (Cicada's prime-dimension motif; 509×503 not present in this corpus).
- All Baseline DCT (no progressive), 8-bit, 4:2:0 color / single-component gray.
- **relikd == ORIGINAL confirmed by MD5**: `p0.jpg` and `p24.jpg` are byte-identical to `ORIGINAL_onion7_p00/p24.jpg`. The relikd corpus IS the pristine onion7 master.

## Confidence ledger
- 2014 = Ghostscript/Artifex render: **HIGH** (reproducible control)
- 2012 = libjpeg/editor export: **HIGH** (PIL DQT byte-match, no ICC)
- 2012/2014 toolchain split: **HIGH** (disjoint signatures)
- Source was PDF/PostScript: **MEDIUM-HIGH**
- Optimized-Huffman ⇒ older GS version: **MEDIUM**
- dl_1033 is a true camera photo: **LOW**
- Attribution to a named individual: **NONE** (EXIF fully stripped)

## Artifacts on disk (`analysis/round29/L4-image-forensics/`)
`jpeg_fingerprint.py`, `prnu.py` (scripts); `fingerprints_authored.json`, `fingerprints_relikd.json`, `exif_authored.json`, `exif_relikd.json`, `prnu.json` (data); `gs_ctrl.jpg`, `ctrl_q{75,92,100}.jpg` (control renders proving the GS match).
