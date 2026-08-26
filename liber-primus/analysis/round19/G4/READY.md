# ROUND 19 / G4 — READY — the Phase-2 run spec for TeX-internal generators

_Written 2026-08-26 at the scoring boundary. Lane G4 is **HOLDING**: its generators are
validated and its keystream interface is live, and it has adjudicated **nothing**._

---

## 1. State

| item | state |
|---|---|
| generators reimplemented | `gen_tex.py` — pgf, `lcg`, `random.tex`, pdfTeX |
| byte-exact vs the real TeX binaries | **PASS, 4 of 4**, 15 808 elements, `validation.json` |
| era-correctness (pgf 2.10 vs pgf 3.1.11a) | **PASS**, 76/76 vectors identical |
| single-cycle claim (offsets absorbed) | **PASS**, both multipliers are primitive roots mod 2³¹−1 |
| `random.tex` default-seed path incl. warm-ups | **PASS** |
| ground-truth plant-and-recover | **V5 as pre-registered: FAIL. V5a: PASS** — see PREREG ADDENDUM |
| decodes scored against LP2 for a search | **ZERO** |
| pilot | `pilot.py`, 10 000 decodes, labelled `pilot:true, interpretable:false` |

Phase 0 exists on disk (`round19/I1/driftbeam.py`, `round19/I2/adjudicate.py`,
`round19/I3/`), so the pilot was run under the brief's allowance. **This lane has not been
shown the I1/I2/I3 PASS verdicts, and nothing in the pilot is interpreted.**

---

## 2. The generators S1 consumes

```python
import sys; sys.path.insert(0, ".../analysis/round19/G4")
import gen_tex as gt
ks = gt.make_ks("pgf_mod29", seed, nsym, direction="fwd")     # list[int] in Z_29
gt.advance("pgf", z, k)                                       # phase arithmetic
gt.build_master("pgf", mapping, path)                         # the whole 2^31-2 cycle, uint8
```

Nine named generators (`gt.GEN_NAMES`), four stream families:

| stream family | generators | phases / seeds | offsets |
|---|---|---:|---|
| `pgf` mod-29 | `pgf_mod29`, `pgf_mod29_c1` | 2 147 483 646 | absorbed |
| `pgf` rnd-scaled | `pgf_rnd29` | 2 147 483 646 | absorbed |
| Park–Miller mod-29 (`lcg`) | `lcg_mod29`, `lcg_mod29_c1` | 2 147 483 646 | absorbed |
| Park–Miller div-scaled (`random.tex`) | `randomtex_div29`, `randomtex_div29_c1` | 2 147 483 646 | absorbed |
| pdfTeX lagged-Fibonacci | `pdftex_u29`, `pdftex_u29_c1` | 268 435 456 | **not** absorbed — sweep B-04's ladder |

---

## 3. THE FULL-ENUMERATION COST, HONESTLY

### 3.1 The naive number, and why it is not the answer

Counting `phases × sign(2) × direction(2) × atbash(2) × c(2)`:

| family | full-enumeration decodes |
|---|---:|
| pgf mod-29 | 3.44 × 10¹⁰ |
| pgf rnd-scaled | 3.44 × 10¹⁰ |
| `lcg` | 3.44 × 10¹⁰ |
| `random.tex` | 3.44 × 10¹⁰ |
| pdfTeX (× 11 offsets) | 4.72 × 10¹⁰ |
| **total** | **1.85 × 10¹¹** |

**Measured** costs on this box (6 cores, 15 GiB), L = 120, from `pilot_results.json`
(10 000 real decodes) and a separate component timing:

| stage | s/decode | decodes/s, 1 proc | decodes/s, 6 procs |
|---|---:|---:|---:|
| I1 `exact` beam alone (= the repo's Round-18 decoder) | 0.0030 | 333 | ~2 000 |
| I1 `pair` beam alone | not measured separately | — | — |
| **I1 `drift` beam alone** (`permissive`, `max_skip=40`, `max_free=2`) | **0.679** | **1.5** | ~9 |
| I2 `adjudicate()` (nine registers + four R3 statistics) | 0.0078 | 128 | ~770 |
| **full pipeline at `exact`** (keystream + beam + adjudicate + row) | **0.0170** | **59** | **≈ 354** |
| full pipeline at `pair` | 0.0155 | 65 | ≈ 390 |
| **full pipeline at `drift`** | **0.619** | **1.6** | **≈ 9.7** |

1.85 × 10¹¹ decodes at the **`drift`** pipeline rate is **1.2 × 10¹¹ seconds ≈ 3 700 years on
six cores**. At the `exact` pipeline rate it is ≈ 17 years. **Direct beam enumeration of this
space is not affordable, and no amount of parallelism on the hardware this project has changes
that.** Anyone who writes "G4 enumerated its space" without the paragraph below is wrong.

> **Two cost ratios, and they say different things.**
> Beam-only, `drift` costs **226 ×** `exact` (0.679 vs 0.0030 s). End-to-end, it costs only
> **36.5 ×** (0.619 vs 0.0170 s) — because on the `exact` path the *adjudicator* and the
> keystream generation, not the beam, are most of the cost. Both numbers matter and they
> matter to different decisions: the 226 × governs how much drift-tolerance a re-decode stage
> can afford, and the 36.5 × governs the whole-sweep budget. At **9.7 decodes/s**, the
> repaired instrument at full drift affords ≈ **6 × 10⁶ decodes/week**. Phase 2's budget is
> therefore a *decision about which 10⁶ decodes*, not a coverage number, and S1 should be told
> that before it plans rather than after.

### 3.2 The route that makes the Lehmer families affordable — measured, not assumed

The three Lehmer families are **one cycle each**, so the entire space is a **sliding window
over one array**. `bench_master.py` measured both stages on a 2²⁴-phase slice and extrapolated
×128:

| stage | measured (2²⁴ slice) | full 2³¹−2 |
|---|---:|---:|
| build the reduced master cycle (uint8) | 1.92 s | **246 s**, 2.00 GiB |
| one rigid 32-rune prefilter pass | 11.31 s | **1 447 s** |
| all 8 cells (sign × dir × atbash × c) | — | **3.2 h per stream family** |
| four Lehmer stream families, all cells | — | **≈ 13 h** (one core; embarrassingly parallel) |
| beam stage | — | set by the cut × band product, §3.3 |

The prefilter reduces 1.4 × 10¹¹ *nominal* decodes to **13 hours of numpy** plus a beam stage
whose size the operator chooses. What the beam stage costs is not a property of the space; it
is a property of the cut, and the cut is only as tight as the prefilter's measured power lets
it be. Two worked points, at the `exact` pipeline rate on six cores (354 decodes/s), with the
band inflation of §3.3 at `max_skip = 40` (× 81) and 32 cells (4 families × 8):

| band-max cut | bands retained per cell | beam decodes | wall clock |
|---:|---:|---:|---:|
| 10⁻⁴ | 214 748 | 5.6 × 10⁸ | **18 days** — too expensive |
| 10⁻⁶ | 2 147 | 5.6 × 10⁶ | **4.4 h** |
| 10⁻⁷ | 215 | 5.6 × 10⁵ | 26 min |

Then re-decode the top ≈ 10⁴ of *those* at `drift` (9.7 decodes/s): **≈ 17 min**.

**So the complete T1/T2/T3 enumeration is ≈ 18 hours of wall clock, not 17 years** — provided
the prefilter is allowed to make the first cut *and* the cut can be taken at 10⁻⁶ rather than
10⁻⁴. That is the whole proposal. It is **conditional on a measurement nobody has made yet**
(§3.3 requirement 1), and it is offered as a plan with a kill condition attached, not as a
promise.

### 3.3 What the prefilter must be gated on — three requirements, all from measurements

1. **Measured power, from I1/I2 — the K2 kill condition.** A rigid 32-rune prefilter is a
   *rigid* decoder, and L7-A/L7-B are about exactly that. Before a single full pass is run,
   plant 200 pads at known phases, push them through the prefilter, and measure the fraction
   of planted phases surviving a 10⁻³ cut. **If that fraction is < 0.50, the full-enumeration
   plan is abandoned** and G4 collapses to Tier 1 (§4). This is pre-registered in
   `PREREG.md` Q5/K2 and must not be softened.
2. **The cut must keep a BAND, not a point.** The V5 control measured that the rigidly best
   phase is the planted phase **advanced by the number of key skips** (planted rank #2 of
   80 004; argmax at phase + 2 with 2 skips). A top-K cut that keeps isolated maxima can
   therefore discard the true phase while keeping its neighbour. **Requirement: every retained
   phase carries its ± `max_skip` neighbourhood into the beam stage.** At `max_skip = 40` that
   is an 81× inflation of the cut, so the cut fraction must be set with that factored in — a
   10⁻⁴ cut becomes 1.7 × 10⁷ beam decodes, not 2.1 × 10⁵. **Budget the band, or the run is
   either unaffordable or unsound.**
3. **Language register.** The prefilter's lookup table is a *unigram* model and therefore
   carries the same English-only defect L7-A measured. It must be built from I2's register
   panel (max over registers, or a register-agnostic statistic such as `ioc` / `mds`), not from
   the English quadgram model. **A prefilter built on English alone reproduces Round 18's
   error at 10⁹ scale.**

### 3.4 pdfTeX is a different shape and needs its own answer

T4 has a 55-word state, so there is no single cycle and no sliding window: each of the 2²⁸
seeds needs its own `init_randoms` + three warm-ups + L draws. Vectorised across seeds with
numpy (state as an `(nseed, 55)` int32 array) this is arithmetic-bound at roughly
4 × 10² integer ops per seed for a 128-symbol prefix, i.e. ≈ 10¹¹ ops for the full 2²⁸ —
**order a day of generation**, plus prefilter, plus the 11-offset ladder that is *not*
absorbed here. **Recommendation: run T4 at Tier 2, after the Lehmer families, and only if
Tier 1 has not already answered.**

---

## 4. The ordering — highest prior first

Doctrine R4: prior beats volume. The ordering below is by *how likely an author is to have
produced that state*, not by how big the slice is.

| tier | what | decodes | wall clock, 6 procs | why it is first |
|---|---|---:|---|---|
| **T1a** | **pgf default seed** `\time × \year`, years 2010–2015 — the state you get if you *never call* `\pgfmathsetseed` | 8 627 × 8 = **69 016** | **3 min** at `exact`, **2.0 h** at `drift` | an author who wrote `\pgfmathrandominteger{\r}{0}{28}` and never thought about seeding lands **here**, and the space is 8 627 |
| **T1b** | **`random.tex` default seed**, date-initialised, years 2010–2015, incl. the three warm-up draws | 3.21 M × 8 = **25.7 M** | **20 h** at `exact` (`drift` = 31 days — do not) | same argument; enumerable; the warm-ups are validated (gate V6) |
| **T1c** | **author-typed integers**: 0 … 2²⁰ for all four generators, plus B-04's `num_*` / `primes_*` dictionary (3301, 1033, 761, 845145127, 1595277641, dates as epochs) | 1.05 M × 8 × 4 = **33.6 M** | **26 h** at `exact` | `\pgfmathsetseed{3301}` is the single most Cicada-shaped line of TeX imaginable |
| **T2** | **full Lehmer phase enumeration** via §3.2 | 1.4 × 10¹¹ nominal | **≈ 18 h** at a 10⁻⁶ band-max cut | only after K2 passes |
| **T3** | **pdfTeX 2²⁸ seeds × 11 offsets** | 2.4 × 10¹⁰ nominal | ≈ 1–2 days | §3.4 |
| **T4** | per-page / per-line reseeding (B-04 stage-C shape) | — | — | **declared out of bound** in PREREG §7; a follow-up, not this run |

**T1a is 69 016 decodes.** It is the cheapest genuinely-high-prior slice in Round 19, it is
*complete* rather than sampled, and at the `exact` preset it runs in three minutes. **If S1
runs one thing from G4, run T1a at the `drift` preset — two hours on six cores — and have it
done properly, with I1's repaired transition relation and I2's nine registers, for the whole
default-seed space at once.** That is a complete, high-prior, instrument-correct result for
the cost of a long lunch, and this project has not had one of those in eleven rounds.

---

## 5. What S1 must write into every `SWEEPROW` header

All three doctrine-Q4 conditionals, plus the two this lane adds:

```python
adj.header("round19/S1/G4-tex",
    key_space      = "<generator> <stream family> phases <a>..<b> ; sign; dir; atbash; c in {0,1}",
    decoder        = "round19/I1 driftbeam PRESETS[<name>] = <full kwargs dict>",
    adjudicator    = "round19/I2 panel build <id>",
    generator_validation = "round19/G4/validation.json (V1 PASS, byte-exact vs pdflatex)",
    offsets_absorbed     = True,     # False for pdftex_*
    prefilter            = "<none | rigid-W32 cut=1e-4 band=+-max_skip, power=<measured>>",
)
```

`offsets_absorbed` and `prefilter` are not optional. Without the first, a later reader cannot
tell whether the offset ladder was swept or absorbed; without the second, a null from a
prefiltered sweep is a null of unknown coverage.

---

## 6. The kill conditions, restated

* **K1** — fewer than two generators byte-exact ⇒ lane INCONCLUSIVE. **Not triggered: 4 of 4.**
* **K2** — planted phase survives a 10⁻³ prefilter cut in < 50 % of 200 trials ⇒ **abandon T2**,
  restrict G4 to Tier 1. **Not yet measured — this is the first thing Phase 2 must run.**

---

## 7. What reopens this lane if Phase 2 returns nothing

* a source PDF/PostScript surfacing with an embedded font subset naming the typesetting program
  (L1 NC-6 — still the highest-value unrecovered artifact after the ciphertext);
* evidence of **per-page or per-line reseeding**, which is declared out of bound here;
* a `c ∈ Z₂₉` Caesar sweep on the reduced key, also out of bound here;
* any `allrunes` follow-up (see `RESULTS.md` §6) that pins the *shape variant*, which would pin
  the LaTeX source and with it the plausible package set.
