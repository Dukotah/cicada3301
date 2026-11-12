"""R44 / W2-C8 plant gate — PREREG sections 3 (Q1) + 6b.  Runs BEFORE any real target.

Round-trip asserts for every family x source branch at k=7 and k=13, then the five plants
P1-P5 pushed through the IDENTICAL full-enumeration sweep path (c8lib.sweep_stream).
Gate per plant: planted cell recovered exactly on [k:], global argmax of its sweep,
pmax >= bar, and every non-planted crosser matches the planted plaintext on >= 25% of
scored positions (addendum 6b).  Any failure => INSTRUMENT-INCOMPLETE.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c8lib as L                                            # noqa: E402

N = 29


def premise_gate():
    U = L.nc.unsolved()
    segs = L.nc.segments()[:-2]
    flat = [i for s in segs for i in s]
    ok = (len(U) == 12956 and len(segs) == 55 and flat == list(U))
    return ok, dict(len_unsolved=len(U), n_segs=len(segs), concat_matches=flat == list(U))


def roundtrip_asserts():
    """Encipher -> decode exact recovery on [k:], every branch, k in {7, 13}."""
    Pt = L.english_plain(300)
    checks = []
    for k in (7, 13):
        # ct-affine (a,b)=(3,17) arbitrary in-grid cell
        a, b = 3, 17
        C = L.encipher_ct_affine(Pt, k, a, b)
        D = L.decode_ct_affine(C, k)[a * 28 + (b - 1)]
        checks.append(("ct_aff", k, bool((D == np.array(Pt[k:])).all())))
        # ct-window all f x sign
        for fi, f in enumerate(L.WINDOW_FS):
            for si, sign in enumerate(L.SIGNS):
                C = L.encipher_ct_window(Pt, k, f, sign)
                D, labels = L.decode_ct_window(np.array(C), k)
                checks.append((f"ct_win_{f}_{sign}", k,
                               bool((D[fi * 2 + si] == np.array(Pt[k:])).all())))
        # pt / mix affine + window via the ONE sequential pass
        for src in ("pt", "mix"):
            for fam, cell in (("aff", (1, 28)), ("win", ("min", -1))):
                seed = 4
                C = L.encipher_ptmix(Pt, k, fam, src, cell, seed)
                D, plab = L.decode_ptmix(np.array(C), k)
                w = plab.index((fam, src, cell, seed))
                checks.append((f"{src}_{fam}_{cell}", k,
                               bool((D[w] == np.array(Pt[k:])).all())))
    return checks


def run_plant(name, stream, planted, plain, orient_of_plant):
    """Full enumeration on the plant stream; evaluate the PREREG gate."""
    sink, state = L.make_topsink(top_n=20)
    L.sweep_stream(np.array(stream, dtype=np.int64), name, sink)
    best = state["best"]
    k = planted["k"]
    tail = np.array(plain[k:])

    def is_planted(row):
        return (row["orient"] == orient_of_plant and row["k"] == k
                and row["family"] == planted["family"] and row["src"] == planted["src"]
                and tuple(row["cell"]) == tuple(planted["cell"])
                and row.get("seed") == planted.get("seed"))

    argmax_ok = is_planted(best)
    bar = L.bar_for(len(stream) - k)
    crossed = best["pmax"] >= bar
    extra = []
    ok_extra = True
    for c in state["crossers"]:
        if is_planted(c):
            continue
        # addendum 6b: acceptable iff decode matches planted plaintext >= 25%
        # re-derive that crosser's decode through the same decoders
        Co = np.array(stream, dtype=np.int64)
        if c["orient"] == "rev":
            Co = Co[::-1].copy()
        kk = c["k"]
        if c["family"] == "ctaff":
            a, b = c["cell"]
            D = L.decode_ct_affine(Co, kk)[a * 28 + (b - 1)]
        elif c["family"] == "ctwin":
            Xw, wl = L.decode_ct_window(Co, kk)
            D = Xw[wl.index(tuple(c["cell"]))]
        else:
            Xp, pl = L.decode_ptmix(Co, kk)
            fam = "aff" if c["family"] == "pmaff" else "win"
            D = Xp[pl.index((fam, c["src"], tuple(c["cell"]), c["seed"]))]
        tailc = np.array(plain[kk:])
        m = min(len(D), len(tailc))
        frac = (float((D[:m] == tailc[:m]).mean())
                if c["orient"] == orient_of_plant else 0.0)
        extra.append(dict(cell=dict(orient=c["orient"], k=kk, family=c["family"],
                                    src=c["src"], cell=c["cell"], seed=c["seed"],
                                    pmax=c["row"]["pmax"]),
                          plain_match_frac=round(frac, 4)))
        if frac < 0.25:
            ok_extra = False
    # exact recovery of planted decode
    Co = np.array(stream, dtype=np.int64)
    if orient_of_plant == "rev":
        Co = Co[::-1].copy()
    if planted["family"] == "ctaff":
        a, b = planted["cell"]
        D = L.decode_ct_affine(Co, k)[a * 28 + (b - 1)]
    elif planted["family"] == "ctwin":
        Xw, wl = L.decode_ct_window(Co, k)
        D = Xw[wl.index(tuple(planted["cell"]))]
    else:
        Xp, pl = L.decode_ptmix(Co, k)
        fam = "aff" if planted["family"] == "pmaff" else "win"
        D = Xp[pl.index((fam, planted["src"], tuple(planted["cell"]), planted["seed"]))]
    recovered = bool((D == tail).all())
    passed = bool(recovered and argmax_ok and crossed and ok_extra)
    return dict(name=name, passed=passed, recovered=recovered, argmax_is_planted=argmax_ok,
                planted_pmax=float(best["pmax"]) if argmax_ok else None,
                best_row=best, bar=bar, n_rows=state["n_rows"],
                n_other_crossers=len(extra), other_crossers=extra,
                best_preg=L.PAN.registers[best["preg"]])


def main():
    t0 = time.time()
    out = {}
    ok, facts = premise_gate()
    out["premise"] = facts
    if not ok:
        out["verdict"] = "UNAVAILABLE-BY-PREMISE"
        json.dump(out, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
        sys.exit(2)

    rt = roundtrip_asserts()
    out["roundtrips"] = [dict(branch=b, k=k, ok=o) for b, k, o in rt]
    if not all(o for _b, _k, o in rt):
        out["verdict"] = "INSTRUMENT-INCOMPLETE (round-trip failure)"
        json.dump(out, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
        sys.exit(3)

    EN = L.english_plain(2000)
    LA = L.latin_plain(2000)
    plants = []

    # P1 — lag-7 ct difference composite (a,b)=(1,28), fwd (the mandated lag-7 plant)
    c1 = L.encipher_ct_affine(EN, 7, 1, 28)
    plants.append(run_plant("P1-ctaff-k7-diff", c1,
                            dict(family="ctaff", src="ct", cell=(1, 28), k=7, seed=None),
                            EN, "fwd"))
    # P2 — pt-affine k=9 (1,1), seed eq4, REV orientation
    c2 = L.encipher_ptmix(EN, 9, "aff", "pt", (1, 1), 4)
    plants.append(run_plant("P2-ptaff-k9-sum-rev", list(reversed(c2)),
                            dict(family="pmaff", src="pt", cell=(1, 1), k=9, seed=4),
                            EN, "rev"))
    # P3 — ct-window prod k=13 sign +1
    c3 = L.encipher_ct_window(EN, 13, "prod", 1)
    plants.append(run_plant("P3-ctwin-prod-k13", c3,
                            dict(family="ctwin", src="ct", cell=("prod", 1), k=13,
                                 seed=None), EN, "fwd"))
    # P4 — P1's construction over LATIN (the register axis)
    c4 = L.encipher_ct_affine(LA, 7, 1, 28)
    p4 = run_plant("P4-ctaff-k7-LATIN", c4,
                   dict(family="ctaff", src="ct", cell=(1, 28), k=7, seed=None), LA, "fwd")
    p4["register_axis_ok"] = p4["best_preg"] not in ("EN_MODERN", "EN_KJV")
    p4["passed"] = bool(p4["passed"] and p4["register_axis_ok"])
    plants.append(p4)
    # P5 — 240-rune English segment through the per-segment driver (same sweep path)
    EN240 = L.english_plain(240)
    c5 = L.encipher_ct_affine(EN240, 7, 1, 28)
    plants.append(run_plant("P5-segment-240", c5,
                            dict(family="ctaff", src="ct", cell=(1, 28), k=7, seed=None),
                            EN240, "fwd"))

    out["plants"] = plants
    # short-L power diagnostics (no gate): planted-config decode at L=120 and L=66
    diag = []
    for Ld in (120, 66):
        ENd = L.english_plain(Ld)
        cd = L.encipher_ct_affine(ENd, 7, 1, 28)
        D = L.decode_ct_affine(np.array(cd, dtype=np.int64), 7)[1 * 28 + (28 - 1)]
        full = L.A.adjudicate(D, pan=L.PAN)
        diag.append(dict(L=Ld, scored_n=Ld - 7, pmax=round(full["pmax"], 3),
                         bar=L.bar_for(Ld - 7), crosses=bool(full["pmax"] >= L.bar_for(Ld - 7))))
    out["short_L_power_diagnostics"] = diag

    out["all_passed"] = bool(all(p["passed"] for p in plants))
    out["wall_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
    print("PLANT GATE:", "PASSED" if out["all_passed"] else "FAILED")
    for p in plants:
        print(f"  {p['name']:24s} passed={p['passed']} recovered={p['recovered']} "
              f"argmax={p['argmax_is_planted']} pmax={p['planted_pmax']} bar={p['bar']} "
              f"other_crossers={p['n_other_crossers']} preg={p['best_preg']}")
    print("short-L power:", diag)
    print("wall %.1fs" % out["wall_s"])


if __name__ == "__main__":
    main()
