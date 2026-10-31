#!/usr/bin/env python3
"""R40-B3 driver. python b3.py counts|control <grid>|run <grid> [stages]|final"""
import sys, os, json, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import grids as G


def mk(name):
    return {"B04": G.B04Grid, "KDF": G.KdfGrid}[name]()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "counts":
        b = G.B04Grid(); k = G.KdfGrid()
        out = {"B04": {**b.counts, "planned": b.planned(), "planned_total": sum(b.planned().values()),
                       "original_seed_count": 2165, "original_core": 504},
               "KDF": {**k.counts, "planned": k.planned(), "original_secrets": 534, "original_decodes": 692064}}
        json.dump(out, open(E.F("counts.json"), "w"), indent=1); print(json.dumps(out, indent=1))
    elif mode == "control":
        g = mk(sys.argv[2]); nd = int(os.environ.get("B3_DECOYS", 512))
        E.control(g, ndecoy=nd)
    elif mode == "run":
        g = mk(sys.argv[2]); stages = tuple(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
        ks_ = {"B04": "B-04 regenerated seed dictionary 2165 seeds / 504 core x 16 generators x reductions x dir x sign x atbash; stages A (offset 0), B (offsets 0..7+ladder), C (55 page heads)",
               "KDF": "R16-KDF 534 secrets x 27 KDF configs x 3 salts x 2 reductions x dir x sign x atbash, offset 0"}[g.name]
        if stages: g.stages = stages
        name = g.name + ("_" + "".join(stages) if stages else "")
        st = E.Store(name, ks_)
        E.run_grid(g, st, cap_s=float(os.environ.get("B3_CAP", 0)) or None)
        st.close(); print("DONE", name, json.dumps(st.st["best"]))
