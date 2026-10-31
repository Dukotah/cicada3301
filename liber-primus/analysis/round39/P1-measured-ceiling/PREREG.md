# Round 39 / P1 — MEASURED-CEILING.md: pre-registration (admissibility rule)

_Dated 2026-10-31, written before `MEASURED-CEILING.md` or `check_ceiling.py` existed. Plan of record:
[`../CAMPAIGN-PLAN.md`](../CAMPAIGN-PLAN.md) §3 P1. Doctrine: [`../../../ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md) R2, R7._

## Q1 — the recognizer (what makes a claim admissible)

A claim in `MEASURED-CEILING.md` is a line of a table in §1–§3 of that file. It is **admissible** iff all hold, and
`check_ceiling.py` enforces each mechanically (exit 1 on any violation):

1. **Citation convention.** Every claim line carries one or more `[[ROW-ID]]` tokens. Every cited id must be an `id` of an
   entry in `liber-primus/LEDGER.json` (256 rows at drafting).
2. **Strong verdicts need a controlled, covered row.** A line whose verdict cell contains `excluded at power` or
   `measured negative` may cite only rows whose `positive_control` begins with `pass` (case-insensitive; the ledger holds
   `passed`, `PASS`, `passed at L=...` forms) and whose `coverage` is non-null and non-empty. Weak verdicts
   (`partial`, `unmeasured`, `inconclusive`, `not excluded`) need only existing ids.
3. **Three conditionals + exit.** Every exclusion-table line carries a non-empty `key space / transition model / register`
   cell and a non-empty `re-opens if` cell, and a measured-power cell.
4. **Numbers are pinned.** Every load-bearing number in the doc is listed in a `pin:` comment as `ROW-ID | substring`;
   the substring must occur in that row's JSON. A drifted number fails.
5. **Vocabulary (doctrine R7).** The words `exhausted`, `exhaustion`, `closed`, `solved`, `dead`, `impossible` may not
   appear except inside double quotes, backticks, or `>` blockquote lines (quoted history). `unsolved` is not matched.
6. **Reach.** Each §2 line's cited rows must include at least one row naming the family (the author's responsibility;
   X1 spot-checks 10 claims against the row's measured power).

## Q2 — prior
`round36/AUDIT-inhibitors.md`: foreclosure labels were the repo's historical failure mode. ARMADA-DOCTRINE §0: the
discoveries came from auditing closures, not from new sweeps. No document yet states the whole instrument generation's
exclusions in one place.

## Q3 — bounded
Reads `LEDGER.json` (256 rows), the round32–38 SYNTHESIS files and RESULTS cited there. No decodes, no sweeps.

## Q4 — conditionals of this lane's own output
(1) key space: the 256 ledger rows as they stand on 2026-10-31; (2) transition model: not applicable (audit);
(3) register: not applicable. The page states *measured* power; where a row's power is assumed rather than measured
the page says "assumed". It cannot be stronger than the rows.

## Q5 — kill
If a claim cannot be tied to a qualifying row it is demoted to `unmeasured`/`inconclusive` in the page, never dropped.
Admissibility used `pc` prefix `pass`, not strict equality; recorded here so X1 can overrule it.
