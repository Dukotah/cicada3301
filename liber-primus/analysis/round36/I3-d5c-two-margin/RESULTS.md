# I3 RESULTS -- D5c two-margin successor (Round 36)

Run exactly per `PREREG.md` (dated 2026-10-30, written before any decode). `gen.py` = Round 35's; `calibrate.py` = Round 35's with the two-margin rule; `derive_margins.py` = the freeze-time derivation; data `feat/`, scores `results.json`, `run.log`.

## Frozen margin tables (derivation: smallest m with catch >= 0.90 on existing R34/R35 data, rounded up 0.1; FR on same data <= 0.012)
| L | m_NV | m_HV | notes |
|---|---|---|---|
| 150 | 8.7 (raw 8.612, R35, 1355 halluc/324 genuine) | 5.3 (raw 5.22, R35, only 9 halluc/134 genuine) | measured |
| 240 | 12.8 (raw 12.774, R34, 1377/144) | 4.5 | m_NV measured; **m_HV INTERPOLATED** linearly between 5.3@150 and 3.9@300 (no genuine HV-only decode exists at 240 in any prior file) |
| 300 | 14.9 (raw 14.812, R35, 1760/101) | 3.9 (raw 3.839, R35, 9 halluc/146 genuine) | measured |

## Keys
`CICADA-R36I3a-x` class 26, `CICADA-R36I3b-zzz` class 273 (the plain names collide: R36I3a = 858 = R35I3b). Prior classes: CICADA 405, CICADA3301 604, I4 575, I4b 673, I4c 674, X1R33 771, R34I3 759, R35I3a 857, R35I3b 858. All distinct.

## Per-L x class (two keys pooled; k/n, Wilson 95 %)
| L | catch H-NV | catch H-HV | FR NV-only | FR HV-only | FR pooled genuine (n) | L verdict |
|---|---|---|---|---|---|---|
| 150 | 1253/1353 = 0.926 [0.911,0.939] | **7/8 = 0.875 [0.529,0.978]** | 1/258 [0.001,0.022] | 0/134 [0,0.028] | 1/922 = 0.001 | **FAIL** (H-HV point < 0.90) |
| 240 | 1505/1667 = 0.903 [0.888,0.916] | 13/13 = 1.0 [0.772,1.0] | 0/162 [0,0.023] | 0/133 [0,0.028] | 0/836 | PASS |
| 300 | 1616/1788 = 0.904 [0.889,0.917] | 18/18 = 1.0 [0.824,1.0] | 0/98 [0,0.038] | 0/148 [0,0.025] | 0/774 | PASS |

Diagnostic (non-binding): HALFVOWEL margin 0 would catch 0/8, 0/13, 0/18 of H-HV, so the HV margin is doing real work. Gray excluded as in R35.

## Reading
* Two of three L pass every clause; L=150 fails exactly one clause, H-HV catch 7/8 (one hallucination of eight had margin >= 5.3; the Wilson interval [0.53,0.98] straddles 0.90, so this is a one-event miss on a tiny class, but the PREREG rule is point >= 0.90 and it failed). No re-tune, no extension.
* H-NV catch sits at 0.903-0.904 at 240/300: the tables were set at the 0.90 edge, so these passes are marginal (lower Wilson bounds 0.888/0.889 are below 0.90). The genuine-side FR is essentially zero everywhere, i.e. m could have been higher at no genuine cost; the binding constraint is catch, and the tables were derived at its minimum by construction.
* H-HV is tiny (8/13/18, never 30); m_HV rests on 9 hallucinations per L in the freeze data. 240's m_HV is interpolated and its genuine FR (0/133 HV-only) is the first direct measurement there, which came out clean.
* Key independence: classes 26 and 273 share no sum(key) class with any earlier key, so the rep-shift caveat of Round 35 does not apply.

## SEAL verdict
**SEAL_PASS = false.** all_L_pass = false (150 fails). Per Q5: ceiling recorded (the two-margin rule holds at 240 and 300 on fresh keys, fails at 150 on the H-HV clause); the lane recommends **not** adopting D5c-successor for a seal and recommends pausing seal-instrument work for a round (or, if the coordinator wants one more try, a fresh pre-registration with an enlarged H-HV sample at L=150, not an edit of this one).

not_covered: wrong-key overfits; non-exact relations; L other than 150/240/300; real pages; Welsh/CY; only two keys; H-HV n<30 at every L; m_HV(240) interpolated; margin tables sit at the 0.90 catch edge.
