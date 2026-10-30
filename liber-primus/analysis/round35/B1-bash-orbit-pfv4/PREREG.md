# R35 / B1 PREREG - bash 4.2 orbit re-screened with pf_v4 (written FIRST, 2026-10-30 09:4x PDT, before any harness code was run)

Doctrine: ARMADA-DOCTRINE.md. Plan: round35/CAMPAIGN-PLAN.md s3 B1, s7. No git run. One Python process, nproc=1, streaming rows. Addenda go in a separate dated file.

## Instrument chain (frozen inputs, nothing re-tuned)
* Screen: `round35/I1-skip-tolerant-screen/pf_v4.prefilter_mask(seeds, variant, Chead, LMT, m=24, rel='both')`, frozen_op.json (m=24, k=2, pen 2, thr a1 7.0994 / a2 7.1761, total FPR ~1e-3). Survivors of EITHER relation's screen go to BOTH v3 relations.
* Decoder: round33/I1 `beam_v3` panel_max, tau=0, lam_u=4, beam_w=400; keyskip1=advance 1, keyskip2=advance 2; sign -1, o=0, C[0]-aligned. Adjudicator: round32/I2 nine-register panel. L=120 screen, L=240 gate.
* Bars: `round34/I1-v3-null/bars_v3.bar_v3(N, L, rel, family="lp2", method="gumbel")`, relations keyskip1 + keyskip2 only (no `free`, no L=31), at the cell's ACTUAL N (v3 L=120 decodes in that ABI x relation) and at declared N=1e6.
* Cells: bash 4.2 LP64 (`bash4.2`) and ILP32 (`bash4.2_i32`), 74 prefixes x 2^20 = 77,594,624 seeds each, 296 chunks of 2^18, order shuffled Random(3301), reduction %29.

## Positive control (REFUSE guard: sweep will not start unless control gate passes)
Real chunk path: pf_v4 (rel='both') on a 2^16-seed chunk containing the planted seed -> v3 L=120 on all survivors, both relations -> v3 L=240 gate -> panel.
Plants: for each ABI x relation (keyskip1 -> real `enc_exact`/encipher_keyskip; keyskip2 -> real `enc_pair`, supp 0.83), 12 EN_MODERN + 12 EN_NOVOWEL (>=10 required), windows from the I2 held-out test halves, seed uniformly from the orbit prefixes. NATURAL RATE: the ONLY plant filter is that the realised CIPHERTEXT C[:40] has no doublet (as the real LP2 head has); there is NO skip-free selection (the R34 flaw at sweep.py:70-71 is not repeated). Skips are labelled afterwards: with-skip = any enciphered rune among the first 24 differs from the naive (P+K) rune (the screen's head); skip-free otherwise. (A skip whose shifted key happens to be equal mod 29 is undetected; ~1/29, stated.)
Per plant: `prefilter_pass`, L120 pmax, L240 pmax, recovery240. `pass` = prefilter pass AND L120 >= bar_v3(1e6,120) AND L240 >= bar_v3(1e6,240) (declared-N bars). `recover` = pass AND recovery240 >= 0.90.
Gate (before any null counts): >=3 recoveries in EACH of {skip-free, with-skip} x {EN_MODERN, EN_NOVOWEL} pooled over ABI x relation, AND the same >=3 in each ABI x relation x skip split where >=3 plants of that split exist is REPORTED (not gating). Any with-skip EN_NOVOWEL plant failing the chunk path (prefilter or bars) = investigate/fix the harness; no coverage claim for that ABI x relation until fixed. Pass/recover reported separately for skip-free vs with-skip.

## Caps (fixed now, not changed after seeing results)
Controls ~10 min. Screening+decoding total cap 4200 s (70 min): LP64 first (own cap 2700 s), then ILP32 for the remaining time (4200 s - LP64 elapsed). If the cap binds, the ILP32 fraction = chunks done / 296 is stated, never silent; unfinished chunks are listed as not_covered. Slack is not rolled over. Hard total cap ~90 min.

## Rows / flagging
Every v3 L=120 decode is a SWEEPROW row (header with v3 version, pf_v4 frozen point, panel hashes). Rows pmax >= 6.0 kept. After the sweep, rows clearing the L=120 bar at actual N -> L=240 re-screen vs bar_v3(N_actual,240); clearing both -> flagged-for-oracle (never certified), both scores listed. Near-miss = clears actual-N L=120 but not declared-N. Top-5 per ABI x relation always listed. Store must pass `validate_store` and `handoff/validate_ledger.check_r3_store`.

## Aiming Test
* Q1 recognizer: the control above, natural-rate, both registers, skip split, through chunk path.
* Q2 prior: R18-L1 era bash 4.2; R32-B1/R34-B1 enumerated; measured reach was 0.65-0.70, pf_v4's measured natural power 0.95-0.99 (round35/I1 RESULTS) is the lift.
* Q3 bounded/enumerable: yes, 2 x 77.6M.
* Q4 conditionals: (1) key space = bash 4.2 auto-seed orbit, %29, offset 0, sign -1, C[0]-aligned, stated ABI fractions; (2) transition = keyskip1 + keyskip2 under v3 (not `free`, not L=31), heads with <=2 skips in 24 runes; (3) register = nine-register panel, reach = coverage x pf_v4 natural power (I1 table) x v3 recovery (control) , per register.
* Q5 kill: with-skip NOVOWEL chunk-path failure => no coverage claim.
Verdict language: `negative (bounded, construction-conditional)` if control passes and nothing flagged; never "closed/exhausted/solved".
