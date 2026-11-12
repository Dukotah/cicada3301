# Fork J — fresh-eyes audit of Rounds 39–43 (+ Round 44 plan) — full notes (2026-11-12)

Scope read: round39..round44 SYNTHESIS/RESULTS/PREREG docs, round43 F1 lists (all 56 raw hypotheses), X0 ADJUDICATION
(all 34 rows), X1 REPORT, F2a/F2b, F3 (KEY-LOCALIZATION, TOOLKIT, ENUMERATION excerpts), F5b, F5bT PREREG, F6, D1;
load-bearing scripts: round42 run_c1/c2/c3.py, round43 run_f6_keystream.py; LEDGER.json rows cited by X0.
Paths below are relative to `liber-primus/analysis/` unless they start with `LEDGER:` (row id in liber-primus/LEDGER.json).
Scratch (NOT registered lanes; verification snippets only): `audit/J_scratch1..5.py`, `audit/J_token_channels.json`.

====================================================================================================================
## A. RANKED FINDINGS
====================================================================================================================

### 1. [INSTRUMENT-DEFECT + LOGIC-GAP] Every "object-as-key" negative of Rounds 42–43 was produced by a RIGID decoder judged
###    against the FREE-BEAM bar, with no filter-shaped plant. Under the repo's own pinned M1 (key-skip) construction a
###    CORRECT key scores pmax ≈ 3.9 — below the lanes' own wrong-key "best" (5.0–5.5) and 13 below the bar.
- Code: `round42/C1-keytexts/run_c1.py:44-56` (`free_bar` = `bars_v3(...,"free")`; `vig_running` = `c[i] + sign*key[start+i]`,
  whole page, no beam); `round42/C2-dated-pads/run_c2.py:39-41,63-67`; `round42/C3-auto-keys/run_c3.py:36-47`;
  `round43/F6-objects/run_f6_keystream.py:2` ("glue copied from round42/C3"), `:22-31`; `round43/F5bT-timing-keystream/PREREG.md`
  §three_conditionals ("position-independent additive/Beaufort ... beam-free direct-decode panel-max ... free-null bar").
- The Round 42 PLAN asked for the beam: `round42/CAMPAIGN-PLAN.md:37` (C2 "decoded under `pf_v4_12` + beam_v3"), `:38`
  (C3 "re-run the R30-B1 **beam** cell"). The executed lanes silently swapped in direct decode. R42 X1 flagged only the
  missing plants (`round42/X1-redteam/RESULTS.md` "FOUND-DEVIATION ... planted no fresh positive controls"), not the decoder,
  and argued "negatives sit 11–12 pmax units below their bars — far outside the region where marginal screen power decides
  anything" — backwards: the gap exists because the bar belongs to a different statistic (beam `free` optimum).
- F5bT did plant (3/3) but the plants are enciphered WITHOUT the anti-repeat filter (PREREG "Positive controls": `c = (p + K)`),
  i.e. a friendly analogue (doctrine Q1), so "plant 3/3" measures glue, not power under the filter. R43 X1 re-derived
  arithmetic and declared NO-ERROR-FOUND.
- Ledger effect: LEDGER:R42-C1-R35-KEYTEXTS-RUN, R42-C2-R36-DATED-PADS-RUN, R42-C3-B1-43-AUTO-KEYS-RUN,
  R43-F6-PAGE56-HASH-AS-KEY, R43-F5BT-TIMING-KEYSTREAM are all `status: negative`, `positive_control: passed`
  (control_detail: "plant-recover calibration from R34/R37 I1" — which calibrated the BEAM, not this path). That is how
  `validate_ledger.py` still reports "0 unsound negatives". Matrix cells H7xF4, H8xF4, H7xF9 and 43-B1 were moved to
  TRIED(panel-R36) on this basis (round42/SYNTHESIS, liber-primus/PICKUP-HERE.md:27-33).
- Measured (audit/J_scratch3.py; repo's own `round19/I1/constructions.py`, `round19/I2/adjudicate.py`, panel-r36, 12 plants each,
  correct key, rigid decode exactly as the lanes do):
    nofilter     L=265  pmax mean 27.75 (min 25.67)  rune match 1.00
    rewrite (M2) L=265  pmax mean 26.04 (min 24.59)  rune match 0.97
    keyskip (M1) L=265  pmax mean  3.94 (max 12.25)  rune match 0.13     <- 0/12 reach the bar
    skip_by_two  L=265  pmax mean  3.56 (max 11.96)  rune match 0.14     <- 0/12
    free bars: N=7,200 L240 16.94; N=13,800 17.42; N=34,668 18.10
  So these five rows are powered ONLY under M2 (value-rewrite, key aligned) / no filter. LEDGER:R18-L2-A-LOCUS not_covered
  says M1 vs M2 are ciphertext-identical (separation power 0.175) and "any sweep must cover both mechanisms".
  Doctrine mechanic 3: "Never use a rigid decoder on LP2."
- Same conditional sits (disclosed) on LEDGER:R28-L2-CONTESTED-BYTES ("no rejection-loop transition model") — the
  21.6M-decode payload-as-key result that X0 item 12 calls "the single most exhaustively covered object", and the harness
  Round 44 P4 says to reuse "verbatim" (`round44/CAMPAIGN-PLAN.md` P4 row). So the pp49–51 payload and the three onion
  256-byte blobs AS PER-PAGE PADS UNDER KEY-SKIP are uncovered, and P4 as planned would stay uncovered.
- Why it matters for solving: these are exactly the Cicada-published finite objects (payload, blobs, hash, timing channel,
  artefact keys, dated pads) that doctrine R5 ranks first. Their "negatives" do not exclude the model the repo believes in.
- Cost to discharge: hours. One shared harness (beam_v3 keyskip1+keyskip2 AND rigid; plants through enc_keyskip /
  enc_skip_by_two / enc_rewrite; a rigid-statistic null for the rigid arm) then re-run C2, C3, F6-keystream, F5bT, payload-as-pad,
  blobs-as-pad. (C1 keytexts and F5bT's repeating mode are separately killed by finding 4 — no re-run needed.)
- Checked not already tracked: R43 X1 correction (2) notes "R42-C1 is rigid-alignment" only as a citation fix for X0 item 9;
  no doc states the bar mismatch or the zero M1 power; rows unchanged; Round 44 plan silent.

### 2. [CONTRADICTION / LOGIC-GAP] The p15 4×4 grid is NOT "14/16 = 3301−prime with two cells breaking the pattern".
###    All 16 cells = |3301 − p(F_n)| for the Fibonacci numbers F_n = 0,1,2,3,5,…,987 (0-based prime index), written as a
###    clockwise spiral starting at the red cell. Verified exactly (16/16).
- R43 text: `round43/X0-firewall/ADJUDICATION.md:41` ("14/16 cells = 3301−prime; red 3299 = F"), F1 A2-H3 ("Two cells
  (4516, 1206) break the pattern and need full-res re-reading"), `round43/F2-inventory/image-channels.md:52`,
  `round43/SYNTHESIS.md` §4 item 2, `round44/CAMPAIGN-PLAN.md` P2 ("14/16 = 3301−prime; red 3299 = F").
- Verification (inline python, this fork): primes at 0-based indices [0,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987] =
  2,3,5,7,13,23,43,79,149,263,463,829,1481,2593,4507,7817; |3301−p| = 3299,3298,3296,3294,3288,3278,3258,3222,3152,3038,
  2838,2472,1820,708,1206,4516 = the grid read (r2c2 red)→r2c3→r3c3→r3c2→r3c1→r2c1→r1c1→r1c2→r1c3→r1c4→r2c4→r3c4→r4c4→
  r4c3→r4c2→r4c1. The two "breaking" cells are the absolute values of the two negatives (4507, 7817 > 3301).
- The community already calls it the "[3301-fib prime] spiral from page 15" — quoted once in `round10b/PA-1/CENSUS.md:154`
  under "untried methods"; no LEDGER row mentions it (grep `fib`: only incidental E-02 / R16-PRNG hits).
- Why it matters: (a) P2 as written ("the 16 numbers as keystream seed, offset table, page-index map, totient parameters")
  tests an object with ZERO free information — the grid is a generator spec, not data; (b) what it does teach is a rule set
  the author demonstrably used on an unsolved-section page: Fibonacci-indexed primes, the 3301−x complement, spiral reading
  order, and RED = ORIGIN marker (not "F interrupter") — the last is direct evidence for how to read the P1 red-ink channel;
  (c) it is a calibration datum on the blind armada: the agent's "needs re-reading" was wrong and X0/F2/SYNTHESIS propagated it.
- Cost: zero to correct the docs; P2 should be re-PREREG'd around rule-derived readings (e.g. k=(3301−p_n) mod 29 streams,
  Fibonacci-indexed start offsets, spiral orderings) — minutes each, through the finding-1 harness.

### 3. [LOGIC-GAP] X0's headline "17 CITED — zero letter-stream items the ledger missed" overstates. Re-checking the 7 CITED
###    stamps X1 did not spot-check, plus items 1 and 12:
- Item 1 (6/6 convergence; `ADJUDICATION.md:24`): cites R12-C1 "incl. f=identity ⇒ bare delta-tape". R12-C1's grid is
  k=2..6 × f∈{sum, gemsum, xor, prime_of_sum, prime_of_gemsum, lastdiff, alt_sum} (`round12/C1/RESULTS.md:33-40`): there is
  no identity/k=1 config, and it is English-quadgram, rigid-bar. The agents' actual first tests — the solved-page toolkit ON
  THE STEP STREAM over a 28-symbol alphabet (D−1∈0..27, mod 28), stream keys on D, doublets-as-interrupters (A1-H1c, A2-H1,
  A3-H1b/c, A6-H1) — are in no row (ledger grep for mod 28 / step / delta stream: none). X1's fallback ("exclusion rests on
  R18-L2-A-LOCUS/D-01") only excludes the STRICT wheel (M5: 0 doublets); composites are in R18-L2's own not_covered
  ("composite loci"). X0 lists this as a 10th REOPEN bullet (`ADJUDICATION.md:81`) but SYNTHESIS counts 9 and the Round 44
  plan drops it. Scratch pre-kill (J_scratch1.py): nonzero-step stream (12,815 symbols, 28-ary) kappa flat to lag 300
  (no |z|>3, sd 1.02), page-anchored periodic IoC·28 ≤ 1.008 for m≤60 → short periodic keys on the step alphabet are out;
  aperiodic stream keys on D (mod 28 / mod 29) remain unrun (minutes).
- Item 7 (prime/totient stream with per-page parameters; F3 ranks it TOP as J2; `ADJUDICATION.md:30`): cited rows cover
  offset 0 only — LEDGER:R22-C-LITERAL-IMPERATIVES not_covered "non-zero offsets on keyed lanes"; LEDGER:R26-C-SEMANTIC-SEED-ZOO
  "Offsets != 0 ... only o=0 swept"; LEDGER:R37-C3-U6A-N5 "per-segment restart on pages 18 and 36" (2 of 55 pages) and
  "29 offsets" that are additive shifts, not stream start indices. A4-H2's test (start index 0..10,000 per page, skip rule,
  F-interrupter) is not covered at power under the modern instrument. Should be REOPEN.
- Item 10 (LP2 is the key for the signed blobs; `ADJUDICATION.md:33`): F-01's five targets are 2012/13 puzzle TEXTS, solved
  LP1 pages, PGP message BODIES, the 63-value AN-END hash and LP2's own head (`round16/F-01/RESULTS.md:40-47`) — none is one
  of the three Cicada-signed 991-byte high-entropy blocks (corpus/A-primary-artifacts/signed-payloads/2014-01-liber-primus-
  hash-block*.bin) the agents named. Those blocks were used as pads OVER LP2 (round17/P3_tables, round40/B3) but never as
  ciphertext under LP2-derived streams, and never stride-parsed. Blind convergence on these objects is 4/6 (A3-H4, A4-H7,
  A5-H5, A6-H8) — the same as red ink — but X0 split it across items 10/29/33 and it surfaced only as "NEW-lite #5" in the
  P5 tail.
- Item 12 (payload as key): rigid-only (finding 1).
- Items 8, 9 (word key + skip; running key + skip): the cited modern rows are R42-C3/R42-C1 (rigid, finding 1) and R26-B
  (4 offsets/text, 5 pages). The stamps are RIGHT, but only because of the mechanism bound in finding 4, which is not a row.
- Items 27, 28, 34: fine as stamped (27 inherits item 7's offset gap).
- Dedup losses: raw count is 56 hypotheses, not the "52" in `ADJUDICATION.md:16`; A6-H5 is credited to no item (content
  covered by 15/16/29). No whole hypothesis vanished; the losses are the sub-tests above folded into CITED rows.
- Cost: item-1 edge + item-7 start-index sweep + LP2→blob direction ≈ a day total, all finite.

### 4. [DROPPED-LEAD / CONTRADICTION] F3a measured an alignment-free, scorer-free kill of natural-language running keys and
###    word keys (monogram flatness); it was never filed, F3c's own top localizations contradict it, and the tracking docs
###    still carry the family as open work.
- F3a: `round43/F3-hand-feasibility/TOOLKIT.md:86` (English running key ⇒ unigram IoC 1.0698, ">100σ"), `:105`
  (Vigenère-13 + skip ⇒ IoC 1.115 ✗), `:123` ("not a literary running key, not a short word key").
- F3c: `KEY-LOCALIZATION.md:148` (C1 short word keys "TOP ... matches every measurement"), `:150-151` (Self-Reliance / own
  plaintext "STRONG"), `:168-188` (J1, J3 ranked joins; "never been done WITH skip-tolerance"). SYNTHESIS §2 reports
  "J1–J6 ... ranked" without the conflict.
- Plant check through the repo's constructions (audit/J_scratch5.py, 8 plants each, n=12,956): Self-Reliance running key over
  the repo's English stream under keyskip / rewrite / skip_by_two ⇒ ciphertext IoC·29 = 1.046 / 1.044 / 1.049 (min 1.037);
  13-rune word key + skip ⇒ 1.114. LP2 = 0.99987 ± 0.00058. So ≥ 60σ, independent of offset, sign, skip relation, text.
  (My analytic convolution for LP-voice + Self-Reliance gives 1.0215, i.e. F3a's "1.0698" is text-pair dependent; the kill
  holds across the range.) Conditional on: index-additive combination; plaintext not already flat.
- Still tracked as open: LEDGER:R12-C2 (never-run), LEDGER:R26-B (partially-run; "large pages capped"), the
  "10-keytext hash-pinned refetch" in `round44/CAMPAIGN-PLAN.md` Deferred and PICKUP-HERE, MEASURED-CEILING.md:65 ("partial").
  All are discharged by one constraint row; nothing in nav docs states it (grep "convol", "unigram IoC", "1.07": no hits in
  ELIMINATION-LEDGER / MEASURED-CEILING / PICKUP-HERE).
- Generalises to a free PRE-SCREEN for any proposed key family: compute its value distribution mod 29, convolve with a
  plaintext register, compare with 0.99987 ± 0.00058. Example: F5bT's timing streams take values {1..7}
  (`round43/F5bT-timing-keystream/key_streams.json`): predicted page IoC·29 = 1.13–1.27 (4–9σ PER PAGE) — the repeating-mode
  bulk of its 1.9M decodes was excluded before it ran. Decimal/hex-digit keys fail the same way.
- NOT usable (I tested and it failed its own control): a matched filter for "key uniform on 28 residues" (totient/prime
  streams). Plants through enc_keyskip give z = +1.68 ± 0.92 vs +0.32 ± 0.87 for a uniform pad; LP2 = +0.47 (J_scratch4.py).
  Likelihood ratio ≈ 0.5 — no information. Recorded so nobody re-derives the optimistic 3.2σ analytic figure.

### 5. [UNDISCHARGED] Round 43's X1 delivered 3 of its 7 planned audits; F2, F3, F5 and F6 were never red-teamed.
- Plan: `round43/CAMPAIGN-PLAN.md:53` — blindness; "F2 inventory completeness vs a second independent pass"; "F3's
  feasibility scores re-derived"; "F5 fetch provenance + hashes"; "F6 counting"; X0 stamps; gate.
- Delivered: `round43/X1-redteam/REPORT.md` §1 blindness, §2 F5bT, §3 X0. `round43/SYNTHESIS.md:3` "the session died mid-X1".
- What the missing audits would have caught: finding 4's F3a/F3c conflict; F3c's word count (`KEY-LOCALIZATION.md:22-23`
  "3,604 words, mean 3.51", `:111` "536 one-rune words" — line breaks counted as word breaks; TOOLKIT.md:48 has 2,928 words,
  blind agents ~320 one-rune words); F2a being a SAMPLE (`F2-inventory/image-channels.md:8-10`: 26 of 56 page images) though
  SYNTHESIS calls it a census; F6-keystream's missing plant.
- Also: the blind prompts are not on disk (`REPORT.md:22`), so the "allowed background" two agents cite cannot be audited.

### 6. [DROPPED-LEAD] F3 ENUMERATION's own proposed tests 2–4 and its two zero-parameter alternatives never reached X0, the
###    ledger or Round 44.
- `F3-hand-feasibility/ENUMERATION.md:133` row 37 "strict no-repeat + scribal dittography" (the 86 doublets are duplicated
  glyphs; "deleting one glyph per doublet should help decryption"), `:134` row 38 "asemic / device-generated stream" as the
  live null, and §7 tests 2 (collapse each doublet, re-run screens), 3 (file T1/T2 as ledger constraints), 4 (asemic bound).
  X0 took only KEY-LOCALIZATION's J1–J6. No LEDGER row for F3 at all (R43 rows: 4×F6 + F5BT), although SYNTHESIS §2 and
  commit fbd1950 say the constraint was "filed".
- LEDGER:A-03 not_covered: "insertions/dittography sites are not bounded by this row."
- Decoder consequence (my analysis): a duplicated ciphertext rune needs a key STALL (advance 0); keyskip1/keyskip2/free only
  advance ≥1, so every decode desynchronises at the first visible doublet. Self-kill attempt: the head sweeps are safe —
  page 0's first doublet is at offset 122, so every L=120 head and 24-rune screen at stream offset 0 is unaffected; but
  41/55 pages have a doublet inside 240 runes and 28/55 inside 120 (J_scratch1.py), so per-page lanes and the two-page oracle
  rule in verify_solution.py are exposed. Cost: add a doublet-collapsed variant of the ciphertext as a second target (2×).
- Also unfollowed: TOOLKIT.md:129 residual — nonzero-difference χ² 41.4 vs 27.8±7.2. My split: pages 0–27 χ²=27.0,
  pages 28–54 χ²=47.9 (df 27, p≈0.008); largest cells Δ=17 (z −2.65), Δ=9 (+2.45). Marginal; untracked.

### 7. [UNDISCHARGED] "An independent null re-test is queued" (Round 39) for the three Round 37 rows whose null was chosen
###    after the data — never run, never carried.
- `round39/SYNTHESIS.md` §3 item 3 (N2, N4-read, R22-C structural). LEDGER:R37-C3-U6A-N2, R37-C3-U6A-N4, R37-C3-U6B-R22C still
  `negative`, `threshold_fixed_in_advance: False`. Round 40 I1 re-planted controls in more registers but did not re-null;
  no mention in round40–44 plans/syntheses or PICKUP-HERE (grep "post-data": none). X0 item 7 cites these rows.
- Cost: minutes (pre-register a null, re-judge stored rows).

### 8. [UNDISCHARGED / tracking] The 8 NEW and 9(+1) REOPEN items exist only in prose.
- LEDGER has no `never-run` rows for red ink, p15 grid, quote/punctuation identity, cuneiform/dots, doublet-site read,
  hash-block parse, tree anomalies, blobs-as-pads; `jq 'select(.status=="never-run")'` (the README's own entry query) cannot
  see the Round 44 queue. Of the REOPENs only R1 (resets) is in the Round 44 plan; figural-motif catalog (3-agent
  convergence; LEDGER:R22-D "THE REOPENER"), all-pairs page keying, mirror byte residue, stationarity, short-page specificity,
  audio reductions, non-linguistic registers are neither planned nor listed as deferred.

### 9. [SHARED-PREMISE with a concrete consequence] `%` segments are treated as pages; they are not.
- `F2-inventory/token-channels.md:54`: krisyotam merges the grid image page (9 runes) into solver page 15 (9+150) and
  91+123 into solver page 33; the three table pages have no runes and vanish; blind agents report an image↔segment
  off-by-one after p49. Round 44 R1 (per-page key resets) and P4 (per-page pads) must use image-page boundaries; a reset
  decoder on `%` is wrong on ≥2 pages. Verified: relikd rune stream == canon for all 12,956 runes (J_token_channels run).

### 10. [UNEXAMINED-INPUT, minor] WATCH-band rows are still inspectable despite the D1 lapse.
- `round42/S1-s2-recovery/state_recovered/candidates_summary.json` keeps the top-10 seeds; five exceed the proposed 7.10
  watermark (1087113973 7.307, 3905907872 7.301, 1774592253 7.285, 2473038093 7.158, 325254043 7.126). The owner decision
  pending since Round 41 can be informed by five L=240 decodes (minutes). Note the proposed fixed 7.10 is not N-scaled:
  at N≈1.8e8 a null max ≈7.3 is expected, so adopt it per-N or it fires on every S2 window.

====================================================================================================================
## B. ANSWERS TO THE POINTED QUESTIONS
====================================================================================================================

Q1 — see finding 3. REOPEN (verbatim list, `ADJUDICATION.md:70-81`): per-page/per-line key resets + p27/p54 7-gram;
figural-motif/marginalia-count catalog; all-pairs page XOR/page-as-key; mirror byte residue (B-09/G-01/H-02/R36-O2);
pad-in-page-JPEGs vs canonical onion-7 originals; doublet-rate stationarity (power 0.075); homophonic/non-linguistic
registers (D-03, D-02, C-01 open); short-page specificity (B-24); audio reductions; delta-stream composites outside
R12-C1's f-set. NEW (`:59-68`): red ink (A2-H7, A3-H3, A5-H4, A6-H4); p15 grid (A2-H3); quote-span/punctuation identity
(A2-H5, A4-H6/H8, A5-H6); onion blobs as per-page pads (F3-J6); hash-block stride parse (A4-H7, A6-H8); cuneiform + 5-dot
(A2-H8); 86-doublet-site read (A2-H2); p32/p55 trees (A4-H9). Agents' rationales are in `F1-blind/hypothesis_lists.json`
(fields title/motivation/first_test). Caution on "6/6 convergence": six instances of one model family reading the same
statistics are not six independent witnesses; doctrine R4 does not admit convergence as a prior.

Q2 — F3 considers an intrinsic no-repeat cipher only as "class 3 ... lowest weight" in one sentence
(`KEY-LOCALIZATION.md:100-102`, argument: "29 admits no Playfair/bifid grid") and as one simulated row, the wheel-walk
c_i = c_{i-1} + nonzero step: "✗ zero doublets (plus it is a skip rule in disguise)" (`TOOLKIT.md:104`). No keyed
step-alphabet (mod 28) cipher is simulated. The 86 survivors are explained three incompatible ways inside F3: "human
slips" at a ~19% lapse rate (`KEY-LOCALIZATION.md:91,227`; `TOOLKIT.md:110-116`, which itself calls 19% "high for a
deliberate single check", `:130`); fitted 80% compliance (`ENUMERATION.md:131`); or dittography with zero free parameters
(`ENUMERATION.md:133`). "Human slips" also sits against the README headline "machine, not by hand (≥0.99)"; LEDGER:D-01's
fine print reconciles them (only human-SUPPLIED RANDOMNESS is excluded; a human applying one rule is underpowered 0.110),
but no nav doc says so.

Q3 — Channels (F2a `image-channels.md:40-67`, F2b `token-channels.md`): red vs black runes [P1]; red drop caps (p0,3,8,15,
23,27,33,40,54) [R22-D done; P1]; word separators 2,766 / line breaks 604 / page breaks 56 [covered B-12, C-02, R23/24];
`&`×18, `$`×9, `§`×1 [not planned]; quotes 14 marks = 7 spans = 405 runes [P3]; apostrophes 4, `⁚` 4, inline `⁜` 31 vs
`⁘` 145 [P3]; digits 1–5 (pp36–38) and inline 7 (p10, rune idx 2566) [P3]; p15 grid [P2 — see finding 2]; base-60 tables
256 cells [known payload]; 0_wisdom number/word grid [R41-C1-R15]; red dot-matrix blocks ≥16 instances on sampled pages
(F2a: "patterns differ"; A2: 13-dot vs 10-dot only on p36/38/49 — unreconciled) [P1]; cuneiform-like clusters p33/p36
[P5]; 5-dot constellation p23 [P5]; three-dot divider, lemniscate ornaments, crosses, vines, bare-branch trees, root-tree
dot clusters (2 left / 4–5 right, p40–54), insects [NOT planned — X0 REOPEN item 5]; grey ghost tree p55 / blurred tree p32
[P5]; layout whitespace [not planned]. Machine-readable? NO. F2 committed two markdown files only; the image pass is a
26/56-page sample with no per-page counts; the "throwaway scripts" are not committed; `data/relikd/` images are gitignored
and absent from a clone. Token positions exist only as markdown tables — I re-derived them exactly from
`data/sources/relikd_p*.txt` and saved `audit/J_token_channels.json` (quote spans (1659,1677) (5459,5478) (9715,9727)
(9811,9869) (10211,10279) (10279,10439) (12522,12592); apostrophes 1110, 5138, 8515, 10089; `⁚` 1317, 2910, 4967, 11329).
Round 44 P1 starts from zero on the image side.

Q4 — Left on the timing channel: (i) intervals for bytes 2–142 (141 of 255 cells) — unattested in the four held witnesses;
no further witness hunt is planned; (ii) the byte VALUES as key (= blob761, Round 44 P4 — rigid harness, finding 1);
(iii) intervals as transposition / permutation / skip schedule / page selection; arithmetic beyond k, 5k, prime[k];
interleavings with byte values; sub-runs; one-shot alignments under 60 runes; a fresh null; (iv) everything under M1,
since the decode was rigid; (v) but additive use is pre-excluded by monogram flatness (finding 4), so only the
non-additive readings in (iii) carry any prior.

Q5 — MEASURED-CEILING X1 corrections landed (checked the page text for the Py2.7 exact/pair, PHP and null12 lines).
Null refit: sound as described; two bar systems still coexist (survivor12 9.34–10.49 for orbit lanes vs the un-recalibrated
Round 19 claim bar 7.6342 for S2), disclosed on the page. R40-C1 blocked cells: R14/R15 → negative (R41); R35/R36/43-B1 →
run in R42 but rigid (finding 1); R31 (instrument floor) and R44 (bookcipher, control 0.74–0.82) remain inconclusive /
partially-run and are absent from the Round 44 deferred list; LEDGER:R41-C1-R35/R36/B1-43-*-VERIFIED still carry the
clone-scoped "absent ... gitignored" text X1-B refuted. 10 corrupt keytexts: tracked, but moot under finding 4 — and any
re-run must not reuse run_c1.py.

Q6 — Round 44 plan vs the Aiming Test:
- No lane fixes the instrument; budget has 0% instrument although finding 1 is an instrument regression. Add I0 (shared
  object-as-key harness with filter-shaped plants and a rigid-statistic null) BEFORE P2/P4.
- P1: Q1 — the red stream is a few hundred runes; panel power at that length is unmeasured (LEDGER:R19-FINITE-ORNAMENT
  "underpowered at band lengths"); reading (b) "standalone stream under panel-R36" can only fire if red runes are
  plaintext. Q2 — the stated prior is blind convergence (not admissible under R4); measured priors exist and are not cited:
  on solved pages red = titles/first words with no payload, and on p15 red = the spiral origin (finding 2). First
  deliverable must be a committed per-rune colour mask for all 56 pages with a solved-page control.
- P2: object carries no free information (finding 2); re-scope.
- P3: positions verified; only crib/reset uses can be adjudicated; pair with R1 (resets at ⁜/⁘/&/$/quote boundaries,
  not just page/line — A1-H4, A5-H7).
- P4: rigid harness (finding 1); pad length 256 vs page length 229–277 plus ~9 skips needs stating.
- R1: correct page map required (finding 9).
- Missing: step-stream toolkit; prime/totient start-index sweep; LP2→signed-blob direction; dittography variant;
  constraint rows (T1, T2, monogram bound); ledger rows for the queue; the R43 audit debt; the R37 post-data nulls.

====================================================================================================================
## C. CHECKED AND CLEAN
====================================================================================================================
- Canonical stream: 12,956 runes, sha matches PROBLEM.json; 86 doublets; relikd == krisyotam on every rune.
- F2b token counts and all 7 quote-span offsets reproduce exactly.
- F3 T1 "smearing bound" is sound for independent position-wise additive keys; plant numbers in measurements2.json match
  TOOLKIT's table.
- X0's REOPEN/NEW quotes I re-read in the ledger are accurate (A-03, R18-L2-A-LOCUS, R33-I2 unrepresented list, D-01).
- R42-S1 recovered state is present locally (STATUS.json, HIT-CANDIDATE.json, candidates_summary.json with top-10 seeds).
- R41 synthesis ↔ ledger statuses agree for I1/C1/B2 rows; R39/R40 X1 corrections are reflected in SYNTHESIS text.
- Step stream: no periodic structure (scratch).
Not checked (out of budget): F5a Wayback hashes; F5bT witness merge (X1 did); R40 B1/B3 engines; R41 I1 fit code.

====================================================================================================================
## D. TAIL (tidiness)
====================================================================================================================
- `ADJUDICATION.md:16` says 52 hypotheses; the JSON has 56. `:33` refers to "REOPEN item R5", which does not exist.
- `round36/O4-clue-coverage/untried.md` / `matrix.md` bodies are the 2026-10-30 state with banners only; CLAUDE.md sends
  agents there for "clue readings never tried".
- F6: prereg'd sig^e mod n test not run (no modulus); blob2/blob3 pixel-diff follow-on untracked; `f6_results.json` duplicate row.
- F5b: the disputed trailing "57" on the onion-3 hex is context-only and unrecoverable.
- PROBLEM.json "≥1.38% floor" vs F3 "0.0186 hard floor" vs ENUMERATION "1.40%" — three numbers for one quantity (text-dependent).
- R43 X1 REPORT cites absolute paths under /mnt/c/Users/... (the owner's laptop), not repo-relative.
