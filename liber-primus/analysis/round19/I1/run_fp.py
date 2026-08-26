"""Round 19 / I1 -- G-FP: what permissiveness does to the WRONG-KEY distribution.

The obvious failure mode of a permissive transition relation is that it hands a wrong key
extra degrees of freedom at every rune, so the beam shops for the most English-looking of
them and the whole null drifts upward into the English band.  If that happens the "fix" is
worthless and this lane has to say so.

Two nulls:
  N-synth  wrong sha256_ctr keys against a synthetic encipher_keyskip plant  (L = 240)
  N-real   wrong sha256_ctr keys against segments of the REAL 12,956-rune LP2 stream
           (round11/lib_numchannel.unsolved()).  This is the null Phase 2 actually faces.

    python3 run_fp.py --stage deep    --n 2000
    python3 run_fp.py --stage curve   --n 500
"""
import os
import sys
import json
import time
import math
import random
import argparse
import statistics
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driftbeam as db                                    # noqa: E402
import constructions as cx                                # noqa: E402
from run_gates import MODES, decode                       # noqa: E402

sys.path.insert(0, os.path.join(cx.ROOT, "analysis", "round11"))
sys.path.insert(0, os.path.join(cx.ROOT, "benchmark"))
import lib_numchannel as ncmod                            # noqa: E402
import null as bnull                                      # noqa: E402

L = 240
BEAM_W = 400

DEEP_MODES = ["repo_ms3", "pair_ms8", "drift_l4", "drift_l8", "drift_l16"]
CURVE_MODES = ["exact_ms8", "drift_l0", "drift_l2", "drift_l6",
               "drift_l12", "drift_l24", "drift_mf1", "drift_mf3"]

_LP2 = None


def lp2():
    global _LP2
    if _LP2 is None:
        _LP2 = ncmod.unsolved()
    return _LP2


def synth_ct(seed=0):
    C, K, P, info = cx.build("keyskip", L, seed, {"supp": 0.83}, headroom=6)
    return C, K, P


_CT = {}


def _ct_cached(null):
    if null not in _CT:
        if null == "synth":
            _CT[null] = synth_ct(0)[0]
        else:
            _CT[null] = None
    return _CT[null]


def _one(job):
    null, cfgname, t = job
    if null == "synth":
        C = _ct_cached("synth")
    else:
        S = lp2()
        r = random.Random(555000 + t)
        s = r.randrange(0, len(S) - L - 1)
        C = S[s:s + L]
    K = cx.key_sha(L * 45 + 2048, seed=b"WRONGKEY-%08d" % t)
    res = decode(C, K, cfgname, beam_w=BEAM_W, want_path=False)
    return {"null": null, "mode": cfgname, "trial": t, "score": res["score"],
            "n_skips": res["n_skips"], "n_unexplained": res["n_unexplained"]}


def pct(v, q):
    v = sorted(v)
    if not v:
        return None
    k = min(len(v) - 1, max(0, int(math.ceil(q * len(v))) - 1))
    return v[k]


def run(modes, n, nulls=("synth", "real"), nproc=6, tag="fp"):
    jobs = [(nu, m, t) for nu in nulls for m in modes for t in range(n)]
    print(f"{tag}: {len(jobs)} wrong-key decodes on {nproc} procs", flush=True)
    rows = []
    t0 = time.time()
    with Pool(nproc) as pool:
        for k, r in enumerate(pool.imap_unordered(_one, jobs, chunksize=8)):
            rows.append(r)
            if (k + 1) % 500 == 0:
                print(f"   {k+1}/{len(jobs)} ({time.time()-t0:.0f}s)", flush=True)
    summ = []
    for nu in nulls:
        for m in modes:
            v = [r["score"] for r in rows if r["null"] == nu and r["mode"] == m]
            if not v:
                continue
            summ.append({
                "null": nu, "mode": m, "n": len(v),
                "cfg": MODES[m],
                "mean": statistics.fmean(v), "sd": statistics.pstdev(v),
                "median": statistics.median(v),
                "p90": pct(v, 0.90), "p99": pct(v, 0.99), "max": max(v),
                "frac_over_-5.5": sum(1 for x in v if x >= -5.5) / len(v),
                "fw_bar_at_n": bnull.threshold_for(len(v)),
                "frac_over_fw_bar": sum(1 for x in v
                                        if x >= bnull.threshold_for(len(v))) / len(v),
                "mean_n_skips": statistics.fmean(r["n_skips"] for r in rows
                                                 if r["null"] == nu and r["mode"] == m),
            })
            s = summ[-1]
            print(f"  {nu:6s} {m:11s} n={s['n']:5d} mean {s['mean']:7.3f} "
                  f"sd {s['sd']:.3f} p99 {s['p99']:7.3f} max {s['max']:7.3f} "
                  f"over-5.5 {s['frac_over_-5.5']:.4f}", flush=True)
    return summ, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="deep")
    ap.add_argument("--modes", default=None, help="comma-separated subset of MODES")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--nproc", type=int, default=6)
    a = ap.parse_args()
    if a.modes:
        modes = a.modes.split(",")
    else:
        modes = DEEP_MODES if a.stage == "deep" else CURVE_MODES
    t0 = time.time()
    summ, rows = run(modes, a.n, nproc=a.nproc, tag=a.stage)
    out = os.path.join(HERE, f"out_fp_{a.stage}.json")
    json.dump({"lane": "round19/I1", "stage": "G-FP/" + a.stage, "L": L,
               "beam_w": BEAM_W, "n_per_setting": a.n,
               "wrong_key_family": "sha256_ctr(seed=WRONGKEY-%08d)",
               "elapsed_s": round(time.time() - t0, 1),
               "summary": summ, "rows": rows}, open(out, "w"), indent=1)
    print("wrote", out, f"({time.time()-t0:.0f}s)")
