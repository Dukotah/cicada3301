"""python final.py   merge parts -> rescore_rows.jsonl, summary.json, stock validation."""
import os, sys, json, time
from c1common import *

MDS_MIN, IOC_MAX, dthr = degenerate_thresholds()
metas = {}
for fn in sorted(os.listdir(F("parts"))):
    if fn.endswith(".done"): metas[fn[:-5]] = json.load(open(F("parts", fn)))
store = F("rescore_rows.jsonl"); n_rows = 0; first = None
with open(store, "w") as out:
    for fam in sorted(metas):
        with open(F("parts", fam + ".jsonl")) as f:
            h = f.readline()
            if first is None:
                h0 = json.loads(h); h0["sweep_id"] = "round40/C1/rescore-all"; h0["universe_units"] = 0; h0["universe_rows"] = 0; out.write(json.dumps(h0) + "\n"); first = h0
            for line in f:
                if line.strip(): out.write(line); n_rows += 1
summ = {"degenerate_filter": dthr, "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha256": P12_SHA, "rows": n_rows, "families": {}, "flagged": [], "near_miss": []}
for fam, m in metas.items():
    e = {"kind": m["kind"]}
    if m["kind"] in ("beam", "screened_beam"):
        best_nd = {r: [-1e9, None, None, None, None] for r in RELS}; ndeg = {r: 0 for r in RELS}; nrows = {r: 0 for r in RELS}; topdeg = {r: [-1e9, None] for r in RELS}; top = {r: [] for r in RELS}
        with open(F("parts", fam + ".jsonl")) as f:
            f.readline()
            for line in f:
                rw = json.loads(line)
                if rw[0].startswith("null:"): continue
                rel = rw[0].rsplit(":", 1)[1]; nrows[rel] += 1
                if rw[9] <= MDS_MIN or rw[8] >= IOC_MAX:
                    ndeg[rel] += 1
                    if rw[3] > topdeg[rel][0]: topdeg[rel] = [rw[3], rw[0], rw[8], rw[9]]
                    continue
                top[rel].append((rw[3], rw[0], REGS[rw[4]]))
                if rw[3] > best_nd[rel][0]: best_nd[rel] = [rw[3], rw[0], REGS[rw[4]], rw[5], (rw[8], rw[9])]
        bars = m["bars"]
        keyN = "actualN_screened" if m["kind"] == "screened_beam" else "actualN"
        e.update({"rows": nrows, "n_degenerate_rows": ndeg, "top_degenerate_row": topdeg, "bars": bars, "bar_key": keyN, "family_null": m["family_null"],
                  "heads_screened": m.get("heads_screened"), "survivors": m.get("survivors"), "keys": m.get("keys"), "n_C_windows": m.get("n_C_windows"),
                  "best_nondegenerate": {r: {"pmax": best_nd[r][0], "kid": best_nd[r][1], "preg": best_nd[r][2], "pmax_ne": best_nd[r][3], "ioc_mds": best_nd[r][4]} for r in RELS},
                  "top3_nondegenerate": {r: sorted(top[r], reverse=True)[:3] for r in RELS}})
        e["clears_actualN"] = {r: bool(best_nd[r][0] >= bars[r][keyN]) for r in RELS}
        e["clears_declared"] = {r: bool(best_nd[r][0] >= bars[r]["declared_1e6"]) for r in RELS}
        e["gap_to_actualN"] = {r: round(best_nd[r][0] - bars[r][keyN], 3) for r in RELS}
        for r in RELS:
            if e["clears_actualN"][r]:
                ent = {"family": fam, "rel": r, "kid": best_nd[r][1], "pmax": best_nd[r][0], "bar_actualN": bars[r][keyN], "bar_declared": bars[r]["declared_1e6"], "FLAGGED_L240_PENDING": True}
                (summ["flagged"] if e["clears_declared"][r] else summ["near_miss"]).append(ent)
            elif m["kind"] == "screened_beam" and best_nd[r][0] >= bars[r]["N_survivors"]:
                summ["near_miss"].append({"family": fam, "rel": r, "kid": best_nd[r][1], "pmax": best_nd[r][0], "bar_survivorN": bars[r]["N_survivors"], "bar_actualN": bars[r][keyN], "note": "clears survivor-N bar only"})
    else:
        e.update({k: m[k] for k in ("n_streams", "D", "best_stream", "best_pmax", "best_Z", "null_max_Z_q99", "exceed", "p_family", "wilson95_exceed_rate", "top5", "n_degenerate_streams", "n_streams_total") if k in m})
        if "raw_best" in m: e["raw_best"] = m["raw_best"]
        e["control"] = m["control"]; e["control_pass"] = m["control"]["all_pass"]
        e["z_only_p_lt_0.01"] = bool(m["p_family"] < 0.01); e["both_Z_and_raw_p_lt_0.01"] = bool(m["p_family"] < 0.01 and m.get("raw_best", {}).get("p", 1) < 0.01)
        if e["both_Z_and_raw_p_lt_0.01"]: summ["near_miss"].append({"family": fam, "best_stream": m["best_stream"], "Z": m["best_Z"], "p_family": m["p_family"], "route": "direct"})
    summ["families"][fam] = e
ctl = {}
for fn in sorted(os.listdir(F("controls"))):
    c = json.load(open(F("controls", fn))); ctl[fn[:-5]] = {"table": c.get("table"), "gate_ge4_of_6_per_relation": c.get("gate_ge4_of_6_per_relation")}
summ["beam_controls"] = ctl
try: summ["validate_store"] = "ok: %s" % (AD.validate_store(store),)
except Exception as ex: summ["validate_store"] = "FAIL: %s" % str(ex)[:300]
sys.path.insert(0, os.path.join(AN, "handoff")); import validate_ledger as VL
try: summ["check_r3_store"] = VL.check_r3_store(store)
except Exception as ex: summ["check_r3_store"] = "ERR: %s" % str(ex)[:300]
json.dump(summ, open(F("rescore_summary.json"), "w"), indent=1, default=float)
log("final: rows", n_rows, "validate_store", summ["validate_store"], "check_r3_store", summ["check_r3_store"], "flagged", len(summ["flagged"]), "near", len(summ["near_miss"]))
