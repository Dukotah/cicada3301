"""Round 41 C1 addendum 1: R44 bookcipher.py re-scored under panel-R36 with the standing matched null.  python -I run_r44.py [D]
Spec: PREREG-ADDENDUM-1-R44.md.  Reuses run_c1.judge_level / lib (round40 direct machinery).  Writes only in this directory."""
import os, sys, re, json, random, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import run_c1 as RC                       # D from argv[1]; __main__ guard keeps it inert
from run_c1 import lib, pm_many, wait_mem, free_gb, log, UN, TEST, BM, BLOCKS, D, TAG, F
gp = RC.C.gp
LPD = RC.C.LPD
BOOKDIR = os.path.join(LPD, "analysis", "bookcipher", "books")
BOOKS = ["kjv.txt", "mabinogion.txt", "miltonPL.txt", "blake.txt", "agrippa.txt"]
P = np.array(gp.PRIMES, dtype=np.int64); N = 29


def load_book(fn):                         # verbatim from analysis/bookcipher/bookcipher.py
    t = open(os.path.join(BOOKDIR, fn), encoding="utf-8", errors="ignore").read()
    a = re.split(r"\*\*\* ?START.*?\*\*\*", t, flags=re.S)
    t = a[1] if len(a) > 1 else t
    t = re.split(r"\*\*\* ?END", t, flags=re.S)[0]
    letters = re.sub(r"[^A-Z]", "", t.upper())
    words = re.findall(r"[A-Za-z]+", t)
    return letters, [w.upper() for w in words if 1 < len(w) < 15]


BK = {}
for b in BOOKS:
    l, w = load_book(b)
    if len(l) >= 5000: BK[b] = (l, w)
log("R44 books", {b: (len(v[0]), len(v[1])) for b, v in BK.items()})
OFFS = (0, 1000, 12345)


def out_string(R, book, scheme, rev, off):
    letters, words = BK[book]; Ln, Wn = len(letters), len(words); R = np.asarray(R)
    rr = R[::-1] if rev else R
    if scheme in ("L1", "L2"):
        steps = (rr + 1) if scheme == "L1" else P[rr]
        pos = (off + np.cumsum(steps)) % Ln
        return "".join(letters[p] for p in pos[:4000])
    if scheme in ("W1", "W2"):
        steps = (rr + 1) if scheme == "W1" else P[rr]
        pos = (off + np.cumsum(steps)) % Wn
        return "".join(words[p] for p in pos[:800])
    pairs = rr[:len(rr) // 2 * 2].reshape(-1, 2)
    pos = (pairs[:, 0] * N + pairs[:, 1]) % Ln
    return "".join(letters[p] for p in pos[:4000])


def unit_keys():
    ks = []
    for b in BK:
        for rev in (False, True):
            for off in OFFS:
                for sc in ("L1", "L2", "W1", "W2"): ks.append((b, sc, rev, off))
            ks.append((b, "G", rev, 0))
    return ks


def uname(k): return "%s|%s|rev%d|off%d" % (k[0], k[1], int(k[2]), k[3])


def build(R):
    out = {}
    for k in unit_keys():
        s = out_string(R, *k)
        idx = gp.keyword_to_indices(s)
        if len(idx) >= 32: out[uname(k)] = np.array(idx, dtype=np.int64)
    return out


def run_null(block):
    path = F("null_R44_b%d%s.npz" % (block, TAG))
    if os.path.exists(path): log("R44", block, "null exists"); return
    keys = None; t0 = time.time(); jl = open(F("null_draws_R44%s.jsonl" % TAG), "a")
    for j in range(D):
        sh = BM.matched_shuffle(UN, block, random.Random(BM.SEED_BASE + j))
        pm = pm_many(build(sh))
        if keys is None:
            keys = sorted(pm); store = np.full((len(keys), D), np.nan, dtype=np.float32)
        for ki, k in enumerate(keys): store[ki, j] = pm[k]
        jl.write(json.dumps({"fam": "R44", "block": block, "j": j, "best": max(v for v in pm.values() if v == v)}) + "\n")
        if (j + 1) % 100 == 0:
            jl.flush(); log("R44 b%d" % block, "draw", j + 1, "of", D, "%.0fs" % (time.time() - t0))
            if free_gb() < 0.4: wait_mem(0.4)
    jl.close(); np.savez_compressed(path, keys=np.array(keys), pm=store); log("R44 b%d null saved" % block)


# ---------------------------------------------------------------- plants (pointer-crafted)
def target_letters(reg, n, seed):
    arr = TEST[reg].astype(np.int64); st = random.Random(seed).randrange(0, len(arr) - n - 1)
    return gp.indices_to_translit([int(x) for x in arr[st:st + n]])


def craft(book, scheme, rev, off, reg, seed):
    letters, words = BK[book]; Ln = len(letters); rng = random.Random(seed)
    if scheme in ("L1", "L2", "G"):
        T = target_letters(reg, 3000, seed)[:3000]
        if scheme == "G":
            occ = {}
            for i, ch in enumerate(letters[:841]): occ.setdefault(ch, []).append(i)
            R = []
            for t in T:
                p = rng.choice(occ[t]) if t in occ else 0
                R += [p // N, p % N]
            return np.array(R, dtype=np.int64), T
        cur = off; R = []
        for t in T:
            hit = None
            for idx in range(N):
                s = (idx + 1) if scheme == "L1" else int(P[idx])
                if letters[(cur + s) % Ln] == t: hit = idx; break
            if hit is None: hit = 0
            R.append(hit); cur = (cur + ((hit + 1) if scheme == "L1" else int(P[hit]))) % Ln
        R = np.array(R, dtype=np.int64)
        return (R[::-1] if rev else R), T
    return None, None


def craft_W(book, scheme, rev, off, seed):
    rng = random.Random(seed); R = np.array([rng.choice((0, 1, 2)) for _ in range(800)], dtype=np.int64)
    return (R[::-1] if rev else R)


def plants(nullmax):
    out = []; regs = ("EN_MODERN", "LATIN", "EN_NOVOWEL"); n = 0
    for k in unit_keys():
        b, sc, rev, off = k; seed = 44000 + n
        if sc in ("W1", "W2"):
            R = craft_W(b, sc, rev, off, seed); s = out_string(R, *k); idx = gp.keyword_to_indices(s)
            if len(idx) < 32: continue
            p = pm_many({"p": np.array(idx, dtype=np.int64)})["p"]
            out.append({"unit": uname(k), "kind": "W-passage", "register": "EN(book passage)", "recovery": None, "plant_pmax": round(p, 3), "null_best_max_allblocks": round(nullmax, 3), "recognised": bool(p > nullmax)})
        else:
            reg = regs[n % 3]; R, T = craft(b, sc, rev, off, reg, seed); s = out_string(R, *k)
            m = min(len(s), len(T)); rec = sum(a == c for a, c in zip(s[:m], T[:m])) / max(m, 1)
            idx = gp.keyword_to_indices(s); p = pm_many({"p": np.array(idx, dtype=np.int64)})["p"]
            out.append({"unit": uname(k), "kind": "pointer-crafted", "register": reg, "recovery": round(rec, 4), "plant_pmax": round(p, 3), "null_best_max_allblocks": round(nullmax, 3),
                        "recognised": bool(rec >= 0.90 and p > nullmax)})
        n += 1
    return out


def first6():
    ok = []
    for i, b in enumerate(list(BK)[:3]):
        for reg in ("EN_MODERN", "LATIN"):
            R, T = craft(b, "L1", False, 0, reg, 44990 + i); s = out_string(R, b, "L1", False, 0)
            m = min(len(s), len(T)); ok.append(sum(a == c for a, c in zip(s[:m], T[:m])) / max(m, 1))
    log("Q5 first-six L1 recoveries", [round(x, 3) for x in ok]); json.dump(ok, open(F("r44_first6.json"), "w"))
    return all(x >= 0.90 for x in ok)


if __name__ == "__main__":
    wait_mem()
    if not first6(): log("kill: crafting failed"); sys.exit(2)
    for b in BLOCKS: wait_mem(); run_null(b)
    obs = pm_many(build(UN)); res = {"family": "R44-bookcipher.py", "n_units": len(obs), "blocks": {}}
    for b in BLOCKS:
        z = np.load(F("null_R44_b%d%s.npz" % (b, TAG))); keys = [str(k) for k in z["keys"]]
        obsl = {("W:" + k): v for k, v in obs.items()}; keysl = ["W:" + k for k in keys]
        res["blocks"][str(b)] = RC.judge_level(obsl, z["pm"], keysl, "W")
    alpha = 0.0025
    pz = [res["blocks"][str(b)]["p_Z"] for b in BLOCKS]; pr = [res["blocks"][str(b)]["p_raw"] for b in BLOCKS]
    res["decision"] = {"p_Z_by_block": pz, "p_raw_by_block": pr, "decision_p_Z": max(pz), "decision_p_raw": max(pr), "alpha": alpha, "crosses": bool(max(pz) <= alpha and max(pr) <= alpha)}
    nullmax = max(res["blocks"][str(b)]["null_best_max"] for b in BLOCKS)
    pl = plants(nullmax); res["plants"] = pl
    res["control_passed"] = all(x["recognised"] for x in pl); res["control_counts"] = {"recognised": sum(x["recognised"] for x in pl), "n": len(pl)}
    res["obs_top10"] = sorted(((v, k) for k, v in obs.items() if v == v), reverse=True)[:10]
    json.dump(res, open(F("result_R44%s.json" % TAG), "w"), indent=1, default=float)
    log("R44 judged", json.dumps(res["decision"]), "control", res["control_counts"])
