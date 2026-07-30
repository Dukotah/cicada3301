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

## Round 2 — 2026-07-30

### KILLED (Gate #2, executed then refuted) — R2-H1 "Fractionation coordinate-plane dispersion signature"
**Mechanism:** trifid/Polybius-class fractionation would leave a period-locked autocorrelation peak
inside a decomposed coordinate sub-stream (a dimension the aggregate IoC-ceiling argument never
measures).
**Why dead:** REFUTED by test (see LEDGER Round 2). Across 3 grid packings (Polybius 6×5; trifid
layer-major; trifid col-major) and all coordinate sub-streams, max autocorrelation A_max ≤ 0.028 over
lags 2–40 — below the length-matched surrogate 99th percentile (~0.032) and far below the 0.05 floor.
Harness validated (synthetic period-13 trifid surfaced at its harmonic lag). This upgrades the prior
IoC-ceiling *inference* against fractionation to a direct coordinate-level *null measurement*.
**Do not revive** trifid/Polybius/coordinate fractionation without a NEW statistic that isn't
period-autocorrelation and isn't bounded by the IoC≤1.39 ceiling.

### KILLED (Gate #1, pre-execution) — "delta=0 hole re-measured under route/rail transposition"
**Why dead:** Redundant. CRYPTO-RIGOR §B already de-transposed at every columnar width 2–40: file
order is the unique global doublet minimum (0.0067) and every width RESTORES doublets toward random —
so "does a transposition refill the hole?" is already answered (yes, for columnar) and the proposed
CONFIRM condition would even mis-fire on that known result. jbo/cicada_tools already ran a spiral
(route) transposition, no solve. The untested residue (rail/boustrophedon) is a marginal slice with
no mechanism to behave opposite to the 39 columnar widths.
**Do not revive** without a specific mechanism predicting a non-columnar order would LOWER d=0 when all
columnar widths raise it.

### KILLED (Gate #1, pre-execution) — "Alternative rune-index-ordering battery"
**Mechanism:** re-run difference/keystream/no-repeat-decode/IoC battery under permuted rune→0..28
orderings (prime-order, Gematria-value, alphabetical) on the theory that "differences are structureless"
was measured in the wrong basis.
**Why dead:** ANCHOR-REFUTED. Five solved pages — Atbash (p01), Caesar −3 (pp06–09), Vigenère
DIVINITY (03–04), Vigenère FIRFUMFERENCE (14–15), and the **LP2 page AN END** (totient shift) — all
reproduce known plaintext ONLY under mod-29 arithmetic in canonical GP order. The cipher's native
basis is therefore *proven* to be canonical order, including into LP2. The only surviving version ("the
unsolved section uses a different ordering than the solved sections") has zero supporting evidence and
is unfalsifiable speculation; scoring alternative orderings for "language" is also a keyspace search.
**Do not revive** without positive evidence of an ordering discontinuity between solved and unsolved
sections.

---

## Round 3 — 2026-07-30

### KILLED (Gate #1, pre-execution) — R3-H1 "Anchored keyed-collision-skip DP/Viterbi decode"
**Mechanism:** c[i]=p[i]+k[i] mod 29 with a forward collision-skip (advance key an extra step if c[i]
would equal c[i-1]) and a short period-2–12 skip-key; inverse = n-gram-scored Viterbi DP enforcing the
skip constraint, co-searching the short key; anchored by recovering WELCOME/AN END.
**Why dead (three independent fatal failures):**
1. UN-ANCHORABLE. No solved page carries the sub-chance doublet deficit (WELCOME 3.56%, koan 2.83%,
   A WARNING 2.73%, AN END 2.38% — all normal). The decoder's defining constraint c[i]≠c[i-1] is FALSE
   on every solved ciphertext, so the novel mechanism cannot be validated on any known solve; only its
   degenerate plain-Vigenère mode anchors, and periodic keys 1–40 are already dead. → keyspace search.
2. DEGENERATE NULL. First-difference entropy near-maximal (4.831/4.858 bits); a no-repeat-preserving
   surrogate matches the only non-flat statistic → the surrogate null is unbeatable by construction.
3. ALREADY KILLED. This IS Round-1 H3 (the doublet-triggered key stall), whose revive-bar it does not
   clear; CRYPTO-RIGOR §C already ran the no-repeat-inversion family (IoC_norm 1.037, no language);
   PICKUP-HERE lists it "Do NOT re-run."
**Do not revive.** The sub-chance deficit is un-anchorable in principle (no solved page has it) and the
no-repeat-preserving null is degenerate. This is a permanent structural barrier, not a tooling gap.

### KILLED (Gate #1, pre-execution) — R3-H2 "Interrupter-position-marginalized collision-skip decode"
**Mechanism:** as R3-H1 but ᚠ/stall positions marginalized as latent Viterbi lattice states instead of
combinatorially searched.
**Why dead:** identical un-anchorable + degenerate-null failures as R3-H1. Its sole differentiator —
latent-state marginalization — is a direct attempt to clear Round-1 H3's revive-bar (b) "invertible
without a position search," but marginalizing the position search IS the position search summed over the
lattice; it does not eliminate it. Fails the bar it targets.
**Do not revive** for the same structural reason as R3-H1.

---

## Round 4 — 2026-07-30 (EXTERNAL leads)

### KILLED (Gate #1) — "External cribs as LP2 additive key" (2012 P.S. number, 2013 onion hashes, missing-primes)
**Mechanism:** apply each catalogued "never-used" string (P.S. 130-digit number; two 256-bit 2013
onion-cookie hashes; missing-primes set 73–1223) as a repeating/seed additive keystream to the 55
unsolved pages, quadgram-score vs surrogate null.
**Why dead:** (1) **Empirically pre-refuted, not merely inferred** — DOUBLET-INVESTIGATION §2 already
measured the additive family's doublet output on THIS ciphertext (prime 2.88%, totient 2.88%,
running-key 3.32%, Vigenère 3.44%) vs the 0.66% deficit (z≈−16.9). Any additive key, including these,
must land in the already-measured normal band; the Round-2 inference→measurement escape hatch does not
apply (dimension already measured). (2) **Un-anchorable** — none of the three equals/generates a known
solved-page key; direct comparison, no experiment. (3) Missing-primes is a number-theoretic keystream,
already dead. Provenance caveat: speculative cribs, none signed as the LP2 key.
**Do not revive** as an additive key without a SIGNED indication a string IS the LP2 key.

### KILLED (Gate #2, OSINT pointer chase R4-OSINT-1) — the three cribs as external POINTERS
**Why dead:** chase came back COLD. 2012 P.S. number = a factored RSA-130 semiprime (p, q, e=65537)
from the signed 2012 Valēte! message — points nowhere, "never used despite factorization"; the
rotate-90°/matrix reading is UNVERIFIED speculation. 2013 cookies = opaque, unexplained by any source,
no match to any onion/file/CT-log/AN END trail (761/167 are the Instar-Emergence audio id + reverse, an
internal cross-link). Missing-primes = a clean contiguous interval indexing nothing. **Do not revive**
without a new archival/signed referent.

### CLOSED — external LP2 key as a released artifact
The only external pointer (AN END hash → `gy3hoy2zizvuzvdb.onion`, Tor v2) is **verifiably dead**
(v2 deprecated Oct 2021; never archived). No credible externally-distributed LP2 key exists.

### AUTHORSHIP — no verifiable identity (do not state a named creator as fact)
Only verifiable anchor: PGP key `7A35090F` (fp `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`),
never controlled by any identified party, last signed April 2017. Best inference: a cypherpunk/privacy
collective (LOW–MODERATE, inferential). Schoenberger = rumor-tier (no key control). Do not launder
named-individual claims into fact.

---

## PROGRAM STATUS — CIPHERTEXT-ONLY ATTACK COMPLETE (2026-07-30)

After ~20 pre-ledger attack families + 3 rigorous ledger rounds (all NEGATIVE or Gate-#1 KILL), the
ciphertext-only program is **exhausted**. Unsolved LP2 is **OTP-class**: full-length keystream + a
deliberate no-repeat rule, **information-theoretically unsolvable from ciphertext alone without an
externally-held key**. No ciphertext-only test can move this verdict. Remaining rational moves are
EXTERNAL only: (a) obtain the key/seed (unpublished; may not exist publicly), or (b) independent
from-scratch re-transcription (already attempted 3 ways, negative-for-errors). **Do not open new
ciphertext-only attack rounds without a genuinely new external input** (a key, a seed text, or a
transcription discrepancy) — absent that, every round will and should end NEGATIVE/KILL by construction.

---

### Cross-round note: ideas foreclosed by ESTABLISHED findings (do not propose)
- **Superimposition / page-on-page differencing** to cancel a shared keystream: DEAD ON ARRIVAL — the
  keystream is established CONTINUOUS across pages with no per-page reset, so different pages are
  different SEGMENTS of one long key, not the same key; differencing aligned positions cancels
  nothing.
- **Any running-key / full-length natural-language keystream:** ruled out by the doublet deficit
  (z ≈ −16.9); such keystreams reproduce a normal ~2.9–3.4% doublet rate.
