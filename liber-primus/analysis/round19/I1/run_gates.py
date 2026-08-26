"""Round 19 / I1 -- G-BASE, G-FIX, G-COST measurement harness.

Every construction, every decoder mode, correct key supplied, English plaintext pinned.
7 seeds per cell; medians reported with min/max.  Recovery is on RUNE INDICES.

    python3 run_gates.py --stage fix       # the power envelope (out_fix.json)
    python3 run_gates.py --stage base      # baseline no-regression (out_base.json)
    python3 run_gates.py --stage book      # L = 12,956 full-book control (out_book.json)
    python3 run_gates.py --stage all
"""
import os
import sys
import json
import time
import argparse
import statistics
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driftbeam as db                                    # noqa: E402
import constructions as cx                                # noqa: E402

BAR_SCORE = -5.5
BAR_REC = 0.90
NSEED = 7
BEAM_W = 400


# ------------------------------------------------------------------- decoder modes
MODES = {
    # the repo's instrument, verbatim (G-EQ proves this IS skipdecode.beam_decode)
    "repo_ms3":   dict(mode="keyskip1", max_skip=3,      max_free=0, lam=0.0,  start_slack=0),
    "exact_ms8":  dict(mode="keyskip1", max_skip=8,      max_free=0, lam=0.0,  start_slack=0),
    "exact_auto": dict(mode="keyskip1", max_skip="auto", max_free=0, lam=0.0,  start_slack=0),
    "pair_ms8":   dict(mode="keyskip2", max_skip=8,      max_free=0, lam=0.0,  start_slack=0),
    "drift_l0":   dict(mode="permissive", max_skip="auto", max_free=2, lam=0.0,  start_slack=2),
    "drift_l2":   dict(mode="permissive", max_skip="auto", max_free=2, lam=2.0,  start_slack=2),
    "drift_l4":   dict(mode="permissive", max_skip="auto", max_free=2, lam=4.0,  start_slack=2),
    "drift_l6":   dict(mode="permissive", max_skip="auto", max_free=2, lam=6.0,  start_slack=2),
    "drift_l12":  dict(mode="permissive", max_skip="auto", max_free=2, lam=12.0, start_slack=2),
    "drift_l24":  dict(mode="permissive", max_skip="auto", max_free=2, lam=24.0, start_slack=2),
    "drift_l8":   dict(mode="permissive", max_skip="auto", max_free=2, lam=8.0,  start_slack=2),
    "drift_l16":  dict(mode="permissive", max_skip="auto", max_free=2, lam=16.0, start_slack=2),
    "drift_mf1":  dict(mode="permissive", max_skip="auto", max_free=1, lam=8.0,  start_slack=1),
    "drift_mf3":  dict(mode="permissive", max_skip="auto", max_free=3, lam=8.0,  start_slack=3),
    # the recommended Phase-2 configuration, and two wider-max_free probes of the bound
    "drift_rec":  dict(mode="permissive", max_skip="auto", max_free=2, lam=12.0, start_slack=2),
    "drift_mf6":  dict(mode="permissive", max_skip="auto", max_free=6, lam=12.0, start_slack=6),
    "drift_mf10": dict(mode="permissive", max_skip="auto", max_free=10, lam=12.0, start_slack=10),
}


def max_run(K, upto=None):
    """Longest constant run in the keystream (the low-entropy-pad diagnostic)."""
    best = cur = 1
    n = len(K) if upto is None else min(len(K), upto)
    for i in range(1, n):
        if K[i] == K[i - 1]:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 1
    return best


def suggest_max_skip(K, L, floor_ms=40):
    """Recommended `max_skip`: big enough to cross the longest constant run in the pad.

    On a high-entropy pad the histogram break makes a large `max_skip` free, so this only
    ever costs anything on exactly the pads (constant runs) where it is needed."""
    r = max_run(K, upto=min(len(K), 12 * L + 4096))
    return max(floor_ms, 2 * r + 8)


def decode(C, K, cfgname, beam_w=BEAM_W, want_path=True, sign=-1, o=0):
    cfg = dict(MODES[cfgname])
    if cfg["max_skip"] == "auto":
        cfg["max_skip"] = suggest_max_skip(K, len(C))
    return db.beam_decode(C, K, sign=sign, o=o, beam_w=beam_w, want_path=want_path, **cfg)


# ---------------------------------------------------------------------- the cases
def fix_cases(L):
    """L7-B's failure table, plus the baseline and two extras. `ndrift` is scaled with L
    so that the RATE (n per 240 runes) is what the gate says it is."""
    sc = lambda n: max(1, int(round(n * L / 240.0)))       # noqa: E731
    return [
        # (label, mech, mech-kwargs, key, key-kwargs, in_gate)
        ("keyskip supp=0.83 (BASELINE)", "keyskip", {"supp": 0.83}, "sha", {}, False),
        ("skip_by_two supp=0.5", "skip_by_two", {"supp": 0.5}, "sha", {}, True),
        ("skip_by_two supp=0.83", "skip_by_two", {"supp": 0.83}, "sha", {}, True),
        ("skip_by_two supp=1.0", "skip_by_two", {"supp": 1.0}, "sha", {}, True),
        ("free_drift q=0.05", "free_drift", {"supp": 0.83, "q": 0.05}, "sha", {}, True),
        ("free_drift q=0.10", "free_drift", {"supp": 0.83, "q": 0.10}, "sha", {}, True),
        (f"drift_at n=5/240 (={sc(5)})", "drift_at", {"supp": 0.83, "ndrift": sc(5)},
         "sha", {}, True),
        (f"drift_at n=10/240 (={sc(10)})", "drift_at", {"supp": 0.83, "ndrift": sc(10)},
         "sha", {}, True),
        ("two-draws: coin_from_key supp=0.83", "coin_from_key", {"supp": 0.83}, "sha", {}, True),
        ("runs r=16 supp=1.0", "keyskip", {"supp": 1.0}, "runs", {"run": 16}, True),
        ("runs r=32 supp=1.0", "keyskip", {"supp": 1.0}, "runs", {"run": 32}, True),
        # not in the gate, but measured because L7-B measured them
        ("free_drift q=0.02", "free_drift", {"supp": 0.83, "q": 0.02}, "sha", {}, False),
        ("drift_at n=1/240", "drift_at", {"supp": 0.83, "ndrift": sc(1)}, "sha", {}, False),
        ("runs r=8 supp=1.0", "keyskip", {"supp": 1.0}, "runs", {"run": 8}, False),
        ("keyskip supp=1.0", "keyskip", {"supp": 1.0}, "sha", {}, False),
    ]


def bound_cases(L):
    """Where does the permissive relation STOP covering? A single key-pointer JUMP of J
    positions at one rune needs max_free >= J; spreading the same drift one-per-rune does
    not. These rows are the lane's `not_covered` boundary, measured rather than asserted."""
    return [(f"jump_at J={J} n=1", "jump_at", {"supp": 0.83, "jump": J, "njump": 1},
             "sha", {}, False) for J in (1, 2, 3, 5, 8, 12)]


def base_cases(L):
    return [(f"keyskip supp={s}", "keyskip", {"supp": s}, "sha", {}, False)
            for s in (0.0, 0.4, 0.83, 1.0)]


# ------------------------------------------------------------------------- worker
def _one(job):
    label, mech, mkw, key, kkw, L, seed, cfgname = job
    hd = 12 if key == "runs" else 6
    C, K, P, info = cx.build(mech, L, seed, mkw, key=key, key_kw=kkw, headroom=hd)
    t = time.time()
    r = decode(C, K, cfgname)
    dt = time.time() - t
    return {"label": label, "mech": mech, "L": L, "seed": seed, "mode": cfgname,
            "score": r["score"], "recovery": db.recovery(r["plain_idx"], P),
            "n_skips_inferred": r["n_skips"], "n_unexplained": r["n_unexplained"],
            "true_skips": info.get("n_skips"), "max_skip_used": r["max_skip"],
            "ct_doublet_pct": cx.doublet_pct(C), "secs": dt}


def run_grid(cases, modes, lengths, nseed=NSEED, nproc=6):
    jobs = []
    for L in lengths:
        for (label, mech, mkw, key, kkw, _g) in cases(L):
            for cfgname in modes:
                for s in range(nseed):
                    jobs.append((label, mech, mkw, key, kkw, L, s, cfgname))
    print(f"  {len(jobs)} decodes on {nproc} procs ...", flush=True)
    rows = []
    t0 = time.time()
    with Pool(nproc) as pool:
        for k, r in enumerate(pool.imap_unordered(_one, jobs, chunksize=1)):
            rows.append(r)
            if (k + 1) % 100 == 0:
                print(f"    {k+1}/{len(jobs)}  ({time.time()-t0:.0f}s)", flush=True)
    return rows


def summarise(rows, cases, modes, lengths):
    out = []
    gate_flag = {}
    for L in lengths:
        for (label, mech, mkw, key, kkw, in_gate) in cases(L):
            gate_flag[(label, L)] = in_gate
            for cfgname in modes:
                sel = [r for r in rows
                       if r["label"] == label and r["L"] == L and r["mode"] == cfgname]
                if not sel:
                    continue
                sc = [r["score"] for r in sel]
                rc = [r["recovery"] for r in sel]
                out.append({
                    "label": label, "L": L, "mode": cfgname, "in_gate": in_gate,
                    "n_seeds": len(sel),
                    "median_score": statistics.median(sc),
                    "min_score": min(sc), "max_score": max(sc),
                    "median_recovery": statistics.median(rc),
                    "min_recovery": min(rc),
                    "frac_over_bar": sum(1 for r in sel
                                         if r["score"] >= BAR_SCORE
                                         and r["recovery"] >= BAR_REC) / len(sel),
                    "median_ct_doublet_pct": statistics.median(
                        r["ct_doublet_pct"] for r in sel),
                    "median_secs": statistics.median(r["secs"] for r in sel),
                    "max_skip_used": sel[0]["max_skip_used"],
                    "PASS": (statistics.median(sc) >= BAR_SCORE
                             and statistics.median(rc) >= BAR_REC),
                })
    return out


# --------------------------------------------------------------------------- stages
def stage_fix(nproc, nseed, lengths=(240, 400), modes=None, out="out_fix.json"):
    modes = modes or ["repo_ms3", "exact_ms8", "exact_auto", "pair_ms8",
                      "drift_l0", "drift_l4", "drift_l8", "drift_l16",
                      "drift_mf1", "drift_mf3"]
    print("\nG-FIX / G-COST grid")
    rows = run_grid(fix_cases, modes, lengths, nseed=nseed, nproc=nproc)
    summ = summarise(rows, fix_cases, modes, lengths)
    payload = {"lane": "round19/I1", "stage": "fix", "bar_score": BAR_SCORE,
               "bar_recovery": BAR_REC, "n_seeds": nseed, "beam_w": BEAM_W,
               "lengths": list(lengths), "modes": {m: MODES[m] for m in modes},
               "summary": summ, "rows": rows}
    json.dump(payload, open(os.path.join(HERE, out), "w"), indent=1)
    for L in lengths:
        print(f"\n--- L = {L} ---")
        for s in summ:
            if s["L"] != L:
                continue
            print(f"  {s['label']:36s} {s['mode']:11s} "
                  f"score {s['median_score']:7.3f}  rec {s['median_recovery']:6.1%}  "
                  f"{'PASS' if s['PASS'] else 'FAIL'}{'  [GATE]' if s['in_gate'] else ''}")
    return payload


def stage_base(nproc, nseed, lengths=(240, 400)):
    modes = ["repo_ms3", "exact_ms8", "pair_ms8", "drift_l0", "drift_l8", "drift_l16"]
    print("\nG-BASE grid (no-regression on the baseline construction)")
    rows = run_grid(base_cases, modes, lengths, nseed=nseed, nproc=nproc)
    summ = summarise(rows, base_cases, modes, lengths)
    payload = {"lane": "round19/I1", "stage": "base", "n_seeds": nseed,
               "lengths": list(lengths), "summary": summ, "rows": rows}
    json.dump(payload, open(os.path.join(HERE, "out_base.json"), "w"), indent=1)
    for s in summ:
        print(f"  L={s['L']:4d} {s['label']:22s} {s['mode']:10s} "
              f"score {s['median_score']:7.3f} rec {s['median_recovery']:6.1%}")
    return payload


def _book_one(job):
    L, seed, cfgname, wrong = job
    C, K, P, info = cx.build("keyskip", L, seed, {"supp": 0.83}, headroom=6)
    if wrong:
        K = cx.key_sha(len(K), seed=b"WRONG-KEY-%d" % seed)
    t = time.time()
    r = decode(C, K, cfgname)
    return {"L": L, "seed": seed, "mode": cfgname, "wrong_key": wrong,
            "score": r["score"], "recovery": db.recovery(r["plain_idx"], P),
            "n_skips_inferred": r["n_skips"], "true_skips": info["n_skips"],
            "secs": time.time() - t}


def stage_book(nproc, nseed=3, L=12956):
    print(f"\nG-BASE full-book control at L = {L} "
          f"(round18/L2 reference: -4.098 / 0.9997, wrong key -7.305)")
    jobs = []
    for cfgname in ("repo_ms3", "drift_l8"):
        for s in range(nseed):
            jobs.append((L, s, cfgname, False))
        jobs.append((L, 0, cfgname, True))
    rows = []
    with Pool(min(nproc, len(jobs))) as pool:
        for r in pool.imap_unordered(_book_one, jobs):
            rows.append(r)
            print(f"    {r['mode']:10s} seed {r['seed']} "
                  f"{'WRONG' if r['wrong_key'] else 'correct'} key: "
                  f"score {r['score']:7.3f} rec {r['recovery']:7.2%} "
                  f"skips {r['n_skips_inferred']}/{r['true_skips']} "
                  f"({r['secs']:.0f}s)", flush=True)
    payload = {"lane": "round19/I1", "stage": "book", "L": L,
               "reference_round18_L2": {"score": -4.098, "recovery": 0.9997,
                                        "wrong_key_score": -7.305},
               "rows": rows}
    json.dump(payload, open(os.path.join(HERE, "out_book.json"), "w"), indent=1)
    return payload


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all",
                    choices=["all", "fix", "base", "book", "bound"])
    ap.add_argument("--nproc", type=int, default=6)
    ap.add_argument("--nseed", type=int, default=NSEED)
    ap.add_argument("--modes", default=None,
                    help="comma-separated subset of MODES (fix stage only)")
    ap.add_argument("--out", default="out_fix.json")
    a = ap.parse_args()
    t0 = time.time()
    if a.stage in ("all", "base"):
        stage_base(a.nproc, a.nseed)
    if a.stage in ("all", "fix"):
        stage_fix(a.nproc, a.nseed,
                  modes=a.modes.split(",") if a.modes else None, out=a.out)
    if a.stage == "bound":
        modes = (a.modes.split(",") if a.modes
                 else ["repo_ms3", "drift_rec", "drift_mf6", "drift_mf10"])
        print("BOUND probe: single key-pointer jumps")
        rows = run_grid(bound_cases, modes, (240,), nseed=a.nseed, nproc=a.nproc)
        summ = summarise(rows, bound_cases, modes, (240,))
        json.dump({"lane": "round19/I1", "stage": "bound",
                   "modes": {m: MODES[m] for m in modes},
                   "summary": summ, "rows": rows},
                  open(os.path.join(HERE, "out_bound.json"), "w"), indent=1)
        for s in summ:
            print(f"  {s['label']:20s} {s['mode']:11s} score {s['median_score']:7.3f} "
                  f"rec {s['median_recovery']:6.1%} {'PASS' if s['PASS'] else 'FAIL'}")
    if a.stage in ("all", "book"):
        stage_book(a.nproc)
    print(f"\ntotal {time.time()-t0:.0f}s")
