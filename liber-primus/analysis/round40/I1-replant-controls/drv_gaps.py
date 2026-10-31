"""I1 R40: re-plant R38-C2 gaps controls (G1 plant-at-true-key, G2, G3). python -I drv_gaps.py REG.."""
import os, sys, json, time, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
GD = os.path.join(AN, "round38", "C2-never-cells", "gaps"); sys.path.insert(0, GD)
import run_gaps as RG
S, E, RELS = RG.S, RG.E, RG.RELS
OUT = os.path.join(HERE, "results_raw.jsonl")
def emit(d): open(OUT, "a").write(json.dumps(d) + "\n")
def run(reg):
    rng = random.Random(6001 + sum(map(ord, reg))); t0 = time.time(); lens0 = E.word_lens_from(0)
    for ch in ("prime", "index"):
        for m in (29, 28):
            for mode in ("a", "b"):
                for rel in RELS:
                    o = rng.randrange(8); P = RG.held(reg=reg, rng=rng); seed = rng.randrange(1, 10 ** 9)
                    Cc = (E.enc_u2a(P, ch, "pline", m, o, rel, seed) if mode == "a" else E.enc_u2b(P, ch, "pline", m, o, lens0, rel, seed))[:240]
                    j = {"sub": "U2", "ch": ch, "nm": "pline", "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
                    p1, a1 = S.plant_run(j, Cc, 120); p2, a2 = S.plant_run(j, Cc, 240)
                    e = {"grp": "R38-C2-G2", "reg": reg, "cell": "%s|%d|%s|%s" % (ch, m, mode, rel)}; e.update(RG.judge(float(a1["pmax"]), float(a2["pmax"]), RG.rec_of(p2, P), rel)); emit(e)
    print(reg, "G2 %.0fs" % (time.time() - t0), flush=True)
    for cell in RG.g3_cells():
        for rep in range(2):
            sigma = rng.choice((-1, 1)); rel = RELS[rng.randrange(2)] if cell[4] == "A3" else "direct"; P = RG.held(reg=reg, rng=rng); seed = rng.randrange(1, 10 ** 9)
            if cell[4] == "A3":
                Cc = None
                for tr in range(10):
                    Cc, it = RG.g3_enc_a3(P, RG.LENSP[0], cell, sigma, rel, seed + tr)
                    if Cc is not None: break
            else:
                Cc, it = RG.g3_enc_direct(P, RG.LENSP[0], cell, sigma), 0
            Cc = Cc[:240]
            p1, a1 = RG.g3_run(cell, 0, sigma, rel, 120, C=Cc[:120], Cfull=Cc, lens=RG.LENSP[0]); p2, a2 = RG.g3_run(cell, 0, sigma, rel, 240, C=Cc, Cfull=Cc, lens=RG.LENSP[0])
            e = {"grp": "R38-C2-G3", "reg": reg, "cell": "%s|%d|%s" % (RG.cname(cell), rep, rel)}; e.update(RG.judge(float(a1["pmax"]), float(a2["pmax"]), RG.rec_of(p2, P[:len(p2)]), rel)); emit(e)
    print(reg, "G3 %.0fs" % (time.time() - t0), flush=True)
    plant_for = {"direct": ("G1-C6", "UP"), "sha256ctr": ("G1-C7", "UPD"), "pbkdf2": ("G1-C6", "AW")}
    for route, (cid, form) in plant_for.items():
        pj = [j for j in RG.g1_jobs((route,)) if j["cid"] == cid and j["form"] == form][0]; K = S.u1_key(route, cid, form, pj["text"])
        for rel in RELS:
            for rep in range(2):
                o = rng.randrange(8); P = RG.held(reg=reg, rng=rng); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
                d1, a1 = RG.v3dec(Cc[:120], K, rel, -1, o); d2, a2 = RG.v3dec(Cc, K, rel, -1, o)
                e = {"grp": "R38-C2-G1", "reg": reg, "cell": "%s|%s|%d" % (route, rel, rep)}; e.update(RG.judge(float(a1["pmax"]), float(a2["pmax"]), RG.rec_of(d2["plain_idx"], P), rel)); emit(e)
    print(reg, "G1 %.0fs" % (time.time() - t0), flush=True)
if __name__ == "__main__":
    for reg in sys.argv[1:]:
        print("free GB", S.free_gb(), flush=True); run(reg)
