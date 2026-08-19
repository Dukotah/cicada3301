# ROUND 15 / KDF — PRE-REGISTRATION

_Written before the sweep was run. Nothing below was changed after seeing sweep output._
_Trust anchor `python3 tests/validate.py` = **ALL VALIDATIONS PASSED** (run first, 2026-08-19)._

---

## 1. Why this lane exists

Round 13's B-04 sweeps **single-application** cryptographic keystreams: `SHA256(seed ‖ ctr)`,
`h = H(h)`, HMAC-DRBG, AES-CTR, RC4, ChaCha20. Its own pre-registration declares, in §6,
that it does **not** cover:

> *key stretching (PBKDF2 / scrypt / Argon2 / iterated-hash counts > 1) — a seed passed
> through 10⁴ iterations is outside this bound*
> *salted constructions (`H(salt ‖ seed)` for unknown salt)*

That exclusion is the entire subject of this round, and the prior on it is **not low**.

**The argument from period practice.** If you are a cryptographically literate author in
2013–2014 and you want a **reproducible** full-length pad derived from a secret you can
remember or write down once, you do not use a bare hash. Using a bare hash for
passphrase-derived key material was, by then, a decade-old and widely-taught mistake. The
standard answer — in PGP's String-to-Key, in TrueCrypt, in OpenSSL's `EVP_BytesToKey`, in
WPA2, in every "how to derive a key from a passphrase" answer of the era — is a **KDF with an
iteration count**. Cicada's own artifacts are steeped in exactly that culture: the puzzles
are built on PGP, RSA, OutGuess and Tor.

So the construction this round tests is not an exotic addition to the search space. Within the
"derived keystream" hypothesis that D3 proved the ciphertext cannot exclude, it is arguably
**more** plausible than the bare-hash family B-04 is sweeping — and no one has ever run it.

**Why it would have been invisible.** A KDF is designed so that its output is
computationally unrelated to its input. `PBKDF2(seed, salt, 10000)` and `SHA256(seed)` share
no detectable statistical relationship, so a null over one says nothing at all about the
other. No result in this repository constrains this family, and the iter-6 MDL kill
("incompressible ⇒ not algorithmically generated") has no power here for the same reason it
has none over B-04: a KDF stream is incompressible by construction.

---

## 2. Hypothesis

**H1.** The LP2 keystream is derived from a short secret via a **key-stretching function** —
PBKDF2 (HMAC-SHA1/SHA256/SHA512), scrypt, or plain iterated hashing at a count > 1 — optionally
**salted** with a Cicada-flavoured constant, then expanded to 12,956 symbols, reduced mod 29,
and applied under the pinned soft anti-repeat filter.

**H0.** No (secret, KDF, iteration count, salt, reduction, sign, direction, offset) in the
enumerated bound of §4 produces English.

**Falsifiability.** H1 is falsified **over the enumerated bound only**. Iteration counts, salts
and secrets outside §4 remain untested, and a negative here must be reported that way.

---

## 3. Instrument

Decoder: `analysis/campaign18_skip/skipdecode.py` — `beam_decode` (skip-aware) with
`rigid_decode` recorded alongside as contrast, never as the decision statistic.

**Beam is mandatory, for the reason D3 established.** On the *correct* seed, rigid alignment
returns −6.835 (indistinguishable from noise) while the beam returns −4.170 at 98.9%
char-recovery. Any KDF sweep run rigidly would produce a guaranteed false negative — the same
structural blindness that made the entire pre-Round-12 seed-sweep programme unable to succeed.

**Sign convention.** `score_norm` is a per-quadgram log-probability: negative, and **higher is
more English**. English solves ≈ −4.0…−4.5; noise ≈ −7.5. A hit means `score_norm ≥ bar`.

---

## 4. Exact search bounds (locked)

### 4.1 Secrets — the B-04 `core` dictionary (504 entries) plus a passphrase set

KDFs are ~10³–10⁵× more expensive per derivation than a bare hash, so the secret list is the
**core** subset rather than B-04's full 2,165, plus a set of multi-word **passphrases** that a
bare-hash sweep had no reason to include but a KDF sweep must: the koan lines, the slogans as
sentences, and the signed-message phrases — with and without spaces, upper and lower.

### 4.2 KDFs and iteration counts

| family | parameters |
|---|---|
| `pbkdf2_sha1` | iterations ∈ {1000, 2048, 4096, 10000, 100000} |
| `pbkdf2_sha256` | iterations ∈ {1000, 2048, 4096, 10000, 100000} |
| `pbkdf2_sha512` | iterations ∈ {1000, 4096, 10000} |
| `scrypt` | N=16384, r=8, p=1 (the RFC 7914 "interactive" parameters) |
| `iterated_sha256` | rounds ∈ {1000, 10000, 100000, 3301} |
| `iterated_md5` | rounds ∈ {1000, 10000, 3301} |
| `openssl_evp_bytestokey` | MD5 and SHA256, 1 and 3301 rounds — the `EVP_BytesToKey` construction, period-ubiquitous |

**Iteration-count choices are pre-registered, not fitted:** 1000/2048/4096/10000 are the era's
defaults (PKCS#5 minimum, TrueCrypt, WPA2, common tutorials); 100000 is the modern-leaning
upper end; **3301** is included in every family because this author signs everything with it.

**Argon2 is deliberately EXCLUDED**: it won the Password Hashing Competition in **2015**, after
LP2 was published in 2014. Including it would be anachronistic. This is recorded here so its
absence reads as a decision rather than an oversight.

### 4.3 Salts

`b""` (empty) · `b"3301"` · `b"cicada"` / `b"CICADA"` / `b"Cicada"` · `b"cicada3301"` ·
the 2014 onion address · `b"1033"` · `b"761"` · the secret itself (salt = password, a common
lazy construction) · the AN-END hash first 16 bytes.

### 4.4 Expansion, reduction, and application

Each KDF yields 64 bytes of key material; the full 12,956-symbol keystream is expanded from it
by SHA-256 counter mode (the standard "derive then expand" shape, and the same expander B-04's
control validated). Reductions: `mod29` and unbiased `rej29`. Signs ∈ {−1, +1}. Direction ∈
{forward, reversed}. Atbash ∈ {off, on}. Offsets ∈ {0, 1, 29, 3301}.

### 4.5 Declared budget and staging — measured, not guessed

KDF cost was **measured before the sweep was designed** (`kdf.py` timing run, 2026-08-19):
one full 27-KDF pass over a single (secret, salt) pair costs **≈602 ms**, dominated by
`pbkdf2_sha1_100000` (160 ms), `scrypt` (141 ms) and `iter_sha256_100000` (122 ms). The full
504 × 11 × 27 cross product is therefore ~150k derivations ≈ 55 core-minutes of pure key
derivation before a single decode. The staging below is chosen to fit that, and the reduction
is declared here rather than applied silently.

| stage | secrets | KDFs | salts | reductions | sign × atbash × dir | offsets | decodes |
|---|---|---|---|---|---|---|---|
| **A** — broad screen, 120-rune head | 504 core + passphrases | 27 | **3** (`empty`, `3301`, `self`) | 2 | 2×2×2 | {0} | ≈650k |
| **B** — salt expansion, on the KDF families surviving A | 504 core | top families | **all 11** | 2 | 2×2×2 | {0, 1, 29, 3301} | as needed |
| **C** — escalation | survivors only | | | | | | page 0 full, then all 12,956 |

**The three Stage-A salts are pre-registered choices, not conveniences.** `empty` is the
default of every naive implementation; `3301` is this author's signature constant; `self`
(salt = password) is the single most common lazy construction in hand-rolled code. If the
construction is salted with something more imaginative, Stage A will miss it and Stage B is
where that is caught — but only for KDF families that Stage A flags, which is a real limit
and is recorded as such in §7.

---

## 5. Positive controls — BOTH must PASS before any null is trusted

**K1 — the expander is sound.** Re-run `round12/D3/pc_derivedkey.py`. Required: beam(correct)
≥ −5.5, char-recovery ≥ 0.90, rigid(correct) < −6.0.

**K2 — plant-and-recover through THIS harness, at real Stage-A settings.** Plant a keystream
derived by `PBKDF2-HMAC-SHA256(secret, salt, 10000)` from a secret **genuinely resident in the
dictionary**, expand it, encipher LP-style English under `encipher_keyskip(sign=-1, supp=0.83,
seed=3301)`, then run the **full Stage-A cross product** against that synthetic ciphertext.
Required: the planted (secret, kdf, iterations, salt, reduction, sign, atbash, direction)
config ranks **#1** and clears the §6 bar.

**If either gate fails, the result is INCONCLUSIVE, not NEGATIVE.** This is the check the
entire pre-Round-12 seed programme omitted, and it is why that programme could not have
succeeded even had it been right.

---

## 6. Decision threshold (fixed in advance)

**HIT** iff `score_norm ≥ HIT_BAR`, where `HIT_BAR = max(-5.5, null_max + 0.5)` and `null_max`
is the maximum of a size-matched shuffle null (n=200, histogram-preserving, `Random(3301+k)`)
decoded exactly as the sweep decodes.

**Scale correction, stated in advance.** The −5.5 floor is calibrated for sweeps of ~10⁶
decodes. This sweep is smaller (KDF cost bounds it), so the floor binds and no correction is
needed — but the sweep's own empirical score distribution is reported as the honest best-of-N
ceiling regardless, and any candidate must be an outlier from *that*, not merely above −5.5.

**Escalation.** Any config at `score_norm ≥ -5.5` is re-decoded on (a) full page 0, (b) the
whole 12,956-rune stream, (c) from a clean process. It is called a HIT only if it survives all
three and yields readable English across **more than one page**.

---

## 7. What this round explicitly does NOT cover

- iteration counts outside §4.2, and any count chosen to be memorable that is not 3301
- salts outside §4.3, and per-page or position-varying salts
- Argon2 and bcrypt (the first is anachronistic; the second has no natural long-output mode)
- expanders other than SHA-256 counter mode over the derived block
- multi-stage constructions (KDF feeding a stream cipher feeding another KDF)
- **salts beyond the three screened in Stage A, for KDF families that Stage A does not flag.**
  Stage B expands the salt list only over surviving families, so an exotic salt paired with a
  family that screens as noise under the three default salts is outside this round's bound.
- secrets outside the core dictionary + passphrase set
- filters other than the pinned soft key-skip at supp = 0.83

A negative closes §4 and nothing more.
