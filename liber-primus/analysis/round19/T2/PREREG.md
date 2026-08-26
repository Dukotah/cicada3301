# T2 — THE DENSE PAGES · PRE-REGISTRATION

_Round 19, transcription phase. Written **before any measurement was scored**.
Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md). Sibling lane: **T1**
(per-rune reader + the 450 located O/A/AE disagreements) — T2 does **not** touch
those 450; that adjudication is T1's._

**Trust anchor (before):** `python3 liber-primus/tests/validate.py` — recorded in
`RESULTS.md` §0.

---

## 0. What this lane is for

Four ledger items sit unfinished, and all four are about the same thing: **the
transcription's support is uneven, and the dense OTP pages 45–54 — the pages carrying
the unsolved ciphertext — are where every audit was weakest.**

| ledger | state on entry |
|---|---|
| **A-01** | Round 9 Track TEMPLATE, "the only genuinely from-scratch re-transcription", `partially-run`. Stage 3 exists on disk (`retranscribe/diff_report.json`, 96.93 % on 232 lines) but was never written up as a verdict, and it covers **38.4 % of lines**. |
| **A-05 / B-23** | Separator audit: **19 rune-count-exact lines disagree on separator count**, listed as "the correct shortlist for a human re-read". Never re-read, several rounds running. |
| **R12-frontB** | `inconclusive`. The forced re-segmentation instrument **fails its own control at 12.9 %** and therefore certifies nothing about 45–54. |

The common cause is stated plainly in frontB's own results: **the dense lines cannot be
segmented blind.** Ornament strokes, `·` separators and touching runes make the glyph
count unrecoverable from the ink, so every instrument that had to *discover* the
segmentation collapsed on exactly the pages that matter.

**T2's move is to stop discovering the segmentation.** The question a transcription audit
actually needs to answer is not "read this line blind" — it is **"does canon's rune
sequence explain this line's ink better than any single-rune alternative?"** That question
does not require the segmentation to be discovered, because the token *count* and *order*
come from canon and only the *identity* at each slot is put at risk. It is the standard
forced-alignment framing, and it has never been run on this book.

---

## 1. Instrument — WFA (forced alignment) + leave-one-out substitution probe

### 1.1 Components, all inherited and already validated

| piece | source | why it is trusted |
|---|---|---|
| 29 rune templates | `analysis/retranscribe/templates.npz` | built **label-free** (Round 9 stage 1); Round 8 measured the median glyph's nearest-neighbour pixel Hamming distance at **0.0000**, so templates are exact, not fuzzy |
| class → rune bijection | `analysis/retranscribe/diff_report.json` `mapping` | a single 29→29 permutation, clean bijection, fitted once in R9 |
| per-column mismatch + DP constants | `analysis/retranscribe/read.py` (verbatim: `dy ∈ {−3,−1,0,1,3}`, blank-skip `colink·3.0 + 0.5`, per-glyph prior `+6.0`) | the instrument that **passes** control at 98.0 % in its native regime |
| glyph-width prior | `round18/L4-forcing/results_confound_layout.json` | fitted widths correlate **+0.879** with `BabelStoneRunicBeorhtnoth.ttf` advance widths — external, ciphertext-independent validation |
| ornament stripping | `round12/frontB` measurement: runes are components of height ≈95–132 px, ornaments ≈41–91 px, dots ≈7–10 px | visually verified in frontB |

### 1.2 The forced alignment

For a line band `B` and canon token sequence `T = t_0 … t_{L−1}` (runes plus the `-` and `.`
separators), find start columns `x_0 ≤ … ≤ x_{L−1}` with `x_{j+1} ≥ x_j + w(t_j)`, minimising

```
C(T) = Σ_j  mismatch(t_j, x_j) + 6.0        (per-glyph prior, R9 constant)
     + Σ_{x in gaps}  colink(x)·3.0 + 0.5    (blank-skip cost, R9 constant)
```

This is exactly R9's DP with the emission alphabet at step *j* restricted to `{t_j}`.
It is **not** frontB's forced cut: frontB forced a *number of pieces* and let the cuts fall
where they may; WFA forces the *identity sequence* and lets the ink choose the cuts.

### 1.3 The leave-one-out substitution probe

Compute `alpha[j][x]` (best cost of tokens `0…j−1` ending at column `x`) and `beta[j][x]`
(best cost of tokens `j…L−1` starting at `x`) once per line. Then for every slot *j* and
every rune *r*:

```
C_j(r) = min_x  alpha[j][x] + mismatch(r, x) + 6.0 + beta[j+1][x + w_r]
```

Per slot this yields:

- `loo_rune[j]` = `argmin_r C_j(r)` — **the ink's own choice at that slot**, with canon
  supplying only the surrounding context and the token count;
- `delta[j]` = `C_j(canon_j) − min_r C_j(r)` — how much worse canon is than the ink's choice;
- `margin[j]` = `C_j(2nd best) − C_j(best)` — how decisive the ink is.

**Coverage:** every slot of every line, dense or not — `13,136` rune slots. This is the
mechanism by which T2 goes past Round 10's 38.4 % bound: no count-exactness is required.

**Cost:** `13,136 × 29 ≈ 3.8 × 10⁵` forced alignments, computed in `O(L·W·29)` per line by
forward–backward. Fully enumerable, minutes of compute.

---

## 2. Positive controls — fixed now, before measuring

frontB's failure was *not* having these. All three are registered with thresholds.

### C1 — ground-truth control (the gate)

**LP2 pages 56 and 57** (`corpus/E-tooling/vendor/…/liber-primus-complete/73.jpg`,
`74.jpg`; `lp.corpus` labels `'73.jpg - 56.jpg'`, `'74.jpg - 57.jpg'`; canon segments 55
and 56 of `krisyotam_runes.txt`; **180 runes**). These are the **only** pages whose
plaintext is known **by decryption** *and* whose typeface is the LP2 face of pages 0–54
(C3/L3 measured the five LP1 solved pages at 42.6 % — outside the template domain — and
these two at 95.56 %).

> **Statistic:** `loo_agreement` = fraction of slots where `loo_rune[j]` equals the
> decryption-proven rune.
> **PASS at ≥ 0.90.** (frontB's forced instrument: 0.129. R9's native regime: 0.980.)

### C2 — analytic plant recall

Planting a single wrong rune at slot *j* leaves every *other* token unchanged, so the LOO
probe's argmin at slot *j* is **identical** whether or not the plant is present. Therefore

> **recall(recover the original | a single-rune error is planted at slot j)
> = `loo_agreement` on that stratum**, exactly,

and detection-only recall (`argmin ≠ planted`) is ≥ that. Reported **per stratum**:
solved LP2 pages, pages 0–44, **pages 45–54**.

### C2′ — ink-splice plant (the control frontB needed and never ran)

C2 is analytic; C2′ is physical, and it runs **on the dense pages themselves**. For a
random slot *j*: take the real page ink, overwrite the pixels of slot *j*'s aligned x-span
with a *different* rune's template bitmap, then run the probe with **uncorrupted canon**
tokens. Record whether `loo_rune[j]` equals the spliced rune (recovery) and whether it
differs from canon (detection).

> **Registered sample:** 200 splices per stratum (solved / 0–44 / 45–54), splice rune drawn
> uniformly from the 28 non-canon runes.
> **Reported as the lane's power number.** No threshold is attached to C2′ — it *is* the
> measurement — but see the gate in §4.

### C3 — false-positive rate and the flag threshold τ

On **uncorrupted** canon, `flag(j) ⇔ delta[j] > τ`. Canon on LP2 p56/p57 is proven correct
by decryption, so **every flag there is a false positive**. τ is fixed as the smallest
value giving **FPR ≤ 1 %** on those two pages, and the **same τ** is then applied to
pages 45–54. τ is chosen from the solved pages only, never re-tuned after seeing 45–54.

### C4 — separator control (for A-05 / B-23)

Delete one `-` token from a solved-page line's canon sequence and re-align. PASS if the
alignment residual of the true separator count is lower than the residual of the deleted
count on ≥ 8 of 10 planted lines.

---

## 3. The Aiming Test (doctrine §1)

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit is a slot *j* on a line whose alignment residual is in-distribution, where
`loo_rune[j] ≠ canon_j` and `delta[j] > τ`. The recognizer is written before the search and
its recall against a **physically planted** single-rune error, in the exact shape a real
transcription error takes, is measured by **C2′** on the target pages themselves. If C2′
recall on 45–54 is low, the lane reports a *bound* on detectable error, not a certification
— this is stated in §4 and is not negotiable after the fact.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Four, each with a path:
1. `analysis/retranscribe/FINDINGS.md` — glyph-level adjudication reliably covers **232/604
   lines (38.4 %)**, and states the OTP pages are "exactly where the independent read is
   weakest". **61.6 % of lines have never been per-rune audited by anything.**
2. `round12/frontB/RESULTS.md` — the only instrument ever pointed at 45–54 **failed its own
   control at 12.9 %**, so those pages carry *no* passing per-rune audit at all. This is a
   coverage hole, not a confirmed negative.
3. `round18/L4-forcing/RESULTS.md` §2 T1 — a glyph-width table externally validated at
   **corr = +0.879** against an independent font, plus a greedy line-breaker that reproduces
   **53.5 %** of line lengths exactly and **82.5 %** within ±1. The layout is *predictable*,
   which is precisely the ingredient frontB lacked.
4. Round 8 geometry — the median glyph has a **pixel-identical twin** (NN Hamming 0.0000).
   Template matching on this render is a lookup, not a recognition problem.

**Q3 — Is the space bounded, and by what?**
**Enumerable.** `13,136` canon rune slots × 29 alternatives = **380,944** forced
alignments — the complete single-substitution neighbourhood of the transcription. Plus 19
separator lines × a small count-variant set. Nothing is sampled except the C2′ splice
positions (600 of them, stated as a sample).

**Q4 — The three conditionals the negative will carry.**
1. **Hypothesis space swept:** *single-token substitutions* at each canon slot, and
   separator-count variants on the 19 A-05 lines. **Not covered:** insertions, deletions,
   transpositions, multi-rune errors, and whole-line omissions — except where explicitly
   tested by the residual statistic.
2. **Transition model:** left-to-right, non-overlapping, canon-ordered token placement with
   the R9 DP constants. It **cannot** represent overlapping/kerned glyph pairs, ligatures,
   reordering, or a rune rendered at a size outside the template's.
3. **Adjudicator register:** pixel mismatch against the R9 template library at *this* render
   (Ghostscript 400 dpi → ImageMagick q92, 2400×3600, per `round18/L1-toolchain`). Its known
   blind spot is the shape-confusable futhorc families (**U↔Y, O/A/AE, L↔W, C↔I**), which
   are reported as a separate column everywhere and never folded into the headline.

**Q5 — What single observation kills the lane at 10 % of budget?**
**C1 < 0.60.** If the probe cannot read the two solved LP2 pages, it has no business
speaking about 45–54; the lane then stops building and reports the render-limited bound
("what render would be needed") instead of a re-segmentation.

---

## 4. Gate — what the instrument is allowed to conclude

Registered now, not after:

| C1 | C2′ recall on 45–54 | what T2 may write |
|---|---|---|
| ≥ 0.90 | ≥ 0.50 | a **certification-strength** statement about single-rune errors on 45–54, with FPR from C3 |
| ≥ 0.90 | < 0.50 | a **measured bound only**: "power to detect a planted single-rune error on the dense pages = *x*", and the residual that leaves |
| < 0.90 | — | **INCONCLUSIVE**, reported the way frontB was, and the lane pivots to the render question |

**Distinguishing segmentation from rune identity — everywhere.** Every disagreement is
labelled with exactly one of:
- **SEG** — the alignment residual for the whole line is out-of-distribution, or the slot
  sits inside a run where alignment slipped (adjacent slots also flagged);
- **ID** — an isolated slot, in-distribution line residual, `delta > τ`;
- **CONF** — an ID case whose canon/probe pair is in a known confusable family.

Only **ID and not CONF** counts as a candidate canon error. The repo has repeatedly
conflated SEG with ID; this lane will not.

---

## 5. Jobs, and the artifact each produces

| # | job | artifact | statistic that closes it |
|---|---|---|---|
| 1 | **Finish A-01** — Round 9 Track TEMPLATE to completion | `out_a01.json` | per-page agreement of the independent read vs canon, with SEG/ID/CONF split |
| 2 | **Cover the 61.6 %** | `out_coverage.json` | slots adjudicated / 13,136, and for every unadjudicated slot a *measured reason* |
| 3 | **Settle frontB** | `out_frontb.json` | C1, C2′ per stratum, C3 τ and FPR, flags on 45–54 |
| 4 | **Close A-05 / B-23** | `out_separators.json` | all 19 lines adjudicated, each into one of {ornament/edge-dot contamination, title mark, genuine separator error, unresolved-at-this-render} |

Plus: `ledger.json` moving **A-01**, **A-05**, **B-23**, **R12-frontB** to measured statuses.

---

## 6. Standing rules for this lane

- Write only inside `round19/T2/`. Crops are rebuildable and gitignorable. No `git commit`.
- Trust anchor before **and** after (`tests/validate.py`).
- **Bounds, not verdicts** (doctrine R7). Nothing here says "closed".
- Report **coverage × power** (doctrine R2). A coverage number without its power is not a
  result.
- Any threshold change is an appended dated addendum with the reason, never an edit.

### Addendum policy on T1
T1 was building a per-rune reader with a measured confusion matrix. At the time T2 started,
`round19/T1/` **did not exist on disk**. T2 therefore builds its own probe, states so here,
and does **not** touch the 450 located O/A/AE disagreements. If T1's confusion matrix lands
later, T2's `CONF` column is the natural place to cross-check it.
