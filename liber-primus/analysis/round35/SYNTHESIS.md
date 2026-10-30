# Round 35 — SYNTHESIS (THE SKIP-TOLERANT SCREEN, THE RESTORED PANEL, AND THE PARKED SWEEP)

_Run 2026-10-30 on the owner's laptop. Plan of record: [`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine:
[`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Six lanes run, one (S1) skipped with cause; seven Sonnet agents;
~4 h wall. Every lane ran a positive control before its null counted. `LEDGER.json` 202 rows, 0 errors, 0 unsound
negatives; `tests/validate.py` passes; `pytest tests/ benchmark/` 24 passed; capsule `verify_capsule.py` **PASS** (first
clean verification since the capsule was written)._

## 1. Verdict in one paragraph

No survivor. The flagship landed: a head screen that tolerates up to two key skips in the first 24 runes (`pf_v4`) lifts
natural-rate screening power from 0.65–0.78 to 0.95–0.99 in every register (I1), and the full bash `$RANDOM` auto-seed
orbit — both ABIs, 77.6 M seeds each — re-screened with it and decoded by the register-aware beam under the observed null
flagged nothing (B1). That orbit is now a negative whose reach is the beam's, not the screen's. The original KJV and
Mabinogion downloads were recovered byte-exact and the capsule verifies clean, but the Round 19 Welsh corpus has no
recorded source and no surviving copy, so the Round 19 panel cannot be rebuilt and the parked S2 sweep stays parked
(P1; S1 skipped). The linear D5c seal rule, pre-registered this time, failed at every length on new keys and is
retired (I3). The last unmeasured payload legs are measured and unchanged (B2). The red-team corrected three errors in
the coordinator's own Round 34 B1 write-up and one in the coordinator's fetcher edit (X1).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | bar met at (m=24, k=2) | 2,000 natural-rate plants/register | instrument | lse over a per-register Viterbi (≤2 skips, 2 nats each); EN_NOVOWEL 0.98, weakest EN_HALFVOWEL 0.948, with-skip heads 0.92–0.99; held-out FPR 7.8–9.6e-4 across six generators; 10.9× pf_v3 (≈23 min per ABI orbit); k=0 ≡ pf_v3 exactly. X1 re-run agrees. |
| B1 | **NEGATIVE, bounded** | 93/96 natural-rate plants (3 prefilter misses; every passer recovered) | both orbits 1.000 × reach 0.95–0.99 per register | 69,017 / 69,104 survivors; 276,242 rows persisted; best 7.068 (seed 1354603465, keyskip2) vs 8.058 actual-N / 9.034 declared-N; 0 flagged, 0 near-miss. |
| P1 | NO-MATCH (Welsh) | hash chain | 10/11 corpora byte-exact | KJV (`/files/10/10-0.txt`) and Mabinogion (`/files/5160/5160-0.txt`) match their recorded hashes; Welsh "diplomatic edition" (4b3fd926…, 524,561 B) has no recorded URL, no backup, nothing in git history, no archive.org OCR match → R19 panel not rebuilt. |
| S1 | skipped with cause | — | — | gated on P1; S2 resume remains blocked; nothing resumed. |
| I3 | **FAIL** at L=150/300/400 | frozen rule, held-out keys only | — | catch 0.853 at L=150; NV-only FR 0.158 / 0.41 at L=300 / 400; HALFVOWEL genuine rejected wholesale; D5c-as-written catches 0/30 HALFVOWEL-argmax hallucinations. Linear rule retired; SEAL_PASS=false. |
| B2 | measured, unchanged | each leg's original control | 3 inputs fetched (folly md5 match; T2/2.jpg statistical/structural identity) | R30-B1 canon-as-key + XOR legs and R30-B2 folly/2.jpg legs reproduce stored results under the superseded canon and show 0 hits under the promoted one. |
| X1 | FOUND-ERROR ×4 on coordinator work + minors | re-runs | — | §4. |

## 3. What the instrument now says that it did not say yesterday

1. **The bash `$RANDOM` auto-seed orbit is a register-aware negative at reach 0.95–0.99.** Three rounds ago it was an
   English-only negative at an unmeasured power; two rounds ago ≈0.47 for vowel-dropped English; one round ago
   ≈0.65–0.70. The screen, the beam and the null are now all measured on natural-rate plants.
2. **Skips in the head were the whole remaining gap, and ≤2 of them are screenable.** ≥3 skips in 24 runes is ≈3 % of
   mass (Poisson estimate, X1); heads past 24 are not screened.
3. **S2 cannot be resumed under its original gate.** The engine is verified (Round 34 S1) but its self-test is bound
   to a panel whose Welsh corpus is lost. Moving S2 requires a governance decision: re-gate on a new panel with a
   recorded build. That is Round 36's P1.
4. **The capsule is trustworthy again.** Every local item verifies; the fetcher restores the Round 19 corpora byte-exact
   (`fetch_sources.py --r19`) and refuses on mismatch.
5. **The seal is still off, and the linear rule is dead.** Separate NOVOWEL / HALFVOWEL margins look separable in
   hindsight (I3 §"Why it fails") and are the only candidate left; they must be pre-registered on independent keys.

## 4. Red-team findings (X1)

| target | verdict |
|---|---|
| R34 B1 write-up (coordinator) | **FOUND-ERROR ×3:** the resumed run reopened the store in write mode so 324,798 bash decodes were never persisted; the PHP prior-dense tier was prefiltered except its 487 core seeds; the 0.061 % uniform fraction was a sleep artefact. Per-cell numbers and fraction 1.000 reproduce. Row corrected, original kept. |
| P1 / coordinator fetcher edit | **FOUND-ERROR:** the script had no KJV/Mabinogion fetch; the coordinator's URL edit changed the Welsh substitute instead. Fixed with `ensure_r19_corpora()` / `--r19`. |
| I1 | NO-ERROR-FOUND: re-run 0.973 / 0.970 vs lane 0.980 / 0.949; k=0 ≡ pf_v3; fresh-seed FPR under 1e-3. |
| B2 | NO-ERROR-FOUND: comparator entropies reproduce to 4 decimals; caveat on the rows. |
| B1 / I3 | audited by the coordinator (X1 closed first): PREREG predates outputs; B1 store holds bash rows; I3 held to the Wilson criteria (it fails under either reading). |

## 5. Owner-only items (recorded, not blocking)

1. **S2 re-gate.** Resuming the 55.86 % remainder of the Py2.7-MT `exact` space now requires accepting a new recorded
   panel as the engine's gate (the original is unrebuildable). Round 36 P1 builds that panel with a recorded,
   reproducible build and S1 runs the engine's self-test against it; the window resume itself is scoped and leaves the
   live state resumable.
2. `data/kjv.txt` and `data/keys/mabinogion.txt` are now the byte-exact originals; the Round 32 substitutes survive
   only under `round35/P1-restore-r19-panel/backup/` (gitignored).
3. The stale Vercel snapshot (expires ~2026-11-05) and PRs #7–#10.
4. A stray `round29/L4-image-forensics/fingerprints.json` (1.9 KB, 09:30 2026-10-30) appeared during B2's JPEG
   fingerprinting; left untracked for the owner to keep or drop.

## 6. Round 36 — seeded from X1's critic list (plan: [`../round36/CAMPAIGN-PLAN.md`](../round36/CAMPAIGN-PLAN.md))

1. Greek, Hebrew and Norse registers (absent since Round 32) → a 12-register panel with measured power → re-adjudicate
   the persisted R35-B1 survivors through it (cheap; the rows exist this time).
2. A new recorded panel to re-gate the S2 engine (Welsh-free, governance change recorded) → sandbox self-test → S2
   window.
3. pf_v4 power on ILP32 and PHP keystreams; the PHP tier re-run awake with rows persisted.
4. A D5c successor with separate NOVOWEL / HALFVOWEL margins, pre-registered on independent keys.

No new key space. A survivor would be extraordinary; the round succeeds without one.
