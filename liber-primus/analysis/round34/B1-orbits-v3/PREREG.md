# R34 / B1 PREREG - the two orbits under pf_v3 + v3 (written FIRST, 2026-10-29, before any harness code was run)

Doctrine: ARMADA-DOCTRINE.md. Plan: round34/CAMPAIGN-PLAN.md s3 B1, s7. No git run. One Python process, nproc=1, streaming to disk.

## Instrument chain (all frozen inputs, none re-tuned here)
* Screen: `round34/I2-novowel-prefilter/pf_v3.py`, m=20 decoded heads at C[0] (skip-free-head argument of I2 RESULTS), lse threshold 3.9053751767817753 nats (frozen, FPR ~1e-3). No per-cell recalibration.
* Decoder: `round33/I1-register-aware-beam/beam_v3.py` `beam_decode_v3(design=panel_max, tau=0, lam_u=4, beam_w=400)`, keyskip1 = advance 1, keyskip2 = advance 2, sign -1, o=0. Adjudicator: `round32/I2` nine-register panel `adjudicate.adjudicate` (pmax). L=120 screen, L=240 gate, on LP2 unsolved stream.
* Bar of record: `round34/I1-v3-null/bars_v3.bar_v3(N, L, relation, family="lp2", method="gumbel")`, relations keyskip1 + keyskip2 ONLY. Reported at the ACTUAL N of each cell x relation (N = v3 L=120 decodes in that cell) AND at the declared N=1e6. No claim at L=31 or `free` (I1 control failed there).

## Cells and committed fractions
| cell | space | commitment | hard cap (screen + decode) |
|---|---|---|---|
| bash LP64 (bash4.2) | 74 prefixes x 2^20 = 77,594,624 seeds | FULL orbit (296 chunks of 2^18, order shuffled Random(3301)) | 3600 s |
| bash ILP32 (bash4.2_i32) | same orbit | same chunk order; stated fraction of what fits | 1500 s |
| PHP tier a | core 487 (decoded unfiltered) + dense 47,549 (pf_v3) = 48,036 seeds, x {mt,php} x {scale29,mod29} | full | inside PHP cap |
| PHP tier b | uniform numpy default_rng(3301) sample of 2^32 in blocks of 2^17, all four twist x reduction cells share the sample | stated fraction | PHP total 2100 s |
Total sweep cap 7200 s; with controls the lane hard cap is ~2.5 h. The remainder of ILP32 / PHP tier b is deferred with its fraction stated, never silently. Caps are fixed now and will not be changed after seeing results; if LP64 finishes early the slack is NOT rolled over.

## Positive control (before the sweep counts; REFUSE guard in sweep.py)
Through the REAL chunk path (pf_v3 prefilter on a 2^16-seed chunk containing the planted seed -> v3 L=120 screen of every survivor -> v3 L=240 gate -> panel). Per cell (bash LP64, bash ILP32, mt_scale, mt_mod, php_scale, php_mod) x relation (keyskip1 exact-skip plant, keyskip2 pair-skip plant): 5 EN_MODERN + 5 EN_NOVOWEL plants (I2 held-out test halves), L=240 ciphertext, plant windows chosen so the first 40 ciphertext runes are doublet-free (as the real LP2 head is, per I2 RESULTS). Pass per plant: passes the prefilter; L=120 pmax >= bar_v3(1e6,120,rel); L=240 pmax >= bar_v3(1e6,240,rel); L=240 recovery >= 0.90. Cell passes only if ALL 10 pass. Any NOVOWEL failure => fix the harness, no coverage claim. Nothing is claimed for a failing cell.

## Row handling
Every v3 L=120 decode is a SWEEPROW row in `sweep_rows.jsonl` (header carries v3 version, pf_v3 threshold/m, panel corpus hashes). Rows with pmax >= 6.0 are kept; after the sweep, any row clearing the L=120 bar at ACTUAL N is re-screened at v3 L=240 and judged against bar_v3(N_actual,240,rel); clearing both => `flagged-for-oracle` (never certified), listed with both scores. Near-miss = clears the actual-N L=120 bar but not the declared-N (1e6) bar. Top-5 per cell x relation always listed. Oracle/>=3 verifiers are the coordinator's step.

## Aiming Test
* Q1 hit = a seed whose keystream under keyskip1/2 decodes LP2[:120] to pmax >= bar and L=240 >= bar; recognizer proven by the control above, incl. NOVOWEL.
* Q2 prior: R18-L1 era (bash 4.2 / PHP) as in R32-B1/B2; R32 NOVOWEL reach 0.28-0.47 fixed by I2; flat prior within the sets.
* Q3 bounded: bash orbit enumerable (full for LP64); ILP32 and PHP tier b samplable (stated fractions).
* Q4 conditionals: (1) key space = the cells/fractions above, mod29 / scale29, sign -1, offset 0, C[0] aligned; (2) transition = keyskip1 + keyskip2 under v3 (not `free`, not L=31); (3) register = nine-register panel, reach = coverage x pf_v3 power x v3 envelope recovery, stated per register.
* Q5 kill: NOVOWEL plant failure => no coverage claim; Q5-of-I1 (bar not observed at actual N) => the Gumbel bar is modelled/conservative and is labelled so.

Verdict language: `negative (bounded, construction-conditional)` if control passes and nothing is flagged; never "closed/exhausted/solved".
