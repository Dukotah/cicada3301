# Round 44 / WAVE-2 CELL B3 — THE 86-DOUBLET-SITE READ — RESULTS

_Run 2026-11-09. PREREG.md (incl. dated Addenda 1-2) preceded every output and is
sha256-stamped in `run.log` before first execution and at each addendum. Instrument:
panel-R36 (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`, sha a0682f0c…) through
the W2-A1 116-map grid; bars = bars_v3's POT model refit on nulls matched to this exact
channel construction at the real L (bars_v3 free has no node below L=120, verified by call;
`bar_v3(928,120,"free") = 11.58` reported non-binding). Pure python3, no network._

## Verdict

**CHANNEL: NEGATIVE at measured power 1.00 for all six verdict-capable readings — the doublet
sites do not carry a panel-visible message in their values, gaps or positions.**
(0 of 928 real readings crossed a bar; no decode is FLAGGED-FOR-ORACLE.)

**FALSIFIER: LOUD FLAG — D-01's flat-Bernoulli residue model is REJECTED on the registered
battery.** T7, the lag-1 autocorrelation of the 85 inter-site gaps, fired at the
pre-registered bar: **observed Pearson ac1 = +0.380** vs null −0.011 ± 0.106
(z = +3.69), two-sided add-one **p = 0.0010 ≤ 0.001428** (Bonferroni/7; family-wise
≈ 0.007 < 0.01) on the D = 10,000 extended null. It is NOT a one-outlier artifact:
leave-any-one-pair-out Pearson stays in [+0.218, +0.420] and Spearman ac1 = +0.269. The
direction is multi-hundred-rune-scale RATE HETEROGENEITY — doublets per 1,000-rune block run
[8,3,7,2,6,9,10,8,11,2,9,6,5] — i.e. consecutive gaps are similar because doublet-poor and
doublet-rich regions exist. The other six statistics (global-position KS, gap dispersion,
mod-29, mod-60, value distribution, per-page dispersion) are all comfortably null (p ≥ 0.23),
which is exactly the signature of SMOOTH regional variation rather than clustering, positional
code or value code. **What this does and does not mean:** it does not resurrect the channel
(all reads negative); it says the residual slip RATE is not constant along the book,
contradicting the uniform-slips picture at a resolution D-01's own coverage field disclosed it
never had (its drift/constancy family: power 0.075–0.195; gap serial correlation was not among
its statistics at all). This is direct measured support for **X0 item 22's REOPEN** (per-page /
regional heterogeneity, "a per-page-heterogeneity test with a real positive control is the
named gap") — a non-stationary filter parameter, a sessioned generation process, or a
rejection-loop variant with state are the candidate mechanism classes for the follow-on lane.

## 1. Positive controls + power (plants.json) — gate passed BEFORE any real read

| plant class (through the full own glue: raw stream → site extraction → channel → grid) | glue recovery | power vs bar |
|---|---|---|
| PLANT-V — 86 doubled values = held-out English window | 40/40 | **1.00** (median pmax 15.21 vs bar 6.00) |
| PLANT-G — 85 gaps = English window + 3 (recovered by grid shift) | 40/40 | **1.00** (median 15.18 vs 6.00) |
| PLANT-P — 86 positions mod 29 = English window (constructed gaps) | 40/40 | **1.00** (median 15.47 vs 6.03) |
| PLANT-C — 55 per-page counts = English window | 40/40 | **0.25** (median 11.71 vs 12.84 — below the 0.5 floor; the counts channel is verdict-INCAPABLE under this instrument, exactly the degenerate-null inflation W2-A1 measured) |
| Battery positive control (PLANT-G's clustered positions must fire T1) | — | **1.00** (40/40 at p = 0.000999) |
| Specificity — 25 untouched surrogate draws, full pipeline | 0 channel crossers, 0 battery fires | clean |

## 2. The real reads (results.json; N = 928 = 8 streams × 116 maps; α = 0.01)

| stream | L | best pmax | bar of record | verdict |
|---|---|---|---|---|
| dblvals_U (doubled runes in order, unsolved 0-54) | 86 | 3.58 | 6.00 | **NEGATIVE** at power 1.00 |
| gapsmod29_U | 85 | 3.60 | 6.00 | **NEGATIVE** at power 1.00 |
| posmod29_U | 86 | 2.79 | 6.03 | **NEGATIVE** at power 1.00 |
| pagecounts_U | 55 | 6.77 | 12.84 | measured-only (stream degenerate: mds 6, IoC·N 6.37 — R38 guard; and plant power 0.25) |
| dblvals_C (full canon incl. AN END + PARABLE) | 89 | 3.43 | 5.97 | **NEGATIVE** at power 1.00 |
| gapsmod29_C | 88 | 3.48 | 6.03 | **NEGATIVE** at power 1.00 |
| posmod29_C | 89 | 2.80 | 6.07 | **NEGATIVE** at power 1.00 |
| pagecounts_C | 57 | 7.00 | 13.01 | measured-only (degenerate, as above) |

Doctrine-R3 statistics for each stream's best map are in `results.json channels.*.best_full`.
The site tuple itself (positions, gaps, values, translit `THXEAJL…`, per-page counts) is
persisted in `results.json real_sites_U86` so nobody has to re-derive it.
Count reconciliation pinned: **86** sites on the 12,956-rune unsolved stream (D-01's object),
**89** on the full 13,136-rune canon (A-06's number), **88** = pages 0-55 (the R43 blind
agents' cut). Same transcription, different segment inclusion.

## 3. The D-01 falsifier battery (U86; α = 0.01 Bonferroni/7 → per-test 0.001428)

Null = site_matched_shuffle (PREREG Addendum 1), D = 1,000 (`nulls.json`) extended to
**D = 10,000** (`battery_ext.json`, PREREG Addendum 2 — the two-sided tests' minimum
attainable p at D=1,000 was 0.001998 > the bar, an attainability defect the addendum fixed
with battery statistics, alpha and decision rule unchanged).

| test | statistic | obs | p (D=10,000) | side | fired? |
|---|---|---|---|---|---|
| T1 | KS of site positions vs uniform | 0.1092 | 0.2409 | one | no |
| T2 | gap CV² (var/mean²) | 0.8924 | 0.7775 | two | no |
| T3 | χ² positions mod 29 | 32.70 | 0.2343 | one | no |
| T4 | χ² positions mod 60 | 50.74 | 0.7738 | one | no |
| T5 | χ² doubled-value counts vs null mean | 27.67 | 0.4543 | one | no |
| T6 | per-page binomial dispersion | 1.091 | 0.5929 | two | no |
| **T7** | **lag-1 gap autocorrelation** | **+0.380** | **0.0010** | two | **YES — LOUD FLAG** |

Battery positive-control power (clustered-position plants, T1): 1.00 (40/40). Specificity on
25 untouched surrogates: 0 fires. An honest caveat: no plant class specifically exercised
SMOOTH rate heterogeneity (the structure T7 found), so T7's power against its own alternative
is not separately measured — what is measured is its false-positive rate (the 10,000-draw
null) and the robustness checks above. The initial D=1,000 run returned T7 at the two-sided
attainability floor (0.001998 — outside all 1,000 draws), which is what triggered Addendum 2.

T7 descriptive context (non-registered, `battery_ext.json`): largest gaps 712/662/553/537;
per-1,000-rune block counts above; null max over 10,000 draws = +0.533 (the observed +0.380
is large but inside the null's extreme range — the p-value, not the maximum, is the verdict).

## 4. Incidental instrument findings (for other lanes)

- **The standing `dfshuffle` (rounds 37-41 null generator) is positionally biased**: it
  repairs bad pairs in array order and stops at the target count, so its residual doublet
  sites cluster at the stream END (one-draw KS vs uniform 0.844; per-page dispersion 6.29)
  and the delivered count undershoots the target (56 observed vs 86 requested). Immaterial
  for its historical use (whole-stream decode scoring); disqualifying for any null over SITE
  POSITIONS. `b3lib.site_matched_shuffle` (uniform-random repair order, exact count) is the
  repaired form. Logged here so no future lane inherits the bias silently.
- The verbatim dfshuffle also has a latent IndexError at i = n-2 (hit when target=0).

## 5. Coverage × not_covered (the three conditionals, PREREG Q4)

**Covered:** the 86-site and 89-site tuples as value / gap / position / count channels ×
116 affine-reversal maps each (928 readings, bars at actual L, N=928, α=0.01, measured power
1.00 on the three verdict-capable channel types); the 7-statistic uniformity battery vs the
flat-Bernoulli instantiation of D-01's model at D=10,000, with battery T1 power 1.00
measured by plants.

**not_covered:**
- *key space:* keyed/derived readings of the channel streams; cross-channel joins;
  site-sets under other doublet definitions (triplet runs, lag-2 pairs); gap encodings
  outside mod-29 shift reach (base-29 multi-digit, varint); sites-as-cribs gating key sweeps
  (VERDICT-OTP-CLASS cap); positions mod 60 as a *read* (tested only as uniformity T4 —
  it is not a 29-ary stream).
- *transition model:* memoryless monoalphabetic on the channel stream only.
- *adjudicator register:* panel-R36's 12 registers at the measured powers; the per-page
  COUNTS channel carries no verdict at all (degenerate real stream + power 0.25) — a
  higher-power counts recognizer (e.g. word/dictionary-level over a 6-symbol alphabet)
  reopens it; numeric/schema registers untested.
- *falsifier:* 7 statistics; power measured for position-clustering structure (1.00), not
  for every conceivable structure class.

## 6. Ledger

Draft rows in `ledger_rows.json` (R44-W2B3-DOUBLET-CHANNEL, R44-W2B3-D01-FALSIFIER).
Cited rows D-01 / A-06 / E-02 untouched; this cell stayed inside X0 item 21's open ground.

## 7. Files

- `PREREG.md` (+ Addenda 1-2) — stamped in `run.log` at each stage
- `b3lib.py` — the single glue (census, channels, grid, surrogate, battery, POT)
- `nulls.py` → `nulls.json` — F1 matched null + F2 SEL cross-check + bars of record
- `plant_gate.py` → `plants.json` — the four plant classes + specificity
- `run_real.py` → `results.json` — the 928 real readings + initial battery
- `battery_ext.py` → `battery_ext.json` — the D=10,000 extended battery (Addendum 2)
