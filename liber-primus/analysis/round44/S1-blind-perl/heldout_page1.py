"""Lane S1, the held-out page: does a flagged key go on decoding page 1? (POST-DATA; see RESULTS.md)

HUMAN-ORACLE.md asks every crosser for a second, independent page that the key was not selected on.
The sweep selected on page 0 only. For a true continuous key, page 1 decoded from the key position
where page 0 ended has the plaintext's index of coincidence (about 1.7 or more); for a wrong key
that got through on a fluke page-0 head, page 1 is a fresh random decode (about 1.1).

Controls: two-page plants (528 runes, one continuous key, the repo's own filter constructions),
decoded the same way. Output: heldout_page1.json.
"""
import collections
import json
import os
import random

import common as cm

N = cm.N
PAGES = cm.lp2.idx(cm.lp2.unsolved())
P0, P1 = PAGES[0], PAGES[1]
L0, LB = len(P0), 200            # page 1 is judged on its first 200 runes


def search(C, K, s, q, i0, i1, j0, maxsk):
    """Best path over C[i0:i1] starting at key pointer j0. Returns (IoC x 29, end pointer, decode)."""
    best = (-1, j0, None)
    stack = [(i0, j0, 0, [0] * N, 0, [])]
    while stack:
        i, j, used, cnt, ssq, dec = stack.pop()
        cnt = cnt[:]; dec = dec[:]
        while i < i1:
            if i > 0 and used < maxsk:
                r = 1
                while r <= 3:
                    jj = j + r * q
                    if (s * (K[jj] - K[j]) - (C[i] - C[i - 1])) % N == 0:
                        stack.append((i, jj, used + r, cnt[:], ssq, dec[:]))
                    if K[jj] != K[j]:
                        break
                    r += 1
            d = (C[i] - s * K[j]) % N
            ssq += 2 * cnt[d] + 1; cnt[d] += 1; dec.append(d)
            i += 1; j += 1
            if q == 2 and i - 1 > 0 and C[i - 1] == C[i - 2]:
                stack.append((i, j + 1, used, cnt[:], ssq, dec[:]))
        if ssq > best[0]:
            best = (ssq, j, dec)
    n = i1 - i0
    return N * (best[0] - n) / (n * (n - 1)), best[1], best[2]


def two_pages(C, K, s, q):
    ioc0, jend, _ = search(C, K, s, q, 0, L0, 0, 24)
    best1 = max(search(C, K, s, q, L0, L0 + LB, jend + d, 20)[0] for d in (0, 1, 2))
    return ioc0, best1


if __name__ == "__main__":
    rng = random.Random(4406)
    out = {"post_data": True, "page1_runes_judged": LB, "plants": [], "flags": []}
    T = cm.plant_texts()
    for k in range(9):
        tname = list(T)[k % 3]; cons = cm.CONSTRUCTIONS[k % 3]; variant = cm.VARIANTS[k % 4]
        K = [rng.randrange(N) for _ in range(700)]
        Cp, _ = cm.make_plant(rng, T[tname], variant, cons, K, L=L0 + LB + 4, sign=+1)
        a, b = two_pages(Cp, K, +1, 1 if cons == "keyskip1" else 2)
        out["plants"].append({"text": tname, "variant": variant, "construction": cons, "page0": a, "page1": b})
        print(f"plant {tname:20s} {variant:22s} {cons:14s} page 0 {a:.3f}   page 1 {b:.3f}", flush=True)
    C = P0 + P1
    res = json.load(open(os.path.join(cm.HERE, "results.json")))
    for f in res["flagged"]:
        s = +1 if f["mode"].startswith("s=+1") else -1; q = int(f["mode"][-1])
        a, b = two_pages(C, cm.perl_stream(f["seed"], 700), s, q)
        out["flags"].append({"seed": f["seed"], "mode": f["mode"], "page0": a, "page1": b})
        print(f"FLAG {f['seed']:>10d} {f['mode']}  page 0 {a:.3f}   page 1 {b:.3f}", flush=True)
    out["summary"] = {"plants_page1_min": min(x["page1"] for x in out["plants"]), "flags_page1_max": max(x["page1"] for x in out["flags"]),
                      "flags_page1_mean": sum(x["page1"] for x in out["flags"]) / len(out["flags"])}
    json.dump(out, open(os.path.join(cm.HERE, "heldout_page1.json"), "w"), indent=1)
    print(json.dumps(out["summary"]))
