# Round 44 / WAVE-2 CELL C1 — THE FIGURAL-MOTIF CATALOG — PREREG

_Dated 2026-11-09, written and hash-stamped into `run.log` BEFORE any census, plant or read
output existed (R44 X1 hygiene fix). Cell dir: `analysis/round44/W2-C1-motifs/`.
Pure python3 (numpy/scipy/PIL), no network. Masters: `liber-primus/data/relikd/p0..p55.jpg`
(2400x3600). Canon: `data/krisyotam_runes.txt` (13,136 runes, 57 `%`-segments)._

## 1. Hypothesis

`R22-D-ILLUSTRATION-DROPCAP.not_covered[0]` names this cell verbatim: "Figural-motif catalog
(type/count/orientation of crosses, trees, shrouded-corpse figure, mayflies) per page — THE
REOPENER ... Documented, not executed." Its `reopens_if`: "A per-page figural-motif integer
sequence (type/count/orientation ...) is catalogued and tested against the same seed-3301
null." Hypothesis: the figural/illustrative elements of the 56 relikd pages carry data — as
per-page count values, as an orientation symbol stream, as a motif-type sequence, or as key
parameters into the solved-page cipher-generator family over the page they sit on.

## 2. Cited ledger rows (`not_covered` verified before freezing; `ledger_rows.json` draft cites these)

- **R22-D-ILLUSTRATION-DROPCAP** (negative, drop-cap channel only, min p=0.18): the quoted
  `not_covered` + `reopens_if` above. Drop-caps themselves are COVERED (presence / position /
  order / gap / centroid / illuminated-rune identity, 58 pages) → drop-caps appear in this
  catalog as an *excluded-from-reads* class.
- **A-06** (measured): ornament *bands* — all 109 band records read end-to-end, content
  negative. Bands/separator strips are an excluded-from-reads class here; A-06's own
  `not_covered` ("Ink outside the 109 boxes", colour channels) and `reopens_if` (iii)
  ("anyone extends the inventory past Round 8's rejection rule") is exactly what a figural
  census does.
- **R30-C1-ART-ATTRIBUTION** (negative): attribution-of-artist only; its coverage line
  ("shroud/mayfly/trees/drop-caps/borders") is OSINT sourcing, not a per-page type/count/
  orientation catalog and not a data read. No overlap with this cell's reads.
- **W2-B2 (this round, wave-2)**: cuneiform-like clusters + dot constellations census —
  dot clusters and the p33/p36/p37 second-script clusters are B2's, excluded here.
- **R44-P1 (wave-1)**: the red-ink channel (red dots, red runes, red numerals) — red marks
  are P1's, excluded here. This cell is the BLACK-channel figural/pictorial census.
- Scanned all 322 `LEDGER.json` entries for motif/mayfly/figural: only the three rows above
  touch the space; none executes a figural type/count/orientation catalog. CONFIRMED OPEN.

## 3. The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
(i) Census-level: a complete per-page feature-vector catalog (type, count, orientation,
normalized position, size of every figural element) — recognizer = this cell's own census
glue (programmatic ink-component detector + agent-visual classification of saved crops),
proven by plant PC1 (synthetic motifs composited into REAL page copies must be recovered
with exact type counts and correct orientations) BEFORE any real page is catalogued.
(ii) Read-level: a stream statistic crossing the fixed Bonferroni bar (§5a), a panel-R36
pmax crossing its matched-length bar (§5b), or a keyed generator decode crossing
`bar_v3(N, L, "free")` (§5c) — each recognizer proven by its own plant (PC2/PC3). Any
crosser is FLAGGED-FOR-ORACLE per `HUMAN-ORACLE.md`, never certified here.

**Q2 — Measured fact raising the prior.** R22-D's row carries priority
`high-prior-bounded-novel` and names this catalog as THE reopener; its drop-cap channel was
the first art channel ever read and the figural channel has never been coded as data
(file: `LEDGER.json` row R22-D-ILLUSTRATION-DROPCAP). Direction prior: R43 X0/SYNTHESIS §1 —
every blind-NEW item lives in presentation channels the rig never represented; the loader
discards all non-rune ink (F2). Honest label: the *census* is high-prior bounded-novel; the
*reads* over it are the registered battery of a bounded object, not a key-space sweep.

**Q3 — Bounded space?** ENUMERABLE and small. 56 pages; expected O(10–30) figural elements
book-wide; feature vectors are finite integers/labels. Reads: battery = 6 fixed statistics x
(≤ 4 stream families); panel reads = 116-map grid x (≤ 8 streams) ≤ 928 decodes; generator
reads ≤ 16 decodes x (≤ 15 motif pages) ≤ 240. Total panel-adjudicated decodes capped at
**N_CAP = 1300** (bars computed at N_CAP; actual N reported).

**Q4 — The three conditionals of a negative.**
1. *Key space*: the catalog's feature streams (counts, orientations, type sequence, position
   ranks) and the fixed generator family of §5c keyed by them — nothing else.
2. *Decoder transition model*: direct/affine reading grid (the W2-A1 116-map grid: {fwd,rev}
   x a∈{1,28} x s∈0..28) for value streams; {shift, atbash+shift, totient-stream,
   prime-totient-stream, vigenère(type-count vector)} with interrupters=True (solved-page
   convention), sign ±, for page decodes. No chained/autokey/reset constructions.
3. *Adjudicator register*: panel-R36 (12 registers) + the seed-3301 order/identity battery
   (language-agnostic); agent-visual classification for the census itself. A negative says
   nothing about registers outside panel-R36 or constructions outside (2).

**Q5 — Kill condition at 10% of budget.** (a) If PC1 (census plant) fails and one dated
repair addendum does not fix it → **INSTRUMENT-INCOMPLETE**, stop, no real census verdict.
(b) 10% checkpoint: after the detector pass over the first 10 pages, if it flags > 40
regions/page (segmentation meltdown) → stop and repair before proceeding. (c) If the real
census finds < 3 figural-bearing pages outside the excluded classes, the stream reads are
underpowered; the battery still runs (cheap) but the verdict is reported as *measured* with
the small-N power stated, not as a clean negative.

## 4. Census instrument (fixed before running)

- **Detector** (`scripts/census_detect.py`): grayscale luminance; ink mask at TWO thresholds
  (black ink Y<128; pale/grey ink Y<200 — the second catches low-alpha art like the p55 grey
  tree); connected components (scipy.ndimage, 8-conn) on a 1/2-scale image; candidate
  figural regions = components (after merging components with bbox gap ≤ 24 px) whose merged
  bbox exceeds 110 px in BOTH dimensions at full scale OR exceeds 200 px in one dimension
  with aspect < 10 (excludes rules/lines), and which are NOT rune-text lines (a region is
  text iff ≥ 60% of its rows have ink-run periodicity matching the page's modal glyph pitch;
  implemented as: region overlaps ≥ 2 detected text-line bands for ≥ 70% of its area).
  Every candidate region saved as a crop (`crops/pXX_rYY.png`), full page census preview too.
- **Classifier**: the agent reads every crop AND every full page image (56/56 — the visual
  full-page pass is the backstop for anything below detector floor). Fixed taxonomy:
  `cross, tree, corpse_figure, insect, emblem_circle, grid_square, humanoid_other,
  other_figural` (read classes) + excluded-from-reads catalog classes
  `drop_cap (R22-D), ornament_band (A-06), dot_cluster/cuneiform (W2-B2), red_mark (R44-P1),
  rule_line, latin_text_numeral (A-06 B098 / pp49-51 rows), text_artifact`.
  Orientation per motif: `up / down / left / right / diag` (crosses: `plus` vs `saltire`),
  `na` if symmetric/unoriented. Position: normalized centroid (x/2400, y/3600) + page third.
- **Catalog** = `results/catalog.json`: per page, list of motifs (type, orientation, bbox,
  centroid, size, source crop) + per-page feature vector (per-type counts, total).

## 5. Reads + FIXED thresholds (set before first run)

Streams (page order p0..p55, N_pages=56): **V1** total figural count/page; **V2_t** per-type
count/page for each read-class type present on ≥ 3 pages; **O1** orientation symbols of all
oriented motifs in page/reading order; **T1** motif-type token sequence in page/reading order.

**(a) Order/identity battery vs seed-3301 null** (numpy default_rng(3301), 10,000 draws each,
mirroring R22-D). Statistics: S1 presence-gap variance (pages with ≥1 read-class motif;
null = same presence count placed uniformly over 56 pages); S2 |Spearman rho|(V1, page index)
(permutation null); S3 zlib length of T1 vs permuted T1 (one-sided, more compressible);
S4 zlib length of O1 vs permuted O1 (one-sided); S5 count of prime values among nonzero V1
entries vs iid uniform draws on 1..max(V1) (size-matched); S6 |Spearman rho| of motif
centroid-y rank vs page index over motif pages (permutation). **Survivor iff any p <
0.01/6 = 1.667e-3** (family-wise 0.01, Bonferroni over the 6 statistics; if V2_t streams are
also tested, the divisor grows to 6 + #extra tests and is reported).

**(b) Panel reads** (V1 and any V2_t, as rune-index streams: values mod 29, L=56) through the
W2-A1 116-map reading grid (`../W2-A1-short-null/shortnull.py` — one shared code path, plants
included). **Degenerate-alphabet branch (pre-registered)**: if a stream has < 5 distinct
symbols (the standing R38 guard regime), its panel read is MEASURED-ONLY — enumerated, no
verdict, exactly as W2-A1 handled the 30-bit dot stream. If ≥ 5 distinct symbols: this cell
builds the missing L=56 null node with A1's POT machinery (two families, 1000 surrogates
each: PERM = permutations of the observed stream, DRAW = iid draws from its multiset; bar of
record = max over families at N_CAP=1300, alpha=0.01) and measures EN power at L=56 via A1's
held-out `english_windows` through THIS cell's path; verdict-capable iff EN power ≥ 0.5
(A1's registered floor). pmax ≥ bar → FLAGGED-FOR-ORACLE.

**(c) Generator-family keyed decodes.** For each page with ≥ 1 read-class motif and a canon
segment of L ≥ 31 runes: k = V1[page]; key vector = (per-type counts) mod 29 in fixed
taxonomy order (read classes, alphabetical). Family (interrupters=True, i.e. ᚠ passes
through unshifted — the solved-page convention; sign ∈ {-1,+1}): (1) shift by k; (2) atbash
then shift by k; (3) `prime_totient_stream` offset k (stream starts at prime index k);
(4) `totient_stream(start=2+k)`; (5) vigenère with the type-count key vector, atbash
∈ {off,on}. = 12 decodes/page. Adjudicate each with `round19/I2/adjudicate.py` panel pmax;
**threshold = `bar_v3(N_CAP=1300, L_page, "free")`** from `round34/I1-v3-null/bars_v3.py`
(L interpolated at the actual page length; pages with L < 120 use the L=120 node — flat
outside the nodes — stated as an instrument limit in RESULTS). pmax ≥ bar →
FLAGGED-FOR-ORACLE. Below bar → negative under Q4's three conditionals.

## 6. Positive controls (planted through THIS cell's own glue, run BEFORE any real target)

- **PC1 (census)**: composite 7 synthetic motifs into copies of p05 and p33 (3 crosses: 2
  plus-upright + 1 saltire; 1 tree ~400 px; 2 insects ~120 px, one inverted; 1 corpse-like
  figure ~500 px), positions logged. Bar: the full census path (detector + crop
  classification) recovers **7/7 with correct type and count, correct orientation on the
  saltire cross and the inverted insect, centroids within ±10 px**. No real page is
  catalogued before PC1 passes.
- **PC2 (keyed-decode)**: a 250-rune held-out English window (A1 `english_windows`) encrypted
  with shift k*=7; planted as a pseudo-page with planted count 7; MY §5c harness must decode
  it and clear `bar_v3(1300, 250, "free")`.
- **PC3 (battery + grid)**: (i) a planted monotone count stream (v[i]=i//8) must fire S2 at
  p < 1.667e-3; a planted periodic type sequence (ABCABC...) must fire S3 likewise.
  (ii) a 56-rune held-out English window pushed through MY stream→grid→panel path must
  reproduce A1-grid behaviour (pmax within float tolerance of calling shortnull directly).

## 7. Outputs

`run.log` (hash-stamped), `scripts/*.py`, `results/*.json` (catalog, battery, panel,
generator), `crops/*.png` (every cited crop), `RESULTS.md` (verdict, numbers vs bar,
coverage, not_covered), `ledger_rows.json` (schema: positive_control exactly "passed" with
control_detail; threshold_fixed_in_advance true; status from the controlled vocabulary).
Verdict vocabulary: measured / negative / flagged-for-oracle / instrument-incomplete; never
"closed". LEDGER.json is NOT modified.
