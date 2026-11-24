# Round 45 / LANE T1 — T7 MECHANISM, HONEST NULLS — RESULTS

_Run 2026-11-23 (UTC 2026-11-24). `PREREG.md` was sha256-stamped into `run.log` before any script ran;
Addendum 1 (exploratory) and Addendum 2 (descriptive) were stamped before their scripts. Pure
python3 + numpy/scipy (both already installed), no network, no decodes. Census halt gate passed:
86 events, identical to B3's `real_sites_U86`._

## Verdict

**T7 replicates, but it is NOT rate heterogeneity at any scale this instrument can see. And 86
events cannot separate the candidate generation mechanisms at the effect size the data supports.**

1. **The registered smooth-heterogeneity statistic is completely null on the real data.** S3 (the
   random-walk log-rate HMM likelihood-ratio test) has σ̂ = 0, LRT = 0.000, p = 1.0. Its gate
   passed, with power 0.865 against the strong drift plant (P-M2 at σ_L = 0.8, α = 0.01) and a
   0.02 false-fire rate on M0, so this is a powered null. The multi-scale Fano statistic
   (S4, p = 0.38) and the free change-point LRT with look-elsewhere control in its null (S5,
   p = 0.62) are null too. Only the gap-ordering statistics fire: S1 (T7) = +0.380, p = 0.0010,
   and S2 (rank AC) = +0.268, p = 0.006. Registered threshold 2 ("non-stationarity confirmed iff
   S3 p ≤ 0.01") therefore **does not fire**.
2. **No rate mechanism reproduces T7 jointly with a flat rate profile** (E1, exploratory). Under
   every heterogeneity plant, T7 ≥ 0.380 happens 3–19 % of the time, but the observed *joint*
   pattern (T7 ≥ 0.380 and S3 = 0) occurred 0 / 3,500 times. Under M0 it occurred 1 / 10,000
   times. A rate process strong enough to push T7 to 0.38 is almost always also seen by S3. The
   observed combination looks like a tail event of the gap sequence, not a regional rate change.
3. **T7 is concentrated.** Two gap pairs inside the 2739–4388 void (400→712→537) carry 0.21 of
   the 0.38. The top 5 pairs carry 0.29, and without them T7 = 0.09 (E0). **A single extra
   doublet** at any of about 740 positions (5.7 % of the stream, mostly 3040–4035, plus
   1565–1620 and 9570–9625) would push T7's p above 0.01; at the worst position it drops T7 to
   0.17 (p = 0.10) (E0b).
4. **Mechanism discrimination: the frozen rule calls M3a "favoured". That label is weak and
   unrelated to T7. Everything else is "not separable at n = 86".** No mechanism meets the
   "decisive" or "disfavoured" bar.
5. **M4, a pure renewal rejection loop (rate depends only on the time since the last slip), is
   excluded as the T7 mechanism** under registered threshold 5. Its T7 95th percentile is
   0.15–0.17 (Stage A) and 0.154 (Stage B), against 0.380 observed.

## 1. Detection statistics (real data; null = 2,000 M0 draws; `results.json detection`)

| stat | what it sees | observed | p | power vs P-M2 σ_L=0.8 (α=.01) | power vs P-M1c σ_L=0.8 |
|---|---|---|---|---|---|
| S1 T7 (Pearson gap AC) | gap ordering | +0.380 | **0.0010** | 0.295 | 0.225 |
| S2 rank gap AC | gap ordering | +0.268 | **0.006** | 0.32 | 0.245 |
| **S3 RW-HMM LRT (PRIMARY)** | smooth rate drift | **0.000 (σ̂=0)** | **1.0** | **0.865** | 0.655 |
| S4 multi-scale Fano (250–2000) | regional count dispersion | z_max 0.875 | 0.38 | 0.78 | 0.59 |
| S5 free change-point LRT (K≤6) | sessions at any position | −4.17 | 0.62 | 0.795 | 0.63 |

Gate (threshold 1): S3 power 0.865 ≥ 0.5 and false fire 0.020 ≤ 0.02 → **PASS**. The false-fire
rate sits exactly on the bar; S3 has a point mass at 0, so its p-values are conservative. Q5 kill
check: continue.

**The R44 gap is now measured.** T7's power against smooth heterogeneity is only 0.14–0.30 at
α = 0.01 (P-M2 σ_L = 0.5 / 0.8). S3, S4 and S5 have 2–3× more power against every session/drift plant class
(`plants.json`). T7 is the *weakest* of the five instruments against rate heterogeneity, and it is
the only one that fires.

## 2. Model comparison on the real data (`results.json models`)

| model | logL | k | ΔBIC | BIC weight | held-out ΔlogL vs M0 |
|---|---|---|---|---|---|
| **M3a** rate ~ position-in-section | −514.50 | 2 | **0.00** | 0.51 | **+2.20** |
| M0 stationary | −517.28 | 1 | 1.11 | 0.29 | 0 |
| M4 gamma renewal (κ̂ = 1.22) | −516.14 | 2 | 3.28 | 0.10 | +0.54 |
| M1c free sessions (K̂ = 1, cp at 4575) | −514.91 | 3 | 5.28 | 0.04 | 0.00 |
| M3b rate ~ position-in-page | −517.19 | 2 | 5.38 | 0.03 | 0.00 |
| M2 smooth drift (σ̂ = 0) | −517.28 | 2 | 5.56 | 0.03 | 0.00 |
| M1a chapter sessions | −514.70 | 8 | 27.14 | ~0 | −2.02 |
| M1b section sessions | −511.78 | 17 | 61.38 | ~0 | −3.04 |

**M3a fit:** log λ = −4.60 − 0.89·Z3. The rate falls from ≈ 10.0 to ≈ 4.1 per 1,000 pairs from
the start of a section to its end. Nominal LRT vs M0: 2ΔL = 5.56 on 1 df (p ≈ 0.018 before
correcting for 2 continuous covariates). The classifier picks M3a under pure M0 3.5 % of the time
(70 / 2,000 null draws) and 2.5 % in Stage B. **Its Stage-B T7 distribution is median 0.005,
95th percentile 0.19, so M3a does not explain T7.** It is a separate, weak, uncorrected-for-history
observation that needs out-of-sample replication before anyone reads it as a mechanism.

Chapter rates per 1,000 (descriptive): 5.5, 5.2, 5.2, 5.3, **10.8, 9.1**, 7.1, 6.3. Chapters 5–6
(runes 5506–7960) run about 2× chapters 1–4, but the chapter model loses by ΔBIC 27 and on
held-out data. This agrees with the external finding that T7 survives chapter conditioning: T7
is not a chapter-rate effect.

## 3. Confusion matrices (rows = planted, columns = BIC choice)

**Stage A (fixed plants, σ_L = 0.8, 200 each)** — heterogeneity is *detected* but not *identified*:

| planted \ chosen | M0 | M1a | M1b | M1c | M2 | M3a | M3b | M4 |
|---|---|---|---|---|---|---|---|---|
| M0 | 145 | 0 | 0 | 33 | 0 | 8 | 7 | 7 |
| M1a chapters | 14 | **25** | 0 | 153 | 8 | 0 | 0 | 0 |
| M1b sections | 13 | 11 | **0** | 159 | 15 | 0 | 1 | 1 |
| M1c free sessions | 30 | 0 | 0 | **167** | 1 | 2 | 0 | 0 |
| M2 smooth drift | 9 | 0 | 0 | 179 | **8** | 3 | 0 | 1 |
| M3a | 0 | 0 | 0 | 0 | 0 | **200** | 0 | 0 |
| M3b | 0 | 0 | 0 | 0 | 0 | 0 | **200** | 0 |
| M4 (κ = 0.4) | 0 | 0 | 0 | 12 | 53 | 0 | 0 | **135** |

At σ_L = 0.5 the same pattern holds, with 23–30 % of plants falling back to M0. The M3a and M3b
recall of about 1.0 reflects how specific those covariates are; they are almost invisible to
S1–S5 (S3 power 0.03–0.7). **Sessioned generation (M1a/b/c) and smooth drift (M2) are
indistinguishable at 86 events: all collapse to "M1c".** Structural sessions are recovered
≤ 13 % of the time.

**Stage B (parametric bootstrap at the real-data fits, 200 each)** — recall / calibrated precision
(uniform prior over rows): M0 0.80 / 0.16; M1a **0.00** / –; M1b **0.00** / –; M1c 0.43 / 0.25;
M2 **0.00** / 0.00 (σ̂ = 0, so the M2 plant is M0); M3a **0.555 / 0.78**; M3b 0.03 / 0.13;
M4 0.205 / 0.66. At the effect sizes the data actually supports, every structural and drift
mechanism is classified as M0 57–80 % of the time. **86 events cannot separate these mechanisms.**

Verdicts under frozen threshold 3: M3a **favoured** (lowest BIC, recall 0.555 ≥ 0.5, precision
0.78 ≥ 0.6; *not* decisive, since ΔBIC to M0 is 1.1 < 6). Every other model is **not separable
at n = 86**. No model is "disfavoured": M1a/M1b lose by ΔBIC 27/61, but their Stage-B recall
is 0, so losing carries no information.

## 4. Where do the rate changes fall? (threshold 4)

The best free change-point fit is K = 1 at pair 4575 (rate 4.6 → 7.8 per 1,000; 21 | 65
events). **BIC prefers K = 0**, so there is no supported change point. Higher-K fits put
boundaries at 2750 / 4375 (the void edges) and 8950 / 9575 (the second-longest gap). Coincidence
tests on the K̂ = 1 point (uniform-grid null, 10,000 draws, per-set α 0.0025): chapter ends
p = 0.82, section ends p = 0.95, page starts p = 0.11 (4575 is 13 pairs after page start 4562),
10-dot pages p = 0.65. **No coincidence with any structure.** The M2 posterior rate profile is
flat (6.64 / 1,000 everywhere), with no low-rate regions. Descriptive: the 10-dot pages hold
3 / 0 / 0 doublets (segments 36 / 38 / 49). The 662 gap (8933–9595) spans the red numbered list
(8805–9229, 1 doublet) and the 10-dot page 38. With n this small that is suggestive only.
Solved pages (AN END, PARABLE) lie outside the 12,956-rune stream, so they cannot be tested here.

## 5. Exploratory (Addendum 1 / 2 — cannot change any verdict above)

- **E1 (`addendum.json`)**: P(T7 ≥ 0.380 and S3 = 0): M0 0.0001 (n = 10,000); P-M1a, P-M1c and
  P-M2 at σ_L 0.5 / 0.8, and the E2 plant, all 0 / 500 (95 % upper bound ≈ 0.006 each).
  P(T7 ≥ 0.380) alone under those plants is 0.03–0.19. Conditional on T7 firing under a rate
  plant, S3 is ≠ 0 in 100 % of 3,500 draws (e.g. P-M2 σ_L = 0.8: 94 T7 hits, 0 with S3 = 0).
- **E2 fast-switching two-state rate model** (dwell 2–32 bins, ratio 1.5–10): LRT 0.18,
  p = 0.37. Plant power 0.58 at ρ = 4 and a 300-pair dwell. Null.
- **E0 / E0b**: the concentration and fragility numbers are in the Verdict, item 3
  (`fragility.json`).

## 6. What each surviving mechanism would imply, and the follow-up

- **Stationary leak + T7 as a tail fluctuation (M0).** This is consistent with every rate
  statistic. T7's p ≈ 0.0005–0.001 is real for *this one statistic*, but the statistic was
  selected after a long project history of doublet tests. Under M0 the generation process is
  D-01's flat filter and there is nothing to chase. **Implies:** no new generation-model lane.
- **Non-renewal short-memory gap process (a stateful loop whose state survives across one
  slip).** Pure renewal (M4) is excluded. A Markov-renewal process, in which gap n+1 depends on
  gap n, would produce gap AC without a visible rate change. It is **not testable
  non-circularly on these 85 gaps**, because T7 *is* that model's natural statistic. It needs an
  independent event stream.
- **M3a (section-position rate decay).** If it were real, the filter would leak more early in
  each section, which fits a per-section restart of the generator state. Evidence is weak
  (ΔBIC 1.1, held-out +2.2, about 3 % false-pick rate under M0) and unrelated to T7.
- **Sessioned generation / drifting filter (M1a/b/c, M2).** Not supported: σ̂ = 0, BIC
  prefers K = 0, and there is no structural coincidence. These are also unidentifiable at
  n = 86, so this is "not seen at power 0.6–0.87 against σ_L = 0.8", not "excluded".

**Bounded follow-up this raises the prior on: route E0b's intervals to lane S1 (transcription
audit).** T7's significance rests on the absence of doublets across ~740 specific positions,
mostly runes 3040–4035 (inside the 2739–4388 void), plus 1565–1620 and 9570–9625. One misread
that hid a doublet there would drop T7 to p ≈ 0.1. Re-reading those image lines for any adjacent
pair where a misread could hide an equal pair is finite: about 1,100 runes, roughly 5 page
images. It either hardens T7 or dissolves it. No generation-model sweep is warranted.
Mechanism identification, if T7 survives the audit, needs a second independent filtered-event
stream. None is known in the corpus.

## 7. Coverage × power and the three conditionals

**Covered:** 8 mechanism models × 4 pre-registered covariates on the 86-event stream; 5 detection
statistics with power measured against 7 plant classes × 2 strengths (200 each) plus M0
specificity; Stage-B parametric bootstrap at the real fits (8 × 200); 2-fold held-out;
change-point coincidence against 4 structure sets; exploratory E1 (13,500 draws), E2 and E0b.

**not_covered:**
- *model space:* Hawkes/self-exciting loops; Markov-renewal (gap-dependent) loops; AR(1)
  mean-reverting drift distinct from the RW; per-rune-value or plaintext-coupled rates; page as a
  55-level factor (C5 covers it); dot diamonds located by image position (only approximate,
  descriptive).
- *generation/transition model:* lag-1 equality events on the pair axis of the transcribed
  unsolved stream only (no triplets, no lag-2); depends on the krisyotam/rtkd transcription,
  which E0b shows T7 is fragile to.
- *register:* N/A (no plaintext adjudicator). The covariate set Z1–Z4 is the analogue.

## 8. Files

`PREREG.md` (+ Addenda 1–2), `run.log` (stamps + all stdout), `t1lib.py` (the single code
path), `run_plants.py` → `plants.json`, `run_real.py` → `results.json`, `addendum.py` →
`addendum.json`, `fragility.py` → `fragility.json`, `ledger_rows.json`. Reproduce:
`python run_plants.py && python run_real.py && python addendum.py && python fragility.py`
(≈ 15 + 8 + 15 + 1 min on a contended machine. Windows throttles detached background python
about 15×, so run in a foreground shell.)

---
_Closing stamp: lane T1 complete 2026-11-23 (UTC 2026-11-24). All registered thresholds applied
as frozen. Exploratory items labelled. Nothing committed and LEDGER.json untouched (rows in
`ledger_rows.json`)._
