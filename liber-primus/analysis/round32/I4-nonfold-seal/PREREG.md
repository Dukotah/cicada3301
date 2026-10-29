# I4 -- Non-fold oracle-seal proxy (reopens round21/L1 KILL)

_Pre-registered 2026-10-28, BEFORE any feature was extracted or any ROC computed. Binding:
`ARMADA-DOCTRINE.md`. Only the 8-register panel build + a timing probe had been run when this was
written; no hallucination/genuine population had been scored._

## Setup carried over unchanged from round21/L1
Tuning split = planted-45 EN_NOVOWEL hallucinations (key `CICADA`, reps 0..59, rng 5000+rep, csd 600+rep)
vs genuine EN_MODERN panel (20 reps, seed 7000, csd 99). Held-out split = surrogate hallucinations
(key `CICADA3301`, 90 reps, seed 8000, csd 2600) vs surrogate genuine (24 reps, seed 9100, csd 770).
L=240, SUPP=0.83, `exact` preset, bar = panelmax_bar(exact, 1e6, 0.01) = 7.634. Hallucination = pmax>=bar and
true rune-index recovery <0.90. Genuine = pmax>=bar and recovery >=0.95. Tune on tuning split, FREEZE the
operating point, score held-out once. Comparison anchor: L1 held-out 0.818 catch / 0.167 false-reject.

## The three non-fold families and the hybrid (designs fixed now)
Every statistic is oracle-free (no plaintext, no truth index).
* **D1 LONGHEAD.** Single attribute/verify cut with a longer attribution head than the 24-32 runes that
  capped R20-P1 (and than hitfn20's 1/4 = 60 runes): head h in {24,32,48,60,80,96,120,144,168,192,216};
  accept iff tail self-consistency >= tau, tau in {0.80,0.85,0.90,0.95,0.98,1.00}. Also D1b: accept iff
  tail self-consistency >= tau on EVERY cut in a stated set of heads (a multi-head AND, still not a
  disjoint-fold scheme because heads are nested prefixes of increasing length).
* **D2 PERREG.** The L1 k-fold min statistic (k in 2..8) with a bar that depends on the decode's argmax
  register: EN-family (EN_MODERN, EN_KJV) keeps 0.90; every other register uses tau_N in
  {0.90,0.92,...,1.00}. Tuned (k, tau_N) on tuning only.
* **D3 LEARNED.** L2-regularised logistic regression (numpy, fixed lambda grid chosen by leave-one-out on
  the tuning split only) on oracle-free features: fold/cut recoveries, cross-construction decode agreement
  (exact vs exact_ms8 vs pair, beam_w 100 vs 400), head-prefix pmax at 64/120/180, pmax-bar margin, pmax_ne,
  pcon, ioc, mds, h2, zl, skip counts. Two variants: **D3a register-blind** (no preg/z-vector/pmax-vs-EN-gap
  features) and **D3b register-aware** (adds preg one-hot and z-vector).
* **D4 HYBRID.** D2 AND D1 (both must accept) and D3 AND D2; cheap conjunctions only, enumerated, not searched
  beyond the stated grids.

## Aiming Test
**Q1 recogniser.** A mis-classification is a hallucination the proxy ACCEPTS, or a genuine decode it
REJECTS. Planted-hit control: the genuine EN_MODERN panel (all designs must accept it at FR<=0.10 on tuning)
and the L1 single-cut baseline must reproduce its known leak (15/45 originally) before any non-fold design is
trusted. Stronger planted shape added for the register axis: genuine correct-key **EN_NOVOWEL** decodes
(recovery >=0.95, pmax>=bar) and correct-key LATIN/DE/OE/EN_KJV decodes -- the real shapes a true LP2 solve
in those registers would take. A design that only separates registers (rejects everything EN_NOVOWEL-argmax)
would catch 100% of hallucinations and is NOT a seal; the hard-register genuine sets expose it.
**Q2 prior.** `round21/L1-seal-realmode-proxy/RESULTS.md` lines 110-118 name exactly these three families as
unmeasured; `round20/P1/RESULTS.md` l.22/94 documents the 24-32-rune head cap; fold ceiling measured 0.80-0.867
(k=5/min 0.818 held-out). Not a completeness ritual: it is the named open door.
**Q3 bounded.** Enumerable: <=~11 heads x 6 taus (D1), 7 k x 6 tau_N (D2), 2 learned variants x lambda grid
(D3), a handful of conjunctions (D4). All designs are deterministic functions of a cached per-case feature
table; hallucination/genuine populations are the L1 populations (n=45/20 tuning, ~66/24 held-out).
**Q4 conditionals.** (1) key space: correct key only (hardest case; wrong-key behaviour is not measured);
(2) decoder relation: `exact` (keyskip1) preset, the planted overfits are keyskip-enciphered; keyskip2/drift
overfits unmeasured; (3) adjudicator register: 8-register panel (CY missing, see below), hallucinations are
EN_NOVOWEL-argmax correct-key overfits, genuine primary set EN_MODERN.
**Q5 kill.** Checkpoint at the first feature table (about 10% of budget): if the population cannot be
rebuilt (hallucination n<20 tuning or <30 held-out, or the L1 single-cut baseline wildly unreproduced),
report the gap and stop. Final kill: if the best design's held-out cell is not >=0.90 catch AND <=0.10 FR,
SEAL_PASS=false unchanged, ceiling reported.

## Pass criteria (set now)
* **SEAL_PASS_L1_COMPARABLE:** a design with ONE operating point frozen on the tuning split that scores
  >=0.90 catch on the held-out hallucinations AND <=0.10 false-reject on the held-out EN_MODERN genuine set,
  AND was >=0.90/<=0.10 on tuning.
* **SEAL_PASS (strict, the verdict):** the above AND false-reject <=0.10 on the pooled register-spread
  genuine set (EN_NOVOWEL correct-key genuine + LATIN/DE/OE/EN_KJV genuine) -- "the seal must hold across
  the I2 panel". A design that passes only the comparable test is reported as `comparable_only`.
* Wilson 95% intervals are reported for every held-out rate; a point estimate >=0.90 whose lower bound is
  <0.80 is flagged under-powered. Because many (design, parameter) cells are inspected, the frozen cell is
  chosen by a pre-stated rule (max tuning catch s.t. tuning FR<=0.10, ties -> simpler/larger-margin) and is
  reported with the number of cells it was selected from; the held-out number is scored once.

## Known environment gaps (stated up front)
* `data/keys/welsh/welsh_mabinogion.txt` missing: the CY register cannot be trained -> 8-register panel
  (rebuilt into this lane's `models/`, 4000 null draws/length vs 20000 originally). pmax distribution and the
  7.634 bar (calibrated for 9 registers) are therefore approximate; the bar is kept at 7.634 for comparability
  (conservative: fewer registers => lower null max).
* `data/kjv.txt` and `data/keys/mabinogion.txt` missing; same-named texts from `analysis/bookcipher/books/`
  substituted. Populations are therefore NOT guaranteed bit-identical to L1's 45/66/20/24; the achieved
  counts are reported honestly and the single-cut baseline rate is re-measured, not assumed.

---
## ADDENDUM A (written 2026-10-28 AFTER the seen-data run, BEFORE any virgin data exists) -- D5 pmax-margin

What the seen data showed (so the reader can judge the contamination): the pre-registered learned gates D3a/D3b
reach 1.00 catch / 0.00 false-reject on the L1-style EN_MODERN genuine set, but reject 13/13 correct-key
EN_NOVOWEL genuine decodes -- they separate REGISTERS, not hallucination from genuine, so they fail the strict
register-spread criterion. An exploratory within-EN_NOVOWEL look (`within_register.py`, 109 hallucinations vs
13 genuine, POOLED tuning+held-out, therefore not a clean test) found that an existing oracle-free statistic,
`pmax` (and ioc, pmax_ne, pcon, h2), separates them at AUC ~0.99: a correct decode clears the panel-max bar by
a wide margin, a hallucination only just clears it (it is selected as bar-clearing).

**Pre-registered D5 (frozen before the virgin set is generated):**
* **D5a PMARGIN:** accept iff `pmax >= bar + m`. m is chosen on the TUNING split only (hallucinations H_t vs
  genuine EN_MODERN G_t UNION correct-key EN_NOVOWEL genuine R_t, n=5): the m maximising tuning catch subject to
  tuning false-reject <=0.10 over G_t UNION R_t; ties -> the midpoint of the tied interval.
* **D5b PMARGIN AND fold(k=5,min>=0.90):** same m, conjunction.
* Scoring: (i) the seen held-out split (contaminated for D5, reported as such), and (ii) a **VIRGIN split**
  never examined: key seed `CICADA-I4`, EN_NOVOWEL 200 reps (seed 12000, csd 6000), EN_MODERN 30 reps (13100,
  8800), LATIN/DE/OE/EN_KJV 14 reps each (14500, 9900), all L=240. **The D5 verdict is decided on the virgin
  split only**, with the same criteria as above (>=0.90 catch, <=0.10 FR on EN_MODERN genuine AND <=0.10 FR on
  the pooled register-spread genuine incl. NOVOWEL), Wilson-95 reported. Frozen m is not re-tuned after the
  virgin split is scored. D5 is exploratory-in-origin: the number of designs now inspected is stated in RESULTS.
* Extra stress, same virgin generator, also pre-stated: L=120 variants are NOT run in this lane unless time
  allows; if not run, length dependence of the margin (pmax is length-standardised) goes in not_covered.

---
## ADDENDUM B (written AFTER the virgin-1 result, BEFORE virgin-2 exists)

Virgin-1 result for the pre-registered D5a (m* = 14.76 frozen on tuning): catch 154/157 = 0.981, FR on EN_MODERN
genuine 0/30, but pooled register-spread genuine FR 18/73 = 0.247 (NOVOWEL 3/17, LATIN/DE/OE/EN_KJV 15/56) ->
D5a FAILS the strict criterion (verdict on virgin-1; no re-tuning of D5a). Diagnosis from the margin
distributions: the hallucination margin (pmax-bar) tops out ~15.8; genuine margin is register-specific
(EN ~16-25, DE/KJV ~19-25, LATIN median ~17, **OE median ~13**, NOVOWEL 14-18). A single global m therefore
over-rejects the low-margin genuine registers, whereas the leak itself is register-specific (EN_NOVOWEL argmax).

**D5c PERREG-MARGIN (frozen now):** accept iff `pmax - bar >= m_r`, with `m_r = m_NV` when the argmax register
is EN_NOVOWEL and `m_r = 0` otherwise. m_NV is set on ALL data seen so far (tuning + seen held-out + virgin-1:
EN_NOVOWEL halluc 40+69+157 vs EN_NOVOWEL correct-key genuine 5+8+17) by: maximise catch subject to
EN_NOVOWEL-genuine reject <= 0.05 over those 30 genuine, ties -> midpoint of the tied interval. It is then scored
ONCE on **virgin-2**: key seed `CICADA-I4b`, EN_NOVOWEL 500 reps (seed 22000, csd 16000), EN_MODERN 40 reps
(23100, 18800), LATIN/DE/OE/EN_KJV 20 reps each (24500, 19900), L=240. PASS needs >=0.90 catch, <=0.10 FR on
EN_MODERN genuine, <=0.10 FR on the pooled register-spread genuine. Because D5c is register-conditional, its
claim is scoped to the class actually measured (correct-key EN_NOVOWEL-argmax overfits at L=240, exact preset,
8-register panel); hallucinations whose argmax is another register are UNMEASURED and m_r = 0 gives them no
extra protection -- recorded in not_covered, and SEAL_PASS (if earned) is conditional on that scope.
Count of designs/cells now inspected is reported in RESULTS.md. A Wilson upper bound >0.10 on a 0-reject FR is
reported as "point estimate meets, bound does not".
