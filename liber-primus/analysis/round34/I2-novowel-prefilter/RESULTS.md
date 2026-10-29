# R34 / I2 RESULTS -- NOVOWEL-aware prefilter (2026-10-29)

**Bar (NOVOWEL >= 0.85, every other register >= 0.90 at FPR <= 1e-3): MET at m=20 (and m=24; m=16 is marginal-to-met).**

## Frozen operating point
`pf_v3.py`: statistic `lse` = log-sum-exp over the nine registers of the head trigram LLR vs uniform (mixture likelihood ratio),
on the first **m=20** decoded runes, pass if lse > **3.9053751767817753** nats. Pooled-null FPR 1.0e-3 (per generator 0.90-1.2e-3, see roc.json);
survivor volume is ~1.7x R32-B1's 6e-4. m=16 alternative: thr 5.5972, FPR 1e-3, NV 0.986, weakest EN_HALFVOWEL 0.943.
API: `heads/ioc_stat/tri_stat` re-exported unchanged from pf.py; new `lse_stat`, `screen(P,LMT,thr)`, `prefilter_mask(seeds,variant,Chead,LMT,m=20)` (drop-in for B1 `prefilter_scores`, returns the survivor mask directly; no per-variant mu/sd needed).

## Key measurement finding (coordinator should read)
The real unsolved ciphertext `U[:40]` contains **zero doublets**. A skip occurs only at a ciphertext doublet, so the true-key head decode is
skip-free for any m<=40. The old 0.47 NOVOWEL figure came from planting with *random* ciphertexts whose own doublets cause skips (about half of
24-rune heads) -- that is a property of the plant, not of the real attack. Operative power = the **no-skip** column. The with-skip column
(B1-comparable pessimistic plants, enc_pair/enc_exact, 200/register) is also given; there the same screen is ~0.6 for everything, so it is
skip-dominated, not register-dominated. Same-plant baseline: pf.py's zmax at m=16 is NV 0.973 / weakest 0.853 (HALFVOWEL) no-skip, 0.62 with-skip --
so the statistic change (zmax -> lse) is what lifts the weakest registers over 0.90; the NOVOWEL gain relative to B1's 0.47 is mostly the plant correction.
If the true cipher head is not at C[0] (key offset into C) the doublet argument does not apply and with-skip power is the relevant number.

## ROC at FPR target 1e-3 (calibrated on half of each null, FPR on the other half; 262,144 heads per generator x 6 generators, 400 no-skip plants/register)
| m | stat | FPR (held-out) | NOVOWEL | worst other (reg) | NV w/skip | min other w/skip |
|--|--|--|--|--|--|--|
| 16 | zmax | 0.00105 | 0.973 | 0.853 (EN_HALFVOWEL) | 0.62 | 0.615 |
| 16 | llrmax | 0.00107 | 0.988 | 0.932 (EN_HALFVOWEL) | 0.645 | 0.68 |
| 16 | lse | 0.00104 | 0.988 | 0.932 (EN_HALFVOWEL) | 0.645 | 0.675 |
| 16 | pq | 0.00103 | 0.985 | 0.917 (EN_HALFVOWEL) | 0.64 | 0.665 |
| 16 | OR | 0.00077 | 0.973 | 0.902 (EN_HALFVOWEL) | 0.62 | 0.65 |
| 20 | zmax | 0.00108 | 0.998 | 0.968 (EN_HALFVOWEL) | 0.6 | 0.63 |
| 20 | llrmax | 0.00102 | 1.0 | 0.988 (EN_HALFVOWEL) | 0.625 | 0.645 |
| 20 | lse | 0.00103 | 1.0 | 0.988 (EN_HALFVOWEL) | 0.62 | 0.645 |
| 20 | pq | 0.00109 | 1.0 | 0.975 (EN_HALFVOWEL) | 0.61 | 0.625 |
| 20 | OR | 0.00076 | 0.998 | 0.978 (EN_HALFVOWEL) | 0.605 | 0.63 |
| 24 | zmax | 0.00100 | 1.0 | 0.995 (OE) | 0.58 | 0.63 |
| 24 | llrmax | 0.00099 | 1.0 | 0.998 (LATIN) | 0.615 | 0.615 |
| 24 | lse | 0.00100 | 1.0 | 0.998 (LATIN) | 0.615 | 0.615 |
| 24 | pq | 0.00102 | 1.0 | 0.995 (OE) | 0.605 | 0.63 |
| 24 | OR | 0.00071 | 1.0 | 0.995 (OE) | 0.605 | 0.62 |

Full curves at FPR 3e-4, 1e-3, 3e-3, 1e-2 for every statistic and m: `roc.json`.

## Power per register (2000 fresh no-skip plants each, SE <= 0.006; `power_per_register.json`)
| register | m=16 | m=20 (FROZEN) | m=24 |
|--|--|--|--|
| EN_MODERN | 0.996 | 1.0 | 1.0 |
| EN_KJV | 0.997 | 0.9995 | 1.0 |
| LP1_REAL | 1.0 | 1.0 | 1.0 |
| LATIN | 0.98 | 0.995 | 0.998 |
| OE | 0.976 | 0.9975 | 0.998 |
| DE | 0.9975 | 0.9995 | 1.0 |
| CY | 0.9785 | 0.997 | 1.0 |
| EN_HALFVOWEL | 0.943 | 0.9905 | 0.997 |
| EN_NOVOWEL | 0.9855 | 0.998 | 1.0 |

Operating point m=20: NOVOWEL 0.998, min other 0.9905. FPR 0.00103 pooled held-out.

## Throughput (single process, 2^18 bash4.2 seeds end-to-end heads+decode+stat, best of 3; `throughput.json`)
pf.py trigram m=16: 1,282,480/s; pf_v3 m=16: 1,111,808/s (1.16x slower); **pf_v3 m=20: 977,563/s (1.31x slower)** -- below the plan's 1.4-2.3x. (Absolute rate is an isolated micro-benchmark; R32-B1's sweep ran ~39k/s with overheads, so use the ratio.)

## not_covered
Heads past a first skip / non-C[0] alignment (with-skip power ~0.6); `free` relation; registers beyond the nine (a novel register is not guaranteed);
panel LMs trained on the non-held-out half, plants from testhalves (held-out) but short LP1_REAL (1769 runes) gives overlapping windows;
PHP generators use heads_all/reduce_heads vectorised (no anti-repeat nuance); IoC/other non-LM features not tried; thresholds calibrated on bash+PHP pooled null (per-gen FPR 0.9-1.2e-3).

## Coordinator decisions
1. Accept m=20 lse thr 3.905 as B1's prefilter (survivors ~1.7x vs R32). 2. Confirm C[0]-aligned head assumption (else with-skip power applies). 3. B1 PHP use of pf_v3.screen requires passing reduce_heads output as K.
Stray-file note: an early run of run.py wrote roc.json/_norm.json into round32/B1-bash-random (common.py shadowed HERE); both deleted, nothing else touched there.

---

## X1/R34 addendum (2026-10-29) -- appended by the red-team lane; text above unchanged

**FOUND-ERROR in "Key measurement finding".** `U[:40]` does have zero doublets (X1 re-checked: also `U[:120]`), but that does not make the true-key head skip-free. A key skip happens when the *candidate* cipher rune equals the previous emitted one and is **invisible in the emitted ciphertext**, so a doublet-free head says nothing about skips. X1 `rerun_i2_skipfree.py` (600 R32-style plants per cell, bash4.2, enc_pair/enc_exact): the fraction of heads with no skip in the first m = 18 / 20 / 24 runes is 0.63 / 0.57-0.59 / 0.49-0.54, and 0.54-0.64 even among plants whose cipher head contains no doublet. The operative power is therefore the **with-skip column** (about 0.62-0.66 for every register at FPR 1e-3; X1 re-run: this screen 0.655-0.663 EN_NOVOWEL, 0.707-0.713 EN_MODERN), not the no-skip 0.998. R32-B1's 0.47 NOVOWEL prefilter power reproduces under its own logic (0.555-0.62 at m=18/24) and is not a planting artefact; `round32/B1-bash-random/RESULTS.md` and its ledger row stand. What I2 genuinely shows: on skip-free heads the lse screen lifts the weakest registers (HALFVOWEL 0.853 -> 0.932 at m=16), and FPR re-checks at 1.07-1.08e-3 on fresh seeds. Any B1 reach statement must use the with-skip power. A skip-tolerant head screen (DP over advance 1/2 on the first ~20 runes) is the untried lever.
