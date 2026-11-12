# F-rounds-20-24 — fresh-eyes audit notes (reader fork F), 2026-11-12

Scope: liber-primus/analysis/round20..round24 (SYNTHESIS/RESULTS/PREREG read; load-bearing code read:
round19/I1/driftbeam.py + constructions.py (the decoder/plants every R20-24 lane uses), round20/N2 script,
round22/D scripts+features.json, round35 pf_v4.py (skip rule only)). Read-only on the repo. All snippets are in this
directory (f_*.py) and run in seconds unless stated. Paths below are relative to liber-primus/ unless noted.

## A. Ranked findings

### 1. [INSTRUMENT-DEFECT + SHARED-PREMISE] A deletion-type anti-repeat mechanism is invisible to keyskip1 AND keyskip2
- Premise shared by every plant in the repo (analysis/round19/I1/constructions.py:84-246, MECH = keyskip, keyskip_varying,
  free_drift, drift_at, skip_by_two, coin_from_key, jump_at, rewrite): the doublet is avoided by RE-DRAWING the key for the
  SAME plaintext rune, so each skipped key value is "doublet-consistent" with the rune decoded at that position
  (driftbeam.py:141-181: `vmap[k]=(k-sgn_delta)`, `nun = need - cnt[vmap[kacc]]`, `if nun > max_free: continue`).
- Unrepresented sibling: the writer/typesetter simply does not write the 2nd rune of a would-be ciphertext doublet
  (haplography at source). Ciphertext footprint is identical (only the lag-1 hole). Key alignment = one extra key element
  consumed, but the skipped key value is tied to the DELETED plaintext rune, so the skip is "unexplained".
- Measured (f_constructions.py + the L=120/240 x10 run in the transcript; correct key, sha256_ctr pad, supp 0.83, beam_w 400):
    deletion plant L=120: exact  median rec 0.67, >=0.90 in 0/10, median score -5.62
                          pair   median rec 0.42, 0/10, -6.34
                          drift  median rec 0.97, 10/10, -4.25
    deletion plant L=240: exact 0.61 (1/10), pair 0.50 (0/10), drift 0.97 (10/10)
    refs: keyskip plant 1.00/1.00; rewrite plant 0.96-0.98 under both; filterless additive 1.00 under both.
- Why it matters: every mass sweep's stage-B is keyskip1+keyskip2 only (MEASURED-CEILING.md sec 2a conditionals: bash orbits
  "`keyskip1`+`keyskip2` ... (not `free`)", PHP same, Py2.7 `pair` full 2^32 and `exact` 47.95 %). R33-I2-CONSTRUCTION-AXIS lists
  skip_by_k / resets as unrepresented but not deletion. If the mechanism was deletion, the correct seed inside any swept orbit
  would have passed the pf_v4 screen (its Viterbi skips are FREE, round35/I1-skip-tolerant-screen/pf_v4.py:11-40, no consistency
  test) and then been dropped at stage B.
- Not already tracked: grep "haplo|delet" over round19/I1, round24, round32, round33 *.py = no plant; LEDGER A-03/R20-N2 treat
  haplography only as (a) a transcriber merge count and (b) an autokey reopener.
- Discharge: (i) add the 12-line deletion plant to the construction axis (minutes); (ii) re-adjudicate the STORED screen survivors
  (seeds are persisted per R3) under beam_v3 `free` at L=240 with the R37 free null — finite, ~3.5e5 survivor decodes, hours-days CPU;
  no new screening needed. Honest prior: a lossy mechanism is an odd design choice, but so is a soft 0.83 coin; D-01's own
  not_covered says "a person did the writing is untouched".
- Also measured: NULL-INSERTION (a null rune written between the two halves of a would-be doublet) defeats exact AND drift
  (rec 0.05-0.45), but it is EXCLUDED by ciphertext statistics: it would add ~370 A-x-A patterns (lag-2 equality z ~ +17);
  observed lag-2 z = -0.39. So that sibling is closed by measurement, not by decoder.

### 2. [LOGIC-GAP -> weak lead] Round 24's gate killed long-period polyalphabetic keys by an argument the repo had retracted
- analysis/round24/PLAN.md:83-93: C3 (period 400-1500, "the band flat-IoC does NOT exclude") KILLED "by mechanism ... cannot
  produce the 0.66% doublet deficit ... Same wall as every additive lane." But the standing model is additive key + a SEPARATE
  output filter, and README.md:280-283 (Superseded 2026-08-17, R12 D1) retracts exactly this inference: the filter "sets the
  doublet rate, so the deficit has no discriminating power over key type". PRNG streams and pads are "additive lanes" too.
  No ledger row covers "periodic key + filter" (only R12-D2 mentions p*=400 as a number); not in PICKUP-HERE / MEASURED-CEILING
  sec 3 / PARKED / AUDIT-inhibitors (grep "long-period|long period|p\*" = 0 hits).
- Why rigid tests do not close it: under a key-SKIP filter the key index drifts +1 per ~35 runes, so a period-p key returns at
  ciphertext lag h*p - k, k ~ Poisson(lam*h*p). Rigid periodic IoC / all-lag kappa are blind for p >~ 70.
- I built the drift-aware detector (matched filter over all harmonics; f_banded2.py, f_banded3.py, f_banded4.py, f_banded5.py;
  lam = 373.6/12956 = the repo's own R18-L2 drift, fixed in advance; lag 1 excluded):
    power (plants: iid English-unigram plaintext kappa 0.059, random period-p key, keyskip supp 0.83, N=12956):
       p=13: z 11.5 (single harmonic) | p=60: 6-7 | p=150: 4.9-5.2 | p=400: 6.8, 10.9, 15.7 | p=800: 4.4, 5.2, 8.6
       p=1500: 4.1, 6.7, 7.0 | p=3000: 0.6-2.6 (blind) | p=5000: blind
    REAL stream, p in [50,2000]: max z = 3.70 at p=800, 3.59 at p=400 (799: 3.50, 801: 3.35, 399: 3.03); z(200)=2.21,
       z(1200)=1.70, z(1600)=2.18.  Null (200 histogram-preserving shuffles, same grid): median max 2.99, q90 3.54, q95 3.82,
       P(max >= 3.70) = 0.075.  -> NOT a detection.
    consistency looks (post hoc, not independent evidence): z(400) is positive in both halves (1.79, 2.07) and all thirds
       (2.76, 1.02, 1.52); the statistic as a function of the ASSUMED total drift peaks at the a-priori value
       (p=800: 250->0.70, 300->0.75, 340->2.42, 373.6->3.70, 410->2.64, 450->1.31, 500->0.78; p=400 same shape);
       rigid column kappa at p=400/800 is flat (z 1.0 / 0.9) as the drift model predicts.
- Reading: periods <= ~150 under a key-skip filter are now excluded with measured power (extends the rigid "1-40" closure);
  the C3 band is neither excluded nor detected: the family-wise p of 0.075 sits where a whole-text period-800 key with kappa
  0.059 could land (plants 4.4-8.6) and where noise lands 1 time in 13.
- Decisive follow-up (hours, pure Python/numpy, pre-registrable): alignment-EM for fixed p in {400, 800} (HMM over cumulative
  skip count, per-phase key letter estimated from shifted-unigram likelihood or language-free column coincidence); if a period
  exists the aligned column kappa is ~0.059 on ~96k (p=800) to ~200k (p=400) same-phase pairs = z ~ 40-58; null = same EM on
  shuffles. Kill at: EM gain within the shuffle envelope.

### 3. [INSTRUMENT-DEFECT] R22-D's drop-cap catalog is wrong in ~half its identity entries, and the wrong string is in 4 nav docs
- analysis/round22/D-illustration-dropcap/PREREG.md:27-29 and RESULTS.md:13-18 assume "the drop-cap is the first body rune of
  the page" and join image page k to analysis/vision/canonical_pages.json entry k (test_illuminated_runes.py:41-52).
  (a) canonical_pages.json has 57 entries and NO entry for image p50; round19/T1/RESULTS.md:115-118 had already warned "Any lane
      joining canon pages to relikd images past p49 without that shift is off by one." R22-D (run later) did exactly that:
      images 53, 54, 56 were given the first runes of entries 53, 54, 56 (A, NG, P) instead of 52, 53, 55 (EO, A, AE), and
      image 57 (PARABLE, P) was reported "absent from canonical_pages.json".
  (b) Sections/paragraphs often begin MID-page. data/krisyotam_runes.txt carries the marks: `$` (9x) and `&` (18x). Marks inside
      pages: seg3 & after rune 119; seg6 & after 71; seg7 & after 194 (then 14 runes, then & $); seg15 = 9 runes, then & $, then
      the new section; seg33 & after 91; seg38 & after 186; seg39 & after 119. R22-D's own features.json agrees: red centroid
      red_cy = 0.52 on p6, 0.70 on p7 (n_red_blobs 0, aspect None, 30,160 px = just over the 30,000 threshold), 0.58 on p39 —
      not top-of-page drop caps. Pages whose section ENDS there (2, 14, 22, 26, 32, 49, 55) each show ~0.86-1.16k red px
      (an end ornament); pp36-38 (numerals 1-5) show 1.9k / 5.7k / 2.7k.
  Likely true reading (to be confirmed on the images, which are gitignored and absent in this checkout): p0 S, p3 L (+P after &),
  p6 A, p7 = a red 14-rune closing line (starts D), p8 X, p15 L after `$` (+ the 9-rune line FULM AEAYOEA), p23 U, p27 M,
  p33 D (+NG), p39 IA, p40 F, p53 a red paragraph, p54 A, p56 AE, p57 P.  Published: `SLXHXFUMDSFAINGP`
  (ELIMINATION-LEDGER.md:213,457; LEDGER.json:5270; PICKUP-HERE.md:487; handoff/SOLVER-STRATEGY-2026.md:249).
- The Round 22 red-team passed lane D on "4/4 has-cap + page-0 = S" (R-redteam/RESULTS.md:129); the hand control itself read
  p8 as "red Y" and p15 as "red I" (RESULTS.md:24-29) against catalog X and F — X is the Y-shaped rune, but F is not I-shaped
  (L is), a visible warning.
- Why it matters: Round 44 P1 (red ink, top of the queue) inherits this as its only prior catalog; the statistics in R22-D
  (entropy p=0.57) are on a string that is ~50 % wrong. Cost: minutes once images are regenerated.

### 4. [UNDISCHARGED] The self-embedded reads cover 5 of the solved sections; the rest was a named reopener and never run
- R22-A-SELFEMBEDDED-READ, R23-A2-LINE-ACROSTIC, R40-C1-R27/R28 all list "the wider community-solved LP corpus" in
  not_covered/reopens_if. SOLVED-PAGES.json holds 5 pages (A WARNING, SOME WISDOM, KOAN 1, WELCOME, KOAN 2 first page).
  data/scream314_lp.md also carries plaintext for 09.jpg AN INSTRUCTION ("DO FOUR UNREASONABLE THINGS EACH DAY"), 10-13.jpg
  (THE LOSS OF DIVINITY, plain gematria), 15.jpg (KOAN 2 end), 16.jpg (AN INSTRUCTION + the 5x5 square), 73.jpg AN END,
  74.jpg PARABLE. validate.py already reproduces AN END. Not in PICKUP-HERE / PARKED / untried.md (grep "wider|community-solved" = 0).
- Cost: < 1 h (lib_selfread + lib_geom unchanged, add pages). Low prior; it is the cheapest way to finish a hint channel the
  repo calls "read".

### 5. [CONTRADICTION / stale blocker] R20-P1's "short-head ceiling" was refuted by pf_v4, but the row still says no sieve exists
- round20/P1/RESULTS.md:88-99: "A 24-32-rune decrypt head does not carry enough language signal ..." -> INFEASIBLE;
  LEDGER R20-P1-SIEVE-INFEASIBLE result: "S-PERL / S-TEX are DEFERRED ... no affordable sieve exists for them",
  superseded_by = None. MEASURED-CEILING.md sec 1: pf_v4_12 reaches 0.952-0.994 per register on a 24-rune head at FPR 8.9e-4.
  The cause in R20 was the RIGID stage-A (half of true heads contain a skip), not signal content.
- Why it matters: Perl 5.14 rand (2^32, the family with the signed Crypt::RSA prior) and the TeX LCG (2^31) are still "flat
  tails unmeasured" (MEASURED-CEILING sec 3) — now purely a compute item (a C port), not an instrument item. Also the R20-R(b)
  standing condition (refit the null on SCREENED wrong keys) was only met in Round 41; R32-R40 screened sweeps ran against
  unscreened-null bars (already caught by R40-X1/R41-I1; direction conservative).

### 6. [LOGIC-GAP] R24's C4 kill ("any feedback model needs cv~1.0") is narrower than stated; measured the general statement instead
- PLAN.md:95-104. Flat (b-a) diagonals refute only keyless ADDITIVE feedback with unit coefficient; c_i = p_i + 2*c_{i-1} has
  flat diagonals. General test (f_banded.py part 2): "contextual kappa" — positions sharing the same preceding k runes must
  share a key under ANY keyless order-k feedback, so their next runes coincide at plaintext kappa (~0.058). With the filter-aware
  null r0 = 0.03528: order 1: 2,869,214 pairs, 3.537 %, z +0.77 (H1 z ~ 209); order 2: 100,584 pairs, 3.491 %, z -0.65 (H1 ~39);
  order 3: 3,473 pairs, 3.570 %, z +0.13 (H1 ~7). So keyless ciphertext feedback of order <= 3, additive or not, is excluded
  at power — D-04's 3-of-55-page coefficient sweep can be replaced by this row. KEYED feedback (decode the delta stream:
  p = (c_i - c_{i-1}) - k) is not touched by any of this and no sweep decodes delta-C.

### 7. Tail (tidiness / low impact)
- [LOGIC-GAP] round20/N2/RESULTS.md:58-59 lists the plaintext-autokey variant in conditional 1; the script plants only
  ciphertext autokey (n2_haplography_falsifier.py:138). The invariance proof is correct for its scope (re-inserting duplicates
  only changes d=0).
- [LOGIC-GAP] round24/C8-date-indexed-pad/RESULTS.md:75 attributes a failed control to "phantom skips" on filterless ciphertext;
  measured: exact and drift both recover 1.00 on a filterless plant. The control failure had another cause (pad builder / tiling).
- [STALE] round21/SYNTHESIS.md:45-54 (L4 glibc gen=0 full-32, L6 decision) are tracked later (R32-B3; pf_v4) — fine.

## B. Checked and clean
- R20 N2 invariance argument; R20 HITFN guard logic; R21 L2 n_skips crossover (later sweeps do not use n_skips alone; they use
  panel pmax on L=120/240, so the >= 6000-rune rule is respected by not being relied on).
- R22-A / R23-A2 / R22-C / R22-B nulls at their stated scope; R22-R recomputation of B's family-wise correction.
- R24 C2 / C2-EXT controls (pair 100 % on skip_by_two; drift 98.3 %); relations enumerated there = keyskip1, keyskip2 (pair),
  permissive drift (max_free 2, lam 12). Nothing else.
- Same-key "depth" tests (f_depth.py; f_banded.py part 3), language-agnostic: page-aligned L=5..300 z in [0.03, 1.55]
  (power z ~ 12 at L=10 if all pages restarted one key); `$`-section banded z +1.31; `&`-paragraph banded z +0.90; sentence and
  word alignment flat. Line-start alignment shows z +4.0 at L=5 — this is the known R18-L4 width bias (re-derived: column-0
  chi2 78.7, corr with ink width r = +0.77), not a cipher signal.
- Null-insertion mechanism: excluded by flat lag-2 (see finding 1).

## C. Answers to the pointed questions
1. Round 20: the INFEASIBLE verdict is superseded in substance by pf_v4 (R35) but its ledger row is not marked; Perl and TeX
   full spaces were never swept (prior-dense fronts only: R24 C2-EXT 20,487 / 48,836 keys, R26-A); Py2.7 reducers at < 0.1 %;
   Marsaglia lane never-run (tracked). N1 is an archival bound. N2 is a closed-form invariance proof plus a K<=40 adversary —
   a bound on "haplography hides autokey" only; it says nothing about deletion as the doublet mechanism, which no decoder
   relation except drift/free represents (finding 1).
2. Round 21: the leaky seal -> flagged-for-oracle only (still binding). n_skips needs >= ~6000 runes to discriminate alone;
   later sweeps never lean on it.
3. Rounds 22-24 enumerations: A = every-k (k<=40), reversed, diagonals (w<=60) on 5 solved pages; A2 = line/word first/last x
   forward/reverse x per-page/concat (48 reads); B = 72 turtle renders of the CIPHERTEXT value stream + base32/lat-long;
   C = 185 ops (every-4th, iterate x2-4, 4-way interleave, reversal, solved-plaintext running key, prime/index/totient of the
   ciphertext rune as keystream); D = red drop-cap presence/gap/centroid/identity (identity defective). Not enumerated anywhere
   in R22-24: prime/Fibonacci-indexed selections, sentence-level acrostics, k-th-rune-per-line, the other solved sections, and
   ANY use of the unsolved pages' cleartext structure (word-length stream, sentence lengths, the 8 `$` sections and 17 `&`
   paragraphs, title-like first sentences, numerals 1-5 on pp36-38 and "7" on p10) as data or as a key schedule.
4. R24 skip rules: exactly keyskip1, keyskip2, permissive drift.

## D. Reproduce
python3 audit/f_depth.py; f_cols.py; f_banded.py; f_banded3.py (5 min, 200 shuffles; output saved in f_banded3.out);
f_banded4.py; f_banded5.py; (cd liber-primus/analysis/round19/I1 && python3 <scratch>/audit/f_constructions.py)
