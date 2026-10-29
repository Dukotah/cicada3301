# R32 / I2 - multi-register re-adjudication - PRE-REGISTRATION
_Written before any panel build or re-score in this lane. Binding: ARMADA-DOCTRINE.md._

Setup facts known at writing: `data/keys/welsh/welsh_mabinogion.txt`, `data/keys/mabinogion.txt` and
`data/kjv.txt` were all absent from disk. Restored as substitutes (see RESULTS.md); the panel is therefore a
REBUILD, not a byte reproduction, and must re-pass its own gate. The round19 code is copied into this lane dir
and run here, so nothing in round19/I2 is overwritten.

**Q1 recognizer.** Plant the correct key over held-out register text (second half of each corpus), encipher
under the pinned soft anti-repeat filter, beam-decode, pass to `adjudicate()`. Hit = panel `pmax` over the
matched-FP bar. Gate: power >= 0.90 for every register at L=120 (target 0.92), by `power.py` unchanged.
**Q2 prior.** Round18 L7-A (`analysis/round18/L7-redteam/RESULTS.md` A): legacy scorer power 0.33 Latin, 0.00
CY and NOVOWEL. Prior for re-scoring is "removes an unstated English-only conditional", NOT "finds a hit".
**Q3 bounded.** Re-score only survivors already stored on disk for B-04, R16-KDF, R16-PRNG, R17-PUBLIC-PAD.
No new decodes. Lanes with no stored decoded survivors are reported un-re-adjudicable.
**Q4 three conditionals.** key space unchanged; transition model unchanged; adjudicator = the axis repaired.
Extra conditional: survivor texts are scored as stored (rune/idx streams), length-matched bars from the round19
null at the nearest L.
**Q5 kill.** If any register < 0.90 power at L=120 after rebuild, drop/fix that register WITH CAUSE and do not
re-adjudicate through it. If CY substitute corpus fails, CY is dropped and listed in not_covered.
Thresholds fixed now: power >= 0.90; flag = pmax_ne above the round19 matched-FP bar (alpha_ref, from
out_null.json) at survivor length, noting the I3 contract/N correction (bar scales with N via k_eff).
Greek/Hebrew/Norse: stretch, not attempted unless cheap; default not_covered.
