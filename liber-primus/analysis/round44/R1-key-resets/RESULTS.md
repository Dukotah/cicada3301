# Round 44 / R1 — per-page / per-line / per-section key resets + the 7-gram anchor: RESULTS

_Run 2026-11-09. PREREG.md dated before any output; thresholds fixed in advance; gate before
sweep. Verdict: **NEGATIVE** (measured, panel-R36, conditionals below) — plus two standalone
measurements: the p27/p54 7-gram is now verified, located and recorded for the first time in the
project's record, and the same-plaintext 7-gram constraint is shown to EXCLUDE every key in the
swept set under page/section resets at every offset ≤ 200._

## 1. Step 1 — the 7-gram, verified (sevengram.json)

**CLAIM VERIFIED.** The 7-gram **ᛞᛄᚢᛒᛖᛁᚫ = D J U | B E I | AE** (indices 23 11 1 17 18 10 25)
occurs at **p27 pos 28** and **p54 pos 70** — exactly the positions X0 item 4 / R43-F3 §1 /
blind agent A5 reported. Measured facts the earlier reports did not pin down:

- It is the **only repeated 7-gram in the entire 57-page concatenated canon stream**
  (13,136 runes; expected matching pairs under uniform iid: **0.0050**).
- The word-gap patterns are **identical** (`001001`: two 3-rune words + the head of a third word)
  at both sites.
- **The p54 occurrence crosses the page boundary**: p54 is 76 runes long, so positions 70–75 are
  its last six runes and the 7th matching rune (ᚫ) is the FIRST rune of p55. A per-page scan
  finds ZERO repeated 7-grams — this lane's own first scan did, and was corrected
  (`verify_7gram.py` documents it). Every per-page analysis is structurally blind to this object.
- Both p27 and p54 **open red-head sections** (map [0,3,6,7,8,15,23,27,33,39,40,53,54]);
  the in-section offsets are 28 and 70 (p55 continues the p54 section, so the second site is
  contiguous 70..76 in section coordinates).

## 2. Gate — positive controls through this lane's own glue (gate.json): **GATE-PASSED**

| control | construction | reset-aware path | rigid path (the differential) |
|---|---|---|---|
| G1 | page resets, direct, (P-totient, o=7, vigp), 3×120 | planted cell = grid max on all 3 pages out of 27,540 cells each; **exact recovery**; pmax 26.35–26.97 vs bar 15.674 | post-reset pages: recovery **0.008 / 0.067**, pmax 1.86 / 1.13 (deep under bar) |
| G2 | line resets, direct, (G-bash-1325734783, o=3, beau), 240 | planted cell = grid max; **exact**; pmax 37.22 vs bar 21.101 | no-reset decode: recovery 0.133, pmax 4.92 |
| G3 | page resets, **keyskip1-filtered** (supp 0.83), (P-prime, o=0, vigm), 3×120 | reset-aware keyskip beam recovery **0.989** (≥ 0.85 bar) | rigid keyskip beam recovery **0.364** (< 0.85) |

**Measured tier-1 screen power against the FILTERED construction: ~zero.** The direct reset
decode of G3's own pages scores pmax 13.02 / 0.92 / 1.23 (recovery 0.675 / 0.000 / 0.092) vs bar
15.674 — even the first segment does not cross once the anti-repeat rejections desynchronise the
pointer. So tier-1's negative covers the UNFILTERED application; the keyskip1-filtered
application is covered only by tier-2 (beam) on the cells tier-2 visited. This is the honest
power statement, measured, not assumed.

## 3. Tier-1 sweep (r1_results.json)

- Matrix: 51 keys (3 solved-page prime/totient streams + 48 bash-4.2-LP64 `$RANDOM` mod-29 seeds:
  seedprior20 top-40 + 8 Cicada integers) × 30 offsets (0..29) × 6 configs × 3 reset modes
  (page / canon-line / red-section) × 55 pages = **1,514,700 cells**, all panel-R36 adjudicated.
- Bars (fixed in PREREG at N_bar = 2,000,000 ≥ actual 1,514,720): **15.674** (L_cap 120),
  **21.101** (L_cap 240).
- **0 crossers.** Global best **pmax 5.631** (page 47, G-bash-1358633868, line mode, o=26,
  beau_atb, L=274) vs bar 21.101 — **15.5z below the bar**, exactly where a null best-of-1.5M
  belongs. No near-miss anywhere.

### The anchor became a falsifier

The 7-gram-anchored offset extension is EMPTY: **no key in the swept set satisfies the
same-plaintext constraint** (K[o+28+j]=K[o+70+j], j=0..6 section-mode; j=0..5 + the p55-crossing
condition K[o+34]=K[o+0] page-mode) at ANY offset o ∈ 0..200, page or section mode (anchor
function validated by a synthetic-key self-test in `run_sweep.py`, and the n-gram scanner by
re-finding the two independently blind-reported 5-gram repeats BMRNM p22:73/p48:224 and OUNWM
p28:224/p33:56). Read as a bound: **under the same-plaintext reading of the 7-gram, NO
per-page/per-section reset of any of these 51 streams can produce LP2** — the sweep's negative
and the anchor agree. The different-plaintext reading (two plaintext words colliding to one
ciphertext 7-gram with identical boundaries) is unconstrained by this and remains open.

## 4. Tier-2 (reset-aware keyskip1 beam; the R33-I2 patch, first time applied to real data)

Top-20 tier-1 cells + all crossers (none) = 20 beam decodes (beam_w 200, max_rej 3, config
algebra in `resets.py::_transform`): best beam pmax **5.423**, 0 crossers, 0 non-degenerate
survivors. Covers the keyskip1-filtered application only for these cells (power 0.989 per G3).

## 5. Verdict and numbers vs bar

**NEGATIVE.** 1,514,700 tier-1 + 20 tier-2 cells, 0 crossers; best 5.631 vs bar 21.101.
Nothing flagged for oracle (no bar-crosser existed). R33-I2's "unrepresented constructions" hole
is now closed FOR THIS KEY SPACE: the reset constructions have a validated decoder and a
measured negative, instead of no coverage at all.

## 6. Three conditionals

- **key_space:** the 51 fixed keys only — P-prime (pᵢ mod 29), P-totient ((pᵢ−1) mod 29), P-phi
  (φ(n) mod 29, n≥2), and bash-4.2-LP64 `$RANDOM` (anti-repeat wrapper, mod-29 reduction) for the
  48 fixed seeds; offsets 0..29 (anchored extension empty, measured).
- **transition_model:** key-pointer reset at canon page / canon-'/'-line / red-head-section
  boundaries at fixed offset; tier-1 = unfiltered position-indexed substitution (vig±, Beaufort,
  × atbash-pre); keyskip1 anti-repeat application covered only at tier-2 on the top-20 cells
  (G3-measured power 0.989 there, ~0 at tier-1); keyskip2/drift with resets not represented.
  Interrupters treated as ordinary ciphertext.
- **adjudicator_register:** panel-R36 (12 registers), pmax vs `bars_v3 'free'` at
  N_bar = 2,000,000; tier-2 beam search internally English-quadgram-guided (the R33-I2 patch
  limitation), final scoring panel-R36.

## 7. Coverage × power

Coverage: the full Q3 grid (1,514,700 cells, enumerable, 100% of the pre-registered space — no
truncation was needed; 17.6 s wall) at power 1.0 for unfiltered reset constructions (G1/G2 exact
recovery through the identical glue) and ~0 for keyskip1-filtered ones at tier-1, plus tier-2 at
power 0.989 on 20 cells. The 7-gram scan: 100% of the concatenated canon stream, all n≥7.

## not_covered

- Generators/seeds/reductions outside the 51 keys (other bash variants/ABIs, Perl 5.14, Py2.7 MT,
  TeX LCGs, the 2³¹ seed tails; rejection-sampled or scaled reductions; reversed streams).
- Offsets 30..200 exist in the space only via the anchor (empty here); unanchored offsets > 29
  and all offsets > 200 uncovered.
- keyskip1-filtered resets beyond the 20 tier-2 cells; keyskip2 / free-drift / skip_by_k≥3
  combined with resets; mixed reset modes; resets at boundaries other than canon page / canon
  line / red-head section (e.g. sentence, paragraph `&`).
- Per-line results are conditional on the canon '/' line map (R33-I2's physical-line-map
  unreliability caveat carries).
- Interrupter-as-null handling; the different-plaintext reading of the 7-gram; the known
  plaintext of p55 rune 0 (first solved page) as a 1-rune crib on the second 7-gram site —
  noted, never exploited by any row.

## reopens_if

A generator/key family outside the 51 gains an evidence prior (source find, artifact) — rerun is
~20 s per 51-key batch through this lane's committed glue; a pre-registered different-plaintext
model of the 7-gram is specified; the keyskip-filtered construction gets a cheap full-grid
decoder (then tier-1's unfiltered-only limitation falls); the canon line map is superseded by a
measured physical-line map.

## Files

`PREREG.md` · `verify_7gram.py` → `sevengram.json` · `resets.py` (keys, phase maps, tier-1
vectorised decode, tier-2 reset-aware keyskip1 beam, encipher) · `plant_gate.py` → `gate.json` ·
`run_sweep.py` → `r1_results.json` · `ledger_rows.json` (drafts; LEDGER.json not modified).
Reproduce: `python3 verify_7gram.py && python3 plant_gate.py && python3 run_sweep.py` (lane dir).
