import json, os
HERE = os.path.dirname(os.path.abspath(__file__))


def row(i, t, cov, res, nc):
    return {"round": 38, "lane": "C2", "date": "2026-10-30", "id": i, "status": "negative", "hypothesis": t, "coverage": cov, "result": res, "positive_control": "passed",
            "threshold_fixed_in_advance": True, "evidence": ["analysis/round38/C2-never-cells/PREREG.md", "analysis/round38/C2-never-cells/RESULTS.md"],
            "three_conditionals": {"key_space": cov, "transition_model": "beam_v3 keyskip1+keyskip2 (direct modes beam-free), L120/L240", "adjudicator_register": "panel-R36 12 registers; EN_MODERN-only planted control"},
            "not_covered": nc}


E = [row("R38-C2-G1-CLAUSES-6-7", "Clauses 6/7 of the 2016 message as seeds on direct/SHA-CTR/PBKDF2", "384 decodes: 2 clauses x forms x 3 routes x rel x sign x off 0..7", "best 4.259/4.323 vs bar 5.99/5.91 at actual N", "free relation; other KDFs; atbash; offsets>7"),
     row("R38-C2-G2-PRINTED-LINE-SUMS", "Printed-line gematria sums (60 lines, 6 solved pages) as U2 key schedule", "768 decodes: additive+pointer, prime/index, mod 29/28, 3 heads", "best 4.567/4.537 vs 6.25/6.16", "other page orders; per-page restarts; phi channel"),
     row("R38-C2-G3-LAGGED-POINTERS", "Lag-1 cipher-word and decoded-word gematria pointers in the composed rule", "576 decodes: cw A1/A2/A3, dw A1/A2; A3 control skip-free", "best 4.911 (ks1), direct 4.038 vs 5.73/6.25", "dw inside the beam; lag>1; s>0; skip-circular A3 plant"),
     row("R38-C2-N5N4-L240", "Top-50 N5 and N4 rows of C3-R37 re-run at L=240", "200 decodes; screen N 2320/168", "N5 7.446, N4 8.572: above bars_v3 at screen N, inside matched cipher-derived-key null (p .74-.78 / .16), below N=1e6 bar; flagged-for-oracle bundle (expected NOISE-CROSSER)", "full two-stage matched null (fixed-config D=22/30 only); second page / held-out clause"),
     row("R38-C2-NEVER-CELLS-RUN", "Seven NEVER cells with a literal operation: H5xF1, H6xF2, L8xF6, L15xF6/F7, L17xF7, L4xF3", "~1,730 decodes + 5,760 hashes + one word-primality measurement", "all below bars/null; no hash match", "see RESULTS cell conditionals")]
json.dump({"lane": "C2", "date": "2026-10-30", "entries": E}, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)
P = {"patches": [
    {"id": "O4-matrix", "set": {"never": 19, "tried": 38, "t_en": 21, "t_leg": 25, "part": 3, "no_operation_stated": 34},
     "cells_to_TRIED": ["H5xF1", "H6xF2", "L8xF6", "L15xF6", "L15xF7", "L17xF7", "L4xF3"],
     "cells_to_C1_R38": [c + "xF5" for c in "H1 H2 H3 H4 H5 H8 H9 H10 L1 L2 L4 L5 L7 L8 L9 L10 L11 L14 L18".split()], "cells_no_operation_stated": "closed_no_operation.md (34)"},
    {"id": "R37-C1-U1-CLUE-STRINGS", "set": {"not_covered_remove": "clauses 6/7 of the 2016 message", "superseded_by": ["R38-C2-G1-CLAUSES-6-7"]}},
    {"id": "R37-C1-U2-LP1-NUMBER-SCHEDULES", "set": {"not_covered_remove": "printed LP1 line layout", "superseded_by": ["R38-C2-G2-PRINTED-LINE-SUMS"]}},
    {"id": "R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION", "set": {"not_covered_remove": "pointer from the ciphertext word's gematria (lag 1)", "not_covered_keep": "decoded-word pointer inside the beam; lag>1",
                                                            "superseded_by": ["R38-C2-G3-LAGGED-POINTERS"]}}], "new_rows": "ledger.json"}
json.dump(P, open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)
print("ok")
