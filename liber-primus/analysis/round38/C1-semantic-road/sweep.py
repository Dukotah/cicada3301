#!/usr/bin/env python3
"""R38/C1: python -I sweep.py control | sweep | finalize.  Writes only inside this dir. Reuses R37 C1 infrastructure."""
import os, sys, json, time, math, random, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R37 = os.path.join(HERE, "..", "..", "round37", "C1-composed-clue-readings")
sys.path.insert(0, R37)
import sweep as S            # R37 infrastructure (its main is guarded)
sys.path.insert(0, HERE)
import enciphers as EN
from c1lib import AD, PAN, PANEL_SHA, bar_v3, B2, wait_mem
F = lambda n: os.path.join(HERE, n)
CAL, ROWS, SUMF, GATEF, KEEPF = F("control.json"), F("sweep_rows.jsonl"), F("sweep_summary.json"), F("gate_hits.jsonl"), F("keep_rows.json")
VARS = ["%s-%s" % v for v in EN.VARIANTS]
REL = "keyskip1"


def lens_p(p): return S.LENS[p]


def dec_shift(p, L, var, s, sigma, mode, C=None):
    C = S.Cpage(p, L) if C is None else C; d = EN.d_seq(var, lens_p(p), s); out = []; D = 0; used = 0
    for k, l in enumerate(lens_p(p)):
        if used >= len(C): break
        D += d[k]; sh = d[k] if mode == "A1" else D
        for t in range(l):
            if used >= len(C): break
            out.append((C[used] - sigma * sh) % 29); used += 1
    return out, AD.adjudicate(out)


def dec_a3(p, L, var, s, sigma, C=None):
    C = S.Cpage(p, L) if C is None else C; d = EN.d_seq(var, lens_p(p), s); K = []; r = 0; J = 0
    for k, l in enumerate(lens_p(p)):
        J += sigma * d[k]
        K.extend(EN.K0[(r + J + t) % len(EN.K0)] for t in range(l)); r += l
    K = K[:S.NKEY]
    dd, a = S.v3dec(C, K, REL, -1, 0); return dd["plain_idx"], a


def run(j, L):
    p = j["page"]; Lp = min(L, S.PAGE_LEN[p]) if L > 120 else L
    if j["mode"] == "A3": return dec_a3(p, Lp, j["var"], j["s"], j["sigma"])
    return dec_shift(p, Lp, j["var"], j["s"], j["sigma"], j["mode"])


def kid(j): return "r38c1:%s:%s:p%d:s%d:sg%d" % (j["var"], j["mode"], j["page"], j["s"], j["sigma"])


def bars(N, L): return {"bar_v3": bar_v3(N, L, REL), "bar12": S.bar12(N, 120 if L < 180 else 240, REL)}


def control():
    rng = random.Random(3338); out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": PANEL_SHA, "plants": []}
    wait_mem(); lens0 = lens_p(0); t0 = time.time(); a3t = []
    for var in VARS:
        for mode in ("A1", "A2", "A3"):
            for rep in range(2):
                sigma = (-1, 1)[rep]; s = rng.randrange(29) if mode != "A3" else rng.randrange(726)
                P = S.held(rng=rng, L=240); seed = rng.randrange(1, 10 ** 9)
                Cc = EN.enc(P, lens0, var, s, sigma, mode, REL if mode == "A3" else None, seed)[:240]
                j = {"var": var, "mode": mode, "s": s, "sigma": sigma, "page": 0}
                U0 = list(S.U); s0 = S.page_start(0); S.U[s0:s0 + len(Cc)] = Cc   # plant into page-0 slots; Cpage reads S.U
                try:
                    t1 = time.time(); p1, a1 = run(j, 120); p2, a2 = run(j, 240)
                    if mode == "A3": a3t.append((time.time() - t1) / 2)
                finally:
                    S.U[:] = U0
                rec = S.rec_of(p2, P); e = {"var": var, "mode": mode, "s": s, "sigma": sigma}; e.update(S.judge(float(a1["pmax"]), float(a2["pmax"]), rec, REL))
                out["plants"].append(e)
        print("ctrl", var, "%.0fs" % (time.time() - t0), flush=True); json.dump(out, open(CAL, "w"), indent=1)
    v = {}
    for e in out["plants"]:
        k = "%s|%s" % (e["var"], e["mode"]); v[k] = v.get(k, True) and e["recover"]
    out["valid"] = v; out["a3_sec_per_decode"] = sum(a3t) / max(1, len(a3t))
    out["summary"] = {"valid_cells": "%d/%d" % (sum(v.values()), len(v)), "plants_recover": "%d/%d" % (sum(e["recover"] for e in out["plants"]), len(out["plants"]))}
    json.dump(out, open(CAL, "w"), indent=1); print(json.dumps(out["summary"]), out["a3_sec_per_decode"]); print({k: x for k, x in v.items() if not x})


def jobs_list(valid):
    c = json.load(open(CAL))
    cells = [k for k, ok in valid.items() if ok]; nA3 = len([k for k in cells if k.endswith("A3")])
    full = nA3 * 726 * 2 * 3; step = max(1, math.ceil(full * c["a3_sec_per_decode"] / 2 / (55 * 60)))
    jobs = []
    for k in cells:
        var, mode = k.split("|")
        for p in (0, 1, 2):
            for sg in (-1, 1):
                for s in (range(29) if mode != "A3" else range(0, 726, step)):
                    jobs.append({"var": var, "mode": mode, "s": s, "sigma": sg, "page": p})
    return jobs, step, full


def sweep():
    c = json.load(open(CAL)); jobs, step, full = jobs_list(c["valid"])
    N = {"shift": sum(1 for j in jobs if j["mode"] != "A3"), "A3": sum(1 for j in jobs if j["mode"] == "A3")}
    print("jobs", len(jobs), N, "A3 step", step, "of full", full, flush=True)
    hdr = AD.header("round38/C1-semantic-road", pan=PAN, key_space="WordNet3.1 first-synset-offset / Norvig freq rank, x R29/R28/D29, x A1/A2/A3 x pages 0-2 x s x sigma", decoder="beam_v3 panel_max tau=0 lam_u=4 keyskip1 (A3); A1/A2 beam-free direct, judged vs keyskip1 bar",
                    register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=PANEL_SHA, v3_version="round33/I1 beam_v3.py via set_panel", bars="round34/I1 bars_v3 (+ bar12 from round36/B1 null12.json)",
                    kid_format="r38c1:var:mode:page:s:sigma", n_planned=dict(N, a3_step=step))
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n"); gate = open(GATEF, "w"); keep = []; best = {}; hist = {}; nd = 0; t0 = time.time()
    Nof = lambda j: N["A3"] if j["mode"] == "A3" else N["shift"]
    for j in jobs:
        pl, a = run(j, 120); out.write(json.dumps(AD.to_row(a, kid(j))) + "\n"); nd += 1; pm = float(a["pmax"])
        key = "%s|%s" % (j["var"], j["mode"]); b = best.get(key)
        if b is None or pm > b["pmax"]: best[key] = {"pmax": round(pm, 3), "preg": PAN.registers[a["preg"]], "kid": kid(j)}
        grp = "A3" if j["mode"] == "A3" else "shift"; h = hist.setdefault(grp, {}); h[str(math.floor(pm))] = h.get(str(math.floor(pm)), 0) + 1
        if pm >= S.KEEP: keep.append({"kid": kid(j), "pmax": round(pm, 3), "preg": PAN.registers[a["preg"]], "mode": j["mode"]})
        if pm >= bar_v3(Nof(j), 120, REL):
            pl2, a2 = run(j, S.Lgate(j["page"])); L2 = len(pl2)
            g = {"kid": kid(j), "pmax120": round(pm, 3), "pmax_gate": round(float(a2["pmax"]), 3), "L_gate": L2, "preg_gate": PAN.registers[a2["preg"]],
                 "bar_gate_actualN": round(bar_v3(Nof(j), L2, REL), 3)}; g["FLAGGED_FOR_ORACLE"] = bool(g["pmax_gate"] >= g["bar_gate_actualN"]); gate.write(json.dumps(g) + "\n"); gate.flush()
        if nd % 250 == 0:
            out.flush(); json.dump(keep, open(KEEPF, "w")); print(nd, len(jobs), "%.0fs" % (time.time() - t0), max(v["pmax"] for v in best.values()), flush=True)
        if nd % 1500 == 0: wait_mem()
    out.close(); gate.close(); json.dump(keep, open(KEEPF, "w"))
    json.dump({"decodes": nd, "N": N, "a3_step": step, "a3_full": full, "elapsed_s": round(time.time() - t0, 1), "best": best, "hist": hist}, open(SUMF, "w"), indent=1); print("DONE", nd)


def finalize():
    s = json.load(open(SUMF)); keep = json.load(open(KEEPF)); gates = [json.loads(l) for l in open(GATEF) if l.strip()]
    res = {"flagged": [g for g in gates if g["FLAGGED_FOR_ORACLE"]], "gate_runs": len(gates), "groups": {}}
    for grp in ("shift", "A3"):
        N = s["N"][grp]
        if not N: continue
        cand = {k: v for k, v in s["best"].items() if (k.endswith("A3") == (grp == "A3"))}
        if not cand: continue
        bk = max(cand.items(), key=lambda t: t[1]["pmax"]); ba, b6 = bars(N, 120), bars(1e6, 120)
        res["groups"][grp] = {"N": N, "best_cell": bk[0], "best": bk[1], "bar_v3_actualN": round(ba["bar_v3"], 3), "bar_v3_N1e6": round(b6["bar_v3"], 3), "bar12_actualN": round(ba["bar12"], 3), "bar12_N1e6": round(b6["bar12"], 3),
                              "clears_actualN": bk[1]["pmax"] >= ba["bar_v3"], "clears_N1e6": bk[1]["pmax"] >= b6["bar_v3"], "per_cell_best": cand}
    res["near_miss"] = [k for k in keep if bar_v3(s["N"]["A3" if k["mode"] == "A3" else "shift"], 120, REL) <= k["pmax"] < bar_v3(1e6, 120, REL)]
    try: AD.validate_store(ROWS); res["validate_store"] = "ok"
    except Exception as ex: res["validate_store"] = "FAIL %s" % ex
    json.dump(res, open(F("sweep_summary_final.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "groups"})[:1200])
    for g, e in res["groups"].items(): print(g, {k: v for k, v in e.items() if k != "per_cell_best"})


if __name__ == "__main__":
    {"control": control, "sweep": sweep, "finalize": finalize}[sys.argv[1]]()
