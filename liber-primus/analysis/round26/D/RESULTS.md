# Round 26 — LANE D — RED TEAM (refute-by-default) — RESULTS

Date 2026-08-31. Ran LAST over lanes A/B/C. Verdict: **NO-ERROR-FOUND** (one minor
scope-hygiene defect in Lane A, non-fatal; no survivor, no unsound null, no FP inflation,
no silent re-run of an existing negative).

## 0. Survivors / hits to re-derive
Independently scanned every raw sweep row of all three lanes:
- A `sweep.jsonl` (now 5,034+ rows, still running): `clears_bar=0`, `hit=0`.
- B `sweep.jsonl` + `sweep_partial_off8.jsonl` (1,562 rows): `clears_null=0`, `hit=0`.
- C `rows.jsonl` (4,274 rows): `escalated=0`, `hit=0`, best screen −6.578.

**Zero survivors, zero flags across all three lanes.** `survivors_confirmed_real = []`.
No STOP-AND-ALERT. Nothing to re-derive because nothing cleared any bar.

## 1. Control soundness (a null from an unvalidated instrument does not count)
- **A**: `control.json` `all_controls_validated:true`, `control_min_recovery:1.0`. Controls
  plant each generator's OWN keystream (perl r29, tex pgf_rnd29, py27 grb5_mod w64), encipher
  held-out English under keyskip1, and hitfn20 returns HIT=True. Identical control pmax across
  the 3 families (24.90 for seed 3301) is EXPECTED, not a bug: recovery=1.0 means the same
  plaintext P is recovered, so the panel score is identical regardless of which keystream
  enciphered it. SOUND.
- **B**: `control.json` `control_passed:true`, keyskip1 & pair both min-recovery 1.0 on a real
  keytext running-key plant. SOUND. (Correctly flags heldout as non-discriminating for a rigid
  running key → panel-max is the operative gate.)
- **C**: `control.json` `all_pass:true`, min recovery 0.9917. **Independently reproduced from
  scratch**: correct key → recovery 1.000 / HIT=True / pmax 25.24; WRONG key (seed 9999) →
  recovery 0.054 / HIT=False / pmax 0.84. The control is genuinely DISCRIMINATING. SOUND.

All three nulls issue from ≥0.90-validated instruments → all three nulls COUNT.

## 2. Coverage × power, independently recomputed from raw rows
| lane | rows (raw) | clears | hits | best score | bar | agree? |
|---|---|---|---|---|---|---|
| A (interim) | 5,034+ | 0 | 0 | pmax 5.438 | 7.63/7.38 | YES |
| B | 1,562 | 0 | 0 | pmax 5.470 | 5.73 | YES |
| C | 4,274 | 0 | 0 | screen −6.578 | 5.0 (screen) | YES |

Every headline number reproduces from the raw ledger rows. B's per-page coverage
independently recomputed and matches its summary exactly (page 19=264/best 5.164, 23=199/5.470,
26=264/3.698, 28=264/3.884; off8 page19=528, page20=43; all 0 clears). C's 323 seeds × 7 gens ×
2 decoders = 4,274 rows confirmed. A's 8 Perl + 4 TeX + 3 py27 gens all present.

## 3. Silent re-run of an existing negative? — checked each anti-repeat proof
- **A / R19-G2 (Perl)**: ledger coverage "ZERO key-space coverage, swept no seeds." A releases
  the FIRST scored Perl seeds. CLEAN extension.
- **A / G4-TEX-RNG (TeX)**: ledger "ZERO decodes." A releases the FIRST scored TeX seeds. CLEAN.
- **A / R21-L3 (Py2.7)**: R21-L3 covered the i386 wordsize=32 init_by_array WORD space
  (45,975 prior words) at offset 0, keyskip1. A sweeps wordsize=64 (amd64 2-word), offsets
  {1,3,5,7,13}, and keyskip2 — all genuinely distinct (NC-2/NC-4 + new offsets). Verified
  directly: py27 w64 keystream != w32 for STRING seeds; for INT seeds w64 == w32.
  **MINOR DEFECT (see §6):** A's code still runs INT seeds at offset=0/preset=exact(keyskip1)
  — 228 such py27 rows — which for int seeds is byte-identical to a wordsize=32 run, contra
  A's PREREG promise to "skip wordsize=32/offset=0/keyskip1 for those three reducers." These
  are semantic-int seeds (int_motif/int_prime), NOT R21-L3's init_by_array P3b words, so they
  do NOT reproduce R21-L3's covered decodes — no existing negative was silently re-run — but
  the code does not honor the PREREG's stated exclusion. Non-fatal.
- **A / R25-COMPUTE-TAIL**: R25 parks the offset-0 wordsize-32-amd64-image random29 tail. A's
  PY27_MODES = {grb5_mod, grb5_rej, shuffle29} — random29 is NOT swept at all. No collision.
- **B / R12-C2**: ledger coverage "Texts fetched; the sweep was never run", not_covered=None.
  B runs exactly that never-run sweep. Distinct from R12-A1 (byte-reduction pads, not
  letters-only running keys). CLEAN — this is the first execution of a staged lane.
- **C / R16-PRNG, R16-KDF, R21-L3, R25, R11**: C's axis is corpus-semantic value AS SEED
  through the generator zoo (incl. the page-56 prime/totient ladder) — an enumerated 323-value
  set, not a 2^32 slice. Distinct from all cited ids. CLEAN.

## 4. Sieve × panel-max FP-inflation (the ~2.5e6-decode R20 hazard)? — NOT reintroduced
The R20 hazard was a FIXED score bar held constant while N grew, inflating false positives.
- **A** feeds `n_round_adjudicated=10^6` (fixed in advance, ≥ actual decode count ~5k) to the
  family-wise `panelmax20.panelmax_bar` (an extreme-value `_fw(N,…)` bar that SCALES UP with N).
  A larger-than-needed N → a CONSERVATIVE (higher) bar. Anti-FP direction. Bars 7.63/7.38.
- **B** sets `N_ADJ = total planned decodes (2,184)` while actually running 1,562 — again the
  bar is set for MORE decodes than were run → conservative. Bars ~5.73–5.92 per page, all
  N-scaled via `panelmax_bar`.
- **C** uses SCREEN_BAR=5.0 as a fixed TRIAGE gate on a fast L=120 beam score — NOT a
  certifier. The certifier is the full hitfn20 panel-max gate (N-scaled, N=4,522), reached only
  ABOVE the screen. Best screen was −6.578, so nothing escalated and the certifier never fired.
  No fixed bar was used to CERTIFY anything at large N. Anti-FP direction preserved.
No lane reintroduced the fixed-bar-at-large-N hazard.

## 5. "Closed"/"exhausted" claims are swept-FRACTION statements (doctrine R7)?
- **A**: reports 747/2^32 = 1.74e-7 per space, "flat tail NOT swept … NOT claimed closed."
  Swept-fraction, honest. (Caveat: A is INTERIM — see §6.)
- **B**: "45.4% of the off4 feasible plan", "3 of 9 pages COMPLETE", large pages "UN-SWEPT and
  go into not_covered", "reported as a bounded slice, never closed." Honest.
- **C**: "323/323 semantic seeds … = 100% of the enumerated semantic-seed space at offset 0;
  ≈0% of raw 2^32 (out of scope by design). Not closed." Honest.
No lane made a bare "closed"/"exhausted" claim; every one is an explicit swept fraction.

## 6. The one defect (minor, non-fatal)
**Lane A: PREREG↔code inconsistency + an INTERIM null presented with a full-plan coverage
figure.**
1. A's PREREG (lines 97-98) states it SKIPS wordsize=32/offset=0/keyskip1 for the three
   reducers to avoid R21-L3 overlap. The code (`sweep.py` L261-268) runs ALL seeds at
   wordsize=64 including offset=0 + preset='exact'(keyskip1); for INT seeds w64≡w32, so 228
   py27 rows re-tread the offset0/keyskip1/exact cell the PREREG promised to skip. Because the
   seeds are semantic ints (not R21-L3's init_by_array words), no existing NEGATIVE is actually
   reproduced — but the code does not implement its own stated exclusion. FIX: guard
   `if not (mode in reducers and off==0 and preset=='exact' and isinstance(seed,int)): emit`.
2. A's sweep was **still running at report time** (control.json `decodes_run/best_pmax_row/
   n_clears_bar/hits` are all `null` — the finalize block never executed; sweep.jsonl grew from
   1,794 → 5,034 rows during this audit). A's coverage headline (747 seeds, 49,302 planned
   decodes, 1.74e-7) is the PLAN; the actual scored slice is a subset. A discloses this
   honestly ("interim — sweep in progress", "~1,794 scored at report time"), so it is not a
   dishonest claim — but the delivered null is PARTIAL, and the ledger row should be read as
   interim until control.json finalizes. The 0-clears result holds across all 5,034 rows so far.

Neither item changes any verdict: no survivor, no unsound null, no FP inflation, no
silently-re-run negative. Both are scope-hygiene notes, logged so the coordinator does not
read A's coverage figure as a completed sweep.

## Bottom line
NO-ERROR-FOUND. All three lanes: control-validated instrument (≥0.90 recovery, C
independently reproduced), N-scaled family-wise bars (no FP inflation), explicit swept
fractions (no false "closed"), clean anti-repeat extensions (no silently-re-run negative),
zero survivors, zero oracle flags, zero hits. Lane A carries a minor code-vs-PREREG scope
inconsistency and an interim (still-running) null; both disclosed, neither fatal.
