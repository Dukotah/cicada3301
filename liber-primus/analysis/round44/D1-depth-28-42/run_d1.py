"""Round 44 lane D1 driver: plants, nulls, then the real pair, per cell. See PREREG.md."""
import itertools
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import depth2 as d2  # noqa: E402
import lp2           # noqa: E402

N_PLANTS, N_NULL_PAIRS, CORRUPT, BEAM = 12, 30, 0.05, 50_000
PA, PB = 28, 42


def page_arrays(pages, k):
    return [r["i"] for r in pages[k]], [lp2.word_start(r, j) for j, r in enumerate(pages[k])]


def pair_D(pages, i, j, off=0):
    a, sa = page_arrays(pages, i); b, sb = page_arrays(pages, j)
    if off >= 0:
        b, sb = b[off:], sb[off:]
    else:
        a, sa = a[-off:], sa[-off:]
    n = min(len(a), len(b))
    sa, sb = list(sa[:n]), list(sb[:n]); sa[0] = sb[0] = True
    return [(a[t] - b[t]) % 29 for t in range(n)], sa, sb


def main(cells):
    pages = lp2.unsolved()
    train, held = d2.corpus_files()
    out = {"prereg": "PREREG.md", "beam": BEAM, "corrupt": CORRUPT, "train_files": len(train),
           "held_out": [os.path.basename(f) for f in held], "cells": {}}
    rng = random.Random(4428)
    elig = [(i, j) for i, j in itertools.combinations(range(55), 2)
            if (i, j) != (PA, PB) and min(len(pages[i]), len(pages[j])) >= 200]
    null_pairs = rng.sample(elig, N_NULL_PAIRS)
    for cname in cells:
        t0 = time.time()
        cell = d2.Cell(cname)
        lm, nchar = d2.train_lm(cell, train)
        res = {"lm_symbols_trained": nchar, "plants": [], "nulls": [], "real": None}
        # ---- plants (held-out text, 5 % corrupted positions)
        prng = random.Random(1000 + len(cname))
        held_txt = [d2.clean(f) for f in held]
        for k in range(N_PLANTS):
            enc = []
            for _ in range(2):
                t = prng.choice(held_txt); w = t.split(); s = prng.randrange(0, len(w) - 400)
                syms, st = cell.encode_text(" ".join(w[s:s + 200]))
                enc.append((syms[:269], st[:269]))
            (xa, sa), (xb, sb) = enc
            D = [(cell.val[p] - cell.val[q]) % 29 for p, q in zip(xa, xb)]
            for t in range(len(D)):
                if prng.random() < CORRUPT:
                    D[t] = prng.randrange(29)
            S, ya, yb = d2.decode(cell, lm, D, sa, sb, beam=BEAM)
            rec = (sum(p == q for p, q in zip(xa, ya)) + sum(p == q for p, q in zip(xb, yb))) / (2 * len(D))
            res["plants"].append({"S": S, "recovery": rec})
            print(f"[{cname}] plant {k:2d}  S={S:.3f}  recovery={rec:.3f}", flush=True)
        # ---- nulls
        for (i, j) in null_pairs:
            D, sa, sb = pair_D(pages, i, j)
            S, _, _ = d2.decode(cell, lm, D, sa, sb, beam=BEAM, want_path=False)
            res["nulls"].append({"pair": [i, j], "off": 0, "n": len(D), "S": S})
        for off in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5):
            D, sa, sb = pair_D(pages, PA, PB, off)
            S, _, _ = d2.decode(cell, lm, D, sa, sb, beam=BEAM, want_path=False)
            res["nulls"].append({"pair": [PA, PB], "off": off, "n": len(D), "S": S})
        ns = [x["S"] for x in res["nulls"]]
        print(f"[{cname}] nulls: n={len(ns)} mean={np.mean(ns):.3f} sd={np.std(ns):.3f} max={max(ns):.3f}", flush=True)
        # ---- the real pair
        D, sa, sb = pair_D(pages, PA, PB)
        S, ya, yb = d2.decode(cell, lm, D, sa, sb, beam=BEAM)
        ps = [x["S"] for x in res["plants"]]; rc = [x["recovery"] for x in res["plants"]]
        ctrl = sum(r >= 0.70 for r in rc) >= 10
        mid = (max(ns) + min(ps)) / 2
        verdict = ("INCONCLUSIVE (control failed)" if not ctrl else
                   "FLAGGED-FOR-ORACLE" if S >= mid else
                   "NEGATIVE" if S <= max(ns) else "INCONCLUSIVE (between null max and midpoint)")
        res["real"] = {"S": S, "n": len(D), "textA": d2.render(cell, ya, sa), "textB": d2.render(cell, yb, sb)}
        res.update({"S_null_max": max(ns), "S_null_mean": float(np.mean(ns)), "S_null_sd": float(np.std(ns)),
                    "S_plant_min": min(ps), "S_plant_median": float(np.median(ps)),
                    "plants_at_0.70": int(sum(r >= 0.70 for r in rc)), "control_passed": bool(ctrl),
                    "midpoint": mid, "verdict": verdict, "seconds": round(time.time() - t0)})
        print(f"[{cname}] REAL S={S:.3f}  null max {max(ns):.3f}  plant min {min(ps):.3f}  midpoint {mid:.3f}  -> {verdict}", flush=True)
        print(f"[{cname}] page 28: {res['real']['textA'][:150]}", flush=True)
        print(f"[{cname}] page 42: {res['real']['textB'][:150]}", flush=True)
        out["cells"][cname] = res
        json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    main(sys.argv[1:] or ["G-LW", "G-MG", "A-LW"])
