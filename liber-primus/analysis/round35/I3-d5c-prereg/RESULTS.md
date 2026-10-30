# I3 RESULTS -- pre-registered D5c, m(L)=0.055*L (Round 35)

_2026-10-30. Binding: PREREG.md (mtime 09:30, before any R35I3 feature file). Keys CICADA-R35I3a/b pooled (held-out only). No extension, no re-tune. **SEAL_PASS = false. The rule FAILS pre-registration at all three L (150, 300, 400); do not adopt.**_

## Table (Wilson 95% in brackets; reject = margin < threshold)
| L | m | catch H-NV (NOVOWEL-argmax overfits) | catch H-HV (HALFVOWEL-argmax overfits) | FR NV-only genuine | FR HV-only genuine | FR pooled spread | PASS |
|---|---|---|---|---|---|---|---|
| 150 | 8.25 | 1156/1355 = 0.853 [.833,.871] FAIL | 9/9 = 1.00 [.70,1.0] | 0/324 [0,.012] | 97/134 = 0.724 [.643,.793] FAIL | 97/984 = 0.0986 ok | **no** |
| 300 | 16.50 | 1725/1760 = 0.980 [.972,.986] | 9/9 = 1.00 [.70,1.0] | 16/101 = 0.158 [.100,.242] FAIL | 146/146 = 1.00 [.974,1] FAIL | 162/776 = 0.209 FAIL | **no** |
| 400 | 22.00 | 1915/1924 = 0.995 [.991,.998] | 12/12 = 1.00 [.76,1.0] | 23/56 = 0.411 [.292,.541] FAIL | 148/148 = 1.00 [.975,1] FAIL | 171/731 = 0.234 FAIL | **no** |

Other-register spread genuine (LATIN/DE/OE/KJV, margin 0): 0 rejects of ~470 per L. H-HV n = 9/9/12 (<30 as pre-announced; HALFVOWEL stream gives ~0 hallucinations, all H-HV come from NOVOWEL-stream plants). Genuine n >= 56 in every class (NV-only 324/101/56; HV-only 134/146/148). Diagnostic (non-binding): with HALFVOWEL margin 0, H-HV catch = 0/9, 0/9, 0/12 -- D5c as written leaves this class entirely unprotected.

## Margin quantiles (p10/p50/p90 of pmax-bar, diagnostic)
| L | NV genuine | HV genuine | H-HV | H-NV |
|---|---|---|---|---|
| 150 | 9.5/10.9/12.2 | 6.2/7.8/8.7 | 0.1/0.3/1.0 | 1.6/5.5/8.6 |
| 300 | 16.2/17.9/20.1 | 12.1/13.5/14.7 | 0.1/0.3/1.9 | 3.7/10.3/14.8 |
| 400 | 20.5/22.4/24.8 | 15.7/17.0/18.5 | 0.3/0.5/1.3 | 6.2/13.7/19.0 |

## Reading
* Pre-registered verdict: FAIL at every L. Failure modes: (1) at L=150 the NV catch is 0.853 (threshold 8.25 sits inside the H-NV tail; NV genuine median 10.9 is fine); (2) at L=300/400 the linear 0.055L overshoots the NV genuine margins (median 17.9 vs 16.5; 22.4 vs 22.0), rejecting 16% / 41% of NV genuine -- Round 34's nodes (13.58@240, 20.21@400) were fitted on another key set and the genuine margin grows slower than 0.055L here (NV genuine median/L = .073/.060/.056); the Round 34 L=400 pass does not replicate on new keys (its n was 100 with a different threshold 20.21 vs 22.0 here); (3) applying the same 0.055L to HALFVOWEL-argmax rejects essentially all HV genuine (HV genuine margins are ~0.75x NV's and sit below 0.055L at every L).
* Diagnostic only (hindsight; not a result): HV hallucinations have margin <= ~2 at all L while HV genuine have p10 >= 6.2, so a separate small HV threshold (a few units, maybe ~0.02L) would separate the classes; any such rule would need its own pre-registration on fresh keys. NV also looks separable with a lower scale than 0.055L at L=300/400 (NV genuine p10 16.2/20.5 vs H-NV p90 14.8/19.0) -- again hindsight.
* Caveat: keys a/b have sum(key)%997 = 857/858, so draws of b are a 7-rep shift of a's (same plaintext windows, different keys/ciphertext); the two keys are not fully independent in plaintext. Does not alter the failure.

## not_covered
Wrong-key overfits; non-exact relations; L outside {150,300,400}; real pages; Welsh/CY; only 2 keys; H-HV class small (n=9/9/12) and sourced only from NOVOWEL-stream plants; HV margin-0 consequence measured only as diagnostic.

## Coordinator decisions
1. Rule 0.055L is rejected as pre-registered; retire the linear rule, or authorize a fresh pre-registration (new keys) with a per-class (NV vs HV) margin form fitted on a tuning key -- the margin data above says the HV scale is clearly lower than NV's.
2. Whether to treat the Round 34 "R1 passes 4/4 L" claim as unreplicated (L=400 NV rejection 41% here at 22.0; per-L fitted thresholds, not the linear form, were what Round 34 validated).
