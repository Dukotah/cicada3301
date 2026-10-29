"""B3 completion: decode the remainder of the Random(3301) permutation, append to readjud_rows.jsonl, rebuild summary."""
import sys, json, time, random
sys.argv = ["x"]
import readjud as R
import numpy as np

uni = R.load_universe()
order = list(range(len(uni)))
random.Random(3301).shuffle(order)
rows_path = R.OUT("readjud_rows.jsonl")
old = []
with open(rows_path, encoding="utf-8") as f:
    f.readline()
    for line in f:
        line = line.strip()
        if line:
            old.append(json.loads(line))
n0 = len(old)
assert old[0][0] == "v3:" + uni[order[0]] and old[-1][0] == "v3:" + uni[order[n0 - 1]], "order mismatch"
stats, keep, allp = {}, [], {"keyskip1": [], "keyskip2": []}


def acc(kid, pm, preg):
    s, f, sd, rel = R.parse(kid)
    st = stats.setdefault(s + "|" + rel, {"n": 0, "max": -1e9, "best_kid": None, "best_preg": None})
    st["n"] += 1
    if pm > st["max"]:
        st["max"], st["best_kid"], st["best_preg"] = pm, kid, R.PAN.registers[preg]
    allp[rel].append(pm)
    if pm >= 4.5:
        keep.append((pm, kid))


for r in old:
    acc(r[0][3:], r[3], r[4])
R.log("resume: existing rows", n0, "remaining", len(uni) - n0)
t0 = time.time()
cache = (None, None)
with open(rows_path, "a", encoding="utf-8") as out:
    for i, ix in enumerate(order[n0:]):
        kid = uni[ix]
        s, f, sd, rel = R.parse(kid)
        if cache[0] != (s, f, sd):
            cache = ((s, f, sd), R.keystream((s, f, sd)))
        d, a = R.decode(R.CS, cache[1], rel)
        out.write(json.dumps(R.AD.to_row(a, "v3:" + kid)) + "\n")
        acc(kid, float(a["pmax"]), a["preg"])
        if i % 20000 == 19999:
            out.flush()
            R.log("resume", n0 + i + 1, "%.0f dec/s" % ((i + 1) / (time.time() - t0)))
        if time.time() - t0 > 1100:
            R.log("TIME CAP hit at", n0 + i + 1)
            break
nl = json.load(open(R.OUT("null_v3.json")))
ctl = json.load(open(R.OUT("control.json")))
rr = {"n_done": sum(v["n"] for v in stats.values()), "elapsed_s": round(time.time() - t0, 1), "stats": stats,
      "keep": sorted(keep, reverse=True)[:400], "allp": allp}
# bars of record are the fitted ones from the 12,000-draw null at N~1.2e5 (not enlarged, not refit at the new N)
old_s = json.load(open(R.OUT("readjud_summary.json")))
fixed = {r: old_s["bars"][r]["bar"] for r in ("keyskip1", "keyskip2")}
R.bar_at = lambda nlr, N, alpha=0.01: (fixed["keyskip1"] if nlr is nl["rels"]["keyskip1"] else fixed["keyskip2"],) * 2
summ = R.finalize(uni, ctl, nl, rr)
summ["bar_note"] = "bars of record = POT fit to the 12,000-draw v3 null at N~1.2e5, MODELLED, extrapolated ~10x past the null; not re-fit at N=%d" % rr["n_done"]
summ["earlier_partial_run"] = {"rows": n0, "fraction": round(n0 / len(uni), 4)}
json.dump(summ, open(R.OUT("readjud_summary.json"), "w"), indent=1)
R.log("done", rr["n_done"], json.dumps({k: (v["fraction"], v["best_pmax"], v["clears"]) for k, v in summ["coverage"].items()}), "flagged", len(summ["flagged"]))
