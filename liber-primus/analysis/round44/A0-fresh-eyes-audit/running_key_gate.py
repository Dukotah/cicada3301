"""Fresh-eyes audit, part 3: a natural-language running key cannot produce LP2's flat monograms.

For C = P +/- K with P and K both English, the ciphertext monogram distribution is the convolution
of two English distributions. It is not flat. This is a family-level gate that needs no key, no
offset and no decoder, and no ledger row uses it. Output: running_key_gate.json.
"""
import collections
import json
import os
import re

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
N = 12956
t = open(os.path.join(lp2.LP, "data", "keys", "armada18", "melville_moby_dick.txt"), encoding="utf-8", errors="ignore").read().upper()
t = re.sub(r"[^A-Z]+", " ", t[len(t) // 5: 4 * len(t) // 5])
single = {x: i for i, x in enumerate(lp2.TR) if len(x) == 1}
single.update({"K": single["C"], "V": single["U"], "Z": single["S"], "Q": single["C"]})
multi = sorted(((x, i) for i, x in enumerate(lp2.TR)), key=lambda z: -len(z[0]))


def letterwise(w):
    return [single[c] for c in w]


def multigraph(w):
    w = w.replace("K", "C").replace("V", "U").replace("Z", "S").replace("Q", "C"); o = []; i = 0
    while i < len(w):
        if w.startswith("ING", i):
            o.append(21); i += 3; continue
        if w.startswith("IO", i):
            o.append(27); i += 2; continue
        for x, k in multi:
            if w.startswith(x, i):
                o.append(k); i += len(x); break
        else:
            i += 1
    return o


def dist(enc):
    c = collections.Counter(x for w in t.split() for x in enc(w)); n = sum(c.values())
    return [c.get(k, 0) / n for k in range(29)]


def conv(p, q):
    return [sum(p[a] * q[(c - a) % 29] for a in range(29)) for c in range(29)]


obs_chi2 = sum((v - N / 29) ** 2 / (N / 29) for v in collections.Counter(x for p in lp2.idx(lp2.unsolved()) for x in p).values())
out = {"observed_monogram_chi2_28df": obs_chi2, "cells": {}}
for name, enc in (("letter-wise", letterwise), ("multigraph (solved-page orthography)", multigraph)):
    p = dist(enc); r = conv(p, p)
    out["cells"][name] = {"plaintext_ioc_x29": 29 * sum(x * x for x in p), "cipher_ioc_x29": 29 * sum(x * x for x in r),
                          "predicted_monogram_chi2": 28 + N * 29 * sum((x - 1 / 29) ** 2 for x in r)}
    mix = {}
    for eps in (0.5, 0.25, 0.15, 0.10):
        q = [(1 - eps) / 29 + eps * x for x in p]; r = conv(p, q)
        mix[str(eps)] = 28 + N * 29 * sum((x - 1 / 29) ** 2 for x in r)
    out["cells"][name]["predicted_chi2_if_key_is_eps_English_plus_uniform"] = mix
# positive control: actually encipher English under an English running key WITH the anti-repeat key-skip
# filter (suppression 0.81) and measure the monogram chi-square of the result, both spellings, +/- key.
import glob
import random

books = [f for f in sorted(glob.glob(os.path.join(lp2.LP, "data", "keys", "armada1[89]", "*.txt")))
         if "latin" not in f and os.path.getsize(f) > 500_000]
rng = random.Random(44)
plants = []
for name, enc in (("letter-wise", letterwise), ("multigraph", multigraph)):
    for sign in (+1, -1):
        for _ in range(3):
            fa, fb = rng.sample(books, 2)
            def stream(f):
                x = re.sub(r"[^A-Z]+", " ", open(f, encoding="utf-8", errors="ignore").read().upper()).split()
                x = x[len(x) // 4:]
                return [v for w in x[:6000] for v in enc(w)]
            Pt, K = stream(fa), stream(fb)
            C, j, prev = [], 0, None
            for p_ in Pt[:N]:
                while True:
                    c = (p_ + sign * K[j]) % 29
                    if prev is not None and c == prev and rng.random() < 0.81:
                        j += 1
                        continue
                    break
                C.append(c); j += 1; prev = c
            cnt = collections.Counter(C)
            plants.append({"spelling": name, "sign": sign, "n": len(C),
                           "monogram_chi2": sum((cnt.get(k, 0) - len(C) / 29) ** 2 / (len(C) / 29) for k in range(29)),
                           "doublets": sum(a == b for a, b in zip(C, C[1:]))})
out["planted_running_key_ciphertexts"] = plants
out["plant_min_chi2"] = min(x["monogram_chi2"] for x in plants)
json.dump(out, open(os.path.join(HERE, "running_key_gate.json"), "w"), indent=1)
print("planted running-key ciphertexts (12 plants, filter on): monogram chi2 min %.0f max %.0f" % (out["plant_min_chi2"], max(x["monogram_chi2"] for x in plants)))
print("observed monogram chi2 %.1f on 28 df" % obs_chi2)
for k, v in out["cells"].items():
    print(f"  {k:38s} predicted chi2 {v['predicted_monogram_chi2']:.0f}  (cipher IoC x29 {v['cipher_ioc_x29']:.4f})  key purity bound: {v['predicted_chi2_if_key_is_eps_English_plus_uniform']}")
