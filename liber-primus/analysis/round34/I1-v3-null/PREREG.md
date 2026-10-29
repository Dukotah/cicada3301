# Round 34 / I1 -- v3 null of record: PREREG
_Dated 2026-10-29T14:16:51 (before any output file in this directory). Lane I1, plan section 3._

## Aiming test
- Q1 recognizer: planted correct key (Round 33 I1 plant machinery: SHA-256-CTR key, supp 0.83, held-out halves, window Random(9000+s), 20 seeds per register, all 9 registers) at each L and relation must have pmax >= fitted family-wise bar at N=1e6, alpha=0.01, in >=19/20 seeds per register. Reported per (L, relation, register, family); failures are reported as failures.
- Q2 measured: beam_v3 panel_max (hard max, lam_u=4, beam_w=400), adjudicator statistic = nine-register panel pmax (batch path, checked equal to adjudicate on a sample).
- Q3 bounded: ONE python process, hard 90-minute total wall cap (null + control + fit). A speed probe (in the scratchpad, before this file) measured wrong-key v3 decodes/s: L31 189/316 (adv1/adv2), L120 108/141, L240 20/15, L400 6.3/4.6. At those rates the target (>=40k per cell family a, >=10k per register family b) costs ~19000 s at L=400 alone, so it does NOT fit. Budget (draws per cell, both relations decoded on each draw; keys round-robin over B3's six families, seeds drawn from the stored survivor seeds as in B3 readjud.py null):
  - family a (shuffled real LP2, Random(3301+k)): L31 40000, L120 40000, L240 6000, L400 1200; free L120 ~1000.
  - family b (shuffle of held-out EN_NOVOWEL, LATIN, OE, DE text; the shuffled register text is the ciphertext; wrong keys): L31 3000/reg, L120 3000/reg, L240 500/reg, L400 200/reg.
  Cells shortfall vs the targets is stated in RESULTS. Time-guard: each cell stops at its own wall allotment if slower than probed; results are streamed to disk per 200 draws.
- Q4: conditionals carried: keyskip1/keyskip2/free relations only (max_skip 8/8/40), nine-register panel, sign -1, o=0, SHA-CTR plants; shuffled-stream null (not a real-key null).
- Q5 (from plan): exponent of beta(L) vs Round 32 I3 -0.55 +/- 0.04; if > 3 combined SE apart, stop and report that v3 may not be Gumbel-tailed; bars_v3 then exposes the empirical quantile and says so.

## Method (fixed in advance)
- Tail model: exponential (Gumbel-max) peaks-over-threshold above the empirical 90th percentile u, p_u = fraction above, beta = mean excess (SE = beta/sqrt(k)). mu = u + beta ln(p_u) (the single-trial Gumbel location). Bar(N, alpha) = mu + beta ln(N / (-ln(1-alpha))). Sensitivity to u at the 85th/95th percentile reported. Tail-shape check by GPD moment estimate xi.
- beta(L): OLS of ln beta on ln L over the four L, per relation and family; SE from OLS (2 DOF).
- bars_v3: beta from the fitted power law, mu from the cell-anchored location interpolated linearly in ln L (flat outside 31..400); L=400 uses its own thin sample unless it is declared fitted-from-three.
- Compare observed bar at N=2e5, L=120 to B3's modelled 8.546 (keyskip1) / 8.373 (keyskip2).
- No "solved / closed / exhausted" language. No git.
