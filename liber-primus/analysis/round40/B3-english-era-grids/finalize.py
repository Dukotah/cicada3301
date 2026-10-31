#!/usr/bin/env python3
"""R40-B3 finalize: bars at actual N / N=1e6 / N=screened, L=240 gate on bar-clearing keep rows, near-miss lists, store validation.
python finalize.py B04|KDF|R17PAD|COSPAD ..."""
import sys, os, json, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

NAME2GRID = {"B04": "b3:B04", "KDF": "b3:KDF", "R17PAD": "pads:G3", "COSPAD": "pads:G4"}


def get_grid(name):
    kind, g = NAME2GRID[name].split(":")
    if kind == "b3":
        import b3; return b3.mk(g)
    import b3pads; return b3pads.mk(g)


def finalize(name):
    grid = get_grid(name)
    st = json.load(open(E.F("summary_%s.json" % name))); keep = json.load(open(E.F("keep_%s.json" % name)))
    out = {"grid": name, "complete": st.get("complete"), "capped": st.get("capped", False), "screened": st["screened"], "survivors": st["survivors"],
           "decode_errors": st.get("decode_errors", 0), "elapsed_s": st.get("elapsed_s"), "rels": {}, "flagged": [], "near_miss": [], "by_group": {}}
    for g, (sc, sv) in sorted(st["by_group"].items()):
        out["by_group"][g] = {"screened": sc, "survivors": sv, "rate": sv / max(sc, 1)}
    for rel in E.RELS:
        N = st["decodes"][rel]
        if N == 0: continue
        Ns = max(st["screened"], 2)
        b = {"actualN": [E.bar(N, 120, rel), E.bar(N, 240, rel)], "declN": [E.bar(E.N_DECL, 120, rel), E.bar(E.N_DECL, 240, rel)], "screenedN": [E.bar(Ns, 120, rel), E.bar(Ns, 240, rel)]}
        best = st["best"][rel]
        ent = {"N_actual": N, "N_screened": st["screened"], "bar120_actualN": round(b["actualN"][0], 3), "bar240_actualN": round(b["actualN"][1], 3),
               "bar120_declN": round(b["declN"][0], 3), "bar240_declN": round(b["declN"][1], 3), "bar120_screenedN": round(b["screenedN"][0], 3),
               "best_pmax": best["pmax"], "best_preg": best["preg"], "best_kid": best["kid"], "best_degenerate": best["degenerate"],
               "clears_actualN": best["pmax"] >= b["actualN"][0], "clears_declN": best["pmax"] >= b["declN"][0], "clears_screenedN": best["pmax"] >= b["screenedN"][0], "hist": st["hist"][rel]}
        cand = sorted([r for r in keep if r["rel"] == rel], key=lambda r: -r["pmax"])
        ent["top5"] = [(r["pmax"], r["preg"], r["kid"], r["degenerate"]) for r in cand[:5]]
        for r in [r for r in cand if r["pmax"] >= b["actualN"][0]]:
            m = r["meta"]; e = {"rel": rel, "kid": r["kid"], "pmax120": r["pmax"], "preg120": r["preg"], "degenerate": r["degenerate"],
                                "bar120_actualN": ent["bar120_actualN"], "bar240_actualN": ent["bar240_actualN"], "clears_declN_L120": r["pmax"] >= b["declN"][0], "gate": None}
            Cf = grid.cfull(m["cname"]); short = len(Cf) < 120
            if short: e["short_page"] = True
            if name == "KDF" and m["dir"] == "rev":
                e["gate"] = "unavailable (rev buffer 184); FLAGGED_FOR_ORACLE directly"; e["FLAGGED_FOR_ORACLE"] = True
            elif len(Cf) < 240:
                e["gate"] = "unavailable (stream shorter than 240 runes: %d); FLAGGED_FOR_ORACLE directly" % len(Cf); e["FLAGGED_FOR_ORACLE"] = True
            else:
                Kf = grid.keyfull(m); C, Ke = E.apply_variant(Cf[:240], Kf, m["atb"], m["sg"])
                d, a = E.v3dec(C, Ke, rel); p240 = float(a["pmax"]); e.update(pmax240=round(p240, 3), preg240=E.PAN.registers[a["preg"]], clears240_actualN=bool(p240 >= b["actualN"][1]),
                                                                              clears_declN_both=bool(r["pmax"] >= b["declN"][0] and p240 >= b["declN"][1]))
                e["gate"] = "pass" if p240 >= b["actualN"][1] else "fail"
                if p240 >= b["actualN"][1]: e["FLAGGED_FOR_ORACLE"] = True
            e["certified"] = False
            (out["flagged"] if e.get("FLAGGED_FOR_ORACLE") else out["near_miss"]).append(e)
        out["rels"][rel] = ent
    rows = E.F("rows_%s.jsonl" % name)
    out["validate_store"] = "ok"
    try: E.AD.validate_store(rows)
    except Exception as ex: out["validate_store"] = "FAIL %s" % ex
    sys.path.insert(0, os.path.join(E.LP, "analysis", "handoff")); import validate_ledger as VL
    try: out["check_r3_store"] = VL.check_r3_store(rows)
    except Exception as ex: out["check_r3_store"] = "ERR %s" % ex
    json.dump(out, open(E.F("final_%s.json" % name), "w"), indent=1, default=str)
    for rel, e in out["rels"].items():
        print(name, rel, "N", e["N_actual"], "best", e["best_pmax"], "bars", e["bar120_actualN"], e["bar120_declN"], e["bar120_screenedN"], "clears", e["clears_actualN"], e["clears_declN"])
    print(name, "flagged", len(out["flagged"]), "near", len(out["near_miss"]), out["validate_store"], out["check_r3_store"])


if __name__ == "__main__":
    for n in sys.argv[1:]: finalize(n)
