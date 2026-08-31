# Round 25 — COMPUTE-TAIL — chunk 1 — RESULTS

**Verdict: CLEAN NULL, control-validated. Chunk 1 of a resumable campaign.**
Zero hits, zero survivors flagged-for-oracle. The Py2.7-MT `init_by_array([w])`
2³² seed tail remains **>99.98% unswept**.

_Trust anchor `tests/validate.py` = **5/5 PASS** (confirmed before scoring).
No git commit (WSL; owner commits from Windows)._

---

## 1. What this lane is

The owner elected to grind the **PRNG/seed tail** — the one branch
[`PICKUP-HERE.md`](../../../PICKUP-HERE.md) lists as still runnable and still
untouched, with an honestly **low prior**. This is a compute lane, not an
instrument audit: it applies the *already control-validated* pipeline
(`round24/C2-skip-by-two` + `round20/HITFN`) to a fresh contiguous slice of the
tail and checkpoints so the campaign can be resumed chunk-by-chunk.

Pipeline (identical to R24-C2, unchanged):
- **Generator:** Python-2.7 `MT19937().init_by_array([w])`, reducer `random29`
  (`round19/G3/gen_py27.py`).
- **Decoder:** `driftbeam` preset **`pair`** (mode `keyskip2`) — the
  `skip_by_two`-exact relation the beam cannot represent (control-validated 100%
  recovery vs the beam's 25.8% in C2).
- **Hit gate:** `hitfn20` three-clause — `pmax ≥ panel-max null bar` **AND**
  rune-index recovery `≥ 0.90` **AND** held-out-3/4 recovery `≥ 0.90`. Score
  alone is never a hit.
- **Ciphertext:** canonical unsolved LP2 (`lib_numchannel.unsolved()`, pages
  0–54), screen `C[:120]`, gate `C[:240]`, sign −1, o 0.

## 2. Red-team sanity — the pipeline recovers a plant at recovery 1.000

Embedded self-test, run FIRST each invocation. Encipher held-out English under
the `skip_by_two` relation with seed 777's `random29` keystream, decode with the
**same** seed via `hitfn20`'s strict `truth_idx` path:

| seed | recovery | held-out | pmax | bar | hit |
|---|---|---|---|---|---|
| 777 | **1.000** | 1.000 | 25.239 | 7.384 | **True** |

The instrument recovers its own plant through the full gate. **A null this chunk
is therefore a true negative, not a broken scan** — this is the same
control-validated pipeline from C2/S-G3.

## 3. The chunk

| quantity | value |
|---|---|
| seed range swept | **[3,000,000 → 3,506,593)** |
| seeds screened this chunk | **506,593** |
| seeds skipped (already-swept exclusion) | 0 (tail starts past all excluded regions) |
| **HITS (three-clause `hitfn20`, pair bar 7.384)** | **0** |
| survivors flagged-for-oracle | **0** |
| best panel-max over the chunk | **5.863** (`w=3,311,419`) |
| pair claim bar (panel-max, N=1e6, α=0.01) | 7.384 |
| margin of best below bar | **1.521** |
| wall-clock | **1,320 s (22.0 min)** |
| throughput (single core) | **383.8 seeds/s** |

The best word in the chunk (pmax 5.863) sits **1.52 below** the claim bar — the
same noise ceiling C2 saw on the prior slice (max pmax 5.904). No word cleared
the null, so recovery/held-out never gated a live candidate. Clean null.

## 4. Coverage (doctrine R2 — reported with power)

Cumulative words covered = this chunk's 506,593 tail words **plus** the 245,975
already swept by C2/S-G3 (200,000 dense baseline `[0, 200000)` + 433 prior words +
their ±512 neighbourhood, all ≥ 20.1M — excluded here so coverage is not
double-counted).

| | before this chunk | after this chunk |
|---|---|---|
| words covered | 245,975 | **752,568** |
| coverage of 2³² | 5.73 × 10⁻⁵ (0.00573%) | **1.75 × 10⁻⁴ (0.01752%)** |

**Power** (unchanged, inherited control): pair-decoder recovery on the
`skip_by_two` relation = **100%**, self-test confirmed each run.

## 5. Realistic size of the remaining tail (honest)

At **383.8 seeds/s single-core**, the remaining **4,294,214,728** words are:

- ≈ **3,108 core-hours** ≈ **129 core-days**, or
- ≈ **8,480 more ~20-minute chunks** at this single-core rate.

This is embarrassingly parallel — N cores divide the wall time (e.g. 32 cores →
~4 core-days of wall). Consistent with S-G3's ~7 core-days for the lighter
`exact` decoder (the `pair` decoder is ~2× heavier per word). **The prior is low
and the tail is enormous; one 22-minute chunk moves coverage from 0.0057% to
0.0175% of 2³².** This lane is a long grind by construction, not a near-term
finish.

## 6. Resume — the checkpoint

`progress.json` holds the resume cursor `next_seed = 3,506,593`, cumulative
`seeds_done = 506,593`, `best_pmax = 5.863`, `flagged_survivors = []`, and the
excluded-region record. The next chunk resumes exactly there:

```bash
cd liber-primus
python3 tests/validate.py                                          # 5/5
python3 analysis/round25/compute-tail/runner.py --self-test --seconds 1320
# resumes from progress.json cursor, appends chunk 2, checkpoints again
```

A word clearing the full three-clause gate **STOPS** the sweep immediately and is
**FLAGGED-FOR-ORACLE** (R21-L1 — the no-oracle proxy is leaky; never
auto-certified).

## 7. What this does and does not close

- **This chunk:** 506,593 fresh tail words, clean null under the
  control-validated `skip_by_two` pipeline. No corrected bound; nothing reopened.
- **Does NOT close:** 99.98% of the 2³² Py2.7-MT tail; other generators
  (bash/perl/tex, amd64 MT image, other reducers); offsets ≠ 0; the `permissive`
  (free-drift) preset. The standing verdict (LP2 0–54 is OTP-class) is unchanged.
