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
3. **(C) The information budget is under-determined by ~2.5 × 10⁴ bits** — see §5.

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

_Sections 4 (draw-count-corrected re-scoring of existing best candidates) and 5 (information
budget) follow._
