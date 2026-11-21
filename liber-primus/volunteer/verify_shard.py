#!/usr/bin/env python3
"""Recheck a submitted shard result. Exit 0 = consistent, 1 = mismatch/tampered, 2 = cannot
verify on this machine (a gate failed here).

    python verify_shard.py results/S2-007.json [more.json ...] [--k 32] [--kc 16] [--rng-seed N]
                           [--pr-shards path/to/pr/shards.json]

Checks, per file:
  * static: shard id/range/lane match shards.json; engine pins and thresholds match the lane;
    result_sha256 recomputes; n_scored == range size == histogram total; candidates unique,
    sorted, inside the range, all >= cand_bar; counts, above_bar, top_k and best consistent.
  * missing-stretch check: no run of >40 expected candidate spacings without a candidate.
  * re-score with the stock engine (after the same gates run_shard uses): every above-bar seed,
    every top-k seed, --kc random candidates, and --k uniformly random seeds from the range.
    Reported scores must match to the last bit. A random seed that scores >= cand_bar must be
    in the candidate list with the same pmax; one that scores below must not be. Then re-sweep
    --windows random whole windows; the candidate set inside each must match exactly.
The default is a probabilistic spot check, not a proof. --full re-sweeps the whole range and
requires identical candidates and histogram: that IS a proof (about 20-45 min per shard on 2 cores).
"""
import argparse
import json
import random
import sys
from pathlib import Path

import _kit as K


def static_checks(res, db, path, errs):
    sid = res.get("shard_id")
    if Path(path).stem != sid:
        errs.append("file name %s does not match shard_id %s" % (Path(path).name, sid))
    try:
        shard = K.shard_by_id(db, sid)
    except K.KitError as e:
        errs.append(str(e))
        return None, None
    lane = db["lanes"][shard["lane"]]
    if res.get("lane") != shard["lane"]:
        errs.append("lane %r != shard lane %r" % (res.get("lane"), shard["lane"]))
    lo, hi = shard["from"], shard["to"]
    if res.get("range") != [lo, hi]:
        errs.append("range %r != shard range [%d, %d]" % (res.get("range"), lo, hi))
    for k in ("relation", "reducer", "offset", "sign"):
        if res.get(k) != lane[k]:
            errs.append("%s %r != lane %r" % (k, res.get(k), lane[k]))
    if res.get("engine_source_sha256") != lane["engine_source_sha256"]:
        errs.append("engine_source_sha256 differs from the pinned instrument")
    if res.get("threshold") != {"cand_bar": lane["cand_bar"], "claim_bar": lane["claim_bar"]}:
        errs.append("threshold %r differs from lane bars" % res.get("threshold"))
    missing = [k for k in K.CANON_FIELDS if k not in res]
    if missing:
        errs.append("missing fields: %s" % missing)
        return shard, lane
    if K.canonical_sha(res) != res.get("result_sha256"):
        errs.append("result_sha256 does not recompute (file edited after it was written)")
    n = hi - lo
    if res["n_scored"] != n:
        errs.append("n_scored %d != range size %d" % (res["n_scored"], n))
    hist = {int(b): v for b, v in res["histogram_0p01"].items()}
    if sum(hist.values()) != n:
        errs.append("histogram total %d != range size %d" % (sum(hist.values()), n))
    cand = res["candidates"]
    seeds = [c[0] for c in cand]
    if seeds != sorted(set(seeds)):
        errs.append("candidates not sorted/unique by seed")
    if any(not (lo <= s < hi) for s in seeds):
        errs.append("candidate seed outside the shard range")
    if any(p < lane["cand_bar"] for _, p in cand):
        errs.append("candidate below cand_bar")
    if res["n_candidates"] != len(cand):
        errs.append("n_candidates %d != %d rows" % (res["n_candidates"], len(cand)))
    hmass = sum(v for b, v in hist.items() if b >= int(round(lane["cand_bar"] * 100)))
    if hmass < len(cand):
        errs.append("histogram mass >= cand_bar (%d) < number of candidates (%d)" % (hmass, len(cand)))
    above = sorted([s, p] for s, p in cand if p >= lane["claim_bar"])
    if res["above_bar"] != above or res["n_above_bar"] != len(above):
        errs.append("above_bar / n_above_bar inconsistent with the candidate list")
    if res.get("flagged_for_oracle") != bool(above):
        errs.append("flagged_for_oracle inconsistent")
    # missing-stretch check: candidates (pmax >= 5.0) arrive at ~1.1e-4 per seed, uniformly. A gap of
    # 40 expected spacings has probability ~e^-40 under honest sweeping; it means part of the range was skipped.
    rate = lane.get("candidate_rate")
    if rate and n >= 1000000:
        edges = [lo] + seeds + [hi]
        gap = max(b - a for a, b in zip(edges, edges[1:]))
        if gap > 40.0 / rate:
            errs.append("a stretch of %d seeds has no candidates (expected spacing %.0f): part of the range "
                        "looks unswept" % (gap, 1 / rate))
    top = res["top_k"]
    if top != sorted(top, key=lambda r: (-r[1], r[0])):
        errs.append("top_k not sorted by pmax desc")
    cmap = dict((s, p) for s, p in cand)
    want = sorted(cmap.items(), key=lambda kv: (-kv[1], kv[0]))[:K.TOP_K]
    if [list(x) for x in want] != top[:len(want)]:
        errs.append("top_k does not match the highest candidates")
    for s, p in top:
        if not (lo <= s < hi):
            errs.append("top_k seed %d outside range" % s)
        if p >= lane["cand_bar"] and cmap.get(s) != p:
            errs.append("top_k seed %d (%r) not in candidates with the same pmax" % (s, p))
    if top and res["best"] != top[0]:
        errs.append("best != top_k[0]")
    return shard, lane


def rescore_checks(res, shard, lane, bdir, rng, k, kc, windows, wsize, threads, errs):
    lo, hi = shard["from"], shard["to"]
    cmap = dict((s, p) for s, p in res["candidates"])
    reported = {}
    for s, p in res["above_bar"] + res["top_k"]:
        reported[s] = p
    pool = sorted(cmap)
    for s in rng.sample(pool, min(kc, len(pool))):
        reported[s] = cmap[s]
    uniform = set()
    while len(uniform) < min(k, hi - lo):
        uniform.add(rng.randrange(lo, hi))
    scores = K.score_seeds(bdir, lane, list(reported) + list(uniform))
    bad = 0
    for s, p in sorted(reported.items()):
        if scores[s] != p:
            errs.append("seed %d: reported %r, re-scored %r" % (s, p, scores[s]))
            bad += 1
    hist = {int(b): v for b, v in res["histogram_0p01"].items()}
    for s in sorted(uniform):
        q = scores[s]
        if q >= lane["cand_bar"]:
            if cmap.get(s) != q:
                errs.append("random seed %d scores %r >= cand_bar but is missing/different in candidates" % (s, q))
                bad += 1
        elif s in cmap:
            errs.append("random seed %d scores %r < cand_bar but is listed as a candidate" % (s, q))
            bad += 1
        b = min(max(int(q * 100.0), 0), K.HIST_BINS - 1)
        if hist.get(b, 0) < 1:
            errs.append("random seed %d falls in histogram bin %d which the result reports empty" % (s, b))
            bad += 1
    # whole-window re-sweeps: inside each random window the candidate set must match exactly
    nwin = 0
    for _ in range(windows):
        size = min(wsize, hi - lo)
        a = rng.randrange(lo, hi - size + 1)
        got, _h = K.sweep_window(bdir, lane, a, a + size, threads)
        want = {s: p for s, p in cmap.items() if a <= s < a + size}
        nwin += size
        if got != want:
            miss = sorted(set(got) - set(want))[:5]
            extra = sorted(set(want) - set(got))[:5]
            diff = sorted(s for s in set(got) & set(want) if got[s] != want[s])[:5]
            errs.append("window [%d, %d): candidate set differs (missing from result %s, not real %s, "
                        "score differs %s)" % (a, a + size, miss, extra, diff))
            bad += 1
    return len(reported), len(uniform), nwin, bad


def check_pr_shards(trusted, pr, results, errs):
    """A PR may only change status/claimant/result; ranges, lanes and pins are immutable."""
    t = {s["id"]: s for s in trusted["shards"]}
    p = {s["id"]: s for s in pr["shards"]}
    if set(t) != set(p):
        errs.append("PR shards.json adds or removes shard ids")
    for sid, s in p.items():
        if sid in t:
            a = {k: v for k, v in t[sid].items() if k not in ("status", "claimant", "result")}
            b = {k: v for k, v in s.items() if k not in ("status", "claimant", "result")}
            if a != b:
                errs.append("PR changes immutable fields of shard %s" % sid)
    if trusted["lanes"] != pr["lanes"]:
        errs.append("PR changes lane definitions (pins/bars/controls) in shards.json")
    for path in results:
        sid = Path(path).stem
        s = p.get(sid)
        if s and (s["status"] != "done" or s.get("result") != "results/%s.json" % sid):
            errs.append("shard %s: PR adds a result but shards.json does not mark it done with result results/%s.json"
                        % (sid, sid))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--k", type=int, default=32, help="uniform random seeds to re-score")
    ap.add_argument("--kc", type=int, default=16, help="random candidate seeds to re-score")
    ap.add_argument("--windows", type=int, default=8, help="random whole windows to re-sweep")
    ap.add_argument("--window-size", type=int, default=32768)
    ap.add_argument("--threads", type=int, default=K.default_threads())
    ap.add_argument("--rng-seed", type=int, default=None, help="reproducible sample (default: unpredictable)")
    ap.add_argument("--shards", default=None, help="trusted shards.json (default: the one next to this script)")
    ap.add_argument("--pr-shards", default=None, help="the PR's shards.json, checked against the trusted one")
    ap.add_argument("--full", action="store_true",
                    help="re-sweep the WHOLE range and require identical candidates + histogram (a proof, not a spot check)")
    ap.add_argument("--no-rescore", action="store_true", help="static checks only")
    a = ap.parse_args()

    db = K.load_shards(a.shards)
    rng = random.Random(a.rng_seed) if a.rng_seed is not None else random.SystemRandom()
    failed = False
    if a.pr_shards:
        errs = []
        check_pr_shards(db, K.load_shards(a.pr_shards), a.results, errs)
        for e in errs:
            print("FAIL shards.json: " + e)
        failed |= bool(errs)

    built = {}
    for path in a.results:
        errs = []
        try:
            res = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print("FAIL %s: unreadable JSON: %s" % (path, e))
            failed = True
            continue
        shard, lane = static_checks(res, db, path, errs)
        line = "static checks"
        if shard and not errs and not a.no_rescore:
            lid = shard["lane"]
            if lid not in built:
                bdir = K.build_engine(lid, lane, quiet=True)
                ok, gates = K.run_gates(bdir, lane)
                if not ok:
                    print(json.dumps(gates, indent=1))
                    print("CANNOT VERIFY: a gate failed on THIS machine; the verifier is broken, not the result.")
                    return 2
                built[lid] = bdir
            if a.full:
                lo, hi = shard["from"], shard["to"]
                got, hist = K.sweep_window(built[lid], lane, lo, hi, a.threads)
                want = dict((s_, p_) for s_, p_ in res["candidates"])
                wh = {int(b_): v_ for b_, v_ in res["histogram_0p01"].items()}
                if got != want:
                    errs.append("full re-sweep: candidate set differs (%d real vs %d reported; missing %s)"
                                % (len(got), len(want), sorted(set(got) - set(want))[:10]))
                if {i: v for i, v in enumerate(hist) if v} != wh:
                    errs.append("full re-sweep: histogram differs")
                print("  full re-sweep of %d seeds done" % (hi - lo))
            nrep, nuni, nwin, bad = rescore_checks(res, shard, lane, built[lid], rng, a.k, a.kc,
                                                   a.windows, a.window_size, a.threads, errs)
            line = ("re-scored %d reported + %d uniform seeds, re-swept %d seeds in %d windows, %d mismatches"
                    % (nrep, nuni, nwin, a.windows, bad))
        if errs:
            failed = True
            print("FAIL %s (%s)" % (path, line))
            for e in errs[:40]:
                print("  - " + e)
        else:
            flag = "  FLAGGED-FOR-ORACLE: %d above claim bar" % res["n_above_bar"] if res["n_above_bar"] else ""
            print("PASS %s: %s; n_scored %d, candidates %d, best %s%s"
                  % (path, line, res["n_scored"], res["n_candidates"], res["best"], flag))
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except K.KitError as e:
        print("ERROR: %s" % e)
        sys.exit(2)
