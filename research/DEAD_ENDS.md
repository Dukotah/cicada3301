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

## Round 5 — 2026-07-30 (new strategist slate)

### KILLED (Gate #2, executed then refuted) — R5-COMBINED "residual-doublet structural anatomy"
Folded three new strategies into one anchored structural test (both anchors passed; degeneracy guard
applied). All refuted:
- **#1 SEAHORSE (Playfair-class digraphic parity):** the 86 residual doublets show NO position-parity
  split (Δ_parity 1.3σ, sign-flips between phases; within-pair hard-zero absent) and NO digraph-IoC
  inflation (1.031 < 1.044 threshold). LP2 is not a Playfair-family polygraphic cipher.
- **#2 TIDELINE (residual-doublet anatomy):** doubled-rune identity χ² p=0.48 (no dominant value → not a
  fixed-shift ciphertext-autokey); inter-doublet gaps geometric (KS p=0.69 → memoryless placement).
- **#4 HALFTIDE (two-track interleave):** lag-k spectrum shows suppression PURELY at lag-1 (0.66%); lags
  2–6 are all at chance (≈3.4%) → no interleave periodicity; the no-repeat rule is adjacent-only.
**Do not revive** the polygraphic, autokey-fingerprint, or interleave families — each is now
measured-closed, not merely inferred.

### KILLED (Gate #1, pre-execution) — #3 ROSETTA "non-English / numeric plaintext rescoring"
**Why dead:** the flat IoC·N≈1.00 is a SCORER-INDEPENDENT measurement — Latin/Old-English/gematria
plaintext would raise IoC·N toward 1.7–1.9 regardless of which n-gram model scores it. Re-scoring under
a different language model cannot rescue a stream already at the OTP coincidence floor; the numeric arm
reduces to scoring readings for meaning (a soft-signal keyspace search).
**Do not revive** without a mechanism that changes the measured IoC, not just the scorer.

### KILLED (Gate #1, pre-execution) — #5 DELVE "non-ᚠ placeholder rune marks suppressed doublets"
**Why dead:** foreclosed by Round 1's established result — within-word pairs with NO intervening marker
are equally suppressed (0.636%); a placeholder-rune channel requires a marker at suppressed sites, which
the marker-free within-word suppression refutes. Revival of the interrupter-channel family (R1 H1)
without new justification.
**Do not revive** without evidence of a marker channel that survives marker-free contexts.

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

## Round 6 — 2026-07-30 / anchor-corrected 2026-08-06
### KILLED (Gate #2, executed then refuted) — TEST 1 SIEVE-W "misfiled-plaintext window"
**Mechanism:** a sliding bigram-LLR + IoC window detector to catch any unsolved page/sub-page window
that is actually readable (mis-filed) plaintext. **Why dead:** REFUTED — 0 windows cleared the family
+ plaintext cut; best real window LLR 0.074 ≪ 0.4808. See LEDGER Round 6.
**Do not revive** without a new plaintext model that lifts a real window above the solved-page floor.
### KILLED (Gate #2, executed then refuted) — TEST 2 TRANSITION-STRUCTURE "keel + lattice"
**Mechanism:** a second forbidden offset ("keel"), hard-zero off-diagonal transition cell, or 2nd-order
(trigram) bias beyond the known lag-1 no-repeat rule. **Why dead:** REFUTED — deepest non-identity
offset k=17 z=−2.78 (not below family 0.1th pct), H2 3.5228 at null center, 0 hard-zero off-diagonal
cells. Trigram-tensor χ² arm INCONCLUSIVE (underpowered, 0.531 counts/cell) and cannot rule the finest
structure in or out. **Anchor-integrity note:** the original run halted on a mis-specified specificity
anchor (A4 used the 85-rune solved *plaintext* page AN END as a null-center control — wrong object,
wrong length); corrected 2026-08-06 to a length-matched held-out no-repeat surrogate through the exact
decision predicates. Verdict direction unchanged (NEGATIVE), no goalpost move.
**Do not revive** the keel/transition-lattice family without a NEW anchorable statistic, nor the
trigram arm without ~10× more data per cell (structurally unavailable at n≈13k).

## Round 7 — 2026-08-06 (external-input hunt) — GATE-#1 KILL, 0/15
### KILLED (Gate #1) — new-keytext under the skip-aware or rigid decoder (8 candidates)
**Included genuinely-absent texts** (real Cornelius Agrippa *De Occulta Philosophia*; Welsh-*source*
Mabinogion; Blake's *Jerusalem/Milton/The Four Zoas*; the author's own solved plaintext; Havamal/
Voluspa/Corpus Hermeticum/OE Rune Poem). **Why dead:** the **rigid** running-key arm is foreclosed by
the doublet deficit (any full-length natural-language key → ~3.3% doublets vs 0.66%, z=−16.9); the
**skip-aware** arm is un-anchorable (c[i]≠c[i-1] is FALSE on all 5 solved pages → validates only on
synthetic self-plants; already killed R1-H3/R3-H1/R3-H2). New text ≠ new mechanism. Two were also
already-executed (Blake-complete-additive; author's-own-plaintext via Campaign XVIII rosetta key).
**Do not revive** any keytext (skip-aware or rigid) as a novel avenue — the avenue is foreclosed by
MECHANISM, not by text coverage. Corrects the `PICKUP-HERE` "untried keytext = #1 open avenue" framing:
that avenue is closed.
### KILLED (Gate #1) — AN END hash-preimage vs new onion/WARC corpora (2 candidates)
**Why dead:** degenerate-null-by-corpus-mismatch (darknet-market/gateway crawls are topically disjoint
from a deliberately-unlinked Cicada key page) and not-runnable (parasitic on an absent corpus). Same
avenue as R4-OSINT-1 (cold). **Do not revive** without a CORRECTLY-TARGETED, locally-held archive that
could plausibly contain the AN END page.
### KILLED (Gate #1) — new ciphertext-only statistics (3) + ledger-integrity "tests" (2)
**Why dead:** the statistics re-parameterize the already-closed Round-6 transition dimension or are
Round-1 H3 read backwards; the ledger-integrity items run no cryptanalytic test (external_input=NONE).

### MAINTENANCE NOTE (not a test) — Campaign XVIII skip-aware program is an UNLOGGED NULL
The `liber-primus/analysis/campaign18_skip/` skip-tolerant/collision-skip program was executed and
returned **NULL** across its families (keyword / numeric / self-referential / autokey / interrupter /
payload running keys, plus the cleaned LP1-English "running_solved" key), but was never logged in this
file or `LEDGER.md`, and now survives only as orphaned Python-3.12 `.pyc` bytecode (source deleted;
does not import under the system's newer Python). **Recorded for provenance:** (a) the skip-aware /
collision-skip family is ALREADY KILLED under R1-H3 / R3-H1 / R3-H2 — future rounds must not re-propose
it as novel; (b) Campaign XVIII ran it to null. **Do NOT** decompile-and-backfill its unauditable run
counts into the multiple-comparisons denominator (unvalidated-harness runs inflate the correction with
noise). This is bookkeeping, not a new measurement.

## PROGRAM STATUS — UPDATED 2026-08-06 (Rounds 6–7)
Round 6 closed the last structured-combiner / keel / transition-lattice family (NEGATIVE) and confirmed
no misfiled-plaintext window. Round 7 (external-input hunt, 15 candidates) was a **unanimous Gate-#1
KILL** and additionally **closed the "untried public keytext" avenue by mechanism** (both rigid and
skip-aware application of ANY keytext are independently dead). The two remaining live threads are
external and low-prior: (a) a signed/archival indication a specific text IS the key, or (b) a
correctly-targeted locally-held archive that could contain the lost AN END page. The
ciphertext-only-COMPLETE / external-input-only verdict stands, hardened.

## External avenue — AN-END deep-web page CLOSED 2026-08 (full writeup: `liber-primus/analysis/anend_hunt/FINDINGS.md`)
Round 7's live external thread (b) — the lost AN-END deep-web page (hashes to `36367763…c2a8b4`) —
was pursued with a fresh, correctly-targeted hunt (reachability analysis + address-free hash-scan +
4-lens adversarial OSINT armada, all live-checked 2026-08). **CLOSEABLE.**
- **Unreachable-by-construction:** the 2014 chain's grammar is "each onion's SOLVED content yields the
  next address"; the AN-END target's address is therefore gated behind solving LP2 0-54 (OTP,
  unsolved). No independent address exists in onion7 / AN-END / PARABLE / the 2017 message. The
  `gy3hoy2zizvuzvdb.onion` "lead" is a search-summary hallucination — **do not revive it.**
- **No retrievable in-scope corpus:** Wayback tor2web CDX is empty-of-content even for the KNOWN
  onion7 host and rejects blind (wildcard) queries; DUTA/DUTA-10K, DARPA Memex CDR, LIGHTS, and
  historical Ahmia are each out-of-scope or not publicly downloadable. **Do not re-chase drug-market
  crawls** (topically disjoint — the prior OSINT's mistake).
- **Held corpus is not the pre-image:** representation-axis hash-scan (raw/text/normalized ×
  sha512/sha3_512/blake2b512) over the iBotPeaches onion1-7 chain + the *original* micheloosterhof
  anomalous captures (server-status, index.html.2) = 2,706 tests, CLEAN NULL.
- **Community 2026 (live):** still unfound — CicadaSolvers official "the referenced hash has never
  been found"; `cicada-solvers/Cicada-DWH-HashcatAttempts` 0 matches as of 2025-10-29;
  `tweqx/3301-hash-alarm` never hit; no 7A35090F-signed message since April 2017.
**Do not re-open** as an OSINT/retrieval problem. Residual is passive-monitoring only (watch the two
repo commit feeds + a new 7A35090F message). One record correction: *original* raw 2014 onion captures
DO survive on GitHub (micheloosterhof/cicada-2014, krisyotam cijhho) — "IA copies = re-uploads" was
true of Internet Archive specifically, not the GitHub mirrors; both hash null.

## Round 8 — 2026-08-11 (unexamined-dimension hunt) — 5 tracks, all NEGATIVE
Full writeup + reproduction: `research/ROUND-8-RESULTS.md`; code in
`liber-primus/analysis/{seed_sweep,geometry,skeleton}/`. These tracks are neither
ciphertext-only attacks nor external inputs — they are dimensions of artifacts already in
hand that the program had never measured (keystream ENTROPY, image GEOMETRY, the cleartext
SKELETON, byte-level payload structure).

### KILLED (Gate #2, executed then refuted) — R8-SEED "the pad is a seeded PRNG"
**Mechanism:** every prior round measured keystream *structure* (none) and none measured
keystream *entropy*. A seeded PRNG is indistinguishable from a pad by every test in this
repo yet carries only 31–48 bits of key. Attack = replay the encoder forward from each
candidate seed and score the decrypt.
**Why the earlier Gate-#1 kills do not reach it:** R1-H2's decisive objection (an OTP-class
object admits a valid key for ANY plaintext) is true for unconstrained 29^n keys and FALSE
for a key that is a deterministic function of a ≤2^32 seed — 12,956 runes carry ~32,000
bits of English redundancy against ≤32 bits of key, so the expected number of spurious
English-scoring decrypts is ~0. R1-H3 / R3-H1 / R3-H2 ("collision-skip is un-invertible")
concern decoding WITHOUT the key; with a seed you never decode, you replay the encoder, so
the rejection rule is free (swept as gen 2).
**Harness validated:** glibc random() reproduced EXACTLY against libc (5 seeds x 2000
draws); MT19937, CPython random.seed(int)+randrange/random, and Java Random.nextInt
reproduced exactly against independent implementations. Self-plant recovered 10/10
generator variants (true −11.24 vs wrong-seed −15.8…−16.9), with the documented interrupter
rule honoured by branching over F decisions.
**Why dead:** REFUTED. 10 generator/reduction variants x both directions over unix-second
seeds 2011-01-01..2015-01-01 = **2.52e9 decodes; 0 hits; best score −13.13**, which is the
maximum of the null and 1.5 units below the English 0.1th percentile. Plus 15,408 decodes
over 1,284 lore/string/date seeds x 6 draw methods (CPython hashes str seeds through
SHA-512, so these are unreachable from the integer sweep): **best −14.69, 0 hits**. A full
32-bit sweep of all ten generators appends to `analysis/seed_sweep/results_full32.txt`.
**Do not revive** these generators over these ranges. Genuinely untested residue, stated so
nobody claims more than was done: seeds beyond 2^32 (Java's full 48-bit space, urandom,
multi-word init_by_array), other generators (PHP mt_rand, .NET subtractive, xorshift, RC4),
and a keystream OFFSET other than 0 (the sweep assumes key index 0 = first rune of page 0).
Extend `sweep.c`, do not rewrite it.

### KILLED (Gate #2, executed then refuted) — R8-GEOMETRY "typeset-document stego"
**Mechanism:** STEGO-VERDICT swept FILE-level channels only (appended bytes, EXIF, carve,
LSB, DQT, OutGuess). Its own provenance finding — 400-DPI Ghostscript renders of a PDF —
means these are a TYPESET DOCUMENT, whose canonical covert channels are geometric:
glyph-shape substitution, inter-glyph advance, baseline jitter. Never measured here; the
vision armada tried to READ glyphs, never to COMPARE them.
**Why dead:** REFUTED on all three, on images re-verified 56/56 SHA1 authentic.
- **Shape:** for each of 13,121 full-height glyphs, exact pixel Hamming distance to its
  nearest neighbour among same-(h,w)±1 glyphs. **Median 0.0000 — the median glyph has a
  pixel-identical twin; p90 = 0.0000.** The 82 (0.625%) exceeding 25% of their ink are
  segmentation artifacts (broken strokes / merged blobs), adjudicated by eye in
  `shape_outliers3.png`. Glyph-substitution stego is dead.
- **Advance:** separator-free inter-glyph gaps (n=11,035) — dominant component mean 4.43
  sd 1.63 carrying 89% of mass; two-component separation only **1.86 sigma**, below what a
  1-bit channel needs to be readable. Pitch residual (advance minus the class median,
  removing glyph shape) likewise unimodal.
- **Baseline:** within-class offset sd 4.15 px; a 2-component GMM is **rejected by BIC**
  (delta −22…−25 favouring 1 component).
**Do not revive** typographic micro-spacing, baseline or glyph-substitution stego.
**Traps recorded so they are not re-fallen-into:** an absolute ink-projection threshold
merges a page into 2–3 line bands (ascenders/descenders overlap) — threshold at ~45% of the
median peak; raw ink gaps look strongly bimodal ONLY because word-separator dots were
filtered out of the glyph sequence; comparing a glyph to its size-group modal mask blends
several different runes sharing a bounding box; and uint8 mask subtraction underflows.
**Left open (inventory, not a verdict):** 47 non-text bands across 23 pages are catalogued
in `geometry/geometry_report.json`. Most are mis-segmented text lines; the short ones
(1/3/4/8/16 glyphs) are the only real ornament candidates and nobody has read them.

### KILLED (Gate #2, executed then refuted) — R8-PAYLOAD "the plaintext is binary, not prose"
**Mechanism:** every "no language" verdict here (IoC_norm, quadgrams, CRYPTO-RIGOR §C, R5
ROSETTA) is blind to a COMPRESSED or BINARY plaintext — gzip output has flat IoC by
construction, which is exactly the observed profile. "Flat IoC" had been read as "still
encrypted" when it is equally consistent with "already decoded, but not prose". R5 ROSETTA
was killed because non-English *language* would raise IoC; that argument does not touch a
binary payload.
**Why dead:** REFUTED. The key-free decodes (raw / first-difference / rank-in-28 /
collision-unbump, each also reversed and Atbash-mapped) packed to bytes across base-29 and
base-28 bignum in both digit orders and 5-bit packing in both bit orders at all 8 phases =
**166 representations**, scanned for 40 file magics, PGP/PEM armor, zlib/deflate/gzip
inflation at every offset in the first 4 KB, letter-runs, entropy and chi-square.
**Nothing.** Byte histogram is exactly uniform: entropy 7.977/8.000, **chi2 = 246.7 on 255
df (p ≈ 0.5)**. (Single-byte "magic" hits occur at 1/256 per representation and are noise.)
**Do not revive** container/compression/keyfile readings of the rune stream. Net effect:
"flat IoC" is now backed by a byte-level uniformity measurement, not only by a language
model's silence.

### KILLED (Gate #2, executed then refuted) — R8-POINTERS "residual doublets as an index list"
**Mechanism:** R5 tested the 86 surviving doublets as cipher STRUCTURE (digraphic parity,
doubled-rune identity, gap distribution) and killed all three. An 86-element position list
is also the shape of a book-cipher index, which was never tested.
**Why dead:** REFUTED. Readings tested — doubled rune values as a message; gaps as letters
(mod 26/29, offset −1); gaps and cumulative gaps as word indices into the solved LP1 English
(0- and 1-based); positions as word indices into LP2's own cleartext skeleton; the runes
before and after each doublet; gaps vs primes and Fibonacci. **Best score −16.34 against a
null of mean −16.69 sd 0.244 (2,000 random position sets of the same size); English-class
is ~−12.** Every reading is inside the null.
**Recorded so it is not re-reported as a signal:** doublet positions that are prime = 3/86
vs ~10 expected (p ≈ 0.007 one-sided) — not significant across the ~15 readings tested and
with no mechanism behind it.

### KILLED (Gate #2, executed then refuted) — R8-SKELETON "identify the PLAINTEXT via the cleartext channel"
**Mechanism:** word/clause/line/page boundaries are NOT enciphered, so word length in runes
is a plaintext invariant under any per-rune substitution or additive keystream, INCLUDING a
one-time pad. The information-theoretic wall applies to rune VALUES only. Every keytext
entry in this log concerns a text used as a KEY; this asks whether a known text is the
PLAINTEXT, which needs no key — and a hit would hand over the keystream by subtraction.
**Why dead:** REFUTED for the corpus tested. FFT cross-correlation of LP2's 2,928-word
rune-length sequence against **every** alignment offset in **51 texts / 8,205,104 words**
(the repo's key texts plus 39 canon-relevant works and controls), slack 0 and 1, windows
2928/400/120. **Best real match 19.8% (slack 0) / 49.2% (slack 1) — BELOW the shuffled-LP2
control's own maximum on the same texts (20.0% / 49.1%).** The leaderboard is an ordering
by text length (KJV, Chaucer, Mabinogion, Homer = most offsets = highest max), i.e. the
maximum-of-many effect. A true identification would score near 100%.
**Do not revive** for these 51 texts. DO extend it — the method is cheap and correct; drop
more texts into `analysis/skeleton/corpus/` and re-run `wordlen_search.py`. This eliminates
a corpus, not "all known texts".

### PARSING BUG found and fixed mid-round — affects any word-length work in this repo
`/` in the krisyotam transcription is a **LINE WRAP, not a word separator**: **458 of the
604 line breaks fall MID-WORD**. Treating `/` as a word terminator shatters 458 words into
fragments, yields 3,316 "words" instead of **2,928**, mean length 3.91 instead of **4.425**,
and manufactures a spurious 2x excess of one-rune words. The first pass of this track had
that bug; every number now recorded is from the corrected parse. Anyone reusing the word
skeleton must split on `-` and `.` only.

### LEFT OPEN (the one live thread Round 8 produced rather than closed) — the LP2 word-length excess
LP2's mean rune-word length is **4.425**. English-in-futhorc is 4.10–4.15; Cicada's own
solved LP1 prose is ~4.0. A null interrupter adds one rune to its word, but all 458 F runes
supply only **+0.156 runes/word** against a gap of **+0.32**. Simulating English with
Poisson F-insertion at the full 458 rate still leaves KS 0.039–0.047 vs a 0.025 critical
value. Latin (Caesar, mean 5.72) is far too long and Welsh / KJV / Mabinogion (3.76–3.82)
too short, so the obvious language substitutions do not resolve it. A **separator audit
against the page images** — never done before; all prior transcription checks compared rune
streams only — finds **151/170 rune-exact lines agree exactly (88.8%), mean difference
−0.03 ± 1.10, no systematic bias**, so missing word separators do not explain it either
(`analysis/geometry/separator_audit.py`, 19 candidate lines listed for re-read).
Surviving explanations, none tested: more nulls than the 458 F runes (which would
contradict the documented "only ᚠ is ever a null" rule); a plaintext register with longer
words than narrative prose; a non-English language other than Latin/Welsh; or a
word-boundary convention that differs from the one assumed. This anomaly lives in a channel
no cipher touches, so it is attackable without a key.

## PROGRAM STATUS — UPDATED 2026-08-11 (Round 8)
The ciphertext-only-COMPLETE verdict stands for rune-value cryptanalysis. Round 8 closes
four dimensions that were never ciphertext-only attacks at all — keystream entropy, page
geometry, byte-level payload structure, and the cleartext skeleton — plus the doublet-pointer
reading. The one-time-pad characterisation is now supported by a *measurement of key
entropy* over 2.5e9 candidate seeds rather than only by the absence of key structure.
