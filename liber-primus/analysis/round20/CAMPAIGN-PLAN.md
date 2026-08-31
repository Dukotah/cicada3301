# Round 20 — "BUILD THE SIEVE, THEN SWEEP THE ENUMERABLE HAYSTACK AT MEASURED POWER"

_Opened 2026-08-28. Fifteen lanes in five phases. Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md)._
_Depends on Round 18 (the broken-magnet diagnosis) and Round 19 (the repaired instrument)._

---

## 0. The one-paragraph thesis

Round 18 proved the project had been searching with a **broken magnet**: an English-only
adjudicator with power 0.33 on Latin and 0.00 on vowel-dropped English, and a beam decoder
exact for exactly one enciphering relation. Round 19 **built the new magnet** — a drift-tolerant
decoder (I1), a nine-register adjudicator (I2), and recalibrated nulls (I3), all gated and
PASSING — and then its own red-team (R1) proved the round **could not affordably sweep anything**,
because the only prefilter cheap enough to make Phase 2 tractable is `round17`'s **rigid,
English-only** `dense_scan` — the exact two defects the new instrument exists to repair. So
Round 19 correctly *did not run the sweep*, and pivoted to a transcription audit that upheld canon
450/450. **Round 20 builds the one missing part — a skip-aware, multi-register prefilter (the
"sieve") — and only then runs the small, enumerable, evidence-prioritised generator spaces through
the fully-repaired instrument at measured power.** For the first time in the project's history, all
four preconditions for a meaningful sweep exist at once: a power-measured instrument, an
evidence-derived prior, target spaces small enough to *enumerate*, and — new this round — a sieve
that does not throw the true key away before the adjudicator ever sees it.

---

## 1. Where Round 19 left the board (the starting state, with receipts)

| asset | state | source |
|---|---|---|
| **I1 drift-tolerant decoder** | REPAIRED. `keyskip1` bit-identical to the repo beam (Δ≤1.07e-14); `drift_rec` preset **lam=12, max_free=2** recovers **20/20** L7-B failure cells (repo scores 0/20); the `skip_by_two` hole recovered at **−4.285 / 100 %**. Clean wrong-key FP at lam≥8; a **trap at lam≤6**. Cost: wrong-key null moves **+0.58**, decode **2.6–9× slower**. | `round19/I1/RESULTS.md` |
| **I2 nine-register adjudicator** | BUILT. Panel `{EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL}` + 4 language-agnostic stats `{ioc, mds, h2, zl}` behind one `adjudicate()` and one `SWEEPROW/1` schema. Power **≥0.90 in 27/27** cells (Latin 0.33→1.00, Welsh 0.00→1.00). **k_eff ≈ 6.3 / 9.5 / 8.0** at L=120/240/400, not 9. Calibrate on **beam decodes, not random runes**. `EN_NOVOWEL` recovery only 67–81 % → a hit there is **detection, not readable plaintext**. | `round19/I2/RESULTS.md` |
| **I3 nulls & thresholds** | CALIBRATED (`calib19.json`). Tail is **Weibull, ξ<0 → the Gumbel bar is conservative**. Repo-wide adjudicated tally corrected **17.06×10⁹ → 2.535×10⁹**. Two open items: **G-PANEL failed → calibrate a direct null on the panel maximum** (not a per-register bar); **drift-on-OE** fell just short (13.40 vs 13.84). Names the **`n_skips` null curve** as "the highest-value single addition." | `round19/I3/RESULTS.md` |
| **The sieve (prefilter)** | **DOES NOT EXIST.** Only affordable prefilter is `round17/lib_padsweep.dense_scan` = rigid + English-only. Measured true-key survival **0.60–0.83 by register, Welsh worst**; on real Marsaglia bytes vowel-dropped English survives **0.000**, half-vowel **0.067**, Welsh **0.300**. `round19/C2 §4.5` union-screen is a free start. | `round19/R1/RESULTS.md` §D-ii; `round19/C2` |
| **Generators G1–G4** | BUILT & byte-exact against real libraries, **all HELD at the scoring boundary, 0 coverage.** Ledger corrected: Perl/Python "never swept" was wrong — a slice ran, but rigid + English-only + invalid bar = **coverage without power**. | `round19/G1–G4/RESULTS.md` |
| **Transcription** | canon UPHELD **450/450**, indels **≤1** at 95 %, **E[W]=0**; but the **decode channel is fragile** (50 % of decodes derail at k=450 substitutions) and **`n_skips` is the robust channel** (98.4 % of margin retained). Three payload bytes (idx **45, 50, 246**) changed → `payload_resolved.bin`. | `round19/T1–T3/RESULTS.md`, `round19/C1` |
| **Seed prior** | L8 ranked **433 candidates**, top = **1325734783** (the second the 3301 primary key + subkey + UID self-sig were created). Round 8 treated all unix seconds as equally likely. | `round18/L8`, `round18/SYNTHESIS.md §6` |
| **Trust anchor** | `tests/validate.py` PASSES; `pytest -m "not network"` green; `validate_ledger.py` Unsound-negatives 0. | Round 19 close |

**Net:** the magnet is fixed and measured; the sieve that makes the magnet *affordable to use* is
the single missing part; the target spaces are built, byte-exact, and enumerable. Round 20 is
therefore the first round whose Phase-2 negatives can legitimately carry all three doctrine
conditionals (key space × decoder model × adjudicator register) — and whose Phase-2 *positive*, if
one exists in these families, would actually be recognised.

---

## 2. The win condition, stated before any measurement

A **HIT** = a decode whose `SWEEPROW/1` clears the **panel-max direct null** (per I3's G-PANEL fix,
not −5.5, not a per-register bar) **and** whose **rune-index recovery ≥ 0.90** (per R1's A-iv
score/recovery-decoupling hazard: score alone certifies a hallucinating decoder), **and** which
**reproduces on the held-out ¾ of the same page** under the same key. Anything clearing the null on
score but under 0.90 recovery is logged as a **decoupling artefact**, not a hit.

Two levels of success below the jackpot, both real and both publishable:
- **A measured negative at power ≥0.90 across the LP1_REAL / Latin / OE / half-vowel registers** over
  a *fully enumerated* generator space **collapses that generator family** as the LP2 key source —
  the first time the project can say that about *any* real-world 2012-Linux PRNG rather than about a
  0–3 % rigid-English slice. Four such collapses (bash, Perl, Py2, TeX) would retire the entire
  "cheap 2012 default PRNG" hypothesis class with receipts.
- **A named toolchain artefact** (Lane N1) — a text-layer or embedded font-subset in any surviving
  LP PDF — could name the typesetting program and rune face outright, promoting the TeX generator
  family from rank 5 to rank 1 and turning a 1.85×10¹¹ fog into a specific enumerable LCG.

---

## 3. Fair statement of what this round can and cannot do (the optimism clause, honestly)

**The optimistic, true part.** Three times the repo declared a lane "closed" and was wrong (the
derived-key dictionary, the public-pad branch, the entire register axis). The doctrine's own §0
finding is that *every* new result in this project came from auditing a closure or building an
instrument — **never from a flat-prior sweep** — and Round 20 is exactly that: it audits the
"we already swept the PRNGs" closure (they were swept at zero power) and builds the last instrument.
The generator spaces are not lore; they are an **evidence-derived prior** (Ubuntu 11.04–12.04, GnuPG
1.4.11, gs 9.04–9.14, a 6×9″ typeset PDF) pointing at a handful of families that a 2012 Linux C /
Perl / Python / bash / TeX program gets *for free*, and two of them (**bash `$RANDOM`**, **TeX
`\pgfmathrandom`**, period 2³¹−1) are **enumerable in minutes-to-hours**. If the LP2 pad was ever a
seeded call to one of those, this is the round that finds it.

**The disciplined, equally-true part.** The `/dev/urandom` branch is real: if the pad was drawn from
a CSPRNG or a genuine hardware source, **nothing in this round (or any round) recovers it**, and a
clean negative here does **not** touch that branch — it only shrinks the "cheap seeded PRNG"
hypothesis. The enumerable spaces are *prior-elevated, not proven*; a null is a real result but not a
closure (doctrine R7 — we write bounds, never "exhausted"). And the deepest constraint stands: LP2
0–54 is **OTP-class**, statistically indistinguishable from a one-time pad under every tested class,
with a soft anti-repeat rewrite acting on the ciphertext output. Round 20 is the strongest *fair* bet
left on the board — not a promise of a solve.

---

## 4. What Round 20 will NOT do (foreclosed — see `ELIMINATION-LEDGER.md:328–384`)

Per doctrine mechanic 6 ("do not re-run measured ground") and R7, none of the following appears as a
lane. Each is dead with a recorded reason; do not revive:

- **Published-keytext / running-key of any text** — foreclosed *by mechanism*, independent of text
  choice: rigid running keys are doublet-excluded (z≈−16.9) and skip-aware decoders are un-anchorable
  on it (`c[i]≠c[i-1]` false on all solved pages). (Round 7 external-input exhaustion.)
- **The number channel** (primes / gaps / digits / base-conversion / totient ladders) — Round 11,
  7 lenses, all control-validated NULL.
- **OSINT / AN-END page retrieval** — closed; AN-END is gated behind solving LP2 0–54, no independent
  address, unreachable-by-construction; preimage battery complete-negative across SHA-2/3, BLAKE-512,
  BLAKE2b, Skein, Whirlpool, Streebog. Passive monitoring only.
- **Attribution to a name** — provably impossible (359-word authentic corpus vs a ~500–1000-word
  floor; WoT-isolated self-expiring keys). Profile only, no falsifiable name.
- **Stego / image LSB / OutGuess re-runs**, **the red-rune colour channel** — both extracted and NULL.
- **Autokey / ciphertext-feedback** — *positively refuted* (difference-diagonal flat, cv=0.061).
  **One cheap reopener only** (Lane N2 below): A-03 haplography — ~20 confirmed doublet-site merges
  would reopen it.
- **Any ciphertext-only sweep under a flat prior, a rigid decoder, or an English-only scorer** — this
  is the entire mistake Rounds 18–20 exist to correct.

> Per doctrine mechanic 6, before any lane runs, query `LEDGER.json` and read each entry's
> `coverage` / `not_covered` — **not** its `status` string. Three lanes (B-04, PHP `mt_rand`, the KDF
> family) were each found *live inside a closure that read as "closed."*

---

## 5. Budget (doctrine §3)

| share | phase | lanes |
|---:|---|---|
| **≈30 %** | **P — instrument completion (the sieve)** | P1 prefilter · P2 `n_skips` null curve + language-agnostic screen · P3 panel-max null + seed-prior + drift re-baseline |
| **≈40 %** | **S — high-prior bounded sweeps** | S-G3 Python 2.7 · S-BASH `$RANDOM` · S-PERL · S-TEX · S-MARS held Marsaglia · S-RESCOPE re-adjudicate survivors |
| **≈20 %** | **R — red-team (doctrine R6, mandatory)** | R1 attack Round 20's own sieve + power claims |
| **≈10 %** | **N + C — new input & closeout** | N1 PDF/font-subset hunt · N2 haplography falsifier · C-prop L1-prior propagation · C-render page-15 · C-nav docs |

**Gate on the 40 %:** doctrine §3 forbids spending >40 % on new key space without a measured power
envelope covering that space's construction and register classes. That envelope is exactly what
Phase P delivers, and **no S-lane scores a single decode until P1, P2, and P3 all PASS** (the same
hard dependency Round 19 enforced, now extended to include the sieve).

```
  PHASE P  sieve+curve  P1 prefilter ─┐
                        P2 n_skips ───┼──ALL PASS──▶ PHASE S  sweeps (S-G3 first, cheapest)
                        P3 null/seed ─┘                         │
  PHASE R  red-team ──── runs concurrently, on the spec first ──┘
  PHASE N  new input ─── N1 concurrent (archival, no gate) ; N2 cheap, independent
  PHASE C  closeout ──── after S lands
```

---

## 6. The lanes

Every lane ships a `PREREG.md` answering the **five Aiming-Test questions (Q1–Q5)** *before* it runs,
with a positive control, a size-matched order-preserving surrogate null (seed 3301), a pass/fail
threshold set in advance, and a kill condition at ≤10 % of budget. Every sweep row is a
**`SWEEPROW/1`** record (`en` + `ioc, mds, h2, zl` + `n_skips, n_unexplained`) so no decode is ever
un-reinterpretable (doctrine R3). Score on **rune indices**, never the transliteration string.

---

### PHASE P — INSTRUMENT COMPLETION (≈30 %)

#### P1 — The skip-aware, multi-register prefilter (THE lane)
**This is the load-bearing piece of the entire round.** R1 named its absence "the finding" (D-ii).

- **Objective.** A cheap first-pass sieve that (a) is skip-aware (admits the `keyskip1` relation and
  the `drift_rec` band, not rigid alignment) and (b) is multi-register (survives Latin / OE / Welsh /
  half-vowel English, not English-only), retaining the true key at ≥0.90 per register so the
  expensive I1×I2 adjudication only runs on survivors.
- **Q1 (recogniser).** Plant a `skip_by_two`-generated key over each of the 9 registers; the sieve
  must pass the true key in ≥90 % of plants at each register *before* any real seed is screened. If it
  cannot, it is not a sieve, it is a second English filter.
- **Q2 (prior).** `round19/C2 §4.5`'s union-screen already survives real Marsaglia true-offsets where
  the English filter scores 0.000 — a measured foothold, not lore.
- **Q3 (bounded).** The sieve's own parameter space (screen statistic × threshold × window) is small
  and enumerable; tune it on planted keys, freeze it, then apply.
- **Q4 (three conditionals).** Report survival as a function of (key space, decoder relation,
  register) — a survival *surface*, not a scalar, so every downstream negative can name its register.
- **Q5 (kill).** If no parameterisation clears 0.90 survival on Welsh + half-vowel English at a
  screen-out fraction that actually makes S affordable (≥100× reduction), the sieve is declared
  infeasible and Phase S runs G3 only (the one space enumerable end-to-end without a sieve).
- **Instrument.** Build on `driftbeam.py` (I1) at reduced beam width as a screen; language-agnostic
  `n_skips` + `mds` + `ioc` as the survival statistics (they are register-blind by construction).
- **Deliverable.** `prefilter20.py` + a published per-register survival surface. This *is* the
  reopener condition R1 attached to D-i/D-ii.

#### P2 — The `n_skips` null curve + the language-agnostic screen
- **Objective.** Build the empirical (discrete) tail of `n_skips` (I3 called it "the highest-value
  single addition"). It is the **only ranking statistic that is both language-independent and
  transcription-robust** (T3: 98.4 % of its margin survives k=450 substitutions), so it is the
  backbone of both the sieve (P1) and any transcription-fragile decode.
- **Q1.** Plant keys at known skip counts; the curve must separate them from wrong-key skip
  histograms at the pre-registered FPR.
- **Q3.** Enumerable — the null is a fixed simulation at seed 3301, order-preserving.
- **Deliverable.** `nskips_null.json` + the screen wired into `SWEEPROW/1`.

#### P3 — Panel-max null, seed prior, drift re-baseline
- **P3a — panel-max direct null.** Resolve I3's **G-PANEL failure** by calibrating a single direct
  null on the **panel maximum** (adopts R1's B-i/B-ii recommendation; the two per-register estimators
  disagree 2.06–2.45×, so no single k_eff describes the panel). This fixes the bar every S-lane
  adjudicates against.
- **P3b — seed prior.** Integrate L8's **433 ranked seed candidates**, top = **1325734783**, as an
  ordering over each generator's seed axis so the sweeps are prior-weighted, not flat (doctrine R4).
  Round 8's "all unix seconds equally likely" is the exact flat-prior error this corrects.
- **P3c — drift re-baseline.** Re-measure T3's §5 decode-derail curve and I3's drift-on-OE shortfall
  under the repaired `drift_rec` beam (both were measured on the old `keyskip1` beam). Confirms the
  fragile-channel bound before we lean on the decode channel in Phase S.
- **Gate.** P1 ∧ P2 ∧ P3 must all PASS to release Phase S.

---

### PHASE S — HIGH-PRIOR BOUNDED SWEEPS (≈40 %)

All S-lanes run through I1 (`keyskip1` baseline + `drift_rec` channel) → **P1 sieve** → I2 panel →
P3a panel-max null, with P3b seed ordering. Each is a legitimate **not-a-re-run**: prior sweeps of
these families ran rigid, English-only, at an invalid bar, at 0–3 % coverage — **zero power** — which
is the closure this phase audits (doctrine §0 / optimism clause). Run in ascending cost so the
cheapest, most-enumerable space reports first.

#### S-G3 — Python 2.7 `random.seed(<string>)` — **run first, ~40 min, genuinely enumerable**
- On 32-bit Python 2.7 the entire string-seed space collapses to `init_by_array([w])` for
  w∈[0, 2³²) — **fully enumerable, no dictionary**. All 600/600 Py2 streams differ from Py3 (the
  silent-coverage hole is real and total; the prior sweeps tested Py3 semantics). Stage A ≈4.3×10⁵
  decodes. Positive control: plant a Py2-seeded key, recover rank-1 through the full pipeline.
- **This is the one space enumerable end-to-end even if P1 proves infeasible** — the round's floor.

#### S-BASH — bash `$RANDOM` / glibc `random()` — enumerable, ~28 min core-time
- Auto-seeded subset = **77.6M seeds (3.6 % of 2³¹), 28 min on 16 cores**; seed ≡ offset (one orbit).
  Era-correct targets `bash4.2` (both ABIs) + `glibc_random`. Open NC-1 (32-bit bash has no L1
  reference) noted as a coverage caveat, not a blocker.

#### S-PERL — Perl 5.14 `rand`/`srand` — enumerable 2³², sieve-gated
- Seed space is exactly **2³² with no residue** (even un-seeded `rand` reads 4 bytes of urandom →
  lands *in* the enumerable space, not the pad branch). Full Stage A = 3.09×10¹¹ decodes (~34 h in C
  at r29×8) → **requires P1** to be affordable; prior source for the prior is C3's signed, dated
  **Crypt::RSA** fact. If P1 is infeasible, run a stated-fraction sample and report the fraction
  (doctrine R2), never a bare "swept."

#### S-TEX — TeX/LaTeX internal LCGs — one-cycle scan ~18 h, sieve-gated
- `\pgfmathrandom` is a Lehmer LCG, **multiplier 69621** (not 16807 — a comment trap), period 2³¹−1,
  one cycle → offset ladder collapses; full space 1.85×10¹¹ but the **one-cycle scan is ~18 h**.
  **Conditional promotion:** if Lane N1 finds a font subset naming an `allrunes`-family face, this
  family jumps rank 5→1 and moves to the front of Phase S.

#### S-MARS — the held Marsaglia units
- **679 units / ~21 CPU-h**, release condition = P1∧P2∧P3 PASS, run under `SWEEPROW/1` (C2's staged
  hold). Real physical randomness (630 MB, hash-verified, 112 PASS/0 DRIFT) — the honest control that
  a sieve survival number means what we think it does.

#### S-RESCOPE — re-adjudicate the survivors (cheap, ~2 h, no new key space)
- R1 D-iii: B-04's Stage A stored everything above −6.412, but `skip_by_two`'s true key scores −6.718
  → 0.31 below the cutoff → **S2 as originally specced cannot recover its own motivating case.**
  Rescope to: **re-adjudicate the 1,312 English-argmax survivors** through I2/I3 + the panel-max null,
  and **re-seed the B-04 slice from `payload_resolved.bin`** (3 changed bytes: idx 45, 50, 246). A
  2-hour job that closes a real gap without opening new space.

---

### PHASE R — RED-TEAM (≈20 %, doctrine R6 — mandatory)

#### R1 — Attack Round 20's own sieve and sweep-power claims
- **Target: this round's own reasoning**, verdicts **FOUND-ERROR / NO-ERROR-FOUND**, pre-registered
  before P1 lands (as Round 19's R1 attacked the spec first).
- Mandatory sub-attacks: **(a)** does P1's sieve leak power on a *structured* wrong-key null (not
  uniform) — the reopener R1 attached to A-i? **(b)** does the sieve × panel-max null interact
  destructively the way free drift × panel did in Round 19 (B-iv)? **(c)** is the "not-a-re-run"
  justification for each S-lane actually true — i.e. does the prior sweep's `coverage`/`not_covered`
  in `LEDGER.json` genuinely leave this space unmeasured *at power*, or are we re-running measured
  ground? **(d)** the A-iv decoupling hazard: verify every S-lane gates on recovery, not score.
- **Kill/abort authority:** if R1 finds the sieve certifies hallucinating decodes, Phase S halts
  until P1 re-ships gated on recovery.

---

### PHASE N — GENUINELY NEW INPUT (part of the 10 %; N1 concurrent, no gate)

#### N1 — The PDF text-layer / embedded font-subset hunt (highest-value single item)
- **Objective.** Find any surviving Liber Primus PDF with a text layer or an embedded font subset.
  A subset `/BaseFont` name + subset tag would **name the typesetting program and the rune face
  outright** (R18 synthesis' top-value item) — the one thing that could turn S-TEX from a fog into a
  specific enumerable LCG and confirm/deny the whole toolchain prior.
- **Q2/Q5.** Prior: L1's byte-exact gs 9.04–9.14 + ImageMagick-q92 + 6×9″ inference. Kill at 10 %:
  if no PDF with an embedded object surfaces across the known mirrors (iBotPeaches, micheloosterhof,
  krisyotam, IA), log the archival bound and stop — **do not** drift into AN-END OSINT (foreclosed).
- Archival, so it runs concurrently with everything and blocks nothing.

#### N2 — The A-03 haplography falsifier (cheap, independent, the one autokey reopener)
- **Objective.** The *only* live reopener for the positively-refuted autokey class: check whether
  ~20 doublet-site merges (a scribe writing a doubled rune once) could hide the diagonal structure
  autokey needs. Low-compute, falsifiable, self-contained; a NEGATIVE hardens the refutation, a
  POSITIVE is the biggest single reopener in the ledger. Runs independent of the P-gate.

---

### PHASE C — CLOSEOUT (rest of the 10 %)

- **C-prop.** Propagate the L1-prior corrections none of Round 19's lanes had write-scope for: F6/F7
  counts (**56 files / 54 messages / running to 2017**, toolchain changed *twice* not once), the
  looser distro bracket (R1 C-ii + C3), and G2's prior re-sourced to the Crypt::RSA fact. Update
  `ELIMINATION-LEDGER.md`, `LEDGER.json` (`coverage`/`not_covered`, never bare `status`),
  `analysis/README.md`, `README.md`, and open `PICKUP-HERE.md` for Round 21.
- **C-render.** The cheapest open physical item: obtain **one independent render of page 15** to
  confirm the `3299` grey-level anomaly (+51.2 levels, z≈92) is in the *document* and not the encode.
- **C-canon.** Coordinator decision: whether to make the 3 changed payload bytes (45, 50, 246)
  canonical, since B-04 / R16-KDF / R17 are input-sensitive downstream of `payload_resolved.bin`.
- **C-eyeball.** Flag the one weak transcription candidate (T1 **p27:93, U→B, margin 5**) for a human.

---

## 7. Sequencing & exit

1. **P1 + P2 + P3 and R1 (spec attack) run first.** R1 attacks the sieve design before compute is
   spent; P-lanes build and self-gate. **No S-lane scores until P1∧P2∧P3 PASS.** N1 + N2 run
   concurrently (archival / cheap, ungated).
2. **On P-gate PASS, Phase S runs cheapest-first:** S-G3 (~40 min) → S-BASH (~28 min) → S-RESCOPE
   (~2 h) → S-MARS (~21 CPU-h) → S-PERL / S-TEX (sieve-gated, ~18–34 h, or stated-fraction samples).
3. **Exit is a bound, never a verdict** (doctrine R7). The round's `SYNTHESIS.md` will state, per
   generator family: the fraction of seed space *enumerated*, the measured power per register, and the
   concrete reopening condition — and will explicitly **not** write "exhausted / closed / unsolvable."
   The standing project verdict (LP2 0–54 is OTP-class, statistically indistinguishable from a
   one-time pad; soft anti-repeat rewrite on the ciphertext output) is unchanged by construction; what
   Round 20 can move is the size of the "cheap seeded 2012-Linux PRNG" hypothesis inside it.

## 8. Definition of done

- P1 sieve shipped with a published per-register survival surface (closes R1 D-i/D-ii's reopener).
- P2 `n_skips` null curve + P3 panel-max null in `SWEEPROW/1`; drift re-baseline confirms the fragile
  decode channel.
- At least S-G3 + S-BASH + S-RESCOPE fully run at measured power ≥0.90 across LP1_REAL/Latin/OE/
  half-vowel English, each with coverage fraction reported (doctrine R2).
- R1 red-team verdicts filed; any FOUND-ERROR either fixed or carried as an explicit conditional.
- N1 archival bound logged; N2 verdict filed; L1-prior corrections propagated; nav docs true.
- `tests/validate.py` PASSES before and after; `validate_ledger.py` Unsound-negatives = 0.
- `SYNTHESIS.md` written as bounds + reopening conditions; `PICKUP-HERE.md` opens Round 21.

---

## 9. Operational notes

- **Write files; do not `git commit`.** Lanes share one worktree; the coordinator commits at the end
  (doctrine mechanic 7). Single-branch, commit-to-master per `CLAUDE.md` (no `research/round-*`
  branches).
- **Never use a rigid decoder on LP2** (scores the correct key −6.835 vs the beam's −4.170); **never
  adjudicate against a fixed −5.5 bar** — use I3's `threshold_for()` / the panel-max null.
- **Push is blocked in WSL** (no GitHub creds; GCM lives on Windows). After the coordinator commits,
  the owner pushes with a plain `git push` from Windows/GCM.
