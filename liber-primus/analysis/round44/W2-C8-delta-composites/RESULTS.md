# Round 44 / WAVE-2 CELL C8 — DELTA-STREAM COMPOSITES k≥7 / OUT-OF-SET FEEDBACK — RESULTS

**Verdict: NEGATIVE (clean, control-validated).** 0 of 1,186,976 pre-registered rows cross the
bars_v3 free bar under panel-R36. The R12-C1 `not_covered` edge that R43 X0 names as "item 1
edge" — lag-k composites k≥7 and feedback functions outside the original 7-f set — is now
measured, and for the FIRST time this family is adjudicated by a register panel rather than
the English quadgram scorer (the L7-A hole the original row carried).

PREREG hash-stamped in `run.log` before first execution (`19b62fb6…` original;
`13275c08…` after the pre-run addendum 6b, both before any plant or decode ran).
Trust anchor `tests/validate.py`: ALL VALIDATIONS PASSED before scoring.

## Positive control — PASSED (plant_gate.py, plant_results.json)

20/20 round-trip asserts (every family × source branch incl. mix, k ∈ {7,13}) plus FIVE
plants pushed through the IDENTICAL full-enumeration sweep path (21,196 rows each):

| plant | construction | pmax | bar | argmax=planted | other crossers |
|---|---|---|---|---|---|
| P1 | lag-7 ct difference composite (a,b)=(1,28), EN | 53.03 | 25.1583 | yes | 0 |
| P2 | pt-affine k=9 (1,1) seed eq4, REV, EN | 53.02 | 25.1583 | yes | 0 |
| P3 | ct-window prod k=13 sign +1, EN | 53.10 | 25.1583 | yes | 0 |
| P4 | P1 construction over LATIN | 42.51 | 25.1583 | yes (non-EN register) | 0 |
| P5 | 240-rune EN segment via the segment driver | 26.44 | 15.5204 | yes | 0 |

Addendum 6b's feared P3 sign-sibling crosser did not fire (0 non-planted crossers on every
plant). Short-L power diagnostics (no gate): planted decode crosses at scored n=113
(pmax 18.49 ≥ 15.52) and does NOT cross at n=59 (12.19 < 15.52) — power is validated down to
roughly n≈113 and is honestly absent for the shortest segments.

## Real sweep (sweep.py → sweep_results.json, rows.npz)

Exactly the PREREG §2 enumeration: 21,196 rows/stream × (1 continuous 12,956-rune unsolved
stream + 55 segments) = **1,186,976 rows** (1,096,136 primary scored-length ≥ 120; 90,840
short-L diagnostic rows). Bars fixed in advance at N_bar = 1.5e6 ≥ actual N:
120→15.5204, 240→20.8883, 400→21.9469, 729→25.1583 (`bars_v3(1.5e6, L, "free")`).

- **Crossers: 0.** Nothing was flagged; nothing goes to the oracle.
- **Best overall: pmax 5.397** (segment 1, fwd, k=13, ct-affine cell (1,15), n=253) vs its
  bar **20.8883** — a 15.5-point shortfall, register LP1_REAL, well inside segment-max noise.
- Continuous-scope best: 1.356 (ct-affine) vs bar 25.1583.
- Family bests (pmax): ct-affine 1.356/5.397 (cont/seg), ct-window 0.995/4.619,
  pt-mix-affine 1.101/5.193, pt-mix-window 1.109/5.247.
- **Diagnostic null gap** (null_diag.json): 200 shuffled-stream draws × the 812-cell
  ct-affine k=7 batch → per-draw max pmax mean 1.065, p99 1.322, max 1.423. The free bar
  (25.16 at the continuous length) is therefore hugely conservative for this deterministic
  decoder — and the plants still clear it by 2×, so the conservatism costs no verdict power
  at the primary lengths.
- Wall: 401 s total (31 s plants).

## Coverage

Lag-(1,k) affine composites k=7..13: FULL 29×28 (a,b) grid on the ct source (seedless ⇒
exhaustive given the construction), the 6-cell negation-closed composite set
{(1,1),(1,28),(28,1),(28,28),(0,1),(0,28)} on pt/mix sources over the 29 all-equal seeds
(R12-C1's documented representative probe); out-of-set window f ∈ {prod, max, min} × both
signs × all three sources × same seeds; both orientations; continuous + all 55 segments;
panel-R36 (12 registers) × bars_v3 at N_bar=1.5e6. Measured plant power: 1.0 recovery on all
five planted constructions, bar-crossing at scored n ≥ 113; register axis demonstrated by
the Latin plant.

## not_covered (carried into ledger_rows.json verbatim)

k ≥ 14; the full affine grid under pt/mix sources (only the 6 composite cells swept there);
arbitrary (non-all-equal) seeds; lag pairs other than (1,k); 3-term and higher combos;
nonlinear f outside {affine-2-term, prod, max, min}; b=0 scaled lag-1; composite +
skip/interrupter hybrids (this decoder models NO rejection loop — the L7-B axis);
scored lengths < ~113 at guaranteed power (segments 49/50/54, segment 32, segment 22 at
k∈{12,13} are diagnostic-only); registers outside panel-R36's 12; R12-C1's ORIGINAL k=2..6 ×
7-f ground is NOT re-adjudicated here (remains an English-quadgram-only negative per its row).

## Three conditionals

1. **Key space:** the PREREG §2 enumeration only (counts above) — not "all feedback ciphers".
2. **Decoder transition model:** deterministic single-pass left-to-right feedback decode
   p=(c±K) mod 29; no rejection loop, no skips, no interrupter/null-F handling.
3. **Adjudicator register:** panel-R36's 12 registers; a plaintext in a register outside
   them would be missed independently of the key space.

## Flags

None. No bar-crosser, so nothing is FLAGGED-FOR-ORACLE.

Reproduce: `python3 plant_gate.py && python3 sweep.py` (pure python3+numpy, no network;
rows.npz and the JSONs regenerate).
