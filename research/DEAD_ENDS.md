# DEAD ENDS — Liber Primus (LP2)

Append-only kill log. Check this BEFORE proposing any attack. Re-testing a killed idea without a
NEW, specific justification for why the prior test was flawed burns the round. Each entry records
the mechanism, why it died, and the round/gate that killed it.

> Pre-ledger dead ends (recorded in `FINDINGS-FOR-SOLVERS.md`, `SOLVE-ATTEMPT-FINAL.md`,
> `PICKUP-HERE.md` "Do NOT re-run") are authoritative and NOT duplicated here in full. Summary:
> all periodic keys 1–40 (both directions + Atbash); running keys vs Mabinogion / Self-Reliance /
> King in Yellow / Liber AL / Agrippa / solved-plaintext; number-theoretic keystreams
> (primes, totient, φ, iterated totient, prime gaps, cumsum, page-seeded, all Fibonacci-mod-29
> seeds); plaintext & ciphertext autokey; first-difference / integral inversion; page-on-page
> keystream REUSE; bifid / fractionation (periods swept); homophonic / substitution;
> transposition-only + columnar re-measure (widths 2–40; file order is the unique global doublet
> minimum 0.0067); collision-skip / doublet-avoidant constrained decode; F-mask → ASCII;
> all image-stego channels; vision re-transcription (alignment 0.145, canonical confirmed).

---

## Round 1 — 2026-07-29

### KILLED (Gate #2, executed then refuted) — H1 "Interrupter-as-doublet-breaker"
**Mechanism:** null-ᚠ interrupters inserted specifically where the keystream would produce a
ciphertext doublet, making the deficit an artifact of ᚠ placement rather than of the enciphered body.
**Why dead:** REFUTED by test (see LEDGER Round 1). Stripping all 458 ᚠ leaves the doublet rate at
0.76% (threshold was ≥2.9%); within-word pairs with no ᚠ between them are equally suppressed
(0.64%); interrupters sit between identical flanks *below* chance (2.89% vs 3.58% unigram baseline)
— the opposite of a doublet-suppressing insertion. The deficit is intrinsic to the ciphertext body.
**Do not revive** unless the canonical transcription's interrupter identification is itself
overturned (a transcription-level challenge, not a cipher-level one).

### KILLED (Gate #1, pre-execution) — H2 "Non-repeating modular walk (self-avoiding LCG keystream)"
**Mechanism:** c = p + k mod 29 with k a self-avoiding walk on Z/29 (k[i] ≠ k[i−1] by construction,
e.g. an LCG), to jointly explain flat IoC + sub-chance doublets + delta=0 hole.
**Why dead:** (1) Ground truth was SYNTHETIC only — calibrating "is the totient stream
self-avoiding?" is not reproducing known plaintext by the method; a method that can only be
validated on synthetic data is a keyspace search, not a method. (2) The attack step is
"search self-avoiding seeds, keep the one maximizing quadgram score" — a large keyspace search;
"it decrypted to something meaningful" is worth zero. (3) A full-length self-avoiding keystream is
exactly the OTP-class object already shown to admit a valid structureless key for ANY chosen
plaintext (page-0 underdetermination). Number-theoretic keystreams incl. totient already dead.
**Do not revive** without a non-synthetic ground-truth anchor AND an argument that the seed space is
small enough not to manufacture English by construction.

### KILLED (Gate #1, pre-execution) — H3 "Skip-encipherment / doublet-triggered key stall"
**Mechanism:** c = p + k mod 29, but "if c[i] would equal c[i−1], advance the key one extra step and
re-encipher" — a rejection stall guaranteeing c[i] ≠ c[i−1].
**Why dead:** (1) CIRCULAR prediction — the headline "≈361 implied stalls" = (0.03448 − 0.00664) ×
12956 is the observed deficit re-expressed as a count; it cannot come out false, so it is not a test.
(2) NOT invertible from ciphertext alone — the stall *prevents* the doublet from ever appearing, so a
decoder cannot see which positions were stalled and must GUESS them, multiplying the keyspace by a
combinatorial factor → collapses to a keyspace search. (3) The only non-circular half ("stall-aware
decode + short key → English") reduces to periodic-keyed decoding, and all periodic keys 1–40 are
already dead.
**Do not revive** without (a) a non-circular pre-registered statistic and (b) a demonstration that the
stall rule is invertible from ciphertext without a position search.

---

### Cross-round note: ideas foreclosed by ESTABLISHED findings (do not propose)
- **Superimposition / page-on-page differencing** to cancel a shared keystream: DEAD ON ARRIVAL — the
  keystream is established CONTINUOUS across pages with no per-page reset, so different pages are
  different SEGMENTS of one long key, not the same key; differencing aligned positions cancels
  nothing.
- **Any running-key / full-length natural-language keystream:** ruled out by the doublet deficit
  (z ≈ −16.9); such keystreams reproduce a normal ~2.9–3.4% doublet rate.
