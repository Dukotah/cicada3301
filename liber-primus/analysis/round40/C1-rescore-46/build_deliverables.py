"""python build_deliverables.py  -> cell_table.json, cell_table.md, ledger.json, ledger_patches.json (from rescore_summary.json + cells_raw.json)."""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda *a: os.path.join(HERE, *a)
S = json.load(open(F("rescore_summary.json")))
cells = json.load(open(F("cells_raw.json")))
FAM = S["families"]

# reading -> status, families (part names) that carry it
DONE_R37 = {"R05": "R37-C3 U5-L2 M5 (p(Z) 0.327, raw p 0.64)", "R09": "R37-C3 U5-L2 M9 (p(Z) 0.392, raw p 0.156)", "R21": "R37-C3 U6a-S1 (p(Z) 0.48)",
            "R23": "R37-C3 U6b R22-C structural (p(Z) 0.75, raw 0.60)", "R24": "R37-C3 U6b R22-C X3 keyed (5.46 vs 6.04, ks1)"}
RESC = {"R04": ["R04_M4_LP1_pointer"], "R06": ["R06_M6_structural_counts"], "R13": ["R13_R9_DIRECTION_walks_D800", "R13_R9_DIRECTION_walks_D500_seed50000"],
        "R27": ["R27_R22A_selfembedded"], "R28": ["R28_R23A2_line_acrostic", "R28_R23A2_line_acrostic_ownhist"],
        "R30": ["R30_B1_artifact_keys", "C18_numeric_PS_tweet_mayan"], "R10b": ["R30_B1_artifact_keys", "C18_numeric_PS_tweet_mayan"], "c18": ["C18_numeric_PS_tweet_mayan"],
        "R32": ["R32_B04_slogan_seeds", "R32_B04_lp_seeds_stageA"], "R33": ["R33_R26C_semantic_seed_zoo"], "R43": ["R43_B5_composed_keys"], "R47": ["R47_F01_LP2_as_pad"]}
NOT_RESC = {"R08": "no adjudicator involved (longest word-length run statistic)"}
INCONC = {"R14": "campaign7 wordsum_selfkey code not committed", "R15": "campaign7 hill5_magic code not committed", "R31": "crib readouts are 5-9 runes (< panel floor); stored top-N absent; own T1 INCONCLUSIVE",
          "R35": "round12/C2/texts (33 key texts) not in repo; fetch.sh needs network", "R36": "dated public-pad data (NIST beacon / blocks) not committed; fetch needs network",
          "R44": "2012-14 book texts not committed as streams; English word-salad test only, no rune adjudicator"}

def reading_ids(rec):
    ids = re.findall(r"R\d+[a-z]?|c18", re.sub(r"\(.*?\)", "", rec))
    return ids

def fam_state(fn):
    e = FAM.get(fn)
    if not e: return None
    if e["kind"] == "direct":
        return {"kind": "direct", "best": e["best_stream"], "pmax": round(e["best_pmax"], 3), "Z": round(e["best_Z"], 2), "p_Z": round(e["p_family"], 4), "raw_p": round(e.get("raw_best", {}).get("p", float("nan")), 4),
                "n": e["n_streams"], "D": e["D"], "control": e["control_pass"], "both_p_lt_0.01": e["both_Z_and_raw_p_lt_0.01"]}
    keyN = e["bar_key"]
    return {"kind": "beam", "n_heads_or_rows": e.get("heads_screened") or e["rows"], "survivors": e.get("survivors"), "best": {r: round(e["best_nondegenerate"][r]["pmax"], 3) for r in ("keyskip1", "keyskip2")},
            "bar_actualN": {r: e["bars"][r][keyN] for r in ("keyskip1", "keyskip2")}, "bar_declared": {r: e["bars"][r]["declared_1e6"] for r in ("keyskip1", "keyskip2")},
            "clears_actualN": e["clears_actualN"], "n_degenerate": e["n_degenerate_rows"]}

table = []
for cell, rec in cells.items():
    rids = reading_ids(rec); st = {}
    for r in rids:
        if r in DONE_R37: st[r] = "DONE-R37: " + DONE_R37[r]
        elif r in RESC: st[r] = "RESCORED-R40: " + ", ".join(RESC[r])
        elif r in NOT_RESC: st[r] = "NOT-RESCORABLE: " + NOT_RESC[r]
        elif r in INCONC: st[r] = "INCONCLUSIVE: " + INCONC[r]
        else: st[r] = "UNMAPPED"
    anyscored = any(v.startswith(("DONE", "RESCORED")) for v in st.values()); anyinc = any(v.startswith("INCONCLUSIVE") for v in st.values())
    if anyscored and not anyinc: new = "TRIED"
    elif anyscored and anyinc: new = "PARTIAL-RESCORED"
    else: new = "UNCHANGED-" + ("T-EN" if rec.startswith("T-EN") else "T-LEG")
    table.append({"cell": cell, "was": rec.split(" ")[0], "record": rec, "readings": st, "new_status": new})
json.dump(table, open(F("cell_table.json"), "w"), indent=1)
cnt = {}
for t in table: cnt[t["new_status"]] = cnt.get(t["new_status"], 0) + 1
S2 = {"cells": len(table), "new_status_counts": cnt}
with open(F("cell_table.md"), "w", encoding="utf-8") as f:
    f.write("| cell | was | readings (status) | new |\n|---|---|---|---|\n")
    for t in table:
        f.write("| %s | %s | %s | **%s** |\n" % (t["cell"].replace("x", " x "), t["was"], "; ".join("%s=%s" % (k, v.split(":")[0]) for k, v in t["readings"].items()), t["new_status"]))
json.dump(S2, open(F("cell_counts.json"), "w"), indent=1)
print(S2)
exec(open(F("ledger_build.py"), encoding="utf-8").read())
