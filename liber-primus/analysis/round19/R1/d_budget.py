"""R1 / sub-attack D — the round's own logic: is 'fix the instrument, then sweep the small
haystack' the highest-value use of the budget?

Pre-registered in PREREG.md §6.

  D-a  throughput arithmetic: wall-clock to ENUMERATE the spaces the plan calls enumerable,
       through a repaired (drift-tolerant) decoder, on this machine.
  D-b  the prefilter dilemma: the only prefilter in the repo is a RIGID ENGLISH trigram scan;
       measure its survival for non-English and for filter-desynchronised plants.
  D-c  what S2 can physically re-adjudicate, against what L7-B rendered conditional.
  D-d  the steel-man: the doctrine-R5 rank-1 objects.

    python3 d_budget.py   -> out_d.json
"""
import json
import math
import os
import random
import statistics as st
import sys
import time

import numpy as np

import r1_lib as R

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round17"))

SEED0 = 55021

# The spaces Round 19's plan calls enumerable, with the plan's / L1's own sizing.
SPACES = [
    ("G1 bash $RANDOM (sbrand seed, 32-bit)", 2 ** 32,
     "CAMPAIGN-PLAN G1 'never swept, enumerable'; L1 6.3.1 'small enough to enumerate "
     "completely in minutes'"),
    ("G1 glibc random() TYPE_3 (32-bit seed)", 2 ** 32, "L1 rank 1"),
    ("G2 Perl 5.14 srand (32-bit)", 2 ** 32, "L1 rank 3, never swept"),
    ("G4 TeX \\pgfmathrandom LCG (2^31-2 seeds)", 2 ** 31 - 2,
     "L1 6.3.3 'period 2^31-1 and a 1..2^31-2 seed range - fully enumerable'"),
    ("G3 Python 2.7 random.seed(<string>) over a 10^4 dictionary", 10 ** 4,
     "L1 6.3.2 'silent coverage hole ... cheap to close'"),
]
# multiplicity every prior sweep in this repo applied per seed
AXES = {"sign +/-": 2, "atbash on/off": 2, "direction fwd/rev": 2}


def throughput(configs, L, n=12):
    out = {}
    uns = R.unsolved()
    for label, model, ms in configs:
        rng = random.Random(SEED0)
        t0 = time.time()
        for k in range(n):
            off = rng.randrange(0, len(uns) - L - 1)
            C = uns[off:off + L]
            K = R.random_key(rng, L * 10 + 512)
            R.beam_decode(C, K, beam_w=400, max_skip=ms, model=model)
        dt = time.time() - t0
        out[label] = {"sec_per_decode": dt / n, "decodes_per_sec": n / dt, "L": L, "n": n}
    return out


def hhmm(seconds):
    if seconds < 3600:
        return f"{seconds/60:.1f} min"
    if seconds < 86400:
        return f"{seconds/3600:.1f} h"
    if seconds < 86400 * 365:
        return f"{seconds/86400:.1f} d"
    return f"{seconds/86400/365.25:.3g} yr"


# ------------------------------------------------------------------ D-b
def prefilter_survival(nrep=40, plen=24, keep_frac=40 / 400):
    """R17's dense_scan is a RIGID English trigram scan over a 24-rune head.

    Measure, for each plaintext register and each construction, whether the TRUE offset
    survives into the top-`keep` of the rigid trigram ranking against a pool of wrong offsets.
    """
    import lib_padsweep as PS
    T = PS.trigram_model()
    regs = R.build_registers()
    rng = random.Random(SEED0 + 7)
    out = {}
    for reg in ("EN", "LP1", "LA", "CY", "OE", "EN_HALF"):
        S = regs[reg]
        for cons, enc in (("keyskip", R.encipher_keyskip), ("skip2", R.encipher_skip2)):
            surv, ranks = 0, []
            for rep in range(nrep):
                a = rng.randrange(0, len(S) - plen - 40)
                P = S[a:a + plen + 20]
                K = R.sha_key(b"CICADA3301" + bytes([rep % 256]), 4000)
                C, _ = enc(P, K, supp=0.83, seed=SEED0 + rep)
                # true offset = 0 in K; wrong offsets = a pool of random offsets in a random key
                def tri(Pidx):
                    s = 0.0
                    for j in range(2, len(Pidx)):
                        s += T[Pidx[j - 2], Pidx[j - 1], Pidx[j]]
                    return s / (len(Pidx) - 2)
                true_p = [(C[j] - K[j]) % 29 for j in range(plen)]
                true_s = tri(true_p)
                pool = []
                for _ in range(400):
                    o = rng.randrange(1, 3000)
                    pool.append(tri([(C[j] - K[o + j]) % 29 for j in range(plen)]))
                r = 1 + sum(1 for x in pool if x > true_s)
                ranks.append(r)
                if r <= max(1, int(keep_frac * len(pool))):
                    surv += 1
            out[f"{reg}/{cons}"] = {"survival_rate": surv / nrep,
                                    "median_rank_of_true_offset": st.median(ranks),
                                    "pool": 400, "keep": int(keep_frac * 400)}
    return out


# ------------------------------------------------------------------ D-c
def s2_reach():
    """How much of the 1.7e10 scored decodes can S2 physically re-adjudicate?"""
    A = os.path.join(LP, "analysis")
    stored, detail = 0, {}
    for f, key in (("round13/B04/results_A.json", "top50"),
                   ("round13/B04/results_B.json", "top50"),
                   ("round13/B04/results_C.json", "top50"),
                   ("round13/B04/results_D.json", "top50"),
                   ("round16/prng/results.json", "top20")):
        p = os.path.join(A, f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if isinstance(d, list):
            d = {key: d}
        rows = d.get(key) or []
        if rows and not isinstance(rows[0], dict):
            rows = []
        sc = [r["score"] for r in rows if isinstance(r, dict) and "score" in r]
        nd = d.get("n_decodes") or d.get("total_decodes")
        sc = [r["score"] for r in rows if isinstance(r, dict) and "score" in r]
        detail[f] = {"rows_stored": len(rows), "n_decodes": nd,
                     "best": max(sc) if sc else None,
                     "worst_stored": min(sc) if sc else None,
                     "has_key_params": bool(rows) and ("seed" in rows[0]),
                     "hist": bool(d.get("hist"))}
        stored += len(rows)
        # where does a skip_by_two correct key land in THIS sweep's own histogram?
        h = d.get("hist")
        hs = d.get("hist_stats")
        if h and hs:
            detail[f]["hist_stats"] = hs
    # round17 lanes
    for root, _dd, ff in os.walk(os.path.join(A, "round17")):
        for fn in ff:
            if fn.endswith(".json"):
                try:
                    d = json.load(open(os.path.join(root, fn)))
                except Exception:                                 # noqa: BLE001
                    continue
                for k in ("top20", "top50", "top"):
                    if isinstance(d, dict) and isinstance(d.get(k), list):
                        stored += len(d[k])
    return {"stored_rows_total_est": stored, "detail": detail}


def main():
    out = {"meta": {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}}

    print("== D-a: throughput arithmetic ==")
    cfgs = [("exact/ms3", "exact", 3), ("union2/ms3", "union2", 3), ("free/ms3", "free", 3)]
    tp = {}
    for L in (24, 120, 240):
        tp[f"L{L}"] = throughput(cfgs, L, n=8 if L == 240 else 12)
        for k, v in tp[f"L{L}"].items():
            print(f"  L={L:3d} {k:12s} {v['decodes_per_sec']:9.2f} decodes/s "
                  f"({v['sec_per_decode']*1000:.1f} ms)")
    out["D_a_throughput"] = tp

    rate = tp["L120"]["union2/ms3"]["decodes_per_sec"]
    rate_free = tp["L120"]["free/ms3"]["decodes_per_sec"]
    mult = 1
    for v in AXES.values():
        mult *= v
    rows = []
    for name, size, cite in SPACES:
        n = size * mult
        rows.append({"space": name, "seeds": size, "axis_multiplier": mult, "decodes": n,
                     "sec_union2_1core": n / rate, "sec_free_1core": n / rate_free,
                     "sec_union2_6core": n / rate / 6,
                     "wall_union2_6core": hhmm(n / rate / 6),
                     "wall_free_6core": hhmm(n / rate_free / 6),
                     "cite": cite})
        print(f"  {name:52s} {n:>18,} decodes -> {hhmm(n/rate/6):>12s} (union2, 6 cores)"
              f"  {hhmm(n/rate_free/6):>12s} (free)")
    out["D_a_spaces"] = rows
    budget_s = 86400.0
    worst = max(r["sec_union2_6core"] for r in rows if r["seeds"] > 10 ** 6)
    out["D_i"] = {"budget_s": budget_s, "worst_space_s": worst,
                  "ratio_over_24h": worst / budget_s,
                  "verdict": "FOUND-ERROR" if worst / budget_s > 1000 else "NO-ERROR-FOUND"}
    print(f"  worst enumerable space = {hhmm(worst)} on 6 cores = "
          f"{worst/budget_s:,.0f}x a 24-hour budget -> D-i {out['D_i']['verdict']}")

    # --- two-stage arithmetic: rigid numpy prefilter -> beam on survivors --------
    print("\n== D-a2: the two-stage (prefilter -> beam) arithmetic ==")
    import lib_padsweep as PS
    T = PS.trigram_model()
    rngx = random.Random(SEED0 + 11)
    uns = R.unsolved()
    Ck = np.array(uns[:24], dtype=np.int16)
    Kbig = np.array([rngx.randrange(29) for _ in range(1 << 21)], dtype=np.int16)
    t0 = time.time()
    hits = PS.dense_scan(Kbig, list(Ck), sign=-1)
    dtp = time.time() - t0
    pref_rate = (len(Kbig) - 24) / dtp
    print(f"  rigid numpy trigram prefilter: {pref_rate:,.0f} candidates/s/core "
          f"({len(hits)} kept of {len(Kbig)-24})")
    two = []
    for r in out["D_a_spaces"]:
        n = r["decodes"]
        for keep in (1e-3, 1e-4, 1e-5):
            t_pref = n / pref_rate / 6
            t_beam = n * keep / rate / 6
            two.append({"space": r["space"], "keep_fraction": keep,
                        "sec_prefilter_6core": t_pref, "sec_beam_6core": t_beam,
                        "sec_total_6core": t_pref + t_beam,
                        "wall_total_6core": hhmm(t_pref + t_beam)})
        w = two[-2]
        print(f"  {r['space']:52s} keep 1e-4 -> {w['wall_total_6core']:>10s} "
              f"(prefilter {hhmm(w['sec_prefilter_6core'])} + beam "
              f"{hhmm(w['sec_beam_6core'])})")
    out["D_a2_two_stage"] = {"prefilter_rate_per_core": pref_rate, "rows": two,
                             "prefilter_model": "RIGID English rune-trigram over a 24-rune head "
                                                "(round17/lib_padsweep.dense_scan); trained on "
                                                "kjv/moby/pride/war"}

    print("\n== D-b: the prefilter dilemma ==")
    try:
        out["D_b_prefilter"] = prefilter_survival(nrep=30)
        for k, v in out["D_b_prefilter"].items():
            print(f"  {k:18s} true-offset survival into top-40/400 = {v['survival_rate']:.2f}"
                  f"   median rank {v['median_rank_of_true_offset']:.0f}/400")
    except Exception as e:                                        # noqa: BLE001
        out["D_b_prefilter"] = {"error": str(e)}
        print("  prefilter measurement failed:", e)

    print("\n== D-c: what S2 can physically re-adjudicate ==")
    out["D_c"] = s2_reach()
    print(f"  stored rows across all post-B6 sweeps: ~{out['D_c']['stored_rows_total_est']}")
    for k, v in out["D_c"]["detail"].items():
        print(f"    {k:34s} rows {v['rows_stored']:>3} of {str(v['n_decodes']):>12}  "
              f"best {v['best']}  cutoff {v['worst_stored']}  "
              f"key params stored: {v['has_key_params']}")
    total_scored = 17_058_157_809          # L7 C.6's repo-wide tally
    frac = out["D_c"]["stored_rows_total_est"] / total_scored
    out["D_iii"] = {"stored": out["D_c"]["stored_rows_total_est"],
                    "total_scored": total_scored, "fraction": frac,
                    "verdict": "FOUND-ERROR" if frac < 1e-4 else "NO-ERROR-FOUND"}
    print(f"  fraction re-adjudicable = {frac:.3e} -> D-iii {out['D_iii']['verdict']}")

    out["meta"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(out, open(os.path.join(HERE, "out_d.json"), "w"), indent=1)
    print("\nwrote out_d.json")


if __name__ == "__main__":
    main()
