# Lane F — BIBLIOGRAPHY

**This bibliography has two halves and they are deliberately kept apart.**

| half | what it is | how much this repo has |
|---|---|---|
| **PRESS** | journalism, documentaries, interviews, forum captures, witness profiles — writing *about* the puzzle | ~110 MB, 134 files, mirrored |
| **CIPHER-SPACE** | peer-reviewed and preprint literature on the cipher families the puzzle actually uses | **zero before this lane; 40 items now** |

Corpus `GAPS.md` **G-08** is exactly this asymmetry: the repository held a large press
archive and nothing at all on runic Vigenère variants, totient-indexed shifts, autokey and
running-key cryptanalysis, book ciphers, interrupter/null schemes, one-time-pad
indistinguishability, extreme-value statistics for keyspace search, or anti-repeat
constrained sequences. **The press half is context. The cipher-space half is the part that
can change a result.** Do not let the two be cited as one body of "sources".

Full machine-generated entries — every citation, DOI, source URL, SHA-256, byte count and
retrieval timestamp — are in **[`BIBLIOGRAPHY-GENERATED.md`](BIBLIOGRAPHY-GENERATED.md)**,
produced by `mkbib.py` directly from `meta/downloads.json` and `meta/press_provenance.json`
so that **no citation in this lane is hand-transcribed**. Paywalled items that could not be
retrieved are listed with citation + DOI + abstract in [`GAPS-F.md`](GAPS-F.md); none was
bypassed, and none was invented.

---

# HALF 1 — CIPHER-SPACE (the real gap, G-08)

**40 items held**, every one open access, each with source URL + SHA-256 + retrieval UTC.
Organised below by the open question in this project that the material bears on. The
per-item "Relevance" lines in `BIBLIOGRAPHY-GENERATED.md` say what each would change.

## 1.1 One-time-pad indistinguishability — true pad vs derived keystream

The single most consequential open question in this repository: the unsolved Liber Primus
pages behave like a running key that is near-random, and the whole project turns on whether
that key is a **true one-time pad** (unbreakable, and the work should stop) or a
**derived keystream** (breakable, and the work should continue).

- **Ryabko (2013), *The Vernam cipher is robust to small deviations from randomness***,
  arXiv:1303.2219 — **the most on-point paper found.** Quantifies how far a keystream may
  deviate from uniform before Vernam secrecy degrades, in terms of the keystream's entropy
  deficit.
- **Beighton (2022), *Security analysis of shift-register based keystream generators***,
  QUT PhD thesis — the mirror image of the question: how structure in a *generated*
  keystream is detected.
- **Ryabko (2016), *Information-Theoretical Analysis of Two Shannon's Ciphers***,
  arXiv:1605.00214 — information-theoretic treatment of the running-key/Vernam family.
- **NIST SP 800-22r1a** (Rukhin et al., 2010) and **NIST SP 800-90B** (Turan et al., 2018)
  — the standard randomness battery and the min-entropy estimators for non-IID sources.
  **Read SP 800-22 for its negative result:** passing it does *not* distinguish a derived
  keystream from a true pad.

## 1.2 Running-key and autokey cryptanalysis

- **Reddy & Knight (2012), *Decoding Running Key Ciphers***, ACL 2012 — the canonical NLP
  attack: Bayesian/HMM decoding with an n-gram LM over **both** plaintext and keytext.
- **HistoCrypt 2020, *The Use of Project Gutenberg and Hexagram Statistics to Help Solve
  Famous Unsolved Ciphers***, DOI 10.3384/ecp2020171005 — Gutenberg as keytext corpus plus
  6-gram statistics. This is precisely the SKELETON lane's method; read it for **how they
  controlled false positives over a large corpus**.

## 1.3 Unicity distance — how much ciphertext before a solution is unique

- **HistoCrypt 2022, *Unicity Distance of the Zodiac-340 Cipher*** — computed for a real
  unsolved-then-solved cipher; the method transfers directly.
- **(2024), *Revisiting the Unicity Distance through a Channel Transmission Perspective***,
  arXiv:2410.14816.
- **(2005), *On the Unicity Distance of Stego Key***, arXiv:cs/0504083.

## 1.4 Anti-repeat constrained sequences — the doublet deficit

The repository's one live statistical lead is that the unsolved pages suppress adjacent
repeated runes far below chance. That is a **Smirnov word** (no two equal adjacent letters),
and the combinatorics literature gives the exact null model.

- **(2015), *Application of Smirnov Words to Waiting Time Distributions of Runs***,
  arXiv:1503.08096 — **directly on the LP2 anti-repeat filter.** Waiting-time and
  run-length distributions, i.e. the null against which the observed doublet suppression
  must be scored.
- **(2018), *Enumerative properties of restricted words and compositions***,
  arXiv:1811.10461 — survey-grade generating functions for exact expected doublet counts on
  a 29-symbol alphabet.
- **(2019), *On enumerators of Smirnov words by descents and cyclic descents***,
  arXiv:1901.01591; **(2023), *Smirnov words and the Delta Conjectures***, arXiv:2312.03956;
  **(2001), *Average number of distinct part sizes in a random Carlitz composition***,
  arXiv:math/0110178.

## 1.5 Extreme-value statistics and multiple testing over keyspace sweeps

Every keyspace sweep in this repository reports a **best-of-N** score with no family-wise
error control. That is the classic multiple-testing failure mode.

- **Schwartzman et al. (2012), *Multiple testing of local maxima for detection of peaks in
  1D***, arXiv:1203.3063 — **directly applicable.** Turns "is this score peak real?" into a
  multiple-testing problem over local maxima with FWER/FDR control.
- **(2010), *Peak Detection as Multiple Testing***, arXiv:1008.1924 — the companion
  framework for converting a raw best-of-N maximum into a calibrated p-value.
- **(2026), *Optimal multiple testing under family-wise error control***, arXiv:2604.10986.

## 1.6 Runic cryptography

- **HistoCrypt 2023, *Runic cryptography in early epigraphic period (200–700)*** — whether
  the Liber Primus runic layer has historical cryptographic precedent.
- **Wase, *The Upplandic Non-Lexical Rune Stones: Ciphers or Nonsense?***, HistoCrypt,
  DOI 10.3384/ecp183168 — **the only paper found that poses the Liber Primus epistemic
  problem in a genuinely runic setting**: runic sequences that may be cipher or may be
  meaningless.

## 1.7 Language-model scoring and search for classical ciphers

- **Corlett & Penn (2008), *Attacking Decipherment Problems Optimally with Low-Order N-gram
  Models***, EMNLP — **an important negative-control result.** Exact/optimal decipherment
  under low-order n-gram models, which lets you separate *"the search failed"* from *"the
  scoring model cannot see the answer."* This repository's negatives currently cannot make
  that separation.
- **Nuhn, Schamper & Ney (2013), *Beam Search for Solving Substitution Ciphers***, ACL —
  the empirical relationship between LM order, beam width and success rate.
- **Ravi & Knight (2011), *Bayesian Inference for Zodiac and Other Homophonic Ciphers***,
  ACL — the prior/likelihood decomposition a principled scoring model needs, instead of a
  bare quadgram sum.
- **Hauer et al. (2014), *Solving Substitution Ciphers with Combined Language Models***,
  COLING; **HistoCrypt 2021, *Dorabella Cipher with Statistical Language Models***
  (DOI 10.3384/ecp183159) — how LM scores behave when the ciphertext is too short to be
  decisive; **HistoCrypt 2023, *Historical Language Models in Cryptanalysis***
  (DOI 10.3384/ecp195701) — how LM period/register/language mismatch changes scoring, which
  bears on applying modern quadgram models to LP's archaic register.

## 1.8 Search-based cryptanalysis — what a failed search proves

- **Clark (2002), *Metaheuristic Search as a Cryptological Tool***, University of York PhD
  thesis — book-length, including **how to choose a cost function and what a failed search
  does and does not prove.**
- **(2007), *Cryptanalysis Using Nature-Inspired Optimization Algorithms***, University of
  Calgary.

## 1.9 Nulls, interrupters and cipher+steganography combinations

- **Szarka, *On the Combination of Cryptography and Steganography in 17th Century
  Germany***, HistoCrypt, DOI 10.3384/ecp195705 — historical null/dummy-symbol schemes.

## 1.10 Diagnosing an unsolved cipher without solving it

- **HistoCrypt 2021, *Cryptodiagnosis of "Kryptos K4"*** — **the closest published analogue
  to the Liber Primus situation**: methodology for diagnosing a short unsolved ciphertext
  without solving it.
- **HistoCrypt 2021, *A Massive Machine-Learning Approach For Classical Cipher Type
  Detection*** — a classifier over 50+ classical cipher types, runnable on LP ciphertext as
  an independent instrument.
- **HistoCrypt 2023, *International Conference on the Voynich Manuscript 2022***,
  DOI 10.3384/ecp195700.

## 1.11 Transcription error as a confound

- **Magnifico et al., *Lost in Transcription of Graphic Signs in Ciphers***, HistoCrypt,
  DOI 10.3384/ecp188403 — bears directly on corpus `GAPS.md` **G-03** (single-root
  transcription lineage).
- **Chen et al., *Unsupervised Alphabet Matching in Historical Encrypted Manuscript
  Images***, HistoCrypt, DOI 10.3384/ecp183154 — automated glyph reading, relevant to the
  parked per-rune re-transcription.

## 1.12 Corpora, tooling, and ML on classical ciphers

- **Héder & Megyesi, *The DECODE Database of Historical Ciphers and Keys: Version 2***,
  HistoCrypt, DOI 10.3384/ecp188397 — a corpus of historical ciphers **and keys**; a source
  of real key material and of cipher-type priors.
- **HistoCrypt 2022, *New Ciphers and Cryptanalysis Components in CrypTool 2*** — inventory
  of implemented instruments this repo does not vendor (cf. `GAPS.md` G-04).
- **HistoCrypt 2022, *Deep Learning Known-Plaintext Attacks on Columnar Transposition***;
  **Greydanus (2017), *Learning the Enigma with RNNs***, arXiv:1708.07576;
  **Antal, Zajac & Mírka, HistoCrypt, DOI 10.3384/ecp183152**;
  **HistoCrypt 2023, *Encrypted epigraphy — Santa Maria inscription***.

## Venue note

**HistoCrypt** (Linköping Electronic Conference Proceedings, `ep.liu.se`) is **fully open
access and is the venue of record for computational historical cryptology.** 17 of the 40
held items come from it. **Cryptologia** (Taylor & Francis) is the other principal venue and
is **paywalled** — its canonical running-key papers are listed in `GAPS-F.md` with citation
and DOI, unretrieved.

---

# HALF 2 — PRESS (context, not evidence about the cipher)

**134 files, ~110 MB**, at `liber-primus/analysis/attribution/papers-archive/`
(gitignored: copyrighted third-party PDFs, re-pullable).

## Collection-level provenance — VERIFIED, not asserted

The archive is a mirror of `github.com/krisyotam/cicada3301` `papers/`. This lane verified
that at the byte level: **133 of the 134 local files are byte-identical (git blob SHA-1
match) to that repository's `papers/` at commit `1ccf9583b706` (2026-04-20T08:01:14Z).**
One file is local-only: `marcus-wanners-net-wayback.txt`, added locally 2026-07-27.

This is the standard the rest of the corpus should meet, and mostly does not — compare
`GAPS-C.md` C-G-12, where the Discord export was pulled from a branch tip with no commit
pin and therefore has no verifiable provenance at all.

## Per-file provenance — RE-DERIVED in this lane

126 of the 134 files are PDFs, and they are **browser print-to-PDF captures whose running
header/footer preserves the original article URL and the capture date.** Extracted with
`pdftotext -layout` (`press_reprov.py` → `meta/press_provenance.json`):

- **88 PDFs yielded both a source URL and a capture date.**
- 24 yielded no source URL; 23 yielded no capture date.
- **87 of the 88 dates are in `dd.mm.yyyy` format** — a German-locale browser.
- The dates cluster tightly: **2021-01 (19), 2021-02 (51), 2021-03 (17)**, with one 2017-04
  outlier that is probably an in-article date rather than a footer capture date.

**This dates a previously undated archive.** The press half was captured in a
January–March 2021 session by a German-locale browser — which also tells you what it can
and cannot contain: nothing published after March 2021, and nothing that was already
link-rotted by then.

Source hosts represented: `en.wikipedia.org` (12), `old.reddit.com` (10),
`calypne.boards.net` (3), `telegraph.co.uk` (3), `thestar.com` (3), `reddit.com` (3),
`bbc.com` (2), and singletons including `rollingstone.com`, `theguardian.com`,
`cbsnews.com`, `mentalfloss.com`, `heise.de`, `theconversation.com`, `knowyourmeme.com`,
`bernsteinbear.com`, `thedrum.com`, `mirror.co.uk`, `guardianlv.com`,
`thedailybanter.com`.

Per-file rows — filename, capture date, source URL, SHA-256, byte count — are in
`BIBLIOGRAPHY-GENERATED.md`, including the 24 and 23 that yielded nothing.

## What the press half contains that matters

Per `PAPERS-ARCHIVE.md`, the substantive primary material inside it:

- `a2e7j6ic78h0j7eiejd0120 - #1..8.pdf` — captures of the 2012 onion pages (that v2 onion is
  dead; these are the surviving record).
- `Search results for '0x181f01e57a35090f'.pdf` and the `header 7A35090F` file — PGP key
  7A35090F forensics.
- `PGP Signed Message April 2017.pdf` — the "Beware false paths" message. **Lane D
  independently confirmed the paste of this message is byte-stable across Wayback captures**
  (`CONFLICTS-D.md` D-C-03b).
- The leaked 2013 PGP email threads — provenance of the individualised RSA distribution.
- Witness/profile material on Marcus Wanner, and hoax/impostor material *labelled as such*.

## Standing caution

The press half is journalism and community writing. It is a source about **what was said
and when**, not about the cipher. Several files are Wikipedia articles and Reddit threads;
they are captures of secondary and tertiary sources. Nothing in this half should be cited
as evidence about the Liber Primus cipher itself.
