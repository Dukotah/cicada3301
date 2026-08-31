# S-G3 — Python 2.7 `random.seed(<str>)` sweep — PREREG (before any sweep row scored)

_Pre-registered 2026-08-28. Lane S-G3 of the Round 20 follow-up armada._
_Binding: `ARMADA-DOCTRINE.md`. Depends on I1 (`round19/I1/driftbeam.py`), I2
(`round19/I2/adjudicate.py`), P3a panel-max bar (`round20/P3/panelmax20.py`), P3b seed prior
(`round20/P3/seedprior20.json`), the RECOVERY-GATED hit function (`round20/HITFN/hitfn20.py`)._

## 0. What this lane is, and why it is NOT a re-run (doctrine mechanic 6 / red-team (c))

The 2³² string-seed space of **Python 2.7** `random.seed(str)` collapses, on a 32-bit interpreter,
to `init_by_array([w])` for a single 32-bit word `w ∈ [0, 2³²)` (Modules/_randommodule.c
`random_seed`: `n = (unsigned long)hash(arg)` → `_chunks32(n)` = `[w]` on i386). **Verified**:
`keystream('CICADA3301', 'random29', wordsize=32)` is bit-identical to `init_by_array([hash32&0xFFFFFFFF])`.
So the whole string-seed space is **directly enumerable by the 32-bit word `w`, no dictionary**.

Prior sweeps of this family (Round 8 `seed_sweep/string_seeds.py`) ran the **Python-3** seeding
path (SHA-512 expansion, ≥18 key words) — a *different stream* — under a **rigid** decoder and an
**English-only** scorer at an **invalid bar**: coverage without power (doctrine L7-A/L7-B). All
600/600 Py2 streams differ from Py3 (G3 validation V6). This lane runs the **Py2 semantics** the
prior sweeps never touched, through the repaired instrument, gated on **recovery** (not score).
Genuinely not-a-re-run.

## 1. The five Aiming-Test questions

- **Q1 (recogniser / positive control — MANDATORY).** Plant a key from *this exact generator*
  (`init_by_array([w])`, `random29` reducer) over a real plaintext, encipher via `keyskip` (supp
  0.83), and recover it **rank-1** through the full pipeline (I1 keyskip1 → I2 panel → P3a bar →
  HITFN `is_hit`) with `is_hit()==True`. **Set before sweeping. If the plant is not recovered
  rank-1 with `is_hit`, the null is from an unvalidated instrument and is discarded.**
- **Q2 (prior).** P3b seed prior: 433 unix-second candidates, top **1325734783** (the second the
  3301 PGP key was created). The sweep is **seeded from this ordering** — the prior words first,
  then their ±neighborhoods — not flat (doctrine R4). Round 8's "all seconds equally likely" is the
  exact flat-prior error this corrects.
- **Q3 (bounded).** Word space is exactly 2³² = 4.29×10⁹, finite and enumerable **without a sieve**
  (P1 was INFEASIBLE; S-G3 is the one lane its frozen kill releases). Reducers: `random29`
  (= randrange/randint/choice in 2.7), plus `grb5_mod`, `grb5_rej`, `shuffle29` as declared modes.
- **Q4 (three conditionals).** Every negative is reported as (key space = Py2.7 word `w`) ×
  (decoder relation = keyskip1 baseline + drift_rec channel) × (register = I2 9-panel, power per
  register from P3a). No bare "swept".
- **Q5 (kill / time-box).** Real compute ≤ 40 min (S-G3 budget). 2³² full beam-decodes is ~205
  CPU-days; **40 min covers a small stated FRACTION**. Report the exact fraction of 2³² screened +
  extrapolated full-run cost. Do NOT claim the family collapsed — 0.90-power collapse needs full
  enumeration, which this time-box cannot buy.

## 2. The win condition (frozen, = CAMPAIGN-PLAN §2 via HITFN)

A **HIT** = a word `w` whose decode satisfies `hitfn20.is_hit`: **(1)** `pmax ≥ panelmax_bar(exact,
N, α=0.01)` (the P3a bar, 7.634 at N=1e6; NEVER −5.5, NEVER a k_eff) **AND (2)** rune-INDEX recovery
≥ 0.90 (from the decode path / held-out self-consistency, never score) **AND (3)** held-out-¾
reproduction ≥ 0.90 under the same key. Score alone is NOT a hit. A word clearing the bar on score
but < 0.90 recovery is logged as a **decoupling artefact**, not a hit (red-team (d) resolved).

## 3. Two-stage sweep (Stage A screen → Stage B recovery gate)

- **Stage A (cheap, every screened word).** keyskip1 beam (`exact` preset) on the first L=120 runes
  of the canonical unsolved ciphertext (`round11/lib_numchannel.unsolved()`), record `pmax`. Screen
  statistic = `pmax`. Words with `pmax ≥ SCREEN_BAR` promote to Stage B. `SCREEN_BAR = 5.0` (well
  below the 7.634 claim bar so no true positive is screened out — the plant clears at pmax≈28, wrong
  neighbors ≤4.2; margin is large). **Frozen before sweep.**
- **Stage B (full gate, survivors only).** For each Stage-A survivor: run L=240, adjudicate 9-panel,
  and evaluate `hitfn20.is_hit` in real-candidate mode (no truth oracle) → SWEEPROW/3 row with the
  recovery + held-out + hit fields. Also carry the `drift_rec` channel for transcription robustness.
- **Coverage accounting.** Words screened = (Stage-A throughput/core × cores × seconds). Report the
  exact count and count/2³² fraction. Seed order = P3b prior words first, then ±512 neighborhoods of
  the top prior seeds, then a contiguous block from `w=0` for a stated dense baseline.

## 4. Pass/fail thresholds (set now)

- **Positive control PASS** ⟺ plant recovered rank-1 with `is_hit()==True`. (Already measured in
  READY: pmax 28.27 vs wrong-max 4.18, rank 1/200, hit=True strict AND real-mode.)
- **HIT** ⟺ any swept `w` returns `is_hit()==True` AND is reproduced on the held-out ¾ (built into
  the predicate). Report `hit` per the schema.
- **NEGATIVE** (the expected outcome) ⟺ no swept word fires `is_hit`, reported WITH: coverage
  fraction of 2³², measured power per register (from P3a), and the three conditionals of §1 Q4.

## 5. Kill at ≤10% budget

If Stage-A throughput is so low that <10⁴ words can be screened in the time-box, stop and report the
throughput wall + extrapolated cost only (still a valid bound). Measured throughput ≈ 630 words/sec/core
(reduced beam) — the time-box screens ~10⁶–10⁷ words, well above the 10⁴ floor. No kill expected.

## 6. Doctrine compliance

Never a rigid decoder (uses driftbeam keyskip1 + drift_rec). Never a fixed −5.5 bar (uses P3a
panel-max). Score on rune INDICES. Emit SWEEPROW/3 (SWEEPROW/1 + recovery fields). Report coverage
FRACTION + power per register. Write files, no git commit. Keep `tests/validate.py` green.
