# R46 / A1: instrument hygiene, RESULTS

_2026-11-24. Pre-registration: `PREREG.md` (sha256 stamped in `run.log` before any lane output; Addendum 1 stamped
before its re-run, and VERIFIED by this lane's own checker). Edited outside this dir: `analysis/stones/alignment.json`
(plus the new `alignment.v1.json`) and `analysis/fable52/*` only. No `LEDGER.json` edit, no commit. `tests/validate.py`
was green after all edits._

## Headline

1. **`alignment.json` is repaired.** 25 positional entries changed (24 R-a1, 1 R-a3; 4 R-a2 rows and the R-a5 row flagged but unchanged), 10 dead tail
   entries dropped, and one new
   defect (line 553) fixed. The old file is kept as `alignment.v1.json`. The repair adds **372 labels**
   (10,774 -> 11,146) and corrects **89 v1 labels** on lines 76/171/173/402. Those 89 are 0.83 % of the dataset,
   and 87 of them change rune. **No label is removed.**
2. **Every one of Campaign-V's 86 classifier-vs-canon disagreements is resolved by the repair.** The committed
   out-of-fold predictions agree with the repaired labels **10,774/10,774** (v1: 10,687). On the 351 newly
   labelled glyphs that have a prediction, the classifier agrees **351/351**. That is an independent check that
   the new registration is right. The one remaining `all_pred` mismatch (image 36, clean line 2, glyph 2) is
   in-sample memorisation of its wrong v1 label (ᛗ from line 402). Its out-of-fold prediction already agrees with
   v2. So the classifier was right everywhere, and the 86 disagreements were the label map's fault.
3. **The "450 O/A/AE disagreements" are not a stable instrument output.** Re-running `oae_deepdive.py` reproduces
   the committed 450 exactly on v1 labels (the control), at every KMeans seed from 0 to 9. On v2 labels it gives
   **670**, again at every seed. Only 4 of the 450 sit on misregistered lines. The jump comes from a basin flip in
   KMeans: dropping **42 random** O/A/AE glyphs from v1 gives 430–438 in 8 of 10 draws and 623–630 in 2 of 10. Any
   claim resting on that exact list (`independent-read/oae_mismatch.json`) is conditional on the clustering
   landing in one basin. The count is not a property of the glyphs; R46-X1 (x1_oae_basins.json) finds both label sets reach
   both basins (v1 5/20, v2 1/20 flip) and a 282-glyph stable core containing 258 of the 450. Use the core as a
   candidate list, not the 450 count.
4. **Fable52 runs from in-repo data.** reconcile, t3, t4, t4b and t6 reproduce `OUTPUTS.txt` exactly. t1, t2 and
   t8 move by small amounts, and **every difference comes from an input, not from the repoint**. Re-running the
   same scripts on the external files reproduces `OUTPUTS.txt` exactly.
5. **PREREG stamp rule.** `check_prereg_stamps.py` passes its three plants, and T1 (known stamped) comes out
   VERIFIED. **10 unstamped addenda:** W1 ×2 and S1 ×5 (known), **S1b ×2** (new, not named in SYNTHESIS §2) and
   **R46 S2 "S2-A" ×1** (in flight; written today, after unsealing).

## (a) alignment.json repair

**Semantics kept.** `alignment[str(n)][i]` is the canon global line shown by the i-th clean (≥ 10-box) segmented
line of image n. That is what every positional consumer already assumed. The schema is unchanged: a dict of 56 int
lists. Rules from PREREG §3 plus Addendum 1:

| rule | rows | what |
|---|---:|---|
| R-a1 (S1 DP `true_gline`) | 24 | images 6, 15, 36, 37, 39 (short-line drop shift and the 35/36, 38/39 page-break crossings) |
| R-a2 (DP null -> keep v1) | 4 | 5/11, 11/4, 26/4, 41/5; all non-exact, so no label |
| R-a3 | 1 | **image 49 clean line 2 -> 553** (new defect: v1 put 553 on image 50, the grid page, which segments to 0 lines, so 553 was never cropped; count 21 = canon 21) |
| R-a5 (Addendum 1) | 1 | image 11 clean line 3 stays 127 (S1 A5 blind strip read beats the DP's 128; non-exact either way) |
| R-a4 | 10 tails | v1 entries beyond the clean-line count are dropped (9 short canon lines < 10 glyphs, plus 553) |

Full per-row diff: `alignment_diff.json` (v1 sha256 and v2 sha256 recorded). Q5 gate: the v1 labels were rebuilt
**exactly** (10,774/10,774, glyph by glyph) from `alignment.v1.json` + S1's box counts, and image-49 crops were
re-cut bit-identical (45/45). The label arithmetic is therefore exact, not estimated.

**Labels** (`downstream.json`): removed 0, added 372 on lines 73, 75, 76, 169, 170, 171, 173, 399, 400, 402, 420,
432–436 and 553. Re-lined 89 (the four false-exact lines S1 flagged; this confirms 76/171/173, which S1 had only
DP-flagged), and 87 of those change rune. I did not rebuild `dataset.npz` in place, because `analysis/stones/` is
out of scope. To rebuild it, run `python analysis/stones/build_dataset.py` (a ~2 min segmentation pass) with the
repaired map. The arithmetic above predicts the result exactly.

**Consumers of `alignment.json`** (grep):

| consumer | effect |
|---|---|
| `stones/build_dataset.py` | correct with v2 unchanged; rebuild gives 11,146 labels |
| `armada_osint/redrune/extract.py`, `round44/P1-red-ink/census.py` (gline -> image map) | 584 glines mapped. Lines 399/432 move to the right image. The 9 short lines leave the map (they had no glyphs), so red-glyph page attributions near the 35/36 and 38/39 breaks become correct |
| **R45 S1 scripts** (`correct_map.py`, `build_set.py`, `adjudicate.py`, `md_template.py`, `locate_unloc.py`, `audit_alignment.py`, `reinspect_render.py`) | **assume v1.** `correct_map.py` raises IndexError on image 50 (now `[]`), and `adjudicate.py`'s "crop shows a different line" logic reproduces the *v1* pairing. To reproduce R45 S1, repoint them to `alignment.v1.json` (outside A1's write scope; flagged for the coordinator) |

## (b) Fable52 repoint

Paths are now repo-relative (`__file__`-based). The mapping follows X1 §6: `load.THEIRS_TXT` -> `data/krisyotam_runes.txt`;
lp1 reference -> `round45/W1-spaces/inputs/lp1-plaintext-reference.txt` (sha256-identical, `902e9db8…`); grid ->
`fable52/lp2-grid-256.json`, built by the new `fable52/derive_grid.py` from `data/sources/rtkd_master.txt`
(`dataset/liber_primus.json` has no grid page, so the brief's suggested source could not be used);
`reconcile.py` -> pinned copy `fable52/inputs/lp2-corpus.json` (sha256 `7f311254…`, which the script asserts);
`doublet_positions.json` is now written next to the script (it used to be written to the cwd). Re-run logs are in
`fable52_rerun/`.

| script | reproduces? | difference and cause |
|---|---|---|
| reconcile | yes | — |
| t1 | all but 2 counts | dash pairs 2721 -> **2723**, period 174 -> **172** (rate 0.57 -> 0.58 %): krisyotam has `-` where the external file has `.` before runes 1886 and 9648. Doublet counts and `doublet_positions.json` are byte-identical |
| t2 | observed z identical | p(family) uniform null 0.0399 -> **0.0374**, power 0.48 -> **0.47**, 95 % bar 4.46 -> **4.47**: 5 grid cells differ in letter case (rtkd vs the external "2021 corrections"). This changes the value predicates in the family; lead0 is unchanged |
| t3, t4/T5, t4b, t6 | **exactly** | — |
| t8 | all but one value | sentence length z +0.83 -> **+0.89** (172 vs 174 sentence breaks; same two separators). Verdict unchanged (CONTROL FAILED, uninformative) |

Control (PREREG Q1): t1, t2 and t8 re-run in scratch against the external files give 2721/174, 0.0399/0.48/4.46 and
sentence z +0.83, matching `OUTPUTS.txt` exactly. Every change is therefore an input change. None changes a Fable52
conclusion: the p50 family p sits below 0.05 under the uniform null in both cases and at 0.54 under the
circular-shift null. **Open choice for the coordinator:** the two separators and the 5 grid cells are real
transcription differences between lineages. Which one is canonical is a transcription question, not an A1 repair.

## (c) PREREG addendum stamps

Rule (now executable): every `#… Addendum <id>` block needs a sha256 stamp equal to sha256 of the PREREG.md byte prefix
through the end of that addendum, recorded in the lane dir (`run.log`/`*.log`/`*.out`/`*.sha256`/`*.txt`) or in the
block itself. Prefixes are compared after stripping trailing newlines and an optional '---' line. The check proves the PREREG is
append-only; it does not prove a stamp was written before the outputs (compare log timestamps for that). Plants: stamped / stale / unstamped -> VERIFIED / MISMATCH / UNSTAMPED (PASS). Real data (`prereg_stamps.json`):

| lane | addenda | status |
|---|---:|---|
| R45 T1 | 2 | VERIFIED (real positive control) |
| R46 A1 | 1 | VERIFIED |
| R45 W1 | 2 | UNSTAMPED (known) |
| R45 S1 | 5 | UNSTAMPED (known; A4's `7b76c643…` is a data hash, not a PREREG stamp) |
| R45 S1b | 2 | **UNSTAMPED (not previously reported)** |
| R46 S2 | 1 | **UNSTAMPED** (S2-A, in flight at check time) |

History is not rewritten. Base-PREREG stamps are reported for information only. R46 L1/P1/S2/A1 verify; R45 I1/S1/S1b/W1/X1
have none in their logs. Suggested CI use: `python analysis/round46/A1-hygiene/check_prereg_stamps.py analysis/round46/*/`
(exit code 1 on any violation). This is not wired into CI here.

## Coverage × power and the three conditionals

- **Coverage:** all 56 images / 594 canon lines / 10,774 v1 labels; all 11 fable52 scripts; all 10 R45/R46 lane PREREGs.
- **Power:** v1 rebuild exact (10,774/10,774); classifier agreement on the newly labelled lines 351/351; O/A/AE control
  reproduces 450 exactly; fable52 external-input control reproduces exactly; stamp checker 3/3 plants plus the T1 real control.
1. **Space:** as above. The O/A/AE instability was measured over KMeans seeds and over one perturbation family only
   (42-glyph removals).
2. **Transition model:** S1's count-based page DP, with one blind-read override. A registration error that keeps box
   counts within a page stays invisible, except where the classifier cross-check sees it (it would, for exact lines).
3. **Adjudicator:** the committed Campaign-V classifier, not retrained (its training script is not in the repo);
   the O/A/AE KMeans as committed.

## Files

`PREREG.md`, `run.log`, `repair_alignment.py` (+`.log`), `alignment_diff.json`, `downstream.py` (+`.log`, `downstream.json`),
`oae_stability.py` (+`.log`, `oae_stability.json`), `check_prereg_stamps.py`, `prereg_stamps.json`, `fable52_rerun/*.out`,
`ledger_rows.json`. Outside: `analysis/stones/alignment.json` (v2), `analysis/stones/alignment.v1.json`,
`analysis/fable52/{load,reconcile,gp,t1_doublet_structure,t2_p50_mask,t4_wordlen_burst,t4b_solved_control,t6_wordlen_lagscan}.py`
(edited), plus new `analysis/fable52/{derive_grid.py, lp2-grid-256.json, inputs/lp2-corpus.json}`.
`downstream.py`/`oae_stability.py` need sklearn, so run them in WSL:
`wsl -d Ubuntu -- bash -lc "cd …/liber-primus && python3 analysis/round46/A1-hygiene/downstream.py"` (~1 min).

---
CLOSING STAMP — R46/A1 closed 2026-11-24. alignment.json repaired (v1 kept). 86/86 Campaign-V disagreements resolved;
+372/±89 labels. The O/A/AE 450 is basin-dependent (450 vs 670). Fable52 is in-repo; every residual comes from an input
(2 separators, 5 grid cells). Stamp checker live: 10 unstamped addenda (W1 2, S1 5, S1b 2, S2 1).

## X1 corrections applied

_Applied by the Round 46 coordinator from `../X1-redteam/AUDIT.md` (2026-11-24); PREREG untouched._ §2.5 items 1–3: "29 positional entries changed" → 25 changed + 4 R-a2 rows flagged unchanged (plus the R-a5 row); the O/A/AE count is basin-dependent but a 282-glyph stable core holds 258 of the 450 (R46-X1-OAE450-BASINS; PCA seed has no effect); the stamp checker proves append-only history, not chronology. Same edits in `ledger_rows.json`.
