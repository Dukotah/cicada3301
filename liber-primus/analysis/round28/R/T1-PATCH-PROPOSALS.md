# R28-R T1 — patch proposals (text only; coordinator applies and commits)

_2026-09-08. Target: `LEDGER.json` row `R12-A1` + `handoff/PARKED.md` P-3._

## 1. R12-A1 `not_covered` — FOUND-ERROR (doctrine R7 hygiene defect), proposed value

The row carries `"not_covered": null` while its own artifacts show real uncovered mass
(verified this lane from `analysis/round12/A1/results_560_13.json` — 160 configs over
exactly 8 offsets {0, 1e3, 5e3, 2e4, 1e5, 1e6, 1e7, 5e7} on a 118,818,811-byte pad —
and `results_560_00_full.json` — 220 configs over 11 offsets to 3.5e6). Proposed
replacement for the `not_covered` field (JSON string value):

> "(a) Offset density: only 8-11 sampled offsets per pad (560.13: 8 offsets of
> 118,818,811 byte positions, a 6.7e-8 fraction; authoritative _560.00: 11 offsets to
> 3.5e6). R28-L1 later densified to strides 16,384/331,777 on the two authoritative
> pads; >99.99% of single-byte offsets remain unswept on every pad, and the 4 smaller
> pads were never densified. (b) Relation: every R12-A1 decode used the keyskip1-class
> beam (max_skip 3); the keyskip2/'pair' relation (R18-L7-B: beam recovers skip_by_two
> at only 25.8%) was unrepresented until R28-L1 swept it on the 2 authoritative pads —
> the 4 smaller pads remain keyskip1-only. (c) Adjudication: fixed -5.5 bar, pre-hitfn20
> — no N-scaled family-wise bar, no 3-clause gate (doctrine mechanic 4). (d) PRF / seed /
> salt uses of the pads (B-04/B-05 axis, already named in reopens_if). (e) Registers
> outside the era's quadgram scoring (L7-A conditional)."

## 2. PARKED.md P-3 staleness — VERIFIED ALREADY CORRECTED, no further patch needed

The stale line ("The A1 re-run was NOT performed") was already corrected in place by
R28-L1's dated CORRECTION OF RECORD (2026-09-08) before this lane ran. This lane
independently verified the correction against the on-disk artifacts:
`results_560_13.json` = 160 configs / 8 offsets / NEGATIVE / dated 2026-08-19;
`results_560_00_full.json` = 220 configs / 11 offsets / NEGATIVE. The correction's
figures are exact. Deliverable closed as OVERTAKEN-AND-VERIFIED.

## 3. Same defect class elsewhere (systemic note for the coordinator)

`B-05` also carries `"not_covered": null` with status negative (its `reopens_if` carries
part of the load but is not a coverage statement). A one-time hygiene pass filling
`not_covered` for all negative rows where it is null would close the R7 gap class;
count and row list in `RESULTS.md` §T1.
