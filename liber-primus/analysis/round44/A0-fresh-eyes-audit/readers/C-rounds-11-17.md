# Fork C — fresh-eyes audit of Rounds 11–17 (2026-11-12)

Scope read: round11 (PREREG, SYNTHESIS, N1–N5/S1 RESULTS, n5.py, lib_numchannel.py), round12 (CAMPAIGN-PLAN, A1, C1 + code,
D1, D2 + g3_floor_probe.py, D3, frontB, A2 runbook), round13 (B04 RESULTS/GATE-NOTE, B05), round14 (both files + git log),
round15 (CAMPAIGN-PLAN, SCORER/FINDING), round16 (SYNTHESIS, zeroFP RESULTS), round17 (SYNTHESIS, P4_filter RESULTS).
Cross-read where a pointed question required it: round37/C3 rescore.py + RESULTS, round33 beam_v3.py, round32 beam_v2 ADVANCE,
round19/I1 constructions.py, campaign18_skip (skipdecode.py, COVERAGE-MATRIX, armada2/numeric2_skip.py header),
round43 F3 (measure.py, measurements.json, KEY-LOCALIZATION.md, ENUMERATION.md), round43 X0 ADJUDICATION, LEDGER.json rows.
All scripts I wrote are in this directory (C_*.py); they import the hash-verified loader `../lpdata.py`.

---------------------------------------------------------------------------------------------------------------------
## A. Findings (ranked)

### 1. [CONTRADICTION] The "repeated 7-gram p27:28 / p54:70" that Round 44 lane R1 wants as an alignment anchor is a 6-gram
- Claim: round43/F3-hand-feasibility/KEY-LOCALIZATION.md:107-110 — "One genuine long repeat: the 7-gram ᛉᛚᛒᚱᛋᚳᛋ (X L B R S C/K
  Z-class) occurs at page 27 offset 28 and page 54 offset 70 (expected count 0.005, p≈0.5%)". Propagated to
  round43/X0-firewall/ADJUDICATION.md:27,72 and round44/CAMPAIGN-PLAN.md:24 ("free alignment anchor", "in no ledger row").
- Measured on the canonical 12,956-rune stream (sha 0233…1585): the rune string ᛉᛚᛒᚱᛋᚳᛋ does not occur anywhere in
  data/krisyotam_runes.txt. At exactly those two locations there is a repeated **6-gram** ᛞᛄᚢᛒᛖᛁ (D J U B E I), p27[28:34] and
  p54[70:76]. p54 is 76 runes long, so the repeat is the LAST SIX RUNES of the unsolved corpus. No 7-gram repeats exist inside
  pages 0–54. The 7th match only appears if the solved AN END page is concatenated: AN END's first cipher rune is AE, and
  p27[34] is AE.
- Cause: F3 was a firewalled lane whose own toolkit classified no page as solved: measurements.json has total_runes 13136,
  solved_pages [], 57 "unsolved" pages, doublets 89; ENUMERATION.md:19 states "Unsolved pool: 56 pages, 13,041 runes" (= 12,956
  + AN END's 85). The canonical corpus is 55 pages / 12,956 runes / 86 doublets (PROBLEM.json). F3's "89 residual doublets",
  "13,041 key values" and the 1,540 (=C(56,2)) cross-page kappa pairs all include the solved totient page.
- Significance of the real object: expected number of repeated 6-gram pairs in 12,956 filtered-uniform runes ≈ 0.14–0.16
  (my MC null: mean 0.1, max 2 over 200 sims; real = 1, z = +2.4 on a Poisson-like count) → P(≥1) ≈ 0.13–0.15, not 0.005.
- Why it matters: R44-R1 and X0 REOPEN #4 treat the repeat as a p≈0.5% "state re-entry" crib. At p≈0.14 it is an
  unremarkable coincidence; it should not steer the reset lane's design or be used as a pass/fail anchor.
- Check that it is not already corrected: grep "7-gram" over round43/round44/PICKUP-HERE/LEDGER.json — every mention repeats
  the 7-gram; R43 X1 ("stamps upheld") did not catch it. Script: C_repeats.py + inline check in the transcript.
- Cost: zero compute; text corrections in 4 files + a ledger note.

### 2. [LOGIC-GAP] The only repaired-instrument coverage of the Round 11 totient/prime streams is 3 aligned starts, and X0 stamped
###    "prime/totient family with per-page parameters" CITED on it
- Round 11 itself is RIGID (see finding 3). The repaired-instrument re-run is round37/C3-rescore-reopened/rescore.py:
  n5_cfgs() (lines 340-352) → for each of 8 generators × 2 signs × 29 additive offsets: "continuous" windows at flat starts
  0, 4800, 9600 with `Kw = K[s:s+1024]` (line 233), plus per-segment restarts on pages 18 and 36 only.
- The 4800 and 9600 windows are vacuous under the relations they are decoded with: a continuous key under key-skip has drifted
  by ≈138 and ≈277 key positions by then (R18-L2 drift 373.6 ± 19.6 over the book); beam_v3 has start_slack 0 for
  keyskip1/2 (round32 beam_v2.py:34-36), max_skip 8 and admits a skip only if the skipped key value reproduces the previous
  cipher rune (beam_v3._drive). So 928 of the 2,320 rows/relation (40 %) carry zero power; aligned coverage = book head
  (p0[:120]), p18[:120], p36[:120]. LEDGER R37-C3-U6A-N5.not_covered says only "5 windows per keystream".
- round43/X0-firewall/ADJUDICATION.md:30 (item 7, proposed independently by blind agents A4-H2 and F3-J2) stamps
  "Prime/totient stream family with per-page parameters (solved-page curriculum continued)" **CITED** citing R11-N2/N5,
  R37-C3-U6A, R22-C X4 (6 page starts under beam_v3: rescore.py:761), R26-C (semantic seeds, offset 0 only) and B-04, with the
  comment "the exact per-page start index + direction + interrupter grid is the repo's oldest and most-rerun family".
  That is true only of the LEGACY instrument (Campaign XVIII: 874 number-theoretic streams × 55 pages × offsets 0–4,
  keyskip1 beam, English quadgrams, fixed −5.5 bar, best −5.57 — COVERAGE-MATRIX.md:58, armada/numeric_skip.py). Under
  keyskip2 + panel-R36 the per-page grid is 3/55 page starts for the N5 zoo and 6/55 for the X4 trio; no reverse direction
  for N5; no page-dependent start index.
- What is left that is worth running (finding 4 removes a large part): page-DEPENDENT parameterisations only — start index or
  additive constant a function of page number / running rune count / page gematria sum — × generator zoo (N5's 8 +
  Campaign XVIII's 874) × all 55 page starts and the &/$ section starts × keyskip1/2 × panel-R36.
  Cost: ~5×10^5 L=120 decodes ≈ hours on one core (R26-C ran 4,274 rows in 166 s). Finite.

### 3. [CONTRADICTION / INSTRUMENT] Round 11 used no beam at all; the ledger says it did
- `grep -l beam round11/*.py round11/*/*.py` → nothing. n5.py:157-161 decodes `(idxs[i] + sign*(ks[i]+offset)) % N`
  (one key value per rune); N4 keystream mode and N1 likewise. Every Round 11 plant is an unfiltered encrypt/decrypt round
  trip (n5.py:205-216) — easier than the hypothesis "stream × anti-repeat rule". The AN END control only checks the head
  `startswith("ANENDWITHIN")` and scores −5.282 because the rigid path loses alignment at the interrupter (offset 56).
- LEDGER.json rows R11-N1…S2 `coverage`: "scored through lib_numchannel and the legacy skip beam"; ELIMINATION-LEDGER.md:968
  repeats it ("English-only, legacy-decoder bounds"). By doctrine §4.3 a rigid decode scores a correct key at −6.835, so the
  N4-keystream and N5 halves of Round 11 had ~no power under key-skip (they remain valid under the REWRITE construction,
  where the key stays synced — D1). Round 11 SYNTHESIS.md still says "Do NOT re-run … closed the same way the letter channel
  is" with no superseded marker in the file.
- Cost: text fix; the substantive gap is finding 2.

### 4. [NEW KEYLESS MEASUREMENT — narrows R44-R1 and several old sweeps] Same-state key resets are excluded for ANY additive key
- If the key returns to the same state at each unit start, column j of all units is "in depth" (shared K_j) and the
  column coincidence rate rises from 1/29 toward the plaintext IoC. Script C_reset_depth.py (+ plants inline):
  | unit | columns | real z | planted z (English + shared random stream + soft key-skip) |
  | page (55) | 0–9 | +0.76 | +12.9 … +15.6 |
  | page | 10–29 | +0.44 | +7.2 … +11.8 |
  | line (594) | 1–4 | +0.91 | +92 … +98 |
  | line | 5–14 | +0.51 | +100 … +110 |
  sentence (217) cols 0–14, word (2,928) cols 0–4, &/$ sections (62): all |z| < 2 (no plants run for these).
  Line column 0 alone shows z = +7.1 — the known typographic line-initial width bias (R18 C-02), not depth; col 1 +2.3.
- With a per-page ADDITIVE constant allowed (C_reset_depth_offset.py; statistic = coincidences among first-W column
  differences of page pairs): real z = +1.0/+1.8/+0.7/+0.5 (W = 8/12/16/24) vs plants +3.3 … +5.2 (W ≥ 12). Disfavoured at
  roughly 3–4 σ, not excluded.
- Consequences: (a) "the same stream restarted at every page" is dead for every generator and seed at once — that is the
  hypothesis B-04 Stage C spent 3,548,160 decodes on (504 seeds × 55 per-page restarts), the Campaign XVIII fixed-key ×
  55-pages design, and N5's per-segment mode with a common offset; (b) R44-R1 need not sweep identical per-page or per-line
  resets at all — only resets to page-/line-DEPENDENT states survive; (c) cross-page pad reuse was already measured flat at
  full-page offset 0 by R43-F3 (on its 56-page corpus); line/sentence/word/section starts and the plant powers are new.

### 5. [LOGIC-GAP] R12-C1's plaintext-/mixed-feedback negative rests on a false "lock-on" argument (but is mostly rescued)
- round12/C1/sweep.py:15-18 and RESULTS.md: pt/mix seeds are swept over the 29 all-equal seeds only, justified by "a genuine
  autokey would still light up because after a short transient the correct-family key locks on". For plaintext feedback a
  seed error never dies out (for f = sum it is a persistent linear recurrence), so the sweep has power for 29 of 29^k
  seeds. control.py:47-52 plants seed [7,11,2] and decodes with the same seed handed over, so the control never tested the
  sweep's own seed probe. The ledger row discloses the 29-seed bound but keeps the lock-on rationale; X0 item 1 cites R12-C1
  for the hypothesis all six blind agents converged on.
- Seed-free replacements I ran:
  * ANY function of the previous k ciphertext runes (CT-feedback, arbitrary f, no external key): context-conditional
    coincidence rate, C_ctxioc.py. k=1: z=+0.9; k=2 (lags 1,2): −0.65; k=3 (lags 1,2,3): +0.10 (null from 300 filtered-
    uniform sims). An English-shifted context distribution would give ≈0.06 → about +40 σ at k=2 and +7.5 σ at k=3.
    This generalises C1's ct-source result from 7 named f to all f for k ≤ 3.
  * Keyless PT-feedback: repeated n-gram counts, C_repeats.py / C_ptfeedback_power.py. LP2: 4-gram repeat pairs 124 vs
    null 122.1 ± 10.4 (z=+0.19). Planted pt-source with RANDOM seeds: k=2 z≈+76, k=3 ≈+18, k=4 ≈+3.4…+6, k=6 ≈0
    (conservative: order-3 Markov English under-produces long repeats). mix-source: no power (state has unbounded memory).
  * None of the keyless feedback plants reproduces the doublet deficit (3.1–5.8 %), so the class needs a filter on top anyway.
- Residual: mix-source and k ≥ 5 pt-source are covered for all-equal seeds only. Low prior.

### 6. [SHARED-PREMISE] The soft leak is an external iid coin with supp = 0.83 in every plant of this era
- campaign18_skip/skipdecode.py:61-83 `encipher_keyskip(supp=0.83, seed=3301)`: the keep/reject coin comes from a separate
  `random.Random(3301)`, never from the keystream. Every R12–R17 control (D3, B-04 G2, B-05, A1, R16 KDF/PRNG/F-01, R17
  P0–P3) uses it. R17-P4 calibrates the real per-attempt supp at 0.8131 (keep 0.187 ± 0.02 → compatible with 3/16, 1/5,
  5/29…6/29; not with 0.83's 0.17 at better than ~1 σ either way).
- No lane in this era asked what IMPLEMENTATION yields a ~19 % leak. Things I checked that do not explain it: mixture of
  filtered/unfiltered units (doublet counts are not over-dispersed at 10/20/30/50/100/236-rune blocks, lines, sentences —
  if anything slightly under-dispersed: lines with ≥2 doublets = 3); rune identity (86 doublets over 28 runes, χ²≈26/28 df;
  2-character runes carry 24/86 ≈ 7/29); boundary class (within-word keep 0.180 vs cross-word 0.232, p=0.32); position
  residues mod 2..40; an unreduced-sum check (predicts ≈1.15 % → ~148 doublets); a no-repeat 5-bit draw (would confine
  doublets to F/U/TH). Later rounds (R19-I1 `coin_from_key`, skip_by_two) model the coin inside the keystream for one draw
  order; a per-rune coin (constant stride 2) is a different relation — defer to the fork covering Rounds 19/33.

### 7. [DROPPED-LEAD] The stronger haplography instrument was started in Round 14 and abandoned without a record
- round14/A03-haplography/explore_width.py is a complete script: fit line ink-width = Σ per-token advances on solved pages,
  read residuals in px, flag lines whose measured width exceeds canon's prediction by one advance. Its output
  (explore_width.json) was never committed; round16/A-03/RESULTS.md does not mention it; no ledger row. Round 16 A-03
  substituted three count tests with K_bound = 26 merges (margin 3.6× vs K_needed = 93) and its row excludes
  "insertions/dittography".
- Since R18-L1 established the pages are typeset Ghostscript renders, a width regression can verify canon's rune COUNT
  on every one of the ~600 lines to ±1 glyph. Count errors (unlike identity errors) are fatal to any keyed decode past the
  error, and no audit covers count on 100 % of lines (R9: 38.4 % count-exact lines; R12 frontB forced-count failed its
  control at 12.9 %; all public transcriptions share one origin — Campaign III). It would also test R43-F3 #37
  (hard rule + dittography) at the 86 sites. Needs data/relikd images + geometry/glyphs2.npz (gitignored). Cost: hours.

### 8. [LOGIC-GAP, superseded in effect] R17-P4 §9(4) / R17 SYNTHESIS "first independent confirmation of the skip-aware beam's
###    cipher model against the real data"
- The battery measures only emitted-ciphertext statistics (flat, unscoped, single-lag suppression). Key-skip, value-rewrite,
  two-draws and coin-from-key constructions are identical under every statistic in it, so nothing about key-pointer
  behaviour was confirmed. R18 L7-B later showed the beam was exact for one construction only; the sentence still stands
  in round17/SYNTHESIS.md and P4_filter/RESULTS.md §9.
- Pointed question 4 answer: D-01's statistics are lag-2..8 bleed (z=+0.65; bound 1.70 % at 95 %), windowed χ² under-
  dispersion (W=58), inter-doublet gap CV, page homogeneity; controls are iid-uniform, the coded filter, a line-scoped
  filter and six "human randomness" rungs. It excludes human-generated randomness (power ≥0.99 for any rung with bleed)
  and a line-scoped rule (power 1.000). It does NOT discriminate a rejection filter from a deterministic construction with
  an intrinsic lag-1 exclusion; any such construction that is flat at lags ≥2 is "machine" by this battery.

### 9. [UNDISCHARGED / tracking defect] RECON-A G-02 (OutGuess blank control) lost its ledger row to an ID collision
- LEDGER.json G-02 is now the corpus signature-verification table (status measured); its own `$note_on_id` says the
  collision "should be resolved on merge". The RECON-A item (round10/RECON-A/REGISTER.md:89; STEGO-VERDICT.md:78-91
  "decisive next experiment"; round15/CAMPAIGN-PLAN.md lane 5) survives only in handoff/PARKED.md:669, whose text says the
  blocker ("no Linux box") evaporated. `jq 'select(.status=="never-run")'` no longer returns it. X0 REOPEN #15 covers the
  keyed-extraction half, not the blank control. Low prior (stego).

### 10. [CONTRADICTION, minor] H-01 head-malformation sub-test
- round16/zeroFP/RESULTS.md: "Raw HTML files are not held locally … INCOMPLETE"; LEDGER H-01 (never-run): "Raw HTML is held
  locally"; round10b/PA-3/ARTIFACT-INVENTORY.md:129 lists the files (a gitignored fetch). Same pattern as E-01, where R19
  found the "missing" moduli had been on disk all along. Minutes once the fetch is present. Low prior.

### 11. [CONTRADICTION, wording] "≥1.38 % plaintext-independent floor" (PROBLEM.json measured_statistics.note)
- The G3 floor min_d P(ΔP=d) is KEY-independent and plaintext-DEPENDENT; 1.38 % is the KJV value (round12/D2/
  g3_floor_probe.py uses four English corpora). Recomputed from the committed panel-R36 trigram LMs (C_floor_registers.py):
  EN_MODERN 1.57, EN_KJV 1.57, LP1_REAL 1.68, LATIN 1.56, OE 2.10, DE 1.22, CY 2.16, EN_HALFVOWEL 1.78, EN_NOVOWEL 1.25,
  GREEK 1.82, HEBREW 1.65, NORSE 1.81 (%; smoothed LMs, so slightly high). All above 0.664 %: the conclusion holds for all
  twelve registers, the number does not. The inequality is sign-agnostic (any ±P±K, Beaufort included, because it is a
  minimum over d) but assumes the identity alphabet and a key independent of plaintext and ciphertext.

### 12. [TRACKING OMISSION] MEASURED-CEILING §3 does not list the non-PHP R16-PRNG generators or R8's rigid full-2^32 rows
- R16-PRNG (.NET System.Random, ISAAC, BBS×2, LFSR32, Geffe; 1,877 daily seeds; legacy keyskip1; English) is not cited
  anywhere on MEASURED-CEILING.md; its "not excluded" line 106 names glibc/Perl/TeX/Py2.7 tails only. The residue is named
  in LEDGER R28-L4-UNSWEPT-GENERATORS-QUEUE.not_covered. R8's nine full-2^32 generator sweeps (rigid; R19-G3-CORRECTION)
  are likewise absent; note they DO hold under the rewrite construction (key stays synced), a statement nobody makes.

---------------------------------------------------------------------------------------------------------------------
## B. Answers to the pointed questions

**Q1 (Round 11 number channel).** Families: N1 cumulative-gematria feedback (PT/CT × f∈{mod29, totient, digitsum} × sign ×
fwd/rev × continuous/per-page); N2 prime-gap and prime-index of the rune's OWN prime and their cumsums read as data (not as a
positional key); N3 whole book/segments as integers; N4 digit planes of the runes' primes (bases 3/5/7/10) as key and as
text; N5 positional φ(φ(p_i)), λ(p_i) (= the AN END stream; additive offset sweep 0..28 also covers p_i itself),
φ(Σp), φ(φ(Σp)), λ(Σp), φ(i), plus two rune-indexed cousins. Not in Round 11: Fibonacci, π/e digits, μ/σ/τ, Collatz,
positional prime gaps as key (Campaign XVIII ran primes/φ/gaps/Fibonacci/π/e/φ-digit streams — 874 — under the legacy
skip beam). Index origin: global from book start ("continuous") and per page; every rune counted (no interrupter-skipping
variant); no per-word/line/section origin (recon i7 had 16 rigid reset cells at % . /). Direction: N1 only. Decoder:
rigid everywhere in Round 11. Skip-aware composition: legacy keyskip1/English in Campaign XVIII (55 pages, offsets 0–4);
repaired instrument only via R37-C3 at 3 aligned starts (finding 2).

**Q2 (Round 12 D1/D2/D3).** D2 reproduces (I re-derived 12,956 / 86 / 0 cross-page / flat lags 2–600 independently).
Floor: see finding 11. D1's rewrite row is in COVERAGE-MATRIX.md:24-42; D3's three corrections are in README and
ELIMINATION-LEDGER.md:22,40,67-77,274-276. B-16/B-21 actioned. Not propagated: Round 11 SYNTHESIS.md itself.

**Q3 (R16/R17 re-decodes).** B-04, R16-KDF, R17-P3 pad list: regenerated and re-decoded by R40-B3 under pf_v4_12 + beam_v3
keyskip1/2 + panel-R36 — matches MEASURED-CEILING lines 61/67 (R17 P1/P2 not regenerated, stated there). R16-PRNG: not
re-decoded and not on the page (finding 12). F-01: R40-C1 partial re-decode, stated. B-05: voided by three wrong payload
bytes, found and re-run by R19-C1 (b05_rerun.py) — clean.

**Q4.** See finding 8.

**Q5 (Rounds 13–15).** R13 ran B-04 (6,224,300 decodes), B-05 (70,680) and the scorer POC. R14 is abandoned scaffolding:
two files, first committed 2026-10-30 (26c4446); zeroFP/PROGRESS.md has four unticked tests and claims a PREREG that is not
in the tree; its lanes were re-homed to round16/zeroFP and round16/A-03 (E-01 finished only in R19; H-01 still never-run;
explore_width.py dropped — finding 7). R15 is a plan + KDF prereg/code + SCORER finding; all six planned lanes ran as
Round 16/17 (KDF, A-03, scorer, F-01, zeroFP batch, PRNG; D-01 as R17-P4; A-06/C-02 in R18).

---------------------------------------------------------------------------------------------------------------------
## C. Checked and clean
- Foundation numbers (D2): reproduce. Lag scan 2–600 has sd(z)=1.00; off-diagonal bigram χ² z=+0.7.
- R17-P4 numbers reproduce (my page-homogeneity under-dispersion z=−1.52, p=0.061; W=290 p=0.10) and the mild
  over-uniformity is not consistent across scales (W=232 z=+0.74) → noise (C_underdispersion.py, 3,000 sims).
- Interrupter holds (which beam_v3 cannot represent: `base = pa + 1`): bounded by the F count. 458 F vs 446.8 ± 20.8
  expected → cleartext-F interrupters ≤ ~54 at 97.5 % (point estimate 12); LP1 density (10 in 798 runes = 1.25 %/rune →
  162) is excluded at 7 σ. Solved keyed pages: first interrupter at offsets 47/49/56; 10 of 26 cipher F are interrupters.
- Page-0 head windows used by the orbit sweeps contain no visible doublet (first at offset 122), so the kept-doublet
  variants (coin_from_key, dittography) do not bite the L=120 screen there; 28/55 pages have a doublet inside their first
  120 runes, so per-page head decodes are exposed.
- B-05 payload-byte void → discharged by R19-C1. E-01 → completed R19. D1/D3 propagation → done.
- mruzuki / A2 runbook → tracked (PARKED I-01, R18-L8, R19-C3).

## D. Premises this era never tested
1. The soft coin is external to the key generator and iid; supp fixed at 0.83 (measured 0.813).
2. Combination is ±key mod 29 on Gematria index order (identity/Atbash only); no keyed alphabet, no arithmetic on prime values.
3. Key consumption is monotone, ≥1 per cipher rune, extra advances only at rejected doublets (no holds; no spurious
   cipher runes — the dittography reading makes the 86 doublets insertions).
4. One stream origin at page 0 rune 0, or an identical restart per page; never a page-dependent schedule (start index or
   constant as a function of page number / running count).
5. English plaintext, fixed −5.5 bar, one head window deciding each key (later rounds repaired the first two).
