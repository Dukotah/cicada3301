# Round 46 / A1 — instrument hygiene: alignment.json repair, Fable52 repoint, PREREG addendum stamps

_Pre-registered 2026-11-24, before any output of this lane. Lane spec: `analysis/round46/CAMPAIGN-PLAN.md` row A1.
Inputs read before writing (code/docs and read-only inspection of inputs, no lane outputs): `../CLAUDE.md`,
`ARMADA-DOCTRINE.md`, `round45/SYNTHESIS.md` §2, `round45/S1-transcription/{RESULTS.md, correct_map.py,
corrected_map.json}`, `round45/X1-redteam/AUDIT.md` §6, `analysis/stones/{build_dataset.py, pipeline.py,
CAMPAIGN-V-FINDINGS.md, disagreements.json}`, `analysis/independent-read/oae_deepdive.py`, `analysis/fable52/*`,
`round45/T1-t7-mechanism/{PREREG.md, run.log}`. The fable52 path edits (part b) were made before this file was
written; they are code edits, not outputs, and nothing has been re-run. The sha256 of this file is written to
`run.log` before the first lane script runs; any addendum goes below a `## Addendum n` header and the sha256 of the
file prefix through that addendum is stamped in `run.log` (the R45 T1 convention, which part (c) turns into a check)._

## 0. What this lane is

Three instrument repairs (doctrine R1/R5: audit the instrument, not the space). No decodes, no key sweeps.

- **(a)** `analysis/stones/alignment.json` (Campaign-V image-line -> canon-line map) mis-registers lines. Repair it
  from S1's `corrected_map.json`, keep the old file as `alignment.v1.json`, and measure the downstream change.
- **(b)** `analysis/fable52/` hard-codes an external clone (`...\Temp\lpx\r\...`) and absolute repo paths. Repoint to
  in-repo data per X1 §6 and check whether `OUTPUTS.txt` reproduces.
- **(c)** `check_prereg_stamps.py`: every `Addendum` block in round45/round46 `PREREG.md` files must carry a sha256
  stamp. Report violations; rewrite nothing.

## 1. Facts already observed while reading inputs (stated so they cannot be "discovered" later)

- `alignment.json` semantics as consumed: `build_dataset.py` (and S1's `build_set.py`/`adjudicate.py`/`md_template.py`)
  pair `clean[i]` (segmented lines with >= 10 boxes) with `alignment[str(n)][i]` **positionally**; a line is
  "exact" (labelled) iff its box count equals the canon line's length. `armada_osint/redrune/extract.py` and
  `round44/P1-red-ink/census.py` use it only as a gline -> image map.
- `corrected_map.json` gives, per image and `clean_i`, `orig_gline` (= v1 positional value), `true_gline` (S1's
  page-constrained DP) and `count`. It differs from v1 at images 6, 11, 15, 26, 36, 37, 39, 41 and has
  `true_gline = null` at 4 rows (5/11, 11/4, 26/4, 41/5); in all 4 the v1 value is non-exact (count != canon length).
- S1's DP was restricted at images 49/50 to "keep the committed split". Image 49 segments to three lines of
  23/22/21 boxes; canon page 49 is lines 551/552/553 of length 23/22/21; image 50 (the numeric grid page) segments
  to zero lines, yet v1 assigns 553 to image 50. So line 553 was never cropped. This is a fifth defect S1 did not list.
- `analysis/stones/disagreements.json` (Campaign-V's 86 classifier-vs-canon disagreements) sits on lines 402, 173,
  171, 76 (from its first rows) — S1's four false-exact lines. `CAMPAIGN-V-FINDINGS.md` already called all 86
  "off-by-one line-misalignment artifacts on 4 ornamented lines".
- Fable52 inputs: the external clone is still present on this machine. `data/krisyotam_runes.txt` is rune-identical to
  the external `lp2-transcription.txt` (13,136/13,136) and differs at exactly **2 separators** (`-` vs `.`, before
  unsolved runes 1886 and 9648). The W1 `inputs/lp1-plaintext-reference.txt` is sha256-identical to the external one.
  The grid: `data/sources/rtkd_master.txt` (and `relikd_p40-53.txt`) carry the 256 base-60 tokens; they differ from
  the external `lp2-grid-256.json` at **5 cells** (indices 45, 50, 165, 172, 246; letter-case "2021 corrections"),
  none in the leading digit. `dataset/liber_primus.json` does **not** contain the grid (it holds rune pages only).
- T1's addendum stamps (`round45/T1-t7-mechanism/run.log`) equal sha256 of the PREREG.md byte prefix through the end of
  that addendum.

## 2. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?**
(a) A hit = the repaired map removes the known false-exact lines and the classifier's 86 disagreements collapse under
the repaired labels. Positive controls: line 402 (verified by eye in S1, item K075) must change label; v1's labels
must be reconstructed **exactly** (all 10,774, glyph by glyph against `dataset.npz` `y`/`prov`) from `alignment.v1.json`
+ `corrected_map.json` counts before any v2 number is trusted. (b) A hit = every number in `OUTPUTS.txt` reproduces,
except where an input differs; control = t1/t2 also run once against the external files (scratch copies, not
committed) so that any residual difference is attributed to an input, not to the repoint. (c) Plants: a synthetic lane
dir with three addenda — one correctly stamped, one stamped with a stale hash, one unstamped — must be classified
VERIFIED / MISMATCH / UNSTAMPED; and T1 (known stamped) must come out VERIFIED on real data.

**Q2 — What measured fact raises the prior?** S1 A4/A5 (`round45/S1-transcription/RESULTS.md` §2, line 402 eye-verified);
`stones/CAMPAIGN-V-FINDINGS.md` (86 disagreements on 4 lines); X1 `AUDIT.md` §6 (path list); SYNTHESIS §2 (W1/S1 unstamped).

**Q3 — Is the space bounded?** Yes, enumerable and fully covered: 56 images / 594 canon lines / 10,774 labels; 11
fable52 scripts; every `PREREG.md` under `analysis/round45/*/` and `analysis/round46/*/`.

**Q4 — Three conditionals.**
1. *Space:* all 56 images' alignment entries; all fable52 scripts; all R45/R46 PREREG addenda present at run time.
2. *Transition model:* S1's count-based page-constrained DP is the registration model. A mis-registration that
   preserves box counts within a page is invisible to it. Label effects are computed from per-line box counts, assuming
   the segmenter is deterministic — tested by the exact v1 reconstruction.
3. *Register/adjudicator:* the Campaign-V classifier is **not retrained** (its training script is not in the repo);
   its committed out-of-fold predictions (`oof_pred.npy`) are re-scored against repaired labels. The O/A/AE 450 are
   re-derived by re-running `oae_deepdive.py`'s PCA+KMeans logic on repaired labels inside this lane dir.

**Q5 — Kill condition.** (a) If v1 labels cannot be reconstructed exactly, stop at quantification (no v2 dataset).
(b) If krisyotam is not rune-identical to the external transcription, stop. (c) If any plant is misclassified, the
checker's report is "uninformative". Checkpoint: after the v1 reconstruction (≈ 10 % of budget).

## 3. Repair rules for alignment.json (frozen)

v2 keeps the schema: a dict `"0".."55"` -> list of int canon glines, read positionally against `clean`.
- **R-a1.** `v2[n][i] = corrected_map[n][i].true_gline` where not null.
- **R-a2.** Where `true_gline` is null: keep the v1 value (it is non-exact in all 4 cases, so it yields no label;
  flagged as "unresolved" in the diff).
- **R-a3.** Image 49 `clean_i 2` -> 553 (see §1); image 50 -> `[]`.
- **R-a4.** List length = number of clean lines; v1 tail entries beyond it (never read by positional consumers) are
  dropped. They are short canon lines (< 10 glyphs) or entries moved to the right image.
Acceptance: every v2 exact line has count == canon length by construction; no gline appears twice except an R-a2 row;
no consumer crashes on load (`tests/validate.py` green; consumers that iterate the map run in a dry check).

## 4. Downstream measures (reported, no thresholds — descriptive instrument audit)

1. `dataset.npz` labels: removed / added / changed (glyph level), and the fraction of 10,774.
2. Classifier: OOF agreement with v1 labels and with v2 labels; how many of the 86 disagreements are resolved.
3. O/A/AE: how many of the 450 sit on changed lines; re-run of the KMeans mismatch on v2 labels and the set diff.
4. Consumers that read `alignment.json` and what changes for each (incl. R45 S1 scripts, which assume v1).
Cheap reruns (< 10 min) are done; anything costlier is quantified, not run.

## 5. Outputs

`run.log`, `repair_alignment.py`, `alignment_diff.json`, `downstream.py`, `downstream.json`, `fable52_rerun/`
(logs), `fable52_compare.md` (in RESULTS), `check_prereg_stamps.py`, `prereg_stamps.json`, `RESULTS.md` (closing stamp),
`ledger_rows.json` (ids `R46-A1-…`). Large rebuilt arrays (if any) are gitignored-class and named in RESULTS.
No edits outside this dir except `analysis/stones/alignment.json` (+ `alignment.v1.json`) and `analysis/fable52/*`.
No `LEDGER.json` edit, no commit.

## Addendum 1 — 2026-11-24 (after the first repair run and downstream.py; before RESULTS)

**Reason.** R45-S1 PREREG Addendum A5 (`strip_registration.json` K250:0) shows the DP is wrong at image 11: the blind
strip read on clean line 3 fits canon 127 at 0.80 against 0.36 for 128. So `corrected_map`'s `true_gline 128` there
is an error, and v1's 127 was right. The first run applied R-a1 there and produced the only duplicate (128, at 11/3
and at the R-a2 row 11/4).
**Change.** New rule **R-a5**: image 11 `clean_i 3` -> 127 (blind-read evidence overrides the DP). Image 11 then
equals v1 exactly. Both lines are non-exact (count 21 against 24, count 22 against 23), so no label, classifier or
O/A/AE number can move. `repair_alignment.py` and `downstream.py` are re-run. Nothing else changes.
