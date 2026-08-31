# P3 — PANEL-MAX NULL + SEED PRIOR + DRIFT RE-BASELINE — results

_Round 20, Phase P. Pre-registered in [`PREREG.md`](PREREG.md) before any statistic was measured.
Fixes the single bar every Phase-S lane will adjudicate against (P3a), replaces Round 8's flat
seed prior with L8's evidence ranking (P3b), and re-baselines the fragile decode channel under the
repaired `drift_rec` beam (P3c). This lane scores no LP2 decode; the P-gate is not released here._

## Verdict

| sub-task | verdict | one line |
|---|---|---|
| **P3a** panel-max direct null | **PASS** | ONE canonical panel-max bar published per I1 preset (`panelmax20.json` / `panelmax20.py`); plant-recovery gives correct-key `pmax` power **1.00** on LP1_REAL/LATIN/OE/half-vowel under `exact`, wrong-key **0.00**; G-CAL on a fresh seed-3301 null passes (ratio 1.042 at the gating block, conservative above). |
| **P3b** seed prior | **PASS** | L8's **433** ranked candidates emitted as `seedprior20.json` + a callable ordering; round-trip 0 mismatches, rank 1 = **1325734783**, tier order A>B>C>D monotone. |
| **P3c** drift re-baseline | **PASS** | OE `pmax` shortfall **confirmed** under repaired `drift` (median 13.543 vs bar 13.842, shortfall **0.299**; I3 ref 13.40/0.44). Derail curve re-measured on `drift_rec` vs `keyskip1` — fragile-decode-channel bound holds (see §3). |

**PREREG Q5 kill condition: NOT met.** The plant-recovery control reproduces I3's §7.1 finding
(panel-max `pmax` power ≥0.90 where the English `en` bar is 0.00 on ≥2 non-English registers), so
the premise "adopt a direct panel-max null" is supported and the lane ran in full.

**Trust anchor.** Before and after: `tests/validate.py` → ALL VALIDATIONS PASSED (rig reproduces
known solves). `analysis/round20/P3/test_p3.py` → 4 passed.

---

## P3a — the ONE panel-max direct null (resolves I3's G-PANEL failure)

**The problem I3 left open.** I3's `G-PANEL` FAILED as pre-registered: its two per-register
effective-test-count estimators disagreed by **2.06–2.45×** (I3 §6.2), so **no single k_eff
describes the 9-register panel** — the registers are not on commensurable per-draw scales (null
locations span −7.09 to −1.48; tail scales span a factor of 14). I3 §6.4 adopted R1's B-i/B-ii
recommendation *in principle* — "stop correcting for a number of tests; calibrate a **direct null
on the panel maximum**" — but left the bar spread across raw calibration cells with no single,
self-describing object for a Phase-S lane to call. This lane closes that.

**What was built.**
- `panelmax20.json` — the canonical bar object: per I1 preset, the (μ, β, M, status) of the
  directly-fitted panel-max cell + claim/escalate bars at N_round ∈ {10⁴,10⁵,10⁶,10⁸}, with all
  three conditionals (null generator, decoder relation, adjudicator register) attached.
- `panelmax20.py` — the callable `panelmax_bar(preset, n_round, alpha)` /
  `panelmax_contract(...)`. It **only** returns the `pmax` bar; there is no `en` path and no −5.5
  floor by construction, and it **refuses an unknown preset** (raises `KeyError`) rather than
  silently substituting the English/keyskip1 bar — the exact L7-C.3 error Round 18 found Round 17
  committing.

**The canonical bar, per preset** (α=0.01 CLAIM, statistic = `pmax`, L=120):

| preset | decoder relation | cell | μ | β | M | status | **claim bar @ N=10⁶** |
|---|---|---|---|---|---:|---|---:|
| `exact` | keyskip1 (repo) | `I19:vecbeam.keyskip1+I2\|pmax\|L120` | 2.3575 | 0.28653 | 1,000,000 | **CALIBRATED** | **7.634** |
| `pair` | keyskip2 (covers L7-B skip_by_two) | `I19:driftbeam.pair+I2\|pmax\|L120` | 2.4200 | 0.26953 | 60,000 | PROVISIONAL | 7.384 |
| `exact_ms8` | keyskip1 ms=8 | `I19:driftbeam.exact_ms8+I2\|pmax\|L120` | 2.0278 | 0.32017 | 60,000 | PROVISIONAL | 7.924 |
| `drift` | permissive drift_rec (lam=12, max_free=2) | `I19:driftbeam.drift+I2\|pmax\|L120` | 5.8995 | 0.43129 | 15,000 | PROVISIONAL | 13.842 |

These are fitted on the **decoder-output null** (wrong-key beam decodes), not on random runes, so
the bar is on the right scale even though I2's *nominal* z scale is not (I3 R-I2-2: I2's internal
`Panel.cal` standardises on a random-rune bulk sd and understates the decoder-output null by ~5×
at keyskip1, ~8× at drift). **The `exact` bar is the load-bearing one — CALIBRATED at M=10⁶.** The
others are carried at I3's measured M (unchanged, not degraded); an S-lane using them stores the
`PROVISIONAL` status in its SWEEPROW header via `panelmax_contract`.

### P3a positive control — plant recovery (the recognizer)

Plant the correct `sha256_ctr(CICADA3301)` key over each of the 9 registers, decode through the
actual instrument, adjudicate, and read `pmax` power at the published bar vs a wrong key
(nrep=10, L=120, N_bar=10⁶; `out_plant_recovery.json`):

**`exact` preset, claim bar `pmax` = 7.634:**

| register | median recovery | **correct-key `pmax` power** | wrong-key `pmax` power | `en` power @ new bar | `en` power @ fixed −5.5 |
|---|---:|---:|---:|---:|---:|
| LP1_REAL | 1.00 | **1.00** | 0.00 | 1.00 | 1.00 |
| LATIN | 1.00 | **1.00** | 0.00 | 1.00 | 0.80 |
| OE | 1.00 | **1.00** | 0.00 | 0.90 | 0.70 |
| EN_HALFVOWEL | 1.00 | **1.00** | 0.00 | 0.80 | 0.40 |
| EN_NOVOWEL | 0.84 | 0.70 | 0.00 | 0.00 | 0.00 |
| RAND *(neg. control)* | 0.29 | **0.00** | 0.00 | 0.00 | 0.00 |

**This is the measured recovery that licenses the bar.** On the four PREREG gate registers the
panel-max bar gives correct-key power **1.00** with wrong-key power **0.00** — it separates a
planted correct key from noise cleanly. It reproduces I3 §7.1's headline: the panel-max statistic
gives ≥0.90 power where the English bar gives 0.00 (EN_NOVOWEL) or 0.40–0.90 (half-vowel/OE). The
negative control (uniform-random plaintext) scores 0.00 on every statistic. `EN_NOVOWEL` recovery
is 0.84 and its power 0.70 — a hit there is **detection, not readable plaintext** (I2), flagged as
such in the bar object.

### P3a G-CAL — the adopted bar controls its FP rate on a fresh, independent null

Freshly generated **120,000** wrong-key panel-max decodes (seed base 3301, order-preserving,
distinct from I3's 770000 base — an independent draw), then G-CAL the **adopted** `exact` bar
against them (`out_panelmax_gcal.json`):

| block | bar | empirical/nominal ratio | gating? | verdict |
|---:|---:|---:|:--:|---|
| 10 | 4.335 | **1.042** | yes | within 20% — PASS |
| 100 | 4.995 | 0.500 | no | conservative |
| 1000 | 5.655 | 0.833 | no | conservative |

The fresh fit (μ=2.575, β=0.253, ξ=**−0.021**) is slightly **stricter** than the adopted M=10⁶
cell (μ=2.358, β=0.287); the negative GEV shape ξ<0 re-confirms I3 §4's bounded-tail finding, so
the Gumbel bar is conservative (the higher blocks' ratios <1 are exactly that signature). **The one
gating block passes at ratio 1.042; the adopted panel-max bar does not manufacture false
positives.** This is an independent cross-check of I3's bar on data this lane generated itself.

**P3a PASS:** canonical bar published + plant recovery ≥0.90 on all four gate registers (wrong-key
0.00) + G-CAL passes.

---

## P3b — the seed prior (replaces Round 8's flat prior)

Round 8 enumerated every unix second 2011–2015 **uniformly** for 10 generators — the exact
flat-prior error doctrine R4 names. L8 (`round18/L8-provenance`) built the correction: **433** unix
seconds a human demonstrably had in front of them, ranked by provenance × authorship-proximity ×
derivation-distance. This lane lifts them into a machine-readable ordering for Phase-S.

**Deliverables.**
- `seedprior20.json` — the 433 candidates as `{rank, seed, tier, tier_weight, n_sources,
  priority}`, stripped of L8's bulky provenance evidence, plus how each generator (S-G3/S-BASH/
  S-PERL/S-TEX) consumes a seed.
- `p3b_seedprior.py` — callable `seed_order(top=None)` (the seeds to try FIRST, in order) and
  `weighted_order(top=None)` (`(seed, priority, tier)` for compute allocation).

**Ranking (top of the list):**

| rank | seed | tier | meaning |
|---:|---:|:--:|---|
| 1 | **1325734783** | A | 2012-01-05T03:39:43Z — the second the 3301 PGP **primary key + encryption subkey + UID self-sig** were all created (3 independent verified sources, author's own machine) |
| 2 | 1325735163 | A | first "we will cryptographically sign all messages" sig |
| 3 | 1325881710 | A | "In twenty-nine volumes, knowledge was once contained." sig |
| 4 | 1325922790 | A | "A poem of fading death, named for a king" sig |
| 5 | 1325930871 | A | "The key has always been right in front of your eyes." sig |

Tier counts: **A=54, B=107, C=260, D=12** (433 total). **Positive control (round-trip):** the
emitted ordering reproduces the source's rank order and tiers with **0 mismatches**, rank 1 =
1325734783, and the tiers are monotone non-worsening down the list (A block → B → C → D). The
ordering is generator-independent (the candidates are unix seconds; only the per-seed decode call
differs), so any Phase-S seed sweep prioritises the same 433 first. **A seed absent from the list
is not excluded** (L8's caveat carried forward).

**P3b PASS.**

---

## P3c — drift re-baseline (confirms the fragile-decode-channel bound)

Both of these were measured on the **old keyskip1 beam**; the campaign plan and T3 §7 conditional 2
explicitly ask for them under the repaired `drift_rec` preset (`max_skip=40, max_free=2, lam=12,
start_slack=2`), which "may be either more robust (it can absorb a spurious advance) or less (it
can absorb a *wrong* one). This lane does not know which, and says so." — now it does.

### P3c-i — I3's drift-on-OE `pmax` shortfall, re-measured (`out_oe_shortfall.json`)

I3 §7.2 (G-RECOVER FAILED on OE): drift-preset OE median `pmax` = 13.40 vs the drift `pmax` bar
13.842, shortfall 0.44. Re-measured here (nrep=12, fresh replicates, repaired `drift`):

| preset | register | median `pmax` | bar @ N=10⁶ | shortfall | power at bar | median recovery |
|---|---|---:|---:|---:|---:|---:|
| `drift` | **OE** | **13.543** | 13.842 | **0.299** | **0.33** | 1.00 |
| `exact` | OE | (well above) | 7.634 | — | 1.00 | 1.00 |

**The shortfall persists** (0.299 vs I3's 0.44; both < 0.5, same sign, same conclusion). Under the
drift channel, OE recovers 100% of runes yet its `pmax` clears its own panel-max bar only 33% of
the time. **Confirmed bound:** the drift channel cannot lift OE over its panel-max bar, so an OE
decode in Phase S must be **ranked** (via `n_skips` / recovery — T3 §5.1's transcription-robust
channel), never **thresholded** on `pmax` alone. Under the `exact` preset OE is fully powered (1.00)
— the recommendation stands to run `exact`/`pair` and `drift` as **separate cells**, each against
its own bar (I3 §7.2).

### P3c-ii — the section-5 decode-derail curve, `drift_rec` vs `keyskip1`

Design mirrors T3.t3_decode.cell exactly (EN_KJV register, L7-A power 1.00; `encipher_keyskip`
supp=0.83; corrupt k runes; decode with the **correct** key), swapping only the decoder. L=400,
REPS=40, k_book matched to T3's x-axis over 12,956 (`out_derail_L400.json`). "graceful" = the
recovery a decoder gets if each wrong ciphertext rune costs exactly one wrong plaintext rune
(1−k/L); the gap below it is the beam **losing key synchronisation** (a derail).

| k_book | k_cell | graceful ideal | `keyskip1` recovery / **derail** | `drift_rec` recovery / **derail** |
|---:|---:|---:|---:|---:|
| 0 | 0 | 1.000 | 1.000 / 0.00 | 1.000 / 0.00 |
| 50 | 2 | 0.995 | 0.995 / 0.03 | 0.995 / 0.00 |
| 100 | 3 | 0.993 | 0.993 / 0.05 | 0.993 / 0.00 |
| 200 | 6 | 0.985 | 0.985 / 0.10 | 0.985 / 0.00 |
| 450 | 14 | 0.965 | 0.956 / 0.17 | **0.965 / 0.00** |
| 900 | 28 | 0.930 | 0.873 / 0.25 | **0.924 / 0.00** |
| **K-REC** (median recovery < 0.90) | | | **k_book = 900** | **never (None) in range** |

**The repaired beam is strictly MORE robust, and this answers T3 §7's open question.** T3 could
not say whether the larger skip budget would help (absorb a spurious advance) or hurt (absorb a
*wrong* one). Measured: **`drift_rec` derails 0.00 at every k** and tracks the graceful ideal
*exactly* (0.965 = 0.965 at k=450), whereas `keyskip1` bleeds 0.009 to derail at k=450 and 0.057 at
k=900. The mechanism T3 §5 identified — "`max_skip` only lets the key run *ahead*; once the beam
takes a spurious skip at a corrupted rune it can never come back" — is exactly what the permissive
relation's `max_free`/`lam` structure repairs: it can decline the spurious advance and stay
synchronised. Both beams' k=0 controls are green (recovery 1.000, correct/wrong separated), so the
instrument is wired correctly before its curve is trusted (PREREG P3c control).

**The fragile-decode-channel bound, restated with the repaired beam.** The decode channel is
fragile *only under the rigid `keyskip1` beam*; under `drift_rec` it is robust across the entire
located-set error range (k ≤ 450) and beyond. This does **not** loosen the standing bound for
Phase S, because Phase S can and should carry both cells: `keyskip1` for its clean CALIBRATED
panel-max bar (M=10⁶) and `drift_rec` for its transcription-robustness, each adjudicated against
its own bar (P3a). And `n_skips` remains exact (p95 error ≤ 1 at every k under `drift_rec`),
confirming T3 §5.1's transcription-robust ranking channel is the backbone regardless of beam.
This is a **decode-channel robustness gain, not an LP2 result** — no LP2 decode is scored here.

---

## Coverage × power (doctrine R2)

- **P3a.** Coverage: 1 canonical bar per 4 presets; the `exact` bar CALIBRATED at M=10⁶, the other
  three carried at I3's M (6×10⁴ / 6×10⁴ / 1.5×10⁴, PROVISIONAL). G-CAL re-verified on a fresh
  1.2×10⁵ null. **Power: measured** — correct-key `pmax` power 1.00 on LP1_REAL/LATIN/OE/half-vowel
  (nrep=10), wrong-key 0.00, negative control 0.00.
- **P3b.** Coverage: 433/433 candidates emitted (full enumeration of the L8 set). Power: n/a (an
  ordering, not a detector); round-trip control 0 mismatches.
- **P3c.** Coverage: OE shortfall (nrep=12) + derail curve (L=400, 6 k-values × REPS reps × 2 beams).
  Power: the k=0 control proves recovery 1.00 + correct/wrong separation under both beams before
  the derailed cells are trusted.

**The three conditionals of every number here:** (1) null generator — uniform ciphertext ×
uniform keystream, seed 3301, validated vs the LP2 histogram-shuffle in I3 §1.2; (2) decoder
relation — reported per I1 preset; a bar under one preset is INVALID under another; (3) adjudicator
register — the I2 9-register panel behind `pmax`, EN_NOVOWEL = detection-only.

## Files

- `PREREG.md` — the five Aiming-Test answers, controls, thresholds, kill condition (pre-run).
- `panelmax20.json` / `panelmax20.py` — **the one bar** every Phase-S lane calls (P3a deliverable).
- `seedprior20.json` / `p3b_seedprior.py` — the 433-candidate prior ordering (P3b deliverable).
- `p3a_panelmax.py` — build + plant-recovery control + fresh-null G-CAL.
- `p3c_drift_rebaseline.py` — derail curve + OE shortfall under `drift_rec`.
- `out_plant_recovery.json`, `out_panelmax_gcal.json`, `out_oe_shortfall.json`, `out_derail_L400.json`.
- `test_p3.py` — 4 self-tests (bar callable + refuses unknown preset; seed round-trip; plant gate).
