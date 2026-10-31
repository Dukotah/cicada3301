"""X1-A B2 audit: re-plant offsets with an independently written generator / enciphering / head wrapper.
python x1a_b2.py plant | misaligned | wrap | rejudge        (writes only in this directory)"""
import os, sys, json, random, math, importlib.util, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import numpy as np
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m
S = _load("r37sweep_x1", os.path.join(LP, "analysis", "round37", "I2-pfv4-12reg", "sweep.py"))
AD, B2, PAN, U = S.AD, S.B2, S.PAN, S.U
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null")); import bars_v3
N = 29

# ---- my own bash 4.2 LP64 $RANDOM: Schrage in unsigned long (64-bit wrap), anti-repeat with last=0
M64 = (1 << 64) - 1
def my_raws(seed, n, anti=True):
    s = seed & M64; last = 0; out = []
    while len(out) < n:
        if s == 0: s = 123459876
        h, l = divmod(s, 127773)
        s = (16807 * l - 2836 * h) & M64
        rv = s & 32767
        if anti and rv == last: continue
        last = rv; out.append(rv)
    return out
def my_heads_np(seeds, m):                     # vectorised, no anti-repeat (as the screen does)
    s = seeds.astype(np.uint64); out = np.empty((m, len(s)), np.int8)
    for t in range(m):
        s = np.where(s == 0, np.uint64(123459876), s)
        h = s // np.uint64(127773); l = s - h * np.uint64(127773)
        s = np.uint64(16807) * l - np.uint64(2836) * h
        out[t] = ((s & np.uint64(32767)) % np.uint64(29)).astype(np.int8)
    return out
CUR = {"off": 0, "sign": -1}
def my_heads(seeds, m, variant):
    assert variant == "bash4.2"
    off, sg = CUR["off"], CUR["sign"]
    H = my_heads_np(seeds, m + off)[off:].astype(np.int16)
    if sg > 0: H = (29 - H) % 29
    return np.ascontiguousarray(H.astype(np.int8))
S.pf_v4.heads = my_heads
def eff_ks(seed, off, sg, n=1024):             # decode keystream: K' = K_raw[off:] (sign -1) or 29-K_raw[off:] (sign +1), exact with anti-repeat
    K = [r % 29 for r in my_raws(seed, n + off)][off:]
    return K if sg < 0 else [(29 - x) % 29 for x in K]

# ---- my own enciphering: c = p - sign*K[j]; on a doublet with prob supp the rejected key is consumed (advance adv extra keys beyond the rejected one)
def enc(P, Kt, sign, adv, supp=0.83, seed=1):
    rng = random.Random(seed); C = []; j = 0; cp = None
    for p in P:
        while True:
            c = (p - sign * Kt[j]) % N
            if cp is not None and c == cp and rng.random() < supp: j += adv; continue
            break
        C.append(c); j += 1; cp = c
    return C

def bars():
    return {r: {"L120": bars_v3.bar_v3(10 ** 6, 120, r, family="survivor12"), "L240": bars_v3.bar_v3(10 ** 6, 240, r, family="survivor12")} for r in ("keyskip1", "keyskip2")}

def one(rng, off, sg, rel, reg, screen_cell, bs):
    arr = S.TEST[reg].astype(np.int64)
    while True:
        ps = (rng.choice(S.PREF) << 20) | rng.randrange(1 << 20)
        raw = my_raws(ps, 1100 + off); Kt = [r % 29 for r in raw][off:]       # TRUE un-negated stream from index off
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + 240].tolist()
        C = enc(P, Kt, sg, S.ADV[rel], seed=rng.randrange(1, 10 ** 9))[:240]
        if len(C) < 240 or any(C[i] == C[i + 1] for i in range(39)): continue
        break
    naive = [(p - sg * k) % N for p, k in zip(P, Kt)]
    wsk = int(any(C[i] != naive[i] for i in range(24)))
    CUR["off"], CUR["sign"] = screen_cell
    base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
    m = S.pf_v4.prefilter_mask(seeds, "bash4.2", np.array(C[:S.M_PF], dtype=np.int8), S.M_PF, "both")
    e = {"offset": off, "sign": sg, "screen_cell": list(screen_cell), "rel": rel, "reg": reg, "seed": int(ps), "with_skip_head24": wsk, "chunk_survivors": int(m.sum()),
         "prefilter_pass": bool(m[ps - base]), "pmax120": None, "pmax240": None, "recovery240": None, "recover": False}
    if e["prefilter_pass"]:
        K = eff_ks(ps, *screen_cell)
        d1 = S.V.beam_decode_v3(list(C[:120]), K, S.ADV[rel], "panel_max", tau=0.0, lam_u=4.0); a1 = AD.adjudicate(d1["plain_idx"])
        d2 = S.V.beam_decode_v3(list(C[:240]), K, S.ADV[rel], "panel_max", tau=0.0, lam_u=4.0); a2 = AD.adjudicate(d2["plain_idx"])
        e["pmax120"] = round(float(a1["pmax"]), 3); e["pmax240"] = round(float(a2["pmax"]), 3); e["recovery240"] = round(float(B2.recovery(d2["plain_idx"], P)), 4)
        e["recover"] = bool(e["pmax120"] >= bs[rel]["L120"] and e["pmax240"] >= bs[rel]["L240"] and e["recovery240"] >= 0.90)
    return e

def plant():
    bs = bars(); out = []; rng = random.Random(8841)
    for (off, sg) in ((2, -1), (0, +1)):
        for j in range(5):
            rel = ("keyskip1", "keyskip2")[j % 2]; reg = ("EN_MODERN", "EN_NOVOWEL")[(j // 2) % 2]
            e = one(rng, off, sg, rel, reg, (off, sg), bs); out.append(e); print(e, flush=True)
    json.dump({"bars_of_record_1e6": bs, "plants": out}, open(os.path.join(HERE, "x1a_b2_plants.json"), "w"), indent=1)

def misaligned():
    bs = bars(); out = []; rng = random.Random(9951)
    for (off, sg) in ((1, -1), (2, -1), (0, +1)):
        for j in range(10):
            rel = ("keyskip1", "keyskip2")[j % 2]; reg = ("EN_MODERN", "EN_NOVOWEL")[(j // 2) % 2]
            e = one(rng, off, sg, rel, reg, (0, -1), bs); out.append(e); print(e, flush=True)
    json.dump({"bars_of_record_1e6": bs, "plants": out}, open(os.path.join(HERE, "x1a_b2_misaligned.json"), "w"), indent=1)

def wrap():
    # independent check vs B2 claim: heads_off vs exact my_raws, random seeds, all five cells
    rng = random.Random(12345); seeds = np.array([(rng.choice(S.PREF) << 20) | rng.randrange(1 << 20) for _ in range(200)], dtype=np.uint64)
    res = {}
    # also confirm my generator equals the repo generator C1.ks on a sample
    ok = all([r % 29 for r in my_raws(int(s), 64)] == list(S.C1.ks(int(s), "bash4.2", 64)) for s in seeds[:50]); res["my_gen_equals_C1.ks_50seeds_64"] = ok
    for off, sg in ((0, 1), (1, -1), (2, -1), (3, -1), (28, -1)):
        CUR["off"], CUR["sign"] = off, sg; H = my_heads(seeds, 28, "bash4.2"); bad = 0; ar_diff = 0
        for i, s in enumerate(seeds):
            ref_noanti = eff_ref = None
            raw = my_raws(int(s), 28 + off + 5, anti=False); r2 = [x % 29 for x in raw][off:][:28]
            r2 = r2 if sg < 0 else [(29 - x) % 29 for x in r2]
            bad += r2 != H[:, i].tolist()
            ex = eff_ks(int(s), off, sg)[:28]; ar_diff += ex != H[:, i].tolist()   # anti-repeat divergence (screen approximation)
        res["o%d_s%s" % (off, "p" if sg > 0 else "m")] = {"seeds": len(seeds), "head_vs_noanti_mismatch": int(bad), "head_vs_exact_antirepeat_differs": int(ar_diff)}
    # B2's own wrapcheck.json cross: do the wrapper's heads equal mine?
    B = _load("b2sweep_x1_hack", os.path.join(LP, "analysis", "round40", "B2-offsets", "sweep.py")) if False else None
    json.dump(res, open(os.path.join(HERE, "x1a_b2_wrap.json"), "w"), indent=1); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    {"plant": plant, "misaligned": misaligned, "wrap": wrap}[sys.argv[1]]()
