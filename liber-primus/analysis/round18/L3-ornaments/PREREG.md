# L3 — ORNAMENTS & LAYOUT · PRE-REGISTRATION

_Round 18. Written **before** any measurement in this lane was run. Ledger items **A-06**
(`never-run`) and **B-12** (`never-run`). Parked item **P-9**._

**Do not edit any threshold in this file after seeing a result.** If a threshold turns out to
be wrong, the honest move is a new pre-registration in a new file that says so.

---

## 0. Why this lane exists

Round 8's GEOMETRY track catalogued **47 non-text bands across 23 pages**
(`analysis/geometry/geometry_report.json:ornaments`, plus a 62-row superset in
`analysis/geometry/ornaments.json`) and wrote, in its own words:

> "This is inventory, not a result — it is the one item in Round 8 left as an open thread
> rather than a verdict." … "the genuinely short bands (1, 3, 4, 8 and 16 glyphs) are the
> only real candidates" … **"nobody has read them."**

That statement is still true on 2026-08-25. Every segmentation pipeline in this repository
explicitly *discards* ornament components ("components far from the dominant text column"),
so this ink has never entered any analysis. Round 17 established that the anti-repeat filter
is machine-applied — the same program that produced the pad also *typeset* the book, and
typesetting decisions (band placement, band length, line fill, where a line breaks) are a
place a designer can put data **without touching the rune stream at all**.

Prior, honestly stated: **LOW**. Ornaments in a hand-set book are usually ornaments, and
1–16 symbols over a 29-symbol alphabet is pareidolia territory. The value of the lane is
mostly the durable artifact (a transcription of ink nobody has transcribed) and a *measured*
bound in place of an open thread.

---

## 1. Instruments, and how each is validated

### I-1 · Glyph reader (band contents)

**Instrument.** The **validated R9 template-DP** reader — `analysis/retranscribe/read.py` +
`analysis/retranscribe/templates.npz` (label-free shape clusters, named through a single
29→29 `linear_sum_assignment` permutation fit on SOLVED pages only). Round 12 front B
reproduced it at **98.0% over 5,150 glyphs on 232 count-exact lines**.

**Explicitly NOT used:** the forced re-segmentation instrument
(`round12/frontB/forceseg.py` / `forcedp.py`). It **fails its own positive control at 12.9%**
and by this campaign's discipline cannot confirm or refute anything.

**Validation required before any band reading is trusted (gate G-A):**
re-run the template-DP reader on the **solved** control pages (LP 0–1 segments whose plaintext
is known: SOLVED-PAGES.json) under the *identical* code path used for ornament bands, and
report the measured per-glyph agreement against canon on count-exact lines.
- **PASS iff agreement ≥ 90%** on the control set (R9 measured 96.9%, R12 98.0%; 90% leaves
  headroom for the fact that ornament bands are cropped differently).
- If G-A fails, every band reading in this lane is reported as **UNCALIBRATED** and no
  hypothesis test that depends on band *content* may be scored.

**Second gate (G-B), rune-vs-ornament discrimination.** The reader has a closed 29-symbol
alphabet: it will emit runes for *any* ink, including a floral swirl. Before calling a band
"runic" we require a discrimination statistic:
- Per-glyph template match cost. On solved text lines the median cost is ~124 (R9); on
  garbage the median runs 500–1,100. A band is called **RUNIC** iff its median per-glyph
  match cost is **≤ 300**, i.e. within ~2.4× the text median and well below the garbage floor.
- A band whose median cost exceeds 300 is reported as **NON-RUNIC (decorative ink)** and its
  emitted "runes" are recorded in the JSON artifact but are **not** admitted to any hypothesis
  test. This is the honest way to avoid manufacturing a message out of a swirl.

### I-2 · Content hypothesis detector

Given the runic bands, the following hypotheses are tested. Every one is scored against a
**size-matched null** built by the same procedure on shuffled/resampled data.

| # | hypothesis | statistic | PASS threshold |
|---|---|---|---|
| H1 | Band decodes to English / a known Cicada string | plaintext length ≥ **8** under a cipher already validated on the solved pages (Atbash, shift-n, key-subtraction with the known page keys, Gematria-Primus value read) | any single hit at length ≥8 that is a real word/phrase |
| H2 | A short band **recurs** at ≥3 sites and decodes consistently | count of exact-content repeats across sites | ≥3 sites, identical content, consistent decode |
| H3 | Band Gematria values = page index | exact match rate over all runic bands | ≥3 exact matches AND p<0.001 vs null |
| H4 | Band Gematria values = prime index / prime at that index | exact match rate | as H3 |
| H5 | Band values are a **checksum** over that page's rune stream (sum mod 29, mod 26, mod 100, XOR, rune count mod k) | exact match rate over 12 checksum forms | as H3, Bonferroni over 12 forms ⇒ p<8.3e-5 |
| H6 | Band values are a **pointer/index** into that page's own rune stream or into the full payload (1-based/0-based, forward/back, per-page/global) | do the pointed-at runes spell anything ≥8 chars, or land on a distinguished position (segment boundary, residual doublet)? | ≥8-char English, or landing-on-doublet rate p<0.001 vs uniform null |
| H7 | Band **lengths** are the channel (1/3/4/8/16 is a binary ladder) | are lengths drawn from {2^k}? exact binomial test vs. the empirical band-length distribution over *all* 646 bands | p<0.001 |
| H8 | Band **positions** are the channel, independent of content | (a) x,y quantised to a grid → bitstream; (b) presence/absence of a band per page → 56-bit word; test both for English/known-string decode and for non-uniformity | p<0.001 vs uniform-position null, or a ≥8-char decode |

**Multiplicity.** H3–H8 are 6 families; the reported family-wise bar is **p < 0.001 / 6 =
1.67e-4** on any single family's headline statistic. H1/H2 keep P-9's own bar verbatim.

**Explicitly not a result:** a 3-glyph band reading as some 3-letter word. With ~47 bands over
a 29-symbol alphabet several such are expected by chance. Stated here so it cannot be claimed
later.

### I-3 · Line-geometry detector (B-12)

Channels measured, per page and per line, from the 646 image bands + the canonical
transcription:

1. runes per line, 2. words per line, 3. words per page, 4. lines per page,
5. line-fill ratio (ink extent ÷ text-column width), 6. left margin, 7. right margin,
8. mean inter-word (separator) gap, 9. line-break position within the word stream
(does the break fall mid-word or at a word boundary — and if mid-word, *where*).

Each is tested three ways:
- **(a) Bimodality / two-state channel.** 1-vs-2-component GMM, report BIC and component
  separation in σ. **PASS iff separation ≥ 2.0 σ AND BIC prefers 2 components by Δ>10.**
  (This deliberately extends Round 8, which measured micro-spacing at 1.86 σ and rejected
  baseline jitter by BIC — those two axes are NOT re-run here.)
- **(b) Bitstream decode.** Median-threshold the channel → bitstream → try 8 packings
  (MSB/LSB first, 5-bit and 8-bit, both bit orders, all phases) → English/magic detection.
  **PASS iff a decode beats the size-matched shuffle null at p<0.001.**
- **(c) Correlation with the rune stream.** Spearman ρ between the channel and per-line rune
  statistics (mean rune index, doublet count, IoC). **PASS iff |ρ| significant at p<0.001
  after Bonferroni over the 9 channels × 3 statistics = 27 tests ⇒ p < 3.7e-5.**

### I-4 · Cross-check against known structure

Any surviving candidate must be cross-checked against (i) the **86 residual doublet
positions** and (ii) the **segment boundaries**. A band that indexes something real should
correlate with something real. This is a *confirmatory* check applied only to candidates
that already passed their own threshold; it cannot by itself promote a candidate.

---

## 2. MANDATORY positive controls (plant-and-recover)

A null from an unvalidated instrument is not a negative. Three controls, all run **before**
any null is trusted:

**C-1 · Glyph reader calibration.** As gate G-A above. Deliverable: a measured accuracy
number on solved pages, stated in RESULTS.md. Threshold ≥90%.

**C-2 · Planted band message.** Synthesise a set of ornament-shaped bands by *compositing
real glyph bitmaps* (from `geometry/glyphs2.npz`) into band-sized strips at ornament
positions, encoding a known plaintext (`"THEPRIMESARESACRED"`, split across bands the same
way the real short bands are sized: 1/3/4/8/16). Run the **entire** L3 band pipeline over the
synthetic page set. **PASS iff the pipeline recovers ≥90% of the planted glyphs and H1 fires
on the planted message.** If C-2 fails, no band-content null in this lane is a negative.

**C-3 · Planted line-fill message.** Take the real per-line geometry, overwrite the channel
values with a two-state encoding of a known 64-bit message (low state = channel 25th
percentile + noise, high state = 75th percentile + noise, with the *measured* real noise sd),
and run detector I-3(a)+(b). **PASS iff the GMM finds ≥2.0 σ separation and the bitstream
decode recovers ≥95% of the planted bits.** If C-3 fails at the real noise level, the lane
reports a *power ceiling* (the smallest planted separation the detector can see) rather than
a negative.

---

## 3. Nulls

- **Band content null:** 10,000 resamples in which each band's glyph sequence is replaced by
  i.i.d. draws from the empirical rune-frequency distribution of the LP2 corpus, band lengths
  held fixed. All of H1–H6 are re-scored on each resample; the reported p is the fraction of
  resamples reaching the observed statistic.
- **Band position null:** 10,000 resamples placing the same number of bands uniformly in the
  page's non-text area.
- **Line-geometry null:** 10,000 within-page shuffles of the channel (destroys any ordering
  channel, preserves the marginal distribution), plus a size-matched Gaussian null at the
  measured mean/sd.
- **Score bars:** any decode scored with the beam decoder uses
  `benchmark/null.py: threshold_for(n_trials, segment_len)`; **no fixed −5.5 bar** is used at
  large N. Scoring is on **rune indices**, never the transliteration string. The rigid decoder
  is **not** used anywhere in this lane.

---

## 4. Deliverables (fixed in advance)

- `PREREG.md` (this file)
- `bands.json` — every band's crop geometry, per-glyph template read, per-glyph match cost,
  RUNIC/NON-RUNIC call. **This is the durable artifact and it is delivered whether or not any
  hypothesis survives.**
- `linegeom.json` — the 9 per-line/per-page geometry channels.
- `RESULTS.md` — readings, per-hypothesis verdict against the thresholds above, measured
  control recovery, coverage and explicit `not_covered`.
- `ledger.json` — ledger-shaped entries for A-06 and B-12.
- scripts: `read_bands.py`, `hypotheses.py`, `linegeom.py`, `controls.py`.

**No `git commit`** — eight lanes share one worktree; the coordinator commits.

## 5. Data integrity precondition (met before running)

`python3 liber-primus/handoff/capsule/verify_capsule.py --only images` → **PASS, 56/56 sha256
intact**, run 2026-08-25 before any crop was taken. A mirror serving different bytes is the
failure mode this repo has been bitten by twice; the local `data/relikd/p*.jpg` were verified,
not re-downloaded blind.

## 6. What a negative in this lane will and will not mean

It will mean: *the ink in the 47/62 catalogued non-text bands has been transcribed and the
listed hypotheses do not survive the listed thresholds.* It will **not** mean the layout
channel is closed — the explicit `not_covered` list in RESULTS.md governs. The words
"exhausted", "closed" and "unsolvable" will not appear in the results of this lane.
