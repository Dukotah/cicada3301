# Round 42 / S1 — S2 window-2 recovery + list export: PREREG

_Dated 2026-11-02, written BEFORE any sandbox call of this round. Plan of record:
`../CAMPAIGN-PLAN.md` §3-S1. Harness: exactly Round 38 S1 (`round38/S1-s2-windows/RESULTS.md`),
whose window-2 end state this lane recovers. Deadline: the three snapshots expire ~2026-11-06/07._

## Aiming Test
- **Q1 (target).** Recover the Round 38 window-2 end state from snapshot
  `snap_ff0SWU76EW32OqbWJvp00fnORypR` (created at the session-2 cap, unix 1793403622; the window's
  `--seconds 2250` ended ≈1793403180, so STATUS.json should be final). Export to the laptop:
  `run_r36/STATUS.json`, `HIT-CANDIDATE.json` (if present), the candidate/hist/top lists — full
  files if the channel allows chunked transfer, else the Round 38 degradation (sha256 + aggregated
  histogram + candidates ≥ 5.0). Then, quota permitting, ≥ 1 persistent-session window resuming
  from the recovered cursors.
- **Q2 (prior).** S2 is the derived-keystream engine lane; prior unchanged from Rounds 36/38
  (enumerable 2^32 space, 47.9 % + unverified-window-2 done under mixed instruments; panel-R36
  fraction small). The recovery itself is bookkeeping with certainty ~1 — the value is not a hit,
  it is that ~2,250 s of already-spent compute stops being unverified.
- **Q3 (instrument/power).** No new instrument. Window-2 rows were produced by the same engine
  whose launch self-test ran 64/64 exact at window start (verified in R38 RESULTS); the claim bar
  (7.6342) and near-miss bar (7.5342) are UNCHANGED from Round 38 for comparability, and every
  recovered count is also read against the Round 41 bar of record at the recovered N
  (`bars_v3(family="survivor12")`) — both reported.
- **Q4 (three conditionals).** key space: bash-$RANDOM-style 2^32 seed cursor region swept in
  window 2 only; transition model: the engine's exact keyskip relation; adjudicator register:
  panel-R36 (12 registers) for the R36-gated fraction, Round 19 panel for the legacy fraction —
  the mixed-instrument split is carried, not blended.
- **Q5 (kill / success).** Success = STATUS.json read with cursors > window-1's 2,059,308,008 and
  internally consistent (seeds_advanced = after − before; candidate counts monotone vs window 1).
  Kill on inconsistency: file the state as CORRUPT, keep window-1 cursors as the resume point,
  and do NOT merge window-2 counts into coverage. If the snapshot is already evicted/expired,
  record UNRECOVERED and close the Round 38 row's "unverified" clause as permanently lost.

## Protocol (Round 39/40/41 text, verbatim discipline)
Persistent sessions; ONE blocking call in flight; state downloaded after every window; nothing is
counted that is not on the laptop. The export is the deliverable, windows are the bonus. S3 (bash
3.2.57 build check) rides the first session after the export completes.

## Deliverables
`round42/S1-s2-recovery/`: `state_recovered/` (STATUS.json + lists or their R38-style summaries,
with sha256), `RESULTS.md`, `ledger.json` (+ patch to the R38 S1 row closing its "window 2 not
recovered" caveat either way), window logs if any windows run.
