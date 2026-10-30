#!/usr/bin/env python3
"""R37 I2: bash 4.2 orbit (LP64, ILP32) under pf_v4_12 (twelve-register lse, frozen point, rel=both) + beam_v3 panel_max under panel-R36.
Usage: python sweep.py control | sweep | finalize.  Writes ONLY inside this file's directory."""
import os, sys, re, json, time, random, math, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round37/I2-pfv4-12reg"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32, R33, R34, R35, R36 = [os.path.join(LP, "analysis", "round%d" % r) for r in (32, 33, 34, 35, 36)]
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V                                  # noqa: E402
sys.path.insert(0, HERE)
import pf_v4_12 as pf_v4                             # noqa: E402  (12-register lse; same prefilter_mask API minus LMT)
P12_PATH = os.path.join(LP, "data", "panels", "panel-r36.npz"); P12_SHA = pf_v4.PANEL_SHA
import hashlib; assert hashlib.sha256(open(P12_PATH, "rb").read()).hexdigest() == P12_SHA
assert HERE == os.path.dirname(os.path.abspath(__file__))
AD = C1.AD; B2 = V.B2; U = C1.U
V.set_panel(P12_PATH); PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN
assert V.A is AD and len(PAN.registers) == 12 and V.panel() is PAN
REGS = list(PAN.registers)
NULL12 = json.load(open(os.path.join(R36, "B1-orbit-12reg", "null12.json")))["cells"]
def bar_v3(N, L, rel):
    c = NULL12["L%d|%s" % (L, rel)]
    return c["mu"] + c["beta"] * math.log(N / -math.log(0.99))
TEST = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
L_SCREEN, L_HIT = 120, 240
C_SCREEN = U[:L_SCREEN]
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip2", "keyskip1")
BASH = ("bash4.2", "bash4.2_i32")
M_PF = pf_v4.FROZEN["m"]; N_DECL = 10 ** 6; KEEP = 6.0
SEC0, SEC1 = 1325376000, 1401580800
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1)); assert len(PREF) == 74
SUB = 1 << 18
CAP_TOTAL, CAP_LP64 = int(os.environ.get("I2_CAP_TOTAL", 6300)), 3300
F = lambda n: os.path.join(HERE, n)
CALF, ROWS, SUMF, KEEPF = F("control.json"), F("sweep_rows.jsonl"), F("sweep_summary.json"), F("keep_rows.json")
NPL = 10
CTRL_REGS = ("EN_MODERN", "EN_NOVOWEL", "HEBREW", "NORSE")


def free_gb():
    import subprocess
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
        print("RAM wait: free %.2f GB" % g, flush=True); time.sleep(60)


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])


def decode_seed(v, seed, C, out=None):
    K = C1.ks(seed, v, 1024); res = []
    for rel in RELS:
        d, a = v3dec(C[:L_SCREEN], K, rel)
        if out is not None: out.write(json.dumps(AD.to_row(a, "bash:%s:%d:%s" % (v, seed, rel))) + "\n")
        res.append({"seed": int(seed), "cell": v, "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]]})
    return res


def chunk_bash(seeds, v, C, out=None):
    m = pf_v4.prefilter_mask(seeds, v, np.array(C[:M_PF], dtype=np.int8), M_PF, "both")
    surv = seeds[m]; rows = []
    for s in surv: rows += decode_seed(v, int(s), C, out)
    return len(surv), rows


# ------------------------------------------------------------------ control (natural-rate plants)
def plant(v, rel, reg, j, rng):
    """No skip-free selection. Only filter: realised ciphertext C[:40] doublet-free (as the real LP2 head)."""
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(500):
        ps = (rng.choice(PREF) << 20) | rng.randrange(1 << 20); K = C1.ks(ps, v, 1024)
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + L_HIT].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:L_HIT]
        if len(C) < L_HIT: continue
        if any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(P[i] + K[i]) % 29 for i in range(L_HIT)]
        nskip24 = int(any(C[i] != naive[i] for i in range(24)))
        return ps, C, P, nskip24
    raise RuntimeError("no plant")


def control():
    rng = random.Random(3301); plants = []; t0 = time.time()
    bars = {r: {"L120": bar_v3(N_DECL, 120, r), "L240": bar_v3(N_DECL, 240, r)} for r in ("keyskip1", "keyskip2")}
    for v in BASH:
        for rel in ("keyskip1", "keyskip2"):
            for reg in CTRL_REGS:
                for j in range(NPL):
                    ps, Cp, P, wsk = plant(v, rel, reg, j, rng)
                    base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                    n_s, rr = chunk_bash(seeds, v, Cp)
                    mine = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                    e = {"abi": v, "rel": rel, "register": reg, "seed": int(ps), "with_skip_head24": bool(wsk),
                         "prefilter_pass": any(r["seed"] == ps for r in rr), "survivors_in_chunk": n_s,
                         "pmax120": None, "pmax240": None, "recovery240": None, "pass": False, "recover": False}
                    if mine:
                        e["pmax120"] = round(mine[0]["pmax"], 3)
                        d, a = v3dec(Cp, C1.ks(ps, v, 1024), rel)
                        e["pmax240"] = round(float(a["pmax"]), 3); e["recovery240"] = round(float(B2.recovery(d["plain_idx"], P)), 4)
                        e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"] and e["pmax240"] >= bars[rel]["L240"])
                        e["recover"] = bool(e["pass"] and e["recovery240"] >= 0.90)
                    plants.append(e)
                print("%.0fs" % (time.time() - t0), v, rel, reg, flush=True)

    def tab(sel):
        out = {}
        for reg in CTRL_REGS:
            for sk in (False, True):
                ps_ = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == sk]
                out["%s|%s" % (reg, "with_skip" if sk else "skip_free")] = {
                    "n": len(ps_), "prefilter": sum(p["prefilter_pass"] for p in ps_), "pass": sum(p["pass"] for p in ps_), "recover": sum(p["recover"] for p in ps_)}
        return out
    pooled = tab(lambda p: True)
    per = {"%s|%s" % (v, rel): tab(lambda p, v=v, rel=rel: p["abi"] == v and p["rel"] == rel) for v in BASH for rel in ("keyskip1", "keyskip2")}
    gate = all(c["recover"] >= 3 for c in pooled.values())
    nov_ws_fail = [p for p in plants if p["register"] == "EN_NOVOWEL" and p["with_skip_head24"] and not p["pass"]]
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "path": "real chunk path: pf_v4 frozen (m=24,k=2,rel=both) on 2^16-seed chunk -> v3 L=120 both rels on all survivors -> v3 L=240 -> panel; natural-rate plants via real enc_exact/enc_pair; only filter = realised C[:40] doublet-free; NO skip-free selection",
           "bars_declared_N1e6": bars, "plants_per_abi_rel_register": NPL, "pooled_by_register_skip": pooled, "per_abi_rel": per,
           "novowel_with_skip_pass_failures": nov_ws_fail, "gate_ge3_recover_each_pooled_split": gate,
           "gate_novowel_withskip_all_pass": len(nov_ws_fail) == 0, "plants": plants}
    json.dump(out, open(CALF, "w"), indent=1)
    print("POOLED", json.dumps(pooled)); print("GATE", gate, "NOVOWEL with-skip failures", len(nov_ws_fail))
    return 0 if gate else 1


# ------------------------------------------------------------------ sweep
def sweep():
    c = json.load(open(CALF))
    if not c["gate_ge3_recover_each_pooled_split"]: print("REFUSE: control gate failed"); return 2
    t0 = time.time()
    hdr = AD.header("round37/I2/bash-orbit-pfv4-12reg", pan=PAN,
                    key_space="bash 4.2 $RANDOM%29 auto-seed orbit 74x2^20=77,594,624 seeds per ABI (LP64, ILP32), 296 chunks of 2^18 shuffled Random(3301); offset 0, sign -1, C[0]-aligned",
                    decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400 under panel-R36; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate",
                    v3_version="round33/I1 beam_v3.py panel_max (set_panel -> panel-R36); bars round36/B1 null12.json POT fit",
                    prefilter={"name": "round37/I2 pf_v4_12 (pf_v4 Viterbi, lse over 12 panel-R36 LMs)", "m": M_PF, "k": 2, "rel": "both", "thr_a1": pf_v4.FROZEN["thr"]["a1"], "thr_a2": pf_v4.FROZEN["thr"]["a2"],
                               "pen": 2, "per_relation_fpr": 5e-4, "fpr": "total ~1e-3 (heldout %.2e)" % pf_v4.FROZEN["fpr_heldout_measured"], "frozen_op": "analysis/round37/I2-pfv4-12reg/frozen_op12.json",
                               "rows_only_for": "prefilter survivors"},
                    register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=P12_SHA, n_registers=12,
                    panel_build="panel-R36 (round36/P1 build1; sha256 " + P12_SHA[:8] + ")",
                    corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)",
                    n_round_adjudicated_reference=N_DECL, seed_sample="chunk order Random(3301)")
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    st = {"cells": {k: {"seeds_screened": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}, "hist": {}} for k in BASH},
          "phase": {}, "cap_total_s": CAP_TOTAL, "cap_lp64_s": CAP_LP64}
    keep = []

    def note(cell, rows):
        S = st["cells"][cell]
        for r in rows:
            S["decodes"][r["rel"]] += 1; b = S["best"].get(r["rel"])
            if b is None or r["pmax"] > b["pmax"]: S["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"]}
            h = S["hist"].setdefault(r["rel"], {}); k = "%d" % math.floor(r["pmax"]); h[k] = h.get(k, 0) + 1
            if r["pmax"] >= KEEP: keep.append(r)

    def save(done=False):
        st["elapsed_s"] = round(time.time() - t0, 1); st["complete_all_phases"] = done
        json.dump(st, open(SUMF, "w"), indent=1); json.dump(keep, open(KEEPF, "w"))

    chunks = [(p, s) for p in PREF for s in range(0, 1 << 20, SUB)]
    random.Random(3301).shuffle(chunks)
    for v in BASH:
        ts = time.time(); cap = CAP_LP64 if v == "bash4.2" else CAP_TOTAL - (ts - t0)
        ph = {"chunks_total": len(chunks), "chunks_done": 0, "cap_s": round(cap, 1)}; st["phase"][v] = ph
        for (p, s) in chunks:
            if time.time() - ts > cap: break
            if ph["chunks_done"] % 8 == 0: wait_mem()
            seeds = np.arange((p << 20) | s, ((p << 20) | s) + SUB, dtype=np.uint64)
            n_s, rows = chunk_bash(seeds, v, C_SCREEN, out)
            S = st["cells"][v]; S["seeds_screened"] += SUB; S["survivors"] += n_s; note(v, rows)
            ph["chunks_done"] += 1; ph["elapsed_s"] = round(time.time() - ts, 1)
            if ph["chunks_done"] % 4 == 0:
                out.flush(); save()
                print("%s chunk %d/%d t=%.0fs surv=%d best=%s" % (v, ph["chunks_done"], len(chunks), time.time() - ts, S["survivors"], S["best"]), flush=True)
        ph["fraction_of_orbit"] = ph["chunks_done"] / len(chunks); ph["complete"] = ph["chunks_done"] == len(chunks)
        out.flush(); save()
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
            b120, b240 = bar_v3(N, 120, rel), bar_v3(N, 240, rel); d120, d240 = bar_v3(N_DECL, 120, rel), bar_v3(N_DECL, 240, rel)
            best = S["best"][rel]
            cand = sorted([r for r in keep if r["cell"] == cell and r["rel"] == rel], key=lambda r: -r["pmax"])
            ent = {"N_actual": N, "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3), "bar240_declN": round(d240, 3),
                   "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"],
                   "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"]) for r in cand[:5]]}
            for r in [r for r in cand if r["pmax"] >= b120]:
                d, a = v3dec(U[:L_HIT], C1.ks(r["seed"], cell, 1024), rel); p240 = float(a["pmax"])
                e = {"cell": cell, "rel": rel, "seed": r["seed"], "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3),
                     "preg240": PAN.registers[a["preg"]], "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3),
                     "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (cell, rel)] = ent
    summ["validate_store"] = "ok"
    try: AD.validate_store(ROWS)
    except Exception as ex: summ["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    summ["check_r3_store"] = VL.check_r3_store(ROWS)
    json.dump(summ, open(F("sweep_summary_final.json"), "w"), indent=1)
    for k, v in summ["cells"].items(): print(k, v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"], v["clears_declN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]), summ["validate_store"], summ["check_r3_store"])


if __name__ == "__main__":
    sys.exit({"control": control, "sweep": sweep, "finalize": finalize}[sys.argv[1]]())
