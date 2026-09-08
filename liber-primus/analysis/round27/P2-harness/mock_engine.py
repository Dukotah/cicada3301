#!/usr/bin/env python3
"""Round 27 / P2 -- MOCK engine: implements the ENGINE-CONTRACT.md CLI on top of the
Python reference. NOT a performance tool -- it exists to prove the HARNESS can recognise
a conforming engine as PASS (the harness's own positive control, doctrine Q1). Usage:

    GRIND27=$PWD/mock_engine.py python3 check_vectors.py         # etc.

Never point the acceptance run at this -- it is Python scoring Python and proves nothing
about the C port. run_all.sh refuses if GRIND27 ends in mock_engine.py.
"""
import argparse
import json
import sys

import pyref


def load_cipher(path):
    if not path:
        return None
    with open(path) as f:
        return json.load(f)["cipher_idx"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--lm", required=True)
    ap.add_argument("--mode", required=True, choices=["score", "sweep", "self-test"])
    ap.add_argument("--seeds")
    ap.add_argument("--out")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--cipher")
    ap.add_argument("--band-start", type=int)
    ap.add_argument("--band-end", type=int)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--progress-dir")
    args = ap.parse_args()
    cipher = load_cipher(args.cipher)

    if args.mode == "self-test":
        pa = pyref.vectors()["planted_stage_a"]
        r = pyref.stage_a_full(pa["seed"], cipher=pa["cipher_idx_120"])
        cand = r["pmax"] >= pyref.CAND_BAR
        print(json.dumps({"mode": "self-test", "seed": pa["seed"],
                          "pmax": r["pmax"], "candidate": cand}))
        return 0 if cand else 1

    if args.mode == "score":
        seeds = [int(x) for x in open(args.seeds).read().split()]
        with open(args.out, "w") as f:
            for w in seeds:
                if args.full:
                    r = pyref.stage_a_full(w, cipher=cipher)
                    f.write(json.dumps(r) + "\n")
                else:
                    p = (pyref.stage_a_full(w, cipher=cipher)["pmax"] if cipher is not None
                         else pyref.runner.stage_a(w))
                    f.write(json.dumps({"seed": w, "pmax": p}) + "\n")
        return 0

    # sweep
    import time
    t0 = time.time()
    seeds = list(range(args.band_start, args.band_end))
    rows = pyref.score_many(seeds, cipher=cipher, workers=args.threads,
                            progress_every=0)
    with open(args.out, "w") as f:
        for w, p in rows:
            if p >= pyref.CAND_BAR:
                f.write(json.dumps({"seed": w, "pmax": p}) + "\n")
    print(json.dumps({"mode": "sweep", "seeds_done": len(seeds),
                      "elapsed_s": round(time.time() - t0, 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
