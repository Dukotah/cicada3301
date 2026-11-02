# Round 41 / X1 (part B) -- RESULTS: C1 audit, S-lane record, gate, Round 42 critic

_2026-11-02. `PREREG-B.md` written first. Part A (`RESULTS-A.md`) covered I1 and B2. Re-run here:
C1 faithfulness (`t_faith.py`, unchanged), full p recount from the persisted draws (`x1b_c1.py`,
own arithmetic, 112 checks), control recounts, the R44 kill values, ledger equality for the seven
filed rows and every patch of parts A and B, `check_ceiling.py`, `validate_ledger.py`. NOT-RERUN:
exceed_Z recounts (the per-unit null matrices `null_*_b*.npz` are not in the canonical tree --
see B-5), the null generation itself, the B2/I1 sweeps (part A's scope)._

## 0. Verdict table

| # | Target | Verdict | What was found |
|---|---|---|---|
| B-1 | C1 raw-p recount | **FOUND-ERROR (minor, no verdict change)** | 11 of 12 (family x block x level) exceed counts reproduce exactly from `null_draws.jsonl`. At R14 b1000/P, **21 of 1,000 draws tie the observed best page exactly** (a block-1000 shuffle can leave whole pages intact, so the observed decode recurs in the null); the stored float32 matrix rounded the ties below the float64 observed value, so stored exceed 833 = strict `>` while the ties-in count is 854 (p 0.854 vs 0.833). The level's decision p is 0.893 (from b250) under either convention. Instrument note: at P level the b1000 blockperm is weak -- b100/b250 carry the constraint |
| B-2 | C1 blocked-cell verification | **FOUND-ERROR (systemic, 4 claims; no status flips)** | The lane ran in a **fresh clone**, where gitignored corpora do not exist, and reported artefacts ABSENT that are PRESENT in the canonical tree with mtimes months older than the lane: R35 keytexts (all 33, `round12/C2/texts/`, 2026-08-17); R36 dated pads (P1_blockchain/data 147 MB + P2_beacons 376 MB, 2026-08-19); 43-B1 OSINT raw (`armada_osint/artifacts/raw/{2012..2017}.md`, all six, 2026-07-27); R44 expand books (6 of 7 in `bookcipher/books/`, `krisyotam_runes.txt` tracked at `data/`). Statuses stay inconclusive/partially-run (nothing was scored), but the cells are **runnable on the canonical machine**, three of them with zero network. Patched: corrected notes on the four R41-C1 rows, the two R40-C1-INCONCLUSIVE coverage lines, and C1's one unapplied patch (R30-B1, superseded with corrected text) -- `ledger_patches_b.json`, applied |
| B-3 | C1 RESULTS SS1 parenthetical | **FOUND-ERROR (wording)** | "(W null max 4.62, P 5.50)" / "(3.92, 4.80)" quote the **b1000-only** maxima; the all-blocks maxima are 5.23/5.81 and 4.25/5.65, and recognition used the all-blocks values per every plant record (`null_best_max_allblocks`). The 120/120 and 144/144 recognitions stand (min plant pmax 28.0 vs null max 5.81) |
| B-4 | C1 faithfulness, decisions, controls, kill | **NO-ERROR-FOUND** | `t_faith.py` reproduces the archived campaign7 bests exactly (R14 -6.897, R15 -6.873, all per-variant/per-matrix bests); decision p = max over blocks and the cross logic verified; 120/120 + 144/144 recognised with control_cells sums consistent; R44 kill re-checked from `r44_first6.json` (0.743-0.815, all < 0.90) and the addendum predates the run artefacts |
| B-5 | C1 persistence | **POLICY NOTE** | The per-unit null matrices (`null_*_b*.npz`, RESULTS SS4) never reached the canonical tree -- only the draw maxima did -- so exceed_Z is not recountable here (regeneration ~hours). The raw path was fully recountable, which is what doctrine R3 is for. For future lanes that run in a side clone: the SWEEPROW/row stores named in RESULTS must be synced back or the RESULTS must say they were not |
| B-6 | S1 / S2 / S3 | **NOT RUN (recorded)** | No `round41/S*` directory exists; wave A' never launched. Consequences: the S2 window-2 recovery from `snap_ff0SWU76EW32OqbWJvp00fnORypR` (open since 2026-11-01 00:00 UTC) and the list export must happen **before the snapshot expires ~2026-11-06** or the R36/after-window-1 lists are lost; the bash 3.2 binary check (S3, ~10 min) and the PHP retry (S2) roll to Round 42 unchanged |
| B-7 | Parts A+B patches vs the live docs | **NO-ERROR-FOUND (after apply)** | Every patch of `ledger_patches_a.json`, `ledger_b2_corrected.json` (entry + 5 patches + page edits, applied by the coordinator pre-audit), C1's `ledger_patches.json` (status/coverage/replaces/status_note all live; its R30-B1 add superseded per B-2) and `ledger_patches_b.json` (8 fields, applied 2026-11-02) verified token-by-token in `LEDGER.json` / `MEASURED-CEILING.md` |
| B-8 | Gate | **PASS (after B-9 repair)** | `check_ceiling.py`: 125 rows cited, 110 pins, PASS. `validate_ledger.py`: 299 entries, ERRORS 0, unsound negatives 0 (non-strict; `--strict` fails on absent gitignored stores by design). `tests/validate.py` green; full non-network pytest 110 passed, 5 skipped (gitignored stores absent) after the two test repairs below |
| B-9 | The documented pre-commit gate itself | **FOUND-ERROR (the full gate was red; no stored verdict involved)** | `pytest -q -m "not network"` -- the command CLAUDE.md orders before every commit -- had TWO failing tests that CI never sees (CI runs a named subset): (1) `round19/I3/test_i3.py::test_backcompat_default_signature` red **since Round 32**, which gave `benchmark/null.py` an L-scaling path while `nullcurve19`'s legacy cell keeps its published ignore-L contract; the test asserted bit-equality over L cells written when both ignored L. Repaired by pinning the real backcompat surface (default signature, the one the LEDGER numbers used) and asserting the L-path divergence explicitly. (2) `tests/test_validate_ledger_r3.py::test_scoping_declared_vs_historical` asserted absent-store = hard error, superseded by the 2026-11-02 checkout-scoped semantics (absent = WARN default / ERROR --strict); the test now pins both modes. Nobody ran the full documented gate between Round 32 and this audit -- the armada relied on the CI subset |

## 1. The systemic finding (B-2), stated once

Every wrong ABSENT claim has the same mechanism: **an ignore-respecting search in a tree where
ignored paths were never populated**. A fresh clone is the degenerate case -- the gitignored
corpora are not invisible there, they are genuinely missing. The claims were true of the clone
and false of the project. Two rules follow, proposed for the doctrine's artefact-search practice:

1. An artefact-absence claim must name the tree it was tested in; "absent from the repo" may
   only be claimed from the canonical working tree (or after regenerating per `.gitignore`'s
   own regeneration notes).
2. In-repo artefact searches must enumerate with ignore-blind tools (`find`/`ls`), never with
   default `rg`/`grep -r` semantics, and must check `.gitignore` itself for the campaign block
   that names what regenerates a missing path.

## 2. Round 42 critic -- where Round 41 leaves the project most exposed

Ranked by (coverage the move would add) x (measured power it would run at), per doctrine R1.

1. **The S2 sandbox window is a wasting asset with a date on it.** Everything else in this list
   survives a week of delay; the snapshot does not (~2026-11-06). It is also the only lane with
   an already-measured instrument (panel-R36 gate, 64/64 engine self-test) waiting on nothing
   but a session. Run S1 first, S3 in the same session (~10 min), S2 after.
2. **Four unblocked cells with artefacts in hand (B-2).** R35 keytexts (33 texts, panel-class
   scoring, no network), R36 dated pads (523 MB local), 43-B1 auto keys (re-derive from the true
   raw, then the existing beam harness), R31 readouts (needs the sub-32-rune recognizer first --
   see 4). These are exactly doctrine R5's "finite objects": enumerable, cheap, honest coverage.
3. **The B2 remainder, prioritised by X1-A SS3.4:** offsets 3-28 at sign -1 and 1-28 at sign +1
   need the screen widened past two skips first (a lane, not a re-run); ILP32 at every offset.
   Without the screen work the cells are power-limited negatives before they start.
4. **The WATCH band decision (X1-A #12).** The bar of record (9.4-10.5) is honest for flagging
   but silently drops the 8.0-9.4 rows the old null12 gate would have decoded at L=240. A row
   above the largest stored survivor (7.10) costing one L=240 decode + a human look is cheap
   insurance against the one failure mode the bar cannot see: a partially-decoded true key
   outside the transition model. Adopt it before the next mass sweep, not after.
5. **The b1000/P null weakness (B-1)** is a one-line fix in the next direct-family lane's
   PREREG: at page level, block sizes >= the page length do not constrain the null; use b100/
   b250 (or page-matched blocks) for P-level decisions.

## 3. Files

`PREREG-B.md`, `RESULTS-B.md`, `x1b_c1.py`, `x1b_c1.out`, `x1b_c1_out.json`,
`ledger_patches_b.json`, `x1b_apply.py`; test repairs in `analysis/round19/I3/test_i3.py` and
`tests/test_validate_ledger_r3.py` (B-9).
