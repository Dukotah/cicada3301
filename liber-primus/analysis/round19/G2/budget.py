"""ROUND 19 / G2 -- the arithmetic behind READY.md.

Every number in READY.md sec.3-5 comes from here, from measured rates in
bench.json / pilot.json plus the in-repo C precedent, so the run spec can be
checked rather than believed.  Prints a table; writes budget.json.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CORES = 6

# --- measured on this box (round19/G2/pilot.json) --------------------------
# end-to-end = keystream gen + I3 vecbeam decode + I2 full SWEEPROW, per core
PY = {
    "screen_L31_keyskip1":   662.9,
    "esc_L120_keyskip1":     106.4,
    "esc_L120_skip_by_two":  108.0,
    "esc_L120_r29nodup":     160.3,
}
# I3 vecbeam.py --bench, decode only, 1 core: permissive modes are far slower
PERMISSIVE_DECODE_PER_S = {"drift3_L120": 12.8, "union0_5_L120": 8.7}

# --- the in-repo C precedent ----------------------------------------------
# round10/L5-seed32/results_newgens.txt:
#   gen=10 perl int(rand(29)) drand48  seeds=1293840000..1420070400 ... 168.1s
# run_newgens.sh sets OMP_NUM_THREADS default 32.
C_SEEDS = 1420070400 - 1293840000
C_SECONDS = 168.1
C_THREADS = 32
C_DIRS = 2                      # sweep32x scored dir in {0,1} per seed
C_PER_S_PER_CORE = C_SEEDS * C_DIRS / C_SECONDS / C_THREADS

# --- the space -------------------------------------------------------------
SEEDS_ALL = 1 << 32
REDUCTIONS = 9
ORIENT = 8                      # sign x atbash x direction
STAGE_A = SEEDS_ALL * REDUCTIONS * ORIENT

BANDS = {
    "S0 authoring window 2013-01-01..2014-06-30": 1404086400 - 1356998400,
    "S1 era band 2011-01-01..2015-01-01":         1420070400 - 1293840000,
    "S2 small literals + pid + top of range":     2 * (1 << 16),
    "S4 remainder of 2**32":                      SEEDS_ALL - (1420070400 - 1293840000) - 2 * (1 << 16),
}


def hours(n_decodes, per_s_per_core, cores=CORES):
    return n_decodes / (per_s_per_core * cores) / 3600


def main():
    out = {"cores": CORES, "measured_python_per_s_per_core": PY,
           "c_precedent": {"source": "round10/L5-seed32/results_newgens.txt gen=10",
                           "seeds": C_SEEDS, "seconds": C_SECONDS,
                           "threads": C_THREADS,
                           "decodes_per_s_per_core": round(C_PER_S_PER_CORE),
                           "caveat": "different box (32 threads), window 48, rigid+F-branch "
                                     "decoder, English 4-gram only. A Round-19 C screen must "
                                     "carry I1's relation and I2's panel, so this is an upper "
                                     "bound on what a faithful C screen achieves, and must be "
                                     "re-measured on this box."},
           "space": {"seeds": SEEDS_ALL, "reductions_perl_reachable": REDUCTIONS,
                     "orientations": ORIENT, "stage_A_decodes": STAGE_A,
                     "stage_B_offset_ladder_multiplier": 10},
           "bands": BANDS}

    scr = PY["screen_L31_keyskip1"]
    print(f"cores={CORES}  python screen L=31: {scr:.0f}/s/core = {scr*CORES:,.0f}/s")
    print(f"C precedent: {C_PER_S_PER_CORE:,.0f}/s/core = {C_PER_S_PER_CORE*CORES:,.0f}/s "
          f"({C_PER_S_PER_CORE/scr:.0f}x python)\n")

    print(f"{'cell':<58} {'decodes':>14} {'py h':>9} {'C h':>8}")
    rows = []
    plan = [
        ("full Stage A: 2**32 x 9 reductions x 8 orientations", STAGE_A),
        ("2**32 x r29 x 8 orientations", SEEDS_ALL * ORIENT),
        ("2**32 x r29 x 1 canonical orientation", SEEDS_ALL),
        ("2**32 x top-3 reductions x 8 orientations", SEEDS_ALL * 3 * ORIENT),
    ]
    for bname, bn in BANDS.items():
        plan.append((f"{bname.split()[0]} ({bn:,}) x r29 x 8 orientations", bn * ORIENT))
        plan.append((f"{bname.split()[0]} ({bn:,}) x 9 reductions x 8 orientations",
                     bn * REDUCTIONS * ORIENT))
    for name, n in plan:
        ph, ch = hours(n, scr), hours(n, C_PER_S_PER_CORE)
        print(f"{name:<58} {n:>14,} {ph:>9.1f} {ch:>8.1f}")
        rows.append({"cell": name, "decodes": n,
                     "python_hours_6core": round(ph, 2), "c_hours_6core": round(ch, 2)})
    out["cells"] = rows

    print("\n-- what a fixed wall-clock buys (python screen, 6 cores) --")
    buys = {}
    for h in (12, 24, 48, 72, 168):
        n = int(scr * CORES * h * 3600)
        buys[f"{h}h"] = {"decodes": n,
                         "seeds_at_1_orientation_1_reduction": n,
                         "frac_of_2**32": n / SEEDS_ALL,
                         "frac_of_stage_A": n / STAGE_A}
        print(f"  {h:>4}h -> {n:>14,} decodes = {n/SEEDS_ALL*100:7.2f}% of 2**32 "
              f"at 1 reduction x 1 orientation, {n/STAGE_A:.2e} of Stage A")
    out["wall_clock_buys_python"] = buys

    print("\n-- permissive / drift modes (I3 vecbeam --bench, decode only, 1 core) --")
    for k, v in PERMISSIVE_DECODE_PER_S.items():
        print(f"  {k:16s} {v:6.1f} dec/s/core  = {PY['esc_L120_keyskip1']/v:5.1f}x slower "
              f"than the L=120 keyskip1 end-to-end rate")
    print("  If I1 ships a permissive relation as the PRIMARY one, divide every")
    print("  number above by ~13 and G2's coverage collapses accordingly.")

    print("\n-- escalation tier is cheap; the screen is everything --")
    for topk in (10**4, 10**5, 10**6, 10**7):
        h = hours(topk, PY["esc_L120_keyskip1"])
        print(f"  escalate top {topk:>10,} screen rows to L=120: {h*60:8.1f} min")
    out["escalation"] = {str(k): round(hours(k, PY["esc_L120_keyskip1"]) * 60, 2)
                         for k in (10**4, 10**5, 10**6, 10**7)}

    with open(os.path.join(HERE, "budget.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote budget.json")


if __name__ == "__main__":
    main()
