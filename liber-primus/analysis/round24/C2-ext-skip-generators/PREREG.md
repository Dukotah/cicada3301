# Round 24 — C2-EXT — broaden the `skip_by_two` closure — PRE-REGISTRATION

_Frozen 2026-08-30 BEFORE scoring the real ciphertext under any new axis. Binding:
`../../../ARMADA-DOCTRINE.md`, `../C2-skip-by-two/PREREG.md` (the parent lane).
Trust anchor `tests/validate.py` = 5/5 PASS confirmed before this file was written._

## 0. What C2-EXT is (and is not)

The parent lane **C2** built the control-validated `pair` decoder (`driftbeam`
mode `keyskip2`, preset `pair`) — the transition relation the repo beam **cannot**
represent (L7-B) — and discharged `L7-B` for the **top-prior Py2.7-MT (S-G3) seed
slice only**, at **offset 0**, under the **pair** decoder. It got a clean null.

C2's RESULTS explicitly left OPEN, over the *same* decoder that already exists:

- skip_by_two under **other generators**: bash `$RANDOM`, perl, tex,
  sha256_ctr-keytexts, (public-pad is out — it has no seed to enumerate);
- **deeper seeds / non-zero offsets** under the top-prior Py2.7-MT generator;
- the **continuous cousin** `free_drift` / `drift_at`, which needs the
  `permissive` (`drift`) preset, not `pair`.

C2-EXT sweeps the **feasible, prior-dense slice** of each of those axes. It does
**NOT** brute the full 2^32 tail of any generator (that is the compute-only lane,
out of scope). Where an axis is only feasible as a thin slice, the covered
fraction is reported honestly; a thin slice is **never** presented as full closure.

This remains a **bound-tightening / instrument-audit lane**, not a new key-space.
Realistic outcomes per axis: (a) NULL under a decoder that CAN represent the axis'
relation → the axis is closed for the swept slice and the beam-based negatives are
confirmed valid over it there; (b) a bar-clearing survivor → **FLAGGED-FOR-ORACLE**
(never auto-certified; the R21-L1 seal — the no-oracle proxy is leaky); (c)
UNVALIDATED if the positive control for that axis fails (then no null is claimed
over it).

## 1. The decoders (unchanged from C2 / round19-I1)

- **`pair`** = `driftbeam` mode `keyskip2`, `max_skip=8`, `max_free=0`, `lam=0` —
  skipped key positions come in PAIRS; the first of each pair reproduces `c_prev`,
  the second is UNCONSTRAINED. Exact for `enc_skip_by_two` (`j += 2` per rejection).
  G-EQ-identical to the repo beam when `mode="keyskip1"` (round19/I1 `out_eq.json`).
  Used for axes 1–5.
- **`drift`** = `driftbeam` mode `permissive`, `max_skip=40`, `max_free=2`,
  `lam=12`, `start_slack=2` — the construction-agnostic preset (round19-I1 RESULTS
  §9): admits ANY key advance ≤ max_skip per rune, ≤ `max_free` of which need not be
  doublet-consistent, at penalty `lam`. Covers the *continuous* cousin
  `free_drift` / `drift_at` (an extra key advance for an unrelated reason). Used for
  axis 6.

## 2. Positive control per axis (MANDATORY — run and scored BEFORE any real decode)

For **each** axis, plant → recover to confirm the decoder actually models that
axis' relation on that axis' generator, and confirm the beam does NOT. Protocol
mirrors the parent C2 `control.py` (L=240, held-out English `self_reliance.txt`,
7 seeds), except the KEY is drawn from that axis' generator and (axis 6) the plant
is `enc_free_drift` / `enc_drift_at` decoded with the `drift` preset.

- **Validated** iff pair (or drift, axis 6) **median recovery ≥ 0.90** over seeds
  AND the beam (`keyskip1`) median recovery **< 0.90** on the same plant.
- If a control **fails**, that axis is marked **UNVALIDATED** and NO null is claimed
  over it (doctrine: an instrument that cannot see the plant cannot prove a null).

Controls are scored first and recorded in `control_ext.json` before any real-slice
decode is written.

## 3. The axes and their prior-dense slices (frozen)

Ciphertext for every axis: canonical unsolved LP2 (`lib_numchannel.unsolved()`),
screen on `C[:120]`, gate on `C[:240]`, **sign = −1**. Offset 0 unless the axis IS
the offset axis. Two-stage per C2: Stage A cheap screen (beam_w=64, L=120) → promote
`pmax ≥ SCREEN_BAR = 5.0`; Stage B full `hitfn20.evaluate` on survivors.

| # | axis | generator + reducer | prior-dense slice (frozen) | decoder |
|---|---|---|---|---|
| A1 | bash `$RANDOM` | `gen_bash` bash4.2 (LP64) → `reduce29.mod29` | B04 integer seed set (NUM_INTS, primes, 3301-family) ∪ the 433 Py2.7 seedprior seconds reused as `RANDOM=<int>` ∪ dense contiguous block from `RANDOM=1`. (offset ≡ seed for bash — measured, `keystream.py` docstring — so no separate offset axis.) | pair |
| A2 | perl `int(rand(29))` | `gen_perl` r29 (drand48) | same integer seed set ∪ dense contiguous block from seed 1 | pair |
| A3 | tex | `gen_tex` pgf_rnd29 AND lcg_mod29 | tex `CICADA_SEEDS` ∪ pgf/randomtex default date-seeds (thin — reported) ∪ dense block | pair |
| A4 | sha256_ctr keytexts / string seeds | `plant.ks_sha256_ctr(seed=b)` | the **full** B04 seed dictionary (`seeds.build()`, ~2165 bytes-seeds) — small, swept in full | pair |
| A5 | non-zero offsets, Py2.7-MT | `gen_py27` random29, top-64 seedprior seeds | offsets o ∈ 1..16 for each of the top-64 prior seeds (1024 cells) | pair |
| A6 | free_drift / drift_at (continuous cousin) | `gen_py27` random29, seedprior slice | the 433 prior seeds ∪ dense block from w=0, decoded under the **drift** preset | drift |

Covered fraction of each generator's full seed space is reported per axis; for the
2^32 (bash/perl) and 2^31 (tex) spaces the swept prior-dense slice is a tiny
fraction and is stated as such — **partial coverage**, not closure.

## 4. Hit function (frozen — reuse `round20/HITFN/hitfn20`, per axis' preset)

`hitfn20.evaluate(HitDecode(C=C[:240], K, o=o, preset=PRESET,
n_round_adjudicated=N_ADJ))`. A HIT requires ALL THREE (unchanged):
1. `pmax` clears the panel-max null for **that axis' preset**:
   `panelmax20.panelmax_bar(preset=PRESET, n_round_adjudicated=N_ADJ, alpha=0.01)`.
   Reference bars @N=1e6: **pair = 7.384**, **drift = 13.842** (measured, this
   session). NEVER −5.5, NEVER another preset's bar.
2. rune-INDEX recovery ≥ 0.90 (real candidate: held-out self-consistency; plant:
   vs truth_idx). Score alone is never a hit.
3. held-out 3/4 recovery ≥ 0.90 under the same key.

## 5. Null, family-wise bar, FP ceiling per axis (frozen)

- **Null (R6):** seed-3301 order-matched wrong-key decodes under the SAME decoder
  used for that axis, on the SAME `C[:120]`: `random.Random(3301)` draws seeds
  (integers for A1/A2/A3/A5/A6; random B04-style byte strings for A4) NOT in that
  axis' prior slice, decoded under that axis' preset, pmax recorded. The FP ceiling
  is the count that clears `SCREEN_BAR` and then the full three-clause gate.
- **Family-wise bar:** the axis' panel-max bar at the ACTUAL Stage-B count
  (`panelmax_bar(preset, n_stage_b, 0.01)`), reported alongside the N=1e6 reference.
- **Expected FP over the screened slice:** `N_screened · P(wrong key clears the full
  three-clause gate)`, measured directly from that axis' seed-3301 null. Pre-reg
  expectation: **< 1** over each axis' swept slice.

## 6. Decision rule (frozen, per axis)

- **NULL** if 0 words clear the three-clause gate at the axis' claim bar AND the
  axis' seed-3301 null produces ≤ its expected FP → the L7-B axis is closed over
  that generator/offset/free_drift **slice** (partial coverage stated).
- **HIT-flagged-for-oracle** if any word clears the full gate. NEVER
  auto-certified (R21-L1 seal). R6 recomputes the FP ceiling under that axis'
  decoder and refutes-by-default before the flag stands.
- **UNVALIDATED** for any axis whose positive control did not reach ≥0.90 recovery
  where the beam fails — no null is claimed over it.
- **PARTIAL-COVERAGE** annotation is mandatory on every axis whose swept slice is a
  small fraction of its generator's full seed space (A1/A2/A3, and A6's dense tail).

## 7. Coverage × power (report both — doctrine R2, per axis)

- **coverage** = exact count of keys screened under the axis' decoder, as a fraction
  of that generator's full seed space.
- **power** = the axis' measured control recovery for its relation (≥0.90 target),
  vs the beam's recovery on the same plant. Both persisted in `control_ext.json`.

## 8. Decision-relevant question this lane answers

Does broadening skip_by_two beyond the Py2.7 offset-0 slice **reopen** ANY
beam-based negative — under bash/perl/tex/sha256-keytexts, non-zero offsets, or the
continuous free_drift cousin — or does `L7-B` close across those axes too (for the
swept, prior-dense slices)? Answer per axis with covered fraction, in RESULTS.md.
