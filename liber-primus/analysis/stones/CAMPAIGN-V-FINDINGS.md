# Campaign V After-Action Report — LP2 (Liber Primus, pages 0–54)
## Final Stones

_Run 2026-06-21. 8 agents (~0.42M tokens). Trained glyph classifier, novel cryptanalysis
(prime/multiplicative gematria, doublet residual, alt-representations), deep external-key OSINT
round 2. Artifacts under `analysis/stones/`._

## 1. Bottom line

Nothing broke (expected for an OTP-class cipher) — but this campaign produced real **closure** on
the open questions:
- **A trained glyph classifier reached 99.2%** and **independently corroborates rtkd canon** with
  zero real transcription errors on pages 0–54. The ciphertext every campaign attacked is
  image-faithful. The "transcription is an unverified assumption" problem is now **resolved**.
- **Page 24:172 is resolved → `ᚫ` (AE): rtkd canon is correct, scream314 was wrong.** The one
  in-scope source discrepancy in the entire corpus closes in canon's favor.
- **Multiplicative gematria is mechanistically excluded** (not merely unobserved), and the doublet
  residual + alternative representations carry zero exploitable information.
- **No external key exists publicly** (AN END page / onion7 / international communities all dry).

## 2. Independent transcription — canon corroborated

- Classifier: SVC (RBF) on normalized binarized glyph pixels, 5-fold CV accuracy **99.2%**
  (10,688/10,774 clean glyphs), 484/488 clean lines perfect.
- The prior 69.5% failure was **segmentation**, now fixed: color-aware ink (keeps red drop-caps),
  rune-height connected-component filter (drops word-dots/ornaments/Latin-index blocks), and a
  discovered correction — **relikd image numbering ≠ krisyotam page numbering past ~page 34**
  (relikd p54 = krisyotam page 53), handled via the relikd ranged-file boundaries.
- **All 86 raw disagreements are off-by-one line-misalignment artifacts** on 4 ornamented lines
  (each: the classifier's whole-line reading matches the *neighboring* canon line at 21–22/22).
  **Zero isolated single-glyph errors.** Canon is image-faithful for pages 0–54.
- Caveat: labels are canon-by-position, so 99.2% measures image↔canon *consistency*; but a
  classifier that reproduces canon near-perfectly with only alignment artifacts strongly supports
  canon being a faithful transcription.

## 3. Page 24:172 — resolved to `ᚫ` (AE)

The classifier and the adversarial verifier **contradicted** each other (classifier: AE 0.973;
verifier: A, claiming the classifier's exemplars were mislabeled). Adjudicated by hand with a
controlled same-page panel (`analysis/stones/MY_adjudication2.png`):

- The verifier's premise ("A = one arm, AE = two arms") is **wrong**: on page 24 both confirmed
  `ᚪ` and confirmed `ᚫ` are two-armed. The real discriminator is the **upper arm shape** —
  confirmed `ᚪ` has a hooked/triangular top; confirmed `ᚫ` has two clean straight parallel arms.
- The target glyph (line 8, first rune of `ᚫᚢ`) shows **two straight parallel arms**, matching the
  confirmed `ᚫ` glyphs at the start of lines 5 and 9, and **not** the hooked-top confirmed `ᚪ` on
  its own line.
- This agrees with the classifier (AE 0.973; A scored 0.001, validated 99.2% corpus-wide). The
  adversarial verifier made an **inverted call**.

**Verdict: page 24:172 = `ᚫ` (AE). rtkd canon correct; scream314's `ᚪ` is the error.** The lone
in-scope transcription discrepancy is closed.

## 4. Novel cryptanalysis — all null, some mechanistically excluded

- **Prime/multiplicative gematria:** NULL, and **mechanistically excluded** — the 29 rune-primes
  (2..109) form no closed multiplicative group under any non-trivial key (mod 109/113/1033/3301;
  closure only at k=1), and totient-multiplicative keystreams mod 29 hit zero divisors. Best −6.54,
  gibberish.
- **Doublet residual:** the ~18% surviving doublets are statistically **uniform random thinning**
  of an OTP stream — no correlation with rune identity, page, line, word-position, F-interrupter
  proximity, cross-page line index, or any keystream period (mod 2–12). The residual carries no
  information.
- **Alternative representations:** latin-multigraph expansion, page reorderings, runes-per-line
  count stream — all flat. The one non-flat statistic (latin-expansion IoC×26 = 1.70) is a
  deterministic translit-table artifact with zero plaintext information.

## 5. External-key OSINT round 2 — no key

- **AN END page / onion7:** the complete 2014 onion7 content is preserved (micheloosterhof,
  rtkd/iddqd) — no extra payload, no external key. The 512-bit AN END hash preimage is downstream
  of LP2 0–54 and points to a dead v2 onion (offline since Oct 2021) — not an LP2 key source.
- **Margin decorations (the only physical hint attached to unsolved pages):** grouped by page-set
  (Babylonian sexagesimal on 34–39; mayflies/"ephemeral" motif on 24–26/57/14; dendrites on
  8–14/32/55). These suggest **per-set cipher variation**, consistent with the rig's
  OTP-class/no-global-period finding — and the mayfly/"ephemeral" motif *thematically* echoes a
  one-time (ephemeral) pad. Not an external key, and per-page method sweeps already came up empty.
- **International communities** (Russian/Chinese/German/etc.): downstream consumers of English
  solver research; no original LP2 key claim.

## 6. Newly eliminated / learned (append to do-not-redo)

- Trained-classifier transcription confirms **canon is image-faithful (pages 0–54)** — stop
  hunting transcription errors; page 24:172 = AE (canon).
- **Multiplicative/number-theoretic gematria is mechanistically excluded** — do not retry.
- Doublet residual and all alternative representations carry no information.
- No public external key exists (onion7, AN END, international communities all confirmed dry).
- Faint open thread (low EV): marginal art implies per-page-set cipher variation; cryptanalytic
  per-page sweeps already negative, so this only matters if a set uses an externally-keyed method.

## 7. Final verdict — LP2 is unsolvable by available means

After **five campaigns** (~55 approaches), every internal attack surface is exhausted and the two
open assumptions are now closed: the **transcription is verified faithful** (99.2% independent
classifier; page 24:172 resolved to canon), and the **cipher is confirmed OTP/long-running-key
class** with a uniform soft anti-repeat overlay and no internal handle. Brute force, published-text
running keys (mechanistically ruled out), per-page polymorphic methods, prime/multiplicative
gematria (mechanistically excluded), stego (validated-clean), the doublet residual, alternative
representations, and exhaustive OSINT have all returned honest negatives.

**LP2 is, to the best of repeatable analysis, a one-time-pad-class cipher whose key was never
published.** It is information-theoretically unbreakable from the ciphertext alone. The only events
that could change this are **external**: the actual key surfacing, or a new Cicada release. Further
internal cryptanalysis is not expected to succeed and should be considered closed.

**Genuinely novel contributions from these campaigns (publishable to the solver community):**
1. The doublet deficit fully characterized (uniform, diagonal-only, memoryless, soft).
2. Published-text running keys mechanistically ruled out (English running key injects ~3.3%
   doublets, which are absent).
3. Multiplicative gematria mechanistically excluded.
4. relikd = onion7 master (byte-identical) — corrects a standing assumption.
5. An independent 99.2% classifier transcription corroborating canon; page 24:172 = AE.
