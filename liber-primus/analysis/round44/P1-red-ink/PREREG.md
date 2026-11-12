# Round 44 / P1 — THE RED-INK CHANNEL, READ IN FULL — PRE-REGISTRATION

_Dated 2026-11-09, written BEFORE any extraction, census, or decode output from this lane._
_Plan of record: `../CAMPAIGN-PLAN.md` lane P1 (X0 NEW #1, blind convergence 4/6 + F2 HIGH ×2)._
_Doctrine: `../../../ARMADA-DOCTRINE.md` (binding). Oracle path: `../../../HUMAN-ORACLE.md`._

## 0. Hypothesis

The red ink in the relikd Liber Primus masters is a data channel the solver rig has never
represented. Specifically, one or more of:

- **H-a (selection):** the subsequence of canon runes rendered in red is, or keys, a message
  (book-wide or per-section, forward or reverse) beyond the already-established fact that the
  red *text-runes* restate each page's own opening words (prior art, §2).
- **H-b (standalone symbol stream):** the red non-rune marks — the dot-matrix blocks (the
  13-dot vs 10-dot distinction the R43 blind agents flagged), red numerals, the red p53
  paragraph, red drop-caps/devices — form their own symbol stream (dot counts as values,
  13-vs-10 as bits).
- **H-c (key-parameter carrier):** per-page red statistics (count of red runes, position of the
  first red rune, cumulative red count) are offsets/seeds into the solved-page generator family
  (prime / prime-totient / totient streams, `src/lp/ciphers.py`), applied to that page.

Null: the red is rubrication + decoration; every reading scores below the fixed bars.

## 1. Ledger coverage queried (before any run)

- **No covering row exists.** `LEDGER.json` (309 entries) greps zero rows for
  red-rune/rubrication; R43 `X0-firewall/ADJUDICATION.md` item 17 adjudicates the red-ink
  channel **NEW**: "No covering row."
- **Adjacent rows, cited, all disclaiming colour verbatim:**
  - `A-06` not_covered: "Ink outside the 109 boxes. Colour/chroma channels (only 8-bit
    luminance was read)."
  - `B-12` not_covered: "Colour/chroma"; reopens_if (iii) "any falsifiable interpretation of
    the p15 `3299` ink-tone marking"; (iv) "transcription of the p53 grey text rows".
  - `R19-FINITE-ORNAMENT-REGISTER` not_covered: "Colour/chroma band channels".
- **Prior art NOT repeated** (not a ledger row): `analysis/armada_osint/redrune/` (2026-07)
  extracted the 187 red text-runes via the verified stones glyph-box alignment and established
  they are rubricated section-opening words; its cryptanalysis used the **legacy English-only
  scorer** (`score_norm`, the exact L7-A conditional) at ~30 configs. This lane (i) re-reads
  the red selection stream under the standing 12-register panel (a register-axis extension, not
  a re-run of a measured cell), (ii) reads everything redrune did NOT read: non-rune red marks,
  dot blocks, numerals, the p53 paragraph, and the key-parameter reading.
- **Eliminated cells not re-run:** no key-space sweep from R8–R42 is re-executed; reading (c)
  uses red-derived offsets only (≤3 per page), not a generator re-sweep (the generator families
  themselves are swept elsewhere, e.g. R11-N2/N5, B-04 — this lane tests only the red-pinned
  cells of that space, which no row pins).

## 2. The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit is a red-selected (or red-parameterised) decode whose panel-R36 `pmax` clears the
pre-registered bars_v3 family-wise bar at its length, non-degenerate. The recognizer is written
before the search and a positive control is PLANTED THROUGH THIS LANE'S OWN GLUE (R42 X1 rule):
a known plaintext is embedded as synthetic red marks in copies of the page images, and the
lane's own extractor + reader must recover it end-to-end (§5). No verdict without the plant
passing.

**Q2 — What measured fact raises this family's prior above the flat rate?**
(i) 4/6 R43 blind agents independently converged on the red channel
(`round43/X0-firewall/ADJUDICATION.md` item 17 — the highest convergence of any uncovered
item); (ii) F2 physical-channel inventory independently ranks it HIGH ×2 with zero rig
representation; (iii) three adjacent ledger rows disclaim colour verbatim (§1); (iv) the
pp49–51 precedent: an entire 2048-bit payload sat invisible to the loader for six campaigns —
exactly this class of channel.

**Q3 — Is the space bounded, and by what?**
Enumerable and finite. The object is every red pixel on the 56 relikd masters (2400×3600).
The census enumerates it completely. The reading matrix is fixed (§4): ≤ 8,734 decodes
(bar N fixed at 10,000, conservative). The lane states what fraction of red marks each
reading consumed.

**Q4 — The three conditionals this lane's negative will carry** (`three_conditionals`):
- **key_space:** red-selection affine readings (2 dirs × a∈{1,−1} × s∈0..28); red-as-key over
  the black stream (2 key dirs × {vigm,vigp,beau} × {±atbash} × all 187 rotations); red-derived
  offsets {r_p, firstpos_p, cum_p} into {prime, prime−1, totient} streams × 6 configs. NOT
  covered: any other function from red marks to keys, red as transposition order, red
  cross-page permutations, chroma channels other than the red rule's band.
- **transition_model:** monoalphabetic affine + periodic/one-shot stream ciphers
  (vigm/vigp/beau ± atbash). No chained/output-aware constructions (the pinned LP2 model is
  only reachable here if red directly carries plaintext or a simple stream key).
- **adjudicator_register:** panel-R36's 12 registers (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE,
  DE, CY, EN_HALFVOWEL, EN_NOVOWEL + R36 additions). Registers outside the panel (Hebrew,
  Greek, numeric/schema payloads) not covered.

**Q5 — Kill condition at 10% of budget:**
If the positive-control plant fails to recover through the lane's own extractor+reader after
one debugging pass of the GLUE (never of the threshold), the lane is KILLED and reported
inconclusive-instrument. If the census finds the red rule fires on < 50 glyphs of the known
p0 rubricated opening (validation target, prior art says the rule is bimodal and stable), the
rule is declared broken and the lane stops.

## 3. Standing instrument + FIXED thresholds

- Adjudicator: `analysis/round19/I2/adjudicate.py` `adjudicate` / `adjudicate_batch` with
  `Panel(data/panels/panel-r36.npz)` — exactly as wired in R43 F5b-T.
- Bars: `analysis/round34/I1-v3-null/bars_v3.py` `bar_v3(N, L_cap, "free")`, **N fixed at
  10,000** (≥ the planned matrix upper bound 8,734; conservative). L_cap = largest node
  ≤ decode length, min node 120 (the F5b-T standing convention; decodes with L ≥ 60 are scored
  against the 120 node, L < 60 are not adjudicable and are census-only / not_covered).
- **Bars of record (computed 2026-11-09, before any run):**

  | L_cap | bar (pmax) |
  |---|---|
  | 120 | **12.8507** |
  | 240 | **17.1842** |
  | 400 | **18.5252** |
  | 729 | **21.5296** |

- A decode crosses iff non-degenerate AND pmax ≥ its bar. Any crosser is
  **FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never self-certified.
- These thresholds are fixed in advance and will not be edited after results; any addendum is
  dated with reason.

## 4. The fixed test matrix

**Census (C):** red mask on all 56 `data/relikd/p*.jpg` masters with the verified rule
`R−(G+B)/2 > 40 & R > 120 & G < 80`; connected components (scipy.ndimage.label), noise floor
area ≥ 20 px; each component classified exactly once:
RED_RUNE (overlaps a stones glyph box, red-fraction > 0.30 per prior-art verified rule) /
DROP_CAP (height > 300 px) / DOT (small compact blob, clustered into blocks by ≤ 60 px·scale
proximity) / NUMERAL / PARAGRAPH (p53 red text region) / OTHER. Rule validation gate: the
glyph-level extraction must reproduce the prior-art 187 red text-runes (±0: it is the same
deterministic rule on the same masters) and the canon p0 opening `HEOGMIAFSYENGC`.

**Reading A (selection, H-a):**
- A1: global red-rune stream (canon reading order, expected L=187): {fwd, rev} ×
  x→(a·x+s) mod 29, a∈{1,28}, s∈0..28 → 116 decodes, bar L_cap 120.
- A2: per-section substreams (sections = the 10 `$`-delimited canon segments): same 116-map
  family for every substream with L ≥ 60, bar L_cap 120. Upper bound 1,160 decodes.
  Substreams with L < 60: census-only, recorded not_covered.
- A3: red stream as KEY over the black stream (all non-red canon runes, L≈12,577): key dirs
  {fwd, rev} × cfgs {vigm, vigp, beau} × {plain, atbash-ct} × rotations 0..186 → 4,488
  decodes, bar L_cap 729.

**Reading B (standalone stream, H-b):** dot-block census → ordered block sequence (page order,
top-to-bottom). Enumerated readings: (i) 13-dot→1 / 10-dot→0 bits, both polarities, reported
as bits + 5-bit groupings; (ii) dot counts mod 29 as rune indices. If any such stream reaches
L ≥ 60 it is adjudicated (116 affine maps, bar L_cap 120); below that, complete enumeration is
reported with NO panel verdict (the instrument has no bar there — honest not_covered).

**Reading C (key-parameter, H-c):** for each of the 55 unsolved canon pages, offsets
O_p = dedup{r_p (red-rune count on page), firstpos_p (canon index on page of first red rune,
0 if none), cum_p (cumulative red count before page)}; generators
G = {prime_stream, prime_totient_stream, totient_stream(start=2)}; key k_i = g[o + i];
configs {vigm, vigp, beau} × {plain, atbash-ct}. ≤ 55 × 3 × 3 × 6 = 2,970 decodes, bar at
the page's L_cap.

Planned-matrix upper bound: 116 + 1,160 + 4,488 + 2,970 = 8,734 ≤ N = 10,000.

## 5. Positive controls (planted through THIS lane's own extraction+decode glue)

- **P1 (image → extractor → reader, end-to-end):** take the first 120 rune indices of the
  solved-page plaintext "WELCOME PILGRIM …"; walk the canon in reading order restricted to
  pages with no genuine red, greedily selecting glyphs whose canon rune matches the next
  plaintext rune; paint each selected glyph's stones box red (the verified red RGB ≈ (200,2,3))
  in COPIES of those page images; run the lane's own red-mask + box-overlap extractor on the
  copies; the extracted red-selection stream must equal the planted 120 indices EXACTLY, and
  its direct reading (a=1, s=0) must clear the L_cap-120 bar (12.8507) under panel-R36.
- **P2 (dot-block census):** paint one 13-dot and one 10-dot red block (dot radius ~10 px,
  real-block-like spacing) onto a copy of a no-red page; the lane's own census must return
  exactly two planted blocks with counts [13, 10] in order.
- **P3 (reading-C decode glue):** encrypt the known "A WARNING …" plaintext (240 runes) with
  k = prime_totient_stream offset 17, vigm; feed the synthetic page + planted red-count
  parameter 17 through the SAME reading-C sweep function; it must recover the plaintext at the
  planted cell (gen=prime_totient, offset=17, cfg=vigm) with pmax ≥ bar(240) = 17.1842.

**No verdict is issued unless P1, P2 and P3 all pass.** `positive_control` in the ledger rows
will be exactly "passed" with detail in `control_detail`.

## 6. Coverage statement (to be finalised with numbers in RESULTS.md)

This lane enumerates the red channel completely at the census level (every red component on
the 56 masters is counted and classified; the fraction of red marks consumed by each reading
is reported) and tests the three pre-registered reading families at the fixed bars. It does
NOT cover: chained/output-aware uses of red parameters; red as transposition/permutation
order; non-red chroma channels; registers outside panel-R36; sub-20-px red components
(JPEG chroma noise floor); readings of red marks on non-page artifacts (0_wisdom.jpg).

## 7. three_conditionals (schema block for ledger_rows.json)

```json
{
  "key_space": "red-selection affine (2 dirs x 58 maps); red-as-key over black (2 x 6 x 187 rotations); red-derived offsets {count,firstpos,cumcount} x {prime, prime-1, totient} x 6 cfgs. Other red->key functions, transposition, chroma bands outside the red rule: not covered.",
  "transition_model": "monoalphabetic affine + periodic/one-shot additive/Beaufort streams (+/- atbash); no chained/output-aware constructions.",
  "adjudicator_register": "panel-R36 (12 registers); Hebrew/Greek/numeric-schema payloads not covered; streams with L<60 not adjudicable (census-only)."
}
```

## ADDENDUM 1 (2026-11-09, after census C, BEFORE any reading/decode run)

The census (validation gate PASSED: reproduces the prior-art 187 glyph-level reds and canon-p0
`HEOGMIAFSYENGC`) found the prior-art stream is incomplete and carries one false entry. The
selection channel of record for readings A and C is therefore the CENSUS-CORRECTED stream:

1. **False entry removed:** the img-p37 "red rune ᚱ" (gli 418) is the red Arabic numeral **4**
   missegmented as a rune by the stones segmenter (bbox [602,669,2570,2665] is the digit).
   → 186 genuine glyph-level reds.
2. **Added — red runes the stones segmentation never held:**
   (i) the p15 red TITLE line = canon rune positions 3603–3611, `FULM AEAYOEA` (9 runes, all
   red, census OTHER comps); (ii) the p53-image red closing word = canon 12644–12647 `URPN`
   (4 runes); (iii) the 13 red DROP-CAP initials (height-excluded by the segmenter; each is the
   canon rune immediately preceding its red run, located geometrically).
3. Readings A1/A3 run on three fixed stream variants: `legacy187` (prior art, comparability),
   `corrected199` (186+title+URPN), `full212` (corrected + 13 drop-caps). Matrix N grows
   accordingly but stays under the pre-registered bar N = 10,000 **for A1/A2**; A3 (red-as-key,
   rotations scale with stream length) is run on `full212` + `legacy187` only, keeping total
   lane N ≤ 10,000. Bars unchanged (fixed at N=10,000).
4. Red numerals census (reading B scope): margin numerals **1,2,3,4,5** (imgs 36,37,37,37,38)
   are ALL red; grid cell **3299** (img 15) red. Dot blocks: 13-dot and 10-dot diamonds + red
   word-separator dots (1/2/4-dot) inside red text lines.
