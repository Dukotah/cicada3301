import json
fin = json.load(open("sweep_summary_final.json")); idx = json.load(open("lp1_sense_index.json")); sh, a3 = fin["groups"]["shift"], fin["groups"]["A3"]
P = "analysis/round39/C1-sense-similarity/"
e = {"round": 39, "lane": "C1", "date": "2026-10-31", "id": "R39-C1-SENSE-SIMILARITY", "status": "negative", "threshold_fixed_in_advance": True,
 "positive_control": "passed (18/18 plants, 9/9 cells)", "sweep_store": P + "sweep_rows.jsonl",
 "source_register": "round36/P1-panel-r36 panel12 a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c",
 "hypothesis": "Direction for LP2 cipher words = WordNet 3.1 sense position (first-synset hypernym depth D; lexicographer-file index L, mod 29/28) of successive LP1 words ('their meaning is the road'), applied per-word, cumulatively, or as key-pointer advance in K0.",
 "coverage": "variants D (R28==R29 merged), L-R29, L-R28 x A1/A2 (s=0..28) and A3 (s=0..725 step 1), sigma +-1, pages 0-2, keyskip1, L=120 heads / L=240 gate, panel-R36; N=14112 (shift 1044, A3 13068)",
 "best_pmax_per_cell": {k: v["pmax"] for k, v in {**sh["per_cell_best"], **a3["per_cell_best"]}.items()},
 "best_overall_bars": {"shift": {"best": sh["best"]["pmax"], "bar_actualN": sh["bar_v3_actualN"], "bar_1e6": sh["bar_v3_N1e6"]}, "A3": {"best": a3["best"]["pmax"], "bar_actualN": a3["bar_v3_actualN"], "bar_1e6": a3["bar_v3_N1e6"]}},
 "evidence": [P + f for f in ("PREREG.md", "RESULTS.md", "control.json", "sweep_summary_final.json", "lp1_sense_index.json", "sweep_rows.jsonl")],
 "threshold": "bars_v3 + bar12 at actual N and N=1e6, L=120 screen / L=240 gate; fixed in PREREG.md before any build or decode",
 "not_covered": "senses beyond first synset; non-first hypernym paths; lexname-category depth (no hierarchy); other lexicons / similarity metrics (path, Lin, embeddings); rho=2/3; keyskip2/free; shift starts beyond 0..28; pages >2; heads beyond L=120/240; non-English plaintext; any non-frozen definition of 'meaning'"}
json.dump({"$comment": "Round 39 C1: bounded, definition-conditional negative; never solved/closed/exhausted. Not merged into LEDGER.json.", "lane": "C1", "entries": [e]}, open("ledger.json", "w"), indent=1)
json.dump({"$comment": "R39 C1 patches (not applied by the lane)", "patches": [{"id": "O4-MATRIX-H-F5", "cell": "H x F5 (meaning -> operation), last remaining cells", "set": {"status": "measured (bounded)", "superseded_by": ["R38-C1-SEMANTIC-WORDNET", "R38-C1-SEMANTIC-FREQRANK", "R39-C1-SENSE-SIMILARITY"], "not_covered": e["not_covered"]}}]}, open("ledger_patches.json", "w"), indent=1)
