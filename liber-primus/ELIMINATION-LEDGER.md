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
| **External-artifact sweep** — pull the un-held onion images/HTML from community mirrors and re-extract | ⚠️ no new key | 2026-07-27 OSINT sweep. Downloaded the mirror set (iBotPeaches `/onions/`, archive.org per-onion, scream314, krisyotam) and re-ran extraction. **T1 onion3 5×5-rune JPG → known 2013 RSA message; T5 4gq25.jpg → known 2016 message** (both already-known payloads reproduced, not new). Broadened 60-key OutGuess sweep = null (default-key keystream artifact). **T2/T3 = unidentified high-entropy blobs, still open (low prior).** | `analysis/OSINT-SWEEP-2026-07-27.md`, `analysis/armada_osint/` |

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
| OSINT-2026-07-27 | **External-artifact sweep** | Pulled the onion images/HTML we never held from community mirrors + re-extracted. No new break: T1 (onion3 5×5-rune) and T5 (4gq25) decode to already-known 2013/2016 messages; 60-key OutGuess sweep null; T2/T3 remain unidentified high-entropy blobs. Confirms the "provable hidden data" onion-image lead resolves to standard payloads. | `analysis/OSINT-SWEEP-2026-07-27.md` |
| XVIII | **Skip-tolerant re-decode (item 2c executed) + coverage armada** | Built + validated a key-skip decoder that tracks the desync the ~83% doublet filter induces (rigid misses the correct key at −7.24/8.5%, beam recovers it at −4.15/100%; FP ceiling −6.82; recall 7/8). Then re-ran **every alignment-sensitive family** under it: referenced texts (best −5.88), full 122-text corpus (best −5.808), armada18+19 literary sweeps (88 more texts, best −5.786/−5.754), **autokey under skip** (community's #1 hypothesis — 45 primers, best −6.627), ~620 Vigenère keywords (−6.021), extended numeric (−5.745), self-referential families (first-diff/integral/self-key/ct-feedback) — **all 0 hits**. Prior keytext nulls now **unconditional**; family-by-family accounting in `armada2/COVERAGE-MATRIX.md`. | `analysis/campaign18_skip/` |

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

---

_Sibling docs: `SOLVERS-DOSSIER.md` (community writeup) · `FINDINGS-FOR-SOLVERS.md`
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
