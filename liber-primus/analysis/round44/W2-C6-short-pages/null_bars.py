"""W2-C6 step 1 — bespoke short-page nulls -> nulls.json (PREREG §3).

SEL + WIN-U x 1000 surrogates x 116-map grid at L in {66,76,85,92,95};
VIGK (L=66): 1000 WIN-U surrogates x 116 random classical configs;
ATTSEL (L=66): the FULL classical attack on 20 WIN-U surrogates, all candidates adjudicated.
POT fit per family; bars at N_DIRECT, N_CL and every lane N; bars_v3 keyskip cross-check.
"""
import json
import time

import numpy as np

import glue as S
import bars_v3 as B

t0 = time.time()
rng = np.random.default_rng(S.SEED)
pan = S.panel()
c = S.canon()
cu = c[:S.UNSOLVED_END]
logq = S.en_unigram_logq()

out = {"seed": S.SEED, "alpha": S.ALPHA, "N_direct": S.N_DIRECT, "N_cl": S.N_CL,
       "attack_total": S.attack_total(), "nodes": {}, "families_L66_extra": {}}

NS = 1000


def surr(fam, L):
    if fam == "SEL":
        return c[np.sort(rng.choice(len(c), size=L, replace=False))]
    a = int(rng.integers(0, len(cu) - L))
    return cu[a:a + L]


# ---- SEL / WIN-U at all nodes
for L in S.L_NODES:
    node = {}
    for fam in ("SEL", "WINU"):
        pm = np.empty(NS * 116)
        for i in range(NS):
            x = surr(fam, L)
            pm[i * 116:(i + 1) * 116] = S.grid_pmax(x, pan)[0]
        u, p_u, beta, nx = S.pot_fit(pm)
        node[fam] = {"u": round(u, 4), "p_u": round(p_u, 5), "beta": round(beta, 5),
                     "n_exceed": nx, "bar_N600": round(S.pot_bar(u, p_u, beta, S.N_DIRECT), 4),
                     "emp_q999": round(float(np.quantile(pm, 0.999)), 4),
                     "emp_max": round(float(pm.max()), 4)}
    node["bar_of_record_N600"] = max(node["SEL"]["bar_N600"], node["WINU"]["bar_N600"])
    # re-adjudication bars at every lane N (max over SEL/WIN-U at that N)
    readj = {}
    for lane, d in S.LANES.items():
        for tag, NN in (("page", d["N_page"]), ("lane", d["N_lane"])):
            bar = max(S.pot_bar(node[f]["u"], node[f]["p_u"], node[f]["beta"], NN)
                      for f in ("SEL", "WINU"))
            readj["%s|%s|N=%d" % (lane, tag, NN)] = round(bar, 4)
    node["readj_bars"] = readj
    # bars_v3 keyskip cross-check (lp2 family), reported not bar-of-record
    node["bars_v3_keyskip_crosscheck"] = {
        "%s|N=%d" % (lane, d["N_page"]): {
            r: round(B.bar_v3(d["N_page"], L, r), 4) for r in ("keyskip1", "keyskip2")}
        for lane, d in S.LANES.items()}
    out["nodes"][str(L)] = node
    print(L, "bar600", node["bar_of_record_N600"], flush=True)

# ---- VIGK at L=66
L = 66
pm = np.empty(NS * 116)
for i in range(NS):
    x = surr("WINU", L)
    dec = np.empty((116, L), dtype=np.int64)
    for j in range(116):
        k = int(rng.integers(2, 9))
        a = int(rng.choice([1, S.N - 1]))
        v = x[::-1] if rng.integers(2) else x
        s = rng.integers(0, S.N, size=k)
        dec[j] = (a * v + s[np.arange(L) % k]) % S.N
    import adjudicate as A
    pm[i * 116:(i + 1) * 116] = A.adjudicate_batch(dec, pan=pan)["pmax"]
u, p_u, beta, nx = S.pot_fit(pm)
out["families_L66_extra"]["VIGK"] = {
    "u": round(u, 4), "p_u": round(p_u, 5), "beta": round(beta, 5), "n_exceed": nx,
    "bar_Ncl": round(S.pot_bar(u, p_u, beta, S.N_CL), 4),
    "emp_max": round(float(pm.max()), 4)}
print("VIGK", out["families_L66_extra"]["VIGK"], flush=True)

# ---- ATTSEL at L=66: full attack on 20 WIN-U surrogates
import adjudicate as A
att = []
for i in range(20):
    x = surr("WINU", L)
    for meta, dec in S.attack_candidates(x, logq):
        att.append(A.adjudicate_batch(dec, pan=pan)["pmax"])
att = np.concatenate(att)
u, p_u, beta, nx = S.pot_fit(att)
out["families_L66_extra"]["ATTSEL"] = {
    "n_pooled": int(len(att)),
    "u": round(u, 4), "p_u": round(p_u, 5), "beta": round(beta, 5), "n_exceed": nx,
    "bar_Ncl": round(S.pot_bar(u, p_u, beta, S.N_CL), 4),
    "emp_max": round(float(att.max()), 4)}
print("ATTSEL", out["families_L66_extra"]["ATTSEL"], flush=True)

# classical bar of record = max over SEL/WINU/VIGK/ATTSEL at N_CL
n66 = out["nodes"]["66"]
cands = [S.pot_bar(n66[f]["u"], n66[f]["p_u"], n66[f]["beta"], S.N_CL) for f in ("SEL", "WINU")]
cands += [out["families_L66_extra"][f]["bar_Ncl"] for f in ("VIGK", "ATTSEL")]
out["classical_bar_of_record"] = round(max(cands), 4)
out["classical_bar_components"] = [round(x, 4) for x in cands]
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("nulls.json", "w"), indent=1)
print("classical bar of record:", out["classical_bar_of_record"])
print("bars600:", {L: out["nodes"][str(L)]["bar_of_record_N600"] for L in S.L_NODES})
print("elapsed", out["elapsed_s"])
