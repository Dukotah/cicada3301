# R45 / S1b — Hidden-doublet audit of T7's fragile intervals: PREREG

_Dated 2026-11-23, written before any output file of this lane (other than an empty `crops/`).
Doctrine binds (`ARMADA-DOCTRINE.md`). Writes only inside `analysis/round45/S1b-hidden-doublets/`;
no commits; no edits elsewhere. Corrections are PROPOSED, never applied._

## 0. Disclosed before writing (feasibility probe; no canon rune value in the target intervals was printed)

- **Indexing.** T1 (`T1-t7-mechanism/t1lib.py: load`, `fragility.py`) works on the pair axis
  t = 0..12,954 of the 12,956-rune unsolved stream (krisyotam canon, segments 0–54); an event at t means
  x[t] == x[t+1]. Same 0-based stream as `analysis/stones/pipeline.py: global_lines()` concatenated
  (S1 verified sha `023312066df4…3af1585`). `fragility.json` sampled insertions every 5 pairs, so its
  breaker intervals ([1565,1620], [3040,3270], [3635,4035], [9570,9625] in runs) are ±5 approximate.
- **Target set (all pairs, padded).** Pairs t in [1560,1625] ∪ [3035,4040] ∪ [9565,9630] — 1,140 pairs.
  The brief's "~3040–4035" is taken whole (including 3270–3635, which E0b did not mark as a breaker),
  i.e. **every** adjacent pair whose 2 runes lie on canon global lines 73–76, 140–187, 440–443
  (56 lines, ≈1,215 glyphs, images p6, p12–p17, p39). Pairs spanning a line break are included.
- **Location.** Line registration uses S1's page-constrained `S1-transcription/corrected_map.json`, NOT
  `analysis/stones/alignment.json` (S1 A4: it false-exacts lines 76, 171, 173 — all in this target set).
  Probe: 50 target lines register with segment count == canon length; lines 74, 152, 168, 176, 183 have
  segment count = canon − 1; lines 166/167 (8 and 9 glyphs, page 14 end / page 15 start) are not in
  the ≥10-segment `clean` set and are located by their own short segmented line.

## 1. Hypothesis

H1: at least one adjacent pair in the target intervals that canon records as two different runes is, in
the image, the same rune twice (a **hidden doublet**), or a glyph is dropped/duplicated in canon such
that the corrected stream has an extra equal adjacent pair there. H0: none, with the miss-rate bounded
by the planted controls.

**What counts.** A hidden doublet is recorded only after unblinded high-zoom re-inspection judges, at
high confidence, both glyphs to be the same Gematria Primus rune while canon differs. A count error is a
glyph present in the image and absent in canon (or vice versa), confirmed on the full-resolution strip.
Ambiguous cases are listed and an upper-bound T7 is computed treating each as real.

## 2. Instrument (two passes, both blind)

- **Pass L (line reads, full coverage).** For every target line, a montage of the unfaded line strip,
  split in halves, with each segmented box numbered, is rendered under an opaque id (`Lxx`). The reader
  (this agent's vision) transcribes each line left→right, including any glyph the segmenter missed
  (marked `+`), and flags every adjacent pair it sees as the same rune. 8 **control lines** (outside the
  intervals, registered exact, containing known doublets confirmed by S1's census) are shuffled in.
  Canon for all lines is sealed in `sealed_lines.json`, opened only after `reads_L.json` is written and
  its sha256 recorded by `adjudicate.py`. Comparison: difflib alignment of read vs canon line; every
  mismatch, insertion or deletion, and every read-equal adjacent pair that canon has unequal, goes to
  unblinded zoom.
- **Pass P (pair deck, same/different).** Shuffled deck of 2-glyph crops (S1's `crop_box`, H=170, faded
  neighbours), opaque ids `Pxxx`, reader records SAME/DIFF + both reads + confidence:
  (a) **every** target pair whose canon runes are distinct members of one look-alike family
  {ᚩ,ᚪ,ᚫ}, {ᚦ,ᚹ}, {ᚱ,ᚹ}, {ᛗ,ᛞ}, {ᚾ,ᛁ}, {ᛒ,ᛖ} (S1 confusion list + S1 F3 families) on exact-registered
  lines; (b) **30 control true doublets** from outside the intervals (seed 45120); (c) **30 control
  look-alike non-doublets** from outside the intervals (seed 45120); (d) 20 random other target pairs
  as decoys. Sealed in `sealed_pairs.json`.

## 3. Control and power

- Pass P sensitivity = SAME calls on (b) / 30; specificity = DIFF calls on (c) / 30. Gate: sensitivity
  ≥ 27/30 (90 %) and specificity ≥ 27/30 → pass P informative. Below → P is reported, but the null rests on L.
- Pass L sensitivity: control-line doublets read as equal pairs / their count; plus agreement rate on
  target lines.
- **Miss bound.** A hidden doublet in a family pair is missed only if BOTH passes miss it; reported as
  the product of the two measured miss upper bounds (CP 95 %), and separately (conservatively) as the
  pass-P miss upper bound alone. For non-family pairs, the pass-L miss bound.

## 4. Outputs / pass-fail

If any hidden doublet or count error is confirmed: apply it to a copy of the stream, recompute T7 r with
`T1-t7-mechanism/t1lib.ac1` on the corrected events and p with `t1lib.addone_two` against T1's
`plants.json` null S1 (2,000 M0 draws; a corrected stream with ±1 rune changes T by ≤1, ignored).
**Verdict:** none found and pass-P gate passed → T7 **HARDENED** (with miss bound); found and p > 0.01 →
**DISSOLVED**; found and p ≤ 0.01 but r lower → **WEAKENED**.

## 5. Aiming Test

**Q1** — Hit = an adjacent pair the image shows as one rune twice where canon has two. Recognised by
pass P (planted true doublets in identical crops measure it) and pass L (control lines with doublets).
**Q2** — `T1-t7-mechanism/RESULTS.md` E0b: one extra doublet in ~740 positions, mostly these intervals,
takes T7 to p ≈ 0.1; S1 measured canon look-alike family confusions (A↔AE, O↔A, D↔M, TH↔W) as the only
reader-disagreement locus. A bounded finite-object audit (R5 #1).
**Q3** — Enumerable: 1,140 pairs, all read (census, not sample).
**Q4** — (1) read set: the 1,140 pairs, nothing else in the stream; (2) location model: corrected_map
registration + segmenter boxes, with pass L catching segmenter misses on the strip; (3) reader: one vision
reader on the sha-pinned relikd 2400×3600 JPEGs, power measured by §3 controls.
**Q5** — Kill: if after the first pass-P batch containing ≥10 controls accuracy < 70 %, pass P stops and is
reported uninformative; the lane falls back to L only and says so.

## 6. Deliverables
`build.py`, `adjudicate.py`, `t7_recompute.py` (if needed), `reads_L.json`, `reads_P.json`,
`adjudications.json`, `RESULTS.md`, `ledger_rows.json` (ids `R45-S1B-…`). `crops/` gitignored-worthy.

---
## Addendum B1 (2026-11-23, after viewing the first line montage L00, before any read was recorded)
Line strips were too small to separate branch shapes. Rendering only: strips upscaled ×1.8 (`SC` in
`build.py`). Selection, seed and sealed files unchanged (sealed_lines sha `c106a958…`, sealed_pairs sha `1784c79d…`).

## Addendum B2 (2026-11-24, after reads were frozen — `reads_frozen.sha256` — and at adjudication)
The session was interrupted after all 64 line reads and 97 pair reads were done but before they were written;
they were written verbatim from the reading notes before either sealed file was opened (hashes in
`reads_frozen.sha256`, re-checked by `adjudicate.py`). Disclosed limitation: at strip resolution the pass-L reader
could not separate M/D or TH/W (recorded as undecided `M|D`, `TH|W`) and called canon A as O 11 times. The
PREREG's "unblinded zoom" step for look-alike candidates is therefore implemented as an objective template
instrument (`template.py`): nearest class-mean (templates built only from canon-labelled glyphs on corrected-map
exact lines OUTSIDE the 56 target lines) plus direct glyph–glyph correlation. It never uses the canon label at
the position it classifies. Its accuracy is measured on every TH/W, M/D, A/AE/O glyph on the target lines and is
reported. Count discrepancies are adjudicated by ink-component listing + small zoom crops (`zoom*.py`).
