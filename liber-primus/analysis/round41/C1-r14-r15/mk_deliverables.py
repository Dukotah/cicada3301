import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
EV = ["liber-primus/analysis/round41/C1-r14-r15/PREREG.md", "liber-primus/analysis/round41/C1-r14-r15/RESULTS.md",
      "liber-primus/analysis/round41/C1-r14-r15/result_R14.json", "liber-primus/analysis/round41/C1-r14-r15/result_R15.json"]
base = {"round": 41, "lane": "C1", "lane_dir": "C1-r14-r15", "date": "2026-10-31", "threshold_fixed_in_advance": True}
CT = "direct panel-R36 (round40 lib copied unchanged), standing matched null bars_matched.matched_shuffle blockperm 100/250/1000, D=1000 each; alpha 0.0025 per (family, level); decision p = max of the three block p's; crosses only if Z-family p AND raw p both <= alpha"
rows = []
def mk(i, status, hyp, pc, cd, res, cov, nc, ri, ev, notes, thr=CT):
    d = dict(base); d.update(id=i, status=status, hypothesis=hyp, positive_control=pc, control_detail=cd, threshold=thr, result=res, coverage=cov, not_covered=nc, reopens_if=ri, evidence=ev, notes=notes)
    rows.append(d)
mk("R41-C1-R14-WORDSUM-SELFKEY", "negative",
   "campaign7 wordsum_selfkey (W1..W5 word-gematria-sum self-keying, sign x atbash) decodes the unsolved LP2 text; cells H4xF3, L2xF3.",
   "passed", "planted-text analogue for EVERY one of the 20 variants x EN_MODERN/LATIN/EN_NOVOWEL (60 plants at level W, 60 at level P) enciphered with the exact inverse; exact recovery 1.000 asserted; 120/120 recognised (plant pmax > max of 3000 matched-null family bests; level W null max 4.62, level P 5.50). Archived-code copy reproduced campaign7's -6.897 and per-variant scores exactly.",
   "negative: level W (20 whole-stream variants) best pmax 2.705, decision p(Z)=0.538, p(raw)=0.374 (blocks 100/250/1000: Z 0.353/0.491/0.538, raw 0.368/0.374/0.366); level P (1,100 page units) best pmax 3.642, decision p(Z)=0.886, p(raw)=0.893. alpha 0.0025: no crossing.",
   "20 variants (W1-W5 x sign x atbash) x 55 unsolved pages, panel-R36 direct, 12 registers, matched null at page/region scale with word and page segmentation held.",
   "other prime tables, sum operators, word segmentations than the transcription's; skip-aware / doublet-aware variants; non-listed registers beyond plant-level EN_MODERN/LATIN/EN_NOVOWEL; key-sweep survivor bar not applicable (direct reading).",
   "a variant outside W1-W5 (different sum/segmentation) is defined, or a segmentation of LP2 other than the transcription's is shown to be the author's", EV, "Supersedes the inconclusive R14 reading in R40-C1-INCONCLUSIVE-R14 (premise 'code not committed' false; archive path used).")
mk("R41-C1-R15-HILL5-MAGIC", "negative",
   "the book's three printed matrices and r4nd0m phi variants (6 matrices x M, MT, Minv, MTinv) as Hill keys mod 29 decode the unsolved text; cell L15xF2.",
   "passed", "planted-text analogue for all 24 variants x 3 registers (72 plants per level, levels W and P) via the inverse matrix; exact recovery; 144/144 recognised (level W null max 3.92, level P 4.80). numpy Hill verified identical to archived apply_hill on all variants. Archived copy reproduced -6.873 and per-matrix scores exactly.",
   "negative: level W (24 whole streams) best pmax 2.443, decision p(Z)=0.641, p(raw)=0.749; level P (1,320 page units) best pmax 4.094, decision p(Z)=0.771, p(raw)=0.424. No crossing at alpha 0.0025.",
   "24 variants, whole and per page, panel-R36 direct, matched null (blockperm 100/250/1000).",
   "matrices as column/row key schedules, as permutations, or with word-number fills; block sizes other than the matrix order; other register coverage than plants.",
   "a matrix-derived key schedule (not block multiply) is defined", EV, "")
mk("R41-C1-R44-BOOKCIPHER-BOOKS-FOUND", "partially-run",
   "R44: LP numbers as pointers into Cicada's known books (bookcipher.py L1/L2/W1/W2/G over kjv, mabinogion, miltonPL, blake, agrippa).",
   "failed", "pre-registered pointer-crafted control (PREREG-ADDENDUM-1-R44) kill fired: first six L1 plants recovered 0.743-0.815 of target letters (< 0.90) because a 1..29-letter forward window cannot reach every target letter; per the addendum the scoring was NOT run.",
   "not scored. Artefact found: the 5 books and bookcipher.py are in analysis/bookcipher/; the premise 'books not committed' is false for them.",
   "verification only", "the 6 books of bookcipher_expand.py (liber_al, kybalion, blake_mhh, goetia_g, thunder, thomas_gnosis) are absent; R44 scoring under panel-R36 not run (control kill).",
   "a pointer-crafted control reaching >=0.90 recovery (e.g. a lookahead beyond one step, or a non-greedy craft) is pre-registered, then the 130-unit family is scored against the blockperm null", ["liber-primus/analysis/round41/C1-r14-r15/PREREG-ADDENDUM-1-R44.md", "liber-primus/analysis/round41/C1-r14-r15/run_r44.out", "liber-primus/analysis/bookcipher/bookcipher.py"],
   "Scripts run_r44.py ready; it exits before scoring.")
for rid, nm, st, nc, extra in [
    ("R41-C1-R31-CRIB-READOUTS-VERIFIED", "R31", "audit",
     "readouts of 5-9 runes cannot be scored by panel-R36 (floor 32); not scored.",
     "artefact is regenerable (round10b/B3-semantic-keys code, ~4 min); T1-RESULTS.json stores the top-50 readouts and top-15 promoted page decodes. The blocker is the instrument floor, not absence."),
    ("R41-C1-R35-KEYTEXTS-VERIFIED", "R35", "audit",
     "analysis/round12/C2/texts/ (33 texts; fetch.sh has 33 pg/url lines) is absent from the working tree, archive/ and corpus/; no distinctive-title file match; gitignored (.gitignore line 158). Not hash-pinned; sweep_summary.json of round26/B records no per-text hashes. data/keys/armada18-19 hold different texts.",
     "network re-fetch would be an unpinned new artefact; not run."),
    ("R41-C1-R36-DATED-PADS-VERIFIED", "R36", "audit",
     "R17 P1 (Bitcoin heights 0-303,726 data/*.bin) and P2 (NIST beacon v1 + random.org) data absent from working tree, archive/, corpus/; R24 C8 cache holds only a 2 KB timestamps.json. The 28 P3 table pads are regenerable and were re-decoded in R40-B3 (that part is not the dated pads).",
     "multi-GB network fetch; not run."),
    ("R41-C1-B1-43-AUTO-KEYS-VERIFIED", "R30 43 auto keys", "audit",
     "analysis/armada_osint/artifacts/raw/{2012..2017}.md absent (gitignored). Partial substitute: archive/corpus scream314_2012/2013/2014/2017 md (no 2015/2016). Of the 43 auto keys only MIDISCV (auto-2012-tick) and WORKING (auto-2013-caps) appear verbatim in b1_results.json; the substitute reproduces MIDISCV but not WORKING, so it is a different artefact and a regeneration would not be the same 43 keys.",
     "not run: key set cannot be reproduced.")]:
    mk(rid, st, "Verify whether the %s artefact is really absent (R40-C1 blocked-cell premise)." % nm, "n/a (no control run)", "verification-only row, no scoring performed",
       extra if nm == "R31" else nc, "searched working tree, archive/, corpus/ (Glob/Grep, in-repo only)", nc if nm != "R31" else "readouts below panel floor; promoted decodes use phase-flexible decode not re-scored",
       "artefact supplied/pinned" if nm != "R31" else "a short-string scorer with a measured control is built, or the promoted page decodes are re-scored as a separate lane",
       ["liber-primus/analysis/round41/C1-r14-r15/RESULTS.md"], "", thr="n/a (verification)")
    rows[-1]["status"] = "inconclusive"
json.dump({"$comment": "R41 C1 ledger rows (LEDGER.json schema)", "entries": rows}, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)

def p(i, **kw):
    d = {"id": i}; d.update(kw); return d
patches = [
 p("R40-C1-INCONCLUSIVE-R14", status="superseded", coverage_add="R41-C1: re-scored from archive code (verbatim copy, reproduces -6.897): 20 variants, panel-R36 direct, blockperm matched null 100/250/1000; negative, level W p(Z)/p(raw) 0.538/0.374; control 120/120. See R41-C1-R14-WORDSUM-SELFKEY.", status_note="superseded by R41-C1-R14-WORDSUM-SELFKEY (negative)", not_covered_replace="other sum operators/segmentations; skip-aware variants", reopens_if_replace="a variant outside W1-W5 is defined"),
 p("R40-C1-INCONCLUSIVE-R15", status="superseded", coverage_add="R41-C1: 24 Hill variants re-scored from archived code (reproduces -6.873); negative, level W p(Z)/p(raw) 0.641/0.749; control 144/144. See R41-C1-R15-HILL5-MAGIC.", status_note="superseded by R41-C1-R15-HILL5-MAGIC (negative)", not_covered_replace="matrices as key schedules/permutations/word-number fills", reopens_if_replace="a matrix-derived key schedule is defined"),
 p("R40-C1-INCONCLUSIVE-R31", coverage_add="R41-C1: premise corrected - readouts are regenerable (round10b/B3 code, ~4 min) and T1-RESULTS.json stores top-50 readouts + top-15 promoted decodes; blocker is the 32-rune panel floor.", status_note="stays inconclusive (instrument floor, not absent artefact)"),
 p("R40-C1-INCONCLUSIVE-R35", coverage_add="R41-C1: verified absent from working tree, archive/ and corpus/ (33 texts per fetch.sh; gitignored; not hash-pinned).", status_note="stays inconclusive"),
 p("R40-C1-INCONCLUSIVE-R36", coverage_add="R41-C1: verified absent (R17 P1 Bitcoin data and P2 NIST/random.org data; C8 cache only timestamps.json). The 28 P3 table pads are covered by R40-B3, not the dated pads.", status_note="stays inconclusive"),
 p("R40-C1-INCONCLUSIVE-R44", status="partially-run", coverage_add="R41-C1: premise partly false - the 5 books of bookcipher.py (kjv, mabinogion, miltonPL, blake, agrippa) and the code are in analysis/bookcipher/. Scoring attempted: pointer-crafted control kill fired (recovery 0.74-0.82 < 0.90), so not scored. The 6 books of bookcipher_expand.py are absent.", status_note="partially-run; control must be redesigned before scoring", not_covered_replace="expanded 6 books absent; scoring not run", reopens_if_replace="a pointer-crafted control reaching >=0.90 recovery is pre-registered"),
 p("R40-C1-R30-B1-ARTIFACT-KEYS", not_covered_add="R41-C1: the 43 auto keys are not reproducible: raw/{2012..2017}.md absent; scream314 year files in archive/corpus are a different artefact (reproduce MIDISCV, not WORKING)."),
]
json.dump({"$comment": "R41 C1 patches by real LEDGER.json ids; coordinator applies", "patches": patches}, open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)
moves = {"R36-O4-CLUE-COVERAGE.x1_r41_cell_moves": {"cells_to_TRIED_panel_R36": ["H4xF3", "L2xF3", "L15xF2"],
  "cells_unchanged_inconclusive": ["H7xF9", "H12xF7", "L12xF5", "L13xF5", "S1xF5"], "cells_still_PARTIAL": ["H2xF7", "H7xF4", "H8xF4"],
  "recount": {"before_R41_C1": {"TRIED": 35, "PARTIAL": 3, "unchanged": 8}, "after": {"TRIED": 38, "PARTIAL": 3, "unchanged": 5}},
  "note": "R14 (H4xF3, L2xF3) and R15 (L15xF2) were each the only reading of their cells; both re-scored negative with passed controls. Control passes: R14 120/120, R15 144/144. H12xF7 still unchanged (R44 control kill)."}}
json.dump(moves, open(os.path.join(HERE, "matrix_cell_moves.json"), "w"), indent=1)
print(len(rows), "rows")
