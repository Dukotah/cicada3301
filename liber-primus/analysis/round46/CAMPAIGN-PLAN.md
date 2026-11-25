# Round 46 — REPAIR THE WORD INSTRUMENTS, TEST THE TWO LEADS (plan of record)

_Drafted 2026-11-24 by the coordinator. Doctrine binds (`ARMADA-DOCTRINE.md`): PREREG with the five
Aiming-Test answers before data, plants through the lane's own glue, coverage × power with the three
conditionals (key space, decoder transition model, adjudicator register), lanes write files and never
commit, dead-man heartbeat for any arm > 30 min. Read `round45/SYNTHESIS.md` first; this round is its §4._

## 0. Why this round

Round 45 showed LP2's printed word breaks are an English-like length multiset in scrambled order over a
contiguous rune stream (W1), and that ten word-indexed ledger rows lose all power if the spaces are decoy
(I1). Independently, R41's loader split words at line breaks, so R41 W1–W4 were underpowered **even with
true spaces** (X1). Round 46 repairs the instruments first (doctrine R1), then re-measures the voided rows,
then gives the two post-hoc leads a fair pre-registered test. No key-space sweep is scheduled.

## 1. Lanes

| ID | Title | Class | Agent |
|---|---|---|---|
| **L1** | **One correct printed-word loader + re-run the voided rows.** Build `analysis/round46/L1-word-loader/words.py`: printed words of LP1/LP2 from the canonical dataset, joining page/line-wrapping words (target 2,896 LP2 words; reconcile any difference). Unit tests against solved pages. Then re-run R41 W1–W4 and R37 U2b/U3 through it, with plants of two kinds on LP2's real layout: (a) true spaces in order, (b) spaces shuffled within sentence. Report power under each, and the new verdict for each of the ten I1-reopened rows (which remain dead under (b) and are marked conditional, which recover power). | instrument (R1) | opus |
| **P1** | **Pre-registered tests of the two leads.** (i) 2-rune-word shortfall (LP2 15.5% vs English ≥ 19.7%); (ii) line breaks inside words 71% vs chance 78% (LP1 53%). These were found on LP2, so the PREREG must say what is genuinely confirmatory: fresh reference corpora not used in R45 (other English registers, archaic/KJV, translated text, non-English GP transliterations where available), split-half within LP2 (chapters held out), and the competing explanations each test discriminates (fewer articles / another language / lengths borrowed from another text / typesetting). | finite object (R5) | opus |
| **A1** | **Instrument hygiene.** (a) Repair `analysis/stones/alignment.json` from `round45/S1-transcription/corrected_map.json` (keep the old file as `alignment.v1.json`; document the diff); measure what changes downstream (Campaign-V classifier labels, the 450 O/A/AE disagreements). (b) Repoint `analysis/fable52/` scripts to in-repo data per `round45/X1-redteam/AUDIT.md`; confirm OUTPUTS reproduce. (c) Add a hash-stamp check for PREREG addenda (rule from R45 §2). | instrument | opus |
| **S2** | **Second independent reader for look-alike classes.** Closes S1's single-reader caveat. Blind re-read of the look-alike-class sample (and a fresh random sample) from page images, without looking at canon or S1's reads until the batch is saved. Small crops only; save reads in batches of ≤ 25; heartbeat file. Report inter-reader agreement and the canon error bound with two readers. | finite object | opus |
| **X1** | **Red-team Round 46** after L1/P1/A1/S2 return. | red-team | coordinator + opus |

Budget: L1 40% · P1 20% · A1 10% · S2 10% · X1 20%.

## 2. Shared rules

Same as Round 45 §3: write only inside `analysis/round46/<LANE>/` (A1 may edit the two named instrument
paths); PREREG.md first (addenda hash-stamped); every statistic ships with its plant and measured power; a
failed control means "uninformative"; leave `ledger_rows.json` (ids `R46-<LANE>-…`) + `RESULTS.md` + a
closing stamp; stdlib Python; never edit `LEDGER.json`; never commit.

## 3. Gate to close

All four lanes stamped; X1 ruled; the five gates green (`tests/validate.py`, `pytest -q -m "not network"`,
`check_consistency.py`, `check_ceiling.py`, ledger validator); nav docs updated; one coordinator commit.
