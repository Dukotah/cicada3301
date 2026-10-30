# R35 / B1 - the bash 4.2 orbit re-screened with pf_v4 (RESULTS)

Pre-registration: [`PREREG.md`](PREREG.md) (written before any code ran). Artifacts: `control.json`/`control.log`, `sweep_rows.jsonl` (276,243 SWEEPROW rows + header; `validate_store` ok; `check_r3_store` -> `[]`), `sweep_summary.json` (raw per-ABI stats, phases), `sweep_summary_final.json` (bars, top-5, flagged), `keep_rows.json` (rows pmax >= 6.0), `sweep.log`. One process; controls ~4 min, sweep 3,479 s (LP64 1,816 s + ILP32 1,663 s), inside the 70-min cap.

## Verdict
**NEGATIVE (bounded, construction-conditional).** Both ABIs screened in FULL (296/296 chunks). 0 rows clear the L=120 bar at actual N, 0 flagged-for-oracle, 0 near-miss. Nothing certified.

## Positive control (natural-rate plants, real chunk path)
pf_v4 frozen (m=24,k=2,rel=both) on a 2^16-seed chunk -> v3 L=120 (both rels, all survivors) -> v3 L=240 -> panel. 12 EN_MODERN + 12 EN_NOVOWEL per (ABI x relation) = 96 plants (real `enc_exact` / `enc_pair`, supp 0.83). The only plant filter is that the realised ciphertext C[:40] has no doublet (as the real head); NO skip-free selection. "with-skip" = a skip altered any of the first 24 enciphered runes (undetected skips that land on an equal key rune, ~1/29, are counted skip-free). pass = prefilter AND L120 >= declared-N bar AND L240 >= declared-N bar; recover = pass AND L240 recovery >= 0.90.

Pooled over 2 ABIs x 2 relations (n / prefilter / pass / recover):
| register | skip-free | with-skip (head 24) |
|---|---|---|
| EN_MODERN | 23 / 23 / 23 / 23 | 25 / 24 / 24 / 24 |
| EN_NOVOWEL | 28 / 28 / 28 / 28 | 20 / 18 / 18 / 18 |

Natural with-skip share of plants: 48 of 96 (50%). Gate (>= 3 recoveries in every register x skip split): PASSED. Every plant that passed the prefilter also passed both bars and recovered >= 0.90 (v3 conditional recovery 1.00 here; n is small). The 3 failures are all prefilter misses: EN_NOVOWEL with-skip keyskip1 LP64 (seed 1340129854), EN_NOVOWEL with-skip keyskip2 LP64 (1345422025), EN_MODERN with-skip keyskip2 ILP32 (1382834568).

Per ABI x relation (recover / n; skip-free | with-skip), from `control.json`:
| cell | MODERN sf | MODERN ws | NOVOWEL sf | NOVOWEL ws |
|---|---|---|---|---|
| LP64 keyskip1 | 6/6 | 6/6 | 7/7 | 4/5 |
| LP64 keyskip2 | 5/5 | 7/7 | 4/4 | 7/8 |
| ILP32 keyskip1 | 4/4 | 8/8 | 8/8 | 4/4 |
| ILP32 keyskip2 | 8/8 | 3/4 | 9/9 | 3/3 |

**Coordinator decision point (Q5).** The brief says a with-skip NOVOWEL plant that fails the chunk path means fix the harness. 2 of 20 with-skip NOVOWEL plants failed, both at the prefilter stage, and none downstream. This is consistent with pf_v4's measured with-skip NOVOWEL power (0.964 keyskip1 / 0.959 keyskip2 on 1000+ plants; expected misses ~0.8 of 20; P(>=2 of 20) ~ 0.2) and I judge it a screen miss, not a harness defect (every decode/adjudication step on passing plants is clean), but a per-ABI x relation x split guarantee of 100% was not shown. The coverage claim below therefore uses the measured pf_v4 power (<1), not 1.0, and ILP32 keyskip2 NOVOWEL with-skip rests on only 3 plants. If the coordinator reads the rule strictly, treat the claim as withheld pending a larger with-skip NOVOWEL control; the sweep was run because the pooled gate passed.

## Sweep (both ABIs full)
| ABI | seeds screened | fraction of orbit | pf_v4 survivors | v3 L=120 decodes (per relation) | rows |
|---|---:|---:|---:|---:|---:|
| bash 4.2 LP64 | 77,594,624 | 1.000 (296/296) | 69,017 | 69,017 x keyskip1 + 69,017 x keyskip2 | 138,034 |
| bash 4.2 ILP32 | 77,594,624 | 1.000 (296/296) | 69,104 | 69,104 x 2 | 138,208 |

Survivor rate 8.9e-4 (the frozen screen's measured FPR was 8.4e-4). This is 0.85x Round 34's 81,414 / 80,985, NOT the 1.7-2x anticipated: pf_v4 was frozen at total FPR 1e-3 with a lower realised null FPR than pf_v3, so the decode load did not grow; what grew is the screen cost (~30 min per ABI vs ~2 min).

## Best pmax vs bars (bar_v3, lp2, Gumbel; L=120)
| ABI | relation | N actual | best pmax (register, seed) | bar @ actual N | bar @ N=1e6 | clears |
|---|---|---:|---|---:|---:|---|
| LP64 | keyskip1 | 69,017 | 6.349 (LP1_REAL, 1368828634) | 8.221 | 9.235 | no |
| LP64 | keyskip2 | 69,017 | **7.068** (LP1_REAL, 1354603465) | 8.058 | 9.034 | no |
| ILP32 | keyskip1 | 69,104 | 6.679 (EN_HALFVOWEL, 1375265595) | 8.222 | 9.235 | no |
| ILP32 | keyskip2 | 69,104 | 6.762 (LP1_REAL, 1354603465) | 8.059 | 9.034 | no |
Seed 1354603465 (keyskip2) is the same R32-B1 / R33-B3 / R34-B1 near-miss again, now 1.0 below the actual-N bar. Top-5 per cell are in `sweep_summary_final.json`.

## Flagged / near-miss
Flagged-for-oracle: none. Near-miss (clears actual-N but not declared-N): none. No L=240 re-screen was triggered. Oracle / >=3-verifier steps are the coordinator's.

## Coverage x power per register
Reach = coverage x pf_v4 natural power (round35/I1, held-out, per relation) x v3 recovery on prefilter-passers. Coverage = 1.000 for both ABIs. v3 recovery on prefilter-passers = 1.00 in this control (95/95 passers pass both bars and recover >= 0.90; n small, so treat as >= ~0.97 lower-bound-ish, not exactly 1). So reach ~ pf_v4 power. Power (keyskip1 / keyskip2 natural):
| register | EN_MODERN | EN_KJV | LP1_REAL | LATIN | OE | DE | CY | EN_HALFVOWEL | EN_NOVOWEL |
|---|---|---|---|---|---|---|---|---|---|
| keyskip1 | 0.984 | 0.988 | 0.991 | 0.972 | 0.977 | 0.985 | 0.976 | 0.948 | 0.982 |
| keyskip2 | 0.981 | 0.987 | 0.994 | 0.975 | 0.965 | 0.987 | 0.978 | 0.949 | 0.980 |
Orbit-level reach 0.95-0.99 per register on a key that lives in the orbit, vs ~0.65-0.70 in Round 34. (With-skip subset: 0.92-0.99; this control's with-skip NOVOWEL prefilter rate 18/20 = 0.90 is within sampling noise of I1's 0.96.)

## Three conditionals
1. Key space: bash 4.2 auto-seed orbit (74 x 2^20 seeds, LP64 and ILP32, both complete), %29, offset 0, sign -1, C[0]-aligned.
2. Transition model: keyskip1 + keyskip2 under beam_v3 panel_max, L=120 screen / L=240 gate; screen is the frozen skip-tolerant pf_v4 (heads with <= 2 skips in 24 runes). Not `free`, not L=31.
3. Register: nine-register panel; reach per register as tabulated, plant control uses only EN_MODERN and EN_NOVOWEL.

## not_covered
Heads with >= 3 skips in 24 runes; the `free` relation; L=31; offsets != 0; other reductions (scale29, etc.); other bash versions / seeding paths (explicit `RANDOM=`, srandom variants, time-seeded outside the 74 prefixes); other PRNGs (PHP tiers not re-run here; Round 34 PHP stands); registers outside the nine; thresholds are calibrated to the real C[:24] head; pf_v4 power was measured on LP64 keystream plants (ILP32 not separately measured for power, FPR measured 9.2e-4); ILP32 keyskip2 NOVOWEL with-skip control n=3; the control's with-skip label misses skips that land on an identical key rune (~1/29).
Reopens if: the oracle clears a flagged row (none), or an oracle shows a true-key head with > 2 skips in 24 runes.
