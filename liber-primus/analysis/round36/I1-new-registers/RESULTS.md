# Round 36 / I1 — Greek, Hebrew, Norse registers: RESULTS
_2026-10-30. Pre-registered in `PREREG.md` (+ `ADDENDUM-2026-10-30.md`). No git, one Python process, nproc=1, ~25 min wall._

## Verdict
**All three registers pass the power gate on the mapping-v1 romanisations (no revision used) and enter the panel, giving
`models/panel12.npz` (12 registers). No existing register lost power. The shuffled-LP2 wrong-key `pmax` null moves up
modestly (mean +0.12, 1e-3 bar +0.02..+0.07 at L=120).** This is an instrument result (status: measured), not a decode result.

## Corpora (all public domain, data only, own subdirectory under `corpora/`; per-file URL/sha256/bytes in `fetch_log.json`)
| register | source | files | bytes | runes (train/test) |
|---|---|---|---|---|
| GREEK | Nestle 1904 GNT base text, github.com/biblicalhumanities/Nestle1904 `xhtml/` (site declares public domain) | 27 | 2,152,582 | 693,743 (346,871 / 346,872) |
| HEBREW | Westminster Leningrad Codex, github.com/openscriptures/morphhb `wlc/`: Gen, Exod, Lev, Num, Deut, Josh, Judg | 7 | 9,105,877 | 513,633 (256,816 / 256,817) |
| NORSE | heimskringla.no normalised Old Norse: Egils, Eyrbyggja, Völsunga, Ynglinga, Gunnlaugs, Hrafnkels, Gísla, Fóstbræðra | 8 | 1,661,762 | 943,356 (471,678 / 471,678) |

`Laxdœla_saga` returned 404 (logged FAILED in `fetch_log.json`); Njáls/Laxdæla-type titles were not at the probed URLs.

## Mappings (full rules in `mappings.md`)
Two steps: corpus-specific romanisation to ASCII (`mappings_r36.py`), then the unchanged Round 32 `text_to_runes(.., "EN")` (K,Q->C, V->U, Z->S, greedy TH/EO/NG/OE/AE/IA/EA). Greek: θ TH, φ F, χ CH, ψ PS, η E, ω O, υ Y (U in αυ/ευ/ου), γ-nasal N, rough breathing H. Hebrew: pointed romanisation with vowels from niqqud, א/ע dropped, שׁ SH, שׂ S, צ TS, sheva dropped, vav+holam O / vav+dagesh U, matres lectionis dropped. Norse: þ ð TH, æ AE, œ ø ö OE, ǫ ó O, other accents stripped, j kept as rune J. Letters with no rune: none. v2 revisions exist in code but were **not run** (not needed).

## 12-register power gate (24 reps, pmax power at matched-FP bar; Round 32 value beside the nine)
Bars (pmax, 12-panel, real-LP2 wrong-key): pre-registered null (n=4000/2000) L=120 4.370, L=240 4.706; larger null (n=20000/10000) 4.439 / 4.778. Round 32 (nine, n=8000/4000): 4.422 / 4.922. Powers are identical in both runs.

| register | L=120 R36 | L=120 R32 | L=240 R36 | L=240 R32 | median own-z (120/240) |
|---|---|---|---|---|---|
| EN_MODERN | 1.000 | 1.00 | 1.000 | 1.00 | 17.4 / 24.6 |
| EN_KJV | 1.000 | 1.00 | 1.000 | 1.00 | 18.5 / 26.8 |
| LP1_REAL | 1.000 | 1.00 | 1.000 | 1.00 | 18.2 / 29.4 |
| LATIN | 1.000 | 1.00 | 1.000 | 1.00 | 18.0 / 25.5 |
| OE | 1.000 | 1.00 | 1.000 | 1.00 | 13.5 / 19.8 |
| DE | 1.000 | 1.00 | 1.000 | 1.00 | 20.2 / 29.0 |
| CY | 1.000 | 1.00 | 1.000 | 1.00 | 15.4 / 22.0 |
| EN_HALFVOWEL | 1.000 | 1.00 | 1.000 | 1.00 | 13.2 / 19.2 |
| EN_NOVOWEL | **0.917 (22/24)** | 0.92 | 1.000 | 1.00 | 12.1 / 18.5 |
| **GREEK** | **1.000** | – | 1.000 | – | 19.7 / 28.5 |
| **HEBREW** | **1.000** | – | 1.000 | – | 17.8 / 26.8 |
| **NORSE** | **1.000** | – | 1.000 | – | 18.1 / 25.4 |

Gate: new registers >= 0.90 at L=120: **pass x3** (target 0.92 also met). Existing registers within 0.02 of Round 32: **pass x9** at both L (EN_NOVOWEL 0.917 vs 0.92 recorded is the same 22/24; it has no spare margin, but adding registers cost it nothing). Scoring the same null draws with a 9-panel bar and a 12-panel bar gives identical powers for all nine. Minimum planted pmax for the new registers is 15.2 (L=120) / 22.3 (L=240) against bars of 4.4 / 4.8, and each planted text's argmax register is its own in 100% of reps. Caveat: 24 reps, so 24/24 has a Wilson lower bound of 0.86; the margin in z is the stronger evidence.

## Null shift 9 -> 12 registers (L=120, `null_shift.json`)
| null | statistic | pmax (9) | pmax (12) |
|---|---|---|---|
| shuffled-LP2, n=2000 | mean / sd | 1.669 / 0.799 | 1.790 / 0.775 |
| | q0.99 / q0.999 / max | 3.665 / 4.523 / 5.171 | 3.736 / 4.523 / 5.171 |
| | GPD 1e-3 bar | 4.633 | 4.655 |
| real-LP2 wrong-key, n=20000 | mean / sd | 1.641 / 0.793 | 1.773 / 0.766 |
| | q0.99 / q0.999 / max | 3.607 / 4.385 / 5.300 | 3.710 / 4.428 / 5.300 |
| | GPD 1e-3 bar | 4.374 | 4.439 |

The shuffled and real-LP2 nulls agree, each new register wins the argmax 7-10% of the time (roughly uniform over 12), and the bar rises by about 0.02-0.07. These are gate-beam (keyskip, English-ranked) numbers; **B1 must refit with v3**, whose beam changes the decodes. The family-wise far tail (N ~ 1e6) is not estimated here.

## Consumers
`adjudicate.Panel(path)` loads any register count; `adjudicate_batch`, `pcon` and `pmax_ne` derive the non-English set by name, so 12 registers need no code change. `beam_v3.panel_max` reads `pan.registers` and loads from `panel12.npz` once `PANEL_PATH` is repointed (smoke-tested: 12 registers, weight table 24389x12). `beam_v3.CLUSTERS` is a hard-coded 7-cluster list, so `register_cond` would silently ignore the new three until clusters are added. `adjudicate.ROW_DTYPE` has `("z","<f4",(9,))` and `validate_row(n_registers=9)` defaults: binary SWEEPROW rows and validation must be widened to 12 for new stores; old 9-wide stores stay 9-wide.

## Reproducibility
`python fetch_r36.py` then `python build_models_r36.py` (28 s) rebuilds `panel12.npz`. Default mode carries the nine LMs, LP1-LOO models and test halves verbatim from the Round 32 files; `--nine=rebuild` rebuilds all twelve from disk corpora. Finding for P1: the rebuilt nine differ from the Round 32 panel (max |LM| diff: EN_MODERN 0.049, EN_KJV 0.317, LP1_REAL 0.158, EN_HALFVOWEL 2.43, EN_NOVOWEL 0.066; LATIN, OE, DE, CY exactly 0) because the on-disk EN-family source corpora no longer match the Round 32 build (rune totals differ by tens to hundreds). The null calibration of the carried nine reproduces Round 32's mu/sd/corr to 1e-8.

## Conditionals (Doctrine Q4)
1. Key space: none swept (instrument lane). 2. Decoder transition model: Round 32 keyskip beam (400,3) with the CORRECT key handed over; other relations are not measured here. 3. Adjudicator register: 12 registers, the new three only as written by the stated romanisations; unpointed Hebrew, other Greek/Norse conventions, other scripts and non-trigram-detectable text remain uncovered. L=400 not run; 24 replicates; plants are same-register held-out text, not independent authors.
