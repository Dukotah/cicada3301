# R45 / S1 — Independent transcription audit: RESULTS

_2026-11-23. Pre-registration: `PREREG.md` (dated before any output; addenda A1–A5 dated and ordered
relative to the frozen reads). Nothing in the dataset, `LEDGER.json` or any existing file was edited._

## Headline

**0 canon errors in 398 adjudicated canon glyphs**, including a **full census of all 86 doublet sites
(172 glyphs)**. Measured canon glyph error rate: **0 / 66** on the primary stratified-random frame
(exact Clopper–Pearson 95 % CI **[0, 5.4 %]**), **0 / 146** on all uniform-position glyphs (CI
**[0, 2.5 %]**), 0 / 398 over the whole read set (CI [0, 0.92 %]; that set is enriched for look-alike families, so the bound is
not a uniform-rate bound). **No correction is proposed**: no doublet site dissolves (T7's 86-site input is
confirmed glyph by glyph), no near-doublet hides a doublet, no solved-page boundary is touched, and the
`PROBLEM.json` stream sha256 `023312066df4…3af1585` is unaffected.

**But the lane as briefed could not run, and it found a defect in a committed instrument instead:**

1. **The RAT frame does not exist in committed data, and its premise is wrong.** The repo's only record
   of RiskAverseTech/cicada-ioc (`analysis/transcription/TRANSCRIPTION-VERDICT.md`, 2026-11-20) says RAT
   **disagrees with canon at 0 of 12,807 aligned glyphs**; the ~149 residue is positions RAT did **not
   align**, not disagreements. No per-position RAT list is committed and no pinned fetch exists
   (`data/fetch_sources.py` pins only rtkd/iddqd, the same root lineage as canon), so per the brief it was
   not fetched. The 149 positions are **not covered** by this lane.
2. **`analysis/stones/alignment.json` (Campaign-V) mis-registers lines** (A4/A5). It assigns canon line 399
   (page 36) to image 35 and line 432 (page 39) to image 38, the only two places where its line→image map
   crosses a canon `%` page break. Separately, `build_dataset.py`'s positional `clean[i] ↔ alignment[i]`
   pairing drops canon lines under 10 glyphs and shifts every line above them. Where two adjacent canon
   lines share a length, the crop is labelled "exact" but shows the wrong canon line. **Verified directly:**
   item K075, a doublet site (canon F,F on line 402), got an "exact" crop that actually showed line 401.
   The blind read was TH,P, which is line 401's glyphs. The page-constrained registration (`correct_map.py`) flags 4 false-exact
   lines (canon 76, 171, 173, 402 ≈ 89 glyphs) whose labels in `analysis/stones/dataset.npz` would then be
   wrong (≈ 0.8 % of the 10,774 training labels). Only line 402 is verified by eye; the DP itself is
   fallible (it mis-registered K250's strip, which the blind read corrected). This bears on the Campaign-V
   classifier and on `analysis/independent-read/` (its 450 O/A/AE "disagreements" were computed against
   these labels). **Reported, not repaired.**

## Coverage × power

| frame | what | glyphs | canon errors | CP 95 % | notes |
|---|---|---:|---:|---|---|
| F1 | stratified random, 11 page blocks × 6 (seed 45013) | 66 | 0 | [0, 5.44 %] | 61 blind-confirmed; 2 reader errors (zoom-confirmed canon); 3 re-located + re-read unblinded |
| F2 | **census of all 86 doublet sites** | 172 | 0 | [0, 2.12 %] | 84 sites confirmed from blind reads (K212's E,E and K250's U,U via strip alignment); 2 sites (K075 F,F; K103 AE,AE) re-located and re-read **unblinded**; K015 O,O and K196 D,D confirmed at zoom / template |
| F3 | 40 sampled near-doublets (distinct look-alike pairs) | 80 | 0 | [0, 4.51 %] | no hidden doublet in the sample (206 such pairs exist) |
| F4 | 40 random decoy pairs | 80 | 0 | — | blinds F2/F3 |
| F1 ∪ F4 | uniform positions | 146 | 0 | [0, 2.49 %] | secondary estimate |

**Power (reader positive control, Q1).** 31 solved-page glyphs (73.jpg, labels confirmed by decryption)
read through the identical crop glue: **31/31** (accuracy CP 95 % lower bound 0.888). On canon items the blind
reader agreed with the crop's canon glyph 381/391 (97.4 %). All 10 disagreements were inside the look-alike
families: A↔AE ×4, O↔A ×3, D→M ×2, TH→W ×1. Every one resolved to canon at zoom, or via M/D class-mean template
correlation (`md_template.py`: line 455 boxes 5/6 = M 0.954 / D 0.969). Detection model: a true canon
error surfaces as a blind mismatch unless the reader makes the *same* wrong call as canon. Within the
look-alike families (O/A/AE, M/D, TH/W) that miss rate is ~7 % (10 of the 146 blind family glyphs), and
elsewhere it is ~0 (0 misses in 245 other glyphs). So the instrument would have caught roughly ≥ 90 % of real errors in the read set.

**Gate history (honest).** The Q5 gate first read 4/24. Cause: the control label map was broken by
73.jpg's drop-cap rune (A2), not reader failure. 13 controls from 74.jpg could not be aligned and were
dropped. 20 extra controls (A3) were added and read blind; pooled result 31/31.

## The three conditionals (Q4)

1. **Read set (the "key space").** F1/F4 uniform sample (146 glyphs, 1.1 % of 12,956), F2 full doublet
   census, F3 sample of 40/206 near-doublets. **Not covered:** the 149 RAT-unaligned positions; the
   ~12,560 positions outside the read set; the 180 solved-page runes (canon segments 55/56) are outside the U stream.
2. **Location model (the "transition model").** Exact segmenter boxes registered by page-constrained DP,
   window strips registered by their own blind reads (A5). An error that is simultaneously a segmentation
   merge/split and a label error is visible only in window items (38 strips).
3. **Reader (the "register").** One vision reader on the relikd 2400×3600 JPEG renders (sha256-pinned,
   same lineage as every other read). Branch-angle calls (ᚩ/ᚪ/ᚫ) and M/D are within resolution only at zoom.
   The reference chart is aggregate class means and exemplars from canon-labelled data, which is a soft
   dependence on canon's partition (itself established label-free in `analysis/independent-read/`).

## Answers to the brief

- **Positions:** RAT list not available (0 disagreements on record; 149 unaligned, unlocatable). Substitute
  read set **398 canon glyphs + 31 controls**, all adjudicated (0 pending, 0 ambiguous).
- **Canon error rate:** 0/66 primary, CI [0, 5.4 %]; 0/146 uniform, CI [0, 2.5 %].
- **Corrections:** none.
- **Doublets / T7:** all 86 sites confirmed. T7's input is unchanged at glyph level.
- **Solved-page boundaries / PROBLEM.json hash:** untouched / unchanged.

## What reopens this

- A committed (pinned) copy of RAT's per-position output → adjudicate the 149 unaligned positions with
  this same glue (`build_set.py` can take an explicit position list).
- Repair `alignment.json` (page-break crossings at 35/36 and 38/39; short-line drop shift) and rebuild
  `analysis/stones/dataset.npz`, then re-run `analysis/independent-read/` on corrected labels.
- Any read of a look-alike-family position at higher resolution than the relikd render (e.g. the crisp masters).

## Files

Scripts: `build_set.py` (sample, seal, render), `extra_controls.py`, `relabel_controls.py`,
`gate_controls.py`, `correct_map.py` (page-constrained registration), `strip_registration.py`,
`render_unloc.py`, `reinspect_render.py`, `md_template.py`, `adjudicate.py`, `stats.py`, `ref_zoom.py`,
`ref_exemplars.py`. Superseded, kept for the record: `audit_alignment.py` / `alignment_audit.json`
(crude shift test) and `locate_unloc.py` (wrong row-band heuristic).
Data: `blind_reads.json` (frozen, sha256 `7b76c643…dfe62e`), `extra_controls_reads.json`,
`sealed_manifest.json`, `items_blind.json`, `controls_relabel.json`, `corrected_map.json`,
`strip_registration.json`, `reinspect.json`, **`adjudications.json`**, `stats.json`, logs.
**`crops/` (rendered PNGs) should be gitignored**; it is regenerated by `build_set.py`,
`extra_controls.py`, `render_unloc.py`, `reinspect_render.py`, `ref_zoom.py` and `ref_exemplars.py`.

Reproduce (from `liber-primus/`, ~2 min per segmentation pass):
`PYTHONUTF8=1 python analysis/round45/S1-transcription/build_set.py && … extra_controls.py && … relabel_controls.py && … correct_map.py && … strip_registration.py && … adjudicate.py && … stats.py`
(blind reads are human/agent input, not regenerated).

---
CLOSING STAMP — R45/S1 closed 2026-11-23. 398/398 canon glyphs + 31 controls adjudicated; 0 canon errors;
0 corrections proposed; 1 instrument defect reported (`analysis/stones/alignment.json` line registration).
