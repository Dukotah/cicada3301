"""T3 — the sensitivity curves. Random, targeted and adversarial perturbation of the pinned
12,956-rune stream; every stream-dependent statistic recomputed at each (model, k).

PREREG §2/§3. Trials are reported as median with a 5-95 % band, never as a point.
Every perturbed stream is hashed; the hash of the k=0 row is the pinned PROBLEM.json SHA.

Run: python3 t3_sensitivity.py            (writes out_random.json, out_targeted.json)
"""
import json, os, random, statistics, sys, time
import t3_lib as T

HERE = os.path.dirname(os.path.abspath(__file__))

TRIALS = 400
KGRID_FULL = [1, 2, 5, 10, 20, 50, 100, 200, 450, 1000, 2000, 4000, 8000, 12956]

# The pre-registered floors (PREREG §2.1). Values in PERCENT.
FLOORS = {
    "D-GER":   (0.972, "German — the binding register (round18/L7 §C.2)"),
    "D-VNV":   (1.084, "vowel-dropped English (round18/L7 §C.2)"),
    "D-LP1":   (1.585, "LP1 solved-page register (round18/L7 §C.2)"),
    "D-LAT":   (1.425, "Latin (round18/L7 §C.2)"),
    "D-KJV":   (1.386, "KJV — lowest of D2's four English corpora"),
    "D-STALE": (1.500, "the stale figure still in ELIMINATION-LEDGER.md:779"),
    "D-ENHO":  (1.483, "held-out English (round18/L7 §C.2)"),
    "D-MAX":   (2.339, "Welsh — the highest register floor"),
    "L2-CONTAIN": (100.0 * (86 + 4 * 86 ** 0.5) / 12955,
                   "L2's 4-sd containment breach of M1_ct_keyskip (86 + 4*sqrt(86) doublets)"),
}


def band(vals):
    vals = sorted(vals)
    n = len(vals)
    return {
        "median": statistics.median(vals),
        "mean": statistics.fmean(vals),
        "sd": statistics.pstdev(vals) if n > 1 else 0.0,
        "p05": vals[max(0, int(0.05 * n) - 1)],
        "p95": vals[min(n - 1, int(0.95 * n))],
        "min": vals[0], "max": vals[-1],
    }


def run_model(C, name, fn, kgrid, trials, seed, pool_kw=None):
    rows = []
    base = T.bundle(C)
    rows.append({"k": 0, "trials": 1, "stats": {kk: band([base[kk]]) for kk in T.CHEAP_KEYS},
                 "example_sha256": base["sha256"]})
    pool_kw = pool_kw or {}
    for k in kgrid:
        rng = random.Random(seed + 1000 * k)
        acc = {kk: [] for kk in T.CHEAP_KEYS}
        sha0 = None
        t0 = time.time()
        for t in range(trials):
            Cp = fn(C, k, rng, **pool_kw)
            b = T.bundle(Cp)
            if sha0 is None:
                sha0 = b["sha256"]
            for kk in T.CHEAP_KEYS:
                acc[kk].append(b[kk])
        rows.append({"k": k, "trials": trials,
                     "stats": {kk: band(acc[kk]) for kk in T.CHEAP_KEYS},
                     "example_sha256": sha0,
                     "secs": round(time.time() - t0, 1)})
        d = rows[-1]["stats"]["doublet_rate_pct"]
        print(f"  {name:10s} k={k:6d}  doublet% med={d['median']:.4f} "
              f"[{d['p05']:.4f},{d['p95']:.4f}]  IoC*N med="
              f"{rows[-1]['stats']['ioc_norm']['median']:.5f}  ({rows[-1]['secs']}s)",
              flush=True)
    return rows


def crossings(rows, key="doublet_rate_pct"):
    """For each pre-registered floor, the smallest k in the grid whose median / p95 / max
    reaches it, plus a linear-interpolated k*.  Returns None where never reached."""
    out = {}
    for fid, (val, src) in FLOORS.items():
        rec = {"floor_pct": val, "source": src}
        for stat in ("median", "p95", "max"):
            kstar = None
            prev = None
            for r in rows:
                v = r["stats"][key][stat] if r["k"] else r["stats"][key]["median"]
                if v >= val:
                    if prev is None:
                        kstar = r["k"]
                    else:
                        (k0, v0) = prev
                        kstar = k0 + (r["k"] - k0) * (val - v0) / (v - v0) if v > v0 else r["k"]
                    break
                prev = (r["k"], v)
            rec[f"k_{stat}"] = kstar
        out[fid] = rec
    return out


def main():
    C = T.stream()
    print(f"baseline sha256 {T.sha_of(C)}")
    out = {"baseline_sha256": T.sha_of(C), "trials": TRIALS, "floors": FLOORS}

    # ---------- adversarial (deterministic; the true worst-case bound) ----------
    print("P-ADV (deterministic worst case)")
    adv = []
    for k in [0, 1, 2, 5, 10, 15, 20, 25, 30, 40, 47, 50, 60, 75, 94, 100, 110, 150,
              200, 300, 441, 450, 500, 1000]:
        Cp = T.p_adv(C, k) if k else list(C)
        b = T.bundle(Cp)
        adv.append({"k": k, "stats": {kk: band([b[kk]]) for kk in T.CHEAP_KEYS},
                    "example_sha256": b["sha256"]})
        print(f"  P-ADV      k={k:6d}  doublets={b['doublets']:5d} "
              f"rate={b['doublet_rate_pct']:.4f}%  supp={b['lag1_suppression_pct']:.2f}%",
              flush=True)
    out["P-ADV"] = {"rows": adv, "crossings": crossings(adv),
                    "note": "deterministic greedy doublet-maximiser; PC-1 verified exact"}

    # ---------- uniform random ----------
    print("P-RAND")
    rr = run_model(C, "P-RAND", T.p_rand, KGRID_FULL, TRIALS, 3301)
    out["P-RAND"] = {"rows": rr, "crossings": crossings(rr)}

    # ---------- dense pages 45-54 ----------
    pool = T._dense_pool()
    print(f"P-DENSE (pool = {len(pool)} positions on pages 45-54)")
    kd = [k for k in KGRID_FULL if k <= len(pool)] + [len(pool)]
    rd = run_model(C, "P-DENSE", T.p_dense, sorted(set(kd)), TRIALS, 4402,
                   pool_kw={"pool": pool})
    out["P-DENSE"] = {"rows": rd, "crossings": crossings(rd), "pool_size": len(pool)}

    json.dump(out, open(os.path.join(HERE, "out_random.json"), "w"), indent=1)
    print("wrote out_random.json")


if __name__ == "__main__":
    main()
