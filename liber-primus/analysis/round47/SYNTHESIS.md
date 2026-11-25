# Round 47 — SYNTHESIS: close the caveats, open the heavy lifts to outside compute

_Coordinator closeout, 2026-11-25. Lanes: T2, L2, H1, X1, plus H2 (a hardening lane added after X1 to fix what X1
found in H1). Plan of record: `CAMPAIGN-PLAN.md`. Every measuring lane pre-registered (PREREG sha256 stamped in its
log before its first output; H2 ran under H1's stamped Addendum 3), planted its own control, and closed with a
stamp. X1 audited T2, L2 and H1 and ruled each **UPHELD-WITH-CORRECTIONS**. Its corrections are applied in the lane
files (each `RESULTS.md` ends with an "X1 corrections applied" note; H2 applied H1's and `CHALLENGES.md`'s, the
coordinator applied T2's, L2's and the R46-L1 qualifier) and in the ledger rows. PREREGs are untouched. Verdict on
the cipher: **OTP-class, UNCHANGED.** No key-space sweep was run. The only real decodes were re-runs of rows that
already existed (L2), through the repaired loader._

## 1. What Round 47 established

1. **The transcription: 3 of the 4 disputes go to canon, and one position is flagged for the oracle** (T2,
   X1-upheld with one correction).
   - A third blind reader read all **27** of S1's window-line look-alike-family glyphs (15 line strips). T2 = canon
     on **26/27**. Controls: W swaps 8/8 caught and named; solved page 73 24/24.
   - **gpos 276 = A, 5054 = TH, 6054 = AE are canon.** At each, S1's blind read was the error.
   - **gpos 9877 (canon D) is `canon-error-candidate`, FLAGGED FOR ORACLE, not applied.** T2 and S1 both read M; the
     leave-line-out template reads D (0.969 vs 0.686). The evidence leans to reader error: T2 also misread a
     non-target canon D (gpos 280) as M, and **an M at 9877 would create an MM doublet with 9876 (M)**. LP2's
     doublet rate (0.66 % vs 3.55 % for any given other rune) favours canon D about **5.3 : 1**, independently of any
     reader (X1's correction; T2 had written "touches no doublet site").
   - Two-reader bounds: O/A/AE ≤ 4.6 %, M/D ≤ 19.9 % (13.4 % if 9877 is upheld), all five families ≤ 2.8 % (1.9 %).
     0 corrections applied to canon.
2. **Every R45-voided word row is now measured** (L1 in Round 46 + L2 here, X1-upheld).
   - **R38-C2-G3 is re-run.** The fragment conventions for the mid-word pages 1, 2, 4, 5 are stated (C0 / CS / CE)
     and all run: 768 real decodes, best ks1 5.440 / ks2 4.737 / direct 4.111 vs bars 6.048 / 5.967 / 6.574,
     0 flagged. Power on LP2's real layout is 1.00 under (a) and (b) for every convention. R46's
     fragment-convention CONDITIONAL is closed.
   - **R38-WORDNET, R38-FREQRANK and R39-SENSE now have measured power** through each row's own lexicon glue: 1.00
     under (a) and (b), C0/CS/CE. Real CS/CE re-runs on pages 1–2 (56,448 decodes) are all below the bars.
   - C0 faithfulness reproduces every recorded best exactly; X1 recomputed all eight bars exactly.
   - Under (b′) every one of these rows is 0.00 **for its own decoder fed the printed lengths**. No segmentation
     search was run (X1 qualifier; see 3).
3. **(b′) is a decoder limitation, not an information barrier, for bounded key families** (H1 + X1 + H2).
   - With the key in hand, the printed-start rule still **detects** U2b plants under (b′) at FPR 0.01 (power
     0.83 / 0.81; H1), and a 58-line position-synchronous segmentation beam **recovers** them (481/500 and 488/500,
     null FP 0; X1). **With the key in hand the (b′) loss is the decoder's, not the information's.**
   - With an **unknown key from a 65,536-key family**, ranking every key by its printed-start decode and running the
     arrangement beam on the top 64 / 512 recovers **78/100 / 88/100** (null FP 0; H2). The residual is a ranking
     problem (true key outside the top m), not a segmentation problem.
   - Consequence: R46's "every word-indexed row falls to ≤ 0.033 under (b′)" reads "not re-run with a
     (b′)-robust decoder", not "blind". **Word-indexed negatives can be re-adjudicated under (b′) with an
     arrangement-aware decoder** wherever the key family is bounded. For the U2b class this costs about 11–88 s per
     unit over 2^16 keys, which is affordable in-house. For G3 lagged pointers and the lexicon rows (key depends on the
     previous word's value or identity) it is unmeasured.
4. **A named rejection-loop gap in the beam: V-BACK** (H1, X1-upheld with qualifiers).
   - Under V-BACK (on a rejected doublet the key pointer steps back one place, a one-character edit from keyskip),
     both the C3 reference beam and beam_v3 score the **correct key as noise**: **0/40**, median −7.01 / −6.79. No
     beam-based negative in the ledger covers it. This is a concrete instance of L7-B.
   - It is **representational and closable**: X1 added one backstep transition to skipdecode's beam and recovered
     **32/40** through the unchanged checker (dev seed 4701, penalties tuned on that seed, so not a sealed result).
   - V-BACK is consistent with LP2's surface statistics (z of LP2 −0.38 / −0.59 / −0.27 on lag-1 / lag-2 / IoC), but
     **no measured fact raises its prior**. It is one of an unbounded family of non-monotone loops.
   - V-NULL (doublet-triggered null, rejected key symbol discarded) is a **recovery gap only**: the key still advances
     once per cipher rune, beams score its correct key as English (−4.54), so every beam negative already covers it
     at detection.
5. **Public challenges C7, C8, C9 are published with isolated checkers** (H1, hardened by H2).
   - `challenges/c7_corpus_forge.py` (reference-corpus forge, with a Latin worked example),
     `c8_register_scorer.py` (non-English adjudicator), `c9_rejection_loops.py` (now scores V-NULL only; V-BACK is a
     diagnostic, scheduled in-house for Round 48). `CHALLENGES.md` has a "Heavy lifts" section, copy-paste agent
     prompts, `AGENTS.md` and `.github/ISSUE_TEMPLATE/challenge.yml` list them.
   - **Isolation:** X1 passed all four v1 checkers with in-process cheats (frame reading, label lies). H2 now runs C8,
     C9 and C10 submissions in a `python -I` child (`challenges/_sandbox.py`) that gets only the granted inputs, one
     call at a time, in `os.urandom` order. All four X1 cheats and a call-order cheat now fail
     (`challenges/test_heavy_checkers.py`, 11/11). C7 has a label gate (GP-bigram JSD ≤ 0.06 to English or to a
     covered language it does not claim is rejected; Latin example 0.122 passes, X1's Dracula-as-Old-Norse 0.024
     fails). Credit still requires code review (OS-level inspection is not blocked).
   - C8 baseline: at FPR 0.01 (not at sweep-scale bars) the English scorer already detects Latin and German
     page-size windows; the gap is in sequence-unlike registers (vowel-dropped English 0.00 / panel 0.33).
6. **C10 is retired pending Round 48** (H2, by its own pre-registered rule).
   - The keyed v1 was crossed in-house by X1 (0.962 / 0.976), so it was not a heavy lift. H2 redesigned it with an
     unknown key (2^16 family) and fixed the rule in Addendum 3 before any number: FINISH = max(0.80, B + 0.20).
     The in-house composition gives B = 0.88, so FINISH = 1.10 > 0.95 and C10 is **not offered**. The checker stays
     as an instrument; the v1 keyed checker is kept at `H2-harden/c10_v1_keyed.py`.

## 2. Defects found

- **T2:** "touches no doublet site" for 9877 was wrong; M would create an MM doublet (X1 §1.3). Corrected in RESULTS
  and the `reopens_if`. Verdict unchanged.
- **L2:** the (b′) "0.00" lacked a decoder qualifier, and "That is challenge C10" was a misattribution (X1 §2.6).
  Corrected; the same qualifier is now on R46-L1's (b′) sentence and on R46-L1-R37-U2B-U3-RECHECK /
  R46-L1-REOPEN-VERDICTS (lane rows and dated R47 notes in LEDGER.json).
- **H1:** C10 was not a heavy lift (crossed by a 58-line beam); all four checkers were cheatable in-process or by
  label; C9's text claimed that crossing V-NULL changes L7-B's detection envelope (it does not); H1's C10 finish line
  was re-aimed after the registered one proved unreachable (disclosed, stamped, but mis-sized). All fixed by H2 and
  recorded in rows R47-X1-… and R47-H2-….
- **Ledger vocabulary:** two H2 rows used statuses outside the controlled vocabulary (`decision`, `recorded`). They
  are merged as `audit` with `status_before_normalisation` kept.
- Still open (carried forward): R46 §4.5 hygiene — rebuild `stones/dataset.npz` from the v2 map; decide which
  lineage is canonical for the 2 separators and 5 grid cells; wire `check_prereg_stamps.py` into CI with a
  chronology check; add a consensus-clustering check before any O/A/AE candidate list is reused. Lead (i) reference
  corpora (Greek, Hebrew, Norse, archaic English verse) are now C7's job; lead (ii) still needs LP1-like data.

## 3. Leads (status after this round)

- **Transcription:** closed except gpos 9877, which waits on the oracle or a higher-resolution master. Prior 5.3 : 1
  for canon D from the doublet rate alone.
- **(b′) word-indexed rows:** now a decoder question with a known, affordable fix for bounded key families.
- **V-BACK:** a named, closable L7-B gap. No evidence LP2 uses it; every beam-based negative is silent on it.
- **2-rune deficit (lead i), line breaks (lead ii), T7:** unchanged from Round 46.

## 4. Round 48 plan

CONTINUE, narrow, in-house. No open-ended key-space sweep.

1. **Backstep-aware beam.** Add a BACK relation to `beam_v3`, certify it on the C3 gates and on sealed V-BACK plants
   (fresh seed, penalties frozen first), then **re-adjudicate the beam-based negatives under V-BACK**.
2. **Arrangement-aware decoder for word-indexed rows under (b′)** where the key family is bounded: the U2b class first
   (R37-U2b real job, R46-L1-R37-U2B-U3-RECHECK), then R41 W1–W4, G3 lagged pointers and the lexicon rows, each with
   its own plants through its own glue.
3. **Relaunch C10** with a finish line that passes its own rule (FINISH ≤ 0.95 against the best in-house
   composition): a larger key family, the doublet filter, or another word-indexed construction.
4. **gpos 9877:** oracle bundle (line 455 boxes 5–6 beside page-73 M and D exemplars) or a higher-resolution master
   ruling.
5. **R46 §4.5 hygiene carry-overs** (see §2).

## 5. Ledger

`LEDGER.json` **400 → 420** (T2 2, L2 4, H1 4, H2 5, X1 5). Statuses of older rows are left as recorded. Dated
R47 notes were added to R38-C2-G3-LAGGED-POINTERS, R38-C1-SEMANTIC-WORDNET, R38-C1-SEMANTIC-FREQRANK,
R39-C1-SENSE-SIMILARITY, R37-C1-U2-LP1-NUMBER-SCHEDULES, R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION, C-01,
R46-L1-R37-U2B-U3-RECHECK, R46-L1-REOPEN-VERDICTS, R46-L1-SKELETON-RERUN, R46-L1-R41-R14-RERUN, L7-B-BEAM-ENVELOPE,
R45-S1-CANON-ERROR-RATE and R46-S2-SECOND-READER-FAMILY-BOUND. 0 unsound negatives.
