# Lane C (closeout & prior propagation) — PREREG

_Round 20, Phase C. Written before any edit. Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

Lane C runs **no search** and **scores no decode**. It is documentary propagation + nav
maintenance + two human-facing flags. The Aiming Test is answered in that light — a propagation
lane's "hit" is a nav-doc/ledger state that is *true and consistent with its sources*, and its
"null" is silent drift (a correction that lives only in one lane's folder).

## The five Aiming-Test answers

- **Q1 (what would a hit look like; would this instrument recognise it?)** A hit = every
  source-of-record document (`round18/L1-toolchain/RESULTS.md`, `ELIMINATION-LEDGER.md`,
  `LEDGER.json`, `README.md`, `analysis/README.md`) agrees with the Round-19 measurements it
  should carry, with old figures marked *superseded* not deleted (per `CLAUDE.md`), and
  `PICKUP-HERE.md` opens Round 21. The recogniser is: `validate_ledger.py` Unsound-negatives = 0,
  `tests/validate.py` PASS, and a grep showing the corrected numbers reach their source rows.
- **Q2 (measured fact raising the prior above flat)** The corrections are not new claims; they are
  already-measured Round-19 results whose *only* defect is that they live in lanes with no write
  scope over the source docs. F6/F7: `round19/C3/RESULTS.md` §6.5 (PGP table re-derived 228/228
  identical to R18, with C2 tamper→BADSIG + C3 foreign-key controls both PASS). Distro bracket:
  `round19/R1/RESULTS.md` §C + C3 §6.5b (two independent lanes). Crypt::RSA: C3 §6.6 (two dated
  PASSing signed messages).
- **Q3 (bounded?)** Fully enumerable and finite: 5 target documents, 3 corrections, 2 new ledger
  entries, 2 human flags. No sampling.
- **Q4 (three conditionals of the negative)** N/A in the search sense — Lane C asserts no negative.
  The propagated corrections carry the conditionals of *their source lanes* (C3/R1), which are
  cited inline so a reader can trace them.
- **Q5 (kill condition at ≤10% budget)** If any edit would *change a verdict* rather than correct a
  count/bracket/source, STOP and escalate to the coordinator instead of editing unilaterally. (This
  fired by design on C-canon: the 3-byte payload promotion is *flagged*, not decided.)

## Positive control

Not a measurement lane, so no planted signal. The control that licenses the propagation is
inherited and stated: C3's PGP re-derivation reproduced R18's table **228/228 file-for-file
identical including every sha256**, with tamper→BADSIG (C2) and foreign-key→no-GOODSIG (C3) both
passing. That is the control proving the F6/F7 correction is real and not an artifact of a
mis-run verifier. Recorded in `LEDGER.json:G-02` and `L1-F6-CORRECTION`.

## Pass/fail threshold (fixed in advance)

PASS iff, after the lane: (1) `tests/validate.py` still PASSES; (2) `validate_ledger.py`
Unsound-negatives = 0 and JSON parses; (3) the F6 count (46→56/54), the F7 bracket-loosening, and
the G2→Crypt::RSA re-sourcing each appear in `round18/L1-toolchain/RESULTS.md` with the old text
marked superseded; (4) `ELIMINATION-LEDGER.md` + `analysis/README.md` carry Round 19 + Round 20
rows; (5) `PICKUP-HERE.md` exists and lists the open items; (6) C-canon is recorded as
*decision-pending*, not decided; (7) C-eyeball flag (T1 p27:93) is recorded. FAIL if any of these
is missing or if `validate.py` regresses.

## No git commit (mechanic 7)

Lane C writes files only. The coordinator commits.
