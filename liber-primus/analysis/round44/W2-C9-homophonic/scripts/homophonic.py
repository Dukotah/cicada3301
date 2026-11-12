"""W2-C9 — the D-03 homophonic-downward screen. Glue per PREREG.md (frozen first).

Modes:
    python3 homophonic.py plant     -> results/plants.json      (PC1/PC2/PC3 gate)
    python3 homophonic.py screen    -> results/screen.json + results/rows.jsonl
    python3 homophonic.py check     -> instrument sanity prints (no verdict output)

Statistic T = mean log2-gain per TEST bigram of the TRAIN-fitted class-bigram model over
the TRAIN-fitted class-unigram model (add-0.5), bigrams within pages, pages 0-54 split
even=TRAIN / odd=TEST. Anneal: SA over surjective 29->k maps, 2 restarts x 2500 proposals,
geometric T 0.3->0.001 (on the bits/bigram objective), best-seen state kept.
Null family A: 1000 whole-stream shuffles. Family B: 1000 doublet-matched filtered-uniform
streams. Crosser iff T_real > 999th order statistic of BOTH families at that cell.
"""
import json
import math
import os
import random
import sys
import zlib
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "src"))

import lib_numchannel as nc           # noqa: E402
from lp import gematria as gp         # noqa: E402

N = 29
KS = list(range(5, 27))               # k = 5..26 (22 annealed cells)
RESTARTS = 2
PROPOSALS = 2500
T0, T1 = 0.3, 0.001
NULL_DRAWS = 1000
SEED_A, SEED_B = 1000, 5000
RESULTS = os.path.join(HERE, "..", "results")

TRANSLIT = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P",
            "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y",
            "IA", "EA"]
VOWELS = {"U", "O", "I", "EO", "E", "A", "AE", "Y", "IA", "EA", "OE"}
# confusable-glyph families, analysis/independent-read/FINDINGS.md
CONFUSABLE = [("O", "A", "AE"), ("R", "W"), ("M", "D"), ("N", "I"), ("B", "E")]


# ------------------------------------------------------------------ data
def real_pages():
    pages = nc.segments()[:-2]        # 55 unsolved pages, rune indices
    assert len(pages) == 55
    stream = [i for p in pages for i in p]
    assert len(stream) == 12956, len(stream)
    return [np.array(p, dtype=np.int64) for p in pages]


def split_counts(pages):
    """(Mtrain, Mtest, Utrain, test_pages) — bigrams within pages, even idx=TRAIN."""
    Mtr = np.zeros((N, N)); Mte = np.zeros((N, N)); Utr = np.zeros(N)
    test_pages = []
    for i, p in enumerate(pages):
        M = Mtr if i % 2 == 0 else Mte
        np.add.at(M, (p[:-1], p[1:]), 1.0)
        if i % 2 == 0:
            np.add.at(Utr, p, 1.0)
        else:
            test_pages.append(p)
    return Mtr, Mte, Utr, test_pages


def doublet_rate(pages):
    d = sum(int((p[:-1] == p[1:]).sum()) for p in pages)
    n = sum(len(p) - 1 for p in pages)
    return d / n


# ------------------------------------------------------------------ objective / statistic
def xlogx(a):
    return float(np.where(a > 0, a * np.log(np.maximum(a, 1e-300)), 0.0).sum())


def agg(M, A, k):
    """class-aggregated matrix  B[c,d] = sum_{A[s]=c,A[t]=d} M[s,t]."""
    S = np.zeros((k, N))
    S[A, np.arange(N)] = 1.0
    return S @ M @ S.T


def mi_bits(B):
    tot = B.sum()
    if tot <= 0:
        return 0.0
    return (xlogx(B) - xlogx(B.sum(1)) - xlogx(B.sum(0)) + tot * math.log(tot)) / (tot * math.log(2))


def t_stat(A, k, Mtr, Mte, Utr):
    """cross-validated bits/bigram gain on TEST under TRAIN-fitted class models."""
    Btr, Bte = agg(Mtr, A, k), agg(Mte, A, k)
    Uc = np.bincount(A, weights=Utr, minlength=k)
    Pc = (Btr + 0.5) / (Btr.sum(1, keepdims=True) + 0.5 * k)      # P(c2|c1) train
    Pu = (Uc + 0.5) / (Uc.sum() + 0.5 * k)                        # P(c2) train
    G = np.log2(Pc) - np.log2(Pu)[None, :]
    return float((Bte * G).sum() / max(Bte.sum(), 1.0))


def anneal(Mtr, k, seed):
    """SA over surjective maps; returns best-seen assignment by train MI."""
    rng = random.Random(seed)
    A = np.array(list(range(k)) + [rng.randrange(k) for _ in range(N - k)], dtype=np.int64)
    rng.shuffle(A)
    sizes = np.bincount(A, minlength=k)
    B = agg(Mtr, A, k)
    obj = mi_bits(B)
    bestA, bestobj = A.copy(), obj
    ratio = (T1 / T0) ** (1.0 / max(PROPOSALS - 1, 1))
    temp = T0
    for _ in range(PROPOSALS):
        r = rng.randrange(N)
        a = A[r]
        if sizes[a] == 1:
            temp *= ratio
            continue
        b = rng.randrange(k - 1)
        if b >= a:
            b += 1
        w_out = np.bincount(A, weights=Mtr[r], minlength=k)
        w_in = np.bincount(A, weights=Mtr[:, r], minlength=k)
        m_rr = Mtr[r, r]
        w_out[a] -= m_rr
        w_in[a] -= m_rr
        B[a, :] -= w_out; B[b, :] += w_out
        B[:, a] -= w_in;  B[:, b] += w_in
        B[a, a] -= m_rr;  B[b, b] += m_rr
        new = mi_bits(B)
        if new >= obj or rng.random() < math.exp((new - obj) / max(temp, 1e-12)):
            A[r] = b
            sizes[a] -= 1
            sizes[b] += 1
            obj = new
            if obj > bestobj:
                bestobj, bestA = obj, A.copy()
        else:                                            # undo
            B[a, a] += m_rr;  B[b, b] -= m_rr
            B[:, a] += w_in;  B[:, b] -= w_in
            B[a, :] += w_out; B[b, :] -= w_out
        temp *= ratio
    return bestA, bestobj


def best_anneal(Mtr, k, seed0):
    best = None
    for r in range(RESTARTS):
        A, obj = anneal(Mtr, k, seed0 + 7919 * r)
        if best is None or obj > best[1]:
            best = (A, obj)
    return best


# ------------------------------------------------------------------ natural partitions
def natural_partitions():
    out = []
    out.append(("aett", np.minimum(np.arange(N) // 8, 3)))
    out.append(("vowel_consonant",
                np.array([1 if TRANSLIT[i] in VOWELS else 0 for i in range(N)])))
    for k in range(2, 14):
        out.append((f"idx_mod_{k}", np.arange(N) % k))
    primes = np.array(gp.PRIMES)
    for m in range(2, 14):
        out.append((f"prime_mod_{m}", primes % m))
    conf = np.arange(N)
    for fam in CONFUSABLE:
        ids = [TRANSLIT.index(t) for t in fam]
        for i in ids[1:]:
            conf[i] = ids[0]
    out.append(("confusable_merge", conf))
    normed = []
    for name, A in out:
        _, A2 = np.unique(A, return_inverse=True)
        normed.append((name, A2.astype(np.int64), int(A2.max()) + 1))
    return normed


# ------------------------------------------------------------------ null stream generators
def shuffle_pages(pages, seed):
    rng = np.random.RandomState(seed)
    stream = np.concatenate(pages)
    rng.shuffle(stream)
    return recut(stream, pages)


def filtered_uniform(pages, s, seed):
    rng = random.Random(seed)
    n = sum(len(p) for p in pages)
    out = np.empty(n, dtype=np.int64)
    prev = -1
    for i in range(n):
        x = rng.randrange(N)
        if x == prev and rng.random() >= s:
            while x == prev:
                x = rng.randrange(N)
        out[i] = x
        prev = x
    return recut(out, pages)


def recut(stream, pages):
    cut, pos = [], 0
    for p in pages:
        cut.append(stream[pos:pos + len(p)])
        pos += len(p)
    return cut


# ------------------------------------------------------------------ R3 stats on the test class stream
def r3_stats(A, k, test_pages):
    seq = np.concatenate([A[p] for p in test_pages])
    cnt = np.bincount(seq, minlength=k).astype(float)
    n = len(seq)
    ioc_k = float((cnt * (cnt - 1)).sum() / (n * (n - 1)) * k)
    w = 32
    mds = min(len(set(seq[i:i + w].tolist())) for i in range(0, n - w + 1, 16))
    raw = bytes(int(c) for c in seq)
    zl = len(zlib.compress(raw, 9)) / len(raw)
    return {"ioc_k": round(ioc_k, 4), "mds32": int(mds), "zlib": round(zl, 4)}


def ari(a, b):
    """adjusted Rand index between two labelings."""
    a = np.asarray(a); b = np.asarray(b)
    ct = np.zeros((a.max() + 1, b.max() + 1))
    np.add.at(ct, (a, b), 1)
    comb = lambda x: x * (x - 1) / 2.0
    sij = comb(ct).sum(); si = comb(ct.sum(1)).sum(); sj = comb(ct.sum(0)).sum()
    n = comb(a.size)
    exp = si * sj / n
    mx = (si + sj) / 2.0
    return float((sij - exp) / (mx - exp)) if mx != exp else 1.0


# ------------------------------------------------------------------ pipeline over one replicate
def eval_replicate(args):
    """worker: (tag, pages_pickle) -> {'annealed': {k: T}, 'natural': {name: T}}"""
    tag, pages, seed0, do_natural = args
    Mtr, Mte, Utr, _tp = split_counts(pages)
    res_a = {}
    for k in KS:
        A, _ = best_anneal(Mtr, k, seed0 + k * 104729)
        res_a[k] = t_stat(A, k, Mtr, Mte, Utr)
    res_n = {}
    if do_natural:
        for name, A, k in natural_partitions():
            res_n[name] = t_stat(A, k, Mtr, Mte, Utr)
    return tag, res_a, res_n


# ------------------------------------------------------------------ plants
def freq_groups(stream, k, seed):
    """frequency-balanced grouping of the 29 runes into k classes (ground truth)."""
    cnt = np.bincount(stream, minlength=N).astype(float)
    order = np.argsort(-cnt)
    rng = random.Random(seed)
    loads = [0.0] * k
    truth = np.zeros(N, dtype=np.int64)
    for r in order:
        c = min(range(k), key=lambda c: (loads[c], rng.random()))
        truth[r] = c
        loads[c] += cnt[r]
    return truth


def homophonic_encipher(plain_classes, truth, k, seed, repeat_avoid_s=None):
    groups = [np.where(truth == c)[0] for c in range(k)]
    rng = random.Random(seed)
    out = np.empty(len(plain_classes), dtype=np.int64)
    prev = -1
    for i, c in enumerate(plain_classes):
        g = groups[c]
        x = int(g[rng.randrange(len(g))])
        if repeat_avoid_s is not None and x == prev and len(g) > 1:
            if rng.random() >= repeat_avoid_s:
                while x == prev:
                    x = int(g[rng.randrange(len(g))])
        out[i] = x
        prev = x
    return out


def build_plant(register, k, seed, s=None):
    d = np.load(os.path.join(LP, "analysis", "round19", "I2", "models", "testhalves.npz"))
    src = d[register].astype(np.int64)
    real = real_pages()
    n = sum(len(p) for p in real)
    reps = int(np.ceil(n / len(src)))
    src = np.tile(src, reps)[:n]
    truth = freq_groups(src, k, seed)
    plain = truth[src]                       # collapse: plaintext class stream
    ct = homophonic_encipher(plain, truth, k, seed + 1, repeat_avoid_s=s)
    return recut(ct, real), truth


def run_plants():
    real = real_pages()
    s = 29 * doublet_rate(real)
    plants = [("PC1_EN_k15_uniform", "EN_MODERN", 15, 33011, None),
              ("PC2_EN_k15_filtered", "EN_MODERN", 15, 33012, s),
              ("PC3_LA_k12_uniform", "LATIN", 12, 33013, None)]
    out = {"doublet_rate_real": doublet_rate(real), "s_keep": s, "plants": {}}
    for name, reg, k, seed, sv in plants:
        pages, truth = build_plant(reg, k, seed, sv)
        Mtr, Mte, Utr, tp = split_counts(pages)
        A, obj = best_anneal(Mtr, k, seed + 2)
        T = t_stat(A, k, Mtr, Mte, Utr)
        # provisional 100-draw family-A envelope on the plant stream itself
        env = []
        for i in range(100):
            sp = shuffle_pages(pages, 90000 + seed + i)
            M1, M2, U1, _ = split_counts(sp)
            A0, _ = best_anneal(M1, k, seed + 3 + i)
            env.append(t_stat(A0, k, M1, M2, U1))
        a = ari(A, truth)
        ct_ioc = float(sum(np.bincount(np.concatenate(pages), minlength=N) *
                           (np.bincount(np.concatenate(pages), minlength=N) - 1)).sum()
                       / (12956 * 12955) * 29)
        out["plants"][name] = {
            "k": k, "T": T, "train_mi": obj, "env100_max": max(env),
            "env100_p999_proxy": sorted(env)[-1], "ari": a,
            "ciphertext_iocN": round(ct_ioc, 4),
            "ciphertext_doublet": doublet_rate(pages),
            "r3": r3_stats(A, k, tp),
            "pass": bool(T > max(env) and a >= 0.5)}
        print(name, "T=%.4f env_max=%.4f ARI=%.3f pass=%s" %
              (T, max(env), a, out["plants"][name]["pass"]), flush=True)
    os.makedirs(RESULTS, exist_ok=True)
    json.dump(out, open(os.path.join(RESULTS, "plants.json"), "w"), indent=1)
    return out


# ------------------------------------------------------------------ the real screen
def tasks_for_screen(real, s):
    yield ("real", real, 424242, True)
    for i in range(NULL_DRAWS):
        yield (f"A{i}", shuffle_pages(real, SEED_A + i), SEED_A * 100 + i, True)
    for i in range(NULL_DRAWS):
        yield (f"B{i}", filtered_uniform(real, s, SEED_B + i), SEED_B * 100 + i, True)


def run_screen(procs=8):
    real = real_pages()
    s = 29 * doublet_rate(real)
    rows_path = os.path.join(RESULTS, "rows.jsonl")
    os.makedirs(RESULTS, exist_ok=True)
    acc = {"annealed": {k: {"A": [], "B": []} for k in KS},
           "natural": {}, "real": None}
    with Pool(procs) as pool, open(rows_path, "w") as fh:
        for tag, ra, rn in pool.imap_unordered(eval_replicate, tasks_for_screen(real, s),
                                               chunksize=4):
            fh.write(json.dumps({"tag": tag, "annealed": ra, "natural": rn}) + "\n")
            if tag == "real":
                acc["real"] = {"annealed": ra, "natural": rn}
            else:
                fam = tag[0]
                for k in KS:
                    acc["annealed"][k][fam].append(ra[k])
                for name, v in rn.items():
                    acc["natural"].setdefault(name, {"A": [], "B": []})[fam].append(v)
    # verdicts at the fixed bar: > 999th order statistic of BOTH families
    def bar(v):
        return sorted(v)[998] if len(v) >= 999 else max(v)
    screen = {"s_keep": s, "cells": {}}
    for k in KS:
        tA, tB = bar(acc["annealed"][k]["A"]), bar(acc["annealed"][k]["B"])
        tr = acc["real"]["annealed"][k]
        screen["cells"][f"anneal_k{k}"] = {
            "T_real": tr, "bar_A_p999": tA, "bar_B_p999": tB,
            "n_A": len(acc["annealed"][k]["A"]), "n_B": len(acc["annealed"][k]["B"]),
            "crosser": bool(tr > tA and tr > tB)}
    for name, v in acc["natural"].items():
        tA, tB = bar(v["A"]), bar(v["B"])
        tr = acc["real"]["natural"][name]
        screen["cells"][f"natural_{name}"] = {
            "T_real": tr, "bar_A_p999": tA, "bar_B_p999": tB,
            "n_A": len(v["A"]), "n_B": len(v["B"]),
            "crosser": bool(tr > tA and tr > tB)}
    # R3 stats + best partitions for the real stream, per k
    Mtr, Mte, Utr, tp = split_counts(real)
    details = {}
    for k in KS:
        A, obj = best_anneal(Mtr, k, 424242 + k * 104729)
        details[f"k{k}"] = {"partition": A.tolist(), "train_mi": obj,
                            "T": t_stat(A, k, Mtr, Mte, Utr), "r3": r3_stats(A, k, tp)}
    screen["real_details"] = details
    screen["n_crossers"] = sum(c["crosser"] for c in screen["cells"].values())
    json.dump(screen, open(os.path.join(RESULTS, "screen.json"), "w"), indent=1)
    print("cells:", len(screen["cells"]), "crossers:", screen["n_crossers"], flush=True)
    return screen


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "check":
        real = real_pages()
        print("pages", len(real), "runes", sum(len(p) for p in real),
              "doublet", doublet_rate(real))
        d = np.load(os.path.join(LP, "analysis", "round19", "I2", "models", "testhalves.npz"))
        print("testhalves:", {k: d[k].shape for k in ("EN_MODERN", "LATIN")})
        import time
        Mtr, Mte, Utr, _ = split_counts(real)
        t = time.time()
        A, obj = best_anneal(Mtr, 15, 1)
        print("anneal k=15: %.2fs train_mi=%.4f T=%.4f" %
              (time.time() - t, obj, t_stat(A, 15, Mtr, Mte, Utr)))
    elif mode == "plant":
        run_plants()
    elif mode == "screen":
        run_screen(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
