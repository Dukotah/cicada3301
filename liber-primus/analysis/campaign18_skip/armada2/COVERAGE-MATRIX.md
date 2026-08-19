# LP2 — Skip-Lens Coverage Matrix

**Purpose.** Campaign XVIII proved that any RIGID-alignment running-key/keystream null is
*unsound* for LP2, because the ~83% doublet filter most plausibly SKIPS key symbols and
desyncs the key. This matrix records, for **every** historical attack family in
`ELIMINATION-LEDGER.md`, whether it has now been re-tested under the validated
**skip-tolerant** decoder — or why the skip lens cannot change its verdict.

**Status legend**
- `DONE-NULL` — full skip-aware run complete, null (log cited)
- `RUNNING` — full skip-aware sweep in progress (this session)
- `VALIDATED+RUNNING` — new decoder built + passed a planted-key gate; full run chained now
- `EXCLUDED-INDEP` — excluded by a statistic (IoC / doublet / provenance) that skip **cannot**
  change → the skip lens does not apply; the prior null stands
- `EXTERNAL` — not a compute lane (the key would have to physically exist off-corpus)

---

## 0. FILTER-MECHANISM coverage (added 2026-08-19, Round 12 front D1)

RECON-B item **B-16** (Round 10) flagged a real gap in this matrix: Campaign XVIII built and
validated its beam decoder against the **key-SKIP** mechanism (when a doublet would occur the
key index ADVANCES, so the key DESYNCS), whereas Campaigns X/XI actually PIN the mechanism as a
soft anti-repeat **value-REWRITE of the output** (`campaign10.soft_norepeat_pad` /
`campaign11.soft_pad`: the ciphertext rune is RESAMPLED in place and the key stays SYNCED).
This matrix had **no rewrite row**, so every "DONE-NULL" below rested on an unverified
robustness assumption. Round 12 D1 ran the decisive test.

| Mechanism | Meaning | Decoder validated against it? | Evidence |
|---|---|---|---|
| **Key-SKIP** (desync) | doublet ⇒ advance the key index | ✅ **VALIDATED** — planted key recovered −4.27…−4.32, 95–100% rune match | `campaign18_skip/skipdecode.py` gate; `round12/D1_redteam/rewrite_gate.py` ARM 1 |
| **Value-REWRITE** (in-place) | doublet ⇒ resample the ciphertext rune, key stays synced | ✅ **VALIDATED 2026-08-19** — planted key recovered **−4.45…−4.70 (95–98% match)** at page length, −4.80…−5.16 on 250 runes at up to 7% corruption | `round12/D1_redteam/rewrite_gate.py` ARM 2 |

**Consequence.** The rewrite mechanism corrupts only ~2.8% of positions on the real cipher
((3.45−0.66)/3.45 × 3.45%), and it does **not** desync the key, so even plain rigid decode
recovers a correct key under it. A correct keytext under the pinned rewrite mechanism would
therefore have scored **~−4.5**, against the **−5.75…−5.88** the actual ~200-text sweeps
produced. **The nulls below DO cover the rewrite mechanism**; no real keytext was hiding at
~−4.5 and being mis-scored as noise. B-16 is closed, not confirmed.

**Wording fix this forces (D1 + D3 agree).** The keytext closure should be cited as
*"by exhaustion over ~200 texts, verified robust to both the skip and rewrite constructions"* —
**not** *"by mechanism, independent of which text."* The conclusion survives; the argument for
it changes.

**Scale (this project):** English solve ≈ −4.0…−4.35 · confirm threshold −5.5 · false-positive
ceiling −6.82 · noise floor ≈ −7.5. Every "null" below sits in the −5.9…−6.9 noise band.

---

## A. Key-guessing / running keys
| Attack | Historical verdict | Skip-lens status | Evidence |
|---|---|---|---|
| Referenced texts as running keys (Mabinogion, Self-Reliance, King in Yellow, Agrippa, Book of the Law, rune poems, solved plaintext) | ❌ rigid null | **DONE-NULL** | `RUN-referenced.log` (best −5.88); + `RUN-armada18` re-tests the *real* Cornelius Agrippa (old file was Gibson's poem) |
| Thematic esoterica + 15 verified + 82-text armada (Campaigns III/XII/XIII) | ❌ rigid null | **DONE-NULL** | `RUN-fullcorpus.log` (122 texts × 55 pages, **0 hits**, best −5.808) |
| **Literary running keys generally** — *the community barely tested these on the runic pages* (they were early-puzzle coordinate lookups, not keystreams) | mostly **untested** | **DONE-NULL** | `RUN-armada18.log` (41 texts, 0 hits, best −5.786) + `RUN-armada19.log` (47 texts: Bibles, Homer, Dante, Blavatsky, Aristotle… — 0 hits, best −5.754) |
| Cicada's OWN text as running key (LP1 plaintext fwd/rev, LP1 runes, PGP bodies, koans) | untested | **DONE-NULL** | null in `RUN-armada18.log`; also in the interrupter driver corpus |
| Number-theoretic keystreams (primes, φ, totient, gaps, Fibonacci, π/e/φ digits) | ❌ rigid null | **DONE-NULL** | `RUN-rosetta.log`, `RUN-numeric.log` (874 streams, best −5.57) |
| PRNG keystreams (LCG/BBS/MT, Cicada seeds) | ❌ rigid null | **DONE-NULL** | `RUN-numeric.log` |
| Extended numeric (payload-as-key all offsets, Mayan key, onion hex, page-seeded, Catalan/Lucas…) | partial | **DONE-NULL** | `RUN-numeric2-full.log` (**0 hits**, best −5.745) |
| Short / periodic Vigenère keywords | ❌ rigid null (flat IoC) | **DONE-NULL** | `RUN-keywords-full.log` — ~620 keywords full run, **0 hits**, best −6.021; the flat-IoC exclusion survives the skip lens |

## B. Self-referential / stream ciphers
| Attack | Historical verdict | Skip-lens status | Evidence |
|---|---|---|---|
| **Plaintext & ciphertext autokey** — *the community's #1 hypothesis* | ❌ excluded **RIGID only** (Campaign X) | **DONE-NULL** | `RUN-autokey-full.log` — 45 primers × P/C-autokey × both signs × 55 pages, **0 hits**, global best −6.627. The gate (rigid −7.60/5% vs beam −4.15/**100%**) makes this null load-bearing: a skip-filtered autokey would have been found |
| First-difference / integral inversion | ❌ rigid null | **DONE-NULL** | `RUN-selfref-full.log` (firstdiff best −6.17, integral best −6.08) |
| Page-on-page key reuse / in-depth | ❌ rigid null | **DONE-NULL** | `RUN-selfref-full.log` — selfkey best −6.50; NB the `shared best=-2.80` line is on the **crib-drag scale** (different-key control scores −3.03 there, flagged WEAK in-log), not a score_norm hit |
| Short-history ciphertext-feedback (k=1–3) | untested | **DONE-NULL** | `RUN-selfref-full.log` (best −7.06, at the floor) |
| Corpus-wide periodicity / key reuse | ❌ null | **DONE** | Campaign XIV; skip does not create periodicity where autocorrelation shows none |

## C. Different cipher classes — skip lens does NOT apply
| Attack | Historical verdict | Skip-lens status | Why skip can't rescue it |
|---|---|---|---|
| Fractionation (bifid / Polybius) | ❌ dead | **EXCLUDED-INDEP** | Every period gives IoC·N 1.39–1.55 — can't reach the flat 1.00; a key-skip changes alignment, not the fractionation IoC |
| Substitution / homophonic | ❌ dead | **EXCLUDED-INDEP** | Preserves IoC; flat 1.00 ≠ English 1.78 regardless of key timing |
| Multiplicative / prime gematria | ❌ excluded | **EXCLUDED-INDEP** | Mechanistic (no closed multiplicative group mod 29) |
| Transposition-only | ❌ dead | **EXCLUDED-INDEP** | Doublet-transparent; the *suppressed* doublet rate falsifies it |
| Block / permutation / Lehmer | ❌ dead | **EXCLUDED-INDEP** | F-run lengths have no peak |
| Hill 2×2 / 3×3 (digraphic) | ❌ rigid null | **EXCLUDED-INDEP (prior null stands)** | Not a running-key/keystream cipher → the skip lens has nothing to re-align; historical exhaustive + crib-drag null holds |

## D. Inputs & side channels
| Attack | Historical verdict | Skip-lens status | Why |
|---|---|---|---|
| Transcription correctness | ✅ verified | **EXCLUDED-INDEP** | 3 independent lineages + label-free audit; alignment-irrelevant |
| Independent vision re-transcription | ⚠️ not viable | **EXCLUDED-INDEP** | — |
| Image provenance / steganography | ✅/❌ none | **EXCLUDED-INDEP** | 56/56 SHA1 match; OutGuess null |

## E. pp49–51 base-60 payload
| Attack | Historical verdict | Skip-lens status | Evidence |
|---|---|---|---|
| Payload as polyalphabetic key over runes | ❌ rigid null | **DONE-NULL** | `RUN-payload-skip.log` (best −6.76, skip-aware) |
| Payload as enciphered ciphertext itself | ❌ null | **DONE-NULL** | `RUN-payload-ct.log` |
| Payload structural (RSA/hash/format/XOR/image) | ❌ null | **DONE** | Campaign VII/IX/XII (alignment-irrelevant) |

## F. Attribution / external
| Attack | Status | Note |
|---|---|---|
| AN END deep-web page (the external key) | **EXTERNAL** | Tor v2 dead; the only place a key could physically exist. Not a compute lane. |
| 2017 PGP / attribution / stylometry | done | Alignment-irrelevant; prior nulls stand |

---

## Prior-art honesty (from the community-research pass)
A drift-tolerant decoder is **not** wholly new: **relikd/LiberPrayground** searches *which ᚠ
runes are interrupters* (binary on/off, exhaustive / genetic), re-syncing a **fixed skip-by-one**
key, scored by IoC; and the "skip to the (n+1)th key symbol to suppress doublets" *idea* was
articulated years ago on the community boards. What is **new here** (per that research, which
searched hard and found no public equivalent): a **beam/probabilistic search over *variable*
key-advance with language re-scoring**, the **autokey-under-doublet-skip** decoder, and the
systematic **literary-running-key** sweep the community largely skipped. Our novelty claim is
calibrated to *those*, not to "we invented skips."

## Verdict — can we say "everything re-tested with the new lens"?
**Yes, with this precise wording:** *Every LP2 attack family whose prior null could have been an
artifact of rigid key alignment now has a **validated** skip-tolerant decoder and has been
re-run under it — **all null, 0 hits** (all lanes complete as of 2026-07-27). The families
still marked excluded are excluded by
alignment-independent statistics (IoC / doublet deficit / provenance) that a key-skip cannot
change, and the only lane the skip lens cannot reach is an **external** key that was never in any
corpus (the lost AN END page).*

**Open, honestly:** (1) ~~running sweeps~~ — **ALL lanes have now completed, all null, 0 hits**,
including the interrupter+skip full run (2026-07-27: `RUN-interrupter-full.log`, global best
−5.911, final 7 pages via 6 parallel `--pages` workers); (2) the interrupter+skip full run is
bounded to the **highest-prior** texts (referenced + Cicada-own), not the entire 122-corpus ×
offset space — marginal, since the interrupter-blind skip-corpus sweep is already null; (3)
Hill/digraphic ciphers are outside the skip lens by nature and rest on their prior exhaustive
null.

## Non-additive ct-feedback: mod-29 COEFFICIENT SWEEP (2026-07-28, novel_cipher lane)
Prior selfref_skip.decode_ctfeedback fixed coeffs=[1,1,1] (unit feedback) -> -7.06..-7.22.
The uncovered corner = the mod-29 linear coefficient space:
  key[i] = seed[i] + sum_{t=1..k} a_t*C[i-t] mod 29,  a_t in {0..28}, k=1..3, both signs,
  seeds = {const0, const1 (autonomous/seed-free), mabinogion}.
Script: analysis/campaign18_skip/ctfeedback_coeffs.py  (gate PASSES: plants a1=7 autonomous
feedback, sweep recovers -4.13/100%, unit-coeff decode misses -7.51/7%).
Result on p0/p5/p20: best = -6.86 / -6.91 / -6.89. All plaintexts gibberish.
VERDICT: NULL (noise floor). Order-2/3 ciphertext-feedback with linear mod-29 coeffs shows
NO signal above -5.2. This closes the last additive-adjacent corner the OTP proof did not exclude.
