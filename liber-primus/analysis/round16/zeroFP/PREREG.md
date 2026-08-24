# Round 16 / zeroFP — Pre-Registration

_Written before running any of the four tests. 2026-08-23._

## Lane identity
Round 16, Wave 1 (light/parallel): the four "zero false positive" micro-tests that are
analytic decisions, not sampling decisions.  These are the four items from the RECON-A
register (E-01, E-02, H-03, H-01) that were flagged "never-run" or "untried specific cross"
and rated minutes-of-compute apiece.

## Positive control (shared)
`python tests/validate.py` must print ALL VALIDATIONS PASSED before any result is trusted.

---

## E-01 — pp49-51 payload as RSA signature under known Cicada moduli

**Hypothesis:** The 256-byte canon_256.bin (and canon_256_decpref.bin) is a valid RSA
signature or ciphertext under one of the known Cicada public-key moduli, recoverable via
`pow(s, e, n)` with e=65537.

**Candidate moduli:**
- 2013 puzzle modulus (~365-bit): n from pgp_welcome.txt line 13
  `n = 75579125746085351644267182920580212556413102071876330957950694457000592
      10248050757270234679993673844203148013173091173786572116639`
- 2014 puzzle moduli: The three 256-byte RSA blobs in rsahex_{cu343_761, fv7ly_1033,
  avowy_3301}.bin are MESSAGE ciphertext/signatures, not public keys. The public key used
  to produce those is the same 2013/2012 puzzle key or the 7A35090F key.
- 7A35090F PGP key (4096-bit): Two RSA moduli (primary + subkey). Source file
  `round10/L6-archives/fetched/jaxonkuipers/comms/cicada-3301-public-key.asc` was listed
  but not fetched; we will extract from the public keyserver directly in the script.

**Pass/fail bar:** `pow(s, e, n)` result begins with 0x0001FF...FF00 (PKCS#1 v1.5 signature
padding) OR begins with 0x00 followed by a known digest OID
(SHA-256/SHA-512/SHA-1 DigestInfo) — probability of random occurrence is ~2^{-8 * (modlen-2)}
per check, which is essentially zero for any key >= 128 bits.

**FP rate per modulus-endianness trial:** < 2^{-100}. This is a hard structural check, not
a threshold score.

---

## E-02 — pp49-51 payload as meta-parameters: permutation-window and doublet-gap correlation

**Hypothesis A (permutation window):** A 56-byte sliding window over the 256-byte payload
is a permutation of 0..55 (in some encoding), intended as a page-order or page-offset table.

**Hypothesis B (doublet-gap table):** Reading the payload as 8-bit or 16-bit (LE/BE) unsigned
integers produces a sequence that is rank-correlated with the actual doublet-gap sequence
[actual gaps between the 86 doublet positions in the 12,956-rune stream].

**Pass/fail bars:**
- A: Any 56-byte window that is a permutation of 0..55. FP rate by chance: 56!/(256^56) ~
  10^{-24} per window. This is ZERO-FP: a hit is unambiguous.
- B: Spearman |r| > 0.5 AND p < 1e-6 under permutation test. A random 85-gap sequence
  at this length has p(|r|>0.5) < 1e-5, so threshold is conservative.

---

## H-03 — 2013 onion cookies XOR'd against the four 256-byte hex strings

**Hypothesis:** The two 32-byte onion cookies (cookie167 = 6941f707..., cookie761 = 7bc1e780...)
XOR'd with (or used as a key to) any of the four 256-byte binary objects produces structure:
ASCII text, a known Cicada plaintext, or recognizable RSA/PGP/hash structure.

**The four target objects:**
1. canon_256.bin (the pp49-51 payload)
2. rsahex_cu343_761.bin (2014 onion 2 RSA hex, 256 B)
3. rsahex_fv7ly_1033.bin (2014 onion 3 RSA hex, 256 B)
4. rsahex_avowy_3301.bin (2014 onion 4 RSA hex, 256 B)

**Method:** XOR each 32-byte cookie against each 256-byte blob at all offsets (0, 32, 64...224),
both raw and hex-decoded forms of the cookie. Test output for: printable ASCII ratio, known
digests (SHA-256/SHA-512 of known Cicada strings), null bytes indicating PKCS padding,
entropy (a valid structure would stand out from the ~8 b/B background).

**Pass/fail bar:** Output with >= 80% printable ASCII, OR matching a known 3301 hash/string,
OR showing PKCS1 padding structure (first bytes 00 01 FF...FF 00) — all of these are
zero-FP signals. Expected: null (entropy 7.x b/B throughout, no structure). This specific
cross is confirmed never-run in the OSINT-SWEEP-2026-07-27.md.

**FP rate:** For the printable-ASCII gate: P(random byte is printable) ~ 0.44 per byte, so
P(>= 0.8 of 32 bytes printable) ~ 10^{-8} per trial. Number of trials: 2 cookies x 4 targets
x 8 offsets x 2 forms = 128 trials. Bonferroni: still ~10^{-6}. Zero-FP in practice.

---

## H-01 — Per-onion HTTP anomalies as a channel

**Hypothesis:** The per-onion HTTP header quirks (port numbers 5240/5241/5242/5243, the
uptime "1 days 0 hours 33 minutes 14 seconds" -> 1033, the leaked host, `<head>`/`</head>`
malformation varying per onion) encode information beyond authentication — specifically, the
port numbers may encode an integer sequence or cipher parameters, and the structural
malformations may embed a bit-string.

**Test:** Read the README/inventory for each of the 12 onion pages, extract the port numbers
and uptime values, decode and test:
1. Port numbers as a sequence vs known Cicada constants (167, 761, 1033, 3301)
2. Uptime value -> 1033 (a known Cicada constant) as the only confirmed anomaly
3. Head/body malformation as a potential bit string (per-onion binary channel)
4. Whether the anomalies together spell out a message or key (e.g., interpreted as a
   runic shift, a seed, or an XOR constant)

**Pass/fail bar:** The uptime->1033 link is already documented. A genuine channel requires
either: (a) a decoded message above the -5.2 quadgram score, OR (b) a numerical sequence
that matches a previously established Cicada cryptographic parameter (to p < 0.001 against
random). If all anomalies resolve to known, publicly-discussed Cicada aesthetics with no
additional information, verdict is CLOSED as an information channel.

**Note on data:** The raw HTML is not held locally as files (the MANIFEST.md shows only
README.md summary files for each onion, not the actual HTML). This test will work from the
documented anomalies in OSINT-SWEEP-2026-07-27.md and the MANIFEST.md, which contain the
specific values.

**FP rate:** Resolving as an information channel requires structure at p < 0.001 over the
set of documented anomalies. The uptime -> 1033 mapping is already known and already
documented (i.e., previously recognized and STILL not closed as a channel). If it adds
no _new_ information, the channel is closed.

---

## Size-matched null

For E-01 and H-03: the random blob rsahex_cu343_761.bin under the same pow() and XOR
tests serves as the null (if E-01 fired on a random 256B blob it would be a FP).
For E-02: a random permutation of the same byte values in canon_256.bin.
For H-01: the null is the set of trivially-explained Cicada aesthetics (port=5240 is not
obviously meaningful; uptime->1033 is already catalogued).
