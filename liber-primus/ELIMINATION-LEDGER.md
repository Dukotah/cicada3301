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

From the **ciphertext alone**, the unsolved runic pages are **one-time-pad-class**:
a full-length keystream whose output was deliberately filtered to avoid writing the
same rune twice in a row (~83% suppression — Campaign XI). That is *not* "a hard
cipher" — it is information-theoretically unsolvable **without the external key**,
because for any chosen plaintext a valid structureless key exists. The transcription
is **not** the blocker (verified three independent ways). The only realistic path to
a solve is **external**: the key itself, most plausibly via the never-recovered
"AN END" deep-web page. Nobody should claim LP2 is "solvable with more compute / more
AI" — the math says otherwise.

**What this project can honestly claim:** every attack *we could concretely construct*
has been run and falsified, and the cipher's mechanism is now described to a
parameter — which appears to be *ahead* of the published community state of the art
(which still stops at "autokey/custom"). **What it cannot claim:** that the space of
*all conceivable* external keytexts is exhausted. See "Still genuinely open" below.

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
| **Mechanistic reason keytext-hunting was doomed** | ⚠️ insight | *Any* natural-English running key injects ~3.3% doublets — which are **absent**. Wrong *mechanism*, not wrong *text*. | Campaign IV `analysis/structure/` |

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

---

## What each campaign added (index)

| # | Focus | One-line result | File |
|---|---|---|---|
| I–II | Rig + statistical baseline | IoC·N 1.000, doublet deficit found; rig validated on solved pages | `FINDINGS.md`, `analysis/STATS.md` |
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

---

## Still genuinely open (the honest frontier)

**Update (Campaign XVII — assumption-stack red-team):** the eight load-bearing
premises the whole effort rested on have now each been attacked directly and hold —
key, reading order, hidden subsequence/acrostic, 1-bit channel, transcription,
fixed-function autokey, **plaintext language** (Latin sealed; the load-bearing
exclusions are language-independent), and **book cipher** (pointer schemes into
Cicada's known books yield only word-salad). What survives is therefore only the
**unbounded** (multi-rune-history feedback; a book outside Cicada's known references)
or the **external** items below. The internal attack surface is closed.

Only two productive things remain, and both are **external** — nothing in the
ciphertext can close them:

1. **An untried already-public keytext** Cicada expected solvers to *recognize*. A
   running-key search over a real text is **falsifiable** (the right text at the right
   alignment would decrypt to readable, high-scoring English), so this is the one
   productive avenue left. We tested the *named/referenced* texts, thematic esoterica
   (Campaign III), 15 verified thematic texts (Campaign XII), and **82 more across 10
   lanes (Campaign XIII)** — 112+ named texts eliminated total — but the space of
   conceivable primary sources is not exhausted. **This is why we can't say "100%,"**
   though the frontier is now much narrower. Trivially extendable: add a slug/ID to
   `analysis/campaign12/fetch_keytexts.py` and re-run `run_sweep.py`.
2. **The "AN END" deep-web page** — the only place a key might physically exist.
   Cold trail (Tor v2 dead). CT-log brute is now **ruled out as non-viable** (Campaign
   XIII); the only tractable-but-low-prior path left is a finite lookup of archived
   v2-onion corpora.
2b. **Word-length skeleton match (best fresh avenue, Campaign XIV / Fable red-team):** an
   OTP hides symbol values but not word boundaries, which are preserved and — measured —
   English-shaped (P5). Slide each page's rune-word-length sequence over the 112+
   already-fetched corpora treated as **plaintext** (not key); a match beyond the
   shuffled-control FPR yields plaintext directly. Full proposal in
   `analysis/campaign14/REDTEAM-PROPOSALS.md`.
2c. **Skip-tolerant / filter-aware re-decode (soundness patch):** all keytext/keystream
   nulls assumed *rigid* key alignment; a doublet filter perturbing key consumption could
   make them unsound. A filter-aware beam decoder + Old-English/Latin re-scoring over the
   existing corpus would discharge the last conditional-null worries.
3. ~~Transcription coverage gap~~ — **RESOLVED (Campaign XIV):** the community's ~75-page
   figure is 72 rune-pages including the **already-solved** intro/koan pages (elevated
   IoC, normal doublets). There is **no new *unsolved* material**; pages 0–55 are the
   complete unsolved corpus.

## Do NOT re-run (proven dead — reasons recorded above)
More keywords • more short/periodic keys • more number-theoretic or PRNG keystreams •
autokey/autoclave • differencing/integration • page-on-page keying • transposition-only •
fractionation • substitution/homophonic • image stego • AI-vision re-transcription •
treating pp49–51 as a runic key. All eliminated with the reason and a reproduce pointer.

---

_Sibling docs: `SOLVERS-DOSSIER.md` (community writeup) · `FINDINGS-FOR-SOLVERS.md`
(short form) · `analysis/OPEN-AVENUES.md` (ranked avenues) · `../PICKUP-HERE.md`
(resume point). This ledger supersedes their scattered "ruled-out" tables as the
single complete index._
