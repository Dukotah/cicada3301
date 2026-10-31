"""R41 I1 Q1b: judge control_raw.jsonl against the refit N=1e6 bars -> control.json.  python judge_control.py"""
import json, os, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "null_survivor12.json")))["cells"]; A = -math.log1p(-0.01)
import sys; sys.path.insert(0, os.path.join(HERE, "..", "..", "round34", "I1-v3-null")); sys.dont_write_bytecode = True
from bars_v3 import bar_v3
bar = lambda L, rel, N=1e6: bar_v3(N, L, rel, family="survivor12")                      # bar of record
bar_refit = lambda L, rel, N=1e6: S["L%d|%s" % (L, rel)]["mu"] + S["L%d|%s" % (L, rel)]["beta"] * math.log(N / A)
rows = [json.loads(l) for l in open(os.path.join(HERE, "control_raw.jsonl"))]
bars = {rel: {"L120": bar(120, rel), "L240": bar(240, rel)} for rel in ("keyskip1", "keyskip2")}
bars_refit = {rel: {"L120": bar_refit(120, rel), "L240": bar_refit(240, rel)} for rel in ("keyskip1", "keyskip2")}
refit_only_clear = {rel: {L: sum(1 for r in rows if r["rel"] == rel and r["prefilter_pass"] and r["pmax%d" % L] >= bars_refit[rel]["L%d" % L]) for L in (120, 240)} for rel in ("keyskip1", "keyskip2")}
tab = collections.OrderedDict(); fails = []
for reg in sorted(set(r["register"] for r in rows)):
    for rel in ("keyskip1", "keyskip2"):
        q = [r for r in rows if r["register"] == reg and r["rel"] == rel]
        c = {"n": len(q), "prefilter_pass": sum(r["prefilter_pass"] for r in q)}
        for L in (120, 240):
            ok = [r["prefilter_pass"] and r["pmax%d" % L] >= bars[rel]["L%d" % L] for r in q]
            c["clear_L%d_path" % L] = sum(ok)
            c["clear_L%d_given_prefilter" % L] = sum(1 for r in q if r["prefilter_pass"] and r["pmax%d" % L] >= bars[rel]["L%d" % L])
        c["joint_L120_L240_path"] = sum(1 for r in q if r["prefilter_pass"] and r["pmax120"] >= bars[rel]["L120"] and r["pmax240"] >= bars[rel]["L240"])
        c["recover240_ge90"] = sum(1 for r in q if r["prefilter_pass"] and r["recovery240"] >= .9 and r["pmax240"] >= bars[rel]["L240"])
        c["with_skip_head24"] = sum(r["with_skip_head24"] for r in q)
        c["min_pmax120"] = min([r["pmax120"] for r in q if r["prefilter_pass"]] or [None]); c["min_pmax240"] = min([r["pmax240"] for r in q if r["prefilter_pass"]] or [None])
        tab["%s|%s" % (reg, rel)] = c
        for L in (120, 240):
            if c["clear_L%d_path" % L] < 19: fails.append({"cell": "%s|%s|L%d" % (reg, rel, L), "clear_path": c["clear_L%d_path" % L], "of": c["n"], "prefilter_pass": c["prefilter_pass"], "clear_given_prefilter": c["clear_L%d_given_prefilter" % L]})
gate = len(fails) == 0
miss = [r for r in rows if not r["prefilter_pass"]]
out = {"design": "20 plants x 12 registers x 2 relations (bash 4.2 LP64/ILP32 alternating), enc_exact/enc_pair of testhalves-r36 text, only filter C[:40] doublet-free, 4096-seed chunk -> pf_v4_12 frozen -> v3 panel_max L=120 / L=240 under panel-R36",
       "bars_of_record_N1e6": bars, "bars_gumbel_refit_only_N1e6": bars_refit, "clear_count_vs_refit_only_bar_(of 240 per relation)": refit_only_clear, "gate_ge19_of_20_every_cell_both_L_path": gate, "cells_below_19": fails,
       "n_plants": len(rows), "prefilter_pass_total": sum(r["prefilter_pass"] for r in rows),
       "prefilter_misses_by_register": dict(collections.Counter(r["register"] for r in miss)), "prefilter_misses_with_skip": sum(r["with_skip_head24"] for r in miss),
       "by_cell": tab, "pooled_clear_L120_path": sum(c["clear_L120_path"] for c in tab.values()), "pooled_clear_L240_path": sum(c["clear_L240_path"] for c in tab.values()),
       "pooled_clear_L120_given_prefilter": sum(c["clear_L120_given_prefilter"] for c in tab.values()), "pooled_clear_L240_given_prefilter": sum(c["clear_L240_given_prefilter"] for c in tab.values())}
json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("gate_ge19_of_20_every_cell_both_L_path", "n_plants", "prefilter_pass_total", "pooled_clear_L120_path", "pooled_clear_L240_path", "pooled_clear_L120_given_prefilter", "pooled_clear_L240_given_prefilter", "prefilter_misses_by_register")}, indent=1))
for f in fails: print("BELOW19", f)
