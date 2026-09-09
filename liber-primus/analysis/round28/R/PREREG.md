# R — red-team: audit this project's current claims (doctrine R6, standing lane)

_Round 28, pre-registered 2026-09-08. Mode: run-now-light. Added lane (2 of 2): the owner
slate carried no red-team lane; doctrine R6 makes one mandatory. Reports **FOUND-ERROR /
NO-ERROR-FOUND** per target — never "confirmed"._

## Targets (chosen because each is load-bearing and freshly touched)

**T1 — `R12-A1`'s ledger hygiene (candidate doctrine-R7 defect).** The row's
`not_covered` is `null` while its own artifacts show 8–11 sampled offsets on pads of up to
118.8 MB and a keyskip1-only decoder — i.e. real uncovered mass with no `not_covered`
statement. Also: `handoff/PARKED.md` P-3 still says "The A1 re-run was NOT performed"
while `results_560_13.json`/`results_560_00_full.json` (2026-08-19) show it was. Deliver:
a corrected `not_covered` proposal for the row + a dated staleness patch for PARKED.md
(patch text only; the coordinator applies and commits).

**T2 — S1-CLOSEOUT recomputation.** From raw artifacts (`../../round27/P1-engine/run/`
copies are READ-ONLY — never write there; read via paths listed in S1-CLOSEOUT.md):
re-sum the pmax histogram to exactly 2³²; re-verify the 392,131-flag count and the 1.31×
Gumbel ratio; re-run the three crosser adjudications' recorded numbers against
`ORACLE-{35563892,348625413,86514964}.md`; spot-re-score ≥100 of the K4 batch rows in
Python and confirm |C−Python| = 0.0. Any mismatch = FOUND-ERROR, stop-and-alert.

**T3 — L3's subsumption claim, tested empirically.** Take ≥100 dictionary strings, compute
the i386 Py2.7 hash word w, and verify `keystream(seed_string, wordsize=32)` ≡
`keystream(init_by_array([w]))` for random29 via `gen_py27` — bit-exact over ≥2,000 draws
each. Also verify the abs/negative-hash edge case (strings whose hash is negative) is
handled the way CPython 2.7 actually handles it, not the way it is assumed to. If ANY
string's keystream is not reachable from the integer space, L3's "i386 image subsumed by
S1/S2" claim is FOUND-ERROR and L3 must sweep the i386 image explicitly.

**T4 — PREREG-vs-code drift across L1–L5 (the R26-D lesson).** After each lane's runner
exists and before its null is accepted: diff the code's actual grid/cells/bars against its
PREREG promises (R26-D caught exactly this class of defect in Lane A). Any silent re-run of
a covered cell, any bar edited after results, any control run after nulls = FOUND-ERROR.

**T5 — This round's own S2-non-interference promise.** Sample `grind27 --status` throughput
before and during L1/L3 runs; if Round-28 load measurably degrades S2 (>10% throughput
drop), FOUND-ERROR against the round's own operating constraint, lanes pause.

## Aiming Test

**Q1 — Hit shape + recognizer.** A "hit" here is a demonstrated discrepancy: a number that
does not recompute, a claim contradicted by its own artifact, a code path that diverges
from its PREREG. Each target above states its concrete recognizer. **Positive control:**
before trusting T2's recomputation tooling, deliberately corrupt one histogram bin in a
COPY of the data and confirm the checker flags it; before trusting T4's differ, plant one
known PREREG/code mismatch in a scratch copy and confirm detection.

**Q2 — Prior fact.** Every genuinely new finding in this repo came from auditing a closure,
instrument, artifact or input (doctrine §0 table) — measured project history, the strongest
prior on the board. Fresh, large, load-bearing claims (S1's first-ever full-space null;
the R12-A1 absorption) have never been independently recomputed.

**Q3 — Bounded?** Yes: 5 enumerated targets, each hours at most, all single-thread reads +
small recomputations.

**Q4 — Three conditionals of a NO-ERROR-FOUND:** (1) only the 5 named targets were audited;
(2) recomputation used the committed artifacts, not a re-run of the sweeps; (3) T2's
spot-parity samples ≥100 rows, not the full 10,971 — stated as a sample.

**Q5 — Kill at 10%.** If T2's artifacts are unreadable without touching
`P1-engine/run/` live files, T2 defers to post-S2 rather than risk the sweep — recorded,
not skipped silently.

## AMENDMENT 2026-09-08 (T5 window substitution, recorded at execution)

T5 as written names "during L1/L3 runs". At this lane's start L1 was already complete
(RESULTS.md 12:17) and L3's runner was not executing; the live round-28 load was L2's
keysweep + L5 + this lane's own compute. T5's windows therefore measure S2 throughput
against THAT concurrent load (strictly analogous target; bar unchanged at >10%), via
interval deltas of `run/STATUS.json` (read-only) rather than `--status` invocation —
grind27 exposes no separate --status subcommand; STATUS.json is its status channel.

## Coverage promise (honest)

Per-target verdict FOUND-ERROR / NO-ERROR-FOUND with the recomputed numbers; proposed
patches delivered as text for the coordinator. No target is reported "confirmed".
