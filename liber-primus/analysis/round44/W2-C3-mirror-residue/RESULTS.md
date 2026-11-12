# W2-C3 — MIRROR BYTE RESIDUE — RESULTS

_Round 44 wave-2, 2026-11-09. PREREG sha256 `484683ca…` stamped in `run.log` before first
execution. All runs pure python3, no network. Scripts in `scripts/`, raw JSON in `results/`._

## Verdict line

**MEASURED (inventory identified) + NEGATIVE (adjudication).** The residue channel is now
byte-accounted end-to-end: of the 13 trailing objects + 9 unparseable files + 3 true-opaque
blobs, **everything is identified except 13 bytes** (the terminal non-periodic bytes of the
Outt.png trailer — below the 120-symbol adjudication floor, unique in the corpus, from a
community-wiki file). No bar-crosser anywhere. **Nothing is flagged for oracle.**

## Positive controls (both passed BEFORE any real target; `results/plant.json`)

- **PC1 (container plant, the cell's own glue):** gzip(known sentence) → complement →
  byte-reverse → appended after IEND of a copy of the real Outt.png. Pipeline recovered it
  (`revxff` transform, offset 0) and returned the exact sentence. PASS.
- **PC2 (adjudicator plant):** bytes with b mod 29 = rune indices of a 240+-rune English
  passage through the identical map+panel glue: pmax **30.38** vs bar **14.805** → PASS.
  Calibration: 200 urandom blobs through the same glue, max pmax **3.42**, **0/200** over
  the bar.

## 1. The 13 TRAILING-DATA.json rows — all verified on disk (13/13 file-sha and
trailer-sha match) and now identified (`results/inventory.json`)

| Object (trailer sha16) | Trailer | Identification (this cell, byte-exact) |
|---|---|---|
| `10.jpg` == `onion6.jpg` (8c90214a) | 3,486,295 B | **Appended-JPEG chain: exactly 11.jpg + 12.jpg + 13.jpg** (= Pg2/Pg3/Pg4 = onion6 pg2/pg3/pg4), three complete JPEGs, sha-matched, zero residue |
| `ONION_2_JPG.jpg` (325ee77f) | 1,651,773 B | = **complete 01.jpg** (sha-exact) **+ the Huh2 trailer** (below). ONION_2 = 01.jpg ∥ reverse(02.jpg) |
| `Huh2.jpg` ×2 copies (0d7a3ec5) | 175,159 B | **Complete byte-reversed 02.jpg (= Intus.jpg)**: reversed trailer walks SOI→EOI with 0 leftover bytes, decodes 2400×3600, sha-exact match to 02.jpg. **NOT truncated — the R43 blind "truncated?" question is answered: no gap exists** |
| `05.jpg` == relikd `0_wisdom.jpg` (3814d8b9) | 336,713 B | **360-B block + byte-reversed copy of the host page's own image** (reversed JPEG = 05.jpg/0_wisdom image-prefix sha-exact, 2400×3600). The 360-B "gap": hex-ASCII encoding of the known 1033 magic square — decoded: `272 138 341 131 151 / 366 199 130 320 18 / 226 245 91 245 226 / 18 320 130 199 366 / 151 131 341 138 272` (every row/col sums 1033). **Zero unexplained bytes.** The blind agent's "72,700-B truncated reversed JPEG" claim is REFUTED (mis-measurement; the reversed JPEG is complete at 336,353 B) |
| `Outt.png` (044a0b54) | 13,592 B | **NOT a palindrome** (blind claim refuted: palindrome core = 0 bytes). Structure: **13,579 B of an exactly 15-byte-periodic carrier** (unit `df7d35d37df4d74d…`, true period 30 bits = 5-bit groups `27,29,30,19,11,20` repeating; 29/30 are not valid rune indices) **+ 13 terminal non-periodic bytes** `7101f04fdc61fd247513e235a2`. The unit and the 13 bytes occur nowhere else in the corpus. Provenance: community-wiki upload (wikia, cb=2014-01-18). The carrier carries zero information beyond its unit; the 13-byte residue is below every instrument floor (too short for panel adjudication; no magic under id/rev/xff/revxff) |
| `signed-payloads/2014-01-onion5-liber-primus.jpg` (2093ade6) | 10,923 B | **Concatenation of onion-5v2 site files: complete Eyebyext.jpg (= onion 5v2/b.jpg, 1,635 B, sha-exact) + complete c.mp3 (= onion 5v2/c.mp3, 9,288 B, byte-identical)**. Zero residue |
| `-016477-.jpg` (da265589) | 424 B | Firefox **necko cache metadata** (visible `necko:classified … request-method GET response-head HTTP/1.1 200 OK`, wikimedia URL) — a saved-from-browser-cache artifact, not a payload |
| `1CcV1.jpg` ×2, `Final.jpg_2012` (f9c65241) | 61 B | The known 2012 first-step TIBERIVS trailer (already ledgered history; confirmed byte-identical across all 3 copies) |
| Blake `…Human_Abstract.jpg` (5ae7e6a4) | 3 B | `ff ff ff` padding |

## 2. The 9 unparseable files — all identified as TRUNCATED mirror copies

All 9 fail the marker walk by **running past EOF** (JPEGs: entropy scan past EOF; PNGs: no
IEND) and PIL confirms "image file is truncated" on every one. None contains residue — the
failure mode is missing tail bytes, not extra bytes. Notables: `Hadyn…/54.jpg` is a byte-
exact **prefix** (212,992 B = 13×16 KiB — a cut-off transfer) of the complete onion7
54.jpg; wiki `53.jpg`/`54.jpg` are wikia **re-encodes** (APP2/ICC header at byte 3) that
were themselves truncated in the mirror — the onion7 masters in-corpus are complete;
cijhho `04.jpg` is a single 2400×3600 JPEG (one SOI, no appended chain in the surviving
bytes) missing its last few dozen bytes. The other five are community wiki images
(screenshots/overlays/Pintogram), not author artifacts.

## 3. T2_2jpg / T3-folly / canon_256 — uncovered-transform battery
(`results/t2t3_battery.json`; identity pins passed: T2 sha `35d31e61…`, folly md5
`0c7d18e8…`, promoted canon)

Ran ONLY what R29-L2/R30-B1/R43-F6 did not: all-offset magic + decompression under
id/rev/xff/revxff, plus rot5, rot6, nibble-swap, per-byte bit-reverse, delta, cumsum,
xor-index; windowed entropy; period/palindrome scan. Result: **no magic hit, no period, no
palindrome core**; T2 windowed entropy 7.954–7.960, folly 7.938, canon 7.170 (256 B, no
randomness claim per PREREG §5). The 31 brute raw-deflate "hits" (outputs 64–736 B with
LZ77 self-repeat heads) are at the measured noise floor: **urandom calibration produced
15/31/23 hits per same-size blob** under identical criteria (`results/brute_calibration.json`)
— the real blobs' 19/11/1 are indistinguishable from noise. R29-L2's "true opaque" verdict
extends to this transform family.

## 4. Adjudication — direct symbol-mapped reads (`results/adjudication.json`)

27 decodes (T2, folly, canon × {id,rev,xff} × {mod29, 5-bit-skip, pair-mod29}),
panel-R36, bars fixed at N_CAP=400: L=120: 11.136, L=240: 14.805, L=729: 19.198.
**Best vs bar: pmax 3.285 vs 11.136** (canon_256|rev|pair_mod29, L=120); every other row
≤ 2.2. Zero degenerate rows, **zero crossers**. N actual = 27 ≤ 400. The Outt carrier was
excluded as degenerate-by-construction (period-6 symbol stream, mds ≤ 6); its 13-byte
residue and the 61-B/424-B/3-B trailers are below the 120-symbol floor (not_covered).

## 5. Coverage / not_covered

**Coverage:** 13/13 trailing rows sha-verified and identified under {id, rev, xff,
rev∘xff} at all offsets (+ full extension family on the 3 opaques); appended-image chains
walked recursively and matched sha-exact against a 1,024-sha corpus index; the 05/0_wisdom
and Huh2 trailers byte-accounted to zero unexplained bytes; Outt trailer decomposed
(carrier + 13 B); 9/9 unparseable files classified (all truncation, no residue); 27
symbol-mapped panel decodes, 0 crossers; plants PC1+PC2 passed with 0/200 calibration
false-fires.

**not_covered:**
1. The 13 terminal Outt bytes (`7101f04fdc61fd247513e235a2`) remain unidentified —
   below the 120-symbol adjudication floor and matching nothing; low prior (community-wiki
   file, likely upload corruption of a periodic pad/pattern, but that is a guess, not a
   measurement).
2. B-09's items 6–9 proper (per-onion HTTP/port anomalies, whitespace re-audit at scale,
   2012 "7 images" endpoint, Columbus GA Shamir onion) require network —
   UNAVAILABLE-BY-PREMISE here; B-09's blob half is what this cell measured.
3. Keyed-cipher constructions over T2/folly/canon (R30-B1's not_covered governs); AEAD/KDF
   keys; registers outside panel-R36; non-linguistic structured payloads (keys,
   coordinates) in any residue.
4. Any trailer that may have existed past the truncation point of the 9 cut files (the
   bytes are absent from every in-corpus copy; for 53/54 the complete onion7 masters have
   no trailer — measured here — so this residual applies to the wiki re-encodes and
   cijhho 04.jpg only).
5. Image-content legs explicitly left to their owning rows: pixel/DCT stego (R8/R29-L1/
   R30), the F6 blob2-vs-blob3 diff region, decoded-image semantics.

**reopens_if:** the 13 Outt bytes match a future artifact; an off-corpus complete copy of
cijhho 04.jpg (or the wiki re-encodes) surfaces with bytes past the truncation point; a
network-capable lane takes up B-09 items 6–9.
