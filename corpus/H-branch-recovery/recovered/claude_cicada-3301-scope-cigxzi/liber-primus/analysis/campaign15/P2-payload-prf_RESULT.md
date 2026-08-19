# Probe P2 — pp49–51 payload as a PRF / stream-cipher SEED

- **probe_id:** P2-payload-prf
- **verdict:** null-closed
- **headline_number:** best decrypt score_norm = **−7.44** (gate −5.2); best decrypt IoC·N = **1.002** (gate 1.3) — over **480 configs**
- **falsifiable_signal:** a payload-seeded keystream decrypt whose translit scores `score_norm > -5.2` OR whose `IoC·N > 1.3`
- **signal_fired:** **false**
- **synthetic_validation:** PASS — planted an RC4(payload)-byte-mod29 keystream over real English (plaintext −4.176, IoC·N 1.756). Encrypted ciphertext collapsed to −7.50 / IoC·N 0.999; correct-seed recovery reproduced the plaintext exactly (−4.176 / 1.756); a wrong seed stayed in noise (−7.54). The pipeline provably distinguishes a true hit (≈+3.3 score gap, IoC·N 1.76 vs 1.00) from noise.
- **method:** The 256-byte pp49–51 payload was never used directly (that is Campaign VII/IX/XI/XII's null). Instead it was EXPANDED into a full-length mod-29 keystream via 10 PRF/stream-cipher generators — RC4, AES-128-CTR, AES-256-CTR, and SHA-256/SHA-1/MD5 each in counter and chain mode, plus HMAC-DRBG(SHA-256). Each raw byte stream was reduced to mod-29 three ways (byte mod 29; unbiased rejection ≥232 then mod 29; 16-bit big-endian word mod 29). Each keystream decrypted all 55 unsolved runic pages under: subtract & add; per-page & continuous; payload forward & reversed; ciphertext with & without Atbash — 10×2×3×2×2×2 = **480 configs**, every one scored (quadgram score_norm on translit + IoC·N). The ~83% soft-skip filter inversion was not composed: it is non-invertible without per-position skip data, and the gate is measured on the raw additive decrypt regardless.
- **script_path:** `analysis/campaign15/P2-payload-prf.py`
- **reproduce_cmd:** `python analysis/campaign15/P2-payload-prf.py` (needs `cryptography`; if its rust backend errors, `pip install --quiet cffi` first)
- **one_paragraph:** The unexamined idea was that the high-entropy 2048-bit payload is not a key but a *seed* — the SEED of a stream cipher or PRF whose expanded keystream is the real one-time-pad over LP2. I built and validated a pipeline that expands the payload through ten standard constructions (RC4, AES-CTR at both key sizes, three hashes in counter and chain mode, HMAC-DRBG), reduces each to mod-29 three unbiased ways, and decrypts all 55 pages under every sign/orientation/page-mode/Atbash combination (480 configs). A synthetic plant confirms the rig recovers a genuine payload-seeded keystream over English (−4.18 vs −7.5 noise floor, IoC·N 1.76 vs 1.00) and rejects wrong seeds — so a real hit could not hide. Nothing fired: the best of 480 real decrypts scored −7.44 (English band ≈ −4.2, break threshold −5.2) and the best IoC·N was 1.002 (flat-random floor; gate 1.3). Expanding the payload as a PRF/stream-cipher seed is dead.
- **ledger_row:**

```
| Payload as **PRF / stream-cipher seed** (RC4, AES-CTR, SHA-256/SHA-1/MD5 ctr+chain, HMAC-DRBG; expanded to mod-29 keystream, not used directly) | ❌ dead | 480 configs (3 reductions × sign × per-page/cont × fwd/rev × ±Atbash); best score −7.44 (gate −5.2), best IoC·N 1.002 (gate 1.3); synthetic RC4-seed plant recovered (−4.18/1.76 vs noise −7.5/1.00) proving detection power | Campaign XV `analysis/campaign15/P2-payload-prf.py` |
```
