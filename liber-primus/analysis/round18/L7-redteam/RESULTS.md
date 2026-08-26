# L7 — INSTRUMENT RED-TEAM — results

_Round 18. Pre-registered in [`PREREG.md`](PREREG.md) before any measurement. Three
sub-attacks; verdicts are stated per sub-attack._

| sub-attack | verdict |
|---|---|
| **A — the English-only scorer** | **FOUND-ERROR** |
| **B — beam power envelope** | **FOUND-ERROR** |
| **C — the bars and the arithmetic** | **FOUND-ERROR** (2 of 6 audits clean, 1 extends a bound, 3 find calibration errors) |

**The single most consequential correction** is at the end of §A.

---

## 0. Trust anchor

Run first, before any measurement in this lane:

```
python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5 known solves)
python3 liber-primus/benchmark/gates.py       -> 7/7 gates passed
```

Every number below comes from the repo's own instrument, unchanged:
`encipher_keyskip(supp=0.83)` → `skipdecode.beam_decode(beam_w=400, max_skip=3)` →
`lp.score.Quadgram.score_norm`, with recovery measured on **rune indices** (AGENTS.md §4).

---

## A. THE ENGLISH-ONLY SCORER — **FOUND-ERROR**

### A.0 What was actually tested

Round 10b lane B6 already ran the *ciphertext-side* version of this question: can a
non-English payload be **detected from the ciphertext alone**. It answered that well and its
answer stands. It did **not** — and said in its own §0 that it could not — answer the question
here: *given the **correct key**, does the repo's adjudicator pass it?*

This lane plants a known key over each plaintext register, enciphers it under the pinned soft
anti-repeat filter, and decodes with the **correct key**. Nothing is being searched. The only
variable is what language the plaintext is in.

### A.1 The scorer-language table

12 replicates per cell, different text window and plant seed each; median `score_norm` of the
**correct-key** beam decode; "power" = fraction of replicates that clear the repo-wide −5.5 bar.
Key family `sha256_ctr(seed=CICADA3301)` — the B-04/D3 live class.

| register | L=31 | L=120 | L=240 | L=400 | median rune recovery | **power at L=120** |
|---|---|---|---|---|---|---|
| `EN_MODERN` (held-out English) | −4.20 | −4.22 | −4.32 | −4.34 | 100 % | **1.00** |
| `EN_KJV` (in the training corpus) | −3.77 | −4.11 | −4.09 | −4.01 | 100 % | **1.00** |
| **`LP1_REAL`** (the five solved pages' own plaintext) | −4.19 | **−4.33** | −4.32 | −4.31 | 100 % | **1.00** |
| **`LATIN`** (Caesar + Principia) | −5.45 | **−5.58** | −5.59 | −5.55 | 100 % | **0.33** |
| **`OE`** (Beowulf + the OE rune poem) | −5.40 | **−5.39** | −5.39 | −5.45 | 100 % | **0.58** |
| `DE` (Faust + Kafka) | −5.19 | −5.52 | −5.36 | −5.48 | 100 % | 0.42 |
| `CY` (Welsh Mabinogion) | −6.54 | −6.58 | −6.55 | −6.75 | 100 % | **0.00** |
| **`EN_HALFVOWEL`** (half the vowels dropped) | −5.44 | **−5.62** | −5.62 | −5.68 | 100 % | **0.33** |
| **`EN_NOVOWEL`** (all vowels dropped) | −7.66 | **−7.60** | −7.74 | −7.76 | 85 % | **0.00** |
| `RAND` (uniform runes — the floor) | −7.27 | −7.39 | −7.29 | −7.23 | 33 % | 0.00 |
| _wrong key, any register_ | ≈ −7.5 | ≈ −7.4 | ≈ −7.3 | ≈ −7.3 | — | 0.00 |

Raw rows in `out_a1.json`; script `a1_scorer_language.py`.

### A.2 What breaks, precisely

**The decoder is not the problem. The adjudicator is.** Rune-index recovery of the correct key
is **100 % for Latin, Old English, German, Welsh and half-vowel English** at every length
tested. The beam finds the right skip path and emits the right runes. The quadgram scorer then
reports the result as noise, and the sweep records a miss.

Distance below the −5.5 bar, at the lengths the sweeps actually scored at:

- Latin: **0.08–0.09 below** the bar. Power 0.33–0.50.
- Half-vowel English: **0.12–0.18 below**. Power 0.25–0.33.
- Welsh: **1.05–1.25 below**. Power 0.00.
- Vowel-dropped English: **2.10–2.26 below** — and *below the wrong-key score*
  (−7.60 correct vs −7.41 wrong). A fully abbreviated English plaintext is not merely
  invisible, it is **anti-selected**: the correct key ranks below a deliberately wrong one.
- Old English and German straddle the bar (−5.39 to −5.52): power 0.42–0.83, i.e. a coin flip.

Every published negative in this repository is stated as if power were 1.0. The measured power
of the instrument that produced them is 1.00 only for modern/archaic English.

### A.3 The good news, stated as clearly as the bad

`LP1_REAL` — the *actual* plaintext register of the solved Liber Primus pages, in the actual
lossy orthography (`CNOW`, `BELIEUE`, `THNGS`), taken from `SOLVED-PAGES.json` — scores
**−4.33 at power 1.00**. The register the puzzle has demonstrably used is fully covered. The
orthography round trip itself (K→C, V→U, Q→C, Z→S, seven digraph expansions) costs only
**0.139** of score. So the English-only conditionality is a real hole, but it is a hole in the
*less likely* directions, and this lane does not claim otherwise.

"Word-boundary-free text" turns out to be a **non-issue, measured rather than assumed**:
`data/BUILD-QUADGRAMS.md` shows the model is built with `re.sub(r'[^A-Z]','',...)`, i.e. it was
trained on boundary-free text, so it is already matched to boundary-free rune output. That
register costs nothing and is struck from the concern list.

### A.4 Re-scoring the archived sweep bests (the never-run `REDTEAM-PROPOSALS.md` item)

340 archived candidate decode strings were harvested from **round13/B04 (A/B/C/D),
round16/KDF, round16/prng and round17 P0–P3** — every `top50`/`top20` `head` field in the
post-B6 sweeps — and re-scored under rune-space trigram LMs for EN / LA / OE / DE / CY / the
real LP1 register, plus decrypt-IoC·N. Script `a2_rescore_archive.py`, output `out_a2.json`.

A raw z against a random-rune null flags 44/340, but that is an artifact: every archived
candidate **is the English argmax of its sweep**, so English-correlated models (OE, DE) light up
by selection alone. The selection-corrected statistic is the contrast
`score_M − score_EN`, standardised against the archive's own distribution:

| model | max z-contrast over 340 candidates | n ≥ 3 | n ≥ 4 |
|---|---|---|---|
| LATIN | 2.71 | 0 | 0 |
| OE | 2.58 | 0 | 0 |
| DE | 2.23 | 0 | 0 |
| CY | 2.91 | 0 | 0 |
| LP1 register | 2.96 | 0 | 0 |

**Result: no archived candidate is more Latin-, Old-English-, German- or Welsh-like than its own
English-likeness already explains.** The queued `campaign14/REDTEAM-PROPOSALS.md` item
(~line 155) is now executed for the post-B6 sweeps and is NEGATIVE.

### A.5 …and how much that re-scoring is actually worth (pre-registered power check)

Rule 5 of the PREREG required this to be computed whether or not anything flagged. Using each
sweep's own recorded score histogram and A1's measured per-register medians:

| register | correct-key score | z vs B-04's own null | expected rank among 1,385,600 decodes | in the stored top-50? |
|---|---|---|---|---|
| LP1_REAL / English | −4.33 | +13.1 | 1 | yes |
| LATIN | −5.58 | **+7.6** | **1** | **yes** |
| OE | −5.39 | +8.5 | 1 | yes |
| EN_HALFVOWEL | −5.62 | +7.5 | 1 | yes |
| CY | −6.58 | +3.3 | 651 | **no** |
| **EN_NOVOWEL** | −7.60 | **−1.10** | **1.2 × 10⁶ of 1.39 × 10⁶** | **no** |

Identical picture for R16-KDF (692,064) and R16-PRNG (52,556).

So the archive re-scoring **is** powered for Latin, Old English and half-vowel English — a
correct key in those registers would have failed the −5.5 *bar* but would still have been
**rank 1** and therefore stored, and §A.4 shows it is not there. That genuinely narrows those
registers. It is **not** powered for Welsh and has **zero** power for vowel-dropped English,
whose correct key lands in the middle of the noise and can never enter any top-N. That is a
permanent blind spot of the archive, not a narrowable one.

### A.6 A binding handoff requirement was issued in Round 10b and never complied with

B6's RESULTS.md §0 states:

> **Handoff requirement for future harnesses:** persist a language-agnostic statistic (decrypt
> IoC.N, distinct-symbol minimum over a 32-window, best non-English LM score) **at sweep time**,
> alongside the English score. Retro-fitting is impossible once the decodes are thrown away.

Checked mechanically across all 15 post-B6 result files (`out_a2.json → b6_handoff_compliance`):

| sweep | rows stored | language-agnostic fields |
|---|---|---|
| round13/B04 A, B, C, D | 50, 50, 50, 2 | **none** |
| round16/KDF stage A | 50 | **none** |
| round16/prng | 20 | **none** |
| round17 P0 (×5), P1, P2, P3 (×2) | 20 each | **none** |

**0 of 15.** Every sweep that ran after the requirement was issued stored only
`(parameters, English score, 64-char head)`. The 6,224,300 + 692,064 + 52,556 decodes and the
≈14.5 × 10⁹ offsets are therefore adjudicated English-only **and cannot be retro-fitted** —
only the argmax-by-English survivors still exist.

### A.7 Round 17 filters on English *twice*

`round17/lib_padsweep.dense_scan` selects which offsets reach the beam using a **rune-index
trigram model trained on the same four English books** (`trigram_model()`, kjv/moby/pride/war),
over a 24-rune head. Only the top 40 per sign are beam-escalated. So for R17's ≈14.5 × 10⁹
offsets the pipeline is *English trigram prefilter → English quadgram beam*, and a non-English
true offset is discarded before the beam ever sees it. R17's own measured prefilter survival
(0.375–0.875, non-monotone in pad size) is a survival rate **for English plants only**; no
non-English survival rate was ever measured, so R17's coverage discount does not apply to a
non-English plaintext at all.

### A.8 Restated coverage bounds (the deliverable)

These are restatements of existing `LEDGER.json` entries. Nothing is downgraded from negative to
positive; what changes is the stated scope. Machine-readable in `ledger.json`.

- **B-04** — *was:* "NEGATIVE. 6,224,300 decodes, 0 over the −5.5 bar."
  *Restated:* "NEGATIVE **for a modern/archaic-English or LP1-register plaintext**, at measured
  power 1.00. Against a Latin plaintext the same sweep has power 0.33–0.50, against
  half-vowel-abbreviated English 0.25–0.33, against Welsh 0.00 and against vowel-dropped English
  0.00. The stored top-50 re-scoring (L7/A.4) extends the negative to Latin, Old English and
  half-vowel English at rank-1 power; it does not extend it to Welsh or to vowel-dropped
  English, for which no evidence exists in the archive at all."
- **R16-KDF** (692,064) and **R16-PRNG** (52,556) — identical restatement; identical measured
  powers; identical top-50/top-20 rank-1 extension.
- **R17-PUBLIC-PAD** — *was:* "NEGATIVE … 14,522,916,046 offsets scored."
  *Restated:* "NEGATIVE for an English plaintext. The offsets were selected by an **English
  trigram prefilter** and adjudicated by an **English quadgram beam**; the measured prefilter
  survival (0.375–0.875) was measured on English plants only. This lane's coverage of a
  non-English plaintext is **unmeasured**, not zero and not one."
- **Round 8 SEED (B-21)**, **R12-A1**, **R12-C1**, **F-01**, and the ~200-text keytext
  sweep — same English-only conditionality; all used `score_norm` against a fixed English
  band.

### A.9 Verdict A — **FOUND-ERROR**

PREREG rule 3 is met: `LATIN` and `EN_HALFVOWEL` are INVISIBLE (median correct-key score below
−5.5) at L = 120 **and** L = 400, `EN_NOVOWEL` catastrophically so, and **no `LEDGER.json` entry
anywhere states an English-register conditionality** — the word "English" does not appear in any
`coverage` or `not_covered` field of the 62 entries.

> **The single most consequential correction.** Every "NEGATIVE" in this repository — 6.2 M
> derived-key decodes, 692 k KDF, 52 k PRNG, 2.52 × 10⁹ Round-8, ≈14.5 × 10⁹ Round-17 offsets —
> is a negative **conditional on the plaintext being modern or archaic English**. That condition
> is true of the register the Liber Primus has actually used (`LP1_REAL` scores −4.33 at power
> 1.00), so the negatives are not void. But the instrument's measured power against a Latin
> plaintext is **0.33–0.50**, against abbreviated English **0.25–0.33**, and against
> vowel-dropped English **0.00 — where the correct key scores *below a wrong key*.** The ledger
> states these bounds as though power were 1.0. That is the same shape of error D3 found: a
> conditional measurement written up as an unconditional one.

**What reopens it:** re-adjudicating any stored top-N under a non-English model (done here for
Latin/OE/DE/CY — negative), or persisting a language-agnostic statistic at sweep time in every
future harness (B6's requirement, still not complied with — see the concrete spec in §A.6).

---

## B. BEAM POWER ENVELOPE — **FOUND-ERROR**

Plaintext held at English throughout, so the scorer is at full power and every loss below is
the **decoder's**. 7 seeds per construction, L = 240, correct key given to the decoder.
"MISSED" = median correct-key `score_norm` < −5.5. Script `b1_power_envelope.py`, raw
`out_b1.json` (67 constructions).

### B.1 The power curve

| axis | robust up to | **breaks at** | does a bigger budget/beam help? |
|---|---|---|---|
| suppression `supp` 0.0 → 1.0 | **all values** | never | n/a |
| position-varying `supp` (ramp / per-page blocks / burst) | **all three** | never | n/a |
| beam width 50 → 1000, `max_skip` 1 → 8 (high-entropy pad) | **all values** | never | no effect at all |
| low-entropy pad, run length r, `supp`=0.83 | r ≤ 32 | — | ms=8 restores r=8..32 |
| low-entropy pad, run length r, **`supp`=1.0** | r ≤ 4 | **r = 8** (−6.56) | ms=8 fixes r=8, **fails at r=16 (−6.50) and r=32 (−7.05)** |
| unrepresentable key advances per 240 runes | n ≤ 3 (−4.91) | **n = 5** (−6.67) | **no** — ms=8 + beam 1000 gives *identical* scores |
| free drift rate q | q ≤ 0.02 (−5.26) | **q = 0.05** (−6.88) | **no** — ms=8 identical |
| **rejection consumes TWO draws** | *nothing* | **every `supp` tested** (−5.90 to −6.90) | **no** — ms=8 identical |

### B.2 The hole that matters: the beam's *transition relation*, not its budget

`beam_decode` admits a key skip only if **every skipped key position would have reproduced the
previous cipher rune**. That test is exact for `encipher_keyskip` and for nothing else. A key
advance that happened for any other reason has probability ≈1/29 of being representable, so it
is not "harder" — it is **outside the decoder's model**. This is why raising `max_skip` from 3
to 8 and the beam from 400 to 1000 changes the numbers by **exactly 0.000**: the failure is not
a search-depth failure.

Measured cost of a single unrepresentable key advance over 240 runes: **−0.30 score, −5 pp
recovery**. At 5 events (≈1 per 48 runes) the correct key is gone: −6.67, 25.8 % recovery.

**`skip_by_two`** — the rejection sampler advances the key by two rather than one when it
rejects a symbol — is the sharp case. It is a one-character change to a plausible 2013
rejection loop, it **reproduces LP2's doublet rate (0.84 % vs the observed 0.664 %)**, and the
correct key scores **−6.90 at 25.8 % recovery**, i.e. deep in the noise band, at every
suppression level and at both skip budgets. It appears in no `not_covered` field anywhere in
`LEDGER.json`.

### B.3 Two constructions that the data *does* exclude (a result in the repo's favour)

Both were tested here for the first time:

- **key-side filter** — the keystream itself generated doublet-free, rigid encipherment: the
  beam misses it (−6.27, 44.6 % recovery), **but it produces a 3.77 % ciphertext doublet rate**,
  nowhere near LP2's 0.664 %.
- **plaintext-side filter** — the plaintext written doublet-free, rigid encipherment: **3.80 %**.

So the anti-repeat filter demonstrably had to act on the **output**, not on the key stream and
not on the plaintext. The repo asserted this; it is now measured. `keyskip` (0.84 %) and
`rewrite` (0.42 %) are the only two placements that reproduce the observed statistic, and the
beam handles both.

### B.4 Restated coverage bounds

- **Every beam-based negative in this repository** — B-04, B-05, R16-KDF, R16-PRNG, R17 P0–P3,
  R12-A1, R12-C1, F-01 and the ~200-text keytext sweep — covers the key-skip filter
  **in which rejection advances the key by exactly one symbol and nothing else ever advances
  it**. It does not cover a sampler that burns two draws per rejection, nor any construction
  with an independent source of key drift at more than ≈1 event per 60 runes.
- **`max_skip`.** Round 17's correction (`ms=3` underpowered on constant-byte runs, `ms=8`
  fixes it) is confirmed and **extended**: at a hard filter (`supp`=1.0) `ms=8` still fails at
  run length 16 and 32. The honest statement is "`ms=8` covers constant runs up to length 8",
  not "`ms=8` fixes it".

### B.5 Verdict B — **FOUND-ERROR**

PREREG rule B-iii is met: `skip_by_two` (a) reproduces LP2's doublet rate to within 0.18 pp,
(b) appears in no ledger `not_covered` field, and (c) is provably missed at every suppression
level and every skip budget tested. The `drift_at`/`free_drift` family is a second, continuous
version of the same hole with a measured breaking point at ≈1 unrepresentable key advance per
60 runes.

---

## C. THE BARS AND THE ARITHMETIC — **FOUND-ERROR**

Script `c1_bars.py`, output `out_c1.json`. Six audits; two reproduce cleanly, one extends a
published bound, three find calibration errors.

### C.1 Headline statistics — reproduce exactly (NO-ERROR)

Recomputed from the pinned runes with independent code:

| statistic | recomputed | published |
|---|---|---|
| n runes | 12,956 | 12,956 |
| doublets | 86 | 86 |
| doublet rate | **0.66384 %** | 0.664 % |
| IoC × N | **0.999874** | 0.9999 |
| entropy | **4.856504 bits** | 4.8565 |
| lag-1 suppression | **80.746 %** | 80.75 % |

One methodological note, not an error: lag-1 suppression is `1 − observed/expected` where
*expected* is the stream's **own** unigram collision rate (measured 3.4478 %), not `1/29`
(3.4483 %). The two agree here only because IoC·N = 1.0000; on any stream with unigram
structure they differ, and the 1/29 shortcut would be wrong.

### C.2 The G3 doublet floor — holds, and is now measured beyond English (bound EXTENDED)

The published floor (`min_d Pdp(d)`, the smallest doublet rate any plaintext-**independent** key
can produce) is measured on four modern English corpora. Recomputed: KJV 1.386 %, Moby 1.798 %,
Pride 1.786 %, War 1.831 % — reproducing D2's published 1.38–1.83 % exactly.

Extended, for the first time, to registers the published floor never covered:

| register | `min_d Pdp(d)` | ratio to observed 0.664 % |
|---|---|---|
| Old English | 2.074 % | 3.12× |
| Welsh | 2.339 % | 3.52× |
| LP1 solved-page register | 1.585 % | 2.39× |
| Latin | 1.425 % | 2.15× |
| held-out English | 1.483 % | 2.23× |
| half-vowel English | 1.694 % | 2.55× |
| vowel-dropped English | 1.084 % | 1.63× |
| **German** | **0.972 %** | **1.46×** |

**No register reaches the pre-registered 0.80 % trigger.** The G3 argument — "to reach 0.664 %
via an independent key the plaintext must itself carry the anti-repeat structure; no natural
language does" — **survives** extension from 4 English corpora to 9 registers across 5
languages, including abbreviated forms. That is a genuine strengthening of a load-bearing step
and it is reported as such.

Two corrections of record, both minor: the floor's **margin** is narrower than published —
the binding register is German at 1.46×, not "1.50 %" at 2.26×; and `ELIMINATION-LEDGER.md:779`
and `round10/SYNTHESIS.md:74` still quote **"floor 1.50 % (KJV)"** when KJV's actual value is
**1.386 %** and D2 already superseded the figure with 1.38–1.83 %. The stale number is quoted
in the ledger's load-bearing line.

### C.3 `threshold_for()`'s Gumbel constants — zero degrees of freedom, and circular

`DEFAULT_MU = −7.2517`, `DEFAULT_BETA = 0.0725` are **not a fit**. They are the exact solution of
two equations in two unknowns, anchored on two single observed maxima (n=200 → −6.826;
N=1,385,600 → −6.185). Verified: solving those two anchors returns β = 0.072484,
μ = −7.251882, i.e. the published constants to 6 significant figures. **Degrees of freedom: 0**,
so there is no residual and no internal check.

Each anchor is itself a single Gumbel draw with sd = βπ/√6 = **0.0930**. Propagating that
through the two-point slope gives **SE(β) = 0.0149, i.e. 20.5 % relative**, and SE(μ) ≈ 0.128.
Both anchors come from **B-04's own run**, and `threshold_for()` was then used to adjudicate
B-04.

Out-of-sample residuals against every recorded sweep maximum in the repository:

| sweep | N | observed max | predicted E[max] | residual (Gumbel SD) |
|---|---|---|---|---|
| B-04 stage A | 1,385,600 | −6.185 | −6.185 | 0.00 _(anchor)_ |
| B-04 stage B | 1,290,240 | −6.129 | −6.190 | +0.65 |
| B-04 stage C | 3,548,160 | −5.885 | −6.116 | +2.49 |
| R16-KDF | 692,064 | −6.259 | −6.235 | −0.26 |
| R16-PRNG | 52,556 | −6.347 | −6.422 | +0.80 |
| **R17 P0 dense** | 3,911,819,734 | −6.769 | −5.609 | **−12.48** |
| **R17 P1 bitcoin** | 1,389,182,016 | −6.802 | −5.684 | **−12.03** |
| **R17 P2 beacons** | 3,464,597,548 | −6.811 | −5.617 | **−12.84** |
| R17 P3 tables | 5,757,316,748 | −5.679 | −5.581 | −1.06 |

**3 of 9 breach the pre-registered 3-SD trigger, all of them Round 17.** The constants are
well calibrated for the family they were derived from (B-04 / R16: −0.26 to +2.49 SD) and are
**not applicable to R17's lanes**.

The cause is not the constants — it is the **N**. R17 fed `threshold_for()` the number of
*offsets scanned*, but the statistic being adjudicated is the maximum over the number of *beam
decodes actually performed*: `lib_padsweep.escalate` beam-decodes only the **top 40 per (pad,
builder, sign)** survivors of the trigram prefilter. For P3 that is 28 configs × ≤40 ≈ 10³ beam
scores, not 3.3 × 10⁹. Inverting the model on the observed maxima gives an effective trial count
of ≈ 4 × 10², which is exactly the right order.

R17's own files contain the evidence and never reconciled it:
`round17/P1_blockchain/results.json` records `expected_null_max_at_n = −5.684` next to
`null_max_over_lane_ms8 = −6.822` — a 1.14 gap, 12 Gumbel SD, sitting unremarked in the result
file.

**Consequence.** R17/SYNTHESIS's claim that *"`threshold_for()` at each lane's true trial count
is stricter than the fixed −5.5 bar in all four cases, so no verdict here depends on which bar
you use"* rests on a trial count that is 6–7 orders of magnitude too large. No published verdict
changes — every best score is below both bars — but the bar-independence argument does not hold
as stated, and the reported bars (−5.29 to −5.39) were **0.11–0.21 stricter than the correct
one**, which is the direction that could hide a marginal signal rather than manufacture one.

### C.4 The constants do not transfer across segment length — measured

`null.py` documents its constants as *"L~120 segments, skip-aware beam"* at `beam_w=400`.
R17 ran its escalations at `beam_w=120` on head windows of **25–400 runes**. Measured directly
(400-sample shuffle nulls, peaks-over-threshold tail scale):

| (L, beam_w) | null mean | null max | tail β | β / `DEFAULT_BETA` |
|---|---|---|---|---|
| (31, 120) | −7.464 | **−5.681** | 0.2481 | **3.42×** |
| (120, 400) | −7.386 | −6.597 | 0.1243 | 1.71× |
| (400, 120) | −7.305 | −6.936 | 0.0522 | 0.72× |

The pre-registered factor-1.5 trigger is breached at every length. **Verdict: DOES NOT TRANSFER.**

The absolute POT values are biased high (at L=120 the estimator returns 1.71× the repo's
tail-calibrated 0.0725 — exactly the bias `null.py` warns about), so the **ratios** are the
robust part, and they follow a clean **1/√L law**: measured β(31)/β(120) = **2.00** against
1/√L's prediction of **1.97**. Anchoring on the repo's own calibrated β at L=120 gives

- β(L = 400) ≈ **0.0397** — R17 used 0.0725, **1.83× too large**, worth **0.83 of score** in the
  bar at N = 10⁹;
- β(L = 31) ≈ **0.143** — twice the default.

**And the concrete consequence for R17's headline number.** P3's best of **−5.679 was scored on
a 31-rune head window**. An order-destroying shuffle null at L = 31 reached **−5.681 in 400
draws** in this lane's own measurement. R17/SYNTHESIS presents that best as "−5.679 vs a bar of
−5.500", i.e. 0.18 short of a hit. At the window length it was actually measured on, a value
indistinguishable from it is reachable by pure shuffling in a few hundred draws. **A fixed −5.5
bar is not a bar at 31 runes.** (P3's own per-pad null was length-matched and correctly returned
`null_max = −6.088` at n=200 for that pad's short 304-symbol keystream, so the lane's *verdict*
is sound; what is wrong is the comparison of a 31-rune score to a bar calibrated on 120–400-rune
segments, and the SYNTHESIS sentence built on it.)

### C.5 Bar-at-own-N audit

`threshold_for()` crosses the −5.5 floor at **N\* = 3.13 × 10⁸**. Below that the historical floor
binds and the scale correction is cosmetic; above it a fixed bar is unsound.

| sweep | N | `threshold_for(N)` | floor binds? | bar actually used |
|---|---|---|---|---|
| **Round 8 SEED** | 2.52 × 10⁹ | −5.349 | **no** | a fixed bar |
| B-04 | 6,224,300 | −5.500 | yes | max(−5.5, null_max+0.5) |
| B-05 | 70,680 | −5.500 | yes | max(−5.5, null_max) |
| R16-KDF | 692,064 | −5.500 | yes | −5.5 + size-matched null |
| R16-PRNG | 52,556 | −5.500 | yes | −5.5 + size-matched null |
| R17 P0–P3 | 1.4–5.8 × 10⁹ | −5.29 … −5.39 | **no** | −5.5 AND null_max+0.5, with `threshold_for(N_offsets)` quoted |
| R12-A1 | 768 | −5.500 | yes | −5.5 |
| F-01 | 40 | −5.500 | yes | −5.5 AND null_max+0.5 |

Round 8 is the one sweep that exceeded N\* **and** used a fixed bar with no correction —
quantifying the flag B-21 has carried unactioned since Round 10. (Round 8's reported best of
−13.13 is on a different score scale and is far below any of these bars, so the verdict itself is
not in question; the *method* is.)

### C.6 The multiple-comparisons tally — B-17's "frozen at 5", recomputed

| level | count | family-wise bar it implies |
|---|---|---|
| pre-registered hypotheses (ledger entries carrying a `threshold`) | **19** | −5.500 (floor binds) |
| ledger entries total | **62** | −5.500 (floor binds) |
| decodes / offsets scored, all rounds | **17,058,157,809** | **−5.210** |
| …after R17's own measured prefilter discount | 10,915,241,763 | −5.242 |

Breakdown of the decode-level tally: Round 8 SEED 2.52 × 10⁹; Round 8 other tracks 8.2 × 10⁶;
B-04 6,224,300; B-05 70,680; R16-KDF 692,064; R16-PRNG 52,556; R17 P0–P3 1.45 × 10¹⁰;
plus the small lanes (R12-A1 768, R12-C1 1,155, F-01 40, ~200 keytexts).

**5 was never the right number at any level.** Which number is right depends on which family is
being controlled, and the repo has never said. At the decode level the repo-wide family-wise bar
is **−5.210 — stricter than the −5.5 floor every sweep quoted**. No published verdict flips
(every best score in the repo is below both), but **−5.5 is not the repo-wide bar and should not
be quoted as one.** Honest caveat: these are not independent tests — the same 12,956 runes are
re-decoded — so the union correction is conservative, which is the safe direction for a negative.

### C.7 Verdict C — **FOUND-ERROR**

Two of the six audits reproduce cleanly (C.1) or strengthen a published bound (C.2). Three find
calibration errors, all in how `threshold_for()` was used rather than in the function itself:
the constants are a zero-DOF, circular two-point solve with 20.5 % relative uncertainty on β
(C.3); they were applied 12–13 Gumbel SD outside their calibrated domain by Round 17, with the
mismatch visible and unremarked in R17's own result file (C.3); and they do not transfer across
segment length, β following 1/√L, which makes R17's headline "−5.679 vs −5.500" near-miss a
31-rune score compared against a 120–400-rune bar (C.4). B-17's tally of 5 is wrong at every
level of granularity (C.6).

### C.8 Restated coverage bounds from C

- **R17-PUBLIC-PAD** — the `threshold_for()` figures quoted per lane are computed at
  *offsets scanned*, not at the number of beam decodes adjudicated, and with constants
  calibrated at a different segment length. Read each lane's **own length-matched shuffle null**
  (which R17 did measure correctly, per pad) instead; the verdicts stand on those.
- **B-21 / Round 8 SEED** — add the number: N = 2.52 × 10⁹ exceeds N\* = 3.13 × 10⁸, so the fixed
  bar it used was outside the region where a fixed bar is valid.
- **B-17** — the tally is 19 / 62 / 1.71 × 10¹⁰ depending on the family; the repo-wide
  decode-level family-wise bar is −5.210.
- **G3 floor** — extend the published bound from "4 English corpora" to "9 registers across 5
  languages including abbreviated forms, minimum 0.972 % (German), margin 1.46× over the
  observed rate"; and retire the stale "1.50 % (KJV)" figure in favour of D2's 1.38–1.83 %.

---

## What this lane measured, and what it did NOT cover

Per Round 18 rule 6. Nothing here is a verdict on the cipher; every result is a property of the
*instrument*.

**Covered:** 10 plaintext registers × 4 segment lengths × 12 replicates of correct-key scoring;
340 archived candidates re-scored under 6 rune-space LMs plus decrypt-IoC·N; 67 decoder
constructions × 7 seeds; 6 arithmetic audits including 1,200 fresh shuffle-null beam decodes at
three (L, beam_w) settings.

**Not covered:**

- Registers outside the 10 tested — Greek, Hebrew, Norse, constructed languages, and any
  non-linguistic payload (B6 proved the last class undetectable in principle).
- Only one key family (`sha256_ctr`) was used for the scorer-language panels. The effect is a
  property of the scorer, not of the key, but that was not verified across families.
- The decoder constructions were tested one axis at a time at L = 240; combinations were not.
- `round16/scorer`'s **matched runic quadgram scorer** exists, passed its gates and is
  importable — and **no lane has adopted it**. Whether it changes any of the A.1 numbers is
  untested here.
- The C.4 tail-scale estimates are relative, not absolute; the absolute β values carry the
  upward bias `null.py` documents, which is why only the ratios are used.

**Follow-ups this lane generates, cheapest first:**

1. **Add one field to every future harness.** Persist `decrypt IoC·N` and a best-non-English-LM
   score alongside every stored candidate. B6 asked for this in Round 10b; 0 of 15 later sweeps
   did it, and it cannot be retro-fitted. Cost: three lines in the sweep loop.
2. **Give `threshold_for()` a `segment_len` argument that actually does something.** It already
   accepts one and ignores it. β scales as 1/√L (measured); wiring that in fixes C.4 outright.
3. **Have lanes pass the number of decodes adjudicated, not the number of offsets scanned.**
   That single change removes the 12-SD residuals in C.3.
4. **Re-run the B-04 / R16-KDF / R16-PRNG top-50 escalations against a Latin and an Old-English
   quadgram model**, not just a trigram LM — cheap, and it would convert A.5's rank-1 power
   argument into a direct measurement.
5. **Bound the `skip_by_two` family.** If the 2013 rejection loop consumed two draws per
   rejection, every beam-based negative in the repository is void. The cheapest discriminator is
   not more sweeping but L2's territory: the filter's own draw-consumption signature.

## Reproduce

```bash
cd liber-primus/analysis/round18/L7-redteam
python3 a1_scorer_language.py     # scorer-language table          -> out_a1.json
python3 a2_rescore_archive.py     # archive re-scoring + its power -> out_a2.json
python3 b1_power_envelope.py      # beam power curve               -> out_b1.json
python3 c1_bars.py                # bars, floors, tallies          -> out_c1.json
```
