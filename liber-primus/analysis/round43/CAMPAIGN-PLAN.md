# Round 43 — THE SCREEN AND THE REMAINDER (pre-registration / plan of record)

_Drafted 2026-11-03 at the Round 42 closeout, from Round 42 X1's critic list
(`round42/X1-redteam/RESULTS.md`). Each lane's `PREREG.md` is authoritative once written and is
dated before its first output. Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md)._

## 0. Thesis — the instrument is the gate; everything else waits behind it

Round 42 emptied the open cells and paid the recovery debt. What is left on the board is almost
entirely **gated mass**: the B2 offset remainder (110.5 of 116 cells of the bash 4.2
offset×sign×ABI axis) is invisible to the current two-skip head screen at offsets ≥ 3, so the
round's centre of gravity is **I1(b) — the widened screen, with its power measured before anything
is swept** (doctrine R2: value = coverage × power; a sweep before the screen is a manufactured
power-limited negative). The small finite items (corrupt-text refetch, snapshot decision) ride
alongside. Nothing here has a deadline except the snapshot decision (~2026-11-09).

## 1. Lane roster

| ID | Type | Title | Gates on |
|---|---|---|---|
| **D1** | decision (FIRST — expires ~2026-11-09) | The S1 full candidate lists (`candidates.jsonl`, `top_S2.json`, `hist_S2.u64`) live only sandbox-side (snapshot `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6` + persistent sandbox `r42-s1-recovery`). Either export them to the laptop before the date or record a deliberate lapse in the `R42-S1` row note. Summaries + shas are already local; the verdict does not depend on the lists. | nothing |
| **I1** | instrument | (b) widen the head screen past two key skips (k ≤ 3–4), measured exactly as `pf_v4` was in R35-I1: power on planted keys with natural skip rates per register, FPR on the survivor population, frozen operating point. Success bar unchanged from the R42 plan: power on with-skip heads at offset ≥ 3 must beat the two-skip screen's 0.19–0.34 at FPR within 3× of the current point, else the B2 remainder is recorded power-limited and stays shut. (a) WATCH-band wiring, on the owner's yes. | (a) owner decision |
| **S2** | sandbox | PHP tier retry (persist control + FPR first; blocks 318+; the 3302 stream) — carried verbatim from the R42 plan, never run in R41 or R42. | a sandbox session |
| **C1** | artefact refetch | The 10 corrupt R35 keytexts: fresh hash-pinned re-download, then the R42-C1 sweep re-run on the 10 under the same PREREG terms — **with a planted control through the lane glue** (the R42 X1 deviation is binding here). | network |
| **B2** | sweep (conditional) | The offset remainder, ONLY if I1(b) lands at its measured-power bar; cells sized and ordered per the R41 B2 filing. Otherwise this lane does not exist this round. | I1(b) |
| **X1** | red-team | I1(b)'s power measurement independence; D1's export shas (if exported); C1 refetch provenance + the planted control; any B2 cells' counting; ledger patches; `check_ceiling.py`; the FULL gate; Round 44 critic. | last |

Deferred, recorded: the R44-expand variant stays control-blocked until a pointer-crafted control
reaching ≥ 0.90 recovery is pre-registered (books in hand; control design is the blocker). R31
readouts stay parked on the sub-32-rune recognizer (power first).

## 2. Verification and hit protocol

As before: `HUMAN-ORACLE.md`; a flag requires the N=1e6 bar of record; WATCH-band rows (if
adopted) get the L=240 decode + human look and are logged, never auto-certified. Every lane
plants its own positive control **through its own glue** (R42 X1 FOUND-DEVIATION — now a hard
rule, not a preference).

## 3. Owner decisions this round carries (from Round 42 §5)

WATCH band yes/no (gates I1(a)); the D1 snapshot export-or-lapse; R13 DIRECTION open→negative;
KDF noise-crosser sign-off; `with_degenerate` SWEEPROW default; the N5/N4 L=240 bundle read.

## 4. Orchestration

- **Wave A:** D1 (before 11-09); I1(b) design + power measurement.
- **Wave B:** S2 when a sandbox session opens; C1 refetch in parallel (light).
- **Wave C:** B2 only behind I1(b)'s measured bar; X1; closeout; Round 44 plan.
