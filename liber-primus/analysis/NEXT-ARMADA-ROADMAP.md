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

---

# ROUND 22 SEED — turn away from the letter-stream sweep, read the un-read channels

_Written 2026-08-29 by the Round 21 coordinator's completeness-critic pass (roadmap Phase 6).
Binding: [`../ARMADA-DOCTRINE.md`](../ARMADA-DOCTRINE.md). A pre-registration seed, not yet run —
each lane still owes a full `PREREG.md` (hypothesis + threshold + positive control + size-matched
null + the five Aiming-Test answers) before it may score anything._

## Why this round turns away from the PRNG branch

Rounds 16–21 spent almost their whole budget on **one branch**: the letter-stream seeded-PRNG /
seed-dictionary / sieve / seal machinery. That branch is now heavily instrumented and heavily
bounded — Round 20 proved the sieve infeasible, Round 21 swept one more Py2.7 slice clean and
proved the no-oracle seal leaky — but every result there is *another stated-fraction negative on
the same channel*, and the doctrine's own §0 warns that this is precisely the mis-aimed activity
that cost this project 10¹⁰ decodes. Meanwhile the roadmap's Phase 1–5 thesis has been read exactly
**once** (Round 11: N1–N5 + S1–S2, all NEGATIVE and control-validated, S2 closing the RECON-A
separator flag) — and **six lenses were never touched at all.** The completeness-critic's answer to
"which channel did we still not read, which imperative did we not execute literally, which number
transform did we skip?" is: **S3, X1, X2, X3, X4, and the G1-turtle render.**

These score highest on the Aiming Test because they are **bounded, human-checkable objects**
(doctrine R5 rank 1) carrying an **evidence-derived prior** (doctrine R4) — the *signed* hints
themselves ("test the knowledge," "seek within," "the numbers are the direction," "the words **or**
their numbers"). They are cheap, and each returns a novel artifact even on a null. **The value of
Round 22 is *only* in these untouched channels — do NOT let it drift back into another key-space or
PRNG sweep** (those stay queued, bounded-not-closed, behind this work).

## The lanes (ranked by novelty × prior; each needs its own PREREG before running)

| lane | roadmap ref | hypothesis (one line) | why it clears the Aiming Test | positive control |
|---|---|---|---|---|
| **A — Self-embedded read** | X2 | The message is a substring / acrostic / every-k-th-rune selection **of the already-solved plaintext**, not of the ciphertext — "seek within" / "test the knowledge" read literally. | Q2 prior: two signed koans point *inward*. Q3: bounded — the solved-page plaintext is a fixed ~finite string; enumerable selection functions. Never done. | plant a known acrostic in a control plaintext of equal length, recover it. |
| **B — Turtle / spatial render** | G1, G3 | "The numbers are the direction": treat the value / prime-index / totient stream as turn-step (or angle-step) instructions and **draw the path** at several moduli; look for a glyph, grid, QR-like structure, or coordinate string. | Q1: the recognizer is the human eye + a structure detector on the rendered image — a channel no symbol-level statistic can see. Q3: bounded (finite moduli × finite step rules). A null is still a publishable novel artifact. | render a plaintext-encoded known shape through the same pipeline and confirm it is legible. |
| **C — The four literal imperatives** | X1, X3, X4 | Execute the koans as operations: "**four** unreasonable things" (every 4th rune / 4× cipher / 4-way interleave); "**question all things**" (read book back-to-front as the *encryption* order; solved pages as cipher, unsolved as key); "the words **OR** their numbers" (score each Phase-1 number lens jointly with its letter twin — the "or" as a combine instruction). | Q2 prior: each is a direct, signed instruction. Q3: each is a small enumerable operation set. Never executed literally. | plant-and-recover for each operation (e.g. a 4-interleaved known text). |
| **D — Illustration / drop-cap channel** | S3 | Do the drop-caps, the shrouded-corpse figure, and the mayfly motifs vary in a **data-bearing** way (count, orientation, which rune is illuminated, ordering)? Code the art as data and test against a null. | Q3: bounded — a finite, hand-countable set of illustrated features across 55 pages. "All is sacred," and nobody has ever coded the art as data. Lowest prior of the four; queue last of the novel lanes but still ahead of any PRNG re-sweep. | hand-count 3 pages' features, confirm the extractor reproduces the count (P0.2-style). |

**Standing lanes carried into Round 22 (doctrine R6 + closeout):**
- **Red-team lane (mandatory, R6):** target Round 22's *own* number/spatial hits — every hit goes
  through ≥3 refute-by-default verifiers, each recomputing its false-positive ceiling at its own N
  (the PA-2 caveat); and confirm none of A–D silently re-reads a Round-11 lens already covered
  NEGATIVE (N1–N5, S1–S2) as if new.
- **Seal note (from R21 L1):** any bar-clearing survivor from *any* lane is **flagged-for-oracle,
  not auto-certified** until a non-fold no-oracle gate reaches ≥0.90 catch at ≤0.10 false-reject.
  Building that non-fold gate (longer decrypt head / per-register bar / learned self-consistency) is
  a legitimate ≈30% instrument slice for the round if a survivor appears.
- **FP-inflation conditional (from R20 R / R21 L5):** if any Round-22 lane introduces a *screened*
  sieve, it must re-derive its null on the screened population (the 2.5×10⁶ inflation), or sweep
  unscreened.

## Budget (doctrine §3)

≈40% to the high-prior bounded novel lanes A–C (Q2 answered with a signed hint, Q3 answered
"enumerable/bounded"); ≈30% instrument (the recognizers each lane needs — the acrostic detector,
the turtle-render structure detector, the illustration-feature extractor — validated on a solved
page first, per Phase 0); ≈20% red-team; ≈10% closeout (D, plus completing any stated-fraction PRNG
tail *only if* a lane argues it in writing). **The PRNG/seed sweeps are explicitly NOT the lead of
this round** — they are bounded-not-closed and queue behind the untouched channels.

## The one-sentence thesis

Round 22 stops sweeping the letter stream and finally **reads the channels the hints have been
pointing at for a decade** — the message hidden *inside the already-solved plaintext* (X2), the
number stream drawn as a *direction* (G1-turtle), the koans executed as *operations* (X1/X3/X4),
and the *art* coded as data (S3) — each bounded, each hint-sanctioned, each with a positive control
and a null, and none of them ever run.

---

# ROUND 23 SEED — the last three hint-channel reopeners, at true resolution (with an honest prior)

_Written 2026-08-29 by the Round 22 coordinator's completeness-critic pass (roadmap Phase 6).
Binding: [`../ARMADA-DOCTRINE.md`](../ARMADA-DOCTRINE.md). A pre-registration seed, not yet run —
each lane still owes a full `PREREG.md` before it may score anything. **Read the honest-prior
section at the bottom first: this is a low-expectation round, and the owner should decide whether
it is worth a full armada or a single afternoon.**_

## What Round 22 changed

Round 22 read all four signed-hint channels — X2 (self-embedded plaintext), G1-turtle
(numbers-as-direction), X1/X3/X4 (koans-as-operations), S3 (art-as-data) — and every one came back
a **clean, control-validated NEGATIVE**. Combined with Round 11 (N1–N5, S1–S2), **every roadmap
lens Phases 1–5 named has now been read at least once at the tested resolution.** The
"we-never-looked-at-the-hinted-channels" objection — the thing that justified turning away from the
PRNG branch — is now **largely closed.** That is the single most important fact for aiming Round 23:
the high-prior novel-channel budget that Rounds 22 spent is **mostly gone**, because the channels
are mostly read. What remains are the **resolution gaps** inside those reads, not new channels.

## The three genuinely-unrun threads (ranked by novelty × prior)

| lane | source | hypothesis (one line) | Aiming-Test standing | positive control |
|---|---|---|---|---|
| **A2 — Printed-line-geometry acrostic** | R22-A `not_covered` | First-rune-of-each-**printed line** (and per-word) acrostic of the solved pages, using the **true page-image line breaks + word spacing** — the one representation R22-A could not build (it had only the concatenated transliteration). | **Highest of the three.** Q2 prior: "seek within" is a signed inward hint AND a line-first acrostic is the single most conventional place a self-embedded message hides — the one spot a self-embedded read could still be hiding. Q3: bounded — a fixed finite string once the line breaks are transcribed. Q1: reuses R22-A's validated acrostic recognizer (recovery 1.000), only the input geometry is new. | plant a line-first acrostic in a control page laid out to the same line widths, recover it (R22-A's Phase-0, re-pointed at line geometry). |
| **D2 — Figural-motif channel** | R22-D `not_covered` | Do the figural illustrations (crosses, trees, the shrouded-corpse figure, mayflies) vary **data-bearingly** — count / type / orientation / per-page ordering — coded as an integer sequence and tested against the seed-3301 null? R22-D read only the drop-cap channel. | **Medium.** Q3: bounded — a finite hand-countable feature set across the in-repo scans. Q2 prior: "all is sacred" + Cicada's known use of imagery. **Q1 is the weak point:** the recognizer is a hand-annotation or a black-channel shape pass entangled with the dense-rune OCR floor (0.145) — the extractor itself must be control-validated before any null means anything. | hand-annotate 3 pages' motif counts, confirm the extractor reproduces them (P0.2-style) BEFORE scoring. |
| **B2 — Non-turtle 2D / columnar / page-overlay reads** | R22-B `not_covered` (Lane G2) | Read the number/value stream as a **2D grid / columnar / page-overlay** using the **true typeset line width** (not turtle turn-step) — the G2 lens R22-B explicitly did not cover. | **Lower.** Q3: bounded once the line width is fixed. **Q2 is thin:** this is closer to "another framing of the number stream" than a new channel, and Round 11 + R22-B already worked the number stream hard from two directions. Q5 kill-fast: if the true-width columnar read is a constrained lattice walk like the turtle render was, abandon at the first modulus. | plant a grid-encoded known shape at the true line width, recover it. |

**Standing lanes carried into Round 23 (unchanged):**
- **Red-team lane (mandatory, R6):** target Round 23's own hits; recompute each FP ceiling at its
  own N; confirm no silent re-read of a Round-11/Round-22 lens already covered NEGATIVE.
- **Seal note (R21 L1):** any bar-clearing survivor is **flagged-for-oracle**, not auto-certified,
  until a non-fold no-oracle gate reaches ≥0.90 catch at ≤0.10 false-reject.

## Budget — but see the honest prior first

If run as a full round: ≈40% to A2 (the only lane with a genuinely high prior and a ready
recognizer), ≈25% to D2 (gated on building + validating the motif extractor first — that IS the
instrument slice), ≈15% B2, ≈20% red-team. But the honest recommendation is **not** a full round —
see below.

## The honest prior (optimism ≠ delusion, doctrine §5 — and its inverse)

**This is the section the owner should weigh.** After Round 22, the honest prior on the remaining
reopeners is **low**, and it should be said plainly:

- The doctrine's optimism clause is real: three times this project called a branch closed and was
  wrong. **But** all three of those reopenings came from **auditing an instrument or a closure** —
  never from running one more framing of an already-read channel. The three Round-23 threads are
  mostly the latter: they are **resolution gaps inside channels Round 22 already read clean**, not
  new closures to audit.
- **A2 is the exception worth running** — a line-first acrostic is the single most conventional
  hiding spot for a self-embedded message, R22-A genuinely could not reach it (it lacked the line
  geometry), and the recognizer already exists. If any one thread justifies effort, it is A2. It is
  also **cheap** — it is a transcription task (get the printed line breaks) plus a re-run of an
  existing validated sweep. This is closer to **an afternoon than an armada.**
- **D2 and B2 are cheap-to-run but low-expectation.** D2's whole cost is building a trustworthy
  motif extractor over the OCR floor; a null there is weak (the extractor, not the puzzle, is on
  trial). B2 is a third framing of a number stream already worked hard from two directions.
- **The two branches that could still hide the real answer are BOTH unaffected by any of this:** the
  bounded-not-closed **PRNG/seed tail** (built byte-exact, unswept — reopens only when someone
  spends the core-days or validates a new Py2.x seed family) and the **`/dev/urandom` branch**
  (untouchable by construction). Neither is a Round-23 lane; the honest position remains that if the
  pad was a CSPRNG or hardware draw, no round recovers it.

**Recommendation to the owner:** run **A2 as a single scoped task** (transcribe the printed line
breaks of the 5 solved pages, re-point R22-A's validated acrostic sweep at the real line geometry,
report). Do **not** stand up a full multi-lane armada for D2/B2 unless A2 surfaces something. After
A2, the project is at a **natural stopping point at the tested resolution**: every hinted channel
read, every instrument audited, the only live-but-unreachable branches being the PRNG tail (needs
compute, not ideas) and `/dev/urandom` (needs the pad to surface). That is a bound, not a verdict —
but it is an honest place to rest the active work.

## The one-sentence thesis

Round 23 is small: read the **one** representation Round 22 could not — the printed-line-geometry
acrostic (A2), the last plausible hiding spot for a self-embedded message — and, that done, accept
that the hinted channels are read and the remaining live branches (the PRNG tail, `/dev/urandom`)
need compute or a leak, not another round.

---

# POST-SEED STATUS — the seed ran, and the two follow-ons it authorized ran too

_Appended 2026-08-31 by the coordinator (doc-only; no measurement in this note is new — sources:
`round23/SYNTHESIS.md`, `round24/SYNTHESIS.md`, `round25/SYNTHESIS.md`, `PICKUP-HERE.md`)._

- **A2 ran (Round 23) and is a clean, control-validated NULL** — 48 reads over the true printed
  geometry, Phase-0 recovery 2/2 = 1.000, 0 family-wise survivors. The seed's decision line
  therefore stands: **natural stopping point at the tested resolution.** D2/B2 were, per the
  recommendation above, NOT stood up.
- **Round 24** did the one thing this roadmap's own philosophy prefers over any new channel:
  it audited the instrument's two known blind spots. The strongest historic slices were
  re-adjudicated under non-English / matched-runic scorers (L7-A) and under a decoder that can
  represent `skip_by_two` across 7 generator axes (L7-B). **The negatives hold under both
  corrections** — 5 of 8 candidate lanes were killed at the planning gate before a single decode.
- **Round 25** began the compute-only branch this roadmap said needs "compute, not ideas":
  the Py2.7-MT 2³² seed tail, ground through the skip-aware gate and **parked at 0.5015 %
  coverage, 0 hits**, resumable from committed checkpoints.

**There is no Round 26 seed here, deliberately** — though a Round 26 did open on 2026-08-31
(in flight at write time; see the note in `../PICKUP-HERE.md`): three lanes firing the
built-but-never-swept derived-key generators, the never-run R12-C2 keytext sweep, and a
semantic-seed enumeration — all instrument/closure work in the spirit of this roadmap's own
ranking, not a new channel. The remaining live items are recorded in
[`../PICKUP-HERE.md`](../PICKUP-HERE.md) (the OPEN list, with per-item updates through Round 25):
resuming the parked grind (or porting it to GPU/C), the two Round-21 housekeeping items that never
ran (the glibc `gen=0` row; the sieve reopening decision), the still-leaky no-oracle seal, and the
external reopeners (a new 7A35090F-signed release, a community-accepted solve, the pad surfacing).
A future round should open by reading `PICKUP-HERE.md` and the doctrine, not this section.
