# I4 RESULTS -- Non-fold oracle-seal proxies (reopens round21/L1 KILL)

_Run 2026-10-28. Binding: `ARMADA-DOCTRINE.md`. Pre-registration: `PREREG.md` (main body + Addendum A + Addendum B,
each written before the data it governs existed). `tests/validate.py` -> ALL VALIDATIONS PASSED before reporting.
All statistics are oracle-free; truth labels only score catch / false-reject. Nothing here says a puzzle is solved
or closed._

## Verdict (bounds, not verdicts)

* **`SEAL_PASS = false` (ledger flag unchanged).** None of the pre-registered non-fold designs (D1 longer head,
  D2 per-register fold bar, D3 learned gate, D4 hybrids) delivers >= 0.90 catch at <= 0.10 held-out false-reject
  *across registers*. The two learned gates clear the L1-style test (EN_MODERN genuine only) at 1.00 / 0.00 but
  do it by detecting the **register**: they reject **13 of 13** correct-key EN_NOVOWEL genuine decodes. L1's own
  genuine panel (EN_MODERN only) could not see that failure mode -- a finding about the criterion.
* **A seal candidate exists and passes a virgin split: D5c, a per-register `pmax` margin.** Accept iff
  `pmax - bar >= m_NV` for EN_NOVOWEL-argmax decodes (`m_NV = 14.0128`, frozen on all data seen before
  virgin-2) and `>= 0` otherwise. On virgin-2 (never examined, L=240): **catch 378/392 = 0.964** (Wilson95
  0.941-0.979), **FR on EN_MODERN genuine 0/40**, **FR on pooled register-spread genuine 1/113 = 0.009**
  (NOVOWEL 1/33, Wilson upper 0.153; LATIN/DE/OE/EN_KJV 0/80). It was derived **post hoc** (Addenda A/B) after
  the pre-registered designs failed, it is **length-conditioned** (see below), and its scope is only the class
  measured. I therefore do **not** flip the ledger flag: `SEAL_CANDIDATE = D5c`, conditional, pending the
  coordinator decisions at the end. Measured ceiling of the pre-registered families: see tables.

## Positive controls (run first, gated everything)

| control | expected | measured | status |
|---|---|---|---|
| hallucination population rebuilt | L1: 45 tuning / 66 held-out | **40 tuning / 69 held-out** (corpora not byte-identical, see not_covered) | PASS (n>=20/30 gate) -- NOT bit-identical |
| genuine EN_MODERN panels | 20 / 24 all rec>=0.95 | **20/20, 24/24** | PASS |
| single-cut (hitfn20 1/4 cut) baseline leak | 15/45 = 0.33 (held 0.318) | **12/40 = 0.30 tuning, 16/69 = 0.23 held-out** | PASS -- leak reproduced |
| L1 fold family (k=5, min, 0.90) | 0.800/0.000 tune, 0.818/0.167 held | **0.825/0.050 tune, 0.855/0.167 held; 0.803/0.133 on virgin-1; 0.798/0.150 on virgin-2** | PASS -- same ceiling, ~0.80-0.86 |
| bar | 7.634 | 7.6341931878728095 (unchanged; 8-register panel) | PASS |
| hard-register genuine planted | needed to expose register detectors | correct-key EN_NOVOWEL rec>=0.95: 5 / 8 / 17 / 33 (tune/held/virgin-1/virgin-2); LATIN/DE/OE/EN_KJV 14-20 each | built |

The planted-hit recogniser for this lane is exactly the genuine sets above (including the register-spread ones, the
real shapes a true solve in those registers would take). Note the fold-family control reproduces L1's ceiling on a
differently built population, so the comparison with 0.818/0.167 is meaningful at the family level.

## ROC table -- pre-registered designs (frozen on tuning by the stated rule, held-out scored once)

Tuning: 40 hallucinations vs 20 EN_MODERN genuine (and 5 NOVOWEL genuine). Held-out: 69 hallucinations vs 24 EN_MODERN
genuine, plus pooled register-spread genuine n=64 (8 NOVOWEL + 56 LATIN/DE/OE/EN_KJV). `catch/FR` = rate;
brackets = Wilson 95%. `reg FR` = false-reject on the register-spread genuine.

| design | frozen cell | tuning catch / FR | held-out catch | held-out FR (EN) | held-out reg FR | L1-comparable | strict |
|---|---|---|---|---|---|---|---|
| CTRL fold k-min (L1 family) | k=7, min >= 0.85 | 0.925 / 0.100 | 0.884 [0.79,0.94] | 0.167 [0.07,0.36] | 0.375 | no | no |
| D1 longer head (single cut) | cut at 192 runes, tail >= 0.95 | 0.550 / 0.000 | 0.536 [0.42,0.65] | 0.042 | 0.078 | no | no |
| D1b multi-head AND | heads >= 144, all >= 0.98 | 0.925 / 0.100 | 0.841 [0.74,0.91] | 0.208 | 0.312 | no | no |
| D2 per-register fold bar | k=7, tau_N=0.90 (no extra bar chosen) | 0.925 / 0.100 | 0.884 [0.79,0.94] | 0.208 | 0.375 | no | no |
| D3a learned, register-blind | LR lambda=0.01, thr 0.0414 (LOO) | 1.000 / 0.000 | **1.000** [0.95,1.00] | **0.000** [0.00,0.14] | **0.156** (NOVOWEL **8/8** rejected) | **yes** | **no** |
| D3b learned, register-aware | LR, thr 0.9984 (LOO) | 1.000 / 0.000 | 1.000 | 0.042 | **0.531** (NOVOWEL 8/8, OE 14/14 rejected) | yes | no |
| D4 hybrid per-reg fold AND head | k=5, tau_N 0.96, cut96>=0.90 | 0.850 / 0.050 | 0.899 [0.81,0.95] | 0.167 | 0.281 | no | no |
| D4b hybrid LR-blind AND fold5 | thr 0.2 AND fold5 >= 0.90 | 1.000 / 0.050 | 1.000 | 0.167 | 0.312 | no | no |

391 pre-registered cells were scored in total (66 + 66 + 42 + 42 + 2x50 + 54 + 21).
**Family ceilings.** Using held-out *hindsight* (the best cell chosen by looking at held-out data -- optimistic, not an
operating point): fold family 0.739 catch at FR <= 0.10; D1 0.536; D1b 0.435; D2 0.739; best cell satisfying
FR_EN <= 0.10 AND reg FR <= 0.10 anywhere in D1-D4 = **0.623 catch** (D2, k=3, tau_N=0.90: FR 2/24, reg FR 6/64).
D3a/D3b reach 1.00 catch only by rejecting the hard registers (hindsight reg FR 0.56 / 0.53).
Because the hallucination set is a corpus-window sample and cell choice is on 40 vs 20 cases, selection noise is
large; every held-out interval above is wide.

## Why the learned gates are not seals

D3a is "register-blind" by feature list (no argmax register, no z vector), yet `ioc`, `mds`, `h2`, `zl`, `pmax` and
the fold/cut statistics jointly encode the register. Breakdown on its frozen threshold: EN_MODERN genuine 0/44 rejected;
EN_NOVOWEL correct-key genuine 13/13 rejected; LATIN 2/14; DE, OE, EN_KJV 0/14. A gate that rejects every correct
EN_NOVOWEL decode would block exactly the vowel-dropped solve the seal exists to certify. This is why the strict
criterion (register-spread genuine) was pre-registered; the L1-comparable test alone would have been passed.

## Exploratory: what actually separates hallucination from genuine inside EN_NOVOWEL

Within the EN_NOVOWEL stream (109 hallucinations vs 13 genuine, seen data, pooled, not a clean test) the best single
oracle-free statistics are `ioc` (AUC 0.996), `pmax` (0.992), `pmax_ne`, `pcon`, `h2` (0.981); fold/cut
self-consistency AUCs are far lower (cut at 192 = 0.74). Reason: a hallucination is, by selection, a decode that only
just clears the panel-max bar; a correct decode clears it by a wide margin. That motivated D5.

## D5 -- pmax margin (post hoc, Addenda A and B; decided on virgin splits)

Virgin-1 (key `CICADA-I4`, L=240; 157 hallucinations, 30 EN genuine, 17 NOVOWEL genuine, 56 spread genuine):

| gate | catch | FR EN_MODERN | FR pooled register-spread | note |
|---|---|---|---|---|
| D5a global margin, m*=14.758 frozen on tuning | 154/157 = 0.981 | 0/30 | **18/73 = 0.247** (NOVOWEL 3/17, spread 15/56) | fails strict |
| D5b D5a AND fold5 | 156/157 | 4/30 | 39/73 | fold clause re-introduces the L1 false-rejects |
| fold5 min 0.90 (control) | 126/157 = 0.803 | 4/30 | 27/73 | L1 ceiling |

Diagnosis: genuine margin is register-specific (OE median ~13, LATIN ~17, EN 16-25, DE/KJV 19-25, NOVOWEL 14-18) while the
hallucination margin tops out ~15.8; one global m over-rejects OE. Addendum B froze the per-register D5c before
virgin-2 existed.

Virgin-2 (key `CICADA-I4b`, L=240; 392 hallucinations, 40 EN, 33 NOVOWEL genuine, 80 spread genuine; **decisive**):

| gate | catch | FR EN_MODERN | FR NOVOWEL genuine | FR LATIN/DE/OE/KJV | FR pooled | PASS (>=0.90, <=0.10) |
|---|---|---|---|---|---|---|
| **D5c per-register margin, m_NV=14.0128** | **378/392 = 0.964** [0.941,0.979] | **0/40** [0,0.088] | 1/33 = 0.030 [0.005,0.153] | 0/80 | **1/113 = 0.009** [0.002,0.048] | **yes** (point estimates; NOVOWEL Wilson upper 0.153 > 0.10) |
| D5a global m*=14.758 (second look) | 390/392 = 0.995 | 0/40 | 5/33 = 0.152 | OE 19/20 | 24/113 = 0.212 | no |
| fold5 min 0.90 (control) | 313/392 = 0.798 | 6/40 = 0.150 | 22/33 | 15/80 | 37/113 = 0.327 | no |
| D5c AND fold5 | 390/392 | 6/40 | 22/33 | 15/80 | 37/113 | no |

Virgin-2 ROC over `m_NV` (catch / FR NOVOWEL genuine): 13.0 -> 0.890 / 0.000; 13.5 -> 0.934 / 0.000; 14.0 -> 0.962 /
0.030; 14.5 -> 0.982 / 0.121; 15.0 -> 0.992 / 0.212. The usable window is narrow (~13.5-14.2), set by the overlap
of the hallucination tail (max margin 16.0, 13 of 392 above 14) with the genuine floor (min 13.7).
Two EN_HALFVOWEL-argmax hallucinations in virgin-2 get `m_r=0` and are not protected by D5c.

## Length-dependence probe (exploratory, not part of the verdict)

Same D5c with the L=240-frozen `m_NV` applied to fresh **L=120** data (272 hallucinations, 92 NOVOWEL genuine, 39 EN
genuine, 78 spread genuine): catch 272/272, but **FR 92/92 on NOVOWEL genuine** -- every correct decode rejected. At
L=120 the margins sit much lower (hallucination max 8.7, NOVOWEL genuine median 8.4, min 5.8); within-L AUC is 0.989 and an
in-sample refit gives 0.967 catch at NOVOWEL FR 0.098 with m ~ 7.3. So the *mechanism* separates at both lengths but `m_NV`
is a function of L (14.0 at 240, ~7.3 at 120, only two calibration points); a single constant is wrong. Real LP2 pages
differ in length, so D5c is not usable on an arbitrary candidate until `m_NV(L)` is calibrated.

## Value = coverage x power (R2) and the three conditionals (Q4)

* Coverage: 391 pre-registered cells (D1-D4) + D5a/D5b/D5c on three disjoint populations: tuning (40/20), seen held-out
  (69/24), virgin-1 (157/30), virgin-2 (392/40), plus register-spread genuine (LATIN, DE, OE, EN_KJV x 14/14/20 draws)
  and an L=120 probe.
* Power: the pre-registered non-fold families: best strict hindsight catch **0.623**; fold family 0.74-0.86 as in L1;
  learned gates 1.00 only via register detection. D5c: 0.964 catch at 0.009 pooled FR on virgin-2 at L=240.
* Conditionals carried by every number: (1) key space = **correct key only**; (2) decoder relation = **exact (keyskip1)
  preset**, hallucinations planted by `encipher_keyskip`; (3) adjudicator = **8-register panel** (CY missing), the
  hallucination class is EN_NOVOWEL-argmax.
* R3 statistics (decrypt IoC, min-distinct, H2/zl, non-English pmax) are persisted per case in `feat_*.json`.

## not_covered

1. **Welsh/CY register**: `data/keys/welsh/welsh_mabinogion.txt` is missing; the panel was rebuilt in this lane's
   `models/` with 8 registers and 4000 null draws/length (originally 9 / 20000). Welsh genuine and Welsh-argmax
   hallucinations are unmeasured. The 7.634 bar was kept (calibrated for 9 registers).
2. **Population identity**: `data/kjv.txt` and `data/keys/mabinogion.txt` are missing; same-named texts from
   `analysis/bookcipher/books/` were substituted, so the 45/66/20/24 populations were NOT reproduced bit-identically
   (got 40/69/20/24); the original I2 panel is not the one used. The 15/45 single-cut count was re-measured, not assumed.
3. **Hallucination classes other than correct-key EN_NOVOWEL / exact preset**: wrong-key overfits, keyskip2/drift-relation
   overfits, EN_HALFVOWEL or non-English-argmax hallucinations (D5c's `m_r=0` leaves them unprotected), and Latin/OE/DE
   vowel-dropped variants.
4. **Length**: only L=240 (decisive) and L=120 (probe, shows `m_NV` must scale). No calibration curve; real page lengths
   untested. Partial recoveries (0.90-0.95, labelled gray: 8/7/14/39 per split) are excluded from both classes.
5. **Genuine realism**: all genuine sets are synthetic correct-key enciphers of corpus windows (none is a genuine
   solved-page decode, since the originals' source files are what the L1 lane also used); a real LP2 plaintext with
   lower language fit than corpus text would have a smaller margin than D5c assumes. Small NOVOWEL genuine counts
   (5/8/17/33) leave the NOVOWEL FR upper bounds above 0.10.
6. **Selection/multiplicity**: D5/D5c were designed after seeing the seen-split margin distributions; D5c's m_NV was fit on
   data that includes virgin-1; only virgin-2 is clean. D5c has not been independently replicated.
7. Several other designs in the brief's spirit not built: a trained neural gate, per-register *adaptive* head lengths,
   fold bars tuned per register on non-EN genuine, and cross-validated threshold stacking on independent splits.
8. The seal is a proxy-power bound for the classes above; it says nothing about whether any specific LP2 candidate is a solve.

## Decisions for the coordinator

1. **Accept D5c as the working no-oracle gate?** It clears the bar on a virgin split, but only conditionally. Recommended:
   keep `SEAL_PASS=false` until (a) a refute-by-default verifier re-runs `analyze_d5c.py` on a third virgin key and (b)
   `m_NV(L)` is calibrated on >= 4 lengths. Meanwhile a survivor with `pmax - bar` below the L-appropriate margin is
   *flagged-for-oracle*; one above it AND passing the existing 3-clause hit predicate can be treated as strongly
   supported (the margin is a necessary-condition filter against the measured leak, not a proof).
2. **Fix L1's criterion going forward**: the EN_MODERN-only genuine panel passes register detectors; require the
   hard-register genuine set (correct-key EN_NOVOWEL, LATIN/OE/DE) in every seal audit.
3. Restore the missing Welsh and `data/kjv.txt` / `data/keys/mabinogion.txt` inputs (another lane is on Welsh), then rerun
   `python shim.py` and the analysis scripts to move from an 8- to the 9-register panel.

## Reproduce

```bash
cd liber-primus/analysis/round32/I4-nonfold-seal
python shim.py                                  # rebuild panel into ./models (8 registers)
for p in tune_nv tune_en held_nv held_en spread virg_en virg_sp virg_nv virg2_en virg2_sp virg2_nv; do python extract.py $p; done
for p in l120_en l120_sp l120_nv; do I4_L=120 python extract.py $p; done
python analyze.py; python within_register.py; python breakdown.py
python analyze_d5.py; python analyze_d5c.py; python analyze_l120.py
```
(`catch_surface.json` already holds the merged outputs of all analysis scripts.)
