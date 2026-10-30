#!/usr/bin/env python3
"""R37 C3: re-score the reopened English-only / legacy-beam families under panel-R36 (12 registers) + beam_v3.
   python rescore.py control | u5 | u6a | u6b | final        (one stage per process; resumable per family; writes only in this dir)
Rows are SWEEPROW (12-wide z) in parts/<family>.jsonl (append mode), merged by `final` into rescore_rows.jsonl."""
import os, sys, re, json, time, math, random, hashlib, importlib.util, subprocess
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
assert HERE.replace("\\", "/").endswith("round37/C3-rescore-reopened"), HERE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AN = os.path.join(LP, "analysis")
R = lambda n: os.path.join(AN, "round%d" % n)
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R(32), "B1-bash-random"))
C1 = _load("b1common", os.path.join(R(32), "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R(33), "I1-register-aware-beam"))
import beam_v3 as V
AD = C1.AD; B2 = V.B2; U = list(C1.U); NC = C1.nc
P12_PATH = os.path.join(R(36), "P1-panel-r36", "build1", "panel12.npz")
TH12_PATH = os.path.join(R(36), "P1-panel-r36", "build1", "testhalves12.npz")
P12_SHA = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
assert hashlib.sha256(open(P12_PATH, "rb").read()).hexdigest() == P12_SHA
PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN; V.PANEL_PATH = P12_PATH
REGS = list(PAN.registers); assert len(REGS) == 12
TEST = np.load(TH12_PATH)
LMT = PAN.LMT.astype(np.float32)                      # (24389, 12)
NULL12 = json.load(open(os.path.join(R(36), "B1-orbit-12reg", "null12.json")))["cells"]
RELS = ("keyskip1", "keyskip2"); ADV = {"keyskip1": 1, "keyskip2": 2}
F = lambda *a: os.path.join(HERE, *a)
os.makedirs(F("parts"), exist_ok=True)
T0 = time.time(); LOG = open(F("rescore.log"), "a")
N = 29


def log(*a):
    s = "[%6.0fs] " % (time.time() - T0) + " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def free_gb():
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"], capture_output=True, text=True, timeout=30).stdout
        return float(o.strip())
    except Exception:
        return 9.9


def wait_mem(minq=0.4, maxwait=1200):
    t = time.time()
    while True:
        g = free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        log("RAM wait: free %.2f GB" % g); time.sleep(60)


def bar12(Nn, L, rel, alpha=0.01):
    c = NULL12["L%d|%s" % (L, rel)]
    return c["mu"] + c["beta"] * math.log(float(Nn) / -math.log1p(-alpha))


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


# ------------------------------------------------------------------ direct panel scoring
def _sd_scale(n): return math.sqrt(n / 1000.0) if n > 1000 else 1.0


def zbatch(X):
    """X (B,n) int64 -> z (B,12), panel-R36 with the n>1000 sd-clamp corrected (z scaled by sqrt(n/1000))."""
    X = np.asarray(X, dtype=np.int64); B, n = X.shape
    mu, sd, _, _ = PAN.cal(n); sd = sd * (1.0 / _sd_scale(n))
    out = np.empty((B, 12)); step = max(1, 500000 // n)
    for st in range(0, B, step):
        blk = X[st:st + step]
        f = blk[:, :-2] * 841 + blk[:, 1:-1] * 29 + blk[:, 2:]
        out[st:st + step] = LMT[f].mean(axis=1, dtype=np.float64)
    return (out - mu) / sd


def pm_many(streams):
    """dict name->array  -> dict name->pmax (batches by length)."""
    by = {}
    for k, v in streams.items():
        by.setdefault(len(v), []).append(k)
    res = {}
    for n, ks in by.items():
        if n < 32:
            for k in ks: res[k] = float("nan")
            continue
        z = zbatch(np.stack([np.asarray(streams[k], dtype=np.int64) for k in ks]))
        for k, zz in zip(ks, z): res[k] = float(zz.max())
    return res


def adj_row(x, kid):
    """SWEEPROW for a bare rune stream; z/pmax/pmax_ne/pcon rescaled by sqrt(n/1000) when n>1000 (panel cal clamps at the grid end)."""
    x = np.asarray(x, dtype=np.int64); r = AD.adjudicate(x, pan=PAN); f = _sd_scale(len(x))
    if f != 1.0:
        r["z"] = [float(v) * f for v in r["z"]]; r["pmax"] = float(r["pmax"]) * f; r["pmax_ne"] = float(r["pmax_ne"]) * f; r["pcon"] = float(r["pcon"]) * f
    return AD.to_row(r, kid)


def hdr(sweep_id, key_space, decoder, universe):
    return AD.header(sweep_id, pan=PAN, key_space=key_space, decoder=decoder,
                     v3_version="round33/I1 beam_v3.py panel_max (PANEL repointed to panel-R36); direct rows = panel-R36 on the bare stream (n>1000 z rescaled by sqrt(n/1000))",
                     register_panel="panel-R36 round36/P1-panel-r36/build1/panel12.npz", panel_sha256=P12_SHA, n_registers=12,
                     panel_build="panel-R36 (P1 build1, byte-reproducible; sha256 " + P12_SHA[:8] + ")",
                     corpora_sha256="see round36/P1-panel-r36/inputs_r36.json (53 inputs)", universe_units=universe, universe_rows=universe)


class Part:
    """Append-mode row sink for one family; done-marker makes the family resumable at family granularity."""
    def __init__(self, fam, key_space, decoder, universe):
        self.fam = fam; self.path = F("parts", fam + ".jsonl"); self.done = F("parts", fam + ".done"); self.n = 0
        if os.path.exists(self.done): self.skip = True; return
        self.skip = False
        self.f = open(self.path, "w"); self.f.write(json.dumps(hdr("round37/C3/" + fam, key_space, decoder, universe)) + "\n")

    def add(self, row):
        self.f.write(json.dumps(row) + "\n"); self.n += 1
        if self.n % 200 == 0: self.f.flush()

    def close(self, meta):
        self.f.flush(); self.f.close(); json.dump(meta, open(self.done, "w"), indent=1, default=float)


DOUBLET_TARGET = 86       # LP2 0-54 has 86 adjacent equal pairs (iid expectation ~447): the doublet suppression is a known real property


def dfshuffle(seq, rng, target=DOUBLET_TARGET):
    """histogram-preserving shuffle repaired to the LP2 doublet level (<= target adjacent equal pairs)."""
    x = list(seq); rng.shuffle(x); n = len(x)
    bad = [i for i in range(n - 1) if x[i] == x[i + 1]]; cnt = len(bad)
    for i in bad:
        if cnt <= target: break
        if x[i] != x[i + 1]: continue
        for _ in range(40):
            j = rng.randrange(2, n - 2)
            if abs(j - i) < 3: continue
            a, b = x[i + 1], x[j]
            if b != x[i] and b != x[i + 2] and a != x[j - 1] and a != x[j + 1] and a != b:
                x[i + 1], x[j] = b, a; cnt -= 1; break
    return x


# ------------------------------------------------------------------ generic family-wise direct evaluation
def eval_family(streams, gen_null, D, tag, part=None, raw_best=True):
    """streams: dict name->array. gen_null(j) -> dict name->array (any subset).  Returns summary dict.
    Per stream standardised Z = (pmax-mean_null)/sd_null; family stat = max_k Z_k vs family max of the same draw index."""
    obs = pm_many(streams); names = [k for k in streams if obs[k] == obs[k]]
    nul = {k: np.full(D, np.nan, dtype=np.float32) for k in names}
    t0 = time.time()
    for j in range(D):
        g = gen_null(j); pm = pm_many({k: v for k, v in g.items() if k in nul})
        for k, v in pm.items(): nul[k][j] = v
        if (j + 1) % 100 == 0:
            log(tag, "null", j + 1, "of", D, "%.1fs" % (time.time() - t0))
            if (j + 1) % 500 == 0 and free_gb() < 0.25: wait_mem(0.4)
    Z = {}; M = np.full(D, -1e9)
    for k in names:
        a = nul[k]; ok = ~np.isnan(a)
        if ok.sum() < 20: continue
        mu, sd = float(a[ok].mean()), float(a[ok].std(ddof=1)) or 1e-9
        Z[k] = (obs[k] - mu) / sd
        zn = np.where(ok, (a - mu) / sd, -1e9); M = np.maximum(M, zn)
    kbest = max(Z, key=Z.get); Mobs = Z[kbest]
    exc = int((M >= Mobs).sum()); p = (1 + exc) / (D + 1)
    out = {"n_streams": len(names), "D": D, "best_stream": kbest, "best_pmax": obs[kbest], "best_Z": Mobs,
           "null_max_Z_q99": float(np.quantile(M, .99)), "null_max_Z_max": float(M.max()), "exceed": exc, "p_family": p,
           "wilson95_exceed_rate": wilson(exc, D), "top5": sorted(((round(Z[k], 3), round(obs[k], 3), k) for k in Z), reverse=True)[:5]}
    if raw_best:                                   # lane-style raw statistic: best-of-family pmax
        bn = np.full(D, -1e9)
        for k in names: bn = np.maximum(bn, np.where(np.isnan(nul[k]), -1e9, nul[k]))
        bo = max(obs[k] for k in names); e2 = int((bn >= bo).sum())
        out["raw_best"] = {"obs_best_pmax": bo, "obs_best_stream": max(names, key=lambda k: obs[k]), "null_best_mean": float(bn.mean()), "null_best_max": float(bn.max()),
                           "null_best_q99": float(np.quantile(bn, .99)), "exceed": e2, "p": (1 + e2) / (D + 1), "wilson95_exceed_rate": wilson(e2, D)}
    if part is not None:
        for k in streams:
            part.add(adj_row(streams[k], "%s:%s" % (tag, k)))
    out["_Z"] = Z; out["_null_famMax"] = M
    return out


def plant_stream(reg, n, seed):
    arr = TEST[reg].astype(np.int64); st = random.Random(seed).randrange(0, len(arr) - n - 1); return arr[st:st + n]


def direct_control(res, nrep, tag, D=300):
    """Plant a held-out text of the family's typical length through the identical direct pipeline; it must beat the
    family-wise null-max q99 (Z of the planted stream vs its own shuffle null)."""
    ctl = {}
    for reg in ("EN_MODERN", "LATIN", "GREEK"):
        P = plant_stream(reg, nrep, 7); obs = pm_many({"p": P})["p"]
        a = np.array([pm_many({"p": np.random.RandomState(1000 + j).permutation(P)})["p"] for j in range(D)])
        Zp = (obs - a.mean()) / (a.std(ddof=1) or 1e-9)
        ctl[reg] = {"n": nrep, "plant_pmax": round(obs, 3), "null_mean": round(float(a.mean()), 3), "Z_plant": round(float(Zp), 2),
                    "family_null_maxZ_q99": round(res["null_max_Z_q99"], 3), "pass": bool(Zp > res["null_max_Z_q99"] + 1.0)}
    ctl["all_pass"] = all(v["pass"] for v in ctl.values() if isinstance(v, dict))
    log(tag, "direct control", {k: v["Z_plant"] for k, v in ctl.items() if isinstance(v, dict)}, ctl["all_pass"])
    return ctl


def finish_direct(part, fam, res, ctl, extra):
    meta = {"family": fam, "kind": "direct", "control": ctl, **{k: v for k, v in res.items() if not k.startswith("_")}, **extra}
    part.close(meta); log(fam, "done: best", res["best_stream"], "pmax %.3f Z %.2f p_family %.4f" % (res["best_pmax"], res["best_Z"], res["p_family"]), "control", ctl["all_pass"])
    return meta


# ================================================================== BEAM machinery
def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), list(K), ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"], pan=PAN)


def run_beam_family(fam, cfgs, starts, L, key_space, decoder, null_draws=100, tag=None):
    """cfgs: list of (cfgname, C_full, K_full, sign_b, start_list or None). Streams rows for both relations; family-matched
    wrong-key null (shuffled U windows, same keys) after the real rows."""
    part = Part(fam, key_space, decoder, 0)
    if part.skip: log(fam, "already done"); return json.load(open(part.done))
    wait_mem(); t0 = time.time(); best = {r: (-1e9, None, None, None) for r in RELS}; nrow = {r: 0 for r in RELS}; npreg = {r: {} for r in RELS}
    for (cn, C, K, sg, sts) in cfgs:
        for s in (sts if sts is not None else starts):
            if s + L > len(C): continue
            Cw = C[s:s + L]; Kw = K[s:s + 1024] if len(K) >= s + 1024 else list(K[s:]) + [0] * (s + 1024 - len(K))
            for rel in RELS:
                d = _dec_sign(Cw, Kw, rel, sg)
                a = AD.adjudicate(d["plain_idx"], pan=PAN); kid = "%s:%s:w%d:%s" % (fam, cn, s, rel)
                part.add(AD.to_row(a, kid)); nrow[rel] += 1
                pm = float(a["pmax"]); npreg[rel][REGS[a["preg"]]] = npreg[rel].get(REGS[a["preg"]], 0) + 1
                if pm > best[rel][0]: best[rel] = (pm, kid, REGS[a["preg"]], float(a["pmax_ne"]))
        if nrow[RELS[0]] % 100 < 20 and free_gb() < 0.25: wait_mem(0.4)
        log(fam, cn, "rows", nrow, "%.0fs" % (time.time() - t0))
    # family-matched wrong-key null: shuffled LP2 windows, keys drawn from the family's own configs
    rng = random.Random(3301); nul = {r: [] for r in RELS}
    for k in range(null_draws):
        cn, C, K, sg, sts = cfgs[rng.randrange(len(cfgs))]; s = rng.choice(sts if sts is not None else starts)
        sh = U[:]; random.Random(3301 + k).shuffle(sh); Cw = sh[:L]
        Kw = K[s:s + 1024] if len(K) >= s + 1024 else list(K[s:]) + [0] * (s + 1024 - len(K))
        for rel in RELS:
            d = _dec_sign(Cw, Kw, rel, sg); a = AD.adjudicate(d["plain_idx"], pan=PAN)
            part.add(AD.to_row(a, "null:%s:%d:%s" % (fam, k, rel))); nul[rel].append(float(a["pmax"]))
    meta = {"family": fam, "kind": "beam", "L": L, "n_configs": len(cfgs), "rows": nrow,
            "best": {r: {"pmax": best[r][0], "kid": best[r][1], "preg": best[r][2], "pmax_ne": best[r][3]} for r in RELS},
            "bars": {r: {"actualN": round(bar12(max(nrow[r], 1), L, r), 3), "declared_1e6": round(bar12(1e6, L, r), 3)} for r in RELS},
            "family_null": {r: {"n": len(nul[r]), "mean": float(np.mean(nul[r])), "max": float(np.max(nul[r]))} for r in RELS},
            "argmax_register_hist": npreg, "elapsed_s": round(time.time() - t0, 1)}
    meta["clears_actualN"] = {r: bool(best[r][0] >= meta["bars"][r]["actualN"]) for r in RELS}
    meta["clears_declared"] = {r: bool(best[r][0] >= meta["bars"][r]["declared_1e6"]) for r in RELS}
    part.close(meta); log(fam, "done", json.dumps({r: (round(best[r][0], 3), meta["bars"][r]["actualN"], meta["bars"][r]["declared_1e6"]) for r in RELS}))
    return meta


def _dec_sign(Cw, Kw, rel, sg):
    return V.beam_decode_v3(list(Cw), list(Kw), ADV[rel], "panel_max", tau=0.0, lam_u=4.0, sign=sg)


# ================================================================== family key/stream generators
PRIMES = NC.PRIMES
SEGS = NC.segments()[:-2]
PAGE_START = [0]
for _s in SEGS: PAGE_START.append(PAGE_START[-1] + len(_s))
assert PAGE_START[-1] == len(U) == 12956


def n1_ct_cfgs():
    FUNCS = {"mod29": lambda s: s % N, "totient": lambda s: (s - 1) % N if s > 0 else 0,
             "digitsum": None}

    def digitsum(s):
        while s >= 10: s = sum(int(d) for d in str(s))
        return s % N
    FUNCS["digitsum"] = digitsum
    cfgs = []
    for fname, f in FUNCS.items():
        for sign in (1, -1):
            for direction in ("fwd", "rev"):
                for mode in ("cont", "reset"):
                    if mode == "cont":
                        st = U[::-1] if direction == "rev" else list(U); K = []; run = 0
                        for c in st: K.append(f(run)); run += PRIMES[c]
                    else:
                        st = []; K = []
                        for seg in SEGS:
                            sg_ = seg[::-1] if direction == "rev" else seg; run = 0
                            for c in sg_: K.append(f(run)); run += PRIMES[c]
                            st += sg_
                    cfgs.append(("%s_s%+d_%s_%s" % (fname, sign, direction, mode), st, K, -sign, None))
    return cfgs, FUNCS


def n1_pt_streams(u, FUNCS):
    """regenerated PT-feedback decodes (lane code, copied unchanged): name -> decoded stream (list)."""
    out = {}
    for fname, f in FUNCS.items():
        for sign in (1, -1):
            for direction in ("fwd", "rev"):
                st = u[::-1] if direction == "rev" else u; p = []; run = 0
                for ci in st:
                    pi = (ci - sign * f(run)) % N; p.append(pi); run += PRIMES[pi]
                out["PT_%s_s%+d_%s_cont" % (fname, sign, direction)] = np.array(p, dtype=np.int64)
                dec = []
                for seg in SEGS:
                    sg_ = seg[::-1] if direction == "rev" else seg; run = 0
                    if len(u) != 12956: pass
                    for ci in sg_:
                        pi = (ci - sign * f(run)) % N; dec.append(pi); run += PRIMES[pi]
                out["PT_%s_s%+d_%s_reset" % (fname, sign, direction)] = np.array(dec, dtype=np.int64)
    return out


def planes(src=None):
    vals = NC.v_prime(U if src is None else src); out = []
    for base in (3, 5, 7, 10):
        mx = max(vals); pl = 0; v = mx
        while v > 0: pl += 1; v //= base
        for place in range(max(pl, 1)): out.append((base, place, NC.digit_plane(vals, base=base, place=place)))
    return out


def n4_cfgs():
    cfgs = []
    for base, place, pl in planes():
        for sign in (-1, 1):
            cfgs.append(("b%d_p%d_ks%+d" % (base, place, sign), list(U), [int(x) for x in pl], sign, None))
    return cfgs


def n5_mod():
    return _load("n5mod", os.path.join(R(11), "N5", "n5.py"))


def n5_cfgs(n5):
    cfgs = []
    # continuous: start offsets 0, 4800, 9600 ; per-segment restart: page starts of pages 18 and 36 with K from index 0
    for gname, fn in n5.GENERATORS.items():
        ks = fn(U)
        for sign in (1, -1):
            for off in range(N):
                K = [(k + off) % N for k in ks]
                cfgs.append(("%s_s%+d_o%d" % (gname, sign, off), list(U), K, sign, [0, 4800, 9600]))
                for pg in (18, 36):
                    seg = SEGS[pg]; kp = [(k + off) % N for k in fn(seg)]
                    cfgs.append(("%s_s%+d_o%d_seg%d" % (gname, sign, off, pg), list(seg), kp, sign, [0]))
    return cfgs


# ================================================================== CONTROL stage
def plant_beam(reg, rel, K, rng, L=240):
    arr = TEST[reg].astype(np.int64); enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    for _ in range(200):
        st = rng.randrange(0, len(arr) - L - 5); P = arr[st:st + L].tolist()
        C = enc(P, K, seed=rng.randrange(1, 10 ** 9))[:L]
        if len(C) >= L: return C, P
    raise RuntimeError("no plant")


def control_stage():
    wait_mem(); rng = random.Random(3301); out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": P12_SHA, "families": {}}
    n5 = n5_mod()
    n1c, FUNCS = n1_ct_cfgs()
    fam_keys = {"N1ct": [c[2] for c in n1c], "N4ks": [c[2] for c in n4_cfgs()], "N5": [c[2] for c in n5_cfgs(n5) if len(c[2]) > 5000][::31],
                "X3b": None, "X4": None}
    KE = _key_english(); fam_keys["X3b"] = [KE]
    fam_keys["X4"] = [[v % N for v in NC.v_totient(U)], [v % N for v in NC.v_prime(U)], [v % N for v in NC.v_prime_index(U)]]
    b = {r: {"L120": bar12(1e6, 120, r), "L240": bar12(1e6, 240, r)} for r in RELS}
    t0 = time.time()
    for fam, Ks in fam_keys.items():
        plants = []
        for reg in ("EN_MODERN", "LATIN", "GREEK"):
            for rel in RELS:
                for j in range(2):
                    K = Ks[rng.randrange(len(Ks))]; s0 = rng.randrange(0, 4000); Kw = K[s0:s0 + 1024]
                    C, P = plant_beam(reg, rel, Kw, rng)
                    d1, a1 = v3dec(C[:120], Kw, rel); d2, a2 = v3dec(C, Kw, rel)
                    rec = float(B2.recovery(d2["plain_idx"], P))
                    e = {"register": reg, "rel": rel, "key_start": s0, "pmax120": round(float(a1["pmax"]), 3), "pmax240": round(float(a2["pmax"]), 3),
                         "preg240": REGS[a2["preg"]], "recovery240": round(rec, 4)}
                    e["recover"] = bool(e["pmax120"] >= b[rel]["L120"] and e["pmax240"] >= b[rel]["L240"] and rec >= 0.9); plants.append(e)
        for rel in RELS + ("both",):
            q = [p for p in plants if rel == "both" or p["rel"] == rel]
        tab = {rel: {"n": len([p for p in plants if p["rel"] == rel]), "recover": sum(p["recover"] for p in plants if p["rel"] == rel)} for rel in RELS}
        ok = all(v["recover"] >= 4 for v in tab.values())      # >=4 of 6 per relation
        out["families"][fam] = {"table": tab, "gate_ge4_of_6_per_relation": ok, "plants": plants}
        log("control", fam, tab, ok, "%.0fs" % (time.time() - t0))
    # N5 real-artifact control: AN END under phi(prime) (lambda_prime == p_i - 1), no offset, sign -1
    ae = NC.anend(); n5m = n5; ks = [k % N for k in n5m.ks_lambda_prime(ae)]; truth = [(c - k) % N for c, k in zip(ae, ks)]
    ae_res = {"n_anend": len(ae), "direct_decode_head": "".join(NC.gp.IDX_TO_TRANS[i] for i in truth[:20])}
    for rel in RELS:
        d, a = v3dec(ae[:120], ks[:1024], rel); ae_res[rel] = {"pmax120": round(float(a["pmax"]), 3), "preg": REGS[a["preg"]], "recovery120": round(float(B2.recovery(d["plain_idx"], truth[:120])), 4),
                                                              "bar120_declared": round(b[rel]["L120"], 3)}
        ae_res[rel]["pmax_ge_L120_bar"] = bool(ae_res[rel]["pmax120"] >= b[rel]["L120"]); ae_res[rel]["pass"] = bool(ae_res[rel]["recovery120"] >= 0.9 and ae_res[rel]["preg"] == "LP1_REAL")   # AN END is only 85 runes (< L=120): bar comparison reported, not gated
    out["N5_AN_END_real_artifact"] = ae_res; log("control AN END", ae_res)
    out["bars_declared_N1e6_12reg"] = b
    out["all_beam_pass"] = bool(all(v["gate_ge4_of_6_per_relation"] for v in out["families"].values()) and all(ae_res[r]["pass"] for r in RELS))
    json.dump(out, open(F("control_beam.json"), "w"), indent=1)
    log("CONTROL beam all_pass", out["all_beam_pass"])


_KE = None


def _key_english():
    global _KE
    if _KE is None:
        sys.path.insert(0, AN)
        from run_stats import english_baseline
        e = english_baseline()
        while len(e) < 4000: e = e + e
        _KE = list(e[:4000])
    return _KE


# ================================================================== U5
def _mapc():
    sys.path.insert(0, os.path.join(R(10), "L2-map")); import mapcommon as M; return M


def variants_stack(seq):
    """29 shifts x {id, atbash} x {fwd, rev} -> (names, (116,n) array)."""
    seq = np.asarray(seq, dtype=np.int64); names = []; rows = []
    for bn, base in (("id", seq), ("atbash", 28 - seq)):
        for rn, rv in (("fwd", base), ("rev", base[::-1])):
            for k in range(N): names.append("%s/%s/+%d" % (bn, rn, k)); rows.append((rv + k) % N)
    return names, np.stack(rows)


def m1_streams(W):
    Wf = [[r for r in w if r != 0] or [w[0]] for w in W]
    types = {"first": [w[0] for w in W], "last": [w[-1] for w in W], "first/noF": [w[0] for w in Wf], "last/noF": [w[-1] for w in Wf]}
    out = {}
    for t, seq in types.items():
        names, st = variants_stack(seq)
        for nm, row in zip(names, st): out["M1:%s:%s" % (t, nm)] = row
    return out


def m1_pm_fast(W):
    """pmax of every pooled M1 reading (464): dict name -> pmax"""
    return pm_many(m1_streams(W))


def wnums(W):
    gp_primes = PRIMES
    sp = np.array([sum(gp_primes[r] for r in w) for w in W]); si = np.array([sum(w) for w in W]); ln = np.array([len(w) for w in W])
    return {"Sprime": sp, "Sidx": si, "len": ln}


def m2_streams(W):
    Wf = [[r for r in w if r != 0] or [w[0]] for w in W]; out = {}
    for wt, ww in (("W", W), ("noF", Wf)):
        for nm, arr in wnums(ww).items():
            base = (arr % N).astype(np.int64)
            for bn, b in (("id", base), ("atbash", 28 - base)):
                for k in range(N): out["M2:%s:%s:%s+%d" % (nm, wt, bn, k)] = (b + k) % N
    return out


def m9_streams(W):
    M = _mapc(); flat = np.array(M.flat(W)); L = len(flat); n = len(W)
    sp, si, ln = wnums(W).values()
    wstart = np.concatenate(([0], np.cumsum([len(w) for w in W])[:-1]))
    fams = {"Sprime->rune": sp % L, "Sidx->rune": si % L, "cumSprime->rune": np.cumsum(sp) % L, "cumSidx->rune": np.cumsum(si) % L,
            "Sprime+pos->rune": (sp + wstart) % L, "Sidx+pos->rune": (si + wstart) % L, "Sprime->word-initial": sp % n, "Sidx->word-initial": si % n,
            "cumSidx->word-initial": np.cumsum(si) % n, "len*idx->rune": (ln * np.arange(1, n + 1)) % L}
    inits = np.array([w[0] for w in W]); out = {}
    for nm, arr in fams.items():
        src = inits if "word-initial" in nm else flat; seq = src[np.asarray(arr) % len(src)]
        for k in range(N): out["M9:%s+%d" % (nm, k)] = (seq + k) % N
    return out


def m5_streams(W, maxlen=400):
    n = len(W); sp, si, ln = wnums(W).values()
    first = np.array([w[0] for w in W]); last = np.array([w[-1] for w in W])
    steps = {"len": ln, "Sidx29": si % N, "Sprime29": sp % N, "Sidxn": si % n, "first": first, "last": last, "Sidx26p1": si % 26 + 1}
    inits = [w[0] for w in W]; starts = list(range(0, n, max(1, n // 32)))[:32]; out = {}
    for nm, f in steps.items():
        f = np.asarray(f)
        for mode in ("self", "cum"):
            for sgn in (1, -1):
                for st in starts:
                    p = st; acc = 0; path = []; seen = set()
                    for _ in range(maxlen):
                        if p in seen: break
                        seen.add(p); path.append(p); d_ = int(f[p])
                        if mode == "cum": acc += d_; p = (st + sgn * acc) % n
                        else: p = (p + sgn * max(1, d_)) % n
                    if len(path) < 24: continue
                    out["M5:%s/%s/%+d/start%d/initials" % (nm, mode, sgn, st)] = np.array([inits[i] for i in path], dtype=np.int64)
                    b = [r for i in path for r in W[i]]; out["M5:%s/%s/%+d/start%d/whole" % (nm, mode, sgn, st)] = np.array(b[:1200], dtype=np.int64)
    return out


def null_B(words, seed):
    """round10 run_map.py::null_B (copied unchanged): permute the WORD ORDER."""
    rng = random.Random(seed); w = words[:]; rng.shuffle(w); return w


def u5_l2_stage():
    M = _mapc(); d = M.parse(); W = d["words"]; assert len(W) == 2928 and sum(map(len, W)) == 12956
    wait_mem()
    # ---- (1) the pooled M1 family and the z=6.94 near-flag: 464 readings vs 2,000 null_A draws (lane's own null)
    fam = "U5_L2_M1_pooled"
    part = Part(fam, "M1 pooled: 4 stream types x 116 transforms (29 shifts x id/atbash x fwd/rev) = 464 regenerated readings; null_A (rune content shuffled, word boundaries held), 2000 draws",
                "direct panel-R36 pmax of the bare stream (no decode)", 464)
    if not part.skip:
        streams = m1_streams(W)
        ctl_gate = None
        res = eval_family(streams, lambda j: m1_streams(M.null_A(W, 100000 + j)), 2000, fam, part=part, raw_best=True)
        res_nrep = 2928
        ctl = direct_control(res, res_nrep, fam)
        orig = "M1:first/noF:atbash/rev/+28"
        zo = [float(v) for v in zbatch(np.array([streams[orig]]))[0]]
        extra = {"original_z694_reading": orig, "original_reading_pmax": max(zo), "original_reading_z_by_register": dict(zip(REGS, [round(v, 3) for v in zo])),
                 "original_reading_Z_vs_family": res["_Z"].get(orig), "original_english_gated_stat": {"ng_abs": -16.51, "z": 6.94}}
        finish_direct(part, fam, res, ctl, extra)
    fam = "U5_L2_M1_pooled_dfnull"
    part = Part(fam, "M1 pooled 464 readings, null = flat rune stream doublet-level-matched shuffle (dfshuffle) re-cut into the identical word lengths, 2000 draws", "direct panel-R36 pmax", 464)
    if not part.skip:
        streams = m1_streams(W); lens = [len(w) for w in W]
        def gdf(j):
            x = dfshuffle(M.flat(W), random.Random(500000 + j)); out = []; k = 0
            for L_ in lens: out.append(x[k:k + L_]); k += L_
            return m1_streams(out)
        res = eval_family(streams, gdf, 2000, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, 2928, fam), {"original_reading_Z_vs_family": res["_Z"].get("M1:first/noF:atbash/rev/+28")})
    # ---- (2) per-page M1 (55 pages x 4 types x 116)
    fam = "U5_L2_M1_perpage"
    part = Part(fam, "M1 per-page acrostics: 55 pages x 4 stream types x 116 transforms = 25,520 regenerated short streams; null_A 200 draws", "direct panel-R36 pmax", 25520)
    if not part.skip:
        wp = d["w_page"]
        def pp(WW):
            out = {}
            for pg in range(55):
                sw = [w for w, p in zip(WW, wp) if p == pg]
                if len(sw) < 40: continue
                for k, v in m1_streams(sw).items(): out["p%d:%s" % (pg, k)] = v
            return out
        streams = pp(W)
        res = eval_family(streams, lambda j: pp(M.null_A(W, 200000 + j)), 200, fam, part=None)
        for kk in sorted(res["_Z"], key=res["_Z"].get, reverse=True)[:300]: part.add(adj_row(streams[kk], "%s:%s" % (fam, kk)))
        ctl = direct_control(res, 53, fam, D=200)
        finish_direct(part, fam, res, ctl, {"rows_stored": "top-300 by standardised Z of 25,520 (all 25,520 scored; full per-stream table not persisted to bound store size)"})
    # ---- (3) M2 / M9 / M5 families
    for fam, fn, nm, D in (("U5_L2_M2", m2_streams, "M2 word sum/len mod 29 streams: 3 numbers x 2 F-handling x 2 base x 29 shifts = 348", 300),
                           ("U5_L2_M9", m9_streams, "M9 word-number addresses into the rune stream / word initials: 10 families x 29 shifts = 290", 300),
                           ("U5_L2_M5", m5_streams, "M5 word-level walk paths: 7 steps x 2 modes x 2 signs x 32 starts x {initials,whole}", 100)):
        part = Part(fam, nm + "; null " + ("null_B (word order permuted)" if fam.endswith("M2") else "null_A (content shuffled, boundaries held)"), "direct panel-R36 pmax", 0)
        if part.skip: continue
        streams = fn(W)
        gen = (lambda j: m2_streams(null_B(W, 300000 + j))) if fam.endswith("M2") else (lambda j, fn=fn: fn(M.null_A(W, 400000 + j)))
        res = eval_family(streams, gen, D, fam, part=part)
        nrep = int(np.median([len(v) for v in streams.values()]))
        finish_direct(part, fam, res, direct_control(res, nrep, fam, D=200), {})


def u5_l3_stage():
    sys.path.insert(0, os.path.join(R(10), "L3-road")); path = os.path.join(R(10), "L3-road", "road.py")
    lines = open(path, encoding="utf-8").read().split("\n")
    src = "\n".join(lines[0:172] + lines[245:316])              # setup+defs, and readings() (T1 count tests skipped)
    ns = {"__name__": "road_chunk", "__file__": path}; exec(compile(src, path + "#chunk", "exec"), ns)
    WORDS, S, readings, shuffled_words, R_ = ns["WORDS"], ns["S"], ns["readings"], ns["shuffled_words"], ns["R"]
    wait_mem(); fam = "U5_L3_T234"
    part = Part(fam, "L3 T2/T3/T4 readings (road.py::readings exec'd unchanged, ~208 streams); lane null = LP2 stream shuffled and re-cut into the identical word-length sequence", "direct panel-R36 pmax", 208)
    if not part.skip:
        rd = {k: np.asarray(v, dtype=np.int64) % N for k, v in readings(WORDS, S).items()}
        rngn = np.random.default_rng(3301)
        def gen(j):
            sw = shuffled_words(rngn); ss = R_.wsum(sw)
            return {k: np.asarray(v, dtype=np.int64) % N for k, v in readings(sw, ss).items()}
        res = eval_family(rd, gen, 300, fam, part=part)
        nrep = int(np.median([len(v) for v in rd.values()]))
        finish_direct(part, fam, res, direct_control(res, nrep, fam, D=200), {"n_readings": len(rd)})
    fam = "U5_L3_T5"
    part = Part(fam, "L3 T5 word-sum book-code streams (first letters of key-text words picked by s%M, cumsum%M, (s*i)%M)", "direct panel-R36 pmax", 0)
    if not part.skip:
        KEYT = []
        for f in ("kjv.txt", "moby.txt", "pride.txt", "war.txt"):
            p = os.path.join(LP, "data", f)
            if os.path.exists(p): KEYT.append((f, open(p, encoding="utf-8", errors="ignore").read()))
        for f in ("mabinogion.txt", "self_reliance.txt", "book_of_the_law.txt", "agrippa.txt", "solved_plaintext.txt", "runepoem_oe.txt"):
            p = os.path.join(LP, "data", "keys", f)
            if os.path.exists(p): KEYT.append((f, open(p, encoding="utf-8", errors="ignore").read()))
        TW = {}
        for nm, txt in KEYT:
            tw = [w for w in re.split(r"[^A-Za-z]+", txt) if w]
            if len(tw) >= 100: TW[nm] = ("".join(w[0] for w in tw), len(tw))
        def t5(Sv):
            out = {}; NW = len(Sv)
            for nm, (letters, M_) in TW.items():
                for sch, idx in (("s%M", Sv % M_), ("cumsum%M", np.cumsum(Sv) % M_), ("(s*i)%M", (Sv * np.arange(1, NW + 1)) % M_)):
                    seq = np.array(R_.eng_to_runes("".join(letters[int(j)] for j in idx)), dtype=np.int64)
                    if len(seq) >= 32: out["T5:%s:%s" % (nm, sch)] = seq
            return out
        rd5 = t5(S); rng5 = np.random.default_rng(3301)
        res = eval_family(rd5, lambda j: t5(R_.wsum(shuffled_words(rng5))), 60, fam, part=part)
        nrep = int(np.median([len(v) for v in rd5.values()]))
        finish_direct(part, fam, res, direct_control(res, nrep, fam, D=100), {"n_streams": len(rd5)})


# ================================================================== U6a
def runs_s2():
    raw = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read(); runs = []; cur = 0
    for ch in raw:
        if 0x16A0 <= ord(ch) <= 0x16FF: cur += 1
        elif ch in "-/.": runs.append(cur); cur = 0
    runs.append(cur); return runs


def u6a_stage():
    wait_mem(); n1c, FUNCS = n1_ct_cfgs()
    ks = "N1 CT-feedback keystreams: 3 f x 2 sign x fwd/rev x continuous/per-segment-reset = 24 REGENERATED (no top-N was stored); 10 windows (starts 0,1200,...,10800) at L=120"
    run_beam_family("U6a_N1_ct", n1c, list(range(0, 12000, 1200)), 120, ks, "beam_v3 panel_max keyskip1+keyskip2 L=120", 100)
    run_beam_family("U6a_N4_ks", n4_cfgs(), list(range(0, 12000, 2000)), 120,
                    "N4 digit planes (bases 3,5,7,10, all places) of prime magnitudes as mod-29 keystream, both signs = 28 keystreams; 6 windows at L=120", "beam_v3 panel_max keyskip1+keyskip2 L=120", 100)
    n5 = n5_mod()
    run_beam_family("U6a_N5", n5_cfgs(n5), [0], 120,
                    "N5 totient ladder: 8 generators x 2 sign x 29 offsets = 464 keystreams; continuous windows at 0/4800/9600 + per-segment-restart windows on pages 18 and 36 (5 windows)", "beam_v3 panel_max keyskip1+keyskip2 L=120", 100)
    # ---- direct families
    M0 = U[:]
    # N1 PT-feedback decodes
    fam = "U6a_N1_pt"
    part = Part(fam, "N1 PT-feedback regenerated decodes (24 configs, skip-free: key depends on recovered plaintext, not representable by fixed-K keyskip beam); null = doublet-level-matched shuffled ciphertext (dfshuffle, <=86 adjacent equal pairs like LP2) through the same config", "direct skip-free decode, panel-R36 on the decoded stream", 24)
    if not part.skip:
        streams = n1_pt_streams(U, FUNCS)
        def gen(j):
            sh = dfshuffle(U, random.Random(3301 + j))
            return n1_pt_streams(sh, FUNCS)
        res = eval_family(streams, gen, 150, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, 12956, fam, D=150), {"not_representable_by_keyskip_beam": True})
    # N4 read mode + N2 + S1 + S2
    fam = "U6a_N4_read"
    part = Part(fam, "N4 digit planes read directly as symbol streams (14 planes); null = planes re-derived from a doublet-level-matched shuffled LP2 source (dfshuffle)", "direct panel-R36 pmax", 14)
    if not part.skip:
        pls = {"b%d_p%d" % (b, p): np.array(pl, dtype=np.int64) % N for b, p, pl in planes()}
        rng = np.random.RandomState(5)
        res = eval_family(pls, lambda j: {"b%d_p%d" % (b, p): np.array(pl, dtype=np.int64) % N for b, p, pl in planes(dfshuffle(U, random.Random(8000 + j)))}, 300, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, 12956, fam, D=150), {})
    fam = "U6a_N2"
    part = Part(fam, "N2 prime_gap / prime_index (+cumsum) streams read as data: mod29, base29 2-digit, base29 3-digit (12 streams); null = streams re-derived from a doublet-level-matched shuffled LP2 source (dfshuffle)", "direct panel-R36 pmax", 12)
    if not part.skip:
        base = {"prime_gap": NC.v_prime_gap(U), "prime_index": NC.v_prime_index(U)}
        base["prime_gap_cumsum"] = NC.cumulative(base["prime_gap"]); base["prime_index_cumsum"] = NC.cumulative(base["prime_index"])
        def interp(st):
            d = [v % N for v in st]; out = {"mod29": np.array(d, dtype=np.int64)}
            for nd in (2, 3):
                o = []
                for j in range(0, len(d) - nd + 1, nd):
                    val = 0
                    for k in range(nd): val = val * N + d[j + k]
                    o.append(val % N)
                out["b29_%d" % nd] = np.array(o, dtype=np.int64)
            return out
        def allint(bs): return {"%s:%s" % (n, k): v for n, st in bs.items() for k, v in interp(st).items()}
        streams = allint(base)
        def gen(j):
            src = dfshuffle(U, random.Random(3301 + j)); b2 = {"prime_gap": NC.v_prime_gap(src), "prime_index": NC.v_prime_index(src)}
            b2["prime_gap_cumsum"] = NC.cumulative(b2["prime_gap"]); b2["prime_index_cumsum"] = NC.cumulative(b2["prime_index"])
            return allint(b2)
        res = eval_family(streams, gen, 200, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, 4318, fam, D=150), {"not_covered_routes": "ASCII printable-ratio and coordinate-structure routes are byte/pair tests, not rune streams"})
    fam = "U6a_S1"
    part = Part(fam, "S1 gaps between F occurrences: mod29, base29 2/3-digit, mod n in {2,3,4,5,8} read as rune indices (9 streams); null = count-preserving random position sets", "direct panel-R36 pmax", 9)
    if not part.skip:
        pos = [i for i, v in enumerate(U) if v == 0]; cnt = len(pos); LL = len(U)
        def s1(P):
            g = [P[k + 1] - P[k] for k in range(len(P) - 1)]; d = [x % N for x in g]; out = {"mod29": np.array(d, dtype=np.int64)}
            for nd in (2, 3):
                o = []
                for j in range(0, len(d) - nd + 1, nd):
                    val = 0
                    for k in range(nd): val = val * N + d[j + k]
                    o.append(val % N)
                out["b29_%d" % nd] = np.array(o, dtype=np.int64)
            for n_ in (2, 3, 4, 5, 8): out["mod%d" % n_] = np.array([x % n_ for x in g], dtype=np.int64)
            return {k: v for k, v in out.items() if len(v) >= 32}
        streams = s1(pos)
        res = eval_family(streams, lambda j: s1(sorted(random.Random(3301 + j).sample(range(LL), cnt))), 300, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, len(pos) - 1, fam, D=150), {"n_interrupters": cnt, "not_covered_routes": "ASCII/bit/indicator-bytes routes are text/byte reads"})
    fam = "U6a_S2"
    part = Part(fam, "S2 separator run-lengths (runes between consecutive '-','/','.') mod29 as rune indices (1 stream); null = run list shuffled", "direct panel-R36 pmax", 1)
    if not part.skip:
        runs = runs_s2(); st = {"runs_mod29": np.array([r % N for r in runs], dtype=np.int64)}
        res = eval_family(st, lambda j: {"runs_mod29": np.random.RandomState(j + 9).permutation(st["runs_mod29"])}, 1000, fam, part=part)
        finish_direct(part, fam, res, direct_control(res, len(runs), fam, D=150), {"n_runs": len(runs), "not_covered_routes": "binary/ternary separator-byte routes are byte reads"})


# ================================================================== U6b
def r22_ops(src=None):
    seq = list(U if src is None else src)
    dec = lambda s, ph, st=4: s[ph::st]
    def inter4(s): return [x for r in range(4) for x in s[r::4]]
    def deinter4(s):
        n = len(s); lens = [len(range(r, n, 4)) for r in range(4)]; cols = []; off = 0
        for Ln in lens: cols.append(s[off:off + Ln]); off += Ln
        out = [0] * n
        for r in range(4):
            for j, v in enumerate(cols[r]): out[r + 4 * j] = v
        return out
    atb = lambda s: [(N - 1 - c) % N for c in s]
    sh = lambda s, k: [(c + k) % N for c in s]
    def it(s, op, t):
        for _ in range(t): s = op(s)
        return s
    ops = []
    for ph in range(4):
        sub = dec(seq, ph); ops.append(("X1a_decim_phase%d_raw" % ph, sub))
        for kk in range(N): ops.append(("X1a_decim_phase%d_shift%d" % (ph, kk), sh(sub, kk)))
        ops.append(("X1a_decim_phase%d_atbash" % ph, atb(sub)))
    for n_ in (2, 3, 4):
        ops.append(("X1b_atbash_x%d" % n_, it(seq, atb, n_)))
        for kk in (1, 3, 7): ops.append(("X1b_shift%d_x%d" % (kk, n_), it(seq, lambda s: sh(s, kk), n_)))
    ops.append(("X1c_interleave4", inter4(seq))); ops.append(("X1c_deinterleave4", deinter4(seq)))
    rev = list(reversed(seq)); ops.append(("X3a_reversed_raw", rev))
    for kk in range(N): ops.append(("X3a_reversed_shift%d" % kk, sh(rev, kk)))
    ops.append(("X3a_reversed_atbash", atb(rev)))
    return ops, (dec, inter4, deinter4, atb, sh)


def u6b_stage():
    wait_mem(); ops, (dec, inter4, deinter4, atb, sh) = r22_ops(); assert len(ops) == 169, len(ops)
    fam = "U6b_R22C_structural"
    part = Part(fam, "R22-C structural operations: X1 (138) + X3a (31) = 169 regenerated streams (code copied unchanged from round22/C imperatives.py::sweep_x1/sweep_x3); no key, so keyskip1/2 not applicable; null = ops re-applied to a doublet-level-matched shuffled LP2 source (dfshuffle)", "direct panel-R36 pmax", 169)
    if not part.skip:
        streams = {nm: np.array(s, dtype=np.int64) for nm, s in ops}
        res = eval_family(streams, lambda j: {nm: np.array(s_, dtype=np.int64) for nm, s_ in r22_ops(dfshuffle(U, random.Random(6000 + j)))[0]}, 300, fam, part=part)
        # inverse-op plants through the real ops (X1 decimation / deinterleave / X3a reversal+shift)
        ctl = {}
        for reg in ("EN_MODERN", "LATIN", "GREEK"):
            P = plant_stream(reg, 3239, 11).tolist(); rnd = random.Random(5); carrier = U[:]; rnd.shuffle(carrier)
            c1 = carrier[:]; c1[1::4] = P[:len(c1[1::4])]
            full = plant_stream(reg, 12956, 12).tolist()
            seq3 = list(reversed(sh(full, -7)))
            plants = {"X1a_decim_phase1_raw": dec(c1, 1), "X1c_deinterleave4": deinter4(inter4(full)), "X3a_reversed_shift7": sh(list(reversed(seq3)), 7)}
            e = {}
            for pn, s in plants.items():
                s = np.array(s, dtype=np.int64); obs = pm_many({"p": s})["p"]
                a = np.array([pm_many({"p": np.random.RandomState(j + 1).permutation(s)})["p"] for j in range(60)])
                Zp = (obs - a.mean()) / (a.std(ddof=1) or 1e-9); e[pn] = {"n": len(s), "Z_plant": round(float(Zp), 2), "pass": bool(Zp > res["null_max_Z_q99"] + 1.0)}
            ctl[reg] = e
        ctl["all_pass"] = all(v["pass"] for r in ctl.values() if isinstance(r, dict) for v in r.values() if isinstance(v, dict))
        log(fam, "inverse-op plants", ctl["all_pass"])
        finish_direct(part, fam, res, ctl, {"ops": 169})
    # ---- keyed ops
    KE = _key_english(); Kfull = (KE * (len(U) // len(KE) + 1))[:len(U)]
    cfgs = []
    for sign in (-1, 1): cfgs.append(("X3b_solvedkey_sign%+d" % sign, list(U), Kfull, sign, None))
    for tn, tf in (("v_prime", NC.v_prime), ("v_prime_index", NC.v_prime_index), ("v_totient", NC.v_totient)):
        base_ks = [v % N for v in tf(U)]
        for vn, letters in (("none", list(U)), ("atbash_pre", [(N - 1 - c) % N for c in U])):
            for sign in (-1, 1): cfgs.append(("X4_%s_%s_sign%+d" % (tn, vn, sign), letters, base_ks, sign, None))
    assert len(cfgs) == 14
    starts = [PAGE_START[p] for p in (0, 10, 20, 30, 40, 50)]
    run_beam_family("U6b_R22C_keyed_L120", cfgs, starts, 120, "R22-C keyed ops: X3b solved-key running key (2 signs) + X4 prime-value/index/totient keystream x {none, atbash_pre} x 2 signs (12) = 14 (the 4 X3b rows of R22-C were 2 signs x exact/drift; keyskip1/2 replaces the preset axis); 6 page-start windows; L=120 screen", "beam_v3 panel_max keyskip1+keyskip2 L=120", 100)
    run_beam_family("U6b_R22C_keyed_L240", cfgs, starts, 240, "same 14 keyed ops, 6 page-start windows at page length L=240", "beam_v3 panel_max keyskip1+keyskip2 L=240", 60)


# ================================================================== FINAL
MDS_MIN, IOC_MAX = 0, 99


def degenerate_thresholds():
    """A decode is 'degenerate' (constant / near-constant output, the hallucination pattern) if mds <= p1(mds) of held-out
    real-language 240-slices over all 12 registers minus 1, or IoC*N >= the max seen in them + 1."""
    rng = random.Random(77); mds_l = []; ioc_l = []
    for reg in REGS:
        arr = TEST[reg].astype(np.int64)
        for _ in range(150):
            st = rng.randrange(0, len(arr) - 250); x = arr[st:st + 240]
            mds_l.append(AD.min_distinct(x)); ioc_l.append(AD.ioc_n(x))
    m = int(np.min(mds_l)) - 1; i = float(np.max(ioc_l)) + 1.0
    return m, i, {"rule": "degenerate iff mds <= %d or ioc*N >= %.2f" % (m, i), "real_language_240_slices": {"mds_min": int(np.min(mds_l)), "mds_p1": float(np.percentile(mds_l, 1)), "ioc_max": float(np.max(ioc_l)), "ioc_p99": float(np.percentile(ioc_l, 99))}}

def final_stage():
    ctl_beam = json.load(open(F("control_beam.json"))) if os.path.exists(F("control_beam.json")) else None
    metas = {}
    for fn in sorted(os.listdir(F("parts"))):
        if fn.endswith(".done"): metas[fn[:-5]] = json.load(open(F("parts", fn)))
    # merge rows into one store
    store = F("rescore_rows.jsonl"); n_rows = 0; first = None
    with open(store, "w") as out:
        for fam in sorted(metas):
            with open(F("parts", fam + ".jsonl")) as f:
                h = f.readline()
                if first is None: first = json.loads(h); h0 = dict(first); h0["sweep_id"] = "round37/C3/rescore-all"; h0["universe_units"] = 0; h0["universe_rows"] = 0; out.write(json.dumps(h0) + "\n")
                for line in f:
                    if line.strip(): out.write(line); n_rows += 1
    global MDS_MIN, IOC_MAX
    MDS_MIN, IOC_MAX, dthr = degenerate_thresholds()
    summ = {"degenerate_filter": dthr, "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": P12_SHA, "rows": n_rows, "families": {}, "flagged": [], "near_miss": [], "control_beam": ctl_beam}
    for fam, m in metas.items():
        e = {"kind": m["kind"]}
        if m["kind"] == "beam":
            best_nd = {r: [-1e9, None, None, None, None] for r in RELS}; ndeg = {r: 0 for r in RELS}; nrows = {r: 0 for r in RELS}; topdeg = {r: [-1e9, None] for r in RELS}
            with open(F("parts", fam + ".jsonl")) as f:
                f.readline()
                for line in f:
                    rw = json.loads(line)
                    if rw[0].startswith("null:"): continue
                    rel = rw[0].rsplit(":", 1)[1]; nrows[rel] += 1
                    if rw[9] <= MDS_MIN or rw[8] >= IOC_MAX:
                        ndeg[rel] += 1
                        if rw[3] > topdeg[rel][0]: topdeg[rel] = [rw[3], rw[0], rw[8], rw[9]]
                        continue
                    if rw[3] > best_nd[rel][0]: best_nd[rel] = [rw[3], rw[0], REGS[rw[4]], rw[5], (rw[8], rw[9])]
            e.update({"rows": m["rows"], "best_all": m["best"], "best_nondegenerate": {r: {"pmax": best_nd[r][0], "kid": best_nd[r][1], "preg": best_nd[r][2], "pmax_ne": best_nd[r][3], "ioc_mds": best_nd[r][4]} for r in RELS},
                      "n_degenerate_rows": ndeg, "top_degenerate_row": topdeg, "bars": m["bars"], "family_null": m["family_null"], "argmax_register_hist": m["argmax_register_hist"]})
            e["clears_actualN"] = {r: bool(best_nd[r][0] >= m["bars"][r]["actualN"]) for r in RELS}
            e["clears_declared"] = {r: bool(best_nd[r][0] >= m["bars"][r]["declared_1e6"]) for r in RELS}
            for r in RELS:
                if e["clears_actualN"][r]:
                    ent = {"family": fam, "rel": r, "kid": best_nd[r][1], "pmax": best_nd[r][0], "bar_actualN": m["bars"][r]["actualN"], "bar_declared": m["bars"][r]["declared_1e6"], "FLAGGED_L240_PENDING": True}
                    (summ["flagged"] if e["clears_declared"][r] else summ["near_miss"]).append(ent)
        else:
            e.update({k: m[k] for k in ("n_streams", "D", "best_stream", "best_pmax", "best_Z", "null_max_Z_q99", "exceed", "p_family", "wilson95_exceed_rate", "top5") if k in m})
            if "raw_best" in m: e["raw_best"] = m["raw_best"]
            e["control"] = m["control"]; e["control_pass"] = m["control"]["all_pass"]
            for k in ("original_z694_reading", "original_reading_pmax", "original_reading_Z_vs_family", "original_reading_z_by_register"):
                if k in m: e[k] = m[k]
            e["z_only_p_lt_0.01"] = bool(m["p_family"] < 0.01); e["both_Z_and_raw_p_lt_0.01"] = bool(m["p_family"] < 0.01 and m.get("raw_best", {}).get("p", 1) < 0.01)
            if e["both_Z_and_raw_p_lt_0.01"]: summ["near_miss"].append({"family": fam, "best_stream": m["best_stream"], "Z": m["best_Z"], "p_family": m["p_family"], "route": "direct (needs oracle/other-corroborator; no key to re-test)"})
        summ["families"][fam] = e
    json.dump(summ, open(F("rescore_summary.json"), "w"), indent=1, default=float)
    # validation with the stock validators
    try:
        n = AD.validate_store(store); summ["validate_store"] = "ok: %s" % (n,)
    except Exception as ex:
        summ["validate_store"] = "FAIL: %s" % str(ex)[:300]
    sys.path.insert(0, os.path.join(AN, "handoff")); import validate_ledger as VL
    try: summ["check_r3_store"] = VL.check_r3_store(store)
    except Exception as ex: summ["check_r3_store"] = "ERR: %s" % str(ex)[:300]
    json.dump(summ, open(F("rescore_summary.json"), "w"), indent=1, default=float)
    log("final: rows", n_rows, "validate_store", summ["validate_store"], "check_r3_store", summ["check_r3_store"], "flagged", len(summ["flagged"]), "near", len(summ["near_miss"]))


if __name__ == "__main__":
    {"control": control_stage, "u5": lambda: (u5_l2_stage(), u5_l3_stage()), "u5l2": u5_l2_stage, "u5l3": u5_l3_stage, "u6a": u6a_stage, "u6b": u6b_stage, "final": final_stage}[sys.argv[1]]()
