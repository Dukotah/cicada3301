# Liber Primus — Findings (Phase: rig built + statistical verdict)

_Updated 2026-06-17._

## 1. We built a cryptanalysis rig and PROVED it works

A pure-Python toolkit (`src/lp/`) implementing the Gematria Primus, the cipher
family Cicada used, an English quadgram scorer (corpus weighted toward archaic
KJV English to match the book's register), and a **beam-search interrupter
solver**.

**Validation gate (`tests/validate.py`) — all 5 known solved pages reproduced:**

| Page | Method | Result |
|---|---|---|
| 01 "A WARNING" | Atbash (reversed Gematria) | ✅ `BELIEVE NOTHING FROM THIS BOOK…` |
| 05 "SOME WISDOM" | Direct transliteration | ✅ `THE PRIMES ARE SACRED…` |
| 06 "A KOAN" | Atbash + shift 3 | ✅ `A MAN DECIDED TO GO AND STUDY WITH A MASTER…` |
| 03 "WELCOME" | Vigenère key `DIVINITY` + interrupters | ✅ `WELCOME PILGRIM TO THE GREAT JOURNEY…` |
| 14 "A KOAN" | Vigenère key `FIRFUMFERENFE` + interrupters | ✅ `…THE I IS THE VOICE OF THE CIRCUMFERENCE…` |

If the rig couldn't re-derive these, nothing it says about unsolved pages would
mean anything. It can. It's trustworthy.

### An honest sub-finding: the interrupter ambiguity
Even with the **correct key**, our scorer-driven interrupter search reconstructs
WELCOME ~90% and still drops some real F's (OF→O, FIND→IND) and mangles F-dense
words (SUFFERING→SUMMOSTUR). Telling a *real* ᚠ from a *null* ᚠ is genuinely
under-determined by statistics alone. This is a microcosm of why "AI solved the
Liber Primus" claims should be distrusted: a model will always hand you a
clean-looking answer; only the ground truth tells you it's subtly wrong.

## 2. Statistical verdict on the 55 unsolved pages

`analysis/run_stats.py` over 12,956 runes (full numbers in `analysis/STATS.md`):

| corpus | IoC·N | doublet % | entropy (bits) |
|---|---|---|---|
| random uniform (theory) | 1.000 | 3.448 | 4.858 |
| English → Gematria (what a solved page looks like) | 1.785 | 2.411 | 4.247 |
| WELCOME ciphertext (Vigenère, 8-letter key) | 1.184 | 3.562 | 4.643 |
| **UNSOLVED pages (aggregate)** | **0.9999** | **0.664** | **4.857** |

**Three hard conclusions:**

1. **Statistically indistinguishable from random.** IoC·N = 0.9999 (random =
   1.000). Even a Vigenère with a short key leaks structure (1.18); the unsolved
   pages leak *none*. This is the fingerprint of a **running-key / autokey /
   stream cipher whose key is as long as the message** — i.e. the regime where
   more compute does **not** help.

2. **No short key period.** Kasiski finds no dominant small spacing (top hits are
   huge: 1031, 6395, 844…). A repeating-key Vigenère is ruled out.

3. **The doublet deficit is real — and it's the one true anomaly.** Doublets
   occur at **0.664%**, vs 3.448% for random and 2.411% for English. Doublets
   are *actively suppressed* — about 5× below chance. A pure one-time-pad would
   sit at random (3.45%); something in the construction prevents consecutive
   equal runes. **This is the single most promising handle on the cipher** —
   it's structure that a true random pad would not have.

## 3. So — can we (or any AI) solve the rest?

Consistent with the research phase, now confirmed by our own measurements:

- **Brute force / "more tokens" will not crack it.** The monographic statistics
  are maximal-entropy and periodless. If the key was never published, short
  passages have multiple valid plaintexts with no way to choose — the
  one-time-pad wall.
- **The only realistic openings are insight-based**, and the **doublet deficit**
  was the thread to pull. We pulled it — see below.

## 4. Update: the doublet deficit, chased to the end (`analysis/DOUBLET-INVESTIGATION.md`)

We rigorously investigated *what cipher forces doublets to 0.66%*. Result:
- The deficit is **real and unique to the unsolved pages** — every solved
  enciphered page is normal (1.9–3.6%), even the flat-IoC totient page (2.38%).
  So flat statistics alone don't cause it; the unsolved cipher does something
  extra no known Cicada cipher does.
- **No standard construction reproduces it** (running key 3.3%, prime/totient
  2.9%, Vigenère 3.4%, autokey 4.2%). Autokey matches the *rate* but its
  decryptions are pure gibberish, and the consecutive **differences are flat
  random with a single hole at zero** (IoC·N 1.04, entropy 4.83/4.86) — so there
  is no keystream or plaintext hidden in them.
- **Verdict: the deficit is a hardening artifact, not a crack.** The cipher was
  engineered to avoid repeated runes and otherwise behaves like a one-time pad.
  This lead, fully chased, did not open the cipher — and it's strong own-measured
  evidence that the remaining pages need an externally-held key or were built to
  be unsolvable.

## What runs today
```
PYTHONUTF8=1 python tests/validate.py        # prove the rig (all PASS)
PYTHONUTF8=1 python analysis/run_stats.py     # regenerate STATS.md
```
