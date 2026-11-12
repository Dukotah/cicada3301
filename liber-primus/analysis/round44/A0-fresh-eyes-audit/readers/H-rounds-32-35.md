# Fork H — rounds 32-35 (the instrument of record: beam_v3 / pf_v4 / bars_v3) — fresh-eyes audit notes
_2026-11-12. Read-only on the repo. Paths relative to `liber-primus/` unless noted. Probes (my own scripts, this dir):
`H_plant_probe.py`, `H_hold_probe.py`, `H_oracle_continuous.py`, `H_gate240_probe.py`. All probes hand the CORRECT key to the
repo's own instrument (`verify_solution.judge_register` = beam_v3 panel_max + panel-R36 + bars_v3) with ciphertext produced by
an independent forward encipherer of mine. Total compute < 1 min._

## 0. What the instrument of record assumes (pointed Q1) — read from code
`analysis/round33/I1-register-aware-beam/beam_v3.py`
- Cipher equation: `p = (C[i] + sign*K[acc]) % 29`, default `sign=-1` (lines 168, 179, 249) => C = P + K mod 29, constant 0, no reflection.
- Key pointer only moves FORWARD by >= 1 per rune: `base = pa + 1; for dsk in range(0, ms1)` (184-188). No zero-advance (key hold), no backward move.
- keyskip1 (`beam_v2.ADVANCE[1]`, round32/I1-skipbytwo-decoder/beam_v2.py:34-38: max_skip 8, max_free 0): every skipped key value must
  equal the value that would have reproduced `C[i-1]` (`vmap`, lines 180, 193-211). keyskip2: skips come in pairs, first of each pair
  doublet-consistent, second unconstrained (192-204). free: `permissive`, max_skip 40, <= 2 unexplained advances PER TRANSITION, penalty lam_u=4 (U units), start_slack 2.
- Segment handling: `_drive(C, K, ..., o)` knows nothing about pages. The caller fixes `o` and passes a slice. Orbit sweeps decode
  `U[:120]` (screen) and `U[:240]` (gate) of the flattened stream = page 0 only (page 0 has 262 runes) with `o=0`
  (round35/B1-bash-orbit-pfv4/PREREG.md "sign -1, o=0, C[0]-aligned"; sweep.py:51,58). c_prev does not exist at i=0.
- F-interrupters: not modelled anywhere in beam_v3 / pf_v4 (grep: 0 hits in both files).
- Search score: `panel_max` = max over registers of U_r = sum of per-register z-normalised TRIGRAM increments over 29 rune indices
  (`W[r1*841 + r2*29 + p]`, line 112) — spaceless: the 2,766 cleartext word separators are not used by screen, beam or adjudicator.
- beam_w 400, tau 0.
`analysis/round35/I1-skip-tolerant-screen/pf_v4.py`: `D[t][s] = (C[t] - K[t + a*s]) % 29` (line 21), s nondecreasing, s_0 = 0, s <= k=2,
a in {1,2}; i.e. draw t (+ <=2 forward skips, not required to be doublet-consistent) is applied to rune t of `C[:24]` of page 0. Thresholds are
calibrated to that one head (RESULTS "Caveats").
`round32/B1-bash-random/pf.py:4-18` `heads`: m CONSECUTIVE generator outputs, `(s & 32767) % 29` (stride 1, no warm-up).
Plant functions (`beam_v2.py:54-91`, `round32/B1 common.py enc_pair/enc_exact`, `sk.encipher_keyskip`, `round19/I1/constructions.py`) are
independent FORWARD encipherers (not inversions of the decoder) — good — but every one shares: C=(P+K)%29, one draw per rune, coin from a
separate Python RNG at supp=0.83, key from index 0 at the first plaintext rune, no interrupter, corpus-window plaintext.

Constructions it cannot represent (by reading + probes): any constant offset or reflection in the combiner; zero-advance (literal F);
key consumed by non-rune tokens; stride >= 2; resets; advance >= 4 (R33-I2); > 2 unexplained advances per rune; anything that is not a
continuous forward walk on ONE key list.

## 1. FINDINGS (ranked)

### F1 [INSTRUMENT-DEFECT] THE ORACLE fails a correct key when the keystream is continuous across pages
`verify_solution.py:243-269` `judge_register(K, pages, ..., o=0)` decodes EVERY page from `K[0]`; `decide` (272-283) needs >= 2 pages under one
relation. Stated only in its own output (`:489` "key offset 0 per page", `:544` "restarting at each page (o=0)") and `PROBLEM.json:115`.
The selftest (`:303-318`) plants each page from offset 0, so CI can never see this. But the project's generative model, every orbit sweep
("C[0]-aligned" continuous stream), R18-L2's 373.6-draw drift and R43-F3 "never rewound" (KEY-LOCALIZATION.md:50,105) all say the stream is
continuous. Probe `H_oracle_continuous.py` (6 pages with the real first six page lengths, EN_MODERN, keyskip1, correct key):
```
CONTINUOUS keystream across pages:  keyskip1 1/6 pages clear  pmax by page [24.3, 3.3, 2.6, 2.1, 1.9, 3.1]   VERDICT: FAIL
key RESTARTS at each page:          keyskip1 6/6 pages clear  pmax [24.3, 23.4, 25.3, 25.8, 26.6, 23.3]      VERDICT: PASS
```
Why it matters: the front-door judge (README item 2, AGENTS.md, HUMAN-ORACLE two-page rule) rejects exactly the kind of hit the sweeps hunt;
an outside solver with the true key gets "VERDICT: FAIL". Not tracked as a defect anywhere (grep "restarting at each page|offset 0 per page":
only the two source lines + PROBLEM.json). Fix: decode pages sequentially with `o = ptr_end` of the previous page (full-page decode; `free`
start_slack for the join) OR accept either alignment; add a continuous-key plant to `--selftest`. Cost: ~1 hour, finite.
Irony worth recording: the oracle is the only instrument that implements reset_per_page; no sweep does.

### F2 [SHARED-PREMISE] The combiner is an unnamed 4th conditional: C = P + K + 0 exactly
Every post-R19 generator-orbit lane (R32-B1/B2/B3, R34-B1, R35-B1, R36-B1/B2, R37-I2, R40-B1, S2) fixes `sign -1`, no reflection, constant 0.
Lane docs list it once as "sign +1, reversed/atbash orientation" (round32/B1-bash-random/PREREG.md:21, RESULTS.md:75;
round32/B2-php-mtrand/PREREG.md:12); R40-B2 later ran sign +1 for bash 4.2 LP64 only. `MEASURED-CEILING.md` section 3 names "sign +1 on most
rows" and "mod-29 additive stream" but has 0 occurrences of atbash/Beaufort/constant offset. Probe `H_plant_probe.py` (correct key, L=120,
3 windows; bars N=1: 4.0/3.99/7.94; sweep-scale bars are 9.3-10.5):
```
baseline keyskip1            ks1 pmax 20.7/19.5/17.9 rec 1.00   free 20.7/19.5/17.9
C = P + K + 1 (off-by-one)   ks1 3.3/3.9/3.9 rec 0.01-0.02      ks2 <=2.9   free 5.1/6.2/4.3   -> noise
Beaufort C = K - P           ks1 2.4/3.0/2.3 rec 0.03-0.05      free 3.4/6.3/6.0               -> noise
Atbash-then-add C=(28-P)+K   ks1 2.8/2.9/2.9 rec 0.00-0.06      free 6.0/5.6/4.4               -> noise
```
House-style prior (doctrine R4, from held artifacts): of the 5 enciphered solved sections 2 use Atbash, one adds a +3 shift, AN END shifts
"down" (docs/SOLVED-PAGES-AND-INTERRUPTERS.md table). A 1-based rune table or `RANDOM % 29 + 1` gives a constant offset.
Algebra: with D1 = C-K and D2 = C+K the four classes are D1+a, D2+a, a-D1, a-D2; the skip/doublet transition structure is identical inside
a sign class, only the LM sees the difference. So 116 combiner cells exist; orbits have 1 (bash 4.2 LP64: 2).
Note R40-B3 already ran sign x atbash x direction under panel-R36 for the B-04 hash dictionary — the harness idea exists, it was never
pointed at the orbits, and constants a != 0 appear nowhere except the single near-miss seed grid (R36-O3).
Cheap discharge: a shift-and-reflection-invariant head screen (LM on first differences of the decoded head, both polarities, both signs)
covers all 116 cells at ~4 screen-costs; needs one plant envelope first (power will be lower than the trigram screen; measure it).
Brute force alternative: 58x the screen (bash: ~23 min/ABI/cell => ~45 laptop-hours per ABI). Finite.

### F3 [SHARED-PREMISE] Alignment: "draw t meets rune t" (+ rejections) and nothing else
(a) separators consume no key; (b) stride 1; (c) no warm-up; (d) the stream starts at page 0 rune 0; (e) forward order.
Measured anywhere: (c) k = 1,2,3 on bash 4.2 LP64 only (R40-B2; 4.7 % of its own 116-cell offset axis); everything else zero in the
modern instrument (pre-R19 sweeps had "2 directions" / "55 per-page restarts" but with the English-only rigid/legacy decoder).
Probe: key burned at every word boundary (42 burns in 120 runes), correct key: ks1 pmax 2.0/0.4/1.7, ks2 2.4/0.9/2.2, free 6.1/5.0/6.4
— noise under all three relations. Because separators are CLEARTEXT (2,766 '-', 181 '.', 604 '/'), "key index counts tokens" variants are
deterministic re-alignments (one extra orbit cell each), not a beam problem. Stride-2 (one extra draw per rune: a per-rune coin, a per-rune
`RANDOM` elsewhere in the loop) turns minstd/MT into a different stream entirely — unrepresented for every generator; grep "stride" in rounds
32-43 finds only pad byte-strides. Cost: one orbit screen per variant (~23 min per ABI for bash at 56.6k heads/s).
What fraction of sweeps would miss a correct in-orbit seed (pointed Q2): ALL of them, for (a) non-rune tokens consuming key, (b) reversed
order, (c) warm-up > 3 (or any warm-up outside bash 4.2 LP64), (d) a stream that began before page 0, stride >= 2, any combiner cell of F2.
NOT missed: per-page RESEED of page 0 itself (page 0's own seed is still screened) — but then the other 54 page heads are 54 further
independent targets that no lane has ever screened (only C[:24] of page 0 is ever used).

### F4 [LOGIC-GAP, out of partition but it feeds Round 44 R1] the "repeated 7-gram p27:28 / p54:70, p ~ 0.5 %" is not what it is said to be
round43/F3-hand-feasibility/KEY-LOCALIZATION.md:107-110; round43/X0-firewall/ADJUDICATION.md:27,72; round43/SYNTHESIS.md:97;
round44/CAMPAIGN-PLAN.md lane R1. Independent scan of the canonical stream (lpdata.py, sha-verified):
- the quoted runes `ᛉᛚᛒᚱᛋᚳᛋ` occur 0 times in all 57 segments;
- inside the 12,956 unsolved runes there is NO repeated 7-gram; there is one repeated 6-gram, D-J-U-B-E-I (idx 23,11,1,17,18,10), at
  page 27 offset 28 and page 54 offsets 70-75 = the LAST six runes of the unsolved text (page 54 has 76 runes);
- the "7th rune" (AE) of the second occurrence is the FIRST rune of the solved AN END page (flat index 12956; plaintext A + phi(2)=1), i.e.
  another cipher with a known key. Expected number of repeated 6-grams by chance = C(12956,2)/29^6 = 0.14 (p ~ 0.13), not 0.005.
- the in-page offsets differ (28 vs 70), so it cannot be an equal-offset anchor for a per-page reset anyway.
Cost: zero — strike it before R1's PREREG is written.

### F5 [LOGIC-GAP] same-key "resets" are already dead by a key-free depth statistic; R33-I2 / X0 / R44-R1 still carry them as open
round33/I2-construction-axis/RESULTS.md section 2 "reset_per_page and reset_per_line are UNREPRESENTED by every relation"; X0 ADJUDICATION.md:27
REOPEN; R44 R1 "decoder must represent resets". If the SAME keystream restarted at each unit, aligned columns would be plaintext in depth
(kappa*29 ~ 1.6-1.8 for any natural language until skip drift decays it: alignment survives (1-0.0286)^(2c)). Measured (my script, canonical stream):
```
page  55 units  first 10 cols kappa*29 1.033 (z +0.76)   first 20: 1.001   first 40: 1.034     -> expected ~1.65: excluded > 14 sigma
line  594 units col 2: 1.006  col 3: 0.986  col 4: 1.002  col 5: 1.001 (sd ~0.013)             -> excluded > 40 sigma
sentence 217 units first 5/10/20: 1.009 / 1.017 / 1.010 ;  word 2,928 units first 1/2/3/5: 0.9985 / 0.998 / 0.998 / 0.9975
(line cols 0-1 are 1.090 / 1.029: the known greedy-line-breaker glyph-width bias, R18-L4 RESULTS.md:11-16 — re-derived independently,
chi2 81.4 at col 0, line-END flat 26.6; NOT a cipher signal)
```
R43-F3 itself measured the page version (KEY-LOCALIZATION.md:50 "cross-page kappa (same offset) 0.0348 vs 0.0345", "never rewound") — the
conclusion was not propagated to X0 item 4 or to R44 R1. What survives is only reset-to-a-DIFFERENT-position / per-unit reseed, which a
reset-aware decoder cannot exploit from one key; for generator orbits it means "screen every page head", not "represent resets".
Cost: zero compute left; re-scope R1.

### F6 [SHARED-PREMISE, quantified; tracked only as a word] literal-F key holds
Solved-page rule (docs/SOLVED-PAGES-AND-INTERRUPTERS.md "The ᚠ interrupter rule"; AN END in the same onion-7 release uses it with a STREAM
key): a literal F consumes no key. beam_v3 / pf_v4 cannot hold (pointer always +>=1). Tracked: the word "interrupters" in R33-I1 / R33-B3
`not_covered` and L7-B `reopens_if`; 0 occurrences in MEASURED-CEILING.md and liber-primus/PICKUP-HERE.md; never quantified.
Quantification (mine): ciphertext F count 458 vs 446.8 uniform => at most ~47 literal F book-wide (95 %), so the full solved-page convention
(every plaintext F literal, ~260-330 expected) is excluded at > 6 sigma, a low rate (<= ~10 % of ciphertext F) is not. Page-0 head has F at
index 7 and 17. Probe `H_hold_probe.py` (40 windows, one hold at index 4..20, correct key): the L=120 beam self-heals because the next true
rejection (+1) cancels the -1 (pmax >= 9.4 in 95 % under keyskip1, 85 % free; recovery >= 0.9 in 50 %) — so the binding loss is the 24-rune
screen (a hold at index 7 leaves 16 misaligned runes unless a resync lands inside; not measured through pf_v4_12 — plumbing > my budget).
Exposure <= ~10-19 % of true-key mass. Fix: allow advance 0 only where C_t = F in the screen DP and the beam (2 positions in the real
head); minutes of code + a plant envelope.

### F7 [NOTE on pointed Q4] p_keep is a fitted constant; nothing derives it; the fit itself is slightly off
- Every plant uses supp = 0.83 with a coin from a separate RNG. R33-I2 RESULTS section 1 gives the analytic rate q(1-s)/(1-qs) = 0.6035 % at
  s = 0.83 vs LP2 0.664 % ("1.2 sd above all seven") and stops. Solving for s: s = 0.812 (86/12,901 within-page pairs; 1-sigma 0.791-0.833).
- The Round 18 skip_by_two "prior" was 2 doublets in 239 pairs (0.84 %); at full length every output-side filter gives ~0.60 %
  (R33-I2, confirmed by R33-X1 row 5b and struck by R34-X1). Left standing: "an output-side soft rejection at s ~ 0.81, mechanism unknown".
- Only one lane ever tied the coin to a code idiom: `round19/I1/constructions.py::enc_coin_from_key` (coin = next key draw < round(0.83*29)=24,
  so 24/29 by construction). Same-stream coins are the natural script idiom (`RANDOM % 5` -> 0.800, `RANDOM % 6` -> 0.833, 24/29 -> 0.828);
  all sit inside 1 sigma of 0.812 — the ciphertext cannot rank them.
- What the ciphertext CAN exclude (checked): rewrite-by-small-shift idioms (c+1, c + RANDOM%m): the ~360 displaced doublets would pile onto
  deltas 1..m-1 (+70-90 each); nonzero-delta histogram is flat there (457, 503, 436, 435, 445 vs mean 457.7). Doublets concentrated on any
  natural position set (prime page/line/word index, parity, word-initial): no (|z| <= 2.4 over 14 tests); dispersion index 1.05 (Poisson).
- Consequence for coverage (probe `H_gate240_probe.py`): under a same-stream coin the transitions are skip_by_two for rejections plus ONE lone
  burn after each KEPT doublet. Real page 0 has its first kept doublets at index 122 and 207, so keyskip2 is exact on the L=120 window and
  the L=240 gate still clears (20/20 plants shaped like page 0: L120 median pmax 18.9, L240 min 14.2, recovery 0.70). So the orbit keyskip2
  cells DO cover the natural same-stream-coin idiom for page 0 — a positive worth writing down; on a page with an early kept doublet they
  would not (H_plant_probe: keyskip2 recovery 1.00 / 0.60 / 0.09; free 0.94-1.00).

### Tail (tidiness)
- KNOWLEDGE.json:266 still says the transcription is "verified four independent ways ... NOT the blocker" without the LP2-typeface-only
  scope R32-X1 #4 put everywhere else.
- 3 negatives have empty `not_covered` (R43-F6-PAYLOAD-VS-ONION-BLOBS, R43-F6-ONION-BLOB-STRUCTURE, R43-F6-PAGE56-HASH-AS-KEY); the R33-X1
  validator warning evidently does not fail CI.
- B-10 / R29-L1 OutGuess 0.2-vs-0.4 mismatch (R32-X1 #7) is still open but honestly recorded in R29-L1 `not_covered`.
- R34-I1's lp2 null draws C as a SHUFFLE of LP2 (run_null.py:28-34: doublets back at 3.4 %); superseded by R41-I1's survivor refit.

## 2. Pointed Q3 — R33-I2 `unrepresented` list, verbatim, and what has been represented since
RESULTS.md section 2 "Reading": "skip_by_3 is REPRESENTED: `free` recovers it in EN_MODERN, v3+free in NOVOWEL. No relation earned. /
skip_by_4 and skip_by_5 are UNREPRESENTED (best cell 0.83 at L=120 MODERN; 0.33-0.56 at page length). / reset_per_page and reset_per_line
are UNREPRESENTED by every relation (<= 0.51), yet recovered (1.00 MODERN) by segmenting at the known boundary and running relation 1."
section 5 not_covered: "Reset to a nonzero/permuted offset; resets combined with skip_by_k or free drift; supp != 0.83; k > 5; burn patterns
other than 'rejected draw plus k-1 more'; other registers; ..." Since then: NONE represented in any sweep (grep keyskipk / decode_with_resets /
reset_per_ over rounds 36-43: only ledger backups, R40-B3 prose and R43 X0). `relation_patch.md` never merged; R34-X1 struck the "earned"
label. Same-key resets are discharged key-free by F5; skip_by_4/5 have no prior (R4) and stay a completeness ritual.

## 3. Pointed Q5 — the seven R32-X1 corrections, propagation check
1 GS band: propagated (now 9.05-9.14 after R34-S1; no stale 9.01-9.15 in README/AGENTS/PAPER/PICKUP/ELIMINATION-LEDGER/analysis README).
2 Py2.7-MT "coverage 1.00 / exhausted": propagated (PAPER.md:256,263 struck-through; README scoped).
3 canon vs payload_resolved: discharged (R33-B1 re-feed, R34-P1 promotion, R35-B2 last legs).
4 transcription "three ways": propagated in README:266; NOT in KNOWLEDGE.json:266 (tail).
5 not_covered null x9: fixed; 3 new empties appeared in R43 (tail).
6 STATUS vs HIT-CANDIDATE / resume bug: R32 patch could not compile (R33-X1), fixed, built and tested on copies (R34-S1); seed 35563892 = noise.
7 B-10 <-> R29-L1: recorded as tool-mismatched; never re-run with OutGuess 0.2 (tracked).

## 4. Checked & clean
- beam_v3 transition algebra read line by line: keyskip1/keyskip2 doublet-consistency matches the forward encipherers; cleanup of `cnt` correct.
- My independent baseline plant is recovered by the oracle path (pmax 17.9-24.3, recovery 0.99-1.00).
- pf_v4 Viterbi recursion and `m_here` indexing; k=0 == pf_v3 claim not re-run (X1-R35 did).
- R34-B1's lost bash rows (R35-X1) were re-persisted by R35-B1 (276,242 rows) and R36-B2 (PHP awake run).
- R35-B1 control is natural-rate (no skip-free selection), 93/96; misses are screen misses.
- Near-miss seed 1354603465: adjudicated noise in R36-O3 (tracked).
- Doublet anatomy: no block/prime/parity structure; lag kappa flat except lag 1; nonzero deltas flat at small values.
- Line-initial rune bias re-derived (chi2 81.4) and matches R18-L4's glyph-width explanation (wide runes first: EA 38, P 33, D 32; I 9, R 6).
