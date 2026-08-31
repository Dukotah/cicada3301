# Round 21 — "SEAL THE GATE, THEN SWEEP THE REDUCERS AND THE ONE OPEN glibc ROW"

_Opened 2026-08-28. Six lanes in the doctrine budget shape. Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md)._
_Depends on Round 19 (repaired instrument I1/I2/I3), Round 20 (panel-max bar, seed prior, `hitfn20`, sieve INFEASIBLE), and Round 20's Sweep follow-up (S-G3 ran 0.057 %, 0 hits; new FOUND-ERROR on the real-mode held-out proxy)._

---

## 0. The one-paragraph thesis

Round 20 built the recovery-gated hit function (`hitfn20.is_hit`) that finally lets a sweep be
adjudicated on *reproduction*, not score, and ran the first genuine power-1.00 sweep in the
project's history — S-G3, 0.057 % of the Py2.7 `random29` word space, **0 hits, max pmax 6.271 <
the 7.634 bar**. But its own Sweep follow-up (SYNTHESIS §8.4) found the one hole that matters:
`is_hit`'s **strict** (oracle) mode catches 45/45 EN_NOVOWEL hallucinations, but its **real** (no-oracle)
clause-3 held-out proxy — the only mode a real LP2 candidate can be judged in — catches only **15/45
(33 %)**. This re-opens red-team defect (d) *at the exact operating point a solve would be certified*.
So Round 21 does the disciplined thing first: **it seals the gate (strengthen the real-mode held-out
proxy to ≥0.90 catch with disjoint folds, re-audited), and only then spends compute** — on the
cheapest bounded ground the ledger still lists as 0 %-covered at power: the **three Py2.7 reducers
never swept** (`grb5_mod`/`grb5_rej`/`shuffle29` + the 64-bit ABI 2-word map — only `random29` ran),
and the **one full-32 glibc row that has been "still absent, still the one open row" since R19-G3-CORRECTION**
(`gen=0`, `random()%29`), whose sibling cells `gen=7`/`gen=8` were flagged as coinciding with Py2.7
reductions and were never re-adjudicated through I1+I2. This is not a new key-space fog; it is a short,
enumerable list of *named, byte-exact, prior-elevated cells the ledger itself says are un-measured at
power*, run through a gate whose real-mode leak this round closes first.

---

## 1. Where Round 20 left the board (starting state, with receipts)

| asset | state | source |
|---|---|---|
| **`hitfn20.is_hit`** | SHIPPED, strict-mode guard PASS (rejects a bar-clearing FAKE at recovery 0.438; accepts a genuine decode at 1.000). **Real-mode clause-3 proxy LEAKS: 15/45 (33 %) EN_NOVOWEL catch vs 100 % strict.** | `round20/HITFN/`, `SYNTHESIS §8.1/§8.4` |
| **P3a panel-max bar** | CALIBRATED M=1e6, claim-bar **7.634** (exact/keyskip1), correct-key power **1.00** / wrong-key 0.00 / RAND 0.00 on LP1_REAL/LATIN/OE/EN_HALFVOWEL. | `round20/P3/panelmax20.json` |
| **P3b seed prior** | 433 ranked candidates, rank-1 = **1325734783**, 0/433 round-trip mismatches. | `round20/P3/seedprior20.json` |
| **S-G3 (Py2.7 `random29`)** | RAN. **0.05723 %** of 2³² (2,458,000 words), **0 hits**, max pmax **6.271** < 7.634; 230 Stage-B survivors, several at recovery/held-out 1.0 but pmax 5.9–6.3 (correctly `hit=false`). | `round20/S-G3/out_sweep.json` |
| **Py2.7 other reducers** | `grb5_mod` / `grb5_rej` / `shuffle29` + 64-bit ABI 2-word map: **0 % swept**, byte-exact generator READY (`REDUCERS` dict in `gen_py27.py`). | `SYNTHESIS §8.5 thread 2`; `round19/G3/gen_py27.py:398` |
| **glibc `gen=0` full-32** | `random()%29` over full 0..2³²: **"still absent, still the one open row."** `gen=7`/`gen=8` (CPython seed(int)) coincide with G3 `random29`/`grb5_rej` and were **never re-adjudicated through I1+I2**. | `LEDGER.json:R19-G3-CORRECTION` not_covered/reopens_if |
| **P1 sieve** | **INFEASIBLE** at 0.90-at-100×; best simultaneous CY+half-vowel survival 0.667. Trilemma (cheap ∧ ≥0.90 ∧ multi-register — pick two). `survival_surface.json` published. | `round20/P1/RESULTS.md` |
| **Sieve × panel-max FP** | FOUND-ERROR (latent): screened-survivor FP 0.025/decode vs nominal 1e-8 → **2.5×10⁶ inflation**. Binds any screened sweep. | `SYNTHESIS §3(b)` |
| **`n_skips` null curve** | Full-book discriminator (recovery 0.999 at L=12956); **zero page-window (L≤400) power**. Crossover length L∈(400, 12956) **UNMEASURED** — named top-3 in R20 §7 and §8.5. | `round20/P2/nskips_null.json`, `SYNTHESIS §2 P2` |
| **Trust anchor** | `tests/validate.py` → ALL VALIDATIONS PASSED (5/5), before/after R20. `validate_ledger.py` Unsound-negatives = 0. | Round 20 close |

**Net:** the gate exists but its deployable (no-oracle) mode leaks; one family had a thin, prior-dense
slice swept at power 1.00 with 0 hits; and the ledger names a *specific, short, enumerable* set of
still-0 % cells — three Py2.7 reducers, the 64-bit map, and the single glibc `gen=0` row. Round 21 is
the first round that can sweep them through a *recovery-gated* instrument — after it stops that gate
from certifying a hallucination in the only mode a real candidate lives in.

---

## 2. The win condition, stated before any measurement (unchanged from R20, gate now hardened)

A **HIT** = a decode for which `hitfn20.is_hit` returns True: (1) `pmax ≥ panelmax_bar(preset, N)`
(exact/keyskip1 → 7.634 at N=1e6; **never −5.5, never a k_eff**), AND (2) rune-**index** recovery
≥ 0.90 from the driftbeam decode path (never from score), AND (3) the same key attributed on ¼ of
the page reproduces recovery ≥ 0.90 on the held-out ¾. **New this round:** clause (3)'s *real-mode*
(no-oracle) proxy must first be strengthened to ≥0.90 catch on the EN_NOVOWEL hallucination
population (L1) before any un-oracled bar-clearing survivor may be called a HIT — otherwise a real
survivor is certified on a proxy proven leaky at 33 %.

Two publishable levels below the jackpot:
- **A measured negative at power ≥0.90** across LP1_REAL/Latin/OE/half-vowel English over a named,
  enumerated cell (a reducer, the 64-bit map, or a stated fraction of `gen=0`) **collapses that cell
  at that fraction** — reported as coverage × power with its reopening condition, never as "swept."
- **A sealed real-mode gate** (L1): the first time the project can trust a no-oracle bar-clearing
  survivor as a solve rather than a possible hallucination — a permanent instrument gain independent
  of any sweep outcome.

---

## 3. Fair statement of what this round can and cannot do (optimism clause, honest)

**Optimistic, true.** Every genuinely-new result this project has produced came from auditing a
closure, instrument, artifact or input — never a flat-prior sweep (doctrine §0). Round 21 is exactly
that: it audits the **`hitfn20` real-mode proxy** (an instrument the project just built and already
knows leaks), and it audits the **"we swept Py2.7 / the full-32 rows" closure** the ledger's own
`not_covered` fields say is false at power for four named cells. These cells are *not* lore — they are
byte-exact against real 2.7.3/2.7.18/i386 libraries (`R19-G3` coverage: 2,165 hash + 8,660 stream
vectors) and prior-elevated by the 2012 Ubuntu/GnuPG toolchain fact. They are enumerable in
minutes-to-hours at stated fraction.

**Disciplined, equally true.** The `/dev/urandom` / CSPRNG branch is untouched and unrecoverable by
any round; a clean negative here only shrinks the "cheap seeded 2012-Linux PRNG" hypothesis, never
touches that branch. The reducer sweeps are **stated-fraction** (prior-dense first), not full
enumerations — a null is a real bound, not a closure (doctrine R7). The sieve stays INFEASIBLE, so
the sieve-gated families (Perl full-2³², TeX one-cycle, Marsaglia) remain deferred; this round either
formally carries them as stated-fraction samples or leaves them exactly where R20 did. And the
standing verdict is unchanged by construction: **LP2 0–54 is OTP-class**, indistinguishable from a
one-time pad under every tested class, with a soft anti-repeat rewrite on the ciphertext output.

---

## 4. What Round 21 will NOT do (foreclosed — see `ELIMINATION-LEDGER.md:328–384`, `PICKUP-HERE.md`)

Per doctrine mechanic 6 and R7, none of the following is a lane; each is dead with a recorded reason:

- **Published-keytext / running-key** — doublet-excluded by mechanism (z≈−16.9), skip-aware
  un-anchorable. (Round 7.)
- **The number channel** (primes/gaps/digits/base-conversion/totient) — Round 11, 7 lenses, NULL.
- **OSINT / AN-END retrieval** — unreachable by construction; preimage battery complete-negative.
- **Attribution to a name** — 359-word corpus < floor; provably impossible.
- **Stego / image-LSB / OutGuess / red-rune colour re-runs** — extracted and NULL.
- **Autokey / ciphertext-feedback** — positively refuted (diagonal cv=0.061); the one live reopener,
  A-03 haplography, was checked NEGATIVE by R20 N2 (super-physical adversary 6.1× below the band).
- **Any ciphertext-only sweep under a flat prior, a rigid decoder, or an English-only scorer** — the
  entire mistake Rounds 18–20 exist to correct.
- **Re-enabling the P1 sieve on any sweep without re-fitting the panel-max null on SCREENED wrong
  keys** — standing condition (b), 2.5×10⁶ FP inflation. Round 21 sweeps **unscreened** (as S-G3 did).
- **Re-running the S-G3 `random29` slice already covered** — the 0.057 % prior-dense block is done;
  Round 21 extends to the *other three reducers* and the glibc row, never re-scores `random29`.

> Before any lane runs, query `LEDGER.json` and read each entry's `coverage`/`not_covered` — **not**
> its `status`. Two entries this round is built on (`R19-G3-CORRECTION`, `R16-PRNG`) read "audit" /
> "negative" but their `not_covered` fields name live, un-measured-at-power cells.

---

## 5. Budget (doctrine §3)

| share | phase-role | lanes |
|---:|---|---|
| **≈30 %** | **instrument** | L1 seal the real-mode held-out proxy (≥0.90 catch, disjoint folds) · L2 measure the `n_skips` power-crossover length L∈(400,12956) |
| **≈40 %** | **high-prior bounded** | L3 sweep the 3 unswept Py2.7 reducers + 64-bit ABI map · L4 the open glibc `gen=0` full-32 row (stated fraction) + re-adjudicate the two coincident `gen=7`/`gen=8` cells through I1+I2 |
| **≈20 %** | **red-team (mandatory; ≥1 red-teams THIS round)** | L5 attack L1's strengthened proxy AND the "reducers are a not-a-re-run" justification |
| **≈10 %** | **new-input / closeout** | L6 sieve-survival reopening decision (accept deferral or lower-reduction reopen) + nav-doc closeout + `PICKUP-HERE` for R22 |

**Gate on the 40 %:** doctrine §3 forbids >40 % on new key space without a measured power envelope
covering its construction and register classes. That envelope already exists (P3a bar, I1+I2 panel,
`hitfn20`); **L1 seals its one known leak**, and **no L3/L4 survivor is certified a HIT until L1
PASSES** its ≥0.90 real-mode catch audit. The reducer/glibc cells are the same construction family
(MT19937 reducers / glibc `random()`) whose power envelope P3a measured at 1.00 — so this is a
power-covered sweep, not a fog.

```
  L1 seal proxy ─┐
                 ├── L1 PASS gates HIT-certification in ── L3 reducers ─┐
  L2 n_skips ────┘   (sweeps may RUN concurrently;         L4 glibc row ┴─▶ report coverage×power
                      only HIT-CALLING waits on L1)
  L5 red-team ─── attacks L1's proxy + L3/L4 not-a-re-run, on spec first, abort authority
  L6 closeout ─── after L3/L4 land
```

---

## 6. The lanes

Every lane ships a `PREREG.md` answering the five Aiming-Test questions (Q1–Q5) *before* it runs,
with a positive control, a size-matched seed-3301 order-preserving surrogate null, a pass/fail
threshold set in advance, and a kill condition at ≤10 % of budget. Every sweep row is a
**`SWEEPROW/3`** record (SWEEPROW/1 base + `recovery, heldout_recovery, recovery_source, clears_null,
hit`) so no decode is score-only or un-reinterpretable (doctrine R3). Score on **rune indices**.

---

### PHASE INSTRUMENT (≈30 %)

#### L1 — Seal the real-mode held-out proxy to ≥0.90 catch (THE lane)
**This is the load-bearing piece.** SYNTHESIS §8.4's FOUND-ERROR: `is_hit` real-mode clause-3 catches
only 15/45 (33 %) EN_NOVOWEL hallucinations; strict-mode catches 45/45. Until this closes, a real
bar-clearing survivor cannot be trusted a solve.
- **Objective.** Strengthen clause (3) so its **no-oracle** catch on the EN_NOVOWEL hallucination
  population reaches ≥0.90, then re-audit against the *same* 45-case population R20 used plus a fresh
  order-preserving surrogate set. Candidate mechanism (from §8.4): **multiple disjoint held-out
  folds** (attribute on fold-k, verify on the complement, over ≥3 disjoint partitions; require
  reproduction on *all* folds, not one ¼→¾ cut) — an overfit basin reproduces on the window it fit,
  not on disjoint ones.
- **Q1 (recogniser).** Plant the 45 EN_NOVOWEL hallucinations (correct key, vowel-dropped English,
  bar-clearing) that the strict guard rejects; the strengthened real-mode proxy must reject ≥0.90 of
  them *without an oracle*, while still ACCEPTING the genuine decode (recovery 1.0) at ≥0.90 —
  measure both catch and false-reject before trusting it.
- **Q2 (prior).** `out_heldout_proxy_audit.json` (S-RESCOPE) already localises the leak to the
  keyskip relation's ¼→¾ single-cut proxy — a measured foothold, not a redesign from zero.
- **Q3 (bounded).** The proxy's parameter space (fold count × fold assignment × agreement rule) is
  small and enumerable; tune on the planted 45, freeze, then audit on the held-out surrogate set.
- **Q4 (conditionals).** Report catch as a function of (relation {keyskip1, drift_rec}, register,
  fold-scheme) — a catch *surface*, so every downstream HIT-certification names its operating point.
- **Q5 (kill).** If no fold scheme reaches ≥0.90 catch without pushing genuine-decode false-reject
  above 0.10, declare the no-oracle gate **provably leaky** and rule that Round 21's sweeps report
  bar-clearing survivors as *flagged-for-oracle*, never auto-certified — and Phase high-prior still
  runs (it produces coverage×power bounds regardless; only auto-HIT-calling is withheld).
- **Instrument.** Extend `hitfn20._heldout_recovery` with a `k_folds` disjoint-fold variant; add a
  `real_mode_catch` audit harness. **Deliverable.** `hitfn21_folds.py` + `catch_surface.json` +
  updated `SWEEPROW/3` (unchanged fields; the proxy behind `recovery_source` improves).

#### L2 — Measure the `n_skips` power-crossover length L∈(400, 12956)
Named top-3 in both R20 §7 and §8.5; still unmeasured. P2 proved `n_skips` has zero page-window
(L≤400) power and 0.999 full-book (L=12956) power; **the crossover L is the one number a future
whole-page/whole-book adjudication needs.**
- **Objective.** Sweep L over a geometric ladder in (400, 12956) at seed 3301 (order-preserving),
  measuring planted-vs-wrong-key `n_skips` separation (two-sided p) per L; report the smallest L at
  which separation crosses the pre-registered FPR 0.01.
- **Q1.** The plant-recovery must reproduce the R20 endpoints (≈no separation at 400, clean at 12956)
  before the intermediate Ls are trusted.
- **Q3.** Enumerable — a fixed simulation over ~8–10 L values, seed 3301.
- **Q5.** If the endpoints do not reproduce, the null build is broken — stop and fix before reporting
  any crossover.
- **Deliverable.** `nskips_crossover.json` + the crossover L wired into `PICKUP-HERE` as the
  window-length gate any future concatenated-page adjudication must respect.

---

### PHASE HIGH-PRIOR BOUNDED (≈40 %)

All lanes run through I1 (`keyskip1` baseline + `drift_rec` channel) → I2 panel → P3a panel-max null,
prior-ordered by P3b, **unscreened** (no P1 sieve — standing condition b), emitting `SWEEPROW/3`.
Each is a legitimate not-a-re-run: the ledger's own `not_covered` names these exact cells un-measured
at power (L5 verifies this per cell).

#### L3 — The three unswept Py2.7 reducers + the 64-bit ABI 2-word map
- Only `random29` ran in S-G3. `grb5_mod` (`getrandbits(5) % 29`), `grb5_rej` (`getrandbits(5)`
  rejection), `shuffle29`, and the **i386-vs-amd64 2-word `init_by_array` map** are 0 % — same
  byte-exact generator (`REDUCERS` in `gen_py27.py`), same P3a power envelope, same prior order.
- **Scope (bounded/stated-fraction).** Mirror S-G3's budget: the 433 prior words + top-64 ±512
  neighbourhoods + a dense-from-0 baseline **per reducer**, time-boxed; report exact words screened,
  fraction of 2³², survivors, hits, and extrapolated full cost **per reducer** (doctrine R2).
- **Q1.** Plant a key from each reducer, recover rank-1 through the full `hitfn20` gate before
  screening real words (S-G3's `poscontrol.py` pattern, per reducer).
- **Q5.** If a reducer's positive control does not recover at rank-1 / pmax≥bar, that reducer's
  generator wiring is wrong — skip it and log the wiring gap, do not report its null.
- **Deliverable.** `reducers_sweep.jsonl` (SWEEPROW/3) + `out_reducers.json` per-reducer
  coverage×power table.

#### L4 — The open glibc `gen=0` full-32 row + re-adjudicate `gen=7`/`gen=8`
`R19-G3-CORRECTION` not_covered: `gen=0` (glibc `random()%29`) over full 2³² is "still absent, still
the one open row," and `gen=7`/`gen=8` (the two full-32 negatives coinciding with Py2.7 reductions)
were **never re-adjudicated through I1+I2** — they were scored by `sweep.c`'s *rigid English-4gram*
decoder at a fixed −12.5 bar = **zero power**.
- **Objective (bounded).** (a) Sweep a **stated fraction** of `gen=0` `random()%29` (prior-ordered by
  the 433 unix-second candidates + neighbourhoods, time-boxed) through I1+I2+`hitfn20`; report
  fraction and power. (b) Re-adjudicate the two archived `gen=7`/`gen=8` full-32 negatives through
  I1+I2 at the P3a bar — the exact re-adjudication `R19-G3-CORRECTION.reopens_if` names as "S2's job."
- **Q1.** Plant a glibc-`random()`-seeded key, recover through the gate; and plant one key at a
  `gen=7`/`gen=8` seed known to the archive, confirm the repaired instrument scores it where the
  rigid scorer could not.
- **Q5.** If the glibc generator's positive control does not recover, the `random()` port is wrong —
  fix or drop, do not report the null.
- **Deliverable.** `glibc_gen0.jsonl` + `readjudicate_gen78.json` closing that "one open row" to a
  measured stated-fraction bound (or a HIT).

---

### PHASE RED-TEAM (≈20 %, doctrine R6 — mandatory; L5 red-teams THIS round's own reasoning)

#### L5 — Attack L1's sealed proxy AND the "reducers/glibc are not-a-re-run" justification
- **Target: this round's own reasoning.** Verdicts **FOUND-ERROR / NO-ERROR-FOUND**, pre-registered
  before L1/L3/L4 land (as R19/R20 red-teams attacked the spec first). Abort authority.
- Mandatory sub-attacks:
  - **(a)** Does L1's disjoint-fold proxy *actually* reach ≥0.90 catch on a **held-out** hallucination
    population (not the 45 it was tuned on)? Generate a fresh order-preserving surrogate hallucination
    set and re-measure; if catch collapses on unseen cases, the seal is overfit → FOUND-ERROR, and HIT
    auto-certification stays withheld (L1 Q5 path).
  - **(b)** Is each L3/L4 cell genuinely un-measured *at power*? Read `LEDGER.json`
    `coverage`/`not_covered` for `R19-G3`, `R16-PRNG`, `R19-G3-CORRECTION`, `B-13-MARSAGLIA` per cell
    and confirm the prior sweep was rigid+English+invalid-bar (zero power) — or FOUND-ERROR if any
    cell was already covered at power (then drop it).
  - **(c)** Does the strengthened multi-fold proxy interact with the panel-max double-max the way the
    single-cut did? Re-check the screened-vs-unscreened FP; since L3/L4 sweep **unscreened**, confirm
    condition (b)'s 2.5×10⁶ inflation is not silently re-introduced by the fold machinery.
  - **(d)** Verify every L3/L4 row gates on **recovery/held-out**, never score (the original defect d).
- **Kill/abort authority:** if L5 finds L1's seal overfit or any cell already power-covered, that
  cell/certification is withdrawn before the negative is published.

---

### PHASE NEW-INPUT / CLOSEOUT (≈10 %)

#### L6 — Sieve-survival reopening decision + closeout
- **Sieve decision (new-input, from `survival_surface.json`).** P1 is INFEASIBLE at 0.90-at-100×.
  Using the *already-published* survival surface (no new compute), make and record the coordinator-
  facing decision R20 left open (PICKUP-HERE item 3): either (a) formally carry Perl/TeX/Marsaglia as
  **stated-fraction unscreened samples** at the S-G3 budget shape, or (b) name the exact lowered
  operating point (e.g. 30× reduction, or a 40-rune decrypt head) at which the surface shows ≥0.90 is
  reachable, as the concrete reopening condition. **Bounds, not a verdict.**
- **Closeout.** Propagate every Round 21 result to `LEDGER.json` (`coverage`/`not_covered`, never bare
  `status`), `ELIMINATION-LEDGER.md`, `analysis/README.md`, `README.md`; add the Round 21 nav row;
  resolve or re-flag the C-canon 3-byte governance item (idx 45/50/246 → `payload_resolved.bin`) and
  the T1 p27:93 U→B eyeball flag; open `PICKUP-HERE.md` for Round 22.

---

## 7. Sequencing & exit

1. **L1 + L2 (instrument) and L5 (spec attack) run first.** L5 attacks L1's fold design before L1's
   audit is trusted; L3/L4 sweeps *may run concurrently* (they produce coverage×power bounds
   regardless), but **no survivor is auto-certified a HIT until L1 PASSES** its ≥0.90 real-mode catch
   re-audit (and L5 confirms the seal is not overfit).
2. **L3/L4 run cheapest-first**, prior-dense block first, time-boxed to ≤20 min compute each; each
   reports fraction enumerated, power per register, and reopening condition.
3. **Exit is a bound, never a verdict** (doctrine R7). `SYNTHESIS.md` will state, per cell (each
   reducer, the 64-bit map, `gen=0`, `gen=7`/`gen=8`): fraction enumerated, measured power per
   register, and the concrete reopening condition — and will **not** write "exhausted/closed/
   unsolvable." The standing OTP-class verdict is unchanged by construction; what Round 21 can move is
   the size of the "cheap seeded 2012-Linux PRNG" hypothesis and the **trustworthiness of the
   no-oracle hit gate**.

## 8. Definition of done

- **L1** ships `hitfn21_folds.py` + `catch_surface.json`; real-mode EN_NOVOWEL catch measured
  (PASS ≥0.90 with genuine-decode false-reject <0.10, or the explicit flagged-for-oracle ruling).
- **L2** ships `nskips_crossover.json`; the crossover L reported with the R20 endpoints reproduced.
- **L3** sweeps the three reducers + 64-bit map at a stated fraction, per-reducer coverage×power in
  `out_reducers.json`; **L4** closes the "one open glibc row" to a measured stated-fraction bound and
  re-adjudicates `gen=7`/`gen=8` through I1+I2 (or a HIT).
- **L5** red-team verdicts filed; any FOUND-ERROR fixed or carried as an explicit conditional; the
  seal-overfit and not-a-re-run checks reported per cell.
- **L6** sieve reopening decision recorded from the published surface; nav docs true; `PICKUP-HERE`
  opens Round 22.
- `tests/validate.py` PASSES before and after; `validate_ledger.py` Unsound-negatives = 0.
- `SYNTHESIS.md` written as bounds + reopening conditions.

---

## 9. Operational notes

- **Write files; do not `git commit`.** Lanes share one worktree; the coordinator commits (doctrine
  mechanic 7). Single-branch, commit-to-master per `CLAUDE.md`.
- **Never a rigid decoder on LP2** (scores the correct key −6.835 vs the beam's −4.170); **never a
  fixed −5.5 bar** — use P3a `panelmax20.panelmax_bar` (7.634 at N=1e6) / I3 `threshold_for()`.
- **A HIT requires ALL THREE** via `hitfn20.is_hit` (clears panel-max null AND rune-index recovery
  ≥0.90 AND held-out ¾ reproduction) — and this round, its **real-mode proxy sealed by L1** before any
  no-oracle survivor is certified.
- **Time-box each compute lane to ≤20 min**; if the space is bigger, run a stated fraction and report
  it + extrapolated full cost.
