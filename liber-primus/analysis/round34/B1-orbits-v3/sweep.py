#!/usr/bin/env python3
"""R34 B1: bash 4.2 orbit (LP64, ILP32) + PHP mt_rand tiers under pf_v3 (screen) + beam_v3 panel_max (decoder).
Usage: python sweep.py control | python sweep.py sweep | python sweep.py finalize"""
from common import *

CALF, ROWS, SUMF = [os.path.join(HERE, f) for f in ("control.json", "sweep_rows.jsonl", "sweep_summary.json")]
KEEPF = os.path.join(HERE, "keep_rows.json")
SEC0, SEC1 = 1325376000, 1401580800
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1)); assert len(PREF) == 74
SUB = 1 << 18
BLK = 1 << 17
CAPS = {"bash4.2": 3600, "bash4.2_i32": 1500, "php_total": 2100}
BASH = ("bash4.2", "bash4.2_i32")


def bash_ks(seed, v, n=NEED): return C1.ks(seed, v, n)
def php_ks(seed, cell, n=NEED): return PM.ks(int(seed), cell[0], cell[1], n)
def keyfn(cellname, seed):
    if cellname in BASH: return bash_ks(seed, cellname)
    tw, rd = cellname.split("_"); return php_ks(seed, (tw, rd))


def pf_bash(seeds, v, Chead):
    return pf_v3.prefilter_mask(seeds, v, Chead, LMT, M_PF)


def pf_php(H31, cell, Chead):
    K = PM.reduce_heads(H31[cell[0]], cell[1])
    P = (np.asarray(Chead[:M_PF], dtype=np.int8)[:, None] - K) % 29
    return pf_v3.screen(P, LMT, THR)


def decode_seed(cellname, seed, C, out=None):
    """both relations at L=120 for one survivor seed"""
    K = keyfn(cellname, seed); res = []
    for rel in RELS:
        d, a = v3dec(C[:L_SCREEN], K, rel)
        kid = "%s:%s:%d:%s" % ("bash" if cellname in BASH else "php", cellname, seed, rel)
        if out is not None: out.write(json.dumps(AD.to_row(a, kid)) + "\n")
        res.append({"seed": int(seed), "cell": cellname, "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]]})
    return res


def chunk_bash(seeds, v, C, out=None):
    m = pf_bash(seeds, v, np.array(C[:M_PF], dtype=np.int8))
    surv = seeds[m]; rows = []
    for s in surv: rows += decode_seed(v, int(s), C, out)
    return len(surv), rows


def chunk_php(seeds, C, out=None, cells=PHP_CELLS):
    H31 = PM.heads_all(seeds, M_PF); Ch = np.array(C[:M_PF], dtype=np.int8); res = {}
    for cell in cells:
        m = pf_php(H31, cell, Ch); surv = seeds[m]; rows = []
        for s in surv: rows += decode_seed(cname(cell), int(s), C, out)
        res[cname(cell)] = (len(surv), rows)
    return res


# ------------------------------------------------------------------ control
def plant(cellname, rel, reg, j, rng):
    """returns (seed, C (L240), P (L240)); doublet-free first-40 ciphertext as the real head is."""
    arr = TEST[reg].astype(np.int64)
    enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(200):
        if cellname in BASH: ps = (rng.choice(PREF) << 20) | rng.randrange(1 << 20)
        else: ps = rng.randrange(1 << 32)
        K = keyfn(cellname, ps)
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + L_HIT].tolist()
        naive = [(P[i] + K[i]) % 29 for i in range(40)]
        if any(naive[i] == naive[i + 1] for i in range(39)): continue
        C = enc(P, K, seed=j + 1)[:L_HIT]
        if len(C) == L_HIT: return ps, C, P
    raise RuntimeError("no plant")


def control():
    rng = random.Random(3301); cells = []; t0 = time.time()
    for cellname in list(BASH) + [cname(c) for c in PHP_CELLS]:
        for rel in ("keyskip1", "keyskip2"):
            plants = []
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                for j in range(5):
                    ps, Cp, P = plant(cellname, rel, reg, j, rng)
                    base = ps & ~0xFFFF
                    seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                    if cellname in BASH: n_s, rr = chunk_bash(seeds, cellname, Cp)
                    else:
                        tw, rd = cellname.split("_"); n_s, rr = chunk_php(seeds, Cp, cells=[(tw, rd)])[cellname]
                    mine = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                    pfp = any(r["seed"] == ps for r in rr)
                    e = {"register": reg, "seed": int(ps), "prefilter_pass": bool(pfp), "survivors_in_chunk": n_s,
                         "pmax120": None, "pmax240": None, "recovery240": None, "ok": False}
                    if mine:
                        e["pmax120"] = round(mine[0]["pmax"], 3)
                        d, a = v3dec(Cp, keyfn(cellname, ps), rel)
                        e["pmax240"] = round(float(a["pmax"]), 3)
                        e["recovery240"] = round(float(B2.recovery(d["plain_idx"], P)), 4)
                        e["ok"] = bool(e["pmax120"] >= bar_v3(N_DECL, 120, rel) and e["pmax240"] >= bar_v3(N_DECL, 240, rel)
                                       and e["recovery240"] >= 0.90)
                    plants.append(e)
            c = {"cell": cellname, "rel": rel, "plants": plants}
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                ps_ = [p for p in plants if p["register"] == reg]
                c["pass_" + reg] = sum(p["ok"] for p in ps_); c["prefilter_" + reg] = sum(p["prefilter_pass"] for p in ps_)
            c["pass"] = bool(c["pass_EN_MODERN"] == 5 and c["pass_EN_NOVOWEL"] == 5)
            cells.append(c)
            print("%.0fs" % (time.time() - t0), cellname, rel, c["pass_EN_MODERN"], c["pass_EN_NOVOWEL"], flush=True)
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "path": "real chunk path: pf_v3(m=20, frozen thr %.6f) on 2^16-seed chunk -> v3 L=120 on all survivors -> v3 L=240 gate; plant windows from I2 held-out test halves, first 40 ciphertext runes doublet-free" % THR,
           "bars_declared_N1e6": {r: {"L120": bar_v3(N_DECL, 120, r), "L240": bar_v3(N_DECL, 240, r)} for r in ("keyskip1", "keyskip2")},
           "plants_per_cell_rel": "5 EN_MODERN + 5 EN_NOVOWEL", "cells": cells, "all_pass": all(c["pass"] for c in cells)}
    json.dump(out, open(CALF, "w"), indent=1); print("ALL_PASS", out["all_pass"])
    return 0 if out["all_pass"] else 1


# ------------------------------------------------------------------ sweep
def tier_a_seeds():
    """(core, dense): core = lore/literature/PGP-second seeds (decoded unfiltered); dense = dates/unix/hours/small ints (prefiltered)."""
    import datetime; sys.path.append(os.path.join(LP, "analysis", "round13", "B04")); import seeds as B04
    core, dense, seen = [], [], set()

    def add(lst, x, lab):
        x = int(x) & 0xFFFFFFFF
        if x not in seen: seen.add(x); lst.append((x, lab))
    for x in B04.NUM_INTS: add(core, x, "B04 NUM_INTS")
    for x in B04.FIRST_PRIMES: add(core, x, "B04 prime")
    for t in B04.NUM_STRINGS:
        try: add(core, int(t), "B04 NUM_STRINGS")
        except ValueError: pass
    for x in (3301, 1033, 761, 845145127, 1595277641, 1325734783, 1325635200, 1357257600, 1388880000, 2012, 2013, 2014, 29): add(core, x, "3301 family")
    for e in json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))["order"]: add(core, e["seed"], "seedprior20")
    d0 = datetime.date(2011, 1, 1)
    for i in range((datetime.date(2015, 12, 31) - d0).days + 1):
        d = d0 + datetime.timedelta(days=i)
        add(dense, int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp()), "unix-midnight-UTC")
        add(dense, d.year * 10000 + d.month * 100 + d.day, "YYYYMMDD")
    for x in range(0, 2048): add(dense, x, "small-int")
    t0 = int(datetime.datetime(2011, 1, 1, tzinfo=datetime.timezone.utc).timestamp()); t1 = int(datetime.datetime(2016, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    for ts in range(t0, t1, 3600): add(dense, ts, "unix-top-of-hour-UTC")
    return core, dense



def php_tier_a():
    return tier_a_seeds()


def sweep(resume=False):
    c = json.load(open(CALF))
    if not c["all_pass"]: print("REFUSE: control failed"); return 2
    t0 = time.time()
    hdr = AD.header("round34/B1/orbits-v3-pfv3",
                    key_space="bash 4.2 $RANDOM%29 auto-seed orbit 74x2^20=77,594,624 seeds (LP64 full; ILP32 stated fraction, chunk order Random(3301)); PHP mt_rand tier a 48,036 + tier b uniform default_rng(3301) of 2^32; mt+php(<=7.0) x scale29+mod29; offset 0, sign -1, C[0]-aligned",
                    decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400; keyskip1=advance1 keyskip2=advance2; sign -1 o=0; L120 screen / L240 gate",
                    v3_version="round33/I1 beam_v3.py panel_max; bars round34/I1 bars_v3 (gumbel, lp2)",
                    prefilter={"name": "round34/I2 pf_v3", "stat": "lse over nine registers of head trigram LLR vs uniform", "m": M_PF, "thr_nats": THR,
                               "fpr": "~1e-3", "power_EN_NOVOWEL": 0.998, "power_weakest_register": 0.9905, "rows_only_for": "prefilter survivors (tier a core: all seeds)"},
                    register_panel="round32/I2 nine-register panel (models/panel.npz)", n_round_adjudicated_reference=N_DECL,
                    seed_sample="bash: 296 chunks of 2^18 shuffled Random(3301); PHP tier b numpy default_rng(3301) blocks 2^17")
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    cells = list(BASH) + [cname(c) for c in PHP_CELLS]
    st = {"cells": {k: {"seeds_screened": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}, "hist": {}} for k in cells},
          "phase": {}, "caps_s": CAPS}
    keep = []
    if resume:
        st = json.load(open(SUMF)); keep = json.load(open(KEEPF))

    def note(cell, rows):
        S = st["cells"][cell]
        for r in rows:
            S["decodes"][r["rel"]] += 1
            b = S["best"].get(r["rel"])
            if b is None or r["pmax"] > b["pmax"]: S["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"]}
            h = S["hist"].setdefault(r["rel"], {}); k = "%d" % math.floor(r["pmax"]); h[k] = h.get(k, 0) + 1
            if r["pmax"] >= KEEP: keep.append(r)

    def save(done=False):
        st["elapsed_s"] = round(time.time() - t0, 1); st["complete_all_phases"] = done
        json.dump(st, open(SUMF, "w"), indent=1)
        json.dump(keep, open(KEEPF, "w"))

    chunks = [(p, s) for p in PREF for s in range(0, 1 << 20, SUB)]
    random.Random(3301).shuffle(chunks)
    C = C_SCREEN
    for v in (() if resume else BASH):
        ts = time.time(); ph = {"chunks_total": len(chunks), "chunks_done": 0, "cap_s": CAPS[v]}
        st["phase"][v] = ph
        for (p, s) in chunks:
            if time.time() - ts > CAPS[v]: break
            seeds = np.arange((p << 20) | s, ((p << 20) | s) + SUB, dtype=np.uint64)
            n_s, rows = chunk_bash(seeds, v, C, out)
            S = st["cells"][v]; S["seeds_screened"] += SUB; S["survivors"] += n_s; note(v, rows)
            ph["chunks_done"] += 1; ph["elapsed_s"] = round(time.time() - ts, 1)
            if ph["chunks_done"] % 4 == 0:
                out.flush(); save()
                print("%s chunk %d/%d t=%.0fs surv=%d best=%s" % (v, ph["chunks_done"], len(chunks), time.time() - ts, S["survivors"], S["best"]), flush=True)
        ph["fraction_of_orbit"] = ph["chunks_done"] / len(chunks); ph["complete"] = ph["chunks_done"] == len(chunks)
        out.flush(); save()
    tp = time.time(); ph = {"cap_s": CAPS["php_total"]}; st["phase"]["php"] = ph
    core, dense = php_tier_a()
    ph.update(tier_a_core=len(core), tier_a_dense=len(dense), tier_b_seeds=0)
    for s, lab in core:
        for cell in PHP_CELLS: note(cname(cell), decode_seed(cname(cell), s, C, out))
    for cell in PHP_CELLS:
        st["cells"][cname(cell)]["seeds_screened"] += len(core)
        st["cells"][cname(cell)]["survivors"] += len(core)       # core decoded unfiltered (all seeds are 'survivors')
    dseeds = np.array([s for s, _ in dense], dtype=np.uint64)
    for i in range(0, len(dseeds), BLK):
        blk = dseeds[i:i + BLK]
        for k, (ns, rows) in chunk_php(blk, C, out).items():
            S = st["cells"][k]; S["survivors"] += ns; S["seeds_screened"] += len(blk); note(k, rows)
    out.flush(); save(); ph["tier_a_done_s"] = round(time.time() - tp, 1)
    print("php tier a done %.0fs" % (time.time() - tp), flush=True)
    rng = np.random.default_rng(3301); nb = 0
    while time.time() - tp < CAPS["php_total"]:
        blk = rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)
        for k, (ns, rows) in chunk_php(blk, C, out).items():
            S = st["cells"][k]; S["survivors"] += ns; S["seeds_screened"] += BLK; note(k, rows)
        ph["tier_b_seeds"] += BLK; ph["elapsed_s"] = round(time.time() - tp, 1); nb += 1
        if nb % 5 == 0:
            out.flush(); save(); print("php b seeds=%d t=%.0fs" % (ph["tier_b_seeds"], time.time() - tp), flush=True)
    ph["tier_b_fraction_of_2p32"] = ph["tier_b_seeds"] / 2.0 ** 32
    out.close(); save(True); print("SWEEP DONE")
    return 0


# ------------------------------------------------------------------ finalize
def finalize():
    st = json.load(open(SUMF)); keep = json.load(open(KEEPF))
    summ = {"cells": {}, "flagged": [], "near_miss": []}
    for cell, S in st["cells"].items():
        for rel in ("keyskip1", "keyskip2"):
            N = S["decodes"][rel]
            if N == 0: continue
            b120, b240 = bar_v3(N, 120, rel), bar_v3(N, 240, rel)
            d120, d240 = bar_v3(N_DECL, 120, rel), bar_v3(N_DECL, 240, rel)
            best = S["best"][rel]
            cand = sorted([r for r in keep if r["cell"] == cell and r["rel"] == rel], key=lambda r: -r["pmax"])
            clear = [r for r in cand if r["pmax"] >= b120]
            ent = {"N_actual": N, "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3),
                   "bar240_declN": round(d240, 3), "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"],
                   "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"]) for r in cand[:5]]}
            for r in clear:
                K = keyfn(cell, r["seed"]); d, a = v3dec(C_HIT, K, rel); p240 = float(a["pmax"])
                e = {"cell": cell, "rel": rel, "seed": r["seed"], "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3),
                     "preg240": PAN.registers[a["preg"]], "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3),
                     "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (cell, rel)] = ent
    json.dump(summ, open(os.path.join(HERE, "sweep_summary_final.json"), "w"), indent=1)
    for k, v in summ["cells"].items():
        print(k, v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"], v["clears_declN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]))


if __name__ == "__main__":
    a = sys.argv[1]
    sys.exit({"control": control, "sweep": sweep, "php": lambda: sweep(True), "finalize": finalize}[a]())
