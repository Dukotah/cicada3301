# Round 36 / X1 -- red-team (R6) -- RESULTS

_2026-10-30. Refute-by-default. Each target is FOUND-ERROR or NO-ERROR-FOUND with citations; a NO-ERROR-FOUND states what was checked. No git run. Paths relative to `liber-primus/`. One Python process at a time, nproc=1, free RAM >= 0.5 GB throughout. Re-runs in this directory: `rerun_i1_gate.py/.json`, `rerun_nine.py/.json`, `rerun_hebrew_seed.py/.txt`, `rerun_o3_verifB.py/.json`, `rerun_b2_stream.py/.json`, `rerun_verify_rk11/12/13.json/.out`; ledger application `apply_ledger.py` (pre-edit copy `LEDGER.pre-x1.json`), nav edits `apply_nav.py`. **B1 (`B1-orbit-12reg`) was still sweeping (`run.out`: 118,000 of 138,121 units) and had no `RESULTS.md`: B1: not yet available.**_

## 0. FOUND-ERROR summary

| # | Target | Sub-verdict | One line |
|---|---|---|---|
| 1a | I1 mappings: "fully deterministic" (`mappings.md:3`, RESULTS "Reproducibility") | **FOUND-ERROR** | `mappings_r36.py:88,98,102`: per-cluster mark `set()` iterated for vowel letters. `rerun_hebrew_seed.txt`: PYTHONHASHSEED 1/2/3 on the 7 WLC files -> `dcb7863f`, `664a2013`, `b9f21645` (three different streams). I1's own `models/panel12.npz` (ea8ef0fd) is not run-to-run reproducible. (P1 found it; I1's docs were never corrected.) |
| 1b | I1 mapping documentation completeness | NO-ERROR-FOUND (one gap) | Greek / Norse / Hebrew rules in `mappings.md` match `mappings_r36.py`; the only undocumented choice was the order of two vowel marks in one cluster (the nondeterminism above). Only other `set`/`dict` uses are membership tests (`DAGESH in m`, `SIN in m`) -- order-free |
| 1c | I1 gate cells GREEK/NORSE, L=120, panel-R36 | NO-ERROR-FOUND | re-run: lane reps 0-7 reproduce z-vectors (atol 1e-3) and 8/8 clear bar 4.3937; fresh reps 100-107: 8/8 each (min pmax 19.16 GREEK, 15.33 NORSE; own register argmax 8/8) |
| 1d | Existing nine registers' power | NO-ERROR-FOUND | re-run EN_NOVOWEL 22/24 (= lane, min pmax 3.07), EN_HALFVOWEL 24/24, CY 24/24; all 24 cells of `gate_proof_r36.json` within 0.02 of Round 32 |
| 2a | P1 build-twice "genuinely different hash seeds" | NO-ERROR-FOUND (evidence weak) | the seeds are protocol prose only (`compare_builds.py:4`; `build_twice.json` records no env). X1 ran a THIRD build, `PYTHONHASHSEED=7`, into scratch: `panel12.npz` a0682f0c.., `testhalves12.npz` cdd55adac.. byte-identical to build1 |
| 2b | Hebrew mark-set sort the only nondeterminism? | NO-ERROR-FOUND | grep of `mappings_r36.py` and `build_models_r36.py` for `set(`/`dict`/`hash(`: only that site; `build_r36.py:36-38` patches both `for x in m` and `for x in pm`, asserts `sorted(` count 2; seeds 1, 2, 7 identical |
| 2c | `inputs_r36.json` 53 hashes | NO-ERROR-FOUND / **FOUND-ERROR (minor)** | 53/53 sha256 equal disk. But 5 Norse paths (Egils, Fostbraedra, Gisla, Hrafnkels, Volsunga) do not resolve as written: on-disk names hold U+FFFD (`os.listdir`); matched by basename |
| 2d | `GATE-CHANGE.md` states the re-gate as NEW | NO-ERROR-FOUND | sec. 5 line 55, verbatim "a NEW measurement, not a continuation" |
| 3a | S1 window arithmetic | NO-ERROR-FOUND | sum of per-worker `seeds_done` 1,895,728,884 -> 1,950,696,430; diff 54,967,546 = sum of cursor diffs; 0.441384 -> 0.454182 (+1.2798 pp); 2^32 - after = 2,344,270,866 = 42.65 windows; 26,175 seeds/s (lane 26,174.5) |
| 3b | live `round27/P1-engine/run/` untouched | NO-ERROR-FOUND | `cmp` STATUS.json, top_S2.json, HIT-CANDIDATE.json against `state_before/` identical; mtimes 2026-10-28 |
| 3c | after-state resumable; 0 crossers vs histogram | NO-ERROR-FOUND | all 6 cursors in band and `cursor - band_start == seeds_done`; `grind27.c:906-922` tolerates absent `hist_`/`top_` files; best per-worker 7.1256 < 7.5342; candidates sum 6,280; per-worker bests (<=6.80 except w0) consistent with histogram >=7.0 count 1, >=6.5 count 4. Blob uploaded without the npz hash check: disclosed by the lane (RESULTS), engine blob hash e46d4bb7.. was checked |
| 3d | S1 "coverage 44.138 -> 45.418 %" | **FOUND-ERROR (wording)** | the 44.138 % was scored under the Round 19 panel and never re-scored (28/64 V1 pmax move -0.66..+1.34, P1 RESULTS); only the 1.28 pp window carries panel-R36 pmax. Proposed patch sets `coverage_fraction` 0.454 as if one instrument. Ledger records it as mixed (panel-R36 coverage = 1.28 %). Also: `top_S2.json` (1024 old entries) could be re-scored under panel-R36 cheaply -- not done |
| 4a | B2 store: header, append mode | NO-ERROR-FOUND | header `SWEEPROW/1`, 263,907 lines = header + 263,906 rows; `sweep.py:186-202` opens "w" only when the store is absent/empty, "a" on resume, refuses non-empty-without-state (rc 3). Rows per cell 66,088/66,036/65,904/65,878 = 2 x per-rel decodes (33,044/33,018/32,952/32,939) |
| 4b | B2 control split, tier arithmetic, best vs bars | NO-ERROR-FOUND | 35+45 = 80, 37+43 = 80 (EN_MODERN, EN_NOVOWEL); keyskip split 17+23+19+21 = 80 / 78 prefilter on keyskip2; tier (a) 487 + 9,280 = 9,767 = 20.33 %, 38,269 = 79.67 %; tier (b) 199 x 2^17 = 26,083,328 = 0.6073 % of 2^32; survivors 23,207 / 26,083,328 = 8.9e-4; best 6.608 (php_scale ks1) < 7.941 |
| 4c | B2 ledger patches | **FOUND-ERROR** | (i) patch id `R32-B2-PHP-MTRAND` does not exist (real: `R32-B2-PHP-MT-RAND`); (ii) "tier b 0.607 % replaces R34's 0.061 %" is presented as new coverage, but R36 `sweep.py:259-263`, R32-B2 `sweep.py:186-190` and R34-B1 `sweep.py:215-217` all draw `default_rng(3301).integers(0,2^32,size=2^17)` in order (`rerun_b2_stream.json`): R36 = first 199 blocks of R32-B2's 318 (0.9705 %) and a superset of R34's 20. No new seeds; what is new is screen power on those 199 blocks (pf_v4 0.94-0.99 vs R32 pf_v2 0.47-0.74), v3 on survivors and 263,906 persisted rows. Patches applied to the real ids with this wording |
| 5a | O3 PREREG misstatement (noise pmax vs L) | NO-ERROR-FOUND | the disclosed error is real; corrected argument holds (excess over size-matched null 4.85 -> 3.58 -> 1.08; plants rise 13.8-27.5 -> 36.3-70.8; raw pmax falls 7.07 -> 5.75); caveat that L=262/729 nulls are post-selection is stated, and the selection-free test (held-out windows) carries the verdict |
| 5b | O3 Verifier B re-run, 2 windows | NO-ERROR-FOUND | L=729 decode: window 0 7.0681 LP1_REAL, window 1 2.4157 EN_KJV; chained 7.0681 / 2.5463 EN_NOVOWEL -- equal to `verifiers.json` to 15 digits (`rerun_o3_verifB.json`) |
| 5c | `free`-relation caveat on the ledger row | NO-ERROR-FOUND -> strengthened | it was only in `not_covered`; appended to `result` of `R36-O3-NEARMISS-1354603465`. Minor: O3's 12-register panel is I1's `models/panel12.npz` (ea8ef0fd), not panel-R36 (immaterial: pmax12 = pmax9 to 1e-7) |
| 6a | O4 counts | NO-ERROR-FOUND | 68+24+29+3+16 = 140; 374 = 34 x 11; 154 clue entries (36 + 1 + 7 + 94 + 1 + 15), 132 mapped |
| 6b | O4 "no overlooked text" vs `pgp/messages/` | NO-ERROR-FOUND (undocumented gap) | directory has 58 files; `clues.json` provenance covers 37 (all exist). The other 21 are `ky_*` copies; all bodies except one (leading-space variant of the 2014 onion-welcome text) match a clue's text, and that one is the onion-welcome body. Not a coverage hole, but the 58-vs-37 gap is not stated in O4 |
| 6c | O4 spot cells, 3 NEVER | **FOUND-ERROR** (2 of 3) | H12 x F2 and H7 x F2 NEVER: the P.S. digit string and `@1231507051321` were run as numeric additive keystreams in R10b B1 (`b1_keys.py:138`, row R30, rigid/legacy) and skip-aware with an offset sweep in campaign18 `numeric2_skip.py:170-205`; the P.S. digits were also R26-C seeds (LEDGER.json R26-C coverage). They sit under F4 in O4's scheme, so NEVER (68) is overstated by >= 2. H1 x F1 NEVER: no counter-evidence found |
| 6d | O4 spot cells, 3 TRIED | NO-ERROR-FOUND | H2 x F10 (R01/R03/R07): `round10/L2-map/PREREG.md:59-62, 84-86, 115-117` exist and say what is claimed (R07 is analytic, IoC.N = 1.0000); H4 x F8 (R26) `R22-B-TURTLE-SPATIAL-RENDER` row exists; L4 x F2 (R16-R20) rows `R11-N1..N5-NUMBER-CHANNEL` exist and are English-only as marked |
| 7 | `verify_solution.py` (audit item 1) | NO-ERROR-FOUND | see section 7 |
| 8 | AUDIT-applied | NO-ERROR-FOUND | see section 8 |
| 9 | Ledger / gate | applied | LEDGER.json 209 -> 219 entries; validator 0 errors; section 9 |
| 10 | B1 | not yet available | coordinator audits |
| 11 | Round-37 critic | 6 candidates | section 11 |

## 1. I1 mappings (target 1)

**Deterministic?** No, for Hebrew. `mappings_r36.hebrew_to_ascii` keeps each cluster's marks as `set()` (line 88 `cl.append([ch, set()])`) and builds vowel text with `for x in m if x in _HV` (line 98) and `for x in pm if x in _HV` (line 102). Iteration order of a one-character-string set depends on `PYTHONHASHSEED`. X1 re-ran the unpatched function over all seven WLC files: seeds 1, 2, 3 give three different SHA-256 prefixes (`rerun_hebrew_seed.txt`). P1 measured 15 of 384,147 clusters affected and a null effect on the gate; `mappings.md:3` ("fully deterministic") and I1 RESULTS "Reproducibility" are still wrong. Greek and Norse functions contain no set/dict-order dependence (grep: `set(` only at line 88). Lane docs are not edited by X1 (nav docs + ledger only); correction is in the ledger row `R36-I1-NEW-REGISTERS.x1_r36` and here.

**Documented choices complete?** The rules listed in `mappings.md` (Greek eta->E, omega->O, upsilon->Y/U, gamma-nasal N, rough breathing H; Hebrew pointed, sheva dropped, vav+holam O / vav+dagesh U, matres lectionis dropped, final silent he dropped, shin/sin; Norse thorn/eth TH, ae/oe, j kept) match the code. Missing: the vowel-mark order for double-pointed clusters (code-point order since P1's patch).

**Gate re-run (`rerun_i1_gate.py`, panel = `P1-panel-r36/build1/panel12.npz`, sha a0682f0c.., bar 4.3937):**

| cell (L=120) | lane reps 0-7: z reproduced / hits | fresh reps 100-107 hits | fresh min pmax | own register argmax (fresh) |
|---|---|---|---|---|
| GREEK | 8/8 reproduced, 8/8 | 8/8 | 19.16 | 8/8 |
| NORSE | 8/8 reproduced, 8/8 | 8/8 | 15.33 | 8/8 |

Existing nine (`rerun_nine.py`, 24 reps, panel-R36): EN_NOVOWEL 22/24 (min pmax 3.07, the same thin cell as Round 32), EN_HALFVOWEL 24/24, CY 24/24. Power from `gate_proof_r36.json` vs Round 32 recorded: no cell differs by > 0.02.

## 2. P1 (target 2)

* Third independent build with `PYTHONHASHSEED=7` into the scratchpad (`python -B build_r36.py <dir>`, 30 s): both npz byte-identical to build1; I1 `models/` untouched (mtimes 11:02).
* `inputs_r36.json`: 53 entries; 48 resolve literally and hash-match; 5 Norse files hash-match after matching on-disk names that contain U+FFFD (mojibake of the accented filenames). Anyone using the JSON paths verbatim on Windows will not find them.
* `build_twice.json` `out_build12.json identical:false` is the `built`/`elapsed_s` fields (file sets `out_build12_identical_except_wallclock_fields: true`); the same sizes (39,681 B) and the array equality claim are consistent.
* GATE-CHANGE.md sec. 5: "NEW measurement" verbatim; the S1 ledger text now carries it too.

## 3. S1 (target 3)

See section 0 rows 3a-3d. Window arithmetic and live-state integrity hold; the problem is the coverage sentence. `S2` still requires `GRIND27_S2_CONTROL_OK=1` and the lane's own planted exact-relation control is not independently validated (S1 caveat, kept in the ledger row). The sandbox snapshot holding the window's top list/histogram expires ~2026-11-06 (`resume_window.json` `snapshot_expires_unix_ms` 1793993590719): if nobody exports it, the window's lists are lost and only the cursors/best remain.

## 4. B2 (target 4)

Recomputed from `sweep_rows.jsonl` (per-cell decode counts, best pmax per cell: mt_scale 6.281, mt_mod 6.496, php_scale 6.608, php_mod 6.271), `control.json` (pooled and per-relation splits) and `sweep.py:186-202`. All numbers in RESULTS reproduce. The substantive finding is the shared seed stream (row 4c), which RESULTS' "~10x R34" and the lane patch text do not disclose. RESULTS "remaining 99.39 % deferred" is right about the uniform space but understates that 62.6 % of R32-B2's already-drawn seeds are now at pf_v4 power and 37.4 % (119 blocks) are still at R32's prefilter power. A fresh stream (different `default_rng` seed) is needed for coverage to grow.

## 5. O3 (target 5) -- see rows 5a-5c.

## 6. O4 (target 6) -- see rows 6a-6d. The matrix is an audit by reading; X1 did not re-run any reading. The ranked top-8 do not depend on the two misclassified cells.

## 7. verify_solution.py (target 7)

* `python verify_solution.py --selftest`: SELF-TEST PASS (EN_MODERN 17.9/20.6, LATIN 18.2/17.7, EN_NOVOWEL 15.9/16.8, GREEK 19.6/19.8 vs bar 4.0 per page; wrong keys 0.1-2.1, FAIL x4). panel-R36, 12 registers, sha a0682f0c...
* Wrong key (3 random 13,000-int keystreams, `--pages 6`, `rerun_verify_rk11/12/13.out`): all three VERDICT: FAIL, each printing the three tested conditionals and "L7 caveat: NEGATIVE UNDER THESE REGISTERS/RELATIONS ONLY". Per-page clears: 2 of 54 decodes (3.7 % vs nominal 1 %; one keyskip2 +0.12, one free +0.37); never 2 under one relation. 2/54 is not significant (Poisson P(>=2 | 0.54) ~ 0.10), but it is the false-clear rate to keep in mind: with 3 relations x N pages, a 2-page rule is the only thing between a random key and PASS. Use `--pages 55` for real runs.
* PASS logic: `decide()` (`verify_solution.py:272-282`) counts rows per relation with `clears` and requires `MIN_PAGES` (2) under ONE relation; rows are one per (page, relation), so pages are distinct.
* `data/panels/panel-r36.npz` sha256 a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c (= P1); `testhalves-r36.npz` cdd55adac...
* `tests/validate.py`: 6 PASS (Runes-01, 05, 06, 03, 14, 73), `ALL VALIDATIONS PASSED`.
* Limits that stand: only keyskip1 plants are recovery-gated in the selftest; `free` has no bar above L=120; N=1 bar.

## 8. AUDIT-applied (target 8)

Spot-checked 5 of the applied edits for over-reach: `PAPER.md` (2 strikes / 2 markers), `round27/S1-CLOSEOUT.md` (3 markers / 2 strikes; original "EXHAUSTED"/"finished" kept struck, bound statement added), `PICKUP-HERE.md` (11 markers / 10 strikes; old text retained), `ELIMINATION-LEDGER.md` (12 strikes; Round-11 absolutes kept as reopen notes), `research/DEAD_ENDS.md` H3 (banner added above intact text), `round20/CAMPAIGN-PLAN.md` (SUPERSEDED note added to the bullet, text retained). No deletion of reasoning found. The 7 new R11 rows (`R11-N1..N5`, `R11-S1`, `R11-S2`, all `measured`): all four evidence paths each exist (RESULTS.md, results.json, SYNTHESIS.md, PREREG.md). `check_consistency.py` count check: matched 209 at AUDIT time; after this round's 10 new rows it failed (`PAPER.md:282, 443`) until the counts were updated to 219; passes now.

## 9. Ledger and gate (target 9) -- applied

Files: see section 12. LEDGER.json 209 -> 219 (+I1, I2, I3, P1, S1, B2, O2, O3, O4, X1). Normalisation: lane/round fields set; I2 id `R36-I2` -> `R36-I2-PFV4-KEYSTREAMS`, I3 `R36-I3` -> `R36-I3-D5C-TWO-MARGIN`; I2 conditionals list -> dict; bare evidence names -> full paths; O2 `negative` -> `partially-run` (a search has no positive control; as `negative` it would be an unsound negative); S1 given hypothesis/three_conditionals/not_covered/evidence. Patches applied: R27-CPORT-MT32-FULLSWEEP (P1 note + S1 note as mixed-instrument), R32-B2-PHP-MT-RAND and R34-B1-ORBITS-V3-PFV3 (B2, corrected). B1: not available.

Output of the gates after the edits (all from `liber-primus/`):

```
validate_ledger.py : ERRORS: 0 ; Unsound negatives: 0 ; 219 entries (71 measured, 58 negative, 37 audit, 19 open, 17 partially-run, 8 never-run, 5 eliminated, 3 superseded, 1 inconclusive); no warning names an R36 row
tests/validate.py  : 6 PASS, ALL VALIDATIONS PASSED
pytest tests/ benchmark/ -q : 26 passed
verify_capsule.py  : OK 89, ABSENT 14, SKIP 1 -> PASS
build_index / build_knowledge / build_problem / build_solved_pages : all wrote cleanly, paths resolve (build_problem n=12956 sha 023312066d.., 86 doublets)
check_consistency.py: all checks ok incl. "ledger counts in nav docs match LEDGER.json"; "No document drift detected."
```

## 10. B1: not yet available (no `RESULTS.md`; `run.out` at 118,000 of 138,121 units).

## 11. Round-37 candidates (<= 6, ranked)

| # | Candidate | Evidence prior | Cost | Why this rank |
|---|---|---|---|---|
| 1 | **Make the 12-panel usable by the sweep tooling** (enabler): `beam_v3.PANEL_PATH` repoint + `CLUSTERS` extension (I1 RESULTS "Consumers": `register_cond` silently ignores the 3 new registers), 12-wide `adjudicate.ROW_DTYPE` / `validate_row(n_registers=9)` / `check_r3_store`, `hitfn20`/`panelmax20` panel parameter (`AUDIT-applied.md` deferred items 10, 11) | not a decode; every other candidate needs it or must hand-roll it. Without it any new sweep either drops R3 persistence or ignores the new registers | ~half a day, no CPU | Preconditions for 2-3 and any future sweep; R3 is CI-enforced so this is also a compliance gap |
| 2 | **U1-U3 as one lane**: 2016 clauses + remaining LP1 imperatives as seeds/keys; LP1 numbers as key schedule; map->road->direction as composed word-boundary-keyed decoder (`O4-clue-coverage/untried.md`, scores 9/9/7) | measured coverage holes: `round26/C/seeds.json` has none of the 2016 clauses; no row composes the three clauses; R26-C used 16 sums only as PRNG seeds. Prior that any works: low (~1-2 %; the 2016 sentence may be devotional restatement, `RESULTS.md` O4), but it is the only bounded, text-supported, never-run family | ~10k decodes total, minutes on beam_v3 | needs each variant to carry a plant through the soft anti-repeat filter and continuity across page joins (O4 note on `ELIMINATION-LEDGER.md:551-569`); fix the H7/H12 x F2 cells first so NEVER is not double-counted |
| 3 | **Re-score the English-only/legacy readings under the repaired instrument**: U5 (Round 10 L2/L3 streams; M1 pooled z=6.94, English-gated near-flag), U6 (R11 N1-N5/S1/S2 backfilled rows; R22-C 185 operations), ornament bands x 12 registers | PICKUP "Reopen under the repaired instrument" table: all minutes-to-1 h; the M1 near-flag is the only English-gated near-miss never re-scored outside English | ~hours | cheap, bounded; 12-register power at L~2.9k for the R10 streams must be measured first (kill rule in U5) |
| 4 | **L-matched `free` null** (O3 decision): `bars_v3` has free at L=120 only; `verify_solution.py` also stops at L=120 for free; X1's random keys cleared `free` at +0.37 once | instrument item: unlocks `free` as evidence at L=240/262/729, where O3's ILP32 free cell (15.15 vs n=100 null max 14.33) sits unresolved | ~2.5 s/draw at L=729, n=300 x 3 L ~40 min | without it `free` rows must stay "not usable as evidence" |
| 5 | **PHP awake remainder, on a fresh stream**: blocks 200-318 of the `default_rng(3301)` stream at pf_v4 power (R32 drew them at pf_v2 power 0.47-0.74), then a NEW stream (`default_rng(<other>)`) for real coverage | B2 (4c): R36's 0.6073 % added no seed coverage; remaining uniform space 99.03 % per cell; expected value per seed is flat | ~30-40 min per 100 blocks, awake, rows persisted | low value per hour; do only with item 1 done so rows are 12-wide; call it coverage x power, not "0.607 %" |
| 6 | **More S2 windows** (42.6 of 35 min at 26 k seeds/s on 2 vCPU) -- conditional on (a) the engine's planted exact-relation control being independently validated, (b) the sandbox snapshot lists being exported before ~2026-11-06, (c) re-scoring `top_S2.json` (1024 old entries) under panel-R36 so the coverage figure stops being mixed | the branch the project has measured the longest; prior flat over 2^32; panel-R36 coverage is 1.28 % | ~25 h sandbox, or an 8-vCPU sandbox (the 8-vCPU request returned 400) | lowest rank: expensive, flat prior, and each window is a NEW measurement that does not extend the Round 19-gated 44.1 % |

Not ranked (zero compute): the Wayback CDX leg of O2 (needs a tool that can query web.archive.org; the O2 addendum says "Temporarily Offline"); the dead `ky_*` duplicate note for O4.

## 12. Files edited by X1

| File | Change |
|---|---|
| `LEDGER.json` | +10 rows (R36-I1/I2/I3/P1/S1/B2/O2/O3/O4/X1); `r36_p1`/`r36_s1` notes + 2 not_covered strings + 2 evidence paths on R27-CPORT-MT32-FULLSWEEP; `r36_b2` on R32-B2-PHP-MT-RAND and R34-B1-ORBITS-V3-PFV3; `counts.total` 219, `by_status` recounted, Round 36 note appended. Pre-edit copy `X1-redteam/LEDGER.pre-x1.json` |
| `README.md` (root) | status line: Round 36 filed sentence prepended |
| `PAPER.md` | lines 282, 443: 209 -> 219 entries |
| `liber-primus/PICKUP-HERE.md` | new "Round 36" status block; Round 35 header struck/marked superseded ("Next" no longer current); lines 64, 281: 209 -> 219 |
| `liber-primus/ELIMINATION-LEDGER.md` | new "## Round 36" section above Round 35 |
| `liber-primus/analysis/README.md` | new `round36/` row above `round35/` |
| `liber-primus/handoff/SOLVER-STRATEGY-2026.md` | line 31: 209 -> 219 |
| `analysis/round36/X1-redteam/*` | new: RESULTS.md, re-run scripts + outputs, apply_ledger.py, apply_nav.py, LEDGER.pre-x1.json |
| regenerated by the build scripts | `INDEX.json`, `KNOWLEDGE.json`, `PROBLEM.json`, `SOLVED-PAGES.json` (content unchanged apart from regeneration) |

Not edited: root `PICKUP-HERE.md` (frozen at Round 18, points to the live file); `liber-primus/README.md` (carries no per-round state); any lane directory (I1 `mappings.md:3`, O4 matrix cells, B2 patches, S1 patch remain as written -- the ledger rows carry the corrections).

## 13. Decisions for the coordinator

1. I1 `mappings.md:3` / RESULTS "Reproducibility" still say "fully deterministic": correct them (one-line) or leave the ledger note as the record?
2. O4 matrix: re-classify H7 x F2 and H12 x F2 (NEVER -> TRIED-LEGACY via R30/campaign18) and re-issue `counts.json` (NEVER 66)?
3. S1 snapshot export before ~2026-11-06 (the window's top list/histogram live nowhere else).
4. Whether the lane `ledger_patches.json` files for B2 and S1 should be amended (they carry the wrong id / single-instrument coverage) or marked superseded by this RESULTS.
5. B1 audit when it lands (RESULTS + readjud store vs the 12-panel; check it uses panel-R36, not I1's `models/panel12.npz`).

## Conditionals (Doctrine Q4)
1. Key space: none swept (audit). 2. Transition model: re-runs use the Round 32 keyskip beam (400,3) with the correct key (gate cells) and beam_v3 keyskip2 (O3); `verify_solution.py` runs keyskip1/keyskip2/free. 3. Adjudicator: panel-R36 (12 registers) for gate cells; O3 windows reproduce under the lane's own panels (9 and I1-12).
