# HITFN — RESULTS: the recovery-gated hit function ships (red-team defect (d) RESOLVED)

_Run 2026-08-28. Trust anchor `tests/validate.py` PASSES before and after. No git commit._

## Verdict: PASS — the red-team HALT (defect (d)) is cleared

The FOUND-ERROR that blocked all of Phase S (SYNTHESIS §3 (d)) is resolved. Before this lane
`panelmax20.py` returned a **score bar only**, `SWEEPROW/1,2` carried **no recovery field**,
and **no hit-decision function existed** — so an S-lane could certify a hallucinating decode on
`pmax ≥ bar` alone. This lane ships the one predicate the win-condition demands, wires a
recovery field into the SWEEPROW emitter, and PROVES the gate rejects the hallucination the
defect names.

## What shipped (files in `analysis/round20/HITFN/`)

| file | what |
|---|---|
| `hitfn20.py` | `is_hit(decode)` predicate + `evaluate()` + `HitDecode` contract + `adjudicate_hit_row` (SWEEPROW/3 emitter with recovery) + `header_v3` + `validate_row_v3`. |
| `guard.py` | the mandatory hallucination guard — plants a fake + a real decode, proves reject/accept. |
| `test_hitfn.py` | 5 tests, all green (predicate, SWEEPROW/3 recovery field, validator, guard, held-out). |
| `out_guard.json` | measured guard numbers. |
| `PREREG.md` | pre-registered before measurement. |

## The predicate — all three clauses (CAMPAIGN-PLAN §2)

`is_hit(decode)` returns **true iff ALL THREE**, rejecting on the first failing clause:

1. **CLEARS THE NULL:** `pmax ≥ panelmax20.panelmax_bar(preset, N, α=0.01)` — the P3a
   calibrated panel-max bar (exact @ N=1e6 = **7.634**), never −5.5, never a per-register bar.
2. **RECOVERS:** rune-**INDEX** recovery ≥ **0.90**, from the **driftbeam decode path**, never
   from `score`.
3. **REPRODUCES HELD-OUT:** the same key, attributed on the **first 1/4** of the page (the
   quarter sub-decode's ending key pointer fixes the phase), reproduces recovery ≥ 0.90 on the
   **held-out 3/4** under that key.

### The crux of defect (d): recovery WITHOUT a plaintext oracle

`driftbeam.recovery()` needs ground-truth plaintext, uncomputable on a real LP2 candidate.
Clause (3) removes that dependency: re-decode the held-out 3/4 with the same key from the
attributed phase and measure self-consistency against the full-page decode's own indices. A
genuine key reproduces (the decode is a fixed function of key × ciphertext); a hallucinating
beam does not reproduce off the window it overfit. **Real candidates supply no `truth_idx`;
the held-out self-consistency IS the recovery number they are gated on.** When `truth_idx` is
supplied (controls only), clauses (2)+(3) are measured strictly against it — the test the
guard is proven on.

## The hallucination guard — PROVEN (the whole point)

Both plants use REAL plaintext, a REAL key, and the CALIBRATED exact-preset bar (7.634 @ 1e6).

| plant | pmax | clears bar | true recovery | held-out recovery | preg | `is_hit` strict | `is_hit` real-mode | required | got |
|---|---:|:---:|---:|---:|---|:---:|:---:|:---:|:---:|
| **FAKE** (vowel-dropped English, correct key, `exact`) | **9.29** | YES | **0.438** | **0.833** | EN_NOVOWEL | **False** | **False** | REJECT | REJECT ✓ |
| **REAL** (English, correct key, `exact`) | **26.41** | YES | **1.000** | **1.000** | LP1_REAL | **True** | **True** | ACCEPT | ACCEPT ✓ |

- The FAKE is the exact EN_NOVOWEL failure mode the defect names: score −7.50 / pmax 9.29
  **clears** the 7.634 bar, but the decode recovers only **43.8%** of rune indices. Score alone
  would certify it. `is_hit` **rejects** it on clause 2.
- Critically, in **real-candidate mode (no plaintext oracle)** the FAKE is still rejected —
  its held-out self-consistency recovery is **0.833 < 0.90**. So the gate rejects hallucination
  with no ground truth, which is the deployable property Phase S needs.
- The REAL genuine decode clears the bar, recovers 100%, reproduces 100% held-out, and is
  **accepted** in both modes — the gate is not so strict it kills the power I1/I2/P3 bought.

**GUARD PASS: rejects the fake AND accepts the real.**

## The recovery field is wired into the SWEEPROW emitter

`adjudicate_hit_row()` emits **SWEEPROW/3** = the full SWEEPROW/1 array (unchanged, append-only)
+ `[recovery, heldout_recovery, recovery_source, clears_null, hit]`. `header_v3()` carries the
`panelmax_contract` (bar + all three conditionals) and the recovery rule. `validate_row_v3()`
enforces recovery ∈ [0,1] and refuses an inconsistent `hit=True` (must have cleared the null and
reproduced held-out ≥ 0.90). Every downstream Phase-S row now carries recovery — no row is
score-only again.

## Ready for sweep

`ready_for_sweep = true`. S-G3 (the one lane P1's frozen kill releases) can now run un-sieved:
each candidate becomes a `HitDecode(C, K, o, preset, n_round_adjudicated)`, and `is_hit` gates
it on pmax-clearance AND recovery ≥ 0.90 AND held-out reproduction. A rank-1 candidate that
`is_hit` returns True on is a HIT by the round's own definition. **Standing condition b carries
forward unchanged:** do NOT re-enable the P1 sieve without re-fitting the panel-max null on
screened wrong keys (~2.5×10⁶ FP inflation otherwise) — this gate does not touch that.

## Key numbers

- panel-max bar (exact, N=1e6, α=0.01): **7.634**
- FAKE: pmax **9.29** (clears), true recovery **0.438**, held-out **0.833** → **REJECTED** (both modes)
- REAL: pmax **26.41** (clears), true recovery **1.000**, held-out **1.000** → **ACCEPTED** (both modes)
- recovery bar: **0.90**; held-out fit fraction: **0.25** (fit 1/4, verify 3/4)
- SWEEPROW/3: 18 fields (13 base + 5 gate); tests 5/5 green; `tests/validate.py` PASS.
