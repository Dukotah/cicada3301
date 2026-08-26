#!/usr/bin/env python3
"""ROUND 19 / G3 — LABELLED PLUMBING PILOT.  NOT EVIDENCE.

Pre-registered in PREREG.md §6 as the sole exception to the Phase-1 hold: I1
(`round19/I1/driftbeam.py`) and I2 (`round19/I2/adjudicate.py`) both exist, so a
pilot of <= 10,000 decodes may be run to prove the plumbing and measure
throughput.

A pilot is a TIMING MEASUREMENT.  It produces no negative, it clears no key
space, and its best score is a plumbing artefact reported as such.  The Phase-2
hit bar is I3's, not this file's.

    python3 pilot.py --seeds 60 --out pilot.jsonl
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
R19  = os.path.abspath(os.path.join(HERE, ".."))
LP   = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE,
          os.path.join(R19, "I1"), os.path.join(R19, "I2"),
          os.path.join(LP, "analysis", "round13", "B04"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import gen_py27 as G
import seeds as B04SEEDS
import driftbeam as DB
from adjudicate import adjudicate, to_row, header
import lib_numchannel as nc

N = 29
MODES = ("random29", "grb5_mod", "grb5_rej", "shuffle29")


def atbash(C):
    return [(N - 1) - c for c in C]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=60)
    ap.add_argument("--L", type=int, default=120)
    ap.add_argument("--beam-mode", default="keyskip1")
    ap.add_argument("--out", default=os.path.join(HERE, "pilot.jsonl"))
    a = ap.parse_args()

    entries = B04SEEDS.build()
    core = B04SEEDS.core(entries)
    use = core[:a.seeds]
    C = list(nc.unsolved()[:a.L])
    CA = atbash(C)

    hdr = header(
        "round19/G3/PILOT",
        key_space=("PILOT ONLY, NOT COVERAGE: first %d B-04 core seeds x 4 py2.7 "
                   "reductions x wordsize{64,32} x sign{-1,+1} x atbash{0,1} x "
                   "dir{fwd,rev}, offset 0" % len(use)),
        decoder="round19/I1 driftbeam mode=%s beam_w=400 max_skip=3" % a.beam_mode,
        generator="round19/G3 gen_py27.py, VALIDATED vs real CPython 2.7.3 + 2.7.18",
        notes=("LABELLED PLUMBING PILOT. Timing only. Not a sweep, not a negative. "
               "Hit bar deferred to round19/I3."),
    )

    t0 = time.time()
    n = 0
    best = (-99.0, None)
    with open(a.out, "w") as f:
        f.write(json.dumps(hdr) + "\n")
        for fam, sb in use:
            for mode in MODES:
                for ws in (64, 32):
                    K0 = G.keystream(sb, mode, a.L * 5 + 64, wordsize=ws)
                    for dirn, K in (("fwd", K0), ("rev", list(reversed(K0)))):
                        for sign in (-1, 1):
                            for ab, Cx in (("off", C), ("on", CA)):
                                r = DB.beam_decode(Cx, K, sign=sign, o=0,
                                                   beam_w=400, max_skip=3,
                                                   mode=a.beam_mode)
                                kid = "%s|%s|ws%d|%s|s%+d|ab%s" % (
                                    sb.decode("latin-1"), mode, ws, dirn, sign, ab)
                                res = adjudicate(r["plain_idx"])
                                f.write(json.dumps(to_row(res, kid)) + "\n")
                                n += 1
                                if res["en"] > best[0]:
                                    best = (res["en"], kid)
    dt = time.time() - t0
    print(json.dumps({
        "decodes": n,
        "seconds": round(dt, 1),
        "decodes_per_sec_1core": round(n / dt, 1),
        "ms_per_decode": round(1000 * dt / n, 2),
        "best_en_PLUMBING_ARTEFACT": round(best[0], 4),
        "best_kid": best[1],
        "out": a.out,
        "NOTE": "timing only; no hit bar applied; see round19/I3 for the bar",
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
