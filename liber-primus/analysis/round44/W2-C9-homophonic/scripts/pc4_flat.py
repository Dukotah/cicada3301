"""PC4 — supplementary plant: the EXACT LP2-matched homophonic shape.

Group sizes proportional to plaintext class frequency (so ciphertext IoC*N ~ 1.000 flat),
plus the lag-1 repeat-avoiding filter (doublet ~ 0.66%). Built through the same glue as
PC1-PC3 (homophonic.py). Dated addendum plant: thresholds untouched, power claim only.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import homophonic as H  # noqa: E402


def flat_groups(stream):
    """groups with |g| ~ 29 * freq(group): high-freq runes get many homophones."""
    cnt = np.bincount(stream, minlength=H.N).astype(float)
    freq = cnt / cnt.sum()
    order = list(np.argsort(-freq))          # by EN freq desc
    truth = -np.ones(H.N, dtype=np.int64)
    c = 0
    while order:
        r = order.pop(0)                      # most frequent remaining
        size = max(1, int(round(29 * freq[r])))
        members = [r]
        while len(members) < size and order:
            members.append(order.pop())       # pad with least-frequent remaining
        for m in members:
            truth[m] = c
        c += 1
    return truth, c


def main():
    real = H.real_pages()
    s = 29 * H.doublet_rate(real)
    d = np.load(os.path.join(H.LP, "analysis", "round19", "I2", "models", "testhalves.npz"))
    src = d["EN_MODERN"].astype(np.int64)[:12956]
    truth, k = flat_groups(src)
    plain = truth[src]
    ct = H.homophonic_encipher(plain, truth, k, 33015, repeat_avoid_s=s)
    pages = H.recut(ct, real)
    cat = np.concatenate(pages)
    cnt = np.bincount(cat, minlength=H.N).astype(float)
    iocN = float((cnt * (cnt - 1)).sum() / (12956 * 12955) * 29)
    Mtr, Mte, Utr, tp = H.split_counts(pages)
    A, obj = H.best_anneal(Mtr, k, 33016)
    T = H.t_stat(A, k, Mtr, Mte, Utr)
    env = []
    for i in range(100):
        sp = H.shuffle_pages(pages, 91000 + i)
        M1, M2, U1, _ = H.split_counts(sp)
        A0, _ = H.best_anneal(M1, k, 33017 + i)
        env.append(H.t_stat(A0, k, M1, M2, U1))
    out = {"k": int(k), "T": T, "train_mi": obj, "env100_max": max(env),
           "ari": H.ari(A, truth), "ciphertext_iocN": round(iocN, 4),
           "ciphertext_doublet": H.doublet_rate(pages),
           "group_sizes": np.bincount(truth, minlength=k).tolist(),
           "r3": H.r3_stats(A, k, tp),
           "pass_detection": bool(T > max(env))}
    json.dump(out, open(os.path.join(H.RESULTS, "pc4_flat.json"), "w"), indent=1)
    print("PC4 k=%d T=%.4f env_max=%.4f ARI=%.3f iocN=%.3f doublet=%.4f pass=%s" %
          (k, T, max(env), out["ari"], iocN, out["ciphertext_doublet"],
           out["pass_detection"]), flush=True)


if __name__ == "__main__":
    main()
