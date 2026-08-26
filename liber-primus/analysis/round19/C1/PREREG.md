# Round 19 · Lane C1 — CLOSEOUT of Round 18 L5 (PAYLOAD) · PRE-REGISTRATION

_Written 2026-08-26, **before** any script in this folder was run and before the E-01 test
existed. Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

## 0. Scope and inheritance

C1 closes out Round 18 lane **L5-payload**, whose `PREREG.md`
(`analysis/round18/L5-payload/PREREG.md`) is **binding and inherited verbatim**. Nothing in
it is restated, relaxed, tightened or re-scoped here. In particular the following L5
thresholds carry over unchanged and this lane reports against them:

| inherited from L5 PREREG | threshold |
|---|---|
| A.3 calibration gate | ≥ 38/40 exact-token agreement on the seeded 40-cell blind sample |
| A.3 | case-ambiguous-subset accuracy reported **separately** |
| A.4 | RESOLVED iff ≥ 3 independent passes concur **and** the calibration gate passed; else STILL-CONTESTED |
| A.2.1 | image/canon SHA-256 must match `handoff/capsule/MANIFEST.json` or the lane stops |
| A.2.2 | grid must yield exactly 80 / 104 / 72 cells |
| A.5 | payload-consuming tests keep their own pre-registered bars; scored bars are recomputed with `benchmark/null.py: threshold_for()` for the variant count |
| B.1 / B.5 | E-01 is a **zero-false-positive structural** test: HIT = structure match, no structure = null. No tunable threshold |
| B.4 | E-01 requires a mandatory positive control: the matcher must fire on a genuine signature and produce **zero** false positives on 10,000 random blocks of the same length, or the E-01 result is reported as instrument failure |

L5's §0 records that its pipeline was built by an agent killed by an infrastructure fault, and
that a later agent re-derived §§1–3. **C1 trusts neither transcript.** Every claim in L5
`RESULTS.md` §§1–3 is re-derived in this folder from the on-disk artifacts, and `round18/L5-payload/`
is treated as read-only input except for writing its completed `RESULTS.md` at the end.

L5's `RESULTS.md` §§4, 5 and 6 (propagation, E-01, coverage) are unwritten. Those are C1's
work, and the new thresholds they need are pre-registered in §2 and §3 below.

---

## 1. The Aiming Test (doctrine §1) — answered for C1

### Q1 — What would a hit look like, and would *this* instrument recognise it?

Two different hits, two different recognizers.

**A-04.** A "hit" is *a byte of the payload that the image says is not the byte the repo has
been using*. The recognizer is nearest-exemplar glyph matching on native-resolution bitmaps
(`pixelmatch.py`), and it is proved able to emit that outcome before it is asked to: its
leave-one-out control classifies 236/237 uncontested trailing symbols and 242/242 leading
digits, i.e. it demonstrably *does* return the true class, and it demonstrably returns a
**wrong** class when the input is damaged (idx 209, a mis-segmented `t`, is classified `0`).
An instrument that only ever agreed with `canon_256.bin` would not be recognising anything;
this one disagrees with it where the pixels disagree with it.

The load-bearing weakness that C1 must close is stated in L5 `RESULTS.md` §1.3 and is real:
the classes `I`, `i`, `l`, `R`, `h` have exactly **one** uncontested exemplar each, so
leave-one-out cannot test them — and four of the six pre-registered cells are decided by
`I` vs `l`. C1 therefore adds a **new control (Control 3, §2.1)** that measures accuracy in
exactly the one-template-per-class regime those cells are decided in.

**E-01.** A hit is a `pow(s, e, n)` output carrying PKCS#1 v1.5 type-1, v1.5 type-2 or
PSS structure. The recognizer is a structural predicate, and PREREG B.4 already requires it
to be planted: a locally generated RSA key signs a message with genuine v1.5 and genuine PSS,
and the matcher must fire on both. The plant is the actual shape, not an analogue.

### Q2 — What measured fact raises this family's prior above the flat rate?

**A-04.** Two, both measured on the held artifact.

1. `round18/L1-toolchain/RESULTS.md` establishes the pp49–51 pipeline as
   ImageMagick-over-Ghostscript from typeset source. That is a *physical* claim with a
   testable consequence — a deterministic renderer emits the same glyph as the same bitmap —
   and L5's Control 1 measures it: mean within-class native-bitmap IoU **0.9948** over 54
   classes, against a maximum between-class IoU of **0.908**. Glyph reading on these pages is
   therefore a lookup, not a scoring problem. Nothing about a hand-scanned page would license
   that.
2. `analysis/pp49_51/canonicalize.py` finds **11** disagreeing cells among 256 and resolves
   them with a tie-breaker (scream314's derived decimal column) whose reliability was never
   measured. A tie-breaker of unmeasured reliability standing between the repo and 11 bytes of
   a 256-byte object is a concrete, bounded defect, not a hunch.

**E-01.** `analysis/round16/zeroFP/zerofp_tests.py` records in its own source that the
4096-bit moduli "not on disk (fetch was planned but not done)", and then justifies not
fetching them with the claim that *"under a 4096-bit modulus, `pow(s,e,n)` would trivially
return s^e as-is (s << n), so PKCS1 padding is impossible."* That justification is
arithmetically false for every exponent > 1 (`s` is 2048-bit, `s^3` is ~6144-bit, `s^65537`
is ~1.3×10⁸ bits; both reduce mod a 4096-bit `n`). The measured fact raising the prior is
therefore not about 3301 at all — it is that **the reason E-01 was left partially-run does
not hold**, and the moduli turn out to be on disk under ten witnesses
(`round18/L5-payload/moduli.json`). This is a closure audit, which doctrine §0 ranks as the
activity that has actually produced findings here.

### Q3 — Is the space bounded, and by what?

Both items are **finite and fully enumerable**; neither is sampled.

- **A-04:** 11 conflict cells × 2 glyphs × ≤ 60 candidate classes = **≤ 1,320** comparisons,
  and in practice 11 × 2 × (5 digit classes + 54 symbol classes). Doctrine R5 rank **1** —
  a finite, human-checkable object.
- **E-01:** |moduli| × |exponents| × |encodings| × |payload variants| =
  3 × 3 × ≤4 × 3 ≈ **≤ 108** modular exponentiations, plus the broadened key scan over all
  301 key-shaped files in `corpus/` + `liber-primus/`. Enumerable in seconds. The space is
  bounded by *what 3301 actually published*, which is why it is small.
- **Propagation:** the resolved payload differs from `canon_256.bin` at 3 indices, none of
  which is one of the 6 that B-05 swept. The re-run space is B-05's own pinned Part-1 grid
  restricted to the resolved-payload representations: 6 reps × 15 generators × 224 = **20,160**
  decodes, exhaustive over that grid, not sampled.

### Q4 — What are the three conditionals the negatives will carry?

**A-04** is not a key-space search and the three conditionals do not apply in their usual
form; its analogous three are stated explicitly in RESULTS §6 (exemplar set, segmentation
model, class alphabet).

**E-01's** null carries: (1) **key space** = the enumerated published-3301 modulus set and
exponent set, with the un-fetched onion-message moduli named as not covered; (2) **decoder /
transition model** = raw `pow(s,e,n)` under the four listed integer encodings, i.e. it cannot
see a payload that is a *fragment* of a signature, or one that was blinded, or one under a
modulus 3301 never published; (3) **adjudicator register** = the three padding schemes
matched (v1.5 type 1 with DigestInfo, v1.5 type 2, PSS/MGF1), i.e. it is blind to raw
unpadded RSA, OAEP, and any bespoke padding.

**The propagation negative** inherits B-05's three conditionals verbatim, and — this is the
point of stating them — inherits Round 18 L7-A and L7-B in full: it is an **English-only**
negative produced by a decoder that can represent exactly one rejection-loop implementation.
It is re-run to restore B-05's *arithmetic* validity under the corrected seed, not to claim
new power. Its residual value is explicitly bounded in RESULTS §6.

### Q5 — What single observation would abandon this lane at 10 % of budget?

- **A-04 kill:** L5's Control-2 leave-one-out accuracy failing to reproduce from the on-disk
  artifacts, or the new Control 3 (§2.1) falling below its bar. Either would mean the
  adjudication is unlicensed and the six cells revert to STILL-CONTESTED. **Checkpoint: after
  `pixelmatch.py` and `singletons.py`, before anything is written up.**
- **E-01 kill:** the matcher failing to fire on a genuine locally generated signature, or
  producing any false positive on 10,000 random blocks. Either is instrument failure and the
  E-01 verdict becomes "instrument failure", not "null". **Checkpoint: the control runs
  first, in the same script, before any 3301 modulus is touched.**
- **Propagation kill:** B-05's plant-and-recover control failing to reproduce on the resolved
  payload. Then the re-run is a null from an unvalidated instrument and is reported as such
  rather than as a negative. **Checkpoint: control before sweep.**

---

## 2. New thresholds — A-04 (these are NEW to C1; nothing in L5 is altered)

### 2.1 Control 3 — the single-template regime (`singletons.py`)

**Why.** Cells 25, 175, 182, 199 (pre-registered) and 45, 50, 165, 246 (the coverage
extension) are all decided against a class — `I`, `i` or `l` — that has exactly one
uncontested exemplar in the payload. L5's leave-one-out control cannot measure those classes,
because removing the exemplar removes the class. So the licence L5 claims for them is an
extrapolation from classes that had 2–7 exemplars.

**The control.** Reduce *every* symbol class to exactly one exemplar (the lowest-index
uncontested cell of that class), then classify every remaining uncontested cell by nearest
single template. This reproduces the exact regime the singleton classes are used in, on cells
whose identity is known, and it is measurable.

**Pre-registered bars, fixed here before the script exists:**

- **PASS iff** single-template accuracy ≥ **99 %** overall **and** **100 %** on the
  case-ambiguous subset (`I i l L 1 O o 0 Q W w S s 5 K k V v`).
- **On failure**, every cell decided by a singleton class is downgraded to
  **STILL-CONTESTED**, with the shortlist reported, and the three byte corrections at 45, 50
  and 246 are withdrawn.

### 2.2 Control 4 — global class separation (`singletons.py`)

**The control.** Compute the full all-pairs best-alignment IoU over the 253 segmented
uncontested cells: `min_within` = smallest same-class pair, `max_between` = largest
different-class pair. L5 measured `max_between` only over the ambiguous classes and only from
one exemplar per class; C1 measures it globally.

**Pre-registered bar:** the decision rule "best IoU ≥ `T` ⟹ same class" is licensed for
`T = 0.995` iff `max_between < 0.995 ≤ min_within` over all *correctly segmented* pairs. Cells
whose segmentation is known-bad are excluded and **named**, not silently dropped. If
`max_between ≥ 0.995` the rule is not licensed and every adjudication whose winning IoU is
below the observed `max_between` is downgraded to STILL-CONTESTED.

### 2.3 Physical-discriminator re-derivation

Every physical claim L5 `RESULTS.md` §2.2 makes (`I` = 8×67 px at `dy_top` −1; `l` = 8×74 px
rising 6 px above cap; `L` carries a foot at `wrel` ≈ 0.38 vs `l` ≈ 0.12; `i` carries a
separate dot; `W` is cap-height at `hrel` ≈ 1.07 vs `w` ≈ 0.67) is re-measured from the
images in this lane. Any claim that does not reproduce is struck from the completed L5
`RESULTS.md` and reported as a re-derivation failure.

---

## 3. New thresholds — E-01 (these are NEW to C1; L5 B.1–B.5 are inherited unchanged)

### 3.1 Broadened modulus scan

L5's `extract_moduli.py` globs nine specific paths. C1 re-runs it **and** re-scans **every**
key-shaped file under `corpus/` and `liber-primus/` (`*.asc *.gpg *.pgp *.key`, 301 files)
for OpenPGP public-key and public-subkey packets, computing each v4 fingerprint from the
packet body rather than trusting a filename. Any RSA modulus found that is not already in
`moduli.json` is added to the test set and reported. This is a coverage extension of L5 B.2,
which says "plus any other published 3301 modulus found in `corpus/`".

**Bar:** none — this is enumeration. The *result* is the count, and any modulus of a size
that could carry a 256-byte signature (2048-bit) is called out explicitly, because that is the
size the payload actually is.

### 3.2 Positive-control acceptance (making L5 B.4 numerically checkable)

L5 B.4 requires the matcher to fire on genuine signatures and to produce no false positives on
10,000 random blocks. C1 fixes what "fires" means, before running:

- **v1.5 type 1:** matcher returns `True` **and** identifies the DigestInfo OID **and** the
  recovered digest equals the real SHA-256 of the signed message. All three, or control FAIL.
- **v1.5 type 2:** matcher returns `True` **and** the recovered message equals the plaintext.
- **PSS:** matcher returns `True` **and** the recovered salt length equals the salt length used.
- **False positives:** **0** hits on 10,000 uniform-random blocks per modulus size tested
  (2048 and 4096 bits), for each of the three matchers. Any non-zero count ⇒ instrument
  failure, and the E-01 verdict is "instrument failure", not "null".

### 3.3 What E-01 will report as not covered, decided in advance

Named now so it cannot be trimmed after seeing a null: RSA moduli 3301 never published
(including the moduli of the three 2014 onion RSA *message* blobs, which are ciphertexts, not
keys); the 432-bit 2013 modulus taken as a signing key for a 54-byte *window* of the payload
rather than the whole thing; blinded or partially-known signatures; OAEP; raw unpadded RSA;
and any payload transform outside the four enumerated integer encodings.

---

## 4. New thresholds — propagation

### 4.1 Which downstream results must be re-run, decided by a rule not by taste

**Rule, fixed here:** a downstream result must be re-run iff its input includes
`canon_256.bin` at any index whose byte C1 changes, **and** its own control records
sensitivity to a single-byte change at that granularity. A downstream result is *flagged but
not re-run* iff it is input-sensitive but its adjudicating instrument is one Round 19 Phase 0
is currently repairing — in which case it is handed to S2 rather than burned here, and that
hand-off is stated explicitly.

### 4.2 B-05 re-run

B-05's own `control_detail` records: *"Flipping ONE contested byte destroys recovery
(-7.38)"* — measured avalanche at exactly one-byte granularity. B-05 swept single-position
variation at the **6** contested indices only. If C1 changes any index outside those 6, B-05's
Part-1 negative covers a seed that is not the payload, and by §4.1 it must be re-run.

- **Instrument:** B-05's own `sweep.py` Part-1 grid, unmodified in structure, pointed at the
  resolved payload. Exhaustive: 6 representations × 15 generators × 224 = 20,160 beam decodes.
- **Positive control (mandatory, runs first):** B-05's `control.py` plant-and-recover on the
  **resolved** payload. **PASS iff** the planted correct key recovers at beam score ≥ −5.0,
  matching B-05's recorded −4.170 within the noise of a different seed. Below that, the re-run
  is reported as a null from an unvalidated instrument.
- **Bar:** B-05's own, inherited unchanged — HIT iff score ≥ −5.5 **and** score > null_max,
  with the null recomputed on this run rather than quoted.
- **Conditionals:** all three of B-05's, plus L7-A (English-only) and L7-B (one
  rejection-loop implementation) named in the result. No claim of new power.

### 4.3 Zero-false-positive re-runs

`characterize.py`, `hash_hunt.py` and zeroFP's E-02A / E-02B / H-03 are exact or
analytically-bounded tests, cheap, and their bars are inherited unchanged from their own
pre-registrations. They are re-run on **both** `canon_256.bin` and `payload_resolved.bin`, and
any difference in verdict is reported. No new threshold.

---

## 5. Deliverables

`PREREG.md` (this file), `singletons.py`, `e01_rsa.py`, `propagate.py`, `b05_rerun.py`,
`out_*.json`, `RESULTS.md` (no TBD sections), `ledger.json`.
Optionally the completed `round18/L5-payload/RESULTS.md`, marked as completed by Round 19 C1.

Trust anchor run before this lane: `python3 liber-primus/tests/validate.py` →
**ALL VALIDATIONS PASSED**; `python3 -m pytest liber-primus/benchmark/ -q` → **8 passed**.
Both are re-run at the end and recorded in `RESULTS.md`.

_No `git commit` from this lane (doctrine mechanic 7)._
