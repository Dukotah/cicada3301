# Liber Primus — findings for fellow solvers

A concise, reproducible summary of what this project established about the
**unsolved** Liber Primus pages (LP2 0–55). Everything here is backed by code in
this repo (run `tests/validate.py` to confirm the rig reproduces all solved
pages first). Shared so others don't re-run the dead ends.

## Statistical profile (reproducible: `analysis/run_stats.py`)
Over 12,956 unsolved runes:
- **IoC·N = 1.000** — *perfectly* flat. Not "near random": at the random floor.
- **Doublet rate = 0.66%** vs 3.45% random — a ~5× deficit.
- **Consecutive differences** `c[i]−c[i−1]` are flat-random **except a hole at 0**.
- Entropy 4.857 / 4.858 bits.

## What we eliminated (with the reason it's ruled out)
- **Every periodic key, any length 1–40** — column-wise frequency (Friedman)
  attack, both directions + Atbash. Best score −5.8 (gibberish). Validated to
  recover a known 7-symbol key from synthetic ciphertext. `attack.py vigauto`.
- **Running keys** from the actual referenced texts (Mabinogion, Self-Reliance,
  King in Yellow, Book of the Law, Agrippa) and the solved-page plaintext —
  all offsets, both directions, +Atbash. Nothing. `attack.py runningkey`.
- **Number-theoretic keystreams** — primes, totient(prime), φ(n), iterated
  totient, prime gaps, cumulative sums, page-seeded, all Fibonacci-mod-29 seeds.
  Nothing. `attack.py keystream` + `analysis/doublet_probe.py`.
- **Plaintext & ciphertext autokey** — refuted; the differences are flat-random,
  so nothing English hides under integration. `src/lp/autokey.py`.
- **First-difference / integral inversion** — integrating raises doublets to a
  normal 3.55% (so the deficit IS a differencing artifact) but the underlying
  stream stays flat-random. No plaintext. `analysis/armada/FOLLOWUP-TESTS.md`.
- **Page-on-page key reuse** — no two pages show a shared-keystream difference
  signal (and English−English difference IoC is only ~1.03, so the test is weak).
- **Fractionation (bifid)** — every period gives doublet 3.6–4.6% and IoC·N
  1.39–1.55; it cannot reach the observed flat 1.00 or the deficit. Ruled out.
- **Substitution / homophonic / transposition-only** — substitution preserves
  IoC (can't turn flat→English); transposition is doublet-transparent.

## The load-bearing conclusion
Perfect IoC flatness (1.00) is only achievable by a **full-length keystream**
(one-time-pad-class); fractionation/substitution top out around 1.4–1.5. Combined
with the doublet deficit (a deliberate no-consecutive-repeat constraint) and the
exhaustive key-search failure, the unsolved pages are **information-theoretically
underdetermined without the key** — for any chosen plaintext a valid structureless
key exists (`analysis/SOLVE-ATTEMPT-FINAL.md` §3). They are not "hard"; absent the
key they are unsolvable by ciphertext-only analysis.

## What is genuinely still open
1. **Transcription correctness.** The two canonical machine-readable
   transcriptions (krisyotam, relikd) are byte-for-byte identical because they
   share an origin — so a systematic mis-read would be in both and undetected.
   An independent re-read from the page images is the one unverified input.
2. **The "AN END" deep-web page** (hash `36367763…c2a8b4`) was never confirmed
   found; if recovered it may hold a key. Likely lost to Tor v2 deprecation.

## Caveat
None of this proves the *intended* method; it proves the cipher's *output* is
indistinguishable from a one-time pad with a no-repeat rule, and that no short or
structured key reproduces English. If 3301 used a long external key, only that
key (or the AN END page) unlocks it.
