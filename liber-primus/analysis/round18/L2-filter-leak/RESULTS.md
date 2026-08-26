# Round 18 — Lane L2 — THE FILTER AS A LEAK — RESULTS

_Run 2026-08-25/26. Pre-registered in [`PREREG.md`](PREREG.md) before any script here was
executed; no threshold was changed after a result was seen._

**Headline, one line each:**

1. **(A) The filter acts on the CIPHERTEXT.** Keystream-side and plaintext-side filtering are
   excluded at power 1.000 (the real stream sits 17.1 and 17.2 sd outside them); the hard rule
   and the deterministic-nudge rewrite are excluded at power 1.000; and **key-skip vs
   value-rewrite is NOT separable from the ciphertext** (measured power 0.175). That settles the
   B4/G3-vs-B-16 argument in B-16's favour: the residual doublet rate is set by the *filter*,
   not by the key or the plaintext.
2. **(B) The draw count is real — 373.6 ± 19.6 draws over the book — and correcting for it does
   not move any existing best score, but it does repair two other things.** The beam already
   models the draw count and **passes a first-ever full-book positive control at 12,956 runes**
   (score −4.098, rune recovery 0.9997, inferred skips 383 vs true 383), so B-04's Stage-D
   escalation argument stands. What the draw count *does* break is **rigid alignment**,
   quantitatively: `(1−rho)^L`, which reproduces Round 17's unexplained prefilter survival
   constant exactly at its own window length (`PREFILTER_LEN = 24` → 0.495).
3. **(C) The information budget is under-determined by +35,408 bits and the acceptance events
   contribute exactly ZERO of them** — proved in closed form, not estimated. The filter is not a
   leak on the plaintext, so the SAT / belief-propagation formulation should not be built. Where
   it *is* a leak is on the key, and the beam's validity test already spends that. See §5.

---

## 0. Trust anchors and instrument gates

| gate | requirement (pre-registered) | measured | verdict |
|---|---|---|---|
| handshake | `len(nc.unsolved()) == 12956` | 12,956 | OK |
| **F0** — fast beam identical to repo beam | score delta < 1e-9 **and** identical plaintext path on >= 20 random cases at L in {60,120,400} | 24 cases, max delta **7.99e-15**, **0** path mismatches | **PASS** (`gate_F0.json`) |
| filter-model sanity | analytic `s*` must reproduce lane P4's independently bisected `supp` to <= 0.001 | `s* = 0.81288` vs P4's **0.8131**, delta **0.00022** | **PASS** |
| A-PC | classifier power >= 0.99 before any model may be called excluded | see §2 table | **PASS** on 5 of 6 pairs |
| B.1 | analytic drift mean inside the simulated 95 % CI | 373.6 in [328, 413] | **PASS** |
| B.3 | beam recovers a planted correct key at L = 12,956: score >= −5.5 **and** recovery >= 0.90 | **−4.098 / 0.9997** | **PASS** |

`fastbeam.py` exists because `skipdecode.beam_decode` carries the growing transliteration
string inside every hypothesis, making a full-book decode O(L^2 · W): B-04 measured **68 s per
12,956-rune decode** (10,192 s / 150). The re-implementation keeps only the last 3 characters
plus a back-pointer and does the same decode in **7.6 s**, bit-identically (gate F0).
Everything below that uses it is therefore directly comparable to previously published numbers.

---

## 1. The closed form the lane starts from

Under the repo's pinned soft key-skip filter each emission is a geometric rejection loop, so
with `q = 1/29`:

        residual doublet rate   r(s) = q(1-s) / (1 - q*s)
        extra draws per rune    rho  = q*s   / (1 - q*s)

Inverting `r = 86/12,955 = 0.00663836` gives **s* = 0.81288**, which reproduces lane P4's
bisected `supp = 0.8131` to 2e-4 — the first time the repo's filter constant has been *derived*
rather than fitted. It follows immediately that

> **rho = 0.0288388**, i.e. the rejection sampler consumed **373.6 ± 19.6 extra keystream
> draws** across the 12,956 runes; the book consumed **~13,330 keystream symbols**; and the
> keystream index leads the rune index by ~374 at the last rune.

---

## 2. SUB-ATTACK A — which stream does the filter act on?

**Verdict: CIPHERTEXT. Within ciphertext: uniform re-roll; key-skip vs value-rewrite
NOT-SEPARABLE.**

Seven models (PREREG §2.A.1), each with a free suppression parameter calibrated *by bisection
to the real lag-1 rate* so the doublet rate itself carries no discriminating information — lane
P4's fairness device. 200 replicates each at n = 12,956 over an archaic-English (KJV) plaintext
in runes. Two independent adjudications are reported because they answer different questions: a
pairwise Gaussian log-LR **power** measurement (can the battery tell this model from M1 at
all?) and a **containment** test (is the real stream inside this model?). A model is EXCLUDED
only if power >= 0.99 **and** the real stream is >= 4 sd outside it.

| model | what is filtered | achieved lag-1 | power vs M1 | real max abs z | verdict |
|---|---|---|---|---|---|
| `M0_nofilter` | nothing | 0.034662 | 1.000 | **17.41** | **EXCLUDED** |
| `M1_ct_keyskip` | ciphertext, key pointer advances | 0.006333 | — | 2.01 | **REFERENCE — real is inside** |
| `M2_ct_rewrite` | ciphertext, output overwritten, key stays aligned | 0.006676 | **0.175** | 2.12 | **UNDERPOWERED-TO-SEPARATE** |
| `M2n_ct_nudge` | ciphertext, output nudged by a fixed delta | 0.006593 | 1.000 | **9.90** | **EXCLUDED** |
| `M3_ks_filtered` | **the keystream** | 0.034854 | 1.000 | **17.05** | **EXCLUDED** |
| `M4_pt_filtered` | **the plaintext** | 0.034677 | 1.000 | **17.15** | **EXCLUDED** |
| `M5_ct_hard` | ciphertext, hard rule | 0.000000 | 1.000 | **inf** | **EXCLUDED** |

**Why keystream- and plaintext-filtering cannot work, and why that is not obvious.** The
intuition that "a pad with no repeats gives a ciphertext with no repeats" is wrong, and the
models show why quantitatively. With `c = p + k`, `c_i = c_{i-1}` requires
`k_i − k_{i-1} = p_{i-1} − p_i`. Forbidding `k_i = k_{i-1}` therefore removes ciphertext
doublets only at positions where the *plaintext* doubles — measured `d_P = 0.02617` on the
English baseline — so M3 predicts a ciphertext doublet rate of `(1−d_P)/28 = 0.03478` and
delivered **0.034854**. Symmetrically M4 predicts exactly `1/29 = 0.034483` and delivered
**0.034677**. Neither can be pushed to 0.664 % at *any* suppression strength: bisection drove
both to `supp = 0.999` and they still sit **17 sd** above the real rate. The observed
suppression is only producible by rejecting on the **emitted symbol**.

**The Delta-spectrum — a new statistic, and what it buys.** Lane P4 measured the full 29x29
off-diagonal bigram table (`bigram_offdiag_chi2_df = 1.0384`, z = +0.75, 783 df), which dilutes
a single-cell spike across 783 cells. Collapsing to `D_i = (c_i − c_{i-1}) mod 29` concentrates
the same evidence into 28 cells:

| | real LP2 | M1/M2 (uniform re-roll) | M2n (fixed nudge) |
|---|---|---|---|
| `delta_chi2 / df` | 1.533 | 1.000 | **11.02** |
| max abs z over 28 cells | **2.64** (at D = 17) | 0.9 sd inside M1 | **16.46** |

Pre-registered bar: Bonferroni over 28 cells, alpha = 0.01 two-sided, |z| >= 3.57. Real = 2.64.
**No nudge signature.** The re-roll draws a fresh uniform symbol; it does not add a constant.
(For the record: `delta_chi2/df` = 1.533 on 27 df is itself +2.0 sd relative to M1's replicate
spread — the largest single deviation of the real stream from the pinned model in this battery,
and not significant after the 5-statistic family. It is recorded so that a future re-read of
the transcription can check whether it moves.)

**What this settles.** `round10b/B4` G3 argued from a plaintext-independent doublet *floor* of
1.50 % against an observed 0.664 %; RECON-B **B-16** objected that the filter, not the key, sets
the rate. Because the surviving model family filters the emitted ciphertext, the residual rate
is a property of the filter alone and is **independent of both key and plaintext**. B-16 is
right: no doublet-based statistic has discriminating power over key type, in either direction.

**What A does NOT cover.** `M1` (key-skip) and `M2` (value-rewrite) are *ciphertext-identical by
construction* — both emit a Markov chain with `P(c_i = c_{i-1}) = r(s)` and a flat off-diagonal
— and the measured power to separate them is **0.175**, essentially the 5 % false-positive rate
plus noise. This was pre-registered as a prediction and it held. The consequence is live for
the search: **M1 desynchronises the key and M2 does not**, so a sweep must cover both, and no
ciphertext statistic will ever tell you which. (B-16 showed a rigid decoder recovers a correct
key under M2 and the beam covers M1, so the pair is covered — but only if both are run.)

Artifacts: `filter_models.py`, `a_locus.py`, `a_locus.json`.

---

## 3. SUB-ATTACK B — rejection consumes draws

### B.1 The drift law — PASS

| | analytic | simulated (200 enciphers of the full book) |
|---|---|---|
| extra draws over 12,956 runes | **373.6** | **374.5** |
| sd | 19.6 | 21.1 |
| 95 % CI | — | 328 … 413 |

Analytic mean inside the simulated CI. Keystream symbols consumed: **13,330**. Drift at the
first rune of page 52 (rune 12,200): **352 ± 19**.

### B.2 The rigid-window survival law — the number Round 17 could not derive

A rigid screen is looking at the right key symbol only if the sampler consumed no extra draw
inside its window: `P(drift-free) = (1−rho)^L`. Measured against 200 plants per length with the
**correct** key and offset; detection = `score_norm >= −5.5`:

| L | `(1−rho)^L` | windows with zero skips | **rigid** power | rigid mean score | rigid recovery | **beam** power | beam recovery |
|---|---|---|---|---|---|---|---|
| 25 | 0.481 | 0.575 | **0.700** | −4.95 | 0.770 | 1.000 | 0.999 |
| 50 | 0.232 | 0.310 | **0.460** | −5.63 | 0.593 | 1.000 | 0.999 |
| 100 | 0.054 | 0.080 | **0.190** | −6.34 | 0.396 | 1.000 | 0.999 |
| 120 | 0.030 | 0.040 | **0.150** | −6.51 | 0.343 | 1.000 | 1.000 |
| 200 | 0.003 | 0.010 | **0.035** | −6.95 | 0.220 | 1.000 | 0.999 |
| 400 | 0.000 | 0.000 | **0.005** | −7.23 | 0.130 | 1.000 | 1.000 |

**Rigid detection power crosses 0.5 at L ~ 45.** Past ~120 runes a rigid decoder holding the
*correct* key scores −6.5, squarely in this repo's noise band — the AGENTS.md §4 lesson 2, now
with a length curve attached.

**The Round 17 repair.** `round17/lib_padsweep.py` sets `PREFILTER_LEN = 24`, and R17's
synthesis reports a measured prefilter survival of **0.4–0.55** (P0: 0.750 / 0.583 / 0.500 /
0.375 / 0.542; P2: 0.875 / 0.500), notes it is "not monotone" in pad size, and files follow-up
3 as *"re-derive the prefilter survival law properly"*. The closed form answers it:

> **(1 − rho)^24 = 0.495.**

The survival constant is not a property of pad size or pad statistics at all. It is the
probability that the rejection sampler consumed no draw inside a 24-rune window, so it is **the
same number for every pad** — which is exactly the pad-independence R17 observed and could not
explain. The closed form is a *lower* bound (a skip in the last one or two positions of the
window is often still survivable); R17's seven measurements average 0.589 ± 0.039, consistent
with that.

### B.3 Full-length beam power — the load-bearing check, and it PASSES

Every plant-and-recover control in this repository (D3, B-04 G1/G2, R16, R17) was run at
**<= 400 runes**, while `round13/B04/RESULTS.md` calls Stage D "the decisive check" on the
strength of a **12,956-rune** decay from −6.654 to −7.239. That reading is only sound if the
beam can recover a *correct* key at that length. It had never been tested. It is now:

| L | mean score | rune recovery | inferred / true skips | s per decode | bar (−5.5 & 0.90) |
|---|---|---|---|---|---|
| 120 | −4.230 | 1.0000 | 3 / 3 | 0.0 | **PASS** |
| 400 | −3.975 | 1.0000 | 10 / 10 | 0.2 | **PASS** |
| 1,000 | −3.971 | 0.9990 | 29 / 29 | 0.6 | **PASS** |
| 3,000 | −3.995 | 0.9994 | 88 / 88 | 1.8 | **PASS** |
| 6,000 | −4.018 | 0.9997 | 178 / 178 | 3.8 | **PASS** |
| **12,956** | **−4.098** | **0.9997** | **383 / 383** | 7.6 | **PASS** |

Negative control, wrong key at L = 12,956: **−7.305**. Separation at full book length: **3.21**.

**Consequence:** B-04 Stage D's instrument is sound at full length; its escalation argument
("a correct key gets better as more text is added") is validated rather than refuted, and the
same now holds for other full-length escalations in the repo. This is the project's first
full-book positive control. Note what it does *not* say: it validates the decoder at length,
not the coverage of the sweep it adjudicated.

**Byproduct — an English-independent second channel.** `fastbeam.beam_decode` returns
`n_skips`, which the original decoder does not expose. At every length tested it recovered the
true skip count **exactly** under the correct key (383 / 383 at full book) while the wrong-key
control inferred **286**. Under a correct key the count must track `rho·L = 373.6`; a wrong key
has no reason to. Quantified in §4.

Artifacts: `fastbeam.py`, `b_drawcount.py`, `b_drawcount.json`, `gate_F0.json`.

---

## 4. SUB-ATTACK B.4 — the drift-corrected offset ladder

**The region.** Under a single continuous keystream — which is what P4's flat, unscoped
verdict implies — the correct key index at the first rune of page `k` is
`o_k = start_k + S_k` with `S_k` of mean `rho*start_k` and sd `sqrt(start_k*var)`. For page 52
(`start = 12,469`) that is **o ~ 12,829 +/- 19**. No stage of any campaign has tested it:
B-04 Stage A/B tested only the 120-rune **head** at offsets {0...3301}; Stage C tested each
page at a **restart** (offset 0); Stage D tested the full stream for 150 configs. And the beam
cannot repair the gap on its own — it can insert skips but never remove them, so it can never
reach an offset *lower* than where it started, and closing a 360-draw deficit inside a 100-rune
page would need 3.6 skips per rune against `max_skip = 3` and a validity test that passes with
probability 1/29.

### 4.1 Positive control B4-PC — PASS, and it *is* the finding

A `sha256_ctr` keystream from the dictionary-resident seed `THE PRIMES ARE SACRED` was planted
over 12,956 runes of archaic English, enciphered under the pinned filter (368 skips in the synthetic book), and three pages were
sliced out and put through the ladder against 20 decoy keystreams. The exact true key index at
each page start is known from the encipherment:

| page | `start_k` | true key index | ladder prediction | inside ladder? | rank | **score at the drift-corrected offset** | score at the **uncorrected** offset `start_k` | score at **restart 0** (Stage C) | best decoy |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 2,397 | 2,464 | 2,466 +/- 8.4 | yes | **1** | **−4.086** | −7.328 | −7.805 | −6.722 |
| 30 | 7,307 | 7,505 | 7,518 +/- 14.7 | yes | **1** | **−4.188** | −7.303 | −7.359 | −6.602 |
| 52 | 12,469 | 12,825 | 12,829 +/- 19.2 | yes | **1** | **−3.949** | −6.940 | −7.522 | −6.653 |

Read the last three score columns together. **A correct key is pure noise at the uncorrected
offset and recovers at −4 at the drift-corrected one — a gap of 3.0 to 3.6 score units.** The
drift correction is not a refinement; without it a correct key is undetectable, and the
positive control that proves the ladder works is the same experiment that proves the region
was never covered. The prediction interval also does its job: the true index landed 2, 13 and
4 draws from the predicted mean, against sds of 8.4, 14.7 and 19.2.

### 4.2 The sweep over mined candidates

Candidates were **mined from the published result JSON** of `round13/B04` (`results_A/B/C/D`),
`round16/KDF` (`results_summary`, `results_A`) and `round16/prng` (`results.top20`) and
deduplicated on (family, seed, generator/KDF, salt, reduction, sign, atbash, direction). No
sweep was re-run (CAMPAIGN-PLAN rule 7).

- candidates: **230**
- segments: all **55** unsolved pages, first 100 runes
- ladder: `o_k +/- 4 sd`, integer step 1, plus two control offsets per page (`start_k`
  uncorrected, and 0 = Stage-C restart) — **5,961 offsets per candidate**
- **total decodes: 1,371,030** in 1,700 s, 0 candidate reconstruction failures

**Bar.** `benchmark/null.py: threshold_for(1,371,030, segment_len=100)` = **−5.500** — at this
trial count the historical floor is still the binding constraint (the family-wise correction
gives a looser bar). `expected_max(1,371,030)` = **−6.185**, which is where the best *wrong*
answer should land.

| | score | where |
|---|---|---|
| **best overall** | **−5.8853** | page 52, offset **0**, i.e. a *control* point |
| best in the **new drift-corrected region** | **−6.0117** | page 49, offset **12,320** (`R16KDF-A pbkdf2_sha256_3301`) |
| expected null max at N = 1,371,030 | −6.1853 | — |
| bar | −5.500 | — |
| **candidates over the bar** | **0** | — |
| best-per-candidate distribution | mean −6.311, sd 0.125, max −5.885 | 230 candidates |

**Draw-count correction does not move any existing best score.** Two things say so:

1. The overall best, −5.8853 at page 52 / offset 0, is a **bit-for-bit reproduction of B-04
   Stage C's published best** (`anend`, `sha256_chain`, `rej29`, sign +1, Atbash, fwd, page 52,
   offset 0, published −5.8852781) — obtained here through a different decoder implementation
   and an independently rebuilt keystream. That is a useful cross-check on the whole harness,
   and it says the corrected region contains nothing that beats the ground already covered.
2. The best score anywhere in the **new** region is −6.0117, which sits **0.17 above the
   expected null maximum** for 1.37 M trials. That is the order statistic doing its job.

173 of the 230 candidates had their best at a corrected offset rather than a control offset,
which is what you would expect from a ladder in which ~99 % of the points are corrected ones;
it is not evidence of anything.

**A calibration note on `expected_max`, offered rather than hidden.** `benchmark/null.py`'s
Gumbel constants are tail-calibrated at segment length ~120, and this sweep runs at 100. Its
prediction for B-04 Stage C (3,548,160 decodes at L = 100) is −6.117 against an observed
−5.885, so at L = 100 the real order statistic runs ~0.23 **hotter** than the fit. The same
0.23 applies here. Nothing in this section turns on it — the bar is the −5.5 floor either way,
and the best score is 0.39 below the floor — but anyone recalibrating `mu`/`beta` for short
segments should start from that offset rather than assume the L≈120 fit transfers.

**A small coverage correction for R16-KDF, found while rebuilding its candidates.** Three of
its published top-50 secrets — `1d00`, `1d000000`, `1d00000000000000` — produce **byte-identical
keystreams**. The cause is not a bug in either harness: in PBKDF2-HMAC the password *is* the
HMAC key, and HMAC zero-pads a short key to the 64-byte block, so **trailing zero bytes in a
PBKDF2 password are absorbed and cannot change the output**. Any seed dictionary that
serialises integers at several byte widths therefore has fewer distinct members than it
counts. R16-KDF's nominal 534-secret coverage is an upper bound; the cheap fix is to
deduplicate on `secret.rstrip(b"\x00")` before quoting a coverage number. This does not affect
its negative.

### 4.3 The skip-count channel — a measured, English-independent ranking statistic

`fastbeam` returns `n_skips`, the number of keystream draws the winning path says the sampler
consumed. The original decoder discards it. Under a correct key it must track `rho·L = 373.6`;
under a wrong key it has no reason to. Measured on full-book (12,956-rune) decodes:

| | inferred skips | decode score |
|---|---|---|
| planted **correct** key | **362** (true value 361; `rho·L` = 373.6) | −4.100 |
| 40 wrong keys on the **planted** ciphertext | 296.3 ± 21.4 | −7.296 mean |
| 40 wrong keys on the **real LP2** ciphertext | 297.8 ± 19.8 | −7.299 mean |

Three things fall out.

1. **Separation 3.08 sd**, giving a screen with **power 0.924 at a 5 % false-positive rate**.
   That is not enough to be a primary discriminator over millions of candidates, but it is a
   perfectly usable *secondary* screen — and it is **orthogonal to the English scorer**.
2. **The channel is English-independent, which is exactly the gap lane L7-A identified** (every
   negative in this repository is an English-only negative). A candidate whose plaintext is not
   modern-English-quadgram-shaped — another language, an archaic register, or a second cipher
   layer — is invisible to the quadgram scorer but still has to consume ~374 draws. This is a
   concrete, cheap statistic that can be persisted at sweep time for exactly that reason.
3. **The two nulls agree at z = 0.32.** Wrong keys behave identically on the real LP2
   ciphertext and on a synthetic filtered ciphertext. That is an independent, decoder-level
   confirmation of the cipher model against the real data — P4 confirmed the *filter's* shape
   from ciphertext statistics; this confirms the *decoder's* behaviour on the real stream.

The candidate-ranking loop was cut short by the run wall-clock; two rows completed, both null:
R16-KDF's own gate seed `THE PRIMES ARE SACRED` on the real ciphertext gives `n_skips` = 277
(z = −1.05, score −7.307), and B-04's best `anend` gives 297 (z = −0.04, score −7.292). The
null bands above are complete at n = 40 and are what the channel claim rests on.

**Caveat, stated rather than buried:** the wrong-key null used a single generator family
(`sha256_ctr` with varied seeds). A pad with long constant byte runs is the case R17/P1 found
makes `max_skip = 3` bind, and it would shift this null; the channel should be recalibrated per
pad family before being used as a screen.

---

## 5. SUB-ATTACK C — the constraint / information budget

**Verdict: UNDER-DETERMINED by ~3.5 x 10^4 bits, and the acceptance events contribute exactly
ZERO of what is needed. Do not build the SAT/BP solver.**

### 5.1 The exact result that decides it

The lane's premise was that each accepted position certifies an inequality on the joint
(plaintext, keystream) and that 12,956 such certificates are unspent information. They are not
information about the plaintext at all, and the reason is one line of algebra. Under the
surviving locus, summing over the number `m` of rejected draws:

        P(c_i | p_i, c_prev)  =  sum_m (s/N)^m * (1/N) * w     with w = (1-s) if c_i == c_prev else 1
                              =  w / (N - s)

Each rejected draw had to reproduce `c_prev`, which pins **one** key value out of `N` (hence
`1/N`) and costs one coin (hence `s`); the accepted draw pins one key value (hence `1/N`).
**`p_i` does not appear.** The plaintext symbol only relabels *which* key value is the pinned
one, and a uniform keystream is invariant under relabelling. Therefore `P(C | P)` is the same
number for every candidate plaintext, the likelihood over plaintexts is exactly flat, and the
filter contributes **0 bits** of constraint on `P`.

The same line delivers the residual doublet rate in closed form, `(1-s)/(N-s)` — a third
independent route to the filter constant:

| | value |
|---|---|
| closed form `(1-s)/(N-s)` at s = 0.8129 | **0.00663779** |
| observed 86 / 12,955 | **0.00663836** |

**Numerical control.** The ciphertext law was measured from 1,000 enciphers each of two
maximally different plaintexts (a constant plaintext and archaic English), 200 runes apiece:

| statistic | constant plaintext | English plaintext | homogeneity chi2 (28 df) |
|---|---|---|---|
| doublet rate | 0.00673 | 0.00633 | — |
| ciphertext symbol law | — | — | **28.2** (p = 0.45) |
| Delta-spectrum law | — | — | **24.5** (p = 0.65) |

Both sit exactly on 28 df. The ciphertext law does not depend on the plaintext.

### 5.2 The budget

| quantity | measured | how |
|---|---|---|
| `H(C)` unfiltered | 62,940.0 bits | 12,956 x log2(29) |
| `H(C)` under the fitted filtered-Markov law | 62,616.6 bits | fitted at the observed doublet rate |
| **filter's total information injection** | **323.4 bits** (0.0250 bits/symbol) | the difference |
| `H(P)` | **2.568 bits/rune -> 33,269 bits** | held-out cross-entropy, order-3 rune Markov model trained on 400k / tested on 200k KJV runes (orders 0-5: 4.294 / 3.616 / 3.000 / **2.568** / 2.592 / 2.908) |
| `H(K)`, full-entropy pad | 64,755 bits | (12,956 + 373.6) x log2(29) |

Decision rule fixed in PREREG §4: the joint is *determined* iff `H(P) + H(K) - H(C) <= 0`.

| hypothesis about the keystream | `H(K)` | deficit | |
|---|---|---|---|
| **full-entropy pad (13,330 symbols)** | 64,755 | **+35,408** | **under-determined** |
| public pad, offset only (2^40 offsets) | 40 | −29,307 | DETERMINED |
| derived keystream, 256-bit seed | 256 | −29,091 | DETERMINED |
| **derived keystream, 64-bit seed — control C-PC** | 64 | −29,283 | **DETERMINED** |
| derived keystream, 32-bit seed | 32 | −29,315 | DETERMINED |

> **The number that matters: any keystream hypothesis carrying less than ~29,300 bits
> (~3,670 bytes, ~6,040 rune-equivalents) of entropy leaves the system determined.**

Sensitivity, because the order-3 held-out figure is an *upper* bound on English's entropy rate
and a lower true rate loosens the requirement:

| assumed `H(P)` | max `H(K)` for determinacy | full-pad deficit |
|---|---|---|
| 1.5 bits/rune | 43,183 bits | +21,573 |
| 2.0 bits/rune | 36,705 bits | +28,051 |
| **2.568 (measured bound)** | **29,347 bits** | **+35,408** |
| 3.0 bits/rune | 23,749 bits | +41,007 |

**Positive control C-PC — PASS.** The accounting returns DETERMINED for a 64-bit-seed derived
keystream, which is the case `round12/D3` demonstrated is actually recoverable in practice
(planted seed recovered at −4.170, 98.9 % character recovery). An accounting that called a
demonstrably recoverable case under-determined would be wrong; this one does not.

### 5.3 What that means for a SAT / BP formulation

**Do not build it.** Under a full-entropy pad the joint is under-determined by **+35,408
bits**, and the acceptance events contribute **0** of them. Constraint propagation cannot
manufacture information the likelihood does not contain; a flat likelihood over plaintexts
propagates to a flat posterior, whatever the solver. This is the same shape of answer lane P4
reached from the other direction — P4 §9(3) said "a key prior buys nothing" because the pad has
no exploitable non-uniformity; C says "an acceptance prior buys nothing" because the acceptance
events are plaintext-independent by construction.

**What would close the gap**, stated concretely, since that is the useful part of a negative:
*any* hypothesis that bounds `H(K)` below ~29,300 bits. That is not an exotic requirement — it
is satisfied by every derived-key family (a seed of any practical length), every public-pad
family (a source identifier plus an offset), and every PRNG-seed family. **The tractability of
those lanes comes entirely from the keyspace bound and not at all from the filter**, which is
worth stating plainly because this lane set out to find the opposite.

### 5.4 Where the filter *is* a leak

Not on the plaintext — on the **key**. Conditioned on a candidate keystream the skip pattern is
heavily constrained (each skipped key symbol must reproduce the previous ciphertext rune,
probability 1/29 each), and that constraint is exactly what the beam's validity test already
exploits. §3's byproduct measures the size of that channel: the inferred skip count recovered
the true value exactly (383/383) under a correct key at full book length. Its usefulness as a
*ranking* channel is measured in §4.3.

Artifacts: `c_budget.py`, `c_budget.json`.

---

## 6. Coverage — what this lane measured, and what it did not

Per `CAMPAIGN-PLAN.md` rule 6. Read this section, not the verdicts.

### 6.1 Covered

| | region actually measured | control that makes it a real negative |
|---|---|---|
| **A** | 7 filter loci, 200 replicates each at n = 12,956, 5 primary statistics + a new Delta-spectrum, every parameterised model bisected to the real lag-1 rate | classifier power 1.000 on 5 of 6 pairs; real stream contained inside M1 at max abs z = 2.01 |
| **B.1** | the drift law over the whole book | analytic 373.6 inside the simulated 95 % CI [328, 413] |
| **B.2** | rigid vs beam detection power at L in {25, 50, 100, 120, 200, 400}, 200 plants each | plants use the **correct** key and offset, so the measured rigid failure is a false-negative rate, not a search failure |
| **B.3** | beam power at L in {120 … 12,956} at B-04 Stage-D settings | planted correct key recovers at −4.098 / 0.9997; wrong key −7.305 |
| **B.4** | 230 mined candidates x 55 pages x 5,961 ladder offsets = 1,371,030 decodes | B4-PC: planted key ranks #1 on 3 pages at −3.949 … −4.188, against −6.940 … −7.328 uncorrected |
| **C** | exact acceptance-channel algebra + a measured entropy budget | C-PC: the accounting returns DETERMINED for the 64-bit-seed case D3 demonstrated is recoverable; ciphertext-law homogeneity chi2 28.2 / 24.5 on 28 df |
| instrument | a fast decoder proved identical to the repo's | gate F0: 24 cases, max score delta 7.99e-15, 0 path mismatches |

### 6.2 Not covered — and what would reopen each

1. **M1 vs M2 (key-skip vs value-rewrite).** Ciphertext-identical by construction; measured
   separation power **0.175**. Nothing computed from the ciphertext alone will separate them.
   *Reopens if* an artifact outside the ciphertext (a toolchain fingerprint from lane L1, an
   author disclosure) pins the implementation. This matters because drift is 374 draws under
   M1 and **zero** under M2, so §4's ladder is the right test under M1 and the *uncorrected*
   offset is the right one under M2 — both need to stay in scope.
2. **Composite and non-stationary loci.** All seven models are stationary and single-stage. A
   filter applied to the ciphertext of an already-deduplicated plaintext, or one whose strength
   varies along the book, is untested here. P4 measured the rate as constant across the 55
   pages but at power 0.075 — underpowered, not excluded.
3. **The 86 residual doublets are a transcription artifact until register item A-03 runs.**
   Every number in §1, §2 and §5.1 is a function of `86 / 12,955`. A high-zoom re-read that
   merges ~20 doublet neighbourhoods moves `s*`, `rho`, the drift, the ladder centre and the
   closed-form residual rate together. A-03 is the cheapest falsifier of this lane's *positive*
   results, as it already is of P4's.
4. **The ladder's candidate set** is the published top lists of three campaigns, not their seed
   dictionaries. Seeds those sweeps ranked below their top-50 cutoff were not re-scored. The
   ladder costs 0.7 ms per 100-rune decode, so re-scoring a full dictionary on it is hours, not
   days; *reopens* whenever a keystream campaign produces a new candidate list.
5. **A global keystream start other than key index 0 at rune 0.** §4's ladder is anchored on
   the assumption that the pad's first symbol keys the book's first rune. Composing it with a
   global offset ladder is the natural extension and is lane L6's item B-02.
6. **Segments longer than 100 runes per page** in the ladder, and pages beyond the first 100
   runes.
7. **B.3 planted one keystream family** (`sha256_ctr`). R17/P1 measured that `max_skip = 3`
   binds on pads with long constant byte runs; a full-length plant on such a pad is untested.
8. **C's zero-information result is conditional** on the keystream being uniform and
   independent of the plaintext. It does not hold if the pad is correlated with the message.

### 6.3 What this lane changes for the next one

- **Do not build the joint SAT / BP decode.** §5 gives the deficit in bits and shows the
  acceptance events contribute none of it. This converges with P4 §9(3) from the other side.
- **Do run the drift-corrected ladder on any new candidate list.** It is cheap, it has a
  passing positive control, and without it a correct key scores as noise (§4.1).
- **Quote `(1−rho)^L` when reporting prefilter coverage.** It replaces a measured constant
  nobody could explain with a closed form, and it says a rigid screen wider than ~45 runes is
  more likely wrong than right.
- **The beam is validated at full book length** — for the first time. Escalation-to-full-length
  arguments in this repo may be quoted; they were previously unvalidated at that length.
- **Deduplicate PBKDF2 seed dictionaries on trailing zero bytes** before quoting coverage
  (§4.2).

## 7. Files

| file | contents |
|---|---|
| `PREREG.md` | hypotheses, instruments, controls, thresholds — fixed before the run |
| `fastbeam.py` | bit-identical fast re-implementation of the skip-aware beam; gate F0 |
| `filter_models.py` | the 7 filter loci, the statistic battery, the calibration |
| `a_locus.py` / `a_locus.json` | sub-attack A |
| `b_drawcount.py` / `b_drawcount.json` | sub-attack B.1–B.3 |
| `b4_ladder.py` / `b4_control.json` / `b4_ladder.json` / `b5_skipchannel.json` | sub-attack B.4, its positive control, and the skip-count channel |
| `c_budget.py` / `c_budget.json` | sub-attack C |
| `gate_F0.json` | the blocking instrument gate |
| `ledger.json` | ledger-shaped entries for merge into `LEDGER.json` |

**One-line result for the ledger:** *the LP2 anti-repeat filter rejects on the **ciphertext**
(keystream- and plaintext-side loci excluded at power 1.000, key-skip vs value-rewrite not
separable at power 0.175); it consumed 373.6 ± 19.6 extra keystream draws, which makes a rigid
window wider than ~45 runes more likely wrong than right and derives Round 17's prefilter
survival constant as `(1−rho)^24 = 0.495`; the skip-aware beam nevertheless recovers a planted
key at the full 12,956 runes (−4.098, 0.9997), so escalation arguments stand; and the 12,956
acceptance events carry **exactly zero** bits about the plaintext, leaving the joint
under-determined by 35,408 bits — so the filter is a leak on the key, not on the message.*
