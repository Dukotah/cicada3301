# Round 32 / I1 -- `beam_decode_v2` power envelope: RESULTS

_2026-10-28. Pre-registered in `PREREG.md` (thresholds fixed before cells ran; Addendum A written
after the envelope, before the re-adjudication). Raw data: `power_envelope.json`, `out_*.json`.
Nothing here is a verdict on any key; it is a measurement of an instrument._

## 0. Headline

* **Kill rule did NOT fire.** `advance=2` recovers planted `skip_by_two` at L=120 on EN_MODERN:
  median rune-index recovery **1.000**, 20/20 seeds over the shuffle-null bar. The harness
  reproduces L7-B: the old relation (`advance=1`) on `skip_by_two` recovers **0.300** (L7-B: 0.258).
* **The decoder already existed.** `round19/I1/driftbeam.py` has the `keyskip2` and `permissive`
  relations and reported `skip_by_two` repaired at L=240. `beam_v2.py` is an explicit-parameter facade
  over it (imported, unmodified). CAMPAIGN-PLAN s3 I1 did not know this; Round 32 I1's real
  contribution is the L=120 / register / panel / null **measurement**, below. Coordinator decision
  needed on whether the lane is credited as a replication+extension (my recommendation) -- see s8.
* **Decoder-recovers is not the same as adjudicator-sees.** EN_NOVOWEL (vowel-dropped English) is
  NOT recovered by `advance=2` (0.72 at L=120, 0.71 at L=400) or by `free` (0.31 / 0.13), because the
  beam still searches with the English quadgram. That is a new, measured hole in the repaired instrument.
* **Bounded re-adjudication run (gate opened):** LP2 page-0 head x SHA-256-CTR(`CICADA3301`),
  `advance=2`, 3302 offsets x 2 signs: **0 flagged** (best pmax 4.54; flag 10.0). In-pipeline planted
  control found the true offset (pmax 18.6). Coverage is one seed of B-04's 2,165 -- see s6/s7.

## 1. Setup actually used

Correct key + offset 0 handed to the decoder (a power test). Key = SHA-256 counter mode mod 29.
Plaintext windows from the held-out second half of each corpus. Enciphers `keyskip1`, `skip_by_two`
(key +2 per rejection), `free_q05` (keyskip1 + unrelated +1 advance w.p. 0.05), supp 0.83. Decoders
`advance` 1 / 2 / free = driftbeam `exact_ms8` / `pair` / `drift` (beam_w 400). Recovery on rune
indices. Adjudicator = `round19/I2/adjudicate.adjudicate` on a **7-register lite panel**
(`build_panel_lite.py`; see s5). **Bar** = max `pmax` of a seed-3301 shuffle null of n=100 per
(decoder, L) (n=4 at L=6000); RECOVERED = median recovery >= 0.85 AND >= 80% of seeds above that bar.

Shuffle-null maxima (`pmax`; legacy `en` max in brackets): advance 1: 4.15 [-6.69] (L120), 3.54 (L400),
2.32 (L6000); advance 2: 4.02 [-6.70], 3.79, 2.78; free: 5.70 [-6.08], 8.16, 6.39. The `free` null sits higher
(the permissive relation raises the wrong-key distribution, as R19/I1 found).

## 2. The measured envelope -- EN_MODERN, positive control (n = 20 seeds; 3 at L=6000)

Entries: median rune-index recovery / median `pmax` (fraction of seeds over the null bar).
**R** = RECOVERED under the s3 rule.

| plant (encipher) \ decoder | advance=1 | advance=2 | advance=free |
|---|---|---|---|
| **L=120** keyskip1 | 1.000 / 18.6 (1.00) **R** | 0.442 / 7.4 (0.90) | 1.000 / 18.6 (1.00) **R** |
| L=120 **skip_by_two** | 0.300 / 5.4 (0.65) | **1.000 / 18.4 (1.00) R** | 1.000 / 18.4 (1.00) **R** |
| L=120 free drift q=0.05 | 0.329 / 6.4 (0.70) | 0.254 / 4.5 (0.60) | 0.992 / 18.8 (1.00) **R** |
| **L=400** keyskip1 | 1.000 / 34.4 (1.00) **R** | 0.435 / 14.3 (1.00) | 1.000 / 34.4 (1.00) **R** |
| L=400 **skip_by_two** | 0.168 / 6.0 (0.70) | **1.000 / 34.4 (1.00) R** | 1.000 / 34.4 (1.00) **R** |
| L=400 free drift q=0.05 | 0.165 / 4.9 (0.70) | 0.226 / 6.1 (0.75) | 0.982 / 34.1 (1.00) **R** |
| L=6000 keyskip1 | 1.000 / 48.8 (1.00) **R** | -- | -- |
| L=6000 **skip_by_two** | 0.056 / 2.5 (0.67) | **1.000 / 48.9 (1.00) R** | 0.888 / 43.9 (1.00) **R** |
| L=6000 free drift q=0.05 | -- | -- | 0.611 / 31.3 (1.00), recovery < 0.85, not R |

Reading it: each advance relation recovers its own construction and **only** its own
(diagonal), `free` covers all three at L<=400 at no cost on the baseline. A note on `advance=2` vs
keyskip1 at L=120/400: the `pmax` of the *wrong* decoder still exceeds the null bar in some seeds (0.90 at
L=120) while recovery is 0.44 -- a half-right decode is partly English; recovery, not pmax, is the arbiter
there, which is why s3 requires both. L=6000 note: `Panel.cal` clamps at its 800-rune grid edge, so L=6000 z values
are on a clamped scale (null and plants share it, so the comparison is consistent, the absolute `pmax` is not
interpretable); only 3 plants per cell, so the 6000 row is a spot check. `free_q05` at L=6000 degrades
(0.611): ~300 unrepresentable advances exceed `max_free=2` budget in places -- a measured limit, not a fix.

## 3. Register axis (planted skip_by_two / keyskip1 / free_q05; matched + free decoders)

n = 10 plants (L=120) / 8 (L=400), median recovery. Full numbers in `power_envelope.json`.

| register | skip_by_two, adv=2 (L120 / L400) | skip_by_two, free | keyskip1, adv=1 | free_q05, free |
|---|---|---|---|---|
| LATIN | 1.000 / 0.998 **R** | 0.983 / 0.963 **R** | 1.000 / 1.000 **R** | 0.950 / 0.930 **R** |
| OE | 1.000 / 0.996 **R** | 0.963 / 0.925 **R** | 1.000 / 0.995 **R** | 0.954 / 0.933 **R** |
| DE | 1.000 / 1.000 **R** | 0.988 / 0.974 **R** | 1.000 / 1.000 **R** | 0.958 / 0.945 **R** |
| **EN_NOVOWEL** | **0.721 / 0.705 -- not R** | **0.312 / 0.126 -- not R** | 0.946 / 0.867 R | **0.567 / 0.416 -- not R** |

Latin / OE / DE are recovered and adjudicated on the lite panel even though the legacy English scorer
puts the correct decode at `en` about -5.4 to -5.5 (borderline against the old -5.5 bar), which is
the L7-A pattern again. **EN_NOVOWEL fails the repaired decoder**: the key-consistency constraint alone does
not pin the path when the plaintext statistics are not English, and the permissive relation (lam=12) leaves
it free to wander. Even where recovery is poor, `pmax` for NOVOWEL under `advance=2` (11.9 / 20.1) is still
over the null bar, so a *flag* survives (the panel sees it) while the *recovered text* does not.

## 4. Positive-control statement

Controls (all passed unless stated): (a) replication -- `advance=1` on `skip_by_two` at L=120 reproduces
L7-B (0.30 vs 0.258; `en` -6.54 vs -6.90); (b) matched-decoder recovery on EN at L=120/400/6000
(1.000); (c) four of five registers recovered; (d) in-pipeline control of the re-adjudication scan (s6).
**Failed control, reported as a result:** EN_NOVOWEL, matched decoder, L=120 and L=400, recovery 0.72 /
0.71 < 0.85 -- the instrument is *not* validated for vowel-dropped plaintext under skip_by_two, so a
re-adjudication negative must not be extended to that register. (`en` for planted OE/DE/LATIN at about -5.4 is
shown only to illustrate the legacy bar; adjudication used `pmax`.)

## 5. Panel gap (stated, instructed fallback)

The I2 nine-register panel is NOT rebuildable here: `data/keys/mabinogion.txt`, `data/kjv.txt` and
`data/keys/welsh/welsh_mabinogion.txt` are absent (`round19/I2/models/` also does not exist). I built
the same statistic over 7 registers (`build_panel_lite.py`, `models/panel_lite.npz`, 3,000-draw null at
6 lengths). **EN_KJV and CY (Welsh) are not covered.** The lite z-scale differs from I2's, so I3's
`calib19.json` contract bars do not apply and the bars here are empirical shuffle-null maxima (alpha about 1/n
per decode). Also note EN_MODERN is trained on ~21k runes (self_reliance only, vs the I2 build that adds
Mabinogion), so it is a weaker English model than I2's; the English plant windows are held-out.

## 6. Bounded re-adjudication (PREREG s5 / Addendum A)

Object: LP2 page-0 head (120 cipher runes, `round13/B04` stage-C head), key = `plant.make_key("sha256_ctr",
seed=b"CICADA3301")` (B-04's family). Decoder `advance=2`, offsets 0..3301, sign -1 and +1: 6,604 decodes,
**0 over the flag (pmax > 10.0); best 4.26 (sign -1, offset 160, panel argmax EN_NOVOWEL) and 4.54 (sign +1,
offset 2563, LP1_REAL)**, both inside the shuffle-null range (advance=2, L=120 null max 4.02; max over
6,604 draws of a null is expected higher than the n=100 max, so 4.5 is unremarkable). `advance="free"`
at offsets 0..9, both signs, atbash 0/1: 0 flagged, best 5.31 / 5.62 (free null max 5.70). **In-pipeline control**:
a plaintext planted at offset 1000 under `encipher_skip_by_two` with the same key family, the identical scan, put
the true offset at rank 1 (pmax 18.59, `en` -4.34); 6 neighbouring offsets 1002..1012 (+2k) were also over the flag at
lower scores (14.98-17.41), because a two-position-shifted key is still reachable by the pair relation. PREREG
said the true offset should be "the unique flagged one"; it was the *highest* flagged, not the unique one -- a
stated deviation from my own wording, not from the flag rule.

## 7. The three conditionals (Doctrine Q4) carried by this result

1. **Key space**: ONE seed (`CICADA3301`) of B-04's 2,165-entry dictionary, family sha256_ctr (byte % 29)
   only, on ONE page head of 120 runes, offsets 0..3301 for advance=2 (0..9 for free), atbash only at offsets
   0..9. Coverage fraction of the B-04 sweep is therefore **well under 1%** (1/2165 seeds x 1/16 generators
   x 1 of 55 page heads); it is a spot re-adjudication, not exhaustion. Everything else B-04 swept is not re-covered.
2. **Decoder transition model**: keyskip1 / keyskip2 (pairs) / permissive (max_skip 40, max_free 2, lam 12,
   start_slack 2), beam_w 400. Not represented: skip_by_three or any advance-per-rejection other than 1 or 2,
   ">2 unexplained advances per rune", reset/restart of the key at line or page breaks, rewrite/keyside/plainside
   constructions, key-offset jumps, interrupters. `free_q05` at L=6000 already exceeds the budget (0.611).
3. **Adjudicator register**: 7-register lite panel; no Welsh, no KJV, no Greek/Hebrew/Norse. The beam itself is
   English-quadgram-guided, so vowel-dropped English is a decoder-side hole (s3) that the panel cannot fix.

## 8. not_covered and coordinator decisions

not_covered: L=6000 beyond 3 plants per cell and not for `advance=1` on keyskip1-only/`free` on keyskip1 /
free_q05 under advance 1-2; the full I2 nine-register panel (EN_KJV, CY); the re-adjudication of any B-04 seed
other than `CICADA3301`, any other page, other key families (KDF, PRNG, Py2.7-MT pair survivors), non-zero atbash
at offsets > 9, other supp values (supp 0.5/1.0 were measured by R19/I1 on EN only); real LP2 path-continuation beyond 120 runes
(the real stream's n_skips crossover at L about 6000 is R21-L2's finding and not re-addressed here).

Coordinator decisions: (1) CAMPAIGN-PLAN s3 I1 should be rewritten to say the decoder pre-exists in R19/I1
and the lane's value is the L=120 / register / null measurement; (2) EN_NOVOWEL under skip_by_two is an
open instrument hole: a panel-aware (or language-agnostic) beam-scoring term is the repair, which I did
not attempt (new decoder, new gates -- a lane of its own); (3) rebuilding the I2 panel needs the Welsh /
Mabinogion / KJV corpora restored (I2 lane's prerequisite) -- B1/B2 sweeps should not adjudicate through my lite panel.

## 9. Coverage x power (R2)

Power against the class "planted skip_by_two, SHA-256-CTR key, English/Latin/OE/DE plaintext, L>=120, correct
key and offset": **1.00** for advance=2 (and 0.98-1.00 for `free`), measured above. Power against vowel-dropped
English: **0.72 recovery, flag still raised by pmax** (not 1.0). Power against free drift q=0.05: 1.00 only
with `free`. Coverage of the actual historical sweep: <1% (s7.1). Therefore the product for the claim "the
LP2 page-0 head is not SHA-256-CTR(CICADA3301) at offsets 0..3301 under skip_by_two" is high power x one
seed; it says nothing about the other 2,164 seeds or the other generators. No verdict about the cipher is drawn.

## 10. Files

`PREREG.md`, `beam_v2.py`, `build_panel_lite.py`, `run_envelope.py`, `readjud.py`, `power_envelope.json`,
`ledger.json`, `RESULTS.md`, raw `out_null.json`, `out_null_L6000.json`, `out_en_L120.json`, `out_en_L400.json`,
`out_en_L6000.json`, `out_reg_L120.json`, `out_reg_L400.json`, `out_readjud_*.json`; `models/*.npz` is
rebuildable (`build_panel_lite.py`) and should be gitignored.
