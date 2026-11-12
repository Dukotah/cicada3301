"""R44 / P1 — doctrine R3: persist the full language-agnostic statistics (en, ioc, mds, h2,
zl + panel z) for each family's best decode, reconstructed from its recorded cell."""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp  # noqa
import adjudicate as A  # noqa
from readings import affine_block, decode, GENS, N  # noqa

pan = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
res = json.load(open(os.path.join(HERE, "results.json")))
ch = json.load(open(os.path.join(HERE, "channel.json")))
legacy = json.load(open(os.path.join(LP, "analysis", "armada_osint", "redrune", "result.json")))
streams = {"legacy187": [gp.RUNE_TO_IDX[c] for c in legacy["global_red_runes"]],
           "corrected200": ch["corrected"]["idx"], "full213": ch["full"]["idx"]}
txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
S = "".join(c for c in txt if c in gp.RUNE_TO_IDX)
canon = np.array([gp.RUNE_TO_IDX[c] for c in S], dtype=np.int64)


def rebuild(fam, b):
    if fam == "A1":
        x = np.asarray(streams[b["stream"]], dtype=np.int64)
    elif fam == "A2":
        lo_hi, off, bounds = None, 0, [0]
        for c in txt:
            if c in gp.RUNE_TO_IDX:
                off += 1
            elif c == "$":
                bounds.append(off)
        bounds.append(len(S))
        lo, hi = bounds[b["section"]], bounds[b["section"] + 1]
        x = np.asarray([i for p, i in zip(ch["full"]["pos"], ch["full"]["idx"])
                        if lo <= p < hi], dtype=np.int64)
    if fam in ("A1", "A2"):
        v = x[::-1] if b["dir"] == "rev" else x
        return (b["a"] * v + b["s"]) % N
    if fam == "A3":
        redset = set(ch["full"]["pos"])
        black = np.array([v for i, v in enumerate(canon) if i not in redset], dtype=np.int64)
        key = np.asarray(streams[b["stream"]], dtype=np.int64)
        kd = key if b["dir"] == "fwd" else key[::-1]
        kk = kd[(b["rot"] + np.arange(len(black))) % len(kd)]
        return decode(black, kk, b["cfg"])
    if fam == "C":
        seg = txt.split("%")[b["page"]]
        c = np.array([gp.RUNE_TO_IDX[ch_] for ch_ in seg if ch_ in gp.RUNE_TO_IDX],
                     dtype=np.int64)
        K = np.asarray(GENS[b["gen"]](len(c), b["offset"]), dtype=np.int64)
        return decode(c, K, b["cfg"])


for fam in ("A1", "A2", "A3", "C"):
    b = res["families"][fam]["best"]
    x = rebuild(fam, b)
    full = A.adjudicate(np.asarray(x, dtype=np.int64), pan=pan)
    assert abs(full["pmax"] - b["pmax"]) < 1e-6, (fam, full["pmax"], b["pmax"])
    res["families"][fam]["best_full_stats"] = {k: full[k] for k in
                                               ("n", "en", "pmax", "preg", "pmax_ne", "pcon",
                                                "ioc", "mds", "h2", "zl", "degenerate")}
    print(fam, json.dumps(res["families"][fam]["best_full_stats"]))

json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
print("updated results.json")
