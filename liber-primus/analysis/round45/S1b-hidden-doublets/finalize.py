"""R45/S1b — merge pass P, pass L, template and zoom outcomes into adjudications.json + stats.
Run after adjudicate.py, template.py, zoom.py:  PYTHONUTF8=1 python finalize.py"""
import json, os, sys
import numpy as np
from scipy.stats import beta
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "T1-t7-mechanism"))
import t1lib as T  # noqa: E402

def cp(k, n):
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [round(lo, 4), round(hi, 4)]

A = json.load(open(os.path.join(HERE, "adjudicate_raw.json"), encoding="utf-8"))
TM = json.load(open(os.path.join(HERE, "template.json"), encoding="utf-8"))
P, L = A["P"], A["L"]
bk = P["by_kind"]
sens = bk["C-dbl"]["said_same"]; spec = bk["C-fam"]["correct"]
stats = {
    "pairs_in_target": 1138, "lines_read": 56, "control_lines": 8,
    "passP_sensitivity_true_doublets": [sens, 30, cp(sens, 30)],
    "passP_specificity_lookalike_nondoublets": [spec, 30, cp(spec, 30)],
    "passP_gate_(>=27/30 both)": sens >= 27 and spec >= 27,
    "passP_decoys_correct": [bk["T-decoy"]["correct"], bk["T-decoy"]["n"]],
    "passP_target_family_said_same": [bk["T-fam"]["said_same"], bk["T-fam"]["n"]],
    "passL_control_doublets_read_equal": [L["ctrl_doublets_read_equal"], L["ctrl_doublets"],
                                          cp(L["ctrl_doublets_read_equal"], L["ctrl_doublets"])],
    "passL_glyph_class_agreement": [L["agree_cls"], L["glyphs"]],
    "template_validation": {f: [d["validation_correct"], d["validation_n"], cp(d["validation_correct"], d["validation_n"])]
                            for f, d in TM["families"].items()},
}
nval = sum(d["validation_n"] for d in TM["families"].values()); ncor = sum(d["validation_correct"] for d in TM["families"].values())
stats["template_validation_pooled"] = [ncor, nval, cp(ncor, nval)]
miss_P = 1 - stats["passP_sensitivity_true_doublets"][2][0]
miss_T = 1 - stats["template_validation_pooled"][2][0]
stats["miss_bound_family_pair_passP_alone_CP95"] = round(miss_P, 4)
stats["miss_bound_family_pair_template_per_glyph_CP95"] = round(miss_T, 4)
stats["miss_bound_family_pair_template_either_glyph"] = round(1 - (1 - miss_T) ** 2, 4)
miss_L = 1 - stats["passL_control_doublets_read_equal"][2][0]
stats["miss_bound_passL_doublet_CP95"] = round(miss_L, 4)

# T7 on canon (unchanged; no correction proposed)
D = T.load(); r = T.ac1(np.diff(D["ev"]).astype(float))
null = np.array(json.load(open(os.path.join(HERE, "..", "T1-t7-mechanism", "plants.json")))["null"]["S1"])
stats["T7_after"] = {"r": round(r, 4), "p": T.addone_two(null, r), "n_events": int(len(D["ev"])), "correction_applied": None}

cands = []
for t, c in TM["candidates"].items():
    cands.append({"t": int(t), "source": "passL read-equal/ambiguous-class and/or passP SAME", "canon": c["canon"],
                  "template_call": c["template_call"], "corr_to_means": c["corr_to_means"], "pair_corr": c["pair_corr"],
                  "verdict": "canon-confirmed (reader error)" if c["template_call"] == c["canon"] else "OPEN"})
count_checks = [
    {"gline": 147, "flag": "pass L saw an extra stem after box 10 (would make I,I)", "verdict": "canon-confirmed: no ink "
     "component there (zoom.json); the 'stem' was the stem of box 11 (F) truncated at the half-strip crop edge"},
    {"gline": 154, "flag": "pass L saw an extra stem between box 10 and 11", "verdict": "canon-confirmed: same crop-edge "
     "artifact (C at 1204 truncated by the 1212 crop edge); no extra component"},
    {"gline": 74, "flag": "segment count = canon-1; pass L saw a partial glyph before box 0", "verdict": "canon-confirmed: "
     "C and E touch (one 107-px component, over the segmenter's width filter); crop zoom_gl74_start.png reads C E IA O"},
    {"gline": 168, "flag": "segment count = canon-1; pass L read 20 glyphs, canon 21 (leading L)", "verdict": "canon-confirmed: "
     "the leading L is the page-15 drop cap (3 lines tall, zoom_dropcap_p15.png): stem + top branch, no right stem = L, "
     "not U, so no U,U doublet at t=3612"},
    {"gline": 152, "flag": "segment count = canon-1", "verdict": "canon-confirmed: C+B touching merged box (pass L read both)"},
    {"gline": 176, "flag": "segment count = canon-1", "verdict": "canon-confirmed: C+AE touching merged box (pass L read both)"},
    {"gline": 183, "flag": "segment count = canon-1", "verdict": "canon-confirmed: C+B touching merged box (pass L read both)"},
]
passP_rows = [{k: r[k] for k in ("id", "kind", "t", "canon_tok", "verdict", "read", "conf", "correct_samediff")} for r in P["rows"]]
out = {"frozen_read_sha256": A["frozen_read_sha256"], "stats": stats, "hidden_doublets_found": [],
       "count_errors_found": [], "lookalike_candidates": cands, "count_checks": count_checks,
       "passP": passP_rows,
       "passL_lines": [{k: r[k] for k in ("id", "kind", "gline", "start", "canon_len", "read_len", "nseg", "diff_ops",
                                         "read_equal_pairs", "ambiguous_class_pairs", "canon_doublets")} for r in L["rows"]]}
json.dump(out, open(os.path.join(HERE, "adjudications.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(stats, indent=1))
print([(c["t"], c["verdict"]) for c in cands])
