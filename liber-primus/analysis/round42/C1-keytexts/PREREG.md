# Round 42 / C1 — R35 keytexts (cells H7xF4, H8xF4) under panel-R36: PREREG

_Dated 2026-11-02, written before decode output. panel-R36, the R41 instrument. No `git`._

## Aiming Test
- **Q1 (target).** Matrix cells H7xF4 ("the key is all around you") and H8xF4 ("right in front of
  your eyes"), currently **T-LEG R30,R35** — tried only under the legacy English/single-register
  instrument. X1-B/R41 showed `round12/C2/texts/` is present (C1's "absent" was clone-scoped).
  Re-run the 33 keytexts as running keys over the unsolved pages under panel-R36 (12 registers).
- **Q2 (prior).** Low: published-text running keys are doublet-excluded for LP2 as an additive
  class; R30/R35 already found no English hit. Value = upgrading T-LEG -> T (current instrument).
- **Q3 (instrument/power).** panel-R36 panel-max over 12 registers (incl. LATIN/OE/GREEK/HEBREW,
  which matter for Latin/Greek/Hebrew source texts), strictly stronger than the legacy pass. Bar:
  standing free-null bar of record `bars_v3(N=grid, L, 'free')`.
- **Q4 (three conditionals).** key space: the 33 R35 keytexts as running keys (offset-swept),
  both signs, both atbash; transition model: running-key Vigenere c +/- key, non-repeating,
  start offset swept; adjudicator register: panel-R36, panel-max over 12.
- **Q5 (kill / success / data-integrity gate).** A page crosses iff its non-degenerate grid-max
  >= its free bar. 0 crossers -> NEGATIVE (measured, panel-R36). **Data-integrity pre-check
  (declared before the run):** each text file is classified real-text vs fetch-error HTML; only
  real texts are swept, corrupt captures are listed and excluded (so the negative is not
  manufactured by feeding garbage). Offsets are stride-sampled (~150 start positions per text) to
  bound cost; the sampling is logged (no silent cap).

## Deliverable
`round42/C1-keytexts/`: `run_c1.py`, `c1_results.json`, `RESULTS.md`, ledger row + patch moving
H7xF4/H8xF4 from T-LEG to TRIED (panel-R36), and recording the corrupt-capture finding.
