# R43 F3a — The Author's Demonstrated Toolkit and Its Measured Hand Constraints

**Lane:** F3a-author-toolkit (Round 43)
**Date:** 2026-11-03
**Inputs:** `tests/validate.py`, `src/lp/` (gematria, ciphers, solve, stats, autokey, score, corpus), raw runes `data/krisyotam_runes.txt`, solved-page corpus `data/scream314_lp.md` (via `lp.corpus`).
**Scripts:** `measure.py` (pass 1), `measure2.py` (pass 2 + simulations); results persisted in `measurements.json`, `measurements2.json`. All statistics below were computed fresh in this lane, not copied from prior docs. The elimination ledger and findings docs were NOT read (firewall condition).

**The constraint being filed:** the book is hand-illuminated. Every ciphertext rune — 12,956 in the unsolved block alone (measured; 13,136 incl. the solved AN-END and Parable pages) — was drawn by a human in 2013/14, either enciphering live or copying from a human-prepared pad/draft. Whatever the unsolved scheme is, a person executed it ~13,000 times without a machine in the loop at write time. This document models what that constraint, combined with the measured statistics, forces the scheme to be.

---

## 1. The demonstrated toolkit (exact solved-page schemes)

Extracted from `tests/validate.py` + `lp.corpus` key notes + re-derived by running the rig (all decodes reproduced in this lane; translit-level quadgram score of true plaintext ≈ −4.2…−4.6, garbage ≈ −7.0).

Ordered as the teaching escalation the author built (book order):

| Rung | Pages (onion #) | Scheme | Key material | New concept introduced | Ops/glyph for a scribe |
|---|---|---|---|---|---|
| 0 | 05, 10–13, 16, 74 | Plain Gematria Primus | none (0 symbols) | the 29-rune alphabet itself | 1 table lookup |
| 1 | Runes-01/02 | Atbash (reversed Gematria) | the table, reversed (1 rule) | reflection `i → 28−i` | 1 lookup (reversed table) |
| 2 | 06–09 | Shift 3 + reversed Gematria | 1 number + 1 rule | composition of two operations | 2 ops (reflect, step 3) |
| 3 | 03–04 | Vigenère, key **DIVINITY** (8 runes), shift-up, **F-interrupters** | 8-symbol word key | repeating key + the null convention | wheel/tableau lookup + key-pointer bookkeeping + null decision |
| 4 | 14–15 | Vigenère, key **FIRFUMFERENFE** (13 runes) | 13-symbol word key, itself distorted (CIRCUMFERENCE with C→F) | self-referential key: the key exhibits the F-convention | same as rung 3 |
| 5 | 73 (AN END) | φ(prime) stream: k_i = (p_i − 1) mod 29, shift-down, F-interrupters | **aperiodic computable number stream** (needs a precomputed prime sheet) | key from a *stated principle* ("the primes are sacred, the totient function is sacred", declared on plain rung-0 page 05) | 1 mod-29 subtract per glyph from a printed pad + pointer discipline |
| — | **17–72 (the wall)** | UNSOLVED | ? | ? (derived in §3) | must stay in this ops-per-glyph class |

### Author style, quantified

- **One primitive everywhere:** mod-29 add/subtract on the Gematria index (a 29-position wheel or 29×29 tableau). No digraph tables, no transposition, no fractionation anywhere in the solved record. Direction and table orientation (up/down, forward/reversed) are per-page conventions — cheap for a hand scribe (flip the wheel), and the rig treats them as free parameters.
- **Key sizes demonstrated:** 0, 1 rule, 1+1, 8, 13, ∞-but-computable. Monotone escalation; each rung adds exactly **one** new concept and re-uses everything prior.
- **Keys are self-disclosed:** DIVINITY is lifted from the book's own closing text ("find the divinity within"); FIRFUMFERENFE is a prior key-word passed through the book's own F-convention; the φ(prime) stream is announced in plaintext on page 05 before it is used on page 73. The author teaches the next lock with the previous key.
- **The interrupter convention, mechanically:** only ᚠ (index 0) is ever a null; a per-page *subset* of the ᚠ's. A null ᚠ is written literally and **does not advance the key pointer**. For a scribe this is one bit of discretion per F: "write ᚠ, freeze the pad finger." Measured workload on the solved pages (beam-recovered in this lane):
  - 03.jpg: 394 runes, 16 ᚠ (4.1%), **7 nulls** (44% of ᚠ's), clustered near the page start;
  - 14.jpg: 319 runes, 5 ᚠ, **2 nulls**;
  - 73.jpg: 85 runes, 5 ᚠ, **1 null**.
  So the convention is exercised sparsely — a few decisions per page, trivially hand-executable, and cryptographically it is a **stream-control** device (breaks Kasiski/period alignment, defeats naive crib dragging).
- **Error-correction affordances the author chose:** short repeating keys are *self-realigning* — a scribe's slip corrupts one glyph and position-mod-keylength restores sync. The φ(prime) pad is a *printed crib sheet* (prime list is computed once, offline); the scribe's only running state is a pointer. Interrupters give the author a pacing/realignment valve. Every demonstrated rung has bounded error propagation — nothing chained, nothing where one slip destroys the rest of the page. (Contrast: a plaintext autokey would propagate a single error to the end of the text; the author never used one on a solved page.)

### Hand budget

12,956 unsolved glyphs at one pad-lookup + one mod-29 operation + one convention check per glyph ≈ 10–25 s/glyph sustained ⇒ **36–90 hours of pure encipherment**, before illumination. Large but entirely feasible for the 2013→2014 gap — *provided* the per-glyph work stays in the 1-lookup-plus-1-add class of every demonstrated rung. Any scheme requiring per-glyph hashing, long modular exponentiation, or multi-round arithmetic is outside the demonstrated class and outside a sane hand budget at n=13k.

---

## 2. Measured statistics of the wall (computed in this lane)

Clean unsolved block = krisyotam pages p0–p54 (= onion 17–72), **n = 12,956 runes**, 2,928 words, 217 sentence marks, 17 `&` paragraph marks, 8 `$` section marks. (p55 = AN END, re-solved here blind via φ(prime)@0, score −4.57; p56 = Parable, plain, score −4.42 — both excluded.)

Null calibration: 200 uniform iid simulations at the same n.

| Statistic | Measured | Uniform null | Verdict |
|---|---|---|---|
| Unigram IoC (×29) | **0.9999** | 1.000 ± 0.0006 | dead flat (z −0.2) |
| Unigram χ² vs uniform (df 28) | 25.9 | ~28 | flat |
| Entropy | 4.8565 bits | max 4.858 | flat |
| Per-page IoC (55 pages) | mean 1.000, range 0.83–1.10 | — | flat everywhere, no mono page hiding |
| Page-homogeneity χ² (unigrams across pages) | 1351 | df ≈ 1540 | pages statistically identical |
| **Doublet rate** | **0.664%** (86 of 447.6 expected) | 3.44% ± 0.16 | **z = −17.4; rate = 0.192× expectation** |
| diffIoC = IoC of (c_i − c_{i−1}) | **1.0244** | 1.000 ± 0.0005 | **z = +47.8** |
| sumIoC = IoC of (c_i + c_{i−1}) | 1.0000 | 1.000 ± 0.0005 | flat |
| lag-2 coincidence | 3.40% | 3.45 ± 0.16 | flat |
| Lag-coincidence spectrum 1..300 | max 3.98% @ lag 99 | binomial sd 0.16% | **no period anywhere ≤ 300** |
| Repeated 4-grams / 5-grams | 133 / 7 | 122 / 4.2 (Poisson) | chance level; longest repeat = 7 runes, once |
| ᚠ rate | 3.55% (per-page 0.5–6.2%) | 3.45% | normal; no excess null-budget visible |

**Analytic identity (important):** if the lag-1 difference distribution is *flat except the suppressed 0-cell*, diffIoC = 29·(p₀² + (1−p₀)²/28) with p₀ = 0.00664 ⇒ **1.0233**, vs measured 1.0244. The entire diffIoC anomaly is the doublet deficit; there is no additional first-order chaining structure. Residual: χ² of the diff distribution *excluding* the 0-cell = 41.4 (df 27) vs 27.8 ± 7.2 under the matched model — a mild (~+1.9σ) unexplained residue, noted for follow-up, not load-bearing.

**Doublet forensics (the 86 survivors):**

- Scatter is **Poisson**: per-page dispersion 1.23 vs 1.08 ± 0.20 under random scatter (z +0.7). No page-level mixture (a block of rule-free pages would blow this up: a rule-free 260-rune page carries ~9 doublets; no page has more than ~5).
- No fatigue signal: Spearman(page order, doublet rate) = +0.11 (ns, sd ≈ 0.14).
- Doublet **values** near-uniform (top AE=7, X=6, W=6 … vs 3.0 expected each); F-F = 4 ≈ expected 3 → no interrupter signature in the doublets.
- **Zero triples.**
- Parity of doublet position within word balanced (36 even / 27 odd) → **no digraph/pair cipher**.
- Suppression is uniform across layout: within-word 0.63%, across word breaks 0.82%, across line breaks 0.70% (uniform expectation 3.45% everywhere). The process sees the glyph stream, not the word; and it did not lapse at line ends.

**Word/boundary structure:** word lengths mean 4.42 runes, distribution matching the LP-plain register (mean 4.09 on the solved plain pages; KJV-in-runes 3.66) with a modest long-word surplus (consistent with a few embedded F-nulls and/or the LP's technical vocabulary). 1-rune words take ≥8 distinct values (in plaintext they'd concentrate on a couple of function words) → polyalphabetic at the word level too. Position-in-word IoC = 1.0 at positions 0–3 → **key does not reset per word**. First-rune-of-word distribution flat (χ² 22.2, df 28).

---

## 3. Derivation: what the next rung MUST be, under the hand constraint

Two measured facts constrain the final writing step:

1. **Flat IoC at every unigram, lag, and period test** ⇒ the effective keystream is aperiodic (no period ≤ 300) **and statistically flat**. This kills more than periods: an English running-key (book pad) gives unigram IoC = **1.0698** (measured here on English+English mod 29, n=13,003) vs the measured 0.9999 ± 0.0006 — ruled out at >100σ. The pad is flat like a math stream (note: (p−1) mod 29 over primes is uniform on 28 of 29 residues — flat to within the measurement floor at this n). Aperiodic flat streams are **already in the author's demonstrated toolkit** (rung 5).
2. **The doublet deficit (z −17.4) with 86 Poisson-scattered survivors** ⇒ the process that wrote the final glyph sequence was **aware of the previous output glyph**. This is provable for the whole additive family: for c_i = p_i + k_i, a ciphertext doublet occurs iff k_{i+1} − k_i = −(p_{i+1} − p_i); no constraint on the key alone (not even "key never repeats a value") changes the collision rate away from ~1/29, because the key generator does not know the plaintext differences. Suppression therefore happened **at pad-application/write time** — i.e., in the human's hands — or in a chained cipher where c_{i−1} enters the equation.

### The mechanical options a scribe actually has, and their fingerprints

Simulated in `measure2.py` on English-in-runes plaintext (n=12,000, 12 seeds each):

| Hand process | ioc | dbl % | diffIoC | sumIoC | lag2 % | Verdict vs measured (1.000 / 0.664 / 1.024 / 1.000 / 3.40) |
|---|---|---|---|---|---|---|
| flat pad, no avoidance | 1.000 | 3.39 | 1.000 | 1.000 | 3.44 | ✗ doublets not suppressed |
| pad + re-draw(+1) on doublet | 1.000 | 0.00 | **1.068** | 1.000 | 3.56 | ✗ diffIoC too high; +1 diff cell would hold ~820 (measured 468) |
| pad + re-draw(random) | 1.000 | 0.00 | 1.035 | 1.000 | 3.55 | ✗ zero doublets; also destroys decryptability at ~3.4% of positions |
| **pad + skip-key on doublet** | 1.000 | **0.00** | 1.036 | 1.000 | 3.63 | ✗ as pure rule (zero doublets) |
| **pad + skip-key, ~20% lapse** | **1.000** | **0.674±0.058** | **1.023±0.001** | **1.000** | **3.49±0.14** | ✓ **matches every statistic within ~1σ** |
| two-stream choose-non-doublet | 1.000 | 0.124 | 1.033 | 1.000 | 3.57 | ✗ pure form: 5× too few doublets; with ~16% lapses becomes equivalent to the row above |
| ciphertext autokey (+) | 1.000 | 2.13 | **1.856** | 1.000 | 2.74 | ✗ annihilated: diff stream would be shifted plaintext |
| ciphertext autokey (−) | 1.000 | 3.55 | 1.000 | **1.856** | 3.27 | ✗ same via sumIoC |
| plaintext autokey | **1.197** | 3.98 | 1.090 | 1.037 | 3.65 | ✗ IoC not flat |
| wheel-walk (c_i = c_{i−1} + nonzero step) | 1.000 | 0.00 | 1.036 | 1.000 | 3.57 | ✗ zero doublets (plus it *is* a skip rule in disguise) |
| Vigenère-13 + skip rule | **1.115** | 0.00 | 1.056 | 1.015 | 2.93 | ✗ short key leaks through skips |
| digraph/pair cipher (Playfair-class) | — | — | — | — | — | ✗ 29 is prime (no grid) and doublet parity is balanced |
| running-key (natural-language pad) | **1.070** | 3.52 | 1.003 | — | — | ✗ unigram IoC |
| transposition after substitution | — | restores 3.45% | — | — | — | ✗ adjacency is preserved at write time ⇒ **page order = encipherment order** |

**The unique survivor:** a flat aperiodic pad applied with the demonstrated one-op-per-glyph arithmetic, plus a **doublet-triggered stream-control rule** ("if the glyph you are about to write equals the one you just wrote, advance the pad and recompute" — or the statistically equivalent two-stream choice), executed with a **~19% human lapse rate** (86 lapses over ~448 collision opportunities, one opportunity every ~29 glyphs ≈ once per written line, Poisson-scattered, no fatigue gradient, no layout dependence).

### Why this is exactly an author-shaped rung

- It is **one new concept**, like every prior rung — and it is the *same species* of concept as the F-interrupter the author already taught twice: a scribe-level stream-control convention. Interrupter = "write a null, freeze the pointer." Next rung = "on collision, advance the pointer." The escalation grammar (each rung re-uses all prior machinery plus one convention) predicts precisely this.
- It is hand-cheap: one extra visual check per glyph (did I just write this rune?), one extra pad step on ~1/29 of glyphs.
- It is decrypt-honest: unlike re-draw(random), a skip rule keeps a bijective decode — a solver (or the author verifying) can resolve skip points by trellis/beam, the exact tool shape the rig already uses for interrupters (`lp.solve.find_interrupters`).
- The lapses are the human signature. A printed computer-generated ciphertext would have ~0 doublets (and copy errors cannot explain 86: a copy error lands on the neighbor's value only ~2/29 of the time, so 86 doublets would imply ~1,200 copy errors = 10% — absurd against the otherwise clean statistics). **The 86 doublets are, on this model, the most direct physical evidence in the ciphertext that a human enciphered the book by hand** — the constraint this lane was asked to file, found written into the stream itself.

### Consequences for attack design (binding on key-hypothesis lanes)

1. **Exact-alignment decoders have ~zero power on the wall.** Under the skip model the pad pointer drifts by ~+1 every ~29 glyphs (~448 skips over the block, ~8 per page). Any sweep that applies a candidate stream positionally without skip tolerance loses sync within a line or two. Skip-tolerant/trellis decoding is mandatory; this is a *measured-power* statement, not a style preference.
2. **The 86 doublet positions are free anchors.** At a surviving doublet, a lapse occurred — i.e., *no skip happened there*, and the local equation c_{i+1} − c_i = 0 = (p_{i+1} − p_i) + (k_{j+1} − k_j) holds with consecutive pad values. Doublets pin pad-pointer phase at 86 points spread through the book (~1.6 per page).
3. **Page order = encipherment order; no post-substitution transposition.** The avoidance acts on physical adjacency, including across line and page-internal word breaks.
4. **One process for the whole wall.** Page-homogeneity + Poisson doublet scatter say the 55 pages are one statistical population: one scheme, one pad discipline, not a per-page scheme carousel.
5. **The pad is flat and aperiodic** — math-stream class (prime/totient family and kin), not a literary running key, not a short word key. This is the author's rung-5 material. The open parameters are: which stream, which per-page offset/continuation convention, which direction/orientation convention, plus the skip rule details and the (sparse) F-null overlay.

### Residuals and honesty

- diff-distribution χ² excl. 0-cell = 41.4 vs 27.8 ± 7.2 modeled (+1.9σ): mild unexplained structure in *which* non-zero differences are preferred. Worth one targeted follow-up (could encode the skip rule's exact form, e.g. "advance by 2" vs "advance by 1", or a second-order plaintext leak).
- The ~19% lapse rate is high for a deliberate single check; alternatives that fit the same statistics: the rule lives in the *pad-preparation draft* (author computing on paper, lapses are arithmetic slips), or a two-stream choice where the scribe defaults to stream 1 under load. These are indistinguishable in ciphertext statistics but differ in trellis branching structure — a decoder should allow both.
- The word-level statistics (lengths matching the LP-plain register, flat 1-rune words) are consistent with real word boundaries over English-register plaintext, but do not prove the plaintext layer is single-stage English.

---

## 4. Model summary (one paragraph)

The author demonstrably works with a single primitive (mod-29 index arithmetic on the Gematria wheel), escalating key material one concept per rung — identity, reflection, reflection+shift, 8-rune word key, 13-rune self-referential word key, aperiodic computable number stream — with a scribe-level null convention (ᚠ freezes the pad pointer) introduced mid-escalation and a declared philosophy that the stream source is announced in earlier plaintext. The unsolved wall (12,956 runes, one statistical population) measures as: perfectly flat unigram/period structure (killing short keys, literary running keys, autokeys both flavors, digraph ciphers, and post-substitution transposition) plus a 5× doublet suppression whose 86 Poisson-scattered survivors match, within ~1σ on every computed statistic, a hand-executed collision rule — "on output doublet, advance the flat aperiodic pad" — applied with a ~1-in-5 human lapse rate. The next rung, under the author's own grammar and the hand-execution budget, is therefore: rung-5-class flat computable pad + F-null overlay + one new write-time stream-control convention, and the attack-side implication is that only skip-tolerant decoders (seeded at the 86 doublet anchors) have measurable power against it.
