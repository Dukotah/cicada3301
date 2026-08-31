# E-01 completion — the 7A35090F RSA-4096 moduli, fetched and checked

_2026-08-31. Resolves the coverage gap Round 16 left on RECON item **E-01**.
Reproduce: `python analysis/round16/zeroFP/e01_complete.py`._

## The gap

Round 16's zeroFP tested the pp49–51 payload as an RSA signature under the 2013 puzzle's
365-bit modulus (payload too large → SKIP) but recorded that the actual Cicada signing key
modulus was **"not on disk (fetch was planned but not done)"**, and argued informally that a
4096-bit modulus could not carry the 256-byte payload. E-01 was left `partially-run`; the
ledger's own open-item list (Round 16 SYNTHESIS item C) named "the 7A35090F RSA-4096 primary
+ subkey moduli … never been checked" as the completion.

## What was done

1. **Fetched the key.** `keyserver.ubuntu.com … op=get 0x6D854CD7933322A601C3286D181F01E57A35090F`.
2. **Verified provenance.** The v4 fingerprint computed from the key packet is
   `6D854CD7933322A601C3286D181F01E57A35090F` — byte-identical to the value recorded in
   `research/05-crypto-techniques.md`. uid `Cicada 3301 (845145127)`, created 2012-01-05.
   The script refuses to emit a verdict if the fingerprint does not match.
3. **Extracted both moduli** by parsing the OpenPGP packets directly (no external deps):
   primary [SC] RSA-4096 (e=65537) and encryption subkey [E] RSA-4096 (e=65537). Saved to
   `keys/moduli.json`.
4. **Validated the checker in both directions** (zero-false-positive discipline):
   - POSITIVE: a genuine PKCS#1 v1.5 SHA-256 signature made under a throwaway RSA-4096 key
     is recovered by the recogniser (`458 FF, DigestInfo SHA-256`) — zero false negative.
   - NEGATIVE: 64 random 256-byte blobs under the real modulus → **0** false positives.
5. **Ran the mechanical check.** Payloads `canon_256` and `canon_256_decpref`, both
   endiannesses, exponents {65537, 3}, both moduli. The 256-byte payload is 2048-bit, so
   `s < n` always holds under a 4096-bit modulus and `pow(s,e,n)` is well-defined and was
   actually computed — not assumed away.

## Result

**NEGATIVE.** 16 checks, 0 HIT, 0 SKIP. No PKCS#1 v1.5 signature block (`00 01 FF… 00`) and
no encryption block (`00 02 …`) appears under either 7A35090F modulus, either endianness, or
either exponent. The payload is not an RSA signature or RSA ciphertext under the Cicada
signing key.

Result JSON: `e01_complete_results.json`.

## Coverage / not covered

Covered: both 7A35090F RSA-4096 moduli × 2 payloads × 2 endians × e∈{65537,3}, with a
validated recogniser. **Not covered** (low prior, recorded honestly): a 2048-bit or other
Cicada key (none is published or held); OAEP/PSS encodings (structure-recognisable only with
the label/salt); the payload as a *fragment* of a 512-byte signature. E-01 moves from
`partially-run` to a **measured negative** over the published-key surface.
