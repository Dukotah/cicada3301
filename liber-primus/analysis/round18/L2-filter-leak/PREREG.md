# Round 18 — Lane L2 — THE FILTER AS A LEAK — PRE-REGISTRATION

_Written 2026-08-25 **before any script in this directory was executed.** Nothing below was
edited after a result was seen. Amendments, if any, are appended at the bottom with a
timestamp and marked as amendments._

---

## 0. The reframe

Every campaign in this repository has treated the anti-repeat filter as an **obstacle** —
the thing that desynchronises key from ciphertext and forces a skip-aware beam
(`AGENTS.md` section 4, lesson 2). Round 17 lane P4 established at power 1.000 that it is a
**flat, unscoped, purely lag-1 machine filter** at `supp ~ 0.813`
(`round17/P4_filter/RESULTS.md`). A machine filter of that shape is a **rejection sampler**.
This lane asks the three questions that follow from that and have never been asked here:

- **(A)** On *which stream* does the sampler reject — ciphertext, keystream, or plaintext?
  These are not equivalent and they make different, testable predictions.
- **(B)** Rejection **consumes draws**, so the keystream index is not the rune index. How
  much drift accumulates, which measured results depend on getting that alignment right,
  and does correcting it change any existing best score?
- **(C)** Every accepted position is a certificate that the sampler did not have to
  re-roll. How many **bits** do 12,956 such certificates carry, versus how many bits the
  unknown (plaintext + keystream) needs?

## 1. Data, instruments, and the handshake

- Target: `round11/lib_numchannel.unsolved()` — LP2 pages 0-54, **12,956 runes**, mod 29.
  Any script here that does not see 12,956 aborts.
- Structure (page / line / position per rune): `round17/P4_filter/fingerprint.load_structure()`,
  which itself asserts stream identity against `nc.unsolved()`.
- Decoder: the repo's skip-aware beam, `campaign18_skip/skipdecode.beam_decode`
  (`AGENTS.md` section 4, lesson 2 — **no rigid decoder may adjudicate anything on LP2**).
  Where a faster re-implementation is used it must first be proved **numerically identical**
  to `sk.beam_decode` (gate F0 below) or it may not be used.
- Encipher model: `skipdecode.encipher_keyskip` — the repo's pinned soft key-skip filter.
- Scoring: `lp.score.Quadgram.score_norm` on the **transliteration of rune indices**
  (`AGENTS.md` section 4, fourth lesson).
- Thresholds: `benchmark/null.py: threshold_for(n_trials, segment_len)`. The historical
  fixed -5.5 bar may be *reported* but may not be the sole bar for any sweep with
  N > 10^4 (`CAMPAIGN-PLAN.md` rule 4).
- Ledger consulted before designing: `LEDGER.json` entries `VERDICT-OTP-CLASS`, `B-04`,
  `B-16`, `D-01`, `A-03`, `R17-PUBLIC-PAD`, `E-02`, read on `coverage` / `not_covered`,
  not on `status` (rule 7).

**Fixed constants derived analytically before the run** (they are predictions, not fits):

Let `q = 1/29 = 0.0344828` and `s` = the suppression probability. Under
`encipher_keyskip`'s geometric retry the residual doublet rate is

        r(s) = q(1-s) / (1 - q*s)

Setting `r = 0.00663836` (the real stream, 86 / 12,955) gives **s* = 0.8129**, which must
reproduce lane P4's independently bisected `supp = 0.8131` to <= 0.001 or this lane's model
of the filter is wrong and everything below is void. Under the same model the expected
number of **consumed extra draws per emitted rune** is

        rho = q*s / (1 - q*s)  = 0.028839

predicting **373.7 extra draws over 12,956 runes**, i.e. the keystream index leads the rune
index by ~374 at the end of the book.

---

## 2. Sub-attack A — WHICH STREAM DOES THE FILTER ACT ON?

### A.1 The models (fixed here, in full)

With decode relation `p = (c + sign*k) mod 29`, i.e. `c = (p - sign*k) mod 29`:

| id | name | rejection test | on reject | key index | prediction for the ciphertext lag-1 rate |
|---|---|---|---|---|---|
| **M0** | no filter | — | — | `j = i` | `q` = 3.448 % |
| **M1** | **ciphertext key-skip** (repo pinned) | `c_i == c_{i-1}` | advance key, redraw | `j = i + S_i` | `r(s)`, tunable to 0.664 % |
| **M2** | **ciphertext value-rewrite** | `c_i == c_{i-1}` | overwrite `c_i` with a fresh uniform draw; key **stays aligned** | `j = i` | `q(1-s) + q^2 s`, tunable to 0.664 % |
| **M2n** | ciphertext deterministic nudge | `c_i == c_{i-1}` | `c_i <- c_i + d` for fixed `d` in {1,-1} | `j = i` | tunable, **but skews the delta-spectrum** |
| **M3** | **keystream-filtered** | `k_j == k_{j-1}` at generation | resample `k` | `j = i` | `(1 - d_P)/28` ~ 3.4 % — *cannot reach 0.664 %* |
| **M4** | **plaintext-filtered** | `p_i == p_{i-1}` | resample/drop `p` | `j = i` | exactly `q` = 3.448 % — *cannot reach 0.664 %* |
| **M5** | hard ciphertext filter | `c_i == c_{i-1}` | redraw until different | `j = i + S_i` | 0 % |

`d_P` = plaintext doublet rate; measured on the repo's English baseline, not assumed.

### A.2 Statistic battery (fixed before the run)

1. `lag1_rate` — the residual doublet rate.
2. **`delta_spectrum`** — the histogram of `D_i = (c_i - c_{i-1}) mod 29` over the 28 cells
   `D != 0`, as a chi-square(27) of uniformity, plus `max_abs_delta_z` over the 28 cells.
   *This is a new statistic in this repo:* lane P4 measured the full 29x29 off-diagonal
   bigram table (chi2/df 1.0384, 783 df), which spreads the power of a single-cell spike
   over 783 cells. The delta-spectrum concentrates it into 28. It is the statistic that
   separates **M1/M2** (uniform redraw => flat) from **M2n** (deterministic nudge => a
   spike of ~ `q*s` excess mass at one D).
3. `run3`, `abab_z` — from P4's battery, re-measured here for the new models.
4. `bleed28_z` — P4's lag-2..8 pooled bleed, as a cross-check that the models under test
   reproduce it.

### A.3 Thresholds and decision rules

- **Gate A-PC (mandatory positive control).** Generate 200 replicates of each model at
  n = 12,956 and adjudicate each replicate with a Gaussian log-LR classifier built from the
  models' replicate distributions. The lane may only claim a model is *excluded* if the
  classifier's **power to detect that model at a 5 % false-positive rate against M1 is
  >= 0.99**. Any pair below 0.80 power is reported **UNDERPOWERED-TO-SEPARATE** and neither
  member may be excluded.
- **Free-parameter fairness.** Every model with a suppression parameter is calibrated by
  bisection to the **real** lag-1 rate, exactly as P4 did, so `lag1_rate` carries no
  information for those models and cannot do the discriminating by itself.
- **Delta-spectrum bar.** Bonferroni over 28 cells at alpha = 0.01 two-sided => **|z| >= 3.57**.
  A cell above that on the real stream is declared a nudge signature.
- **Pre-registered prediction, recorded so it can be wrong:** M3 and M4 are excluded on
  `lag1_rate` alone with power 1.000; M2n is excluded by the delta-spectrum; **M1 and M2 are
  NOT separable by any ciphertext-only statistic** and the measured power for that pair will
  come out at ~ alpha = 0.05. If M1/M2 separate, that is a finding and this prediction was
  wrong.
- **Verdict labels:** CIPHERTEXT / KEYSTREAM / PLAINTEXT / AMBIGUOUS, plus, within
  CIPHERTEXT, SKIP / REWRITE / NOT-SEPARABLE.

### A.4 The repo tension this settles

`round10b/B4` G3 says the plaintext-independent doublet floor is 1.50 % > observed 0.664 %;
RECON-B **B-16** objects that the filter, not the key, sets the rate. A.1's table decides
it: under M1/M2 the rate is a property of the *filter* and is independent of both key and
plaintext; under M3/M4 it is a property of the *key* or *plaintext*. Whichever model
survives A.3 settles the argument, and the answer is recorded either way.

---

## 3. Sub-attack B — REJECTION CONSUMES DRAWS

### B.1 The drift law
Predict `E[S] = 373.7` and derive `sd[S]` analytically; verify against 200 simulated
enciphers of 12,956 English runes under the pinned filter. **Pass** if the analytic mean
lies inside the simulated 95 % interval. If it does not, the drift model is wrong and
B.2-B.4 are void.

### B.2 Where alignment was assumed — the rigid-window survival law
A rigid decode of a window of length `L` is correct only if the sampler consumed **no**
extra draw inside it: `P = (1-rho)^L`. Measure, by plant-and-recover at 200 plants per
length, the **detection power of a rigid decode** and of the **beam** at
`L in {25, 50, 100, 120, 200, 400}`, and report the `L` at which rigid power falls below 0.5.
This is a coverage correction for every prefilter / rigid screen in the repo, R17's
`lib_padsweep.dense_scan` included, whose survival discount was measured at 0.4-0.55 but
never derived (`round17/SYNTHESIS.md`, follow-up 3). No pass/fail; it is a measurement.

### B.3 Full-length beam power — the load-bearing check
`round13/B04/RESULTS.md` calls Stage D "the decisive check": 150 survivors escalated to the
full 12,956 runes, best decayed -6.654 -> -7.239, read as *"a correct key gets better as
more text is added; a lucky one decays."* **That reading is only valid if the beam can
recover a correct key at 12,956 runes.** Every plant-and-recover control in this repo
(D3, B-04 G1/G2, R16, R17) was run at **<= 400 runes**. The beam is width-limited
(`beam_w=400`) and ranks partial paths on a **raw cumulative quadgram sum** over
transliterations of *unequal character length*, so a longer decode gives a length-selection
bias more room to displace the true path.

- **Instrument gate F0 (mandatory, blocking).** A fast re-implementation of `beam_decode`
  must reproduce `sk.beam_decode`'s returned `score` to < 1e-9 on **>= 20** independent
  random (ciphertext, keystream) pairs at L in {60, 120, 400}, and its recovered plaintext
  index vector must match exactly. If F0 fails, the fast decoder is not used and B.3/B.4
  fall back to the repo decoder at reduced N.
- **Test.** Plant `sha256_ctr(b"CICADA3301")` reduced mod 29 (the exact B-04/G5 family) over
  12,956 runes of English, encipher with `encipher_keyskip(sign=-1, supp=0.8129, seed=3301)`,
  decode with the beam at the settings B-04 Stage D actually used (`beam_w=400,
  max_skip=3`), at `L in {120, 400, 1000, 3000, 6000, 12956}`.
- **Pass bar, fixed now:** at L = 12,956 the beam must return `score >= -5.5` **and**
  rune-recovery >= 0.90.
- **Consequence, fixed now:** if it fails, then Stage D's full-stream escalation, and any
  other escalation-to-full-length argument in this repo, is **UNSOUND-AT-LENGTH** — a null
  from an unvalidated instrument (`AGENTS.md` section 4, lesson 1) — and must be
  re-labelled. This lane will say so in exactly those words and will report the longest `L`
  at which the beam still passes, as the honest bound.

### B.4 The drift-corrected offset ladder — the never-run region
Under a **single continuous keystream** (which is what P4's flat, unscoped verdict implies),
the correct key index at the first rune of page `k` is

        o_k  =  start_k + S_k ,   S_k ~ mean rho*start_k,  sd ~ sqrt(start_k * rho * (1+rho))

For page 52 that is `start ~ 12,200` => **o ~ 12,552 +/- 19**. No stage of any campaign has
tested this. B-04 Stage A/B tested only the 120-rune **head** at offsets {0...3301}; Stage C
tested each page at a **restart** (offset 0); Stage D tested the full stream for 150 configs
only. And the beam **cannot repair the gap by itself**: it can insert skips but never remove
them, and closing a 352-draw deficit inside a 100-rune page would need 3.5 skips per rune
against a `max_skip` of 3 and a validity test that passes with probability 1/29.

- **Region.** Candidates = the union of the published top lists of `round13/B04`
  (`results_A/B/C/D`), `round16/KDF` (`results_summary`, `results_A`) and `round16/prng`
  (`results.top20`), deduplicated on (generator, reduction, seed, sign, atbash, direction).
  Segments = all 55 unsolved pages, first 100 runes. Offsets = `o_k` +/- 4 sd, integer step
  1, plus a control point at `start_k` (uncorrected) and at 0 (Stage-C restart) so the
  *increment over covered ground* is visible.
- **Positive control B4-PC (mandatory).** Plant a keystream, encipher the real page-`k`
  length under the filter at the true continuous offset, drop it into the ladder among the
  real candidates, and require it to rank **#1** and clear the bar. The ladder may not
  report a negative unless this passes.
- **Bar.** `threshold_for(N_decodes, segment_len=100)` from `benchmark/null.py`, reported
  alongside the fixed -5.5 floor and alongside a measured shuffle null at the same segment
  length (N >= 200, seed 3301).
- **Also measured:** the beam's **inferred skip count** for each candidate. Under a true
  keystream this should track `rho*L`; under a wrong one it is score-hacking. If the two
  distributions separate, that is a *second, English-independent ranking channel* and is
  reported as an instrument, with its measured separation.

---

## 4. Sub-attack C — THE CONSTRAINT / INFORMATION BUDGET

An honest accounting, in bits, of what the 12,956 acceptance certificates buy.

- `H(C)` — entropy of the observed ciphertext under the fitted filtered-Markov law, measured
  on the real stream, versus `12,956*log2(29)` for an unfiltered stream. The difference is
  the **filter's total information injection**.
- `H(P)` — plaintext entropy, measured as the empirical per-rune conditional entropy of the
  repo's own English-in-runes baseline (not assumed at 1.5 bits).
- `H(K)` — `(12,956 + E[S])*log2(29)` for a full-entropy pad; and, for the derived branch,
  the seed length in bits.
- **The decision rule (fixed now):** the joint (P, K) is *determined* iff
  `H(P) + H(K) - H(C) <= 0`. Report the deficit in bits. Report separately:
  (i) the acceptance events' contribution to that deficit, computed exactly, and
  (ii) the maximum `H(K)` for which the system becomes determined — the number that says
  what extra input would close the gap.
- **A falsifiable sub-claim, recorded now:** the acceptance events contribute **zero** net
  constraint on the plaintext, because for *any* candidate plaintext there exists at least
  one consistent keystream (the zero-skip one). If a counting argument or a simulation shows
  otherwise, this claim was wrong and the SAT/BP formulation is worth building.
- **Positive control C-PC.** Run the same accounting on a **64-bit-seed** derived keystream
  and confirm the budget returns "over-determined" — i.e. the instrument agrees with D3's
  demonstrated recovery of a planted short seed. If the accounting says a recoverable case
  is under-determined, the accounting is wrong.
- **Build-it trigger (fixed now):** a constraint-propagation / SAT / belief-propagation
  solver over the joint variables is built and run **only if** the deficit is <= 0 or within
  ~10^3 bits of zero under some stated extra assumption. Otherwise the deliverable is the
  number and the statement of what would close it. Reporting the size of the gap is the
  useful negative.

---

## 5. What this lane will report regardless of outcome

Per `CAMPAIGN-PLAN.md` rule 6: coverage, not conclusion. `RESULTS.md` will carry, for each
sub-attack, the measured control recovery, the bar in force, the region actually covered,
the region explicitly **not** covered, and the concrete condition that reopens it. The words
"exhausted", "closed" and "unsolvable" will not appear as verdicts.

## 6. Files this lane will write

`PREREG.md` (this file) - `fastbeam.py` - `filter_models.py` - `a_locus.py` -
`b_drawcount.py` - `c_budget.py` - `RESULTS.md` - `ledger.json` - `*.json` result files.
No `git commit` (rule 8).
