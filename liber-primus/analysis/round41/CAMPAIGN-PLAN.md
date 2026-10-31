# Round 41 — THE BAR OF RECORD (pre-registration / plan of record)

_Drafted 2026-10-31 as Round 40 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded by
Round 40 X1's instrument finding and critic list. Each lane's `PREREG.md` is authoritative once written and is dated
before its first output; addenda in a separate dated file._

## 0. Thesis — fix the bar before claiming anything else against it

Round 40 X1 found that `null12` — the twelve-register null every sweep since Round 36 has quoted its actual-N bar
from — was fitted on a wrong-key survivor population less English-like than the survivors real sweeps produce
(median pmax 2.33 vs ≈2.8 across 131,786 real rows). At N≈130k the empirical 99 % bar is ≈9.6 against the stored 8.3.
No stored verdict flips (every best row sits ≥1 below even the lenient bar), but a bar that is lenient at scale is the
Round 19 I3 defect in a new coat, and the doctrine's R2 says a negative with an unmeasured bar is not a negative. The
N=1e6 bar is the only flag gate until the refit lands; the refit is this round's flagship, and it includes page- and
region-scale matched nulls for the direct (non-key) families, since X1 showed the R13 near-miss's p moved from 0.004
to 0.070 depending on the null's structure scale.

The rest is mass with a known harness: S2 window 2 recovery (deadline ~2026-11-07) and persistent windows; the PHP
retry; a real bash 3.2 binary on the sandbox to retire the only source-derived generator; the R14/R15 cells whose
code turned up in the branch archive; and B2 (key offsets), still sweeping as Round 40 closed, to be filed and
audited here.

**Not a target:** new generator families; the 5.1 PIE orbit (~2³¹, ~12 h) unless the sandbox has idle time; dense pad
offsets; the seal; V2 geometry.

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈35%** | instrument — the refit null and matched nulls; the bash 3.2 binary | I1, S3 |
| **≈40%** | enumerable mass on the sandbox — S2 windows, PHP | S1, S2 |
| **≈10%** | the unblocked matrix cells | C1 |
| **≈15%** | B2 audit + red-team + closeout | X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **I1** | instrument (flagship) | Refit `null12` on the real sweep survivor population (wrong-key heads that PASS pf_v4_12, decoded by v3 — the population the bars are applied to), ≥40,000 draws at L=120 and ≥5,000 at L=240 per relation; Gumbel + empirical bars at N=1e5/1e6; re-judge every Round 36–40 best row against the refit bar; page-/region-scale matched nulls for the direct families (R13-style walks, acrostics, streams) as a standing function | medium (laptop) | — |
| **S1** | sandbox (first) | S2 window 2 recovery from `snap_ff0SWU76EW32OqbWJvp00fnORypR`; export lists; ≥2 persistent-session windows | sandbox | 2026-11-01 00:00 UTC |
| **S2** | sandbox | PHP tier retry (persist control + FPR first; blocks 318+; the 3302 stream) | sandbox | S1's first session |
| **S3** | sandbox (cheap) | Build bash 3.2.57 from the GNU tarball; print `RANDOM=1` ×20 and the auto-seed path; compare to `round40/B1-bash-versions/verification.json`; upgrade the 3.2 row from partially-run if it matches | sandbox, ~10 min | any S session |
| **C1** | re-score | R14/R15 (campaign7) from `archive/branches-2026/.../campaign7/` + `corpus/H-branch-recovery/`, plus the other five blocked cells' claims verified | light | — |
| **B2** | filed from Round 40 | key offsets on the 4.2 orbit — audit the offset alignment (control enciphered with the offset; screen fed the advanced keystream) before any row merges | — | B2 lands |
| **X1** | red-team | the refit (is the population definition circular? is the Gumbel fit still conservative?); B2's alignment; S1 counted only from downloaded state; S3's build; C1; Round 42 critic | light | last |

## 3. Lanes in detail

---

### I1 — The refit  _(flagship instrument lane)_

- **Q1 (recognizer).** Planted correct keys (20 per register × 12 registers, L=120 and L=240, keyskip1 + keyskip2)
  through the real chunk path must clear the refit bar at N=1e6 in ≥19/20; and the refit bar at N≈131,786 must sit at
  or above the empirical 99 % of the pooled real-sweep survivor maxima X1 measured (≈9.6) — if it does not, the
  population definition is wrong, not the data.
- **Q2 (prior).** `round40/X1-redteam/RESULTS.md` ("B3 bars" + `rerun_bars.json`, `rerun_r37_calibration.json`): median
  2.33 vs ≈2.8; q99 4.06 vs ≈4.7; empirical 99 % bar ≈9.6 at N≈131k vs 8.3 stored.
- **Q3 (bounded).** Null population = wrong-key seeds drawn uniformly from the six generator families, passed through
  pf_v4_12 (so the null is the SURVIVOR population, as the sweeps are), decoded by v3 on panel-R36; ≥40,000 at L=120,
  ≥5,000 at L=240, both relations; cost ≈ the survivors' decode cost (~100/s) → ~15 min per relation at L=120. Also
  record, per draw, which generator it came from, so a per-family bar can be checked for heterogeneity.
- **Q4.** N/A; the deliverable is `bars_v3`'s `family="survivor12"` (and `bar_keymatched` unchanged).
- **Q5.** If the survivor-population Gumbel exponent or tail shape disagrees with the empirical maxima by >2 SE at
  N≈131k, use the empirical quantile as the bar of record and say so.
- **Matched nulls for direct families.** A standing `bars_matched.py` with `page_scale` / `region_scale` shuffles
  (X1's recipe: shuffle within blocks of 100 / 250 / 1,000 runes keeping interrupters), applied to the R13 walk as the
  fixture (family p 0.004 / 0.018 / 0.070 reproduced).
- **Deliverable.** `round41/I1-null-refit/` — `null_survivor12.json`, `fit.json`, patches to `bars_v3.py` (+ doctest),
  `benchmark/bars_matched.py` (+ test), `rejudged_rounds36_40.json` (every best row vs the refit bar), `control.json`,
  `RESULTS.md`, `ledger.json`, `ledger_patches.json` (`R36-B1`, `R37-I2`, `R40-B1/B3/C1`, `null12`-citing rows:
  bar-of-record note), and the `MEASURED-CEILING.md` §1 calibration caveat replaced by the refit statement (pins).

---

### S1 / S2 / S3 — sandbox lanes  _(after 2026-11-01 00:00 UTC)_

S1 and S2 exactly as Round 40 §3 (which carries Round 39's text verbatim): persistent sessions, ONE blocking call in
flight, state downloaded after every window, nothing counted that is not on the laptop; S1 first (the deadline), S2
second. S3: `wget` bash-3.2.57.tar.gz from ftp.gnu.org (record sha), `./configure && make`, run `RANDOM=1; for i in
1..20; do echo $RANDOM; done` and the auto-seed path (`$RANDOM` in a fresh shell with known pid/time if controllable
via `faketime`/`unshare`, else just the seeded sequence), save `bash32_reference.json`, compare to
`round40/B1-bash-versions/verification.json`; 3.2's row → `negative` on match, else record the divergence and keep
`partially-run`.

---

### C1 — R14/R15 and the blocked cells  _(re-score)_

Locate the campaign7 code X1 found (`archive/branches-2026/.../campaign7/`, `corpus/H-branch-recovery/`); if it runs
from the archive, regenerate the R14/R15 candidate sets, control, re-score under panel-R36 with the I1 bars (or the
N=1e6 bar if I1 is not yet done — say which); for the other five blocked cells (R31 sub-32-rune readouts; R35 texts;
R36 dated pads; R44 book texts; the 43 B1 keys) verify the artefact really is absent (not merely elsewhere, as
R14/R15 were) and record each with a precise `not_covered`. Deliverable `round41/C1-r14-r15/`.

---

### X1 — Red-team  _(last)_

Targets: I1's population definition (not circular: the null must not be conditioned on the real ciphertext's
survivors), the refit fit vs empirical, the re-judged rows; B2's offset alignment (re-plant two offsets yourself);
S1's recovery and counting; S3's build log; C1; ledger patches; `check_ceiling.py`; gate; Round 42 critic.

## 4. Verification and hit protocol
As before with `HUMAN-ORACLE.md`; until I1 lands, a flag requires the N=1e6 bar.

## 5. Recorded, not blocking
- Snapshots: `snap_fWma12lA…` (~11-06), `snap_3uGXrds5…`, `snap_ff0SWU76…` (~11-07).
- The KDF bundle (`round40/B3-english-era-grids/ORACLE-KDF-…`) remains for the owner to overrule.
- The `round29/L4-image-forensics/fingerprints.json` stray file.

## 6. Orchestration
- **Wave A (laptop, now):** I1 (one heavy process; B2 from Round 40 is the other).
- **Wave A′ (sandbox, 17:00 PDT):** S1 → S3 (cheap, same session) → S2.
- **Wave B:** C1 when a laptop slot frees; B2 filed when it lands.
- **Wave C:** X1; coordinator closeout.
Discipline unchanged.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–40 §6/§7.

## 8. Definition of a good Round 41
The bar every sweep quotes is fitted on the population it is applied to, and every Round 36–40 best row is re-judged
against it; S2 window 2 is recovered and S2 advances; the PHP tier has persisted rows; the last source-derived
generator is verified against a real binary; the matrix has no cell blocked by an artefact that actually exists.
A survivor would be extraordinary; the round succeeds without one.
