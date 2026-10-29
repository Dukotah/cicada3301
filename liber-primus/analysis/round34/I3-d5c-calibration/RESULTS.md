# I3 RESULTS -- D5c m_NV(L) calibration (Round 34)

_2026-10-29. Binding: PREREG.md (written before any feature table). Tuning key `CICADA-X1R33`; held-out keys `CICADA-I4b`, `CICADA-I4c`, `CICADA-R34I3` pooled. All populations regenerated fresh by `ext.py` (lean copy of round32/I4 recipe, ~450 NV / 30 EN / 60 spread draws per key per L). SEAL_PASS stays **false**; no ledger flag touched._

## Held-out table (pooled 3 keys; Wilson-95 in brackets)

| L | recipe | fitted threshold | catch | FR EN_MODERN | FR pooled spread | FR NOVOWEL-only | PASS |
|---|---|---|---|---|---|---|---|
| 120 | R1 per-L m_NV | 6.948 | 631/674 = 0.936 [0.915,0.952] | 0/90 | 10/466 = 0.021 | 10/289 = 0.035 [0.019,0.063] | yes |
| 180 | R1 | 10.450 | 843/923 = 0.913 [0.893,0.930] | 0/90 | 1/333 = 0.003 | 1/154 = 0.006 [0.001,0.036] | yes |
| 240 | R1 | 13.577 | 969/1031 = 0.940 [0.924,0.953] | 0/90 | 1/296 = 0.003 | 1/118 = 0.008 [0.001,0.046] | yes |
| 400 | R1 | 20.209 | 1138/1182 = 0.963 [0.950,0.972] | 0/90 | 2/223 = 0.009 | 2/44 = 0.045 [0.013,0.151] | **no** (NV Wilson upper 0.151 > 0.10; n=44) |
| 120 | R2 c*beta(L), c=101.73 | 7.319 | 654/674 = 0.970 | 0/90 | 27/466 = 0.058 | 27/289 = 0.093 [0.065,0.133] | no (NV upper) |
| 180 | R2 | 5.864 | 375/923 = 0.406 [0.375,0.438] | 0/90 | 0/333 | 0/154 [0,0.024] | no (catch) |
| 240 | R2 | 5.012 | 206/1031 = 0.200 | 0/90 | 0/296 | 0/118 | no (catch) |
| 400 | R2 | 3.791 | 60/1182 = 0.051 | 0/90 | 0/223 | 0/44 [0,0.080] | no (catch) |

Fitted R1 curve (tuning key): m_NV = 6.95 / 10.45 / 13.58 / 20.21 at L = 120 / 180 / 240 / 400, i.e. ~0.050-0.058 per rune (m_NV/L = .058, .058, .057, .051): the margin scale grows roughly linearly in L. Per-key refit values agree within ~0.2-1.0 (240: 13.58-14.41; 400: 19.6-21.1).

## Verdict

* **R1 (D5c with a per-L m_NV) passes at L=120, 180, 240 on all four clauses, and fails at L=400 on exactly one clause**: NOVOWEL-only held-out FR 2/44, Wilson upper 0.151. Catch there is 0.963 and pooled FR 0.009, so the failure is a small-n/fit-noise problem on the genuine side (tuning key had only 14 NOVOWEL genuine at L=400; the fitted 20.21 sits above the held-out-optimal ~19.7; both rejects are on `CICADA-R34I3`, 0 of 26 on the other two keys). It is not a demonstrated separability failure.
* **R2 (normalised by null beta(L)) fails at every L**, and structurally so: beta(L) falls as L^-0.55 while the observed margin threshold rises ~L^+1, so a single constant c cannot serve (it over-rejects genuine NOVOWEL at L=120 and passes ~nothing of the hallucinations at L>=180). The null-beta normalisation is the wrong scale for pmax margin.
* **SEAL_PASS = false** (Q5: a recipe fails at L=400 and R2 everywhere; and the prereg requires all four L). Survivors stay flagged-for-oracle.

## Per-L ceiling (diagnostic; optimistic - m chosen with held-out labels)

Best held-out catch subject to NOVOWEL Wilson upper <= 0.10, pooled FR <= 0.10, EN FR <= 0.10: L=120 0.955 (m 7.14); L=180 0.957 (m 11.08); L=240 0.967 (m 14.20); L=400 0.940 (m 19.66). So the mechanism separates at all four lengths with a hindsight m; the honest, frozen-in-advance result is R1 pass at 3 of 4 L. Not a seal proof: real LP2 pages need m_NV(L) to be applied at their own L (interpolation between nodes unmeasured; 120-400 only).

## Positive controls / sanity
Tuning-key values at 120 and 240 (6.95, 13.58) bracket Round 32's in-sample refit (~7.3 at 120) and frozen 14.01 at 240; L=120 genuine NOVOWEL now accepted (10/289 rejected) vs Round 33's 53/53 with the 240 constant, confirming the length-conditioning diagnosis. My `ext.py` is a re-implementation, not bit-identical to I4 seeds/streams (spread hallucinations, 1 case at 120, ignored).

## not_covered
EN_HALFVOWEL-argmax hallucinations (m=0 under D5c, unprotected; planted set is NV stream only); wrong-key overfits; non-exact (skip_by_two etc.) relations; lengths between nodes or >400 (interpolation untested); real (non-planted) pages; R2's beta(L) is extrapolated to 400 and uses round32 fit constants; tuning NV-genuine n is small at 400 (14) so the L=400 fit is noisy; Welsh/CY register absent (8-register panel); panels rebuilt in I4 models/; NV-only genuine n at L=400 (44) cannot show Wilson upper <=0.10 unless 0-1 rejects; held-out keys include two keys reused from Round 32 (different L than originally used, fresh seeds).

## Coordinator decisions
1. Accept "3 of 4 L" as progress or demand a rerun at L=400 with larger NV-genuine sample (cheap: ~2 min per 450 draws/key; ~1500 draws per key would give ~30 genuine each).
2. Whether to adopt the linear working rule m_NV ~ 0.055*L (empirical, not pre-registered) as a Round 35 pre-reg.
3. Drop R2 (null-beta normalisation) as a candidate.
