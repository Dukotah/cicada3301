# R46-X1 — Red-team audit of Round 46 (P1, A1, S2, L1)

_2026-11-24. Doctrine R6: verdicts are FOUND-ERROR / NO-ERROR-FOUND, never "confirmed". Rulings per lane:
UPHELD / UPHELD-WITH-CORRECTIONS / REJECTED. P1/A1/S2 audited first; L1 audited after its 21:25 closing stamp (§5)._

**Process note.** X1 wrote no PREREG this round. The new measurements (§2.3 `x1_oae_basins.py`; §5.3 re-score of L1 plants) are
descriptive. Its rule (stable core = mismatched in ≥ 90 % of runs) is fixed in the script docstring, and the
ledger row says `threshold_fixed_in_advance: false`. Every other number below is a recomputation of a lane's
own claim, done from raw data with independent code where that was cheap.

| lane | ruling | headline issue | severity |
|---|---|---|---|
| P1-leads | **UPHELD-WITH-CORRECTIONS** | the T1 "uninformative" call is correct. Plain-language §"What this means" #1 claims more than an uninformative primary allows. T3 says Old English is separable from English, but it fails the registered distinguishability rule. Lead-(ii) plants skip the lane's own parser | medium (wording), low (glue) |
| A1-hygiene | **UPHELD-WITH-CORRECTIONS** | the repair is verified line by line. "29 positional entries changed" is really 25 changed + 4 flagged. The O/A/AE instability holds and is sharper than A1 says: both label sets reach both basins, and 258/450 form a stable core | low |
| L1-word-loader | **UPHELD-WITH-CORRECTIONS** | loader and recounts are exact. "R41 was blind (legacy power 0.001)" comes from an exact-recovery conjunct R41 never used; by score alone legacy page power is 0.64 | medium |
| S2-second-reader | **UPHELD-WITH-CORRECTIONS** | κ and all bounds recompute exactly. But 4 of S1's 10 canon-resolved mismatches are **outside** S2's frame A, so "closes the X1 caveat" is too strong. The pooled 2.1 % bound hides OA ≤ 5.2 % and MD ≤ 14.8 %. The sealed.json helper leak can't be audited, though the canon conclusion doesn't depend on it | medium |

---

## 1. P1 — pre-registered tests of the two leads

### 1.1 Pre-registration: clean
- sha256(`PREREG.md`) = `fd9fa758…94425285`. That is the current file and also `run.log` line 1, stamped at
  15:46:47.
- PREREG mtime is 15:46:43. The first script (`p1lib.py`) is 15:47:27, and outputs start at 15:54.
- There are no addenda, and A1's checker gives base = VERIFIED.
- One disclosed design choice: lead-(ii) "stage 1" calibrates ρ on **full-LP2 π**, so stage 1 is not "before
  LP2 is read" for lead (ii). The PREREG specified this (§3 U1), so it is not a violation.

### 1.2 Recomputed independently
- **2-rune share 15.47 %: reproduced.** My parser is not w1lib. It takes the first 12,956 runes of
  `krisyotam_runes.txt` and breaks on `- . & $ §` and digits. Result: **2,896 words, 448 two-rune, 0.154696**,
  mean 4.474.
- **π (lead ii): reproduced exactly.** c = 0.77730, 532 running gaps, 388 inside, f_in = 0.72932,
  **π = 0.06173**, U1a binomial p = 0.005270.
- **U1b full-LP2 permutation.** My run (20,000 perms, own code) gives **p = 0.0057**, against the lane's 0.0051.
  The two agree within Monte Carlo error. A plain two-proportion z test on the raw boundary rates (52/126 vs
  144/532) gives p ≈ 0.0009, so the excess-indicator permutation is, if anything, conservative.
- **T1 per-corpus minimums and size vector: reproduced from `results.json`.**
  - `S1_per_corpus` is 0.00 for 29 corpora and 0.99 for *Paradise Lost*.
  - 0.99 / 30 = **0.0330**.

### 1.3 Specific ask — T1 "uninformative" at 0.033 vs 0.03: **the correct pre-registered call**
- PREREG §3 T1 and Q5(b) both say "mean over corpora must be ≤ 0.03, else T1 uninformative". 0.0330 > 0.03.
  No discretion applies.
- It is also not really a near miss. With 30 corpora, one fully outlying corpus alone contributes 0.033. So the
  bar in effect required that no fresh English text sits wholly below the others' 1st percentile, and one in
  thirty does.
- The 1 % bar's real per-text false-flag rate is therefore about 3.3× nominal. That is register heterogeneity.
  It is not sampling noise.
- The lane reports this honestly in the T1 row and the closing stamp. The problem is the plain-language summary
  (1.5 #1).

### 1.4 Specific ask — lead (ii) "descriptive p = 0.005": **fair label, incomplete caveat**
- The number is correct (§1.2), and calling it "descriptive" is right. Three things are missing:
  1. The full-LP2 U1b is **not a registered test**. The PREREG registers U1b on four parts only.
  2. It is computed on the **discovery data**. R45-X1 found this lead as 53 % vs 71 % on these same 126 + 532
     lines, so the p-value re-expresses the original observation and carries no confirmatory weight.
  3. The same applies to "LP2 shows a small boundary preference overall" (U1a full, p = 0.005), since X1's
     "71 % vs chance 78 %" was itself the observation that π > 0.

### 1.5 Further findings
- **(a) T3 distinguishability misreported (FOUND-ERROR, low–medium).**
  - `conf[R][R']` is the fraction of R's windows admitted by R' (`p1_lead_i.py:129`).
  - Row OE gives EN-FE = **1.00**, so OE and EN-FE are **not** distinguishable under the registered rule (both
    off-diagonals must be ≤ 0.2).
  - "Latin … separable from English (≤ 0.07)" is also loose: EN-merge20 windows are admitted by LA at 0.18. That
    still passes ≤ 0.2, but it is not ≤ 0.07.
  - The OE and SOLVED rejections still follow the rule ("survives iff admitted"). But both references are single
    texts with narrow bars: OE rejects 80 % of fresh-English windows, and SOLVED rejects 67 %. So the rejection
    says LP2 is not a resample of *Beowulf* or of the 739 solved words. It does not say LP2 is outside Old English
    or outside a "Cicada register".
- **(b) T2 inherits T1's panel.** T2's part p-values come from the same FE panel whose size control failed, and
  T2 had no size control of its own. S_even's p = 0.0006 is 1 of 1,800 windows, very likely *Paradise Lost*. So
  "replicates in every part" is sound as a **homogeneity** result (the section G test, p = 0.80, at power 0.98)
  and register-conditional as an extremity result.
- **(c) Lead-(ii) plants do not run through the lane's own glue (low).**
  - Real data go through `struct()` and `summ()`, which parse the transcription string.
  - Plants compute c, f_in and excess inside `layout()`, a parallel implementation with no page gaps and no
    non-running lines.
  - Every lead-(ii) verdict is already "uninformative", so this changes no verdict. It does mean the power
    figures (0.17–0.62) are measured on a model, not on the pipeline. The next lane should render plants to a
    `/`-`-` string and parse them with `struct()`.
- **(d) Plants for lead (i)** (thinning, article deletion, merging) act on length lists. The parser is guarded by
  an `assert` against `w1lib.load_lp2`, which is acceptable for a length-level statistic.
- **Conditionals:** all three are stated, with Greek, Hebrew and Norse listed as not covered.

### 1.6 Required corrections (exact edits to `P1-leads/RESULTS.md`; coordinator applies)
1. Replace `**LP2 sits below every fresh English
register tested except Milton's archaic blank verse, which comes within 0.6 points.** The R45 reference panel
was not the cause of the lead, but the panel's lower edge depends on register.` with `**LP2 is below all 6,000
fresh windows, but one fresh register (Milton's blank verse, minimum 16.06 %) comes within 0.6 points, and that
single corpus is what fails the size control.** Whether the R45 panel caused the lead is therefore not settled
by T1; the panel's lower edge depends on register.`
2. Replace `1. **Lead (i) is real, it covers the whole text, and it is not an artefact of R45's corpus choice.**` with
`1. **Lead (i) covers the whole text (T2 homogeneity, section G p = 0.80); whether it is extreme for English is
register-dependent (T1 uninformative: Paradise Lost windows reach 16.1 %).**`
3. Replace `Latin and Welsh are cleanly separable from English (≤ 0.07). German and Old English
are separable from fresh English, with a caveat: 70 % of German windows are admitted by EN-noART.` with `Latin and
Welsh are separable from English (off-diagonals ≤ 0.18). German is separable from fresh English, but 70 % of German
windows are admitted by EN-noART. Old English is **not** distinguishable from fresh English by the registered rule
(100 % of OE windows are admitted by EN-FE); its rejection of LP2 reflects a narrow single-text (Beowulf) bar.`
4. Replace `That last
point is new: LP2's length profile is **not** the solved pages' profile (G 193 vs bar 91).` with `LP2's profile
is not a resample of the 739 solved words (G 193 vs bar 91), but that bar has no between-text variance and
rejects 67 % of fresh-English windows too, so this is weak evidence about register.`
5. In the lead-(ii) table, replace `| the LP1/LP2 difference holds on the full data |` with `| not registered; computed on
the R45-X1 discovery data, so no confirmatory weight |`. Then, after `stands as a
**descriptive** fact.`, insert ` It is the R45-X1 observation itself re-expressed as a p-value (same 126 + 532 lines),
not a test of it.`
6. Add to Conditionals §2: `Lead-(ii) plants are simulated inside layout(), not parsed through struct()/summ(), so
lead-(ii) power is measured on the layout model, not on the lane's parsing glue.`
7. Make the same changes to `ledger_rows.json`:
   - In R46-P1-TWO-RUNE-EXPLANATIONS, `"LA, CY vs English": "off-diagonal <= 0.07: distinguishable"` →
     `"off-diagonal <= 0.18: distinguishable; OE vs EN-FE NOT distinguishable (OE->EN-FE 1.00)"`.
   - In R46-P1-LINEBREAK-INSIDE-WORDS `result`, `Full LP2 vs LP1 p=0.0051 (descriptive)` →
     `Full LP2 vs LP1 p=0.0051 (descriptive; unregistered, on the discovery data)`.

---

## 2. A1 — instrument hygiene

### 2.1 Pre-registration: clean, with disclosed exceptions
- **Stamps verified.** The base stamp `6409d7bc…` equals sha256 of the PREREG prefix before `## Addendum 1`,
  with trailing whitespace stripped and one `\n` added. The Addendum stamp `47c12be5…` equals sha256 of the full
  file. `run.log` timestamps (UTC) precede `downstream.py` and `repair_alignment.py` in their final versions.
- **Disclosed exception 1.** The fable52 code edits were made before the PREREG.
- **Disclosed exception 2.** Rule R-a5 (Addendum 1) was added after the first repair run produced a duplicate.
  It is justified by pre-existing evidence (S1 A5 strip read) and moves no label, since both lines are non-exact.
- **Stamp convention (low).** The checker accepts a normalised prefix (rstrip + `\n`, optional `---`). The rule
  text in RESULTS §(c) says "byte prefix". Also, the checker proves append-only history but **not chronology**:
  a stamp written into a log after results would still VERIFY. Both should be stated (correction 3).

### 2.2 Alignment repair: verified. **NO-ERROR-FOUND in the map**; one count misstated
- **All rows checked programmatically.** Comparing `alignment.json` (v2) to `corrected_map.json` for all 56
  images, every v2 entry equals `true_gline`, with two exceptions:
  - 11/3 (R-a5, disclosed);
  - 49/2 (R-a3: `true_gline` null, set to 553).
  No image's v2 lines span more than one canon page. Image 50 is `[]`, and image 49 is `[551, 552, 553]`.
- **Spot-checks against independently rebuilt canon line lengths** (`%` and `/` split of `krisyotam_runes.txt`):

  | image/clean | count | v1 → len | v2 → len | corrected_map | ok |
  |---|---:|---|---|---|---|
  | 36/3 | 22 | 403 (len 8) | **402 (len 22, opens ᚠᚠ)** | 402 | ✔ the S1/X1 line-402 defect fixed |
  | 36/2 | 22 | 402 (22, false-exact) | 401 (22, opens ᚦᛈ) | 401 | ✔ |
  | 6/7 | 22 | 75 (24) | 76 (22) | 76 | ✔ |
  | 39/0 | 23 | 433 (22) | 432 (23) | 432 | ✔ |
  | 15/5 | 22 | 172 (23) | 173 (22) | 173 | ✔ |
  | 49/2 | 21 | — | 553 (21, page 49) | null | ✔ R-a3 justified |
- **Count error (low).** `changed_or_flagged` has 29 rows, but 4 of them are R-a2 rows where v2 = v1. Entries
  that actually changed: **25** (24 R-a1 + 1 R-a3). "29 positional entries changed" is wrong in both RESULTS and
  the ledger row.
- **Label diff counts reproduce.** I re-ran `downstream.py` inside my script: removed 0, added 372, relined 89,
  rune-changed 87, OOF agreement 10,687 → 10,774/10,774, 86/86 disagreements resolved, 351/351 on new labels.
  This is the same code, so it shows reproducibility, not independence. The 351/351 really is out-of-sample,
  because those glyphs were unlabelled in v1.

### 2.3 Specific ask — "450 → 670 is unstable": **UPHELD, and sharper than stated** (new measurement)
`x1_oae_basins.py` reuses A1's glue read-only and runs 20 random 42-glyph removals from **each** label set, plus
PCA seeds 0–4 (A1 varied only the KMeans seed):

| set | PCA seeds 0–4 | 42-glyph removals (20) |
|---|---|---|
| v1 | 450 ×5 | 15 × low basin (428–439), **5 × high (621–628)** |
| v2 | 670 ×5 | 19 × high (641–650), **1 × low (447)** |

- **Both label sets reach both basins.** The repair moved the default basin. It did not create the instability.
- **Stable core.** 282 glyphs are mismatched in ≥ 90 % of the runs where they are present. **258 of the
  committed 450 are in that core**, so about 190 of the 450 are basin artefacts.
- So "It is not a property of the glyphs" overstates the case. The count is basin-dependent, but a
  258-glyph core is stable.
- **Context.** S2's leave-line-out template agrees with canon on 1186/1186 exact-line O/A/AE glyphs, and A1's
  classifier OOF is 100 %. The core is a property of unsupervised clustering, not a canon-error signal.

### 2.4 Fable52 repoint: verified where cheap
- The external clone is still on disk. krisyotam and the external `lp2-transcription.txt` are rune-identical
  (13,136 runes), and their separators differ at exactly **2** positions: rune index 1886 and 9648, `-` vs `.`.
  This matches A1's claim.
- `git diff` shows path-only edits, plus `doublet_positions.json` now being written beside the script.
- I did not re-run the scripts. A1's external-input control already reproduces `OUTPUTS.txt`.

### 2.5 Required corrections (exact edits)
1. In `A1-hygiene/RESULTS.md`, replace `29 positional entries changed, 10 dead tail entries dropped` with
   `25 positional entries changed (24 R-a1, 1 R-a3; 4 R-a2 rows and the R-a5 row flagged but unchanged), 10 dead tail
   entries dropped`. Make the same change in `ledger_rows.json` R46-A1-ALIGNMENT-REPAIR `result`, replacing
   `29 entries changed` with `25 entries changed (+4 R-a2 rows flagged, unchanged)`.
2. In `A1-hygiene/RESULTS.md`, replace `It is not a property of the glyphs. The list stays useful as a candidate list, not as
   a count.` with `The count is not a property of the glyphs; R46-X1 (x1_oae_basins.json) finds both label sets reach
   both basins (v1 5/20, v2 1/20 flip) and a 282-glyph stable core containing 258 of the 450. Use the core as a
   candidate list, not the 450 count.` In the ledger row R46-A1-OAE450-INSTABILITY `not_covered`, add
   `"PCA seed (measured by R46-X1: no effect)"` → move it into coverage, and cite R46-X1-OAE450-BASINS.
3. In `A1-hygiene/RESULTS.md` §(c), after `recorded in the lane dir (…) or in the block itself.`, insert
   ` Prefixes are compared after stripping trailing newlines and an optional '---' line. The check proves the PREREG is
   append-only; it does not prove a stamp was written before the outputs (compare log timestamps for that).`

---

## 3. S2 — second independent reader

### 3.1 Pre-registration and blinding record
- **PREREG.** `build_log.txt` (15:43:33) logs `4f92cd4c…118bd3b`. I verified that this equals sha256 of the
  PREREG prefix before `---\n## Addendum S2-A` (rstripped + `\n`).
- **Unstamped addendum.** Addendum S2-A itself has no stamp; A1's checker flags it as UNSTAMPED. Full-file sha
  at audit time is `8a15e0dcaf96e40488f79031c40951cfe2d1a231e531b19714a7b18412e2d050`. The coordinator should
  record it in S2's log, noting it was stamped by X1 after the fact.
- **Batch chain.** 13 batch hashes are frozen between 15:46:22 and 15:49:43. `unseal.log` verifies all 13 before
  it opens `sealed.json` (15:53:13).
- **`gate.py`.** It reads `sealed.json` after batch 1 and prints only aggregates. That is the pre-registered Q5
  gate, so it is sanctioned.

### 3.2 Specific ask — leaked blinding
- **(a) The in-memory `json.load(open("sealed.json"))`.** It ran in an *inline, unsaved* helper, so it can't be
  audited at code level. "Nothing printed" is an honour-system claim.
  - The outcome is exactly what a leaked reader would produce: S2 = canon 279/279, 310/311 reads at H confidence,
    no alternatives used, about 13 s per 24-glyph batch.
  - It is also what a very good reader would produce. The files cannot tell the two apart.
- **(b) The C control is not blind to the reader in principle.** The reader recomputed the control-box indices
  from seed 46022 and labelled reference strips from decrypted page 73, the same page the C controls come from.
  - So C (24/24) is an optimistic power measure.
  - W (8/8, unsolved-page donors) is the clean control. With W alone, m₂ ≤ 0.369, and the two-reader bound
    becomes 2.04 % / (1 − 0.265 × 0.369) = **2.26 %** (vs 2.12 %).
- **(c) What does not depend on the blinding.** The leave-line-out template matches canon on every A/R item
  and on 1186/1186 OA, 751/751 MD and 1092/1092 THWR exact-line glyphs. It also names every W donor
  (`template_on_shown`), which makes W a planted hit through the template path too.
  - So **"0 canon errors on these 279" is supported by machine evidence independent of S2's blinding.**
  - What does depend on the blinding is the *inter-reader* result: κ, "S1 misreads", and S1's miss rate.

### 3.3 Arithmetic: all recomputed and reproduced
- **κ = 0.96898** (own code over the 179 pairs: p_o = 0.97207, p_e = 0.09962). OA 0.915, MD 0.916, THWR, NI and
  BE all 1.0.
- **CP95 upper bounds (two-sided, own bisection).**
  - Detection limits: 0/179 → 2.04 %; 0/217 → 1.69 %; 0/100 → 3.62 %.
  - Miss rates: 0/24 → m₂ 0.1425; 0/12 → m₁ 0.2646.
  - Two-reader bound 2.12 %, S2-only 1.97 %, R 4.22 %.
  - S1 miss rates: 5/179 → upper 6.40 %; 4/72 → upper 13.6 %.

### 3.4 Further findings
- **(a) The X1 caveat is not closed for 4 of its 10 cases (FOUND-ERROR, medium).**
  - S1's `adjudications.json` holds 10 family blind-vs-canon mismatches resolved for canon (excluding the 2
    misregistered line-401 items).
  - Six are in S2's frame A: gpos 6158, 6159, 1724, 4580, 4867 and 4773.
  - **Four are not:** 276 (A/AE), 5054 (TH/W), 6054 (AE/A) and 9877 (D/M).
  - X1 R45 §3's complaint was precisely that those 10 were resolved by an unblinded reader. Those 4 still rest on
    that resolution.
- **(b) The "2.1 % on the look-alike families" figure is a pooled bound.** THWR, NI and BE, which X1 did not
  flag, make up 83 of the 179. For the families X1 named, the two-reader bounds are:
  - **OA: 0/72, ≤ 4.99 % / 0.962 = 5.2 %**
  - **MD: 0/24, ≤ 14.8 %**
- **(c) S1's miss rate is heterogeneous.** It is 5/179 = 2.8 % on exact-line glyphs, but S1's own misses on its
  27 window-item family glyphs are at least 4 (≈ 15 %). "Replaces S1's ~7 %" holds for exact lines only.
- **(d) Ledger coverage miscount.** "32 family-hard controls" should be 24 (16 C-family + 8 W). The 14.3 % figure
  is the CP bound for 24.

### 3.5 Required corrections (exact edits)
1. In `S2-second-reader/RESULTS.md`, replace `This closes the X1 caveat
(`round45/X1-redteam/AUDIT.md` §3) for these glyphs.` with `This closes the X1 caveat (`round45/X1-redteam/AUDIT.md`
§3) for 6 of S1's 10 canon-resolved family mismatches; the other 4 (gpos 276, 5054, 6054, 9877) are outside frame A
and still rest on S1's unblinded adjudication.`
2. Replace `**Two-reader canon error bound on the family glyphs: ε ≤ 2.1 %** (95 %).` with `**Two-reader canon error
bound on the family glyphs: ε ≤ 2.1 %** (95 %, pooled over five families; O/A/AE alone ≤ 5.2 %, M/D alone ≤ 14.8 %).`
3. Replace `This replaces S1's circular
~7 % estimate.` with `This replaces S1's circular ~7 % estimate for exact-line glyphs; S1's misses on its 27
window-item family glyphs are ≥ 4 (≈ 15 %), so S1's rate is not homogeneous.`
4. Replace `**closed for the 179 exact-line family glyphs** and still open for S1's 27 window-item family glyphs.` with
`**closed for the 179 exact-line family glyphs** and still open for S1's 27 window-item family glyphs, which include
4 of S1's 10 canon-resolved mismatches.`
5. Add to the Blinding record: `The C control is not blind in principle: the reader recomputed the C box indices
(seed 46022) and labelled reference strips from the same decrypted page 73. W is the clean control; with W alone
(m₂ ≤ 0.369) the two-reader bound is 2.26 %. The sealed.json helper was inline and unsaved, so its "nothing printed"
cannot be audited; the canon conclusion is independently supported by the leave-line-out template (= canon at all
279), the inter-reader κ is not.`
6. In `ledger_rows.json` R46-S2-SECOND-READER-FAMILY-BOUND `coverage`, replace `1.0 observed on 32 family-hard
controls (C-family + W)` with `1.0 observed on 24 family controls (16 C-family + 8 W)`. In `not_covered`, add
`"4 of S1's 10 canon-resolved family mismatches (gpos 276, 5054, 6054, 9877) lie outside frame A."`. In
R46-S2-S1-READER-MISS-RATE `result`, append ` Exact-line glyphs only; S1's window-item family misses are >= 4/27.`
7. The coordinator stamps Addendum S2-A (§3.1).

---

## 4. Cross-lane notes
- **A1 × S2.** The template's 1186/1186 agreement on exact-line O/A/AE, together with A1's 100 % OOF, shows that
  the committed "450 O/A/AE disagreements" (doctrine R5 #1's "finite human-checkable object") were never
  evidence of canon ambiguity. They are an unsupervised-clustering output. R5's example list should cite the
  258-glyph core as a candidate list, or drop the example.
- **A1 → R45 S1.** The S1 scripts now break on v2 (`correct_map.py` IndexError on image 50). They need repointing
  to `alignment.v1.json` before R45 S1 can be reproduced. This is flagged by A1 and is the coordinator's job.

## 5. L1 — one printed-word loader + re-run of the voided rows (audited after its 21:25 closing stamp)

**Ruling: UPHELD-WITH-CORRECTIONS.** The loader, the reconciliation and every real-data re-run stand. One
headline is wrong: "R41 was effectively blind / legacy power 0.001 / the R41 negative was uninformative". That
figure comes from an exact-recovery conjunct which R41's own decision rule never had. Scored by panel score
alone, which is R41's actual criterion, legacy page-level power is **0.64** (§5.3). FOUND-ERROR, medium.

### 5.1 PREREG before outputs (ask 1): clean
- sha256(`PREREG.md`) = `8cf2c0ca…19da01`. That is the current file and also `run.log` line 1, stamped at
  15:43:49. PREREG mtime is 15:43:44, and the first code (`words.py`) is 15:45:24.
- There are no addenda; A1's checker gives base VERIFIED.
- Disclosed post-PREREG fixes:
  - the 452/34 → 388/32 wrap-count fix;
  - the `make_plant` overrun fix at 21:10, before any R41 plant number existed;
  - one miscounted test expectation.
  None of these edits a threshold.
- The R37 plants ran at 15:58, before the overrun fix. Their 240-rune heads lie well inside the stream, so they
  could not reach the overrun.

### 5.2 Recount (ask 2): reproduced with independent code
- My parser: first 12,956 runes of `krisyotam_runes.txt`, with breaks at `- . & $ §` and digits.
  - It gives **2,896 words**.
  - Non-empty rune gaps with no break character number **420**: **388** containing `/` (line) and **32**
    containing `%` (page).
- The legacy rules give the following counts, each the new count plus extra cuts only:

  | rule | words | = 2,896 + |
  |---|---:|---:|
  | "any non-rune breaks" (camp7) | 3,316 | 420 |
  | "`- . %` break" (mapcommon / SKELETON) | 2,928 | 32 |

- Every `&` and `$` gap also contains `-` or `.`: there are 0 exceptions. So mapcommon's blindness to `&`/`$`
  costs no cut.
- **Old loaders only added cuts: confirmed.**

### 5.3 R41 power (ask 3): the plants are partly R41's code; the legacy figure is not R41's power
- **Glue.** `enc_words` is verbatim `run_c1.py`, and the decode is `camp7.decrypt_variant`, R41's own code. The
  **scorer is panel-R36 `AD.adjudicate`, not R41's panel12** (gitignored; disclosed in RESULTS §7). The
  faithfulness check (best real page 3.642 on R41's segmentation) ties the two on real data only.
- **Same rule both ways.** The legacy 2/1760 *is* computed by the same rule and code as the new 1760/1760. The
  legacy arm swaps only the parser, through `l1lib.legacy_parse`, a re-implementation of camp7's rule.
- **The rule itself is the problem.** It is "exact page recovery AND pmax > P-null max 5.591". R41 decided on
  panel score against its null only, since it had no ground truth to check recovery against. Re-scoring
  `r41_plants_raw.json` with the score conjunct alone:

  | regime / loader | exact ∧ score (L1) | **score only (R41's criterion)** | mean recovery |
  |---|---:|---:|---:|
  | a / legacy | 2/1760 | **1129/1760 (0.64)** | 0.48 |
  | b / legacy | 1/1760 | **1134/1760 (0.64)** | 0.48 |
  | a / words.py | 1760/1760 | 1760/1760 | 1.00 |

- **The page score bar is clean.** Legacy pages with recovery < 0.1 cross it only 14/506 times, and pages with
  recovery ≥ 0.6 cross it 997/997. So the 0.64 is real detection of partly-recovered W1/W4 pages (mean recovery
  0.77 / 0.76). W2 is at 0.16 and W3 at 0.25.
- **The W level should not be scored by score alone.** b′ decodes at about 9 % recovery still exceed the W null
  max of 1.416 (30/32). The W-level null, built from LP2 shuffles, is not matched to English-plant ciphertext.
  Only the exact conjunct makes W-level power meaningful.
- **Verdict on R41.** Its page-level negative was **weakened (≈ 0.64, and about 0 for W2/W3)**, not
  uninformative. The re-run makes it a full-power negative, and the real-data conclusion (no crossing) is
  unchanged under both loaders.
- **This also corrects my own R45-X1 §2 wording** ("mostly corrupted"). Panel power at those recoveries is now
  measured, and it is substantial for W1/W4.
- **Pseudo-replication.** The 1,760 pages are 32 plant streams (16 variants × 2 reps) × 55 pages. The Wilson
  [0.998, 1] treats pages as independent. The stream-level figure is 32/32 (Wilson lower bound ≈ 0.89).

### 5.4 "Holds by inheritance" for R38-WORDNET / FREQRANK / R39-SENSE (ask 4)
- **"Decodes unchanged" is sound without a plant.** It is an equality argument. Both sweeps loop only
  `for p in (0, 1, 2)` (`round38/C1-semantic-road/sweep.py:86`, `round39/C1-sense-similarity/sweep.py:86`), and
  L1 shows the word boundaries inside those heads are identical under both loaders. Deterministic code on
  identical inputs gives identical decodes.
- **"Power 1.00 inherited" is not a measurement.** The U3 rho1 plants (16/16) share the decoder and `judge()`,
  but not the lexicon → key glue (WordNet/frequency/sense lookups) that these rows actually run.
- So the right statement is "real result unchanged; power under (a)/(b) not measured for this row's own glue".
  RESULTS already says "not separately planted". The power columns should not read 1.00.

### 5.5 C-01 "20.2 % chance-level" (ask 5)
- **The null is weak.** It is one shuffled-pattern scan per text, so 53 per-text maxima; z = (best − mean) / sd
  of those 53.
- **At full window the real best actually beats every shuffled maximum** (584 > 579, z 1.54,
  `real_beats_all_shuffled: true`). So "chance-level" means "a z-score of about 1.5 against a 53-draw null",
  not "inside the null".
- **The negative is still sound, for a different reason.** L1's own plants put a true plaintext at about 100 %
  (20/20 at W120 and W400), and 20.2 % is nowhere near that. The verdict should rest on the distance from the
  planted-hit level, not on the null.
- Minor: the RESULTS table's legacy cell "581 / 1,441" mixes slack 0 (581) and slack 1 (1,441).

### 5.6 R37-U3 928 decodes, best 4.35 vs bars (ask 6): sound
- The bars (6.632 / 6.529 / 6.895) are hard-coded from the R37-C1-U3 ledger coverage (bar_v3 at the original
  family N).
- That is the right bar, because the 928 re-decodes replace members of that family. All three bests are 2.3–3.2
  below their bars.
- Scope: only pages 1–2 under the new fragment convention C1. The old convention's decodes are R37's
  originals, so both conventions are now covered for the heads.

### 5.7 (b′) "kills power for every row" (ask 7): substantively right, with two wording errors
- Under (b′), every word-indexed instrument is at or near 0: R41 0/1760 exact, R37 0/64 and 0/48, SKELETON 0/20.
  R44-7GRAM is **0.033, not 0**. W5 (95/440) is the space-blind control, and R40 is not word-indexed.
- So "every row falls to 0" should read "every word-indexed row falls to ≤ 0.033".
- (b′) is one specific alternative, printed lengths permuted *within sentence*. Other non-plaintext length
  sources (lengths borrowed from another text, book-scope permutation) are not planted. The (b′) conditional is
  therefore "conditional under (b′) and any space source not equal to the plaintext's words", which the ledger
  text ("spaces not the plaintext's boundaries") states correctly.

### 5.8 Required corrections (exact edits to `L1-word-loader/`)
1. `RESULTS.md` line 17: replace `- **R41-R14 was effectively blind before. It is now a real negative.**` with
   `- **R41-R14 was weakened before (page-level power ≈ 0.64 by its own score rule; ≈ 0 for W2/W3). It is now a
   full-power negative.**`
2. `RESULTS.md` §3 R41 pages row: replace `**1760/1760** [0.998,1] | 2/1760 |` with `**1760/1760** (32/32 streams,
   Wilson ≥ 0.89) | 2/1760 exact∧score; 1129/1760 score-only (R46-X1) |`
3. `RESULTS.md` §5 R41 row: replace `**1.00** (legacy **0.001**: the R41 negative was uninformative)` with `**1.00**
   (legacy 0.001 under exact∧score; 0.64 under R41's score-only criterion: the R41 negative was weakened, not
   uninformative)`
4. `RESULTS.md` §5 R38-WORDNET row: replace `1.00 inherited (U3 rho1 16/16) | 1.00 inherited |` with `not measured
   (shares decoder/judge with U3 rho1, 16/16; lexicon glue not planted) | not measured |`. Make the same change in
   the FREQRANK and R39-SENSE rows (`1.00 inherited | 1.00 inherited |` → `not measured | not measured |`).
5. `RESULTS.md` §0: replace `every word-indexed row falls to 0.` with `every word-indexed row falls to ≤ 0.033
   (7-gram shape 0.033; all others 0).`
6. `RESULTS.md` §4 SKELETON: after `A true plaintext would sit near 100 %.`, insert ` The shuffled null is weak
   (one shuffle per text; the full-window real best 584 exceeds all 53 shuffled maxima, z 1.54); the negative
   rests on the distance from the planted-hit level (20/20 at ~100 %), not on the null.`
7. Closing stamp and `ledger_rows.json` (R46-L1-R41-R14-RERUN and R46-L1-REOPEN-VERDICTS):
   - replace `(legacy 0.001)` with `(legacy 0.001 exact∧score; 0.64 score-only)`;
   - replace `was uninformative before (legacy power 0.001)` with `was weakened before (legacy page power 0.64
     by score, 0.001 with exact recovery)`;
   - replace `holds a and b by inheritance (U3 rho1 plants 1.0), not separately planted` with `real decodes
     identical (holds); power for its own glue not measured`;
   - replace `Every row is CONDITIONAL under b' (spaces not the plaintext's boundaries): power 0.` with
     `Every word-indexed row is CONDITIONAL under b' (spaces not the plaintext's boundaries): power <= 0.033.`
8. Coordinator: add a `.gitignore` block for `L1-word-loader/r41_null_b*.npz` (regenerated by
   `arm_r41.py null`), as L1 itself asks.

New ledger row: **R46-X1-R41-LEGACY-SCORE-POWER** (`ledger_rows.json`).

## Files
`AUDIT.md`, `ledger_rows.json` (R46-X1-OAE450-BASINS), `x1_oae_basins.py`, `x1_oae_basins.json`,
`x1_oae_basins.log`. I wrote nothing outside this folder, did not edit LEDGER.json, and committed nothing.
