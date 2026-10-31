"""Head-screened beam family engine (pf_v4_12 -> beam_v3 keyskip1+2 on panel-R36), controls, summary."""
import os, sys, json, math, random, time
from c1common import *

L120 = 120

class KeySet:
    """heads: (28,B) int8 with plain = C - E (E effective key); full(b)->list E[:1100]; label(b)->str"""
    def __init__(self, heads, full, label):
        self.heads = heads; self.full = full; self.label = label; self.B = heads.shape[1]

def decode_row(part, fam, kid, Cw, E, rel, best, ndeg_cnt, mds_min, ioc_max):
    d = V.beam_decode_v3(list(Cw), list(E), ADV[rel], "panel_max", tau=0.0, lam_u=4.0, sign=-1)
    a = AD.adjudicate(d["plain_idx"], pan=PAN)
    part.add(AD.to_row(a, kid))
    deg = (int(a["mds"]) <= mds_min) or (float(a["ioc"]) >= ioc_max)
    pm = float(a["pmax"])
    if deg:
        ndeg_cnt[rel] += 1
    elif pm > best[rel][0]:
        best[rel] = (pm, kid, REGS[a["preg"]], float(a["pmax_ne"]), d["plain_idx"])
    return pm

def run_screened(fam, ks, Cs, key_space, decoder, mdsioc, null_draws=60, L=L120):
    """Cs: list of (cid, Cwindow(list, len>=L)). Returns meta dict."""
    mds_min, ioc_max = mdsioc
    part = Part(fam, key_space, decoder, 0)
    if part.skip: log(fam, "already done"); return json.load(open(part.done))
    wait_mem(); t0 = time.time()
    best = {r: (-1e9, None, None, None, None) for r in RELS}; ndeg = {r: 0 for r in RELS}; nrow = {r: 0 for r in RELS}
    nsurv = 0; screened = 0; hist_reg = {r: {} for r in RELS}
    for (cid, Cw) in Cs:
        mask = screen(Cw[:24], ks.heads); screened += ks.B
        idx = np.flatnonzero(mask); nsurv += len(idx)
        for b in idx:
            E = ks.full(int(b))
            for rel in RELS:
                decode_row(part, fam, "%s:%s:%s:%s" % (fam, ks.label(int(b)), cid, rel), Cw[:L], E, rel, best, ndeg, mds_min, ioc_max); nrow[rel] += 1
        log(fam, cid, "screened", screened, "survivors", nsurv, "%.0fs" % (time.time() - t0))
        if free_gb() < 0.25: wait_mem(0.4)
    # family-matched wrong-key null: shuffled LP2 windows against survivor-conditioned random entries
    rng = random.Random(3301); nul = {r: [] for r in RELS}
    for k in range(null_draws):
        b = rng.randrange(ks.B); E = ks.full(b); sh = U[:]; random.Random(3301 + k).shuffle(sh)
        for rel in RELS:
            d = V.beam_decode_v3(sh[:L], list(E), ADV[rel], "panel_max", tau=0.0, lam_u=4.0, sign=-1); a = AD.adjudicate(d["plain_idx"], pan=PAN)
            part.add(AD.to_row(a, "null:%s:%d:%s" % (fam, k, rel))); nul[rel].append(float(a["pmax"]))
    Nn = max(screened, 1); Ns = max(nsurv, 1)
    bars = {r: {"actualN_screened": round(bar12(Nn, L, r), 3), "N_survivors": round(bar12(Ns, L, r), 3), "declared_1e6": round(bar12(1e6, L, r), 3)} for r in RELS}
    meta = {"family": fam, "kind": "screened_beam", "L": L, "keys": ks.B, "n_C_windows": len(Cs), "heads_screened": screened, "survivors": nsurv, "rows": nrow,
            "n_degenerate_rows": ndeg, "best_nondegenerate": {r: {"pmax": best[r][0], "kid": best[r][1], "preg": best[r][2], "pmax_ne": best[r][3]} for r in RELS},
            "bars": bars, "family_null": {r: {"n": len(nul[r]), "mean": float(np.mean(nul[r])), "max": float(np.max(nul[r]))} for r in RELS},
            "clears_actualN": {r: bool(best[r][0] >= bars[r]["actualN_screened"]) for r in RELS},
            "clears_declared": {r: bool(best[r][0] >= bars[r]["declared_1e6"]) for r in RELS},
            "near_miss_survivorN": {r: bool(bars[r]["N_survivors"] <= best[r][0] < bars[r]["actualN_screened"]) for r in RELS}, "elapsed_s": round(time.time() - t0, 1)}
    part.close(meta); log(fam, "done", {r: (round(best[r][0], 3), bars[r]["actualN_screened"]) for r in RELS}, "surv", nsurv, "scr", screened)
    return meta

def control_screened(fam, ks, nplants_per=2):
    """plants enciphered with the family's own keys (random entries, random registers); gate >=4/6 per relation."""
    rng = random.Random(4001); b120 = {r: bar12(1e6, 120, r) for r in RELS}; b240 = {r: bar12(1e6, 240, r) for r in RELS}
    plants = []
    for reg in ("EN_MODERN", "LATIN", "GREEK"):
        for rel in RELS:
            for j in range(nplants_per):
                b = rng.randrange(ks.B); E = ks.full(b); C, P = plant_beam(reg, rel, E[:1024], rng, 240)
                scr = bool(screen_rel(C[:24], np.array(E[:28], dtype=np.int8).reshape(28, 1))[rel][0])
                scr_any = bool(screen(C[:24], np.array(E[:28], dtype=np.int8).reshape(28, 1))[0])
                d1, a1 = v3dec(C[:120], E, rel); d2, a2 = v3dec(C, E, rel); rec = float(B2.recovery(d2["plain_idx"], P))
                e = {"register": reg, "rel": rel, "entry": ks.label(b), "screen_pass_own_rel": scr, "screen_pass_any": scr_any, "pmax120": round(float(a1["pmax"]), 3),
                     "pmax240": round(float(a2["pmax"]), 3), "recovery240": round(rec, 4)}
                e["decode_recover"] = bool(e["pmax120"] >= b120[rel] and e["pmax240"] >= b240[rel] and rec >= 0.9)
                e["recover"] = bool(e["decode_recover"] and scr_any); plants.append(e)
    tab = {rel: {"n": sum(p["rel"] == rel for p in plants), "recover": sum(p["recover"] for p in plants if p["rel"] == rel),
                 "decode_only_recover": sum(p["decode_recover"] for p in plants if p["rel"] == rel)} for rel in RELS}
    ok = all(v["recover"] >= 4 for v in tab.values()); log("control", fam, tab, ok)
    return {"family": fam, "table": tab, "gate_ge4_of_6_per_relation": ok, "plants": plants}
