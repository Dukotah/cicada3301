"""L5 / PREREG A.5 - B-05's pinned Part-1 grid, re-run on the RESOLVED payload.

Why this is new coverage and not a re-run of measured ground (Round 18 Rule 7):
B-05's LEDGER `reopens_if` reads "JOINT corruption of two or more contested bytes (only
single-position sweeps and the 64 all-combination masks were run)". A-04's adjudication
changed THREE bytes jointly - and at indices 45, 50 and 246, which are not among B-05's six
contested indices at all. B-05 varied only {25, 175, 182, 199, 215, 237}; no part of it ever
touched 45/50/246. So payload_resolved.bin is a seed B-05 provably never evaluated, and
B-05's own control measured that a single byte flip moves a keystream decode from -4.170
(perfect recovery) to -7.38 (noise).

Grid is B-05's Part 1 verbatim, on the resolved payload's six representations:
  6 reps x 15 generators x {mod, reject} x {fwd, rev} x {atbash, plain} x {+1, -1}
  x 14 offsets = 20,160 skip-aware beam decodes, HEAD=400, beam_w=120, max_skip=3.

Bar (Rule 4): benchmark/null.py threshold_for(20160, 400), and the operative bar is
max(that, null_max) exactly as in B-05.

Writes b05_propagation.json incrementally so an infrastructure stall cannot cost the run.

    nohup python3 propagate_b05.py > b05.log 2>&1 &
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
B05 = os.path.join(LP, "analysis", "round13", "B05")
for p in (os.path.join(LP, "src"), os.path.join(LP, "analysis"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "benchmark"), B05):
    sys.path.insert(0, p)

import skipdecode as sk          # noqa: E402
import lib_numchannel as nc      # noqa: E402
import prf                       # noqa: E402
import null as nullmod           # noqa: E402

HEAD = 400
BEAM_W = 120
MAX_SKIP = 3
OFFSETS = [0, 1, 2, 3, 5, 8, 13, 29, 64, 128, 256, 512, 1024, 3301]
REDUCTIONS = ["mod", "reject"]
SIGNS = [-1, +1]
DIRECTIONS = ["fwd", "rev"]
ATBASH = [False, True]
CKPT = os.path.join(HERE, "b05_propagation.json")

UNS = nc.unsolved()
HEADSEQ = UNS[:HEAD]
TOTAL_KS = HEAD * (MAX_SKIP + 1) + max(OFFSETS) + 64


def null_band(n=200, seed0=3301):
    """Size-matched shuffle null, same construction as B-05."""
    import random
    scores = []
    for i in range(n):
        rnd = random.Random(seed0 + i)
        surro = list(HEADSEQ)
        rnd.shuffle(surro)
        K = [rnd.randrange(29) for _ in range(TOTAL_KS)]
        scores.append(sk.beam_decode(surro, K, sign=1, o=0,
                                     beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    return sum(scores) / len(scores), max(scores)


def main():
    payload = open(os.path.join(HERE, "payload_resolved.bin"), "rb").read()
    assert len(payload) == 256
    reps = {"res." + k: fn(payload) for k, fn in prf.REPR_FNS.items()}
    gens = list(prf.GENERATORS)
    n_planned = (len(reps) * len(gens) * len(REDUCTIONS) * len(DIRECTIONS)
                 * len(ATBASH) * len(SIGNS) * len(OFFSETS))

    fw_bar = nullmod.threshold_for(n_planned, HEAD)
    print("planned decodes: %d" % n_planned, flush=True)
    print("threshold_for(%d, %d) = %.3f" % (n_planned, HEAD, fw_bar), flush=True)
    nmean, nmax = null_band(200)
    bar = max(fw_bar, nmax)
    print("null (n=200): mean %.3f  max %.3f   -> operative bar %.3f"
          % (nmean, nmax, bar), flush=True)

    state = {"payload": "payload_resolved.bin",
             "payload_sha256": __import__("hashlib").sha256(payload).hexdigest(),
             "head": HEAD, "beam_w": BEAM_W, "max_skip": MAX_SKIP,
             "n_planned": n_planned, "threshold_for": fw_bar,
             "null_mean": nmean, "null_max": nmax, "bar": bar,
             "reps": sorted(reps), "gens": gens,
             "done": 0, "best": None, "top20": [], "hits": [],
             "status": "running", "started": time.time()}

    def flush():
        state["elapsed_s"] = time.time() - state["started"]
        with open(CKPT, "w") as f:
            json.dump(state, f, indent=1)

    flush()
    results = []
    t0 = time.time()
    for rname in sorted(reps):
        seed = reps[rname]
        for gname in gens:
            for red in REDUCTIONS:
                base = prf.keystream(seed, gname, red, TOTAL_KS)
                for direction in DIRECTIONS:
                    Kd = base if direction == "fwd" else base[::-1]
                    for atb in ATBASH:
                        K = prf.atbash(Kd) if atb else Kd
                        for sign in SIGNS:
                            for o in OFFSETS:
                                bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=o,
                                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                                rec = {"rep": rname, "gen": gname, "red": red,
                                       "dir": direction, "atbash": atb, "sign": sign,
                                       "o": o, "score": bd["score"],
                                       "head": bd["translit"][:48]}
                                results.append(rec)
                                if rec["score"] >= bar:
                                    state["hits"].append(rec)
            state["done"] = len(results)
            results.sort(key=lambda x: x["score"], reverse=True)
            state["best"] = results[0]
            state["top20"] = results[:20]
            flush()
            print("  [%s %s] done=%d/%d  %.0fs  best=%.3f"
                  % (rname, gname, len(results), n_planned, time.time() - t0,
                     results[0]["score"]), flush=True)

    results.sort(key=lambda x: x["score"], reverse=True)
    state["done"] = len(results)
    state["best"] = results[0]
    state["top20"] = results[:20]
    state["status"] = "complete"
    state["verdict"] = "CANDIDATES FOUND" if state["hits"] else "NEGATIVE"
    state["comparison_to_b05"] = {
        "b05_part1_best_on_canon": -6.770530995360567,
        "b05_null_max": -7.001321900235663,
        "b05_bar": -5.5,
        "note": "B-05 Part 1 ran 40,320 decodes over the 12 maj/dec representations and "
                "returned NEGATIVE with best -6.771. This run covers the 6 representations "
                "of the resolved payload, which B-05 never evaluated."}
    flush()
    print("\nVERDICT: %s   best %.3f vs bar %.3f"
          % (state["verdict"], results[0]["score"], bar), flush=True)


if __name__ == "__main__":
    main()
