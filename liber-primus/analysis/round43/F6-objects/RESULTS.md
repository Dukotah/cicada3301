# R43 / F6 — RESULTS: the open internal objects, joined

Ran 2026-11-03 per `PREREG.md` (written first; no threshold moved after data).
Runners: `run_f6.py` (parts a, b, c-xor, d → `f6_results.json`),
`run_f6_keystream.py` (part c keystream → `f6_keystream_results.json`).

**Headline: NEGATIVE on every prereg'd hit rule.** The only detector fires are the
pre-registered PGP-tag magic, which post-hoc null calibration shows fires on **32.8 % of
random 256-byte strings** — observed fire rates (12/36 and 2/4) are exactly chance.
One genuinely new side fact fell out of (d): the three T4 blobs decode to **complete,
valid 2400×3600 RGB JPEGs** and blob2/blob3 are the *same image to 95.2 % of pixels*
(diffs localized to a central bbox) — a refinement of the already-closed R29-L2
identification, not a new channel claim.

## Objects as extracted (shas in `f6_results.json["objects"]`)

| Object | len | sha256 (first 16) | note |
|---|---|---|---|
| canon_256 | 256 | `3b9b07d9a26e6d55` | `analysis/pp49_51/canon_256.bin` |
| canon_256_decpref | 256 | `f42b7caa1e7df703` | variant |
| blob3301 (avowy pre) | 256 | `4f1cef871153b821` | marker `<!--3301-->`, hex starts `bf1d5574…` |
| blob761 (cu343 pre) | 256 | `05acf0d8e2ba7d85` | marker `<!--761-->`, hex starts `634292ba…` |
| blob1033 (fv7ly pre) | 256 | `d8c0f83cf91d0ded` | marker `<!--1033-->`, hex starts `87de5b7f…` |
| page-56 hash | 64 | `0911bf3c8cc3a73b` | canonical 128-hex from p56 "AN END" (KEY-HINT-RESEARCH.md) |

Each pre-page HTML contains exactly one ≥512-hex run (asserted), one marker comment.

## Control (mandatory, through the same glue)

`data/pride.txt[:256]` XOR blob761 → detector says NOT a hit (printable 0.371,
entropy 7.114, no magic); XOR again → recovered text fires D1 (printable 1.000),
D2 (run 256), D3 (entropy 2.936). `control.valid = true`. The pipeline sees plaintext
when plaintext is there.

## (a) Payload-as-ciphertext vs the onion blobs — NULL

36 outputs ({2 payloads} × {3 blobs} × {fwd, byte-reversed} × {XOR, ADD, SUB mod 256}):

- D1 printable: max **0.410** (bar 0.85) — none fire.
- D2 run: max **8** bytes (bar 40) — none.
- D3 entropy: min **7.07** bits/byte (bar ≤ 6.00) — none; all 36 sit in the random band.
- D5 ASN.1: none parse.
- D6 mod-29 screen (panel-R36): max pmax **3.223** vs free bar **13.02** — nowhere near.
- D4 magic: **12/36 fired, all of them the PGP-packet-tag check and nothing else.**
  Post-hoc null calibration of the *fixed* detector (100 000 random 256-byte strings,
  seed 43): `pgp_ok` fires at **0.3277**; 12/36 = 0.333. Exactly the chance rate.
  No fired output passes any corroborating detector. **Verdict: all 12 are false
  positives of a weak detector; (a) is null.**

## (b) The blobs themselves — not RSA moduli; unrelated to each other

| blob | bitlen | parity | small factors < 10⁶ | verdict |
|---|---|---|---|---|
| blob3301 | 2048 | odd | 13 | divisible by 13 ⇒ **not a well-formed RSA modulus** |
| blob761 | 2047 | even | 2, 17 | even ⇒ **not a modulus** |
| blob1033 | 2048 | even | 2, 3, 17, 4273, 338761 | **not a modulus** |

- GCD of each with {3301, 503, 509, 761, 1033, 503·509, 503·509·3301}: **all 1.**
  No arithmetic tie to the marker numbers or the 503/509/3301 structure.
- Pairwise GCDs: 1, 1, 34 (= 2·17, the shared trivial small factors — chance-level).
- Pairwise XOR: entropy 7.09–7.25, printable 0.31–0.34, shared prefix/suffix **0 bytes**.
- `armada_osint/keys.txt` holds no modulus/exponent, so the prereg'd conditional
  sig^e-mod-n test could not run (noted, not skipped silently).

**Bound:** the three blobs are *consistent with* RSA-2048 signatures (a signature is an
arbitrary residue < n; parity/small factors prove nothing against that) or with random
bytes; they are definitively **not** moduli, and they show **no relation to each other**.

## (c) Page-56 hash as key — NEGATIVE

- **Keystream over the 55 unsolved pages**: keys = 64 hash bytes mod 29 and 128 hex
  nibbles mod 29; grid {±1} × {atbash 0/1} × {offset 0..63} = **512 decodes/page**,
  **28 160 total**, adjudicated with panel-R36 against the standing free-null
  `bars_v3`. **0 / 55 pages cross.** Observed global best: pmax **4.596** (page 6,
  byte key, sign −1, atbash, off 39) vs its bar **11.27**. Language scoring here is the
  repo's standing instrument + standing bar (same glue as R42-C3), not an ad-hoc screen.
- **Hash ×4 XOR canon_256 / decpref** (fwd + reversed): 4 outputs; 2 fired the same
  32.8 %-chance PGP-tag detector and nothing else (printable ≤ 0.37, entropy ≥ 7.23,
  mod-29 pmax ≤ 1.09). **Null.**

## (d) T4 blobs — identified (reproduces R29-L2, with two new refinements)

R29-L2 (`analysis/round29/L2-blob-cross/FINDINGS.md`) already classified T4 as the
"KNOWN image chain (gzip'd JPEG under 0xFF)". F6 reproduces that and pins it down:

- The committed `_flip` variants are the **bytewise complement** (verified
  `flip[i] == blob[i] ^ 0xFF` on stride samples; not byte-reversal).
- `T4_blob1_flip` = gzip, decompresses at offset 0 to 3 010 703 bytes whose sha256
  `8ebf4c48…` **equals both** the committed `T4_blob1_gunzip.bin` **and**
  `onions_ibotpeaches/avowy_post_gzip_inner_2400x3600.jpg`.
- **New:** `T4_blob2_flip`, `T4_blob3_flip`, and the blob1 inner all fully decode in
  PIL as **valid 2400×3600 RGB JPEGs** (complete streams, no truncation error).
- **New:** blob2 vs blob3 images agree on **95.20 % of pixels**; the 4.80 % that differ
  are confined to bbox y 640–2815, x 591–1791 with mean |Δ| = 484/765 — i.e. different
  *image content* in the central region (portrait variants), not LSB-style noise.
  blob2 vs blob1-inner differ on 31.6 % of pixels.
- Whole-file entropies 7.40–8.00; windowed 4 KiB entropy min −0.0 (blob2's known
  all-0xFF run @ ~348 k, per R29-L2) — all consistent with JPEG/gzip, now explained.
- Decompression sweep elsewhere: 0 successes at any other header offset (gzip/zlib/bz2/xz,
  ≤10 000 offsets per format per blob); interior "gzip magic" counts (23–95 per blob) are
  2-byte false positives. No printable run reached the 1 KiB base64/85 threshold.
- **T2/T3:** no `T2*/T3*.bin` exists in `artifacts/` (prereg noted). Per R29-L2, T2_2jpg
  and T3-folly are the still-open *true opaque* blobs — out of this lane's object list.
- Bookkeeping: `f6_results.json["d"]` carries `T4_blob1_gunzip.bin` twice (glob + the
  explicit section); identical rows, harmless.

## Verdict

Every prereg'd hit rule returns null: the pp49–51 payload is not the onion blobs'
XOR/ADD/SUB plaintext in either byte order; the blobs are not RSA moduli and are
mutually unrelated; the page-56 hash is not an additive mod-29 keystream for any of the
55 unsolved pages at the standing bar (0/55, best 4.60 vs 11.27) and not an XOR key for
the payload. T4 is closed-as-identified (images), with the blob2/blob3 pixel-diff region
recorded as a cheap *exploratory* follow-on (post-hoc, outside this prereg).
