"""Fresh-eyes audit, part 9: proof of concept for a language-model-free ("blind") adjudicator.

Claim (AUDIT.md 1.7): under key-skip, a rejection at cipher position i with key pointer j is only
POSSIBLE if s*(K[j+1] - K[j]) == C[i] - C[i-1] (mod 29) (for a run of r rejections: the r rejected
draws are equal and the accepted one differs from them by C[i] - C[i-1]). So the key pointer can be tracked from the
key and the ciphertext alone: branch only at admissible sites, score each complete path by the index
of coincidence of its decode, keep the best. The score does not depend on how the plaintext symbols
are labelled, so one adjudicator covers any language, any orthography, any plaintext numbering, a
constant in the combiner, Atbash and Beaufort.

This file measures that on plants. It is a feasibility measurement, not a lane: no real key is
tested and no threshold is fixed for one. The encipherer is the Campaign XVIII implementation
(analysis/campaign18_skip/skipdecode.py), which shares no code with the decoder below.
Output: blind_adjudicator_poc.json.
"""
import collections
import json
import os
import random
import re
import sys

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(lp2.LP, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(lp2.LP, "src"))
import skipdecode as sk  # noqa: E402

N = 29


def blind_decode(C, K, s=+1, max_skips=10):
    """Best-IoC path for C = P + s*K with key-skips at admissible sites. Returns (ioc_x29, skips, paths)."""
    L = len(C)
    best = (-1, 0)
    paths = 0
    stack = [(0, 0, 0, [0] * N, 0)]            # i, j, skips used, counts, sum of squares
    while stack:
        i, j, used, cnt, ssq = stack.pop()
        while i < L:
            if i > 0 and used < max_skips:
                # r draws K[j..j+r-1] were rejected and K[j+r] accepted. Each rejected draw gave the same
                # would-be rune C[i-1], so the rejected draws are all equal, and the accepted one differs
                # from them by exactly C[i] - C[i-1].
                r = 1
                while r <= 3:
                    if (s * (K[j + r] - K[j]) - (C[i] - C[i - 1])) % N == 0:
                        stack.append((i, j + r, used + r, cnt[:], ssq))    # its own copy of the counts
                    if K[j + r] != K[j]:
                        break
                    r += 1
            d = (C[i] - s * K[j]) % N
            ssq += 2 * cnt[d] + 1
            cnt[d] += 1
            i += 1
            j += 1
        paths += 1
        if ssq > best[0]:
            best = (ssq, used)
    ioc = N * (best[0] - L) / (L * (L - 1))
    return ioc, best[1], paths


def texts():
    single = {x: i for i, x in enumerate(lp2.TR) if len(x) == 1}
    single.update({"K": single["C"], "V": single["U"], "Z": single["S"], "Q": single["C"]})
    multi = sorted(((x, i) for i, x in enumerate(lp2.TR)), key=lambda z: -len(z[0]))

    def lw(w):
        return [single[c] for c in w]

    def mg(w):
        w = w.replace("K", "C").replace("V", "U").replace("Z", "S").replace("Q", "C"); o = []; i = 0
        while i < len(w):
            if w.startswith("ING", i):
                o.append(21); i += 3; continue
            for x, k in multi:
                if w.startswith(x, i):
                    o.append(k); i += len(x); break
            else:
                i += 1
        return o

    def load(path, enc):
        t = open(path, encoding="utf-8", errors="ignore").read().upper()
        ws = re.sub(r"[^A-Z]+", " ", t[len(t) // 4: 3 * len(t) // 4]).split()
        return [v for w in ws[:40000] for v in enc(w)]

    keys = os.path.join(lp2.LP, "data", "keys")
    return {"English letter-wise": load(os.path.join(keys, "armada18", "melville_moby_dick.txt"), lw),
            "English multigraph": load(os.path.join(keys, "armada18", "melville_moby_dick.txt"), mg),
            "Latin letter-wise": load(os.path.join(lp2.LP, "analysis", "latin", "latin_28233.txt"), lw)}


def main():
    rng = random.Random(4401)
    T = texts()
    out = {"cells": []}
    for L in (64, 120, 160):
        # null: wrong (random) keys against real LP2 page-0 ciphertext, both signs
        C0 = lp2.idx(lp2.unsolved())[0][:L]
        null = []
        for _ in range(400):
            K = [rng.randrange(N) for _ in range(L + 40)]
            null.append(max(blind_decode(C0, K, +1)[0], blind_decode(C0, K, -1)[0]))
        null.sort()
        nm = sum(null) / len(null); nsd = (sum((x - nm) ** 2 for x in null) / len(null)) ** 0.5
        for tname, stream in T.items():
            for variant in ("as written", "random relabelling of the plaintext", "C = P + K + 7", "Beaufort C = K - P"):
                vals, exact, npaths = [], 0, []
                for _ in range(40):
                    a = rng.randrange(0, len(stream) - L - 1)
                    P = stream[a:a + L]
                    if variant.startswith("random"):
                        perm = list(range(N)); rng.shuffle(perm); P = [perm[x] for x in P]
                    elif variant.startswith("C = P"):
                        P = [(x + 7) % N for x in P]
                    elif variant.startswith("Beaufort"):
                        P = [(-x) % N for x in P]
                    K = [rng.randrange(N) for _ in range(L + 60)]
                    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=rng.randrange(10 ** 6))
                    ioc, used, paths = blind_decode(C, K, +1)
                    vals.append(ioc); exact += (used == sum(skips)); npaths.append(paths)
                vals.sort()
                cell = {"L": L, "plaintext": tname, "variant": variant, "ioc_x29_min": vals[0], "ioc_x29_median": vals[len(vals) // 2],
                        "null_mean": nm, "null_sd": nsd, "null_max_of_400": null[-1],
                        "plants_above_null_max": sum(v > null[-1] for v in vals), "plants": len(vals),
                        "skip_count_exact": exact, "mean_paths": sum(npaths) / len(npaths),
                        "z_of_median": (vals[len(vals) // 2] - nm) / nsd}
                out["cells"].append(cell)
                print(f"L={L:3d} {tname:20s} {variant:36s} IoCx29 min/med {vals[0]:.2f}/{cell['ioc_x29_median']:.2f} | null {nm:.2f}+-{nsd:.2f} max {null[-1]:.2f} "
                      f"| above null max {cell['plants_above_null_max']}/{len(vals)} | z(med) {cell['z_of_median']:+.1f} | paths {cell['mean_paths']:.0f}", flush=True)
    json.dump(out, open(os.path.join(HERE, "blind_adjudicator_poc.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
