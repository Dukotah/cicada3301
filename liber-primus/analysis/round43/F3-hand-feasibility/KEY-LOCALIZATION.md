# KEY-LOCALIZATION — where does the paper key physically live?

Round 43, lane F3c (hand-feasibility). First explicit modelling of the physical constraint:
~13,000 rune encryptions were executed by a human hand (or from a human-prepared printed pad)
in 2013/14, and the author's design philosophy (every prior stage solvable, self-contained,
fairly pointed) implies the key or its generator was made reachable in what was RELEASED.

All statistics below were computed fresh this session from
`data/krisyotam_runes.txt` (and controls from `data/sources/relikd_*.txt`,
`data/keys/solved_plaintext.txt`). No prior measurement was consulted.

---

## 0. The corpus, quantified (what the key must cover)

- `krisyotam_runes.txt` = the ky2khlqdf onion-7 dump (58 images, `0.jpg..57.jpg`), 57 `%`-separated
  pages, **13,136 runes total**.
- Final page (95 runes) is the plain-runeglish Parable (IoC 1.82). Everything else is
  statistically flat ciphertext (per-section IoC 0.94–1.00).
- **Keystream needed: ~13,041 rune-values mod 29**, across 56 ciphertext pages.
  Per-page need: min 66, mean ~233, **max 277** rune-values.
- Page layout: 604 hand-lettered lines, mean 20.97 runes/line (max 26). Word separators
  preserved: 3,604 words, mean 3.51 runes/word. Sentence dots: 181. Section marks: 9.
- Released render geometry: 2400x3600 px (`0_wisdom.jpg`, and the avowy post gzip inner JPEG,
  400 DPI per gzip metadata) → **physical page 6"x9"**. The avowy gzip header also leaked
  `was "data.out", from Unix, last modified Fri Jan 24 15:10:12 2014` — a production-pipeline
  timestamp: pages were being rendered/packaged *during* the January 2014 run, i.e. encipherment
  and release overlapped; the pad (if pre-printed) existed by early January 2014.

### Hand-execution budget
A practiced operator with a 29x29 tabula recta (or a two-strip St-Cyr slide relabeled with
runes) sustains ~2–4 operations/minute including transcription checking. 13,041 ops ≈
**55–110 hours of deskwork** — weeks of evenings. This is feasible but *large*: it strongly
rewards key designs with low per-symbol overhead (arithmetic streams, running text in front
of you) and punishes designs needing per-symbol table lookups in a separate document
(book running key from a dense printed page is ~2x slower than a pre-written key line).
The most ergonomic physical format is the classic worksheet: key line written *above* the
plaintext line, ciphertext written below — which makes the key a **13k-rune handwritten
worksheet stack (~50 sheets at 10 lines/sheet)**, the single largest physical artifact of
the whole project. Where is it, or what generated it?

---

## 1. The measured fingerprint of the hand process (computed this session)

| statistic | unsolved ciphertext | expected (uniform indep. key) |
|---|---|---|
| unigram IoC (x29) | 1.000 | 1.000 |
| periodic IoC, m=1..40 | flat (max 1.008) | flat |
| cross-page kappa (same offset), mean over all 1,540 page pairs | 0.0348 | 0.0345 (=1/29) |
| successive-diff distribution, bins 1..28 | flat (0.030–0.039) | flat |
| **doublet rate P(c_i = c_i+1)** | **0.0068** (89/13,078; pure unsolved stretch 0.0073) | **0.0345** |
| chi2 of diff distribution (df 28) | 345.7 (all excess in bin 0) | ~28 |

Controls:
- LP-voice plaintext (cleaned solved-trail plaintext, 2,203 runes): IoC 1.67, doublet rate
  0.0391, successive-diff bins range 0.0186–0.0495 (min at d=7).
- Parable page (released plain runes): 1 doublet in 94 pairs.
- Generic English → runes (War & Peace, 288k pairs): doublet 0.0379.
- Doublet suppression is uniform across boundary types (within-word 0.0063, across word-sep
  0.0084, across line-break 0.0076, across sentence 0.0060) → the rule operates on the raw
  glyph stream, blind to words/lines/layout.
- Stable across the whole book: pages 0–27 rate 0.0067, pages 28–56 rate 0.0069. One
  discipline, one process, start to finish.

### The floor theorem (the lane's central result)

For any cipher of the form c = p + k (mod 29) with keystream **k independent of p**:

    P(c_i = c_{i+1}) = Σ_d P_P(diff=d) · P_K(diff=-d)  ≥  min_d P_P(diff=d)

With LP-voice plaintext, min_d P_P(d) = **0.0186** (and that floor is attained only by the
degenerate constant-increment key d=7, a progressive Caesar, excluded by every other
statistic). Any realistic independent keystream — true-random pad, book running key
(predicted 0.0354, computed by convolution), prime/totient stream, pi digits — predicts
**0.033–0.035**.

**Observed: 0.0068–0.0073. That is 2.7x below the hard floor and 5x below every realistic
plaintext-independent keystream. z ≈ 17σ (expected ~440 doublets under a blind pad; observed 89).**

> **Consequence: the ~13k-glyph blind pad never existed as a blindly-applied artifact.**
> Whoever/whatever produced the keystream could SEE the emerging ciphertext (or equivalent
> feedback) and avoided writing the same rune twice in a row, slipping ~0.7% of the time.
> The "paper key" is therefore not a static pad photocopied and applied mechanically;
> it is a **desk process** — a generator plus a rejection/skip rule — and the generator
> itself can be small enough to memorize or print on one sheet.

Surviving model classes:
1. **Skip-rule encipherment**: any underlying keystream (even a short repeating word) +
   "if the output rune equals the previous one, advance the key one extra step / re-roll".
   Reproduces every measured statistic; the 89 residual doublets are human slips (and their
   positions are then *key-schedule anchors*). Crucially the skips **self-desynchronize the
   key**, which is sufficient by itself to explain why 12 years of periodic/running-key
   attacks fail against what could be ordinary Vigenère underneath. Author precedent: the
   solved pages already use key-skip mechanics (F-interrupters; `FIRFUMFERENFE`).
2. **Scribal haplography at the lettering stage**: encipherment was blind (true pad), but the
   hand-lettering pass dropped doubled runes (aesthetic rule or eye-skip), deleting ~250
   glyphs (~2%) from the released ciphertext. Every positional attack then desyncs after the
   first drop. Testable (insertion-tolerant decoding).
3. A structurally doublet-free non-additive cipher. No classical hand cipher over a prime
   alphabet (29 admits no Playfair/bifid grid) has this property; mod-29 arithmetic is
   clearly the author's idiom (gematria, phi(prime) page). Lowest weight.

Additional computed facts that any key hypothesis must satisfy:
- **No pad reuse anywhere**: mean cross-page kappa exactly 1/29; max pair consistent with
  noise over 1,540 trials. The process never rewound — 13k fresh key values.
- **One genuine long repeat**: the 7-gram ᛉᛚᛒᚱᛋᚳᛋ(X L B R S C/K Z-class) occurs at
  **page 27 offset 28 and page 54 offset 70** (expected count 0.005, p≈0.5%). Either a
  transcription duplication, or the only place the key stream + plaintext coincide — a
  free crib-anchor if any generator hypothesis reaches those pages.
- Word lengths pass through unencrypted (mean 3.51 runes/word, 536 one-rune words):
  plaintext segmentation was released intact — no nulls, no transposition.

---

## 2. The author's production workflow, and where key material can leak into the release

Reconstructed pipeline with leak audit (release = onion pages + images + trail artifacts
2014 solvers already held):

| stage | physical act | what leaked into the RELEASE |
|---|---|---|
| 1. compose | plaintext draft (English in runeglish orthography) | word lengths, sentence dots, section marks — all preserved verbatim in ciphertext |
| 2. key + encipher | worksheet: key source + tabula/slide + rejection rule | the doublet fingerprint (process, 17σ); kappa=1/29 (never rewound); the residual 89 slips; possibly the repeated 7-gram |
| 3. hand-letter | 6"x9" leaves, ~21 runes/line, illumination | line geometry, page capacities (131/121/137-rune short pages = illustration pages), potential haplography channel |
| 4. photograph/render | 400 DPI scans → JPEG | gzip timestamp Jan 24 2014 `data.out`; render variants; **stego capacity** (precedent: every 2014 rune image carried its key/instructions in outguess; the 1033 magic square came out of OOB JPEG data) |
| 5. release | onion HTML, file order | page order 0..57; titles/ids (`133`/`331`); the three 256-byte RSA hex blobs (761/1033/3301); the Blake quote title "For Every Thing That Lives Is Holy"; the Self-Reliance book-code (stage 1 of the whole 2014 trail) |

Design-philosophy constraint: every pre-LP key the author ever used was **released in-band**
— `DIVINITY` and `FIRFUMFERENFE` are the book's own vocabulary; "welcome pilgrim to the" was
the running plaintext itself ("Key: Continuation of key"); phi(prime) is announced by the
totient/prime ideology of the text; the 2014 entry key was a *printed mass-market essay*
(Self-Reliance) pointed to by a riddle. The author's established practice localizes key
material in exactly three places: **(a) the book's own plaintext, (b) public printed texts
pointed to in-trail, (c) small arithmetic generators (primes/totients)** — never an
unreachable random pad. The floor theorem above *independently* says the same thing: there
was no blind 13k pad.

---

## 3. Candidate inventory (released corpus as key material)

Needed: 13,041 values mod 29; per page ≤ 277. "Hand process" = how a human turns the object
into a keystream at the desk.

| # | candidate (released where) | yield as mod-29 stream | hand process | verdict |
|---|---|---|---|---|
| C1 | **Short word keys from the book's own vocabulary** (practice released via solved pages: DIVINITY, FIRFUMFERENFE) | unlimited (repeating, ≤13 runes) | memorized word + tabula + **skip rule** | TOP. Zero artifact; periodicity erased by skips; matches every measurement |
| C2 | **Prime/totient tables** (precedent released: the solved phi(prime) page; "the primes are sacred") | unlimited; p_i mod 29 / (p_i−1) mod 29; 277 primes/page → primes to ~2,000th | one printed prime-table sheet per book page, pencil mod-29 column | TOP. Author already did exactly this for a full page; cheapest per-symbol cost of all candidates |
| C3 | **Self-Reliance, Emerson** (released as THE book key, stage 1 of 2014: "The work of a private man… He trusted himself" → book code → first onion) | 40,985 runes = 3.1x need | printed essay + translit + tabula (+ skip rule mandatory per floor theorem) | STRONG. The only *mass-printed paper object* the author verifiably keyed from |
| C4 | **The book's own plaintext** (running key / autokey; released practice: "Key: Continuation of key" across images 14–15) | solved-trail plaintext ~2.2k clean runes; full book plaintext ≈ need, released progressively as pages fall | author's own draft = the pad; nothing extra exists | STRONG conceptually; bootstrap problem for solvers is deliberate (chain design) |
| C5 | **Blake corpus** (released pointer: onion-1 title "For Every Thing That Lives Is Holy" = Marriage of Heaven and Hell / America: A Prophecy) | MHH ≈ 40k+ runes | printed poem + tabula + skip | MEDIUM. Pointer is real and deliberate but was "consumed" by the 1033.jpg stage |
| C6 | **Outguess payloads of the 58 released page JPEGs** (precedent: every 2014 rune image carried keys/instructions via outguess; magic square arrived in OOB bytes) | capacity ~30k usable bits per 1327x1427 image (measured on zN4h51m); a page needs only 277x5 ≈ 1.4k bits | not hand — but it is the one workflow stage where the author could attach each page's pad to the page itself with zero new objects | MEDIUM. We hold crops, not canonical originals; an extraction at entropy 7.997 b/B exists on one render (held locally as `avowy` note) |
| C7 | **The three 256-byte RSA hex blobs** (released in onions 2/3/4 pre-pages, labeled 761/1033/3301) | 256 bytes mod 29 ≈ one page's key each (page needs 229–277) | hex→byte→mod 29 by pencil, 256 ops/page — tedious but real | LOW-MEDIUM. Only covers 3 pages; but the label-primes and page-prime ideology rhyme; test is nearly free |
| C8 | **Magic squares** (released: 5x5 sum-1033 square in OOB; onion-6 form demanded squares but *accepted any valid square*) | 25–50 numbers | repeating key period 25 | **ELIMINATED this session**: periodic IoC flat through m=40; and the form accepting ANY square proves the squares were authentication, not key material |
| C9 | **Rune poem (OE)** (the canonical futhorc source text; self-contained with the alphabet) | 2,289 runes ≈ one 10-page section per restart | printed poem + tabula + skip | MEDIUM-LOW. Needs per-section restarts (9 section marks exist) |
| C10 | **Per-line / per-word keys from page geometry** (604 lines released) | 604 or 3,604 values | one shift per lettered line | **ELIMINATED this session**: a locally-constant key forces ciphertext diffs to mirror plaintext digraph structure; observed diffs are flat (Pearson vs LP-voice diffs ≈ 0.1, and vs generic English −0.02) |
| C11 | Onion page numerics (`133`/`331`, `107/167/229`, port 5243) | seeds only | — | seeds for C1/C2 offsets, not streams |

---

## 4. Ranked joins (candidate x hand process) with tests

Every surviving join carries the **no-doublet rejection rule** (or, in J5, the haplography
variant) — this is now a *filed constraint*, not an option: the floor theorem forbids blind
application of any independent keystream.

**J1. Short vocabulary key + tabula + skip-on-doublet (C1).** The key lives in the author's
head and on a margin scrap; the released localization is the solved pages' demonstrated
practice plus the book's own vocabulary. Explains the 12-year failure of periodic attacks
(skips erase the period). TEST: implement skip-aware Vigenère search — beam/Viterbi over
skip positions (skip prior 3.3%/symbol, slip prior 0.7%), key lengths 1–15 from (i) LP-voice
vocabulary, (ii) brute short keys; validate the decoder first on synthetic pages enciphered
with the exact rule; run per page (pages 54/27 first, exploiting the repeated 7-gram as a
same-plaintext anchor). Cost: days of compute, all local.

**J2. Prime-stream + skip/interrupters (C2).** The paper artifact = ~15 sheets of printed
prime tables (reachable to any solver; "sacred primes" is the released pointer; a full page
was already solved this way). TEST: per page, streams k_i = p_{a+i} mod 29 and (p_{a+i}−1)
mod 29 (and decimations p_{a+ci}) over start indices a ≤ 10,000, each with skip-rule
branching; score quadgrams. Cheap: ~10^7 light decodes/page.

**J3. Released-text running key + skip (C3 Self-Reliance; C5 Blake; C4 own plaintext).** The
paper key = a printed copy of a text the trail itself pointed at. TEST: running-key DP with
skip branching over every start offset (Self-Reliance alone: ~28k offsets x 56 pages),
both add/subtract, 29 rotations; include the solved-trail plaintext concatenation as key
text. This has never been done WITH skip-tolerance — all prior running-key sweeps assumed
rigid alignment, which the floor theorem says cannot work.

**J4. Pad embedded in the released page images (C6).** The 13k pad was never paper at
release time — it rides inside each page's JPEG, exactly as every 2014 key did. TEST:
(1) acquire canonical onion-7 originals (0.jpg..57.jpg — iBotPeaches mirror holds them);
(2) outguess (default + derived passphrases: page primes, `133`, `3301`), plus OOB/EXIF/DCT
audit; (3) reduce any payload mod 29 and subtract from its own page at offset 0 (both
directions, 29 rotations). Decisive and bounded (~an afternoon once originals are local).

**J5. Haplography model (lettering-stage loss).** Blind pad OR plain periodic cipher, but
~250 doubled runes were dropped when inking. The "key" question then re-opens toward C2/C3
*without* the rejection rule, and the physical pad is a real 50-sheet stack the author kept.
TEST: insertion-tolerant decoding — periodic Vigenère with ≤2% symbol-insertion edits
(Smith-Waterman-style DP over key phase); pilot on the three shortest pages (66/76/85
runes) where ≤2 insertions are expected. Also: inspect high-res scans at the 89 surviving
doublets for ink hesitation/cramping (scribe noticing the rule).

**J6. 256-byte blobs as page pads (C7).** TEST: subtract each blob-stream (bytes mod 29,
also nibbles mod 29, reversed, byte-pairs mod 29) from every page, offsets 0–20, both signs;
quadgram score. Near-zero cost; do it as a side dish to J4.

### Eliminated by this session's computation (fresh, not from any ledger)
- Magic-square repeating keys (period ≤ 40 periodicity absent; squares shown to be
  non-unique authentication tokens by the onion-6 form text).
- Per-line / per-word constant shifts (diff spectrum flat, not plaintext-shaped).
- **Any blind (plaintext-independent) additive keystream whatsoever** — pad, book, primes,
  digits — applied without a feedback rule: doublet rate 0.0068 vs hard floor 0.0186 (17σ).
  This is the constraint this lane files for the project.

---

## 5. Answer to the lane question

Where does the paper key physically live? **Not in a 13,000-glyph pad used blind — that
object is statistically excluded by the released ciphertext itself.** The key lived on the
enciphering desk as a *small generator plus a visible-ciphertext rejection rule*: a
memorized word from the book's own voice (J1), a printed prime table (J2), or a printed
trail-text (J3) — all three localizations were deliberately released (solved-page practice,
the totient page, the Self-Reliance/Blake pointers), exactly as the author's fairness
philosophy predicts. The residual 89 doublets are the human slips of that desk process and
double as key-schedule anchors. The main alternative worth budget is that the pad's digital
twin was attached to the release itself inside the page JPEGs (J4), the author's
demonstrated habit for every key before it.
