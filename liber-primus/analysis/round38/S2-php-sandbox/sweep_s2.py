#!/usr/bin/env python3
"""R38 S2: PHP mt_rand tier (b) on the sandbox: pf_v4_12 + beam_v3 panel_max under panel-R36. Runs identically on laptop/sandbox.
Usage: python sweep_s2.py smoke | fpr | control [W] | window NAME STREAMSEED B0 B1 CAP_S [WORKERS] | finalize
Writes ONLY inside this file's directory."""
import os, sys, json, time, random, math, hashlib, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round38/S2-php-sandbox"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32, R33, R36, R37 = [os.path.join(LP, "analysis", "round%d" % r) for r in (32, 33, 36, 37)]
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
PM = _load("php_mt", os.path.join(R32, "B2-php-mtrand", "php_mt.py"))
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V                                  # noqa: E402
sys.path.insert(0, os.path.join(R37, "I2-pfv4-12reg"))
import pf_v4_12 as pf                                # noqa: E402
P12_PATH = os.path.join(LP, "data", "panels", "panel-r36.npz"); P12_SHA = pf.PANEL_SHA
AD = C1.AD; B2 = V.B2; U = C1.U
V.set_panel(P12_PATH); PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN
assert V.A is AD and len(PAN.registers) == 12 and V.panel() is PAN
NULL12 = json.load(open(os.path.join(R36, "B1-orbit-12reg", "null12.json")))["cells"]


def bar_v3(N, L, rel):
    c = NULL12["L%d|%s" % (L, rel)]
    return c["mu"] + c["beta"] * math.log(N / -math.log(0.99))


TEST = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
L_SCREEN, L_HIT = 120, 240
C_SCREEN = U[:L_SCREEN]
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip2", "keyskip1")
FZ = pf.FROZEN; M_PF = FZ["m"]; KSK = FZ["k"]; assert M_PF == 24 and KSK == 2
CELLS = [("mt", "scale"), ("mt", "mod"), ("php", "scale"), ("php", "mod")]
CN = ["%s_%s" % c for c in CELLS]
BLK = 1 << 17; N_DECL = 10 ** 6; KEEP = 6.0
F = lambda n: os.path.join(HERE, n)
CALF, ROWS, SUMF, KEEPF, FPRF = F("control.json"), F("sweep_rows.jsonl"), F("sweep_state.json"), F("keep_rows.json"), F("fpr12_php.json")
NPL = 10; CTRL_REGS = ("EN_MODERN", "EN_NOVOWEL", "HEBREW")


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])


def cellkey(cn, seed, n=1024):
    tw, rd = cn.split("_"); return PM.ks(int(seed), tw, rd, n)


def php_masks(K, Chead):
    out = []
    for a in (1, 2):
        R = pf.dp_regs(Chead, K[:M_PF + a * KSK], KSK, a, FZ["pen_a%d" % a], ms=(M_PF,))
        out.append(pf.lse_from_regs(R[M_PF], M_PF) > FZ["thr"]["a%d" % a])
    return out


def decode_cell(cn, seed, C, lines):
    K = cellkey(cn, seed); res = []
    for rel in RELS:
        d, a = v3dec(C[:L_SCREEN], K, rel)
        lines.append(json.dumps(AD.to_row(a, "php:%s:%d:%s" % (cn, seed, rel))))
        res.append({"seed": int(seed), "cell": cn, "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]]})
    return res


def block_screen(seeds, C, lines, cells=CN):
    H = PM.heads_all(seeds, M_PF + 2 * KSK); Ch = np.array(C[:M_PF], dtype=np.int8); res = {}
    for cn in cells:
        tw, rd = cn.split("_"); K = PM.reduce_heads(H[tw], rd); m1, m2 = php_masks(K, Ch); m = m1 | m2; rows = []
        for s in seeds[m]: rows += decode_cell(cn, int(s), C, lines)
        res[cn] = {"n_surv": int(m.sum()), "n_a1": int(m1.sum()), "n_a2": int(m2.sum()), "rows": rows}
    return res


def _work(args):
    seeds, tag = args; t = time.time(); lines = []
    r = block_screen(seeds, C_SCREEN, lines)
    return tag, r, lines, time.time() - t


def plant(rel, reg, cn, rng):
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(500):
        ps = rng.randrange(1 << 32); K = cellkey(cn, ps)
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + L_HIT].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:L_HIT]
        if len(C) < L_HIT: continue
        if any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(P[i] + K[i]) % 29 for i in range(L_HIT)]
        return ps, C, P, int(any(C[i] != naive[i] for i in range(24))), K
    raise RuntimeError("no plant")


# ------------------------------------------------------------------ smoke
def smoke():
    rng = random.Random(7)
    ps, C, P, wsk, K = plant("keyskip1", "EN_MODERN", "mt_scale", rng)
    base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
    t = time.time(); res = block_screen(seeds, C, [], cells=["mt_scale"])["mt_scale"]
    pf_pass = any(r["seed"] == ps for r in res["rows"])
    d, a = v3dec(C, K, "keyskip1"); rec = float(B2.recovery(d["plain_idx"], P))
    out = {"imports_ok": True, "n_registers": len(PAN.registers), "panel_sha_ok": hashlib.sha256(open(P12_PATH, "rb").read()).hexdigest() == P12_SHA,
           "planted_seed": int(ps), "with_skip_head24": bool(wsk), "prefilter_pass": bool(pf_pass), "chunk_survivors": res["n_surv"], "pmax240": round(float(a["pmax"]), 3),
           "recovery240": round(rec, 4), "php_mt_selftest": PM.selftest(), "chunk_s": round(time.time() - t, 1), "ok": bool(pf_pass and rec >= 0.9)}
    json.dump(out, open(F("smoke.json"), "w"), indent=1); print(json.dumps(out)); return 0 if out["ok"] else 1


# ------------------------------------------------------------------ fpr
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 6), round((c + h) / d, 6)]


def fpr():
    rng = np.random.default_rng(3399); seeds = rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)
    H = PM.heads_all(seeds, M_PF + 2 * KSK); Ch = np.array(C_SCREEN[:M_PF], dtype=np.int8); res = {}
    for cn in CN:
        tw, rd = cn.split("_"); K = PM.reduce_heads(H[tw], rd); m1, m2 = php_masks(K, Ch)
        res[cn] = {"n": BLK, "pass_a1": int(m1.sum()), "pass_a2": int(m2.sum()), "pass_union": int((m1 | m2).sum()),
                   "fpr_a1": float(m1.mean()), "fpr_a2": float(m2.mean()), "fpr_union": float((m1 | m2).mean()), "wilson95_union": wilson(int((m1 | m2).sum()), BLK)}
    tot = sum(v["pass_union"] for v in res.values()); n = BLK * 4
    out = {"what": "PHP-cell prefilter FPR under frozen 12-register pf_v4_12 point (thr a1 %.4f / a2 %.4f); wrong-key heads = uniform seeds default_rng(3399) x 2^17; ciphertext head = LP2 C[:24]" % (FZ["thr"]["a1"], FZ["thr"]["a2"]),
           "target_total": FZ["fpr_target_total"], "cells": res, "pooled": {"n": n, "pass_union": tot, "fpr_union": tot / n, "wilson95": wilson(tot, n)}}
    json.dump(out, open(FPRF, "w"), indent=1); print(json.dumps(out["pooled"]))
    for k, v in res.items(): print(k, v["fpr_union"], v["pass_union"])
    return 0


# ------------------------------------------------------------------ control
def _ctl_one(args):
    cn, rel, reg, j, pseed = args; rng = random.Random(pseed)
    ps, Cp, P, wsk, K = plant(rel, reg, cn, rng)
    base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
    r = block_screen(seeds, Cp, [], cells=[cn])[cn]; mine = [x for x in r["rows"] if x["seed"] == ps and x["rel"] == rel]
    e = {"cell": cn, "rel": rel, "register": reg, "j": j, "seed": int(ps), "with_skip_head24": bool(wsk), "prefilter_pass": any(x["seed"] == ps for x in r["rows"]),
         "survivors_in_chunk": r["n_surv"], "pmax120": None, "pmax240": None, "recovery240": None, "pass": False, "recover": False}
    if mine:
        bars = {L: bar_v3(N_DECL, L, rel) for L in (120, 240)}
        e["pmax120"] = round(mine[0]["pmax"], 3)
        d, a = v3dec(Cp, K, rel); e["pmax240"] = round(float(a["pmax"]), 3); e["recovery240"] = round(float(B2.recovery(d["plain_idx"], P)), 4)
        e["pass"] = bool(e["pmax120"] >= bars[120] and e["pmax240"] >= bars[240]); e["recover"] = bool(e["pass"] and e["recovery240"] >= 0.90)
    return e


def control(workers=2):
    import multiprocessing as mp
    t0 = time.time(); master = random.Random(3301); jobs = []
    for cn in CN:
        for rel in ("keyskip1", "keyskip2"):
            for reg in CTRL_REGS:
                for j in range(NPL): jobs.append((cn, rel, reg, j, master.randrange(1 << 60)))
    plants = []
    with mp.get_context("fork").Pool(workers) as pool:
        for i, e in enumerate(pool.imap_unordered(_ctl_one, jobs)):
            plants.append(e)
            if i % 10 == 0: print("%.0fs plant %d/%d" % (time.time() - t0, i, len(jobs)), flush=True)
    plants.sort(key=lambda e: (e["cell"], e["rel"], e["register"], e["j"]))

    def tab(sel):
        o = {}
        for reg in CTRL_REGS:
            for sk in (False, True):
                q = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == sk]
                o["%s|%s" % (reg, "with_skip" if sk else "skip_free")] = {"n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "pass": sum(p["pass"] for p in q), "recover": sum(p["recover"] for p in q)}
        return o
    pooled = tab(lambda p: True)
    per = {"%s|%s" % (cn, rel): tab(lambda p, cn=cn, rel=rel: p["cell"] == cn and p["rel"] == rel) for cn in CN for rel in ("keyskip1", "keyskip2")}
    per_reg = {}
    for cn in CN:
        for rel in ("keyskip1", "keyskip2"):
            for reg in CTRL_REGS:
                q = [p for p in plants if p["cell"] == cn and p["rel"] == rel and p["register"] == reg]
                per_reg["%s|%s|%s" % (cn, rel, reg)] = {"n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "recover": sum(p["recover"] for p in q)}
    gate = all(c["recover"] >= 3 for c in pooled.values())
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "path": "real chunk path: pf_v4_12 frozen on a 2^16-seed chunk containing the plant -> v3 L120 both rels on survivors -> v3 L240; natural-rate plants real enc_exact/enc_pair; only filter C[:40] doublet-free; NO skip-free selection",
           "bars_declared_N1e6": {r: {"L120": bar_v3(N_DECL, 120, r), "L240": bar_v3(N_DECL, 240, r)} for r in ("keyskip1", "keyskip2")}, "plants_per_cell_rel_register": NPL,
           "pooled_by_register_skip": pooled, "per_cell_rel": per, "per_cell_rel_register": per_reg, "gate_ge3_recover_each_pooled_split": gate, "plants": plants, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(CALF, "w"), indent=1); print("POOLED", json.dumps(pooled)); print("GATE", gate); return 0 if gate else 1


# ------------------------------------------------------------------ windows
def window(name, sseed, b0, b1, cap_s, workers=2):
    import multiprocessing as mp
    c = json.load(open(CALF))
    if not c["gate_ge3_recover_each_pooled_split"]: print("REFUSE: control gate failed"); return 2
    t0 = time.time(); nonempty = os.path.exists(ROWS) and os.path.getsize(ROWS) > 0
    if nonempty and not os.path.exists(SUMF): print("REFUSE: non-empty store without state"); return 3
    if nonempty:
        st = json.load(open(SUMF)); keep = json.load(open(KEEPF)); out = open(ROWS, "a")
    else:
        hdr = AD.header("round38/S2/php-sandbox-pfv4-12reg", pan=PAN,
                        key_space="PHP 5.x mt_rand: twist {mt canonical, php<=7.0 legacy} x reduction {scale29, mod29} = 4 cells; tier b = uniform numpy default_rng(stream) blocks of 2^17 over [0,2^32), equal fraction per cell; streams 3301 (blocks>=199) and 3302; offset 0, sign -1, C[0]-aligned",
                        decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400 under panel-R36; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate",
                        v3_version="round33/I1 beam_v3.py panel_max (set_panel -> panel-R36); bars round36/B1 null12.json POT fit",
                        prefilter={"name": "round37/I2 pf_v4_12 (lse over 12 panel-R36 LMs)", "m": M_PF, "k": KSK, "rel": "both", "thr_a1": FZ["thr"]["a1"], "thr_a2": FZ["thr"]["a2"], "pen": 2,
                                   "per_relation_fpr": 5e-4, "fpr": "PHP-cell FPR measured in fpr12_php.json", "frozen_op": "analysis/round37/I2-pfv4-12reg/frozen_op12.json", "rows_only_for": "prefilter survivors"},
                        register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=P12_SHA, n_registers=12,
                        panel_build="panel-R36 (round36/P1 build1; sha256 " + P12_SHA[:8] + ")", corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)",
                        n_round_adjudicated_reference=N_DECL, seed_sample="numpy default_rng(3301/3302) blocks 2^17")
        out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n"); out.flush(); st = {"windows": {}, "cells": {}}; keep = []
    W = st["windows"].setdefault(name, {"stream": sseed, "b0": b0, "b1": b1, "cap_s": cap_s, "blocks_done": [], "compute_s": 0.0,
                                        "cells": {cn: {"seeds": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}} for cn in CN}})
    done = set(W["blocks_done"])
    for cn in CN: st["cells"].setdefault(cn, {"decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}})

    def note(cn, rows):
        for D in (W["cells"][cn], st["cells"][cn]):
            for r in rows:
                D["decodes"][r["rel"]] += 1; b = D["best"].get(r["rel"])
                if b is None or r["pmax"] > b["pmax"]: D["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"], "block": r.get("block")}
        for r in rows:
            if r["pmax"] >= KEEP: keep.append(r)

    def save():
        out.flush(); W["elapsed_s"] = round(time.time() - t0, 1)
        json.dump(st, open(SUMF + ".tmp", "w"), indent=1); os.replace(SUMF + ".tmp", SUMF)
        json.dump(keep, open(KEEPF + ".tmp", "w")); os.replace(KEEPF + ".tmp", KEEPF)

    rng = np.random.default_rng(sseed)
    for _ in range(b0): rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)

    def gen():
        for b in range(b0, b1 + 1):
            blk = rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)
            if b in done: continue
            if time.time() - t0 > cap_s: return
            yield (blk, b)
    nb = 0
    with mp.get_context("fork").Pool(workers) as pool:
        for tag, res, lines, dt in pool.imap_unordered(_work, gen(), chunksize=1):
            for ln in lines: out.write(ln + "\n")
            for cn, r in res.items():
                for x in r["rows"]: x["block"] = tag; x["win"] = name
                W["cells"][cn]["seeds"] += BLK; W["cells"][cn]["survivors"] += r["n_surv"]; note(cn, r["rows"])
            W["blocks_done"].append(tag); W["compute_s"] += dt; nb += 1; save()
            if nb % 4 == 0: print("%s blocks %d wall %.0fs best %s" % (name, len(W["blocks_done"]), time.time() - t0, {cn: W["cells"][cn]["best"] for cn in CN}), flush=True)
    W["complete_range"] = len(W["blocks_done"]) == (b1 - b0 + 1); W["wall_s"] = round(time.time() - t0, 1); save(); out.close()
    print("WINDOW DONE", name, "blocks", len(W["blocks_done"]), "wall", W["wall_s"]); return 0


# ------------------------------------------------------------------ finalize
def finalize():
    st = json.load(open(SUMF)); keep = json.load(open(KEEPF)); summ = {"windows": {}, "cells": {}, "flagged": [], "near_miss": []}
    for wn, W in st["windows"].items():
        bd = W["blocks_done"]
        summ["windows"][wn] = {"stream": W["stream"], "range": [W["b0"], W["b1"]], "blocks_done": len(bd), "blocks_min_max": [min(bd, default=None), max(bd, default=None)],
                               "compute_s": round(W["compute_s"], 1), "wall_s": W.get("wall_s"), "cells": {}}
        for cn in CN:
            D = W["cells"][cn]; e = {"seeds": D["seeds"], "survivors": D["survivors"], "decodes": D["decodes"], "best": D["best"]}
            for rel in ("keyskip1", "keyskip2"):
                if D["decodes"][rel]: e["bar120_N_" + rel] = round(bar_v3(D["decodes"][rel], 120, rel), 3)
            summ["windows"][wn]["cells"][cn] = e
    for cn in CN:
        S = st["cells"][cn]
        for rel in ("keyskip1", "keyskip2"):
            N = S["decodes"][rel]
            if N == 0: continue
            b120, b240 = bar_v3(N, 120, rel), bar_v3(N, 240, rel); d120, d240 = bar_v3(N_DECL, 120, rel), bar_v3(N_DECL, 240, rel); best = S["best"][rel]
            cand = sorted([r for r in keep if r["cell"] == cn and r["rel"] == rel], key=lambda r: -r["pmax"])
            ent = {"N_actual": N, "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3), "bar240_declN": round(d240, 3),
                   "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"], "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"], r.get("win"), r.get("block")) for r in cand[:5]]}
            for r in [r for r in cand if r["pmax"] >= b120]:
                d, a = v3dec(U[:L_HIT], cellkey(cn, r["seed"]), rel); p240 = float(a["pmax"])
                e = {"cell": cn, "rel": rel, "seed": r["seed"], "win": r.get("win"), "block": r.get("block"), "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3),
                     "preg240": PAN.registers[a["preg"]], "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3), "clears240_actualN": bool(p240 >= b240),
                     "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (cn, rel)] = ent
    json.dump(summ, open(F("sweep_summary_final.json"), "w"), indent=1)
    for k, v in summ["cells"].items(): print(k, v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"], v["clears_declN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "window": sys.exit(window(a[1], int(a[2]), int(a[3]), int(a[4]), float(a[5]), int(a[6]) if len(a) > 6 else 2))
    if a[0] == "control": sys.exit(control(int(a[1]) if len(a) > 1 else 2))
    sys.exit({"smoke": smoke, "fpr": fpr, "finalize": finalize}[a[0]]())
