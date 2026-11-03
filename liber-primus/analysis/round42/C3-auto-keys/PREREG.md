# Round 42 / C3 — 43-B1 artifact keys re-derived from the PRESENT raw: PREREG

_Dated 2026-11-02, written before any decode output. No `git`. Panel-R36, the R41 instrument._

## Aiming Test
- **Q1 (target).** The R30-B1 "43 auto-extracted keys" cell. X1-B/R41 (finding B-2) showed C1's
  "raw absent" was a fresh-clone artefact; `analysis/armada_osint/artifacts/raw/{2012..2017}.md`
  are present. Re-derive the keys from them (`b1_keys.auto_alpha_from_raw()` + the curated set),
  confirm the two stored auto keys (MIDISCV, WORKING) reproduce, and give the cell a verdict under
  the current 12-register instrument (the original R30-B1 scored English-only).
- **Q2 (prior).** Low. These are published-artifact tokens used as repeating Vigenere / running
  keys; the whole published-text running-key class is doublet-excluded for LP2, and R30-B1
  already found no English hit. The value is coverage (closing a cell the matrix carried as
  blocked), not an expected break.
- **Q3 (instrument/power).** panel-R36 (12 registers) adjudication of every decode — strictly
  stronger than the original English-only pass, so a negative here dominates the original. The
  bar is the standing free-null bar of record `bars_v3(N=grid_per_page, L, 'free')`.
- **Q4 (three conditionals).** key space: CURATED_ALPHA + C->F variants + hex-letter NUMER +
  auto_alpha_from_raw() (ALL-CAPS and backtick tokens from the six raw .md), as repeating keys;
  transition model: Vigenere `c +/- key` and atbash, phase 0..11, both signs (the R30-B1 grid,
  NOT the keyskip beam); adjudicator register: panel-R36, panel-max over 12 registers.
- **Q5 (kill / success).** A page crosses iff its non-degenerate grid-max pmax >= its free bar.
  0 crossers -> NEGATIVE (measured, panel-R36). Degenerate decodes (constant/near-constant) are
  excluded from the max per the standing degeneracy flag. Success of the X1-B claim = MIDISCV and
  WORKING both re-derive from the present raw.

## Deliverable
`round42/C3-auto-keys/`: `run_c3.py`, `c3_results.json`, `RESULTS.md`, and a ledger row/patch
(the R40-C1-INCONCLUSIVE-R31/43-B1 lineage: this moves the 43-key cell from
blocked/inconclusive to measured-negative, or records the cross). Full-grid null is not run
(10^8 decodes); the standing bar of record is the threshold, stated as such.
