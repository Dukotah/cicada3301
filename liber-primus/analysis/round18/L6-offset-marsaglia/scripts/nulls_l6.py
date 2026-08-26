"""L6 - this lane's OWN null band, measured at ms=8 on the real keystream families.

Two reasons this is not optional:

1. A bigger skip budget gives the beam more freedom, so a null measured at ms=3 is not a
   null at ms=8.  Round 17's P3 addendum re-measured for exactly this reason.
2. `benchmark/null.py: threshold_for(n_trials, segment_len)` ACCEPTS a segment_len and
   does not use it - its Gumbel constants (mu=-7.2517, beta=0.0725) were tail-calibrated
   on L~120 windows (see the CALIBRATION block in that file).  This lane adjudicates on a
   400-rune window.  Measuring the null at BOTH lengths establishes the direction of that
   mismatch empirically instead of assuming it is harmless.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L

N = 200


def main():
    L.trigram_model()
    out = {"n": N, "max_skip": X.MS, "beam_w": X.BEAM_W, "families": {}}
    fams = []

    # a real B-04 derived keystream (dictionary seed, real generator)
    cfgs = [c for c in X.mine_configs() if c["kind"] == "b04"]
    c = cfgs[0]
    fams.append((f"derived:{c['gen']}|{c['red']}", X.derived_keystream(c, 1 << 18)))
    k = [q for q in X.mine_configs() if q["kind"] == "kdf"][0]
    fams.append((f"derived:{k['kdf']}|{k['reduction']}", X.derived_keystream(k, 1 << 18)))

    # the real, hash-verified Marsaglia bytes
    mp = os.path.join(X.DATA, "MANIFEST.json")
    if os.path.exists(mp):
        man = json.load(open(mp))
        p = next((q for q in man["verified_pads"] if q["name"] == "BITS.01"), None)
        if p:
            a = np.fromfile(os.path.join(X.DATA, "iso", p["extracted"]), dtype=np.uint8,
                            count=1 << 22)
            fams.append(("marsaglia:BITS.01|mod29", X.build_full(a, "mod29")))

    for name, K in fams:
        out["families"][name] = {}
        for head in (400, 120):
            t = time.time()
            mean, mx = X.shuffle_null(K, seq_len=head, n=N, ms=X.MS, beam_w=X.BEAM_W)
            out["families"][name][f"head{head}"] = {
                "null_mean": round(mean, 4), "null_max": round(mx, 4),
                "bar_null_max_plus_0.5": round(mx + 0.5, 4), "seconds": round(time.time() - t, 1)}
            print(f"  {name} head={head}: mean={mean:+.4f} max={mx:+.4f}", flush=True)

    m400 = [v["head400"]["null_max"] for v in out["families"].values()]
    m120 = [v["head120"]["null_max"] for v in out["families"].values()]
    out["null_max_head400"] = max(m400)
    out["null_max_head120"] = max(m120)
    out["head400_null_is_lower_than_head120"] = max(m400) < max(m120)
    out["note"] = (
        "threshold_for()'s Gumbel constants are tail-calibrated on L~120 windows and the "
        "function ignores its segment_len argument. This lane adjudicates on L=400. The "
        "measured L=400 null max is "
        + ("LOWER" if max(m400) < max(m120) else "NOT lower") +
        " than the L=120 null max, so applying the L~120-calibrated bar to L=400 scores is "
        + ("CONSERVATIVE - it can only make a hit harder to claim, never easier."
           if max(m400) < max(m120) else
           "NOT automatically conservative and the measured null_max+0.5 bar governs."))
    X.jdump(out, os.path.join(X.OUT, "nulls.json"))
    print(json.dumps({k: v for k, v in out.items() if k != "families"}, indent=1))


if __name__ == "__main__":
    main()
