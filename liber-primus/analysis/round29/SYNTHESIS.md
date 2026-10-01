# Round 29 — "Active Attack" Armada — SYNTHESIS (2026-09-28)

Five parallel ACTIVE attack fronts (no tool-building, no passive monitoring), each control-validated
before any claim. All five are genuinely new vs the ~162-entry elimination ledger. Standing OTP-class
/ unsolvable-by-design verdict is **UNCHANGED**; two lanes produced real *positive* findings (not just
nulls), and several premise errors in the record were corrected.

## Results

| Lane | Attack | Verdict | Payoff |
|---|---|---|---|
| L1 | Onion image large-dictionary OutGuess/steghide crack (4,013 keys × 3 imgs × 2 tools = 24,078 extractions) | CLEAN NULL | First real key-attack on the onion chain; corrected the "5×5-rune" record |
| L2 | Two-time-pad cross-XOR of all opaque blobs + as pads over known plaintexts | CLEAN NULL | De-aliased the blob pile; closed the deferred cross-XOR lane |
| L3 | Interior chroma/LSB of rune imgs 107/229 as its own bitstream | CLEAN NULL | Anomaly = constant red DC offset (decoration), not a signal |
| L4 | PRNU + JPEG quant-table encoder fingerprinting across 2012→2014 corpus | **POSITIVE** | 2014 LP master = Ghostscript-rendered PDF; splits from 2012 libjpeg toolchain |
| L5 | Live-web OSINT people-hunt (mruzuki first) | NULL + tightened | mruzuki = zero-footprint burner, resolved to dead end |

## The two real positives

**L4 — toolchain identified (HIGH confidence, reproducible control).** The entire 2014 onion7 / Liber
Primus master (all 56 relikd pages = byte-identical to the pristine onion7 master by MD5) was authored
as a **PDF/PostScript document and rasterized through Ghostscript (Artifex GhostPDL)** to JPEG at 400 DPI,
q~92, optimized Huffman. Proven because a local Ghostscript render emits the byte-identical Artifex ICC
profile, marker order, and quant table. The 2012 images are a different toolchain (plain libjpeg/editor
export, no ICC). This narrows the *process* (LP2 was typeset, not hand-composed per page) and dates the
GS build (optimized Huffman ⇒ older than GS 10.06). All EXIF deliberately stripped everywhere = OPSEC
finding. No named individual (nothing identifying survives).

**L1 — record correction.** `dl_onion3.jpg` is authentic (matches micheloosterhof/cicada-2014
stage03/onion3.jpg) but is a "Chapter 1 / Intus" divider, NOT a literal 5×5 rune grid. The runic
"A WARNING / BELIEVE NOTHING" page is **onion2**. Every prior "onion3 payload" in the repo was really the
keyless 1033.jpg "Welcome" message — so the onion image chain had **never** been password-attacked until now.

## Doctrine

Each lane ran positive + negative controls before any positive claim. L1 reproduced the 1033 "Welcome"
payload byte-for-byte; L2's crib-drag fired on shared-pad English and stayed silent on independent random;
L3 recovered an OutGuess-embedded test message and fired null on a clean JPEG; L4 reproduced the GS render
byte-identically; L5 fetched every handle/key claim from a live source. No false positives were promoted.
The wrong-key-artifact trap (OutGuess never fails → every key yields random bytes) was explicitly avoided.

## What remains open after R29

- **Three genuinely-random blobs** (2.jpg stage04 payload, folly, canon_256) could be single-use ciphertext
  under an external key — crib-drag cannot detect a non-reused OTP, so this is unfalsifiable by these means.
- **Goal-2 attribution**: only human-in-the-loop contacts left (email mruzuki@gmail.com; Wanner re: CAKES
  git survival; transcribe the Oct-2025 Eriksson podcast; Nox Populi DEF CON 26 detail). Nothing crawlable.
- Standing compute-tail branches (PRNG seed space, /dev/urandom) unchanged — out of this armada's scope.

## Ledger entries to add (5)
R29-L1-ONION-STEGO (null), R29-L2-BLOB-CROSSXOR (null), R29-L3-CHROMA-BITSTREAM (null),
R29-L4-IMAGE-FORENSICS (positive: 2014=Ghostscript, toolchain split), R29-L5-OSINT-MRUZUKI (null/tightened).

Artifacts per lane under `analysis/round29/L{1..5}-*/`. Nothing committed (WSL no creds; owner pushes from Windows/GCM).
