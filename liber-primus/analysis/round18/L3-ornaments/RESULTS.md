# L3 — ORNAMENTS & LAYOUT · RESULTS

_Round 18. Ledger items **A-06** and **B-12** (both `never-run`). Parked item **P-9**.
Pre-registration: `PREREG.md`, written before any measurement._

**STATUS: IN PROGRESS — this file is updated as each stage lands.**
Last update: 2026-08-25, after calibration gate G-A.

---

## 0. Data integrity (precondition)

`python3 liber-primus/handoff/capsule/verify_capsule.py --only images` →
**PASS, 56/56 sha256 intact.** The local `data/relikd/p*.jpg` were verified, not
re-downloaded blind.

Additional provenance fact established this lane and **not previously recorded anywhere in
the repo**: the vendored 2014 render set at
`corpus/E-tooling/vendor/cicada-solvers__documenting-cicada3301-scream314/assets/2014/liber-primus-complete/`
is the **same lineage** as `data/relikd/` — asset `17.jpg` is **byte-identical by sha256**
(`197e1e153958b9a2…`, 695,525 B) to `data/relikd/p0.jpg`. That matters because it supplies
something the relikd mirror does not: the **cryptographically solved** pages (`73.jpg` =
LP2 p56, `74.jpg` = LP2 p57, plus the LP1 pages 01/03/05/06/14) at the identical
2400×3600 render, and therefore a real solved-page control for a glyph reader.
relikd serves p0…p55 only; `p56.jpg`/`p57.jpg` return **404** (checked).

---

## 1. What the 47 bands actually are (stage 1 — inventory, complete)

`inventory.py` re-runs the row-grouping and ornament-rejection logic of Round 8's
`geometry/analyze.py` (62 rows) and `analyze2.py` (47 rows) and, critically, **restores the
y coordinate that `ornaments.json` drops** — the stored file is
`[page, x_lo, x_hi, n_components, median_height]` with no y, which is why nobody could crop
these bands even if they wanted to. Union, deduped: **109 band records across 39 pages**
(`inventory.json`).

**30 of the 109 have n ≤ 16 glyphs** — P-9's "only real candidates".

The first substantive result of this lane is that the 47/62 catalogued bands are **not one
population**. They are four, and only one of them is ink anybody should care about:

| class | what it is | how many | verdict |
|---|---|---|---|
| **T — mis-grouped rune text** | ordinary text lines that the Round 8 heuristic rejected because a *marginal vine ornament* merged several rows into one tall band (`h` = 671–2167 px, `n` = 11–37, `medh` = 114 = the rune body height) | ~62 | not ornaments at all; already in the ciphertext |
| **W — woodcut illustrations** | the cicada (p2/p3), the wing (p14), the reclining figure (p22), the trees (p32/p55), the cicada at p54/p55 | ~10 | pictures, no glyph content |
| **V — vine / floral marginalia** | the page-border swirls on pp. 40–55 and the tree ornaments on pp. 8–14; also the 8 px × 39 px hairline slivers on p24/p26 that are single vine strokes | ~30 | decoration |
| **D — non-runic DATA that the pipeline threw away** | the **alphanumeric blocks on pages 49, 50 and 51** and (adjacent, same failure mode) the **4×4 numeric grid on page 15** | 7 | **this is the find** |

### 1a. The load-bearing discovery

Round 8's ornament catalogue contains, mislabelled as ornament, the pages of the Liber
Primus that are **not runic at all**. `analysis/geometry/*` rejects a band when it sits
outside the dominant text column or when its median component height exceeds 240 px — and
the alphanumeric lines on pp. 49–51 are shorter than rune lines and sit inside a vine frame,
so they were dropped as "non-text".

Concretely, three of P-9's short-band candidates are these:

| band | page | n | what it actually reads |
|---|---|---|---|
| `B096` | 50 | 16 | `2M 0w 3L 3D 2r 0S 1p 15` |
| `B098` | 51 | 16 | `28 2a 0J 1L 0c 3C 2o 0X` |
| `B100` | 51 | 8 | a full-width slice: two vine fragments + a sliver of the row below |

`B096`'s reading is **independently confirmed byte-for-byte** by two vendored community
transcriptions already in this repo
(`corpus/E-tooling/vendor/cicada-solvers__cmbsolverwp/cmbsolver-lpviewer/files/text/lb/50.txt`
and `corpus/E-tooling/vendor/cicada-solvers__libergo/cmd/base60/base60numbers.txt`), which
is a genuine cross-check of the vision read rather than a claim on trust.

So P-9's "16-glyph bands" are **not 16 runes**. They are 16 *characters* — eight
two-character tokens of the form `[0-4][0-9A-Za-z]`. Any hypothesis that treated them as a
16-rune Gematria string was going to be testing the wrong object.

### 1b. A second, unrecorded typesetting anomaly (page 15)

While cropping, one page-15 element turned up that is **not in `ornaments.json`, not in any
community transcription in this repo, and not mentioned anywhere in the analysis tree**: in
the 4×4 numeric grid

```
3258 3222 3152 3038
3278 3299 3298 2838      <- 3299 is rendered in GREY, every other number is BLACK
3288 3294 3296 2472
4516 1206  708 1820
```

the entry **3299 is set in a lighter ink than the other fifteen**. The community
transcriptions (`data/scream314_lp.md:1595`, cmbsolver, libergo) record the *digits* and
lose the *colour*. Whether this is deliberate marking or a render artifact is measured in
§4 below; either way it is a typesetting-channel observation that this repository did not
previously hold. This was found by inspection, not by a pre-registered test, and is treated
as such (see the addendum in `PREREG-ADDENDUM.md`).

---

## 2. Calibration of the glyph reader (gate G-A)

**Instrument:** the validated R9 template-DP reader (`analysis/retranscribe/templates.npz`
+ the stored 29-class bijection in `retranscribe/diff_report.json`), driven through one
shared code path (`reader.py: read_ink_strip`) so that the calibration number describes the
same machine that reads the bands. The Round 12 front-B **forced** re-segmentation
instrument is not used anywhere in this lane — it fails its own control at 12.9%.

**Measured, whole-page, per-glyph agreement against the decryption-verified rune sequence:**

| control page | typeface era | glyphs read | canon runes | agreement |
|---|---|---|---|---|
| `73.jpg` = LP2 p56 (solved, φ(prime) shift) | LP2 | 96 | 85 | **86.5%** |
| `74.jpg` = LP2 p57 (solved, default-gematria substitution) | LP2 | 109 | 95 | **81.7%** |
| `14.jpg` A KOAN (circumference) | LP1 | 237 | 319 | 70.2% |
| `01.jpg` A WARNING | LP1 | 182 | 184 | 50.5% |
| `05.jpg` SOME WISDOM | LP1 | 90 | 157 | 50.3% |
| `03.jpg` WELCOME | LP1 | 283 | 394 | 32.7% |
| `06.jpg` A KOAN | LP1 | 224 | 742 | 25.3% |
| **pooled** | | 2,001 | | **44.2%** |

Whole-page pooled agreement is **44.2%**, which is **below the pre-registered 90% bar**, so
**gate G-A FAILS as first measured**. Two things about that number, both stated so it is not
over- or under-read:

1. The split is structural, not random: the two pages in the **LP2 typeface** (73/74 —
   the same face as every page in this lane's target set) score 81.7–86.5%, while the LP1
   pages score 25–70%. The templates in `templates.npz` were clustered from LP2 renders, so
   LP1 is out of the instrument's domain. Pooling them understates the reader on its own
   target set and overstates the pooled figure's relevance.
2. The residual on 73/74 is **row segmentation**, not glyph identity: the reader emits
   96 and 109 glyphs where canon has 85 and 95, i.e. it over-segments (vine ink and
   separator dots read as glyphs), exactly the failure Round 12 front B characterised. On a
   correctly isolated line the read is verbatim correct — reading page `05.jpg` line by line
   returns `SOMEWISDOM`, `THEPRIMESARESACRED`, `THETOTIENTFUNCTIANISSACRED`,
   `ALLTHNGSSHOULDBEENCRYPTED` against canon `SOMEWISDOM`, `THEPRIMESARESACRED`,
   `THETOTIENTFUNCTIANISSACRED`, `ALLTHNGSSHOULDBEENCRYPTED`.

**Consequence, applied honestly:** the reader is good enough to *classify* band ink
(runic vs decorative vs alphanumeric) and good enough to read a cleanly isolated rune line,
but the pooled solved-page number does not clear the bar this lane set in advance. Bands
are therefore reported with their read **and** their per-glyph match cost, and any band
whose read is not corroborated is labelled **UNRESOLVED-AT-THIS-ACCURACY** rather than
asserted. No hypothesis in §3 is scored on an uncorroborated band read.

---

## 3. Hypothesis verdicts

_(pending — filled in as each test lands)_

---

## 4. B-12 — line geometry and line fill

_(pending)_

---

## 5. Coverage / not covered

_(pending)_
