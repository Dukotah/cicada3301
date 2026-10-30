# Round 18 / Marsaglia — pre-registration

_Written before the sweep. Closes the item Round 17's SYNTHESIS named as the cheapest
live unswept public-pad source._

## Hypothesis

The LP2 keystream is (a reading of) the **Marsaglia Random Number CDROM (1995)** — 60×10 MB
`bits.NN` files + `calif/canada/germany.bit`, ≈630 MB of published physical randomness with
a permanent public record. This is the third-branch "seedless, full-entropy, yet permanently
public" pad class Round 17 opened; Marsaglia was found, named, and left unswept there because
its only host (archive.org item `marsaglia-cdrom`) is egress-blocked in this environment.
Fetched here from the `jeffThompson/DiehardCDROM` GitHub mirror (recreated from the Wayback
Machine copy of Marsaglia's FSU FTP site).

## Instrument

`analysis/round17/lib_padsweep.py`, unchanged — the dense every-offset scanner + beam, with
A1's beam settings, score scale, null, and HIT bar, so results are directly comparable to
Round 17's P0–P3.

**Instrument fix carried by this lane (not an edit to lib_padsweep):** the shared
`trigram_model()` trains on `data/{kjv,moby,pride,war}.txt`, which are gitignored and
unreachable here (Gutenberg egress-blocked), so on a fresh checkout it silently falls back to
a **uniform** model — under which every offset scores identically and `control()` reports
survival 0. `build_trigram_from_quadgrams.py` rebuilds an equivalent index-space model
offline from the committed `english_quadgrams.txt`; run it before sweeping. With the real
model, `lib_padsweep.control(blob=bits.01)` **PASSES**: beam recovers 8/8 planted keystreams
at 100% of runes, dense-prefilter **survival 0.375** (the honest coverage discount for 10 MB
uniform-random pads; Round 17's own pads measured 0.625).

## Keystream variants (per pad)

The 6 byte-oriented builders × {forward, reverse} = 12 variants: `mod29`, `hi_nibble`,
`lo_nibble`, `byte_scaled`, `prime_to_idx`, `hexchars`. No digit/text builders — the pads are
uniform binary (measured 8.000 b/B, 256/256 byte values), so `classify()` adds nothing.

## Acceptance criterion (fixed in advance)

HIT iff `score_norm >= -5.5` **AND** `score_norm >= null_max + 0.5`, i.e.
`bar = max(-5.5, null_max + 0.5)`. Null: A1's shuffle null, n=200, under the exact keystream,
per configuration reaching −5.5, plus a per-pad reference null. The multiple-comparisons
`benchmark/null.threshold_for(n_offsets)` is reported alongside; at these trial counts it is
**stricter** than the fixed bar, so the fixed bar binds.

## Coverage claim this can and cannot make

**Can:** every offset of every fetched pad, under 12 keystream readings × 2 signs, with a
control-validated instrument, discounted by the measured 0.375 survival.
**Cannot:** the archive.org item's published SHA-256s were not cross-checked (archive.org
blocked); provenance rests on the GitHub mirror + the measured digests in
`pads_manifest.json`. A control FAIL on any pad ⇒ that pad reports INCONCLUSIVE, never
NEGATIVE.

## Prediction

NEGATIVE. Marsaglia is one more published-randomness source; Round 17 already nulled
RANDOM.ORG, NIST Beacon, Bitcoin, and RAND. Prior is low; the value is closing a named gap
by measurement rather than leaving it as an assertion.
