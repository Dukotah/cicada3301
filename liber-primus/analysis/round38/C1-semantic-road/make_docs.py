import json
man = json.load(open("lexicon_manifest.json")); fin = json.load(open("sweep_summary_final.json"))
base = {"round": 38, "lane": "C1", "date": "2026-10-30", "threshold_fixed_in_advance": True, "positive_control": "passed (36/36 plants, 18/18 cells)",
        "sweep_store": "analysis/round38/C1-semantic-road/sweep_rows.jsonl", "source_register": "round36/P1-panel-r36 panel12 a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c",
        "evidence": ["analysis/round38/C1-semantic-road/PREREG.md", "analysis/round38/C1-semantic-road/RESULTS.md", "analysis/round38/C1-semantic-road/control.json", "analysis/round38/C1-semantic-road/sweep_summary_final.json", "analysis/round38/C1-semantic-road/lexicon_manifest.json", "analysis/round38/C1-semantic-road/sweep_rows.jsonl"],
        "threshold": "bars_v3 + bar12 at actual N and N=1e6, L=120 screen / L=240 gate; fixed in PREREG.md before any download or decode"}
sh, a3 = fin["groups"]["shift"], fin["groups"]["A3"]
ents = []
for res, rid, name, hyp in (("A", "R38-C1-SEMANTIC-WORDNET", "WordNet 3.1 first-synset offset", "Direction for the LP2 cipher words = reduction (mod 29 / mod 28 / digit-sum mod 29) of the WordNet 3.1 first noun/verb/adj synset offset of the successive LP1 words ('their meaning is the road'), applied per-word, cumulatively, or as key-pointer advance in the LP1 rune stream."),
                         ("B", "R38-C1-SEMANTIC-FREQRANK", "Norvig top-50000 frequency rank", "Same, with the word's frequency rank (Norvig count_1w top 50000; unknown = 50001) as the meaning value.")):
    cells = {k: v["pmax"] for k, v in {**sh["per_cell_best"], **a3["per_cell_best"]}.items() if k.startswith(res + "-")}
    e = dict(base); e.update({"id": rid, "status": "negative", "hypothesis": hyp,
        "coverage": "3 reductions x A1/A2 (s=0..28, sigma +-1, pages 0-2: 348 decodes each) and A3 (s=0..725 step 1, sigma +-1, pages 0-2: 4356 decodes each); keyskip1 only; L=120 head, panel-R36 12 registers; 6 value variants total N=28224 (shift 2088, A3 26136)",
        "best_pmax_per_cell": cells, "best_overall_bars": {"shift": {"best": sh["best"]["pmax"], "bar_actualN": sh["bar_v3_actualN"], "bar_1e6": sh["bar_v3_N1e6"]}, "A3": {"best": a3["best"]["pmax"], "bar_actualN": a3["bar_v3_actualN"], "bar_1e6": a3["bar_v3_N1e6"]}},
        "not_covered": "other senses than first synset; other lexicons/frequency lists; lemmatiser variants; rho=2,3 (d indexed by word index only); keyskip2/free; pages >2; shift-mode starts beyond 0..28; meaning as dictionary semantics under any non-frozen definition; non-English plaintext", "lexicon": man["resource_A" if res == "A" else "resource_B"]})
    ents.append(e)
json.dump({"$comment": "Round 38 C1: bounded, definition-conditional negatives; never solved/closed/exhausted. Not merged into LEDGER.json by the lane.", "lane": "C1", "entries": ents}, open("ledger.json", "w"), indent=1)
json.dump({"$comment": "R38 C1 patches (not applied by the lane)", "patches": [{"id": "O4-MATRIX-H-F5", "cell": "H x F5 (meaning -> operation)", "set": {"status": "measured (bounded)", "raw_status": "was NEVER; now run under a frozen lore-free definition", "superseded_by": ["R38-C1-SEMANTIC-WORDNET", "R38-C1-SEMANTIC-FREQRANK"],
 "not_covered": "senses beyond first synset, other lexicons/frequency lists, rho=2/3, keyskip2/free, pages>2"}}]}, open("ledger_patches.json", "w"), indent=1)
