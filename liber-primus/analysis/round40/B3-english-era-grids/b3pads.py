#!/usr/bin/env python3
"""R40-B3 pad driver. python b3pads.py regen | counts | control G3|G4 | run G3|G4"""
import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import pads as P

SCR = "C:/Users/Jeff/AppData/Local/Temp/claude/C--Users-Jeff/aa51cdb9-c856-4e25-a820-1ce5c0520024/scratchpad/b3dl"
P3DIR = SCR + "/p3/pads"
LADDER = [1000, 5000, 20000, 100000, 1000000, 10 ** 7, 5 * 10 ** 7]
G4_PADS = {"560.00auth": SCR + "/DATA__560.00.iso-authoritative", "560.13": SCR + "/DATA_560.13", "560.17": SCR + "/DATA_560.17", "761.mp3": SCR + "/761.mp3"}
G4_SHA = {"560.00auth": "a24051a87f0eb25ca21accbd3158fdf7b4911243e5ee1b9778b81182f0d36573", "560.13": "db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f"}
G4_BUILD = ["mod29", "prime_to_idx", "hi_nibble", "lo_nibble", "byte_scaled"]
G3_BUILD = ["mod29", "prime_to_idx", "hi_nibble", "lo_nibble", "byte_scaled", "nibbles", "hexchars"]


def mk(g):
    if g == "G3":
        pads = {f[:-4]: P3DIR + "/" + f for f in sorted(os.listdir(P3DIR)) if f.endswith(".bin")}
        return P.PadGrid("R17PAD", pads, G3_BUILD, int(os.environ.get("G3_CAP", 40000)), LADDER)
    ex = {"560.00auth": [k * 16384 for k in range(244)], "560.13": [k * 331777 for k in range(359)]}
    return P.PadGrid("COSPAD", G4_PADS, G4_BUILD, int(os.environ.get("G4_CAP", 250000)), LADDER, ex)


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "regen":
        cmp, pd = P.regen_p3(SCR + "/p3")
        print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in cmp.items()}))
        import hashlib
        rec = {}
        for k, p in G4_PADS.items():
            h = hashlib.sha256(open(p, "rb").read()).hexdigest(); rec[k] = {"bytes": os.path.getsize(p), "sha256": h, "receipt_match": (G4_SHA.get(k) == h) if k in G4_SHA else None}
        json.dump(rec, open(E.F("cos_pads_regen.json"), "w"), indent=1); print(rec)
    elif m == "counts":
        out = {}
        for g in ("G3", "G4"):
            gr = mk(g); tot, per = gr.planned(); out[g] = {**gr.counts, "columns_planned": tot, "screens_planned": 2 * tot, "per_cell": per}
        json.dump(out, open(E.F("counts_pads.json"), "w"), indent=1)
        print({g: (v["pads"], v["bytes"], v["cells"], v["columns_planned"]) for g, v in out.items()})
    elif m == "control":
        E.control(mk(sys.argv[2]), ndecoy=int(os.environ.get("B3_DECOYS", 256)))
    elif m == "run":
        g = mk(sys.argv[2])
        ks_ = {"G3": "R17 P3 regenerated pads x builders(mod29,prime_to_idx,hi_nibble,lo_nibble,byte_scaled,nibbles,hexchars<=2MB) x {fwd,rev} x sign; offsets 0..7+A1 ladder+stride sample (cap per cell)",
               "G4": "CicadaOS ISO pads (560.00 authoritative, 560.13, 560.17, 761.mp3) x 5 reductions x {fwd,rev} x sign; offsets 0..7+A1 ladder+R28-L1 stride grids+stride sample (cap per cell)"}[sys.argv[2]]
        st = E.Store(g.name, ks_)
        E.run_grid(g, st, cap_s=float(os.environ.get("B3_CAP", 0)) or None)
        st.close(); print("DONE", g.name, json.dumps(st.st["best"]))
