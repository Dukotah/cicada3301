#!/usr/bin/env python3
"""Round 38 / C2 sub-lane G (C1-R37 gaps). python run_gaps.py control | sweep | final.  Writes only in this directory."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from lib import *      # noqa
GAPS = os.path.dirname(os.path.abspath(__file__))
GF = lambda n: os.path.join(GAPS, n)
CALF, ROWSF, SUMF, GATEF = GF("control.json"), GF("sweep_rows.jsonl"), GF("sweep_summary.json"), GF("gate_hits.jsonl")
PL = json.load(open(GF("printed_lines.json")))
E.SEQS["prime"]["pline"] = PL["prime_seq"]; E.SEQS["index"]["pline"] = PL["index_seq"]
CL = {c["id"]: c["text"] for c in json.load(open(os.path.join(LP, "analysis", "round36", "O4-clue-coverage", "clues.json"), encoding="utf-8"))}
NKEY = S.NKEY
LENSP = {p: lens_from_page(p) for p in range(6)}
HEADFULL = {p: U[page_start(p):page_start(p) + NKEY] for p in range(6)}
K0 = E.K0; nK = len(K0)

# ---------------------------------------------------------------- G1 strings
G1_KEYS = []     # (cid, form, text, routes)
c6, c7 = CL["C-2016-6"], CL["C-2016-7"]
G1_KEYS.append(("G1-C6", "UP", S.norm_upper(c6), ("direct", "sha256ctr", "pbkdf2")))
G1_KEYS.append(("G1-C6", "AW", c6, ("sha256ctr", "pbkdf2")))
G1_KEYS.append(("G1-C7", "UP", S.norm_upper(c7), ("direct", "sha256ctr", "pbkdf2")))
G1_KEYS.append(("G1-C7", "UPD", " ".join(c7.upper().replace(".", " ").split()), ("sha256ctr", "pbkdf2")))
G1_KEYS.append(("G1-C7", "AW", c7, ("sha256ctr", "pbkdf2")))


def g1_jobs(routes=("direct", "sha256ctr", "pbkdf2")):
    jobs = []
    for cid, form, text, rts in G1_KEYS:
        for route in rts:
            if route not in routes: continue
            for rel, sign, off in itertools.product(RELS, (-1, 1), range(8)):
                jobs.append({"sub": "G1", "cell": "%s|%s|%s" % (route, cid, form), "route": route, "cid": cid, "form": form, "text": text, "rel": rel, "sign": sign, "o": off})
    return jobs


def g1_decode(j, L=120):
    K = S.u1_key(j["route"], j["cid"], j["form"], j["text"]); d, a = v3dec(U[:L], K, j["rel"], j["sign"], j["o"]); return d["plain_idx"], a


def g1_kid(j): return "g1:%s:%s:%s:%s:%d:%d" % (j["route"], j["cid"], j["form"], j["rel"], j["sign"], j["o"])


# ---------------------------------------------------------------- G3 lagged pointer rule
def vword(rs, ch): return E.vsum(list(rs), ch)


def dval(prev, ch, M, dk):
    return prev % M if dk == "self" else E.VAL["prime"][prev % len(E.W)] % M


def g3_decode_direct(C, lens, cell, sigma):
    src, ch, M, dk, mode = cell; out = []; D = 0; prev = 0; u = 0
    for k, l in enumerate(lens):
        if u >= len(C): break
        d = dval(prev, ch, M, dk); D += d; sh = d if mode == "A1" else D
        seg = [(C[u + t] - sigma * sh) % 29 for t in range(l) if u + t < len(C)]
        out += seg
        prev = vword(C[u:u + l], ch) if src == "cw" else vword(seg, ch)
        u += l
    return out


def g3_enc_direct(P, lens, cell, sigma):
    src, ch, M, dk, mode = cell; C = []; D = 0; prev = 0; u = 0
    for k, l in enumerate(lens):
        if u >= len(P): break
        d = dval(prev, ch, M, dk); D += d; sh = d if mode == "A1" else D
        seg = [(P[u + t] + sigma * sh) % 29 for t in range(l) if u + t < len(P)]
        C += seg
        prev = vword(seg, ch) if src == "cw" else vword(P[u:u + l], ch)
        u += l
    return C


def g3_key_cw(Cfull, lens, cell, sigma, need=NKEY):
    """A3, cipher-word pointer: K'[r+t] = K0[(r + J + t) mod nK], J += sigma*d_k, d_k from the previous CIPHER word value."""
    src, ch, M, dk, mode = cell; K = []; r = 0; J = 0; prev = 0
    for k, l in enumerate(lens):
        d = dval(prev, ch, M, dk); J += sigma * d
        K += [K0[(r + J + t) % nK] for t in range(l)]
        prev = vword(Cfull[r:r + l], ch); r += l
        if len(K) >= need: break
    return K


def g3_enc_a3(P, lens, cell, sigma, rel, seed):
    """Causal, skip-FREE planted encipherer for A3/cw: C_i = P_i + K'_i, K' built word by word from the already-produced cipher words.
    (With doublet skips the cw pointer is circular - K' indexed by consumed key position depends on cipher words that depend on it - so the
    control for this cell is the skip-free case; recorded as a conditional.)"""
    src, ch, M, dk, mode = cell; C = []; r = 0; J = 0; prev = 0
    for k, l in enumerate(lens):
        if r >= len(P): break
        d = dval(prev, ch, M, dk); J += sigma * d
        seg = [(P[r + t] + K0[(r + J + t) % nK]) % 29 for t in range(l) if r + t < len(P)]
        C += seg; prev = vword(seg, ch); r += l
    return C, 0


def g3_cells():
    cells = []
    for src in ("cw", "dw"):
        for ch, M, dk in itertools.product(("prime", "index"), (29, 28), ("self", "cb")):
            for mode in (("A1", "A2", "A3") if src == "cw" else ("A1", "A2")): cells.append((src, ch, M, dk, mode))
    return cells


def cname(c): return "%s|%s|M%d|%s|%s" % c


def g3_run(cell, p, sigma, rel, L=120, C=None, Cfull=None, lens=None):
    """real or planted decode of head C -> (plain, adjudication)"""
    src, ch, M, dk, mode = cell
    if mode in ("A1", "A2"):
        x = g3_decode_direct(C, lens, cell, sigma); return x, AD.adjudicate(x)
    K = g3_key_cw(Cfull, lens, cell, sigma); d, a = v3dec(C, K, rel, -1, 0); return d["plain_idx"], a


def g3_jobs(valid=None):
    jobs = []
    for cell in g3_cells():
        if valid is not None and not valid.get(cname(cell)): continue
        for p in range(6):
            for sigma in (-1, 1):
                for rel in (RELS if cell[4] == "A3" else ("direct",)):
                    jobs.append({"sub": "G3", "cell": cname(cell), "c": cell, "page": p, "sigma": sigma, "rel": rel})
    return jobs


def g3_kid(j): return "g3:%s:p%d:sg%d:%s" % (j["cell"], j["page"], j["sigma"], j["rel"])


# ---------------------------------------------------------------- controls
def control():
    rng = random.Random(38021); t0 = time.time(); wait_mem()
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": PANEL_SHA, "G1": {}, "G2": [], "G3": []}
    # ---- G2 via C1's own run_job / plant_run with the new sequence name 'pline'
    lens0 = E.word_lens_from(0)
    for ch in ("prime", "index"):
        for m in (29, 28):
            for mode in ("a", "b"):
                for rel in RELS:
                    o = rng.randrange(8); P = held(rng=rng); seed = rng.randrange(1, 10 ** 9)
                    Cc = (E.enc_u2a(P, ch, "pline", m, o, rel, seed) if mode == "a" else E.enc_u2b(P, ch, "pline", m, o, lens0, rel, seed))[:240]
                    j = {"sub": "U2", "ch": ch, "nm": "pline", "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
                    p1, a1 = S.plant_run(j, Cc, 120); p2, a2 = S.plant_run(j, Cc, 240)
                    e = {"ch": ch, "m": m, "mode": mode, "rel": rel, "o": o}; e.update(judge(float(a1["pmax"]), float(a2["pmax"]), rec_of(p2, P), rel)); out["G2"].append(e)
        print("G2 ctrl", ch, "%.0fs" % (time.time() - t0), flush=True)
    json.dump(out, open(CALF, "w"), indent=1)
    # ---- G3
    for cell in g3_cells():
        for rep in range(2):
            sigma = rng.choice((-1, 1)); rel = RELS[rng.randrange(2)] if cell[4] == "A3" else "direct"; P = held(rng=rng); seed = rng.randrange(1, 10 ** 9)
            if cell[4] == "A3":
                Cc, it = None, 0
                for tr in range(10):
                    Cc, it = g3_enc_a3(P, LENSP[0], cell, sigma, rel, seed + tr)
                    if Cc is not None: break
                if Cc is None:
                    out["G3"].append({"cell": cname(cell), "rep": rep, "recover": False, "note": "fixed-point encipherer did not converge in 10 seeds"}); continue
            else:
                Cc, it = g3_enc_direct(P, LENSP[0], cell, sigma), 0
            Cc = Cc[:240]
            p1, a1 = g3_run(cell, 0, sigma, rel, 120, C=Cc[:120], Cfull=Cc, lens=LENSP[0]); p2, a2 = g3_run(cell, 0, sigma, rel, 240, C=Cc, Cfull=Cc, lens=LENSP[0])
            e = {"cell": cname(cell), "rep": rep, "rel": rel, "sigma": sigma, "fixed_point_iters": it}
            e.update(judge(float(a1["pmax"]), float(a2["pmax"]), rec_of(p2, P[:len(p2)]), rel)); out["G3"].append(e)
        print("G3 ctrl", cname(cell), "%.0fs" % (time.time() - t0), flush=True)
    json.dump(out, open(CALF, "w"), indent=1)
    # ---- G1 rank test
    decoys = [it for it in S.u1_items() if it["stratum"] == "N"][:30]
    plant_for = {"direct": ("G1-C6", "UP"), "sha256ctr": ("G1-C7", "UPD"), "pbkdf2": ("G1-C6", "AW")}
    for route in ("direct", "sha256ctr", "pbkdf2"):
        jobs = g1_jobs((route,))
        for rel in RELS:
            wait_mem(); cid, form = plant_for[route]; pj = [j for j in jobs if j["cid"] == cid and j["form"] == form][0]
            K = S.u1_key(route, cid, form, pj["text"]); o = rng.randrange(8); P = held(rng=rng); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
            best = {}
            allj = list(jobs) + [{"cell": "dec", "route": route, "cid": it["cid"], "form": "UP", "text": it["upper"], "rel": r2, "sign": s2, "o": o2}
                                  for it in decoys for r2, s2, o2 in itertools.product(RELS, (-1, 1), range(8))]
            for j in allj:
                Kj = S.u1_key(route, j["cid"], j["form"], j["text"]); d, a = v3dec(Cc[:120], Kj, j["rel"], j["sign"], j["o"]); kk = "%s|%s" % (j["cid"], j["form"])
                if float(a["pmax"]) > best.get(kk, (-9, 0))[0]: best[kk] = (float(a["pmax"]), "%s/%d/%d" % (j["rel"], j["sign"], j["o"]))
            rank = sorted(best.items(), key=lambda t: -t[1][0]); pk = "%s|%s" % (cid, form); pos = [i for i, (k, v) in enumerate(rank) if k == pk][0] + 1
            d2, a2 = v3dec(Cc, K, rel, -1, o); rec = rec_of(d2["plain_idx"], P)
            e = {"route": route, "planted": pk, "plant_rel": rel, "plant_offset": o, "n_keys_ranked": len(rank), "rank_of_planted": pos, "planted_pmax120_in_grid": round(best[pk][0], 3),
                 "runner_up": [rank[1][0] if pos == 1 else rank[0][0], round(rank[1][1][0] if pos == 1 else rank[0][1][0], 3)]}
            e.update(judge(best[pk][0], float(a2["pmax"]), rec, rel)); e["recover"] = bool(e["recover"] and pos == 1); out["G1"].setdefault(route, []).append(e)
            print("G1 ctrl", route, rel, "rank", pos, "of", len(rank), "%.0fs" % (time.time() - t0), flush=True); json.dump(out, open(CALF, "w"), indent=1)
    v1 = {r: all(e["recover"] for e in out["G1"][r]) for r in out["G1"]}
    v2 = {}
    for e in out["G2"]:
        k = "%s|%d|%s" % (e["ch"], e["m"], e["mode"]); v2[k] = v2.get(k, True) and e["recover"]
    v3 = {}
    for e in out["G3"]: v3[e["cell"]] = v3.get(e["cell"], True) and e["recover"]
    out["valid"] = {"G1_routes": v1, "G2_variants": v2, "G3_cells": v3}
    out["summary"] = {"G1_routes_valid": "%d/3" % sum(v1.values()), "G2_valid": "%d/%d" % (sum(v2.values()), len(v2)), "G3_valid": "%d/%d" % (sum(v3.values()), len(v3)),
                      "G2_plants": "%d/%d" % (sum(e["recover"] for e in out["G2"]), len(out["G2"])), "G3_plants": "%d/%d" % (sum(e["recover"] for e in out["G3"]), len(out["G3"])), "elapsed_s": round(time.time() - t0)}
    json.dump(out, open(CALF, "w"), indent=1); print(json.dumps(out["summary"]), json.dumps(v1)); return 0


# ---------------------------------------------------------------- sweep
def g2_jobs(valid):
    jobs = []
    for ch, m, mode in itertools.product(("prime", "index"), (29, 28), ("a", "b")):
        if not valid.get("%s|%d|%s" % (ch, m, mode)): continue
        for p in (0, 1, 2):
            for rel, sign, off in itertools.product(RELS, (-1, 1), range(8)):
                jobs.append({"sub": "U2", "cell": "%s|pline|m%d|%s" % (ch, m, mode), "ch": ch, "nm": "pline", "m": m, "mode": mode, "rel": rel, "sign": sign, "o": off, "page": p})
    return jobs


def sweep():
    c = json.load(open(CALF)); val = c["valid"]
    vr = tuple(r for r, ok in val["G1_routes"].items() if ok)
    j1 = g1_jobs(vr); j2 = g2_jobs(val["G2_variants"]); j3 = g3_jobs(val["G3_cells"])
    N = {}
    for fam, js in (("G1", j1), ("G2", j2), ("G3", j3)):
        for j in js: N[(fam, j["rel"])] = N.get((fam, j["rel"]), 0) + 1
    print("jobs", len(j1), len(j2), len(j3), {"%s|%s" % k: v for k, v in N.items()}, "valid routes", vr, flush=True)
    rows = Rows(ROWSF, header("round38/C2/gaps", "G1 clauses 6/7 (UP/UPD/AW) x routes direct/sha256ctr/pbkdf2; G2 printed-line sums (60 lines) as U2 schedule; G3 lag-1 gematria pointers in composed rule",
                              "beam_v3 panel_max tau=0 lam_u=4 beam_w=400 keyskip1/keyskip2; G2 additive/pointer via C1 sweep.run_job; G3 A1/A2 beam-free direct decodes (judged vs keyskip1 bar), A3 beam",
                              "g1:route:cid:form:rel:sign:off | u2:ch:pline:m:mode:page:rel:sign:off | g3:src|ch|M|dk|mode:page:sigma:rel", {"%s|%s" % k: v for k, v in N.items()}))
    gate = open(GATEF, "w"); keep = []; wait_mem(); t0 = time.time(); nd = 0
    trig = {k: bar_v3(n, 120, relbar(k[1])) for k, n in N.items()}
    for fam, js in (("G1", j1), ("G2", j2), ("G3", j3)):
        for j in js:
            if fam == "G1":
                plain, a = g1_decode(j); kid = g1_kid(j); gl = (lambda j=j: g1_decode(j, 240))
            elif fam == "G2":
                plain, a = S.run_job(j, 120); kid = S.kid(j); gl = (lambda j=j: S.run_job(j, min(240, S.PAGE_LEN[j["page"]])))
            else:
                p = j["page"]; cell = j["c"]; C = HEADFULL[p][:120]
                plain, a = g3_run(cell, p, j["sigma"], j["rel"], 120, C=C, Cfull=HEADFULL[p], lens=LENSP[p]); kid = g3_kid(j)
                gl = (lambda j=j, p=p, cell=cell: g3_run(cell, p, j["sigma"], j["rel"], 240, C=HEADFULL[p][:min(240, page_len(p))], Cfull=HEADFULL[p], lens=LENSP[p]))
            pm = rows.add(a, kid, fam, j["rel"], j["cell"]); nd += 1
            if pm >= 6.0: keep.append({"kid": kid, "pmax": round(pm, 3), "preg": REGS[a["preg"]]})
            if pm >= trig[(fam, j["rel"])]:
                pl, a2 = gl(); L2 = len(pl)
                g = {"kid": kid, "pmax120": round(pm, 3), "pmax_gate": round(float(a2["pmax"]), 3), "L_gate": L2, "bar_gate_actualN": round(bar_v3(N[(fam, j["rel"])], L2, relbar(j["rel"])), 3)}
                g["FLAGGED_FOR_ORACLE"] = bool(g["pmax_gate"] >= g["bar_gate_actualN"]); gate.write(json.dumps(g) + "\n"); gate.flush()
            if nd % 250 == 0:
                rows.f.flush(); top = max(rows.best.items(), key=lambda t: t[1]["pmax"]); print("%d %.0fs top %s %s" % (nd, time.time() - t0, top[0], top[1]["pmax"]), flush=True)
            if nd % 1000 == 0: wait_mem()
    rows.close(); gate.close()
    summ = {"decodes": nd, "N": {"%s|%s" % k: v for k, v in N.items()}, "elapsed_s": round(time.time() - t0, 1), "best": {"%s|%s|%s" % k: v for k, v in rows.best.items()}, "hist": rows.hist,
            "valid_routes": vr, "keep_ge_6": keep}
    json.dump(summ, open(SUMF, "w"), indent=1); print("SWEEP DONE", nd, "%.0fs" % (time.time() - t0)); return 0


def final():
    s = json.load(open(SUMF)); res = {"families": {}}
    gates = [json.loads(l) for l in open(GATEF) if l.strip()]
    for fam in ("G1", "G2", "G3"):
        for rel in ("keyskip1", "keyskip2", "direct"):
            kN = "%s|%s" % (fam, rel)
            if kN not in s["N"]: continue
            N = s["N"][kN]; cand = {k: v for k, v in s["best"].items() if k.startswith(kN + "|")}
            bst = max(cand.items(), key=lambda t: t[1]["pmax"])
            res["families"][kN] = {"N": N, "best_pmax": bst[1]["pmax"], "best_cell": bst[0].split("|", 2)[2], "best_register": bst[1]["preg"], "best_kid": bst[1]["kid"],
                                   "bar_v3_actualN": round(bv3(N, 120, rel), 3), "bar_v3_N1e6": round(bv3(1e6, 120, rel), 3), "bar12_actualN": round(b12(N, 120, rel), 3),
                                   "clears_actualN": bool(bst[1]["pmax"] >= bv3(N, 120, rel))}
    res["gate_runs"] = len(gates); res["flagged"] = [g for g in gates if g["FLAGGED_FOR_ORACLE"]]
    try:
        AD.validate_store(ROWSF); res["validate_store"] = "ok"
    except Exception as ex:
        res["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    res["check_r3_store"] = VL.check_r3_store(ROWSF)
    json.dump(res, open(GF("summary_final.json"), "w"), indent=1)
    for k, v in res["families"].items(): print(k, v["N"], v["best_pmax"], v["best_cell"], v["best_register"], "bar", v["bar_v3_actualN"], v["clears_actualN"])
    print(res["validate_store"], res["check_r3_store"], "gates", res["gate_runs"], "flagged", len(res["flagged"]))


if __name__ == "__main__":
    sys.exit({"control": control, "sweep": sweep, "final": final}[sys.argv[1]]())
