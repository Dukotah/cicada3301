# I3 PREREG -- D5c m_NV(L) calibration (Round 34)

_Dated 2026-10-29. Written BEFORE any feature table for this lane existed (only a 25-draw timing run at L=400 on a throwaway key, deleted)._

## Populations
Lean re-implementation (`ext.py`) of round32/I4 `extract.py` (same panel, exact keyskip beam_w=400, supp 0.83, bar 7.6342, labels:
halluc = pmax>=bar and recovery<0.90; genuine = recovery>=0.95). Regenerated at every L in {120,180,240,400} (all cells fresh, new seeds).
* hallucination set: EN_NOVOWEL stream, correct key, over-bar & rec<0.90 (the I4 planted overfits).
* genuine sets: EN_MODERN; NOVOWEL-only (EN_NOVOWEL stream rec>=0.95); spread (LATIN/DE/OE/EN_KJV rec>=0.95); pooled register-spread = NOVOWEL + spread.
* draws per key per L: 450 NV, 30 EN, 15 per spread stream.

## Key assignment (FROZEN)
* TUNING key: `CICADA-X1R33` (all m_NV fitting, all L).
* HELD-OUT keys: `CICADA-I4b`, `CICADA-I4c`, `CICADA-R34I3` (new), pooled per L; scored once after m_NV frozen.

## Recipes
1. D5c as written: accept iff (pmax-bar) >= m_NV(L) for EN_NOVOWEL-argmax decodes, >=0 otherwise. m_NV(L) fitted per L on the tuning key:
   among thresholds with tuning NOVOWEL-genuine FR <= 0.05, maximise tuning catch; m = midpoint of the tied-optimal interval (the I4 rule).
2. Normalised: threshold = c * beta(L), beta(L)=0.07194*(L/120)^-0.5463 (round32/I3 `fit_new_only`; extrapolated to 400, flagged). A SINGLE constant c is
   fitted on the tuning key pooled over all four L, same rule (pooled tuning NV-genuine FR<=0.05, max pooled catch).

## Pass criterion (every L, each recipe, held-out only)
catch >= 0.90 AND FR(EN_MODERN) <= 0.10 AND FR(pooled register-spread) <= 0.10 AND Wilson-95 upper of FR(NOVOWEL-only) <= 0.10.
If NOVOWEL-only held-out n is too small for the Wilson upper to reach 0.10 even at 0 rejects (n<37), that L is recorded "underpowered" = NOT passed.
Round passes only if both-or-either recipe passes at ALL four L; SEAL_PASS stays false regardless (no ledger flag flipped); the measured ceiling per L
(max held-out catch s.t. NOVOWEL FR upper<=0.10 and pooled FR<=0.10, with m free -- an oracle-on-held-out optimistic bound) is reported as a diagnostic only.
