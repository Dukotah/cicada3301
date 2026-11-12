# Fork I — rounds 36-38 audit notes (2026-11-12)

Scope read: round36/37/38 SYNTHESIS, O4 (PREREG/RESULTS/matrix/untried/clues.json), AUDIT-inhibitors + AUDIT-applied,
O3 RESULTS + decode_text, R37 C1 PREREG/RESULTS, C3 RESULTS, U7/U8 RESULTS, R38 C1/C2/I1 RESULTS, closed_no_operation.md,
n5n4 bundle, X1 reports (grep-skim), plus code: beam_v2 ADVANCE, driftbeam docstring, beam_v3 header, pf_v4_12, c1lib,
run_b.py, round11/N5/n5.py. Paths below are relative to liber-primus unless they start with research/.
My scripts (all in scratchpad audit/): wordlen_register.py, wordlen_windows.py, wordlen_alternatives.py,
probe_unfolded.py, probe_unfolded_screen.py, skeleton_probe.py. Loader: scratchpad lpdata.py (hash-verified).
Nothing in the repo was modified (git status clean after every run; PYTHONDONTWRITEBYTECODE=1).

---------------------------------------------------------------------------------------------------------------
## F1 [DROPPED-LEAD -> new measured fact]  LP2's cleartext word-length SHAPE is incompatible with LP1 orthography
---------------------------------------------------------------------------------------------------------------
History. Round 8 left "the LP2 word-length excess" open; Round 9 closed it on the MEAN only, at the lower bound 4.268
(all 458 F treated as nulls): research/DEAD_ENDS.md:448-465, line 464 "Do not re-open the word-length excess";
analysis/skeleton/length_anomaly.py:1-25; length_anomaly.json h1 {lo 4.268, n_reaching 44/47}.
Round 10 RECON-B item B-19 objected (analysis/round10/RECON-B/REGISTER.md:172-185: "closed on the lower bound, not the
point estimate ... a one-line change"). LEDGER.json row `B-19` is still `open` with every field null; it is not in
PICKUP-HERE.md, MEASURED-CEILING.md, ELIMINATION-LEDGER.md or handoff/PARKED.md (grep). 33 rounds, never run.

What I measured (like-sized passages, as DEAD_ENDS:464 demands; canonical parse: '-' and '.' are word boundaries, '/' is
a wrap; 2,928 words, mean 4.425, matches ST-LP2-SHAPE):
- LP2 length profile (% of words, len 1..10): 3.4, 15.9, 24.8, 17.6, 10.9, 8.6, 7.3, 5.4, 2.6, 1.7.
- Solved pages, actual rune words (scream314 parse): 2-rune share 0.22-0.32 on every solved page with >=25 words
  (01: .222, 03: .221, 06: .215, 10: .318, 14: .307, AN END .320, PARABLE .250). LP1 English (729 words) folded: .244.
- 82 English texts in data/keys (armada18/19 + self_reliance), 21,698 sliding 2,928-word windows (step 400):
  | orthography of the candidate plaintext | windows with 2-rune share <= LP2's 0.159 | windows whose full profile is
  compatible with LP2 (two-sample G <= 22.4) | min G | median G |
  | O1 = LP1 greedy digraph folding (ING,EA,IA,IO,AE,OE,NG,EO,TH) | 2 (0.01%; both in Crowley's *Liber 777*, a book of
  tables) | 0 | 37.2 | 169 |
  | O2 = same, TH NOT folded (THE = 3 runes) | 2,376 (10.95%, 50 texts) | 611 | 6.0 | 77 |
  | O3 = no digraph runes at all | 3,040 (14.0%, 51 texts) | 845 | 3.3 | 74 |
- The repo's own statistic at the point estimate (B-19's one-line change): mean >= 4.425 is reached by 11.7 % of O1
  windows (71/82 texts) -> the MEAN is unremarkable; the anomaly is entirely the 2-rune-word deficit.
- Same-author check: LP1's own English (THE = 6.3 % of tokens) vs LP2, two-sample G: O1 38.7 (p~6e-5), O2 15.2
  (compatible), O3 27.7.
- Uniform across the book: 2-rune share by 5-page block .12-.18; per-page heterogeneity chi2 43.1 on 54 df.
- Alternatives tried and found worse: (i) strip all 458 F as nulls -> still only 2/21,698 O1 windows compatible;
  (ii) uniform inserted nulls at rate q: needs q >= 0.10-0.14 (1,300-1,800 extra runes) to reach 0.8-1.5 % compatible
  windows, vs 2.8-3.9 % for O2/O3 with no free parameter; (iii) dropped separators cannot reach 15.9 % (merging lowers
  f1 too; f1 = 3.4 % is English-normal); line-wrap is not the cause (124 of 512 in-page line breaks carry a '-',
  expected 116 for random breaks).
- 1-rune-word share 3.4 % is English-like (Latin Aeneid 0.6 %, Welsh substitute corpus 19.5 %, OE rune poem 11.5 %).
Reading: the unsolved pages' plaintext is English-like but is NOT written the way LP1/AN END/PARABLE are written; the
simplest fit is that TH (possibly every digraph rune) is spelled with two runes (a per-letter transliteration, as a
script would do), or the text has ~10 %+ extra in-word runes. Either way the "LP1 orthography" premise is contradicted
by the one cleartext channel.

Consequences checked here (probes, small n, not ledger-grade):
- Instrument is ROBUST to it: beam_v3 panel_max + panel-R36 with the correct key on O2/O3 plants (EN_MODERN and
  LP1_REAL held-out text, keyskip1 and skip_by_two encipherers, 8 plants/cell): recovery 0.999, pmax 15.4-17.2 at L=120
  (O1 17.9-19.7; bars 9.0-10.5), 22.9-25.3 at L=240. pf_v4_12 head screen, 1,500 true-key heads per cell: pass rate
  O1 0.979-0.984, O2 0.975-0.980, O3 0.975-0.983 (EN_MODERN, EN_KJV; a=1,2). So no retro-invalidated sweep negative.
- Lanes that used LP1-folded word lengths ARE conditional on the wrong orthography: Round 8 SKELETON (known text as
  plaintext, 51 texts / 8.2 M words; ELIMINATION-LEDGER.md:247; ledger C-01 open, extension never run), Campaign XVIII
  item 2b (ELIMINATION-LEDGER.md:317), the "word-length typology" retraction (ELIMINATION-LEDGER.md:705), and any future
  crib/word-pattern work. Exploratory probe (skeleton_probe.py; exact 12-word-length runs, 95 local key texts, 9.1 M
  words, O1/O2/O3): longest run 12 = chance (shuffled-LP2 control 0-4 raw hits). Probe-only; a registered re-run with
  an indel-tolerant matcher and the C-01 corpus extension is the proper discharge.
- Free language-agnostic oracle clause: under O2 about a quarter of the 726 three-rune words must decode to T-H-E, and
  the TH rune should be near-absent in a correct decode; under O1 the 465 two-rune words cannot hold a normal THE rate.
- Register prior: Greek/Hebrew/Norse were added with Q2 = "not covered before" (analysis/round36/I1-new-registers/
  PREREG.md:10) — the cleartext channel was never used as register evidence; it favours English strongly.
Cost to discharge properly: 1-2 h (PREREG; planted O2/O3 control through beam/screen at 24 plants x 12 registers is
unnecessary — EN family only; skeleton re-run under O2/O3 minutes; annotate DEAD_ENDS:464; fill ledger B-19).

-----------------------------------------------------------------------------------------------
## F2 [UNDISCHARGED owner decision -> mechanically adjudicable]  The N5/N4 "bundle read" is moot
-----------------------------------------------------------------------------------------------
analysis/round38/C2-never-cells/RESULTS.md:17-22, 39; n5n4/oracle/bundle.json; PICKUP-HERE.md:24.
Both flagged rows use keys that are POINTWISE functions of the ciphertext rune itself:
- N4 `b5_p1_ks-1`: K_i = base-5 digit (place 1) of prime(C_i)  (run_b.py:44-60).
- N5 `phi_phi_prime_RI_s-1_o11`: K_i = phi(phi(prime(C_i))) + 11  (round11/N5/n5.py:128-129,147 "rune-indexed cousin").
So "plaintext" P_i = C_i - K_i = h(C_i) is a fixed many-to-one relabelling of a flat ciphertext. Verified: the rigid
relabelling reproduces the bundle decodes 240/240 runes (both rows); |image(h)| = 14 (N4) and 16 (N5); predicted
IoC*29 = 2.72 / 2.52 from preimage multiplicities alone; observed 2.69 / 2.31. A pointwise function of a ciphertext
with IoC 1.000 cannot be plaintext in any register; the pmax comes from alphabet collapse. NOISE by construction —
no human read is needed. The whole R11-N4 "keystream" family (digit planes of the ciphertext's own primes) and every
`_RI` generator are degenerate in the same way; the R37-C3 degenerate filter (mds <= 6 or IoC*N >= 4.24;
round37/C3-rescore-reopened/RESULTS.md:5) does not catch image sizes 14-16. A one-line structural rule ("key is a
function of C_i alone -> not a decode") is exact and cheaper than the key-matched null (R39 T1).

---------------------------------------------------------------------------------------------------------
## F3 [SHARED-PREMISE, bounded here]  No lane of the panel-R36 generation can represent an F-interrupter stall
---------------------------------------------------------------------------------------------------------
Every keyed solved page has literal-F nulls that do NOT advance the key (docs/SOLVED-PAGES-AND-INTERRUPTERS.md "The F
interrupter rule"; 03.jpg x7, 14.jpg x2, AN END x1). The beam's relations only ever advance the key (analysis/round19/I1/
driftbeam.py:11-19; round32/I1-skipbytwo-decoder/beam_v2.py:34-38: keyskip1, keyskip2, permissive), pf_v4 likewise
(advance 1 or 2). Round 19 measured the consequence on AN END (~14 % read; README "Round 19" note). The ledger discloses
it only inside two rows' not_covered (R33-I1-REGISTER-AWARE-BEAM, R33-B3-V3-READJUDICATION: "interrupters"), and
MEASURED-CEILING.md:33 (the beam row's "Measured limits") omits it. No round 19-43 doc quantifies it (grep).
Bound from the data (mine): F count 458 vs 446.8 expected (sd 20.8) -> literal-F nulls m = 11.6, 95 % upper 47,
2-sigma upper 55 (<= 0.42 %/rune). LP1-style "every plaintext F is a literal F" is excluded for English: 2-rune words
ending in F: 10 of 465 (expected 16 uniform; ~110 if OF were written with a literal F); 3-rune words starting with F: 34
(25 uniform; ~51 if FOR etc.). So the hole is real but small: P(>=1 stall in a 24-rune head) <= 0.10, in an L=120 window
<= 0.40 at the 2-sigma limit (central estimate ~0.10). Unmeasured power loss; a stall transition in beam_v3 plus a
planted control is ~half a day; the census itself is minutes and should be cited on the ceiling page.

-------------------------------------------------------------------------------------------
## F4 [UNDISCHARGED]  The critic pass over the 34 "no operation stated" cells never happened
-------------------------------------------------------------------------------------------
round38/C2-never-cells/RESULTS.md:39 (Decision 4: "Round-39 critic: do any of the 34 no-operation closures hide a
literal rule (H8xF1, L11xF1, L18xF1 likeliest)?"). round39/CAMPAIGN-PLAN.md:33 and round40/CAMPAIGN-PLAN.md:26 list the
34 cells as "Not a target"; MEASURED-CEILING.md:198 pins them as a class. No reason recorded.
My sample judgement of closed_no_operation.md:
- Fair closures (no operation): H1xF1/F7/F8, H5xF10, H6xF1, H9x*, L1xF1, L3x*, L7xF1, L9xF1, L10xF1, L12xF7, L16xF11,
  L17xF3, S3xF7 (later run anyway: R43 F6), S4xF10.
- Rationale wrong on its face: L13xF7, L13xF8, L18xF1 say "circumference is never formalised". The author formalised
  it: FIRFUMFERENFE is the Vigenere key of the circumference koan and DIVINITY the key of WELCOME (clues.json ST-KEYS;
  matrix row S1). PARABLE is the last page of the release and reads as an instruction naming both key words ("shed our
  own circumferences / find the divinity within and emerge"). Finite formalisations: (a) remove key CIRCUMFERENCE then
  apply DIVINITY (period lcm(13,8)=104) under per-page/per-line resets and stalls — this lands inside Round 44 R1's
  reset family and should be named there; (b) "circumference" = outer runes of each word/line/page, shed them, read
  the interior with DIVINITY. Low prior (short periodic keys are IoC-excluded on a continuous stream), cost minutes.
- L11xF1 / H10xF1 ("within"): the cleartext chapter title "Chapter I / Intus" (data/scream314_lp.md:193-202) is not a
  clue entry at all; INTUS was used only as a keyword (armada20/riddle_phrases.txt, round29 L1).

-----------------------------------------------------------------------------------------------------
## F5 [LOGIC-GAP]  "Measured keystream continuity across page joins" is not a measurement of the key
-----------------------------------------------------------------------------------------------------
O4 leans on it to damp per-page/per-word reset readings (round36/O4-clue-coverage/RESULTS.md:23; untried.md "Cells
deliberately NOT ranked" H8; closed_no_operation.md H8xF1). The cited evidence, ELIMINATION-LEDGER.md:551-569 (recon
LP2-H2), is the adjacent-equal rate at the 54 joins: 0 observed. Expected 1.86 with no filter at joins, 0.36 with it:
P(0) = 0.156 vs 0.70, likelihood ratio 4.5 for *filter* continuity, and no bearing at all on whether the *key index*
restarts (a restart does not create doublets). What actually excludes same-key restarts is depth: R43-F3's cross-page
kappa, and my page-start check (first 8-160 runes of all page pairs: 3.45-3.57 % vs 6.2 % expected in depth, z <= 1.6).
Per-line: positions 2+ are flat; positions 0-1 are the known width-greedy line-break artefact (chi2 81.4 at line
position 0, cf. round18/L4-forcing/RESULTS.md:11) and must be masked in any R44-R1 per-line test. Different key per
page (page-number-seeded, per-section) remains open and is R44 R1 (tracked). Fix: annotate ELIMINATION-LEDGER:551-569.

--------------------------------------------
## Pointed question answers (not findings)
--------------------------------------------
Q1 O4 matrix. Rows: H1-H12 (out-of-book signed: the five 2016 clauses split H1-H5, H6 seek/beware 2016+2017, H7 2013
"key is all around you", H8 2012 "right in front of your eyes", H9 2013 knock on the sky, H10 2014 let the text guide
you / Self-Reliance riddle, H11 2014 ciphertexts, H12 2012-13 pointers), L1-L5, L7-L18 (LP1 sentences; there is no L6
row, numbering gap only — all 94 in-book sentences map to a row), S1-S5 structural. Columns F1 literal instruction, F2
number channel, F3 gematria on words, F4 word-as-key, F5 semantic, F6 positional, F7 cross-page/document, F8 physical,
F9 temporal, F10 acrostic/stego, F11 AN-END structure. Not rows at all: cleartext headings "Liber Primus" and
"Chapter I / Intus"; the unsigned Jan-2014 image text ("Epiphany is upon you. Your pilgrimage has begun..."); the 22
row=None entries are logistics plus the hash-block / JPEG / RSA / Interconnectedness payloads (data, not method).
No signed method sentence is missing. The ky_* files are duplicates of entries already present.
Q2 Compositions enumerated. R37 C1: U1 83 strings (5 clauses, 3 compositions, keyword string, 29 noun phrases, LP1
imperatives) x direct / SHA-256-CTR / PBKDF2-10000-salt-3301 x offsets 0-7 x sign x ks1/ks2; U2 16 LP1 number
schedules (word/line/sentence/cumulative x prime/index x mod 29/28) x additive or pointer-jump x page heads 0-2; U3
rho{position, rune offset, length} x M{29,28} x s 0-28 x sigma x {A1 per-word shift, A2 cumulative, A3 key-pointer
advance through the LP1 rune stream}. R38 C2: clauses 6/7, printed-line sums, lagged cipher-word/decoded-word pointers;
R38 C1: WordNet first-synset offset / Norvig rank; R39 C1 hypernym depth / lexname. Natural siblings not run (all in
the rows' own not_covered, so tracked): phi(p) channel; base keys other than the LP1 rune stream (LP2's own runes,
solved LP2 pages); pages beyond heads 0-2; free relation; direction-then-road order; lower-case / despaced hash forms;
schedules applied per ciphertext line. Shared conditional of all of them: additive mod-29 key under keyskip beam,
L=120 heads, EN_MODERN-only plants.
Q3 O3 near-miss 1354603465: sound. Family-wise P 0.20 at N=69,017; held-out windows 1-5 average 1.73 vs null median
2.19; decode has no words; plants read verbatim; R41 survivor-population bar puts it >= 2.3 below. KDF crosser
(round40/B3 ORACLE-PENDING.md; decode "FICNIFGEWWIAOORSNCEN...") : sound, decays with L, forward twin 1.96, below the
R41 bar of record. Both owner sign-offs are formalities.
Q4 Inhibitor audit remediations: landed — persona block (CLAUDE.md), oracle rewrite (verify_solution.py register-aware),
"Do NOT re-run" retitled, R11 rows, count check, HUMAN-ORACLE.md, panel plumbing (beam_v3 env override, R37 T1),
fetch --r36. NOT landed: SOLVERS-DOSSIER.md:9-13 and :79 still say "information-theoretically unsolvable without the
key ... the realistic path is external" with no banner (README "Start here" sends attackers there);
FINAL-SYNTHESIS.md:115 bottom line unannotated (listed as deferred in AUDIT-applied.md); research/DEAD_ENDS.md:200-201
"exhausted ... unsolvable" and :464 "Do not re-open the word-length excess"; no AN-END ledger row; A-03 and H-03 are
negatives with null coverage; three_conditionals present on 92/309 rows. Cheap reopen items the audit priced at
"minutes" and still unrun after seven rounds (all tracked): R19 ornament bands under 12 registers (PROBLEM.json:172);
R16-PRNG non-PHP generators under v3 (LEDGER R16-PRNG not_covered).
Q5 Geometry: R37 U8 control failed (0/5 plants separable); R38 I1 recognizer power 1.0 but FPR 0.16 (V2 0.58); R39 I1
page-matched null -> V2 unmeasurable (within-line FPR 0.30), V1/V3/V4 chance-level. A powered instrument needs a
generative page-matched null or a stroke classifier trained on turtle output, and a bounded rule space (4 rules x 58
pages today, moduli/steps unbounded). Tracked on MEASURED-CEILING; low prior; I would not spend on it.

## Out-of-partition observations (one line each)
- CONTRADICTION: analysis/round43/F3-hand-feasibility/KEY-LOCALIZATION.md:111 states "mean 3.51 runes/word, 536
  one-rune words"; the canonical parse gives 4.425 and 99 (that count treats line wraps as word boundaries — the same
  artefact FINAL-SYNTHESIS.md:9 records as a caught false positive).
- R26-C notes that ladder generators "that validate.py proves reproduce solved page 05" — page 05 is plaintext
  (shift 0); AN END is the phi(prime) page. Wording only.

## Checked and clean
N5/N4 numbers and alignment; O3 autopsy; KDF crosser; clue list completeness for signed text; R37 C1 control design
(independent encipherer, 6/6, 32/32, 24/24); panel/beam/screen robustness to unfolded orthography (probe); same-key
page/line/sentence restarts (depth tests flat); doublet anatomy (86, uniform by word position, page, block).
