# Round 19 — LANE 3 (RED-TEAM on this repo's own claims) — PREREG

_Pre-registration only. The attack is NOT run in this phase. Written under ARMADA-DOCTRINE.md
(R6: report FOUND-ERROR or NO-ERROR-FOUND, never "confirmed")._

## Target claim (the repo's current strongest, chosen for R6)

The combined **construction-class closure** that underwrites the standing `VERDICT-OTP-CLASS`:

1. `analysis/recon/i9_deficit/construction_class.py` pins LP2 0-54's forward fingerprint as
   **"memoryless base + a soft anti-repeat rewrite"** (doublet deficit 0.18x, flat non-zero
   difference-diagonals, uniform off-diagonal inflation).
2. `analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md` §0 pins the enciphering **combiner**
   as the **value-REWRITE (soft anti-repeat, key stays synced)** mechanism and asserts the
   ~200-text keytext nulls (and the number-theoretic keystream nulls, `RUN-numeric.log`,
   874 streams) **cover** that combiner, because a correct keystream under it would have
   scored ~-4.5, not the -5.9..-6.9 the sweeps produced.

The load-bearing inference being red-teamed: *"no generative keystream family fits LP2 0-54
under the pinned combiner."* The AN-END page (file 73.jpg / LP2 p56) is the ONE book-terminal
page with a **known generative keystream** — the running totient phi(prime)=(p-1) mod 29,
shift-down, with F-interrupters (`docs/SOLVED-PAGES-AND-INTERRUPTERS.md` line 33). If
crib-dragging AN-END's KNOWN plaintext back through the **pinned** combiner recovers a keystream
that is *anything other than* that known phi(prime) totient — in particular a generative family
whose generator naturally extends to the 0-54 index range — that is a FOUND-ERROR: the closure
would have mis-represented a live generative lane as covered.

Two attached sub-audits that the doctrine's Lane-3 text names explicitly:
- **(a) holdout spec audit**: is the AN-END holdout correctly specified (right page, right
  target hash, right method)? Preliminary finding already surfaced in recon (see Q1/Q2): the
  phi(prime) AN-END solve is in the *prose* doc but **NOT in the machine trust-anchor**
  (`SOLVED-PAGES.json` / `tests/validate.py` validate only 01/03/05/06/14 — LP1 + p05). So the
  instrument the whole repo trusts has **never** reproduced the phi(prime) keystream. This is a
  specification/instrument gap to adjudicate, not yet a FOUND-ERROR.
- (c) input re-measure is deferred unless (a)/(b) point at a drifted file; the AN-END
  ciphertext source to be used is `data/sources/relikd_p56_an_end.txt` (475 bytes, holds the
  three rune blocks + the literal 128-hex hash, verified readable this phase).

---

## The Five Aiming-Test Questions

### Q1 — What would a hit (a FOUND-ERROR) look like, and would THIS instrument recognise it?

**Recognizer.** A FOUND-ERROR is: crib-dragging AN-END's known plaintext through the pinned
soft-anti-repeat combiner yields a per-index keystream `k_i` that (i) is NOT equal to the
documented phi(prime) totient `(p_i - 1) mod 29` on the interrupter-free positions, AND/OR
(ii) matches a *different* generative recurrence (e.g. prime-value, prime-index pi(p),
Fibonacci mod 29, an affine/LCG step, first-difference of a value stream) whose generator is
defined for arbitrary index and therefore **extends to indices 0-54**. The strongest form of
the hit: the recovered keystream equals phi(prime) on AN-END but the *same combiner* admits a
second, equally-consistent generator — i.e. the closure's "only phi(prime) fits terminal
pages" is under-determined.

**Proof the instrument can recognise the planted shape (to be executed in the run phase, pre-registered here):**
- Positive control 1 (phi(prime) recovery): take AN-END ciphertext indices from
  `data/sources/relikd_p56_an_end.txt`, encipher the known plaintext forward with the
  documented phi(prime) keystream + the documented interrupter set, confirm it reproduces the
  held ciphertext; then crib-drag backward and confirm the recovered `k_i` == `(p_i-1) mod 29`
  on non-interrupter positions. If the backward crib-drag does NOT recover phi(prime), the
  instrument is broken and the lane reports that (an instrument defect, still a Lane-3 result).
- Positive control 2 (generator discrimination): plant a DIFFERENT known generator
  (Fibonacci mod 29) as the AN-END keystream on synthetic ciphertext, crib-drag, confirm the
  recovered stream is identified as Fibonacci and NOT mis-labelled phi(prime). This proves the
  recognizer can tell two generative families apart — the exact discrimination the hit needs.

Both controls use rune INDICES (not transliteration), the beam/interrupter-aware decoder in
`src/lp/solve.py` (never a rigid decoder on LP2), and `benchmark/null.py: threshold_for(...)`
for any score bar. Recovery of a planted keystream is a deterministic equality check, so power
on this axis is 1.0 by construction once the control passes.

### Q2 — What measured fact raises this family's prior above the flat rate? (file path)

**Measured fact (real, this phase):** `SOLVED-PAGES.json` validates exactly five pages
(labels `Runes-01.jpg atbash+shift0`, `05.jpg shift0`, `06.jpg atbash+shift3`,
`03.jpg vigenere(DIVINITY)`, `14.jpg vigenere(FIRFUMFERENFE)`) — enumerated live this phase.
**AN-END's phi(prime) keystream is absent from the trust anchor**, while
`docs/SOLVED-PAGES-AND-INTERRUPTERS.md` line 33 and the holdout spec both assert it as a
KNOWN solved method. So there is a concrete, file-located **instrument/spec mismatch**: the
repo claims a known generative keystream it has never machine-reproduced. That is the
evidence-derived prior — a closure/instrument defect of exactly the kind every genuine finding
in this repo (D3, R17 public-pad, L7-A/B) came from auditing — not lore. Prior is above flat
because the mismatch is already observed, not hypothesised.

(Note: this prior supports the audit's EXISTENCE. Whether the eventual keystream-family finding
is positive is what the run phase decides; the lane is NOT a completeness ritual — Q2 is a
measured file-located fact, not "none".)

### Q3 — Is the space bounded, and by what size?

**Bounded and small — finite human-checkable + enumerable (R5 tier 1-2).**
- The AN-END keystream to recover is a **single finite sequence** of length = AN-END's
  non-interrupter rune count (~60-90 runes from a 475-byte page). One human-checkable object.
- The generator-family comparison set is **enumerable and tiny**: phi(prime), prime-value,
  prime-index pi(p), Fibonacci mod 29, Lucas mod 29, first-difference of each, running-sum of
  each, +/- sign, +/- atbash. Order ~ 10 generators x 2 signs x 2 atbash x {value,diff,sum}
  = ~120 closed-form streams, each a deterministic equality check against the recovered
  sequence. Minutes of compute, zero sweep.
- The holdout-rediscovery (BLIND phi recovery from ciphertext + its stated external input,
  per the AN-END HOLDOUT clause) is a single deterministic derivation, not a search.

No unbounded component. This is the highest-prior tier the doctrine ranks.

### Q4 — The three conditionals the negative (NO-ERROR-FOUND) will carry

1. **Key space swept:** the ~120-member enumerable closed-form generator family above, plus
   the single crib-recovered keystream — NOT "all keystreams". A NO-ERROR verdict means *no
   generator in this enumerated family (beyond the documented phi(prime)) fits the recovered
   AN-END keystream*; it does not exclude a generator outside the family.
2. **Decoder transition model:** the **pinned soft anti-repeat value-REWRITE combiner**
   (`campaign18_skip/armada2/COVERAGE-MATRIX.md` §0; `round12/D1_redteam/rewrite_gate.py` ARM 2)
   with interrupter-aware beam (`src/lp/solve.py`). Per L7-B the beam represents ONE
   rejection-loop form; the negative is conditional on the rewrite form and does NOT cover
   skip_by_two or a rigid combiner. If the crib-drag is run ONLY under rewrite, that is named.
3. **Adjudicator register:** AN-END plaintext is **English** (known), so the crib-recovery leg
   is register-independent (equality check). Any secondary LM scoring of a *projected* 0-54
   keystream decode is scored over the L7-A register panel (English, Latin, Old English, Welsh,
   German, abbreviated/vowel-dropped English), not English-only.

### Q5 — Single observation that abandons this lane at 10% of budget

**Kill condition:** if Positive-Control-1 shows the backward crib-drag through the pinned
combiner recovers the documented phi(prime) totient **exactly and uniquely** (the ~120-member
family yields no second consistent generator, and the recovered stream has no index-extensible
structure beyond phi), THEN there is no generative-family leak and the lane collapses to the
spec-gap sub-audit (a) only. Checkpoint: after both positive controls + the single crib-drag
(the first ~10% of budget). At that point either (i) a second generator fits -> escalate to the
0-54 extension test (FOUND-ERROR track), or (ii) only phi fits -> stop the keystream-family
attack and report NO-ERROR-FOUND on (b), while still delivering the (a) spec-gap finding and
the BLIND-rediscovery holdout outcome.

---

## R3 columns to persist (CI-enforced) for any sweep row

Every row in the run phase persists, alongside the English score: **decrypt IoC*N**,
**min distinct symbols over a 32-rune window**, **best non-English LM score over the L7-A
register panel**, and a **compressibility figure**. (The crib-recovery controls are equality
checks, not scored sweeps, but the ~120-generator comparison and any 0-54 projection ARE rows
and carry all R3 columns.) Instrument validated by `tests/validate.py` before any row counts.

## Deliverables of the run phase (for the record)
- FOUND-ERROR or NO-ERROR-FOUND on (b) the crib-constrained combiner closure.
- Adjudication of (a): is the AN-END holdout correctly specified, and should the phi(prime)
  keystream be added to the `SOLVED-PAGES.json` trust anchor?
- The AN-END HOLDOUT outcome: BLIND rediscovery of the phi(prime) keystream from
  `data/sources/relikd_p56_an_end.txt` + the stated external input (the prime sequence),
  NOT handed the key.
- Write files only; the coordinator commits.
