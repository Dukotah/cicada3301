import os, sys, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import enciphers as E
sys.path.insert(0, os.path.join(HERE, "..", "..", "round10", "L2-map"))
import mapcommon as M
B = E.B
LP2 = 0.66384
d = M.parse(); pages = [len(p) for p in d["pages"]]
lines = [len(l) for l in d["lines"] if l]
TEST = np.load(os.path.join(B.HERE, "models", "testhalves_lite.npz"))
a = TEST["EN_MODERN"].astype(np.int64)
L = sum(pages); NREP = 30
def lines_cover(): return lines
encs = {
 "keyskip1": lambda P, K, s: E.keyskip1(P, K, 0.83, s),
 "skip_by_two": lambda P, K, s: E.skip_by_two(P, K, 0.83, s),
 "reset_per_page": lambda P, K, s: E.encipher_reset_per_page(P, K, pages, 0.83, s),
 "reset_per_line": lambda P, K, s: E.encipher_reset_per_line(P, K, lines, 0.83, s),
 "skip_by_3": lambda P, K, s: E.encipher_skip_by_k(P, K, 3, 0.83, s),
 "skip_by_4": lambda P, K, s: E.encipher_skip_by_k(P, K, 4, 0.83, s),
 "skip_by_5": lambda P, K, s: E.encipher_skip_by_k(P, K, 5, 0.83, s)}
res = {}
for name, f in encs.items():
    rates = []
    for s in range(NREP):
        r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1)
        P = a[st:st + L].tolist()
        K = B.sha_ctr_key(L * 12 + 2048, seed=b"PRIOR%d" % s)
        C, _ = f(P, K, 3301 + s)
        rates.append(100 * sum(1 for i in range(1, len(C)) if C[i] == C[i-1]) / (len(C) - 1))
    m = float(np.mean(rates)); sd = float(np.std(rates))
    res[name] = {"mean_pct": round(m, 4), "sd_pct": round(sd, 4), "err_vs_LP2": round(abs(m - LP2), 4), "n_reps": NREP, "L": L}
    print(name, res[name], flush=True)
e2 = res["skip_by_two"]["err_vs_LP2"]
for k, v in res.items():
    v["err_ratio_vs_skip_by_two"] = round(v["err_vs_LP2"] / e2, 3) if e2 else None
    v["within_2x_of_skip_by_two_match"] = v["err_vs_LP2"] <= 2 * e2
json.dump({"LP2_observed_pct": LP2, "L": L, "supp": 0.83, "rows": res,
           "kill_rule_fired": not any(v["within_2x_of_skip_by_two_match"] for k, v in res.items() if k not in ("keyskip1", "skip_by_two"))},
          open(os.path.join(HERE, "doublet_priors.json"), "w"), indent=1)
