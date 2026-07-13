# Campaign XVII — four fresh attacks on the actual cipher (2026-07-13)

_Not article work. A session spent throwing genuinely-new, well-motivated
cryptanalytic angles at the unsolved pages, driven by "we need headway on the
puzzle itself." All four reproducible; all four null. Recorded so the elimination
ledger stays honest._

## 1. Is the page-56 "AN END" hash a hash of something INSIDE the book?
`pp49_51/hash_hunt.py`. For 10 years the community only hashed external candidate
.onion pages against the page-56 512-bit target (all failed; Tor v2 now dead). We
hashed Cicada's OWN internal artifacts — the pp49-51 2048-bit data object (both
canonical variants, reversed, hex-string, ±newline), the full runic ciphertext
(utf-8 and index-bytes) — across 10 algorithms (SHA-2/3, BLAKE2, SHAKE, …).
**140 combinations, no full or partial preimage match.** The "sought page is the
data object in the book" hypothesis is dead.

## 2. Could interrupters mask a running key (rescuing the excluded class)?
The doublet-deficit finding excludes additive running keys because they'd inject
~3.45% doublets. Hypothesis: Cicada's confirmed ᚠ-interrupter mechanism erases
the doublets, so a running key survives. **Refuted by the interrupter rule
itself:** only `ᚠ` (1 of 29 runes), and only a sparse subset, is ever a null —
that cannot uniformly suppress doublets across all 29 runes (the observed deficit
is uniform and all-rune). The exclusion stands.

## 3. Plaintext-feedback autokey over the prime/totient family
`seek_autokey.py`. `seek_primes.py` only fed back on the CIPHERTEXT; the cipher
Cicada's hints suggest ("THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED",
page-56's prime-totient keystream) is a plaintext-feedback autokey
`p[i]=c[i]-F(p[i-1])`, decrypted sequentially from a brute seed. Swept 5 feedback
functions × 2 signs × 2 atbash × 29 seeds over all 55 pages, English-quadgram
scored. **Best −6.67 vs English −4.24 / noise −4.5 — pure noise. Null.**

## 4. Crib-dragging that recovers an ARBITRARY fixed feedback function
`crib_autokey.py`. The right weapon against autokey: a known-plaintext crib. For
any fixed single-history autokey `c[i]=p[i]+K(p[i-1])`, a correct crib at a page
start yields a consistent partial K-table (wrong cribs contradict) — recovering K
*without guessing it*, then extending the decrypt. Tried 24 Cicada openers ×
offsets 0-6 × signs × atbash over all pages. **Exactly one consistent extension:
"WELCOME" on the solved intro page, extending to noise ("WELCOMEWMMELNG",
−6.10).** No real page yields a consistent extendable table. Fixed single-history
autokey with known openers is refuted.

## Honest net
Four distinct, previously-untried-or-under-tried attacks, each motivated by a
real signpost (the hash, the interrupter mechanism, Cicada's prime/totient hints,
the autokey fingerprint). All null. Crib-dragging — the technique that actually
breaks autokey ciphers — found nothing, which is strong: it means the mechanism
is either a true external-key OTP (unbreakable from inside by construction) or a
multi-rune-history feedback whose function space is too large to guess and which
cribs don't catch. **No internal-ciphertext attack surfaced this session moved
the needle. The wall is real, and it is where the evidence has always pointed.**
