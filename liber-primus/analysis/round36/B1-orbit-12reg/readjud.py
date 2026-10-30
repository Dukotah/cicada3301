#!/usr/bin/env python3
"""R36 B1: round35/B1 bash-orbit survivors re-decoded (v3 panel_max) and adjudicated under panel-R36 (12 registers).
python readjud.py null|control|pfpower|run [budget_s]|final     (one stage per process; resumable; writes only in this dir)"""
import os, sys, re, json, time, math, random, heapq, hashlib, importlib.util, subprocess
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round36/B1-orbit-12reg"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32, R33, R34, R35, R36 = [os.path.join(LP, "analysis", "round%d" % r) for r in (32, 33, 34, 35, 36)]
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V
sys.path.insert(0, os.path.join(R35, "I1-skip-tolerant-screen"))
import pf_v4
sys.path.insert(0, os.path.join(R34, "I1-v3-null"))
from bars_v3 import bar_v3
FIT = _load("fit34", os.path.join(R34, "I1-v3-null", "fit.py"))
AD = C1.AD; B2 = V.B2; U = list(C1.U)
PAN9 = V.panel()                      # Round 32 nine-register panel (pf_v4 stays on this, frozen)
LMT9 = PAN9.LMT.astype(np.float32)
P12_PATH = os.path.join(R36, "P1-panel-r36", "build1", "panel12.npz")
TH12_PATH = os.path.join(R36, "P1-panel-r36", "build1", "testhalves12.npz")
P12_SHA = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
assert hashlib.sha256(open(P12_PATH, "rb").read()).hexdigest() == P12_SHA
PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN; V.PANEL_PATH = P12_PATH
REGS = list(PAN.registers); assert len(REGS) == 12
TEST = np.load(TH12_PATH)
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip1", "keyskip2")
BASH = ("bash4.2", "bash4.2_i32")
F = lambda n: os.path.join(HERE, n)
ROWS_SRC = os.path.join(R35, "B1-bash-orbit-pfv4", "sweep_rows.jsonl")
ROWS = F("readjud_rows.jsonl")
T0 = time.time(); LOG = open(F("readjud.log"), "a")
SEC0, SEC1 = 1325376000, 1401580800
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1))


def log(*a):
    s = "[%6.0fs] " % (time.time() - T0) + " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def free_gb():
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"], capture_output=True, text=True, timeout=30).stdout
        return float(o.strip())
    except Exception:
        return 9.9


def wait_mem(minq=0.4, maxwait=1200):
    t = time.time()
    while True:
        g = free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        log("RAM wait: free %.2f GB" % g); time.sleep(60)


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])


def survivors():
    """-> {abi: sorted list of seeds} from the stored R35 rows (kid = bash:<abi>:<seed>:<rel>)."""
    by = {v: set() for v in BASH}; pat = re.compile(r'^\["([^"]+)"')
    with open(ROWS_SRC, encoding="utf-8") as f:
        f.readline()
        for line in f:
            p = pat.search(line[:120]).group(1).split(":")
            by[p[1]].add(int(p[2]))
    return {k: sorted(v) for k, v in by.items()}


# ---------------------------------------------------------------- 12-register bars from null12 stream
def load_null():
    cells = {}; seen = set()
    p = F("null12_stream.jsonl")
    if not os.path.exists(p): return cells
    for line in open(p):
        r = json.loads(line); k = (r["L"], r["rel"])
        if (k, r["i0"]) in seen: continue
        seen.add((k, r["i0"])); c = cells.setdefault(k, {"pm": [], "preg": []})
        c["pm"].extend(r["pm"]); c["preg"].extend(r["preg"])
    return cells


_BC = {}


def bar12(N, L, rel, alpha=0.01):
    if "f" not in _BC:
        cells = load_null(); _BC["f"] = {k: FIT.tailfit(v["pm"]) for k, v in cells.items()}
    f = _BC["f"][(L, rel)]
    return f["u"] + f["beta"] * math.log(f["p_u"]) + f["beta"] * math.log(float(N) / -math.log1p(-alpha))


# ---------------------------------------------------------------- null
def null_stage():
    by = survivors(); out = open(F("null12_stream.jsonl"), "a")
    done = {}
    for k, c in load_null().items(): done[k[0]] = max(done.get(k[0], 0), len(c["pm"]))
    PLAN = [(120, 25000), (240, 4000)]
    for L, target in PLAN:
        k0 = done.get(L, 0)
        if k0 >= target: continue
        wait_mem(); n = max(1024, 6 * L + 64); buf = {r: [] for r in RELS}; t0 = time.time(); k = k0
        while k < target:
            sh = U[:]; random.Random(3301 + k).shuffle(sh); C = sh[:L]
            rg = random.Random(3301 + k * 13 + L); v = BASH[k % 2]; seed = rg.choice(by[v])
            K = C1.ks(seed, v, n)
            for r in RELS: buf[r].append(V.beam_decode_v3(C, K, ADV[r], "panel_max", tau=0.0, lam_u=4.0)["plain_idx"])
            k += 1
            if k % 200 == 0 or k == target:
                for r in RELS:
                    X = np.asarray(buf[r], dtype=np.int64); res = AD.adjudicate_batch(X)
                    out.write(json.dumps({"L": L, "rel": r, "i0": k - len(X), "pm": [round(float(x), 4) for x in res["pmax"]], "preg": [int(x) for x in res["preg"]]}) + "\n")
                    buf[r] = []
                out.flush(); log("null L%d" % L, k, "of", target, "%.0f draws/s" % ((k - k0) / (time.time() - t0)))
                if k % 2000 == 0: wait_mem()
    out.close(); fin_null()


def fin_null():
    cells = load_null(); res = {"panel_sha256": P12_SHA, "n_registers": 12, "family": "shuffled real LP2 wrong-key, keys = R35 survivor bash seeds (ABI alternating)",
                                "method": "POT exponential tail above empirical 90th pct (round34 fit.tailfit); bar = mu + beta ln(N/-ln(0.99)); beta from the node at its own L", "cells": {}}
    for (L, rel), c in sorted(cells.items()):
        f = FIT.tailfit(c["pm"]); a = np.array(c["pm"]); pr = np.bincount(c["preg"], minlength=12)
        f["argmax_register_share"] = {REGS[i]: round(float(pr[i]) / len(a), 4) for i in range(12)}
        f["bars"] = {"N=%g" % N: round(bar12(N, L, rel), 3) for N in (69017, 69104, 1e6)}
        f["bars9_bar_v3"] = {"N=%g" % N: round(bar_v3(N, L, rel), 3) for N in (69017, 69104, 1e6)}
        f["emp_q999"] = float(np.quantile(a, .999)); res["cells"]["L%d|%s" % (L, rel)] = f
    json.dump(res, open(F("null12.json"), "w"), indent=1)
    for k, f in res["cells"].items(): log("NULL", k, "n", f["n"], "mean %.3f max %.3f" % (f["mean"], f["emp_max"]), f["bars"], "9-reg", f["bars9_bar_v3"])


# ---------------------------------------------------------------- controls
def plant(v, rel, reg, rng, by, L=240):
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(500):
        ps = rng.choice(by[v]) if by else (rng.choice(PREF) << 20) | rng.randrange(1 << 20)
        K = C1.ks(ps, v, 1024); st = rng.randrange(0, len(arr) - 300); P = arr[st:st + L].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:L]
        if len(C) < L or any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(P[i] + K[i]) % 29 for i in range(L)]
        return ps, K, C, P, int(any(C[i] != naive[i] for i in range(24)))
    raise RuntimeError("no plant")


def control_stage():
    wait_mem(); by = survivors(); rng = random.Random(3301); plants = []; t0 = time.time()
    NP = 8
    b = {rel: {"L120": bar12(1e6, 120, rel), "L240": bar12(1e6, 240, rel)} for rel in RELS}
    for reg in ("GREEK", "HEBREW", "NORSE"):
        for rel in RELS:
            for j in range(NP):
                v = BASH[j % 2]; ps, K, C, P, wsk = plant(v, rel, reg, rng, by)
                d1, a1 = v3dec(C[:120], K, rel); d2, a2 = v3dec(C, K, rel)
                rec = float(B2.recovery(d2["plain_idx"], P)); rec120 = float(B2.recovery(d1["plain_idx"], P))
                e = {"register": reg, "rel": rel, "abi": v, "seed": ps, "with_skip_head24": bool(wsk),
                     "pmax120": round(float(a1["pmax"]), 3), "preg120": REGS[a1["preg"]], "recovery120": round(rec120, 4),
                     "pmax240": round(float(a2["pmax"]), 3), "preg240": REGS[a2["preg"]], "recovery240": round(rec, 4)}
                e["pass"] = bool(e["pmax120"] >= b[rel]["L120"] and e["pmax240"] >= b[rel]["L240"]); e["recover"] = bool(e["pass"] and rec >= 0.90)
                e["own_argmax"] = bool(e["preg120"] == reg and e["preg240"] == reg); plants.append(e)
            log("stage2 control", reg, rel, "%.0fs" % (time.time() - t0))
    tab = {}
    for reg in ("GREEK", "HEBREW", "NORSE"):
        for rel in RELS + ("both",):
            ps_ = [p for p in plants if p["register"] == reg and (rel == "both" or p["rel"] == rel)]
            tab["%s|%s" % (reg, rel)] = {"n": len(ps_), "pass": sum(p["pass"] for p in ps_), "recover": sum(p["recover"] for p in ps_), "own_argmax": sum(p["own_argmax"] for p in ps_),
                                         "rec120_ge90": sum(p["recovery120"] >= .9 for p in ps_), "min_pmax120": min(p["pmax120"] for p in ps_)}
    gate_new = all(tab["%s|both" % r]["recover"] >= 5 for r in ("GREEK", "HEBREW", "NORSE"))
    nat = natural_control(by, b)
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": P12_SHA, "bars_declared_N1e6_12reg": b,
           "stage2_path": "v3 panel_max with the true key handed over, L=120 and L=240, panel-R36; plants from testhalves12; keys = R35 survivor seeds (ABI alternating)",
           "stage2_new_registers": tab, "stage2_gate_ge5_recover_each": gate_new, "stage2_plants": plants, "natural_rate_rescore": nat, "all_pass": bool(gate_new and nat["gate"])}
    json.dump(out, open(F("control.json"), "w"), indent=1)
    log("CONTROL stage2", json.dumps({k: (v["recover"], v["n"]) for k, v in tab.items() if k.endswith("both")}), "natural gate", nat["gate"], "pooled", nat["pooled"])


def natural_control(by, bars):
    """Round 35 B1 natural-rate control, same RNG/plant rule, pf_v4 on the frozen 9-register LMT, v3 + bars under panel-R36."""
    rng = random.Random(3301); plants = []; M = pf_v4.FROZEN["m"]; t0 = time.time()
    for v in BASH:
        for rel in RELS:
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                for j in range(12):
                    ps, K, C, P, wsk = plant(v, rel, reg, rng, None)
                    m = pf_v4.prefilter_mask(np.array([ps], dtype=np.uint64), v, np.array(C[:M], dtype=np.int8), LMT9, M, "both")
                    e = {"abi": v, "rel": rel, "register": reg, "seed": int(ps), "with_skip_head24": bool(wsk), "prefilter_pass": bool(m[0]), "pass": False, "recover": False}
                    if e["prefilter_pass"]:
                        d1, a1 = v3dec(C[:120], K, rel); d2, a2 = v3dec(C, K, rel)
                        e["pmax120"] = round(float(a1["pmax"]), 3); e["pmax240"] = round(float(a2["pmax"]), 3); e["preg120"] = REGS[a1["preg"]]
                        e["recovery240"] = round(float(B2.recovery(d2["plain_idx"], P)), 4)
                        e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"] and e["pmax240"] >= bars[rel]["L240"]); e["recover"] = bool(e["pass"] and e["recovery240"] >= .9)
                    plants.append(e)
            log("natural", v, rel, "%.0fs" % (time.time() - t0))
    pooled = {}
    for reg in ("EN_MODERN", "EN_NOVOWEL"):
        for sk in (False, True):
            q = [p for p in plants if p["register"] == reg and p["with_skip_head24"] == sk]
            pooled["%s|%s" % (reg, "with_skip" if sk else "skip_free")] = {"n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "pass": sum(p["pass"] for p in q), "recover": sum(p["recover"] for p in q)}
    passers = [p for p in plants if p["prefilter_pass"]]
    return {"pooled": pooled, "gate": all(c["recover"] >= 3 for c in pooled.values()),
            "v3_recovery_on_prefilter_passers": [sum(p["recover"] for p in passers), len(passers)],
            "note": "pf_v4 evaluated on the single plant seed (thresholds are absolute, so identical to the 2^16 chunk path); plants regenerated with R35's rule (key seed drawn from the full prefix space as in R35, testhalves12 text)", "plants": plants}


def pfpower_stage():
    """pf_v4 natural power per register via planted heads (no selection other than C[:40] doublet-free)."""
    wait_mem(); rng = random.Random(33011); M = pf_v4.FROZEN["m"]; res = {}; t0 = time.time(); NP = 100
    for reg in ("EN_MODERN", "GREEK", "HEBREW", "NORSE"):
        c = {"keyskip1": [0, 0], "keyskip2": [0, 0]}
        for j in range(NP):
            rel = RELS[j % 2]; v = BASH[(j // 2) % 2]; ps, K, C, P, wsk = plant(v, rel, reg, rng, None, L=60)
            m = pf_v4.prefilter_mask(np.array([ps], dtype=np.uint64), v, np.array(C[:M], dtype=np.int8), LMT9, M, "both")
            c[rel][1] += 1; c[rel][0] += int(bool(m[0]))
        res[reg] = {rel: {"pass": a, "n": n, "power": round(a / n, 3)} for rel, (a, n) in c.items()}
        res[reg]["pooled"] = round((c["keyskip1"][0] + c["keyskip2"][0]) / NP, 3); log("pfpower", reg, res[reg], "%.0fs" % (time.time() - t0))
    json.dump({"n_per_register": NP, "design": "natural-rate plants, real enc_exact/enc_pair, ABI mixed, key seed from the prefix space, only filter C[:40] doublet-free; pf_v4 frozen on the 9-register LMT", "power": res}, open(F("pfpower_new.json"), "w"), indent=1)


# ---------------------------------------------------------------- re-decode run
def run_stage(budget):
    wait_mem(); by = survivors(); units = [(v, s) for v in BASH for s in by[v]]
    random.Random(3301).shuffle(units)
    hdr = AD.header("round36/B1/orbit-12reg-readjud", pan=PAN,
                    key_space="STORED R35-B1 pf_v4 survivor seeds (bash 4.2 LP64 %d + ILP32 %d), unit=(ABI,seed) both relations, Random(3301) shuffle, wall cap" % (len(by[BASH[0]]), len(by[BASH[1]])),
                    decoder="beam_decode_v3 design panel_max (hard max, lam_u=4, beam_w=400), keyskip1=advance1 keyskip2=advance2, sign -1, o=0, L=120 on LP2[:120]",
                    v3_version="round33/I1 beam_v3.py panel_max (PANEL repointed to panel-R36)", register_panel="panel-R36 round36/P1-panel-r36/build1/panel12.npz",
                    panel_sha256=P12_SHA, n_registers=12, panel_build="panel-R36 (P1 build1, byte-reproducible; sha256 " + P12_SHA[:8] + ")",
                    corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)", universe_units=len(units), universe_rows=2 * len(units))
    done = 0
    if os.path.exists(ROWS):
        with open(ROWS, "rb") as f: lines = f.read().split(b"\n")
        good = [l for l in lines[1:] if l.strip().endswith(b"]")]
        done = len(good) // 2
        with open(ROWS, "wb") as f: f.write(lines[0] + b"\n" + b"\n".join(good[:2 * done]) + (b"\n" if done else b""))
        log("resume: units done", done)
        out = open(ROWS, "a")
    else:
        out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    t0 = time.time(); n0 = done; i = done
    while i < len(units):
        if time.time() - t0 > budget: break
        v, s = units[i]; K = C1.ks(s, v, 1024); buf = ""
        for rel in RELS:
            d, a = v3dec(U[:120], K, rel); buf += json.dumps(AD.to_row(a, "v3:bash:%s:%d:%s" % (v, s, rel))) + "\n"
        out.write(buf); i += 1
        if i % 500 == 0:
            out.flush()
            if i % 2000 == 0:
                log("run units", i, "of", len(units), "%.1f units/s" % ((i - n0) / (time.time() - t0)))
                if free_gb() < 0.25: wait_mem(0.4)
    out.flush(); out.close()
    json.dump({"units_done": i, "units_total": len(units), "unit_fraction": i / len(units), "elapsed_s": round(time.time() - t0, 1), "budget_s": budget, "complete": i >= len(units)}, open(F("run_state.json"), "w"), indent=1)
    log("run finished", i, "of", len(units))


# ---------------------------------------------------------------- finalize
def validate12(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        h = json.loads(f.readline()); assert len(h["registers"]) == 12 and h["panel_sha256"] == P12_SHA
        for line in f:
            if line.strip(): AD.validate_row(json.loads(line), h, n_registers=12); n += 1
    return n


def final_stage():
    st = json.load(open(F("run_state.json")))
    cells = {}; heaps = {}
    with open(ROWS, encoding="utf-8") as f:
        hdr = json.loads(f.readline())
        for line in f:
            if not line.strip(): continue
            r = json.loads(line); p = r[0].split(":"); abi, seed, rel = p[2], int(p[3]), p[4]
            k = "%s|%s" % (abi, rel); c = cells.setdefault(k, {"N": 0, "best": -1e9, "best_kid": None, "preg_hist": [0] * 12, "best_z_by_reg": [-1e9] * 12, "hist": {}})
            pm, z = r[3], r[12]; c["N"] += 1; c["preg_hist"][r[4]] += 1
            for i in range(12):
                if z[i] > c["best_z_by_reg"][i]: c["best_z_by_reg"][i] = z[i]
            if pm > c["best"]: c["best"] = pm; c["best_kid"] = r[0]; c["best_preg"] = REGS[r[4]]
            hb = str(math.floor(pm)); c["hist"][hb] = c["hist"].get(hb, 0) + 1
            h = heaps.setdefault(k, []); item = (pm, seed, REGS[r[4]])
            if len(h) < 8: heapq.heappush(h, item)
            elif pm > h[0][0]: heapq.heapreplace(h, item)
    summ = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": P12_SHA, "run": st, "cells": {}, "flagged": [], "near_miss": []}
    for k, c in sorted(cells.items()):
        abi, rel = k.split("|"); N = c["N"]
        b120, b240 = bar12(N, 120, rel), bar12(N, 240, rel); d120, d240 = bar12(1e6, 120, rel), bar12(1e6, 240, rel)
        top = sorted(heaps[k], reverse=True)
        ent = {"N_actual": N, "best_pmax": round(c["best"], 3), "best_kid": c["best_kid"], "best_preg": c["best_preg"],
               "bar12_actualN": round(b120, 3), "bar12_N1e6": round(d120, 3), "bar12_L240_actualN": round(b240, 3), "bar12_L240_N1e6": round(d240, 3),
               "bar9_actualN": round(bar_v3(N, 120, rel), 3), "bar9_N1e6": round(bar_v3(1e6, 120, rel), 3),
               "clears_actualN": bool(c["best"] >= b120), "clears_N1e6": bool(c["best"] >= d120),
               "top8": [(round(p, 3), s, g) for p, s, g in top], "argmax_register_hist": {REGS[i]: c["preg_hist"][i] for i in range(12)},
               "best_z_by_register": {REGS[i]: round(c["best_z_by_reg"][i], 3) for i in range(12)}, "pmax_floor_hist": c["hist"]}
        for p, s, g in top:
            if p >= b120:
                K = C1.ks(s, abi, 1024); d, a = v3dec(U[:240], K, rel); p240 = float(a["pmax"])
                e = {"abi": abi, "rel": rel, "seed": s, "pmax120": round(p, 3), "preg120": g, "pmax240": round(p240, 3), "preg240": REGS[a["preg"]],
                     "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3), "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(p >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if p < d120: summ["near_miss"].append(e)
        summ["cells"][k] = ent
    summ["validate12_rows"] = validate12(ROWS)
    summ["validate_store_default9"] = "ok"
    try: AD.validate_store(ROWS)
    except Exception as ex: summ["validate_store_default9"] = "FAIL (expected, n_registers=9 default): %s" % str(ex)[:160]
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    summ["check_r3_store_unpatched"] = VL.check_r3_store(ROWS)
    miss = [x for x in VL.R3_STATS if x not in hdr.get("fields", [])]
    summ["check_r3_store_local12"] = [("header lacks R3 statistics %s" % miss)] if miss else []
    json.dump(summ, open(F("readjud_summary.json"), "w"), indent=1)
    for k, e in summ["cells"].items(): log("CELL", k, e["N_actual"], e["best_pmax"], e["best_preg"], "bar12", e["bar12_actualN"], e["bar12_N1e6"], "bar9", e["bar9_actualN"], e["bar9_N1e6"], e["clears_actualN"])
    log("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]), summ["validate12_rows"], summ["validate_store_default9"][:60], summ["check_r3_store_unpatched"], summ["check_r3_store_local12"])


if __name__ == "__main__":
    s = sys.argv[1]
    {"null": null_stage, "control": control_stage, "pfpower": pfpower_stage, "run": lambda: run_stage(float(sys.argv[2])), "final": final_stage}[s]()
