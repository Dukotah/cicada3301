"""R44 / W2-A1 step 1 — build the short-stream null (PREREG §3) -> short_null.json.

Families (seed 3301), 1000 surrogates each through the FULL 116-map grid:
  SEL  sorted uniform position selections from canon (order-preserving selection)
  WIN  contiguous canon windows
L nodes {13, 26, 30, 40, 120}.  POT exponential fit above the 90th pct; bar at N=600,
alpha=0.01; bar of record per L = max over the two families.  L=120 cross-checked vs
bars_v3 free (sanity, not identity: different null population by design).
"""
import json
import time

import numpy as np

import shortnull as S
import bars_v3 as B

N_SURR = 1000
t0 = time.time()
rng = np.random.default_rng(S.SEED)
pan = S.panel()
c = S.canon()
out = {"seed": S.SEED, "n_surrogates": N_SURR, "grid_size": 116,
       "N_budget": S.N_BUDGET, "alpha": S.ALPHA, "nodes": {}}

for L in S.L_NODES:
    node = {}
    for fam in ("SEL", "WIN"):
        pmaxes = np.empty(N_SURR * 116)
        for i in range(N_SURR):
            if fam == "SEL":
                posn = np.sort(rng.choice(len(c), size=L, replace=False))
                x = c[posn]
            else:
                a = int(rng.integers(0, len(c) - L))
                x = c[a:a + L]
            pm, _, _, _ = S.grid_pmax(x, pan)
            pmaxes[i * 116:(i + 1) * 116] = pm
        u, p_u, beta, n_exc = S.pot_fit(pmaxes)
        bar = S.pot_bar(u, p_u, beta)
        node[fam] = {"u": round(u, 4), "p_u": round(p_u, 5), "beta": round(beta, 5),
                     "n_exceed": n_exc, "bar": round(bar, 4),
                     "emp_q999": round(float(np.quantile(pmaxes, 0.999)), 4),
                     "emp_max": round(float(pmaxes.max()), 4)}
    node["bar_of_record"] = max(node["SEL"]["bar"], node["WIN"]["bar"])
    out["nodes"][str(L)] = node
    print(L, node["bar_of_record"], node, flush=True)

out["bars_v3_free_120_at_N600"] = round(B.bar_v3(S.N_BUDGET, 120, "free"), 4)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("short_null.json", "w"), indent=1)
print("bars of record:", {L: out["nodes"][str(L)]["bar_of_record"] for L in S.L_NODES})
print("bars_v3 free@120,N600 cross-check:", out["bars_v3_free_120_at_N600"])
