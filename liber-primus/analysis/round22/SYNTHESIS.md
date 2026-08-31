# Round 22 — SYNTHESIS (bounds, not a verdict)

_Written 2026-08-31 by the coordinator, from the five lane `RESULTS.md` files as filed on
2026-08-29. Doctrine [`ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) R7: measured bounds and
reopening conditions only. Trust anchor `python tests/validate.py` → **ALL VALIDATIONS PASSED
(5/5)** before and after every lane; `validate_ledger.py` Unsound negatives = **0**. Ledger
entries: `R22-A-SELFEMBEDDED-READ`, `R22-B-TURTLE-SPATIAL-RENDER`, `R22-C-LITERAL-IMPERATIVES`,
`R22-D-ILLUSTRATION-DROPCAP`, `R22-R-REDTEAM` (130 → 135)._

> **Filed late** (the round closed into `PICKUP-HERE.md` and the ledger but never got its own
> exit document). Nothing here is new measurement; it is the round-level record of what the five
> lane files already establish.

---

## 0. The one-line result

After Rounds 16–21 spent nearly their entire budget on the letter-stream PRNG/seed branch,
Round 22 turned and — **for the first time in the project's history — read every channel the
signed hints actually point at**: the hidden message *inside the already-solved plaintext* (X2),
the *numbers-as-direction* turtle render (G1/G3), the *koans-as-operations* (X1/X3/X4), and the
*art-as-data* drop-cap channel (S3). **All four came back clean, control-validated NEGATIVES**,
and the red-team lane returned **NO-ERROR-FOUND** on the round's own reasoning. Combined with
Round 11 (N1–N5, S1–S2), every roadmap lens the hints name has now been read at least once at the
tested resolution.

**There is no HIT and no flagged-for-oracle survivor anywhere in the round.**

---

## 1. Per lane: what was read, at what coverage × power, and what reopens it

### Lane A — X2, self-embedded read of the SOLVED plaintext — NULL
- **Coverage:** 3,508 selection functions — every-k for k ∈ [2,40] at all offsets, reversed
  every-k, diagonal / anti-diagonal folds w ∈ [2,60] — over the 5 rig-solved pages (1,887
  letters / 1,769 rune indices, book order), in both a letter stream and a rune-index stream.
- **Power:** Phase-0 planted every-7th and width-13 diagonal acrostics both recover as the top
  selection, **recovery 1.000**.
- **Result:** **0 family-wise survivors**; 6 per-cell FPR=0.001 crossers against 3.5 expected by
  chance — noise, all gibberish (best −5.37 vs real English ≈ −2.2). Secondary language-agnostic
  panel (IoC·N, min-distinct-32, base32 fraction, gzip) flat.
- **Instrument note:** width-w main diagonal ≡ every-(w+1) at offset 0 (subsumption disclosed).
- **Reopens:** the one representation this lane could not build — a first-rune-of-each-**printed
  line** acrostic at true page-image geometry. _(Run the next round: R23-A2, also NULL.)_

### Lane B — G1 turtle render + G3 pointer decode — CLEAN NULL
- **Coverage:** the value / π(p) / φ(p) stream of LP2 0–54 drawn as a turtle path across the full
  frozen enumeration: 3 streams × turn-moduli {4,6,8,12,29,360} × {absolute, relative} × {unit,
  value-step} = **72 render combos**, against a 6-stat geometry detector (closure,
  self-intersections, bbox-fill, caging, symmetry, components) and a size-matched
  histogram-preserving seed-3301 shuffle null (200/combo, refinement at N=2000/10,000).
- **Power:** Phase-0 planted closed square fires **5/6** stats (self-intersections ~170× the null
  mean); planted square-wave fires 2. The detector provably sees a made figure.
- **Result:** every render is what it mathematically is — a **constrained lattice random walk**.
  6 shape-stat p<0.01 candidates all fail the frozen family-wise flag gate (empirical floor ∧
  Bonferroni z-tail 2.3×10⁻⁵); **0 flagged-for-oracle**. G3 base32/onion/lat-long:
  **POINTER_FOUND = False** — base32 low-entropy runs at or below the shuffle null, 0 lat/long
  matches, coord-pair rate below null.
- **Novel artifact:** nobody had ever rendered LP2's number stream as a path.
- **Reopens:** non-turtle 2D reads (columnar at true line width — "Lane G2"), other moduli /
  step functions, 3D lifts, prose-along-path.

### Lane C — X1/X3/X4, the koans executed as OPERATIONS — NEGATIVE
- **Coverage:** **185 enumerated operations** over LP2 0–54 (12,956 runes): X1 every-4th
  decimation ×4 phases + cipher ladder, iterated ×{2,3,4}, 4-way interleave/de-interleave; X3a
  whole-stream reversal re-enciphered forward; X3b solved-plaintext as a running key; X4
  prime-value / prime-index / totient keystreams (±sign, ±atbash). All adjudicated by the
  repaired 9-register panel-max bar; keyed operations additionally gated by `hitfn20.is_hit`.
- **Power:** all four Phase-0 plant-and-recover controls at **recovery 1.000** (X3b/X4 held-out
  1.000, `is_hit=True` on the plants).
- **Result:** **0 survivors.** Best structural pmax 1.53–2.6 against bars ≈ 4.7–5.1. Four keyed
  decodes cleared 0.90 recovery but sat at pmax 2.4–2.9 — **correctly rejected at the panel-max
  clause; the exact hallucination pattern the recovery gate exists to catch.** The X4-totient
  cell legitimately re-adjudicates Round-11 N5 under the repaired instrument and **re-confirms
  NEGATIVE**. The size-matched seed-3301 null was equally empty — the real stream is statistically
  indistinguishable from its histogram-preserving shuffle under every operation.
- **Reopens:** operations outside the enumerated 185 (deeper iteration, other braid widths),
  keystreams from number-theoretic functions not in {value, index, totient}.

### Lane D — S3, illustration / drop-cap channel — NEGATIVE, and RUNNABLE after all
- **Asset verdict first:** this channel was long assumed blocked-on-assets. It is not — the 58
  full-page scans are **in-repo**, and the drop-cap is a single large **red** glyph separable by
  a colour mask with no OCR (the old 0.145 vision-OCR closure does not apply).
- **Coverage:** the first LP2 drop-cap catalog (`features.json`): **15/58 pages illuminated**
  (0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54, 56, 57 — 15 is not prime, not 29, not a
  distinguished value); illuminated runes in page order read `SLXHXFUMDSFAINGP` — not English,
  not base-29/ASCII. Presence, order, gap, centroid, and identity each tested against a
  size-matched seed-3301 null (10,000 shuffles).
- **Power:** extractor reproduces 4/4 hand-read pages and page 0's red **S**.
- **Result:** **min p = 0.18**; nothing approaches the Bonferroni p<0.01 bar.
- **Reopens:** the **figural-motif** channel (crosses / trees / shrouded-corpse / mayflies) is
  documented but not yet coded as data — it needs hand annotation or a control-validated
  black-channel shape extractor first.

### Lane R — red-team (doctrine R6) — NO-ERROR-FOUND
- Independently **recomputed** Lane B's family-wise correction from the raw ledger rows (not the
  summary): per-stat counts reproduce exactly; 6 observed shape-stat hits vs 2.88 expected is
  P(≥6) ≈ 0.072 (Poisson) / 0.071 (binomial) — **consistent with multiple-comparisons noise**;
  the 4.7σ 'components' candidate is a discrete-stat z-tail artifact (empirical p = 0.012).
  **B's 0-flagged-for-oracle is SOUND.**
- No lane silently re-reads a Round-11 negative (Lane C's X4/N5 disclosure explicit); all nulls
  seed-3301; **no −5.5 relapse**; no lane rests on an unvalidated instrument.
- One low-severity, non-blocking disclosure gap: B's G3 coord-pair sub-detector partially overlaps
  Round-11 N2's route (d). **Fix applied in-round** — B now cites N2.

---

## 2. What Round 22 moved, and what it did not

**Moved.** The strongest standing objection to the project — *"you ground the letter stream for
ten rounds and never once read the channels the authors signed and pointed at"* — is now **largely
closed at the tested resolution.** Every one of those reads is control-validated, family-wise
adjudicated, and red-teamed. Two durable artifacts exist that did not before: the drop-cap catalog
and the turtle-render suite.

**Did not move.** The standing verdict — **LP2 0–54 is OTP-class**, with a soft anti-repeat
rewrite on the ciphertext output — is unchanged; no lane here touched the letter-stream key space
at all. The PRNG/seed tail (bounded, not closed) and the `/dev/urandom` branch are exactly where
Round 21 left them.

---

## 3. Live threads leaving Round 22

1. **A2 — the printed-line-geometry acrostic** (Lane A's named reopener; the most conventional
   hiding place for a self-embedded message, and cheap: a line-break transcription plus a re-run
   of A's validated recognizer). _This became Round 23, and returned a clean NULL._
2. **D2 — the figural-motif channel**, gated on building a control-validated motif extractor
   before any scoring.
3. **B2 — non-turtle 2D / columnar reads at true line width** (Lane G2).

The completeness-critic's honest-prior note from the round stands: after item 1, the remaining
reopeners are resolution gaps inside channels already read clean, not new channels — and all
three of this project's past reopenings came from auditing an instrument or a closure, not from
one more framing of an already-read channel. See `NEXT-ARMADA-ROADMAP.md` → "ROUND 23 SEED".
