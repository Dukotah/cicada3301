# ROUND 21 / L3 — RESULTS
### Python 2.7 `random.seed(<str>)` reducers (grb5_mod / grb5_rej / shuffle29) + the amd64 2-word `init_by_array` map

_Lane L3 of `analysis/round21/CAMPAIGN-PLAN.md`. Pre-registration: `PREREG.md`, written and
frozen before any keystream was scored. Binding: `liber-primus/ARMADA-DOCTRINE.md`._

> **What this lane delivers.** The S-G3 sweep that Round 20's SYNTHESIS §8.5 thread 2 left open:
> the **three Py2.7 rune reducers S-G3 never covered** (`grb5_mod`, `grb5_rej`, `shuffle29`) plus
> the **amd64 (2-word) `init_by_array` map** for `random29`, each run through the exact S-G3
> two-stage instrument (I1 keyskip1 → I2 9-register panel → P3a panel-max null → HITFN recovery
> gate). **Result: 884,000 words screened across the 4 configs, 0 hits, 0 survivors even clearing
> the panel-max claim bar.** A clean negative at a stated coverage, consistent with the standing
> OTP-class verdict. The sweep was previously started and killed mid-run (`reducers_sweep.jsonl`
> was 0 bytes); this run finished it.

---

## 1. Headline

**Four era-idiomatic Py2.7 reducer/ABI configurations, swept prior-dense-first, produced zero
hits and zero bar-clearing survivors.** The best decode over all 884,000 words reached
`pmax = 6.248` (shuffle29, word 27069, LP1_REAL register) — **1.39 units below** the 7.6342
panel-max claim bar and nowhere near a solve. Every one of the four positive controls recovers
its planted key at **recovery 1.000, rank 1, pmax 28.268 >> bar**, so this is a measured negative
from a validated instrument, not a null from an unproven one.

| config | reducer | map | words screened | fraction of 2³² | survivors (Stage B) | **hits** | max pmax | full-2³² extrapolation |
|---|---|---|---:|---:|---:|---:|---:|---:|
| grb5_mod_i386 | `getrandbits(5) % 29` | i386 1-word | 288,000 | 0.006706 % | 21 | **0** | 6.089 | 10.9 core-days |
| grb5_rej_i386 | `getrandbits(5)` reject 29–31 | i386 1-word | 216,000 | 0.005029 % | 25 | **0** | 5.260 | 14.3 core-days |
| shuffle29_i386 | repeated `shuffle(range(29))` | i386 1-word | 186,000 | 0.004331 % | 24 | **0** | 6.248 | 18.4 core-days |
| random29_amd64 | `int(random()*29)` | **amd64 2-word** | 194,000 | 0.004517 % | 25 | **0** | 5.341 | 18.0 core-days |
| **TOTAL** | | | **884,000** | — | **95** | **0** | **6.248** | — |

In each config the **entire 45,975-word prior-dense front** (433 P3b top seeds + the top-64
seeds' ±512 neighbourhoods) was screened *first and in full* (`prior_words_all_screened: true`)
before any dense-from-0 baseline words — so the highest-prior region of every config is completely
covered, and the uncovered remainder is the flat-prior tail of 2³².

---

## 2. Trust anchor and positive control (gate the whole lane)

**Trust anchor.** `python3 liber-primus/tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5),
run before this sweep. Without it no negative in this repo means anything.

**Positive control** (`poscontrol.py` → `out_poscontrol.json`, re-run fresh this session,
exit 0). Per (reducer, map) config, plant P3b top word `1325734783` as `w` (amd64 config given a
nonzero high word so the 2-word path is genuinely exercised), encipher `EN_MODERN[2000:2240]` via
keyskip (supp 0.83), recover through the full pipeline including `hitfn20.is_hit`:

| config | strict hit | pmax | recovery | held-out | rank (±500 neigh) | wrong-max pmax | PASS |
|---|---|---:|---:|---:|---:|---:|---|
| grb5_mod_i386 | True | 28.268 | 1.000 | 1.000 | 1 / 99 wrong | 3.693 | **PASS** |
| grb5_rej_i386 | True | 28.268 | 1.000 | 1.000 | 1 / 99 wrong | 3.792 | **PASS** |
| shuffle29_i386 | True | 28.268 | 1.000 | 1.000 | 1 / 99 wrong | 4.059 | **PASS** |
| random29_amd64 | True | 28.268 | 1.000 | 1.000 | 1 / 99 wrong | 3.239 | **PASS** |

`PASS_all: true`, `wiring_gaps: []`. Every config's instrument recognises its own planted hit at
**recovery 1.000** (PREREG gate is recovery ≥ 0.90, **not** score — R's A-iv decoupling hazard),
rank 1, at pmax ~20 units above the bar, with the nearest wrong word in a ±500 neighbourhood
peaking at pmax ≤ 4.06. **Q5 kill condition did not fire for any config**, so all four nulls are
reported as bounds.

---

## 3. Instrument (reused byte-exact from S-G3)

`round19/G3/gen_py27.py` REDUCERS → I1 `round19/I1/driftbeam.beam_decode` keyskip1 (exact preset:
`drift_rec` lam=12 max_free=2) → I2 `round19/I2/adjudicate` 9-register panel → P3a panel-max bar
(`round20/HITFN/panelmax20`, `exact`/N=1e6/α=0.01) → `round20/HITFN/hitfn20.is_hit`. Two stages:

- **Stage A** (every screened word): keyskip1 beam bw64 on the first L=120 runes of the canonical
  unsolved ciphertext → `pmax`. Promote at `pmax ≥ SCREEN_BAR = 5.0` (<< the 7.6342 claim bar).
- **Stage B** (survivors only): full L=240 `HitDecode` → `is_hit` → `SWEEPROW/3` row.

**HIT iff all three** (`hitfn20.is_hit`): `pmax ≥ 7.6342` **AND** rune-index recovery ≥ 0.90 (from
the decode path, never from score) **AND** held-out 3/4 self-consistency ≥ 0.90. Score alone is
never a hit. Panel-max bar confirmed this session at **7.6341931878728095**, unchanged from R19/R20.

Seed order (P3b prior-weighted, doctrine R4): 45,975 prior-dense words (433 P3b seeds +
top-64 ±512 neighbourhoods) → dense-from-0 baseline. Time-boxed at ~240 s/config real compute
(5 procs); actual per-config wall 310–351 s including worker cold-start.

`SWEEPROW/3` rows persist the language-agnostic statistics at sweep time (doctrine R3): per
survivor `pmax`, `bar`, decode-path `recovery`, held-out `heldout`, argmax register `preg`, beam
`score`, `clears`. Header + 95 survivor rows in `reducers_sweep.jsonl`; full aggregate in
`out_reducers.json`.

---

## 4. The negative in detail — no survivor clears the bar, no clause-2/3 coincidence hides a hit

Of the 95 Stage-B survivors, **none clears the panel-max bar** (`clears = false` on all 95). The
top survivor per config, by pmax:

| config | word | pmax | recovery | held-out | register | clears bar |
|---|---:|---:|---:|---:|---|---|
| grb5_mod_i386 | 55754 | 6.089 | 1.000 | 1.000 | LP1_REAL | **no** |
| grb5_rej_i386 | 136983 | 5.260 | 0.872 | 0.872 | EN_KJV | **no** |
| shuffle29_i386 | 27069 | 6.248 | 1.000 | 1.000 | LP1_REAL | **no** |
| random29_amd64 | 1438060426 | 5.341 | 1.000 | 1.000 | LP1_REAL | **no** |

**A caution read correctly.** 71 of the 95 survivors carry `recovery = 1.000` and `heldout =
1.000`. This is *not* a suppressed hit — it is the expected behaviour of the self-consistency
recovery proxy: the beam trivially "recovers" its own decode when the key is wrong, which is
exactly why `hitfn20` gates on **pmax clearing the null**, not on recovery in isolation (the
hitfn20 docstring calls this out — EN_NOVOWEL clears the bar at recovery 0.84/0.26 on hallucinated
decodes). Verified directly: **rows meeting all three hit clauses simultaneously = 0**; **rows with
`pmax ≥ 7.6342` (which would be flagged-for-oracle per L1) = 0.** Nothing is even a candidate for
the L1 flagged-for-oracle channel.

**Consistency with L1.** Round 21 L1 established that the no-oracle held-out proxy is provably
leaky (single-cut 0.33 catch, fold strengthening 0.80–0.87 < 0.90 seal), so any bar-clearing
real-mode survivor must be reported *flagged-for-oracle*, never auto-certified. This lane has **no
bar-clearing survivor at all**, so the leak is moot here: there is nothing to flag.

---

## 5. Coverage × power (doctrine R2 — reported together)

**Power.** Positive-control measured recovery = **1.000 strict, rank 1** on the LP1_REAL / EN
register at the planted supp, for **all four** configs, at pmax ~20 units above the claim bar. So
power ≈ 1.0 on the win-condition registers (LP1_REAL / LATIN / OE / EN_MODERN / EN_KJV / DE / CY).
This inherits S-G3's measured envelope: correct-key power 1.00 on those registers, 0.70 on
EN_NOVOWEL (detection-only, median recovery 0.84 < 0.90 → HITFN rejects), RAND 0.00, wrong-key 0.00.

**Coverage.** Per config, fraction of the 2³² word space screened (all 45,975 prior-dense words
fully covered first in every config):

| config | words | fraction of 2³² |
|---|---:|---:|
| grb5_mod_i386 | 288,000 | 6.706 × 10⁻⁵ (0.006706 %) |
| grb5_rej_i386 | 216,000 | 5.029 × 10⁻⁵ (0.005029 %) |
| shuffle29_i386 | 186,000 | 4.331 × 10⁻⁵ (0.004331 %) |
| random29_amd64 | 194,000 | 4.517 × 10⁻⁵ (0.004517 %) |

**Value = coverage × power** = (~5 × 10⁻⁵ of 2³² per config, prior-dense front fully covered) ×
(~1.0 on the win-condition registers) = **a high-power exclusion of a low-coverage, high-prior
slice of each reducer's word space.** It excludes the 45,975 highest-prior words per config and a
dense baseline tail, at power ~1.0; it does **not** exclude the flat-prior remainder of 2³² (that
is the extrapolation below). Reported together per doctrine R2 — neither number stands alone.

**Extrapolated full-2³² cost** (from measured words/sec × 5 procs): grb5_mod 10.9 core-days,
grb5_rej 14.3, shuffle29 18.4, random29_amd64 18.0 — i.e. a full enumeration of all four reducers'
2³² i386/amd64 word spaces is ~61 core-days total on this box. Tractable but not run here; the
prior-dense front carried the value.

---

## 6. The three conditionals this negative carries (doctrine Q4)

1. **Key space** — the swept fraction (§5) of the Py2.7 `init_by_array` 32-bit word space per
   reducer, **prior-dense first** (45,975 words fully covered per config) then dense-from-0. **Not**
   the full 2³²; **not** the amd64 seeds outside the folded word image; **not** other point
   releases, `PYTHONHASHSEED`-randomised runs, WichmannHill, or Python 2.6/2.5.
2. **Decoder transition model** — I1 keyskip1 + `drift_rec(lam=12, max_free=2)`: one skip/drift
   family. A different rejection-loop (e.g. `skip_by_two`, L7-B) or a non-keyskip enciphering is
   **not** represented.
3. **Adjudicator register** — I2's 9-register panel (LP1_REAL + Latin / OE / German / Welsh / EN
   variants). A plaintext outside the panel is invisible (L7-A conditional).

---

## 7. Coverage — measured vs NOT covered, with the reopen condition for each

**Measured (this lane).**
- 884,000 words screened across 4 (reducer, map) configs through the full S-G3 two-stage
  instrument; 95 Stage-B survivors persisted with all doctrine-R3 statistics.
- All 45,975 prior-dense words fully screened in every config (`prior_words_all_screened: true`).
- 0 hits, 0 bar-clearing survivors; best pmax 6.248 (shuffle29) vs bar 7.634.
- 4/4 positive controls PASS strict (recovery 1.000, rank 1, pmax 28.268), fresh this session.
- Full-2³² extrapolated cost per config from measured throughput.

**Not covered, and what reopens each.**

| # | not covered | reopens if |
|---|---|---|
| **NC-1** | The **flat-prior tail of 2³²** for each of the 4 configs (>99.99 % of each word space). | someone spends the ~10.9–18.4 core-days/config full enumeration; throughput is measured (§5). |
| **NC-2** | The **amd64 2-word map beyond the folded `w`→(lo,hi) image**. This lane folds one 32-bit `w` deterministically into a 64-bit long (`w·φ⁻¹ mod 2⁶⁴`) to exercise the 2-word path; the full 2⁶⁴ hash image is a superset not enumerated. | the amd64 seed dictionary is extended or the 2⁶⁴ image is sampled/enumerated. |
| **NC-3** | **random29 / i386 1-word** — already swept by S-G3 (round20, 2,458,000 words, 0.05723 %, 0 hits); this lane deliberately did **not** re-run it. | subsumed by NC-1's full-2³² enumeration of the i386 branch. |
| **NC-4** | **Decoder relations other than keyskip1** (skip_by_two / keyskip2 / non-keyskip). | an L7-B-style relation lane plants and measures along the relation axis. |
| **NC-5** | **Registers outside the I2 9-panel**, and **EN_NOVOWEL** (detection-only, power 0.70 < gate). | the panel is extended or a per-register bar is calibrated. |
| **NC-6** | **`PYTHONHASHSEED`/-R randomised hash, WichmannHill, float/jumpahead seeds, Python 2.6/2.5** (S-G3 NC-5..NC-10). | those seed families are added to REDUCERS and validated against a real interpreter. |
| **NC-7** | The **`/dev/urandom` / unseeded** branch — no seed, no key. | nothing in any PRNG sweep touches this; it is the doctrine §5 branch no compute reaches. |

**Reopen condition for the lane as a whole.** The four reducer/ABI configs are **bounded, not
closed.** Each reopens the moment its full-2³² enumeration is run (NC-1), a new decoder relation
(NC-4) or register (NC-5) is added, or the amd64 2⁶⁴ image (NC-2) is enumerated. Doctrine R7: this
is a bound, not a verdict.

---

## 8. Reproduce

```bash
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus
python3 tests/validate.py                                   # trust anchor, 5/5

cd analysis/round21/L3-py27-reducers-plus-64bit-map
python3 poscontrol.py                                       # 4/4 PASS, exit 0, writes out_poscontrol.json
python3 sweep.py --seconds-per-config 240 --procs 5         # writes reducers_sweep.jsonl + out_reducers.json
```

**Trust anchor.** `python3 liber-primus/tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5), run
before this lane. Positive control `out_poscontrol.json`: `PASS_all: true`, 4/4 configs recover at
recovery 1.000. Sweep `out_reducers.json`: `total_words_screened: 884000`, `total_hits: 0`,
`any_hit: false`.
