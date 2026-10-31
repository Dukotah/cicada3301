# R40-B3 RESULTS: the English-era seed / key grids re-decoded under beam_v3 keyskip1+keyskip2 on panel-R36

_Run 2026-10-31. Instrument = R37-I2 imported unchanged (pf_v4_12 frozen screen, beam_v3 panel_max, panel-R36 12 registers, null12 POT bars). PREREG: `PREREG.md` + `PREREG-ADDENDUM-1.md`, dated before the first grid row. No `git` was run. No terminal verdicts are claimed: every line below is a bound on the regenerated list._

## 1. Per-grid table

| grid | keys regenerated / original | configs screened | N per relation | best pmax keyskip1 / keyskip2 | actual-N bar L120 (ks1/ks2) | flagged | near-miss |
|---|---|---:|---:|---|---|---:|---:|
| B04 | 2,165 seeds (504 core) / 2,165 (504) | 6998144 | 6041 | 6.336 / 6.049 | 7.244 / 7.173 | 0 | 0 |
| KDF | 534 secrets / 534 | 692064 | 591 | 5.150 / 6.528 | 6.399 / 6.342 | 1 | 0 |
| R17PAD | 28 pads (P3) / 28 | 15013222 | 9908 | 5.745 / 5.846 | 7.424 / 7.350 | 0 | 0 |
| COSPAD | 4 ISO pads / 6 (R12-A1) or 2 authoritative (R28-L1) | 20012680 | 16940 | 6.066 / 5.967 | 7.619 / 7.542 | 0 | 0 |

Planted-control recovery per register (recovered = screen pass + pmax120 and pmax240 >= N=1e6 bars + recovery >= 0.90; KDF rev plants are L=120 only):

| register | B04 | KDF | R17PAD | COSPAD | pooled | Wilson 95% lower |
|---|---|---|---|---|---|---|
| EN_MODERN | 20/20 | 20/20 | 20/20 | 20/20 | 80/80 | 0.954 |
| EN_NOVOWEL | 20/20 | 20/20 | 19/20 | 19/20 | 78/80 | 0.913 |
| LATIN | 20/20 | 20/20 | 19/20 | 19/20 | 78/80 | 0.913 |

## Flagged / near-miss

- **FLAGGED_FOR_ORACLE** (KDF): `KDF|03000000:iter_md5_1000:self:mod29:rev|v01|U|keyskip2` pmax120 6.528 (EN_MODERN) vs actual-N bar 6.342; clears N=1e6 bar: False; gate: unavailable (rev buffer 184); FLAGGED_FOR_ORACLE directly. Not certified; bundle `ORACLE-KDF-iter_md5_1000-rev/bundle.json`, notes `ORACLE-PENDING.md` (score falls with read length 6.528 -> 5.531, gibberish transliteration, single-cell exceedance P=0.6%, 8 cells run).
- Near-misses (cleared the actual-N L=120 bar but failed the gate or N=1e6): none other than the row above.
- Rows with pmax >= 6.0 (retained, `keep_*.json`): B04 2, KDF 1, R17PAD 0, COSPAD 2. Top rows per grid are listed in section 2; none is degenerate.

## 2. Grids

### B-04 seed dictionary (SHA/HMAC/RC4/AES/ChaCha expanders)

Keys regenerated: **2165 seeds / 504 core** (original 2,165 / 504); 16 generators x 5 reductions; configs screened **6998144** (planned 6998144: A 1385600, B 2064384, C 3548160). Original B-04 decodes: 6,224,300 (legacy beam).

Planted controls (natural rate, real route, 10 per register x relation):

| register | skip split | n | screen pass | pass | recover (>=0.90) |
|---|---|---:|---:|---:|---:|
| EN_MODERN | skip_free | 11 | 11 | 11 | 11 |
| EN_MODERN | with_skip | 9 | 9 | 9 | 9 |
| EN_NOVOWEL | skip_free | 13 | 13 | 13 | 13 |
| EN_NOVOWEL | with_skip | 7 | 7 | 7 | 7 |
| LATIN | skip_free | 11 | 11 | 11 | 11 |
| LATIN | with_skip | 9 | 9 | 9 | 9 |

Decoy columns screened with the plants: 122880, survivors 104 (rate 8.46e-04). Registers licensed by the >=3-per-cell gate: {'EN_MODERN': True, 'EN_NOVOWEL': True, 'LATIN': True}.

| relation | N decodes (survivors) | screened | best pmax (register) | bar L120 actual N | bar L120 N=1e6 | bar L120 N=screened | clears actual N | clears N=1e6 |
|---|---:|---:|---|---:|---:|---:|---|---|
| keyskip1 | 6041 | 6998144 | 6.336 (OE) | 7.244 | 9.102 | 9.809 | False | False |
| keyskip2 | 6041 | 6998144 | 6.049 (DE) | 7.173 | 8.999 | 9.695 | False | False |

Flagged-for-oracle: **0**. Near-miss (cleared actual-N L=120 but not the gate / N=1e6): **0**. Survivor rate (screen FPR) 8.63e-04; decode errors 0; elapsed 350s.
- top (keyskip1): 6.336 OE [B04|C:35716379656572626e696e61:chacha20:rej29:fwd:o0:onion|v00|pg16|keyskip1]
- top (keyskip2): 6.049 DE [B04|B:00000000000007de:aes_ctr_zeroiv:mod29:rev:o3:num_be|v00|U|keyskip2]
- screen survivor rate by group: A|bits5 8.1e-04, A|hi_nib 8.2e-04, A|lo_nib 8.9e-04, A|mod29 8.7e-04, A|rej29 8.6e-04, B|mod29 9.1e-04, B|rej29 8.3e-04, C|mod29 8.7e-04, C|rej29 8.6e-04
- store validation: validate_store=ok, check_r3_store=[]

### R16-KDF (PBKDF2/scrypt/iterated/EVP, 534 secrets)

Keys regenerated: **534 secrets** (original 534) x 27 KDFs x 3 salts x 2 reductions x 8 variants = **692064** configs screened (original 692,064 legacy decodes).

Planted controls (natural rate, real route, 10 per register x relation):

| register | skip split | n | screen pass | pass | recover (>=0.90) |
|---|---|---:|---:|---:|---:|
| EN_MODERN | skip_free | 14 | 14 | 14 | 14 |
| EN_MODERN | with_skip | 6 | 6 | 6 | 6 |
| EN_NOVOWEL | skip_free | 11 | 11 | 11 | 11 |
| EN_NOVOWEL | with_skip | 9 | 9 | 9 | 9 |
| LATIN | skip_free | 10 | 10 | 10 | 10 |
| LATIN | with_skip | 10 | 10 | 10 | 10 |

Decoy columns screened with the plants: 30720, survivors 23 (rate 7.49e-04). Registers licensed by the >=3-per-cell gate: {'EN_MODERN': True, 'EN_NOVOWEL': True, 'LATIN': True}.

| relation | N decodes (survivors) | screened | best pmax (register) | bar L120 actual N | bar L120 N=1e6 | bar L120 N=screened | clears actual N | clears N=1e6 |
|---|---:|---:|---|---:|---:|---:|---|---|
| keyskip1 | 591 | 692064 | 5.150 (GREEK) | 6.399 | 9.102 | 8.968 | False | False |
| keyskip2 | 591 | 692064 | 6.528 (EN_MODERN) | 6.342 | 8.999 | 8.868 | True | False |

Flagged-for-oracle: **1**. Near-miss (cleared actual-N L=120 but not the gate / N=1e6): **0**. Survivor rate (screen FPR) 8.54e-04; decode errors 0; elapsed 1252s.
- top (keyskip1): 
- top (keyskip2): 6.528 EN_MODERN [KDF|03000000:iter_md5_1000:self:mod29:rev|v01|U|keyskip2]
- screen survivor rate by group: KDF|mod29 8.8e-04, KDF|rej29 8.3e-04
- store validation: validate_store=ok, check_r3_store=[]

### R17 public pads (P3: RAND digits + 3301's published bytes)

Pads regenerated: P3 list **28 of 28** (sha256 match 25, mismatch 3, missing 0); builders mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled, nibbles, hexchars; configs screened **15013222**, planned columns 7506611. P1 (Bitcoin) and P2 (beacon + random.org) are NOT regenerated. Offset coverage: 7506611 of 1577174689 (builder x direction) offset-columns = 0.4760% of the dense offset space of these cells.

Planted controls (natural rate, real route, 10 per register x relation):

| register | skip split | n | screen pass | pass | recover (>=0.90) |
|---|---|---:|---:|---:|---:|
| EN_MODERN | skip_free | 9 | 9 | 9 | 9 |
| EN_MODERN | with_skip | 11 | 11 | 11 | 11 |
| EN_NOVOWEL | skip_free | 11 | 11 | 11 | 11 |
| EN_NOVOWEL | with_skip | 9 | 8 | 8 | 8 |
| LATIN | skip_free | 15 | 14 | 14 | 14 |
| LATIN | with_skip | 5 | 5 | 5 | 5 |

Decoy columns screened with the plants: 30720, survivors 33 (rate 1.07e-03). Registers licensed by the >=3-per-cell gate: {'EN_MODERN': True, 'EN_NOVOWEL': True, 'LATIN': True}.

| relation | N decodes (survivors) | screened | best pmax (register) | bar L120 actual N | bar L120 N=1e6 | bar L120 N=screened | clears actual N | clears N=1e6 |
|---|---:|---:|---|---:|---:|---:|---|---|
| keyskip1 | 9908 | 15013222 | 5.745 (EN_MODERN) | 7.424 | 9.102 | 10.086 | False | False |
| keyskip2 | 9908 | 15013222 | 5.846 (LP1_REAL) | 7.350 | 8.999 | 9.968 | False | False |

Flagged-for-oracle: **0**. Near-miss (cleared actual-N L=120 but not the gate / N=1e6): **0**. Survivor rate (screen FPR) 6.60e-04; decode errors 0; elapsed 562s.
- top (keyskip1): 
- top (keyskip2): 
- screen survivor rate by group: R17PAD|canon_256|byte_scaled 0.0e+00, R17PAD|canon_256|hi_nibble 0.0e+00, R17PAD|canon_256|lo_nibble 4.5e-03, R17PAD|canon_256|mod29 0.0e+00, R17PAD|canon_256|nibbles 2.4e-03, R17PAD|canon_256|prime_to_idx 0.0e+00, R17PAD|cicada_all_pub|byte_scaled 9.8e-04, R17PAD|cicada_all_pub|hi_nibble 8.2e-04, R17PAD|cicada_all_pub|lo_nibble 7.6e-04, R17PAD|cicada_all_pub|mod29 9.1e-04, R17PAD|cicada_all_pub|nibbles 8.0e-04, R17PAD|cicada_all_pub|prime_to_idx 8.3e-04
- store validation: validate_store=ok, check_r3_store=[]

### CicadaOS pads (R12-A1 / R28-L1)

Pads regenerated from the ISO: 560.00auth (3992970 B, receipt True), 560.13 (118818811 B, receipt True), 560.17 (1183811 B, receipt None), 761.mp3 (4010732 B, receipt None); builders mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled; configs screened **20012680**, planned columns 10006340. Offset coverage: 10006340 of 1280055240 (builder x direction) offset-columns = 0.7817% of the dense offset space of these cells.

Planted controls (natural rate, real route, 10 per register x relation):

| register | skip split | n | screen pass | pass | recover (>=0.90) |
|---|---|---:|---:|---:|---:|
| EN_MODERN | skip_free | 11 | 11 | 11 | 11 |
| EN_MODERN | with_skip | 9 | 9 | 9 | 9 |
| EN_NOVOWEL | skip_free | 10 | 10 | 10 | 10 |
| EN_NOVOWEL | with_skip | 10 | 9 | 9 | 9 |
| LATIN | skip_free | 11 | 11 | 11 | 11 |
| LATIN | with_skip | 9 | 8 | 8 | 8 |

Decoy columns screened with the plants: 30720, survivors 25 (rate 8.14e-04). Registers licensed by the >=3-per-cell gate: {'EN_MODERN': True, 'EN_NOVOWEL': True, 'LATIN': True}.

| relation | N decodes (survivors) | screened | best pmax (register) | bar L120 actual N | bar L120 N=1e6 | bar L120 N=screened | clears actual N | clears N=1e6 |
|---|---:|---:|---|---:|---:|---:|---|---|
| keyskip1 | 16940 | 20012680 | 6.066 (DE) | 7.619 | 9.102 | 10.191 | False | False |
| keyskip2 | 16940 | 20012680 | 5.967 (EN_NOVOWEL) | 7.542 | 8.999 | 10.070 | False | False |

Flagged-for-oracle: **0**. Near-miss (cleared actual-N L=120 but not the gate / N=1e6): **0**. Survivor rate (screen FPR) 8.46e-04; decode errors 0; elapsed 622s.
- top (keyskip1): 6.066 DE [COSPAD|560.17:lo_nibble:fwd:o222234|v00|U|keyskip1]; 6.046 EN_KJV [COSPAD|761.mp3:prime_to_idx:fwd:o2274517|v00|U|keyskip1]
- top (keyskip2): 
- screen survivor rate by group: COSPAD|560.00auth|byte_scaled 8.8e-04, COSPAD|560.00auth|hi_nibble 8.8e-04, COSPAD|560.00auth|lo_nibble 8.6e-04, COSPAD|560.00auth|mod29 8.5e-04, COSPAD|560.00auth|prime_to_idx 8.3e-04, COSPAD|560.13|byte_scaled 8.6e-04, COSPAD|560.13|hi_nibble 8.8e-04, COSPAD|560.13|lo_nibble 9.1e-04, COSPAD|560.13|mod29 8.0e-04, COSPAD|560.13|prime_to_idx 8.4e-04, COSPAD|560.17|byte_scaled 7.8e-04, COSPAD|560.17|hi_nibble 8.9e-04
- store validation: validate_store=ok, check_r3_store=[]

### Supplementary B-04 control (Z16 / bit-group reductions)

Plants restricted to hi_nib, lo_nib, bits5 (stage A, offset 0), EN_MODERN + EN_NOVOWEL, 10 per register x relation:

| register | skip split | n | screen pass | pass | recover (>=0.90) |
|---|---|---:|---:|---:|---:|
| EN_MODERN | skip_free | 14 | 14 | 14 | 14 |
| EN_MODERN | with_skip | 6 | 6 | 6 | 6 |
| EN_NOVOWEL | skip_free | 10 | 10 | 10 | 10 |
| EN_NOVOWEL | with_skip | 10 | 10 | 10 | 10 |

Decoy columns screened with the plants: 40960, survivors 35 (rate 8.54e-04). Registers licensed by the >=3-per-cell gate: {'EN_MODERN': True, 'EN_NOVOWEL': True}.

## 3. What could not be regenerated

- **R12-A1 truncated `_560.00`** (2,412,544 B), `folly`/`wisdom` (3,368 B) and `prime_echo` (12,248 B): sources were the cicada-solvers mirror and local OSINT artifacts not on this disk. The 3,992,970 B ISO `DATA/_560.00` (the R28-L1 authoritative pad) IS regenerated.
- **R17-P1 Bitcoin heights 0-303,726 and R17-P2 NIST beacon v1 + random.org 153 files**: multi-GB network fetches; not regenerated; their (English-only) negatives keep all three conditionals.
- **R17 and R12/R28 dense offset spaces**: only the stated sampled fractions below were re-decoded (not a dense re-sweep). R17 scored 1.45e10 offsets; this lane screened a sampled subset.
- **B-04 Stage D** (survivor escalation) is superseded by the L=240 gate; B-05 payload-as-seed and B-02 offset scans were not in this lane's list.
- **KDF**: Stage B salt expansion was never run in the original and is not run here; rev-direction L=240 gate is unavailable (184-symbol buffer).

## 4. Conditionals now carried (doctrine Q4)

1. **Key space**: exactly the regenerated lists above (counts), with pad grids at the stated sampled fractions.
2. **Transition model**: `keyskip1` + `keyskip2`, heads with <= 2 skips in 24 runes (pf_v4_12); `skip_by_4`, `skip_by_5`, reset-per-page/line, `free`, combined axes unrepresented. This REPLACES the legacy keyskip1-only conditional (legacy beam recovered 0.258 of a `skip_by_two` plant).
3. **Register**: panel-R36, 12 registers (reach per register = screen power 0.952-0.994 x v3 recovery); planted controls here cover **EN_MODERN, EN_NOVOWEL, LATIN** only: `[plants: EN_MODERN / EN_NOVOWEL / LATIN]`; the other nine registers are assumed from the R37-I2 screen-power table and the pooled v3 recovery.
4. The screen thresholds were calibrated on bash heads (uniform Z29); the realised survivor rates on these hash/KDF/pad key heads (table above) are the empirical check that the screen FPR transfers.

## 5. Files

`PREREG.md`, `PREREG-ADDENDUM-1.md`, `engine.py`, `grids.py`, `pads.py`, `b3.py`, `b3pads.py`, `b3extra.py`, `finalize.py`, `mk_results.py`, `control_*.json`, `final_*.json`, `summary_*.json`, `keep_*.json`, `rows_*.jsonl` (SWEEPROW, 14 fields, append-mode), `counts*.json`, `p3_regen_compare.json`, `cos_pads_regen.json`, `ledger.json`, `ledger_patches.json`.
