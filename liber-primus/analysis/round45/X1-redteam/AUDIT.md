# R45-X1 — Red-team audit of Round 45

_2026-11-23. PREREG: `PREREG.md` (written before any X1 output). Doctrine R6: verdicts are FOUND-ERROR /
NO-ERROR-FOUND (with caveats), never "confirmed". Scripts in this folder; each re-run < 1 min._

| lane | verdict | headline issue | severity |
|---|---|---|---|
| W1-spaces | **NO-ERROR-FOUND, with caveats** | headline reproduces (LP2 A_global LLR z −1.16 vs lane −1.18; solved +3.75 vs +3.79); segmentation alternatives do not create order; "+7.5" is a point extrapolation (95 % range ≈ +3.6 … +11.4) | low |
| I1-decoy-space | **FOUND-ERROR (evidence mislabelled) + missed pre-existing defect** | (1) the "bit-identical 160/160" test cannot fail: the harness asserts `parse(render(C)) == C` before decoding; (2) the R41-C1-R14 real run split 420 line-wrapped LP2 words, so its negative was underpowered even with true spaces, and I1 did not see this | (1) low · (2) **medium** |
| S1-transcription | **NO-ERROR-FOUND, with caveats** | line-402 alignment defect independently verified from data and image; error-rate bound depends on unblinded, same-reader adjudication that resolved 10/10 mismatches toward canon | medium (for the bound only) |
| T1-t7-mechanism | **NO-ERROR-FOUND, with caveat** (closed mid-audit; audited after its stamp) | PREREG sha chain verified append-only; "T7 is concentrated (top-5 pairs 0.29 of 0.38)" is what chance produces for any r of this size (§5) | low–medium (interpretive) |
| Fable52 vs T1 | **both consistent; neither localisation nor "distributed" is strongly established** | see §5 | — |

---

## 1. W1 — What are the spaces?

**Re-run** (`x1_w1_segmentation.py` → `x1_w1_segmentation.json`; W1's own LLR model, 2,000 global shuffles):

| stream / segmentation | n words | LLR z | MI z | mean len | 2-rune share |
|---|---:|---:|---:|---:|---:|
| LP2, W1 canonical (`- . & $ §` break; `/`, `%` don't) | 2,896 | −1.16 | +0.03 | 4.47 | 15.5 % |
| LP2, line breaks also break | 3,316 | +0.75 | −0.49 | 3.91 | 18.7 % |
| LP2, page breaks also break | 2,928 | −1.55 | +0.26 | 4.43 | 15.9 % |
| solved, canonical | 738 | +3.75 | +2.84 | 4.03 | 24.0 % |
| solved, line breaks also break | 822 | +2.81 | +1.18 | 3.62 | 25.1 % |

- **Segmentation artifact? No.** Neither alternative segmentation brings out order in LP2. The canonical rule
  is right: splitting at line breaks *weakens* the solved reference (+3.75 → +2.81), which shows that
  line-wrapped words really are single words.
- **Solved reference (739 words): correct object.** These are the printed LP1 + AN END/PARABLE lengths. The rtkd
  LP2 tail is asserted identical to krisyotam. R-A matches 739/739, against 95.4 % for R-B and 76.6 % for R-C, so
  the alignment does tell the rules apart. Caveat: the difflib alignment can skip the 135 extra reference words
  freely, so 100 % is an upper-biased agreement figure. It does not change the rule choice.
- **z scaling.** +7.5 is a point estimate. From the solved run's numbers (excess 22.8 over the null mean, null
  sd 6.02, 737 pairs), the 95 % range at 2,896 words is about **+3.6 … +11.4**. LP2's −1.18 is still far below
  the lower end, and the English power of 1.00 doesn't depend on this extrapolation. *Fix:* the ledger row
  should report the range, not "~+7.5". Note also that the solved-Cicada positive control is weak at its own
  size: LLR is 3.79 against a bar of 3.35, and MI at 2.78 fails the bar.
- **Controls.** Every failing control is reported as uninformative (B_U, single-page D, M1 size). That is honest.
- **Look-elsewhere.** Q1 is Bonferroni-corrected over 25 tests. The 2-rune deficit is labelled post-hoc
  (Addendum 2). Honest.
- **Process caveat.** `PREREG.md`'s mtime (21:09) is later than the q1/q2/q2b outputs (20:58–21:08). The addenda
  were appended, and the file is untracked with no sha stamp, so the original frozen text can't be verified.
  The same holds for S1 (PREREG mtime 21:16, after the blind reads). *Fix for future rounds:* write the PREREG
  sha256 into the first run log (R44-B3 practice).
- **Q4 caveat (low).** The q̂ ≤ 0.20 boundary-contiguity bound uses the within-word doublet rate as a stationary
  baseline. T7 says the leakage rate is non-stationary. The effect is small, but the bound assumes stationarity.
- **New descriptive lead (post-hoc, no verdict).** 420 of 593 LP2 line breaks (71 %) fall inside words. If line
  breaks were placed without regard to words, about 78 % would. In solved LP1 only 78 of 146 (53 %) fall inside
  words, against a chance rate of 75 %. So LP1's layout prefers to break lines at word boundaries and LP2's
  layout barely does. That fits "LP2 layout done without regard to the printed spaces", but page-format
  differences could also explain it. A candidate for a pre-registered test only.

## 2. I1 — decoy-space audit

1. **The "bit-identical under 4 space conditions, 160 plants" result is a tautology, not a measurement.**
   `arm_beam.py` renders C with `-` separators, parses back runes only, and then `assert Cp == list(C)` before
   decoding. Identical decodes are guaranteed before beam_v3 runs. The conclusion is still true, but for a
   different reason. The instruments take index arrays, and the real LP2 path builds them with
   `src/lp/gematria.runes_to_indices` (non-runes dropped). That is a **source property**, verified here by
   reading the code, not something measured on plants. The row `R45-I1-SPACE-BLIND-PIPELINE` names "bit-identical
   a–d" as its *threshold*, a threshold that cannot fail. *Fix:* restate the row as "space-blind by construction
   (runes_to_indices); H-shuffle power measured (condition e)". Condition e (words permuted before
   encipherment) is a genuine measurement and stands.
2. **Missed defect, pre-existing: R41-C1-R14 split line-wrapped words (FOUND-ERROR, medium).**
   `round41/C1-r14-r15/camp7.word_pages()` ends a word at *any* non-rune character, including `/` and newline.
   The R41 real run (`run_c1.py:27 pages_w = C.word_pages()`) therefore decoded LP2 as **3,316 words instead of
   2,896**: 420 line-wrapped words were cut in two. The R41 plants were recut with that same fragmented length
   list (`recut_words`), so the lane's own plant could not see the problem. I1's condition "a" hands the decoder
   the true segmentation directly, so it does not reproduce the real run either.
   Measured here (`x1_r41_linewrap.py` → `x1_r41_linewrap.json`): English plaintext (pride) is laid out with
   LP2's exact page lengths and line-break positions, enciphered per page with the true words (I1's verbatim
   `enc_words`), and decrypted by camp7's own `decrypt_variant`.

   | variant (sign +1 / −1) | mean page recovery, camp7 parse | pages ≥ 0.9 | `-`-only parse |
   |---|---:|---:|---:|
   | W1 | 0.79 / 0.81 | 0.03 | 1.00 |
   | W2 | 0.25 / 0.26 | 0.00 | 1.00 |
   | W3 | 0.91 / 0.91 | 0.68 | 1.00 |
   | W4 | 0.78 / 0.80 | 0.01–0.04 | 1.00 |
   | W5 (space-blind) | 1.00 | 1.00 | 1.00 |

   So **under the very hypothesis R41 tested (true, in-order spaces), its W1/W2/W4 decodes were mostly
   corrupted.** Panel power at 0.79 recovery was not measured: the panel npz is gitignored and the run would
   exceed the audit budget. This matters most under **H-shuffle** (plaintext words permuted but still the
   encipherer's words). W1 cannot exclude H-shuffle, and I1 shows word schedules keep full power under it, *if*
   the segmentation is right.
   Other loaders, checked by reading code:
   - `round10/L2-map/mapcommon.parse` (R37 U2/U3, and R38/R39 by inheritance) and
     `skeleton/wordlen_search.lp2_words` treat `/` correctly. Both break at `%`, which splits 32 page-wrapped
     words, and mapcommon also ignores `&`/`$`. Those are minor, but they are inconsistent with W1's rule.
   - `round40|41 lib.runs_s2` (U6A-S2, class B) counts `/` as a separator and emits zero-length runs. That is
     its own channel definition, but it is not the printed-word convention.
3. **Reopen list.** The rows really are word-indexed, checked against the LEDGER `hypothesis` text: C-01, R37-U2
   (the U2b half), U3, R38-WORDNET/FREQRANK, R39-SENSE, R38-G3, R41-R14 and R44-7GRAM all index by printed or
   cipher word. Two caveats:
   - **R40-C1-INCONCLUSIVE-R31**'s row text ("page-local semantic keys / crib readouts") doesn't say it uses
     word positions, so its inclusion is unverified.
   - Four rows are inherited and were not re-run, which I1 itself states.
4. **R41 enc_words copy: faithful.** It is identical to `run_c1.py:107-124` up to the module alias `C`→`C7`
   (`diff -w` clean).
5. Minor: the closing stamp says 21:25, but RESULTS.md's mtime is 21:21. The stamp time is not real.

## 3. S1 — transcription audit

- **The line-402 defect is verified independently.**
  - `alignment.json` lists canon line 399 under image 35 (`[387…399]`) and image 36 as `[400…409]`.
  - The canon `%` markers put 399 on page 36.
  - Cropping `data/relikd/p35.jpg` and `p36.jpg` shows p35 ending with line 398 (ᛗᛒᚢ…). The first text line of
    p36 reads as 23 glyphs ending …ᚠᛠᚫᚫᚩ·ᛉ, which is canon 399.
  - Canon lines 401 and 402 are both 22 glyphs long. `build_dataset.py`'s positional `clean[i] ↔ align[i]`
    pairing therefore matches physical line 401 to canon 402 as "exact".
  - Line 402 opens ᚠᚠ (the doublet) and line 401 opens ᚦᛈ, which is S1's blind read TH,P. The mechanism is
    confirmed from data. The same page-break crossing exists at 432 (image 38). There, no adjacent lines have
    equal lengths, so no false-exact pairing follows.
- **Blinding is honour-system.** The same agent built `sealed_manifest.json` (written in the same second as
  `items_blind.json`) and did the reads. The procedure records the sha of `blind_reads.json` before unsealing,
  which is good. Nothing shows the manifest was not read. All 7 relocated targets, including 2 doublet sites
  (K075, K103) and 3 F1 items, were re-read **unblinded with canon printed**.
- **Adjudication bias (medium, affects the bound only).** All 10 blind mismatches went to unblinded zoom by a
  reader who knew canon, and all 10 were resolved *for* canon. The "≥ 90 % detection" model estimates the miss
  rate in the look-alike families (~7 %) from those same canon-resolved disagreements, which is circular. The 31
  controls come from one page (73.jpg) and only exact-count lines, and few of them are O/A/AE or M/D. So reader
  accuracy on the hard families has no independent measurement. The **0/146 [0, 2.5 %]** bound holds for
  non-family glyphs. For O/A/AE and M/D it is a bound conditional on an unblinded adjudicator.
- **Control relabel: honest.** The gate went 4/24 → 11/11 after the drop-cap relabel. That relabel was then
  tested out of sample on 20 freshly drawn, sealed controls, which scored 20/20. Dropping 74.jpg (13 controls)
  is justified (box count off by 5).
- T7 depends on the doublet census. All 86 sites are confirmed (84 blind), and no hidden doublet turned up in
  F3. That supports T7's input at the canon level.

## 4. T1 — T7 mechanism (closed 21:32, while this audit was running; audited after its closing stamp)

**Verdict: NO-ERROR-FOUND, with one interpretive caveat.**

- **Process: the best in the round.** `run.log` stamps the PREREG sha256 before any script ran, and again
  before each addendum. I checked: the sha256 of PREREG.md's bytes up to `## Addendum 1` equals the first stamp
  (`02c52532…`). The bytes up to `## Addendum 2` equal the second (`45dd27d4…`). The full file equals the
  third (`9b9459db…`). So the PREREG really was append-only.
- **T7 replicates.** My independent uniform null gives p = 0.00055 (T1 reports 0.0010). The census reproduces
  B3's 86 sites (halt gate).
- **S3 null is powered** (0.865 vs the P-M2 plant). The gate's false-fire rate sits exactly on the bar (0.020)
  and is disclosed. The "no mechanism reproduces T7" point (E1: joint T7 ≥ 0.38 ∧ S3 = 0) is a post-hoc joint
  event and is correctly labelled exploratory.
- **Caveat (low–medium, interpretive).** Verdict item 3, "**T7 is concentrated**" (top-5 pairs 0.29 of 0.38),
  is reported as a property of the data. Under the null, any r ≥ 0.3 has the same concentration (median top-5
  share 0.76; §5). This figure should not be read as localising T7 to the void.
- E0b fragility (one extra doublet at ~740 positions drops T7 to p ≈ 0.1) is a fair and useful measurement. It
  points the next lane at specific image lines (§7).
- The M3a "favoured" label is correctly downgraded: it is unrelated to T7 and has a 3.5 % false-pick rate.

## 5. Cross-lane: Fable52 "distributed heterogeneity" vs T1 "top 5 gap pairs carry 0.29 of 0.38"

`x1_t7_concentration.py` (null = 86 sites uniform on 12,955 adjacencies, 20,000 draws):

- Observed: r = 0.380 (p = 0.0005); top-5 contribution 0.291 = **77 % of r**.
- **Under the null, among draws that reach r ≥ 0.3 by chance (62 of them), the median top-5 share is 76 %.** For
  a Pearson lag-1 AC on near-exponential gaps, a few large-gap products always dominate. So "5 pairs carry most
  of it" **does not localise T7**. It is what any r of this size looks like.
- Dropping the 5 top pairs from both the real data and every null draw leaves residual dependence at
  **p ≈ 0.04 (Pearson 0.126) / 0.05 (rank 0.181)**. The full rank AC is 0.269 (p ≈ 0.003, Fable52).
- **Reading.** Both statements are consistent. Neither is strong evidence for its framing. The rank and
  winsorised versions survive (Fable52), so T7 is not *only* a few outlier gaps. The residual after the top-5
  removal is marginal, so "distributed" is also only weakly supported. T1 should not present the top-5 figure as
  a localisation result without this null comparison.

## 6. Fable52 external paths (not edited)

| script | external file (`C:\Users\dukot\AppData\Local\Temp\lpx\r\resources\liber-primus\…`) | in-repo replacement |
|---|---|---|
| `load.py` (`THEIRS_TXT`) → used by `load2.py` → `t1_doublet_structure.py`, `t3_t7_anatomy.py`, `t4_wordlen_burst.py`, `t4b_solved_control.py`, `t6_wordlen_lagscan.py`, `t8_wordlen_scope.py` | `lp2-transcription.txt` | `data/krisyotam_runes.txt` (rune-identical; carries `- . / % & $`; the W1/T1 loaders) |
| `t4b_solved_control.py`, `t6_wordlen_lagscan.py` | `lp1-plaintext-reference.txt` | printed LP1 lengths from `data/sources/rtkd_master.txt` (W1 `w1lib.load_lp1`, the correct object), or the sha-pinned copy `analysis/round45/W1-spaces/inputs/lp1-plaintext-reference.txt` |
| `t2_p50_mask.py` | `lp2-grid-256.json` | **no in-repo equivalent**; derive from `dataset/liber_primus.json` page 50 or commit a pinned copy |
| `reconcile.py` | `lp2-corpus.json` | the external side by design; pin a hashed copy (M0 imports) |
| `t2_p50_mask.py` input `doublet_positions.json` (made by t1) | (in-folder, 2nd-rune index) | `analysis/round44/W2-B3-doublet-sites/results.json` `real_sites_U86` (first-rune index, used by T1) |

`load.py` and `reconcile.py` also hard-code the absolute path `C:\Users\dukot\projects\…\dataset\liber_primus.json`;
they should use a path relative to `__file__`.

## 7. Recommendation for Round 46

**CONTINUE, with a REDIRECT of the word lane.** Nothing in Round 45 is overturned:

- W1's "no order" survives the segmentation audit.
- The standing pipeline is space-blind (by construction).
- Canon is clean at the measured resolution.

The one error that changes a ledger row is pre-existing: the word-indexed schedules were run on a segmentation
that splits 420 words. That matters exactly in the case W1 cannot exclude (H-shuffle).

**Single best-aimed next lane: a T7-void targeted transcription re-read (finite object, R5).**

- **What to read.** T1's E0b names the ~1,100 runes where one hidden doublet would drop T7 to p ≈ 0.1: runes
  3040–4035, 1565–1620 and 9570–9625, about 5 page images.
- **Who reads it.** A *different* agent from S1, fully blind, with no unblinded adjudication by someone who
  knows canon. Plant real controls drawn from the look-alike families.
- **What to read for.** Every adjacent pair where a misread could hide an equal pair.
- **Why this lane.** T7 is the round's only live anomaly. This lane either hardens it or dissolves it. It also
  closes S1's main caveat, the unblinded family adjudication.
- **First fix.** Repair `analysis/stones/alignment.json` (S1's defect), so the crops show the right canon lines.

**Second (cheap, instrument R1): segmentation repair.**

1. One canonical printed-word loader, using the W1 rule: `- . & $ §` and numerals break; `/` and `%` do not.
2. Re-run R41-C1-R14 W1–W4 with it, and re-check R37 U2b/U3 `%`/`&`/`$` handling.
3. Plant under H-shuffle on LP2's real line layout.

This one is lower prior, since the campaign7 self-key is a lore-derived hypothesis, but it costs minutes and
fixes a measured defect.
