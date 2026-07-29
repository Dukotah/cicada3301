# Liber Primus 2 (pages 0–54) — Five-Campaign Analysis Summary (2026)

A solver-facing summary of an exhaustive, adversarially-verified attack on the **unsolved**
Liber Primus pages, run as five multi-agent campaigns (~55 distinct approaches) against a
validated cryptanalysis rig. **Headline: LP2 was not broken** — but the analysis closed several
long-standing open questions and produced results the solver community does not appear to have.
If you are about to attack LP2, **read §5 (do-not-redo) first** — it will save you weeks.

The rig reproduces every known LP solve (`tests/validate.py`); all negative results below were
produced with a scorer that correctly finds DIVINITY/WELCOME at −4.34 (random ≈ −7.3, the
readable-English break threshold is ≈ −5.0). Per-approach detail and reproduction commands are
in `analysis/ARMADA-20-FINDINGS.md`, `analysis/foundation/CAMPAIGN-III-FINDINGS.md`,
`analysis/structure/CAMPAIGN-IV-FINDINGS.md`, and `analysis/stones/CAMPAIGN-V-FINDINGS.md`.

## 1. The verdict

**LP2 is a one-time-pad / long-running-key-class cipher whose key was never published.** It is
information-theoretically unbreakable from the ciphertext alone. Five campaigns of brute-force
cryptanalysis, published-text running keys, per-page polymorphic methods, number-theoretic
attacks, steganography, structural analysis, transcription verification, and OSINT all returned
honest negatives (best score ever: **−6.023**, no readable English on any front). The only
events that could change this are **external**: the actual key surfacing, or a new Cicada
release.

## 2. Five genuinely-new findings

1. **The doublet deficit is fully characterized.** Adjacent identical runes occur at 0.68% vs
   ~3.45% expected (~5× suppressed, z = −16.9, p < 5e-4). The suppression is **uniform across
   all 29 runes, diagonal-only, memoryless, and *soft*** (~18–20% of doublets survive). The
   entire off-diagonal bigram table is indistinguishable from perfect independence; there are no
   forbidden pairs, no periodicity at any lag, no inter-page shared keystream, and no higher-order
   n-gram structure. It is a global soft no-adjacent-repeat rule over an otherwise random stream.

2. **Published-text running keys are mechanistically ruled out.** A real English running key
   *injects* ~3.3% doublets into the ciphertext. LP2 has 0.68%. The doublets being **absent**
   means running-key-over-natural-text is the wrong *mechanism*, not the wrong *text* — which
   explains why every keytext attempt (this project's and the community's) has failed. Stop
   hunting for "the right book."

3. **Multiplicative gematria is mechanistically excluded.** The 29 rune-primes (2…109) form no
   closed multiplicative group under any non-trivial key (mod 109/113/1033/3301; closure only at
   k=1), and totient-multiplicative keystreams mod 29 hit zero divisors. "The primes are sacred"
   does not cash out as a multiplicative cipher.

4. **relikd = the onion7 master (byte-identical).** A standing community assumption that the
   relikd image set is a re-encoded re-host is **wrong**: relikd's `p0.jpg`/`p24.jpg` are
   MD5-identical to krisyotam's raw onion7 files. All public images are 2400×3600 @ 400 DPI
   Ghostscript/MuPDF **vector renders** (glyphs crisp by construction). No higher-resolution
   master exists publicly. Image quality is not a limiting factor.

5. **The canonical transcription is image-faithful (independently verified).** A trained glyph
   classifier (SVC on normalized glyph pixels) reaching **99.2%** cross-validated accuracy
   independently re-read the runes from the images and corroborates rtkd canon with **zero real
   single-glyph errors** on pages 0–54 (all raw disagreements were off-by-one line-alignment
   artifacts). Crucially, **all public transcriptions trace to one origin (rtkd/iddqd)** — even
   the supposed "independent OCR" is byte-identical — so this classifier is the first genuinely
   image-independent check, and canon passes it.
   - **Resolved:** the lone in-scope inter-source discrepancy, **page 24 index 172**, is
     **`ᚫ` (AE)** — rtkd canon is correct; the scream314 reading of `ᚪ` (A) is the error.
     (Both glyphs are two-armed here; the discriminator is the upper arm — `ᚪ` has a hooked/
     triangular top, `ᚫ` has two straight parallel arms; the target matches `ᚫ`, confirmed by
     the classifier at 0.973.)

## 3. What the structure implies about the mechanism

The fingerprint — flat IoC, no period at any lag, perfect off-diagonal independence, and a
uniform soft diagonal-only doublet suppression with a small residual — is reproduced by
**soft-rejection sampling from the empirical unigram distribution**. Mechanisms consistent with
it: an OTP / long running-key (mod-29 stream addition) whose **keystream was itself filtered to
avoid producing two identical output runes in a row**, or a by-hand "don't write the same rune
twice" encoding rule (the ~20% residual = tolerated/missed repeats). Ciphertext-autokey matches
the doublet *rate* but decrypts to gibberish under brute force, so it is refuted as the actual
cipher. The onion7 margin art is grouped by page-set (Babylonian sexagesimal on 34–39,
mayfly/"ephemeral" motif on 24–26/57/14, dendrites on 8–14/32/55), weakly suggesting per-set
cipher *variation* — consistent with the no-global-period finding; the mayfly/ephemeral motif
thematically echoes a one-time pad.

## 4. Methods that correctly reproduce known solves (sanity)

The rig re-derives: WELCOME/DIVINITY (Vigenère "DIVINITY" + interrupters), A WARNING (Atbash +
shift), SOME WISDOM (shift), the shift-3 koan, FIRFUMFERENFE, and the AN END page
(φ(prime)/prime-minus-1 keystream). A per-page polymorphic sweep correctly re-solved AN END from
scratch — confirming the toolkit works — while finding nothing on pages 0–54.

## 5. Do-not-redo list (eliminated with reasons)

Brute-force / running-key family:
- Additive keystreams (primes, totient, Fibonacci, OEIS A061474, prime-counting, CFB), autokey,
  first-differencing, page-on-page keying.
- Running keys vs: Mabinogion, Self-Reliance, The King in Yellow, Liber AL/Book of the Law,
  Agrippa, Tao Te Ching, Blake's *Marriage of Heaven and Hell*, Gospel of Thomas, the
  Anglo-Saxon Rune Poem, solved-page text (latin **and** rune/gematria space), Cicada's own PGP
  prose, and the Cicada-thematic esoteric corpus: **Iamblichus, Nicomachus, Corpus Hermeticum,
  Sepher Yetzirah, Mathers' Kabbalah Unveiled, John Dee (Monas + Enochian), Rosicrucian
  (Fama/Confessio/Chymical Wedding), Pistis Sophia, Lesser Key of Solomon, Crowley (Book of
  Thoth)**. (All running-key attempts are now also covered by finding #2 above.)
- Vigenère all key lengths; per-page exhaustive Vigenère L1–4 (+interrupter beam) and hill-climb
  L4–12, Atbash/shift, prime/totient/prime-1 keystreams with offset search, autokey — **per page,
  independently**, pages 0–54.
- Hill cipher: 2×2 exhaustive (all 682,080 invertible matrices) + 3×3 sampled.
- Fractionation/bifid, transposition-only, prime/totient transposition + substitution combos,
  monographic substitution (ruled out by IoC).
- Multiplicative/number-theoretic gematria (mechanistically excluded — finding #3).

Structure / representation:
- Off-diagonal bigram structure, n-gram repeats, periodicity (lags 2–30), inter-page shared
  keystream, gematria prime-value modular sums, word-boundary positional bias, the doublet
  residual, latin-multigraph expansion, page reorderings, runes-per-line count stream — **all
  null**.

Forensics / images / transcription:
- Real OutGuess 0.4 (built from source, validated against all known 2012–2014 payloads) +
  steghide/stegseek on every page image: **no payload** on the rune pages (the OutGuess-data
  claim applies to the 2012–2014 *clue* images, not the LP rune pages).
- LSB/DCT stego sweep, EOF/appended-data + EXIF forensics, PGP operational forensics (RSA sound).
- Template/classifier re-transcription: **canon is image-faithful**; no higher-res original
  exists; page 24:172 = AE.

OSINT:
- Uncovering Cicada wiki, r/cicada, all English solver repos (scream314, relikd/rtkd,
  r4nd0mD3v3l0p3r, krisyotam, cicada-solvers/iddqd), GitHub/Gist/Pastebin code search, archive
  mining, the AN END deep-web hash + full onion7 content, and non-English (Russian/Chinese/
  German/etc.) communities — **no public external key exists**; no insider ever leaked key
  material; Cicada has been silent since the verified 2017 message.

## 6. Reproducing

```
cd liber-primus
python3 tests/validate.py          # rig reproduces all known solves
python3 attack.py selftest         # scorer re-finds DIVINITY at -4.34
```
The `analysis/{armada20,foundation,structure,stones}/` directories contain the attack scripts
and result JSONs. Large fetched public-domain corpora and binary datasets are intentionally not
committed (re-fetchable; see each campaign report for sources and the exact fetch URLs).

---
*Caveat on completeness: "unbreakable by available means" is a statement about exhaustive
internal cryptanalysis plus public OSINT, not a mathematical impossibility proof. If LP2 is a
true OTP, no ciphertext-only attack can ever succeed; if it instead uses a specific external
keytext nobody has tried, finding that text remains the only path — but it is **not** a
natural-language running key (finding #2).*
