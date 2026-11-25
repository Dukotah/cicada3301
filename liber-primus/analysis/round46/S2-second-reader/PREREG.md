# R46 / S2 — Second independent reader for the look-alike classes: PREREG

_Dated 2026-11-24, written before any other file in this lane. Doctrine binds (`ARMADA-DOCTRINE.md`).
Writes only inside `analysis/round46/S2-second-reader/`; no commits; no edit to `LEDGER.json`, the dataset,
or any other file. Corrections are PROPOSED (flagged-for-oracle), never applied._

## 0. What this lane closes, and what was read before writing it

`round45/X1-redteam/AUDIT.md` §3: S1's 0/146 bound holds for non-family glyphs, but for the look-alike
families (O/A/AE, M/D, TH/W) it rests on **one reader** whose 10/10 mismatches were resolved for canon by an
**unblinded** adjudicator; reader accuracy on the hard families has no independent measurement. This lane
is a second reader (a different agent from S1 and S1b), blind, with a family-rich positive control and a
substitution control, and with **no eye-based unblinded adjudication** (§5).

Read before writing: the doctrine, `round46/CAMPAIGN-PLAN.md`, S1 `PREREG.md`/`RESULTS.md` and code
(`build_set.py`, `correct_map.py`, `relabel_controls.py`, `extra_controls.py`), S1b `RESULTS.md` and
`template.py`, the X1 audit. **Not opened** (and not to be opened until every S2 batch is saved):
`round45/S1-transcription/{sealed_manifest,blind_reads,extra_controls_reads,adjudications,items_blind,
reinspect}.json`, `round45/S1b-hidden-doublets/{reads_*,sealed_*,adjudications,adjudicate_raw}.*`.
Aggregate counts in those RESULTS files were seen (S1: 0 canon errors; mismatch classes A↔AE, O↔A, D→M,
TH→W); no per-position read or canon value was. One count probe (no per-position output) was run to size
the sample: S1's read set replays to 394 distinct glyph positions, 206 in the look-alike union, 179 of them
on exact-registered lines; 11,125 / 12,956 stream positions are on exact-registered lines.

## 1. Hypothesis

H1: canon (`data/krisyotam_runes.txt`) has glyph-level errors in the look-alike families at a rate that a
second blind reader detects (any position where S2 ≠ canon and the independent evidence of §5 sides with S2).
H0: no such position; the canon family error rate is bounded by the two-reader bound of §6.
Secondary: S1's family reads are reproducible by an independent reader (inter-reader agreement and κ).

## 2. Instrument

Reader = this agent's vision reading of single-glyph crops from the sha-pinned relikd renders
(`data/relikd/p*.jpg`, pins `analysis/round19/C3/l3/hashes.json`, re-checked by `build.py`). Crop glue =
S1's `crop_box` (pad 10, neighbours faded to 18 %), height raised to 200 px. Location = S1's page-constrained
registration `round45/S1-transcription/corrected_map.json`; **only exact-registered lines** (segment count ==
canon count) are used, so every item is one segmented box ↔ one canon position, and no window/strip
alignment is needed. Reference chart = exemplars of each rune cut from the **solved** page `73.jpg`
(labels from the decrypted page, drop-cap offset 1 per S1 A2), boxes disjoint from the control boxes;
it carries no label of any target position.

## 3. Sample (all seeds fixed here; Python `random.Random`)

| frame | what | n | seed |
|---|---|---:|---|
| **A** S1 look-alike | every glyph of S1's read set (replayed from S1's seed 45013 code: F1 ∪ both glyphs of F2, F3, F4) whose canon rune is in the union {ᚩᚪᚫ}{ᛗᛞ}{ᚦᚹᚱ}{ᚾᛁ}{ᛒᛖ}, on an exact-registered line | 179 (expected) | replay of 45013 |
| **R** fresh random | uniform over exact-registered positions not in S1's read set | 100 | **46021** |
| **C** reader control | boxes of solved `73.jpg` (label = decrypted page), 16 drawn from look-alike runes + 8 from others | 24 | **46022** |
| **W** swap control | 8 positions with canon in {ᚩᚪᚫ}{ᛗᛞ}{ᚦᚹ} (not in A/R), each rendered with the crop of a *donor* position whose canon is a **different** member of the same family; the item's claimed label is the recipient's canon. Which items are swaps is sealed. | 8 | **46024** |

Frames are pooled, shuffled (seed **46023**), and dealt into **13 batches of ≤ 24** with C and W items dealt
round-robin so every batch carries controls (batch 1 carries ≥ 2 C). Crops are single glyphs; doublet
pairs are split into two independent singles (so a reader cannot see that a pair is a pair — stronger
blinding than S1's pair montages). Each batch is shown as 2 montages of ≤ 12 cells (~800×700 px).
`manifest.json` lists `crop id → batch, montage` only. Canon, frame, position and swap status go to
`sealed.json`, which is not printed or opened until all batches are saved.

**Known leak (disclosed):** frame A is selected by canon *family*; the reader is told only that the deck mixes
random glyphs with family-enriched ones, not which item is which.

## 4. Reading protocol (operational)

View only the batch montages and, if needed, a single-glyph zoom; never a full page. Each read: a GP
transliteration (`F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA`), confidence H/M/L, and
`?` alternatives allowed (e.g. `A|AE`, scored as no-call for agreement and as non-match for canon). After
each batch: write `reads_batchNN.json`, append its sha256 to `reads_frozen.sha256`, write `heartbeat.txt`
(timestamp, batch). `unseal.py` refuses to run unless all 13 batch files exist, and records their hashes
before opening `sealed.json` or any S1 file.

## 5. Adjudication (no unblinded eye calls)

For every item where S2 ≠ canon (or S2 no-call) the verdict uses only evidence fixed before unsealing:
(a) S1's frozen blind read of that position (if any), (b) a **template call** — nearest class mean
(correlation of `build_dataset.norm_crop` bitmaps) with templates from all exact-line glyphs **excluding the
item's own line**. Verdicts:
- `canon-confirmed` — template = canon and (S1 = canon or no S1 read);
- **`canon-error-candidate`** — S2 = S1 (independent blind) ≠ canon, or S2 = template ≠ canon → flagged for
  oracle (`HUMAN-ORACLE.md`), never auto-certified;
- `ambiguous` — anything else (listed; counted as errors in the upper bound).
No verdict is made by this agent re-looking at the glyph with canon known.

## 6. Statistics and pass/fail

- **Reader power gate (C):** accuracy ≥ 90 % (with family-rune C items reported separately) → informative;
  70–90 % → informative for non-family classes only; < 70 % → lane **uninformative**.
- **Substitution gate (W):** a swap is *caught* if S2 ≠ claimed label (and *named* if S2 = donor canon).
  Gate: ≥ 6/8 caught. Fewer → family-level claims are uninformative.
- **S2 vs S1** on frame A positions S1 read: raw agreement, Cohen's κ over runes (all of A, and per family
  with ≥ 15 items: OA, MD, THWR, NI, BE), no-calls excluded and counted.
- **S2 vs canon** on A ∪ R: mismatch list, per-class rate, exact Clopper–Pearson 95 %.
- **Two-reader canon error bound.** A canon error at a position escapes only if *both* readers make canon's
  wrong call. Per-reader miss rate m on the family classes is bounded by the CP upper bound of misses on
  family controls (S2: C-family ∪ W; S1: its published controls). Bound on the family canon error rate:
  ε ≤ CP95_upper(k_err, n) / (1 − m̂_S1·m̂_S2) for the n A-glyphs read by both, independence assumed and
  stated; also reported S2-only (÷ (1 − m̂_S2)).
- H1 supported iff ≥ 1 `canon-error-candidate`.

## 7. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit is a glyph whose image
is a different family member than canon says. The W frame plants exactly that shape — a real crop of rune Y
under a label of family-mate X — through the identical crop/montage/read/unseal glue, and the lane's gate
asks whether S2 flags it. C measures plain family accuracy on decryption-confirmed labels.

**Q2 — What measured fact raises the prior?** Not a prior on canon errors (S1 0/398, RAT 0/12,807 lower it):
this lane audits an *instrument* — the X1 finding (`round45/X1-redteam/AUDIT.md` §3) that S1's family bound
rests on one reader with circular, unblinded adjudication. T7 (`round44/SYNTHESIS.md`, S1b) is computed on
family-sensitive doublet sites, so the family bound is load-bearing. Doctrine R5 #1 / R6 audit.

**Q3 — Bounded?** Enumerable: 179 + 100 canon glyphs (2.2 % of 12,956) + 32 controls. The family-union
positions of S1's set on exact lines are a census of that set; the rest of the stream is not covered.

**Q4 — The three conditionals.** (1) read set = frame A (S1's family glyphs on exact lines) ∪ R (100 uniform);
not covered: 27 S1 family glyphs on non-exact lines, the 1,831 off-exact positions, all else. (2) location
model = S1's `corrected_map.json` exact lines only (a merge/split error is invisible). (3) reader = one
further vision reader on the same relikd 2400×3600 renders (an error baked into the render is invisible to
both readers; readers share the render, so their errors are not fully independent).

**Q5 — Kill condition at 10 % of budget.** After batch 1: if C+W accuracy in batch 1 is < 50 % (e.g. ≤ 1 of
≥ 3), check for a label-map defect (as S1 A2); if none, stop and report uninformative.

## 8. Deliverables

`build.py` (sample, seal, render; logs this PREREG's sha256), `manifest.json`, `sealed.json`,
`reads_batch01..13.json`, `reads_frozen.sha256`, `heartbeat.txt`, `unseal.py`, `template_call.py`,
`results.json`, `RESULTS.md` (closing stamp), `ledger_rows.json` (ids `R46-S2-…`). `crops/` is gitignored.

---
## Addendum S2-A (2026-11-24, written after unsealing; disclosure only, no threshold changed)

Pre-addendum sha256 of this file = the value logged in `build_log.txt` (`4f92cd4c…118bd3b`), recorded before
any read. Three things happened during reading that this PREREG did not specify, disclosed here:
1. **Reference strips.** Besides `reference_73.png`, same-glue reference strips per family rune were cut from
   solved `73.jpg` (non-control boxes; `crops/ref_<T>.png`) and shown beside some zoomed cells (`zoom.py --ref`).
   Labels are from the decrypted page, not any target position. The discriminators used were: O = both branch
   ends hooked, A = top hooked / bottom straight, AE = both straight; M = diagonals start at the stem tops,
   D = stems rise above the X; W = bump starts at the stem top, TH = stem rises above the bump.
2. **Helper read sealed.json into memory once.** The inline script that built those strips contained a stray
   `json.load(open("sealed.json"))` whose value was discarded (`and []`); nothing from it was printed or
   used. Control-box indices were recomputed from seed 46022, not read from the file.
3. **`zoom.py`** (blind cell enlarger, reads only `manifest.json` + montages) and **`gate.py`** (aggregate
   C/W count after batch 1, no per-item output) were added as glue.
