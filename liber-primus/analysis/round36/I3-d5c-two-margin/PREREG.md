# I3 PREREG -- D5c two-margin successor (Round 36)

_Dated 2026-10-30. Written BEFORE any decode of keys R36I3a/b exists. Never rewritten; later notes go in `ADDENDUM-<date>.md`._
No pilot run, no tuning decode. Everything below comes from existing Round 34/35 feature files (derivation script reproduced in RESULTS.md; derived at freeze time with the same code).

## 1. Frozen margin tables (accept a decode iff `pmax - bar >= m`)
Rule: argmax register EN_NOVOWEL -> margin m_NV(L); argmax EN_HALFVOWEL -> margin m_HV(L); any other argmax -> margin 0 (over bar only). bar = 7.6342 (panelmax_bar exact, 1e6, 0.01), same engine/beam as Round 34/35 (keyskip exact, beam_w 400, supp 0.83; labels halluc rec<0.90, genuine rec>=0.95, gray excluded).
Derivation: per class, per L, the smallest margin m giving catch >= 0.90 (fraction of that class's hallucinations with margin < m), then rounded UP to 0.1; FR at that m checked on the same data's genuine decodes of that class (all <= 0.012, i.e. <= 0.10).

| L | m_NV | source | m_HV | source |
|---|---|---|---|---|
| 150 | **8.7**  (raw 8.612; 1355 halluc, 324 genuine NV-only, FR 0.012) | R35 feat, 2 keys | **5.3** (raw 5.22; 9 halluc, 134 genuine HV-only, FR 0.0) | R35 feat |
| 240 | **12.8** (raw 12.774; 1377 halluc, 144 genuine NV-only, FR 0.0) | R34 feat, 4 keys (L=240 exists) | **4.5** | **INTERPOLATED**: linear in L between 5.3@150 and 3.9@300 (4.46 -> 4.5). No genuine HV-only decodes exist at L=240 in any existing file; the 13 R34 NV-stream HV-argmax hallucinations (max margin 1.99) are all caught at 4.5 but FR at 240 is untested by existing data |
| 300 | **14.9** (raw 14.812; 1760 halluc, 101 genuine, FR 0.0) | R35 feat | **3.9** (raw 3.839; 9 halluc, 146 genuine HV-only, FR 0.0) | R35 feat |

Caveats stated in advance: m_HV rests on only 9 hallucinations at 150 and 300 (the raw values are the 9th-smallest-rank edge, so fragile); m_HV is non-monotone in L (5.3 then 3.9), taken as measured.

## 2. Keys (classes = sum(key bytes) mod 997)
Prior classes: CICADA 405, CICADA3301 604, CICADA-I4 575, CICADA-I4b 673, CICADA-I4c 674, CICADA-X1R33 771, CICADA-R34I3 759, CICADA-R35I3a 857, CICADA-R35I3b 858 (Round 32 I4 keys = CICADA, CICADA3301, CICADA-I4, -I4b, -I4c).
`CICADA-R36I3a` collides (858) with R35I3b and R36I3b is 859, so variants are used:
* **`CICADA-R36I3a-x`** class **26**
* **`CICADA-R36I3b-zzz`** class **273**
Classes differ from each other and from every prior key; also >= 130 classes away from every prior class, so the seed offsets (class*7) do not make rep ranges collide with R35's. (Caveat: the two keys' offsets differ by 1729 > 1100 draws, so no seed range overlap between them either.)

## 3. Samples (from Round 35 yields; no extension)
L in {150, 240, 300}. Per key per L: EN_NOVOWEL stream 1100 draws, EN_HALFVOWEL 100, LATIN/DE/OE/EN_KJV 60 each. Seeds: gen.py (NOVOWEL 100000, HALFVOWEL 400000, LATIN 300000, DE 310000, OE 320000, KJV 330000, each + class*7).
Expected genuine NV-only per L over both keys (R35/R34 yields 0.147/0.08/0.046 per draw): ~320 / ~176 / ~100; HV-only genuine (~0.6/draw over 200): ~120+ per L; all >= 30. H-NV hallucinations >1000/L. H-HV (hallucinations argmaxing HALFVOWEL) are rare (R34: 1-3/450 draws at 240; R35 pooled 9 at 150, 9 at 300): NOT sized to 30; reported as is; n=0 -> cell not passed.

## 4. Pass criteria (every L; Wilson 95 % score intervals)
1. catch(H-NV) >= 0.90 AND catch(H-HV) >= 0.90 (point; n=0 fails). H-NV: NV-stream, argmax NV, halluc. H-HV: NV- or HV-stream plants, argmax HALFVOWEL, halluc.
2. FR(pooled genuine: NV-only + HV-only + all genuine of LATIN/DE/OE/KJV streams) <= 0.10.
3. Wilson upper of FR(NV-only) <= 0.10 and of FR(HV-only) <= 0.10.
L passes iff 1-3. SEAL_PASS stays false regardless; if all L pass the lane only RECOMMENDS. not_covered: wrong-key overfits, non-exact relations, L other than 150/240/300, real pages, Welsh/CY, only two keys, 240 HV margin interpolated. No extensions, no re-tuning after results.
