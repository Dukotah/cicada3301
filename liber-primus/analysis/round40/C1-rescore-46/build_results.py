import os, json
HERE = os.path.dirname(os.path.abspath(__file__)); F = lambda *a: os.path.join(HERE, *a)
S = json.load(open(F("rescore_summary.json"))); FAM = S["families"]; T = json.load(open(F("cell_table.json")))
KEY = {"R04": ["R04_M4_LP1_pointer"], "R06": ["R06_M6_structural_counts"], "R13": ["R13_R9_DIRECTION_walks_D800"], "R27": ["R27_R22A_selfembedded"], "R28": ["R28_R23A2_line_acrostic_ownhist"],
       "R30": ["R30_B1_artifact_keys"], "R10b": ["R30_B1_artifact_keys", "C18_numeric_PS_tweet_mayan"], "c18": ["C18_numeric_PS_tweet_mayan"], "R32": ["R32_B04_slogan_seeds", "R32_B04_lp_seeds_stageA"],
       "R33": ["R33_R26C_semantic_seed_zoo"], "R43": ["R43_B5_composed_keys"], "R47": ["R47_F01_LP2_as_pad"]}


def fam_line(fn):
    e = FAM[fn]
    if e["kind"] == "direct":
        return "%s: n=%d streams, D=%d; best %s pmax %.2f, Z %.2f, p(Z) %.4f, raw p %.4f" % (fn, e["n_streams"], e["D"], e["best_stream"], e["best_pmax"], e["best_Z"], e["p_family"], e["raw_best"]["p"])
    k = e["bar_key"]; b = e["bars"]; bn = e["best_nondegenerate"]
    return "%s: N=%s %s; best %.2f/%.2f vs actual-N %.2f/%.2f, declared %.2f/%.2f" % (fn, e.get("heads_screened") or e["rows"]["keyskip1"], "heads" if e.get("heads_screened") else "rows/rel", bn["keyskip1"]["pmax"], bn["keyskip2"]["pmax"],
                                                                                    b["keyskip1"][k], b["keyskip2"][k], b["keyskip1"]["declared_1e6"], b["keyskip2"]["declared_1e6"])


def fam_row(fn):
    e = FAM[fn]
    if e["kind"] == "direct":
        return "| %s | direct panel-R36 stream score (regen) | pass (Z %s) | %d streams / D=%d | pmax %.2f (Z %.2f, p(Z) %.4f, raw p %.4f) | direct | %s |" % (
            fn, "/".join("%.0f" % v["Z_plant"] for v in e["control"].values() if isinstance(v, dict)), e["n_streams"], e["D"], e["best_pmax"], e["best_Z"], e["p_family"], e["raw_best"]["p"], "see notes")
    k = e["bar_key"]; b = e["bars"]; bn = e["best_nondegenerate"]
    return "| %s | pf_v4_12 -> beam_v3 ks1+ks2 (regen) | pass 6/6 per rel | %s | %.3f / %.3f | actual-N %.2f / %.2f; declared %.2f / %.2f | negative |" % (
        fn, ("%s heads, %s decoded" % (format(e["heads_screened"], ","), e["survivors"])) if e.get("heads_screened") else ("%d rows/rel" % e["rows"]["keyskip1"]),
        bn["keyskip1"]["pmax"], bn["keyskip2"]["pmax"], b["keyskip1"][k], b["keyskip2"][k], b["keyskip1"]["declared_1e6"], b["keyskip2"]["declared_1e6"])


out = []
out.append(open(F("RESULTS_head.md"), encoding="utf-8").read())
out.append("\n## Per-family table (what was run)\n\n| family | artefact / route | control | N | best (non-degenerate; ks1 / ks2 for beam) | bars | verdict |\n|---|---|---|---|---|---|---|")
for fn in ("R30_B1_artifact_keys", "C18_numeric_PS_tweet_mayan", "R32_B04_slogan_seeds", "R32_B04_lp_seeds_stageA", "R33_R26C_semantic_seed_zoo", "R43_B5_composed_keys", "R47_F01_LP2_as_pad"):
    out.append(fam_row(fn))
out.append("")
out.append("| family | artefact / route | control | N | best | null | verdict |\n|---|---|---|---|---|---|---|")
for fn, verdict in (("R04_M4_LP1_pointer", "negative on the raw statistic (Z invalid: null sd 0 for length pointers)"), ("R06_M6_structural_counts", "negative"), ("R13_R9_DIRECTION_walks_D800", "NEAR-MISS (see below), not flagged"),
                    ("R13_R9_DIRECTION_walks", "first pass D=150 (superseded by D=800 / D=500)"), ("R13_R9_DIRECTION_walks_D500_seed50000", "replicate, other null seeds"), ("R27_R22A_selfembedded", "negative"),
                    ("R28_R23A2_line_acrostic", "lane null (order-shuffled letter pool): excess explained by natural English baseline"), ("R28_R23A2_line_acrostic_ownhist", "matched null: raw p 0.10, negative")):
    e = FAM[fn]
    out.append("| %s | regen, direct | pass | %d streams (%d below floor/degenerate excluded or counted), D=%d | pmax %.2f, Z %.2f | p(Z) %.4f, raw %.4f | %s |" % (
        fn, e["n_streams"], e.get("n_streams_total", e["n_streams"]) - e["n_streams"], e["D"], e["best_pmax"], e["best_Z"], e["p_family"], e["raw_best"]["p"], verdict))
out.append("\n## Per-cell table (46 cells)\n")
out.append("Verdict column: TRIED = every re-scorable reading in the cell's record re-scored (here or in R37-C3) with a passed control and no clearing row; PARTIAL = some reading inconclusive; UNCHANGED = nothing re-scorable. All re-scored readings are negative conditional on the three conditionals below.\n")
out.append("| cell | was | reading -> artefact (control, N, best vs bars) | verdict |\n|---|---|---|---|")
for t in T:
    parts = []
    seen = set()
    for r, st in t["readings"].items():
        if st.startswith("DONE-R37"):
            parts.append("%s: %s" % (r, st.split(": ", 1)[1]))
        elif st.startswith("RESCORED"):
            for fn in KEY.get(r, []):
                if fn in seen: continue
                seen.add(fn); parts.append("%s: %s" % (r, fam_line(fn)))
        elif st.startswith("NOT-RESCORABLE"):
            parts.append("%s: not re-scorable (%s)" % (r, st.split(": ", 1)[1]))
        else:
            parts.append("%s: INCONCLUSIVE (%s)" % (r, st.split(": ", 1)[1]))
    note = ""
    if "R13" in t["readings"]: note = " (R13 near-miss caveat)"
    out.append("| %s | %s | %s | %s%s |" % (t["cell"].replace("x", " x "), t["was"], "<br>".join(parts), t["new_status"], note))
open(F("RESULTS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n" + open(F("RESULTS_tail.md"), encoding="utf-8").read())
print("ok")
