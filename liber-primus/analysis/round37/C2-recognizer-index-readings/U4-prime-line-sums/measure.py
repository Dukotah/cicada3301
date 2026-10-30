import sys, os, re, json, math, time
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "tests"))
from lp import corpus, ciphers, solve, gematria as gp, score as _score
import validate as V
NS = 10000
rng = np.random.default_rng(3301037)
PR = np.array(gp.PRIMES)
N = 29
LIM = 109 * 800
sv = np.ones(LIM + 1, bool); sv[:2] = False
for i in range(2, int(LIM ** .5) + 1):
    if sv[i]:
        sv[i*i::i] = False
RUNE_RE = re.compile(r"[ᚠ-᛿]")
sp = {p["page_label"]: p for p in json.load(open(os.path.join(ROOT, "SOLVED-PAGES.json"), encoding="utf-8"))["pages"]}
scorer = _score.default()


def lines_of(label):
    p = corpus.page_by_label(label)
    L = [[gp.RUNE_TO_IDX[c] for c in RUNE_RE.findall(x) if c in gp.RUNE_TO_IDX] for x in p["runes"].split("\n")]
    return [l for l in L if l]


def tr(idx):
    return gp.indices_to_translit(idx)


def decode_pos(flat, mode, key=None):
    n = len(flat)
    if mode == "simple":
        best = None
        for atb in (False, True):
            base = ciphers.atbash_indices(flat) if atb else flat
            for k in range(N):
                for s in (-1, 1):
                    out = [(c + s * k) % N for c in base]
                    sc = scorer.score_norm(tr(out))
                    if best is None or sc > best[0]:
                        best = (sc, out)
        return best[1]
    runes = "".join(gp.IDX_TO_RUNE[i] for i in flat)
    stream = ciphers.repeat_key(gp.keyword_to_indices(key), n) if mode == "vig" else V.phi_prime(n)
    res = solve.find_interrupters(runes, stream, sign=-1, beam_width=500, scorer=scorer)
    iset = set(res["interrupters"]); out = []; j = 0; f = 0
    for c in flat:
        if c == 0:
            if f in iset:
                out.append(-1); f += 1; continue
            f += 1
        out.append((c - stream[j]) % N); j += 1
    return out


PAGES = [("Runes - 01.jpg", "simple", None), ("05.jpg", "simple", None), ("06.jpg", "simple", None),
         ("03.jpg", "vig", "DIVINITY"), ("14.jpg", "vig", "FIRFUMFERENFE"), ("73.jpg", "tot", None)]


def val(idx):
    return np.array([PR[i] if i >= 0 else 0 for i in idx])


def bnd(lens):
    return np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(int)


def nulls(vals_flat, lens, kind):
    b = bnd(lens); res = np.empty(NS); B = 500
    for a in range(0, NS, B):
        m = min(B, NS - a)
        if kind == "shuffle":
            perm = np.argsort(rng.random((m, len(vals_flat))), axis=1)
            M = vals_flat[perm]
        else:
            M = PR[rng.integers(0, N, (m, len(vals_flat)))]
        res[a:a + m] = sv[np.add.reduceat(M, b, axis=1)].sum(1)
    return res


def analyse(pages):
    out = {}; pool = {"shuffle": 0, "random": 0}; tot_obs = 0; tot_l = 0
    for name, (vals, lens) in pages.items():
        b = bnd(lens)
        s = np.add.reduceat(vals, b); ps = sv[s]; k = int(ps.sum()); nl = len(lens)
        r = {"lines": nl, "passing": k, "fraction": k / nl, "all_prime": bool(k == nl),
             "line_sums": s.tolist(), "line_pass": ps.astype(int).tolist(), "line_lengths": list(map(int, lens))}
        for kind in ("shuffle", "random"):
            nu = nulls(vals, lens, kind)
            pool[kind] = pool[kind] + nu
            r[kind + "_null_mean_frac"] = float(nu.mean() / nl)
            r["p_" + kind] = float((1 + (nu >= k).sum()) / (NS + 1))
        out[name] = r; tot_obs += k; tot_l += nl
    pooled = {"lines": tot_l, "passing": tot_obs, "fraction": tot_obs / tot_l}
    for kind in ("shuffle", "random"):
        pooled[kind + "_null_mean_frac"] = float(pool[kind].mean() / tot_l)
        pooled["p_" + kind] = float((1 + (pool[kind] >= tot_obs).sum()) / (NS + 1))
    return out, pooled


def verdict(per, pooled):
    n5 = sum(1 for r in per.values() if r["p_shuffle"] < 0.05)
    sep = pooled["p_shuffle"] < 0.01 and n5 >= 4
    return {"pages_p_lt_0.05": n5, "pooled_p_shuffle": pooled["p_shuffle"], "separation": bool(sep)}


def construct_prime_lines(lens):
    flat = []
    for L in lens:
        while True:
            r = rng.integers(0, N, L)
            for _ in range(2000):
                if sv[int(PR[r].sum())]:
                    break
                r[rng.integers(0, L)] = rng.integers(0, N)
            if sv[int(PR[r].sum())]:
                break
        flat.extend(r.tolist())
    return PR[np.array(flat)]


t0 = time.time()
data = {}
for label, mode, key in PAGES:
    L = lines_of(label)
    flat = [c for l in L for c in l]
    lens = [len(l) for l in L]
    pt = decode_pos(flat, mode, key)
    txt = tr([i for i in pt if i >= 0])
    if label in sp:
        want = sp[label]["plaintext_transliteration"]
        ok = V.canon(txt)[:80] == V.canon(want)[:80]
    else:
        ok = all(w in V.canon(txt) for w in ["ANEND", "DEEPWEB", "HASHESTO", "DUTY", "EUERYPILGRIM", "SEECOUT", "THISPAGE"])
    pl, i = [], 0
    for L_ in lens:
        pl.append(sum(1 for x in pt[i:i + L_] if x >= 0)); i += L_
    data[label] = {"cipher": val(flat), "plain": val(pt), "lens": lens, "plens": pl, "decode_ok": bool(ok),
                   "n_interrupters": sum(1 for x in pt if x < 0), "n": len(flat)}
    print(label, "decode_ok", ok, "lines", len(lens), "intr", data[label]["n_interrupters"], flush=True)

ctrl_pages = {label: (construct_prime_lines(d["lens"]), d["lens"]) for label, d in data.items()}
cper, cpool = analyse(ctrl_pages)
control = {"per_page": {k: {kk: v[kk] for kk in ("lines", "passing", "fraction", "p_shuffle", "p_random")} for k, v in cper.items()},
           "pooled": cpool,
           "pass": bool(all(v["fraction"] == 1.0 for v in cper.values()) and cpool["p_shuffle"] < 1e-4
                        and cper["06.jpg"]["p_shuffle"] < 1e-4 and cper["Runes - 01.jpg"]["p_shuffle"] < 1e-4)}
print("control", control["pass"], cpool, flush=True)

pt_pages = {k: (d["plain"], d["plens"]) for k, d in data.items()}
ct_pages = {k: (d["cipher"], d["lens"]) for k, d in data.items()}
pt_per, pt_pool = analyse(pt_pages)
ct_per, ct_pool = analyse(ct_pages)
pt_v, ct_v = verdict(pt_per, pt_pool), verdict(ct_per, ct_pool)
print("PLAIN", pt_pool, pt_v, flush=True); print("CIPHER", ct_pool, ct_v, flush=True)
for k in pt_per:
    print(k, "PT", pt_per[k]["passing"], "/", pt_per[k]["lines"], pt_per[k]["p_shuffle"], "CT", ct_per[k]["passing"], ct_per[k]["p_shuffle"])

_, loo_pt = analyse({k: v for k, v in pt_pages.items() if k != "Runes - 01.jpg"})
print("LOO plaintext excluding 01:", loo_pt)
sec = {}
for lab in ("Runes - 01.jpg", "05.jpg", "03.jpg"):
    d = data[lab]
    s = np.add.reduceat(d["plain"], bnd(d["plens"]))
    sec[lab] = {"line_sums": s.tolist(), "pass": sv[s].astype(int).tolist(), "excluding_first_line": "%d/%d" % (int(sv[s][1:].sum()), len(s) - 1)}

allsums = np.concatenate([np.add.reduceat(d["plain"], bnd(d["plens"])) for d in data.values()])
alllens = np.concatenate([d["plens"] for d in data.values()])
meanS = float(allsums.mean())
conf = {"line_length_min": int(alllens.min()), "line_length_median": float(np.median(alllens)), "line_length_max": int(alllens.max()),
        "line_length_mean": float(alllens.mean()), "line_sum_mean": meanS, "line_sum_min": int(allsums.min()), "line_sum_max": int(allsums.max()),
        "base_rate_1_over_ln_meanS": 1 / math.log(meanS), "base_rate_2_over_ln_meanS": 2 / math.log(meanS),
        "primes_among_all_integers_in_sum_range": float(sv[allsums.min():allsums.max() + 1].mean()),
        "observed_pooled_plaintext_fraction": pt_pool["fraction"], "pooled_shuffle_null_mean": pt_pool["shuffle_null_mean_frac"],
        "pooled_random_null_mean": pt_pool["random_null_mean_frac"]}
kj = open(os.path.join(ROOT, "data", "kjv.txt"), encoding="utf-8", errors="ignore").read().upper()
kj = re.sub(r"[^A-Z]", "", kj)[:600000]
dig = ["TH", "EO", "NG", "OE", "AE", "IA", "EA"]
TRs = gp.TRANSLIT
er = []; i = 0
while i < len(kj):
    if kj[i:i + 2] in dig:
        er.append(TRs.index(kj[i:i + 2])); i += 2
    else:
        c = {"K": "C", "V": "U", "Z": "S", "Q": "C"}.get(kj[i], kj[i])
        if c in TRs:
            er.append(TRs.index(c))
        i += 1
ev = PR[np.array(er)]
cs = np.concatenate([[0], np.cumsum(ev)])
starts = rng.integers(0, len(ev) - 200, 20000)
Lr = rng.choice(alllens, 20000)
es = cs[starts + Lr] - cs[starts]
conf["english_kjv_window_prime_rate_same_lengths"] = float(sv[es].mean())

res = {"date": "2026-10-30", "ns": NS, "decode_ok": {k: d["decode_ok"] for k, d in data.items()},
       "n_interrupters": {k: d["n_interrupters"] for k, d in data.items()},
       "positive_control": control, "plaintext": {"per_page": pt_per, "pooled": pt_pool, "verdict": pt_v},
       "ciphertext": {"per_page": ct_per, "pooled": ct_pool, "verdict": ct_v},
       "secondary_title_excluded": sec, "plaintext_pooled_excluding_A_WARNING": loo_pt, "confound": conf, "separation": pt_v["separation"], "seconds": time.time() - t0}
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"), indent=1)
print(json.dumps(conf, indent=1)); print(sec)
