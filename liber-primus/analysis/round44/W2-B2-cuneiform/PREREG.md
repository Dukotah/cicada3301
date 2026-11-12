# Round 44 / W2-B2 — CUNEIFORM CLUSTERS + DOT CONSTELLATIONS CENSUS — PREREG

_Dated 2026-11-09, written and hash-stamped BEFORE any census or read output existed
(R44 X1 hygiene fix: sha256 of this file echoed into run.log before first execution)._

## 1. Hypothesis

R43 X0 NEW item 20 (`analysis/round43/X0-firewall/ADJUDICATION.md` row 20): the book carries
**black non-runic ink with zero representation in any rig input** — a cuneiform-like
second-script cluster on p33 bottom / p36 top / p37 top (verified present in this lane's
`look/` previews before this PREREG was frozen — that is an existence check, not a read),
a 5-dot irregular scatter on p23 top, 3-dot divider rows, and (F2 #22) small dot clusters
beside the root-tree margin pairs. Hypothesis: one of these unlogged black channels carries
data readable as (a) a rune-index selection stream, (b) coordinate values, or (c) per-page
count values.

## 2. The five Aiming-Test answers

**Q1 — hit shape + recognizer.** A hit is (i) census-level: a black mark outside every
logged channel, located with page+bbox — recognizer is this lane's own census code, proven
by plant PC-A (a synthetic 6-glyph cuneiform-like cluster + a 7-dot constellation painted on
a REAL page copy must be found, classified UNLOGGED, dot count exact, centers within ±3 px);
(ii) read-level: any derived stream of length ≥ 60 rune indices whose panel-R36 pmax clears
the fixed bar below — recognizer proven by plant PC-B (≥60-rune known-plaintext selection
planted as black dots under canon glyphs on page copies, extracted by the SAME
dot→nearest-glyph glue, must recover the planted rune stream exactly and clear its bar).
Streams with L < 60 have NO adjudicable bar (pending W2-A1's short-stream bars): they are
enumerated verbatim, **measured-only, no verdict** — stated now so a "pass" cannot be
invented later.

**Q2 — measured fact raising the prior.** (a) `analysis/round43/X0-firewall/ADJUDICATION.md`
item 20: no ledger row covers these marks; A-06's own `not_covered` says "Ink outside the
109 boxes" and its `reopens_if` (iii) is "anyone extends the inventory past Round 8's
rejection rule". (b) Checked against `analysis/round19/C3/l3/bands.json` before freezing:
pages 34–38 contain ZERO of the 109 band boxes, yet p36/p37 visibly carry the cluster; on
p33 the cluster (y≈3050+) and the 3-dot row (y≈1740) lie outside all three p33 boxes
(B054 y667–1165, B055 y787–861, B056 y1908–2406). The inventory provably never reached
these marks. (c) `analysis/round43/F2-inventory/image-channels.md` rows 15/16 rank them HIGH
with "zero representation".

**Q3 — bounded?** Yes — doctrine R5 rank 1, a finite human-checkable object: all black ink
on the 57 relikd masters minus the logged channels, enumerable in one pass. Decode budget
**N = 2,000** total panel decodes (fixed; actual N reported).

**Q4 — the three conditionals this lane's negative will carry.**
1. *key space*: only the registered read families in §4 (selection stream fwd/rev × affine;
   coordinate/count enumerations); no transpositions, no keyed use of the marks over the
   black text.
2. *transition model*: DIRECT reads only (affine symbol maps); no keyskip/chained/
   output-aware construction is represented.
3. *adjudicator register*: panel-R36's 12 registers; numeric/schema/Hebrew/Greek payloads
   invisible; and L < 60 streams receive NO verdict at all.

**Q5 — kill condition at 10% budget.** (a) PC-A fails after at most ONE glue fix (thresholds
untouched; same allowance P1 used) → INSTRUMENT-INCOMPLETE, stop. (b) Census finds zero
UNLOGGED components on p23/p33/p36/p37 at the registered mask (premise artifacts absent) →
UNAVAILABLE-BY-PREMISE, stop. (c) Honesty gate: any cataloged object that is already a
censused device (red anything → R44-P1 census.json; the 109 band boxes → A-06; drop-caps →
R22-D features.json) is CITED, not recounted; R22-D's figural-motif reopener ("documented,
not executed") means margin art is cataloged here at bbox level but NOT read — reads are
restricted to the §4 families.

## 3. Instrument + fixed thresholds

- Census: luminance mask `mean(RGB) < 128` AND NOT red (P1's verified red rule
  `R−(G+B)/2>40 & R>120 & G<80` — red is P1's censused territory, cited not recounted);
  8-conn components, noise floor area ≥ 20 px (P1's). Classification, each component exactly
  once, priority order: RUNE_GLYPH (overlaps a stones glyph box padded 6 px) → BAND_COVERED
  (center inside one of the 109 `round19/C3/l3/bands.json` boxes; A-06's territory) →
  TEXT_PUNCT (small: area ≤ 2500 ∧ maxdim ≤ 60, center inside a stones text-line bbox
  padded x±40/y±10 — word separators/punctuation, logged in canon per R43 F2) → UNLOGGED
  (the census target), proximity-clustered into objects at gap ≤ 100 px, each cropped.
- Adjudicator: the standing panel-R36 (`round19/I2/adjudicate.py` +
  `data/panels/panel-r36.npz`), scored on rune indices.
- Bars, FIXED now via `analysis/round34/I1-v3-null/bars_v3.py` at the declared budget
  N=2,000, relation "free": **L120 11.9933, L240 15.9945, L400 17.4261, L729 20.3640**;
  L_cap rule = largest node ≤ L, else 120 (identical to P1's `bar_for`). Verdict against
  the bar at declared N=2000 (conservative if actual N is lower; actual N reported).
- Any bar-crosser (non-degenerate, confirmed by single-row re-adjudication) is
  **FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never certified.

## 4. Registered reads (and nothing else)

- **R-A cluster identity**: the 3 cuneiform cluster instances aligned pairwise by
  translation-only correlation; report IoU. IoU ≥ 0.95 → same stamp (information =
  placement only; enumeration). Measurement, not verdict.
- **R-B cluster decomposition**: per-instance component count, per-glyph bboxes, shape
  classes by normalized-overlap clustering. Enumeration (expected total glyphs « 60 →
  measured-only).
- **R-C dot selection stream**: every UNLOGGED dot component book-wide in reading order
  (page, then y, then x); each mapped to the nearest stones glyph center on its image →
  that glyph's canon rune index (nearest-glyph distance recorded; dots on glyph-free pages
  carry no mapping and are recorded as coordinates only). If the mapped stream has L ≥ 60:
  adjudicate fwd + rev × all 812 affine maps (a∈1..28, s∈0..28) = ≤ 1,624 decodes vs the
  fixed bar. If L < 60: enumeration only.
- **R-D per-page UNLOGGED counts**: 56-value stream (and the cuneiform cluster-count-per-
  page stream) — L < 60, enumeration only.
- **R-E p23 constellation geometry**: dot centers, pairwise distance matrix, angles,
  nearest-rune indices, counts — compared against the named constants {29, 3301, first
  primes, gematria values} as a RECORDED enumeration with NO verdict (n=5; no null exists).

## 5. Positive controls (before any real read)

- **PC-A** (census glue): synthetic 6-glyph cuneiform-like cluster + 7-dot constellation at
  known coordinates painted in black on a copy of a real page; SAME census code via
  `--images`; must find both, classify UNLOGGED, dot count 7 exact, centers ±3 px.
- **PC-B** (read glue): ≥60 runes of the solved LP plaintext planted as black dots directly
  under canon glyphs spelling it (walking canon in order over page copies); SAME census +
  R-C mapping; must recover the planted rune stream EXACTLY and its direct reading must
  clear the L_cap bar (L=120 bar 11.9933 if 60 ≤ L < 240).

No verdict is reported unless both relevant plants pass through this lane's own glue.

## 6. Cited ledger rows

A-06 (not_covered "Ink outside the 109 boxes"; reopens_if iii), R22-D-ILLUSTRATION-DROPCAP
(not_covered: figural-motif catalog "documented, not executed"), B-12 (colour/chroma +
layout not_covered), R44-P1-RED-CENSUS (red territory complete — this lane is black-only),
R19-FINITE-ORNAMENT-adjacent rows via A-06. Coverage wording verified against LEDGER.json
this date; none covers black non-runic ink outside the 109 boxes.
