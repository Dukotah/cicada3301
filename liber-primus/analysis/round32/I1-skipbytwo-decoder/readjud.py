"""Round 32 / I1 -- bounded re-adjudication (PREREG s5 + Addendum A).

    python readjud.py control      # plant at offset 1000 under skip_by_two, scan offsets 0..3301
    python readjud.py real [sign]  # LP2 page-0 head (120 runes) x sha256_ctr(CICADA3301), advance=2
    python readjud.py real_free    # advance="free", offsets 0..9, both signs, atbash 0/1
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import beam_v2 as B
sys.path.insert(0, os.path.join(B.LP, "analysis", "round13", "B04"))
import lib_numchannel as nc
import plant as PL
import run_envelope as R

FLAG = 10.0
MAXOFF = 3301
L = 120


def key():
    return PL.make_key("sha256_ctr", length=MAXOFF + L * 12 + 400, seed=b"CICADA3301")


def atbash(C):
    return [(28 - c) % 29 for c in C]


def scan(C, K, signs, offs, dec, out, tag):
    rows = []
    t0 = time.time()
    best = None
    for sg in signs:
        for o in offs:
            bd = B.beam_decode_v2(C, K, dec, sign=sg, o=o, want_path=True)
            a = R.adj(bd["plain_idx"])
            row = [sg, o, a["pmax"], a["pmax_ne"], a["en"], a["preg"]]
            rows.append(row)
            if best is None or a["pmax"] > best[2]:
                best = row
        print(tag, "sign", sg, "done", round(time.time() - t0), "best", best, flush=True)
    pm = np.array([r[2] for r in rows])
    res = {"tag": tag, "dec": dec, "n_decodes": len(rows), "flag": FLAG,
           "n_flagged": int((pm > FLAG).sum()), "best": best,
           "flagged": [r for r in rows if r[2] > FLAG][:20],
           "pmax_quantiles": {str(q): float(np.quantile(pm, q)) for q in (0.5, 0.99, 0.999)},
           "pmax_max": float(pm.max()), "sec": round(time.time() - t0, 1)}
    json.dump(res, open(out, "w"), indent=1)
    return res


if __name__ == "__main__":
    mode = sys.argv[1]
    K = key()
    if mode == "control":
        P = R.plain("EN_MODERN", L, 77)
        C, info = B.encipher_skip_by_two(P, K[1000:], 0.83, 3301)
        # planted at offset 1000; decode sign -1 (c = p + k)
        r = scan(C, K, [-1], range(0, MAXOFF + 1), 2, os.path.join(HERE, "out_readjud_control.json"), "control")
        print({k: r[k] for k in ("n_flagged", "best", "pmax_max", "flagged")})
    elif mode == "real":
        C = nc.segments()[0][:L]
        sg = int(sys.argv[2])
        r = scan(C, K, [sg], range(0, MAXOFF + 1), 2,
                 os.path.join(HERE, "out_readjud_real_s%+d.json" % sg), "real_s%+d" % sg)
        print({k: r[k] for k in ("n_flagged", "best", "pmax_max", "flagged")})
    elif mode == "real_free":
        C0 = nc.segments()[0][:L]
        res = {}
        for ab in (0, 1):
            C = atbash(C0) if ab else C0
            r = scan(C, K, [-1, 1], range(0, 10), "free",
                     os.path.join(HERE, "out_readjud_free_ab%d.json" % ab), "free_ab%d" % ab)
            res[ab] = {k: r[k] for k in ("n_flagged", "best", "pmax_max")}
        print(res)
