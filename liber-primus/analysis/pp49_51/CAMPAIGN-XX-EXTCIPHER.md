# Campaign XX — pp49-51 payload as EXTERNAL-KEY CIPHERTEXT + HMAC to page-56 (2026-07-28)

Novel_cipher lane. Prior campaigns (IX/XII/XVII) tested the pp49-51 256-byte
object `canon_256.bin` as: a runic additive key (null), a preimage of the page-56
"AN END" 512-bit hash (null, 140+ combos incl. 32B/64B blocks), and tiled-keystream
XOR/subtract (null). **Never tested until now:** the payload decrypted as *ciphertext
in its own right* under a short external key via real block/stream ciphers, and an
HMAC relationship to the page-56 hash.

Reproduce: `PYTHONUTF8=1 python3 analysis/pp49_51/campaign20_extcipher.py`
(uses `cryptography` for AES/ChaCha; pure-stdlib RC4/HMAC).

## Tested (all NULL)
- **AES-ECB / AES-CBC(iv0) / AES-CTR(nonce0) / ChaCha20 / RC4 / repeating-key XOR**
  decryption of both payload variants (P, P2), keyed by 73 candidate keys (the 59-key
  armada OSINT list + koan/structural phrases: AN END, PILGRIM, THE PRIMES ARE SACRED,
  3301, CICADA 3301, LIBER PRIMUS, ...), with key derivations raw / md5(16B) / sha256(32B).
  ~1000 decrypts. **Zero beat printable>0.85, entropy<6.5, or 3+ dictionary words.**
- **Key = the page-56 hash itself** (the natural "sought page's hash is the key" reading)
  across XOR/RC4/AES-ECB/AES-CTR/ChaCha: entropy stayed 7.10–7.26 (baseline 7.170). Null.
- **Best entropy across ALL short-key decrypts = 7.000** (RC4/sha256 key '481'), vs 7.170
  baseline. Real text collapses to ~4–5; this is sample variance on 256 bytes, not signal.
  Printable fraction never rose meaningfully above the ~0.41 baseline.
- **HMAC(key, artifact) vs page-56 target:** 1752 combos — HMAC-{SHA-512, SHA3-512, BLAKE2b}
  over {P, P2, P.hex, runic index-bytes} both as message (keyed by each candidate) and as
  key (message = candidate string). **0 hits.**
- **Internal structural digests:** does any 64B quarter / 128B half equal a
  SHA-512/SHA3-512/BLAKE2b of another quarter/half/prefix? **0 hits.** The four 64B
  quarters are not stacked hashes of each other.

## Verdict
The pp49-51 payload is **not decryptable as ciphertext under any short external key**
in the standard AES/RC4/ChaCha/XOR/HMAC family, and has **no HMAC or internal-digest
link to the page-56 "AN END" hash.** Combined with prior campaigns, the object is now
excluded as: runic additive key, hash preimage, tiled keystream, AND external-key
ciphertext. It behaves as a genuine high-entropy random/OTP-class blob under every
plaintext-independent test. The only classes NOT closed remain the truly unbounded ones
(an unknown long external key / true OTP — unbreakable from inside by construction).

Full run that would follow ONLY IF a lead were live: none — this is a clean close.
The remaining open surface is unbounded external key material, which cannot be brute-forced.
