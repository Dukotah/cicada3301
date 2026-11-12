"""R44/R1 — the positive-control GATE (PREREG: G1/G2/G3), run BEFORE the sweep.

Plants three known plaintexts through THIS lane's own encipher+decode glue (R42 X1 rule) and
requires (a) the reset-aware path to recover each exactly, (b) the rigid (non-reset) path to
MISS them — the differential that licenses the lane.  Writes gate.json.
Any failure => INSTRUMENT-INCOMPLETE (run_sweep.py refuses to run).
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resets as R                               # noqa: E402

LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))
sys.path.insert(0, os.path.join(LP, "src"))
import adjudicate as A                           # noqa: E402
import bars_v3 as B                              # noqa: E402
from lp import gematria as gp                    # noqa: E402

PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
FREE_LS = (120, 240, 400, 729)


def free_bar(L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(R.N_BAR, max(cand), "free")


def to_idx(text):
    out = []
    for w in text.split():
        out.extend(gp.keyword_to_indices(w))
    return out


# the F5b-T LP-register plaintexts (known-English controls of record)
PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
       "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE "
       "MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM "
       "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED "
       "KNOW THIS WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP "
       "BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND "
       "AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND "
       "YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO "
       "DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING "
       "A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN "
       "ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR "
       "HEAD")


def plant_phases(n_pages, page_len, line_len=24):
    """Phase vectors per mode for a synthetic plant group (its own red-head 'section')."""
    phs = []
    for t in range(n_pages):
        ar = np.arange(page_len, dtype=np.int64)
        phs.append({"page": ar, "line": ar % line_len, "section": t * page_len + ar})
    return phs


def main():
    t0 = time.time()
    keys = R.build_keys()
    anchors = {m: {k: R.anchor_offsets(K, m) for k, K in keys.items()} for m in R.MODES}
    out = {"n_keys": len(keys), "bars": {"120": round(free_bar(120), 4),
                                         "240": round(free_bar(240), 4)},
           "controls": [], "passed": None}

    # ---------------- G1: page resets, direct, (P-totient, page, o=7, vigp), 3 x 120
    p1 = (to_idx(PT1) + to_idx(PT2))[:360]
    assert len(p1) == 360
    C1 = R.encipher_reset(p1, keys["P-totient"], "vigp", [120, 120, 120], offset=7)
    g1 = {"name": "G1", "cell": dict(key="P-totient", mode="page", offset=7, cfg="vigp"),
          "pages": []}
    phs = plant_phases(3, 120)
    ok1 = True
    for t in range(3):
        c = np.asarray(C1[t * 120:(t + 1) * 120], dtype=np.int64)
        pt = p1[t * 120:(t + 1) * 120]
        bar = free_bar(120)
        cnt, best, cross = R.tier1_sweep_page(c, phs[t], keys, anchors, bar, A, PAN)
        # the planted cell's own decode + score
        dec = R.cell_decode(c, phs[t]["page"], keys["P-totient"], 7, "vigp")
        full = A.adjudicate(dec, pan=PAN)
        planted_is_max = bool(full["pmax"] >= best["pmax"] - 1e-9)
        exact = bool(list(dec) == list(pt))
        # rigid differential = the global-key continuation (== the plant-section phase)
        rig = R.cell_decode(c, phs[t]["section"], keys["P-totient"], 7, "vigp")
        rfull = A.adjudicate(rig, pan=PAN)
        rrec = R.recovery(rig, pt)
        g1["pages"].append(dict(
            page=t, n_cells=cnt, grid_best={k: best[k] for k in
                                            ("pmax", "mode", "key", "offset", "cfg", "bar")},
            planted_pmax=float(full["pmax"]), planted_degenerate=bool(full["degenerate"]),
            planted_is_grid_max=planted_is_max, exact_recovery=exact,
            rigid_recovery=round(float(rrec), 4), rigid_pmax=float(rfull["pmax"])))
        ok1 &= (planted_is_max and exact and not full["degenerate"] and full["pmax"] >= bar)
        if t > 0:  # differential binds on the post-reset pages
            ok1 &= (rrec <= 0.5 and rfull["pmax"] < bar)
    g1["passed"] = bool(ok1)
    out["controls"].append(g1)
    print(json.dumps(g1), flush=True)

    # ---------------- G2: line resets, direct, (G-bash-1325734783, line, o=3, beau), 1 x 240
    p2 = to_idx(PT2)[:240]
    assert len(p2) == 240
    kname2 = "G-bash-1325734783"
    seg2 = [24] * 10
    C2 = R.encipher_reset(p2, keys[kname2], "beau", seg2, offset=3)
    phs2 = plant_phases(1, 240)[0]
    bar = free_bar(240)
    cnt, best, cross = R.tier1_sweep_page(np.asarray(C2), phs2, keys, anchors, bar, A, PAN)
    dec = R.cell_decode(C2, phs2["line"], keys[kname2], 3, "beau")
    full = A.adjudicate(dec, pan=PAN)
    rig = R.cell_decode(C2, phs2["page"], keys[kname2], 3, "beau")   # rigid: no line resets
    rfull = A.adjudicate(rig, pan=PAN)
    rrec = R.recovery(rig, p2)
    g2 = {"name": "G2", "cell": dict(key=kname2, mode="line", offset=3, cfg="beau"),
          "n_cells": cnt,
          "grid_best": {k: best[k] for k in ("pmax", "mode", "key", "offset", "cfg", "bar")},
          "planted_pmax": float(full["pmax"]), "planted_degenerate": bool(full["degenerate"]),
          "planted_is_grid_max": bool(full["pmax"] >= best["pmax"] - 1e-9),
          "exact_recovery": bool(list(dec) == list(p2)),
          "rigid_recovery": round(float(rrec), 4), "rigid_pmax": float(rfull["pmax"]),
          }
    g2["passed"] = bool(g2["planted_is_grid_max"] and g2["exact_recovery"]
                        and not g2["planted_degenerate"] and g2["planted_pmax"] >= bar
                        and rrec <= 0.5 and rfull["pmax"] < bar)
    out["controls"].append(g2)
    print(json.dumps(g2), flush=True)

    # ---------------- G3: page resets, keyskip1-FILTERED, (P-prime, page, o=0, vigm), 3 x 120
    p3 = (to_idx(PT3) + to_idx(PT1))[:360]
    assert len(p3) == 360
    C3 = R.encipher_reset(p3, keys["P-prime"], "vigm", [120, 120, 120], offset=0,
                          keyskip=True, supp=0.83, seed=3301)
    beam = R.beam_reset_decode(C3, keys["P-prime"], "vigm", [120, 120, 120], offset=0)
    rigid = R.beam_rigid_decode(C3, keys["P-prime"], "vigm", offset=0)
    brec, rrec3 = R.recovery(beam, p3), R.recovery(rigid, p3)
    # tier-1 screen power against the FILTERED construction (measured, not assumed)
    scr = []
    phs3 = plant_phases(3, 120)
    for t in range(3):
        c = C3[t * 120:(t + 1) * 120]
        dec = R.cell_decode(c, phs3[t]["page"], keys["P-prime"], 0, "vigm")
        full = A.adjudicate(dec, pan=PAN)
        scr.append(dict(page=t, tier1_pmax=float(full["pmax"]),
                        tier1_recovery=round(R.recovery(dec, p3[t * 120:(t + 1) * 120]), 4),
                        bar=round(free_bar(120), 4), crosses=bool(full["pmax"] >= free_bar(120)
                                                                  and not full["degenerate"])))
    g3 = {"name": "G3", "cell": dict(key="P-prime", mode="page", offset=0, cfg="vigm",
                                     keyskip=True, supp=0.83),
          "beam_reset_recovery": round(float(brec), 4),
          "beam_rigid_recovery": round(float(rrec3), 4),
          "tier1_screen_power_on_filtered": scr,
          "passed": bool(brec >= 0.85 and rrec3 < 0.85)}
    out["controls"].append(g3)
    print(json.dumps(g3), flush=True)

    out["passed"] = bool(all(c["passed"] for c in out["controls"]))
    out["verdict"] = "GATE-PASSED" if out["passed"] else "INSTRUMENT-INCOMPLETE"
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "gate.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("passed", "verdict", "bars", "elapsed_s")}))


if __name__ == "__main__":
    main()
