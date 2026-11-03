# Round 42 / C3 — 43-B1 artifact keys, re-derived from the present raw: RESULTS

2026-11-02. `PREREG.md` first. panel-R36, standing free-null bar of record.

## Result: NEGATIVE (measured, 12 registers)

X1-B/R41 (finding B-2) showed C1 had reported the OSINT raw ABSENT from a fresh clone; it is
present (`analysis/armada_osint/artifacts/raw/{2012..2017}.md`). This lane ran the cell C1 could
not:

- **Keys re-derived from the present raw.** `b1_keys.build()` yields 168 ALPHA (curated + C->F
  variants + hex-letter NUMER) + 16 NUMER streams; **43** of the ALPHA keys are
  `auto_alpha_from_raw()` tokens (ALL-CAPS + backtick) scraped from the six raw .md — exactly the
  "43 auto keys" the ledger named. **MIDISCV and WORKING both reproduce** (the two auto keys
  `b1_results.json` had stored), confirming the raw is the right artefact.
- **Honest-instrument re-score.** 485,760 decodes (184 keys x 2 signs x 2 atbash x 12 phases x 55
  unsolved pages), each as a Vigenere / running key, every decode adjudicated under panel-R36
  (panel-max over 12 registers) — strictly stronger than the original R30-B1 English-only pass.
- **Verdict.** Global best **pmax 5.496** (`SHAMIRSSECRETSHARINGSCHEME`, page 24, L=270, sign+1
  atb0 ph9, register LP1_REAL) vs its free-null bar of record **17.09** at N=8,832. **0 pages
  cross.** Every per-page grid-max sits far below bar. No survivor, no near-miss.

The cell is therefore **not blocked** (as the round-41 verification implied) and **not a hit**:
it is a measured negative at full 12-register power. This dominates the original English-only
negative (best -6.3 on the English scorer); the panel-max over 11 non-English registers never
lifts any decode near the bar.

## Scope / not covered
Repeating-key Vigenere + atbash, phase 0..11, both signs only (the R30-B1 grid; not the keyskip
beam, not interrupter arms). Keys are the catalogued artefact tokens; non-tokenised prose and
numeric schedules beyond the 16 NUMER streams are out of scope. The free bar is the standing
measured null, not a fresh per-shuffle null (the full-grid null would be ~10^8 decodes); it is
the R41 bar of record, stated as the threshold.

## Ledger
Patches `R41-C1-B1-43-AUTO-KEYS-VERIFIED` (inconclusive -> the measured result lives in the new
row) and adds `R42-C3-B1-43-AUTO-KEYS-RUN` (negative). `ledger_patches.json` + `apply_ledger.py`.

## Files
`PREREG.md`, `RESULTS.md`, `run_c3.py`, `c3_results.json`, `ledger_patches.json`, `apply_ledger.py`.
