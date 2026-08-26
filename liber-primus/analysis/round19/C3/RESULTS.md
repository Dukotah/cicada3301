# C3 — CLOSEOUT of Round 18 L3 (ORNAMENTS) and L8 (PROVENANCE) · RESULTS

_Round 19, Phase 3. Pre-registration: [`PREREG.md`](PREREG.md), written before any C3
measurement was scored. Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Trust anchor, before the lane:** `python3 liber-primus/tests/validate.py` →
`ALL VALIDATIONS PASSED — rig reproduces known solves.` (5/5: 01, 03, 05, 06, 14.)
**After the lane:** see §7.

---

## Headline

| item | ledger | result |
|---|---|---|
| **1. Ornament bands** | **A-06**, **B-12**, parked **P-9** | **All 109 bands read.** They are **decoration and mis-grouped body text**, and that is now a measurement rather than an assumption. **P-9's premise is refuted**: the `n ≤ 16` field it called "the only real candidates" is **not a glyph count** — those 30 boxes hold between **0 and 341** components. H1–H8 are **all negative after controls**; the two that "passed" are killed by controls this lane added. |
| **1b. Band-reader power** | new, gate **G-A2** | Round 18 could not say what its silence was worth. Now measured: on the **LP2 typeface** — the face of all 56 target pages — the band reader recovers **95.6 %** of known runes (172/180 glyphs). Conditioned on its own `RUNIC` call, **95.6 %** (1049/1097). **But the `RUNIC` call itself is a coin-flip at ≤ 16 glyphs** (sensitivity 0.50, PPV 0.75), which is exactly the size class P-9 nominated. |
| **1c. H9, ink tone** | addendum #1 | Round 18's H9 detector **failed its own plant at every level up to ΔL = 40 grey levels**. Diagnosed (the plant inflated its own null) and **repaired**: recall now **1.000 at ΔL = 2**. Re-measured. |
| **1d. page 15** | new | The `3299` grey anomaly is **quantified**: four adjacent digit components, one row, **+51.2 grey levels** at **z ≈ 92** against a stroke-and-height-matched reference, where every other digit on the page sits at z ≤ 13. **Not yet established as a property of the document** — the repo holds no second render (§3.5). |
| **2. PGP table** | corpus **G-02** | **Independently re-derived from scratch.** On the **228 files both runs saw, the verdicts are identical, file for file, and so is every sha256** — 192 PASS / 3 FAIL / 22 NO-SIG / 11 KEY, one signing key ID. All four controls met in the independent run, **including C2 (tamper ⇒ BADSIG) and C3 (foreign key ⇒ no GOODSIG)**. |
| **2b. L1 cross-check** | **FOUND-ERROR** | L1's `GnuPG v1.4.11 (GNU/Linux)` **46/46** is wrong in its denominator and its span. That directory holds **56** PASSing files / **54** distinct messages running to **2017**, and carries **three** version strings: **53 × 1.4.11, 2 × `GnuPG v1`, 1 × `CicadaPG v.3301`**. L1's conclusion survives; its numbers do not. **The toolchain changed twice, not once.** |
| **2b′. R1 convergence** | **FOUND-ERROR, twice** | Round 19's **R1** reached the same defect in L1's prior from the *render* side — a non-ImageMagick chain reproduces all four discriminating JPEG fields, and GnuPG 1.4.11 shipped in ≥ 6 OS generations including **Ubuntu 12.10, outside L1's bracket** (`round19/R1/RESULTS.md` §C). Two lanes, two independent evidence bases, one conclusion. §6.5b. |
| **2c′. The Perl fact** | new, high value | R1 spotted that a 2012 message names **"the Crypt::RSA Perl module available in CPAN"**. C3 answers the question that makes it load-bearing: **it PASSes.** Two distinct messages (2012-01-15, 2014-01-06), four files, **all PASS**, carrying the prose claim, the library's own `Version: 1.99` / `Scheme: Crypt::RSA::ES::OAEP` armor, **and Perl `Data::Dumper` output**. A signed, dated, self-declared Perl environment — strictly stronger than any distro inference, and **G2's prior should be re-sourced to it**. §6.6. |
| **2d. I-03** | **I-03** | Round 18's mailing-list negative **covered nothing**. metzdowd holds **1 of 13** months of the window; cypherpunks holds **0**, and its `http=000` was an **expired TLS certificate plus a dead endpoint**, not an empty archive. C3 also closed the lane's own reopening condition #2 — **bitcointalk upgraded from `reported` to `verified`** via a real full-text index; **no hit**, and `845145127` / `futhorc` / the onion string have **zero occurrences there, ever**. §7. |
| **2e. I-01** | **I-01** | Round 18's **INDECISIVE** verdict stands and is **not** disturbed by §5's finding (§5.4). |

---

# ITEM 1 — L3 ORNAMENTS

## 1. Instrument first: gate G-A2, the band-shaped control

### 1.1 Why Round 18's number could not answer the question

Round 18's gate G-A read seven **whole solved pages** and scored **44.2 %** pooled per-glyph
agreement against a 90 % bar — a FAIL. That number is correct and it is the wrong instrument
statistic for this lane, in both directions:

- it **understates** the reader on its target set, because it pools five LP1 pages whose
  typeface is outside the template domain with the two LP2 pages that share the target set's face;
- it **overstates** the difficulty of a band read, because a whole page is read as one long
  stream in which one dropped glyph shifts everything after it.

So C3 registered **G-A2** (`PREREG.md` §0.1) and ran it: plant band-shaped boxes of **known**
content and push them through the identical code path `read_bands.py` uses on real bands.

### 1.2 The plant

Every image text row on all seven pages whose plaintext is known **by decryption**, turned
into a band record and read through the band path. 64 control bands, 1 198 glyphs.

Ground truth is attributed against each page's **flat** canonical rune stream, not line by
line, because the corpus breaks lines **semantically** and the image breaks them
**typographically** — a fact Round 18 already recorded in `calibrate.py`'s docstring. Matching
band *i* to canon line *i* measures the transcriber's paragraph breaks: on page 05 the image's
first row genuinely carries `SOMEWISDOM · THEPRIMESARESAC` and the second genuinely begins
`RED`. C3's first pass made exactly that error and scored 38 % before the attribution was
corrected to the method registered in `PREREG.md` §0.1.

### 1.3 What it measures

| page | face | bands | glyphs read | canon | matched | agreement | precision |
|---|---|---:|---:|---:|---:|---:|---:|
| `73.jpg` = LP2 p56 (solved) | **LP2** | 5 | 85 | 85 | 83 | **97.65 %** | 97.65 % |
| `74.jpg` = LP2 p57 (solved) | **LP2** | 5 | 95 | 95 | 89 | **93.68 %** | 93.68 % |
| `01.jpg` A WARNING | LP1 | 11 | 212 | 184 | 173 | 81.60 % | 81.60 % |
| `03.jpg` WELCOME | LP1 | 13 | 273 | 394 | 237 | 60.15 % | 86.81 % |
| `05.jpg` SOME WISDOM | LP1 | 6 | 86 | 157 | 79 | 50.32 % | 91.86 % |
| `06.jpg` A KOAN | LP1 | 13 | 215 | 742 | 186 | 25.07 % | 86.51 % |
| `14.jpg` A KOAN (circumference) | LP1 | 11 | 232 | 319 | 219 | 68.65 % | 94.40 % |
| **pooled** | | **64** | **1 198** | | **1 066** | **53.95 %** | **88.98 %** |

**Gate G-A2 against the inherited 90 % bar: pooled FAILS at 53.95 %.** That is the number that
governs, and it is stated first.

Three things about it that are measurements, not excuses:

1. **The split is by typeface, and it is large.** The two LP2 pages — the face of every one of
   the 56 target pages — score **97.65 %** and **93.68 %**, pooling to **95.56 %**, *above* the
   bar. The five LP1 pages pool to 42.6 %. `templates.npz` was clustered from LP2 renders.
2. **Agreement and precision are different failures.** On LP1 the reader's *precision* is
   86–94 % — what it emits is mostly right — while its *agreement* collapses because it emits
   far fewer glyphs than the canon holds (86 read against 157 on page 05). That is a **recall**
   failure, not a substitution failure. For reading a band, precision is the governing quantity.
3. **The residual on the LP2 pages is not glyph identity.** Round 18's whole-page pass matched
   the same **83** glyphs on `73.jpg` but emitted **96** where canon has 85; restricting the box
   to rune-height components removes 11 spurious glyphs and nothing else. Round 18's own
   diagnosis — "the residual is row segmentation, not glyph identity" — is now measured: same
   matches, fewer false glyphs, 86.46 % → 97.65 %.

### 1.4 Specificity — the half Round 18 never measured

A reader that calls everything runic has perfect sensitivity and no information. 15 probes over
ink **known not to be runes** (woodcut interiors, vine-margin strokes, blank margin):

| probe class | n | not called RUNIC |
|---|---:|---:|
| blank margin | 8 | 8/8 (all `EMPTY`) |
| woodcut interior | 7 | 5/7 |
| **total** | **15** | **13/15 = 86.7 %** |

The two false positives are **p2** (7 glyphs, reads `AECGEOLSC`) and **p14** (5 glyphs, reads
`XTEO?I`). Both are ≤ 7 glyphs. That is not a coincidence, and §1.5 is why it matters.

### 1.5 The finding that governs everything below

Stratifying by the reader's own `RUNIC` call — a rule whose two constants (`cost_median ≤ 300`,
`degeneracy < 0.60`) were fixed in Round 18 before any band was read, though the decision to
*report* along this axis is post-hoc and is disclosed as such:

| stratum | bands | glyphs | per-glyph precision |
|---|---:|---:|---:|
| called **RUNIC** | 56 | 1 097 | **95.62 %** |
| called **NON-RUNIC** | 8 | 101 | 16.83 % |
| LP2 face (all called RUNIC) | 10 | 180 | **95.56 %** |
| **≤ 16 glyphs, called RUNIC** | 6 | 54 | **100.00 %** |
| **≤ 16 glyphs, not RUNIC** | 6 | 40 | 5.00 % |

So *conditional on the `RUNIC` call*, a band read is trustworthy — 95.6 % overall, and 54/54 on
the short ones. **But the call itself is weak precisely where P-9 wanted to use it.** The
two-sided table for objects of ≤ 16 glyphs, combining the known-rune bands with the known-non-rune
probes of the same size:

|  | called RUNIC | called other |
|---|---:|---:|
| known **rune** ink | 6 | 6 |
| known **non-rune** ink | 2 | 2 |

**sensitivity 0.50 · specificity 0.50 · positive predictive value 0.75** (n = 16).

**The bound this lane is allowed to state:** at ≤ 16 glyphs, a `RUNIC` call is right about three
times in four, and when it is right the glyphs are essentially verbatim; a `NON-RUNIC` call at
that size **carries no information at all** — it is as likely to be misread runes as decoration.
Any claim of the form "this short band is decoration because it did not read as runes" is
therefore **unsupported by this instrument**, and no such claim is made below.

**Kill condition (PREREG Q5): not met.** The lane's stop rule was ≥ 50 % of known non-rune ink
called RUNIC; measured 13.3 %. The lane continued.

## 2. The 109 bands, read

All 109 catalogued band records read end to end (`l3/bands.json`; Round 18's run stopped at 45).

| call | bands | | ink class | bands |
|---|---:|---|---|---:|
| RUNIC | 74 | | TEXT | 82 |
| NON-RUNIC | 27 | | DOT/HAIRLINE | 10 |
| DEGENERATE | 8 | | MIXED | 6 |
| | | | ALPHANUMERIC? | 5 |
| | | | EMPTY | 3 |
| | | | WOODCUT/DROPCAP | 2 |
| | | | VINE/WOODCUT | 1 |

### 2.1 P-9 is refuted, and by a field-definition error

P-9 nominated "the 30 bands with **n ≤ 16 glyphs**" as "the only real candidates". **`n` in
`ornaments.json` is not a glyph count.** Re-measuring the component count inside the same boxes:

| band | page | `n` reported | components actually in the box | box h × w | rows | glyphs read |
|---|---:|---:|---:|---|---:|---:|
| B052 | 27 | 3 | **0** | 86 × 1071 | 1 | 21 |
| B055 | 33 | 1 | **0** | 74 × 230 | 1 | 27 |
| B100 | 51 | 8 | **0** | 49 × 2344 | 1 | 43 |
| B001/B005/B009 | 0/1/2 | 1 | 1 | 42 × ~21 | 1 | 2 |
| B096 | 50 | 16 | 16 | 69 × 1043 | 1 | 30 |
| B098 | 51 | 16 | 16 | 48 × 997 | 1 | 39 |
| B025 | 8 | 15 | **251** | 1565 × 1749 | 7 | 162 |
| B028 | 9 | 16 | **257** | 1567 × 1686 | 7 | 162 |
| B106 | 54 | 14 | **292** | 2034 × 2344 | 11 | 342 |
| B101 | 52 | 13 | **325** | 2034 × 2344 | 11 | 231 |
| B058 | 40 | 15 | **326** | 2167 × 2344 | 11 | 245 |
| B089 | 48 | 14 | **341** | 2034 × 2344 | 11 | 237 |

The "≤ 16 glyph" set spans **0 to 341** components. Six of its members are **whole multi-line
text blocks 7–11 rows tall and up to 2 167 px high** — Round 18's class **T**, ordinary body text
that the ornament heuristic rejected because a marginal vine merged several rows into one band.
Three contain **no components at all**.

The bands that really are tiny are **B001/B005/B009** (1 component, 42 × 21 px, reading `GI` /
`G?` at degeneracy 0.50) and **B048/B049** (1 component, 39 × 8 px). Those are single vine
hairlines, and per §1.5 the instrument cannot distinguish them from misread runes at that size.

**So P-9's candidate set does not contain what P-9 believed it contained, and it never did.**
This is recorded as a **field-definition error in the Round 8 catalogue**, alongside the dropped
`y` coordinate Round 18 found in the same file. Both are the same class of defect: the artifact's
schema was never checked against what its consumers assumed it meant.

### 2.2 The only short bands with real, corroborated content

**B096** (p50, 16 components) and **B098** (p51, 16 components) are the alphanumeric base-60
token blocks. Their reads are **byte-for-byte confirmed by two independent community
transcriptions already vendored in this repo**
(`cmbsolver-lpviewer/files/text/lb/50.txt` and `libergo/cmd/base60/base60numbers.txt`,
`IDENTICAL` to each other):

```
p50 line 1   2M 0w 3L 3D 2r 0S 1p 15
p51 line 1   28 2a 0J 1L 0c 3C 2o 0X
```

These are **16 characters, not 16 runes** — eight two-character `[0-4][0-9A-Za-z]` tokens.
Round 18 established this; C3 confirms it on the completed read. **256 tokens over pp. 49–51,
values 0–255, 161 distinct against 162.0 expected under uniform i.i.d., not a permutation of
0–255** (`l3/nonrunic.json`). Any hypothesis treating these as a 16-rune Gematria string is
testing the wrong object.

## 3. Hypothesis verdicts

### 3.1 H1–H6 — negative, and the register conditional on H1

| id | hypothesis | measured | verdict |
|---|---|---|---|
| **H1** | ≥ 8-char English / known-Cicada string in a runic short band | **0 hits** over 12 short RUNIC bands | FAIL |
| **H2** | content recurring at ≥ 3 sites | **0** | FAIL |
| **H3** | band value == page index | 1 exact (bar: ≥ 3 and p < 1.67 × 10⁻⁴) | FAIL |
| **H4** | band value == prime index | 0 exact | FAIL |
| **H5** | band value == a page checksum (12 forms) | best form 2 exact (bar ≥ 3, Bonferroni p < 8.3 × 10⁻⁵) | FAIL |
| **H6** | bands are pointers/indices | 0 English hits; **0 of 12** pointers land on one of the **89** residual doublets (base rate 0.0068, binomial p = 1.0) | FAIL |

**H1 carries the register conditional and the others do not.** H1's recognizer is an
English-plus-known-Cicada-string matcher. Per Round 18 L7-A that register scores 0.33 for Latin
and **0.00** for vowel-dropped English. A short band holding Latin, Old English or abbreviated
English would very likely be scored as noise by H1, and H1's negative is an **English-register**
negative. H2–H6 are numeric/positional and register-free.

### 3.2 H7 — "passed", then died under its control

`hypotheses.py` reports **29 of 109** band lengths on the binary ladder {1,2,4,8,16,32} against a
base rate of 0.0728 taken over all 646 image bands → **p = 6.74 × 10⁻¹⁰**, clearing the family
bar by six orders of magnitude. It was the only content PASS in the family.

**Decoy panel (`l3/h7_control.py`).** Score the same 109 lengths against six other six-element
integer sets:

| set | members | hits | p vs the same null |
|---|---|---:|---:|
| binary ladder | 1 2 4 8 16 32 | 29 | 6.74 × 10⁻¹⁰ |
| triangular | 1 3 6 10 15 21 | 27 | **8.88 × 10⁻²²** |
| squares | 1 4 9 16 25 36 | 26 | 4.13 × 10⁻⁷ |
| Fibonacci | 1 2 3 5 8 13 | 21 | 1.41 × 10⁻¹⁵ |
| **six integers drawn at random from 1..32** | 3 5 13 14 16 22 | 16 | **1.70 × 10⁻⁶** |
| multiples of 3 | 3 6 9 12 15 18 | 8 | 5.85 × 10⁻⁴ |
| primes | 2 3 5 7 11 13 | 6 | 1.27 × 10⁻³ |

**A set of six integers drawn at random clears the family bar by two orders of magnitude.** The
null is invalid: the 109 records are exactly the bands Round 8's rule *rejected*, that rule
prefers short things, and small integers are mechanically rich in any "special" set.

**Set-randomisation test (`l3/h78_controls.py`, C-H7c)** — the correct null holds the data fixed
and randomises the set. 20 000 random six-element subsets of the observed length support:

- binary ladder captures **29** of 109;
- random sets capture **17.66 ± 7.40**, median 17, p95 **31**, max 52;
- **1 782 of 20 000 random sets score ≥ 29 → p = 0.089.**

**H7 after controls: NEGATIVE.** The apparent 6.7 × 10⁻¹⁰ is a reference-class artifact.

### 3.3 H8 — "passed" against a threshold that is not discriminating

`hypotheses.py` rejects uniformity of band positions at KS **p = 8.2 × 10⁻¹¹** (x) and
3.97 × 10⁻⁵ (y), clearing the registered bar. Control **C-H8b** runs the identical test on the
**616 ordinary text rows** in `linegeom.json`, which nobody claims carry a covert channel:

| population | n | KS x | KS y |
|---|---:|---:|---:|
| catalogued bands | 109 | 8.20 × 10⁻¹¹ | 3.97 × 10⁻⁵ |
| **ordinary text rows** | 616 | **3.32 × 10⁻¹¹²** | 3.58 × 10⁻¹¹ |

Ordinary typeset text rejects uniformity **a hundred orders of magnitude more strongly** than the
bands do. A page of text sits in a column; it is not uniform over the page. **H8 after controls:
NEGATIVE**, and the registered threshold is recorded as **not discriminating** so that nobody
re-runs it expecting it to mean something.

**No claim of a hit survives in the H1–H8 family.**

### 3.4 H9 — the detector was broken; repaired, then re-measured

**The Round 18 detector failed its own plant at every level.** `intensity.py`'s positive control
lightens K = 40 random body components by ΔL and requires ≥ 90 % recovery:

| ΔL (grey levels) | 2 | 5 | 10 | 20 | 40 |
|---|---:|---:|---:|---:|---:|
| recall | 0.050 | 0.025 | 0.050 | **0.000** | 0.100 |

It cannot recover a lightening of **40 grey levels**, which is obvious to the eye. Its 1 098
reported outliers were therefore uninterpretable in both directions.

**Diagnosis.** `detect()` estimates the page's body-text mean and sd from a set that **includes**
the planted components. Body ink here is nearly saturated (median grey ≈ 0.6, MAD-σ ≈ 0.19), so
lifting 40 of ~270 body components by 40 levels drags the mean up ~6 and inflates the sd from
~1.4 to ~15. A planted component's z becomes 40/15 = 2.7 — under the 4 σ bar it is meant to trip.
**The plant destroyed its own null.**

**Repair (addendum #2, `l3/intensity2.py`).** The addendum's *rule* is kept verbatim — outlier
iff mean grey exceeds the page body-text distribution by > 4 σ, with a stroke-width-and-height-matched
re-test. Only the *estimator* changes: median and 1.4826 × MAD replace mean and sd. Both estimate
the same quantity for a clean Gaussian; MAD has a 50 % breakdown point, so a 15 % contamination
cannot move it. **This is a repair to the instrument, not a relaxation of the bar**, and it is
filed here rather than edited into the addendum.

**Repaired control:** recall **1.000** at ΔL = 2, 5, 10, 20 and 40, with 21–22 false positives.
**Smallest recoverable ΔL: 2 grey levels.** The channel is now measured with essentially full
power down to a 2-level difference.

**Re-measurement.** 18 514 components book-wide; 2 039 candidates at > 4 MAD-σ; **1 504 survive
the stroke-and-height-matched re-test — 8.12 % of all ink.**

8.12 % of ink is not a covert message, and the addendum has no clause for it (its clauses cover
"< 10 book-wide ⇒ anomaly list" and "beats a size-matched null ⇒ channel"). So C3 registered the
discriminating question in `l3/h9_verdict.py` before running it: **is being flagged predicted by
how the component was rendered?** Pooled AUC of "is flagged" from geometry alone:

| feature | height | stroke-width proxy | area | width | aspect |
|---|---:|---:|---:|---:|---:|
| AUC | **0.709** | 0.707 | 0.687 | 0.606 | 0.282 |

Against the bars fixed in advance (≥ 0.80 render artifact, ≤ 0.60 unexplained): **0.709 →
PARTIALLY EXPLAINED. The number is reported and no claim is made.** Render geometry explains a
substantial part of the flagging and does not explain all of it, and this lane does not have the
evidence to close the gap.

**H9 status: the channel is now measurable (that is the contribution), and C3's own mean-grey
statistic does NOT resolve it.** The 8.12 % flag rate is partly predicted by stroke geometry and
partly not.

> **Superseded, 2026-08-26.** A concurrent Round-18 continuation reached the *same* detector defect
> and the *same* median/MAD repair independently, then went further with a better statistic:
> **minimum** grey rather than mean. A solid-black glyph has at least one near-0 pixel however thin
> its strokes, so the floor is nearly free of the stroke-width confound that left C3's AUC at 0.709.
> That yields a clean, discrete result C3's statistic could not: **226 components at 25 sites on 16
> pages** at a uniform lighter tone — mostly section headings and drop-caps, which is what a
> specified fill colour looks like. See `round18/L3-ornaments/RESULTS.md` §5. **It supersedes this
> subsection**, and under the addendum's own "< 10 book-wide ⇒ anomaly list" logic, 25 sites is
> reported there as an annotated list rather than as a channel. C3's contribution here is the
> diagnosis and repair of the control, which both runs made.

### 3.5 Page 15 — the `3299` anomaly, quantified

The observation that prompted addendum #1 is now a number. Page 15's 68 digit-height components
have median grey **10.06** with MAD-σ **0.546**. The four lightest are:

| box | size | mean grey | z |
|---|---|---:|---:|
| 913–958 × 1016–1094 | 45 × 78 | 60.13 | **91.67** |
| 974–1022 × 1016–1093 | 48 × 77 | 61.24 | **93.71** |
| 1035–1086 × 1016–1094 | 51 × 78 | 60.38 | **92.13** |
| 1097–1148 × 1016–1094 | 51 × 78 | 60.36 | **92.10** |
| *(next-lightest digit on the page)* | 21 × 76 | 17.20 | 13.08 |

**Four adjacent digit glyphs, on one row, at +51.2 grey levels — z ≈ 92 — where every other digit
on page 15 sits at z ≤ 13.** They are the same height and width as their neighbours, so the
stroke-width-and-height-matched re-test cannot explain them, and the repaired detector recovers a
planted 2-level lightening at recall 1.000, so a 51-level difference is 25× inside its power
envelope. Four adjacent glyphs is the width of a four-digit number, consistent with the `3299`
entry of the 4×4 grid.

**What this is NOT.** A JPEG is not a document. `l3/p15_second_render.py` looked for a second,
independent render: the vendored 2014 asset `32.jpg` is **byte-identical by sha256**
(`5543cfce96493b86…`) to `data/relikd/p15.jpg` — the same file, not a second encode. **So the
anomaly is established as a property of this render and is not yet established as a property of
the Liber Primus.**

> **Strengthened, 2026-08-26.** The concurrent run measured the same four glyphs on the cleaner
> **minimum-grey** statistic: **min grey 47–51** where **every other digit on page 15 has min grey
> 0.0**, uniform across all 1 347–1 449 ink pixels of each glyph, and the same tone recurs at 25
> unrelated sites book-wide. Compression noise does not produce a uniform floor across an entire
> glyph body, still less the same floor at 25 unrelated sites. So the lightening is a **real,
> systematic feature of this render — almost certainly a specified fill colour**, not an encode
> artifact. It also notes `3299` is **the prime immediately preceding 3301**.
> C3's byte-identity check still stands as the residual guard: confirming it as a property of the
> *document* rather than of this render wants one independent render, and this repository holds
> none. The joint statement is in `round18/L3-ornaments/RESULTS.md` §10.4.

> **Reopening condition (the cheapest open item this lane leaves):** obtain a second independent
> render of page 15 — a different mirror's JPEG, a PNG, or the original PDF — and re-measure the
> four component boxes listed above. If the +51-level difference reproduces, it is in the
> document and the community transcriptions have been discarding a real typographic mark. If it
> does not, it is an artifact of this encode. Either answer is worth having and neither is
> expensive.

## 4. B-12 — line geometry

`l3/linegeom.py` → **616 text rows over 56 pages**. `l3/linetests.py` completes the three stages
Round 18 left unfinished.

**Stage a — bimodality** (bar: separation ≥ 2.0 σ **and** ΔBIC > 10). Five of eleven channels
clear it: `row_height` (4.71 σ), `body_per_line` (4.53 σ), `runes_per_line` (2.89 σ),
`words_per_page` (2.62 σ), `lines_per_page` (2.12 σ). `fill_ratio`, both margins, `sep_per_line`,
`mean_sep_gap` and `words_per_line` fail.

**Stage 0 — the confound.** The obvious non-covert explanation is the last line of a paragraph
(short) and the short section pages. Removing them:

| channel | all | last-lines removed | + short pages removed |
|---|---:|---:|---:|
| `row_height` | 4.71 σ | 6.97 σ | **7.90 σ** |
| `body_per_line` | 4.53 σ | 4.13 σ | 3.93 σ |
| `runes_per_line` | 2.89 σ | 2.52 σ | — |
| `fill_ratio` | 0.53 σ | 0.32 σ | — |

The bimodality **survives** the confound and strengthens for `row_height`. So there really are
two row-height states in this book. That is a fact about the typesetting, and stages b and c ask
whether it carries anything.

**Stage b — bit decode** (bar p < 0.001 vs a size-matched shuffle null). All eight channels
score **0** against null means of 0.0–0.1 → **p = 1.0000, FAIL, every one.**

**Stage c — correlation with the rune stream** (Bonferroni p < 3.7 × 10⁻⁵). Exactly one of 24
correlations clears: `runes_per_line ~ mean_rune_idx`, ρ = −0.257, p = 1.47 × 10⁻¹⁰. It is
**explained, not covert**:

| relation | ρ | p |
|---|---:|---:|
| `runes_per_line ~ mean_rune_idx` | −0.257 | 1.47 × 10⁻¹⁰ |
| `runes_per_line ~ mean GLYPH WIDTH` | **−0.653** | 8.26 × 10⁻⁷⁵ |
| `mean_rune_idx ~ mean GLYPH WIDTH` | +0.367 | 9.49 × 10⁻²¹ |
| **partial** `runes_per_line ~ mean_rune_idx \| width` | **−0.018** | **0.661** |

Controlling for mean glyph width the correlation vanishes. Wider runes ⇒ fewer runes per justified
line. That is a typesetter, not a channel.

**Control C-3 — the two halves that make the negative real.**

*C-3a, power ceiling.* Plant a known 64-bit message in `fill_ratio` at k × sd separation and
measure bit recovery (bar ≥ 95 %):

| planted separation | 0.5 sd | 1 sd | 2 sd | 3 sd | 4 sd | 6 sd | 8 sd |
|---|---:|---:|---:|---:|---:|---:|---:|
| bit recovery | 0.547 | 0.703 | 0.797 | 0.859 | 0.859 | 0.859 | **0.859** |

**Recovery saturates at 0.859 and never reaches the bar, even at 8 sd.** So the `fill_ratio`
channel's negative is bounded at a **85.9 % power ceiling** — a message written there at any
separation would lose ~14 % of its bits to line-geometry quantisation.

*C-3b, decoder validation.* Plant real ASCII in the bit channel noise-free: the bit-decoder
recovers it at **p = 0.0005 → PASS**. **The decoder works.** Combined with C-3a: the stage-b
failure is a property of the *channel*, not of the *decoder*, and that is the distinction that
makes the eight FAILs mean something.

**B-12 verdict: NEGATIVE, with a stated power ceiling.** Line geometry in the Liber Primus is
genuinely two-state in `row_height` (7.90 σ after confounds), that two-state structure is
**not** decodable as bits (8/8 fail at p = 1.0 with a validated decoder), and the one surviving
correlation is fully accounted for by glyph width.

## 5. Item-1 coverage × power, and what is not covered

**Coverage.** 109/109 catalogued band records read (Round 18: 45). 30/30 of P-9's nominated set
re-measured. 256/256 base-60 tokens. 616/616 text rows. 18 514 components for H9. 64 control
bands / 1 198 glyphs for G-A2. 15 specificity probes. 20 000 set-randomisation draws for H7.

**Power.** Band reads: **95.6 %** per-glyph precision on the LP2 face and conditional on the
`RUNIC` call; **100 %** on ≤ 16-glyph bands *given* a RUNIC call — but the RUNIC call at that size
has **sensitivity 0.50, PPV 0.75 (n = 16)**. H9 detector: recall **1.000 at ΔL = 2**. B-12
bit-channel: ceiling **0.859**, decoder validated at p = 0.0005. Pooled G-A2 **FAILS** the
inherited 90 % bar at 53.95 %.

**The three conditionals on every negative above.**

1. **Object space** — the 109 records Round 8's grouping emitted. Non-text ink the ornament rule
   never bounded is **not covered**, and §2.1 shows that rule's output carries at least two schema
   defects (dropped `y`, an `n` that is not a glyph count). This frame cannot be treated as complete.
2. **Decoder / transition model** — R9 template DP, 29-class bijection, templates clustered from
   **LP2**. LP1 is measurably out of domain (42.6 % vs 95.6 %). Non-Futhorc glyph systems, glyphs
   below ~30 px, and any glyph absent from `templates.npz` are outside the model entirely.
3. **Adjudicator register** — H1 is **English + a known-Cicada-string list**, power 0.33 Latin /
   0.00 vowel-dropped English (L7-A). H2–H8 and B-12 are register-free.

**Not covered.** Ink outside the 109 boxes. Colour/chroma channels (only 8-bit luminance was
read). Sub-30-px glyph systems. Any band content in a non-English register (H1 only). Whether the
page-15 anomaly is in the document (§3.5). Whether the row-height bimodality encodes anything
non-binary — only bit packings were tested.

**Reopening conditions.** (a) A second render of page 15 — §3.5. (b) Re-run the ornament grouping
with the rejection rule's thresholds swept, and read whatever new boxes appear; the 109 are the
output of a rule now known to be defective. (c) Extend `templates.npz` with LP1-clustered
templates and re-run G-A2; if LP1 rises to LP2's level the pooled gate may pass. (d) Re-adjudicate
H1 through Round 19's I2 multi-register panel — H1's negative is English-only.

---

# ITEM 2 — L8 PROVENANCE

## 6. The PGP verification table, re-derived from scratch

### 6.1 Method — reproduce, do not trust

C3 did not read `PGP-VERIFICATION-TABLE.json`. It re-ran `verify_all_signatures.py` from a
fresh, isolated `GNUPGHOME` under GnuPG 2.4.8, over the whole repository, and then diffed the
result against Round 18's stored table file by file (`l8/crosscheck.py`).

One change was made to the enumerator and it is disclosed: Round 18's own control artifacts
(`round18/L8-provenance/work/control_C2_tampered.asc`, `control_C3_foreign.asc`) are excluded, so
that a deliberately tampered file and a foreign-key file cannot enter the corpus counts.

### 6.2 The controls — what makes the table worth anything

All four met in the independent run:

| control | required | measured | met |
|---|---|---|---|
| **C1** untouched known-good file | `GOODSIG 181F01E57A35090F` | `GOODSIG 181F01E57A35090F` + `VALIDSIG 6D854CD7…7A35090F` | ✅ |
| **C2** one character of the signed body flipped | `BADSIG`, no `GOODSIG` | `BADSIG`, no `GOODSIG` | ✅ |
| **C3** message signed by a freshly generated foreign RSA-2048 key | not `GOODSIG` for 3301 | `NO_PUBKEY` for the foreign keyid, no `GOODSIG` | ✅ |
| **C4** timestamp recovered from the *tampered* file | `created` unchanged | unchanged | ✅ |

**C2 and C3 are the whole basis for reading a FAIL as a fact.** Without them a table of 192
PASSes says only that gpg ran. The keyring is isolated **in code**: a throwaway `GNUPGHOME` per
run, importing only key blocks whose primary fingerprint is
`6D854CD7933322A601C3286D181F01E57A35090F`, and the script aborts if the resulting keyring holds
any other primary key — so a PASS cannot be manufactured from ambient GnuPG state.

### 6.3 The re-derivation agrees exactly

| | C3 run | Round 18 | on the 228 files **both** runs saw |
|---|---:|---:|---|
| files scanned | **238** | 228 | 228 |
| PASS | 192 | 192 | **192 = 192** |
| FAIL | 3 | 3 | **3 = 3** |
| NO-SIG | 27 | 22 | **22 = 22** |
| KEY | 16 | 11 | **11 = 11** |
| distinct by sha256 | 121 | 113 | — |
| distinct signing key IDs | **`181F01E57A35090F`** (1) | 1 | identical |

- **verdict changed on a shared file: 0**
- **sha256 changed on a shared file: 0**
- **files only in Round 18: 0**

The 238 − 228 = **10 extra files are entirely accounted for**: they are L8's *own* evidence
artifacts, fetched **after** its verification run — seven third-party project keys under
`evidence/baserate/` (Tor Browser, Bitcoin Core, GnuPG release, Tails, Apache, Debian archive,
Linus Torvalds) plus the two `mruzuki` keyserver exports and one zero-byte `.asc`. None is
Cicada corpus. **Excluding them, the two runs are identical in every field.**

### 6.4 Table scope, in the terms the brief asked for

- **Messages.** 238 `.asc` files, 121 distinct by sha256, deduplicating to **54 distinct signed
  messages** (55 distinct normalised bodies including the damaged copy of one).
- **Dates.** 54 distinct verified signature timestamps, **2012-01-05T03:46:03Z →
  2017-04-04T23:23:28Z** — a span of **1 916 days**. Every timestamp is read from the signature
  packet itself, not from a filename or a webpage.
- **Verifying against `7A35090F`.** **192 files PASS**; deduplicated, **54 of 54 distinct messages
  verify.**
- **Failing.** **3 files FAIL, and they are one message** — the 2013-01-03 "Welcome again."
  book-code message, mirrored into three 1 536-byte copies. gpg names the defect:
  `invalid armor header: Welcome again.` The mirror dropped the blank line separating the
  `Hash: SHA1` armor header from the body, so the message's first line is parsed as a header and
  excluded from the hashed data. **Four other files carry the identical normalised signed text and
  PASS**, and the repo already holds a repaired 1 538-byte copy that PASSes with the identical
  signature packet. Under the rule fixed in advance this is a **transport defect, not a canon
  failure**.
- **What the failure means, operationally.** A **two-byte** whitespace defect turns an authentic
  Cicada message into a `BADSIG`. Anyone running this repository's own declared authenticity test
  against a casually mirrored copy gets a **false negative** and may conclude a genuine message is
  a forgery. **Three such files are in this tree right now.**
- **One key ID, everywhere.** Across every signed message in the repository the set of signing key
  IDs has size **1**. No second key appears in any mirror, in any era. Independently reproduced.
- **The 22/27 NO-SIGs.** 19 are 199-byte HTTP **429** error pages in
  `round10/L6-archives/fetched/jaxonkuipers/comms/`, named like communications
  (`2012-01-book-code-poem.asc`) and picked up by any `**/*.asc` glob. Still in the tree.

**On the "no PGP verification table exists anywhere" claim.** C3 does not endorse it as written.
`corpus/A-primary-artifacts/SIGNATURES.json` already verified **140** files on 2026-08-20 — one
day *after* `GAPS.md` was compiled, which is why G-02 does not mention it. The defensible claim,
which C3 does endorse, is narrower and still substantial: **this is the first verification of the
whole tree (238 files, including the entire `jaxonkuipers` fetch that G-02 points at, every
`E-tooling/vendor/` mirror and `H-branch-recovery/`), the first with published positive AND
negative controls, the first grouped to distinct messages, and the first in human-readable form.**
Prior art exists and is credited; the gap it left is 88 files wide and had no controls.

### 6.5 Cross-check against L1's `GnuPG v1.4.11` finding — **FOUND-ERROR**

Round 18's **L1-toolchain** built this project's first evidence-derived prior on finding **F6**:

> "**46/46** curated 3301 PGP messages, 2012→2014, are `GnuPG v1.4.11 (GNU/Linux)`" — sourced to
> `corpus/A-primary-artifacts/ibotpeaches/messages/` — "the author's working machine is GNU/Linux,
> **one environment, three years, no drift**."

Measured over the same directory, from the re-derived table:

| | |
|---|---|
| PASSing files in `ibotpeaches/messages/` | **56** (not 46) |
| distinct signature timestamps there | **54** |
| actual date span | **2012-01-05 → 2017-04-04** (not 2012→2014) |
| `GnuPG v1.4.11 (GNU/Linux)` | **53** |
| `GnuPG v1` | **2** |
| `CicadaPG v.3301` | **1** |

Repository-wide, per **distinct message**: **54 × `GnuPG v1.4.11 (GNU/Linux)`, 2 × `GnuPG v1`,
1 × `CicadaPG v.3301`.** The non-1.4.11 messages are dated:

| version string | messages | dates |
|---|---:|---|
| `GnuPG v1.4.11 (GNU/Linux)` | 54 | 2012-01-05 → **2014-04-02** |
| `GnuPG v1` | 2 | **2015-07-28**, **2016-01-01** |
| `CicadaPG v.3301` | 1 | **2017-04-04** |

**Three consequences, in decreasing order of confidence.**

1. **F6's denominator and window are wrong.** 46 is not the count of that directory (56 files /
   54 messages), and "2012→2014" silently truncates the span at exactly the point where the
   version string changes. The claim is *true inside its stated window* and the headline drawn
   from it — "one environment, three years, no drift" — is **contradicted by the same directory's
   own later files**.
2. **The toolchain changed twice, not once.** Round 18's L8 §1.5 recorded one change, from the
   digest algorithm (SHA-1 × 53 → SHA-512 × 1 at 2017-04-04). The armor `Version:` header shows an
   **earlier, independent** change between **2014-04-02 and 2015-07-28**, from the long
   `v1.4.11 (GNU/Linux)` form to the short `GnuPG v1` form. Two dated transitions, from two
   independent fields, and the later one is corroborated by both.
3. **`CicadaPG v.3301` is hand-set.** No GnuPG build emits that string. It is a deliberately
   customised armor version on the final 2017-04-04 message — the same message that is also the
   only SHA-512 one. Two independent signals of a changed signing setup on the same message.

**L1's conclusion survives; its numbers need correcting, and the correction sharpens it.** The
1.4.11 environment is now attested over **2012-01-05 → 2014-04-02 — 818 days** covering the entire
Liber Primus release window, which is precisely the period L1's Ubuntu 11.04–12.04 prior is about.
Round 19's Phase-1 generator ranking (G1 `$RANDOM`, G2 Perl 5.14, G3 Python 2.7, G4 TeX LCGs) is
**not weakened** — if anything the era attribution is tighter than L1 stated, because C3 has now
bounded when it ended.

*(Recommended, not done here since it is outside C3's write scope: correct F6/F7's numbers in
`round18/L1-toolchain/RESULTS.md` §6 and its ledger entry, marking the old figures superseded per
`CLAUDE.md` rather than deleting them.)*

### 6.5b Two lanes reached this defect independently — cite R1

**Round 19's red-team lane R1 found the same problem in L1's prior from the opposite direction.**
Working from the *render and packaging* side rather than the signed corpus, R1 established that a
**non-ImageMagick** chain — Ghostscript → PIL with `quality="keep"` — reproduces **all four** of
LP2's discriminating JPEG fields, and that **GnuPG 1.4.11 shipped in at least six OS generations,
including Ubuntu 12.10 — outside L1's stated 11.04–12.04 bracket**
(`round19/R1/RESULTS.md` §C).

C3 reached the same conclusion from the corpus side: L1's `46/46` is really **56 PASSing files /
54 distinct messages / three version strings / running to 2017**.

That convergence is the point, and it is worth more than either finding alone. Two lanes, two
independent evidence bases — one physical (JPEG fields, package archives), one cryptographic
(signed message armor) — both land on the conclusion that **L1's environment bracket is narrower
than its evidence supports**. Under doctrine R6 this is exactly what a red-team lane is for, and
under R4 it matters concretely: **L1's prior is what justifies Round 19's entire Phase 1.** The
generator families are not invalidated — §6.5 argues the era attribution is if anything *tighter*
— but the *distro bracket* they were ranked by is not as tight as `RESULTS.md` §6 states, and
anyone re-deriving the Phase-1 ranking should read L1 §6, R1 §C and C3 §6.5–6.6 together.

### 6.6 The Perl fact nobody cited — signed, dated, and it PASSes

R1 noticed in passing that a 2012 signed message has 3301 stating they encrypted using **"the
Crypt::RSA Perl module available in CPAN"**. C3 is positioned to answer the question that makes
that observation load-bearing: **does that message verify?**

**It does.** Four files in the verification table mention `Crypt::RSA`. They are **two distinct
messages, and every one of the four PASSes** against `181F01E57A35090F`:

| date (from the signature packet) | verdict | what it carries |
|---|---|---|
| **2012-01-15T01:39:42Z** | **PASS** | the prose statement, plus `Version: 1.99` / `Scheme: Crypt::RSA::ES::OAEP` |
| **2014-01-06T07:35:27Z** (3 mirrors) | **PASS** ×3 | `Version: 1.99` / `Scheme: Crypt::RSA::ES::OAEP` |

The 2012-01-15 message — ten days after the first 3301 image — says, over a signature that
verifies:

> "Here is a message that has been encrypted with RSA (the Crypt::RSA Perl module available in
> CPAN)"

and then pastes the public key **as Perl `Data::Dumper` output**:

```
$VAR1 = bless( {
                 'e' => 65537,
                 'n' => '78808916397911537795302584646496939287334116815815771036902928223331980368647...',
                 'Version' => '1.99',
                 'Identity' => '...'
               }, 'Crypt::RSA::Key::Public' );
```

`$VAR1 = bless( {...}, 'ClassName' );` is *literally* `Data::Dumper`'s default emission. So the
author ran a Perl script, dumped a live `Crypt::RSA::Key::Public` object, and pasted the dump into
a message they then signed.

**Three independent Perl signals, all inside one PASSing artifact:** a prose claim, the library's
own machine-emitted armor (`Version: 1.99`, `Scheme: Crypt::RSA::ES::OAEP` — the module version is
pinned by the library itself), and `Data::Dumper` output. The armor recurs on a **second** message
**two years later**, so this is not a one-off borrowed snippet.

**Why this matters more than any distro argument.** Round 19's Phase-1 lane **G2** sweeps Perl 5.14
`rand`/`srand`, ranked by L1 at ×2.5 on the strength of *"Ubuntu 11.04–12.04 shipped Perl 5.14"* —
an inference from a package list. §6.5b shows that bracket is looser than claimed. But **the Perl
prior does not need it**: the author *says* they used Perl, in a signed message, and the library's
own output is in the artifact, on two dates **twenty-four months apart**, and **both dates fall
inside the 2012-01-05 → 2014-04-02 GnuPG 1.4.11 window §6.5 bounds**. That is evidence of the class
doctrine R4 asks for — a measurement on a held artifact — and it is strictly stronger than a
distro-version inference, because it is the author's own dated, authenticated statement about their
own toolchain.

**Recommendation to the coordinator: G2's prior should be re-sourced to this, not to the distro
bracket.** It is the best-attested toolchain fact in the entire corpus and no lane has used it.

**What this is not.** It does **not** establish that the Liber Primus keystream came from Perl. It
establishes that the author had a working Perl + CPAN environment in January 2012 and still in
January 2014, by their own signed statement and by the library's machine-emitted armor.

**One lead, explicitly not a claim.** `Crypt::RSA::ES::OAEP` draws its padding randomness through
`Crypt::Random`. Whether that dependency chain is a plausible source for any 3301 keystream is a
question for a generator lane, and C3 does not answer it.

**A bonus for G-02 itself.** The same PASSing 2012 message contains 3301's *own* statement of the
authenticity test:

> "There are many fake messages out there. Only messages signed with public key ID 7A35090F are
> valid."

That is the keyholder, in a message that verifies, declaring the exact test `KNOWLEDGE.json:
authenticity_test` encodes and that corpus G-02 exists to operationalise. The table in §6.3 is not
applying a convention the community invented — it is applying the rule 3301 published. *(The key
dump also carries an `Identity` email field. It is an artifact field, already public in the corpus,
and this lane does not pursue it — the standing constraint in §8 applies.)*

## 7. I-03 — the pre-disclosure search, and why Round 18's negative covered nothing

### 7.1 The finding about the previous run

Round 18's `predisclosure_search.sh` hit a fixed pipermail URL for every month of 2011–2013 and
treated a non-200 as "searched, nothing". Its own fetch log shows what it actually got:

| list | months requested | `http=200` | what the non-200s were |
|---|---:|---:|---|
| metzdowd cryptography | 36 | 8 | **404** — the archive genuinely has no monthly file |
| cypherpunks (`lists.cpunks.org/pipermail/`) | 36 | **0** | **`http=000`** — a transport failure |

`http=000` is not a 404 and neither is a searched month. C3 re-probed both:

- **metzdowd** — the index lists **274** monthly archives, and for 2011–2013 exactly **eight**
  exist: `2011-August`, then nothing until `2013-June`. The list was dormant. So of the 13 months
  in the hard window **2011-01-01 → 2012-01-04, the archive holds one: 2011-August.**
  **Coverage: 1/13.**
- **cypherpunks** — two independent faults, neither of them absence. The host's **TLS certificate
  has expired**, so a verifying client fails before it sees an HTTP status; and the list no longer
  runs pipermail at all — `/pipermail/cypherpunks/` returns **404** and the archive is served by
  **HyperKitty** at `/archives/list/cypherpunks@lists.cpunks.org/`. Round 18 was pointed at a dead
  endpoint behind a broken certificate and recorded the result as a negative.

### 7.2 What C3 actually searched

`l8/predisclosure_archives.py` and `l8/cpunks_export.py`, against the live endpoints, with the
term list fixed in `round18/L8-provenance/PREREG.md` and not extended:

| archive | reachable | coverage of the hard window (2011-01 → 2012-01-04) | downloaded | term hits |
|---|---|---|---|---|
| metzdowd cryptography | yes | **1 of 13 months** (`2011-August` only) | 8 months, 1.9 MB | **40 — all in 2013-09 and 2013-11**; **0 in 2011-August** |
| cypherpunks @ cpunks.org (HyperKitty) | yes (expired cert, fetched unverified — recorded) | **0 of 13 months** — the archive holds **0 messages before 2013** | 2013: 5.5 MB, **2 645 messages** | **0** |
| mail-archive.com cypherpunks | yes | n/a — search interface only, no mbox export, so it yields **no coverage number** | — | — |

The 40 metzdowd hits are all **post-disclosure context**: a November 2013 forward of a Telegraph
article about the puzzle (which is where `845145127`, `instar emergence` and `Cicada 3301` appear)
and three 2013-09 hits on `3301` inside a Message-ID. **None is in the window and none is a hit
under the pre-registered bar.**

### 7.3 The bound

**Mailing lists: searched `2011-August` (metzdowd) with all 12 pre-registered terms — nothing.
That is one month of a thirteen-month window. Every other month of the hard window is not held by
either archive.** This is a **1/13 bound**, and it is a much weaker statement than Round 18's
apparent "searched 2011–2013, nothing". The correction is the result here.

Secondary, and free: **the cypherpunks list never mentioned Cicada 3301 in 2013** — 2 645 messages,
5.5 MB, zero hits on any of the twelve terms, in the year the puzzle was at its most public. That
is a genuine (if minor) negative about where the puzzle was and was not discussed, and it is
properly bounded: the archive holds nothing earlier.

### 7.4 bitcointalk — the `reported` gap, now closed

Round 18's L8 §4.6 names its own reopening condition #2: *"A local bitcointalk corpus (the forum's
own search, or a database dump) replacing the search-engine layer, which would upgrade §4.4's
`reported` rows to `verified`."* C3 closed it.

**Instrument:** `api.ninjastic.space` — a third-party full-text index over bitcointalk posts
carrying per-post ids, dates and authors. A grep over a real index is reproducible and its negative
is a measurable bound; a search-engine miss is not. All twelve pre-registered terms, unchanged and
unextended, oldest-first, ceiling **2012-01-04**.

| term | total in index | earliest match | pre-2012-01-04 | adjudication |
|---|---:|---|---:|---|
| `845145127` | **0** | — | 0 | **zero occurrences, ever** |
| `futhorc` | **0** | — | 0 | **zero occurrences, ever** |
| `a2e7j6ic78h0j` | **0** | — | 0 | **zero occurrences, ever** |
| `liber primus` | 4 | 2018-01-16 | 0 | no pre-ceiling match |
| `mabinogion` | 4 | 2016-10-26 | 0 | no pre-ceiling match |
| `instar emergence` | 1 | 2017-08-11 | 0 | no pre-ceiling match |
| `cicada 3301` | 263 | 2014-03-15 | 0 | no pre-ceiling match |
| `3301` | 999 | 2011-04-24 | 2 | **not a hit** — the number inside MtGox order-book JSON on a trading thread |
| `cicada` | 622 | 2011-07-04 | 20 | **not a hit** — a bitcointalk *username* posting in GPU-mining threads (rigs, fan noise, PCI-E hash rate) |
| `instar` | 279 | 2011-05-17 | 3 | **not a hit** — French posts using *"à l'instar de"* |
| `looking for highly intelligent` | 306 | 2011-05-31 | 3 | **not a hit** — unrelated mining/gold threads; token-matched, not phrase-matched |
| `outguess` | 65 | 2011-01-11 | 1 | **not a hit** — see below |

**All 29 pre-ceiling matches were adjudicated by eye and every one fails the bar.** The
anti-motivated-reasoning clause is doing real work here: a user named `cicada` discussing GPU
cooling in July 2011 is exactly the "someone mentioned cicadas" the clause excludes, and it is not
pursued as an attribution lead either.

**The one near-miss, named and rejected.** `outguess`, 2011-01-11: a thread *"steganography: Hiding
your wallet in a JPEG image"* discussing `stegdetect`. It is genuinely about JPEG steganography,
a year before the first image. It is still **not a hit**: the pre-registered term was
*outguess + steganography + **recruit***, and this is generic Bitcoin wallet-hiding tooling talk
with no Cicada element and no recruitment element. Recorded explicitly so nobody later "finds" it
and mistakes it for something this lane missed.

**The strongest part of this arm is the zeroes.** `845145127`, `futhorc` and the onion string
`a2e7j6ic78h0j` have **zero occurrences in the entire bitcointalk index at any date** — not merely
zero before 2012.

**Two instrument caveats, stated because they bound the claim.**

1. The API **token-matches** multi-word queries rather than phrase-matching, so the four multi-word
   terms were **not tested as phrases**. The single-token terms are reliably tested; that is where
   the strong zeroes are.
2. ninjastic's earliest `cicada 3301` is 2014-03-15, while the Round-18 lane read bitcointalk
   **topic 347716** directly and dated its first post **2013-11-26**. So the index is *not complete*
   for that topic, and the direct read is the better evidence. Recorded rather than reconciled: the
   index is a **supplement**, not a replacement.

### 7.5 I-03 verdict, and the decision this lane made

**Verdict: NO HIT, across every arm.** Every hit in every machine-searched corpus is
post-disclosure and traceable to one 2013 newspaper article — the Telegraph piece that reached
metzdowd on 2013-11-27 and bitcointalk on 2013-11-26, *one day apart*.

**The decision, stated explicitly as the brief asks.** C3 **did not re-run I-03 in full**, and
reports it as **partially covered**. The reason: while C3 was down, a concurrent Round-18
continuation completed L8's §4 using Wayback CDX, a direct read of bitcointalk topic 347716, live
probes of `al-qaeda.net` and `cypherpunks.venona.com`, and the cryptoanarchy.wiki maintainers'
statement that no 2000–2013 cypherpunks archive is public. **It reached the same conclusions C3's
archive work reached, by different evidence.** Re-running it would have duplicated finished work.
So C3 added only what that record did not have: the **coverage denominators** (§7.2), the
**transport diagnosis** of the `http=000` (§7.1), a **direct HyperKitty measurement** confirming
zero pre-2013 cypherpunks messages from the archive's own export rather than from a Wayback
inference, and the **bitcointalk upgrade** above.

**Residual coverage gap, in full:**

- **12 of the 13 months** of the hard window are not held by either mailing-list archive and were
  **not searched**. No public cypherpunks archive covering 2011–2012 exists as of 2026-08-26 —
  that is the *absence of an instrument*, not a null result from one.
- The four multi-word pre-registered terms were **not phrase-tested** on bitcointalk.
- **4chan `/x/` and `/b/` for 2011**: the archives largely postdate 2011, so this vector is
  **structurally incapable** of a hit rather than merely unsearched.
- sci.crypt, Freenode IRC logs and `full-disclosure` were not searched at all.

**Vectors needing owner-run or paid access** (`round12/A2` is the standing register):

| vector | what it would buy |
|---|---|
| a cypherpunks 2000–2013 archive surfacing (cryptoanarchy.wiki maintainers are actively seeking one) | the single largest missing corpus; the term set is already fixed, so a result would be immediately comparable to this one |
| paid newspaper / Usenet full-text archive search | window coverage beyond 1/13 months |
| a bitcointalk database dump | phrase-accurate search, closing caveat 1 above |
| a second independent render / the original PDF of LP page 15 | settles §3.5 — the cheapest open item in the whole lane |

## 8. I-01 — `mruzuki` / `cicadeur`

Round 18's verdict is **INDECISIVE against a threshold fixed in advance**, and C3 leaves it there.
Restating it because it is the load-bearing part: **where the software chose, the two keys agree;
where a human chose, they differ.** Key size (4096 vs 2048), expiry policy (none vs **one day**)
and revocation (never vs 2012-01-22, reason `0x03` *no longer used*) all diverge. The matching
preference lists (`S9 S8 S7 S3 S2` / `H8 H2 H9 H10 H11` / `Z2 Z3 Z1`, features `01`, keyserver-prefs
`80`) are **exactly** GnuPG 1.4.x/2.0.x's `keygen_set_std_prefs()` defaults — in January 2012 that
describes most new OpenPGP keys on Earth.

Two C3 notes:

1. **§6.5 does not disturb this verdict.** The `CicadaPG v.3301` header proves the author edited
   armor output **in 2017**. §3.2's argument is about **key preference packets set in January
   2012**, five years earlier and in a different part of the format. The INDECISIVE verdict rests
   on the 2012 packets and is unaffected. Recording this explicitly so the two findings are not
   later welded into a claim neither supports.
2. **The base-rate control is still missing and still matters.** Round 18's attempt used four live
   project keys, none created in January 2012, and a live key's UID self-signature is **reissued**
   on every edit — so a keyserver copy shows the preferences of the last edit, not of creation.
   The control needs keys whose self-sigs are **frozen in 2012** (abandoned or revoked keys). Not
   sourced by Round 18 and not by C3.

Round 18's factual correction stands and is worth repeating because a mis-stated coincidence
hardens through repetition: `AUDITOR-LOOP-2026-07-28.md` and `LEDGER.json` I-01 both say the key
was revoked "seven days after the first 3301 image". The first image is 2012-01-04, so the
revocation is **18** days after it and the creation **8**. Seven days is the gap between **3301's
key creation (2012-01-05)** and **mruzuki's (2012-01-12)** — the right number attached to the
wrong anchor.

**Standing constraint honoured throughout: no person is named as Cicada 3301.** No breach
databases, no people-search services, no contact with anyone. The falsifiable version of the
question is the packet comparison, and it was run.

---

## 9. Provenance of this lane's own execution

Recorded because it bears on how the files here should be read.

- C3 was **terminated mid-run by an API error**, not by a measurement problem. Every number in
  §§1–8 was already computed and on disk; the write-up tail was finished afterwards from those
  artifacts. No measurement was re-run from memory, and nothing in this file is reconstructed.
- The **I-03 open-web sub-agent died on the same error**, partway through the bitcointalk arm. Its
  one durable contribution was the lead that `api.ninjastic.space` offers real full-text search over
  bitcointalk; C3 ran the pre-registered terms against it directly (§7.4) rather than restarting
  the agent. §7.5 states the decision and the residual gap.
- A **concurrent Round-18 continuation process** completed `round18/L8-provenance/RESULTS.md` §4
  and §6 while C3 was down. C3 **did not overwrite it**; §12 below records what C3 appended to it
  instead, as a dated addendum.

## 10. Trust anchor, after the lane

```
python3 liber-primus/tests/validate.py
→ ALL VALIDATIONS PASSED — rig reproduces known solves.   (5/5)
```

Recorded in `l3/validate_after.log`. No file outside `round19/C3/` and the two Round-18
`RESULTS.md` files named in the brief was modified. No `git commit` was made.

## 11. Artifacts

| path | what |
|---|---|
| `PREREG.md` | Aiming Test, inherited thresholds, gate G-A2 registered before it was scored |
| `PGP-VERIFICATION-TABLE.json` | the independent re-derivation (238 files, full status lines) |
| `verify_all_signatures_rerun.py` | the instrument, with its one disclosed enumerator change |
| `verify_rerun.log` | run summary + control block |
| `l8/crosscheck.py` · `crosscheck.json` · `crosscheck.log` | file-by-file diff vs Round 18 + the L1 version-string cross-check |
| `l8/predisclosure_archives.py` · `.json` · `.log` | archive **coverage** audit + term grep |
| `l8/cpunks_export.py` · `cpunks_export.json` · `.log` | the cypherpunks arm, live endpoint |
| `l8/bitcointalk_ninjastic.py` · `.json` · `.log` | the bitcointalk arm — 12 pre-registered terms over a real full-text index |
| `out_l3_ornaments.json` · `out_l8_provenance.json` | machine summaries of both items |
| `l3/read_bands.py` · `bands.json` · `read_bands.log` | all **109** bands read |
| `l3/band_control.py` · `band_control.json` · `.log` | **gate G-A2** |
| `l3/control_strata.py` · `control_strata.json` · `.log` | the stratified power table (§1.5) |
| `l3/hypotheses.py` · `hypotheses.json` · `.log` | H1–H8 |
| `l3/h7_control.py` · `h7_control.json` · `.log` | H7 decoy panel |
| `l3/h78_controls.py` · `h78_controls.json` · `.log` | H7 set-randomisation, H8 ordinary-text control |
| `l3/intensity.py` · `intensity.log` | H9 as Round 18 wrote it — control fails at every ΔL |
| `l3/intensity2.py` · `intensity2.json` · `.log` | H9 repaired — control recall 1.000 at ΔL = 2 |
| `l3/h9_verdict.py` · `h9_verdict.json` | the geometry-AUC discriminator + the p15 measurement |
| `l3/p15_second_render.py` · `.json` · `.log` | the second-render test (byte-identical ⇒ no second render) |
| `l3/linegeom.py` · `linetests.py` · `linetests.json` · `.log` | B-12, all stages including C-3a/C-3b |
| `l3/hashes.py` · `hashes.json` | sha256 of all 8 control renders and all 56 target renders |
| `ledger.json` · `out_*.json` | ledger fragments for A-06, B-12, P-9, I-01, I-03, G-02 |

Crops are **not** committed: they are rebuildable from the committed scripts plus the hashes in
`l3/hashes.json`, per `CLAUDE.md`.

## 12. Bounds, not verdicts

Nothing here is exhausted, closed or unsolvable.

- The 109 bands are read; the **rule that produced those 109 is defective in at least two ways**
  and its output is not a complete frame for the book's non-text ink.
- The band reader is trustworthy at **95.6 %** on the LP2 face conditional on its `RUNIC` call,
  and its call is **a coin flip at ≤ 16 glyphs**. Improve the classifier and the ≤ 16-glyph class
  becomes readable; that is a concrete, small piece of work.
- H9 is now **measurable** for the first time (recall 1.000 at ΔL = 2). It is not a demonstrated
  channel, and **one four-glyph group on page 15 sits 51 grey levels off its neighbours** with no
  geometric explanation and no second render to test it against.
- The PGP table is **reproduced exactly** and one signing key ID is independently confirmed. L1's
  46/46 is corrected, and the toolchain is now dated as changing **twice**.
- I-03 has a **1/13-month** bound on the mailing-list arm, not the 36-month sweep the previous
  run appeared to report.
- The corpus contains a **signed, dated, verifying statement that the author used Perl**, on two
  messages two years apart, which no lane had cited. It is the best-attested toolchain fact this
  project holds and it is **not** a statement about the keystream.
- L1's environment bracket is **looser than published**, established independently by C3 and R1.
  Phase 1's generator families stand; the bracket that ranked them needs re-sourcing.

---

## 13. What C3 wrote into Round 18's record

The brief requires Round 18's record to be whole. C3 checked timestamps and content before writing,
and found that **a concurrent Round-18 continuation process had completed both files** while C3 was
down (L8 at 11:44, L3 at 12:30). **Nothing was overwritten.** C3 appended a dated addendum to each:

| file | state when C3 reached it | what C3 did |
|---|---|---|
| `round18/L3-ornaments/RESULTS.md` | 26 081 B, §§1–9 complete (12:30) | appended **§10** — dated C3 addendum |
| `round18/L8-provenance/RESULTS.md` | 34 828 B, §§1–6 complete (11:44) | appended **§7** — dated C3 addendum |

**This turned the closeout into an unplanned replication, which is worth more than the closeout
would have been.** Two independent runs, from the same PREREGs and the same inherited thresholds,
using different instruments. Where they converge the result is much better attested than either
alone; where they differ, the addenda say which is better and why.

**Convergences.**

| question | concurrent run | C3 | agreement |
|---|---|---|---|
| band-scale reader power | **C-2**: real glyph bitmaps composited into band strips → **93.8 %** | **G-A2**: band boxes on pages solved by decryption → **95.6 %** (LP2), 95.62 % given `RUNIC` | two plant designs, **94–96 %** |
| H9 detector defect | mean/sd fails its own plant; median/MAD → recall **1.00 at ΔL = 2** | identical finding, identical fix | **independently derived twice** |
| H7 | size-matched base rate → p = 0.019, FAIL | set-randomisation → p = 0.089, FAIL; decoy panel shows the original null invalid for *every* set | same verdict, two nulls |
| H8 | "uninformative — a uniform-position null is physically impossible" | measured it: the same test on 616 ordinary text rows gives **p = 3.3e-112** vs the bands' 8.2e-11 | disposition → number |
| the p15 `3299` lightening | min grey **47–51** vs **0.0** for every other digit on the page | mean grey **+51.2 levels, z ≈ 92**, stroke-and-height matched | same feature, two statistics |

**Where the concurrent run is better, stated plainly.** Its §5 switched from *mean* grey to
**minimum** grey — a solid-black glyph has a near-0 pixel however thin its strokes, so the floor is
nearly free of the stroke-width confound. That resolved what C3 could only report as *partially
explained* (§3.4, pooled AUC 0.709), yielding a clean population of **226 components at 25 sites**
at a uniform tone, mostly section headings and drop-caps. **It supersedes C3 §3.4**, and §3.4 is
annotated to say so. It also noted that **3299 is the prime immediately preceding 3301**.
Its **H1′** repair (confusable-tolerant matching, after the exact-substring detector failed its own
plant) and its **H8b** finding (109 bands occupy only 58 distinct boxes; the x-span `[28, 2372]`
recurs 21 times — *template, not data*) are both real additions C3 did not make.

**Where C3 is additive.** The **P-9 refutation** (§2.1) — the concurrent run still treats `n ≤ 16`
as a glyph-count set; it is a row-group count and those 30 boxes hold **0 to 341** components. The
**specificity/PPV table** at ≤ 16 glyphs. The **independent re-derivation** of the PGP table
(228/228 identical). The **L1 FOUND-ERROR** and the **Crypt::RSA** result. The **I-03 coverage
denominators**, the **transport diagnosis**, and the **bitcointalk upgrade** that closes that lane's
own reopening condition #2.
