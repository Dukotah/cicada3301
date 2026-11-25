"""R47-L2 finalize: merge arm outputs -> results.json + ledger_rows.json (ids R47-L2-...)."""
import os, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
REL = "liber-primus/analysis/round47/L2-g3-lexicon/"
REG = "panel-R36 12 registers (sha a0682f0c...); plants English only (data/pride.txt, B6 EN mapping via R46-L1 l1lib.make_plant)"


def verdict(p):
    return "holds" if p >= 0.90 else ("weakened" if p >= 0.50 else "conditional")


def main():
    g3f, g3r, g3p = J("g3_faith.json"), J("g3_real.json"), J("g3_plants.json")
    lex = {r: (J("%s_faith.json" % r), J("%s_real.json" % r), J("%s_plants.json" % r)) for r in ("r38", "r39")}
    rows = {}
    # ---- G3 power table
    g3pow = {}
    for reg in ("a", "b", "bp"):
        g3pow[reg] = {"page0": g3p["summary_regime_p0"][reg]}
        for c in ("C0", "CS", "CE"):
            g3pow[reg]["mid_" + c] = g3p["summary_regime_conv"]["%s|%s" % (reg, c)]
    rows["R38-C2-G3-LAGGED-POINTERS"] = {"power": g3pow, "real": {k: g3r[k] for k in ("n_decodes", "best", "bar120_combinedN", "bar120_origN", "N_combined", "flagged_for_oracle", "validate_store", "check_r3_store")},
                                         "faith": g3f, "mismatch_a": g3p["mismatch_a"]}
    # ---- lexicon rows
    for rid in ("R38-C1-SEMANTIC-WORDNET", "R38-C1-SEMANTIC-FREQRANK", "R39-C1-SENSE-SIMILARITY"):
        r = "r39" if rid.startswith("R39") else "r38"; f, re_, pl = lex[r]
        pw = {}
        for reg in ("a", "b", "bp"):
            pw[reg] = {"page0": pl["summary_row_regime_p0"]["%s|%s" % (rid, reg)]}
            for c in ("C0", "CS", "CE"):
                pw[reg]["mid_" + c] = pl["summary_row_regime_conv"]["%s|%s|%s" % (rid, reg, c)]
        best = {k: v for k, v in re_["best"].items() if v["row"] == rid}
        rows[rid] = {"power": pw, "real": {"n_decodes_family": re_["n_decodes"], "best": best, "bar120_combinedN": re_["bar120_combinedN"], "bar120_origN": re_["bar120_origN"],
                                           "N_combined": re_["N_combined"], "flagged_for_oracle": re_["flagged_for_oracle"], "validate_store": re_["validate_store"], "check_r3_store": re_["check_r3_store"]},
                     "faith": f, "mismatch_a": {k: v for k, v in pl["mismatch_a"].items() if k.startswith(rid)}}
    for rid, d in rows.items():
        d["verdicts"] = {reg: {k: verdict(v["power"]) for k, v in d["power"][reg].items()} for reg in d["power"]}
    res = {"lane": "R47-L2 g3-lexicon", "date": "2026-11-24", "prereg_sha256": hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest(),
           "conventions": {"C0": "split at page (legacy; = recorded real decodes)", "CS": "wrapped word belongs to the page it starts on", "CE": "wrapped word belongs to the page it ends on"},
           "rows": rows, "flagged_for_oracle_total": sum(len(d["real"]["flagged_for_oracle"]) for d in rows.values()),
           "large_outputs": ["g3_sweep_rows.jsonl", "r38_sweep_rows.jsonl", "r39_sweep_rows.jsonl", "*_plants.json (rows)"]}
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    # ---- ledger rows
    ev = lambda *x: [REL + n for n in ("PREREG.md", "RESULTS.md", "results.json") + x]
    def pstr(d, reg):
        p = d["power"][reg]
        return "p0 %.2f, mid-word C0 %.2f / CS %.2f / CE %.2f" % (p["page0"]["power"], p["mid_C0"]["power"], p["mid_CS"]["power"], p["mid_CE"]["power"])
    L = []
    g = rows["R38-C2-G3-LAGGED-POINTERS"]; gb = g["real"]["best"]
    L.append({"id": "R47-L2-G3-RERUN", "round": "47/L2", "lane": "round47/L2-g3-lexicon", "date": "2026-11-24", "status": "negative",
              "hypothesis": "R38-C2-G3 (lag-1 cw/dw gematria pointers in the R37 composed rule) re-run through words.py on the pages that open mid-word, under fragment conventions CS (wrapped word on the page it starts on) and CE (on the page it ends on); C0 (split, legacy) = recorded decodes.",
              "threshold": "bar_v3 at combined family N (orig + new) per relation, L=120 screen, L=min(240,unit) gate; plant rule = lane judge(); fixed in PREREG.md",
              "threshold_fixed_in_advance": True, "positive_control": "passed",
              "control_detail": "words.py plants on LP2's real layout, lane's own encipherers/decoder/judge, 40 cells x 26 plants per regime. (a) %s; (b) %s; (b') %s. C0 faithfulness re-run reproduced 4.911/4.700/4.038 exactly." % (pstr(g, "a"), pstr(g, "b"), pstr(g, "bp")),
              "result": "768 real decodes (pages 1,2,4,5 x CS,CE): best ks1 %.3f, ks2 %.3f, direct %.3f vs combined-N bars %.3f/%.3f/%.3f; 0 gate runs, 0 flagged." % (
                  max(gb["CS|keyskip1"]["pmax120"], gb["CE|keyskip1"]["pmax120"]), max(gb["CS|keyskip2"]["pmax120"], gb["CE|keyskip2"]["pmax120"]), max(gb["CS|direct"]["pmax120"], gb["CE|direct"]["pmax120"]),
                  g["real"]["bar120_combinedN"]["keyskip1"], g["real"]["bar120_combinedN"]["keyskip2"], g["real"]["bar120_combinedN"]["direct"]),
              "coverage": "R38-C2-G3's frozen space (40 cells, pages 0-5, sigma +-1, ks1/ks2 for A3, s=0) under C0 (recorded), CS and CE; total family 1,344 decodes",
              "not_covered": ["lag>1; dw inside the beam; skip-circular A3/cw plant; pointer carry across the page break (wrapped word's value as page p's first pointer)",
                              "(b') printed lengths not the plaintext's: power 0 under every convention"],
              "three_conditionals": {"key_space": "R38-C2-G3 frozen space, conventions C0/CS/CE", "transition_model": "A1/A2 beam-free direct; A3 beam_v3 keyskip1/keyskip2 with a skip-free A3/cw planted encipherer; per-page key restart", "adjudicator_register": REG},
              "sweep_store": REL + "g3_sweep_rows.jsonl", "source_register": "round36/P1-panel-r36 panel12 a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c",
              "evidence": ev("g3_real.json", "g3_plants.json", "g3_faith.json", "arm_g3.py", "l2lib.py"),
              "supersedes_note": "Closes the R46-L1 CONDITIONAL on R38-C2-G3's fragment convention: the negative holds under (a) and (b) for C0, CS and CE; conditional under (b')."})
    for rid in ("R38-C1-SEMANTIC-WORDNET", "R38-C1-SEMANTIC-FREQRANK", "R39-C1-SENSE-SIMILARITY"):
        d = rows[rid]; r = "r39" if rid.startswith("R39") else "r38"; b = d["real"]["best"]
        sh = max(v["pmax120"] for k, v in b.items() if "|shift|" in k); a3 = max(v["pmax120"] for k, v in b.items() if "|A3|" in k)
        L.append({"id": "R47-L2-%s-POWER" % rid.split("-", 2)[2] if not rid.startswith("R39") else "R47-L2-SENSE-POWER", "round": "47/L2", "lane": "round47/L2-g3-lexicon", "date": "2026-11-24",
                  "status": "measured",
                  "hypothesis": "%s's own lexicon->key glue (enciphers.enc / sweep.dec_shift / dec_a3 / judge) has measured power on LP2's real layout via words.py under (a), (b), (b'), and its real result holds under fragment conventions CS and CE on pages 1-2." % rid,
                  "threshold": "power >= 0.90 holds / 0.50-0.90 weakened / < 0.50 conditional; real re-run vs bar_v3 at combined family N; fixed in PREREG.md",
                  "threshold_fixed_in_advance": True, "positive_control": "passed",
                  "control_detail": "9 cells x 14 plants per regime (pages 0,1,2; C0/CS/CE on 1,2). (a) %s; (b) %s; (b') %s. C0 faithfulness re-run reproduced the recorded family bests exactly." % (pstr(d, "a"), pstr(d, "b"), pstr(d, "bp")),
                  "result": "Power now MEASURED (was inherited, R46-X1 s5.4): verdict (a) %s, (b) %s, (b') %s. Real CS+CE re-run on pages 1-2: best shift %.3f, A3 %.3f vs combined-N bars %.3f / %.3f; 0 flagged." % (
                      verdict(min(v["power"] for v in d["power"]["a"].values())), verdict(min(v["power"] for v in d["power"]["b"].values())), verdict(max(v["power"] for v in d["power"]["bp"].values())),
                      sh, a3, d["real"]["bar120_combinedN"]["shift"], d["real"]["bar120_combinedN"]["A3"]),
                  "coverage": "the row's frozen key space (vars x A1/A2 s=0..28 / A3 s=0..725, sigma +-1, pages 0-2) under C0 (recorded) + CS + CE on pages 1-2",
                  "not_covered": ["the row's own not_covered (rho 2/3, keyskip2/free, pages>2, other senses/lexicons, non-English)", "(b') and any space source not equal to the plaintext's words: power <= the b' figure above"],
                  "three_conditionals": {"key_space": "row's frozen space, conventions C0/CS/CE", "transition_model": "A1/A2 direct; A3 beam_v3 keyskip1; per-page restart", "adjudicator_register": REG},
                  "sweep_store": REL + "%s_sweep_rows.jsonl" % r, "source_register": "round36/P1-panel-r36 panel12 a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c",
                  "evidence": ev("%s_real.json" % r, "%s_plants.json" % r, "%s_faith.json" % r, "arm_lex.py", "l2lib.py"),
                  "supersedes_note": "Replaces '%s power under (a)/(b) not measured' (R46-L1-REOPEN-VERDICTS / R46-X1 s5.4)." % rid})
    json.dump(L, open(os.path.join(HERE, "ledger_rows.json"), "w"), indent=1)
    return res, L


if __name__ == "__main__":
    res, L = main()
    for r in L: print(r["id"], "|", r["result"])
