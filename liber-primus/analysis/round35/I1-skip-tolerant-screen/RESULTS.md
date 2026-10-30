# R35 / I1 -- pf_v4 skip-tolerant head screen (2026-10-30)

Status: MEASURED. Bar met at the frozen point (m=24, k=2, relation-agnostic OR screen, FPR 1e-3) -- but at ~10.9x pf_v3's cost, not the <=3x target.
Held-out data only is quoted (plants 1000-1999 per register per relation; null half B). pen chosen on calibration plants/half-A nulls (PREREG rule). Reproduced bit-identically on rerun.

## Method
Per-register Viterbi over cumulative key offset (s_t*a, s_t nondecreasing, s_0=0, s_t<=k; a=1 keyskip1, a=2 keyskip2), score = best-path trigram sum minus pen nats per skip, then the pf_v3 `lse` over the nine registers. k=0 reproduces pf_v3.lse_stat exactly (max |diff| = 0.0). "both" = OR of the a=1 and a=2 screens, each at FPR/2.
Plants: 2000/register x 9 x {keyskip1, keyskip2} through the real encipherer (sk.encipher_keyskip / j+=2 enc_pair), bash LP64 keystream, natural skip rate, no selection. 49-50 % of m=24 heads contain a skip.

## ROC: min over registers of (held-out natural power / bar), bar = 0.85 EN_NOVOWEL, 0.90 others; >=1.0 means bar met
Matched-relation screen (pen in parentheses, chosen per cell). FPR column = nominal; held-out FPR is within 0.9-1.05x nominal pooled.
| (m,k) | rel | 3e-4 | 1e-3 | 3e-3 | 1e-2 |
|---|---|---|---|---|---|
| 20,0 (= pf_v3) | a1 | 0.671 | 0.717 | 0.754 | 0.790 |
| 24,0 (= pf_v3 style) | a1 | 0.663 | 0.696 | 0.728 | 0.773 |
| 20,1 | a1 (pen3) | 0.922 | 0.972 | 1.000 | 1.029 |
| 24,1 | a1 (pen1) | 0.968 | 0.991 | 1.008 | 1.031 |
| 20,2 | a1 (pen3) | 0.957 | 1.017 | 1.053 | 1.089 |
| 24,2 | a1 (pen2) | 1.033 | 1.066 | 1.080 | 1.092 |
| 20,1 | a2 (pen3) | 0.937 | 0.976 | 1.009 | 1.030 |
| 24,1 | a2 (pen3) | 0.971 | 0.992 | 1.007 | 1.021 |
| 20,2 | a2 (pen3) | 0.967 | 1.026 | 1.056 | 1.086 |
| 24,2 | a2 (pen2) | 1.041 | 1.069 | 1.080 | 1.091 |

Relation-agnostic OR screen (worst of the two plant relations per register):
| (m,k) | 3e-4 | 1e-3 | 3e-3 | 1e-2 |
|---|---|---|---|---|
| 20,1 | 0.892 | 0.957 | 0.990 | 1.021 |
| 24,1 | 0.961 | 0.988 | 1.002 | 1.014 |
| 20,2 | 0.909 | 0.984 | 1.038 | 1.069 |
| 24,2 | 1.020 | **1.053** | 1.074 | 1.086 |
Full per-cell curves, per-generator FPR and per-register splits: roc.json (also roc_matched.json, roc_both.json).

## Frozen operating point (frozen_op.json)
m=24, k=2, rel=both, pen=2 nats/skip (both relations), lse thresholds a1 7.0994, a2 7.1761 (each component FPR 5e-4; total FPR 1e-3). Held-out total FPR 8.4e-4.
`pf_v4.prefilter_mask(seeds, variant, Chead, LMT, m=24, rel='both')` (same signature as pf_v3 plus optional rel; rel='keyskip1'/'keyskip2' runs one component at that relation's own threshold, but note frozen thr then corresponds to FPR 5e-4).

## Power at the frozen point (held-out, 1000 plants/register/relation)
Registers: EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL
- keyskip1 natural: 0.984 0.988 0.991 0.972 0.977 0.985 0.976 0.948 0.982
- keyskip1 skip-free: 1.000 0.998 1.000 0.992 0.998 1.000 1.000 0.981 0.998
- keyskip1 with-skip: 0.968 0.979 0.982 0.952 0.954 0.970 0.950 0.918 0.964
- keyskip2 natural: 0.981 0.987 0.994 0.975 0.965 0.987 0.978 0.949 0.980
- keyskip2 skip-free: 1.000 1.000 1.000 0.996 0.994 1.000 0.994 0.980 1.000
- keyskip2 with-skip: 0.961 0.974 0.987 0.953 0.934 0.973 0.962 0.920 0.959
EN_NOVOWEL natural 0.98 (bar 0.85); min other = EN_HALFVOWEL 0.948 (bar 0.90). ~470-480 with-skip NOVOWEL plants per relation (binomial se ~0.008). Baseline pf_v3-equivalent (k=0,m=20) natural 0.65-0.78, with-skip 0.24-0.48 (consistent with X1's 0.19-0.34 band, same direction; our plants include the 17 % unsuppressed doublets). Power conditional on no ciphertext doublet in the head (the real C[:40] has none) is within 0.01 of natural (roc_matched.json).

## FPR per generator (held-out half B, 65,536 heads each, frozen OR screen at 1e-3)
bash LP64 7.8e-4, bash ILP32 9.2e-4, PHP mt_scale 7.9e-4, mt_mod 9.6e-4, php_scale 7.9e-4, php_mod 7.8e-4; pooled 8.4e-4. Total null 131,072 per generator (>=1e5; split A/B). None exceeds 1e-3.

## Throughput (2^18 bash4.2 seeds, one process, end-to-end heads+decode+stat; throughput.json)
pf_v3 m=20: 617k heads/s. pf_v4: m24 k1 single relation 277k/s (2.2x); m24 k1 both 175k/s (3.5x); m24 k2 single relation 106k/s (5.8x); **frozen m24 k2 both 56.6k/s (10.9x)**; m20 k2 both 67.9k/s (9.1x). Target <=3x NOT met for any bar-meeting point. One ABI orbit (77.6M seeds) at the frozen point is ~23 min per ABI, ~46 min for both ABIs (the json field `orbit_minutes_155M_seeds_frozen` = 45.7 is both ABIs; the pre-screen is still cheaper than the beam by orders of magnitude).

## Q5 / cost tradeoff for the coordinator
Bar met at FPR 1e-3 only at (24,2). Cheaper options, none meets the bar at 1e-3: (24,1,both) 3.5x: NOVOWEL 0.907, min other 0.889 (fails by 0.011 on one register), meets the bar at FPR 3e-3 (NOVOWEL 0.922, min other 0.902). (20,2,both) 9.1x: fails at 1e-3 (min other 0.886), meets at 3e-3. So: either pay 10.9x for the bar at 1e-3, or 3.5x at FPR 3e-3 (3x more survivors into v3). The "not screenable" stop condition is not triggered.

## Caveats / not_covered
- pen tuned per cell on calibration plants; held-out numbers are post-selection-clean, but the grid is coarse (0-3).
- Plants use bash LP64 keystream; PHP/ILP32 plant power not separately measured (the key is statistically uniform for the screen; FPR measured on all six generators).
- Heads past 24 runes, >k skips in the head (k=2: a head with 3+ skips, rare), skips in a head whose ciphertext path is outside keyskip1/keyskip2 models, free relation, registers outside the nine, generators outside the six: not covered.
- Per-register Viterbi max then lse (not joint-path max); this is more permissive than a single shared path and is part of the measured FPR.
- Thresholds calibrated against the real C[:24] head; a different ciphertext head needs recalibration.
- Operational reach for B1 = coverage x this power, 0.95-0.98 on natural-rate plants vs pf_v3's 0.65-0.78 (on this panel).
- A lane-script path bug (common.py rebinds HERE) briefly wrote three json files into round32/B1-bash-random; they were moved into this lane and the script fixed; no other files there were touched.
