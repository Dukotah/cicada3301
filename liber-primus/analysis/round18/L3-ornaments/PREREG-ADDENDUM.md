# L3 — PRE-REGISTRATION ADDENDUM #1 · the ink-intensity channel

_Written 2026-08-25, **after** descriptive inspection of the band crops and **before** the
test below was run. It is filed as an addendum rather than an edit to `PREREG.md` because
this repo's discipline is that a threshold is never rewritten after a result: the original
nine B-12 channels stand exactly as registered, and this is a tenth, added openly._

## What prompted it

Cropping page 15 for the band inventory showed the 4×4 numeric grid with **one entry
(`3299`) set in a visibly lighter ink than the other fifteen**. Every community
transcription in this repo records the digits and discards the colour. Round 8's GEOMETRY
track measured glyph *shape* (nearest-neighbour Hamming distance, median 0.0000), *advance*
(1.86 σ, unimodal) and *baseline jitter* (BIC rejects 2 components) — but **never ink
intensity**. In a 400-DPI render of a typeset document, per-glyph grey level is an obvious
covert channel and it has not been measured here.

## Hypothesis (H9)

Per-glyph ink intensity carries information: some glyphs in the Liber Primus renders are
deliberately set in a different tone from the body text.

## Instrument

For every connected component on all 56 relikd page renders (sha256-verified), compute the
**mean grey value of the component's pixels** and the **10th-percentile (darkest core)
value**, from the original 8-bit greyscale, before any binarisation. Components are the same
objects `reader.py: comp_table` produces. Group by page, and by ink class.

## Positive control (mandatory, run before the null is trusted)

Take a real page render, select K components at random, and lighten them by a known ΔL
(the *measured* Δ between `3299` and its neighbours, and also at ΔL = 5, 10, 20, 40 grey
levels). **PASS iff the detector recovers ≥ 90% of the planted components at the measured
Δ.** If it fails at small Δ, report the smallest recoverable Δ as the channel's power
ceiling instead of claiming a negative.

## Pass/fail threshold (fixed here, before running)

- **Population test.** Body-text components' mean-grey distribution is measured per page.
  A component is an **intensity outlier** iff its mean grey exceeds the page's body-text
  mean by **> 4 σ** of that page's body-text distribution.
- **PASS iff** the number of intensity outliers across the book is **greater than the
  size-matched null expectation** at **p < 0.001**, where the null is 10,000 draws of the
  same component counts from each page's own fitted body-text intensity distribution.
- **A single outlier is not a channel.** If the count of outliers is small (< 10 book-wide),
  the result is reported as an **annotated list of individual anomalies**, not as a channel,
  and each is adjudicated by eye against a JPEG-artifact explanation (thin strokes, isolated
  small components and components adjacent to a chroma edge all lighten under JPEG).
- **Confound that must be excluded before any positive claim:** stroke width. A thin stroke
  antialiases lighter. Every candidate outlier is therefore re-tested against components of
  **matched stroke width** (area ÷ perimeter proxy) and matched height, not against the
  page as a whole.

## What a negative here means

That per-component ink intensity in these renders is consistent with a single tone plus
JPEG/antialiasing noise, down to the measured power ceiling in grey levels. It does not
close the layout channel; §5 of `RESULTS.md` governs coverage.
