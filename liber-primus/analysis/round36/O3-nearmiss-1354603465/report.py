#!/usr/bin/env python3
"""Aggregates cells.json / nulls.json / plant.json / verif_raw.json into verifiers.json, decode_text.md, curve.json (no decoding)."""
import os, sys, json, math
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))
from bars_v3 import bar_v3
J = lambda n: json.load(open(os.path.join(HERE, n)))
cells = J("cells.json")["rows"]; nul = J("nulls.json"); plant = J("plant.json"); vr = J("verif_raw.json"); rep = J("repro.json")
TR = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA"]
N_ACT, N_DECL = 69017, 10 ** 6
OBS = {"LP64_ks2_120": 7.068050415466602, "ILP32_ks2_120": 6.762366956470023}


def pot(x, obs, N):
    x = np.sort(np.asarray(x)); n = len(x); u = float(np.quantile(x, 0.9)); ex = x[x > u] - u
    beta = float(ex.mean()); pu = len(ex) / n
    p1 = pu * math.exp(-(obs - u) / beta) if obs > u else float((x >= obs).mean())
    fw = 1 - math.exp(-N * p1) if p1 < 1 else 1.0
    return {"n": n, "emp_exceed_count": int((x >= obs).sum()), "emp_exceed_frac": float((x >= obs).mean()), "emp_quantile_of_obs": float((x < obs).mean()),
            "null_median": float(np.median(x)), "null_q90": u, "null_q99": float(np.quantile(x, .99)), "null_q999": float(np.quantile(x, .999)), "null_max": float(x[-1]),
            "pot_beta": beta, "pot_per_draw_exceed": p1, "familywise_P_best_of_N_actual_ge_obs": (1 - math.exp(-N_ACT * p1)), "familywise_P_best_of_N_declared_ge_obs": (1 - math.exp(-N_DECL * p1)),
            "bar_pot_99pct_at_N_actual": u + beta * math.log(pu * N_ACT / -math.log(0.99)), "bar_pot_99pct_at_N_declared": u + beta * math.log(pu * N_DECL / -math.log(0.99))}


def sel(abi, rel, sign, L, **kw):
    return [r for r in cells if r["abi"] == abi and r["rel"] == rel and r["sign"] == sign and r["L"] == L and all(r[k] == v for k, v in kw.items())]


V = {}
col = lambda k, key="p9": [r[key] for r in nul[k]["rows"]]
# --- A
A = {}
A["L120_LP64_ks2"] = pot(col("A120"), OBS["LP64_ks2_120"], N_ACT)
A["L120_ILP32_ks2"] = pot(col("I120"), OBS["ILP32_ks2_120"], N_ACT)
A["L120_ks2_p12_check"] = pot(col("A120", "p12"), OBS["LP64_ks2_120"], N_ACT)
if "K1_120" in nul:
    A["L120_LP64_ks1"] = pot(col("K1_120"), 4.273283688284226, N_ACT)
reg_axis = {}
for L, key in ((262, "A262"), (729, "A729")):
    c0 = sel("bash4.2", "keyskip2", -1, L, o=0, c0=0)[0]["pmax9"]
    ax = [r["pmax9"] for r in sel("bash4.2", "keyskip2", -1, L) if (r["o"] == 0 or r["c0"] == 0)]
    A["L%d_LP64_ks2_obs_at_o0c0" % L] = pot(col(key), c0, N_ACT); A["L%d_LP64_ks2_obs_at_o0c0" % L]["obs"] = c0
    mx = max(ax); p = pot(col(key), mx, 1); p1 = p["pot_per_draw_exceed"]
    A["L%d_LP64_ks2_best_of_%d_axis_cells" % (L, len(ax))] = {"obs_best": mx, "n_cells": len(ax), "P_best_of_cells_ge_obs_pot": 1 - (1 - p1) ** len(ax), "emp_exceed_frac_per_cell": p["emp_exceed_frac"]}
if "FREE729B" in nul:
    nul["FREE729"]["rows"] = nul["FREE729"]["rows"] + nul["FREE729B"]["rows"]
for L, key in ((120, "FREE120"), (262, "FREE262"), (729, "FREE729")):
    if key in nul:
        for sign in (-1, 1):
            o = sel("bash4.2", "free", sign, L, o=0, c0=0)[0]["pmax9"]
            x = np.array(col(key)); A["free_L%d_sign%+d" % (L, sign)] = {"obs": o, "null_n": len(x), "null_median": float(np.median(x)), "null_max": float(x.max()), "emp_exceed_frac": float((x >= o).mean()),
                                                                          "null_regs": {r: col(key, "r9").count(r) for r in set(col(key, "r9"))}}
g = nul["GRID"]["rows"]; ba = np.array([r["best_all"] for r in g])
own = max(r["pmax9"] for r in cells if r["abi"] == "bash4.2" and r["L"] == 120 and r["rel"] in ("keyskip1", "keyskip2") and (r["o"] >= 0) and r["c0"] == 0)
A["grid_matched_L120_ks1ks2_sign_o0-28"] = {"seeds": len(ba), "own_best": own, "null_best_median": float(np.median(ba)), "null_best_max": float(ba.max()), "frac_null_seeds_ge_own": float((ba >= own).mean()),
                                              "own_best_cell": max((r for r in cells if r["abi"] == "bash4.2" and r["L"] == 120 and r["rel"] in ("keyskip1", "keyskip2") and r["c0"] == 0), key=lambda r: r["pmax9"])}
V["A_size_matched_null"] = A
# bars
V["bars_v3_lp2_ks2"] = {str(L): {"N_actual": bar_v3(N_ACT, L, "keyskip2"), "N_declared": bar_v3(N_DECL, L, "keyskip2")} for L in (120, 240, 262, 400, 729)}
V["bars_note"] = "L=262 interpolated in ln L between fit nodes; L=729 clamped to the L=400 node (extrapolated, unreliable). Verifier A's own null is the bar of record at 262/729."
# --- curve
curve = {}
for abi in ("bash4.2", "bash4.2_i32"):
    for rel in ("keyskip2", "keyskip1", "free"):
        for sign in (-1, 1):
            curve["%s|%s|%+d" % (abi, rel, sign)] = {str(r["L"]): [round(r["pmax9"], 3), r["reg9"], round(r["pmax12"], 3), r["reg12"]] for r in cells if r["abi"] == abi and r["rel"] == rel and r["sign"] == sign and r["o"] == 0 and r["c0"] == 0}
# best per (abi,rel,sign,L) over offset axes
bestax = {}
for r in cells:
    k = "%s|%s|%+d|%d" % (r["abi"], r["rel"], r["sign"], r["L"])
    if k not in bestax or r["pmax9"] > bestax[k]["pmax9"]: bestax[k] = {kk: r[kk] for kk in ("pmax9", "reg9", "pmax12", "reg12", "o", "c0")}
    bestax[k]["n"] = bestax[k].get("n", 0) + 1
curve_nulls = {}
for L, key in ((120, "A120"), (262, "A262"), (729, "A729")):
    x = np.array(col(key)); curve_nulls["ks2_L%d" % L] = {"median": float(np.median(x)), "q99": float(np.quantile(x, .99)), "q999": float(np.quantile(x, .999)), "max": float(x.max())}
for L, key in ((120, "FREE120"), (262, "FREE262"), (729, "FREE729")):
    if key in nul:
        x = np.array(col(key)); curve_nulls["free_L%d" % L] = {"median": float(np.median(x)), "q99": float(np.quantile(x, .99)), "max": float(x.max()), "n": len(x)}
V["curve_o0c0"] = curve; V["best_over_offsets"] = bestax; V["null_by_L"] = curve_nulls
# plant growth
V["plant_curve"] = {nm: {L: [round(v["pmax9"], 2), v["reg9"], round(v["pmax12"], 2), round(v["recovery"], 3), v["wordhits"]] for L, v in d.items()} for nm, d in plant.items()}
# --- B
segs = vr["B_segments"]; chain = vr["B_chained"]
nseg = [r["seg"] for r in nul["A729"]["rows"]]
modal_share = []; mean_seg = []
for r in nul["A729"]["rows"]:
    regs = [s[1] for s in r["seg"]]; modal_share.append(max(regs.count(q) for q in set(regs)) / 6); mean_seg.append(np.mean([s[0] for s in r["seg"]]))
cand_regs = [s["r9"] for s in segs]; cm = max(cand_regs.count(q) for q in set(cand_regs)) / 6; cmean = float(np.mean([s["p9"] for s in segs]))
lp1share_null = float(np.mean([sum(1 for s in r["seg"] if s[1] == "LP1_REAL") / 6 for r in nul["A729"]["rows"]]))
V["B_register_consistency"] = {"candidate_segments_L729_ks2": segs, "candidate_chained_120_windows": chain,
                               "candidate_modal_share": cm, "candidate_LP1_REAL_share": cand_regs.count("LP1_REAL") / 6, "candidate_mean_seg_pmax": cmean,
                               "null_seeds": len(modal_share), "null_modal_share_mean": float(np.mean(modal_share)), "null_frac_modal_share_ge_candidate": float(np.mean(np.array(modal_share) >= cm - 1e-9)),
                               "null_LP1_REAL_segment_share_mean": lp1share_null, "null_mean_seg_pmax_mean": float(np.mean(mean_seg)), "null_frac_mean_seg_pmax_ge_candidate": float(np.mean(np.array(mean_seg) >= cmean)),
                               "null_frac_seeds_with_LP1_REAL_in_ge4of6": float(np.mean([sum(1 for s in r["seg"] if s[1] == "LP1_REAL") >= 4 for r in nul["A729"]["rows"]])),
                               "chained_LP1_REAL_count": sum(1 for c in chain if c["r9"] == "LP1_REAL")}
ho = float(np.mean([x["p9"] for x in segs[1:]])); nho = [np.mean([q[0] for q in r["seg"][1:]]) for r in nul["A729"]["rows"]]
V["B_register_consistency"]["heldout_segments_1to5_mean_pmax"] = ho
V["B_register_consistency"]["null_heldout_segments_mean_median"] = float(np.median(nho)); V["B_register_consistency"]["null_frac_heldout_mean_ge_candidate"] = float(np.mean(np.array(nho) >= ho))
V["B_register_consistency"]["null_seg0_pmax_ge_7.068_count"] = sum(1 for r in nul["A729"]["rows"] if r["seg"][0][0] >= 7.068)
# --- C
a262 = nul["A262"]["rows"]; cand = vr["candidate"]
V["C_text_stats"] = {"candidate": {L: {k: v for k, v in r.items() if k not in ("text", "z9", "z12")} for L, r in cand.items()},
                     "null_L262": {"wordhits_median": float(np.median([r["wh"] for r in a262])), "wordhits_q99": float(np.quantile([r["wh"] for r in a262], .99)), "wordhits_max": max(r["wh"] for r in a262),
                                   "ioc_median": float(np.median([r["ioc"] for r in a262])), "ioc_q01": float(np.quantile([r["ioc"] for r in a262], .01)), "ioc_q99": float(np.quantile([r["ioc"] for r in a262], .99)),
                                   "mds_median": float(np.median([r["mds"] for r in a262])), "mds_q01": float(np.quantile([r["mds"] for r in a262], .01))},
                     "candidate_L262_wordhits_exceed_frac": float(np.mean([r["wh"] >= cand["262"]["wordhits"] for r in a262]))}
json.dump(V, open(os.path.join(HERE, "verifiers.json"), "w"), indent=1, default=float)
# --- decode_text.md
def wrap(s, w=100): return "\n".join(s[i:i + w] for i in range(0, len(s), w))
md = ["# decode_text.md - best decodes (rune indices -> R32 transliteration letters, lower-case, no word breaks) + calibration plant\n",
      "Candidate = bash 4.2 LP64 seed 1354603465, `%29`, keyskip2, sign -1, o=0, c0=0, beam_w 400, v3 panel_max. Plant = SAME seed/key, English test-half plaintext, enc_pair(supp .83), same pipeline.\n"]
for L in ("120", "240", "262", "729"):
    r = cand[L]
    md += ["\n## Candidate L=%s  pmax9 %.2f (%s)  pmax12 %.2f (%s)  n_skips %d  IoC*N %.3f  mds %s  h2 %.3f  zlib %.3f  wordhits %d\n" % (L, r["pmax9"], r["reg9"], r["pmax12"], r["reg12"], r["n_skips"], r["ioc"], r["mds"], r["h2"], r["zl"], r["wordhits"]),
           "Panel z (9): " + ", ".join("%s %.1f" % kv for kv in r["z9"].items()), "\n```\n" + wrap(r["text"] if L != "729" else r["text"][:600] + " ...[truncated at 600 letters]") + "\n```"]
for nm, d in plant.items():
    for L in ("120", "262"):
        r = d[L]
        md += ["\n## PLANT %s L=%s  pmax9 %.2f (%s)  pmax12 %.2f (%s)  recovery %.3f  wordhits %d\n" % (nm, L, r["pmax9"], r["reg9"], r["pmax12"], r["reg12"], r["recovery"], r["wordhits"]),
               "decode:\n```\n" + wrap(r["text"][:300]) + "\n```\ntruth:\n```\n" + wrap(r["plain_true_text"][:300]) + "\n```"]
open(os.path.join(HERE, "decode_text.md"), "w", encoding="utf-8").write("\n".join(md))
print(json.dumps({k: V[k] for k in ("A_size_matched_null", "B_register_consistency", "C_text_stats", "plant_curve", "bars_v3_lp2_ks2", "null_by_L")}, indent=1, default=float))
