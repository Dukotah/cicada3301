"""Error-rate statistics for RESULTS.md (exact Clopper-Pearson, 0 or k errors). Output: stats.json"""
import json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "adjudications.json"), encoding="utf-8"))["rows"]
def cp_upper(k, n, a=0.05):
    lo, hi = 0.0, 1.0  # bisection on binomial cdf
    from math import comb
    cdf = lambda p: sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    for _ in range(100):
        m = (lo + hi) / 2
        (lo, hi) = (m, hi) if cdf(m) > a / 2 else (lo, m)
    return hi
def cp_lower(k, n, a=0.05):
    if k == 0: return 0.0
    from math import comb
    sf = lambda p: 1 - sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k))
    lo, hi = 0.0, 1.0
    for _ in range(100):
        m = (lo + hi) / 2
        (lo, hi) = (lo, m) if sf(m) > a / 2 else (m, hi)
    return lo
can = [r for r in rows if r["frame"] in ("F1", "F2", "F3", "F4")]
err = lambda rs: sum(1 for r in rs if r["verdict"] == "canon-error")
out = {}
for name, sel in [("F1", ["F1"]), ("F1+F4 uniform", ["F1", "F4"]), ("F2 doublet census", ["F2"]), ("F3 near-doublets", ["F3"]),
                  ("all canon glyphs", ["F1", "F2", "F3", "F4"])]:
    rs = [r for r in can if r["frame"] in sel]; k = err(rs); n = len(rs)
    out[name] = {"n": n, "errors": k, "ambiguous": sum("ambiguous" in r["verdict"] for r in rs),
                 "cp95": [round(cp_lower(k, n), 4), round(cp_upper(k, n), 4)]}
ctrl = [r for r in rows if r["frame"] == "C" and "verdict" in r]
kc = sum(r["verdict"] == "control-hit" for r in ctrl)
out["reader_controls"] = {"n": len(ctrl), "hits": kc, "cp95_lower_accuracy": round(1 - cp_upper(len(ctrl) - kc, len(ctrl)), 4)}
blind = [r for r in can if "unblinded" not in r["verdict"]]
mm = [r for r in blind if "reader error" in r["verdict"]]
out["reader_blind_on_canon_items"] = {"n": len(blind), "mismatches": len(mm),
    "agreement": round(1 - len(mm) / len(blind), 4),
    "mismatch_pairs": Counter(f'{r["crop_canon"]}->{r["blind_read"]}' for r in mm)}
out["verdicts"] = Counter(r["verdict"] for r in can)
json.dump(out, open(os.path.join(HERE, "stats.json"), "w"), indent=1, default=dict)
print(json.dumps(out, indent=1, default=dict))
