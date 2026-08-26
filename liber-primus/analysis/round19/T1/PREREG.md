# T1 — THE PER-RUNE READER AND THE 450 · PRE-REGISTRATION

_Written 2026-08-26, **before any accuracy was measured**. Binding:
[`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). Lane opened as the redirect
target of Round 19 on the recommendation of `round19/R1/RESULTS.md` §D.5 / §E item 6._

> Reconnaissance performed before this file was written, and disclosed here so the reader can
> judge what was already known: (a) the trust anchor was run and passes; (b) the vendored asset
> set was confirmed to be the same lineage as `data/relikd` by sha256 (`17.jpg` = `p0.jpg`,
> `72.jpg` = `p55.jpg`, so vendor index = relikd index + 17, hence `73.jpg` = p56 and
> `74.jpg` = p57); (c) all images are 2400×3600; (d) the corpus sections for `73.jpg` and
> `74.jpg` were read, and `74.jpg` is a **direct substitution** page whose runes are fully
> determined by its documented English plaintext. **No classification accuracy of any kind had
> been computed when this file was written.**

---

## 0. What this lane is for

Every statistical claim in this repository — the doublet deficit, the flat IoC, the entropy
bound, the OTP-class verdict — is downstream of the transcription being correct. The
transcription has **never had a from-scratch, per-glyph, independent re-read**:

- the 2026-06 whole-page vision armada scored mean alignment **0.145** — noise
  (`analysis/vision/AVENUE-1-VISION-VERDICT.md`). Its own stated revival path was *per-rune
  cropping, ~13k individual high-zoom reads, cost-prohibitive, documented but not executed.*
- the Campaign-V SVC scored 99.2 % CV but was **trained on canon labels**, so it proves the
  labels are learnable, not that they are correct
  (`analysis/independent-read/FINDINGS.md`).
- the 2026-07 label-free clustering audit refuted the *gross* systematic-misread hypothesis but
  left **450 located O/A/AE disagreements** unadjudicated
  (`analysis/independent-read/oae_mismatch.json`).

This lane builds the instrument that was never built, measures it, and — only if it passes —
uses it on the 450.

---

## 1. Hypothesis

**H-T1.** The LP page images are typeset renders of a font at a single point size
(`round18/L1-toolchain`: Ghostscript 400 dpi → ImageMagick q92, 2400×3600 px = 6.00×9.00 in).
Round 8's geometry lane measured that the **median glyph has a pixel-identical twin** — median
nearest-neighbour Hamming distance **0.0000** over 13,121 glyphs
(`analysis/geometry/shape_report3.json`). Therefore a per-rune reader that (i) segments by
connected component and (ii) classifies by native-resolution template match should reach
**≥ 99 %** per-rune accuracy, where whole-page vision reached 0.145 and C3's band reader reached
95.6 % on the LP2 face.

**H-T1 is a claim about the instrument, not about the cipher.** Its falsification is a measured
accuracy below the bar, and that falsification is itself the lane's deliverable.

---

## 2. The instrument, specified before it is built

### 2.1 Segmentation (fixed here; no post-hoc tuning)

1. Load page, greyscale, ink = `pixel < 128` (identical threshold to `geometry/segment.py` and
   `round19/C3/l3/reader.py`, so the number is comparable to both).
2. 4-connected components; discard `area < 40` or `h < 6` or `w < 4` (verbatim
   `geometry/segment.py` rejection rule).
3. Keep components whose height lies in the **rune band** `[95, 135]` px
   (`C3/l3/reader.py: RUNE_H`). Everything else — word-separator dots, vine margins, woodcuts,
   drop-caps, hairlines — is not a rune candidate.
4. Group rune candidates into text rows by vertical overlap; sort rows top-to-bottom, and
   within a row sort left-to-right by `x0`.
5. The emitted stream is the page's rune sequence.

**No merging or splitting of components is performed.** If a rune is not one component in this
font, this segmentation will fail and the failure will be visible in §5's kill condition rather
than hidden by a repair.

### 2.2 Classification (fixed here)

1. **Templates are built by unsupervised shape clustering with no labels shown.** Every rune
   candidate on **LP2 pages p0–p54** (the target set) is reduced to its native-resolution binary
   mask. Instances are clustered by exact/near-exact bitmap agreement under a small translation
   search; a cluster is a set of instances mutually within a distance cut.
2. A **cluster → rune bijection** (29 elements) is then fixed. This is the *only* label
   information entering the reader, it is a permutation, and it is a finite human-checkable
   object in the sense of doctrine R5. It is fixed by majority agreement against canon on
   p0–p54 and is **disclosed as canon-derived**.
3. Because a canon-derived bijection is a circularity risk, it carries **two independent
   checks, both pre-registered here**:
   - **B1 (external-plaintext check).** Reading `74.jpg` (p57) with this bijection must
     reproduce the page's **documented English plaintext** — `PARABLE / LIKE THE INSTAR
     TUNNELING TO THE SURFACE / WE MUST SHED OUR OWN CIRCUMFERENCES / FIND THE DIVINITE WITHIN
     AND EMERGE`. p57 is a direct substitution page, so its runes are determined by English text,
     which is an external human-readable fact and **not** a rune transcription. A wrong bijection
     cannot survive B1.
   - **B2 (chart check).** Each class's mean shape is rendered and read against the Gematria
     Primus chart. 29 human-checkable comparisons.
   A bijection error is necessarily *global* (it permutes a whole class), so B1 detects it at
   once. Per-glyph classification error is a different failure and is what G-READ measures.
4. **Control pages are held out of template construction entirely.** LP2 templates come from
   p0–p54; the LP2 control pages are p56 and p57. LP1 templates are built the same way from the
   LP1 image set with the page under test **left out** (leave-one-page-out).
5. Classification of a crop = nearest template under the same distance, with the **runner-up
   distance retained** so a margin is available for confidence.

### 2.3 The one code path

Everything — control measurement, plant-and-recover, and the 450 — goes through **one**
`classify()` and **one** `read_page()`. The number measured on the controls is a number about
the same machine that adjudicates the 450.

---

## 3. Gates and thresholds — fixed now, not to be edited

### G-READ (blocking; Job 2 does not start unless it passes)

Per-rune accuracy against decryption-validated ground truth on the solved control pages.

| gate | control set | bar | what it governs |
|---|---|---:|---|
| **G-READ-LP2** | `73.jpg` (p56) + `74.jpg` (p57), the **LP2 typeface** — the face of all 56 target pages | **≥ 99 %** | licence to run **Job 2**, because all 450 disagreements are on the LP2 face |
| **G-READ-ALL** | pooled over all seven solved control pages, both faces | **≥ 99 %** | the `AGENTS.md` §8 unpark claim, which does not distinguish faces |

Both are reported, with **raw counts**, a **full 29×29 confusion matrix**, and **per-class
recall**. Reported additionally, per the brief:

- accuracy split by typeface (LP1 vs LP2), because C3 measured they differ;
- accuracy as a function of **local page density**, because the OTP pages 45–54 are the densest
  and are where every prior audit was weakest;
- **the O/A/AE pairwise confusion rates specifically.** A per-class failure on exactly this
  triple invalidates Job 2 even at 99 % overall, and is therefore a separate, named gate:

### G-OAE (blocking for Job 2 independently of G-READ)

On the control set plus the held-out plant of §4.2, the pairwise confusion rate within
{O, A, AE} must be **≤ 1 %** in every ordered direction (O→A, O→AE, A→O, A→AE, AE→O, AE→A), and
each of the three classes must have recall **≥ 99 %**. If G-READ passes and G-OAE fails, **Job 2
does not run** and the lane reports that the triple is unseparable by this instrument.

### Anti-rounding clause

If G-READ lands between 95 % and 99 %, the **exact figure with counts** is reported, the gate is
recorded as **FAILED**, and the results state plainly what the measured level licenses and what
it does not. The bar is not relaxed, not re-scoped, and not rounded up. Any later change to a
threshold appears as a dated addendum with its reason, per doctrine mechanic 1.

---

## 4. Positive controls — plant, prove recovery, then trust silence

Doctrine mechanic 2: *a null from an unvalidated instrument is not a negative.* Job 2's most
likely outcome is "canon holds", which is a null. It is worth nothing unless the instrument is
shown to be able to **see a transcription error that is really there**.

### P-1 — the adversarial plant (governs the value of a "canon holds" result)

On a control page, replace the pixels of **k = 50** rune instances at known positions with the
pixel crop of a *different* rune taken from elsewhere in the corpus, and re-run the whole
pipeline. **Requirement: the reader flags ≥ 49/50 of the planted positions as disagreeing with
canon, and flags no more than the measured baseline false-disagreement rate elsewhere.**

If P-1 fails, "canon holds" from this lane means nothing and will be reported as meaning nothing.

### P-2 — the O/A/AE-specific plant

P-1 restricted to substitutions **within the {O, A, AE} triple only** — the hardest case, and
exactly the case Job 2 turns on. Same k = 50, same ≥ 49/50 requirement. Reported separately.

### P-3 — leave-one-out recovery on the template bank

Every template instance is classified with itself excluded. This measures the ceiling the
clustering imposes, independent of segmentation.

### N-1 — the null

Rune-height components drawn from **non-rune ink** (woodcut interiors, vine margins) pushed
through `classify()`. A classifier with no reject option will label them; the point is to
measure the distance distribution of true runes against non-runes, so that the confidence
reported in Job 2 is a calibrated quantity and not a softmax artefact.

---

## 5. Kill condition (Aiming Test Q5) — checkpoint at 10 % of budget

**Stop rule.** After segmentation is built and before any classifier is trained: emit the rune
count per LP2 control page and per LP2 target page and compare to canon's count for that page.

> **If the segmented stream cannot be put into 1:1 positional correspondence with canon to
> within 1 % of glyph count on the LP2 control pages, the lane stops and reports that per-rune
> adjudication is not reachable by connected-component segmentation.**

Rationale: per-rune *classification* accuracy is meaningless without positional correspondence —
that is precisely the error `analysis/vision/DIFF-REPORT.md` made when it read
"high-confidence disagreements" off a globally misaligned page. If positions do not line up, no
amount of classifier accuracy adjudicates anything.

A second, softer checkpoint: if the unsupervised clustering of §2.2 does not collapse to
approximately 29 dominant classes, the pixel-identical-twin premise is wrong for this
segmentation and the lane reports that instead of forcing it.

---

## 6. Job 2 — protocol, fixed before the 450 are looked at

Runs **only if G-READ-LP2 passes and G-OAE passes and P-1 and P-2 pass.**

1. **Locate.** Each of the 450 records in `oae_mismatch.json` carries
   `page_image`, `line_in_image`, `pos_in_line`, `global_glyph_index`, `canon`, `looks_like`.
   The records were produced against the *Campaign-V* segmentation, which is not this lane's
   segmentation. Each record must therefore be **re-located** in this lane's stream and the
   location **verified** by requiring that canon's rune at the located index equals the record's
   `canon` field. Records that cannot be located under that constraint are reported as
   **UNLOCATABLE** and counted; they are not silently dropped and not silently re-aligned.
2. **Classify.** The located crop goes through the same `classify()`.
3. **Confidence.** Calibrated from the control set: the margin between best and runner-up
   distance is binned, and each bin's empirical accuracy on the control set is the confidence
   attached to a call in that bin. **The margin cut separating DECIDED from UNDECIDABLE is set
   on the control set before the 450 are classified**, at the smallest margin whose control-set
   accuracy is ≥ 99.5 %.
4. **Emit** `adjudication.json`: one row per record —
   `page, line, pos, global_glyph_index, canon_call, t1_call, distance_best, distance_runnerup,
   margin, confidence, verdict ∈ {AGREE, DISAGREE, UNDECIDABLE, UNLOCATABLE}`.
5. **Answer the question the repo needs**, in these terms and no others:
   - does canon change — how many of the 450, in which direction;
   - is any of it on the **unsolved pages 0–54**;
   - if canon holds, say so plainly, quote P-1/P-2 as the evidence that a change would have been
     seen, and label it what it is: a valuable negative that retires a standing doubt.
6. The disagreement **count** is handed to sibling lane **T3**, which is measuring how many
   changed runes it would take to break the doublet-deficit argument. Sibling lane **T2** is
   doing the from-scratch A-01 re-read and the dense pages 45–54; this lane does not duplicate
   that and publishes its reader for T2 to consume.

---

## 7. The Aiming Test (doctrine §1) — five questions, answered

**Q1 — What would a hit look like, and would *this* instrument recognise it?**

A hit is: *canon's rune at a specific located position is not the rune on the page.* The
instrument recognises it as a DISAGREE row with a high-confidence call. This is not asserted —
it is **planted and measured**: P-1 substitutes 50 glyphs at known positions and requires
≥ 49/50 detection; P-2 does the same *inside the O/A/AE triple*, which is the exact shape the
hit is believed to take. If P-1 or P-2 fails, this lane is generating a null, not running an
experiment, and will say so.

**Q2 — What measured fact raises this family's prior above the flat rate?**

Four, each with a path:

1. `analysis/geometry/shape_report3.json` — over 13,121 glyphs the **median nearest-neighbour
   Hamming distance is 0.0000** (mean 0.0060, p99.9 = 1.358). The glyphs have pixel-identical
   twins. This is a typeset font, not handwriting, and it is the direct reason to expect
   template matching to succeed where vision failed.
2. `round18/L1-toolchain/RESULTS.md` — the render chain is Ghostscript 400 dpi → ImageMagick
   q92, 2400×3600 = exactly 6.00×9.00 in, runes typeset from a proportional font. The glyphs
   existed as character data before they were pixels.
3. `round19/C3/RESULTS.md` §1.3 — a band reader already reaches **95.56 %** on the LP2 face
   (172/180), and §1.5 reaches **100 %** (54/54) on short runic bands. The remaining gap was
   diagnosed there as **row segmentation, not glyph identity** ("same matches, fewer false
   glyphs, 86.46 % → 97.65 %"). This lane attacks exactly that diagnosed residual.
4. `analysis/independent-read/metrics.json` — unsupervised K=29 clustering already reaches
   homogeneity 0.879 rising to 0.983 at K=87 against canon, i.e. same-rune glyphs reliably
   co-locate by shape alone.

**Q3 — Is the space bounded, and by what?**

Yes, and it is **finite and enumerable**: 13,136 canonical runes, of which the adjudication
target is **450 located records**, each a single glyph at a stated page/line/position. This is
doctrine R5 **rank 1** — a finite, human-checkable object. There is no sampling fraction to
report; coverage of the stated target is intended to be 450/450, with any shortfall reported as
UNLOCATABLE counts rather than absorbed.

**Q4 — What are the three conditionals the negative will carry?**

Restated for an imaging lane, since the canonical three are cipher-shaped:

1. **The image space** — which pages, which lineage, at what resolution. Here: the hash-verified
   relikd masters for p0–p55 and the byte-identical-lineage vendored set for p56/p57 and LP1, all
   2400×3600. A different master or a higher-resolution source is **not covered**.
2. **The segmentation model** — connected components with a fixed rune-height band and no
   merge/split repair. Any true rune that is not one component in this band is **not covered**,
   and that gap is measured by §5's count check rather than assumed away.
3. **The classifier's discrimination register** — native-resolution binary template distance.
   A distinction the render does not preserve in ink (e.g. a difference below the JPEG-threshold
   noise floor) is invisible to this instrument and is **not covered**. The N-1 null and the
   margin distribution are what let this be stated quantitatively rather than waved at.

**Q5 — What single observation would make you abandon this lane at 10 % of budget?**

§5's kill condition: segmented glyph count on the LP2 control pages failing to reach 1:1
positional correspondence with canon to within 1 %. Positional correspondence is a precondition
for the whole lane; without it the per-rune reader would repeat the vision armada's exact error
in a more expensive form.

---

## 8. Rules this lane binds itself to

- Report **coverage × power**, never coverage alone (doctrine R2). Coverage = glyphs adjudicated
  / 450; power = P-1 and P-2 detection rates.
- **Bounds, not verdicts** (doctrine R7). No "the transcription is correct". The output is a
  measured disagreement count with a measured detection power and a stated not-covered list.
- Write only inside `round19/T1/`. **No `git commit`.** Crops and intermediate arrays are
  rebuildable and are not committed; hashes and findings are recorded instead.
- Trust anchor before and after. Before: run 2026-08-26, `validate.py` **ALL VALIDATIONS PASSED
  (5/5)**, `pytest benchmark/` **8 passed**.

---

## 9. Deliverables

`PREREG.md` (this file) · the reader and its tests · `RESULTS.md` (confusion matrix, G-READ
verdict, the 450 adjudication, the does-canon-change answer) · `out_*.json` ·
`adjudication.json` · `ledger.json`.
