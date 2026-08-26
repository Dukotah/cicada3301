# ROUND 19 / G1 — READY: the Phase 2 run specification

_Written at the scoring boundary. G1 has validated its generators and built the keystream
interface; **this file is the handoff to S1**, not a result. Nothing in G1 has been
scored except the labelled plant/pilot in §6._

---

## 0. State of the gate

| gate | result |
|---|---|
| **G1-VAL** — every generator reproduces the real library byte-for-byte | **PASS, 19/19, zero failures** (`validation.json`) |
| **G1-ORB** — no era-correct variant has a cycle shorter than the 12,956-rune book | **PASS** — `bash4.2` LP64 cycle **2,147,483,646**; `bash4.2_i32` cycle **343,896** |
| **G1-WIN** — the sliding-window identity that licenses an O(2³¹ + L) sweep | **HOLDS** for `bash4.2`, `bash4.2_i32`, `bash3.2`, `bash5.1` |
| **plant + pilot** — the whole pipeline recovers a planted G1 key through I1 + I2 | **PASS, rank #1 of 9,600** (§6) |

**The era-correct generators are `bash4.2` (validated against a REAL GNU bash 4.2.0
binary) and `glibc_random` / `lrand48` / `drand48` (validated against the REAL system
glibc).** They are ready to sweep the moment Phase 0's gates pass.

---

## 1. The call S1 makes

```python
import sys; sys.path.insert(0, ".../analysis/round19/G1")
import keystream as KS

spec = {"family": "bash", "generator": "bash4.2", "seed": 3301,
        "reduction": "mod29", "sign": -1, "direction": "fwd",
        "atbash": False, "offset": 0}
K = KS.keystream(spec, n)            # n ints in 0..28
kid = KS.spec_id(spec)               # "bash4.2|3301|mod29|-1|fwd|False|0"

for spec in KS.enumerate_specs("bash4.2", range(0, 2**32)):   # lazy, does not materialise
    ...
```

`KS.PRIORITY` is the generator order S1 should walk — it is L1 §6.2's ranking, not
alphabetical. `KS.bash_sliding(variant, start_state, n_windows, klen)` is the
O(2³¹ + L) form for the bash family. `KS.shuf_keystream(path, n)` is the oracle path.

**One fact S1 must not lose:** for every `bash` generator, `seed` and `offset` are the
same axis (§3 of `RESULTS.md`). Sweeping the B-04 offset ladder on top of a *full* bash
seed enumeration buys exactly nothing; on top of a *partial* one it is a worse way of
covering more seeds. For `glibc` the offset ladder is a genuine extra axis.

---

## 2. The space, with sizes

| # | generator | seed space | distinct keystreams | class | L1 rank |
|---|---|---:|---|---|---|
| 1 | `glibc_random` (= `glibc_rand`) | 2³² − 1 | 2³² − 1 (state ≫ seed, no collapse) | enumerable | **row 1, ×3** |
| 2 | `bash4.2` (LP64) | 0…2³²−1 | ≤ 2,147,483,646 on-cycle + short transients (tail 13–72) | **enumerable, one orbit** | **row 4, ×2** |
| 3 | `bash4.2_i32` (ILP32) | 0…2³²−1 | ≤ 2³², dominated by transient trees (tail 210k–500k, cycle only 343,896) | enumerable | **row 4, ×2** |
| 4 | `lrand48` / `drand48_x2p53` / `mrand48` | 2³² | 2³² | enumerable | row 1 — but **`lrand48` and Perl-drand48 are CENSUS gens 10/11, already covered over 2011–2015 seconds. DE-DUPLICATE.** |
| 5 | `glibc_initstate{8,32,64,256}` | 2³² each | 2³² each | enumerable | row 1 (variant) |
| 6 | `bash4.0` | 0…2³²−1 | **deterministic prefix only** — the stream becomes time-seeded once the state reaches 0 | partially enumerable | row 4 |
| 7 | `bash3.2`, `bash3.2_i32`, `bash5.0`, `bash5.1`, `bash5.1c50` | 2³² each | LCG/Lehmer orbits | enumerable | **wrong era — completeness only, queue last** |
| 8 | `openssl_enc_rc4_k` | passphrases | — | **dictionary**; overlaps `R16-KDF` | row 6 |
| 9 | `shuf_random_source` | files | — | **dictionary** (58 LP2 JPEGs + PGP messages) | row 4 |
| — | `/dev/urandom`, bare `shuf`, `openssl rand`, `$SRANDOM` | — | — | **UNREACHABLE — do not report a null** | — |

**The priority subset.** bash 4.2's auto-seeded path (`sbrand(tv.tv_sec ^ tv.tv_usec ^
getpid())`, `variables.c:537`) can only reach **74 × 2²⁰ = 77,594,624** seeds for a run
between 2012-01-01 and 2014-06-01 — 3.6 % of 2³¹. It is a *subset* of the full range, so
a full enumeration subsumes it; its value is that **it tells S1 which 3.6 % to run
first**. See `RESULTS.md` §3.3 for the derivation.

**The cross:** 6 reductions × 2 signs × 2 directions × 2 Atbash × 1 offset =
**48 cells per (generator, seed)** at Stage A (`reduce29.variant_count("A")`), 240 at
Stage B. Note `mod29` and `rej29` are **near-aliases for a 15-bit source** (only 27 of
32,768 `$RANDOM` values are rejected), so the effective bash cell count is closer to 40.

---

## 3. Measured throughput (this box, one core)

| step | rate | how measured |
|---|---:|---|
| `skipdecode`-equivalent beam, `fastbeam`, L=120, w=400, skip=3 | **143 decodes/s** | timed loop |
| I1 `driftbeam.beam_decode`, same settings | ~**80 decodes/s** | from the pilot, net of the rest |
| I3 `vecbeam.batch_decode`, `keyskip1`, T=2000, L=120 | **166 decodes/s** | timed batch |
| **end-to-end pilot** (driftbeam + per-row `adjudicate` + pure-Python keystream) | **55 decodes/s** | `pilot.json` |
| I2 `adjudicate_batch`, L=120 | 1,007 rows/s | timed batch |
| **rigid head-window screen, L=31, 9-register panel, numpy** | **137,414 rows/s** | timed batch |
| rigid head-window screen, L=31, 1 register | 3.0e6 rows/s | timed batch |
| `gen_bash.raws` (pure Python), 544 draws | 1,235 keystreams/s | timed loop |
| `KS.bash_sliding` (master-orbit window) | 5,403 windows/s | timed loop |

---

## 4. What a full beam enumeration would cost — and why S1 must not attempt it

`bash4.2` alone: 2³² seeds × 48 cells = **2.06 × 10¹¹ decodes**. At the best measured
beam rate (166/s/core) that is 1.24 × 10⁹ core-seconds = **39 core-years**. Add
`glibc_random` and it is 78. **A full-enumeration beam sweep of this space is not
affordable, and G1 pre-registered that in `PREREG.md` §5 before measuring anything.**

Round 8 reached 2.52e9 decodes only because it used a *rigid* decoder in C — the decoder
D3 showed scores the correct key at **−6.835** while the beam gets **−4.170**
(LEDGER `B-21` coverage field: "Round 8 also used RIGID decode throughout"). Repeating
that trade is how this repository produced ten rounds of nulls that did not mean what
they said.

---

## 5. The run specification

### 5.1 Two stages, and the thing that has to be measured before stage 1 is legal

**Stage G1-S — the screen (enumerative).**
Rigid decrypt of a **head window** (L = 31, matching I3's `out_registers_L31.json`),
scored by **I2's 9-register panel z**, not by English quadgrams — because L7-A measured
English-only power at 0.33 for Latin and 0.00 for vowel-dropped English. Persist the
full `SWEEPROW` for retained rows (doctrine R3, `I2/SWEEPROW.md`).

The head window is legal under the key-skip cipher *only* because the desync begins at
the first skip: at LP2's ~1 skip per 35 runes, `P(no skip in the first 31) ≈ 0.41`, and a
skip late in the window still leaves a correct prefix.

> **BLOCKING PRECONDITION (doctrine R1).** The screen is an instrument. **I3 must
> measure its power before S1 runs it**: plant the correct key (G1 ships one —
> `plant.json`), run the L=31 head screen, and report what retention fraction keeps the
> plant with ≥ 95 % probability under a size-matched null at N ≈ 2 × 10¹¹. G1 has
> deliberately NOT calibrated this and must not. If the measured retention needed is
> larger than Stage G1-B can afford, the enumeration is not affordable at any stage and
> S1 should say so rather than shrink the window until the number looks nice.

**Stage G1-B — the beam (survivors only).**
The retained rows re-decoded with I1's `driftbeam` in **every published mode** —
`keyskip1`, `keyskip2`/`skip_by_two`, and the permissive/drift modes — because L7-B
showed the transition relation, not the search depth, is the hole. Adjudicated with I2,
thresholded with I3's `calib19.json`.

### 5.2 Estimated decode counts and wall-clock

Screen rate 1.374e5/s/core; assume **16 cores** (2.2e6 screens/s aggregate).

| slice | screens | core-time | wall-clock @16 cores |
|---|---:|---:|---:|
| **A. `bash4.2` auto-seed priority subset** — 77,594,624 seeds × 48 | 3.72e9 | 7.5 core-h | **28 min** |
| **B. `bash4.2` full 0…2³²** × 48 | 2.06e11 | 17.4 core-d | **26 h** |
| **C. `bash4.2_i32` full 0…2³²** × 48 | 2.06e11 | 17.4 core-d | **26 h** |
| **D. `glibc_random` full 0…2³²** × 48 (+ ~25 core-min of C-level seeding) | 2.06e11 | 17.5 core-d | **26 h** |
| **E. `glibc_initstate{8,32,64,256}`** × 4 | 8.2e11 | 70 core-d | 4.4 d |
| **F. `bash3.2/4.0/5.0/5.1` completeness** × 5 | 1.03e12 | 87 core-d | 5.4 d |
| **G. Stage G1-B beam on 10⁶ survivors × 3 decoder modes** | 3e6 decodes | 5.0 core-h | **19 min** |
| | | | |
| **recommended Phase-2 order: A → B → D → C → G, then E/F only if budget remains** | **4.2e11** | **≈ 52 core-days** | **≈ 3.3 days** |

Slices A–D + G are the whole of L1's rows 1 and 4 at **100 % seed coverage**, which no
previous round has ever reached for any generator (B-21: ~3 %; R16-PRNG: 0.004 %).

If the screen's measured power forbids Stage G1-S, the fallback is beam-only at a
**stated coverage fraction**: at 16 cores × 24 h = 2.3e8 decodes = 4.8e6 seeds = **0.11 %
of 2³²** per generator. That is 25× R16-PRNG's coverage and still a rounding error, and
it must be reported as such.

### 5.3 Non-negotiables for S1

1. Persist the full `SWEEPROW/1` (`I2/adjudicate.to_row`) for every scored decode.
   Retro-fitting is impossible; 10¹⁰ decodes already went that way.
2. Report all three conditionals on any negative: key space, **decoder transition
   model**, **adjudicator register**.
3. Recover `plant.json` at rank #1 before reporting any G1 negative. Also plant the
   **`skip_by_two`** variant — the plant G1 ships uses `encipher_keyskip`, and L7-B's
   whole point is that a one-character variant of that loop is missed at −6.90.
4. De-duplicate `lrand48` / Perl-drand48 against `round10/L5-seed32/CENSUS.md` §B
   generators 10 and 11 rather than re-running measured ground (doctrine §4 r6).
5. Never report a null for `/dev/urandom`, bare `shuf`, `openssl rand` or `$SRANDOM`.
   They are unreachable, which is a property of the object, not of the effort.

---

## 6. The pilot (labelled: a pilot, not a sweep)

I1's `driftbeam.py` and I2's `adjudicate.py` were both published before G1 reached this
boundary, so G1 ran the ≤10,000-decode pilot its brief allows.

```
decodes                  9,600   (200 seeds x 48 cells, planted seed included)
wall-clock               173.8 s  ->  55.2 decodes/s/core end-to-end
decoder                  round19/I1/driftbeam.py, mode=keyskip1, w=400, max_skip=3
adjudicator              round19/I2/adjudicate.py
planted spec             bash4.2|3301|mod29|-1|fwd|False|0
planted rank by English  #1 of 9,600
planted rank by I2 pcon  #1 of 9,600
planted row              en=-4.356  pmax=+26.22  pcon=+20.86  ioc=1.612  mds=13  zl=0.808
best WRONG-key English   -6.214     (separation 1.86)
```

The #2 row is `bash4.2|3301|rej29|...` — the *same* key under a near-alias reduction, not
a wrong key, because only 27 of 32,768 `$RANDOM` values are rejected.

**This pilot carries no verdict.** It proves that a G1 keystream, enciphered under the
repo's key-skip model, survives I1 + I2 and lands first. It says nothing about LP2.

---

## 7. Reproduce

```bash
cd liber-primus/analysis/round19/G1
bash fetch_bash_src.sh            # bash 3.2-5.2 sources + a real bash 4.2 binary
python3 validate.py               # THE GATE. 19/19 PASS, writes validation.json
gcc -O2 -o /tmp/orbit orbit.c && /tmp/orbit -n 3 bash4.2 bash4.2_i32
python3 keystream.py              # the production interface, smoke test
python3 plant.py --plant          # build plant.json
python3 plant.py --seeds=200      # the pilot (requires I1 + I2)
```
