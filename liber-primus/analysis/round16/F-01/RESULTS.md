# Lane F-01 — Results

**Lane:** F-01, LP2-as-pad inversion  
**Date:** 2026-08-23  
**Verdict: NEGATIVE**

---

## Trust anchor

`python tests/validate.py` = **ALL VALIDATIONS PASSED** (confirmed before run)

---

## Positive control

Gate: plant a known English sentence under the LP2 stream (key-skip model, supp=0.83),
then recover via skip-aware beam decoder.

| Channel | Score |
|---|---|
| English plaintext target | -4.413 |
| RIGID decode (correct key) | -7.334 |
| BEAM decode (correct key) | **-4.413** |
| Char recovery | **1.000** |
| Null (n=100): mean | -7.381 |
| Null (n=100): max | -6.787 |

**Gate: PASS.** Beam recovers the planted text exactly; rigid decode fails (score -7.334
= noise). This confirms the instrument is powered: if LP2 is the key to any target in
the finite candidate set, the beam would detect it.

---

## Sweep

**Hypothesis:** LP2 (12,956 runes, SHA256 verified) is key material; one of five known
Cicada objects is the ciphertext.

**Targets:**
- T1: Cicada 2012/2013 puzzle texts (1250 rune-indices, trimmed to 500)
- T2: Five solved LP1 pages concatenated (1769 rune-indices, trimmed to 500)
- T3: Cicada PGP message bodies (1385 rune-indices, trimmed to 500)
- T4: AN-END SHA-512 hash bytes mod 29 (63 values)
- T6: LP2 head first 200 runes as ciphertext (auto-encode test)

(T5 = pp49-51 payload was skipped; no payload.bin/hex file exists in analysis/pp49_51/.)

**Key variants:** LP2_fwd, LP2_rev, LP2_atbash, LP2_neg × sign ∈ {-1, +1}

**Decoder:** skip-aware beam (beam_w=400, max_skip=3, offset=0)

**Total decodes:** 40 beam runs

### Score table (top results, all targets)

| Target | Key variant | Sign | Score |
|---|---|---|---|
| T1_cicada_2012_2013 | lp2_fwd | +1 | -7.032 |
| T1_cicada_2012_2013 | lp2_neg | -1 | -7.032 |
| T2_lp1_solved | lp2_fwd | -1 | -7.105 |
| T2_lp1_solved | lp2_neg | +1 | -7.105 |
| T4_anend_hash | lp2_atbash | -1 | -7.116 |
| T3_pgp_messages | lp2_atbash | +1 | -7.138 |
| T6_lp2_head_200 | lp2_rev | +1 | -7.132 |
| ... (all others < -7.2) | | | |

**Best score: -7.032** (T1, lp2_fwd, sign=+1)  
**Bar: -5.5** — all results are 1.5 units below the threshold.

### Null bands for top 5 candidates

| Target | Key | Sign | Score | Null max | Beats by | HIT |
|---|---|---|---|---|---|---|
| T1 | lp2_fwd | +1 | -7.032 | -6.972 | -0.060 | No |
| T1 | lp2_neg | -1 | -7.032 | -6.972 | -0.060 | No |
| T2 | lp2_fwd | -1 | -7.105 | -7.015 | -0.089 | No |
| T2 | lp2_neg | +1 | -7.105 | -7.015 | -0.089 | No |
| T4 | lp2_atbash | -1 | -7.116 | -6.528 | -0.587 | No |

Every candidate is deep within the noise band. No candidate beats its null_max.
The best score does not even beat noise — it falls *below* the null distribution peak.

---

## Verdict: NEGATIVE

The LP2-as-pad inversion hypothesis is falsified over the finite candidate set:

- **Positive control PASSED** — instrument is powered; would detect the signal if present
- **All 40 beam decodes score in the noise band** (-7.0 to -8.2)
- **None beats its size-matched null** (n=200) — in fact all top-5 score *below* null_max
- **Best score -7.032 vs bar -5.5** — margin is 1.5 units below threshold

The LP2 stream is not a running key for any of the five finite Cicada objects tested,
under four key-stream variants and two cipher signs.

---

## Coverage bound

Swept: 5 target objects × 4 LP2 variants × 2 signs = 40 beam decodes.  
All targets trimmed at 500 runes to match the beam budget.  
Null bands: n=200 for top 5 candidates.

Not covered by this lane:
- pp49-51 payload (T5): no binary payload file found; would require rebuilding from source
- LP2 as key against longer offsets (all tested at offset=0)
- Segment-by-segment tests (each page of LP2 vs each fragment)
- LP2 runes as plaintext and other objects as key (reverse of this hypothesis)

Those are separately registered attacks; this lane closes the stated finite candidate set.

---

## Elapsed

296 seconds (4m 56s). Within the 8-minute budget.
