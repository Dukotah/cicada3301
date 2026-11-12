# A1 — campaign-era cipher-structure partition: fresh-eyes audit notes (2026-11-12)

Scope read: analysis/ top-level campaign docs + loose scripts, structure/, foundation/ (index), armada/, armada20/ (index +
hill.py, task5.py), campaign14/, campaign18_skip/, stones/CAMPAIGN-V (for the multiplicative row), FINAL-SYNTHESIS.md,
docs/SOLVED-PAGES-AND-INTERRUPTERS.md, ELIMINATION-LEDGER master table A–C; cross-checked against LEDGER.json (309 rows),
MEASURED-CEILING.md, PICKUP-HERE.md, round24/PLAN.md, round18/L4, round40/C1, round43/F3+X0.
All paths relative to liber-primus unless absolute. Scripts I wrote are in this audit/ directory
(a1_checks.py, a1_checks2.py, a1_wordrep.py, a1_bandscan.py, a1_bandscan2.py, a1_bandpower.py, a1_comb.py); they use the
hash-verified loader ../lpdata.py. Everything below marked "measured here" is an UNREGISTERED exploratory audit probe,
not a lane result — a real lane must PREREG and re-run it.

---------------------------------------------------------------------------------------------------------------------
## 1. Findings, ranked

### F1 [CONTRADICTION + mis-tracked lead] The only long repeat in LP2 is recorded wrongly in every place it appears
What the data says (data/krisyotam_runes.txt; identical in all 6 lineages under analysis/foundation/trans_*.txt):
- ᛞᛄᚢ-ᛒᛖᛁ ("D J U • B E I") occurs at page 27 runes 28–33 (flat 6555–6560) and page 54 runes 70–75 (flat 12950–12955).
- Inside the 12,956-rune unsolved stream it is a **6-gram**. It becomes a 7-gram (…ᚫ) ONLY if segment 55 — the SOLVED
  AN END page, independently keyed by phi(prime) from its own first rune — is concatenated after page 54: page 54 has
  76 runes, so offset 70+6 = end of page. The 7th "match" is AN END's first ciphertext rune (A+phi(2)=AE), a 1/29 event
  across a join where the cipher demonstrably restarts.
- It is **word-aligned at both sites with identical word shape (3,3)**: p27 "…ᛒᚠ-ᛞᛄᚢ-ᛒᛖᛁ-ᚫᚠ-ᛈ-/", p54 "…ᚳᛉ-ᛞᛄᚢ-ᛒᛖᛁ./ & $".
- The second occurrence is the **last six runes of the last unsolved page**, closing a sentence ('.') and the final
  section ('&','$' markers; '$' ends sections at segs 2,7,15,22,26,32,39,54,55). The first occurrence is in the first
  body sentence of the section that STARTS on page 27 (seg 26 ends with '$'; p27 line 1 = title-like "3,12,4 ." sentence).
- No surrounding alignment: at the exact spacing 6395 the only matches near the site are the six runes themselves
  (window 6461..6560: 8 matches incl. the 6; whole-lag kappa z=-1.84).
What the repo says:
- analysis/ARMADA-20-FINDINGS.md:81 — "DJU BEI 6-gram repeat on pages 27/55 is chance (Poisson P≈13%)". The 13 % is the
  UNALIGNED 6-gram figure (expected 0.14). Nobody conditioned on the word alignment.
- analysis/round43/F3-hand-feasibility/KEY-LOCALIZATION.md:107-110 — calls it "the 7-gram ᛉᛚᛒᚱᛋᚳᛋ (X L B R S C/K Z-class)
  … expected count 0.005, p≈0.5%". The glyph string ᛉᛚᛒᚱᛋᚳᛋ occurs **0 times** in the data file (grep -c = 0); the length
  is 7 only across the p54→AN END join; the p-value is for that non-existent in-book 7-gram.
- round43/X0-firewall/ADJUDICATION.md:27,72, round43/SYNTHESIS.md:97, round44/CAMPAIGN-PLAN.md (lane R1) propagate
  "the p27/p54 repeated 7-gram … a free alignment anchor". R43 X1 "all stamps upheld" did not catch it.
Corrected statistics (a1_wordrep.py, measured here): 2,928 words (line-wrap-aware). Expected number of repeated
whole-word BIGRAMS with total length ≥6 under uniform content = 4e-5 (T≥5: 8e-4); observed 1 (this one). Single-word
repeats are at chance (L=3: 17 pairs vs 10.8; L≥4: 0 vs 0.19), repeated n-grams 2..5 at chance (z within ±0.8), so this
is not a general "word-level determinism" signal — it is ONE isolated, word-aligned, end-of-book repeat with a chance
probability of order 1e-4 (1e-3 after a generous look-elsewhere factor), i.e. 100x less likely than the 13 % on file.
Why it matters for solving: under the project's central model (fresh keystream + anti-repeat) an exact repeat can ONLY
be chance, so a 1e-4..1e-3 event is the single largest likelihood ratio in the ciphertext against that model and for
models with key-state recurrence or deliberate ciphertext reuse. R44-R1 (per-page/line resets anchored on "the 7-gram")
is about to pre-register against a mis-specified anchor: (i) the constraint is 6 runes, not 7; (ii) its strength comes
from word alignment + end-of-section position, not from length; (iii) the natural reset hypotheses it should test are
section-level ('$'), since site 1 is 28 runes after a section title and site 2 is a section's last words.
Checked not resolved: grep "DJU|7-gram|6-gram" over rounds 10–44, LEDGER.json (no row; X0 says so itself), PICKUP-HERE.
Cost: minutes (correct F3/X0/R44 text, add a ledger row with the right numbers; two image crops to confirm both sites
against the page renders, since all six transcriptions share one origin).

### F2 [LOGIC-GAP] "Long-period periodic key + the filter" was never tested; it was killed by an argument the repo itself voided
- analysis/round24/PLAN.md:83-93 kills C3 (periods 400–1500) "by mechanism … the doublet-deficit floor still refutes it.
  Same wall as every additive lane." That is exactly the argument ELIMINATION-LEDGER.md:113-122 marks **void** (Round 10
  B-16 / Round 12 D1: under the pinned construction the deficit is set by the filter, so it cannot discriminate key type).
  Every live lane in the project (PRNG, KDF, keytext) IS "additive + filter"; a periodic key is no different.
- The only periodicity measurements are campaign14/probes.py P1 (lines 40-56: single-lag kappa, flag if z>5) and P2
  (lines 58-75: rigid columns s[c::P]). Both are RIGID. Under key-skip (1 skip / ~35 runes) rigid columns lose phase
  after the first skip, and a lag-L coincidence peak is smeared over ~4·sqrt(0.028·L) lags.
- Measured here (a1_bandpower.py; English-in-runes plaintext, random period-p key, key-skip at 0.83; 5 seeds each):
  P1's ">5σ at one lag" rule detects p=41: 5/5, p=60: 4/5, p=100: 1/5, p=200: 0/5, p≥800: 0/5 (the same p=800 key under
  the REWRITE filter gives z=15.9 at lag 800 — so the CAMPAIGN-XIV claim "no periodic key … up to 2000 / no key reuse at
  any lag 1–6478" holds for rigid/rewrite constructions only, and for key-skip only up to p≈60).
  `attack.py vigauto` ("every periodic key 1–40 dead", ELIMINATION-LEDGER.md:104; SOLVE-ATTEMPT-FINAL.md §1) is per-page
  rigid column chi-square: zero power under key-skip; §2 there "closes collision-skip by logic" by assuming skips occur
  only at the 0.66 % surviving doublets — wrong, they occur at the ~2.8 % SUPPRESSED ones (superseded in spirit by
  Campaign XVIII, never marked).
- Measured here, drift-tolerant (a1_comb.py: sum of lag-band kappa over all harmonics k·p/(1+0.0288), band ±2·sqrt(r·L)):
  planted detection at the 95 % null: p=400 4/4, 800 4/4, 1200 4/4, 1500 3/4, 2000 1/4, 2500 0/4, 3000 1/4.
  REAL LP2: comb max 3.77 (p=800; null max over 160 delta-shuffle surrogates: mean 3.18, 95 % 3.98) → p=0.09, and it is
  below every p≤1200 plant (5.2–9.3). So: periodic key + key-skip is **negative for p ≈ 50–1500 at power ~0.75–1.0
  (English-like kappa), unmeasured above ~2000** (information-limited at N=12,956), exploratory, not pre-registered.
- Residual anomaly logged, not claimed: single lag-band 5425–5449 has +385 coincidences over 6,492 expected (band z=4.41;
  family-wise p≈0.02 over my band family, 300 surrogates; it is what drives the comb's p=800/5608/1121/559 candidates).
  Spread evenly along the stream; no section offset matches; a true period-5600 key predicts only z≈1.8. Most likely noise.
Why it matters: this is the one classical family the solved-page ladder points at (keyword → keyword+interrupter →
number stream) in its "long key" form, and it had zero valid coverage. Cost: ~10 s compute; a PREREG'd lane is an hour.

### F3 [SHARED-PREMISE, evidence-prior] The F-interrupter key-STALL is unrepresented in beam_v3/pf_v4 and missing from the position statement
- docs/SOLVED-PAGES-AND-INTERRUPTERS.md: on all three keyed solved pages (incl. the only keyed LP2-typeface page, AN END)
  a plaintext ᚠ may be left unenciphered and the key does NOT advance. That is a −1 desync; keyskip1/keyskip2/free only
  model +1/+2. README (Round 19 note) already measured "the sweep beam reads an interrupter page (AN-END) at ~14 %".
- Tracking: only as a token inside `not_covered` of R33-I1-REGISTER-AWARE-BEAM and R33-B3; `grep -ci interrupt` = 0 in
  MEASURED-CEILING.md (its list of unrepresented constructions omits it), PICKUP-HERE.md, handoff/PARKED.md; not in R44.
- Bound available for free (measured here): ᚠ count 458 vs 446.8±20.8 uniform → extra literal ᚠ = 11.6, ≤ ~50 at 95 %.
  So solved-page-rate interrupters (1.2–1.8 % → 155–233) are excluded at 7–10σ, but ~1 per page is allowed: enough to
  desync any whole-page/whole-book decode, and up to ~37 % of 120-rune heads at the bound (10 % at the point estimate).
  The 24-rune pf_v4 head of page 0 itself contains ᚠ at rune 7 (last rune of word 1) and rune 17.
Cost: hours — add an advance-0-at-ciphertext-ᚠ transition (cap by the ≤50 bound) to the `free` relation, plant, re-measure
power; state the bound in MEASURED-CEILING §1.

### F4 [INSTRUMENT-DEFECT, recurring] Word tokenisers that split at line wraps ('/'): 388 of 594 line breaks are mid-word
Correct (skeleton/wordlen_search.py:88, used by Round 8): 2,928 words, mean 4.42 runes, 99 one-rune words (3.4 %).
- campaign14/probes.py:129 (`elif ch in "-./ "`) → P5's "1-rune words: unsolved 10 % / solved 12 % / random 26 %"
  (CAMPAIGN-XIV-FINDINGS.md P5) is an artifact (true 3.4 %); the "directional positive evidence the plaintext is English
  prose" rests on it.
- campaign18_skip/word_skeleton.py:15-26 (`page_wordlens`: any non-rune char ends a word) → Lead 2's skeleton match saw
  3,316 pseudo-words; 65 % of lines inject a false boundary, cutting any true match into ~7-word stretches, with control
  ceilings of 8–12 and NO planted positive control (solved pages excluded by pages[:-2]). Superseded for the family by
  Round 8's correctly tokenised skeleton lane, but CAMPAIGN-XVIII-FINDINGS still cites it as "a strong null … regardless of
  the cipher model".
- round43/F3-hand-feasibility/KEY-LOCALIZATION.md:23,111 ("3,604 words, mean 3.51 runes/word, 536 one-rune words") — the
  same class of error in the newest round; none of the three numbers reproduces under either tokenisation (3,316 / 3.91 /
  318 split-everything; 2,928 / 4.42 / 99 correct).
Cost: minutes to mark; the defect class deserves one shared tokenizer + a CI test.

### F5 [LOGIC-GAP / CONTRADICTION] "Autokey positively refuted by simulation" (Campaign X) simulated one offset
- campaign10_otp_vs_autokey.py:63-69 simulates ciphertext autokey with K=0 only (seed lengths 1, 8) and concludes
  "no autokey construction produces the deficit" (CAMPAIGN-X-FINDINGS.md; ELIMINATION-LEDGER.md:129).
- src/lp/autokey.py:6-11 and DOUBLET-INVESTIGATION.md §3 state the opposite, correctly: c_i=p_i+c_{i-1}+K doublets iff
  p=-K, so the rate equals one plaintext rune's frequency and CAN be 0.66 % (EO 0.67 %).
- The valid refutation is elsewhere and is solid: the lag-1 difference stream is flat off zero (FINAL-SYNTHESIS iter 9),
  and — measured here — the lag-L difference AND sum distributions are flat for every L=2..400 (z sd 0.99; max 3.5/3.9
  over 400 lags). That excludes pure ciphertext-autokey/Beaufort-autokey with ANY primer length ≤400 and any constant
  offset, language-independently; plaintext-autokey is excluded by IoC (sum of two English letters is 1.06+, not 1.000).
  Not covered by any of this: feedback composed with an independent long key (collapses into the pad class), keyless
  history ≥4 (statistically invisible: 5-gram repeats 6 vs 4.3 expected), D-04 (open, tracked).
Fix is wording: cite the diagonal/lag-L flatness, not Campaign X's table.

### F6 [SHARED-PREMISE] Every decoder assumes the decrypted plaintext is forward, unrelabelled text
Beam skip-tracking, the pf_v4 head screen and the 12-register panel are all n-gram-LM driven. A correct key composed with
(a) a plaintext-side relabel other than identity/Atbash (Caesar +s as on the solved A KOAN page, affine, keyed alphabet),
(b) reversed or transposed plaintext, or (c) a reduction with a constant offset (rand()%29+1), decodes to text no LM in
the panel recognises, so it is rejected at the screen. Campaign-era sweeps tried sign/Atbash only; LEDGER.json has no
row for transposition- or relabel-composed keystreams (grep transposi/revers: none relevant); MEASURED-CEILING is silent.
A cheap order- and relabel-agnostic adjudicator exists in principle: under keyskip1 a skip is possible only where
K[j+1]-K[j] = c[i-1]-c[i] (key+ciphertext only, ~6.6 % of positions), so skip paths can be enumerated without an LM and
scored by decrypt IoC (invariant to any monoalphabetic relabel and any transposition). Cost: a day to build + plant.

### F7 [LOGIC-GAP, mostly superseded — tail]
- KEY-HINT-RESEARCH.md ("Principled exclusion: … the whole additive-keystream family … is ruled out by the doublet
  deficit") — same void argument as F2; the family was later re-run under skip (XVIII numeric, R11, R37-C3) so the
  conclusion survives; the passage carries no superseded mark.
- CAMPAIGN-XVIII-FINDINGS.md Lead 3: "key-skip is the only filter mechanism that desynchronises the key" — false in
  general (stalls, ciphertext deletion/haplography, null insertion); later rounds enumerate constructions, text unmarked.
- campaign18_skip/RUN-numeric.log:225-231: best −5.571 ('fib_4_17', 12 NOTABLE rows) reported as "in the noise band
  (null-max −6.82)" although −5.571 > −6.82; the bar was a 400-trial null applied to ~10^5 trials. The 12 rows are one
  key: Fibonacci mod 29 has Pisano period 14 and the two cycles are negatives of each other; a period-14 key is excluded
  by lag structure. Noise, mis-stated.
- stones/CAMPAIGN-V + COVERAGE-MATRIX "multiplicative: no closed multiplicative group mod 29" — (Z/29)* is a group of
  order 28; what was shown is that a bijective multiplicative SUBSTITUTION on prime values fails. A multiplicative/affine
  COMBINER with a keystream is untested (falls under F6).
- FOLLOWUP-TESTS.md #4 page-on-page in-depth is rigid; measured here instead: the first 24 runes of the 55 pages stacked
  by column have IoC·29 = 1.002 (z=+0.06) → no keystream restart at page starts (aligned prefix survives skips).

### Small negatives measured here (nobody had them on file as far as grep shows)
- Vertical adjacency (rune directly above, index offsets −3..+3 and right-aligned): equality 3.28–3.67 %, |z|≤1.2 → the
  anti-repeat rule is 1-D (reading order), not applied at layout time.
- Doublet positions: uniform over in-word/word/line/sentence boundaries (keep ratio 0.18–0.24 everywhere), no residue
  structure mod 2..40 in flat/page/line coordinates, gaps geometric, 0 triples; lag-11 equality is the global minimum
  over lags 2..180 (z=−3.1; page 29 has 0 of 9.2 expected) — consistent with look-elsewhere noise (dispersion χ² 63.6/55).
- Line-initial rune non-uniformity (χ²=81 here) is already explained by glyph-width line fill (round18/L4 confound_layout).
- Repeated n-grams 2..5 at chance vs delta-shuffle surrogates (z +0.3, −0.4, +0.3, +0.8) → keyless feedback of history ≤3
  excluded; bigram off-diagonal χ² 782.7/755.

---------------------------------------------------------------------------------------------------------------------
## 2. Pointed question 1 — per-family accounting
"Sees it under the filter?" = could the test have recognised the family if combined with key-skip anti-repeat.
| Family | What actually ran | Decoder / scorer | Control | Sees it under key-skip? | Re-run post-R19/R33? |
|---|---|---|---|---|---|
| Periodic key 1–40 | attack.py vigauto (SOLVE-ATTEMPT-FINAL §1) | rigid per-page columns, English 4-gram | synthetic len-7 key, no filter | NO (zero power) | keywords only (XVIII, ~620 words, legacy beam, English, fixed −5.5); never beam_v3/panel-R36; no MEASURED-CEILING row |
| Periodic 41–2000 / key reuse | campaign14/probes.py P1,P2 | rigid kappa / rigid columns | none planted | only p≲60 (measured here) | R24-C3 killed by void argument; a1_comb.py here: negative p≤1500 (exploratory) |
| Autokey (PT/CT) | DOUBLET-INV §3 brute 29×29×2×2; Campaign X sim (K=0); seek_autokey.py (5 fns); crib_autokey.py (24 openers); XVIII autokey_skip (45 primers) | rigid or legacy beam, English | synthetic recover; XVIII gate | structural refutation is filter-independent (flat lag-L differences) | R11-N1 → R37-C3: 24 CT-feedback configs under beam_v3+panel-R36 |
| k-history feedback | XIV P4 bigram χ²; ctfeedback_coeffs.py (linear k≤3, 3 pages) | statistic / legacy beam | planted a1=7 | k≤3 keyless: yes (n-gram repeats); keyed: no | D-04 open (tracked) |
| Differencing / integration | armada/FOLLOWUP #2; crypto_rigor.py C | parameter-free decode + IoC | none needed | yes (IoC, language-free) | not needed |
| Page-on-page keying | FOLLOWUP #4; IV kappa 0.0344; XVIII selfref smoke | rigid | "different-key control" | only at page starts (clean here) | all-pairs under beam: tracked REOPEN (R40-C1-R47) |
| Transposition-only | crypto_rigor.py B (widths 2–40, doublet re-measure) | statistic | — | yes (IoC + file-order minimum) | n/a |
| Transposition ∘ keyed layer | armada20/task5.py (prime columnar + short Vig/mono) | rigid, English | none | NO | never; no ledger row (F6) |
| Fractionation (bifid/Polybius) | r2_fractionation_signature.py | IoC of keyless bifid over English | — | keyless: yes; +long key: merges with pad class | never |
| Substitution / homophonic | IoC argument; XIV P4 | statistic | — | bijective: yes; many-to-few: D-03 open | D-03 open (tracked) |
| Polygraphic (Playfair-class, Hill) | r5_doublet_anatomy.py (parity split, digraph IoC; anchor PASS); armada20/hill*.py (2×2 exhaustive, 3×3 sampled) | statistic / rigid English | synthetic Playfair anchor | keyless: yes (digraph flatness) | never (not needed for keyless) |
| Multiplicative / affine | stones (prime-value closure) | argument + rigid | — | substitution: yes; combiner: NO | never (F6) |
| Mixed-alphabet tableau | none found (grep: only R43-F3 enumeration) | — | — | — | never |
| Nulls / interrupters | armada20 interrupter_search.py (#17), XVIII interrupter_skip (10 texts), crypto_rigor A (F-gap histogram), h1_interrupter_strip.py | rigid/legacy beam, English | XVIII gates | stall not representable in beam_v3 | never (F3) |

## 3. Pointed question 2 — what "autokey is refuted" covers
Argument + partial exhaustive tests, not one exhaustive test. Solid (language- and filter-independent): pure CT-autokey /
Beaufort-CT-autokey, any primer length ≤400, any constant offset (flat lag-L difference/sum spectra); PT-autokey of any
primer (IoC). Tested only as decodes (English, mostly rigid): Atbash/sign variants (§3 brute), 5 prime/totient feedback
functions, 24 crib openers, 45 primers under the legacy skip beam; no F-interrupter variant; Atbash+shift pre-layers
only as far as "atbash" flags. Campaign X's simulation is not evidence (F5).

## 4. Pointed question 3 — roadmap / open-avenue items
All OPEN-AVENUES items ran (vision re-read → R9/R19 T1; fractionation; skeleton → Round 8; AN-END OSINT). KEY-HINT leads:
run. NEXT-ARMADA-ROADMAP: Phase 1/2 → Round 11; X2/G1/X1/X3/X4/S3 → Round 22; A2 → Round 23. Not run, and tracked:
Phase 3 I1 all-pairs page-as-pad (R43 X0 REOPEN), D2 figural motifs / B2 non-turtle 2D (R22 not_covered), P0.3 dense-page
re-segmenter (superseded by R19 T1/T2). Campaign XIV proposals: all executed or tracked (D-02, D-03, D-04 open). Nothing
silently vanished that I could find; what vanished is the *marking* of superseded arguments (F2, F5, F7).

## 5. Pointed question 4 — where the deficit is inferred to be a FILTER on a pad
DOUBLET-INVESTIGATION §2–4 and Conclusion; CAMPAIGN-X (table: only "OTP + soft filter" matches); CAMPAIGN-XI Part 1
(suppression sweep → 0.83); structure/CAMPAIGN-IV §3 ("soft-rejection sampling reproduces the exact fingerprint");
CRYPTO-RIGOR B/C; FINAL-SYNTHESIS "Pinned construction"; LEDGER L7-C-G3-FLOOR-EXTENDED (min_d Pdp(d) floor).
Alternatives actually excluded there: unfiltered additive keys with plaintext-independent key (floor argument, additive
combiner in Gematria order only); keyless first-order feedback / fixed tables (flat differences, flat bigrams);
keyless polygraphic; rank/bump parameter-free inversions; Lehmer blocks. NOT excluded there: an intrinsic nonzero-step
construction driven by an independent uniform key (step zero only for one plaintext symbol — predicts doublet sites =
occurrences of one rare rune; rune-identity of doublets would still be uniform, as observed χ²=27.8/28); non-additive
(Latin-square) combiners, for which the "floor" is an assignment problem and can sit far below 1 %; non-linguistic
plaintext. The simulations all fit ONE parameter (suppression) to ONE number (0.664 %).

## 6. Section structure (for whoever aims R44-R1)
'$' = section end at segs 2,7,15,22,26,32,39,54 (55=AN END) → sections start at 0,3,8,16,23,27,33,40.
First-sentence word shapes at section starts: seg0 [8,5]; seg3 [2,11,3]; seg23 [2,6,3,5]; seg27 [3,12,4]; seg33 [2,8];
(AN END [2,3], PARABLE [7]); segs 8,16,40 open with long sentences. '&' appears mid-section in segs 3,6,14,33,38,49,52.
