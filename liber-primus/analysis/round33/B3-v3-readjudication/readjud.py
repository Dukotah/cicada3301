#!/usr/bin/env python3
"""Round 33 / B3: re-decode stored Round 32 B1/B2 survivor rows through beam_decode_v3 (panel_max, hard max, lam_u=4).
Usage: python readjud.py all [run_budget_s]   (control -> null -> run -> finalize, one process)."""
import os, sys, json, time, math, random, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32 = os.path.join(LP, "analysis", "round32")
I1D = os.path.join(LP, "analysis", "round33", "I1-register-aware-beam")
import numpy as np
sys.path.insert(0, os.path.join(R32, "B1-bash-random"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m
    sp.loader.exec_module(m)
    return m


C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R32, "B2-php-mtrand"))
C2 = _load("b2common", os.path.join(R32, "B2-php-mtrand", "common.py"))
sys.path.insert(0, I1D)
import beam_v3 as V
AD = C1.AD
B2 = V.B2
PAN = V.panel()
CS = C1.C_SCREEN
CH = C1.C_HIT
NEED = C1.NEED
ADV = {"keyskip1": 1, "keyskip2": 2}
TEST = np.load(os.path.join(R32, "I2-multiregister-readjudication", "models", "testhalves.npz"))
OUT = lambda f: os.path.join(HERE, f)
T0 = time.time()
LOG = open(OUT("readjud.log"), "a")


def log(*a):
    s = "[%6.0fs] " % (time.time() - T0) + " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


def keystream(kid_parts):
    """kid_parts = (store, family, seed) -> K list."""
    store, fam, seed = kid_parts
    if store == "B1":
        return C1.ks(seed, fam)
    tw, rd = fam.split("_")
    return C2.ks(seed, (tw, rd))


def parse(kid):
    p = kid.split(":")
    return ("B1" if p[0] == "bash" else "B2", p[1], int(p[2]), p[3])


def decode(C, K, rel):
    d = V.beam_decode_v3(C, K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    a = AD.adjudicate(d["plain_idx"])
    return d, a


def load_universe():
    uni = []
    for store, rel_path in (("B1", "B1-bash-random"), ("B2", "B2-php-mtrand")):
        with open(os.path.join(R32, rel_path, "sweep_rows.jsonl"), encoding="utf-8") as f:
            f.readline()
            for line in f:
                line = line.strip()
                if line:
                    uni.append(json.loads(line)[0])
    return uni


FAMS = [("B1", "bash4.2"), ("B1", "bash4.2_i32")] + [("B2", c) for c in ("mt_scale", "mt_mod", "php_scale", "php_mod")]


def by_family(uni):
    byfam = {}
    for k in uni:
        s, f, sd, r = parse(k)
        if r == "keyskip1":
            byfam.setdefault((s, f), []).append(sd)
    return byfam


# ------------------------------------------------------------------ control
def control(uni):
    byfam = by_family(uni)
    rng = random.Random(3301)
    cells = []
    for (s, f) in FAMS:
        for rel in ("keyskip1", "keyskip2"):
            plants = []
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                arr = TEST[reg].astype(np.int64)
                for j in range(5):
                    sd = rng.choice(byfam[(s, f)])
                    K = keystream((s, f, sd))
                    st = rng.randrange(0, len(arr) - 130)
                    P = arr[st:st + 120].tolist()
                    Cc = (C1.enc_exact(P, K, seed=j + 1) if rel == "keyskip1" else C1.enc_pair(P, K, seed=j + 1))[:120]
                    t = time.time()
                    d, a = decode(Cc, K, rel)
                    rec = float(B2.recovery(d["plain_idx"], P))
                    plants.append({"register": reg, "seed": sd, "recovery": round(rec, 4), "pmax": round(float(a["pmax"]), 3),
                                   "preg": PAN.registers[a["preg"]], "sec": round(time.time() - t, 3)})
            c = {"store": s, "family": f, "rel": rel, "plants": plants}
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                c["rec_" + reg] = sum(1 for p in plants if p["register"] == reg and p["recovery"] >= 0.90)
            c["rec_total"] = c["rec_EN_MODERN"] + c["rec_EN_NOVOWEL"]
            c["pass"] = bool(c["rec_total"] >= 3 and c["rec_EN_NOVOWEL"] >= 3)
            cells.append(c)
            log("control", s, f, rel, "MOD", c["rec_EN_MODERN"], "NOV", c["rec_EN_NOVOWEL"])
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "decoder": "beam_decode_v3 panel_max hard-max lam_u=4 beam_w=400",
           "plants_per_cell": "5 EN_MODERN + 5 EN_NOVOWEL, L=120 (I2 testhalves), key = stored survivor seed of the family",
           "path": "B3 stage-2 path (v3 decode + panel adjudication); R32 prefilter not re-run (declared deviation)",
           "cells": cells, "all_pass": all(c["pass"] for c in cells)}
    json.dump(out, open(OUT("control.json"), "w"), indent=1)
    return out


# ------------------------------------------------------------------ null
def null(uni, n=12000):
    byfam = by_family(uni)
    stream = list(C1.U)
    rng = random.Random(3301)
    vals = {"keyskip1": [], "keyskip2": []}
    en = {"keyskip1": [], "keyskip2": []}
    t0 = time.time()
    for k in range(n):
        sh = stream[:]
        random.Random(3301 + k).shuffle(sh)
        Cc = sh[:120]
        fam = FAMS[k % len(FAMS)]
        K = keystream((fam[0], fam[1], rng.choice(byfam[fam])))
        for rel in ("keyskip1", "keyskip2"):
            d, a = decode(Cc, K, rel)
            vals[rel].append(float(a["pmax"]))
            en[rel].append(float(a["en"]))
        if k % 500 == 499:
            log("null", k + 1, "max", {r: round(max(v), 3) for r, v in vals.items()}, "%.0fs" % (time.time() - t0))
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "n_draws": n, "seed": 3301, "L": 120,
           "stream": "real LP2 unsolved stream, Random(3301+k).shuffle, first 120 runes, key from round-robin of 6 key families (stored survivor seeds)",
           "decoder": "beam_decode_v3 panel_max lam_u=4", "rels": {}}
    for rel, v in vals.items():
        a = np.sort(np.array(v))
        u = float(np.quantile(a, 0.90))
        exc = a[a > u] - u
        out["rels"][rel] = {"n": n, "mean": float(a.mean()), "sd": float(a.std()), "p50": float(np.quantile(a, .5)),
                            "p99": float(np.quantile(a, .99)), "emp_max": float(a[-1]), "pot_u90": u,
                            "pot_beta": float(exc.mean()), "pot_p_u": float((a > u).mean()),
                            "en_max": float(max(en[rel])), "values": [round(x, 3) for x in v]}
    json.dump(out, open(OUT("null_v3.json"), "w"), indent=1)
    return out


def bar_at(nl, N, alpha=0.01):
    """family-wise bar at N decodes: POT exponential tail, P(max>=b) = alpha."""
    pot = nl["pot_u90"] + nl["pot_beta"] * math.log(nl["pot_p_u"] * N / alpha)
    return pot, max(pot, nl["emp_max"])


# ------------------------------------------------------------------ re-adjudication
def run(uni, budget):
    order = list(range(len(uni)))
    random.Random(3301).shuffle(order)
    hdr = AD.header("round33/B3/v3-readjudication-of-round32-B1-B2-survivors",
                    key_space="STORED SURVIVOR ROWS ONLY of round32/B1 (192,066) + round32/B2 (212,218); uniform random prefix (Random(3301) shuffle) under a wall budget",
                    decoder="beam_decode_v3 design panel_max (hard max, lam_u=4, beam_w=400), keyskip1=advance 1, keyskip2=advance 2, sign -1, o=0, L=120 on LP2[:120]",
                    v3_version="round33/I1 beam_v3.py panel_max", register_panel="round32/I2 nine-register panel (models/panel.npz)",
                    universe_rows=len(uni), run_budget_s=budget, seed_sample="Random(3301).shuffle of universe, processed in order")
    out = open(OUT("readjud_rows.jsonl"), "w")
    out.write(json.dumps(hdr) + "\n")
    stats = {}
    keep = []
    allp = {"keyskip1": [], "keyskip2": []}
    t0 = time.time()
    n = 0
    cache = (None, None)
    for ix in order:
        if time.time() - t0 > budget:
            break
        kid = uni[ix]
        s, f, sd, rel = parse(kid)
        if cache[0] != (s, f, sd):
            cache = ((s, f, sd), keystream((s, f, sd)))
        d, a = decode(CS, cache[1], rel)
        out.write(json.dumps(AD.to_row(a, "v3:" + kid)) + "\n")
        pm = float(a["pmax"])
        key = s + "|" + rel
        st = stats.setdefault(key, {"n": 0, "max": -1e9, "best_kid": None, "best_preg": None})
        st["n"] += 1
        if pm > st["max"]:
            st["max"] = pm
            st["best_kid"] = kid
            st["best_preg"] = PAN.registers[a["preg"]]
        allp[rel].append(pm)
        if pm >= 4.5:
            keep.append((pm, kid))
        n += 1
        if n % 3000 == 0:
            out.flush()
            log("run", n, "of", len(uni), {k: (v["n"], round(v["max"], 2)) for k, v in stats.items()},
                "%.0f dec/s" % (n / (time.time() - t0)))
    out.close()
    log("run done", n)
    return {"order_seed": 3301, "n_done": n, "universe": len(uni), "elapsed_s": round(time.time() - t0, 1), "stats": stats,
            "keep": sorted(keep, reverse=True)[:400], "allp": allp}


def finalize(uni, ctl, nl, rr):
    from collections import Counter
    uni_cnt = Counter()
    for k in uni:
        s, f, sd, rel = parse(k)
        uni_cnt[s + "|" + rel] += 1
    nrel = {r: sum(v["n"] for k, v in rr["stats"].items() if k.endswith("|" + r)) for r in ADV}
    bars = {}
    for r in ADV:
        pot, b = bar_at(nl["rels"][r], max(nrel[r], 2))
        bars[r] = {"N": nrel[r], "pot_bar": round(pot, 3), "emp_max": round(nl["rels"][r]["emp_max"], 3),
                   "p99": round(nl["rels"][r]["p99"], 3), "bar": round(b, 3),
                   "binds": "pot" if pot >= nl["rels"][r]["emp_max"] else "empirical max"}
    cov = {}
    for k, v in rr["stats"].items():
        r = k.split("|")[1]
        cov[k] = {"n": v["n"], "universe": uni_cnt[k], "fraction": round(v["n"] / uni_cnt[k], 4), "best_pmax": round(v["max"], 3),
                  "best_kid": v["best_kid"], "best_preg": v["best_preg"], "bar": bars[r]["bar"], "clears": bool(v["max"] >= bars[r]["bar"])}
    insample = {}
    for r, v in rr["allp"].items():
        a = np.sort(np.array(v))
        if len(a) > 100:
            insample[r] = {"n": len(a), "p50": round(float(np.quantile(a, .5)), 3), "p99": round(float(np.quantile(a, .99)), 3),
                           "p9999": round(float(np.quantile(a, .9999)), 3), "max": round(float(a[-1]), 3)}
    pw = {}
    for c in ctl["cells"]:
        for reg in ("EN_MODERN", "EN_NOVOWEL"):
            ps = [p for p in c["plants"] if p["register"] == reg]
            e = pw.setdefault(reg + "|" + c["rel"], {"plants": 0, "recovered": 0, "pmax_ge_bar": 0})
            e["plants"] += len(ps)
            e["recovered"] += sum(p["recovery"] >= 0.9 for p in ps)
            e["pmax_ge_bar"] += sum(p["pmax"] >= bars[c["rel"]]["bar"] for p in ps)
    flagged = []
    for pm, kid in rr["keep"]:
        s, f, sd, rel = parse(kid)
        if pm >= bars[rel]["bar"]:
            K = keystream((s, f, sd))
            d, a = decode(CH, K, rel)
            flagged.append({"kid": kid, "pmax_L120": round(pm, 3), "bar": bars[rel]["bar"], "pmax_L240": round(float(a["pmax"]), 3),
                            "preg_L240": PAN.registers[a["preg"]], "FLAGGED_FOR_ORACLE": True, "certified": False})
    summ = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "universe_rows": len(uni), "rows_readjudicated": rr["n_done"],
            "fraction_overall": round(rr["n_done"] / len(uni), 4), "elapsed_run_s": rr["elapsed_s"], "bars": bars, "coverage": cov,
            "in_sample_tail": insample, "control_power": pw, "control_all_pass": ctl["all_pass"], "flagged": flagged,
            "top_keep": rr["keep"][:20]}
    json.dump(summ, open(OUT("readjud_summary.json"), "w"), indent=1)
    return summ


def main():
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
    uni = load_universe()
    log("universe", len(uni))
    ctl = control(uni)
    log("control all_pass", ctl["all_pass"])
    if not ctl["all_pass"]:
        log("CONTROL FAILED: stopping before null/run (see control.json)")
        return 2
    nl = null(uni)
    log("null", {r: (round(v["emp_max"], 2), round(v["p99"], 2)) for r, v in nl["rels"].items()})
    rr = run(uni, budget)
    summ = finalize(uni, ctl, nl, rr)
    log("summary", json.dumps({"bars": summ["bars"], "flagged": len(summ["flagged"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main() if len(sys.argv) > 1 and sys.argv[1] == "all" else 0)
