#!/usr/bin/env python3
"""R36 B2: PHP mt_rand tier (mt/php twist x scale/mod) under pf_v4 + beam_v3 panel_max, AWAKE, rows persisted (append on resume).
Usage: python sweep.py control | sweep | finalize.  Writes ONLY inside this file's directory."""
import os, sys, re, json, time, random, math, hashlib, importlib.util, datetime
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round36/B2-php-awake"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32, R33, R34, R35, R36 = [os.path.join(LP, "analysis", "round%d" % r) for r in (32, 33, 34, 35, 36)]
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
PM = _load("php_mt", os.path.join(R32, "B2-php-mtrand", "php_mt.py"))
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V                                  # noqa: E402
sys.path.insert(0, os.path.join(R35, "I1-skip-tolerant-screen"))
import pf_v4                                         # noqa: E402
sys.path.insert(0, os.path.join(R34, "I1-v3-null"))
from bars_v3 import bar_v3                           # noqa: E402
assert HERE == os.path.dirname(os.path.abspath(__file__))
AD = C1.AD; B2 = V.B2; PAN = V.panel(); LMT = PAN.LMT.astype(np.float32); U = C1.U
TEST = np.load(os.path.join(R32, "I2-multiregister-readjudication", "models", "testhalves.npz"))
L_SCREEN, L_HIT = 120, 240
C_SCREEN = U[:L_SCREEN]
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip2", "keyskip1")
FZ = pf_v4.FROZEN; M_PF = FZ["m"]; KSK = FZ["k"]; assert M_PF == 24 and KSK == 2
N_DECL = 10 ** 6; KEEP = 6.0
CELLS = [("mt", "scale"), ("mt", "mod"), ("php", "scale"), ("php", "mod")]
CN = ["%s_%s" % c for c in CELLS]
BLK = 1 << 17
B_TARGET_BLOCKS = 330; B_CAP_S = 3300; DENSE_UNF_CAP_S = 600; STALL_S = 120
F = lambda n: os.path.join(HERE, n)
CALF, ROWS, SUMF, KEEPF = F("control.json"), F("sweep_rows.jsonl"), F("sweep_summary.json"), F("keep_rows.json")
NPL = 10
I2P = json.load(open(os.path.join(R36, "I2-pfv4-keystreams", "power_by_generator.json")))["power"]
SUBS = ("a_core", "a_dense_unf", "a_dense_pf", "b")


def inhibit_sleep():
    try:
        import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001); return True
    except Exception: return False


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])


def cellkey(cn, s31cache, seed):
    tw, rd = cn.split("_"); s = s31cache.get(tw)
    if s is None: s = s31cache[tw] = PM.stream31(int(seed), tw, 1024)
    return [PM.red(x, rd) for x in s]


def decode_cell(cn, seed, K, C, out, sub):
    res = []
    for rel in RELS:
        d, a = v3dec(C[:L_SCREEN], K, rel)
        if out is not None: out.write(json.dumps(AD.to_row(a, "php:%s:%d:%s" % (cn, seed, rel))) + "\n")
        res.append({"seed": int(seed), "cell": cn, "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]], "sub": sub})
    return res


def php_mask(K, Chead):
    mask = np.zeros(K.shape[1], bool)
    for a in (1, 2):
        s = pf_v4.lse_v4(Chead, K[:M_PF + a * KSK], LMT, KSK, a, FZ["pen_a%d" % a], ms=(M_PF,))[M_PF]
        mask |= s > FZ["thr"]["a%d" % a]
    return mask


def block_screen(seeds, C, out, sub, cells=CN):
    """pf_v4 on all listed cells for a block of seeds; decode survivors (both rels). returns {cell: (n_surv, rows)}"""
    H = PM.heads_all(seeds, M_PF + 2 * KSK); Ch = np.array(C[:M_PF], dtype=np.int8); res = {}
    for cn in cells:
        tw, rd = cn.split("_"); K = PM.reduce_heads(H[tw], rd); m = php_mask(K, Ch); surv = seeds[m]; rows = []
        for s in surv:
            s = int(s); rows += decode_cell(cn, s, cellkey(cn, {}, s), C, out, sub)
        res[cn] = (len(surv), rows)
    return res


# ------------------------------------------------------------------ control
def plant(rel, reg, K_of, rng):
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(500):
        ps = rng.randrange(1 << 32); K = K_of(ps)
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + L_HIT].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:L_HIT]
        if len(C) < L_HIT: continue
        if any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(P[i] + K[i]) % 29 for i in range(L_HIT)]
        return ps, C, P, int(any(C[i] != naive[i] for i in range(24))), K
    raise RuntimeError("no plant")


def control():
    inhibit_sleep(); rng = random.Random(3301); plants = []; t0 = time.time()
    bars = {r: {"L120": bar_v3(N_DECL, 120, r), "L240": bar_v3(N_DECL, 240, r)} for r in ("keyskip1", "keyskip2")}
    for cn in CN:
        for rel in ("keyskip1", "keyskip2"):
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                for j in range(NPL):
                    ps, Cp, P, wsk, K = plant(rel, reg, lambda s, cn=cn: cellkey(cn, {}, s), rng)
                    base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                    n_s, rr = block_screen(seeds, Cp, None, "ctl", cells=[cn])[cn]
                    pf = any(r["seed"] == ps for r in rr)
                    d1, a1 = v3dec(Cp[:L_SCREEN], K, rel); d2, a2 = v3dec(Cp, K, rel)
                    p120, p240 = float(a1["pmax"]), float(a2["pmax"]); rec = float(B2.recovery(d2["plain_idx"], P))
                    pas = bool(p120 >= bars[rel]["L120"] and p240 >= bars[rel]["L240"])
                    plants.append({"cell": cn, "rel": rel, "register": reg, "seed": int(ps), "with_skip_head24": bool(wsk),
                                   "prefilter_pass": bool(pf), "survivors_in_chunk": n_s, "pmax120": round(p120, 3), "pmax240": round(p240, 3),
                                   "recovery240": round(rec, 4), "pass_unfiltered": pas, "recover_unfiltered": bool(pas and rec >= 0.90),
                                   "pass": bool(pf and pas), "recover": bool(pf and pas and rec >= 0.90)})
                print("%.0fs" % (time.time() - t0), cn, rel, reg, flush=True)

    def tab(sel):
        out = {}
        for reg in ("EN_MODERN", "EN_NOVOWEL"):
            for sk in (False, True):
                q = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == sk]
                out["%s|%s" % (reg, "with_skip" if sk else "skip_free")] = {
                    "n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "pass": sum(p["pass"] for p in q), "recover": sum(p["recover"] for p in q),
                    "pass_unfiltered": sum(p["pass_unfiltered"] for p in q), "recover_unfiltered": sum(p["recover_unfiltered"] for p in q)}
        return out
    pooled = tab(lambda p: True)
    per = {"%s|%s" % (cn, rel): tab(lambda p, cn=cn, rel=rel: p["cell"] == cn and p["rel"] == rel) for cn in CN for rel in ("keyskip1", "keyskip2")}
    per_rel = {rel: tab(lambda p, rel=rel: p["rel"] == rel) for rel in ("keyskip1", "keyskip2")}
    gate = all(c["recover"] >= 3 for c in pooled.values())
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "path": "real chunk path: pf_v4 frozen (m=24,k=2,rel=both) on a 2^16-seed chunk containing the plant -> v3 L=120 both rels on all survivors -> v3 L=240 -> panel; PLUS an unfiltered direct v3 L120/L240 decode of the planted seed (tier-a reach); natural-rate plants via real enc_exact/enc_pair; only filter = realised C[:40] doublet-free; NO skip-free selection; PHP seed uniform 32-bit",
           "bars_declared_N1e6": bars, "plants_per_cell_rel_register": NPL, "pooled_by_register_skip": pooled, "per_rel": per_rel, "per_cell_rel": per,
           "gate_ge3_recover_each_pooled_split": gate, "plants": plants, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(CALF, "w"), indent=1)
    print("POOLED", json.dumps(pooled)); print("GATE", gate)
    return 0 if gate else 1


# ------------------------------------------------------------------ tier a seeds (copied from round34/B1 sweep.py; that module rebinds HERE on import)
def tier_a_seeds():
    sys.path.append(os.path.join(LP, "analysis", "round13", "B04")); import seeds as B04
    core, dense, seen = [], [], set()

    def add(lst, x):
        x = int(x) & 0xFFFFFFFF
        if x not in seen: seen.add(x); lst.append(x)
    for x in B04.NUM_INTS: add(core, x)
    for x in B04.FIRST_PRIMES: add(core, x)
    for t in B04.NUM_STRINGS:
        try: add(core, int(t))
        except ValueError: pass
    for x in (3301, 1033, 761, 845145127, 1595277641, 1325734783, 1325635200, 1357257600, 1388880000, 2012, 2013, 2014, 29): add(core, x)
    for e in json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))["order"]: add(core, e["seed"])
    d0 = datetime.date(2011, 1, 1)
    for i in range((datetime.date(2015, 12, 31) - d0).days + 1):
        d = d0 + datetime.timedelta(days=i)
        add(dense, int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())); add(dense, d.year * 10000 + d.month * 100 + d.day)
    for x in range(0, 2048): add(dense, x)
    t0 = int(datetime.datetime(2011, 1, 1, tzinfo=datetime.timezone.utc).timestamp()); t1 = int(datetime.datetime(2016, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    for ts in range(t0, t1, 3600): add(dense, ts)
    return core, dense


# ------------------------------------------------------------------ sweep (resumable, append-only)
def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def power_block():
    return {g: {rel: {reg: I2P["php_" + g][rel][reg]["natural"]["power"] for reg in ("EN_MODERN", "EN_NOVOWEL", "EN_HALFVOWEL", "LATIN")}
                for rel in ("keyskip1", "keyskip2")} for g in CN}


def sweep():
    c = json.load(open(CALF))
    if not c["gate_ge3_recover_each_pooled_split"]: print("REFUSE: control gate failed"); return 2
    inhibit_sleep(); t0 = time.time()
    nonempty = os.path.exists(ROWS) and os.path.getsize(ROWS) > 0
    resume = nonempty and os.path.exists(SUMF)
    if nonempty and not resume: print("REFUSE: non-empty store without state"); return 3
    if resume:
        st = json.load(open(SUMF)); keep = json.load(open(KEEPF)); out = open(ROWS, "a"); st["resumes"] = st.get("resumes", 0) + 1
        print("RESUME (append mode)", flush=True)
    else:
        hdr = AD.header("round36/B2/php-awake-pfv4",
                        key_space="PHP 5.x mt_rand: twist {mt canonical, php<=7.0 legacy} x reduction {scale29, mod29} = 4 cells; tier a = 48,036 prior-dense seeds (487 core + 47,549 dense; core and a listed-order prefix of dense decoded UNFILTERED, remainder via pf_v4); tier b = uniform numpy default_rng(3301) blocks of 2^17 over [0,2^32), equal fraction per cell, target 330 blocks (1.007 %), compute-capped; offset 0, sign -1, C[0]-aligned",
                        decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate",
                        v3_version="round33/I1 beam_v3.py panel_max (sha256 %s); bars round34/I1 bars_v3 (gumbel, lp2)" % sha(os.path.join(R33, "I1-register-aware-beam", "beam_v3.py")),
                        prefilter={"name": "round35/I1 pf_v4", "frozen_op_sha256": sha(os.path.join(R35, "I1-skip-tolerant-screen", "frozen_op.json")), "m": M_PF, "k": KSK,
                                   "rel": "both", "thr_a1": FZ["thr"]["a1"], "thr_a2": FZ["thr"]["a2"], "pen": 2, "fpr": "~1e-3 total; R36-I2 realised 6.7e-4..9.6e-4 on PHP cells",
                                   "power_by_cell_rel_register_R36_I2_natural": power_block(), "rows_only_for": "prefilter survivors, except tier a core + unfiltered dense prefix (every seed)"},
                        register_panel="round32/I2 nine-register panel (models/panel.npz sha256 %s)" % sha(os.path.join(R32, "I2-multiregister-readjudication", "models", "panel.npz")),
                        n_round_adjudicated_reference=N_DECL, seed_sample="tier b numpy default_rng(3301) blocks 2^17; tier a list order of round34/B1 tier_a_seeds")
        out = open(ROWS, "w"); out.write(json.dumps(hdr) + "\n"); out.flush()
        st = {"cells": {cn: {"sub": {s: {"seeds": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}} for s in SUBS},
                              "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}, "hist": {}} for cn in CN},
              "prog": {"core": False, "dense_unf_idx": 0, "dense_unf_s": 0.0, "dense_unf_done": False, "dense_pf": False, "b_blocks": 0, "b_compute_s": 0.0, "gaps": [], "b_done": False},
              "caps": {"b_cap_s": B_CAP_S, "dense_unf_cap_s": DENSE_UNF_CAP_S, "b_target_blocks": B_TARGET_BLOCKS}, "resumes": 0, "wall_start": time.strftime("%Y-%m-%dT%H:%M:%S")}
        keep = []
    pg = st["prog"]

    def note(cn, sub, rows):
        S = st["cells"][cn]; SS = S["sub"][sub]
        for r in rows:
            for D in (S, SS):
                D["decodes"][r["rel"]] += 1; b = D["best"].get(r["rel"])
                if b is None or r["pmax"] > b["pmax"]: D["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"]}
            h = S["hist"].setdefault(r["rel"], {}); k = "%d" % math.floor(r["pmax"]); h[k] = h.get(k, 0) + 1
            if r["pmax"] >= KEEP: keep.append(r)

    def save():
        out.flush(); st["elapsed_s_this_run"] = round(time.time() - t0, 1)
        json.dump(st, open(SUMF + ".tmp", "w"), indent=1); os.replace(SUMF + ".tmp", SUMF)
        json.dump(keep, open(KEEPF + ".tmp", "w")); os.replace(KEEPF + ".tmp", KEEPF)

    core, dense = tier_a_seeds()
    assert len(core) == 487 and len(core) + len(dense) == 48036, (len(core), len(dense))
    st["tier_a"] = {"core": len(core), "dense": len(dense), "total": len(core) + len(dense)}
    C = C_SCREEN
    if not pg["core"]:
        for s in core:
            cache = {}
            for cn in CN:
                note(cn, "a_core", decode_cell(cn, s, cellkey(cn, cache, s), C, out, "a_core"))
        for cn in CN:
            st["cells"][cn]["sub"]["a_core"]["seeds"] += len(core); st["cells"][cn]["sub"]["a_core"]["survivors"] += len(core)
        pg["core"] = True; save(); print("core done %.0fs" % (time.time() - t0), flush=True)
    DB = 64
    while not pg["dense_unf_done"]:
        i = pg["dense_unf_idx"]
        if i >= len(dense) or pg["dense_unf_s"] >= DENSE_UNF_CAP_S: pg["dense_unf_done"] = True; save(); break
        tb = time.time()
        for s in dense[i:i + DB]:
            cache = {}
            for cn in CN: note(cn, "a_dense_unf", decode_cell(cn, s, cellkey(cn, cache, s), C, out, "a_dense_unf"))
        n = len(dense[i:i + DB])
        for cn in CN:
            SS = st["cells"][cn]["sub"]["a_dense_unf"]; SS["seeds"] += n; SS["survivors"] += n
        pg["dense_unf_idx"] = i + n; dt = time.time() - tb
        if dt >= STALL_S * 5: pg["gaps"].append({"phase": "dense_unf", "s": round(dt, 1)})
        else: pg["dense_unf_s"] += dt
        save()
        if (i // DB) % 20 == 0: print("dense_unf idx=%d/%d phase_s=%.0f" % (pg["dense_unf_idx"], len(dense), pg["dense_unf_s"]), flush=True)
    if not pg["dense_pf"]:
        rest = np.array(dense[pg["dense_unf_idx"]:], dtype=np.uint64); st["tier_a"]["dense_unfiltered"] = pg["dense_unf_idx"]; st["tier_a"]["dense_pf_v4"] = len(rest)
        for i in range(0, len(rest), BLK):
            blk = rest[i:i + BLK]
            for cn, (ns, rows) in block_screen(blk, C, out, "a_dense_pf").items():
                SS = st["cells"][cn]["sub"]["a_dense_pf"]; SS["seeds"] += len(blk); SS["survivors"] += ns; note(cn, "a_dense_pf", rows)
        pg["dense_pf"] = True; save(); print("dense pf done %.0fs" % (time.time() - t0), flush=True)
    rng = np.random.default_rng(3301)
    for _ in range(pg["b_blocks"]): rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)       # fast-forward on resume
    while not pg["b_done"]:
        if pg["b_blocks"] >= B_TARGET_BLOCKS or pg["b_compute_s"] >= B_CAP_S: pg["b_done"] = True; break
        tb = time.time(); blk = rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64)
        for cn, (ns, rows) in block_screen(blk, C, out, "b").items():
            SS = st["cells"][cn]["sub"]["b"]; SS["seeds"] += BLK; SS["survivors"] += ns; note(cn, "b", rows)
        dt = time.time() - tb; pg["b_blocks"] += 1
        if dt > STALL_S: pg["gaps"].append({"phase": "b", "block": pg["b_blocks"], "s": round(dt, 1)})
        else: pg["b_compute_s"] += dt
        save()
        if pg["b_blocks"] % 5 == 0:
            print("b blocks=%d/%d compute_s=%.0f wall_run=%.0f surv=%s best=%s" % (pg["b_blocks"], B_TARGET_BLOCKS, pg["b_compute_s"], time.time() - t0,
                  {cn: st["cells"][cn]["sub"]["b"]["survivors"] for cn in CN}, {cn: st["cells"][cn]["best"] for cn in CN}), flush=True)
    st["tier_b_fraction_of_2p32"] = pg["b_blocks"] * BLK / 2.0 ** 32; st["complete_all_phases"] = True
    save(); out.close(); print("SWEEP DONE", flush=True)
    return 0


# ------------------------------------------------------------------ finalize
def finalize():
    st = json.load(open(SUMF)); keep = json.load(open(KEEPF)); ctl = json.load(open(CALF))
    summ = {"cells": {}, "flagged": [], "near_miss": [], "subsets": {}}
    for cn, S in st["cells"].items():
        summ["subsets"][cn] = {s: {"seeds": v["seeds"], "survivors": v["survivors"], "decodes": v["decodes"], "best": v["best"]} for s, v in S["sub"].items()}
        for rel in ("keyskip1", "keyskip2"):
            N = S["decodes"][rel]
            if N == 0: continue
            b120, b240 = bar_v3(N, 120, rel), bar_v3(N, 240, rel); d120, d240 = bar_v3(N_DECL, 120, rel), bar_v3(N_DECL, 240, rel)
            best = S["best"][rel]
            cand = sorted([r for r in keep if r["cell"] == cn and r["rel"] == rel], key=lambda r: -r["pmax"])
            ent = {"N_actual": N, "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3), "bar240_declN": round(d240, 3),
                   "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"], "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "best_by_subset": {s: S["sub"][s]["best"].get(rel) for s in SUBS},
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"], r["sub"]) for r in cand[:5]]}
            for r in [r for r in cand if r["pmax"] >= b120]:
                tw, rd = cn.split("_"); K = PM.ks(int(r["seed"]), tw, rd, 1024); d, a = v3dec(U[:L_HIT], K, rel); p240 = float(a["pmax"])
                e = {"cell": cn, "rel": rel, "seed": r["seed"], "sub": r["sub"], "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3),
                     "preg240": PAN.registers[a["preg"]], "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3),
                     "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (cn, rel)] = ent
    frac_b = st.get("tier_b_fraction_of_2p32", 0.0); reach = {}
    for rel in ("keyskip1", "keyskip2"):
        for reg in ("EN_MODERN", "EN_NOVOWEL"):
            q = [p for p in ctl["plants"] if p["rel"] == rel and p["register"] == reg]
            pf = sum(p["prefilter_pass"] for p in q); rec_c = sum(p["recover"] for p in q) / max(pf, 1); rec_u = sum(p["recover_unfiltered"] for p in q) / len(q)
            for cn in CN:
                pw = I2P["php_" + cn][rel][reg]["natural"]["power"]
                reach["%s|%s|%s" % (cn, rel, reg)] = {"pf_v4_power_I2": pw, "v3_recovery_given_prefilter_pass": round(rec_c, 3), "v3_recovery_unfiltered": round(rec_u, 3),
                                                         "n_control_plants_pooled_cells": len(q),
                                                         "tier_b_reach": round(pw * rec_c * frac_b, 5), "tier_a_unfiltered_reach": round(rec_u, 3),
                                                         "tier_a_dense_pf_reach": round(pw * rec_c, 3)}
    summ["reach"] = reach; summ["tier_b_fraction_of_2p32"] = frac_b; summ["tier_a"] = st.get("tier_a"); summ["prog"] = st["prog"]
    try: summ["validate_store"] = {"rows_validated": AD.validate_store(ROWS)["rows_validated"]}
    except Exception as ex: summ["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    summ["check_r3_store"] = VL.check_r3_store(ROWS)
    json.dump(summ, open(F("sweep_summary_final.json"), "w"), indent=1)
    for k, v in summ["cells"].items(): print(k, v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"], v["clears_declN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]), summ["validate_store"], summ["check_r3_store"])


if __name__ == "__main__":
    sys.exit({"control": control, "sweep": sweep, "finalize": finalize}[sys.argv[1]]())
