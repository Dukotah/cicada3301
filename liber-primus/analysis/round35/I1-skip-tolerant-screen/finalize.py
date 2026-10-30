import json, os
H = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(H, "roc_matched.json"))); B = json.load(open(os.path.join(H, "roc_both.json")))
CP = json.load(open(os.path.join(H, "chosen_pen.json")))["chosen_pen"]
# frozen: k=2, m=24, 'both' at FPR 1e-3 (each component at 5e-4)
e = B["k2|m24|0.001"]
fz = {"m": 24, "k": 2, "rel": "both", "pen": CP["a1|k2|m24"], "pen_a1": CP["a1|k2|m24"], "pen_a2": CP["a2|k2|m24"],
      "thr": {"a1": e["thr"]["a1"], "a2": e["thr"]["a2"]}, "fpr_target_total": 1e-3, "fpr_heldout_measured": e["fpr_heldout"]}
json.dump(fz, open(os.path.join(H, "frozen_op.json"), "w"), indent=1)
json.dump({"matched_relation": M, "both_or_screen": B, "chosen_pen": CP,
           "note": "ratio_min = min over nine registers of held-out natural power / bar (0.85 NOVOWEL, 0.90 others); >=1 means bar met"},
          open(os.path.join(H, "roc.json"), "w"), indent=1)
pp = {"plants_per_register": 2000, "heldout_per_register": 1000, "frozen": fz,
      "frozen_power_both": B["k2|m24|0.001"],
      "matched_k2_m24": {a: M["%s|k2|m24" % a]["curves"]["0.001"] for a in ("a1", "a2")},
      "baseline_pf_v3_equivalent_k0_m20": {a: M["%s|k0|m20" % a]["curves"]["0.001"] for a in ("a1", "a2")}}
json.dump(pp, open(os.path.join(H, "power_per_register.json"), "w"), indent=1)
# print tables
REG = list(e["plants_keyskip1"]["natural"])
def row(d): return " ".join("%.3f" % d[r] for r in REG)
print(REG)
for rel in ("plants_keyskip1", "plants_keyskip2"):
    for nm in ("natural", "skip_free", "with_skip"): print("BOTH k2 m24", rel, nm, row(e[rel][nm]))
for a in ("a1", "a2"):
    c = M["%s|k2|m24" % a]["curves"]["0.001"]
    for nm in ("natural", "skip_free", "with_skip", "natural_no_cipher_doublet"): print("matched", a, nm, row(c[nm]))
    print("frac_with_skip", c["frac_with_skip"], "n with-skip NOVOWEL", c["with_skip_n"]["EN_NOVOWEL"], "thr", c["thr"], "fpr", c["fpr_heldout"], c["fpr_heldout_per_gen"])
    c0 = M["%s|k0|m20" % a]["curves"]["0.001"]
    for nm in ("natural", "skip_free", "with_skip"): print("k0 m20 baseline", a, nm, row(c0[nm]))
print(e["fpr_heldout"], e["fpr_heldout_per_gen"], e["thr"])
