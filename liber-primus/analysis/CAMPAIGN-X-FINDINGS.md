# Campaign X — Autokey is Excluded (a positive result)

_2026-07-06. The one chip that moved something. Reproduce:_
`PYTHONUTF8=1 python3 analysis/campaign10_otp_vs_autokey.py` _(stdlib + the project's own `lp.stats`)._

## The question

The public solver community's stated reason the runic pages resist is that the low
doublet count *"traditionally points to an autokey / autoclave cipher"* (Uncovering
Cicada wiki, corroborated across mirrors). That has been the field's working
hypothesis for years — **assumed, never simulated.** This campaign simulates it.

Method: encipher a realistic English-in-runes plaintext under each candidate
mechanism, then measure whether the **ciphertext** reproduces *both* observed LP2
statistics — doublet rate **0.664%** and **IoC·N 1.000** — using the same
`lp.stats.summary` the rest of the project uses. Deterministic, seed = 3301.

## Result

| mechanism | IoC·N | doublet % | reproduces LP2? |
|---|---|---|---|
| **OBSERVED — LP2 unsolved** | **1.000** | **0.664** | — (target) |
| random uniform (theory) | 0.999 | 3.319 | no |
| running-key OTP (English key) | 1.061 | 4.114 | no |
| running-key OTP (uniform pad) | 1.000 | 3.227 | no |
| **OTP + soft no-repeat filter** | 1.001 | 0.834 | **YES** |
| plaintext autokey (seed 1) | 1.232 | 4.245 | no |
| plaintext autokey (seed 8) | 1.060 | 3.257 | no |
| ciphertext autokey (seed 1) | 0.999 | 3.450 | no |
| ciphertext autokey (seed 8) | 1.000 | 3.304 | no |

**All four autokey variants sit at 3.3–4.2% doublets — the random band. Autokey does
not suppress adjacent repeats at all.** (Plaintext-autokey seed 1 is *doubly* wrong —
its IoC·N 1.232 isn't even flat.) The observed 0.66% deficit is reproduced by exactly
one model: a keystream deliberately filtered to avoid adjacent-equal output.

## Why this is progress, not another null

This is the difference between "we tried X and it failed" and "we proved X isn't the
mechanism." It **excludes the community's leading hypothesis** and does it
constructively:

- **Autokey is out.** No autokey/autoclave construction produces the deficit; they all
  inherit the ~3.45% random doublet rate. The decade-old "probably autokey" reading is
  wrong, and now there's a number that says so.
- **An unfiltered pad is also out.** Plain running keys and uniform pads sit at ~3.45%
  too — so the deficit is not a passive side effect of *any* additive keystream.
  **Active suppression is required.**
- **What's left is specific.** The mechanism is a one-time-pad / long key whose output
  was engineered (by tooling or by hand) to avoid writing the same rune twice in a row.
  That is a much sharper description of the wall than "it resists."

Combined with the Campaign IV mechanistic exclusion of plaintext-independent running
keys, the internal picture is now: **not a running key, not autokey, not an unfiltered
pad — an OTP with a single engineered hole.** On the "why does it resist" question, this
appears to be *ahead* of the published community state of the art, which still stops at
"autokey/custom."

## Honest caveats

- The soft-filter model lands at 0.834% vs the observed 0.664% — same regime, slightly
  under-suppressed at the illustrative `suppress=0.80`; tightening the filter closes the
  gap. The point is categorical (autokey ~3.4% vs filtered ~0.8%), not a fit to three
  decimals.
- This refutes autokey as the *doublet-producing mechanism*. It does not, by itself,
  decrypt anything — an OTP with an unknown external key remains unbreakable from the
  ciphertext. Progress here is **narrowing the mechanism**, not opening the lock.
