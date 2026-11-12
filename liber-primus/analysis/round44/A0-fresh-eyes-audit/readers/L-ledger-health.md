# L-ledger-health — tracking-layer audit (fork L, 2026-11-12)

Scope: LEDGER.json (309 rows), ELIMINATION-LEDGER.md, MEASURED-CEILING.md, liber-primus/PICKUP-HERE.md, handoff/PARKED*.md,
analysis/handoff/*, PROBLEM.json, verify_solution.py, benchmark/, tests/, CI. Read-only on the repo. Helper dumps in this dir:
`L-open-rows.txt` (all never-run/open/partially-run/inconclusive rows), `L-reopens.txt` (reopens_if of all 197 closed rows),
`L-pytest.log`, `L-pytest-full.log`, `L-pubkey-6.txt`/`L-pubkey-14.txt` (7A35090F n,e).

## 1. Health (fresh clone, Python 3.13, numpy present, scipy absent; pytest installed into a scratch venv)
| check | result |
|---|---|
| `tests/validate.py` | ALL VALIDATIONS PASSED |
| `verify_solution.py --selftest` | PASS (EN_MODERN/LATIN/EN_NOVOWEL/GREEK; panel-R36 sha a0682f0c committed) |
| `analysis/handoff/validate_ledger.py` | 0 errors, **0 unsound negatives**, 167 warnings (>=11 "evidence path does not exist" = gitignored/absent), 25 notes |
| `round39/P1-measured-ceiling/check_ceiling.py` | PASS (58 claim lines, 125 rows cited) |
| CI pytest subset (5 files) | 29 passed, 7 skipped (all skips: gitignored stores) |
| `pytest benchmark/` | 9 passed |
| `pytest tests/ -m "not network"` | 31 passed, 6 skipped (R36/R35 stores, relikd images, R38 X4 rows absent) |
| documented full gate `pytest -q -m "not network"` (CLAUDE.md) | with `-x`: dies at collection. With `--continue-on-collection-errors`: **82 passed, 22 skipped, 11 failed, 3 collection errors**. Every failure = absent scipy (round19/I3, round19/T1, round30/A2) or gitignored artefact (`analysis/geometry/glyphs2.npz`, `data/keys/mabinogion.txt` -> round20 HITFN/P1, `round19/I2/models/panel.npz` -> round20/P2, round22/C). No logic failure. NB the R19 panel is declared unrebuildable (R35-P1), so this gate cannot be green off the owner's tree. |
| `analysis/handoff/check_consistency.py` (a CI step) | **FAIL at HEAD**: PAPER.md:282 and :443 say 299 ledger entries; LEDGER.json = 309 |
| CI "regenerate entry points, fail on drift" | **must fail at HEAD**: build_problem.py:160 copies LEDGER counts; committed PROBLEM.json has the 299-row counts (neg 99/meas 82/partial 25) vs ledger 107/85/24. PROBLEM.json last touched 14b9e4d (2026-11-02). So CI is red on the R42/R43 closeout commits even though the closeout says "full gate green". |

## 2. Ranked findings

### F1 [INSTRUMENT-DEFECT] The oracle FAILs a correct *continuous* keystream
- `verify_solution.py:243-262` decodes every page with the same K at `o=0`; `:381` prints "key offset o=0 (key restarts at each page)";
  `:169` MAX_LEN=240; `segments()[:6]`; `decide()` needs >=2 pages under one relation; selftest (`:336-347`) plants ONLY per-page restart;
  PROBLEM.json acceptance: "key offset 0 per page".
- Demonstration with the oracle's own functions (panel-R36, held-out EN_MODERN text, random K, `_encipher` = keyskip1 supp 0.83):
  one continuous key over two consecutive 240-rune pages -> page0 pmax 27.42 (bar 4.64) clears, page1 pmax 2.97 fails -> `decide -> (False, None)`.
  Same text with the key restarted per page -> 27.42 / 28.80 -> PASS.
- Why it matters: the project's primary hypothesis (seed-derived full-length keystream; Campaign IV "keystream continuous across page joins";
  D-01 "no per-line scope") is exactly the construction the oracle rejects. A true bash/PHP/MT seed would clear page 0 only -> VERDICT FAIL.
  HUMAN-ORACLE.md asks for the oracle output in every bundle; README calls it "The oracle".
- Also not acceptable by design: per-page distinct keys (one K only); any non-additive solution (transposition, codebook, homophonic) ->
  `--plaintext` = NOT-ADJUDICABLE; sign +1 only by negating K; F-interrupter key-holds (advance 0) are not a relation.
- The 2-page same-key rule is the anti-forgery device (K = C - P_fake cannot satisfy two pages). A continuous mode needs a different guard
  (e.g. `--key-module` with a description-length cap), otherwise any plaintext is forgeable.
- Cost: 1-2 h (continuous mode: page k at o = sum(prev lengths) + searched drift window; add a continuous plant to --selftest and tests).

### F2 [LOGIC-GAP, doctrine R4] The per-second wall-clock seed window was never swept under the repaired instrument
- Covered at arbitrary seconds: bash 3.2 (pid+time, 2012-01..2014-06) and Py2.7 MT (`pair` full 2^32; `exact` cursor to 2.24e9).
- NOT covered: glibc srandom/rand, PHP mt_rand, Perl, TeX, MSVC/Java/.NET. Their time coverage = unix midnights, YYYYMMDD, top-of-hour
  2011-2015, 433 seedprior entries (`round32/B2-php-mtrand/sweep.py:20-43`; R32-B3 row not_covered: "timestamp jitter around the listed
  instants; seconds not on the list"). PHP tier (b) is a uniform random draw of 2^32 (`sweep.py:95`), i.e. ~1 % of any window.
- Round 8 did sweep every second 2011-2015 x 10 generators (2.52e9) but with an interrupter-only decoder (`seed_sweep/sweep.c:9,244`) and the
  old English score: zero measured power under key-skip (B-21 partially-run, PARKED P-2).
- MEASURED-CEILING section 3 files glibc/Perl/TeX as "flat tails ... a C or GPU port"; no doc in rounds 32-44 names a per-second tier
  (grep: per-second|every second|unix-second -> only PARKED.md:141,312). R44's deferred "S2 PHP retry" continues the uniform tier.
- Size: 2013-10-01 -> 2014-04-02 08:33:19 UTC = 1.59e7 seeds per generator cell; all of 2011-01 -> 2014-04 = 1.0e8, i.e. the scale of the
  bash orbit (7.76e7) that was run three times. Hours per generator with pf_v4_12; enumerable; plantable.

### F3 [UNDISCHARGED, G-09 reopens_if met] Author-infrastructure timestamps are not in the seed prior
- R43 F5-stored/RESULTS-irc.md:63 onion-7 index thttpd `Last-Modified Wed, 02 Apr 2014 08:33:19 GMT` (= 1396427599; "already in our record");
  :83 Jan-11-2014 status hex `Last-Modified Sat, 11 Jan 2014 22:07:12 GMT` (= 1389478032).
- Neither integer occurs anywhere in the repo (grep). seedprior20.json (433 candidates) nearest: 1396396800, 1396425600, 1396428540, 1396428590-92.
- G-09 reopens_if: "an authenticated onion post time or a dated archive capture is recovered, which would add author_infrastructure entries".
- Cost: minutes to add both (+/- a window) to the prior-dense core tier of every generator; natural right edge for F2's window.

### F4 [INSTRUMENT-DEFECT in the plan of record] R44-P4 would reuse a rigid, English-only harness
- round44/CAMPAIGN-PLAN.md P4 and round43/X0-firewall/ADJUDICATION.md:64: "reuse the R28-L2 keytest harness verbatim (payload analogue already validated)".
- `analysis/round28/L2/keysweep.py:100-106`: `p = (c + sign*stream[i]) % N` position by position, scored by `SC.score_norm` (English quadgrams);
  plant `:119-132`: `cipher = (p + key) % N` with NO anti-repeat filter. Row R28-L2 not_covered admits "no rejection-loop transition model".
  Its "plant power 1.000" is for an unfiltered English plant; under key-skip a 236-rune page loses alignment after ~35 runes (doctrine mechanic 3).
- Consequence beyond P4: "payload as key" (X0 item 12, CITED) rests on R28-L2 (rigid) + B-05 (keyskip1 beam, English -5.5 bar; R40-B3 not_covered:
  "B-05 payload-as-seed"). The book's one distinguished 256-byte object has never been run as a direct per-page key or PRF seed under beam_v3 + panel-R36
  (only 7 payload-derived seeds inside the B-04/KDF grids). Cost: minutes to 1 h (128 variants x 55 pages x 3 relations; 70,680 B-05 configs).

### F5 [CONTRADICTION] R43-F3's premise vs the repo's measured production facts
- F3 TOOLKIT.md:8 "the book is hand-illuminated. Every ciphertext rune ... was drawn by a human ... without a machine in the loop at write time";
  :117 "The lapses are the human signature"; ENUMERATION.md:155 "precisely a hand-execution signature. No machine-generated OTP, no PRNG ...".
  F3 ran firewalled (TOOLKIT.md:6 "ledger and findings docs were NOT read").
- Against: G-01/R18-L1 (Ghostscript -> ImageMagick render of a typeset document), analysis/README.md:50 (identical glyph bitmaps, median NN
  Hamming 0.0000), T1-02 ("Y is typeset as two components"), D-01 (source of randomness MACHINE at >=0.99 power; "a person did the writing" untouched).
- The 17-sigma blind-pad exclusion is just the doublet deficit and stands. The hand-hours feasibility ranking (e.g. ENUMERATION.md:108 "pi in base 29
  infeasible by hand") is not a valid exclusion for a typeset book. README "The creator" paragraph still says "by hand" while its own Round 17
  note says machine. X0/X1 did not diff F3's premise against G-01/R8. F3 has no ledger row.

### F6 [CONTRADICTION / tracking gap] The ledger no longer holds the current state
- No rows for R43 F1, F2, F3, F5a, F5b, X0, X1. Zero rows mention red ink (except an aside in T1-02), quote spans, punctuation identity,
  hand-feasibility; the p27/p54 7-gram and per-page resets exist only as not_covered text. README's "what's open" query
  (`select(.status=="never-run")`) returns 10 rows, none of them in the Round 44 plan.
- Stale rows (later work exists, row not updated/superseded): R36-O2 (partially-run; R43-F5a ran the Wayback leg), R35-S1-S2-WINDOW and
  R39-S1-S2-WINDOWS (never-run; S2 resumed R36/R38/R42), R41-C1-*-VERIFIED x4 and R40-C1-INCONCLUSIVE-R35/R36 (R42-C1/C2/C3 ran them),
  G4-TEX-RNG ("ZERO decodes" vs R26-A first fire), B-03 (PHP "untested"), R20-SRESCOPE-B04 (its reopen was executed by R40-B3-B04-REDECODE),
  A-02/B-13 (see F11), B-01.
- C-CANON-PAYLOAD-3BYTES: row + PICKUP-HERE.md:191,638-644 present the promotion as an open owner decision ("status open" - it is `measured`),
  but `analysis/pp49_51/canon_256.bin` was overwritten with the corrected bytes in commit 26c4446 (2026-10-30; sha 3b9b07d9 == payload_resolved.bin).
  Side effect: R28-L2 `keysweep.py` base 0 ("canon majority") now equals base 1.
- Ledger-open rows that appear in NEITHER PICKUP (current part) NOR the R44 plan NOR ceiling section 3 NOR PARKED (by id):
  B-21, B-01, B-03, C-01, D-02, I-02, I-04, J-01, B-08, B-11, B-09, B-06, B-07, B-14, B-15, B-17, B-18, B-19, B-20, B-22, B-24, G4-TEX-RNG,
  G4-ALLRUNES-NC5, I1-09, R25-COMPUTE-TAIL-CHUNK1, R33-O1-GS-RENDER-COMPARE, R37-C3-U6A-N3. 25 recon rows have no reopens_if at all (validator NOTES).

### F7 [CONTRADICTION] MEASURED-CEILING.md is stale against Rounds 41-43
- Header: "290 rows"; 0 mentions of Round 42. Line 58 + section 3: Py2.7 exact "47.95 %", "recover window 2 before 2026-11-07" (R42-S1: 52.05 %, recovered).
  Lines 53, 107: bash 3.2 "unverified against a binary" (R42-S3 verified; ledger row is now `negative`). Section 3: "R14 and R15 ... re-scorable, not run"
  (R41-C1 ran both), "supply the R35 key texts, the R36 dated pad data" (R42-C1/C2 ran), line 114 "p27:93 unresolved" (README:266 "machine-resolved to U in R33 B2").
- check_ceiling.py passes because it verifies citations and pins, not currency. README says "CI checks every claim on that page against LEDGER.json (309 rows)".
- The page never names F-interrupter key-holds as an unrepresented construction (grep "interrupter": 0 hits).

### F8 [CONTRADICTION] PROBLEM.json (front door #1) is stale
- counts_by_status = 299 rows; open_or_untested still lists A-03, F-01 and D-01 as open (all `negative` since R16/R17; F-01 re-scored R40-C1);
  "B-04 ... v3 re-decode of the sources not run" and "KDF ... re-decode not run" (R40-B3 did both).
- measured_statistics.note: "~0.66 % against a >=1.38 % plaintext-independent floor for running keys. Everything in the verdict rests on it" -
  contradicted by B-16 / R18-L2-A ("no doublet-based statistic has discriminating power over key type") and by R43-F3's different floor (1.86 %).

### F9 [UNDISCHARGED] Marsaglia: reopen condition met since Round 19
- R19-C2-MARSAGLIA-COST reopens_if "I1 and I2 gates PASS - at which point the 679 remaining units should be run"; R20-SMARS-SCAFFOLDED never-run:
  "Nothing blocks it ... simply unrun" (~21 CPU-h; needs the 634 MB refetch). 24 rounds later it is in ceiling section 3 only, not in PICKUP or R44.

### F10 [UNDISCHARGED conflict of record + a free structural gate]
- round19/T3/RESULTS.md:112-126: R18 L2-A vs L7-C.2 disagree on whether the doublet-floor argument is load-bearing; "Flagged for R1"; no other
  file mentions it (grep). PROBLEM.json still presents the floor as the verdict's basis (F8).
- Independent of the filter, a letters-only natural-language running key over linguistic plaintext leaves a monogram signature: IoC*29-1 = 0.046
  (English/English, computed here from data/keys/self_reliance.txt; 0.017-0.084 for the other corpora) -> predicted monogram chi2 ~ 618 vs
  observed 26.4 on 28 df (~79 sigma). R43-F3 ENUMERATION.md:109 has the same gate (IoC 1.076, "dead"). The tracking layer never applied it:
  R12-C2 (never-run), R26-B "large pages un-swept", R42-C1's reopen and the R44-deferred "10-keytext hash-pinned refetch" are zero-information
  for linguistic plaintext, and the panel cannot see non-linguistic plaintext. Drop them from the queue (cost 0).

### F11 [UNDISCHARGED finite objects]
- T1-04/T1-05 reopens_if "the 113 unaligned positions are adjudicated": exists only in round19/T1/RESULTS.md:475-486 (where a canon insertion
  or deletion would hide); no later doc mentions it.
- A-02/B-13 (450 O/A/AE calls) are `partially-run` with null coverage; ceiling:114 says "never decided per instance"; analysis/README.md:59 and
  ELIMINATION-LEDGER.md:210 say "T1/T2/T3 upheld canon 450/450". One of the two is wrong.
- R22-D reopen (per-page figural-motif integer sequence) never catalogued; overlaps R44 P5.

### F12 [reopens_if premise false; discharged here as a spot check]
- R43-F6-ONION-BLOB-STRUCTURE: "signature verification against 7A35090F (modulus not in repo)". It is in the repo:
  `corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` (v4 RSA-4096, e=65537, primary + subkey; also
  archive/.../campaign15/cicada_pubkey.asc). Spot check (unregistered, not a lane): blob^e mod n for the three sha-verified blobs (from the
  committed wiki exports; sha prefixes 4f1cef87/05acf0d8/d8c0f83c), both keys, both byte orders -> no PKCS#1 v1.5 structure. Expected by size:
  a 2048-bit blob cannot be a 4096-bit signature. The live question is an unknown 2048-bit modulus, not 7A35090F.

## 3. Ledger census
Status counts: negative 107, measured 85, audit 42, partially-run 24, open 18, inconclusive 13, never-run 10, superseded 5, eliminated 5.
Full per-row dump (hypothesis / coverage / not_covered / reopens_if): `L-open-rows.txt`.

Cheapest finite undone items (ledger-open or legacy-only), ranked by (chance to change belief) x cheapness:
1. Oracle continuous mode + plant (F1) - 1-2 h - instrument.
2. Payload as direct per-page key and as PRF seed under beam_v3 + panel-R36 (F4; rows R28-L2, B-05) - minutes to 1 h.
3. Add the two server timestamps to the seed prior and re-run the prior-dense core tiers (F3) - minutes.
4. Per-second window tier for glibc / PHP / Perl / TeX (F2) - hours per generator - enumerable.
5. D-04 non-additive ciphertext-feedback sweep on all 55 pages (3 of 55 run) and R12-C1 (k-history feedback; English quadgram only; pt/mix
   seeds eq0..eq28 only) under the register panel - 1-3 h. The only cipher class that makes the doublet deficit intrinsic.
6. R19-FINITE-ORNAMENT-REGISTER: 74 bands under 12 registers - minutes (low prior, underpowered at band length).
7. T1-05's 113 unaligned positions - finite, human/reader.
8. G4-TEX-RNG three Lehmer families (row's own estimate ~18 h wall, pre-pf_v4) and Perl 2^32.
9. Marsaglia 679 units - ~21 CPU-h + refetch (F9).
10. D-03 homophonic-downward search (never coded), D-02 PPM-order test vs matched controls - hours each.
11. H-01 onion HTTP/server-status anomalies (never-run), C-01, B-14 - OSINT/unbounded.

## 4. reopens_if audit (all 197 negative/eliminated/measured rows read; see `L-reopens.txt`)
Met but not re-run / not restated: R19-C2-MARSAGLIA-COST (F9); G-09 (F3); R43-F6-ONION-BLOB-STRUCTURE (F12, premise false);
R20-SRESCOPE-B04-SURVIVORS (executed by R40-B3, row not updated); C-CANON-PAYLOAD-3BYTES (executed on disk, row/PICKUP not updated);
T1-04/T1-05 (113 positions; p27:93 half discharged by R33-B2); T3-PROPAGATION-MAP (conflict + "re-run under I1's decoder" never done);
A-06 / R19-FINITE-ORNAMENT-REGISTER ((ii)/(a): a multi-register scorer beyond nine now exists; bands not re-read);
R24-C1(-EXT) (Hebrew/Norse LMs now exist; that Py2.7 prior slice was never re-adjudicated under panel-R36 - tracked in the ceiling as the 44 % R19-gated mass);
L7-B-BEAM-ENVELOPE ("an interrupter ... advanced the key independently" - interrupter holds still unrepresented; bounded below).
Checked, NOT triggered: R12-D2 / D-01 / R18-L2-A/B (issue #12 changed separators only; n=12,956, 86 doublets intact); A-04 / T1-01 / T1-03 /
R28-L2 / R30-A2 "higher-resolution master" (R43-F5a's "masters" are the same 2400x3600 files; 56/56 digest match); R24-C8 (R43 recovered one
index-level Last-Modified, not per-page timestamps); G-02 (no new signed block in R43-F5b section 2b); E-01 (onion blobs tested R43-F6);
R11-N1..S2 (discharged by R37-C3 rows); R22-A (discharged by R23-A2); R20-P1 (superseded by pf_v4).

## 5. Legacy-only decode rows (no re-run under panel-R36 + beam_v3), ranked by prior x cheapness
1. R28-L2 decode half (rigid, English quadgram, unfiltered plant) and B-05 (keyskip1 beam, English, fixed -5.5) - payload keys - minutes to 1 h.
2. R12-C1 (feedback/autokey; English quadgram, no panel) and D-04 (3/55 pages) - 1-3 h.
3. R16-PRNG (.NET, ISAAC, BBS, LFSR32, Geffe: stored decoded heads re-scored only; no ciphertext/key pair kept) - fold into F2's window tier.
4. R19-FINITE-ORNAMENT-REGISTER (nine registers) - minutes.
5. R20-SG3 / R24-C2 / R24-C2-EXT / R26-A (Py2.7 prior slice, skip generators, Perl/TeX prior slice: Round 19 nine-register panel; no Greek/Hebrew/Norse) - hours.
6. B-02 dense offsets (2.04e9, legacy English) and B-13-MARSAGLIA (77/756 units, legacy English) - CPU-days; low prior.
7. R18-L2-DRIFT-LADDER, R22-B, R22-D - non-decode or superseded; leave.

## 6. Kill-checks I ran against my own candidates
- "R43-F6 used the uncorrected payload" - false: canon_256.bin already equals payload_resolved.bin.
- "Unmodelled F-interrupters void the sweeps" - bounded: 458 F observed vs 446.8 expected under uniform -> ~12 +/- 21 literal-F interrupters
  (<= ~55 at 2 sigma, <= 0.42 %/rune) -> P(>=1 hold in a 120-rune head) <= ~40 % at the 2-sigma bound, ~10 % at the point estimate. A conditional, not a void.
- "Value-rewrite (M2) is uncovered by keyskip decoders" - false: the zero-skip path recovers ~97 %.
- "sig^e mod n on the onion blobs could be informative" - no: size mismatch makes it null a priori (confirmed).
