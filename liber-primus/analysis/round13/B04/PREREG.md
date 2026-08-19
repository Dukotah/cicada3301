# ROUND 13 / B-04 — PRE-REGISTRATION

_Written before the sweep was run. Nothing below was changed after seeing sweep output.
Agent R13-A. Trust anchor: `python3 tests/validate.py` = **ALL VALIDATIONS PASSED**
(run first, 2026-08-18)._

---

## 1. Hypothesis

**H1 (the claim under test).** The LP2 0–54 keystream is not a true external one-time pad
but a **cryptographic keystream derived from a short, Cicada-flavoured seed** — MD5 /
SHA-1 / SHA-256 / SHA-512 (chain or counter), HMAC counter-KDF, HMAC-DRBG, AES-CTR, RC4 or
ChaCha20 — expanded, reduced to Z₂₉, and applied additively under the repo's pinned soft
anti-repeat (key-skip) filter.

**H0 (the null).** No seed in the enumerated dictionary, under any enumerated
generator/reduction/sign/direction/offset, produces English.

**Why this is the one live lane.** Round 10b's B4/G5 result shows the ciphertext *cannot*
separate a true external pad from a short-seed-derived keystream (`separated:false`,
max |z| = 1.60 over the 6-stat battery). One member of that indistinguishability class is
information-theoretically closed; the other lives in a **finite, enumerable keyspace**. The
top-line verdict promoted the first to the whole class. RECON-A B-04 is marked `never-run`.
Round 8's "2.52e9 decodes" covered *hobbyist integer-seeded PRNGs*, never keyed hash /
stream-cipher keystreams; and the iter-6 MDL "incompressible ⇒ not algorithmically
generated" kill has **no power** here (a hash keystream is incompressible by construction).
Only running the dictionary settles it.

**Falsifiability.** H1 is falsified *over the enumerated bound only*. A negative here does
not close the derived-key family — it closes the region tabulated in §3.

---

## 2. Instrument and why RIGID alone would be a false negative

Decoder: `analysis/campaign18_skip/skipdecode.py` — `beam_decode` (skip-aware) and
`rigid_decode` (classic 1:1). Scorer: `Q.score_norm` / `nc.eng_norm`.

**Sign convention (fixed here to avoid ambiguity):** `score_norm` is a per-quadgram
log-probability. It is **negative, and HIGHER (closer to zero) is MORE English**. On this
repo's scale: genuine English solves ≈ **-4.0 … -4.5**, campaign threshold **-5.2**, noise
floor ≈ **-7.5**. So a hit means `score_norm ≥ bar`, not `≤`.

D3's control (`analysis/round12/D3/pc_derivedkey.py`) shows that on the **correct** seed the
rigid decoder returns **-6.835** (indistinguishable from noise) while the beam returns
**-4.170** at 98.9 % char-recovery. **Every prior seed sweep in this repo used rigid
alignment.** Running rigid only would therefore manufacture a guaranteed false negative.
**Beam is mandatory** and is used for every decode reported here; rigid is recorded
alongside as the contrast, never as the decision statistic.

---

## 3. Exact search bounds (locked)

### 3.1 Seed dictionary — `seeds.py`, **2,165** distinct seed byte-strings
(`core` subset = **504**, used for the deeper offset / per-page stages)

| family | n | content |
|---|---|---|
| `lp_word` | 756 | every ≥3-letter word of the solved LP plaintexts, the 2012–2014 puzzle texts and the Cicada PGP messages, UPPER and lower |
| `lp_line` | 500 | every distinct line of those texts (4–120 chars), as-written / UPPER / lower / de-spaced |
| `lore_file` | 267 | book-title & author tokens from the 87-text lore key corpus filenames |
| `slogan` | 139 | Cicada slogans and koan phrases (THE PRIMES ARE SACRED, AN END, THEIR NUMBERS ARE THE DIRECTION, …) |
| `lore` | 138 | book titles / author names in the lore (Mabinogion, Agrippa, Liber AL vel Legis, King in Yellow, Self-Reliance, …) |
| `onion` | 132 | every onion address of the 2012–2014 chain — bare, with scheme, with/without `.onion`, both cases |
| `thematic` + `solvedkey` | 70 | the canonical solved-page keywords: DIVINITY, CIRCUMFERENCE, FIRFUMFERENFE, INSTAR, WELCOME, MOBIUS, ADHERE, PILGRIM, TOTIENT, … |
| `num_*` | 124 | 3301 and variants, 1033, 761, 845145127, 1595277641, 29, dates as strings and as epoch integers — decimal-ASCII **and** raw big/little-endian 2/4/8-byte forms |
| `primes_*` | 12 | first 5/10/15/29 primes as CSV, concatenated digits, and raw bytes |
| `anend_*` | 6 | the AN END 512-bit hash `36367763…c2a8b4` — ASCII hex (both cases), **raw 64 bytes**, reversed, and each 32-byte half |
| `canon256_*` | 7 | `analysis/pp49_51/canon_256.bin` (this is RECON-A **B-05**) — raw 256 bytes, reversed, head/tail 32, ASCII hex, dec-pref variant |
| `pgp*` | 14 | fingerprint `6D854CD7…7A35090F`, key id `7A35090F`, long id, the spaced fingerprint, the "Cicada 3301 (845145127)" uid, and raw-byte forms |

### 3.2 Generators — **16** (`ks.py`)

`sha256_ctr`, `sha512_ctr`, `sha1_ctr`, `md5_ctr` (counter = 4-byte big-endian appended);
`sha256_ctr_le` (little-endian counter), `sha256_ctr_asc` (ASCII-decimal counter);
`sha256_chain`, `sha512_chain`, `sha1_chain`, `md5_chain` (h = H(h), emit);
`hmac_sha256_ctr` (NIST SP800-108 counter KDF: HMAC(key=seed, msg=ctr));
`hmac_drbg_sha256` (NIST SP800-90A, instantiate-then-generate);
`rc4` (pure-Python ARC4 keystream, key = seed bytes);
`aes_ctr_zeroiv` and `aes_ctr_deriviv` (key = SHA-256(seed); IV = 0 / MD5(seed));
`chacha20` (key = SHA-256(seed), zero nonce).

### 3.3 Reductions to Z₂₉ — **5**

`mod29` (`b % 29`); `rej29` (**unbiased rejection sampling** — keep `b < 232 = 8·29`, then
`% 29`; this is the form a careful author would use); `hi_nib` (`(b>>4) % 29`);
`lo_nib` (`b & 15`); `bits5` (5-bit groups off the bit stream, rejecting 29–31).

### 3.4 Direction / sign / reflection

* sign ∈ {−1, +1} — key **subtracted** and key **added**
* keystream direction ∈ {forward, reversed}
* Atbash ∈ {off, on} — applied as the plaintext-alphabet reflection `i ↦ 28 − i`
  (implemented on the ciphertext, which with both signs swept is the exact equivalent)

### 3.5 Offsets

Stage A pins offset 0 (an author aligning the keystream to rune 0 of page 0).
Stage B sweeps offset ∈ {1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301}.
Stage C tests **per-page keystream restarts** (offset 0 at the head of each of the 55 pages).

### 3.6 Stages and decode budget

| stage | segment | seeds | gens | reds | sign | atbash | dir | offsets/pages | decodes |
|---|---|---|---|---|---|---|---|---|---|
| A — broad screen | unsolved head, L=120 | 2165 | 16 | 5 | 2 | 2 | 2 | 1 | **1,385,600** |
| B — offsets | unsolved head, L=120 | 504 core | 16 | 2 (mod29, rej29) | 2 | 2 | 2 | 10 | **1,290,240** |
| C — per-page restarts | each page head, L=min(100,len) | 504 core | 16 | 2 | 2 | 2 | 1 (fwd) | 55 pages | **3,548,160** |
| D — deepen survivors | page 0 full (262), then all 12,956 | top 300 configs of A/B/C | | | | | | | ≈ 300 + escalation |
| | | | | | | | | **total** | **≈ 6.22 M** |

Beam settings fixed for all stages: `beam_w = 400`, `max_skip = 3`, matching D3's control.

---

## 4. Positive controls (both must PASS before any sweep result is trusted)

**G1 — replicate D3.** Re-run `round12/D3/pc_derivedkey.py` verbatim. Required:
beam(correct seed) ≥ -5.5, char-recovery ≥ 0.90, beam(correct) − beam(wrong) > 1.0,
rigid(correct) < -6.0.

**G2 — plant-recover through MY OWN harness (the stage-A screen at its real settings).**
Plant a keystream from a seed that is **actually resident in the dictionary**
(`b"THE PRIMES ARE SACRED"`, family `slogan`) over L=120 runes of LP-style English,
encipher with `sk.encipher_keyskip(sign=-1, supp=0.83, seed=3301)`, then run the **full
Stage-A cross product** (all 2,165 seeds × 16 × 5 × 2 × 2 × 2) against that synthetic
ciphertext. Required: the planted `(seed, generator, reduction, sign, atbash, direction)`
config ranks **#1** and clears the HIT bar of §5. A screen that cannot find a planted seed
proves nothing, and this is exactly the check every prior seed sweep omitted.

If either gate fails, the sweep is reported as INCONCLUSIVE, not NEGATIVE.

---

## 5. Decision threshold (fixed in advance)

Primary statistic: `beam_decode(...)["score"]` = `score_norm` of the recovered
transliteration.

**HIT** iff

&nbsp;&nbsp;&nbsp;&nbsp;`score_norm ≥ HIT_BAR`, where `HIT_BAR = max(-5.5, null_max + 0.5)`

with `null_max` = the maximum over a **size-matched shuffle null, n = 200**: shuffle the
segment (histogram-preserving, order-destroying, `random.Random(3301+k)`) and beam-decode it
under a B-04-family keystream, exactly as the sweep does. This is A1's and D3's null and
bar, unchanged.

Measured in advance (n=200, `sha256_ctr`/`mod29`, offset 0):
`L=120 → mean -7.366, max -6.826` ⇒ **HIT_BAR = -5.5** (the -5.5 floor binds).
`L=100 → mean -7.342, max -6.761` ⇒ **HIT_BAR = -5.5**.

**FP-ceiling caveat, stated in advance.** A 200-draw null max is *not* the order statistic of
a 6.2-million-decode best-of. The sweep's own empirical score distribution — 6.2 M decodes
all of which are presumed wrong under H0 — is therefore reported as the honest
best-of-N ceiling, and any candidate must also be an outlier from it. A "hit" that merely
matches the sweep's own maximum is noise.

**Escalation rule for a candidate.** Any config with `score_norm ≥ -5.5` is re-decoded on
(a) the full 262-rune page 0, (b) the full 12,956-rune unsolved stream, and (c) from a clean
process. It is only called a HIT if it survives all three and yields readable English across
**more than one page**.

**Outcome labels.**
* **HIT** — a config clears the bar and survives escalation.
* **NEGATIVE** — both gates PASS and the best score over the whole enumerated bound is
  below the bar. Meaning: H1 is false *over the tabulated region*, no more.
* **INCONCLUSIVE** — a gate fails, or the run does not complete its stated bound.

---

## 6. What this run explicitly does NOT cover (declared in advance)

* seeds outside the 2,165-entry dictionary (in particular: passphrases, non-English seeds,
  seeds with punctuation/whitespace variants beyond the 4 emitted forms, and any seed the
  author never wrote down in public)
* key stretching (PBKDF2 / scrypt / Argon2 / iterated-hash counts > 1) — a seed passed
  through 10⁴ iterations is outside this bound
* salted constructions (`H(salt ‖ seed)` for unknown salt)
* offsets beyond 3301 and non-integer / per-line restarts
* filters other than the pinned soft key-skip at supp = 0.83 (in particular the
  **value-rewrite** filter form, which RECON-B/B-16 flags as never validated)
* composite plaintext transforms (interrupters, page-order permutations, atbash-on-key)
