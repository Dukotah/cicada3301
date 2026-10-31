"""X1: independent spot-check of I1 re-plants with FRESH seeds. python -I rerun_i1_spot.py u1|g2|n5|l2map  (writes rerun_i1_<what>.json here only)"""
import os, sys, json, random, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); I1 = os.path.abspath(os.path.join(HERE, "..", "I1-replant-controls"))
sys.path.insert(0, I1)
what = sys.argv[1]; out = []
REGS5 = ["LATIN", "GREEK", "HEBREW", "EN_NOVOWEL", "EN_NOVOWEL"]
def save():
    json.dump(out, open(os.path.join(HERE, "rerun_i1_%s.json" % what), "w"), indent=1)
    rec = sum(1 for e in out if e.get("recover")); print(what, "recovered", rec, "of", len(out), flush=True)
if what == "u1":
    import drv_c1 as D
    S = D.S; E = S.E; rng = random.Random(910001)
    ids = {"direct": "U1-001", "sha256ctr": "U1-002", "pbkdf2": "U1-003"}
    for i, reg in enumerate(REGS5):
        route = list(ids)[i % 3]; rel = S.RELS[i % 2]
        pj = [j for j in S.u1_jobs((route,)) if j["cid"] == ids[route] and j["form"] == "UP"][0]; K = S.u1_key(route, pj["cid"], "UP", pj["text"])
        o = rng.randrange(8); P = S.held(reg=reg, rng=rng, L=240); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
        d1, a1 = S.v3dec(Cc[:120], K, rel, -1, o); d2, a2 = S.v3dec(Cc, K, rel, -1, o)
        e = {"row": "R37-C1-U1", "reg": reg, "route": route, "rel": rel}; e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), S.rec_of(d2["plain_idx"], P), rel)); out.append(e)
elif what == "g2":
    import drv_gaps as D
    RG, S, E, RELS = D.RG, D.S, D.E, D.RELS; rng = random.Random(910002); lens0 = E.word_lens_from(0)
    for i, reg in enumerate(REGS5):
        ch = ("prime", "index")[i % 2]; m = (29, 28)[i % 2]; mode = ("a", "b")[(i // 2) % 2]; rel = RELS[i % 2]
        o = rng.randrange(8); P = RG.held(reg=reg, rng=rng); seed = rng.randrange(1, 10 ** 9)
        Cc = (E.enc_u2a(P, ch, "pline", m, o, rel, seed) if mode == "a" else E.enc_u2b(P, ch, "pline", m, o, lens0, rel, seed))[:240]
        j = {"sub": "U2", "ch": ch, "nm": "pline", "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
        p1, a1 = S.plant_run(j, Cc, 120); p2, a2 = S.plant_run(j, Cc, 240)
        e = {"row": "R38-C2-G2", "reg": reg, "cell": "%s|%d|%s|%s" % (ch, m, mode, rel)}; e.update(RG.judge(float(a1["pmax"]), float(a2["pmax"]), RG.rec_of(p2, P), rel)); out.append(e)
elif what == "n5":
    import drv_c3 as D
    R = D.R; rng = random.Random(910003)
    n5 = R.n5_mod(); n5k = [c[2] for c in R.n5_cfgs(n5) if len(c[2]) > 5000][::31]
    b = {r: {"L120": R.bar12(1e6, 120, r), "L240": R.bar12(1e6, 240, r)} for r in R.RELS}
    for i, reg in enumerate(REGS5):
        rel = R.RELS[i % 2]; K = n5k[rng.randrange(len(n5k))]; s0 = rng.randrange(0, max(1, min(4000, len(K) - 1024))); Kw = K[s0:s0 + 1024]
        C, P = R.plant_beam(reg, rel, Kw, rng)
        d1, a1 = R.v3dec(C[:120], Kw, rel); d2, a2 = R.v3dec(C, Kw, rel); rec = float(R.B2.recovery(d2["plain_idx"], P))
        e = {"row": "R37-C3-U6A-N5", "reg": reg, "rel": rel, "pmax120": round(float(a1["pmax"]), 3), "pmax240": round(float(a2["pmax"]), 3), "recovery240": round(rec, 4), "bar120": round(b[rel]["L120"], 3), "bar240": round(b[rel]["L240"], 3)}
        e["recover"] = bool(e["pmax120"] >= b[rel]["L120"] and e["pmax240"] >= b[rel]["L240"] and rec >= 0.9); out.append(e)
elif what == "l2map":
    import drv_c3 as D
    import numpy as np
    R = D.R
    s = json.load(open(os.path.join(D.D3, "rescore_summary.json")))["families"]
    fam = [k for k in s if "M1_perpage" in k][0]; v = s[fam]; n = v["control"]["EN_MODERN"]["n"]; q99 = v["null_max_Z_q99"]
    res = {"family": fam, "n": n, "q99": q99}
    for reg in ("EN_MODERN", "EN_NOVOWEL"):
        k = 0; zs = []
        for sd in range(10):
            P = R.plant_stream(reg, n, 500 + sd); obs = R.pm_many({"p": P})["p"]
            a = np.array([R.pm_many({"p": np.random.RandomState(1000 + j).permutation(P)})["p"] for j in range(150)])
            Zp = float((obs - a.mean()) / (a.std(ddof=1) or 1e-9)); zs.append(round(Zp, 2)); k += Zp > q99 + 1.0
        res[reg] = {"recovered": int(k), "of": 10, "Z": zs}
    out.append(res); json.dump(res, open(os.path.join(HERE, "rerun_i1_l2map.json"), "w"), indent=1); print(res); sys.exit(0)
save()
