import os, sys, json, time, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import enciphers as E
sys.path.insert(0, os.path.join(HERE, "..", "..", "round10", "L2-map"))
import mapcommon as M
B = E.B
d = M.parse(); pages = [len(p) for p in d["pages"]]
# per-page line lengths
pl = {}
for l, pg in zip(d["lines"], d["line_page"]):
    if l: pl.setdefault(pg, []).append(len(l))
TEST = np.load(os.path.join(B.HERE, "models", "testhalves_lite.npz"))
DECS = [1, 2, "free"]
def seg_lens(kind, s, L):
    if kind == "page":
        pg = (2 * s) % 54; return [pages[pg], pages[pg + 1]], pages[pg] + pages[pg + 1]
    return None, None
def plant(kind, reg, mode, s):
    a = TEST[reg].astype(np.int64)
    if mode == "page":
        pg = (2 * s) % 54
        plens = [pages[pg], pages[pg + 1]]; llens = pl.get(pg, []) + pl.get(pg + 1, [])
        L = sum(plens)
    else:
        L = 120
        pg = (2 * s) % 54; plens = [L]; llens = (pl.get(pg, []) + pl.get(pg + 1, []))
    r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1)
    P = a[st:st + L].tolist(); K = B.sha_ctr_key(L * 12 + 2048)
    sd = 3301 + s
    if kind == "reset_per_page": C, info = E.encipher_reset_per_page(P, K, plens, 0.83, sd)
    elif kind == "reset_per_line": C, info = E.encipher_reset_per_line(P, K, llens, 0.83, sd)
    elif kind.startswith("skip_by_") and kind[8:].isdigit() and kind != "skip_by_two": C, info = E.encipher_skip_by_k(P, K, int(kind[8:]), 0.83, sd)
    elif kind == "keyskip1": C, info = E.keyskip1(P, K, 0.83, sd)
    elif kind == "skip_by_two": C, info = E.skip_by_two(P, K, 0.83, sd)
    segs = plens if kind == "reset_per_page" else (llens if kind == "reset_per_line" else None)
    return P, C, K, segs
def oracle(P, C, K, segs):
    """decode each segment separately from key offset 0 with relation 1"""
    if not segs: return None
    out = []; a = 0; tot = 0; n = 0
    bounds = []
    for x in segs:
        if a >= len(C): break
        bounds.append((a, min(a + x, len(C)))); a += x
    if a < len(C): bounds.append((a, len(C)))
    rec = 0
    for (u, v) in bounds:
        bd = B.beam_decode_v2(C[u:v], K, 1)
        rec += B.recovery(bd["plain_idx"], P[u:v]) * (v - u)
    return rec / len(C)
def run(kinds, regs, modes, nseed, out):
    res = json.load(open(out)) if os.path.exists(out) else {}
    for kind in kinds:
        for reg in regs:
            for mode in modes:
                if kind == "reset_per_page" and mode == "L120": continue
                key = f"{kind}|{reg}|{mode}"
                if key in res: continue
                t0 = time.time(); cell = {d_: [] for d_ in DECS}; orc = []
                for s in range(nseed):
                    P, C, K, segs = plant(kind, reg, mode, s)
                    for dec in DECS:
                        bd = B.beam_decode_v2(C, K, dec)
                        cell[dec].append(round(float(B.recovery(bd["plain_idx"], P)), 4))
                    o = oracle(P, C, K, segs)
                    if o is not None: orc.append(round(float(o), 4))
                res[key] = {"kind": kind, "register": reg, "mode": mode, "n": nseed, "sec": round(time.time() - t0, 1),
                  "median_recovery": {str(k): float(np.median(v)) for k, v in cell.items()},
                  "frac_ge_085": {str(k): float(np.mean([x >= .85 for x in v])) for k, v in cell.items()},
                  "recoveries": {str(k): v for k, v in cell.items()},
                  "oracle_segmented_rel1_median": float(np.median(orc)) if orc else None}
                print(key, res[key]["median_recovery"], res[key]["oracle_segmented_rel1_median"], res[key]["sec"], flush=True)
                json.dump(res, open(out, "w"), indent=1)
if __name__ == "__main__":
    nseed = int(sys.argv[1]); out = sys.argv[2]
    kinds = sys.argv[3].split(","); modes = sys.argv[4].split(",")
    run(kinds, ["EN_MODERN", "EN_NOVOWEL"], modes, nseed, out)
