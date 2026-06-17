# The Doublet Deficit — Full Investigation

_2026-06-17. Tools: `analysis/doublet_probe.py`, `src/lp/autokey.py`, ad-hoc probes._

The unsolved Liber Primus pages have one statistical anomaly: consecutive
identical runes ("doublets") occur at **0.664%**, ~5× below the random rate of
3.448%. This was the single most promising lead. We chased it rigorously. Here
is what we found.

## Method
A doublet `cᵢ = cᵢ₊₁` is suppressed below random by only a narrow set of cipher
constructions. We (1) derived the doublet signature of each candidate, (2)
validated the math against synthetic ground truth, (3) tested each against the
real pages, and (4) compared to the known-solved pages as controls.

## Results

### 1. The deficit is real and specific to the unsolved pages
| page set | doublet % | IoC·N |
|---|---|---|
| Solved WELCOME (Vigenère) | 3.56 | 1.18 |
| Solved koan (Vigenère) | 2.83 | 1.13 |
| Solved A WARNING (Atbash) | 2.73 | 1.86 |
| Solved AN END (**totient keystream**) | **2.38** | **0.94** |
| **Unsolved pages** | **0.66** | **1.00** |

Every *solved* enciphered page has a normal doublet rate. Critically, **AN END**
uses a totient keystream that flattens its IoC to 0.94 — identical to the
unsolved pages — yet its doublet rate is a normal 2.38%. **So flat/random
statistics do NOT by themselves cause a doublet deficit.** The unsolved pages do
something extra that no known Cicada cipher does. (And it isn't a transcription
artifact: the solved pages, transcribed by the same community, are normal.)

### 2. No standard construction reproduces 0.66%
Encrypting real English (mapped to Gematria Primus) every standard way:
| construction | doublet % |
|---|---|
| running key (English + independent English) | 3.32 |
| prime keystream | 2.88 |
| totient(prime) keystream | 2.88 |
| short Vigenère (len 8) | 3.44 |
| plaintext autokey | 4.17 (*more* doublets) |
| **target (observed)** | **0.66** |

Running key, autokey, prime/totient streams, Vigenère — all land at 2.9–4.2%.
None suppresses doublets.

### 3. Ciphertext-autokey: matches the *rate*, fails to *decrypt*
A ciphertext autokey (`cᵢ = pᵢ + cᵢ₋₁ + K`) is the one construction that
suppresses doublets: a doublet then occurs only when `pᵢ₊₁ = −K`, so the
doublet rate equals the plaintext frequency of one fixed rune. Synthetic test
confirmed this exactly (K=0 → 3.407% predicted vs 3.408% measured; decrypt
recovers plaintext). Rare runes (EO 0.67%, P 0.89%, NG 0.29%) have frequencies
near the observed 0.66%, so the rate *is* consistent with a ciphertext autokey.

**But brute-forcing every (seed, K, sign, Atbash) ciphertext- and
plaintext-autokey decryption of the real pages produced only gibberish**
(score ≈ −7.4, identical to raw ciphertext; real English ≈ −4.0). Autokey is
refuted as the actual cipher.

### 4. The differences are structureless
Under any cumulative/autokey model the consecutive differences `dᵢ = cᵢ − cᵢ₋₁`
would be the plaintext (or keystream). We measured the full difference
distribution over the unsolved corpus:
- `d = 0`: 0.664% (the deficit)
- **IoC·N of all differences = 1.024; of non-zero differences = 1.037** (flat)
- entropy 4.831 / 4.858 bits (near-maximal)
- rune frequencies 3.08–3.80% (uniform); ᚠ/F at 3.54% (not inflated)

**The differences are flat random with a single hole at zero.** There is no
period, no keystream structure, no English hiding in the differences.

## Conclusion

The entire unsolved corpus reduces to **one anomaly — consecutive runes almost
never repeat — and that anomaly carries no recoverable structure.** This is the
fingerprint of a cipher (or hand-encoding rule) that *deliberately avoids
producing two identical runes in a row* while otherwise randomizing maximally.
It is categorically different from every solved Cicada cipher.

Honest bottom line: the doublet deficit, chased to the end, is a **hardening
artifact, not a crack.** It tells us the cipher was engineered to defeat exactly
this kind of statistical attack — and it succeeds: once you set aside the
no-repeat property, nothing distinguishes the text from a one-time pad. Chasing
this lead did not open the cipher, and it provides strong (own-measured)
evidence for the view that the remaining pages need an externally-held key or
were designed to be unsolvable.

### Where that leaves the realistic options
1. **Running-key against the *actual* referenced texts** (Mabinogion, Gibson's
   *Agrippa*, Emerson's *Self-Reliance*) — low odds (a running key would have
   shown ~3.3% doublets, which we do NOT see), but cheap to rule in/out properly.
2. **The key was never published** → cryptographically a dead end, as the flat
   statistics imply.
3. **A non-standard hand cipher** with the no-repeat rule — would need a
   structural insight we do not currently have.
