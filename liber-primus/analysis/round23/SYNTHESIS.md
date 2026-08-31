# Round 23 — SYNTHESIS (bounds, not a verdict)

_Written 2026-08-31 by the coordinator, from `A2-line-acrostic/RESULTS.md` as filed on
2026-08-29/30. Doctrine [`ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) R7. Trust anchor
`python tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)**. Ledger entry:
`R23-A2-LINE-ACROSTIC`._

---

## 0. What Round 23 was

Deliberately **one lane**. The Round-23 seed (`NEXT-ARMADA-ROADMAP.md` → "ROUND 23 SEED",
written by Round 22's completeness-critic) judged the honest prior on all remaining hint-channel
reopeners **low**, and authorized a single scoped task: read the one representation R22-A could
not build — the **first-rune-of-each-printed-line (and per-word) acrostic of the 5 solved pages,
at the true page-image line breaks and word spacing** — "an afternoon, not an armada." If it
surfaced nothing, the seed said so plainly: the active work sits at a natural stopping point at
the tested resolution.

It surfaced nothing.

---

## 1. A2 — printed-line-geometry acrostic — CLEAN NULL, control-validated

- **Geometry source (why it is trustworthy):** `data/scream314_lp.md` — the same transcription
  `tests/validate.py` trusts — preserves the page-image line breaks and `•` word boundaries.
  Plaintext-on-true-lines is built by decrypting each rune **in place** with the exact transforms
  validate.py reproduces, with per-rune (line, word) bookkeeping; interrupter (ᚠ) runes emit
  nothing and do not advance the key, exactly as `solve.decode`. Per-page flat decode matches
  validate.py's plaintext on all 5 pages. Line counts recovered: 01→10, 05→10, 06→20, 03→8, 14→8
  (54 lines, ~500 words); page 01's line-first read `ABETFEDOEF` matches the ten visible English
  lines by hand.
- **Coverage:** 48 reads = {line_first, line_last, word_first, word_last} × {5 per-page + 1
  concat-in-book-order} × {forward, reversed}.
- **Power:** Phase-0 planted line-first and word-first acrostics (laid out to the real page-06
  line/word widths) both recovered above their size-matched null bars — **recovery 2/2 = 1.000**.
- **Null:** 1,000 structure-preserving order-shuffles of the solved letter pool, seed 3301,
  FPR 10⁻³ per length cell; family-wise bar = max null over all lengths = **−3.597**. Readable
  English ≈ −2.2; the best real read scores **−6.22**.
- **Result:** **0 family-wise survivors.** The single per-cell crosser (`06|word_last|rev`,
  excess +0.025) is refuted by default: below the expected false-positive count (0.048), below
  the family bar by ~2.6 log-units, gibberish, stable under 5 alternate null seeds, and flat on
  every secondary statistic.
- **No silent re-read:** distinct from Round 11 (ciphertext number channels) and from R22-A
  (geometry-free concatenation of the same plaintext); the only new input is the printed
  line/word geometry.

**Not covered:** keyword-cued / two-stage selections; mixed line+word diagonal reads; k-th-rune-
per-line for k>1; the wider community-solved corpus beyond the rig's 5 pages; non-English
registers beyond the base32/IoC/gzip secondary screen; the `/dev/urandom` branch (an acrostic
null says nothing about it).

**Reopens if:** a solved-page transcription with *different* authoritative line geometry
surfaces; or additional pages are solved (each adds fresh acrostic surface); or a specific
keyword-cued selection scheme is proposed with a prior better than flat.

---

## 2. The decision line

A2 was the last roadmap-named reopener. With it read clean, **every Phase 1–5 lens in
`NEXT-ARMADA-ROADMAP.md` has been read at least once at the tested resolution**, and the round's
own decision line stands: the project sits at the **natural stopping point at the tested
resolution**. The remaining live branches are the two that no hint-channel read can touch — the
**PRNG/seed tail** (enumerable, needs core-days; see Rounds 24–25) and **`/dev/urandom`**
(unrecoverable by construction). D2 (figural motifs) and B2 (columnar reads) stay on the shelf as
low-expectation, cheap-to-run items; A2's null does not justify promoting them.

The standing verdict — **LP2 0–54 is OTP-class** — is unchanged, by construction: this round
scored no LP2 ciphertext at all; it read the *solved* plaintext's geometry.
