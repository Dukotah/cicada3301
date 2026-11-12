"""W2-C6 step 2 — plants + power -> power.json (PREREG §2 Q1, §4).

GLUE plants: the two SOLVED canon pages p55 (L=85 'AN END') and p56 (L=95) through the
cell's own 116-map grid; identity cell must cross the node bar (Q5(i)).
NODE power: 300 EN + 300 LA held-out windows per node vs the N600 bar AND every
re-adjudication bar at that L.
CLASSICAL plants: k=3 glue plant (Q5(iii)) + 30 EN / 30 LA plants per k in 1..8 through
the real attack code path (membership + true-decode pmax vs the classical bar of record).
"""
import json
import time

import numpy as np

import glue as S
import adjudicate as A

t0 = time.time()
rng = np.random.default_rng(S.SEED)
pan = S.panel()
c = S.canon()
P = S.pages()
nulls = json.load(open("nulls.json"))
logq = S.en_unigram_logq()
out = {"glue_plants": {}, "node_power": {}, "classical": {}}

# ---- GLUE plants: solved pages through own grid
all_glue_ok = True
for pg in (55, 56):
    st, L = P[pg]
    x = c[st:st + L]
    pm, r, X, meta = S.grid_pmax(x, pan)
    bar = nulls["nodes"][str(L)]["bar_of_record_N600"]
    ident = [i for i, m in enumerate(meta) if m["dir"] == "fwd" and m["a"] == 1 and m["s"] == 0][0]
    rec = {"page": pg, "L": L, "bar_N600": bar,
           "identity_pmax": round(float(pm[ident]), 4),
           "grid_max_pmax": round(float(pm.max()), 4),
           "identity_crosses": bool(pm[ident] >= bar),
           "argmax_is_identity": bool(int(pm.argmax()) == ident)}
    rec["passed"] = rec["identity_crosses"]
    all_glue_ok &= rec["passed"]
    out["glue_plants"]["p%d" % pg] = rec
    print("GLUE p%d" % pg, rec, flush=True)

# ---- node power vs every bar issued at that L
en = S.corpus_stream(latin=False, held_out=True)
la = S.corpus_stream(latin=True, held_out=True)
for L in S.L_NODES:
    node = nulls["nodes"][str(L)]
    bars = {"N600": node["bar_of_record_N600"]}
    bars.update(node["readj_bars"])
    if L == 66:
        bars["classical_Ncl"] = nulls["classical_bar_of_record"]
    maxes = {}
    for tag, stream in (("EN", en), ("LA", la)):
        W = S.windows(stream, L, 300, rng)
        gm = np.empty(300)
        for i in range(300):
            gm[i] = S.grid_pmax(W[i], pan)[0].max()
        maxes[tag] = gm
    rec = {}
    for bname, bval in bars.items():
        rec[bname] = {"bar": bval,
                      "EN_power": round(float((maxes["EN"] >= bval).mean()), 4),
                      "LA_power": round(float((maxes["LA"] >= bval).mean()), 4)}
    rec["EN_median_gridmax"] = round(float(np.median(maxes["EN"])), 4)
    rec["LA_median_gridmax"] = round(float(np.median(maxes["LA"])), 4)
    out["node_power"][str(L)] = rec
    print(L, {b: (v["EN_power"] if isinstance(v, dict) else v) for b, v in rec.items()}, flush=True)

# ---- classical plants through the REAL attack code path
bar_cl = nulls["classical_bar_of_record"]
L = 66


def plant_once(stream, k, rng):
    p = S.windows(stream, L, 1, rng)[0]
    a = int(rng.choice([1, S.N - 1]))
    s = rng.integers(0, S.N, size=k)
    cst = (a * ((p - s[np.arange(L) % k]) % S.N)) % S.N   # c = a*(p - s); decode a*c+s = p
    # membership through the real selection code path (fwd, same a, same k)
    if k <= 3:
        member = True
    else:
        v = (a * cst) % S.N
        tops = S.column_topB(v, k, S.BEAM_B[k], logq)
        member = all(int(s[j]) in tops[j].tolist() for j in range(k))
    pmax_true = float(A.adjudicate_batch(p[None, :], pan=pan)["pmax"][0])
    return member, pmax_true


# Q5(iii) glue plant: one EN window, k=3, must be recovered via FULL attack enumeration
rng_g = np.random.default_rng(S.SEED + 1)
p = S.windows(en, L, 1, rng_g)[0]
a = S.N - 1
s = np.array([5, 17, 23])
cst = (a * ((p - s[np.arange(L) % 3]) % S.N)) % S.N
found = False
best_pm = -9.9
for meta, dec in S.attack_candidates(cst, logq):
    pm = A.adjudicate_batch(dec, pan=pan)["pmax"]
    if meta["dir"] == "fwd" and meta["a"] == a and meta["k"] == 3:
        hit = np.where((dec == p[None, :]).all(axis=1))[0]
        if len(hit):
            found = True
            best_pm = max(best_pm, float(pm[hit].max()))
gl = {"recovered": found, "true_pmax": round(best_pm, 4), "bar": bar_cl,
      "crosses": bool(best_pm >= bar_cl), "passed": bool(found and best_pm >= bar_cl)}
out["classical"]["glue_plant_k3"] = gl
print("CLASSICAL GLUE", gl, flush=True)

per_k = {}
for k in S.KS:
    rec = {}
    for tag, stream in (("EN", en), ("LA", la)):
        ok = 0
        for _ in range(30):
            member, pt = plant_once(stream, k, rng)
            ok += int(member and pt >= bar_cl)
        rec[tag + "_power"] = round(ok / 30, 4)
    rec["verdict_capable_EN"] = rec["EN_power"] >= S.POWER_FLOOR
    per_k[str(k)] = rec
    print("k=%d" % k, rec, flush=True)
out["classical"]["per_k_power"] = per_k
out["classical"]["bar_of_record"] = bar_cl

out["all_glue_passed"] = bool(all_glue_ok and gl["passed"])
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("power.json", "w"), indent=1)
print("all_glue_passed:", out["all_glue_passed"])
