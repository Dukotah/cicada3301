# PREREG — Lane B6: non-English / non-prose plaintext detectors

Registered BEFORE any run. Lane dir: `liber-primus/analysis/round10b/B6-non-english-plaintext/`.

## The blind spot being tested

Every scorer in this repo (and, as far as the prior-art census shows, in the public community)
ranks a candidate decode by ENGLISH likeness: KJV-weighted quadgrams, English bigram
instruments, English word detection, English word-length skeletons. If the true LP2 plaintext is
a machine-shaped string (onion address, coordinate block, digit block, key block, another cipher
layer) or prose in another language, every sweep run to date would have scored it as noise.

## Hypotheses

- **H-B6.1 (structure)** — Some window of the LP2 ciphertext, or of a simple transform of it,
  carries a *locally structured* region (restricted symbol alphabet / elevated windowed IoC /
  internal repeats) that page-scale English scoring averaged away.
- **H-B6.2 (non-English prose)** — Some decode already swept under English scoring is high-scoring
  under a Latin / German / Welsh / Old English rune-space language model.
- **H-B6.3 (machine payload)** — Some decode contains an onion-address-shaped, coordinate-shaped
  or digit-block-shaped token.

## Instruments (built here, calibrated here)

| ID | detector | invariances |
|----|----------|-------------|
| D1 | distinct-symbol count in window (alphabet restriction) | any monoalphabetic substitution, Atbash, all 29 shifts, reversal |
| D2 | windowed IoC x 29 | same as D1 |
| D3 | repeat structure (repeated bigram/trigram mass, longest repeat) | same as D1 |
| D4 | compressibility (lzma) of window | same as D1 |
| D5 | rune-space trigram LM: EN / LA / DE / CY / OE / Runeglish | none (decode-specific) |
| D6 | token/crib detector on Runeglish output: ONION, HTTP, WWW, TOR, COM, ONE..NINE, ZERO, NORTH/SOUTH/EAST/WEST/DEGREES, PGP/KEY/BEGIN | none |
| D7 | base32/hex-shape: longest run of window symbols confined to a 16- or 32-symbol subalphabet | monoalphabetic |

D1-D4 and D7 are **language-agnostic**: they fire on ANY non-random structure. That is the
instrument the repo does not have. Because they are invariant under monoalphabetic substitution,
a single scan of the raw ciphertext closes the ENTIRE 29!-permutation / all-shift / Atbash /
reversal decode family for those statistics simultaneously.

## Pre-registered thresholds

Null = 200 independent uniform-random shuffles of the real LP2 unsolved stream (same length, same
symbol multiset), scanned identically. For each (detector, window size, stream) cell:

1. **Per-cell threshold** = the maximum detector value observed over the whole null ensemble
   (i.e. an empirical family-wise max-statistic threshold, alpha ~ 1/200 = 0.005 family-wise over
   all windows in a scan). REAL must EXCEED the null max to count as a hit.
2. Report as z = (real_max - null_max_mean) / null_max_sd using the per-shuffle maxima.
   **PASS = z >= +3.0 AND real_max > null ensemble max.** Anything else = NEGATIVE.
3. **Language sweep (D5):** a decode is a hit only if its rune-space trigram score under a
   non-English model exceeds that model's own real-text calibration floor AND exceeds the maximum
   score achieved by the same model on 200 shuffled-LP2 decodes of the same length.
   Pre-registered: **hit iff z >= +4.0 vs the shuffled-decode null for that (model, page-length)**.
4. **D6 token detector:** hit iff the observed count of a token class in the real decode set
   exceeds the null-set maximum count at the same corpus size.

## Positive control (mandatory)

Plant into a uniform-random rune stream, at a known offset:
(a) a 16-character v2-onion-shaped base32 string mapped into a 32->29 rune subalphabet;
(b) a hex-shaped block (16-symbol subalphabet);
(c) a digit block (10-symbol subalphabet);
(d) a coordinate block spelled in Runeglish ("FIFTY ONE DEGREES NORTH ...");
(e) an English sentence;
(f) a Latin sentence.
Plant lengths 8,12,16,24,32,48,64,96,128. Report, per detector, the **detection floor** = the
shortest planted payload still exceeding the pre-registered threshold. An instrument that cannot
find its own plant reports NO coverage at that length; this bound is the lane's deliverable.

## Null control

The shuffle ensemble above, plus (for D5) shuffled-ciphertext decodes under identical key search,
so that any hill-climbing optimism is charged to the null as well.

## Scope declared up front

- I do NOT run a global randomness battery on the whole stream — Round 10 lane owns that. B6 is
  strictly *local/short-window* and *shape-specific*.
- Round 8 Track PAYLOAD already killed 166 byte-representations of the RAW stream against 40
  magics; I do not repeat it. D7 is a symbol-alphabet test, not a byte-magic test.
- Keytext running keys are mechanism-killed (doublet argument); I do not add keytexts. The D5
  sweep covers monoalphabetic + short periodic keys, which are the families where a short
  non-English payload could survive.

## Falsification

If every detector's real value sits inside its shuffle null AND the positive controls show the
detectors work down to a stated floor, then the non-English/non-prose blind spot is CLOSED for
payloads at or above that floor, under the decode families scanned. That is a real closure, not
an absence of evidence.
