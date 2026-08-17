# PA-2 — Internal prior-work census (Round 10B)

Every mass-agent run and campaign this repo has executed, what it concluded, and **how good the
instrument was**. Cite this file instead of re-running. Paths are relative to
`liber-primus/analysis/` unless prefixed.

Scale note (get this right before reading any number): **page-scale** scoring (`lp.score.score_norm`)
puts English at −4.0…−4.35 and random at ≈−7.5; **stream-scale** scoring (seed sweep, direction
sweep, doublet pointers) puts English at −11…−12 and random at ≈−16…−16.7. The two are not
comparable and several docs quote them side by side.

---

## 1. The run inventory

| # | Run | Date | Scale | Verdict | Artifacts |
|---|---|---|---|---|---|
| 1 | **Armada / completeness-critic + novel-attacks recon** | 2026-06-17 | reasoning-only (no compute) | Proposed A doublet-avoidant DP, B in-depth, C transposition-validity-check, E fractionation | `armada/completeness-critic.md`, `armada/recon-novel-attacks.md`, `armada/FINAL-VERDICT.md` |
| 2 | **Armada follow-up tests** | 2026-06-17 | page | Differencing/integral explained the deficit but yields flat-random `q`; page-on-page in-depth null | `armada/FOLLOWUP-TESTS.md` |
| 3 | **20-front Armada (36 agents, 2 waves, ~1.26M tok)** | 2026-06-20 | page | 20/20 `hit=false`, best −6.023; OutGuess 0.4 built from source + validated on known payloads; LP2 pages carry no stego | `ARMADA-20-FINDINGS.md`, `armada20/` (431 og_out blobs, hill/cribdrag/interrupter/forensics scripts) |
| 4 | **Campaign III — foundation** | — | page | Transcriptions all trace to rtkd/iddqd; esoterica running keys null (best −6.049) | `foundation/CAMPAIGN-III-FINDINGS.md` |
| 5 | **Campaign IV — structure** | — | — | Doublet deficit = uniform soft no-repeat rule; keystream continuous across page joins; English running keys ruled out *by mechanism* | `structure/CAMPAIGN-IV-FINDINGS.md` |
| 6 | **Campaign V — stones** | — | — | Glyph classifier 99.2%; multiplicative gematria excluded | `stones/CAMPAIGN-V-FINDINGS.md` |
| 7 | **Campaign VI — OSINT** | — | — | 2017 PGP carries no key; reopened pp49–51 | `osint/CAMPAIGN-VI-OSINT-FINDINGS.md` |
| 8 | **Campaigns VII / IX / XX — pp49–51** | — | page | 2048-bit high-entropy blob; not prime/RSA/key/text/format/image; 337,944 key configs null; 76,360 numeric configs null (best −6.491) | `pp49_51/` |
| 9 | **Campaign VIII / XIX — attribution** | — | — | No named author attributable; full winner/insider roster holds no key material | `attribution/` |
| 10 | **Campaign X — autokey** | — | — | All 4 autokey variants sit at 3.3–4.2% doublets → excluded | `CAMPAIGN-X-FINDINGS.md` |
| 11 | **Campaign XI — mechanism** | — | — | No-repeat filter is **soft, ~83% suppression**; alt-base-as-key null | `CAMPAIGN-XI-FINDINGS.md` |
| 12 | **Campaign XII — burn-down + 15 keytexts** | — | page | best −6.048, 0 hits | `CAMPAIGN-XII-FINDINGS.md`, `campaign12/` |
| 13 | **Campaign XIII — 13-agent armada, 82 keytexts / 10 lanes** | — | page | best −5.809, 0 hits; CT-log avenue closed; 2 AN-END onion theories debunked | `CAMPAIGN-XIII-FINDINGS.md`, `campaign13/` |
| 14 | **Campaign XIV — Fable 5 red-team + probes P1–P5** | — | mixed | 4 over-claims caught and closed by measurement; corpus-wide periodicity null; combiner/homophonic bigram matrix dead flat; ~75-page "gap" = solved pages | `CAMPAIGN-XIV-FINDINGS.md`, `campaign14/REDTEAM-PROPOSALS.md` |
| 15 | **Campaign XV — label-free transcription audit** | 2026-07-13 | — | Canon = the natural visual partition (ARI 0.745); only fragile locus is ᚩ/ᚪ/ᚫ (10.7%, crypto-inert) | `independent-read/FINDINGS.md` |
| 16 | **Campaign XVI — stylometry** | — | — | 359 words of authentic prose → attribution provably impossible | `stylometry/FINDINGS.md` |
| 17 | **Campaign XVII — assumption-stack red-team (8 fronts)** | — | page | All sealed incl. Latin plaintext and book cipher | `CAMPAIGN-XVII-FINDINGS.md`, `red_team.py`, `latin/`, `bookcipher/` |
| 18 | **Campaign XVIII — skip-tolerant decoder + coverage armada** | 2026-07-20…27 | page | Built + gate-validated a key-skip beam; re-ran every alignment-sensitive family: ~200 texts, 45 autokey primers, ~620 keywords, 874+ numeric streams — **0 hits**, global bests −5.75…−6.63 | `campaign18_skip/` (13 RUN-*.log all present), `armada2/COVERAGE-MATRIX.md`, `armada/ARMADA-RUN-QUEUE.md` |
| 19 | **OSINT external-artifact sweep** | 2026-07-27 | — | T1/T5 decode to already-known 2013/2016 messages; 60-key OutGuess sweep on **onion** images null; T2/T3 unidentified blobs | `OSINT-SWEEP-2026-07-27.md`, `armada_osint/` |
| 20 | **LP1/LP2 recon + 3 hypotheses** | 2026-07-28 | page | Key selection on solved pages is **SEMANTIC not numeric**; LP1-H no-repeat combiner null (best −6.88); LP2-H1 index null (−7.20); LP2-H2 red-join null | `recon/RECON-SUMMARY-2026-07-28.md`, `recon/lp1h_norepeat/`, `recon/lp2h_index/` |
| 21 | **Auditor-directed fan-out loop (26 agents, ~1.15M tok, ~75 min)** | 2026-07-28/29 | page | 3 frontiers declared exhausted; LP 4/100, Creator 8/100 | `AUDITOR-LOOP-2026-07-28.md` |
| 22 | **11-iteration rotating-critic loop (iters 2–11)** | 2026-07-29 | mixed | Non-cipher framings null; message-existence **undecidable**; autokey **positively refuted** (z=−17.25); inventory=29 confirmed; alphabet-ordering falsified; Smirnov rewrite retired; construction pinned to soft anti-repeat p_keep≈0.18 over memoryless base | `recon/i2_*`…`i11_*`, `FINAL-SYNTHESIS.md` |
| 23 | **Freshness sweep (5 web agents)** | 2026-07-29 | — | Nothing reopened; 3 deltas (SHA-1 forgery paper, Schoenberger litigation, hoaxes) | `FRESHNESS-2026-07-29.md` |
| 24 | **Rounds 1–7 (pre-registered loop)** | 2026-07-29…08-06 | mixed | R1 interrupter-artifact NEGATIVE; R2 fractionation NEGATIVE; R3/R7 Gate-#1 KILLs; R5 doublet anatomy NEGATIVE; R6 SIEVE-W + transition-lattice NEGATIVE | `../../research/LEDGER.md`, `DEAD_ENDS.md` |
| 25 | **Round 8 — 5 unexamined axes** | 2026-08-11 | stream/pixel | SEED 2.52e9 decodes 0 hits; GEOMETRY 3 channels dead; PAYLOAD 166 reps uniform; POINTERS inside null; SKELETON 51 texts / 8.2M words negative | `../../research/ROUND-8-RESULTS.md`, `seed_sweep/`, `geometry/`, `skeleton/` |
| 26 | **Round 9 — length / direction / template** | 2026-08-11 | stream/pixel | LENGTH anomaly **overturned as a large-n artifact**; DIRECTION 2,670 readings z=−0.40; TEMPLATE stage 1 = 1,067 exact bitmaps → 32 shape classes | `../../research/ROUND-9-RESULTS.md`, `direction/`, `retranscribe/` |
| 27 | **AN-END hunt** | 2026-08 | — | Unreachable by construction; 2,706 hash tests null; `gy3hoy2…onion` is a hallucination | `anend_hunt/FINDINGS.md` |

---

## 2. Instrument quality — the part that matters

### 2.1 Runs WITH a demonstrated positive control (trustworthy)

| Run | Positive control | Result of the plant |
|---|---|---|
| Campaign XVIII skip decoder | plant correct key with 6 skips | rigid **−7.24 / 8.5%** (missed) vs beam **−4.15 / 100%** (found). Also robustness across 4 texts × 2 offsets up to 14 skips → 99.6–100% match; pipeline recall **7/8** per page | `campaign18_skip/skipdecode.py`, `robustness.py`, `sweep_selftest.py` |
| ct-feedback coefficient sweep | plant `a1=7` autonomous feedback | recovered −4.13; unit-coeff decode misses at −7.51 | `campaign18_skip/ctfeedback_coeffs.py` |
| LP1-H no-repeat combiner | plant key + English | 100% key recovery, planted English −4.750 vs wrong-key −7.355 | `recon/lp1h_norepeat/` |
| i7 pad-restoration oracle | synthetic English enciphered with the *known* AN-END φ(prime) generator | correct keystream recovered P=0.398; wrong keystreams at the 0.09 floor | `recon/i7_oracle/` |
| i11 Smirnov un-bump | synthetic Smirnov-rewritten sample | P 0.202 → 1.000; wrong ordering 0.106 | `recon/i11_smirnov/` |
| Round 2 fractionation autocorrelation | synthetic period-13 trifid | surfaced at its harmonic lag | `r2_fractionation_signature.py` |
| Round 8 SEED | self-plant across all 10 generator variants | **10/10 recovered**, true −11.24 vs wrong-seed −15.8…−16.9; 5 generators reproduced *exactly* against the real libraries | `seed_sweep/` |
| i8 image stego | working OutGuess payload | detected at χ²=47,940 | `recon/i8_image/` |
| Rigid running-key harness | `attack.py selftest` re-finds DIVINITY | pass | `liber-primus/attack.py` |
| Hash preimage batteries | KAT vectors — Whirlpool 5/5 ISO 10118-3, Skein 2/2 v1.3, Streebog RFC 6986, BLAKE 4/4 | pass before use | `pp49_51/`, `blake_closure/` |

### 2.2 Runs with NO positive control — an attack never shown capable of finding a planted signal

**Flag these. Their nulls are weaker than the docs imply.**

1. **Round 9 DIRECTION** (`direction/direction.py`). 2,670 walk/sieve readings, scored against six
   shuffles of the same ciphertext. **No planted signal was ever inserted at computed positions and
   recovered.** The lane's own doc says the real ciphertext scored *worse than its own shuffles*
   (z = −0.40) — which is equally consistent with "no message" and with "the 4-gram scorer cannot
   see a short non-contiguous message read out of a 12,956-rune stream at all." A message occupying
   ~200 of 12,956 positions, scored over a 2,670-reading sweep at stream scale, has never been shown
   detectable by this instrument. **Round-10B lanes reviving any positional reading must first plant
   one and prove recovery.** (ROUND-9-RESULTS.md l.99–124.)
2. **Round 8 SKELETON** (`skeleton/wordlen_search.py`). Null = shuffled LP2 skeleton. **No positive
   control**: no known text was ever inserted as LP2's plaintext (with ~458 interrupters at the
   observed rate and the multigraph ambiguity) and then recovered by the FFT matcher. The doc's
   "a true identification would score near 100%" is an *argument*, not a demonstration — and the
   interrupter/transliteration model is exactly where a true plaintext would fail to hit 100%.
   The encoder alone was validated later (Round 9: PARABLE 20/20 word lengths) — that validates the
   encoder, not the search. **The 20.0% vs 19.8% result may be at the instrument's ceiling.**
3. **Round 8 GEOMETRY, channels B (advance) and C (baseline)** (`geometry/analyze*.py`). No planted
   micro-spacing or baseline channel was inserted into a control render and recovered; the verdicts
   rest on distributional arguments (1.86σ separation; BIC Δ −22…−25). Channel A (shape) is
   quasi-self-validating (a substituted glyph *by construction* has no pixel-identical twin), so A is
   sound; B and C are not demonstrated-sensitive.
4. **Round 8 POINTERS** (`skeleton/doublet_pointers.py`). Null = 2,000 random position sets. No
   planted book-cipher index was recovered first.
5. **ARMADA-20 (2026-06-20), most of the 20 fronts.** `ARMADA-20-FINDINGS.md` reports verdicts and
   best scores but states no per-front positive control. Fronts #14 (crib-drag) and #15
   (doublet-prior decode) explicitly report control behaviour; the rest do not. The Hill 2×2
   exhaustive (#16) is exhaustive so needs none; the running-key fronts inherit `attack.py selftest`.
   Treat the OSINT/reasoning fronts (#7, #10, #18, #20) as *literature review*, not measurement.

### 2.3 Nulls that are best-of-N against a search of best-of-M, M >> N

**This is the single most consequential instrument flaw in the repo.**

- **Campaign XVIII's "false-positive ceiling −6.82"** comes from `robustness.py`:
  **400** wrong-(key, offset) beam trials at `beam_w=300`. The sweeps it licenses run
  41–122 texts × 55 pages × 2 signs × 2 atbash × *every offset* in texts up to 1.6M characters —
  order 1e7–1e9 trials at `beam_w` up to 600. Ratio null_N / search_N ≈ **1e-5 or worse**.
  The tell is on the face of the logs: `RUN-armada18.log` reports per-page bests of
  **−5.79 … −6.22**, i.e. *routinely above the stated "false-positive ceiling"* of −6.82.
  A ceiling that the search beats on every one of 55 pages is not a ceiling.
  - **Does this overturn the nulls? No** — the sweeps found 0 hits above the *confirm* threshold
    −5.5, and a correctly-scaled null would sit *higher* (less negative), making the null safer.
  - **But it does two damaging things.** (a) It means the margin between "best noise" (−5.75) and
    "confirm" (−5.5) is **0.25**, not the "wide, safe 1.3" the findings doc claims
    (`CAMPAIGN-XVIII-FINDINGS.md` l.84–85). (b) Any Round-10B lane that scores −5.4 on a big sweep
    and calls it a hit will be reporting a max-of-many artifact. **Recompute the FP ceiling at your
    lane's actual N before interpreting any number near −5.5.**
- **Round 8 SEED.** Null band measured over **20,000** uniform draws (mean −16.70, max −14.43);
  the sweep ran **2.52e9** decodes. `ROUND-8-RESULTS.md` states the best of 2.52e9 (−13.13) "is
  the maximum of the null" — the *measured* null max was −14.43, so that sentence is wrong as
  written; −13.13 is the *extreme-value expectation* at 2.5e9 draws, which is a different (and
  weaker) statement. **The SEED verdict nonetheless survives**, because its detection threshold
  (−12.5) was anchored on the *English* side (0.1th percentile −11.55), not on the null side. That
  is the right way to do it and is why SEED is the most trustworthy large sweep in the repo.
- **Consequence for the un-finished full-32 sweep (see §4.1):** the two completed generators score
  **−12.85 and −12.79** against a −12.5 threshold. At 4.3e9 seeds per generator the extreme value
  has already climbed ~0.3 from the time-seed sweep's −13.13. Running the remaining 8 generators
  will push it further. **A "hit" at −12.4 in the full-32 sweep would very likely be noise.**
  Whoever resumes that sweep must raise the threshold or re-anchor it on the English tail.

### 2.4 Conclusions promoted beyond their stated scope

1. **The repo's flagship contradiction — Campaign XVIII vs Round 7.**
   `campaign18_skip/armada2/COVERAGE-MATRIX.md` treats the skip-tolerant re-runs as *load-bearing*
   unconditional eliminations ("a clean null from any lane is now an **unconditional** elimination").
   `research/DEAD_ENDS.md` Round 7 (l.234–264) simultaneously says the skip-aware family is
   **already killed as un-anchorable** (R1-H3/R3-H1/R3-H2) and that Campaign XVIII is an
   "**UNLOGGED NULL** … surviving only as orphaned Python-3.12 `.pyc` bytecode (source deleted)"
   whose run counts must **not** be backfilled. Both cannot be right. **On disk today the sources
   exist** (`campaign18_skip/*.py`, `armada/*.py`, `armada2/*.py`) and **all 13 cited RUN-*.log
   files are present** — the merge described in `CLAUDE.md` (2026-08-11) restored them. The Round-7
   "unauditable" note is **stale**. Round 10B lanes should treat Campaign XVIII as audited and
   present, and should not cite the Round-7 note as grounds for either dismissing or re-running it.
2. **"Ciphertext-only program COMPLETE" generalised to all axes.** Declared at
   `DEAD_ENDS.md` l.195–204 (2026-07-30), then Rounds 8 and 9 found five-plus axes that had never
   been ciphertext-only attacks at all (keystream entropy, page geometry, byte payload, cleartext
   skeleton, positional readings). `FRESH-ANGLES-2026-08.md` §"one honest framing note" names the
   error exactly: "the program declared itself complete along one axis and then generalised the
   claim to all axes." **The generalisation has been wrong once already; assume it can be wrong again.**
3. **"Every attack family re-tested with the new lens."** `COVERAGE-MATRIX.md` §"Open, honestly"
   item (2) concedes the interrupter+skip full run was bounded to the **highest-prior** texts, not
   the full 122-corpus × offset space — but the headline verdict above it says every family was
   re-run. Scope-limited in the footnote, unlimited in the headline.
4. **BLAKE preimage "COMPLETE" — caught and retracted in-repo.** `AUDITOR-LOOP-2026-07-28.md` l.29
   carries an explicit `[SCOPE CORRECTION 2026-07-29]`: "last untested hash family / COMPLETE" was
   retracted when the iter-5 provenance pass found the AN-END page names *no* algorithm. Closed
   properly by iter 6 (Skein/Whirlpool/Streebog, KAT-validated). **This is the repo doing it right —
   the template to imitate.**
5. **Campaign-V classifier "corroborates canon" was circular** — caught by Campaign XV
   (`independent-read/FINDINGS.md` l.16–20: the SVC was *trained on canon labels*). The
   `ELIMINATION-LEDGER.md` D-row still cites "trained glyph classifier 99.2% corroborates canon"
   without that caveat.
6. **`research/LEDGER.md`'s multiple-comparisons tally is stale.** It declares itself "the source of
   truth for the cumulative multiple-comparisons correction" and counts **5** executed tests — never
   updated for Round 8 (2.52e9 decodes, 166 payload representations, 3 geometry channels, ~15
   pointer readings, 51-text skeleton scan) or Round 9 (2,670 direction readings). Any lane invoking
   a corrected threshold from this file will use a denominator ~9 orders of magnitude too small.
7. **Two documented self-corrections worth internalising** (the repo already caught these):
   Round 9 overturned Round 8's word-length "anomaly" as a large-*n* passage-vs-aggregate artifact
   (`ROUND-9-RESULTS.md` l.24–61); and the 2026-07-29 loop retracted three of its own positives —
   the clause-position "English signature" (driven by the `/` line-wrap, wrong sign vs English), the
   "surviving English phonotactics" doubling claim (PARABLE was 95 runes / 1 doublet), and
   `FRESH-ANGLES-2026-08.md`'s own §3 statistics (measured over the whole file including the two
   *solved* English pages).
8. **A parsing bug that invalidates any pre-Round-8 word-length work.** `/` in the krisyotam
   transcription is a **LINE WRAP, not a word separator**; **458 of 604 line breaks fall mid-word**.
   Treating `/` as a terminator yields 3,316 "words" (mean 3.91) instead of **2,928** (mean 4.425)
   and manufactures a 2× excess of one-rune words. Split on `-` and `.` **only**.
   (`DEAD_ENDS.md` l.411–417.) Note `FRESH-ANGLES-2026-08.md` §3 and `CAMPAIGN-XIV`'s word-length
   proposals both predate the fix and quote the broken numbers.

### 2.5 Paused, partially run, or missing from the record

| Item | Status | Evidence |
|---|---|---|
| **Full 32-bit seed sweep** | **PARTIALLY RUN — 2 of 10 generators.** `seed_sweep/results_full32.txt` is 214 bytes and contains exactly two lines: gen=3 (MSVC) and gen=5 (mt19937). The documented generator order is 0,3,5,7,9,1,4,6,8,2 — so **gen 0 (glibc `rand()`, called "the single most likely thing" in `FRESH-ANGLES-2026-08.md` §1) is absent from the full-32 record**, as are 7,9,1,4,6,8,2. `PICKUP-HERE.md` item 3 calls it "still running." | `seed_sweep/results_full32.txt`, `run_full32.sh` |
| **`RUN-skipvariants.log`** | Queued as RANK 5 in `ARMADA-RUN-QUEUE.md` with an explicit re-verify command; **no such log on disk**. The finding is asserted in prose ("1.8s smoke, PASS") with no committed output. | `campaign18_skip/armada/ARMADA-RUN-QUEUE.md` l.96–109; `ls campaign18_skip/` |
| **`RUN-armada18-fullcorpus.log`** | The queue's RANK-1 command tees to this filename; on disk there are `RUN-armada18.log` (41 texts) and `RUN-fullcorpus.log` (122 texts) instead. Probably a rename, but the queue and the artifacts do not match by name. | same |
| **A ~53-hour stall inside `RUN-armada18.log`** | Page 47 completes at **4,866 s**; page 48 at **196,176 s**. Pages 0–47 average ~100 s each. Either the run was suspended/resumed or a worker hung. Pages 48–54 (the tail, incl. the two shortest pages 49 and 54) all carry the post-stall timestamps. Not necessarily wrong — but it is an unexplained discontinuity in the only full literary sweep. | `campaign18_skip/RUN-armada18.log` |
| **Ornament inventory** | **Explicitly left open by Round 8.** 47 non-text bands across 23 pages catalogued in `geometry/geometry_report.json`; most are mis-segmented text lines; the short bands (1, 3, 4, 8, 16 glyphs) are the real candidates. `ROUND-8-RESULTS.md` §D: "This is inventory, not a result — the one item in Round 8 left as an open thread rather than a verdict." **Nobody has read them.** | `geometry/geometry_report.json` |
| **Round 9 TEMPLATE (re-transcription)** | **Stage 1 only.** 13,140 glyphs → 1,067 exact bitmaps → 32 shape classes covering 95.8%. Results "appended on completion" — the completion never appears in the record. *(Round 10's template lane owns this; noted here so nobody double-books it.)* | `ROUND-9-RESULTS.md` l.133–143, `retranscribe/` |
| **O/A/AE adjudication** | Campaign XV **did** record a verdict (contra `FRESH-ANGLES-2026-08.md` §4, which says none was): "no blatant single-glyph error"; family is 10.70% of corpus and max-damage collapse moves IoC·29 only 1.00→1.14. **Closed, and the FRESH-ANGLES claim that it is unclosed is itself wrong.** | `independent-read/FINDINGS.md` l.52–68 |
| **STEGO-VERDICT's two "decisive next experiments"** | Experiment **2** (`-k` passphrase re-extraction) **was run** — `armada20/extract21.sh` swept 13 passphrases (DIVINITY/SACRED/PRIMES/CIRCUMFERENCE/WELCOME/3301/INSTAR + case variants) over the relikd LP2 pages; 431 blobs in `armada20/og_out/`, all null. **`33011033`, `firfumferenfe`, `pilgrim` were never tried.** Experiment **1** (blank 400-DPI Ghostscript control JPEG through OutGuess to reproduce the 1417-byte shared prefix) **was never run** — no control file exists in `og_out/`. `STEGO-VERDICT.md` still ends "closed pending the Linux control run", never updated. | `stego/STEGO-VERDICT.md` tail; `armada20/extract21.sh`; `ls armada20/og_out` |
| **`FRESH-ANGLES-2026-08.md` tracks 4 (ADJUDICATE) and 5 (PROVENANCE)** | Round 8 ran tracks 1/2/3 + two of the §6 short shots. **Track 4 (re-run and *commit* the lost wordlen/stylometry/latin/bookcipher campaigns) and Track 5 (source-PDF + rune-font identification) were never run.** No Ghostscript-version fingerprint, no font identification, no search for an original text-layer PDF, no re-read of `structure/origsearch/onion7_index.html` for non-`.jpg` assets. | `FRESH-ANGLES-2026-08.md` §4–5 vs `ROUND-8-RESULTS.md` |
| **Campaign VI open questions #2–#4** | Declared "genuinely not yet run" at `osint/CAMPAIGN-VI-OSINT-FINDINGS.md` l.85–96. #4 (Mayan key) and the P.S. digit string were **subsequently executed** by Campaign VII's completeness pass (76,360 configs, best −6.491) and by Round 4's Gate-#1 kill. #1 (pp49–51 ⊕ 2014-onion-hex) is covered by Campaign IX/XX. **These are closed; the CAMPAIGN-VI doc was never updated to say so.** | `pp49_51/CAMPAIGN-VII-FINDINGS.md` §4; `DEAD_ENDS.md` Round 4 |
| **Per-rune high-zoom vision re-read** | "Documented, not executed" — cost-prohibitive (~13k individual reads). | `PICKUP-HERE.md` l.165, `vision/AVENUE-1-VISION-VERDICT.md` l.60 |
| **6 contested bytes in `canon_256`** | 11 witness disagreements, 5 resolved, **6 genuinely contested** and flagged open; settling them needs a Latin-character OCR (the repo's classifier is rune-trained). | `ARTICLE.md` l.63, `pp49_51/canonicalize.py` |
| **T2/T3 unidentified blobs** | Chased twice (OSINT 2026-07-27; loop iter 11) and characterised as uniform-random with no PGP/RSA/container structure. **Closed enough; do not re-chase.** | `OSINT-SWEEP-2026-07-27.md`, `ELIMINATION-LEDGER.md` l.596–603 |
| **`campaign18_skip` sources once deleted** | `DEAD_ENDS.md` Round 7 recorded them as lost `.pyc` only. **They are present on disk today** (the 2026-08-11 branch merge described in `CLAUDE.md` restored 100 Python sources). The Round-7 note is stale; do not act on it. | `ls campaign18_skip/` |

---

## 3. What the past armadas QUEUED but never ran

`campaign14/REDTEAM-PROPOSALS.md` is the highest-yield file in the repo for this. It is a
17-item standing agenda; only items marked `[DONE XIV]` were executed, and the file explicitly says
"the rest are the standing agenda for future researchers." Cross-checking each against the
subsequent record:

**Executed since (do NOT re-run):**
- word-length/separator battery → Round 8 SKELETON + Round 9 LENGTH (with the `/` bug fixed)
- skip-tolerant keystream decode (the page-73 mechanism generalised) → Campaign XVIII
- doublet forensics (86 doublets as fingerprint) → Round 5 + Round 8 POINTERS
- seeded-generator keystream with encryption-time skip filter → Round 8 SEED (partially: it covered
  glibc/MSVC/MT/CPython/Java, **not** the hash-chain/HMAC-DRBG/RC4/AES-CTR arm — see below)
- generalized-combiner ciphertext-feedback → executed *inside the review itself* (bigram matrix dead
  flat, off-diagonal χ² 841 vs df 811, z = +0.75σ) + `ctfeedback_coeffs.py` for the k=2/3 coefficient grid
- skip-tolerant re-verification of the 112 keytexts → Campaign XVIII
- full-lag self-coincidence scan → Campaign XIV P1–P2 (0 peaks >5σ, column IoC max 1.087)
- word-length skeleton attack → Round 8 SKELETON

**Queued and, on the record, never run:**
1. **Hash/stream-cipher keystreams** — `{MD5, SHA-1, SHA-256, SHA-512 chain & counter, HMAC-DRBG,
   RC4, AES-CTR}` × Cicada seed dictionary × 3 mod-29 reductions × skip-beam. Round 8 SEED swept
   *PRNGs* (glibc/MSVC/MT19937/CPython/Java) and explicitly lists as untested residue: "other
   generators (PHP `mt_rand`, .NET subtractive, xorshift, **RC4/ARC4 keystreams**)". The
   hash-chain/AES-CTR family is queued in two places and executed in neither.
2. **pp49–51 payload as a PRF *seed*** (expanded via RC4/AES-CTR/SHA-counter/HMAC-DRBG), as opposed
   to used directly. The ledger's payload rows all test the payload *as* a key, never *expanded*.
   `RUN-payload-skip.log` and `RUN-payload-ct.log` cover direct use only.
3. **pp49–51 payload as per-page META-parameters** — slide a 56-byte window and test for a
   permutation of 0–55; read the payload as 85–128 gap values (8/16-bit LE/BE, varint) and rank-correlate
   against the observed doublet gaps `[122, 85, 249, 197, 129, …]`; bytes 0–55 as per-page start
   offsets into a generator. Hard numeric gates already written (a valid permutation window has
   chance ~1e-24). **Minutes of compute. Never run.**
4. **pp49–51 payload as an RSA signature/ciphertext under known Cicada moduli** — `pow(s, e, n)` in
   both endiannesses against every Cicada PGP/2012/2013 modulus, pattern-matched for PKCS#1
   `0x0001FF..FF00||DigestInfo` or PSS `0xBC`. Zero-false-positive structure. Explicitly listed as
   "never executed, but P/Q factorization is done; completeness-only" in `OSINT-SWEEP-2026-07-27.md` l.60.
5. **Targeted doublet-site image count-audit (haplography test)** — crop the neighbourhoods of all
   86 canon doublet sites plus ~200 random adjacent-pair sites from the SHA1-verified 400-DPI
   renders and audit **rune COUNT** (not identity) per crop. The proposal's own framing: "the cheap
   falsifier of the entire 'engineered filter' edifice" — ~20 confirmed merges would move the true
   doublet rate toward random and put ciphertext autokey back on the table. **The one queued item
   that could overturn the load-bearing statistic, and it was never run.** (Note: iter 9's
   `i9_inventory`/`i9_ocr` attacked the *inventory cardinality* and did a p0 line-diff, which is
   related but not the same test — it never audited the 86 doublet sites specifically for merged glyphs.)
6. **Generator-fingerprint suite (4 sub-tests)** — conditional next-rune distribution after each rune
   value; windowed χ² under-dispersion (shuffle-bag signature); doublet rate conditioned on
   preceding doublet distance (fit the gap law). Round 5 TIDELINE did the KS-geometric gap test
   (p=0.69) and iter 9 measured per-glyph uniformity, so ~half is covered; the **windowed
   under-dispersion sweep** (machine sampler vs human/deck generation) is not.
7. **Language-agnostic re-scoring of all archived sweep bests** — rebuild OE/Latin quadgram tables,
   re-score every archived best-candidate decrypt from vigauto/runningkey/keystream/autokey, and add
   `decrypt IoC·N > 1.3` as a language-blind gate. R5 ROSETTA was killed on the grounds that
   non-English would raise IoC — which is precisely the gate this proposes adding, and it was never
   added to the harnesses.
8. **LP2-as-pad inversion** — use the 12,956-rune stream (fwd/rev/±/Atbash) as a running key against
   every *other* machine-readable Cicada object (2012/2013 fragments, the AN-END hash bytes, the
   pp49–51 payload, onion names, PGP bodies). Finite and small. Not in any log.
9. **Extended-corpus second-order rerun** — moot: Campaign XIV established the "~75-page gap" is
   solved pages, so there is no additional unsolved material to ingest.

`ARMADA-RUN-QUEUE.md`'s six RANKs are all accounted for except RANK 5's log (§2.5). RANK 6 (AN-END
v2-onion OSINT) was executed and closed by the 2026-08 AN-END hunt.

From `armada/completeness-critic.md` (2026-06-17), item **C — "transposition combined with a
doublet-avoidant layer"** was proposed not as an attack but as a **validity check on the whole
fingerprint**: if a transposition sits *outside* the substitution, the measured delta=0 hole is an
artifact of reading order. `CRYPTO-RIGOR §B` answered this for **columnar widths 2–40** (file order is
the unique global doublet minimum, 0.0067; every width restores doublets toward random) and Round 2
killed the rail/boustrophedon residue at Gate #1. **So C is covered for columnar/rail — but the
critic's framing ("this tells you whether your own evidence means what you think it means") never got
its own recorded verdict.**

---

## 4. Practical guidance for Round-10B lanes

1. **Do not re-derive the state.** Everything in §1 is cited. Cite it.
2. **If your lane touches a score near −5.5 (page scale) or −12.5 (stream scale), recompute the null
   at your own N first.** The published ceilings (−6.82 / −14.43) are best-of-400 and best-of-20,000.
3. **If your lane proposes a decode, plant a signal and recover it before you interpret a null.**
   Three of Round 8/9's five tracks did not.
4. **Anything touching word lengths: split on `-` and `.` only.** `/` is a line wrap; 458 of 604
   fall mid-word.
5. **The highest-prior queued-never-run items**, in the owner's "small, human, period-correct"
   frame: the **doublet-site haplography image audit** (§3.6 — falsifies the load-bearing statistic
   for the price of ~286 image crops), the **payload-as-meta-parameters** battery (§3.3, minutes of
   compute, 1e-24 gates), the **payload-as-RSA-signature** check (§3.4, zero-false-positive), and
   **track 5 PROVENANCE** (source PDF / rune-font identification — a 2014-era artifact hunt nobody in
   this repo has ever attempted).
6. **The one genuinely dangling instrument question**: `RUN-armada18.log`'s 53-hour stall between
   pages 47 and 48. If a Round-10B lane needs the literary sweep to be load-bearing, re-run pages
   48–54 and confirm they reproduce.
