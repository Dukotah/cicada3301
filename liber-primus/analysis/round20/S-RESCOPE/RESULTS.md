# S-RESCOPE — RESULTS: re-adjudicated B-04 survivors through the fixed hit function

_Run 2026-08-28. Trust anchor `tests/validate.py` PASSES before and after. No git commit._

## Verdict: NEGATIVE (instrument validated), with one RED-TEAM FOUND-ERROR carried forward

Re-adjudicating the Round-13 B-04 stored survivors through the **repaired** Round-20 instrument
(I1 driftbeam keyskip1 `exact` + repaired `drift_rec` channel → I2 nine-register panel → P3
panel-max null → HITFN recovery-gated `is_hit`) produced **zero hits and zero panel-max-null
clearances in any register**. The positive control PASSED (a planted B-04-generator key recovers
rank-1 and fires `is_hit`), so this is a validated negative, not unvalidated silence.

**This is NOT new key space** and is a legitimate not-a-re-run (R1 (c) NO-ERROR-FOUND): the
original B-04 scored these keys with a rigid decoder + English-only argmax + an invalid −5.5 bar =
ZERO power. R1 D-iii's own `reopens_if` names this re-adjudication as the reopener.

## Positive control — PASS (gates everything; `out_poscontrol.json`)

Planted a real B-04 generator key (`sha256_ctr` + `mod29`, seed `CICADA`) over real English
plaintext via the `keyskip` relation the instrument targets, dropped it into the survivor pile:

| quantity | value |
|---|---:|
| plant pmax (exact preset) | **29.87** |
| panel-max bar (exact, N=1e6) | 7.634 |
| true rune-index recovery | **1.000** |
| held-out recovery (real mode) | 1.000 |
| `is_hit` strict / real | **True / True** |
| rank among wrong survivor keys | **rank 1** (0 of 55 wrong keys beat its pmax) |
| argmax register | LP1_REAL |

The instrument recovers a key from this exact generator family rank-1 through the full pipeline.
The null below is therefore trustworthy.

## Negative control — the hallucination is rejected in strict mode

An EN_NOVOWEL decode that clears the panel-max bar on pmax (19.11 ≥ 7.634) but recovers only
**0.746** of rune indices is **rejected** by `is_hit` in strict mode (recovery 0.746 < 0.90) — the
score/recovery decoupling R1 A-iv named. The gate does not certify it.

## The re-adjudication — NEGATIVE (`out_survivors.jsonl`, `out_rescope.json`)

250 stored survivor keys (Stage A/B/C top-50 each = 150, + Stage-D deepenings = 100), each
re-decoded under BOTH relations (keyskip1 `exact` + `drift_rec`) = **487 adjudications** (13 exact
decodes hit offset/length edge cases and were skipped; all 250 drift decodes ran).

| relation | n | max pmax | panel-max bar (N=1e6) | gap to bar | clears null | is_hit |
|---|---:|---:|---:|---:|---:|---:|
| keyskip1 `exact` | 237 | **4.759** | 7.634 | −2.88 | **0** | **0** |
| `drift_rec` | 250 | **7.986** | 13.842 | −5.86 | **0** | **0** |

- **`n_is_hit` = 0. `n_clears_null_total` = 0.** No survivor clears the panel-max null in ANY of the
  9 registers under either relation.
- Best survivor overall: `sha1_chain`+`mod29`, atbash, drift preset, pmax 7.986 vs bar 13.842 —
  argmax register EN_MODERN, but 5.86 below its bar. The best English-argmax of a 6.2M-decode sweep
  re-scored under the correct instrument does not come close to the calibrated bar.

### clears-null by register (clears / total adjudications)

Every register is 0/total: CY 0/39, DE 0/16, EN_HALFVOWEL 0/39, EN_KJV 0/83, EN_MODERN 0/121,
EN_NOVOWEL 0/6, LATIN 0/25, LP1_REAL 0/62, OE 0/96. **Power to detect a real key here is
established by the positive control (rank-1, pmax 29.87); the survivors carry none of that signal.**

## payload_resolved re-seed — NEGATIVE (`out_rescope.json:payload_resolved_reseed`)

Re-seeded the B-04 slice from `round19/C1/payload_resolved.bin` (the resolved canon, 3 changed
bytes idx 45/50/246, sha256 `3b9b07d9…`). 96 adjudications (4 gens × 2 reds × 2 signs × 2 presets ×
3 seed slices of the resolved payload). **0 hits, 0 null clearances**; best pmax 8.141 (drift) vs
bar 13.842. The resolved-canon seed produces no decode the old canon missed.

## RED-TEAM FOUND-ERROR (carried forward) — the HITFN real-mode held-out proxy leaks

Auditing the deployable no-oracle gate on this lane's `keyskip` relation (`out_heldout_proxy_audit.json`):

- Over 45 EN_NOVOWEL hallucinations (pmax ≥ bar, **true** recovery < 0.90 — the decodes score alone
  would certify), the **real-mode held-out self-consistency proxy catches only 15/45 (33%)**. The
  other 30 reproduce their own wrong decode consistently on the held-out 3/4 (held-out recovery
  1.000 for 24 of them). **Strict mode (truth) catches 100%.**
- **Consequence:** HITFN's guard proved rejection on a single hand-picked plant (held-out 0.833);
  at scale the held-out proxy is a much weaker discriminator than that one example implied. On a
  REAL survivor no truth exists, so `is_hit` real-mode alone **cannot certify a HIT** — a survivor
  clearing the bar would need strict recovery (unavailable) to be trusted as a solve. This does not
  affect THIS lane's negative (nothing cleared the bar at all, so the proxy was never load-bearing),
  but it **re-opens red-team defect (d) at the deployable operating point** for any future S-lane
  (S-G3) that DOES get a bar-clearing candidate: it must not certify on the real-mode proxy alone.
  Recommended fix for Round 21: strengthen clause-3 (e.g. multiple disjoint held-out folds, or a
  held-out fraction split that a hallucinating basin cannot self-reproduce across) and re-audit at
  ≥0.90 catch on this exact EN_NOVOWEL population before S-G3 certifies anything.

## Coverage + power (doctrine R2)

- **Coverage FRACTION:** 250 stored survivor keys × 2 relations = 487 adjudications + 96
  payload-reseed = 583 decodes. This is the **fully recoverable** slice of the ~1,312 repo-wide
  English-argmax rows R1 D-iii names. The remainder is NOT recoverable and is a stated hole: R17's
  rows were stored only partially (no full key params), and — decisively — B-04's −6.412 cutoff
  **structurally excluded any true `skip_by_two` key** (which scores −6.718, 0.31 below), so those
  keys were **never stored** and cannot be re-adjudicated. Fraction of the motivating case
  recoverable: **0** (the case that motivated S2 was never in the store).
- **Power PER register:** the positive control establishes power 1.00 to detect a genuine
  B-04-family key (rank-1, pmax 29.87 ≫ 7.634, recovery 1.00, LP1_REAL). Across the 9 panel
  registers the null population sits 2.9 (exact) / 5.9 (drift) below the bar — the instrument has
  ample separation and none of it is spent by a survivor.

## Three conditionals of this negative

This negative holds for: **(key space)** the 250 stored B-04 English-argmax survivor keys +
payload_resolved re-seed — NOT the un-stored keys below B-04's −6.412 cutoff (the coverage hole);
**(decoder relation)** keyskip1 `exact` and `drift_rec` (permissive, lam=12, max_free=2) — NOT
other transition models; **(adjudicator register)** all 9 panel registers via the panel-max null at
N=1e6 — NOT a per-register bar.

## Files written (`analysis/round20/S-RESCOPE/`)

`PREREG.md`, `rescope20.py`, `out_poscontrol.json`, `out_heldout_proxy_audit.json`,
`out_survivors.jsonl` (SWEEPROW/3-style rows), `out_rescope.json`, `RESULTS.md`.

## Key numbers

- positive control: plant pmax **29.87** ≥ bar 7.634, recovery **1.000**, **rank 1**/56, is_hit **True**
- survivors: **487** adjudications, **0** is_hit, **0** clears null (max pmax exact 4.76 / drift 7.99
  vs bar 7.634 / 13.842)
- payload_resolved re-seed: **96** adjudications, **0** hit, best pmax 8.14 < 13.842
- red-team: real-mode held-out proxy catches **15/45 (33%)** EN_NOVOWEL hallucinations; strict 100%
- `tests/validate.py`: PASS (5/5) before and after
