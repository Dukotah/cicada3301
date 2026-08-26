# R1 — RED-TEAM ROUND 19 — PRE-REGISTRATION

_Written 2026-08-26, **before any measurement**. Lane R1 of `round19/CAMPAIGN-PLAN.md`.
Binding: `liber-primus/ARMADA-DOCTRINE.md` (rule **R6**)._

> **Target.** Not the cipher. **This round.** Specifically: the premise that a drift-tolerant
> decoder (I1), a multi-register panel (I2) and recalibrated nulls (I3) will repair the
> instrument enough to make a Phase-2 sweep of G1–G4 worth its budget; and the L1 prior that
> justifies G1–G4 at all.
>
> Verdict vocabulary is **FOUND-ERROR** / **NO-ERROR-FOUND**. Never "confirmed", never
> "validated".

---

## 0. State of the round at pre-registration time

`round19/` contains `CAMPAIGN-PLAN.md` and an **empty** `G1/` directory. **I1, I2 and I3 have
not landed.** Per the task's rules of engagement, where a lane has no artifact this lane attacks
its **specification** in `CAMPAIGN-PLAN.md` and records what could not be tested. If I1/I2/I3
files appear mid-run they will be attacked as found and the fact noted with a timestamp.

## 1. Rules of engagement I bind myself to

1. **Own instruments.** No I1/I2/I3 harness is used to test I1/I2/I3. My beam decoder, my
   register LMs, my null generator, my Gumbel fits are written in `r1_lib.py` from the
   primitives (the gematria table, the quadgram count file, the pinned rune stream). The repo's
   `skipdecode.beam_decode` is used **only as a cross-check reference point**, never as the
   measuring device for a claim about I1.
2. **No threshold is edited after a result.** Addenda are appended and dated.
3. Scoring on **rune indices / transliteration characters**, never on a rune string (7 of 29
   runes are 2 characters).
4. Trust anchor `python3 liber-primus/tests/validate.py` run **before** (done: ALL VALIDATIONS
   PASSED 5/5) and **after**.
5. Nothing outside `round19/R1/` is written. No `git commit`.

---

## 2. THE AIMING TEST (doctrine §1) — five answers

**Q1 — What would a hit look like, and would this instrument recognise it?**

A "hit" for this lane is *an error in Round 19's own reasoning*, in one of four concrete shapes:
(a) a permissiveness setting at which I1's wrong-key null overtakes its correct-key signal;
(b) a panel-selection correction whose false-positive or false-negative rate is mis-stated;
(c) an inference step in the L1 prior that has an untested alternative explanation, or a
weighting with no derivation; (d) an arithmetic inconsistency between the round's stated plan
and the resources the plan implies.

The recognizers are written **before** the searches, in §3–§6 below, each with a numeric
trigger. Positive controls: for (a) I plant the *known* failure L7-B found (`skip_by_two` at
−6.90 / 25.8 % recovery under the exact-transition beam) and require my independent decoder to
reproduce it within 0.5 of score before I trust any of my own permissiveness numbers — if my
instrument cannot re-find L7-B's hole, my frontier is fiction. For (b) I plant a *genuine*
non-English plaintext and require the panel to see it before I claim anything about how it
handles noise. For (c) the control is a positive reproduction: the alternative pipeline must
produce the LP2 marker vector on this machine, not merely be argued for.

**Q2 — What measured fact raises this lane's prior above the flat rate?**

Two, both with paths:
- `round12/D3/RESULTS.md` and `round18/L7-redteam/RESULTS.md` — the two red-team lanes this
  project has run **both returned FOUND-ERROR**, and both found errors of the *same shape*: a
  conditional measurement written up as an unconditional one. The base rate of "this repo's
  load-bearing claims contain a scope overreach" is, on the available sample, **2/2**.
- `round18/L7-redteam/RESULTS.md` §A.4 already documents that the naive multi-register
  statistic is confounded by selection — i.e. the exact machine I2 proposes to build has a
  known-in-advance confound, and Round 19's plan allocates it one line ("plus the four
  language-agnostic statistics") with no correction specified.

**Q3 — Is the space bounded, and by what?**

Bounded and **enumerable**: the objects under attack are 3 lane specifications, 1 campaign plan,
1 prior with 11 ranked rows and 10 supporting facts, and a decoder transition relation with a
2-dimensional permissiveness parameter (`model` ∈ 5 values × `max_skip` ∈ 1..6). The
measurement space is 5 × 6 = 30 decoder configurations × {baseline plant, `skip_by_two` plant,
free-drift plant, real LP2 ciphertext} × {correct key, ≥200 wrong keys}. That is a few times 10⁴
decodes — affordable, and completely enumerated, not sampled.

**Q4 — What are the three conditionals my negative will carry?**

If any sub-attack returns NO-ERROR-FOUND, it carries:
1. **key space** — my wrong-key null is uniform-random mod-29 keystreams plus the linear key
   L7 used; it does not cover structured wrong keys (near-misses, off-by-one offsets of the
   correct key), which are the wrong keys a real sweep actually generates most of;
2. **decoder transition model** — the five transition families in §3; a construction outside
   all five is outside my measurement too;
3. **adjudicator register** — my panel is 9 registers built from the corpora this repo holds;
   Greek, Hebrew, Norse, constructed languages and non-linguistic payloads are outside it, and
   B6 already proved the last class undetectable in principle.

**Q5 — What single observation would make me abandon a sub-attack at 10 % of budget?**

- **A** — if my independent decoder fails its L7-B reproduction control (`skip_by_two` correct
  key must score below −6.4 with recovery below 40 % under the exact-transition model at
  `max_skip`=3), I stop and report that I could not build a trustworthy instrument, rather than
  publishing a frontier from a broken one.
- **B** — if fewer than 6 of the 9 registers produce an LM with measurable discrimination
  (planted correct-register text scoring ≥ 1.0 above uniform-rune text on its own model), the
  panel attack is unbuildable from this repo's corpora and I say so instead of reporting noise.
- **C** — if Ghostscript, ImageMagick and `jpegtran` are not all available under WSL, the
  positive-control arm of C is dead and C reduces to a documentary audit, explicitly labelled.
- **D** — if measured decode throughput implies the plan's "enumerable in minutes" spaces are in
  fact enumerable in minutes through a drift-tolerant decoder, D-i is dead on the spot.

---

## 3. Sub-attack A — I1's permissiveness

### A.0 The claim under attack

`CAMPAIGN-PLAN.md`, lane I1: *"Generalise the beam's transition relation to cover `skip_by_two`,
free drift, and unrepresentable key advances — **without losing power on the baseline
construction or admitting wrong keys**."* The parenthetical is the entire load-bearing content
and the plan offers no evidence it is achievable.

### A.1 Instrument (mine)

`r1_lib.py` — an independent beam decoder with an explicit, parameterised transition relation.
Accepted key index `acc = pa + 1 + d`; five families:

| model | admissible `d` | constraint on skipped key positions `m ∈ (pa+1 … acc−1)` |
|---|---|---|
| `exact` | 0 … `max_skip` | **every** `m` must satisfy `(p − sign·K[m]) mod 29 == c_prev` |
| `by2` | 0, 2, 4 … 2·`max_skip` | only `m` at **even** offset from `pa+1` constrained; the rest free |
| `union` | `exact` ∪ `by2` | as above, per branch |
| `free` | 0 … `max_skip` | **none** — full drift tolerance |
| `freepen` | 0 … `max_skip` | none, but −λ per skipped position (λ ∈ {0.25, 0.5, 1.0}) |

Score is accumulated incrementally over transliteration characters from a quadgram table I load
myself from `data/english_quadgrams.txt`; reported on the project's `score_norm` scale
(total ÷ (n_chars − 3)) so numbers are comparable to the ledger's −4.0 / −5.5 / −7.5 bands.

### A.2 Positive controls (must pass before any frontier is reported)

- **PC-A1 — reproduce the baseline.** `exact`, `max_skip`=3, correct key, `encipher_keyskip`
  plant at supp=0.83, L=120: median `score_norm` in **[−4.6, −3.9]** and rune recovery ≥ 0.95.
  (L7 measured −4.20 / 100 %.)
- **PC-A2 — reproduce L7-B's hole.** `exact`, `max_skip`=3, correct key, **`skip_by_two`** plant:
  median `score_norm` **≤ −6.4** and recovery **≤ 0.40**. (L7 measured −6.90 / 25.8 %.)
- **PC-A3 — wrong-key floor.** `exact`, `max_skip`=3, 200 uniform-random wrong keystreams
  against the real LP2 ciphertext at L=120: null mean in **[−7.6, −7.1]**.

If PC-A1 or PC-A2 fails, **stop** (Q5).

### A.3 What is measured

For each of the 30 decoder configurations, at L = 120 and L = 240:

1. `correct_keyskip` — median correct-key `score_norm` and recovery on a `encipher_keyskip`
   plant (does the fix keep the baseline power?);
2. `correct_skip2` — the same on a `skip_by_two` plant (does the fix actually cover it?);
3. `correct_drift` — the same on a free-drift plant at q = 0.05 (L7-B's second hole);
4. `null` — `score_norm` over **n = 200** uniform-random wrong keystreams against the real LP2
   ciphertext, giving mean, sd, observed max, and a two-point Gumbel extrapolation to the bar at
   N = 10⁶ and N = 10⁹ decodes.

### A.4 Pre-registered triggers

**A-i (separation collapse) — FOUND-ERROR if:** there exists **no** configuration that
simultaneously satisfies
(a) `correct_skip2` median ≥ −5.5 with recovery ≥ 0.80, **and**
(b) `correct_skip2` median ≥ (extrapolated null bar at N = 10⁶) + 0.30.
In words: no permissiveness setting both sees `skip_by_two` and still separates it from the
best of a million wrong keys. This is the plan's central premise, negated.

**A-ii (baseline power loss) — FOUND-ERROR if:** at the *least* permissive configuration that
satisfies A-i(a), `correct_keyskip` drops by **≥ 0.40** of `score_norm` relative to
`exact`/`max_skip`=3, or the N = 10⁶ bar rises by **≥ 0.40**. (The plan promises "without losing
power on the baseline construction".)

**A-iii (frontier) —** report, regardless of verdict, the permissiveness frontier as a table:
for each model × `max_skip`, the null bar at N = 10⁶ and the three correct-key scores, plus the
"free-choice count" (mean number of admissible transitions per position), which is the natural
scalar summarising permissiveness.

**NO-ERROR-FOUND** if some configuration satisfies both A-i(a) and A-i(b) without breaching
A-ii. In that case I report the configuration as the one I1 must hit and the margin it has.

---

## 4. Sub-attack B — I2's panel

### B.0 The claim under attack

`CAMPAIGN-PLAN.md`, lane I2: a **9-way** register panel behind one `adjudicate()` call, and I3
"recalibrat[ing]" because "a 9-way max-over-panel statistic inflates the null". The plan asserts
the inflation is a factor to be recalibrated. It is not obviously a *factor*: the registers are
LMs over the same 29-symbol alphabet trained on related European languages, so they are
**correlated**, and the effective number of tests is neither 1 nor 9.

### B.1 Instrument (mine)

Nine rune-space trigram LMs (EN, LP1-orthography, Latin, OE, DE, CY, half-vowel EN, no-vowel EN,
and a KJV-in-training upper bound), each built by me from this repo's corpora, each normalised
per-symbol. Plus the four doctrine-R3 statistics (decrypt IoC·N, min distinct symbols over a
32-window, best non-English LM, compressibility via zlib ratio).

### B.2 Positive control

**PC-B1 — the panel can see its own registers.** For each register, planted *correct-register*
text must score ≥ 1.0 (nats/symbol scale) above uniform-random runes on that register's own
model. ≥ 6 of 9 must pass or the attack is abandoned (Q5).

### B.3 What is measured

1. **Correlation / effective tests.** Score 2,000 uniform-random rune strings (L = 120) on all
   9 models; compute the correlation matrix and `M_eff` by the Li–Ji eigenvalue method and by
   Nyholt's. Compare to the naive 9.
2. **Naive panel FPR.** With each register's bar set at its own α = 0.01 point (measured, not
   assumed), measure the fraction of pure-noise decodes for which **max over the panel** clears
   *some* bar.
3. **Adversarial promotion.** Take the top 200 of 20,000 noise decodes *by Welsh score* and by
   *no-vowel-English score* — noise that happens to look non-English-y — and measure how often
   a max-over-panel adjudicator promotes them relative to an English-only adjudicator.
4. **The selection correction's power (the L7-A.4 audit).** L7 corrected for selection with the
   contrast `score_M − score_EN` standardised against the archive's own spread, and reported
   0 candidates at z ≥ 3 for every register. I plant **genuine** Latin, Welsh, OE and half-vowel
   English plaintexts, recover them with the correct key, and compute the *same* contrast
   statistic against the *same* kind of reference spread. If a true positive does not reach
   z ≥ 3, then A.4's zero-count is uninformative and A.5's "rank-1 power" claim does not carry
   to the corrected statistic that A.4 actually used.

### B.4 Pre-registered triggers

**B-i — FOUND-ERROR if** `M_eff` differs from 9 by more than a factor of **1.5** in either
direction (i.e. `M_eff` < 6 or > 13.5 — the latter impossible, so effectively: the registers are
substantially redundant and a 9-way correction is the wrong correction).

**B-ii — FOUND-ERROR if** the measured naive-panel FPR at per-register α = 0.01 is ≥ **0.05**
(five-fold inflation) — the plan's "recalibrate" has to absorb this and the plan does not say how.

**B-iii — FOUND-ERROR if** a *planted, correct-key, genuine* Latin **or** Welsh **or**
half-vowel-English plaintext scores **z < 3** on L7-A.4's selection-corrected contrast — i.e.
the correction that produced §A.4's negative is blind to the very true positive it was used to
exclude.

**NO-ERROR-FOUND** on each trigger it does not fire.

---

## 5. Sub-attack C — is the L1 prior load-bearing or post-hoc?

### C.0 The claim under attack

`round18/L1-toolchain/RESULTS.md` §6: an Ubuntu 11.04–12.04-class GNU/Linux workstation,
inferred from F1–F10, promoting glibc (×3), Python 2.7 (×3), Perl 5.14 (×2.5), bash `$RANDOM`
(×2) and TeX LCGs (×2), and demoting .NET to ×0.05. Round 19's Phase 1 exists **only** because
of this table (doctrine Q2 names it as the model answer).

### C.1 What is measured

1. **C-a — encoder-identification alternatives (positive control required).** L1's discriminator
   is "Artifex sRGB ICC **and** optimised Huffman **and** IJG q92 **and** 4:2:0", which it says
   no single-stage pipeline produces. I test named alternatives that L1's control table does not
   contain, in particular a **`gs -dJPEGQ=92` → `jpegtran -optimize -copy all`** chain, and
   `gs → GraphicsMagick`, and check each against the LP2 marker vector measured directly from
   the page files.
2. **C-b — the GnuPG string's independence and its actual distribution.** Count how many of the
   46 messages are *distinct signing events* (dedupe on the signature block, not the file), and
   enumerate the distros/builds that shipped GnuPG **1.4.11** — a version whose armor header is
   emitted by whatever build the signer ran, and which was shipped by more than one OS
   generation and remained the newest 1.4.x for two years.
3. **C-c — the shift arithmetic.** For each of the 11 rows, ask: is the multiplier derivable from
   any stated base rate, likelihood ratio or count? Are two members of the *same* family given
   different shifts on the same evidence?
4. **C-d — the inferential distance.** Does any measured fact in F1–F10 constrain the **pad
   generator** as opposed to the **May-2014 publication toolchain**? State the missing link
   explicitly.

### C.2 Pre-registered triggers

**C-i — FOUND-ERROR if** any pipeline **not containing ImageMagick** reproduces the four
discriminating fields on this machine.
**C-ii — FOUND-ERROR if** the 46 messages contain fewer than **30** distinct signature blocks,
or if ≥ 2 distinct OS generations shipped GnuPG 1.4.11 as their default (so the string does not
pin 11.04–12.04).
**C-iii — FOUND-ERROR if** no row's multiplier is traceable to a stated count/ratio **and** at
least one pair of rows in the same generator family carries different multipliers.
**C-iv — FOUND-ERROR if** zero facts in F1–F10 bear on pad generation rather than publication.

Any of C-i…C-iv firing makes the sub-attack FOUND-ERROR; the write-up states which, and — per
doctrine — whether the prior *survives in weakened form* rather than collapsing, because a
weakened prior is still a prior and this lane must not overreach in the other direction.

---

## 6. Sub-attack D — the round's own logic

### D.0 The claim under attack

The plan's thesis: *"repair the decoder, repair the adjudicator, recalibrate the nulls, and then
run the small, high-prior, enumerable spaces through the repaired instrument"*, with `$RANDOM`
"enumerable completely in minutes" and `\pgfmathrandom` "fully enumerable" (2³¹−1 seeds).

### D.1 What is measured

1. **D-a — throughput arithmetic.** Measure decodes/second for my beam at each permissiveness
   setting, on this machine, at L = 120 and L = 240. Multiply by the seed-space sizes the plan
   calls enumerable (bash `$RANDOM`: the 2³² `sbrand` seed space; `\pgfmathrandom`: 2³¹−2;
   Perl 5.14 `srand`: 2³² ; Python 2.7 `random.seed(str)` over a dictionary). Report wall-clock.
2. **D-b — the prefilter dilemma.** If a cheap prefilter is required to make D-a tractable,
   check what register coverage the prefilter has — L7-A.7 showed R17's English trigram
   prefilter silently reimposed exactly the English-only conditionality I2 exists to remove.
3. **D-c — does I1 reopen anything?** L7-A.6 measured **0/15** compliance: the prior sweeps'
   decodes were discarded and only English-argmax survivors remain. Enumerate what S2
   ("re-adjudicate the highest-prior slice") can physically re-run, and how many decodes that is
   against the 1.7 × 10¹⁰ that were scored.
4. **D-d — the steel-man.** Cost and expected-information comparison against the doctrine-R5
   rank-1 objects: the 450 located O/A/AE transcription disagreements, the 6 contested payload
   bytes, the 47 unread ornament bands.

### D.2 Pre-registered triggers

**D-i — FOUND-ERROR if** the measured wall-clock to enumerate any space the plan calls
"enumerable in minutes" through the repaired instrument exceeds **10³ ×** a 24-hour budget on
this machine.
**D-ii — FOUND-ERROR if** the only way to close that gap is a prefilter whose register coverage
is narrower than I2's panel (i.e. the round reintroduces the defect it exists to remove).
**D-iii — FOUND-ERROR if** S2's physically re-adjudicable set is **< 0.01 %** of the decodes
whose negatives L7-B rendered conditional.

The final section of `RESULTS.md` answers **"Is Round 19 correctly aimed?"** in plain words,
with a STOP / REDIRECT / PROCEED-AS-PLANNED recommendation, whichever the evidence supports.

---

## 7. Outputs

`RESULTS.md`, `out_a.json`, `out_b.json`, `out_c.json`, `out_d.json`, `ledger.json`,
and the scripts `r1_lib.py`, `a_permissive.py`, `b_panel.py`, `c_prior.py`, `d_budget.py`.

## 8. What this lane will NOT cover (stated in advance)

- I1/I2/I3 as **implementations** if they do not land during this lane's run. Their
  specifications are attacked; their code is not.
- Structured wrong keys (near-miss keys, offset-shifted correct keys). My null is uniform.
- Registers outside the 9 buildable from this repo's corpora.
- Whether any G1–G4 generator actually produces the LP2 keystream. That is S1's question and
  this lane deliberately does not touch it.

---

## ADDENDUM 1 — 2026-08-26, added BEFORE any sub-attack B measurement

Reason: sub-attack A's first frontier rows (`free/ms1`…`free/ms4`) showed that a drift-tolerant
transition relation has **mean branching > 1**, i.e. the decoder acquires a genuine per-position
*choice*. The decoder's internal objective is the **English quadgram model**. That creates a
compositional hazard between I1 and I2 that was not in §4: the more permissive I1 is, the harder
its beam steers a decode toward English at every free choice — including when the true plaintext
is Welsh or Latin, which is precisely what I2 exists to adjudicate. I2 can only see registers
that I1 emits.

No threshold in §3–§6 is changed. One sub-attack is added, with its trigger fixed here, before
it is run:

**B-iv — I1 × I2 destructive interaction.** Plant genuine `LA`, `CY`, `OE` and `EN_HALF`
plaintexts under `skip_by_two`; decode with the **correct key** under `exact/ms3` and under
`free/ms3`; score each emitted decode under its own register's rune LM (nats/symbol) and measure
recovery of the true rune indices.

**FOUND-ERROR if** for any non-English register the own-register LM score of the emitted decode
is **≥ 0.10 nats/symbol lower** under `free/ms3` than under `exact/ms3`, or the rune recovery is
**≥ 10 pp lower** — i.e. the I1 repair degrades exactly the signal I2 is built to detect.

**Also recorded here before measurement:** my `union` transition model as first written
de-duplicates admissible key-advances by their magnitude, so an even advance `d` inherited the
strict `exact` constraint and never got the looser `by2` constraint. That is a defect in **my**
instrument, not a finding about I1. A corrected model `union2` (which admits every even `d`
under *either* constraint) is added and both are reported; the `union` rows in `out_a.json` are
marked `instrument_defect: true` and are not used for any verdict.
