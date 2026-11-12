"""R44/W2-A4 — the pre-registered sweep (tier A + tier B) over the real unsolved corpus.

Refuses to run unless gate.json says passed (PREREG Q5).  Writes results.json.
Pure python3 + numpy, no network.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chained as CH                              # noqa: E402

LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
import adjudicate as A                            # noqa: E402

PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


def r3_stats(full):
    return {k: (round(float(full[k]), 4) if isinstance(full[k], (int, float, np.floating))
                else full[k]) for k in ("pmax", "preg", "pmax_ne", "ioc", "mds", "h2", "zl",
                                        "en", "degenerate") if k in full}


def main():
    t0 = time.time()
    gate = json.load(open(os.path.join(HERE, "gate.json")))
    if not gate.get("passed"):
        print("GATE NOT PASSED — INSTRUMENT-INCOMPLETE; refusing to sweep (PREREG Q5).")
        sys.exit(1)

    corpus = CH.load_corpus()
    assert CH.collapse_lemma_check(corpus["chans"])
    pages, lens, chans = corpus["pages"], corpus["lens"], corpus["chans"]

    out = {"n_bar": CH.N_BAR, "bars": CH.BARS, "tierA": {"pages": [], "crossers": []},
           "tierB": {}, "verdict": None}

    # ------------------------------------------------ tier A: 16 variants x 29 o x 55 pages
    total = 0
    gbest = {"pmax": -99.0}
    for pi in range(55):
        bar = CH.bar_for(lens[pi])
        rows, meta = [], []
        for (s1, s2, k, sc) in CH.tierA_variants():
            rows.append(CH.decode_page_grid(pages, pi, s1, s2, k, sc))
            meta.extend((s1, s2, k, sc, o) for o in range(CH.N))
        X = np.concatenate(rows, axis=0)
        r = A.adjudicate_batch(X, pan=PAN)
        total += X.shape[0]
        pm = r["pmax"]
        i = int(pm.argmax())
        s1, s2, k, sc, o = meta[i]
        best = dict(page=pi, L=int(lens[pi]), bar=bar, pmax=float(pm[i]),
                    preg=int(r["preg"][i]), s1=s1, s2=s2, k=k, scope=sc, o=o)
        full = A.adjudicate(X[i], pan=PAN)
        best["stats"] = r3_stats(full)
        out["tierA"]["pages"].append(best)
        if best["pmax"] > gbest["pmax"]:
            gbest = best
        for j in np.nonzero(pm >= bar)[0]:
            fj = A.adjudicate(X[int(j)], pan=PAN)
            if not fj["degenerate"] and fj["pmax"] >= bar:
                s1, s2, k, sc, o = meta[int(j)]
                members = [dict(ch=ch, f=f, sig3=g3, s=s)
                           for ch in CH.CHANNELS for f in CH.FS for g3 in CH.SIG3S
                           for s in CH.SHIFTS
                           if int(CH.offsets_for(dict(ch=ch, f=f, sig3=g3, s=s),
                                                 chans)[pi]) == o]
                out["tierA"]["crossers"].append(
                    dict(page=pi, L=int(lens[pi]), bar=bar, pmax=float(fj["pmax"]),
                         preg=int(fj["preg"]), s1=s1, s2=s2, k=k, scope=sc, o=o,
                         stats=r3_stats(fj), family_members=members,
                         decode=X[int(j)].tolist()))
    out["tierA"]["n_cells"] = total
    out["tierA"]["best"] = gbest

    # ------------------------------------------------ tier B: 13,920 thetas on head-729
    thetas = CH.tierB_thetas()
    uniq = {}
    for th in thetas:
        ov = CH.offsets_for(th, chans)
        key = (th["s1"], th["s2"], th["k"], th["scope"], int(ov[0]), int(ov[1]), int(ov[2]))
        uniq.setdefault(key, []).append(th)
    Xs, keys = [], []
    for key in uniq:
        s1, s2, k, sc, a, b, c = key
        Xs.append(CH.decode_head(pages, lens, s1, s2, k, sc, [a, b, c]))
        keys.append(key)
    X = np.stack(Xs)
    r = A.adjudicate_batch(X, pan=PAN)
    total += X.shape[0]
    pm = r["pmax"]
    i = int(pm.argmax())
    fullB = A.adjudicate(X[i], pan=PAN)
    bkey = keys[i]
    out["tierB"] = {"n_thetas": len(thetas), "n_unique": len(keys), "L": 729,
                    "bar": CH.BARS[729],
                    "best": dict(key=list(bkey), pmax=float(pm[i]), preg=int(r["preg"][i]),
                                 stats=r3_stats(fullB),
                                 thetas=uniq[bkey][:6]),
                    "crossers": []}
    for j in np.nonzero(pm >= CH.BARS[729])[0]:
        fj = A.adjudicate(X[int(j)], pan=PAN)
        if not fj["degenerate"] and fj["pmax"] >= CH.BARS[729]:
            out["tierB"]["crossers"].append(
                dict(key=list(keys[int(j)]), pmax=float(fj["pmax"]), preg=int(fj["preg"]),
                     stats=r3_stats(fj), thetas=uniq[keys[int(j)]],
                     decode=X[int(j)].tolist()))

    nA, nB = len(out["tierA"]["crossers"]), len(out["tierB"]["crossers"])
    assert total <= CH.N_BAR, total
    out["n_total_adjudicated"] = total
    out["verdict"] = ("FLAGGED-FOR-ORACLE (%d tierA + %d tierB crossers)" % (nA, nB)
                      if nA or nB else "NEGATIVE")
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("cells", total, "verdict", out["verdict"], "in", out["seconds"], "s")
    print("tierA best:", json.dumps(gbest))
    print("tierB best:", json.dumps(out["tierB"]["best"])[:400])


if __name__ == "__main__":
    main()
