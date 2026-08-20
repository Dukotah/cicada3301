# Lane F — REPORT (press and academic)

Branch `corpus-sweep`. Working dir `corpus/F-press-academic/`.
Lane resumed and closed 2026-08-19/20 UTC after a network outage killed it mid-download.

**Deliverables:** `MANIFEST.json`, `BIBLIOGRAPHY.md` (+ generated `BIBLIOGRAPHY-GENERATED.md`),
`GAPS-F.md`, `CONFLICTS-F.md`, this file.

---

## 1. The asymmetry this lane exists to fix

Corpus `GAPS.md` **G-08**: the repository held **~110 MB of journalism about the puzzle and
zero academic literature on the cipher families it uses.**

| half | before | after |
|---|---|---|
| press | 134 files, ~110 MB, provenance asserted at collection level only | 134 files, provenance **verified** to an upstream commit and **re-derived per file** for 88 of them |
| cipher-space | **0** | **40 items**, all open access, each with source URL + SHA-256 + retrieval UTC |

`BIBLIOGRAPHY.md` keeps the two halves apart deliberately. The press half is context about
what was said and when. **The cipher-space half is the only part that can change a result.**

---

## 2. Which papers bear directly on this project's open questions, and what each
would change if applied

This is a reading plan derived from abstracts and stated methods. **No held paper has yet
been read and applied to this project's data** (`GAPS-F.md` F-G-10); nothing below should be
cited as a result.

### 2.1 The derived-vs-true-pad question — the one that decides whether to keep going

The unsolved Liber Primus pages behave as a running key over a near-random keytext. Whether
that key is a **true one-time pad** (unbreakable; stop) or a **derived keystream**
(breakable; continue) is the load-bearing question in this repository, and it is currently
argued informally.

**Most relevant, in order:**

1. **Ryabko (2013), *The Vernam cipher is robust to small deviations from randomness***
   (arXiv:1303.2219, held).
   *What it would change:* it converts the question from binary to quantitative. Ryabko
   bounds how far a keystream may deviate from uniform before Vernam secrecy measurably
   degrades, expressed through the keystream's **entropy deficit**. Applied here, it turns
   "is this a real pad?" into "what entropy deficit would the observed statistics imply, and
   is that deficit large enough to be exploitable over the length of ciphertext we hold?" —
   a question with a number for an answer. It also formalises the uncomfortable middle case
   this project keeps running into: a *derived* keystream can still be effectively a pad up
   to N symbols, so a failed attack over a short page proves much less than it feels like it
   does.

2. **NIST SP 800-22r1a (2010)** and **NIST SP 800-90B (2018)** (both held).
   *What they would change:* SP 800-90B supplies the **min-entropy estimators for non-IID
   sources** — the operational instrument for putting a lower bound on a candidate
   keystream's entropy. SP 800-22 matters for its **negative** result, and this is the part
   that should be written into the repository's method notes: **passing SP 800-22 does not
   distinguish a derived keystream from a true pad.** A statistical randomness battery is
   the wrong instrument for this question, and running one and passing it would be a
   false closure.

3. **Beighton (2022), *Security analysis of shift-register based keystream generators***
   (QUT PhD thesis, held).
   *What it would change:* it is the mirror image of the question — how structure in a
   *generated* keystream is actually detected. If the LP keystream is derived, it was
   derived by *something*, and this thesis is a catalogue of what the detectable signatures
   of generator structure look like and what sample sizes are needed to see them.

4. **Ryabko (2016), *Information-Theoretical Analysis of Two Shannon's Ciphers***
   (arXiv:1605.00214, held) — the information-theoretic frame that the Vernam-robustness
   result sits inside.

5. **HistoCrypt 2022, *Unicity Distance of the Zodiac-340 Cipher*** and
   **(2024), *Revisiting the Unicity Distance***, both held.
   *What they would change:* unicity distance answers *how much ciphertext must be right
   before a decryption is uniquely determined rather than one candidate among many.* This
   repository reports candidate decryptions without ever stating that threshold. Computing
   it for the LP alphabet and page lengths would tell you whether any single page is even
   long enough to admit a unique solution — which, if the answer is no, reframes every
   per-page negative result in the repository.

### 2.2 Running-key attacks — the method that would actually be run

- **Reddy & Knight (2012), *Decoding Running Key Ciphers*** (ACL, held). The canonical
  attack: Bayesian/HMM decoding with an n-gram LM over **both** plaintext and keytext
  simultaneously. *What it would change:* this repository's sweeps model the plaintext and
  treat the key as unknown noise. Reddy & Knight model both jointly, which is strictly more
  powerful when the keytext is natural language. If the LP keytext is a book or a
  natural-language string, this is the attack — and it has not been run here.
- **HistoCrypt 2020, *Project Gutenberg and Hexagram Statistics*** (held, DOI
  10.3384/ecp2020171005). Effectively the same design as this repository's SKELETON lane.
  *What it would change:* read it for **how they controlled false positives across a large
  keytext corpus** — the exact failure mode of a Gutenberg-wide sweep.
- **PAYWALLED, unretrieved:** Bauer & Tate (2002), Bauer & Gottloeb (2005), Griffing (2006)
  in *Cryptologia* — the statistical and Viterbi attacks on running keys. Citations and DOIs
  in `GAPS-F.md` F-G-01.

### 2.3 The doublet deficit — this repository's one live statistical lead

The unsolved pages suppress adjacent repeated runes far below chance. That is a **Smirnov
word** (no two equal adjacent letters), and the combinatorics literature gives the exact
null model that the repository currently approximates.

- **(2015), *Application of Smirnov Words to Waiting Time Distributions of Runs***
  (arXiv:1503.08096, held). *What it would change:* supplies the **exact** waiting-time and
  run-length distributions for a no-adjacent-repeat constraint. The observed doublet
  suppression can then be scored against a correct null instead of a simulated or
  hand-derived one.
- **(2018), *Enumerative properties of restricted words and compositions***
  (arXiv:1811.10461, held). *What it would change:* generating functions that give the
  **exact expected doublet count for a 29-symbol alphabet** — a closed-form number to
  compare the observation against.

Together these decide whether the doublet deficit is a real constraint imposed by the
cipher (and therefore a lever) or an artifact of alphabet size and text length.

### 2.4 Keyspace sweeps — the statistical error the repository is currently making

Every keyspace sweep here reports a **best-of-N** score with no family-wise error control.
That is textbook multiple testing, and the best score out of a large N is expected to look
good even under a pure null.

- **Schwartzman et al. (2012), *Multiple testing of local maxima for detection of peaks in
  1D*** (arXiv:1203.3063, held) and **(2010), *Peak Detection as Multiple Testing***
  (arXiv:1008.1924, held). *What they would change:* they turn a raw best-of-N maximum into
  a **calibrated p-value with FWER/FDR control**. Applied retroactively, they would tell you
  which of this repository's past "promising peaks" survive correction — and my expectation
  is that some will not. This is the single most likely paper-driven change to an existing
  conclusion in this repository.

### 2.5 Separating "the search failed" from "the scoring model is blind"

- **Corlett & Penn (2008), *Attacking Decipherment Problems Optimally with Low-Order N-gram
  Models*** (EMNLP, held). *What it would change:* it gives **exact/optimal** decipherment
  under low-order n-gram models. Every negative result in this repository is currently
  ambiguous between "the search did not find the key" and "the quadgram model cannot see the
  answer even if handed it." An optimal-decoding baseline separates the two. That
  distinction is not currently makeable anywhere in this repo, and it is the difference
  between a closed avenue and an untested one.
- **Nuhn, Schamper & Ney (2013)**, **Ravi & Knight (2011)**, **Hauer et al. (2014)** (all
  held) — beam-width/LM-order success curves, a proper Bayesian prior/likelihood
  decomposition instead of a bare quadgram sum, and combined character+word models for an
  alphabet where word boundaries are unreliable.
- **HistoCrypt 2023, *Historical Language Models in Cryptanalysis*** (held). *What it would
  change:* quantifies how LM period/register/language mismatch shifts cryptanalytic scores —
  which bears directly on applying modern English quadgram models to the Liber Primus's
  deliberately archaic register.

### 2.6 Diagnosing without solving

- **HistoCrypt 2021, *Cryptodiagnosis of "Kryptos K4"*** (held). **The closest published
  analogue to the Liber Primus situation**: a methodology for saying substantive things
  about a short unsolved ciphertext *without solving it*. If one paper in this collection
  should be read first as a template for how to write up an unsolved cipher, it is this one.
- **HistoCrypt 2021, *Massive ML Classical Cipher Type Detection*** (held). *What it would
  change:* an **independent instrument** — a classifier over 50+ classical cipher types that
  can be run on LP ciphertext without any assumption from this repository's own priors.

### 2.7 Runic precedent, and the signal-vs-noise question in a runic setting

- **Wase, *The Upplandic Non-Lexical Rune Stones: Ciphers or Nonsense?*** (HistoCrypt,
  DOI 10.3384/ecp183168, held). **The only paper found that poses the Liber Primus epistemic
  problem in a genuinely runic setting.** *What it would change:* it supplies the vocabulary
  and the method for arguing about runic sequences that may be cipher or may be meaningless —
  which is the argument this project is actually having.
- **HistoCrypt 2023, *Runic cryptography in early epigraphic period (200–700)*** (held) —
  whether the LP runic layer has historical cryptographic precedent at all.

### 2.8 Transcription as a confound

- **Magnifico et al., *Lost in Transcription of Graphic Signs in Ciphers*** (HistoCrypt,
  DOI 10.3384/ecp188403, held). *What it would change:* corpus `GAPS.md` **G-03** flags that
  this repository's transcription has a **single root lineage** — every downstream analysis
  inherits whatever errors that root contains. This paper measures how transcription error
  propagates into cryptanalytic results, and would let the repository put a bound on how
  much of its negative-result space could be transcription noise.

---

## 3. The press half: provenance turned from asserted into verified

Two results, both new.

**Collection level — verified.** The 134-file archive at
`liber-primus/analysis/attribution/papers-archive/` is a mirror of
`github.com/krisyotam/cicada3301` `papers/`. That was previously an assertion. It is now
checked: **133 of 134 files are byte-identical (git blob SHA-1 match) to that repository at
commit `1ccf9583b706` (2026-04-20T08:01:14Z).** One file, `marcus-wanners-net-wayback.txt`,
is local-only and has no upstream provenance (`CONFLICTS-F.md` F-C-04).

**Per file — re-derived, and it dates a previously undated archive.** 126 of the files are
browser print-to-PDF captures whose running header/footer preserves the original article URL
and the capture date. Extracted with `pdftotext -layout` (`press_reprov.py` →
`meta/press_provenance.json`): **88 PDFs yield both**, 102 yield a URL, 103 yield a date.
**87 of the 88 dates are `dd.mm.yyyy`** — a German-locale browser — and they cluster in
**2021-01 (19), 2021-02 (51), 2021-03 (17)**.

So the press archive is a single January–March 2021 capture session by a German-locale
browser. That is worth knowing for a reason beyond tidiness: **it fixes the archive's
horizon.** It cannot contain anything published after March 2021, and it cannot contain
anything that had already link-rotted before January 2021. Absence from this archive is
therefore not evidence of absence, at either end.

This is also the standard the rest of the corpus should be held to and mostly is not —
compare `GAPS-C.md` C-G-12, where the Discord export was pulled from a branch tip with no
commit pin and consequently cannot be verified at all.

---

## 4. What is still missing

Detail in `GAPS-F.md`. The load-bearing items:

- **Autokey cryptanalysis: zero open-access papers held.** The three Cryptologia papers are
  paywalled (F-G-03). This is the largest subject-matter hole left.
- **Book ciphers: nothing held.** **Totient-indexed shifts: nothing held** — and that may be
  the true state of the literature rather than a search failure, but it should be
  established deliberately.
- **The three canonical Cryptologia running-key papers** (Bauer & Tate 2002, Bauer &
  Gottloeb 2005, Griffing 2006) — citations and DOIs recorded, unretrieved, no paywall
  bypassed, no abstract invented. Crossref holds no abstracts for these DOIs, so `GAPS-F.md`
  says so rather than paraphrasing.
- **8 SJSU + 1 RIT theses failed on a mechanical fetch problem**, not a paywall — the Digital
  Commons `viewcontent.cgi` endpoint needs a landing-page referer. All are open access and
  all nine are recoverable in one pass (F-G-04).
- **IACR ePrint: searched, nothing downloaded.** Fully open access; pure unfinished work.
- **The press-half extension never ran** — no documentaries, podcasts, interviews, or
  7A35090F signature-status material (F-G-08).

---

## 5. Next steps in this lane, in order

1. **Read Ryabko (2013) and compute the entropy-deficit bound for the LP keystream.** It is
   the shortest path from "we argue about whether it's a real pad" to a number.
2. **Apply Schwartzman's FWER correction retroactively to the repository's existing keyspace
   sweeps.** This is the most likely paper-driven change to an existing conclusion, and it
   only needs already-recorded score distributions.
3. **Compute unicity distance for the LP alphabet and page lengths.** If a page is shorter
   than its unicity distance, every per-page negative in this repository needs restating.
4. **Score the doublet deficit against the exact Smirnov null** rather than an approximation.
5. **Fix the SJSU fetch** (landing page + referer) and recover the nine theses in one pass.
6. **Run the HistoCrypt 2021 cipher-type classifier on LP ciphertext** as an independent
   instrument that carries none of this repository's priors.
