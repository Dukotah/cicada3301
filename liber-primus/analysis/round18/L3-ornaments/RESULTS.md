# L3 — ORNAMENTS & LAYOUT · RESULTS

_Round 18. Ledger items **A-06** and **B-12** (both `never-run`). Parked item **P-9**.
Pre-registration: `PREREG.md` + `PREREG-ADDENDUM.md`, both written before the measurements
they govern._

**Headline.** The 47/62 catalogued "ornament bands" have been cropped, physically
classified and read for the first time. **None of them contains a runic message.** They
decompose into four populations, three of which are decoration or mis-binned body text —
and one of which is *data the pipeline threw away*: the alphanumeric blocks on pages 49–51.
Separately, a channel this repo had never measured — **ink tone** — turns out to be real,
discrete and previously unrecorded here: **226 components across 25 sites on 16 pages are
set in a lighter ink than the body text**, and one of them is **the single grid cell `3299`
on page 15**. Every content hypothesis H1–H8 fails its pre-registered threshold; the B-12
line-geometry channels fail at stage (b)/(c) and the one correlation that survived is
**fully mediated by glyph width** — it is typographic justification, not a channel.

---

## 0. Data integrity (precondition)

`python3 liber-primus/handoff/capsule/verify_capsule.py --only images` →
**PASS, 56/56 sha256 intact.** The local `data/relikd/p*.jpg` were verified, not
re-downloaded blind.

**New provenance fact, not previously recorded anywhere in this repo:** the vendored 2014
render set at
`corpus/E-tooling/vendor/cicada-solvers__documenting-cicada3301-scream314/assets/2014/liber-primus-complete/`
is the **same lineage** as `data/relikd/` — asset `17.jpg` is **byte-identical by sha256**
(`197e1e153958b9a2…`, 695,525 B) to `data/relikd/p0.jpg`. That matters because it supplies
what the relikd mirror does not: the **cryptographically solved** pages (`01/03/05/06/14`
from LP1, and `73.jpg`/`74.jpg` = LP2 p56/p57) at the identical 2400×3600 render, and
therefore a genuine solved-page control for a glyph reader. relikd serves p0…p55 only;
`p56.jpg`/`p57.jpg` return **404** (checked). **No page in `data/relikd/` is solved** — a
fact that matters for anyone who assumed otherwise when calibrating.

---

## 1. What the 47 bands actually are

`inventory.py` re-runs Round 8's row-grouping and ornament-rejection logic
(`geometry/analyze.py`, 62 rows; `geometry_report.json:ornaments`, 47 rows) and restores
the **y coordinate that `ornaments.json` drops** — the stored file is
`[page, x_lo, x_hi, n_components, median_height]` with no y, which is the mechanical reason
nobody could crop these bands even if they wanted to. Union, deduped: **109 band records
across 39 pages** (`inventory.json`); **30 have n ≤ 16** — P-9's "only real candidates".

Every band was cropped from the verified renders and read (`read_bands.py` →
**`bands.json`**, 109 records, **9,899 glyphs**, with per-glyph template match cost, a
physical ink classification and a RUNIC / DEGENERATE / NON-RUNIC call).

### The four populations

| class | n | what it is | evidence |
|---|---|---|---|
| **T — mis-grouped rune TEXT** | 82 | ordinary body lines the Round 8 heuristic rejected because a marginal vine ornament merged several rows into one tall band | `medh` = 114 (the rune body height), match cost 55–175 (known-text median 128), degeneracy 0.06–0.17 |
| **V — vine / hairline decoration** | 10 | page-border swirls, and the 8 px × 39 px slivers on p24/p26 that are single vine strokes | reads are **DEGENERATE** — one long vertical stroke matched repeatedly by the narrow `ᛁ` template (degeneracy 0.89–1.00) |
| **W — woodcut illustration** | 3 | the cicada (p2/p3), the wing (p14), the reclining figure (p22), the trees (p32/p55) | match cost 348–2003, i.e. far into the garbage band |
| **D — non-runic DATA discarded as ornament** | 5 | the **alphanumeric blocks on pp. 49/50/51**; adjacent, same failure mode: the **4×4 numeric grid on p15** | see §1a |

**No band in any class is a runic ornament carrying a message.** Every band that reads as
runes is either genuine body text that was mis-binned, or a degenerate stroke read.

### 1a. The load-bearing discovery — the "ornament" bucket contains the book's non-runic data

`analysis/geometry/*` rejects a band when it sits outside the dominant text column or when
its median component height exceeds 240 px. The alphanumeric lines on pp. 49–51 are shorter
than rune lines and sit inside a vine frame, so they were binned as **non-text** and have
never entered any analysis in this repository.

P-9's "16-glyph bands" are therefore **not 16 runes**:

| band | page | n | what it actually is |
|---|---|---|---|
| `B096` | 50 | 16 | `2M 0w 3L 3D 2r 0S 1p 15` — 8 two-character tokens, 16 characters |
| `B098` | 51 | 16 | `28 2a 0J 1L 0c 3C 2o 0X` |
| `B100` | 51 | 8 | a full-width slice: two vine fragments plus a sliver of the row below |

Read from the verified render at high zoom and **cross-checked against two independent
community transcriptions already vendored here** — `cmbsolver-lpviewer/files/text/lb/{49,50,51}.txt`
and `libergo/cmd/base60/base60numbers.txt`, which are **byte-identical to each other** and
match the vision read of the first line of p50 and p51 exactly (`nonrunic.py` →
`nonrunic.json`).

The full block is **32 lines × 8 tokens = 256 tokens** over pp. 49 (10 lines), 50 (13) and
51 (9). Under the base-60 reading (`value = 60·index(c₀) + index(c₁)` on
`0-9A-Za-z`) they span exactly **0…255**: **256 bytes**. They are **not** a permutation —
161 distinct values, against a uniform-i.i.d. expectation of **162.0**. So: 256 bytes of
material statistically indistinguishable from uniform random.

That object exists in the community corpus; what is new here is that **this repository's own
analysis tree has never held it**, because its segmentation pipeline classified it as
ornament and discarded it. It is now in `nonrunic.json` with the derivation and the
cross-check.

The p15 grid, likewise recorded with its arithmetic (`nonrunic.json:page15_grid`):
row sums `[12670, 12713, 12350, 8250]`, column sums `[14340, 11021, 10454, 10168]`,
total `45983` — **not** a magic square in either direction.

---

## 2. Calibration — how far the reader can be trusted (gates G-A, G-B, C-2)

**Instrument:** the validated R9 template-DP reader (`retranscribe/templates.npz` + the
stored 29-class bijection in `retranscribe/diff_report.json`), driven through one shared
code path (`reader.py: read_ink_strip`) so the calibration number describes the same machine
that read the bands. The Round 12 front-B **forced** re-segmentation instrument is used
**nowhere** in this lane — it fails its own control at 12.9%.

### G-A — whole solved page, including row segmentation: **FAILS the 90% bar**

| control page | typeface | glyphs read | canon runes | agreement |
|---|---|---|---|---|
| `73.jpg` = LP2 p56 (solved, φ(prime) shift) | LP2 | 96 | 85 | **86.5%** |
| `74.jpg` = LP2 p57 (solved, default-gematria substitution) | LP2 | 109 | 95 | **81.7%** |
| `14.jpg` A KOAN (circumference) | LP1 | 237 | 319 | 70.2% |
| `01.jpg` A WARNING | LP1 | 182 | 184 | 50.5% |
| `05.jpg` SOME WISDOM | LP1 | 90 | 157 | 50.3% |
| `03.jpg` WELCOME | LP1 | 283 | 394 | 32.7% |
| `06.jpg` A KOAN | LP1 | 224 | 742 | 25.3% |
| **pooled** | | 2,001 | | **44.2%** |

Two structural facts, stated so the number is not over- or under-read:

1. The split is not random. The two pages in the **LP2 typeface** — the same face as every
   page in this lane's target set — score **81.7–86.5%**; the LP1 pages score 25–70%.
   `templates.npz` was clustered from LP2 renders, so LP1 is outside the instrument's
   domain, and pooling the two overstates neither more than it understates.
2. The residual on 73/74 is **row segmentation**, not glyph identity — the reader emits 96
   and 109 glyphs where canon has 85 and 95 (vine ink and separator dots read as glyphs).
   On a cleanly isolated line the read is verbatim: page `05.jpg` returns `SOMEWISDOM`,
   `THEPRIMESARESACRED`, `THETOTIENTFUNCTIANISSACRED`, `ALLTHNGSSHOULDBEENCRYPTED` against
   canon `SOMEWISDOM`, `THEPRIMESARESACRED`, `THETOTIENTFUNCTIANISSACRED`,
   `ALLTHNGSSHOULDBEENCRYPTED`.

### C-2 — the control that actually governs this lane: **PASSES**

G-A measures whole-page transcription. The band task is different and narrower: read a
short, already-localised strip. `controls.py` plants `THEPRIMESARESACRED` by compositing
**real glyph bitmaps lifted from the verified renders** into band-shaped strips on P-9's own
length ladder (16 / 8 / 4 / 3 / 1 glyphs), then runs the identical band pipeline:

```
planted 16 glyphs  ->  read THEPRLMESARESACRE
planted  8 glyphs  ->  read DTHEPRLME
planted  4 glyphs  ->  read SARE
planted  3 glyphs  ->  read SAC
planted  1 glyph   ->  read R
C-2 recovery: 30 / 32 planted glyphs = 93.8%   (bar 90%)  -> PASS
```

So **the band nulls in §3 are meaningful**: the instrument demonstrably recovers a message
planted in exactly the shape being hunted.

One thing C-2 also proved, and it changed a detector: the **exact-substring** form of H1
**does not fire on a correctly recovered plant** — the two errors are a single `I→L`
substitution inside the confusable family R9 named. An exact detector that fails its own
positive control cannot be used to declare a negative, so H1 is run in the
**confusable-tolerant** form `H1′` (≤1 substitution, and that substitution must lie inside a
named confusable family — `fuzzy.py`). `H1′` fires on the plant. This is not a threshold
moved to fit a result; it is a detector repaired because its control failed, and the repair
is recorded with its justification.

### G-B — the RUNIC/NON-RUNIC discriminator has a measured false-positive rate

The cost bar (`median per-glyph template cost ≤ 300` ⇒ RUNIC) is calibrated on a known-text
median of **128**. It is **not** sufficient on its own: band `B098` — the p51 alphanumeric
line, known by construction to contain **no runes** — is called RUNIC at cost **251.5**. The
reader will emit plausible-cost runes for non-runic ink. That is why every band call in
`bands.json` carries its cost **and** a degeneracy figure, and why no hypothesis in §3 is
scored on a band call alone.

---

## 3. A-06 — hypothesis verdicts

`hypotheses.py` → `hypotheses.json`; `h1score.py` → `h1score.json`.
Corpus: 13,136 runes, 57 segments, **89 residual doublets**.
Candidates: 109 bands → 30 short (n ≤ 16) → **12 short AND called RUNIC**.

| # | hypothesis | pre-registered bar | measured | verdict |
|---|---|---|---|---|
| **H1** | a band decodes to an English word / known Cicada string of length ≥ 8 | any hit (confusable-tolerant, per C-2) | **0 hits** across 12 runic short bands | **FAIL** |
| **H1-quad** | a band's read beats its own size-matched null | score > null max over 2,000 draws from the LP2 rune frequency | 5 of 25 beat it — **all 5 are the DEGENERATE vine-stroke reads** (`JIIIIIII…`, z = 4.5–8.4, flagged before scoring). **0 non-degenerate bands beat their null.** | **FAIL** |
| **H2** | the same short band recurs at ≥ 3 sites and decodes consistently | ≥ 3 sites, identical content | **0** | **FAIL** |
| **H3** | band value = page index | ≥ 3 exact matches, p < 1.67e-4 | **1** exact | **FAIL** |
| **H4** | band value = prime index | ≥ 3 exact | **0** | **FAIL** |
| **H5** | band value = a checksum over that page's rune stream (12 forms) | ≥ 3 exact on one form, Bonferroni p < 8.3e-5 | best form: **2** | **FAIL** |
| **H6** | band values are a pointer/index into the page's own text or into the payload | ≥ 8-char English via the pointer, **or** doublet-landing p < 0.001 | 0 English hits; **0 / 12** pointers land on a residual doublet against a base rate of 0.0068 (binomial p = 1.0). The 256 base-60 bytes read as indices into the rune stream give nothing ≥ 8 chars. | **FAIL** |
| **H7** | band **lengths** are a binary ladder (1/3/4/8/16) | p < 0.001 | naive: 29/109 are 2ᵏ vs an all-bands base rate of 0.073, p = 6.7e-10 — **but that base rate is set by TEXT lines at n = 20–40, where powers of two are sparse.** Size-matched to small bands: **22/30 are 2ᵏ against an empirical base rate of 0.531 over all n ≤ 16 image bands, p = 0.019.** The ladder is an artifact of ornament bands being small. | **FAIL** |
| **H8** | band **positions** are a channel independent of content | p < 0.001 non-uniform, or a ≥ 8-char decode | KS uniformity rejects at p = 8e-11 (x) / 4e-5 (y) — **but a uniform-position null is physically impossible for marginal decoration, so rejecting it carries no information.** The presence-bit word `1111111111111111000000111011000001000001111111111111111` decodes to nothing. | **PASS on the letter of the statistic, uninformative** |
| **H8b** | are band coordinates unique per-page **data**, or a repeated **template**? | descriptive | 109 bands occupy only **58 distinct bounding boxes** and **45 distinct x-spans**; **69 of 109 share an exact box with another band**; the x-span `[28, 2372]` recurs **21 times**. | **template, not data** |

**Cross-check (PREREG I-4).** No candidate reached its own threshold, so nothing was
promoted to the confirmatory stage; the doublet cross-check is reported above as part of H6
(0/12, base rate 0.0068) and the segment-boundary cross-check found no band coordinate
aligned to a segment boundary beyond the page-template repetition H8b measures.

---

## 4. B-12 — line geometry and line fill

`linegeom.py` → `linegeom.json` (**616 text rows over 56 pages**, plus the canonical
per-line rune/word statistics); `linetests.py` → `linetests.json`.
Round 8's already-measured axes — inter-glyph **advance** (1.86 σ, unimodal) and **baseline
jitter** (BIC rejects two components) — are **not** re-run.

### (a) Two-state screen — 5 of 11 channels clear the pre-registered bar

| channel | n | separation | ΔBIC | stage (a) |
|---|---|---|---|---|
| row_height | 616 | **4.71 σ** | 2391 | PASS |
| body_per_line | 616 | **4.53 σ** | 824 | PASS |
| runes_per_line | 604 | **2.89 σ** | 394 | PASS |
| words_per_page | 57 | **2.62 σ** | 22.8 | PASS |
| lines_per_page | 57 | **2.12 σ** | 1433 | PASS |
| sep_per_line | 616 | 1.02 σ | 286 | fail |
| mean_sep_gap | 594 | 0.99 σ | 57.9 | fail |
| right_margin | 616 | 0.80 σ | 1739 | fail |
| fill_ratio | 616 | 0.53 σ | 1836 | fail |
| words_per_line | 604 | 0.30 σ | −3.5 | fail |
| left_margin | 616 | 0.00 σ | −19.3 | fail |

**Descriptive note (not a threshold change):** in every "PASS", the minority component is a
**fat tail, not a second state** — `row_height` is 92.8% at 114.5 px with sd **0.50** plus
7.2% at 131.6 px with sd **13.4**; `lines_per_page` is 61.4% at exactly **12.0 with sd
0.000** plus 38.6% at 8.36 with sd 2.76. That is the same shape Round 8 diagnosed for
micro-spacing ("the second component is a wide tail, sd 17.4, not a second state"). A 1-bit
channel needs two comparably tight states.

**Confound test.** Removing the last row of every page and every page with < 8 rows does not
kill the bimodality (`row_height` 4.71 → 7.90 σ), i.e. the tail is not only "last line of a
paragraph" — it is glyph-repertoire driven (rows containing an ascending/descending rune).

### (b) Bit decode — **all 8 channels FAIL**

Median-threshold → 8 packings (fwd/rev × 5-bit/8-bit) × 8 phases → English 4-gram score,
against a 2,000-draw size-matched shuffle null. Every channel scores **0** where the null's
own maximum is 1–3: **p = 1.000 for all eight.**

**And the decoder is validated.** C-3b plants real ASCII in the bit channel noise-free and
the same detector fires at **p = 0.0005 (PASS)** — so the eight nulls are silence from a
working instrument, not silence from a dead one.

### (c) Correlation with the rune stream — 1 of 24 clears Bonferroni, and it is explained

`runes_per_line ~ mean_rune_idx`: ρ = **−0.257**, p = 1.5e-10 (bar 3.7e-5).

The typesetter justified to a fixed column width, so a line packs *more* runes when its
runes are *narrower* — and rune index correlates with glyph width. Measuring the mean glyph
advance per rune class from the image itself and partialling it out:

```
runes_per_line ~ mean_rune_idx                 rho = -0.257  p = 1.5e-10
runes_per_line ~ mean GLYPH WIDTH              rho = -0.653  p = 8.3e-75
mean_rune_idx  ~ mean GLYPH WIDTH              rho = +0.367  p = 9.5e-21
PARTIAL runes_per_line ~ mean_rune_idx | width rho = -0.018  p = 0.66
```

The correlation **collapses to zero** once glyph width is controlled. It is typographic
justification, not a covert channel.

### C-3a — the line-fill channel's measured power ceiling

Planting a 64-bit message in `fill_ratio` at k × the channel's own measured sd:

| planted separation | GMM separation | bit recovery |
|---|---|---|
| 0.5 sd | 1.96 σ | 0.547 |
| 1 sd | 1.76 σ | 0.703 |
| 2 sd | 1.21 σ | 0.797 |
| 3 sd | 2.26 σ | 0.859 |
| 4–8 sd | 4.15–7.29 σ | 0.859 |

The GMM screen sees a planted two-state channel from **≈ 3 sd** upward. Median-threshold
bit recovery saturates at **0.859** because ASCII is not bit-balanced and a median threshold
mis-assigns the minority bit — a property of the pre-registered detector, stated rather than
patched. **So the B-12 negative is bounded: it excludes a line-fill channel with ≥ 3 sd
state separation, and says nothing below that.**

---

## 5. H9 (addendum) — the ink-tone channel: a real, discrete, previously unrecorded feature

Round 8's GEOMETRY track measured glyph **shape** (nearest-neighbour Hamming 0.0000),
**advance** (1.86 σ) and **baseline jitter** (BIC-rejected) and stopped. **Ink tone was
never measured.** `PREREG-ADDENDUM.md` registered it before the sweep.

The first detector (mean grey, mean/sd reference) **failed its own plant-and-recover control
at recall 0.05–0.10** — a handful of genuinely lighter glyphs inflate the very dispersion
they are tested against. Replacing the reference with median/MAD lifts recall to **1.00 at
ΔL = 2 grey levels**. That failure is recorded because it is exactly the failure mode this
repository exists to catch.

The clean statistic is **minimum grey**: a glyph printed solid black has at least one pixel
near 0 no matter how thin its strokes, while a glyph printed in a lighter tone has a floor
above 0 across its whole body — so it is almost free of the stroke-width confound.
`greyglyphs.py` → `greyglyphs.json`.

**Result.** Book-wide, the median component minimum-grey is **0.00**. Against that:

- **226 components at 25 sites on 16 pages** are set in a distinct lighter tone —
  minimum grey **44–51**, mean grey **57.4–57.6** at rune stroke weight and **63.7–69.9** at
  thinner weight. The tone is remarkably uniform, which is what a specified fill colour
  looks like and not what JPEG noise looks like.
- Most of those sites are **section headings and their drop-caps** (p0, p3×2, p6, p7, p8,
  p15, p23, p27, p33×2, p39, p40, p54) plus **three full grey text rows on p53**
  (y 1874–2365) and **single grey marks in the left margin of p36, p37×3, p38**.
- A further ~104 components with minimum grey 56–196 and mean 124–198 are **woodcut and
  vine antialiasing** (p9–p14, p22, p24–p26, p32, p55) and are excluded.

**The one element that is neither a heading, a drop-cap, nor a drawing:**

> On page 15, in the 4×4 numeric grid, the four digits of **`3299`** (box x 913–1149,
> y 1016–1094) have **minimum grey 47–51 and mean grey 68.1–69.1**, while **every other
> digit on that page has minimum grey 0.0** and mean 16–22. The lightening is uniform across
> all four glyphs and all 1,347–1,449 ink pixels of each — not a JPEG artifact.

`3299` is the prime immediately preceding 3301. **This lane makes no claim about what the
marking means.** What it establishes is the measurement, and that the measurement is absent
from every transcription in this repository and from both vendored community transcriptions
of that page (`data/scream314_lp.md:1595`, cmbsolver, libergo), all of which record the
digits and discard the tone.

Per the addendum's own rule, 25 sites is not "a channel" — a uniform tone used for headings
carries roughly one bit per heading and that bit says "this is a heading". It is reported as
an **annotated list of individual anomalies**, which is what the rule prescribes, and the
list is in `greyglyphs.json`.

---

## 6. Coverage

**Measured.**
- All **109** catalogued band records (union of Round 8's 62- and 47-row inventories),
  cropped from sha256-verified renders, physically classified, and read: **9,899 glyphs**
  with per-glyph match cost. → `bands.json`
- The **256 base-60 tokens** on pp. 49–51 transcribed and cross-checked against two
  independent vendored community sources; the p15 grid transcribed with its arithmetic.
  → `nonrunic.json`
- **8 pre-registered content hypotheses** + a quadgram-vs-null test on every short band.
  → `hypotheses.json`, `h1score.json`
- **11 line/page geometry channels** × 3 stages (bimodality / bit decode / correlation),
  with the justification-mediation test. → `linegeom.json`, `linetests.json`
- **Ink tone** over every component on all 56 pages. → `intensity.json`, `greyglyphs.json`
- Three positive controls: **C-2 band plant 93.8% PASS**, **C-3b decoder validation
  p = 0.0005 PASS**, **H9 tone plant recall 1.00 at ΔL = 2 PASS** (after the first
  detector failed and was repaired).

**Measured power (Doctrine R2).** Band reading: 93.8% glyph recovery on a planted message in
the exact target shape (C-2); 81.7–86.5% whole-page on LP2-typeface solved pages; 44.2%
pooled across all solved pages including the out-of-domain LP1 typeface. Line-fill: the
detector sees a planted two-state channel from ≈ 3 sd separation. Ink tone: ΔL ≥ 2 grey
levels with a robust reference, ΔL ≥ 30 with the min-grey detector.

## 7. Not covered

1. **Band content below the reader's resolution.** The band nulls hold at 93.8% glyph
   recovery on planted band-shaped text. A message hidden in ink that the template DP cannot
   segment at all — sub-rune marks, deliberate stroke modifications inside a vine — is
   outside this. Reopens if a per-rune reader reaches ≥ 99% on the solved control pages
   (P-1's unpark condition).
2. **H1's word list is finite.** H1′ tests 24 named English/Cicada strings plus a full
   quadgram-vs-null score. A message in Latin, Old English, or an abbreviated register would
   be invisible to both — this is the same **English-only** conditional that Round 18 L7-A
   found on every negative in this repository. Reopens with a multi-register scorer.
3. **The 256 bytes of pp. 49–51 are transcribed, not attacked.** This lane established that
   the repo's analysis tree never held them and put them in `nonrunic.json` with their
   base-60 derivation. Testing them as a key, a keystream, a seed or a payload is a
   different lane's work and is **not** done here.
4. **Line-fill separations below ≈ 3 sd** are below the detector's measured ceiling (C-3a).
5. **Ink tone: the p15 `3299` marking is measured, not interpreted.** Whether it points at
   3301, at a prime index, at a cell coordinate, or at nothing is untested.
6. **Only the bands Round 8 catalogued** were read. Round 8's rejection rule
   (`outside the text column OR median height > 240 px`) is itself a filter; ink that is
   neither in the text column nor rejected by that rule was never listed by anyone and is
   not listed here either. A from-scratch inventory of *all* non-body ink on all 56 pages
   would strictly extend this.
7. **Grey-tone sites were not read as text.** The 226 light components are located and
   measured; the three grey text rows on p53 and the grey heading lines were not separately
   transcribed and diffed against canon.

## 8. What reopens each item

- **A-06** reopens if (i) a per-rune reader reaches ≥ 99% on solved control pages and finds
  runic content in any band this lane called VINE/WOODCUT, or (ii) a multi-register scorer
  finds language in a short band's read that the English quadgram model cannot see, or
  (iii) anyone extends the inventory beyond Round 8's rejection rule (item 6 above).
- **B-12** reopens if a planted-signal detector is built with sensitivity below 3 sd on
  line-fill, or if a channel not in the eleven measured here (e.g. inter-line leading, which
  this lane did not measure) is proposed with a control.
- **H9** reopens on any interpretation of the `3299` marking that makes a falsifiable
  prediction, or if the grey text rows on p53 are transcribed and differ from canon.

---

## 9. Artifacts

| file | what it holds |
|---|---|
| `PREREG.md`, `PREREG-ADDENDUM.md` | pre-registration, thresholds, controls, Aiming Test |
| `inventory.py` → `inventory.json` | 109 band records **with y coordinates restored** |
| `crop.py` → `crops/` | 63 band crops + the 56-page contact sheet (gitignorable, regenerable) |
| `reader.py` | the shared band-reading code path (validated R9 template DP) |
| `calibrate.py` → `calibration.json` | gate G-A on cryptographically solved pages |
| `read_bands.py` → **`bands.json`** | **the durable artifact: every band read, 9,899 glyphs, with cost, degeneracy and ink class** |
| `nonrunic.py` → `nonrunic.json` | the 256 base-60 tokens + the p15 grid, cross-checked |
| `hypotheses.py` → `hypotheses.json` | H1–H8 + H8b against size-matched nulls |
| `h1score.py` → `h1score.json` | quadgram score vs per-band null |
| `linegeom.py` → `linegeom.json` | 616 text rows, 11 geometry channels |
| `linetests.py` → `linetests.json` | confound, bit decode, correlation, C-3 controls |
| `controls.py` → `controls.json`, `ctrl_page.png` | C-2 plant-and-recover, 93.8% |
| `fuzzy.py` | the confusable-tolerant matcher C-2 forced into existence |
| `intensity.py` → `intensity.json`, `greyglyphs.py` → `greyglyphs.json` | the ink-tone sweep |
| `ledger.json` | ledger-shaped entries for A-06 and B-12 |

---

## 10. Addendum — Round 19 lane C3, 2026-08-26

_Appended, not merged: §§1–9 above were completed by a concurrent Round-18 continuation and are
left exactly as written. C3 (`analysis/round19/C3/`) ran the same closeout independently, from the
same PREREG and the same inherited thresholds, and this section records only where C3 **adds**,
**converges with**, or **corrects** what is above. Full C3 record:
[`round19/C3/RESULTS.md`](../../round19/C3/RESULTS.md); machine summary
`round19/C3/out_l3_ornaments.json`; ledger fragments `round19/C3/ledger.json`._

### 10.1 Convergence — two independent controls, same answer

The two runs built **different** band-scale positive controls and got the same number.

| control | design | measured |
|---|---|---|
| **C-2** (§2 above) | real glyph bitmaps composited into band-shaped strips on P-9's length ladder (16/8/4/3/1) | **93.8 %** (30/32) |
| **G-A2** (C3) | band boxes around real text rows on the seven pages solved *by decryption*, read through the identical `read_bands.py` path, truth attributed against each page's **flat** canon stream | **95.6 %** on the LP2 face; **95.62 %** conditional on the reader's own `RUNIC` call (1 049/1 097 glyphs, 56 bands) |

Two plant designs, one composited and one drawn from genuine solved pages, agreeing at
**94–96 %**. The whole-page 44.2 % of gate G-A is confirmed as the wrong statistic for this lane,
by two routes.

C3 also measured the **specificity** side that neither G-A nor C-2 covers: 15 probes over ink
*known* not to be runes (blank margin, woodcut interiors, vine strokes) → **13/15 not called
RUNIC**. Combined with the known-rune bands at the same size, the two-sided table for objects of
**≤ 16 glyphs** is **sensitivity 0.50, specificity 0.50, PPV 0.75** (n = 16). That is the
quantitative form of §2's G-B warning: a short band called RUNIC is right about three times in four
and its glyphs are then essentially verbatim, while **a short band called NON-RUNIC carries no
information at all**. No band in either run is asserted to be decoration on the strength of a
failed read.

### 10.2 Correction — P-9's `n` is not a glyph count

§3 above, and P-9 itself, treat the catalogue's `n ≤ 16` set as "short bands". **`n` in
`ornaments.json` is a Round 8 row-group count, not a glyph count.** C3 re-measured the connected
components actually inside those same 30 boxes:

| | |
|---|---|
| component count across the 30 "short" boxes | **0 to 341** |
| boxes containing **no components at all** | 3 — B052 (p27), B055 (p33), B100 (p51) |
| boxes that are whole **multi-line text blocks** | 6 — B025, B028, B058, B089, B101, B106: **7–11 rows tall, up to 2 167 px high, 251–341 components** |
| genuinely tiny bands | B001/B005/B009 (1 component, 42 × 21 px, read `GI`/`G?` at degeneracy 0.50) and B048/B049 (1 component, 39 × 8 px) — single vine hairlines |

So the six largest members of P-9's "short" set are §1's class **T** — ordinary body text the
ornament heuristic rejected because a marginal vine merged rows. **P-9's candidate set does not
contain what P-9 believed it contained**, and the only members that really are ~16 short tokens are
**B096** (p50) and **B098** (p51), the base-60 blocks already corroborated in §1a.

This is the **same class of defect as the dropped `y` coordinate** §0 records in the same file:
the artifact's schema was never checked against what its consumers assumed it meant. Two schema
defects in one catalogue is the concrete reason §7's non-coverage statement should be read
strictly — the 109 records are the output of a rule now known to be defective, and they are not
the book's full inventory of non-text ink.

*(This does not disturb any verdict in §3. H1–H8 were negative and remain negative; what changes
is the description of the objects they were negative about, and the standing of P-9 as a parked
item — C3 files it `run / refuted at the premise`.)*

### 10.3 Second nulls for the two statistics that "passed"

§3's H7 and H8 rows already reject both on the right grounds. C3 built a different null for each
and reached the same place, which is worth recording because the two nulls fail in different ways.

- **H7.** §3 size-matches the base rate (22/30 vs 0.531 over all n ≤ 16 image bands → p = 0.019).
  C3 instead **held the data fixed and randomised the set**: 20 000 random six-element subsets of
  the observed length support capture **17.66 ± 7.40** of the 109 lengths against the binary
  ladder's 29, and **1 782 / 20 000 score ≥ 29 → p = 0.089**. C3 also ran a **decoy panel** showing
  the original null is invalid for *every* set, not just the ladder: triangular numbers score
  p = 8.9e-22, Fibonacci 1.4e-15, and **six integers drawn at random from 1..32 score p = 1.7e-06**
  — two orders of magnitude past the family bar. Same verdict, **FAIL**, by a second route.
- **H8.** §3 rejects it as "uninformative" on the physical argument that marginal decoration
  cannot be uniform. C3 measured that argument: the **identical KS test on the 616 ordinary text
  rows** of `linegeom.json` rejects uniformity at **p = 3.3e-112**, against the bands' 8.2e-11 —
  a hundred orders of magnitude *more* strongly. The registered threshold fires on ordinary
  typeset text, so it is **not discriminating**, and that is now a number rather than a
  disposition.

### 10.4 Where §5 is better than C3's own H9 work — recorded plainly

Both runs independently found the same instrument defect and the same fix: the mean/sd reference
**fails its own plant** (recall 0.05–0.10, including at a lightening of 40 grey levels, because the
planted components inflate the very dispersion they are tested against), and replacing it with
**median/MAD** lifts recall to **1.00 at ΔL = 2 grey levels**. Two independent derivations of the
same failure and the same repair.

From there §5 goes further and better. C3 continued with **mean** grey and got a flag rate of
**8.12 %** of all ink (1 504 of 18 514 components), which it could only report as *partially
explained* by render geometry (pooled AUC 0.709 for height, 0.707 for stroke width) — an honest
number that settles nothing. **§5's switch to minimum grey is the better statistic and it does
settle it**: a solid-black glyph has at least one near-0 pixel however thin its strokes, so the
floor is nearly free of the stroke-width confound. That yields a clean, discrete population —
**226 components at 25 sites on 16 pages** at a uniform lighter tone, mostly section headings and
drop-caps — which is what a specified fill colour looks like and what C3's mean-grey AUC could not
resolve. **§5 supersedes C3 §3.4 on this point.**

**One residual guard C3 can add to §5's `3299` result.** §5 argues the lightening is not a JPEG
artifact from *within-render* evidence — uniformity across all 1 347–1 449 ink pixels of each of
the four glyphs, and the same tone recurring at 25 unrelated sites. That is strong, and C3's own
mean-grey measurement agrees on the magnitude (**+51.2 grey levels, z ≈ 92** against a
stroke-and-height-matched reference, where the next-lightest digit on p15 is at z = 13.08).
The guard is that **no second render exists in this repository to test it against**: C3 checked,
and the only other page-15 render — vendored 2014 asset `32.jpg` — is **byte-identical by sha256**
(`5543cfce96493b86…`) to `data/relikd/p15.jpg`. The same file, not a second encode.

So the honest joint statement is: *the lightening is a real, uniform, systematic feature of this
render, almost certainly a specified fill colour rather than compression noise — and confirming it
as a property of the* **document** *still wants one independent render.* That remains the cheapest
open item either run leaves, and either answer is worth having.

### 10.5 What C3 files to the ledger

| item | status | one line |
|---|---|---|
| **A-06** | `run` | 109/109 bands read; H1–H8 all negative after controls; the catalogue that framed them carries two schema defects |
| **B-12** | `run` | line geometry genuinely two-state (`row_height` 7.90 σ after confounds) but **not** decodable — 8/8 bit channels at p = 1.0 with a decoder validated at p = 0.0005, and a measured **85.9 % power ceiling**; the one surviving correlation is fully explained by glyph width (partial ρ = −0.018, p = 0.661) |
| **P-9** | `run` — **refuted at the premise** | the `n ≤ 16` set is not a glyph-count set (§10.2) |

Fragments: `round19/C3/ledger.json`. Trust anchor before and after C3: **ALL VALIDATIONS PASSED
(5/5)**.
