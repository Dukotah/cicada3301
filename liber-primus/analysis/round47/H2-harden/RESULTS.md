# Round 47 / H2 — harden the heavy-lift challenges before outreach: RESULTS

_2026-11-24. Lane brief: fix what R47-X1 (`../X1-redteam/AUDIT.md` §3) found in R47-H1's C7–C10. Pre-registration:
**Addendum 3 to H1's PREREG** (`../H1-heavy-lifts/PREREG.md`, sha256 `f9b4a571…` stamped in `run.log` at 22:58:53,
before any C10 number; the earlier stamps still verify on the prefix before `## Addendum 3`). Ledger rows:
`ledger_rows.json` (`R47-H2-…`). No LEDGER.json edit, no commit, no network._

## 0. Headline

- **C10 redesigned, measured, and retired by its own pre-registered rule.** The key is now unknown: the plant
  draws it from a stated family of 2^16 = 65,536 splitmix64 counter keys. Against that design, the obvious in-house
  composition crosses. It ranks every key by its printed-start decode, then runs R47-X1's segmentation beam on the
  top 512, and it recovers **88/100** plants (null FP 0). Addendum 3 fixed the rule before any number:
  FINISH = max(0.80, B + 0.20) = 1.10 > 0.95, so **C10 is not offered**. It stays in the repo as an instrument for
  a Round 48 re-scope. X1's crossing of the keyed C10 stays recorded as a finding. This is a result for the
  ledger as well as for the challenge: a (b′)-robust **unknown-key** sweep for the U2b class costs about 11–88 s per
  unit over 2^16 keys, which is affordable in-house.

- **Isolation.** C8, C9 and C10 now run the submission in a `python -I` child process (`challenges/_sandbox.py`)
  that gets only the inputs the challenge grants, one call at a time, in a random order drawn from os.urandom. All
  four of R47-X1's cheats now **fail**, and so does a call-order cheat that the fix would otherwise have left
  open (§1).
- **C7 label gate.** A corpus whose GP bigram profile is within JSD 0.06 of English, or of a covered language it
  doesn't claim, is rejected. The Latin example passes (0.12 from English). X1's Dracula-as-Old-Norse fails
  (0.024) (§2).
- **C9 re-scoped.** V-BACK is no longer scored or pitched. It is a real gap but closable in-house (X1, 32/40), and it is
  scheduled for Round 48. C9 keeps V-NULL, a *recovery* gap only, and is no longer called a heavy lift. The false
  claim that crossing V-NULL changes L7-B's detection envelope is removed (§3).
- **X1's exact text corrections** are applied to `CHALLENGES.md` and H1 `RESULTS.md` / `ledger_rows.json`. `AGENTS.md`
  and `.github/ISSUE_TEMPLATE/challenge.yml` now list the challenges that survive.

## 1. Isolation: cheat regressions

`run_cheats.sh` re-runs AUDIT §4's cheat commands against the hardened checkers. `test_heavy_checkers.py` holds
the same cases as pytest regressions.

| checker | R47-X1 cheat | before (R47-X1) | after (R47-H2, `out_cheat_*.txt`) |
|---|---|---|---|
| C7 | Dracula labelled Old Norse (`x1_cheat_c7_manifest.json`) | "NEW REGISTER … Submit it" | **FAIL** on the label gate (JSD 0.024 to English), exit 1 |
| C8 | `score()` walks to `evaluate()` and reads whether `sp` is bound | power 1.000 | power **0.000** at L = 236, exit 1 |
| C9 | `decode()` reads `evaluate()`'s `P`, `K` | V-BACK 40/40, V-NULL 40/40, "FINISH LINE MET" | C3 7/7 (the cheat falls back to the beam), **V-NULL 0/40**, V-BACK 0/40, exit 1 (seed 99) |
| C10 | `attack()` reads the loop tuple `c` | 500/500 | 0/20: the old signature no longer exists, exit 1. A frame-walking cheat for the new signature also scores 0 (pytest) |
| C8 | (new) call-order cheat: "yes" to the first n calls | (would have passed: positives were scored first) | **fails** (pytest) |

What isolation does **not** stop: a hostile program running as the same user can read another process's command
line or memory through the OS. The docs say so, and credit still needs code review. Before the fix, positives
were scored before nulls in C8, so a stateful scorer could have read the label off the call order. The random
order closes that (`test_c8_call_order_cheat_fails_isolated`). A side fix: `benchmark/gates.run_all` swallows
`TypeError` and silently re-runs the gate with the reference decoder, so submission errors are raised as
`SubmissionError` (a `RuntimeError`). C9's gate adapter computes `score` and `translit` from the returned
`plain_idx` instead of trusting the submission's own.

## 2. C7 label gate: calibration (calibrated, not pre-registered; disclosed in Addendum 3)

JSD (nats) between GP bigram profiles, using the first 150,000 runes, against the English dev pool (`_heavy.DEV_ENGLISH`):

| text | JSD vs English |
|---|---|
| 15 in-repo English texts (Poe, Legge, Kant, Whitman, *Dracula*, Herodotus, Crowley, Bunyan, *Hamlet*, KJV Job, Dryden, Agrippa, *Liber AL*, Douay-Rheims, Tyndale) | 0.014 – 0.049 |
| Old English (Beowulf) | 0.079 |
| Latin (Aeneid / latin_218) | 0.122 / 0.134 |
| German (Faust / de_2) | 0.137 / 0.144 |
| Welsh (Mabinogion) | 0.187 |

- **Within a language:** Latin–Latin 0.019, German–German 0.017.
- **Between languages:** every pair is ≥ 0.079.
- **τ = 0.06.** The gate rejects a corpus within τ of English or of any covered language other than its claimed one.
- **Checks:** the Latin worked example validates, at 0.12 from English. X1's manifest fails at 0.024. Both are in
  `--self-test` and pytest.
- **Limits:**
  - A table can be tuned to move a profile.
  - No Middle English text was available, so a close relative of English may be flagged legitimately.
  - The message says this, and maintainers still review source and table by hand.

## 3. C9 re-scope

- **V-BACK is diagnostic now.**
  - It still runs and is still reported.
  - The C9 docstring, CHALLENGES.md and the prompt say it is closable in-house (X1, 32/40, dev seed).
  - Round 48 is to add a backstep relation to beam_v3 and re-adjudicate the beam-based negatives under it.
- **V-NULL is the only scored variant.**
  - Its thresholds are unchanged.
  - X1's §3.6 #4 and #5 texts are inserted verbatim.
  - "Changes" now says no detection negative moves; only the recovery qualifier does.
- **Not a heavy lift.** C9 is relabelled "days", because X1's quick null relation already gets 8/40.

## 4. C10 redesign

**Design** (H1 PREREG Addendum 3; checker `challenges/c10_shuffled_lengths.py`):
- **Plant.** The plant and the print are R47-H1's: R37-U2b word jump; whole English sentences of 236–472 runes;
  lengths shuffled within each sentence; true sentence boundaries.
- **Key.** Per unit, the key is drawn from
  K_s[t] = splitmix64(SALT + s·2^32 + t) mod 29, with s < 2^16.
- **Null.** The null uses a key from outside the family (s ≥ 2^20).
- **Submission.** `attack(C, printed)` runs isolated, with 60 s wall-clock per unit.
- **Probes before the stamp.** Two probes ran before the stamp and are disclosed in the addendum: a key-family
  equality check, and one timing of the ranker.

**Baselines** (seed 4710, 100 plants + 100 nulls, `c10_baselines.py`, `c10_baselines.json`, `out_c10_*.txt`;
7 worker processes, so the times are under load):

| arm | plants recovered (Wilson 95 %) | mean recovery | null FP | s / unit |
|---|---|---|---|---|
| (i) exhaustive over all 2^16 keys, TRUE lengths (control, needs ≥ 0.95) | **100/100** (0.963–1.0) | 1.000 | 0.00 | 7 |
| (ii) exhaustive, jumps at the PRINTED starts | **0/100** (0–0.037) | 0.209 | 0.00 | 7 |
| (iii) X1's beam, per key: correct key vs 1,024 sampled wrong keys (16 plant + 16 null units) | the correct key beats every sampled wrong key on **16/16** units; recovery 0.968; correct −4.13…−4.58 vs best wrong −5.86…−6.17; null max −5.84…−6.14 | — | — | 0.20 s/key, so ≈ 13,250 s (3.7 h) per unit for the full family |
| (iv) printed-start rank, X1's beam on the top 64 | **78/100** (0.689–0.85); true key in top 64: 0.80 | 0.780 | 0.00 | 11 |
| (iv) printed-start rank, X1's beam on the top 512 | **88/100** (0.802–0.93); true key in top 512: 0.90 | 0.871 | 0.00 | 88 |

**Applying the rule:**
- B = 0.88, so FINISH = max(0.80, 1.08), rounded up to 1.10, which is above 0.95.
- So C10 is **not published as a heavy lift**. CHALLENGES.md marks it retired pending Round 48.
- The checker keeps the instrument bar (0.80) but never prints a crossing.
- The threshold was not moved after the numbers.

**What it means:**
- **Shuffled lengths do not hide the key.** The printed-start decode cannot *recover* a plant (ii), but it
  *ranks* the true key in the top 64 of 65,536 on 80 % of units and in the top 512 on 90 %. That fits H1's finding
  that the printed-start rule still *detects* at FPR 0.01 (0.83).
- **The gap between (iv) and (i) is a ranking problem.** It is the 10–20 % of units whose true key falls outside
  the top m, not a segmentation problem. Every key that reached the beam was decoded.
- **Implication for R46-L1.** For the U2b class, (b′) is a decoder conditional, now also at unknown key over a 2^16
  family. A (b′)-robust re-run of `R46-L1-R37-U2B-U3-RECHECK`'s real job is affordable in-house. That is a Round 48
  item, together with re-scoping C10: a larger family, the doublet filter, and the other word-indexed
  constructions (R41 W1–W4, G3 lagged pointers, the lexicon rows).
- **The keyed C10 crossing is kept.**
  - The v1 checker is preserved at `c10_v1_keyed.py` with X1's reproduce line. It is in-process, so it is not
    safe for outside submissions.
  - The finding stands: at known key, the (b′) loss is the decoder's, not the information's.
  - (iii) adds that the same beam also separates the correct key from 1,024 wrong ones (margin about 1.5
    log-units).

## 5. Tests

- `challenges/test_heavy_checkers.py`: **11/11 pass** (`out_pytest_challenges.txt`). It includes the 6 isolation and
  label regressions and the redesigned C10's family and ceiling test. `c1_crossdiff_test.py` fails on purpose, as
  before.
- Self-tests:
  - C7 PASS (the Latin example passes; the corrupted copy and X1's label cheat FAIL).
  - C8 PASS (seed 4712).
  - C9 PASS (seed 4711: keyskip 12/12, V-NULL 0/12, V-BACK 1/12).
  - C10 PASS (seed 4713, n = 20: exact 20/20; (i) 20/20; (ii) 0/20).
- `python -m pytest -q -m "not network"` from `liber-primus/`: **120 passed, 5 skipped, 3 deselected**
  (`out_pytest.txt`).
- Deviations:
  - The first (iv, m=64) launch was killed by the lane at start-up while it was diagnosing a slow-looking pool.
    It had no output, and it was re-run unchanged.
  - The pytest and cheat runs overlapped the baseline pool, so the s/unit figures are under load.
  - X1's §3.6 #8 sealing sentence ("Submissions run in the checker's process; credit also requires code review")
    is superseded by the isolation paragraph, because the first half is no longer true.

## 6. For the coordinator

- `ELIMINATION-LEDGER.md`, `analysis/README.md`, `PICKUP-HERE.md` and `README.md` need the C9/C10 changes.
- They also need the Round 48 item: a backstep-aware beam, plus a re-adjudication of the beam negatives.
- The R46-L1 qualifier from AUDIT §5 is still unapplied. It is outside this lane's scope.

---
CLOSED 2026-11-25 R47-H2 harden | isolation: C8/C9/C10 submissions in a python -I child, inputs only, os.urandom order; all 4 R47-X1 cheats + a call-order cheat now FAIL | C7 label gate JSD<=0.06 (Latin example passes 0.122, X1 Dracula-as-Norse fails 0.024) | C9 scores V-NULL only, V-BACK -> Round 48 | C10 redesigned (unknown key, 2^16 family): (i) 100/100, (ii) 0/100, (iii) correct key wins 16/16 vs 1,024 at ~3.7 h/unit, (iv) 78/100 (m=64) and 88/100 (m=512) -> pre-registered FINISH 1.10 > 0.95 -> C10 RETIRED pending R48 | H1 PREREG Addendum 3 f9b4a571 | 5 ledger rows R47-H2-… | tests 11/11, liber-primus pytest 120 passed | no LEDGER.json edit, no commit
