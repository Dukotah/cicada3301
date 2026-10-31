# Round 41 / C1 - R14, R15 re-score from archived campaign7 code; blocked-cell artefact verification: RESULTS

2026-10-31. PREREG.md (and PREREG-ADDENDUM-1-R44.md) written first. No git. One process at a time. psutil not installed: the round40 `lib.free_gb()` CIM reading was used for the RAM rule. Everything is conditional on (the variants campaign7 defines) x (exact deterministic decrypt, no skips) x (panel-R36, 12 registers, direct). No discovery claim.

## 1. R14 / R15 (cells H4xF3, L2xF3, L15xF2)
Faithfulness: `camp7.py` (functions copied verbatim, run `python -I` from this dir, archive untouched) reproduces the archived results exactly with the repo's `lp.score`: R14 best -6.897 and all five per-variant bests and best text; R15 best -6.873 and all 24 per-matrix bests (`faithfulness.json`). The numpy Hill used for null speed equals the archived `apply_hill` on all 24 variants. The archive and corpus copies are identical modulo line endings.

Instrument: round40 `lib.py` direct machinery (copied unchanged), standing matched null `benchmark/bars_matched.py` blockperm (Random(60000+j)), blocks 100/250/1000, D=1000 each, ciphertext re-cut to the real page/word lengths, whole family re-derived each draw. alpha 0.0025 per (family, level); decision p = max of three; cross needs Z-family and raw both.

| family / level | units | best pmax (unit) | p(Z) 100/250/1000 | p(raw) 100/250/1000 | decision p(Z)/p(raw) | cross |
|---|---|---|---|---|---|---|
| R14 W (whole stream) | 20 | 2.705 (W4 +1 atb) | 0.353/0.491/0.538 | 0.368/0.374/0.366 | 0.538 / 0.374 | no |
| R14 P (page units) | 1,100 | 3.642 (W5 +1 atb p22) | 0.831/0.886/0.528 | 0.892/0.893/0.833 | 0.886 / 0.893 | no |
| R15 W (whole) | 24 | 2.443 (M3_4x4.M) | 0.525/0.583/0.641 | 0.641/0.749/0.548 | 0.641 / 0.749 | no |
| R15 P (page units) | 1,320 | 4.094 (M3_4x4.M p36) | 0.257/0.771/0.660 | 0.389/0.424/0.338 | 0.771 / 0.424 | no |

Best W-level pmax 2.7 / 2.4 and best page pmax 3.6 / 4.1 sit far below the survivor12 key-sweep bar (10.46 at N=1e6; non-binding here). No crosser, no ORACLE bundle.

Positive controls (every variant x EN_MODERN/LATIN/EN_NOVOWEL, exact inverse enciphering, exact recovery asserted, level W and level P): R14 120/120 recognised (W null max 4.62, P 5.50); R15 144/144 (W 3.92, P 4.80). `positive_control: passed`. Plant files: `result_R14.json`, `result_R15.json` (`plants`).

Verdict: R14 and R15 `negative` conditional on the three conditionals in PREREG Q4; cells H4xF3, L2xF3, L15xF2 -> TRIED (panel-R36) (`matrix_cell_moves.json`).

## 2. Other five blocked cells (in-repo search only: working tree, archive/, corpus/)
- **R31** (L12xF5, L13xF5, S1xF5): artefact NOT absent. Code `round10b/B3-semantic-keys/` regenerates the 37,696 readouts in ~4 min; `T1-RESULTS.json` stores top-50 readouts and top-15 promoted page decodes. Blocked by the instrument: 5-9-rune readouts are below the 32-rune panel floor; promotion uses a phase-flexible per-segment decode not in the direct/beam machinery. Not run. not_covered: readouts as language under any panel-class scorer.
- **R35** (H7xF4, H8xF4 partial): ABSENT. `round12/C2/` holds only `fetch.sh` (33 pg/url lines); none of the texts exists anywhere searched (name and title grep); gitignored; not hash-pinned (round26/B records no per-text hashes), so a network re-fetch would be a new artefact. data/keys/armada18-19 are different texts.
- **R36** (H7xF9): ABSENT. R17 P1 (Bitcoin) and P2 (NIST beacon v1, random.org) data directories do not exist; R24 C8 `cache/` has only a 2 KB `timestamps.json`. The 28 P3 table pads are regenerable and were done in R40-B3; they are not the dated pads. Multi-GB network fetch.
- **R44** (H12xF7, H2xF7 partial): artefact PRESENT for bookcipher.py: 5 books + code in `analysis/bookcipher/` (premise false). The 6 books of `bookcipher_expand.py` are absent. Attempted: the pre-registered pointer-crafted control gave 0.743-0.815 letter recovery (< 0.90) on the first six L1 plants, so the Q5 kill fired and scoring was not run (a 1..29-letter forward window cannot reach every target letter). Status partially-run; cell stays unchanged.
- **43 B1 keys**: ABSENT. `armada_osint/artifacts/raw/{2012..2017}.md` not present (gitignored). archive/corpus hold `scream314_2012/2013/2014/2017` md (no 2015/2016); that substitute reproduces auto key MIDISCV but not WORKING (the only two auto keys stored in `b1_results.json`), so it is a different artefact. Not run.

## 3. Deviations from PREREG
(1) R44 added by dated addendum after the artefact search; it was not scored (control kill), as the addendum specified. (2) psutil unavailable, CIM RAM reading used. (3) The R14 level-W stream concatenates per-page decrypts (state resets per page, as campaign7 does). (4) Importing nothing from round40 side effects: `lib.py` was copied, so round40 `c1.log` was not touched.

## 4. Files
`PREREG.md`, `PREREG-ADDENDUM-1-R44.md`, `RESULTS.md`, `ledger.json`, `ledger_patches.json`, `matrix_cell_moves.json`, `camp7.py`, `lib.py`, `t_faith.py`, `faithfulness.json`, `run_c1.py`, `run_r44.py`, `mk_deliverables.py`, `result_R14.json`, `result_R15.json`, `null_R1x_b*.npz`, `null_draws.jsonl`, `plants_first6.json`, `r44_first6.json`, logs.
