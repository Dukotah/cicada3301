"""B2 lane, Stage 1 — forward simulation of the HAND-CIPHER family.

Encipher real English with a SHORT key (k = 4..12) over the 29-rune Gematria
Primus, apply a local no-repeat correction rule whenever the next ciphertext
rune would repeat the previous one, and measure whether the result can look
like LP2: doublet rate 0.66%, IoC*29 = 1.0000, no key-length signature.

Decisive statistic: kappa(L) = P(c_i == c_{i+L}).  It is LOCAL, so global phase
drift cannot destroy it.

Usage:  PYTHONUTF8=1 python3 b2_sim.py
Writes: results_stage1.json  (and prints a table)
"""
import io
import json
import os
import re
import sys
import math
import random

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(REPO, "liber-primus")
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402

N = 29
RAND_KAPPA = 1.0 / N


# ---------------------------------------------------------------- data loading
def load_lp2():
    """Concatenated unsolved stream, pages 0-54 (n = 12,956)."""
    d = json.load(io.open(os.path.join(LP, "dataset", "liber_primus.json"),
                          encoding="utf-8"))
    idx = []
    for p in d["pages"]:
        if p["page"] <= 54:
            idx.extend(p["indices"])
    return np.array(idx, dtype=np.int8)


def load_english_runes(nmin):
    """Real English -> Gematria Primus indices (runeglish, greedy digraphs)."""
    out = []
    for fn in ("moby.txt", "pride.txt", "war.txt", "kjv.txt"):
        path = os.path.join(LP, "data", fn)
        if not os.path.exists(path):
            continue
        txt = io.open(path, encoding="utf-8", errors="ignore").read()
        txt = re.sub(r"[^A-Za-z]", "", txt).upper()
        # chunk to keep keyword_to_indices cheap
        for i in range(0, min(len(txt), 400000), 4000):
            try:
                out.extend(gp.keyword_to_indices(txt[i:i + 4000]))
            except ValueError:
                pass
            if len(out) >= nmin:
                return np.array(out[:nmin], dtype=np.int8)
    return np.array(out[:nmin], dtype=np.int8)


# ------------------------------------------------------------------ statistics
def kappa_spectrum(c, lags):
    c = np.asarray(c, dtype=np.int16)
    out = {}
    for L in lags:
        if L >= len(c):
            continue
        out[L] = float(np.mean(c[:-L] == c[L:]))
    return out


def ioc_norm(c):
    c = np.asarray(c)
    n = len(c)
    cnt = np.bincount(c, minlength=N).astype(float)
    return float(np.sum(cnt * (cnt - 1)) / (n * (n - 1)) * N)


def column_ioc(c, period):
    """Classic key-length detector: mean IoC*29 of the `period` columns."""
    c = np.asarray(c)
    vals = []
    for r in range(period):
        col = c[r::period]
        if len(col) < 20:
            continue
        vals.append(ioc_norm(col))
    return float(np.mean(vals)) if vals else float("nan")


def doublet_rate(c):
    c = np.asarray(c)
    return float(np.mean(c[:-1] == c[1:]))


def kasiski(c, nmin=3, maxgcd=40):
    """Histogram of GCD-compatible spacings between repeated trigrams."""
    c = np.asarray(c)
    seen = {}
    for i in range(len(c) - nmin + 1):
        t = (int(c[i]) << 10) | (int(c[i + 1]) << 5) | int(c[i + 2])
        seen.setdefault(t, []).append(i)
    votes = np.zeros(maxgcd + 1)
    nsp = 0
    for pos in seen.values():
        if len(pos) < 2:
            continue
        for a in range(len(pos) - 1):
            sp = pos[a + 1] - pos[a]
            nsp += 1
            for f in range(2, maxgcd + 1):
                if sp % f == 0:
                    votes[f] += 1
    if nsp:
        votes /= nsp
    return votes, nsp


def sigma(n):
    return math.sqrt(RAND_KAPPA * (1 - RAND_KAPPA) / n)


# --------------------------------------------------------------------- ciphers
def encipher(pt, key, rule, p_fix, nout, rng):
    """Encipher plaintext indices `pt` with short key `key`, applying the local
    no-repeat correction `rule` with probability p_fix when a doublet appears.

    Returns (ciphertext array, n_corrections, n_drift_events).
    """
    k = len(key)
    out = np.empty(nout, dtype=np.int8)
    j = 0          # ciphertext index
    pi = 0         # plaintext index
    ph = 0         # key phase
    prev = -1
    ncorr = 0
    ndrift = 0
    npt = len(pt)
    while j < nout and pi < npt:
        c = (int(pt[pi]) + int(key[ph % k])) % N
        if c == prev and rng.random() < p_fix:
            ncorr += 1
            if rule == "R1_BUMP":
                c = (c + 1) % N
                pi += 1
                ph += 1
            elif rule == "R2_KEYADV":
                tries = 0
                while c == prev and tries < N:
                    ph += 1
                    ndrift += 1
                    tries += 1
                    c = (int(pt[pi]) + int(key[ph % k])) % N
                pi += 1
                ph += 1
            elif rule == "R3_KEYRESET":
                ph = 0
                ndrift += 1
                c = (int(pt[pi]) + int(key[ph % k])) % N
                tries = 0
                while c == prev and tries < N:
                    ph += 1
                    tries += 1
                    c = (int(pt[pi]) + int(key[ph % k])) % N
                pi += 1
                ph += 1
            elif rule == "R4_PTSKIP":
                tries = 0
                while c == prev and tries < N and pi + 1 < npt:
                    pi += 1
                    ph += 1
                    ndrift += 1
                    tries += 1
                    c = (int(pt[pi]) + int(key[ph % k])) % N
                pi += 1
                ph += 1
            elif rule == "R5_INTERRUPT":
                c = 0  # the F rune, emitted as a null; consumes nothing
                ndrift += 1
                if c == prev:      # F already on the wire -> fall back to bump
                    c = 1
            elif rule == "R6_REPICK":
                c = rng.randrange(N - 1)
                if c >= prev:
                    c += 1
                pi += 1
                ph += 1
            else:
                raise ValueError(rule)
        else:
            pi += 1
            ph += 1
        out[j] = c
        prev = c
        j += 1
    return out[:j], ncorr, ndrift


# ----------------------------------------------------------------------- nulls
def null_shuffled(c, rng):
    a = np.array(c, copy=True)
    rs = np.random.RandomState(rng.randrange(1 << 30))
    rs.shuffle(a)
    return a


def null_memoryless_softfilter(n, p_fix, rng):
    """The repo's incumbent model: i.i.d. uniform base + soft anti-repeat."""
    out = np.empty(n, dtype=np.int8)
    prev = -1
    for i in range(n):
        c = rng.randrange(N)
        if c == prev and rng.random() < p_fix:
            c = rng.randrange(N - 1)
            if c >= prev:
                c += 1
        out[i] = c
        prev = c
    return out


# ------------------------------------------------------------------------ main
def summarize(c, label, lags, extra=None):
    n = len(c)
    ks = kappa_spectrum(c, lags)
    band = [L for L in ks if 2 <= L <= 40]
    kmax_L = max(band, key=lambda L: ks[L])
    wide = [L for L in ks if 2 <= L <= 400]
    wmax_L = max(wide, key=lambda L: ks[L])
    cols = {p: column_ioc(c, p) for p in range(2, 41)}
    cp = max(cols, key=lambda p: cols[p])
    rec = {
        "label": label,
        "n": n,
        "doublet": doublet_rate(c),
        "ioc29": ioc_norm(c),
        "kappa1": ks.get(1),
        "kappa_max_2_40": ks[kmax_L], "kappa_argmax_2_40": kmax_L,
        "kappa_max_2_40_z": (ks[kmax_L] - RAND_KAPPA) / sigma(n),
        "kappa_max_2_400": ks[wmax_L], "kappa_argmax_2_400": wmax_L,
        "kappa_max_2_400_z": (ks[wmax_L] - RAND_KAPPA) / sigma(n),
        "colioc_max": cols[cp], "colioc_argmax": cp,
        "spectrum": {str(L): ks[L] for L in sorted(ks)},
    }
    if extra:
        rec.update(extra)
    return rec


def main():
    rng = random.Random(3301)
    lags = list(range(1, 401))
    results = []

    real = load_lp2()
    print(f"LP2 pages 0-54: n={len(real)}")
    R = summarize(real, "REAL_LP2_0_54", lags)
    results.append(R)
    print(f"  REAL: doublet={R['doublet']:.4%} ioc29={R['ioc29']:.4f} "
          f"maxkappa[2,40]={R['kappa_max_2_40']:.4f} (L={R['kappa_argmax_2_40']}, "
          f"z={R['kappa_max_2_40_z']:+.2f})  colIoC max={R['colioc_max']:.3f} "
          f"@p={R['colioc_argmax']}")

    n = len(real)
    pt = load_english_runes(int(n * 1.6))
    print(f"English runeglish plaintext: n={len(pt)} ioc29={ioc_norm(pt):.4f} "
          f"doublet={doublet_rate(pt):.4%}")
    results.append(summarize(pt[:n], "ENGLISH_PLAINTEXT_RUNEGLISH", lags))

    # ---- nulls
    for lab, arr in (
        ("NULL_N1_shuffled_LP2", null_shuffled(real, rng)),
        ("NULL_N2_memoryless_softfilter", null_memoryless_softfilter(n, 0.82, rng)),
    ):
        r = summarize(arr, lab, lags)
        results.append(r)
        print(f"  {lab}: doublet={r['doublet']:.4%} ioc29={r['ioc29']:.4f} "
              f"maxkappa[2,40]={r['kappa_max_2_40']:.4f} z={r['kappa_max_2_40_z']:+.2f} "
              f"colIoC={r['colioc_max']:.3f}")

    # ---- N3 anchor: rigid short-key Vigenere, no correction at all
    for k in (4, 8, 12):
        key = [rng.randrange(N) for _ in range(k)]
        c, _, _ = encipher(pt, key, "R1_BUMP", 0.0, n, rng)
        r = summarize(c, f"NULL_N3_rigid_vigenere_k{k}", lags, {"k": k})
        results.append(r)
        print(f"  N3 rigid k={k}: doublet={r['doublet']:.4%} ioc29={r['ioc29']:.4f} "
              f"kappa({k})={r['spectrum'][str(k)]:.4f} "
              f"maxkappa[2,40]={r['kappa_max_2_40']:.4f}@{r['kappa_argmax_2_40']} "
              f"colIoC={r['colioc_max']:.3f}@{r['colioc_argmax']}")

    # ---- the B2 family
    rules = ["R1_BUMP", "R2_KEYADV", "R3_KEYRESET", "R4_PTSKIP", "R5_INTERRUPT",
             "R6_REPICK"]
    print("\n--- B2 family sweep ---")
    for rule in rules:
        for k in range(4, 13):
            for p_fix in (0.82, 1.0):
                key = [rng.randrange(N) for _ in range(k)]
                c, ncorr, ndrift = encipher(pt, key, rule, p_fix, n, rng)
                r = summarize(c, f"B2_{rule}_k{k}_p{p_fix}", lags, {
                    "rule": rule, "k": k, "p_fix": p_fix,
                    "n_corrections": ncorr, "n_drift": ndrift,
                    "drift_rate": ndrift / max(1, len(c)),
                    "kappa_at_k": kappa_spectrum(c, [k])[k],
                    "kappa_at_k_z": (kappa_spectrum(c, [k])[k] - RAND_KAPPA) / sigma(len(c)),
                    "colioc_at_k": column_ioc(c, k),
                })
                results.append(r)
            print(f"  {rule} k={k:2d}: doublet={r['doublet']:.4%} "
                  f"ioc29={r['ioc29']:.4f} kappa(k)={r['kappa_at_k']:.4f} "
                  f"(z={r['kappa_at_k_z']:+6.1f}) colIoC(k)={r['colioc_at_k']:.3f} "
                  f"drift={r['drift_rate']:.3%}")

    # ---- detection wall: how long can the key be before kappa(k) hides?
    print("\n--- detection wall (rule R2_KEYADV, p_fix 0.82) ---")
    wall = []
    real_max400 = R["kappa_max_2_400"]
    for k in (4, 8, 12, 16, 20, 24, 30, 40, 50, 60, 80, 100, 120, 150, 200):
        key = [rng.randrange(N) for _ in range(k)]
        c, ncorr, ndrift = encipher(pt, key, "R2_KEYADV", 0.82, n, rng)
        kk = kappa_spectrum(c, [k])[k]
        z = (kk - RAND_KAPPA) / sigma(len(c))
        zvsreal = (kk - real_max400) / sigma(len(c))
        wall.append({"k": k, "kappa_at_k": kk, "z_vs_random": z,
                     "z_vs_real_max": zvsreal, "doublet": doublet_rate(c),
                     "ioc29": ioc_norm(c), "colioc_at_k": column_ioc(c, k),
                     "drift_rate": ndrift / max(1, len(c))})
        print(f"  k={k:4d}: kappa={kk:.4f} z_vs_random={z:+6.1f} "
              f"z_vs_real_max={zvsreal:+6.1f} colIoC(k)={column_ioc(c, k):.3f}")

    # ---- Kasiski on real vs one B2 config
    votes_real, nsp_real = kasiski(real)
    key = [rng.randrange(N) for _ in range(8)]
    c8, _, _ = encipher(pt, key, "R2_KEYADV", 0.82, n, rng)
    votes_b2, nsp_b2 = kasiski(c8)
    kas = {"real_nspacings": nsp_real, "b2_k8_nspacings": nsp_b2,
           "real_votes": votes_real.tolist(), "b2_k8_votes": votes_b2.tolist()}

    json.dump({"results": results, "wall": wall, "kasiski": kas,
               "sigma_at_n": sigma(n), "random_kappa": RAND_KAPPA},
              io.open(os.path.join(HERE, "results_stage1.json"), "w",
                      encoding="utf-8"))
    print("\nwrote results_stage1.json")


if __name__ == "__main__":
    main()
