# Round 24 — C2 — `skip_by_two` decoder — PRE-REGISTRATION

_Frozen 2026-08-30 BEFORE scoring the real ciphertext slice. Binding:
`../../ARMADA-DOCTRINE.md`, `../PLAN.md` §C2 pre-reg. Trust anchor
`tests/validate.py` = 5/5 PASS confirmed before this file was written._

## 0. What C2 is (and is not)

C2 audits the closure the round-18 red-team named `L7-B`: **every beam-based
negative in this repository covers only a rejection loop that advances the key by
exactly one symbol per rejection.** If the real 2013 rejection sampler burned
**two** draws per rejection (`skip_by_two`, `j += 2`), the correct key is
recoverable only by a decoder that models that relation, and the repo beam
(`campaign18_skip.beam_decode` == `driftbeam` mode `keyskip1`) provably cannot
represent it (L7-B: −6.90 score, 25.8 % recovery, unchanged by beam width or skip
budget — the true path is outside the transition relation, not beyond search depth).

This is a **bound-tightening / instrument-audit lane**, not a new key-space. Its
realistic outcomes are (a) NULL under a decoder that CAN represent skip_by_two →
the L7-B axis is closed and the beam-based negatives are confirmed valid over it
for the swept slice, or (b) a bar-clearing survivor → FLAGGED-FOR-ORACLE (never
auto-certified; the R21-L1 seal — the no-oracle proxy is leaky).

## 1. The decoder (the transition relation the beam cannot express)

`driftbeam.beam_decode(..., mode="keyskip2", max_skip=8)` — preset `"pair"`.
Relation: **skipped key positions come in PAIRS; the first of each pair must
reproduce `c_prev`, the second is UNCONSTRAINED.** That is exactly the
`enc_skip_by_two` encipher relation (`j += 2` on reject: one position is
constrained to double, one is silently burned). Gated G-EQ-identical to the repo
beam when `mode="keyskip1"` (24 cases, |Δscore| < 1e-14, 0 path mismatches —
`round19/I1/out_eq.json`), so the ONLY axis that differs vs every beam-based
negative is the transition relation.

## 2. Positive control (MANDATORY — run and passed BEFORE this freeze)

`control.py`, protocol identical to `round18/L7-redteam/b1_power_envelope.py`
(L=240, `sha256_ctr` key, held-out English from `self_reliance.txt`, seeds 3301+s,
7 seeds), plant `enc_skip_by_two` at supp ∈ {0.4, 0.83, 1.0}. Recorded in
`control.json`. Result (frozen):

| supp | beam keyskip1 (ms3=ms8) | **pair keyskip2** | ct-doublet |
|---|---|---|---|
| 0.40 | −5.897 / 59.6 % | **−4.285 / 100.0 %** | 2.09 % |
| 0.83 | **−6.903 / 25.8 %** | **−4.285 / 100.0 %** | 0.84 % |
| 1.00 | −6.857 / 24.6 % | **−4.285 / 100.0 %** | 0.00 % |

Beam at supp=0.83 reproduces L7-B's canonical −6.90 / 25.8 % to 3 s.f. The pair
decoder recovers **100 %** at every supp (min-over-seeds 100 %). **CONTROL
VALIDATED** (pair median recovery ≥0.90 at every supp AND beam <0.90 everywhere).
Per the rule, C2 is cleared to score the real slice.

## 3. The slice to sweep (top-prior, per PLAN §C2 — frozen)

The single highest-prior LP2-plausible key generator, at the top-prior seed slice,
re-decoded under the **pair** decoder. This mirrors `round20/S-G3/sweep.py`
one-for-one except the decoder preset is `"pair"` instead of `"exact"`:

- **Generator:** Python-2.7 `MT19937().init_by_array([w])`, reducer `random29`
  (`round19/G3/gen_py27.py`) — the idiomatic Py2.7 `random.seed(int)` → 0..28
  stream. This is the S-G3 generator; it is the generator the P3b seed prior
  (`seedprior20.json`, 433 ranked unix seconds, rank-1 = 1325734783 = the 3301 key
  creation second) was built for.
- **Ciphertext:** the canonical unsolved LP2 runes, `lib_numchannel.unsolved()`.
  Screen on `C[:120]`, adjudicate/gate on `C[:240]` (S-G3's L_SCREEN / L_HIT).
- **Word order (frozen, = S-G3 `build_word_order`):**
  1. block 0 — the 433 prior words themselves;
  2. block 1 — ±512 neighbourhood of the top 64 prior words;
  3. block 2 — dense contiguous baseline from w=0, filling the time-box.
- **sign = −1, o = 0**, matching S-G3 and the control.

## 4. Hit function (frozen — reuse `round20/HITFN/hitfn20`)

`hitfn20.evaluate(HitDecode(C=C[:240], K, o=0, preset="pair",
n_round_adjudicated=N_ADJ))`. A HIT requires ALL THREE (unchanged from R20):
1. `pmax` clears the panel-max null for the **pair** preset:
   `panelmax20.panelmax_bar(preset="pair", n_round_adjudicated=N_ADJ, alpha=0.01)`
   = **7.384** at N=1e6 (the pair-preset cell `I19:driftbeam.pair+I2|pmax|L120`,
   fitted on wrong-key pair decodes — NEVER −5.5, NEVER another preset's bar).
2. rune-INDEX recovery ≥ 0.90 (real candidate: held-out self-consistency; plant:
   vs truth_idx). Score alone is never a hit.
3. held-out 3/4 recovery ≥ 0.90 under the same key.

Two-stage to fit the time-box: **Stage A** cheap pair screen (beam_w=64, L=120)
→ promote words with `pmax ≥ SCREEN_BAR = 5.0` (frozen; ≪ the 7.384 claim bar,
the S-G3 value; plant clears far above, wrong keys ≤ ~4.2). **Stage B** full
`hitfn20.evaluate` at the pair preset on survivors.

## 5. Null, family-wise bar, FP ceiling (frozen)

- **Null:** seed-3301 wrong-key decodes under the SAME pair decoder,
  order-matched (`redteam.py`): draw K from `init_by_array([w])` for words NOT in
  the prior (random 32-bit words seeded by `random.Random(3301)`), decode the SAME
  `C[:120]` under `mode="keyskip2"`, record pmax. The FP ceiling is the number of
  those wrong keys that clear `SCREEN_BAR` and then the claim bar.
- **Family-wise bar:** the pair panel-max bar at the ACTUAL number of words
  adjudicated in Stage B (`panelmax_bar("pair", n_stage_b, 0.01)`), reported
  alongside the N=1e6 reference bar. Never −5.5.
- **Expected FP over the screened slice:** `N_screened · P(wrong pair key clears
  the full three-clause gate)`. Measured directly from the seed-3301 null in
  `redteam.py`; the pre-registered expectation is **< 1** over the whole slice (the
  claim bar α=0.01 is a per-1e6 panel-max tail; the three-clause recovery gate is
  far stricter — R20 measured 0/4000 wrong keys clearing it).

## 6. Decision rule (frozen)

- **NULL** if 0 words clear the three-clause pair gate at the pair claim bar AND
  the seed-3301 null produces ≤ its expected FP. → the L7-B axis is closed over
  this slice; the beam-based negatives are **confirmed valid** over the
  skip_by_two transition on the swept generator/slice.
- **HIT-flagged-for-oracle** if any word clears the full gate. NEVER
  auto-certified (R21-L1 seal). Red-team (R6) recomputes the FP ceiling under the
  pair decoder and refutes-by-default before the flag stands.
- **INCONCLUSIVE** if the control had failed (it did not) or the slice proved
  infeasible in-session (it is not — stage-A ≈1 ms, stage-B ≈0.24 s/word).

## 7. Coverage × power (report both — doctrine R2)

- **coverage** = the exact count of Py2.7-MT `init_by_array([w])` words screened
  under the pair decoder (block 0 + block 1 + as much of block 2 as the time-box
  buys) — reported as a fraction of 2^32.
- **power** = the measured pair-decoder recovery for the skip_by_two relation:
  **100 %** (control §2), vs the beam's 25.8 % that L7-B recorded. This is the
  number L7-B said was 0.258 for the beam.
