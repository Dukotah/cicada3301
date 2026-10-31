#!/usr/bin/env python3
"""Round 38 / C2 sub-lane B: top-50 N5 and top-50 N4-keystream rows of C3-R37 re-run at L=240. python run_b.py control | sweep | final."""
import os, sys, re, importlib.util
sys.dont_write_bytecode = True
HERE0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE0))
from lib import *      # noqa
BD = HERE0
BF = lambda n: os.path.join(BD, n)
sys.path.insert(0, os.path.join(LP, "src"))
NC = C1.nc; N29 = 29
C3 = os.path.join(LP, "analysis", "round37", "C3-rescore-reopened", "parts")
SEGS = NC.segments()[:-2]
ADV = {"keyskip1": 1, "keyskip2": 2}
NTOP = 50
CALF, ROWSF, SUMF = BF("control.json"), BF("rows_L240.jsonl"), BF("summary.json")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


n5 = _load("n5mod", os.path.join(LP, "analysis", "round11", "N5", "n5.py"))
_GEN = {}


def gen_stream(gname, seq):
    return n5.GENERATORS[gname](seq)


def top_rows(fam, n=NTOP):
    f = open(os.path.join(C3, fam + ".jsonl")); h = json.loads(f.readline()); ip = h["fields"].index("pmax"); best = {}
    for l in f:
        r = json.loads(l)
        if r[0].startswith("null:"): continue
        cfg_w, rel = r[0].rsplit(":", 1); cfg_w = cfg_w.split(":", 1)[1]
        e = best.setdefault(cfg_w, {"pmax": {}, "kid120": {}}); e["pmax"][rel] = float(r[ip])
    ranked = sorted(best.items(), key=lambda t: -max(t[1]["pmax"].values()))
    return [(k, v["pmax"]) for k, v in ranked[:n]], len(best)


PL = None


def planes_all():
    global PL
    if PL is None:
        vals = NC.v_prime(U); PL = {}
        for base in (3, 5, 7, 10):
            mx = max(vals); pl = 0; v = mx
            while v > 0: pl += 1; v //= base
            for place in range(max(pl, 1)): PL[(base, place)] = [int(x) for x in NC.digit_plane(vals, base=base, place=place)]
    return PL


def build(fam, cfg_w):
    """cfg_w like 'phi_phi_prime_RI_s-1_o20_seg36:w0' -> (C, K, sign, start)"""
    cfg, w = cfg_w.rsplit(":w", 1); w = int(w)
    if fam == "U6a_N4_ks":
        m = re.match(r"^b(\d+)_p(\d+)_ks([+-]\d)$", cfg); base, place, sg = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return list(U), planes_all()[(base, place)], sg, w
    m = re.match(r"^(.*)_s([+-]\d)_o(\d+)(?:_seg(\d+))?$", cfg); gname, sg, off, pg = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    if pg is None:
        if gname not in _GEN: _GEN[gname] = gen_stream(gname, U)
        return list(U), [(k + off) % N29 for k in _GEN[gname]], sg, w
    seg = SEGS[int(pg)]; return list(seg), [(k + off) % N29 for k in gen_stream(gname, seg)], sg, w


def window(C, K, s, L):
    Cw = C[s:s + L]; Kw = K[s:s + 1024] if len(K) >= s + 1024 else list(K[s:]) + [0] * (s + 1024 - len(K)); return Cw, Kw


def dec(Cw, Kw, rel, sg):
    d = V.beam_decode_v3(list(Cw), list(Kw), ADV[rel], "panel_max", tau=0.0, lam_u=4.0, sign=sg); return d, AD.adjudicate(d["plain_idx"], pan=PAN)


def control():
    rng = random.Random(38031); t0 = time.time(); wait_mem(); out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": PANEL_SHA, "plants": [], "an_end": {}}
    tops = {"U6a_N5": top_rows("U6a_N5")[0], "U6a_N4_ks": top_rows("U6a_N4_ks")[0]}
    b = {rel: {"L240": bar_v3(1e6, 240, rel)} for rel in RELS}
    for fam, rows in tops.items():
        for idx in (0, 7):
            C, K, sg, s = build(fam, rows[idx][0]); Kw = window(C, K, s, 240)[1]
            for reg in ("EN_MODERN", "LATIN", "GREEK"):
                for rel in RELS:
                    P = held(reg, 240, rng); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
                    # decoder uses sign sg: C = P + (-sg)... encipher consistent with beam sign: plaintext = (C - sg*K) so C = P + sg*K -> use key sg*K
                    Kenc = [(sg * k) % 29 for k in Kw]
                    # enc_exact/enc_pair implement C = P + K ; sign +1 decode subtracts?  determine by round trip below
                    for trial_sign in (1, -1):
                        Cc = enc(list(P), [(trial_sign * k) % 29 for k in Kw], seed=rng.randrange(1, 10 ** 9))[:240]
                        d, a = dec(Cc, Kw, rel, sg)
                        rec = rec_of(d["plain_idx"], P)
                        if rec >= 0.9 or trial_sign == -1: break
                    e = {"fam": fam, "cfg": rows[idx][0], "register": reg, "rel": rel, "key_sign_used": trial_sign, "pmax240": round(float(a["pmax"]), 3), "recovery240": round(rec, 4),
                         "bar240_N1e6": round(b[rel]["L240"], 3), "recover": bool(float(a["pmax"]) >= b[rel]["L240"] and rec >= 0.9)}
                    out["plants"].append(e)
        print("plants", fam, "%.0fs" % (time.time() - t0), flush=True)
    # AN END real artifact (85 runes, phi(prime) keystream, no offset)
    ae = NC.anend(); ks = [k % N29 for k in n5.ks_lambda_prime(ae)]; truth = [(c - k) % N29 for c, k in zip(ae, ks)]
    out["an_end"] = {"n": len(ae), "head": "".join(NC.gp.IDX_TO_TRANS[i] for i in truth[:20])}
    for rel in RELS:
        d, a = dec(ae, ks[:1024], rel, -1); out["an_end"][rel] = {"pmax": round(float(a["pmax"]), 3), "preg": REGS[a["preg"]], "recovery": round(rec_of(d["plain_idx"], truth), 4)}
    tab = {fam: {rel: [sum(e["recover"] for e in out["plants"] if e["fam"] == fam and e["rel"] == rel), sum(1 for e in out["plants"] if e["fam"] == fam and e["rel"] == rel)] for rel in RELS} for fam in tops}
    out["table"] = tab
    out["valid"] = {fam: all(v[0] >= max(1, v[1] - 1) for v in tab[fam].values()) for fam in tab}   # at most 1 miss per relation
    out["valid"]["an_end"] = all(out["an_end"][r]["recovery"] >= 0.9 for r in RELS)
    json.dump(out, open(CALF, "w"), indent=1); print(json.dumps(out["table"]), json.dumps(out["valid"]), json.dumps(out["an_end"])); return 0


def sweep():
    c = json.load(open(CALF)); valid = c["valid"]; wait_mem(); t0 = time.time()
    fams = [f for f in ("U6a_N5", "U6a_N4_ks") if valid.get(f)]
    N = {}; jobs = []
    meta = {}
    for fam in fams:
        rows, ncfg = top_rows(fam); meta[fam] = {"configs_in_part": ncfg, "top": rows}
        for cfg_w, pm in rows:
            for rel in RELS: jobs.append((fam, cfg_w, rel)); N[(fam, rel)] = N.get((fam, rel), 0) + 1
    rows_w = Rows(ROWSF, header("round38/C2/n5n4_L240", "top-%d N5 rows and top-%d N4-keystream rows of C3-R37 at L=240 (same config + window start), ks1+ks2" % (NTOP, NTOP),
                                "beam_v3 panel_max tau=0 lam_u=4 beam_w=400 keyskip1/keyskip2, L=240 (segment configs: min(240, segment length))",
                                "fam:cfg:wSTART:rel", {"%s|%s" % k: v for k, v in N.items()}))
    flagged = []; repro = []
    for (fam, cfg_w, rel) in jobs:
        C, K, sg, s = build(fam, cfg_w); L = min(240, len(C) - s); Cw, Kw = window(C, K, s, L)
        d120, a120 = dec(Cw[:120], Kw, rel, sg)           # reproduction of the C3 L=120 row
        d, a = dec(Cw, Kw, rel, sg); kid = "%s:%s:%s" % (fam, cfg_w, rel)
        pm = rows_w.add(a, kid, fam, rel, fam)
        stored = dict(meta[fam]["top"])[cfg_w].get(rel)
        repro.append({"kid": kid, "pmax120_stored": stored, "pmax120_rerun": round(float(a120["pmax"]), 3), "L": L})
        bar = bar_v3(N[(fam, rel)], L, rel)
        if pm >= bar:
            txt = "".join(NC.gp.IDX_TO_TRANS[i] for i in d["plain_idx"])
            flagged.append({"kid": kid, "pmax240": round(pm, 3), "bar240_actualN": round(bar, 3), "preg": REGS[a["preg"]], "decoded_head": txt[:200]})
    rows_w.close()
    mism = [r for r in repro if r["pmax120_stored"] is not None and abs(r["pmax120_stored"] - r["pmax120_rerun"]) > 0.01]
    summ = {"N": {"%s|%s" % k: v for k, v in N.items()}, "best": {"%s|%s|%s" % k: v for k, v in rows_w.best.items()}, "hist": rows_w.hist, "flagged": flagged,
            "repro_n": len(repro), "repro_mismatch_gt_0.01": len(mism), "repro_mismatch_examples": mism[:5], "repro": repro,
            "top_L120_ranges": {fam: [max(meta[fam]["top"][0][1].values()), max(meta[fam]["top"][-1][1].values())] for fam in fams},
            "elapsed_s": round(time.time() - t0, 1)}
    json.dump(summ, open(SUMF, "w"), indent=1); print("DONE", len(jobs), "flagged", len(flagged), "repro mismatches", len(mism), "%.0fs" % (time.time() - t0))
    if flagged:
        os.makedirs(BF("oracle"), exist_ok=True); json.dump(flagged, open(os.path.join(BD, "oracle", "flagged_N50.json"), "w"), indent=1)
    return 0


NSCREEN = {"U6a_N5": 2320, "U6a_N4_ks": 168}      # rows per relation in the C3-R37 L=120 sweep these 50 were selected from


def final():
    s = json.load(open(SUMF)); res = {}
    best_rows = {}
    for fam in ("U6a_N5", "U6a_N4_ks"):
        for rel in RELS:
            k = "%s|%s" % (fam, rel)
            if k not in s["N"]: continue
            N = s["N"][k]; Ns = NSCREEN[fam]; cand = {kk: v for kk, v in s["best"].items() if kk.startswith(k + "|")}; bst = max(cand.values(), key=lambda v: v["pmax"])
            res[k] = {"N_rerun": N, "N_screen": Ns, "best_pmax240": bst["pmax"], "best_register": bst["preg"], "best_kid": bst["kid"],
                      "bar_v3_240_N_rerun": round(bar_v3(N, 240, rel), 3), "bar_v3_240_N_screen": round(bar_v3(Ns, 240, rel), 3), "bar_v3_240_N1e6": round(bar_v3(1e6, 240, rel), 3),
                      "bar12_240_N_screen": round(S.bar12(Ns, 240, rel), 3), "clears_N_rerun": bool(bst["pmax"] >= bar_v3(N, 240, rel)), "clears_N_screen": bool(bst["pmax"] >= bar_v3(Ns, 240, rel)),
                      "clears_N1e6": bool(bst["pmax"] >= bar_v3(1e6, 240, rel))}
    # count of rerun rows over each bar
    f = open(ROWSF); h = json.loads(f.readline()); ip = h["fields"].index("pmax"); cnt = {}
    for l in f:
        r = json.loads(l); kid = r[0]; fam = kid.split(":")[0]; rel = kid.rsplit(":", 1)[1]
        c = cnt.setdefault("%s|%s" % (fam, rel), {"rows": 0, "ge_bar_N_rerun": 0, "ge_bar_N_screen": 0, "ge_bar_N1e6": 0}); pm = float(r[ip]); c["rows"] += 1
        c["ge_bar_N_rerun"] += pm >= bar_v3(50, 240, rel); c["ge_bar_N_screen"] += pm >= bar_v3(NSCREEN[fam], 240, rel); c["ge_bar_N1e6"] += pm >= bar_v3(1e6, 240, rel)
    res["counts_over_bars"] = cnt
    try:
        AD.validate_store(ROWSF); res["validate_store"] = "ok"
    except Exception as ex:
        res["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    res["check_r3_store"] = VL.check_r3_store(ROWSF); res["flagged_N50"] = len(s["flagged"]); res["repro_mismatch"] = s["repro_mismatch_gt_0.01"]
    json.dump(res, open(BF("summary_final.json"), "w"), indent=1)
    for k, v in res.items():
        if isinstance(v, dict): print(k, v)
    print(res["validate_store"], res["check_r3_store"], "flagged at N=50:", res["flagged_N50"], "repro mismatches", res["repro_mismatch"])


if __name__ == "__main__":
    sys.exit({"control": control, "sweep": sweep, "final": final}[sys.argv[1]]())
