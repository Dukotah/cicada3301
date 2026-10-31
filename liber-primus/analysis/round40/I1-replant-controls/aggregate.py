import json, math, collections
REGS = ["EN_MODERN", "LATIN", "GREEK", "EN_NOVOWEL", "HEBREW"]
def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
raw = [json.loads(l) for l in open("results_raw.jsonl")]
G = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for x in raw:
    g = G[x["grp"]][x["reg"]]; g[0] += x["recover"]; g[1] += 1
direct = lambda *f: ["R37-C3-direct-" + a for a in f]
beam = lambda *f: ["R37-C3-beam-" + a for a in f]
ROWS = {
 "R37-C1-U1-CLUE-STRINGS": ["R37-C1-U1"],
 "R37-C1-U2-LP1-NUMBER-SCHEDULES": ["R37-C1-U2"],
 "R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION": ["R37-C1-U3"],
 "R38-C1-SEMANTIC-WORDNET": ["R38-C1"], "R38-C1-SEMANTIC-FREQRANK": ["R38-C1"],
 "R39-C1-SENSE-SIMILARITY": ["R39-C1"],
 "R38-C2-G1-CLAUSES-6-7": ["R38-C2-G1"], "R38-C2-G2-PRINTED-LINE-SUMS": ["R38-C2-G2"], "R38-C2-G3-LAGGED-POINTERS": ["R38-C2-G3"],
 "R37-C3-U5-L2-MAP": direct("U5_L2_M1_perpage", "U5_L2_M1_pooled", "U5_L2_M1_pooled_dfnull", "U5_L2_M2", "U5_L2_M5", "U5_L2_M9"),
 "R37-C3-U5-L3-ROAD": direct("U5_L3_T234", "U5_L3_T5"),
 "R37-C3-U6A-N1-CT": beam("N1ct") + direct("U6a_N1_pt"),
 "R37-C3-U6A-N2": direct("U6a_N2"),
 "R37-C3-U6A-N4": beam("N4ks") + direct("U6a_N4_read"),
 "R37-C3-U6A-N5": beam("N5"),
 "R37-C3-U6A-S1": direct("U6a_S1"), "R37-C3-U6A-S2": direct("U6a_S2"),
 "R37-C3-U6B-R22C": beam("X3b", "X4"),
}
out = {"rows": {}, "groups": {}, "n_notes": "power = recovered/planted per harness group; row power = the MINIMUM over the row's groups (conservative); Wilson 95%"}
for g, d in G.items():
    out["groups"][g] = {r: {"k": d[r][0], "n": d[r][1], "power": round(d[r][0] / d[r][1], 3), "wilson95": wilson(*d[r])} for r in REGS if r in d}
for row, groups in ROWS.items():
    res = {}
    for r in REGS:
        per = {g: G[g][r] for g in groups if r in G[g]}
        if not per: continue
        worst = min(per, key=lambda g: per[g][0] / per[g][1])
        k, n = per[worst]
        res[r] = {"power": round(k / n, 3), "k": k, "n": n, "wilson95": wilson(k, n), "limiting_group": worst, "all_groups": {g: "%d/%d" % tuple(v) for g, v in per.items()}}
    out["rows"][row] = res
json.dump(out, open("replant_results.json", "w"), indent=1)
for row, res in out["rows"].items():
    print(row, {r: "%s %s" % (v["power"], v["limiting_group"][-14:]) for r, v in res.items()})
