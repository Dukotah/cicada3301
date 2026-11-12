# E-round-19 — fresh-eyes audit notes (reader fork E), 2026-11-12

Partition: `liber-primus/analysis/round19` (Aug-26 lanes I1 I2 I3 R1 G1-G4 T1-T3 C1-C3; Oct-01 lanes instrument/ derivedkey/
finite/ redteam/). Paths below are relative to `liber-primus/` unless they start with `analysis/`.
Read in full or near-full: CAMPAIGN-PLAN, I1/{constructions.py,driftbeam.py,RESULTS}, instrument/POWER-ENVELOPE,
derivedkey/RESULTS, redteam/RESULTS, finite/RESULTS(top). Headlines + targeted sections: I2, I3, R1, G1, G2, G3, G4, T1, T2,
T3, C1, C2, C3. Cross-checks: LEDGER.json (python queries), MEASURED-CEILING.md, PICKUP-HERE.md, later decoders
(round32 beam_v2, round33 beam_v3 + I2-construction-axis, round35 pf_v4, round27/28 grind C), round43 F2/F3.

---------------------------------------------------------------------------------------------------------------------
## Q1. Every enciphering construction the project models (exact generative rule as coded)

All share: C_i = (P_i + K[j]) mod 29 (decode p = c - k, "sign -1"), one key value per emitted rune, key pointer j only moves
FORWARD, one cipher rune per plaintext rune, coin = `rng.random() < supp` from an independent `random.Random(seed)`.

round18/L7-redteam/b1_power_envelope.py (MECH, l.203-206) and round19/I1/constructions.py (MECH, l.238-248):
| name | rule |
|---|---|
| keyskip (baseline; campaign18_skip/skipdecode.py:61-83) | if c == c_prev and coin(supp): j += 1, retry (loop) |
| keyskip_varying (ramp / blocks / burst) | same, supp a function of position |
| free_drift(q) | before each rune, with prob q: j += 1 (unrelated advance); then keyskip |
| drift_at(n) | exactly n extra single advances at evenly spaced runes; then keyskip |
| jump_at(jump, n) (R19 only) | n pointer jumps of `jump` at single runes; then keyskip |
| skip_by_two | on rejection j += 2 (rejected draw + one burned) |
| coin_from_key (R19 only) | coin is K[j+1] < round(0.83*29)=24; every doublet event burns one extra draw |
| rewrite (benchmark/plant.py:193-209) | key stays synced; a would-be doublet is replaced by a uniformly random OTHER rune |
| keyside (R18 only) | key stream itself filtered doublet-free, rigid encipher |
| plainside (R18 only) | plaintext doublets dropped, rigid encipher |
round33/I2-construction-axis/enciphers.py adds: reset_per_page, reset_per_line (key pointer returns to 0), skip_by_k (k=3,4,5).

Decoder relations (round19/I1/driftbeam.py): keyskip1 (all skipped key values must equal v(acc) = K[acc]+(c_prev-c_i), i.e. would
have reproduced c_prev with THIS rune's plaintext), keyskip2 (pairs: first consistent, second free), permissive/"free"
(<= max_free unexplained advances per rune, penalty lam). I re-derived the algebra (l.21-30, 136-211): correct. `cnt` reset
(l.209-211) correct for both pair and non-pair. G-EQ vs skipdecode exact. NO-ERROR-FOUND in the decoder as a decoder.

STRUCTURAL LIMIT (driftbeam.py:151 `base = pa + 1`; identical in round33 beam_v3 `_drive`, round35 pf_v4 `dp_regs` where the
cumulative skip count s is monotone non-decreasing): **every ciphertext rune consumes >= 1 key value and the pointer never
stays or goes back.** Anything needing a "stay" (advance 0) is unrepresentable by every relation in every generation.

### Plausible avoidance implementations NOT in the modelled set
| implementation | subsumed? | measured? |
|---|---|---|
| re-draw that consumes no key (resample cipher rune) | = `rewrite`; any relation decodes (key in sync, ~2.8 % substitution errors) | R12-D1, R18 L7-B, R19 instrument (97 % recovery). pf_v4 screen power under rewrite never measured (R33-I1 not_covered lists rewrite) |
| "add 1 to the cipher rune" / increment key VALUE until different (deterministic offset) | = rewrite to a fixed delta | **excluded by data, not by any lane I found**: lag-1 delta histogram is flat over the 28 nonzero deltas (coordinator stats1.py: counts 401-510, mean 457.7; a fixed-delta dump of ~360 events would put one bin at ~817). R43-F3 ENUMERATION.md:158 says the same ("no +1 dump bucket") |
| reject only within word / line | data-excluded: keep ratio in-word 0.180, word-boundary 0.235, line 0.224 (coordinator stats1.py; R43-F3 TOOLKIT.md:76) | yes |
| filter on key stream alone | `keyside` (R18) | excluded by the statistic itself (produces no ciphertext deficit); R33-I2 RESULTS s.1 |
| **delete the offending rune / skip that plaintext letter ("haplography as encipherment")** | From the decoder: one key advance that is NOT doublet-consistent for the next plaintext rune (it was consistent for the deleted one) + a missing plaintext letter. = `free_drift` at q ~ 2.8 %/rune. Representable ONLY by `free`/permissive; NOT by keyskip1/keyskip2 | free_drift q<=0.10 recovered by permissive (I1 RESULTS s.4). **But the mass sweeps decode survivors under keyskip1+keyskip2 only ("not free", MEASURED-CEILING.md:51)**, while the pf_v4 screen DOES pass such heads (its skips are unconstrained). In the ledger "haplography" (A-03, R20-N2) means transcription merges only - never an enciphering rule |
| **null-rune insertion that consumes no key** | needs "stay" -> unrepresentable by all relations, all generations | never |
| **F-interrupter (plaintext F left clear, key not advanced)** - Cicada's demonstrated convention on all 3 keyed solved pages | needs "stay" -> unrepresentable; see Finding 1 | R19 instrument measured the consequence (14.4 % recovery, AN-END-class); nothing after R19 |
| swap (encipher this rune with the NEXT key value, next rune with the skipped one) | non-monotone pointer -> unrepresentable; desync +1 forever | never |
| filter before a second layer (Atbash / constant Caesar / fixed monoalphabetic on top of the filtered stream) | decoders handle the skip structure, but screen + panel see Atbash'd / shifted plaintext = noise | G1 READY.md:72 pre-registered sign x direction x Atbash; G4 covered c in {0,1}; the orbit sweeps ran neither (Finding 4) |
| per-page / per-line key reset, skip_by_4/5 | unrepresented (R33-I2) | tracked (MEASURED-CEILING.md:102; R44 lane R1) |

### The 0.83 coin itself (premise note)
Every plant from R18 to R43 implements the soft filter as an independent Bernoulli(0.83) inside a machine loop
(constructions.py:108,130,152,178,197; coin_from_key l.213 `thresh=int(round(supp*N))`). `grep` over rounds 17-44 + FINAL-SYNTHESIS
for any account of WHY a machine loop would be soft returns one line: FINAL-SYNTHESIS.md:75 ("its softness points to a human
calligrapher"). README.md:173 says R17 established "machine, not by hand (>=0.99 power)", but the D-01 ledger row's own
`not_covered` says "'A person did the writing' is untouched; only 'a person supplied the randomness' is excluded" and rates
the human-applies-one-rule-to-a-machine-pad question UNDERPOWERED (0.110). R43-F3 TOOLKIT.md:110-117 then attributes the 86
survivors to a "~19% human lapse rate ... the human signature". So the record holds three positions at once.
I tested the cheapest deterministic alternative ("a HARD test in a wider domain looks soft after reduction"): hard no-repeat
on the UNREDUCED sum p+k (0..56) gives keep = E|dp|/29 = 0.303 (self_reliance, 41,875 runes) / 0.311 (solved_plaintext) / 0.333
(uniform) -> ~135-149 doublets expected vs 86 +/- 9 observed. **Excluded (~5 sd) for English-like plaintext in Gematria index
order.** Other wide-domain variants (prime-value arithmetic, 5-bit draws) not tested. bash's own `$RANDOM` anti-repeat loop
(G1 RESULTS.md:32, M4) is the same shape at 15 bits and is correctly dismissed there.

---------------------------------------------------------------------------------------------------------------------
## FINDINGS (ranked)

### 1. [SHARED-PREMISE + UNDISCHARGED] Interrupters x key-skip were never represented jointly; the R19 "standing constraint" vanished
- R19 itself: analysis/round19/instrument/POWER-ENVELOPE.md:39-45 (FOUND-ERROR: keyskip beam reads an AN-END-class page at 14.4 %;
  "any lane whose key hypothesis implies an interrupter page MUST run the interrupter-aware solver");
  analysis/round19/derivedkey/RESULTS.md:60,101,108 ("multi-interrupter pages ... NOT covered"; "the standing FOUND-ERROR
  constraint on every derived-key sweep in the repo").
- After R19: `grep -i interrupt` = 0 hits in round32 beam_v2.py, round33 beam_v3.py, round35 pf_v4.py, verify_solution.py,
  round27/28 grind C engines; **0 hits in MEASURED-CEILING.md and PICKUP-HERE.md**. MEASURED-CEILING.md:33 and :102 list the
  unrepresented constructions (skip_by_4/5, resets, combined axes) without interrupters. Only trace: `not_covered` of ledger
  rows R33-I1-REGISTER-AWARE-BEAM / R33-B3 (one word), and L7-B `reopens_if`.
- The two decoder generations are complementary, never joint: Round 8/10 C sweeps (analysis/seed_sweep/sweep.c:9,244;
  round10/L5-seed32/sweep32.c) = interrupter fork but RIGID; Round 19+ = key-skip but NO interrupter fork.
- New, from the ciphertext alone (scratchpad lpdata.py; no lane states this - searched "458" x interrupt across all rounds;
  R10-L4/R11-S1 just call all 458 F "interrupters"): F count 458 vs 446.8 +/- 20.8 expected for a uniform stream =>
  number of clear-F interrupters n = 11.6, **<= 47 (95 %), <= 62 (99 %)**. Consequences:
  (a) the solved-page convention (EVERY plaintext F is clear: WELCOME 7/7, KOAN 2/2, AN END 1/1) is excluded for an
      English-rate plaintext (~285 clear F expected; observed excess 12 +/- 21) - LP2 either abandoned the convention, has
      <= ~1 interrupter per page, or has an F-poor plaintext. A real constraint nobody wrote down.
  (b) sparse interrupters are NOT excluded, and the head is exposed: F runes sit at positions **7 and 17 of the first 24**
      (first_24_indices in PROBLEM.json), 7 in the first 120, 12 in the first 240. If either head F is an interrupter the
      24-rune pf_v4 screen is desynced from that rune on and the TRUE key is discarded at the screen. P = 2n/458: 5 % at the
      point estimate, 20 % at the 95 % bound; for the L=120 confirm (7 F) 16 % / 52 %.
- Cost to discharge: an interrupter at head position x is exactly "delete rune x from the ciphertext". Three extra screens per
  orbit (delete 7; delete 17; delete both) with the UNCHANGED pf_v4/beam_v3 engines; then an F-stay branch (2^5) only on the
  few L=120 survivors. Bash orbits: hours. Zero-cost part: add the conditional + the F-count bound to MEASURED-CEILING s.1/s.3.
- Kill attempts: (i) could forward skips re-sync? No - pointer is one AHEAD, relations only advance. (ii) Is it already
  tracked? Only as one word in two `not_covered` fields; absent from the page CI enforces.

### 2. [UNDISCHARGED] Perl `rand`: the only generator with SIGNED first-party evidence, complete in 2^32, dropped after R21
- analysis/round19/C3/RESULTS.md:23 and s.6.6 (l.646-696): two PASSing signed messages (2012-01-15, 2014-01-06) carry
  `Crypt::RSA` + Perl `Data::Dumper` output; l.696 "G2's prior should be re-sourced to this".
- analysis/round19/G2/RESULTS.md:17-21,147,163-182: Perl 5.14 un-seeded `rand` reads 4 bytes of /dev/urandom -> the WHOLE
  family incl. the no-srand case is exactly 2^32, "no residue"; l.341-344: 2^32 x r29 x 8 orientations = 34 h in C.
- What ran since: R24-C2-EXT ~24k prior/dense seeds, R26-A 347 prior + ~400 dense (LEDGER R26-A-GEN-SWEEP-FIRST-FIRE, 1.74e-7).
  `grep -i perl` over every CAMPAIGN-PLAN R22..R44: no hits. R20/R21 held it "sieve-gated"; the sieve blocker was lifted by
  pf_v4 (R35) and pf_v4_12 (R37) and applied to bash/PHP/Py2.7 only. LEDGER R19-G2 has status `measured` (so a
  `status=="never-run"` query does not show it); MEASURED-CEILING.md:106 folds it into "flat tails ... a C or GPU port".
- R1 (analysis/round19/R1/RESULTS.md:470-512) had already shown the L1 distro prior does not discriminate bash from Python
  from Perl ("enumerable lanes wearing a prior's clothes"); Perl is the one with an independent signed fact.
- Cost: days (C port of drand48 + pf_v4 screen); finite; closes a whole tool family including its "random seed" mode.

### 3. [UNDISCHARGED / mis-tracked] bash 4.2 LP64: "Full orbit" on the ceiling page is 3.6 % of the generator's state cycle
- analysis/round19/G1/RESULTS.md:29 (M1: seed == offset; `RANDOM=n` writes the state; one cycle of 2,147,483,646, tail 13-72) and
  the R19-G1 ledger row ("auto-seeded path reaches at most 77,594,624 seeds, i.e. 3.6% of 2^31, which is a PRIORITY ORDERING
  inside the full range"); READY.md: "a full enumeration subsumes it"; `KS.bash_sliding` (O(2^31+L)) was built for it.
- MEASURED-CEILING.md:51 calls the 77.6M auto-seed set "Full orbit"; no doc after R19 mentions the 2^31-2 cycle or the 3.6 %
  (grep 2147483646 / "full cycle" / "3.6 %" over rounds 20-44, MEASURED-CEILING, PICKUP-HERE: none).
- R40-B2 / the deferred "B2 offset remainder (110.5 of 116 cells)" pays per (offset, sign, ABI) cell of 77.6M. By M1 an offset-o
  cell on LP64 is just another 77.6M-state subset of the SAME cycle: offsets 0-28 cost 2.25e9 state-decodes per sign, MORE than
  the entire cycle (2.147e9), which would close every offset, every explicit `RANDOM=n`, every date and pid at once.
- Cost: one dense sliding scan of a 2^31-long sequence per sign (R17 did 1.45e10 offsets); hours in C, days in numpy. ILP32
  differs (cycle 343,896 + long tails) and needs its own accounting. Check with the R40 reader before acting.

### 4. [SHARED-PREMISE] G1's pre-registered 48-cell cross collapsed to one cell; Atbash and reduction are absent from "not excluded"
- analysis/round19/G1/READY.md:72-75: 6 reductions x 2 signs x 2 directions x 2 Atbash per (generator, seed).
  round34/B1-orbits-v3/sweep.py:29,154; round35/B1-bash-orbit-pfv4/sweep.py:74,131: `$RANDOM % 29`, (C-K), forward, no Atbash.
- MEASURED-CEILING s.3 lists offsets and sign; the words reduction/scale29/rej29/Atbash/direction do not occur for the orbits
  (grep). Atbash is in Cicada's demonstrated repertoire (01.jpg atbash; 06.jpg atbash+3 - tests/validate.py) and Atbash'd or
  Caesar-shifted plaintext is invisible to the LM screen, so the true key dies at the screen. G4 (RESULTS s.5.2) at least
  named "c in {0,1} only".
- Cost: each variant = one orbit screen with C replaced by 28-C (or decode shifted); hours each for bash.

### 5. [UNDISCHARGED, cheap] `free` never applied to the persisted orbit survivors
- pf_v4 admits unconstrained skips (round35/I1-skip-tolerant-screen/pf_v4.py:12-33) but survivors are decoded under
  keyskip1/keyskip2 only (MEASURED-CEILING.md:51 "not `free`"). Constructions that are free-drift-shaped (delete-on-doublet,
  an unrelated draw, a canon indel) therefore pass the screen and are lost at the confirm. Survivor seeds are stored
  (263,572 rows). Cost: re-decode ~130k stored seeds under `free` at L>=240 where the free null is licensed: hours.
  (Not verified against R37 internals - flag for the R36-38 reader.)

### 6. [UNDISCHARGED] TeX Tier-1 default seeds never interpreted
- analysis/round19/G4/RESULTS.md:228 (pgf default seed `\time x \year` = 8,627 values, "enumerable - trivially"; random.tex date
  seeds 3,214,080), l.312 (the only run is a 10,000-decode pilot, year 2013, `interpretable: false`). LEDGER G4-TEX-RNG
  `reopens_if` names Tier 1 at "69,016 decodes, 2.0 h". R24-C2-EXT/R26-A used Cicada integers + dense-from-0 (covers
  \time x \year only for \time <= 9 min). R1 C-iv: TeX is the only generator with a generation-side (not availability) argument.
  MEASURED-CEILING.md:106 describes the TeX remainder as needing "a C or GPU port". Cost: ~2 h python.

### 7. [CONTRADICTION] hand vs machine (see premise note above)
README.md:173 / analysis/README.md:57 vs LEDGER D-01 `not_covered` vs round43/F3 TOOLKIT.md:110-117 vs FINAL-SYNTHESIS.md:75.
Matters because "machine loop consuming RNG draws" is the sole motivation for keyskip2 and for the whole PRNG programme.

### 8. [CONTRADICTION, low stakes] page-initial runes
round43/F2-inventory/image-channels.md:44 lists drop-caps p0 ᛁ, p15 ᛚ, p33 ᛗ+ᛟ, p54 ᚠ; canon first runes are seg0 ᛋ,
seg15 ᚠ, seg33 ᛞ, seg53 ᚪ (p3, p8, p23, p27, p40 agree). T1 read 15/17 initials = canon but calls the sub-path "not trusted"
(T1/RESULTS.md:251-253, 412-413, 470-472, 50 false positives); T2 leaves exactly these 15 slots unadjudicated (LEDGER A-01).
The 17 page-opening runes are the least-verified runes in the canon. F2a is an AI-vision read (likely the wrong side), but a
human glance at 17 glyphs is minutes. One wrong head rune costs one plaintext symbol, not sync.

### Tail (tidiness)
- T2/RESULTS.md:166-173 says the 487 mid-size marks are "proven non-textual by decryption ... canon is right not to transcribe"
  and leaves "whether they carry information" open (l.365, LEDGER R12-frontB reopens_if). Resolved here by arithmetic on
  T2/out_orphan.json: the 452 marks with h=58/59 equal the Y-rune count on **every one of 57 segments** (0 mismatches; corr 0.916
  before splitting) - they are the detached inner stroke of ᚣ (T1 s.2.2), i.e. textual and already transcribed; the 32 h=40
  marks = 14 double quotes x 2 ticks + 4 apostrophes (segs 6,7,22,40,42,43,52 and 4,21,35,41 - matches R43-F2b); 3 others
  (seg 10 h93 w70; segs 41, 48 h65 w50) unidentified. No hidden mark class. T2's prose is wrong, its verdict is not.
- derivedkey/RESULTS.md:17 notes the README "derived-key lane untested" line is stale (README still carries it at l.153-156
  inside a superseded block).
- redteam/RESULTS.md sub-audit (a): AN-END absent from the trust anchor - since fixed (validate.py now prints 73.jpg PASS).

---------------------------------------------------------------------------------------------------------------------
## Q2. I2 / I3 holes today
- I2 panel models are gitignored "rebuildable" (I2/RESULTS.md s.1) but the Welsh corpus was lost -> R19 panel (sha 14a23d36)
  retired; 44.138 % of the Py2.7 `exact` sweep judged under it was never re-scored. Tracked (MEASURED-CEILING.md:32,54).
- I3: G-PANEL FAILED (no single k_eff), G-RECOVER FAILED for `drift` on Old English, 71 PROVISIONAL cells - all superseded by
  the R34/R37/R41 nulls. Nothing untracked found.
- R1 A-iv (score/recovery decoupling) honoured in I1 (gates on recovery). R1 "structured wrong keys" follow-up: R20 R lane.

## Q3. Generators built in R19 vs later sweeps
| generator | later coverage | tracked? |
|---|---|---|
| bash 4.2 auto-seed set (LP64+ILP32) | swept R34/35/36/37; 4.0/4.1 by identity; 3.2, 5.1 R40/R42 | yes - but see Finding 3 (3.6 % of the cycle) and 4 (1 of 48 cells) |
| glibc random()/rand() | prior-dense 48,036 seeds (R32-B3); full 2^32 in R28-L4 queue, never fired | yes |
| lrand48 / drand48 / Perl | rigid English slice over 2011-2015 seconds (R10); ~25k prior seeds (R24, R26-A) | weakly (Finding 2) |
| TeX pgf / lcg / random.tex / pdfTeX | ~24k (R24) + ~750 (R26-A) | weakly (Finding 6) |
| Py2.7 string seeds (G3) | R28-L3 dictionary: inconclusive, artefacts absent | yes |
| `shuf --random-source` (58 LP2 JPEGs + PGP messages as source), `openssl enc -k` | **no later reference** outside R18-L1 and ledger snapshots (grep) | only in R19-G1 `not_covered` (NC-2, NC-6); small dictionaries, never run |

## Q4. Transcription
T1: LP2-typeface control 180/180; whole corpus leave-one-page-out 13,073/13,074 ordinary glyphs (the one = p27:93, settled U in
R33-B2); O/A/AE 0 confusions in 1,404; the 450: 450/450 agree with canon (MEASURED-CEILING.md:114 still says "450 located
O/A/AE disagreements never decided per instance" - that describes the pre-T1 state; T1 decided them by machine, a per-instance
HUMAN adjudication is what never happened). T2: indel bound k <= 1 insertion and <= 1 deletion at 95 % (0 candidates over 13,121
slots, power 0.990/0.974); crude ceiling 26 if every flag is charged to canon. Not covered: whole-line omissions, the 15-17
illuminated initials, LP1 typeface (95.09 % pooled, FAIL), one image lineage. Residual per-rune substitution bound for the
12,956 stream: ~1 known candidate; T3 shows statistics survive even 398 wrong runes; decode channel is the fragile one.

## Q5. Finite objects
C3 read all 109 bands (R18 stopped at 45): 74 RUNIC (mostly mis-grouped body text), 27 NON-RUNIC, 8 DEGENERATE; band reader
95.6 % on the LP2 face; RUNIC call is a coin-flip at <= 16 glyphs; P-9's "30 short bands" refuted (field-definition error).
256 non-runic tokens = the pp49-51 base-60 payload (C1 corrected 3 bytes). finite/ re-scored the 74 bands as plaintext under
the 9-register panel: 0/74; English registers never reach 0.80 power at band lengths; no Greek/Hebrew/Norse (tracked in
PROBLEM.json open list). p15 `3299` grey anomaly quantified (z ~ 92) but "not yet established as a property of the document"
(no second render) -> R44 P1/P2.

## Q6. See Finding 1. Every sweep from R20 to R42 (driftbeam, beam_v2, beam_v3, pf_v3/pf_v4, grind27/28, verify_solution.py)
decodes without an interrupter branch; none routes through src/lp/solve.py. F-as-interrupter jointly with a skip relation exists
in no LP2 decode relation.

## Checked and clean
- driftbeam.py transition algebra, histogram trick, pair mode, cnt reset; constructions.py vs R18 originals.
- I1 gates read against code (recovery-gated, lam window [8,12]).
- T1/T2 controls and the 487-mark class (resolved above).
- C3 PGP re-derivation (228 files identical verdicts) - headline only.
- redteam Oct lane: phi(prime) positional stream is in campaign18 rosetta sweep (not re-verified by me beyond the prose).
