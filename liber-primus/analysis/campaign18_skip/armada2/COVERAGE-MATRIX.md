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

**Scale (this project):** English solve ≈ −4.0…−4.35 · confirm threshold −5.5 · false-positive
ceiling −6.82 · noise floor ≈ −7.5. Every "null" below sits in the −5.9…−6.9 noise band.

---

## A. Key-guessing / running keys
| Attack | Historical verdict | Skip-lens status | Evidence |
|---|---|---|---|
| Referenced texts as running keys (Mabinogion, Self-Reliance, King in Yellow, Agrippa, Book of the Law, rune poems, solved plaintext) | ❌ rigid null | **DONE-NULL** | `RUN-referenced.log` (best −5.88); + `RUN-armada18` re-tests the *real* Cornelius Agrippa (old file was Gibson's poem) |
| Thematic esoterica + 15 verified + 82-text armada (Campaigns III/XII/XIII) | ❌ rigid null | **RUNNING** | `RUN-fullcorpus.log` (122 texts, ~½ done, all noise) |
| **Literary running keys generally** — *the community barely tested these on the runic pages* (they were early-puzzle coordinate lookups, not keystreams) | mostly **untested** | **RUNNING** | `RUN-armada18` (42 texts) + `RUN-armada19` (47 texts: Bibles, Homer, Dante, Blavatsky, Aristotle…) |
| Cicada's OWN text as running key (LP1 plaintext fwd/rev, LP1 runes, PGP bodies, koans) | untested | **DONE-NULL / RUNNING** | in `armada18`; also fed to interrupter driver |
| Number-theoretic keystreams (primes, φ, totient, gaps, Fibonacci, π/e/φ digits) | ❌ rigid null | **DONE-NULL** | `RUN-rosetta.log`, `RUN-numeric.log` (874 streams, best −5.57) |
| PRNG keystreams (LCG/BBS/MT, Cicada seeds) | ❌ rigid null | **DONE-NULL** | `RUN-numeric.log` |
| Extended numeric (payload-as-key all offsets, Mayan key, onion hex, page-seeded, Catalan/Lucas…) | partial | **VALIDATED+RUNNING** | `armada2/numeric2_skip.py` (gate ok, smoke −6.11) → `RUN-numeric2-full.log` |
| Short / periodic Vigenère keywords | ❌ rigid null (flat IoC) | **VALIDATED+RUNNING** | `armada2/keywords_skip.py` — skip desyncs a periodic key, so the IoC exclusion may not bind; ~620 keywords, gate ok, smoke −6.16 → `RUN-keywords-full.log` |

## B. Self-referential / stream ciphers
| Attack | Historical verdict | Skip-lens status | Evidence |
|---|---|---|---|
| **Plaintext & ciphertext autokey** — *the community's #1 hypothesis* | ❌ excluded **RIGID only** (Campaign X) | **VALIDATED+RUNNING** | `armada2/autokey_skip.py` — autokey UNDER the doublet-skip filter, never tested. Gate: rigid −7.60/5% vs beam −4.15/**100%**; smoke −6.65 → `RUN-autokey-full.log` |
| First-difference / integral inversion | ❌ rigid null | **VALIDATED+RUNNING** | `armada2/selfref_skip.py` → `RUN-selfref-full.log` |
| Page-on-page key reuse / in-depth | ❌ rigid null | **VALIDATED+RUNNING** | `selfref_skip.py` (self-keying + shared-keystream pair tests) |
| Short-history ciphertext-feedback (k=1–3) | untested | **VALIDATED+RUNNING** | `selfref_skip.py` |
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
artifact of rigid key alignment now has a **validated** skip-tolerant decoder and has been (or is
being) re-run under it — all null so far. The families still marked excluded are excluded by
alignment-independent statistics (IoC / doublet deficit / provenance) that a key-skip cannot
change, and the only lane the skip lens cannot reach is an **external** key that was never in any
corpus (the lost AN END page).*

**Open, honestly:** (1) the VALIDATED+RUNNING full sweeps (autokey, interrupter, selfref, keywords,
numeric2, armada19) are executing now — statuses flip to DONE-NULL on completion; (2) the
interrupter+skip full run is bounded to the **highest-prior** texts (referenced + Cicada-own),
not the entire 122-corpus × offset space — marginal, since the interrupter-blind skip-corpus
sweep is already null; (3) Hill/digraphic ciphers are outside the skip lens by nature and rest on
their prior exhaustive null.
