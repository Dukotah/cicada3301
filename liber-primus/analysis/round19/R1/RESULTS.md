# R1 — RED-TEAM ROUND 19 — RESULTS

_Doctrine rule **R6**. Target: **this round's own reasoning**, not the cipher.
Pre-registered in [`PREREG.md`](PREREG.md) (+ ADDENDUM 1) before any measurement.
Verdicts are **FOUND-ERROR** / **NO-ERROR-FOUND**. Nothing here is "confirmed" or "validated"._

| sub-attack | trigger | verdict |
|---|---|---|
| **A — I1's permissiveness** | **overall** | **NO-ERROR-FOUND** — I1's premise is achievable, and §A.4/A.4b give the frontier and the design that hits it |
| | A-i separation collapse | **NO-ERROR-FOUND** |
| | A-ii baseline power loss | **FOUND-ERROR** (literal) / NO-ERROR-FOUND (substantive — see §A.5) |
| | A-iv score/recovery decoupling _(not pre-registered — reported as an observation)_ | **the round's biggest single hazard** |
| **B — I2's panel** | B-i effective number of tests | **FOUND-ERROR** |
| | B-ii naive panel FPR | **FOUND-ERROR** |
| | B-iii the selection correction's power | **FOUND-ERROR** |
| | B-iv I1 × I2 destructive interaction | **FOUND-ERROR** |
| **C — the L1 prior** | C-i encoder identification is not unique | **FOUND-ERROR** |
| | C-ii the GnuPG string's pinning power | **FOUND-ERROR** (independence half: NO-ERROR-FOUND) |
| | C-iii the shift arithmetic | **FOUND-ERROR** |
| | C-iv inferential distance to pad generation | **NO-ERROR-FOUND** (1 of 11 rows survives) |
| **D — the round's own logic** | D-i enumeration cost | **FOUND-ERROR** (qualified by §D.2) |
| | D-ii the prefilter dilemma | **FOUND-ERROR** — *this is the finding* |
| | D-iii what S2 can reach | **FOUND-ERROR** |
| | D-iv Phase 3 is specified against a repo state that is not true | **FOUND-ERROR** |

**Answer to "is Round 19 correctly aimed?" — §E. Short version: Phase 0 yes and it is worth
more than the plan says; Phase 1/2 no; Phase 3 is aimed at work that is already done. The
recommendation is REDIRECT, not STOP.**

---

## 0. Trust anchor and instrument independence

```
python3 liber-primus/tests/validate.py       ->  ALL VALIDATIONS PASSED (5/5)   [before]
                                             ->  ALL VALIDATIONS PASSED (5/5)   [after]
python3 -m pytest liber-primus/benchmark/ -q ->  8 passed                       [after]
```

Everything measured here comes from `r1_lib.py`, written for this lane: its own quadgram
loader, its own transliteration, its own beam with an explicit parameterised transition
relation, its own encipherment constructions, its own rune-space LMs, its own tail-calibrated
Gumbel fit. `skipdecode.beam_decode`, `benchmark/null.py` and the I-lane harnesses were read but
not used as measuring devices. The Gematria table, the pinned 12,956-rune stream, the quadgram
count file and the corpus texts are **data** and are shared.

**State of Round 19 when this lane ran:** `round19/` held `CAMPAIGN-PLAN.md` and an empty `G1/`.
**I1, I2 and I3 had not landed and did not land during this lane's run.** What is attacked below
is therefore their **specification** in `CAMPAIGN-PLAN.md`, plus the L1 prior and the plan's own
arithmetic. Where a claim could only be tested against code that does not exist, it is marked
**UNTESTED** in §F.

---

## A. I1's PERMISSIVENESS — the frontier

### A.1 The claim

> **I1** — DRIFT-TOLERANT DECODER. *"Generalise the beam's transition relation to cover
> `skip_by_two`, free drift, and unrepresentable key advances — **without losing power on the
> baseline construction or admitting wrong keys**."*

The parenthetical is the whole content and the plan offers no evidence it is achievable. A
drift-tolerant beam searches a strictly larger hypothesis space per decode, and its internal
objective is the English quadgram model. The obvious failure mode is that it starts finding
English in noise.

### A.2 Positive controls (PREREG §A.2) — PASS

| control | requirement | measured | |
|---|---|---|---|
| **PC-A1** baseline | `exact/ms3`, correct key, `keyskip` plant: score ∈ [−4.6, −3.9], recovery ≥ 0.95 | L=120 **−4.268 / 1.000**; L=240 **−4.380 / 1.000** | **PASS** |
| **PC-A2** reproduce L7-B's hole | `exact/ms3`, correct key, `skip_by_two` plant: score ≤ −6.4, recovery ≤ 0.40 | L=240 **−6.718 / 0.275**; L=120 −6.115 / 0.483 | **PASS at L=240** (L7-B's own length; **see note**) |
| **PC-A3** wrong-key floor | 200 uniform-random keystreams vs real LP2, `exact/ms3`: null mean ∈ [−7.6, −7.1] | mean **−7.323**, max **−6.872** | **PASS** |

_Note on PC-A2._ The threshold in PREREG §A.2 did not name a length. At L = 240 — the length
L7-B measured at — my independent decoder reproduces L7-B's `skip_by_two` hole to **0.18 of
score** (−6.718 vs L7's −6.90) and **1.7 pp of recovery** (27.5 % vs 25.8 %). At L = 120 the
hole is real but shallower (−6.115 / 48.3 %), missing the score half of the bar by 0.29. The
hole **deepens with length**, which is expected (drift accumulates) and is recorded here rather
than smoothed over. All frontier numbers below are at L = 240.

The reproduction is the licence for everything that follows: an instrument written from scratch,
by a different author, from the same primitives, finds the same hole in the same place.

### A.3 The frontier

`out_a.json` (16 configurations) + `out_a2.json` (6 more). 7 replicates per correct-key cell,
200 uniform-random wrong keystreams per null, all at L = 240, beam width 400, against the **real
LP2 ciphertext** for the nulls. `bar 10⁶` is a family-wise α = 0.01 bar from a tail-calibrated
two-point Gumbel fit on the lane's own 200 order statistics; `null max` is the raw observed
maximum of those 200 and carries no distributional assumption at all.

| transition model | branch­ing | `keyskip` score / rec | `skip_by_two` score / rec | free-drift q=.05 score / rec | null mean | **null max (n=200)** | **bar 10⁶** |
|---|---:|---|---|---|---:|---:|---:|
| `exact/ms1` | 1.034 | −4.509 / 1.00 | −6.718 / 0.26 | −6.784 / 0.33 | −7.332 | −6.842 | −5.845 |
| **`exact/ms3`** _(the repo's decoder)_ | **1.036** | **−4.380 / 1.00** | **−6.718 / 0.28** | **−6.784 / 0.33** | **−7.323** | **−6.872** | **−5.966** |
| `exact/ms8` | 1.036 | −4.380 / 1.00 | −6.718 / 0.28 | −6.784 / 0.33 | −7.323 | −6.872 | −5.966 |
| `by2/ms3` _(skip-by-two only)_ | 1.036 | −6.452 / 0.43 | −4.380 / 1.00 | −6.633 / 0.25 | −7.311 | −6.946 | −6.438 |
| **`union2/ms3`** _(both, constrained)_ | **1.071** | **−4.380 / 1.00** | **−4.380 / 1.00** | −5.736 / 0.68 | **−7.146** | **−6.697** | **−5.880** |
| `free/ms1` | 2.000 | −4.475 / 0.97 | −4.567 / 0.78 | −4.432 / 0.96 | −5.645 | −5.151 | −4.168 |
| `free/ms2` | 3.000 | −4.849 / **0.16** | −4.707 / **0.15** | −4.804 / **0.12** | −4.933 | −4.617 | −4.070 |
| `free/ms3` | 4.000 | −4.521 / **0.13** | −4.503 / **0.11** | −4.497 / **0.10** | −4.573 | −4.330 | −3.927 |
| `free/ms4` | 5.000 | −4.274 / **0.06** | −4.299 / **0.10** | −4.335 / **0.08** | −4.355 | −4.127 | −3.732 |
| `freepen λ=0.5/ms3` | 4.000 | −4.971 / 0.19 | −5.025 / 0.15 | −4.899 / 0.16 | −5.237 | −4.853 | −4.163 |
| `freepen λ=2/ms3` | 4.000 | −4.424 / 0.98 | −4.451 / 0.98 | −4.496 / 0.96 | −6.233 | −5.584 | −4.204 |
| `freepen λ=4/ms3` | 4.000 | −4.497 / 0.98 | −4.555 / 0.98 | −4.646 / 0.96 | −6.797 | −6.337 | −5.525 |
| **`freepen λ=6/ms3`** | 4.000 | **−4.570 / 0.99** | **−4.620 / 0.99** | **−4.815 / 0.96** | **−7.067** | **−6.636** | **−5.906** |
| `freepen λ=10/ms3` | 4.000 | −4.693 / 0.99 | −4.858 / 0.97 | −5.156 / 0.96 | −7.331 | −6.910 | −6.202 |

_(`union` — the first version of the union model — carried an instrument defect of mine and is
excluded from every verdict; see ADDENDUM 1 and `out_a.json:instrument_defect`.)_

### A.4 **THE PERMISSIVENESS FRONTIER, in one sentence**

> **The wrong-key null is safe for exactly as long as every admissible key-advance carries a
> constraint the decoder can check against the ciphertext. The first *unconstrained* alternative
> per position — branching 1.04 → 2.00 — moves the wrong-key null mean by +1.68 and the
> family-wise bar at 10⁶ decodes by +1.80, which is more than the entire margin the instrument
> has (`exact/ms3`'s correct-key margin over its own 10⁶ bar is **1.59**). Separation is gone at
> the *first* free step, not gradually.**

Assumption-free version of the same statement, using only the observed max of 200 wrong keys:

| decoder | correct key (`keyskip`) | best of 200 **wrong** keys | gap |
|---|---:|---:|---:|
| `exact/ms3` | −4.380 | −6.872 | **2.49** |
| `union2/ms3` | −4.380 | −6.697 | **2.32** |
| `freepen λ=6/ms3` | −4.570 | −6.636 | **2.07** |
| `free/ms1` | −4.475 | −5.151 | **0.68** |
| `free/ms3` | −4.521 | −4.330 | **−0.19 — a wrong key beats the correct one** |

And the cost of covering `skip_by_two`, per route:

| route | covers `keyskip` | covers `skip_by_two` | covers free drift | bar 10⁶ vs `exact/ms3` | baseline score cost |
|---|---|---|---|---:|---:|
| `union2` (constrained union) | yes, 1.00 | **yes, 1.00** | partly (0.68) | **+0.086** | **0.000** |
| `freepen λ=6` (cost-regularised) | yes, 0.99 | **yes, 0.99** | **yes, 0.96** | **+0.060** | −0.190 |
| `free` (naive drift tolerance) | **no** (rec 0.06–0.16 above ms1) | no | no | **+1.80 … +2.04** | catastrophic |

### A.4b The frontier as one curve — realised permissiveness

`mean_branching` counts admissible transitions but ignores what a penalty costs. The scalar that
actually predicts the null is the **realised drift rate on the winning path when the key is
wrong** — how often, per rune, the decoder actually exercises its freedom to steer noise toward
English. 60 uniform-random keystreams against the real LP2 ciphertext, L = 240 (`out_a3.json`):

| decoder | nominal branching | **wrong-key drift / rune** | correct-key drift / rune | null mean | null max |
|---|---:|---:|---:|---:|---:|
| `exact/ms3` | 1.036 | **0.021** | 0.021 | −7.296 | −6.962 |
| `union2/ms3` | 1.071 | **0.067** | 0.021 | −7.120 | −6.834 |
| `freepen λ=10/ms3` | 4.000 | **0.071** | 0.021 | −7.335 | −7.081 |
| `freepen λ=6/ms3` | 4.000 | **0.169** | 0.021 | −7.071 | −6.643 |
| `freepen λ=4/ms3` | 4.000 | **0.285** | 0.021 | −6.807 | −6.324 |
| `freepen λ=2/ms3` | 4.000 | **0.544** | 0.029 | −6.265 | −5.851 |
| `free/ms1` | 2.000 | **0.500** | 0.096 | −5.600 | −5.215 |
| `freepen λ=1/ms3` | 4.000 | **0.865** | 0.267 | −5.703 | −5.341 |
| `free/ms2` | 3.000 | **0.971** | **0.917** | −4.927 | −4.602 |
| `free/ms3` | 4.000 | **1.504** | **1.546** | −4.593 | −4.371 |

The null level is a clean monotone function of one number. Read the curve:

- **≤ 0.07 drift/rune on a wrong key → null mean ≈ −7.1 to −7.3.** This is the safe region, and
  both `union2` (by constraint) and `freepen λ ≥ 6` (by cost) sit in it.
- **≈ 0.5 → −5.6.** Half the positions steered; 1.7 of null level gone.
- **≥ 0.97 → −4.6 to −4.9,** and note the **correct-key** column at that point: 0.92 and 1.55
  drift events per rune. Past ~0.9 the decoder has stopped tracking the key at all; correct and
  wrong keys drift at the same rate because the key is no longer doing any work. That is the
  mechanism behind §A.6's hallucination.
- The `freepen` rows show what a penalty buys: at λ = 4 the **correct**-key drift is already back
  to the true rate (0.021, identical to `exact`) while the wrong key still drifts at 0.285. λ is
  simply a prior on how often unrepresentable advances happen, and stating it explicitly is what
  separates a usable drift-tolerant decoder from an unusable one.

**So the frontier is not "how many transitions are admissible" — it is "how often a wrong key
gets to use one". Keep that below ~0.07 per rune and the instrument is intact; let it past ~0.5
and the instrument is gone.**

### A.5 Verdicts A-i and A-ii

**A-i — NO-ERROR-FOUND.** The pre-registered trigger was "no configuration simultaneously sees
`skip_by_two` (score ≥ −5.5, recovery ≥ 0.80) and clears its own 10⁶ bar by ≥ 0.30". Such
configurations exist and there are several: `union2/ms{2,3,4}` (margin **+1.50**),
`freepen λ=4` (+0.97), `λ=6` (+1.29), `λ=10` (+1.34), `by2/ms{1,3}` (+1.84/+2.06).
**I1's central premise is achievable.** This lane went looking for a collapse and did not find
one at the point the plan needs it. That is a real result and it is reported as one.

**A-ii — FOUND-ERROR by the letter; NO-ERROR-FOUND on the substantive reading.** The trigger
reads "at the *least permissive* configuration that satisfies A-i(a)". That is `by2/ms1`
(branching 1.034), whose baseline score drops **2.072** — trigger fires. But `by2` is a
*specialised* relation that cannot represent the baseline construction at all, so it was never a
candidate decoder; my trigger was mis-specified in not requiring the configuration to cover both
constructions. Under the reading I believe is honest — the least permissive configuration
covering **both** — the answer is `union2/ms3`, whose baseline score cost is **0.000** and whose
10⁶ bar rises by **0.086**. Both are inside the 0.40 tolerance. **I report the literal firing and
the substantive non-firing, and I do not get to choose which one to headline: it is A-i that
carries the weight, and A-i is NO-ERROR-FOUND.**

### A.6 A-iv — the hazard the plan does not mention (NOT pre-registered)

Look at the `free/ms2…ms4` rows again. **The score stays in the English band (−4.3 to −4.9)
while rune recovery falls to 0.06–0.16.** The decoder is emitting fluent English that is *not the
plaintext*. It is not failing loudly; it is hallucinating quietly, from the **correct key**.

The consequence for Round 19 is immediate and concrete:

> **Any validation of I1 that gates on score alone will certify a hallucinating decoder.**
> `free/ms4` with the correct key scores **−4.274** — better than `exact/ms3`'s −4.380 — at
> **6 % recovery**. A PREREG that says "the correct key must score ≥ −5.5" passes it. A PREREG
> that says "the correct key must be *recovered*" fails it.

`round18/L2-filter-leak`'s gate B.3 already got this right (`score >= -5.5 **and** recovery >=
0.90` at L = 12,956, measured −4.098 / 0.9997). Round 19's `CAMPAIGN-PLAN.md` restates rule 3
("plant, prove recovery, then trust silence") but its I1 row states the success criterion as
"without losing power … or admitting wrong keys", which is a score criterion. **I1's PREREG must
gate on recovery, on a `skip_by_two` plant, at L ≥ 240, or the gate is worthless.**

### A.7 What A did not cover

- The wrong-key null is **uniform-random keystreams**. It does not cover *structured* wrong keys
  — off-by-one offsets of the correct key, near-miss seeds, keys sharing a prefix — which are
  the wrong keys a real seed sweep mostly generates, and which are plausibly *more* dangerous
  under a permissive relation than uniform ones.
- One key family (`sha256_ctr`) and one plaintext register (held-out English) in the frontier.
- λ was scanned on a log-ish grid {0.25, 0.5, 1, 2, 3, 4, 6, 10}; the optimum was not located,
  only bracketed to 4 ≤ λ ≤ 10.
- Combinations of constructions (e.g. `skip_by_two` *plus* free drift) were not tested.
- Beam width fixed at 400 throughout.

---

## B. I2's PANEL — a register-shopping machine

Nine rune-space trigram LMs built by me, trained on the first 80 % of each register's stream and
tested on the last 20 %. **PC-B1 PASSES 9/9**: every register scores its own text 1.09–3.07 nats
above uniform runes. The panel can see what it claims to see.

### B.1 B-i — the registers are not 9 tests. **FOUND-ERROR**

Correlation of the 9 register scores over 2,000 uniform-random rune strings:

```
              EN   KJV   LP1    LA    OE    DE    CY  HALF NOVOW
EN         +1.00 +0.80 +0.77 +0.37 +0.63 +0.54 +0.38 +0.84 +0.30
EN_KJV     +0.80 +1.00 +0.77 +0.33 +0.76 +0.61 +0.40 +0.75 +0.25
LP1        +0.77 +0.77 +1.00 +0.38 +0.70 +0.61 +0.44 +0.77 +0.25
LA         +0.37 +0.33 +0.38 +1.00 +0.33 +0.50 +0.50 +0.34 +0.16
OE         +0.63 +0.76 +0.70 +0.33 +1.00 +0.58 +0.34 +0.68 +0.29
DE         +0.54 +0.61 +0.61 +0.50 +0.58 +1.00 +0.40 +0.60 +0.37
CY         +0.38 +0.40 +0.44 +0.50 +0.34 +0.40 +1.00 +0.37 +0.06
EN_HALF    +0.84 +0.75 +0.77 +0.34 +0.68 +0.60 +0.37 +1.00 +0.50
EN_NOVOW   +0.30 +0.25 +0.25 +0.16 +0.29 +0.37 +0.06 +0.50 +1.00
```

**M_eff = 5.00 (Li–Ji), 7.01 (Nyholt)** against a naive 9. The trigger was `M_eff` < 6 or > 13.5;
Li–Ji fires. There is a tight English cluster (EN / EN_KJV / LP1 / EN_HALF / OE, r = 0.63–0.84 —
`EN_HALF` correlates with `EN` at **0.84**, so half-vowel English is barely an extra test at all)
and three near-independent outliers (LA, CY, EN_NOVOW; CY–EN_NOVOW r = **0.06**).

**Why this matters for I3.** The plan says I3 exists because "a 9-way max-over-panel statistic
inflates the null". It does — but not by a factor of 9, and the inflation is **not uniform across
registers**: adding Welsh buys nearly a whole extra test, adding half-vowel English buys about a
sixth of one. A single scalar "panel correction" is the wrong shape of fix. The right fix is a
**direct null on the max statistic itself** — draw the panel maximum under noise and calibrate
*that* — which costs the same as calibrating one register and is exact regardless of correlation.

### B.2 B-ii — the naive panel FPR. **FOUND-ERROR**

Per-register α = 0.01 bars measured on 3,000 calibration noise strings, then applied to 3,000
fresh ones:

| statistic | measured FPR |
|---|---:|
| English only (the current instrument) | **0.0093** |
| **max over the 9-register panel** | **0.0543** |
| naive-independent expectation, 1 − 0.99⁹ | 0.0865 |

A **5.8×** inflation, which is what the M_eff = 5.0 correlation structure predicts. The plan
allocates this to I3 as "recalibration" without saying what is recalibrated; a per-register bar
that looks correct in isolation is a 5.4 % false-positive rate the moment the maximum is taken,
and at 10⁶ decodes that is 54,000 spurious promotions before any prior is applied.

### B.3 B-iii — L7-A.4's selection correction is powered for some registers and not others. **FOUND-ERROR**

L7-A.4 corrected the archive re-scoring for selection with the contrast `score_M − score_EN`,
standardised against the archive's own spread, and reported **0 of 340** candidates at z ≥ 3 for
every register — the basis of its "no archived candidate is more Latin-, Old-English-, German- or
Welsh-like than its own English-likeness already explains", and one of the two things that
narrows Round 19's hypothesis space.

I rebuilt the same statistic (reference set = top-120 by **English** score out of 1,200 noise
decodes — the same selection the archive underwent) and asked what z a **genuine** plaintext of
each register, recovered with the **correct key**, actually gets:

| register | true-positive median z | max z | reaches L7's z ≥ 3? |
|---|---:|---:|---|
| LA | **6.89** | 8.08 | yes |
| DE | **9.14** | 10.68 | yes |
| EN_NOVOW | **5.57** | 6.77 | yes |
| OE | **5.09** | 9.35 | yes |
| CY | **4.15** | 6.68 | yes |
| **EN_HALF** | **2.55** | 3.52 | **no** |
| **LP1 (the register the puzzle actually uses)** | **−8.61** | −6.50 | **no — maximally anti-flagged** |

Two things fall out, and only the second is a criticism:

1. **The correction is genuinely powered for Latin, German, Old English, Welsh and vowel-dropped
   English** (median z 4.2–9.1 against a z ≥ 3 bar). L7-A.4's null over those five registers
   means what it says, and this lane strengthens rather than weakens it. Reported as such.
2. **It has no power for half-vowel English** (median 2.55, max 3.52 — straddling the bar), and
   it is **structurally anti-powered for any register the English model already sees**: LP1's own
   plaintext gets **z = −8.61**, because the statistic is a *difference against English*. That is
   defensible as a design (English is adjudicated separately) but it means the corrected panel's
   coverage is exactly "the five clearly-non-English registers", not "the register axis". L7-A.4
   is written as the latter. Also worth noting: L7's archive maxima were **2.58–2.96**, i.e.
   within 0.04 of a z ≥ 3 bar that a real half-vowel-English positive would only reach 50 % of
   the time — a coin-flip separation that the write-up presents as a clean zero.

### B.4 B-iv — I1 and I2 interact destructively (ADDENDUM 1). **FOUND-ERROR**

Genuine non-English plaintexts planted under `skip_by_two`, decoded with the **correct key**,
scored under their own register's LM (nats/symbol) and by rune recovery:

| register | `exact/ms3` LM / rec | `free/ms3` LM / rec | `union2/ms3` LM / rec | Δ LM (free−exact) | Δ rec (free−exact) |
|---|---|---|---|---:|---:|
| LA | −3.511 / 0.35 | −3.613 / **0.09** | **−1.992 / 1.00** | **−0.102** | **−0.258** |
| CY | −3.102 / 0.51 | −3.322 / **0.07** | **−2.363 / 1.00** | **−0.220** | **−0.442** |
| OE | −3.269 / 0.46 | −3.082 / **0.12** | **−2.352 / 1.00** | +0.187 | **−0.333** |
| EN_HALF | −3.250 / 0.61 | −3.032 / **0.09** | **−2.733 / 1.00** | +0.217 | **−0.517** |
| LP1 | −3.468 / 0.42 | −3.049 / **0.09** | **−2.872 / 1.00** | +0.420 | **−0.325** |
| EN | −2.873 / 0.69 | −2.747 / **0.13** | **−2.197 / 1.00** | +0.126 | **−0.558** |

The trigger (Δ LM ≤ −0.10 **or** Δ rec ≤ −0.10 for any non-English register) fires on **all four**
non-English registers, on the recovery arm for every one of them, and on the LM arm for Latin and
Welsh.

**The mechanism, stated plainly.** I2 can only adjudicate what I1 emits. I1's beam maximises an
**English** objective at every free choice. Give it free choices and it spends them making the
output more English — so for a Latin or Welsh plaintext, *more permissiveness means more
corruption of the very signal I2 was built to detect*. The Δ LM column is small and mixed
precisely because the register LMs partly reward English-ish structure too (§B.1); the **Δ rec
column is the real damage**, and it is −0.26 to −0.56 across the board.

**And the constructive half.** `union2/ms3` — constrained, branching 1.071 — recovers **1.00** of
the true runes in **every** register and lifts the own-register LM by 0.4–1.5 nats over `exact`.
A correctly-specified I1 does not just avoid harming I2; it **materially improves** it. The
difference between the two designs is not a tuning parameter, it is the difference between a
transition relation that checks its skips against the ciphertext and one that does not.

### B.4b A smaller thing, but it is in the load-bearing sentence

`CAMPAIGN-PLAN.md` lane **I2** specifies the panel as *"EN / LP1-orthography / Latin / OE / DE /
CY / half-vowel / no-vowel"* — **eight** registers. Lane **I3** exists because *"a **9-way**
max-over-panel statistic inflates the null"*. The plan is internally inconsistent about the size
of the thing I3 is being asked to correct for, in the two lines that define both lanes. Given
§B.1 (the answer is neither 8 nor 9 but ≈ 5 effective tests) this is cosmetic in effect, but it
is the kind of drift that turns into a mis-stated bar three lanes downstream, which is exactly
what L7-C.3 found happened to `threshold_for()` in Round 17.

### B.5 What B did not cover

- Order-3 rune LMs with add-0.5 smoothing; `round16/scorer`'s matched runic **quadgram** scorer
  exists, passes its gates, and — as L7 already recorded — no lane has adopted it. Not adopted
  here either.
- The four doctrine-R3 language-agnostic statistics are implemented in `r1_lib.py` but were not
  made part of a panel test; whether adding them raises or lowers M_eff is **UNTESTED**.
- Registers outside the 9; non-linguistic payloads (B6 proved these undetectable in principle).
- The adversarial-promotion arm of PREREG §B.3.3 was folded into B-ii rather than run separately.

---

## C. THE L1 PRIOR — load-bearing, or post-hoc?

Round 19 Phase 1 exists because of `round18/L1-toolchain/RESULTS.md` §6, and the doctrine names
that section as the model answer to Aiming-Test Q2. So it has to hold.

### C.1 C-i — the encoder identification is not unique. **FOUND-ERROR**

L1's discriminator is four fields together: **IJG quality 92 DQT + optimised Huffman + Artifex
sRGB ICC + 4:2:0**, and §3.2 concludes *"no single-stage pipeline produces the LP2 vector"*,
identifying stage 2 as ImageMagick. §3.3 explicitly **excludes Python/PIL** (*"`stage2_pil_*`
keeps 3 components on gray content, so it cannot produce the 23-page grayscale class"*).

I re-read the LP2 vector with my own JPEG parser (no PIL, no ImageMagick) and re-ran the chain
with alternatives L1's control table does not contain:

| pipeline | ncomp | sampling | Huffman | ICC | DQT sha1 (luma, chroma) |
|---|---|---|---|---|---|
| **LP2 `0.jpg` (observed)** | 3 | `22x11x11` | **custom-optimised** | 2576 B Artifex sRGB | `c96e442f9ce9`, `cd6e3767d9c4` |
| `gs -dJPEGQ=92 -r400` (stage 1) | 3 | `22x11x11` | IJG-standard | 2576 B Artifex sRGB | `c96e442f9ce9`, `cd6e3767d9c4` |
| **ALT-2: gs → PIL `quality="keep", optimize=True`** | **3** | **`22x11x11`** | **custom-optimised** | **2576 B Artifex sRGB** | **`c96e442f9ce9`, `cd6e3767d9c4`** |
| **ALT-3: gs → PIL `.convert("L")`, q92, optimise** | **1** | **`11`** | **custom-optimised** | **2576 B Artifex sRGB** | **`c96e442f9ce9`** |
| REF: gs → ImageMagick default | 1 | `11` | custom-optimised | 2576 B Artifex sRGB | `c96e442f9ce9` |

**ALT-2 reproduces LP2's colour class on all four discriminating fields, and ALT-3 reproduces the
grayscale class — including the sRGB-on-grayscale fact that L1 §3.2 argument 2 treats as
diagnostic.** `jpegtran` is not installed here so the lossless-optimise arm is **UNTESTED**, but
it is a strictly easier case: `jpegtran -optimize -copy all` changes Huffman tables and nothing
else, so it would preserve DQT, ICC and sampling by construction.

L1's exclusion of PIL is an exclusion of **one PIL invocation** (a plain re-encode), not of PIL.
This is the same shape of error D3 named: a member of a class promoted to a property of the
class.

**What survives, and it is most of it.** Two of L1's three secondary arguments are untouched:
(1) 4:2:0 at q92 still requires stage 2 to have **inherited** sampling factors from a JPEG input,
so the two-stage reading stands; (3) the *automatic* 23/35 grayscale split is still better
explained by a tool that auto-detects grayscale (ImageMagick does; PIL does not) than by an
author choosing per-page. So the honest restatement is: **"stage 2 was a CLI-driven re-encoder
that inherited its input's sampling and passed the ICC through, of which ImageMagick is the
best-fitting single candidate and Python/PIL is not excluded"** — not "it was ImageMagick".

Why this matters to Round 19 specifically: L1's **F1** reads the encoder as *"a shell/scripting
idiom"*, and F1+F8 are what promote **rank 4, bash `$RANDOM`, ×2**. If stage 2 was a Python
script, the same evidence promotes rank 2 (Python) and says nothing about the shell. The evidence
does not distinguish, so it should not be spent twice in opposite directions.

### C.2 C-ii — the GnuPG string. **FOUND-ERROR** on pinning; **NO-ERROR-FOUND** on independence

**Independence — L1 understates its own corpus.** Parsing every PGP signature block in
`corpus/A-primary-artifacts/ibotpeaches/messages/` and hashing the signature payloads:
**56 signature blocks, 55 distinct payloads, 53 of them carrying `GnuPG v1.4.11 (GNU/Linux)`,
spread 14 / 23 / 15 across 2012 / 2013 / 2014.** These are independent signing events, not
mirror copies. L1 says "46 of 46"; the real figure is **53**. The trigger (fewer than 30 distinct)
does not fire.

**Pinning — the string does not pin the OS or the era.** (External verification, sources in
`out_c.json`.)

| fact | consequence |
|---|---|
| 1.4.11 released **2010-10-18**; 1.4.12 **2012-01-30** | 1.4.11 was upstream-current for **469 days** — the longest gap in the 1.4.10→1.4.16 run. Any Linux provisioned in that window and not upgraded emits it. |
| Shipped in Ubuntu **11.04, 11.10, 12.04 LTS and 12.10**; Mint 11–14; Fedora **15 and 16 at GA**, 14 after update | **≥ 2 OS generations** → trigger fires. And **12.10 is outside L1's stated "11.04–12.04" bracket**, so the bracket is wrong at its upper edge even within Ubuntu. |
| `(GNU/Linux)` is `PRINTABLE_OS_NAME`, a **`configure`-time constant** | It carries **zero** distro information. Identical on Ubuntu, Fedora, Gentoo, Arch, LFS, or a hand-built tarball. |
| Ubuntu 12.04 LTS carried 1.4.11 to **2017** | The string **does not date the messages**. A box installed once in 2011–12 emits the identical header across 2012, 2013 and 2014 — which is exactly what "53/53 uniform" looks like. |
| `no-emit-version` — one line in `gpg.conf`, present in every 1.4.x | The header is suppressible; and the corpus contains **`Version: CicadaPG v.3301`** (2017), so **3301 demonstrably edited an armor Version header at least once**. It is not a passive fingerprint. |

The honest restatement: *"one stable, unchanged, **non-Debian-stable** Linux box or VM image,
provisioned roughly 2011–2012, using `gpg1` with a default `gpg.conf`."* Note the string's
strongest content is **negative** and L1 does not use it: Debian went 1.4.10 (squeeze) → 1.4.12
(wheezy), **skipping 1.4.11 entirely**, so the header **excludes stock Debian and excludes Tails
throughout 2012–2014**. That is a genuinely useful constraint sitting unclaimed.

**Two facts in the same corpus that L1's §6 does not use, and one of them is stronger than F7.**
The 2012 message `this-message-will-only-be-displayed.asc` carries an embedded block reading
`Version: 1.99 / Scheme: Crypt::RSA::ES::OAEP`, and 3301's own plaintext says *"encrypted with
RSA (the **Crypt::RSA Perl module** available in CPAN)"*. That is a **direct, self-declared
statement that the author used Perl for cryptographic work** — far stronger support for L1's
rank-3 Perl row than "Ubuntu 12.04's system Perl is 5.14.2", and it is not cited. Second, the
author did **not** set `no-emit-version` in three years, which is one line of trivial armor
hygiene — corroborating L1's **F8** ("ran the tool with defaults") from an independent channel.
**A red-team lane reports what strengthens as well as what weakens: the Perl row's real
justification is in the corpus and should replace the distro-version one.**

### C.3 C-iii — the shift arithmetic. **FOUND-ERROR**

| finding | rows | detail |
|---|---|---|
| **no derivation** | all 11 | No row states a base rate, a count, a likelihood ratio or a calibration. The multipliers are asserted. §6.2's own header concedes they are "priors for search-order and budget allocation, not probabilities" — but Round 19's plan then uses them as a *ranking of hypotheses*, which is a probability claim. |
| **same family, two shifts** | 1 & 4 | Row 4's own text calls `$RANDOM` "a 15-bit glibc `rand()` derivative". Row 1 **is** glibc `rand()`/`random()`. Same family, **×3 and ×2**, on non-overlapping citations (F6/F7 vs F8/F9). |
| **same family again** | 1 & 3 | Row 3's own parenthetical says Perl's `rand` is "**drand48** under the hood". `drand48` is listed inside row 1. Rows 1 and 3 are not disjoint hypotheses but are weighted as if they were (×3, ×2.5). |
| **same evidence, different demotion** | 9 & 10 | Windows CRT (×0.15) and .NET (×0.05) are demoted by the **same four facts**, a factor of 3 apart, with no stated discriminator. |
| **no normalisation** | all 11 | Multiplicative re-weightings over a partition need a normalisation to be read as a distribution. There is none, so the table is an **ordering**, not a prior. |

This does not make the ordering wrong. Linux-in-2012 really does favour glibc/Perl/Python/shell
over .NET, and that is worth acting on. What it does mean is that the *numbers* carry no
information beyond the ordering, and Round 19's plan quotes them (`×3`, `×2.5`, `×2`) as if they
did.

### C.4 C-iv — inferential distance. **NO-ERROR-FOUND**, narrowly

Trigger: FOUND-ERROR if **zero** of F1–F10 bear on **pad generation** rather than on the
**May-2014 publication toolchain**. It does not fire — **one** does. F4 (a 6.00 × 9.00-inch
typeset page) + F5 (runes typeset from a font, horizontally scaled, none of 11 stock faces) do
constitute an argument that the source was a LaTeX-class document, and *if the pad was generated
inside that document* the generator is a TeX LCG. That is rank 5, and it is the only row in the
table with a generation-side argument rather than an availability-side one.

**But the other ten rows are availability arguments**, and the gap deserves naming because the
doctrine's Q2 leans on this section:

> F1, F2, F3, F6, F7, F8, F9 establish **which tools were installed on the machine that rendered
> and signed things in 2012–2014**. They do not establish which tool generated a keystream, which
> may have happened on a different machine, at a different time, possibly before any of the
> observed artifacts existed. The prior is therefore over **"what a person with this toolbox
> would reach for"**, which is a behavioural prior, not a physical measurement — and the doctrine
> R4 line it is cited under says *"Evidence means a measurement on a held artifact."*

That is a real inferential step, and it is not labelled as one in L1 §6 or in Round 19's plan.
And per §C.2 the OPSEC reading cuts the other way too: a signer disciplined enough to keep one
unchanged signing environment for three years is *more* likely, not less, to have separated it
from a pad-generation machine.

### C.5 C verdict and what survives

**FOUND-ERROR (C-i, C-ii, C-iii).** The prior survives in weakened form, and the weakening is
specific rather than total:

- **survives:** GNU/Linux, CLI-driven, 2011–2014-era toolchain, defaults-only habits; a two-stage
  render→re-encode chain whose second stage inherited JPEG sampling factors; the demotion of
  Windows/.NET; a Ghostscript build in 9.04–9.14; the exclusion of stock Debian and Tails.
- **does not survive:** "Ubuntu 11.04–12.04" as a pin (12.10, Mint 11–14, Fedora 15/16 and any
  self-build are equally consistent); "ImageMagick" as *the* encoder; the specific multipliers;
  the reading that the shell (rather than Python) is indicated by F1/F8; and the implicit
  transfer from publication toolchain to pad generator.
- **consequence for the shape of Round 19:** since the prior does not discriminate G1 from G2
  from G3 from G4, "high-prior bounded lanes" is really **"enumerable lanes"** wearing a prior's
  clothes. Doctrine R5 ranks enumerable generator spaces **second**, which is a perfectly good
  place to be — but the round's budget table justifies its 40 % under the *Q2/high-prior* heading,
  and per doctrine that share should be labelled for what the evidence actually supports.

---

## D. THE ROUND'S OWN LOGIC

### D.1 D-i — enumeration through the repaired instrument. **FOUND-ERROR**

Measured on this machine (6 cores, WSL, Python 3.14), L = 120, beam 400:

| decoder | decodes/s/core |
|---|---:|
| `exact/ms3` | 57.6 |
| **`union2/ms3`** (the repaired relation) | **5.6** |
| `free/ms3` | 1.0 |

`union2` is **10× slower** than the decoder it replaces, because its branching factor moves the
beam from ~68 live states to the full 400. **The repair makes the sweep an order of magnitude
more expensive**, and the plan does not price it.

Against the spaces the plan calls enumerable (× the 8-fold sign/atbash/direction multiplier every
prior sweep in this repo applied):

| space | plan's / L1's words | decodes | wall-clock, 6 cores, `union2` |
|---|---|---:|---:|
| G1 bash `$RANDOM` (2³² seeds) | *"enumerable"* / *"enumerate completely in **minutes**"* | 3.44 × 10¹⁰ | **32.4 years** |
| G1 glibc `random()` (2³²) | rank 1 | 3.44 × 10¹⁰ | 32.4 years |
| G2 Perl 5.14 `srand` (2³²) | *"never swept"* | 3.44 × 10¹⁰ | 32.4 years |
| G4 TeX `\pgfmathrandom` (2³¹−2) | *"**fully enumerable**"* | 1.72 × 10¹⁰ | 16.2 years |
| **G3 Python 2.7 `seed(str)`, 10⁴ dictionary** | *"cheap to close"* | 8.0 × 10⁴ | **40 minutes** |

**11,838 × a 24-hour budget** for the worst; the trigger was 10³×. The plan's own words —
"enumerable in minutes", "fully enumerable" — describe the cost of *generating* the keystreams,
not of *adjudicating* them, and the two differ by nine orders of magnitude. **G3 is the only one
of the four that is enumerable in the sense the plan means.**

### D.2 D-ii — and the only affordable route is the defect the round exists to remove. **FOUND-ERROR — this is the finding**

There is an obvious fix: prefilter cheaply, beam only the survivors. Measured here:

- `round17/lib_padsweep.dense_scan`, the repo's only prefilter, runs at **≈3.2 × 10⁵
  candidates/s per core** in numpy (321,455 measured; 275,708 on a warm-up run).
- At keep = 10⁻⁴, a 2³² × 8 space costs **5.8 h of prefilter + 1.2 d of beam = 1.4 days** on
  6 cores. G4 costs 17 hours. **Phase 2 becomes entirely affordable.**

And here is the problem. `dense_scan` scores by

```python
P = (C[None, :] + sign * Kw) % N        # RIGID
...
sc += T[P[:, j-2], P[:, j-1], P[:, j]]  # ENGLISH rune-trigram, trained on kjv/moby/pride/war
```

— a **rigid** decode under an **English-only** trigram model over a 24-rune head. That is
simultaneously:

- **the rigid alignment** the doctrine forbids on LP2 (mechanics §3: "Never use a rigid decoder
  on LP2"), which `round18/L2` then quantified: rigid survival decays as `(1−ρ)^L` and hits
  **0.495 at `PREFILTER_LEN = 24`**; and
- **the English-only register** that I2 exists to remove (L7-A.7 already flagged this for R17).

I measured the true-key survival through it directly — correct key, real construction, true
offset ranked against 400 wrong offsets, keep = top-40:

| register | `keyskip` survival | `skip_by_two` survival | median rank of the true offset |
|---|---:|---:|---:|
| LP1 | 0.83 | 0.83 | 1 / 400 |
| EN | 0.77 | 0.77 | 1 / 400 |
| LA | 0.77 | 0.80 | 1 / 400 |
| OE | 0.77 | 0.87 | 1–8 / 400 |
| EN_HALF | 0.70 | 0.80 | 2 / 400 |
| **CY** | **0.67** | **0.60** | **6–11 / 400** |

So the prefilter is not a catastrophe — it is a **discount**, and a bounded one: it loses 17–40 %
of true keys and it loses them unevenly by register (Welsh worst at 0.60). That is genuinely
better than I expected and it is reported as such. But the structure is what matters:

> **Round 19's Phase 2 is affordable only through a gate that reimposes rigid alignment and an
> English-only register — the two defects the round's own Phase 0 exists to repair. The round
> would spend 30 % of its budget building a multi-register drift-tolerant instrument and then put
> a rigid English filter in front of it.**

The fix is not expensive, and the plan should say it: build the prefilter **skip-aware and
multi-register** (a 3-state cheap beam over a 24–32-rune head, max over the 5 near-independent
registers of §B.1 rather than 9), measure its survival per register, and publish coverage ×
survival. Until that exists, **no Phase-2 negative can claim register coverage no matter what I2
does downstream**, because I2 never sees the discarded 20–40 %.

### D.3 D-iii — what S2 can physically reach. **FOUND-ERROR**

| sweep | rows stored | of N decodes | best | **stored cutoff** | key params stored? |
|---|---:|---:|---:|---:|---|
| B-04 stage A | 50 | 1,385,600 | −6.185 | **−6.412** | yes |
| B-04 stage B | 50 | 1,290,240 | −6.129 | **−6.403** | yes |
| B-04 stage C | 50 | 3,548,160 | −5.885 | **−6.228** | yes |
| B-04 stage D | 2 | — | — | — | no |
| R16-PRNG | 20 | 52,556 | −6.347 | **−6.559** | yes |
| R17 P0–P3 | ~1,140 | 1.45 × 10¹⁰ | — | — | partial |

**~1,312 rows** against L7-C.6's repo-wide tally of **17,058,157,809** scored decodes:
**7.7 × 10⁻⁸**, four orders of magnitude below the 10⁻⁴ trigger.

The stored rows **do** carry full key parameters (`seed`, `gen`, `sign`, `atbash`, `offset`), so
S2 can genuinely re-decode them with a repaired instrument — that part of the plan works. But it
is decisive that they are the **English argmax** of their sweeps, and the cutoffs are hard:

> B-04 stage A stored everything above **−6.412**. Under `skip_by_two` the **correct key** scores
> **−6.718** (this lane, L = 240; L7-B measured −6.90). **A correct key inside B-04's swept space
> would, under the construction L7-B found, have scored 0.31 below the cutoff and would not be in
> the stored 50.** The same holds for stage C (−6.228) and R16-PRNG (−6.559).

So S2 is not merely small, it is **structurally unable to recover the case that motivates it.**
L7-A.5's rank-1 argument — that a Latin or half-vowel-English correct key would still have been
rank 1 and therefore stored — is an argument made under the **`exact`** transition model. L7-B's
own finding voids it: under `skip_by_two` the correct key is not rank 1, it is somewhere around
rank 10⁵. **S2 should be re-scoped to "re-adjudicate 1,312 English-argmax survivors under a
multi-register panel", which is a two-hour job with a small expected yield, and should not be
sold as "the only route to recovering any value from 10¹⁰ discarded decodes."**

### D.4 D-iv — Phase 3 is specified against a repository state that is not true. **FOUND-ERROR**

`CAMPAIGN-PLAN.md` Phase 3, checked against `round18/` as it stands:

| plan says | actually on disk |
|---|---|
| **C1** — "L5 … `RESULTS.md` is a TBD skeleton" | `L5-payload/RESULTS.md`, **206 lines**. "A-04 complete. E-01 in progress." A-04 is done with a new independent instrument (`pixelmatch.py`) and finds **11** disagreeing cells, not 6. Three `_TBD_` stubs remain, all in the E-01 tail. |
| **C2** — "L6 … PREREG written, **no results**" | `L6-offset-marsaglia/RESULTS.md`, **377 lines**. **287,834,112** offsets (B-02) + **299,999,280** (Marsaglia) densely scored, positive controls **PASS 40/40 and 16/16**, both NEGATIVE with stated bounds. |
| **C3** — "L8 PGP verification table has data and **no `RESULTS.md`**" | `L8-provenance/RESULTS.md`, **448 lines**. 228 `.asc` files, 192 PASS / 3 FAIL / 22 NO-SIG, grouped to **54 distinct signed messages, 54 verify**, one signing key ID; plus a timestamp seed dataset and an `I-01` adjudication. |
| **C3** — L3 ornament reader | `L3-ornaments/RESULTS.md`, **159 lines**, honestly marked **IN PROGRESS** — this one is real. |

Three of the four closeout targets are **already delivered**. Only L3's band reader and L5's
E-01 tail are genuinely open. Phase 3's ~10 % is aimed at roughly **2 %** of real work.

Related, and worth more than the closeout: `round18/L2-filter-leak` is not referenced anywhere in
Round 19's plan, and it contains **exactly the assets I1 needs** — `fastbeam.py`, a
bit-identical re-implementation of the beam that is **9× faster** (7.6 s vs 68 s for a full-book
12,956-rune decode) using the same last-3-characters-plus-backpointer design this lane
independently arrived at, and gate **B.3**, the full-book positive control at **−4.098 / 0.9997
recovery**, which is the model for the gate §A.6 argues I1 must have. **I1 should start from
`fastbeam.py`, not from `skipdecode.beam_decode`** — that alone recovers most of the 10×
slowdown `union2` costs.

### D.5 D — the steel-man for spending the budget elsewhere

Doctrine R5's ranking, priced against what this lane measured:

| object | doctrine rank | cost | what a hit looks like | current status |
|---|---|---|---|---|
| **450 located O/A/AE transcription disagreements** | **1** (finite, human-checkable) | bounded, human-checkable, decidable from pixels | the ciphertext itself changes → **every** negative in the repo is re-opened, not re-weighted | located; not adjudicated |
| **6 (really 11) contested payload bytes** | **1** | L5's `pixelmatch.py` already built | a resolved 256-byte payload → a concrete PRF seed for B-04/E-01 | A-04 **done**, E-01 tail open |
| **47 unread ornament bands** | **1** | L3's reader is written | a second data channel | **IN PROGRESS**, genuinely open |
| **G3 Python 2.7 `seed(str)`** | 2 (enumerable) | **40 min** measured | a silent coverage hole closed | never swept |
| G1/G2/G4 full enumeration | 2 (enumerable *in name*) | 16–32 **years** beam-only, or 17 h–1.4 d **behind a rigid English prefilter** | — | never swept |
| **I1/I2/I3** | 3 (instrument) | measured here to be achievable | every future negative gets its power stated | **not started** |
| **A skip-aware, multi-register prefilter** | 3 (instrument) | small; the missing piece of §D.2 | Phase 2's negatives become sayable | **does not exist** |

The rank-1 objects share a property none of G1–G4 has: **their outcome is decidable, and one of
them (the transcription disagreements) can invalidate the input every other lane depends on.**
A sweep's most likely outcome is another conditional null; a transcription audit's most likely
outcome is a fact.

---

## E. IS ROUND 19 CORRECTLY AIMED?

**Partly. Phase 0 is aimed correctly and is worth more than the plan claims. Phase 1/2 is aimed
at a target the plan cannot afford to hit honestly. Phase 3 is aimed at work that is already
done. My recommendation is REDIRECT — not STOP.**

Taking the doctrine's own test to the round itself:

**Q1 (would the instrument recognise a hit?)** — For Phase 0, yes, *if* I1 is gated on recovery
rather than score. §A.6 is the sharpest thing in this lane: at `free/ms4` the **correct key**
scores −4.274 — *better than the working decoder's baseline* — at **6 % recovery**. A score-gated
I1 validation passes a decoder that hallucinates. The plan's I1 row phrases success in score
terms. **This is the single change most likely to save the round.**

**Q2 (what raises the prior?)** — Weaker than claimed. §C shows the L1 prior does not pin an OS
generation, does not uniquely identify the encoder, carries multipliers with no derivation, and —
except for rank 5 — argues about **tool availability in 2012–14**, not about pad generation.
G1–G4 are a good set of lanes because they are *enumerable and never swept* (R5 rank 2), and that
is enough to justify them. They should be labelled that way and not as R4 evidence-derived priors.

**Q3 (bounded?)** — Only one of the four is bounded in the sense the plan means. §D.1: G3 is
40 minutes; G1, G2 and G4 are 16–32 years through the repaired instrument, or 17 h–1.4 days
behind a **rigid English** prefilter. "Enumerable" was measured on keystream *generation*; the
adjudication is nine orders of magnitude more expensive.

**Q4 (the three conditionals)** — The plan states them well, and then Phase 2 as designed cannot
honour the third. §D.2: I2 can only adjudicate what reaches it, and at 2³¹–2³² candidates
nothing reaches it except through a filter whose register panel is `{English}` and whose
alignment model is `rigid`.

**Q5 (kill condition)** — The plan has no checkpoint at which Phase 2 is abandoned. It should:
*"if the prefilter is still English-only and rigid when Phase 0 gates pass, Phase 2 does not
run."*

### The recommendation

1. **KEEP Phase 0, and re-specify I1.** Not "drift-tolerant". **Constrained-union first**
   (`union2`: 0.000 baseline cost, +0.086 on the bar, recovery 1.00 on both constructions and
   **1.00 in every register** — §B.4), with a **cost-regularised** drift term (λ ≈ 4–10 in raw
   quadgram log-units) as a *second, separately-adjudicated* hypothesis for genuinely
   unrepresentable advances. Build on `round18/L2`'s `fastbeam.py`. **Gate on recovery ≥ 0.90 on
   a `skip_by_two` plant at L ≥ 240, not on score.** Each construction is one extra test, so the
   family-wise cost of covering three constructions is ≈ 0.08 of bar — nothing.
2. **KEEP I2 but change I3's job.** Do not "correct for 9 tests": M_eff is **5.0**, the panel's
   naive FPR is **5.4 %**, and the registers are unevenly redundant (`EN_HALF`~`EN` at r = 0.84).
   Calibrate a **direct null on the panel maximum** — exact regardless of correlation, same cost.
   Trim the panel to the ~5 near-independent registers and say so.
3. **BUILD THE MISSING LANE: a skip-aware, multi-register prefilter.** It is the load-bearing
   piece of Phase 2 and it is in nobody's lane. Publish its per-register survival. Without it,
   Phase 2's negatives cannot state their register conditional and are worth what Rounds 8–17's
   were worth.
4. **RUN G3 NOW (40 minutes) and RESCOPE G1/G2/G4.** G3 is the one genuinely enumerable, genuinely
   never-swept item. For the others, either run a **stated-fraction sample** with honest coverage
   ("2³² seeds, 10⁻³ sampled, coverage 0.1 %, power X per register") or hold them until item 3
   exists. Do not publish "enumerated" for a space that was prefiltered at 10⁻⁴ by an English
   rigid scan.
5. **RESCOPE S2 downward and honestly.** 1,312 rows, 7.7 × 10⁻⁸ of the scored space, all English
   argmax, and under `skip_by_two` the correct key would sit **0.31 below B-04's stored cutoff**.
   It is a two-hour re-adjudication with a small expected yield. It is not "the only route to
   recovering any value from 10¹⁰ discarded decodes" and should not be budgeted as one.
6. **CUT Phase 3's C1/C2/C3 to what is actually open** — L3's band reader and L5's E-01 tail —
   and move the freed budget to the doctrine-R5 rank-1 object nobody has touched: **the 450
   located O/A/AE transcription disagreements.** That is the only open item whose resolution can
   change the *input* rather than re-weight the search, and by this repo's own history
   (`round12` found a truncated `_560.00` and a drifted mirror by auditing an input) it is the
   activity with the best measured yield.

### The one-line answer

**Round 19 is correctly aimed at the instrument and mis-aimed at the haystack.** Fix the magnet —
the measurements in §A say it can be fixed, cheaply, and better than the plan hoped. Then notice
that the haystack is not small: it is 10⁹ times larger than the adjudicator can search, and the
only thing that makes it look small is a filter made of exactly the material Round 18 proved was
broken.

---

## F. WHAT THIS LANE DID NOT COVER

Per doctrine R7 — bounds, not verdicts.

- **I1, I2 and I3 as code. UNTESTED.** They did not land during this run. Every A/B verdict is
  against the specification in `CAMPAIGN-PLAN.md` and against decoder families I built to match
  it. If I1 ships a transition relation outside my five families, my frontier does not bound it.
- **Structured wrong keys.** My null is uniform-random keystreams. Near-miss seeds, offset-shifted
  correct keys and prefix-sharing keys — the wrong keys a seed sweep actually generates — are not
  covered, and are plausibly *worse* under a permissive relation than uniform ones. **This is the
  cheapest follow-up to A and I recommend it before I1's gate is written.**
- **λ was bracketed, not optimised** (4 ≤ λ ≤ 10). Beam width fixed at 400. One key family. One
  register in the A frontier. Constructions tested one at a time.
- **`jpegtran` is not installed here**, so the lossless-optimise arm of C-i is untested; the PIL
  arm alone is sufficient to fire the trigger.
- **The two-stage encoder question is not settled by C-i** — it shows non-uniqueness, not a
  different answer. ImageMagick remains the best single fit on the auto-grayscale argument.
- **The GnuPG distro table is external research**, verified against Launchpad / Debian Sources /
  the gnupg-1.4.11 source tree (`g10/armor.c`, `g10/gpg.c`); openSUSE and the exact CentOS 6
  `gnupg`-1 NEVR are **unconfirmed**.
- **Throughput is one machine** (6 cores, WSL, CPython 3.14). A C or numpy-vectorised beam would
  change §D.1's absolute numbers, though not the ratio between `exact` and `union2`, nor the nine
  orders of magnitude between generating and adjudicating a keystream.
- **Nothing here is a statement about the cipher.** Every result is a property of Round 19.

### What would reopen each finding

| finding | reopens if |
|---|---|
| A-i NO-ERROR-FOUND | a structured-wrong-key null (not uniform) shows separation collapsing at `union2`'s branching, or I1 ships a relation outside my five families |
| A-iv (score/recovery decoupling) | it does not — it is a direct measurement; it *closes* if I1's PREREG gates on recovery |
| B-i / B-ii | I2 calibrates a direct null on the panel maximum instead of a per-register bar |
| B-iii | the archive's own contrast spread differs materially from my noise-decode reference; L7's `out_a2.json` holds the raw contrasts and a direct comparison is a one-hour job |
| B-iv | I1 ships constrained rather than free drift, in which case it is *superseded by an improvement*, which is the outcome I want |
| C-i | someone measures ImageMagick 6.x `coders/jpeg.c` against the LP2 vector directly (L1's own NC-2), or a source PDF surfaces (NC-6) |
| C-ii | the corpus is shown to have been re-armored downstream, or a second dated artifact narrows the OS |
| C-iii | L1 §6.2 is restated as an ordering with the multipliers withdrawn, or the multipliers are derived |
| D-i / D-ii | a skip-aware multi-register prefilter is built and its per-register survival published |
| D-iii | a sweep persists the doctrine-R3 statistics at sweep time so future re-adjudication is possible at all |
| D-iv | it does not; it is a documentation fix |

---

## G. REPRODUCE

```bash
cd liber-primus/analysis/round19/R1
python3 a_permissive.py    # the frontier, 16 configs           -> out_a.json
python3 a2_union.py        # union2 + the lambda scan           -> out_a2.json
python3 a3_effperm.py      # realised permissiveness            -> out_a3.json
python3 b_panel.py         # the register panel, 4 attacks      -> out_b.json
python3 c_prior.py         # PGP corpus, encoder alts, shifts   -> out_c.json
python3 d_budget.py        # throughput, prefilter, S2 reach    -> out_d.json
```

Requires Ghostscript, Pillow and numpy under WSL. Trust anchor before and after:
`python3 liber-primus/tests/validate.py`.
