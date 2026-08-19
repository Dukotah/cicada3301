# Round 15 — the armada aimed at what is genuinely unexhausted

_Drafted 2026-08-19, after Round 13's B-04 Stage A returned NEGATIVE and Round 12's A1 closed._

## How the targets were chosen

Not by "what have we not done" — that list is long and mostly low-value — but by a harder
filter, applied in this order:

1. **Is it inside the one hypothesis class the ciphertext cannot rule out?** D3 proved LP2 is
   OTP-*class*: indistinguishable between a true external pad (closed) and a **short-seed
   derived** keystream (finite, brute-forceable). Work inside the derived branch is the only
   compute that can possibly succeed.
2. **Is it explicitly outside the bound of everything already run?** A lane that merely adds
   items to an exhausted family is not new evidence.
3. **Is it control-detectable?** If a planted signal cannot be recovered through the harness,
   the lane cannot produce a trustworthy negative and should not be run at all.
4. **If it cannot solve, does it harden or falsify a load-bearing claim?**

Lanes are ordered by honest prior, and the priors are stated. Most are low. That is the real
state of this problem, and a plan that pretends otherwise is worth less than no plan.

---

## LANE 1 — KDF / key stretching · prior: **the highest available** · flagship

**The gap.** B-04 sweeps *single-application* keystreams: `SHA256(seed ‖ ctr)`, `h = H(h)`,
HMAC-DRBG, AES-CTR, RC4, ChaCha20. Its own §6 declares out of scope: *"key stretching
(PBKDF2 / scrypt / Argon2 / iterated-hash counts > 1)"* and *"salted constructions"*.

**Why the prior is genuinely high, not merely nonzero.** Ask what a cryptographically literate
author in 2013–14 would actually do to derive a **reproducible** full-length pad from a secret
they can remember. They would not use a bare hash — that was already a decade-old, widely-taught
mistake. They would use a **KDF with an iteration count**: PGP's String-to-Key, TrueCrypt,
OpenSSL's `EVP_BytesToKey`, WPA2, and every tutorial of the era. Cicada's own artifacts are
steeped in exactly that culture — PGP, RSA, OutGuess, Tor.

Within the derived-keystream branch, this is arguably **more** plausible than the bare-hash
family B-04 is sweeping, and it has never been run.

**Why it was invisible.** A KDF's output is by design computationally unrelated to its input,
so `PBKDF2(s, salt, 10000)` and `SHA256(s)` share no detectable relationship. A null over one
constrains the other **not at all**. And the MDL kill ("incompressible ⇒ not algorithmically
generated") has no power here, for the same reason it has none over B-04.

**Bound.** 27 KDF configurations (PBKDF2-SHA1/256/512 at 1000/2048/4096/10000/100000 and 3301;
scrypt at RFC-7914 interactive; iterated SHA-256/MD5; `EVP_BytesToKey`) × 504 core secrets +
124 passphrase forms × 3 salts (Stage A) → 11 salts (Stage B) × 2 reductions × sign × Atbash ×
direction. Argon2 deliberately excluded as **anachronistic** (PHC winner 2015, after LP2).

**Gates.** K1 replicates D3's expander control. K2 plants a `PBKDF2-SHA256(·, ·, 10000)`
keystream from a dictionary-resident secret and requires it to rank #1 through the full
Stage-A cross product.

→ `round15/KDF/` — `PREREG.md`, `kdf.py`, `sweep.py`

---

## LANE 2 — A-03, the haplography count-audit · prior: **medium** · the cheap falsifier

**Why this outranks most attack lanes.** It does not try to solve the cipher. It attacks the
**load-bearing evidence** for the verdict. The entire OTP-class conclusion rests on the doublet
*deficit* — 0.664% observed against a ≥1.38% plaintext-independent floor. If ~20 of the 86
doublet sites are actually transcription **merges** (a doubled rune silently read as one), the
deficit shrinks and **autokey returns to the table**.

**Why it is still open after four transcription audits.** Every one of them checked rune
**identity**. None checked rune **count**. Campaign IX's OCR spot-checked three lines of one page.

**Method.** Use the *validated* R9 template-DP instrument (98.0% on control), never the forced
re-segmentation one (12.9% — fails its own control). Measure per-line glyph count against canon;
adjudicate mismatches at high zoom. **Plant synthetic merges first** — if the instrument cannot
detect a planted merge, report INCONCLUSIVE, as frontB correctly did.

**The deliverable is a bound, not a verdict.** "No merges found" is nearly useless. "The deficit
survives up to K merges, and we bound K < M" is what lets the next person stop worrying about it.

---

## LANE 3 — the matched scorer · prior: n/a · +18% power, measured, benefits every lane

Not an attack. Every sweep in this repo scores with raw-English quadgrams, but the decoder emits
the runic **transliteration** — 7 of 29 runes expand to two characters, and the alphabet is
lossy. Training on one distribution and scoring another costs power.

**Measured, not asserted:** a matched model tightens noise σ from 0.089 to 0.071 and improves
separation from **34.4σ to 40.5σ**. Modest and real. It changes no completed negative (every
published null sits far below the English band); it makes *future* sweeps harder to fool.

→ `round15/SCORER/FINDING.md`, `poc.py`

---

## LANE 4 — F-01, LP2-as-pad inversion · prior: **low** · finite, never run

Invert the assumption: the unsolved pages are **key material**, not a message. Use the
12,956-rune stream (forward/reversed, ±, Atbash) as a running key against every other
machine-readable Cicada object — the 2012/2013 fragments, the AN-END hash bytes, `canon_256`,
onion names, PGP bodies. Finite candidate set, hours of compute, and it survives the
"message-existence is undecidable" finding rather than being killed by it.

---

## LANE 5 — the zero-FP and provenance batch · prior: **low each, cheap in aggregate**

Register items that are minutes of compute apiece and have sat unrun because they are small,
not because they are weak. Each has an *analytic* false-positive probability, which makes them
decision-grade rather than suggestive.

- **E-01** payload as an RSA signature under published 3301 moduli — PKCS#1 padding does not
  occur by chance; a zero-false-positive test.
- **E-02** payload as meta-parameters — the 56-byte permutation window (≈1e-24 per window).
- **H-03** the 2013 onion cookies XOR'd against the four hex strings — "that specific cross is
  untried".
- **H-01** per-onion HTTP anomalies, resolved as a channel or closed.
- **D-01** the generator-fingerprint suite — tests whether the anti-repeat hardening was
  **applied by hand**, which `FINAL-SYNTHESIS.md` asserts and nothing has ever tested.
- **A-06** the 47 catalogued ornament bands nobody has read.
- **C-02** line-initial uniformity, the detector for acrostic *forcing*, at a pre-registered
  p<0.001.
- **G-02** the OutGuess blank control, deferred in 2026-06 for want of a Linux environment that
  now exists.

---

## LANE 6 — PHP `mt_rand` and the uncovered generators · prior: **medium-low**

"Seeded-PRNG pads — do not re-run" is wrong: 10 generators over ~3% of each seed space, and
`L5-seed32/CENSUS.md` names PHP `mt_rand` as the highest-prior untouched generator —
period-appropriate for Cicada's 2012–13 PHP stack. Requires validating each generator against a
real reference implementation first, and the **beam** decoder, since Round 8 swept rigid-only.

---

## What this armada will not do

It will not solve LP2 if the keystream is a true external pad. Nothing can. Lanes 1, 4 and 6
are bets on the derived branch; lanes 2, 3 and 5 harden or falsify the reasoning either way.

The honest expectation is that all of it comes back negative. It is worth running because the
derived branch is **cheap to eliminate and impossible to eliminate by argument**, and because
every lane leaves behind a stated coverage bound — which is what makes the next attempt cheaper
instead of a repeat.
