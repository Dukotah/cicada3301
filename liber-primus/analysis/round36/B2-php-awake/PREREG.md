# R36 / B2 PREREG - PHP mt_rand tier, awake, rows persisted (written FIRST, 2026-10-30 10:52 PDT, before any harness code ran)

Doctrine: ARMADA-DOCTRINE.md. Plan: round36/CAMPAIGN-PLAN.md s3 B2, s7. No git. ONE Python process, nproc=1, streaming rows, no filesystem-wide find. Addenda go in a separate dated file.

## Why (Aiming Test, brief)
Q1 recognizer: natural-rate plants (real enc_exact/enc_pair, no skip-free selection) pushed through the REAL chunk path per cell x relation; refuse to sweep unless >=3 recoveries in each pooled (register x skip-free/with-skip) split.
Q2 prior: R34-B1 PHP tier was damaged (X1 1a-1c): store reopened in WRITE mode on resume (rows lost); prior-dense tier prefiltered except 487 core seeds; uniform tier cut to 0.061 % by a laptop sleep. PHP mt_rand is a Round-18 L1 toolchain-promoted family (PHP in the Ubuntu-era box); this lane repairs the coverage, it adds no new hypothesis.
Q3 space: tier (a) 48,036 prior-dense seeds (enumerable); tier (b) uniform 2^32 per cell (samplable; target >=1 %).
Q4 conditionals: (1) key space = tiers a/b of PHP 5.x mt_rand, twist {canonical mt, legacy php<=7.0} x reduction {scale29, mod29}, offset 0, sign -1, C[0]-aligned; (2) transition model = keyskip1 + keyskip2 under beam_v3 (pf_v4 handles <=2 skips in 24 head runes); (3) register = round32/I2 nine-register panel, with measured reach only for EN_MODERN/EN_NOVOWEL (v3 recovery) and prefilter power for HALFVOWEL/LATIN.

## Instrument chain (frozen, nothing re-tuned)
* Screen: round35/I1 pf_v4 frozen_op.json (m=24,k=2,pen 2, thr a1 7.099447749731914 / a2 7.176139668549184, rel=both). PHP heads: php_mt.heads_all(seeds, 28) -> reduce_heads per reduction -> K[:m+a*k] -> pf_v4.lse_v4 (identical arithmetic to pf_v4.prefilter_mask, which only takes bash variants). Survivors of EITHER relation go to BOTH v3 relations.
* Decoder: round33/I1 beam_v3 panel_max tau=0 lam_u=4 beam_w=400; keyskip1=advance1, keyskip2=advance2; L=120 screen, L=240 gate. Adjudicator round32/I2 nine-register panel. Bars: round34/I1 bars_v3.bar_v3(N,L,rel) (lp2, gumbel), at actual N per cell x relation and declared N=1e6.
* pf_v4 power on these cells (R36-I2, natural, per register x relation, all >=0.940) is quoted per row in RESULTS.

## Phases (order fixed)
0. Control: per cell (mt_scale, mt_mod, php_scale, php_mod) x relation (keyskip1, keyskip2) x register (EN_MODERN, EN_NOVOWEL): 10 plants (= 160), rng Random(3301), PHP seed uniform 32-bit, plaintext windows from held-out testhalves, only filter = realised C[:40] doublet-free. Each plant: (i) real chunk path (2^16-seed chunk containing it -> pf_v4 -> v3 L120 both rels on survivors -> L240 -> panel); (ii) ALSO an unfiltered direct v3 L120+L240 decode of the planted seed (for tier-a reach). recover = pass both declared-N=1e6 bars AND recovery240 >= 0.90. Splits skip-free / with-skip (any of C[:24] != (P+K)%29). Gate: >=3 recoveries in every pooled register x split. Cell-level numbers also reported.
1. Tier (a) core 487 seeds (R34 tier_a_seeds core list; assert 487): decoded UNFILTERED, all 4 cells, both relations.
2. Tier (a) dense (48,036 - 487 = 47,549, list order): decoded UNFILTERED (no prefilter) in list order for as long as a 10-minute compute cap allows (decode rate measured live); the remainder runs through pf_v4. BOTH subsets and their reach are reported separately. Costing note: 48,036 x 4 x 2 = 384k v3 decodes; whether the full list fits is decided by the live rate under this rule, not by hand.
3. Tier (b): numpy default_rng(3301) blocks of 2^17 uint64 draws in [0,2^32); each block screened for all four cells (equal fraction per cell); target 330 blocks (43.25 M = 1.007 % of 2^32) per cell; hard cap 55 min compute (sum of per-block times; blocks that stall >120 s are logged as sleep gaps and excluded). The process sets SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED) so the laptop does not sleep. Achieved fraction is stated per cell; duplicates in the uniform draw are not removed (stated).
4. Overall hard cap ~90 min wall. If a cap fires, report what ran; do not extend.

## Store discipline
sweep_rows.jsonl created once with header (AD.header: v3 version, pf_v4 frozen point, panel hashes, I2 per-cell power); ANY resume opens it with "a" and the harness refuses mode "w" on a non-empty file. State (sweep_summary.json) saved after every block; rows flushed before state. validate_store + check_r3_store at finalize.

## Adjudication
Bars from bars_v3 at actual N (decodes of that cell x rel) and N=1e6. pmax >= L120 bar -> re-decode at L=240 with cell key -> pmax240 >= L240 bar -> FLAGGED_FOR_ORACLE (SEAL_PASS=false). Clears actual-N bar but not declared-N: listed as near-miss. No "solved/closed/exhausted" language.

## Addendum A (written before the control or sweep produced any output; dated 2026-10-30 ~11:00 PDT)
A 2^16-seed single-cell timing probe (not a result) measured pf_v4 + survivor decode at ~2.6 s per 2^16 seeds per cell (~25-30 k seeds/s, slower than the 56 k/s in R36 plan because other lanes share the laptop) and v3 at ~330 decodes/s. Consequence: a full 1.007 % tier b for four cells (~95 min) does NOT fit the 60-min cap; the achieved fraction will be lower and is reported as such (not extended). Caps set accordingly: dense-unfiltered 10 min (about half the dense list, ~41 seeds/s x 4 cells x 2 rels), tier b 55 min compute (target 330 blocks stays the stopping rule if reached first). Expected total: control ~9 + core <1 + dense 10 + tier b 55 = ~75 min wall, inside the ~90-min cap.
