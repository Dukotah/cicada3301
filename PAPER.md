# Every Negative Was an English-Only Negative

### Instrument power as the binding constraint on ~10¹⁰ pre-registered decode attempts against the Liber Primus

**Dukotah** · <https://github.com/Dukotah/cicada3301> · Release `v2026.10.5-round30-handoff` · 2026-10-05

---

## Abstract

Between 2026-06 and 2026-10 this project ran approximately 10¹⁰ pre-registered decode attempts
against LP2 — the 12,956-rune unsolved section of the Cicada 3301 *Liber Primus* — across 30
numbered rounds, every one with its threshold fixed in advance and its result committed to a
machine-readable falsification ledger. Every attempt returned a negative.

The most consequential finding of the entire programme was not about the cipher. It was that
the instrument producing those negatives could not have detected success over most of the
hypothesis space it was being used to exclude. Handed the **correct key**, our adjudicator
recovered **100% of rune indices** against Latin, Old English, German and Welsh plaintexts and
then scored every one of them as noise. Against vowel-dropped English, the correct key scored
**below a deliberately wrong key**. Measured statistical power at the project's own published
decision bar was **1.00** for the register the Liber Primus demonstrably uses, **0.33** for
Latin, **0.00** for Welsh, and **0.00** for vowel-dropped English.

Separately, the decoder's transition relation was exact for exactly one rejection-sampling
implementation and no other. A one-character variant of that loop — which independently
reproduces LP2's observed doublet rate — drives the correct key to **−6.90 at 25.8% rune
recovery**, deep in the noise band, and raising the search budget changes that number by
**exactly 0.000**.

Neither failure was a search-depth problem, and neither was recoverable after the fact: a
standing requirement to persist language-agnostic statistics at sweep time had **0/15**
compliance, so ~10¹⁰ discarded decodes cannot be re-adjudicated. We report the scope of what
those sweeps actually measured, the three terminal verdicts this project has had to retract,
and a reusable discipline for producing negative results that are worth something. The
cryptanalytic verdict that survives is narrow and stated precisely: LP2 is **OTP-class**.

**Keywords:** negative results · pre-registration · statistical power · instrument validation ·
cryptanalysis · reproducible research

---

## 1. Why this is a paper about measurement, not about a puzzle

A null result carries information only in proportion to the probability that the experiment
would have produced a positive had one existed. This is elementary, it is taught in every
statistics sequence, and it is routinely ignored in computational search — because in search
the instrument is code you wrote yourself, and code you wrote yourself feels like a known
quantity rather than an apparatus requiring calibration.

It is not a known quantity. This paper is a case study in how far that assumption can carry a
careful, honest, pre-registered research programme before it collapses, and in what it costs
when it does.

The setting is adversarial and unusually clean. The target is a cipher that has resisted the
internet for a decade. Success is unambiguous and self-evident (readable English). The search
space is enormous. Crucially, **the ground truth for calibration is available**: five pages of
the same book are already solved, so a correct key can be planted and the apparatus asked a
question it is almost never asked — *would you recognise your own answer if it were handed to
you?*

For most of this project's history, nobody asked. The answer, when finally measured, was
largely **no**.

## 2. The object

LP2 is pages 0–54 of the *Liber Primus*, the final artifact of the Cicada 3301 puzzle series
(2012–2014; the entity went silent in April 2017). It is a 29-symbol runic alphabet, 12,956
symbols, pinned by SHA-256 in [`liber-primus/PROBLEM.json`](liber-primus/PROBLEM.json) so that
no number in this paper is comparable to a reader's work unless their copy hashes identically.

Measured statistics:

| statistic | value | interpretation |
|---|---|---|
| Index of coincidence × N | **1.0000** | indistinguishable from uniform random |
| Shannon entropy | **4.857 bits** | ≈ log₂(29) = 4.858; maximal |
| Adjacent-equal ("doublet") count | **86 / 12,956** | — |
| Doublet rate | **0.6638%** | **the only real anomaly** |

The doublet rate is the whole case. Natural English runs ≈3.4% adjacent-equal pairs, uniform
random over 29 symbols runs ≈3.45%, and — this is the load-bearing part — **any running-key or
additive stream cipher inherits a plaintext-independent floor of ≥1.38%**, because the
combining step injects collisions regardless of what the message says. LP2 sits at less than
half that floor.

That single number does real work. It mechanically excludes the entire published-text
running-key family, which explains a decade of failed keytext attempts as *wrong mechanism*
rather than *wrong text*; and it positively refutes autokey, the community's standing
hypothesis for ten years. Autokey is not merely "fails to decrypt" here: the difference
diagonal `d = (b − a) mod 29` has `d = 0` as its only outlier at **z = −17.25**, and the 28
nonzero diagonals are flat (**cv = 0.061**) where autokey structurally requires lumpy
per-rune-frequency diagonals (**cv ≈ 1.0**).

What produced the deficit is a **soft anti-repeat filter**: a rejection sampler over a
memoryless base that declines to emit the symbol it just emitted, at **80.75% lag-1
suppression**. We later established the filter is *machine-applied, not hand-applied* — pooled
lag-2..8 bleed is **z = +0.65** (zero bleed, and the sign is wrong for a human), and the filter
has no per-line scope at power 1.000: 4 of the 86 residual doublets cross a line boundary
(4.65% against a 4.58% base), where a calligrapher checking the rune they had just written
would leave ≈22.9%.

That filter is also the reason every instrument in this story failed, and it is worth being
precise about why.

## 3. The first failure: the decoder

A rejection sampler consumes key material it does not use. When it declines a symbol, the key
advances but the ciphertext does not. The alignment between key position and cipher position
therefore drifts, unpredictably, as a function of the plaintext.

A *rigid* decoder — one that assumes key position *i* encrypts cipher position *i* — is
therefore wrong almost everywhere after the first rejection. The consequence is severe and
easy to state:

> Under the anti-repeat filter, rigid decoding scores the **correct key** at **−6.835** —
> squarely in the noise band — while a skip-aware beam decoder recovers the same key at
> **−4.170** with **98.9% rune accuracy**.

Reproduce in about two seconds:
`pytest liber-primus/benchmark/ -k rigid_scores_correct`

This single fact invalidates most published "we ruled that family out" claims about LP2 —
including several of this project's own, and including **Round 8's 2.52 × 10⁹ decodes**, which
were run through a decoder that could not have succeeded even had its hypothesis been correct.
Rigid alignment does not make the problem harder. It makes the correct answer *unobservable*.

This was found and fixed. We then spent several further rounds believing the instrument was
repaired. It was not.

## 4. The second failure: the adjudicator

The decoder recovers symbols. A separate component — a quadgram language model trained on
English — decides whether the recovered symbols constitute language. In Round 18, lane L7-A
planted a known-good `sha256_ctr` keystream, decoded it correctly, and scored the result
against nine plaintext registers, 12 replicates per cell, measuring power as the fraction of
replicates clearing the project's own published −5.5 decision bar.

| plaintext register | median score (L=120) | median rune recovery | **power at the −5.5 bar** |
|---|---|---|---|
| `EN_MODERN` (held-out English) | −4.22 | 100% | **1.00** |
| `EN_KJV` (in the training corpus) | −4.11 | 100% | **1.00** |
| `LP1_REAL` (the solved pages' own plaintext) | **−4.33** | 100% | **1.00** |
| `OE` (Beowulf, OE rune poem) | −5.39 | 100% | **0.58** |
| `DE` (Faust, Kafka) | −5.52 | 100% | **0.42** |
| `LATIN` (Caesar, *Principia*) | −5.58 | 100% | **0.33** |
| `EN_HALFVOWEL` (half the vowels dropped) | −5.62 | 100% | **0.33** |
| `CY` (Welsh, *Mabinogion*) | −6.58 | 100% | **0.00** |
| `EN_NOVOWEL` (all vowels dropped) | **−7.60** | 85% | **0.00** |
| `RAND` (uniform runes — the floor) | −7.39 | 33% | 0.00 |
| *wrong key, any register* | ≈ −7.4 | — | 0.00 |

Read the recovery column against the power column. **The decoder was not the problem. The
adjudicator was.** Rune-index recovery of the correct key is 100% for Latin, Old English,
German and Welsh — the decryption *worked* — and the scorer called all four of them noise.
`EN_NOVOWEL` is the case that should be disturbing: at −7.60 the correct key scores **below the
≈−7.4 a deliberately wrong key earns**. An instrument that ranks the right answer beneath a
wrong one is not a weak detector; it is an inverted one.

Every negative result this project had published was stated as though power were 1.0. In fact
**every negative in the repository was an English-register negative**, and no ledger entry said
so until L7-A forced it.

### 4.1 What this does and does not void

It does not void the negatives, and overstating this finding would repeat the error it
diagnoses. The register the Liber Primus demonstrably uses — the plaintext of its own solved
pages — scores **−4.33 at power 1.00**. That register is fully covered. Re-scoring the archived
top-50 candidates under matched models extends the negatives to Latin, Old English and
half-vowel English at rank-1 power.

What changed is the **claim**, not the result. A null from a scorer that cannot see your
hypothesis is not evidence against your hypothesis. Restated coverage bounds now sit on five
ledger entries, each preserving its original wording in a `restated_from` field so the
correction is auditable rather than silent.

## 5. The third failure: the transition model

L7-B then attacked the repaired decoder itself, and found a deeper problem than the scorer.

`beam_decode` admits a key skip only when **every skipped key position would have reproduced
the previous cipher rune**. That test is exact for one specific rejection loop,
`encipher_keyskip`, and for nothing else. A key advance occurring for any other reason has
probability ≈1/29 of being representable at all. It is therefore not *harder* to find — it is
**outside the decoder's model**.

The measured consequence:

| perturbation | correct-key score | does a bigger beam/budget help? |
|---|---|---|
| 1 unrepresentable key advance / 240 runes | −4.91 | — |
| 5 unrepresentable advances / 240 runes | **−6.67** (25.8% recovery) | **no** — identical |
| free drift rate q = 0.05 | **−6.88** | **no** — identical |
| **rejection consumes two draws (`skip_by_two`)** | **−6.90** (25.8% recovery) | **no** — identical |

`skip_by_two` is the sharp case, and the reason this is not a hypothetical. It is a
**one-character change** to a plausible 2013 rejection loop — advance the key by two on
rejection instead of one — it **independently reproduces LP2's observed doublet rate** (0.84%
against the observed 0.664%), and under it the correct key is unrecoverable at every
suppression level and every search budget.

Raising the beam from 400 to 1000 and `max_skip` from 3 to 8 changes these numbers by
**exactly 0.000**. That zero is the whole point of the section: it is the signature of a
*model* error rather than a *search* error, and no amount of compute addresses it. Every
negative this project has published covers exactly one rejection-loop construction.

## 6. The cost, stated plainly

Round 10b had already mandated that language-agnostic statistics be persisted at sweep time,
precisely so that nulls could be re-adjudicated when the instrument improved. Measured
compliance across the sweeps that followed: **0 of 15**.

Because those statistics were never written down, the ~10¹⁰ decodes run between Round 8 and
Round 17 **cannot be retro-fitted**. The decodes are gone. Only their summary verdicts remain,
and those verdicts are now known to have been produced by an apparatus with measured power
near zero over much of the space they claimed to close.

This is the single most expensive lesson in the project, and it is the one that generalises
furthest: **the statistic you fail to persist at measurement time is not recoverable later, at
any price.** A pipeline that discards everything except a pass/fail verdict has silently bet
that its adjudicator will never be found wrong.

A fourth, smaller instrument error belongs here for completeness, because it is the kind that
hides in plain sight: 7 of the 29 runes transliterate to two characters. Measuring recovery on
the transliteration *string* rather than on **rune indices** means a single wrong rune shifts
the alignment and makes a **98.6%-correct decode report as 32% correct**. Score on indices.

## 7. A fourth failure mode: the fixed bar

The project's −5.5 decision bar was a fixed constant applied across sweeps spanning nine orders
of magnitude in trial count. This is invalid, for the ordinary reason: the maximum of N draws
from a null distribution grows with N, so a "hit" that merely matches your own sweep's maximum
is noise with a good publicist.

The corrected family-wise threshold crosses the −5.5 floor at **N\* = 3.13 × 10⁸ trials**. Of
14 historical sweeps re-examined under the corrected bar, the fixed −5.5 was wrong in **14/14**
— usually *too strict*, which is the benign direction, and no verdict flipped. Round 8's
2.52 × 10⁹ decodes is the one sweep in the repository that both exceeded N\* and reported
against the uncorrected floor.

`benchmark/null.py: threshold_for(n_trials, segment_len)` returns the more conservative of the
scale-corrected bar and the historical floor, because at small N the floor binds and at large N
the correction does.

## 8. What survives

Stripping out everything the above undermines, the following are measured, control-validated,
and stated with their coverage bounds intact.

**The verdict: LP2 is OTP-class.** The ciphertext is a full-length keystream under a soft
anti-repeat filter, and it **cannot distinguish** a true external one-time pad
(information-theoretically closed — no compute recovers it) from a keystream **derived from a
short seed** (finite keyspace, brute-forceable). Which of the two it is remains unsettled. This
phrasing is load-bearing and the qualifier is not optional; §9 explains why.

**One search family is genuinely exhausted.** Round 27 ported the screening stage to a
bit-exact C implementation and completed the **first full-space sweep in the project's
history**: all **2³² = 4,294,967,296** Python-2.7 Mersenne Twister integer seeds scored exactly
once under the `pair` relation, with the histogram summing to 2³² exactly. It produced 392,131
candidate flags at **1.31×** the Gumbel prediction — the expected pure-noise shape, no second
mode — and **three** claim-bar crossers, **all three** oracle-adjudicated NOISE-CROSSER under a
three-clause gate. C-versus-Python parity on 10,971 re-scored flags: **max |Δ| = 0.0 exactly**.
Lane verdict: NULL, branch exhausted, conditional on its three named conditionals.

**The artifact is machine-rendered, and the toolchain is narrowed.** The 2014 master is a
rendered PDF whose embedded ICC profile is **byte-identical to Ghostscript 9.06's Artifex
`srgb.icc`**, bounding the renderer to **GS 9.01–9.15**. The runes are a deterministic vector
font with no glyph-variant channel; there is no sub-pixel positioning channel; the page images
are byte-authentic 400-DPI renders with no recoverable steganography (56/56 SHA-1s match the
archived dump); the onion images survived their first genuine key-attack at 24,078 extractions,
0 hits; and 74 of 74 ornament bands, read under a nine-register panel, show no language.

**The elimination map.** 172 ledger entries, each carrying its pre-registered threshold, its
positive-control status, its honest coverage bound, and the concrete condition that would
reopen it. Unsound negatives — entries claiming a negative whose instrument was never shown
able to detect a planted signal — **0**.

## 9. Three retractions

This project has twice published a terminal verdict that was wrong, and both times the error
had the same shape: **a measured bound got written up as a settled conclusion.**

1. **"Information-theoretically unsolvable."** Retracted. The ciphertext cannot separate a true
   pad from a short-seed-derived keystream, and the control that proves the distinction matters
   planted exactly such a keystream and **recovered it at 98.9%** through this project's own
   decoder. The unqualified claim had foreclosed a real, tractable line of attack for months.
   The narrowed claim is *OTP-class*.
2. **"Seeded PRNGs are closed."** Retracted. The reality was 10 generators at roughly 3% of
   each seed space. PHP `mt_rand` went untested for months behind that sentence.
3. **"Keytexts are dead by mechanism."** Retracted. They are dead by *exhaustion*, which is a
   weaker and differently-shaped claim.

Add to these the four instrument defects above, a silently truncated 118 MB data input, and a
stale "the derived-key lane is untested" line that survived in the README after the lane had
become one of the most-swept families in the repository.

We report these not as penance but as calibration. A research artifact that has never
corrected itself is not thereby more reliable; it is less audited. The appropriate inference
from a visible correction log is that the log exists.

## 10. The generalisation

Nothing above is specific to runes, and the failure modes are not exotic. They are what happens
whenever a measurement apparatus is treated as infrastructure rather than as an instrument.

1. **A null from an unvalidated instrument is not a negative — it is an unknown wearing a
   negative's clothes.** Plant a known-good signal, prove recovery, *then* trust silence. This
   is one afternoon of work and it is the highest-leverage afternoon in the project.
2. **Name all three conditionals on every negative:** the space you swept, the *model* your
   detector can represent, and the *register* your adjudicator can see. Two of the three are
   invisible by default, and both of ours were wrong.
3. **Persist the raw statistic, not the verdict.** What you discard at measurement time is
   unrecoverable at any later price. 10¹⁰ decodes proved this.
4. **A fixed threshold is invalid at scale.** Correct for trial count or report nothing.
5. **When a bigger budget changes the result by exactly 0.000, stop tuning.** That zero is a
   model error announcing itself. Compute will not fix it.
6. **Audit closures, not spaces.** Every genuinely new finding in this project — all of them —
   came from auditing a closure, an instrument, an artifact or an input. **None** came from a
   new key-space sweep. That ratio is the most actionable number here.

Point 6 deserves emphasis for anyone running large automated search. We ran agent armadas
across 30 rounds, concurrent attack lanes each red-teamed by a separate adversarial lane whose
only job was refutation. The lanes that produced value were overwhelmingly the ones pointed at
*our own prior conclusions*. Scaling the search was cheap and nearly worthless. Scaling the
scepticism was expensive and paid every time.

## 11. Reproducibility

The repository is designed to be falsified rather than believed. Four commands, about a minute:

```bash
python3 liber-primus/tests/validate.py              # the rig reproduces every KNOWN solved page (6/6)
python3 liber-primus/verify_solution.py --selftest  # the judge accepts a good key, rejects a bad one
python3 -m pytest liber-primus/benchmark/ -q         # 8 instrument gates, both directions
python3 liber-primus/analysis/handoff/validate_ledger.py   # must report 0 unsound negatives
```

**If any of those fail, distrust everything in this paper.** That is the intended
relationship, and it is enforced in CI so the instruction stays true between commits rather
than only at the moment someone checked by hand.

Every claim above resolves to a reproduce command in
[`liber-primus/LEDGER.json`](liber-primus/LEDGER.json). The ciphertext is pinned by SHA-256;
103 data inputs are pinned by SHA-256 with provenance chains and mirrors in
[`handoff/capsule/MANIFEST.json`](liber-primus/handoff/capsule/MANIFEST.json); the trust-surface
files are bound to this release by EOL-independent git-blob hashes in
[`PROVENANCE.md`](PROVENANCE.md) §4.

A claimed solution is adjudicated by `verify_solution.py` against criteria fixed in advance —
the English band, at least two pages passing independently, and beating a size-matched shuffle
null. Run `--selftest` first; it validates the judge before the judge validates you.

## 12. Limitations, and what is open

**Nothing in this repository is currently running.** Every sweep was killed by a host reboot on
2026-09-15 and none was resumed. The second Round 27 lane is parked at **44.14%** of its 2³²
space; Round 28's 25-cell successor queue **never fired**; Round 28's L3 lane finished its
sweep and was **never written up**, so that result does not exist as far as the ledger is
concerned. Coverage, state files and resume routes:
[`handoff/PARKED-SWEEPS.md`](liber-primus/handoff/PARKED-SWEEPS.md).

This project stopped because it ran out of machine and out of instrument, not out of ideas, and
it does not have the capability to push a solve on its own.

Three further honest limits:

- **The transcription has never had a from-scratch independent re-read.** The entire statistical
  case rests on it. Label-free clustering of glyph bitmaps reproduces the canonical partition,
  and an independent blind instrument agrees with the canon 100% on the contested bytes — but
  whole-page AI vision scored 0.145 alignment (noise) in 2026. A per-rune re-transcription at
  ≥99% accuracy on the solved control pages is the one task that could *invalidate the map*
  rather than merely extend it, and it remains undone.
- **The negatives remain conditional on nine registers and one transition model.** Broader than
  when they were English-only and single-construction, but still bounded. A tenth language or a
  second rejection-loop family is uncovered by construction.
- **The `/dev/urandom` branch is untouchable.** If the pad was seedless and unrecorded, then no
  instrument and no compute ever recovers it, and nothing in this paper applies. That branch is
  real and may well be the true one. The author's subjective prior is that it is more likely
  than not — but that is a **judgement, not a measurement**: it rests on the maker's evident
  opsec and defaults-only tooling, there is no experiment behind it, and it appears in no ledger
  entry. Treat it as the author's opinion and discount accordingly. What is not opinion is that
  it is **not the only branch**, and that this project has three times found a branch it had
  called closed to be open.

---

## Citing this

Cite the specific round or lane and its verdict file, not the repository as a whole, so a
reader can check the individual claim: e.g. *"Round 18 lane L7-A
(`liber-primus/analysis/round18/L7-redteam/RESULTS.md`)"*. Metadata in
[`CITATION.cff`](CITATION.cff); release `v2026.10.5-round30-handoff`.

If you solve the Liber Primus using this archive's ledger, benchmark, oracle or doctrine, the
honest and sufficient credit is a line naming it as the source of the negative map you did not
have to redraw. The solve is yours.

**This paper does not claim a solve, and it does not claim to identify Cicada 3301's authors —
no falsifiable attribution exists.** It claims priority over a scoped negative map and a
method. License MIT; see [`PROVENANCE.md`](PROVENANCE.md).

## Sources for every figure in this paper

| claim | file |
|---|---|
| Ciphertext identity, measured statistics, acceptance criteria | `liber-primus/PROBLEM.json` |
| Scorer power table by register (§4) | `liber-primus/analysis/round18/L7-redteam/RESULTS.md` §A |
| Beam transition-model envelope, `skip_by_two` (§5) | `liber-primus/analysis/round18/L7-redteam/RESULTS.md` §B |
| Rigid vs. beam on the correct key (§3) | `liber-primus/benchmark/gates.py`, `benchmark/README.md` |
| Family-wise threshold, N\* (§7) | `liber-primus/benchmark/null.py` |
| Retraction of the unsolvability claim (§9) | `liber-primus/analysis/round12/D3/RESULTS.md` |
| Autokey refutation, filter characterisation (§2) | `liber-primus/ELIMINATION-LEDGER.md`, `analysis/round17/P4_filter/RESULTS.md` |
| Full 2³² sweep closeout (§8) | `liber-primus/analysis/round27/S1-CLOSEOUT.md` |
| Ghostscript/ICC toolchain bound (§8) | `liber-primus/analysis/round30/SYNTHESIS.md` |
| Ornament-band nine-register read (§8) | `liber-primus/analysis/round19/finite/RESULTS.md` |
| All 172 entries with thresholds and coverage | `liber-primus/LEDGER.json` |
| The research discipline (§10) | `liber-primus/ARMADA-DOCTRINE.md` |
| Parked sweeps and real coverage (§12) | `liber-primus/handoff/PARKED-SWEEPS.md` |
| Capability-blocked work with unpark thresholds (§12) | `liber-primus/handoff/PARKED.md` |
