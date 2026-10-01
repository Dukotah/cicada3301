# L3 — Interior chroma modification of LP images 107 & 229, read as a raw bitstream

**Round 29 "active attack" armada, Lane L3.** Dir: `analysis/round29/L3-chroma-bitstream/`.

**Mission:** extract the confirmed interior chromatic modification in rune images 107
& 229 as its OWN bitstream (bit-plane) — the angle prior armadas deferred (they only
attacked the whole JPEG with OutGuess) — and cryptanalyze it. Controls: 167 (in-corpus),
a synthetic clean JPEG (negative), an OutGuess round-trip (positive).

## VERDICT

**Confirmed anomaly, no decodable payload. The "interior chroma modification" of 107 &
229 is a constant DC red offset (saturated rubrication ink, R-G ~= 192), not a modulated
per-pixel signal. A constant offset carries zero bits. Every bit-plane reading of the
modified region is noise (no magic header, LP score at the -7.5 noise floor). Real,
publishable characterization — NOT a hidden message.**

The prior "interior |R-G| > edge" signal is real but was measuring the INTERIORS of
red-rubrication strokes, which 107/229 have in quantity and control 167 barely has. The
redrune lane already proved that same red is decorative rubrication and cryptographically
null; this lane closes the remaining "read it as a bit-plane" branch, now from the pixel
side.

---

## 1. Anomaly mask characterization (107 / 229 vs 167 control) — mask.py

Interior ink pixels (dark strokes, eroded, off luminance-edges) with |R-G| > 5. Absolute
interior |R-G| is the discriminator (edges/bg are chroma-neutral in all three, so the
interior/edge RATIO is high everywhere; the absolute interior value separates targets from
control):

| image | interior |R-G| mean | edge |R-G| | bg |R-G| | mask px (|R-G|>5) |
|-------|--------------------|-----------|---------|-------------------|
| 107 | 11.05 | 1.24 | 0.02 | 32,054 |
| 229 | 18.13 | 2.38 | 0.04 | 46,212 |
| 167 (control) | 0.54 | 0.05 | 0.01 | 338 |

107/229 carry a strong localized interior chroma signal; 167 is two orders of magnitude
cleaner. Edges (1-2) and background (~0.02) confirm it is NOT JPEG ringing (ringing lives
on high-gradient edges, which are chroma-neutral). Anomaly is real and localized.

## 2. What the modified pixels actually are (decisive step) — controls.py

R-G over the mask is NOT a low-amplitude modulation — it is a constant DC offset:

| image | R-G mean | R-G std | R-G>0 | modal R-G (count) | value entropy |
|-------|----------|---------|-------|-------------------|---------------|
| 107 | 191.6 | 2.41 | 100% | 192 (21,164/32,054) | 0.0 bits |
| 229 | 191.3 | 2.97 | 100% | 192 (24,912/46,212) | 0.0 bits |
| 167 | 191.1 | 3.99 | 100% | 193 (51/338) | 0.0 bits |

R-G ~= 192 (R~=255, G~=63) is saturated red ink = the #C80000 rubrication the redrune lane
characterized. Applied as ONE constant colour (value entropy 0, R>G in 100% of px). A
constant value is the same everywhere; it cannot encode a bitstream. Hence the "sign of
chroma deviation" bit is degenerate (all-ones, entropy 0.000).

Bimodality proof: R-G has NOTHING between the two modes. The sub-saturated band R-G in
[1,20] is IDENTICAL across all three images incl. control: ~144K-164K px, mean 1.02, std
0.14, LSB ones-fraction exactly 0.500 (pure noise = JPEG 4:2:0 chroma-subsample residue).
No intermediate "LSB-scale" modification band exists that 107/229 have and 167 lacks. The
ONLY thing distinguishing targets from control is how much red rubrication ink the page
carries — decoration amplitude, not payload.

## 3. Every bitstream reading tried — bitstream.py / bitstream_results.json

Per image x ordering {raster, column, boustrophedon} x bit-def {LSB-R, LSB-G, LSB-B,
sign(R-G), magnitude>median} + full-interior LSB planes = 56 readings.

- Magic header: NONE (gzip/zip/PNG/JPEG/PGP/PEM/bzip2/7z/rar/pdf) in any reading.
- sign bit: degenerate — ones-fraction 1.000, entropy 0.000 (DC-offset consequence).
- Mask LSB reads: low byte-entropy (1.5-5.5) is an ARTIFACT of low ones-fraction
  (0.04-0.23 -> bytes cluster near 0x00), not structure; printable-ratio 0.05-0.23 (garbage).
  Low ones-fraction is expected: saturated-red px pin R near 255 -> LSB(R) biased.
- Full-interior LSB planes (classic stego): entropy 6.9-7.4 for ALL THREE incl. control.
  167 reads ~7.44 identically to 229's 7.40. No spatial payload.
- Bit counts: 32,054 / 46,212 mask bits -> 4,006 / 5,776 bytes. Not 256/512, not a hash
  length; just the red-stroke pixel count.

## 4. Cryptanalysis of the mask bitstreams — crypto.py

12 lowest-entropy mask streams (LSB-R, magnitude; all orderings): header-hunt over 260
transforms each (raw/invert/reverse/nibble-swap/XOR 0x00-0xFF + gunzip) and LP base-29
scoring with the calibrated project scorer.

- Header-hunt: 0 hits across all 12 x 260 transforms. No gunzip success.
- LP score: best -7.42 (229 mask-magnitude raster). Threshold -5.2, English ~-4.0, noise
  floor ~-7.5. Every stream sits at the noise floor, ~3 below English. No plaintext, no key.

## 5. Controls (false-positive guard)

- Positive (reader works): OutGuess-embedded a known message into a clean carrier and
  extracted it BYTE-EXACT (roundtrip_ok true). Pipeline recovers real payloads.
- Negative (not reading noise): synthetic clean JPEG, chroma-neutral strokes. Interior
  |R-G| = 0.0002, mask px (|R-G|>5) = 0 -> detector fires NULL on clean input. Its
  full-interior LSB-R entropy = 7.957, ones 0.497 = the JPEG-LSB bias baseline (LSB planes
  are ~random by nature; entropy near 8 / ones near 0.5 is expected noise, not data).
- In-corpus control 167: 338 anomaly px vs 32K/46K -> ranked ~100x below targets, yet its
  LSB planes are indistinguishable from targets (all ~7.4) -> LSB channel is noise for all.

Bias baseline reported: clean-JPEG LSB entropy ~= 7.96 (ones 0.497); in-corpus interior LSB
entropy ~= 7.4 (ones ~0.38, pulled down by dark-ink R-channel saturation). Neither is a
payload signature.

## Files
- mask.py -> mask_stats.json, mask_*.npy, RmG_*.npy, interior_*.npy, rgb_*.npy
- bitstream.py -> bitstream_results.json, bits_dl_{107,229}_*.bin
- controls.py -> controls_results.json, clean_neg.jpg, pc_stego.jpg, pc_extract.txt
- crypto.py (header-hunt + LP score)

## Reproduce
```
cd analysis/round29/L3-chroma-bitstream
PYTHONUTF8=1 python3 mask.py && python3 bitstream.py && python3 controls.py && python3 crypto.py
```
Depends on target JPEGs in analysis/armada_osint/artifacts/ and the LP scorer in src/lp/ + analysis/.

## Relationship to prior work
- armada_osint/t1_chroma + redrune identified the red as saturated #C80000 rubrication and
  killed it as a rune SELECTION key. This lane confirms, from the raw pixel/bit-plane side,
  that the same red is a constant DC offset and thus cannot be a bit-plane payload either.
  The deferred "attack the modified plane as its own bitstream" branch is CLOSED as a
  documented null.
- armada_osint note on dl_1033: its visible chroma is the OutGuess embedding of the
  already-known keyless 2013 RSA message; no external key. Consistent.
