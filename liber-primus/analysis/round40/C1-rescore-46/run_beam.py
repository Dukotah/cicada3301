"""python run_beam.py r33 | r47   (direct beam_v3 families, run_beam_family from the C3 machinery; control first)"""
import os, sys, json, time, random
from c1common import *
from lib import _load
os.makedirs(F("controls"), exist_ok=True)
MD = deg_thr()

def control_beam(fam, Ks, regs=("EN_MODERN", "LATIN", "GREEK")):
    p = F("controls", fam + ".json")
    if os.path.exists(p): return json.load(open(p))
    rng = random.Random(4002); b120 = {r: bar12(1e6, 120, r) for r in RELS}; b240 = {r: bar12(1e6, 240, r) for r in RELS}; plants = []
    for reg in regs:
        for rel in RELS:
            for j in range(2):
                E = [int(v) for v in Ks[rng.randrange(len(Ks))][:1024]]; C, P = plant_beam(reg, rel, E, rng, 240)
                d1, a1 = v3dec(C[:120], E, rel); d2, a2 = v3dec(C, E, rel); rec = float(B2.recovery(d2["plain_idx"], P))
                e = {"register": reg, "rel": rel, "pmax120": round(float(a1["pmax"]), 3), "pmax240": round(float(a2["pmax"]), 3), "recovery240": round(rec, 4)}
                e["recover"] = bool(e["pmax120"] >= b120[rel] and e["pmax240"] >= b240[rel] and rec >= 0.9); plants.append(e)
    tab = {rel: {"n": 6, "recover": sum(q["recover"] for q in plants if q["rel"] == rel)} for rel in RELS}
    c = {"family": fam, "table": tab, "gate_ge4_of_6_per_relation": all(v["recover"] >= 4 for v in tab.values()), "plants": plants}
    json.dump(c, open(p, "w"), indent=1); log("control", fam, tab, c["gate_ge4_of_6_per_relation"]); return c

def l240_followup(fam, meta, cfgs_by_name):
    """clears actual-N at L=120 -> L=240 re-decode of the best row per relation (flag record)."""
    out = {}
    for rel in RELS:
        if meta["clears_actualN"][rel]:
            kid = meta["best"][rel]["kid"]; out[rel] = {"kid": kid, "pending": "L=240 rescreen + oracle bundle"}
    return out

def stage_r33():
    sw = _load("r26c_sweep", os.path.join(R(26), "C", "sweep.py"))
    seeds = json.load(open(os.path.join(R(26), "C", "seeds.json")))["seeds"]; cfgs = []; fam = "R33_R26C_semantic_seed_zoo"
    for s in seeds:
        for gname, (gfn, accepts_str) in sw.ZOO.items():
            if s["is_str"] and not accepts_str: continue
            try: K = gfn(s["value"])
            except Exception: continue
            if len(K) < sw.NEED: continue
            cfgs.append(("%s|%s|%s" % (s["kind"], str(s["label"])[:40], gname), U, np.array(K, dtype=np.int64), -1, [0]))
    log(fam, "keystreams", len(cfgs), "(original: 4274 rows / 2 presets = 2137)")
    c = control_beam(fam, [c_[2] for c_ in cfgs[::max(1, len(cfgs) // 40)]])
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED"); return
    m = run_beam_family(fam, cfgs, [0], 120, "R26-C zoo regenerated: %d (seed,generator) keystreams (323 corpus values + phrases x 7 generators, str seeds only on py27 generators), offset 0, window 0 (as original), L=120" % len(cfgs), "beam_v3 panel_max keyskip1+keyskip2 panel-R36", null_draws=100)
    return m

def stage_r47():
    f01 = os.path.join(R(16), "F-01"); sys.path.insert(0, f01)
    f = _load("f01_sweep", os.path.join(f01, "sweep.py")); fam = "R47_F01_LP2_as_pad"
    LP2 = list(f.load_lp2()); variants = {"lp2_fwd": LP2, "lp2_rev": LP2[::-1], "lp2_atbash": [28 - x for x in LP2], "lp2_neg": [(-x) % 29 for x in LP2]}
    targets = {"T1_cicada_2012_2013": list(f.load_cicada_2012_2013())[:500], "T2_lp1_solved": list(f.load_lp1_runes())[:500], "T3_pgp_messages": list(f.load_pgp_messages())[:500], "T6_lp2_head_200": LP2[:200]}
    t4 = f.load_anend_hash(); log(fam, "target lengths", {k: len(v) for k, v in targets.items()}, "T4", len(t4))
    cfgs = []
    for tn, T in targets.items():
        starts = [s for s in range(0, len(T) - 119, 120)] if len(T) >= 240 else [0, 80]
        starts = [s for s in starts if s + 120 <= len(T)]
        for vn, K in variants.items():
            for sg in (-1, +1): cfgs.append(("%s|%s|s%+d" % (tn, vn, sg), T, np.array(K, dtype=np.int64), sg, starts))
    c = control_beam(fam, [np.array(variants["lp2_fwd"]), np.array(variants["lp2_rev"]), np.array(variants["lp2_atbash"]), np.array(variants["lp2_neg"])])
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED"); return
    run_beam_family(fam, cfgs, [0], 120, "R47 F-01 LP2 (fwd/rev/atbash/neg) x sign +-1 as running key over T1 2012-13 texts, T2 solved LP1, T3 PGP bodies (500 runes each, L=120 windows at 0,120,240,360), T6 LP2 head 200 (windows 0,80); T4 (63 values) shorter than L=120: not scored; T5 payload absent as in the original", "beam_v3 panel_max keyskip1+keyskip2 panel-R36", null_draws=100)

if __name__ == "__main__":
    globals()["stage_" + sys.argv[1]]()
