"""Collect stored decoded survivors (translit strings) from historical-negative result files."""
import json, glob, os, sys
A = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # analysis/round32 -> analysis
A = os.path.abspath(os.path.join(A, ".."))
LANES = {
 "B-04": ["round13/B04/results_[ABCD].json"],
 "R16-KDF": ["round16/KDF/results_A.json"],
 "R16-PRNG": ["round16/prng/results.json"],
 "R17-PUBLIC-PAD": ["round17/P*/results*.json"],
}
TXT = ("head", "text", "translit")
def walk(x, path, out, src):
    if isinstance(x, dict):
        for k in TXT:
            v = x.get(k)
            if isinstance(v, str) and len(v) >= 12 and v.replace(" ", "").isalpha() and v.upper() == v:
                sc = x.get("score", x.get("best", x.get("score_norm")))
                out.append({"src": src, "path": path, "field": k, "text": v, "legacy_score": sc if isinstance(sc,(int,float)) else None})
        for k, v in x.items(): walk(v, path + "/" + str(k), out, src)
    elif isinstance(x, list):
        for i, v in enumerate(x): walk(v, path + f"[{i}]", out, src)
def collect():
    res = {}
    for lane, pats in LANES.items():
        out = []
        for p in pats:
            for f in sorted(glob.glob(os.path.join(A, p))):
                walk(json.load(open(f, encoding="utf-8")), "", out, os.path.relpath(f, A).replace("\\", "/"))
        # de-dup by (src, text)
        seen = set(); u = []
        for r in out:
            k = (r["src"], r["text"])
            if k not in seen: seen.add(k); u.append(r)
        res[lane] = u
    return res
if __name__ == "__main__":
    r = collect()
    for l, v in r.items():
        print(l, len(v), sorted({x["src"] for x in v})[:12], [len(x["text"]) for x in v[:5]])
        if v: print("  e.g.", v[0])
