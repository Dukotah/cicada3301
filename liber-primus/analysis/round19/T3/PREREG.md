# T3 — THE PROPAGATION MAP — PRE-REGISTRATION

_Round 19, Phase 3 (independent). Written **before** any perturbation was measured.
Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Status of this file at the moment it was written:** the only quantities read from the repo
so far are *published* ones (`PROBLEM.json`, `LEDGER.json`, `round18/L2`, `round18/L4`,
`round18/L7`, `round17/P4`, `independent-read/FINDINGS.md`, `retranscribe/FINDINGS.md`,
`round12/frontB/RESULTS.md`) plus two structural facts established as a *prerequisite* and
reported here as such (§0.2). No perturbation has been run.

---

## 0. What this lane is

T1 and T2 are re-reading the transcription. Neither can say what a changed rune would **do**.
This lane answers that in advance and quantitatively:

> **If the 12,956-rune stream changes by _k_ runes at positions _P_, which of this
> repository's results move, and by how much?**

The repo has audited the transcription four ways. An audit says *how likely it is to be
wrong*. It does not say *what happens if it is*. Only the second question prices T1 and T2.

### 0.1 The object, pinned

| | value |
|---|---|
| baseline stream | `lib_numchannel.unsolved()`, 12,956 runes |
| `sha256(",".join(indices))` | `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585` |
| matches `PROBLEM.json.ciphertext_identity` | **required, checked at the top of every script** |

Every perturbed stream this lane produces is hashed the same way and the hash is stored with
its statistics, so any row here is re-derivable and no row can be confused with the baseline.

### 0.2 A prerequisite that turned out to be a finding — the 450 are now in stream coordinates

`analysis/independent-read/oae_mismatch.json` records the 450 located O/A/AE disagreements as
`(page_image, line_in_image, pos_in_line, global_line, global_glyph_index)`. Those coordinates
live in the **segmented-glyph index space** of `analysis/stones/dataset.npz` (10,774 glyphs on
count-exact lines), **not** in the 12,956-rune stream. No file in the repository maps them to
stream positions; `crypto_exposure.py`, the only script that costed the family
cryptographically, worked on the whole `ᚩ/ᚪ/ᚫ` family in `data/krisyotam_runes.txt` and never
used the located positions at all.

The map exists and is exact. `analysis/stones/pipeline.global_lines()` returns the 594 canon
lines of pages 0–54; their concatenation is **element-wise identical** to
`lib_numchannel.unsolved()` (verified, 12,956/12,956) and hashes to the `PROBLEM.json` SHA-256.
So `stream_pos = offset(global_line) + pos_in_line`.

**Positive control on the map, run before anything else:** for all 450 records the canon rune
at the mapped stream position must equal the record's `canon` field. Measured: **450/450, zero
mismatches, 450 distinct positions**, spanning positions 27 … 12,897 across all 55 pages.

This is pre-registered as a *gate*, not a result: if it had returned < 450/450 the targeted arm
(§3) would not have run.

---

## 1. The Aiming Test (doctrine §1) — five answers

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A "hit" for this lane is a **flip**: a statistic that is load-bearing for a published claim
crossing the threshold that claim rests on, at a perturbation size _k_ that is plausible.

The recognizer is written before the search and is a **planted flip**:

- **PC-1 (plant a flip, doublet channel).** Construct a perturbation designed to *maximise*
  doublet creation — for each chosen position, overwrite it with a copy of its neighbour.
  The instrument must show the doublet rate crossing every pre-registered floor and must report
  the crossing _k_ to within ±1 of the analytic prediction. If the instrument cannot see a flip
  it was handed, its silence on random perturbation means nothing.
- **PC-2 (plant a flip, decode channel).** At ε = 1.0 (every ciphertext rune replaced by a
  uniform draw) the correct-key beam decode must collapse to the wrong-key band. If it does
  not, the decode arm is not measuring what it claims.
- **PC-3 (equivalence).** Every statistic this lane recomputes must reproduce the repo's own
  published value on the **unperturbed** stream, to the published precision, using the repo's
  own implementation where one exists (`lp.stats`) and a proven-equivalent one where it does
  not. Any mismatch is reported as a **finding**, not silently fixed.

### Q2 — What measured fact raises this family's prior above the flat rate?

Three, each with a path:

1. **`round18/L2-filter-leak/RESULTS.md` §2**, closing line of the Δ-spectrum paragraph:
   `delta_chi2/df` = 1.533 is *"the largest single deviation of the real stream from the pinned
   model in this battery … **recorded so that a future re-read of the transcription can check
   whether it moves**."* L2 explicitly deferred a transcription-sensitivity check to a later
   lane. This is that lane.
2. **`round18/L7-redteam/RESULTS.md` §C.2** narrowed the doublet-deficit margin from a published
   2.26× to a measured **1.46×** (binding register German, floor 0.972 %). A margin of 1.46×
   is small enough that "how many runes does it take to close?" is a real question with a
   finite answer, where at 2.26× it would have been rhetorical.
3. **`analysis/round10/RECON-A/REGISTER.md` A-02** carries the 450 as `partially-run` — *"no
   per-instance verdict was ever recorded"* — and `round19/R1/RESULTS.md` ranks them the repo's
   **rank-1 bounded object**, noting the consequence: *"the ciphertext itself changes → **every**
   negative in the repo is re-opened, not re-weighted."* R1 asserts that consequence. Nobody has
   measured it.

### Q3 — Is the space bounded, and by what?

**Enumerable at the object level; samplable at the perturbation level, with a stated fraction.**

- The **targeted** space is *finite and fully enumerated*: 450 located positions × the O/A/AE
  confusion set. The full power set is 2⁴⁵⁰, so subsets of size _k_ are sampled — but the
  *positions* and the *substitution alphabet* are exhaustive, which is the part that matters.
- The **random** space is sampled: C(12956, k) × 28ᵏ. Coverage fraction is ~0 and is reported as
  such; the estimand is a **distribution over a summary statistic**, not a search, so sampling
  error (not coverage) is the honest uncertainty and it is reported as a band.
- The **register floor** space is enumerated: the 9 registers L7-C.2 measured, plus the 4
  D2 English corpora, plus the stale published figure.

### Q4 — What are the three conditionals the negative will carry?

This lane produces **bounds on sensitivity**, not a key-space negative, so the three conditionals
take their sensitivity-analysis form and all three are named in `RESULTS.md`:

1. **Perturbation model** — which error processes are covered (uniform-random substitution;
   O/A/AE confusion at the 450 located positions; O/A/AE confusion anywhere in the family;
   dense-page-concentrated; adversarial doublet-maximising). **Not covered:** insertions,
   deletions, and line-order/segmentation errors, which change _n_ and shift every downstream
   index. Those are a different and strictly more damaging class and this lane does not bound
   them.
2. **Statistic set** — which published quantities are recomputed. Anything load-bearing whose
   provenance cannot be established is **flagged**, not assumed insensitive.
3. **Decoder / adjudicator** — the decode arm uses `campaign18_skip.encipher_keyskip` +
   `round18/L2/fastbeam.beam_decode` (gate-F0-identical to `skipdecode.beam_decode`) with the
   English quadgram scorer. Per L7-A that is an **English-only, `encipher_keyskip`-only**
   instrument, so the decode arm's numbers are conditional on both, and it is used
   **relatively** (correct-key vs wrong-key in the same cell) so that no absolute bar is needed.

### Q5 — What single observation kills this lane at 10 % of budget?

**If PC-3 fails** — if the recomputed statistics do not reproduce the repo's published values on
the unperturbed stream — the lane stops and reports the discrepancy as its whole result. A
sensitivity curve anchored at the wrong baseline measures nothing.

Secondary kill: if the map gate (§0.2) had returned fewer than 450/450, the targeted arm would
have been dropped and the lane would have reported the random arm plus the mapping failure.

---

## 2. The statistics, and the thresholds each is measured against

**No fixed score bar is used anywhere in this lane.** Per the round's own instruction and
`round19/G2`'s measurement (random data scores −4.51/−4.82 under I1's drift modes), −5.5 is not
valid. The decode arm uses an **in-lane, same-cell wrong-key comparison**; where an absolute
bar is unavoidable it defers to `round19/I3/calib19.json`.

### 2.1 Channel D — the doublet deficit (the headline)

Statistic: `lp.stats.doublet_count` / `doublet_rate` on the perturbed stream.
Baseline: 86 doublets, 0.66384 % over 12,955 adjacent pairs.

Pre-registered floors, all published, all cited, **fixed now**:

| id | floor | value | source | doublets needed |
|---|---|---|---|---|
| **D-GER** | binding register, all 9 | **0.972 %** German | `round18/L7-redteam/RESULTS.md` §C.2 | 126 |
| **D-VNV** | vowel-dropped English | 1.084 % | ibid. | 141 |
| **D-LAT** | Latin | 1.425 % | ibid. | 185 |
| **D-KJV** | lowest of D2's four English corpora | 1.386 % | `round18/L7` §C.2 reproducing R12/D2 | 180 |
| **D-STALE** | the figure still quoted in `ELIMINATION-LEDGER.md:779` | 1.50 % | (superseded; carried for continuity) | 195 |
| **D-MAX** | highest register floor | 2.339 % Welsh | `round18/L7` §C.2 | 304 |

**Reported quantity `k*(floor)`** — the smallest _k_ at which the perturbed doublet rate reaches
the floor. Three variants, all reported:

- `k*_med` — median over trials reaches the floor (the *typical* case);
- `k*_p95` — the 95th percentile reaches the floor (the *earliest plausible* failure);
- `k*_max` — the adversarial doublet-maximising perturbation reaches the floor (the **worst
  case**, and the only one that is a true bound).

`k*_max` is the number that bounds the argument. `k*_med` is the number that describes it.

### 2.2 Channel I — flatness

`lp.stats.ioc_norm` (baseline 0.999874 published 0.9999) and `lp.stats.shannon_entropy`
(4.856504, published 4.8565) and `lp.stats.chi2_uniform`. Threshold: **|IoC·N − 1| exceeding
the 99th percentile of a size-matched uniform-rune null measured in-lane (n = 2,000 draws)**.
Direction matters and is reported: O/A/AE confusion *concentrates* mass on three symbols and
therefore pushes IoC·N **up**, i.e. toward English, which is the dangerous direction.

### 2.3 Channel F — the filter constants

- lag-1 suppression, computed **L7-C.1's way**: `1 − r_obs / r_unigram` where `r_unigram` is the
  stream's own collision rate (3.4478 %), not 1/29. Baseline 80.746 %.
- `s*` from L2's closed form `r(s) = q(1−s)/(1−qs)`, `q = 1/29`, inverted. Baseline 0.81288.
- draw count `ρ·n = n·qs/(1−qs)`. Baseline 373.6.
- **L2 containment threshold**: L2 declared the real stream *inside* `M1_ct_keyskip` at
  max |z| = 2.01 and excluded a model only at ≥ 4 sd. The replicate sd of the doublet count
  under M1 is ≈ √86 = 9.27, so the pre-registered containment breach is a doublet count of
  **86 + 4 × 9.27 = 123** (0.949 %) — a *separate* and independently-motivated threshold that
  happens to sit near D-GER. Both are reported; neither is adjusted to the other.

### 2.4 Channel L — layout-coupled statistics

- doublets crossing a line break (baseline **4** of 86; `round18/L4` §0, `round17/P4`);
- line-initial χ²(28) vs the full-text distribution (baseline **78.656**; `round18/L4` Arm A1);
- the layout-aware null's verdict on it (baseline p = 0.177).

A substitution at a line-initial position changes A1 directly; the 450 include such positions,
so this channel is measured on the targeted arm specifically.

### 2.5 Channel Δ — L2's deferred statistic

`delta_chi2/df` over the 28 non-zero cells of `D_i = (c_i − c_{i−1}) mod 29`, baseline **1.533**,
plus max |z| over the 28 cells, baseline **2.64** at D = 17, against L2's pre-registered
Bonferroni bar **|z| ≥ 3.57**. This is the statistic L2 asked a re-read to check. Reported at
every _k_ and on the targeted arm.

### 2.6 Channel K — do the *negatives* survive? (correct-key recovery)

The statistics above are properties of the ciphertext. The **negatives** are properties of a
decode. Pre-registered design:

1. take a real LP1-register plaintext window of length L;
2. encipher under a known keystream with `encipher_keyskip(supp=0.83)` — the pinned filter;
3. corrupt _k_ ciphertext runes (i.e. simulate the transcription error the sweeps were fed);
4. decode with the **correct** key through `fastbeam.beam_decode(beam_w=400, max_skip=3)`;
5. record `score_norm` and rune-index recovery.

Two **relative**, bar-free endpoints, fixed now:

- **K-REC**: the _k_ at which median rune recovery drops below **0.90** (L2's own B.3 gate
  value for a passing full-book positive control).
- **K-SEP**: the _k_ at which the correct-key score distribution's 5th percentile falls below
  the **in-lane wrong-key** distribution's 95th percentile — i.e. the point at which a sweep
  could no longer rank the correct key above noise. Measured, not assumed; no fixed bar.

If K-REC / K-SEP sit **below** the expected wrong-rune count, then every negative in the repo
is conditional on a transcription that may already be too noisy for the instrument, and T1/T2
are not a refinement but a prerequisite. If they sit **far above**, the negatives are robust and
that is worth stating plainly because it has never been demonstrated.

### 2.7 Provenance flags

Every `LEDGER.json` entry and every synthesis claim is classified
`stream_dependent ∈ {yes, no, indirect, UNKNOWN}` with the script that computes it. **UNKNOWN on
a load-bearing claim is itself a reported finding** (doctrine R7: say what was not covered).

---

## 3. Perturbation models (fixed in advance)

| id | model | positions | substitution |
|---|---|---|---|
| **P-RAND** | uniform random | _k_ of 12,956, uniform without replacement | uniform over the 28 other runes |
| **P-OAE450** | the located set | _k_ of the **450** mapped positions | the recorded `looks_like` rune (the clusterer's actual alternative) |
| **P-OAE450R** | the located set, random direction | _k_ of the 450 | uniform over the other two members of {O, A, AE} |
| **P-OAEFAM** | the whole family | _k_ of the 1,4xx O/A/AE positions in the stream | uniform over the other two family members |
| **P-DENSE** | dense-page concentration | _k_ drawn only from pages 45–54 | uniform over the 28 others |
| **P-ADV** | adversarial | _k_ chosen to maximise doublet creation | copy of a neighbour |
| **P-COLLAPSE** | the published maximum-damage case | all O/A/AE positions | family merged to one symbol |

`P-COLLAPSE` reproduces `independent-read/FINDINGS.md` §4 (doublet 0.68 % → 1.46 %) and is
therefore a **second independent equivalence control** on this lane's machinery.

_k_ grid: **1, 2, 5, 10, 20, 50, 100, 200, 450**, extended upward (1000, 2000, 4000, 8000,
12956) wherever a threshold has not yet been crossed at 450 — because "it does not flip at 450"
is only a bound if the flip point is located.

Trials: **400 per (model, k)** for the cheap channels; **≥ 60** for the decode channel.
Reported as median with a 5–95 % band, never as a point.

---

## 4. Reuse, and the equivalence proof if not

Doctrine and the lane brief both require reusing the repo's own implementations.

| statistic | implementation used | equivalence obligation |
|---|---|---|
| doublets, IoC·N, entropy, χ² | **`lp.stats`** (the repo's own) | none — it *is* the repo's |
| lag-1 suppression | reimplemented, L7-C.1 formula | must return 80.746 % on baseline |
| `s*`, draw count | reimplemented, L2 §1 closed form | must return 0.81288 / 373.6 |
| Δ-spectrum | reimplemented, L2 §2 definition | must return 1.533 / max‖z‖ 2.64 |
| line-break doublets, line-initial χ² | reimplemented over `pipeline.global_lines()` | must return 4 and 78.656 |
| beam decode | **`round18/L2/fastbeam`** (gate F0 vs `skipdecode`) | F0 re-run in-lane |
| enciphering | **`campaign18_skip.encipher_keyskip`** | none |

**Any mismatch is a finding and is reported in `RESULTS.md`, not fixed silently.**

---

## 5. The decision question, and how it will be answered in one number

Given the four audits, compute an **expected wrong-rune count** `E[W]` and compare it to the
smallest flip point `k*` over every channel above.

Audit inputs, all published, fixed now:

| audit | measured | coverage |
|---|---|---|
| R9 template DP (`retranscribe/FINDINGS.md`) | 96.93 % (5,047/5,207) | 232/604 lines = 38.4 % |
| R12 front B (`round12/frontB/RESULTS.md`) | 98.0 % over 5,150 glyphs | same 232 count-exact lines |
| krisyotam ≡ relikd (`transcription/TRANSCRIPTION-VERDICT.md`) | 0 disagreements / 12,956 | 100 %, but **not independent** (one 2017 root) |
| label-free clustering (`independent-read/FINDINGS.md`) | 450 O/A/AE disagreements | 10,774 glyphs |

Three estimators are pre-registered and **all three** are reported, because they differ by an
order of magnitude and picking one would be the whole answer:

- `E[W]_upper` — every audit disagreement is canon's error: `(1 − 0.9693) × 12,956`.
- `E[W]_located` — the located candidate set taken at face value: 450.
- `E[W]_attributed` — the audits' own bucket attribution (R9: 15 DP edge artifacts + 3
  high-cost misreads on *solved* pages + 85 whole-line read failures on 45–47 = 103, none
  attributed to canon), i.e. the audits' own claim.

The verdict sentence is fixed in advance and takes one of exactly two forms:

> **MARGIN HOLDS** — `E[W]_upper < k*_min` by a factor of _R_ ≥ 2. The transcription is not
> the blocker *and this is now demonstrated rather than assumed*; T1/T2 are confirmatory.
>
> **MARGIN DOES NOT HOLD** — some channel flips at `k* ≤ E[W]_upper`. Name the channel, the
> claim it carries, and the ledger entries downstream of it.

A factor between 1 and 2 is reported as **MARGIN NARROW** with the factor stated.

---

## 6. Kill conditions and checkpoints

| checkpoint | condition | action |
|---|---|---|
| after PC-3 | any baseline statistic disagrees with its published value beyond stated precision | **STOP**, report the discrepancy as the lane's result |
| after the map gate | < 450/450 | drop the targeted arm, report the mapping failure |
| after channel D at k = 450 | no floor crossed and `k*_max` located | proceed to channels I/F/L/Δ/K |
| after channel K pilot (10 reps) | wrong-key and correct-key bands already overlap at k = 0 | **STOP** channel K, report the decode instrument as unusable at that L, do not report a curve |

---

## 7. Deliverables

`PREREG.md` (this file) · `dependency_map.json` · `t3_lib.py` · `t3_baseline.py` ·
`t3_sensitivity.py` · `t3_targeted.py` · `t3_decode.py` · `t3_depmap.py` ·
`out_baseline.json` · `out_random.json` · `out_targeted.json` · `out_decode.json` ·
`RESULTS.md` · `ledger.json`

Written 2026-08-26, before measurement. No threshold in §2, §3 or §5 may be edited after a
result is seen; corrections go in a dated addendum with the reason.

---
