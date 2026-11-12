# Round 44 / P1 — THE RED-INK CHANNEL, READ IN FULL — RESULTS

_Run 2026-11-09. PREREG.md (incl. dated Addendum 1) preceded every output. Instrument:
panel-R36 (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`) with bars_v3 `free`
bars FIXED at N=10,000 before any run. Positive controls: **3/3 PASSED through this lane's
own extraction+decode glue** (R42 X1 rule). Doctrine gates honoured throughout._

## Verdict

**Readings: NEGATIVE — 7,460 decodes, 0 bar-crossers, nothing FLAGGED-FOR-ORACLE.**
**Census: MEASURED — the red channel is now enumerated completely for the first time, and the
census CORRECTS the prior-art extraction in five concrete ways (below).** The red ink remains
what prior art called it — rubrication of each page's opening words plus ornament furniture —
but the corrected, complete selection stream and all its pre-registered readings are now on
the record at 12-register power instead of the old English-only scorer.

## 1. Positive controls (plant_results.json)

| plant | what it proves | result |
|---|---|---|
| P1 | image → own red-mask extractor → reader, END TO END: 120-rune known plaintext painted as a red selection over 13 no-red page copies | extracted 120/120, **exact recovery**, direct reading pmax 26.367 ≥ bar 12.8507, non-degenerate → **PASSED** |
| P2 | dot-block census: planted 13-dot + 10-dot red blocks on a page copy | blocks found [13, 10] exactly → **PASSED** (first attempt failed because the blocks were painted over text and correctly classified RUNE_OVERLAP; placement moved to the margin — a GLUE fix, threshold untouched, within the Q5 allowance) |
| P3 | reading-C decode glue: known plaintext enciphered with prime_totient offset 17 (vigm) fed through the SAME sweep function | planted cell found (gen=prime_totient, offset=17, cfg=vigm), plaintext recovered, pmax 38.321 ≥ bar 17.1842 → **PASSED** |

## 2. The census (census.json — the complete finite object)

All 56 relikd masters swept with the verified rule `R−(G+B)/2>40 & R>120 & G<80`;
**645 red components ≥ 20 px**, each classified exactly once:

| class | n | identity |
|---|---|---|
| RUNE_OVERLAP | 191 | red text-rune glyphs (187 true red canon runes over 186 boxes (the merged img33 box carries 2 runes: ᚳᛟ) + 1 red numeral "4" missegmented as a rune + multi-part glyphs) |
| DROP_CAP | 13 | red drop-cap initials (height-excluded from all prior reads) |
| DOT | 420 | 64 proximity blocks: **27× 13-dot diamonds**, **3× 10-dot diamonds** (imgs 36, 38, 49), 31× single + 2× double + 1× quadruple red word-separator dots inside red text lines |
| OTHER | 21 | 9× the p15 red TITLE runes, 4× the p53-image red closing word, 4+4× red Arabic numerals (digits of grid `3299`; margin `1 2 3 5`) |

Validation gate: reproduces the prior-art 187 glyph-level reds and canon-p0
`HEOGMIAFSYENGC` exactly — **PASSED**.

**Five corrections to the prior-art (armada_osint/redrune) stream:**
1. The "red rune ᚱ" at img37 gli418 is the red Arabic numeral **4** missegmented as a rune
   (crops/p37_four_zone.png). The margin numerals **1,2,3,4,5** (imgs 36–38) are all red.
2. The img33 wide red box (gli369 gi4) is TWO canon runes `ᚳᛟ` merged by the segmenter
   (crops/p33_gli369.png): the prior stream carried a phantom `U` there.
3. The p15 red TITLE line `FULM AEAYOEA` (canon 3603–3611, 9 runes) sits on a line the stones
   segmentation never held — never extracted, never read, though present in canon.
4. The red closing word `URPN` (canon 12644–12647, on the img-p53 bottom line,
   crops/p53_bottomline_full.png) — same blind spot.
5. The **13 red drop-cap initials** (`SLPAXLUMDNGIAFA` in canon order) are red canon runes
   excluded from every prior red read.

**The corrected complete red selection = 213 canon runes on 13 canon pages**
(`channel.json full`): r_p = {0:13, 3:19, 6:11, 7:14, 8:12, 15:20, 23:16, 27:19, 33:18,
39:3, 40:8, 52:51, 53:9}. Every red run remains that page/section's own opening words (the
title and URPN are the canon's own first/last line of their pages) — the rubrication verdict
survives the corrections.

**Red numerals:** margin list labels `1 2 3 4 5` all red; grid cell `3299` red (3299 mod 29
= 22 = `OE`; 3301 − 3299 = 2). **Dot blocks:** the 13-dot/10-dot stream in book order has 30
symbols; as bits (13→1): `111111111111111111111001110111` (the three 10-dot diamonds sit on
imgs 36, 38, 49) — results.json families.B holds the exact sequences (recorded enumeration;
too short for any panel verdict, see §4).

## 3. Readings vs the fixed bars (results.json)

| family | N decodes | best pmax | bar (L_cap) | crossers |
|---|---|---|---|---|
| A1 selection streams {legacy187, corrected200, full213} × fwd/rev × 58 affine | 348 | 2.852 (legacy187 rev, a=28 s=14, reg LP1_REAL-adjacent) | 12.8507 (120) | 0 |
| A2 per-section substream (only section 7, 68 reds, qualified; sections 0–6 have 11–44 reds < 60 → not adjudicable) | 116 | 3.164 | 12.8507 (120) | 0 |
| A3 red-as-key over the 12,923-rune black remainder, {legacy187, full213} × fwd/rev × 6 cfgs × all rotations | 4,800 | 1.239 | 21.5296 (729) | 0 |
| B dot/numeral standalone stream | 0 (enumeration only) | — | none exists at L=30 | — |
| C red parameters {r_p, firstpos_p, cum_p} × {prime, prime−1, totient} × 6 cfgs × 55 pages | 2,196 | 3.684 (page 50, totient, offset 153) | 12.8507 (120) | 0 |
| **total** | **7,460 ≤ N=10,000** | **3.684** | — | **0** |

Doctrine-R3 statistics for each family's best decode are persisted in
`results.json families.*.best_full_stats` (en, ioc·N, mds, h2, zl, pmax_ne, pcon, degenerate).
Every best is an order of magnitude below its bar; nothing approached FLAGGED-FOR-ORACLE.

## 4. Coverage × not_covered

**Covered (fraction of red marks consumed):** 645/645 red components (100%) are classified
and consumed: reading A consumed 216 (185 rune boxes + 13 drop-caps + 9 title + 4 URPN +
multi-part composites), reading B consumed 429 (420 dots + the 9 numeral components incl.
the missegmented "4"). Reading C consumed the derived per-page statistics of the full213
stream. The selection channel is read at panel-R36 power over the affine family fwd/rev; the
key channel over periodic additive/Beaufort/atbash at every rotation; the parameter channel
over the three solved-page generators at three red-derived offsets per page.

**not_covered (the three conditionals, from PREREG §2 Q4):**
- *key_space:* other functions red→key (e.g. red positions as transposition order, red counts
  as per-LINE resets, cross-page red permutations); chroma bands outside the red rule;
  sub-20-px components (JPEG chroma noise floor); red marks on non-page artifacts
  (0_wisdom.jpg).
- *transition_model:* chained/output-aware constructions (the pinned LP2 model) are NOT
  representable by these decoders; a red channel that parameterises the chained filter would
  not be seen here.
- *adjudicator_register:* panel-R36's 12 registers only; numeric/schema payloads, Hebrew,
  Greek not covered. Streams/sections with L < 60 (sections 0–6; the 30-symbol dot stream;
  the 6-value numeral stream) have NO adjudicable bar — they are enumerated verbatim in
  results.json and census.json instead (bounds, not verdicts).

**Reopens if:** (i) a bar is built for L < 60 streams (the dot/numeral enumerations are
preserved ready-to-score); (ii) a reset-capable or chained decoder takes the red parameters
as input (R1-lane territory); (iii) anyone finds red outside the 56 masters' red-rule band
(e.g. a second ink tone — the B-12 p15 `3299` reopener is hereby DISCHARGED for the red
tone: it is red, it is one of 16 grid values, and the grid readings belong to lane P2).

## 5. Files

- `PREREG.md` (+ Addendum 1, dated before any reading) — hypothesis, Aiming Test, fixed bars
- `census.py` → `census.json` — the complete red-mark enumeration (validation gate inside)
- `extract_channel.py` → `channel.json` — the corrected selection streams + per-page params
- `plant.py` → `plant_results.json` — the three positive controls (all passed)
- `readings.py` → `results.json` — A1/A2/A3/B/C vs the fixed bars; `best_stats.py` appends
  doctrine-R3 statistics
- `ledger_rows.json` — three draft rows (census/measured, selection/negative,
  keyparam/negative); LEDGER.json itself NOT modified
- `crops/*.png`, `plant_work/` — visual evidence / plant workspace (regenerable; candidates
  for a .gitignore block per repo policy — coordinator's call)

Reproduce: `python3 census.py && python3 extract_channel.py && python3 plant.py &&
python3 readings.py && python3 best_stats.py` (pure python3, no network).


> **X1 correction (2026-11-09):** PREREG Addendum 1's stream names `corrected199`/`full212` are superseded by the implemented `corrected200`/`full213` (and corrected200 = 187 red canon runes + 9 title + 4 URPN). Artifacts and all N accounting were always consistent; prose only.
