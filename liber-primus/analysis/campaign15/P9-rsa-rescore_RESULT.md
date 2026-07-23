# P9-rsa-rescore — Campaign XV probe result

- **probe_id:** P9-rsa-rescore
- **verdict:** null-closed
- **headline_number:** 0 RSA-structure matches in 12 pow(s,e,n) tests against 2 authentic 4096-bit Cicada moduli; best OE re-score −5.819 and best Latin −5.767 both sit at the random-key floor (OE self-cal −5.487, Latin self-cal −4.597), full-page IoC·N max 1.264 < 1.3.
- **falsifiable_signal:**
  - (A) `pow(payload, e, n) mod n` under a real Cicada modulus yields PKCS#1 v1.5 padding (`00 01 FF..FF 00 || DigestInfo`) or a PSS trailer `0xBC` in either endianness.
  - (B) any archived running-key decrypt scoring, under an Old-English or Latin rune-space quadgram model, above the matched random-key control AND at least halfway to genuine-language self-calibration; OR a full-length page (L≥200) decrypt with IoC·N > 1.3 exceeding the random-key control.
- **signal_fired:** false
- **synthetic_validation:** n/a — this probe is pattern-matching (PKCS/PSS) and re-scoring, not a decrypt whose recovery needs synthetic confirmation. Trust anchor `python tests/validate.py` PASSES (rig reproduces all known solves); RSA modulus authenticated by fingerprint match `6D854CD7933322A601C3286D181F01E57A35090F` = the repo's documented Cicada signing key (KEY-HINT-RESEARCH.md).

## method

**(A) RSA.** The full Cicada 3301 public key (not mirrored on disk — only metadata
`n_bits=4096, e=65537` survived in `analysis/armada20/pubkey_packets.json`; the
armored `.asc` lived at a Windows path and the on-disk `key_b64_letters.txt` is
letters-only and non-decodable) was fetched from `keyserver.ubuntu.com` by keyid
`0x181F01E57A35090F` and saved to `analysis/campaign15/cicada_pubkey.asc`. A
pure-Python OpenPGP packet parser recovered **two** RSA moduli — the primary key
(`181F01E57A35090F`) and the encryption subkey (`4D390ECF671DDEB1`), both 4096-bit,
e=65537. The pp49–51 payload (`analysis/pp49_51/canon_256.bin`, 256 bytes) was
read as an integer in **both** endiannesses; for each (modulus, endianness, e∈{65537,3,17})
with s<n, `pow(s,e,n)` was computed and the 512-byte block pattern-matched against
PKCS#1 v1.5 signature padding (with SHA-1/256/512/MD5 DigestInfo DER prefixes) and
the PSS `0xBC` trailer. 12 valid tests ran (e=3,17 gave s≥n for one endianness and
were skipped). **Structural bar:** 256 bytes = 2048 bits is exactly *half* a
4096-bit block, so the payload cannot be a genuine RSA signature/ciphertext under
the only known Cicada key regardless of the pow() outcome.

**(B) Language-agnostic re-score.** Rune-index-space quadgram models were built,
via Gematria Primus, from Old English (`data/keys/runepoem_oe.txt`) and Latin
(`analysis/campaign15/latin_caesar.txt` = Caesar *De Bello Gallico*, 311k letters,
fetched from Perseus), plus an English control (solved-page plaintext). The
archived sweeps (`campaign12/13`) stored only scores, not decrypt strings, so
best-of-search running-key decrypts of all 55 unsolved pages were **regenerated**
from the on-disk keytext corpus (foundation esoterica: Enoch/Hermes/Monas/
Rosicrucian/Sepher Yetzirah, plus solved plaintext, the OE rune-poem, and Latin
Caesar) over all offsets/signs/atbash, and each decrypt scored under all three
models simultaneously. A **matched random-key control** (8 uniform-random keys, same
search) provides the null. Language-blind gate: decrypt IoC·N, gated on full-length
pages (L≥200, where the null variance is small enough that >1.3 is ~3σ); short-page
maxes are extreme-value noise and reported but not gated.

## results (actual numbers)

RSA (Probe A): moduli `181F01E57A35090F` / `4D390ECF671DDEB1`, both 4096-bit e=65537;
tests_run=12; **PKCS#1 v1.5 matches: 0; PSS matches: 0.**

Re-score (Probe B), best decrypt score per model vs matched random-key control vs
genuine-language self-calibration:

| model | real best | random-key control | genuine-language self-cal | beats control? | looks like language? |
|---|---|---|---|---|---|
| Old English | −5.819 | −5.816 | −5.487 | no | no |
| Latin | −5.767 | −5.719 | −4.597 | no | no |
| English (ctrl) | −5.787 | −5.805 | −5.544 | ~tie | no |

IoC·N: full-page (L≥200) real max **1.264** vs control **1.207** (gate 1.3 → not fired);
short-page max 1.852 vs control 1.676 (extreme-value noise, ungated). Real keytexts do
not even beat random keys under OE/Latin — every regenerated decrypt sits at the
random floor, ~0.3 (OE) / ~1.2 (Latin) *below* what genuine OE/Latin text scores.

## one_paragraph

Two cheap closers, both clean nulls. (A) The pp49–51 payload is **not** an RSA
signature or ciphertext under Cicada's real public keys: the authentic 4096-bit key
(fingerprint 6D85…090F, verified against the repo) was fetched and both its moduli
parsed, and `pow(payload, e, n)` in both endiannesses over e∈{65537,3,17} produced
**zero** PKCS#1 v1.5 or PSS structure in 12 tests — and structurally can't, since a
256-byte (2048-bit) payload is exactly half a 4096-bit RSA block. This is the first
time the repo actually holds a usable Cicada modulus on disk (`cicada_pubkey.asc`);
the prior "no modulus on disk" state is now upgraded to a *tested* negative. (B) The
English-plaintext scoring assumption is discharged: re-scoring regenerated running-key
decrypts of all 55 unsolved pages under Old-English and Latin rune-space quadgram
models yields best scores of −5.819 (OE) and −5.767 (Latin) — at the random-key
control floor and far below the −5.487 / −4.597 that genuine OE/Latin text scores —
with no decrypt beating a matched random-key control and full-page IoC·N peaking at
1.264, under the 1.3 language-blind gate. No archived null is a missed OE/Latin hit.
The flat (IoC·N=1.000) ciphertext yields flat decrypts regardless of scoring language,
exactly as the one-time-pad-class model predicts.

## reproduce

- **script_path:** `analysis/campaign15/P9-rsa-rescore.py`
- **reproduce_cmd:** `cd liber-primus && python3 analysis/campaign15/P9-rsa-rescore.py`
  (runs fully offline against `analysis/campaign15/cicada_pubkey.asc` and
  `analysis/campaign15/latin_caesar.txt`, both saved in-repo; JSON →
  `analysis/campaign15/P9_result.json`). Modulus provenance re-fetch:
  `curl "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x181F01E57A35090F&options=mr"`.

## ledger_row

| Attack | Verdict | Why | Where |
|---|---|---|---|
| pp49–51 payload as RSA sig/ciphertext under real Cicada public keys (both 4096-bit moduli, e∈{65537,3,17}, both endian) + OE/Latin language-agnostic re-scoring of running-key decrypts | ❌ null-closed | 0/12 pow(s,e,n) show PKCS#1v1.5/PSS structure — and 2048-bit payload is half a 4096-bit block; OE/Latin re-scores (−5.819/−5.767) sit at the random-key floor, below genuine-language self-cal, none beat a matched control; full-page IoC·N max 1.264 < 1.3 | Campaign XV P9 `analysis/campaign15/P9-rsa-rescore.py`, `P9-rsa-rescore_RESULT.md` |
