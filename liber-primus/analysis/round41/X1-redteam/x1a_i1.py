"""X1-A I1 audit: independent refit, real-store exceedance counts, row recompute, control check. python x1a_i1.py"""
import json, math, os, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
I1 = os.path.join(AN, "round41", "I1-null-refit")
A = -math.log1p(-0.01)
RELS = ("keyskip1", "keyskip2")
out = {}
# null stream, own dedup (first occurrence of (fam, seed))
seen = set(); null = {r: [] for r in RELS}; fam_of = []
for l in open(os.path.join(I1, "null_stream.jsonl")):
    r = json.loads(l); k = (r["fam"], r["seed"])
    if k in seen: continue
    seen.add(k)
    for rel in RELS: null[rel].append(r[rel][0])
out["n_null_distinct"] = len(seen)
# real rows
def real(path):
    d = {r: [] for r in RELS}
    with open(path) as f:
        f.readline()
        for l in f:
            r = json.loads(l)
            if r[1] != 120: continue
            k = r[0]; rel = k.rsplit("|", 1)[1] if "|" in k else k.rsplit(":", 1)[1]
            if rel in d: d[rel].append(r[3])
    return d
R37 = real(os.path.join(AN, "round37", "I2-pfv4-12reg", "sweep_rows.jsonl"))
R40 = real(os.path.join(AN, "round40", "B1-bash-versions", "sweep_rows.jsonl"))
pool = {r: list(R37[r]) + list(R40[r]) for r in RELS}
for g in ("B04", "KDF", "R17PAD", "COSPAD"):
    d = real(os.path.join(AN, "round40", "B3-english-era-grids", "rows_%s.jsonl" % g))
    for r in RELS: pool[r] += d[r]
def pot(v, q=0.90):
    v = np.sort(np.asarray(v, float)); u = np.quantile(v, q); ex = v[v > u] - u
    beta = ex.mean(); p = len(ex) / len(v)  # exponential MLE
    mu = u + beta * math.log(p)
    return u, p, beta, mu
def bar(par, N): return par[3] + par[2] * math.log(N / A)
def ks(a, b):
    a = np.sort(a); b = np.sort(b); x = np.concatenate([a, b])
    return float(np.abs(np.searchsorted(a, x, "right") / len(a) - np.searchsorted(b, x, "right") / len(b)).max())
rng = np.random.default_rng(4141)
res = {}
for rel in RELS:
    nv = np.array(null[rel]); rv = np.array(R37[rel]); pv = np.array(pool[rel])
    pn = pot(nv); pp = pot(pv)
    d = ks(nv, rv); n = len(nv) * len(rv) / (len(nv) + len(rv)); lam = (math.sqrt(n) + .12 + .11 / math.sqrt(n)) * d
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 100))
    # bootstrap SE of null bar
    bs = {N: [] for N in (131786, 1e6)}
    for _ in range(100):
        q = pot(nv[rng.integers(0, len(nv), len(nv))])
        for N in bs: bs[N].append(bar(q, N))
    # exceedance counts of pooled real rows vs null-fit and vs null empirical
    ex = {}
    for x in (4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0):
        obs = int((pv > x).sum())
        pe_fit = (pn[1] * math.exp(-(x - pn[0]) / pn[2])) if x > pn[0] else float((nv > x).mean())
        ex[str(x)] = {"obs": obs, "n": len(pv), "fit_expected": round(pe_fit * len(pv), 1), "null_emp_expected": round(float((nv > x).mean()) * len(pv), 1), "null_count": int((nv > x).sum())}
    res[rel] = {"null_pot": [float(t) for t in pn], "pool_pot": [float(t) for t in pp],
                "median_null": float(np.median(nv)), "median_R37": float(np.median(rv)), "q99_null": float(np.quantile(nv, .99)), "q99_R37": float(np.quantile(rv, .99)),
                "ks_D_null_vs_R37": d, "ks_p": float(min(max(p, 0), 1)),
                "bar131786_null": bar(pn, 131786), "bar1e6_null": bar(pn, 1e6), "bar131786_pool": bar(pp, 131786), "bar1e6_pool": bar(pp, 1e6),
                "boot_se_131786": float(np.std(bs[131786], ddof=1)), "boot_se_1e6": float(np.std(bs[1e6], ddof=1)),
                "exceed_pool_vs_fit": ex}
    # GPD (PWM/moments) bar on pooled real for N=131786, 1e6 and observed max
    v = np.sort(pv); u = np.quantile(v, .9); e = v[v > u] - u; m1 = e.mean(); m2 = (e ** 2).mean()
    xi = 0.5 * (1 - m1 ** 2 / (m2 - m1 ** 2)) if False else 0.5 * (1 - m1 * m1 / (m2 - m1 * m1))
    sig = m1 * (1 - xi); pu = len(e) / len(v)
    def gb(N):
        # level so that N*pu*(1+xi z/sig)^(-1/xi) = A
        return u + sig / xi * ((N * pu / A) ** xi - 1)
    res[rel]["gpd_pool"] = {"xi": xi, "sigma": sig, "bar131786": gb(131786), "bar1e6": gb(1e6), "max_pool": float(pv.max())}
out["res"] = res
json.dump(out, open(os.path.join(HERE, "x1a_i1_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
