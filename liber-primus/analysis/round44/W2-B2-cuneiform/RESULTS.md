# Round 44 / W2-B2 — CUNEIFORM CLUSTERS + DOT CONSTELLATIONS CENSUS — RESULTS

_Run 2026-11-09. PREREG.md hash-stamped in run.log (sha256 6bfdde40…f795f) before first
execution. Instrument: panel-R36 (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`);
bars FIXED via `round34/I1-v3-null/bars_v3.py` at declared N=2,000 "free" before any run.
Positive controls 2/2 PASSED through this lane's own glue. LEDGER.json not modified._

## Verdict

**Census: MEASURED — black non-runic ink is now enumerated book-wide for the first time
(912 UNLOGGED components → 124 objects, each classified exactly once and dispositioned in
`catalog.json`), and the census CORRECTS the blind-agent inventory in three concrete ways
(below).** **Readings: NEGATIVE at panel-R36 power for the one adjudicable stream (1,624
decodes, best 8.185 vs bar 15.995, 0 crossers, nothing FLAGGED-FOR-ORACLE); every other
registered read is a recorded enumeration with L < 60 — measured-only, no verdict exists
(pending W2-A1 short-stream bars).**

## 1. Positive controls (plant_results.json)

| plant | what it proves | result |
|---|---|---|
| PC-A | census glue end to end: synthetic 6-glyph cuneiform-like cluster + 7-dot constellation painted in black on a copy of real p1 | both found, classified UNLOGGED, 7/7 dots, center error 0.71 px (bar ±3) → **PASSED** |
| PC-B | read glue end to end: 120 runes of the solved "A WARNING…" plaintext planted as black dots under the canon glyphs spelling it, extracted by the SAME census + dot→nearest-glyph mapping | 120/120 extracted, **exact recovery**, pmax 26.668 ≥ bar 11.9933 → **PASSED** |

Two control-forced GLUE fixes, thresholds untouched (run.log, dated): (1) BAND_COVERED
restricted to non-TEXT band boxes — the raw 109-box rule swallowed in-text marks because
TEXT-class band boxes are the rune text column itself; (2) reading order row-bucketed
(ROW_GAP 40 px) — raw (y0,x0) sorting scrambled within-row x-order. Plus two plant-harness
(not glue) fixes: placement page range and baseline-subtraction proximity matching.

## 2. The census (census.json + catalog.json — the complete finite object)

All 57 relikd masters, mask `mean(RGB)<128 ∧ ¬red` (red = R44-P1's censused territory),
8-conn, ≥ 20 px: **18,051 components (15,186 RUNE_GLYPH + 1,118 TEXT_PUNCT + 835
BAND_COVERED + 912 UNLOGGED)**; the 912 UNLOGGED cluster into **124 objects**, all cropped
(`crops/`) and dispositioned exactly once (`catalog.json`, completeness-checked):

| class | n objects | identity | disposition |
|---|---|---|---|
| CUNEIFORM_CLUSTER | 7 | ONE 6-glyph cuneiform-like device: p33 bottom + tops of p34/p35/p36/p37/p38/p39 | NEW — read (R-A/R-B) |
| BIG_DOT_CONSTELLATION | 10 | p23-top 5-dot scatter + an **exact vertical-mirror twin on p7 bottom** | NEW — enumerated (R-E) |
| DOT_ROW | 6 | 3-dot divider rows p33 (70 px) and p39 (32 px) | NEW — enumerated (R-E) |
| MARGIN_ART | 67 | crosses/vines/trees/mayflies/root-trees + side dots; p32 blurred tree; p55 ghost tree | cataloged; CITE R22-D reopener (reads out of scope) |
| LEMNISCATE | 6 | infinity squiggles p0–p2, p15 | catalog (F2 #18) |
| UNSEGMENTED_RUNIC_TEXT | 8 | runic lines missing from stones segmentation (p6/p10/p32/p36/p37/p39/p41/p52) | CITE T1-05 not_covered + R44-P1 corrections 3/4 |
| PUNCT_DIAMOND_FRAGMENT | 11 | leaked components of ⁘-style diamonds at line starts/ends (+ the red "1" core) | CITE lane P3 (item 19) + R44-P1 |
| P15_NUMBER_GRID | 1 | the 4×4 Arabic grid, 59 digit components | CITE lane P2 (item 18) |
| PAYLOAD_LINE | 1 | p49 "2i 1J 3P 2v 1s 2O 0k 1M" | CITE A-04 / R28-L2 |
| SOLVED_PAGE_CONTENT | 6 | 0_wisdom.jpg own content (no stones glyphs exist for it) | catalog-only |
| ARTIFACT | 1 | p22 left-edge smudge | scan artifact |

**Three corrections to the R43 blind-agent inventory (F2 #15/#16/#17):**
1. The cuneiform cluster is on **seven** pages, not two: p33 bottom and the TOPS of
   p34–p39 (blind agents reported p33/p36-37). It brackets exactly the p33–p39 section.
2. The p34–p39 instances are **bitwise identical** (pairwise translation-aligned IoU
   1.0000); the p33 instance is the same device at IoU 0.853 (sub-pixel resampling at a
   different y). It is a repeated digital stamp: its only degrees of freedom are
   *placement*, and placement = section header/footer.
3. The p23 5-dot "constellation" has an unreported **twin on p7 bottom**: same five x
   centers to 0.0 px, y mirrored (y₂₃ = 3675 − y₇, max deviation 0.5 px; results.json
   `mirror_twin` — the coded strict-equality flag reads false on the 0.5 px pair, the
   measured residuals are the record). A vertically-mirrored ornament pair bracketing
   pp. 7–23 is furniture symmetry, not an irregular star map; the "irregular placement
   looks positional" reading of F2 #16 does not survive the census.

## 3. Readings vs the fixed bars (results.json)

| read | N decodes | best pmax | bar | result |
|---|---|---|---|---|
| R-A cluster identity | — | min IoU 0.853 (p33×6 pairs); 1.0000 within p34–p39 | registered 0.95 | same_stamp=False by the letter of the rule, driven solely by the p33 resampling; 6/7 bitwise identical |
| R-B decomposition | — | 7 components per instance, geometry persisted | — | enumeration |
| R-C dot stream: 356 UNLOGGED is_dot comps (row-major, p0–p55) → nearest-glyph rune indices, L=356; fwd/rev × 812 affine | 1,624 | 8.185 (rev, a=11, s=2, reg 8) | **15.9945** (L_cap 240) | **NEGATIVE, 0 crossers** |
| R-D per-page UNLOGGED counts | 0 | 56 values | none exists | measured-only |
| R-E constellations/rows | 0 | coordinates, pairwise distances, mirror relation, nearest-rune mapping (dists 410–710 px — the dots sit far from any text), n ∈ {3,5} | none exists | measured-only |

Doctrine-R3 statistics for the R-C best decode persisted (`best_full_stats`: en −7.78,
ioc 1.207, mds 7, h2 0.962, zl 0.570, pmax_ne 8.185, pcon 8.004, non-degenerate). Best is
7.8 below its bar; nothing approached FLAGGED-FOR-ORACLE.

## 4. Coverage × not_covered

**Covered:** 100% of ≥20 px black components on the 57 masters classified exactly once;
124/124 objects dispositioned; the one adjudicable derived stream read at panel-R36 power
over fwd/rev × all 812 affine maps; the cluster identity measured pairwise over all 7
instances; both constellations and both dot rows enumerated to the pixel.

**not_covered (the PREREG Q4 conditionals, plus census limits):**
- *key_space:* only direct affine reads of the nearest-rune dot stream; no transposition,
  no keyed use of the marks against the rune stream, no placement-as-key constructions
  (the stamp's 7 placements and the mirror pair are enumerated but not swept as keys).
- *transition_model:* direct reads only — no keyskip/chained/output-aware construction.
- *adjudicator_register:* panel-R36's 12 registers; numeric/schema/Hebrew/Greek invisible;
  **every L < 60 stream (constellation n=5, rows n=3, per-page counts 56, cluster glyphs
  ~42) carries NO verdict** — enumerations are preserved ready-to-score (reopens when
  W2-A1 lands short-stream bars).
- *census mask:* ink with mean(RGB) ≥ 128 (the p55 ghost tree is only partially above
  threshold — its sub-threshold remainder is item-30 territory), sub-20 px components,
  marks inside non-TEXT band boxes (A-06's territory by construction), 0_wisdom reads
  (no stones glyphs), and the cuneiform glyphs' identification against real cuneiform
  sign lists (no network in-lane; shapes persisted for offline comparison).

**Reopens if:** (i) W2-A1 ships bars for L<60 (all short enumerations in results.json are
ready); (ii) a placement-as-key or marks-as-key decoder construction is registered (R1-lane
territory); (iii) sign-list identification of the 6 cluster glyphs yields a reading.

## 5. Files

- `PREREG.md` (hash-stamped in `run.log` before first execution) — Aiming Test + fixed bars
- `census.py` → `census.json` — the complete black-ink census; `crops/*.png`
- `glue.py` — shared dot→rune mapping + reading order (used identically by plant and reads)
- `plant.py` → `plant_results.json` — PC-A/PC-B (both passed)
- `reads.py` → `results.json` — R-A…R-E vs the fixed bars + doctrine-R3 stats
- `catalog.json` — all 124 objects dispositioned (completeness-checked)
- `ledger_rows.json` — draft rows; LEDGER.json NOT modified
- `look/` — identification previews (regenerable; .gitignore candidate per repo policy)

Reproduce: `python3 plant.py && python3 census.py && python3 reads.py`
(pure python3, no network).
