"""R37 I2: calibration/ROC, natural-rate power x12, throughput.  python roc.py calib|power|thru"""
import sys, os, json, random, time, math
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pf_v4_12 as P12
pf_v4 = P12.pf_v4
LP = P12.LP
sys.path.insert(0, os.path.join(LP, "analysis", "round32", "B1-bash-random"))
import importlib.util as iu
_s = iu.spec_from_file_location("b1common", os.path.join(LP, "analysis", "round32", "B1-bash-random", "common.py"))
C1 = iu.module_from_spec(_s); sys.modules["b1common"] = C1; _s.loader.exec_module(C1)
sk = C1.sk; U = C1.U
REGS = P12.REGS
TEST = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
SEC = [(1325376000 >> 20), (1401580800 >> 20)]
M = 24; K_ = 2; PEN = 2; KL = 28
CREAL = np.array(U[:24], dtype=np.int8)
F = lambda n: os.path.join(HERE, n)


def wilson(x, n, z=1.96):
    if n == 0: return [None, None]
    p = x / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def bseeds(rng, n): return np.array([(rng.randrange(SEC[0], SEC[1] + 1) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)


def null_scores(variant, n, rng):
    sd = bseeds(rng, n); K = pf_v4.heads(sd, KL, variant); out = {}
    for a in (1, 2):
        R = P12.dp_regs(CREAL, K[:M + a * K_], K_, a, PEN, ms=(M,)); out[a] = P12.lse_from_regs(R[M], M)
    return out


def enc1(P, K, seed):
    Cc, _, used = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=seed); return list(Cc), used


def enc2(P, K, seed):
    r = random.Random(seed); Cc, used, j, cp = [], [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if cp is not None and c == cp and r.random() < 0.83: j += 2; continue
            break
        Cc.append(c); used.append(j); j += 1; cp = c
    return Cc, used


def make_plants(rng, regs, N, rels=(1, 2)):
    out = dict(C=[], K=[], reg=[], rel=[], abi=[], f=[])
    for a in rels:
        enc = enc1 if a == 1 else enc2
        for r, reg in enumerate(regs):
            txt = TEST[reg].astype(np.int64)
            for abi_i, v in enumerate(("bash4.2", "bash4.2_i32")):
                n = N // 2; got = 0
                while got < n:
                    nb = max(8, (n - got) * 2); sd = bseeds(rng, nb); Kf = pf_v4.heads(sd, 70, v)
                    for i in range(nb):
                        if got >= n: break
                        st = rng.randrange(0, len(txt) - 60); Pt = [int(x) for x in txt[st:st + 40]]
                        try: Cc, used = enc(Pt, Kf[:, i].tolist(), rng.randrange(1, 10 ** 9))
                        except Exception: continue
                        if len(Cc) < 40 or any(Cc[t] == Cc[t + 1] for t in range(39)): continue
                        out["C"].append(Cc[:24]); out["K"].append(Kf[:KL, i]); out["reg"].append(r); out["rel"].append(a); out["abi"].append(abi_i)
                        out["f"].append(next((t for t in range(24) if used[t] != t), 99)); got += 1
    for k in ("reg", "rel", "abi", "f"): out[k] = np.array(out[k])
    out["C"] = np.array(out["C"], dtype=np.int8).T; out["K"] = np.array(out["K"], dtype=np.int8).T
    return out


FPRS = [2.5e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2]   # per relation
ABIS = ("bash4.2", "bash4.2_i32")


def calib():
    rng = random.Random(3701); t0 = time.time(); NG = 1 << 19
    sc = {1: [], 2: []}; abi = []
    for vi, v in enumerate(ABIS):
        for i0 in range(0, NG, 1 << 17):
            o = null_scores(v, 1 << 17, rng)
            for a in (1, 2): sc[a].append(o[a])
            abi.append(np.full(1 << 17, vi))
        print("null", v, round(time.time() - t0), flush=True)
    sc = {a: np.concatenate(sc[a]) for a in (1, 2)}; abi = np.concatenate(abi); n = len(abi)
    perm = np.random.default_rng(3701).permutation(n); half = np.zeros(n, bool); half[perm[: n // 2]] = True   # True = held-out
    cal = ~half
    thr = {f: {a: float(np.quantile(sc[a][cal], 1 - f)) for a in (1, 2)} for f in FPRS}
    res = {}
    for f in FPRS:
        hit = (sc[1] > thr[f][1]) | (sc[2] > thr[f][2])
        res[str(f)] = dict(thr_a1=thr[f][1], thr_a2=thr[f][2], fpr_total_calib=float(hit[cal].mean()), fpr_total_heldout=float(hit[half].mean()),
                           heldout_wilson=wilson(int(hit[half].sum()), int(half.sum())),
                           per_abi_heldout={v: float(hit[half & (abi == i)].mean()) for i, v in enumerate(ABIS)})
    json.dump(dict(n_per_abi=NG, n_total=n, split="random 50/50 seed 3701", per_relation_fprs=FPRS, points=res), open(F("roc12_null.json"), "w"), indent=1)
    np.savez(F("_null_scores.npz"), a1=sc[1], a2=sc[2], abi=abi, half=half)
    print(json.dumps(res["0.0005"]), round(time.time() - t0))


def power():
    rng = random.Random(3702); t0 = time.time(); N = 500
    nl = json.load(open(F("roc12_null.json")))["points"]
    PL = make_plants(rng, REGS, N); print("plants", len(PL["reg"]), round(time.time() - t0), flush=True)
    nn = PL["C"].shape[1]
    sc = {a: np.concatenate([P12.dp_cols(PL["C"][:, i:i + 8192], PL["K"][: M + a * K_, i:i + 8192], K_, a, PEN) for i in range(0, nn, 8192)]) for a in (1, 2)}
    np.savez(F("_plant_scores.npz"), a1=sc[1], a2=sc[2], **{k: PL[k] for k in ("reg", "rel", "abi", "f")})
    out = {}

    def st(hit, m_):
        x = int(hit[m_].sum()); n = int(m_.sum()); return dict(n=n, hits=x, power=(x / n if n else None), wilson95=wilson(x, n))
    for f in FPRS:
        t = nl[str(f)]; hit = (sc[1] > t["thr_a1"]) | (sc[2] > t["thr_a2"]); per = {}
        for r, reg in enumerate(REGS):
            sel = PL["reg"] == r; e = {}
            e["natural"] = st(hit, sel); e["keyskip1_plants"] = st(hit, sel & (PL["rel"] == 1)); e["keyskip2_plants"] = st(hit, sel & (PL["rel"] == 2))
            e["skip_free"] = st(hit, sel & (PL["f"] >= 24)); e["with_skip"] = st(hit, sel & (PL["f"] < 24))
            e["frac_with_skip"] = float((PL["f"][sel] < 24).mean())
            e["LP64"] = st(hit, sel & (PL["abi"] == 0)); e["ILP32"] = st(hit, sel & (PL["abi"] == 1))
            per[reg] = e
        out[str(f)] = dict(per_relation_fpr=f, total_fpr_heldout=t["fpr_total_heldout"], per_register=per,
                           min_power=min(per[g]["natural"]["power"] for g in REGS), all_ge_085=all(per[g]["natural"]["power"] >= 0.85 for g in REGS))
    json.dump(dict(design="500 plants/register/relation, ABI alternating, natural rate, C[:40] doublet-free only filter; pass = OR over relations", pen=PEN, k=K_, m=M, curves=out), open(F("power12_per_register.json"), "w"), indent=1)
    for f in FPRS:
        print(f, "tot_fpr", round(nl[str(f)]["fpr_total_heldout"], 5), {g: round(out[str(f)]["per_register"][g]["natural"]["power"], 3) for g in REGS}, flush=True)
    print(round(time.time() - t0))


def thru():
    rng = random.Random(3703); n = 1 << 18; res = {}
    LMT9 = None
    sys.path.insert(0, os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication"))
    LMT9 = C1.AD.panel().LMT.astype(np.float32)
    for nm in ("pf_v4_9reg", "pf_v4_12reg", "pf_v4_9reg", "pf_v4_12reg"):
        sd = bseeds(rng, n); t = time.time(); K = pf_v4.heads(sd, KL, "bash4.2"); th = time.time() - t
        for a in (1, 2):
            if nm == "pf_v4_9reg": pf_v4.dp_regs(CREAL, K[:M + a * K_], LMT9, K_, a, PEN, (M,))
            else: P12.dp_regs(CREAL, K[:M + a * K_], K_, a, PEN, (M,))
        tt = time.time() - t
        res.setdefault(nm, []).append(dict(seeds=n, seconds_total=round(tt, 2), seconds_heads=round(th, 2), seeds_per_s=round(n / tt)))
    res["ratio_12_over_9_time"] = round(sum(r["seconds_total"] for r in res["pf_v4_12reg"]) / sum(r["seconds_total"] for r in res["pf_v4_9reg"]), 3)
    json.dump(res, open(F("throughput.json"), "w"), indent=1); print(res)


if __name__ == "__main__":
    {"calib": calib, "power": power, "thru": thru}[sys.argv[1]]()
