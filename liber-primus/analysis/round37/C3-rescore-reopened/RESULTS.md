# Round 37 / C3 - re-score of the reopened families under panel-R36 (12 registers) + beam_v3: RESULTS
Dated 2026-10-30. PREREG.md was written first. No discovery claim: 0 flagged, 0 near-miss (clearing the actual-N bar). Nothing here is "solved/closed/exhausted" - every row is negative **conditional on** (key space regenerated here) x (keyskip1/2, or skip-free for direct rows) x (panel-R36, 12 registers).

## Method deviations from PREREG (each forced by a measured fact; none chosen after seeing a hit)
1. **Degenerate-decode filter.** X4 `prime_index/atbash_pre/sign+1` decodes to a constant stream (IoC*N=29, mds=1), which OE's trigram LM scores 12.4 (above both L=240 declared bars). R22-C's recovery gate used to catch this; with no truth text here, rows with `mds <= 6` or `IoC*N >= 4.24` (thresholds from real-language 240-slices over all 12 registers: mds min 7, IoC*N max 3.24) are excluded from "best" and counted (12 rows/rel in U6b, 0 elsewhere). All best values below are non-degenerate.
2. **Null for derived streams.** The first pass used the lane's plain histogram shuffle; LP2 has only 86 adjacent equal pairs (iid ~447), so a plain shuffle drops a real property. N1-PT, N2, N4-read and the X1/X3a structural ops were re-run with a doublet-level-matched (dfshuffle, <=86 pairs) shuffled LP2 source re-derived through each family's own transform; first-pass results are kept in `superseded_plain_shuffle_null/`. M1 pooled carries both nulls.
3. **Two direct statistics.** Per-stream standardised Z (p of the family max against >=200 same-draw nulls) and the raw best-of-family pmax. A direct row counts only if both p < 0.01. One family has p(Z) < 0.01 alone (N1-PT, Z=78, p=0.0066) and fails the raw test (p=0.50; pmax 2.7 is the random level for 12 correlated registers): a null-variance artefact, not a hit. S1/S2 ran before the raw statistic was made default (their p(Z) is 0.44-0.48; raw not recomputed).
4. n>1000 z in the rows is rescaled by sqrt(n/1000) (panel `cal` clamps at the grid end n=1000); verdicts use the self-calibrating shuffle null and do not depend on it.
5. R22-C "185 ops x keyskip1/2": the 169 structural ops have no key, so keyskip is inapplicable and they are scored directly. Keyed ops are 14 configs (X3b 2 signs + X4 12; R22-C's exact/drift axis is replaced by keyskip1/2).
6. No top-N sets were stored for any lens, so **all candidate sets were regenerated** from committed lane code (`n1.py`, `n4.py`, `n5.py`, `s1.py`/`s2.py` logic, `mapcommon.py`, `road.py::readings` exec'd unchanged, R22-C ops copied unchanged). M1 per-page: 21,808 of 25,520 streams (pages with < 40 words skipped).

## Controls (control.json; all passed before counting)
- Beam families (N1-CT, N4-ks, N5, X3b, X4): plants from `testhalves12.npz` (EN_MODERN, LATIN, GREEK; real `enc_exact`/`enc_pair`) encrypted with each family's own keystream and decoded with the true key by beam_v3 panel_max: **30/30** recovered (pmax120 >= 12-reg declared-N L=120 bar AND pmax240 >= L=240 bar AND recovery240 >= 0.90); 6/6 per family per relation (gate >= 4/6). N5 real artifact: AN END with phi(prime) recovers 1.00 (keyskip1) / 0.93 (keyskip2), own register LP1_REAL; pmax 8.93/9.00 at n=85 vs L=120 bars 9.10/9.00 (length-mismatched, reported, not gated).
- Direct families (14 runs): a held-out text of the family's stream length through the identical pipeline beats the family-null max-Z q99 by > 1 in all 3 registers for every family; X1/X3a also through the real inverse ops (decimation embed, interleave, reversal+shift): 9/9.
- Round 11's own planted controls (English scorer) are restated, not re-run. Only EN_MODERN/LATIN/GREEK were planted (not HEBREW/NORSE) for these key families.

## Per-family table
Bars = 12-register POT bar (`round36/B1-orbit-12reg/null12.json`): actual-N (declared N=1e6). Beam "best" = best non-degenerate pmax over the family.

| family (ledger row) | artifact | control | N | best | bars ks1 / ks2 | verdict |
|---|---|---|---|---|---|---|
| U5-L2 M1 pooled (R10-L2-MAP, the **z=6.94 stream**) | 464 regenerated readings | pass | 464 streams; 2000 null_A + 2000 dfnull draws | z694 reading (first/noF atbash/rev/+28): pmax **3.94** (EN_MODERN), Z 1.63 in-family; family best Z 2.50 (p 0.947; dfnull Z 2.57, p 0.922); raw best-of-464 4.45, p 0.739, Wilson95 exceedance [0.72, 0.76] | direct | negative |
| U5-L2 M1 per-page | 21,808 short streams | pass | 200 draws | Z 5.07 (p34 last/noF id/fwd/+8, pmax 4.62), p(Z) 0.095, raw p 0.647 | direct | negative |
| U5-L2 M2 / M9 / M5 | 348 / 290 / 1,486 streams | pass | 300 / 300 / 100 draws | p(Z) 0.233 / 0.392 / 0.327; raw p 0.74 / 0.16 / 0.64 | direct | negative |
| U5-L3 T2-T4 / T5 (R10-L3-ROAD) | 208 / 15 streams | pass | 300 / 60 | p(Z) 0.960 / 0.377; raw p 0.88 / 0.56 | direct | negative |
| U6a-N1 CT-feedback (R11-N1) | 24 configs x 10 windows | pass | 240 rows/rel | 4.76 (EN_MODERN) / 4.61 (NORSE) | 6.07 (9.10) / 6.02 (9.00) | negative |
| U6a-N1 PT-feedback | 24 decodes, skip-free | pass | 24 | p(Z) 0.0066 but raw p 0.50, pmax 2.7 | direct | negative (skip-free only) |
| U6a-N2 | 12 streams | pass | 200 draws | p(Z) 0.41, raw p 0.67 | direct | negative |
| U6a-N3 | none | n/a | - | no adjudicator ever involved | - | not re-scored (inconclusive) |
| U6a-N4 keystream / read | 28 keystreams x 6 windows / 14 planes | pass | 168 rows/rel / 300 draws | 5.56 (EN_HALFVOWEL) / p(Z) 0.505, raw p 0.43 | 5.94 (9.10) / 5.89 (9.00) | negative |
| U6a-N5 (R11-N5) | 464 keystreams x 5 windows | pass (+AN END) | 2,320 rows/rel | **6.30** (CY) | 6.90 (9.10) / 6.83 (9.00) | negative; closest beam row, 0.59 below actual-N bar |
| U6a-S1 / S2 | 8 / 1 streams | pass | 300 / 1000 draws | p(Z) 0.48 / 0.44 | direct | negative |
| U6b R22-C structural (X1+X3a) | 169 streams | pass | 300 draws | p(Z) 0.75, raw p 0.60 (best X1a_decim_phase2_shift8, pmax 3.18) | direct | negative |
| U6b R22-C keyed L=120 | 14 configs x 6 windows | pass | 84 rows/rel (12 degenerate) | 4.78 (GREEK) | 5.69 (9.10) / 5.65 (9.00) | negative |
| U6b R22-C keyed L=240 | same | pass | 84 rows/rel | 5.46 (EN_KJV) | 6.04 (8.98) / 6.15 (9.28) | negative |

Family-matched wrong-key nulls (shuffled windows, same keys; 100 draws per relation, 60 at L=240) peak at 4.2-4.6, so the transferred bars are not undercut. For data-dependent X4 keys the match is only approximate (reported, not relied on).

## Flagged / near-miss
- Flagged-for-oracle: **none**. Near-miss (clears actual-N, not declared-N): **none**. U6b keyed was already run at L=240 for every row (best 5.46 < 6.04); nothing else proceeded to L=240.
- Closest: N5 6.30 vs 6.90 (`phi_phi_prime_RI_s-1_o20_seg36`, window 0, CY); N4 5.56 vs 5.94 (`b5_p1_ks-1`, window 10000, EN_HALFVOWEL). Neither clears; listed for the red team.
- The Round 10 z=6.94 near-flag is resolved as a retired-scorer artefact: under the 12-register panel the same reading is pmax 3.94 (EN_MODERN) and sits at Z 1.6 of its own 464-reading family.

## Conditionals now carried (Aiming Test Q4)
(1) key space = only what was regenerated (N1 24 CT + 24 PT, N4 28 keystreams + 14 planes, N5 464 keystreams, X3b 2 + X4 12, plus the listed streams); a keystream is covered only at the windows listed (N1 10, N4 6, N5 5, U6b 6 page starts); (2) transition model = keyskip1+keyskip2 for beam families, skip-free for N1-PT and all direct streams; (3) adjudicator = panel-R36, 12 registers.

## not_covered
M3/M4/M6/M7/M8 of R10-L2 (bits, LP1 pointers, counts, analytic, run pattern); R10-L3 T1 count tests; N2/S1/S2 ASCII/bit/coordinate routes (byte reads, not rune space); N1-PT under skip relations; N4/N5 windows beyond those listed and offsets beyond additive; R22-C non-zero offsets, width != 4, drift constructions beyond keyskip; pf_v4 not used (no head screen exists in these families); HEBREW/NORSE not planted in the beam controls.

## Could not be re-run
None outright. N3 has nothing to re-score. N1-PT can be re-scored only skip-free (its key depends on recovered plaintext).

## Coordinator decisions
1. Apply `ledger.json` / `ledger_patches.json`? The R10-L2-MAP and R10-L3-ROAD patches presume C1's proposed rows are accepted.
2. Accept the IoC/mds degenerate filter as a standing part of keyed-lens adjudication (R22-C's recovery gate needs truth).
3. Bars for data-dependent keys (X4) are transferred from random-key nulls; a bespoke null (dfshuffled C with K re-derived) was not built.

## Files
PREREG.md, rescore.py, build_deliverables.py, control.json (+ control_beam.json), rescore_rows.jsonl (10,545 SWEEPROW rows, 12-wide; stock `validate_store` ok, `check_r3_store` []), rescore_summary.json, ledger.json, ledger_patches.json, parts/ (per-family rows + meta), superseded_plain_shuffle_null/, logs.
