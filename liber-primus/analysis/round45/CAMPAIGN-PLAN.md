# Round 45 — THE SPACES ARE NOT THE WORDS (pre-registration / plan of record)

_Drafted 2026-11-23 by the coordinator. Doctrine binds (`ARMADA-DOCTRINE.md`): PREREG before data,
plants through the lane's own glue, ledger-diff before any run, coverage × power with the three
conditionals, HUMAN-ORACLE.md for any bar-crosser, lanes write files and never commit. Round 44's
dead-man rule is binding: any arm expected to run > 30 min writes a timestamped heartbeat, and the
coordinator does not close a lane with no closing stamp. Read `round44/SYNTHESIS.md` §2 and §6 first._

## 0. Inputs that changed the aim

1. **External ledger reviewed: FlareZ123/liber-primus** (≈50 agents, 48K commits, 2026-11-08 → 23).
   Its rune data is *derived from this repo's `dataset/liber_primus.json`* (13,136 = 12,956 unsolved +
   85 + 95 solved runes + an empty p50 slot). The two efforts therefore share one transcription;
   agreement between them is not replication of the input. Imported rows: `R45-IMPORT-*` (M0 below).
2. **Fable 5.2 fresh-eyes pass** (`analysis/fable52/`, scripts + `OUTPUTS.txt`, 2026-11-23):
   - **Printed word breaks in LP2 carry no word-order grammar.** Adjacent word-length mutual
     information on the 2,896 printed words is shuffle-level (z = +0.5); the solved-LP reference
     scores z = +7.4 on only 875 words; 32 English windows of matched size, min z = +5.4. Nine
     875-word LP2 windows span −1.5 … +2.3. (FlareZ123 found this first —
     `im-results/lp2-original-wordlength-grammar-mi.md`; Fable replicated independently.)
   - FlareZ123's line-occupancy null that appears to explain T7 (p ≈ 0.23) is saturated: null mean
     0.367 / sd 0.009 against observed 0.380, power 0.04 against a planted low-rate window. **T7 stays
     live.** T7 is distributed rate heterogeneity (rank AC +0.27 p = 0.003), not a single void.
   - FlareZ123's p50 leading-zero doublet enrichment fails phase look-elsewhere. Not imported as signal.

## 1. Thesis

Every lane in this repo that uses the printed spaces — word-length cribs, C-01 SKELETON, word-sum
keys, quote-span cribs, the HUMAN-ORACLE reading rule, and any scorer whose plants keep real word
boundaries — assumes the spaces are the plaintext's words in order. The data now contradicts that.
If the spaces are a decoy, shuffled, or keyed, then (a) some negatives in the ledger are conditional
on a false premise, and (b) *what the spaces are* is itself a new finite channel. Round 45 audits the
instrument against that premise first (R1), then characterises the channel, then spends the rest on
the one live anomaly (T7) and on the single shared point of failure (the transcription).

## 2. Lane roster

| ID | Title | Doctrine class | Agent |
|---|---|---|---|
| **M0** | **Import fold-in.** FlareZ123 imports as bounded rows (with register conditionals), Fable52 measured rows, CROSS-LEDGER entry, README "doublet-free 1,649" correction. | closeout | opus, sequential, commits |
| **I1** | **Decoy-space audit.** Inventory every instrument/lane that consumes printed word boundaries. Re-plant the standing positive controls (beam_v3, pf_v4, panel-R36, verify_solution) with the plaintext's spaces shuffled / removed / replaced by LP2's own printed lengths, and measure the power delta. Output: a list of ledger rows whose negative is conditional on "spaces = plaintext words in order", each with measured power under the alternative. | instrument (R1) | opus |
| **W1** | **What are the spaces?** Characterise the printed word-length stream as an object: (i) a statistic that *passes a positive control on real prose* for within-scope shuffling (Fable's t8 failed this — fix it); (ii) scope of the scrambling: global / chapter / page / line / sentence; (iii) multiset test: is the LP2 length multiset (per chapter, per page) consistent with GP-English plaintext lengths at all, vs geometric/random spacing, vs a fixed-period or keyed generator; (iv) dependence between word length and rune content (do runes at word starts/ends differ from interior — would a keyed spacing leak?). | finite object (R5 #1) | opus |
| **T1** | **T7 mechanism, honest nulls.** Pre-register ≤ 4 covariates (chapter, 10-/13-dot interval, position within section, page) and fit a doublet-rate model; ordering-sensitive registered statistic with a *smooth-heterogeneity* plant (R44 §2 gap). Compare mechanisms: drifting filter parameter, sessioned generation (rate changes at session boundaries), stateful rejection loop. Plaintext-letter marker is disfavoured by Fable52 T5 — test it only as the null alternative. | measured-anomaly lane | opus |
| **S1** | **Independent transcription audit.** The shared transcription is the common point of failure. Re-read the positions where RiskAverseTech's independent read does not align with canon (≈149) directly from the page images, blind to both readings first, then adjudicate. Output: a corrected-or-confirmed position list and the measured canon error rate. | finite object (R5 #1) | opus |
| **X1** | **Red-team Round 45 itself** after I1/W1/T1/S1 return: audit each lane's plant, null and conditionals; recommend STOP/REDIRECT if warranted (R6). | red-team | coordinator + opus |

Budget split (doctrine §3): I1 30% · W1 + S1 40% (bounded high-prior objects) · X1 20% · M0/T1 10%.
No key-space sweep is scheduled. A sweep may be proposed by W1 or I1 only if their result names a
bounded space whose prior was raised by a measured fact.

## 3. Shared rules for this round

- Lanes write only inside `analysis/round45/<LANE>/`. PREREG.md (with the five Aiming-Test answers
  and a dated header) is written before the first output file in the lane.
- Every statistic ships with its planted positive control and its measured power; a test whose
  control fails is reported "uninformative", not "negative".
- Each lane leaves `ledger_rows.json` (same schema as `LEDGER.json` entries, ids `R45-<LANE>-…`) and
  `RESULTS.md`. The coordinator merges rows into `LEDGER.json`; lanes do not edit it.
- Pure stdlib Python preferred; no installs; single runs under ~10 min unless heartbeated.
- Shared input: canonical stream pinned by `PROBLEM.json` sha256; word/line/page boundaries from the
  canonical dataset. Fable52's loaders (`analysis/fable52/load2.py`, `gp.py`) may be reused.

## 4. Gate to close the round

I1, W1, T1, S1 all have RESULTS.md + ledger_rows.json + closing stamp; X1 has ruled on each; the
four CI gates are green (`tests/validate.py`, `pytest -q -m "not network"`,
`analysis/handoff/check_consistency.py`, `analysis/round39/P1-measured-ceiling/check_ceiling.py`);
nav docs updated; one coordinator commit to master.
