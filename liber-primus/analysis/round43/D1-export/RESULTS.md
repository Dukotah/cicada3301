# Round 43 / D1 — export of the R42-S1 full result lists: LAPSE (source destroyed)

2026-11-03. **Nothing exported.** The Vercel project `skyfling` (prj_Gs5dIz30aiS3MO7OuAZGipJo4lnA)
was deleted at 2026-11-03T21:47:01Z (team activity log: "You deleted project skyfling"), ~24 min
before this lane ran, destroying all three preservation copies from R42-S1: snapshots
`snap_ff0SWU76EW32OqbWJvp00fnORypR` and `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6`, and the persistent
sandbox `r42-s1-recovery`. Every MCP and CLI path 404s on the missing project; the snapshot cannot
be restored into another project (project-scoped). Full attempt log and recommendation:
`analysis/round42/S1-s2-recovery/state_recovered/LAPSE-RECOMMENDATION.md`.

**Decision: accept the lapse.** The R42-S1 verdict is unaffected — it rests on the local,
sha-verified `STATUS.json` (`1aa529444548e3e1f3add420936ddfd40ee9b9fe4cb6d25b74c197a2e070c2ba`),
`HIT-CANDIDATE.json` (`b05fd0ba..`, hits:[]) and `candidates_summary.json`. Permanently lost:
`candidates.jsonl` (sandbox sha `bd5c8289..`), `top_S2.json` (`f60eece8..`), `hist_S2.u64`
(`60c1744a..`) — recoverable only by re-running the sweep. Lesson: project-scoped
sandboxes/snapshots are not durable storage; pull load-bearing artifacts into the repo before a
lane closes.

## R42-S1 story, one line
2026-11-03 (R43-D1): full-list export attempted → project `skyfling` had been deleted 24 min
earlier, snapshots + sandbox gone; exported nothing; lapse accepted — verdict stands on local
STATUS/HIT-CANDIDATE/summary shas (`1aa52944..`, `b05fd0ba..`); lost-file fingerprints recorded
(`bd5c8289..`, `f60eece8..`, `60c1744a..`).
