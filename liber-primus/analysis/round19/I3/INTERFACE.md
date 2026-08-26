# I3 — INTERFACE

_What I3 requires from I1 (`round19/I1/driftbeam.py`) and I2 (`round19/I2/adjudicate.py`),
and what I3 hands back to Phase 2. Written against the state of those two files at
2026-08-26 11:37 (I1) / 11:15 (I2); every requirement is checkable mechanically._

A threshold is a property of a **triple**, not of a score:

```
bar = f( null generator , decoder transition relation , adjudicator statistic )
```

Round 18 L7-C.3 is the whole reason this file exists: R17 quoted `threshold_for(N)` with an
`N` taken from a different stage of its own pipeline, and the 12-Gumbel-SD mismatch sat
unremarked in its own result file. The interface below is designed so that mistake cannot be
made silently — `nullcurve19.threshold_for` **raises** rather than substituting a bar from a
cell it was not calibrated on.

---

## 1. What I3 needs from I1 — `driftbeam.py`

### R-I1-1 — the reported `score` must stay unpenalised and on the canonical scale
**Status: SATISFIED.** `beam_decode` already returns `score` = the unpenalised
`Quadgram.score_norm` of the path the penalised search chose, with `beam_score` separate.
Every bar in `calib19.json` is calibrated on `score`. If a future edit makes `score` the
penalised quantity, **every EN cell in `calib19.json` is void** and must be re-run.

### R-I1-2 — a preset is a frozen, named, fingerprinted object
A bar is conditional on the **whole** parameter tuple
`(mode, max_skip, max_free, lam, lam_explained, start_slack, beam_w, sign)`, not on the mode
name. `PRESETS["drift"] = dict(mode="permissive", max_skip=40, max_free=2, lam=8.0,
start_slack=2)` is what I3 calibrated; a later change to `lam` or `max_free` changes the null
maximum and invalidates the cell.

**Required:** expose

```python
driftbeam.preset_fingerprint(name) -> str      # stable hash of the full kwargs dict
```

and have Phase 2 write it into every `SWEEPROW` header. `nullcurve19` stores the fingerprint
in each cell and refuses a mismatch. Until this exists, I3 stores the literal kwargs dict in
`calib19.json` (`preset_kw`) and Phase 2 must compare it by hand.

### R-I1-3 — `n_unexplained` per decode
**Status: SATISFIED.** I3 uses the mean realised count of unexplained advances as the
*empirical* permissiveness covariate; it is the x-axis of the dose–response curve in
`RESULTS.md` §3 and it is what tells Phase 2 what permissiveness it can afford.

### R-I1-4 — Phase 2 must pass the number of decodes ADJUDICATED, not enumerated
The `drift` preset runs at **1.39 decodes/s** at L = 120 on one core (measured here). That is
the binding constraint on Phase 2's N, and N is what sets the bar. A lane that enumerates
10⁹ keys but beam-decodes 10⁵ of them must call `threshold_for(n_trials=1e5, ...)`. This is
L7-C.3's error and it is the single easiest way to re-commit it.

### R-I1-5 — do not change `keyskip1`
I3 independently re-verified I1's own G-EQ claim (`out_geq.json`): `driftbeam(keyskip1)`,
`skipdecode.beam_decode` and this lane's vectorised engine agree to ≤ 1e-9. That identity is
what licenses I3 to calibrate the `exact` preset with a fast engine at M = 10⁶ instead of
M = 10⁴. If it breaks, the large-M EN cells lose their licence.

---

## 2. What I3 needs from I2 — `adjudicate.py`

### R-I2-1 — `adjudicate_batch` stays vectorised over equal-length decodes
**Status: SATISFIED.** I3 calibrates 10⁶ panel decodes per cell through it. A per-row Python
path would make the panel cells PROVISIONAL at ~10⁴.

### R-I2-2 — **the panel z is standardised against the wrong null. Do not derive a bar from it.**
This is the substantive finding of this section and it is a **false-positive** risk.

`Panel.cal(n)` returns `mu`, `sd` fitted on a **uniform-random-rune** null, and
`z = (s - mu)/sd`. Two separate problems:

1. **Wrong population.** The object being adjudicated is not a random rune string, it is the
   *argmax of an English-driven beam search* over a wrong key. I2's own `null.log` records
   the gap at L = 120: random-rune `pmax` max **1.163** over 200,000 draws vs wrong-key beam
   `pmax` max **1.672** over 8,000. Under I1's `drift` preset the gap is far larger — a
   single wrong-key decode on random ciphertext measured here reached **pmax = 6.07**.
2. **Bulk vs tail.** `sd` is a bulk dispersion. `benchmark/null.py`'s own calibration note is
   that for this family the bulk sd overestimates the tail scale by ~2.5×, and this lane
   re-measures that ratio on every cell (`bulk_sd_beta / beta`). A `z` built on a bulk sd is
   not on a scale where "z = 4" corresponds to any particular error rate.

**Required, in order of preference:**

- **(a) Keep `z` exactly as it is, as a reporting scale, and take every bar from
  `calib19.json`.** This is I3's recommendation. It keeps `z` comparable across decoder
  presets (a decoder-output-standardised `z` would be mode-dependent and would silently
  change meaning between presets), and it puts the error-rate claim in one place.
- (b) If I2 prefers to re-standardise on a decoder-output null, then `mu`/`sd` become
  functions of `(mode, preset, L)` and **every** panel cell in `calib19.json` must be re-run
  against the new `panel.npz`. Say so before Phase 2 starts, not after.

Either way: **`adjudicate.py` must not publish a fixed `pmax` bar**, and `SWEEPROW.md` must
not describe `z` as "sigmas".

### R-I2-3 — `rho` for `pcon` comes from the same wrong null
`pcon` whitens the English correlation using `rho` from the random-rune null. The correlation
between registers *in decoder output* is not the correlation in random runes — L7-A.4 showed
English-correlated registers light up by selection alone precisely because the candidate is
an English argmax. I3 calibrates `pcon`'s null directly, so the bar is right; but the
*whitening* is imperfect, which costs `pcon` power rather than error control. Reported as a
finding, not a blocker.

### R-I2-4 — the panel is a frozen object
The register list, its order, the LM construction, the smoothing `alpha`, the length grid and
`SCHEMA_VERSION` all enter the null. **Required:** a `panel_fingerprint` written into
`models/panel.npz` and into the `SWEEPROW` header, checked against the one stored in each
`calib19.json` panel cell. A rebuilt `panel.npz` with a different corpus is a different
statistic with a different null.

### R-I2-5 — adjudicate at a calibrated length
I3's cells exist at **L ∈ {31, 120, 240}**. `Panel.cal` silently clamps outside its own grid;
`nullcurve19.threshold_for` will interpolate by the measured β ∝ 1/√L law **only** when the
caller passes `strict=False`, and it labels the result `interpolated_from`. Phase 2 should
adjudicate at one of the three calibrated lengths, or ask I3 for the cell.

### R-I2-6 — persist `preg` / `pcreg`
**Status: SATISFIED** (`SWEEPROW` carries both). I3 needs the argmax register for the
register attribution of any escalation, and for the R1 red-team's register-shopping check.

---

## 3. What I3 hands to Phase 2

```python
import sys; sys.path.insert(0, "liber-primus/analysis/round19/I3")
from nullcurve19 import threshold_for, threshold_contract, report

# the legacy statistic, unchanged, bit-identical to benchmark/null.py
threshold_for(n_trials)                                  # -5.5 floor binds below N*=3.13e8
threshold_for(n_trials, segment_len)                     # segment_len still ignored (legacy)

# the Round-19 instrument
threshold_contract(n_trials=..., segment_len=120,
                   register="I19:driftbeam.drift+I2", statistic="pmax")
```

`threshold_contract` returns **both tiers** (ESCALATE α = 0.05 per lane, CLAIM α = 0.01
round-wide), the cell it used, that cell's `M`, its `CALIBRATED`/`PROVISIONAL` status, and an
`extrapolated` flag that is true whenever `n_trials > M/50`. Store the whole dict in the
sweep's header. A number without its cell is not a threshold.

---

## 4. Coordination status and the re-run needed to finalise

| item | state |
|---|---|
| I1 `driftbeam.py` present | **yes** — calibrated directly, presets `exact`, `exact_ms8`, `pair`, `drift` |
| I2 `adjudicate.py` + `models/panel.npz` present | **yes** — calibrated directly via `adjudicate_batch` |
| I1 preset fingerprints | **absent** — cells store the literal kwargs instead (R-I1-2) |
| I2 panel fingerprint | **absent** — cells store the register list + `SCHEMA_VERSION` instead (R-I2-4) |

**Re-run required to finalise, and only these:**

1. If any `PRESETS` entry's kwargs change → re-run `run_i1i2.py --stage i1 --preset <name>`
   for that preset (all lengths). Cost: `drift` at M = 2×10⁴ is ~40 min on 6 cores.
2. If `models/panel.npz` is rebuilt → re-run `run_i1i2.py --stage i2panel` for L ∈ {31,120,240}
   **and** every `--stage i1` preset, because `pmax`/`pcon` are panel-dependent. Cost ~1 h.
3. If `driftbeam.beam_decode` starts returning a penalised `score` → every EN cell is void.
4. If Phase 2 needs a segment length outside {31, 120, 240} → one new `--stage i2panel` run
   at that length (M = 10⁶ costs ~17 min at L = 120, scaling roughly as L²).

Nothing else in this lane depends on I1 or I2 finishing.
