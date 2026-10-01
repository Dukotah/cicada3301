# L2-blob-cross — two-time-pad / crib-drag attack on the opaque high-entropy blobs

**Round 29 "active attack" armada, Lane L2.**
**Verdict: CLEAN NEGATIVE.** No two blobs share a pad. No blob is an OTP pad over any
known Cicada plaintext. No hidden second message, no shared keystream. This closes the
deferred lane flagged by prior completeness critics ("test opaque blobs against EACH
OTHER + as OTP pads for KNOWN Cicada plaintexts; cross-artifact XOR").

This was a **Kerckhoffs / two-time-pad crib-drag attack**, not rune cryptanalysis. If any
two of these blobs were ciphertexts under the same pad, XOR(c1,c2) = XOR(p1,p2) would
collapse entropy and leak English structure recoverable by crib-drag. It does not. If any
blob were itself an OTP pad laid over a known plaintext, blob XOR plaintext would yield a
structured/readable keystream. It does not.

Artifacts:
- `attack.py` — the full rig (3 batteries + controls). Re-run: `python3 attack.py`.
- `run_full.log` — full output (pair matrix, pad-over-plaintext table, self-structure).

---

## Positive/negative control (run BEFORE any claim — required by doctrine)

The crib-drag detector was **control-validated**. A naive "all-alpha window" gate produced
false positives on random data (birthday paradox on short windows), so the detector was
hardened: it slides only long space-bounded cribs (" the ", " cicada ", " within ", ...)
and counts a hit only when the recovered fragment is fully printable-alpha AND contains a
common English trigram/word.

| Control | Entropy | IC | crib hits | fires? |
|---|---|---|---|---|
| POSITIVE — two English msgs under a shared random pad (c1^c2 = p1^p2) | 5.462 | 0.02596 | **31** | YES |
| NEGATIVE — two independent random strings | 7.504 | 0.00377 | **0** | NO |

DETECTOR VALID -> PASS. Positive control recovered real fragments (" and ", "shes ",
"ts a "). The detector fires on genuine English-over-English and stays silent on noise.

---

## Blob inventory (with self-structure verdict, Battery 3)

| Blob | Bytes | Entropy | IC | header_hunt | Nature |
|---|---|---|---|---|---|
| **T2_2jpg** (stage04 rev-index extract) | 7524 | 7.978 | 0.00389 | none | **True opaque** — random-like, no header, no period |
| **T3/folly/folly_snap2/wisdom** | 3368 | 7.938 | 0.00393 | none | **True opaque** — 4 names, ONE file (md5 0c7d...) |
| **canon_256** (pp49-51 base-60) | 256 | 7.170 | 0.00389 | none | **True opaque** — random-like, no header |
| T4_blob1 (.htaccess) | 2.53 M | 7.998 | 0.00392 | **GZIP @ xor0xFF** | KNOWN image chain (gzip'd JPEG under 0xFF), closed |
| T4_blob2 (.htaccess) | 2.79 M | 7.766 | 0.00874 | **JPEG @ xor0xFF** | KNOWN image chain; all-0xFF run @ 348k |
| T4_blob3 (.htaccess) | 1.82 M | 7.403 | 0.01039 | **JPEG @ xor0xFF** | KNOWN image chain; strong lag-4 autocorr (JPEG) |
| T1_onion3/nokey_dl_1033 | 1498 | 6.010 | 0.01629 | **PGP/PEM raw** | ASCII PGP text; 2 names, ONE file (md5 5974...) |
| lpc02_out | 2899 | 5.214 | 0.03630 | **PGP/PEM raw** | ASCII PGP text (-----BEGIN PGP SIGNED MESSAGE) |
| t5_nokey | 1136 | 5.974 | 0.01698 | **PGP/PEM raw** | ASCII PGP text |

**Two duplicate groups found and de-aliased:**
folly.bin == folly_snap2.bin == wisdom.bin == extracts/T3.bin (md5 0c7d18e8...) and
T1-onion3...bin == nokey_dl_1033.bin (md5 597414fb...). Reduces the real distinct-blob set
to: {T2_2jpg, T3-folly, canon_256, T4_blob1/2/3, T1_onion3, lpc02_out, t5_nokey}.

**Three of the "opaque blobs" are not opaque at all** — the four T4 blobs and the four
PGP-text blobs (T1/lpc02/t5/nokey) self-identify: T4 = the known-closed .htaccess
gzip/JPEG image chain (all reveal GZIP/JPEG under a single 0xFF XOR), and the low-entropy
group are literal ASCII PGP messages. Only **T2_2jpg, the T3-folly file, and canon_256**
are genuinely random-by-every-test.

---

## Battery 1 — cross-XOR pair matrix (all 78 unordered pairs)

Every pair XOR'd at offset 0; unequal-length pairs additionally slid short-over-long
(32-step sweep) looking for an entropy trough. Full table in run_full.log. Summary:

- **Byte-identical pairs -> XOR = 0.00 entropy, IC = 1.0.** The two md5-duplicate groups
  above. Correctly flagged as identical files, not a shared pad.
- **The only "low-entropy" non-identical XORs are the ASCII-text blobs** (lpc02_out,
  t5_nokey, T1_onion3): H~5.8-6.8 with printable~0.70. Trivial — ASCII^ASCII stays in the
  printable band. Their validated crib count is a handful of isolated garbage fragments
  (e.g. " the " -> "g NTH"), NOT contiguous English. No shared pad.
- **Every pair involving a true opaque blob** (T2_2jpg, T3-folly, canon_256) XORs to
  **entropy 7.14 - 8.00, IC ~ 0.0039 (random floor), validated crib hits = 0.** T4-vs-T4
  and T2-vs-T4 all sit at H = 7.97 - 8.00. The 44-447 raw crib counts on the multi-MB
  T4xT4 pairs are pure birthday noise (44 hits / 2.5 M positions << the positive control's
  31 hits / 400 positions) and vanish as isolated non-contiguous fragments.

**No pair of blobs was encrypted under the same pad.**

---

## Battery 2 — each blob as an OTP pad over known Cicada plaintext

Plaintexts: the five solved LP pages (A WARNING, SOME WISDOM, both KOANs, WELCOME) plus
"FOR EVERY THING THAT LIVES IS HOLY". Each plaintext window slid across each blob; the
lowest-entropy alignment kept and inspected. Full table in run_full.log.

Apparent "HIT" rows all fell to inspection — **every one is an artifact, none survives as
readable text**:

- **ASCII-text blobs** (lpc02_out, t5_nokey, T1_onion3, nokey_dl): pr~0.86-0.98, run up to
  158. Trivially expected — these blobs ARE printable text, so text^text stays printable.
  The recovered "keystream" is unreadable garbage, e.g.
  lpc02_out ^ KOAN -> "wz-wz"|#(!w +stvc-u,...". No English, no PRNG, no second message.
- **T4_blob2 @ offset ~348520**: H~4.0 for every plaintext at the same offset. Cause: the
  blob contains a solid **500-byte run of 0xFF** there. 0xFF^plaintext = inverted plaintext
  — reveals nothing but the plaintext you put in. Blob self-structure, not a pad.
- **T4_blob3 @ offset 0**: H~4.6, pr=0.06. The bytes are JPEG artifacts
  (\x00'\x00\x1f\xff\xef...), not text. Low entropy from the JPEG's own byte skew.
- **T2_2jpg, T3-folly, canon_256** (the true opaque blobs) ^ every plaintext ->
  **H = 7.2 - 7.7, pr ~ 0.35-0.47, run <= 7, no repeated block.** Indistinguishable from
  XOR-ing a plaintext into random. No structured keystream emerges.

**No blob is an OTP pad over any known Cicada plaintext.**

---

## Battery 3 — self-structure (autocorrelation / repeated-block / header-hunt)

- **True opaque blobs (T2_2jpg, T3-folly, canon_256):** no repeated 8-block, no
  autocorrelation peaks (T2/T3 empty; canon_256 only noise-level 0.02), no magic header
  under raw / reverse / xor-0xFF / rotate(1,2,3,4,7) / base64. Single high-entropy stream,
  no period, no concatenation seam — consistent with strong ciphertext or a genuine random
  pad, and inconsistent with a reused/structured keystream.
- **T4 blobs:** JPEG/GZIP under 0xFF (known chain), plus repeated blocks and lag-4 period
  (blob3) — structured image data, confirming they are NOT random pads.

---

## Verdict per blob

| Blob | Shared-pad w/ another blob? | OTP pad over known plaintext? | Self-structure hidden header? |
|---|---|---|---|
| T2_2jpg | NO (H 7.9-8.0 vs all) | NO (H>=7.2) | NO |
| T3-folly (=folly/snap2/wisdom) | NO (identical to its 3 aliases only) | NO | NO |
| canon_256 | NO | NO | NO |
| T4_blob1/2/3 | NO (H 7.97-8.0) | NO (dips = 0xFF-run / JPEG-skew artifacts) | Yes — JPEG/GZIP under 0xFF (known, closed) |
| T1_onion3 / lpc02_out / t5_nokey | NO (text^text only) | NO (garbage keystream) | Yes — raw PGP/PEM ASCII |

## What this closes and what it does NOT touch

**Closes:** the deferred cross-artifact XOR / two-time-pad / OTP-pad-over-known-plaintext
lane, with a control-validated detector and an honest clean negative. None of these blobs
is the other half of a two-time-pad, none pads a known Cicada plaintext, and the three
genuinely-random ones (T2_2jpg, T3-folly, canon_256) show no reusable keystream structure.

**Does NOT touch (out of scope, unchanged):** the LP2 runes (OTP-excluded per doctrine);
whether T2_2jpg / T3-folly / canon_256 are strong single-key ciphertext under some
*external* key never seen here (this lane can only detect pad *reuse* / *known-plaintext*
relationships; a one-time single-use pad is information-theoretically undetectable by
crib-drag — correctly, we make no claim about it).
