#!/usr/bin/env python3
"""Round 28 / L4 -- per-cell gate construction for grind28.

For EVERY queued cell (generator-reducer x relation x offset) this builds, through
the R25 Python reference pipeline imported verbatim (runner/driftbeam/adjudicate/
hitfn20 -- reimplements nothing):

  (a) a 64-seed VECTOR set: seed -> ks128 -> stage-A decode artifacts on the real
      C_SCREEN (pmax at full repr precision, plain_idx, beam_score, ptr_end,
      n_skips, nchars). grind28 must reproduce ALL of it |delta|=0 at launch.
  (b) a PLANTED CONTROL: held-out English (self_reliance[5000:5240]) enciphered
      with THIS cell's true keystream under THIS cell's relation and offset
      (pair -> skip_by_two supp=.83 / exact -> one-draw keyskip supp=.83, both
      rng=Random(777), key cursor starting at the cell offset), plus the full
      3-clause hitfn20 verdict (must be HIT=True, recovery >= 0.999) and the
      stage-A screen expectation the C engine must match and flag.
  (c) a FALSE-REJECT set: 8 wrong seeds decoded against the plant cipher; all
      reference pmax values recorded; every one must sit below the cell claim bar.

Cell keystreams come from gen28 (PHP/glibc; |delta|=0-validated against
/usr/bin/php + resident glibc, receipts/genval.json) or gen_py27 (R21-L3-validated)
for the S3 cells. Claim bars are frozen HERE, per cell, at the PREREG's
N = 2^32 ceiling: panelmax_bar(relation, 2**32, 0.01), family count disclosed.

Outputs: gates/cellgate_<lane>.dat (C-parseable), receipts/gates_receipts.json,
queued_cells.json (heavy sweeps -- NOT fired here).
"""
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round25", "compute-tail"))
sys.path.insert(0, HERE)

import runner                    # noqa  (R25 pipeline, verbatim; extends sys.path)
import driftbeam as DB           # noqa
import adjudicate as AD          # noqa
import hitfn20 as H              # noqa
import gen_py27 as G             # noqa
import skipdecode as sk          # noqa
import gen28                     # noqa

L_SCREEN, L_HIT = runner.L_SCREEN, runner.L_HIT
CAND_BAR = 5.0
# PREREG amendment A1: frozen ladder; first seed whose FULL gate passes is the cell's
# plant; every tried seed + verdict is recorded (measured clause-3 power, no cherry-pick).
PLANT_LADDER = [777, 778, 1001, 20260908, 555, 31337, 90210, 424242]
FR_SEEDS = [779, 3301, 42, 123456789, 999999999, 2147483648, 4294967295, 31415926]
FIXED_SEEDS = [0, 1, 3301, 1325734783, 2149309687, 2 ** 32 - 1]
RAND_SEED = 20260907             # same frozen vector-seed list as R27 P0

N_CEILING = 2 ** 32              # PREREG bar N per cell


def py27_stream(mode):
    def f(w, n):
        r = G.MT19937()
        r.init_by_array([w] if w else [0])
        return G.REDUCERS[mode](r, n)
    return f


STREAMS = dict(gen28.CELL_GENS)
STREAMS["grb5_mod"] = py27_stream("grb5_mod")
STREAMS["grb5_rej"] = py27_stream("grb5_rej")
STREAMS["shuffle29"] = py27_stream("shuffle29")


def cells():
    """Queue order frozen in PREREG Q3: PHP-canonical, PHP-broken, glibc, S3 last."""
    out = []
    for red in ("php_mt_scale", "php_mt_mod", "php_php_scale", "php_php_mod",
                "glibc_mod"):
        for rel in ("pair", "exact"):
            out.append((f"L4-{red}-{rel}", red, rel, 0))
    for red in ("grb5_mod", "grb5_rej", "shuffle29"):
        for off in (1, 3, 5, 7, 13):
            out.append((f"S3-{red}-o{off}", red, "pair", off))
    return out


def encipher(P, K, relation, o, seed, supp=0.83):
    """pair -> skip_by_two (reject advances key by 2); exact -> one-draw keyskip
    (advances by 1). Key cursor starts at the cell offset o. Decode relation is
    p = (c + sign*k) mod 29 with sign=-1, i.e. c = (p + k) mod 29."""
    rng = random.Random(seed)
    step = 2 if relation == "pair" else 1
    C, j, c_prev = [], o, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += step
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C


def stage_a(C, K, relation, o):
    d = DB.beam_decode(C, K, sign=-1, o=o, beam_w=runner.SCREEN_BEAM_W,
                       **DB.PRESETS[relation])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return d, float(a["pmax"])


def main():
    rng = random.Random(RAND_SEED)
    vec_seeds = FIXED_SEEDS + sorted(rng.randrange(0, 2 ** 32) for _ in range(58))
    bars = {rel: float(H.PM.panelmax_bar(rel, N_CEILING, 0.01))
            for rel in ("pair", "exact")}
    with open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
              encoding="utf-8", errors="ignore") as f:
        truth = sk.eng_to_idx(f.read())[5000:5000 + L_HIT]

    all_cells = cells()
    receipts = {"n_cells": len(all_cells), "bars_at_N": {"N": N_CEILING, **bars},
                "family_note": f"{len(all_cells)} cells; each bar stated at its own "
                               f"N=2^32 with this family count disclosed (PREREG).",
                "vector_seed_list": "FIXED_SEEDS + Random(20260907) x58 (= R27 P0)",
                "cells": {}}
    plan = []
    for lane, red, rel, off in all_cells:
        stream = STREAMS[red]
        nK_a = L_SCREEN * 6 + 64
        lines = [f"GRIND28GATE 1", f"LANE {lane}", f"REDUCER {red}",
                 f"RELATION {rel}", f"OFFSET {off}",
                 f"CAND_BAR {CAND_BAR!r}", f"CLAIM_BAR {bars[rel]!r}",
                 f"NVEC {len(vec_seeds)}"]
        pmaxes = []
        for w in vec_seeds:
            K = stream(w, nK_a)
            d, pmax = stage_a(runner.C_SCREEN, K, rel, off)
            pmaxes.append(pmax)
            lines.append(f"VEC {w} {pmax!r} {float(d['score'])!r} "
                         f"{d['ptr_end']} {d['n_skips']} {d['nchars']}")
            lines.append("KS " + " ".join(map(str, K[:128])))
            lines.append("PLAIN " + " ".join(map(str, d["plain_idx"])))

        # ---- planted control (b): encipher truth with THIS cell's true keystream.
        # Frozen ladder (PREREG amendment A1): first full-gate-passing seed is the
        # plant; every tried seed's verdict is recorded (measured clause-3 power).
        ladder_log, plant = [], None
        for ps in PLANT_LADDER:
            Kp = stream(ps, L_HIT * 6 + 64)
            Cp = encipher(truth, Kp, rel, off, seed=ps)
            dec = H.HitDecode(C=Cp, K=Kp, o=off, preset=rel,
                              n_round_adjudicated=N_CEILING,
                              truth_idx=truth[:len(Cp)])
            v = H.evaluate(dec)
            ladder_log.append({"seed": ps, "hit": bool(v.hit),
                               "recovery": float(v.recovery),
                               "heldout": float(v.heldout_recovery),
                               "pmax": float(v.pmax)})
            if v.hit and v.recovery >= 0.999:
                plant = ps
                break
        assert plant is not None, (lane, "no ladder seed passes full gate", ladder_log)
        dp, plant_pmax = stage_a(Cp[:L_SCREEN], Kp, rel, off)
        assert plant_pmax >= CAND_BAR, (lane, plant_pmax)
        lines.append(f"PLANT_SEED {plant}")
        lines.append(f"PLANT_PMAX {plant_pmax!r}")
        lines.append(f"PLANT_CIPHER {L_SCREEN} " +
                     " ".join(map(str, Cp[:L_SCREEN])))
        lines.append(f"PLANT_PLAIN {L_SCREEN} " +
                     " ".join(map(str, dp["plain_idx"])))

        # ---- false-reject micro-set (c): wrong seeds on the plant cipher
        fr_seeds = [w for w in FR_SEEDS if w != plant]
        lines.append(f"NFR {len(fr_seeds)}")
        fr_pmax = []
        for w in fr_seeds:
            Kw = stream(w, nK_a)
            _, pm = stage_a(Cp[:L_SCREEN], Kw, rel, off)
            fr_pmax.append(pm)
            assert pm < bars[rel], (lane, w, pm)
            lines.append(f"FR {w} {pm!r}")
        lines.append("END")

        path = os.path.join(HERE, "gates", f"cellgate_{lane}.dat")
        blob = "\n".join(lines) + "\n"
        with open(path, "w") as f:
            f.write(blob)
        receipts["cells"][lane] = {
            "reducer": red, "relation": rel, "offset": off,
            "claim_bar": bars[rel],
            "plant_seed": plant, "plant_ladder": ladder_log,
            "vec_pmax_min": min(pmaxes), "vec_pmax_max": max(pmaxes),
            "plant_screen_pmax": plant_pmax,
            "plant_screen_margin_over_cand": plant_pmax - CAND_BAR,
            "plant_screen_margin_over_claim": plant_pmax - bars[rel],
            "plant_fullgate": {"hit": bool(v.hit), "pmax": float(v.pmax),
                               "bar": float(v.bar), "recovery": float(v.recovery),
                               "heldout": float(v.heldout_recovery),
                               "preg": v.preg_name},
            "false_reject_max_pmax": max(fr_pmax),
            "gate_sha256": hashlib.sha256(blob.encode()).hexdigest(),
        }
        plan.append({
            "lane": lane, "reducer": red, "relation": rel, "offset": off,
            "from": 0, "to": 2 ** 32,
            "cand_bar": CAND_BAR, "claim_bar": bars[rel],
            "gate": os.path.join(HERE, "gates", f"cellgate_{lane}.dat"),
            "engine": os.path.join(HERE, "grind28"),
        })
        print(f"{lane:24s} plant {plant_pmax:7.3f} (claim {bars[rel]:.3f}) "
              f"plant_seed={plant} fullgate rec={ladder_log[-1]["recovery"]:.3f} frmax={max(fr_pmax):.3f}")

    with open(os.path.join(HERE, "receipts", "gates_receipts.json"), "w") as f:
        json.dump(receipts, f, indent=1)
    with open(os.path.join(HERE, "queued_cells.json"), "w") as f:
        json.dump(plan, f, indent=1)
    print(f"wrote {len(all_cells)} gates + receipts + queued_cells.json "
          f"(bars: pair {bars['pair']!r} exact {bars['exact']!r} at N=2^32)")


if __name__ == "__main__":
    main()
