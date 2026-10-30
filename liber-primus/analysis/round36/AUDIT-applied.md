# AUDIT-applied: R36 inhibitor audit, safe fixes (2026-10-30)

Source: `AUDIT-inhibitors.md` (same folder). No git, no heavy Python, no edits to `.py`/`.c` under
`analysis/round19`, `round33/I1`, `round34`, `round35`, `round36` or `benchmark/`. Superseded text is struck through or prefixed
"SUPERSEDED (R36 audit, 2026-10-30)"; reasoning is kept. Live ledger count after the Round 11 backfill: **209** (was 202).

## Files edited
- `PAPER.md`: S1 "genuinely exhausted / branch exhausted" replaced by the bound statement (pair only, English plants, panel unrebuildable); counts 172 -> 209 (lines ~282, 443).
- `liber-primus/analysis/round27/S1-CLOSEOUT.md`: sec. 5 verdict gets the bound statement; "EXHAUSTED" and "finished" struck.
- `liber-primus/PICKUP-HERE.md`: S1 "Closed; needs nobody" and "EXHAUSTED" struck; "NOTHING IS RUNNING" and "R28-L3 never written up" marked superseded; counts (181, 162 -> 209); new "Reopen under the repaired instrument" section; Rounds 28-30 blocks placed under a "Historical" heading; foreclosure section retitled. (Root `PICKUP-HERE.md` carries no S1-exhausted text; not edited.)
- `liber-primus/ELIMINATION-LEDGER.md`: "Do NOT re-run" retitled "Measured bounds and their reopen conditions" with per-item reopen conditions; "PRNG keystreams" and "another keytext" absolutes struck; "Do NOT re-run any Round-11 lens" -> reopen note.
- `liber-primus/LEDGER.json`: +7 rows `R11-N1..N5-NUMBER-CHANNEL`, `R11-S1-`, `R11-S2-` (status `measured`, English-only conditional, `not_covered`, evidence verified present, no `positive_control` field, noted); `counts.total` 209, `by_status.measured` 67.
- `liber-primus/handoff/FOR-FUTURE-SOLVERS.md`: sec. 5 retitled "Bounded: do not re-run as-is" with a Conditionals column; line 7 "Frozen at Round 25"; line 242 bar caveat; line 400 `len(d['entries'])`.
- `liber-primus/analysis/round20/CAMPAIGN-PLAN.md`, `round21/CAMPAIGN-PLAN.md`: sec. 4 keytext bullet marked SUPERSEDED (R12-D1 + R26-B).
- `research/DEAD_ENDS.md`: H3 banner (skip-encipherment is the core decoder's model).
- `README.md`: "30 rounds / 172 rows" -> 36 / 209.
- `liber-primus/handoff/SOLVER-STRATEGY-2026.md`: 142 -> 209 entries, 25 -> 36 rounds.
- `liber-primus/analysis/handoff/check_consistency.py`: new pure-text check "ledger counts in nav docs match LEDGER.json" (skips lines marked historical).
- `AGENTS.md`: lines 8-9 and sec. 8 rewritten to the Round 36 state (old list kept, marked superseded).
- `liber-primus/analysis/handoff/build_problem.py` -> regenerated `liber-primus/PROBLEM.json`, `INDEX.json`, `KNOWLEDGE.json`, `SOLVED-PAGES.json`: KDF no longer "running", PHP no longer "~3 %", ornaments no longer "never read"; every `eliminated_families` item says "bounded" with a ledger id.
- `liber-primus/analysis/handoff/validate_ledger.py`: WARN (not error) for round>=19 negatives without `three_conditionals` and for negatives with null `coverage` (8 warnings today).
- `liber-primus/data/fetch_sources.py` + new `liber-primus/data/r36_corpora.json`: `--r36` (42 sha-pinned files, refuses on mismatch; the one Laxdoela page 404 in the original log is not in the table); `--welsh` now verifies the pinned sha 624ffc97... / 761,030 B with a clear failure message.
- `.github/workflows/ci.yml`: `PICKUP-HERE.md` added to `pull_request` paths.
- `liber-primus/HUMAN-ORACLE.md` (new) and `liber-primus/ARMADA-DOCTRINE.md` (one-line item 9 in sec. 4 linking it; the doctrine had no explicit hit-protocol line).

## Audit items
Applied: 1, 2, 3, 4, 5, 6 (incl. the count check), 7, 8, 9, 12, 14, 15, plus HUMAN-ORACLE.
Deferred: **10** (`beam_v3`/`adjudicate`/`validate_ledger.check_r3_store` panel width) , **11** (`hitfn20`/`panelmax20` parameters), **13** (`verify_solution.py` L7 caveat and PROBLEM.json wording) - edits under the excluded dirs or touching the oracle while sweeps B1/B2 run; do after they finish. Also deferred (not on the apply list): a committed panel fixture and the round19/20 instrument tests in CI; `LEDGER-SUMMARY`; AN-END ledger row; `FINAL-SYNTHESIS.md:115` and `NEXT-ARMADA-ROADMAP.md:9` banners; `PARKED-SWEEPS.md:70`.

## Needs the owner
HUMAN-ORACLE.md names the owner as adjudicator and the issue tracker as the channel - confirm. Persona/branch policy, PRs #7-#10, `._round31_stale_backup/`, `round29/L4-image-forensics/fingerprints.json` (see the audit "Owner decides"). The CLAUDE.md persona block was already replaced by another lane today; CLAUDE.md links `HUMAN-ORACLE.md`, which now exists.
