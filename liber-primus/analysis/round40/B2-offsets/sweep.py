#!/usr/bin/env python3
"""R40 B2: bash 4.2 LP64 auto-seed orbit at key offsets / sign under the R37-I2 instrument (imported unchanged).
Usage: python sweep.py wrapcheck | control | run | finalize.  Writes ONLY inside this file's directory."""
import os, sys, json, time, random, math, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round40/B2-offsets"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


R37 = os.path.join(LP, "analysis", "round37", "I2-pfv4-12reg")
S = _load("r37sweep", os.path.join(R37, "sweep.py"))
AD, C1, PAN, B2 = S.AD, S.C1, S.PAN, S.B2
sk = C1.sk
V = "bash4.2"
CELLS = [(0, +1), (1, -1), (2, -1), (3, -1), (28, -1)]
cname = lambda c: "o%d_s%s" % (c[0], "p" if c[1] > 0 else "m")
RELS = S.RELS; L_SCREEN = S.L_SCREEN; N_DECL = S.N_DECL; KEEP = 6.0
F = lambda n: os.path.join(HERE, n)
ROWS, SUMF, KEEPF, PROGF = F("sweep_rows.jsonl"), F("sweep_summary.json"), F("keep_rows.json"), F("sweep_progress.json")
NPL = 10; CTRL = ("EN_MODERN", "EN_NOVOWEL")
T_START = float(os.environ.get("B2_T0", 0)) or time.time()
END = T_START + float(os.environ.get("B2_CAP_S", 2.5 * 3600 - 300))

# ---- the offset/sign machinery: effective keystream K' = K_raw[k:] (s=-1) or (29-K_raw[k:])%29 (s=+1)
CUR = {"off": 0, "sign": -1}
_orig_heads = S.pf_v4.heads


def eff(Kraw, off, sign):
    K = list(Kraw[off:])
    return K if sign < 0 else [(29 - x) % 29 for x in K]


def heads_off(seeds, m, variant):
    off, sg = CUR["off"], CUR["sign"]
    H = _orig_heads(seeds, m + off, variant)[off:]
    if sg > 0: H = ((29 - H.astype(np.int16)) % 29).astype(np.int8)
    return np.ascontiguousarray(H)


S.pf_v4.heads = heads_off
KS_N = 1024


def ks_eff(seed, off, sign): return eff(C1.ks(seed, V, KS_N + off), off, sign)


def v3dec_cell(C, seed, rel, off, sign):
    K = ks_eff(seed, off, sign)
    d = S.V.beam_decode_v3(list(C), K, S.ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])


def header():
    cfg = "|".join(cname(c) for c in CELLS)
    return AD.header("round40/B2/bash4.2-offsets-sign", pan=PAN, with_degenerate=True,
        key_space="bash 4.2 LP64 $RANDOM%%29 auto-seed orbit 74x2^20=77,594,624 seeds, 296 chunks of 2^18 shuffled Random(3301); cells (offset,sign) %s; ciphertext C[0] paired with K_raw[offset]; row id carries o<k>_s<m|p>" % cfg,
        decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400 under panel-R36; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate; effective keystream = K_raw[k:] (sign -1) or 29-K_raw[k:] (sign +1)",
        v3_version="round33/I1 beam_v3.py panel_max (set_panel -> panel-R36); bars round36/B1 null12.json POT fit",
        prefilter={"name": "round37/I2 pf_v4_12 (frozen_op12.json, instrument unchanged; heads advanced by offset and negated for sign +1 before the Viterbi)", "m": S.M_PF, "k": 2, "rel": "both",
                   "thr_a1": S.pf_v4.FROZEN["thr"]["a1"], "thr_a2": S.pf_v4.FROZEN["thr"]["a2"], "frozen_op": "analysis/round37/I2-pfv4-12reg/frozen_op12.json", "rows_only_for": "prefilter survivors"},
        register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=S.P12_SHA, n_registers=12, panel_build="panel-R36 (round36/P1 build1; sha256 " + S.P12_SHA[:8] + ")",
        corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)", n_round_adjudicated_reference=N_DECL, seed_sample="chunk order Random(3301) per cell")


def decode_seed(seed, C, cell, out=None):
    off, sg = cell; res = []
    for rel in RELS:
        d, a = v3dec_cell(C[:L_SCREEN], seed, rel, off, sg)
        if out is not None: out.write(json.dumps(AD.to_row(a, "bash:%s.%s:%d:%s" % (V, cname(cell), seed, rel), with_degenerate=True)) + "\n")
        res.append({"seed": int(seed), "cell": cname(cell), "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]]})
    return res


def chunk(seeds, C, cell, out=None):
    CUR["off"], CUR["sign"] = cell
    m = S.pf_v4.prefilter_mask(seeds, V, np.array(C[:S.M_PF], dtype=np.int8), S.M_PF, "both")
    surv = seeds[m]; rows = []
    for s in surv: rows += decode_seed(int(s), C, cell, out)
    return len(surv), rows


# ------------------------------------------------------------------ wrapper sanity
def wrapcheck():
    rng = random.Random(7); seeds = np.array([(rng.choice(S.PREF) << 20) | rng.randrange(1 << 20) for _ in range(300)], dtype=np.uint64)
    r = {}
    CUR.update(off=0, sign=-1); a = heads_off(seeds, 28, V); b = _orig_heads(seeds, 28, V); r["wrapper_(0,-1)_equals_R37_heads"] = bool((a == b).all())
    for off, sg in CELLS:
        CUR.update(off=off, sign=sg); h = heads_off(seeds, 28, V); bad = 0
        for i, s in enumerate(seeds):
            raw = C1.GB.raws(int(s), 28 + off + 5, V, anti_repeat=False)
            ref = eff([x % 29 for x in raw], off, sg)[:28]
            bad += ref != h[:, i].tolist()
        r["heads_%s_vs_exact_noantirepeat" % cname((off, sg))] = {"seeds": len(seeds), "mismatches": int(bad)}
    json.dump(r, open(F("wrapcheck.json"), "w"), indent=1); print(json.dumps(r, indent=1))
    return 0 if all(v is True or (isinstance(v, dict) and v["mismatches"] == 0) for v in r.values()) else 1


# ------------------------------------------------------------------ control
def enc_pair_s(P, K, sign, supp=0.83, seed=777):
    rng = random.Random(seed); C, j, cp = [], 0, None
    for p in P:
        while True:
            c = (p - sign * K[j]) % 29
            if cp is not None and c == cp and rng.random() < supp: j += 2; continue
            break
        C.append(c); j += 1; cp = c
    return C


def plant(cell, rel, reg, rng):
    off, sg = cell
    arr = S.TEST[reg].astype(np.int64)
    for _ in range(500):
        ps = (rng.choice(S.PREF) << 20) | rng.randrange(1 << 20)
        Kt = C1.ks(ps, V, KS_N + off)[off:]                      # TRUE (un-negated) stream from index `off`
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + 240].tolist()
        sd = rng.randrange(1, 10 ** 9)
        C = (sk.encipher_keyskip(P, Kt, sign=sg, supp=0.83, seed=sd)[0] if rel == "keyskip1" else enc_pair_s(P, Kt, sg, seed=sd))[:240]
        if len(C) < 240: continue
        if any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(p_ - sg * k_) % 29 for p_, k_ in zip(P, Kt)]   # no-skip ciphertext: c = p - sign*K
        return ps, C, P, int(any(C[i] != naive[i] for i in range(24)))
    raise RuntimeError("no plant")


def control(cell, npl=NPL, misaligned=False):
    off, sg = cell
    rng = random.Random(3301 + 97 * off + (11 if sg > 0 else 0)); plants = []; t0 = time.time()
    bars = {r: {"L120": S.bar_v3(N_DECL, 120, r), "L240": S.bar_v3(N_DECL, 240, r)} for r in RELS}
    run_cell = (0, -1) if misaligned else cell
    for rel in ("keyskip1", "keyskip2"):
        for reg in CTRL:
            for j in range(npl):
                ps, Cp, P, wsk = plant(cell, rel, reg, rng)
                base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                n_s, rr = chunk(seeds, Cp, run_cell)
                mine = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                e = {"cell": cname(cell), "screened_as": cname(run_cell), "rel": rel, "register": reg, "seed": int(ps), "with_skip_head24": bool(wsk), "prefilter_pass": any(r["seed"] == ps for r in rr),
                     "survivors_in_chunk": n_s, "pmax120": None, "pmax240": None, "recovery240": None, "pass": False, "recover": False}
                if mine:
                    e["pmax120"] = round(mine[0]["pmax"], 3)
                    d, a = v3dec_cell(Cp, ps, rel, *run_cell)
                    e["pmax240"] = round(float(a["pmax"]), 3); e["recovery240"] = round(float(B2.recovery(d["plain_idx"], P)), 4)
                    e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"] and e["pmax240"] >= bars[rel]["L240"])
                    e["recover"] = bool(e["pass"] and e["recovery240"] >= 0.90)
                plants.append(e)
            print("%.0fs" % (time.time() - t0), cname(cell), "mis" if misaligned else "", rel, reg, flush=True)

    def tab(sel):
        o = {}
        for reg in CTRL:
            for skp in (False, True):
                q = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == skp]
                o["%s|%s" % (reg, "with_skip" if skp else "skip_free")] = {"n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "pass": sum(p["pass"] for p in q), "recover": sum(p["recover"] for p in q)}
        return o
    pooled = tab(lambda p: True); per_rel = {rel: tab(lambda p, rel=rel: p["rel"] == rel) for rel in RELS}
    gate = all(c["recover"] >= 3 for c in pooled.values())
    out = {"cell": cname(cell), "offset": off, "sign": sg, "misaligned_negative_control": misaligned, "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "path": "real chunk path: pf_v4_12 frozen (m=24,k=2,rel=both) on the 2^16-seed chunk containing the planted seed, heads advanced by the offset (and negated for sign +1) -> v3 L=120 both rels on all survivors -> v3 L=240 -> panel-R36; plants enciphered from the TRUE K_raw[offset:] with the TRUE sign via encipher_keyskip(sign)/enc_pair_s (natural-rate); only filter = realised C[:40] doublet-free",
           "bars_declared_N1e6": bars, "pooled_by_register_skip": pooled, "per_rel": per_rel, "gate_ge3_recover_each_pooled_split": gate,
           "recover_total": sum(p["recover"] for p in plants), "prefilter_total": sum(p["prefilter_pass"] for p in plants), "n_plants": len(plants), "elapsed_s": round(time.time() - t0, 1), "plants": plants}
    json.dump(out, open(F(("control_misaligned_%s.json" if misaligned else "control_%s.json") % cname(cell)), "w"), indent=1)
    print("CONTROL", cname(cell), "misaligned" if misaligned else "", "gate", gate, "recover", out["recover_total"], "/", len(plants), "prefilter", out["prefilter_total"], flush=True)
    return gate


def do_control():
    gates = {}
    for c in CELLS: gates[cname(c)] = control(c)
    control((1, -1), npl=5, misaligned=True)           # offset-1 plants screened as offset 0: alignment matters
    json.dump(gates, open(F("control_gates.json"), "w")); print(gates); return 0 if all(gates.values()) else 1


# ------------------------------------------------------------------ sweep (resumable by chunk)
def load_prog():
    return json.load(open(PROGF)) if os.path.exists(PROGF) else {"cells": {}}


def run():
    gates = json.load(open(F("control_gates.json")))
    S.wait_mem()
    prog = load_prog(); keep = json.load(open(KEEPF)) if os.path.exists(KEEPF) else []
    first = not os.path.exists(ROWS) or os.path.getsize(ROWS) == 0
    out = open(ROWS, "a")
    if first: out.write(json.dumps(header()) + "\n"); out.flush()
    chunks = [(p, s) for p in S.PREF for s in range(0, 1 << 20, S.SUB)]; random.Random(3301).shuffle(chunks)

    def save(): json.dump(prog, open(PROGF, "w"), indent=1); json.dump(keep, open(KEEPF, "w"))
    for cell in CELLS:
        n = cname(cell)
        if not gates.get(n): print("REFUSE", n); prog["cells"].setdefault(n, {})["refused"] = "control failed"; continue
        P = prog["cells"].setdefault(n, {"offset": cell[0], "sign": cell[1], "done_chunks": [], "seeds_screened": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}, "hist": {}, "elapsed_s": 0.0, "checkpoint10": None})
        ts = time.time(); el0 = P["elapsed_s"]; done = set(map(tuple, P["done_chunks"]))
        for (p, s) in chunks:
            if (p, s) in done: continue
            if time.time() > END: break
            if len(done) % 8 == 0: S.wait_mem()
            seeds = np.arange((p << 20) | s, ((p << 20) | s) + S.SUB, dtype=np.uint64)
            n_s, rows = chunk(seeds, S.C_SCREEN, cell, out)
            P["seeds_screened"] += S.SUB; P["survivors"] += n_s
            for r in rows:
                P["decodes"][r["rel"]] += 1; bb = P["best"].get(r["rel"])
                if bb is None or r["pmax"] > bb["pmax"]: P["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"]}
                h = P["hist"].setdefault(r["rel"], {}); k = "%d" % math.floor(r["pmax"]); h[k] = h.get(k, 0) + 1
                if r["pmax"] >= KEEP: keep.append(r)
            done.add((p, s)); P["done_chunks"].append([p, s]); P["elapsed_s"] = round(el0 + time.time() - ts, 1)
            if len(done) == 30:
                rate = P["survivors"] / 30.0; P["checkpoint10"] = {"survivors_per_chunk": round(rate, 1), "R37_ref": round(65815 / 296, 1), "ok": bool(0.5 * 222 <= rate <= 2 * 222)}
                if not P["checkpoint10"]["ok"]: out.flush(); save(); print("KILL checkpoint", n, P["checkpoint10"]); return 3
            if len(done) % 4 == 0:
                out.flush(); save(); print("%s chunk %d/296 t=%.0fs surv=%d best=%s" % (n, len(done), P["elapsed_s"], P["survivors"], P["best"]), flush=True)
        P["complete"] = len(done) == len(chunks); P["fraction_of_orbit"] = len(done) / len(chunks)
        out.flush(); save()
        if time.time() > END: print("CAP reached in", n); break
    out.close(); save(); print("RUN DONE"); finalize(); return 0


# ------------------------------------------------------------------ finalize
def finalize():
    prog = load_prog(); keep = json.load(open(KEEPF)) if os.path.exists(KEEPF) else []
    summ = {"cells": {}, "flagged": [], "near_miss": []}
    for n, P in prog["cells"].items():
        if "refused" in P or not P.get("done_chunks"): continue
        cell = (P["offset"], P["sign"])
        for rel in RELS:
            N = P["decodes"][rel]
            if N == 0: continue
            b120, b240 = S.bar_v3(N, 120, rel), S.bar_v3(N, 240, rel); d120, d240 = S.bar_v3(N_DECL, 120, rel), S.bar_v3(N_DECL, 240, rel)
            best = P["best"][rel]; cand = sorted([r for r in keep if r["cell"] == n and r["rel"] == rel], key=lambda r: -r["pmax"])
            ent = {"offset": cell[0], "sign": cell[1], "chunks_done": len(P["done_chunks"]), "fraction_of_orbit": len(P["done_chunks"]) / 296, "N_actual": N, "seeds_screened": P["seeds_screened"], "survivors": P["survivors"],
                   "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3), "bar240_declN": round(d240, 3),
                   "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"], "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"]) for r in cand[:5]], "elapsed_s": P["elapsed_s"], "checkpoint10": P.get("checkpoint10")}
            for r in [r for r in cand if r["pmax"] >= b120]:
                d, a = v3dec_cell(S.U[:S.L_HIT], r["seed"], rel, *cell); p240 = float(a["pmax"])
                e = {"cell": n, "rel": rel, "seed": r["seed"], "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3), "preg240": PAN.registers[a["preg"]],
                     "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3), "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (n, rel)] = ent
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    try: AD.validate_store(ROWS); summ["validate_store"] = "ok"
    except Exception as ex: summ["validate_store"] = "FAIL %s" % ex
    summ["check_r3_store"] = VL.check_r3_store(ROWS)
    json.dump(summ, open(SUMF, "w"), indent=1)
    for k, v in summ["cells"].items(): print(k, v["chunks_done"], v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]), summ["validate_store"], summ["check_r3_store"]); return 0


if __name__ == "__main__":
    sys.exit({"wrapcheck": wrapcheck, "control": do_control, "run": run, "finalize": finalize}[sys.argv[1]]())
