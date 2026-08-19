# ROUND 13 / B-05 — the pp49–51 payload as a PRF seed. VERDICT: **NEGATIVE**

_Ran 2026-08-18/19. Pre-registration: [`PREREG.md`](PREREG.md). Trust anchor
`tests/validate.py` = ALL VALIDATIONS PASSED._

## What was tested

RECON-A item **B-05**, marked `never-run` since 2026-08-12. Pages 49–51 carry a 256-byte
non-runic payload. Campaign XX applied AES/RC4/ChaCha to that payload **as ciphertext**;
nobody had ever **expanded it into a keystream** over the runes. Those are different
hypotheses, and a null over one says nothing about the other.

## Positive control — PASS (this is what makes the null trustworthy)

`control.py`, all four generator families. A payload-derived keystream was planted, the
plaintext enciphered under the pinned soft anti-repeat filter, and the beam decoder asked to
recover it:

| channel | score |
|---|---|
| beam, correct seed | **−4.170** (98.9% char recovery) |
| beam, wrong seed | −7.33 |
| rigid, correct seed | −6.68 … −7.48 (**noise — on the CORRECT seed**) |
| one contested byte flipped | **−7.38** |

Two things worth extracting. First, the rigid row reproduces the structural blindness again:
a rigid sweep of this family would have returned a guaranteed false negative. Second, the
last row measures **avalanche sensitivity** directly — flipping a single byte of the seed
collapses recovery from perfect to noise, which is exactly why the contested bytes below had
to be swept rather than assumed.

## Bound actually covered

| part | what | decodes |
|---|---|---|
| 1 | Payload representations (raw, reversed, bit-reversed, byte-swapped, dec-prefix, hex-ASCII) × {SHA-256/512 ctr and chain, SHA-1/MD5 ctr, HMAC-DRBG, AES-CTR, RC4, ChaCha20} × {mod29, rejection} × sign × direction × Atbash × offsets | 43,800 |
| 1b | constant-shift pass | — |
| 2a | all 64 combinations of the 6 contested bytes | 3,840 |
| 2b | **single-position 256-value sweep** at each contested index (25, 175, 182, 199, 215, 237) | 23,040 |
| — | rigid control channel (180 corners) | — |
| — | full-page rerun of the top-5 Part-1 configs | — |
| | **total beam decodes** | **70,680** |

## Result

| quantity | value |
|---|---|
| best overall | **−6.745** (Part 2b) |
| best Part 1 | −6.771 |
| null (n=200, HEAD) | mean −7.302, **max −7.001** |
| HIT bar | −5.500 |
| **hits** | **0** |

The best configuration is **1.25 below the bar and 0.26 above the null maximum** — inside the
noise band. The rigid control channel peaked at −7.096, confirming the beam is what carried
the test.

**The escalation check is the informative part.** The top-5 head configs were re-decoded on
the full page: every one got *worse* (−7.22 … −7.33 against heads of −6.77 … −6.86). That is
the signature of an order statistic rather than a signal. A real key improves as more text is
added; a lucky one degrades. Anyone tempted by a marginal score should run this check before
anything else.

## What this closes, and what it does not

**Closes:** the payload-as-PRF-seed lane over the tabulated region, *including* the
contested-byte sensitivity that PREREG flagged as potentially making the lane unsettleable.
Part 2b swept all 256 values at each of the six contested positions independently, so a
single mis-transcribed byte can no longer be hiding the answer.

**Does not close:** joint corruption of **two or more** contested bytes (only single-position
and the 64 all-combinations masks were run), key stretching applied to the payload (that is
Round 15's KDF lane), salted expansion, and expanders other than the tested set.

**Ledger effect:** RECON-A B-05 moves `never-run` → `negative`, with a passing positive
control. RECON-A **A-04** (the 6 contested bytes) is materially weakened as a blocker — it
still matters for other lanes, but it no longer blocks B-05.
