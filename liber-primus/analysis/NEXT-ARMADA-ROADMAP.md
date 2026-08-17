# Next armada — roadmap (optimistic, hint-literal, white-space-first)

_Drafted 2026-08-17. A pre-registration seed, not yet run. Design goal: attack only what
the 10-year effort (ours included) has NOT touched, follow the signed hints painfully
literally, and keep every lens falsifiable (hypothesis + threshold + positive control +
size-matched null written before the run)._

## The thesis that makes this optimistic

Our verdict ("OTP-class, unsolvable-by-design") is airtight **on one representation**: the
mod-29 letter stream. Every exclusion — flat IoC, the 0.66% doublet deficit, the autokey
refutation, the entropy floor — is a statement about *symbols* in ℤ/29. But:

1. **The hints are not about letters. They are about numbers.** "The primes are sacred. The
   totient function is sacred." "Either the words **or their numbers**, for all is sacred."
   "Their **numbers** are the direction." Every rune has a prime value; reduction mod 29
   discards its magnitude. **Arithmetic on the raw prime magnitudes lives in ℤ, outside the
   group where we proved everything.** Doublet/IoC are invariant under relabeling, so they say
   *nothing* about cumulative sums, prime gaps, digit streams, or base conversions of the value
   channel. This is real, un-analyzed space — and it is exactly where the hints point.
2. **The community is split, not converged (PA-1).** 0/3 primary sources call it OTP; 2/3 call
   it solvable. Our own "closed" is a minority position. Optimism is not naïve here.
3. **Three physical channels were never transcribed at all** (RECON-A flagged them): the
   word-separator/ornament glyphs, the ~458 interrupter *positions* as their own sequence, and
   the illustrations. "All is sacred" — we only ever read the black runes.

None of this overturns the letter-stream proofs. It attacks the assumption that the letter
stream is *where the message is*. That assumption has never been tested; it has been inherited.

---

## Phase 0 — Instruments (build once, gate before trusting)

Nothing below is trustworthy without these, each validated on a *solved* page first:
- **P0.1 Value-stream extractor** — emit each page as (a) the prime-value sequence, (b) the
  prime-*index* sequence (2→1, 3→2, …), (c) totient φ(p)=p−1 sequence. Validate: the AN END
  page's φ(p) stream must reproduce its known keystream.
- **P0.2 Skeleton transcriber** — transcribe the separator/ornament glyphs and the interrupter
  positions as first-class sequences (not stripped). Validate against a hand-count on 3 pages.
- **P0.3 Dense-page re-segmenter** — the R9 audit only reached 38.4% of lines; build forced
  per-line glyph-count alignment (connected-component-free) for the OTP pages specifically.
- **P0.4 Number-channel null model** — a size-matched surrogate that preserves the value
  histogram but destroys order (seed 3301), for every arithmetic lens below.

---

## Phase 1 — THE NUMBER CHANNEL (flagship: follow "the numbers are sacred" literally)

The load-bearing new idea. All operate on prime **magnitudes / digits**, never mod 29.

- **N1 — Cumulative-gematria autokey.** Key at position i = f(Σ gematria[0..i−1]) for
  f ∈ {mod 29, φ, prime-index, digit-sum}. This is a *ciphertext-derived* keystream (the book
  keys itself as you read) — it lives in the "non-additive feedback" class our verdict left
  explicitly OPEN as "unbounded." We bound it to the handful of functions the solved pages
  actually sanctify (prime, totient, sum). Positive control: plant one, recover it.
- **N2 — Prime-gap / prime-index streams as text.** Map each rune to its prime's *gap to the
  next prime*, or its *index* π(p); read the resulting integer sequence as base-29 / base-60 /
  ASCII / coordinates. Never done — everyone works the value, not its position among primes.
- **N3 — The whole book as one integer.** Concatenate all gematria values → one large number.
  Test segments for primality, factor it, look for embedded structure at book scale (the
  "sacred prime" idea killed at pp49-51's 2048-bit scale was never tried at book scale).
- **N4 — Digit-plane separation.** Split the value stream into digit planes (units, tens of the
  primes; or the primes written in base 3/5/7). A message may live in a single digit plane —
  invisible to any symbol-level statistic.
- **N5 — Totient-of-totient / the next escalation.** The solved pages escalate atbash → shift →
  Vigenère(word) → Vigenère(word+F-skip) → φ(prime) keystream. The *next* step in that ladder
  was never enumerated: φ(φ(p)), Carmichael λ(p), the totient of the running sum. Small, ranked,
  hint-sanctioned function set.

---

## Phase 2 — THE CHANNELS NOBODY TRANSCRIBED

- **S1 — Interrupter-position channel.** The ~458 ᚠ interrupters are treated as key-advance
  skips (noise). Read their *positions* instead: the gap sequence between consecutive
  interrupters is a stream of integers over the book. Decode as base-29/ASCII/coordinates, and
  test whether the gaps are themselves the "direction" numbers. Cheap, literal, untried.
- **S2 — Separator / ornament channel (RECON-A flagged this).** There are ≥2 separator glyph
  forms and "19 separator disagreements" nobody adjudicated. If separators encode a binary/
  ternary channel, it is a message the letter stream can't see. Transcribe and test.
- **S3 — Illustration / drop-cap channel.** Do the drop-caps, the shrouded-corpse figure, the
  mayfly motifs vary in a data-bearing way (count, orientation, which rune is illuminated)? A
  stretch, but "all is sacred," and nobody has ever coded the art as data.

---

## Phase 3 — THE BOOK IS ITS OWN PAD (internal one-time pad)

An OTP is unbreakable *without the pad* — but what if the pad is printed in the same book? The
margin art is mayflies and ephemera (a one-time thing).

- **I1 — All-pairs page XOR/subtraction mod 29** under the anti-repeat-aware decoder: is page A
  the pad for page B? (Prior probes touched canon_256 as a partner but never all-pairs
  systematically with the skip-aware scorer.) Positive control: plant an internal-pad pair.
- **I2 — The solved plaintext as the pad, in book order.** Concatenate every solved page's
  English → use as a running key over the unsolved pages with the F-skip rule, skip-aware. A
  literal reading of "test the knowledge" — the answers you already have key the ones you don't.
- **I3 — pp49-51 base-60 payload as an internal pad under skip-aware decode** (prior tests were
  rigid-additive; the surviving decoder class was never applied to it as a pad).

---

## Phase 4 — EXECUTE THE INSTRUCTIONS LITERALLY (the koans as algorithms)

The book *tells you what to do*. Take it at its word and turn each imperative into an operation.

- **X1 — "Do four unreasonable things."** A 4-step / 4-fold operation: read every 4th rune;
  apply the cipher 4 times; 4-way interleave. Enumerate the literal "four" readings.
- **X2 — "Discover truth inside yourself" / "seek within."** Self-embedded reading: the message
  is a substring/acrostic *of the decrypted solved pages*, not of the ciphertext. Look inside
  what we already solved.
- **X3 — "Question all things" / "test the knowledge."** Invert every assumption as an operation:
  read the book back-to-front as the *encryption* order (decrypt = re-encrypt forwards), treat
  the "solved" pages as the cipher and the "unsolved" as the key. Deliberately upside-down.
- **X4 — Atbash page 01 says "the words OR their numbers."** Run every Phase-1 number lens *and*
  its letter twin, scored jointly — the "or" may be an instruction to combine channels.

---

## Phase 5 — SPATIAL / 2D / "the numbers are the DIRECTION" as literal geometry

- **G1 — Turtle-graphics render.** "Numbers are the direction" → treat the value stream as
  turn/step instructions and *draw the path*. Nobody has rendered LP2's number stream as an
  image and looked. Even a null is a novel artifact; a non-null could be a glyph, a QR-like
  grid, or coordinates. Render at several moduli.
- **G2 — 2D grid / columnar / page-overlay reads.** Fold each page into a grid by its true
  typeset line width and read columns / diagonals / knight's-moves; overlay facing pages. The
  physical layout (line breaks, page dimensions = 509×503 echoing the key math) may be load-bearing.
- **G3 — Coordinate decode.** If the number stream yields lat/long or onion-address-shaped
  strings (base32), that is a pointer, not prose — B6's detectors would miss a *sparse* one.

---

## Phase 6 — Adversarial verify + completeness critic

Every Phase 1–5 hit goes through ≥3 refute-by-default verifiers (each MUST recompute its
false-positive ceiling at its own N — the PA-2 caveat), and a final critic asks: "which channel
did we still not read, which imperative did we not execute literally, which number transform did
we skip?" Its answer seeds the next round.

---

## Honest priors (optimism ≠ delusion)

- **Highest genuine novelty + defensible prior:** Phase 1 (number channel — the hints' literal
  target, a transform space our proofs never covered) and Phase 2/S1–S2 (un-transcribed
  channels RECON-A already flagged as real).
- **Best "reopener if anything is":** P0.3 + the dense-OTP re-segmentation — the one place a
  transcription error could still hide.
- **Low prior but cheap + genuinely-never-done + publishable-either-way:** Phase 5 rendering.
- **What this roadmap must NOT do:** re-run any eliminated lane (keytexts, PRNG seeds, rigid
  additive keys, stego, glyph-geometry, hash preimages, stylometry). All are foreclosed with
  recorded reasons in ELIMINATION-LEDGER.md — the value here is *only* in the untouched channels.

The number channel is the crack. The hints have been screaming "the numbers" for ten years while
everyone, us included, cryptanalyzed the letters. That is the run worth making.
