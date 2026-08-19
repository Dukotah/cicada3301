# Liber Primus — Elimination Ledger

**Purpose.** A single, complete, reproducible record of *everything that has been
tried* against the unsolved Liber Primus pages (LP2, onion7 `0`–`55`) and *why each
was eliminated* — written so the next researcher (human or agent) can use this repo
as footing instead of re-running dead ends. If you are here to attack LP2, **read
this file first**, then go to the deeper doc each row points to.

> **Trust anchor.** Every negative result below is only meaningful because the rig
> is validated: `python tests/validate.py` reproduces *every known solved page*
> (2012/2013 puzzles + solved LP pages) from the canonical runes. Run it first. If
> it passes, the tooling that produced these eliminations is sound.

---

## The one-paragraph honest verdict

From the **ciphertext alone**, the unsolved runic pages are **OTP-class**: a full-length
keystream whose output was deliberately filtered to avoid writing the same rune twice in a
row (~83% suppression — Campaign XI). "OTP-class" is a precise claim and it is weaker than
"one-time pad": the ciphertext is **indistinguishable between a true external pad
(information-theoretically closed) and a short-seed *derived* keystream (finite keyspace,
brute-forceable)**. The derived-key dictionary lane is untested; only running it settles
which. The transcription is **not** the blocker (verified three independent ways). If the
keystream is a true external pad, the only path to a solve is **external** — the key itself,
most plausibly via the never-recovered "AN END" deep-web page — because for any chosen
plaintext a valid structureless key exists. If instead it is derived from a short seed, the
keyspace is enumerable and compute *does* apply.

> **⚠️ Superseded 2026-08-17 (Round 12, front D3 — FOUND-ERROR).** This paragraph previously
> ended: *"it is information-theoretically unsolvable **without the external key** … Nobody
> should claim LP2 is 'solvable with more compute / more AI' — the math says otherwise."*
> That promoted **one member** of an indistinguishability class (a true external pad) into a
> property of the whole class. `analysis/round10b/B4-otp-steelman/b4_results.json` (G5) shows
> the ciphertext cannot separate an external pad from a SHA-256 counter-mode keystream derived
> from a short seed — `"separated": false`, max |z| = 1.60 across the 6-statistic battery — and
> a short-seed-derived keystream has a finite, enumerable keyspace. D3's positive control
> planted such a keystream (seed `CICADA3301`) under the repo's own pinned soft anti-repeat
> filter and **recovered it** through the project's own beam decoder (−4.170, 98.9%
> char-recovery, vs −7.349 on a wrong seed), so "no compute recovers it" is demonstrably false
> over that lane. Round 10's `SYNTHESIS.md` already stated the correction ("OTP-*class*, not a
> unique external pad"); it had never reached this headline. The reasoning is kept; the claim is
> narrowed, not withdrawn. See `analysis/round12/D3/RESULTS.md`. The settling test is
> **RECON-A item B-04** (derived-key dictionary), in flight as Round 13.

**What this project can honestly claim:** every attack *we could concretely construct*
has been run and falsified, and the cipher's mechanism is now described to a
parameter — which appears to be *ahead* of the published community state of the art
(which still stops at "autokey/custom"). **What it cannot claim:** a solve, or a name.

> **Update 2026-08 (Rounds 1–8).** This section used to end "…cannot claim that the space
> of all conceivable external keytexts is exhausted." Round 7 closed that — **by exhaustion
> over ~200 texts, now verified robust to both the skip and the rewrite construction** — and
> **Round 8** then measured the pad's **entropy** (2.52×10⁹ seeded-PRNG decodes, 0 hits)
> rather than only observing the absence of key structure. See the Rounds index below.
>
> > **⚠️ Corrected 2026-08-17 (Round 12, fronts D1 and D3).** This update used to read "*Round 7
> > closed that **by mechanism** rather than by exhaustion: any keytext is dead both rigidly
> > (doublet-excluded) and skip-aware (un-anchorable), independent of which text it is.*" Round
> > 10's RECON-B/B-16 showed the mechanism half is unsound under the repo's *own* pinned
> > construction: a soft anti-repeat **rewrite** of the output sets the doublet rate, so the
> > deficit carries no discriminating power over key *type* and "dead rigidly
> > (doublet-excluded)" does no work. Round 12's D1 ran the decisive test
> > (`analysis/round12/D1_redteam/rewrite_gate.py`): under the rewrite mechanism the correct
> > running key still decodes to **−4.45…−4.70 (95–98% rune match)**, versus the **−5.75…−5.88**
> > the real ~200-text sweeps actually produced — so the sweeps *do* cover the rewrite model and
> > no real keytext was hiding at ~−4.5. **The conclusion survives; the argument for it changes**
> > from "by mechanism, independent of text" to "by exhaustion over ~200 texts, verified robust
> > to skip and rewrite." A genuinely new candidate text is therefore a weak lead, not a dead
> > one. Three verified-absent texts (Blake's *Jerusalem* / *Milton* / *The Four Zoas*) were
> > killed at Round 7's Gate #1 on the mechanism argument alone and were never run.

---

## Statistical profile (the thing every attack must explain)

Reproduce: `python analysis/run_stats.py`. Over 12,956 unsolved runes:

- **IoC·N = 1.000** — at the random floor. Perfectly flat, not merely "near random."
- **Doublet rate 0.66%** vs 3.45% random — a ~5× *deficit* (the one real anomaly).
- **Consecutive differences** `c[i]−c[i−1] mod 29` flat-random **except a hole at 0**.
- Shannon entropy ≈ 4.857 bits (max for 29 symbols ≈ 4.858).

Any proposed mechanism must reproduce **both** IoC·N ≈ 1.000 **and** doublet ≈ 0.66%.
Almost everything fails one or the other.

---

## Master elimination table

Grouped by attack family. "Where" = the deeper writeup + the reproduce command.

### A. Key-guessing / running keys
| Attack | Verdict | Why it's ruled out | Where |
|---|---|---|---|
| Every **periodic key**, length 1–40 (Friedman/column-freq, both directions, +Atbash) | ❌ dead | Best score −5.8 = gibberish; validated to recover a known 7-symbol key from synthetic ct | `attack.py vigauto` |
| **Running keys** from the referenced texts (Mabinogion, Self-Reliance, King in Yellow, Book of the Law, Agrippa) + solved-page plaintext | ❌ dead | All offsets, both directions, +Atbash → nothing | `attack.py runningkey` |
| **Cicada-thematic esoterica** as running keys (Mathers/Kabbalah Unveiled, alchemical/Gnostic sources) | ❌ dead | Best −6.049, near-random band | Campaign III `analysis/foundation/` |
| **Expanded thematic corpus** (15 verified texts: Tao Te Ching, Bhagavad Gita, Meditations, Zarathustra, I Ching, Beowulf, Poe/Gold-Bug, Gilgamesh, Dhammapada, Walden, Whitman, Rubáiyát, Gibran, Augustine, Sun Tzu) | ❌ dead | Content-verified; all offsets/signs/Atbash; best −6.048, 0 over threshold | Campaign XII `analysis/CAMPAIGN-XII-FINDINGS.md` |
| **Armada corpus — 82 more never-tested texts** across 10 lanes (Hermetica/alchemy, occult/magick, Kabbalah/Gnostic, world scripture, Norse/runic, English canon, philosophy, math/science, cypherpunk, mysticism/poetry: Corpus Hermeticum, Kybalion, full Crowley Liber set, Enochian Calls, Book of Enoch, Zohar, Koran, Eddas, Paradise Lost, Euclid, Principia, manifestos, Rumi…) | ❌ dead | 13-agent Workflow; verified sources; best −5.809, 0 over threshold, verify phase found nothing | Campaign XIII `analysis/CAMPAIGN-XIII-FINDINGS.md` |
| **Cicada's own PGP prose** as key material | ❌ dead | nothing readable | ARMADA-20 `analysis/ARMADA-20-FINDINGS.md` |
| **Number-theoretic keystreams** (primes, φ, iterated φ, prime gaps, cumsums, page-seeded, all Fibonacci-mod-29 seeds) | ❌ dead | nothing | `attack.py keystream`, `analysis/doublet_probe.py` |
| **PRNG keystreams** (BBS / LCG / Mersenne Twister seeded) | ❌ dead | nothing | ARMADA-20 |
| **Mechanistic reason keytext-hunting was doomed** | ⚠️ ~~insight~~ **superseded** | *Any* natural-English running key injects ~3.3% doublets — which are **absent**. Wrong *mechanism*, not wrong *text*. **This argument is void** — see the note below. | Campaign IV `analysis/structure/` |

> **⚠️ Superseded 2026-08-12/17 (Round 10 RECON-B/B-16, closed by Round 12 D1).** The last row
> above is kept for its reasoning but no longer carries weight. The repo's own pinned
> construction is a **soft anti-repeat rewrite of the output** (p_keep≈0.18, `FINAL-SYNTHESIS.md`),
> which erases exactly the ~3.3% doublets a natural-English running key injects. Under that model
> the deficit is set by the filter, not by the key, so it cannot discriminate key *type* at all.
> What actually closes the keytext family is the **~200-text exhaustion sweep** (best −5.75…−5.88
> against an English band of −4.0…−4.35), and Round 12's `D1_redteam/rewrite_gate.py` verified
> that sweep is robust to *both* constructions: under key-**skip** the correct key recovers at
> −4.27…−4.32 (95–100% match, the positive control) and under value-**rewrite** at −4.45…−4.70
> (95–98% match). Cite this family as *closed by exhaustion, verified robust to skip and rewrite*.

### B. Self-referential / stream ciphers
| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Plaintext & ciphertext autokey** (the community's decade-old leading hypothesis) | ❌ **excluded** | Simulated directly: all 4 autokey variants sit at 3.3–4.2% doublets (random band). Autokey does **not** suppress doublets. | Campaign X `analysis/CAMPAIGN-X-FINDINGS.md` |
| **First-difference / integral** inversion | ❌ dead | Integrating normalizes doublets to ~3.55% but the underlying stream stays flat-random. Deficit IS a differencing artifact; no plaintext. | `analysis/armada/FOLLOWUP-TESTS.md` |
| **Page-on-page key reuse / in-depth** | ❌ dead | No two pages show a shared-keystream difference signal | ARMADA reports |
| **Corpus-wide periodicity / key reuse** (any lag 1–6478, period 41–2000) | ❌ dead | Prior test was per-page/no-skip only; now scanned book-wide: 0 coincidence peaks >5σ, column IoC flat (max 1.087) | Campaign XIV `analysis/campaign14/probes.py` P1–P2 |
| **Generalized-combiner feedback / many-to-few homophonic** | ❌ dead | Beyond additive autokey & bijective substitution: off-diagonal bigram χ² vs filtered null = +0.81σ (flat), no second-order structure | Campaign XIV P4 |
| **Unfiltered one-time pad** | ❌ dead | Plain pads sit at ~3.45% doublets too — the deficit needs **active** suppression | Campaign X |

### C. Different cipher classes
| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Fractionation** (bifid / Polybius) | ❌ dead | Every period gives doublet 3.6–4.6% and IoC·N 1.39–1.55 — can't reach flat 1.00 or the deficit | `analysis/OPEN-AVENUES.md` |
| **Substitution / homophonic** | ❌ dead | Preserves IoC; can't turn flat (1.00) into English (1.78) | `analysis/crypto_rigor.py` |
| **Multiplicative / prime gematria** substitution | ❌ excluded | Mechanistically ruled out, not merely unobserved | Campaign V `analysis/stones/` |
| **Transposition-only** | ❌ dead | Doublet-transparent; falsified by the *suppressed* doublet rate | `analysis/crypto_rigor.py` |
| **Block / permutation / Lehmer decode** (F-delimited) | ❌ dead | F-run lengths have no peak (modal share 0.055) | `analysis/crypto_rigor.py` A |
| **No-repeat / collision-inversion** decodes (delta≠0 family) | ❌ dead | IoC stays flat (≤1.04) | `analysis/crypto_rigor.py` C |
| **Hill 2×2 exhaustive + 3×3, crib-dragging** | ❌ dead | nothing | ARMADA-20 |

### D. Inputs & side channels (is the ciphertext even what we think?)
| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Transcription correctness** (is canon a mis-read?) | ✅ verified correct | 3 independent lineages rune-for-rune identical (13136/13136); trained glyph classifier 99.2% corroborates canon; spot-audited vs authentic images | Campaign V; `analysis/transcription/TRANSCRIPTION-VERDICT.md` |
| **Independent AI-vision re-transcription** | ⚠️ not viable | Vision can't read dense ~250-rune pages (mean alignment 0.145 = noise); template matcher 69.5% < 90% gate | `analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| **Image provenance** | ✅ verified authentic | 56/56 SHA1 match the archived onion7 dump; 400-DPI Artifex renders | `analysis/stego/provenance.json` |
| **Image steganography** (appended/EXIF/LSB/carve/color/OutGuess) | ❌ none | Built real OutGuess 0.4 from source (recovers known payloads) → LP2 pages carry no stego | `analysis/stego/STEGO-VERDICT.md` |

### E. The pp49–51 base-60 payload (the non-runic object)
Pages 49–51 aren't runic prose — they're a table of two-character tokens decoding to a
**2048-bit / 256-byte high-entropy binary payload**. Attacked in its own right:
| Attack | Verdict | Why | Where |
|---|---|---|---|
| Payload = a prime / clean RSA modulus | ❌ no | The big-endian integer is even | Campaign VII `analysis/pp49_51/` |
| Payload = polyalphabetic **key** over the runic pages | ❌ dead | 337,944 decryption configs, clean null | Campaign VII |
| Payload = plaintext text | ❌ no | 40% ASCII-printable, longest printable run 5 bytes | Campaign VII |
| Payload structural leads (4×64 = hash digests? relation to AN END 512-bit hash? XOR with P.S. digits?) | ❌ null | Worked, measured, reproducible — all honest nulls | Campaign IX `analysis/pp49_51/` |
| **Alt-base** readings (59/61/62/64) of the same glyph-digits used as key over the runes | ❌ null | All deep in noise (best −6.06 vs −5.2 threshold) | Campaign XI `analysis/CAMPAIGN-XI-FINDINGS.md` |
| Payload = **container/format** (PGP/gzip/zip/PNG/DER/base64…) | ❌ no | Magic-byte sniff fwd/rev/decpref clean (lone PGP flag = false positive); base64→noise | Campaign XII `analysis/campaign12/payload_forensics.py` |
| Payload = **32-byte-block hash** preimage (SHA-256/SHA3-256/blake2s) | ❌ null | 37-string Cicada dict × 3 algos × 16 blocks → 0 hits (IX did 64-byte only) | Campaign XII |
| Payload = short **repeating-key XOR** | ❌ dead | ks=12 Hamming "dip" falsified — columns at entropy ceiling, ~53% printable = random | Campaign XII |
| Payload = hidden **image / QR** | ❌ null | 2D bit-matrix autocorrelation ≈0.50 at every raster width; no periodic structure | Campaign XII |

### F. Attribution / external OSINT (where a key might physically exist)
| Attack | Verdict | Why | Where |
|---|---|---|---|
| 2017 "Beware false paths" PGP message = hidden key/pad/hash | ❌ no | `7A35090F`/`3301`/CRC are standard PGP mechanics, not cipher material | Campaign VI `analysis/osint/` |
| Any **publicly-published external key** ever existed | ❌ none found | AN END page / onion7 / international communities all dry; every solved page is self-contained | Campaigns V, VI |
| **Named author** attribution (cypherpunk lineage) | ❌ unproven | "Consistent-with, not evidence-of"; zero priority-of-knowledge leaks | Campaign VIII `analysis/attribution/` |
| **"AN END" deep-web page** (hash `36367763…c2a8b4`) recovery | ⚠️ cold | Never confirmed found; likely lost to Tor v2 deprecation (Oct 2021) | `analysis/DEEPWEB-HASH-OSINT.md` |
| **CT-log brute** for the AN END hash (was a documented long-shot) | ❌ non-viable | CT logs hold CA-issued cert domains, not page contents/v2 onions → no relevant candidates exist | Campaign XIII |
| "AN END hash = v2-onion payload" theory (monokro.me 2024) | ❌ debunked | Standard first-80-bit base32 = `gy3hoy5lon4dy6xs` ≠ theory's cherry-picked address | Campaign XIII |
| "AN END hash = ed25519/v3 onion" theory | ❌ debunked | Anachronistic — v3 onions didn't exist until 2017; AN END is 2014 | Campaign XIII |
| **Current solve state** (any page solved / key published since 2017?) | ✅ confirmed none | Independent 2022–26 sources: LP2 still unsolved, no key ever published, no authenticated 3301 activity since Apr-2017 PGP msg; Schoenberger 2023 self-claim fails the PGP gate | Campaign XIII |
| **External-artifact sweep** — pull the un-held onion images/HTML from community mirrors and re-extract | ⚠️ no new key | 2026-07-27 OSINT sweep. Downloaded the mirror set (iBotPeaches `/onions/`, archive.org per-onion, scream314, krisyotam) and re-ran extraction. **T1 onion3 5×5-rune JPG → known 2013 RSA message; T5 4gq25.jpg → known 2016 message** (both already-known payloads reproduced, not new). Broadened 60-key OutGuess sweep = null (default-key keystream artifact). **T2/T3 = unidentified high-entropy blobs, still open (low prior).** | `analysis/OSINT-SWEEP-2026-07-27.md`, `analysis/armada_osint/` |

---

## What each campaign added (index)

| # | Focus | One-line result | File |
|---|---|---|---|
| I–II | Rig + statistical baseline | IoC·N 1.000, doublet deficit found; rig validated on solved pages | `docs/FINDINGS.md`, `analysis/STATS.md` |
| Armada / 20-front | Exhaustive key/keystream assault (36+ agents) | 0 breaks; eliminated the memoryless-keystream family, differencing, page-keying, stego | `analysis/ARMADA-20-FINDINGS.md` |
| III | Transcription integrity + esoteric keys | All public transcriptions trace to one origin (rtkd/iddqd); esoterica keys null | `analysis/foundation/` |
| IV | Structure / mechanism | Doublet deficit = uniform soft no-repeat rule; **mechanistically rules out English running keys** | `analysis/structure/` |
| V | Final stones | Glyph classifier 99.2% → transcription verified; multiplicative gematria excluded; no public key | `analysis/stones/` |
| VI | OSINT key-artifact hunt | 2017 PGP carries no key; reopened pp49–51 as the one unexamined object | `analysis/osint/` |
| VII | pp49–51 payload characterized | 2048-bit high-entropy blob; not prime/RSA/key/text | `analysis/pp49_51/` |
| VIII | Attribution (cypherpunk) | No named author attributable on surviving evidence | `analysis/attribution/` |
| IX | pp49–51 structural leads | 4×64 / AN-END-hash / XOR leads all worked → null | `analysis/pp49_51/` |
| X | **Autokey excluded** | Simulated the community's leading hypothesis and disproved it (positive result) | `analysis/CAMPAIGN-X-FINDINGS.md` |
| XI | Mechanism quantified | No-repeat filter = **soft, ~83% suppression**; alt-base-as-key null | `analysis/CAMPAIGN-XI-FINDINGS.md` |
| XII | Burn-down | Payload: no format/32-byte-preimage/repeating-XOR/image; +15 verified thematic keytexts null (best −6.048) | `analysis/CAMPAIGN-XII-FINDINGS.md` |
| XIII | Armada | +82 never-tested keytexts across 10 lanes null (best −5.809); fresh OSINT confirms still-unsolved-2026, closes CT-log avenue, debunks 2 AN END onion theories; surfaces ~75-page transcription gap | `analysis/CAMPAIGN-XIII-FINDINGS.md` |
| XIV | Fable 5 red-team + probes | Fresh-eyes review caught 4 over-claims → all closed by measurement (corpus-wide periodicity P1–P2, combiner/homophonic P4); word boundaries English-like (P5); continuous stream in book order (P3); ~75-page "gap" = solved pages, no new unsolved material | `analysis/CAMPAIGN-XIV-FINDINGS.md` |
| XV | **Label-free transcription audit** | Clustered glyphs by shape with canon never shown; canon = the natural visual partition (ARI 0.75, homogeneity→0.98). First confirmation independent of the labels; only fragile locus = ᚩ/ᚪ/ᚫ (10.7%, crypto-inert) | `analysis/independent-read/` |
| XVI | Stylometry + attribution power | Cicada's connected prose = 359 words (floor ~500–1000/doc) → un-attributable; closed-set naming gate fails at 359w (62% impostor acceptance); live demo mis-names "Stallman" inside the noise band | `analysis/stylometry/` |
| XVII | **Red-team the assumption stack** | 8 fronts attacked, all sealed: page-56-hash-preimage-of-internal-object, interrupter-masked running key, plaintext-feedback autokey, crib-drag fixed-function autokey, serialization (reversed/boustrophedon), selection/acrostic, 1-bit channel, **Latin plaintext** (language-independent exclusions), **book cipher** (KJV/Mabinogion/Milton word-salad) | `analysis/CAMPAIGN-XVII-FINDINGS.md`, `analysis/red_team.py`, `analysis/latin/`, `analysis/bookcipher/` |
| OSINT-2026-07-27 | **External-artifact sweep** | Pulled the onion images/HTML we never held from community mirrors + re-extracted. No new break: T1 (onion3 5×5-rune) and T5 (4gq25) decode to already-known 2013/2016 messages; 60-key OutGuess sweep null; T2/T3 remain unidentified high-entropy blobs. Confirms the "provable hidden data" onion-image lead resolves to standard payloads. | `analysis/OSINT-SWEEP-2026-07-27.md` |
| XVIII | **Skip-tolerant re-decode (item 2c executed) + coverage armada** | Built + validated a key-skip decoder that tracks the desync the ~83% doublet filter induces (rigid misses the correct key at −7.24/8.5%, beam recovers it at −4.15/100%; FP ceiling −6.82; recall 7/8). Then re-ran **every alignment-sensitive family** under it: referenced texts (best −5.88), full 122-text corpus (best −5.808), armada18+19 literary sweeps (88 more texts, best −5.786/−5.754), **autokey under skip** (community's #1 hypothesis — 45 primers, best −6.627), ~620 Vigenère keywords (−6.021), extended numeric (−5.745), self-referential families (first-diff/integral/self-key/ct-feedback) — **all 0 hits**. Prior keytext nulls now **unconditional**; family-by-family accounting in `armada2/COVERAGE-MATRIX.md`. | `analysis/campaign18_skip/` |

---

## The 2026-08 pre-registered rounds (index)

Where the campaigns above ran an attack and reported the outcome, each round below had its
**hypothesis and pass/fail threshold written down before the run** — which is what let the
later rounds close whole families by mechanism instead of one candidate at a time. Full
detail: `../research/LEDGER.md`; kill reasons: `../research/DEAD_ENDS.md`.

| Round | Hypothesis | Result | Where |
|---|---|---|---|
| 1 | The doublet deficit is an artifact of the interrupters | **NEGATIVE** — intrinsic | `analysis/h1_interrupter_strip.py` |
| 2 | A period-locked fractionation signature exists in LP2 | **NEGATIVE** | `analysis/r2_fractionation_signature.py` |
| 3 | A differencing/DP decode can be anchored | **KILL at Gate #1** — un-anchorable; the ciphertext-only program is COMPLETE | `../research/LEDGER.md` |
| 4 | An external key/seed lead, or a verifiable author identity, exists | **NEGATIVE** — cold | `../research/LEDGER.md` |
| 5 | Residual doublets carry digraphic/autokey/interleave structure | **NEGATIVE** | `analysis/r5_doublet_anatomy.py` |
| 6 | Misfiled plaintext windows; transition-lattice/keel structure | **NEGATIVE** — the no-repeat rule is a *pure lag-1 identity*, no second-order structure | `analysis/r6_sieve_windows.py`, `r6_transition_structure.py` |
| 7 | Some untried already-public keytext is the key | **KILL, 0/15 unanimous** — ~~dead rigidly *and* skip-aware, independent of which text~~ → **dead by exhaustion over ~200 texts, verified robust to skip *and* rewrite** (Round 12 D1; the "independent of which text" mechanism argument is void — see §A note) | `../research/ROUND-7-GATE1-SYNTHESIS.md`, `analysis/round12/D1_redteam/RESULTS.md` |
| 8 | Five axes that were never ciphertext-only attacks (below) | **NEGATIVE ×5** | `../research/ROUND-8-RESULTS.md` |

**Round 8's five axes**, each previously uncovered by "ciphertext-only complete":

| Axis | Question it asked | Result |
|---|---|---|
| **SEED** | Is the pad a seeded PRNG? Structure was measured; entropy never was. | 10 generators validated against the real libraries × both directions × every unix-second seed 2011–2015 = **2.52×10⁹ decodes, 0 hits**, best −13.13 (= the null max); +15,408 lore/string/date seeds, 0 hits. `analysis/seed_sweep/` |
| **GEOMETRY** | The pages are 400-DPI renders of a *typeset* document — only FILE-level stego had been swept. | Glyph-shape substitution dead (median nearest-neighbour Hamming distance **0.0000**); micro-spacing 1.86σ unimodal; baseline jitter fails BIC. `analysis/geometry/` |
| **PAYLOAD** | "Flat IoC" is blind to a *compressed or binary* plaintext. | 166 representations scanned for magics/armor/inflate: nothing. Byte histogram exactly uniform (χ² 246.7 / 255 df). |
| **SKELETON** | Word length is a cleartext invariant no pad touches — a known text could be identified as the **plaintext**, no key needed. | FFT scan of every offset, 51 texts / 8.2M words: 20.0% vs a 19.8% shuffled control. Negative *for that corpus*; the tool extends. `analysis/skeleton/` |
| **POINTERS** | The 86 residual doublets as a book-cipher index. | Every reading inside the random null. |

**AN-END hunt closed (2026-08).** The lost deep-web page is **unreachable by construction**:
its address is gated behind solving OTP-class LP2 0–54 (the 2014 chain grammar is "each
onion's solved content yields the next address"), `gy3hoy2…onion` is a debunked
hallucination, no genuinely-retrievable in-scope Tor-v2 corpus exists, the held corpus hashes
null across representations (2,706 tests), and the 2026 community status is a sourced
negative. `analysis/anend_hunt/FINDINGS.md`.

---

## Still genuinely open (the honest frontier)

> **⚠️ Superseded 2026-08.** Both numbered items below were closed after this section was
> written — **#1 by Round 7** (keytexts dead by mechanism, not by exhaustion) and **#2 by the
> AN-END hunt** (unreachable by construction). They are kept here unedited because the
> reasoning that *narrowed* them is still the useful record. For what is actually open now,
> see `../PICKUP-HERE.md` § "What is actually still open" — all of it external and low-prior.

**Update (Campaign XVII — assumption-stack red-team):** the eight load-bearing
premises the whole effort rested on have now each been attacked directly and hold —
key, reading order, hidden subsequence/acrostic, 1-bit channel, transcription,
fixed-function autokey, **plaintext language** (Latin sealed; the load-bearing
exclusions are language-independent), and **book cipher** (pointer schemes into
Cicada's known books yield only word-salad). What survives is therefore only the
**unbounded** (multi-rune-history feedback; a book outside Cicada's known references)
or the **external** items below. ~~The internal attack surface is closed.~~

> **⚠️ Corrected 2026-08-17 (Round 12, front D3).** "The internal attack surface is closed" is
> the wrong word for the actual state. `analysis/round10/RECON-A/REGISTER.md` registers **30
> leads, of which 16 are still marked `never-run`** (A-03, A-04, A-06, B-04, B-05, C-02, D-01,
> E-01, E-02, F-01, G-01, G-02, H-01, H-03, I-01, I-03). The honest statement is: **the internal
> attack surface is heavily swept and every family we could concretely construct has been
> falsified — but it is not closed.** The highest-prior un-run internal items are **B-04/B-05**
> (cryptographic derived-key keystreams from a Cicada seed dictionary — the lane the OTP-class
> correction above turns on, in flight as Round 13), **A-03** (haplography count-audit of the 86
> doublet sites — the cheap falsifier of the whole engineered-filter edifice; ~20 confirmed
> merges would put autokey back on the table, in flight as Round 14), **D-01** (the
> generator-fingerprint suite Campaign IV skipped) and **F-01** (LP2-as-pad inversion against
> other Cicada objects). Since this line was written, Round 11 additionally closed the
> "unbounded" *feedback* class it names (N1, control-validated) and Round 12's C1 bounded and
> falsified k-history feedback for k=2..6 — so the unbounded half is now smaller, and the
> `never-run` half is what remains.

Only two productive things remain, and both are **external** — nothing in the
ciphertext can close them:

1. **An untried already-public keytext** Cicada expected solvers to *recognize*. A
   running-key search over a real text is **falsifiable** (the right text at the right
   alignment would decrypt to readable, high-scoring English), so this is the one
   productive avenue left. We tested the *named/referenced* texts, thematic esoterica
   (Campaign III), 15 verified thematic texts (Campaign XII), **82 more across 10
   lanes (Campaign XIII)**, and **88 more literary texts skip-aware (Campaign XVIII
   armada18/19)** — ~200 named texts eliminated total, all now re-tested (or newly
   tested) under the corrected skip-alignment model — but the space of conceivable
   primary sources is not exhausted. **This is why we can't say "100%,"**
   though the frontier is now much narrower. Trivially extendable: add a slug/ID to
   `analysis/campaign12/fetch_keytexts.py` and re-run `run_sweep.py`.
2. **The "AN END" deep-web page** — the only place a key might physically exist.
   Cold trail (Tor v2 dead). CT-log brute is now **ruled out as non-viable** (Campaign
   XIII); the only tractable-but-low-prior path left is a finite lookup of archived
   v2-onion corpora. **Partly executed (OSINT sweep 2026-07-27):** the archived onion
   image/HTML corpora (iBotPeaches/archive.org/scream314/krisyotam) were pulled and
   re-extracted — the AN END page itself is not among them, and the recovered onion
   images decode to already-known messages. What remains genuinely un-examined from that
   sweep is narrow and low-prior: two unidentified high-entropy blobs (`2.jpg`/`.htaccess`
   class → T2/T3), the per-onion HTTP/port anomalies, a full-corpus whitespace re-audit at
   scale, the unconfirmed 2012 "7 images" endpoint, and the missing 2013 Columbus GA
   Shamir-share onion. See `analysis/OSINT-SWEEP-2026-07-27.md`.
2b. ~~**Word-length skeleton match**~~ — **EXECUTED (Campaign XVIII), null on high-prior
   corpus.** An OTP hides symbol values but not word boundaries (transcription keeps `-`
   separators). Slid each page's rune-count-per-word sequence over 11 high-prior texts as
   **plaintext**, scored by the high-power statistic (longest consecutive exact-length run,
   chance ≈ 0.4^R) vs an 8-shuffle control. **Strong null:** every page's real longest run
   (7–10) is at or *below* the shuffled-control ceiling (8–12) — controls often beat the
   real sequence, i.e. zero signal. Cipher-model-independent, so this holds no matter the
   keystream. Extendable to the full 122-text corpus by widening the `REF` list in
   `analysis/campaign18_skip/word_skeleton.py`. Original proposal: `analysis/campaign14/
   REDTEAM-PROPOSALS.md`.
2c. ~~**Skip-tolerant / filter-aware re-decode (soundness patch)**~~ — **EXECUTED
   (Campaign XVIII).** Built and validated a key-skip encipher model + a skip-tolerant
   beam decoder that tracks the key/plaintext desync the ~83% doublet filter induces.
   Validation is decisive: a correct key with only 6 skips scores **−7.24 (noise)** under
   the rigid test every prior campaign used but **−4.15 / 100% recovery** under the beam;
   false-positive ceiling over 400 wrong (key,offset) trials is **−6.82** vs genuine
   English −4.3 (wide margin); planted-key pipeline recall **7/8** per page. Re-ran the
   **9 directly-referenced texts** through it across all 55 pages → **clean null** (best
   −5.88, median −6.21). Then the **full 122-text corpus** (0 hits, best −5.808) and the
   armada18/19 literary sweeps (88 additional texts, 0 hits) completed under the same
   corrected model. The keytext nulls are now **unconditional**, not conditional on rigid
   alignment. See `analysis/campaign18_skip/CAMPAIGN-XVIII-FINDINGS.md` and
   `analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md`.
3. ~~Transcription coverage gap~~ — **RESOLVED (Campaign XIV):** the community's ~75-page
   figure is 72 rune-pages including the **already-solved** intro/koan pages (elevated
   IoC, normal doublets). There is **no new *unsolved* material**; pages 0–55 are the
   complete unsolved corpus.

## Do NOT re-run (proven dead — reasons recorded above)
More keywords • more short/periodic keys • more number-theoretic or PRNG keystreams •
autokey/autoclave • differencing/integration • page-on-page keying • transposition-only •
fractionation • substitution/homophonic • image stego • AI-vision re-transcription •
treating pp49–51 as a runic key. All eliminated with the reason and a reproduce pointer.

**Added by Rounds 1–8 (2026-08):** **another keytext** (dead by exhaustion over ~200 texts,
verified robust to skip and rewrite — Round 7 + Round 12 D1) • **integer-seeded PRNG pads over
the swept generators** (2.52×10⁹ decodes, 0 hits — Round 8 SEED; **bounded — read the correction
below**) • **glyph-shape / micro-spacing / baseline stego** in the page renders (Round 8
GEOMETRY) • **compressed or binary plaintext** (Round 8 PAYLOAD) • **residual doublets as
book-cipher pointers** (Round 8 POINTERS) • **the interrupter-artifact explanation** of the
doublet deficit (Round 1) • **second-order structure in the no-repeat rule** — it is a pure
lag-1 identity (Round 6).

**Added by Rounds 9–12 (2026-08):** the **number/value channel** in every form Round 11 tested
(feedback autokey, prime-gap/index, number-theoretic structure, digit planes, totient ladder,
interrupter positions, separators — 7 lenses, all controls PASSED) • **k-history feedback
autokey, k=2..6** over 7 combiners, both signs, both orientations (Round 12 C1, 23,520 configs,
control PASSED) • **the author's own recoverable binary pads** under the skip-aware beam
(Round 12 A1 — except `DATA/560.13`, still unfetched) • **rigid-alignment re-runs of anything in
`campaign18_skip/armada2/COVERAGE-MATRIX.md`.**

> **⚠️ Corrected 2026-08-17 (Round 12, front D3; first flagged 2026-08-12 as RECON-B item B-21
> and never actioned until now).** The line above used to read a flat "**seeded-PRNG pads**
> (2.52×10⁹ decodes, 0 hits — Round 8 SEED)", i.e. the whole family closed. What Round 8
> actually covered, per its own census `analysis/round10/L5-seed32/CENSUS.md`, is **10
> generators over ~3% of each one's seed space** (2 of them fully at 32 bits; L5 later added 4
> validated generators — Perl/drand48, `lrand48`, Ruby MT, xorshift32 — and extended generator 0).
> The census names as **UNCOVERED and plausible**: PHP `mt_rand` (**the single highest-prior open
> generator** — PHP's MT deviates from reference MT19937 and is unreachable from generator 5),
> PHP `rand()` (partly covered), .NET `System.Random` (Knuth subtractive), **Blum–Blum–Shub as a
> real seed space** (ARMADA-20 tested 2,080 Cicada-constant configs, which is a keyword probe,
> not a sweep), **ISAAC**, **LFSR / Geffe / Gollmann** stream ciphers, KISS/MWC/WELL/lagged
> Fibonacci — plus seed spaces wider than 2³² (Java's full 48-bit `setSeed`, millisecond
> timestamps, `init_by_array` multi-word keys) and **keystream offset ≠ 0** (RECON-A/B-02), which
> multiplies *every* generator. So the honest wording is: **integer-seeded PRNG pads are excluded
> over the generators and seed ranges actually swept — a real but partial bound, not a closed
> family.** Two caveats keep it from being a live lead anyway: (a) PCG, xoroshiro and xorshift128+
> are **excluded by date** (published after LP2 was posted in Jan 2014), and (b) the *modal*
> behaviour for anyone building "a one-time pad" — `/dev/urandom`, a hardware RNG, random.org,
> dice — leaves **no seed at all** and no sweep can ever reach it. The census's own arithmetic:
> finishing the last 8 generators at full 32 bits multiplies total coverage by ~1.3×; adding PHP
> `mt_rand` multiplies it by ~1.1× and closes the highest-prior named gap. Note this is a
> *different lane* from the **cryptographic** keystreams (SHA/HMAC-DRBG/AES-CTR/RC4 from a seed
> **dictionary**) — those are RECON-A **B-04/B-05**, never-run, and the census marks them "out of
> scope for a seed sweep, by construction."

---

_Sibling docs: `SOLVERS-DOSSIER.md` (community writeup) · `docs/FINDINGS-FOR-SOLVERS.md`
(short form) · `analysis/OPEN-AVENUES.md` (ranked avenues) · `../PICKUP-HERE.md`
(resume point). This ledger supersedes their scattered "ruled-out" tables as the
single complete index._

## Welsh-original Mabinogion / Taliesin (novel_cipher lane, 2026-07-28) — NULL
The anagram convention fingerprints a Welsh-myth author; the Mabinogion had only ever
been tested as ENGLISH (Guest translation). Tested the MIDDLE-WELSH ORIGINAL as keytext.
- **Source:** archive.org `pedeirkeincymabi00will_djvu.txt` (Ifor Williams, Middle Welsh,
  769KB) + maryjones.us Llyfr Taliesin Welsh. Normalized 2 ways (Welsh W→U vowel, and
  W-kept), digraphs DD/LL/FF/RH/CH/PH/NG mapped into the 29-rune Futhorc transliteration.
  ~411K letters each. Installed at `data/keys/welsh/`.
- **Additive skip-aware running key** (validated beam gate PASS; both signs, both atbash,
  all offsets, skip-tolerant): every unsolved page 0–54 best score −5.99…−6.44, **0 hits**
  above conf −5.5. In the null regime (null-max −6.82, English −4.3, thresh −5.2).
  Confirms the additive/OTP exclusion is language-independent (as predicted).
- **Book cipher** (runes as pointers into the Welsh text — the form NOT excluded by the
  additive proof): 4 pointer schemes (per-rune word-advance, cumulative-sum word pointer,
  cumulative-sum letter pointer, first-letter-stream pointer) × idx/prime rune values ×
  both texts × all 57 pages = 912 decodes. Best overall **−6.623**, median −7.57 (noise
  floor). **0 readable English.** Reproduce: `/tmp/bookcipher.py` (self-contained).
- **Verdict:** Welsh-original hypothesis CLOSED in both additive and book-cipher forms.

## Themed-word key × no-repeat (doublet-suppressing) combiner (recon LP1-H, 2026-07-28) — NULL
LP1 recon showed every *word*-keyed solved page uses an LP-thematic word from its OWN
plaintext, spelled in Gematria-Primus runes with C→F. Hypothesis: LP2 uses the same themed
word but through a NON-ADDITIVE combiner forbidden from emitting a rune equal to the previous
ciphertext rune (a 29→28 no-repeat reduction that would itself PRODUCE the ~0.66% doublet
deficit) — dodging both the additive exclusion AND the doublet exclusion. Prior ledger entry
(crypto_rigor probe C) only measured IoC of a *keyless* rank-in-allowed(28) transform; never
swept a periodic themed key with English scoring → genuinely un-run.
- **Validation gate PASS:** combiner recovers its own planted key 100% (vs 16.5% wrong-key),
  emits 0 ciphertext doublets, recovers planted English to −4.750 vs −7.355 wrong-key; scorer
  orders known solves (p03 DIVINITY −4.10, p14 CIRCUMFERENCE −4.08, noise −8.86).
- **LP2 sweep NULL:** 58 themed keys (C→F + plain) × both signs × no-repeat over all 13
  scorable unsolved pages. Best on any ≥100-rune page **−6.88** (noise band; baseline −4.0,
  thresh −5.2, floor −7.49). Lone nominal −5.272 was a 9-rune fragment (length artifact).
- **Intrinsic nail:** the combiner is lossy (~4.4% ≈ 1/28 of English positions un-encipherable)
  → inconsistent with the author's clean, fully-recoverable solved ciphers.
- **Verdict:** CLOSED. Repro: `analysis/recon/lp1h_norepeat/lp1h_norepeat.py`.

## pp49-51 table as per-section INDEX + red-join continuity (recon LP2-H1/H2, 2026-07-28) — NULL
H1: the base-60 256-token table (canon_256) read as a per-section index/offset keyed to the
14 red-section-head pages [0,3,6,7,8,15,23,27,33,37,39,40,53,54], with the base-60 margin art
(pp34-39) as the "read in base-60" instruction. Ledger had tested the table as
key/number/text/format/preimage/XOR/image but NEVER as a section index; red heads never used
as a segmentation map (only as null cipher-selection). An index needs no keystream reset, so
NOT refuted by the cross-page continuity finding.
- **Validation gate PASS:** page map (57 seg, 12,956 unsolved runes, 594 lines), 256-token
  table, red-head list, and scorer all reproduce.
- **H1 NULL:** T1 index-concentration on red boundaries p=0.60/0.72/0.08/0.05 (sub-0.1 = tiny
  Poisson noise, fail Bonferroni). 11 decode models (per-section shift / table-key / repeating
  key / prime-offset selector / 3 gather-into-self book variants, both signs) best **−7.200**
  (~2.0 below thresh). T2 fails geometrically (base-60 first digit 0-4 can't index 13-14
  sections); T3 no pp34-39 count matches any table dimension.
- **H2 NULL:** adjacent-equal rate at 13 red joins = 0.0 vs 41 non-red = 0.0 (perm p=1.0); 3×3
  window red 0.0256 vs non-red 0.0325 — red LOWER (opposite of a reset). All-joins test was not
  diluting a sparse signal; no red-boundary reset exists.
- **Verdict:** both CLOSED. Repro: `analysis/recon/lp2h_index/h1_index.py`, `h2_redjoins.py`.

## Non-cipher framings of LP2 (rotating-loop iter 2, naive-outsider, 2026-07-29) — NULL
The whole ledger above assumes LP2 is a SUBSTITUTION cipher of an English message. Iteration 2
challenged that premise itself with three orthogonal non-cipher lenses. All NULL; artifacts in
`analysis/recon/i2_image/`, `i2_signal/`, `i2_message/`.
- **LP2-as-image (raw stream plotted, not decrypted):** every rendering (index/prime/parity/isF/
  delta at widths 29/41/79/82/113/158 + line-length shape) is pure salt-and-pepper noise. Row/col
  structure z-scores all NEGATIVE (−1.67…−0.67 = LESS structure than random shuffles), 1D
  autocorrelation zero peaks |r|>0.05 over lags 1-299, marginal chi2=26.4 (uniform). No glyph, QR
  finder pattern, or symmetry. **CLOSED.**
- **LP2-as-signal / DSP:** spectral-entropy ratio 0.9535 ≈ random control 0.9520 (whiter than real
  plaintext PARABLE 0.9005 = white noise over 29 symbols). Top peak p=0.971 (shuffles beat it 97%),
  period-29 (natural Vigenère carrier) power=1.05 = noise. No carrier/periodicity a generator would
  leave. **CLOSED.**
- **LP2 message-vs-filler UNDECIDABLE:** LP2 sits INSIDE both the English-plaintext-under-true-pad
  band AND the uniform-filler-under-pad band on all 10 statistics; the two bands OVERLAP on every
  statistic post-filter. No residual a true pad would lack (off-diagonal bigram chi2 z~0.8, no
  positional regularity surviving multiple-comparison correction). **The existence of a plaintext
  is undecidable from the ciphertext — a message is an ASSUMPTION, not a finding.**
- **Ledger correction:** prior "the only path is external: the key" phrasing silently presupposes a
  plaintext exists. Accurate statement: even the existence of plaintext is undecidable from these runes.

## Schoenberger founder-claim (attribution, iter 2, 2026-07-29) — NULL (self-asserted, unsigned)
Verified against PRIMARY court docs: consolidation order Dec 4 2025 (Hon. Redford, Court of Claims;
cases 25-000045-MM + 25-000186-MZ; plaintiff "Cicada 3301 Metaverse LLC," a Utah LLC). Order text has
ZERO occurrences of 7a35/090f/PGP/runic/Liber Primus (the author/creator/2012 hits are from an
attached unrelated Westlaw prison-grievance reprint). The Mar-2023 "Founder's Statement" CAREFULLY
does not claim authorship of the 2012 runic puzzles and never mentions 7A35090F. Nothing ties him to
the key or pre-2014 authorship. Consistent with post-2014 brand "gamejacking." Original-creator
verdict intact.

## Author-empathy: intended-path + doublet-intent discriminator (iter 3, 2026-07-29)
Stopped interrogating the runes (message-existence undecidable) and reconstructed the author's design.
- **Doublet author-intent discriminator (NEW FINDING):** solved-page PRE-encryption PLAINTEXT doublet
  rate = 3.52% (35/995 runes) = natural English rate (~3.45%); the author's own plaintext FREELY
  repeats glyphs (LL, EE, SS...). Unsolved 0-55 = 0.675% (88/13041) = ~5x suppression. Since neither
  the plaintext NOR any solved ciphertext (2.4-3.6%) suppresses doublets, the no-repeat property is a
  GENERATOR/HARDENING SIGNATURE present ONLY in the unsolved output — NOT a runic-typographic
  convention. Rules out the innocent "scribes avoid repeats" explanation; leans weak-moderate toward
  pad/deliberate-anti-statistics-hardening. Load-bearing measurement = the 995-rune LP1 plaintext.
- **Retrieval-chain reconstruction:** Cicada's authored grammar = each solved artifact's plaintext
  hands the seeker the ADDRESS of the next (2012 image->phone->book->image; 2014 onion1->RSA->
  onion2..onion7; onion7 = the 58-image index that DELIVERED pages 0-57 as a finished corpus). Thus
  pages 0-54 were the terminal DELIVERABLE of onion7 with NO accompanying key; nothing solved gates
  the START of 0-54 (LP2-STRUCTURE BRIDGE 1/3: AN END + PARABLE are book-terminal, own keystreams).
  AN END's plaintext ("WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO 36367763...c2a8b4 / IT
  IS THE DUTY OF EUERY PILGRIM TO SEEK OUT THIS PAGE") is the ONE outward pointer, but it is
  DOWNSTREAM of 0-54 = reward/continuation, NOT the key TO 0-54. PARABLE/KOANs point INWARD (self).
- **Conclusion:** by the author's own grammar the 0-54 pad was NEVER planted in a retrievable prior
  artifact -> consistent with an OTP whose pad was scheduled for a FUTURE chain step Cicada never
  released (silent since April 2017). Decisive gate: whole-file SHA-512 of every held open blob
  (T2.bin, 2.jpg, T3==folly==wisdom 3368B) vs the AN-END target = clean NULL -> the page must be
  RECOVERED as an archived object, not computed. Pivots the frontier to a pure archival problem.

## HISTORIAN/ARCHIVIST: Tor-v2 crawl-corpora sweep for AN-END page (iter 4, 2026-07-29) — NULL (sourced)
New primary-source class checked = archival crawl corpora (distinct from the 4 community mirrors + iBotPeaches GitHub).
- **Internet Archive `.onion` items**: IA hosts items for 5 of 8 Cicada onions (auqgnxjtvdbll3pv, cu343l33nqaekrnw,
  fv7lyucmeozzd5j4, avowyfgl5lkzfj3n, ky2khlqdf7qdznac). Verified they are 2020 COMMUNITY RE-UPLOADS, not new
  captures: IA avowy `3301` blob un-hexed == repo `rsahex_avowy_3301.bin` byte-identical; IA onion7 `index.html`
  (title "133", div "331") lists only 0-57.jpg with NO next-page pointer. SHA-512 of IA index.html and of the
  256B RSA blob (raw + hex forms) vs AN-END target 36367763...c2a8b4 = all NULL.
- **onion.link/onion.city IA WARC collection** (real 2014-15 Tor2web crawls): only 4 items total, ZERO Cicada
  onions. Not a comprehensive v2 crawl; AN-END page could not survive there. Exhausted.
- **gwern Darknet Market Archives 2013-2015**: scoped to 89 markets + 37 forums ONLY (non-market Cicada page
  out of scope by construction). Excluded.
- **Public preimage status**: web sweep through 2025 confirms NO published discovery of a page hashing to the
  target. Two recent solver artifacts are unverified/irrelevant: Zenodo 18199474 ("Bruno Becker", unsigned,
  fails the 7A35090F gate) and Tumbleson Part-4 (Dec 2024, "progress slowed massively, no clear path" — no
  archival recovery). AN-END page remains UNRECOVERED; archival frontier for these corpus classes = closed.

## Historian/archivist: AN-END page recovery + era endpoints (iter 4, 2026-07-29) — NULL
Frontier is now purely archival (0-54 pad never planted internally). Chased primary sources.
- **Tor-v2 crawl corpora:** AN-END page (SHA-512 36367763...c2a8b4) NOT in any archival corpus.
  Internet Archive holds .onion items for 5/8 Cicada onions but they are 2020 COMMUNITY RE-UPLOADS
  proven byte-identical to held content (IA avowy '3301' un-hexed == repo rsahex_avowy_3301.bin;
  IA onion7 index lists only 0-57.jpg, no pointer); SHA-512 of both vs target = null. onion.link
  WARC has 0 Cicada; gwern DNM archive out of scope. **AN-END likely LOST to Oct-2021 Tor-v2
  deprecation, never mirrored.** Only residual untried class = Tor2web-proxy (onion.to/tor2web.org)
  Wayback CDX captures — longshot (address unknown).
- **Onion7 continuation pointer:** NULL — onion7 (ky2khlqdf7qdznac, the LP2 deliverer) terminates
  CLEANLY, byte-structurally identical across 2 independent captures (iBotPeaches + IA-2020):
  <title>133</title>, <div id="331">, exactly 58 images 0-57.jpg, ZERO comments/address/hash/email/
  PGP/form. Contrasts with onions 2/3/4 (each embed <!--761/1033/3301--> + 256B RSA hex) and onion6
  (PGP gate + /cgi-bin/squares form). onion7 is a pure terminal book-delivery index; chain ends here
  by design. Confirms the ONE outward pointer is AN-END's hash, absent from onion7 HTML.
- **2013 Columbus-GA Shamir 7th share DEBUNKED as key source:** threshold is 5-of-10; we already hold
  6 valid 22-byte shares → the degree-4 polynomial is over-determined, secret already known, the
  missing 7th share is deterministically REDUNDANT (just re-encodes the known Questions onion), zero
  independent information. 2012 terminus went private per-solver (individual RSA modulus) past the
  email gate; no public "7 final images" terminal page exists in primary sources.
- **AN-END hash->address derivation:** author left it UNSPECIFIED. Exact text = "WITHIN THE DEEP WEB
  THERE EXISTS A PAGE THAT HASHES TO [512-bit digest] IT IS THE DUTY OF EUERY PILGRIM TO SEEK OUT
  THIS PAGE" — a PREIMAGE/content-address instruction (find the page whose SHA-512 = x), NOT a
  derivation. No base-encoding/char-count rule anywhere in authentic Cicada text. gy3hoy5...base32 =
  debunked modern fabrication (already ledger:119 / CAMPAIGN-XIII).

## Data-provenance red-team (iter 5, 2026-07-29) — DATA CLEAN, one SCOPE gap reopened
Attacked the DATA behind every null (is the ciphertext/hash/corpus faithful to primary source?).
- **AN-END digest = clean bill-of-health:** the 128-hex `36367763...c2a8b4` is nibble-identical
  across 5+ independent witnesses (primary image 56.jpg, solved_plaintext.txt, scream314,
  tweqx/3301-hash-alarm, Boxentriq); 0 divergent nibbles. Verified it is printed LITERAL Latin hex
  on the page (never a cipher output) → all 1572+ preimage nulls ran against the CORRECT target.
- **Runic ciphertext 0-54 = clean:** 4-witness char-level diff (krisyotam vs remlong vs scream314 vs
  relikd). All 13 rune substitutions + 8 length mismatches trace to the REMLONG witness's errors, NONE
  to ours; the lone 2-2 tiebreak (p24 idx172 aesc-vs-ac) decided FOR krisyotam by direct relikd
  p24.jpg read. Correction to a prior note: os/ac/aesc (7/97/101) are NOT equal-value so a swap WOULD
  matter — but no such swap is in our text.
- **Solved corpus = provenance-tagged:** the 2013 hash blocks + 2014 magic-square posts are
  PGP-SIGNED under key 0x181F01E57A35090F (self-authenticating, not solver output); LP1/AN-END/PARABLE
  English is community-deciphered but the AN-END hash appears as literal transcribed hex. Retrieval-
  chain grammar traces to held primary captures, not wiki narrative.
- **REOPENED (scope-of-null, not data):** the AN-END hash ALGORITHM is UNSOURCED. The page says only
  "HASHES TO x"; primary source (Uncovering-Cicada PAGE_56) states verbatim "algorithm not known,
  candidates SHA-512 / BLAKE-512 / BLAKE2b." The preimage battery covered SHA-2/SHA-3/BLAKE2/original-
  BLAKE but NEVER **Skein-512-512** (itself a SHA-3 finalist), **Whirlpool**, or **Streebog-512**
  (GOST R 34.11-2012). The blake_closure "last untested hash family / COMPLETE" verdict is therefore
  unsound for the wider 512-bit space. FIX = run the whole-file preimage gate under those 3 digests
  (KAT-validated) vs every held blob + candidate object; a hit means the AN-END page is a HELD object
  and the archival-loss verdict collapses. Scheduled into loop iter 6 as the mechanical prerequisite.

## Lateral-field transplant (iter 6, 2026-07-29) — hash gap CLOSED; 3 fields harden OTP
Imported unrelated-field methods (fields the cipher lanes never used) to pages 0-54.
- **Reopened preimage gate CLOSED:** Skein-512-512 + Whirlpool + Streebog-512, each KAT-validated
  (Whirlpool 5/5 ISO 10118-3, Skein 2/2 v1.3, Streebog RFC6986), whole-file over every held blob +
  internal candidate set, 2658 byte/digest-orientation combos = CLEAN NULL. The AN-END target
  36367763...c2a8b4 is now unsourced to any held object across SHA-2/SHA-3/BLAKE/BLAKE2/shake +
  Skein/Whirlpool/Streebog. The iter-5 scope gap is closed; archival-loss verdict hardened.
- **MDL / compression-distance (info-theory) NULL:** 0-54 packs to 7868B = Shannon floor 7867.5B
  (exactly incompressible) → NOT an algorithmically-generated pad (hash-chain/PRNG would compress).
  The lone order-1 entropy dip (z=-14.6) decomposes to ONE cause: doubled-rune suppression ratio
  0.19, which MATCHES known-plaintext PARABLE (0.147) and NOT a pad (~1.0) → an English-phonotactic
  fingerprint, independent re-confirmation that English plaintext exists under 0-54.
- **Bioinformatics approximate-repeat finder (BLAST seed-and-extend, k<=3 mismatch, g<=2 indel)
  NULL:** one 6-mer repeat, zero at w>=7, longest gapped approx repeat only 7 runes — at/below the
  random 29-ary floor (sensitivity validated on a planted length-14 repeat). FALSIFIES the
  filter-induced gapped-keystream-desync hypothesis (campaign-14 flagged blind spot).
- **Word-length typology — FALSE POSITIVE, retracted:** an agent claimed an English clause-position
  length signature (z=-8); the critic reproduced z=-7.94 but disqualified it: the effect is driven by
  the '/' LINE-WRAP separator (edge-int -0.748) not the grammatical '.' clause boundary (-0.234), and
  its SIGN is OPPOSITE to English (English clause-last words LONG +0.476; cipher clause-last SHORT
  3.58). It is line-typography, NOT recoverable plaintext. Does NOT reopen message-existence; do not
  build crib-dragging on it.
- **Surviving positive:** anti-doubling fingerprint (English present, but it constrains the PAD, not
  the message). Feeds iter-7's plaintext-blind pad-restoration oracle.
- **iter-7 pad-restoration oracle (game-theorist) — NULL, and it CORRECTS the anti-doubling claim
  above.** Built a plaintext-BLIND oracle (doubling ratio D + PARABLE-learned bigram plausibility P)
  and VALIDATED it: on synthetic English-in-runes enciphered with the KNOWN AN-END phi(prime)
  generator, subtracting the correct keystream recovers English on both metrics (D=0.699==English,
  P=0.398) while every wrong/random keystream fails the P channel (~0.09 floor) — the oracle
  discriminates a correct pad from a wrong one with no language model. SWEEP of the demonstrated
  generator family {prime(n), totient(n), phi(prime)=AN-END re-seeded, Fibonacci, golden} × add/sub/
  Beaufort × strides{1,2,3} × offsets{0..39} = 1800 configs subtracted from real 0-54: **ZERO
  residuals land in the English band**; every generator RAISES D from 0.19 toward the random-control
  band (0.83–1.25), i.e. injects doublets rather than restoring English. CORRECTION: the prior
  "PARABLE English doubling = 0.147 ≈ 0-54's 0.19 → English survives" is small-sample noise (PARABLE
  is 95 runes / 1 doublet → D=0.309; a large-N quadgram English-in-runes reference has D=0.699). The
  0-54 baseline D=0.19 is BELOW the English band and its bigram plausibility P=0.095 sits at the
  RANDOM floor — the low doubling is doublet-SUPPRESSION intrinsic to the cipher mechanism (matches
  Campaign IV's diagonal doublet deficit), NOT surviving English phonotactics. The
  self-contained-deterministic-generator restoration hypothesis is FALSIFIED for the demonstrated
  family. See `analysis/recon/i7_oracle/` (sweep.py, RESULTS.txt).

## Game-theorist: plaintext-blind pad-restoration oracle (iter 7, 2026-07-29) — NULL + a CORRECTION
Hypothesis (from Cicada's recruiter payoff structure): 0-54's pad is a self-contained DETERMINISTIC
generator seeded by a taught constant (not a true OTP). Tested with a plaintext-BLIND oracle: subtract
candidate keystream, measure residual doubling-ratio D + rune-bigram-plausibility P (no language model).
- **Oracle VALIDATED:** on synthetic English-in-runes enciphered with the known AN-END phi(prime)
  generator, subtracting the CORRECT keystream recovered English on the P channel (P=0.398) while every
  wrong/random keystream collapsed to the P~0.08-0.10 floor. D alone is insufficient (prime(n)
  coincidentally hits D=0.699); P carries the decision. Model-free discrimination confirmed.
- **Sweep NULL:** 0 of 1800 continuous configs + 0 of 16 per-segment-reset cells (reset at %/./ '/')
  land a residual in the English band. Every deterministic generator {prime, totient, phi(prime),
  Fibonacci, golden} x {add,sub,Beaufort} x strides x offsets pushes D the WRONG way — UP from raw 0.19
  toward the random band (0.83-1.25), INJECTING doublets rather than restoring English. The
  constant-derived-generator hypothesis is FALSIFIED for the sanctified/demonstrated family.
- **CORRECTION to iter-6:** the "anti-doubling = English phonotactics survive" positive is FALSIFIED.
  PARABLE's 0.147 was 95-rune sample noise; large-N English-in-runes has D~0.699 (English DOUBLES).
  0-54's D=0.19 is BELOW the English band and its bigram-plausibility P=0.095 is at the RANDOM floor.
  So the low doubling is intrinsic cipher doublet-SUPPRESSION (Campaign IV diagonal deficit ~0.66% vs
  3.45%), NOT surviving English. Message-existence is back to UNDECIDABLE (iter-2 stands).
- **Surviving structural handle:** the correct model must REPRODUCE the 0.66%-vs-3.45% doublet deficit
  as an OUTPUT statistic while yielding bigram-plausible plaintext — a no-repeat/doublet-avoiding output
  constraint over the (sealed) additive core. Constant audit: only prime-stream + (prime-1)-stream are
  ever the actual deterministic pad on solved pages; no solved key is external. (Repro analysis/recon/
  i7_oracle/, i7_oracle_reset/, i7_constants/.)

## iter-8 — DEVIL'S-ADVOCATE (premise b): glyph->index MAPPING / alphabet-ordering attack
- **Premise attacked:** "the 29-symbol glyph->index mapping (alphabet order) is right." If the raw
  0-54 glyphs were plaintext under a WRONG symbol->index labeling (a monoalphabetic relabeling of GP),
  NO decryption would be needed — only re-ordering the alphabet. Monoalphabetic substitution preserves
  bigram structure, so SOME permutation of the 29 symbols would lift an English-bigram score off the
  floor. Reused the i7-scale plaintext-blind bigram instrument (P) + added log-bigram fitness (F).
- **Method:** remap raw 0-54 under 6 principled orderings (standard GP / futhorc canonical / prime-value
  / reverse / atbash / frequency-matched-to-English), plus a FULL 40-restart monoalphabetic hill-climb
  over all 29! orderings (the textbook solver that WOULD recover English-under-a-permutation if it
  existed). Controls: 500 random permutations (null band) + hill-climb run on pure random noise.
- **Result NULL / mapping is FINE.** Instrument anchors (tight top-60 LEGAL, i7 scale): English-in-GP
  P=0.465; raw-0-54 (identity) P=0.074; random P=0.072 — the raw stream sits ON the random floor,
  the full English band away. None of the 6 named orderings moves it (all ~0.47 on the loose LEGAL,
  all at floor on the tight one; freq-match's 100th-pctl is a 0.488-vs-0.482 non-signal). The
  exhaustive hill-climb reached only F=-6.026 vs the English target F=-2.938 — and the DECISIVE control:
  climbing on pure random noise reached F=-6.017, i.e. the raw-stream climb gain is 100% overfitting,
  identical to noise. Best remapped output is gibberish ("THAEEOBDGNATHWEOHRCTD...").
- **Conclusion:** the alphabet ORDERING is not the lock. A wrong monoalphabetic label would have been
  trivially recovered by the bigram climb; it wasn't. The stream is bigram-flat like a properly
  ENCIPHERED text, consistent with the sealed additive-core frontier — substance is hidden by
  encryption, not by a mislabeled alphabet. Premise (b) alphabet-order variant FALSIFIED.
  (Repro analysis/recon/i8_mapping/i8_mapping.py, i8_results.json.)

## Devil's-advocate believer: 4 artifact premises audited (iter 8, 2026-07-29) — ALL CLEAN
Assumed LP2 IS solvable; attacked the never-audited ARTIFACT premises (not sealed cipher lanes).
- **Alphabet-ORDER / glyph-mapping sweep (premise b) NULL:** no 29-symbol reordering lifts raw-0-54
  bigram-plausibility off the floor (identity P=0.074, random P=0.072, English-in-GP P=0.465). The
  monoalphabetic hill-climb — which WOULD recover English under any wrong ordering — reached F=-6.026,
  IDENTICAL to climbing pure random noise (F=-6.017) → 100% overfit. Stream is bigram-flat like
  properly enciphered text; substance hidden by encryption, not a mislabeled alphabet.
- **Transcription common-origin re-derivation (premise a) CLEAN:** krisyotam and relikd are
  CHARACTER-FOR-CHARACTER IDENTICAL over the full 12,956-rune overlap (first divergence: None); kris's
  180-rune surplus = the unsolved tail relikd truncates; the 40-55 count divergence is page-boundary
  bookkeeping that cancels in the concatenated stream. GP table matches canonical futhorc on all 29
  entries; the mapping is FALSIFIABLY correct (unique labeling under which BOTH solved pages read
  English — every confusable swap corrupts PARABLE; the 7 rare runes PARABLE lacks are anchored by
  AN-END). 29/29 glyph labels plaintext-verified.
- **Image stego + external-solve (premise d) NULL:** DCT-LSB shows natural coefficient-parity bias on
  every LP2 page (not flattened; working OutGuess positive control detected at chi2=47940); PNG-LSB 0
  anomalous planes across 461 PNGs×8×3; trailer scan 0 bytes after EOI on all 56 pages. No external
  solve survives the 3301-PGP gate (one editable-Fandom Solana-token self-claim fails it like Schoenberger).
- **VERDICT: closed-frontier verdict MAXIMALLY HARDENED.** Residual unrun levers (all low-prior):
  (b') 29-rune INVENTORY cardinality (a glyph that's really two, or two that are one variant — NOT
  detectable by the alphabet-ORDER attack, and the exact fingerprint that would create the doublet
  deficit); pixel-level OCR re-derivation from the 57 relikd JPGs (catches a common-origin READING
  error both Unicode witnesses share); the doublet deficit used as a FORWARD distributional constraint.

## Contrarian restart: 29-rune inventory + doublet-deficit forward-constraint (iter 9, 2026-07-29)
Tested whether the doublet deficit is a rune-inventory MISCOUNT (two glyphs = one symbol → doublets
miscounted). REFUTED three independent ways + produced two positive results.
- **Inventory cardinality = 29 CORRECT (premise b' eliminated):** every confusable-pair MERGE lands in
  the random-merge control band (0.85-0.98% doublet, P at floor); closes only ~10% of the 0.66→3.45 gap
  (pure 29→28 arithmetic). Cross-adjacency ratios at chance for all 7 confusable pairs (a real scribal
  variant would spike ONE pair >>1). The deficit is UNIFORM across all 29 runes (per-glyph error would
  suppress ONE, leaving 28 at ~1.0x). No off-diagonal pair absorbs hidden doublets. OCR self-control
  passed; p0 line-diff = ZERO disagreements; runes are a consistent digital font (no scribal variation).
- **AUTOKEY POSITIVELY REFUTED (upgrade from conditional null):** profiling by difference d=(b-a) mod 29,
  only d=0 is an outlier (0.180x, z=-17.25 vs shuffle); the 28 nonzero diagonals are FLAT (cv=0.061,
  chi 35.4<40). Under ciphertext-autokey each diagonal would equal a distinct plaintext-rune frequency
  (lumpy, cv~1.0). The flatness POSITIVELY excludes autokey — stronger than prior "matches rate, fails
  to decrypt."
- **CONSTRUCTION CLASS PINNED:** forward simulation — only a SOFT ANTI-REPEAT REWRITE (p_keep~0.18) over
  a MEMORYLESS base reproduces the observed 0.622% (memoryless OTP 3.43%, autokey 3.37%, first-diff
  3.52%, hard anti-repeat 0.00%). Residual 60 survivors uniform over value + positionally flat.
  Repro: analysis/recon/i9_inventory/, i9_deficit/, i9_ocr/.
- **CRITIC VERDICT: internal solve frontier EXHAUSTED — diminishing-returns hardening, not solve paths.**
  ⚠️ **Superseded 2026-08-19 — this was false when written.** RECON-A item **B-04** (the derived-key
  dictionary) was an *internal, ciphertext-only* lane marked `never-run`, and 16 further RECON-A items
  were `never-run` at the same date. See the correction block at the end of this section.
  Loop pivots to goal 2 (creator attribution); the soft-anti-repeat-over-memoryless construction is now
  a candidate TECHNIQUE fingerprint for attribution.

## Final pass: T2/T3 blobs, Smirnov-rewrite, key-location (iter 11, 2026-07-29) — ALL NULL
Last substantive pass before wind-down. Nothing survived.
- **T2/T3 opaque blobs — no author-side crypto artifact:** both statistically uniform-random
  (T2 entropy 7.978 chi2 226; T3 7.938 chi2 278; T3==folly==wisdom md5 0c7d18e8). NO OpenPGP (T2 byte0
  0x40 bit7-clear = not a packet header; T3 byte0 0xbf = invalid packet chain), NO RSA modulus / DER /
  ASCII-armor, NOT compressed/base-N/container. OTP-fit fails (7524B/3368B = 59.4%/26.6% of 12670 runes,
  mod-29 chi2 41.8/24.5 n.s.). T2 = OutGuess wrong-seed keystream artifact. The last physical hiding
  place for an author identity artifact is EMPTY.
- **Smirnov-rewrite decode RETIRED:** gate-validated (un-bump restored a synthetic Smirnov-rewritten
  sample P 0.202->1.000; wrong ordering 0.106), real sweep clean null — best of 116 orderings P=0.107 ==
  random-Smirnov control MAX (mean 0.098/p95 0.103). Un-bumping the real ciphertext pushes doubling D
  0.19->~1.05 (destroys structure into randomness). The 'deterministic Smirnov rewrite over a linear
  ordering' sub-hypothesis is dead; anti-repeat = SOFT REJECTION-SAMPLING over an EXTERNAL pad.
- **Key-location = UNPUBLISHED-BY-DESIGN:** author-intent enumeration — the pad's most-consistent home is
  private delivery to vetted 2014 winners (privacy-ideological collective, OTP chosen so brute force is
  pointless), NOT a public page. Pages 0-54 were onion7's terminal deliverable with no key; thematic
  pointers (mayfly/ephemeral=OTP, koan 'seek within'=gated-not-published) confirm. LP2 is
  unsolvable-BY-DESIGN, not unsolved-by-effort.
- **LOOP TERMINUS:** both frontiers exhausted; further rotation re-derives these conclusions. Wind down
  to synthesis (see FINAL-SYNTHESIS.md).

> ### ⚠️ SUPERSEDED 2026-08-19 — this whole iter-11 block reads more finally than the evidence allows
>
> Three statements above were written on **2026-07-29** and are now known to be wrong or overstated.
> They are kept because the reasoning that produced them is still worth reading, but **do not treat
> them as instructions**:
>
> | line | said | actually |
> |---|---|---|
> | *"internal solve frontier EXHAUSTED"* | no internal lane remained | **False.** RECON-A item **B-04** (the derived-key dictionary) was an *internal, ciphertext-only* lane, was marked `never-run`, and was not run until Round 13 — three weeks after this line was written. 16 further RECON-A items were `never-run` at the time. |
> | *"LP2 is unsolvable-BY-DESIGN, not unsolved-by-effort"* | settled | **Retracted.** Round 12 D3: the ciphertext cannot separate a true external pad from a short-seed *derived* keystream, which is finite and brute-forceable. The supported claim is **OTP-class**. |
> | *"LOOP TERMINUS … further rotation re-derives these conclusions. Wind down"* | stop | **Wrong as an instruction.** Rounds 12–15 each opened lanes this block asserted did not exist, and Round 12's D3 found the error above precisely *by* rotating again. |
>
> **The distinction that matters for anyone starting fresh work here:** a *coverage bound* ("swept
> 2,165 seeds × 16 generators, best −6.185 against a −5.5 bar") is a fact that saves you from
> repeating a sweep. A *terminal verdict* ("exhausted", "wind down") is a mood, and this repository
> has now been wrong with that mood twice. **Publish bounds; distrust terminals — including these.**

## Round 9/10 — multi-lens armada (2026-08-11 → 17)

A 22-lens wide re-attack, pre-registered per lens (positive control + size-matched null).
**Zero hits.** Full synthesis: `analysis/round10/SYNTHESIS.md`. New eliminations:

- **Plaintext/word channel — NULL.** "words are the map" (L2, 9 readings), "meaning is the road"
  (L3, gematria-sum T1–T5), "numbers are the direction" (R9-DIRECTION, 2,670 positional reads,
  real z=−0.40), and contiguous-passage-in-extended-corpus (L4-skeleton, 224 texts / 22.6M words,
  best 22.7% match z=−1.03 vs a ≥60%/z≥10 bar) all sit inside their nulls. The 2016 hint's three
  clauses are now each tested and dead.
- **Keystream/pad channel — NULL.** 32-bit PRNG seed (L5, 0 hits on covered space; threshold
  proven invalid at full scale → parked, not "unfinished"); finite-state generator / reuse
  (L9-randomness, linear complexity = n/2 exactly, inside anti-repeat control range); short-key
  hand-Vigenère k=4–12 (B2, S1-FAIL — survives only k≥64, out of scope); page-local semantic keys
  (B3, 0 hits / 168k crib readouts); composed key W⊕G (B5, margin +0.064 vs +0.50); artifact-string
  keys under the hand toolkit (B1, doublet z=−14.4 vs the author's OWN output).
- **Non-English / machine plaintext — NULL (B6).** Language-agnostic detectors real z=+1.35 vs a
  +3.0 bar; note the v2-onion base32 body is information-theoretically undetectable (random in
  random) — a permanent, principled blind spot, not a lead.
- **External / provenance — NULL.** SOTA watch (L7, 25 web ops, last verified 3301 msg still
  2017-04-04); community-archive key claims (L6, 0/109,917 Discord msgs clear the "3301 gave
  insiders CIPHER MATERIAL" bar — the 2 "insider" hits are the *public* Gematria Primus); sourced
  primary statement about the pad (L8, 0 of {liber primus, key, pad, gematria, 7A35090F} in ~264k
  chars of Schoenberger court filings — court-records source class clean-negative).
- **Transcription — canon reconfirmed a 4th, independent way (R9-TEMPLATE).** Label-free glyph
  clustering (NOT canon-trained) → 96.93% agreement, clean 29→29 bijection, **no reopener**.
  Bounded: 38.4% of lines glyph-diffable; the OTP pages are where the read is weakest.

**Two prior claims CORRECTED (supersede, per below):**
- *"Flat IoC forces a full-length key"* → **false** (B4/G2): smallest IoC-invisible period at
  N=12,956 is p*≈400. The OTP conclusion rests on the DOUBLET argument, not IoC.
- *"LP2 is an external one-time pad"* → **OTP-class**, one member of a ciphertext-indistinguishability
  class (B4/G4–G5): a SHA-256 counter-mode derived key + filter and ciphertext-autokey over flat
  non-English plaintext both pass the full battery inside the pad model's band (no statistic
  separates them at |z|>2.93).

**Doublet-deficit discriminating power PINNED (B4/G3 + B1 vs RECON-B/B-16):** the deficit (0.664%,
floor 1.50%) excludes *rigid* plaintext-independent keys; it carries NO discrimination once the soft
anti-repeat rewrite is the mechanism (the filter sets the rate) — which is exactly why the
skip/anti-repeat-aware decoders (Campaign XVIII + every B-lane) are the ones that exclude the rest,
to the audited limit of their power.

**Genuinely-new untested INPUT (PA-3), do-not-mistake-for-a-lead-strength:** the author's own ~4 MB
binary pads from the 2013 CicadaOS (`DATA/_560.*`, `761.mp3`⊕`twitter.txt`) — never fed under the
skip-aware decoder. Not held in-repo; needs fetching. Highest-prior remaining input, low absolute prior.

**Instrument caveats (PA-2), carry forward:** R9-DIRECTION lacked a positive control; Campaign XVIII's
FP ceiling was computed at ~400 trials vs 1e7–1e9-trial sweeps (realistic confirm-margin ~0.25, not
~1.3) — any new lane scoring near threshold MUST recompute its FP ceiling at its own N.

## Round 11 — the NUMBER CHANNEL armada (2026-08-17)

Followed the signed hints literally ("the primes are sacred", "either the words or their
numbers", "their numbers are the direction"): every prior exclusion lived on the mod-29 LETTER
stream, so this round attacked the VALUE channel (arithmetic on raw prime magnitudes, in Z,
outside the group where everything was proven) + the two physical channels never transcribed.
Instrument `analysis/round11/lib_numchannel.py`, gated PASS. **7 lenses, ALL NEGATIVE, ALL
positive controls PASSED, 0 hits** (true negatives, not blind scans). Full: `analysis/round11/SYNTHESIS.md`.

- **N1 cumulative-gematria FEEDBACK autokey** (the class the verdict called "open, unbounded")
  — NULL. 48 configs (PT/CT feedback x f{mod29,totient,digitsum} x sign x direction x
  reset/continuous), best -7.438 vs null_max -7.446. Controls recovered PT- and CT-feedback
  plants exactly. First control-validated null on this class.
- **N2 prime-gap / prime-index as data** — NULL, best -6.951 vs -6.901. (prime_gap has only 5
  distinct values = low-entropy; printable-ratio 1.0 is a mapping artifact.)
- **N3 whole-book / segments as number-theoretic objects** — NULL and ANTI-special: 0 primes,
  0 perfect powers, 0 Mersenne-ish, 0 notable bit-lengths across 55 segments; real structure
  total 0 vs null mean 0.125 (LESS coincidence than random). Whole-book prime-concat = 86,084
  bits, no landmark, byte-printable 0.367 = random baseline. Control 11/11 (Mersenne/RSA/perfect-power).
  Kills the "sacred prime" intuition at book scale (already dead at pp49-51 scale).
- **N4 digit-plane separation** (bases 3/5/7/10) — NULL, best -5.728 vs -5.722.
- **N5 totient-ladder escalation** (phi(phi(p)), Carmichael lambda, totient-of-running-sum) —
  NULL, best -6.667 vs -6.722. Control reproduced AN END via phi(prime).
- **S1 interrupter-position channel** (458 F-runes / 457 gaps) — NULL, best -5.994 vs -5.997;
  control recovered a planted gap-message (sep 2.26).
- **S2 separator/ornament channel** — NULL, and RESOLVES the RECON-A "ornaments never read"
  flag: the separators are TYPOGRAPHY (mean run before '/'=2.39 line-wrap, '.'=4.13 sentence,
  '-'=3.96 word; var ratio 0.307), not a hidden payload. Controls (ternary+binary) recovered plants.

NET: the hint-literal number channel — the most-cited "surely they meant the primes" intuition
in the whole mystery — is now a measured, control-validated NEGATIVE. Verdict tightened, not
reopened. Only roadmap residue left is external/low-prior (PA-3 binary pads under skip-aware
decode; dense-OTP re-segmentation) — inputs/imaging, not more transforms of the held stream.
Do NOT re-run any Round-11 lens.
