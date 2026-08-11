# Fresh-eyes review — unexhausted angles (2026-08-11)

> **SUPERSEDED IN PART — all five tracks were run the same day. Results:
> `research/ROUND-8-RESULTS.md`; kill entries: the Round-8 block in
> `research/DEAD_ENDS.md`. All five came back NEGATIVE.**
>
> Two numbers quoted in §3 below were measured over the whole krisyotam file, which
> includes the two SOLVED LP2 pages (real English), and do not survive correct
> scoping to the 55 unsolved pages:
> - the clause-edge effect (+0.315 runes, p = 0.039) is **+0.253, p = 0.143 — not
>   significant** on the unsolved pages;
> - the word count is **3,316**, not 3,367, and LP2 is *distinguishable* from large
>   English corpora (KS 0.036 vs Moby Dick, crit 0.026), not indistinguishable.
>
> The reasoning about which dimensions were unexamined held up; those two
> supporting statistics did not. Read this document for the argument, and
> ROUND-8-RESULTS.md for what is actually true.

A deliberately adversarial read of the whole repo by someone who did *not* run any of
the prior rounds. Premise: the ledger's "ciphertext-only COMPLETE / external-input-only"
verdict is well-earned for the families it actually tested — but it is **not** the same
statement as "everything has been tried," and in a few places the repo says the stronger
thing. Below is what is genuinely still open, ranked by expected value.

Nothing here proposes re-running a killed family under a new name. Where an angle touches
a `DEAD_ENDS.md` entry, the specific reason the prior kill does not reach it is stated.

---

## 0. What is honestly closed (so this document is not mistaken for optimism)

Rune-value cryptanalysis really is done: periodic keys 1–40, running keys, autokey,
differencing, page-keying, fractionation/bifid/trifid coordinate streams, transposition
(all columnar widths), polygraphic/Playfair, interleave, keel/transition-lattice,
misfiled-plaintext windows, no-repeat inversions, image byte/DCT stego, three
transcription lineages, the AN-END OSINT target. Those are measured-closed, not argued-closed.
Don't reopen them.

The angles below are all in dimensions the program **never measured**.

---

## 1. The one-time pad may be 32 bits wide — exhaustive seeded-PRNG reconstruction

**The gap.** Every round proved the same thing: the keystream is *full-length and
structureless*. That is the signature of a one-time pad — and it is equally the signature of
`srand(time(NULL))`. The program measured keystream **structure** and correctly found none;
it never measured keystream **entropy**. A hobbyist in 2013–14 writing an enciphering script
almost certainly did not source 13,136 symbols from a real pad. They called a PRNG.

A seeded PRNG stream is statistically indistinguishable from an OTP by *any* test the repo
ran (flat IoC, no period, no boundary reset, continuous across the book — all exactly what a
single scripted pass over one long file produces). But it is only 32–48 bits of key.

**Why this is not R1-H2 ("self-avoiding LCG keystream", Gate-#1 KILL).** That kill rested on
three objections; none survives contact with a *bounded* key family:

| R1-H2 objection | Why it doesn't reach this |
|---|---|
| "OTP-class objects admit a valid key for any chosen plaintext" (page-0 underdetermination) | True for unconstrained keys (29ⁿ). False here: the key is a **deterministic function of a ≤2³² seed**. Unicity distance — 12,956 symbols × ~2.5 bits/symbol of English redundancy ≈ 32,000 bits of constraint against ≤48 bits of key — puts the expected number of spurious English-scoring decrypts at ~0. English cannot be manufactured by construction from 4·10⁹ trials. |
| "It's a keyspace search scored by quadgrams" | It is an **exhaustive** search of a *named, finite, historically-motivated* family with a computable false-positive budget. A null result eliminates the family outright — that is a real negative, not a fishing expedition. |
| "Ground truth was synthetic only" | The harness anchors two ways: (a) self-plant (encipher known English at a known seed, confirm recovery), and (b) it must reproduce the solved pages in its degenerate fixed-key mode. |

**Why this also escapes the R1-H3 / R3-H1 / R3-H2 "collision-skip is uninvertible" kills.**
Those kills are about *decoding without the key* — a decoder can't see which positions stalled,
so it must search them. With a candidate seed you never decode: you **replay the encoder
forward** and compare to the ciphertext. The rejection rule (`redraw if c[i] == c[i-1]`) is a
one-line addition to the generator loop and costs nothing. This is exactly the mechanism that
produces the no-repeat rule naturally, and it is only attackable from the seed side — which is
the side nobody has attacked.

**Sweep plan (embarrassingly parallel — ideal armada / GPU work).**

- glibc `rand()` after `srand(time(NULL))`, unix seconds Jan 2012 → Jul 2014: **≈ 7.9·10⁷ seeds.**
  This is the single most likely thing and it is exhaustible in minutes.
- glibc `rand()` over the **full 32-bit** seed space: 4.3·10⁹ with early-abort on the first
  ~40 runes (hours on a multicore box, minutes on GPU).
- Python 2.7 / 3.x `random.seed(int)` (MT19937) — same ranges; plus `random.seed(str)` over a
  curated wordlist (3301, CICADA, DIVINITY, INSTAR, CIRCUMFERENCE, PILGRIM, WELCOME, the
  7A35090F fingerprint, each onion address, the 2012 P.S. semiprime and its factors).
- Java `Random` (48-bit LCG) seeded from `currentTimeMillis()` over a targeted publication window.
- PHP `mt_rand`, .NET `Random` (Knuth subtractive), `os.urandom` (unattackable — declare it,
  don't chase it).
- Combiner variants per generator: add / subtract, with and without the rejection-resample
  loop, with and without the ᚠ interrupter consuming a draw. ~6 variants × 6 generators.

**Outcome either way is publishable.** A hit is the solve. A null is the first *quantitative*
statement that the key is not machine-generated from a small seed — which is the only evidence
that would make "true one-time pad" more than an inference from the absence of structure.

**Estimated effort:** one careful C/CUDA kernel + a scoring threshold with a stated
false-positive budget. Days, not weeks.

---

## 2. The geometry plane of the page images — never examined

**The gap.** `analysis/stego/STEGO-VERDICT.md` swept *file-level* channels: appended bytes,
EXIF/COM/XMP, carve, spatial LSB, DQT tables, OutGuess DCT. All empty. But the verdict's own
provenance finding is that these are **400-DPI Ghostscript/Artifex renders of a PDF** — i.e. a
*typeset document*. The canonical stego channel for a typeset document is not the file bytes,
it is the **geometry**: glyph advance, baseline offset, glyph-shape substitution, line
justification. That plane was never touched. The vision armada tried to *read* the glyphs; it
never *compared* them.

Concrete tests, all offline against hash-verified authentic images (56/56 SHA1 match):

1. **Per-glyph template residual.** In a font render, every instance of a given rune must be
   pixel-identical modulo sub-pixel phase and JPEG noise. Cluster all ~13k glyph crops by rune
   and rank by distance from the class mean. *Any* real outlier — a rotation, a mirror, a
   modified stroke, a different font — is by construction deliberate. Decisive in one pass.
2. **Inter-glyph advance histogram.** Measure x-gaps between consecutive glyph bounding boxes.
   A unimodal distribution kills it; bimodality is a ~13,000-bit channel.
3. **Baseline y-jitter**, per-glyph, same test.
4. **Line geometry**: runes-per-line, right-margin ragging, leading. In a justified typeset
   book these are determined by the plaintext; deviations are marks.
5. **The ornaments.** `stones/pipeline.py`'s own docstring says the segmenter *drops* "ornament
   components far from the dominant text column." So there **are** non-rune graphical
   components on these pages, and every pipeline in the repo threw them away. Nobody has ever
   analysed the illustrations as data.

**Plus: a documented open door that is now unblocked.** STEGO-VERDICT §"the one thing not 100%
closed" says the avenue is *"closed pending the Linux control run"* because the box had "no
WSL/Docker/compiler." That is no longer true — this machine runs WSL2 Ubuntu with `gcc`/`make`
today. The two decisive experiments the verdict itself specifies (OutGuess 0.2 on a blank
400-DPI Ghostscript control to prove the 1417-byte shared prefix is an artifact, and `-k`
re-extraction of pages 0/4/26 with the seven candidate passphrases) can be run this week.
An avenue was left ajar on a constraint that has since evaporated.

---

## 3. The cleartext channel: word lengths are transmitted in the clear

**The gap.** Word (`-`), clause (`.`), line (`/`) and page (`%`) boundaries are *not*
enciphered. Therefore **word length is a plaintext invariant under any per-rune
substitution or additive stream, including a one-time pad.** The information-theoretic wall
applies to rune *values*. It does not apply to this channel at all. The repo's dead-end log
covers key texts exhaustively and plaintext-identification not at all.

**I ran a fast version of this while reviewing** (~10 minutes, single run, uncorrected —
treat as directional, not decisive):

```
LP2 cipher       n=3367 mean=3.901   1:.096  2:.189  3:.237  4:.168  5:.106 ...
LP2 minus-ᚠ      n=3360 mean=3.771   1:.108  2:.201  3:.236  4:.165  5:.105 ...
solved LP1 (English → futhorc) n=217 mean=4.005
Pride & Prejudice (→ futhorc)  n=20000 mean=4.131

KS(LP2, solved-LP1-English) = 0.050   (crit@.05 = 0.095)  → indistinguishable
KS(LP2, English prose)      = 0.054   (crit@.05 = 0.025)  → close, deviates at length 1

clause-FIRST mean 3.859 | clause-LAST mean 4.197 | INTERIOR mean 3.882
last-vs-interior  +0.315 runes, permutation p = 0.039
first-vs-interior −0.023 runes, p = 0.89
```

Two things fall out. **(a)** LP2's word-length profile is statistically indistinguishable from
the known-English solved pages rendered into futhorc — a random filler at matched boundary
density would not do that. **(b)** Clause-final words are measurably longer than clause-interior
words, which is a natural-language positional signature (content words cluster at clause ends);
a pad or a filler has zero length-vs-position structure. Neither result breaks anything, but
together they are *positive evidence that real English prose sits behind LP2* — which is worth
knowing before anyone concludes the pages are noise. The one anomaly is a **2× excess of
one-rune words** (9.6% vs 4.2% in English); that is ~180 words and is itself an unexplained lead.

**The strong version, which nobody has run:**

- **Word-length fingerprint search.** Take the 3,367-length sequence plus its clause/line
  skeleton and search a large corpus (Gutenberg, Blake, the Mabinogion, hermetic/gnostic
  texts, Cicada's own solved output) for a matching length signature, under an insertion model
  for the 458 interrupters and the futhorc multigraph compression. Alignment by seeded n-gram
  of length patterns + edit distance. **A hit identifies the plaintext, and the plaintext hands
  you the key** — bypassing the information-theoretic wall entirely rather than assaulting it.
- Same trick on **line-fill patterns** (a justified book's line breaks are a function of the
  plaintext's word lengths and the measure) and **per-page word counts**.
- Chase the 1-rune-word excess: which runes are they, are they ᚠ, are they positional?

Note this also reopens the R5 ROSETTA question *without* violating its kill rationale. ROSETTA
died because "non-English plaintext would raise IoC regardless of scorer" — correct, and it is
a statement about **rune values**. The word-length channel is a different object and gives an
independent, key-free read on what language the plaintext is.

---

## 4. There is unaudited work in this repo, and a live lead abandoned inside it

`DEAD_ENDS.md` flags Campaign XVIII as an unlogged null surviving only as orphaned bytecode.
That problem is **substantially bigger than the ledger knows.** Present as `.pyc`-only, source
deleted, never committed to git, absent from `LEDGER.md`, `DEAD_ENDS.md` and the dossier:

| Location | What it was | Result |
|---|---|---|
| `analysis/recon/i6_wordlen/` | 4 generations: `wordlen_typology`, `v2`, `v3_mc`, `v4_lang` — cross-language KS discrimination + clause-edge positional structure (§3 above, done properly) | **lost** — wrote `RESULTS_v4.txt`, deleted |
| `analysis/stones/` | full LP2 glyph segmentation → line alignment → labeled crops → trained classifier (`dataset.npz`, `oof_pred.npy`, `doublet_positions`) | **lost** |
| `analysis/independent-read/` | `cluster_read`, `family_probe`, `crypto_exposure`, `oae_deepdive` | **lost** |
| `analysis/stylometry/` | 5 modules: corpus build, calibration/power, rejection, `cicada_rank`, forensic profile | **lost** (`forensic.json` gone) |
| `analysis/stones/altrep/scan` | Latin multigraph expansion, 7 page-ordering variants, count-sequences vs primes/totient | **lost** |
| `analysis/latin/latin_redteam`, `analysis/bookcipher/` | as named | **lost** |

Two consequences. First, part of the "everything is closed" claim rests on runs nobody can
audit or reproduce — the same integrity problem the ledger already called out once. Second,
and more usefully:

### The O/A/AE adjudication was started and never finished

`independent-read/oae_deepdive.py`'s own docstring: unsupervised 3-way sub-clustering of the
ᚩ / ᚪ / ᚫ glyphs *"agrees with canon ~80%. The ~20% that land with a sibling are the only
glyphs in the whole book where a visual read might disagree with canon."* It isolated and
rendered every one of them for human adjudication (`oae_mismatch.png`, `oae_mismatch.json`,
and two `MY_adjudication*.png` files exist on disk). **No verdict was ever recorded anywhere.**

That matters more than it looks. `DEAD_ENDS.md` Round 1 says H1 may be revived only "if the
canonical transcription's interrupter identification is itself overturned," and the program
status says the only remaining rational inputs are "a key, a seed text, **or a transcription
discrepancy**." This is a half-finished hunt for exactly that third thing, sitting unclosed.

Honest counterweight: ~20% disagreement between an unsupervised clusterer and ground truth on
three visually similar glyphs is roughly what you'd expect from the clusterer, and the 3-way
lineage diff (13,136/13,136 identical) is strong evidence against real errors. But it is cheap
to finish: high-zoom crops of the ~20%, per-instance template distance against class means,
adjudication, then re-measure the doublet/IoC fingerprint under any confirmed flips. Either it
produces the discrepancy the program says it needs, or it retires the last transcription doubt
with an actual recorded verdict instead of a deleted script.

---

## 5. Hunt the source PDF and the font — a new external target

The AN-END hunt closed a *hashed web page*. It never looked for the **document**. The images
are 400-DPI Artifex/Ghostscript renders, which means a **PDF existed upstream** and was
rendered to JPEG for release. A surviving original PDF would carry text objects, glyph order,
and an embedded font — a direct structural leak, and a completely different search than the
one Round 7 closed.

- Fingerprint the render: DQT tables + the 2576-byte "Artifex Software 2011" ICC + page
  geometry pin the exact Ghostscript version and build → dates and platform-constrains the
  toolchain.
- Search for circulating "Liber Primus PDF" copies that are **originals** rather than
  image re-wraps (most community PDFs are the latter — check for a text layer, not a page count).
- Re-read the archived onion7 directory listing (`analysis/structure/origsearch/onion7_index.html`
  is already on disk) for non-`.jpg` assets nobody fetched.
- **Identify the rune font** from glyph outlines against stock Unicode runic faces (Junicode,
  Noto Runic, FreeSerif, Caslon Antique…). If it is stock, the author typed Unicode runes in a
  normal editor — which means the enciphering was done by a *script*, which independently
  strengthens §1. If it is custom, the font file itself becomes an artifact to hunt.

---

## 6. Short shots — one agent each, an afternoon apiece

- **The 86 residual doublets as an index list.** R5 tested them for digraph parity, doubled-rune
  identity and gap distribution — i.e. as *structure*. Nobody tested them as *pointers*:
  positions and gaps read as page/line/word indices into the solved LP1 English, or into the
  book itself. Book-cipher shaped, cheap, and the repo already has `analysis/bookcipher/`.
- **Non-language payload scan.** Every "no language" verdict used IoC or quadgrams. Both are
  blind to a *compressed or binary* plaintext — gzip output has flat IoC by construction, which
  is precisely the observed profile. Take the parameter-free decodes already in
  `CRYPTO-RIGOR §C` (rank-in-28, first-difference, collision-unbump), pack to bytes across all
  bit orders / offsets / directions, and scan for magic headers (gzip, zlib, PGP packet framing,
  PNG/JPEG, ASN.1 DER, base64 armor) and byte-histogram structure. An hour of work that closes a
  real hole in the evidence for "OTP-class": right now "flat IoC" is being read as "encrypted"
  when it is equally consistent with "already decoded, but not prose."
- **Ornament inventory.** Extract and catalogue every non-rune graphical component the
  segmenter discarded (§2.5). Nobody has even listed them.

---

## Suggested armada shape

Five parallel tracks, no shared state, each with a pre-registered kill condition:

1. **SEED** — the PRNG sweep (§1). Highest expected value; also the highest-value *negative*.
2. **GEOMETRY** — glyph template residuals, advances, baselines, ornaments (§2), plus the now-runnable
   WSL OutGuess control.
3. **SKELETON** — word-length fingerprint search against a large corpus (§3).
4. **ADJUDICATE** — finish the O/A/AE triad and record a verdict; re-run and *commit* the lost
   wordlen/stylometry campaigns (§4).
5. **PROVENANCE** — source PDF + font identification (§5).

Rule for all five, borrowed from the existing ledger and worth keeping: pre-register the
statistic and the kill condition before running, and commit the source **and** the results this
time. The reason §4 exists is that this discipline was applied to the ledger rounds and not to
the campaigns run alongside them.

---

## The one honest framing note

`PICKUP-HERE.md` and `DEAD_ENDS.md` both say the ciphertext-only program is complete and that
only external inputs remain. For **rune-value cryptanalysis** that is true and well-evidenced.
But three of the five tracks above are neither ciphertext-only attacks nor external inputs —
they are *unexamined dimensions of artifacts already in hand*: the geometry of the page images,
the cleartext structural skeleton, and the entropy (as opposed to the structure) of the
keystream. The program declared itself complete along one axis and then generalised the claim
to all axes. That generalisation is the thing worth revisiting.
