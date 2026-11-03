"""R43 F3a pass 2 — clean unsolved block (krisyotam p0..p54), null calibration,
multi-seed mechanical simulations, doublet forensics, solved-page interrupter
workload. See measure.py for pass 1.
"""
import collections
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from lp import gematria as gp, ciphers, solve, stats, corpus, score as _score  # noqa
from measure import (parse_pages, words_of, boundary_pairs, diff_ioc,
                     lag_coincidence, doublet_z, load_english_rune_plaintext)

N = gp.N
scorer = _score.default()


def fingerprint(cidx):
    lag2 = sum(1 for i in range(2, len(cidx)) if cidx[i] == cidx[i - 2]) / (len(cidx) - 2)
    return {"ioc": stats.ioc_norm(cidx), "dbl_pct": 100 * stats.doublet_rate(cidx),
            "diffIoC": diff_ioc(cidx, 1, -1), "sumIoC": diff_ioc(cidx, 1, +1),
            "lag2_pct": 100 * lag2}


def mean_sd(vals):
    m = sum(vals) / len(vals)
    v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1) if len(vals) > 1 else 0.0
    return m, math.sqrt(v)


def agg_fps(fps):
    out = {}
    for k in fps[0]:
        m, s = mean_sd([f[k] for f in fps])
        out[k] = f"{m:.3f}±{s:.3f}"
    return out


# ------------------------------------------------------------------ sims
def sim_stream(plain, kind, seed):
    rnd = random.Random(seed)
    n = len(plain)
    pad = [rnd.randrange(N) for _ in range(2 * n + 10)]
    c, prev, j = [], None, 0
    if kind == "pad":
        return [(p + pad[i]) % N for i, p in enumerate(plain)]
    if kind == "redraw+1":
        for p in plain:
            o = (p + pad[j]) % N
            j += 1
            while o == prev:
                o = (o + 1) % N
            c.append(o)
            prev = o
        return c
    if kind == "redraw-rand":
        for p in plain:
            o = (p + pad[j]) % N
            j += 1
            while o == prev:
                o = rnd.randrange(N)
            c.append(o)
            prev = o
        return c
    if kind == "skip-key":
        for p in plain:
            o = (p + pad[j]) % N
            while o == prev:
                j += 1
                o = (p + pad[j]) % N
            c.append(o)
            prev = o
            j += 1
        return c
    if kind == "skip-key-miss20":
        for p in plain:
            o = (p + pad[j]) % N
            if o == prev and rnd.random() < 0.80:
                while o == prev:
                    j += 1
                    o = (p + pad[j]) % N
            c.append(o)
            prev = o
            j += 1
        return c
    if kind == "two-stream":
        pad2 = [rnd.randrange(N) for _ in range(n)]
        for i, p in enumerate(plain):
            o1, o2 = (p + pad[i]) % N, (p + pad2[i]) % N
            o = o1 if o1 != prev else o2
            c.append(o)
            prev = o
        return c
    if kind == "ct-autokey+":
        prev = 0
        for p in plain:
            o = (p + prev) % N
            c.append(o)
            prev = o
        return c
    if kind == "pt-autokey+":
        prev = 0
        for p in plain:
            c.append((p + prev) % N)
            prev = p
        return c
    if kind == "wheel-walk":  # c_i = c_{i-1} + step, step=(p+k) forced nonzero
        prev = 0
        for p in plain:
            s = (p + pad[j]) % N
            while s == 0:
                j += 1
                s = (p + pad[j]) % N
            j += 1
            prev = (prev + s) % N
            c.append(prev)
        return c
    if kind == "vig13-skip":
        key = gp.keyword_to_indices("FIRFUMFERENFE")
        for p in plain:
            o = (p + key[j % 13]) % N
            while o == prev:
                j += 1
                o = (p + key[j % 13]) % N
            c.append(o)
            prev = o
            j += 1
        return c
    raise ValueError(kind)


def main():
    pages = parse_pages()
    # clean unsolved block = p0..p54 (p55 = AN END phi(prime), p56 = plain parable)
    unsolved = list(range(55))
    U_raw = "\n%\n".join(pages[i]["raw"] for i in unsolved)
    U = [i for p in unsolved for i in pages[p]["idxs"]]
    n = len(U)
    print(f"clean unsolved block p0..p54: n={n}")
    fpU = fingerprint(U)
    print("measured:", {k: round(v, 4) for k, v in fpU.items()})
    obs, exp, z = doublet_z(U)
    print(f"doublets obs={obs} exp={exp:.1f} z={z:+.1f}  rate={100*obs/(n-1):.3f}% "
          f"= {obs/exp:.3f} of expectation")

    # ---------------- null calibration (uniform iid, same n)
    rnd = random.Random(1)
    nulls = []
    for t in range(200):
        s = [rnd.randrange(N) for _ in range(n)]
        nulls.append(fingerprint(s))
    print("\nuniform-null calibration (200 sims, n=%d):" % n)
    print(agg_fps(nulls))
    # z of measured diffIoC against null
    m, s = mean_sd([f["diffIoC"] for f in nulls])
    print(f"measured diffIoC={fpU['diffIoC']:.4f}  null={m:.4f}±{s:.4f} "
          f"z={(fpU['diffIoC']-m)/s:+.1f}")
    m, s = mean_sd([f["ioc"] for f in nulls])
    print(f"measured ioc={fpU['ioc']:.4f}  null={m:.4f}±{s:.4f} z={(fpU['ioc']-m)/s:+.1f}")
    m, s = mean_sd([f["lag2_pct"] for f in nulls])
    print(f"measured lag2={fpU['lag2_pct']:.3f}%  null={m:.3f}±{s:.3f} "
          f"z={(fpU['lag2_pct']-m)/s:+.1f}")

    # analytic diffIoC for flat-with-suppressed-zero
    p0 = obs / (n - 1)
    pred = N * (p0 ** 2 + (1 - p0) ** 2 / (N - 1))
    print(f"analytic diffIoC if diffs flat except suppressed 0-cell: {pred:.4f} "
          f"(measured {fpU['diffIoC']:.4f})")

    # ---------------- multi-seed sims
    words = load_english_rune_plaintext()
    plain = [i for w in words for i in w]
    kinds = ["pad", "redraw+1", "redraw-rand", "skip-key", "skip-key-miss20",
             "two-stream", "ct-autokey+", "pt-autokey+", "wheel-walk", "vig13-skip"]
    print(f"\nmechanical sims (english-rune plaintext n={len(plain)}, 12 seeds):")
    simfps = {}
    for kind in kinds:
        fps = [fingerprint(sim_stream(plain, kind, seed)) for seed in range(12)]
        simfps[kind] = agg_fps(fps)
        print(f"{kind:18s} {simfps[kind]}")
    print(f"{'MEASURED':18s} " + str({k: f"{v:.3f}" for k, v in fpU.items()}))

    # ---------------- doublet forensics
    print("\n== doublet forensics (clean block) ==")
    # per-page counts -> dispersion
    counts, lens = [], []
    for i in unsolved:
        idxs = pages[i]["idxs"]
        counts.append(stats.doublet_count(idxs))
        lens.append(len(idxs) - 1)
    mean_c = sum(counts) / len(counts)
    var_c = sum((c - mean_c) ** 2 for c in counts) / (len(counts) - 1)
    print(f"per-page doublets: mean={mean_c:.2f} var={var_c:.2f} "
          f"dispersion={var_c/mean_c:.2f} (Poisson=1)")
    # Monte-Carlo dispersion null: scatter 'obs' doublets over pages ~ len
    tot = sum(counts)
    disp_null = []
    rnd = random.Random(2)
    wts = [l / sum(lens) for l in lens]
    import itertools
    cum = list(itertools.accumulate(wts))
    for t in range(500):
        cc = [0] * len(lens)
        for _ in range(tot):
            r = rnd.random()
            for k, cv in enumerate(cum):
                if r <= cv:
                    cc[k] += 1
                    break
        mc = sum(cc) / len(cc)
        vc = sum((x - mc) ** 2 for x in cc) / (len(cc) - 1)
        disp_null.append(vc / mc)
    m, s = mean_sd(disp_null)
    print(f"dispersion null={m:.2f}±{s:.2f}  z={(var_c/mean_c - m)/s:+.1f}")
    # trend with page index (fatigue)
    rates = [c / l for c, l in zip(counts, lens)]
    # spearman by hand
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = rank(list(range(len(rates)))), rank(rates)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    print(f"spearman(page index, doublet rate) = {cov/(sx*sy):+.3f}")
    print("per-page doublet rates %:", [round(100 * r, 2) for r in rates])

    # doublet VALUES
    dvals = collections.Counter(U[i] for i in range(1, n) if U[i] == U[i - 1])
    print("doublet values:", {gp.IDX_TO_TRANS[k]: v for k, v in dvals.most_common()})
    print(f"F-F doublets: {dvals.get(0,0)} (uniform exp {obs/N:.1f})")
    # triples
    tr = sum(1 for i in range(2, n) if U[i] == U[i - 1] == U[i - 2])
    print(f"triples: {tr}")
    # parity of doublet positions within their word (digraph-cipher test)
    par = collections.Counter()
    W = []
    for i in unsolved:
        W += words_of(pages[i]["raw"])
    for w in W:
        for k in range(1, len(w)):
            if w[k] == w[k - 1]:
                par[k % 2] += 1
    print(f"doublet second-glyph parity in word (odd=pair-internal): {dict(par)}")

    # ---------------- longer-range structure
    lc = lag_coincidence(U, 300)
    hot = sorted(lc.items(), key=lambda kv: -kv[1])[:8]
    print("\nlag-coincidence 1..300 top:", [(L, round(100 * v, 2)) for L, v in hot])
    mlag, slag = mean_sd(list(lc.values()))
    print(f"lag spectrum mean={100*mlag:.3f}% sd={100*slag:.3f}% "
          f"(binomial sd ~{100*math.sqrt(0.0345*0.9655/n):.3f}%)")

    # per-page homogeneity of unigram distribution
    gtot = collections.Counter(U)
    chi, df = 0.0, 0
    for i in unsolved:
        idxs = pages[i]["idxs"]
        if len(idxs) < 50:
            continue
        for v in range(N):
            e = gtot[v] * len(idxs) / n
            o = idxs.count(v)
            chi += (o - e) ** 2 / e
            df += 1
        df -= 1
    print(f"page-homogeneity chi2={chi:.0f} df~{df} (flat if ~df)")

    # English word-length reference
    wlU = [len(w) for w in W]
    wlE = [len(w) for w in words]
    print(f"\nword lengths: unsolved mean={sum(wlU)/len(wlU):.2f} "
          f"english-rune mean={sum(wlE)/len(wlE):.2f}")
    hU = collections.Counter(wlU)
    hE = collections.Counter(wlE)
    totU, totE = sum(hU.values()), sum(hE.values())
    print("len:  " + "  ".join(f"{L}" for L in range(1, 13)))
    print("uns%: " + " ".join(f"{100*hU.get(L,0)/totU:4.1f}" for L in range(1, 13)))
    print("eng%: " + " ".join(f"{100*hE.get(L,0)/totE:4.1f}" for L in range(1, 13)))

    # ---------------- solved-page interrupter workload (scream314 corpus)
    print("\n== solved-page interrupter workload ==")
    jobs = [("03.jpg", "vig", "DIVINITY"),
            ("14.jpg", "vig", "FIRFUMFERENFE"),
            ("73.jpg", "totient", None)]
    for label, kind, key in jobs:
        page = corpus.page_by_label(label)
        runes = page["runes"]
        idxs = gp.runes_to_indices(runes)
        nF = idxs.count(0)
        nr = len(idxs)
        if kind == "vig":
            stream = ciphers.repeat_key(gp.keyword_to_indices(key), nr)
        else:
            primes, p = [], 2
            while len(primes) < nr:
                if all(p % q for q in primes if q * q <= p):
                    primes.append(p)
                p += 1
            stream = [(q - 1) % N for q in primes]
        res = solve.find_interrupters(runes, stream, sign=-1, beam_width=500,
                                      scorer=scorer)
        print(f"{label}: n={nr} F-runes={nF} ({100*nF/nr:.1f}%) nulls={res['n_interrupters']} "
              f"({100*res['n_interrupters']/max(nF,1):.0f}% of F) score={res['score_norm']:.2f}")
        print(f"   null positions in rune stream: {res['interrupters']}")

    # persist
    with open(os.path.join(HERE, "measurements2.json"), "w") as f:
        json.dump({"n": n, "measured": fpU, "doublets": [obs, exp, z],
                   "null": agg_fps(nulls), "sims": simfps,
                   "dispersion": [var_c / mean_c, m, s]}, f, indent=1, default=str)
    print("\nwrote measurements2.json")


if __name__ == "__main__":
    main()
