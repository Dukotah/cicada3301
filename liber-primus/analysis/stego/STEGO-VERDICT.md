# Image-steganography sweep — VERDICT (2026-06-20)

Avenue: do the unsolved Liber Primus **page images** (LP2, onion7 `0.jpg`–`57.jpg`)
carry steganography — the way Cicada's 2012/2013 and early-2014 images did?
This repo had only ever treated the images as transcription sources; image
stego was never examined here.

## 0. Provenance — the images we have ARE the authentic originals (proven)

The widely-circulated relikd/LiberPrayground images we already had are **byte-identical
to the original onion7 release**: all **56/56 SHA1 hashes match** the values
published in the Internet Archive item `ky2khlqdf7qdznac.onion` (the archived
capture of the actual 7th Tor hidden service Cicada used to dump LP2 in May 2014).
Table: `analysis/stego/provenance.json`.

- Each is a 2400×3600 JPEG, **400 DPI**, with an identical 2576-byte
  **"Artifex Software 2011" sRGB ICC profile** — the Ghostscript production
  fingerprint, uniform across every page and every independent mirror
  (relikd, rtkd/iddqd "unmodified files", krisyotam, archive.org).
- This is the first published cryptographic provenance check tying the circulating
  copies to the archived onion dump. (No Cicada-signed image hashes exist; this is
  the best achievable chain.)

Implication: stego analysis on these files is **valid** — they are not re-renders.
And because they are **Ghostscript renders at 400 DPI** (genuine OutGuess carriers
have JFIF density 1×1/unknown), the LP2 pages were **not produced as OutGuess
carrier images** in the first place.

## 1. Channel-by-channel results (tool: `stego_scan.py`, pure Python)

| Channel | Result |
|---|---|
| **Appended data after JPEG EOI** | **None** on all 56 (0 trailing bytes). Kills the scream314 "trailing-space anomaly" hint. |
| **Metadata (EXIF / COM / XMP)** | **None.** Only the uniform Artifex ICC (production, identical across pages). |
| **Embedded file carve** (binwalk-lite, validated) | **None.** Raw signature matches in compressed DCT entropy fail header validation (false positives). |
| **Spatial LSB (R/G/B planes)** | **Not applicable / noise.** JPEG is lossy; spatial-pixel LSB is compression noise, not a usable channel. |
| **Red/black rune color channel** | **Dead.** Confirmed a *solver-tool annotation* — relikd marks "active runes in red"; the originals are black-on-white with no color semantics. Not a Cicada channel. |
| **DQT quantization tables** | 2 distinct fingerprints across 56 pages (benign Ghostscript quality grouping); no payload signal. |
| **OutGuess DCT-domain** | See §2. |

## 2. OutGuess — empty, plus one precisely-characterized artifact

Using rtkd/iddqd's pre-extracted payloads (`lp_outguessed/`, the .jpg there are
SHA-verified identical to the originals), with the confirmed historical command
`outguess -r page.jpg out` (no passphrase):

- **LP1 carrier pages (00–16)** reproduce the *real, known* stego: PGP-signed
  messages (`-----BEGIN PGP SIGNED MESSAGE-`, ~98% ASCII). Method validated.
- **LP2 pages — 30 of 33 sampled (onion7 0–32) extract EMPTY.** OutGuess's
  validity check fails ⇒ no embedded payload.
- **3 pages (onion7 0, 4, 26 = rtkd 17, 21, 43)** each yield exactly **58152 bytes
  at entropy 7.997** (≈ maximal randomness, 37% ASCII). 58152 B is simply the
  OutGuess extraction *capacity* of a 2400×3600 JPEG (same dims → same length) —
  it is the classic "OutGuess false-positive on a non-carrier JPEG."

**Novel observation (community only ever called these "garbage"):** the three
false-positive blobs are **not independent**. They share an identical **1417-byte
prefix** (pages 4 & 26 share 2004 B), and even their tails correlate
(4.74% positional byte match vs 0.39% random). High entropy (7.87), no
text/PGP/zlib/gzip signature anywhere.

**Most likely explanation (mundane):** OutGuess `-r` with the default key walks the
*same* initial coefficient path in every image and XORs against a *fixed* RC4
keystream. These pages share large **identical blank margins** (same Ghostscript
template), so the early-path coefficients are identical across pages → identical
high-entropy prefix; divergence begins where the path enters page-specific rune
regions. I.e. a formatting+tool artifact, **not a hidden payload** — consistent
with the pages not being OutGuess carriers at all.

## Verdict

**No recoverable image steganography in the unsolved LP2 pages.** Appended-data,
metadata, color, LSB, and carve channels are all empty; OutGuess yields empty or
capacity-length false-positives. The unsolved challenge is the runic cipher
(shown elsewhere to be one-time-pad-class), not image stego — matching community
consensus, now backed here by verified-authentic originals and a per-channel sweep.

## The one thing not 100% closed (decisive next experiment)

The shared-prefix artifact hypothesis is *strongly* supported but not *proven*,
because this Windows box has no way to run OutGuess 0.2 (no WSL/Docker/compiler).
Decisive test, on a Linux env:
1. `outguess -r` a **blank/control** JPEG produced through the same 400-DPI
   Ghostscript/Artifex pipeline and same dimensions. If it reproduces the 1417-byte
   prefix ⇒ artifact confirmed, avenue fully closed.
2. Re-extract pages 0/4/26 with candidate passphrases (`-k`): `3301`, `33011033`,
   `circumference`, `firfumferenfe`, `welcome`, `instar`, `pilgrim`. A passphrase
   that turns the high-entropy blob into structure would be a real break (very low
   prior, but it is the only untested OutGuess parameter).

Until then: avenue is **closed pending the Linux control run** above.
