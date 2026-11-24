# R45-X1 red-team — PREREG

_Written 2026-11-23 before any X1 output. Doctrine R6 (report FOUND-ERROR / NO-ERROR-FOUND, never "confirmed") and R7 (bounds)._

## Aiming test
1. **Target:** the claims of R45 lanes W1, I1, S1, T1 (T1 only if it has a RESULTS.md with closing stamp), plus the Fable52-vs-T1 T7 characterisation and Fable52's hard-coded external path.
2. **Why this has prior:** R6 — every past instrument defect was found by cross-audit. Round 45's thesis (spaces are not words) is new and its supporting statistics are all < 3 h old.
3. **Instrument:** re-reading each lane's PREREG/outputs/scripts; mtime ordering for PREREG-before-data; cheap re-runs (< 10 min each) of the key statistic of each lane from the canonical dataset.
4. **Positive control for the audit:** each re-run must reproduce the lane's own number on the lane's own inputs before I use it to test an alternative (if I cannot reproduce, that is itself a finding).
5. **Conditional / what would change verdict:** an error is anything that changes a headline number, a power figure, a control's pass/fail, or the set of ledger rows a claim attaches to.

## Checks planned
- W1: solved reference set (739 words) membership and comparability; GP transliteration of English corpora; z-size scaling; control pass; look-elsewhere; LP2 segmentation artifacts (hyphen/line wrap/separators) — recompute adjacent-length MI on LP2 with alternative segmentations.
- I1: whether the harness strips spaces before the instruments in a way the real LP2 path would not; reopen-list rows truly word-indexed; R41 enc_words copy fidelity (diff/hash).
- S1: PREREG/blind-read/adjudication ordering; control relabel honesty; line-402 alignment defect from `analysis/stones/alignment.json`.
- T1: closing stamp present? if yes, audit nulls and Stage-B.
- Cross: Fable52 "distributed" vs T1 "5 gap pairs carry 0.29/0.38".
- Fable52 external path inventory.

Outputs: AUDIT.md, scripts, ledger_rows.json (ids R45-X1-*, status `audit`).
