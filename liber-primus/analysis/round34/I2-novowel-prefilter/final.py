import sys, os, json, random, time
import numpy as np
sys.dont_write_bytecode = True
MYDIR = os.path.dirname(os.path.abspath(__file__))
B1 = os.path.join(MYDIR, "..", "..", "round32", "B1-bash-random")
sys.path.insert(0, B1)
from common import *
import pf as PF1
sys.path.insert(0, MYDIR); import pf_v3
LMT = AD.panel().LMT.astype(np.float32)
roc = json.load(open(os.path.join(MYDIR, "roc.json")))["roc"]; norm = json.load(open(os.path.join(MYDIR, "_norm.json")))
REG = list(AD.panel().registers)
TH = np.load(os.path.join(LP, "analysis/round32/I2-multiregister-readjudication/models/testhalves.npz"))
rng = random.Random(77)
out = {"plants_per_register": 2000, "note": "no-skip heads = operative (real C[:40] has no doublets); fresh seed 77, independent of roc.json plants", "by_m": {}}
for m in (16, 20, 24):
    thr = pf_v3.FROZEN.get(m, roc[str(m)]["lse"]["0.001"]["thr"])
    pw = {}
    for r in REG:
        txt = TH[r].astype(np.int64)
        P = np.array([txt[s:s + m] for s in (rng.randrange(0, len(txt) - 200) for _ in range(2000))], dtype=np.int8).T
        p = float(pf_v3.screen(P, LMT, thr).mean())
        pw[r] = {"power": round(p, 4), "se": round((p * (1 - p) / 2000) ** .5, 4)}
    out["by_m"][m] = {"lse_thr_fpr1e-3": thr, "power": pw, "min_other": min(v["power"] for k, v in pw.items() if k != "EN_NOVOWEL"),
                      "novowel": pw["EN_NOVOWEL"]["power"], "fpr_by_gen": roc[str(m)]["lse"]["0.001"]["fpr_by_gen"],
                      "fpr_pooled_heldout": roc[str(m)]["lse"]["0.001"]["fpr_heldout"]}
    print(m, out["by_m"][m]["novowel"], out["by_m"][m]["min_other"], flush=True)
json.dump(out, open(os.path.join(MYDIR, "power_per_register.json"), "w"), indent=1)
# throughput: end-to-end on 2^18 bash seeds, best of 3
rs = random.Random(5)
sd = np.array([(rs.randrange(1325376000 >> 20, (1401580800 >> 20) + 1) << 20) | rs.randrange(1 << 20) for _ in range(1 << 18)], dtype=np.uint64)
C16 = np.array(U[:24], dtype=np.int8)
mu = np.array(norm["16"]["mu"], dtype=np.float32); sdv = np.array(norm["16"]["sd"], dtype=np.float32)
def run_pf():
    n = 0
    for i in range(0, len(sd), 65536):
        K = PF1.heads(sd[i:i + 65536], 16, "bash4.2")
        S = PF1.tri_stat((C16[:16, None] - K) % 29, LMT, mu, sdv).max(1); n += int((S > 3.5).sum())
def mk(m):
    def f():
        for i in range(0, len(sd), 65536): pf_v3.prefilter_mask(sd[i:i + 65536], "bash4.2", C16, LMT, m)
    return f
tp = {"n_heads": len(sd), "variant": "bash4.2", "single_process": True}
for name, f in (("pf_py_trigram_m16", run_pf), ("pf_v3_lse_m16", mk(16)), ("pf_v3_lse_m20", mk(20))):
    best = 1e9
    for _ in range(3):
        t = time.perf_counter(); f(); best = min(best, time.perf_counter() - t)
    tp[name] = {"sec": round(best, 3), "heads_per_s": round(len(sd) / best)}
for k in ("pf_v3_lse_m16", "pf_v3_lse_m20"): tp[k]["slowdown_vs_pf_py"] = round(tp[k]["sec"] / tp["pf_py_trigram_m16"]["sec"], 2)
json.dump(tp, open(os.path.join(MYDIR, "throughput.json"), "w"), indent=1); print(tp)
