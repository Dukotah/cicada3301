# I3 PREREG -- D5c m_NV(L) = 0.055*L, pre-registered (Round 35)

_Dated 2026-10-30. Written BEFORE any key-R35I3a/b decode exists. Never rewritten; any later note goes in `ADDENDUM-<date>.md`._
Only prior run in this lane: a 60-draw/L EN_HALFVOWEL-stream yield pilot on the throwaway key `THROWAWAY-PILOT` (L=150/300/400; scratchpad, not in the lane dir, discarded), used solely to size the HALFVOWEL genuine sample. Pilot yields (EN_HALFVOWEL stream, over-bar): L=150 35/60 genuine with HALFVOWEL argmax (4 gray, 0 halluc); L=300 43/60; L=400 45/60; HALFVOWEL-stream hallucinations 0/180.

## Frozen rule (no tuning key this round)
* `m(L) = 0.0550 * L` exactly (constant 0.0550; read from the Round 34 I3 fitted nodes m_NV = 6.9476 / 10.4496 / 13.5766 / 20.2089 at L = 120 / 180 / 240 / 400, m/L = .0579/.0581/.0566/.0505; 0.055 is the post-hoc rounded central value, NOT fit to any R35 data). Thresholds: L=150 -> 8.25; L=300 -> 16.50; L=400 -> 22.00. (L=150 and 300 are interpolation/untested nodes; L=400 sits above its fitted node 20.21.)
* Accept a decode iff `pmax - bar >= m(L)` when the panel-argmax register is EN_NOVOWEL **or EN_HALFVOWEL** (decision, frozen: the SAME 0.055*L applies to HALFVOWEL-argmax; D5c's old margin 0 for HALFVOWEL is NOT used). Any other argmax register: accept iff `pmax - bar >= 0` (over bar), as D5c. bar = panelmax_bar("exact", 1e6, 0.01) of the Round 32 engine (7.6342), same engine/beam (keyskip exact, beam_w 400, supp 0.83, rec labels: halluc rec<0.90, genuine rec>=0.95, gray excluded) as Round 34 `ext.py`.
* As a non-binding diagnostic only, results also report the consequence of HALFVOWEL margin 0 (catch of the HV class at m=0). It does not enter pass/fail.

## Keys and lengths
Held-out only: `CICADA-R35I3a`, `CICADA-R35I3b` (both clean, new). L in {150, 300, 400}. Generators: `gen.py` (Round 34 ext.py recipe incl. same RNG convention; new seed offsets for HALFVOWEL stream 400000+, LATIN/DE/OE/EN_KJV 300000/310000/320000/330000, NOVOWEL 100000, each + (sum(key)%997)*7).

## Populations (classes defined by plant stream + panel-argmax of the decode)
* Hallucination class H-NV: NOVOWEL-stream plant, correct key, over bar, rec<0.90, argmax EN_NOVOWEL.
* Hallucination class H-HV: any NOVOWEL- or HALFVOWEL-stream plant, correct key, over bar, rec<0.90, argmax EN_HALFVOWEL.
* Genuine NV-only: NOVOWEL-stream, rec>=0.95, argmax EN_NOVOWEL. Genuine HV-only: HALFVOWEL-stream, rec>=0.95, argmax EN_HALFVOWEL.
* Genuine pooled register-spread: NV-only + HV-only + all genuine decodes of LATIN/DE/OE/EN_KJV streams (any argmax; those with non-NV/HV argmax have margin 0).

## Sample plan (fixed in advance; no extension)
Per key per L: NOVOWEL stream 1100 draws; HALFVOWEL stream 100 draws; LATIN, DE, OE, EN_KJV 60 draws each. Two keys pooled.
* Expected NV-only genuine, from Round 34 yields (genuine-NV/draw: L=240 0.080, L=400 0.032; L=120 0.198, L=180 0.106): L=150 ~0.15, L=300 ~0.055, L=400 ~0.032 -> per L over 2200 draws: ~330 / ~120 / ~70 (all >= 30).
* Expected HV-only genuine: pilot 0.58-0.75/draw over 200 draws -> ~115-150 per L (>= 30).
* H-NV: Round 34 NV-stream halluc yield 0.5-0.9/draw -> >1000 per L. H-HV: Round 34 NV-stream HV-argmax halluc rate 1/1800 (L120), 3/1800 (180), 13/1800 (240), 3/1800 (400) -> expect only ~1-30 per L over 2200 draws, probably < 30; this class is NOT sized to 30 (the HALFVOWEL stream yields ~0 hallucinations); its interval is reported as is.

## Pass criteria (every L, each separately; Wilson 95% score intervals)
1. catch >= 0.90 in H-NV (point estimate) AND catch >= 0.90 in H-HV (point estimate; n=0 -> cell not passed, "no evidence"); pooled-H catch also reported.
2. FR(pooled register-spread genuine) <= 0.10 (point).
3. Wilson-95 upper of FR(NV-only) <= 0.10 AND Wilson-95 upper of FR(HV-only) <= 0.10. A class with n<30 genuine is reported as is (interval as computed); it passes or fails on the interval only.
L passes iff all of 1-3. SEAL_PASS is false unless all three L pass all clauses; even then the lane only RECOMMENDS and lists not_covered (wrong-key overfits; non-exact relations; L other than 150/300/400, incl. 120-400 interpolation beyond these three; real pages; Welsh/CY; only 2 keys). No extensions, no re-tuning, no ledger flag flipped.
