"""R44/W2-C2 positive controls (PREREG section 5) — three plants through the IDENTICAL runner.

Plant A: pair lane, sub fwd, key page 13 at its first line start in (29, 72], shift 0, EN_KJV.
Plant B: pair lane, add REV, key page 40 at offset 17, shift 1, LATIN.
Plant C: canon lane, sub fwd, canon offset 7001, shift 0, EN_KJV (different passage).

Pass (all three): argmax over the plant ct page's cells == planted coordinates, pmax >= bar,
non-degenerate; second-best non-neighbour below bar (neighbour = same rel/dir/shift family
within +-2 offsets, documented if above). Writes plant_pair.json + plant_canon.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c2lib as C                                     # noqa: E402


def neighbour(m, pm):
    return (m["tag"] == pm["tag"] and m["dir"] == pm["dir"] and m["rel"] == pm["rel"]
            and m["shift"] == pm["shift"] and abs(m["off"] - pm["off"]) <= 2)


def run_pair_plant(name, plant_ct, pages, planted_meta):
    """Plant ct page scanned against ALL 55 unsolved key pages — the identical pair runner."""
    best = C.Best(k=20)
    for i in range(55):
        kf = np.asarray(pages[i]["idx"], dtype=np.int64)
        kr = kf[::-1].copy()
        offs = C.key_offsets(pages[i])
        C.scan_ct_against_key(plant_ct, kf, kr, offs, best, tag="key=%d" % i)
    return verdict(name, best, planted_meta)


def verdict(name, best, planted_meta):
    rows = sorted(best.rows, key=lambda r: -r[0])
    top_v, top_m, top_dec = rows[0]
    import adjudicate as A
    res = A.adjudicate(np.asarray(top_dec, dtype=np.int64), pan=C.PAN)
    exact = all(top_m.get(k) == v for k, v in planted_meta.items())
    bar = C.bar_for(top_m["L"])
    second = next(((v, m) for v, m, _ in rows[1:] if not neighbour(m, planted_meta)),
                  (None, None))
    passed = bool(exact and (not res["degenerate"]) and top_v >= bar
                  and (second[0] is None or second[0] < C.bar_for(second[1]["L"])))
    return dict(name=name, passed=passed, planted=planted_meta,
                top=dict(pmax=float(top_v), meta=top_m, degenerate=bool(res["degenerate"]),
                         bar=bar, head=C.gp.indices_to_translit(top_dec[:40])),
                second_nonneighbour=dict(pmax=second[0],
                                         meta=second[1]) if second[0] is not None else None,
                n_cells=best.n)


def main():
    pages = C.canon_pages()
    ok, facts = C.verify_premise(pages)
    if not ok:
        print("PREMISE RE-VERIFICATION FAILED:", facts)
        json.dump(dict(passed=False, reason="premise", facts=facts),
                  open(os.path.join(HERE, "plant_pair.json"), "w"), indent=1)
        sys.exit(2)

    out = {"premise": facts, "plants": []}

    # ---- Plant A: sub fwd key page 13, first line start in (29,72], shift 0, EN_KJV 200
    ls = [t for t in C.line_starts(pages[13]) if 29 < t <= 72]
    oA = ls[0]
    kf13 = np.asarray(pages[13]["idx"], dtype=np.int64)
    pA = np.asarray(C.kjv_plain(200), dtype=np.int64)
    ctA = C.encipher(pA, kf13[oA:oA + 200], 1, -1, 0)
    mA = dict(tag="key=13", dir="fwd", rel="sub", shift=0, off=oA)
    out["plants"].append(run_pair_plant("A_sub_fwd_p13_linestart", ctA, pages, mA))

    # ---- Plant B: add REV key page 40, offset 17, shift 1, LATIN 150
    kr40 = np.asarray(pages[40]["idx"], dtype=np.int64)[::-1].copy()
    pB = np.asarray(C.latin_plain(150), dtype=np.int64)
    ctB = C.encipher(pB, kr40[17:17 + 150], 1, 1, 1)
    mB = dict(tag="key=40", dir="rev", rel="add", shift=1, off=17)
    out["plants"].append(run_pair_plant("B_add_rev_p40_o17_s1", ctB, pages, mB))

    out["passed"] = all(p["passed"] for p in out["plants"])
    json.dump(out, open(os.path.join(HERE, "plant_pair.json"), "w"), indent=1)

    # ---- Plant C: canon lane, sub fwd, offset 7001, shift 0, EN_KJV 180 (later passage)
    canon = np.asarray([i for pg in pages for i in pg["idx"]], dtype=np.int64)
    pC = np.asarray(C.kjv_plain(180, skip_chars=400_000), dtype=np.int64)
    ctC = C.encipher(pC, canon[7001:7001 + 180], 1, -1, 0)
    bestC = C.Best(k=20)
    ovC = C.Best(k=5)
    # plant page has no canon interval; pass an empty interval (no self-overlap possible)
    C.scan_ct_against_canon(ctC, canon, bestC, ovC, (-1, -1), tag="canon")
    mC = dict(tag="canon", dir="fwd", rel="sub", shift=0, off=7001)
    vC = verdict("C_canon_sub_o7001", bestC, mC)
    json.dump(vC, open(os.path.join(HERE, "plant_canon.json"), "w"), indent=1)
    out["plants"].append(vC)

    all_pass = all(p["passed"] for p in out["plants"])
    print(json.dumps({p["name"]: p["passed"] for p in out["plants"]}, indent=1))
    print("ALL PLANTS PASSED" if all_pass else "PLANT FAILURE — INSTRUMENT-INCOMPLETE")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
