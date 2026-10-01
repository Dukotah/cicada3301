# LANE 4 (finite) — RESULTS

_Round 19. Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). Pre-registration:
[`PREREG.md`](PREREG.md). This document reports a RUN, not a verdict (R7)._

## 0. One line

The 74 already-extracted **RUNIC ornament bands** (`round18/L3-ornaments/bands.json`, 7,796
readable rune-index glyphs) were re-scored over the **I2 nine-register adjudicator** — closing
A-06's own reopen condition (ii), *"a multi-register (non-English) scorer finds language in a
short band's read."* **It does not.** 0 of 74 bands read as language in any of the nine
registers once the mandatory R3 statistics gate out restricted-alphabet false positives.

## 1. What was run

- **Object (R5 rank-1, finite, enumerable):** the `call=="RUNIC"` bands from
  `round18/L3-ornaments/bands.json`. 74 bands, 7,796 readable glyphs (unreadable `-1` stripped),
  lengths 8–314 (median 89); 42 bands ≥64 glyphs, 23 at 32–63, 6 at 16–31, 3 <8.
- **Instrument:** `round19/I2/adjudicate.py` nine-register trigram panel
  (`EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL`), each register
  null-standardised at the decode's own length. **No decryption key** — the bands are scored as
  plaintext-in-themselves (ornaments-as-plaintext). Scored on **rune indices**, never translit.
- **Bar:** per-band matched-FP bar = the (1 − 0.001) quantile of `pmax` over 2,000 uniform-rune
  strings **at that band's own length** (`bar_pmax`). A band is a candidate only if its `pmax`
  clears this bar with a natural-language register as the panel argmax.
- **R3 (CI-enforced):** every band row persists `en, pmax, preg, pmax_ne, pcon, pcreg, ioc, mds,
  h2, zl, z[9]` → `sweeprows.jsonl`, validated by `adjudicate.validate_store` (74/74 rows pass).

Reproduce: `cd round19/finite && python3 run_bands.py` (→ `out_bands.json`, `sweeprows.jsonl`).

## 2. Power — the recognizer-plant gate (PREREG Q1/Q5), measured

Held-out register text (from `I2/models/testhalves.npz`, never used to train the panel) was cut
to band lengths L∈{8,16,32,48,89,128}, corrupted at the **band-reader's measured 4.4% per-glyph
error** (95.6% recall, C3/A-06 — pure-substitution model, charitable), scored, and the recovery
= fraction clearing the length-L bar with the correct register as argmax (200 trials/cell):

| register | L8 | L16 | L32 | L48 | L89 | L128 | usable floor (noisy≥0.80) |
|---|---:|---:|---:|---:|---:|---:|---:|
| EN_MODERN | .04 | .20 | .24 | .20 | .12 | .07 | **never** |
| EN_KJV | .04 | .14 | .12 | .07 | .04 | .01 | **never** |
| LP1_REAL | .82 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 8 |
| LATIN | .28 | .81 | .95 | .98 | 1.00 | 1.00 | 16 |
| OE | .02 | .46 | .68 | .70 | .81 | .86 | 89 |
| DE | .49 | .93 | .98 | .99 | .99 | .99 | 16 |
| CY | .00 | .56 | .83 | .88 | .91 | .92 | 32 |
| EN_HALFVOWEL | .00 | .25 | .56 | .57 | .63 | .73 | **never** |
| EN_NOVOWEL | .20 | .81 | .99 | 1.00 | 1.00 | 1.00 | 16 |

**The lane survives the kill gate for the non-English registers the reopen names.** LATIN, DE,
EN_NOVOWEL recover a planted hit at L≥16 through band-reader noise; CY at L≥32; OE at L≥89 (the
slow one). Where the real bands live — median 89, 65/74 at ≥32 — the panel can recognise its own
planted in-register hit for LATIN/DE/CY/EN_NOVOWEL/OE.

**Underpowered cells, reported as such (not as absence):** the three *English* registers
(EN_MODERN, EN_KJV, EN_HALFVOWEL) never reach 0.80 noisy recovery at any band length against the
length-matched bar with the argmax-register requirement. So the English-register silence over
these bands carries little information — but that is the exact silence A-06 already reported, and
this lane was aimed at the **non-English** gap, where power is real.

## 3. Result — the 74 bands

**Bands clearing their own-length bar in a natural-language register: 3.**
**Bands doing so in a NON-ENGLISH register (the reopen's target): 3** — B010 (OE, pmax 5.30),
B006 (OE, pmax 4.50), B100 (LATIN, pmax 4.30).

**All 3 are restricted-alphabet decoration, not language — and the mandatory R3 columns are what
show it.** The doctrine's R3 statistics exist for exactly this: a low-entropy repeated-glyph
string trips a trigram LM without being text.

| band | n | pmax | reg | **mds** | **ioc** | translit (readable) |
|---|---:|---:|---|---:|---:|---|
| B010 | 133 | 5.30 | OE | **5** | **2.88** | `…IIIIIIIIIIILILXILUCIIIIIIIIIIIIIL…` |
| B006 | 194 | 4.50 | OE | **5** | **2.29** | `…SCIIITHLNIIIIIIILXIIIL…IIIIIIIX…` |
| B100 | 33 | 4.30 | LATIN | **13** | **9.50** | `IFUIHCOEIIIITHLILIEOIIIIIIIWCBIISTII` |

Reference — real held-out language text at the same lengths (30 draws each):

| register | L=33 | L=133 | L=194 |
|---|---|---|---|
| OE | mds 16.4 / ioc 1.54 / pmax 7.65 | mds 12.5 / ioc 1.78 / pmax 14.58 | mds 12.8 / ioc 1.66 / pmax 17.93 |
| LATIN | mds 13.8 / ioc 1.94 / pmax 9.23 | mds 11.5 / ioc 2.07 / pmax 18.57 | mds 11.3 / ioc 2.03 / pmax 22.04 |

Real OE at L=133 has **mds≈12.5, ioc≈1.78, pmax≈14.6**. B010 has **mds=5, ioc=2.88, pmax=5.30**:
an alphabet collapsed to 5 symbols in its densest 32-window (the `IIIIIIIII`/`LILIL` runs visible
above), an IoC 1.6× a real OE sample's, and a pmax a *third* of real OE's. B100's ioc=9.50 is 5×
real Latin. None is language; each is a decorative repeated-glyph band whose low entropy
mechanically lifts a trigram score just over the length bar.

**Bands clearing the bar in a natural-language register AND R3-consistent with language
(mds ≥ 10 AND ioc ≤ 2.5): 0 / 74.** The band `pmax` distribution is min −62.3, median **0.90**,
max 5.30 — i.e. the typical band scores like the random-rune null, as expected for decoration.

## 4. Conclusion (bound, not verdict — R7)

**NEGATIVE for ornament-band content in a natural-language register, extending A-06 from
English-only to the nine-register panel, at measured power.** The reopen the repo wrote for A-06
— condition (ii), a multi-register scorer — has now been run and returns no language. Every band
that clears a length-matched bar does so only through restricted-alphabet repetition that the R3
statistics (mds, ioc) independently disqualify.

### Measured power (both axes)
- **Register axis:** recovery of a planted in-register hit, through the band-reader's 4.4%
  per-glyph noise, at band lengths — LATIN/DE/EN_NOVOWEL ≥0.95 at L≥32, CY ≥0.83 at L≥32, OE
  0.81 at L=89; LP1 1.00 at L≥16. The three **English** registers are **underpowered (<0.80 at
  all L)** and their negative is reported as underpowered, not as absence.
- **Construction axis:** the primary read applies **no cipher** (identity / ornaments-as-
  plaintext), so there is no rejection-loop construction to represent here. The gated
  secondary pass (bands-as-key under the I1 drift-tolerant beam) was **not triggered** — it is
  gated on the primary read producing a non-noise register signal first, and it did not.

### Coverage
74/74 RUNIC bands, 7,796 readable glyphs, 9 registers, each band judged at its own length with a
2,000-draw null bar; full R3 SWEEPROW persisted per band (74/74 CI-valid).

### Not covered
- **Registers outside the nine-panel** (Hebrew, Greek, cipher-of-a-cipher, a tenth language).
- **The three English registers** at band lengths: underpowered (<0.80), per §2.
- **Colour / chroma band channels** — only 8-bit luminance was read (unchanged from A-06).
- **The 27 NON-RUNIC + 8 DEGENERATE bands and the 256 base-60 tokens** — out of scope here;
  A-06 already read them (NON-RUNIC call carries no info at ≤16 glyphs, sensitivity 0.50).
- **Band-reader fidelity:** a negative is conditional on `round18/L3-ornaments`'s connected-
  component reader (95.6% per-glyph) being faithful; a higher-recall reader could change a
  band's string.
- **Bands-as-key** (the gated secondary pass) — not triggered, so uncovered by construction.

### Reopens if
(a) a tenth register / non-panel language scores a band above its length bar WITH mds≥10 and
ioc≤2.5 (i.e. language, not alphabet-collapse); (b) a ≥99%-per-glyph band reader changes a
band's rune string such that it clears the bar on genuine language statistics; (c) chroma-channel
extraction yields a readable band the luminance read missed; (d) the gated bands-as-key pass is
ever triggered (and then must first clear the AN-END blind-rediscovery holdout before any
unsolved-page claim).

## 5. AN-END holdout

**NOT_APPLICABLE.** This lane applies no keystream and claims no decode of any unsolved page; it
reads a finite extracted object as plaintext-in-itself. The holdout gate is pre-committed in
PREREG §4 for the bands-as-key secondary pass, which was not triggered.

## 6. Honest notes

The result is clean but its strength rests on the R3 statistics the doctrine mandates: without
`mds`/`ioc` persisted per band, the 3 bar-clearances would read as 3 "non-English hits" and this
lane would have manufactured exactly the kind of false positive L7-A warns about, in reverse (a
low-entropy string fooling a language scorer). The English-register cells are honestly
underpowered; the non-English cells — the ones the reopen targeted — are powered where the bands
are long enough, and they are silent.
