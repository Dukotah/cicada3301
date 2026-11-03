# Round 42 / C2 — R36 dated pads (cell H7xF9) under panel-R36: PREREG

_Dated 2026-11-02, before decode output. panel-R36. No `git`._

## Aiming Test
- **Q1 (target).** Cell H7xF9 ("the key is all around you" x temporal / dated-pad), whose data
  round41-C1 reported absent (clone-scoped, X1-B B-2). The R17 P1 (Bitcoin block hash / merkle /
  nonce / time streams) and P2 (NIST beacon outputValue+seedValue, random.org pre-generated) pad
  bytes are present (523 MB). Re-apply them as additive mod-29 pads over the unsolved pages under
  panel-R36 (12 registers); R17 ran them under the legacy instrument.
- **Q2 (prior).** Very low: a full-entropy public pad added to the runes is exactly the
  doublet-excluded additive-keystream class; R17 was negative. Value = coverage under the current
  instrument + closing the "data absent" mislabel.
- **Q3 (instrument/power).** panel-R36 panel-max over 12 registers; bar = standing free-null bar
  of record `bars_v3(N=grid, L, 'free')`.
- **Q4 (three conditionals).** key space: the dated-pad byte streams (P1 hash/merkle/nonce/time +
  2013 variants; P2 beacon output/seed + random.org aggregates) as additive mod-29 pads,
  offset-swept; transition model: pad add/subtract `c +/- pad`, atbash; adjudicator: panel-R36.
- **Q5 (kill/success).** A page crosses iff non-degenerate grid-max >= its free bar. 0 -> NEGATIVE
  (measured, panel-R36). Each pad is read to a bounded prefix and offsets stride-sampled (~150 per
  pad); the cap is logged (no silent truncation). Byte%29 bias (256 = 8*29+24) is noted in
  not_covered.

## Deliverable
`round42/C2-dated-pads/`: `run_c2.py`, `c2_results.json`, `RESULTS.md`, ledger row (negative) +
patch moving the H7xF9 dated-pad verification from inconclusive/absent to measured.
