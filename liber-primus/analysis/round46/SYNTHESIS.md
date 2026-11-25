# Round 46 — SYNTHESIS: repair the word instruments, test the two leads

_Coordinator closeout, 2026-11-24. Lanes: L1, P1, A1, S2, X1. Plan of record: `CAMPAIGN-PLAN.md`. Every lane
pre-registered (PREREG sha256 stamped in its log before its first output), planted its own control, and closed
with a stamp. X1 audited all four and ruled each UPHELD-WITH-CORRECTIONS. Its corrections are applied in the lane
files (each `RESULTS.md` ends with an "X1 corrections applied" note) and in the ledger rows. Verdict on the
cipher: **OTP-class, UNCHANGED.** No key-space sweep was run. The only decodes were re-runs of rows that
already existed, through the repaired loader._

## 1. What Round 46 established

1. **There is now one correct printed-word loader** (L1, X1-upheld). `L1-word-loader/words.py` gives **2,896 LP2
   words**. The stream sha matches PROBLEM.json, the 10/10 tests pass, and *A WARNING* and *PARABLE* decode word
   by word. It joins 420 wrapping words (388 across a line, 32 across a page). The legacy loaders only **added**
   cuts and never missed a boundary: R41's camp7 had +420, and R37–R39 `mapcommon` / SKELETON had +32. X1
   reproduced this with independent code.
2. **The ten R45-reopened rows are re-measured** (L1 §5, X1 corrections applied). Plants on LP2's real layout
   were run under (a) true spaces in order, (b) plaintext words shuffled within sentence, and (b′) printed
   lengths permuted within sentence.
   - **R41-C1-R14 (word-sum self-key)** was re-run through words.py and is **negative** (W p 0.249/0.262,
     P 0.858/0.781, α 0.0025). Power is 1.00 under (a) and (b): 1760/1760 pages, 32/32 streams.
     - The old loader's page power, by R41's own score-only rule, was **≈ 0.64**, and about 0 for W2/W3
       (R46-X1-R41-LEGACY-SCORE-POWER).
     - So the original negative was **weakened, not blind**. L1's "legacy 0.001" figure needs an
       exact-recovery conjunct that R41 never used.
   - **C-01 SKELETON** was re-run and is at chance (best 20.2 %; a true hit is near 100 %).
     - Power under (a) is 1.00. The legacy loader had 0.25–0.50, so the old negative was weakened even with
       true spaces.
     - Under (b) it is 0, so the row stays **CONDITIONAL** on in-order spaces.
     - The verdict rests on the distance from the planted-hit level, not on the weak shuffled null (X1).
   - **R37-U2 (U2b) and R37-U3 hold** under (a) and (b). The 928 rho3 re-decodes on the mid-word pages 1–2 have
     a best of 4.35, below every bar.
   - **R38-WORDNET, R38-FREQRANK and R39-SENSE: their real decodes are identical**, so the real results hold.
     Power for each row's own lexicon glue is **not measured**. L1 had written "1.00 inherited"; X1 corrected
     this.
   - **R44-7GRAM holds** under (a) and (b).
   - **R38-C2-G3 was not re-run** and stays CONDITIONAL on the fragment convention. 32 of the 55 pages open
     mid-word.
   - **R40-R31 is not word-indexed.** The reopen conditional does not apply to it, and it stays INCONCLUSIVE.
   - **Under (b′), every word-indexed row falls to ≤ 0.033** (7-gram 0.033, all others 0). Which of (b) or (b′)
     describes LP2 is R45-W1's open question, and this round does not settle it.
3. **The 2-rune-word deficit replicates across the whole text** (P1 T2, X1-upheld). Both halves and both sets of
   `$`-sections sit at 15.3–15.6 % (each part p ≤ 0.0006, power ≥ 0.995). The text is homogeneous: section
   G p = 0.80 at power 0.98.
   - **Whether this is extreme for English is not settled.** T1, the fresh-English test, is **uninformative**
     by its registered rule: size 0.033 > 0.03. One fresh register, Milton's *Paradise Lost*, reaches 16.06 %.
   - Lead (i) is therefore "real and whole-text, but register-dependent". It is **not** shown to be "not an
     artefact of R45's corpus choice" (X1 withdrew that wording).
   - T3 rejects Latin, German and Welsh under the §2 fold. **Old English is not distinguishable** from fresh
     English by the registered rule (OE→EN-FE 1.00). Its rejection reflects a narrow single-text (Beowulf) bar.
   - The "not the solved pages' profile" result is weak, because that bar also rejects 67 % of fresh English.
   - "Fewer articles", "another English register" and "missing separators" all survive, and T3 cannot tell them
     apart.
4. **The line-break lead (ii) can't be confirmed.** Every registered discriminator is uninformative
   (power 0.17–0.62), limited by LP1's 126 running lines.
   - The full-data contrast (LP2 boundary preference π = 0.062 vs LP1 0.22, p = 0.005) is **descriptive only**.
     It is unregistered and computed on the R45-X1 discovery data, so it carries no confirmatory weight.
   - LP1 shows a strong word-aware-wrapping signature (U2 p = 0.0003). LP2's is weak and not significant.
5. **`analysis/stones/alignment.json` is repaired** (A1, X1-verified line by line).
   - **25 entries changed**: 24 by R-a1 and 1 by R-a3, the new line-553 defect. 4 R-a2 rows and the R-a5 row
     were flagged but left unchanged. 10 dead tail entries were dropped.
   - v1 is kept as `alignment.v1.json`.
   - The repair adds 372 labels and re-lines 89. **All 86 Campaign-V classifier-vs-canon disagreements were the
     map's fault.** OOF agreement is now 10,774/10,774, and 351/351 on the newly labelled glyphs.
   - The R45 S1 scripts are repointed to `alignment.v1.json`, so R45 S1 still reproduces.
6. **The "450 O/A/AE disagreements" are a KMeans basin artefact** (A1, sharpened by X1's
   `x1_oae_basins.json`).
   - Both label sets reach both basins: v1 gives 450 and v2 gives 670 by default. PCA seed is irrelevant.
   - **258 of the 450 sit in a 282-glyph stable core.** That core is a clustering property, not a canon-error
     signal.
   - The doctrine R5 example is amended to match.
7. **The transcription holds on the look-alike classes under a second blind reader** (S2, X1-upheld with
   corrections).
   - S2 = canon on 279/279 glyphs: the 179 S1 family glyphs on exact lines plus 100 fresh uniform glyphs.
   - **κ = 0.969** against S1. All 5 disagreements are S1 misreads.
   - Two-reader canon error bound, pooled over five families: **≤ 2.1 %**. Per family it is **O/A/AE ≤ 5.2 %**
     and **M/D ≤ 14.8 %**. With the W control alone the pooled bound is 2.26 %.
   - **The single-reader caveat is closed only for the 179 re-read glyphs.** 4 of S1's 10 canon-resolved
     mismatches (gpos **276, 5054, 6054, 9877**) lie outside S2's frame A. They still rest on S1's unblinded
     adjudication, along with the other S1 window-item family glyphs (27 in all).
   - The canon conclusion does not depend on S2's blinding: the leave-line-out template equals canon at all 279.
     The κ does depend on it.
8. **Fable52 runs from in-repo data** (A1). Every residual against `OUTPUTS.txt` traces to an input: 2
   separators (`-` vs `.` at runes 1886 and 9648) and 5 grid-cell case differences between lineages. No Fable52
   conclusion changes.
   - **The PREREG-addendum stamp rule is now executable** (`A1-hygiene/check_prereg_stamps.py`). It proves the
     history is append-only, **not** that stamps came before the outputs.
   - S2's Addendum S2-A was stamped after the fact by the coordinator, in `S2-second-reader/build_log.txt`.

## 2. Defects found

- **L1's R41 legacy-power figure** (0.001) used an exact-recovery conjunct that R41 never used. By R41's own rule
  the figure is 0.64 (X1 §5.3). Corrected in RESULTS, in the ledger rows, and in the R41 row note.
- **"1.00 inherited" power** for the three rho1 lexicon rows was not a measurement (X1 §5.4). They now read "not
  measured".
- **P1's plain-language summary** overclaimed: "not an artefact of R45's corpus choice", and Old English
  "separable". The lead-(ii) plants also bypass the lane's own `struct()/summ()` parser (X1 §1.5c). This changes
  no verdict, but the power is measured on the layout model.
- **A1's change count**: 29 → 25 + 4 flagged.
- **The S2 ledger control count**: 32 → 24. The C control is not blind in principle.
- **R45 S1 scripts break on alignment v2.** Fixed by repointing them to `alignment.v1.json`.
- Still open (carried forward):
  - `dataset.npz` has not been rebuilt with the v2 map (`python analysis/stones/build_dataset.py`).
  - Which transcription lineage is canonical for the 2 separators and 5 grid cells.
  - The stamp checker is not yet wired into CI.

## 3. Leads (status after this round)

- **2-rune deficit (lead i):** replicated and homogeneous across held-out parts. Its extremity for English is
  register-dependent. This is **not** a key lead.
  - It cannot be tested further post hoc. In particular, a re-run that decides after the fact how to treat
    Paradise Lost-style outliers is **not allowed**.
  - The next step is more reference data, not more analysis of LP2: Greek, Hebrew and Norse corpora (not on
    disk), and more archaic English verse registers. Any re-test must fix its outlier handling in the PREREG
    before the new corpora are read.
- **Line breaks inside words (lead ii):** descriptive only. It needs more LP1-like word-aware data (solved Cicada
  pages, or comparable typeset documents) before any held-out test has power.
- **T7:** unchanged from R45. It is hardened but unexplained, and this round has no new evidence on it.

## 4. Round 47 plan

CONTINUE, narrow. No key-space sweep.

1. **Close the transcription caveat completely.** Run a blind re-read (S2 protocol) of S1's 4 remaining disputed
   positions (gpos 276, 5054, 6054, 9877) and the 27 window-line family glyphs.
2. **Re-run R38-C2-G3** through `words.py`, with plants on the mid-word pages 1, 2, 4 and 5. The fragment
   convention must be stated in the PREREG. Also plant the lexicon glue of R38-WORDNET, R38-FREQRANK and
   R39-SENSE, so their (a)/(b) power is measured rather than assumed.
3. **Collect reference corpora** for lead (i): Greek, Hebrew, Norse and more archaic English verse. Then
   pre-register a held-out test with fixed outlier handling.
4. **Line-break test (lead ii):** gather more LP1-like data. Re-plant through `struct()/summ()` so power is
   measured on the pipeline.
5. **Hygiene.**
   - Rebuild `stones/dataset.npz` from the v2 map.
   - Decide which lineage is canonical for the 2 separators and 5 grid cells.
   - Wire `check_prereg_stamps.py` into CI, with a chronology check against log timestamps.
   - Add a consensus-clustering check before any O/A/AE candidate list is used again.
6. **L1 carry-overs** (not covered this round):
   - book-scope shuffles;
   - whole-stream (no per-page reset) word schedules;
   - assigning a page-wrap word to the page it *ends* on;
   - SKELETON beyond the resident corpus.

## 5. Ledger

`LEDGER.json` **384 → 400** (L1 5, P1 3, A1 4, S2 2, X1 2). The ten R45-reopened rows each carry a dated R46 note
with L1's corrected verdict. In R45's pattern, **statuses are left as recorded**. R45-S1-STONES-ALIGNMENT-DEFECT,
R45-S1-CANON-ERROR-RATE and R45-X1-R41-LINEWRAP-SEGMENTATION also carry R46 notes.
