"""P0's own extra control: measure the dense prefilter's survival rate AT THE REAL SCALE.

`lib_padsweep.control()` plants keystreams in a 1 MB blob -> 1e6 competing offsets, and
measured survival 0.625. This lane's largest pad has 1.19e8 competing offsets. Retention of
the true offset inside a fixed top-400 keep window is a rank statistic, so it MUST get worse
as the number of competitors grows, and quoting the 1 MB number on a 118 MB pad would be
exactly the kind of unmeasured assumption AGENTS.md lesson 1 warns about.

So: plant in `DATA_560.13` itself and measure the rank there.

    python control_at_scale.py [--trials 8]
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import lib_padsweep as L                                  # noqa: E402

PAD = os.path.join(L.ROOT, "analysis", "round12", "A1", "pads", "DATA_560.13")

ap = argparse.ArgumentParser()
ap.add_argument("--trials", type=int, default=8)
ap.add_argument("--pad", default=PAD)
a = ap.parse_args()

t0 = time.time()
blob = open(a.pad, "rb").read()
print("pad %s  %s bytes" % (os.path.basename(a.pad), format(len(blob), ",")), flush=True)
r = L.control(blob=blob, n_trials=a.trials, seed=3301, verbose=True)
r["pad"] = os.path.basename(a.pad)
r["pad_bytes"] = len(blob)
r["competing_offsets"] = len(blob) - L.PREFILTER_LEN
r["elapsed_s"] = round(time.time() - t0, 1)
json.dump(r, open(os.path.join(HERE, "control_at_scale.json"), "w"), indent=2)
print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=2))
print("CONTROL AT SCALE:", "PASS" if r["PASS"] else "FAIL")
