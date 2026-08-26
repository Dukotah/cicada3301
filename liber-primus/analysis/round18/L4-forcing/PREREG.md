# Round 18 — Lane L4 (FORCING) — PRE-REGISTRATION

_Written 2026-08-25, **before any test was run**. Ledger item **C-02** (`status: never-run`,
"Proposed with a hard gate; no script and no result anywhere")._

Source of the item: `liber-primus/analysis/campaign14/REDTEAM-PROPOSALS.md`, proposal
*"Preserved plaintext metadata: word-length / punctuation / layout channel"*, sub-test **(c)**:

> uniformity test on line-initial, word-initial, and page-initial ciphertext runes vs the global
> uniform distribution (any forcing = non-uniform) … falsifiable signal: **(c) p < 0.001
> non-uniformity at line/page starts.**

That gate (`p < 0.001`) is **inherited, not chosen here**, and is not editable after seeing a result.

---

## 1. Hypothesis

**H1 (forcing).** The author constrained the *ciphertext* so that a ciphertext-visible positional
subset — line initials, page initials, word initials, or their finals — spells or encodes
something. If so the constraint is visible **with no key at all**, because it is a property of the
emitted symbols rather than of (plaintext, key).

**H0 (no forcing).** Every rune of LP2 pages 0–54 is an unconstrained draw from the keystream
process, modulated only by the single already-measured constraint: the memoryless, unscoped,
lag-1 anti-repeat filter at suppression s ≈ 0.8075 (`round17/SYNTHESIS.md` §2, item D-01).

**Why this is worth running now, and was not obviously worth running in campaign 14.** Round 17
proved the anti-repeat filter is *machine-applied* at ≥0.99 power. A machine-applied anti-repeat
filter **is** a ciphertext-level constraint enforced by a rejection sampler. The author is therefore
demonstrably a person who wrote code to constrain the ciphertext. H1 is the hypothesis that the
sampler enforced a *second* predicate. This is the only attack in the repo that requires no key
hypothesis whatsoever, so it is orthogonal to every sweep here and cannot be pre-empted by them.

**Three distinct mechanisms of forcing, which leave different signatures.** Stated in advance
because they determine which arm is the sensitive one:

| mechanism | how the author did it | signature |
|---|---|---|
| **M1 direct assignment** | write the wanted rune, back-derive the key symbol | Arm A only (subset distribution ≠ text distribution) |
| **M2 rejection over keystream** | re-roll the draw until the forced position emits the wanted rune | Arm A, **plus Arm C**: the forced position also has to satisfy the anti-repeat predicate, so the two constraints interact |
| **M3 soft forcing** | force only *some* lines (f < 1) | Arm A, attenuated by f — this is what the power curve is for |

Under M2 there are exactly two ways the conflict "the forced rune equals the previous rune"
resolves, and both are measurable: the author lets the doublet through (⇒ **excess** doublet rate
at the forced position) or lets the filter win / re-rolls upstream (⇒ **deficit**). Either
direction is evidence; only "identical to the within-line rate" is consistent with H0.

## 2. Data

- `liber-primus/data/krisyotam_runes.txt`, pages 0–54 only (`%`-delimited, first 55 segments).
- Structure measured before pre-registration (these are counts, not results):
  **12,956 runes / 55 pages / 594 lines / 3,316 words / 175 `.`-delimited sentence units.**
  The 12,956 matches `lib_numchannel.unsolved()` exactly, so the object under test is the
  ciphertext pinned by `PROBLEM.json`.
- Delimiters: `-` and `.` = word boundary, `/` = line break, `%` = page break, `&`/`$`/`§`/digits
  = non-rune marks (18/9/1/6 occurrences) that are *not* treated as boundaries.

## 3. Instruments and pass/fail thresholds

### Multiplicity correction (declared here, applied verbatim later)

**21 pre-registered tests**: 10 in Arm A, 6 in Arm B (one per family, each family internally
multiplicity-free by construction — see below), 5 in Arm C. Bonferroni over all 21 at the
inherited family gate of 0.001:

> **α_test = 0.001 / 21 = 4.762 × 10⁻⁵.**

Any test with p < 4.762e-5 is a **HIT** and escalates. p in [4.762e-5, 0.001) is reported as
`SUBTHRESHOLD` and escalates only if a second, independent test also lands there. p ≥ 0.001 is
NEGATIVE *for that statistic at that power*.

### Arm A — uniformity of positional subsets (the literal C-02 test)

Ten subsets, each a list of positions in the 12,956-rune stream:

| id | subset | n |
|---|---|---|
| A1 | line-initial | 594 |
| A2 | line-final | 594 |
| A3 | word-initial | 3,316 |
| A4 | word-final | 3,316 |
| A5 | page-initial | 55 |
| A6 | page-final | 55 |
| A7 | sentence-initial (after `.` or page start) | 175 |
| A8 | sentence-final | 175 |
| A9 | line-second (adjacency control) | 594 |
| A10 | line-penultimate (adjacency control) | 594 |

Statistic: **χ² goodness-of-fit, 28 df**, of the subset's 29-bin rune histogram against
(a) the **full-text empirical distribution** of all 12,956 runes, and separately (b) **uniform**
(the literal wording of the proposal; the two are nearly identical here since LP2's IoC·N ≈ 1.000,
but both are reported).

p-value: **empirical, from 200,000 size-matched position resamples** drawn without replacement from
the 12,956 positions — this is the "size-matched null built from the ciphertext's own model" the
task requires, and it automatically absorbs the ciphertext's own histogram. Resolution floor
5 × 10⁻⁶, below α_test. The asymptotic χ² p is reported alongside as a cross-check.

A second null is run for A1/A2/A5/A6: **synthetic streams from the fitted generative model**
(uniform draws under a memoryless lag-1 anti-repeat filter at s = 0.8075, same line/page geometry),
2,000 replicates, same statistic. If the two nulls disagree the *more conservative* p is used.

### Arm B — the subset read as a message (goes past the original proposal)

Six families. Each family's gate is on a **max statistic over all variants inside the family**, so
multiplicity inside a family is handled exactly by the null rather than by a Bonferroni factor:

| id | family | variants inside the family |
|---|---|---|
| B1 | line-initial sequence (594) | forward/reverse × identity/Atbash × 29 Caesar shifts = 116 |
| B2 | per-page acrostic, down and up | 55 pages × 2 directions |
| B3 | diagonal readings | per-page main + anti diagonal, plus global diagonal |
| B4 | first rune of every N-th line, N = 2…12 | all N, all phases, both directions |
| B5 | page-initial (55) and page-final (55) strings | 2 strings × 116 shift/Atbash variants |
| B6 | word-initial (3,316) and word-final strings | 2 strings × 116 variants |

Scorer: `lp.score.Quadgram.score_norm` on the **Gematria Primus transliteration of rune indices**
(never on a re-parsed string — AGENTS.md §5, seven runes are two characters). Where a keyed read is
meaningful the skip-aware beam (`campaign18_skip.skipdecode.beam_decode`) is used, not rigid
alignment (AGENTS.md §4 lesson 2).

Null: **2,000 replicates** in which the same pipeline (identical variant set, identical max) runs on
size-matched sequences drawn from the ciphertext's own positions. Because 2,000 replicates cannot
resolve 4.762e-5 empirically, the gate is declared as a conjunction:

> **B fires iff** the observed max (i) exceeds **all 2,000** null maxima, **and** (ii) exceeds the
> Gumbel bar fitted to those 2,000 null maxima at α_test = 4.762e-5, **and** (iii) exceeds
> `benchmark/null.py: threshold_for(n_variants_total, segment_len)` where a beam score is used.

Any B family that clears all three goes to `liber-primus/verify_solution.py`. **A decode that
"looks English" is not a result** (AGENTS.md §3).

### Arm C — excess rejection conditioned on position-within-line (the sharpest sub-test)

This is the measurement nobody in this repo has made. Round 17 measured only that 4 of the 86
doublets cross a line boundary (4.65 % vs a 4.58 % base) — a scope test at n = 86, which is a
different and much weaker question than "is the filter's *residual rate* a function of
position-within-line".

| id | test | statistic | null |
|---|---|---|---|
| C1 | doublet rate by within-line position bucket {p=0 i.e. cross-line, p=1, p=2–4, p≥5} | 2×4 contingency χ² | 200,000 label permutations of line geometry |
| C2 | doublet rate by within-word position bucket {cross-word, p=1, p≥2} | 2×3 χ² | same |
| C3 | suppression s estimated per bucket, Wilson 95 % CI; H0: s equal across buckets | likelihood-ratio G² | parametric bootstrap from the fitted filter model, 20,000 reps |
| C4 | difference channel d = (x[i] − x[i−1]) mod 29, 29 bins, at line boundaries vs within-line | χ² homogeneity, 28 df | 200,000 permutations |
| C5 | mutual information between line-final rune and the next line-initial rune | MI in bits, bias-corrected | 200,000 permutations of line-initial labels |

Direction is recorded but the gate is **two-sided**: excess *or* deficit at the line boundary is
evidence, per §1's M2 table.

## 4. Positive control — mandatory, and the power curve is the deliverable

No arm's null is trusted until the same code fires on a planted signal.

**Construction.** Synthesise a 12,956-rune stream with LP2's exact line/page/word geometry from the
H0 generative model (uniform draws, memoryless lag-1 anti-repeat rejection at s = 0.8075 — validated
by reproducing LP2's observed 86 doublets and flat IoC before use). Then force line initials to
spell a fixed 594-rune phrase (`THEPRIMESARESACRED…` repeated, mapped through
`gematria.keyword_to_indices`), forcing a random fraction **f** of the 594 lines. Forcing is
implemented **both ways** — M1 direct assignment and M2 re-roll-until-match — and both are measured,
because they are different generative processes and Arm C only responds to M2.

**Power curve.** f ∈ {1.00, 0.80, 0.60, 0.40, 0.30, 0.20, 0.10, 0.05, 0.00}, **200 replicates each**.
Report, per arm:
- detection rate at α_test = 4.762e-5 (this is the power),
- the smallest f at which power ≥ 0.80 (the lane's sensitivity floor),
- the rate at **f = 0.00**, which is the measured false-positive rate and must be ≈ α_test.

**A negative from this lane is only reportable together with that curve.** If power at f = 1.00 is
not ≥ 0.99 the instrument is declared broken and the null is not reported as a negative
(AGENTS.md §4 lesson 1; Round 18 rule 2).

A second control is run for Arm B: plant an actual English acrostic (real plaintext in the line
initials) and confirm the scorer + max-null pipeline recovers it above the declared bar.

## 5. What a HIT does and does not mean

A hit in Arm A says a positional subset is distributionally special. It does **not** say the puzzle
is solved, and no solve will be declared in this lane. Any Arm B family that clears its bar is
handed to `liber-primus/verify_solution.py --key-module`, and its verdict — including FAIL — is
reported verbatim. Per Round 18 rule 6 the lane ends with coverage and non-coverage, and the words
"exhausted", "closed" and "unsolvable" do not appear in its results.

## 6. Files

- `parse_structure.py` — geometry extractor (pages → lines → words → positions)
- `armA_uniformity.py`, `armB_message.py`, `armC_rejection.py`
- `control_power.py` — synthesiser + power curve
- `RESULTS.md`, `ledger.json`
