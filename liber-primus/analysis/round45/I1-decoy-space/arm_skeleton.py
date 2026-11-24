"""R45 I1 arm_skeleton: Round 8 SKELETON (C-01) word-length plaintext identification under the decoy conditions.
Uses analysis/skeleton/wordlen_search.py's own corpus_lengths() and FFT scan() unchanged.
Plant: a W-word passage of data/pride.txt is the plaintext; the 'printed' length pattern handed to the scan is
  a = its true lengths, b = true lengths permuted within 53-word pages (LP2 mean words/page), c = LP2's actual printed
  lengths (decoy); d = no spaces -> no pattern exists (power 0 by construction, recorded, not run).
Corpus scanned = pride + moby (data/). Detection = global argmax offset is the planted one AND its count > max of the
same scan over 5 shuffled patterns.   python -I arm_skeleton.py -> out_skeleton.json"""
import os, sys, json, time, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common45 as G
import numpy as np
WS = G._load("wordlen_search", G.AN("skeleton", "wordlen_search.py"))
OUT = os.path.join(HERE, "out_skeleton.json")
NPL, NNULL, PAGE_W = 20, 5, 53


def best(pattern, LENS, slack=0):
    top = (-1, None, None)
    for name, arr in LENS.items():
        r = WS.scan(pattern, arr, slack)
        if r is None: continue
        i = int(np.argmax(r)); v = float(r[i])
        if v > top[0]: top = (v, name, i)
    return top


def run():
    t0 = time.time()
    LENS = {n: WS.corpus_lengths(open(os.path.join(G.LP, "data", n), encoding="utf-8", errors="ignore").read()) for n in ("pride.txt", "moby.txt")}
    lp, _ = WS.lp2_words()
    res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "corpus_words": {k: int(len(v)) for k, v in LENS.items()}, "cells": {}}
    if os.path.exists(OUT):
        res["cells"] = json.load(open(OUT)).get("cells", {})           # resume
    for W in (120, 400):
        if "W%d" % W in res["cells"]:
            continue
        rows = []
        for s in range(NPL):
            open(os.path.join(HERE, "heartbeat.txt"), "w").write("%s arm_skeleton W%d plant %d\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), W, s))
            rng = random.Random(45800 + 97 * W + s)
            off = rng.randrange(len(LENS["pride.txt"]) // 20, len(LENS["pride.txt"]) - W - 1)
            true = LENS["pride.txt"][off:off + W].copy()
            pats = {"a": true}
            b = true.copy()
            for k in range(0, W, PAGE_W):
                seg = b[k:k + PAGE_W].copy(); rng.shuffle(seg); b[k:k + PAGE_W] = seg
            pats["b"] = b
            st = rng.randrange(0, len(lp) - W)
            pats["c"] = lp[st:st + W].astype(np.int16)
            row = {"seed": s, "offset": off}
            for cond, pat in pats.items():
                v, name, i = best(pat, LENS)
                nulls = []
                for q in range(NNULL):
                    sh = pat.copy(); np.random.default_rng(1000 * s + q).shuffle(sh)
                    nulls.append(best(sh, LENS)[0])
                hit = bool(name == "pride.txt" and i == off and v > max(nulls))
                row[cond] = {"best": v, "where": [name, i], "true_count": float(WS.scan(pat, LENS["pride.txt"], 0)[off]),
                             "null_max": max(nulls), "detected": hit}
            rows.append(row)
        cell = {"W": W, "n": NPL, "cond": {}}
        for cond in ("a", "b", "c"):
            k = sum(r[cond]["detected"] for r in rows)
            cell["cond"][cond] = {"power": k / NPL, "wilson": G.wilson(k, NPL),
                                  "median_true_count_frac": float(np.median([r[cond]["true_count"] / W for r in rows])),
                                  "median_null_max_frac": float(np.median([r[cond]["null_max"] / W for r in rows]))}
        cell["cond"]["d"] = {"power": 0.0, "note": "no spaces -> no length pattern; instrument cannot run"}
        cell["rows"] = rows
        res["cells"]["W%d" % W] = cell
        print("W", W, {c: cell["cond"][c]["power"] for c in "abcd"}, "%.0fs" % (time.time() - t0), flush=True)
        json.dump(res, open(OUT, "w"), indent=1)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    run()
