# Fork B — fresh-eyes audit of Rounds 1–10b (research/ round-era docs, seed_sweep, skeleton, direction, round10, round10b)
_2026-11-12. Read-only on the repo. Verification snippets live in `audit/B_work/` (this scratchpad). Paths below are relative to
`the repo root` unless they start with `analysis/` (= `liber-primus/analysis/`)._

## 0. What I read
research/LEDGER.md (all), DEAD_ENDS.md (all), FRESH-ANGLES-2026-08.md (all), ROUND-8-RESULTS.md (all), ROUND-9-RESULTS.md (LENGTH part),
round10/SYNTHESIS.md, RECON-A/REGISTER.md, RECON-B/REGISTER.md, L5-seed32/CENSUS.md (grep), L9-randomness (PREREG + result JSON),
round10b/B4-otp-steelman (PREREG + full run log), B2-hand-cipher (PREREG, logs, results_stage1b.json), B5 file list,
seed_sweep/sweep.c (all of keystream/decode/selftest), skeleton/{length_anomaly.py, *.json, fetch_corpus.sh},
LEDGER.json rows A-xx…J-xx, B-21, B-01, R19-G1/G2/G3-CORRECTION, R26-A, R28-L4, R32-B3; MEASURED-CEILING/PICKUP/ELIMINATION greps.
NOT read in depth: round10 L1–L3/L6–L8, round10b B1/B3/B6/PA-1..3, direction.py, ROUND-7-GATE1-SYNTHESIS, ROUND-9 TEMPLATE part.

---------------------------------------------------------------------------------------------------------------
## 1. FINDINGS (ranked)

### F1 [INSTRUMENT-DEFECT → reopens a closed cleartext-channel anomaly] R9-LENGTH's closing statistic is Project-Gutenberg licence boilerplate
- Claim closed: research/DEAD_ENDS.md:448-465 and research/ROUND-9-RESULTS.md:34-61 ("44 / 47 texts contain a 2,928-word passage
  reaching 4.268 … NOT AN ANOMALY … Do not re-open the word-length excess"); README analysis map repeats it ("closes the word-length excess").
- Code: analysis/skeleton/length_anomaly.py:106,125-126 reads every corpus file raw and tokenises all `[A-Za-z']+` — the PG header and the
  ~3,000-word PG licence at the end of every Gutenberg file are never stripped. The sliding window is exactly 2,928 words.
- Smoking gun in the committed result: analysis/skeleton/length_anomaly.json `h1.top` — ten unrelated texts (Corpus Hermeticum, Elder Edda,
  Anne Frank, Apocrypha, Iliad, Meditations, Metamorphosis, Poetic Edda, Blake, "Emerson") all have max_passage 4.776–4.800, and two
  (`g/blake_poems`, `g/emerson_essays_first`) are identical to 15 digits (4.77629781420765 = 13,985/2,928). Same 2,928 words = the licence.
- Verified by execution (audit/B_work/pg_boiler.py) on the 34 locally held texts in liber-primus/data/keys/armada18/ (22 still carry the PG
  licence): RAW, 22/22 PG files have max-window 4.77–4.85 with argmax at file position 1.000 (the tail) and all "reach" 4.268.
  STRIPPED (between `*** START OF`/`*** END OF`): Dante 4.771→3.973, Odyssey 4.779→4.121, Genesis 4.771→3.857, Hamlet 4.773→4.026,
  Tempest 4.773→3.940, Magna Carta 4.777→4.197, Moby Dick 4.777→4.405, Republic 4.774→4.417. Stripped: 14/22 PG files reach 4.268, 10/22 reach 4.425.
- Second defect in the same closure: the "lower bound" 4.268 assumes ALL 458 F runes are nulls (length_anomaly.py:119). F occurs at the flat
  rate (458 vs 446.8 expected, z=+0.5), so at most ~50 F can be nulls (2σ); the plaintext mean is ≥ ~4.41. RECON-B already said the test was
  only shown at the favourable end (analysis/round10/RECON-B/REGISTER.md "B-19 in detail"; LEDGER.json B-19 = open, empty coverage, never actioned).
- Possible mislabel (UNVERIFIED — gutenberg.org is blocked by this session's proxy): skeleton/fetch_corpus.sh:21 `fetch 26 emerson_essays_first`;
  PG ebook #26 is, to my memory, Milton's Paradise Lost (and :24 "milton_paradise_lost" 26839 is the one that failed). If so the "Emerson 19.5 %" row is Milton + licence.
- What survives honestly: after stripping, LP2's point estimate 4.425 IS reached by Latinate/occult/legal/Lovecraft registers
  (Blavatsky 26 % of windows, Levi 34 %, Agrippa 3–8 %, Lovecraft 10–87 %, US Constitution 23 %) and by NONE of Emerson I/II, Moby Dick,
  Plato, KJV, Mabinogion, Shakespeare, Dante, Homer, Crowley, Hall. So "register variance" is not refuted — but it is no longer demonstrated
  for the registers the book resembles, and the closure rests on a contaminated number. See F2 for what the channel actually says.

### F2 [UNEXAMINED-INPUT / SHARED-PREMISE] The word-length DISTRIBUTION of pp.0-54 does not match multigraph-transliterated English — it matches one-rune-per-letter English
The repo only ever tested the MEAN. The shape was recorded as "distinguishable" and then dropped:
analysis/skeleton/cleartext_profile.json (`solved LP1 English` KS 0.120 > crit 0.093; moby 0.099; pride 0.080; kjv 0.138, all "distinguishable"),
analysis/skeleton/interrupter_null.json (best_ks 0.0459 > crit 0.0253 even with ALL 458 F treated as nulls).
My measurements (audit/B_work/wl_check.py, wl_shape.py; LP2 parse reproduces 2,928 words / mean 4.4249 exactly):
- LP2 unsolved word-length histogram (% of words, len 1..8): 3.4 15.9 24.8 17.6 10.9 8.6 7.3 5.4.
- The author's SOLVED pages in the same book, actual runes, same separator convention (scream314 source; 732 words; AN END 25 words mean
  3.40 and PARABLE 20 words mean 4.75 reproduce the repo's numbers): 3.8 24.3 23.9 17.5 7.8 8.3 6.0 3.3, mean 4.068.
  Two-rune words: solved 24.3 % vs unsolved 15.9 % → z = 4.9. Mean +0.36 → z = 3.5. Homogeneous: every 5-page block of pp.0-54 has p2 = 12–18 %.
- 34 local texts × 2 encodings ranked by KS to LP2: the 16 best fits are ALL the one-rune-per-letter encoding; zero multigraph encodings.
  Best: Moby Dick [letters] KS 0.0222 (< 0.0251 critical: statistically indistinguishable — the first encoding of any text in this repo that is),
  Lovecraft-Colour [letters] 0.0230, Hall 0.0282, Agrippa-3 0.0317, Emerson II 0.0362, Emerson I 0.0374 … Cicada's own prose [letters] 0.0475.
  Best multigraph fit of any text: 0.0550; Cicada's own prose [multigraph] 0.109; Emerson I [multigraph] 0.108.
  The discriminator is the 2-rune class: multigraph English makes THE/THY/… two runes → 21.6–27.1 % two-rune words; letter-wise gives 14.6–20.5 %.
- Nulls do not rescue the multigraph reading: inserting nulls at the doublet-site rate (2.9 %) leaves KS 0.070–0.094; the best null rate is
  10–12 % of all runes (≥1,300 nulls) and still fits worse (KS 0.032–0.049) than the letter encoding (0.022–0.037) for all three base texts tried.
Three readings, all with consequences, none tested anywhere in LEDGER.json (grep for multigraph/orthography/letter-by-letter rows: only the
round16 "matched runic" scorer, which moved the instrument TOWARD strict multigraph):
 (a) pp.0-54 plaintext was transliterated one rune per Latin letter (THE = 3 runes; TH/NG/EA/IO/… runes essentially unused in plaintext) —
     natural for a script-enciphered text; contradicts nothing measured (ciphertext is flat either way); the solved pages do use multigraphs.
 (b) ≥10 % non-F nulls (no construction, no precedent; R1 found none at F).
 (c) a non-English / article-free / unusual register (R8/R9 compared means for Latin and Welsh only).
Why it matters for solving: under (a) every language model in panel-R36 is mis-specified. The panel streams are built by
`text_to_runes` = strip to A–Z then greedy multigraph (analysis/round19/R1/r1_lib.py:423-428, used by round19/I2/build_models.py:106-145), so
the bigrams T→H, N→G, E→A, I→O/I→A, A→E, O→E, E→O never occur in ANY training stream, while letter-wise English has one in ~7–8 % of positions
(TH ≈3.5 %, IO in -TION, ING, EA…). Power of beam_v3 + pf_v4_12 + panel-R36 against letter-wise English is unmeasured (controls plant through the
same encoder). This is the L7-A failure shape on the orthography axis. Also under (a) a correct decode would use ≤ ~22–24 distinct runes — a
language-free recognizer already persisted per R3 (mds / IoC·N) but only for rows that survive an LM-based screen.
Cheapest discharge (all local, no network): (1) PREREG + rerun of the shape test with boilerplate stripped (30 min); (2) plant letter-wise
English through verify_solution.py / beam_v3 / pf_v4_12 and read recovery + screen power (≈1 h); (3) if power is low, add an EN_LETTERWISE
register and re-score stored rows. Kill attempts I made: parse identity (2,928/4.4249 ✓), separator audit exists (A-05: 582/604 lines exact),
per-section homogeneity ✓, solved-page like-for-like ✓, nulls ✗. Not killed: reading (c).
(Adjacent, outside my partition, one line: because `text_to_runes` strips spaces before the greedy merge, the panel LMs — and LP1_REAL, built from
concatenated transliterations — also merge digraphs ACROSS word boundaries ("THE OTHER" → TH,EO,TH,E,R; "BE A" → B,EA), which real word-wise
plaintext never does; ~1 % of positions; someone reading round19/I2 should confirm.)

### F3 [LOGIC-GAP, handed-off-and-dropped] Periodic keys of period 64–~3000 under filter drift were never tested; B2 and B4 both say so
- analysis/round10b/B2-hand-cipher/PREREG.md:70-72,99 ("Key lengths above k_max are *not* excluded by this test and must be handed to future
  work"); results_stage1b.json: W1 `k_min_excluded_below` 444 (IoC), W2 single-lag κ wall ≈ k 32–48 for R2_KEYADV; round10/SYNTHESIS.md
  ("survives only k≥64, outside scope"); ELIMINATION-LEDGER.md:878,895 (p*≈400). B4's battery has no lag-p statistic at all.
- Campaign XIV P1 (lags 1..6478, "0 lags above 5σ") is a rigid single-lag test. Checked: no LEDGER.json row, nothing in MEASURED-CEILING/PICKUP
  for period/kappa (greps). So the class {key period ≥ ~444, key-advancing soft anti-repeat} is IoC-invisible, single-lag-κ-invisible and untracked.
- I ran the missing test at audit level (audit/B_work/drift_kappa.py, drift_kappa2.py): a drift-matched filter over the lag-coincidence curve
  (Poisson(ρ·p) smear, ρ=0.0279, both drift directions, harmonics 1–2, p=64..3000) plus a rigid p/2p scan.
  Planted (quadgram-Markov English, random periodic key, B2 rule R2_KEYADV, soft 0.81): detection at the null-p99 threshold 8/8 for p=300/450/600,
  7/8 for 800 and 1000, 4/8 for 1300, 1/8 for 1700; the rigid scan detects 0–1/8 of the same plants (confirms B2's wall) but T≈17–20 for no-drift rules.
  REAL LP2: drift-matched T = 2.76 (24th percentile of a 300-stream soft-filter null; null p99 3.80, max seen 5.47 in 340), rigid T = 3.14 (3rd pct).
  Real T is below every one of the 24 plants at p ≤ 600. So: no key-advancing periodic key with period 64–~1000; unpowered above ~1300.
  This is an audit snippet, not a pre-registered lane — it needs a PREREG + ledger row to be citable. Cost: < 1 hour.

### F4 [LOGIC-GAP] L9 "finite-state generator" negative has zero power by its own gate, and is cited as an elimination
- analysis/round10/L9-randomness/results_linear_complexity.json `gate`: `lcg_mod29` bm_lc 6478 = n/2 and `lfsr40_antirepeat` bm_lc 6478 = n/2 —
  the instrument cannot see an LCG reduced mod 29, nor any LFSR once the anti-repeat filter is applied; and the test ran on CIPHERTEXT
  (plaintext + key), where even an unfiltered LFSR keystream gives n/2. Yet round10/SYNTHESIS.md verdict table ("Pad is a finite-state
  generator … NEGATIVE") and liber-primus/ELIMINATION-LEDGER.md:876-877 list it as a keystream/pad-channel elimination. No LEDGER.json row.
- Matters because it is the only "generator-agnostic" exclusion the repo claims; in truth only named-generator sweeps exist. Cost: a text fix.

### F5 [LOGIC-GAP in tracking] The `srand(time(NULL))` window for libc-family generators has only ever met the rigid English 48-rune kernel
- analysis/seed_sweep/sweep.c:246-292 `decode_score` is rigid (F-null branching only); the selftest plant (:315) applies no ciphertext filter; gen 2
  (:167) rejects on a repeated KEY value, not a repeated ciphertext rune, so none of the ten generators models the pinned filter. By arithmetic,
  P(no key-skip in 48 runes) = 0.26 and the −12.5 bar needs the first ~29 runes aligned → power ≈ 0.44 against a true keyskip1 seed (lower for keyskip2).
- LEDGER R19-G3-CORRECTION records "rigid, power not re-measured"; R32-B3 re-ran glibc gen 0 on 48,036 prior-dense seeds (top-of-hour/midnight, not
  every second); R19-G1 not_covered says the 2011-2015 unix-second window for lrand48/Perl drand48 is "already covered … S1 must NOT re-sweep that window".
  MEASURED-CEILING.md:106 files the remainder under "the flat tails". The unix-second window 2012-01..2014-06 (7.9e7 seeds/generator) is the
  highest-prior idiom FRESH-ANGLES §1 named, is the size of one bash orbit (swept three times), and is not a flat tail. Tracked only inside the
  never-run 25×2^32 queue (R28-L4). Cost: one orbit-sized pf_v4_12 run per generator (hours each on the existing engine).

### F6 [CONTRADICTION / stale ledger rows] (tidiness, but they mislead a ledger query)
- LEDGER.json A-02 and B-13 (O/A/AE adjudication) = partially-run, empty coverage; analysis/README Round 19 row says T1/T2/T3 upheld canon 450/450.
- C-01 = open "Never extended"; round10 L4-skeleton extended it to 224 texts / 22.6 M words (round10/SYNTHESIS.md table).
- B-01 = "2/10 complete"; R19-G3-CORRECTION found nine full-32 rows. B-03 = open with empty coverage though PHP/.NET were later swept.
- No LEDGER.json row at all for round10b B2 (k≥64 residue), B3, B5, B6, or round10 L9, L1 (INCONCLUSIVE at 99.41 % vs 99.5 %).
- round10/SYNTHESIS.md says B5 "complete (6/55 pages)" but the lane holds RESULTS-all55.txt.
- research/LEDGER.md Round 4 states the AN-END hash → `gy3hoy2zizvuzvdb.onion` as fact; DEAD_ENDS.md (AN-END section) calls that address a
  search-summary hallucination.

### F7 [DROPPED-LEAD, low] B4's own table: real LP2 misfits the pinned model on the nonzero-delta dispersion
- analysis/round10b/B4-otp-steelman/RUN-identifiability.log:111,114: "A_extpad+filter (REPO'S PINNED MODEL) differs: diag_cv_nz(z=2.0)"; D z=2.4;
  vs shuffled null z=+1.59. Consistent with R6's deepest offset k=17 (z=−2.78) and an independent χ² of 42.1 on 27 df (p≈0.03) for nonzero lag-1
  deltas. Three views of one ~2σ effect; never followed up; probably chance. A matched-control χ² with 10^4 soft-filter surrogates would settle it in minutes.

---------------------------------------------------------------------------------------------------------------
## 2. Answers to the pointed questions

**Q1 RECON registers vs LEDGER.json today (53 rows A-xx…J-xx).** Still never-run/open/partially-run: A-02, B-01, B-03, B-06, B-07, B-08, B-09, B-11,
B-13, B-13-MARSAGLIA, B-14, B-15, B-17, B-18, B-19, B-20, B-21, B-22, B-24, C-01, D-02, D-03, D-04, F-02, G-01, H-01, H-02, I-02, I-04, J-01.
Of these, stale (work was done): A-02/B-13, C-01, B-01, B-03 (partly), B-20 (R40-C1-R13 re-scored it). Genuinely open and solving-relevant:
B-19 (see F1/F2), B-11/G-01 (font: Junicode, Everson Mono, allrunes slot search — an allrunes hit would promote TeX PRNGs), D-04 (ciphertext-feedback
sweep on 3/55 pages), H-01 (onion server-status channel), D-02 (matched-control higher-order test). B-14's S1/S2 (superimposition / positional
structure) are effectively covered by in-depth tests; D-03 is effectively closed by off-diagonal bigram flatness (any direct class coding would
inflate the 29×29 χ² far beyond the observed z≈0.7–0.8).
Closed by a test that could not represent the hypothesis: L9 (F4, no row); B-21/R8 family (rigid; tracked); A-03 is a rune-COUNT bound only
(K_bound 26 vs 93), which is fine for its stated purpose.

**Q2 B4/G5.** Six statistics: IoC·N, doublet %, entropy, monogram χ², CV of nonzero lag-1 difference counts, off-diagonal bigram χ² — all
first-order or lag-1. Rivals actually run: A pad+filter, B SHA-256-ctr+filter, C period-40 key+filter (fails), D Caesar over flat plaintext,
E ciphertext-autokey over flat plaintext (both pass), F unfiltered pad (fails). So "OTP-class" = G3 (a theorem: an unfiltered plaintext-independent
additive key cannot go below 1.50 % doublets) + a failure to separate two additive+filter members with a lag-1 battery of 40 realisations each.
It has no power against a long-period key (no lag-p statistic; see F3), polygraphic systems beyond R5's digraph-parity test, transposition layers,
or feedback constructions over real language. It is a non-rejection inside a small comparison, not a measured property; the ledger's
VERDICT-OTP-CLASS row is correctly `open`.

**Q3 period 300–2000.** Nothing after B2/B4. Instruments on file: monogram IoC (excludes < ~444), rigid single-lag κ (Campaign XIV to 6478; B2 to 400).
Neither is powered under key-advancing drift (B2's own wall ≈ k 32–48; my plants: rigid 0–1/8). F3 supplies an audit-level negative for 64–~1000.

**Q4 FRESH-ANGLES.** §1 SEED run (rigid). §2 geometry run; line geometry later measured (B-12, R19); ornaments read (R18/R19); OutGuess control
superseded (B-10). §3 skeleton run (51 → 224 texts); the "1-rune excess" was the `/` parse bug; the shape question was never asked (F2).
§4 O/A/AE finished in R19. §5 provenance partly run (R18 L1); font identity still open (B-11). §6 all three short shots run. Nothing vanished silently.

**Q5 English-only rigid dead ends never re-run.** R8-SEED time-seed windows for glibc/MSVC/Java/py3/Perl (F5); R8-POINTERS and R8-PAYLOAD (low value);
R6 SIEVE-W's LLR arm is English-only but its IoC arm is register-agnostic. R4's three "never-used" strings and R7's absent keytexts WERE later run
(H-03, R37-C2, R40-C1-C18; Campaign XVIII armada) — not findings.

---------------------------------------------------------------------------------------------------------------
## 3. Checked & clean
- Rounds 1, 2, 5, 6 structural tests: statistics and nulls read; R5/R6 conclusions (pure lag-1 rule, no parity, geometric gaps) agree with the
  coordinator's independent recomputation. NO-ERROR-FOUND.
- B4 G1–G3: re-derivation matches; G3 bound is a correct theorem for its stated class.
- R4 external strings, R7 keytexts: later executed under skip-aware decoders. Not open.
- B5: all 55 pages were run (file present); SYNTHESIS wording is stale only.
- sweep.c generator implementations: read, consistent with the stated references; the defect is the decode model, already recorded.

## 4. Premises this era never tested
1. That pp.0-54 plaintext uses the same multigraph transliteration as the solved pages (F2).
2. That the filter's corrections do not re-phase a long periodic key (F3) — tested here only for one rule and ρ.
3. That "keystream continuous across pages" is a keystream fact; the evidence is filter continuity (0 cross-page doublets of 54, LR ≈ 4.5:1).
4. That a ciphertext statistic (linear complexity) can speak about the keystream while the plaintext is still in it (F4).
5. That word boundaries in pp.0-54 mean what they mean on the solved pages (reading (c) of F2).
