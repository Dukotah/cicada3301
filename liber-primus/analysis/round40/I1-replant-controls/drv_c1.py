"""I1 R40: re-plant R37-C1 (U1,U2,U3), R38-C1, R39-C1 controls in other registers.  python -I drv_c1.py REG [REG..]
Imports committed harnesses unmodified; writes only results_raw.jsonl here."""
import os, sys, json, time, random, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
R37 = os.path.join(AN, "round37", "C1-composed-clue-readings")
sys.path.insert(0, R37)
import sweep as S
import c1lib
OUT = os.path.join(HERE, "results_raw.jsonl")
def emit(d):
    open(OUT, "a").write(json.dumps(d) + "\n")
def load(name, d):
    for m in ("enciphers",): sys.modules.pop(m, None)
    sys.path.insert(0, d)
    sp = importlib.util.spec_from_file_location(name, os.path.join(d, "sweep.py")); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); sys.path.remove(d); return m
def run_c1(reg):
    rng = random.Random(4001 + sum(map(ord, reg))); t0 = time.time(); E = S.E; lens0 = E.word_lens_from(0)
    for rho in (1, 2, 3):
        for Mm in (29, 28):
            for mode, rels in (("A1", ("direct",)), ("A2", ("direct",)), ("A3", S.RELS)):
                for rel in rels:
                    s = rng.randrange(29); sigma = rng.choice((-1, 1)); P = S.held(reg=reg, rng=rng, L=240)
                    Cc = E.enc_u3(P, lens0, rho, Mm, s, sigma, mode, rel if mode == "A3" else None, rng.randrange(1, 10 ** 9))[:240]
                    j = {"sub": "U3", "rho": rho, "M": Mm, "mode": mode, "s": s, "sigma": sigma, "rel": rel, "sign": sigma, "o": 0, "page": 0}
                    p1, a1 = S.plant_run(j, Cc, 120); p2, a2 = S.plant_run(j, Cc, 240)
                    e = {"grp": "R37-C1-U3", "reg": reg, "cell": "%d|%d|%s|%s" % (rho, Mm, mode, rel)}; e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), S.rec_of(p2, P), rel)); emit(e)
    print(reg, "U3 done %.0fs" % (time.time() - t0), flush=True)
    for (ch, nm, m) in E.VARIANTS:
        for mode in ("a", "b"):
            rel = S.RELS[rng.randrange(2)]; o = rng.randrange(8); P = S.held(reg=reg, rng=rng, L=240); seed = rng.randrange(1, 10 ** 9)
            Cc = (E.enc_u2a(P, ch, nm, m, o, rel, seed) if mode == "a" else E.enc_u2b(P, ch, nm, m, o, lens0, rel, seed))[:240]
            j = {"sub": "U2", "ch": ch, "nm": nm, "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
            p1, a1 = S.plant_run(j, Cc, 120); p2, a2 = S.plant_run(j, Cc, 240)
            e = {"grp": "R37-C1-U2", "reg": reg, "cell": "%s|%s|%d|%s" % (ch, nm, m, mode)}; e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), S.rec_of(p2, P), rel)); emit(e)
    print(reg, "U2 done %.0fs" % (time.time() - t0), flush=True)
    ids = {"direct": "U1-001", "sha256ctr": "U1-002", "pbkdf2": "U1-003"}
    for route in ids:
        pj = [j for j in S.u1_jobs((route,)) if j["cid"] == ids[route] and j["form"] == "UP"][0]; K = S.u1_key(route, pj["cid"], "UP", pj["text"])
        for rel in S.RELS:
            for rep in range(2):
                o = rng.randrange(8); P = S.held(reg=reg, rng=rng, L=240); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
                d1, a1 = S.v3dec(Cc[:120], K, rel, -1, o); d2, a2 = S.v3dec(Cc, K, rel, -1, o)
                e = {"grp": "R37-C1-U1", "reg": reg, "cell": "%s|%s|%d" % (route, rel, rep)}; e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), S.rec_of(d2["plain_idx"], P), rel)); emit(e)
    print(reg, "U1 done %.0fs" % (time.time() - t0), flush=True)
def run_sem(tag, mod, reg):
    rng = random.Random(5001 + sum(map(ord, reg))); S_ = mod.S; EN = mod.EN; lens0 = mod.lens_p(0); t0 = time.time()
    for var in mod.VARS:
        for mode in ("A1", "A2", "A3"):
            for rep in range(2):
                sigma = (-1, 1)[rep]; s = rng.randrange(29) if mode != "A3" else rng.randrange(726)
                P = S_.held(reg=reg, rng=rng, L=240); seed = rng.randrange(1, 10 ** 9)
                Cc = EN.enc(P, lens0, var, s, sigma, mode, mod.REL if mode == "A3" else None, seed)[:240]
                j = {"var": var, "mode": mode, "s": s, "sigma": sigma, "page": 0}
                U0 = list(S_.U); s0 = S_.page_start(0); S_.U[s0:s0 + len(Cc)] = Cc
                try: p1, a1 = mod.run(j, 120); p2, a2 = mod.run(j, 240)
                finally: S_.U[:] = U0
                e = {"grp": tag, "reg": reg, "cell": "%s|%s|%d" % (var, mode, rep)}; e.update(S_.judge(float(a1["pmax"]), float(a2["pmax"]), S_.rec_of(p2, P), mod.REL)); emit(e)
    print(reg, tag, "done %.0fs" % (time.time() - t0), flush=True)
if __name__ == "__main__":
    what = sys.argv[1]; regs = sys.argv[2:]
    for reg in regs:
        g = c1lib.wait_mem(0.4, 1200); print("free GB", g, flush=True)
        if what == "c1": run_c1(reg)
        elif what == "r38": run_sem("R38-C1", load("sweep38", os.path.join(AN, "round38", "C1-semantic-road")), reg)
        elif what == "r39": run_sem("R39-C1", load("sweep39", os.path.join(AN, "round39", "C1-sense-similarity")), reg)
