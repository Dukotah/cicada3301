# Round 24 — C2 — the `skip_by_two` decoder — RESULTS

**Verdict: CLEAN NULL, control-validated.** The single highest-leverage
un-audited closure in the campaign (L7-B) is now closed over the swept slice under
a decoder that *can* represent the skip_by_two transition. Modeling skip_by_two
does **not** change the bound: every beam-based negative survives over this axis for
the swept generator/slice.

_Pre-registered in [`PREREG.md`](PREREG.md), frozen before scoring the real
ciphertext. Trust anchor `tests/validate.py` = **5/5 PASS**._

---

## 1. The decision-relevant finding (read this first)

L7-B established that **every beam-based negative in this repository** (B-04,
R16-KDF, R16-PRNG, R17 P0–P3, R12-A1, R12-C1, F-01, the ~200-text keytext sweep)
covers only a rejection loop that advances the key by **exactly one** symbol per
rejection. If the real 2013 sampler burned **two** draws per rejection
(`skip_by_two`), those negatives would be **invalid over that axis**, because the
beam's transition relation cannot represent it (recovery 25.8 %, deep in the noise
band — RESULTS.md B, `round18/L7-redteam`).

C2 built the decoder that *does* represent skip_by_two (`driftbeam` mode
`keyskip2`, preset `pair`), proved it recovers a skip_by_two plant at **100 %**
where the beam gets **25.8 %**, and re-decoded the top-prior seed slice under it.

**Result: 0 hits over 245,975 words; max panel-max over the whole slice = 5.904,
which is 1.48 below the pair-decoder claim bar of 7.384; the seed-3301 wrong-key
null under the same decoder produced 0/4000 full-gate false positives (max null
pmax 5.08).**

Therefore, **on the swept slice, modeling skip_by_two reopens nothing.** The
beam-based negatives are **confirmed valid over the skip_by_two transition** for the
top-prior Python-2.7-MT generator slice. No corrected bound is needed for this
slice. (Scope: this closes the axis for the swept slice, not for every generator
at 2^32 — see §5 coverage.)

## 2. Positive control — VALIDATED (`control.py` → `control.json`)

Plant `enc_skip_by_two` (`j += 2` per rejection), L=240, `sha256_ctr` key,
held-out English, 7 seeds — the exact `round18/L7-redteam/b1_power_envelope.py`
protocol. Decoded with the beam (keyskip1, ms3 and ms8) vs the pair decoder
(keyskip2, ms8):

| supp | beam keyskip1 (ms3 = ms8) | **pair keyskip2** | ct-doublet |
|---|---|---|---|
| 0.40 | −5.897 / 59.6 % | **−4.285 / 100.0 %** | 2.09 % |
| 0.83 | **−6.903 / 25.8 %** | **−4.285 / 100.0 %** | 0.84 % |
| 1.00 | −6.857 / 24.6 % | **−4.285 / 100.0 %** | 0.00 % |

The beam at supp=0.83 reproduces L7-B's canonical **−6.90 / 25.8 %** to 3 s.f.,
confirming the control is measuring the exact hole L7-B named. The pair decoder
recovers **100 % at every suppression level** (min-over-seeds 100 %), score −4.285
(genuine-English band). Raising beam width / max_skip changes the beam by 0.000
(the failure is the transition relation, not search depth). **Control validated:
the new decoder models skip_by_two; the beam cannot.**

This is the number the PLAN asked for: **power = 100 % (pair) vs 25.8 % (beam,
L7-B).**

## 3. The sweep (`sweep.py` → `sweep.jsonl`)

One-for-one with `round20/S-G3/sweep.py` **except the driftbeam preset is `pair`
(keyskip2) instead of `exact` (keyskip1)** — the ONLY axis that differs from every
beam-based negative. Generator: Py2.7 `MT19937().init_by_array([w])`, reducer
`random29`. Ciphertext: canonical unsolved LP2 (`lib_numchannel.unsolved()`),
screen L=120, gate L=240, sign −1, o 0.

| quantity | value |
|---|---|
| words screened under the pair decoder | **245,975** |
| fraction of 2^32 | 5.73 × 10⁻⁵ |
| prior words (block 0) fully swept | 433 / 433 |
| prior + ±512 neighbourhood (block 1) fully swept | 45,975 (yes) |
| dense baseline (block 2) | 200,000 |
| screen survivors (pmax ≥ 5.0) | 18 |
| **HITS (three-clause hitfn20, pair claim bar 7.384)** | **0** |
| max panel-max over the whole slice | **5.904** |
| pair claim bar (panel-max, N=1e6, α=0.01) | 7.384 |
| elapsed | 562.8 s |

Every one of the 18 screen survivors fails the full gate: the best (w=143516)
reaches L=240 pmax 5.472 — still 1.9 below the claim bar. Several show recovery
1.000 / held-out 1.000 (self-consistent decodes) but do NOT clear the panel-max
null, so they are noise, not hits. w=30843 (rec 0.033) is a hallucinating decode
the held-out gate correctly rejects. The rank-1 prior seed (1325734783, the 3301
key-creation second) screens at pmax 1.072 — pure noise.

## 4. Red-team (R6, mandatory) — FP ceiling refutes any survivor (`redteam.py`)

Seed-3301 order-matched wrong-key null under the **same** pair decoder, on the
**same** ciphertext, 4,000 wrong Py2.7-MT words not in the prior:

| quantity | value |
|---|---|
| wrong keys tested | 4,000 |
| clearing the screen bar (5.0) | 1 (pmax 5.08) |
| **clearing the full three-clause gate** | **0** |
| null pmax: median / p99 / max | 1.656 / 3.622 / 5.08 |
| pair claim bar | 7.384 |
| wrong keys clearing the claim bar | 0 |

P(wrong key clears full gate) < 1/4000. Expected FP over the 245,975-word slice is
essentially **0** (the observed screen-clear rate 2.5 × 10⁻⁴ × the full-gate
conditional 0). The null's max pmax (5.08) is *below* the sweep's max screen pmax
(5.904) only because the sweep screened 60× more words; both sit ~2.3 below the
claim bar. **Refute-by-default holds trivially: there is no survivor to flag —
0 hits, and the FP ceiling would have swallowed any near-bar candidate anyway.**

## 5. Coverage × power (doctrine R2 — both reported)

- **Coverage:** 245,975 Py2.7-MT `init_by_array([w])` words (the full 433-word
  P3b prior + the ±512 neighbourhood of the top 64 + a 200k dense baseline),
  = **5.73 × 10⁻⁵ of 2^32**, re-decoded under the skip_by_two-exact pair decoder.
- **Power:** pair-decoder recovery on the skip_by_two relation = **100 %**
  (`control.json`), vs the beam's **25.8 %** (the L7-B number). The instrument that
  produced this null *can* see a skip_by_two plant; the beam that produced every
  historical negative could not.

## 6. What this does and does not close

- **Closes (for this slice):** the L7-B reopener over the top-prior Py2.7-MT
  generator. The beam-based negatives are valid over the skip_by_two transition
  here; no corrected bound is required.
- **Does NOT close:** skip_by_two under generators outside S-G3 (bash/perl/tex,
  sha256_ctr keytexts, the public-pad lanes), seeds outside this 246k slice, or
  offsets ≠ 0. The pair decoder now exists and is control-validated, so any of
  those is a cheap re-run of an existing script with `preset="pair"`. Also
  unaddressed: `free_drift` / `drift_at` (the continuous cousin of the same hole),
  which needs the `permissive` preset, not `pair`.

## 7. Reproduce

```bash
cd liber-primus
python3 tests/validate.py                                   # 5/5
python3 analysis/round24/C2-skip-by-two/control.py          # -> control.json (VALIDATED)
python3 analysis/round24/C2-skip-by-two/redteam.py --n 4000 # -> redteam.json (0 FP)
python3 analysis/round24/C2-skip-by-two/sweep.py --seconds 900 --dense 200000  # -> sweep.jsonl (0 hits)
python3 analysis/handoff/validate_ledger.py                 # Unsound=0
```
