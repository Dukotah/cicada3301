# Campaign IV After-Action Report — LP2 (Liber Primus, pages 0–55)
## Structure & Foundation

_Run 2026-06-21. 8 agents (~0.35M tokens). Four thrusts: independent template-matched
transcription, deep structural fingerprint, per-page polymorphic attack, original-hi-res image
hunt. Artifacts under `analysis/structure/`._

## 1. Bottom line

Nothing broke — but this campaign produced the most important *understanding* yet. The single
real anomaly (the doublet deficit) is now **fully characterized as a uniform, global,
memoryless soft no-adjacent-repeat rule** over an otherwise perfectly random stream. Critically,
that structure **mechanistically rules out a published-text running key** (a real English
running key would itself inject ~3.3% doublets — which are absent), explaining why three
campaigns of keytext-hunting failed: wrong *mechanism*, not wrong *text*. Two standing
assumptions were also corrected: **relikd IS the original onion7 master (byte-identical), not a
re-host**, and **krisyotam segment 55 is the already-solved AN END page** (a scoping bug).

## 2. Independent transcription (template matching)

- **Matcher accuracy on solved pages: 69.5%** — below the ~90% gate. No metric variant cleared
  70% (NCC 0.70, binarized 0.62, Hamming 0.64). Bottleneck is **segmentation/alignment**, not the
  matching metric.
- **Verified disagreements with canon: 0.** The 236 raw disagreements are dominated by the
  matcher's own ~30% error rate (degenerate "many runes → H" alignment-drift artifacts; cropping
  the top hits shows clean runes mislabeled). Not systematic ciphertext errors.
- The pipeline is built and runs over all 56 pages (`template_transcription.txt`, flagged LOW
  CONFIDENCE) but **cannot currently catch propagated rtkd errors** without a trained shape-model
  classifier (double-stem runes D/OE/M, connected pairs, decoration handling).
- **Canon is neither corroborated nor refuted by an image-independent reading.** page 24:172
  (AE vs A) remains unresolved — but now known to be **interpretive, not resolution-limited**
  (the master glyph is razor-sharp); it needs a careful human re-read, not a better image.

## 3. Structural fingerprint (the real result)

The doublet deficit is the **only** structure, now fully characterized:

- **Uniform across all 29 runes, diagonal-only.** Every doublet cell is suppressed (~5×, ~80% of
  expected doublets removed; measured 0.678% vs ~3.45%); the 20 most-suppressed cells in the
  841-cell bigram table are exactly the 20 doublets. The entire off-diagonal table is
  indistinguishable from perfect independence (χ²=810 vs df=812). **No forbidden pairs.**
- **No periodicity, no higher-order structure.** Doublet positions flat mod all M; inter-doublet
  gaps geometric/memoryless; autocorrelation IoC×N = 1.000 at every lag 2–30 (only the lag-1 hole
  deviates); per-page counts Poisson. Trigram IoC flat, no 8-gram repeats, inter-page
  shared-keystream null (0.0344 vs chance 0.0345), gematria prime-value sums uniform mod
  {3,7,29,109,1033,3301}. The one "significant" positional signal is a physical line-wrap artifact.
- **Significance:** z = −16.9 vs marginal-preserving permutations, p < 5e-4 (never reached in
  2000 shuffles). Real and overwhelming — but confined entirely to the diagonal.
- **Mechanism implied:** a SOFT (not hard) no-adjacent-repeat rule (soft-rejection sampling from
  the empirical unigram distribution reproduces the exact fingerprint; ~20% residual = tolerated
  repeats). Consistent with an **OTP / long running-key whose keystream was filtered to avoid
  producing two identical output runes in a row**, or a by-hand "don't write the same rune twice"
  rule. **Ruled out:** short-period polyalphabetic (no period at any lag), homophonic/columnar
  transposition (would leave off-diagonal/n-gram structure — none), and **published-text running
  key** (would inject ~3.3% doublets — absent). Ciphertext-autokey matches the *rate* but is
  already brute-forced to gibberish.

**Net: the text is statistically a one-time pad with a single engineered hole. The deficit is
fully explained and offers no further internal purchase without the externally-held key.**

## 4. Per-page polymorphic attack

Every page 0–54 attacked independently with the full known-Cicada toolkit (Atbash, shifts,
exhaustive Vigenère L1–4 ±atbash both signs, hill-climb L4–12, interrupter beam, prime/totient/
prime-1 keystreams with offset search, ciphertext+plaintext autokey). Selftest + validate.py
passed each run.

| Range | Hit? | Best | Page | Note |
|---|---|---|---|---|
| 0–13 | No | −6.643 | 7 | gibberish |
| 14–27 | No | −6.628 | 22 | gibberish (vigauto −6.27 discarded as metric-overfit) |
| 28–41 | No | −6.541 | 32 | gibberish |
| 42–55 | "Yes" | −5.282 | 55 | **already-solved AN END page — not a new break** |

No genuinely-unsolved page reached the −5.5 investigate threshold. The per-page hope (one page
crackable in isolation) is **false for the entire 0–54 range**. The page-55 "hit" correctly
re-solved the known AN END page (prime-1 key) — a good sanity check that the rig works.

## 5. Hi-res images — relikd IS the original

**No better originals exist.** krisyotam's `original-onion7/{0,24}.jpg` ("raw from the onion7
hidden service") are **MD5-identical** to relikd. All sources are 2400×3600 @ 400 DPI; the files
are **Ghostscript/MuPDF vector renders** (ICC = "Artifex Software 2011"), so glyphs are crisp by
construction. No TIFF/PNG/PDF master exists in any mirror; archive.org is the lowest quality.
**The prior assumption that relikd is a re-encoded re-host is WRONG — it is the byte-for-byte
master.** Image quality is not a limiting factor for transcription.

## 6. Newly eliminated / corrected (append to do-not-redo)

**Eliminated:** per-page polymorphic battery on pages 0–54; template-matching transcription from
the 2400×3600 images (≤69.5% without a trained classifier); searching for higher-res originals
(none exist); off-diagonal bigram structure, n-gram repeats, periodicity (lags 2–30), inter-page
shared-keystream, gematria prime-value modular sums, word-boundary positional bias — **all null.**

**Corrected facts:** (1) relikd = onion7 master, byte-identical — no cleaner original to recover.
(2) Images are vector renders — an unpublished vector source is the only thing that could be
sharper. (3) The doublet deficit is uniform/diagonal-only/memoryless/soft — not a new attack
surface. (4) krisyotam segment 55 = the already-solved AN END page; the genuinely-unsolved set is
0–54.

## 7. Honest verdict — it is time to call LP2 unsolvable by available means

After four campaigns (~48+ approaches), **there is no warm thread left inside the ciphertext.**
Brute-force cryptanalysis, published-text running keys, per-page polymorphic methods, structural
fingerprinting, and image re-transcription have all returned honest negatives. The one real
anomaly is fully explained as a uniform soft anti-repeat overlay on an OTP/long-running-key
cipher — precisely the structure that offers **no internal purchase** without the externally-held
key.

Remaining threads, all external to pure cryptanalysis, none high-probability:
1. **The key is exogenous and not public.** If LP2 is a true OTP it is information-theoretically
   unbreakable from the ciphertext alone — cryptanalysis cannot win this.
2. **One definitive human-grade re-transcription** of the existing master (verify canon, resolve
   page 24:172). Tractable, worth doing once — but verification, not a break.
3. **Monitor for external key material** (a new Cicada release, a community key drop).

**Plain statement:** the text is statistically a one-time pad with a single engineered hole.
Absent a new *external* input, no further internal cryptanalysis on the canonical ciphertext is
expected to succeed. Further brute-force/running-key/per-page work should be considered closed.
