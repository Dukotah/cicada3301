# Liber Primus — Negative-Results Archive

**What a frontier AI model eliminated, so the next researcher doesn't repeat it.**

_Analysis engine: **Claude Opus 4.8** (Anthropic), driven via Claude Code as a
multi-agent "armada"; the final hint-derived probes (hill5-magic, wordsum-selfkey)
ran under **Claude Fable 5**. Work performed 2026-06 → 2026-07 on
[github.com/Dukotah/cicada3301](https://github.com/Dukotah/cicada3301). Every entry
below is a **run, recorded, reproducible negative** — an approach that was tried
against the unsolved Liber Primus (LP2) pages and did **not** yield the answer._

> **Why this document exists.** These are long shots taken deliberately. LP2 looks
> like a one-time pad, which is information-theoretically unbreakable from ciphertext
> alone — so the value of this project is not a solve but a **map of dead ends**: a
> future solver can see that a state-of-the-art model was run against each of these
> candidate solutions and that none was the answer, and spend their time elsewhere.
> Provenance is in the git history — every commit carries a `Co-Authored-By: Claude
> Opus 4.8` trailer and a dated message.

---

## How to read a "negative" here (methodology)

- **Validated rig.** All attacks run on a cryptanalysis toolkit that reproduces every
  *known* LP solve (`liber-primus/tests/validate.py`) and whose scorer re-finds the
  known key DIVINITY at **−4.34** (`attack.py selftest`).
- **The number.** Scores are per-quadgram English log-probability (`score_norm`).
  **Readable English ≈ −4.0 to −4.4; the break threshold is ≈ −5.0; random runic
  noise ≈ −7.4.** A "null" means the best result over the entire variant sweep stayed
  in noise — no page, no offset, no key produced readable plaintext.
- **Variant sweep.** Unless noted, each attack was run both cipher directions
  (C−K and C+K), with and without Atbash reflection, with and without the ᚠ-interrupter
  rule, **per page and over the whole-book concatenation**.
- **Adversarial verification.** OSINT / identity claims were checked by independent
  multi-vote agents (majority-refutes-to-kill), not accepted on a single pass.

---

## Part A — Cryptanalysis of the runic pages (Campaigns I–VII)

Every family below is **eliminated**. Best score ever recorded across all of it:
**−6.02**. Nothing reached the −5.0 readable-English break.

### Key / keystream families
| Approach | Detail | Result |
|---|---|---|
| Vigenère, all key lengths | keyword lists + per-page exhaustive L1–4 (interrupter beam) + hill-climb L4–12 | null |
| Additive keystreams | consecutive primes, totient, Fibonacci, OEIS A061474, prime-counting, CFB, φ(prime)/prime−1, with offset search | null |
| Autokey / differencing | ciphertext- & plaintext-autokey, first-differencing, page-on-page keying | null |
| Hill cipher | 2×2 exhaustive (all 682,080 invertible matrices) + 3×3 sampled | null |
| Atbash / shift | reflection + all shifts, per page | null (only re-solves already-solved pages) |

### Running keys (every text tried)
Mabinogion, Self-Reliance, The King in Yellow, Liber AL, Agrippa, Tao Te Ching,
Blake, Gospel of Thomas, Anglo-Saxon Rune Poem, solved-page text (Latin **and**
rune/gematria space), Cicada's own PGP prose, and the full esoteric corpus:
**Iamblichus, Nicomachus, Corpus Hermeticum, Sepher Yetzirah, Mathers, John Dee
(Monas + Enochian), Rosicrucian (Fama/Confessio/Chymical Wedding), Pistis Sophia,
Lesser Key of Solomon, Crowley (Book of Thoth).** → **all null.**

### Structure / representation
Off-diagonal bigram structure, n-gram repeats, periodicity (lags 2–30), inter-page
shared keystream, gematria prime-value modular sums, word-boundary positional bias,
the doublet residual, Latin-multigraph expansion, page reorderings, runes-per-line
count stream, fractionation/bifid, transposition-only, monographic substitution
(ruled out by IoC). → **all null.**

### Forensics / images / transcription
Real OutGuess 0.4 (built from source, validated on all 2012–2014 payloads) +
steghide/stegseek on every page image; LSB/DCT sweep; EOF/appended-data + EXIF; PGP
operational forensics (RSA sound); template + 99.2%-accuracy glyph-classifier
re-transcription. → **no payload; canon is image-faithful; no higher-res master exists.**

### Campaign VII — the specific "nobody ever ran it" leads (2026-07)
The OSINT sweep (Campaign VI) reopened concrete leads. All were then run:

| # | Lead (candidate solution) | Best | Verdict | Script |
|---|---|---:|---|---|
| B1 | 2012 **Mayan rotation key** as a shift | −6.895 | null | `campaign7/b1_mayan.py` |
| B3 | **HINTS-NEVER-USED** numerics (P.S. digits, telnet missing-primes + gaps, trailing-space seqs) | −6.757 | null | `campaign7/b3_hints.py` |
| A2 | **pp49-51 base-60 token pad** as key (base 59/60/62/64) | −6.72 | null | `campaign7/a2_tokenpad.py`, `a2_altbase.py` |
| B2 | **token pad ⊕ 2014 onion-trail hex** *(the op a wiki author proposed and nobody ran)* | −6.597 | null; XOR stays random | `campaign7/b2_onion_xor.py` |
| — | token pad as its **own byte-domain ciphertext** | 0.45 printable | null; no ASCII | `campaign7/token_as_ciphertext.py` |
| B4 | **page-56 512-bit hash** as key seed (raw / hex / SHAKE-256 / SHA-512 & BLAKE2b chains) | −6.679 | null | `campaign7/b4_hash_kdf.py` |
| C1 | **doublet-avoiding running key** (beam search over key-skip trajectory) | −6.086 | null | `campaign7/c1_skipkey.py` |
| — | token bytes as a **book-cipher index** into the runes | −7.339 | null | `campaign7/token_as_index.py` |
| C2 | **cuneiform / base-60 numerals** (17 13 55 1; 1033; 3301) as keys | −6.725 | null | `campaign7/c2_cuneiform.py` |

Full narrative: [`liber-primus/analysis/campaign7/CAMPAIGN-VII-FINDINGS.md`](liber-primus/analysis/campaign7/CAMPAIGN-VII-FINDINGS.md).

### Community "false holes" — the wiki's own untried ideas, tested
The Uncovering-Cicada *"Ideas and Suggestions"* wiki and solver repos list methods
"never tried." We ran them (`campaign7/false_holes.py`) so the record is explicit:

| Idea (as proposed by the community) | Best (unsolved) | Verdict |
|---|---:|---|
| **FH1 — "count spaces as runes":** word/clause/line separators *advance* the keystream instead of being ignored | −6.904 | **false hole** — null at every separator-set × keystream |
| **FH2 — section-split + shift by the first rune's gematria** | −6.847 | **false hole** — null (subsumed by the per-page shift sweep) |
| **FH3 — segment key-reset Vigenère** (r4nd0mD3v3l0p3r's `splitBy=segment`): key restarts at each boundary | −7.008 | **null on unsolved** — but it *correctly re-solves the known AN END page* (−5.28), so the technique is real and already accounted for; it just unlocks nothing new |
| **FH4 — "use OutGuess data to relocate the runes before shifting"** | — | **false premise, not runnable** — our Campaign VII stego (real OutGuess 0.4) proved the LP rune pages carry **no** payload; the tabs/spaces OutGuess data belongs to the 2012/2014 *clue* images, not the rune pages. There is no relocation data to apply. |

FH3 is the instructive one: a proposed method that *works* (it re-derives a solved
page) yet still produces no new plaintext — the clearest possible evidence that the
wall is the missing key, not a missing technique.

### "Cicada told us the approach" — the hint-derived methods, tested
The strongest meta-hypothesis (Cicada's puzzles are self-teaching, so the verified
hints encode the method) was audited systematically: every primary-source hint was
mapped to its operational method classes and each class checked against the record
([`liber-primus/analysis/campaign7/HINT-DERIVED-METHODS.md`](liber-primus/analysis/campaign7/HINT-DERIVED-METHODS.md)).
Three results a future researcher should know:

1. **The "find the right keyword" genre is mechanically dead.** Per-page exhaustive
   Vigenère L1–4 + interrupter beam and hill-climb L4–12 already covered **every
   possible keyword** of those lengths — so even if a hint names the key
   (SACRED, INSTAR, EMERGENCE, …), it was already tried. No keyword ≤ ~12 runes solves
   any unsolved page. Stop keyword-hunting.
2. **The book's own matrices are not the key** (`hill5_magic.py`): the three matrices
   Cicada printed (5×5 trace-1033 from SOME WISDOM, 5×5 trace-3301, 4×4 trace-10673) +
   φ-substituted variants, as Hill ciphers mod 29 — all six **are invertible** (fair
   test), all transforms (M, Mᵀ, M⁻¹, (Mᵀ)⁻¹), per page + whole book → best −6.873, null.
   First rigorously scored, recorded run of these matrices.
3. **"Their numbers are the direction" (verified 2016 hint) does not cash out as
   word-sum self-keying** (`wordsum_selfkey.py`): gematria-prime-sums of words driving
   the next word's shift (cipher-fed, plain-fed, cumulative, φ-of-sum, rune-prime
   autokey) → best −6.897, null.

The structural counter-argument (HINT-DERIVED-METHODS.md §4) explains why: any
deterministic scheme derived from *public* material is a fixed keystream, but the
doublet fingerprint is that of a **random filtered stream**. The hints most plausibly
describe how to use a key that was never published — not how to derive one.

---

## Part B — Two mechanistic impossibility results (the strongest findings)

These are *why* the above all fail — the most useful thing here for a future solver:

1. **Natural-language running keys are excluded by mechanism.** A real English running
   key *injects* ~3.3% adjacent doublets. LP2 shows **0.68%**. The doublets are
   *absent*, so running-key-over-natural-text is the wrong **mechanism**, not the wrong
   book. **Stop hunting for "the right text."** (We even tested the escape hatch — a key
   that *skips* to avoid making doublets, C1 above — still null.)
2. **The keystream was itself filtered to avoid adjacent repeats.** The full fingerprint
   (flat IoC, no period at any lag, perfect off-diagonal independence, uniform *soft*
   diagonal-only doublet suppression, ~20% residual) is reproduced by soft-rejection
   sampling from the empirical unigram distribution → an **OTP / long running-key whose
   output was filtered**, or a by-hand "don't write the same rune twice" rule. Any real
   key is therefore **non-linguistic** (numeric / structured) — which is why Campaign
   VII chased numeric artifacts (and why they too came up empty).

**Bottom line:** consistent with a **one-time pad whose key was never published.** If
so, no ciphertext-only attack can ever succeed.

---

## Part C — OSINT negatives (no external key exists publicly)

Confirmed dead via adversarial verification: the 2017 "Beware false paths" PGP message
(authentication-only, no key material), a claimed page-32 numeric matrix (does not
exist), the base-60-indexes-the-files claim (false), onion cookie hashes & magic-square
digit streams (real but tested as keys, null). No insider leak of key material has ever
surfaced; Cicada has been silent since the verified **April 2017** message. Every
machine-readable transcription traces to **one origin** (rtkd/iddqd) — unanimity, not
independence — and our image-independent classifier confirms canon anyway.

Detail: [`liber-primus/analysis/osint/CAMPAIGN-VI-OSINT-FINDINGS.md`](liber-primus/analysis/osint/CAMPAIGN-VI-OSINT-FINDINGS.md),
[`liber-primus/LP2-ANALYSIS-SUMMARY-2026.md`](liber-primus/LP2-ANALYSIS-SUMMARY-2026.md).

---

## Part D — What is genuinely still open (for the next researcher)

Not everything is closed — these are untried or need external input. If you pick this
up, **start here**, not at Part A:

1. **A corrected pp49-51 (p50) transcription** from the page image. scream314 flags its
   own p50 base-60 read "wrong!!!"; a clean re-read could change 104 of the 256 token-pad
   bytes and reopen the token-as-key tests. (AI vision failed on these dense pages; needs
   a human or a per-glyph pipeline.)
2. **The unfound deep-web page** that page-56 hashes to (`36367763…c2a8b4`) — the only
   place a key might physically persist. Tor v2 host is dead; a CT-log / archive hunt is
   the low-odds tail.
3. **A genuinely independent transcription** (non-rtkd lineage), or an alternate scan
   that contains material our corpus lacks.
4. **A new Cicada 3301 release.** External, and the cleanest possible unblock.

Ranked live leads and reproduction: [`MASTER-ROADMAP.md`](MASTER-ROADMAP.md).

---

## Reproduce / cite

```bash
git clone https://github.com/Dukotah/cicada3301 && cd cicada3301/liber-primus
python3 tests/validate.py        # rig reproduces all known solves
python3 attack.py selftest       # scorer re-finds DIVINITY at -4.34
# Campaign VII negatives (each writes a *_results.json):
for s in b1_mayan b3_hints a2_tokenpad a2_altbase b2_onion_xor \
         token_as_ciphertext b4_hash_kdf c1_skipkey token_as_index c2_cuneiform; do
  PYTHONUTF8=1 python3 analysis/campaign7/$s.py
done
```

Each `analysis/campaign7/*_results.json` holds the full result (best score, per-key
breakdown, sample plaintext) for independent audit. If you reproduce a *different*
result on any of these, that is itself a finding — please open an issue.

_Archive maintained alongside [`MASTER-ROADMAP.md`](MASTER-ROADMAP.md). Negative results
are results._
