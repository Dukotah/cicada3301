# Round 40 — THE MASS THE CEILING PAGE NAMES (pre-registration / plan of record)

_Drafted 2026-10-31 as Round 39 closed. Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seeded
by [`../../MEASURED-CEILING.md`](../../MEASURED-CEILING.md) §3 "what is NOT excluded" and Round 39 X1's list. Each lane's
`PREREG.md` is authoritative once written and is dated before its first output; addenda in a separate dated file._

## 0. Thesis — the position statement is a to-do list

`MEASURED-CEILING.md` now states, with every claim checked against a measured ledger row, what the panel-R36
instrument generation excludes. Its §3 is therefore the most honest ranking of remaining work the repo has ever had,
and three of its items are **enumerable, cheap under the current instrument, and never swept**:

1. **The other bash versions' auto-seed orbits.** Only bash 4.2 was swept (three times, at reach ≥0.95 ×12). bash
   3.2, 4.0 and 4.1 share the LCG but differ in the auto-seed formula and `$RANDOM` post-processing; bash 5.1+
   replaced the generator outright. Each orbit is ~77.6 M seeds ≈ 25 min under pf_v4_12 on this laptop. The toolchain
   prior (Ubuntu 11.04–12.04, R18-L1) makes 4.1/4.2 the likeliest and 5.x the least.
2. **Non-zero key offsets.** Every orbit sweep decoded at C[0] with key offset 0. An offset into the keystream is a
   one-parameter extension; 28 offsets × the 4.2 orbit is ~12 h, so a stated-fraction lane (prior-weighted offsets
   first: 1, 2, 3, and the sign flip) is the honest unit.
3. **The Py2.7-MT `exact` remainder and the PHP uniform tier** — on the sandbox, now that its quota has reset, with
   the fixed session protocol and S2's window-2 state recovered before its snapshot expires (~2026-11-07).

Plus the re-score the matrix still owes: 46 clue-reading cells measured only English-only or legacy-beam, each with
stored artefacts, re-scorable under panel-R36 at C3-R37's cost.

**Not a target:** new generator families beyond bash versions; the 34 no-operation clue cells; V2 geometry (recorded
unmeasurable); the seal (paused).

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| **≈45%** | enumerable mass — bash versions on the laptop, S2 + PHP on the sandbox | B1, S1, S2 |
| **≈25%** | the offset extension (stated fraction) | B2 |
| **≈15%** | the 46 English-only/legacy matrix cells under panel-R36 | C1 |
| **≈15%** | red-team + closeout | X1 |

## 2. Lane roster

| ID | Type | Title | Compute | Gates on |
|---|---|---|---|---|
| **S1** | sandbox (first, after reset) | Recover S2 window 2 from `snap_ff0SWU76EW32OqbWJvp00fnORypR`; export lists; ≥2 persistent-session windows; coverage per instrument | sandbox | 2026-11-01 00:00 UTC |
| **S2** | sandbox | PHP tier retry with `round38/S2-php-sandbox/run_commands.sh`: control + FPR persisted and downloaded FIRST; 3301 blocks 318+ then the 3302 stream; rows downloaded after each window | sandbox | S1's first session done |
| **B1** | bounded (laptop flagship) | bash 3.2 / 4.0 / 4.1 / 5.1 `$RANDOM` auto-seed orbits under pf_v4_12 + beam_v3 + panel-R36, with each version's exact generator and auto-seed formula verified against a reference (bash source or a built binary on the sandbox if available) | ~25 min per version | — |
| **B2** | bounded, stated fraction | bash 4.2 orbit at key offsets {1, 2, 3, 28} and sign +1 (prior-weighted), each a full orbit under pf_v4_12 + v3; remaining offsets deferred with their fraction stated | ~25 min per offset | B1 (shares harness) |
| **C1** | re-score | the 46 TRIED-EN / TRIED-LEG matrix cells (`round38/X1-redteam/o4_recount_r38.json`) under panel-R36 + beam_v3, controls first, as C3-R37 | ~1–2 h laptop | — |
| **I1** | instrument | Re-plant LATIN, GREEK, EN_NOVOWEL and HEBREW in the 14 control harnesses whose exclusions rest on EN_MODERN-only plants (Round 39 X1 list; the `[plants: …]` tags on `MEASURED-CEILING.md`), measure recovery and panel power, refresh the page tags | light (minutes each) | — |
| **B3** | bounded re-run | the English-era SHA-256-CTR / PBKDF2 / public-pad / CicadaOS-pad grids re-decoded with beam_v3 keyskip1+keyskip2 (the legacy beam recovered 0.258 of a skip_by_two plant) on panel-R36, stored seed lists only, bars from null12 | ~1 h laptop | B1 (CPU) |
| **X1** | red-team | this round; I1's re-plants and B3's grids; B1's generator verification; B2's offset arithmetic; the ceiling page refreshed by each lane's result (`check_ceiling.py` must stay green); Round 41 critic | light | last |

## 3. Lanes in detail

All laptop decode lanes: `beam_v3` panel_max on panel-R36 (`data/panels/panel-r36.npz`), keyskip1 + keyskip2,
pf_v4_12 at its frozen point (`round37/I2-pfv4-12reg/frozen_op12.json`), bars from `round36/B1-orbit-12reg/null12.json`
at actual N and N=1e6 (L=120 screen, L=240 gate), 12-wide SWEEPROW rows with the optional `degenerate` flag ON
(`with_degenerate=True` — Round 39 T1), natural-rate planted controls through the real chunk path (skip split
reported) before any null counts, stores gitignored, PREREG before the first output, no `git`.

---

### B1 — The other bash versions  _(laptop flagship; enumerable)_

- **Q1 (recognizer).** For each version: implement `$RANDOM` exactly as that version's `variables.c`/`lib/sh/random.c`
  does (3.2: the same 16807 LCC with the bash-3 seeding; 4.0/4.1: the 4.x reseed and `brand()` post-processing
  differences, if any — read the source, state the diff from 4.2; 5.1+: the new 32-bit generator `genrand32`/xoshiro
  per bash 5.1 `lib/sh/random.c`) and the auto-seed formula (`sbrand(tv_sec ^ tv_usec ^ pid)` in 4.x; check 3.2 and
  5.x). Verify against a reference: known `$RANDOM` sequences for `RANDOM=1` from each version (search the bash
  source test suite / changelog; if the sandbox is available, build each bash and print the first 20 values; else
  mark the version "source-derived, unverified" in the row). Natural-rate control per version × relation (≥10
  EN_MODERN + ≥10 EN_NOVOWEL + ≥10 HEBREW) through the real chunk path, ≥3 recoveries per skip split.
- **Q2 (prior).** R18-L1 §6: the toolchain box is Ubuntu 11.04–12.04 (bash 4.1/4.2); 3.2 and 4.0 are period-plausible
  (macOS/older Debian); 5.x post-dates 2014 and is a completeness ritual — queue it last and label it.
- **Q3 (bounded).** Four orbits × 77,594,624 seeds (LP64 only; ILP32 only if the version's generator differs by ABI —
  state it) ≈ 25 min each under pf_v4_12; cap 2 h; run 4.1 → 4.0 → 3.2 → 5.1.
- **Q4.** key space = each version's auto-seed orbit, `%29`, offset 0, sign −1; transition model = keyskip1 + keyskip2
  (≤2 skips in the head); register = panel-R36 with pf_v4_12's measured power stated.
- **Q5.** A version whose generator cannot be verified against any reference is run but filed `partially-run` with
  "generator source-derived, unverified"; a failed control stops that version.
- **Deliverable.** `round40/B1-bash-versions/` — `generators.py` (with the source citations per version),
  `verification.json`, per-version `control.json`, `sweep_rows.jsonl`, `sweep_summary.json`, `RESULTS.md` (per version:
  seeds, fraction, survivors, best vs bars, flagged/near-miss, reach per register), `ledger.json` (one row per
  version), `ledger_patches.json` (MEASURED-CEILING "other bash versions" line → measured; `check_ceiling.py` pins).

---

### B2 — Key offsets on the bash 4.2 orbit  _(stated fraction)_

- **Q1.** Planted controls with the key stream offset by k (and sign +1) through the real chunk path; the screen is
  aligned at C[0] so the head statistic must be computed on the offset-aligned keystream — verify the control
  recovers before any orbit runs.
- **Q2.** Every orbit sweep so far decoded at offset 0 / sign −1 only (`MEASURED-CEILING.md` §3). A keystream offset is
  the single most common implementation variant (discarding the first draws) and costs one parameter.
- **Q3.** Prior-weighted order: sign +1 at offset 0; then offsets 1, 2, 3; then 28 (one full period of the reduction)
  — five full orbits ≈ 2 h; the remaining 24 offsets deferred with their fraction (5/29 of the offset axis) stated.
- **Q5.** Control fails for any offset → fix the alignment; no coverage claim.
- **Deliverable.** `round40/B2-offsets/` — `sweep.py`, per-offset `control.json`, `sweep_rows.jsonl`, `RESULTS.md`,
  `ledger.json`, `ledger_patches.json` (R35-B1/R37-I2 extension: offsets covered).

---

### S1 / S2 — sandbox lanes  _(after 2026-11-01 00:00 UTC; as specified in Round 39 §3 S1/S2, verbatim)_

S1: recover window 2 (STATUS, HIT-CANDIDATE, top list, histogram; chunked downloads), report seeds advanced /
fraction / crossers / near-misses, then ≥2 `persistent:true` windows with ONE blocking call each, state downloaded
after every window; coverage per instrument. S2: control + FPR persisted and downloaded before the first window;
then blocks 318+ of the 3301 stream and the 3302 stream in ≤40-min windows; rows downloaded after each. Both: stop
non-persistent; nothing counted that is not on the laptop.

---

### C1 — The 46 English-only / legacy cells  _(re-score)_

As C3-R37: for each cell, the original artefact (stored stream / top-N / regenerated candidates — say which), the
original planted control re-run under panel-R36 + beam_v3 (+ pf_v4_12 where heads are screened), then the re-score
with bars from `null12.json` (keyskip) or the key-matched null (`benchmark/bars_keymatched.py`) where the key is
ciphertext-derived; `degenerate` flag on; any clearer → L=240 → oracle bundle. Deliverable
`round40/C1-rescore-46/` with per-cell outcomes, `RESULTS.md`, `ledger.json`, `ledger_patches.json` (matrix cells →
TRIED).

---

### X1 — Red-team  _(last)_

Targets: B1's per-version generator verification (re-derive 20 `$RANDOM` values per version from the cited source
logic yourself); B2's offset alignment in the screen; S1's recovery arithmetic and that windows were counted only from
downloaded state; S2's persisted-first protocol; C1's controls; `check_ceiling.py` green after every refresh; ledger;
gate; Round 41 critic.

## 4. Verification and hit protocol
As Rounds 32–39 with `HUMAN-ORACLE.md`.

## 5. Recorded, not blocking
- Snapshots expiring ~11-06/07 (S1 reads them first); then delete the stopped sandboxes and old snapshots.
- The `round29/L4-image-forensics/fingerprints.json` stray file.

## 6. Orchestration
- **Wave A (laptop, now):** B1 (one process), C1 (one process), I1 (light) — two heavy laptop processes maximum.
- **Wave A″:** B3 after B1 or C1 frees a slot.
- **Wave A′ (sandbox, at 17:00 PDT 2026-10-31):** S1, then S2.
- **Wave B:** B2 after B1 (shares the harness).
- **Wave C:** X1; coordinator closeout (SYNTHESIS, ledger, nav docs, `check_ceiling.py`, gate, commit to master, push).
Discipline unchanged: Sonnet; no `git` in lanes; own `round40/<lane>/` dir; nproc=1; append-mode streams; stores
gitignored; no `find /`; PREREG dated before first output; RAM check before heavy runs; no blocking on sleeping timers.

## 7. Guardrails — do NOT re-run
Everything in Rounds 32–39 §6/§7; the bash 4.2 orbit at offset 0 / sign −1 (three negatives); the semantic readings
(address and similarity); V2 geometry.

## 8. Definition of a good Round 40
The ceiling page's "other bash versions" and "non-zero offsets" lines become measured rows; S2 window 2 is recovered
and S2 advances under persistent sessions; the PHP tier has persisted rows; the matrix carries no English-only or
legacy-beam cell. A survivor would be extraordinary; the round succeeds without one.
