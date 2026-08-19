# ROUND 13 / B-04 — the derived-key dictionary. VERDICT: **NEGATIVE**

_Pre-registration: [`PREREG.md`](PREREG.md), written before any code ran. Gate corrections:
[`GATE-NOTE.md`](GATE-NOTE.md). Completed 2026-08-19._

## Why this lane existed

RECON-A item **B-04**, marked `never-run` since 2026-08-12 and foreclosed for months by a
verdict line reading *"internal solve frontier EXHAUSTED"* that was **false when written**.

Round 12's front D3 established the opening: the ciphertext **cannot distinguish** a true
external one-time pad (information-theoretically closed) from a keystream **derived from a
short seed** (finite, enumerable, brute-forceable). One member of that class is unsolvable;
the other is a search problem. Only running the dictionary settles which.

## Gates — both PASS

| gate | result |
|---|---|
| **G1** — replicate D3's control | beam(correct) **−4.170**, rigid(correct) −6.835, beam(wrong) −7.349, char-recovery **98.9%**. PASS |
| **G2** — plant-and-recover through *this* harness at full Stage-A settings | planted dictionary-resident seed `THE PRIMES ARE SACRED` ranks **#1 at −4.186**, reading `THEPRIMESARESACREDANDTHETOTIENTFUNCTIONI…` in clear; runner-up noise **−6.621**. PASS |

G1 initially reported a false FAIL from a key-alias bug in the gate reader; see `GATE-NOTE.md`
for the corrected numbers and why the run's own `results_summary.json` may carry a stale label.

**Because both gates pass, the null below is a real negative rather than an unknown.**

## Coverage actually executed

| stage | what | decodes | best | over bar |
|---|---|---|---|---|
| **A** | 2,165 seeds × 16 generators × 5 reductions × sign × Atbash × direction, offset 0 | 1,385,600 | −6.185 | **0** |
| **B** | 504 core seeds × 10 keystream offsets | 1,290,240 | −6.129 | **0** |
| **C** | 504 core seeds × 55 per-page keystream restarts | 3,548,160 | −5.885 | **0** |
| **D** | escalation of the top 150 distinct configs onto full page 0, then all 12,956 runes | 300 | −6.654 / −7.239 | **0** |
| | **total** | **6,224,300** | | **0** |

HIT bar: **−5.500**. Nothing came within 1.2 of it.

## The distribution is the result, not the maximum

Stage A's own score histogram: mean **−7.344**, sd 0.231, p99.999 **−6.35**. The best score of
1.4 M decodes landed at −6.185 — precisely where the best-of-N order statistic of a null should
land. Stage C's −5.885, the highest of the campaign, is likewise the expected maximum of 3.5 M
draws, not a signal. The top seeds at that extreme (`anend`, `LIBER`, `mit`, `email`) are
lottery winners, not meaning.

**Stage D is the decisive check, and it is unambiguous.** Escalating the 150 best configs onto
longer text: **0 of 150 improved** on page 0, and **0 of 150 improved** on the full stream,
where the best fell from −6.654 to −7.239. A correct key gets *better* as more text is added;
a lucky one decays toward the noise mean. Every survivor decayed.

## What this closes — and what it does not

**Closes:** single-application cryptographic keystreams from a 2,165-entry Cicada seed
dictionary — SHA-1/256/512 counter and chain, HMAC counter-KDF, HMAC-DRBG, AES-CTR, RC4,
ChaCha20 — reduced to Z₂₉ by five methods, under the pinned soft anti-repeat filter, at the
offsets and per-page restarts tabulated above.

**Explicitly NOT covered** (declared in PREREG §6, before the run):
- **key stretching** — PBKDF2 / scrypt / iterated hashing > 1 round. *This is Round 15's KDF
  lane, and the argument from period practice makes it arguably a higher prior than the
  bare-hash family swept here: a crypto-literate author in 2013–14 deriving a reproducible pad
  from a memorable secret would reach for a KDF, not a bare hash.*
- salted constructions `H(salt ‖ seed)` for unknown salt
- seeds outside the 2,165-entry dictionary
- offsets beyond 3301; non-integer or per-line restarts
- filters other than the pinned soft key-skip at supp = 0.83
- composite plaintext transforms

## Consequence for the top-line verdict

The derived-key branch is **narrowed, not eliminated**. LP2 remains **OTP-class**: the
ciphertext still cannot separate a true pad from a derived keystream, and this campaign has
removed one large, well-specified region of the derived branch without touching the rest.

Do not read this as evidence for "unsolvable by design". It is evidence that *this* region is
empty.

## Artifacts

`PREREG.md` · `GATE-NOTE.md` · `sweep.py` · `harness.py` · `ks.py` · `seeds.py` · `control.py` ·
`results_{gates,A,B,C,D}.json` · `results_G1_rerun.json` · `sweep.log`

Reproduce: `cd liber-primus/analysis/round13/B04 && python3 sweep.py --nproc 6`
