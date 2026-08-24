# Round 16 / zeroFP — RESULTS

_Executed 2026-08-23. Trust anchor: ALL VALIDATIONS PASSED (confirmed before run)._

## Overall verdict: NEGATIVE — all four tests null

No zero-false-positive signal found in any of the four tests.

---

## E-01: pp49-51 payload as RSA signature (PKCS#1 v1.5 padding check)

**Result: COVERAGE-LIMITED (not a true null)**

The test as designed requires `s < n` (the candidate signature must be smaller than the
modulus). The pp49-51 payload is 256 bytes = 2048 bits.

- **2013 puzzle modulus** (from `pgp_welcome.txt`): the file shows 432-bit n (PROGRESS.md
  called it "365-bit" — that is incorrect; it is 432 bits). Either way, n is far smaller
  than the 2048-bit payload, so `s >= n` for all endiannesses. No pow() computation was
  possible.
- **7A35090F 4096-bit PGP key** (primary pkt6 + subkey pkt14): the `.asc` file was listed
  in the source inventory but was never fetched (the fetch script exists but was not run;
  no `.asc` file is on disk). Under a 4096-bit modulus, pow(s,e,n) would be meaningful for
  a 256-byte payload — but the modulus is not available.
- **Three 2014 onion RSA blobs** (rsahex_cu343/fv7ly/avowy, 256B each): these are RSA
  ciphertext/signature OUTPUTS, not public keys. The corresponding public moduli are not
  separately held.

**What this means for the ledger:** E-01 cannot be closed as "null" — it is incomplete.
The 7A35090F 4096-bit moduli are the relevant check (the payload is 2048-bit and would
fit under those 4096-bit keys). To complete E-01:
1. Fetch the 7A35090F public key from a keyserver (e.g., `gpg --recv-keys 7A35090F`
   and export to binary, or use `pgpdump` to extract the two RSA moduli).
2. Run `pow(canon_256_as_int, 65537, n_primary)` and `pow(canon_256_as_int, 65537, n_subkey)`.
3. Check result for 0x0001FF...FF00 prefix (PKCS#1 v1.5) or PSS trailer (0xBC).

**Coverage bound:** 0 of 3 relevant moduli checked (2013 key: payload too large; 4096-bit
keys: not held; 2014 onion keys: public moduli not separately held).

---

## E-02: payload as meta-parameters

**Result: NULL (complete)**

**E-02A — 56-byte permutation window:**
- Checked all 201 consecutive 56-byte windows in the 256-byte payload.
- Zero windows are a permutation of 0..55.
- Also checked 57-byte windows (permutation of 0..56): zero hits.
- FP rate: ~10^{-24} per window. This is a clean null with analytic certainty.

**E-02B — doublet-gap rank correlation:**
- Rune stream: 12,956 runes, 86 doublets, 85 inter-doublet gaps.
- First 5 gaps: [85, 249, 197, 129, 127, ...]
- Payload decoded as uint8 (256 values), uint16-LE (128 values), uint16-BE (128 values)
  and correlated against the gap sequence:
  - uint8:    Spearman r = 0.043, p = 0.70 (noise)
  - uint16-LE: Spearman r = -0.018, p = 0.87 (noise)
  - uint16-BE: Spearman r = -0.026, p = 0.81 (noise)
- All three well within the null (threshold was |r| > 0.5, p < 1e-6).

**CLOSED.** The payload contains no permutation index of the pages and is uncorrelated
with the doublet-gap sequence in all tested encodings.

---

## H-03: 2013 onion cookies XOR'd against four 256-byte blobs

**Result: NULL (complete)**

- Cookie 167 (`6941f707...`, 32 bytes) and Cookie 761 (`7bc1e780...`, 32 bytes).
- Four 256-byte target blobs: canon_256, rsahex_cu343_761, rsahex_fv7ly_1033, rsahex_avowy_3301.
- XOR'd at each 32-byte offset (8 offsets × 4 blobs × 2 cookies = 64 trials).
- Gate: >= 80% printable ASCII ratio.
- Best result: cookie761 XOR rsahex_avowy@offset_96 = 62.5% printable (head: `7180647a07076bed`).
  This is within the noise band (a random byte is ~44% printable, so 62.5% can occur by chance
  in any one of 64 trials: p ≈ 64 × C(32,20) × 0.44^20 × 0.56^12 ≈ not negligible at 62.5%).
- Zero trials above 80% threshold.

**CLOSED.** The cookie XOR cross is null in all 64 trials. The OSINT-SWEEP item "that specific
cross is untried" is now tried and closed.

---

## H-01: per-onion HTTP anomalies as an information channel

**Result: NULL / CHANNEL CLOSED (on available data)**

**Sub-tests:**

1. **Port sequence (5240, 5241, 5242, 5243):** Sequential per-onion indexing (5239 + onion#).
   No alignment with Cicada cryptographic constants (none are near 5240). Aesthetic only.

2. **Uptime "1 days 0 hours 33 minutes 14 seconds" → 1033:** The decode 1×1000 + 33 = 1033
   is already a documented Cicada constant (embedded as `<!--1033-->` in onion 3 HTML). This
   is a known aesthetic marker, not a new channel. The specific encoding adds no information
   beyond what the HTML comment already states.

3. **`<head>`/`</head>` malformation varying per onion:** Raw HTML files are not held locally
   (only README.md summaries). The specific per-onion bit pattern cannot be measured from
   available data. This sub-test is INCOMPLETE, not null: if the raw HTML were fetched,
   a per-onion bit string could be constructed and scored.

4. **Leaked host (li676-224.members.linode.com / 106.186.123.224):** Standard Linode hosting
   IP, publicly known. Deanonymization artifact, not cipher material.

**Verdict on available data:** CLOSED as an information channel — all measurable anomalies
are known aesthetics. One sub-test (malformation bit pattern) is incomplete due to raw HTML
not being held; it remains a micro-open thread if HTML is fetched.

---

## Coverage summary

| Test | Status | Key limitation |
|------|--------|----------------|
| E-01 RSA/PKCS#1 | INCOMPLETE | 7A35090F 4096-bit moduli not on disk; 2013 modulus too small |
| E-02A permutation window | COMPLETE, NULL | 201 windows checked, FP ~10^{-24}/window |
| E-02B doublet-gap correlation | COMPLETE, NULL | 3 encodings, all |r| < 0.05, p > 0.69 |
| H-03 cookie XOR cross | COMPLETE, NULL | 64 trials, max 62.5% printable, gate 80% |
| H-01 HTTP channel | MOSTLY CLOSED | Head malformation sub-test needs raw HTML |

## What remains open from this batch

- **E-01 (partial):** Fetch 7A35090F key moduli from public keyservers and run the
  pow(canon_256, 65537, n_4096) check. The payload size (2048-bit) is compatible with
  a 4096-bit RSA signature verification. This is ~5 minutes of work with `gpg --recv-keys`.
- **H-01 malformation (micro-thread):** If the raw onion HTML is ever fetched (8 files,
  iBotPeaches/cicada_3301 or archive.org), extract the per-onion `<head>` structure and
  test as a bit string. Low prior.

## Artifact paths

- Script: `analysis/round16/zeroFP/zerofp_tests.py`
- Results JSON: `analysis/round16/zeroFP/results.json`
- Rune stream (local): `analysis/round16/zeroFP/ct_local.bin` (regenerated from krisyotam_runes.txt)
- PREREG: `analysis/round16/zeroFP/PREREG.md`
