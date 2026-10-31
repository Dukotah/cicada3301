# exec'd inside apply_ledger.py
raw = jl("I2-x4-null/ledger.json")[0]
e = {"id": "R38-I2-X4-NULL", "round": 38, "lane": "I2", "lane_dir": "I2-x4-null", "date": "2026-10-31", "status": "measured", "type": raw.get("type"),
     "hypothesis": "A bespoke null for the data-dependent X4 key family (key re-derived from each doublet-matched LP2 shuffle) sets a higher bar than the bars transferred from random-key nulls, and re-judging the R37 C3 X4 rows against it changes no verdict.",
     "positive_control": "passed", "control_detail": raw["control"], "threshold": "empirical q99 of the family-max pmax over 60 non-degenerate rows per relation (L=120: 6.994 from 2,000 draws; L=240: 7.919/7.931 from 121 draws); fixed in PREREG before any null ran",
     "threshold_fixed_in_advance": True, "result": raw["result"] + "; " + raw["filter_audit"],
     "coverage": "L=120: 2,000 draws x 60 non-degenerate rows/rel; L=240: 121 analysed draws (the store holds 122); 12 X4 configs, offset 0, 6 page-start windows, keyskip1/2, panel-R36; real rows 72/rel/L (60 non-degenerate).",
     "not_covered": "L=240 null of 2,000 draws; offsets > 0; other windows; the free relation; N4/N5-class data-dependent keys (C2 has a fixed-config matched null only); 8 of 12 X4 configs cannot carry a general plaintext (|image| 20-21 of 29) and 2 are constant maps",
     "three_conditionals": {"key_space": "X4: K[i]=f(S[i]) mod 29, f in prime value / prime index / totient, letters S or atbash(S), sign +-1; 12 configs; 6 windows", "transition_model": "beam_v3 keyskip1 + keyskip2", "adjudicator_register": "panel-R36 12 registers; plants EN_MODERN/LATIN/GREEK on the 2 bijective configs only"},
     "reopens_if": "an X4-class family with a general-purpose map is needed at other offsets, or the L=240 null is extended to 2,000 draws",
     "evidence": [PFX + "I2-x4-null/" + x for x in ("RESULTS.md", "PREREG.md", "null_x4.json", "control.json", "rejudged.json", "filter_audit.json", "null_rows_L120.jsonl", "null_rows_L240.jsonl")],
     "lane_ledger_raw": raw, "x1_r38": CFG["i2"]}
add(e)
for pid in ("R22-C-LITERAL-IMPERATIVES", "R37-C3-U6B-R22C"):
    byid[pid]["r38_i2"] = ("R38 I2: the transferred actual-N bars undercut the true X4 null (bespoke q99 6.994 vs 5.69 at L=120; 7.92 vs 6.04 at L=240); 0 of 120 non-degenerate X4 rows clear at either L (best 4.779 / 5.455, family-wise p 0.87 / 0.98); "
                           "the degenerate filter removes only the two constant-decode configs (raw 8.70 / 12.40 = recognizer failure). Verdict negative, unchanged; the L=240 null is partial (121 draws).")
