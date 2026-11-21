#!/usr/bin/env python3
"""Run one volunteer shard end to end.

    python run_shard.py <shard-id> [--threads N] [--force]
    python run_shard.py --gates-only            # build + gates, no sweep (smoke check)

Steps: verify the engine inputs against the sha256 pins in shards.json -> build the
committed C engine (unmodified) -> run the gates (panel gate, V1/V2 self-test, the Round 38
exact-relation planted control reproduced to the last digit, the anchor seed) and REFUSE to
sweep if any fails -> sweep the shard range -> write results/<shard-id>.json.

If a run is interrupted, just re-run: the shard starts over (shards are sized at under ~2 h
on one core, and a fresh run keeps the histogram exact).
"""
import argparse
import datetime
import json
import sys
import time

import _kit as K


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shard", nargs="?")
    ap.add_argument("--threads", type=int, default=K.default_threads())
    ap.add_argument("--force", action="store_true", help="overwrite an existing results/<id>.json")
    ap.add_argument("--gates-only", action="store_true")
    ap.add_argument("--shards", default=None, help="alternate shards.json (testing only)")
    a = ap.parse_args()

    db = K.load_shards(a.shards)
    if a.gates_only:
        lane_id = "S2"
    else:
        if not a.shard:
            ap.error("shard id required (see shards.json / SHARDS.md)")
        shard = K.shard_by_id(db, a.shard)
        lane_id = shard["lane"]
    lane = db["lanes"][lane_id]

    K.log("[1/4] build (engine inputs checked against sha256 pins)")
    bdir = K.build_engine(lane_id, lane)
    K.log("      binary sha256 %s" % K.binary_sha(bdir)[:16])

    K.log("[2/4] gates: panel gate, self-test, exact-relation planted control, anchor seed")
    ok, gates = K.run_gates(bdir, lane, threads=min(a.threads, 4))
    for name, rec in gates.items():
        K.log("      %-14s %s" % (name, "PASS" if rec["pass"] else "FAIL"))
    if not ok:
        K.log(json.dumps(gates, indent=1))
        K.log("REFUSING TO SWEEP: a gate failed. A broken instrument produces a fake null. "
              "Do not submit anything; open an issue with the output above.")
        return 2
    if a.gates_only:
        K.log("gates PASS (no sweep requested)")
        return 0

    sid = shard["id"]
    is_test = shard["status"] == "test"
    out_dir = K.RUNS_DIR / "test-results" if is_test else K.RESULTS_DIR   # test output is never submitted
    out = out_dir / ("%s.json" % sid)
    if out.exists() and not a.force:
        K.log("%s already exists; use --force to redo" % out)
        return 1
    lo, hi = shard["from"], shard["to"]
    run_dir = K.RUNS_DIR / sid
    K.rmtree(run_dir)                                   # always a fresh run (see docstring)
    K.log("[3/4] sweep %s [%d, %d) = %d seeds on %d threads" % (sid, lo, hi, hi - lo, a.threads))
    t0, started = time.time(), utcnow()
    r = K.run_plan(bdir, run_dir, [K.plan_lane("S2", lane, lo, hi)], a.threads)
    wall = time.time() - t0
    (run_dir / "engine.log").write_text(r.stdout + r.stderr)
    if r.returncode != 0:
        K.log(r.stdout[-3000:] + r.stderr[-3000:])
        K.log("engine exited rc=%d; nothing written" % r.returncode)
        return 3
    st = json.loads((run_dir / "STATUS.json").read_text())
    covered = sum(w["cursor"] - w["band_start"] for w in st["workers"])
    if "S2" not in st["lanes_completed"] or covered != hi - lo or not all(w["done"] for w in st["workers"]):
        K.log("engine did not complete the range (covered %d of %d); nothing written" % (covered, hi - lo))
        return 3

    K.log("[4/4] collect results")
    cands = {}
    for ln in (run_dir / "candidates.jsonl").read_text().splitlines():
        if not ln.strip():
            continue
        c = json.loads(ln)
        s, p = int(c["seed"]), float(c["pmax"])
        if s in cands and cands[s] != p:
            raise K.KitError("seed %d written twice with different pmax" % s)
        cands[s] = p
    hist = K.read_hist(run_dir, "S2")
    if sum(hist) != hi - lo:
        raise K.KitError("histogram total %d != range size %d" % (sum(hist), hi - lo))
    pool = dict(cands)
    for s, p in K.read_top(run_dir, "S2"):
        pool.setdefault(s, p)
    top = sorted(pool.items(), key=lambda kv: (-kv[1], kv[0]))[:K.TOP_K]
    above = sorted((s, p) for s, p in cands.items() if p >= lane["claim_bar"])

    res = {
        "kit_version": K.KIT_VERSION,
        "shard_id": sid, "lane": lane_id, "range": [lo, hi],
        "relation": lane["relation"], "reducer": lane["reducer"], "offset": lane["offset"], "sign": lane["sign"],
        "engine_source_sha256": lane["engine_source_sha256"],
        "threshold": {"cand_bar": lane["cand_bar"], "claim_bar": lane["claim_bar"]},
        "n_scored": hi - lo,
        "n_candidates": len(cands),
        "n_above_bar": len(above),
        "best": list(top[0]) if top else None,
        "flagged_for_oracle": bool(above),
        "selftest": gates,
        "build": {"binary_sha256": K.binary_sha(bdir), "cflags": " ".join(K.CFLAGS)},
        "wall_time_s": round(wall, 1),
        "seeds_per_s": round((hi - lo) / wall, 1) if wall > 0 else None,
        "started_utc": started, "finished_utc": utcnow(),
        "machine": K.machine_info(a.threads),
        "histogram_0p01": {str(i): v for i, v in enumerate(hist) if v},
        "above_bar": [list(x) for x in above],
        "top_k": [list(x) for x in top],
        "candidates": [[s, cands[s]] for s in sorted(cands)],
    }
    res["result_sha256"] = K.canonical_sha(res)
    out_dir.mkdir(parents=True, exist_ok=True)
    K.write_result(out, res)
    K.log("wrote %s" % out)
    K.log("  n_scored %d  candidates>=%.1f %d  above claim bar %d  best %s  wall %.1fs (%.0f seeds/s)"
          % (res["n_scored"], lane["cand_bar"], res["n_candidates"], res["n_above_bar"], res["best"],
             wall, res["seeds_per_s"] or 0))
    K.log("  result_sha256 %s" % res["result_sha256"])
    if above:
        K.log("\n*** %d seed(s) at/above the claim bar %.6f. This is FLAGGED-FOR-ORACLE, not a solve. ***\n"
              "Noise crossers are expected in a 2^32 sweep (the S1 lane had 3, all adjudicated NOISE-CROSSER).\n"
              "Submit the result as normal and say so in the PR; do not announce anything. See README.md."
              % (len(above), lane["claim_bar"]))
    K.rmtree(run_dir)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except K.KitError as e:
        sys.exit("ERROR: %s" % e)
