# Round 24 — C2-EXT — broaden the `skip_by_two` closure — RESULTS

**Verdict: CLEAN NULL on all 7 axes, every positive control validated.** Broadening
the skip_by_two audit beyond C2's Py2.7 offset-0 slice — to bash `$RANDOM`, perl,
tex, sha256_ctr keytexts, non-zero Py2.7 offsets, and the continuous `free_drift` /
`drift_at` cousin — **reopens nothing.** L7-B now closes across generators, offsets,
and the drift cousin too, **for the swept prior-dense slices** (partial coverage,
stated per axis below — this is not full-space closure of any generator).

_Pre-registered in [`PREREG.md`](PREREG.md), frozen before scoring any real
ciphertext. Trust anchor `tests/validate.py` = **5/5 PASS**._

---

## 1. Decision-relevant finding (read this first)

C2 discharged L7-B (every beam-based negative covers a one-symbol-per-rejection
loop) for the top-prior **Py2.7-MT generator, offset 0**, under the pair
(`keyskip2`) decoder — the relation the beam cannot represent. It left OPEN whether
the same skip_by_two hole reopens a beam-based negative under **other generators**,
at **non-zero offsets**, or under the **continuous drift cousin**.

C2-EXT re-decoded the prior-dense slice of each of those axes under the
control-validated decoder that models the axis' relation. **0 hits over 113,432 keys
across 7 axes.** The single closest approach (A6 drift, seed 4437, pmax 9.287,
self-consistent recovery 0.911) is **4.6 below its pre-registered claim bar** and
well inside the wrong-key null tail. **No beam-based negative reopens over any swept
axis; no corrected bound is needed for these slices.**

## 2. Positive controls — ALL VALIDATED (`control_ext.py` → `control_ext.json`)

Per axis: plant the axis' relation using the axis' **own generator** as the key,
L=240, held-out `self_reliance.txt`, 7 seeds. Pair decodes skip_by_two (A1–A5);
drift decodes the continuous cousin `free_drift` + `drift_at` (A6).

| axis | generator | decoder | plant | dec median rec | beam median rec | VALID |
|---|---|---|---|---|---|---|
| A1 | bash `$RANDOM` mod29 | pair | skip_by_two | **100.0 %** | 17.1 % | YES |
| A2 | perl `int(rand(29))` | pair | skip_by_two | **100.0 %** | 11.7 % | YES |
| A3t | tex `pgf_rnd29` | pair | skip_by_two | **100.0 %** | 10.8 % | YES |
| A3l | tex `lcg_mod29` | pair | skip_by_two | **100.0 %** | 20.0 % | YES |
| A4 | sha256_ctr (B04 dict) | pair | skip_by_two | **100.0 %** | 10.0 % | YES |
| A5 | Py2.7-MT random29 | pair | skip_by_two | **100.0 %** | 24.2 % | YES |
| A6 | Py2.7-MT (free_drift) | drift | free_drift | **98.3 %** | 32.9 % | YES |
| A6 | Py2.7-MT (drift_at) | drift | drift_at | **98.3 %** | 12.1 % | YES |

Every axis: the decoder recovers ≥0.90 where the beam gets 10–33 %. The instrument
that produced each null **can see the plant on that axis' generator**; the beam that
produced the historical negatives cannot. No axis is UNVALIDATED. All cleared to
score the real ciphertext.

## 3. The sweep (`sweep_ext.py` → `sweep_ext.json`)

Ciphertext: canonical unsolved LP2 (`lib_numchannel.unsolved()`), screen `C[:120]`,
gate `C[:240]`, sign −1. Two-stage per C2 (Stage A beam_w=64 screen → promote
pmax≥5.0; Stage B `hitfn20.evaluate` at the axis' preset). dense=20000 per int-seed
axis; A4 = full B04 dictionary; A5 = top-64 seeds × offsets 1..16.

| axis | keys screened | frac of gen space | screen survivors | **HITS** | max pmax | claim bar |
|---|---|---|---|---|---|---|
| A1 bash | 20,487 | 4.8×10⁻⁶ | 1 | **0** | 5.204 | 7.384 |
| A2 perl | 20,487 | 4.8×10⁻⁶ | 3 | **0** | 5.715 | 7.384 |
| A3t tex-pgf | 24,418 | 1.1×10⁻⁵ | 3 | **0** | 5.210 | 7.384 |
| A3l tex-lcg | 24,418 | 1.1×10⁻⁵ | 1 | **0** | 5.563 | 7.384 |
| A4 sha keytexts | 2,165 | full dict | 0 | **0** | 4.669 | 7.384 |
| A5 Py2.7 offsets | 1,024 | 2.4×10⁻⁷ | 0 | **0** | 3.969 | 7.384 |
| A6 free_drift | 20,433 | 4.8×10⁻⁶ | 1,803 | **0** | 7.719* | 13.842 |
| **total** | **113,432** | — | 1,811 | **0** | — | — |

\* A6 stage-A screen max 7.719; the highest stage-B survivor pmax is **9.287**
(seed 4437, rec 0.911, held 0.911) — still 4.6 below the 13.842 drift claim bar and
below even the family-wise bar at the actual stage-B N (11.117). **0 survivors clear
the claim bar on any axis.** Every screen survivor fails **clause 1** (pmax < the
axis' claim bar). Several show self-consistent decodes (rec 1.0 / held 1.0) — those
are the expected noise C2 documented, not hits: a self-consistent low-alphabet decode
that does not clear the panel-max null. Elapsed 1,038 s.

**Why A6 has 1,803 screen survivors and the pair axes have ~1–3.** The drift
(permissive, max_skip=40, max_free=2) decoder is deliberately loose, so ~9 % of keys
clear the low pmax≥5.0 screen — exactly why its claim bar is calibrated at 13.842,
not 5.5 (round19-I1 §9). The recovery+claim-bar gate then rejects all 1,803.

## 4. Red-team (R6, mandatory) — FP ceilings refute any survivor (`redteam_ext.py`)

Seed-3301 order-matched wrong-key null under the **same** decoder per axis, on the
**same** ciphertext, 2,000 wrong keys/axis not in that axis' prior:

| axis | wrong clearing screen | **clearing full gate** | wrong-key pmax max | claim bar |
|---|---|---|---|---|
| A1 bash | 0/2000 | **0** | 4.351 | 7.384 |
| A2 perl | 0/2000 | **0** | 4.197 | 7.384 |
| A3t tex-pgf | 1/2000 | **0** | 5.039 | 7.384 |
| A3l tex-lcg | 0/2000 | **0** | 4.464 | 7.384 |
| A4 sha | 1/2000 | **0** | 5.040 | 7.384 |
| A5 Py2.7 off | 0/2000 | **0** | 4.545 | 7.384 |
| A6 drift | 177/2000 | **0** | 7.010 | 13.842 |

**0 wrong keys clear a full three-clause gate on any axis.** P(wrong key clears the
gate) < 1/2000 everywhere; expected FP over each axis' real slice ≈ 0. The A6
wrong-key screen-pass rate (177/2000 ≈ 8.9 %) matches the sweep's A6 screen-survivor
fraction — confirming the sweep's A6 survivors are the same wrong-key noise, and the
13.842 bar is doing its job. Refute-by-default holds trivially: **there is no
survivor to flag** — 0 hits, and the FP ceiling would swallow any near-bar candidate.

## 5. Coverage × power (doctrine R2 — both reported, per axis)

- **Power:** the decoder recovery on each axis' relation (§2): 100 % for skip_by_two
  under bash/perl/tex/sha/Py2.7-offset (pair), 98.3 % for free_drift/drift_at
  (drift), vs the beam's 10–33 %. Every null was produced by an instrument that can
  see its axis' plant.
- **Coverage (PARTIAL — stated honestly):** 113,432 keys across 7 axes. The bash /
  perl / tex axes each cover only ~10⁻⁵–10⁻⁶ of their 2³¹–2³² seed spaces (the
  Cicada-integer prior + a 20k dense tail) — this is **prior-dense partial
  coverage, not full-space closure.** A4 (sha256_ctr keytexts) IS full over the B04
  seed dictionary. A5 covers top-64 seeds × 16 offsets. A6 covers the 433-seed
  prior + 20k dense. The full 2³² tail of each generator remains a compute-only lane,
  explicitly out of scope (PREREG §0).

## 6. What this does and does not close

- **Closes (for the swept slices):** the L7-B reopener over bash `$RANDOM`, perl,
  tex (pgf+lcg), the full sha256_ctr keytext dictionary, non-zero Py2.7 offsets, and
  the continuous free_drift/drift_at cousin. The beam-based negatives are valid over
  the skip_by_two transition **and** the drift cousin on all these slices.
- **Does NOT close:** the full 2³²/2³¹ seed tails of bash/perl/tex (compute-only,
  out of scope); Py2.7 offsets beyond o=16 or seeds beyond the top-64; free_drift q
  or drift_at ndrift regimes beyond the control settings; public-pad (no seed to
  enumerate — excluded by construction). These are cheap re-runs of these scripts
  with a larger `--dense` / different axis parameters.

## 7. Reproduce

```bash
cd liber-primus
python3 tests/validate.py                                              # 5/5
python3 analysis/round24/C2-ext-skip-generators/control_ext.py         # -> control_ext.json (8/8 VALIDATED)
python3 analysis/round24/C2-ext-skip-generators/redteam_ext.py --n 2000 # -> redteam_ext.json (0 FP)
python3 analysis/round24/C2-ext-skip-generators/sweep_ext.py --dense 20000 # -> sweep_ext.json (0 hits)
python3 analysis/handoff/validate_ledger.py                            # Unsound=0
```
