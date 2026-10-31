# Round 41 / I1 -- PREREG (null12 refit on the survivor population)

_Dated 2026-10-31, written BEFORE any draw is made. Binding doctrine: ARMADA-DOCTRINE.md (R2: a negative with an unmeasured bar is not a negative). Plan: round41/CAMPAIGN-PLAN.md section 3 "I1" (Q1-Q5). No `git` run. One Python process, nproc=1; RAM check before each heavy stage (wait up to 20 min if free < 0.4 GB); draws streamed to disk in append mode; hard cap ~2 h._

## Why
Round 40 X1 (`round40/X1-redteam/RESULTS.md`, FOUND-ERROR #4/#5) showed the `null12` bars (round36/B1 `null12.json`: shuffled-LP2 wrong keys, NO prefilter) are fitted on a population less English-like than the survivors real sweeps decode (median pmax 2.33 vs 2.80; q99 4.06 vs 4.7). The bar must be fitted on the population it is applied to.

## Population definition (fixed now)
1. **Seeds**: wrong-key seeds drawn uniformly from SIX generator families: `bash4.2` (LP64), `bash4.2_i32`, PHP `mt_scale`, `mt_mod`, `php_scale` (legacy twist), `php_mod`. Bash seeds: uniform on the orbit prefix space (74 prefixes x 2^20 = the R37-I2 domain). PHP seeds: uniform on 2^32 (R32-B2 tier b). Blocks of 2^16 seeds, families in round-robin, RNG `numpy default_rng(4101)` (seeds recorded). Each survivor records its family and seed.
2. **Ciphertext**: the REAL LP2 stream `U` (the sweeps decode the real ciphertext, not a shuffle). Screen head `U[:24]`.
3. **Screen**: `round37/I2-pfv4-12reg/pf_v4_12` at the FROZEN point (`frozen_op12.json`: m=24, k=2, rel=both, pen 2, thr a1 7.4155 / a2 7.4412), reimplemented only to feed PHP heads (`php_mt.heads_all` + `reduce_heads`) through the identical `dp_regs`/`lse_from_regs`; bash heads via `pf_v4.heads`. Not conditioned on anything else.
4. **Decode**: every survivor decoded by `beam_v3.beam_decode_v3(panel_max, tau=0, lam_u=4, beam_w=400)` under panel-R36 (sha a0682f0c...), both relations (keyskip1 = advance 1, keyskip2 = advance 2), sign -1, offset 0, on `U[:120]` (L=120) and, for the first survivors in draw order, `U[:240]` (L=240); keystream = exact generator `ks(seed, ..., 1024)`. Adjudicated by `adjudicate` (pmax, preg, mds, ioc); degenerate decodes KEPT in the fit (as the sweep stores keep them) and counted separately.
5. **Counts (floors)**: >=40,000 survivors per relation at L=120 and >=5,000 per relation at L=240 (survivors are decoded under both relations, so counts are equal). Expect ~4.5e7 heads screened (screen rate ~1e-3).

## Fit
Round-34 recipe (`round34/I1-v3-null/fit.py::tailfit`): exponential (Gumbel-max) peaks-over-threshold above the empirical 90th percentile; `mu = u + beta ln p_u`; `bar(N) = mu + beta ln(N / -ln 0.99)`. Per relation x L; per-family fits at L=120 for heterogeneity (and L=240 where counts allow, flagged as thin).

## Recognizer and kill (Q1, Q5)
- **Q1a**: the refit bar at N=131,786 (L=120) must be >= the 99 % bar fitted by the same POT recipe to the POOLED real-sweep survivor rows (R37-I2 `sweep_rows.jsonl`, R40-B1 `sweep_rows.jsonl`, R40-B3 `rows_{B04,KDF,R17PAD,COSPAD}.jsonl`, L=120 rows) = X1's "empirical 9.6". (An empirical 1 %-FWER quantile at N=1.3e5 cannot be read off 3e5 rows directly; the POT bar is what X1 measured. I also report raw tail quantiles and the survivor max.) If it fails the population definition is wrong, not the data.
- **Q1b**: PLANTED correct keys, 20 per register x 12 registers x 2 relations (480 plants; bash 4.2 ABIs alternating), enciphered with the real `enc_exact` / `enc_pair`, test-half text, only filter = realised C[:40] doublet-free, passed through the REAL chunk path (pf_v4_12 on the 2^16-seed chunk holding the key -> v3 L=120 -> v3 L=240). Evaluated at L=120 and L=240. The criterion per (register, L, relation) cell: clears the N=1e6 refit bar in >=19/20. Prefilter losses are counted as failures of the path (the path is the instrument) and reported separately from conditional-on-prefilter.
- **Q5 (kill)**: if the Gumbel fit disagrees with the empirical data by >2 SE at N~131k (tested: (a) observed maxima of the three real stores' rows vs the fit-implied Gumbel location mu+beta ln N with SE 1.28 beta; (b) the null's own high-quantile counts vs fit-implied exceedance counts at q99, q99.9, q99.97 with Poisson SE), the empirical quantile is the bar of record and the report says so.

## Matched nulls (instrument deliverable)
`benchmark/bars_matched.py`: `bar_matched(stream, block_sizes=(100,250,1000), draws, stat_fn)`: block permutation of the stream within blocks of the given size keeping interrupters in place; fixture = the R13 walk (family Z p ~0.004 / 0.018 / 0.070 reproduced at block 100 / 250 / 1000 by X1's `rerun_r13_matched.py`). `bars_v3.bar_v3(..., family="survivor12")` returns the refit bars (default family unchanged). `tests/test_null_refit.py` wired into root `.github/workflows/ci.yml`.

## Re-judgement
Every Round 36-40 best row (R36-B1, R37-I2, R38-B2 if persisted, R40-B1 x2, R40-B3 x4, R40-C1 screened families) is re-judged against the refit bar at its actual N and at 1e6; any row that crosses is decoded at L=240 and bundled flagged-for-oracle (expectation: none).

## Conditionals (R-Q4)
This is a bar for the pf_v4_12-survivor population of the six keyskip-family generators on LP2[:120]/[:240] under beam_v3 panel_max / panel-R36; it is not a bar for direct (non-key) families (see matched nulls), not for registers outside the panel, not for the free relation, and the six-family mixture is the declared population (per-family bars reported; the pooled bar is the record unless heterogeneity says otherwise). Not a claim about any generator outside the six.
