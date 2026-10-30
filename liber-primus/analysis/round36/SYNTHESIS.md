# Round 36 — SYNTHESIS (THE MISSING REGISTERS, THE NEW GATE, AND THE PARKED SWEEP)

_Run 2026-10-30 on the owner's laptop plus a Vercel Linux sandbox. Plan of record: [`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md).
Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seven planned lanes plus four opportunistic ones (O2,
O3, O4 and the repo audit) and the oracle rewrite; thirteen Sonnet agents; ~9 h wall. Every decode lane ran a positive
control before its null counted. `LEDGER.json` 220 rows, 0 errors, 0 unsound negatives; `tests/validate.py` passes;
`pytest tests/ benchmark/` 26 passed; capsule `verify_capsule.py` PASS; no document drift._

## 1. Verdict in one paragraph

No survivor. The panel now reads twelve registers — Greek, Hebrew and Norse were added at 1.000 gate power with no
existing register moving (I1) — and the whole persisted bash orbit was re-decoded under it with nothing clearing (B1).
The parked Py2.7-MT S2 sweep has a gate again: panel-R36, built byte-reproducibly from recorded inputs with the
governance change written down (P1), and the verified engine advanced it 1.28 points on the sandbox with no crosser
(S1). The PHP tier ran awake with rows persisted (B2). The one recurring near-miss was autopsied and is noise on three
verifiers (O3). The clue-coverage matrix answered the owner's theory with numbers: nothing overlooked in the text, but
66 clue × reading cells never run and 55 run only English-only or legacy-beam — the Round 37 seed (O4). The repo
audit found the front-door oracle itself rejected non-English solves; it is rewritten (audit item 1), and the persona
block, stale PRs, old branches and foreclosure labels that steered work wrongly are gone or restated (AUDIT-applied).
The seal's last candidate passed at two lengths and missed at one; seal work is paused (I3).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | three registers added | 24 plants/cell | instrument | GREEK/HEBREW/NORSE 1.000 at L=120/240; nine existing within 0.02 (EN_NOVOWEL 22/24 as always); null bar +0.02–0.07 with 12 registers. X1: the mapper iterated Python sets → I1's own panel not reproducible; P1's is. |
| P1 | panel-R36 = gate of record | 12/12 ≥0.917 | — | byte-identical under three hash seeds; 53 inputs recorded (KJV/Mabinogion originals, frozen Welsh substitute, 42 new files); mu/sd match Round 19 to 5e-16 on 8/9 original registers; `GATE-CHANGE.md`; engine copy re-pointed (NREG 12, V1 references re-scored); the engine never compared its panel hash → `check_panel_gate.py`. |
| S1 | S2 advanced, 0 crossers | self-test V1 64/64, V2 exact; 4/4 resume tests | 54.97 M seeds (+1.28 pp of 2³²) | 44.138 % (Round 19 panel) + 1.28 pp (panel-R36 measurement) = 45.418 %; best 7.1256 vs 7.6342; histogram/top list live only in sandbox snapshot `snap_fWma12lA…` (expires ~2026-11-06). |
| B1 | **NEGATIVE** under 12 registers | GREEK/HEBREW/NORSE 16/16; R35 natural-rate control reproduces | 276,242 rows (1.000) re-decoded | best 7.065 (seed 1354603465 again) vs 8.044 actual-N / 8.999 declared-N; new-register best z 5.9–6.1; **reach GREEK 0.91, HEBREW 0.68, NORSE 0.64** — the nine-register-calibrated pf_v4 drops a third of Hebrew/Norse keys. |
| I2 | pf_v4 power holds on every keystream | 500 plants/cell | — | 0.94–0.99 on ILP32 and four PHP cells; FPR 6.6–9.6e-4. |
| B2 | NEGATIVE, persisted | 158/160 pf_v4, every passer recovered | tier (a) 20 % unfiltered + 80 % pf_v4; tier (b) 199 blocks | X1: tier (b) re-draws the same seed stream as R32/R34 — adds screen power + 263,906 rows, not seeds. |
| I3 | two-margin D5c: PASS L=240/300, FAIL L=150 | frozen tables, independent keys | — | HV catch 7/8 at L=150; SEAL_PASS=false; seal work paused. |
| O2 | NOT-FOUND (partial) | — | — | no source PDF/PS/font trace; GitHub trees empty; Wayback offline at query time. |
| O3 | **NOISE** | 15/15 plants | — | excess over size-matched null falls with L (4.85 → 1.08) while plants grow; argmax wanders; no word structure. Open: `free` needs L-matched nulls. |
| O4 | audit | — | — | 154 clues × 11 families: NEVER 66, English-only/legacy 55; top-8 PREREG seeds. |
| X1 | FOUND-ERROR ×5 | re-runs | — | §4. |

## 3. What the instrument now says that it did not say yesterday

1. **Twelve registers, and the first measured hole in the twelfth.** The bash orbit negative now carries Greek, Hebrew
   and Norse — at reach 0.91 / 0.68 / 0.64, because the skip-tolerant screen's log-sum-exp was frozen on nine registers.
   Recalibrating pf_v4 on twelve and re-screening is bounded (~46 min) and is Round 37's I2.
2. **S2 has a reproducible gate and a verified engine.** The Round 19 panel is retired (its Welsh corpus is lost); every
   S2 result from here on is a panel-R36 measurement and the ledger says so. 42 windows of this size remain at 2 vCPU.
3. **The oracle no longer applies the Round 18 defect.** `verify_solution.py` decodes under three relations, adjudicates
   with panel-R36, requires two pages under one relation, and emits the human-oracle bundle. Latin and vowel-dropped
   plants that FAILED yesterday PASS at 16–20 above the bar.
4. **The repo no longer forecloses by label.** "Do NOT re-run" lists are measured bounds with reopen conditions; the
   Round 11 lenses have rows; the persona block that pushed stego and motif-matching is retired; one branch, zero open
   PRs; `HUMAN-ORACLE.md` defines who reads a crosser and how.
5. **The owner's theory is now a ranked list, not a hunch.** The never-run readings with the most literal clue support
   are the composed map → road → direction rule, the first part's own numbers as a key schedule, and the 2016 clauses as
   seeds. None has a ledger row. All are thousands of decodes.

## 4. Red-team findings (X1)

| target | verdict |
|---|---|
| I1 | FOUND-ERROR: "fully deterministic" — the Hebrew mapper iterates sets; corrected in the lane docs. |
| O4 | FOUND-ERROR: two cells marked NEVER were run (English-only/legacy) → NEVER 66; corrected. |
| B2 | FOUND-ERROR: patch targeted a nonexistent id; tier (b) is not new seed coverage; patch marked superseded, ledger corrected. |
| S1 | FOUND-ERROR (wording): 44.138 → 45.418 % mixes instruments; stated per instrument in the ledger. |
| P1 | minor: five Norse paths carry U+FFFD on disk; build-twice shown under a third seed. |
| B1 | audited by the coordinator: PREREG 11:56 before null (12:24) and rows (12:56); 276,242 rows, 12-wide, panel-R36; cells match. Noted: `recovery120` diagnostic is mis-scored (not used in any decision); stock `validate_store` fails 12-wide rows (Round 37 T1). |

## 5. Recorded, not blocking

- Export sandbox snapshot `snap_fWma12lA…` (S2 histogram/top list) before ~2026-11-06, or accept losing it; the Round 34
  snapshot expires ~2026-11-05.
- S2 windows resume after the exact-relation control is independently validated and `top_S2.json` is re-scored.
- A stray `round29/L4-image-forensics/fingerprints.json` (B2 R35 fingerprinting) is untracked.

## 6. Round 37 — THE UNTRIED READINGS (plan: [`../round37/CAMPAIGN-PLAN.md`](../round37/CAMPAIGN-PLAN.md))

T1 twelve-register plumbing (incl. `validate_store` reading the register count from the header); I1 L-matched `free`
null; **I2 pf_v4 recalibrated on twelve registers and the orbit re-screened**; C1 the composed clue readings (U1–U3);
C2 recognizer/index/geometry readings (U4, U7, U8); C3 re-score the English-only clue readings under the repaired
instrument; X1. No new key space. A survivor would be extraordinary; the round succeeds without one.
