"""ROUND 19 / LANE G2 -- throughput measurement.

`READY.md` has to state a wall-clock, and a wall-clock invented from intuition is
how this repo produced ten rounds of sweeps whose size nobody could sanity-check.
So the numbers in READY.md come from here.

Measures, on THIS box:
  1. keystream generation cost per reduction (symbols/sec)
  2. decode cost per config, using `campaign18_skip.beam_decode` at B-04's
     settings (beam_w=400, max_skip=3, L=120) as the ONLY available stand-in for
     I1's driftbeam, which does not exist yet
  3. rigid decode cost, for contrast only -- NOT a candidate decision statistic
     (round12/D3: rigid scores the CORRECT key at -6.835, i.e. noise)

Nothing here scores a real G2 keystream against a threshold.  It times the
plumbing on a fixed, arbitrary seed block and reports seconds.  No decode
produced here is retained, compared to a bar, or reported as a result.

Run:  python3 bench.py
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import skipdecode as sk          # noqa: E402
import lib_numchannel as nc      # noqa: E402
import gen_perl as G             # noqa: E402

N = 29
L = 120          # B-04 stage-A segment length
BEAM_W = 400
MAX_SKIP = 3


def main():
    out = {"box": os.uname().nodename if hasattr(os, "uname") else "?",
           "python": sys.version.split()[0],
           "params": {"L": L, "beam_w": BEAM_W, "max_skip": MAX_SKIP}}

    # ---- 1. generation ---------------------------------------------------
    NSYM = 512
    gen = {}
    for red in G.PERL_REACHABLE:
        t0 = time.time()
        n = 0
        while time.time() - t0 < 0.35:
            for s in range(64):
                G.make_ks(red, 1389657600 + s, NSYM)
                n += 1
        dt = time.time() - t0
        gen[red] = {"keystreams_per_sec": round(n / dt, 1),
                    "sym_per_sec": round(n * NSYM / dt)}
        print(f"  gen {red:12s} {gen[red]['keystreams_per_sec']:>9.1f} ks/s "
              f"({gen[red]['sym_per_sec']:>10,} sym/s)")
    out["generation"] = gen

    # ---- 2. decode -------------------------------------------------------
    C = nc.unsolved()[:L]
    K = G.make_ks("r29", 1389657600, L * (MAX_SKIP + 1) + 16)

    t0 = time.time()
    nd = 0
    while time.time() - t0 < 4.0:
        sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
        nd += 1
    dt = time.time() - t0
    beam_per_s = nd / dt
    print(f"\n  beam_decode  L={L} beam_w={BEAM_W} max_skip={MAX_SKIP}: "
          f"{beam_per_s:.2f} decodes/s/core  ({1000/beam_per_s:.1f} ms each)")

    t0 = time.time()
    nr = 0
    while time.time() - t0 < 1.5:
        sk.rigid_decode(C, K, sign=-1, o=0)
        nr += 1
    rigid_per_s = nr / (time.time() - t0)
    print(f"  rigid_decode (CONTRAST ONLY, not a decision statistic): "
          f"{rigid_per_s:.0f} decodes/s/core")

    # smaller beams, to show the shape of any speed/power trade I1 might face
    variants = {}
    for bw, msk in ((100, 3), (50, 2), (25, 2), (400, 8)):
        t0 = time.time()
        k = 0
        while time.time() - t0 < 1.5:
            sk.beam_decode(C, K, sign=-1, o=0, beam_w=bw, max_skip=msk)
            k += 1
        variants[f"beam_w={bw},max_skip={msk}"] = round(k / (time.time() - t0), 2)
    for k, v in variants.items():
        print(f"    {k:26s} {v:>8.2f} decodes/s/core")

    out["decode"] = {"beam_decodes_per_sec_per_core": round(beam_per_s, 3),
                     "beam_ms_per_decode": round(1000 / beam_per_s, 2),
                     "rigid_decodes_per_sec_per_core": round(rigid_per_s, 1),
                     "beam_variants": variants}

    # ---- 3. what that buys, in decodes ----------------------------------
    cores = os.cpu_count() or 1
    out["cores_detected"] = cores
    budgets = {}
    for cores_used in (1, max(1, cores - 2), cores):
        for hours in (1, 6, 24, 72):
            budgets[f"{cores_used}c x {hours}h"] = int(beam_per_s * cores_used * hours * 3600)
    out["decode_budget"] = budgets

    SPACE_A = (1 << 32) * 9 * 2 * 2 * 2
    out["space"] = {
        "seeds": 1 << 32,
        "reductions_perl_reachable": 9,
        "sign_atbash_direction": 8,
        "stageA_offset0_decodes": SPACE_A,
        "stageB_offset_ladder_multiplier": 10,
    }
    print(f"\n  cores detected: {cores}")
    print(f"  Stage-A full cross product: {SPACE_A:,} decodes")
    for k in (f"{max(1, cores-2)}c x 24h", f"{max(1, cores-2)}c x 72h"):
        n = budgets[k]
        print(f"  {k:14s} -> {n:>15,} decodes = {n/SPACE_A:.3e} of Stage A")

    with open(os.path.join(HERE, "bench.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote bench.json")


if __name__ == "__main__":
    main()
