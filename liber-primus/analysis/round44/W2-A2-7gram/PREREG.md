# Round 44 / WAVE-2 CELL A2 — THE 7-GRAM, DIFFERENT-PLAINTEXT READING + THE p55-RUNE-0 CRIB — PREREG

_Dated 2026-11-09, written BEFORE any execution of this cell (no solver run, no plant, no decode;
the only numbers computed in advance are the bars_v3 thresholds from the committed fit and the
premise facts re-verified read-only from canon/corpus, listed in §1). Doctrine binds
(ARMADA-DOCTRINE.md). This file is hash-stamped into `run.log` before the first run (R44 X1
hygiene fix). No `git commit` from this cell._

## 0. What this cell is

R44-R1 proved the 7-gram ᛞᛄᚢᛒᛖᛁᚫ (indices 23 11 1 17 18 10 25, translit DJUBEIAE) at
p27:28 / p54:70 is the ONLY repeated 7-gram in the 57-page canon (expected pairs 0.005), that the
p54 occurrence CROSSES into p55 (a solved page), and that the SAME-plaintext anchored reading
excludes all 51 swept streams under page/section resets at every offset ≤ 200. Its rows left two
named open objects. This cell takes exactly those:

1. **DIFFERENT-plaintext reading** — enumerate key-difference constraints k1−k2 = ±(P1−P2) over a
   fixed plaintext-pair vocabulary and test satisfiability by LOW-COMPLEXITY key relations
   (constant shift, arithmetic progression mod 29, same-generator-different-offset for the 51
   standing keys).
2. **Positional numerology** — a fixed predicate table over the sites' coordinates vs the book's
   constants (measured-only, like the W2-A1 structural table).
3. **The p55-rune-0 crib** — p55 is solved (AN END, totient keystream, vigm/shift-down,
   `tests/validate.py`), so the 7-gram's 7th rune at the second site (= p55 pos 0, ciphertext
   ᚫ=25) has KNOWN plaintext A=24 and, under the known solve, KNOWN consumed key totient[0]=1.
   Any hypothesis whose key stream flows ACROSS the p54→p55 boundary (section-continuation or
   global stream) must satisfy a 1-rune key equation at that index. Use it as a filter over the
   51 standing keys × 6 configs × offsets, decode ALL 55 unsolved pages at surviving cells under
   panel-R36 vs bars_v3, and measure the FULL-p55 propagation depth of every survivor.

## 1. Cited ledger rows (verified open ground; LEDGER.json queried 2026-11-09 before writing)

- **R44-R1-SEVENGRAM** (measured) — not_covered verbatim: "The different-plaintext reading of the
  7-gram (two plaintext phrases colliding under different key segments); the p55-rune-0
  known-plaintext crib on the second site (p55 is solved - a 1-rune crib never exploited by any
  row); …". Items 1 and 3 of §0 are exactly those two clauses. reopens_if names "a pre-registered
  different-plaintext model is specified" — this PREREG is that specification.
- **R44-R1-RESET-SWEEP** (negative) — not_covered: "…unanchored offsets >29 and all offsets
  >200…; the different-plaintext reading of the 7-gram." My section-mode decodes run ONLY at
  offsets 30..200 (crib-anchored — a NEW anchor, not R1's empty same-plaintext anchor); R1's
  own o ≤ 29 section cells are NOT re-decoded (their crib-consistency flags are reported from
  the filter alone). R1 ran NO global-phase cells at all.
- Global-mode overlap check: the bash-orbit rows (R32-B1, R34-B1, R35-B1, R37-I2, R40-B1/B2…)
  score C[0]-aligned heads at key offsets 0..3 under keyskip relations — key indices ≈ 0..31 at
  canon START. My global cells tie key index to canon position (p54 start = 12880 + o): disjoint
  cells. Historical "solved-page stream applied globally" coverage is pre-panel English-only
  (L7-A); the panel-R36 register axis extends it (the same re-adjudication precedent R1's PREREG
  cites for its one overlapping cell).
- Premise facts re-verified read-only before writing this (allowed: they are the cell's cited
  inputs, not outputs): canon p27 start global 6527 → site A global 6555..6561; p54 start 12880 →
  site B global 12950..12956 (7th rune = p55 pos 0 = global 12956); p55 = 73.jpg, 85 runes, first
  rune ᚫ=25; `solve.find_interrupters(phi_prime)` reproduces AN END… with 1 interrupter
  (F-occurrence #3), plaintext first rune A=24. These match sevengram.json and validate.py.

## 2. The Aiming Test

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
Three recognizers, each plant-validated through this cell's own glue before any real target:
(A) the constraint solver: a hit = a vocabulary plaintext pair whose key-difference vector is
realisable by a pre-registered low-complexity relation; recognizer = exact set-membership
counting over packed difference tables; plant = engineered constant-shift, AP and
generator-window pairs injected through the identical pipeline, which must be recovered at
exactly the planted coordinates. (B) the numerology table: exact predicate matches only
(measured-only by construction). (C) the crib sweep: a hit = a crib-consistent (key, cfg, mode,
offset) cell whose full-page decode is non-degenerate and crosses the bars_v3 free bar under
panel-R36 (`round19/I2/adjudicate.py`, `data/panels/panel-r36.npz`); plant = a synthetic
two-page join enciphered with an in-family key at an out-of-base offset, pushed through the
IDENTICAL filter → decode → adjudicate path; it must be flagged at exactly the planted offset,
recovered exactly, and cross the bar, with non-planted offsets staying below.

**Q2 — What measured fact raises the prior?**
(a) R44-R1-SEVENGRAM: the object is unique in canon at expected rate 0.005 and in no prior row;
its same-plaintext reading is now EXCLUDED over the 51 streams (R1's anchored falsifier) — the
different-plaintext reading is the only live cipher reading of a ≪1-in-200 object. (b) The crib
is FREE and TRUE: p55's solve is machine-guarded (`tests/validate.py`, 73.jpg row), so plaintext
A=24 at global 12956 is a fact, not a guess — the first known-plaintext constraint ever available
inside the LP2 cipher region boundary (the row's own not_covered says "never exploited by any
row"). (c) The only cipher-solved LP2 page (p55) demonstrably uses a FRESH stream at its own page
start — measured support for boundary-keyed constructions generally (R33-I2 lineage).

**Q3 — Is the space bounded, and by what?**
Enumerable, all parts. Part 1: |V3|² directed word-pair differences → one 29³ table; 29² (a,b)
AP cells; generator axis = 51 keys × (261² free (o1,o2) window pairs + 201 global-diagonal +
201 section-diagonal) ≈ 3.5M difference vectors, all exact lookups. Part 2: ≤ ~40 site-derived
numbers × ≤ 11 constants × a fixed predicate list. Part 3: 51 keys × 6 cfgs × (171 section +
201 global offsets) = 113,832 crib checks → expected ~1/29 survive ≈ 3,926 cells × 55 pages ≈
216k panel decodes (+ plants + ≤ 20 tier-2 beam decodes). Bars fixed at N_bar = 400,000 ≥ any
actual N. Minutes of compute.

**Q4 — the three conditionals** — see `three_conditionals` (§8).

**Q5 — Kill condition at 10% budget:**
(i) Any plant (solver or crib-glue) fails its pass criterion → **INSTRUMENT-INCOMPLETE**, stop,
no verdicts. (ii) The premise re-verification (7-gram sites, p55 identity/crib facts, §1) fails
from canon → **UNAVAILABLE-BY-PREMISE**, stop. Checkpoint: after `plant_solver.py` +
`plant_crib.py`, before any real target.

## 3. Fixed vocabulary (part 1; built by rule, before any solve)

- **V3** (3-rune plaintext words, rune-index triples) = union of:
  (a) ALL rune-length-3 plaintext words of the 6 solved pages (Runes-01, 03, 05, 06, 14, 73
  via `corpus.page_by_label`; simple pages by their validate.py brute transform, 03/14/73 by
  their documented keys + `find_interrupters` null set; word boundaries = maximal rune runs);
  (b) the top 150 KJV (`data/kjv.txt`) tokens by frequency whose `keyword_to_indices` encoding
  has rune-length 3; (c) the top 100 such Latin tokens from `analysis/latin/latin_28233.txt`.
- **H** (head runes) = first-rune indices of all solved-page words (rune-length ≥ 2) ∪ top 500
  mappable KJV words ∪ top 300 mappable Latin words. |V3|, |H| reported in RESULTS.
- Site-B head is FIXED by the crib: P2[6] = 24 (A). Site-A head P1[6] ranges over H.

## 4. Part 1 — different-plaintext constraint enumeration (FIXED)

Model: sites share ciphertext C = (23,11,1,17,18,10,25); word-gap pattern 001001 at both sites →
P = (w1, w2, h), w ∈ V3, h = head. For every additive/Beaufort config (vig±, Beaufort, × atbash
pre-transform) the collision condition is k1 − k2 ≡ σ·(P1 − P2) mod 29 with σ ∈ {+1,−1} (derived
per config in `a2lib.py`; σ is absorbed by scanning both signs). Tests, all exact counts:
- **constant**: e = P1−P2 constant over i=0..6 (site-B head fixed → shift s = (24−P1[6]) forced);
  b=0 row of AP. Count pairs; s=0 ∧ P1=P2 (the same-plaintext case, already excluded by R1)
  subtracted and reported separately.
- **AP**: e_i = a + b·i mod 29, all 29² (a,b); count = c1(a,b)·c2(a,b)·[24+a+6b ∈ H]-style exact
  membership (head factor per the site-B fix; also reported with i=0..5 only, head-free, for
  page-mode where the key stream breaks at the boundary).
- **generator**: for each of the 51 R44-R1 keys (rebuilt via `resets.py::build_keys`,
  KEY_LEN=13400): D(o1,o2)_i = K[o1+i]−K[o2+i], (o1,o2) ∈ 0..260² (covers page-mode
  oA+28/oB+70, oA,oB ≤ 190), PLUS the two physically-anchored diagonals: section
  D(o)=K[o+28+i]−K[o+70+i] and global D(o)=K[o+6555+i]−K[o+12950+i], o ∈ 0..200. Vocab-pair
  count per D via the packed g3 table (both σ); i=0..6 for section/global-style (stream crosses
  the boundary; site-B head key is then bound by the crib), i=0..5 + head-free for page-style.
- **Null of record**: the identical pipeline on random vocabularies (same |V3|, uniform distinct
  triples; same |H|), seed 3301 — 200 trials for constant/AP, 20 for the generator axis. Observed
  counts are reported AGAINST this null; part 1 is measured-only unless a LOUD criterion (§7)
  fires.

## 5. Part 2 — positional numerology (FIXED predicate table; measured-only)

Site numbers S = {27, 54, 28, 55 (pages 0/1-based), 28, 70 (positions), 6555, 12950, 12956
(globals), 234, 76, 85 (page lengths), 42, 27, 6395, 6401 (deltas), 105 (index sum), 389
(gematria-prime sum), 6555+12950, 12950−2·6555}; constants C = {1, 2, 3, 29, 58, 311, 509, 761,
1033, 3299, 3301, 1595277641}. Predicates, exhaustive over S×C and S×S: equality; divisibility
(both directions); x±y ∈ C for x,y ∈ S; x·y ∈ C; x mod 29 / mod 3301 (values recorded);
primality of every member of S. Every match REPORTED verbatim; no verdict attaches (the table is
the record, as W2-A1 §5).

## 6. Part 3 — the crib sweep (FIXED)

- **Required key value at the boundary index** (ciphertext 25, plaintext 24): vigm k=1, vigp
  k=28, beau k=20, vigm_atb k=8, vigp_atb k=21, beau_atb k=27 (derivations in `a2lib.py`;
  vigm's k=1 = totient[0] is the known solve, the filter's built-in truth anchor).
- **Filter**: for each key K (51), cfg (6), mode ∈ {section: crib index o+76, o ∈ 30..200;
  global: crib index o+12956, o ∈ 0..200}: keep (K, cfg, mode, o) iff K[crib index] == required.
  Section o ≤ 29 flags reported WITHOUT decode (R1's cells, already negative). Line mode: the
  key stream cannot cross the p54→p55 boundary under it (p55 pos 0 starts a new line) — the crib
  does not bind; excluded by construction, stated in not_covered.
- **Decode**: every surviving cell decodes ALL 55 unsolved pages (tier-1 unfiltered decode,
  `resets.py::decode_block` / section phases from `resets.py::phase_vectors`; global phase =
  canon global position), `adjudicate_batch` panel-R36, full `adjudicate` + degenerate guard on
  any bar-crosser.
- **Propagation**: for every surviving cell, the full-p55 match depth T = #leading p55 positions
  j (capped 30, truncated before the known solve's null-F) with K[crib index + j] == required
  key R_j(cfg) derived from p55's known plaintext. Null: P(T ≥ d) = 29^−(d−1) per survivor.
- **Tier 2**: the top-10 surviving cells by tier-1 pmax re-decoded (their best page) under the
  R1 reset-aware keyskip1 beam (`resets.py::beam_reset_decode`, G3-gated in R1 at power 0.989),
  full adjudicate, same bar.
- **Thresholds (FIXED now, from the committed bars_v3 fit, N_bar = 400,000 ≥ any actual N;
  L_cap = largest of {120, 240} ≤ decode length, floor 120 — unsolved pages are L 66..277):**

| L_cap | bar (pmax), free, N = 400,000 |
|---|---|
| 120 | **14.8161** |
| 240 | **19.9112** |

A cell crosses iff its non-degenerate full-adjudicate pmax ≥ the bar at its page's L_cap.
0 crossers → NEGATIVE (measured, conditionals §8). Any crosser → **FLAGGED-FOR-ORACLE** per
`HUMAN-ORACLE.md`, never certified. Propagation flag threshold: T ≥ 5 (expected count over
~3,926 survivors ≈ 3926·29^−4 ≈ 0.0056).

## 7. LOUD criteria (fixed)

- **LOUD-1**: any constant-shift vocab pair with s ≠ 0 (listed verbatim, vs null rate).
- **LOUD-2**: any physically-anchored generator cell (section/global diagonal) with vocab-pair
  count > 0 whose (K, o) is ALSO crib-consistent — cross-referenced into part 3's decode set.
- **LOUD-3**: crib propagation depth T ≥ 5.
- **LOUD-4**: any panel bar-crosser → FLAGGED-FOR-ORACLE (HUMAN-ORACLE.md bundle), full stop.
None of LOUD-1..3 is a verdict; each is a measured anomaly reported loudly.

## 8. three_conditionals

- **key_space**: the 51 R44-R1 keys only (P-prime, P-totient, P-phi, bash-4.2-LP64 $RANDOM
  mod-29 anti-repeat for the 48 fixed seeds), offsets: section 30..200 / global 0..200
  (crib-filtered), generator-difference windows (o1,o2) ≤ 260 + the two diagonals ≤ 200; vocab
  V3/H exactly as §3. Nothing else.
- **transition_model**: position-indexed substitution mod 29 (vig±, Beaufort, × atbash-pre),
  key stream CONTINUOUS across the p54→p55 boundary (section-continuation or one global
  stream); tier-1 unfiltered application; keyskip1-filtered application only via the tier-2
  beam on the top-10 cells; the different-plaintext model assumes both sites carry the
  word-gap-aligned (3,3,1) word shapes; interrupters as ordinary ciphertext except p55's known
  null-F (propagation window truncates before it).
- **adjudicator_register**: panel-R36 (12 registers), pmax vs bars_v3 'free' at N_bar=400,000;
  the negative extends only to those registers. Parts 1–2 are counting instruments, not
  language adjudicators: their outputs are measured-only except per §7.

## 9. Positive controls (through THIS cell's own glue; run before any real target)

- **PLANT-S1 (constant)**: inject u1+σs, u2+σs companions for a chosen vocab pair into a COPY of
  V3; solver must count ≥ 1 at exactly s and list the planted pair.
- **PLANT-S2 (AP)**: same with e_i = a+b·i, (a,b)=(4,3); must appear at exactly (4,3).
- **PLANT-S3 (generator)**: K = G-bash-3301, (o1,o2) = (57, 141): inject P2 = P1 − D into the
  vocab copy; the generator scan must flag (57,141) with count ≥ 1.
- **PLANT-C1 (crib glue)**: synthetic join — 120 runes held-out English (self_reliance second
  half) as "pageX" + real p55 plaintext prefix as "pageY" — enciphered continuously with
  G-bash-1033 at offset o*=137, cfg=vigm, through `resets.py::encipher_reset`. The identical
  filter→decode→adjudicate path must flag o=137 among its survivors, decode pageX exactly
  (recovery 1.0), cross the 14.8161 bar, measure propagation T = cap, AND the grid best over
  all surviving offsets must be o*=137 with every other surviving offset's decode below bar
  (the differential licence).
Pass/fail is binary; any failure → INSTRUMENT-INCOMPLETE (Q5).

## 10. Outputs

`a2lib.py` (vocab, tables, keys, crib, decode glue) · `plant_solver.py` → `plant_solver.json` ·
`plant_crib.py` → `plant_crib.json` · `run_diffplain.py` → `diffplain.json` · `run_numerology.py`
→ `numerology.json` · `run_crib.py` → `crib_results.json` · `RESULTS.md` · `ledger_rows.json`
(drafts; LEDGER.json NOT modified) · `run.log` (hash-stamped). Pure python3+numpy, no network;
masters untouched (this is a canon/stream cell, no image work).
