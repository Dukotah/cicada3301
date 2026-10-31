"""R40-B3 engine: the R37-I2 instrument (imported unchanged) + a generic grid screen/decode/control machinery.
Writes ONLY inside this directory."""
import os, sys, re, json, time, random, math, importlib.util, subprocess
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round40/B3-english-era-grids"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


S = _load("r37sweep", os.path.join(LP, "analysis", "round37", "I2-pfv4-12reg", "sweep.py"))
AD, C1, PAN, B2, pf, V = S.AD, S.C1, S.PAN, S.B2, S.pf_v4, S.V
F = lambda n: os.path.join(HERE, n)
RELS = ("keyskip1", "keyskip2")
U = list(S.U)
TEST = S.TEST
M = pf.FROZEN["m"]; K_SK = pf.FROZEN["k"]
THR = pf.FROZEN["thr"]; PEN = {1: pf.FROZEN["pen_a1"], 2: pf.FROZEN["pen_a2"]}
N_DECL = 10 ** 6; KEEP = 6.0
CTRL_REGS = ("EN_MODERN", "EN_NOVOWEL", "LATIN")
SCREEN_CHUNK = 16384


def free_gb():
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"],
                           capture_output=True, text=True, timeout=30).stdout
        return float(o.strip())
    except Exception:
        return 9.9


def wait_mem(minq=0.4, maxwait=1200):
    t = time.time()
    while True:
        g = free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        print("RAM wait: free %.2f GB" % g, flush=True); time.sleep(60)


def bar(N, L, rel):
    return S.bar_v3(max(N, 2), L, rel)


# ------------------------------------------------------------------ screen
def screen_cols(K28, C24, atbs=(0, 1)):
    """K28 (28,B) int8 base stream heads (decode = C' - K).  C24 (24,) raw ciphertext head.
    Returns {(atb, sign): bool mask (B,)} for the four variants."""
    out = {}
    Craw = np.asarray(C24, dtype=np.int32)
    Kn = ((-K28.astype(np.int16)) % 29).astype(np.int8)
    for atb in atbs:
        C = Craw if atb == 0 else (28 - Craw)
        for sg in (-1, 1):
            Ke = K28 if sg == -1 else Kn
            m = np.zeros(K28.shape[1], bool)
            for a in (1, 2):
                R = pf.dp_regs(C, Ke[:M + a * K_SK], K_SK, a, PEN[a], ms=(M,), chunk=SCREEN_CHUNK)
                m |= pf.lse_from_regs(R[M], M) > THR["a%d" % a]
            out[(atb, sg)] = m
    return out


def apply_variant(Cfull, Kfull, atb, sg):
    C = list(Cfull) if atb == 0 else [28 - c for c in Cfull]
    K = list(Kfull) if sg == -1 else [(-k) % 29 for k in Kfull]
    return C, K


def v3dec(C, K, rel):
    return S.v3dec(C, K, rel)


# ------------------------------------------------------------------ SWEEPROW store
def header(sweep_id, key_space):
    return AD.header(sweep_id, pan=PAN, with_degenerate=True, key_space=key_space,
        decoder="beam_v3 beam_decode_v3 panel_max tau=0 lam_u=4 beam_w=400 under panel-R36; keyskip1=advance1 keyskip2=advance2; L120 screen / L240 gate",
        v3_version="round33/I1 beam_v3.py panel_max (set_panel -> panel-R36); bars round36/B1 null12.json POT fit",
        prefilter={"name": "round37/I2 pf_v4_12 (frozen_op12.json, instrument unchanged; key heads from the regenerated English-era grids)", "m": M, "k": 2, "rel": "both",
                   "thr_a1": THR["a1"], "thr_a2": THR["a2"], "frozen_op": "analysis/round37/I2-pfv4-12reg/frozen_op12.json", "rows_only_for": "prefilter survivors"},
        register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=S.P12_SHA, n_registers=12, panel_build="panel-R36 (round36/P1 build1; sha256 " + S.P12_SHA[:8] + ")",
        corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)", n_round_adjudicated_reference=N_DECL, seed_sample="enumeration order of the regenerated list")


class Store:
    def __init__(self, name, key_space):
        self.rows = F("rows_%s.jsonl" % name); self.sumf = F("summary_%s.json" % name); self.keepf = F("keep_%s.json" % name)
        new = not os.path.exists(self.rows)
        self.out = open(self.rows, "a")
        if new: self.out.write(json.dumps(header("round40/B3/" + name, key_space)) + "\n")
        self.st = {"grid": name, "screened": 0, "survivors": 0, "decodes": {r: 0 for r in RELS}, "best": {}, "hist": {r: {} for r in RELS},
                   "by_group": {}, "keep_n": 0}
        self.keep = []
        self.t0 = time.time()

    def note(self, meta, rel, a, kid):
        self.out.write(json.dumps(AD.to_row(a, kid, with_degenerate=True)) + "\n")
        st = self.st; st["decodes"][rel] += 1; p = float(a["pmax"])
        b = st["best"].get(rel)
        if b is None or p > b["pmax"]:
            st["best"][rel] = {"pmax": round(p, 3), "preg": PAN.registers[a["preg"]], "kid": kid, "degenerate": bool(a.get("degenerate", False))}
        h = st["hist"][rel]; k = "%d" % math.floor(p); h[k] = h.get(k, 0) + 1
        if p >= KEEP:
            self.keep.append({"kid": kid, "rel": rel, "pmax": round(p, 3), "preg": PAN.registers[a["preg"]], "meta": meta,
                              "degenerate": bool(a.get("degenerate", False))})

    def group(self, g, screened, surv):
        d = self.st["by_group"].setdefault(g, [0, 0]); d[0] += screened; d[1] += surv

    def save(self, done=False):
        self.out.flush()
        self.st["elapsed_s"] = round(time.time() - self.t0, 1); self.st["complete"] = done
        json.dump(self.st, open(self.sumf, "w"), indent=1); json.dump(self.keep, open(self.keepf, "w"))

    def close(self):
        self.save(self.st.get("complete", False)); self.out.close()


# ------------------------------------------------------------------ generic grid sweep
def run_grid(grid, store, cap_s=None, mem_every=6, log_every=4):
    """grid.batches() yields dicts: K28 (28,B) int8, metas (len B), Cs [(cname, Cfull list)], group (str)."""
    t0 = time.time(); nb = 0
    for bt in grid.batches():
        if cap_s and time.time() - t0 > cap_s:
            store.st["capped"] = True; break
        if nb % mem_every == 0: wait_mem()
        K28, metas = bt["K28"], bt["metas"]; B = K28.shape[1]
        for (cname, Cfull) in bt["Cs"]:
            atbs = getattr(grid, "atbs", (0, 1))
            masks = screen_cols(K28, Cfull[:M], atbs)
            scr = 2 * len(atbs) * B; surv = 0
            for (atb, sg), m in masks.items():
                for j in np.nonzero(m)[0]:
                    meta = metas[int(j)]; surv += 1
                    Kf = grid.keyfull(meta)
                    L = min(120, len(Cfull))
                    C, Ke = apply_variant(Cfull[:L], Kf, atb, sg)
                    for rel in RELS:
                        try:
                            d, a = v3dec(C, Ke, rel)
                        except Exception as ex:
                            store.st["decode_errors"] = store.st.get("decode_errors", 0) + 1; continue
                        kid = "%s|%s|v%d%d|%s|%s" % (grid.name, grid.meta_str(meta), atb, 1 if sg == 1 else 0, cname, rel)
                        mm = dict(meta); mm.update(atb=atb, sg=sg, cname=cname)
                        store.note(mm, rel, a, kid)
            store.st["screened"] += scr; store.st["survivors"] += surv
            store.group(bt["group"], scr, surv)
        nb += 1
        if nb % log_every == 0:
            store.save()
            print("%s batch %d t=%.0fs screened=%d surv=%d best=%s" % (grid.name, nb, time.time() - t0, store.st["screened"], store.st["survivors"], store.st["best"]), flush=True)
    store.save(not store.st.get("capped", False))


# ------------------------------------------------------------------ planted controls
def rec_of(d, P):
    return float(B2.recovery(d["plain_idx"], P))


def plant_for(grid, rel, reg, rng, L_HIT=240):
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(800):
        meta = grid.random_meta(rng)
        Kf = grid.keyfull(meta)
        atb = rng.choice(getattr(grid, "atbs", (0, 1))); sg = rng.choice((-1, 1))
        Lh = grid.plant_len(meta)
        if len(Kf) < int(1.1 * Lh) + 24: continue
        st = rng.randrange(0, len(arr) - 300); P = arr[st:st + Lh].tolist()
        Kenc = Kf if sg == -1 else [(-k) % 29 for k in Kf]
        try:
            Cp = enc(P, Kenc, seed=rng.randrange(1, 10 ** 9))[:Lh]
        except IndexError:
            continue
        if len(Cp) < Lh: continue
        if any(Cp[i] == Cp[i + 1] for i in range(39)): continue
        Craw = Cp if atb == 0 else [28 - c for c in Cp]
        naive = [(P[i] + Kenc[i]) % 29 for i in range(Lh)]
        nsk = int(any(Cp[i] != naive[i] for i in range(24)))
        return meta, atb, sg, Craw, P, nsk, Lh
    raise RuntimeError("no plant")


def control(grid, npl=10, ndecoy=512, seed=3301, regs=CTRL_REGS):
    rng = random.Random(seed); plants = []; t0 = time.time()
    bars = {r: {"L120": bar(N_DECL, 120, r), "L240": bar(N_DECL, 240, r)} for r in RELS}
    for reg in regs:
        for rel in RELS:
            for j in range(npl):
                meta, atb, sg, Craw, P, nsk, Lh = plant_for(grid, rel, reg, rng)
                # real screen path: planted column + decoy columns of the same grid, same screen function
                cols = [meta] + [grid.random_meta(rng) for _ in range(ndecoy)]
                K28 = np.stack([grid.head28(mt) for mt in cols], axis=1)
                masks = screen_cols(K28, Craw[:M], getattr(grid, "atbs", (0, 1)))
                passed = bool(masks[(atb, sg)][0]); fp = int(sum(int(m[1:].sum()) for m in masks.values()))
                e = {"grid": grid.name, "rel": rel, "register": reg, "meta": grid.meta_str(meta), "atb": atb, "sg": sg, "Lh": Lh,
                     "with_skip_head24": bool(nsk), "prefilter_pass": passed, "decoy_survivors": fp, "decoys": 2 * len(getattr(grid, "atbs", (0, 1))) * ndecoy,
                     "pmax120": None, "pmax240": None, "recovery": None, "pass": False, "recover": False}
                if passed:
                    Kf = grid.keyfull(meta); C, Ke = apply_variant(Craw[:min(120, Lh)], Kf, atb, sg)
                    d, a = v3dec(C, Ke, rel); e["pmax120"] = round(float(a["pmax"]), 3)
                    if Lh >= 240:
                        C2, Ke2 = apply_variant(Craw[:240], Kf, atb, sg)
                        d2, a2 = v3dec(C2, Ke2, rel); e["pmax240"] = round(float(a2["pmax"]), 3); e["recovery"] = round(rec_of(d2, P), 4)
                        e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"] and e["pmax240"] >= bars[rel]["L240"])
                    else:  # L=120-only plant (KDF rev, 184-symbol buffer)
                        e["recovery"] = round(rec_of(d, P), 4)
                        e["pass"] = bool(e["pmax120"] >= bars[rel]["L120"])
                    e["recover"] = bool(e["pass"] and e["recovery"] >= 0.90)
                plants.append(e)
            print("%.0fs" % (time.time() - t0), grid.name, reg, rel, flush=True)

    def tab(sel):
        out = {}
        for reg in regs:
            for sk_ in (False, True):
                ps_ = [p for p in plants if sel(p) and p["register"] == reg and p["with_skip_head24"] == sk_]
                out["%s|%s" % (reg, "with_skip" if sk_ else "skip_free")] = {"n": len(ps_), "prefilter": sum(p["prefilter_pass"] for p in ps_),
                                                                          "pass": sum(p["pass"] for p in ps_), "recover": sum(p["recover"] for p in ps_)}
        return out
    pooled = tab(lambda p: True)
    per_rel = {r: tab(lambda p, r=r: p["rel"] == r) for r in RELS}
    gate = {k: v["recover"] >= 3 for k, v in pooled.items()}
    reg_ok = {reg: all(v["recover"] >= 3 for k, v in pooled.items() if k.startswith(reg + "|")) for reg in regs}
    n_dec = sum(p["decoys"] for p in plants); n_fp = sum(p["decoy_survivors"] for p in plants)
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "grid": grid.name,
           "path": "grid key function -> sweep screen (screen_cols, pf_v4_12 frozen) on planted column + %d random decoy columns of the same grid -> v3 L=120 -> L=240 -> panel; natural-rate plants via real enc_exact/enc_pair; atbash/sign applied as in the sweep; only filter: C[:40] doublet-free" % ndecoy,
           "bars_declared_N1e6": bars, "plants_per_register_rel": npl, "pooled_by_register_skip": pooled, "per_rel": per_rel,
           "gate_cells_ge3": gate, "register_licensed": reg_ok, "decoy_fpr": {"n": n_dec, "survivors": n_fp, "rate": n_fp / max(n_dec, 1)},
           "elapsed_s": round(time.time() - t0, 1), "plants": plants}
    json.dump(out, open(F("control_%s.json" % grid.name), "w"), indent=1)
    print("POOLED", json.dumps(pooled)); print("LICENSED", reg_ok, "decoy fpr", out["decoy_fpr"])
    return out
