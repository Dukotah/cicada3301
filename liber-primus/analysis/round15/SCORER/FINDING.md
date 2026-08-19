# The scorer is trained on the wrong distribution — measured, and worth ~18% of power

_2026-08-19. Instrument finding, not an attack result. `poc.py` reproduces every number here._

## The observation

Every attack ever run in this repository — every sweep, every null, every beam decode, across
~20 campaigns and 15 rounds — scores candidates with **one** model:
`data/english_quadgrams.txt`, quadgram log-probabilities over raw English (KJV-weighted).

But the decoder does not emit English. It emits the **runic transliteration**, and that is a
different alphabet with different statistics:

- **7 of the 29 runes expand to two characters** — `TH`, `EO`, `NG`, `OE`, `AE`, `IA`, `EA`.
  A 4-rune window therefore produces anywhere from 4 to 8 characters, and the quadgram window
  slides over *characters*, not runes.
- **The alphabet is lossy**: no K (→C), no Q, no V (→U), no Z. Solved-page plaintext reads
  `BELIEUE`, `CNOW`, `THNGS`, `FIRFUMFERENFE`.

So the model is trained on one distribution and applied to another. That is why the solved
pages — genuine, correct, known-good English — score **−4.1 to −5.0** instead of real English's
**−2.2**. Roughly half the apparent "distance from English" of a *correct* decode is the
scorer's own mismatch, not the plaintext.

## The measurement

`poc.py` builds a **matched** quadgram model: take the same KJV corpus, push it through the
same rune round-trip the decoder inverts (`eng_to_idx` → `IDX_TO_TRANS`), and train quadgrams
on the resulting transliteration string. Then score the five solved pages (known ground truth)
and a 200-draw shuffle null under both models.

| | OLD (English quadgrams) | NEW (matched) |
|---|---|---|
| 01 A WARNING | −4.944 | −4.618 |
| 05 SOME WISDOM | −4.599 | −4.741 |
| 06 A KOAN | −4.055 | −4.310 |
| 03 WELCOME | −4.442 | −4.685 |
| 14 CIRCUMFERENCE | −4.406 | −4.453 |
| **noise mean** | −7.562 | −7.444 |
| **noise max** | −7.309 | −7.280 |
| **noise sd** | **0.089** | **0.071** |
| **separation** | +3.073 raw = **34.39 σ** | +2.882 raw = **40.53 σ** |

## What this does and does not show

**It is a real gain, and it is modest.** The *raw* gap does not widen — it narrows slightly.
The gain is entirely in the **noise distribution tightening by 20%** (sd 0.089 → 0.071), which
buys **+18% separation in sigma units**. Reported honestly: this is an instrument improvement,
not a discovery, and anyone extending it should expect ~18%, not a breakthrough.

**Why 18% still matters at sweep scale.** The thing that swamps a large sweep is the
best-of-N order statistic, which grows like `sd · sqrt(2 ln N)`. A 20% smaller `sd` shrinks
that ceiling proportionally at *every* N. In a 6.2M-decode sweep like B-04 that is the
difference between a marginal candidate sitting inside the null's upper tail and sitting
clear of it. It does not manufacture a signal, but it stops a real one from being written off.

**What it does NOT support.** It gives no reason to revisit any completed negative. Every
published null in this repo sits at −5.7 or below against an English band of ≈−4.2; an 18%
sigma improvement moves nothing across that gap. The claim here is strictly forward-looking:
*future* sweeps should use the matched model.

## The larger point for whoever comes next

This is worth recording less for its size than for its type. It is a **systematic instrument
error that survived twenty campaigns** — not because anyone was careless, but because the
scorer was inherited as infrastructure and never re-derived against the thing it actually
scores. Nobody re-asked "what distribution does the decoder's *output* have?"

That is the same shape as the two other errors found this week: the truncated `_560.00`
(a file trusted without checking its digest) and the rigid-decoder blindness (a decoder
trusted without planting a signal through it). In each case the mistake was inherited
infrastructure, accepted rather than re-validated.

**The general lesson: re-derive your instrument against your actual output distribution, not
against the textbook one.** That is cheap, it is almost never done, and here it was worth 18%.

## Status

`poc.py` is a proof of concept and is **not yet wired into any sweep**. Doing so means:

1. Build the matched model once and cache it (`build_matched.py`, not yet written).
2. Add it to `benchmark/` as a second scorer so `power.py` can report both.
3. Re-validate: the matched model must still put the five solved pages above the noise band by
   a margin at least as large as the old model's — verified above, but it must be a *gate*,
   not a one-off check, before any sweep depends on it.
4. Extend to non-English hypotheses (Latin, Old English) as separate models, each with its own
   solved-page control. **Note the prior is low**: Campaign XIV's P5 found the word-length
   distribution English-like, and the solved pages are English, so a non-English LP2 plaintext
   would be an odd authorial choice. Cheap to test, but do not oversell it.
