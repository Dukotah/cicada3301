#!/usr/bin/env python3
"""Resume the L2 sweep after the host slept / the background task was killed.

- Keeps every variant with all 56 target rows already in sweep_rows.part1.jsonl
  (74 variants at the point of death; partial b1m10 rows are dropped and re-run).
- Reuses null_calibration.json (nulls are seed-deterministic; no need to re-run).
- Plant control was already validated and re-validated by the aborted second run
  (plant_control.json, HIT=true) — not re-run here.
- Appends remaining variants in the identical row format, then writes the same
  sweep_summary.json keysweep.py would have written, from ALL rows.
"""
import json, os, time, zlib, collections
import keysweep as K
import adjudicate as adj

HERE = os.path.dirname(os.path.abspath(__file__))
PART1 = os.path.join(HERE, "sweep_rows.part1.jsonl")
ROWS = os.path.join(HERE, "sweep_rows.jsonl")

base_rows = [json.loads(l) for l in open(PART1)]
cnt = collections.Counter(r["variant"] for r in base_rows)
done = {v for v, n in cnt.items() if n == len(K.TARGETS)}
keep = [r for r in base_rows if r["variant"] in done]
with open(ROWS, "w") as f:
    for r in keep: f.write(json.dumps(r) + "\n")
print(f"resume: {len(done)} variants kept ({len(keep)} rows); "
      f"{len(K.VARIANTS) - len(done)} to run", flush=True)

bar = json.load(open(os.path.join(HERE, "null_calibration.json")))["family_bar"]
pan = adj.panel()
t0 = time.time()
todo = [(vid, pay) for vid, pay in K.VARIANTS if vid not in done]
nconf1 = None
with open(ROWS, "a") as fout:
    for k, (vid, pay) in enumerate(todo):
        best, nconf, _ = K.battery(pay, K.TARGETS)
        nconf1 = nconf
        for tname, (sc, mode, dec) in best.items():
            a = adj.adjudicate(dec, pan=pan)
            row = {"variant": vid, "target": tname, "score": round(sc, 4), "config": mode,
                   "ioc_n": round(float(a["ioc"]), 4), "min_distinct32": int(a["mds"]),
                   "panel_en": round(float(a["en"]), 4),
                   "best_ne_z": round(float(a["pmax_ne"]), 4),
                   "ne_reg": pan.registers[a["ne_reg"]],
                   "zlib_ratio": round(len(zlib.compress(bytes(dec), 9)) / len(dec), 4),
                   "above_family_bar": bool(sc >= bar),
                   "near_bar": bool(bar > sc >= bar - 0.15)}
            fout.write(json.dumps(row) + "\n")
        fout.flush()
        el = time.time() - t0
        print(f"  resumed {k+1}/{len(todo)} ({vid}), {el:.0f}s, "
              f"ETA {el/(k+1)*(len(todo)-k-1):.0f}s", flush=True)

rows = [json.loads(l) for l in open(ROWS)]
assert len(rows) == len(K.VARIANTS) * len(K.TARGETS), (len(rows),)
lead = sorted(((r["score"], r["variant"], r["target"], r["config"]) for r in rows),
              reverse=True)
hits = [r for r in lead if r[0] >= bar]
near = [r for r in lead if bar > r[0] >= bar - 0.15]
summary = {"variants": len(K.VARIANTS), "targets": len(K.TARGETS),
           "total_configs": len(K.VARIANTS) * (nconf1 or 168972), "family_bar": bar,
           "hits_above_bar": [dict(zip(("score", "variant", "target", "config"), r)) for r in hits],
           "near_bar_within_0.15": [dict(zip(("score", "variant", "target", "config"), r)) for r in near],
           "top20": [dict(zip(("score", "variant", "target", "config"), r)) for r in lead[:20]],
           "resumed": True, "kept_variants": len(done)}
json.dump(summary, open(os.path.join(HERE, "sweep_summary.json"), "w"), indent=1)
print(f"SWEEP DONE: {summary['total_configs']:,} configs across {len(K.VARIANTS)} variants; "
      f"{len(hits)} above family bar {bar:.3f}; {len(near)} near-bar.", flush=True)
for r in lead[:10]:
    print(f"  {r[0]:7.3f}  {r[1]}  {r[2]:16s}  {r[3]}", flush=True)
