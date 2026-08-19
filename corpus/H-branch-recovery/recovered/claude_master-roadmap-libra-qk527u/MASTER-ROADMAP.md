# MASTER ROADMAP — Liber Primus ("Libra") solve

_Last updated 2026-07-07. This is the top-level map: where we are, everything we've
already dug (so we don't dig it twice), and the ranked, still-open surface to keep
hammering. If you are picking this up cold, read this file first, then
[`PICKUP-HERE.md`](PICKUP-HERE.md)._

> **One-line state.** The **runic** Liber Primus pages (relikd index 0–56) are
> exhaustively attacked and behave as a **one-time-pad / long-running-key class
> cipher whose key was never published** — information-theoretically unbreakable
> from ciphertext alone. Six campaigns closed the *internal* cryptanalysis. What
> is genuinely **still open** is a small, concrete surface: a handful of **untested
> external key artifacts**, a **page-numbering reconciliation** that may mean some
> pages were never modeled as the right *data type*, and **watching for new Cicada
> material**. That surface is the whole point of this roadmap.

---

> **📕 Companion:** [`NEGATIVE-RESULTS.md`](NEGATIVE-RESULTS.md) is the citable failure
> archive — every candidate solution Claude Opus 4.8 ran and eliminated, with scores +
> reproduction. This roadmap is the *forward* view; that is the *record*.

## 0. How to read this map

- **§1 The wall** — the honest verdict and why ciphertext-only is a dead end.
- **§2 What we've already dug** — the Campaign I–VI ledger. This is the
  "don't re-run it" record. Each row links to its full findings.
- **§3 The do-not-redo list** — the compressed eliminated-with-reasons wall.
- **§4 The OPEN surface** — ranked leads that are genuinely *not yet run*, each with
  a concrete action, a run sketch, and a "resolved when" bar. **This is Campaign VII.**
- **§5 Execution order** — what to actually run first.
- **§6 Standing watch** — the only things that can change the verdict from outside.

---

## 1. The wall (why we keep hitting it)

Five campaigns of brute-force cryptanalysis, published-text running keys, per-page
polymorphic methods, number-theoretic attacks, steganography, structural analysis,
transcription verification, and OSINT returned honest negatives. Best score ever
**−6.023** (readable-English threshold ≈ −5.0; the rig correctly finds
DIVINITY/WELCOME at −4.34, random ≈ −7.3). See
[`liber-primus/LP2-ANALYSIS-SUMMARY-2026.md`](liber-primus/LP2-ANALYSIS-SUMMARY-2026.md).

Two mechanistic results define the wall and should shape every future attempt:

1. **Natural-language running keys are ruled out by mechanism, not just by trial.**
   A real English running key *injects* ~3.3% adjacent doublets. LP2 shows **0.68%**.
   The doublets are *absent*, so running-key-over-natural-text is the wrong
   **mechanism** — not the wrong book. **Stop hunting for "the right text."**
2. **The keystream was itself filtered to avoid adjacent repeats.** The fingerprint
   (flat IoC, no period at any lag, perfect off-diagonal independence, uniform *soft*
   diagonal-only doublet suppression with ~20% residual) is reproduced by soft-rejection
   sampling from the empirical unigram distribution. That points at an OTP / long
   running-key whose output was filtered, or a by-hand "don't write the same rune
   twice" rule. Any real key is therefore **non-linguistic** (numeric / structured).

**Consequence for this roadmap:** the only paths with non-zero odds are (a) an
**external key artifact** that is numeric/structured, or (b) a page that was never
the runic-OTP data type we assumed. §4 is built entirely around those two ideas.

---

## 2. What we've already dug — Campaign ledger

Single source of record. Do not reopen a CLOSED row without a new reason.

| # | Campaign | Scope | Verdict | Report |
|---|----------|-------|---------|--------|
| I–II | **ARMADA-20** | 20-agent brute-force: additive keystreams, Vigenère all lengths, autokey, hill cipher, PGP/onion cookie & magic-square keys, PRNG, appended-data/stego sweep | CLOSED — all null, best −6.02 | [`analysis/ARMADA-20-FINDINGS.md`](liber-primus/analysis/ARMADA-20-FINDINGS.md) |
| III | **Foundation** | Cicada-thematic esoteric running keys (Iamblichus, Nicomachus, Corpus Hermeticum, Dee/Enochian, Sepher Yetzirah, Mathers, Rosicrucian, Crowley, Pistis Sophia, Lesser Key…) as running/interrupter keys | CLOSED — all null; superseded by doublet mechanism proof | [`analysis/foundation/CAMPAIGN-III-FINDINGS.md`](liber-primus/analysis/foundation/CAMPAIGN-III-FINDINGS.md) |
| IV | **Structure** | Doublet deficit fully characterized; per-page polymorphic sweep; periodicity/inter-page keystream/n-gram tests; multiplicative gematria excluded | CLOSED — soft no-repeat rule over random stream; running-key mechanism ruled out | [`analysis/structure/CAMPAIGN-IV-FINDINGS.md`](liber-primus/analysis/structure/CAMPAIGN-IV-FINDINGS.md) |
| V | **Stones** | Independent glyph re-transcription (99.2% classifier); transcription lineage map; page 24:172 = ᚫ resolved | CLOSED — canon is image-faithful; all public transcriptions trace to one origin (rtkd) | [`analysis/stones/CAMPAIGN-V-FINDINGS.md`](liber-primus/analysis/stones/CAMPAIGN-V-FINDINGS.md) |
| — | **Vision** | 56-agent AI-vision re-transcription armada | CLOSED — vision cannot read dense pages (0.145 alignment) | [`analysis/vision/AVENUE-1-VISION-VERDICT.md`](liber-primus/analysis/vision/AVENUE-1-VISION-VERDICT.md) |
| — | **Stego** | OutGuess 0.4 (source-built) + steghide/stegseek on all page images; provenance: 56/56 SHA1 match onion7 | CLOSED — no payload on rune pages; images are vector renders | [`analysis/stego/STEGO-VERDICT.md`](liber-primus/analysis/stego/STEGO-VERDICT.md) |
| — | **Transcription** | 3-way rune-stream cross-diff (krisyotam/relikd/rtkd) | CLOSED — 13136/13136 identical; consensus corroborated | [`analysis/transcription/TRANSCRIPTION-VERDICT.md`](liber-primus/analysis/transcription/TRANSCRIPTION-VERDICT.md) |
| VI | **OSINT** | Deep external sweep for a numeric/structured key artifact; 67 claims → 25 adversarially verified | **PARTIAL — reopened a live surface.** Several artifacts confirmed dead; **4 concrete leads never run** | [`analysis/osint/CAMPAIGN-VI-OSINT-FINDINGS.md`](liber-primus/analysis/osint/CAMPAIGN-VI-OSINT-FINDINGS.md) |

Campaign VI is the important one: it did **not** confirm total closure — it found that
a small, concrete set of external-key experiments were never actually run. Those are §4.

---

## 3. Do-not-redo (eliminated with reasons)

Full list in
[`LP2-ANALYSIS-SUMMARY-2026.md` §5](liber-primus/LP2-ANALYSIS-SUMMARY-2026.md).
Compressed:

- **Running keys** — every book/esoteric text (see Campaign III), solved-page text,
  Cicada PGP prose, the Rune Poem. Ruled out by **mechanism** (§1.1), not just trial.
- **Additive keystreams** — primes, totient, Fibonacci, OEIS A061474, prime-counting,
  CFB, autokey, first-differencing, page-on-page keying, φ(prime)/prime−1.
- **Vigenère** all key lengths; per-page exhaustive L1–4 + interrupter beam, hill-climb
  L4–12; Atbash/shift.
- **Hill cipher** 2×2 exhaustive (all 682,080 matrices) + 3×3 sampled.
- **Fractionation/bifid, transposition-only, monographic substitution** — ruled out by IoC.
- **Multiplicative/number-theoretic gematria** — mechanistically excluded (no closed group).
- **Structure/representation** — off-diagonal bigrams, n-gram repeats, periodicity (lags
  2–30), inter-page shared keystream, word-boundary bias, runes-per-line stream — all null.
- **Forensics** — OutGuess/steghide/stegseek, LSB/DCT, EOF/EXIF, PGP RSA soundness — clean.
- **OSINT dead ends** — 2017 "Beware false paths" PGP (auth-only, no key material),
  page-32 numeric matrix (doesn't exist), onion cookie hashes & magic-square streams
  (tested as keys), base-60-indexes-the-files (false).

**Do not re-run any of the above.** If you have a genuinely new mechanism, note *why*
it escapes §1's two proofs before spending compute.

---

## 4. The OPEN surface — Campaign VII

Ranked by expected value. Each lead is something **no one in this project (and, per
OSINT, likely no one publicly) has actually run.** All are cheap relative to a solve.

> **▶ Campaign VII progress (2026-07-07).** Executed B1, B3, and the direct-key form of
> A2 — **all null** (best −6.72). But A1 is **resolved with a real discovery**: relikd
> pages 49–51 are base-60 **token tables (256 bytes) that our rig excluded** and had
> never tested as a key. That's now the concrete frontier. Full writeup:
> [`analysis/campaign7/CAMPAIGN-VII-FINDINGS.md`](liber-primus/analysis/campaign7/CAMPAIGN-VII-FINDINGS.md).

### Track A — Page-numbering reconciliation (PREREQUISITE, do first)

**Lead A1 — Resolve community page numbers → relikd image indices.** ✅ **RESOLVED
(2026-07-07).** scream314's catalog is the Rosetta Stone (scream314 jpg = relikd index
+ 17). Key result: **relikd pages 49/50/51 are the base-60 token tables** — and our
rig's `%`-split page set *excluded* them (non-runic), so they were never attacked. See
Campaign VII findings. The reconciliation below stands as context:
Campaign VI's single strongest lead is a community claim that "**pages 49–51 are not
runic prose but a ~250-element table of two-char base-59/60 tokens**" — a *different
data type* than the OTP-runic model. **But verified 2026-07-07:** in our rig (relikd
image-numbering) indices **49/50/51 are ordinary runic pages** (66 / 92 / 263 runes).
So the community's "pp49–51 data" is at **different physical pages** — community
numbering diverges from relikd image-numbering past ~p34.

- **Action:** build the explicit map between community page numbers and relikd image
  indices across the whole book (align on the solved/known pages as anchors — SOME
  WISDOM, A WARNING, AN END, the parable pages). Locate *where the token table actually
  lives* in the relikd set — or establish that it is not in our set at all (e.g. a
  segment only present in a different scan/host).
- **Run sketch:** cross-reference `liber-primus/SOLVED-PAGES-AND-INTERRUPTERS.md` +
  the relikd page images against the uncovering-cicada wiki "Unsolved Pages" numbering;
  emit a `PAGE-MAP.md` table (community-# ↔ relikd-index ↔ content-type ↔ status).
- **Resolved when:** every community page number has a relikd index or an explicit
  "not in our set," and the token-table page(s) are pinned. **Blocks A2, B2.**

**Lead A2 — The pp49-51 token pad as key/pad.** ⚠️ **PARTIALLY RUN (2026-07-07).**
The token bytes are already decoded (scream314): 256 bytes total, 161 distinct (**not a
permutation/S-box**). Tested as a **direct mod-29 additive keystream** (each page, concat,
XOR combos, both orders) against every runic page + whole book → **null, best −6.72.**
Still **OPEN** in these untested forms (Campaign VII findings §"what this does NOT rule
out"): (1) token pages as their *own* ciphertext; (2) **byte-domain** XOR against runes
(not mod-29); (3) XOR against the 2014 onion hex (Lead B2); (4) corrected p50 re-read
(scream314 flags its p50 decode "wrong!!!").

### Track B — Untested external key artifacts (run against the runic pages)

All of these are concrete, Cicada-authored or Cicada-adjacent numeric data that were
**never tried as keys** against the rune pages. Apply each as a Gematria-Primus-indexed
polyalphabetic shift **and** as an XOR/mod-29 additive keystream, with and without the
interrupter rule, per-page and whole-book.

- **B1 — 2012 Mayan rotation key** `10 2 14 7 19 6 18 12 7 8 17 0 19`. ✅ **RUN → null
  (−6.895).** Confirmed Cicada key; forward/reversed × sign × atbash × interrupter,
  per-page + whole-book, all noise. CLOSED. (Campaign VI lead #3.)
- **B2 — XOR pp49–51 token data ⊕ 2014 onion-trail hex.** ✅ **RUN → null (−6.597).**
  Both sides sourced and vendored (token pad + 2nd/3rd/4th onion hex, each exactly 256
  bytes → clean full-length XOR). The op a wiki author proposed and nobody ran is now
  run: the XOR stays random (entropy ~7.1, no payload) and is null as a key. CLOSED.
  (Campaign VI lead #2 — was the highest-novelty operation.)
- **B3 — `HINTS-NEVER-USED.md` numerics as Gematria keys.** ✅ **RUN → null (−6.757).**
  P.S. digit string (3 readings: digits / 2-digit groups / big-int base-29), telnet
  missing-primes + first-difference gaps, all four trailing-space sequences. Every
  stream in noise. CLOSED. Data vendored at
  [`sources/community/krisyotam_HINTS-NEVER-USED.md`](sources/community/krisyotam_HINTS-NEVER-USED.md).
  (Campaign VI lead #4.)
- **B4 — page-56 512-bit hash as key seed.** ✅ **RUN → null (−6.679).**
  `36367763ab73783c…132c2a8b4` expanded 5 ways (raw bytes, hex-digits, SHAKE-256,
  SHA-512 chain, BLAKE2b chain) → mod-29 keystream, full sweep. All noise. CLOSED.
  (Campaign VI lead #5.)

- **Resolved when:** each artifact has a committed result JSON under
  `analysis/campaign7/` with best score and a one-line verdict; readable English
  (score > −5.0) on any = **potential break — escalate immediately.**

### Track C — Novel mechanism attacks (respect §1's proofs)

These are new *because* they target the filtered-keystream fingerprint rather than
assuming a plain running key.

- **C1 — Filtered-keystream inversion.** Model the encoder as "mod-29 additive stream
  whose output was soft-rejection-filtered to suppress adjacent repeats," and attempt
  to *invert the filter* to recover keystream constraints. Prior work only tested
  *memoryless* keystreams (excluded by the doublet deficit). This is the one mechanism
  consistent with the actual fingerprint that has **not** been attacked directly.
  Start from [`analysis/seek_primes.py`](liber-primus/analysis/seek_primes.py)
  (history-dependent prime transforms) and generalize.
- **C2 — Per-thematic-set keying.** The onion7 margin art groups pages by set
  (Babylonian sexagesimal on 34–39; mayfly/"ephemeral" on 24–26/57/14; dendrites on
  8–14/32/55), weakly suggesting per-set cipher *variation*. Attack each set with the
  key *type its art hints at* (base-60 numeric keying on 34–39; treat the mayfly set as
  OTP; etc.) rather than one global method. Not the same as the closed per-page sweep —
  the grouping and matched key-type are the new variables.

- **Resolved when:** each has a committed probe + result; null closes it with a reason.

### Track D — External / OSINT long-shots (low odds, non-zero)

- **D1 — CT-logs brute force for the "AN END" deep-web hash.** Hash early-2014
  Certificate Transparency log entries against `36367763…c2a8b4` across the candidate
  algorithm set (tweqx/dwh-check). Only place a key might physically persist; Tor v2
  host is dead. Documented in
  [`analysis/DEEPWEB-HASH-OSINT.md`](liber-primus/analysis/DEEPWEB-HASH-OSINT.md).
- **D2 — Non-English & fresh-host transcription hunt.** Confirm no *independent*
  (non-rtkd-lineage) transcription exists anywhere, including a possible alternate scan
  that contains the token-table pages our relikd set may lack (ties to A1).

---

## 5. Execution order (Campaign VII)

Cheapest-and-highest-leverage first; each writes to `liber-primus/analysis/campaign7/`.

- ✅ **B1 (Mayan key)** — RUN, null (−6.895).
- ✅ **A1 (page-map)** — RESOLVED; discovered relikd 49–51 = token tables excluded from rig.
- ✅ **B3 (HINTS numerics)** — RUN, null (−6.757).
- ⚠️ **A2 (token pad as direct key)** — RUN, null (−6.72); refined forms still open.

- ✅ **B2 (token ⊕ onion hex)** — RUN, null (−6.597); XOR stays random, no payload.
- ✅ **A2 refined (token as its own ciphertext)** — RUN, null; no readable ASCII decode.
- ✅ **B4 (page-56 hash as KDF)** — RUN, null (−6.679).

**All cheap self-contained key artifacts are now exhausted (every one null).** The
token pad behaves as true OTP/random data. What's left needs new *external* input or
heavier machinery:

1. ✅ **C1 — doublet-avoiding running key** — RUN (bounded), null (−6.086). Beam search
   over the key-skip trajectory vs 3 major texts; answers finding #2's objection but does
   not break. The best-motivated computational mechanism is now tested and negative.
   *(Remaining C1 surface: more candidate texts — but finding #2 argues no natural text
   works, and the 3 tested are null.)*
2. **Corrected p50 transcription** — scream314 flags its own p50 base-60 read "wrong!!!";
   a re-read of the p50 token glyphs from the image could change 104 of the 256 pad bytes.
   Needs the page image + careful transcription (external input).
3. **C2 (per-thematic-set keying), D1 (CT-logs hash brute), D2 (fresh-scan hunt)** —
   long-shots; background/opportunistic.

**Guardrail:** before running anything, check it against §3. Every run commits a
result JSON + a one-line verdict so this ledger stays the source of truth. Any score
> −5.0 (readable English) halts the campaign and escalates — that is the solve.

---

## 6. Standing watch (the only things that change the verdict from outside)

If LP2 is a true OTP, no ciphertext-only attack can *ever* succeed. The genuine
game-changers are external and worth a passive watch:

- **A new Cicada 3301 release / key publication.** They have been silent since the
  verified 2017 message. A key or new puzzle surfacing is the cleanest path.
- **The unfound "AN END" deep-web page** actually being recovered (D1).
- **A genuinely independent transcription** that diverges from rtkd canon at a load-
  bearing rune (Campaign V says none exists today; D2 keeps looking).

Everything else is us hammering the small open surface in §4 until it's all closed or
one of the artifacts reads English.

---

_This roadmap supersedes the "4 avenues closed" framing in earlier notes: Campaign VI
reopened a concrete surface. Keep this file current — it is the master record of what
we've dug and what's left._
