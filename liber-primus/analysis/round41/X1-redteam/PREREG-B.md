# Round 41 / X1 (part B) -- PREREG (red-team of C1; S-lane record; gate; Round 42 critic)

_Dated 2026-11-02, written BEFORE any re-run output of this part. Refute-by-default. Writes only
inside `round41/X1-redteam/` (scripts/data prefixed `x1b_`). C1's files, `LEDGER.json` and
`MEASURED-CEILING.md` are not edited by the audit itself; any patch text goes in
`ledger_patches_b.json` for the coordinator._

Part A (`PREREG.md`, `RESULTS-A.md`) covered I1 and B2. This part covers everything else the
campaign plan's X1 roster names: C1, the S lanes, the applied ledger patches, `check_ceiling.py`,
the gate, and the Round 42 critic.

## Targets and the test for each

**C1 (R14/R15 re-score; blocked-cell verification)**
- (a) Faithfulness: run `t_faith.py` unchanged; the archived campaign7 bests must reproduce
  exactly (R14 -6.897 with all five per-variant bests; R15 -6.873 with all 24 per-matrix bests).
- (b) The table: recompute every decision p in RESULTS.md §1 independently from the persisted
  draws (`null_draws.jsonl`) and the unit maxima in `result_R14.json` / `result_R15.json` — own
  code, not `lib.py`. Decision p = max over the three block sizes; cross requires Z-family and
  raw both below alpha 0.0025.
- (c) Controls: recount 120/120 and 144/144 recognised from the stored `plants` blocks, and the
  null maxima the recognition threshold was judged against (W 4.62 / P 5.50; W 3.92 / P 4.80).
- (d) R44 kill: `r44_first6.json` recoveries must all be < 0.90 and match the 0.743–0.815 band;
  the addendum must predate the run artefacts it governs.
- (e) The five blocked-cell claims: spot-verify each in-repo ABSENT/PRESENT claim by listing the
  named paths (R31 code present + T1-RESULTS.json; R35 `round12/C2/` fetch.sh only; R36 P1/P2
  dirs absent; R44 5 books present / 6 absent; 43-B1 raw md absent, scream substitute present).
- (f) Ledger: the seven filed rows equal `C1-r14-r15/ledger.json` field-for-field; the
  `inconclusive` rows claim no negative; `ledger_patches.json` applied; `positive_control`
  is `passed` only where plants actually ran.

**S1/S2/S3** — never run (no `round41/S*` directory exists). The audit records that as fact with
the deadline consequences; there is nothing to refute. Test: directory listing; the sandbox
snapshot id and dates as stated in the campaign plan vs PICKUP-HERE.

**Gate and patches**
- Re-run `check_ceiling.py` and `validate_ledger.py` (both modes; `--strict` is expected to fail
  on absent gitignored stores by design — record counts).
- Confirm part A's `ledger_patches_a.json` / `ledger_b2_corrected.json` text is actually live in
  `LEDGER.json` and `MEASURED-CEILING.md` (token-presence check per patch).

**Round 42 critic** — one section: what Round 41 left most exposed, ranked by
coverage x power against doctrine R1, for the Round 42 plan to aim at.

## Verdict vocabulary
As part A: FOUND-ERROR (size; whether a stored verdict flips) / NO-ERROR-FOUND (what was
checked) / NOT-RERUN (anything > 20 min; stated, not claimed).
