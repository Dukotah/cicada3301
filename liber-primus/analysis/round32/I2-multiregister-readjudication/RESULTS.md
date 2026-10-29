# R32 / I2 - multi-register re-adjudication - RESULTS

Pre-registered in [`PREREG.md`](PREREG.md) before running. An instrument measurement plus a survivor-level re-score;
nothing here is a "solved/closed/exhausted" claim.

## 1. Corpus repair (three files were missing, not one)
| file | status | action |
|---|---|---|
| `data/keys/welsh/welsh_mabinogion.txt` | absent; no Welsh Mabinogion on disk (the `mabinogion*` files on disk are Guest's ENGLISH translation) | **substitute** built from 4 public-domain Welsh prose texts from Project Gutenberg (#3680 Cartrefi Cymru, #57981 Brethyn Cartref, #56275 I'r Aifft Ac Yn Ol, #67424 Nedw), boilerplate stripped, 716,409 chars. NOT the original corpus (original 524,561 B, sha 4b3fd926...). CY retained, but it is modern Welsh prose, not the Mabinogion's Middle Welsh. |
| `data/keys/mabinogion.txt` (EN_MODERN, EN_HALFVOWEL, EN_NOVOWEL) | absent (original 617,362 B) | copied from `analysis/bookcipher/books/mabinogion.txt` (617,553 B, same text, header differs) |
| `data/kjv.txt` (EN_KJV) | absent (original 4,436,268 B) | copied from `analysis/bookcipher/books/kjv.txt` (4,455,950 B) |

Hashes therefore differ from `round19/I2/out_build.json`: this is a REBUILD, not a byte reproduction, which is why it had to re-pass the gate.

## 2. Gate (kill rule Q5): PASSED at L=120 and L=240
Rebuilt `models/panel.npz` is in this lane dir (nothing written into round19/I2). Code is a copy of round19/I2 with
`nproc=1` (no `fork` on Windows), same beam, 24 replicates, held-out plant windows. Matched-FP bar (alpha 1e-3):
`pmax >= 4.422` at L=120, `4.922` at L=240.

| register | pow pmax L=120 | pow pcon L=120 | legacy -5.5 L=120 | pow pmax L=240 |
|---|---|---|---|---|
| EN_MODERN | 1.00 | 1.00 | 1.00 | 1.00 |
| EN_KJV | 1.00 | 1.00 | 1.00 | 1.00 |
| LP1_REAL | 1.00 | 1.00 | 1.00 | 1.00 |
| LATIN | 1.00 | 1.00 | 0.67 | 1.00 |
| OE | 1.00 | 1.00 | 0.71 | 1.00 |
| DE | 1.00 | 1.00 | 0.67 | 1.00 |
| CY | 1.00 | 1.00 | 0.00 | 1.00 |
| EN_HALFVOWEL | 1.00 | 1.00 | 0.42 | 1.00 |
| EN_NOVOWEL | 0.92 | 0.96 | 0.00 | 1.00 |

Minimum L=120 power **0.92** (EN_NOVOWEL, 22/24): identical to round19's 0.92. Gate (>=0.90) passed; target
(>=0.92) met exactly, with zero margin (one replicate). CY = 1.00 on the substitute corpus. The L=120 null matches
round19 (pmax mean 1.647 vs 1.674, k_eff 6.06 vs 6.25). Honest limits: **L=400 was NOT run** (CPU contention);
the L=240 null used 4,000 wrong-key / 40,000 random decodes (reduced from 20,000 / 200,000), so L=240 bars are noisier.
G-FP, G-LP1, G-SPEED were not re-run. See `gate_proof.json`.

## 3. Where the stored survivors are
| negative | stored | form | usable |
|---|---|---|---|
| B-04 | `round13/B04/results_[A-D].json` top-50 per stage | 64-char decoded head (stage D: ~100-char `text`) + legacy score | 225 texts |
| R16-KDF | `round16/KDF/results_A.json` top-50 | 64-char head | 48 texts |
| R16-PRNG | `round16/prng/results.json` best_config etc. | 40-char translit | 20 texts |
| R17-PUBLIC-PAD | `round17/P0..P4/results*.json` bests/top lists | 64-char heads | 5,730 texts (overlapping files; dedup by file+text) |

Only decoded heads (31-55 runes) were stored, never whole-segment decodes.

## 4. Re-adjudication table
Panel `adjudicate()`; bars from round19/I3 `calib19.json` cells `I19:vecbeam.keyskip1+I2`, nearest-L rescaled by 1/sqrt(L), at each lane's N; escalate alpha 0.05 / claim alpha 0.01.

| negative | N decodes | survivor texts | n runes (best) | best pmax_ne (register) | pmax_ne bar esc / claim | best pcon (register) | pcon bar esc / claim | # >= escalate |
|---|---|---|---|---|---|---|---|---|
| B-04 | 6,224,300 | 225 | 53 | 5.36 (LP1_REAL) | 6.37 / 6.76 | 4.42 (LP1_REAL) | 5.98 / 6.33 | 0 |
| R16-KDF | 692,064 | 48 | 48 | 3.97 (LP1_REAL) | 6.05 / 6.46 | 3.18 (LP1_REAL) | 5.57 / 5.94 | 0 |
| R16-PRNG | 52,556 | 20 | 31 | 2.61 (LATIN) | 6.25 / 6.75 | 2.31 (OE) | 5.75 / 6.20 | 0 |
| R17-PUBLIC-PAD | 14,522,916,046 | 5730 | 55 | 7.55 (LP1_REAL) | 8.08 / 8.46 | 5.63 (LP1_REAL) | 7.44 / 7.78 | 0 |

Best z per register across each lane's survivors:

| negative | EN_MODERN | EN_KJV | LP1_REAL | LATIN | OE | DE | CY | EN_HALFVOWEL | EN_NOVOWEL |
|---|---|---|---|---|---|---|---|---|---|
| B-04 | 4.56 | 4.85 | 5.36 | 3.60 | 3.77 | 3.72 | 3.25 | 4.42 | 2.06 |
| R16-KDF | 3.13 | 3.12 | 3.97 | 2.69 | 3.38 | 2.86 | 3.10 | 3.18 | 2.47 |
| R16-PRNG | 2.19 | 2.60 | 2.27 | 2.61 | 2.45 | 1.61 | 1.67 | 1.69 | 1.75 |
| R17-PUBLIC-PAD | 6.96 | 7.39 | 7.55 | 5.67 | 5.59 | 6.50 | 5.81 | 5.66 | 3.10 |

**Result: no survivor in any of the four negatives clears even the ESCALATE (alpha 0.05) bar; no FLAGGED survivor.**
Closest: R17-PUBLIC-PAD best pmax_ne 7.55 vs escalate 8.08 (LP1_REAL register, which is half-KJV and English-like; R17
survivors are dense-prefilter-selected best-of-many so this lane's keyskip1 bar is not exactly their null).

## 5. What this does and does NOT confirm
1. **Survivor-level only.** The stored survivors were ranked by the legacy English score. A Latin/Welsh/vowel-dropped decode
   would have had a low English score and would not be in any top-50 (L7-A: power 0.00-0.33). The table shows that among
   the English-ranked survivors none is a non-English hit; it does NOT show the sweeps would have surfaced one. The
   sweep-level non-English conditional remains and cannot be re-adjudicated (decodes discarded, R3 non-compliance).
   Suggested restatement: "negative under the English ranker; re-scored top-N carry no register-conditional hit under the
   powered 9-register panel (survivor-level, short heads)". That is a partial confirmation, not the full one CAMPAIGN-PLAN hoped for.
2. **Short heads** (31-55 runes): bars rest on 1/sqrt(L) extrapolation from the L=31/120 cells; panel power at L=31 is lower
   (round19/I3 s10.0: EN_NOVOWEL 0.67, HALFVOWEL 0.83, CY 0.92).
3. Bars are I3's, calibrated on the round19 panel. The rebuilt panel's null matched at L=120; L=240/400 bars not re-verified.
4. `pmax_ne` is dominated by LP1_REAL (English-adjacent); `pcon` (conditional on EN) is the cleaner non-English test.

## 6. not_covered
Greek, Hebrew, Norse registers (no corpora fetched; stretch not attempted); Middle-Welsh Mabinogion proper; L=400;
sweep-level (non-top-N) decodes; any decodes beyond the stored heads.

## 7. Files
Lane dir: PREREG.md, RESULTS.md, gate_proof.json, readjudication_table.json, ledger_patches.json, ledger.json,
out_build.json, out_null.json, out_power.json, power.log, models/panel.npz (regenerable), code copies (adjudicate.py,
build_models.py, power.py [nproc=1, LENGTHS=[120,240], null sizes reduced], gates.py [unused], collect.py, rescore.py,
write_deliverables.py), SWEEPROW_ref.md.
Outside lane dir: `data/keys/welsh/welsh_mabinogion.txt`, `data/keys/mabinogion.txt`, `data/kjv.txt` (restored inputs). Nothing written into round19/I2.
