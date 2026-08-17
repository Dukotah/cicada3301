# PREREG — Round 10, lane RECON-A (document-mining register)

**Registered before any file was opened beyond the four mandatory docs.**

## What this lane is
Not an attack. A **register** of leads that appear in this repo's own markdown as
*listed but never executed*, *executed only partially*, *closed with an explicitly narrow
scope*, or *declared closed on thin evidence*. Deliverable = a machine-readable list with
`file:line`, why it is still open, and a falsifiable closing test.

## Hypothesis
H0 (null): every lead-shaped statement in the repo's markdown has either been executed, or
is foreclosed by a mechanism kill already recorded in `ELIMINATION-LEDGER.md` /
`research/DEAD_ENDS.md`. Under H0 the register would be empty or near-empty.

H1: the corpus contains a non-trivial number of un-executed / partially-executed leads,
because the program's own docs repeatedly use the language of unfinished work
("documented but not run", "left open", "honest scope", "the tool is built to extend",
"remains uninterpreted", "decisive next experiment", "cost-prohibitive").

## Method (fixed in advance)
1. Enumerate every `*.md` under `liber-primus/` and `research/` (94 + 13 files).
2. Two grep passes over fixed phrase sets (unfinished-work language; hedge language).
   Phrase sets written before running: *residual unrun levers, not executed, never
   executed, cost-prohibitive, documented but not run, low-prior, honest scope, this does
   not cover, only conceivable revival, built to extend, remains uninterpreted, future
   work, needs a Linux env, decisive next experiment, left open, still open, nobody has
   read, genuinely untested, untested residue, out of scope, bounded to, only tested.*
3. Full read of every doc the lane brief names (OPEN-AVENUES, completeness-critic,
   FOLLOWUP-TESTS, ARMADA-RUN-QUEUE, COVERAGE-MATRIX, CAMPAIGN-*, AUDITOR-LOOP-*, recon/,
   attribution/, anend_hunt/, stego/, pp49_51/) plus FRESH-ANGLES / ROUND-8 / ROUND-9.
4. **Filesystem verification** of each candidate: a lead is only recorded as un-run if the
   artifact that would exist if it had been run is absent (no output JSON/log, no script,
   no verdict section). This is the null control for this lane — it prevents recording a
   lead that was silently executed and reported elsewhere.
5. Each candidate is checked against the kill lists in `ELIMINATION-LEDGER.md` "Do NOT
   re-run" and `research/DEAD_ENDS.md`. Anything foreclosed **by mechanism** is dropped,
   even if it is still phrased as open somewhere in the docs.

## Pass/fail thresholds (fixed in advance)
- **Lane succeeds** if ≥15 leads survive step 4 + step 5 with a stated `file:line` and a
  falsifiable closing test.
- **Lane returns a null** (i.e. "the program really is exhausted at the document level")
  if <5 survive. 5–14 = partial.
- **A lead is rejected** if any of: (a) a mechanism kill in DEAD_ENDS/LEDGER covers it;
  (b) an output artifact exists on disk showing it was run; (c) its closing test is not
  falsifiable (no pre-statable numeric or binary outcome).

## Explicit non-claims
This lane runs no cryptanalysis and produces no evidence about LP2's cipher. A lead being
listed here is **not** a claim that it will work — most are low-prior by the repo's own
assessment. The claim is only: *this specific test was named and not run, and here is how
to close it.*
