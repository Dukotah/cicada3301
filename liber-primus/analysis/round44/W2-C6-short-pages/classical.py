"""W2-C6 step 3 (REAL READ, after Addendum 1) — p49 classical exhaust -> classical.json.

Full fixed attack (PREREG §3): dir {fwd,rev} x a {1,28} x [k<=3 full exhaust; k=4..8
unigram beam] = 157,532 candidates, all panel-R36 adjudicated vs the classical bar of
record. Any non-degenerate crosser -> FLAGGED-FOR-ORACLE. Top decodes persisted with full
R3 statistics.
"""
import json
import time

import numpy as np

import glue as S
import adjudicate as A

t0 = time.time()
pan = S.panel()
c = S.canon()
P = S.pages()
nulls = json.load(open("nulls.json"))
logq = S.en_unigram_logq()
bar = nulls["classical_bar_of_record"]

st, L = P[49]
x = c[st:st + L]
assert L == 66

n_total = 0
best = []          # keep global top-20 (pmax, config, key, decode)
crossers = []
per_cfg_best = []
for meta, dec in S.attack_candidates(x, logq):
    pm = A.adjudicate_batch(dec, pan=pan)["pmax"]
    n_total += len(dec)
    j = int(pm.argmax())
    per_cfg_best.append({"dir": meta["dir"], "a": meta["a"], "k": meta["k"],
                         "n": meta["n"], "best_pmax": round(float(pm[j]), 4)})
    order = np.argsort(pm)[::-1][:20]
    for i in order:
        best.append((float(pm[i]), meta["dir"], meta["a"], meta["k"],
                     [int(v) for v in meta["keys"][i]], [int(v) for v in dec[i]]))
    for i in np.where(pm >= bar)[0]:
        crossers.append((float(pm[i]), meta["dir"], meta["a"], meta["k"],
                         [int(v) for v in meta["keys"][i]], [int(v) for v in dec[i]]))

best.sort(key=lambda t: -t[0])
best = best[:20]
assert n_total == S.attack_total() == 157532, n_total

def full_row(t):
    pmv, d, a, k, key, dec = t
    r = A.adjudicate(np.asarray(dec, dtype=np.int64), pan=pan)
    return {"pmax": round(pmv, 4), "dir": d, "a": a, "k": k, "key": key,
            "translit": A.idx_to_trans(np.asarray(dec, dtype=np.int64)),
            "stats": {kk: (round(r[kk], 4) if isinstance(r[kk], float) else r[kk])
                      for kk in ("en", "pmax", "preg", "pmax_ne", "pcon", "ioc",
                                 "mds", "h2", "zl", "degenerate")}}

out = {"page": 49, "L": L, "bar_of_record": bar, "N_budget": S.N_CL,
       "n_adjudicated": n_total,
       "per_config_best": per_cfg_best,
       "global_best": [full_row(t) for t in best[:10]],
       "crossers": [full_row(t) for t in crossers],
       "n_crossers": len(crossers),
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open("classical.json", "w"), indent=1)
print("p49 classical: N=%d best=%.4f bar=%.4f crossers=%d" %
      (n_total, best[0][0], bar, len(crossers)))
for row in out["global_best"][:3]:
    print(row["pmax"], row["dir"], row["a"], row["k"], row["stats"]["degenerate"], row["translit"][:48])
