"""R44 / W2-B3 step 1 — positive controls through the cell's OWN glue -> plants.json.

Four plant classes (PREREG Q1), 40 replicates each, plus 25 untouched-draw specificity runs
and the battery's positive control.  NO REAL TARGET IS READ HERE.  Bars used by the gate are
built first (nulls.py must have run) — gate order: nulls (no real data read, only surrogates)
-> plants -> real.
"""
import json
import random as pyrandom
import time

import numpy as np

import b3lib as B

REPS = 40
rng = np.random.default_rng(B.SEED + 7)
pan = B.panel()
t0 = time.time()

xU, pgU = B.stream_pages("U")
nU = len(xU)
bars = json.load(open("nulls.json"))["bars"]
null_batt = json.load(open("nulls.json"))["battery_null_U"]

out = {"reps": REPS, "classes": {}}


def _plant_once_value(rng1):
    base = B.zero_doublet_base(xU, pyrandom.Random(int(rng1.integers(1 << 30))))
    w = B.english_windows(86, 1, rng1)[0]
    pos = B.random_positions(86, nU, rng1)
    y = B.inject_value_sites(base, pos, w)
    ch, p, g, cnt = B.channels(y, pgU, B.N_PAGES_U)
    ok = len(p) == 86 and np.array_equal(p, pos) and np.array_equal(ch["dblvals"], w)
    pm, meta, full, deg = B.best_reading(ch["dblvals"], pan)
    return ok, pm, "dblvals"


def _plant_once_gap(rng1):
    base = B.zero_doublet_base(xU, pyrandom.Random(int(rng1.integers(1 << 30))))
    w = B.english_windows(85, 1, rng1)[0]
    gaps = w + 3                                  # recoverable at grid shift s = -3 mod 29
    pos = B.positions_from_gaps(gaps, start=10)
    vals = rng1.integers(0, B.N, size=86)
    y = B.inject_value_sites(base, pos, vals)
    ch, p, g, cnt = B.channels(y, pgU, B.N_PAGES_U)
    ok = len(p) == 86 and np.array_equal(p, pos)
    pm, meta, full, deg = B.best_reading(ch["gapsmod29"], pan)
    # battery positive control: clustered positions must fire T1 at the registered bar
    st = B.battery_stats(y, pgU, B.N_PAGES_U, nU)
    t1p = B.addone_upper(null_batt["T1_ks"], st["T1_ks"])
    return ok, pm, t1p


def _plant_once_pos(rng1):
    base = B.zero_doublet_base(xU, pyrandom.Random(int(rng1.integers(1 << 30))))
    w = B.english_windows(86, 1, rng1)[0]
    gaps = (np.diff(w)) % B.N
    gaps = np.where(gaps < 3, gaps + B.N, gaps)
    pos = B.positions_from_gaps(gaps, start=29 + int(w[0]))
    vals = rng1.integers(0, B.N, size=86)
    y = B.inject_value_sites(base, pos, vals)
    ch, p, g, cnt = B.channels(y, pgU, B.N_PAGES_U)
    ok = len(p) == 86 and np.array_equal(p % B.N, w)
    pm, meta, full, deg = B.best_reading(ch["posmod29"], pan)
    return ok, pm, "posmod29"


def _plant_once_cnt(rng1):
    base = B.zero_doublet_base(xU, pyrandom.Random(int(rng1.integers(1 << 30))))
    # feasibility: shortest pages cannot hold 28 separated doublets, so reject-sample
    # English windows until every page's count fits its capacity (sep 4)
    caps = np.array([(np.flatnonzero(pgU == pg)[-1] - np.flatnonzero(pgU == pg)[0] - 4) // 4
                     for pg in range(B.N_PAGES_U)])
    for _ in range(400):
        w = B.english_windows(55, 1, rng1)[0]
        if np.all(w <= caps):
            break
    else:
        raise RuntimeError("no feasible counts window")
    pos_all = []
    for pg in range(B.N_PAGES_U):
        k = int(w[pg])
        if k == 0:
            continue
        idx = np.flatnonzero(pgU == pg)
        lo, hi = idx[0] + 2, idx[-1] - 2
        # stars-and-bars: distinct sorted draws + 3*arange guarantees pairwise diff >= 4
        span = hi - lo - 3 * (k - 1)
        if span < k:
            raise RuntimeError("page placement failed")
        c = np.sort(rng1.choice(span, size=k, replace=False))
        cand = lo + c + 3 * np.arange(k)
        pos_all.extend(cand.tolist())
    pos = np.asarray(sorted(pos_all), dtype=np.int64)
    vals = rng1.integers(0, B.N, size=len(pos))
    y = B.inject_value_sites(base, pos, vals)
    ch, p, g, cnt = B.channels(y, pgU, B.N_PAGES_U)
    ok = np.array_equal(ch["pagecounts"], w)
    pm, meta, full, deg = B.best_reading(ch["pagecounts"], pan)
    return ok, pm, "pagecounts"


for name, fn, chan in (("PLANT-V", _plant_once_value, "dblvals_U"),
                       ("PLANT-G", _plant_once_gap, "gapsmod29_U"),
                       ("PLANT-P", _plant_once_pos, "posmod29_U"),
                       ("PLANT-C", _plant_once_cnt, "pagecounts_U")):
    bar = bars[chan]["bar_of_record"]
    glue_ok, hits, extra = 0, 0, []
    pms = []
    for r in range(REPS):
        rng1 = np.random.default_rng(B.SEED + 100 * (1 + ["PLANT-V", "PLANT-G", "PLANT-P",
                                                          "PLANT-C"].index(name)) + r)
        ok, pm, x3 = fn(rng1)
        glue_ok += int(ok)
        hits += int(pm >= bar)
        pms.append(pm)
        if name == "PLANT-G":
            extra.append(x3)
    cls = {"glue_recovered": glue_ok, "power": hits / REPS, "bar": bar,
           "pm_median": float(np.median(pms)), "pm_min": float(np.min(pms)),
           "pm_max": float(np.max(pms))}
    if name == "PLANT-G":
        cls["battery_T1_fire_rate"] = float(np.mean([p <= B.BATT_ALPHA for p in extra]))
        cls["battery_T1_p_median"] = float(np.median(extra))
    out["classes"][name] = cls
    print(name, cls, flush=True)

# -------- specificity: 25 untouched dfshuffle draws through the full channel pipeline
spec_cross = 0
spec_batt_fire = 0
for j in range(25):
    y = B.site_matched_shuffle(xU, pyrandom.Random(B.SEED + 900000 + j), target=86)
    ch, p, g, cnt = B.channels(y, pgU, B.N_PAGES_U)
    for cname, key in (("dblvals", "dblvals_U"), ("gapsmod29", "gapsmod29_U"),
                       ("posmod29", "posmod29_U"), ("pagecounts", "pagecounts_U")):
        pm, _, _, deg = B.best_reading(ch[cname], pan)
        if (not deg) and pm >= bars[key]["bar_of_record"]:
            spec_cross += 1
    st = B.battery_stats(y, pgU, B.N_PAGES_U, nU)
    vc_mean = np.asarray(null_batt["vc_mean"], dtype=float)
    t5 = float(((np.asarray(st["T5_valuecounts"], dtype=float) - vc_mean) ** 2
                / np.maximum(vc_mean, 1e-9)).sum())
    ps = [B.addone_upper(null_batt["T1_ks"], st["T1_ks"]),
          B.addone_two(null_batt["T2_gapcv2"], st["T2_gapcv2"]),
          B.addone_upper(null_batt["T3_chi2_mod29"], st["T3_chi2_mod29"]),
          B.addone_upper(null_batt["T4_chi2_mod60"], st["T4_chi2_mod60"]),
          B.addone_upper(null_batt["T5_chi2"], t5),
          B.addone_two(null_batt["T6_dispersion"], st["T6_dispersion"]),
          B.addone_two(null_batt["T7_gap_ac1"], st["T7_gap_ac1"])]
    spec_batt_fire += int(any(q <= B.BATT_ALPHA for q in ps))
out["specificity"] = {"draws": 25, "channel_crossers": spec_cross,
                      "battery_fires": spec_batt_fire}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("plants.json", "w"), indent=1)
print("SPECIFICITY", out["specificity"], "elapsed", out["elapsed_s"], flush=True)
