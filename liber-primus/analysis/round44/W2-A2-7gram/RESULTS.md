# Round 44 / WAVE-2 CELL A2 — the 7-gram's different-plaintext reading + the p55-rune-0 crib: RESULTS

_Run 2026-11-09. PREREG.md hash-stamped into run.log before first execution
(sha256 ee903573…7d19a). Plants passed before any real target. Verdicts below; nothing
flagged for oracle (no bar-crosser existed)._

## 0. Verdict line

- **Part 1 (different-plaintext constraint enumeration): MEASURED — everything at or below
  the vocab-null rate.** The different-plaintext reading of the 7-gram requires NO
  low-complexity key relation that the actual plaintext vocabulary prefers over chance.
- **Part 2 (positional numerology): MEASURED — no non-trivial tie** to 3301/1033/761/509/3299;
  the one curiosity (gematria-prime sum of the 7-gram = 389, prime) is recorded.
- **Part 3 (the p55-rune-0 crib sweep): NEGATIVE** (measured, panel-R36, conditionals §5):
  3,905 crib-consistent cells × 55 pages = 214,775 tier-1 decodes (3,905×55) + 550 tier-2 page-rescans + 10 beam decodes = 215,335 total adjudicated + 10 tier-2 beam decodes,
  **0 crossers**; best pmax 4.922 vs bar 19.911. Crib propagation depth is a textbook
  geometric null (max 3; flag threshold 5 never reached).

## 1. Gate (plants through this cell's own glue) — **GATE-PASSED**

| plant | construction | result |
|---|---|---|
| S1 constant | engineered s=11 companions injected into a V3 copy | count 16 ≥ 1 at s=11, planted pair listed verbatim |
| S2 AP | (a,b)=(4,3) companions | count 12 ≥ 1 at exactly (4,3) |
| S3 generator | K=G-bash-3301, (o1,o2)=(57,141), σ=+1 | cell count 4 ≥ 1 at (57,141) |
| C1 crib glue | 120 held-out EN + real p55-plaintext prefix enciphered continuously, G-bash-1033, o\*=137, vigm | o\*=137 flagged (9 surviving offsets), grid best = o\*, recovery 1.000, pmax **18.59 ≥ bar 14.8161**, all other offsets below bar, propagation T = 30/30 |

Plant fix (logged in run.log before re-run): PLANT-S1 exposed a listing bug — the constant-pair
list had a global 50-item cap that filled before row s=11; changed to a per-row cap. Counting
(the instrument) was never wrong; thresholds and criteria unchanged.

Premise re-verification (Q5 ii) passed: sites global 6555/12950, p54 len 76, p55 first rune
ᚫ=25, known solve reproduces AN END WITHIN THE… (1 interrupter, null-F at ciphertext pos 30 →
propagation window T_max = 30).

## 2. Part 1 — different-plaintext enumeration (diffplain.json)

Model: identical ciphertext C at both sites ⇒ k1−k2 ≡ σ(P1−P2) mod 29 for every
additive/Beaufort config (σ derived per config; both signs scanned). Vocabulary by the
pre-registered rule: **|V3| = 244** 3-rune plaintext words (solved pages + top KJV English +
top Latin), **|H| = 25** head runes; site-B head FIXED at A=24 by the crib.

| key relation | observed | vocab-null (seed 3301) | reading |
|---|---|---|---|
| constant shift (LOUD-1) | 19 shifts satisfiable, **202 pairs** (all listed in diffplain.json; e.g. HEAP·HEAP·EA ↔ RAN·RAN·A at s=4) | 195.7 ± 64.1 (200 trials) | **z ≈ +0.1 — exactly chance** |
| arithmetic progression (b≠0) | 530/812 cells satisfiable | 584.1 ± 20.0 | **below null** |
| same-generator window pairs (51 keys, (o1,o2) ≤ 260²) | mean satisfiable fraction 0.685 | 0.813 ± 0.022 (20 trials) | **below null** |
| section diagonal K[o+28+i]−K[o+70+i] | 7,121 satisfiable cells (51 keys × 201 o) | 8,367.9 ± 236.6 | below null |
| global diagonal K[o+6555+i]−K[o+12950+i] | 7,195 | 8,368.2 ± 246.5 | below null |

The real vocabulary is LESS compatible with the different-plaintext collision than random
triples (real words cluster, so their difference sets are thinner). **No key-relation class is
preferred.** LOUD-1 pairs exist but at exactly the chance rate — each is a triple-word Caesar
coincidence inside the vocab, not evidence. LOUD-2 (loud2.json): 14,316 of 20,502 diagonal
cells are vocab-satisfiable (chance-level), 2,760 of them crib-consistent — **every one was
decoded in part 3 and none crossed.**

## 3. Part 2 — positional numerology (numerology.json)

Fixed predicate table over 20 site-derived numbers × 12 book constants. Matches found:
divisibility by 2/3 (trivial), |28−27|=1-type adjacencies, |76−105|=29, |85−27|=58 — nothing
involving 311/509/761/1033/3299/3301/1595277641 beyond those. mod-29 and mod-3301 residues
recorded verbatim. Prime members of S: only **gpsum = 389** (the 7-gram's gematria-prime sum
89+37+3+61+67+31+101). Measured-only; no verdict attaches.

## 4. Part 3 — the crib sweep (crib_results.json)

The 7-gram's 7th rune at the second site IS p55 pos 0 (solved): ciphertext ᚫ=25, plaintext
A=24, consumed key totient[0]=1 under the documented vigm solve. Any key stream flowing across
the p54→p55 boundary must therefore hit a fixed key value at that index — per config:
vigm 1, vigp 28, beau 20, vigm_atb 8, vigp_atb 21, beau_atb 27.

- **Filter:** 113,832 crib checks (51 keys × 6 cfgs × (section o 30..200 + global o 0..200)) →
  **3,905 consistent cells** (≈ 1/29, as chance predicts). 308 additional section flags at
  o ≤ 29 are reported WITHOUT decode (they are R44-R1-RESET-SWEEP cells, already negative).
- **Sweep:** every cell decoded on ALL 55 unsolved pages (215,325 decodes, 4.8 s), panel-R36,
  bars fixed in PREREG at N_bar = 400,000 ≥ actual: **14.8161** (L_cap 120) / **19.9112**
  (L_cap 240). **0 crossers.** Best cell pmax **4.922** (page 18, G-bash-1325735163, section,
  o=33, vigm, L=260) vs bar 19.9112 — deep in the null.
- **Propagation (the full-p55 crib):** depth over the 3,905 cells: 3,776 at T=1, 125 at T=2,
  4 at T=3, none ≥ 4 (geometric 1/29 expects ≈130 / 4.5 / 0.16 — observed matches the null
  almost exactly). Flag threshold T ≥ 5: never reached. **No standing key continues through
  the p54/p55 boundary in agreement with the known solve beyond chance** — including every
  section-continuation of the 51 streams: the red-section containing p54+p55 cannot be
  enciphered by any single one of them in any of the 6 configs at any offset ≤ 200.
- **Tier 2:** top-10 cells re-decoded on their best page under the R1 reset-aware keyskip1
  beam (G3-validated at power 0.989): best beam pmax 4.785, 0 crossers, 0 degenerate.

## 5. Three conditionals

- **key_space:** the 51 R44-R1 keys only (P-prime, P-totient, P-phi; bash-4.2-LP64 $RANDOM
  mod-29 anti-repeat, seedprior20 top-40 + 8 Cicada integers); crib offsets section 30..200 /
  global 0..200; generator-difference windows (o1,o2) ∈ 0..260² + diagonals ≤ 200; vocabulary
  V3 (244 triples) + H (25 heads) built by the PREREG rule.
- **transition_model:** position-indexed substitution mod 29 (vig±, Beaufort, × atbash-pre)
  with the key stream CONTINUOUS across p54→p55 (section or global phase); tier-1 unfiltered;
  keyskip1-filtered application only via tier-2 beam on the top-10 cells; the
  different-plaintext model assumes both sites carry (3,3,1)-shaped word tuples from V3×V3×H;
  interrupters as ordinary ciphertext except p55's known null-F (window truncated at 30).
- **adjudicator_register:** panel-R36 (12 registers), pmax vs bars_v3 'free' at
  N_bar = 400,000. Parts 1–2 are exact counting instruments (no language adjudication; their
  nulls are the random-vocab trials, seed 3301).

## 6. Coverage × power

Part 3 coverage: 100% of the pre-registered crib grid (113,832 checks, 3,905/3,905 surviving
cells decoded on all 55 pages — no truncation) at power 1.0 for unfiltered continuous-stream
constructions (PLANT-C1: exact recovery + bar crossing through the identical glue) and at
tier-2 beam power 0.989 (R1's G3 measurement, same code) on the top-10 cells. Part 1 coverage:
100% of the pre-registered relation classes over the full vocab (exact counts, not samples).
Part 2: the fixed predicate table, exhaustively.

## not_covered

- Plaintext shapes other than (3-rune word, 3-rune word, word-head) at the two sites (e.g.
  mid-word spans that happen to share the gap pattern; words outside V3 — V3 is 244 of ~29³
  possible triples; proper names; non-EN/Latin registers in the PAIR model — the DECODES are
  panel-R36 12-register, but the vocab is EN/Latin/solved-page only).
- Key relations beyond constant / AP / same-generator-window for the 51 keys: polynomial ≥ 2,
  keyed permutations of one stream, two UNRELATED streams (that reading is unconstrainable by
  construction — stated, not covered).
- Crib offsets > 200; keys outside the 51; line-mode (the stream cannot cross the p54→p55
  boundary under the canon line map — excluded by construction); keyskip1-filtered cells
  beyond the tier-2 top-10; keyskip2/drift with continuous phase; p55-propagation window
  beyond 30 positions and beyond the first null-F; interrupter conventions other than the
  known solve's.
- The 308 section o ≤ 29 crib flags are R44-R1 ground (negative there); not re-decoded here.
- Numerology predicates outside the fixed table (no open-ended search was run — by design).

## reopens_if

A key family outside the 51 gains an evidence prior (the crib filter + decode glue re-runs in
~5 s per 51-key batch); a vocabulary for another register is specified (re-run part 1 by rule);
a transcription revision moves either site or changes p54's length; an adjacent lane produces
a crosser whose key is crib-consistent (the propagation table in crib_results.json then ranks
it instantly).

## Files

`PREREG.md` (hash-stamped) · `a2lib.py` · `plant_solver.py` → `plant_solver.json` ·
`plant_crib.py` → `plant_crib.json` · `run_diffplain.py` → `diffplain.json` ·
`run_numerology.py` → `numerology.json` · `run_crib.py` → `crib_results.json` · `loud2.json` ·
`run.log` · `ledger_rows.json` (drafts; LEDGER.json not modified).
Reproduce: `python3 plant_solver.py && python3 plant_crib.py && python3 run_diffplain.py &&
python3 run_numerology.py && python3 run_crib.py` (cell dir).
