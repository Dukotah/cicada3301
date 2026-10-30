#!/usr/bin/env python3
"""Round 37 / C1: composed clue readings. Usage: python sweep.py control | sweep | finalize
Writes only inside this directory.  One process.  Rows streamed in append mode (12-wide SWEEPROW)."""
import os, sys, json, time, math, random, itertools, hashlib, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round37/C1-composed-clue-readings"), HERE
sys.path.insert(0, HERE)
from c1lib import *            # noqa
from c1lib import _load
import enciphers_u2_u3 as E
import mapcommon as M
b04ks = _load("b04ks", AN("round13", "B04", "ks.py"))
kdf = _load("kdf15", AN("round15", "KDF", "kdf.py"))
TEST = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
F = lambda n: os.path.join(HERE, n)
CALF, ROWS, SUMF, GATEF, KEEPF = F("control.json"), F("sweep_rows.jsonl"), F("sweep_summary.json"), F("gate_hits.jsonl"), F("keep_rows.json")
NKEY = 1100; KEEP = 6.0
NULL12 = json.load(open(AN("round36", "B1-orbit-12reg", "null12.json")))["cells"]
PAGE_LEN = {p: len(M.parse()["pages"][p]) for p in (0, 1, 2)}
PARSE = M.parse()


def bar12(N, L, rel):
    c = NULL12["L%d|%s" % (L, rel)]
    return c["u"] + c["beta"] * math.log(c["p_u"]) + c["beta"] * math.log(float(N) / -math.log1p(-0.01))


def relbar(rel): return "keyskip1" if rel == "direct" else rel


def bars(N, L, rel):
    r = relbar(rel); Lb = L if L in (120, 240) else L
    return {"bar_v3": bar_v3(N, L, r), "bar12": bar12(N, 120 if L < 180 else 240, r)}


# ------------------------------------------------------------------ cipher-side word structure (decoder side, from the ciphertext)
def page_start(p): return sum(len(PARSE["pages"][q]) for q in range(p))


def lens_from_page(p, nrunes=NKEY):
    first = PARSE["w_page"].index(p); out = []; tot = 0
    for w in PARSE["words"][first:]:
        out.append(len(w)); tot += len(w)
        if tot >= nrunes: break
    return out


LENS = {p: lens_from_page(p) for p in (0, 1, 2)}
HEADS = {p: PARSE["pages"][p] for p in (0, 1, 2)}
for p in (0, 1, 2):
    assert HEADS[p] == U[page_start(p):page_start(p) + len(HEADS[p])]


def Lgate(p): return min(240, PAGE_LEN[p]) if p is not None else 240


def Cpage(p, L):
    """ciphertext head of page p of length L (pages are contiguous in U)."""
    s = page_start(p); return U[s:s + L]


# ------------------------------------------------------------------ decoder-side key builders (written separately from the encipherers)
def key_u2a(ch, nm, m):
    S = E.SEQS[ch][nm]; return [S[j % len(S)] % m for j in range(NKEY)]


def key_u2b(ch, nm, m, o, p):
    S = E.SEQS[ch][nm]; K0 = E.K0; nK = len(K0); out = []; J = 0; i = 0
    for k, l in enumerate(LENS[p]):
        J += S[k % len(S)] % m
        out.extend(K0[(o + i + t + J) % nK] for t in range(l)); i += l
    return out[:NKEY]


def u3_digits(p, rho, Mm, s):
    n = len(E.W); d = []; r = 0
    for k, l in enumerate(LENS[p]):
        pk = k if rho == 1 else (r if rho == 2 else l)
        d.append(E.VAL["prime"][(s + pk) % n] % Mm); r += l
    return d


def u3_direct(p, L, rho, Mm, s, sigma, mode):
    C = Cpage(p, L); d = u3_digits(p, rho, Mm, s); out = []; D = 0; k = 0; used = 0
    for k, l in enumerate(LENS[p]):
        if used >= len(C): break
        D += d[k]; sh = d[k] if mode == "A1" else D
        for t in range(l):
            if used >= len(C): break
            out.append((C[used] - sigma * sh) % 29); used += 1
    return out


def key_u3a3(p, rho, Mm, s, sigma):
    d = u3_digits(p, rho, Mm, s); K0 = E.K0; nK = len(K0); out = []; r = 0; J = 0
    for k, l in enumerate(LENS[p]):
        J += sigma * d[k]
        out.extend(K0[(r + J + t) % nK] for t in range(l)); r += l
    return out[:NKEY]


# ------------------------------------------------------------------ U1 keys
def norm_upper(s): return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z ]", "", s)).strip().upper()


def key_direct(s):
    r = sk.eng_to_idx(s); assert r
    return [r[j % len(r)] for j in range(NKEY)]


def key_sha(b): return [x % 29 for x in b04ks.GENERATORS["sha256_ctr"](b, NKEY)]


def key_pbkdf2(b): return kdf.keystream(b, "3301", "pbkdf2_sha256_10000", NKEY, "mod29")


def u1_items():
    cj = json.load(open(F("candidates.json")))
    items = []
    for stratum, lst in (("N", cj["candidates"]), ("R", cj["already_covered"])):
        for c in lst:
            cid = c.get("id") or ("R-" + c["norm"][:24])
            forms = [("UP", c["upper"])]
            if stratum == "N" and c["as_written"].encode() != c["upper"].encode(): forms.append(("AW", c["as_written"]))
            items.append({"cid": cid, "stratum": stratum, "upper": c["upper"], "forms": forms})
    return items


_KC = {}


def u1_key(route, cid, form, text):
    k = (route, cid, form)
    if k not in _KC:
        _KC[k] = key_direct(text) if route == "direct" else (key_sha(text.encode()) if route == "sha256ctr" else key_pbkdf2(text.encode()))
    return _KC[k]


def u1_jobs(valid_routes=("direct", "sha256ctr", "pbkdf2")):
    jobs = []
    for it in u1_items():
        for route in valid_routes:
            if it["stratum"] == "R" and route == "sha256ctr": continue
            for fm, text in (it["forms"] if route != "direct" else it["forms"][:1]):
                for rel, sign, off in itertools.product(RELS, (-1, 1), range(8)):
                    jobs.append({"sub": "U1", "cell": "%s|%s|%s" % (route, it["cid"], fm), "route": route, "cid": it["cid"], "form": fm, "text": text,
                                 "rel": rel, "sign": sign, "o": off, "page": None})
    return jobs


def u2_jobs(valid=None):
    jobs = []
    for (ch, nm, m) in E.VARIANTS:
        for mode in ("a", "b"):
            if valid is not None and ("%s|%s|%d|%s" % (ch, nm, m, mode)) not in valid: continue
            for p in (0, 1, 2):
                for rel, sign, off in itertools.product(RELS, (-1, 1), range(8)):
                    jobs.append({"sub": "U2", "cell": "%s|%s|m%d|%s" % (ch, nm, m, mode), "ch": ch, "nm": nm, "m": m, "mode": mode,
                                 "rel": rel, "sign": sign, "o": off, "page": p})
    return jobs


def u3_jobs(valid=None):
    jobs = []
    for rho, Mm, mode in itertools.product((1, 2, 3), (29, 28), ("A1", "A2", "A3")):
        if valid is not None:
            ok = valid.get("%d|%d|%s" % (rho, Mm, mode if mode != "A3" else "A3"))
            if not ok: continue
        for p in (0, 1, 2):
            for s, sigma in itertools.product(range(29), (-1, 1)):
                for rel in (("direct",) if mode != "A3" else RELS):
                    jobs.append({"sub": "U3", "cell": "rho%d|M%d|%s" % (rho, Mm, mode), "rho": rho, "M": Mm, "mode": mode, "s": s, "sigma": sigma,
                                 "rel": rel, "sign": sigma, "o": 0, "page": p})
    return jobs


# ------------------------------------------------------------------ run one job at head length L
def run_job(j, L=120):
    sub = j["sub"]; rel = j["rel"]
    if sub == "U1":
        K = u1_key(j["route"], j["cid"], j["form"], j["text"]); C = U[:L]
        d, a = v3dec(C, K, rel, j["sign"], j["o"]); return d["plain_idx"], a
    p = j["page"]; Lp = min(L, PAGE_LEN[p]) if L > 120 else L
    C = Cpage(p, Lp)
    if sub == "U2":
        K = key_u2a(j["ch"], j["nm"], j["m"]) if j["mode"] == "a" else key_u2b(j["ch"], j["nm"], j["m"], j["o"], p)
        o = j["o"] if j["mode"] == "a" else 0
        d, a = v3dec(C, K, rel, j["sign"], o); return d["plain_idx"], a
    if j["mode"] in ("A1", "A2"):
        x = u3_direct(p, Lp, j["rho"], j["M"], j["s"], j["sigma"], j["mode"]); return x, AD.adjudicate(x)
    K = key_u3a3(p, j["rho"], j["M"], j["s"], j["sigma"])
    d, a = v3dec(C, K, rel, -1, 0); return d["plain_idx"], a


def kid(j):
    if j["sub"] == "U1": return "u1:%s:%s:%s:%s:%d:%d" % (j["route"], j["cid"], j["form"], j["rel"], j["sign"], j["o"])
    if j["sub"] == "U2": return "u2:%s:%s:m%d:%s:p%d:%s:%d:%d" % (j["ch"], j["nm"], j["m"], j["mode"], j["page"], j["rel"], j["sign"], j["o"])
    return "u3:rho%d:M%d:%s:p%d:s%d:sg%d:%s" % (j["rho"], j["M"], j["mode"], j["page"], j["s"], j["sigma"], j["rel"])


# ------------------------------------------------------------------ controls
def held(reg="EN_MODERN", L=240, rng=None):
    arr = TEST[reg].astype(np.int64); st = rng.randrange(0, len(arr) - L - 10); return arr[st:st + L].tolist()


def rec_of(plain, P): return float(B2.recovery(plain, P))


def judge(pm120, pm240, rec, rel):
    b1, b2 = bar_v3(1e6, 120, relbar(rel)), bar_v3(1e6, 240, relbar(rel))
    return {"pmax120": round(pm120, 3), "pmax240": round(pm240, 3), "recovery240": round(rec, 4), "bar120_N1e6": round(b1, 3), "bar240_N1e6": round(b2, 3),
            "recover": bool(pm120 >= b1 and pm240 >= b2 and rec >= 0.90)}


def control():
    rng = random.Random(3301); t0 = time.time(); out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": PANEL_SHA, "U1": {}, "U2": [], "U3": []}
    wait_mem()
    # ---- U3 first (cheapest), then U2, then U1 (rank test is the expensive one)
    lens0 = E.word_lens_from(0)
    for rho, Mm in itertools.product((1, 2, 3), (29, 28)):
        for mode, rels in (("A1", ("direct",)), ("A2", ("direct",)), ("A3", RELS)):
            for rel in rels:
                s = rng.randrange(29); sigma = rng.choice((-1, 1)); P = held(rng=rng, L=240)
                Cc = E.enc_u3(P, lens0, rho, Mm, s, sigma, mode, rel if mode == "A3" else None, rng.randrange(1, 10 ** 9))[:240]
                j = {"sub": "U3", "rho": rho, "M": Mm, "mode": mode, "s": s, "sigma": sigma, "rel": rel, "sign": sigma, "o": 0, "page": 0}
                # decoder works on the REAL page-0 ciphertext slots, so run it on the planted ciphertext by temporarily swapping U
                p1, a1 = plant_run(j, Cc, 120); p2, a2 = plant_run(j, Cc, 240)
                rec = rec_of(p2, P)
                e = {"rho": rho, "M": Mm, "mode": mode, "rel": rel, "s": s, "sigma": sigma}; e.update(judge(float(a1["pmax"]), float(a2["pmax"]), rec, rel))
                out["U3"].append(e)
        print("U3 ctrl", rho, Mm, "%.0fs" % (time.time() - t0), flush=True)
    for (ch, nm, m) in E.VARIANTS:
        for mode in ("a", "b"):
            rel = RELS[rng.randrange(2)]; o = rng.randrange(8); P = held(rng=rng, L=240); seed = rng.randrange(1, 10 ** 9)
            if mode == "a": Cc = E.enc_u2a(P, ch, nm, m, o, rel, seed)[:240]
            else: Cc = E.enc_u2b(P, ch, nm, m, o, lens0, rel, seed)[:240]
            j = {"sub": "U2", "ch": ch, "nm": nm, "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
            p1, a1 = plant_run(j, Cc, 120); p2, a2 = plant_run(j, Cc, 240); rec = rec_of(p2, P)
            e = {"ch": ch, "nm": nm, "m": m, "mode": mode, "rel": rel, "o": o}; e.update(judge(float(a1["pmax"]), float(a2["pmax"]), rec, rel)); out["U2"].append(e)
        print("U2 ctrl", ch, nm, m, "%.0fs" % (time.time() - t0), flush=True)
    json.dump(out, open(CALF, "w"), indent=1)
    # ---- U1 rank test
    items = u1_items(); routes = ("direct", "sha256ctr", "pbkdf2")
    plant_ids = {"direct": "U1-001", "sha256ctr": "U1-002", "pbkdf2": "U1-003"}
    for route in routes:
        pj = [j for j in u1_jobs((route,)) if j["cid"] == plant_ids[route] and j["form"] == "UP"][0]
        text = pj["text"]; K = u1_key(route, pj["cid"], "UP", text)
        jobs = u1_jobs((route,))
        for rel in RELS:
            wait_mem(); o = rng.randrange(8); P = held(rng=rng, L=240); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
            best = {}
            for j in jobs:
                Kj = u1_key(route, j["cid"], j["form"], j["text"])
                d, a = v3dec(Cc[:120], Kj, j["rel"], j["sign"], j["o"])
                kk = "%s|%s" % (j["cid"], j["form"])
                if float(a["pmax"]) > best.get(kk, (-9, None))[0]: best[kk] = (float(a["pmax"]), a["preg"], "%s/%d/%d" % (j["rel"], j["sign"], j["o"]))
            rank = sorted(best.items(), key=lambda t: -t[1][0])
            pk = "%s|UP" % plant_ids[route]
            pos = [i for i, (k, v) in enumerate(rank) if k == pk][0] + 1
            d2, a2 = v3dec(Cc, K, rel, -1, o); rec = rec_of(d2["plain_idx"], P)
            e = {"route": route, "planted": plant_ids[route], "planted_text": text, "plant_rel": rel, "plant_offset": o, "n_keys_ranked": len(rank), "rank_of_planted": pos,
                 "planted_pmax120_in_grid": round(best[pk][0], 3), "planted_best_setting": best[pk][2], "runner_up": [rank[1][0], round(rank[1][1][0], 3)] if pos == 1 else [rank[0][0], round(rank[0][1][0], 3)]}
            e.update(judge(best[pk][0], float(a2["pmax"]), rec, rel)); e["rank1"] = pos == 1; e["recover"] = bool(e["recover"] and pos == 1)
            out["U1"].setdefault(route, []).append(e)
            print("U1 ctrl", route, rel, "rank", pos, "of", len(rank), "%.0fs" % (time.time() - t0), flush=True)
            json.dump(out, open(CALF, "w"), indent=1)
    # ---- validity maps used by the sweep
    v1 = {r: all(e["recover"] for e in out["U1"][r]) for r in routes}
    v2 = {"%s|%s|%d|%s" % (e["ch"], e["nm"], e["m"], e["mode"]): e["recover"] for e in out["U2"]}
    v3 = {}
    for e in out["U3"]:
        k = "%d|%d|%s" % (e["rho"], e["M"], e["mode"]); v3[k] = v3.get(k, True) and e["recover"]
    out["valid"] = {"U1_routes": v1, "U2_variants": v2, "U3_cells": v3}
    out["summary"] = {"U1_routes_valid": sum(v1.values()), "U2_valid": "%d/%d" % (sum(v2.values()), len(v2)), "U3_valid": "%d/%d" % (sum(v3.values()), len(v3)),
                      "U3_plants_recover": "%d/%d" % (sum(e["recover"] for e in out["U3"]), len(out["U3"])), "U2_plants_recover": "%d/%d" % (sum(e["recover"] for e in out["U2"]), len(out["U2"]))}
    json.dump(out, open(CALF, "w"), indent=1); print(json.dumps(out["summary"]), json.dumps(v1))
    return 0


_SWAP = {}


def plant_run(j, Cc, L):
    """Run the sweep decoder on a PLANTED ciphertext occupying page-0 slots (word structure of page 0)."""
    global U
    import c1lib
    saved = list(c1lib.U)
    try:
        s0 = page_start(0)
        U_ = list(saved); U_[s0:s0 + len(Cc)] = Cc
        globals()["U"] = U_
        return run_job(j, L)
    finally:
        globals()["U"] = saved


# ------------------------------------------------------------------ sweep
def sweep():
    c = json.load(open(CALF)); val = c["valid"]
    valid_routes = tuple(r for r, ok in val["U1_routes"].items() if ok)
    j1 = u1_jobs(valid_routes); j2 = u2_jobs({k for k, ok in val["U2_variants"].items() if ok}); j3 = u3_jobs(val["U3_cells"])
    jobs = j1 + j2 + j3
    N = {}
    for j in jobs: N[(j["sub"], j["rel"])] = N.get((j["sub"], j["rel"]), 0) + 1
    print("jobs", len(jobs), {"%s|%s" % k: v for k, v in N.items()}, "valid routes", valid_routes, flush=True)
    hdr = AD.header("round37/C1-composed-clue-readings", pan=PAN,
                    key_space="U1 clue strings (42 new + 41 covered; routes direct/sha256ctr/pbkdf2 x rel x sign x offset 0..7); U2 LP1-number key schedules (16 variants x a/b x 3 page heads); U3 composed map-road-direction rule (rho x M x s x sigma x A1/A2/A3 x 3 page heads)",
                    decoder="beam_v3 panel_max tau=0 lam_u=4 beam_w=400 keyskip1/keyskip2; U3 A1/A2 are beam-free direct decodes (judged vs keyskip1 bar)",
                    register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=PANEL_SHA, v3_version="round33/I1 beam_v3.py via set_panel", bars="round34/I1 bars_v3 (+ bar12 from round36/B1 null12.json)",
                    kid_format="u1:route:cid:form:rel:sign:off | u2:ch:seq:m:mode:page:rel:sign:off | u3:rho:M:mode:page:s:sigma:rel", n_planned=N_as_json(N))
    out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n")
    wait_mem(); t0 = time.time(); keep = []; best = {}; hist = {}
    gate = open(GATEF, "w"); nd = 0
    trig = {k: bar_v3(n, 120, relbar(k[1])) for k, n in N.items()}
    for j in jobs:
        plain, a = run_job(j, 120)
        out.write(json.dumps(AD.to_row(a, kid(j))) + "\n"); nd += 1
        pm = float(a["pmax"]); key = (j["sub"], j["rel"], j["cell"])
        b = best.get(key)
        if b is None or pm > b["pmax"]: best[key] = {"pmax": round(pm, 3), "preg": PAN.registers[a["preg"]], "kid": kid(j)}
        hk = "%s|%s" % (j["sub"], j["rel"]); h = hist.setdefault(hk, {}); h[str(math.floor(pm))] = h.get(str(math.floor(pm)), 0) + 1
        if pm >= KEEP: keep.append({"kid": kid(j), "sub": j["sub"], "rel": j["rel"], "cell": j["cell"], "pmax": round(pm, 3), "preg": PAN.registers[a["preg"]]})
        if pm >= trig[(j["sub"], j["rel"])]:
            p = j["page"]; pl, a2 = run_job(j, Lgate(p) if p is not None else 240)
            L2 = len(pl); g = {"kid": kid(j), "pmax120": round(pm, 3), "pmax_gate": round(float(a2["pmax"]), 3), "L_gate": L2, "preg_gate": PAN.registers[a2["preg"]],
                               "bar120_actualN": round(trig[(j["sub"], j["rel"])], 3), "bar_gate_actualN": round(bar_v3(N[(j["sub"], j["rel"])], L2, relbar(j["rel"])), 3)}
            g["FLAGGED_FOR_ORACLE"] = bool(g["pmax_gate"] >= g["bar_gate_actualN"]); gate.write(json.dumps(g) + "\n"); gate.flush()
        if nd % 250 == 0:
            out.flush(); json.dump(keep, open(KEEPF, "w"))
            top = max(best.items(), key=lambda t: t[1]["pmax"])
            print("%d/%d %.0fs top %s %s" % (nd, len(jobs), time.time() - t0, top[0], top[1]["pmax"]), flush=True)
        if nd % 2000 == 0: wait_mem()
    out.close(); gate.close(); json.dump(keep, open(KEEPF, "w"))
    summ = {"decodes": nd, "N": {"%s|%s" % k: v for k, v in N.items()}, "elapsed_s": round(time.time() - t0, 1),
            "best": {"%s|%s|%s" % k: v for k, v in best.items()}, "hist": hist, "valid_routes": valid_routes}
    json.dump(summ, open(SUMF, "w"), indent=1); print("SWEEP DONE", nd, "%.0fs" % (time.time() - t0))
    return 0


def N_as_json(N): return {"%s|%s" % k: v for k, v in N.items()}


# ------------------------------------------------------------------ finalize
def finalize():
    s = json.load(open(SUMF)); keep = json.load(open(KEEPF)); gates = [json.loads(l) for l in open(GATEF) if l.strip()]
    res = {"subfamilies": {}, "flagged": [g for g in gates if g["FLAGGED_FOR_ORACLE"]], "gate_runs": len(gates)}
    for sub in ("U1", "U2", "U3"):
        ent = {}
        for rel in ("keyskip1", "keyskip2", "direct"):
            kN = "%s|%s" % (sub, rel)
            if kN not in s["N"]: continue
            N = s["N"][kN]; cand = {k: v for k, v in s["best"].items() if k.startswith(kN + "|")}
            bst = max(cand.items(), key=lambda t: t[1]["pmax"]); b120 = bars(N, 120, rel); d120 = bars(1e6, 120, rel)
            ent[rel] = {"N": N, "best_pmax": bst[1]["pmax"], "best_cell": bst[0].split("|", 2)[2], "best_register": bst[1]["preg"], "best_kid": bst[1]["kid"],
                        "bar_v3_actualN": round(b120["bar_v3"], 3), "bar_v3_N1e6": round(d120["bar_v3"], 3), "bar12_actualN": round(b120["bar12"], 3), "bar12_N1e6": round(d120["bar12"], 3),
                        "clears_actualN": bst[1]["pmax"] >= b120["bar_v3"], "clears_N1e6": bst[1]["pmax"] >= d120["bar_v3"],
                        "top5_kept": sorted([k for k in keep if k["sub"] == sub and k["rel"] == rel], key=lambda k: -k["pmax"])[:5]}
        res["subfamilies"][sub] = ent
    res["near_miss"] = [k for k in keep if k["pmax"] >= bar_v3(s["N"]["%s|%s" % (k["sub"], k["rel"])], 120, relbar(k["rel"])) and k["pmax"] < bar_v3(1e6, 120, relbar(k["rel"]))]
    try: AD.validate_store(ROWS); res["validate_store"] = "ok"
    except Exception as ex: res["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, AN("handoff")); import validate_ledger as VL
    res["check_r3_store"] = VL.check_r3_store(ROWS)
    json.dump(res, open(F("sweep_summary_final.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("flagged", "near_miss", "validate_store", "check_r3_store", "gate_runs")}, indent=0)[:1500])
    for sub, ent in res["subfamilies"].items():
        for rel, e in ent.items(): print(sub, rel, e["N"], e["best_pmax"], e["best_cell"], e["bar_v3_actualN"], e["bar_v3_N1e6"], e["clears_actualN"])


if __name__ == "__main__":
    sys.exit({"control": control, "sweep": sweep, "finalize": finalize}[sys.argv[1]]())
