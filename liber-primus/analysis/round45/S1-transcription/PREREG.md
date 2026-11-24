# R45 / S1 — Independent transcription audit: PREREG

_Dated 2026-11-23, written before any output file in this lane. Doctrine binds (`ARMADA-DOCTRINE.md`).
Lane writes only inside `analysis/round45/S1-transcription/`; no commits; no edits to LEDGER.json,
the dataset, or any existing file. Corrections are PROPOSED, never applied._

## 0. What was found before writing this (disclosed so the design is auditable)

1. **The RAT frame as briefed does not exist in committed data.** The only committed record of
   RiskAverseTech/cicada-ioc is two sentences in `analysis/transcription/TRANSCRIPTION-VERDICT.md`
   (2026-11-20 update): RAT re-read the unsolved images blind and **disagrees with canon at 0 of
   12,807 aligned glyphs (98.8 % of 12,956)**. The ~149 residue (12,956 − 12,807) is therefore
   **unaligned** — positions RAT did not produce an aligned read for — **not disagreements**. No
   per-position RAT list is in the repo, and no pinned fetch exists for it (`data/fetch_sources.py`
   pins only rtkd/iddqd PR #8 head `8ae822e6…`, which is the *same root lineage* as canon, not RAT).
   Per the brief ("don't fetch anything else") **RAT data is not fetched.** The 149 unaligned positions
   cannot be located from committed data and are reported as `not_covered`.
2. **Substitute frame (this lane's actual measurement).** The brief's purpose — measure the canon
   error rate on the shared input from the page images, blind, with special attention to the doublet
   sites T7 depends on — is executed directly on canon positions (§3).
3. **Images.** `data/relikd/p0..p55.jpg` all match the pinned SHA256s in
   `analysis/round19/C3/l3/hashes.json` (`target_renders`, 56/56, checked 2026-11-23). These are used.
   The external `…/Temp/lpx/…` clone is **not used**. Reader-accuracy control renders `73.jpg` / `74.jpg`
   (solved LP2 pages, canon segments 55/56) at
   `corpus/A-primary-artifacts/cijhho123/2014/Liber Primus/liber primus images full/` match their
   pinned SHA256s (`control_renders`).
4. **Stream pin reproduces.** Concatenating `analysis/stones/pipeline.py: global_lines()` (594 lines,
   pages 0–54) gives 12,956 indices, sha256 `023312066df4…3af1585` = `PROBLEM.json`.
5. **Feasibility probe (no files written, no canon value at any sampled position looked at):** the
   Campaign-V segmenter + `analysis/stones/alignment.json` box 10,774 positions exactly
   (segment count == canon count on the line); 2,025 positions sit on 92 lines whose segment count
   differs (mostly −1); 10 global lines are not aligned to an image line
   (77,166,174,363,399,420,432,553,578,593).

## 1. Hypothesis

H1: canon (`data/krisyotam_runes.txt`, the single rtkd-root transcription every public LP2 effort
uses) contains glyph-level errors at a rate ≥ 1 % on the unsolved stream, or at any of the 86 doublet
sites, such that an input correction would change the doublet count or the pinned stream hash.
H0: no canon error is found in the read set; the measured rate is bounded by the binomial CI.

## 2. Instrument

The reader is this agent's own vision reading of glyph crops rendered from the pinned page images
(PIL; `crops/` subfolder, gitignore-worthy). Reads are **blind**: montages carry only opaque item ids;
canon values for read items are written to `sealed_manifest.json`, which is not printed or opened
until `blind_reads.json` is written. `adjudicate.py` records the sha256 + mtime of `blind_reads.json`
before it opens the sealed manifest. A reference chart of the 29 Gematria Primus glyph forms in the
LP typeface (class-mean images from `analysis/stones/dataset.npz`, plus solved-page exemplars) may
be consulted while reading — it is an aggregate chart, not any position's label (conditional noted).

Location: exact-box items crop the segmented component(s). Items on count-mismatched or unaligned
lines are **window items**: a strip of ~7–9 glyphs around the proportional location; the reader
reads the whole strip left→right blind; the target's read is recovered afterwards by local
alignment (difflib) of the strip read to the canon line. Unaligned lines are located by row-band
detection (`analysis/transcription/linecrop.py: detect_rows` logic, re-implemented locally).

## 3. Read set (sampling plan; seed **45013**, Python `random.Random(45013)`)

| frame | what | n | role |
|---|---|---:|---|
| **F1** random singles | stratified by 11 page blocks (pages 0–4, 5–9, …, 50–54), 6 uniform positions per block | 66 glyphs | **primary** error-rate estimate (block-size weighted) |
| **F2** doublet sites | **every** adjacent equal pair in the 12,956 stream (expected 86), both glyphs | 172 glyphs | T7 input: does any site dissolve? |
| **F3** near-doublets | adjacent pairs whose canon runes are distinct members of one look-alike family {ᚩ,ᚪ,ᚫ}, {ᚱ,ᚹ}, {ᛗ,ᛞ}, {ᚾ,ᛁ}, {ᛒ,ᛖ} (families from `analysis/independent-read/FINDINGS.md`); 40 sampled | 80 glyphs | could a misread *create* a site? |
| **F4** random decoy pairs | 40 uniform adjacent pairs that are neither F2 nor F3 | 80 glyphs | blinds F2/F3 (reader cannot tell a doublet pair from a decoy) and adds uniform positions to the secondary estimate |
| **C** reader control | 24 glyphs sampled from the solved pages (73.jpg / 74.jpg; labels cryptographically confirmed by `tests/validate.py`) | 24 glyphs | positive control: measures reader accuracy |

F2/F3/F4 items are pairs rendered identically and shuffled together; C items are shuffled among the
singles. Sampling is done once by `build_set.py` with the seed above; the set is not redrawn.

## 4. Adjudication rule and what counts as a canon error

For each item: blind read vs canon. If equal → `canon-confirmed`. If unequal → unblinded high-zoom
re-inspection of that glyph against the reference chart and against the canon and read values, then
one verdict: `canon-confirmed (reader error)`, **`canon-error`** (glyph is, at high confidence, a
different Gematria Primus rune than canon, or canon has an inserted/omitted glyph there), or
`ambiguous` (cannot be decided from this render). Only `canon-error` counts as an error. Ambiguous
items are listed and an upper bound counting them as errors is also reported. Every read carries a
confidence H/M/L.

## 5. Statistics and pass/fail

- Canon error rate: primary = F1 (weighted by block size), exact Clopper–Pearson 95 % CI; secondary =
  F1 ∪ F4 (uniform-position glyphs, 146) unweighted CP 95 %. F2 and F3 reported as targeted counts.
- **Positive control gate:** reader accuracy on C ≥ 90 % → blind reads informative. 70–90 % → reads
  are informative only through the unblinded re-inspection step (stated). < 70 % → lane result is
  "uninformative" (not "negative").
- H1 supported if any `canon-error` is found, or the F1 CP lower bound exceeds 1 %.
- Report for every proposed correction whether it touches a doublet site (count changes 86 → ?), a
  solved-page boundary (segments 54/55), or the PROBLEM.json sha256 (any U-stream change does).

## 6. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit is a glyph whose
image is clearly another rune than canon says (or a missing/extra glyph). The instrument is a blind
read of that exact glyph; recognition is measured by the C control (solved-page glyphs whose labels
are cryptographically confirmed), i.e. the planted "known answer" is read through the identical
crop/montage glue. A canon error that looks like a different rune would surface as a blind-read
mismatch, which then goes to zoomed re-inspection.

**Q2 — What measured fact raises this family's prior above the flat rate?** (a) Every public LP2
effort, including FlareZ123, runs on one transcription (`analysis/round45/CAMPAIGN-PLAN.md` §0.1),
so an error there is a common-mode failure no cross-effort agreement can detect; (b) the
`ᚩ/ᚪ/ᚫ` family is the one locus where a label-free read diverges from canon
(`analysis/independent-read/FINDINGS.md` §3, 450 located disagreements); (c) T7's doublet
heterogeneity (`round44/SYNTHESIS.md`) is computed on 86 sites, so a handful of misreads is
leverage-heavy. Counter-evidence lowering the prior: RAT 0/12,807; three lineages identical;
solved pages decrypt. This is a bounded finite-object audit (R5 #1), not a completeness ritual,
because of (c).

**Q3 — Is the space bounded?** Yes, enumerable: 12,956 positions; this lane reads 66 + 172 + 80 +
80 = 398 canon glyphs (3.1 %) plus 24 controls; F2 is a **census** (100 % of doublet sites).

**Q4 — The three conditionals.** (1) *Key space* analogue = the read set: F1/F4 uniform sample,
F2 census, F3 sample; the 149 RAT-unaligned positions are not covered. (2) *Transition model*
analogue = the location model: exact boxes from the Campaign-V segmenter, window+alignment
elsewhere; an error that is simultaneously a segmentation error and a mislabel is visible only in
window items. (3) *Register* analogue = the reader: one vision reader on the relikd 2400×3600 JPEG
renders (same lineage as every other read), with measured accuracy on C; subtle branch-angle
calls (ᚩ/ᚪ/ᚫ) may exceed its resolution and fall to `ambiguous`.

**Q5 — Kill condition at 10 % of budget.** After the first montage of mixed items including ≥ 8
controls: if reader accuracy on those controls is < 70 %, stop blind reading and report the lane
uninformative (the reader cannot see what it would need to see).

## 7. Deliverables

`build_set.py` (sampling + sealed manifest + crops/montages), `adjudicate.py`, `blind_reads.json`,
`adjudications.json`, `RESULTS.md` (closing stamp), `ledger_rows.json` (ids `R45-S1-…`).
`crops/` holds rendered PNGs and should be gitignored (regenerated by `build_set.py`).

---
## Addendum A1 (2026-11-23, after viewing one montage, before any read was recorded or any canon value seen)

The first render (`single_00.png`, glyph height 100 px, pad 10, 24 per montage) was too small to
resolve branch angles, and neighbouring glyph edges inside the crop read as extra strokes. Rendering
changed only: glyph height 170 px, ink outside the target box faded to 18 % (window items unfaded),
12 singles / 8 pairs / 3 windows per montage. Sampling code and seed are untouched, so the read set
is identical (same ids K000…). Build outcome recorded: 86 doublet sites, 206 near-doublet pairs
(40 drawn), control pool 36 glyphs on exact-count solved-page lines (24 drawn), 3 items on
unaligned lines (to be located by row-band, blind).

## Addendum A2 (2026-11-23, after the Q5 gate first fired, before any non-control canon value was seen)

The Q5 gate (`gate_controls.py`, reads frozen at `blind_reads.json` sha256 `d860385f…f9f49e`) first
scored 4/24. Misses were high-confidence clean shapes (e.g. a textbook ᛟ labelled ᚪ), which is the
signature of a label-map defect, not reader failure. Cause, found from the image: `73.jpg` opens with a
drop-cap rune that the segmenter's height filter excludes, so image line 1 is one glyph short and
`build_set.py`'s equal-count line matching assigned later image lines to the wrong canon lines.
Fix (`relabel_controls.py`), fixed before re-scoring: whole-page reading-order alignment; usable only
if box count = canon count (offset 0) or canon − 1 (drop cap, offset 1). 73.jpg: 84 = 85 − 1 → usable;
74.jpg: 90 vs 95 → **dropped** (13 controls). The crops that were read are unchanged; only labels are
re-derived. Re-scored gate: **11/11**. Reads were not changed.

## Addendum A3 (same time)

11 controls give a weak accuracy bound, so 20 further controls are drawn from the remaining 73.jpg
boxes (seed 45014, `extra_controls.py`), rendered with the identical crop function, read blind
(labels sealed in `extra_controls_sealed.json`), and pooled with the 11. The ≥ 90 % gate applies to the pool.

## Addendum A4 (2026-11-23, after all blind reads were frozen — `blind_reads.json` sha256 `7b76c643…dfe62e` — and before the sealed manifest was opened for any non-control frame)

**Instrument defect found in the location glue (committed `analysis/stones/alignment.json`).** The 3
"unaligned" items sit on canon lines 399 and 432. Page images show 399 is the first text line of image 36
(segment count 23 = canon 23) and 432 the first line of image 39, but `alignment.json` assigns 399 to
image 35 and 432 to image 38 — the only two places where its line→image assignment crosses a canon `%`
page break. Consequence: on images 35/36 and 38/39 the positional `clean[i] ↔ alignment[i]` pairing used
by `analysis/stones/build_dataset.py` (and by this lane's `build_set.py`) is one line off near those
breaks, and wherever two adjacent canon lines share a length the crop is called "exact" but shows the
wrong canon line (false-exact). A short canon line (< 10 glyphs) dropped from `clean` causes the same
shift. Handling, fixed now: `correct_map.py` re-registers every image's segmented lines to the canon
lines of its own page by DP on counts (page-constrained; a first unconstrained version slid across page
breaks and is superseded). `adjudicate.py` scores each exact-box item against the canon rune actually in
its crop (`crop_canon`) and flags misregistered items; a misregistered window target is `not-read`.
The 3 unaligned items were rendered as exact-box pairs from the first line of images 36/39
(`render_unloc.py`) and read blind (K144, K181, K255). This defect also bears on the Campaign-V
classifier labels (`analysis/stones/dataset.npz`) — reported, not repaired here.

## Addendum A5 (2026-11-23, at adjudication)

The page-constrained DP (`correct_map.py`) is itself fallible: for image 11 it registers the strip of K250
to canon line 128, but the frozen blind strip read ("T I EO I C U U E C B AE EO") matches canon line 127
at ratio 0.80 vs 0.36. Window items are therefore registered by their own blind strip reads
(`strip_registration.py`: difflib fit against item line ±2; registered iff the item line is best, ratio
≥ 0.6, margin ≥ 0.15). 34/38 strips register to their item line; 4 (K072, K103, K225, K235) register to
an adjacent line, agreeing with the DP, i.e. their targets were not in the crop. Exact-box items keep the
DP registration (no exact-box item lies on image 11 lines 127/128). Not-read targets are re-located and
re-read UNBLINDED (`reinspect_render.py`, canon already printed) and labelled so.
