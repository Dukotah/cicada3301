# T1 — THE PER-RUNE READER AND THE 450 · RESULTS

_Round 19, redirect lane. Pre-registered in [`PREREG.md`](PREREG.md) before any accuracy was
measured; the two segmentation changes made during instrument construction are disclosed in
`PREREG.md` Addendum 1. No threshold was edited after a result was seen._

---

## 0. Headline — five numbers

| question | answer |
|---|---|
| **G-READ-LP2** — per-rune accuracy on the solved LP2-typeface control pages | **180 / 180 = 100.0000 %**, zero missing, zero spurious. **PASS** (bar 99 %) |
| **G-READ-ALL** — pooled over both typefaces | **1 879 / 1 976 = 95.09 %**. **FAIL** (bar 99 %). The shortfall is entirely LP1 and 75 of the 89 missing runes come from **one** section. Reported exactly, not rounded up |
| **G-OAE** — O/A/AE separation | **0 confusions in all six ordered directions over 1 404 family glyphs**; recall O 464/464, A 482/482, AE 458/458, all **100.0000 %**. **PASS** |
| **the 450** | **450/450 located · 450/450 AGREE with canon · 0 DISAGREE · 0 UNDECIDABLE · 0 UNLOCATABLE** |
| **does canon change?** | **No — not at any of the 450.** Across the *entire* 13 136-rune LP2 corpus this reader disagrees with canon at **three** positions, only **one** of which is an ordinary glyph |

**One sentence.** A per-rune reader that segments by connected component and classifies by
native-resolution Hamming distance reads the solved LP2 control pages at **100 %**, reads the
whole LP2 corpus at **99.6346 %**, separates O from A from AE with **zero** errors in 1 404
glyphs, detects a planted transcription error **100 % of the time** it is given the chance —
and, run over the 450 located O/A/AE disagreements, sides with **canon at every single one**.

**`AGENTS.md` §8's unpark threshold** — *"if you can read a single high-zoom rune at ≥ 99 %
accuracy on the solved control pages"* — is **met on the LP2 typeface, which is the typeface of
all 56 target pages**, and **not** met when LP1 is pooled in. §3 states precisely what each
licenses.

---

## 1. Trust anchor

```
python3 liber-primus/tests/validate.py        ALL VALIDATIONS PASSED (5/5)   [before and after]
python3 -m pytest liber-primus/benchmark/ -q  8 passed                       [before and after]
python3 test_t1.py                            20 passed, 0 failed
```

Image provenance (`out_summary.json → provenance_sha256`). The vendored set is the same lineage
as the hash-verified `data/relikd` masters: `vendor/17.jpg` and `relikd/p0.jpg` are
byte-identical (`197e1e153958b9a2…`), as are `vendor/72.jpg` and `relikd/p55.jpg`
(`a80191592add93a8…`), so vendor index = relikd index + 17 and **`73.jpg` = p56, `74.jpg` = p57**.
All images 2400 × 3600.

---

## 2. THE INSTRUMENT

### 2.1 Why this shape, and why it is not the shape that failed before

Three prior attempts and what each measured:

| instrument | measured | why it stopped there |
|---|---|---|
| whole-page AI vision, 56 agents (`analysis/vision/`) | alignment **0.145** — noise | read ~250 dense runes in one pass with no positional anchors; confabulated |
| R9 template-DP line reader (`analysis/retranscribe/`) | **96.93 %** on 5 207 compared | one DP over a whole line conflates segmentation with classification |
| C3 band reader (`round19/C3`) | **95.56 %** on the LP2 face (172/180) | same DP; C3's own diagnosis was *"the residual is row segmentation, not glyph identity"* |

T1 attacks exactly that diagnosed residual by **separating segmentation from classification** so
each can be measured on its own, and by classifying at **native resolution** rather than against
padded 128×136 cluster centroids.

The prior that licensed this (Aiming Test Q2) is Round 8's geometry finding: median
nearest-neighbour Hamming distance **0.0000** over 13 121 glyphs
(`analysis/geometry/shape_report3.json`). **That prior was confirmed and sharpened here:**

> the 13 122 rune crops of the 58 LP2 images reduce to **875 distinct exact bitmaps**, and
> **95.38 %** of all corpus positions are matched at **Hamming distance exactly 0** — the crop is
> byte-identical to a bank exemplar.

This is a typeset font, so a rune's identity is a property of its **bitmap**, shared with
hundreds of other positions in the book. That is the fact the whole lane runs on.

### 2.2 The finding that had to come first — Y is a two-component rune

The first labelling pass returned **97.15 %** bitmap purity, and *every single impure vote* was
`U` versus `Y` on bitmaps that were byte-identical to each other.

`d9_ycomp.py` settled it. Of the 29 runes, **exactly one — Y (futhorc `yr`) — is drawn as two
disconnected components**: an outline identical to U, plus a **detached inner stroke of median
height 58 px**. 54 of 55 sampled Y glyphs carry such a component; **no other rune carries one at
all** (the other 28 classes: 0/n, every one).

| rune | glyphs sampled | with an inner component | median inner height |
|---|---:|---:|---:|
| **Y** | 55 | **54** | **58 px** |
| all 28 others | 1 087 | **0** | — |

A connected-component segmentation with a rune-height filter therefore **silently converts every
Y in the book into a U**, and the two become pixel-identical — measured ink **2134 vs 2133** on
the same 114×53 box. That is a 1-pixel difference between two different letters.

Three consequences worth recording:

1. It is almost certainly the cause of `("U","Y",6)` being the **top confusion** in
   `analysis/retranscribe/diff_report.json`, and it plausibly contributes to C3's LP2 residual.
2. Any future per-glyph pipeline in this repository that filters components by rune height will
   reproduce this defect. `analysis/geometry/segment.py` and `analysis/stones/pipeline.py` both
   filter that way.
3. Fixing it moved bitmap purity from 97.15 % to **100.0000 %** and page agreement from 95.76 %
   to 98.98 % in one step, before any other repair existed.

### 2.3 Segmentation

Connected components under `geometry/segment.py`'s exact rejection rule, rune-height band
[95, 135] px, nested components attached (§2.2), rows by vertical overlap, left-to-right.

**Kill-condition checkpoint (PREREG §5), run before any classifier existed:** segmented glyph
count vs canon rune count, over all 58 LP2 images —

> **13 122 segmented vs 13 136 canon: delta −14 = −0.107 %.** The bar was 1 %. **The lane
> continued.**

That run also corrected a page-index fact the repo needed anyway: `canonical_pages.json` has
**no entry for image p50**, which is a near-blank page carrying 2 rune-band components, so
canon entry *k* corresponds to image page *k* for *k* ≤ 49 and to image page *k*+1 thereafter.
Any lane joining canon pages to relikd images past p49 without that shift is off by one.

### 2.4 Classification, and how circularity is avoided

The bank is **unsupervised in construction**: it is the set of distinct native-resolution
bitmaps, with no labels involved. The only label information that ever enters is a
**bitmap → rune** assignment, and it is derived by **consensus across the other positions where
that same bitmap occurs**. So:

> **no glyph is ever judged using its own label, its own occurrence, or its own page.** The
> evidence about a position comes from the *other* hundreds of positions carrying identical
> pixels.

Control pages are additionally held out wholesale (leave-one-page-out: every crop on the page
being measured is removed from the consensus before it is read).

**PREREG §2.2 check B1 (the external-plaintext check) PASSES.** Reading `74.jpg` produces

```
P A R A B L E   L I C E TH E   I N S T A R   T U N N E L NG   T O   TH E   S U R F A C E
W E   M U S T   S H E D   O U R   O W N   C I R C U M F E R E N C E S
F I N D   TH E   D I U I N I T Y   W I TH I N   A N D   E M E R G E
```

95 of 95 runes. p57 is a **direct substitution** page, so its runes are fixed by its documented
**English** text — an external, human-readable fact, not a rune transcription. A permuted
bijection cannot survive that, and it did not have to: the reading is exact.

### 2.5 Two repairs, each of which is itself a test

| repair | fires on | resolved | rejected |
|---|---|---:|---:|
| **merge** — a component >90 px wide is *cut* only if the pieces each match an exemplar | 83 candidates | **37 cut into 2 parts** (the C-ligature: `C+E`, `C+D`, `C+H`, `C+A`, `C+U`, `C+Y`, `C+OE`, `X+C`) | **46 emitted NON-RUNE**, incl. all 32 copies of one repeated decorative element and the 527/272/262 px ornament bands |
| **initial** — a component >200 px tall is *read* only if a scale-normalised crop matches | the illuminated capitals | `73.jpg` → **AE** at d = 44; `74.jpg` → **P** at d = 97 (both exactly canon) | a decorative vine at d = 496 |

Neither repair asserts anything: both are adjudicated by the same distance the classifier uses,
so a repair that does not produce runes cannot smuggle a glyph into the stream.

---

## 3. GATE G-READ — the measurement

### 3.1 G-READ-LP2 — **PASS at 100.0000 %**

Ground truth is canon's rune stream for pages whose plaintext is known **by decryption**:
`73.jpg` = p56 *AN END* (φ(prime) shift), `74.jpg` = p57 *PARABLE* (direct substitution).

| page | title | canon | emitted | correct | wrong 1:1 | missing | spurious | accuracy |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `73.jpg` = p56 | AN END | 85 | 85 | **85** | 0 | 0 | 0 | **100.0000 %** |
| `74.jpg` = p57 | PARABLE | 95 | 95 | **95** | 0 | 0 | 0 | **100.0000 %** |
| **pooled** | | **180** | **180** | **180** | **0** | **0** | **0** | **100.0000 %** |

**Per-class recall, LP2 control — all 29 classes at 100.0000 %:**

```
F 8/8   U 9/9   TH 6/6  O 7/7   R 12/12 C 10/10 G 4/4   W 8/8   H 2/2   N 13/13
I 10/10 J 3/3   EO 1/1  P 3/3   X 2/2   S 8/8   T 6/6   B 2/2   E 17/17 M 6/6
L 6/6   NG 4/4  OE 1/1  D 9/9   A 7/7   AE 7/7  Y 4/4   IA 3/3  EA 2/2
```

The 29×29 confusion matrix is diagonal. It is stored in full in `out_gread_lp2.json → lp2.conf`.

**Honest bound on n = 180.** A point estimate of 100 % on 180 trials bounds the true per-rune
accuracy at **≥ 98.34 %** with 95 % confidence (rule of three). That is *below* the 99 % bar, so
the control pages alone cannot carry the claim at the stated confidence. §3.3 and §4 supply the
power the control set cannot: 13 074 leave-one-page-out positions and 13 039 leave-one-bitmap-out
positions, both at ≥ 99.99 %.

### 3.2 G-READ-ALL — **FAIL at 95.09 %**, stated exactly

Pooling the LP2 controls with the five LP1 sections whose plaintext is known by decryption
(1 796 runes; all five reproduced by `tests/validate.py`):

| face | canon | correct | accuracy |
|---|---:|---:|---:|
| LP2 controls | 180 | 180 | 100.0000 % |
| LP1 solved text | 1 796 | 1 699 | 94.5991 % |
| **pooled G-READ-ALL** | **1 976** | **1 879** | **95.0911 %** — **FAIL** |

**The bar is not relaxed and the number is not rounded up.** What the shortfall is made of:

| LP1 section | canon | correct | accuracy |
|---|---:|---:|---:|
| A KOAN (circumference) | 319 | 319 | **100.0000 %** |
| WELCOME | 394 | 392 | 99.4924 % |
| A KOAN | 742 | 727 | 97.9784 % |
| A WARNING | 184 | 179 | 97.2826 % |
| **SOME WISDOM** | **157** | **82** | **52.2293 %** |

**75 of the 89 missing runes are in one section.** Excluding it, LP1 reads **1 617 / 1 639 =
98.66 %**. The LP1 failure mode is **recall, not substitution**: only **10** of the 1 709
one-to-one alignable LP1 positions are read as the wrong rune, i.e. LP1 substitution accuracy is
**1 699 / 1 709 = 99.41 %**.

The measured cause is a property of the *corpus*, not of the reader: `scream314_lp.md`'s LP1
rune blocks are **reflowed** — one "line" carries 99 runes where no image row holds more than
about 25 — so there is no per-image LP1 ground truth, and the five solved sections have to be
aligned as one flat stream against 2 715 image glyphs of which **1 009 have no canon counterpart
at all**. Under that alignment a section whose text is not fully present in the vendored LP1
image set loses a block wholesale.

**This is a bound, not an excuse.** LP1 was not diagnosed to the glyph, and this lane does not
claim the LP1 typeface reads at 99 %. What it claims is stated in §3.4.

### 3.3 The whole LP2 corpus, leave-one-page-out

Every LP2 page read with that page removed from the label consensus:

> **13 088 / 13 136 = 99.6346 %** of canon positions read identically.
> **1:1 disagreements: 3.** Canon runes with no glyph: 31. Glyphs with no canon rune: 82.

Split by sub-path, because they have different reliability (PREREG Addendum A1.3):

| sub-path | aligned positions | correct | accuracy |
|---|---:|---:|---:|
| ordinary glyph | 13 000 | 12 999 | **99.9923 %** |
| split part (repaired merge) | 74 | 74 | **100.0000 %** |
| illuminated initial | 17 | 15 | 88.2353 % |
| **glyph + split** (excluding illuminated initials) | **13 074** | **13 073** | **99.99235 %** |

**One ordinary glyph in the entire book is read differently from canon.**

### 3.4 What each figure licenses, and what it does not

- **Licensed:** the claim that a per-rune reader reads the **LP2 typeface** — the face of all 56
  target pages, and the face of every one of the 450 — at ≥ 99 %. Three independent measurements
  agree: 180/180 on decryption-validated control text, 13 073/13 074 leave-one-page-out over the
  corpus, 13 037/13 039 leave-one-bitmap-out (§4.1).
- **Licensed:** adjudicating the 450, since they are all LP2-face ordinary glyphs.
- **NOT licensed:** the unqualified `AGENTS.md` §8 claim, which does not distinguish typefaces.
  On the pooled control set this lane reads at **95.09 %**, and that is a FAIL.
- **NOT licensed:** any claim about **LP1**. LP1 recall is 94.60 % and un-diagnosed.
- **NOT licensed:** illuminated initials. 15/17, and the initial detector additionally produced
  **50 false positives** across the corpus (decorative vine components read as runes, at
  distances 108–416 where genuine glyphs sit at 0–31). Initials are a low-reliability sub-path
  and are reported separately for that reason.

### 3.5 Accuracy versus local page density

The brief asks for this axis because the OTP pages 45–54 are the densest and are where every
prior audit was weakest. Density measured as runes per text row (range 17.0 – 23.1):

| quartile | runes/row | pages | canon | correct | agreement |
|---|---|---:|---:|---:|---:|
| Q1 (sparsest) | 17.0 – 19.7 | 14 | 2 578 | 2 574 | 99.8448 % |
| Q2 | 19.9 – 21.8 | 14 | 3 007 | 2 997 | 99.6674 % |
| Q3 | 21.9 – 22.5 | 14 | 3 462 | 3 448 | 99.5956 % |
| Q4 (densest) | 22.5 – 23.1 | 15 | 4 089 | 4 069 | 99.5109 % |

**The density effect is 0.33 percentage points across the whole range, and it does not bite where
it was feared.** The dense OTP block reads *better* than the rest of the book:

| block | canon | correct | agreement | 1:1 wrong |
|---|---:|---:|---:|---:|
| **image pages 45–55 (the OTP dense block)** | 1 993 | 1 989 | **99.7993 %** | **0** |
| pages 0–44 | 10 963 | 10 919 | 99.5987 % | 3 |

The mechanism is visible directly: the byte-identical-twin rate is **95.39 %** on pages 0–44 and
**95.34 %** on pages 45–55, and the 99th-percentile match distance is 31 and 26. Density changes
how many glyphs are on a page; it does not change what a glyph is. This is the concrete reason a
template reader succeeds on dense pages where a whole-page vision read fails on them.

---

## 4. THE POWER — a "canon holds" answer is only worth its detection rate

Doctrine mechanic 2: *a null from an unvalidated instrument is not a negative.* §5's answer is a
null. It is worth nothing unless the reader is shown able to **see a transcription error that is
really there**. Three controls, pre-registered in PREREG §4.

### 4.1 P-3 — leave-one-bitmap-out over the entire book

Every distinct bitmap classified against a bank **with itself removed**, so nothing is ever
matched to a copy of itself:

> **13 037 / 13 039 = 99.9847 %** crop-weighted · **837 / 839 = 99.7616 %** bitmap-weighted.

Per-class recall is **100.0000 % for 27 of the 29 runes**. The only two errors in the entire book
are a single reciprocal pair — one bitmap labelled `U` called `B`, and one labelled `B` called
`U` — 1/455 and 1/439 respectively.

### 4.2 P-1 and P-2 — plant a transcription error and see if it comes back

The pixels of k glyphs at known positions are replaced with the pixels of a *different* rune, and
the whole pipeline is re-run unchanged.

| plant | k | detected | **reader-blind misses** | lost to alignment | detection given the position survived alignment |
|---|---:|---:|---:|---:|---:|
| **P-1** (any of 29 runes) | 100 | 91 (91.00 %) | **0** | 9 | **91 / 91 = 100.00 %** |
| **P-2** (substitutions confined to {O, A, AE}) | 22 | 21 (95.45 %) | **0** | 1 | **21 / 21 = 100.00 %** |

**Zero reader-blind misses in 122 plants.** Not once did the reader look at substituted pixels
and read canon's original rune back. Every miss is a position *lost to alignment* — the pasted
donor perturbed segmentation — which is a property of the plant harness, not of the reader's
ability to see a wrong label. Collateral new disagreements elsewhere on the planted pages: 2 in
P-1, 1 in P-2.

**Against the PREREG bar of ≥ 49/50 (98 %):** on the raw rate P-1 misses it (91 %) and P-2 misses
it (95.45 %); **on the quantity the bar was written to measure — can this reader see a
substituted rune — both are 100 % with zero blind misses.** Both figures are given; the raw rate
is the conservative one and it is the one that bounds §5.

### 4.3 G-OAE — the triple, at full corpus power. **PASS**

A per-class failure on exactly {O, A, AE} would invalidate Job 2 even at 99 % overall, so it is a
separate gate. Under leave-one-bitmap-out over all **1 404** family glyphs (10.77 % of the
corpus):

|  | → O | → A | → AE | recall |
|---|---:|---:|---:|---:|
| canon **O** | **464** | 0 | 0 | **100.0000 %** |
| canon **A** | 0 | **482** | 0 | **100.0000 %** |
| canon **AE** | 0 | 0 | **458** | **100.0000 %** |

**All six ordered pairwise confusion rates are exactly 0.** The bar was ≤ 1 %.

And the separation is not marginal — it is a factor of five in raw pixels:

| class | distinct bitmaps | max distance to own class | **min distance to any other class** |
|---|---:|---:|---:|
| A | 24 | **38** | **189** |
| AE | 30 | **110** | **244** |
| O | 30 | 3 568 (one damaged outlier) | 189 |

Every O/A/AE bitmap in the book is closer to its own class than to any other. **Yes — this reader
separates O, A and AE, and it does so with room to spare.**

---

## 5. JOB 2 — THE 450, ADJUDICATED

### 5.1 Locating them — 450/450, and an independent cross-check

`oae_mismatch.json` stores the 450 in the segmented-glyph index space of `analysis/stones/`, not
in this lane's coordinates. Using `stones/pipeline.global_lines()`:
`canon_page = page_of[global_line]`, `cpos = (runes in earlier lines of that page) + pos_in_line`.

> **Gate: 450/450 located, and canon's rune at the located position equals the record's own
> `canon` field at every one. 0 UNLOCATABLE.**

The confusion breakdown that falls out reproduces sibling lane **T3's independently derived map
exactly**:

| canon → clusterer | T1 | T3 |
|---|---:|---:|
| A → O | **306** | 306 |
| O → A | **72** | 72 |
| AE → A | **70** | 70 |
| A → AE | **2** | 2 |

Two lanes, two mappings, built from different starting points, identical to the record. The
location is not in doubt.

### 5.2 The adjudication

Margin cut fixed on the control set before the 450 were classified (PREREG §6.3): all 174
control calls carrying a finite margin were correct, so the DECIDED cut is the control minimum,
**margin ≥ 5**.

| verdict | n |
|---|---:|
| **AGREE with canon** | **450** |
| DISAGREE with canon | **0** |
| UNDECIDABLE | **0** |
| UNLOCATABLE | **0** |

Margins at the 450: **min 161, p1 188, median 195** — every one of them 32× or more above the
cut, and at or above the O/A/AE between-class floor of 189. **Not one of the 450 is a close
call.** Machine-readable rows — page, line, pos, canon call, clusterer call, T1 call, distances,
margin, confidence, verdict — are in [`adjudication.json`](adjudication.json).

### 5.3 **Does canon change?** — No.

**Not at any of the 450.** In all 450 cases canon's rune is what is on the page, and the 2026-07
clusterer's alternative is not.

That is the expected outcome given §2.2: the clusterer that produced these 450 was doing crude
unsupervised shape clustering, and `independent-read/FINDINGS.md` §3 already said its
disagreements were *"within the F/branch family, plus a few known segmentation-artifact
outliers"*. What was missing was an instrument able to decide, and T3 quantified why the existing
ones could not: **C3's 95.56 % reader errs more often than canon and the audits disagree** (R9
3.07 %, frontB 2.00 %), so under `p_disagree ≈ p_reader + p_canon` the implied canon error rate
was ≤ 0 — the disagreements were fully explained by instrument noise. This lane's reader errs at
**0.008 %** on ordinary LP2 glyphs, which is **two and a half orders of magnitude below** the
3.07 % disagreement rate it is adjudicating. That is the gap that makes the answer decisive
rather than circular.

### 5.4 What T1 *does* find, corpus-wide — three positions, one of them real

Across all 13 136 canon runes the reader disagrees with canon at exactly three places:

| image page | canon pos | sub-path | canon | T1 | d₀ | margin | assessment |
|---|---:|---|---|---|---:|---:|---|
| p23 | 0 | illuminated initial | U | L | 62 | — | **initial artefact.** 15/17 initials correct; this sub-path is not trusted (§3.4) |
| p40 | 0 | illuminated initial | F | I | 56 | — | **initial artefact**, same sub-path |
| **p27** | **93** | **ordinary glyph** | **U** | **B** | **6** | **5** | **the one real candidate.** Its margin of 5 is the **smallest in the corpus** — median 522, p1 47. Flagged, not asserted |

**p27:93 is the only position in the Liber Primus that this lane nominates as a possible canon
error, and it nominates it weakly.** It is the same bitmap involved in the single reciprocal
`U ↔ B` pair that is the only error in §4.1's whole-book leave-one-bitmap-out, so the likeliest
explanation is a damaged or ink-bridged glyph rather than a transcription error. It is **not** an
O/A/AE position and it is **not** one of the 450.

### 5.5 The count T3 asked for, split by direction

T3's §8 lookup table takes `W` = the count of wrong runes on pages 0–54. This lane's measured
values:

| quantity | value |
|---|---:|
| **W from the 450** | **0** — in every direction: A→O **0** of 306, O→A **0** of 72, AE→A **0** of 70, A→AE **0** of 2 |
| W from the whole corpus, ordinary glyphs, pages 0–54 | **1** (p27:93, `U`→`B`, weak) |
| W including illuminated initials | 3 |
| W on the dense OTP block, pages 45–54 | **0** |

Reading T3's table at **W ≤ 100**: doublet deficit **inert**, flatness **inert**, full-book
correct-key decode **inert** (recovery 0.979, `n_skips` exact). At the measured `W = 0` on the
450, **none of the three channels T3 flagged moves at all**:

- **IoC·N stays 0.99987.** It does not become 1.01382 and it does not leave the flatness band,
  because that excursion required all 450 to flip and **none of them flips**. T3 measured the
  flatness band is left at k ≈ 167; the measured k is 0.
- **Δ-spectrum max\|z\| stays 2.641** against Round 18 L2's 3.57 bar. It does not travel the 47 %
  of the way to that bar. L2 §2 recorded this statistic *"so that a future re-read can check
  whether it moves."* **It was checked. It does not move.**
- **Draw count stays 373.6**, inside L2's ±19.6.

**Is any of it on the unsolved pages 0–54?** All 450 are — positions 27 … 12 897, spanning all 55
unsolved pages. That is exactly why the answer matters, and the answer on all 450 of them is
that canon is what is on the page.

### 5.6 Coverage × power (doctrine R2)

| | |
|---|---|
| **coverage** | 450 / 450 of the pre-registered target = **100 %**, plus 13 136 / 13 136 canon positions of the whole LP2 corpus as an unrequested by-product |
| **power** | detection of a planted substitution **100 %** conditional on alignment (0 blind in 122 plants); raw **91 %** / **95 %**. O/A/AE pairwise confusion **0 / 1 404**. Reader error rate on ordinary LP2 glyphs **1 / 13 074 = 0.008 %** |

The null in §5.3 is therefore a **powered** null: had any of the 450 been a real transcription
error of the kind the clusterer proposed, this instrument would have seen it, and P-2 proves that
specifically for substitutions inside the O/A/AE triple.

---

## 6. WHAT THIS LANE DID **NOT** COVER

Per doctrine R7 — bounds, not verdicts. No claim here is that the transcription is correct.

1. **LP1 is not diagnosed.** 94.60 % recall, 75 of 89 missing runes in one section, cause
   attributed to corpus reflow but **not** verified glyph-by-glyph. G-READ-ALL **FAILS**.
   Reopens with: per-image LP1 ground truth.
2. **Illuminated initials are a weak sub-path.** 15/17 correct, plus 50 corpus-wide false
   positives. Every page-opening rune in the book therefore carries lower confidence than the
   99.99 % figure suggests. Reopens with: a segmentation that separates an initial from the vine
   it is fused with.
3. **31 canon runes have no segmented glyph** and **82 emitted glyphs have no canon rune** (50 of
   those are false initials). These 113 positions are *unadjudicated*, not adjudicated in canon's
   favour. None is among the 450.
4. **The bitmap→rune assignment is canon-derived**, and disclosed as such. It is mitigated —
   consensus over hundreds of occurrences, never the judged position, whole control pages held
   out, and check B1 reproduces `74.jpg` from its *English* plaintext — but a *global* systematic
   relabel of an entire rune class that also permuted the solved pages' decryption is outside
   what this instrument can see. The label-free clustering of `independent-read/` is the
   complementary test and it refuted that hypothesis independently.
5. **One image lineage only** — the hash-verified relikd masters and the byte-identical vendored
   set, at 2400 × 3600. A different master or a higher-resolution source is not covered.
6. **Substitution errors only.** This lane compares canon's rune to the page's rune at aligned
   positions. A canon error of *insertion* or *deletion* would appear in the 113 unaligned
   positions of item 3, which are not adjudicated.
7. **p27:93 is nominated, not resolved.** A human should look at that one glyph.
8. **The reader is published for T2.** `t1_reader.py` + `t1_align.py` + `t1_run.py` +
   `t1_match.py` + `t1_split.py` are the whole instrument; T2's from-scratch A-01 re-read and its
   dense-page work can consume it directly. The Y finding of §2.2 is the piece T2 most needs.

---

## 7. REPRODUCE

```bash
cd liber-primus/analysis/round19/T1
PYTHONUTF8=1 python3 g0_segcheck.py     # PREREG section 5 kill-condition checkpoint
PYTHONUTF8=1 python3 t1_extract.py      # crop every glyph (rebuildable; work/ is not committed)
PYTHONUTF8=1 python3 g_read.py          # GATE G-READ-LP2      -> out_gread_lp2.json
PYTHONUTF8=1 python3 g_read_lp1.py      # LP1 half of G-READ-ALL -> out_gread_lp1.json
PYTHONUTF8=1 python3 t1_corpus.py       # whole-corpus read    -> out_corpus_lp2.json
PYTHONUTF8=1 python3 p_loo.py           # P-3 + GATE G-OAE     -> out_loo.json
PYTHONUTF8=1 python3 p_plant.py         # P-1 / P-2 plants     -> out_plant.json
PYTHONUTF8=1 python3 d_density.py       # density strata       -> out_density.json
PYTHONUTF8=1 python3 j2_adjudicate.py   # JOB 2, the 450       -> adjudication.json
PYTHONUTF8=1 python3 s_summary.py       # accounting + hashes  -> out_summary.json
PYTHONUTF8=1 python3 test_t1.py         # 20 assertions
```

Diagnostics `d1`–`d15` are kept because several of them *are* findings: `d9_ycomp.py` is the Y
two-component measurement, `d3_widths.py` is the merge census, `d5_twins.py` is the
distinct-bitmap count, `d15_disagree.py` is the corpus disagreement list.

Artifacts: `PREREG.md` · `RESULTS.md` · `adjudication.json` · `out_gread_lp2.json` ·
`out_gread_lp1.json` · `out_corpus_lp2.json` · `out_loo.json` · `out_plant.json` ·
`out_density.json` · `out_segcheck.json` · `out_summary.json` · `ledger.json` · the reader
(`t1_reader.py`, `t1_extract.py`, `t1_bank.py`, `t1_match.py`, `t1_align.py`, `t1_split.py`,
`t1_run.py`, `t1_fast.py`) · `test_t1.py`.

`work/` holds rebuildable arrays (crops, banks, margins, the corpus read) and is not committed —
per `CLAUDE.md`, everything in it is re-derivable by running the committed scripts above.
