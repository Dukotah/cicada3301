# T3 — THE PROPAGATION MAP — RESULTS

_Round 19, Phase 3. Pre-registered in [`PREREG.md`](PREREG.md) before any perturbation was
measured. No threshold in the PREREG was edited after a result was seen._

**The question:** the repo has audited the transcription four ways. An audit says *how likely
it is to be wrong*. It does not say *what happens if it is*. This lane measures the second
thing, so that T1's and T2's re-read has a price.

---

## 0. Headline — four numbers

| question | answer |
|---|---|
| **k at which the doublet-deficit argument fails** | **k = 20** as an adversarial *bound*; **k ≈ 714** (median) / **497** (p95) for uniform random error; **never** for the actual O/A/AE error process, which tops out at **0.795 %** against a 0.972 % floor |
| **the targeted result — all 450 located O/A/AE flipped** | doublets 86 → **103**, rate 0.664 % → **0.795 %**. Still **1.22× below** the binding floor and **1.74× below** the lowest English floor. The one thing that does move: **IoC·N 0.99987 → 1.01382**, out of the flatness band from k ≈ 167 |
| **expected wrong runes** | **0** (point estimate, and it is *measured*, not assumed — see §6); **398** as the crudest upper bound the audits themselves reject |
| **does the margin hold?** | **YES on every statistic channel, against every error process in evidence** — and it has never been demonstrated before. **NARROW** on the decode channel, and that is the finding this lane did not expect |

**One sentence.** An independent per-glyph reader measured at 95.56 % on the LP2 typeface
(round19/C3) errs *more often* than canon and that reader disagree, so the audits' 3.07 % and
2.0 % disagreement rates are fully explained by the instrument and imply a canon error rate of
**zero**; and even charging every disagreement to canon (398 runes) leaves the doublet deficit
short of the binding floor by a factor of 1.79 and the *actual* O/A/AE error process short of it
in every direction it can be pushed.

---

## 1. Trust anchor and PC-3 — the equivalence gate

```
python3 liber-primus/tests/validate.py     ->  ALL VALIDATIONS PASSED (5/5 known solves)   [before and after]
```

Baseline stream: **12,956 runes**,
`sha256 = 023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`
— identical to `PROBLEM.json.ciphertext_identity`. Every perturbed stream in `out_*.json`
carries its own SHA-256 so no row can be confused with the baseline.

**PC-3 — every published statistic reproduces on the unperturbed stream. 13 of 13.**

| statistic | published | recomputed | source |
|---|---|---|---|
| runes | 12,956 | 12,956 | `PROBLEM.json` |
| doublets | 86 | 86 | `PROBLEM.json`, L4 §0, L7 C.1 |
| doublet rate | 0.664 % | **0.663836 %** | L7 C.1 |
| IoC·N | 0.9999 | **0.999874** | L7 C.1 |
| entropy | 4.8565 | **4.856504** | L7 C.1 |
| unigram collision | 3.4478 % | **3.447840 %** | L7 C.1 |
| lag-1 suppression | 80.75 % | **80.7463 %** | L7 C.1, R17/P4 |
| `s*` | 0.81288 | **0.8128837** | L2 §1 |
| extra draws | 373.6 | **373.636** | L2 §1 |
| Δ-spectrum χ²/df | 1.533 | **1.53260** | L2 §2 |
| Δ max \|z\| (at D = 17) | 2.64 | **2.6414 at D = 17** | L2 §2 |
| line-break doublets | 4 | **4** | L4 §0, R17 |
| line-initial χ²(28) | 78.656 | **78.65603** | L4 Arm A1 |

Two further equivalence controls, neither required:

- **`P-COLLAPSE`** reproduces `independent-read/FINDINGS.md` §4 on its own corpus:
  IoC 0.9998 → **1.1370** (published "1.00 → 1.14"), doublet 0.6776 % → **1.4617 %**
  (published "0.68 % → 1.46 %"). That is the only sensitivity number previously published
  anywhere in this repo, and this lane's machinery reproduces it.
- **`gate_F0`** re-run in-lane: `fastbeam` vs `skipdecode.beam_decode`, 20 cases,
  max score delta **8.88e-15**, **0** path mismatches.

**One methodological note, not an error.** "The stream's own unigram collision rate" in L7-C.1
is the *unbiased* estimator `Σcᵢ(cᵢ−1)/n(n−1)` — i.e. exactly `lp.stats.ioc` — not the plug-in
`Σpᵢ²`. The two differ in the third significant figure here (3.44784 % vs 3.45529 %) and only
the unbiased one returns the published 80.746 %. A reimplementation that reaches for `Σpᵢ²`
lands on 80.788 %. Recorded so the next lane does not re-derive it.

**PC-1 — the planted flip is recognised.** The adversarial doublet-maximiser's output matches
its closed-form prediction **exactly at every k tested** (k = 1 … 1000). The instrument can see
a flip it is handed.

---

## 2. Job 1 — the dependency graph

`dependency_map.json`. All **62** ledger entries plus **17** load-bearing synthesis claims,
each classified by *how* it touches the stream — because each channel has a different
sensitivity curve, and lumping them together is what made "the transcription is not the
blocker" un-testable.

| channel | what it means | entries | measured sensitivity |
|---|---|---|---|
| **S0** | not stream-dependent (images, PGP, OSINT, toolchain, provenance, bar calibration) | 30 (+2 mixed) | insensitive by construction |
| **S1** | stream → **summary statistic** (doublet rate, IoC, entropy, Δ-spectrum, χ²) | 10 (+5 mixed) | **smooth**: +1 doublet per ~17 random substitutions |
| **S2** | stream → **decode score** (every keystream / keytext / pad / KDF sweep) | 27 (+5 mixed) | **discontinuous** — §5 |
| **S3** | stream → **layout / counts** (line breaks, glyph widths, positional subsets) | 4 (+2 mixed) | smooth, but assumes `n` is preserved |
| **S4** | the transcription **is** the claim (the four audits, A-01, A-02, B-13, frontB) | 5 | these are producers, not consumers |
| **UNKNOWN** | provenance not establishable | **0** | — |

`n_stream_dependent = 53 of 62`. **Nothing load-bearing is left UNKNOWN.** One
`reproduce` path in the ledger does not resolve on disk (`R16-KDF` → `sweep.py` in
`analysis/round16/KDF/`, which holds only `PREREG.md`, `RESULTS.md` and three result JSONs);
it is flagged in `dependency_map.json.reproduce_paths_missing`, and its entry's own note says
it "reuses round15/KDF/sweep.py", so this is a stale path rather than a lost script.

**Two structural facts the map makes visible, and neither was written down before:**

1. **Every sweep negative in the repository (27 S2 entries, ~10¹⁰ decodes) routes through the
   *same* fragile channel** — a beam decode of *this exact ciphertext*. They do not inherit the
   gentle S1 curve. §5 measures what they actually inherit.
2. **L7-A and L7-B are `S0`-like, not `S2`.** They measure the instrument on *synthetic*
   ciphertext, so they are transcription-independent — the two most consequential findings of
   Round 18 are immune to whatever T1 and T2 come back with. Worth knowing before the re-read
   lands.

### 2.1 A conflict of record the map surfaces

`round18/L2` §2 and `round18/L7` §C.2 disagree about whether the object of this lane's headline
is load-bearing at all:

- **L2-A** concludes the surviving filter family acts on the *emitted ciphertext*, so the
  residual doublet rate "is a property of the filter alone and is **independent of both key and
  plaintext** … **no doublet-based statistic has discriminating power over key type, in either
  direction**", explicitly finding for RECON-B's **B-16**.
- **L7 §C.2** concludes the G3 doublet-deficit argument "**survives** extension from 4 English
  corpora to 9 registers".

Both are Round 18, neither cites the other. This lane does not adjudicate it — but it changes
what the headline *means*: if L2-A stands, the k below is the sensitivity of a statistic that
was already not doing the work; if L7-C.2 stands, it is the sensitivity of the load-bearing
step. **Either way the transcription is not the binding constraint on it**, which is the only
claim this lane makes. Flagged for R1.

---

## 3. Job 2 — the sensitivity curve for the doublet deficit

### 3.1 The arithmetic, measured

A substitution touches exactly two adjacent pairs. Measured yield per changed rune:

| model | doublets added per substitution | why |
|---|---|---|
| uniform random | **0.050 – 0.060** (0.0578 at k = 450) | new rune matches a neighbour with prob ≈ 1/28 on each side, minus the doublets it destroys |
| **adversarial** | **exactly 2.00**, while the +2 sites last | there are **441** positions where `C[i−1] == C[i+1] != C[i]`; overwriting one doubles *both* pairs |

The floors, and the doublets each requires (12,955 adjacent pairs):

| floor | % | doublets needed | Δ from 86 |
|---|---:|---:|---:|
| observed | 0.6638 | 86 | — |
| **D-GER — German, the binding register** | **0.972** | **126** | **+40** |
| L2's 4-sd containment breach of `M1_ct_keyskip` | 0.950 | 124 | +38 |
| vowel-dropped English | 1.084 | 141 | +55 |
| **KJV — lowest of D2's four English corpora** | **1.386** | 180 | +94 |
| Latin | 1.425 | 185 | +99 |
| held-out English | 1.483 | 193 | +107 |
| **the stale "1.50 % (KJV)" still at `ELIMINATION-LEDGER.md:779`** | 1.500 | 195 | +109 |
| Welsh — highest | 2.339 | 304 | +218 |

> **Correction of record, carried forward from L7 §C.2.** The lane brief and
> `ELIMINATION-LEDGER.md:779` both quote a **1.50 % (KJV)** floor. L7 measured KJV at **1.386 %**
> and found the *binding* register is **German at 0.972 %** — a margin of **1.46×**, not the
> 2.26× the 1.50 % figure implies. This lane reports k against **all** of them, but the honest
> headline is the 0.972 % one, because it is the first to close.

### 3.2 k\*(floor) — the table

`out_summary.json → k_star_doublet`. `k_median` = the median trial reaches the floor;
`k_p95` = the 95th-percentile trial reaches it (earliest plausible failure); P-ADV is
deterministic and is the **worst-case bound**.

| model | **k\*(0.972 % German)** | k\*(1.386 % KJV) | k\*(1.50 % stale) | k\*(L2 containment) |
|---|---:|---:|---:|---:|
| **P-ADV** — adversarial bound | **20** | 47 | 54 | 19 |
| **P-RAND** — uniform random, median | **714** | 1,756 | 2,053 | 660 |
| P-RAND — p95 (earliest plausible) | **497** | 1,410 | 1,679 | 452 |
| **P-DENSE** — pages 45–54 only, median | **893** | never (max 1.104 % at k = 1,993) | never | 819 |
| **P-OAE450** — the located set, clusterer's own alternative | **never** (max **0.795 %** at k = 450) | never | never | never |
| **P-OAE450R** — the located set, random within {O,A,AE} | **never** (max **0.841 %** at k = 450) | never | never | never |
| **P-OAEFAM** — any of the 1,385 family runes | **never** (max **0.857 %** at k = 800) | never | never | never |

**Read across the row that matches your error model.** The three that matter:

- If transcription errors were **uniform random substitutions**, it takes **~714** of them
  (median) or **~497** (p95) before the doublet rate reaches the binding floor. Both are above
  the crudest expected-error estimate of 398.
- If they are the **O/A/AE confusions actually in evidence**, the floor is **never reached** —
  not at k = 450, not at the whole 1,385-rune family. The family is too small and its runes are
  too rarely adjacent to each other. Of the 450 located positions only **74** have an O/A/AE
  neighbour at all, and only **one** is a +2 site.
- The **adversarial k = 20** is a genuine bound and is reported as one. It requires an error
  process that finds the 441 positions where both neighbours are already equal and writes the
  doubling rune into each. Nothing in the evidence resembles that; the measured process is a
  branch-angle confusion inside a 3-rune family, which is close to the *opposite*.

### 3.3 The other statistic channels, at k = 450 (uniform random)

| statistic | baseline | k = 450 random, median [p05, p95] | threshold | crossed? |
|---|---|---|---|---|
| doublet rate | 0.6638 % | 0.8645 % [0.7873, 0.9494] | 0.972 % | **no** |
| IoC·N | 0.99987 | 0.99987 [—] | uniform-null p99 = 1.00172 | **no** |
| entropy | 4.8565 | 4.8565 | — | no |
| lag-1 suppression | 80.75 % | ≈ 74.9 % | — | — |
| line-break doublets | 4 | ≈ 4 | — | no |
| line-initial χ² | 78.656 | ≈ 78 | L4's layout-aware null | no |

Uniform random error is essentially invisible to everything except the doublet rate, and even
there it takes ~700 runes. **The doublet deficit is the *most* fragile of the summary
statistics, not the least** — which is worth knowing, because it is also the load-bearing one.

---

## 4. Job 3 — the targeted perturbation. This is the realistic case

### 4.1 The 450 are now in stream coordinates — a prerequisite that was a finding

`independent-read/oae_mismatch.json` stores the 450 disagreements as
`(page_image, line_in_image, pos_in_line, global_line, global_glyph_index)`. Those live in the
**segmented-glyph index space** of `analysis/stones/dataset.npz` (10,774 glyphs on count-exact
lines), **not** in the 12,956-rune stream. Nothing in the repo mapped them across;
`crypto_exposure.py`, the only script that ever costed the family, worked on the *whole* family
in `krisyotam_runes.txt` and never used the located positions.

The map is `stream_pos = offset(global_line) + pos_in_line`, licensed by the fact that
`stones/pipeline.global_lines()`'s 594 lines concatenate to a stream **element-wise identical**
to `lib_numchannel.unsolved()` and hashing to the `PROBLEM.json` pin.

**Gate: 450/450 records map, 450 distinct positions, the canon rune matches at every one.**
Positions span **27 … 12,897** across all 55 pages. Confusion breakdown:

| canon → looks-like | n |
|---|---:|
| A → O | 306 |
| O → A | 72 |
| AE → A | 70 |
| A → AE | 2 |

The O/A/AE family is **1,385 of 12,956 runes = 10.69 %** of the unsolved stream
(1,406 / 13,136 = 10.70 % over the full corpus, matching FINDINGS §4).

**Doublet potential of the located set — this is why the targeted case is inert.** Of the 450:

| | n |
|---|---:|
| flipping it would add **2** doublets | **1** |
| would add 1 | 42 |
| would add 0 | 403 |
| would **destroy** a doublet | 4 |
| **net if all 450 are flipped** | **+40** |
| have an O/A/AE rune as a neighbour at all | 74 |

### 4.2 The exact points — every one of these is a single deterministic stream, hashed

| stream | doublets | rate | IoC·N | lag-1 supp | Δ max\|z\| | line-init χ² | sha256 (first 16) |
|---|---:|---:|---:|---:|---:|---:|---|
| **baseline** | 86 | 0.6638 % | 0.99987 | 80.75 % | 2.641 | 78.66 | `023312066df47100` |
| **all 450 → clusterer's own alternative** | **103** | **0.7951 %** | **1.01382** | 77.26 % | **3.137** | 82.14 | `35651be7ba831ce2` |
| all 450 → adversarial within {O,A,AE} | 141 | 1.0884 % | 0.99991 | 68.43 % | 2.554 | 79.56 | see `out_targeted.json` |
| **all 1,385 family → adversarial within {O,A,AE}** | 186 | **1.4357 %** | 0.99976 | 58.35 % | 2.478 | 78.24 | see `out_targeted.json` |
| P-COLLAPSE (family merged, published max-damage) | 187 | 1.4435 % | 1.2207 | 65.71 % | 2.957 | 76.93 | see `out_targeted.json` |

**What the realistic case does and does not do:**

- **Doublet deficit: untouched.** 0.795 % is **1.22× below** the binding German floor and
  **1.74× below** KJV. Even the *adversarial* relabel of all 450 (1.0884 %) stays below every
  English floor. Even the adversarial relabel of the **entire family** (1.4357 %) stays below
  the stale 1.50 %, below held-out English (1.483 %) and below Latin (1.425 %) — it clears only
  KJV's 1.386 %. **A pure O/A/AE confusion, however malicious, cannot carry this ciphertext to
  the English band.** That is a hard bound on the whole family, and it strengthens the
  independent-read verdict from a hand-wave to a measurement.
- **Flatness: this is the one that moves.** IoC·N goes 0.99987 → **1.01382**, crossing the
  uniform-null 99th percentile (1.00172) at **k ≈ 167** of the 450. The mechanism is obvious in
  hindsight: 306 of the 450 flips are A → O, so the perturbation *concentrates* mass rather than
  redistributing it. **This is the only channel where the located set is not inert, and it moves
  in the dangerous direction — toward English.** In magnitude it is 1.9 % of the distance from
  flat (1.00) to English (1.73), so nothing changes qualitatively, but a future lane quoting
  "IoC·N = 1.0000, flat" should know it is a 167-rune claim, not a 12,956-rune one.
- **Δ-spectrum: L2's deferred check, now run.** L2 recorded `delta_chi2/df` = 1.533 and
  max \|z\| = 2.64 "**so that a future re-read of the transcription can check whether it
  moves**". It moves: max \|z\| **2.641 → 3.137** under the full located-set flip, against L2's
  own Bonferroni bar of **3.57**. **Not crossed** — but it travels 47 % of the remaining
  distance to the bar on 450 runes, so the statistic is materially transcription-sensitive and
  L2 was right to flag it. `delta_chi2/df` moves the other way, 1.533 → 1.485.
- **Layout: inert.** Line-break doublets stay at **4/103** (4.65 % → 3.88 %, still nowhere near
  the ~22.9 % a per-line hand filter would leave, so R17/P4's power-1.000 exclusion is
  untouched). Line-initial χ² 78.66 → 82.14, i.e. L4's Arm-A1 hit gets marginally *stronger*
  and its layout explanation is unaffected.
- **Filter constants: move, and should be re-quoted with a tolerance.** `s*` 0.8129 → 0.7756,
  extra draws 373.6 → 356.0, lag-1 suppression 80.75 % → 77.26 %. L2's stated draw count is
  **373.6 ± 19.6**; a 450-rune re-read shifts the central value by **17.6**, i.e. **0.90 of its
  own stated sd**. So L2's error bar already covers the realistic transcription uncertainty —
  narrowly.

### 4.3 Dense-page concentration (pages 45–54)

The 1,993 stream positions on pages 45–54 are where every audit is weakest (R9 could not
glyph-diff them; frontB's forced segmentation failed its own control at 12.9 %). Concentrating
*all* error there is **less** damaging per rune than spreading it, not more: k\*(0.972 %) rises
from 714 to **893** (median), because the pool saturates — even corrupting **every** rune on
pages 45–54 reaches only **1.104 %**, below KJV.

**So the worst-audited 15.4 % of the book cannot, by itself, carry the doublet rate to any
English floor.** That is a bound on exactly the region the repo has been least able to check.

---

## 5. The channel nobody had measured — do the *negatives* survive?

Everything above is a property of the ciphertext. The repo's ~10¹⁰ negatives are properties of
a **decode**. `out_decode_L{120,400,12956}_*.json`.

Design: real LP1-register plaintext (L7-A power 1.00) → `encipher_keyskip(supp=0.83)` → corrupt
k ciphertext runes → decode with the **correct** key through `fastbeam` (gate-F0-identical to
`skipdecode.beam_decode`, `beam_w=400`, `max_skip=3`). **No fixed score bar is used**: the
endpoints are recovery against L2's own 0.90 gate, and correct-key p05 vs **in-lane** wrong-key
p95. (Per the round's instruction and I1's finding that each channel has its own null — the
−5.5 floor appears nowhere in this lane.)

### Full book, L = 12,956 — the real object

| k (whole book) | ε | correct score med | p05 | recovery med | graceful ideal | **derail fraction** | wrong-key med | separated |
|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| 0 | 0 | −4.103 | −4.130 | **1.0000** | 1.000 | 0.00 | −7.320 | yes |
| 50 | 0.39 % | −4.167 | −4.267 | 0.990 | 0.996 | 0.00 | −7.304 | yes |
| 100 | 0.77 % | −4.217 | −4.301 | 0.979 | 0.992 | 0.00 | −7.294 | yes |
| 200 | 1.54 % | −4.390 | −4.694 | 0.937 | 0.985 | **0.17** | −7.302 | yes |
| **450** | 3.47 % | −4.719 | −5.213 | **0.862** | 0.965 | **0.50** | −7.296 | yes |
| 900 | 6.95 % | −6.841 | −7.306 | 0.199 | 0.931 | **1.00** | −7.290 | **no** |

- **K-REC** (median recovery below L2's 0.90 gate): **k = 450**.
- **K-SEP** (correct key no longer ranks above noise): **k = 900**.

**The mechanism, and it is not the errors themselves.** "Graceful ideal" is the recovery a
decoder would get if each wrong ciphertext rune cost exactly one wrong plaintext rune
(`1 − k/L`). At k = 450 the ideal is 0.965 and the beam delivers **0.862** — the gap is the beam
**losing key synchronisation**. `max_skip` only lets the key run *ahead*; once the beam takes a
spurious skip at a corrupted rune it can never come back. At full-book length the derail
probability compounds: **0.17 at k = 200, 0.50 at k = 450, 1.00 at k = 900.**

This is the S2 channel's real curve, and it is much steeper than S1's:

| | S1 (doublet rate) | S2 (correct-key decode) |
|---|---|---|
| k = 200 | +0.085 pp, invisible | 17 % of full-book decodes derail |
| k = 450 | +0.201 pp, still 1.2× below the floor | **50 %** derail, recovery gate **fails** |
| k = 900 | still 1.3× below the floor | correct key **indistinguishable from wrong** |

**What that does and does not mean.** It does *not* void the negatives: the correct key still
scores −4.72 against a wrong key's −7.30 at k = 450, so a sweep that **ranks** would still have
surfaced it. It does mean that a sweep that **thresholds** — and the repo's sweeps all
thresholded — loses margin fast, and that L2's landmark full-book positive control
(−4.098 / 0.9997) is a **clean-transcription** result. If T1/T2 return a four-figure error
count, `R18-L2-BEAM-LENGTH-POWER` needs re-running before it can be quoted again.

Shorter windows are much more forgiving (K-REC at k = 900 for L = 400, k = 1,800 for L = 120),
because a derail costs less of a short window. The full-book number is the binding one.

### 5.1 `n_skips` — I1's language-independent discriminator is the robust one

I1 reports `n_skips` as a discriminator that does not route through the English scorer: at full
book the correct key infers **418/418 exactly** and a wrong key infers **1537** — a margin of
**1,119 draws**. It is stream-dependent, so it belongs in the map, and its curve is the
best news in this lane:

| k | inferred-`n_skips` error, median | p95 | **fraction of I1's 1,119-draw margin retained** |
|---:|---:|---:|---:|
| 0 – 100 | 0 | **0** | **100.0 %** |
| 200 | 0 | 13 | 98.8 % |
| **450** | **0** | **18** | **98.4 %** |
| 900 | 73.5 | 85 | 92.4 % |

**At the entire located-set error count, `n_skips` is still exactly right in half of all runs
and off by at most 18 of 1,119 in the worst 5 %.** Where the English score has lost half its
recovery, this channel has lost 1.6 % of its discriminating power. Its analytic sibling —
L2's 373.6 extra draws, which is just the doublet rate inverted — inherits the gentle S1 curve
and moves by 17.6 at k = 450, inside L2's own ±19.6.

**Recommendation for Phase 2, offered as a measurement not an opinion:** `n_skips` is the
transcription-robust ranking channel. If S1/S2 store it per `SWEEPROW` as I1 asks, the sweep
becomes robust to exactly the uncertainty T1 and T2 are resolving.

---

## 6. Job 4 — the decision number

### 6.1 Five estimators of E[W], the expected wrong-rune count

| estimator | value | how |
|---|---:|---|
| `E_upper_R9` | **398** | (1 − 0.9693) × 12,956 — every R9 disagreement charged to canon |
| `E_upper_frontB` | **259** | (1 − 0.980) × 12,956 — same, frontB's rate |
| `E_located` | **450** | the located O/A/AE candidate set at face value |
| `E_attributed` | **0** | the audits' own bucket attribution |
| **`E_C3_corrected`** | **0** | §6.2 — and this one is *measured* |

`E_attributed` is 0 because R9 assigns all 103 of its loci elsewhere: 15 DP edge artifacts at
`position 0, x=601`; 3 high-cost `C→I` misreads on pages that are **solved by decryption**, so
canon is proven correct there and the *read* is the wrong party; and 85 whole-line read failures
on pages 45–47. Its own sentence: *"Zero disagreements are real, localized rune-value errors in
canon."* Likewise `independent-read` finds **"no blatant single-glyph error"** among the 450.

### 6.2 C3's reader closes the argument

Round 19 lane **C3** measured an independent per-glyph band reader at **95.56 %** on the **LP2
typeface** (172/180; 95.62 % conditional on its own `RUNIC` call). That is a *reader error rate
of 4.44 %*.

Both audits disagree with canon **less often than that**:

| | disagreement with canon | reader's own error rate | implied canon error |
|---|---:|---:|---:|
| R9 template DP | 3.07 % | 4.44 % | **−1.37 pp → 0** |
| frontB validated instrument | 2.00 % | 4.44 % | **−2.44 pp → 0** |

Under `p_disagree ≈ p_reader + p_canon`, a disagreement rate *below* the reader's own error rate
implies `p_canon ≤ 0`. **The observed disagreements are fully accounted for by the instrument
and carry no evidence of canon error at all.** Before C3 this was an assertion the audits made
about their own buckets; it is now a measurement against an independently calibrated reader.

Caveat, stated because it matters: C3's 95.56 % is measured on 180 glyphs of the LP2 face, and
its `RUNIC` gate is a coin flip at ≤ 16 glyphs. It bounds the reader class, not every reader.
T1's ≥ 99 %-gated reader is a *different* instrument and its disagreements will not be
explained away this way — which is exactly why T1 is worth running.

### 6.3 The verdict, in the form fixed in §5 of the PREREG

Stratified, because a single ratio would hide the one channel that is narrow.

| channel | k\* | E[W] used | R | verdict |
|---|---:|---:|---:|---|
| **doublet deficit vs the actual O/A/AE process** | **never crosses** | 450 | ∞ | **MARGIN HOLDS** |
| doublet deficit vs uniform random, median | 714 | 398 (crudest) | **1.79** | **MARGIN NARROW** |
| doublet deficit vs uniform random, p95 | 497 | 398 (crudest) | 1.25 | **MARGIN NARROW** |
| doublet deficit, adversarial bound | 20 | 398 | 0.05 | **DOES NOT HOLD** — but see below |
| flatness (IoC·N) vs the located set | 167 | 450 | 0.37 | **DOES NOT HOLD** (moves; magnitude 1.9 % of the way to English) |
| Δ-spectrum vs the located set | > 450 | 450 | > 1 | **MARGIN HOLDS**, 47 % of the way to L2's bar |
| **full-book correct-key recovery (S2)** | **450** | 398 | **1.13** | **MARGIN NARROW** |
| `n_skips` discriminator | ≫ 900 | 450 | ≫ 2 | **MARGIN HOLDS** |
| every channel, at `E_attributed` / `E_C3_corrected` = 0 | — | **0** | ∞ | **MARGIN HOLDS** |

**Plainly.** Against the error process actually in evidence — a branch-angle confusion inside a
three-rune family, at 450 located positions — **the doublet-deficit argument does not fail at any
k, because the family cannot reach the floor even when every one of its 1,385 runes is
adversarially relabelled.** Against the crudest possible reading of the audits (398 wrong runes,
placed uniformly at random) the argument survives with a factor of 1.79, and the honest word for
1.79 is *narrow*, not *safe*. Against an adversary who chooses the positions it takes 20 runes,
and that number is a bound, not a forecast.

And with C3's reader measurement the expected count is **0**, at which point every ratio is
unbounded. **The repo's standing claim that "the transcription is not the blocker" is now
demonstrated rather than assumed — for the summary statistics. It is *not* demonstrated for the
decode channel, where a four-figure error count would void L2's full-book control and cost every
sweep real margin.**

---

## 7. Coverage × power

**Coverage.** 62/62 ledger entries and 17 synthesis claims classified, 0 UNKNOWN. 7 perturbation
models × 9–14 k values × 400 trials on the cheap channels (≈ 20,000 perturbed streams, each
SHA-256'd); 3 segment lengths × 14 k values × 60–120 replicates on the decode channel; the
targeted arm's positions are **exhaustively** enumerated (all 450, all 1,385) rather than
sampled, and its worst case is computed exactly rather than estimated.

**Power.** PC-1 proves the instrument reports a planted flip to its closed form exactly at every
k. PC-3 reproduces 13/13 published statistics. `gate_F0` re-verified in-lane at 8.88e-15. The
`P-COLLAPSE` control reproduces the repo's only previously published sensitivity figure. The
instrument can see what it is hunting.

**The three conditionals, per doctrine Q4:**

1. **Perturbation model.** Covered: uniform random; O/A/AE at the 450 located positions in both
   the recorded and the adversarial direction; O/A/AE anywhere in the 1,385-rune family;
   dense-page concentration; the adversarial doublet-maximiser; family collapse.
   **NOT covered: insertions, deletions, line-order and segmentation errors.** Those change `n`,
   re-index every downstream position and every S3 layout statistic, and are strictly more
   damaging than substitution. Ledger items **B-23** (separator audit, 170 of 604 lines, 19
   disagreements unread) and **H-02** (full-corpus whitespace re-audit) sit in exactly that class
   and this lane bounds neither. **That is the gap this lane most wants closed.**
2. **Decoder transition model.** The decode arm uses `encipher_keyskip` → `fastbeam`
   (`max_skip=3`), which per L7-B is exact for one rejection-loop implementation and **does not
   cover `skip_by_two` or free drift**. I1 has since repaired that; the derail curve in §5 should
   be re-measured under `driftbeam`'s `drift_rec` preset, whose larger skip budget may be either
   more robust (it can absorb a spurious advance) or less (it can absorb a *wrong* one). This
   lane does not know which, and says so.
3. **Adjudicator register.** English quadgram only, `LP1_REAL` plaintext. Per L7-A that is power
   1.00 for this register and as low as 0.00 for others. The §5 curve is an **English-register**
   curve. §5.1's `n_skips` channel is the register-free one and is reported separately for
   exactly that reason.

**What would reopen this lane.** (a) T1 or T2 returning a disagreement count with a *non*-O/A/AE
component — the §3.2 P-RAND row is then the one to read, not P-OAE450. (b) Any evidence of
insertion/deletion errors, which this lane does not bound at all. (c) Re-running §5 under I1's
repaired decoder. (d) A resolution of the L2-A / L7-C.2 conflict in §2.1, which decides whether
the headline k is measuring a load-bearing step or a superseded one.

---

## 8. For T1 and T2 — read your number off the x-axis

Neither lane had published when this was written, so the curves are stated so their real counts
can be substituted directly. Take your measured count of wrong runes on pages 0–54, `W`:

| if W is… | doublet deficit | flatness | full-book correct-key decode |
|---|---|---|---|
| **≤ 100** | inert (< 0.68 %) | inert | inert — recovery 0.979, `n_skips` exact |
| **100 – 450, inside the O/A/AE family** | inert — cannot reach any floor | IoC·N leaves the flat band above ~167 | 17–50 % of full-book decodes derail |
| **100 – 450, outside the family** | ≤ 0.865 %, still below 0.972 % | inert | as above |
| **450 – 700** | approaching the German floor at the p95 | — | recovery gate fails; still ranks above noise |
| **≥ 900** | crosses German; still below KJV until ~1,750 | — | **correct key no longer separable — every S2 negative needs re-running** |

`out_summary.json → doublet_curves` and `ioc_flatness.curves` hold every point with p05/p95
bands and a SHA-256 per row.

---

## 9. Bounds, not verdicts

This lane measured **sensitivity**, not truth. It does not say the transcription is right — it
says what changes if it is wrong, and by how much. The summary-statistic claims are robust to
every error process in evidence and to the crudest upper bound the audits admit; the decode
channel is not comfortably robust, and the substitution-only assumption is the largest thing
left uncovered.

Artifacts: `PREREG.md` · `dependency_map.json` · `t3_lib.py` · `t3_baseline.py` ·
`t3_sensitivity.py` · `t3_targeted.py` · `t3_decode.py` · `t3_depmap.py` · `t3_summary.py` ·
`out_baseline.json` · `out_random.json` · `out_targeted.json` · `out_decode_L120_LP1.json` ·
`out_decode_L400_LP1.json` · `out_decode_L12956_KJV.json` · `out_summary.json` · `ledger.json`.

Reproduce:
```bash
cd liber-primus/analysis/round19/T3
PYTHONUTF8=1 python3 t3_baseline.py     # PC-3 + PC-1 + the map gate
PYTHONUTF8=1 python3 t3_sensitivity.py  # P-ADV, P-RAND, P-DENSE
PYTHONUTF8=1 python3 t3_targeted.py     # P-OAE450, P-OAE450R, P-OAEFAM, exact points
PYTHONUTF8=1 python3 t3_decode.py 400 60 LP1
T3_KBOOK=0,50,100,200,450,900 PYTHONUTF8=1 python3 t3_decode.py 12956 6 KJV
PYTHONUTF8=1 python3 t3_depmap.py && PYTHONUTF8=1 python3 t3_summary.py
```
