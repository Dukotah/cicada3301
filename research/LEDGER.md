# RESEARCH LEDGER — Liber Primus (LP2) rigorous attack loop

Append-only. One entry per pre-registered test that reaches execution. Killed-before-execution
hypotheses go to `DEAD_ENDS.md`. This ledger is the source of truth for the cumulative
multiple-comparisons correction: **every executed statistical test ever run against the fixed
ciphertext must be counted here**, and any "surviving" result must clear a threshold corrected
across the full ledger, not per-round.

## Multiple-comparisons running tally

- Executed statistical tests logged in THIS ledger: **3** (Rounds 1, 2, 5; Rounds 3–4 executed no
  cryptanalytic test — all candidates killed at Gate #1)
- Loop re-pointed after Round 3 from ciphertext-only attacks to EXTERNAL leads (Round 4). Round 5
  added a standing SUPERVISING STRATEGIST role that generates genuinely-new attack surfaces each
  round, so the exhaustion trail keeps advancing for future researchers.
- Prior attack families (pre-ledger, from FINDINGS/SOLVE-ATTEMPT-FINAL/CRYPTO-RIGOR): ~20 families,
  hundreds–thousands of parameterized runs. Treat the effective prior test count as large; a new
  result at p < 0.01 is expected by chance somewhere in the accumulated search and is worth ~nothing
  without an order-matched-surrogate null and a corrected threshold.

---

## Round 1 — 2026-07-29 — H1 "Interrupter-as-doublet-breaker"

**Branch:** `research/round-1-interrupter-doublet`

**Question (from the Contrarian's load-bearing flag + Cryptanalyst H1):** The repo's headline doublet
deficit (0.664% vs 3.448% random, z ≈ −16.9) is measured on the raw stream with all 458 ᚠ (F)
interrupters left in. Since a null-ᚠ does not advance the key, are the interrupters themselves the
doublet-suppression mechanism — i.e. is the deficit an artifact of ᚠ *placement* between would-be
identical runes, rather than a property of the enciphered body?

**Pre-registration (fixed before any code):**
- Ground-truth anchor (required): decrypt canonical page 03 WELCOME with Vigenère key DIVINITY under
  the documented ᚠ-non-advance rule, and re-encipher to the EXACT known ciphertext (round-trip).
- Test statistic: `doublet%_deᚠ` = adjacent-doublet rate after deleting ALL ᚠ and rejoining
  neighbors; plus flank-identity rate (fraction of interior `a ᚠ b` with a == b).
- Null model (order-matched surrogates): 10,000 permutations of ᚠ positions holding the rune
  multiset and ᚠ count fixed (seed 3301).
- Decision threshold: CONFIRM iff `doublet%_deᚠ ≥ 2.9% AND > 99th percentile of surrogates`;
  otherwise REFUTE.

**Execution:** `liber-primus/analysis/h1_interrupter_strip.py` (seed 3301). Harness validated by the
ground-truth anchor (WELCOME 4/4 words; full 394-rune round-trip identical = True).

**Results (12,956 runes, 458 ᚠ):**
| statistic | observed | reference |
|---|---|---|
| doublet%_raw (ᚠ in) | 0.6638% | repo sanity ~0.664% ✓ |
| doublet%_deᚠ (ᚠ stripped) | **0.7602%** | threshold 2.9% |
| flank-identity (a ᚠ b, a==b) | 2.8889% | random 3.448% / unigram-collision 3.579% — *below* both |
| ᚠ frequency | z = +0.541 | not inflated |
| within-word non-ᚠ doublet (no ᚠ between pair) | 0.6364% | corroborating diagnostic |

Null (flank-identity, non-degenerate): mean 0.756%, sd 0.417%, 99th 1.887%. Note: the
`doublet%_deᚠ` arm of the surrogate null is **mathematically degenerate** (permuting-then-deleting ᚠ
always returns the identical non-ᚠ subsequence, sd = 0), so cond2 is ill-posed for that statistic.
This was disclosed by the executor without altering the verdict; cond1 (absolute 2.9% floor) resolves
the test on its own.

**Gate #2 verdict: NEGATIVE (H1 refuted).** cond1 fails by ~4× (0.76% vs 2.9%); two independent
diagnostics corroborate. Not INVALID: no goalpost move, harness anchored, refutation triangulated.

**ESTABLISHED (assumed → measured):** The low doublet rate is a **global, ᚠ-independent property of
the ciphertext body**. Removing all interrupters barely moves it (0.66% → 0.76%); the same
suppression appears within words where no interrupter can act (0.64%); interrupters do not sit
between identical flanks more than chance. Any future decryption model must treat doublet
suppression as intrinsic to the enciphered stream, NOT as an interrupter-insertion artifact.

**Also killed this round (pre-execution, Gate #1):** H2 (self-avoiding-LCG keystream) and H3
(doublet-triggered key stall). See `DEAD_ENDS.md`.

---

## Round 2 — 2026-07-30 — R2-H1 "Fractionation coordinate-plane dispersion signature"

**Branch:** `research/round-2-fractionation-signature` (stacked on round-1 branch for ledger continuity)

**Question:** Round 1 established the doublet deficit is intrinsic to the ciphertext body, which
points at body-level mechanisms. The Archivist found only *bifid* was ever run; trifid/Polybius were
closed only by the aggregate IoC-ceiling argument (fractionation tops out IoC·N≈1.4–1.5, can't reach
observed 1.00). Does the unsolved body carry a **period-locked autocorrelation signature inside a
decomposed coordinate sub-stream** — a dimension the aggregate IoC ceiling never measures — that a
trifid/Polybius fractionation would impose and a flat OTP-class keystream would not?

**Why this wasn't redundant (Gate #1):** the IoC ceiling bounds the *marginal* whole-stream
coincidence rate; it says nothing about periodicity *within* a coordinate axis. Non-decrypting
structural discriminator (no key search). Gate #1 killed two alternatives: the transposition-delta
re-measure (already answered by CRYPTO-RIGOR §B: columnar restores doublets toward random, file order
is the unique minimum; jbo already ran a spiral route) and the alternative-index-ordering battery
(anchor-refuted — five solved pages incl. LP2's AN END decrypt ONLY in canonical GP order).

**Pre-registration (fixed before code):**
- Statistic: `A_max` = max normalized autocorrelation over lags 2–40, over all coordinate sub-streams,
  across 3 grid packings (P = Polybius 6×5; T = trifid 3×3×3 layer-major; T2 = trifid col-major).
- Anchors: (1) synthetic trifid with a KNOWN injected period must surface as a super-threshold peak
  (harness sensitivity); (2) real solved LP2 page AN END must show no period peak; (3) aggregate
  IoC·N below the 1.39 bifid floor.
- Null: 10,000 order-matched surrogates (permute exact rune multiset through the same decomposition,
  seed 3301).
- Threshold: CONFIRM iff `A_max(real) > surrogate 99.9th pct AND ≥ 0.05 abs AND peak lag reproduces
  ±1 across ≥2 of 3 grid variants`; else REFUTE.

**Execution:** `liber-primus/analysis/r2_fractionation_signature.py` (seed 3301; ~13 min for the null).
Output: `liber-primus/analysis/r2_frac_out.txt`.

**Anchors:** (1) synthetic period-13 → peak at lag 39 (=3×13 harmonic, in-spec), A_max 0.0787 >
surrogate 99.9th 0.0384 → PASS. (2) AN END (85 runes) A_max 0.386 < its wide surrogate 99.9th 0.562 →
no peak → PASS (note: short page, provisional-quality control; decision weight sits on the
length-matched synthetic + the real corpus's own tight null). (3) IoC·N 0.9999 < 1.39 → coherent.

**Results (12,956 runes, 10,000 surrogates):**
| variant | A_max (sub, lag) | null mean | null p99 | null p99.9 | > p99.9? | ≥0.05? |
|---|---|---|---|---|---|---|
| P  | 0.0246 (col, 26) | 0.0211 | 0.0320 | 0.0376 | no | no |
| T  | 0.0284 (row, 18) | 0.0224 | 0.0330 | 0.0386 | no | no |
| T2 | 0.0284 (row, 18) | 0.0224 | 0.0330 | 0.0386 | no | no |

Real A_max (0.025–0.028) sits ≈ null-mean + 1.6 sd — inside the null bulk, below even the 99th pct.

**Gate #2 verdict: NEGATIVE (R2-H1 refuted, decision-grade).** No goalpost move, order-matched null,
harness validated by Anchor 1, robust to the cumulative multiple-comparisons correction (signal
doesn't clear the 99th pct, let alone 99.9th). Soft spot: the AN END control is underpowered at 85
runes, but the verdict does not lean on it.

**ESTABLISHED (assumed → measured):** Unsolved LP2 carries **no detectable period-locked fractionation
autocorrelation** (A_max ≤ 0.028, below its own tight length-matched null and far below the 0.05 floor)
in any of 3 coordinate sub-streams across 3 grid packings — upgrading the trifid/Polybius exclusion
from an IoC-ceiling *inference* to a direct coordinate-level *measurement*, consistent with the
sub-1.39 IoC·N.

---

## Round 3 — 2026-07-30 — R3-H1/H2 "Doublet-avoidant constrained Viterbi/DP decode" → KILLED at Gate #1 (nothing executed)

**Branch:** `research/round-3-dp-decode-killed`

**Target:** the repo's own #1-ranked untested avenue per completeness-critic §A / FINAL-VERDICT §5.1 —
a doublet-avoidant constrained Viterbi/DP decode (max-likelihood plaintext subject to c[i]≠c[i-1],
co-searching a short skip-key period 2–12), "the only hypothesis that predicts the delta=0 hole."

**Outcome: BOTH candidates KILLED at Critic gate #1. No test executed this round.** The critic verified
three fatal objections against the repo's own files:
1. **UN-ANCHORABLE (decisive).** The sub-chance doublet deficit is the ONE property separating unsolved
   from solved pages. Verified solved-page doublet rates (DOUBLET-INVESTIGATION §1): WELCOME 3.56%,
   koan 2.83%, A WARNING 2.73%, AN END 2.38% — all NORMAL, none sub-chance. A decoder whose novel
   mechanism inverts the deficit therefore cannot be validated on ANY known solve; it can only anchor
   its degenerate plain-keyed-Vigenère mode, which is already dead (all periodic keys 1–40). Per the
   loop's hard rule, an un-anchorable method is a keyspace search, not a method.
2. **DEGENERATE NULL.** First-difference entropy is near-maximal (4.831/4.858 bits; DOUBLET-INVESTIGATION
   §4). A surrogate preserving the unigram multiset AND the no-adjacent-repeat structure preserves the
   only non-flat statistic the corpus has → the surrogate null is unbeatable by construction (Δ>0 can
   only be multiple-comparisons noise). Same defect class as R1's degenerate deᚠ arm.
3. **ALREADY DONE / REVIVAL OF A DEAD END.** R3-H1's forward rule is character-for-character Round 1's
   H3 ("if c[i] would equal c[i-1], advance the key one extra step") — killed at Gate #1 with a standing
   revive-bar it did not clear. CRYPTO-RIGOR §C already ran the no-repeat/collision-inversion family
   (IoC_norm 1.037, no language); PICKUP-HERE lists it under "Do NOT re-run." R3-H2's latent-state
   marginalization does not clear H3's revive-bar (b) — marginalizing the stall-position search IS the
   position search, summed over. Note: completeness-critic §A / FINAL-VERDICT §5.1's #1 ranking is a
   STALE doc, superseded by CRYPTO-RIGOR §C + PICKUP-HERE + the Round-1 kills.

**Researcher (redundancy):** confirmed the specific constrained-DP-with-no-repeat technique appears in
no public solver (jbo, relikd, r4nd0mD3v3l0p3r, scream314, mortlach all do keystream/key search +
distributional scoring) and no 2023–2026 credible solve exists (DEF CON 31 talk confirms candidate keys
from solved pages do NOT unlock the rest). So the technique is publicly un-run — but "un-run publicly"
does not rescue "un-anchorable + degenerate + already-killed-here."

**PROGRAM-LEVEL CONCLUSION (declared this round):** The ciphertext-only attack program is **COMPLETE /
EXHAUSTED.** Across the pre-ledger ~20 families and 3 ledger rounds, the memoryless-keystream,
running-key, number-theoretic-keystream, autokey, fractionation (bifid + trifid/Polybius coordinate),
transposition, first-difference/integral, no-repeat-inversion, interrupter-channel, and stego families
are all eliminated with recorded reasons. The unsolved LP2 pages are **OTP-class**: a full-length
keystream with a deliberate no-repeat rule, information-theoretically **unsolvable from ciphertext alone
without an externally-held key**. The remaining rational moves are EXTERNAL, not cryptanalytic:
(a) obtain the key/seed (never published; may not exist publicly), or (b) an independent from-scratch
re-transcription — already attempted 3 ways (krisyotam/relikd/rtkd rune-identical; vision re-read failed
at alignment 0.145; SHA1 provenance 56/56). No ciphertext-only test can move this verdict.

**Also killed this round (Gate #1):** R3-H1, R3-H2. See `DEAD_ENDS.md`.

---

## Round 4 — 2026-07-30 — EXTERNAL leads (key/seed hunt + authorship) → 0 cryptanalytic tests; OSINT cold

**Branch:** `research/round-4-external-leads`

**Re-point rationale:** Round 3 proved the ciphertext-only program complete; the loop's own conclusion
named EXTERNAL material as the only live avenue. This round hunted for (a) an external LP2 key/seed and
(b) verifiable authorship evidence, keeping the auditor gates.

**External Key/Seed Hunter (web):** The one real external pointer — AN END's hash →
`gy3hoy2zizvuzvdb.onion` (Tor v2) — is **verifiably dead** (v2 deprecated Oct 2021; never archived
anywhere; monokro.me confirms "the trail goes cold at a door that no longer exists"). No credible
externally-distributed LP2 key exists; post-2021 community consensus leans "OTP / key withheld." The
only concrete candidate material: three primary-sourced strings the community logs as *never applied to
LP2* — the 2012 P.S. number (130 digits), two 2013 onion-cookie hashes (256-bit), and the missing-primes
set (73–1223). Source: krisyotam/cicada3301 `HINTS-NEVER-USED.md`.

**Fresh-Surface Cryptanalyst:** verdict **NO QUALIFYING SURFACE** — structural. No solved-page-anchored
method can produce the doublet deficit (every solved page has normal doublets), and any deficit-
consistent construction is un-anchorable; everything else is measured flat. The only open door is
Criterion 3's external branch, unsatisfiable without a real external key.

**Critic gate #1: 0 cryptanalytic tests approved.** The three external strings applied as an additive
key are not merely *inferred* dead but **empirically pre-measured** dead — DOUBLET-INVESTIGATION §2
already measured the additive family's doublet output on this ciphertext (prime 2.88%, totient 2.88%,
running-key 3.32%, Vigenère 3.44%) vs the 0.66% deficit (z≈−16.9); any additive key must land in that
already-measured normal band. So the Round-2 "inference→measurement" escape hatch does NOT apply (the
dimension is already measured). Anchor check: none of the three equals/generates a known solved-page key
(Atbash/Caesar/DIVINITY/FIRFUMFERENCE/totient) — settled by direct comparison, no experiment. Missing-
primes is a number-theoretic keystream, already dead. Auditor routed the strings to a non-cipher OSINT
pointer-chase (R4-OSINT-1) instead.

**Executed (OSINT only, no cipher/keyspace): R4-OSINT-1 pointer chase.** Result **COLD on all three:**
- 2012 P.S. number → RESOLVED as an artifact (a factored **RSA-130 semiprime**: p, q, exponent 65537,
  from the PGP-signed 2012 "Valēte!" message) but points nowhere; community records it "never used
  despite factorization." The "rotate 90° = 3301 / matrix" reading is UNVERIFIED speculation.
- 2013 cookies → opaque, provenance-verified to the final onion `p7amjopgric7dfdi.onion`, but explained
  by no source; no match to any onion/file/CT-log/AN END trail. (761/167 are just the Instar-Emergence
  audio id and its reverse — an internal cross-link, not an external referent.)
- Missing-primes → a clean contiguous prime interval (73–1223), indexes nothing per community analysis.

**Authorship Evidence Auditor (web):** The only VERIFIABLE identity anchor is PGP key `7A35090F`
(fp `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`), which **has never been controlled by any
identified party**, never rotated/compromised, last signed April 2017. No named individual — Schoenberger
included (controls no key; his own 2025 litigation filings retreat to "collective contributor") — is
verified as creator. Best evidence-supported inference: a small English-speaking, Western-esoterica-
literate, cryptographically sophisticated **cypherpunk/privacy collective** (2012–2017), held at
**LOW–MODERATE confidence, explicitly inferential**. 2024 "Cicada3301" ransomware and 2026 Zenodo "IA
Gemini translation" are unrelated / NOISE.

**Verdict: NEGATIVE (external leads cold).** No cryptanalytic test was rigorously runnable; the OSINT
chase found no live referent; authorship has no verifiable identity. This is the honest outcome, not a
process failure.

**ESTABLISHED (assumed → measured/closed):** The three high-profile "never-used" external cribs are now
definitively closed — as LP2 keys (additive application empirically pre-refuted by the deficit;
un-anchorable) AND as pointers (OSINT chase cold). The only external door (AN END onion) is verifiably
gone. Authorship: no verifiable identity exists; the creator is the anonymous, never-unmasked holder of
key 7A35090F.

---

## Round 5 — 2026-07-30 — NEW strategist slate → R5-COMBINED residual-doublet anatomy → NEGATIVE

**Branch:** `research/round-5-doublet-anatomy`

**New role:** a SUPERVISING STRATEGIST generated 5 genuinely-untested surfaces and verified via
`analysis/armada/recon-novel-attacks.md` that Playfair/digraphic, doublet position-parity, residual-
doublet anatomy, and lag-k≥2 spectrum appear in NO prior doc. Gate #1 killed #3 ROSETTA (non-English
plaintext) and #5 DELVE (placeholder-rune), approved ONE combined structural test folding #1 SEAHORSE
(Playfair parity) + #2 TIDELINE (residual anatomy) + #4 HALFTIDE (lag spectrum) — sharing one
order-matched null with a family-wide correction, in the Round-1&2 mold.

**Pre-registration:** non-decrypting structural test on the 86 residual doublets. Anchors: synthetic
Playfair-class positive must surface Δ_parity beyond surrogate 99.9th + within-pair hard-zero; solved
pages WELCOME & AN END must be clean. Statistics: S1 parity split (both phases), S2 digraph-vs-monograph
IoC, S3 doubled-rune identity χ², S4 inter-doublet gap KS vs geometric, S5 lag-k spectrum k=1..6. Null:
10,000 surrogates fixing exact multiset AND doublet count D=86 (seed 3301), reused across sub-stats.
Mandatory degenerate-null guard (R1 lesson). CONFIRM iff any non-degenerate statistic clears surrogate
99.9th pct (family-corrected).

**Execution:** `liber-primus/analysis/r5_doublet_anatomy.py`; output `r5_out.txt`. Surrogates realized
EXACT D=86 at 100%. Anchor 1 PASS (synthetic Playfair Δ_parity −0.027 at ~13σ, within-pair rate 0.000).
Anchor 2 PASS (WELCOME & AN END clean). S2 monograph arm correctly disclosed degenerate (sd=0) and
excluded.

**Results (12,956 runes, 86 residual doublets):**
| stat | observed | surrogate 99.9th | verdict |
|---|---|---|---|
| S1 parity Δ (both phases) | ±0.00185 (1.3σ; 37 within / 49 across) | ±0.00432 | REFUTE |
| S2 digraph IoC·N | 1.0306 | 1.0444 | REFUTE |
| S3 identity χ² | 27.79 (p=0.48; no dominant rune) | 56.57 | REFUTE |
| S4 gap KS vs geometric | 0.0765 (p=0.69) | 0.1600 | REFUTE |
| S5 lag-1 / lag-2..6 | 0.0066 / all ≈0.034 (chance) | 0.0395 | REFUTE |

**Gate #2 verdict: NEGATIVE (decision-grade).** Both anchors fired (sensitivity ~13σ, specificity on
two solved pages); no non-degenerate statistic cleared the family-corrected 99.9th; the S1 lean is
1.3σ noise that sign-flips between phases. Not INCONCLUSIVE (well-powered), not INVALID (no goalpost
move, real null, degeneracy handled).

**ESTABLISHED (assumed → measured):** LP2's 86 residual doublets carry NO Playfair-class digraphic-parity
signature (within-pair hard-zero absent), NO autokey/substitution fingerprint (χ² p=0.48, no dominant
doubled rune; digraph IoC below tail), GEOMETRIC/memoryless inter-doublet spacing (KS p=0.69), and a
no-repeat rule that is provably PURELY lag-1 with zero higher-order (lag-2..6) suppression. This closes
the polygraphic-cipher, two-track-interleave, and structured-doublet-placement families as explanations,
and sharpens the OTP-class verdict: the residuals look exactly like a pure lag-1 no-repeat rule over
otherwise-random text.

**Also killed this round (Gate #1):** #3 ROSETTA, #5 DELVE. See `DEAD_ENDS.md`.

---

## Round 7 — 2026-07-31 — RE-POINTED to win-condition B (authorship) + external-input rescout → stylometry feasibility CLOSED; external surface NULL

**Branch:** `research/round-7-authorship-stylometry`

**Re-point rationale (Novelty Scout / Organizer):** The ciphertext-only program is declared COMPLETE (Round 3, reaffirmed R4–R6); DEAD_ENDS bars new ciphertext rounds "without a genuinely new external input — absent that, every round will and should end NEGATIVE/KILL by construction." So opening another cipher round would be a budgeted no-op. This round instead works the two frontiers that are NOT formally exhausted: (A) a rescout for any new external input that could legitimately reopen the cipher, and (B) authorship — specifically a **computational-stylometry** angle that no prior round or public solver has tried (all prior attribution here is journalism-based OSINT). Lean 3-agent fleet (Sonnet), Organizer+Critic (Opus) gated all outputs.

**This round runs NO cryptanalytic test** (none is rigorously runnable absent a new external key — same Gate-#1 wall as R4). It logs feasibility/closure results, not a statistical decode. Multiple-comparisons tally unchanged (still 3 executed cryptanalytic tests: R1/R2/R5).

### Track A — External-Input Scout (win condition A): NEGATIVE, cipher remains legitimately closed
Swept 2025–2026 CicadaSolvers/GitHub/Zenodo/Uncovering-Cicada wiki/DEF CON follow-ups/Reddit/Tor-archive status. **Zero candidates clear the "genuinely-new external input" bar.** Every item is either ciphertext-derived, an unauthenticated personal translation, or historical reconstruction:
- **Zenodo "IA Gemini Final Translation" (Becker/OFFELLIA, 2026)** — AI-assisted ciphertext-only interpretation, no PGP signature, no delivered key. NOISE (reaffirms the R4 note). Bar: NO.
- **`53cr37-layer` "solve" → Solana token** (copycat `unc0vering-cicada` wiki) — **assessed HIGH-confidence crypto-SCAM**: no 3301 PGP signature, keys (DANAD/MIDBV) are ciphertext-derived, "plaintext" is a Solana address that postdates LP. **QUARANTINED as a named distractor** (see DEAD_ENDS). Bar: NO.
- Tumbleson Puzzle-3 Part 4 (Dec 2024), krisyotam/cicada3301 April-2026 archive commits, cmbsolver July-2025 binary-as-runes, DEF CON 31 — all historical/exploratory, no external input. `gy3hoy2zizvuzvdb.onion` still never archived. Last verified 3301 PGP-signed message remains **April 2017**.

### Track B — Fresh-surface authorship OSINT (2026 only): NO NEW SURFACE
No post-2025-12-04 court ruling, no new signed message from key 7A35090F, no new documentary/book/2026 conference talk/academic paper/insider leak. Only new datapoint: a possible Wayne County companion filing (25-012153-CZ) — partisan-sourced, LOW confidence, procedural only. Authorship verdict unchanged: anonymous cypherpunk/privacy collective, LOW–MODERATE, no cryptographic proof of any named individual.

### Track B — Stylometry feasibility (NEW angle): CLOSED as currently-infeasible (decision-grade NEGATIVE)
Question: can computational stylometry of the solved-page English prose discriminate authorship? **Answer: not at present.** The full solved LP English corpus is **~800 words** (A Warning, Welcome, Some Wisdom, both Koans, Loss of Divinity, An Instruction, An End, Parable). Published stylometry limits (Eder 2015 "Does size matter?"; Koppel et al. 2009) put the reliable floor at **2,000–5,000 running words**; below ~3,000 words false-attribution rates exceed 60%. The query corpus is ~¼ of the floor ⇒ any positive attribution result would be statistically meaningless. Anchoring note: this mirrors the rig's standing rule against un-anchorable keyspace searches — a positive stylometric "match" on 800 words is manufacturable by chance, the textual analogue of scoring readings for meaning.

**ESTABLISHED (assumed → measured):** Prose-style authorship attribution of Liber Primus is **information-poor, not just unattempted** — the solved corpus is too small for any standard method to beat chance. The strongest *available* authorship signal is not the prose but the **cryptographic-design taste** (MODERATE–HIGH): the design demands simultaneous competence in ascending-prime gematria, Anglo-Saxon (not Elder/Younger) futhorc, Euler-totient number theory, and Vigenère/interrupter engineering, wrapped in an integrated Zen-koan + apophatic-Gnostic + cypherpunk-privacy worldview. This fingerprint is culturally specific to the 1993–2000 cypherpunk milieu and is **consistent with — does not upgrade — the existing LOW–MODERATE cypherpunk-collective inference**. It matches no documented named individual's verified skill profile (Schoenberger's public profile shows the esoteric/musical side but no number-theory/crypto-engineering evidence; confidence he is the technical designer: LOW). No named attribution is supportable (HIGH confidence).

**Gate verdict: NEGATIVE on both win conditions this round, decision-grade.** No goalpost move; the stylometry closure rests on the method's published limits, not on a failed search. Honest outcome, not a process failure.

**Recommended next tests (bounded, deferred):**
- (B, cheap, runnable now) **Negative-space clustering** — Burrows' Delta / nearest-neighbour of the 800-word LP prose vs public-domain reference sets (Timothy May *Cyphernomicon*, Crowley, Zen-koan translations, Schoenberger's public blog). Exclusion results (LP does NOT cluster with X) are robust in small-sample regimes even when positive attribution is not. Label as EXPLORATORY, not decision-grade.
- (B) Monitor dockets 26-000013-MZ / 25-012153-CZ for identity-relevant discovery.
- (A) Re-run the external-input scout only when a *new* signed artifact/key surfaces; do not reopen ciphertext attacks.

**Also logged this round:** `53cr37-layer` Solana scam quarantine; Becker/OFFELLIA Zenodo noise reaffirmed. See `DEAD_ENDS.md`.

---

## Round 8 — 2026-08-06 — RECONCILED onto canonical origin/master; SECURITY/FORENSICS lane → S1 NEGATIVE, S2 INCONCLUSIVE

**Branch:** `research/round-8-artifact-provenance` (based on `origin/master` 8319e24, NOT the stale
June-20 base the round-1–7 branches used).

**Reconciliation (why this round changed base):** The round-1–7 rigor-rail branches were built on the
pre-refactor master (b1762307, 2026-06-20). Meanwhile `origin/master` advanced to a fully reconciled
archive (the "Loop iter 1–11 / FINAL-SYNTHESIS" lineage, `liber-primus/ELIMINATION-LEDGER.md`) that had
INDEPENDENTLY reached the same terminal verdict (LP2 OTP-class, unsolvable-by-design; authorship
un-attributable) AND had already worked most of the security/forensics lane. Owner confirmed GitHub is
the source of truth, so Round 8 rebased onto origin/master and carried `research/LEDGER.md` +
`DEAD_ENDS.md` forward. The Archivist reconciled BOTH kill-logs so nothing was re-derived. Two
independent lineages converging on the same NEGATIVE verdict is corroboration, not new progress.

**Holdout marked (owed, not consumed):** AN END (LP2 p56, φ-totient) reserved as the blind anchor for any
future LP2 decode method (see `OPEN_QUESTIONS.md`). No Round-8 hypothesis proposed a decode, so the
holdout was not consumed. Solved-plaintext ground-truth locations pinned for agent seeding.

### Fan-out → Gate #1 (max 2 approved, default KILL)
Cryptanalyst returned an honest NULL (no new anchorable ciphertext attack exists; both residual avenues
are external, not pre-registerable). Lateral provocations P1–P5 all KILLED at Gate #1 as re-skins of
executed/refuted work: P1 = R5-S4 inter-doublet-gap (already geometric, p=0.69); P2 = closed F-channel
family; P4/P5 = Campaign-XIV '/'-line false-positive + message-existence-undecidable; P3 = pp49-51 pad
(exhausted, underpowered). **FORWARD: S1, S2** (both forensic — no holdout, no ciphertext touched, real
controls, verified genuinely novel against the actual code). Web scout: **zero** new external input
(last 3301 PGP signature still April 2017); confirmed the Smirnov-filter and Burrows'-Delta-exclusion
findings have **no published prior art** (so those remain non-redundant if ever run).

### Executed (deterministic, seeded 3301) — `research/experiments/r8-01-*`, `r8-02-*`
**S1 — ICC-profile interior parse (generation-tooling fingerprint).** The APP2/ICC blob (byte-identical
across all 56 pages, len 2576, valid `acsp`) was structurally parsed for the first time (prior work only
recorded `has_icc=true`). Result: `creation_datetime` all-zero; no manufacturer/model/creator/profile-ID;
no Ghostscript build-version tag; text tags only `desc="Artifex Software sRGB ICC Profile"` +
`cprt="Copyright Artifex Software 2011"`; standard 10-tag minimal sRGB set. The script's auto-VERDICT
mis-fired "POSITIVE-DATABLE" on the static 2011 copyright — a token the pre-registration EXCLUDES;
overridden per the fixed decision rule (see `EXECUTION-NOTE.md`, no goalpost move).
**Gate #2: NEGATIVE.** No new datable/tooling/operator info. Side-benefit: the *stock Artifex sRGB
profile* structurally CONFIRMS the Ghostscript/Artifex renderer (upgrades STEGO-VERDICT's prior
strings-based claim to a structured-parse basis); `platform=APPL` is hardcoded in this stock profile and
is NOT a Mac-operator signal. Missing gs positive-control does not INVALIDATE — the null rests on
directly-observable absence-of-tags.

**S2 — JPEG DQT page-membership (production-batch / OPSEC test).** Two DQT fingerprints (33 vs 23 pages),
never tabulated by page. Pre-registered Wald–Wolfowitz runs test: **R=11 vs E[R]=28.1, z=−4.77,
Monte-Carlo two-sided p≈0** (100k perms, seed 3301) → DQT label assignment is strongly non-random w.r.t.
page order. Pre-registered file-size confound: MW U=278, z=−1.69, **p=0.091** (groups not size-different
at p<0.05); Spearman(page,size)=0.288. The pre-registered rule mechanically returned SURVIVES.
**Gate #2 OVERRODE mechanical SURVIVES → INCONCLUSIVE** (a *more conservative* verdict, not a goalpost
move to manufacture a positive): (a) the switch pattern is blocky/**alternating** (~11 blocks, single-page
flips at 49/53) — NOT the two contiguous batches the hypothesis assumed; the shape argues for per-page
content-driven table switching. (b) byte-size is a weak proxy for the DCT complexity that actually drives
GS quantization-table choice; p=0.091 is an under-powered non-rejection and cannot affirmatively clear
the confound. **Zero ciphertext bearing** (doublet deficit / OTP-class verdict untouched); does NOT
reopen the closed program.

### Round verdicts & counts
- S1: **NEGATIVE** (decision-grade). S2: **INCONCLUSIVE** (positional fact reproducible; batch-vs-content
  unresolved — resolving measurement pinned in `OPEN_QUESTIONS.md`).
- **Cumulative rigorous CRYPTANALYTIC tests executed (this round-loop lineage): 3** (R1/R2/R5) —
  **unchanged**; Round 8 added **2 executed FORENSIC tests (S1/S2)**, 0 new cryptanalytic. Multiple-
  comparisons tally on the ciphertext family is unchanged.
- **Most useful thing learned:** the forensic/provenance surface on the LOCAL artifacts is now
  near-exhausted at the file-metadata layer — the images are the stock-Ghostscript-sRGB render, carry no
  operator metadata, and the one non-random structural fact left (DQT page-membership) lives entirely in
  the JPEG-encoder layer, downstream of any glyph/cipher content. Attacking "the system, not the cipher"
  did not find an operator slip in the bytes we hold; it confirmed the toolchain and produced one
  benign-until-disambiguated encoder artifact.
