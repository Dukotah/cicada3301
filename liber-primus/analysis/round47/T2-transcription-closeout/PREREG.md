# R47 / T2 — Transcription close-out: blind read of S1's 27 window-line family glyphs: PREREG

_Dated 2026-11-24, written before `build.py` exists and before any read. Doctrine binds (`ARMADA-DOCTRINE.md`).
Writes only inside `analysis/round47/T2-transcription-closeout/` (crops in `crops/`, gitignored); no commits; no edit
to `LEDGER.json` or any other file. Corrections are PROPOSED (flagged-for-oracle), never applied._

## 0. What this lane closes, and what was read before writing it

R46-S2 closed the X1 single-reader caveat for S1's 179 exact-line look-alike-family glyphs. Still open
(`round46/X1-redteam/AUDIT.md` §3.4, `round46/S2-second-reader/RESULTS.md` "X1 corrections"): S1's **27 family
glyphs on window (non-exact) lines**, which contain **4 of S1's 10 canon-resolved mismatches — gpos 276, 5054,
6054, 9877** — still resting on S1's unblinded adjudication. This lane is a third reader (a different agent from
S1, S1b and S2), blind, using S2's protocol and crop glue, with a sealed substitution control.

Read before writing: the doctrine, `round47/CAMPAIGN-PLAN.md`, S2 `PREREG.md`/`RESULTS.md`/`build.py`/
`template_call.py`/`unseal.py`/`save_batch.py`/`zoom.py`, X1 R46 audit (S2 section), S1 `RESULTS.md`,
A1 `RESULTS.md` §(a) (alignment repair). **Not opened, and not to be opened until every T2 batch is saved:**
any S1 per-position file (`blind_reads`, `adjudications`, `sealed_manifest`, `items_blind`, `reinspect`,
`strip_registration`, `extra_controls_*`), any S2 `reads_*`/`sealed.json`/`results.json`/`template_calls.json`,
and this lane's own `sealed.json`. `sealed.json` is not loaded by any script, inline or saved, before the last
batch is frozen (S2's disclosed inline-helper leak is the thing being avoided; the gate check in §7 Q5 is
computed by `unseal.py`-style code only after all batches, see §4).

**Prior knowledge (disclosed leak).** From documents I was required to read, I already know the *family pairs*
of the 4 disputed positions — 276 A/AE, 5054 TH/W, 6054 AE/A, 9877 D/M — and S1's aggregate "D→M ×2, TH→W ×1"
(so plausibly canon D at 9877, TH at 5054). Mitigation: strips are shown under opaque ids, shuffled with
controls, and the target glyph's place inside a strip is never shown; the canon verdict is additionally checked by
a machine template (§5) that does not depend on the reader.

**Sizing probe (disclosed).** `probe.py` (kept in this folder) was run once before this PREREG. It printed no
canon rune: only that S1's replayed set has 394 glyphs, 206 family, **27 off exact lines**, all 4 disputed gpos among
them, and per target the gpos, canon line, line offset, image / clean-line index and box count vs canon length.
The 27 sit on **16 canon lines** (12, 41, 74, 232, 234, 265, 277, 284, 291, 299, 327, 445, 455, 509, 519); each line
has 1–2 fewer segmented boxes than canon glyphs (merges/drops), which is why they are "window" items.

## 1. Hypothesis

H1: canon has a glyph error at ≥ 1 of the 27 window-line family positions (in particular at one of the 4 disputed
positions), detectable by a blind reader plus a machine template. H0: none; canon is confirmed there, and the
two-reader family bound extends to all 206 of S1's family glyphs.

## 2. Instrument and registration

- **Renders:** sha-pinned relikd `data/relikd/p*.jpg` (pins `analysis/round19/C3/l3/hashes.json`, re-checked).
- **Line registration:** the **repaired `analysis/stones/alignment.json` (v2, R46-A1)**: image n, clean (≥ 10-box)
  line i → canon global line. Cross-checked against S1 `corrected_map.json`; the probe found they agree on 15/16
  target lines; line 291 is `null` in `corrected_map` and v2 keeps v1's image 26 / clean line 4 (A1 rule R-a2).
  `build.py` asserts and logs this.
- **Within-line registration (the window problem):** boxes do not correspond 1:1 to canon glyphs on these lines, so
  no single box is shown as "the" target. Instead each target line yields a **strip**: the contiguous image region
  spanning boxes `[floor(j·c/L) − 3, ceil(j·c/L) + 3]` (union over the line's targets; c = box count, L = canon
  length, clipped to the line), cut with S2's `crop_box` glue (pad 10, H = 200 px, horizontal context outside the
  strip faded to 18 %). The reader reads **every glyph in the strip, left to right**, not knowing which is the target.
  After all batches are frozen, the read token sequence is aligned to the full canon line by semi-global edit
  distance (free end gaps on canon; substitution 1, within-family substitution 0.6, indel 1); the token aligned to the
  target position is the T2 read. The alignment cost and its margin over the second-best offset are reported. A target
  aligned to a gap, or with margin 0, is **unregistered** (counted as not-read, not as agreement).
- **Reference chart:** S2's `crops/reference_73.png` and `crops/ref_<T>.png` (exemplars from solved page 73,
  labels from the decrypted page, carrying no label of any target), viewed read-only. No other labelled material.

## 3. Sample (seeds fixed here; Python `random.Random`)

| frame | what | n | seed |
|---|---|---:|---|
| **T** targets | one strip per target line (16 strips) covering all 27 window-line family glyphs of S1's set (replay of 45013) | 16 strips / 27 targets | replay |
| **W** swap control | 8 strips of 7 boxes from exact-registered lines (S1 `corrected_map` exact, not containing any S1-set or target position), each with **one** box whose pixels are replaced by the box crop of a *donor* exact-line glyph of a **different** member of the same core family ({O,A,AE},{M,D},{TH,W}), resized to the recipient box. The recipient is at a random place in the strip. Sealed: canon sequence, swap index, donor canon. | 8 strips (8 swaps + 48 plain exact-line glyphs) | **47024** |
| **C** solved-page control | 4 strips of 6 consecutive boxes of solved `73.jpg` (labels = decrypted page, drop-cap offset 1 per S1 A2), start indices drawn uniformly | 4 strips / 24 glyphs | **47022** |

Strips are pooled and shuffled (seed **47023**) and dealt into batches of **≤ 25 boxes** (in practice ≤ 3 strips);
batch 1 carries ≥ 1 control strip. Each strip is one image file `crops/<id>.png` (ids `T2-sNN`, opaque).
`manifest.json` lists `strip id → batch, file, n_boxes` only. Frame, line, canon, swap status go to `sealed.json`.

## 4. Reading protocol

View only the strip images (≤ ~10 glyphs at 200 px), optional enlargement of a strip region via `zoom.py` (reads
only the strip png), and the S2 reference strips; never a full page. Each strip read: a token list in GP
transliteration (`F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA`), each with confidence H/M/L,
alternatives `A|AE` allowed (scored as non-match to canon, and as no-call for agreement), `?` for an illegible
glyph, edge glyphs cut by the strip border read if identifiable, else `?`. After each batch: `save_batch.py` writes
`reads_batchNN.json`, appends its sha256 to `reads_frozen.sha256`, rewrites `heartbeat.txt`. `unseal.py` refuses to
run unless all batch files exist and match the frozen hashes, and logs those hashes before it opens `sealed.json`
or any S1/S2 per-position file.

## 5. Adjudication (no unblinded eye calls)

For each target: T2 read (aligned), S1's frozen blind read (from `round45/S1-transcription/adjudications.json`, opened
only by `unseal.py`), canon, and a **template call**: when the strip's token count equals its box count (1:1), the
box aligned to the target gets S2's leave-line-out nearest-class-mean call (templates from exact-line glyphs, excluding
the target's own line); otherwise template = n/a. Verdicts (as S2 §5):
- `canon-confirmed (T2 blind)` — T2 = canon;
- **`canon-error-candidate`** — T2 ≠ canon and (T2 = S1 blind or T2 = template) → flagged-for-oracle, never applied;
- `canon-confirmed (T2 reader error)` — T2 ≠ canon, template = canon, and S1 blind ∈ {canon, none};
- `ambiguous` — anything else, including unregistered targets (counted as errors in the upper bound).
No verdict is made by re-looking at a glyph with canon known.

## 6. Statistics and pass/fail

- **Substitution gate (W):** swap caught iff the aligned T2 token at the swap ≠ claimed label (named iff = donor).
  Gate ≥ 6/8 caught; fewer → family claims uninformative.
- **Reader gate (C + plain W glyphs):** token accuracy ≥ 90 % on C (24 decryption-labelled glyphs) → informative;
  70–90 % → non-family only; < 70 % → uninformative. Plain W glyphs (canon-labelled exact-line) reported separately.
- **Per-target verdict** vs canon, with T2 / S1 / template, for all 27 (the 4 disputed listed first).
- **Two-reader bound, updated.** For each family F ∈ {OA, MD} (and pooled over all five):
  n_F = S1's family glyphs in F read by S1 and by one further blind reader (S2's 179 exact-line + T2's registered
  window targets); k_F = `canon-error-candidate` + `ambiguous` among them;
  ε_F ≤ CP95_upper(k_F, n_F) / (1 − m_S1 · max(m_S2, m_T2)), m = CP95 upper miss rate on family controls
  (m_S1 = 0.265 on 0/12, m_S2 = 0.143 on 0/24 as published; m_T2 on W swaps + C family glyphs). S2's per-glyph
  verdicts are taken from its committed `results.json`, opened only by `unseal.py`. Independence assumed and stated.
- H1 supported iff ≥ 1 `canon-error-candidate`. The caveat is called **closed for the 27** only if every target is
  registered and none is ambiguous or a candidate; otherwise the residual list is reported (R7: bounds, not verdicts).

## 7. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit is a window-line glyph whose image is a
different family member than canon says. The W frame plants exactly that shape — a real crop of rune Y under a label of
family-mate X, embedded at an unknown place in a strip — through the identical strip / read / align / unseal glue, so it
also tests the strip-alignment step the targets depend on.

**Q2 — What measured fact raises the prior?** Not a prior on canon errors (S1 0/398, S2 0/279 lower it). This closes a
named open caveat: X1 R46 §3.4 — 4 canon-resolved mismatches (276, 5054, 6054, 9877) rest on an unblinded adjudicator,
and S1's window-item miss rate is ≥ 4/27 (heterogeneous with its exact-line 2.8 %). Doctrine R5 #1 (finite object), R6.

**Q3 — Bounded?** Enumerable: 27 target glyphs on 16 strips (+ the strips' other glyphs as a by-product), 8 + 4 control
strips. Census of S1's off-exact family glyphs; nothing else in the 1,831 off-exact positions is covered.

**Q4 — The three conditionals.** (1) read set = S1's 27 window-line family glyphs (census) + strip neighbours; not covered:
the other off-exact positions, RAT's 149 unaligned positions. (2) location model = repaired `alignment.json` v2 for lines,
blind-read-to-canon edit-distance alignment within the line (a reader error adjacent to a segmentation defect could shift
registration — reported via margin). (3) reader = one further vision reader on the same relikd 2400×3600 renders (render
errors are invisible to all readers; readers share the render).

**Q5 — Kill condition at 10 % of budget.** If after batch 1 the build/strip pipeline shows strips that do not contain the
expected box count (visibly empty or misplaced strips), stop and fix glue (disclosed addendum). Control accuracy is not
inspected mid-run (no sealed access before all batches); if at unseal W < 6/8 or C < 70 %, the lane reports
uninformative.

## 8. Deliverables

`probe.py`, `build.py` (sample, seal, render; logs this PREREG's sha256), `manifest.json`, `sealed.json`, `zoom.py`,
`save_batch.py`, `reads_batchNN.json`, `reads_frozen.sha256`, `heartbeat.txt`, `unseal.py` (alignment, template,
adjudication, bounds), `unseal.log`, `results.json`, `RESULTS.md` (closing stamp), `ledger_rows.json` (ids `R47-T2-…`).

---
## Addendum T2-A (2026-11-24, written after unsealing; disclosure only, no threshold changed)

Pre-addendum sha256 of this file = `d9c40eb4…a3d8ddff` (full value in `build_log.txt`, logged by `build.py` before any read).
1. **Line count typo.** §0 says "16 canon lines"; the list it gives (and `build.py`) has **15**. 15 strips were built.
2. **Extra reference image.** `crops/refs_family.png` is a stack of R46/S2's own `ref_{O,A,AE,M,D,TH,W}.png` (solved page 73),
   built for viewing; no new labelled material.
3. **Post-hoc template run (`posthoc_md.py` → `posthoc_md.json`).** Run after unsealing, not pre-registered, descriptive only:
   the same leave-line-out template on every box of the two strips where T2 read M for a canon D (T2-s25, line 455; T2-s27,
   line 12). It changes no verdict; it is reported so the one `canon-error-candidate` (gpos 9877) can be read in context.
