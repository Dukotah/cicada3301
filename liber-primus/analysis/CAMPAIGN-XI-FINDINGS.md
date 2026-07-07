# Campaign XI — Pinning the Filter (the mechanism gets a number)

_2026-07-07. Reproduce:_ `PYTHONUTF8=1 python3 analysis/campaign11_pin_the_filter.py`
_(stdlib + `lp.stats`/`lp.ciphers`/`lp.score`; deterministic seed 3301)._

Builds directly on Campaign X (autokey excluded; only a *filtered* one-time pad fits).
Three parts: sharpen the filter into a parameter, close the alt-base gap, and run one
honest-but-underpowered probe.

## Part 1 — the no-repeat rule is SOFT, and ~83% strong (progress)

Sweeping the keystream's adjacent-repeat suppression from 0 → 1 and measuring the
resulting ciphertext doublet rate:

| suppression | doublet % |
|---|---|
| 0.00 (no rule) | 3.543 |
| 0.20 | 2.763 |
| 0.40 | 2.177 |
| 0.60 | 1.443 |
| 0.80 | 0.787 |
| **0.83 (best fit)** | **0.625** ← observed 0.664 |
| 0.90 | 0.386 |
| 1.00 | 0.154 |
| HARD rule (never repeat) | 0.000 |

**The observed 0.664% is reproduced at ~83% suppression.** That is a concrete, new
characterization: the author's keystream avoids writing the same rune twice in a row
**~83% of the time, tolerating a repeat ~17% of the time.** It is a *soft* rule — a
*hard* no-repeat rule forces 0% doublets, and the observed rate is emphatically not 0;
an *unfiltered* pad gives 3.5%. The truth sits precisely between, and now has a number.
(This independently corroborates Campaign IV's rough "~20% residual repeats tolerated.")

Why it matters: "the cipher suppresses doublets" was qualitative. Now the suppression
is quantified, which constrains *how* the pad was generated — soft rejection sampling,
or a by-hand "try not to repeat" discipline that slips ~1 time in 6 — and rules out any
mechanism that would produce a hard 0% or an unfiltered 3.5%.

## Part 2 — alt-base readings as key material: null (community gap closed)

The community read pp49–51 in base-60 → ASCII and got "rubbish," and floated bases
59/61/62/64 but only as text. Reading the **same glyph-digits** under each base and
using the result as **key material over the runes** (additive ±, Atbash, reversed,
offset-swept on short pages + corpus) had never been done.

| base | entropy | printable | best key-score (English −4.0, noise −7.5, thresh −5.2) |
|---|---|---|---|
| 59 | 7.162 | 41% | −6.065 |
| 60 *(canonical)* | 7.170 | 40% | −6.404 |
| 61 | 7.170 | 39% | −6.303 |
| 62 | 7.135 | 39% | −6.463 |
| 64 | 7.101 | 37% | −6.400 |

**All deep in the noise band; nothing near threshold.** The alt-base avenue is now
executed and documented as null — no one need re-run it.

## Part 3 — payload self-signature: honestly inconclusive

Does the 256-byte payload itself avoid adjacent-equal bytes the way the runic keystream
avoids adjacent-equal runes? Measured: **0 adjacent-equal bytes** vs a random expectation
of ~1.0. With only 255 adjacencies and ~1 expected collision, the test is **underpowered
by construction** — it can neither confirm nor deny a byte-level no-repeat rule. Reported
as inconclusive rather than spun into a false tie between the two halves.

## Net

- **New this campaign:** the no-repeat mechanism is quantified — **soft, ~83% suppression**
  — the sharpest description yet of the single engineered feature in LP2's cipher.
- **Gap closed:** alt-base-as-key (59/61/62/64) — null, documented.
- **Integrity:** the one underpowered test is labelled underpowered.

Still nothing that opens the lock (an OTP with an external key can't be opened from the
ciphertext) — but the wall is now described to a parameter, and two more avenues are
retired. That is the honest shape of progress on this object.
