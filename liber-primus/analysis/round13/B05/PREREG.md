# Round 13 — B-05 PRE-REGISTRATION

**Written before any sweep was run.** Bounds, thresholds and rejection rules are fixed here;
`RESULTS.md` reports against exactly these numbers.

Lane: RECON-A item **B-05** — *pp49-51's 256-byte payload as a **PRF seed** expanded into a
runic keystream* (never run). Campaign XX applied AES/RC4/ChaCha to the payload as
*ciphertext*; nobody expanded it into a **keystream over the 12,956 unsolved runes**.
Plus RECON-A **A-04** (the 6 contested bytes) as a sensitivity dimension, and RECON-A
**E-02** (payload as meta-parameters) as a zero-false-positive side test.

Trust anchor: `python3 tests/validate.py` from `liber-primus/` = **ALL VALIDATIONS PASSED**
(run 2026-08-18, before writing this file).

---

## H0 / H1

- **H0 (Part 1):** no PRF expansion of the pp49-51 payload, over the enumerated
  {representation × generator × reduction × sign × direction × atbash × offset} grid,
  produces an English-scoring decode of the unsolved LP2 stream under the skip-aware beam.
- **H1 (Part 1):** some expansion does — i.e. the payload is the seed of the pad.
- **H0 (Part 2):** the 6 contested bytes are irrelevant to the above, because no combination
  of their two adjudicated candidate values yields a hit either.
- **H0 (Part 3a):** no 56-byte window of any payload representation is a permutation of 0-55.
- **H0 (Part 3b):** the payload, read as gap values, is uncorrelated with the real
  86-doublet gap sequence.

## Why this is not foreclosed

The iter-6 MDL kill ("exactly incompressible ⇒ not an algorithmically-generated pad") has
**no power here**: a hash/stream-cipher keystream is incompressible by construction.
Round 12 D3 established the same point and passed a plant-recover control for exactly this
decoder path (`round12/D3/pc_derivedkey.py`). Round 8 SEED swept *integer-seeded hobbyist
PRNGs*, not keyed cryptographic keystreams. Campaign XX tested the payload as ciphertext,
not as seed.

## Decoder (mandatory)

**Both** `rigid_decode` and `beam_decode` from `analysis/campaign18_skip/skipdecode.py`.
**Beam is the primary and mandatory instrument** — D3 proved rigid returns noise (-6.8)
even on a *correct* seed under the repo's pinned key-skip filter (supp=0.83), which is
exactly how this family stayed invisible to every prior sweep. Rigid is reported only as
a control channel, never as the decision instrument.

Beam parameters: `beam_w=120, max_skip=3` on a HEAD window of 400 runes for the grid;
survivors re-run full-page (12,956 runes) at `beam_w=400`.

## Part 1 — enumerated grid (fixed before running)

**Seed representations (12)** — the cross of {`canon_256.bin` (majority), `canon_256_decpref.bin`
(decimal-preferred)} × {raw, byte-reversed, per-byte bit-reversed, whole-bitstream-reversed,
32-bit word byte-swap (endianness variant per `characterize.py`), lowercase ASCII hex}.

**PRF generators (15)**
`md5_ctr`, `sha1_ctr`, `sha256_ctr`, `sha512_ctr` (counter mode, `H(seed || ctr_be32)`);
`sha256_ctr_le` (little-endian counter); `sha256_chain`, `sha512_chain` (iterated digest);
`hmac_drbg_sha256` (payload as entropy input, SP800-90A);
`aes256_ctr_k` (key=seed[:32], IV=0), `aes256_ctr_kiv` (key=seed[:32], IV=seed[32:48]),
`aes128_ctr_k` (key=seed[:16], IV=0);
`rc4` (full 256-byte payload as key);
`chacha20_k` (key=seed[:32], nonce=0), `chacha20_kn` (key=seed[:32], nonce=seed[32:48]);
`shake256`.

**Reduction to mod 29 (2):** plain `byte % 29`, and **unbiased rejection sampling**
(accept bytes < 232 = 8×29, reject the rest).

**Sign (2):** ±1 in `p = (c + sign·k) mod 29`.
**Direction (2):** forward keystream, reversed keystream.
**Atbash (2):** `k` and `28 − k`.
**Offset (14):** o ∈ {0, 1, 2, 3, 5, 8, 13, 29, 64, 128, 256, 512, 1024, 3301}.

Grid size: 12 × 15 × 2 × 2 × 2 × 2 × 14 = **40,320 beam decodes** (HEAD=400).

**Secondary constant-shift pass:** the grid above does not include an additive constant.
A restricted pass adds shift s ∈ 0..28 over {2 canonical representations × 15 generators ×
2 reductions × 2 signs × forward × no-atbash × o=0} = 3,480 further decodes.

## Part 2 — contested-byte sensitivity (A-04)

The 6 contested indices (25, 175, 182, 199, 215, 237) each have **exactly two** adjudicated
candidate values on disk — the token-majority value and the scream314 decimal value:

| idx | token/majority | decimal |
|---|---|---|
| 25  | 198 | 224 |
| 175 | 18  | 44  |
| 182 | 167 | 141 |
| 199 | 47  | 21  |
| 215 | 84  | 5   |
| 237 | 32  | 58  |

So the *documented* alternative space is **2^6 = 64 payloads, fully enumerable** — no
combinatorial truncation is needed at the documented level. (`canon_256.bin` and
`canon_256_decpref.bin` are two of the 64 corners.) All 64 are swept over
15 generators × 2 reductions × 2 signs × forward × o=0 = **3,840 beam decodes**.

**Accepted limit, declared in advance:** if the true byte at a contested index is a *third*
value not represented by either witness (an OCR error shared by both token tables), the
enumeration misses it. Sweeping all 256 values at all 6 positions jointly is 256^6 ≈ 2.8e14
and is **not** attempted. A one-position-at-a-time 256-value sweep (6 × 256 = 1,536 payloads,
holding the other 5 at majority) IS run to bound the single-error case; it cannot cover
joint multi-position unknown errors, and that residue is reported explicitly.

## Part 3 — payload as meta-parameters (E-02)

(a) **56-permutation window.** Slide a window of width w ∈ {55, 56, 57} across every payload
representation and test whether the window is a permutation of 0..w−1, both as raw bytes and
as bytes mod w. False-positive probabilities stated exactly in RESULTS.md
(raw: w!/256^w; mod-w: w!/w^w) and Bonferroni-corrected by the number of windows tested.
This is a **zero-false-positive** test by construction.

(b) **Gap correlation.** Read the payload as gap values in 4 encodings (8-bit, 16-bit LE,
16-bit BE, LEB128 varint), at every start offset, and compare against the real doublet gap
sequence from `analysis/skeleton/doublet_pointer_results.json`
(85 gaps, `[85, 249, 197, 129, 127, …]`; also tested with position 122 prepended as the
86-element form the register quotes). Statistics: exact-equality match count (zero-FP), and
Spearman rank correlation vs a 10,000-draw permutation null.

## Positive control (mandatory gate — must PASS before any negative is reported)

`control.py`. Plant a **payload-derived** keystream (`sha256_ctr` over `canon_256.bin`, and
also `rc4` over the payload) onto known English-in-runes, encipher through the repo's pinned
soft key-skip filter (`encipher_keyskip`, supp=0.83, seed=3301). Gate requires **all** of:

1. beam decode under the **correct** payload seed scores ≥ −5.5 and ≥ null_max + 0.5;
2. beam beats **rigid** on the same correct seed by > 1.0 (proves rigid alone is blind);
3. beam under a **wrong** seed stays in noise (correct − wrong > 1.0);
4. char-recovery of the planted plaintext > 0.80.

A sweep that cannot find its own plant proves nothing; if the gate fails, no negative is
published.

**Avalanche sub-control (Part 2's justification):** the same plant is re-decoded with a
payload differing in **one** contested byte. If that single-byte change drops the beam to
noise, contested bytes are load-bearing and must be enumerated — which is what Part 2 does.

## Null and HIT threshold (fixed)

Null: **size-matched shuffle null**, n = **200**. The unsolved HEAD (400 runes) is shuffled
(order-destroying, histogram-preserving) and beam-decoded under a real payload-derived
keystream at rotating offsets. Report **mean and max**.

**HIT bar:** `score_norm ≥ −5.5` **AND** `score_norm > null_max`.
(Higher is better; English ≈ −4.2, project threshold −5.2, noise ≈ −7.5.)
Anything below the bar is reported as NEGATIVE with its coverage stated. No post-hoc
threshold movement.

## Rejection rules

- A config is a candidate only if it clears the HIT bar on HEAD; candidates are then re-run
  full-page and must hold ≥ −5.5 there.
- No result is reported without the control having passed in the same run.
- Coverage is reported as a table of the exact grid dimensions above; anything not in the
  grid is written into the residue section rather than implied to be covered.

## Deliverables

`PREREG.md` (this file), `prf.py`, `sweep.py`, `control.py`, `meta.py`, `results.json`,
`RESULTS.md`. Nothing outside `analysis/round13/B05/` is edited.
