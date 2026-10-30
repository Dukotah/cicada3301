# Round 37 / I1 -- L-matched `free` null and `free` planted control: RESULTS
_2026-10-30. PREREG.md written first (plus two dated addenda: allocation after the 50-draw timing; a path-bug note). Instrument: `beam_v3.beam_decode_v3(.., "free", "panel_max", beam_w=400, lam_u=4)` as it stood at my start, **panel-R36 (12 registers) for both the beam objective and the pmax statistic**, so every number here is a 12-register number; the Round 34 `free` L=120 node and the O3 "15.15 / 14.33" were 9-register beams and are not directly comparable. Compute: about 89 min single-process (cap 90): timing 205 s, controls 280 s, nulls 262 + 1251 + 1352 + 2002 s. Files: `run_null_free.py`, `finalize_free.py`, `o3_rejudge.py`, raw `null_free_stream.jsonl`, `control_free_stream.jsonl`, derived `null_free.json`, `fit_free.json`, `control_free.json`, `o3_cell_rejudged.json`, `ledger.json`._

## 0. Headline
* **Draw shortfall (stated, not hidden).** Cost was 2.7 / 1.0 / 0.5 / 0.26 draws/s at L=120/240/400/729 (1.6 / 0.77 / 0.46 draws/s at L=240/400/729 in the clean 50-draw timing; the laptop was shared with Lane T1). The 90-min cap allowed 701 / 1335 / 726 / 562 draws, **not 2,000**, at L=120/240/400/729. L=400 and L=729 are fitted from what ran (tail k = 10% of n = 73 and 56 exceedances), not from the trend; beta SEs are 0.08-0.10 (about 12-13% of beta), so the N=1e6 bars carry roughly +-1.0 of statistical uncertainty. The empirical null max is far below every N>=1e5 bar, so bars of record sit in the extrapolated tail, as in Round 34.
* **Control: `free` FAILS for OE and EN_HALFVOWEL at L=240** (3/20 and 7/20 clear the N=1e6 Gumbel bar 20.59), and CY is marginal (19/20, one miss at 19.8). All nine other registers pass 20/20 at L=240, and every register passes at L=400 (5/5) and L=729 (3/3) -- but those are n<20 and are indicative only.
* **Verdict.** `free` carries claims at **L=240 for registers EN_MODERN, EN_KJV, LP1_REAL, LATIN, DE, CY (19/20, meets the >=19/20 rule exactly), EN_NOVOWEL, GREEK, HEBREW, NORSE** (not OE, not EN_HALFVOWEL). At **L=400 and L=729 no register is *passed*** under the pre-registered rule (needs >=19/20; only 5/5 and 3/3 plants were run). The 5/5 and 3/3 indicate `free` is probably usable there (plant medians 25-51 at L=400 vs bar 21.7; 33-70 at L=729 vs bar 24.9; weakest plants OE/HALFVOWEL clear by 1-4), but no claim is licensed until 20 plants per register are run. Round 34 found `free` fails OE/CY/HALFVOWEL at L=120; here the same two weakest registers (OE, HALFVOWEL) still fail at L=240.
* **Tail-model sensitivity.** Under the lighter-tailed GPD sensitivity bar (xi<0; not the bar of record) the N=1e6 bars are 16.2 / 19.3 / 18.5 at L=240/400/729 and every plant of every register at every L clears it, including OE and HALFVOWEL at L=240. So "OE/HALFVOWEL fail" is a statement about the conservative Gumbel bar. Do not use the GPD bar for claims.
* **O3 ILP32 `free` L=729 cell: NOISE.** Re-decoded under panel-R36: 15.157 (LP1_REAL). The 562-draw null has max 15.54 (2 of 562 draws >= 15.157 = 0.36%, empirical quantile 0.9964, Gumbel single-decode p = 0.0067). It is below the N=1e3 bar (19.86); family-wise over the ~460 free cells of the O3 grid the p is ~0.95. It is what the max of a few hundred `free` decodes at L=729 looks like.

## 1. Null table (shuffled-LP2 wrong keys, `free`, panel-R36)
| L | draws | median | p99 | max | u (q90) | beta (+-SE) | mu | xi (GPD) | bar N=1e3 | bar N=1e5 | bar N=1e6 | GPD bar 1e6 (sens.) |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 120 | 701 | 5.30 | 7.90 | 8.57 | 6.72 | 0.533 (0.064) | 5.49 | -0.14 | 11.62 | 14.08 | 15.30 | 10.56 |
| 240 | 1335 | 7.13 | 10.36 | 11.69 | 8.67 | 0.739 (0.064) | 6.97 | -0.07 | 15.48 | 18.89 | 20.59 | 16.15 |
| 400 | 726 | 8.71 | 12.03 | 13.88 | 10.66 | 0.683 (0.080) | 9.09 | -0.04 | 16.95 | 20.10 | 21.67 | 19.29 |
| 729 | 562 | 11.32 | 14.75 | 15.54 | 13.19 | 0.724 (0.096) | 11.53 | -0.14 | 19.86 | 23.20 | 24.86 | 18.51 |

Fit: R34 `fit.py` machinery (exponential POT above the empirical 90th percentile; mu = u + beta ln p_u; bar = mu + beta ln(N / -ln 0.99), alpha 0.01). Medians 5.30 / 7.13 / 11.32 reproduce O3's `free` medians (5.2 / 7.5 / 11.2). **Trend:** mu rises with L, mu = -11.08 + 3.39 ln L (L=120..729); the Gumbel scale does NOT shrink with L as keyskip's does: beta(L) exponent **+0.15 +- 0.09** (4 points; keyskip1/2 were -0.10 to -0.14), i.e. beta is flat at 0.53-0.74. Consequence: `free` bars grow with L (N=1e6: 15.3 -> 24.9), the opposite of keyskip.

**L=120 vs Round 34.** R34 (9-register beam, 1000 draws, 6L+64 key): median 5.26, max 9.91, beta 0.669 (0.067), mu 5.115, N=1e5 bar 15.89 (`bar_v3(1e5,120,"free")`). Here (12-register beam and pmax, 701 draws, 41L+64 key): median 5.30, max 8.57, beta 0.533 (0.064), mu 5.49, N=1e5 bar 14.08. Median agrees; beta differs by 0.136 = 1.5 combined SE (consistent); the bar differs by 1.8 at N=1e5. Panel, key length and draws all differ, so this is a consistency check, not a replication. `bar_v3(.., 120, "free", panel="r36")` returns my node.

## 2. Control (planted correct keys, `free_q05` enciphering, SHA-CTR key, held-out register windows; pass = pmax12 >= bar(N=1e6, L, free))
Bars: 20.59 (L=240), 21.67 (L=400), 24.86 (L=729). Cells: **L=240: 20 plants/register, all 12 registers (240 plants)**; **L=400: 5/register (60)**; **L=729: 3/register (36)** -- cap bound.

| register | L=240 pass (median / min pmax) | L=400 pass (median / min) | L=729 pass (median / min) |
|---|---|---|---|
| EN_MODERN | 20/20 (27.7 / 25.2) | 5/5 (36.1 / 34.9) | 3/3 (47.2 / 46.4) |
| EN_KJV | 20/20 (29.4 / 26.9) | 5/5 (38.4 / 37.4) | 3/3 (53.6 / 45.2) |
| LP1_REAL | 20/20 (40.3 / 38.2) | 5/5 (51.0 / 49.6) | 3/3 (70.2 / 69.2) |
| LATIN | 20/20 (25.1 / 21.5) | 5/5 (31.8 / 29.5) | 3/3 (42.8 / 40.9) |
| OE | **3/20 (19.1 / 17.4)** | 5/5 (26.0 / 24.7) | 3/3 (35.1 / 28.2) |
| DE | 20/20 (28.8 / 27.6) | 5/5 (37.8 / 36.3) | 3/3 (51.1 / 50.5) |
| CY | 19/20 (22.4 / 19.8) | 5/5 (27.7 / 26.5) | 3/3 (38.7 / 36.3) |
| EN_HALFVOWEL | **7/20 (20.3 / 17.6)** | 5/5 (25.0 / 22.5) | 3/3 (33.3 / 31.9) |
| EN_NOVOWEL | 20/20 (23.7 / 21.8) | 5/5 (30.9 / 29.5) | 3/3 (41.2 / 40.6) |
| GREEK | 20/20 (28.4 / 26.8) | 5/5 (36.6 / 34.6) | 3/3 (49.2 / 48.4) |
| HEBREW | 20/20 (26.6 / 24.5) | 5/5 (35.1 / 32.4) | 3/3 (46.1 / 45.8) |
| NORSE | 20/20 (25.6 / 20.7) | 5/5 (33.2 / 32.9) | 3/3 (45.1 / 44.7) |

Median recovery is 0.95-1.00 in every cell, so the failures are score failures against a high bar, not decoder failures: OE/HALFVOWEL plants are decoded 96%/95% correctly yet score only 19-20 because those registers' trigram models separate a correct plaintext from the wrong-key maximum less than the others (LP1_REAL scores 40). The `free` null's Gumbel scale (0.5-0.7) is about double keyskip's (0.3-0.4), which makes the N=1e6 bar high.
Plan Q5: L=240 fails for 2 registers (OE, EN_HALFVOWEL) -> **no usable `free` bar at L=240 for OE/EN_HALFVOWEL; B/C lanes claim no `free` reach there.** CY at L=240 meets the rule only just (19/20). At L=400/729 the control is under-powered (n<20) and passes nothing formally.

## 3. O3 ILP32 `free` cell at L=729 re-judged (`o3_cell_rejudged.json`)
Cell: bash 4.2 ILP32, seed 1354603465, `free`, sign -1, o=0, c0=0, C = LP2[0:729].

| quantity | value |
|---|---|
| O3 stored (9-register beam) pmax9 / pmax12 | 15.147 / 15.147 |
| re-decoded here, panel-R36 beam, pmax12 | **15.157** (LP1_REAL; n_skips 69) |
| null n / median / max | 562 / 11.32 / 15.54 |
| draws >= observed | 2 of 562 (0.36%); empirical quantile 0.9964 |
| Gumbel/POT single-decode p | 0.0067 |
| bars at L=729 N=1e3 / 1e5 / 1e6 | 19.86 / 23.20 / 24.86 |
| family-wise p over ~460 free cells (independent-cell bound) | 0.95; above the N=460 bar? **no** |

**Verdict: NOISE (below every pre-registered N>=1e3 bar; consistent with the null max).** O3's 100-draw max of 14.33 was a small-n maximum of the same distribution; with 562 draws the null max is 15.54. The sibling LP64 cell (13.37) sits at the 93rd percentile. Not a signal. Caveat: the seed was the max of a selected sweep and the null is shuffled-LP2 with random survivor-family keys, not real-LP2 structure; a real-structure null could sit slightly higher, which only strengthens NOISE.

## 4. Authorised edit
`round34/I1-v3-null/bars_v3.py`: `bar_v3(N, L, "free")` for L in {240, 400, 729} returns the fitted panel-R36 bars (nodes embedded, source `null_free.json`); L=120 default unchanged (R34 node), `panel="r36"` selects the R37 L=120 node; other L raise; `method="gpd"` for `free` now raises unless L=120 (it silently used the L=120 node before). The 4 old doctests are green, one added (`bar_v3(1e6, 729, "free")` = 24.9). Dated addendum appended to the R34 RESULTS.md.
Note: these `free` bars are **panel-R36 / 12-register** numbers; do not apply them to a pmax9 statistic. The PREREG said the new family would be exposed as a `panel` argument; as built, L in {240,400,729} returns the R36 node by default (no R34 node exists there) and `panel="r36"` is needed only at L=120.

## 5. not_covered
* 2,000 draws at L=120 (701), 240 (1335), 400 (726), 729 (562). N=1e6 bars are far-tail extrapolations (empirical max 11.7-15.5 vs bars 20-25), uncertain by roughly +-1.
* Control: only L=240 has 20 plants/register; L=400 (5) and L=729 (3) are indicative; no L=120 12-register control was run (R34's L=120 failure was a 9-register measurement).
* A real-LP2-structure (non-shuffled) null; a held-out-register-text null for `free`; `free` at other beam widths or lam_u; key families: nulls use the six B1/B2 families, plants use SHA-CTR.
* The planted control uses `free_q05` (5% unrelated advance) only; other free-like enciphering rates not tested.
* Contention: Lane T1 shared the CPU, so throughput at L>=240 was 40-60% of the quiet timing; the statistics do not depend on it.
* Operational note: a path bug briefly wrote two new stream files into round34/I1-v3-null/ (nothing overwritten); they were moved here and the path fixed.

## 6. ADDENDUM 2026-10-30 (b): free control completed to 20 plants/register at L=400 and L=729 (coordinator order; see ADDENDUM-2026-10-30-b.md)
This supersedes the "indicative only" wording in sections 0, 2 and 5 for L=400 / L=729. Bar of record = conservative Gumbel N=1e6 (GPD = sensitivity only, unchanged). 12 registers x 20 plants at each of L=240/400/729; ~12.5 min extra compute (RAM gate on).

| register | L=240 | L=400 (bar 21.67) | L=729 (bar 24.86) |
|---|---|---|---|
| EN_MODERN | 20/20 | 20/20 | 20/20 |
| EN_KJV | 20/20 | 20/20 | 20/20 |
| LP1_REAL | 20/20 | 20/20 | 20/20 |
| LATIN | 20/20 | 20/20 | 20/20 |
| OE | **3/20 FAIL** | 19/20 (min 21.3) | 20/20 |
| DE | 20/20 | 20/20 | 20/20 (min 29.0) |
| CY | 19/20 | 20/20 | 20/20 |
| EN_HALFVOWEL | **7/20 FAIL** | 20/20 | 20/20 |
| EN_NOVOWEL | 20/20 | 20/20 | 20/20 |
| GREEK | 20/20 | 20/20 | 20/20 |
| HEBREW | 20/20 | 20/20 | 20/20 |
| NORSE | 20/20 | 20/20 | 20/20 |

**Licensing verdict (>=19/20 at the N=1e6 bar of record):** `free` carries claims at **L=400 for all 12 registers** (OE at the threshold, 19/20) and at **L=729 for all 12 registers**; at **L=240 for 10 registers (all except OE and EN_HALFVOWEL)**. No claim at L=240 for OE/EN_HALFVOWEL. Caveats: the bars at 400/729 rest on 726/562 null draws (+-~1 on the N=1e6 bar); OE at L=400 passes with zero margin (one miss, 19/20); plants are SHA-CTR keys with `free_q05` enciphering only, so the licence is for a real `free`-type signal of that kind, not a statement about any key. The O3 re-judgement (NOISE) is unchanged.
