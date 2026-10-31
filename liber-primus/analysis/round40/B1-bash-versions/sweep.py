#!/usr/bin/env python3
"""R40 B1: bash 3.2 / 4.0 / 4.1 / 5.1 auto-seed orbits under the R37-I2 instrument (imported unchanged).
Usage: python sweep.py verify | run | finalize.  Writes ONLY inside this file's directory."""
import os, sys, re, json, time, random, math, importlib.util, hashlib, subprocess, difflib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round40/B1-bash-versions"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


R37 = os.path.join(LP, "analysis", "round37", "I2-pfv4-12reg")
S = _load("r37sweep", os.path.join(R37, "sweep.py"))
sys.path.insert(0, HERE)
import generators as G
S.pf_v4.heads = G.heads                      # pf_v4_12.prefilter_mask resolves `heads` in its own module globals
AD, C1, PAN, B2 = S.AD, S.C1, S.PAN, S.B2
F = lambda n: os.path.join(HERE, n)
ROWS, SUMF, KEEPF = F("sweep_rows.jsonl"), F("sweep_summary.json"), F("keep_rows.json")
REPL_ROWS = F("replication_rows_bash4.1.jsonl")
SRC = os.environ.get("B1_SRC", "")
RELS = S.RELS; L_SCREEN = S.L_SCREEN; N_DECL = S.N_DECL; KEEP = 6.0
CAP_V = int(os.environ.get("B1_CAP", 2900)); END = float(os.environ.get("B1_END", 0)) or None
NPL = 10; CTRL = ("EN_MODERN", "EN_NOVOWEL", "HEBREW")


def header(sweep_id, key_space):
    return AD.header(sweep_id, pan=PAN, with_degenerate=True, key_space=key_space,
        decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400 under panel-R36; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate",
        v3_version="round33/I1 beam_v3.py panel_max (set_panel -> panel-R36); bars round36/B1 null12.json POT fit",
        prefilter={"name": "round37/I2 pf_v4_12 (frozen_op12.json, instrument unchanged; keystream heads swapped per bash version)", "m": S.M_PF, "k": 2, "rel": "both",
                   "thr_a1": S.pf_v4.FROZEN["thr"]["a1"], "thr_a2": S.pf_v4.FROZEN["thr"]["a2"], "frozen_op": "analysis/round37/I2-pfv4-12reg/frozen_op12.json", "rows_only_for": "prefilter survivors"},
        register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=S.P12_SHA, n_registers=12, panel_build="panel-R36 (round36/P1 build1; sha256 " + S.P12_SHA[:8] + ")",
        corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)", n_round_adjudicated_reference=N_DECL, seed_sample="chunk order per version (see key_space)")


def decode_seed(v, seed, C, out=None):
    K = G.ks(seed, v, 1024); res = []
    for rel in RELS:
        d, a = S.v3dec(C[:L_SCREEN], K, rel)
        if out is not None: out.write(json.dumps(AD.to_row(a, "bash:%s:%d:%s" % (v, seed, rel), with_degenerate=True)) + "\n")
        res.append({"seed": int(seed), "cell": v, "rel": rel, "pmax": float(a["pmax"]), "preg": PAN.registers[a["preg"]]})
    return res


def chunk_bash(seeds, v, C, out=None):
    m = S.pf_v4.prefilter_mask(seeds, v, np.array(C[:S.M_PF], dtype=np.int8), S.M_PF, "both")
    surv = seeds[m]; rows = []
    for s in surv: rows += decode_seed(v, int(s), C, out)
    return len(surv), rows


# ------------------------------------------------------------------ verify
def sh(c):
    return subprocess.run(c, capture_output=True, text=True, timeout=120).stdout


def block(path, a, b):
    t = open(path, encoding="latin-1").read(); i = t.index(a); j = t.index(b, i); return t[i:j]


def verify():
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "generators": {}, "tarball_sha256": {}, "source_lines": {}}
    for v in ("3.2", "4.0", "4.1", "4.2", "5.1"):
        p = os.path.join(SRC, "b-%s.tgz" % v)
        if os.path.exists(p): out["tarball_sha256"][v] = {"url": "https://ftp.gnu.org/gnu/bash/bash-%s.tar.gz" % v, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(), "bytes": os.path.getsize(p)}
        vp = os.path.join(SRC, "variables-%s.c" % v)
        if os.path.exists(vp):
            L = open(vp, encoding="latin-1").read().split("\n")
            out["source_lines"][v] = {"variables.c": {k: [i + 1 for i, l in enumerate(L) if re.search(k, l)][:6] for k in (r"^brand \(\)", r"^sbrand \(", r"^seedrand \(\)", r"rseed = ", r"seedrand \(\);|sbrand \(dollar")}}

    def blk(v): return block(os.path.join(SRC, "variables-%s.c" % v), "/* The random number seed.", "static SHELL_VAR *\nget_random (var)")
    d = {}
    for a, b in (("4.0", "4.1"), ("4.1", "4.2"), ("3.2", "4.0")):
        d["%s_vs_%s" % (a, b)] = "".join(difflib.unified_diff(blk(a).splitlines(1), blk(b).splitlines(1), "variables.c@" + a, "variables.c@" + b, n=0))
    out["variables_c_random_block_diffs"] = d
    out["random_c_5_1_sha256"] = hashlib.sha256(open(os.path.join(SRC, "random-5.1.c"), "rb").read()).hexdigest()
    gb = _load("g1gen", os.path.join(LP, "analysis", "round19", "G1", "gen_bash.py"))
    rng = random.Random(40); xi = {}

    def cmp(vmine, vg1, seeds, n=1024):
        bad = 0
        for s in seeds:
            a, hit = G.raws(s, n, vmine, fill_zero=False)
            b = gb.raws(s, n, vg1)
            if hit: continue
            bad += (a != b)
        return {"seeds": len(seeds), "n": n, "mismatches": bad}
    for vm, vg, name in (("bash3.2", "bash3.2", "3.2"), ("bash4.1", "bash4.2", "4.1"), ("bash4.0", "bash4.2", "4.0"), ("bash4.1_i32", "bash4.2_i32", "4.1_i32"), ("bash5.1", "bash5.1", "5.1")):
        seeds = [G.sample_seed(vm if vm != "bash4.1_i32" else "bash4.1", rng) for _ in range(2000)]
        xi[name] = cmp(vm, vg, seeds)
    out["cross_impl_vs_R19_G1_gen_bash"] = xi
    pre = [m * 2147483647 for m in range(0, 46)]
    zr = {"preimages_of_zero_LP64": len(pre), "all_step_to_zero": all(G.brand_40(s)[1] == 0 for s in pre if s != 0),
          "argument": "f(s)=16807*l-2836*h with s=127773h+l; |16807*l|<2.2e9 and 2836*h<4.2e17 << 2^64 so f(s)==0 mod 2^64 iff 16807*l==2836*h; gcd(16807,2836)=1 => l=2836m,h=16807m, l<127773 => m<=45, s=m*2147483647. Same for ILP32 (m<=2). Lehmer states below 2^31-1 never equal m*(2^31-1), m>=1; a state can reach 0 only by hitting one of 45 specific 64-bit (2 specific 32-bit) values after a negative-residue wrap.",
          "expected_orbit_seeds_with_zero_in_first_1024_steps_heuristic": {"LP64": 77594624 * 1024 * 45 / 2 ** 64, "ILP32": 77594624 * 1024 * 2 / 2 ** 32}}
    out["zero_state"] = zr
    live = {"version": sh(["bash", "--version"]).split("\n")[0], "cases": {}}
    for s in (1, 3301, 12345, 1354603465, 2147483646, 4000000000):
        o = sh(["bash", "-c", 'RANDOM=%d; for i in $(seq 1 200); do echo -n "$RANDOM "; done' % s]).split()
        mine = G.raws(s, 200, "bash5.1")[0]
        live["cases"][str(s)] = {"match": [int(x) for x in o] == mine, "first20": mine[:20]}
    out["live_bash_reference_for_5x"] = live
    out["first20_after_RANDOM_equals_1"] = {v: G.raws(1, 20, v)[0] for v in ("bash3.2", "bash4.1", "bash5.1")}
    vh = {}
    for v in G.VARIANTS:
        sv = v if v != "bash4.0_i32" else "bash4.1"
        seeds = np.array([G.sample_seed(sv, rng) for _ in range(3000)], dtype=np.uint64)
        H = G.heads(seeds, 28, v); bad = 0
        for i, s in enumerate(seeds):
            st = int(s) & G.MASK[v]; ref = []
            for _ in range(28):
                r, st = G.BRANDS[v](st); ref.append(r % 29 if r != G.NONDET else -9)
            bad += ref != H[:, i].tolist()
        vh[v] = {"seeds": 3000, "mismatches": int(bad)}
    out["vector_heads_vs_scalar_no_antirepeat"] = vh
    out["orbit"] = {v: {"seeds": G.orbit_size(v), "chunks": len(G.orbit_chunks(v))} for v in ("bash3.2", "bash4.1", "bash5.1")}
    json.dump(out, open(F("verification_raw.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("cross_impl_vs_R19_G1_gen_bash", "zero_state", "vector_heads_vs_scalar_no_antirepeat", "orbit")}, indent=1)[:3500])
    print(json.dumps(live)[:900]); print(d["4.0_vs_4.1"] or "4.0==4.1 (empty diff)"); print(d["4.1_vs_4.2"][:1500]); return 0


# ------------------------------------------------------------------ control
def plant(v, rel, reg, rng):
    arr = S.TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(500):
        ps = G.sample_seed(v, rng); K = G.ks(ps, v, 1024)
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + 240].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:240]
        if len(C) < 240: continue
        if any(C[i] == C[i + 1] for i in range(39)): continue
        naive = [(P[i] + K[i]) % 29 for i in range(240)]
        return ps, C, P, int(any(C[i] != naive[i] for i in range(24)))
    raise RuntimeError("no plant")


def control(v, npl=NPL):
    rng = random.Random(3301 + sum(map(ord, v))); plants = []; t0 = time.time()
    bars = {r: {"L120": S.bar_v3(N_DECL, 120, r), "L240": S.bar_v3(N_DECL, 240, r)} for r in RELS}
    for rel in ("keyskip1", "keyskip2"):
        for reg in CTRL:
            for j in range(npl):
                ps, Cp, P, wsk = plant(v, rel, reg, rng)
                base = ps & ~0xFFFF; seeds = np.arange(base, base + (1 << 16), dtype=np.uint64)
                n_s, rr = chunk_bash(seeds, v, Cp)
                mine = [r for r in rr if r["seed"] == ps and r["rel"] == rel]
                e = {"version": v, "rel": rel, "register": reg, "seed": int(ps), "with_skip_head24": bool(wsk), "prefilter_pass": any(r["seed"] == ps for r in rr),
                     "survivors_in_chunk": n_s, "pmax120": None, "pmax240": None, "recovery240": None, "pass": False, "recover": False}
                if mine:
                    e["pmax120"] = round(mine[0]["pmax"], 3)
                    d, a = S.v3dec(Cp, G.ks(ps, v, 1024), rel)
                    e["pmax240"] = round(float(a["pmax"]), 3); e["recovery240"] = round(float(B2.recovery(d["plain_idx"], P)), 4)
                    e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"] and e["pmax240"] >= bars[rel]["L240"])
                    e["recover"] = bool(e["pass"] and e["recovery240"] >= 0.90)
                plants.append(e)
            print("%.0fs" % (time.time() - t0), v, rel, reg, flush=True)

    def tab(sel):
        o = {}
        for reg in CTRL:
            for sk in (False, True):
                q = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == sk]
                o["%s|%s" % (reg, "with_skip" if sk else "skip_free")] = {"n": len(q), "prefilter": sum(p["prefilter_pass"] for p in q), "pass": sum(p["pass"] for p in q), "recover": sum(p["recover"] for p in q)}
        return o
    pooled = tab(lambda p: True)
    per_rel = {rel: tab(lambda p, rel=rel: p["rel"] == rel) for rel in RELS}
    gate = all(c["recover"] >= 3 for c in pooled.values())
    per_rel_n = {rel: {reg: sum(1 for p in plants if p["rel"] == rel and p["register"] == reg) for reg in CTRL} for rel in RELS}
    out = {"version": v, "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "path": "real chunk path: pf_v4_12 frozen (m=24,k=2,rel=both) on 2^16-seed chunk containing the planted seed -> v3 L=120 both rels on all survivors -> v3 L=240 -> panel-R36; natural-rate plants via enc_exact/enc_pair; only filter = realised C[:40] doublet-free; NO skip-free selection; keystream = this version's generator",
           "bars_declared_N1e6": bars, "plants_per_rel_register": per_rel_n, "pooled_by_register_skip": pooled, "per_rel": per_rel, "gate_ge3_recover_each_pooled_split": gate,
           "recover_total": sum(p["recover"] for p in plants), "n_plants": len(plants), "elapsed_s": round(time.time() - t0, 1), "plants": plants}
    json.dump(out, open(F("control_%s.json" % v.replace("bash", "")), "w"), indent=1)
    print("CONTROL", v, "gate", gate, json.dumps(pooled)); return gate


# ------------------------------------------------------------------ replication of 4.1 against R37 4.2 LP64 rows
def replicate41(nchunks=8):
    PREF = list(range(S.SEC0 >> 20, (S.SEC1 >> 20) + 1)); ch = [(p, s) for p in PREF for s in range(0, 1 << 20, S.SUB)]
    random.Random(3301).shuffle(ch); ch = ch[:nchunks]
    r37 = {}
    with open(os.path.join(R37, "sweep_rows.jsonl")) as f:
        f.readline()
        for line in f:
            r = json.loads(line); k = r[0].split(":")
            if k[1] == "bash4.2": r37[(int(k[2]), k[3])] = r[3]
    out = open(REPL_ROWS, "a")
    if os.path.getsize(REPL_ROWS) == 0:
        out.write(json.dumps(header("round40/B1/bash4.1-replication-vs-R37-4.2-LP64", "bash 4.1 replication: first %d chunks of R37-I2's Random(3301)-shuffled 296-chunk bash4.2 LP64 order" % nchunks)) + "\n")
    mine = {}; nsurv = 0; ts = time.time()
    for (p, s) in ch:
        seeds = np.arange((p << 20) | s, ((p << 20) | s) + S.SUB, dtype=np.uint64)
        n_s, rows = chunk_bash(seeds, "bash4.1", S.C_SCREEN, out); nsurv += n_s
        for r in rows: mine[(r["seed"], r["rel"])] = r["pmax"]
    out.close()
    lo_hi = [((p << 20) | s, ((p << 20) | s) + S.SUB) for (p, s) in ch]
    theirs = {k: v for k, v in r37.items() if any(a <= k[0] < b for a, b in lo_hi)}
    same_keys = set(mine) == set(theirs)
    maxdiff = max([abs(mine[k] - theirs[k]) for k in mine if k in theirs] or [0])
    res = {"chunks": nchunks, "chunks_ids": [(p, s) for p, s in ch], "seeds": nchunks * S.SUB, "survivors_4.1": nsurv, "rows_4.1": len(mine), "rows_R37_4.2_LP64_same_chunks": len(theirs),
           "identical_survivor_decode_sets": same_keys, "max_abs_pmax_diff_3dp": maxdiff, "zero_state_events_seen": G.ZERO_EVENTS.get("bash4.1", 0), "elapsed_s": round(time.time() - ts, 1)}
    json.dump(res, open(F("replication_4.1_vs_R37.json"), "w"), indent=1); print("REPL", res); return res


# ------------------------------------------------------------------ sweep
def sweep_version(v, out, st, keep, t0, save):
    chunks = G.orbit_chunks(v)
    if v == "bash3.2": random.Random(3301).shuffle(chunks)
    ts = time.time(); cap = CAP_V if END is None else min(CAP_V, END - ts)
    ph = {"chunks_total": len(chunks), "seeds_total": sum(b - a for a, b in chunks), "chunks_done": 0, "cap_s": round(cap, 1)}; st["phase"][v] = ph
    Sx = st["cells"][v]
    for (a, b) in chunks:
        if time.time() - ts > cap or (END and time.time() > END): break
        if ph["chunks_done"] % 8 == 0: S.wait_mem()
        seeds = np.arange(a, b, dtype=np.uint64)
        n_s, rows = chunk_bash(seeds, v, S.C_SCREEN, out)
        Sx["seeds_screened"] += b - a; Sx["survivors"] += n_s
        for r in rows:
            Sx["decodes"][r["rel"]] += 1; bb = Sx["best"].get(r["rel"])
            if bb is None or r["pmax"] > bb["pmax"]: Sx["best"][r["rel"]] = {"pmax": round(r["pmax"], 3), "seed": r["seed"], "preg": r["preg"]}
            h = Sx["hist"].setdefault(r["rel"], {}); k = "%d" % math.floor(r["pmax"]); h[k] = h.get(k, 0) + 1
            if r["pmax"] >= KEEP: keep.append(r)
        ph["chunks_done"] += 1; ph["elapsed_s"] = round(time.time() - ts, 1)
        if ph["chunks_done"] % 4 == 0:
            out.flush(); save(); print("%s chunk %d/%d t=%.0fs surv=%d best=%s zero=%s" % (v, ph["chunks_done"], len(chunks), time.time() - ts, Sx["survivors"], Sx["best"], G.ZERO_EVENTS), flush=True)
    ph["seeds_done"] = Sx["seeds_screened"]; ph["fraction_of_orbit"] = ph["chunks_done"] / len(chunks); ph["complete"] = ph["chunks_done"] == len(chunks)
    out.flush(); save()


def run():
    t0 = time.time(); S.wait_mem()
    gates = {}
    for v in ("bash3.2", "bash5.1", "bash4.1", "bash4.0"):
        gates[v] = control(v)
    json.dump(gates, open(F("control_gates.json"), "w"))
    replicate41()
    first = not os.path.exists(ROWS) or os.path.getsize(ROWS) == 0
    out = open(ROWS, "a")
    if first:
        out.write(json.dumps(header("round40/B1/bash-versions-3.2-5.1", "bash 3.2 (seed=pid+tv_sec, 76,237,568 seeds, 291 chunks of 2^18 shuffled Random(3301)) and bash 5.1 non-PIE family (prefix XOR {0..7}: 88x2^20=92,274,688 seeds, 352 chunks, x=4 image first); %29, offset 0, sign -1, C[0]-aligned")) + "\n")
    st = {"cells": {k: {"seeds_screened": 0, "survivors": 0, "decodes": {"keyskip1": 0, "keyskip2": 0}, "best": {}, "hist": {}} for k in ("bash3.2", "bash5.1")}, "phase": {}, "control_gates": gates, "cap_per_version_s": CAP_V}
    keep = []

    def save(done=False):
        st["elapsed_s"] = round(time.time() - t0, 1); st["complete_all_phases"] = done; st["zero_events"] = G.ZERO_EVENTS; st["trunc"] = G.TRUNC
        json.dump(st, open(SUMF, "w"), indent=1); json.dump(keep, open(KEEPF, "w"))
    for v in ("bash3.2", "bash5.1"):
        if not gates[v]:
            print("REFUSE sweep", v, "control gate failed"); st["phase"][v] = {"refused": "control failed"}; continue
        sweep_version(v, out, st, keep, t0, save)
    out.close(); save(True); print("SWEEP DONE"); finalize(); return 0


# ------------------------------------------------------------------ finalize
def finalize():
    st = json.load(open(SUMF)); keep = json.load(open(KEEPF))
    summ = {"cells": {}, "flagged": [], "near_miss": []}
    for cell, Sx in st["cells"].items():
        for rel in RELS:
            N = Sx["decodes"][rel]
            if N == 0: continue
            b120, b240 = S.bar_v3(N, 120, rel), S.bar_v3(N, 240, rel); d120, d240 = S.bar_v3(N_DECL, 120, rel), S.bar_v3(N_DECL, 240, rel)
            best = Sx["best"][rel]
            cand = sorted([r for r in keep if r["cell"] == cell and r["rel"] == rel], key=lambda r: -r["pmax"])
            ent = {"N_actual": N, "seeds_screened": Sx["seeds_screened"], "survivors": Sx["survivors"], "bar120_actualN": round(b120, 3), "bar120_declN": round(d120, 3), "bar240_actualN": round(b240, 3), "bar240_declN": round(d240, 3),
                   "best_pmax": best["pmax"], "best_seed": best["seed"], "best_preg": best["preg"], "clears_actualN": best["pmax"] >= b120, "clears_declN": best["pmax"] >= d120,
                   "top5": [(round(r["pmax"], 3), r["seed"], r["preg"]) for r in cand[:5]]}
            for r in [r for r in cand if r["pmax"] >= b120]:
                d, a = S.v3dec(S.U[:S.L_HIT], G.ks(r["seed"], cell, 1024), rel); p240 = float(a["pmax"])
                e = {"cell": cell, "rel": rel, "seed": r["seed"], "pmax120": round(r["pmax"], 3), "preg120": r["preg"], "pmax240": round(p240, 3), "preg240": PAN.registers[a["preg"]],
                     "bar120_actualN": round(b120, 3), "bar240_actualN": round(b240, 3), "clears240_actualN": bool(p240 >= b240), "clears_declN_both": bool(r["pmax"] >= d120 and p240 >= d240), "certified": False}
                if p240 >= b240: e["FLAGGED_FOR_ORACLE"] = True; summ["flagged"].append(e)
                if r["pmax"] < d120: summ["near_miss"].append(e)
            summ["cells"]["%s|%s" % (cell, rel)] = ent
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    for pth in (ROWS, REPL_ROWS):
        k = os.path.basename(pth)
        try:
            AD.validate_store(pth); summ["validate_store_" + k] = "ok"
        except Exception as ex:
            summ["validate_store_" + k] = "FAIL %s" % ex
        summ["check_r3_store_" + k] = VL.check_r3_store(pth)
    json.dump(summ, open(F("sweep_summary_final.json"), "w"), indent=1)
    for k, v in summ["cells"].items(): print(k, v["N_actual"], v["best_pmax"], v["bar120_actualN"], v["bar120_declN"], v["clears_actualN"], v["clears_declN"])
    print("flagged", len(summ["flagged"]), "near", len(summ["near_miss"]), {k: v for k, v in summ.items() if k.startswith(("validate", "check"))})
    return 0


if __name__ == "__main__":
    sys.exit({"verify": verify, "run": run, "finalize": finalize}[sys.argv[1]]())
