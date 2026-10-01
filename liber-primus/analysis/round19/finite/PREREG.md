# LANE 4 (finite) — PREREGISTRATION

_Round 19. Written before any score is computed. Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). PREREGISTER-ONLY phase — this document
answers the five Aiming-Test questions and defines the attack; the attack is NOT run here._

---

## 0. One sentence

Take the ONE finite object that is already extracted, already bounded, and carries a real
measured prior — the **74 RUNIC ornament-band reads** (8,095 rune-index glyphs, 71 bands of
length ≥ 8) from `round18/L3-ornaments/bands.json`, whose only negative so far is an
**English-register H1 string match** — and re-score them over the **nine-register adjudicator
built and power-measured in `round19/I2`**, closing the explicit reopen condition the repo
itself wrote for them.

---

## 1. The object and why THIS one

R5 ranks finite human-checkable objects first and names three: the ornament bands, the
contested payload bytes, and the 450 located O/A/AE disagreements. Two of the three are already
read to completion with no live reopen:

- **Contested payload bytes** — `round19/C1` corrected idx 45/50/246 → `payload_resolved.bin`
  at 100% calibrated accuracy; B-05 re-ran clean. Closed.
- **450 O/A/AE disagreements** — `round19/T1` read them at a control-measured 100.0000%
  (180/180) and found **450/450 agree with canon, 0 disagree**. Closed; no residual over the
  LP2 target typeface.

The ornament bands are read too (`round19/C3`, all 109 bands / 9,899 glyphs) — **but their one
content verdict is explicitly English-register-only**, and the ledger records a live,
evidence-named reopen for exactly that gap. That is the object this lane reads to the end: not
the pixels again (those are done) but the **already-extracted rune strings under a register the
original read could not see.** This is the DISCIPLINED "use the illustrations": a bounded re-read
of a finite data product, not an unbounded traversal.

---

## 2. The five Aiming-Test answers

### Q1 — Recognizer + proof the instrument can recognize the planted shape

**A hit** = at least one RUNIC band whose rune-index string scores `pmax` over the I2
nine-register panel above that register's matched-FP bar, where the winning register is a
*natural-language* register (EN / LATIN / OE / GERMAN / WELSH / EN_NOVOWEL), not the
numeric/positional channels — i.e. the band is **text in a language the English-only H1 read was
blind to**.

**Planted-shape proof (the recognizer the attack must pass FIRST, in-band):** the I2 panel
already carries a measured recognizer for this exact shape. `round19/I2/RESULTS.md` G-POWER:
handed held-out plaintext in each register, the panel scores LATIN `pmax` 25.5 vs matched-FP bar
4.67 at **power 1.00**, and `EN_NOVOWEL` 12.1→20.0 at power 0.92→1.00, in **27/27** cells. The
run will additionally **plant a known band-length (L=8..32) snippet of held-out Welsh / Latin /
OE / vowel-dropped-English into the band-reader's own output path and confirm the panel flags it
at the band lengths actually present** (median band ≈ hundreds of glyphs; 71 bands ≥ 8). If a
planted in-register snippet of a given band length is NOT recognized at that length, the negative
for that length/register cell is declared underpowered and reported as such, not as absence.

### Q2 — Measured fact raising the prior above flat (with path)

**NOT a completeness ritual — the prior is measured, twice.**

1. `LEDGER.json` entry 19 (`round19/C3` closeout of `round18/L3-ornaments`),
   `not_covered`: *"Any band content in a non-English register (H1 only)"*; `reopens_if` (ii):
   *"a multi-register (non-English) scorer finds language in a short band's read."* The repo
   wrote the reopen; this lane is it.
2. `round19/I2/RESULTS.md` G-POWER / L7-A: the English quadgram adjudicator — the only scorer
   ever applied to these bands — scores correct-key **LATIN at −5.44, power 0.33**, and
   vowel-dropped English at **power 0.00** (ranks below a wrong key). So the existing band
   negative is produced by an instrument *measured to be blind* to five of the registers LP2
   could plausibly use. A real, measured defect in the only instrument that has read the object
   is the strongest prior class this doctrine recognizes (instrument audit, R5 rank 3; combined
   here with a rank-1 finite object).

Flat prior would be "re-score random strings." This is not that: it is re-scoring a specific
extracted object with an instrument proven to have 3× its recall in the untested registers.

### Q3 — Boundedness + size

**ENUMERABLE and tiny.** 74 RUNIC bands (`bands.json`, `call=="RUNIC"`), 71 of length ≥ 8,
**8,095 rune-index glyphs total**; max band 342 glyphs. Plus, as a bounded extension, the 27
NON-RUNIC bands and the 256 base-60 tokens on pp.49–51 (`nonrunic.json`) re-examined for any
sub-string that reads as text. The entire object fits in one JSON file and is human-checkable
band by band. No key-space sweep, no PRNG, no offset ladder — the register panel runs over ~8k
glyphs in seconds. This is the opposite of the unbounded fog the doctrine was written against.

### Q4 — The three conditionals the negative will carry

1. **Key space swept:** NONE. This lane applies no decryption key; it scores the band reads
   *as plaintext in themselves* (ornaments-as-plaintext hypothesis). The conditional is instead
   **the band-extraction instrument**: the connected-component reader of `round18/L3-ornaments`,
   whose own power is 95.6% recall on the LP2 typeface but **coin-flip (sensitivity 0.50) on the
   RUNIC/NON-RUNIC call at ≤16 glyphs** (C3 gate G-A2). A negative is conditional on that
   reader's output being faithful at each band length.
2. **Decoder transition model:** identity (no enciphering) for the primary read; the bands are
   tested as direct plaintext. If a band is instead *key material*, a secondary pass feeds the
   band's rune indices as a key under the **round19/I1 drift-tolerant beam** (lam=12/max_free=2,
   the decoder that recovers the L7-B skip_by_two cells the old beam missed) against the LP2
   target pages — but that secondary pass is gated on the primary read producing a non-noise
   register signal first, and its negative carries the beam's construction-panel conditional.
3. **Adjudicator register:** the **I2 nine-register panel** (EN, LATIN, OE, GERMAN, WELSH,
   EN_NOVOWEL + 3 numeric/positional), measured power ≥ 0.90 in 27/27 cells, EN_NOVOWEL ≥ 0.92.
   The negative is NO LONGER English-only; it is conditional on these nine registers, and
   anything outside them (e.g. Hebrew, Greek, cipher-of-a-cipher) remains uncovered and is named.

### Q5 — Kill condition at 10% of budget

**Kill if the in-band planted-snippet recognizer FAILS at the band lengths present.** The first
step is to plant held-out in-register text of lengths L∈{8,16,32} into the band-reader output
path and confirm the I2 panel flags it above the matched-FP bar at those lengths. **If the panel
cannot recognize a planted hit at the lengths the real bands actually have** (because band reads
are too error-corrupted end-to-end — the reader is only 95.6% per-glyph, so a 32-glyph band
carries ~1.4 expected errors and recall of language may collapse), then this instrument cannot
recognize its own planted hit over this noisy object, the lane is generating a null (doctrine Q1
violation), and it STOPS — reporting the measured recognizer-failure length as the bound, not
claiming the bands are decorative. Checkpoint: after the recognizer plant, before scoring the 74
real bands.

---

## 3. Deliverables (when the attack is later run)

1. `RESULTS.md` with: the recognizer-plant power table (register × band-length), then the
   per-band `pmax` / winning-register / matched-FP-bar table for all 74 RUNIC bands (+ 27
   NON-RUNIC, + 256 base-60 tokens).
2. **R3 columns on EVERY band row** (CI-enforced): decrypt IoC·N, min distinct symbols over a
   32-rune window, best non-English LM score over the register panel, compressibility (h2 +
   gzip). A `SWEEPROW.md` / JSONL that `validate_ledger.py` accepts.
3. A `ledger.json` entry stating what was covered (9 registers over the extracted band object)
   and what was NOT (registers outside the panel; colour/chroma band channels, still unread;
   bands below the recognizer's power-floor length).
4. R7 bound, not verdict: the concrete condition that reopens (a tenth register; a higher-recall
   per-glyph band reader; chroma channel extraction).

---

## 4. AN-END holdout note

This lane applies **no keystream** and claims to decode **no unsolved page** — it reads a
finite already-extracted object as plaintext-in-itself. The AN-END blind-rediscovery holdout is
therefore **not triggered** by the primary read. It IS triggered only if the gated secondary
pass (Q4.2, bands-as-key under the I1 beam) ever claims a decode of an unsolved page; in that
event the method must first rediscover AN-END's φ(prime) totient keystream BLIND before any
unsolved-page claim is admitted. Recorded here so the gate is pre-committed, not retrofitted.

---

## 5. Honest label

**This lane is NOT a completeness ritual.** Q2 cites a measured fact with a file path (the only
instrument ever applied to this object is measured at power 0.33/0.00 in five of the registers
LP2 could use, `round19/I2/RESULTS.md`), and the object is R5 rank-1 (finite, human-checkable,
enumerable at 8,095 glyphs). The honest caveat is in Q5/Q4.1: end-to-end band-read noise may
drive the recognizer below usable power at real band lengths, in which case the lane converts to
a *measured power-floor bound* on the ornament-as-text hypothesis rather than a content hit —
which is still a result (it would be the first measurement of what the multi-register silence is
worth over this object), not a ritual.
