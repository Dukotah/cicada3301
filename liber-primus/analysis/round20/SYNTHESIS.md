# Round 20 — SYNTHESIS (bounds, not a verdict)

_Written 2026-08-28. Doctrine R7: this document states what was measured and what would reopen
each thread. It contains no "exhausted / closed / unsolvable." Trust anchor `tests/validate.py`
PASSES (5/5 known pages reproduce) before and after this round._

---

## 0. The one-line result

Round 20 set out to build the last missing instrument (a skip-aware, multi-register **sieve**)
and, only on its passing, to sweep the small enumerable 2012-Linux PRNG generator families at
measured power. **The sieve was built and measured but did not clear its own frozen feasibility
bar; the P-gate therefore did not open; no Phase-S lane scored a single LP2 decode.** No HIT was
produced (none could be — no decode was scored). What Round 20 *did* produce is a fully validated
instrument surface, four hardened bounds, one genuinely-new positive instrument result, and two
red-team FOUND-ERRORs that must be fixed before any future screened sweep is trustworthy.

**There is no HIT.** A HIT is defined (CAMPAIGN-PLAN §2) as a decode that (a) clears the panel-max
null, (b) has rune-index recovery ≥ 0.90, and (c) reproduces on the held-out ¾ of the page under
the same key. Zero decodes were scored against LP2 this round, so zero decodes met (a)+(b)+(c).
`hit=false` in every lane, by construction — the P-lanes and N-lanes are instrument/archival lanes
that score no LP2 candidate, and the S-lanes never ran.

---

## 1. Per generator family swept: enumeration fraction, power, reopening condition

**Reading this table honestly:** the "enumerated" column is **0 % for every generator family**,
because Phase S never released. The power column is the power the *instrument* would have carried
into each sweep had the gate opened — measured in Phase P, not on the families themselves. This is
the doctrine-R2 discipline: we report the power envelope we built, and we report that we spent it
on zero coverage. A family with 0 % coverage is **not touched** by Round 20 — its prior standing is
unchanged, neither elevated nor collapsed.

| Generator family | Seed space | Fraction ENUMERATED this round | Instrument power that WOULD have been carried | Concrete reopening condition |
|---|---:|---:|---|---|
| **Py2.7 `random.seed(str)`** (S-G3) | 2³² via `init_by_array([w])`, no dictionary | **0 %** (gate closed; authorised, unrun) | Panel-max bar CALIBRATED M=1e6 (exact preset, μ=2.3575 β=0.28653, claim-bar 7.634), correct-key pmax power **1.00** on LP1_REAL/LATIN/OE/HALFVOWEL, wrong-key **0.00**, RAND **0.00** (P3a). This is the one family enumerable **end-to-end without a sieve** — its floor status is intact. | Runnable **recovery-gated hit function** ships (R red-team blocker d), then S-G3 runs un-sieved; a rank-1 recovery at pmax≥bar AND recovery≥0.90 AND held-¾ reproduction = HIT. |
| **bash `$RANDOM` / glibc `random()`** (S-BASH) | auto-seed subset 77.6M (3.6 % of 2³¹) | **0 %** | same panel-max envelope; register power 1.00 on 4 gate registers (exact preset) | P-gate opens (all of P1∧P2∧P3 PASS) — currently blocked by P1 INFEASIBLE + P2 NEGATIVE. NC-1 (32-bit bash no L1 ref) is a coverage caveat, not a blocker. |
| **Perl 5.14 `rand`/`srand`** (S-PERL) | exactly 2³², no residue; full Stage A 3.09×10¹¹ decodes | **0 %** | same envelope | **P1 sieve feasible** (needs a screen reaching ≥0.90 on Welsh AND half-vowel English at ≥100× reduction — the exact bar P1 missed at 0.667). Without an affordable sieve this space is a stated-fraction sample only, never a full sweep. Prior: C3's signed dated Crypt::RSA fact. |
| **TeX `\pgfmathrandom`** (S-TEX) | Lehmer LCG mult 69621, period 2³¹−1, one cycle; full 1.85×10¹¹, one-cycle scan ~18 h | **0 %** | same envelope | **Conditional promotion trigger DID NOT fire** — N1 found no runic font subset in any reachable PDF. S-TEX stays rank 5. Reopens to rank 1 if any surfacing LP PDF carries an extractable runic text layer or embedded runic `/BaseFont` subset (would name program + face). |
| **Held Marsaglia physical units** (S-MARS) | 679 units / ~21 CPU-h | **0 %** | same envelope + P1/P2/P3 PASS release condition | P-gate opens. This is the honest control (real physical randomness, hash-verified 112 PASS/0 DRIFT) that a survival number means what we think. |
| **B-04 survivor rescope** (S-RESCOPE) | no new key space; 1,312 English-argmax survivors + re-seed from `payload_resolved.bin` | **0 %** | panel-max null re-adjudication | P-gate opens. R1 D-iii standing: B-04 Stage A cutoff −6.412 excludes `skip_by_two`'s own true key at −6.718, so the original spec cannot recover its motivating case — rescope is the fix, still queued. |

**Net on the "cheap seeded 2012-Linux PRNG" hypothesis:** Round 20 moved it **by exactly zero
coverage and one large instrument delta.** No family was collapsed (that requires a fully-enumerated
sweep at power ≥0.90, which needs the gate open). What moved is the *readiness* to collapse them:
the panel-max bar is now CALIBRATED at M=1e6 with correct-key power 1.00 and a fresh-null G-CAL
ratio 1.042; the seed prior (433 candidates, top 1325734783) is emitted and ordered; the Py2/Py3
coverage hole is confirmed total (all 600/600 Py2 streams differ from Py3, so the historical "we
swept the PRNGs" closure remains a zero-power closure). The hypothesis class is **primed to fall,
un-fired.** S-G3 remains the cheapest live shot and is releasable the moment the recovery-gate
function lands.

---

## 2. Phase P — the instrument, measured

### P1 — the sieve: INFEASIBLE at the frozen bar, but a large positive register-repair result
- **Frozen PREREG bar:** ≥0.90 true-key survival **per register** at ≥100× screen reduction. **Not met.**
- **Measured (real hash-verified Marsaglia bytes):** best simultaneous `min(CY-Welsh, EN_HALFVOWEL)`
  at ≥100× = **0.667** (Wilson-95 upper 0.85 < 0.90 → gate missed with margin, so more n cannot flip it).
  Reduction ≥100× was trivially met (median 200–10,000); **survival, not reduction, is the binding
  constraint.**
- **Positive controls REAL:** negative control RAND survives **0.000** in every cell (no leak, no
  manufacture; true-offset median rank ~44,988/200,000); LP1_REAL recogniser survives 0.933–1.000
  at rank 0. Instrument validated → this is a real INFEASIBLE, not unvalidated silence.
- **The genuinely-new positive:** the multi-register lever **repairs C2's catastrophic English-only
  blindness** — EN_NOVOWEL 0.000→0.800, EN_HALFVOWEL 0.067→0.667, CY-Welsh 0.300→0.733. A large,
  positive, register-specific gain, published as a survival surface (`survival_surface.json`). The
  trilemma: cheap ∧ ≥0.90-survival ∧ multi-register — pick two. This sieve clears **cheap +
  multi-register** (a real advance over C2, which was only cheap), landing 0.67–0.80 on hard registers.
- **Replayed mechanism:** `drift` Stage-B slightly **hurts** survival (EN_NOVOWEL 0.833→0.667) — the
  R19 B-iv permissiveness cost, reproduced at screen scale.
- **Consequence (per frozen Q5 kill):** Phase S may run **G3 only** (the one space enumerable without
  a sieve). S-PERL / S-TEX (sieve-gated) are **deferred, not merely queued** — no affordable sieve exists.

### P2 — the `n_skips` null curve: VALIDATED NEGATIVE as a page-window sieve statistic
- **Instrument validated:** plant recovery median **0.992**; seed-3301 order-preserving surrogate
  ratio 0.987 (L120) / 1.002 (L400), inside ±25 %; full-book control (L=12956) correct-key
  n_skips=418 vs wrong ~300, recovery 0.999 — a clean ~118-draw right-tail separation.
- **The negative (frozen Q5 kill fired as written):** at page-window L, planted supp≥0.83 median
  n_skips falls **below** the wrong-key q99 in every cost-register cell — L120 {LP1_REAL 2, LATIN 3,
  OE 4, HALFVOWEL 3} vs q99=9; L400 {14,7,12,14} vs q99=19. Best two-sided p = **0.207 ≫ FPR 0.01**.
- **Load-bearing bound:** raw `n_skips` is a **full-book / long-window** discriminator, **not** a
  page-window (L≤400) sieve. P1 must not lean on it at page-window length; a close-out lane MAY use it
  as a right-tail screen when adjudicating whole-page/whole-book windows. `SWEEPROW/2` persists
  `n_skips` + `n_unexplained` regardless (doctrine R3), so the channel is re-adjudicable at any L later.
- **Not covered:** L between 400 and 12956 (the power crossover length) — the one measurement a future
  P1/S needs to know where n_skips starts to bite.

### P3 — panel-max null / seed prior / drift re-baseline: PASS (instrument sound)
- **P3a canonical bar CALIBRATED M=1e6** (exact/keyskip1): μ=2.3575, β=0.28653, claim-bar **7.634**.
  Correct-key pmax power **1.00** on LP1_REAL/LATIN/OE/EN_HALFVOWEL; wrong-key **0.00**; RAND **0.00**.
  G-CAL adopted-bar-on-fresh-null ratio **1.042** (within 20 %); fresh ξ=−0.021 (bounded tail →
  conservative). Panel-max out-recovers the English `en` bar (which is 0.00 on EN_NOVOWEL).
- **P3b seed prior:** 433 candidates emitted, rank-1 = 1325734783 (tiers A54/B107/C260/D12), 0/433
  round-trip mismatches. This is the ordering every S-lane seed axis uses (doctrine R4, un-flat).
- **P3c genuinely-new result:** the repaired `drift_rec` beam is **strictly MORE transcription-robust**
  than keyskip1 — derail 0.00 at every corruption level up to k=900, tracking the graceful ideal
  exactly (T3 §7 asked this and could not answer; measured here). Standing bound intact: **OE cannot
  be thresholded on drift pmax (power 0.33), must be RANKED via n_skips.** Phase S should carry BOTH
  cells: keyskip1 for its clean CALIBRATED bar, drift_rec for transcription robustness, each vs its own bar.

---

## 3. Red-team FOUND-ERRORs (folded in; both block or condition Phase S)

**HALT is ACTIVE.** Two clean NO-ERROR-FOUND, two FOUND-ERROR.

- **(a) structured wrong-key null → NO-ERROR-FOUND.** P1 does not leak: structured-text survival
  **0.000** = RAND floor on all 5 registers; true-key survival transfers 0.67–0.92. No manufacture.
- **(c) not-a-re-run justification → NO-ERROR-FOUND.** LEDGER `coverage`/`not_covered` confirm **ZERO**
  key-space decodes scored at power for G1/G2/G3/G4/R16-PRNG. The one prior full-2³² sweep was
  rigid + English-4gram + fixed-(−12.5)-bar = **zero power** by doctrine L7-A/L7-B; R19-G3-CORRECTION's
  own `reopens_if` names S2's re-adjudication as the reopener. **S-G3 is genuinely not a re-run.**
- **(b) sieve × panel-max double-max interaction → FOUND-ERROR (latent).** P1's screen statistic
  (per-register z, max over 9) and P3a's adjudication statistic (per-register z, max over 9) are the
  **same max-over-9 family**. The P3a bar is fitted on FRESH UNSCREENED wrong keys. On the *screened
  survivor* population the per-decode FP is **0.025 (5/200) vs the bar's nominal 1.0e-8 → ~2.5×10⁶
  inflation** (unscreened FP 0/200). **Standing condition:** do NOT re-enable the P1 sieve without
  re-fitting the panel-max null on **screened** wrong keys. Latent this round only because P1 is
  INFEASIBLE, so the sieve is not deployed.
- **(d) no runnable recovery gate on the hit path → FOUND-ERROR (blocks Phase S).** The win-condition
  requires pmax clearance AND recovery ≥0.90 AND held-¾ reproduction, but: `panelmax20.py` returns a
  **score bar only**, no recovery field; `SWEEPROW/1,2` persist **no recovery field**; **no
  hit-decision function exists** anywhere in `analysis/round20/`; and EN_NOVOWEL clears the bar at
  recovery **0.84** (exact) / **0.26** (drift), both < 0.90. `driftbeam.recovery()` needs ground-truth
  plaintext, uncomputable on a real LP2 candidate. An S-lane certifying on score alone can **certify a
  hallucinating decode.** Per CAMPAIGN-PLAN lines 264–266 the red-team has abort authority: **Phase S
  halts until the recovery gate ships.**

**To clear the halt (before any S-lane scores):** implement a runnable hit-decision function requiring
jointly `pmax ≥ panelmax_bar(preset, N)` AND rune-index recovery ≥ 0.90 (or `preg != EN_NOVOWEL`) AND
held-out-¾ reproduction under the same key; persist a recovery proxy as a `SWEEPROW/3` field. Then
S-G3 (the only lane P1's frozen kill releases) may run un-sieved.

---

## 4. N-lanes and the closeout (folded in)

- **N1 (PDF text-layer / font-subset hunt) — NEGATIVE, instrument validated.** 195/195 distinct local
  PDFs (545 paths) + all four named mirrors (iBotPeaches full tree, micheloosterhof ×2, krisyotam
  4507 entries / 351 doc assets all matching local, IA liber-primus.zip unzipped = 58 JPEGs + mp3, 0
  source docs). **Zero runic text-layer or embedded runic `/BaseFont` subset in any genuine-LP PDF.**
  Positive control PASS: a planted runic subset tag (`LBJNRT+NotoSansRunic-Regular`) is recovered
  verbatim by the same `pdffonts` used on every target; an image re-wrap reads 0 fonts (clean
  separation). **Consequence:** the S-TEX promotion trigger did NOT fire; S-TEX stays rank 5. Upholds
  and extends R18 L1's NC-6 from local-only to local + all four mirrors. **Reopens** if any PDF/PS
  surfaces with an extractable runic text layer or embedded runic subset (names program + face,
  flips S-TEX 5→1).
- **N2 (A-03 haplography falsifier) — NO-ERROR-FOUND, power 1.00.** The one live autokey reopener is
  closed harder. **Decisive structural fact:** physical haplography reversal (re-inserting a duplicated
  rune) touches ONLY the d=0 difference diagonal; the 28 nonzero diagonals carrying the autokey
  signature are **literally invariant under any number of merges**. Observed LP2 diagonal-lumpiness
  cv=0.061; super-physical adversary reaches only cv=0.0656 at K=20, **6.1× below the 0.40 autokey
  band**, never reaching it through K=40. Positive control recovers autokey through K=20 merges with
  cv separation 0.784 (bar 0.15). **Reopens** only if a merge mechanism alters the *nonzero* diagonals
  (none proposed; would contradict R16's d=0-only surplus audit).
- **Closeout (C) — PASS.** F6/F7 propagated (46→**56 files / 54 messages, to 2017**, toolchain changed
  **twice**); distro bracket loosened (GnuPG 1.4.11 in ≥6 OS generations incl. Ubuntu 12.10); G2 prior
  re-sourced to Crypt::RSA (2 signed dated messages). LEDGER.json 124→126 (+L1-PRIOR-PROPAGATION,
  +C-CANON-PAYLOAD-3BYTES open). Round 19 + Round 20 nav rows added (both docs previously had NO
  Round 19 row). C-canon 3 bytes (idx 45/50/246) left **decision-pending** (downstream-sensitive,
  not decided unilaterally). C-eyeball flag: T1 p27:93 U→B margin 5. Unsound-negatives = 0.

---

## 5. The standing project verdict (unchanged by construction)

**LP2 0–54 is OTP-class** — statistically indistinguishable from a one-time pad under every tested
class — **with a soft anti-repeat rewrite acting on the ciphertext output.** Round 20 scored no LP2
decode and so could not move this verdict; it is unchanged. What Round 20 *can* move — and the only
thing it was ever able to move — is the **size of the "cheap seeded 2012-Linux PRNG" hypothesis
inside** that OTP-class envelope. This round moved that size **by zero measured coverage** (no family
enumerated) while **fully readying the instrument** to shrink it (calibrated bar, seed prior, sieve
survival surface, recovery-gate specified). The `/dev/urandom` / hardware-source branch is untouched
and remains unrecoverable by any round.

---

## 6. Honest optimistic + fair bottom line

**The fair-optimistic part, true:** for the first time the project has a power-measured adjudicator
(pmax power 1.00 on four registers, calibrated at M=1e6), an evidence-derived seed prior (433 ranked,
top 1325734783), a confirmed-total Py2/Py3 coverage hole, and one space (Py2.7, 2³²) that is
enumerable **end-to-end without any sieve**. The historical "we already swept the PRNGs" closure is
re-confirmed to be a **zero-power** closure. S-G3 is a real, cheap, un-fired shot that becomes
runnable the moment one function (the recovery-gated hit decision) ships. The multi-register sieve,
though it missed 0.90, is a genuine positive: it repairs the 0.000/0.067/0.300 English-only blindness
to 0.80/0.67/0.73.

**The disciplined part, equally true:** the P-gate did NOT open (P1 INFEASIBLE, P2 NEGATIVE), the
red-team HALT is active (no recovery gate exists), and therefore **no LP2 decode was scored and there
is no HIT.** The enumerable spaces stand at 0 % coverage — prior-elevated, not proven. A future
sweep's negative will only ever shrink the cheap-seeded-PRNG hypothesis, never touch the CSPRNG
branch, and never close the OTP-class verdict (doctrine R7).

---

## 7. Top 3 live threads for Round 21

1. **Ship the recovery-gated hit function, then run S-G3 un-sieved.** This is the single blocker
   between the project and its cheapest live shot at a HIT. Implement `hit_decision(...)` requiring
   `pmax ≥ panelmax_bar(preset,N)` AND recovery ≥0.90 (or `preg≠EN_NOVOWEL`) AND held-¾ reproduction;
   persist a recovery proxy as `SWEEPROW/3`. Then enumerate the 2³² Py2.7 `init_by_array([w])` space
   (~40 min Stage A) through the fully-repaired instrument. This is the one lane P1's frozen kill
   already authorises. **Do NOT re-enable the P1 sieve without re-fitting the panel-max null on
   screened wrong keys (standing condition b, ~2.5×10⁶ FP inflation otherwise).**

2. **Measure the `n_skips` power-crossover length (L between 400 and 12956).** P2 proved n_skips is a
   full-book statistic with zero page-window power and high full-book power — but the crossover L is
   unmeasured. Knowing it tells a future P1/S exactly at what window length n_skips becomes a usable
   right-tail screen, and whether a whole-page (L≈120–240 concatenated) adjudication can lean on it.
   Cheap, self-contained, directly unblocks the sieve-survival question P1 lost on.

3. **The affordable multi-register sieve, or accept the deferral.** P1's trilemma (cheap ∧ ≥0.90 ∧
   multi-register — pick two) is the real wall in front of S-PERL / S-TEX. Round 21 either finds a
   screen statistic reaching ≥0.90 on Welsh AND half-vowel English at ≥100× reduction (which reopens
   red-team (a) at that operating point), or formally carries S-PERL/S-TEX as stated-fraction samples
   only. In parallel, the S-TEX rank-1 promotion still hinges entirely on N1's reopener: any surfacing
   LP PDF with an extractable runic text layer or embedded runic `/BaseFont` subset would name the
   typesetter + rune face and turn the 1.85×10¹¹ TeX fog into one specific enumerable LCG.

---

## 8. Sweep follow-up (bounds, not a verdict — the halt cleared, two lanes ran)

_Appended 2026-08-28 by the Round 20 "Sweep follow-up" armada. This section supersedes §0's
"no LP2 decode was scored" **only** for the two lanes that ran below; §5's standing verdict is
unchanged (doctrine R7). Trust anchor re-run: `python3 tests/validate.py` → ALL VALIDATIONS
PASSED (5/5) before and after this follow-up._

### 8.1 The red-team HALT (defect d) is CLEARED — recovery-gated hit function shipped and passed its guard
The blocker on all of Phase S is resolved. `analysis/round20/HITFN/hitfn20.py` exposes one
predicate `is_hit(decode)` that returns True **only** when all three hold: (1) `pmax ≥
panelmax20.panelmax_bar` (exact preset, N=1e6 → **7.634**, never −5.5, never a k_eff); (2)
rune-**index** recovery ≥ 0.90 from the driftbeam decode path (never from score); (3) the same key
attributed on the first ¼ of the page reproduces recovery ≥ 0.90 on the held-out ¾. Real
candidates carry no plaintext oracle and are gated purely on the self-referential held-out
reproduction (clause 3); controls supply `truth_idx` for the strict test the guard is proven on.
Emits `SWEEPROW/3` (18 fields = 13 base + `[recovery, heldout_recovery, recovery_source,
clears_null, hit]`), `header_v3`, and `validate_row_v3` (refuses inconsistent `hit=True`).

**Hallucination guard, measured (`out_guard.json`):** a FAKE — real vowel-dropped English, correct
key, exact preset — genuinely **clears** the panel-max bar on pmax (9.29 ≥ 7.634, `clears_null=True`,
so this is a real hallucination test, not a null-failure) yet true rune-index recovery is only 0.438
and held-out self-consistency 0.833; `is_hit` **REJECTS** it in BOTH strict mode (clause 2, 0.438<0.90)
and real/no-oracle mode (clause 2, 0.833<0.90). A REAL genuine decode (correct key, English, exact:
pmax 26.41, recovery 1.000, held-out 1.000) is **ACCEPTED** in both modes. So score alone no longer
certifies a hallucinating decode. **Guard: PASS.** Tests 5/5 HITFN + 4/4 P3 green.

### 8.2 Lanes that ran — enumeration fraction, power per register, and whether `is_hit()` fired

| Lane | Family / scope | Fraction ENUMERATED | Power (correct-key pmax, P3a N=1e6 bar 7.634) | `is_hit()` fired? |
|---|---|---:|---|---|
| **S-G3** | Py2.7 `random.seed(str)` → `init_by_array([w])` random29, 2³² word space | **0.05723 %** (2,458,000 / 4,294,967,296); all 45,975 P3b prior words fully covered first | **1.00** on LP1_REAL / LATIN / OE / EN_HALFVOWEL / EN_MODERN / EN_KJV / DE / CY; **0.70** EN_NOVOWEL (detection-only, median recovery 0.84<0.90 → HITFN rejects); RAND 0.00; wrong-key 0.00 | **NO** — 0 hits |
| **S-RESCOPE** | B-04 survivor re-adjudication (no new key space) | **0 %** of any generator family; 583 decodes = 250 stored survivor keys × 2 relations (487) + 96 `payload_resolved.bin` re-seeds | poscontrol establishes **1.00** to detect a genuine B-04-family key (rank-1, pmax 29.87≫7.634, recovery 1.00, LP1_REAL) | **NO** — 0 hits |
| **S-MARS** | held Marsaglia physical units | **not run** — scaffolded only (`PREREG.md` + `smars_sweep.py`; `out/sweep.jsonl` and `out/run.log` are empty; only a poscontrol `control.json` exists). No sweep verdict produced. | — | — |

**`is_hit()` fired on NOTHING.** Across both lanes that ran, **0 genuine HITS** and — verified
independently from the raw `S-G3/sweep.jsonl` — **0 rows even cleared the null** (S-G3 max pmax
**6.271** < bar 7.634; S-RESCOPE max pmax 4.759 exact / 7.986 drift, both below their bars 7.634 /
13.842). `n_clears_null_total = 0` in S-RESCOPE across all 9 registers. Several survivors reached
recovery/held-out 1.0 but sit at pmax 5.9–6.3, all correctly `hit=false`: the gate discriminated
exactly as designed and the null was never spent.

### 8.3 What the negatives collapse (which family, what fraction, at what power) + reopening

- **S-G3 (Py2.7 32-bit string-seed).** Collapses **0.05723 % of the 2³² `init_by_array([w])`
  random29 word space** at correct-key power **1.00** on the four win-condition registers
  (LP1_REAL/Latin/OE/half-vowel English), 0.00 false-positive power. The **prior words are fully
  covered** (top prior seed 1325734783 + its neighborhood, 45,975 words, 0 above bar). This is the
  one family enumerable **without a sieve** (P1 INFEASIBLE, unused); it verified the foundational
  claim that on 32-bit Py2.7 `seed(str)` collapses bit-identically to `init_by_array([w])`.
  **Reopening condition:** the remaining **99.943 %** is a dense contiguous block from w=0 — a full
  2³² enumeration is **~7 core-days** at power 1.00; also untouched are the three other Py2.7
  reducers (grb5_mod / grb5_rej / shuffle29 — only random29 swept) and the 64-bit ABI 2-word map.
  The `/dev/urandom` branch is unrecoverable by construction. Not a re-run: prior Round-8 sweeps ran
  the Python-**3** seeding path (SHA-512 expansion, a different stream) under a rigid English-only
  scorer at an invalid bar = zero power.
- **S-RESCOPE (B-04 survivors).** Collapses the **fully recoverable slice** of the ~1,312 repo-wide
  English-argmax rows (583 decodes) at detection power **1.00** for a genuine B-04-family key; **no
  new key space** enumerated. Coverage HOLE stated as a bound: B-04's −6.412 Stage-A cutoff
  **structurally excluded** every true `skip_by_two` key (true key scores −6.718, 0.31 below), so
  S2's motivating case was **never stored** → fraction of the motivating case recoverable = **0**.
  The `payload_resolved.bin` re-seed (3 changed bytes idx 45/50/246, sha256 3b9b07d9…) also produced
  0 hits either way, so the C-canon 3-byte decision is not forced by this lane.

### 8.4 NEW red-team FOUND-ERROR (carried to Round 21, did not affect either negative)
S-RESCOPE's held-out proxy audit (`out_heldout_proxy_audit.json`) finds the HITFN **real-mode**
(no-oracle) clause-3 proxy catches only **15/45 (33 %)** EN_NOVOWEL hallucinations on the keyskip
relation, vs **100 %** in strict mode. This **re-opens defect (d) at the deployable operating point**:
a real bar-clearing survivor cannot be certified a solve on the real-mode proxy alone. It did **not**
affect either negative this round — nothing cleared the bar, so the leak was never exercised —
but before any future S-lane certifies a bar-clearing candidate on the no-oracle gate, clause 3 must
be strengthened (multiple disjoint held-out folds) and re-audited to ≥0.90 catch on the EN_NOVOWEL
population.

### 8.5 Standing verdict + top 3 live threads for Round 21 (updated)
**Standing verdict UNCHANGED:** LP2 0–54 is OTP-class — statistically indistinguishable from a
one-time pad under every tested class — with a soft anti-repeat rewrite on the ciphertext output.
Two lanes scored decodes through the repaired, recovery-gated instrument and produced **no HIT**;
this shrank the "cheap seeded 2012-Linux PRNG" hypothesis by a **thin, prior-dense slice** of exactly
one family (Py2.7 random29, 0.057 %) at power 1.00, and re-adjudicated the recoverable B-04 survivors
to 0 hits. No family is collapsed; none is touched beyond these fractions. The CSPRNG branch is
untouched and unrecoverable.

**Top 3 live threads for Round 21:**
1. **Strengthen the HITFN real-mode held-out proxy to ≥0.90 catch, THEN finish the S-G3 full-2³²
   enumeration (~7 core-days).** The gate now ships and rejects hallucinations in strict mode, but
   its no-oracle clause-3 proxy is leaky (33 % catch) — fix it (disjoint folds) before certifying any
   bar-clearing candidate, then run the remaining 99.943 % of the Py2.7 random29 word space, the one
   family enumerable without a sieve. Standing condition (b) still binds: do NOT re-enable the P1
   sieve without re-fitting the panel-max null on screened wrong keys (~2.5×10⁶ FP inflation).
2. **Sweep the other three Py2.7 reducers + the 64-bit ABI word map.** Only random29 was swept; grb5_mod
   / grb5_rej / shuffle29 and the i386-vs-amd64 2-word init map remain 0 % — same instrument, same
   power, cheap to add.
3. **Measure the `n_skips` power-crossover length (L between 400 and 12956)** — unchanged from §7,
   still the cheap self-contained unblock for the sieve-survival question P1 lost on.

---
_Trust anchor: `python3 tests/validate.py` → ALL VALIDATIONS PASSED (5/5), before and after Round 20
and after this Sweep follow-up. `validate_ledger.py` Unsound-negatives = 0. No git commit made
(coordinator commits)._
