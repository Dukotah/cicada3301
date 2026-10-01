# Round 30 — "The Rendered Book" Special Armada — SYNTHESIS (2026-09-28)

8 active attack lanes fanned out from the Round-29 discovery that the LP2 master is a machine-rendered
PDF. Each lane control-gated and then adversarially verified refute-by-default. **No verifier downgraded
any lane.** Trust anchors green throughout (validate.py 5/5, ledger unsound=0, now 171 entries).

## Headline

**The needle did not move on the puzzle.** No plaintext, no new decode avenue; the OTP-class wall on
pp0-54 and the pp49-51 payload stands untouched and is now *reinforced*. Two POSITIVE verdicts were
upheld, but both are process/bookkeeping positives, not solving positives.

## Per-lane verdicts (verifier-adjusted; none downgraded)

| Lane | Verdict | Result |
|---|---|---|
| A1 font | NULL (HIGH) | Runes are a deterministic vector font — same rune renders byte-identically everywhere; the imagined glyph-variant channel does not exist |
| A2 sub-pixel | NULL (HIGH) | No hidden channel in baseline/advance/kerning/jitter; ~2px detection threshold on 400dpi q92, nothing near it |
| **A3 PDF forensics** | **POSITIVE (HIGH)** | ICC profile **byte-identical to Ghostscript 9.06 Artifex srgb.icc** → toolchain narrowed to GS 9.01-9.15; process-attribution only |
| B1 blob crypto | NULL (HIGH) | External-key symmetric battery (AES/RC4/Blowfish/DES/3DES × ~37 keys) on the 3 random blobs: 0 hits |
| B2 RSA/GPG | NULL (HIGH) | canon_256/folly/2.jpg carry no RSA modulus/ciphertext or OpenPGP structure; canon_256 is even with small factors |
| C1 art | NULL (HIGH) | No attributable individual hand; art = processed public-domain imagery + generic cipher-nav line work |
| D1 ledger audit | PARTIAL (audit) | Ledger soundness holds; 2 bookkeeping gaps found + fixed (B-10 discharged, R29-L1 mislabel) |
| **E1 render-reopen** | **POSITIVE (HIGH)** | 6 contested pp49-51 bytes resolved from the render → canon_256 **unchanged**, decpref variant refuted, open item CLOSED |

## The two upheld positives

- **A3** — the 2014 book's embedded ICC profile is a byte-for-byte match to Ghostscript 9.06's Artifex
  `srgb.icc` (MD5 `e409cef13cd06f6b371f6cddc8e31fcf`), refetched fresh and `cmp`-confirmed. This narrows the
  authoring toolchain to the GS 9.01-9.15 family (only 9.06 was byte-confirmed; the window is inference).
  Optimized Huffman = a deliberate `/Optimize` choice. No public source ever noted this signature. Yields
  zero plaintext but is a genuine, novel process-attribution.
- **E1** — all 6 previously-contested pp49-51 base-60 bytes adjudicated from the 400dpi render to exactly
  the reading `canon_256.bin` already held. Net: canon_256 unchanged (0 flips), the competing decpref
  variant refuted, the "6 contested bytes" open item CLOSED. Consolidation, not a break.

## Standing OTP verdict

**UNCHANGED and REINFORCED.** B1 extends the closure past ciphertext-only to the keyed-external-symmetric-
cipher hypothesis for the 3 random blobs (now also NULL). B2 confirms the pp49-51 payload is not a
self-contained number-theoretic / PGP object. E1 confirms canon_256 is the single canonical 2048-bit stream.

## Genuinely-new live threads (all off-repo OSINT / higher-fidelity-source hunts — none runnable in-corpus)

1. **Original source PDF/PostScript hunt.** A PDF source provably existed; recovering it would expose exact
   TJ kerning arrays (bypassing raster noise, A2) and the custom face's `/BaseFont` subset tag (which would
   NAME the typeface, A1). Off-repo archival hunt.
2. **Differential GS version pinning.** Build GS 9.05/9.07/9.10/9.14, render through the jpeg device with
   `/Optimize`, diff DQT + Huffman bytes to pin the single release. Strengthens attribution only.
3. **Art-attribution closure.** Wayback/authenticated fetch of the 402-gated "Art of Liber Primus" wiki
   page + true reverse-image search of the shroud/tree crops. If both null, C1 becomes final.

**Explicitly NOT live** (do not re-run): glyph-variant clustering (A1), sub-pixel positioning on current
JPEGs (A2), keyed cipher on the 3 blobs (B1), RSA/PGP structure (B2).

## Ledger

9 entries added (R30-A1/A2/A3/B1/B2/C1/D1/E1 + R29-L1-ONION-STEGO backfill); B-10 superseded by
R29-L1-ONION-STEGO. Total 162 → 171. by_status: measured 49, negative 47, audit 25, open 20,
partially-run 14, never-run 6, eliminated 5, superseded 3, in-flight 2. Unsound negatives: 0.

Nothing committed (owner pushes from Windows/GCM).
