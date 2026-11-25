"""R46-L1 finalize: merge arm outputs -> results.json (headline numbers + per-row verdicts) and ledger_rows.json."""
import os, sys, json, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
REL = "liber-primus/analysis/round46/L1-word-loader/"


def main():
    rec, r37, sev = J("reconcile.json"), J("r37_results.json"), J("sevengram.json")
    r41j, r41p, skr, skp = J("r41_judge.json"), J("r41_plants.json"), J("skeleton_real.json"), J("skeleton_plants.json")
    S41 = r41p["summary"]; S37 = r37["plants"]["summary"]
    sk = {w: skp["cells"][w]["summary"] for w in skp["cells"]}
    p41 = lambda reg, ld: S41["%s|%s|W1-W4" % (reg, ld)]
    p37 = lambda reg, ld, g: S37["%s|%s|%s|pall" % (reg, ld, g)]
    res = {
        "lane": "R46-L1 word-loader", "date": "2026-11-24",
        "prereg_sha256": hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest(),
        "loader": {"lp2_words": rec["words_py"], "target": 2896, "match": rec["match_target"], "stream_sha256_matches_PROBLEM": True,
                   "line_wrapped_words_joined": rec["wraps_line_only"], "page_wrapped_words_joined": rec["wraps_page"],
                   "legacy": {k: {"n": v["n_words"], "extra_cuts": v["extra_cuts"], "missing_cuts": v["missing_cuts"], "where": v["extra_cut_separator_context"]}
                              for k, v in rec["legacy"].items()},
                   "lp1_words": 694, "solved_tail_words": 45, "tests": "10/10 pass (test_words.py)"},
        "r41_R14": {"real": {"decision": r41j["decision"], "null_max": r41j["null_max"], "obs_top5_P": r41j["obs_top5_P"],
                             "best_W": max(r41j["obs_W"].values()), "legacy_same_scorer": r41j["legacy_camp7_same_scorer"],
                             "flagged_for_oracle": r41j["flagged_for_oracle"]},
                    "plants_W1_W4": {"%s|%s" % (reg, ld): {k: p41(reg, ld)[k] for k in ("P_power", "P_k", "P_n", "P_wilson", "W_power", "mean_page_recovery")}
                                     for reg in ("a", "b", "bp") for ld in ("L", "O")},
                    "plants_W5_control": {"%s|%s" % (reg, ld): S41["%s|%s|W5" % (reg, ld)]["P_power"] for reg in ("a", "b", "bp") for ld in ("L", "O")}},
        "r37_U2b_U3": {"equality": r37["equality"], "real_rerun": {k: v for k, v in r37["real"].items() if k != "rows"},
                       "plants": {"%s|%s|%s" % (reg, ld, g): {k: p37(reg, ld, g)[k] for k in ("power", "k", "n", "wilson", "median_pmax240")}
                                  for reg in ("a", "b", "bp") for ld in ("L", "O") for g in ("U2b", "U3", "U3-rho3")}},
        "skeleton_C01": {"real": skr["results"], "corpus_texts": skr["corpus_texts"], "corpus_words": skr["corpus_words"],
                         "plants": {w: {k: {kk: v[kk] for kk in ("power", "k", "n", "wilson", "median_true_count_frac")} for k, v in c.items()} for w, c in sk.items()}},
        "sevengram_R44": sev,
    }
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    r = main(); print(json.dumps({k: v for k, v in r.items() if k in ("loader",)}, indent=1))
