# R46 / S2 — Second independent reader for the look-alike classes: RESULTS

_2026-11-24. Pre-registration: `PREREG.md` (sha256 `4f92cd4c…118bd3b` logged in `build_log.txt` before any read;
Addendum S2-A is disclosure only). Nothing outside this folder was written. No correction is proposed._

## Headline

**A second, independent, blind reader finds 0 canon errors in 279 glyphs.** These are all 179 of S1's
look-alike-family glyphs that sit on exact-registered lines, plus 100 fresh uniform glyphs. Every read was
saved to disk before any label was opened.
**Two-reader canon error
bound on the family glyphs: ε ≤ 2.1 %** (95 %, pooled over five families; O/A/AE alone ≤ 5.2 %, M/D alone ≤ 14.8 %). The independent reader has fully
passed both positive controls: **24/24** solved-page controls (16/16 on family runes) and **8/8** swapped
look-alike crops, all caught and all named.

**S2 vs S1: 174/179 agree, Cohen's κ = 0.969.** All 5 disagreements are **S1 misreads**: S2's blind read,
canon and a leave-line-out template all agree at each one. This closes the X1 caveat (`round45/X1-redteam/AUDIT.md`
§3) for 6 of S1's 10 canon-resolved family mismatches; the other 4 (gpos 276, 5054, 6054, 9877) are outside frame A
and still rest on S1's unblinded adjudication. S1's canon-ward resolutions are now backed by
independent blind evidence, not by an unblinded reader who knew canon.

## Controls (power)

| control | what | result | CP 95 % |
|---|---|---|---|
| **C** reader | 24 boxes of solved `73.jpg` (labels from the decrypted page; drop-cap offset 1) | **24/24** | [0.858, 1] |
| C, family subset | AE 5, E 2, W 2, D 2, R, O, M, TH, N | **16/16** | [0.794, 1] |
| **W** substitution | 8 positions shown with a crop of a *different* family member, under the original label (sealed) | **8/8 caught, 8/8 named** | — |
| W detail | claimed→shown: D→M ×2, O→AE ×2, A→AE ×2, TH→W, AE→O | all read as the shown rune | |
| Q5 gate after batch 1 | C+W in batch 1 | 3/3 | |
| Template (adjudication) | leave-line-out class means, all exact-line family glyphs | OA 1186/1186 · MD 751/751 · THWR 1092/1092 · BE 756/756 · NI 471/787 ¹ | |

¹ I is a bare stem. Its normalised bitmap has zero variance, so the template cannot call it. It was not needed,
because there were no N/I mismatches.

Both pre-registered gates passed (C ≥ 90 %, W ≥ 6/8). **The W control is the planted hit (Q1).** A real crop
of rune Y, filed under label X from the same family, goes through the same crop, montage, read and unseal
steps, and S2 flags it every time.

## S2 vs canon

| frame | n | S2 ≠ canon | CP 95 % |
|---|---:|---:|---|
| A: S1 family glyphs (exact lines) | 179 | 0 | [0, 2.04 %] |
| … OA (O/A/AE) | 72 | 0 | [0, 4.99 %] |
| … THWR (TH/W/R) | 42 | 0 | [0, 8.41 %] |
| … MD (M/D) | 24 | 0 | [0, 14.3 %] |
| … NI (N/I) | 22 | 0 | [0, 15.4 %] |
| … BE (B/E) | 19 | 0 | [0, 17.7 %] |
| R: fresh uniform (seed 46021) | 100 | 0 | [0, 3.62 %] |
| A ∪ R | 279 | 0 | [0, 1.31 %] |

Every verdict is `canon-confirmed (S2 blind)`. There were 0 `canon-error-candidate` and 0 `ambiguous`
verdicts. No verdict needed an unblinded eye call.

## S2 vs S1 (inter-reader agreement on the 179 shared glyphs)

| family | n | agree | κ | S1 = canon | S2 = canon |
|---|---:|---:|---:|---:|---:|
| OA | 72 | 68 | 0.915 | 68 | 72 |
| MD | 24 | 23 | 0.916 | 23 | 24 |
| THWR | 42 | 42 | 1.000 | 42 | 42 |
| NI | 22 | 22 | 1.000 | 22 | 22 |
| BE | 19 | 19 | 1.000 | 19 | 19 |
| **all** | **179** | **174** | **0.969** | 174 | 179 |

The 5 disagreements (gpos: canon / S2 / S1 / template):

- 6159: O / O / A / O
- 4867: AE / AE / A / AE
- 4773: D / D / M / D
- 1724: A / A / O / A
- 4580: O / O / A / O

S1 also read glyph 6158 twice, once as A and once as AE (canon A). **S1's blind family miss rate is 5/179 =
2.8 %** (CP [0.9 %, 6.4 %]); in O/A/AE it is 4/72 = 5.6 % (CP [1.5 %, 13.6 %]). This replaces S1's circular
~7 % estimate for exact-line glyphs; S1's misses on its 27
window-item family glyphs are ≥ 4 (≈ 15 %), so S1's rate is not homogeneous. A likely cause: S1 read 170 px pair cells, and the O/A/AE call depends on whether a branch end
is hooked or straight. S2 read single glyphs at 200 px, next to solved-page reference strips.

## Two-reader canon error bound

A canon error at a position escapes only if **both** readers make canon's wrong call.

- Per-reader family miss rate m (CP 95 % upper, on family-labelled controls):
  - S2 = 0/24 → m₂ ≤ 0.143
  - S1 = 0/12 → m₁ ≤ 0.265
  - joint m₁·m₂ ≤ 0.038
- Family glyphs read by both readers: 0 errors in 179 → ε ≤ 2.04 % / (1 − 0.038) = **2.12 %**.
- S2 alone, over all 217 family glyphs in A ∪ R: ε ≤ 1.69 % / (1 − 0.143) = **1.97 %**.
- Uniform positions (R alone): ε ≤ **4.2 %**.

Read honestly, the bound is now **limited by sample size, not by reader reliability**. Adding the second reader
shrinks the miss correction from ×1.36 (S1 alone) to ×1.04. Going below about 2 % needs more glyphs, not more
readers.

**Independence caveat.** Both readers read the same relikd render, so their misses are not fully
independent. An error baked into the render would get past both of them.

## The three conditionals (Q4)

1. **Read set.** Frame A is a census of S1's family glyphs on exact-registered lines (179/206). Frame R is
   100 uniform exact-line positions outside S1's set. **Not covered:** 27 S1 family glyphs on window lines,
   1,831 off-exact positions, and everything else.
2. **Location model.** S1's page-constrained `corrected_map.json`, exact lines only, one box ↔ one canon
   position. An error that is both a merge/split and a mislabel cannot be seen.
3. **Reader.** One further vision reader (a different agent from S1 and S1b) on the sha-pinned relikd
   2400×3600 renders. The reference material is solved-page exemplars only. Doublet pairs were split into
   independent singles and shuffled, so the reader could not tell that two glyphs formed a pair.

## Blinding record

- `manifest.json` lists crop ids only. Labels, frames and swap status were kept in `sealed.json`.
- 13 batches of ≤ 24 reads each were saved and sha-frozen (`reads_frozen.sha256`), with `heartbeat.txt`
  written after each batch.
- `unseal.py` checks every batch hash before it opens `sealed.json` or any S1 file (`unseal.log`).
- S1/S1b read files were not opened until all 13 batches were frozen.
- Disclosed in PREREG Addendum S2-A: one helper script parsed `sealed.json` into memory once, discarded the
  value and printed nothing. The only exception to the blinding was the aggregate batch-1 gate count.
- Frame A was chosen by canon *family*. That is a mild, disclosed leak, mitigated because frame A was shuffled
  together with R, C and W.
- (R46-X1) The C control is not blind in principle: the reader recomputed the C box indices
  (seed 46022) and labelled reference strips from the same decrypted page 73. W is the clean control; with W alone
  (m₂ ≤ 0.369) the two-reader bound is 2.26 %. The sealed.json helper was inline and unsaved, so its "nothing printed"
  cannot be audited; the canon conclusion is independently supported by the leave-line-out template (= canon at all
  279), the inter-reader κ is not.

## Verdict

**NO-CANON-ERROR-FOUND at a two-reader bound of ε ≤ 2.1 %** on the look-alike families. The reader was shown
to catch planted look-alike substitutions (8/8). The X1 single-reader / circular-adjudication caveat is
**closed for the 179 exact-line family glyphs** and still open for S1's 27 window-item family glyphs, which include
4 of S1's 10 canon-resolved mismatches.

**What reopens this:**
- a higher-resolution master showing a different glyph at a read position;
- a third reader or the human oracle disagreeing with S2 at a family position;
- a read of the 27 window-item glyphs that disagrees with canon.

## Files

| kind | files |
|---|---|
| Scripts | `build.py` (sample, seal, render), `zoom.py` (blind cell enlarger), `save_batch.py`, `gate.py`, `template_call.py`, `unseal.py` |
| Data | `manifest.json`, `sealed.json`, `reads_batch01..13.json`, `reads_frozen.sha256`, `heartbeat.txt`, `build_log.txt`, `gate.log`, `template_calls.json`, **`results.json`**, `unseal.log`, `ledger_rows.json` |
| Ignored | `crops/` is gitignored (`.gitignore` here) and regenerated by `build.py` |

Reproduce from `liber-primus/`:

```
PYTHONUTF8=1 python analysis/round46/S2-second-reader/build.py && … template_call.py && … unseal.py
```

The reads are agent input and are not regenerated.

---
CLOSING STAMP — R46/S2 closed 2026-11-24. 311/311 crops read blind in 13 frozen batches. C 24/24, W 8/8.
S2 = canon 279/279. S2 vs S1 κ 0.969 (5 S1 misreads, 0 canon errors). Two-reader family bound ε ≤ 2.12 %.
0 corrections.

## X1 corrections applied

_Applied by the Round 46 coordinator from `../X1-redteam/AUDIT.md` (2026-11-24); PREREG untouched._ §3.5 items 1–7: the X1 caveat is closed only for the 179 re-read exact-line glyphs; 4 of S1's 10 canon-resolved mismatches (gpos 276, 5054, 6054, 9877) lie outside frame A and remain open; the pooled 2.1 % bound splits as O/A/AE ≤ 5.2 %, M/D ≤ 14.8 %; S1's ~2.8 % miss rate holds for exact-line glyphs only (≥ 4/27 on window items); the C control is not blind in principle (W-only bound 2.26 %); ledger control count 24, not 32. Addendum S2-A was stamped after the fact by the coordinator (sha256 `8a15e0dc…12e2d050`, appended to `build_log.txt`).
