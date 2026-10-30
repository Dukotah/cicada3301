#!/usr/bin/env python3
"""R36 O3 autopsy of bash 4.2 seed 1354603465.  usage: python autopsy.py repro|cells <budget_s>|nulls <which>|verif|plant
Writes only inside this directory.  One small process; memory-gated."""
import os, sys, json, time, math, random, ctypes
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32, R33, R34, R36 = [os.path.join(LP, "analysis", "round%d" % r) for r in (32, 33, 34, 36)]
import numpy as np
sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
import common as C1
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V
sys.path.insert(0, os.path.join(R34, "I1-v3-null"))
from bars_v3 import bar_v3
AD = C1.AD; B2 = V.B2; U = C1.U; PAN9 = V.panel()
PAN12 = AD.Panel(os.path.join(R36, "I1-new-registers", "models", "panel12.npz"))
SEED = 1354603465
ABIS = ("bash4.2", "bash4.2_i32")
ADV = {"keyskip1": 1, "keyskip2": 2, "free": "free"}
PAGES = (262, 266, 201)
P012 = sum(PAGES)
LS = (120, 240, 262, 400, 729)
F = lambda n: os.path.join(HERE, n)
SEC0, SEC1 = 1325376000, 1401580800
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1))
WORDS = ["the", "and", "that", "with", "for", "was", "his", "not", "but", "are", "from", "they", "have", "this", "which",
         "were", "said", "all", "one", "there", "been", "their", "would", "when", "will", "more", "into", "than"]


class MS(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("ml", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong), ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]


def freegb():
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return m.ap / 2 ** 30


def memwait():
    t = time.time()
    while freegb() < 0.4:
        if time.time() - t > 1200: raise SystemExit("mem wait >20min")
        time.sleep(60)


def zs(pan, x):
    x = np.asarray(x, dtype=np.int64); s = pan.raw(x); mu, sd, _, _ = pan.cal(len(x)); z = (s - mu) / sd
    i = int(z.argmax()); return float(z[i]), pan.registers[i], z


_KC = {}
def keys(seed, abi, n):
    k = (seed, abi)
    if k not in _KC or len(_KC[k]) < n:
        _KC.clear(); _KC[k] = C1.ks(seed, abi, max(n, 1024))
    return _KC[k]


def decode(abi, seed, rel, sign, L, o=0, c0=0, C=None, both=True):
    C = list(C) if C is not None else list(U[c0:c0 + L])
    K = keys(seed, abi, o + (41 if rel == "free" else 9) * len(C) + 64)
    d = V.beam_decode_v3(C, K, ADV[rel], "panel_max", sign=sign, o=o, beam_w=400, tau=0.0, lam_u=4.0)
    x = d["plain_idx"]; p9, r9, _ = zs(PAN9, x)
    out = {"pmax9": p9, "reg9": r9, "n_skips": d["n_skips"], "ptr_end": d["ptr_end"]}
    if both:
        p12, r12, _ = zs(PAN12, x); out.update(pmax12=p12, reg12=r12)
    return d, out


def draw_seeds(n, rng):
    return [(rng.choice(PREF) << 20) | rng.randrange(1 << 20) for _ in range(n)]


def load(n, d=None):
    return json.load(open(F(n))) if os.path.exists(F(n)) else d


def save(n, o): json.dump(o, open(F(n), "w"), indent=1)


def wordhits(x):
    s = "".join(AD.TRANSLIT[i] for i in x).lower()
    return sum(s.count(w) for w in WORDS)


def repro():
    memwait(); r = {}
    for abi in ABIS:
        for rel in ("keyskip2", "keyskip1", "free"):
            _, o = decode(abi, SEED, rel, -1, 120); r["%s|%s" % (abi, rel)] = o
    r["R33_rescreen_beam_w64"] = {"LP64 keyskip2": 7.068050415466602, "ILP32 keyskip2": 6.762366956470023, "LP64 keyskip1": 2.800052873731619, "ILP32 keyskip1": 2.8629356814132825}
    r["pass"] = bool(abs(r["bash4.2|keyskip2"]["pmax9"] - 7.068) < 0.001 and r["bash4.2|keyskip2"]["reg9"] == "LP1_REAL" and abs(r["bash4.2_i32|keyskip2"]["pmax9"] - 6.762) < 0.01)
    save("repro.json", r); print(json.dumps(r, indent=1))


def cells(budget):
    cur = load("cells.json", {"rows": [], "done": [], "budget_hit": False})
    done = set(map(tuple, cur["done"])); t0 = time.time()
    jobs = []
    for L in LS:
        for abi in ABIS:
            for rel in ("keyskip2", "keyskip1", "free"):
                for sign in (-1, 1): jobs.append((abi, rel, sign, L, 0, 0))
    for L in LS:
        for abi in ABIS:
            for rel in ("keyskip2", "keyskip1", "free"):
                if rel == "free" and L > 262: continue
                for sign in (-1, 1):
                    for o in range(1, 29): jobs.append((abi, rel, sign, L, o, 0))
                    for c0 in range(1, 29): jobs.append((abi, rel, sign, L, 0, c0))
    cur["budget_hit"] = False; n = 0
    for j in jobs:
        if j in done: continue
        if time.time() - t0 > budget: cur["budget_hit"] = True; break
        if n % 40 == 0: memwait()
        abi, rel, sign, L, o, c0 = j
        _, r = decode(abi, SEED, rel, sign, L, o, c0)
        r.update(abi=abi, rel=rel, sign=sign, L=L, o=o, c0=c0); cur["rows"].append(r); cur["done"].append(list(j)); n += 1
        if n % 100 == 0: save("cells.json", cur)
    cur["n_jobs_total"] = len(jobs); cur["n_done"] = len(cur["done"]); cur["elapsed_this_run_s"] = round(time.time() - t0)
    save("cells.json", cur); print("cells done", cur["n_done"], "/", len(jobs), "budget_hit", cur["budget_hit"])


def extra729():
    cur = load("cells.json"); done = set(map(tuple, cur["done"])); n = 0
    for sign in (-1,):
        for kind in ("o", "c0"):
            for v in range(1, 29):
                j = ("bash4.2", "keyskip2", sign, 729, v if kind == "o" else 0, v if kind == "c0" else 0)
                if j in done: continue
                if n % 20 == 0: memwait()
                _, r = decode(j[0], SEED, j[1], j[2], j[3], o=j[4], c0=j[5]); r.update(abi=j[0], rel=j[1], sign=sign, L=729, o=j[4], c0=j[5])
                cur["rows"].append(r); cur["done"].append(list(j)); n += 1
    cur["n_done"] = len(cur["done"]); save("cells.json", cur); print("extra729 done", n)


def nulls(which):
    st = load("nulls.json", {})
    rng = random.Random(36036 + sum(map(ord, which)))
    spec = {"A120": ("bash4.2", "keyskip2", 120, 2000), "A262": ("bash4.2", "keyskip2", 262, 1000), "A729": ("bash4.2", "keyskip2", 729, 400),
            "I120": ("bash4.2_i32", "keyskip2", 120, 1000), "FREE120": ("bash4.2", "free", 120, 300), "K1_120": ("bash4.2", "keyskip1", 120, 500),
            "FREE262": ("bash4.2", "free", 262, 150), "FREE729": ("bash4.2", "free", 729, 30), "FREE729B": ("bash4.2", "free", 729, 70)}
    t0 = time.time()
    if which == "GRID":
        rows = []
        for s in draw_seeds(30, rng):
            memwait(); best = {}
            for rel in ("keyskip1", "keyskip2"):
                for sign in (-1, 1):
                    for o in range(29):
                        _, r = decode("bash4.2", s, rel, sign, 120, o, 0, both=False)
                        k = "%s|%d" % (rel, sign); best[k] = max(best.get(k, -9), r["pmax9"])
            rows.append({"seed": s, "best": best, "best_all": max(best.values())})
        st["GRID"] = {"rows": rows, "time_s": round(time.time() - t0)}; save("nulls.json", st); print("GRID done"); return
    abi, rel, L, n = spec[which]
    rows = []
    for i, s in enumerate(draw_seeds(n, rng)):
        if i % 50 == 0: memwait()
        d, r = decode(abi, s, rel, -1, L)
        row = {"seed": s, "p9": round(r["pmax9"], 4), "r9": r["reg9"], "p12": round(r["pmax12"], 4), "r12": r["reg12"]}
        x = np.asarray(d["plain_idx"], dtype=np.int64)
        if which == "A262":
            row["wh"] = wordhits(x); row["ioc"] = AD.ioc_n(x); row["mds"] = AD.min_distinct(x)
        if which == "A729":
            row["seg"] = []
            for k in range(6):
                a, b, _ = zs(PAN9, x[k * 120:(k + 1) * 120]); row["seg"].append([round(a, 3), b])
        rows.append(row)
        if i % 200 == 199: st[which] = {"rows": rows, "partial": True}; save("nulls.json", st)
    st = load("nulls.json", {})
    st[which] = {"rows": rows, "partial": False, "time_s": round(time.time() - t0), "abi": abi, "rel": rel, "L": L}
    save("nulls.json", st); print(which, "done", len(rows), round(time.time() - t0))


def plant():
    memwait()
    T = np.load(os.path.join(R36, "I1-new-registers", "models", "testhalves12.npz"))
    sources = {"EN_MODERN_a": T["EN_MODERN"][1000:1800], "EN_MODERN_b": T["EN_MODERN"][5000:5800],
               "LP1_pages0-2": np.concatenate([T["LP1PAGE%d" % i] for i in range(3)])}
    K = keys(SEED, "bash4.2", 12000); res = {}
    for nm, arr in sources.items():
        P = [int(v) for v in arr[:P012]]
        Cf = C1.enc_pair(P, K, seed=777)
        res[nm] = {}
        for L in LS:
            d, r = decode("bash4.2", SEED, "keyskip2", -1, L, C=Cf[:L])
            r["recovery"] = float(B2.recovery(d["plain_idx"], P[:L])); r["text"] = "".join(AD.TRANSLIT[i] for i in d["plain_idx"]).lower()
            r["wordhits"] = wordhits(d["plain_idx"]); r["plain_true_text"] = "".join(AD.TRANSLIT[i] for i in P[:L]).lower()
            res[nm][str(L)] = r
            print(nm, L, round(r["pmax9"], 2), r["reg9"], round(r["pmax12"], 2), r["reg12"], round(r["recovery"], 3), flush=True)
    save("plant.json", res)


def verif():
    memwait(); out = {}; cand = {}
    for L in LS:
        d, r = decode("bash4.2", SEED, "keyskip2", -1, L); x = np.asarray(d["plain_idx"], dtype=np.int64)
        r["text"] = "".join(AD.TRANSLIT[i] for i in x).lower(); r["ioc"] = AD.ioc_n(x); r["mds"] = AD.min_distinct(x)
        r["h2"] = AD.h2_cond(x); r["zl"] = AD.zlib_ratio(x); r["wordhits"] = wordhits(x)
        r["z9"] = dict(zip(PAN9.registers, zs(PAN9, x)[2].tolist())); r["z12"] = dict(zip(PAN12.registers, zs(PAN12, x)[2].tolist()))
        cand[str(L)] = r
        if L == 729: x729 = x
    out["candidate"] = cand; segs = []
    for k in range(6):
        sg = x729[k * 120:(k + 1) * 120]; p9, r9, _ = zs(PAN9, sg); p12, r12, _ = zs(PAN12, sg); segs.append({"seg": k, "p9": p9, "r9": r9, "p12": p12, "r12": r12})
    out["B_segments"] = segs
    o = 0; ch = []
    for k in range(6):
        d, r = decode("bash4.2", SEED, "keyskip2", -1, 120, o=o, c0=120 * k)
        ch.append({"win": k, "o": o, "p9": r["pmax9"], "r9": r["reg9"], "p12": r["pmax12"], "r12": r["reg12"]}); o = d["ptr_end"] + 1
    out["B_chained"] = ch
    save("verif_raw.json", out); print("verif raw saved")


if __name__ == "__main__":
    a = sys.argv[1]
    if a == "repro": repro()
    elif a == "cells": cells(float(sys.argv[2]))
    elif a == "nulls": nulls(sys.argv[2])
    elif a == "plant": plant()
    elif a == "extra729": extra729()
    elif a == "verif": verif()
