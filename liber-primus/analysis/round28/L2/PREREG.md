# L2 — contested-bytes: adjudicate the 6 contested canon_256 cells + variant-enumerated keytest

_Round 28, pre-registered 2026-09-08. Mode: run-now-light._

## Hypothesis

One or more of the six contested payload cells (indices **25, 175, 182, 199, 215, 237** of
`analysis/pp49_51/canon_256.bin`) is wrong in canon, and because the payload's downstream
uses are avalanche-sensitive (B-05's own control: one flipped byte drops recovery
−4.170 → −7.38), every canon_256 negative is conditional on these bytes. Resolving them —
or exhausting their reading-variant product — converts conditional negatives into
unconditional ones, and could surface a key.

## Anti-repeat (ledger ids extended)

- **`B-05`** (negative): swept payload representations × PRF constructions, with the 6
  contested bytes covered only as a **sensitivity dimension** (its own coverage text) — it
  never adjudicated their values, and P-7's interim Cartesian-enumeration procedure was
  never executed (no ledger row, no artifact in `pp49_51/`).
- Campaigns VII / IX / XX (`pp49_51/CAMPAIGN-*-FINDINGS.md`): flagged the cells as
  contested; none resolved them. `pp49_51/canonicalize.py` line 108 prints the
  majority-vs-decimal-preferred delta — the witness disagreement is measured, unresolved.
- The 99.2% rune classifier is RUNE-trained and structurally cannot read these Latin/digit
  glyphs (P-7) — no prior instrument covers this read.

## Aiming Test

**Q1 — Hit shape + recognizer.** Two deliverables, each with its recognizer written first:
(a) **A read**: for each contested cell, a same-page template-match adjudication (crop the
glyph cell from the master page images in-repo; build per-glyph templates from the ~250
UNCONTESTED cells of the same three pages; normalized cross-correlation; top-1 vs top-2
margin recorded). AI-vision reads are **advisory only**, never adjudicating. (b) **A
decode**: any variant stream that clears the variant-corrected keytest bar. **Positive
controls before any null counts:** (a) template reader must reproduce `canon_256.bin`
**100/100** on a blind sample of uncontested cells (P-7's own gate) — below 100/100 the
reader is not trusted and the lane falls back to enumeration-only; (b) plant: run
`keytest.py` on a stream deliberately seeded with a known-good construction (its existing
self-check) and confirm the battery's detector fires.

**Q2 — Measured fact above flat prior.** The witnesses **measurably disagree at exactly
these 6 cells** (canonicalize.py's printed delta), and B-05 **measured** single-byte
avalanche sensitivity. This is doctrine R5 class 1: a finite, human-checkable object
(6 cells), the highest-ranked object class in the doctrine.

**Q3 — Bounded?** Fully enumerable: 6 cells × the per-cell plausible-reading sets taken
from the witness tables (each cell has 2–4 candidate readings recorded across
relikd/majority/decimal-preferred witnesses) ⇒ Cartesian product **≈64–4,096 variants**,
hard-capped at 4,096. The keytest battery is seconds per variant single-threaded; worst
case ≈ a few hours at nice 15. 100% of the enumerated product will be covered.

**Q4 — Three conditionals of the negative:**
1. key space: the enumerated reading-variant product (readings drawn from the recorded
   witnesses — a genuinely novel glyph value outside all witnesses is not covered);
2. transition model: the constructions inside `pp49_51/keytest.py`'s battery (and B-05's,
   if a byte flips and the B-05 harness is re-run) — nothing outside them;
3. register: the battery's English-led scoring (L7-A conditional).

**Q5 — Kill at 10%.** If the template reader scores <100/100 on the uncontested control,
kill the read half immediately (fall back to enumeration-only — the lane still completes).
If keytest throughput makes 4,096 variants exceed 6 h, cap the product by per-cell margin
ranking (keep top readings per cell) and state the cap in coverage.

## Bars

- Read half: a cell's canon value is **changed** only if the template match is unambiguous
  (top-1 = a non-canon reading with margin ≥ the minimum margin observed among correct
  reads in the 100-cell control) on ≥3 independent crops/passes. Anything weaker: cell
  stays contested, recorded per-cell.
- Decode half: keytest family-wise bar recomputed for the variant count (adding N variants
  multiplies the space by N — recompute the null on the enumerated family, per P-7; the
  single-payload bar is NOT reused). Any crosser → hitfn20 + FLAGGED-FOR-ORACLE.
- If any byte flips: re-run the cheap canon_256 keytest battery on the corrected stream,
  and file the C-canon governance flag (do not decide canon promotion inside this lane —
  that is the coordinator's open item `C-CANON-PAYLOAD-3BYTES`).

## Coverage promise (honest)

Delivered: 6/6 cells adjudicated-or-explicitly-still-contested + 100% of the (possibly
capped, stated) variant product through keytest. Not covered: readings outside all recorded
witnesses; constructions outside the battery; B-05's full PRF grid re-run unless a byte
actually flips (then only the corrected stream is re-swept, disclosed).

---

## AMENDMENT 1 — 2026-09-08, before any run (anti-repeat audit re-scope)

The mandatory anti-repeat audit against `LEDGER.json` **falsifies part of this lane's
premise**, and the lane is re-scoped accordingly BEFORE any control or null is run.

**What the audit found (coverage/not_covered fields, not status):**

1. **`A-04` (Round 19 C1, status eliminated/RESOLVED)** already adjudicated ALL 11
   witness-conflict cells with a validated pixel instrument (blind 40/40 calibration gate,
   100% on the case-ambiguous subset, single-template-regime control 100% case-ambiguous,
   global separation licensed over 29,161 pairs). Verdict: the 6 pre-registered contested
   cells (25/175/182/199/215/237) all resolve to the MAJORITY value already in
   `canon_256.bin` (0 flips); 3 token-split cells flip (45→107, 50→47, 246→198) producing
   `round19/C1/payload_resolved.bin` (sha256 3b9b07d9…b290). The planner's claim "no ledger
   row adjudicates their values" is **wrong**; this lane may NOT present a fresh
   adjudication as novel.
2. What A-04 explicitly does **NOT** cover (its `not_covered` / `reopens_if`):
   (e) an **independent BLIND transcription** of the 11 conflict cells — C1's second-reader
   pass was non-blind, L5's "blind passes" are an unverifiable hard-coded table; the named
   reopening condition is exactly such an independent blind read disagreeing;
   (a) cells **186, 210, 211** never adjudicated by the pixel instrument (segmentation
   failure), (b) cell **209** objectively mis-segmented — all four unchallenged, unverified.
3. **`B-05`** covered the 6 contested bytes as a sensitivity dimension and (per its
   `reopens_if`) ran "single-position sweeps and the 64 all-combination masks" — but ONLY
   through its PRF-expansion grid. The direct-key battery `pp49_51/keytest.py`
   (additive/Beaufort/atbash, per-page, offset sweeps) has only ever been run on the
   `maj` and `decpref` streams; it has never been run on the contested-cell Cartesian
   product nor on `payload_resolved.bin` (C1's propagation re-ran the B-05 PRF grid only).
4. `C-CANON-PAYLOAD-3BYTES` remains an open coordinator flag; this lane still does not
   decide canon.

**Re-scoped deliverables (bars unchanged, hit shape unchanged):**

- **Read half** → an INDEPENDENT BLIND read: new segmentation + normalized-cross-correlation
  template classifier built in this lane (no reuse of round18/L5 `grid.py`/`pixelmatch.py`
  code), templates labeled ONLY from witness-unanimous cells (never from canon at conflict
  cells), gated at **100/100** on a blind sample of 100 witness-unanimous cells in the
  single-template regime. Read targets: the 11 conflict cells (blind, then compared to
  A-04's verdicts — agreement closes A-04 not_covered(e) as far as one more independent
  instrument can; disagreement triggers A-04's reopens_if) **plus** cells 186/210/211/209
  (A-04 not_covered(a),(b)) if this lane's independent segmentation succeeds on them.
- **Decode half** → variant-enumerated `keytest.py` battery, family-bar-corrected:
  the pre-registered 2^6 = 64 contested-cell product on the canon majority base **and**
  the same 2^6 product on the `payload_resolved` base (45/50/246 corrected) = **128
  variants** (`canon_256_decpref.bin` is a corner of the first set; `payload_resolved.bin`
  is a corner of the second; per-cell readings remain the 2 recorded witness values).
  The full 2^11 joint product over all 11 conflict cells (~2,048 variants ≈ 18 h at the
  measured 32 s/variant single-threaded) exceeds the run-now-light budget and goes to
  not_covered unless time remains after the front.
- **Bar** → Gumbel family-wise threshold fitted from THIS battery's own null order
  statistics (shuffled-payload keys through the identical battery, two-N fit per
  `benchmark/null.py`'s calibration doctrine), evaluated at the full family size
  (~21.6 M configs); the historical −5.2 single-battery bar is reported but NOT used
  as the decision bar.
- **Plant control** (before any null counts): a synthetic target enciphered with a known
  variant/config/offset must be recovered by the actual sweep code at ≥0.90 rune recovery
  and must clear the family bar.
- **R3 stats** per sweep row (variant × target, best config): score_norm, IoC·N,
  min-distinct-32, zlib ratio, best non-English register (I2 panel).

Throughput fact recorded pre-run: one keytest battery (2 payload variants + reverses,
337,944 configs) = 63 s wall at nice 15 single-threaded, measured 2026-09-08.
