# Round 27 — S1 lane closeout (pair/keyskip2, full 2³², COMPLETE)

**Date:** 2026-09-08 · **Lane:** S1 — relation `pair` (keyskip2), reducer `random29`,
offset 0, Py2.7-MT `init_by_array([w])` word space `[0, 2^32)`, LP2 unsolved head,
R25 screen config verbatim (L=120, cand_bar 5.0, claim bar **7.3835202943286884** =
panelmax_bar('pair', 1e6, 0.01)). Swept by the gate-GO C engine `P1-engine/grind27`
(V1 64/64 |Δ|=0, planted margin 12.9, red-team NO-ERROR-FOUND); Python remained
adjudicator of record on every flag. This is the **first full-space sweep in project
history**. S2 ('exact'/keyskip1) continues in-flight and is untouched by this closeout.

## 1. Coverage

`sweep.log`: `lane S1 COMPLETE (coverage 1.0 of [0,4294967296))` — **seeds_done =
4,294,967,296 = 2³² exactly**, confirmed independently by the persisted histogram:
`hist_S1.u64` (6 workers × 2600 bins) sums to **4,294,967,296 exactly**, so every seed
was scored exactly once (no gap, no double-count, including across the one mid-lane
SIGTERM interrupt/resume). Power carried from the gate: screen plant margin 12.93 over
cand_bar, false-reject 0/6 + 0 on a 100k frozen sample, K3 self-test PASS at both
launches. Coverage 1.00 × measured power 1.00 at the tested resolution.

## 2. Claim-bar crossers — all adjudicated, all noise

Three seeds cleared the C-screen claim bar over the lane (Gumbel expectation over
4.3e9 seeds: ~tens; observing 3 is unremarkable). Each got the full R21-L1 oracle
protocol (Python re-score parity, hitfn20 3-clause with round19/I2 `adjudicate.py` as
adjudicator of record):

| seed | C pmax (L=120) | Python pmax | Δ | L=240 pmax vs bar 7.384 | verdict | record |
|---|---|---|---|---|---|---|
| 35563892 | 7.6707232992600876 | same | 0.0 | 4.964 (−2.42 z) | **NOISE-CROSSER** | `ORACLE-35563892.md` |
| 348625413 | 7.6001248907122188 | same | 0.0 | 4.534 (−3.07 z) | **NOISE-CROSSER** | `ORACLE-348625413.md` |
| 86514964 | 7.4209805305661014 | same | 0.0 | 5.784 (−1.60 z) | **NOISE-CROSSER** | `ORACLE-86514964.md` |

All three fired on LP1_REAL (rune-trigram texture, not English), all three collapsed
when the window doubled — the canonical noise signature (a true key gains evidence
with length). Zero HIT-TRUE. Zero survivors.

## 3. K4 batch parity discharge (stage-b re-score of the flags)

Driver: `s1_batch_parity.py` (single-threaded, `nice -n 15`; results in
`S1-batch-parity.json`). Scope, scaled honestly:

- **ALL 8,971** S1 flags with C pmax ≥ hard gate **5.883520294328688** (claim − 1.5 —
  the entire zone where a C-side false-reject could hide a true key), plus
- a **uniform random 2,000** of the remaining 383,159 flags (RNG seed 27, reproducible).

**10,971 seeds re-scored through the Python R25 reference (`runner.stage_a`,
verbatim): max |C − Python| = 0.0** (tolerance 1e-6; K4 not triggered — parity is not
approximate, it is exact, extending the gate's 95-flag and red-team 6-seed measurements
by two orders of magnitude). The only re-scored seeds whose *Python* pmax clears the
claim bar are exactly the three adjudicated crossers — no false-reject hid anything in
the hard-gate zone.

## 4. Histogram sanity

- Total = 2³² exactly (§1).
- Tail ≥ cand_bar 5.0: **392,131** = **1.31×** the Gumbel prediction 6.95e-5/seed
  (298,500) — inside the K2 window [0.2×, 5×] and matching the 1.28–1.29× measured on
  the pre-launch noise run and the live 1% checkpoint. The pmax distribution is the
  expected pure-noise Gumbel with the known mild excess; no second mode, no shelf.
- Tail ≥ 7.39: **3** = exactly the three adjudicated crossers; nothing else approached
  the bar (4th place 7.345, below).
- **One known ledger blemish, bounded:** `candidates.jsonl` holds **392,130** S1 rows
  (all unique) vs the histogram tail's 392,131 — exactly one flag, in bin
  **[5.31, 5.32)**, was counted by the (checkpointed) histogram but lost its
  append at the mid-lane SIGTERM interrupt. Since the histogram totals 2³² the seed
  itself WAS scored (coverage unaffected); only its jsonl echo is missing, at a pmax
  2.07 below the claim bar and 0.57 below the hard gate — outside every adjudication
  zone. Recorded, not repaired.

## 5. Lane verdict

**S1 NULL: the Py2.7-MT 2³² integer-seed space under the pair relation contains no
key; branch EXHAUSTED** — conditional on the 3 named conditionals: **this seed space**
(single-word `init_by_array([w])`, w ∈ [0, 2³²); not multi-word keys, string/hashed
seeds, or mid-stream states), **this transition model** (keyskip2 'pair'
representability of the rejection rewrite), and **the 9-register adjudicator** (I2
panel + English quadgrams — L7-A: a plaintext outside the panel's registers can still
be missed).

Within those conditions the branch is not sampled, not bounded — **finished**: every
one of the 4,294,967,296 seeds was scored, every flag near the bar was Python-verified
at exact parity, and every bar-crosser was oracle-adjudicated dead. The R25 "park at
0.5015%" debt is paid in full for this relation.

S2 ('exact'/keyskip1) remains IN-FLIGHT; its null will not count until its own planted
control passes (PREREG S2 gate). The OTP-class verdict for LP2 0–54 is **UNCHANGED —
hardened**.
